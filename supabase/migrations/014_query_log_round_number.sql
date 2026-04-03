-- Migration 014: add round_number column to query_log
-- round_number records the orchestration round that produced specialist findings.
-- NULL for GREY path queries (no specialists ran).
ALTER TABLE query_log ADD COLUMN round_number INTEGER;
