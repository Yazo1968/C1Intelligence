# DOA Compliance

**SME:** Compliance
**Tier:** 2
**Invoked by:** Financial Orchestrator (primary); Legal & Compliance Orchestrator; Commercial Orchestrator

---

## Purpose

Assess whether decisions — payments, contract awards, variation approvals,
procurement actions — were made at the correct authority level as defined
in the applicable internal DOA framework (Layer 2a). This skill is
time-aware: it applies the DOA version in effect at the date of the
decision, not the current version. It operates at query time and depends
on a confirmed governance event log produced by governance_establishment.md.

---

## Evidence Declaration

Every output produced by this skill must begin with an Evidence Declaration
block in the following format:

    EVIDENCE DECLARATION
    Layer 1 sources retrieved: [list document titles and chunk references, or NONE]
    Layer 2a sources retrieved: [list document titles and chunk references, or NONE]
    Layer 2b sources retrieved: [list document titles and chunk references, or NONE]
    Governance event log: [confirmed / not established / stale]
    DOA framework version applied: [version / date / CANNOT CONFIRM]
    Decisions assessed: [count]
    DOA compliant: [count]
    DOA non-compliant: [count]
    Cannot confirm: [count]
    Confidence: [GREEN / AMBER / GREY — see rules below]

Confidence rules:
- GREEN: all decisions assessed against a confirmed DOA framework version
  retrieved from Layer 2a and a confirmed governance event log
- AMBER: one or more decisions assessed against an inferred DOA version or
  an unconfirmed governance event
- GREY: DOA framework not retrieved or governance not established —
  assessment cannot be completed

---

## Prerequisite Check

Before any analysis, confirm:

1. Has governance_establishment.md been run and confirmed by the user?
2. Is the governance event log current?

If governance has not been established: state CANNOT CONFIRM — GOVERNANCE
NOT ESTABLISHED. DOA compliance assessment requires a confirmed governance
event log to identify who held authority at the decision date.

If governance is stale: state WARNING — GOVERNANCE MAY BE STALE. Proceed
with current event log but flag that findings may be incomplete.

---

## Retrieval Instructions

**Layer 1 — Project documents:**
Use search_chunks to retrieve:
- The document recording the decision under assessment (payment certificate,
  variation order, contract award letter, procurement approval, or equivalent)
- The signatory or approver on that document
- Any delegated authority letter relevant to the approver

**Layer 2a — Internal documents:**
Use search_chunks to retrieve:
- All versions of the DOA framework ingested in the warehouse
- The version in effect at the date of the decision — apply that version,
  not the current one
- Any internal authority matrix, approval threshold schedule, or
  authorised signatory list

**Layer 2b — External standards:**
Use search_chunks_reference to retrieve the governing contract standard.
Retrieve provisions governing variation approval, payment certification,
and any contractual authority requirements for the decision type under
assessment. Apply retrieved provisions — never assumed ones.

If the DOA framework is not in Layer 2a: state CANNOT CONFIRM — DOA
FRAMEWORK NOT RETRIEVED. Internal authority level cannot be assessed.

---

## Assessment Steps

Execute in this order for each decision under assessment.

**Step 1 — Retrieve across all three layers** as instructed above.

**Step 2 — Identify the decision.**
Extract from the retrieved document:
- Decision type (payment approval / variation approval / contract award /
  procurement action / other)
- Decision date
- Decision value (monetary amount if applicable)
- The approver — name exactly as it appears; resolve to canonical name
  from the entity registry

**Step 3 — Identify the applicable DOA version.**
From retrieved Layer 2a documents, identify which version of the DOA
framework was in effect on the decision date. If multiple versions are
ingested, apply the one whose effective date is on or before the decision
date and whose supersession date (if any) is after the decision date.
If version dating cannot be determined from retrieved documents: state
CANNOT CONFIRM — DOA VERSION AT DECISION DATE NOT DETERMINABLE.

**Step 4 — Identify the required authority level.**
From the applicable DOA version, identify:
- The decision category that covers this decision type and value
- The minimum authority level required to approve it
- Whether delegation is permitted for this category and under what conditions

**Step 5 — Confirm the approver's authority level.**
Using the confirmed governance event log, establish the approver's role
and authority level on the decision date. Cross-reference with the DOA
framework to determine whether that role satisfies the required authority
level for this decision.

**Step 6 — Assess and conclude.**
For each decision state one of:

- DOA COMPLIANT: the approver held a confirmed role on the decision date
  that satisfies the required DOA authority level for this decision type
  and value. Cite the specific DOA provision and governance event.

- DOA NON-COMPLIANT: one or more of the following apply —
  (a) the approver's confirmed role does not meet the required authority level
  (b) the decision value exceeds the approver's delegated threshold
  (c) delegation was not permitted for this category or no valid delegation
      letter is evidenced
  (d) the approver held no confirmed role on the decision date
  State which condition applies and cite the specific gap.

- CANNOT CONFIRM: DOA framework or governance event log not available
  for the decision date. Assessment incomplete.

---

## CANNOT CONFIRM Rules

Apply these exactly.

- If the DOA framework is not retrieved from Layer 2a:
  CANNOT CONFIRM — DOA FRAMEWORK NOT RETRIEVED.

- If the applicable DOA version at the decision date cannot be determined:
  CANNOT CONFIRM — DOA VERSION AT DECISION DATE NOT DETERMINABLE.

- If the approver cannot be resolved to the entity registry:
  CANNOT CONFIRM — APPROVER NOT IN ENTITY REGISTRY.

- If the approver's role on the decision date cannot be confirmed from
  the governance event log:
  CANNOT CONFIRM — APPROVER AUTHORITY AT DECISION DATE NOT CONFIRMED
  IN GOVERNANCE EVENT LOG.

- If the governing standard is not in Layer 2b:
  CANNOT CONFIRM — STANDARD FORM NOT RETRIEVED. Contractual authority
  requirements for this decision type cannot be assessed.

---

## Output Format

### Decision Assessment

For each decision under assessment:

**Decision type:** [payment approval / variation approval / contract award / other]
**Decision date:** [date]
**Decision value:** [amount or N/A]
**Approver:** [canonical name]
**Approver role at decision date:** [role — from governance event log]
**DOA version applied:** [version / effective date]
**Required authority level:** [from DOA — cited provision]
**Approver authority level:** [from DOA — satisfies / does not satisfy]
**Finding:** DOA COMPLIANT / DOA NON-COMPLIANT / CANNOT CONFIRM
**Basis:** [citation to specific DOA provision, governance event, and
retrieved standard provision where applicable]

### Assessment Summary

**Total decisions assessed:** [count]
**DOA compliant:** [count]
**DOA non-compliant:** [count]
**Cannot confirm:** [count]
**Material gaps:** [summary of any non-compliant findings or gaps]

### Always Flag

The following must always be reported regardless of findings:
- Governance event log status at time of assessment
- DOA framework retrieval status and version applied
- Any decision where the DOA version at decision date could not be confirmed
- Any approver not resolvable to the entity registry
- Governing standard retrieval status

---

*Governed by SKILLS_STANDARDS.md v2.0. Form-agnostic — applies to any
contract form. All characterisations grounded in retrieved warehouse
documents only.*
