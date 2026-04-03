# C1 Intelligence — Remaining Work Plan

**Date:** 2026-04-03
**Status:** Both active workstreams complete. This document captures all
remaining items, their priority, prerequisites, and the exact work required.

---

## Context

Both governing workstreams are fully executed:
- `C1_QUERY_IMPROVEMENT_PLAN.md` v1.3 — all four phases complete
- `C1_MULTIAGENT_ARCHITECTURE_PLAN.md` v1.0 — all six phases complete

What remains falls into three categories:
1. Small deferred tasks — actionable now, no prerequisites missing
2. External dependency items — blocked on Supabase platform upgrade
3. Phase 2 product features — larger scope, require separate planning
4. Security hardening — low urgency, non-blocking

---

## Category 1 — Actionable Now

These were deferred during the build for stated reasons. All conditions
are now met. Recommended execution order: 1 → 2 → 3 → 4.

---

### Item 2 — Document download endpoint

**Priority:** HIGH
**Agent:** API Engineer (backend + frontend)
**Effort:** Medium — one API endpoint, one frontend button
**Condition met:** "After Phase D" — Phase D is complete. `storage_path`
column exists on `documents` table and is populated on upload.

**The problem:**
Users can upload documents but cannot download the originals. The file
is stored in Supabase Storage at `{project_id}/{document_id}/{filename}`
in the `document-originals` bucket. There is no API endpoint or
frontend control to retrieve it.

**What to build:**

*API Engineer (backend) — new endpoint:*
```
GET /projects/{project_id}/documents/{document_id}/download
```
- Verify project access (RLS)
- Retrieve `storage_path` from `documents` table
- Generate a signed URL from Supabase Storage (short-lived, e.g. 60 seconds)
- Return the signed URL in the response
- The signed URL redirects to the actual file

*API Engineer (frontend):*
- Add a download icon/button to each row in `DocumentTable.tsx`
- On click: call the download endpoint, open the signed URL in a new tab

**Files:** `src/api/routes/documents.py`, `src/api/schemas.py`,
`frontend/src/components/documents/DocumentTable.tsx`,
`frontend/src/api/documents.ts`

**Commit protocol:** Backend and frontend each committed separately after
individual QG PASS.

---

## Category 2 — External Dependency

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

## Category 3 — Phase 2 Product Features

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

## Category 4 — Security Hardening

Non-blocking. Acceptable in current state for a known frontend
deployment. Address in a dedicated hardening session.

---

### Item 11 — CORS tightening

**Current state:** `allow_methods=["*"]` and `allow_headers=["*"]`
in `src/api/main.py`

**What to do:**
Restrict to: `allow_methods=["GET", "POST", "OPTIONS"]` and
`allow_headers=["Authorization", "Content-Type"]`

**File:** `src/api/main.py`

---

### Item 12 — `function_search_path_mutable` on RPC functions

**Current state:** Pre-existing Supabase security advisory affecting
all RPC functions across migrations 001, 006, 007, 010, 011, and 013.

**What to do:**
Add `SET search_path = public` to each affected function definition.
This is a migration that uses `CREATE OR REPLACE FUNCTION` on each
affected function to add the search path constraint.

**Affects:** All RPC functions defined in migrations 001, 006, 007,
010, 011, 013.

---

## Summary Table

| # | Item | Category | Priority | Effort | Prerequisite |
|---|---|---|---|---|---|
| 2 | Document download endpoint | Actionable now | HIGH | Medium | None |
| 5 | HNSW/IVFFlat vector index | External dependency | — | Small | pgvector upgrade |
| 6 | Party ID resolution | Phase 2 | — | Medium-large | Parties API |
| 7 | Cross-specialist contradiction detection | Phase 2 | — | Medium | — |
| 8 | Approval workflows | Phase 2 | — | Large | — |
| 9 | Five user roles and authority matrix | Phase 2 | — | Large | — |
| 10 | Document control system integration | Phase 2 | — | Large | — |
| 11 | CORS tightening | Security hardening | LOW | Trivial | — |
| 12 | `function_search_path_mutable` on RPC functions | Security hardening | LOW | Small | — |
