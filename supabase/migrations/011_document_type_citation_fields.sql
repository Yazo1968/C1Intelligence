-- Migration 011: Add citation_fields column to document_types and update
-- all four retrieval RPC functions to return it.
--
-- citation_fields is an ordered TEXT[] array specifying which metadata fields
-- to include in the source label for a given document type.
-- Valid values: 'type_name', 'reference_number', 'date'.
--
-- NOTE: This migration has already been applied to the live Supabase database.
-- This file exists to keep the repo in sync with the live schema.

-- =============================================================================
-- 1. Add citation_fields column to document_types
-- =============================================================================
ALTER TABLE document_types ADD COLUMN IF NOT EXISTS citation_fields TEXT[];

-- =============================================================================
-- 2. Set citation_fields by category
-- =============================================================================

-- Contracts & Agreements: type + reference number + date
UPDATE document_types SET citation_fields = '{type_name,reference_number,date}'
WHERE category IN ('Contract Documents', 'Procurement & Tendering');

-- Correspondence & Notices: type + reference number + date
UPDATE document_types SET citation_fields = '{type_name,reference_number,date}'
WHERE category IN ('Correspondence', 'Claims & Disputes');

-- Financial: type + reference number + date
UPDATE document_types SET citation_fields = '{type_name,reference_number,date}'
WHERE category IN ('Financial & Commercial', 'Insurance & Bonds');

-- Design & Technical: type + reference number (date less relevant)
UPDATE document_types SET citation_fields = '{type_name,reference_number}'
WHERE category IN ('Design & Engineering', 'Quality & Testing');

-- Programme & Schedule: type + date (reference numbers less common)
UPDATE document_types SET citation_fields = '{type_name,date}'
WHERE category IN ('Programme & Schedule', 'Site Records & Reports');

-- Governance & Compliance: type + reference number + date
UPDATE document_types SET citation_fields = '{type_name,reference_number,date}'
WHERE category IN ('Governance & Compliance', 'Regulatory & Permits');

-- Health & Safety: type + reference number + date
UPDATE document_types SET citation_fields = '{type_name,reference_number,date}'
WHERE category IN ('Health & Safety', 'Environmental');

-- Default: anything not yet covered gets the full set
UPDATE document_types SET citation_fields = '{type_name,reference_number,date}'
WHERE citation_fields IS NULL;

-- =============================================================================
-- 3. Layer 1: search_chunks_semantic — add citation_fields
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
    document_type_name TEXT,
    citation_fields TEXT[]
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
        dt.name AS document_type_name,
        dt.citation_fields
    FROM document_chunks dc
    LEFT JOIN documents d ON d.id = dc.document_id
    LEFT JOIN document_types dt ON dt.id = d.document_type_id
    WHERE dc.project_id = p_project_id
    ORDER BY dc.embedding <=> p_query_embedding
    LIMIT p_top_k;
$$;

-- =============================================================================
-- 4. Layer 1: search_chunks_fulltext — add citation_fields
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
    document_type_name TEXT,
    citation_fields TEXT[]
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
        dt.name AS document_type_name,
        dt.citation_fields
    FROM document_chunks dc
    LEFT JOIN documents d ON d.id = dc.document_id
    LEFT JOIN document_types dt ON dt.id = d.document_type_id
    WHERE dc.project_id = p_project_id
      AND to_tsvector('english', dc.content) @@ plainto_tsquery('english', p_query_text)
    ORDER BY rank DESC
    LIMIT p_top_k;
$$;

-- =============================================================================
-- 5. Layer 2: search_chunks_reference_semantic — add citation_fields (NULL for references)
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
    document_type_name TEXT,
    citation_fields TEXT[]
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
        rd.document_type AS document_type_name,
        NULL::TEXT[] AS citation_fields
    FROM reference_chunks rc
    LEFT JOIN reference_documents rd ON rd.id = rc.reference_document_id
    ORDER BY rc.embedding <=> p_query_embedding
    LIMIT p_top_k;
$$;

-- =============================================================================
-- 6. Layer 2: search_chunks_reference_fulltext — add citation_fields (NULL for references)
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
    document_type_name TEXT,
    citation_fields TEXT[]
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
        rd.document_type AS document_type_name,
        NULL::TEXT[] AS citation_fields
    FROM reference_chunks rc
    LEFT JOIN reference_documents rd ON rd.id = rc.reference_document_id
    WHERE to_tsvector('english', rc.content) @@ plainto_tsquery('english', p_query_text)
    ORDER BY rank DESC
    LIMIT p_top_k;
$$;
