# Specification Compliance

**Skill type:** Contract-type-agnostic for the assessment framework
The method for assessing specification compliance — retrieve the
specification requirement, retrieve the test or inspection record,
compare — applies regardless of FIDIC book or edition. The
contractual consequences of non-compliance and the party responsible
for rectification are contract-type-specific and must be confirmed
from the retrieved Particular Conditions.
**Layer dependency:**
- Layer 1 — project documents: project specification (technical
  sections); material approval submittals; material test certificates;
  inspection and test plans (ITP); inspection request forms; test
  reports; NCR records; as-built records; Particular Conditions
  (defects clause, testing clause)
- Layer 2 — reference standards: FIDIC Clause 7 (Plant, Materials
  and Workmanship) and Clause 11 (Defects After Taking Over) for
  the confirmed book and edition; referenced testing standards
  (BS, ASTM, ISO, EN) if available in Layer 2
**Domain:** Technical & Construction SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when a query concerns whether materials or workmanship comply
with the contract specification, whether a test result constitutes
a non-conformance, whether a defect is attributable to specification
non-compliance, or whether the specification requirement for a
specific element can be confirmed from the retrieved documents.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings.

From the invoking orchestrator extract:
- Confirmed FIDIC book and edition
- Any Particular Conditions amendments to the testing or defects
  clauses

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The project specification — the technical section relevant to
  the element under assessment
- The material approval submittal for the element (if applicable)
- The test certificate(s) for the element
- The inspection and test plan (ITP) for the work stage
- The inspection request form and inspection record
- The NCR (if a non-conformance has been raised)
- The Particular Conditions — testing clause and defects clause

**If the project specification is not retrieved:**
State CANNOT CONFIRM the applicable specification requirement.
Do not assess compliance without the specification. This is the
foundational document for this skill.

**If no test certificate or inspection record is retrieved:**
State CANNOT ASSESS compliance from warehouse documents. Testing
may have occurred but the records are not in the warehouse.

**For each document retrieved:** State its reference number, date,
and the element it covers. The specification section and the test
certificate must both be present to perform a compliance assessment.

### Layer 2 documents to retrieve (reference standards)

Call `search_chunks` to retrieve from Layer 2:
- FIDIC Clause 7 for the confirmed book and edition — materials,
  plant, and workmanship obligations
- FIDIC Clause 11 — defects after Taking Over
- Referenced testing standards (BS, ASTM, ISO) if ingested in
  Layer 2 and referenced in the retrieved specification

**Purpose:** To establish the FIDIC framework for testing and
defects obligations, and to access the referenced testing standards
where available. The project specification governs compliance
requirements — the testing standards provide the methodology.

---

## Analysis workflow

### Step 1 — Identify the specification requirement
*Contract-type-agnostic*

From the retrieved project specification:
- Identify the specific requirement for the element under assessment
- State the requirement exactly as it appears in the retrieved
  specification: the material standard, the test standard, the
  acceptance criteria, and any method of measurement
- Identify the testing standard referenced (BS, ASTM, ISO, EN,
  etc.) and the edition year if stated

**Do not state any specification requirement without the retrieved
specification document as the source.** If the specification has
not been retrieved: state CANNOT CONFIRM the applicable requirement.

### Step 2 — Identify the applicable test or inspection record
*Contract-type-agnostic*

From the retrieved documents, identify:
- The test certificate(s) for the element under assessment —
  state the document reference, date, test type, test standard
  applied, result, and pass/fail determination
- The inspection record for the work stage
- The ITP hold point status for this element

**Assess only what is in the retrieved documents.** If test
certificates reference a test standard different from the
specification requirement: flag the discrepancy — the specification
governs.

### Step 3 — Compare test result against specification requirement
*Contract-type-agnostic*

Compare the test result in the retrieved certificate against the
acceptance criteria in the retrieved specification.

**State both values and both source documents.** Do not calculate
whether the result passes or fails without both retrieved documents.

If the test standard in the certificate differs from the standard
in the specification: flag this as a specification compliance gap —
the test was conducted to a different standard and cannot be used
to confirm compliance with the specified standard.

If the test result is not clearly pass or fail from the retrieved
certificate: state that pass/fail status is not determinable from
the retrieved document.

### Step 4 — Assess ITP compliance
*Contract-type-agnostic*

From the retrieved ITP and inspection records:
- Were the required ITP hold points and witness points observed?
- Were inspections conducted before work was covered or concealed?
- Is there any indication in the retrieved documents that work
  was covered before inspection?

**Flag any ITP hold point that was not observed before work
proceeded** — this is a quality control failure regardless of
whether the underlying work is compliant.

### Step 5 — Assess material approval status
*Contract-type-agnostic*

From the retrieved submittal register and material approval
documents:
- Was the material formally approved before installation?
- If rejected: was a compliant substitute approved?
- Is the material installed consistent with the approved material?

**If material was installed without approval:** flag as a
specification compliance failure regardless of the test results —
the approval process is a contractual requirement independent of
the test result.

### Step 6 — Assess NCR records
*Contract-type-agnostic*

From the retrieved NCR log and individual NCRs:
- Are there NCRs raised for the element under assessment?
- What is the NCR status: open, under rectification, closed?
- Does the NCR description confirm a specification non-conformance?

If NCRs are present: state the NCR reference, description, and
status from the retrieved document. Do not characterise an NCR as
closed without a retrieved close-out record.

### Step 7 — Assess rectification obligation
*Contract-type-specific*

From the retrieved Particular Conditions and confirmed FIDIC clause:
- Who is obliged to rectify a non-conformance: the Contractor
  (workmanship/materials obligation under Clause 7) or the Employer
  (design deficiency)?
- Is the rectification obligation within the DNP or has the DNP
  expired?
- Has a formal instruction to rectify been issued?

**The rectification obligation and the DNP period to apply are
from the retrieved Particular Conditions and Contract Data.**
Do not apply any standard form period without retrieved confirmation.

---

## Classification and decision rules

**Specification compliance:**

Test result retrieved AND specification requirement retrieved AND
result meets the requirement → COMPLIANT — state both values
and sources
Test result retrieved AND specification requirement retrieved AND
result does not meet the requirement → NON-COMPLIANT — flag;
state both values and sources; state the non-conformance clearly
Test conducted to different standard than specified →
TEST STANDARD MISMATCH — flag; compliance cannot be confirmed
from the retrieved test certificate
Test certificate not retrieved → CANNOT ASSESS COMPLIANCE —
records not in warehouse
Specification requirement not retrieved → CANNOT CONFIRM
APPLICABLE REQUIREMENT

**Material approval:**

Formally approved before installation (confirmed from retrieved
submittal register) → APPROVED
No approval record found in warehouse → CANNOT CONFIRM APPROVAL
STATUS — flag; material may have been installed without approval
Material installed different from approved material →
MATERIAL SUBSTITUTION — flag

**ITP hold point:**

Hold point observed and recorded in retrieved ITP/inspection record
→ HOLD POINT OBSERVED
Hold point not observed before work proceeded (evidenced from
retrieved site diary or diary entry) → HOLD POINT NOT OBSERVED —
flag
Hold point status not determinable from retrieved documents →
CANNOT CONFIRM HOLD POINT STATUS

**NCR status:**

Open NCR in retrieved log → OPEN NON-CONFORMANCE — flag
Closed NCR with close-out record → CLOSED — state close-out date
NCR referenced but close-out not retrieved → CANNOT CONFIRM
CLOSE-OUT STATUS

---

## When to call tools

**Signal:** Project specification not retrieved for the element
under assessment
**Action:** `search_chunks` with query "[element description]
specification requirement [material or test type]";
`get_related_documents` with document type "Project Specification",
"Technical Specification"
**Look for:** The specification section covering the element

**Signal:** Test certificate not retrieved
**Action:** `get_related_documents` with document types "Test
Certificate", "Test Report", "Lab Report"; `search_chunks` with
query "[element] test certificate [date range]"
**Look for:** Test certificates for the element in the relevant
period

**Signal:** ITP not retrieved
**Action:** `get_related_documents` with document type "Inspection
and Test Plan", "ITP"; `search_chunks` with query "inspection test
plan hold point witness"
**Look for:** The ITP and hold point records for the work stage

**Signal:** NCR log referenced but not retrieved
**Action:** `get_related_documents` with document type "NCR Log",
"Non-Conformance Report"; `search_chunks` with query "NCR
non-conformance [element description]"
**Look for:** The NCR log and any individual NCRs for the element

---

## Always flag — regardless of query

1. **Non-conformance confirmed from retrieved documents** — flag
   immediately; state the specification requirement, the test
   result, and both source documents.

2. **Test standard mismatch** — flag where the test certificate
   uses a different standard from the specification; state that
   compliance cannot be confirmed from the retrieved records.

3. **Material installed without confirmed approval** — flag; state
   that the approval process is a contractual requirement
   independent of test results.

4. **ITP hold point not observed before work proceeded** — flag;
   state the forensic implication (work may need to be exposed
   for inspection to confirm compliance).

5. **Open NCR at Taking-Over or still open in the warehouse** —
   flag; state the NCR reference and the forensic implication for
   the defects liability position.

---

## Output format

```
## Specification Compliance Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2 Reference Retrieved
[State whether FIDIC Clause 7 and 11 were retrieved. If not:
state analytical knowledge applied.]

### Specification Compliance Register

| # | Element | Specification requirement | Test standard | Test result | Pass/Fail | Assessment |
|---|---|---|---|---|---|---|
| 1 | [element] | [requirement and source] | [standard from spec] | [result from cert] | [PASS/FAIL/NOT DETERMINABLE] | [COMPLIANT/NON-COMPLIANT/CANNOT ASSESS] |

### Findings by Element

**[Element description]**
Specification requirement: [value and source document and clause]
Test certificate retrieved: [YES — reference and date / NOT FOUND]
Test standard applied: [from certificate / CANNOT CONFIRM]
Test result: [from certificate / CANNOT CONFIRM]
Compliance assessment: [COMPLIANT / NON-COMPLIANT — describe /
TEST STANDARD MISMATCH / CANNOT ASSESS]
Source documents: [specification reference, certificate reference]

### Material Approval Status
[For each material in scope:]
Material: [description]
Submittal reference: [from register / NOT FOUND]
Approval status: [APPROVED / NOT APPROVED / CANNOT CONFIRM]
Source: [document reference]

### ITP Hold Point Assessment
[For each hold point relevant to the query:]
Hold point: [description from ITP]
Observed: [YES — source / NOT OBSERVED — source / CANNOT CONFIRM]

### NCR Assessment
[For each NCR in scope:]
NCR reference: [from log]
Description: [from NCR document]
Status: [OPEN / CLOSED — date / CANNOT CONFIRM CLOSE-OUT]
Source: [document reference]

### Rectification Position
Rectification obligation: [CONTRACTOR — clause reference / EMPLOYER /
CANNOT CONFIRM — PC not retrieved]
DNP status: [ACTIVE / EXPIRED / CANNOT CONFIRM]
Instruction to rectify issued: [YES — reference / NOT FOUND]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any specification standard or testing
requirement from this section without first confirming it from the
retrieved project specification.*

**FIDIC Clause 7 — analytical reference:**
FIDIC Clause 7 (all books, both editions) requires that plant,
materials, and workmanship shall be of the kind described in the
contract and shall be fit for their intended purpose. Testing
requirements are as specified in the contract. The Contractor
must provide samples for testing as required. The Engineer
(Red/Yellow) or Employer's Representative (Silver) may reject
materials or workmanship that do not comply. Retrieve the
specific clause from Layer 2 and check the PC for amendments.

**Specification hierarchy — analytical reference:**
The project specification governs compliance requirements. Shop
drawings and submittals must comply with the specification — a
shop drawing approval does not override a specification requirement
unless the Engineer expressly approves a deviation via a formal
instruction or variation. An RFI response that appears to relax
a specification requirement without a formal variation instruction
creates ambiguity — flag where this pattern is identified in
retrieved documents.
