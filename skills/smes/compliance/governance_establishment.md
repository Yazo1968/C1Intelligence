# Governance Establishment

**SME:** Compliance
**Tier:** 2
**Invoked by:** Legal & Compliance Orchestrator (primary)

---

## Purpose

Scan all ingested documents across all three warehouse layers to extract
every authority event in the project. Classify each event, link it to its
source document and effective date, flag inferred events for user confirmation,
and populate the governance event log. This skill executes Task 1 of the
Compliance SME — it is a prerequisite for all compliance investigation.

Party and role identification (party_and_role_identification.md) must be
completed before this skill runs. The entity registry produced by that skill
is the input to this one.

---

## Evidence Declaration

Every output produced by this skill must begin with an Evidence Declaration
block in the following format:

    EVIDENCE DECLARATION
    Layer 1 sources retrieved: [list document titles and chunk references, or NONE]
    Layer 2a sources retrieved: [list document titles and chunk references, or NONE]
    Layer 2b sources retrieved: [list document titles and chunk references, or NONE]
    Events extracted: [count]
    Events confirmed (explicitly evidenced): [count]
    Events inferred (flagged for user review): [count]
    Confidence: [GREEN / AMBER / GREY — see rules below]

Confidence rules:
- GREEN: all events are directly evidenced in retrieved source documents
- AMBER: one or more events are inferred from context rather than explicitly
  documented in a retrieved source
- GREY: the body of contracts required for complete establishment has not been
  fully retrieved — the event log is incomplete

---

## Retrieval Instructions

Before extracting any event, retrieve across all three warehouse layers.

**Layer 1 — Project documents:**
Use search_chunks with the following queries across all ingested project documents:
- "appointed", "appointment", "appoints"
- "delegated", "delegation", "authorised", "authority"
- "terminated", "termination", "replaced", "replacement"
- "suspended", "suspension", "modified", "modification"
- "effective date", "with effect from", "as of"
- Role titles from the entity registry produced by party_and_role_identification.md
- Canonical names of all identified parties and individuals

**Layer 2a — Internal documents:**
Use search_chunks to retrieve DOA framework, authority matrices, and any
internal appointment or delegation documents.

**Layer 2b — External standards:**
Use search_chunks_reference to retrieve the governing contract standard.
Retrieve provisions governing appointment, delegation, replacement, and
termination of roles. Apply retrieved provisions — never assumed ones.

If the governing standard is not in Layer 2b: state CANNOT CONFIRM —
STANDARD FORM NOT RETRIEVED. Proceed with Layer 1 and 2a extraction only
and cap confidence at AMBER.

---

## Extraction Steps

Execute in this order. Do not skip steps.

**Step 1 — Retrieve across all three layers** as instructed above.

**Step 2 — Scan for authority events.**
For each retrieved document chunk, identify every statement that:
- Appoints a party or individual to a role
- Delegates authority from one party or individual to another
- Terminates an appointment or delegation
- Replaces one party or individual with another
- Modifies the scope of an existing appointment
- Suspends an appointment or authority temporarily

**Step 3 — Classify each event.**
For every identified event, record:

| Field | Value |
|---|---|
| Event type | appointment / delegation / termination / replacement / modification / suspension |
| Effective date | Date the event takes effect — extract from document text |
| End date | If stated — otherwise leave blank |
| Party or individual | Canonical name from the entity registry |
| Role | The functional role or authority position involved |
| Appointed / terminated by | The source of authority for this event |
| Authority dimension | layer_1 (contractual) / layer_2a (internal DOA) / layer_2b (statutory) |
| Contract source | Which instrument in the project body is the source |
| Scope | What the appointment covers or what authority is delegated |
| Terminus node | Yes / No — whether this party has downward authority |
| Source document | Title and chunk reference of the document evidencing this event |
| Extraction status | confirmed (explicitly stated) / inferred (deduced from context) |

**Step 4 — Flag inferred events.**
Any event where the authority act is not explicitly stated in the retrieved
document but is deduced from surrounding context must be marked as inferred
and flagged for user confirmation before it is used in compliance investigation.

**Step 5 — Identify statutory authorities.**
From retrieved documents, identify every entity that appears to exercise
statutory authority over the project. For each:
- Record the entity name and jurisdiction
- Record what approval, permit, or NOC it issues
- Record whether the required interaction is evidenced in retrieved documents
- Classify authority dimension as layer_2b

**Step 6 — Identify governance gaps.**
List every event type that the retrieved contract standard indicates should
be documented but for which no evidencing document has been retrieved.
Flag each gap explicitly.

---

## CANNOT CONFIRM Rules

Apply these exactly. Do not characterise what cannot be retrieved.

- If an authority event is referenced in a document but the source instrument
  is not retrieved:
  CANNOT CONFIRM — SOURCE INSTRUMENT FOR [event description] NOT RETRIEVED.

- If an effective date cannot be extracted from any retrieved document:
  CANNOT CONFIRM — EFFECTIVE DATE FOR [event description] NOT RETRIEVABLE.
  Record the event with effective date marked as unknown. Flag for user review.

- If the governing standard is not in Layer 2b:
  CANNOT CONFIRM — STANDARD FORM NOT RETRIEVED. Event classification against
  standard form provisions cannot be completed.

- If a role change is implied by project correspondence but no formal
  appointment document is retrieved:
  Record as inferred. Flag for user confirmation.

---

## Output Format

### Governance Event Log

Present all extracted events in a table ordered by effective date (earliest first).
Where effective date is unknown, place the event at the end of the table.

| # | Event Type | Effective Date | Party / Individual | Role | Appointed By | Authority Dimension | Contract Source | Scope | Terminus Node | Source Document | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | appointment | [date] | [name] | [role] | [name] | layer_1 | [instrument] | [scope] | Yes/No | [doc ref] | confirmed |

### Statutory Authorities

| Entity | Jurisdiction | Required Interaction | Evidenced in Warehouse |
|---|---|---|---|
| [name] | [scope] | [approval / permit / NOC] | Yes / No |

### Governance Gaps

List every role or authority event required by the retrieved contract standard
but not evidenced in retrieved documents.
If none: state "No gaps identified in retrieved documents."

### Always Flag

The following must always be reported regardless of findings:
- Total events extracted (confirmed + inferred)
- Total inferred events requiring user review
- Documents scanned (count)
- Any contract instrument not retrieved that may contain authority events
- Governing standard retrieval status (retrieved / not retrieved)

---

## Sequence Dependency

This skill must not run without a completed entity registry from
party_and_role_identification.md. If the entity registry is absent or
incomplete, stop and state: GOVERNANCE ESTABLISHMENT CANNOT PROCEED —
ENTITY REGISTRY NOT CONFIRMED.

---

*Governed by SKILLS_STANDARDS.md v2.0. Form-agnostic — applies to any
contract form. All characterisations grounded in retrieved warehouse
documents only.*
