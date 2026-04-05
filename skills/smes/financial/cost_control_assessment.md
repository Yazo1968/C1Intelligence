# Cost Control Assessment

**Skill type:** Mixed
- Contract-type-agnostic: the assessment framework for cost control
  adequacy, WBS structure quality, EAC credibility, and contingency
  governance applies regardless of contract form
- Contract-type-specific: the contractual cost reporting obligations,
  required reporting format, and cost breakdown structure requirements
  differ by contract — retrieved from each contract document in Layer 1

**Layer dependency:**
- Layer 1 — project documents: all contract documents in the warehouse
  (main contract, subcontracts, consultancy agreements, purchase orders,
  task orders); cost reports; budget documents; approved budget amendments;
  payment certificates; variation registers; contingency drawdown records;
  progress reports with financial data
- Layer 2a — internal documents: internal financial reporting policy;
  cost management procedure; contingency governance framework; DOA matrix
  for budget amendments and contingency approvals
- Layer 2b — reference standards: applicable cost management standard
  referenced in retrieved contract documents (AACE International, PMBOK,
  or equivalent — if ingested); applicable accounting standard if
  referenced (IFRS or equivalent — if ingested)

**Domain:** Financial & Accounting SME

**Invoked by:** Financial & Reporting Orchestrator

---

## When to apply this skill

Apply when a query asks whether the project's cost management system is
functioning adequately — whether cost reporting is reliable, whether the
cost-to-complete estimate is credible, whether the cost breakdown is
sufficient to support meaningful cost control, or whether contingency
is being governed in accordance with the retrieved internal policy and
contractual obligations.

Apply when the Financial Orchestrator requires a quality assessment of
the cost data it is extracting — not just what the numbers say, but
whether those numbers are trustworthy and what they are grounded in.

Do not apply for: extraction of specific cost figures from retrieved
reports (Financial Orchestrator direct scope); contractual payment
certification assessment (Commercial Orchestrator scope); claims quantum
assessment (Delay and Cost Analytics SME scope); or reconciliation of
contract accounts across multiple contracts (route to
`multi_contract_account_reconciliation.md`).

---

## Before you begin

Read the Financial Orchestrator findings and any Commercial Orchestrator
findings before proceeding. From those findings extract:
- The approved budget and its source document
- The latest reported EAC and its source document
- Actual cost to date and its source document
- Any cost performance flags already raised

Do not duplicate findings the orchestrators have already established.
This skill adds the quality layer — not the extraction layer.

### Layer 1 documents to retrieve

Call `search_chunks` and `get_related_documents` to retrieve:
- All cost reports for the project — identify the most recent and
  whether a series exists covering the project duration
- Budget documents — the approved budget baseline and all approved
  budget amendments
- All contract documents in the warehouse — to identify contractual
  cost reporting obligations for each instrument
- Variation registers or change order logs for each contract
- Contingency drawdown records — approvals, amounts, dates, reasons
- Payment certificates — for cross-checking actual cost to date
- Progress reports containing cost-to-complete projections or
  financial performance sections

**If no cost reports are retrieved:** State CANNOT ASSESS — no cost
reports found in the warehouse. List what documents would be needed.
Do not proceed with Steps 2–6.

**If cost reports cover only part of the project period:** Proceed
with available data. Flag the gap explicitly in the output.

### Layer 2a documents to retrieve

Call `search_chunks` with `layer_type = '2a'` to retrieve:
- Internal financial reporting policy — required reporting frequency,
  format, and content
- Cost management procedure — WBS requirements, cost coding standards,
  committed/incurred/forecast distinction requirements
- Contingency governance framework — approval thresholds, required
  documentation for drawdown
- DOA matrix — authority levels for budget amendments and contingency
  approvals

**If Layer 2a not retrieved:** State CANNOT CONFIRM — INTERNAL POLICY
NOT RETRIEVED for all steps requiring it. Proceed using Layer 1 and
Layer 2b only. Flag that compliance with internal financial policy
cannot be assessed.

### Layer 2b documents to retrieve

After identifying any governing cost management or accounting standard
referenced in the retrieved contract documents, call `search_chunks`
with `layer_type = '2b'`. Query by subject matter — not by standard
name or clause number.

If the applicable standard is not in Layer 2b: record as CANNOT CONFIRM
— STANDARD NOT IN WAREHOUSE. Do not characterise the standard from
training knowledge.

---

## Analysis workflow

### Step 1 — Establish contractual cost reporting obligations

For each contract document retrieved from Layer 1:
- What cost reporting does this contract require? Retrieve the
  reporting obligation provision from the contract document.
- What reporting frequency is required?
- What content is required — WBS breakdown, committed/incurred/
  forecast distinction, variance explanation, contingency status?
- Is a specific format prescribed?

State the contractual reporting obligation per contract from retrieved
documents. If a contract does not specify a cost reporting obligation:
state this explicitly — the absence of a contractual obligation does
not mean reporting is not required under internal policy (Layer 2a).

CANNOT CONFIRM if the contract document was not retrieved.

### Step 2 — Assess WBS and cost coding structure

From retrieved cost reports:
- Is the WBS adequate to support meaningful cost control? Does it
  break costs down at a level that allows issues to be identified and
  located — by contract, by trade or discipline, by work package, or
  by phase?
- Are costs coded consistently across reporting periods?
- Are costs from different contracts — main contract, subcontracts,
  consultancy agreements, POs, task orders — separately identifiable
  in the cost report, or aggregated without breakdown?
- Does the cost coding correspond to the contract structure and
  variation register?

State the WBS structure from retrieved documents. If the cost reports
do not show sufficient breakdown: flag as a cost control deficiency.
CANNOT ASSESS if no cost reports retrieved.

### Step 3 — Assess committed vs incurred vs forecast distinction

A sound cost management system distinguishes between three states for
each cost line:
- **Committed:** contracted obligation exists but not yet paid —
  subcontracts, POs, task orders, and approved variations at their
  contracted values
- **Incurred:** actually paid or invoiced and accepted
- **Forecast:** estimated cost to complete remaining scope

From retrieved cost reports:
- Does the cost report distinguish between these three states — or
  does it report only an aggregate figure?
- Are committed costs (approved contracts, POs, and variations) captured
  at their contracted values?
- Are forecast costs derived from a stated methodology, or are they
  carry-forwards of the original budget with no explicit basis?

State the finding from retrieved documents. If the distinction is absent:
flag as a significant cost control deficiency. An EAC cannot be credible
if committed costs are not captured separately from incurred costs.

### Step 4 — Assess EAC credibility

The Financial Orchestrator extracts the EAC from retrieved reports.
This step challenges whether that EAC is credible. The agent does not
calculate an alternative EAC — it identifies inconsistencies between
the reported EAC and the evidence in retrieved documents.

Assess each of the following from retrieved documents:

**Burn rate consistency:** Does the EAC imply a cost-to-complete rate
consistent with the actual burn rate evidenced in retrieved cost reports
and payment records? If the project has consistently spent above the
planned rate but the EAC assumes remaining work at the planned rate:
flag the inconsistency. State the inconsistency from retrieved figures only.

**Open contractual items:** From the retrieved variation register and
claims correspondence: are approved-but-not-yet-priced variations,
submitted claims, and anticipated variations reflected in the EAC?
If the EAC does not account for documented open items: state the gap
and identify the unincorporated items from retrieved documents.

**Remaining scope:** From retrieved progress reports, is the percentage
complete consistent with the cost incurred to date relative to the EAC?
If significant scope remains but the cost-to-complete is low relative to
the work outstanding: flag the inconsistency from retrieved data.

**Basis of forecast:** Does the retrieved documentation state the basis
of the cost-to-complete forecast? If the basis is unstated: flag that
the EAC cannot be independently validated from retrieved documents.

State each factor as: CONSISTENT WITH RETRIEVED DOCUMENTS |
INCONSISTENT — state the specific inconsistency from retrieved figures |
CANNOT ASSESS — state which document is missing.

### Step 5 — Assess cost report currency and completeness

From retrieved cost reports:
- What is the reporting date of the most recent cost report?
- Is the reporting cadence consistent with the contractual obligation
  identified in Step 1?
- Does the cost report cover all contracts in the warehouse — or
  only the main contract?
- Are all approved variations reflected in the reported contract sum?

Flag any gap between contractual reporting obligation and actual
reporting cadence. Flag any contract for which cost reporting is
absent from the warehouse.

### Step 6 — Assess contingency governance

From retrieved contingency records and Layer 2a DOA framework:
- What was the approved contingency baseline? State value and source.
- What has been drawn against contingency, for what stated reasons,
  approved by whom? List each drawdown from retrieved records.
- Was each drawdown approved at the correct authority level under the
  retrieved DOA framework? Where DOA confirmation is required for a
  specific drawdown: invoke `doa_compliance.md` for that transaction.
- What is the remaining contingency balance from retrieved records?
- Is the drawdown rate accelerating? State from retrieved drawdown
  history only — do not project.

CANNOT CONFIRM contingency governance if the DOA framework was not
retrieved from Layer 2a. Flag that drawdown authority cannot be assessed.

---

## Classification and decision rules

**GREEN:** All required cost reports present and current; WBS adequate
to cost code level; committed/incurred/forecast distinction present;
EAC consistent with burn rate, open items, and remaining scope;
contingency drawdowns documented and within confirmed DOA authority.

**AMBER:** Cost reports present but one or more of: WBS inadequate;
committed/incurred/forecast distinction absent; EAC inconsistency
identified; reporting cadence gap against contractual obligation;
contingency drawdown without confirmed DOA authority; or internal
policy not retrieved.

**RED:** EAC materially inconsistent with retrieved evidence —
specifically where documented open variations or claims are absent
from the EAC, or where burn rate implies completion cost significantly
above reported EAC.

**GREY:** No cost reports retrieved — cost control system cannot be
assessed from the warehouse.

---

## When to call tools

- Call `search_chunks` to retrieve cost reports, budget documents, and
  contract documents from Layer 1
- Call `search_chunks` with `layer_type = '2a'` for internal financial
  policy and DOA framework
- Call `search_chunks` with `layer_type = '2b'` for applicable cost
  management or accounting standards
- Call `get_related_documents` when a retrieved chunk indicates a cost
  report or budget document exists — retrieve the full document
- Invoke `doa_compliance.md` for any contingency drawdown where the
  approver or authority level requires confirmation
- Always call tools before concluding any document is absent

---

## Always flag — regardless of query

- **EAC not supported by retrieved evidence** — when burn rate, open
  contractual items, or remaining scope are inconsistent with the
  reported EAC; state the specific inconsistency
- **Committed costs absent from cost report** — when approved contracts,
  POs, or variations are not reflected in the reported cost position
- **Cost reporting cadence gap** — when reports are absent for periods
  required by the retrieved contract
- **WBS inadequate for cost control** — when costs cannot be traced
  to individual contracts, work packages, or trades in retrieved reports
- **Contingency drawdown without confirmed authority** — when drawdown
  records exist but DOA compliance cannot be confirmed from retrieved
  documents
- **Governing cost management standard not in Layer 2b** — when the
  contract references a standard that is not in the warehouse; state
  which standard and what analysis cannot proceed

---

## Output format

```
## Cost Control Assessment

### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [standard name — or NOT RETRIEVED]
Layer 2b provisions retrieved: [description — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE]
Layer 2a source: [policy name — or NOT RETRIEVED / NOT APPLICABLE]
Layer 1 primary document: [name and reference — or NOT RETRIEVED]
Layer 1 amendment document: [NOT APPLICABLE — this skill does not
  assess contractual amendment positions]
Provisions CANNOT CONFIRM: [list — or NONE]

### Documents Retrieved (Layer 1)
[Every retrieved cost report, budget document, and contract document
with reference and reporting date]

### Documents Not Retrieved
[Every required document absent — which steps are affected.
If nothing missing: "None."]

### Layer 2b Reference
[Retrieved standard and relevant provisions — or: CANNOT CONFIRM —
[standard name] NOT IN WAREHOUSE]

### Contractual Cost Reporting Obligations
[Per contract — obligation, frequency, and content requirement
from retrieved documents. CANNOT CONFIRM where contract not retrieved.]

### WBS and Cost Coding Structure
[GREEN / AMBER / RED / GREY / CANNOT ASSESS]
[Finding from retrieved documents — state the breakdown level
and whether it is adequate to identify issues by contract,
trade, work package, or phase]

### Committed vs Incurred vs Forecast
[GREEN / AMBER / RED / GREY / CANNOT ASSESS]
[Finding — state whether the distinction is present in retrieved
cost reports and whether committed costs are captured at
contracted values]

### EAC Credibility Assessment
[GREEN / AMBER / RED / GREY / CANNOT ASSESS]
Burn rate consistency: [CONSISTENT / INCONSISTENT / CANNOT ASSESS]
Open contractual items: [REFLECTED / NOT REFLECTED / CANNOT ASSESS]
Remaining scope consistency: [CONSISTENT / INCONSISTENT / CANNOT ASSESS]
Basis of forecast: [STATED / UNSTATED / CANNOT ASSESS]
[Narrative — state all inconsistencies specifically from retrieved
figures. Do not calculate an alternative EAC.]

### Cost Report Currency and Completeness
[GREEN / AMBER / RED / GREY / CANNOT ASSESS]
Most recent report date: [date and source]
Reporting cadence vs contractual obligation: [COMPLIANT / GAP IDENTIFIED /
  CANNOT ASSESS — state gap if identified]
Contract coverage: [list which contracts are covered and which are absent]

### Contingency Governance
[GREEN / AMBER / RED / GREY / CANNOT ASSESS]
Baseline: [amount and source document]
Drawdowns: [list each — amount, reason, approver, date, DOA status]
Remaining balance: [amount and source]
Drawdown authority: [CONFIRMED / NOT CONFIRMED / CANNOT CONFIRM]
Drawdown rate trend: [STABLE / ACCELERATING / CANNOT ASSESS]

### FLAGS
FLAG: [finding] — [forensic implication in one sentence]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
*(Confidence scale: GREEN = all required evidence retrieved and findings
fully supported | AMBER = Layer 2b not retrieved or amendment position
unknown -- findings provisional | RED = critical document absent --
findings materially constrained | GREY = standard form unconfirmed --
form-specific analysis suspended. Full definition:
skills/c1-skill-authoring/references/grounding_protocol.md)*
Summary: [two to three sentences — retrieved facts only]
```

---

## Domain knowledge and standards

The assessment framework applies regardless of contract form. A project
with multiple contracts has multiple sets of cost reporting obligations —
this skill assesses all of them from retrieved documents. Cost management
standards (AACE, PMBOK, or equivalent) are retrieved from Layer 2b and
applied only if found — never assumed from training knowledge. The EAC
credibility assessment does not produce an alternative figure — it
identifies inconsistencies between what is reported and what the
retrieved documents support. Contingency governance is assessed against
the retrieved DOA framework from Layer 2a — not against any assumed
authority threshold.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies
to any contract form. All characterisations grounded in retrieved warehouse
documents only.*
