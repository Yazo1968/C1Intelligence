# C1 Intelligence — Governance Feature Redesign
# Clean Slate Design Document

**Version:** 2.0
**Date:** April 2026
**Status:** Approved for implementation
**Author:** Strategic Partner (Claude)
**Approved by:** Yasser Darweesh

---

## 1. Purpose

This document defines the complete redesign of the C1 Governance feature.
The previous implementation is to be fully obliterated — database, backend,
frontend, and skills — before any new code is written.

The redesigned feature has two distinct, sequentially gated functions:

- **Function 1 — Entity Directory:** Identify and confirm every organisation
  and individual named in the project documents. Resolve name discrepancies.
  Produce a confirmed cast of characters. Nothing more.

- **Function 2 — Event Log:** For a selected entity, extract every authority
  event from the documents. Resolve contradictions and gaps with the user.
  Produce a confirmed, locked event log for that entity.

---

## 2. What Must Be Obliterated

### 2.1 Database Tables — Drop All

The following tables must be dropped completely via a new migration.
No data migration. No archiving. Complete removal.

| Table | Origin | Action |
|---|---|---|
| `party_identities` | Migration 021 | DROP |
| `party_roles` | Migration 021 | DROP |
| `authority_events` | Migration 021 | DROP |
| `assumption_register` | Migration 021 | DROP |
| `reconciliation_questions` | Migration 021 | DROP |
| `governance_run_log` | Migration 018 | DROP |
| `parties` | Migration 001 | DROP (dead — never written to) |
| `contracts` | Migration 001 | DROP (dead — never written to, contains fidic_edition) |

Note on `parties` and `contracts`: these two tables were created in
Migration 001 but have never been written to by any code. They are dead
weight. `contracts` also contains a `fidic_edition` column that violates
the platform's universal design principle. This redesign is the correct
moment to remove them.

### 2.2 Backend Files — Delete Entirely

| File | Action |
|---|---|
| `src/api/routes/governance.py` | DELETE |
| `src/agents/governance_runner.py` | DELETE |

### 2.3 Backend Files — Partial Removal

| File | What to Remove |
|---|---|
| `src/api/schemas.py` | Remove all governance-related classes: `GovernanceRunRequest`, `GovernanceRunResponse`, `GovernanceStatusResponse`, `PartyRoleResponse`, `PartyIdentityResponse`, `ReconciliationQuestionResponse`, `ReconciliationAnswerRequest`, `InterviewStatusResponse` |
| `src/api/main.py` | Remove `from src.api.routes.governance import router as governance_router` and `app.include_router(governance_router)` |
| `src/agents/tools.py` | Remove `get_party_authority` tool definition from `ORCHESTRATOR_TOOL_DEFINITIONS` and `TOOL_DEFINITIONS`, remove `_execute_get_party_authority()` function, remove `"get_party_authority": _execute_get_party_authority` from `_TOOL_EXECUTORS` |
| `src/agents/skill_loader.py` | Remove `_generate_project_context()` method entirely. Remove its call from `load()`. The method reads from tables being dropped. |

### 2.4 Skills Files — Delete Entirely

| File | Action |
|---|---|
| `skills/smes/compliance/governance_establishment.md` | DELETE |
| `skills/smes/compliance/party_and_role_identification.md` | DELETE |

These two skill files were written for the old governance design.
The other compliance skills (`compliance_investigation.md`,
`doa_compliance.md`, `signatory_validation.md`,
`statutory_authority_mapping.md`) are retained — they are not
governance-specific.

### 2.5 Frontend Files — Delete or Replace

| File | Action |
|---|---|
| `frontend/src/components/governance/GovernancePanel.tsx` | REPLACE with new implementation |
| `frontend/src/api/governance.ts` | REPLACE with new implementation |

### 2.6 Frontend Files — Partial Removal

| File | What to Remove |
|---|---|
| `frontend/src/api/types.ts` | Remove all governance interfaces: `GovernanceRunResponse`, `GovernanceStatusResponse`, `PartyRoleResponse`, `PartyIdentityResponse`, `ReconciliationQuestionResponse`, `InterviewStatusResponse`, `AuthorityEventResponse` |
| `frontend/src/pages/ProjectWorkspacePage.tsx` | Remove `GovernancePanel` import and the governance tab render block. The `governance` tab entry in `Sidebar.tsx` stays — it will be re-wired to the new panel. |

---

## 3. New Database Schema

One migration creates all new tables. Migration number: 022.

### 3.1 `entity_directory_runs`

Tracks each execution of Function 1 (Entity Directory extraction).

```sql
CREATE TABLE entity_directory_runs (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    status              text NOT NULL DEFAULT 'running',
    -- status values: running | awaiting_confirmation | confirmed | failed
    triggered_at        timestamptz NOT NULL DEFAULT now(),
    completed_at        timestamptz,
    chunks_processed    integer NOT NULL DEFAULT 0,
    total_chunks        integer NOT NULL DEFAULT 0,
    organisations_found integer NOT NULL DEFAULT 0,
    individuals_found   integer NOT NULL DEFAULT 0,
    error_message       text,
    created_at          timestamptz NOT NULL DEFAULT now()
);
```

### 3.2 `entities`

One record per confirmed legal entity (organisation or individual).
This is the Entity Directory. No roles. No scope. No relationships.

```sql
CREATE TABLE entities (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    run_id              uuid NOT NULL REFERENCES entity_directory_runs(id),
    entity_type         text NOT NULL,
    -- entity_type values: organisation | individual
    canonical_name      text NOT NULL,
    -- The confirmed legal name after user resolution
    name_variants       text[] NOT NULL DEFAULT '{}',
    -- All other names found in documents for this entity
    short_address       text,
    -- Registered address or location if stated in documents. Optional.
    title               text,
    -- For individuals only: Mr / Eng / Dr / Arch etc. Not a role.
    confirmation_status text NOT NULL DEFAULT 'proposed',
    -- proposed: extracted, not yet confirmed by user
    -- confirmed: user confirmed this entity
    -- merged: merged into another entity record (canonical_name points to survivor)
    -- rejected: user rejected this extraction as incorrect
    user_note           text,
    -- Free text from user during confirmation
    created_at          timestamptz NOT NULL DEFAULT now()
);
```

### 3.3 `entity_discrepancies`

Name discrepancies detected during extraction that require user resolution.

```sql
CREATE TABLE entity_discrepancies (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    run_id              uuid NOT NULL REFERENCES entity_directory_runs(id),
    discrepancy_type    text NOT NULL,
    -- name_variant: same entity appears under different names
    -- possible_duplicate: two entries that may be the same entity
    -- ambiguous_individual: individual name without enough context
    description         text NOT NULL,
    -- Plain English description of the discrepancy
    name_a              text NOT NULL,
    name_b              text,
    -- The two names in conflict (name_b null for single-name ambiguities)
    chunk_references    text[] NOT NULL DEFAULT '{}',
    -- Document chunk IDs where each name was found
    resolution          text,
    -- same_entity: user confirmed these are the same entity
    -- different_entities: user confirmed these are different entities
    -- correction: user provided the correct canonical name
    resolved_canonical  text,
    -- The canonical name after resolution
    resolved_by         uuid REFERENCES auth.users(id),
    resolved_at         timestamptz,
    user_note           text,
    created_at          timestamptz NOT NULL DEFAULT now()
);
```

### 3.4 `event_log_runs`

Tracks each execution of Function 2 (Event Log extraction) per entity.

```sql
CREATE TABLE event_log_runs (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    entity_id           uuid NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    status              text NOT NULL DEFAULT 'running',
    -- running | awaiting_confirmation | confirmed | failed
    triggered_at        timestamptz NOT NULL DEFAULT now(),
    completed_at        timestamptz,
    chunks_scanned      integer NOT NULL DEFAULT 0,
    events_extracted    integer NOT NULL DEFAULT 0,
    error_message       text,
    created_at          timestamptz NOT NULL DEFAULT now()
);
```

### 3.5 `entity_events`

One record per authority event per entity. The event log.

```sql
CREATE TABLE entity_events (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    entity_id           uuid NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    run_id              uuid NOT NULL REFERENCES event_log_runs(id),
    event_type          text NOT NULL,
    -- nomination | appointment | authority_grant | scope_addition |
    -- scope_reduction | role_transfer | novation | replacement |
    -- suspension | termination
    event_date          date,
    event_date_certain  boolean NOT NULL DEFAULT true,
    -- false if date is inferred or approximate
    status_before       text,
    -- Plain English: what was this entity's authority/role before this event?
    -- null for first event in the log
    status_after        text,
    -- Plain English: what is this entity's authority/role after this event?
    initiated_by        text,
    -- Name of entity who initiated this event (as found in document)
    authorised_by       text,
    -- Name of entity who authorised this event (as found in document)
    -- null if same as initiated_by or not stated
    source_document     text,
    -- Document name/reference as found in the chunk
    source_excerpt      text,
    -- Verbatim short excerpt from the source document evidencing this event
    confirmation_status text NOT NULL DEFAULT 'proposed',
    -- proposed | confirmed | disputed | rejected
    user_note           text,
    -- Free text from user during confirmation
    sequence_number     integer NOT NULL DEFAULT 0,
    -- Chronological order within this entity's log
    created_at          timestamptz NOT NULL DEFAULT now()
);
```

### 3.6 `event_log_questions`

Questions generated after event extraction for the user to resolve.

```sql
CREATE TABLE event_log_questions (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    run_id              uuid NOT NULL REFERENCES event_log_runs(id),
    entity_id           uuid NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    question_text       text NOT NULL,
    -- Plain English question for the user
    question_type       text NOT NULL,
    -- date_conflict | missing_authorisation | overlapping_roles |
    -- termination_without_replacement | gap_in_timeline | ambiguous_event
    events_referenced   uuid[] NOT NULL DEFAULT '{}',
    -- IDs of entity_events this question relates to
    answer              text,
    answered_by         uuid REFERENCES auth.users(id),
    answered_at         timestamptz,
    sequence_number     integer NOT NULL DEFAULT 0,
    created_at          timestamptz NOT NULL DEFAULT now()
);
```

---

## 4. Function 1 — Entity Directory

### 4.1 What it does

Reads every document chunk in the project warehouse sequentially.
Identifies every organisation and individual named in those chunks.
Consolidates name variants. Detects discrepancies. Presents results to
the user for confirmation.

### 4.2 Processing approach

**Batch processing — not retrieval.** All chunks are processed in order,
not searched by similarity. This guarantees completeness regardless of
how many documents are in the warehouse.

Processing runs in batches of 30 chunks per LLM call. Each call asks:
"Who is mentioned in these chunks? Extract organisations and individuals."
Results are accumulated in Python across all batches.

After all batches complete, a consolidation pass groups name variants
and flags discrepancies.

The token budget per call:
- System prompt: ~200 tokens
- 30 chunks × 450 tokens: ~13,500 tokens
- Response: ~2,000 tokens
- Total: ~16,000 tokens per call

For 185 chunks: 7 calls. For 1,000 chunks: 34 calls. Scales linearly.

### 4.3 Extraction schema (LLM output per batch)

```json
{
  "organisations": [
    {
      "name": "Exact name as it appears in this text",
      "context": "One sentence describing how this name appears"
    }
  ],
  "individuals": [
    {
      "name": "Full name as it appears",
      "title": "Mr/Eng/Dr/Arch or null",
      "context": "One sentence describing how this name appears"
    }
  ]
}
```

No roles. No scope. No relationships. Names and context only.

### 4.4 Consolidation pass (Python, no LLM)

After all batches:
1. Group organisations by normalised name (lowercase, stripped punctuation)
2. Group individuals by normalised name
3. For each group with more than one name variant — flag as discrepancy
4. Write consolidated entities to `entities` table with
   `confirmation_status = 'proposed'`
5. Write discrepancies to `entity_discrepancies` table
6. Update `entity_directory_runs` status to `awaiting_confirmation`

### 4.5 User confirmation flow

The user sees:
- List of organisations (proposed)
- List of individuals (proposed)
- List of discrepancies requiring resolution

For each entity: Confirm / Edit name / Reject
For each discrepancy: Same entity (merge) / Different entities / Provide correction

When all discrepancies are resolved and entities confirmed:
- `entities.confirmation_status` → `confirmed` (or `merged` / `rejected`)
- `entity_directory_runs.status` → `confirmed`
- Entity Directory is locked. Function 2 becomes available.

### 4.6 Re-run behaviour

If the user is not satisfied with the result, they can re-run Function 1.
A new `entity_directory_runs` record is created. The previous run's
entities are superseded but not deleted (audit trail). Only the most
recent confirmed run's entities are used by Function 2.

---

## 5. Function 2 — Event Log

### 5.1 What it does

For a selected confirmed entity, extracts every authority event from
the project documents. Presents a draft event log. Asks the user to
resolve any conflicts or gaps. Locks the confirmed log as a record.

### 5.2 How it is triggered

The user clicks an icon on any confirmed entity in the Entity Directory.
Event log extraction runs for that entity only. Other entities are
unaffected.

### 5.3 Processing approach

**Per-entity fulltext search.** For each entity, search all document
chunks for that entity's canonical name and all known name variants
using fulltext/keyword search — not semantic search. Fulltext search
on a proper noun is reliable: it either matches or it does not.

Steps:
1. Retrieve all chunks containing the entity's canonical name or any
   name variant (fulltext search, no limit — return all matching chunks)
2. Sort chunks by chunk_index (chronological document order)
3. For large entities (>60 matching chunks), process in batches of 30
   chunks per LLM call, accumulating events across batches
4. Each call receives: entity name, known variants, and 30 chunks
5. LLM extracts events from those chunks
6. After all batches, a Python consolidation pass deduplicates and
   sorts events chronologically

Token budget per call (worst case):
- System prompt: ~300 tokens
- Entity context (name, variants): ~100 tokens
- 30 chunks × 450 tokens: ~13,500 tokens
- Response: ~3,000 tokens
- Total: ~17,000 tokens per call

A party mentioned in 150 chunks: 5 calls. Fully within limits.

### 5.4 Event extraction schema (LLM output per batch)

```json
{
  "events": [
    {
      "event_type": "appointment",
      "event_date": "YYYY-MM-DD or null",
      "event_date_certain": true,
      "status_before": "What this entity could do before this event, or null for first event",
      "status_after": "What this entity can do after this event",
      "initiated_by": "Name of party who initiated this — exactly as in document",
      "authorised_by": "Name of party who authorised this — null if not stated",
      "source_document": "Document name or reference as found in the text",
      "source_excerpt": "Verbatim short excerpt (max 100 words) evidencing this event"
    }
  ]
}
```

### 5.5 Consolidation pass (Python, no LLM)

After all batches:
1. Deduplicate events with identical event_type + event_date + status_after
2. Sort by event_date (nulls last), then by chunk_index order
3. Assign sequence_number to each event
4. Detect conflicts and gaps — generate questions:
   - Date conflict: two events on the same date with contradicting status_after
   - Missing authorisation: appointment with no authorised_by
   - Gap in timeline: termination with no subsequent replacement where
     the role appears to continue
   - Overlapping events: two appointments with no termination between them
5. Write events to `entity_events` with `confirmation_status = 'proposed'`
6. Write questions to `event_log_questions`
7. Update `event_log_runs.status` to `awaiting_confirmation`

### 5.6 User confirmation flow

The user sees:
- Chronological event log for this entity
- Each event: type, date, status before/after, source excerpt
- Questions requiring resolution (if any)

For each event: Confirm / Edit / Reject
For each question: Answer (free text or selection)

When all questions answered and events reviewed:
- `entity_events.confirmation_status` → `confirmed` / `rejected`
- `event_log_runs.status` → `confirmed`
- Event log is locked as a record for this entity.

### 5.7 Re-run behaviour

User can re-run event extraction for any entity at any time. A new
`event_log_runs` record is created. Previous run's events are superseded
but retained. Only the most recent confirmed run's events represent the
current record.

---

## 6. API Endpoints

All endpoints under `/projects/{project_id}/governance/`.

### Function 1 Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/directory/run` | Trigger Entity Directory extraction |
| GET | `/directory/status` | Get current run status + progress |
| GET | `/directory/entities` | List all proposed entities |
| GET | `/directory/discrepancies` | List all unresolved discrepancies |
| PATCH | `/directory/entities/{entity_id}` | Confirm / edit / reject an entity |
| POST | `/directory/discrepancies/{discrepancy_id}/resolve` | Resolve a discrepancy |
| POST | `/directory/confirm` | Lock the directory (all entities confirmed) |

### Function 2 Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/entities/{entity_id}/events/run` | Trigger event log extraction |
| GET | `/entities/{entity_id}/events/status` | Get run status + progress |
| GET | `/entities/{entity_id}/events` | List all proposed events |
| GET | `/entities/{entity_id}/events/questions` | List unresolved questions |
| PATCH | `/entities/{entity_id}/events/{event_id}` | Confirm / edit / reject event |
| POST | `/entities/{entity_id}/events/questions/{question_id}/answer` | Answer question |
| POST | `/entities/{entity_id}/events/confirm` | Lock event log for this entity |

---

## 7. Frontend — GovernancePanel Redesign

### 7.1 States

The panel has three top-level states:

**State A — No directory yet**
Single button: "Build Entity Directory"
Brief explanation of what this does.

**State B — Directory in progress or awaiting confirmation**
Progress indicator (chunks processed / total chunks).
Once complete: two lists (organisations, individuals) with
confirm/edit/reject controls. Discrepancy cards if any exist.
"Confirm Directory" button (disabled until all discrepancies resolved).

**State C — Directory confirmed**
Collapsed summary of confirmed entities.
Each entity has an icon button "Build Event Log."
Entities with a confirmed event log show a timeline icon.
Entities with a running extraction show a spinner.
Entities with no event log show an empty icon.

### 7.2 Event Log drawer or panel

When the user triggers or views an event log for an entity, a panel
(or slide-over drawer) opens for that entity showing:
- Entity name and variants
- Chronological event timeline
- Questions requiring resolution
- "Confirm Event Log" button

### 7.3 No polling loops

The frontend polls the status endpoint every 5 seconds while a run is
in progress. When status transitions to `awaiting_confirmation`, polling
stops and the confirmation UI is shown.

---

## 8. Backend File Structure

### New files to create

```
src/agents/governance/
├── __init__.py
├── entity_extractor.py      — Function 1: batch chunk processing
├── event_extractor.py       — Function 2: per-entity event extraction
└── consolidator.py          — Python consolidation pass for both functions

src/api/routes/governance.py — Rebuilt from scratch (new endpoints only)
```

### Modified files

```
src/api/schemas.py           — New governance schemas (clean, no old schemas)
src/api/main.py              — Re-register governance router
src/agents/skill_loader.py   — _generate_project_context() reads entities table
src/agents/tools.py          — get_entity_authority() replaces get_party_authority()
```

---

## 9. The get_entity_authority Tool

Once the new schema is in place, the compliance agent tool is rebuilt:

`get_entity_authority(entity_name, date)` →

1. Look up entity in `entities` by canonical_name or name_variants
   (fulltext match — not semantic)
2. Read all confirmed events from `entity_events` for that entity,
   ordered by event_date, up to and including the specified date
3. Return the accumulated authority position at that date:
   - Current status_after from the most recent event
   - Chain of events that led to it
   - Whether any events in the chain are not user-confirmed

This is deterministic. Zero LLM calls. Reads only confirmed records.

---

## 10. What Stays Untouched

The following are completely unaffected by this redesign:

- Query pipeline (`orchestrator.py`, `base_orchestrator.py`, all SMEs)
- Ingestion pipeline
- All skill files except the two compliance skills being deleted
- Document storage, chunk storage, retrieval functions
- Reference document layer (Layer 2b)
- Contradiction detection
- Audit log
- All non-governance API routes

---

## 11. Implementation Sequence

Phases execute in strict order. One commit per task. QG PASS before next.

### Phase 0 — Obliterate (database + backend + frontend)
- 0.1: Migration 022 — drop all old governance tables, create all new tables
- 0.2: Delete `governance_runner.py`, delete old `governance.py` routes
- 0.3: Clean `schemas.py`, `main.py`, `tools.py`, `skill_loader.py`
- 0.4: Delete two old compliance skill files
- 0.5: Clean frontend `types.ts`, `governance.ts`, `ProjectWorkspacePage.tsx`

### Phase 1 — Function 1 Backend
- 1.1: `entity_extractor.py` — batch chunk processor
- 1.2: `consolidator.py` — name grouping and discrepancy detection
- 1.3: `governance.py` routes — Function 1 endpoints
- 1.4: `schemas.py` — Function 1 schemas

### Phase 2 — Function 1 Frontend
- 2.1: `governance.ts` — Function 1 API calls
- 2.2: `types.ts` — Function 1 types
- 2.3: `GovernancePanel.tsx` — States A and B

### Phase 3 — Function 2 Backend
- 3.1: `event_extractor.py` — per-entity event extraction
- 3.2: `consolidator.py` — event dedup, sequencing, question generation
- 3.3: `governance.py` routes — Function 2 endpoints
- 3.4: `schemas.py` — Function 2 schemas

### Phase 4 — Function 2 Frontend
- 4.1: `governance.ts` — Function 2 API calls
- 4.2: `types.ts` — Function 2 types
- 4.3: `GovernancePanel.tsx` — State C + event log panel

### Phase 5 — Compliance Agent Integration
- 5.1: `get_entity_authority()` tool in `tools.py`
- 5.2: `skill_loader._generate_project_context()` reads `entities` table
- 5.3: Governing documents update

---

## 12. Document Control

| Field | Value |
|---|---|
| Version | 2.0 |
| Date | April 2026 |
| Supersedes | C1_GOVERNANCE_AUTHORITY_LOG_DESIGN.md v1.0 |
| Location | docs/C1_GOVERNANCE_REDESIGN.md |
| Status | Awaiting approval before Phase 0 begins |
