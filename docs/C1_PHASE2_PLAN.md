# C1 Intelligence — Phase 2 Product Plan

**Date:** April 2026
**Status:** Planning — no work started. This document records the strategic
assessment of each Phase 2 feature and the conditions under which each should
be built.

---

## Context

The C1 platform is fully operational. The core capability — ingest project
documents, reason across them using a three-tier multi-agent architecture,
detect contradictions, and produce forensic-grade responses with full source
attribution — is built and live.

What remains are five features that expand the platform's scope. None of them
are required for C1 to function. None are technically blocked. They are product
decisions: each one represents a choice about what C1 should become and for
whom.

The decision that should precede any of this work: what does C1 need to
demonstrate to reach its first paying client or pilot project? The answer to
that question determines which feature gets built first.

---

## Feature 1 — Cross-Specialist Contradiction Detection

**Scope:** Medium
**Current state:** `contradiction_cross.py` returns `[]` intentionally. The
intra-document contradiction detection (`contradiction.py`) is fully working.
**Prerequisite:** None. This is purely a code change.

### What it is
When multiple orchestrators analyse the same documents, they may reach
conflicting conclusions about the same field. For example: the Legal
orchestrator identifies a Completion Date of 15 March 2025 from the contract,
while the Schedule SME identifies a current programme completion of 22 June
2025 from the latest programme submission. C1 should detect and surface that
conflict.

Currently `contradiction_cross.py` is a stub that returns an empty list.
The `ContradictionFlag` model and write-back infrastructure already exist.

### Why build it
This directly strengthens C1's core value proposition. A platform that detects
contradictions *between* specialists is more forensically credible than one
that only detects contradictions within a single document. It is the only Phase
2 item that makes C1 smarter rather than bigger.

### What is needed
- Implement `cross_specialist_contradiction_pass(all_findings)` in
  `contradiction_cross.py`
- Compare `SpecialistFindings` across orchestrators for conflicting values on
  the same named field (completion dates, contract values, notice periods, etc.)
- Integrate with the existing `ContradictionFlag` model and
  `write_contradiction_flags()` write-back

### When to build
Before the first client demonstration. This is the one feature on this list
that should not wait for a commercial trigger.

---

## Feature 2 — User Roles and Authority Matrix

**Scope:** Medium-large
**Current state:** All authenticated users have identical access within a
project. RLS enforces project-level isolation but not role-level permissions.
**Prerequisite:** None technically. Requires a product decision on the five
roles.

### What it is
Five roles within a project workspace:

| Role | Capabilities |
|---|---|
| Owner | Full access — create, upload, query, manage members |
| Admin | Upload, query, manage members — cannot delete project |
| Legal | Query only — no upload, no member management |
| Commercial | Query only — no upload, no member management |
| Viewer | Query only — read-only access |

### Why build it
Required before C1 is used by more than one person per organisation. A lender,
auditor, or legal counsel accessing a project should not have the same
permissions as the project manager who ingested the documents. Without roles,
C1 cannot be safely shared within a client organisation.

### What is needed
- New `project_members` table with `role` column
- RLS policy updates on all project-scoped tables
- API endpoints: invite member, list members, update role, remove member
- Frontend: member management UI within project workspace
- Auth middleware update: resolve user role on each request

### When to build
When onboarding a second organisation or when a client explicitly requires
role separation. Not before.

---

## Feature 3 — Party ID Resolution

**Scope:** Medium-large
**Current state:** `issuing_party_id` and `receiving_party_id` on documents
are always NULL. The `parties` table exists but nothing writes to it.
**Prerequisite:** User Roles should precede this — parties are project-scoped
and access control matters.

### What it is
When a document is ingested, C1 currently extracts metadata including who
issued it and who received it — but stores those as text fields only, not as
resolved entity references. Party ID resolution means: the "Engineer" in a
notice is resolved to the actual entity (e.g. Mott MacDonald) registered in
the project's parties register, and linked via foreign key.

### Why build it
Forensic traceability. When C1 says "the Engineer issued a notice on 3 March",
it should be able to say exactly which legal entity that was, with their full
registered details. This matters for dispute resolution, where the precise
identity of parties to a communication can be material.

### What is needed
- API endpoints: create party, list parties, assign party role to project
- Frontend: parties management UI within project workspace
- Ingestion pipeline update: attempt to resolve issuing/receiving party from
  document metadata against the parties register at ingestion time
- Fallback: if party cannot be resolved, store as unresolved text (current
  behaviour) — do not block ingestion

### When to build
When a client's use case requires it — typically when C1 is being used for
active dispute preparation rather than general project intelligence.

---

## Feature 4 — Approval Workflows

**Scope:** Large
**Current state:** Not started. No schema, no API, no frontend.
**Prerequisite:** User Roles must be built first. Approvals without role
enforcement are meaningless.

### What it is
Structured approval workflows for documents, variations, and payment
certificates within the C1 platform. A document or event enters a workflow,
moves through defined states (Submitted → Under Review → Approved / Rejected),
and each state change is recorded with the approving user, timestamp, and
comments.

### Why build it
Construction projects run on approvals. If C1 can not only analyse documents
but also manage the approval chain for variations and payment certificates, it
moves from a query tool to an active project management platform. This
represents a significant expansion of C1's scope and commercial proposition.

### What is needed
- Schema: `workflows`, `workflow_steps`, `workflow_events` tables
- State machine logic in the API layer
- Notification system (email or in-platform)
- Authority matrix enforcement — who can approve what
- Frontend: workflow dashboard, approval UI, audit trail view

### When to build
Only after User Roles are live and validated. Requires a separate planning
session. Do not scope this as a sprint task — it is a product workstream.

---

## Feature 5 — Document Control System Integration

**Scope:** Large
**Current state:** Not started. Manual upload only.
**Prerequisite:** None technically. Commercially requires an API agreement or
access credentials for the target system.

### What it is
Integration with document control systems used on GCC projects — primarily
Aconex, with Docutrack as a secondary target. C1 would ingest documents
directly from the project's document management system rather than requiring
manual upload, using the system's API to pull documents as they are issued and
transmitted.

### Why build it
Manual upload is the primary friction point for C1 on a live project. A project
generating 50–100 documents per week cannot rely on a team member manually
uploading each one. Direct integration removes this friction entirely and makes
C1 a passive intelligence layer that requires no operational overhead.

### Why not build it yet
This is a commercial and technical commitment. It requires:
- API access agreements with Aconex and/or Docutrack
- Authentication handling for the client's instance of those systems
- Ongoing maintenance as those APIs evolve
- Testing against a live project environment

It also raises a product question: should C1 own the integration, or should
it expose a webhook/API that allows document control systems to push to C1?
The second approach is simpler and puts the integration burden on the client's
IT team.

### When to build
When a specific client with a specific document control system commits to a
pilot. Build to that client's system, not generically.

---

## Recommended Build Order

| Priority | Feature | Trigger |
|---|---|---|
| 1 | Cross-specialist contradiction detection | Build now — no trigger needed |
| 2 | User roles and authority matrix | Second organisation onboarding |
| 3 | Party ID resolution | Client requires it for dispute use case |
| 4 | Approval workflows | After roles live; separate planning session |
| 5 | Document control integration | Specific client + specific system |

---

## The Question to Answer First

Before any of items 2–5 are built, one question should be answered:

**What does C1 need to demonstrate to reach its first paying client?**

If the answer is "a clean query response with contradiction detection across
domains" — then only Feature 1 needs to be built and the platform is ready
for a first demonstration today.

If the answer is "a multi-user workspace that a project team can use
collaboratively" — then Features 2 and 3 come before a demonstration.

If the answer is "a platform that replaces the document control workflow" —
then Features 4 and 5 define the roadmap.

These are different products with different build timelines and different
commercial propositions. The right answer to that question should drive
everything that follows.
