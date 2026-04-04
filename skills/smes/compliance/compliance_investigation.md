# Compliance Investigation

**SME:** Compliance
**Tier:** 2
**Invoked by:** Legal & Compliance Orchestrator (primary); Commercial Orchestrator; Financial Orchestrator

---

## Purpose

The orchestrating skill for query-time compliance investigation. Receives a
compliance query, determines its type, routes to the appropriate sub-skill,
and assembles the findings into a single coherent compliance assessment.
This skill is the entry point for all compliance investigation — it does not
duplicate the analytical logic of the other five Compliance SME skills but
draws on their outputs and the established governance event log to answer
the query.

This skill depends on a confirmed governance event log. Task 1 (governance
establishment) must be complete before this skill runs.

---

## Evidence Declaration

Every output produced by this skill must begin with an Evidence Declaration
block in the following format:

    EVIDENCE DECLARATION
    Layer 1 sources retrieved: [list document titles and chunk references, or NONE]
    Layer 2a sources retrieved: [list document titles and chunk references, or NONE]
    Layer 2b sources retrieved: [list document titles and chunk references, or NONE]
    Governance event log: [confirmed / not established / stale]
    Query type: [signatory validity / appointment chain / DOA compliance / statutory confirmation / governance gap / composite]
    Sub-skills invoked: [list]
    Confidence: [GREEN / AMBER / GREY — see rules below]

Confidence rules:
- GREEN: all findings grounded in confirmed governance events and retrieved
  documents across all required layers
- AMBER: one or more findings rest on inferred governance events or partially
  retrieved documents
- GREY: governance not established or critical documents not retrieved —
  investigation cannot be completed

---

## Prerequisite Check

Before any analysis, confirm governance readiness:

1. Has governance_establishment.md been run and confirmed by the user?
2. Is the governance event log current — no new documents ingested since
   the last governance run that may contain authority events?

If governance has not been established: state CANNOT CONFIRM — GOVERNANCE
NOT ESTABLISHED. Compliance investigation requires a confirmed governance
event log. Advise the user to run governance establishment first. Do not
proceed with investigation.

If governance is stale: state WARNING — GOVERNANCE MAY BE STALE. New
documents have been ingested since the last governance run. Proceed with
current event log but flag that findings may be incomplete.

---

## Query Classification

Classify the incoming query into one or more of the following types before
routing. A single query may require more than one type — treat it as composite
and invoke all relevant sub-skills.

**Signatory validity**
Query asks whether an individual had authority to sign a specific document
on behalf of their organisation on a given date.
Route to: signatory_validation.md

**Appointment chain integrity**
Query asks whether there is a complete and unbroken chain of authority from
the top of the project structure to a specific party or individual, or
whether there are gaps or breaks in the chain.
Route to: this skill — apply appointment chain analysis below.

**DOA compliance**
Query asks whether a decision — payment, variation approval, contract award,
procurement action — was made at the correct internal authority level.
Route to: doa_compliance.md

**Statutory authority confirmation**
Query asks whether a required approval, permit, or NOC was obtained from
the relevant statutory authority and is documented in the warehouse.
Route to: statutory_authority_mapping.md

**Governance gap identification**
Query asks whether there are roles required by the contract but unfilled,
delegation claims without supporting instruments, or authority events
not evidenced in the warehouse.
Route to: this skill — apply governance gap analysis below.

**Composite**
Query requires findings across more than one type above. Invoke all
relevant sub-skills and synthesise findings into one assessment.

---

## Appointment Chain Analysis

When a query requires appointment chain integrity assessment, execute these
steps using the confirmed governance event log.

**Step 1 — Identify the party or individual under assessment.**
Resolve to canonical name from the entity registry.

**Step 2 — Trace upward through the event log.**
Starting from the party or individual, trace each appointment event upward
through the authority chain to the top of the project structure. For each
link in the chain record:
- The appointing party
- The appointment instrument
- The effective date
- Whether the appointment was active at the relevant date
- Whether the link is confirmed or inferred

**Step 3 — Identify breaks.**
A break occurs where:
- No appointment event connects two consecutive links in the chain
- An appointment was terminated before the relevant date and no replacement
  event is recorded
- A delegation claim exists in project documents but no supporting delegation
  instrument has been retrieved

**Step 4 — Assess and conclude.**
- CHAIN INTACT: every link from the party or individual to the top of the
  project authority structure is confirmed by a governance event with a
  retrieved source document, active at the relevant date.
- CHAIN INCOMPLETE: one or more links are missing, inferred without a
  retrieved source document, or broken by a termination without a confirmed
  replacement. State which link is broken and what evidence is missing.
- CANNOT CONFIRM: governance event log not established or insufficient
  events retrieved to trace the chain.

---

## Governance Gap Analysis

When a query requires governance gap identification, execute these steps.

**Step 1 — Retrieve the governing contract standard from Layer 2b.**
Identify all roles the standard requires to be formally appointed.
If the standard is not in Layer 2b: state CANNOT CONFIRM — STANDARD FORM
NOT RETRIEVED. Gap analysis against standard form requirements cannot proceed.

**Step 2 — Cross-reference with the entity registry.**
For each role required by the standard, check whether a confirmed entity
holds that role in the governance event log at the relevant date.

**Step 3 — Check delegation claims.**
From retrieved Layer 1 documents, identify any statements where a party
claims to act under delegated authority. For each such claim, check whether
a corresponding delegation event with a retrieved source instrument exists
in the governance event log.

**Step 4 — Report gaps.**
For each gap identified, state:
- The role or delegation that is unfilled or unsupported
- The contract provision requiring it (from retrieved Layer 2b)
- Whether the gap is a missing appointment, a missing instrument, or both
- The date from which the gap applies

---

## CANNOT CONFIRM Rules

Apply these exactly.

- If governance has not been established:
  CANNOT CONFIRM — GOVERNANCE NOT ESTABLISHED. Do not proceed.

- If the party or individual under assessment is not in the entity registry:
  CANNOT CONFIRM — ENTITY NOT IN REGISTRY.

- If the governing standard is not in Layer 2b:
  CANNOT CONFIRM — STANDARD FORM NOT RETRIEVED. Assessment against
  standard form requirements cannot be completed.

- If a query requires sub-skill analysis and the sub-skill returns
  CANNOT CONFIRM: carry that finding through unchanged into the
  composite assessment. Do not override it.

---

## Output Format

### Query Classification

**Query received:** [restate the query]
**Classification:** [query type(s)]
**Sub-skills invoked:** [list]

### Findings

Present findings from each invoked sub-skill in sequence, clearly labelled
by sub-skill. Do not merge or summarise individual sub-skill findings —
present them in full, then synthesise.

**[Sub-skill name] Findings:**
[Full findings from that sub-skill]

### Compliance Assessment

Synthesise all sub-skill findings into a single compliance position:

**Overall finding:** COMPLIANT / NON-COMPLIANT / PARTIALLY COMPLIANT / CANNOT CONFIRM
**Basis:** [integrated summary of findings — how each sub-skill finding
contributes to the overall position]
**Gaps requiring action:** [list any governance gaps, missing instruments,
or unconfirmed events that must be resolved]

### Always Flag

The following must always be reported regardless of findings:
- Governance event log status at time of investigation
- Any sub-skill that returned CANNOT CONFIRM and why
- Any entity not resolvable to the registry
- Any required document not retrieved
- Governing standard retrieval status

---

## Boundary with Legal & Compliance Orchestrator

This skill assembles and presents compliance findings. The Legal & Compliance
Orchestrator synthesises compliance findings with legal SME findings into
a single professional assessment that integrates both. This skill does not
perform that synthesis — it delivers its output to the orchestrator, which
performs the final integration.

---

*Governed by SKILLS_STANDARDS.md v2.0. Form-agnostic — applies to any
contract form. All characterisations grounded in retrieved warehouse
documents only.*
