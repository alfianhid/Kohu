# Kohu — Company Knowledge Hub

Kohu is one place where anyone in a company can find what the company knows and what it has paid for. Internal documents, purchased data, and reports are ingested as they are, including scanned PDFs, slides, and spreadsheets. Muse Spark reads them, including charts and tables. Employees search or ask questions. Role-based access, including data license coverage, controls what each person's results and answers can draw from. Every answer cites the page, cell, or video timestamp it came from.

Built for the Meta Global AI Developer Hackathon (Remote, Oct 26 – Nov 4, 2025 EST), Startup track, theme Build for Your World.

- Representative: `alfianhid`
- Public repo: <https://github.com/alfianhid/Kohu>
- Status: pre-build. See [PROJECT.md](PROJECT.md), [PLAN.md](PLAN.md), [PRD.md](PRD.md), [TASK_CHECKLIST.md](TASK_CHECKLIST.md), [HACKATHON.md](HACKATHON.md).

## Hackathon slice (what the demo proves)

Cited search and Q&A over a synthetic corpus of 6–8 files (PDFs, slides, spreadsheets, one scanned PDF), with role-based filtering and exact citations.

- Ingest of PDFs, slides, and spreadsheets as they are, parsed through Muse Spark on the Meta Model API.
- Five agents per query: planner, per-source retrieval with role pre-filter, policy enforcer, citation verifier, conflict flagger.
- Four mocked personas: Employee, Licensed Analyst, Manager, Data Steward (Admin). Same query returns visibly different cited answers per role.
- Seeded conflict: sales deck vs. licensed sheet Q3 figure flags exactly once into the Steward queue.
- Three-minute Hyperframes video shows only hackathon-built work.

Deferred to follow-ons: recording-to-guide with SAM marks, full license-management backend, production hardening. See [PROJECT.md](PROJECT.md) D1.

## Repo layout

| Path | Contents |
|---|---|
| `api/` | FastAPI service + five agents + pgvector schema (planned, Phase 2–4) |
| `ui/` | Minimal web UI: four logins, ask box, comparison, citation panel (planned, Phase 5) |
| `corpus/` | 8 synthetic demo files + `manifest.json`, all stamped `DEMO DATA — FICTIONAL` (planned, Phase 1) |
| `video/` | Hyperframes project source (HTML scenes, 180 s timeline) + rendered MP4 (planned, Phase 6) |
| `seed.sh` | Fresh-clone seed: corpus, migrations, ingest, counts (planned, Phase 0–2) |

Which files are hackathon-built vs. reference-inspired is recorded in [HACKATHON.md](HACKATHON.md). No WeKnora or Logseq code is copied or vendored.

## Quickstart (once scaffold lands)

```sh
cp .env.example .env   # set META_API_KEY (never commit it)
./seed.sh              # build corpus, migrate, ingest, print counts
uvicorn api.main:app --reload
```

Fresh clone plus `seed.sh` reproduces the demo. All judged model calls go through the Meta Model API. No closed-model fallback in the judged path.

## Roles (simulated, all data synthetic)

| Persona | Sees | Never sees |
|---|---|---|
| Employee | Handbook, process docs, general reports | Licensed data, manager-restricted |
| Licensed Analyst | Employee set + licensed sheet and licensed report | Manager-restricted |
| Manager | Employee set + performance summary | Licensed data |
| Steward | All + license metadata (vendor, coverage, expiry) and redacted stubs | Nothing hidden |

Denial is silent except Steward stubs. Denied sources never leak through snippets, citations, or reranking.

## Compliance

- New work only: demo highlights only features built during the hackathon.
- Rights clean: synthetic corpus only, no company files.
- SAM references use `SAM 3.1` in submission materials.
- One submission per team by the Representative via the CV platform by Nov 4 9:00 PM EST.
