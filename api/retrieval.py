"""Kohu retrieval (P31a): per-source retrieval with role pre-filter.

Contract (PLAN.md section 3, PRD.md FR3/FR5, TASK_CHECKLIST.md T31):
  retrieval agents run per source type with the role filter applied
  BEFORE search, so denied sources never enter ranking, snippets,
  citations, or the run log. Each planner subtask (pdf/page, deck/slide,
  sheet/cell-range) is searched only over the intersection of its sources
  with the persona's manifest visible_to set.

Role map comes from corpus/manifest.json "visible_to" (single source of
truth, same file the planner reads). Scoring is lexical term frequency
(embeddings stay NULL until the embedding pass lands); ranking never
widens the pre-filtered set.

Usage:
  python api/retrieval.py --persona analyst --run-id <id> [--limit 50]
"""

import argparse
import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import migrate  # noqa: E402  (same-dir runner; ensures run tables exist)
import planner  # noqa: E402  (subtask definitions + run creation)

REPO = HERE.parent
DEFAULT_CORPUS = REPO / "corpus"
DEFAULT_DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres@localhost:5432/kohu")

PERSONAS = ("employee", "analyst", "manager", "steward")

STOPWORDS = frozenset(
    "what was for and the a an of to in is it that with how why who which "
    "are were has have had this these those then than are was were be been "
    "or on at by from".split())


def load_manifest(corpus_dir):
    with open(pathlib.Path(corpus_dir) / "manifest.json",
              encoding="utf-8") as f:
        return json.load(f)


def allowed_sources(persona, manifest):
    """Source ids visible to a persona. Raises on unknown persona."""
    if persona not in PERSONAS:
        raise ValueError("unknown persona %r (want one of %s)"
                         % (persona, ", ".join(PERSONAS)))
    return sorted(e["id"] for e in manifest["entries"]
                  if persona in e.get("visible_to", []))


def query_terms(query):
    terms = [t for t in re.findall(r"[a-z0-9]+", query.lower())
             if t not in STOPWORDS and len(t) >= 2]
    return sorted(set(terms))


def score_text(text, terms):
    low = text.lower()
    return sum(low.count(t) for t in terms)


def citation_for(row):
    """row: (id, source_id, text, page, cell_range, slide)."""
    _, source_id, _, page, cell_range, slide = row
    if page is not None:
        return {"source_id": source_id, "pointer": "p.%d" % page}
    if slide is not None:
        return {"source_id": source_id, "pointer": "slide %d" % slide}
    return {"source_id": source_id, "pointer": cell_range}


def retrieve(query, persona, run_id, database_url, corpus_dir=DEFAULT_CORPUS,
             limit=None):
    """Search each planner subtask over role-allowed sources only.

    Returns ranked candidates [{chunk_id, source_id, text, citation,
    score, subtask_index}]. Logs one run_steps row (agent='retrieval')
    with per-subtask source ids and counts only — no chunk text, so the
    log itself cannot leak denied content. Raises on unknown persona or
    empty query.
    """
    import psycopg

    if not query or not query.strip():
        raise ValueError("query must be a non-empty string")
    manifest = load_manifest(corpus_dir)
    role_allowed = set(allowed_sources(persona, manifest))
    terms = query_terms(query)
    migrate.cmd_up(database_url)
    with psycopg.connect(database_url) as conn:
        with conn.transaction():
            rows = conn.execute(
                "SELECT subtask_index, source_type, anchor, sources "
                "FROM planner_subtasks WHERE run_id = %s "
                "ORDER BY subtask_index", (run_id,)).fetchall()
            if not rows:
                raise ValueError("no planner subtasks for run_id %r "
                                 "(plan the query first)" % (run_id,))
            candidates = []
            logged_sets = []
            with conn.cursor() as cur:
                for subtask_index, _stype, _anchor, sources in rows:
                    wanted = sorted(set(sources) & role_allowed)
                    logged_sets.append({"subtask_index": subtask_index,
                                        "searched_sources": wanted})
                    if not wanted:
                        continue
                    cur.execute(
                        "SELECT id, source_id, text, page, cell_range, slide "
                        "FROM chunks WHERE source_id = ANY(%s)",
                        (wanted,))
                    scored = [(score_text(r[2], terms), r)
                              for r in cur.fetchall()]
                    scored.sort(key=lambda s: (-s[0], s[1][1], s[1][0]))
                    if limit is not None:
                        scored = scored[:limit]
                    for score, r in scored:
                        candidates.append(
                            {"chunk_id": str(r[0]), "source_id": r[1],
                             "text": r[2], "citation": citation_for(r),
                             "score": score,
                             "subtask_index": subtask_index})
            candidates.sort(key=lambda c: (-c["score"], c["source_id"],
                                           c["chunk_id"]))
            conn.execute(
                "INSERT INTO run_steps (run_id, step_index, agent, detail) "
                "VALUES (%s, %s, 'retrieval', %s) "
                "ON CONFLICT (run_id, step_index) DO UPDATE "
                "SET detail = EXCLUDED.detail",
                (run_id, 1, json.dumps({
                    "persona": persona,
                    "terms": terms,
                    "subtask_sets": logged_sets,
                    "candidate_count": len(candidates),
                    "candidate_sources": sorted(
                        {c["source_id"] for c in candidates})}))
            )
    return candidates


def main(argv=None):
    parser = argparse.ArgumentParser(description="Kohu retrieval (P31a)")
    parser.add_argument("--persona", required=True, choices=PERSONAS)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--query", default=planner.DEMO_QUERY)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--database-url", default=os.environ.get(
        "DATABASE_URL", DEFAULT_DATABASE_URL))
    parser.add_argument("--corpus", default=str(DEFAULT_CORPUS))
    args = parser.parse_args(argv)
    cands = retrieve(args.query, args.persona, args.run_id,
                     args.database_url, args.corpus, args.limit)
    print("persona: %s  candidates: %d" % (args.persona, len(cands)))
    for c in cands[:20]:
        print("  [%s %s score=%d] %.80s" % (
            c["source_id"], c["citation"]["pointer"], c["score"],
            c["text"].replace("\n", " ")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
