# C1 Intelligence — Governance Authority Log Design

**Version:** 1.0
**Date:** April 2026
**Status:** Approved for implementation
**Author:** Strategic Partner (Claude)
**Approved by:** Yasser Darweesh

---

## 1. Purpose

This document defines the complete architecture for the C1 Governance
Authority Log — the system that records every event that created, changed,
extended, restricted, transferred, or terminated a party's role and authority
on a construction project.

It supersedes the prototype governance feature (governance_parties,
governance_events tables in their current form). The prototype demonstrated
the concept and established the extraction pipeline. This design replaces
the data model with one that is forensically correct.

---

## 2. Why the Current Model Is Insufficient

### 2.1 One role per party

governance_parties.contractual_role stores a single text field. In reality,
a party can hold multiple roles simultaneously (Lead Design Consultant and
Contract Administrator after novation) or sequentially (PMC until
termination, then scope transferred). A single field cannot represent this.

### 2.2 No appointment status

governance_events.extraction_status has three values: confirmed, inferred,
flagged. This conflates two different concepts:

- How certain is the identification (confirmed vs inferred)
- What is the legal status of the event (proposed, pending, executed)

A nominated subcontractor named in the contract appendix but never formally
appointed is "confirmed" in the current model — the name was found in a
retrieved document. But they have no contractual standing. The current model
cannot distinguish this from a party with an executed appointment instrument.

### 2.3 No preceding event chain

Events are stored as independent records with no link to the event they
modify or supersede. The system cannot determine that a consultant's AED
1,500,000 variation approval threshold came from the PMC's Amendment No. 3,
carried over through a novation. The authority chain is broken.

### 2.4 No actor fields

appointed_by_party_id exists on governance_events but records only one
actor. There is no distinction between who initiated the event and who
authorised it. A contractor sending a termination notice (initiated) is not
the same as the employer approving the termination (authorised). This
distinction is a compliance test in itself.

### 2.5 No missing action tracking

When an event is Pending (initiated but not authorised), the system must
record what is missing — which party needs to act, what instrument is
required. The current model has no field for this.

### 2.6 No assumption register

When the user declares something the system cannot confirm from documents,
that declaration must be recorded with user identity, verbatim text, and
date. The current model has no assumption provenance fields.

### 2.7 Orphan tables in the broader schema

The parties table (Migration 001) is never written to by any current code.
skill_loader._generate_project_context() reads from it and from contracts
(which also has zero writes from current code). Both tables exist from the
original schema but are dead weight. contracts also contains a fidic_edition
field that violates the platform's universal (form-agnostic) design principle.

---

## 3. Existing Bugs and Dead Code — Full Audit

The following issues were identified by direct inspection of the live
codebase. They are recorded here so the implementation plan can address
them in the correct sequence.

### 3.1 Dead database tables

| Table | Status | Issue |
|---|---|---|
| parties | Dead | Never written to by any current code. Read by skill_loader but returns empty. Referenced by documents.issuing_party_id and receiving_party_id as foreign keys — both always NULL. |
| contracts | Dead | Never written to by any current code. Read by skill_loader but returns empty. Contains FIDIC-specific fidic_edition column. |

Resolution: Both tables remain in the schema for now — dropping them
requires removing foreign key references on documents. They are explicitly
noted as dead. Migration 021 will address them once the governance authority
log replaces their intended function.

### 3.2 skill_loader._generate_project_context() — known backlog item

This function queries the dead contracts and parties tables and constructs
a context block that references fidic_edition. Since both tables are always
empty, it silently produces "No contracts or parties have been registered for
this project yet." Resolution: once the governance identity register is live,
this function is rewritten to query party_identities and party_roles instead.

### 3.3 documents.fidic_clause_ref

The documents table has a fidic_clause_ref column populated by the metadata
extractor. The column name is FIDIC-specific but does not affect any agent
reasoning — metadata storage and display only. Low priority. Rename to
standard_clause_ref in a future migration.

### 3.4 src/agents/specialists/ directory

Contains only __init__.py with a docstring. No specialist classes are defined
here — all agents use BaseSpecialist directly. Dead directory. Remove in
housekeeping.

### 3.5 Procfile

Procfile exists at repo root. Railway uses railway.json with a Dockerfile
builder — the Procfile is never read. Dead file. Remove in housekeeping.

### 3.6 risk_mode parameter

SubmitQueryRequest.risk_mode: bool = False is passed through to QueryRequest
but is not used anywhere in the agent pipeline. Dead parameter. Remove in
housekeeping.

### 3.7 governance_events.terminus_node

terminus_node is stored on both governance_parties and governance_events.
Terminus status is a property of the party's identity, not of individual
events. The event-level field is redundant and inconsistently populated.
Remove from events table in Migration 021.

### 3.8 Current governance model is a prototype

governance_parties, governance_events, and governance_run_log in their
current form are superseded by this design. The tables will be replaced by
the three-level model defined in Section 5. Data currently in these tables
(from test runs) is discarded — it was extracted by a prototype system
against test data and has no production value.

---

## 4. Foundational Principles

### 4.1 The log is the primary output

The governance output is not a party table. It is a chronological Party
Authority Log — a record of every event that created, changed, extended,
restricted, transferred, or terminated a party's role and authority. The
party table is a derived view of the log, not the source.

### 4.2 Roles are not static

A party's authority at any point in time is determined by reading their log
from first event to that date and applying all modifications, additions, and
terminations. A static role field is never sufficient.

### 4.3 Appointment status is separate from confirmation status

- Appointment status — the legal state of the event: Proposed (named but
  no appointment instrument), Pending (initiated but not authorised),
  Executed (binding instrument exists or user-declared assumption).
- Confirmation status — how certain the system is: Confirmed (from retrieved
  document), Assumed (user-declared).

These are two independent dimensions. An event can be Executed-Confirmed
(binding instrument retrieved), Executed-Assumed (binding instrument declared
by user but not retrieved), Pending-Confirmed (initiation document retrieved,
authorisation document not found), or Proposed-Confirmed (nomination found in
retrieved document, no appointment instrument).

### 4.4 Every actor field is populated separately

Two actors on every event: who initiated it, who authorised it. These may be
the same party. They are never collapsed into one field. Where authorisation
is absent or unconfirmed, that is explicitly recorded and propagates to the
event's appointment status (Pending).

### 4.5 Assumptions are first-class records

A user declaration that fills a documentary gap is a record with: the exact
text of the user's statement, the user's identity, the date of the
declaration, and the question that prompted it. Every downstream compliance
finding that depends on an assumption cites the assumption record by ID.

### 4.6 Missing actions are surfaced, not suppressed

When an event is Proposed or Pending, the system records explicitly what is
missing: which party must act, what instrument is required, and whether a
contractual deadline applies.

### 4.7 The log is the compliance agent's source of truth

The compliance agent does not re-read contract documents to determine who
had authority at a given date. It reads the authority log. The log cites
the documents. This separation is what makes compliance analysis fast,
consistent, and auditable.

---

## 5. Three-Level Data Model

### Level 1 — Legal Identity Register (party_identities)

One record per legal entity. Establishes who the party is, independent of
any specific role or contract.
party_identities
├── id                        uuid PK
├── project_id                uuid FK → projects
├── entity_type               text  organisation | individual
├── legal_name                text  Registered legal name (contract execution block)
├── trading_names             text[] All trading names and abbreviations found
├── registration_number       text  CR / trade licence number if available
├── party_category            text  See Section 6 taxonomy
├── is_internal               bool  True if part of Employer's organisation
├── identification_status     text  confirmed | assumed
├── assumption_id             uuid FK → assumption_register (if assumed)
└── created_at                timestamptz

Notes:
- legal_name is the authoritative name from the contract execution block.
- trading_names replaces the current aliases array — every name variant
  found across all warehouse documents.
- registration_number is optional but is the definitive reconciliation anchor
  when available (CR number, DED registration, etc.).
- party_category is assigned by the reconciliation interview, not by document
  extraction alone. The SME proposes; the user confirms.
- is_internal drives the Internal / External tab split in the UI.

### Level 2 — Role and Authority Records (party_roles)

One record per role held by a party under a specific instrument. A party may
have multiple simultaneous or sequential role records.
party_roles
├── id                        uuid PK
├── party_identity_id         uuid FK → party_identities
├── project_id                uuid FK → projects
├── role_title                text  Role as it appears in the source instrument
├── role_category             text  Maps role to standard category (Section 6)
├── governing_instrument      text  Name of the instrument that creates this role
├── governing_instrument_type text  main_contract | appointment_letter |
│                                   delegation_letter | novation_agreement |
│                                   board_resolution | correspondence | other
├── effective_from            date  Date this role takes legal effect
├── effective_to              date  Date this role ends — null if ongoing
├── authority_scope           text  What the party can do in this role
├── financial_threshold       text  Monetary limit if applicable
├── financial_currency        text  Currency of the threshold
├── counterparty_id           uuid FK → party_identities
├── appointment_status        text  proposed | pending | executed
├── source_document_id        uuid FK → documents
├── source_clause             text  Specific clause or section reference
├── confirmation_status       text  confirmed | assumed
├── assumption_id             uuid FK → assumption_register (if assumed)
├── preceding_role_id         uuid FK → party_roles (role this supersedes)
└── created_at                timestamptz

Notes:
- One party may have multiple active role records simultaneously.
- preceding_role_id creates the chain — this role supersedes that role.
- Only Executed roles are treated as conferring actual authority.

### Level 3 — Authority Event Log (authority_events)

One record per event that created, changed, or ended a role record.
authority_events
├── id                        uuid PK
├── project_id                uuid FK → projects
├── party_role_id             uuid FK → party_roles
├── party_identity_id         uuid FK → party_identities (denormalised)
├── event_type                text  See Section 7 taxonomy
├── appointment_status        text  proposed | pending | executed
├── event_date                date  Date event takes legal effect
├── event_date_certain        bool  False if date is inferred or unknown
├── end_date                  date  If event has a defined end
├── initiated_by_party_id     uuid FK → party_identities
├── authorised_by_party_id    uuid FK → party_identities (null if absent)
├── authority_before          text  What party could do before this event
├── authority_after           text  What party can do after this event
├── financial_threshold_before text
├── financial_threshold_after  text
├── missing_action            text  Required to execute (for proposed/pending)
├── missing_action_party_id   uuid FK → party_identities (who must act)
├── missing_deadline          date  Contractual deadline if applicable
├── source_document_id        uuid FK → documents
├── source_clause             text
├── instrument_status         text  retrieved | referenced_only | absent
├── confirmation_status       text  confirmed | assumed
├── assumption_id             uuid FK → assumption_register (if assumed)
├── preceding_event_id        uuid FK → authority_events
├── reconciliation_question_id uuid FK → reconciliation_questions
└── created_at                timestamptz

### Supporting Table — Assumption Register (assumption_register)

One record per user declaration that fills a documentary gap.
assumption_register
├── id                        uuid PK
├── project_id                uuid FK → projects
├── question_posed            text  The exact question asked of the user
├── evidence_available        text  Summary of documentary evidence at time
├── user_statement            text  User's exact answer — recorded verbatim
├── declared_by               uuid FK → auth.users
├── declared_at               timestamptz
├── reconciliation_question_id uuid FK → reconciliation_questions
└── superseded_by             uuid FK → assumption_register (if revised)

### Supporting Table — Reconciliation Questions (reconciliation_questions)

Records each question asked during the reconciliation interview.
reconciliation_questions
├── id                        uuid PK
├── project_id                uuid FK → projects
├── run_id                    uuid FK → governance_run_log
├── question_type             text  name_variant | role_conflict |
│                                   missing_party | unmatched_name |
│                                   hierarchy_placement | scope_change |
│                                   role_absorption | mandatory_role_assignment
├── question_text             text  Full question as presented to user
├── parties_referenced        uuid[] Party identity IDs relevant to question
├── documents_referenced      uuid[] Document IDs cited as evidence
├── options_presented         jsonb  Array of options shown to user
├── answer_selected           text  Option chosen
├── user_free_text            text  User's additional comment
├── answered_by               uuid FK → auth.users
├── answered_at               timestamptz
├── sequence_number           integer Order within the interview
└── created_at                timestamptz

---

## 6. Party Category Taxonomy

Applies to party_identities.party_category. Derived from roles that exist
across all major contract forms — FIDIC, NEC, JCT, PMBOK — using the most
widely recognised terminology.

**Internal (Employer's Organisation)**
- employer — The contracting authority or client entity
- employer_representative — Named representative of the employer
- funder — Lender, bank, or financing institution
- parent_affiliate — Parent company, holding entity, or affiliate

**Contract Administration**
- contract_administrator — Engineer (FIDIC), Supervisor (NEC), Contract
  Administrator (JCT), Project Manager (NEC Option C/D), or equivalent
- resident_engineer — Site-based representative of the contract administrator
- independent_certifier — Required under Silver Book or Turnkey arrangements

**Main Contractor**
- main_contractor — Principal contracting party
- contractors_representative — Named representative of the main contractor

**Subcontractors**
- nominated_subcontractor — Nominated by the Employer under the main contract
- domestic_subcontractor — Appointed by the Contractor at their discretion
- specialist_subcontractor — Specialist scope subcontractor
- supplier_manufacturer — Supply-only party

**Consultants**
- design_consultant — Architect, structural, MEP, or other design discipline
- cost_consultant — Quantity surveyor or cost manager
- project_management_consultant — PMC or programme manager
- planning_consultant — Scheduler or programme consultant
- clerk_of_works — Site inspector or quality inspector

**Statutory and Regulatory**
- competent_authority — Government body, municipality, or regulatory authority
  with jurisdiction over the project (FIDIC: Competent Authority)
- utility_authority — Utility provider with statutory connection rights
- statutory_inspector — Approved inspector with statutory certification role

**Dispute Resolution**
- dab_daab — Dispute Adjudication Board (FIDIC 1999) or Dispute Avoidance
  and Adjudication Board (FIDIC 2017)
- arbitral_tribunal — Arbitration panel or sole arbitrator
- expert_mediator — Independent expert or mediator

**Financial and Legal**
- insurer — Project insurer (CAR, TPL, PI, or decennial)
- surety — Bond or guarantee provider
- legal_counsel — Legal advisors (not a contract party — appears in
  correspondence only)

**Other**
- unclassified — Cannot be placed in any other category from available evidence

---

## 7. Event Type Taxonomy

Applies to authority_events.event_type.

| Event type | Definition |
|---|---|
| nomination | Party named in a document but no appointment instrument exists. Always sets appointment_status to Proposed. |
| appointment | Binding instrument appoints party to a role. Sets appointment_status to Executed when authorised. |
| authority_grant | Specific authority delegated to an already-appointed party. Supplements an existing role. |
| scope_addition | Existing appointment extended — additional scope or increased financial threshold. |
| scope_reduction | Existing appointment reduced in scope or financial threshold. |
| role_transfer | Scope and authority moved from one party to another. Creates a new role record for the receiving party. |
| novation | Formal legal substitution of one party for another under a specific instrument. |
| replacement | One party replaced by another in the same role. Original party's role terminated; new role record created. |
| suspension | Authority temporarily suspended. Requires a corresponding reinstatement or termination event. |
| termination | Appointment ended. With or without cause — the distinction is recorded in authority_after. |

---

## 8. Appointment Status Definitions

| Status | Meaning | Compliance agent treatment |
|---|---|---|
| Proposed | Party named or nominated. No binding appointment instrument. | No contractual standing. Cannot be used as an authority chain link. |
| Pending | Action initiated. Authorisation by required party not yet confirmed. | Event has no legal effect until authorised. Authority unchanged from preceding event. |
| Executed | Binding instrument exists — retrieved from warehouse or user-declared as assumption. | Full legal effect from event_date. Used in all authority chain determinations. |

---

## 9. Reconciliation Interview Design

### 9.1 When the interview runs

Between Phase 1 (party identification) and Phase 2 (event extraction).
Phase 2 does not begin until the interview is complete and all mandatory
roles have been resolved or declared as assumptions.

### 9.2 Question types

Eight question types, triggered by specific conditions found during
Phase 1 extraction:

**Type 1 — Name variant reconciliation**
Triggered when: the same legal entity appears under materially different
names across different retrieved documents.
Resolution: user confirms same entity or identifies them as distinct.

**Type 2 — Role conflict**
Triggered when: the same party is described with different roles in
different retrieved documents.
Resolution: user confirms which role governs and from which instrument.

**Type 3 — Missing party**
Triggered when: a document references a role but no party has been
identified holding that role.
Resolution: user identifies the party or confirms the role is unfilled.

**Type 4 — Unmatched name**
Triggered when: a name appears in a retrieved document that cannot be
matched to any registered identity.
Resolution: user maps to existing identity, creates new one, or confirms
typographical error.

**Type 5 — Hierarchy placement**
Triggered when: a party has been identified but their position in the
authority hierarchy cannot be determined.
Resolution: user places them under the correct party.

**Type 6 — Scope change or amendment**
Triggered when: a contract amendment appears to change a party's scope
or authority.
Resolution: user confirms the operative authority position following
the amendment.

**Type 7 — Role absorption**
Triggered when: documents suggest one party's scope was absorbed by
another (e.g. PMC termination followed by consultant performing PMC
functions).
Resolution: user confirms the transfer and its effective date.

**Type 8 — Mandatory role assignment**
Triggered when: the governing contract form (retrieved from Layer 2b)
requires a named role holder not identified in retrieved documents.
Resolution: user declares who holds this role. Recorded as assumption
if no supporting document is available.

### 9.3 Interview UI principles

- One question at a time, presented sequentially.
- Each question shows: the specific discrepancy or gap, the document
  references that triggered it, and 3-5 options derived from the warehouse
  plus a free-text option.
- User can flag a question for later resolution — it remains Pending.
- Progress indicator shows questions answered / remaining.
- Every answer recorded to reconciliation_questions immediately on
  submission — no batch save.
- Session can be paused and resumed — interview state is persisted.

---

## 10. Compliance Agent Integration

### 10.1 Authority position at a specific date

The compliance agent calls a deterministic function (no LLM):

  get_party_authority(party_identity_id, date) → AuthorityPosition

This function:
1. Reads all authority_events for this party ordered by event_date
2. Applies events up to and including the specified date
3. Returns current role, authority scope, financial threshold,
   appointment status, and any assumptions the result depends on

### 10.2 Authority chain validation

When validating whether a specific action was within authority:

1. Identify the acting party from the document
2. Look up their party_identity_id from the identity register
3. Call get_party_authority(party_identity_id, action_date)
4. Check: appointment_status == Executed
5. Check: authority_scope covers the action type
6. Check: financial_threshold >= action_value (if applicable)
7. Return: VALID | INVALID | CANNOT_CONFIRM with the log entry cited

### 10.3 Assumption citation

Every compliance finding that depends on an assumption states:
"This finding depends on the assumption declared by [user] on [date]:
'[verbatim statement]' (Assumption ID: [uuid]). If this assumption is
incorrect, this finding is affected."

---

## 11. What Changes in the Current Codebase

### 11.1 Database — what is replaced

| Current table | Disposition |
|---|---|
| governance_parties | Replaced by party_identities + party_roles |
| governance_events | Replaced by authority_events |
| governance_run_log | Retained — add reconciliation_complete bool and interview_run_id |
| parties (Migration 001) | Retained but explicitly dead — Migration 021 |
| contracts (Migration 001) | Retained but explicitly dead — Migration 021 |

New tables: party_identities, party_roles, authority_events,
assumption_register, reconciliation_questions.

Migration 021 creates new tables and drops governance_parties and
governance_events (prototype tables with no production data).

### 11.2 Backend — what changes

governance_runner.py — Phase 1 rewrites to populate party_identities and
party_roles. Phase 2 rewrites to populate authority_events. New Phase 1.5
(reconciliation interview) added between them.

src/api/routes/governance.py — all existing endpoints updated to reference
new tables. New endpoints for reconciliation interview.

src/api/schemas.py — new response models for all three levels.

skill_loader._generate_project_context() — rewritten to query
party_identities and party_roles instead of dead parties and contracts tables.

src/agents/tools.py — new deterministic tool get_party_authority(party_id,
date) available to the compliance SME.

### 11.3 Frontend — what changes

GovernancePanel.tsx — restructured around three phases: Phase 1 output
(identity review), reconciliation interview (new), Phase 2 output (authority
event log). Internal/External tab split. Collapsible sections by
party_category.

### 11.4 Dead code to remove

| Item | Action |
|---|---|
| src/agents/specialists/ directory | Delete — empty, never used |
| Procfile | Delete — superseded by railway.json |
| risk_mode parameter | Remove from SubmitQueryRequest, QueryRequest, all call sites |
| governance_parties, governance_events tables | Drop in Migration 021 |

---

## 12. Migration Plan

| Migration | Content |
|---|---|
| 021 | Create party_identities, party_roles, authority_events, assumption_register, reconciliation_questions. Drop governance_parties and governance_events. Remove terminus_node from governance_events. Add reconciliation fields to governance_run_log. |

No data migration required — governance tables contain only test data
from prototype sessions. governance_run_log is retained for audit continuity.

---

## 13. Build Sequence

Implementation follows this sequence after document approval:
Phase 0: Housekeeping — dead code removal
Delete src/agents/specialists/
Delete Procfile
Remove risk_mode
One commit per item
Phase 1: Migration 021
New tables + drop prototype tables
Phase 2: governance_runner.py Phase 1 rewrite
Party identification populates party_identities + party_roles
Phase 3: Reconciliation interview — backend
New endpoints: serve questions, record answers
Question generation logic
Phase 4: Reconciliation interview — frontend
Interview UI in GovernancePanel
Phase 5: governance_runner.py Phase 2 rewrite
Event extraction populates authority_events
Uses confirmed identity register from interview
Phase 6: Compliance agent integration
get_party_authority() deterministic function
Assumption citation in compliance findings
Phase 7: skill_loader rewrite
_generate_project_context() reads party_identities and party_roles
Phase 8: Frontend — authority log display
Internal/External tabs
Collapsible party categories
Full event log per party with all fields
Phase 9: Governing documents
CLAUDE.md, C1_MASTER_PLAN.md, BUILD_LOG.md

---

## 14. Approval Required Before Build Begins

Before any code is written:

1. Three-level data model (Section 5) — field names and types
2. Party category taxonomy (Section 6) — the 20 categories
3. Event type taxonomy (Section 7) — the 10 event types
4. Appointment status definitions (Section 8) — Proposed / Pending / Executed
5. Reconciliation interview question types (Section 9) — the 8 types
6. Build sequence (Section 13)

---

## 15. Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Date | April 2026 |
| Location | docs/C1_GOVERNANCE_AUTHORITY_LOG_DESIGN.md |
| Supersedes | C1_GOVERNANCE_EXECUTION_PLAN.md (prototype spec) |
| Status | Approved for implementation pending Section 14 sign-off |
