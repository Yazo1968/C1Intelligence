# C1 Intelligence — Compliance Feature Plan

**Version:** 0.2 (Draft)
**Date:** April 2026
**Status:** In discussion — not approved for execution
**Owner:** Yasser Darweesh (Product Owner)

---

## 1. Concept and Scope

### 1.1 The Problem Being Solved

Construction projects involve a complex and evolving web of parties,
individuals, and authorities. Documents refer to the same entity in
multiple ways. Individuals act on behalf of organisations under
delegated authority. That authority changes over the project lifecycle —
parties are appointed, replaced, and terminated. Delegations are granted
and revoked.

A project is governed by a body of contracts — the main construction
contract, the PMC appointment, the design consultant agreement,
sub-contract agreements, nominated sub-contractor appointments, and
employer-direct supply agreements. These contracts are interrelated.
The Engineer may be defined in the construction contract but appointed
under a completely separate consultancy agreement. Their authority may
be further defined or limited in their appointment letter. Party and
role identification requires reading across all of these instruments
together, not just the construction contract.

C1 currently has no structured representation of this authority
structure. Agents see party references as raw text. They cannot assess
whether a notice was signed by an authorised individual, whether an
instruction came from a party with authority to give it, or whether a
payment was approved at the right level. This is a fundamental gap for
audit, compliance, entitlement assessment, and dispute resolution.

The compliance feature addresses this gap by introducing a dynamic,
document-grounded authority model that spans the full project lifecycle,
the full body of project contracts, and all three warehouse layers.

### 1.2 The Three Authority Dimensions

Authority in a construction project comes from three distinct sources,
each living in a different layer of the C1 warehouse.

**Contractual project authority — Layer 1**
Authority created by and for this specific project. Defined across the
full body of project contracts — construction contract, PMC appointment,
consultant agreements, sub-contracts, appointment letters, delegation
letters. Governs who can instruct, certify, claim, and act on behalf
of each contractual party. This is the primary dimension — dynamic,
project-scoped, and the focus of this feature.

**Internal corporate DOA — Layer 2a**
The organisation's own Delegation of Authority framework. Governs
internal decision-making — who within the organisation can approve
procurement, sign contracts, authorise payments. Exists independently
of any project but applies to project decisions. Also time-variant —
DOA frameworks are revised and updated during a project's life.

**Statutory authorities — Layer 2b**
Authority that exists by force of law. Municipality, civil defence,
utility authorities, traffic department, regulatory bodies. Their
authority is not conferred by the contract — it derives from
legislation. It is not contestable. The relevant question for C1 is
not the internal structure of a statutory authority but whether a
given entity is a recognised statutory authority, what its jurisdiction
covers, and whether the project has the required interactions with it
documented in the warehouse.

### 1.3 The Dynamic Authority Model

The authority structure of a project is not static. It evolves
continuously across the project lifecycle — from pre-design through
construction to handover and defects. New parties are appointed. Roles
change hands. Delegations are granted and revoked. Statutory approvals
are obtained at specific milestones. Internal DOA frameworks are
revised.

The correct model for representing this is an **event log of authority
events**, not a snapshot org chart. Each event changes the shape of
the authority structure. The authority matrix at any point in time is
derived from all events up to that date. This allows C1 to answer
time-specific forensic questions: who had authority on this date, under
what instrument, and does that authority satisfy the contractual
requirement for this act?

**Event types:**
- **Appointment** — a party or individual takes a role or is granted authority
- **Delegation** — authority is passed from one party or individual to another
- **Termination** — an appointment or delegation ends
- **Replacement** — one party or individual is substituted for another in a role
- **Modification** — the scope of an existing appointment is changed
- **Suspension** — authority is temporarily suspended

Every event is grounded in a source document with an effective date.
Without a source document, an event is inferred — flagged for user
confirmation, not treated as confirmed.

### 1.4 Directionality of Authority

The authority structure is a directed graph, not a flat list. Each
node has defined authority properties:

**Downward authority** — the ability to instruct, direct, or delegate
to parties below. The Employer has it over the Contractor via the
Engineer. The Contractor has it over sub-contractors.

**Upward standing** — the ability to submit claims, notices, and
communications to parties above and have those recognised as
contractually valid. A sub-contractor has upward standing to the
Contractor. Whether that standing extends to the Employer depends
on the contract structure — under most standard forms it does not.

**Terminus nodes** — parties and individuals with no downward
authority. A domestic sub-contractor operates within a defined scope
but cannot instruct anyone above them. A site foreman directs labour
but cannot issue contractually binding instructions. Terminus nodes
are leaf nodes in the authority graph.

### 1.5 Statutory Authorities as a Collective

Statutory authorities are treated differently from contractual parties.
Their authority is not contestable and their internal structure is not
relevant to C1. The forensic questions are:

- Is this entity a recognised statutory authority with jurisdiction
  over this project?
- What approvals, permits, or NOCs are required from this authority?
- Are those interactions documented in the warehouse?

C1 classifies statutory authorities as a collective — binary membership,
jurisdiction scope defined — and tracks whether required interactions
with them are evidenced in the project documents.

### 1.6 The Project Lifecycle Dimension

The authority structure differs fundamentally at each project phase:

- **Pre-design:** Employer, architect, feasibility consultant
- **Design:** Employer, design consultant, early PMC appointment
- **Tender:** Procurement authority structure — who approves tender list,
  bid opening, award recommendation
- **Pre-contract:** Contractor emerges. Letter of Award signatory
  authority matters. Construction contract may not yet be executed.
- **Construction:** Full cast — Employer, PMC or Engineer, design
  consultant, Contractor, nominated and domestic sub-contractors,
  statutory authorities at milestone hold points
- **Handover and defects:** Reduced cast. Different team members on
  both sides from the construction phase.
- **Post-contract / dispute:** Looking back across all phases. Authority
  questions are time-specific — what was the position on a particular
  date?

---

## 2. Agent Architecture Changes

### 2.1 Legal & Compliance Orchestrator

The existing Legal orchestrator is renamed and expanded to
**Legal & Compliance**. Its scope expands to include governance
establishment and compliance investigation as first-class
responsibilities alongside its existing legal analysis functions.

The Legal & Compliance orchestrator synthesises the outputs of the
legal SMEs and the Compliance SME into a single coherent assessment.
This synthesis is performed by the orchestrator agent — it is
AI-driven, not client-side code. The orchestrator reads all inputs
and produces a professional assessment that integrates them,
understanding how compliance findings qualify or reinforce legal
findings.

For example: the legal SME confirms a notice was issued in time and
in the correct form. The Compliance SME finds that the individual who
signed it had no delegated authority on that date. The orchestrator
synthesises these into one position: the notice may be formally
defective despite correct form and timing.

### 2.2 Skill File Change — engineer_identification.md Retired

The existing `skills/smes/legal/engineer_identification.md` is retired.

Party and role identification — for every role, across every contract
in the project body — belongs entirely to the Compliance SME. The
Engineer is one role among many. Identifying who holds it requires
reading across the construction contract, the PMC appointment, the
consultancy agreement, and any delegation letters. This is governance
establishment work, not legal analysis.

**The boundary between legal SMEs and the Compliance SME:**

- **Legal SMEs** reason about contractual powers — what the standard
  form and amendment document say roles are authorised to do. They
  work with contract text.
- **Compliance SME** establishes who actually holds those roles, under
  what instrument, from what date, with what authority confirmed by
  what document. It works with appointment events across the body
  of contracts.

They are complementary. The legal SME tells you what the Engineer is
authorised to do. The Compliance SME tells you whether the person who
acted as Engineer was properly appointed to that role on the date in
question.

### 2.3 New Compliance SME

A new Tier 2 SME is added: the **Compliance SME**. It operates under
the Legal & Compliance orchestrator and is the sole owner of governance
establishment and compliance investigation.

**Scope:** Party and role identification across the full body of project
contracts; authority mapping; appointment chain integrity; signatory
validity; DOA compliance; statutory authority confirmation; governance
gap identification.

**Invocation:** Primary — Legal & Compliance orchestrator. Secondary —
Commercial orchestrator (party standing, contractual authority to submit
claims or agree variations) and Financial orchestrator (internal DOA
compliance for payment approvals).

### 2.4 The Two Tasks of the Compliance SME

**Task 1 — Establish governance**
Build the authority picture from all ingested documents across all
three warehouse layers. Extract every governance event. Populate the
governance event log. This task is a prerequisite — it must be
completed and user-confirmed before compliance-dependent queries
proceed. It is user-triggered, not automatic.

**Task 2 — Investigate compliance**
Given the established governance structure, assess whether parties
and individuals acted within their authority for specific acts or
documents under investigation. This is a query-time task and depends
entirely on Task 1 having been completed and confirmed.

The sequence is non-negotiable. Task 2 without Task 1 produces
unreliable findings.

### 2.5 Compliance SME Skill Files

The Compliance SME requires six skill files under
`skills/smes/compliance/`:

**`party_and_role_identification.md`**
Identifies every party and individual across the full body of project
contracts. Resolves aliases and variant name references to confirmed
entities. Establishes what role each entity holds under which contract
and at what point in time. Classifies entities: organisation or
individual; contractual role; terminus node status.

**`governance_establishment.md`**
Scans all ingested documents to extract governance events. Classifies
each event by type and authority dimension. Links each event to its
source document and effective date. Flags inferred events for user
confirmation. Populates the governance event log.

**`signatory_validation.md`**
Given a signed document, traces the signatory's authority back through
the appointment chain. Confirms or challenges whether the individual
had authority to sign on behalf of their organisation in the relevant
role on the date of signing. References the established governance
event log and the source appointment instruments.

**`doa_compliance.md`**
Assesses whether decisions — payments, contract awards, variation
approvals, procurement actions — were made at the correct authority
level as defined in the applicable internal DOA framework (Layer 2a).
Time-aware: applies the DOA version in effect at the date of the
decision.

**`statutory_authority_mapping.md`**
Identifies all statutory authorities with jurisdiction over the project.
Maps required approvals, permits, and NOCs to project milestones.
Assesses whether required interactions with statutory authorities are
evidenced in the warehouse.

**`compliance_investigation.md`**
The orchestrating skill for query-time compliance investigation. Draws
on the outputs of the other five skills and the established governance
event log to answer compliance queries. Routes to the appropriate
sub-skill based on the nature of the query.

### 2.6 How the Compliance SME Feeds Other Orchestrators

The Compliance SME is foundational infrastructure for the whole
platform. Its outputs are consumed by:

- **Legal & Compliance** — primary owner; synthesises legal and
  compliance findings into one assessment
- **Commercial** — party standing, contractual authority to submit
  claims or agree variations
- **Financial** — internal DOA compliance for payment approvals,
  budget authority, contract signing authority
- **Technical** — authority to approve method statements, issue
  inspection requests, sign off commissioning records

---

## 3. Governance Establishment

### 3.1 Governance Readiness State

Every project has a governance readiness state tracked and surfaced
by the platform at all times.

**States:**
- **Not established** — governance event log has not been run
- **Established** — event log has been run and confirmed by the user
- **Stale** — documents have been ingested since the last governance
  run that may contain authority events; re-run recommended before
  compliance-dependent queries

### 3.2 The Trigger

Governance establishment is a deliberate, user-initiated action. The
user navigates to the Governance page and triggers it. It is not
automatic on document ingestion. It is a prerequisite for any query
that depends on party authority or compliance.

### 3.3 What the Compliance SME Does When Triggered

1. Scans all ingested documents across all three warehouse layers
2. Runs party and role identification across the full body of project
   contracts to establish the entity registry
3. Runs governance establishment to extract every authority event
4. Runs statutory authority mapping to identify statutory bodies
   and required interactions
5. For each event: identifies the event type, parties involved,
   the role, effective date, scope, and source document
6. Classifies each event by authority dimension (Layer 1 / 2a / 2b)
7. Flags events that are inferred rather than explicitly documented
8. Populates the governance event log table for user review

### 3.4 User Review and Confirmation

After the Compliance SME populates the event log, the user reviews
each event:

- **Confirm** — the event is correct as extracted
- **Correct** — the user amends the event details
- **Flag** — the event needs further investigation or is disputed
- **Add** — the user manually adds an event not extracted by the SME

Only confirmed events are used by agents in compliance investigation.
Flagged and unconfirmed events are surfaced as governance gaps.

### 3.5 Incremental Refresh

When new documents are ingested after governance has been established,
the user can trigger an incremental refresh. The Compliance SME scans
only the new documents, extracts new events, and appends them to the
existing confirmed event log. Prior confirmed events are not affected.

The platform surfaces a stale governance warning when new documents
have been ingested since the last run.

---

## 4. The Governance Event Log

### 4.1 Event Types

| Event Type | Description |
|---|---|
| Appointment | A party or individual takes a role or is granted authority |
| Delegation | Authority is passed from one party or individual to another |
| Termination | An appointment or delegation ends |
| Replacement | One party or individual is substituted for another in a role |
| Modification | The scope of an existing appointment is changed |
| Suspension | Authority is temporarily suspended |

### 4.2 Data Captured Per Event

| Field | Description |
|---|---|
| Event type | One of the six types above |
| Effective date | When the event took effect |
| End date | When the authority ended (if known) |
| Party or individual | Who is affected |
| Role | The functional role or authority position involved |
| Appointed / terminated by | The source of authority for this event |
| Authority dimension | Layer 1 (contractual) / Layer 2a (internal DOA) / Layer 2b (statutory) |
| Contract source | Which contract in the project body is the source |
| Scope | What the appointment covers or what authority is delegated |
| Terminus node | Yes / No — whether this party has downward authority |
| Source document | The document in the warehouse evidencing this event |
| Extraction status | Confirmed / Flagged / Inferred |

### 4.3 Deriving Authority State at Any Date

The governance event log is the ground truth. The authority structure
at any specific date is derived by taking all events with an effective
date on or before that date and applying terminations and replacements
to determine what remains active. This allows time-specific forensic
queries without maintaining a separate snapshot for each date.

---

## 5. The Governance Page (Frontend)

### 5.1 Governance Readiness Indicator

Prominently displayed on the Governance page and visible from the
project dashboard. Shows the current governance state (Not established /
Established / Stale) and the date of the last run.

### 5.2 Trigger Button

A clearly labelled action button: "Establish Governance" (first run)
or "Refresh Governance" (subsequent runs). Disabled during processing.
Shows progress while the Compliance SME is running.

### 5.3 The Event Log Table

Displays all governance events, sortable and filterable by:
- Date (chronological or reverse)
- Event type
- Party or individual
- Authority dimension (Layer 1 / 2a / 2b)
- Contract source
- Extraction status (confirmed / flagged / inferred)

Each row links to its source document in the warehouse.

### 5.4 User Review Workflow

Each event row has a status control: Confirm / Correct / Flag.
Unreviewed events are highlighted. A summary counter shows how many
events are pending review. The user cannot mark governance as
established until all events have been reviewed.

### 5.5 Org Chart Visualisation

**Deferred to future phase.** The event log table is the primary
interface. A visual org chart derived from the event log at a
user-selected date is a future enhancement.

---

## 6. Compliance Investigation

### 6.1 What Compliance Investigation Means

Given the established governance structure, the Compliance SME
assesses whether parties and individuals acted within their authority
for specific acts or documents. This is a query-time function triggered
by a user query, not a standalone action.

### 6.2 Query Types the Compliance SME Handles

**Signatory validity**
Did the individual who signed this document have authority to do so
on behalf of their organisation in their role on the date of signing?
Handled by `signatory_validation.md`.

**Appointment chain integrity**
Is there a complete and unbroken chain of authority from the top of
the project structure to the party or individual in question? Are
there gaps or breaks in the chain? Handled by
`compliance_investigation.md` drawing on the event log.

**Internal DOA compliance**
Was this decision — payment, contract award, variation approval —
made at the correct authority level as defined in the applicable
internal DOA framework? Handled by `doa_compliance.md`.

**Statutory authority confirmation**
Was the required approval, permit, or NOC obtained from the relevant
statutory authority before the relevant activity proceeded? Is it
documented in the warehouse? Handled by
`statutory_authority_mapping.md`.

**Governance gap identification**
Are there roles that the contract requires to be filled but for which
no appointment is evidenced in the warehouse? Are there delegation
claims in documents that have no supporting delegation letter?
Handled by `compliance_investigation.md`.

### 6.3 Dependency on Established Governance

If governance has not been established or is stale when a
compliance-dependent query is submitted, the Compliance SME flags
this before proceeding. It states which governance events are missing
or unconfirmed and what compliance assessment cannot be completed as
a result. It does not fabricate authority positions from training
knowledge.

---

## 7. Implications for the Rest of the Platform

### 7.1 Data Model Changes

New tables required:
- **governance_parties** — organisations and individuals with their
  project role, classification, terminus status, and alias registry
- **governance_events** — the event log table described in Section 4
- **governance_run_log** — records each governance establishment or
  refresh run, its trigger date, and the documents scanned

Existing tables affected:
- **query_log** — governance readiness state at query time should be
  recorded for audit purposes

### 7.2 Agent Skill File Changes

**Retired:**
- `skills/smes/legal/engineer_identification.md` — party and role
  identification moves entirely to the Compliance SME

**Updated:**
- `skills/orchestrators/legal/directive.md` — renamed and expanded
  to Legal & Compliance scope; synthesis of legal SME and Compliance
  SME outputs defined as AI-driven; invocation rules for Compliance
  SME added
- `skills/orchestrators/commercial/directive.md` — invoke Compliance
  SME for party standing and authority-dependent assessments
- `skills/orchestrators/financial/directive.md` — invoke Compliance
  SME for internal DOA compliance on payment and approval decisions

**New — `skills/smes/compliance/`:**
- `party_and_role_identification.md`
- `governance_establishment.md`
- `signatory_validation.md`
- `doa_compliance.md`
- `statutory_authority_mapping.md`
- `compliance_investigation.md`

### 7.3 API Changes

New endpoints required:
- `POST /projects/{id}/governance/run` — trigger governance
  establishment or incremental refresh
- `GET /projects/{id}/governance/status` — return governance
  readiness state
- `GET /projects/{id}/governance/events` — return the event log
- `PATCH /projects/{id}/governance/events/{event_id}` — confirm,
  correct, or flag an event
- `POST /projects/{id}/governance/events` — manually add an event

### 7.4 Frontend Changes

New page: **Governance** — as described in Section 5.
Project dashboard: governance readiness indicator added.

### 7.5 Impact on Existing Queries

Compliance investigation enriches findings across all domains:
- Legal & Compliance findings gain signatory validity assessments
  on notices and instructions, and appointment chain confirmation
  for entitlement analysis
- Commercial findings gain party standing confirmation on claims
  and variation submissions
- Financial findings gain DOA compliance assessment on payment
  certificates and approvals
- Technical findings gain authority confirmation on method statement
  approvals and commissioning sign-offs

---

## 8. What Is Deferred

- **Org chart visualisation** — future phase; the event log table
  is the primary interface for now
- **Corporate authority** — board resolutions, powers of attorney,
  authorised signatory lists; noted as relevant, not in scope for
  this phase
- **Cross-project authority patterns** — identifying the same
  individual or organisation across multiple projects; future phase

---

## Document Control

| Field | Value |
|---|---|
| Version | 0.2 Draft |
| Date | April 2026 |
| Status | In discussion — not approved for execution |
| Previous version | 0.1 — initial draft |
| Changes in 0.2 | engineer_identification.md retired; Compliance SME expanded to 6 skill files; Legal & Compliance orchestrator synthesis clarified as AI-driven; body of contracts framing added throughout; boundary between legal SMEs and Compliance SME defined; statutory authorities treatment refined; contract source field added to event log; governance establishment process expanded to include party identification and statutory mapping steps |
| Next step | Review and approval by Yasser Darweesh |
