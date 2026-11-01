"""Kohu ask endpoint (P40): POST /ask over the five-agent pipeline.

Contract (PRD.md FR4/FR5, TASK_CHECKLIST.md T40-T42):
  POST /ask {persona, query} -> {run_id, persona, answer, claims,
  sources, stubs, conflict, dropped_count}. Each claim links to one
  chunk; unverified claims are dropped, never shown. Same query as
  different personas returns different source sets; denied sources
  never leak via text, snippet, or citation.

Pipeline (one run id, steps 0-4 in run_steps):
  planner.plan_and_log -> retrieval.retrieve (role pre-filter) ->
  policy.enforce (re-check + Steward stubs) -> one claim per allowed
  source (top chunk) -> verifier.verify_claims (drops uncited) ->
  conflict.flag_conflict (exactly-once Steward task).

Answer synthesis is extractive (verified claim texts with pointers);
the synthesize() seam is where a Muse Spark call plugs in later
without changing the schema. No model call today, so no model-outage
path yet; empty results return a safe message (T42).

Usage:
  uvicorn api.app:app --port 8000
"""

import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

import conflict  # noqa: E402
import planner  # noqa: E402
import policy  # noqa: E402
import retrieval  # noqa: E402
import verifier  # noqa: E402

REPO = HERE.parent
DEFAULT_CORPUS = REPO / "corpus"
DEFAULT_DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres@localhost:5432/kohu")

MAX_WORDS_PER_CLAIM = 40

app = FastAPI(title="Kohu ask API (P40)")


class AskRequest(BaseModel):
    persona: str = Field(description="one of employee, analyst, manager, steward")
    query: str = Field(description="non-empty question")


def database_url():
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)


def excerpt(text, limit=MAX_WORDS_PER_CLAIM):
    words = text.split()
    return " ".join(words[:limit])


def synthesize(verified):
    """Extractive answer: numbered claim lines with [source pointer].

    Seam for a future Muse Spark synthesis call: replace this body,
    keep the signature (verified claims in, answer string out).
    """
    lines = []
    for i, claim in enumerate(verified, start=1):
        cite = claim["citation"]
        lines.append("%d. %s [%s %s]" % (
            i, claim["text"], cite["source_id"], cite["pointer"]))
    return "\n".join(lines)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/steward/queue")
def steward_queue(persona: str = ""):
    if persona != "steward":
        raise HTTPException(
            status_code=403,
            detail="steward queue is visible to the steward persona only")
    return {"persona": "steward",
            "tasks": conflict.list_tasks(
                database_url(), str(DEFAULT_CORPUS))}


@app.post("/ask")
def ask(req: AskRequest):
    persona, query = req.persona, (req.query or "").strip()
    if persona not in retrieval.PERSONAS:
        raise HTTPException(
            status_code=422,
            detail="unknown persona %r (want one of %s)"
            % (persona, ", ".join(retrieval.PERSONAS)))
    if not query:
        raise HTTPException(
            status_code=422, detail="query must be a non-empty string")
    db = database_url()
    run_id, _ = planner.plan_and_log(query, db, str(DEFAULT_CORPUS))
    cands = retrieval.retrieve(query, persona, run_id, db,
                               str(DEFAULT_CORPUS))
    out = policy.enforce(cands, persona, run_id, db, str(DEFAULT_CORPUS))
    best = {}
    for c in out["allowed"]:
        prev = best.get(c["source_id"])
        if (prev is None or (c["score"], c["chunk_id"])
                > (prev["score"], prev["chunk_id"])):
            best[c["source_id"]] = c
    draft = [{"text": excerpt(c["text"]),
              "citation": {"source_id": c["source_id"],
                           "pointer": c["citation"]["pointer"]}}
             for c in sorted(best.values(), key=lambda c: c["source_id"])]
    res = verifier.verify_claims(draft, run_id, db)
    flag = conflict.flag_conflict(out["allowed"], run_id, db,
                                  str(DEFAULT_CORPUS))
    verified = res["verified"]
    answer = (synthesize(verified) if verified
              else "No citable answer found for this query under the "
              "%s role." % persona)
    return {
        "run_id": run_id,
        "persona": persona,
        "answer": answer,
        "claims": verified,
        "sources": sorted({c["citation"]["source_id"] for c in verified}),
        "stubs": out["stubs"],
        "conflict": {"fired": flag["fired"],
                     "conflict_id": (flag["task"]["conflict_id"]
                                     if flag["task"] else None)},
        "dropped_count": len(res["dropped"]),
    }


CORPUS_DIR = REPO / "corpus"
if CORPUS_DIR.is_dir():
    app.mount("/corpus", StaticFiles(directory=str(CORPUS_DIR)),
              name="corpus")

UI_DIR = REPO / "ui"
if UI_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(UI_DIR), html=True),
              name="ui")
