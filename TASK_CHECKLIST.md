# Kohu Task Checklist — Small-Medium Tasks

Status: Draft. Check off only when the done bar is met. Owners: A is backend, B is frontend and video. Either can take Shared tasks.

## Phase 0 — Setup (Shared)

- [ ] T01 Public repo hygiene: README, LICENSE, `.gitignore`, `HACKATHON.md` marking new work. Done: fresh clone shows all four.
- [ ] T02 Meta Model API credits claimed by both builders, spend limit set. Done: both confirm in chat.
- [ ] T03 Monorepo scaffold: `api/`, `ui/`, `corpus/`, `video/`, one seed script. Done: `seed.sh` prints plan without keys.

## Phase 1 — Synthetic corpus (A)

- [ ] T10 Write 8-file manifest with license classes and citation anchors. Done: manifest lists all 8 plus conflict pair.
- [ ] T11 Generate 2 PDFs with tables and charts. Done: tables extract as text, charts have captions.
- [ ] T12 Generate 2 decks (10 slides product, sales with conflict figure). Done: slide numbers stable.
- [ ] T13 Generate 2 sheets (licensed A1:F200, performance summary). Done: cell ranges addressable.
- [ ] T14 Generate 1 scanned PDF for OCR path. Done: OCR text lands in chunks.
- [ ] T15 Mark every file `DEMO DATA — FICTIONAL`. Done: grep finds marker in all 8.

## Phase 2 — Data layer (A)

- [ ] T20 Postgres plus pgvector schema for chunks and citations. Done: migration applies clean.
- [ ] T21 Ingest pipeline through Muse Spark parse. Done: 8 files chunked with pointers.
- [ ] T22 License tags immutable at query time. Done: test tries override, fails closed.
- [ ] T23 Seed script reproduces corpus and index. Done: fresh clone seeds without manual steps.

## Phase 3 — Agents (A)

- [ ] T30 Planner splits by source type. Done: log shows subtasks per query.
- [ ] T31 Retrieval with role pre-filter. Done: denied ids absent from candidate sets.
- [ ] T32 Policy enforcer plus Steward stubs. Done: leakage probe passes for all roles.
- [ ] T33 Verifier drops uncited claims. Done: adversarial query drops cleanly.
- [ ] T34 Conflict flagger routes one Steward task. Done: seeded conflict fires exactly once.
- [ ] T35 Run log records steps, tokens, decisions. Done: one query shows full trace.

## Phase 4 — API (A)

- [ ] T40 `POST /ask` with persona, query, answer, claims, citations, run id. Done: schema pinned.
- [ ] T41 Persona switch changes sources only. Done: same query, four payloads differ correctly.
- [ ] T42 Error paths: denied source, empty result, model outage. Done: each returns safe message.

## Phase 5 — UI (B)

- [ ] T50 Four logins and ask box. Done: login swaps persona token.
- [ ] T51 Side-by-side persona comparison. Done: Employee versus Analyst diff visible.
- [ ] T52 Citation panel opens to page, cell, slide. Done: each claim click lands correctly.
- [ ] T53 Steward queue shows conflict task. Done: one task with both sources linked.

## Phase 6 — Video (B)

- [ ] T60 Hyperframes project scaffold with 180-second timeline. Done: preview plays end to end.
- [ ] T61 Scenes for problem, product, agentic run, conflict, stack, close. Done: matches PLAN.md arc.
- [ ] T62 Captions on, music low, MP4 renders. Done: file plays under 3:00.

## Phase 7 — Submission (Shared)

- [ ] T70 Demo script rehearsed with fixed query. Done: two dry runs pass AC1-AC7.
- [ ] T71 Submission page: repo link, video link, builders listed. Done: Representative submits once.
- [ ] T72 Retrospective: what was hackathon-built versus reference-inspired. Done: noted in README.
