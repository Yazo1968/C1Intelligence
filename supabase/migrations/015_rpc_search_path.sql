-- Migration 015: fix function_search_path_mutable security advisory
-- Adds SET search_path = public to all five affected RPC functions.
-- Function bodies are unchanged — only the search_path setting is added.
-- Resolves the advisory across migrations 001, 006, 007, 010, 011, and 013.

-- ---------------------------------------------------------------------------
-- 1. set_updated_at (migration 001)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = public
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

-- ---------------------------------------------------------------------------
-- 2. search_chunks_semantic (current definition: migration 011)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION search_chunks_semantic(
    p_project_id      UUID,
    p_query_embedding vector(3072),
    p_top_k           INT DEFAULT 20
)
RETURNS TABLE (
    id                       UUID,
    document_id              UUID,
    chunk_index              INT,
    content                  TEXT,
    token_count              INT,
    similarity               FLOAT,
    filename                 TEXT,
    document_reference_number TEXT,
    document_date            DATE,
    document_type_name       TEXT,
    citation_fields          TEXT[]
)
LANGUAGE sql STABLE
SET search_path = public
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

-- ---------------------------------------------------------------------------
-- 3. search_chunks_fulltext (current definition: migration 011)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION search_chunks_fulltext(
    p_project_id  UUID,
    p_query_text  TEXT,
    p_top_k       INT DEFAULT 20
)
RETURNS TABLE (
    id                       UUID,
    document_id              UUID,
    chunk_index              INT,
    content                  TEXT,
    token_count              INT,
    rank                     FLOAT,
    filename                 TEXT,
    document_reference_number TEXT,
    document_date            DATE,
    document_type_name       TEXT,
    citation_fields          TEXT[]
)
LANGUAGE sql STABLE
SET search_path = public
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

-- ---------------------------------------------------------------------------
-- 4. search_chunks_reference_semantic (current definition: migration 013)
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
SET search_path = public
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
-- 5. search_chunks_reference_fulltext (current definition: migration 013)
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
SET search_path = public
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
