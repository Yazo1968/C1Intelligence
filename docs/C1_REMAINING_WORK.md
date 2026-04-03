# C1 Intelligence — Remaining Work Plan

**Date:** 2026-04-03
**Status:** Both active workstreams complete. This document captures all
remaining items, their priority, prerequisites, and the exact work required.

---

## Context

Both governing workstreams are fully executed:
- `C1_QUERY_IMPROVEMENT_PLAN.md` v1.3 — all four phases complete
- `C1_MULTIAGENT_ARCHITECTURE_PLAN.md` v1.0 — all six phases complete

What remains falls into one category: Phase 2 product features — larger
scope, require separate planning.

---

## Phase 2 Product Features

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
| 6 | Party ID resolution | Phase 2 | — | Medium-large | Parties API |
| 8 | Approval workflows | Phase 2 | — | Large | — |
| 9 | Five user roles and authority matrix | Phase 2 | — | Large | — |
| 10 | Document control system integration | Phase 2 | — | Large | — |
