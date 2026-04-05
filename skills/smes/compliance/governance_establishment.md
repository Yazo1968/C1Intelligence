# Governance Establishment

**Skill type:** Contract-type-agnostic
- The requirement to extract authority events, classify them, link them
  to source documents, and populate the governance event log applies
  regardless of the standard form in use. The event types that the
  governing standard requires to be formally documented differ by standard
  form and are retrieved from Layer 2b — never assumed.

**Layer dependency:**
- Layer 1 — project documents: the full body of ingested project documents
  scanned for authority events — appointment, delegation, termination,
  replacement, modification, and suspension of roles and authority
- Layer 2a — internal documents: DOA framework, authority matrices, internal
  appointment and delegation documents
- Layer 2b — reference standards: governing contract standard — provisions
  on appointment, delegation, replacement, and termination of roles; any
  statutory compliance framework applicable to the project

**Domain:** Compliance SME

**Invoked by:** Legal & Compliance Orchestrator (primary). Triggered by
user action — not automatic on document ingestion.

**Sequence dependency:** party_and_role_identification.md must be completed
and its entity registry user-confirmed before this skill runs. The entity
registry is the input to event extraction — events are linked to confirmed
canonical entities, not raw text names.

---

## When to apply this skill

Apply when the user triggers governance establishment (first run) or
governance refresh (incremental run after new documents are ingested).
This skill executes Task 1 of the Compliance SME — it is a prerequisite
for all compliance investigation. Do not apply this skill if the entity
registry from party_and_role_identification.md has not been confirmed.

**If the entity registry is absent or unconfirmed:**
State GOVERNANCE ESTABLISHMENT CANNOT PROCEED — ENTITY REGISTRY NOT
CONFIRMED. Advise the user to complete party and role identification first.

---

## Before you begin

### Layer 1 documents to retrieve

Call `search_chunks` with multiple queries across all ingested project
documents. Use the following query terms:

- "appointed", "appointment", "appoints", "is hereby appointed"
- "delegated", "delegation", "authorised", "authority", "authorises"
- "terminated", "termination", "dismissed", "relieved of"
- "replaced", "replacement", "substituted", "novated"
- "suspended", "suspension", "temporarily"
- "modified", "modification", "varied", "amended scope"
- "effective date", "with effect from", "as of", "from the date of"
- Role titles from the confirmed entity registry
- Canonical names of all confirmed parties and individuals

Also retrieve:
- All appointment letters and delegation letters
- All notices of replacement or termination of any party
- All correspondence that establishes or changes authority

**If a contract instrument is referenced in retrieved documents but not
itself retrieved:**
Note it as a gap. Events that originate from that instrument are
CANNOT CONFIRM — source instrument not retrieved.

### Layer 2a documents to retrieve

Call `search_chunks` with `layer_type = '2a'` to retrieve:
- All versions of the DOA framework ingested in the warehouse
- Authority matrices and approval threshold schedules
- Internal appointment or delegation documents

Note the effective dates of each DOA version if they can be determined
from the retrieved documents — this is required for time-aware DOA
compliance assessment.

**If Layer 2a is not retrieved:**
State CANNOT CONFIRM for any event that requires classification under
the internal DOA framework. Proceed with Layer 1 event extraction only.

### Layer 2b documents to retrieve

Call `search_chunks` with `layer_type = '2b'` to retrieve provisions of
the governing contract standard that govern:
- Appointment and replacement of the contract administrator (Engineer,
  Project Manager, or equivalent role)
- Sub-contractor appointment and nomination procedures
- Delegation of authority by the Employer
- Termination of appointment

Query format: search by subject matter — "appointment replacement
Engineer" or "nomination sub-contractor" — not by clause number.

**If the governing standard is not in Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT RETRIEVED. Event classification
against standard form provisions cannot be completed. Proceed with
Layer 1 and 2a extraction. Cap confidence at AMBER.

---

## Analysis workflow

### Step 1 — Retrieve across all three layers

Execute the retrieval instructions above before any extraction begins.
Record what was retrieved. Do not proceed until retrieval is complete.

### Step 2 — Scan retrieved documents for authority events

For each retrieved document chunk, identify every statement that:
- Appoints a party or individual to a role or grants them authority
- Delegates authority from one party or individual to another
- Terminates an appointment or delegation
- Replaces one party or individual with another in a role
- Modifies the scope of an existing appointment
- Suspends an appointment or authority temporarily

Record each identified event before classifying it.

### Step 3 — Classify each event

For each identified event record the following fields:

| Field | Value |
|---|---|
| Event type | appointment / delegation / termination / replacement / modification / suspension |
| Effective date | Extracted from document text — record exactly as stated |
| End date | If stated — otherwise leave blank |
| Party or individual | Canonical name from the confirmed entity registry |
| Role | The functional role or authority position involved |
| Appointed / terminated by | The party exercising the authority for this event |
| Authority dimension | layer_1 (contractual) / layer_2a (internal DOA) / layer_2b (statutory) |
| Contract source | The instrument in the project body that is the source |
| Scope | What the appointment covers or what authority is delegated |
| Terminus node | Yes / No — from the entity registry |
| Source document | Title and chunk reference of the evidencing document |
| Extraction status | confirmed / inferred (see classification rules below) |

### Step 4 — Flag inferred events

An event is inferred when the authority act is not explicitly stated in
a retrieved document but is deduced from surrounding context — for example,
a party acting in a role without a retrieved appointment document, or an
authority change implied by correspondence without a formal instrument.

All inferred events must be:
- Marked extraction_status = inferred
- Listed separately in the FLAGS section
- Flagged for user confirmation before use in compliance investigation

### Step 5 — Identify statutory authorities

From retrieved Layer 1 documents, identify every entity that:
- Is referenced as a government body, municipality, regulatory authority,
  or statutory body
- Issues permits, NOCs, approvals, or inspection certificates
- Has jurisdiction over any aspect of the project

For each, record entity name, jurisdiction scope, required interaction
type, and whether the required interaction is evidenced in the warehouse.
Classify authority dimension as layer_2b.

**Invoke `statutory_authority_mapping.md` at this step.** That skill
retrieves all statutory authorities with jurisdiction over this project,
maps required interactions to project milestones, and identifies which
permits, NOCs, and approvals are documented in the warehouse. Its output
feeds into the governance event log — statutory approvals are a distinct
category of authority event alongside contractual party appointments.

### Step 6 — Identify governance gaps

Using the retrieved Layer 2b standard form provisions, identify every
authority event type that the governing standard requires to be formally
documented but for which no evidencing document has been retrieved.
List each gap with the applicable standard form provision reference.

---

## Classification and decision rules

**Confirmed event:** The authority act is explicitly stated in a retrieved
source document — an appointment letter names the party and role, a
delegation letter specifies what authority is transferred, a termination
notice explicitly ends an appointment. Source document cited.

**Inferred event:** The authority act is deduced from context without
explicit documentation in a retrieved instrument. Must be flagged for
user confirmation. Cannot be used as a confirmed link in signatory
validation or appointment chain analysis.

**Effective date unknown:** Where an event is identified but no effective
date can be extracted from any retrieved document, record effective date
as "unknown" and flag for user review. The event is retained in the log
but cannot be used in time-specific forensic analysis until confirmed.

**Authority dimension classification:**
- layer_1: authority created by and for this project — contractual
  appointment, project-specific delegation
- layer_2a: authority derived from the organisation's own DOA framework —
  internal approval thresholds, internal sign-off authority
- layer_2b: authority that exists by force of law — statutory bodies,
  regulatory authorities, government agencies

---

## When to call tools

- `search_chunks` — retrieve Layer 1 project documents and Layer 2a
  internal documents. Run multiple queries using the terms listed above.
  Do not rely on a single search pass — authority events are distributed
  across many document types.
- `search_chunks` with `layer_type = '2b'` filter — retrieve governing
  standard provisions on appointment and delegation.
- `get_document` — where a specific instrument needs to be read in full,
  particularly appointment letters, delegation letters, and termination
  notices. Chunks may not capture the complete authority statement.

---

## Always flag — regardless of query

The following must always be reported:
- **Governing standard not retrieved from Layer 2b** — state which standard
  was expected and which event classifications cannot be completed
- **Contract instruments not retrieved that may contain authority events** —
  list every instrument referenced but not retrieved; state which event
  types cannot be confirmed as a result
- **Total inferred events requiring user review** — count and list; these
  cannot be used in compliance investigation until confirmed
- **Events with unknown effective date** — list each; these cannot be used
  in time-specific forensic analysis until confirmed
- **Governance gaps** — every authority event type required by the retrieved
  standard form but not evidenced in retrieved documents

---

## Output format

```
## Governance Establishment Assessment

### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [standard form name — or NOT RETRIEVED]
Layer 2b provisions retrieved: [appointment and delegation provisions
  description — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE]
Layer 2a source: [DOA framework name and version — or NOT RETRIEVED / NOT APPLICABLE]
Layer 1 primary document: [construction contract name and reference — or NOT RETRIEVED]
Layer 1 amendment document: [particular conditions or equivalent — or NOT RETRIEVED / NOT APPLICABLE]
Provisions CANNOT CONFIRM: [list of event types whose standard form
  provision was not retrieved — or NONE]

### Extraction Summary

Documents scanned: [count]
Total events extracted: [count]
Events confirmed: [count]
Events inferred (pending user review): [count]
Events with unknown effective date: [count]

### Governance Event Log

Ordered by effective date, earliest first. Events with unknown effective
date listed at end.

| # | Event Type | Effective Date | End Date | Party / Individual | Role | Appointed By | Authority Dimension | Contract Source | Scope | Terminus Node | Source Document | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [type] | [date] | [date or —] | [canonical name] | [role] | [canonical name] | [layer_1/2a/2b] | [instrument] | [scope] | Yes/No | [doc ref] | confirmed/inferred |

### Statutory Authorities

| Entity | Jurisdiction Scope | Required Interaction | Evidenced in Warehouse |
|---|---|---|---|
| [name] | [scope] | [permit / NOC / approval / inspection] | Yes / No / Partial |

### Documents Not Retrieved

[List every instrument referenced in recovered documents but not retrieved.
For each: state which events cannot be confirmed as a result.]

### FLAGS
FLAG: [finding] — [forensic implication in one sentence]
[One flag per inferred event, per instrument not retrieved, per governance
gap, per event with unknown effective date.]

### Overall Assessment
Confidence: [GREEN / AMBER / GREY]
[GREEN: all events confirmed from retrieved source documents, governing
standard provisions retrieved]
[AMBER: one or more events inferred; or governing standard not retrieved]
[GREY: entity registry not confirmed, or body of contracts not sufficiently
retrieved to establish event log]
Summary: [Two to three sentences — retrieved facts only]
```

---

## Domain knowledge and standards

The governance event log is not a snapshot — it is an ordered record of
every authority change across the full project lifecycle. The authority
structure at any specific date is derived by taking all events with an
effective date on or before that date and applying terminations and
replacements to determine what remains active. This is what enables
time-specific forensic queries: who had authority on a particular date,
under what instrument, does that satisfy the contractual requirement.

The event log is only as reliable as the documents retrieved. Gaps in
the warehouse produce gaps in the event log. Every gap must be surfaced
— a governance event log that appears complete but is missing instruments
is more dangerous than one that explicitly flags what is missing.

Inferred events must never be silently promoted to confirmed status.
The user review step exists precisely because the Compliance SME cannot
determine from documents alone whether an inferred event represents a
real authority act or a misreading of context.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies to any
contract form. All characterisations grounded in retrieved warehouse
documents only.*
