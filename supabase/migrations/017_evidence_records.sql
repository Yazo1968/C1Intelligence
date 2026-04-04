-- Migration 017: Add evidence_records column to query_log
-- Persists EvidenceRecord data from specialist findings for forensic auditability.

ALTER TABLE query_log
ADD COLUMN IF NOT EXISTS evidence_records JSONB;

COMMENT ON COLUMN query_log.evidence_records IS
'JSON array of EvidenceRecord objects from all specialist findings in this query. '
'Records layer retrieval status, sources, and provisions that could not be confirmed.';
