# Kohu PRD — Hackathon Slice

Status: Draft. Sources: PROJECT.md decisions D1-D9 and PLAN.md. No build until PLAN.md is approved.

## 1. Problem

Company knowledge sits on laptops and in heads. Licensed data bought for the whole company goes unused. Teams lose a quarter of search time. Kohu makes one searchable hub with role-based access and exact citations.

## 2. Users and roles

Four mocked personas. Mappings are illustrative, not real IdP wiring.

| Persona | Sees | Never sees |
|---|---|---|
| Employee | Handbook, process docs, general reports | Licensed data, manager-restricted |
| Licensed Analyst | Employee set plus licensed sheet and licensed report | Manager-restricted |
| Manager | Employee set plus performance summary | Licensed data |
| Steward | All plus license metadata and redacted stubs | Nothing hidden |

## 3. Functional requirements

FR1 Ingest 8 synthetic files as they are: 2 PDFs with tables and charts, 2 decks, 2 sheets including 1 licensed-only, 1 scanned PDF for OCR, 1 manager-restricted sheet. All parsing through Muse Spark on Meta Model API.

FR2 Chunk model: text plus source id, license class (open-internal, licensed, manager-restricted), citation pointer (page, cell range, slide number). License class set at ingest, immutable at query.

FR3 Five agents per query: planner, per-source retrieval with pre-filter, policy enforcer, citation verifier, conflict flagger. Reuse WeKnora and Logseq patterns, original code only.

FR4 Ask endpoint returns answer plus claims. Each claim links to one chunk. Unverified claims are dropped, never shown.

FR5 Same query asked as each persona returns visibly different answers. Denied sources never leak via text, snippet, or citation. Steward sees license labels and stubs.

FR6 Seeded conflict (sales deck versus licensed sheet Q3 figure) flags exactly once and creates one Steward task. Agent never invents a resolution.

FR7 Run log per query: planner subtasks, retrieval sets, policy decisions, verifier passes and drops, tokens used. Inspectable in UI.

FR8 Minimal UI: four logins, ask box, side-by-side persona comparison, citation panel that opens to source location, Steward queue view.

## 4. Non-functional requirements

Public repo from day one. Fresh clone plus seed script reproduces demo. All judged model calls go through Meta Model API. No closed-model fallback. Three-minute video shows only hackathon-built work.

## 5. Out of scope

Recording to guide, SAM 3.1 marking, full license backend, production auth, open-weights parity. One closing video slide may name them as follow-ons.

## 6. Acceptance criteria

AC1 Employee answer cites only internal pages. AC2 Analyst answer adds licensed cells. AC3 Manager answer adds performance summary, no licensed cells. AC4 Steward sees license labels and conflict task. AC5 Zero leakage in any denied view. AC6 Conflict flags exactly once. AC7 Every claim opens to its source. AC8 Rubric covered: Impact 30, Meta use 25, Depth 20, Demo 25.
