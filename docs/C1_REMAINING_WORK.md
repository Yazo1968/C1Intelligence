# C1 Intelligence — Remaining Work Plan

**Date:** 2026-04-03
**Status:** Both active workstreams complete. This document captures all
remaining items, their priority, prerequisites, and the exact work required.

---

## Context

Both governing workstreams are fully executed:
- `C1_QUERY_IMPROVEMENT_PLAN.md` v1.3 — all four phases complete
- `C1_MULTIAGENT_ARCHITECTURE_PLAN.md` v1.0 — all six phases complete

What remains falls into two categories:
1. External dependency items — blocked on Supabase platform upgrade
2. Phase 2 product features — larger scope, require separate planning

---

## Category 1 — External Dependency

Blocked on a Supabase platform upgrade. No action possible until the
dependency resolves.

---

### Item 5 — Vector similarity index (HNSW/IVFFlat)

**Blocked on:** Supabase upgrading pgvector beyond 0.8.0
**Current constraint:** pgvector 0.8.0 caps HNSW/IVFFlat at 2000 dimensions.
Embeddings are 3072 dimensions. Sequential scan is used.

**When unblocked:**
Apply a migration to create an HNSW index on `document_chunks.embedding`
and `reference_chunks.embedding`. This will significantly improve
retrieval performance at scale.

```sql
-- When pgvector supports 3072 dims
CREATE INDEX ON document_chunks
USING hnsw (embedding vector_cosine_ops);

CREATE INDEX ON reference_chunks
USING hnsw (embedding vector_cosine_ops);
```

**Monitor:** Check Supabase release notes for pgvector version upgrades.

---

## Category 2 — Phase 2 Product Features

These are larger-scope features that require separate planning sessions.
None are blocked on technical prerequisites — they are product decisions.

---

### Item 6 — Party ID resolution

**Scope:** Medium-large
**Condition:** Requires a parties management API that does not exist

`issuing_party_id` and `receiving_party_id` on documents are always NULL
because there is no mechanism to create parties, assign them roles, and
resolve them at ingestion time. The data model supports it — the
`parties` table exists — but the API and ingestion pipeline do not.

**What is needed:**
- API endpoints: create party, list parties, assign party to project
- Ingestion pipeline update: attempt to resolve issuing/receiving party
  from document metadata against the parties register
- Frontend: party management UI within a project workspace

---

### Item 7 — Cross-specialist contradiction detection

**Scope:** Medium
**Reference:** AGENT_PLAN Phase 7
**Current state:** `contradiction_cross.py` returns `[]` intentionally

The current `contradiction.py` detects intra-document contradictions.
Cross-specialist contradiction detection (e.g. the Legal orchestrator
finds a completion date that conflicts with the Schedule SME's analysis)
is not yet implemented.

**What is needed:**
- Implement `contradiction_cross.py` with logic to compare findings
  across Tier 1 orchestrators for conflicting values on the same field
- Integrate with the existing `ContradictionFlag` model and write-back

---

### Item 8 — Approval workflows

**Scope:** Large
**Reference:** Phase 2 feature

Approval workflows for documents, variations, and payment certificates
within the platform. Requires a workflow engine or state machine,
notification system, and authority matrix enforcement.

---

### Item 9 — Five user roles and authority matrix

**Scope:** Large
**Reference:** Phase 2 feature

Currently all authenticated users have the same access level within
a project. Phase 2 requires: Owner, Admin, Legal, Commercial, Viewer
roles with different read/write/query permissions.

---

### Item 10 — Document control system integration

**Scope:** Large
**Reference:** Phase 2 feature

Integration with Aconex, Docutrack, or other document control systems
used on GCC projects. Allows C1 to ingest documents directly from the
project document management system rather than manual upload.

---

## Summary Table

| # | Item | Category | Priority | Effort | Prerequisite |
|---|---|---|---|---|---|
| 5 | HNSW/IVFFlat vector index | External dependency | — | Small | pgvector upgrade |
| 6 | Party ID resolution | Phase 2 | — | Medium-large | Parties API |
| 7 | Cross-specialist contradiction detection | Phase 2 | — | Medium | — |
| 8 | Approval workflows | Phase 2 | — | Large | — |
| 9 | Five user roles and authority matrix | Phase 2 | — | Large | — |
| 10 | Document control system integration | Phase 2 | — | Large | — |
