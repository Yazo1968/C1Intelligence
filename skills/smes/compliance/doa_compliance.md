# DOA Compliance

**Skill type:** Contract-type-agnostic for the DOA assessment logic;
contract-type-specific for the contractual authority requirements
- The assessment of whether a decision was made at the correct internal
  DOA authority level is driven by the retrieved Layer 2a DOA framework
  and is independent of the contract form in use
- Whether the contract form imposes its own authority requirements for
  specific decision types (variation approval, payment certification) is
  contract-type-specific and retrieved from Layer 2b

**Layer dependency:**
- Layer 1 — project documents: the document recording the decision under
  assessment (payment certificate, variation order, contract award letter,
  procurement approval, or equivalent); any delegation letter relevant to
  the approver
- Layer 2a — internal documents: all versions of the DOA framework ingested
  in the warehouse; the version in effect at the date of the decision —
  this is time-aware: the applicable version is the one in effect on the
  decision date, not the current version
- Layer 2b — reference standards: governing contract standard — provisions
  on variation approval authority, payment certification authority, and
  any contractual requirement for who may make or authorise this type of
  decision

**Domain:** Compliance SME

**Invoked by:** Financial Orchestrator (primary); Legal & Compliance
Orchestrator; Commercial Orchestrator

**Sequence dependency:** The confirmed governance event log produced by
governance_establishment.md must be available before this skill runs.

---

## When to apply this skill

Apply when a query asks whether a payment approval, variation approval,
contract award, budget approval, or procurement decision was made at the
correct internal authority level as defined by the applicable DOA
framework. Apply when a financial or commercial finding depends on whether
the approver had the internal authority required to make that decision.

This skill is time-aware. It applies the DOA version in effect on the
decision date — not the current version, and not any prior version whose
applicability to that date cannot be confirmed from retrieved documents.

---

## Before you begin

### Foundational requirement — governance readiness

Before any retrieval or analysis, confirm the governance event log status:

1. Has governance_establishment.md been run and user-confirmed?
2. Is the governance event log current?

**If governance has not been established:**
State CANNOT CONFIRM — GOVERNANCE NOT ESTABLISHED. DOA compliance
assessment requires a confirmed governance event log to identify
who held what role at the decision date. Do not proceed.

**If governance is stale:**
State WARNING — GOVERNANCE MAY BE STALE. Proceed with current event log
but flag that findings may be incomplete.

### Layer 1 documents to retrieve

Call `search_chunks` to retrieve:
- The document recording the decision under assessment — payment
  certificate, variation order, contract award letter, purchase order,
  budget approval, or equivalent
- Any delegation letter relevant to the approver that may extend their
  authority beyond their base role
- Any document that establishes the decision value if not stated in
  the decision document itself

**If the decision document is not retrieved:**
State CANNOT ASSESS — DECISION DOCUMENT NOT RETRIEVED. Do not proceed.

### Layer 2a documents to retrieve

Call `search_chunks` with `layer_type = '2a'` to retrieve:
- All versions of the DOA framework ingested in the warehouse
- Authority matrices and approval threshold schedules
- Any internal delegated authority letters that extend standard DOA thresholds

Record the effective date and supersession date of each DOA version
retrieved. The applicable version for this assessment is the one in
effect on the decision date.

**If the DOA framework is not retrieved:**
State CANNOT CONFIRM — DOA FRAMEWORK NOT RETRIEVED. Internal authority
level cannot be assessed. This is the primary source for this skill —
without it, the core assessment cannot proceed.

**If the applicable DOA version at the decision date cannot be determined
from retrieved documents:**
State CANNOT CONFIRM — DOA VERSION AT DECISION DATE NOT DETERMINABLE.

### Layer 2b documents to retrieve

Call `search_chunks` with `layer_type = '2b'` to retrieve the governing
contract standard provisions on:
- Who may approve variations and at what threshold
- Who may certify or approve payments
- Who may commit the organisation to contractual obligations

Query format: search by subject matter — "variation approval authority"
or "payment certificate issued by" — not by clause number.

**If the governing standard is not in Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT RETRIEVED. Contractual authority
requirements for this decision type cannot be assessed. Proceed with
DOA assessment from Layer 2a only.

---

## Analysis workflow

Execute in this order for each decision under assessment.

### Step 1 — Retrieve across all three layers

Execute the retrieval instructions above. Record what was retrieved
and what was not. Do not proceed until retrieval is complete.

### Step 2 — Identify the decision

From the retrieved decision document extract:
- Decision type (payment approval / variation approval / contract award /
  procurement action / budget approval / other)
- Decision date
- Decision value (monetary amount if applicable)
- The approver — name exactly as it appears; resolve to canonical name
  from the entity registry

### Step 3 — Identify the applicable DOA version

From retrieved Layer 2a documents, identify which DOA version was in
effect on the decision date. Apply the version whose effective date is
on or before the decision date and whose supersession date (if any) is
after the decision date.

**If multiple versions are retrieved and version dating is ambiguous:**
State CANNOT CONFIRM — DOA VERSION AT DECISION DATE NOT DETERMINABLE.
Apply the most conservative version (highest threshold) and flag the
ambiguity.

### Step 4 — Identify the required authority level

From the applicable DOA version, identify:
- The decision category that covers this decision type and value
- The minimum authority level required to approve it
- Whether delegation is permitted for this category and under what
  conditions

### Step 5 — Confirm the approver's authority level

Using the confirmed governance event log, establish the approver's
confirmed role on the decision date. Cross-reference with the applicable
DOA framework to determine whether that role satisfies the required
authority level.

Also check whether any delegation letter retrieved from Layer 1 extends
the approver's authority beyond their base role for this decision type.

### Step 6 — Assess and conclude

For each decision state one of:

**DOA COMPLIANT:** The approver held a confirmed role on the decision date
that satisfies the required DOA authority level for this decision type and
value. Cite the specific DOA provision and governance event.

**DOA NON-COMPLIANT:** One or more of the following apply:
(a) The approver's confirmed role does not meet the required authority level
(b) The decision value exceeds the approver's delegated threshold
(c) Delegation is not permitted for this category, or no valid delegation
    letter is evidenced for a delegated approval
(d) The approver held no confirmed role in the governance event log on
    the decision date
State which condition applies. Cite the specific gap and the DOA provision.

**CANNOT CONFIRM:** DOA framework not retrieved, DOA version at decision
date not determinable, decision document not retrieved, or approver not
in the entity registry. State precisely what is missing.

---

## Classification and decision rules

| Condition | Finding |
|---|---|
| Approver role confirmed, DOA level satisfied, value within threshold | DOA COMPLIANT |
| Approver role confirmed, DOA level not satisfied | DOA NON-COMPLIANT — (a) |
| Value exceeds approver's delegated threshold | DOA NON-COMPLIANT — (b) |
| Delegation not evidenced for delegated approval | DOA NON-COMPLIANT — (c) |
| No confirmed role for approver at decision date | DOA NON-COMPLIANT — (d) |
| DOA framework not retrieved | CANNOT CONFIRM |
| DOA version at decision date not determinable | CANNOT CONFIRM |
| Approver not in entity registry | CANNOT CONFIRM |
| Decision document not retrieved | CANNOT ASSESS |
| Governance not established | CANNOT CONFIRM — do not proceed |

---

## When to call tools

- `search_chunks` — retrieve the decision document and delegation letters
- `search_chunks` with `layer_type = '2a'` — retrieve all DOA versions
- `search_chunks` with `layer_type = '2b'` — retrieve governing standard
  provisions on approval authority
- `get_document` — where the full DOA framework document is required
  rather than chunks, particularly when authority thresholds are in tables
  or matrices within the document
- Governance event log — query by approver canonical name and decision date
  to confirm their role at that date

---

## Always flag — regardless of query

The following must always be reported:
- **Governance event log status** at time of assessment
- **DOA framework retrieval status** — if not retrieved, the core
  assessment cannot proceed; this is always material
- **DOA version applied** — state the version name, effective date, and
  whether its applicability at the decision date was confirmed or assumed
- **Any decision where the DOA version at decision date could not be
  confirmed** — flag the ambiguity and state what was applied instead
- **Any approver not resolvable to the entity registry** — cannot be
  assessed; flag for user review
- **Governing standard not retrieved from Layer 2b** — contractual
  authority requirements cannot be assessed; DOA assessment proceeds
  but contractual dimension is CANNOT CONFIRM

---

## Output format

```
## DOA Compliance Assessment

### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [standard form name — or NOT RETRIEVED]
Layer 2b provisions retrieved: [approval authority provisions description — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE]
Layer 2a source: [DOA framework name and version applied — or NOT RETRIEVED]
Layer 1 primary document: [decision document name and reference — or NOT RETRIEVED]
Layer 1 amendment document: [NOT APPLICABLE — unless the contract form is
  relevant to the contractual authority dimension]
Provisions CANNOT CONFIRM: [list of approval authority provisions not
  retrieved from Layer 2b — or NONE]

### Governance Event Log Status
Status: [confirmed / not established / stale]
Last run: [date — or NOT RUN]

### Decision Assessment

For each decision:

**Decision type:** [payment approval / variation approval / contract award / other]
**Decision date:** [date]
**Decision value:** [amount or N/A]
**Approver:** [canonical name]
**Approver role at decision date:** [role from governance event log, or CANNOT CONFIRM]
**DOA version applied:** [version name / effective date / confirmed at decision date: Yes / No]
**Required authority level:** [from DOA — cited provision and threshold]
**Approver authority level:** [from DOA — satisfies / does not satisfy / CANNOT CONFIRM]
**Contractual authority requirement:** [from Layer 2b — satisfied / not satisfied / CANNOT CONFIRM]
**Finding:** DOA COMPLIANT / DOA NON-COMPLIANT / CANNOT CONFIRM
**Basis:** [citation to specific DOA provision, governance event, and Layer 2b provision where applicable]

### Assessment Summary

Total decisions assessed: [count]
DOA compliant: [count]
DOA non-compliant: [count]
Cannot confirm: [count]

### FLAGS
FLAG: [finding] — [forensic implication in one sentence]
[One flag per non-compliant finding, per DOA version ambiguity, per
approver not in registry, per missing DOA framework.]

### Overall Assessment
Confidence: [GREEN / AMBER / GREY]
[GREEN: all decisions assessed against a confirmed DOA version retrieved
from Layer 2a and a confirmed governance event log]
[AMBER: one or more decisions assessed against an ambiguous DOA version,
or approver role inferred rather than confirmed]
[GREY: DOA framework not retrieved or governance not established]
Summary: [Two to three sentences — retrieved facts only]
```

---

## Domain knowledge and standards

DOA compliance is a time-specific question. A decision made in year two
of a project must be assessed against the DOA framework in effect in year
two — not the framework that may have been revised in year four. Projects
frequently revise their DOA frameworks during execution. This skill
retrieves all available DOA versions and identifies the applicable one
from its effective date — it does not assume a single version applies
throughout the project.

Where no DOA framework has been ingested into Layer 2a, the internal
authority assessment cannot proceed. This is a material gap that must be
surfaced, not silently omitted from the output. The absence of an ingested
DOA framework does not mean the organisation had no DOA — it means the
compliance assessment cannot be grounded in a retrieved document.

*Governed by SKILLS_STANDARDS.md v2.0. Form-agnostic — applies to any
contract form. All characterisations grounded in retrieved warehouse
documents only.*
