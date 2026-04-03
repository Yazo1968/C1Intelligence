# EVM and Cost Reporting

**Skill type:** Mixed
- Contract-type-agnostic: the EVM methodology and metric
  interpretation (CPI, SPI, EAC, ETC, VAC) apply regardless of
  FIDIC book type or edition
- Contract-type-specific: whether EVM reporting is a contractual
  obligation, the required reporting format, and the reporting
  frequency are stated in the retrieved Particular Conditions,
  Contract Data, or Employer's Requirements — they differ by project
**Layer dependency:**
- Layer 1 — project documents: EVM reports (Excel, Primavera
  export, PDF); monthly progress reports (EVM section); cost
  reports; budget documents; Particular Conditions or Employer's
  Requirements (EVM reporting obligation); Contract Data (reporting
  periods); payment certificates (actual cost verification)
- Layer 2 — reference standards: AACE International EVM standards
  (if available in Layer 2); PMI/PMBoK EVM framework (if available)
**Domain:** Schedule & Programme SME
**Invoked by:** Financial orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when retrieved chunks contain EVM reports, earned value data,
S-curves comparing planned vs actual vs earned value, cost
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
  under the retrieved contract documents — confirm from the
  retrieved Particular Conditions, Employer's Requirements, or
  Contract Data

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
- Contract Data or Employer's Requirements — EVM reporting
  obligation, required format, reporting frequency
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

### Layer 2 documents to retrieve (reference standards)

Call `search_chunks` to retrieve from Layer 2:
- AACE International EVM standards (if ingested in Layer 2)
- PMBoK EVM framework (if ingested in Layer 2)

**Purpose:** To apply the standard EVM metric definitions as the
interpretive framework for assessing the retrieved reports. If Layer
2 EVM standards are not retrieved: apply standard EVM metric
definitions from analytical knowledge and note this in the output.

---

## Analysis workflow

### Step 1 — Confirm the EVM reporting obligation
*Contract-type-specific*

From the retrieved Particular Conditions, Employer's Requirements,
or Contract Data:
- Is EVM reporting a contractual obligation? Cite the retrieved
  clause or provision.
- What reporting format is required? (P6 report, Excel template,
  standard PMBoK format, bespoke Employer format)
- What is the required reporting frequency? (Monthly, quarterly,
  milestone-based)
- What metrics are required to be reported?

**Do not assume EVM is a contractual obligation without a retrieved
document confirming it.** If no contractual EVM requirement is
found after searching: state that EVM reporting has not been
confirmed as a contractual obligation from the retrieved documents.
Note that EVM reports may exist as a PMC or Employer internal
reporting tool even where not contractually required.

### Step 2 — Retrieve and identify all EVM data in the warehouse
*Contract-type-agnostic*

Call `get_related_documents` with document types "EVM Report",
"Cost Performance Report", "Earned Value Report".
Call `search_chunks` with query "earned value CPI SPI EAC planned
actual earned".

For each retrieved EVM document:
- State the document reference, date, and period covered
- Identify the format (Excel, P6 export, PDF)
- Identify which EVM metrics are present

### Step 3 — Extract EVM metrics from retrieved reports
*Contract-type-agnostic*

For the most recent retrieved EVM report (and for any earlier
reports relevant to the query period), extract:

From the retrieved document:
- **BAC (Budget at Completion):** The total approved budget
- **PV (Planned Value) at the reporting date:** The budgeted cost
  of work scheduled to the reporting date
- **EV (Earned Value) at the reporting date:** The budgeted cost
  of work actually performed
- **AC (Actual Cost) at the reporting date:** The actual cost
  incurred
- **SV (Schedule Variance = EV − PV):** As stated in the
  retrieved report
- **CV (Cost Variance = EV − AC):** As stated in the retrieved
  report
- **SPI (Schedule Performance Index = EV/PV):** As stated
- **CPI (Cost Performance Index = EV/AC):** As stated
- **EAC (Estimate at Completion):** As stated in the retrieved
  report
- **ETC (Estimate to Complete):** As stated
- **VAC (Variance at Completion = BAC − EAC):** As stated
- **TCPI (To-Complete Performance Index):** As stated if present

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

**State both figures and their sources.** If they differ: flag
the discrepancy; state both values and the source documents.
Do not resolve the discrepancy — present both figures.

### Step 5 — Cross-verify PV against the accepted programme
*Contract-type-agnostic*

The Planned Value (PV) baseline in the EVM report should derive
from the accepted baseline programme.
From programme_assessment findings:
- Was the baseline programme formally accepted?
- Does the PV baseline in the retrieved EVM report appear to
  correspond to the accepted programme?

**If the baseline programme was not formally accepted (from
programme_assessment):** Flag that the PV baseline in the EVM
report may be based on a disputed programme; state the
programme_assessment conclusion.

### Step 6 — Assess trend across reporting periods
*Contract-type-agnostic*

If multiple EVM reports have been retrieved for consecutive
reporting periods:
- Extract the SPI and CPI trend across the retrieved periods
  (state each period's values from the retrieved reports)
- Identify whether performance is improving, stable, or
  deteriorating from the retrieved data
- Identify the earliest period in the retrieved reports where
  performance indicators fell below 1.0

**State only what the retrieved reports show.** Do not project
future performance or calculate trend lines — the agent reports
what the retrieved documents say.

### Step 7 — Identify contradictions between EVM and other reports
*Contract-type-agnostic*

From the retrieved progress reports for the same period:
- Does the narrative in the progress report describe a project
  on programme / under budget while the EVM data shows SPI or
  CPI below 1.0?
- Does the programme update show on-programme while EVM shows
  schedule slippage?

**State both documents and their respective positions.**
Flag any contradiction with both source documents cited.

---

## Classification and decision rules

**Schedule performance (from retrieved SPI):**

SPI = 1.0: ON SCHEDULE — as stated in retrieved report
SPI 0.9–0.99: MINOR SCHEDULE SLIPPAGE — as stated
SPI 0.8–0.89: MODERATE SCHEDULE SLIPPAGE — as stated
SPI below 0.8: SIGNIFICANT SCHEDULE SLIPPAGE — as stated; flag
SPI above 1.0: AHEAD OF SCHEDULE — as stated

**Cost performance (from retrieved CPI):**

CPI = 1.0: ON BUDGET — as stated in retrieved report
CPI 0.9–0.99: MINOR COST OVERRUN — as stated
CPI 0.8–0.89: MODERATE COST OVERRUN — as stated; flag
CPI below 0.8: SIGNIFICANT COST OVERRUN — as stated; flag
CPI above 1.0: UNDER BUDGET — as stated

**These classifications are applied to the metric values extracted
from the retrieved documents — they are not the agent's own
assessment of project performance.**

**EAC vs BAC:**

EAC in retrieved report exceeds BAC → COST OVERRUN FORECAST —
state EAC, BAC, and VAC from retrieved report
EAC in retrieved report below BAC → COST SAVINGS FORECAST —
state values from retrieved report
EAC not in retrieved report → CANNOT CONFIRM EAC FROM WAREHOUSE

**Contradictions:**

EVM data and progress report narrative contradict on performance →
CONTRADICTION — flag; state both documents and their positions

---

## When to call tools

**Signal:** EVM report not retrieved in initial search
**Action:** `search_chunks` with query "earned value EVM CPI SPI
EAC performance report [period]"; `get_related_documents` with
document types "EVM Report", "Cost Report", "Progress Report"
**Look for:** Any document containing EVM metrics for the period

**Signal:** Budget at Completion not confirmed from retrieved
documents
**Action:** `search_chunks` with query "budget at completion BAC
approved budget contract sum"; `get_related_documents` with
document type "Budget", "Cost Plan"
**Look for:** The approved budget document confirming BAC

**Signal:** EVM reporting obligation not confirmed from retrieved
contract documents
**Action:** `search_chunks` with query "earned value EVM reporting
requirement particular conditions employer requirements";
`get_document` on Employer's Requirements document ID if known
**Look for:** The clause or provision requiring EVM reporting

**Signal:** Payment certificates not retrieved for AC cross-check
**Action:** `get_related_documents` with document type "Interim
Payment Certificate", "Payment Certificate"
**Look for:** Certified amounts for the EVM reporting period

---

## Always flag — regardless of query

1. **SPI below 0.8 or CPI below 0.8 in any retrieved EVM report**
   — flag as SIGNIFICANT performance issue; state the metric value,
   reporting period, and source document.

2. **EAC exceeds BAC in retrieved reports** — flag; state EAC,
   BAC, and VAC from the retrieved document.

3. **Contradiction between EVM metrics and progress report
   narrative** — flag both documents; state the contradiction.

4. **EVM reports absent from warehouse** — flag; state that
   project performance cannot be assessed from warehouse documents.

5. **PV baseline derived from a disputed or unaccepted programme**
   — flag; state the programme_assessment finding and its
   implication for the reliability of the PV baseline.

6. **AC in EVM report inconsistent with certified amounts in
   payment certificates** — flag; state both values and sources.

---

## Output format

```
## EVM and Cost Reporting Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2 Reference Retrieved
[State whether AACE/PMBoK EVM standards were retrieved from Layer 2.
If not: state standard EVM definitions applied from analytical
knowledge.]

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
[For the most recent retrieved report — state the reporting date:]
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
Cumulative certified amount (from retrieved PCs): [value / NOT FOUND]
AC in retrieved EVM report: [value / NOT IN REPORT]
Consistency: [CONSISTENT / DISCREPANCY — state both values and sources /
CANNOT ASSESS — one or both values not retrieved]

### PV Baseline Cross-Verification
PV baseline derived from: [accepted programme — reference /
programme not formally accepted — flag / CANNOT CONFIRM]

### Performance Trend (if multiple reports retrieved)
| Period | SPI | CPI | Source |
|---|---|---|---|
| [period] | [value] | [value] | [report reference] |
Trend: [IMPROVING / STABLE / DETERIORATING — from retrieved data /
CANNOT ASSESS — insufficient periods retrieved]

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
PV (Planned Value): budgeted cost of work scheduled to the
reporting date. EV (Earned Value): budgeted cost of work
actually performed. AC (Actual Cost): actual cost incurred.
SPI = EV/PV: schedule performance index — below 1.0 means
behind schedule. CPI = EV/AC: cost performance index — below
1.0 means over budget. EAC: estimated total cost at completion.
ETC: remaining cost to complete. VAC = BAC − EAC: projected
surplus or overrun. TCPI: efficiency required to complete
within budget. These are standard EVM definitions — apply them
only to values extracted from retrieved documents. Never derive
these metrics from raw cost and programme data in the warehouse.

**GCC EVM practice — analytical reference:**
EVM is increasingly mandated on major GCC projects — Ashghal
(Qatar) requires it above a contract value threshold; Abu Dhabi
government projects and ADNOC projects require it on major
infrastructure and capital programmes; Saudi Aramco and NEOM
require it universally. The format varies: P6 reporting modules,
Excel dashboards, and bespoke Employer templates are all in use.
The contractual obligation (if any) is always stated in the
retrieved Particular Conditions, Employer's Requirements, or
Contract Data — extract from Layer 1.
