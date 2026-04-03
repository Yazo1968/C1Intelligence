-- Migration 016: HNSW indexes on document_chunks and reference_chunks
-- Uses halfvec cast to support 3072-dimension vectors (halfvec supports up to 4000 dims).
-- Cosine distance matches the <=> operator used in all four retrieval RPC functions.
-- Migration already applied to live Supabase by session coordinator.

CREATE INDEX idx_document_chunks_embedding_hnsw
    ON document_chunks
    USING hnsw ((embedding::halfvec(3072)) halfvec_cosine_ops);

CREATE INDEX idx_reference_chunks_embedding_hnsw
    ON reference_chunks
    USING hnsw ((embedding::halfvec(3072)) halfvec_cosine_ops);
