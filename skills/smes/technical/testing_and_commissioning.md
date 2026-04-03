# Testing and Commissioning

**Skill type:** Mixed
- Contract-type-agnostic: the review of test certificates,
  commissioning records, and the completion acceptance process
  applies regardless of standard form or version
- Contract-type-specific: the completion acceptance mechanism,
  the employer's right to refuse or defer acceptance, the defects
  liability period obligation, and the final certificate mechanism
  differ by standard form and must be confirmed from the retrieved
  governing standard in Layer 2b and the amendment document
**Layer dependency:**
- Layer 1 — project documents: inspection and test plan (ITP);
  test certificates; commissioning procedures and records;
  pre-commissioning checklists; completion certificate (if issued);
  outstanding works or snagging list; defects liability period
  register; final certificate (if issued); amendment document
  (testing, completion acceptance, and defects provisions);
  Contract Data or equivalent (defects liability period duration,
  completion acceptance mechanism)
- Layer 2b — reference standards: tests on completion provisions,
  completion acceptance mechanism, and defects liability provisions
  for the confirmed standard form (if ingested)
- Layer 2a — internal standards: commissioning procedures, authority
  inspection requirements (if applicable)
**Domain:** Technical & Construction SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when a query concerns whether tests on completion were
properly conducted, whether the completion certificate was correctly
issued or withheld, whether outstanding defects at handover were
recorded, whether the defects liability period obligation is being
met, or whether the final certificate has been issued. Apply when
assessing the handover status and defects position.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings and key_dates_and_securities
findings where available.

From the invoking orchestrator extract:
- Confirmed standard form and version
- Defects liability period as confirmed from retrieved Contract Data
  or equivalent
- Completion certificate date (if issued)
- Final certificate date (if issued)

From key_dates_and_securities findings:
- Completion certificate date and status
- Final certificate status
- Defects liability period expiry date (if calculable from
  confirmed dates)

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The inspection and test plan (ITP) for the relevant work stages
- Test certificates for tests on completion
- Commissioning procedures and commissioning records
- Pre-commissioning checklists
- The completion certificate (if issued)
- The outstanding works or snagging list at handover
- The defects liability period defect register (if maintained)
- The final certificate (if issued)
- The amendment document — testing, completion acceptance, and
  defects provisions
- The Contract Data or equivalent — defects liability period
  duration, completion acceptance mechanism

**If the completion certificate has not been retrieved:**
State CANNOT CONFIRM the completion acceptance status. The
completion certificate date is the trigger for the defects
liability period and, typically, for the first retention release —
its absence from the warehouse is a significant gap.

**If test certificates for tests on completion have not been
retrieved:** State CANNOT CONFIRM the test results from warehouse
documents.

**If the amendment document testing and acceptance provisions
have not been retrieved:** State CANNOT CONFIRM the applicable
acceptance mechanism, tests on completion requirements, or defects
liability obligations.

### Layer 2b documents to retrieve (reference standards)

Call `search_chunks` with `layer_type = '2b'` to retrieve:
- Tests on completion provisions for the confirmed standard form
  (search by subject matter: "tests completion commissioning
  procedure pass fail")
- Completion acceptance mechanism for the confirmed standard form
  (search by subject matter: "completion acceptance certificate
  employer contractor obligation")
- Defects liability provisions for the confirmed standard form
  (search by subject matter: "defects liability period
  rectification obligation final certificate")

**Purpose:** To establish the standard form testing, acceptance,
and defects framework for structural comparison against the
retrieved amendment document. The actual obligations are in the
retrieved contract documents.

**If the governing standard form is not retrieved from Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE for the
testing, acceptance, and defects provisions. Confidence cap: AMBER.
Proceed with what is confirmed from Layer 1.

---

## Analysis workflow

### Step 1 — Confirm the tests on completion requirements
*Contract-type-specific*

From the retrieved amendment document and ITP:
- What tests are required before completion acceptance? Extract
  from the retrieved amendment document, specification, or ITP.
- Who conducts the tests — the contractor alone, or witnessed
  by the contract administrator?
- What are the pass criteria?
- What notice period is required before testing? Extract from
  the retrieved contract documents — do not apply any standard
  form period without retrieved confirmation.

**Do not state any testing requirement without a retrieved source.**
If the ITP has not been retrieved: state CANNOT CONFIRM the required
test schedule.

### Step 2 — Assess test certificates
*Contract-type-agnostic*

From the retrieved test certificates for tests on completion:
- What tests were conducted?
- What test standard was applied?
- What was the result?
- Was the test passed or failed per the retrieved certificate?
- Was the test witnessed by the required party (confirm from the
  retrieved certificate or ITP)?

**For each test: state the result from the retrieved certificate.**
Do not assess pass/fail without the retrieved specification
requirement and the retrieved test result.

If a test was failed: is there a re-test record? Retrieve it and
state the re-test result.

### Step 3 — Assess commissioning records
*Contract-type-agnostic*

From the retrieved commissioning procedures and records:
- Were commissioning procedures submitted and approved before
  commissioning commenced?
- Were pre-commissioning checklists completed?
- Are there commissioning records showing system-by-system
  completion?
- Are there outstanding items on the pre-commissioning checklists?

**State what the retrieved commissioning records show.** If
commissioning records have not been retrieved: state CANNOT ASSESS
commissioning status from warehouse documents.

### Step 4 — Assess the completion certificate
*Contract-type-specific*

From the retrieved completion certificate (if issued) and the
retrieved amendment document:
- Was the certificate issued after successful tests on completion?
- What was accepted — the whole of the works, a section, or a part?
- Were any outstanding items or defects noted on the certificate
  or accompanying snagging list?
- Is the certificate date consistent with the snagging list and
  test certificate dates?

**If the certificate has not been issued but the works appear
complete from retrieved site records:** State from the retrieved
documents what the position appears to be. Do not conclude whether
a certificate should have been issued — flag the gap and state the
forensic implication (defects liability period may not have started;
retention may not have been released).

**If the employer withheld the certificate:** From the retrieved
correspondence, identify the reason stated for withholding. Assess
whether the stated reason corresponds to a contractual basis for
withholding from the retrieved amendment document.

### Step 5 — Assess the completion acceptance mechanism
*Contract-type-specific*

From the retrieved amendment document and Layer 2b provisions:
- What is the mechanism for completion acceptance — does the
  contractor apply for the certificate, or does the employer issue
  it at the employer's election?
- What is the prescribed response period for the contract
  administrator? Extract from the retrieved Contract Data or
  equivalent.
- Has the response period elapsed without a response?

**Apply only the mechanism confirmed from the retrieved amendment
document.** Standard forms differ in their acceptance mechanics —
do not apply provisions from the standard form without confirming
they have not been amended.

### Step 6 — Assess the defects liability period register
*Contract-type-specific*

From the retrieved defects liability period register and the
confirmed period duration:
- How many defects have been notified during the defects liability
  period?
- What is the status of each notified defect?
- Are there defects notified during the defects liability period
  that have not been rectified?
- Has the defects liability period expired? (Calculate from
  confirmed completion certificate date and confirmed period
  duration — only if both are confirmed from retrieved documents.)

**If the defects liability period has not expired and defects
remain open:** flag the open defects and state the rectification
obligation from the retrieved amendment document.

**If the defects liability period has expired:** flag any defects
notified before expiry but not yet rectified — state the basis
from retrieved documents and what the amendment document says
about the consequence.

### Step 7 — Assess the final certificate
*Contract-type-specific*

From the retrieved final certificate (if issued):
- Has the final certificate been issued?
- What was its date?
- Were any outstanding matters noted?

**If the final certificate has not been issued and the defects
liability period appears to have expired (from confirmed dates):**
Flag that the final certificate may be overdue. State the basis
from retrieved documents only. Cross-reference key_dates_and_
securities findings.

---

## Classification and decision rules

**Tests on completion:**

All required tests passed from retrieved certificates →
ALL TESTS PASSED
One or more tests failed in retrieved certificates →
TEST FAILURE — flag; state the test, result, and source
Re-test passed → TEST FAILED THEN PASSED — note; state dates
Test certificates not retrieved → CANNOT CONFIRM TEST RESULTS

**Completion certificate:**

Certificate retrieved and dated → COMPLETION ACCEPTED — state
date and scope
Works appear complete from retrieved records but certificate not
retrieved → COMPLETION STATUS UNCONFIRMED — flag; state the basis
for the assessment and what is missing
Employer withheld certificate — reason stated in retrieved
correspondence → CERTIFICATE WITHHELD — flag; state the stated
reason and the contractual basis if confirmable from amendment
document
Response period elapsed without response (period confirmed from
Contract Data) → POTENTIALLY OVERDUE — flag

**Defects liability period:**

Period active, defects notified, all rectified from retrieved
records → DEFECTS LIABILITY OBLIGATIONS BEING MET
Period active, open defects in retrieved register →
OPEN DEFECTS IN LIABILITY PERIOD — flag; state number and
references
Period expired (from confirmed dates), open defects remain →
OVERDUE DEFECTS — flag
Period status cannot be confirmed (completion certificate date
or period duration not retrieved) → CANNOT CONFIRM DEFECTS
LIABILITY PERIOD STATUS

**Final certificate:**

Final certificate retrieved → ISSUED — state date
Defects liability period appears expired from confirmed dates
AND final certificate not retrieved → POTENTIALLY OVERDUE — flag
Period status unconfirmed → CANNOT ASSESS FINAL CERTIFICATE STATUS

---

## When to call tools

**Signal:** Completion certificate not retrieved
**Action:** `get_related_documents` with document type "Completion
Certificate", "Taking-Over Certificate", "Certificate of Practical
Completion", "Certificate of Substantial Completion";
`search_chunks` with query "completion certificate issued
acceptance handover"
**Look for:** The completion certificate document

**Signal:** Test certificates for tests on completion not retrieved
**Action:** `get_related_documents` with document types "Test
Certificate", "Commissioning Certificate"; `search_chunks` with
query "tests completion commissioning certificate [work type]"
**Look for:** Test and commissioning certificates for the relevant
systems

**Signal:** ITP not retrieved
**Action:** `get_related_documents` with document type "Inspection
and Test Plan"; `search_chunks` with query "inspection test plan
ITP hold point tests completion"
**Look for:** The ITP for the relevant work stage

**Signal:** Final certificate not retrieved
**Action:** `get_related_documents` with document type "Final
Certificate", "Performance Certificate", "Defects Certificate";
`search_chunks` with query "final certificate defects
liability period completion"
**Look for:** The final certificate

**Signal:** Amendment document testing and acceptance provisions
not retrieved
**Action:** `search_chunks` with query "amendment particular
conditions testing completion acceptance defects";
`get_document` on amendment document ID
**Look for:** The testing on completion and acceptance provisions

**Signal:** Layer 2b tests on completion or acceptance provisions
not retrieved
**Action:** `search_chunks` with `layer_type = '2b'` and query
"[standard form name] tests completion acceptance certificate
defects liability period"
**Look for:** Standard form testing and acceptance provisions

---

## Always flag — regardless of query

1. **Tests on completion failed or not evidenced in the warehouse**
   — flag; state the test type and the consequence for the
   completion acceptance position.

2. **Completion certificate not issued despite works appearing
   complete from retrieved records** — flag; state what the
   retrieved records show and the forensic implication (defects
   liability period not started, retention not released, agreed
   damages position unclear).

3. **Outstanding items or open defects at the confirmed completion
   certificate date** — flag; state the items from the retrieved
   snagging list or defect register.

4. **Defects notified during the defects liability period but not
   rectified before period expiry** — flag; state the open defects
   and the consequence from the retrieved amendment document.

5. **Final certificate not issued and defects liability period
   appears to have expired** — flag; state the basis from retrieved
   documents and the forensic implication (second retention release
   pending, contractor's contractual liability period unclear).

6. **Governing standard not in Layer 2b** — flag; state that the
   completion acceptance mechanism, tests on completion
   requirements, and defects liability framework cannot be confirmed
   from the warehouse and that confidence is capped at AMBER.

---

## Output format

```
## Testing and Commissioning Assessment

### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [standard form name — or NOT RETRIEVED]
Layer 2b provisions retrieved: [tests on completion, completion
acceptance, defects liability — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE]
Layer 2a source: [policy name — or NOT RETRIEVED / NOT APPLICABLE]
Layer 1 primary document: [ITP and test certificates — or NOT RETRIEVED]
Layer 1 amendment document: [name — or NOT RETRIEVED]
Provisions CANNOT CONFIRM: [list — or NONE]

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2b Reference Retrieved
[State whether tests on completion, completion acceptance, and
defects liability provisions were retrieved from Layer 2b. If not:
state CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE and list
affected analysis steps. Confidence cap: AMBER.]

### Tests on Completion
ITP retrieved: [YES — reference / NOT FOUND]
Required tests confirmed: [from retrieved ITP and amendment document /
CANNOT CONFIRM]

| Test type | Certificate retrieved | Date | Standard applied | Result | Pass/Fail |
|---|---|---|---|---|---|
| [type] | [YES — ref / NOT FOUND] | [date] | [standard] | [result] | [PASS/FAIL/CANNOT CONFIRM] |

### Commissioning
Commissioning records retrieved: [YES — description / NOT FOUND]
Pre-commissioning checklists: [COMPLETE / OUTSTANDING ITEMS —
describe / NOT RETRIEVED]
Commissioning status: [COMPLETE FROM RETRIEVED RECORDS /
OUTSTANDING ITEMS / CANNOT ASSESS]

### Completion Certificate
Status: [ISSUED — date and scope / NOT FOUND IN WAREHOUSE /
WITHHELD — stated reason from retrieved correspondence]
Source: [document reference]
Outstanding items at acceptance: [YES — describe from snagging
list / NONE RECORDED / CANNOT CONFIRM — snagging list not retrieved]
Response period: [from retrieved Contract Data / CANNOT CONFIRM]
Assessment: [TIMELY / POTENTIALLY OVERDUE / WITHHELD —
contractual basis from amendment document / CANNOT CONFIRM STATUS]

### Defects Liability Period Position
Period duration: [from retrieved Contract Data / CANNOT CONFIRM]
Period start date: [from completion certificate date /
CANNOT CONFIRM — certificate not retrieved]
Period expiry date: [calculated from confirmed dates /
CANNOT CALCULATE]
Period status: [ACTIVE / EXPIRED / CANNOT CONFIRM]
Defects notified during period: [number from retrieved register /
NOT FOUND]
Open defects in liability period: [number and references /
NONE / CANNOT CONFIRM]

### Final Certificate
Status: [ISSUED — date / NOT FOUND IN WAREHOUSE]
Source: [document reference]
Assessment: [ISSUED / POTENTIALLY OVERDUE — state basis /
CANNOT ASSESS — defects liability period status unconfirmed]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any completion acceptance mechanism,
testing requirement, or defects liability obligation from this
section without first confirming it from the retrieved project
documents and Layer 2b.*

**Completion acceptance mechanism — analytical reference:**
Standard forms differ in how completion is accepted. Some require
the contractor to apply for the completion certificate when the
works are substantially complete; others require the employer to
issue the certificate at the employer's election or after
inspection. Many standard forms prescribe a response period for
the contract administrator — if the period lapses without a
response, deemed acceptance may apply. The specific mechanism
must be retrieved from the amendment document and the governing
standard form. Do not assume any particular acceptance procedure
without retrieved confirmation.

**Defects liability period — analytical reference:**
After completion acceptance, most standard forms provide for a
defects liability period during which defects are notified by the
contract administrator and remedied by the contractor. The duration
is in the Contract Data or equivalent — retrieve from Layer 1.
The contractual name for this period varies by standard form.
The final certificate is issued after all defects have been
remedied and the contractor has fulfilled its contractual
obligations. After the final certificate, the contractor's
contractual liability for construction defects typically ends
(subject to any statutory long-stop liability under applicable
law). Retrieve the period duration and the final certificate
mechanism from Layer 2b and the amendment document before applying
this framework.

**Tests on completion — analytical reference:**
Tests on completion are conducted before or as part of the
completion acceptance process, depending on the standard form.
They typically include system performance tests, commissioning
tests, and inspection of completed work. The test requirements —
scope, pass criteria, witnessing requirements, and the consequence
of failure — are in the contract specification, the ITP, and the
amendment document. Retrieve before applying.
