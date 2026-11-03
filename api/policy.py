"""Kohu policy enforcer (P31b): license/role enforcement + Steward stubs.

Contract (PLAN.md section 3, PRD.md FR3/FR5, TASK_CHECKLIST.md T31-T32):
  the policy agent enforces license class and role on retrieval output,
  blocking leaks through snippets and citations. Denial is silent for
  non-steward personas (denied chunks simply absent). The Steward sees
  everything plus license labels (vendor, coverage, expiry) and stub
  cards for restricted sources; stubs carry metadata only, no chunk text.

Defense in depth: retrieval pre-filters by role, and enforce() re-checks
every candidate against the manifest visible_to set, so a smuggled chunk
(an adversarial or buggy candidate) is dropped here. Every decision is
logged to run_steps (agent='policy') with ids and counts only.

Fictional demo license registry (all DEMO DATA — FICTIONAL, like the
corpus itself); the manifest carries no vendor terms, so Steward labels
live here, not in ingest.

Usage:
  python api/policy.py --probe   # leakage probe, all four personas
"""

import argparse
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import migrate  # noqa: E402  (same-dir runner; once-per-process ensure)
import planner  # noqa: E402  (run creation for the probe)
import retrieval  # noqa: E402

REPO = HERE.parent
DEFAULT_CORPUS = REPO / "corpus"
DEFAULT_DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres@localhost:5432/kohu")

# Fictional demo license terms for restricted classes. DEMO DATA — FICTIONAL.
LICENSE_REGISTRY = {
    "licensed-market": {"vendor": "Northwind Data Co. (demo)",
                        "coverage": "Q1-Q4 2025 market dataset",
                        "expiry": "2026-12-31",
                        "seats": "25 analyst seats"},
    "licensed-report": {"vendor": "Northwind Data Co. (demo)",
                        "coverage": "licensed report quoting market dataset",
                        "expiry": "2026-12-31",
                        "seats": "25 analyst seats"},
    "performance": {"vendor": "Internal HR (demo)",
                    "coverage": "team performance summary",
                    "expiry": "n/a — manager-restricted",
                    "seats": "managers"},
}

RESTRICTED_CLASSES = ("licensed", "manager-restricted")


def license_class(source_id, manifest):
    for e in manifest["entries"]:
        if e["id"] == source_id:
            return e.get("license_class") or e.get("licenseClass")
    return None


def enforce(candidates, persona, run_id, database_url,
            corpus_dir=DEFAULT_CORPUS):
    """Filter candidates to persona-visible sources; attach Steward labels.

    Returns {"allowed": [...], "stubs": [...]}. Allowed chunks keep
    {chunk_id, source_id, text, citation, score} plus (Steward only)
    license_class and license label. Stubs are Steward-only metadata
    cards for restricted sources in the result set — no chunk text.
    Logs agent='policy' with ids/counts only, never text.
    """
    import psycopg

    manifest = retrieval.load_manifest(corpus_dir)
    visible = set(retrieval.allowed_sources(persona, manifest))
    allowed, dropped = [], 0
    for c in candidates:
        if c["source_id"] not in visible:
            dropped += 1
            continue
        row = {"chunk_id": c["chunk_id"], "source_id": c["source_id"],
               "text": c["text"], "citation": c["citation"],
               "score": c["score"]}
        if persona == "steward":
            lic = license_class(c["source_id"], manifest)
            row["license_class"] = lic
            if lic in RESTRICTED_CLASSES:
                row["license"] = LICENSE_REGISTRY.get(c["source_id"], {})
        allowed.append(row)
    stubs = []
    if persona == "steward":
        for sid in sorted({c["source_id"] for c in allowed}):
            lic = license_class(sid, manifest)
            if lic in RESTRICTED_CLASSES:
                stubs.append({"source_id": sid, "license_class": lic,
                              "license": LICENSE_REGISTRY.get(sid, {}),
                              "note": "restricted source — metadata only"})
    migrate.ensure_up_once(database_url)
    with psycopg.connect(database_url) as conn:
        with conn.transaction():
            conn.execute(
                "INSERT INTO run_steps (run_id, step_index, agent, detail) "
                "VALUES (%s, %s, 'policy', %s) "
                "ON CONFLICT (run_id, step_index) DO UPDATE "
                "SET detail = EXCLUDED.detail",
                (run_id, 2, json.dumps({
                    "persona": persona,
                    "allowed_count": len(allowed),
                    "dropped_count": dropped,
                    "stub_count": len(stubs),
                    "allowed_sources": sorted(
                        {c["source_id"] for c in allowed}),
                    "stub_sources": [s["source_id"] for s in stubs],
                    "input_tokens": sum(
                        planner.estimate_tokens(c["text"])
                        for c in candidates),
                    "output_tokens": sum(
                        planner.estimate_tokens(a["text"])
                        for a in allowed)})))
    return {"allowed": allowed, "stubs": stubs}


def _check(name, cond, detail=""):
    cond = bool(cond)
    print(("PASS " if cond else "FAIL ") + name
          + ((" — " + detail) if detail and not cond else ""))
    return cond


def cmd_probe(database_url, corpus_dir):
    """Leakage probe: same demo query as all four personas.

    Asserts per-persona source sets, silent denial, Steward labels/stubs,
    and that an injected denied chunk is dropped. Exit 0 iff all pass.
    """
    manifest = retrieval.load_manifest(corpus_dir)
    expect = {p: set(retrieval.allowed_sources(p, manifest))
              for p in retrieval.PERSONAS}
    ok = True
    for persona in retrieval.PERSONAS:
        run_id, _ = planner.plan_and_log(
            planner.DEMO_QUERY, database_url, corpus_dir)
        cands = retrieval.retrieve(
            planner.DEMO_QUERY, persona, run_id, database_url, corpus_dir)
        denied = {"licensed-market", "licensed-report", "performance",
                  "handbook", "process-report", "product-deck",
                  "sales-deck", "scanned-note"} - expect[persona]
        ok &= _check("%s: retrieval holds no denied source" % persona,
                     not ({c["source_id"] for c in cands} & denied),
                     "got %s" % sorted({c["source_id"] for c in cands}))
        out = enforce(cands, persona, run_id, database_url, corpus_dir)
        got = {c["source_id"] for c in out["allowed"]}
        ok &= _check("%s: allowed sources exactly the visible set" % persona,
                     got == expect[persona] and got,
                     "got %s want %s" % (sorted(got), sorted(expect[persona])))
        ok &= _check("%s: denial silent (no stubs)" % persona
                     if persona != "steward" else
                     "steward: stubs list restricted sources",
                     (out["stubs"] == []) if persona != "steward"
                     else len(out["stubs"]) > 0,
                     "stubs=%s" % [s["source_id"] for s in out["stubs"]])
        if persona == "steward":
            labelled = [c for c in out["allowed"]
                        if c.get("license_class") in RESTRICTED_CLASSES]
            ok &= _check("steward: restricted chunks carry license labels",
                         labelled and all("license" in c for c in labelled),
                         "labelled %d" % len(labelled))
            stub_text = json.dumps(out["stubs"])
            ok &= _check("steward: stubs carry no chunk text",
                         not any(c["text"][:40] in stub_text
                                 for c in out["allowed"]),
                         "stub leaks chunk text")
        print("  %s: %d candidates -> %d allowed, %d stubs (%s)" % (
            persona, len(cands), len(out["allowed"]), len(out["stubs"]),
            ",".join(sorted(got)) or "-"))
    # Adversarial: smuggled denied chunks must drop silently for employee.
    run_id, _ = planner.plan_and_log(
        planner.DEMO_QUERY, database_url, corpus_dir)
    cands = retrieval.retrieve(
        planner.DEMO_QUERY, "employee", run_id, database_url, corpus_dir)
    smuggled = list(cands) + [
        {"chunk_id": "smuggled-1", "source_id": "licensed-market",
         "text": "SECRET licensed figure 7.1", "citation": {"pointer": "E12"},
         "score": 999, "subtask_index": 2},
        {"chunk_id": "smuggled-2", "source_id": "performance",
         "text": "SECRET review note", "citation": {"pointer": "Summary"},
         "score": 999, "subtask_index": 2}]
    out = enforce(smuggled, "employee", run_id, database_url, corpus_dir)
    blob = json.dumps(out)
    ok &= _check("adversarial: smuggled chunks dropped, nothing leaks",
                 "SECRET" not in blob and out["stubs"] == [],
                 "leaked: %s" % blob[:200])
    print("LEAKAGE PROBE: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description="Kohu policy (P31b)")
    parser.add_argument("--probe", action="store_true",
                        help="leakage probe with all four personas")
    parser.add_argument("--database-url", default=os.environ.get(
        "DATABASE_URL", DEFAULT_DATABASE_URL))
    parser.add_argument("--corpus", default=str(DEFAULT_CORPUS))
    args = parser.parse_args(argv)
    if not args.probe:
        parser.error("need --probe")
    return cmd_probe(args.database_url, args.corpus)


if __name__ == "__main__":
    raise SystemExit(main())
