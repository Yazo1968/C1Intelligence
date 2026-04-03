-- =============================================================================
-- C1 — Migration 013: Layer 2 retrieval filters
-- Adds optional p_layer_type and p_jurisdiction parameters to the two
-- reference document search RPC functions. NULL = no filter (all documents).
-- Uses CREATE OR REPLACE — safe to apply over migration 007 functions.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. Semantic search — updated with layer_type and jurisdiction filters
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION search_chunks_reference_semantic(
    p_query_embedding vector(3072),
    p_top_k           INT     DEFAULT 5,
    p_layer_type      TEXT    DEFAULT NULL,
    p_jurisdiction    TEXT    DEFAULT NULL
)
RETURNS TABLE (
    id                    UUID,
    reference_document_id UUID,
    chunk_index           INT,
    content               TEXT,
    token_count           INT,
    similarity            FLOAT,
    name                  TEXT,
    document_type         TEXT,
    layer_type            TEXT,
    jurisdiction          TEXT
)
LANGUAGE sql STABLE
AS $$
    SELECT
        rc.id,
        rc.reference_document_id,
        rc.chunk_index,
        rc.content,
        rc.token_count,
        1 - (rc.embedding <=> p_query_embedding) AS similarity,
        rd.name,
        rd.document_type,
        rd.layer_type,
        rd.jurisdiction
    FROM reference_chunks rc
    JOIN reference_documents rd ON rd.id = rc.reference_document_id
    WHERE
        (p_layer_type   IS NULL OR rd.layer_type   = p_layer_type)
        AND (p_jurisdiction IS NULL OR rd.jurisdiction = p_jurisdiction)
    ORDER BY rc.embedding <=> p_query_embedding
    LIMIT p_top_k;
$$;

-- ---------------------------------------------------------------------------
-- 2. Full-text search — updated with layer_type and jurisdiction filters
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION search_chunks_reference_fulltext(
    p_query_text   TEXT,
    p_top_k        INT  DEFAULT 5,
    p_layer_type   TEXT DEFAULT NULL,
    p_jurisdiction TEXT DEFAULT NULL
)
RETURNS TABLE (
    id                    UUID,
    reference_document_id UUID,
    chunk_index           INT,
    content               TEXT,
    token_count           INT,
    rank                  FLOAT,
    name                  TEXT,
    document_type         TEXT,
    layer_type            TEXT,
    jurisdiction          TEXT
)
LANGUAGE sql STABLE
AS $$
    SELECT
        rc.id,
        rc.reference_document_id,
        rc.chunk_index,
        rc.content,
        rc.token_count,
        ts_rank(
            to_tsvector('english', rc.content),
            plainto_tsquery('english', p_query_text)
        ) AS rank,
        rd.name,
        rd.document_type,
        rd.layer_type,
        rd.jurisdiction
    FROM reference_chunks rc
    JOIN reference_documents rd ON rd.id = rc.reference_document_id
    WHERE
        to_tsvector('english', rc.content) @@ plainto_tsquery('english', p_query_text)
        AND (p_layer_type   IS NULL OR rd.layer_type   = p_layer_type)
        AND (p_jurisdiction IS NULL OR rd.jurisdiction = p_jurisdiction)
    ORDER BY rank DESC
    LIMIT p_top_k;
$$;
