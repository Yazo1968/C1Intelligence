-- Migration 023: Two-stage entity extraction staging table
-- Supports progressive population of entity directory.
-- Stage 1 (extracting): each batch writes raw names here immediately.
-- Stage 2 (consolidating): consolidation pass reads from here, writes to entities table.

CREATE TABLE entity_raw_extractions (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    run_id          uuid NOT NULL REFERENCES entity_directory_runs(id) ON DELETE CASCADE,
    entity_type     text NOT NULL,
    -- 'organisation' | 'individual'
    name            text NOT NULL,
    title           text,
    -- individuals only: Mr / Eng / Dr / Arch
    context         text,
    -- one sentence describing how this name appears in the source text
    batch_number    integer NOT NULL DEFAULT 0,
    created_at      timestamptz NOT NULL DEFAULT now()
);

-- Index for efficient consolidation pass reads
CREATE INDEX idx_entity_raw_extractions_run_id
    ON entity_raw_extractions(run_id);
