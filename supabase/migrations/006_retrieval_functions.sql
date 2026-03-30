-- Migration 006: Retrieval RPC functions for pgvector similarity + full-text search
-- Called via supabase_client.rpc() from src/agents/retrieval.py.
-- Required because the pgvector <=> cosine distance operator cannot be expressed
-- through the standard Supabase PostgREST filter API.

-- =============================================================================
-- Function 1: Semantic (vector cosine similarity) search
-- =============================================================================
CREATE OR REPLACE FUNCTION search_chunks_semantic(
    p_project_id UUID,
    p_query_embedding vector(3072),
    p_top_k INT DEFAULT 20
)
RETURNS TABLE (
    id UUID,
    document_id UUID,
    chunk_index INT,
    content TEXT,
    token_count INT,
    similarity FLOAT
)
LANGUAGE sql STABLE
AS $$
    SELECT
        dc.id,
        dc.document_id,
        dc.chunk_index,
        dc.content,
        dc.token_count,
        1 - (dc.embedding <=> p_query_embedding) AS similarity
    FROM document_chunks dc
    WHERE dc.project_id = p_project_id
    ORDER BY dc.embedding <=> p_query_embedding
    LIMIT p_top_k;
$$;

-- =============================================================================
-- Function 2: Full-text search (PostgreSQL tsvector/tsquery)
-- =============================================================================
CREATE OR REPLACE FUNCTION search_chunks_fulltext(
    p_project_id UUID,
    p_query_text TEXT,
    p_top_k INT DEFAULT 20
)
RETURNS TABLE (
    id UUID,
    document_id UUID,
    chunk_index INT,
    content TEXT,
    token_count INT,
    rank FLOAT
)
LANGUAGE sql STABLE
AS $$
    SELECT
        dc.id,
        dc.document_id,
        dc.chunk_index,
        dc.content,
        dc.token_count,
        ts_rank(to_tsvector('english', dc.content), plainto_tsquery('english', p_query_text)) AS rank
    FROM document_chunks dc
    WHERE dc.project_id = p_project_id
      AND to_tsvector('english', dc.content) @@ plainto_tsquery('english', p_query_text)
    ORDER BY rank DESC
    LIMIT p_top_k;
$$;
