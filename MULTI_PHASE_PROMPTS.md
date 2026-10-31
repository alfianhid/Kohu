# Kohu Multi-Phase Prompts — Copy-Paste Build Order

Status: Draft. Run in order. Each prompt is one small-medium task. Stop after each verify step and report the result before the next prompt.

## Phase 0 — Setup

P00 Repo hygiene: "In C:\Users\User\Kohu, add README.md, LICENSE (MIT for our code), .gitignore for Python, Node, Postgres data, and Hyperframes renders, plus HACKATHON.md listing exactly which paths are hackathon-built versus reference-inspired (WeKnora, Logseq) with no copied code. Verify: fresh `git status` is clean and the four files render."

P01 Scaffold: "Create api/, ui/, corpus/, video/ plus a seed.sh that prints the 8-file plan and checks for META_API_KEY without printing it. Verify: seed.sh runs with no keys and exits 0."

## Phase 1 — Corpus

P10 Manifest: "Write corpus/manifest.json with 8 entries: id, filename, license class, citation anchors, and the conflict pair (sales deck slide vs licensed sheet range). Verify: a script counts 8 entries and 1 conflict pair."

P11 PDFs: "Generate the 2 PDFs with real tables and chart captions, each stamped DEMO DATA — FICTIONAL. Verify: text extraction finds the tables."

P12 Decks: "Generate the 2 decks with stable slide numbers, including the seeded Q3 disagreement. Verify: slide count matches manifest."

P13 Sheets: "Generate the licensed sheet (A1:F200 addressable) and the manager-restricted sheet. Verify: cell reads return expected ranges."

P14 Scanned PDF: "Generate the 1-page scanned PDF and prove the OCR path extracts its text. Verify: OCR text lands in output."

## Phase 2 — Data

P20 Schema: "Add Postgres plus pgvector migration for chunks (text, source id, license class, page, cell range, slide). Verify: migration applies to a fresh database."

P21 Ingest: "Build ingest that parses all 8 files through Muse Spark on Meta Model API and writes chunks with pointers. Verify: chunk count per file matches manifest."

P22 Seed: "Wire seed.sh to generate corpus, run migrations, ingest, and print counts. Verify: delete database, reseed, counts match."

## Phase 3 — Agents

P30 Planner: "Implement the planner that splits a query into per-source subtasks and logs them under a run id. Verify: fixed demo query shows subtasks."

P31 Retrieval plus policy: "Implement per-source retrieval with role pre-filter, then policy enforcement with Steward stubs. Verify: leakage probe with all four personas passes."

P32 Verifier plus conflict: "Implement verifier that drops uncited claims and conflict flagger that fires exactly once on the seeded pair. Verify: adversarial query drops cleanly, conflict creates one task."

## Phase 4 — API

P40 Ask endpoint: "Build POST /ask accepting persona and query, returning answer, claims with citations, and run id. Verify: same query as four personas yields the four expected source sets."

## Phase 5 — UI

P50 Personas and ask: "Build four logins and an ask box bound to POST /ask. Verify: switching persona changes the token and results."

P51 Comparison and citations: "Build side-by-side Employee vs Analyst view plus citation panel that jumps to page, cell, slide. Verify: each claim click lands correctly."

P52 Steward queue: "Build Steward queue showing the one conflict task with both sources linked. Verify: task appears only for Steward."

## Phase 6 — Video

P60 Hyperframes scaffold: "Scaffold video/ as a Hyperframes project with a 180-second timeline and the six scenes from PLAN.md. Verify: preview plays end to end."

P61 Render: "Fill scenes, turn captions on, keep music low, render MP4 under 3:00 showing only hackathon-built work. Verify: runtime and content checklist pass."

## Phase 7 — Submission

P70 Rehearsal: "Run the fixed demo query as all four personas twice and check AC1-AC7. Verify: two clean passes logged."

P71 Submit: "Prepare repo link, video link, and builder list for the Representative to submit once. Verify: all links are public and accessible."
