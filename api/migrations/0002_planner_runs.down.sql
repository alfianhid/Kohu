-- Kohu migration 0002 (down): drop planner run log.
DROP TABLE IF EXISTS run_steps;
DROP TABLE IF EXISTS planner_subtasks;
DROP TABLE IF EXISTS runs;
