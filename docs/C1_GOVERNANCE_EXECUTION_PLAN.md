# C1 Intelligence — Governance Execution Plan

**Version:** 1.0
**Date:** April 2026
**Status:** Active workstream
**Author:** Strategic Partner (Claude)
**Approved by:** Yasser Darweesh

---

## 1. Problem Statement

The governance feature is structurally complete — three database tables
(governance_parties, governance_events, governance_run_log), five API
endpoints, two SME skill files, and a full frontend panel — but the /run
endpoint is a stub. It creates a log entry and returns. It never invokes
the Compliance SME. Clicking "Establish Governance" spins and produces nothing.

---

## 2. Design

The skill files define a mandatory two-phase sequence with a user
confirmation gate between phases:

Phase 1: Party and role identification
  → Compliance SME scans all project documents
  → Produces entity registry (organisations + individuals)
  → Writes to governance_parties
  → run_log status: parties_identified

USER REVIEWS ENTITY REGISTRY
  → Confirms or flags each party
  → Clicks "Confirm Parties & Establish Governance"

Phase 2: Governance establishment
  → Compliance SME scans all project documents using confirmed entity registry
  → Extracts authority events (appointments, delegations, terminations, etc.)
  → Writes to governance_events
  → run_log status: complete

Design principle: The Compliance SME uses its tools (search_chunks,
get_document) to retrieve documents from the warehouse. The governance
runner kicks it off with a targeted query and lets it retrieve.

Structured output: The governance runner appends a JSON output instruction
to the SME query. The SME produces its full analysis text AND a delimited
JSON block (delimited with ~~~json_registry and ~~~json_events). The runner
parses the JSON block deterministically and writes to the DB.

---

## 3. Migration 019 — Applied

Supabase project bkkujtvhdbroieffhfok. Applied as 019_governance_execution_schema.

Changes:
- governance_parties.confirmation_status: text NOT NULL DEFAULT 'inferred'
  CHECK (confirmed / inferred / flagged)
- governance_run_log.status constraint updated to include 'parties_identified'
- governance_run_log.phase: integer NOT NULL DEFAULT 1

---

## 4. Tasks

### A1 — Migration 019 ✅ COMPLETE
Applied directly via Supabase MCP.

### B1 — specialist_config.py
Add compliance SME entry to SPECIALIST_CONFIGS:
  "compliance": SpecialistConfig(domain="compliance", tier=2,
    round_assignment=2, max_tool_rounds=5)
max_tool_rounds=5 — governance scans many document types.

### B2 — src/agents/governance_runner.py (new file)
Phase 1 function: run_party_identification(project_id, run_id)
  - Instantiate BaseSpecialist(config=SPECIALIST_CONFIGS["compliance"])
  - Call sme.run() with PARTY_ID_QUERY (see below)
  - Parse ~~~json_registry block from findings.findings
  - Write to governance_parties
  - Update run_log to parties_identified

Phase 2 function: run_governance_establishment(project_id, run_id)
  - Fetch confirmed parties from governance_parties
  - Call sme.run() with GOVERNANCE_EST_QUERY including entity registry context
  - Parse ~~~json_events block from findings.findings
  - Resolve party_canonical_name → party_id via governance_parties lookup
  - Write to governance_events
  - Update run_log to complete

PARTY_ID_QUERY instructs the SME to:
  1. Execute party and role identification skill
  2. Append ~~~json_registry block with organisations[] and individuals[]
  Each entry: canonical_name, aliases[], contractual_role,
  terminus_node (bool), confirmation_status (confirmed/inferred)

GOVERNANCE_EST_QUERY instructs the SME to:
  1. Execute governance establishment skill using provided entity registry
  2. Append ~~~json_events block with events[]
  Each entry: event_type, effective_date, end_date, party_canonical_name,
  role, appointed_by_canonical_name, authority_dimension,
  contract_source, scope, terminus_node, extraction_status

JSON parse: regex r'~~~json_registry\s*(.*?)\s*~~~json_registry' with re.DOTALL
On parse failure: mark run_log failed, log error, return — never proceed silently.

### C1 — src/api/schemas.py
Add GovernancePartyResponse model:
  id, project_id, entity_type, canonical_name, aliases,
  contractual_role, terminus_node, confirmation_status, created_at
Add ConfirmPartiesRequest model (empty body).
Add parties_count: int = 0 to GovernanceStatusResponse.

### C2 — src/api/routes/governance.py — modify /run + /status
/run: add BackgroundTasks parameter, launch run_party_identification as
  background task after creating run_log entry.
/status: add parties_identified state detection — check for run_log entries
  with status='parties_identified' when no complete run exists.
  Return status='parties_identified' with parties_count when applicable.

### C3 — src/api/routes/governance.py — new endpoints
GET /parties → list all governance_parties for project (GovernancePartyResponse[])
PATCH /parties/{party_id} → update confirmation_status (confirm / flag)
POST /confirm-parties → verify ≥1 confirmed party, create phase=2 run_log
  entry, launch run_governance_establishment background task.

### D1 — frontend/src/api/types.ts
Add GovernancePartyResponse interface.
Update GovernanceStatusResponse: add parties_count field,
  add 'parties_identified' to status union type.

### D2 — frontend/src/api/governance.ts
Add: listGovernanceParties(projectId) → GovernancePartyResponse[]
Add: updateGovernanceParty(projectId, partyId, {confirmation_status}) → GovernancePartyResponse
Add: confirmParties(projectId) → GovernanceRunResponse

### D3 — frontend/src/components/governance/GovernancePanel.tsx
When status.status === 'parties_identified':
  - Show "Parties Identified" amber badge
  - Show parties count and "review and confirm before proceeding" message
  - Fetch and display entity registry table:
      Columns: Type | Canonical Name | Contractual Role | Terminus | Status | Actions
      Status badges: Confirmed (green) / Inferred (amber) / Flagged (red)
      Actions: Confirm button (if not confirmed), Flag button (if not flagged)
  - Show "Confirm Parties & Establish Governance" button
      Disabled if 0 confirmed parties or while running
      On click: calls confirmParties() then re-fetches status
When status.status === 'established' or 'stale':
  - Show existing event log (unchanged)

### E1 — BUILD_LOG.md session close

---

## 5. Execution Sequence

B1 → B2 → C1 → C2 → C3 → D1 → D2 → D3 → E1

One commit per task. QG PASS required before next task.

---

## 6. Database State After A1

19 migrations (001–019). 15 tables unchanged. governance_parties gains
confirmation_status column. governance_run_log gains phase column and
parties_identified status.

---

## 7. Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Date | April 2026 |
| Location | docs/C1_GOVERNANCE_EXECUTION_PLAN.md |
