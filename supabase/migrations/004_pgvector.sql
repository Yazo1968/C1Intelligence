-- Migration 004: pgvector — Replace Gemini File Search with self-owned vector pipeline
-- Enables pgvector extension, creates document_chunks table, adds full-text index,
-- enables RLS, and removes Gemini-specific columns from projects and documents tables.

-- =============================================================================
-- 1. Enable pgvector extension
-- =============================================================================
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;

-- =============================================================================
-- 2. Create document_chunks table
-- =============================================================================
CREATE TABLE public.document_chunks (
    id              uuid            PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     uuid            NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
    project_id      uuid            NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    chunk_index     integer         NOT NULL,
    content         text            NOT NULL,
    embedding       vector(3072)    NOT NULL,
    token_count     integer,
    created_at      timestamptz     NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.document_chunks IS 'Stores chunked document content with vector embeddings for pgvector similarity search.';

-- =============================================================================
-- 3. Vector index — DEFERRED
-- pgvector 0.8.0 on Supabase caps both HNSW and IVFFlat at 2000 dimensions.
-- Gemini gemini-embedding-001 produces 3072-dimension vectors.
-- Cosine similarity search (<=> operator) works via sequential scan — acceptable
-- at current document volumes (hundreds to low thousands of chunks).
-- When Supabase upgrades pgvector beyond 0.8.0, add:
--   CREATE INDEX idx_document_chunks_embedding_hnsw
--       ON public.document_chunks
--       USING hnsw (embedding vector_cosine_ops);
-- =============================================================================

-- =============================================================================
-- 4. GIN index on tsvector for full-text search
-- =============================================================================
CREATE INDEX idx_document_chunks_content_fts
    ON public.document_chunks
    USING gin (to_tsvector('english', content));

-- =============================================================================
-- 5. Enable RLS — project-owner scoped (same pattern as all other tables)
-- =============================================================================
ALTER TABLE public.document_chunks ENABLE ROW LEVEL SECURITY;

CREATE POLICY document_chunks_select ON public.document_chunks
    FOR SELECT TO authenticated
    USING (is_project_owner(project_id));

CREATE POLICY document_chunks_insert ON public.document_chunks
    FOR INSERT TO authenticated
    WITH CHECK (is_project_owner(project_id));

CREATE POLICY document_chunks_update ON public.document_chunks
    FOR UPDATE TO authenticated
    USING (is_project_owner(project_id))
    WITH CHECK (is_project_owner(project_id));

CREATE POLICY document_chunks_delete ON public.document_chunks
    FOR DELETE TO authenticated
    USING (is_project_owner(project_id));

-- =============================================================================
-- 6. Remove Gemini-specific columns — no longer needed
-- =============================================================================
ALTER TABLE public.projects DROP COLUMN IF EXISTS gemini_store_name;
ALTER TABLE public.documents DROP COLUMN IF EXISTS gemini_file_name;
ALTER TABLE public.documents DROP COLUMN IF EXISTS gemini_document_name;
