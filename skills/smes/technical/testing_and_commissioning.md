# Testing and Commissioning

**Skill type:** Mixed
- Contract-type-agnostic: the review of test certificates,
  commissioning records, and the Taking-Over process applies
  regardless of FIDIC book or edition
- Contract-type-specific: the Taking-Over Certificate mechanism,
  the Employer's right to refuse Taking-Over, and the DNP defects
  obligation differ by FIDIC book and edition and must be confirmed
  from the retrieved Particular Conditions
**Layer dependency:**
- Layer 1 — project documents: inspection and test plan (ITP);
  test certificates; commissioning procedures and records;
  pre-commissioning checklists; Taking-Over Certificate;
  snagging list; DNP defect register; Performance Certificate;
  Particular Conditions (Clauses 9, 10, 11); Contract Data
  (DNP period, TOC mechanism)
- Layer 2 — reference standards: FIDIC Clause 9 (Tests on
  Completion), Clause 10 (Employer's Taking Over), and Clause 11
  (Defects After Taking Over) for the confirmed book and edition
**Domain:** Technical & Construction SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when a query concerns whether Tests on Completion were
properly conducted, whether the Taking-Over Certificate was
correctly issued or withheld, whether outstanding defects at
handover were recorded, whether the DNP defect obligation is
being met, or whether the Performance Certificate has been issued.
Apply when assessing the handover status and defects position.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings and key_dates_and_securities
findings where available.

From the invoking orchestrator extract:
- Confirmed FIDIC book and edition
- DNP period as confirmed from retrieved Contract Data
- Taking-Over Certificate date (if issued)
- Performance Certificate date (if issued)

From key_dates_and_securities findings:
- TOC date and status
- Performance Certificate status
- DNP expiry date (if calculable from confirmed dates)

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The inspection and test plan (ITP) for the relevant work stages
- Test certificates for Tests on Completion
- Commissioning procedures and commissioning records
- Pre-commissioning checklists
- The Taking-Over Certificate (if issued)
- The snagging list or outstanding works list at handover
- The DNP defect register (if maintained)
- The Performance Certificate (if issued)
- The Particular Conditions — Clauses 9, 10, and 11 amendments
- The Contract Data — DNP period, TOC mechanism

**If the Taking-Over Certificate has not been retrieved:**
State CANNOT CONFIRM the Taking-Over status. The TOC date is the
trigger for the DNP and the first retention release — its absence
from the warehouse is a significant gap.

**If test certificates for Tests on Completion have not been retrieved:**
State CANNOT CONFIRM the test results from warehouse documents.

**If the Particular Conditions Clauses 9–11 have not been retrieved:**
State CANNOT CONFIRM the applicable TOC mechanism, the Tests on
Completion requirements, or the DNP obligations.

### Layer 2 documents to retrieve (reference standards)

Call `search_chunks` to retrieve from Layer 2:
- FIDIC Clause 9 (Tests on Completion) for the confirmed book
  and edition
- FIDIC Clause 10 (Employer's Taking Over) for the confirmed
  book and edition
- FIDIC Clause 11 (Defects After Taking Over) for the confirmed
  book and edition

**Purpose:** To establish the standard FIDIC testing and Taking-Over
framework for comparison against the retrieved Particular Conditions.
The actual obligations are in the retrieved PC.

---

## Analysis workflow

### Step 1 — Confirm the Tests on Completion requirements
*Contract-type-specific*

From the retrieved Particular Conditions and ITP:
- What tests are required before Taking-Over? Extract from the
  retrieved Particular Conditions, specification, or ITP.
- Who conducts the tests — the Contractor alone, or witnessed
  by the Engineer/Employer's Representative?
- What are the pass criteria?
- What is the notice period required before testing? Extract
  from the retrieved contract documents — do not apply a standard
  form period without confirmation.

**Do not state any testing requirement without a retrieved source.**
If the ITP has not been retrieved: state CANNOT CONFIRM the required
test schedule.

### Step 2 — Assess test certificates
*Contract-type-agnostic*

From the retrieved test certificates for Tests on Completion:
- What tests were conducted?
- What test standard was applied?
- What was the result?
- Was the test passed or failed per the retrieved certificate?
- Was the test witnessed by the required party (confirm from
  the retrieved certificate or ITP)?

**For each test: state the result from the retrieved certificate.**
Do not calculate pass/fail without the retrieved specification
requirement and the retrieved test result.

If a test was failed: is there a re-test record? Retrieve it
and state the re-test result.

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

### Step 4 — Assess the Taking-Over Certificate
*Contract-type-specific*

From the retrieved Taking-Over Certificate (if issued) and the
retrieved Particular Conditions:
- Was the TOC issued after successful Tests on Completion?
- What was taken over — the whole of the Works, a section,
  or a part?
- Were any outstanding items or defects noted on the TOC?
- Is the TOC date consistent with the snagging list and
  test certificate dates?

**If the TOC has not been issued but the works appear complete
from retrieved site records:**
State from the retrieved documents what the position appears to
be. Do not conclude whether a TOC should have been issued —
flag the gap and state the forensic implication.

**If the Employer withheld the TOC:** From the retrieved
correspondence, identify the reason stated for withholding.
Assess whether the stated reason corresponds to a contractual
basis for withholding from the retrieved Particular Conditions.

### Step 5 — Assess the Taking-Over mechanism
*Contract-type-specific*

From the retrieved Particular Conditions (Clause 10 as amended):
- What is the mechanism for Taking-Over — does the Contractor
  apply for the TOC, or does the Employer issue it at the
  Employer's election?
- What is the prescribed response period for the Engineer/ERA?
  Extract from the retrieved Contract Data.
- Has the response period elapsed without a response?

**Apply only the mechanism confirmed from the retrieved PC.**
The 2017 and 1999 editions differ in their Taking-Over provisions.
Do not apply edition-specific provisions without confirming
the edition from the retrieved documents.

### Step 6 — Assess the DNP defect register
*Contract-type-specific*

From the retrieved DNP defect register and the confirmed DNP
period:
- How many defects have been notified during the DNP?
- What is the status of each notified defect?
- Are there defects notified during the DNP that have not been
  rectified?
- Has the DNP expired? (Calculate from confirmed TOC date and
  confirmed DNP period — only if both are confirmed from
  retrieved documents.)

**If the DNP has not expired and defects remain open:** flag
the open defects and state the Contractor's obligation to rectify.

**If the DNP has expired:** flag any defects notified before
expiry but not yet rectified — these should be addressed under
the Performance Certificate mechanism.

### Step 7 — Assess the Performance Certificate
*Contract-type-specific*

From the retrieved Performance Certificate (if issued):
- Has the Performance Certificate been issued?
- What was its date?
- Were any outstanding matters noted?

**If the Performance Certificate has not been issued and the
DNP appears to have expired (from confirmed dates):**
Flag that the Performance Certificate may be overdue. State
the basis for this from retrieved documents only.
Cross-reference key_dates_and_securities findings.

---

## Classification and decision rules

**Tests on Completion:**

All required tests passed from retrieved certificates →
ALL TESTS PASSED
One or more tests failed in retrieved certificates →
TEST FAILURE — flag; state the test, result, and source
Re-test passed → TEST FAILED THEN PASSED — note; state dates
Test certificates not retrieved → CANNOT CONFIRM TEST RESULTS

**Taking-Over Certificate:**

TOC retrieved and dated → TAKING-OVER OCCURRED — state date
and scope
Works appear complete from retrieved records but TOC not retrieved
→ TOC STATUS UNCONFIRMED — flag; state the basis for the
assessment and what is missing
Employer withheld TOC — reason stated in retrieved correspondence
→ TOC WITHHELD — flag; state the stated reason and the
contractual basis (if confirmable from PC)
TOC response period elapsed without response (period confirmed
from Contract Data) → POTENTIALLY OVERDUE — flag

**DNP defects:**

DNP active, defects notified, all rectified from retrieved records
→ DNP OBLIGATIONS BEING MET
DNP active, open defects in retrieved register →
OPEN DNP DEFECTS — flag; state number and references
DNP expired (from confirmed dates), open defects remain →
OVERDUE DNP DEFECTS — flag
DNP status cannot be confirmed (TOC date or DNP period not
retrieved) → CANNOT CONFIRM DNP STATUS

**Performance Certificate:**

Performance Certificate retrieved → ISSUED — state date
DNP appears expired from confirmed dates AND PC not retrieved →
POTENTIALLY OVERDUE — flag
DNP status unconfirmed → CANNOT ASSESS PC STATUS

---

## When to call tools

**Signal:** Taking-Over Certificate not retrieved
**Action:** `get_related_documents` with document type "Taking-Over
Certificate"; `search_chunks` with query "taking over certificate
issued handover completion"
**Look for:** The TOC document

**Signal:** Test certificates for Tests on Completion not retrieved
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

**Signal:** Performance Certificate not retrieved
**Action:** `get_related_documents` with document type "Performance
Certificate"; `search_chunks` with query "performance certificate
defects notification period"
**Look for:** The Performance Certificate

**Signal:** Particular Conditions Clauses 9–11 not retrieved
**Action:** `search_chunks` with query "particular conditions
clause 9 10 11 tests taking over defects"; `get_document` on
PC document ID
**Look for:** The testing and Taking-Over provisions in the PC

---

## Always flag — regardless of query

1. **Tests on Completion failed or not evidenced in the warehouse**
   — flag; state the test type and the consequence for the
   Taking-Over position.

2. **Taking-Over Certificate not issued despite works appearing
   complete from retrieved records** — flag; state what the
   retrieved records show and the forensic implication (DNP not
   started, retention not released, LD position unclear).

3. **Outstanding items or open defects at the confirmed TOC date**
   — flag; state the items from the retrieved snagging list or
   NCR/defect register.

4. **DNP defects notified but not rectified before DNP expiry**
   — flag; state the open defects and the consequence from the
   retrieved PC.

5. **Performance Certificate not issued and DNP appears to have
   expired** — flag; state the basis from retrieved documents
   and the forensic implication (second retention release
   pending, Contractor's contractual liability period unclear).

---

## Output format

```
## Testing and Commissioning Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2 Reference Retrieved
[State whether FIDIC Clauses 9, 10, and 11 were retrieved.
If not: state analytical knowledge applied.]

### Tests on Completion
ITP retrieved: [YES — reference / NOT FOUND]
Required tests confirmed: [from retrieved ITP and PC / CANNOT CONFIRM]

| Test type | Certificate retrieved | Date | Standard applied | Result | Pass/Fail |
|---|---|---|---|---|---|
| [type] | [YES — ref / NOT FOUND] | [date] | [standard] | [result] | [PASS/FAIL/CANNOT CONFIRM] |

### Commissioning
Commissioning records retrieved: [YES — description / NOT FOUND]
Pre-commissioning checklists: [COMPLETE / OUTSTANDING ITEMS — describe /
NOT RETRIEVED]
Commissioning status: [COMPLETE FROM RETRIEVED RECORDS /
OUTSTANDING ITEMS / CANNOT ASSESS]

### Taking-Over Certificate
Status: [ISSUED — date and scope / NOT FOUND IN WAREHOUSE /
WITHHELD — stated reason from retrieved correspondence]
Source: [document reference]
Outstanding items at TOC: [YES — describe from snagging list /
NONE RECORDED / CANNOT CONFIRM — snagging list not retrieved]
TOC response period: [from retrieved Contract Data / CANNOT CONFIRM]
TOC assessment: [TIMELY / POTENTIALLY OVERDUE / WITHHELD —
contractual basis / CANNOT CONFIRM STATUS]

### DNP Position
DNP period: [from retrieved Contract Data / CANNOT CONFIRM]
DNP start date: [from TOC date / CANNOT CONFIRM — TOC not retrieved]
DNP expiry date: [calculated from confirmed dates / CANNOT CALCULATE]
DNP status: [ACTIVE / EXPIRED / CANNOT CONFIRM]
Defects notified during DNP: [number from retrieved register /
NOT FOUND]
Open DNP defects: [number and references / NONE / CANNOT CONFIRM]

### Performance Certificate
Status: [ISSUED — date / NOT FOUND IN WAREHOUSE]
Source: [document reference]
Assessment: [ISSUED / POTENTIALLY OVERDUE — state basis /
CANNOT ASSESS — DNP status unconfirmed]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any TOC mechanism, testing requirement,
or DNP obligation from this section without first confirming it from
the retrieved project documents.*

**FIDIC Taking-Over mechanism — analytical reference:**
Under FIDIC (all books), the Contractor applies for the Taking-Over
Certificate when the Works are substantially complete. The Engineer
(Red/Yellow) or Employer's Representative (Silver) either issues
the TOC or gives notice of the work required before it can be
issued. The 1999 and 2017 editions differ in the detailed mechanics
— the 2017 edition is more prescriptive on timeframes and deemed
acceptance. The Particular Conditions frequently amend the Taking-Over
provisions — always retrieve from Layer 1 before applying the
standard form framework.

**DNP and Performance Certificate — analytical reference:**
The DNP runs from the TOC date for the period stated in the
Contract Data. During the DNP, the Contractor must remedy defects
notified by the Engineer/ERA. The Performance Certificate is issued
when all defects have been remedied and the Contractor has fulfilled
all contractual obligations. After the Performance Certificate,
the Contractor's liability under the contract ends for construction
defects (subject to decennial liability where applicable). The
DNP duration and PC mechanism are in the Contract Data and
Particular Conditions — retrieve from Layer 1.

**GCC testing and commissioning — analytical reference:**
Authority inspections are mandatory hold points in all GCC
jurisdictions before commissioning can proceed — municipality,
civil defence, utility authorities. These hold points must be
completed before the Taking-Over Certificate can be issued.
Their status should be evidenced in the ITP and commissioning
records. The absence of authority inspection sign-offs is a
common reason for TOC delays on GCC projects.
