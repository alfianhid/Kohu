-- Kohu migration 0003 (up): Steward conflict-task store (P32 / FR6).
--
-- Contract (PLAN.md section 4, PRD.md FR6, TASK_CHECKLIST.md T34):
--   the seeded sales-deck-vs-licensed-sheet Q3 disagreement flags exactly
--   once and creates one Steward task. The agent never invents a
--   resolution (status stays 'open', resolution stays 'none').
--
-- Exactly-once relies on the conflict_id UNIQUE constraint: repeat fires
-- for the same seeded pair are INSERT ... ON CONFLICT DO NOTHING, so the
-- table can never hold a second task for the pair. Additive-only;
-- rollback drops only this table, never chunks or run logs.
-- Rollback: api/migrations/0003_conflict_tasks.down.sql.

CREATE TABLE IF NOT EXISTS steward_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conflict_id TEXT NOT NULL UNIQUE,
  run_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'open'
    CONSTRAINT steward_tasks_status_check
    CHECK (status IN ('open', 'acknowledged', 'closed')),
  resolution TEXT NOT NULL DEFAULT 'none',
  detail JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT steward_tasks_conflict_nonempty_check
    CHECK (char_length(conflict_id) > 0)
);
-- Note: no CHECK on resolution — the flagger always writes 'none' (the
-- agent never invents a resolution), but a human Steward may update the
-- row later. Status transitions stay within open/acknowledged/closed.

CREATE INDEX IF NOT EXISTS steward_tasks_run_id_idx
  ON steward_tasks (run_id);
