# Party and Role Identification

**Skill type:** Contract-type-agnostic
- The requirement to identify every party and individual, resolve aliases,
  and establish the entity registry applies regardless of the standard form
  in use. The specific role titles and definitions differ by standard form
  and are retrieved from Layer 2b — never assumed.

**Layer dependency:**
- Layer 1 — project documents: the full body of project contracts —
  construction contract, PMC or Engineer appointment, design consultant
  agreements, sub-contract agreements, nominated sub-contractor appointments,
  employer-direct supply agreements, letters of award, appointment letters,
  delegation letters
- Layer 2a — internal documents: DOA framework, organisational charts if
  ingested, internal appointment letters
- Layer 2b — reference standards: governing contract standard — specifically
  the definitions section establishing what each role means (Employer,
  Contractor, Engineer, PMC, sub-contractor, and any other defined role)

**Domain:** Compliance SME

**Invoked by:** Legal & Compliance Orchestrator (primary); Commercial
Orchestrator; Financial Orchestrator. Also invoked as the first step of
every governance establishment run.

---

## When to apply this skill

Apply when any query requires knowing who holds what role, under what
instrument, and at what point in time. Apply as the mandatory first step
before governance_establishment.md runs — the entity registry produced
by this skill is the input to all subsequent governance and compliance
work. Also apply directly when a query concerns party identity, role
assignment, authority chain membership, or alias resolution.

Do not proceed with any compliance investigation until the entity registry
has been produced and user-confirmed. This skill is a prerequisite, not
an optional step.

---

## Before you begin

### Layer 1 documents to retrieve

Call `search_chunks` to retrieve every contract instrument in the project body:
- Construction contract (conditions of contract, particular conditions, appendix)
- PMC appointment or Engineer appointment
- Design consultant agreements
- Sub-contract agreements (domestic and nominated)
- Employer-direct supply agreements
- Letter of Award and pre-contract correspondence naming parties
- Appointment letters and delegation letters

Query terms: role titles (Engineer, Contractor, Employer, PMC, sub-contractor,
consultant, project manager), "appointed", "delegation", "authority",
"on behalf of", party names if known from project context.

**If the construction contract is not retrieved:**
State CANNOT ASSESS — CONSTRUCTION CONTRACT NOT RETRIEVED. The primary
authority structure cannot be established. Do not proceed with entity
identification beyond what is retrievable from other instruments.

**If an appointment instrument is referenced in retrieved documents but
not itself retrieved:**
Note it as a gap. Parties under that instrument are CANNOT CONFIRM.

### Layer 2a documents to retrieve

Call `search_chunks` with `layer_type = '2a'` to retrieve:
- DOA framework or authority matrix
- Organisational charts if ingested
- Internal appointment or delegation documents

**If Layer 2a is not retrieved:**
State CANNOT CONFIRM for any finding that depends on internal authority
structure. Proceed with Layer 1 and Layer 2b identification only.

### Layer 2b documents to retrieve

After identifying the governing standard form from the Layer 1 construction
contract, call `search_chunks` with `layer_type = '2b'` to retrieve the
definitions section of the governing standard.

Query format: search by subject matter — "definitions Engineer Contractor
Employer" or "[role title] definition" — not by clause number. Clause
numbers differ across standard forms and editions.

**If the governing standard is not in Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM DEFINITIONS NOT RETRIEVED. Role
classifications from Layer 1 text only. Cap confidence at AMBER.
Do not characterise what a role is authorised to do from training knowledge.

---

## Analysis workflow

### Step 1 — Retrieve across all three layers

Execute the retrieval instructions above before any identification begins.
Record what was retrieved and what was not. Do not proceed to Step 2 until
retrieval is complete.

### Step 2 — Establish the body of contracts

From retrieved Layer 1 documents, list every contract instrument in the
project. For each instrument record:
- Instrument title
- Parties named on the instrument
- Execution date (if retrievable)
- Whether the full instrument was retrieved or only referenced

### Step 3 — Identify organisations

For each retrieved instrument:
- Extract every named organisation exactly as it appears
- Record all variant names and abbreviations used across documents
- Establish the canonical name (most complete formal name found)
- Record the contractual role under each instrument

Cross-reference all instruments — the same organisation may appear under
different names in different documents.

### Step 4 — Identify individuals

For each retrieved instrument and any appointment or delegation letters:
- Extract every named individual exactly as they appear
- Record all variant names (initials, titles, abbreviated names)
- Establish the canonical name
- Record the role and the instrument under which they act
- Record whether their authority is directly stated or inferred from context

### Step 5 — Resolve aliases

Cross-reference all identified names across all retrieved documents.
Where the same entity appears under different names, consolidate to one
canonical entry with all aliases recorded. Do not assume two similar
names are the same entity without documentary evidence.

### Step 6 — Classify each entity

For every identified entity record:
- Entity type: organisation or individual
- Canonical name and all aliases
- Contractual role(s) — may hold multiple roles across instruments
- Terminus node: Yes if the entity has no downward authority to instruct,
  direct, or delegate to parties below it; No if it can
- Evidence status: Confirmed (explicitly named in retrieved document) or
  Inferred (presence deduced from context without explicit naming)

### Step 7 — Identify governance gaps

Using the retrieved Layer 2b standard form definitions, identify any role
that the governing standard requires to be held by a named party but for
which no entity has been identified in retrieved documents. List each gap
with the role name and the Layer 2b provision that requires it.

---

## Classification and decision rules

**Confirmed entity:** Named explicitly in a retrieved Layer 1 document in
a specific role under a specific instrument. Source document cited.

**Inferred entity:** Presence or role deduced from surrounding context —
for example, a party referenced by role title without a corresponding
appointment document retrieved. Must be flagged for user confirmation.
Cannot be used as a confirmed authority chain link.

**Terminus node — Yes:** The entity has no downward authority. Examples:
domestic sub-contractor, site foreman, equipment operator. Operates within
a defined scope but cannot issue contractually binding instructions.

**Terminus node — No:** The entity can instruct, direct, or delegate to
parties below it in the authority structure. Examples: Employer, Engineer,
Contractor (relative to sub-contractors).

**CANNOT CONFIRM:** Applied when a required instrument is not retrieved,
a named role has no identified holder in retrieved documents, or the
governing standard definition is not available from Layer 2b.

---

## When to call tools

- `search_chunks` — retrieve Layer 1 project documents and Layer 2a internal
  documents. Use multiple queries across different role titles and appointment
  terminology.
- `search_chunks` with `layer_type = '2b'` filter — retrieve the governing
  standard form definitions from Layer 2b.
- `get_document` — when a specific instrument needs to be read in full rather
  than by chunk, particularly for the construction contract and appointment letters.

---

## Always flag — regardless of query

The following must always be reported:
- **Governing standard not retrieved from Layer 2b** — state which standard
  was expected, that it was not found, and that role definitions are applied
  from Layer 1 text only
- **Contract instruments referenced but not retrieved** — list every instrument
  mentioned in recovered documents that was not itself retrieved; state which
  parties and roles cannot be confirmed as a result
- **Inferred entities** — every entity whose presence or role is inferred
  rather than confirmed from a retrieved document, flagged for user confirmation
- **Aliases requiring user confirmation** — where the same entity appears
  under materially different names and consolidation is not certain
- **Roles required by the standard form but unfilled** — every governance
  gap identified in Step 7

---

## Output format

```
## Party and Role Identification Assessment

### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [standard form name — or NOT RETRIEVED]
Layer 2b provisions retrieved: [definitions section description — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE]
Layer 2a source: [policy or framework name — or NOT RETRIEVED / NOT APPLICABLE]
Layer 1 primary document: [construction contract name and reference — or NOT RETRIEVED]
Layer 1 amendment document: [particular conditions or equivalent — or NOT RETRIEVED / NOT APPLICABLE]
Provisions CANNOT CONFIRM: [list of roles whose standard form definition
  was not retrieved — or NONE]

### Contract Body

| Instrument | Parties Named | Execution Date | Retrieved |
|---|---|---|---|
| [title] | [parties] | [date or unknown] | Yes / No |

### Entity Registry — Organisations

| Canonical Name | Aliases | Contractual Role | Instrument | Terminus Node | Evidence Status |
|---|---|---|---|---|---|
| [name] | [list] | [role] | [instrument] | Yes / No | Confirmed / Inferred |

### Entity Registry — Individuals

| Canonical Name | Aliases | Role | Acting Under | Terminus Node | Evidence Status |
|---|---|---|---|---|---|
| [name] | [list] | [role] | [instrument] | Yes / No | Confirmed / Inferred |

### Documents Not Retrieved

[List every instrument referenced in recovered documents but not retrieved.
For each: state which parties and roles cannot be confirmed as a result.
If nothing missing: "None identified in retrieved documents."]

### FLAGS
FLAG: [finding] — [forensic implication in one sentence]
[One flag per governance gap, per inferred entity requiring confirmation,
per instrument not retrieved that affects a required role.]

### Overall Assessment
Confidence: [GREEN / AMBER / GREY]
*(Confidence scale: GREEN = all required evidence retrieved and findings fully supported | AMBER = Layer 2b not retrieved or amendment position unknown -- findings provisional | RED = critical document absent -- findings materially constrained | GREY = standard form unconfirmed -- form-specific analysis suspended. Full definition: skills/c1-skill-authoring/references/grounding_protocol.md)*
[GREEN: all identified entities confirmed from retrieved documents, governing
standard definitions retrieved]
[AMBER: one or more entities inferred; or governing standard not retrieved]
[GREY: construction contract not retrieved — entity registry incomplete]
Summary: [Two to three sentences — retrieved facts only]
```

---

## Domain knowledge and standards

This skill reasons about authority structure — who holds what role, under
what instrument, from what date. It does not reason about what those roles
are authorised to do. The boundary is important:

- **This skill:** who holds the Engineer role, confirmed by which appointment
  instrument, from which effective date
- **Legal SMEs:** what the Engineer role is authorised to do under the
  governing contract standard and the project's particular conditions

These are complementary. Both are required for a complete compliance finding.

The body of contracts for a construction project is not a single document.
Authority is distributed across the construction contract, the PMC or
Engineer appointment, consultant agreements, sub-contracts, and
correspondence. This skill reads all of them together. A role identified
in the construction contract may be held by an entity appointed under a
completely separate instrument — both must be retrieved and read together
to establish who holds what authority.

Standard forms define roles precisely. The definitions section of the
governing standard is retrieved from Layer 2b to confirm what each role
title means in the context of the applicable standard form. This prevents
the agent from applying training knowledge about what "Engineer" means
under FIDIC when the project may use NEC4, JCT, or a bespoke contract.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies to any
contract form. All characterisations grounded in retrieved warehouse
documents only.*
