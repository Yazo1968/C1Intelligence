# Signatory Validation

**Skill type:** Contract-type-specific for formal signing requirements;
contract-type-agnostic for the appointment chain tracing logic
- Formal requirements for who may sign a notice, certificate, or
  instruction — and whether a signature by an unauthorised party renders
  the document defective — differ by standard form and are retrieved
  from Layer 2b
- The appointment chain tracing logic (who held what role on what date,
  confirmed by what instrument) is form-agnostic and applies regardless
  of the standard form in use

**Layer dependency:**
- Layer 1 — project documents: the document under assessment (full text);
  appointment instrument for each signatory; any delegation letter
  conferring authority; the governing contract — provisions on who may
  sign on behalf of each contractual party
- Layer 2a — internal documents: DOA framework applicable at the date of
  signing; any internal authorised signatory list
- Layer 2b — reference standards: governing contract standard — provisions
  on notice execution, payment certificate signing, instruction authority,
  and any formal requirement for who may sign on behalf of each party

**Domain:** Compliance SME

**Invoked by:** Legal & Compliance Orchestrator (primary); Commercial
Orchestrator; Financial Orchestrator

**Sequence dependency:** The confirmed governance event log produced by
governance_establishment.md must be available before this skill runs.

---

## When to apply this skill

Apply when a query asks whether an individual had authority to sign a
specific document on behalf of their organisation in their role on the
date of signing. Apply when a legal or commercial finding depends on
whether the signatory was authorised. Apply when an instruction, notice,
certificate, or agreement is under challenge and authority is in question.

Do not proceed if governance has not been established. Signatory
validation without a confirmed governance event log produces unreliable
findings.

---

## Before you begin

### Foundational requirement — governance readiness

Before any retrieval or analysis, confirm the governance event log status:

1. Has governance_establishment.md been run and user-confirmed for this project?
2. Is the governance event log current — no new documents ingested since
   the last run that may contain authority events?

**If governance has not been established:**
State CANNOT CONFIRM — GOVERNANCE NOT ESTABLISHED. Signatory validation
requires a confirmed governance event log. Advise the user to run
governance establishment first. Do not proceed.

**If governance is stale:**
State WARNING — GOVERNANCE MAY BE STALE. New documents have been ingested
since the last governance run. Proceed with the current event log but
flag that findings may be incomplete if new appointment events exist in
the recently ingested documents.

### Layer 1 documents to retrieve

Call `search_chunks` to retrieve:
- The document under assessment (full text including signature block)
- The appointment instrument for each signatory (appointment letter,
  contract clause naming them, or equivalent)
- Any delegation letter conferring authority on the signatory
- The governing contract — provisions on signing authority, notice
  execution, and who may act on behalf of each contractual party

**If the document under assessment is not retrieved:**
State CANNOT ASSESS — DOCUMENT UNDER ASSESSMENT NOT RETRIEVED. Do not proceed.

**If the appointment instrument for a signatory is not retrieved:**
State CANNOT CONFIRM — APPOINTMENT INSTRUMENT NOT RETRIEVED for that
signatory. The chain cannot be confirmed without the source instrument.

### Layer 2a documents to retrieve

Call `search_chunks` with `layer_type = '2a'` to retrieve:
- The DOA framework version in effect on the date of signing
- Any internal authorised signatory list

**If Layer 2a is not retrieved:**
State CANNOT CONFIRM — DOA FRAMEWORK NOT RETRIEVED. Internal authority
level cannot be assessed. Proceed with contractual authority assessment
from Layer 1 and Layer 2b only.

### Layer 2b documents to retrieve

Call `search_chunks` with `layer_type = '2b'` to retrieve the governing
contract standard provisions on:
- Who may give notices and how they must be executed
- Who may issue payment certificates and instructions
- Who may sign agreements or variations on behalf of each party
- Whether an unauthorised signature renders the document void or voidable

Query format: search by subject matter — "notice execution signing
authority" or "certificate issued by" — not by clause number.

**If the governing standard is not in Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT RETRIEVED. Formal signing
requirements under the standard form cannot be assessed.

---

## Analysis workflow

Execute in this order for each signatory on the document under assessment.

### Step 1 — Identify the signatory and signing date

Extract the signatory's name exactly as it appears on the document.
Resolve to canonical name using the confirmed entity registry.
Extract the date of signing from the document or, if absent, the document
date.

**If the name cannot be resolved to the entity registry:**
State CANNOT CONFIRM — SIGNATORY NOT IN ENTITY REGISTRY. Flag for
user review.

**If no signing date or document date is present:**
State CANNOT CONFIRM — SIGNING DATE NOT RETRIEVABLE. Flag for user review.
The appointment chain cannot be assessed without a date reference.

### Step 2 — Identify the required signing authority

From the retrieved Layer 1 governing contract and Layer 2b standard form
provisions, establish what authority is required to sign this type of
document on behalf of the relevant party. Record the retrieved provision
exactly.

Classify the document type: notice / payment certificate / instruction /
variation order / agreement / other. The signing authority requirement
differs by document type under most standard forms.

### Step 3 — Trace the appointment chain

Using the confirmed governance event log, trace the signatory's authority
at the signing date:

1. What role did the individual hold on the signing date?
   Source: governance event log — appointment events with effective dates
   on or before the signing date, not terminated before it.

2. Under what instrument was that role conferred?
   Source: the appointment event's source document field.

3. Was the appointment active on the signing date?
   Active = appointment event exists with effective date on or before
   signing date AND no termination or replacement event before signing date.

4. Is the authority scope sufficient to cover this document type?
   Source: the appointment instrument scope field from the governance
   event log, or the retrieved appointment letter.

### Step 4 — Check internal DOA compliance

Using the retrieved Layer 2a DOA framework applicable at the signing date:
- Does the internal DOA require a specific authority level to execute this
  document type?
- Does the signatory's confirmed role satisfy that authority level?

**If multiple DOA versions exist and the applicable version at signing
date is uncertain:**
State CANNOT CONFIRM — DOA VERSION AT SIGNING DATE NOT DETERMINABLE.

### Step 5 — Assess and conclude

For each signatory state one of:

**AUTHORITY CONFIRMED:** The individual held the required role under a
confirmed appointment event active on the signing date. The appointment
scope covers this document type. Internal DOA requirements are satisfied
(or Layer 2a is not applicable). Cite the specific governance event,
appointment instrument, and retrieved standard form provision.

**AUTHORITY CHALLENGED:** One or more of the following apply:
(a) No confirmed appointment event found for this individual in this
    role active on the signing date
(b) The appointment was terminated or replaced before the signing date
(c) The appointment scope does not cover this document type
(d) Internal DOA level not satisfied
State which condition applies. Cite the specific gap.

**CANNOT CONFIRM:** Required appointment instrument not retrieved, DOA
framework not retrieved, or governance event log not available for the
signing date. State precisely what is missing.

---

## Classification and decision rules

| Condition | Finding |
|---|---|
| Appointment confirmed active on date, scope covers document type, DOA satisfied | AUTHORITY CONFIRMED |
| No appointment event found for this individual and role at signing date | AUTHORITY CHALLENGED — (a) |
| Appointment terminated before signing date, no confirmed replacement | AUTHORITY CHALLENGED — (b) |
| Appointment active but scope does not cover this document type | AUTHORITY CHALLENGED — (c) |
| DOA level not satisfied | AUTHORITY CHALLENGED — (d) |
| Appointment instrument not retrieved | CANNOT CONFIRM |
| DOA framework not retrieved | CANNOT CONFIRM (DOA dimension only) |
| Signatory not in entity registry | CANNOT CONFIRM |
| Governance not established | CANNOT CONFIRM — do not proceed |

**Overall document finding:**
- VALID: all signatories AUTHORITY CONFIRMED
- CHALLENGED: one or more signatories AUTHORITY CHALLENGED
- CANNOT CONFIRM: one or more signatories CANNOT CONFIRM with no
  AUTHORITY CHALLENGED findings
- PARTIALLY CONFIRMED: mix of AUTHORITY CONFIRMED and CANNOT CONFIRM
  with no AUTHORITY CHALLENGED

---

## When to call tools

- `search_chunks` — retrieve the document under assessment, appointment
  instruments, delegation letters, and the governing contract
- `search_chunks` with `layer_type = '2a'` — retrieve the DOA framework
- `search_chunks` with `layer_type = '2b'` — retrieve the governing
  standard form signing authority provisions
- `get_document` — where the full appointment letter or delegation
  instrument is required, not just chunks
- Governance event log — query by party canonical name and date range
  to retrieve active appointments at the signing date

---

## Always flag — regardless of query

The following must always be reported:
- **Governance event log status** at the time of assessment
- **Signatories not resolvable to the entity registry** — cannot be
  assessed; flag for user review
- **Appointment instruments not retrieved** — which signatories are
  affected and what cannot be confirmed as a result
- **DOA framework not retrieved** — internal authority level cannot
  be assessed for any signatory
- **Governing standard not retrieved from Layer 2b** — formal signing
  requirements under the standard form cannot be assessed
- **Stale governance warning** — if applicable, state that findings
  may be incomplete

---

## Output format

```
## Signatory Validation Assessment

### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [standard form name — or NOT RETRIEVED]
Layer 2b provisions retrieved: [signing authority provisions description — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE]
Layer 2a source: [DOA framework name and version at signing date — or NOT RETRIEVED / NOT APPLICABLE]
Layer 1 primary document: [document under assessment name and reference — or NOT RETRIEVED]
Layer 1 amendment document: [particular conditions or equivalent — or NOT RETRIEVED / NOT APPLICABLE]
Provisions CANNOT CONFIRM: [list of signing requirement provisions not retrieved — or NONE]

### Governance Event Log Status
Status: [confirmed / not established / stale]
Last run: [date — or NOT RUN]

### Document Under Assessment
Document: [title and reference]
Document type: [notice / certificate / instruction / variation order / agreement / other]
Date: [signing date or document date]

### Signatory Assessment

For each signatory:

**Signatory:** [canonical name]
**Role at signing date:** [role — from governance event log, or CANNOT CONFIRM]
**Appointment instrument:** [instrument title and date — or NOT RETRIEVED]
**Appointment active on signing date:** Yes / No / CANNOT CONFIRM
**Authority scope covers this document type:** Yes / No / CANNOT CONFIRM
**Internal DOA satisfied:** Yes / No / CANNOT CONFIRM / NOT APPLICABLE
**Finding:** AUTHORITY CONFIRMED / AUTHORITY CHALLENGED / CANNOT CONFIRM
**Basis:** [citation to specific governance event, appointment instrument,
and retrieved standard form provision]

### Document Assessment Summary
Overall finding: VALID / CHALLENGED / CANNOT CONFIRM / PARTIALLY CONFIRMED
Conditions: [summary of any challenges or gaps]

### FLAGS
FLAG: [finding] — [forensic implication in one sentence]
[One flag per challenged or unconfirmed authority finding, per missing
instrument, per governance gap.]

### Overall Assessment
Confidence: [GREEN / AMBER / GREY]
*(Confidence scale: GREEN = all required evidence retrieved and findings fully supported | AMBER = Layer 2b not retrieved or amendment position unknown -- findings provisional | RED = critical document absent -- findings materially constrained | GREY = standard form unconfirmed -- form-specific analysis suspended. Full definition: skills/c1-skill-authoring/references/grounding_protocol.md)*
[GREEN: all signatories AUTHORITY CONFIRMED from confirmed governance events
and retrieved instruments]
[AMBER: one or more signatories assessed against inferred governance events
or with DOA framework not retrieved]
[GREY: governance not established, or document under assessment not retrieved]
Summary: [Two to three sentences — retrieved facts only]
```

---

## Domain knowledge and standards

Signatory authority on a construction project document is not a simple
question of job title. It requires:

1. **A confirmed appointment** — a formal instrument that puts the
   individual in the relevant role with authority to act
2. **The appointment active on the date** — not terminated, suspended,
   or replaced before the signing date
3. **Scope alignment** — the appointment's scope covering this document type
4. **Internal DOA compliance** — the individual's level meeting the
   organisation's own internal requirements for this act

A notice signed by an individual who is not formally appointed to the
relevant role may be void, voidable, or challengeable depending on the
governing standard form. The legal consequences depend on the specific
provision in the retrieved standard form — this skill does not
characterise those consequences. It establishes the factual position;
legal SMEs draw the legal conclusions.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies to any
contract form. All characterisations grounded in retrieved warehouse
documents only.*
