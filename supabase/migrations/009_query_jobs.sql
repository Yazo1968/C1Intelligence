-- Migration 009: Query Jobs table for persistent async query state.
-- Replaces the in-memory _query_status dict that was lost on Railway restarts.
-- NOTE: This migration has already been applied to the live Supabase database.
-- This file exists to keep the repo in sync with the live schema.

CREATE TABLE query_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    query_text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PROCESSING'
        CHECK (status IN ('PROCESSING', 'COMPLETE', 'FAILED')),
    response JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE query_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users access own query jobs"
    ON query_jobs FOR ALL
    USING (user_id = auth.uid());

CREATE INDEX idx_query_jobs_project_id ON query_jobs(project_id);
CREATE INDEX idx_query_jobs_status ON query_jobs(status);
