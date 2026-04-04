# Compliance Investigation

**Skill type:** Contract-type-agnostic for the routing and synthesis
logic; inherits contract-type specificity from the sub-skills invoked
- The query classification, sub-skill routing, and findings synthesis
  are form-agnostic
- Contract-type-specific analysis is performed by the sub-skills
  (signatory_validation.md, doa_compliance.md, etc.) which retrieve
  the applicable standard form from Layer 2b

**Layer dependency:** Inherits from sub-skills invoked. At minimum:
- Layer 1 — project documents: depends on query type
- Layer 2a — internal documents: depends on query type
- Layer 2b — reference standards: depends on query type

**Domain:** Compliance SME

**Invoked by:** Legal & Compliance Orchestrator (primary); Commercial
Orchestrator; Financial Orchestrator

**Sequence dependency:** The confirmed governance event log produced by
governance_establishment.md must be available before this skill runs
for any compliance-dependent query.

---

## When to apply this skill

Apply when any compliance query is received. This is the entry point for
all compliance investigation — it classifies the query, routes to the
appropriate sub-skills, performs any direct analysis (appointment chain
and governance gap analysis are handled here), and synthesises findings.

Do not apply this skill if governance has not been established. A
compliance query received before governance is established must be
returned with a CANNOT CONFIRM and a clear instruction to establish
governance first.

---

## Before you begin

### Foundational requirement — governance readiness

Before any routing or analysis, confirm the governance event log status:

1. Has governance_establishment.md been run and user-confirmed?
2. Is the governance event log current — no new documents ingested since
   the last run that may contain authority events?

**If governance has not been established:**
State CANNOT CONFIRM — GOVERNANCE NOT ESTABLISHED. Compliance investigation
requires a confirmed governance event log. Advise the user to run
governance establishment first. Do not proceed with any investigation.

**If governance is stale:**
State WARNING — GOVERNANCE MAY BE STALE. New documents have been ingested
since the last governance run. Proceed with the current event log but
flag that findings may be incomplete for events in recently ingested
documents.

### Layer 1 documents to retrieve

Retrieval is delegated to the invoked sub-skills. For appointment chain
and governance gap analysis performed directly by this skill:

Call `search_chunks` to retrieve:
- Governance event log entries for the parties and dates in question
- Appointment instruments and delegation letters relevant to the chain
- The governing contract — provisions on role requirements and delegation

### Layer 2a documents to retrieve

Delegated to invoked sub-skills. For direct analysis:
Call `search_chunks` with `layer_type = '2a'` for DOA framework if
appointment chain analysis requires authority level confirmation.

### Layer 2b documents to retrieve

Delegated to invoked sub-skills. For direct analysis:
Call `search_chunks` with `layer_type = '2b'` to retrieve governing
standard provisions on roles required to be formally appointed,
delegation permissions, and appointment chain requirements.

**If the governing standard is not in Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT RETRIEVED for all findings
that depend on standard form role requirements.

---

## Analysis workflow

### Step 1 — Confirm governance readiness

Execute the prerequisite check above. If governance is not established,
stop and return the CANNOT CONFIRM response. Do not proceed.

### Step 2 — Classify the query

Classify the incoming query into one or more of the following types.
A single query may require more than one type — treat it as composite
and invoke all relevant sub-skills.

**Signatory validity:** Query asks whether an individual had authority
to sign a specific document on behalf of their organisation in their role
on a given date.
→ Route to: signatory_validation.md

**Appointment chain integrity:** Query asks whether there is a complete
and unbroken chain of authority from the top of the project structure
to a specific party or individual, or whether there are gaps or breaks.
→ Handle directly: apply appointment chain analysis below (Step 4)

**DOA compliance:** Query asks whether a decision (payment, variation
approval, contract award, procurement action) was made at the correct
internal authority level.
→ Route to: doa_compliance.md

**Statutory authority confirmation:** Query asks whether a required
approval, permit, or NOC was obtained from the relevant statutory
authority and is documented in the warehouse.
→ Route to: statutory_authority_mapping.md

**Governance gap identification:** Query asks whether there are roles
required by the contract but unfilled, delegation claims without
supporting instruments, or authority events not evidenced in the warehouse.
→ Handle directly: apply governance gap analysis below (Step 5)

**Composite:** Query requires findings across more than one type.
Invoke all relevant sub-skills and handle any direct analysis.
Synthesise in Step 6.

### Step 3 — Invoke sub-skills

For each routed query type, invoke the appropriate sub-skill as specified
in Step 2. Each sub-skill returns its own output including its Evidence
Declaration, analysis findings, flags, and overall assessment.

Do not merge or summarise sub-skill findings at this stage — present them
in full before synthesising.

### Step 4 — Appointment chain analysis (if applicable)

When a query requires appointment chain integrity assessment:

**4a — Identify the party or individual under assessment.**
Resolve to canonical name from the entity registry. If not in the
entity registry, state CANNOT CONFIRM — ENTITY NOT IN REGISTRY.

**4b — Trace upward through the governance event log.**
Starting from the party or individual, trace each appointment event
upward through the authority chain to the top of the project structure
(Employer). For each link record:
- The appointing party (canonical name)
- The appointment instrument (source document from governance event log)
- The effective date
- Whether the appointment was active at the relevant date
- Whether the link is confirmed or inferred

**4c — Identify breaks.**
A break occurs where:
- No appointment event connects two consecutive links in the chain
- An appointment was terminated before the relevant date with no
  confirmed replacement event
- A delegation claim exists in project documents but no supporting
  delegation instrument has been retrieved

**4d — Assess and conclude.**

CHAIN INTACT: Every link from the party or individual to the top of the
project authority structure is confirmed by a governance event with a
retrieved source document, active at the relevant date.

CHAIN INCOMPLETE: One or more links are missing, inferred without a
retrieved source document, or broken by a termination without a confirmed
replacement. State which link is broken and what instrument is missing.

CANNOT CONFIRM: Governance event log not established, insufficient events
retrieved to trace the chain, or the party is not in the entity registry.

### Step 5 — Governance gap analysis (if applicable)

When a query requires governance gap identification:

**5a — Retrieve the governing contract standard from Layer 2b.**
Identify all roles the standard requires to be formally appointed.
If not in Layer 2b: state CANNOT CONFIRM — STANDARD FORM NOT RETRIEVED.
Gap analysis against standard form requirements cannot proceed.

**5b — Cross-reference with entity registry and governance event log.**
For each role required by the standard, check whether a confirmed entity
holds that role in the governance event log at the relevant date.

**5c — Check delegation claims.**
From retrieved Layer 1 documents, identify any statements where a party
claims to act under delegated authority. For each, check whether a
corresponding confirmed delegation event with a retrieved source instrument
exists in the governance event log.

**5d — Report gaps.**
For each gap identified state:
- The role or delegation that is unfilled or unsupported
- The standard form provision requiring it (from retrieved Layer 2b)
- Whether the gap is a missing appointment, a missing instrument, or both
- The date from which the gap applies

### Step 6 — Synthesise findings

After all sub-skills have returned their outputs and any direct analysis
is complete, synthesise into one compliance position:

1. Present each sub-skill finding in full, clearly labelled by sub-skill
2. Present any direct analysis findings (appointment chain, governance gap)
3. Assess the combined position:
   - Are there CANNOT CONFIRM findings that prevent a complete assessment?
   - Are there conflicts between sub-skill findings?
   - What is the overall compliance position?
4. Produce the Compliance Assessment (output format below)

---

## Classification and decision rules

**COMPLIANT:** All sub-skill findings are positive. No AUTHORITY CHALLENGED,
DOA NON-COMPLIANT, CHAIN INCOMPLETE, or governance gaps identified.

**NON-COMPLIANT:** One or more sub-skill findings are negative. State
which dimension is non-compliant and what the specific finding is.

**PARTIALLY COMPLIANT:** One or more sub-skill findings are positive and
one or more are negative. State what is compliant and what is not.

**CANNOT CONFIRM:** One or more sub-skill findings are CANNOT CONFIRM and
no sub-skill findings are CHALLENGED or NON-COMPLIANT. State what is
missing and what must be resolved.

**Sub-skill CANNOT CONFIRM — carry through unchanged:**
If any sub-skill returns CANNOT CONFIRM, carry that finding through into
the composite assessment without override. Do not substitute a finding
from another sub-skill or from training knowledge.

---

## When to call tools

- `search_chunks` — for direct appointment chain and governance gap
  analysis in Steps 4 and 5
- `search_chunks` with `layer_type = '2b'` — retrieve standard form
  role requirements for governance gap analysis
- Sub-skills handle their own tool calls per their Before you begin sections
- Governance event log — query by party canonical name and date range
  for appointment chain tracing

---

## Always flag — regardless of query

The following must always be reported:
- **Governance event log status** at time of investigation
- **Any sub-skill that returned CANNOT CONFIRM** — state the sub-skill,
  the specific CANNOT CONFIRM finding, and what must be resolved
- **Any entity not resolvable to the entity registry** — cannot be assessed
- **Governing standard not retrieved from Layer 2b** — state which
  analysis dimensions are affected
- **Stale governance warning** — if applicable, state that findings may
  be incomplete for events in recently ingested documents
- **Composite query routing** — state every sub-skill invoked and every
  direct analysis performed, so the assessment is fully traceable

---

## Output format

```
## Compliance Investigation Assessment

### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL — aggregate across sub-skills]
Layer 2b source: [standard form name — or NOT RETRIEVED]
Layer 2b provisions retrieved: [aggregate description — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE — aggregate]
Layer 2a source: [DOA framework name — or NOT RETRIEVED / NOT APPLICABLE]
Layer 1 primary document: [primary document under investigation — or NOT RETRIEVED]
Layer 1 amendment document: [particular conditions or equivalent — or NOT RETRIEVED / NOT APPLICABLE]
Provisions CANNOT CONFIRM: [list of provisions not retrieved — or NONE]

### Governance Event Log Status
Status: [confirmed / not established / stale]
Last run: [date — or NOT RUN]

### Query Classification
Query received: [restate the query]
Classification: [query type(s)]
Sub-skills invoked: [list]
Direct analysis performed: [appointment chain / governance gap / none]

### Sub-Skill Findings

[For each invoked sub-skill, reproduce its full output in a labelled section]

#### Signatory Validation Findings
[Full output from signatory_validation.md — or NOT INVOKED]

#### DOA Compliance Findings
[Full output from doa_compliance.md — or NOT INVOKED]

#### Statutory Authority Mapping Findings
[Full output from statutory_authority_mapping.md — or NOT INVOKED]

### Direct Analysis Findings

#### Appointment Chain Analysis
[Full output from Step 4 — or NOT APPLICABLE]

#### Governance Gap Analysis
[Full output from Step 5 — or NOT APPLICABLE]

### Compliance Assessment
Overall finding: COMPLIANT / NON-COMPLIANT / PARTIALLY COMPLIANT / CANNOT CONFIRM
Basis: [integrated summary — how each sub-skill and direct analysis finding
contributes to the overall position]
Gaps requiring action: [list any governance gaps, missing instruments, or
unconfirmed events that must be resolved before a complete assessment is possible]

### FLAGS
FLAG: [finding] — [forensic implication in one sentence]
[Aggregate flags from all sub-skills and direct analysis. Do not duplicate
flags already raised in sub-skill outputs — cross-reference them.]

### Overall Assessment
Confidence: [GREEN / AMBER / GREY]
[GREEN: all findings confirmed from confirmed governance events and retrieved
documents across all required layers]
[AMBER: one or more findings rest on inferred governance events, partially
retrieved documents, or stale governance]
[GREY: governance not established, or critical documents not retrieved —
investigation cannot be completed]
Summary: [Two to three sentences — retrieved facts only]
```

---

## Domain knowledge and standards

This skill is the orchestrating entry point for compliance investigation.
It does not duplicate the analytical logic of the five specialist skills —
it routes, synthesises, and delivers the integrated compliance position.

The boundary with the Legal & Compliance Orchestrator is important:
this skill assembles and presents compliance findings. The Legal &
Compliance Orchestrator synthesises compliance findings with legal SME
findings into a single professional assessment that integrates both
dimensions. This skill delivers its output to the orchestrator; the
orchestrator performs the final integration across legal and compliance.

Compliance investigation without a confirmed governance event log is
not a degraded assessment — it is not an assessment at all. Authority
chain findings, signatory validity findings, and DOA compliance findings
all depend on knowing who held what role at what date, confirmed by what
instrument. Without the governance event log, any such finding is based
on assumption, not evidence. The correct output in that case is CANNOT
CONFIRM with a clear instruction to establish governance first.

*Governed by SKILLS_STANDARDS.md v2.0. Form-agnostic — applies to any
contract form. All characterisations grounded in retrieved warehouse
documents only.*
