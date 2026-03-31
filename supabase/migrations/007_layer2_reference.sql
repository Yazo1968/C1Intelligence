-- =============================================================================
-- C1 — Construction Documentation Intelligence Platform
-- Migration 007: Layer 2 Reference Document Tables, RLS, and RPC Functions
-- =============================================================================
-- Implements the two-layer warehouse architecture (README Section 6.2).
-- Layer 2 stores platform-wide reference documents: FIDIC, PMBOK, IFRS, laws.
-- These tables are NOT project-scoped — all authenticated users can SELECT.
-- Only the service role can INSERT/UPDATE/DELETE.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. reference_documents — metadata for reference documents
-- ---------------------------------------------------------------------------
CREATE TABLE reference_documents (
    id               uuid         PRIMARY KEY DEFAULT gen_random_uuid(),
    name             text         NOT NULL,
    document_type    text         NOT NULL,
    standard_body    text         NOT NULL,
    edition_year     text,
    jurisdiction     text,
    description      text,
    status           text         NOT NULL CHECK (status IN ('ACTIVE', 'SUPERSEDED', 'DRAFT')),
    created_at       timestamptz  NOT NULL DEFAULT now(),
    updated_at       timestamptz  NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- 2. reference_chunks — chunked content with vector embeddings
-- ---------------------------------------------------------------------------
CREATE TABLE reference_chunks (
    id                    uuid         PRIMARY KEY DEFAULT gen_random_uuid(),
    reference_document_id uuid         NOT NULL REFERENCES reference_documents(id) ON DELETE CASCADE,
    chunk_index           integer      NOT NULL,
    content               text         NOT NULL,
    embedding             vector(3072) NOT NULL,
    token_count           integer,
    created_at            timestamptz  NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- 3. GIN full-text index on reference_chunks
-- ---------------------------------------------------------------------------
CREATE INDEX idx_reference_chunks_fulltext
    ON reference_chunks USING gin (to_tsvector('english', content));

-- ---------------------------------------------------------------------------
-- 4. updated_at trigger on reference_documents
--    Reuses set_updated_at() from migration 001.
-- ---------------------------------------------------------------------------
CREATE TRIGGER trg_reference_documents_updated_at
    BEFORE UPDATE ON reference_documents
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------------
-- 5. Row Level Security
-- ---------------------------------------------------------------------------
ALTER TABLE reference_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE reference_chunks ENABLE ROW LEVEL SECURITY;

-- reference_documents: SELECT for all authenticated users
CREATE POLICY reference_documents_select ON reference_documents
    FOR SELECT TO authenticated
    USING (true);

-- reference_documents: INSERT for service role only
CREATE POLICY reference_documents_insert ON reference_documents
    FOR INSERT TO service_role
    WITH CHECK (true);

-- reference_documents: UPDATE for service role only
CREATE POLICY reference_documents_update ON reference_documents
    FOR UPDATE TO service_role
    USING (true)
    WITH CHECK (true);

-- reference_documents: DELETE for service role only
CREATE POLICY reference_documents_delete ON reference_documents
    FOR DELETE TO service_role
    USING (true);

-- reference_chunks: SELECT for all authenticated users
CREATE POLICY reference_chunks_select ON reference_chunks
    FOR SELECT TO authenticated
    USING (true);

-- reference_chunks: INSERT for service role only
CREATE POLICY reference_chunks_insert ON reference_chunks
    FOR INSERT TO service_role
    WITH CHECK (true);

-- reference_chunks: DELETE for service role only (no UPDATE — immutable)
CREATE POLICY reference_chunks_delete ON reference_chunks
    FOR DELETE TO service_role
    USING (true);

-- ---------------------------------------------------------------------------
-- 6. RPC: Semantic search on reference_chunks (platform-wide, no project_id)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION search_chunks_reference_semantic(
    p_query_embedding vector(3072),
    p_top_k INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    reference_document_id UUID,
    chunk_index INT,
    content TEXT,
    token_count INT,
    similarity FLOAT
)
LANGUAGE sql STABLE
AS $$
    SELECT
        rc.id,
        rc.reference_document_id,
        rc.chunk_index,
        rc.content,
        rc.token_count,
        1 - (rc.embedding <=> p_query_embedding) AS similarity
    FROM reference_chunks rc
    ORDER BY rc.embedding <=> p_query_embedding
    LIMIT p_top_k;
$$;

-- ---------------------------------------------------------------------------
-- 7. RPC: Full-text search on reference_chunks (platform-wide, no project_id)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION search_chunks_reference_fulltext(
    p_query_text TEXT,
    p_top_k INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    reference_document_id UUID,
    chunk_index INT,
    content TEXT,
    token_count INT,
    rank FLOAT
)
LANGUAGE sql STABLE
AS $$
    SELECT
        rc.id,
        rc.reference_document_id,
        rc.chunk_index,
        rc.content,
        rc.token_count,
        ts_rank(to_tsvector('english', rc.content), plainto_tsquery('english', p_query_text)) AS rank
    FROM reference_chunks rc
    WHERE to_tsvector('english', rc.content) @@ plainto_tsquery('english', p_query_text)
    ORDER BY rank DESC
    LIMIT p_top_k;
$$;
