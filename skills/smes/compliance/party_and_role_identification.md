# Party and Role Identification

**SME:** Compliance
**Tier:** 2
**Invoked by:** Legal & Compliance Orchestrator (primary); Commercial Orchestrator; Financial Orchestrator

---

## Purpose

Identify every party and individual across the full body of project contracts.
Resolve aliases and variant name references to confirmed canonical entities.
Establish what role each entity holds, under which contract, and at what point
in time. This skill is a prerequisite for governance establishment — the entity
registry it produces is the foundation for all subsequent compliance work.

---

## Evidence Declaration

Every output produced by this skill must begin with an Evidence Declaration
block in the following format:
EVIDENCE DECLARATION
Layer 1 sources retrieved: [list document titles and chunk references, or NONE]
Layer 2a sources retrieved: [list document titles and chunk references, or NONE]
Layer 2b sources retrieved: [list document titles and chunk references, or NONE]
Entities confirmed from retrieved documents: [count]
Entities inferred (not directly evidenced): [count]
Confidence: [GREEN / AMBER / GREY — see rules below]

Confidence rules:
- GREEN: all identified entities are directly evidenced in retrieved documents
- AMBER: one or more entities are inferred from context rather than explicitly named in a retrieved document
- GREY: the body of contracts required for identification has not been fully retrieved — identification is incomplete

---

## Retrieval Instructions

Before identifying any party or individual, retrieve across all three warehouse layers.

**Layer 1 — Project documents:**
Use search_chunks to retrieve:
- The construction contract (conditions of contract, particular conditions, appendix)
- The PMC or Engineer appointment
- Design consultant agreements
- Sub-contract agreements
- Nominated sub-contractor appointments
- Employer-direct supply agreements
- Letter of Award and any pre-contract correspondence naming parties
- Delegation letters and authority letters

Query terms: party names if known, role titles (Engineer, Contractor, Employer,
PMC, sub-contractor, consultant), "appointed", "delegation", "authority".

**Layer 2a — Internal documents:**
Use search_chunks to retrieve:
- DOA framework or authority matrix
- Organisational charts if ingested
- Any internal appointment letters

**Layer 2b — External standards:**
Use search_chunks_reference to retrieve the governing contract standard.
Retrieve the definitions section — standard forms define roles such as
Engineer, Contractor, Employer, and sub-contractor with precision.
Apply retrieved definitions — never assumed ones.

If the governing standard is not in Layer 2b: state CANNOT CONFIRM —
STANDARD FORM DEFINITIONS NOT RETRIEVED. Proceed with Layer 1 identification
only and cap confidence at AMBER.

---

## Identification Steps

Execute in this order. Do not skip steps.

**Step 1 — Retrieve across all three layers** as instructed above.

**Step 2 — Extract the body of contracts.**
From retrieved Layer 1 documents, identify every contract instrument in the
project body. List each instrument with its title, parties named, and
execution date if retrievable.

**Step 3 — Identify organisations.**
For each contract instrument retrieved:
- Identify every named organisation
- Record the name exactly as it appears in the document
- Record all variant names and abbreviations used across documents
- Establish the canonical name (the most complete formal name found)
- Record the contractual role under each instrument

**Step 4 — Identify individuals.**
For each contract instrument and any appointment or delegation letters retrieved:
- Identify every named individual
- Record name exactly as it appears
- Record all variant names (initials, titles, abbreviated names)
- Establish canonical name
- Record the role and the instrument under which they act
- Record whether their authority is directly evidenced or inferred

**Step 5 — Resolve aliases.**
Cross-reference all identified names across all retrieved documents.
Where the same entity appears under different names, consolidate to
one canonical entity with all aliases recorded.

**Step 6 — Classify each entity.**
For every identified entity record:
- Entity type: organisation or individual
- Canonical name
- Aliases
- Contractual role(s) — may hold more than one role across instruments
- Terminus node: Yes if the entity has no downward authority; No if it
  can instruct, direct, or delegate to parties below it
- Evidence status: Confirmed (explicitly named in retrieved document) or
  Inferred (presence deduced from context)

**Step 7 — Identify gaps.**
List any roles that the retrieved contract standard or project contracts
indicate should be filled but for which no entity has been identified
in the retrieved documents. Flag each gap explicitly.

---

## CANNOT CONFIRM Rules

Apply these exactly. Do not characterise what cannot be retrieved.

- If a contract instrument is referenced but not retrieved from Layer 1:
  CANNOT CONFIRM — [instrument name] NOT RETRIEVED. Parties under that
  instrument cannot be confirmed.

- If an individual is named in a document but their role or appointing
  instrument is not retrievable:
  CANNOT CONFIRM — APPOINTMENT INSTRUMENT FOR [name] NOT RETRIEVED.

- If the governing standard's definitions are not in Layer 2b:
  CANNOT CONFIRM — STANDARD FORM DEFINITIONS NOT RETRIEVED. Role
  classifications applied from Layer 1 text only.

- If a role is referenced but no individual or organisation is named
  as holding it in any retrieved document:
  CANNOT CONFIRM — NO ENTITY IDENTIFIED FOR ROLE [role name].

---

## Output Format

### Entity Registry

**Organisations**

| Canonical Name | Aliases | Contractual Role | Terminus Node | Evidence Status |
|---|---|---|---|---|
| [name] | [list] | [role / instrument] | Yes / No | Confirmed / Inferred |

**Individuals**

| Canonical Name | Aliases | Role | Acting Under | Terminus Node | Evidence Status |
|---|---|---|---|---|---|
| [name] | [list] | [role] | [instrument] | Yes / No | Confirmed / Inferred |

### Contract Body

| Instrument | Parties | Execution Date | Retrieved |
|---|---|---|---|
| [title] | [parties] | [date or unknown] | Yes / No |

### Governance Gaps

List every role identified as required but unfilled in retrieved documents.
If none: state "No gaps identified in retrieved documents."

### Always Flag

The following must always be reported regardless of findings:
- Number of contract instruments identified vs retrieved
- Number of entities confirmed vs inferred
- Any instrument referenced in project documents but not present in the warehouse
- Governing standard retrieval status (retrieved / not retrieved)

---

## Boundary with Legal SMEs

This skill establishes who holds a role. Legal SMEs establish what that role
is authorised to do under the governing contract standard. The two are
complementary — this skill does not characterise contractual powers, and
legal SMEs do not identify appointment chains.

---

*Governed by SKILLS_STANDARDS.md v2.0. Form-agnostic — applies to any
contract form. All characterisations grounded in retrieved warehouse
documents only.*
