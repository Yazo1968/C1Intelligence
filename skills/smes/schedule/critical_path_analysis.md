# Critical Path Analysis

**Skill type:** Contract-type-agnostic
The methodology for identifying and assessing the critical path
applies regardless of FIDIC book or edition. The contractual
significance of the critical path (in EOT entitlement, float
ownership, and LD enforcement) is book-specific and must be
confirmed from retrieved Particular Conditions.
**Layer dependency:**
- Layer 1 — project documents: baseline programme (CPM network);
  programme updates; as-built programme; Particular Conditions
  (float ownership clause if any); Contract Data; progress reports
  and site records (to verify actual critical path performance)
- Layer 2 — reference standards: SCL Protocol 2nd Edition 2017
  (float and critical path principles); AACE RP 29R-03 (schedule
  analysis methodology)
**Domain:** Schedule & Programme SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when a query requires identification of the critical path,
assessment of float consumption, assessment of whether a delay
event affected the critical path, or analysis of whether a claimed
EOT is supported by demonstrated critical path impact. Apply as
a supporting analysis within delay_identification and
eot_quantification assessments.

---

## Before you begin

### Foundational requirements

Read programme_assessment findings first.

From programme_assessment extract:
- Whether a baseline programme was retrieved and its formal status
- Whether the critical path was identifiable from the retrieved
  programme
- Whether the programme was formally accepted

**If the baseline programme was NOT retrieved or the critical path
was NOT identifiable from the retrieved programme:**
State CANNOT PERFORM critical path analysis. Do not proceed.
Flag the dependency on programme_assessment.

From the invoking orchestrator extract:
- Confirmed FIDIC book and edition
- Particular Conditions float ownership clause (if identified)
- Time for Completion as confirmed from retrieved Contract Data

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The baseline programme (CPM network) — if not already retrieved
  in programme_assessment
- Programme updates for the period under analysis
- As-built programme (if submitted)
- Progress reports for the period covering the claimed delay events
- Site diaries or daily reports corroborating actual progress
- The Particular Conditions — float ownership clause if any

**If no CPM programme has been retrieved:**
State CANNOT ASSESS the critical path. A critical path analysis
requires a CPM network — a bar chart programme without logical
links cannot be used for critical path analysis. Flag this.

**If programme updates for the delay period have not been retrieved:**
State CANNOT VERIFY critical path status during the delay period.
The critical path is dynamic — it must be assessed from the
programme update current at the time of the delay event, not
from the baseline alone.

### Layer 2 documents to retrieve (reference standards)

Call `search_chunks` to retrieve from Layer 2:
- SCL Protocol 2nd Edition 2017 — float principles (Core Principle 6)
  and critical path analysis guidance
- AACE RP 29R-03 — schedule analysis methodology relevant to
  the methodology identified from the retrieved documents

**Purpose:** To apply the correct interpretive framework to float
and critical path findings. The float position in the retrieved
Particular Conditions (Layer 1) takes precedence over the SCL
Protocol default where the two conflict.

---

## Analysis workflow

### Step 1 — Establish the baseline critical path
*Contract-type-agnostic*

From the retrieved baseline programme (CPM network):
- Identify the activities on the critical path (zero or negative
  total float)
- Identify near-critical activities (total float within a threshold
  relevant to the project duration — assess from the programme)
- State the critical path sequence from start to completion
- Confirm that the critical path runs to the contractual completion
  date as confirmed from the retrieved Contract Data

**State only what is identifiable from the retrieved programme.**
If the critical path cannot be identified (bar chart only, no logic
links): state CANNOT IDENTIFY CRITICAL PATH and flag.

### Step 2 — Assess float on affected activities
*Contract-type-agnostic*

For the activities identified as relevant to the query or delay
claim, from the retrieved programme:
- State the total float and free float on each activity
- Identify whether the claimed delay event affects an activity
  with zero float (critical), positive float (non-critical), or
  negative float (already delayed)

### Step 3 — Confirm float ownership position
*Contract-type-specific*

From the retrieved Particular Conditions:
- Is there an express float ownership clause? Extract it.
- Does it allocate float to the Contractor, to the Employer, or
  treat it as a shared resource?

**The float position to apply is the one in the retrieved
Particular Conditions.** If no express float clause is found
AND the Particular Conditions have been fully retrieved: note
that no express provision was found and the shared resource
principle appears to apply — citing the PC as the source of
that finding. If the Particular Conditions have not been
retrieved: state CANNOT CONFIRM the float ownership position.

Under the SCL Protocol (Layer 2), absent express contractual
provision, float is a shared resource — neither party owns it.
Apply this only where confirmed from the retrieved PC (or the
PC has been retrieved and contains no express float clause).

### Step 4 — Assess critical path impact of the claimed delay events
*Contract-type-agnostic*

For each delay event in the claim or query context:
- Identify the activities affected from the retrieved programme
- Assess whether those activities are on the critical path at
  the time of the event — from the retrieved programme update
  current at the time of the event (not the baseline alone)
- Assess whether the event consumed float or extended the
  critical path

**Critical path impact must be demonstrated from the retrieved
programme update — not from the baseline programme alone.**
If the programme update for the relevant period has not been
retrieved: state CANNOT VERIFY critical path impact at the
time of the event from warehouse documents.

### Step 5 — Assess critical path shift
*Contract-type-agnostic*

During a project, the critical path can shift — activities that
were non-critical can become critical as float is consumed.
From the retrieved programme updates:
- Has the critical path shifted during the project?
- Which activities became critical?
- When did the shift occur?

**Assess the critical path shift only from the retrieved programme
updates.** If updates are not in the warehouse for the relevant
period: state CANNOT ASSESS critical path shift from retrieved
documents.

### Step 6 — Assess concurrent critical path events
*Contract-type-agnostic*

Where multiple delay events affect the critical path in the same
period:
- Identify all concurrent events from the retrieved documents
- Identify which events are Employer-caused and which are
  Contractor-caused (from the retrieved claim documents and
  site records)
- State the concurrent period and the overlapping events

**Do not classify events as Employer-caused or Contractor-caused
without retrieved evidence for each event.** If the causation
of a concurrent event cannot be confirmed from retrieved
documents: state CANNOT CONFIRM causation for [event] from
retrieved documents.

---

## Classification and decision rules

**Critical path impact:**

Delay event affects a critical path activity confirmed from
retrieved programme update → CRITICAL PATH IMPACT DEMONSTRATED
— proceed with EOT entitlement assessment

Delay event affects non-critical activity with available float →
NO CRITICAL PATH IMPACT AT EVENT DATE — float absorbed but no
EOT entitlement unless float is subsequently exhausted

Delay event affects non-critical activity AND float is
subsequently exhausted in the retrieved programme updates →
CRITICAL PATH IMPACT AFTER FLOAT EXHAUSTION — flag; state when
the activity became critical and the float exhaustion date

Critical path impact cannot be verified (programme update not
retrieved for the delay period) →
CANNOT VERIFY CRITICAL PATH IMPACT FROM WAREHOUSE DOCUMENTS

**Float ownership:**

Express clause in retrieved PC allocating float → apply the PC
provision; state source
No express clause in retrieved PC AND PC fully retrieved →
SHARED RESOURCE PRINCIPLE APPLIES — cite PC as source of
confirmation of absence
PC not retrieved → CANNOT CONFIRM float ownership

**Concurrent delay:**

Both Employer-caused and Contractor-caused events on critical
path in same period, both evidenced in retrieved documents →
CONCURRENT DELAY IDENTIFIED — state events, period, and sources
One or more concurrent events cannot be confirmed from retrieved
documents → POSSIBLE CONCURRENT DELAY — state what is evidenced
and what cannot be confirmed

---

## When to call tools

**Signal:** Programme updates for the delay period not retrieved
**Action:** `search_chunks` with query "programme update revised
schedule [delay period dates]"; `get_related_documents` with
document type "Programme Update", "Revised Programme"
**Look for:** The programme update current at the time of the
claimed delay event

**Signal:** As-built programme not retrieved
**Action:** `get_related_documents` with document type "As-Built
Programme"; `search_chunks` with query "as-built programme actual
completion schedule"
**Look for:** The as-built programme for critical path verification

**Signal:** Float ownership clause referenced in claim or
correspondence but PC not yet retrieved
**Action:** `search_chunks` with query "float ownership Contractor
Employer particular conditions clause"; `get_document` on PC ID
**Look for:** Any express float ownership provision

**Signal:** Layer 2 SCL Protocol float principles not retrieved
**Action:** `search_chunks` with query "SCL Protocol float critical
path shared resource"
**Look for:** SCL Protocol core principle on float

---

## Always flag — regardless of query

1. **Critical path not identifiable from retrieved programme** —
   flag; state that all critical path impact assessments depend
   on this gap being resolved.

2. **Programme update not retrieved for the delay period** — flag;
   state that the critical path status at the time of the event
   cannot be confirmed from warehouse documents.

3. **Float consumed by Contractor risk events before or during the
   claimed delay period** — flag; state the float position at the
   time of the Employer delay event from retrieved programme updates.

4. **Critical path shift identified — activities not on baseline
   critical path became critical** — flag; state when the shift
   occurred and which activities are affected, from retrieved
   programme updates.

5. **Concurrent delay — multiple events on critical path in the
   same period** — flag; state the concurrent events and period
   from retrieved documents; do not resolve which party's delay
   governs without retrieved evidence.

---

## Output format

```
## Critical Path Analysis

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2 Reference Retrieved
[State whether SCL Protocol and AACE RP 29R-03 were retrieved.
If not: state analytical knowledge applied.]

### Baseline Critical Path
Baseline programme retrieved: [YES — reference / NOT FOUND — CANNOT PROCEED]
Critical path identifiable: [YES / NOT IDENTIFIABLE — CANNOT PROCEED]
Critical path activities: [list of key activities on critical path
from retrieved programme, or CANNOT IDENTIFY]
Critical path runs to contractual completion date: [YES / NO — state
discrepancy / CANNOT CONFIRM — Contract Data not retrieved]

### Float Position
Float ownership clause in retrieved PC: [YES — describe and source /
NOT FOUND IN RETRIEVED PC / CANNOT CONFIRM — PC not retrieved]
Applicable position: [PC provision / SHARED RESOURCE PRINCIPLE —
PC retrieved, no express clause / CANNOT CONFIRM]

### Critical Path Impact Assessment

[For each delay event or activity in scope:]

**[Activity / Event description]**
Programme update retrieved for this period: [YES — reference /
NOT FOUND — CANNOT VERIFY]
Activity float at event date: [value from retrieved programme update /
CANNOT CONFIRM]
Critical path status at event date: [CRITICAL / NON-CRITICAL —
float available / CANNOT CONFIRM]
Impact assessment: [CRITICAL PATH IMPACT DEMONSTRATED /
NO CRITICAL PATH IMPACT AT EVENT DATE /
CRITICAL PATH IMPACT AFTER FLOAT EXHAUSTION — date /
CANNOT VERIFY FROM WAREHOUSE DOCUMENTS]
Source documents: [list]

### Critical Path Shift
Critical path shift identified: [YES — describe / NOT EVIDENCED
IN RETRIEVED DOCUMENTS / CANNOT ASSESS — updates not retrieved]
Activities affected: [from retrieved programme updates]
Period of shift: [from retrieved documents]

### Concurrent Delay
Concurrent delay identified: [YES — period and events / NOT IDENTIFIED /
CANNOT ASSESS — causation not confirmed for one or more events]
[For each concurrent event: event description, classification
(Employer/Contractor/CANNOT CONFIRM), source document]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any float rule, methodology standard,
or critical path principle from this section without first confirming
the applicable position from retrieved project documents.*

**SCL Protocol float principles — analytical reference:**
Core Principle 6 of the SCL Protocol 2nd Edition 2017 states that
float is a shared resource — neither party is entitled to use it
to the exclusion of the other, absent express contractual provision.
A Contractor cannot claim an EOT for a period that would only
consume float. An Employer cannot use float to resist an EOT for
a genuine Employer delay event. Retrieve the Protocol from Layer 2
and check the retrieved Particular Conditions for any express float
clause before applying this principle.

**Dynamic critical path — analytical reference:**
The critical path is not static. As the project progresses and
float is consumed, non-critical activities can become critical.
A delay event that had no critical path impact at the baseline
stage may become critical later if intervening events consumed the
float. This is why the programme update current at the time of the
delay event — not the baseline — is the correct reference for
assessing critical path impact.

**Near-critical activities — analytical reference:**
Activities with low positive float are at risk of becoming critical
if delays occur. On complex projects, near-critical activities
(typically those with total float below a project-specific threshold)
require the same attention as critical activities in delay analysis.
The threshold is a matter of professional judgement applied to the
project — it is not a fixed number.
