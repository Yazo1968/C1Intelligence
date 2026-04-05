# EVM and Cost Reporting

**Skill type:** Mixed
- Contract-type-agnostic: the EVM methodology and metric
  interpretation (CPI, SPI, EAC, ETC, VAC) apply regardless of
  standard form or version
- Contract-type-specific: whether EVM reporting is a contractual
  obligation, the required reporting format, and the reporting
  frequency are stated in the retrieved amendment document, Contract
  Data, or Employer's Requirements — they differ by project
**Layer dependency:**
- Layer 1 — project documents: EVM reports (Excel, Primavera
  export, PDF); monthly progress reports (EVM section); cost
  reports; budget documents; amendment document or Employer's
  Requirements (EVM reporting obligation); Contract Data (reporting
  periods); payment certificates (actual cost verification)
- Layer 2b — reference standards: AACE International EVM standards
  (if ingested); PMI/PMBoK EVM framework (if ingested)
**Domain:** Schedule & Programme SME
**Invoked by:** Financial orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when retrieved documents contain EVM reports, earned value
data, S-curves comparing planned vs actual vs earned value, cost
performance reports, or a query about project financial performance,
cost overrun, schedule performance, or EAC/ETC projections. Apply
when the Financial orchestrator requires programme performance data
to support its financial assessment.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings and programme_assessment
findings.

From the invoking orchestrator extract:
- Whether EVM reporting is a contractual or reporting obligation
  under the retrieved contract documents — confirm from the retrieved
  amendment document, Employer's Requirements, or Contract Data

From programme_assessment:
- The baseline programme and its formal status — EVM planned value
  is derived from the accepted baseline programme; if the baseline
  programme status is disputed, the PV baseline may also be disputed

**Critical principle:** The agent extracts what the retrieved EVM
reports say. It does not calculate EVM metrics. CPI, SPI, EAC, ETC,
and VAC are extracted from the retrieved documents — not derived by
the agent from first principles. If an EVM report contains these
metrics: state what the report says and the report reference. If
the metrics are not in the retrieved documents: state NOT FOUND IN
RETRIEVED DOCUMENTS.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- EVM reports for the period under analysis (in any format: Excel,
  Primavera P6 export, PDF progress report section)
- Monthly progress reports containing EVM data tables or S-curves
- Budget document — the Budget at Completion (BAC) baseline
- Amendment document or Employer's Requirements — EVM reporting
  obligation, required format, reporting frequency
- Contract Data — reporting periods
- Payment certificates — for Actual Cost (AC) verification
- The accepted baseline programme — for Planned Value (PV) baseline

**If no EVM reports are retrieved:**
State CANNOT ASSESS EVM performance — no EVM reports found in
the warehouse. Call tools to search before concluding.

**If EVM reports are retrieved but do not contain all metrics:**
State what metrics are present and what are absent. Extract only
what the retrieved documents contain.

**If the Budget at Completion (BAC) is not confirmed from a
retrieved budget document:**
State CANNOT CONFIRM BAC. EAC, VAC, and TCPI cannot be assessed
without BAC.

### Layer 2b documents to retrieve (reference standards)

Call `search_chunks` with `layer_type = '2b'` to retrieve:
- AACE International EVM standards (search by subject matter:
  "AACE earned value management EVM metrics")
- PMBoK EVM framework (search by subject matter: "PMBoK earned
  value planned value SPI CPI")

**Purpose:** To apply the standard EVM metric definitions as the
interpretive framework for assessing the retrieved reports.

**If Layer 2b EVM standards are not retrieved:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE. Apply
standard EVM metric definitions and note that Layer 2b
confirmation is absent from the warehouse.

---

## Analysis workflow

### Step 1 — Confirm the EVM reporting obligation
*Contract-type-specific*

From the retrieved amendment document, Employer's Requirements, or
Contract Data:
- Is EVM reporting a contractual obligation? Cite the retrieved
  clause or provision.
- What reporting format is required?
- What is the required reporting frequency?
- What metrics are required to be reported?

**Do not assume EVM is a contractual obligation without a retrieved
document confirming it.** If no contractual EVM requirement is found
after searching: state that EVM reporting has not been confirmed as
a contractual obligation from the retrieved documents. Note that
EVM reports may exist as an internal or employer reporting tool
even where not contractually required.

### Step 2 — Retrieve and identify all EVM data in the warehouse
*Contract-type-agnostic*

Call `get_related_documents` with document types "EVM Report",
"Cost Performance Report", "Earned Value Report".
Call `search_chunks` with query "earned value CPI SPI EAC planned
actual earned".

For each retrieved EVM document:
- State the document reference, date, and period covered
- Identify the format
- Identify which EVM metrics are present

### Step 3 — Extract EVM metrics from retrieved reports
*Contract-type-agnostic*

For the most recent retrieved EVM report, extract:

From the retrieved document:
- **BAC (Budget at Completion)**
- **PV (Planned Value) at the reporting date**
- **EV (Earned Value) at the reporting date**
- **AC (Actual Cost) at the reporting date**
- **SV (Schedule Variance = EV − PV):** as stated in the retrieved report
- **CV (Cost Variance = EV − AC):** as stated
- **SPI (Schedule Performance Index = EV/PV):** as stated
- **CPI (Cost Performance Index = EV/AC):** as stated
- **EAC (Estimate at Completion):** as stated
- **ETC (Estimate to Complete):** as stated
- **VAC (Variance at Completion = BAC − EAC):** as stated
- **TCPI (To-Complete Performance Index):** as stated if present

**Extract all values exactly as stated in the retrieved document.**
Do not recalculate. Do not adjust. If a metric is not in the
retrieved report: state NOT IN RETRIEVED REPORT for that metric.

### Step 4 — Cross-verify AC against payment certificates
*Contract-type-agnostic*

The Actual Cost (AC) in the EVM report should be consistent with
the certified and paid amounts in the payment certificates.
From the retrieved payment certificates:
- What is the cumulative certified amount at the reporting date?
- Does this correspond to the AC in the retrieved EVM report?

**State both figures and their sources.** If they differ: flag the
discrepancy. Do not resolve the discrepancy — present both figures.

### Step 5 — Cross-verify PV against the accepted programme
*Contract-type-agnostic*

The Planned Value (PV) baseline should derive from the accepted
baseline programme. From programme_assessment findings:
- Was the baseline programme formally accepted?
- Does the PV baseline in the retrieved EVM report appear to
  correspond to the accepted programme?

**If the baseline programme was not formally accepted:** Flag that
the PV baseline in the EVM report may be based on a disputed
programme; state the programme_assessment conclusion.

### Step 6 — Assess trend across reporting periods
*Contract-type-agnostic*

If multiple EVM reports have been retrieved for consecutive periods:
- Extract the SPI and CPI trend across the retrieved periods
- Identify whether performance is improving, stable, or deteriorating
  from the retrieved data
- Identify the earliest period where performance indicators fell
  below 1.0

**State only what the retrieved reports show.** Do not project
future performance or calculate trend lines.

### Step 7 — Identify contradictions between EVM and other reports
*Contract-type-agnostic*

From the retrieved progress reports for the same period:
- Does the narrative describe a project on programme while EVM
  shows SPI below 1.0?
- Does the programme update show on-programme while EVM shows
  schedule slippage?

**State both documents and their respective positions.**
Flag any contradiction with both source documents cited.

### Fallback — No EVM Reports in Warehouse

If no EVM report has been retrieved after exhausting tool searches, and
budget documents, payment certificates, or progress reports with financial
data ARE retrieved — proceed with a partial financial performance assessment
using only those documents. Do not calculate EVM metrics.

Extract from retrieved budget documents:
- Approved budget (BAC equivalent): state value and source
- Budget breakdown by cost category: state from retrieved documents

Extract from retrieved payment certificates and cost reports:
- Actual cost to date (AC equivalent): state value and source
- Certified amount to date: state value and source

Extract from retrieved progress reports:
- Percentage complete as reported: state value, report date, and source

State explicitly:
> No formal EVM report was found in the warehouse. This assessment is
> derived from budget, payment, and progress documents only. EVM metrics
> (CPI, SPI, EAC, ETC, VAC) cannot be extracted — they have not been
> reported in the retrieved documents.

Flag: EVM REPORTING NOT FOUND IN WAREHOUSE — list which financial
documents were retrieved. Set confidence to AMBER.

Do not produce SPI, CPI, EAC, ETC, or VAC values under the fallback
path. These are extracted metrics — if not in retrieved documents,
they are not available.

---

## Classification and decision rules

**Schedule performance (from retrieved SPI):**

SPI = 1.0: ON SCHEDULE
SPI 0.9–0.99: MINOR SCHEDULE SLIPPAGE
SPI 0.8–0.89: MODERATE SCHEDULE SLIPPAGE
SPI below 0.8: SIGNIFICANT SCHEDULE SLIPPAGE — flag
SPI above 1.0: AHEAD OF SCHEDULE

**Cost performance (from retrieved CPI):**

CPI = 1.0: ON BUDGET
CPI 0.9–0.99: MINOR COST OVERRUN
CPI 0.8–0.89: MODERATE COST OVERRUN — flag
CPI below 0.8: SIGNIFICANT COST OVERRUN — flag
CPI above 1.0: UNDER BUDGET

**These classifications are applied to values extracted from the
retrieved documents — they are not the agent's own assessment.**

**EAC vs BAC:**

EAC exceeds BAC → COST OVERRUN FORECAST — state EAC, BAC, and VAC
EAC below BAC → COST SAVINGS FORECAST — state values
EAC not in retrieved report → CANNOT CONFIRM EAC FROM WAREHOUSE

**Contradictions:**

EVM data and progress report narrative contradict →
CONTRADICTION — flag; state both documents and positions

---

## When to call tools

**Signal:** EVM report not retrieved in initial search
**Action:** `search_chunks` with query "earned value EVM CPI SPI
EAC performance report [period]"; `get_related_documents` with
document types "EVM Report", "Cost Report", "Progress Report"
**Look for:** Any document containing EVM metrics

**Signal:** Budget at Completion not confirmed
**Action:** `search_chunks` with query "budget at completion BAC
approved budget contract sum"; `get_related_documents` with
document type "Budget", "Cost Plan"
**Look for:** The approved budget document

**Signal:** EVM reporting obligation not confirmed
**Action:** `search_chunks` with query "earned value EVM reporting
requirement employer requirements contract data"; `get_document`
on Employer's Requirements document ID if known
**Look for:** The clause or provision requiring EVM reporting

**Signal:** Payment certificates not retrieved for AC cross-check
**Action:** `get_related_documents` with document type "Interim
Payment Certificate", "Payment Certificate"
**Look for:** Certified amounts for the EVM reporting period

---

## Always flag — regardless of query

1. **SPI below 0.8 or CPI below 0.8 in any retrieved EVM report**
   — flag; state the metric value, reporting period, and source.

2. **EAC exceeds BAC in retrieved reports** — flag; state EAC,
   BAC, and VAC from the retrieved document.

3. **Contradiction between EVM metrics and progress report
   narrative** — flag both documents; state the contradiction.

4. **EVM reports absent from warehouse** — flag; state that project
   performance cannot be assessed from warehouse documents.

5. **PV baseline derived from a disputed or unaccepted programme**
   — flag; state the programme_assessment finding and its
   implication for the reliability of the PV baseline.

6. **AC in EVM report inconsistent with certified amounts in
   payment certificates** — flag; state both values and sources.

---

## Output format

```
## EVM and Cost Reporting Assessment

### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [standard or methodology name — or NOT RETRIEVED]
Layer 2b provisions retrieved: [description — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE]
Layer 2a source: [policy name — or NOT RETRIEVED / NOT APPLICABLE]
Layer 1 primary document: [name and reference — or NOT RETRIEVED]
Layer 1 amendment document: [name — or NOT RETRIEVED / NOT APPLICABLE]
Provisions CANNOT CONFIRM: [list — or NONE]

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2b Reference Retrieved
[State whether AACE/PMBoK EVM standards were retrieved from Layer 2b.
If not: state CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE and
note that standard EVM definitions have been applied.]

### EVM Reporting Obligation
Contractual obligation confirmed: [YES — clause and source /
NOT CONFIRMED FROM RETRIEVED DOCUMENTS]
Required format: [from retrieved documents / NOT STATED]
Reporting frequency: [from retrieved documents / NOT STATED]

### EVM Reports Retrieved
[List each retrieved EVM report with reference, date, period covered,
and format. If none: state NOT FOUND IN WAREHOUSE.]

### Budget at Completion (BAC)
BAC: [value from retrieved budget document / CANNOT CONFIRM —
budget document not retrieved]
Source: [document reference]

### EVM Metrics (from retrieved reports)
Reporting date: [date]
Source document: [reference]

| Metric | Value from retrieved report | Interpretation |
|---|---|---|
| PV | [value / NOT IN REPORT] | [Planned value to date] |
| EV | [value / NOT IN REPORT] | [Earned value to date] |
| AC | [value / NOT IN REPORT] | [Actual cost to date] |
| SV | [value / NOT IN REPORT] | [Schedule variance] |
| CV | [value / NOT IN REPORT] | [Cost variance] |
| SPI | [value / NOT IN REPORT] | [classification from retrieved value] |
| CPI | [value / NOT IN REPORT] | [classification from retrieved value] |
| EAC | [value / NOT IN REPORT] | [Estimate at completion] |
| ETC | [value / NOT IN REPORT] | [Estimate to complete] |
| VAC | [value / NOT IN REPORT] | [Variance at completion] |
| TCPI | [value / NOT IN REPORT] | [To-complete performance index] |

### AC Cross-Verification
Cumulative certified amount (from retrieved payment certificates):
[value / NOT FOUND]
AC in retrieved EVM report: [value / NOT IN REPORT]
Consistency: [CONSISTENT / DISCREPANCY — state both values and sources /
CANNOT ASSESS]

### PV Baseline Cross-Verification
PV baseline derived from: [accepted programme — reference /
programme not formally accepted — flag / CANNOT CONFIRM]

### Performance Trend (if multiple reports retrieved)
| Period | SPI | CPI | Source |
|---|---|---|---|
| [period] | [value] | [value] | [report reference] |
Trend: [IMPROVING / STABLE / DETERIORATING / CANNOT ASSESS]

### Contradictions
[Contradiction between EVM and other reports with both document
references, or NONE IDENTIFIED IN RETRIEVED DOCUMENTS]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — metric definitions are applied to values extracted
from retrieved documents. The agent does not calculate EVM metrics.*

**EVM metric definitions — analytical reference:**
PV (Planned Value): budgeted cost of work scheduled to the reporting
date. EV (Earned Value): budgeted cost of work actually performed.
AC (Actual Cost): actual cost incurred. SPI = EV/PV. CPI = EV/AC.
EAC: estimated total cost at completion. ETC: remaining cost.
VAC = BAC − EAC. TCPI: efficiency required to complete within budget.
These are standard EVM definitions — apply them only to values
extracted from retrieved documents. Never derive these metrics from
raw cost and programme data in the warehouse.

**EVM reporting obligations — analytical reference:**
EVM reporting requirements vary by project and contract type. Some
contracts mandate specific EVM formats and frequencies; others leave
EVM as an internal or employer reporting tool. The contractual
obligation (if any) is always stated in the retrieved contract
documents — extract from Layer 1.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies to
any contract form. All characterisations grounded in retrieved warehouse
documents only.*
