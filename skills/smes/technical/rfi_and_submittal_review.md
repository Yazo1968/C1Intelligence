# RFI and Submittal Review

**Skill type:** Mixed
- Contract-type-agnostic: the framework for reviewing RFI logs,
  assessing response timeliness, and evaluating submittal approval
  status applies regardless of book type
- Contract-type-specific: the contractual consequence of a delayed
  RFI response (whether it constitutes an Employer Risk Event
  entitling EOT and Cost), and the authority of the Engineer or
  Employer's Representative to respond, differs by book and edition
**Layer dependency:**
- Layer 1 — project documents: RFI log and individual RFI forms;
  submittal register and submittal packages; Particular Conditions
  (RFI and submittal response periods if stated); Contract Data;
  Employer's Requirements (Yellow/Silver — defines submittal
  requirements); programme (to assess delay impact of late responses)
- Layer 2 — reference standards: FIDIC Clause 1.9 (errors in
  Employer's Requirements — Yellow Book) and relevant clause for
  information supply obligations for the confirmed book and edition
**Domain:** Technical & Construction SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when a query concerns RFI response times, whether a delayed
RFI or submittal response caused delay or disruption, whether an
RFI response constituted a variation instruction, whether a submittal
was approved before work proceeded, or whether the RFI or submittal
register reveals patterns of delay or non-compliance.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings first.

From the invoking orchestrator extract:
- Confirmed FIDIC book and edition
- Contract administrator identity (Engineer or Employer's
  Representative)
- Any Particular Conditions provisions on RFI or submittal
  response periods

**RFI response periods:** These may or may not be stated in the
contract. Extract from the retrieved Particular Conditions or
Contract Data if present. Do not apply any response period as
a standard without a retrieved contractual source.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The RFI log (full register with submission and response dates)
- Individual RFI forms for RFIs relevant to the query
- The submittal register (full register with submission, review,
  and approval status)
- Individual submittal packages for submittals relevant to the query
- The Particular Conditions — any RFI or submittal clause
- The Contract Data — any prescribed response periods
- The Employer's Requirements (Yellow/Silver) — submittal
  requirements and format
- The programme — to assess the delay impact of late responses
  on specific activities

**If the RFI log is not retrieved:**
State CANNOT ASSESS RFI timeliness or patterns from warehouse
documents. Call tools to search before concluding.

**If the submittal register is not retrieved:**
State CANNOT ASSESS submittal approval status from warehouse
documents.

**If RFI response periods are not stated in the retrieved
Particular Conditions or Contract Data:**
State that no contractual response period has been confirmed from
retrieved documents. Assessment of response timeliness cannot be
made against a contractual standard in the absence of a confirmed
period.

### Layer 2 documents to retrieve (reference standards)

Call `search_chunks` to retrieve from Layer 2:
- FIDIC Clause 1.9 (Yellow Book — errors in Employer's
  Requirements; obligation to supply information) for the confirmed
  edition
- The relevant FIDIC clause on information supply obligations
  for the confirmed book and edition

**Purpose:** To establish the FIDIC framework for information
supply obligations and the consequence of delayed responses.

---

## Analysis workflow

### Step 1 — Assess the RFI log
*Contract-type-agnostic*

From the retrieved RFI log:
- Total number of RFIs submitted
- Number of RFIs responded to (and within what period where
  determinable from the log)
- Number of RFIs outstanding / open at the time of the query
- Date range of RFI submissions

**Extract these figures from the retrieved log.** Do not estimate
quantities not in the retrieved document.

### Step 2 — Assess RFI response timeliness
*Contract-type-specific for the contractual standard;
contract-type-agnostic for the measurement*

For each RFI relevant to the query (or the full log if a pattern
assessment is required):
- State the RFI submission date from the retrieved log
- State the response date from the retrieved log
- Calculate the elapsed days (response date minus submission date)
- Compare against the response period extracted from the retrieved
  Particular Conditions or Contract Data

**If no contractual response period has been confirmed from
retrieved documents:** State the elapsed days per RFI but note
that timeliness cannot be assessed against a contractual standard
because no confirmed period exists in the retrieved contract
documents. Flag this gap.

**If a contractual response period has been confirmed:**
Classify each RFI response as: WITHIN PERIOD / LATE / NO RESPONSE.

### Step 3 — Assess RFI content and impact
*Contract-type-agnostic*

For RFIs relevant to the query or to a claimed delay or disruption:
- What does the RFI request? (Clarification of specification,
  drawing discrepancy, design information, instruction)
- Did the response resolve the RFI or require further information?
- If the RFI concerned a drawing discrepancy or missing information:
  does the retrieved programme show the affected activity was on
  or near the critical path during the response period?

**Do not assess delay impact without the retrieved programme.**
If the programme has not been retrieved for the relevant period:
state CANNOT ASSESS delay impact from warehouse documents.

### Step 4 — Assess whether an RFI response constituted a variation
*Contract-type-specific*

From the retrieved RFI response:
- Does the response go beyond clarification — does it change the
  scope, specification, or design?
- If yes: was a formal variation instruction issued separately,
  or was the change implemented via the RFI response alone?

An RFI response that changes the scope without a formal variation
instruction is a potential variation without proper authority.
Flag where this pattern is identified from the retrieved documents.
Confirm the Engineer's variation authority from the invoking
orchestrator's engineer_identification findings.

### Step 5 — Assess the submittal register
*Contract-type-agnostic*

From the retrieved submittal register:
- For each submittal: state the submission date, the review
  completion date, the approval status (Approved, Approved as
  Noted, Revise and Resubmit, Rejected), and whether resubmission
  was required
- Identify submittals where work proceeded before approval was
  confirmed
- Identify submittals still under review (open) at the time of
  the query

**Assess only from the retrieved register.** Do not infer
approval status from the absence of a rejection record.

### Step 6 — Assess patterns
*Contract-type-agnostic*

From the retrieved RFI log and submittal register:
- Is there a pattern of late RFI responses in a specific period
  or for a specific discipline?
- Is there a pattern of submittal rejections for a specific trade
  or material?
- Do multiple late responses cluster around the same period as
  claimed delay events in the eot_quantification findings?

**Identify patterns only from retrieved documents.** A pattern
requires multiple instances from the retrieved log — do not
characterise a single late response as a pattern.

---

## Classification and decision rules

**RFI response timeliness:**

Response within confirmed contractual period → WITHIN PERIOD
Response outside confirmed contractual period → LATE — state
days overdue and source
No contractual period confirmed → ELAPSED TIME STATED — cannot
classify as within or outside contractual period
No response at date of query → OUTSTANDING — flag

**Delay impact of late RFI response:**

Late response AND affected activity on critical path from
retrieved programme → POTENTIAL DELAY IMPACT — flag; state
the RFI, the response delay, and the critical path status
from retrieved programme
Late response AND activity not on critical path → NO CRITICAL
PATH IMPACT IDENTIFIED FROM RETRIEVED DOCUMENTS
Programme not retrieved → CANNOT ASSESS DELAY IMPACT

**RFI response as variation:**

RFI response changes scope or specification confirmed from
retrieved documents AND no formal variation instruction retrieved
→ POTENTIAL VARIATION WITHOUT INSTRUCTION — flag
RFI response is clarification only → NO VARIATION IDENTIFIED

**Submittal approval:**

Approved before work proceeded (confirmed from retrieved register
and site records) → APPROVED PRE-COMMENCEMENT
Work proceeded before approval (evidenced from retrieved records)
→ WORK PROCEEDED BEFORE APPROVAL — flag
Approval status not determinable → CANNOT CONFIRM APPROVAL STATUS

---

## When to call tools

**Signal:** RFI log not retrieved
**Action:** `get_related_documents` with document type "RFI Log",
"Request for Information Log"; `search_chunks` with query "RFI
log register request information response"
**Look for:** The full RFI register with dates

**Signal:** Individual RFI form not retrieved for a specific RFI
**Action:** `search_chunks` with query "RFI [number] request
information [subject]"; `get_document` on RFI document ID if known
**Look for:** The individual RFI form and response

**Signal:** Submittal register not retrieved
**Action:** `get_related_documents` with document type "Submittal
Register", "Shop Drawing Register"; `search_chunks` with query
"submittal register approval status"
**Look for:** The full submittal register with approval status

**Signal:** Programme not retrieved — delay impact cannot be assessed
**Action:** `search_chunks` with query "programme update schedule
[RFI period dates]"; `get_related_documents` with document type
"Programme Update"
**Look for:** The programme update current during the RFI delay
period — to assess critical path status of the affected activity

**Signal:** No RFI response period in retrieved PC or Contract Data
**Action:** `search_chunks` with query "RFI response period days
particular conditions employer requirements"; `get_document` on
Employer's Requirements document ID if known
**Look for:** Any prescribed RFI response period in the contract
documents

---

## Always flag — regardless of query

1. **Outstanding RFIs at the time of the query** — flag; state
   the number and the oldest outstanding RFI date from the
   retrieved log.

2. **Pattern of late RFI responses clustering around claimed delay
   periods** — flag with specific RFI references and dates from
   the retrieved log.

3. **RFI response that appears to change scope without a formal
   variation instruction** — flag; state the RFI reference and
   the nature of the apparent change from the retrieved document.

4. **Work proceeded before submittal approval confirmed** — flag;
   state the submittal reference and the forensic implication.

5. **No contractual RFI response period confirmed from retrieved
   documents** — flag; state that timeliness assessment cannot
   be made against a contractual standard.

---

## Output format

```
## RFI and Submittal Review Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2 Reference Retrieved
[State whether relevant FIDIC clauses were retrieved. If not:
state analytical knowledge applied.]

### Contractual RFI Response Period
Period confirmed: [YES — value and source / NOT CONFIRMED FROM
RETRIEVED DOCUMENTS]

### RFI Log Summary
Total RFIs in retrieved log: [number / NOT RETRIEVED]
RFIs responded to: [number]
RFIs outstanding: [number]
Date range: [from retrieved log]

### RFI Timeliness Assessment

| RFI # | Submitted | Responded | Elapsed days | Contractual period | Classification |
|---|---|---|---|---|---|
| [#] | [date] | [date / NO RESPONSE] | [days] | [from PC / NOT CONFIRMED] | [WITHIN PERIOD / LATE / OUTSTANDING / CANNOT CLASSIFY] |

### RFI Impact Assessment
[For RFIs with potential delay impact:]
**RFI [number] — [subject]**
Response delay: [days from retrieved log]
Affected activity: [from retrieved programme / CANNOT CONFIRM — programme not retrieved]
Critical path status at time: [from retrieved programme update / CANNOT CONFIRM]
Delay impact: [POTENTIAL DELAY IMPACT / NO CRITICAL PATH IMPACT /
CANNOT ASSESS — programme not retrieved]
Variation risk: [YES — describe from retrieved response /
NO / CANNOT ASSESS]

### Submittal Register Summary
Total submittals in retrieved register: [number / NOT RETRIEVED]
Approved: [number]
Approved as Noted: [number]
Revise and Resubmit / Rejected: [number]
Outstanding: [number]

### Submittal Findings
[For each submittal of significance:]
**Submittal [reference] — [description]**
Submitted: [date]
Response: [date / NOT RESPONDED]
Status: [APPROVED / APPROVED AS NOTED / REVISE AND RESUBMIT /
REJECTED / OUTSTANDING]
Work proceeded before approval: [YES — source / NO / CANNOT CONFIRM]
Source: [register reference]

### Patterns Identified
[Pattern description with supporting RFI/submittal references,
or NO PATTERNS IDENTIFIED FROM RETRIEVED DOCUMENTS]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any response period or contractual
obligation from this section without first confirming it from the
retrieved project documents.*

**RFI response obligations — analytical reference:**
FIDIC does not prescribe a specific RFI response period in the
General Conditions. The obligation on the Engineer to supply
information and instructions in time for the Contractor to
plan and execute the works is implied in the contract. A delayed
response that prevents the Contractor from executing work on
programme may be an Employer Risk Event under the EOT clause.
Whether a specific response period is contractual depends on
the retrieved Particular Conditions or Employer's Requirements.

**Submittal review — analytical reference:**
The contract specification or Employer's Requirements typically
state the submittal review period. The Engineer's approval of a
submittal does not override the specification — a submittal
approved with conditions that conflict with the specification
creates ambiguity. An RFI response that relaxes a specification
requirement without a formal variation instruction is a potential
variation without proper authority.
