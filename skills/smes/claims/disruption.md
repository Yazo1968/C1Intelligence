# Disruption

**Skill type:** Mixed
- Contract-type-specific: entitlement basis and recoverable heads
  depend on which provision applies under the confirmed standard form
  — differs by standard form and version; amendment provisions are
  project-specific
- Contract-type-agnostic: the methodology for measuring productivity
  loss (measured mile, industry study, global claim) applies
  regardless of contract type; the evidential requirements apply
  regardless of contract type
**Layer dependency:**
- Layer 1 — project documents: disruption claim submission;
  amendment document (entitlement clause, definition of cost);
  contemporaneous records (labour returns, daily reports, quantity
  records); instructions or correspondence causing the disruption;
  payment certificates
- Layer 2b — reference standards: entitlement provision for the
  confirmed standard form and version; SCL Protocol 2nd Edition 2017
  (disruption methodology framework, if ingested); AACE RP 29R-03
  (if referenced in the claim)
**Domain:** Claims & Disputes SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when retrieved documents contain a disruption claim, a loss of
productivity claim, a measured mile analysis, a labour inefficiency
claim, or a query about whether reduced productivity is recoverable.
Apply when retrieved documents reference acceleration without a formal
acceleration instruction — this may indicate constructive acceleration
arising from disruption.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings and notice_compliance findings.

From the invoking orchestrator extract:
- Confirmed standard form and version
- The entitlement basis established from retrieved documents — the
  provision under which the disruption is claimed and whether it
  provides for cost (or cost plus profit)

**Disruption is distinct from prolongation.** Prolongation covers
time-related costs of being on site longer than planned. Disruption
covers loss of productivity during the works — additional resources
used for the same scope due to employer interference, without
necessarily additional time. Assess separately.

From notice_compliance:
- Time bar status — if POTENTIALLY TIME-BARRED: flag at the start

**If standard form is UNCONFIRMED:** State CANNOT CONFIRM entitlement
basis. Do not proceed with entitlement assessment.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The disruption claim submission
- The amendment document — entitlement clause and definition of cost
- Contemporaneous records for both the disrupted and any claimed
  undisrupted (baseline) periods:
  - Labour returns and timesheets
  - Daily site diaries
  - Quantity records (output per trade per period)
  - Supervision or foreman reports recording productivity issues
- Instructions, correspondence, or RFIs from the employer or contract
  administrator cited as causing the disruption
- Any industry productivity study referenced in the claim

**If the amendment document is not retrieved:**
State CANNOT CONFIRM entitlement basis or cost recoverability.
Do not proceed with entitlement assessment.

**If no contemporaneous records are retrieved:**
State that the disruption claim has not been independently verified
from warehouse records. Flag this as a critical evidential gap for
every head of claim.

**If no baseline period records are retrieved:**
State CANNOT VERIFY the measured mile analysis — there is no
independently confirmed undisrupted baseline.

### Layer 2b documents to retrieve (reference standards)

Call `search_chunks` with `layer_type = '2b'` to retrieve:
- The entitlement provision for the confirmed standard form under
  which the disruption is claimed (search by subject matter:
  "employer risk event entitlement cost disruption productivity")
- SCL Protocol 2nd Edition 2017 guidance on disruption (if available
  in Layer 2b)

**Purpose:** To establish the standard form entitlement baseline and
the SCL Protocol framework for methodology assessment. The entitlement
terms to apply are always those in the retrieved amendment document.

**If the governing standard form is not retrieved from Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE for the
entitlement provisions. Do not describe the provisions from training
knowledge.

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

From the retrieved amendment document:
- Identify the provision cited as the entitlement basis
- Confirm whether it provides for cost, or cost plus profit
- Confirm whether the disruption events qualify under that provision

Retrieve the applicable provision from Layer 2b to establish the
standard form baseline; then apply the amendment document version.

If the amendment document has not been retrieved: state CANNOT
CONFIRM entitlement basis. Do not classify any event as qualifying.

### Step 3 — Identify and assess the disruption events
*Contract-type-agnostic*

For each disruption event claimed:
- Identify the event from the retrieved claim document
- Identify the employer instruction, correspondence, or action
  cited as the cause
- Retrieve that instruction or correspondence from the warehouse —
  confirm it exists and predates the disruption period
- Identify the work activity or trade affected
- Identify the period of disruption

**Do not characterise an event as employer-caused disruption
without retrieving the instruction or correspondence that caused it.**
If the causal document is not in the warehouse: state CANNOT CONFIRM
the employer cause from retrieved documents.

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
  claim?
- Are both the baseline and disrupted period productivity rates
  supported by retrieved labour returns and quantity records?

If the baseline period records have not been retrieved: state CANNOT
VERIFY the measured mile — there is no independently confirmed
undisrupted productivity rate from the warehouse.

**(b) Industry productivity studies:**
Identify the specific study and factors cited in the retrieved claim
document. From retrieved documents: is there any project-specific
adjustment stated in the claim? If not: flag that the factors have
been applied without project-specific adjustment — state this
limitation from the retrieved claim.

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
- Is there a demonstrable causal link between the retrieved employer
  instruction/event and the productivity reduction in the retrieved
  records?
- Does the baseline period (if retrieved) exclude periods affected
  by contractor inefficiency, learning curve, or weather?
- Has the claim addressed the contractor's own contribution to any
  productivity loss?

**Do not characterise causation as established without retrieved
evidence.** If the causal link is not evidenced in retrieved
documents: state CANNOT ESTABLISH CAUSATION FROM RETRIEVED DOCUMENTS.

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
- A time extension was claimed and denied or not responded to within
  the period in the retrieved Contract Data
- The contractor gave notice of acceleration and its cost — retrieve
  this notice
- Acceleration measures were implemented — retrieve evidence of
  additional resources or extended hours

**Only flag constructive acceleration if all three conditions are
evidenced in retrieved documents.** If the evidence is partial:
state which conditions are evidenced and which are not.

---

## Classification and decision rules

**Entitlement basis:**

Disruption events qualify under retrieved amendment document
entitlement provision → ENTITLEMENT BASIS CONFIRMED — proceed
with methodology and quantum
Disruption events do not qualify under retrieved provision →
OUT OF SCOPE under retrieved provision — flag
Amendment document not retrieved → CANNOT CONFIRM ENTITLEMENT BASIS

**Causation:**

Causal link between employer event and productivity loss evidenced
in retrieved documents → CAUSATION EVIDENCED FROM RETRIEVED DOCUMENTS
Productivity reduction present but causal link not evidenced →
CAUSATION NOT ESTABLISHED FROM RETRIEVED DOCUMENTS — flag
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
warehouse → LAST RESORT METHODOLOGY — flag the limitation

**Constructive acceleration:**

All three conditions evidenced in retrieved documents →
POSSIBLE CONSTRUCTIVE ACCELERATION — flag; state the conditions
evidenced
Partial conditions only → INSUFFICIENT EVIDENCE FROM RETRIEVED
DOCUMENTS — state what is evidenced

---

## When to call tools

**Signal:** Disruption claim references employer instructions or
correspondence as the cause but these have not been retrieved
**Action:** `search_chunks` with query "[instruction or correspondence
reference] [date range]"; `get_related_documents` with document types
"Engineer's Instruction", "RFI", "Variation Order"
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
**Action:** `search_chunks` with query "productivity factor inefficiency
study table"
**Look for:** The specific study reference and the factors applied

**Signal:** Constructive acceleration suspected — time extension
claimed but no response retrieved
**Action:** `get_related_documents` with document type "Determination";
`search_chunks` with query "time extension response [claim reference]"
**Look for:** Whether the time extension was responded to and any
acceleration notice

---

## Always flag — regardless of query

1. **No contemporaneous records retrieved** — state that the
   disruption claim cannot be independently verified from warehouse
   documents.

2. **Global disruption where measured mile was feasible from
   retrieved records** — state the available records and the
   methodology weakness.

3. **Industry study factors applied without project-specific
   adjustment** — state this limitation from the retrieved claim
   document.

4. **Causation not established for a material head from retrieved
   documents** — state what evidence would be required.

5. **Possible constructive acceleration evidenced in retrieved
   documents** — state the conditions evidenced and their implication.

6. **Governing standard not retrieved from Layer 2b** — flag when
   the entitlement provisions could not be retrieved; state what
   standard would need to be ingested.

---

## Output format

```
## Disruption Assessment

### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [standard form name — or NOT RETRIEVED]
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
[State whether the entitlement provision and SCL Protocol were
retrieved from Layer 2b. If not: state CANNOT CONFIRM —
STANDARD FORM NOT IN WAREHOUSE and list which analysis steps
are affected.]

### Notice Position
[From notice_compliance findings — time bar caveat if applicable]

### Entitlement Basis
Standard form: [from orchestrator findings]
Entitlement provision: [from retrieved amendment document / CANNOT CONFIRM]
Cost recoverable: [YES — provision / NO / CANNOT CONFIRM]
Profit recoverable: [YES / NO — cost only / CANNOT CONFIRM]

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
Time extension claimed and denied/not responded to: [YES — source / NO / CANNOT CONFIRM]
Acceleration notice issued: [YES — reference / NOT FOUND]
Acceleration measures evidenced: [YES — source / NOT FOUND]
Assessment: [POSSIBLE CONSTRUCTIVE ACCELERATION — conditions evidenced /
INSUFFICIENT EVIDENCE FROM RETRIEVED DOCUMENTS / NOT APPLICABLE]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
*(Confidence scale: GREEN = all required evidence retrieved and findings fully supported | AMBER = Layer 2b not retrieved or amendment position unknown -- findings provisional | RED = critical document absent -- findings materially constrained | GREY = standard form unconfirmed -- form-specific analysis suspended. Full definition: skills/c1-skill-authoring/references/grounding_protocol.md)*
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
are treated with caution and require the contractor to demonstrate
it was impossible to link individual causes to individual effects.
Industry study factors are corroborating evidence only — not a
substitute for project-specific records. Retrieve the Protocol
from Layer 2b to apply these principles.

**Measured mile requirements — analytical reference:**
The baseline must be genuinely undisrupted — excluding learning
curve, mobilisation, weather, or contractor inefficiency periods.
The comparison must be like-for-like — same trade, same work type,
comparable conditions. The productivity metric must be consistent
and objectively measurable. Both baseline and disrupted period records
must be retrieved before the measured mile can be verified.

**Industry productivity studies — analytical reference:**
Industry studies provide productivity impact factors for common
disruption causes (stacking of trades, overtime, changes, etc.).
These studies are based on data from particular markets and conditions.
Application without project-specific adjustment may face challenge.
Identify the specific study from the retrieved claim documents and
assess whether any adjustment is documented.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies to
any contract form. All characterisations grounded in retrieved warehouse
documents only.*
