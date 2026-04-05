# Financial Reporting Compliance

**Skill type:** Mixed
- Contract-type-agnostic: the assessment framework for financial
  reporting completeness, consistency, and compliance with internal
  financial policy applies regardless of contract form
- Contract-type-specific: the contractual financial reporting
  obligations — frequency, format, content — differ by contract and
  are retrieved from each contract document in Layer 1; the applicable
  accounting standard differs by organisation and jurisdiction and is
  retrieved from Layer 2b

**Layer dependency:**
- Layer 1 — project documents: all contract documents in the warehouse
  (for contractual reporting obligations); all financial reports
  produced for the project — cost reports, cash flow statements,
  financial forecasts, budget reports, progress reports with financial
  sections, management accounts, board reports; any audit or review
  reports on project financials
- Layer 2a — internal documents: internal financial reporting policy;
  required report types, frequency, and content; management reporting
  framework; applicable accounting principles and financial controls
  policy
- Layer 2b — reference standards: applicable accounting standard
  referenced in retrieved documents (IFRS 15, IFRS for SMEs, or
  equivalent — if ingested); applicable cost reporting standard
  (AACE, PMBOK, or equivalent — if ingested)

**Domain:** Financial & Accounting SME

**Invoked by:** Financial & Reporting Orchestrator

---

## When to apply this skill

Apply when a query asks whether the project's financial reporting is
complete, current, consistent, and compliant — whether all required
reports are present in the warehouse, whether they are internally
consistent with each other, whether they comply with contractual
reporting obligations, and whether applicable accounting principles
and internal financial policy have been followed.

Apply when an audit or governance query requires an opinion on the
quality and reliability of the financial reporting package as a whole
— not just the figures within individual reports.

Apply when a query asks whether financial reports are consistent with
each other — for example, whether the cash flow statement is consistent
with the cost report, or whether the budget report reflects approved
variations as reported in the payment records.

Do not apply for: extraction of specific financial figures (Financial
Orchestrator direct scope); reconciliation of contract accounts (route
to `multi_contract_account_reconciliation.md`); assessment of cost
control system quality (route to `cost_control_assessment.md`); or
assessment of payment certification compliance (Commercial Orchestrator
scope).

---

## Before you begin

Read the Financial Orchestrator findings before proceeding. From those
findings extract:
- The reports already retrieved and their reporting dates
- Any inconsistencies between reported metrics already identified by
  the Financial Orchestrator
- The overall financial position established

This skill assesses the reporting system — not the individual figures
already extracted by the orchestrator. Do not duplicate extraction work.

### Layer 1 documents to retrieve

Call `search_chunks` and `get_related_documents` to retrieve:
- All financial reports present in the warehouse: cost reports, cash
  flow statements, financial forecasts, budget reports, management
  accounts, board financial reports, progress reports with financial
  sections
- All contract documents — to establish contractual reporting
  obligations per instrument
- Any audit reports, review reports, or management letters relating
  to project financial reporting

For each report retrieved: note the report type, reporting period,
reporting date, and preparer.

**If financial reports are absent or cover only part of the project
period:** Flag immediately. The absence of financial reports is itself
a finding — not a reason to stop. State what is absent and what
cannot be assessed.

### Layer 2a documents to retrieve

Call `search_chunks` with `layer_type = '2a'` to retrieve:
- Internal financial reporting policy — what reports are required,
  at what frequency, in what format, and with what content
- Management reporting framework — what financial information must
  be reported to which governance level and at what cadence
- Applicable accounting principles policy — which accounting standard
  does the organisation apply to construction contracts?
- Financial controls policy — what sign-off and review is required
  before financial reports are issued?

**If Layer 2a not retrieved:** State CANNOT CONFIRM — INTERNAL POLICY
NOT RETRIEVED. Proceed with contractual obligations from Layer 1 and
any applicable standard from Layer 2b only. Flag that compliance with
internal financial policy cannot be assessed.

### Layer 2b documents to retrieve

After identifying the applicable accounting standard from Layer 2a or
from references in the retrieved contract or financial documents, call
`search_chunks` with `layer_type = '2b'`. Query by subject matter —
for example, search for revenue recognition on long-term contracts,
percentage of completion, contract assets and liabilities, or cost
reporting requirements — not by standard name or clause number.

If the applicable standard is not in Layer 2b: record as CANNOT CONFIRM
— STANDARD NOT IN WAREHOUSE. Do not characterise the standard from
training knowledge.

---

## Analysis workflow

### Step 1 — Establish reporting obligations

**Contractual obligations (Layer 1):**
For each contract document retrieved, identify the financial reporting
obligation: what reports does this contract require, at what frequency,
in what format, and to whom? State per contract from retrieved documents.
CANNOT CONFIRM where the contract document was not retrieved.

**Internal policy obligations (Layer 2a):**
From the retrieved internal financial reporting policy: what reports
does internal policy require, at what frequency, and what content is
mandatory? State from retrieved documents. CANNOT CONFIRM if not retrieved.

**Accounting standard requirements (Layer 2b):**
From the retrieved accounting standard: what financial reporting does
the applicable standard require for construction contracts? State from
retrieved provisions only. CANNOT CONFIRM if the standard is not in
Layer 2b.

### Step 2 — Assess report completeness

Compare the reports retrieved from Layer 1 against the obligations
established in Step 1:

For each required report type:
- Is it present in the warehouse?
- Does it cover the required reporting period?
- Is the cadence consistent with the required frequency?
- Is the content consistent with what the obligation requires?

State the finding per report type:
PRESENT AND COMPLIANT | PRESENT BUT INCOMPLETE — state what is missing |
ABSENT — state the reporting obligation it was required to satisfy |
CANNOT ASSESS — reporting obligation not retrieved

Flag any required report that is absent from the warehouse. An absent
report is a reporting deficiency regardless of what the underlying
financial position may be.

### Step 3 — Assess inter-report consistency

From the retrieved financial reports, assess whether they are consistent
with each other. Inconsistency between reports produced for the same
period is a material finding — it indicates either an error in one
report, different data sources being used, or a reporting control
failure.

Assess the following pairs where both reports are retrieved:

**Cost report vs cash flow statement:** Is the actual cost to date in
the cost report consistent with the cumulative payments shown in the
cash flow statement? State any discrepancy from retrieved figures.

**Cost report vs payment certificates:** Is the actual cost to date in
the cost report consistent with the aggregate of retrieved payment
certificates? State any discrepancy.

**Budget report vs variation register:** Is the current approved budget
in the budget report consistent with the original budget plus all
approved variations in the retrieved variation register? State any
discrepancy.

**Financial forecast vs cost report:** Is the EAC or cost-to-complete
in the financial forecast consistent with what the cost report shows
for actual cost to date and projected completion? State any discrepancy.

**Management accounts vs project cost reports:** Where both exist: are
the project figures in the management accounts consistent with the
project cost reports for the same period? State any discrepancy.

For each pair: CONSISTENT | INCONSISTENT — state the discrepancy and
the source documents | CANNOT ASSESS — state which report is absent.

### Step 4 — Assess compliance with applicable accounting standard

From the retrieved accounting standard provisions (Layer 2b):

**Revenue recognition (where applicable):** Is revenue on the project
being recognised in accordance with the retrieved standard? What method
is applied — input method, output method, or percentage of completion?
Is the method consistent with what the standard permits for this type
of contract? State from retrieved financial reports and retrieved
standard provisions only. CANNOT CONFIRM if the standard is not in
Layer 2b.

**Contract asset or liability position:** Does the project carry a
contract asset (revenue recognised exceeds amounts billed) or contract
liability (amounts billed exceed revenue recognised)? Is this position
disclosed in the retrieved financial reports? State from retrieved
documents only.

**Provision for foreseeable losses:** Where retrieved financial reports
indicate a forecast overrun: has a provision for the foreseeable loss
been recognised in the period it was identified? State from retrieved
documents. CANNOT CONFIRM if the applicable standard is not in Layer 2b.

**Onerous contract assessment:** Where the retrieved cost-to-complete
exceeds the remaining revenue, has the contract been assessed as
onerous in the retrieved financial reports? State from retrieved
documents only.

Do not characterise what the accounting standard requires from training
knowledge. All characterisations come from retrieved Layer 2b provisions.
If the standard is not in Layer 2b: state CANNOT CONFIRM and list what
cannot be assessed.

### Step 5 — Assess financial reporting controls

From retrieved Layer 2a financial controls policy:
- What review and sign-off is required before financial reports are
  issued? Is this evidenced in the retrieved reports?
- Are the retrieved reports signed, approved, or reviewed by the
  parties required under the internal policy?
- Where a report has been issued without the required sign-off:
  flag as a financial control deficiency.

CANNOT ASSESS if Layer 2a policy was not retrieved.

---

## Classification and decision rules

**GREEN:** All required reports present and current; cadence consistent
with contractual and internal obligations; reports internally consistent
with each other; applicable accounting standard retrieved and findings
consistent with its provisions; financial reporting controls evidenced.

**AMBER:** One or more of: reports present but cadence gaps exist;
minor inter-report inconsistency identified; accounting standard not
in Layer 2b — compliance cannot be confirmed; internal policy not
retrieved; financial controls sign-off not evidenced for one or more
reports.

**RED:** Material inter-report inconsistency — cost report and cash
flow statement inconsistent for the same period; required reports
absent for a material portion of the project duration; provision for
foreseeable loss not recognised in retrieved reports where a forecast
overrun is documented.

**GREY:** No financial reports retrieved — reporting compliance cannot
be assessed from the warehouse.

---

## When to call tools

- Call `search_chunks` to retrieve all financial report types from
  Layer 1 — use broad queries: cost report, cash flow, budget report,
  management accounts, financial forecast, board report
- Call `search_chunks` with `layer_type = '2a'` for internal financial
  reporting policy and accounting principles
- Call `search_chunks` with `layer_type = '2b'` for the applicable
  accounting standard — query by subject matter (revenue recognition,
  long-term contracts, contract assets, foreseeable losses)
- Call `get_related_documents` when a retrieved chunk indicates a
  financial report or audit letter exists — retrieve the full document
- Always call tools before concluding any report or policy is absent

---

## Always flag — regardless of query

- **Required report absent from warehouse** — state which report type,
  the period it should cover, and which obligation required it
- **Material inter-report inconsistency** — state the two reports,
  the period, and the discrepancy from retrieved figures
- **Foreseeable loss not provisioned** — where a forecast overrun is
  evidenced in retrieved cost reports but no provision appears in
  retrieved financial accounts for the same period
- **Applicable accounting standard not in Layer 2b** — state which
  standard was expected, that it was not found, and what accounting
  compliance assessments cannot proceed
- **Financial reporting cadence gap** — where reports are absent for
  periods required by the retrieved contractual or internal obligation
- **Financial controls sign-off absent** — where retrieved policy
  requires sign-off and retrieved reports show no evidence of it
- **Inconsistency between project reports and management accounts** —
  where both exist and figures for the same period do not reconcile

---

## Output format

```
## Financial Reporting Compliance

### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [accounting standard name — or NOT RETRIEVED]
Layer 2b provisions retrieved: [revenue recognition, contract assets,
  foreseeable losses — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE]
Layer 2a source: [financial reporting policy name — or NOT RETRIEVED /
  NOT APPLICABLE]
Layer 1 primary document: [list all financial reports retrieved]
Layer 1 amendment document: [NOT APPLICABLE — this skill assesses
  reporting compliance, not contractual amendment positions]
Provisions CANNOT CONFIRM: [list — or NONE]

### Documents Retrieved (Layer 1)
[Every retrieved financial report — type, period, date, preparer]

### Documents Not Retrieved
[Every required report or policy absent — which steps are affected.
If nothing missing: "None."]

### Layer 2b Reference
[Retrieved accounting standard and relevant provisions — or:
CANNOT CONFIRM — [standard name] NOT IN WAREHOUSE]

### Reporting Obligations
Contractual: [per contract — report type, frequency, content
  from retrieved documents. CANNOT CONFIRM where not retrieved.]
Internal policy: [from retrieved Layer 2a — or CANNOT CONFIRM]
Accounting standard: [from retrieved Layer 2b — or CANNOT CONFIRM]

### Report Completeness Assessment
[GREEN / AMBER / RED / GREY / CANNOT ASSESS]
[For each required report type:]
[Report type]: [PRESENT AND COMPLIANT / PRESENT BUT INCOMPLETE /
  ABSENT / CANNOT ASSESS]
[State cadence finding and content gaps where applicable]

### Inter-Report Consistency Assessment
[GREEN / AMBER / RED / GREY / CANNOT ASSESS]
Cost report vs cash flow: [CONSISTENT / INCONSISTENT / CANNOT ASSESS]
Cost report vs payment certificates: [CONSISTENT / INCONSISTENT /
  CANNOT ASSESS]
Budget report vs variation register: [CONSISTENT / INCONSISTENT /
  CANNOT ASSESS]
Financial forecast vs cost report: [CONSISTENT / INCONSISTENT /
  CANNOT ASSESS]
Management accounts vs project reports: [CONSISTENT / INCONSISTENT /
  CANNOT ASSESS — state if either absent]
[Narrative for each inconsistency — state discrepancy from retrieved
figures and both source documents]

### Accounting Standard Compliance
[GREEN / AMBER / RED / GREY / CANNOT ASSESS]
Applicable standard: [identified from Layer 2a or Layer 1 — or
  CANNOT CONFIRM]
Revenue recognition method: [from retrieved reports — or CANNOT CONFIRM]
Contract asset/liability: [disclosed / not disclosed / CANNOT CONFIRM]
Foreseeable loss provision: [recognised / not recognised where required /
  CANNOT CONFIRM]
Onerous contract assessment: [performed / not evidenced / CANNOT CONFIRM]
[All findings from retrieved Layer 2b provisions only]

### Financial Reporting Controls
[GREEN / AMBER / RED / GREY / CANNOT ASSESS]
[Finding — state whether required sign-off is evidenced in retrieved
reports or CANNOT ASSESS if Layer 2a policy not retrieved]

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

Financial reporting compliance on a construction project has three
distinct obligation layers: what each contract requires, what internal
policy requires, and what the applicable accounting standard requires.
All three are retrieved from the warehouse — none are assumed. Where
the applicable accounting standard is not in Layer 2b, revenue
recognition, foreseeable loss, and contract asset/liability assessments
cannot proceed. The agent does not apply accounting standards from
training knowledge. Inter-report consistency is assessed arithmetically
from retrieved figures — the agent does not reconcile across documents
it has not retrieved.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies
to any contract form. All characterisations grounded in retrieved warehouse
documents only.*
