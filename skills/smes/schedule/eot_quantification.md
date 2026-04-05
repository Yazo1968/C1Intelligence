# EOT Quantification

**Skill type:** Contract-type-specific
The time extension clause, the list of qualifying entitlement events,
and the contract administrator's authority all differ by standard form
and version. The amendment document frequently amends the entitlement
event list. No entitlement classification can be made without first
retrieving the applicable provision from the amendment document.
**Layer dependency:**
- Layer 1 — project documents: time extension claim submission; delay
  analysis report; baseline programme; as-built programme or progress
  records; amendment document (time extension clause); Contract Data
  (Time for Completion, programme submission requirements); contract
  administrator determination or response; contemporaneous site records
- Layer 2b — reference standards: time extension provision for the
  confirmed standard form and version; SCL Protocol 2nd Edition 2017
  (delay methodology framework, if ingested)
**Domain:** Delay and Cost Analytics SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when retrieved documents contain a time extension claim
submission, a delay analysis report, a notice of delay referencing a
programme impact, or a query about entitlement to additional time.
Apply when a completion certificate shows a completion date materially
later than the contractual completion date and no time extension record
has been found.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings and notice_compliance findings.

From the invoking orchestrator extract:
- Confirmed standard form and version
- Time for Completion as confirmed from retrieved Contract Data —
  if not confirmed: state CANNOT ESTABLISH the baseline for delay
  assessment
- Amendment document provisions affecting the time extension clause
  and the entitlement event list

From notice_compliance findings:
- Notice classification for this claim
- If POTENTIALLY TIME-BARRED: flag at the start of this assessment
  and note throughout that the entitlement analysis is conditional
  on the notice position being resolved

**If standard form is UNCONFIRMED:** State CANNOT ASSESS time extension
entitlement. The qualifying events and time extension clause differ by
standard form — analysis without a confirmed standard form is not
possible.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The time extension claim submission
- The delay analysis report (if a separate document)
- The amendment document — specifically the time extension clause
  and entitlement event list
- The Contract Data — Time for Completion, programme submission
  requirements
- The baseline programme — the programme accepted or approved by the
  contract administrator
- The as-built programme or monthly progress reports covering the
  delay period
- Site diaries and contemporaneous records for the claimed delay events
- The contract administrator determination or response (if any)

**If the amendment document is not retrieved:**
State CANNOT CONFIRM the time extension clause or the qualifying event
list. Do not classify any event as an employer risk event, neutral
event, or contractor risk event. Entitlement classification requires
the retrieved amendment document.

**If the baseline programme is not retrieved:**
State CANNOT VERIFY the delay analysis. A delay analysis without
a baseline programme cannot be independently assessed. Flag this
immediately.

**If no time extension claim document is retrieved:**
State CANNOT ASSESS — no time extension claim found in the warehouse.

### Layer 2b documents to retrieve (reference standards)

After confirming standard form, call `search_chunks` with
`layer_type = '2b'` to retrieve:
- The time extension clause for the confirmed standard form
  (search by subject matter: "time extension entitlement employer
  risk event programme delay")
- SCL Protocol 2nd Edition 2017 guidance on delay methodology
  (if available in Layer 2b)

**Purpose:** The Layer 2b time extension clause establishes the
standard form qualifying events. The amendment document then amends
that list — events may be added, removed, or qualified. The
entitlement event list to apply is always the amendment document
version. Layer 2b provides the comparison baseline only.

**If the governing standard form is not retrieved from Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE for the
time extension provisions. Do not describe the qualifying events
from training knowledge.

---

## Analysis workflow

### Step 1 — Retrieve and identify all time extension claim documents
*Contract-type-agnostic*

Call `get_related_documents` with document type "EOT Claim" or
"Time Extension Claim".
Call `get_related_documents` with document type "Delay Analysis Report".
Call `search_chunks` with query "extension of time critical path
delay programme impact".
Compile a complete list of retrieved claim and analysis documents.

### Step 2 — Confirm the time extension clause and entitlement event list
*Contract-type-specific*

From the retrieved amendment document confirm:
- Which provision governs time extensions (the amendment document
  version, as amended)
- The list of qualifying entitlement events as stated in the
  retrieved amendment document

**Do not apply the General Conditions event list without confirming
from the retrieved amendment document that it has not been amended.**
If the amendment document has not been retrieved: state CANNOT CONFIRM
the entitlement event list. Do not classify any event as qualifying
or non-qualifying.

For each delay event in the claim: identify which entitlement event
in the retrieved amendment document it corresponds to (if any). If
no corresponding event is found in the retrieved documents: flag as
ENTITLEMENT BASIS NOT CONFIRMED FROM RETRIEVED DOCUMENTS.

### Step 3 — Assess the baseline programme
*Contract-type-agnostic*

From the retrieved programme document:
- Has it been formally accepted or approved by the contract
  administrator? State the source document and date.
- Does it show the contractual completion date as confirmed from
  the retrieved Contract Data?
- Is it a CPM (Critical Path Method) network — does it show the
  critical path?
- Was it submitted within the required period? Extract the programme
  submission requirement from the retrieved Contract Data or amendment
  document — do not apply any default period.

**If the baseline programme has not been retrieved:**
State CANNOT VERIFY the delay analysis. Flag this as a critical gap.
Call tools to search before proceeding. If still not found: state
that the methodology assessment cannot proceed.

**If the programme was not formally accepted or approved:**
State this from the retrieved documents. Flag and state what was
retrieved.

### Step 4 — Assess as-built records
*Contract-type-agnostic*

From the retrieved progress reports, site diaries, and as-built
programme (if available), assess:
- Are the claimed delay events evidenced in contemporaneous records?
- Do the contemporaneous records correspond to the delay periods
  stated in the claim?

**Do not characterise a delay event as established unless it is
evidenced in retrieved contemporaneous records.** If the delay
events are described only in the claim submission and not in any
contemporaneous record: state this and flag the evidential gap.

### Step 5 — Assess the delay analysis methodology
*Contract-type-agnostic*

Identify the methodology used from the retrieved analysis document.
Do not assume a methodology — identify it from what the retrieved
documents describe.

For the identified methodology, assess from the retrieved documents:
- What data does the methodology require?
- Is that data present in the warehouse?
- Does the methodology produce a result that can be independently
  verified from retrieved records?

**Assessment by methodology type — apply only to the methodology
identified from retrieved documents:**

Time Impact Analysis (TIA): requires programme updates at regular
intervals and fragnets for each delay event. From retrieved documents:
verify the fragnet represents the actual event; verify the programme
update is current at the time of the event; verify the critical path
impact is calculated from the insertion point forward.

Windows Analysis: requires programme updates across defined time
windows. From retrieved documents: verify window boundaries are
logical; verify concurrent delay is addressed within each window.

Collapsed As-Built: requires as-built programme and defined delay
events. From retrieved documents: verify the as-built programme is
based on contemporaneous records; verify the delay events removed
are correctly characterised.

As-Planned vs As-Built: requires baseline programme and as-built
records. Flag if used on a project with multiple concurrent delay
events — this methodology cannot isolate causation in that context.

Impacted As-Planned: requires baseline programme only — does not
use as-built records. Flag this methodology on any complex project.
State that it does not account for actual performance.

**If the methodology cannot be identified from retrieved documents:**
State CANNOT IDENTIFY METHODOLOGY.

### Step 6 — Assess concurrent delay
*Contract-type-agnostic*

From the retrieved records, assess whether any contractor-caused delay
events overlap with the claimed employer-caused delay events on the
critical path during the same period.

**Only assess concurrent delay that is evidenced in retrieved
documents.** Do not introduce concurrent delay scenarios not supported
by retrieved records.

If concurrent delay is evidenced: state the period affected and the
overlapping events from retrieved documents. Retrieve the SCL Protocol
from Layer 2b to confirm the applicable concurrent delay principle —
state the principle from the retrieved Protocol. Do not apply a
concurrent delay methodology without retrieved Layer 2b confirmation.

If the claim does not address concurrent delay but the retrieved
records indicate it: flag this as a gap in the claim.

### Step 7 — Assess float
*Contract-type-agnostic*

From the retrieved programme:
- Does the baseline programme show float on the activities affected
  by the claimed delay events?
- Has the claim correctly treated float?
- Does the retrieved amendment document contain an express float
  ownership clause? If so: extract from retrieved documents and apply.

**Do not apply any float position without retrieving the amendment
document float clause (if any).** If no express float clause is found
in the retrieved amendment document AND it has been fully retrieved:
note that no express provision was found — citing the amendment document
as source.

### Step 8 — Assess the claimed time extension quantum
*Contract-type-agnostic*

Compare the claimed time extension days against the delay demonstrated
in the retrieved analysis documents.

**State only what the retrieved analysis shows.** If the analysis
does not demonstrate the full claimed quantum: state the gap between
demonstrated impact and claimed days. Do not calculate an alternative
quantum — flag the difference and state what additional evidence would
be needed.

### Step 9 — Assess the contract administrator's response
*Contract-type-specific*

From the retrieved determination or response:
- What position has the contract administrator taken?
- What was awarded (if any)?
- What reasons were given for reduction or rejection?

If no determination has been retrieved after searching:
State CANNOT ASSESS the contract administrator's position.

---

## Classification and decision rules

**Entitlement event:**

Event corresponds to a qualifying event in the retrieved amendment
document → IN SCOPE — proceed with proof and methodology assessment
Event does not correspond to any qualifying event in retrieved
amendment document → OUT OF SCOPE — flag; state the specific
provision that excludes it
Amendment document not retrieved → CANNOT CLASSIFY the event

**Critical path impact:**

Impact on critical path demonstrated in retrieved analysis →
CRITICAL PATH IMPACT DEMONSTRATED — proceed with quantum assessment
Impact on non-critical activities only → NO TIME EXTENSION ENTITLEMENT
for this event unless float is exhausted — flag
Critical path not demonstrated in retrieved analysis →
CRITICAL PATH NOT ESTABLISHED — flag

**Baseline programme:**

Programme retrieved, accepted/approved, CPM-based → VALID BASELINE
Programme retrieved but not accepted/approved → DISPUTED BASELINE —
flag
Programme not retrieved → CANNOT VERIFY — flag immediately

**Methodology:**

Identified from retrieved documents and data requirements met →
state methodology and assessment
Data requirements not met → METHODOLOGY CANNOT BE VERIFIED FROM
WAREHOUSE DOCUMENTS — flag

---

## When to call tools

**Signal:** Claim references delay events but no contemporaneous
records for those events retrieved
**Action:** `search_chunks` with query "[event description]
[date range]"; `get_related_documents` with document types "Site
Diary", "Daily Report" for the relevant period
**Look for:** Contemporaneous records evidencing the event

**Signal:** Claim references a programme revision but only the
baseline has been retrieved
**Action:** `get_related_documents` with document types "Revised
Programme", "Programme Update"
**Look for:** Programme updates referenced in the analysis

**Signal:** Contract administrator determination referenced but not
retrieved
**Action:** `get_related_documents` with document type "Determination";
`search_chunks` with query "time extension determination awarded"
**Look for:** The determination and any awarded time extension

**Signal:** Amendment document not retrieved — entitlement event list
cannot be confirmed
**Action:** `search_chunks` with query "particular conditions time
extension entitlement events"; `get_document` on the amendment
document ID if known
**Look for:** Amendment to the time extension clause and entitlement
events

**Signal:** Layer 2b time extension clause not retrieved
**Action:** `search_chunks` with `layer_type = '2b'` and query
"[standard form name] time extension entitlement employer risk"
**Look for:** Standard form time extension clause

---

## Always flag — regardless of query

1. **Notice time bar caveat** — if notice_compliance shows POTENTIALLY
   TIME-BARRED: state that the procedural gateway may not be satisfied
   and entitlement analysis is conditional.

2. **Baseline programme absent or not formally accepted** — flag
   immediately; state that the delay analysis cannot be independently
   verified.

3. **Concurrent delay evidenced in retrieved records but not addressed
   in the claim** — flag; state the period and overlapping events.

4. **Claimed time extension exceeds demonstrated critical path impact**
   — flag the gap; state demonstrated and claimed quantum.

5. **Methodology not supported by available records** — flag; state
   which required data is absent.

6. **Entitlement event list not confirmed from amendment document** —
   flag; state that event classification cannot be made.

7. **Governing standard not retrieved from Layer 2b** — flag when
   the time extension provisions could not be retrieved; state what
   standard would need to be ingested.

---

## Output format

```
## EOT Quantification Assessment

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
[State whether the time extension provision and SCL Protocol were
retrieved from Layer 2b. If not: state CANNOT CONFIRM —
STANDARD FORM NOT IN WAREHOUSE and list which analysis steps
are affected.]

### Notice Position
[From notice_compliance findings — time bar caveat if applicable]

### Contract Basis
Standard form: [from orchestrator findings]
Time extension provision: [from retrieved amendment document / CANNOT CONFIRM]
Time for Completion: [from retrieved Contract Data / CANNOT CONFIRM]
Contractual completion date: [from retrieved documents / CANNOT CONFIRM]
Amendment document amendments to time extension clause: [list or NONE FOUND /
CANNOT CONFIRM]

### Baseline Programme
Status: [RETRIEVED — accepted/approved / RETRIEVED — not accepted /
NOT FOUND IN WAREHOUSE]
CPM-based: [YES / NO / CANNOT DETERMINE]
Source: [document reference]
Analysis gate: [PROCEED / CANNOT VERIFY — baseline not retrieved]

### Delay Event Register

| # | Event | Provision in retrieved documents | Event type | CP impact | Concurrent delay | EOT claimed | Supportable |
|---|---|---|---|---|---|---|---|
| 1 | [description] | [provision or NOT CONFIRMED] | [ER/Neutral/CR/CANNOT CLASSIFY] | [YES/NO/PARTIAL] | [YES/NO/NOT ASSESSED] | [days] | [YES/PARTIAL/NO/CANNOT ASSESS] |

### Findings by Delay Event

**[Event description]**
Entitlement provision: [from retrieved amendment document / CANNOT CONFIRM]
Event classification: [Employer Risk / Neutral / Contractor Risk /
CANNOT CLASSIFY — amendment document not retrieved]
Notice status: [from notice_compliance findings]
Critical path impact: [demonstrated / not demonstrated / not assessed]
Concurrent delay: [identified — period and events / not evidenced in
retrieved records]
Float position: [from retrieved programme / not assessable]
Time extension claimed: [days]
Time extension supportable from retrieved documents: [days / CANNOT ASSESS]
Methodology: [identified name and assessment / CANNOT IDENTIFY]
Contemporaneous records: [PRESENT — list / PARTIAL — gaps noted / ABSENT]
Source documents: [list with references]
Finding: [from retrieved documents only]

### Methodology Assessment
Methodology identified: [name / CANNOT IDENTIFY]
Data requirements: [MET / PARTIALLY MET — gaps / NOT MET]
SCL Protocol assessment: [from retrieved Layer 2b / CANNOT ASSESS —
Protocol not retrieved]
Finding: [from retrieved documents only]

### Contract Administrator Position
Determination retrieved: [YES / NO — NOT FOUND IN WAREHOUSE]
Time extension awarded: [days / NOT FOUND]
Reasons for reduction/rejection: [from retrieved determination / NOT FOUND]
Source: [document reference]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
*(Confidence scale: GREEN = all required evidence retrieved and findings fully supported | AMBER = Layer 2b not retrieved or amendment position unknown -- findings provisional | RED = critical document absent -- findings materially constrained | GREY = standard form unconfirmed -- form-specific analysis suspended. Full definition: skills/c1-skill-authoring/references/grounding_protocol.md)*
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any classification, methodology
standard, or entitlement position from this section without first
confirming the applicable terms from retrieved project documents.*

**Time extension clause structure — analytical reference:**
Standard forms of contract list qualifying events that entitle the
contractor to a time extension. The list differs between standard
forms — some forms allocate more risk to the employer; others place
more risk on the contractor. The actual qualifying events for any
project are the events in the retrieved amendment document — retrieve
from Layer 2b for the standard text and from Layer 1 for the
project-specific version.

**SCL Protocol 2017 — analytical reference:**
The SCL Protocol is a widely referenced framework for delay
methodology assessment. Core principles: contemporaneous records
are the evidential foundation; prospective analysis is more reliable
than retrospective; concurrent delay must be addressed; float is a
shared resource absent express contractual agreement. Retrieve from
Layer 2b to apply these principles to the retrieved analysis.

**Delay methodology hierarchy — analytical reference:**
TIA and Windows Analysis are generally the most defensible
methodologies. Collapsed As-Built and As-Planned vs As-Built are
acceptable for simpler projects. Impacted As-Planned is the least
defensible — it models delay theoretically without reference to
as-built records. These assessments apply to the methodology
identified from the retrieved documents.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies to
any contract form. All characterisations grounded in retrieved warehouse
documents only.*
