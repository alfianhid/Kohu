"""A07 regression proof: structured errors + per-step tokens, no per-request migrations.

Usage:
  python api/verify_a07.py [--database-url URL] [--corpus DIR]

Checks (exit 0 iff all pass):
  1. POST /ask with an unknown persona -> HTTP 422 with a JSON body.
  2. POST /ask with an empty query -> HTTP 422 with a JSON body.
  3. POST /ask with Postgres unreachable -> HTTP 503 with a JSON body
     (never a raw 500 or an HTML error page).
  4. A live ask persists non-null integer input_tokens/output_tokens on
     every run_steps row (steps 0-4); when Spark backs the run, the
     step-4 spark_* totals are non-null too.
  5. Serving requests performs zero migration runs: after startup, two
     full asks issue no migrate.cmd_up call.

Needs a migrated + seeded database for checks 1, 4, 5 (same as the
other --probe entry points). Check 3 points at a dead port and needs
no database.
"""

import argparse
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import migrate  # noqa: E402
import planner  # noqa: E402
from fastapi import HTTPException  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import app as askapp  # noqa: E402

REPO = HERE.parent
DEFAULT_CORPUS = REPO / "corpus"
DEFAULT_DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres@localhost:5432/kohu")
DEAD_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/kohu_unreachable"


def _check(name, cond, detail=""):
    cond = bool(cond)
    print(("PASS " if cond else "FAIL ") + name
          + ((" — " + detail) if detail and not cond else ""))
    return cond


def _json_body(resp):
    try:
        return resp.json()
    except Exception:
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(description="Kohu A07 verify (P12)")
    parser.add_argument("--database-url", default=os.environ.get(
        "DATABASE_URL", DEFAULT_DATABASE_URL))
    parser.add_argument("--corpus", default=str(DEFAULT_CORPUS))
    args = parser.parse_args(argv)
    database_url = args.database_url
    os.environ["DATABASE_URL"] = database_url
    ok = True

    # Count real migration runs for check 5.
    migration_runs = []
    real_cmd_up = migrate.cmd_up

    def counting_cmd_up(database_url):
        migration_runs.append(database_url)
        return real_cmd_up(database_url)

    migrate.cmd_up = counting_cmd_up
    try:
        with TestClient(askapp.app) as client:
            startup_runs = list(migration_runs)
            ok &= _check("startup ensures schema at most once",
                         len(startup_runs) <= 1,
                         "runs=%d" % len(startup_runs))
            migration_runs.clear()

            r = client.post("/ask", json={"persona": "hacker",
                                          "query": "What was Q3 growth?"})
            body = _json_body(r)
            ok &= _check("unknown persona -> 422 JSON",
                         r.status_code == 422
                         and isinstance(body, dict)
                         and isinstance(body.get("detail"), str),
                         "status=%s body=%.120s" % (r.status_code, r.text))

            r = client.post("/ask", json={"persona": "analyst",
                                          "query": "   "})
            body = _json_body(r)
            ok &= _check("empty query -> 422 JSON",
                         r.status_code == 422
                         and isinstance(body, dict)
                         and isinstance(body.get("detail"), str),
                         "status=%s body=%.120s" % (r.status_code, r.text))

            r = client.post("/ask", json={
                "persona": "analyst", "query": planner.DEMO_QUERY})
            ok &= _check("live ask -> 200", r.status_code == 200,
                         "status=%s body=%.200s" % (r.status_code, r.text))
            if r.status_code != 200:
                print("A07 VERIFY: FAIL")
                return 1
            run_id = r.json()["run_id"]

            r2 = client.post("/ask", json={
                "persona": "analyst", "query": planner.DEMO_QUERY})
            ok &= _check("second live ask -> 200", r2.status_code == 200,
                         "status=%s" % r2.status_code)
            ok &= _check("requests perform zero migration runs",
                         migration_runs == [],
                         "runs=%s" % migration_runs)
    finally:
        migrate.cmd_up = real_cmd_up

    # Check 3: DB-down maps to structured 503, not a raw 500.
    saved = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = DEAD_DATABASE_URL
    try:
        try:
            askapp.ask(askapp.AskRequest(persona="analyst",
                                        query="What was Q3 growth?"))
            ok &= _check("DB-down -> 503 JSON, never raw 500", False,
                         "no exception raised")
        except HTTPException as e:
            body = json.loads(json.dumps(
                {"detail": e.detail})) if not isinstance(
                    e.detail, str) else {"detail": e.detail}
            ok &= _check("DB-down -> 503 JSON, never raw 500",
                         e.status_code == 503
                         and isinstance(body.get("detail"), str),
                         "status=%s detail=%.120s"
                         % (e.status_code, body.get("detail")))
    finally:
        if saved is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = saved

    # Check 4: per-step token counts persisted for the live run.
    import psycopg

    with psycopg.connect(database_url) as conn:
        rows = conn.execute(
            "SELECT step_index, agent, detail FROM run_steps "
            "WHERE run_id = %s ORDER BY step_index", (run_id,)).fetchall()
    by_step = {}
    for step_index, agent, detail in rows:
        d = json.loads(detail) if isinstance(detail, str) else detail
        by_step[step_index] = (agent, d or {})
    for step in (0, 1, 2, 3, 4):
        present = step in by_step
        toks = by_step.get(step, (None, {}))[1]
        good = (present
                and isinstance(toks.get("input_tokens"), int)
                and isinstance(toks.get("output_tokens"), int))
        ok &= _check("step %d has non-null token counts" % step, good,
                     "detail=%.200s" % (toks,))
    step4 = by_step.get(4, (None, {}))[1]
    spark_calls = step4.get("spark_calls", 0)
    spark_used = step4.get("spark_used", False)
    print("step 4 spark: synthesis detail spark_used=%s calls=%s "
          "input=%s output=%s estimated=%s degraded=%s" % (
              spark_used, spark_calls, step4.get("spark_input_tokens"),
              step4.get("spark_output_tokens"),
              step4.get("spark_tokens_estimated"),
              step4.get("degraded")))
    if spark_calls:
        ok &= _check("Spark-backed run shows non-null spark token counts",
                     isinstance(step4.get("spark_input_tokens"), int)
                     and isinstance(step4.get("spark_output_tokens"), int),
                     "step4=%.200s" % (step4,))
    else:
        print("NOTE no successful Spark call this run "
              "(key off or model unreachable); per-step estimates still "
              "cover every step.")

    print("A07 VERIFY: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
