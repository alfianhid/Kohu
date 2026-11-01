-- Kohu migration 0002 (up): planner run log (P30 / FR7).
--
-- Contract (PLAN.md section 3, PRD.md FR3/FR7, TASK_CHECKLIST.md T30/T35):
--   planner splits each query into per-source-type subtasks and logs them
--   under a run id. Later agents (retrieval, policy, verifier, conflict)
--   append their own steps to run_steps under the same run id.
--
-- Safety: additive-only. IF NOT EXISTS so retries are no-ops. Rollback:
-- api/migrations/0002_planner_runs.down.sql.

-- One row per asked query. run_id is client-generated (uuid hex) so the
-- planner can log subtasks in the same transaction as the run row.
CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY,
  query TEXT NOT NULL
    CONSTRAINT runs_query_nonempty_check CHECK (char_length(query) > 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- One row per planner subtask. source_type is the store family the
-- subtask hits; anchor is the manifest citation kind it cites with.
CREATE TABLE IF NOT EXISTS planner_subtasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id TEXT NOT NULL REFERENCES runs (run_id) ON DELETE CASCADE,
  subtask_index INTEGER NOT NULL,
  source_type TEXT NOT NULL
    CONSTRAINT planner_subtasks_source_type_check
    CHECK (source_type IN ('pdf', 'deck', 'sheet')),
  anchor TEXT NOT NULL
    CONSTRAINT planner_subtasks_anchor_check
    CHECK (anchor IN ('page', 'slide', 'cell-range')),
  store TEXT NOT NULL DEFAULT 'chunks',
  sources TEXT[] NOT NULL DEFAULT '{}',
  query_hint TEXT NOT NULL DEFAULT '',
  rationale TEXT NOT NULL DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT planner_subtasks_run_index_unique UNIQUE (run_id, subtask_index),
  CONSTRAINT planner_subtasks_index_nonnegative_check CHECK (subtask_index >= 0),
  CONSTRAINT planner_subtasks_sources_nonempty_check CHECK (cardinality(sources) > 0)
);

CREATE INDEX IF NOT EXISTS planner_subtasks_run_id_idx
  ON planner_subtasks (run_id);

-- Generic step log for later agents (T35): retrieval sets, policy
-- decisions, verifier passes/drops, conflict flags, token use. Planner
-- writes agent='planner' rows here too; readers join on run_id.
CREATE TABLE IF NOT EXISTS run_steps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id TEXT NOT NULL REFERENCES runs (run_id) ON DELETE CASCADE,
  step_index INTEGER NOT NULL,
  agent TEXT NOT NULL
    CONSTRAINT run_steps_agent_check
    CHECK (agent IN ('planner', 'retrieval', 'policy', 'verifier', 'conflict')),
  detail JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT run_steps_run_step_unique UNIQUE (run_id, step_index),
  CONSTRAINT run_steps_index_nonnegative_check CHECK (step_index >= 0)
);

CREATE INDEX IF NOT EXISTS run_steps_run_id_idx ON run_steps (run_id);
