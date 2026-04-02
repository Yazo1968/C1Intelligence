-- Migration 010: Add document metadata columns to all four retrieval RPC functions.
-- Each function now JOINs to its parent document table to return:
--   filename, document_reference_number, document_date, document_type_name
-- This enables human-readable source labels in agent citations.
--
-- NOTE: This migration has already been applied to the live Supabase database.
-- This file exists to keep the repo in sync with the live schema.

-- =============================================================================
-- Layer 1: search_chunks_semantic — JOIN to documents + document_types
-- =============================================================================
DROP FUNCTION IF EXISTS search_chunks_semantic(UUID, vector(3072), INT);

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
    similarity FLOAT,
    filename TEXT,
    document_reference_number TEXT,
    document_date DATE,
    document_type_name TEXT
)
LANGUAGE sql STABLE
AS $$
    SELECT
        dc.id,
        dc.document_id,
        dc.chunk_index,
        dc.content,
        dc.token_count,
        1 - (dc.embedding <=> p_query_embedding) AS similarity,
        d.filename,
        d.document_reference_number,
        d.document_date,
        dt.name AS document_type_name
    FROM document_chunks dc
    LEFT JOIN documents d ON d.id = dc.document_id
    LEFT JOIN document_types dt ON dt.id = d.document_type_id
    WHERE dc.project_id = p_project_id
    ORDER BY dc.embedding <=> p_query_embedding
    LIMIT p_top_k;
$$;

-- =============================================================================
-- Layer 1: search_chunks_fulltext — JOIN to documents + document_types
-- =============================================================================
DROP FUNCTION IF EXISTS search_chunks_fulltext(UUID, TEXT, INT);

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
    rank FLOAT,
    filename TEXT,
    document_reference_number TEXT,
    document_date DATE,
    document_type_name TEXT
)
LANGUAGE sql STABLE
AS $$
    SELECT
        dc.id,
        dc.document_id,
        dc.chunk_index,
        dc.content,
        dc.token_count,
        ts_rank(to_tsvector('english', dc.content), plainto_tsquery('english', p_query_text)) AS rank,
        d.filename,
        d.document_reference_number,
        d.document_date,
        dt.name AS document_type_name
    FROM document_chunks dc
    LEFT JOIN documents d ON d.id = dc.document_id
    LEFT JOIN document_types dt ON dt.id = d.document_type_id
    WHERE dc.project_id = p_project_id
      AND to_tsvector('english', dc.content) @@ plainto_tsquery('english', p_query_text)
    ORDER BY rank DESC
    LIMIT p_top_k;
$$;

-- =============================================================================
-- Layer 2: search_chunks_reference_semantic — JOIN to reference_documents
-- =============================================================================
DROP FUNCTION IF EXISTS search_chunks_reference_semantic(vector(3072), INT);

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
    similarity FLOAT,
    filename TEXT,
    document_reference_number TEXT,
    document_date DATE,
    document_type_name TEXT
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
        rd.name AS filename,
        rd.edition_year AS document_reference_number,
        NULL::DATE AS document_date,
        rd.document_type AS document_type_name
    FROM reference_chunks rc
    LEFT JOIN reference_documents rd ON rd.id = rc.reference_document_id
    ORDER BY rc.embedding <=> p_query_embedding
    LIMIT p_top_k;
$$;

-- =============================================================================
-- Layer 2: search_chunks_reference_fulltext — JOIN to reference_documents
-- =============================================================================
DROP FUNCTION IF EXISTS search_chunks_reference_fulltext(TEXT, INT);

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
    rank FLOAT,
    filename TEXT,
    document_reference_number TEXT,
    document_date DATE,
    document_type_name TEXT
)
LANGUAGE sql STABLE
AS $$
    SELECT
        rc.id,
        rc.reference_document_id,
        rc.chunk_index,
        rc.content,
        rc.token_count,
        ts_rank(to_tsvector('english', rc.content), plainto_tsquery('english', p_query_text)) AS rank,
        rd.name AS filename,
        rd.edition_year AS document_reference_number,
        NULL::DATE AS document_date,
        rd.document_type AS document_type_name
    FROM reference_chunks rc
    LEFT JOIN reference_documents rd ON rd.id = rc.reference_document_id
    WHERE to_tsvector('english', rc.content) @@ plainto_tsquery('english', p_query_text)
    ORDER BY rank DESC
    LIMIT p_top_k;
$$;
