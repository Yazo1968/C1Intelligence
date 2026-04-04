# Programme Assessment

**Skill type:** Mixed
- Contract-type-specific: the programme submission period, acceptance
  mechanism, and required content differ by standard form and version;
  the contract administrator who accepts or approves differs by
  standard form
- Contract-type-agnostic: the assessment of programme logic integrity,
  completeness, and adequacy as a contractual baseline applies
  regardless of standard form
**Layer dependency:**
- Layer 1 — project documents: baseline programme (P6 or equivalent);
  programme narrative or method statement; amendment document and
  Contract Data (programme clause, submission period, required content);
  contract administrator acceptance or response letter; revised
  programme submissions; progress reports
- Layer 2b — reference standards: programme submission provision for
  the confirmed standard form and version (whatever is in the warehouse);
  SCL Protocol 2nd Edition 2017 (programme record-keeping principles,
  if ingested)
**Domain:** Schedule & Programme SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when a query concerns the contractual status of the baseline
programme, whether the programme was properly submitted and accepted,
whether it constitutes a valid baseline for delay analysis, or whether
a revised or recovery programme has been submitted and accepted.
Apply at the start of any schedule-related analysis — programme
assessment is foundational to all subsequent delay analysis.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings first.

From the invoking orchestrator extract:
- Confirmed standard form and version
- Programme submission requirements as confirmed from retrieved
  amendment document and Contract Data
- Contract administrator identity (from engineer_identification
  findings)

**If standard form is UNCONFIRMED:** Proceed with programme retrieval
and assessment but flag that the acceptance mechanism and submission
requirements cannot be confirmed. Acceptance/approval classification
will be CANNOT CONFIRM.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The baseline programme document (P6 export, Excel, or PDF)
- The programme narrative or method statement (if separate)
- The amendment document — programme clause and any specific
  programme requirements
- The Contract Data — programme submission period, required content,
  required level of detail
- The contract administrator's response to the programme submission
  (acceptance, no objection, rejection, or comments)
- Any revised programme submissions and their responses
- Monthly progress reports — programme update sections
- Any recovery programme submission

**If the amendment document is not retrieved:**
State CANNOT CONFIRM the programme submission requirements, the
required content, or the prescribed submission period. Do not apply
any standard form requirement without confirmation.

**If the baseline programme document is not retrieved:**
State CANNOT ASSESS programme adequacy. Call tools to search before
concluding. If not found: flag the absence as a critical gap —
all subsequent delay analysis is affected.

**If no contract administrator acceptance or response letter is
retrieved:**
State CANNOT CONFIRM the formal status of the programme. Note the
distinction between formal acceptance and absence of objection.

### Layer 2b documents to retrieve (reference standards)

Call `search_chunks` with `layer_type = '2b'` to retrieve:
- Programme submission provision for the confirmed standard form
  (search by subject matter: "programme submission content
  requirements contract data acceptance")
- SCL Protocol 2nd Edition 2017 guidance on programme records
  (search by subject matter: "SCL Protocol programme baseline
  records contemporaneous")

**Purpose:** To establish what the standard form clause requires
so that amendment provisions can be assessed against it. The
requirements to apply are always those in the retrieved amendment
document — Layer 2b is the comparison baseline only.

**If the governing standard form is not retrieved from Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE for the
programme submission provisions. Do not describe requirements from
training knowledge.

---

## Analysis workflow

### Step 1 — Confirm programme submission requirements
*Contract-type-specific*

From the retrieved amendment document and Contract Data:
- What is the required submission period? (Extract from Contract
  Data — do not apply any standard form default.)
- What level of detail is required? (Activity level, resource
  loading, critical path visibility, method statements.)
- Is a specific software format required?
- Is the programme required to be resource-loaded?

**Do not apply any programme requirement without extracting it from
the retrieved amendment document or Contract Data.** If these
documents have not been retrieved: state CANNOT CONFIRM programme
requirements.

### Step 2 — Confirm the acceptance mechanism
*Contract-type-specific*

From the confirmed standard form and the retrieved amendment
document, establish what the acceptance mechanism requires.
Standard forms vary in how they handle programme acceptance:
- Some standard forms require the contract administrator to formally
  accept or give notice of non-compliance
- Others provide for a deemed acceptance mechanism if no response
  is issued within the prescribed period
- Others require explicit approval

Retrieve the applicable provision from Layer 2b to confirm the
mechanism for the confirmed standard form. Check the amendment
document for any modification. If the acceptance mechanism cannot
be confirmed from retrieved documents: state CANNOT CONFIRM the
formal acceptance position.

The distinction matters: a formally accepted programme constitutes
the contractual baseline. A programme not objected to within the
prescribed period may be deemed accepted under some standard forms —
confirm from the retrieved amendment document whether a deemed
acceptance mechanism exists.

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

**(f) Non-working periods and constraints:**
From the retrieved documents, identify whether non-working periods
(statutory holidays, project-specific shutdowns, authority
inspection hold points) are shown in the programme. These are
programme completeness checks — assess only from what the retrieved
project documents and contract documents show.

### Step 5 — Assess the contract administrator's response
*Contract-type-specific*

From the retrieved response letter:
- Was the programme formally accepted / approved?
- Was a no-objection issued (different from acceptance)?
- Was the programme rejected or returned with comments?
- Was no response issued within the prescribed period?

**Classify the formal status only from the retrieved response letter.**
If no response has been retrieved: state CANNOT CONFIRM formal
acceptance status.

### Step 6 — Assess revised and recovery programmes
*Contract-type-agnostic*

From the retrieved documents:
- Have revised programmes been submitted? State submission dates and
  scope of revision.
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
Formal acceptance letter retrieved → FORMALLY ACCEPTED — state
date and source
No-objection letter retrieved → NO OBJECTION ISSUED — note
distinction from formal acceptance
Rejection or comments letter retrieved → NOT ACCEPTED — state
reasons from retrieved letter
No response retrieved after searching → CANNOT CONFIRM FORMAL
STATUS — flag; note the forensic implication for delay analysis
Deemed acceptance mechanism in retrieved amendment document and
period elapsed → POTENTIALLY DEEMED ACCEPTED — flag; state the
mechanism and source

**Programme as contractual baseline:**
Formally accepted / deemed accepted → VALID CONTRACTUAL BASELINE
No objection issued → ARGUABLE BASELINE — flag; note that formal
acceptance and no-objection are treated differently in proceedings
Not formally accepted → DISPUTED BASELINE — flag immediately
Cannot confirm status → CANNOT CONFIRM BASELINE STATUS

**Critical path:**
Identifiable from retrieved programme → CRITICAL PATH IDENTIFIED
Not identifiable → CRITICAL PATH NOT IDENTIFIABLE — flag

---

## When to call tools

**Signal:** Baseline programme not retrieved
**Action:** `search_chunks` with query "baseline programme P6
master programme schedule"; `get_related_documents` with document
type "Baseline Programme", "Master Programme"
**Look for:** The programme document — any format

**Signal:** Programme submission period not in retrieved Contract Data
**Action:** `get_document` on the Contract Data document ID;
`search_chunks` with query "programme submission period weeks
days clause"
**Look for:** The programme clause and any prescribed submission period

**Signal:** Contract administrator response or acceptance letter
not retrieved
**Action:** `get_related_documents` with document type "Response
Letter"; `search_chunks` with query "programme accepted approved
no objection response"
**Look for:** The formal response to the programme submission

**Signal:** Layer 2b programme submission provision not retrieved
**Action:** `search_chunks` with `layer_type = '2b'` and query
"[standard form name] programme submission content requirements"
**Look for:** Standard form programme clause

---

## Always flag — regardless of query

1. **Baseline programme not found in the warehouse** — flag
   immediately; state that all delay analysis is affected.

2. **Programme not formally accepted or acceptance status
   unconfirmed** — flag; state the forensic implication: delay
   analysis relying on an unaccepted programme as the baseline
   is vulnerable to challenge.

3. **Programme does not show the contractual completion date** —
   flag the discrepancy; state both values and sources.

4. **Critical path not identifiable from the retrieved programme**
   — flag; state that the critical path cannot be assessed.

5. **Non-working periods or key constraints not reflected in the
   retrieved programme** — flag where the project scope makes
   these relevant; state the forensic implication for duration
   and productivity assumptions.

6. **Governing standard not retrieved from Layer 2b** — flag when
   the programme submission provision could not be retrieved; state
   what standard would need to be ingested.

---

## Output format

```
## Programme Assessment

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
[State whether the programme submission provision and SCL Protocol
were retrieved from Layer 2b. If not: state CANNOT CONFIRM —
STANDARD FORM NOT IN WAREHOUSE and list which analysis steps
are affected.]

### Programme Submission Requirements (this project)
Submission period: [from retrieved Contract Data / CANNOT CONFIRM]
Required content: [from retrieved amendment document or Contract Data /
CANNOT CONFIRM]
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
Non-working periods and constraints: [REFLECTED / NOT REFLECTED —
describe gap / CANNOT ASSESS]

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

**Programme submission provisions — structural summary (analytical
reference):**
Most standard forms of contract require the Contractor to submit a
programme within the period stated in the Contract Data. The
programme must typically show the order and timing of operations,
major stages, the methods intended, and the sequence of inspections
and tests. The contract administrator reviews the programme and
either accepts it or gives notice of non-compliance. The submission
period, required content, and acceptance mechanism are in the
contract documents — retrieve from Layer 1.

**Acceptance vs no objection — analytical reference:**
Formal acceptance and no-objection are not the same thing. A
no-objection letter is not necessarily a formal acceptance and its
status as a contractual baseline may be challenged in proceedings.
The formal status determines the strength of the programme as a
baseline for delay analysis. Some standard forms provide for a
deemed acceptance mechanism — confirm from the retrieved amendment
document.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies to
any contract form. All characterisations grounded in retrieved warehouse
documents only.*
