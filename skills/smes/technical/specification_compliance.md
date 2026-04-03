# Specification Compliance

**Skill type:** Mixed
- Contract-type-agnostic: the method for assessing specification
  compliance — retrieve the specification requirement, retrieve the
  test or inspection record, compare — applies regardless of standard
  form or version
- Contract-type-specific: the contractual consequences of non-
  compliance and the party responsible for rectification must be
  confirmed from the retrieved governing standard in Layer 2b and
  the amendment document
**Layer dependency:**
- Layer 1 — project documents: project specification (technical
  sections); material approval submittals; material test certificates;
  inspection and test plans (ITP); inspection request forms; test
  reports; NCR records; as-built records; amendment document
  (quality, testing, and defects clauses); Contract Data or
  equivalent (defects liability period)
- Layer 2b — reference standards: quality, testing, and defects
  provisions for the confirmed standard form; referenced testing
  standards (BS, ASTM, ISO, EN, or others) if ingested in Layer 2b
- Layer 2a — internal standards: quality management procedures,
  material approval processes (if applicable)
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
- Confirmed standard form and version
- Any amendment document provisions on testing or defects

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The project specification — the technical section relevant to
  the element under assessment
- The material approval submittal for the element (if applicable)
- The test certificate(s) for the element
- The inspection and test plan (ITP) for the work stage
- The inspection request form and inspection record
- The NCR (if a non-conformance has been raised)
- The amendment document — testing and defects clauses

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

### Layer 2b documents to retrieve (reference standards)

Call `search_chunks` with `layer_type = '2b'` to retrieve:
- Quality, testing, and materials obligations for the confirmed
  standard form (search by subject matter: "quality workmanship
  materials testing obligation rejection")
- Defects provisions for the confirmed standard form (search
  by subject matter: "defects liability rectification defects
  period")
- Referenced testing standards (BS, ASTM, ISO, EN) if ingested
  in Layer 2b and referenced in the retrieved specification
  (search by standard name and number)

**Purpose:** To establish the standard form quality and defects
framework, and to access the referenced testing standards where
available. The project specification governs compliance
requirements — the testing standards provide the methodology.

**If the governing standard form is not retrieved from Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE for the
quality and defects provisions. Confidence cap: AMBER. The
compliance assessment against the specification proceeds
regardless — Layer 2b is needed only for the contractual
consequence assessment.

---

## Analysis workflow

### Step 1 — Identify the specification requirement
*Contract-type-agnostic*

From the retrieved project specification:
- Identify the specific requirement for the element under assessment
- State the requirement exactly as it appears in the retrieved
  specification: the material standard, the test standard, the
  acceptance criteria, and any method of measurement
- Identify the testing standard referenced and the edition year
  if stated

**Do not state any specification requirement without the retrieved
specification document as the source.** If the specification has
not been retrieved: state CANNOT CONFIRM the applicable requirement.

### Step 2 — Identify the applicable test or inspection record
*Contract-type-agnostic*

From the retrieved documents, identify:
- The test certificate(s) for the element — state the document
  reference, date, test type, test standard applied, result, and
  pass/fail determination
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

**State both values and both source documents.** Do not assess
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

State the NCR reference, description, and status from the retrieved
document. Do not characterise an NCR as closed without a retrieved
close-out record.

### Step 7 — Assess the rectification obligation
*Contract-type-specific*

From the retrieved amendment document and Layer 2b provisions:
- Who is obliged to rectify a non-conformance: the contractor
  (workmanship or materials failure) or the employer (design
  deficiency)?
- Is the rectification obligation within the defects liability
  period or has the period expired?
- Has a formal instruction to rectify been issued?

**The rectification obligation and the defects liability period
to apply are from the retrieved amendment document and Contract
Data.** Do not apply any standard form period without retrieved
confirmation. If Layer 2b not retrieved: state CANNOT CONFIRM —
STANDARD FORM NOT IN WAREHOUSE.

---

## Classification and decision rules

**Specification compliance:**

Test result retrieved AND specification requirement retrieved AND
result meets the requirement → COMPLIANT — state both values
and sources
Test result retrieved AND specification requirement retrieved AND
result does not meet the requirement → NON-COMPLIANT — flag;
state both values and sources
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

Hold point observed and recorded in retrieved ITP or inspection
record → HOLD POINT OBSERVED
Hold point not observed before work proceeded (evidenced from
retrieved site diary or inspection record) → HOLD POINT NOT
OBSERVED — flag
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

**Signal:** Layer 2b quality or defects provisions not retrieved
**Action:** `search_chunks` with `layer_type = '2b'` and query
"[standard form name] quality workmanship materials testing
defects liability rectification"
**Look for:** Standard form quality and defects provisions

**Signal:** Referenced testing standard not in Layer 2b
**Action:** `search_chunks` with `layer_type = '2b'` and query
"[standard name e.g. BS, ASTM, ISO] [number] [subject]"
**Look for:** The referenced testing standard if ingested

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

5. **Open NCR at handover or still open in the warehouse** —
   flag; state the NCR reference and the forensic implication for
   the defects liability position.

6. **Governing standard not in Layer 2b** — flag; state that the
   rectification obligation and defects liability framework cannot
   be confirmed from the warehouse and that confidence is capped
   at AMBER for the contractual consequence assessment.

---

## Output format

```
## Specification Compliance Assessment

### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [standard form name — or NOT RETRIEVED]
Layer 2b provisions retrieved: [quality/workmanship/testing,
defects liability — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE]
Layer 2a source: [policy name — or NOT RETRIEVED / NOT APPLICABLE]
Layer 1 primary document: [project specification reference —
or NOT RETRIEVED]
Layer 1 amendment document: [name — or NOT RETRIEVED]
Provisions CANNOT CONFIRM: [list — or NONE]

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2b Reference Retrieved
[State whether quality/workmanship/testing and defects liability
provisions were retrieved from Layer 2b. State whether any
referenced testing standards were retrieved. If not: state
CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE and list affected
analysis steps. Confidence cap: AMBER for contractual consequence
assessment.]

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
Rectification obligation: [CONTRACTOR — source document /
EMPLOYER / CANNOT CONFIRM — amendment document not retrieved /
CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE]
Defects liability period status: [ACTIVE / EXPIRED /
CANNOT CONFIRM — dates not confirmed]
Instruction to rectify issued: [YES — reference / NOT FOUND]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any specification standard, testing
requirement, or rectification obligation from this section without
first confirming it from the retrieved project specification and
Layer 2b.*

**Quality and workmanship obligations — analytical reference:**
Standard forms consistently require that plant, materials, and
workmanship comply with the contract. The contract administrator
may reject materials or workmanship that do not comply. Testing
requirements are as specified in the project specification. The
contractor must provide samples, test certificates, and
certification as required. The specific testing and rejection
mechanisms are in the standard form and the amendment document —
retrieve before applying.

**Specification hierarchy — analytical reference:**
The project specification governs compliance requirements.
Shop drawings and submittals must comply with the specification —
a shop drawing approval does not override a specification
requirement unless the contract administrator expressly approves
a deviation via a formal instruction or variation. An RFI response
that appears to relax a specification requirement without a formal
variation instruction creates ambiguity — flag where this pattern
is identified in retrieved documents and cross-reference the
rfi_and_submittal_review findings.

**Testing standards — analytical reference:**
Test certificates must reference the same testing standard as the
specification. If the specification requires testing to a specific
standard (e.g. a particular BS, ASTM, ISO, or EN standard and
edition) and the test certificate references a different standard,
the test result cannot be used to confirm specification compliance.
This is a common quality documentation failure — flag when
identified from retrieved documents.
