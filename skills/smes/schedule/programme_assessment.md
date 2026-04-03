# Programme Assessment

**Skill type:** Mixed
- Contract-type-specific: the programme submission period, acceptance
  mechanism, and required content differ by FIDIC book and edition;
  the contract administrator who accepts or approves differs by book
- Contract-type-agnostic: the assessment of programme logic integrity,
  completeness, and adequacy as a contractual baseline applies
  regardless of book type
**Layer dependency:**
- Layer 1 — project documents: baseline programme (P6 or equivalent);
  programme narrative or method statement; Particular Conditions and
  Contract Data (programme clause, submission period, required
  content); Engineer's acceptance or response letter; revised
  programme submissions; progress reports
- Layer 2 — reference standards: FIDIC programme clause (Clause 8.3
  for 1999 / Clause 8.3 for 2017) for the confirmed book and edition;
  SCL Protocol 2nd Edition 2017 (programme record-keeping principles)
**Domain:** Schedule & Programme SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when a query concerns the contractual status of the baseline
programme, whether the programme was properly submitted and accepted,
whether it constitutes a valid baseline for EOT analysis, or whether
a revised or recovery programme has been submitted and accepted.
Apply at the start of any schedule-related analysis — programme
assessment is foundational to all subsequent delay analysis.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings first.

From the invoking orchestrator extract:
- Confirmed FIDIC book and edition
- Programme submission requirements as confirmed from retrieved
  Particular Conditions and Contract Data
- Contract administrator identity (Engineer or Employer's
  Representative)

**If book type is UNCONFIRMED:** Proceed with programme retrieval
and assessment but flag that the acceptance mechanism and submission
requirements cannot be confirmed. Acceptance/approval classification
will be CANNOT CONFIRM.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The baseline programme document (P6 export, Excel, or PDF)
- The programme narrative or method statement (if separate)
- The Particular Conditions — programme clause and any specific
  programme requirements
- The Contract Data — programme submission period, required content,
  required level of detail
- The Engineer's or Employer's Representative's response to the
  programme submission (acceptance, no objection, rejection, or
  comments)
- Any revised programme submissions and their responses
- Monthly progress reports — programme update sections
- Any recovery programme submission

**If the Particular Conditions are not retrieved:**
State CANNOT CONFIRM the programme submission requirements, the
required content, or the prescribed submission period. Do not apply
any standard form requirement without confirmation.

**If the baseline programme document is not retrieved:**
State CANNOT ASSESS programme adequacy. Call tools to search before
concluding. If not found: flag the absence as a critical gap —
all subsequent delay analysis is affected.

**If no Engineer acceptance or response letter is retrieved:**
State CANNOT CONFIRM the formal status of the programme (accepted,
not accepted, or not objected to). Note the distinction between
formal acceptance and absence of objection.

### Layer 2 documents to retrieve (reference standards)

Call `search_chunks` to retrieve from Layer 2:
- FIDIC Clause 8.3 for the confirmed book and edition — the programme
  submission clause
- SCL Protocol 2nd Edition 2017 guidance on programme records and
  baseline establishment

**Purpose:** To establish what the standard FIDIC clause requires
so that Particular Conditions amendments can be assessed against it.
The requirements to apply are always those in the retrieved
Particular Conditions — Layer 2 is the comparison baseline only.

---

## Analysis workflow

### Step 1 — Confirm programme submission requirements
*Contract-type-specific*

From the retrieved Particular Conditions and Contract Data:
- What is the required submission period? (Extract from Contract
  Data — do not apply any standard form default.)
- What level of detail is required? (Activity level, resource
  loading, critical path visibility, method statements.)
- Is a specific software format required? (P6, Microsoft Project,
  other — extract from contract documents.)
- Is the programme required to be resource-loaded?

**Do not apply any programme requirement without extracting it from
the retrieved Particular Conditions or Contract Data.** If these
documents have not been retrieved: state CANNOT CONFIRM programme
requirements.

### Step 2 — Confirm the acceptance mechanism
*Contract-type-specific*

From the confirmed book type and the retrieved Particular Conditions:

**Red Book / Yellow Book:**
The Engineer reviews and either accepts or gives notice that the
programme does not comply with the contract. Under FIDIC, failure
to accept is not the same as rejection — the Engineer must give
a notice of non-compliance. A programme submitted and not objected
to within the response period may be treated as accepted. Confirm
the response period from the retrieved Contract Data.

**Silver Book:**
The Employer's Representative reviews and approves. There is no
Engineer. The approval mechanism is as stated in the retrieved
Particular Conditions.

**If the acceptance mechanism cannot be confirmed from retrieved
documents:** State CANNOT CONFIRM the formal acceptance position.

### Step 3 — Assess submission compliance
*Contract-type-agnostic*

From the retrieved documents:
- Was the programme submitted? State the submission date from the
  retrieved programme or covering letter.
- Was it submitted within the required period? Compare against the
  period extracted from the retrieved Contract Data. If the period
  has not been confirmed: state CANNOT ASSESS submission timeliness.
- What format was it submitted in? State from the retrieved documents.

### Step 4 — Assess programme content and logic
*Contract-type-agnostic*

From the retrieved programme document, assess:

**(a) Contractual completion date:**
Does the programme show the contractual completion date as confirmed
from the retrieved Contract Data? If the dates differ: flag the
contradiction and state both values with their sources.

**(b) Critical path:**
Is a critical path visible in the retrieved programme? Does the
programme identify the activities that determine the completion date?
If the critical path cannot be identified from the retrieved document:
state CANNOT IDENTIFY CRITICAL PATH from the retrieved programme.

**(c) Logic integrity:**
Are there activities with no successors (open ends)? Are there
activities with no predecessors? Do the logical relationships appear
reasonable for the scope of work? State findings from the retrieved
document only.

**(d) Resource loading:**
If required by the retrieved Contract Data: is the programme
resource-loaded? State from the retrieved document.

**(e) Method of working:**
Does the programme reflect a logical construction sequence? Are
major work sequences represented? State from the retrieved document.

**(f) GCC-specific programme requirements:**
From the retrieved documents, identify:
- Are non-working periods for UAE summer restrictions (if UAE
  project), Ramadan, or public holidays shown in the programme?
- Are authority inspection hold points reflected as constraints?
These are programme completeness checks — assess only from what
the retrieved documents show.

### Step 5 — Assess the Engineer's or Employer's Representative's response
*Contract-type-specific*

From the retrieved response letter:
- Was the programme formally accepted / approved?
- Was a no-objection issued (different from acceptance)?
- Was the programme rejected or returned with comments?
- Was no response issued within the prescribed period?

**Classify the formal status only from the retrieved response letter.**
If no response has been retrieved: state CANNOT CONFIRM formal
acceptance status.

The distinction matters: a formally accepted programme constitutes
the contractual baseline. A programme not objected to within the
prescribed period may be deemed accepted under some FIDIC
interpretations — confirm from the retrieved Particular Conditions
whether a deemed acceptance mechanism exists.

### Step 6 — Assess revised and recovery programmes
*Contract-type-agnostic*

From the retrieved documents:
- Have revised programmes been submitted? State submission dates
  and scope of revision.
- Have recovery programmes been submitted? What does the recovery
  programme state about planned completion?
- Have revised/recovery programmes been formally accepted?

Assess each submission using the same framework as Steps 3–5.

---

## Classification and decision rules

**Programme submission:**
Submitted within confirmed period → TIMELY SUBMISSION
Submitted outside confirmed period → LATE SUBMISSION — flag
Period not confirmed from retrieved Contract Data →
CANNOT ASSESS TIMELINESS

**Formal status:**
Formal acceptance letter retrieved → FORMALLY ACCEPTED —
state date and source
No-objection letter retrieved → NO OBJECTION ISSUED — note
distinction from formal acceptance
Rejection or comments letter retrieved → NOT ACCEPTED —
state reasons from retrieved letter
No response retrieved after searching → CANNOT CONFIRM FORMAL
STATUS — flag; note the forensic implication for EOT analysis
Deemed acceptance mechanism in retrieved PC and period elapsed →
POTENTIALLY DEEMED ACCEPTED — flag; state the mechanism and source

**Programme as contractual baseline:**
Formally accepted / deemed accepted → VALID CONTRACTUAL BASELINE
— proceed with confidence in delay analysis
No objection issued → ARGUABLE BASELINE — flag; note that formal
acceptance and no-objection are treated differently in proceedings
Not formally accepted → DISPUTED BASELINE — flag immediately;
state the forensic implication for any EOT analysis that relies
on this programme
Cannot confirm status → CANNOT CONFIRM BASELINE STATUS

**Critical path:**
Identifiable from retrieved programme → CRITICAL PATH IDENTIFIED
Not identifiable → CRITICAL PATH NOT IDENTIFIABLE FROM RETRIEVED
PROGRAMME — flag; state the impact on delay analysis

---

## When to call tools

**Signal:** Baseline programme not retrieved in initial retrieval
**Action:** `search_chunks` with query "baseline programme P6
master programme schedule"; `get_related_documents` with document
type "Baseline Programme", "Master Programme"
**Look for:** The programme document — any format

**Signal:** Programme submission period not in retrieved Contract Data
**Action:** `get_document` on the Contract Data document ID;
`search_chunks` with query "programme submission period weeks days
clause 8"
**Look for:** The programme clause and any prescribed submission period

**Signal:** Engineer response or acceptance letter not retrieved
**Action:** `get_related_documents` with document type "Engineer's
Response", "Engineer's Letter"; `search_chunks` with query
"programme accepted approved no objection Engineer response"
**Look for:** The Engineer's formal response to the programme submission

**Signal:** Layer 2 FIDIC Clause 8.3 not retrieved
**Action:** `search_chunks` with query "[FIDIC book] [edition]
clause 8.3 programme submission"
**Look for:** Standard FIDIC programme clause for the confirmed book

---

## Always flag — regardless of query

1. **Baseline programme not found in the warehouse** — flag
   immediately; state that all delay analysis is affected.

2. **Programme not formally accepted or acceptance status
   unconfirmed** — flag; state the forensic implication: EOT
   analysis relying on an unaccepted programme as the baseline
   is vulnerable to challenge.

3. **Programme does not show the contractual completion date** —
   flag the discrepancy between the programme completion date and
   the Contract Data date; state both values and sources.

4. **Critical path not identifiable from the retrieved programme**
   — flag; state that the critical path cannot be assessed for
   delay analysis purposes.

5. **GCC-specific: UAE summer restrictions, Ramadan, or authority
   hold points not reflected in retrieved programme** — flag as a
   programme deficiency where the project location and scope make
   these relevant; state the forensic implication for duration and
   productivity assumptions.

---

## Output format

```
## Programme Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2 Reference Retrieved
[State whether FIDIC Clause 8.3 and SCL Protocol were retrieved.
If not: state analytical knowledge applied.]

### Programme Submission Requirements (this project)
Submission period: [from retrieved Contract Data / CANNOT CONFIRM]
Required content: [from retrieved PC or Contract Data / CANNOT CONFIRM]
Software format required: [from retrieved documents / CANNOT CONFIRM]
Resource loading required: [from retrieved documents / CANNOT CONFIRM]
Source: [document reference]

### Baseline Programme
Document retrieved: [YES — reference and date / NOT FOUND IN WAREHOUSE]
Submission date: [from retrieved document / CANNOT CONFIRM]
Submission timeliness: [TIMELY / LATE / CANNOT ASSESS — period not confirmed]
Format: [P6 / Excel / PDF / other — from retrieved document]

### Formal Status
Contract administrator response retrieved: [YES — reference / NOT FOUND]
Classification: [FORMALLY ACCEPTED / NO OBJECTION / NOT ACCEPTED /
POTENTIALLY DEEMED ACCEPTED / CANNOT CONFIRM FORMAL STATUS]
Source: [response letter reference and date]
Forensic implication: [one sentence on the baseline status]

### Programme Content Assessment
Contractual completion date shown: [YES — matches Contract Data /
YES — CONFLICTS with Contract Data — state both values /
NOT IDENTIFIABLE / CANNOT ASSESS — programme not retrieved]
Critical path identifiable: [YES / NOT IDENTIFIABLE / CANNOT ASSESS]
Logic integrity: [ACCEPTABLE / ISSUES — describe / CANNOT ASSESS]
Resource loading: [PRESENT / ABSENT — required by contract /
NOT REQUIRED / CANNOT CONFIRM REQUIREMENT]
GCC-specific non-working periods: [REFLECTED / NOT REFLECTED —
describe gap / NOT APPLICABLE / CANNOT ASSESS]

### Revised / Recovery Programmes
[For each, if retrieved:]
Submission date: [date]
Scope of revision: [from retrieved document]
Formal status: [ACCEPTED / NOT ACCEPTED / CANNOT CONFIRM]
Source: [document reference]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any requirement, period, or standard
from this section without first confirming it from retrieved project
documents.*

**FIDIC Clause 8.3 — structural summary (analytical reference):**
FIDIC Clause 8.3 (all books, both editions) requires the Contractor
to submit a programme within the period stated in the Contract Data.
The programme must show the order and timing of operations, major
stages, the methods intended, and the sequence of inspections and
tests. The Engineer (Red/Yellow) or Employer's Representative
(Silver) reviews the programme and either accepts it or gives notice
that it fails to comply. The submission period and required content
are in the Contract Data — retrieve from Layer 1. The standard form
details are the analytical reference only.

**Acceptance vs no objection — analytical reference:**
Under FIDIC, the Engineer accepts the programme or gives notice of
non-compliance. A programme not responded to within the prescribed
period may be deemed accepted under some interpretations — the
Particular Conditions may provide expressly for this. A no-objection
letter is not the same as formal acceptance and its status as a
contractual baseline may be challenged. The formal status determines
the strength of the programme as a baseline for EOT analysis.

**GCC programme requirements — analytical reference:**
Abu Dhabi ADGCC contracts have specific programme requirements
that may differ from the standard FIDIC Clause 8.3. Saudi
government contracts and Qatar Ashghal contracts have their own
programme submission requirements. Always extract requirements
from the retrieved Particular Conditions and Contract Data.
