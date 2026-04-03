# Site Execution

**Skill type:** Contract-type-agnostic
The review of site diaries, daily reports, method statements, work
permits, inspection records, and resource reports to establish the
factual record of site execution applies regardless of standard form
or version. The contractual consequences of deviations from approved
methods, access restrictions, or resource shortfalls are assessed
against the retrieved amendment document provisions and the governing
standard form retrieved from Layer 2b.
**Layer dependency:**
- Layer 1 — project documents: site diaries and daily construction
  reports; method statements (submitted and approved versions); work
  permits; daily resource reports (manpower, plant); progress
  photographs; access records; weather records; amendment document
  (relevant clauses on method, access, and resources)
- Layer 2b — reference standards: contractor general obligations
  provisions for the confirmed standard form (method, resources,
  access); employer access and possession provisions (if ingested)
- Layer 2a — internal standards: site management procedures,
  health and safety frameworks (if applicable)
**Domain:** Technical & Construction SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when a query requires establishing the factual record of what
happened on site — sequence of construction, resource deployment,
access conditions, weather impact, method of working, or compliance
with approved method statements. Apply when contemporaneous site
records are needed to support or challenge a delay claim, a
disruption claim, or a quality assertion. This skill is primarily
a factual record extraction and assessment skill.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings and programme_assessment
findings where available.

From the invoking orchestrator:
- The period under analysis
- The specific query or factual question to be answered from
  the site records

From programme_assessment:
- The planned construction sequence for the period under analysis
  (to compare against the actual sequence from site records)

**This skill does not make legal or contractual conclusions.**
It extracts and presents the factual record from retrieved site
documents. Legal and contractual consequences are assessed by
the invoking orchestrator.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- Site diaries and daily construction reports for the period
  under analysis
- Method statements for the activities under assessment —
  the submitted version and the approved version
- Work permits for the relevant work types and period
- Daily resource reports (manpower, plant) for the period
- Progress photographs (dated) for the period
- Weather records for the period (if weather is relevant)
- Access records or site possession records
- The amendment document — clauses on method, access, and resources
  relevant to the query

**If site diaries are not retrieved for the relevant period:**
State CANNOT ESTABLISH the factual site record for that period
from warehouse documents. The site diary is the primary
contemporaneous record of site execution.

**For each retrieved document:** State its reference, date, and
the period it covers. Note any gaps (e.g. site diaries retrieved
for most of the period but missing for specific dates).

### Layer 2b documents to retrieve (reference standards)

Call `search_chunks` with `layer_type = '2b'` to retrieve:
- Contractor general obligations provisions for the confirmed
  standard form (search by subject matter: "contractor general
  obligations method resources programme access")
- Employer access and possession provisions for the confirmed
  standard form (search by subject matter: "employer access
  possession site contractor obligation")

**Purpose:** To establish the standard form framework for method
and resource obligations and employer access duties. Specific
requirements are in the retrieved amendment document.

**If the governing standard form is not retrieved from Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE for the
contractor obligations framework. Confidence cap: AMBER. This
skill's primary value lies in the factual record from Layer 1 —
proceed with Layer 1 analysis regardless.

---

## Analysis workflow

### Step 1 — Establish the factual sequence of construction
*Contract-type-agnostic*

From the retrieved site diaries and daily reports for the period:
- What activities were carried out each day?
- What was the actual construction sequence?
- Does the actual sequence match the planned sequence from the
  retrieved programme?

**State the actual sequence from the retrieved site diaries.**
If there are gaps in the retrieved site diaries: flag the dates
for which no record was retrieved and note that the record for
those dates cannot be established from warehouse documents.

### Step 2 — Assess method statement compliance
*Contract-type-agnostic*

From the retrieved method statement (approved version) and the
retrieved site diaries:
- Was the work executed in accordance with the approved method
  statement?
- Are there any deviations from the approved method recorded in
  the retrieved site diaries?
- Was the method statement approved before the work commenced?
  (Cross-reference the submittal register if available.)

**Flag any deviation from the approved method that is evidenced
in the retrieved site records.** Do not characterise a deviation
without a retrieved document evidencing it.

If the method statement has not been retrieved: state CANNOT
ASSESS method compliance from warehouse documents.

### Step 3 — Assess resource deployment
*Contract-type-agnostic*

From the retrieved daily resource reports and site diaries:
- What labour resources were deployed each day during the period?
  (State numbers by trade from the retrieved reports.)
- What plant resources were deployed?
- Does the resource deployment match the resource-loaded programme?
  (Cross-reference programme_assessment findings if available.)

**State resource figures from the retrieved reports.** Do not
estimate or extrapolate. If resource reports are not retrieved
for specific dates: flag the gap.

### Step 4 — Assess work permit compliance
*Contract-type-agnostic*

From the retrieved work permits:
- Were work permits in place for the relevant activities?
  (Hot work, confined space, lifting operations, excavation,
  working at height)
- Were permits issued before work commenced?
- Were there any permit violations recorded in the retrieved
  documents?

**Assess only from retrieved work permits.** If work permits
have not been retrieved: state CANNOT CONFIRM work permit
compliance from warehouse documents.

### Step 5 — Assess access and possession records
*Contract-type-agnostic*

From the retrieved access records and site diaries:
- Was the contractor given access to the areas required for the
  work on the planned dates?
- Are there records of restricted access, delayed handover of
  areas, or employer interference with the contractor's operations?

**State the access position from the retrieved records.** Do not
characterise an access restriction as an employer default without
retrieved evidence.

### Step 6 — Assess weather records
*Contract-type-agnostic*
*Apply only where weather is relevant to the query*

From the retrieved weather records or site diary entries recording
weather conditions:
- What weather conditions were recorded during the period?
- Were any stoppages due to weather recorded?
- Does the site diary record the impact of weather on specific
  activities?

**State weather conditions from the retrieved records.** Whether
conditions were sufficiently adverse to constitute a weather risk
event under the governing standard form is a contractual assessment
— flag that this requires the relevant Layer 2b provisions and
the amendment document to confirm. State the factual weather record
from retrieved documents only.

---

## Classification and decision rules

**Site diary coverage:**

Site diaries retrieved for the full period → COMPLETE RECORD
Gaps identified in retrieved site diaries → INCOMPLETE RECORD —
flag the missing dates
No site diaries retrieved → NO CONTEMPORANEOUS RECORD IN WAREHOUSE

**Method statement compliance:**

Approved method statement retrieved AND site diary shows
compliance → COMPLIANT WITH APPROVED METHOD
Approved method statement retrieved AND site diary records
deviation → DEVIATION FROM APPROVED METHOD — flag; state the
deviation and source documents
Method statement not retrieved → CANNOT ASSESS METHOD COMPLIANCE

**Resource deployment:**

Resource reports retrieved for full period → COMPLETE
Resource reports retrieved for part of period → PARTIAL —
state the covered and uncovered periods
No resource reports retrieved → CANNOT CONFIRM RESOURCE DEPLOYMENT

**Work permit compliance:**

Permits retrieved and pre-dated work commencement → COMPLIANT
Work evidenced before permit issue date → PERMIT COMPLIANCE ISSUE
— flag
Permits not retrieved → CANNOT CONFIRM WORK PERMIT COMPLIANCE

**Access:**

Site diary confirms full access on planned dates → ACCESS CONFIRMED
Site diary records restricted access or delay → ACCESS RESTRICTION
EVIDENCED — flag; state the period and source
No access records in warehouse → CANNOT CONFIRM ACCESS POSITION

---

## When to call tools

**Signal:** Site diaries not retrieved for the relevant period
**Action:** `get_related_documents` with document type "Site Diary",
"Daily Construction Report"; `search_chunks` with query "site
diary daily report [date range]"
**Look for:** Site diary entries for the specific period

**Signal:** Method statement not retrieved
**Action:** `get_related_documents` with document type "Method
Statement"; `search_chunks` with query "method statement [activity
description] approved"
**Look for:** The approved method statement for the activity

**Signal:** Daily resource reports not retrieved
**Action:** `get_related_documents` with document type "Daily
Resource Report", "Manpower Report"; `search_chunks` with query
"manpower plant resource [date range]"
**Look for:** Daily or weekly resource reports for the period

**Signal:** Weather records not retrieved but weather is relevant
**Action:** `search_chunks` with query "weather record rainfall
temperature [period]"; `get_related_documents` with document type
"Weather Record", "Meteorological Report"
**Look for:** Any weather records in the warehouse for the period

**Signal:** Layer 2b contractor obligations provisions not retrieved
**Action:** `search_chunks` with `layer_type = '2b'` and query
"[standard form name] contractor general obligations method
resources access"
**Look for:** Standard form contractor general obligations and
employer access provisions

---

## Always flag — regardless of query

1. **Gaps in site diary coverage** — flag the specific dates or
   periods for which no site diary has been retrieved; state that
   the factual record cannot be established for those periods.

2. **Deviation from approved method statement** — flag where the
   site diary records a different construction method from the
   approved method statement; state both documents.

3. **Access restriction recorded in site diary** — flag; state
   the period, the nature of the restriction, and the source
   document.

4. **Resource deployment significantly below the resource-loaded
   programme** — flag where retrieved resource reports show
   substantially fewer resources than the programme assumed; state
   the figures from both documents.

5. **Work proceeded before work permit issued** — flag where
   retrieved records show this sequence; state the work type,
   dates, and source documents.

6. **Governing standard not in Layer 2b** — flag; state that the
   contractual framework for method and access obligations cannot
   be confirmed from the warehouse; confidence capped at AMBER
   for contractual consequence assessment.

---

## Output format

```
## Site Execution Assessment

### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [standard form name — or NOT RETRIEVED]
Layer 2b provisions retrieved: [contractor obligations, employer
access and possession — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE]
Layer 2a source: [policy name — or NOT RETRIEVED / NOT APPLICABLE]
Layer 1 primary document: [site diary or daily report reference —
or NOT RETRIEVED]
Layer 1 amendment document: [name — or NOT RETRIEVED]
Provisions CANNOT CONFIRM: [list — or NONE]

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.
Note the periods covered by site diaries and any gaps.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2b Reference Retrieved
[State whether contractor obligations and employer access provisions
were retrieved from Layer 2b. If not: state CANNOT CONFIRM —
STANDARD FORM NOT IN WAREHOUSE. Note that the factual record from
Layer 1 is unaffected by this gap. Confidence cap: AMBER for
contractual consequence assessment.]

### Site Diary Coverage
Period under analysis: [dates]
Site diaries retrieved: [period covered — note gaps]
Coverage: [COMPLETE / INCOMPLETE — state gap dates / NONE RETRIEVED]

### Construction Sequence (from retrieved site diaries)
[Narrative of actual construction sequence from retrieved records,
or CANNOT ESTABLISH — site diaries not retrieved]

### Method Statement Compliance
Method statement retrieved: [YES — reference and approval date /
NOT FOUND]
Work commencement vs approval: [APPROVED BEFORE COMMENCEMENT /
WORK PRECEDED APPROVAL / CANNOT CONFIRM]
Compliance with approved method: [COMPLIANT / DEVIATION — describe
and source / CANNOT ASSESS]

### Resource Deployment (from retrieved reports)

| Period | Labour (trades and numbers) | Plant | Source |
|---|---|---|---|
| [dates] | [from retrieved reports] | [from reports] | [report references] |

Comparison to programme resource loading: [CONSISTENT / BELOW
PROGRAMME LEVELS — state figures / CANNOT COMPARE — programme
not retrieved]

### Work Permit Compliance
Work permits retrieved: [YES — list types / NOT FOUND]
Pre-work issue confirmed: [YES / ISSUE IDENTIFIED — describe /
CANNOT CONFIRM]

### Access Position
Access records retrieved: [YES — period / NOT FOUND]
Access restrictions recorded: [YES — describe and source /
NONE IN RETRIEVED RECORDS]

### Weather Records
Weather records retrieved: [YES — period / NOT FOUND]
Weather stoppages recorded: [YES — dates and duration from records /
NONE IN RETRIEVED RECORDS]
Note: Whether weather conditions constitute a contractual risk
event requires Layer 2b provisions and amendment document
confirmation — this section states the factual record only.

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — factual record from retrieved
documents only; note periods where the record is incomplete]
```

---

## Analytical framework
*Reference only — do not apply any contractual obligation or
standard from this section without first confirming it from the
retrieved project documents and Layer 2b.*

**Site diary as contemporaneous evidence — analytical reference:**
The site diary is the most important contemporaneous record in
construction dispute resolution. It records daily events, resources,
weather, visitors, instructions received, and problems encountered.
A well-maintained site diary provides the evidential foundation
for delay, disruption, and defects claims. The absence of site
diary records is itself forensically significant — it weakens
the evidential basis for any claim or defence that depends on
establishing what actually happened on site.

**Method statement compliance — analytical reference:**
The contractor is generally required to execute the works in
accordance with approved method statements. Deviations without
the contract administrator's approval may constitute a contractual
breach. They may also be evidence of acceleration (different
sequence, additional resources) or of the cause of a defect
(deviation from the specified method). The connection between
method deviation and outcome depends on the specific circumstances
evidenced in the retrieved documents and the relevant obligation
in the amendment document.

**Resource deployment and disruption — analytical reference:**
Daily resource reports, cross-referenced against the resource-loaded
programme, establish whether the contractor deployed the resources
the programme assumed. Below-programme resource deployment may
indicate contractor culpability for delay; above-programme
deployment may indicate disruption or acceleration. The forensic
significance depends on the reason for the deviation, which must
be established from the retrieved contemporaneous records.
