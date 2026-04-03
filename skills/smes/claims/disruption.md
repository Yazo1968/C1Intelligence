# Disruption

**Skill type:** Mixed
- Contract-type-specific: entitlement basis and recoverable heads
  depend on which FIDIC sub-clause applies — differs by book and
  edition; Particular Conditions amendments are project-specific
- Contract-type-agnostic: the methodology for measuring productivity
  loss (measured mile, industry study, global claim) applies
  regardless of contract type; the evidential requirements apply
  regardless of contract type
**Layer dependency:**
- Layer 1 — project documents: disruption claim submission;
  Particular Conditions (entitlement clause, definition of Cost);
  contemporaneous records (labour returns, daily reports, quantity
  records); instructions or RFIs causing the disruption; payment
  certificates
- Layer 2 — reference standards: FIDIC entitlement sub-clause for
  the confirmed book and edition; SCL Protocol 2nd Edition 2017
  (disruption methodology framework); AACE RP 29R-03 (if referenced
  in the claim)
**Domain:** Claims & Disputes SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when retrieved chunks contain a disruption claim, a loss of
productivity claim, a measured mile analysis, a labour inefficiency
claim, or a query about whether reduced productivity is recoverable.
Apply when retrieved chunks reference acceleration without a formal
acceleration instruction — this may indicate constructive acceleration
arising from disruption.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings and notice_compliance findings.

From the invoking orchestrator extract:
- Confirmed FIDIC book and edition
- The entitlement basis established from retrieved documents — the
  sub-clause under which the disruption is claimed and whether it
  provides for Cost (or Cost plus Profit)

**Disruption is distinct from prolongation.** Prolongation covers
time-related costs of being on site longer than planned. Disruption
covers loss of productivity during the works — additional resources
used for the same scope due to Employer interference, without
necessarily additional time. Assess separately.

From notice_compliance:
- Time bar status — if POTENTIALLY TIME-BARRED: flag at the start

**If book type is UNCONFIRMED:** State CANNOT CONFIRM entitlement
basis. Do not proceed with entitlement assessment.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The disruption claim submission
- The Particular Conditions — entitlement clause and definition of Cost
- Contemporaneous records for both the disrupted and any claimed
  undisrupted (baseline) periods:
  - Labour returns and timesheets
  - Daily site diaries
  - Quantity records (output per trade per period)
  - Supervision or foreman reports recording productivity issues
- Instructions, RFIs, or correspondence from the Engineer cited as
  causing the disruption
- Any industry productivity study referenced in the claim

**If the Particular Conditions are not retrieved:**
State CANNOT CONFIRM entitlement basis or cost recoverability.
Do not proceed with entitlement assessment.

**If no contemporaneous records are retrieved:**
State that the disruption claim has not been independently verified
from warehouse records. Flag this as a critical evidential gap for
every head of claim.

**If no baseline period records are retrieved:**
State CANNOT VERIFY the measured mile analysis — there is no
independently confirmed undisrupted baseline.

### Layer 2 documents to retrieve (reference standards)

Call `search_chunks` to retrieve from Layer 2:
- The FIDIC entitlement sub-clause for the confirmed book and edition
  under which the disruption is claimed
- SCL Protocol 2nd Edition 2017 guidance on disruption (if available
  in Layer 2)

**Purpose:** To establish the standard FIDIC entitlement baseline
and the SCL Protocol framework for methodology assessment. The
entitlement terms to apply are always those in the retrieved
Particular Conditions.

---

## Analysis workflow

### Step 1 — Retrieve all disruption claim documents
*Contract-type-agnostic*

Call `get_related_documents` with document type "Disruption Claim".
Call `search_chunks` with query "loss of productivity disruption
measured mile labour inefficiency".
Compile all retrieved disruption claim documents and supporting
analyses.

### Step 2 — Confirm entitlement basis
*Contract-type-specific*

From the retrieved Particular Conditions:
- Identify the sub-clause cited as the entitlement basis
- Confirm whether it provides for Cost, or Cost plus Profit
- Confirm whether the disruption events qualify under that clause

**Disruption is not expressly provided for as a standalone head in
FIDIC.** It is claimed under the same Employer Risk Event clauses
as EOT and prolongation cost. The qualifying events in the retrieved
Particular Conditions govern — not the General Conditions standard
list without confirmation.

If the Particular Conditions have not been retrieved: state CANNOT
CONFIRM entitlement basis. Do not classify any event as qualifying.

### Step 3 — Identify and assess the disruption events
*Contract-type-agnostic*

For each disruption event claimed:
- Identify the event from the retrieved claim document
- Identify the Employer instruction, RFI, or action cited as the cause
- Retrieve that instruction or RFI from the warehouse — confirm it
  exists and predates the disruption period
- Identify the work activity or trade affected
- Identify the period of disruption

**Do not characterise an event as an Employer-caused disruption
without retrieving the instruction or correspondence that caused it.**
If the causal document is not in the warehouse: state CANNOT CONFIRM
the Employer cause from retrieved documents.

### Step 4 — Assess the productivity measurement methodology
*Contract-type-agnostic*

Identify the methodology from the retrieved analysis document —
do not assume. The methodology must be identified from what the
retrieved documents describe.

**(a) Measured mile (preferred):**
Requires: an undisrupted baseline period and a disrupted period
on the same project, same trade, comparable work.

From retrieved documents assess:
- Has a genuine undisrupted baseline period been identified in the
  retrieved records? State the baseline period and its source.
- Is the baseline from the same project, same trade, and comparable
  conditions? State the basis for this from retrieved documents.
- Is the productivity metric consistent and stated in the retrieved
  claim (e.g. cubic metres per labour hour)?
- Are both the baseline and disrupted period productivity rates
  supported by retrieved labour returns and quantity records?

If the baseline period records have not been retrieved: state CANNOT
VERIFY the measured mile — there is no independently confirmed
undisrupted productivity rate from the warehouse.

**(b) Industry productivity studies (e.g. MCAA, AACE, CII):**
Identify the specific study and factors cited in the retrieved
claim document. Note that these studies reflect North American or
European norms. From retrieved documents: is there any project-specific
adjustment stated in the claim? If not: flag that the factors have
been applied without GCC-specific adjustment — state this limitation.

**(c) Global disruption claim:**
If the claim is presented as a global claim without individual
causation links: from retrieved documents assess whether a measured
mile was feasible (i.e. whether the warehouse contains records from
both disrupted and undisrupted periods that would support a measured
mile). If such records are present: flag the methodology choice as
a weakness and state the available records.

**If the methodology cannot be identified from retrieved documents:**
State CANNOT IDENTIFY METHODOLOGY.

### Step 5 — Assess causation
*Contract-type-agnostic*

For each disruption event, causation must be established from
retrieved documents — not assumed from the claim submission.

From retrieved documents assess:
- Is there a demonstrable causal link between the retrieved Employer
  instruction/event and the productivity reduction in the retrieved
  records?
- Does the baseline period (if retrieved) exclude periods affected
  by Contractor inefficiency, learning curve, or weather?
- Has the claim addressed the Contractor's own contribution to any
  productivity loss?

**Do not characterise causation as established without retrieved
evidence.** If the causal link is not evidenced in retrieved documents:
state CANNOT ESTABLISH CAUSATION FROM RETRIEVED DOCUMENTS.

### Step 6 — Assess the quantum
*Contract-type-agnostic*

From retrieved documents:
- Is the planned productivity rate from the retrieved original
  programme or priced bill — or retrospectively revised?
- Is the actual productivity rate from retrieved contemporaneous
  records — or from the claim submission only?
- Is the cost rate applied to the additional hours consistent with
  the retrieved contract rates or payroll records?

**Do not verify any rate without a retrieved source document.**
If a rate has no retrieved source: state CANNOT VERIFY from
warehouse documents.

### Step 7 — Assess constructive acceleration
*Contract-type-agnostic*

From retrieved documents, assess whether the following conditions
are all present:
- An EOT was claimed and denied or not responded to within the
  period in the retrieved Contract Data
- The Contractor gave notice of acceleration and its cost —
  retrieve this notice
- Acceleration measures were implemented — retrieve evidence
  of additional resources or extended hours

**Only flag constructive acceleration if all three conditions are
evidenced in retrieved documents.** If the evidence is partial:
state which conditions are evidenced and which are not.

---

## Classification and decision rules

**Entitlement basis:**

Disruption events qualify under retrieved PC entitlement clause →
ENTITLEMENT BASIS CONFIRMED — proceed with methodology and quantum
Disruption events do not qualify under retrieved PC → OUT OF SCOPE
under retrieved clause — flag
PC not retrieved → CANNOT CONFIRM ENTITLEMENT BASIS

**Causation:**

Causal link between Employer event and productivity loss evidenced
in retrieved documents → CAUSATION EVIDENCED FROM RETRIEVED DOCUMENTS
Productivity reduction present but causal link not evidenced in
retrieved documents → CAUSATION NOT ESTABLISHED FROM RETRIEVED
DOCUMENTS — flag; state what evidence would be needed
Mixed causation evidenced → CAUSATION PARTIAL — flag; state the
mixed causation from retrieved documents

**Measured mile:**

Undisrupted baseline retrieved, comparable to disrupted period,
records for both periods present → MEASURED MILE VERIFIABLE
Baseline not retrieved → CANNOT VERIFY MEASURED MILE — flag

**Global disruption:**

Global claim presented AND records from both disrupted and undisrupted
periods are in the warehouse → METHODOLOGY WEAKNESS — flag; state
the available records
Global claim AND no undisrupted baseline period exists in the
warehouse → LAST RESORT METHODOLOGY — flag the limitation; note
that the aggregate must be verified from records

**Constructive acceleration:**

All three conditions evidenced in retrieved documents →
POSSIBLE CONSTRUCTIVE ACCELERATION — flag; state the conditions
evidenced
Partial conditions only → INSUFFICIENT EVIDENCE FOR CONSTRUCTIVE
ACCELERATION FROM RETRIEVED DOCUMENTS — state what is evidenced

---

## When to call tools

**Signal:** Disruption claim references Employer instructions or RFIs
as the cause but these have not been retrieved
**Action:** `search_chunks` with query "[instruction or RFI reference]
[date range]"; `get_related_documents` with document types
"Engineer's Instruction", "RFI"
**Look for:** The causal document — confirm it exists and predates
the disruption period

**Signal:** Measured mile analysis references a baseline period but
no site records for that period retrieved
**Action:** `get_related_documents` with document types "Site Diary",
"Daily Report" for the baseline period dates; `search_chunks` with
query "labour return productivity [baseline period dates]"
**Look for:** Labour returns, quantity records, or daily reports
covering the baseline period

**Signal:** Industry study referenced but the specific study or
factors not identified in the retrieved claim
**Action:** `search_chunks` with query "productivity factor MCAA
AACE CII inefficiency table"
**Look for:** The specific study reference and the factors applied

**Signal:** Constructive acceleration suspected — EOT claimed but
no response retrieved
**Action:** `get_related_documents` with document type "Engineer's
Determination"; `search_chunks` with query "extension of time
response determination [claim reference]"
**Look for:** Whether EOT was responded to and any acceleration notice

---

## Always flag — regardless of query

1. **No contemporaneous records retrieved** — state that the
   disruption claim cannot be independently verified from warehouse
   documents.

2. **Global disruption where measured mile was feasible from
   retrieved records** — state the available records and the
   methodology weakness.

3. **Industry study factors applied without GCC-specific adjustment**
   — state this limitation from the retrieved claim document.

4. **Causation not established for a material head from retrieved
   documents** — state what evidence would be required.

5. **Possible constructive acceleration evidenced in retrieved
   documents** — state the conditions evidenced and their implication.

---

## Output format

```
## Disruption Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2 Reference Retrieved
[State whether the entitlement clause and SCL Protocol were retrieved
from Layer 2. If not: state analytical knowledge applied.]

### Notice Position
[From notice_compliance findings — time bar caveat if applicable]

### Entitlement Basis
FIDIC book and edition: [from orchestrator findings]
Entitlement clause: [from retrieved PC / CANNOT CONFIRM]
Cost recoverable: [YES — clause / NO / CANNOT CONFIRM]
Profit recoverable: [YES / NO — Cost only / CANNOT CONFIRM]

### Disruption Event Register

| # | Event | Causal document retrieved | Period | Activity | Methodology | Causation | Records |
|---|---|---|---|---|---|---|---|
| 1 | [description] | [ref or NOT RETRIEVED] | [dates] | [trade/activity] | [methodology] | [EVIDENCED/NOT ESTABLISHED/PARTIAL] | [PRESENT/PARTIAL/ABSENT] |

### Findings by Disruption Event

**[Event description]**
Period: [dates]
Activity affected: [trade or activity]
Causal document: [retrieved reference / NOT FOUND IN WAREHOUSE]
Methodology: [measured mile / industry study — name / global]
Baseline period: [dates and source documents / NOT RETRIEVED]
Planned productivity rate: [rate and source document / NOT CONFIRMED]
Actual productivity rate: [rate and source document / NOT CONFIRMED]
Productivity loss: [from retrieved records / CANNOT CONFIRM — records not retrieved]
Causation: [EVIDENCED — source docs / NOT ESTABLISHED / PARTIAL — describe]
Contemporaneous records: [PRESENT — list / PARTIAL — gaps / ABSENT]
Quantum claimed: [amount]
Quantum verifiable from retrieved documents: [amount / CANNOT VERIFY — reason]
Finding: [from retrieved documents only]

### Constructive Acceleration
EOT claimed and denied/not responded to: [YES — source / NO / CANNOT CONFIRM]
Acceleration notice issued: [YES — reference / NOT FOUND]
Acceleration measures evidenced: [YES — source / NOT FOUND]
Assessment: [POSSIBLE CONSTRUCTIVE ACCELERATION — conditions evidenced /
INSUFFICIENT EVIDENCE FROM RETRIEVED DOCUMENTS / NOT APPLICABLE]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any methodology standard, causation
framework, or productivity factor from this section without first
identifying its application from the retrieved claim documents and
verifying inputs from retrieved project records.*

**SCL Protocol 2017 — disruption principles (analytical reference):**
Contemporaneous records are essential for disruption claims. The
measured mile is the preferred methodology. Global disruption claims
are treated with caution and require the Contractor to demonstrate
it was impossible to link individual causes to individual effects.
Industry study factors are corroborating evidence only — not a
substitute for project-specific records. Retrieve the Protocol
from Layer 2 to apply these principles.

**Measured mile requirements — analytical reference:**
The baseline must be genuinely undisrupted — excluding learning
curve, mobilisation, weather, or Contractor inefficiency periods.
The comparison must be like-for-like — same trade, same work type,
comparable conditions. The productivity metric must be consistent
and objectively measurable. Both baseline and disrupted period records
must be retrieved before the measured mile can be verified.

**GCC-specific productivity factors — analytical reference:**
GCC projects are affected by extreme summer heat (mandatory rest
periods in UAE), high labour turnover, mixed-nationality workforces,
and Ramadan working patterns. Industry study factors that do not
account for these conditions face challenge in GCC arbitration.
These are contextual flags — apply to the methodology identified
from retrieved documents only.
