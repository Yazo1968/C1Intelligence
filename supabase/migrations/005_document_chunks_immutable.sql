-- Migration 005: Remove UPDATE policy from document_chunks — chunks are immutable.
-- document_chunks is intentionally write-once: chunks are created at ingestion
-- and deleted via CASCADE when the parent document is deleted. No update path
-- exists by design. This deviates from the 4-policy pattern on other tables
-- because immutability is an architectural constraint, not an oversight.

DROP POLICY IF EXISTS document_chunks_update ON public.document_chunks;
