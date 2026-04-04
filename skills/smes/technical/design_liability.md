# Design Liability

**Skill type:** Mixed
- Contract-type-specific: design responsibility allocation and the
  standard of care differ fundamentally between standard forms —
  some place design with the employer, others with the contractor,
  others split it; the allocation must be retrieved from the
  governing standard in Layer 2b and confirmed from the amendment
  document before any liability position is stated
- Contract-type-agnostic: the framework for assessing defect
  causation (design vs workmanship), the review of design submittals,
  and the assessment of the design brief for deficiency apply
  regardless of which standard form governs
**Layer dependency:**
- Layer 1 — project documents: amendment document (design
  responsibility clause, standard of care provisions); Employer's
  Requirements or equivalent design brief (where contractor designs);
  Contractor's design submittals and calculations; design change
  notices; RFI responses that affected design requirements; defect
  records and technical investigation reports; governing law clause
- Layer 2b — reference standards: design responsibility provisions
  for the confirmed standard form; standard of care provisions;
  applicable law (if ingested)
- Layer 2a — internal standards: design authority policies, design
  review procedures (if applicable)
**Domain:** Technical & Construction SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when a query concerns which party bears design responsibility,
whether a defect is attributable to design or workmanship, whether
the design brief or Employer's Requirements are deficient, whether
a contractor design obligation has been fulfilled, or whether
statutory or long-stop liability for structural defects is engaged.
Apply when assessing the liability basis for any defect claim where
design involvement is asserted.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings first.

From the invoking orchestrator extract:
- Confirmed standard form and version
- Governing law as confirmed from retrieved contract documents
- Amendment document provisions on design responsibility

**Design responsibility allocation is contract-form-specific.**
The governing standard establishes the default allocation; the
amendment document may modify it. If neither has been retrieved:
state CANNOT ASSESS design liability allocation — do not apply
any assumed position.

**If the standard form type is not confirmed from retrieved
documents:** State CANNOT CONFIRM design responsibility allocation.
Do not proceed with a design liability assessment on an assumed
standard form.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The amendment document — design responsibility clause, standard
  of care provisions, and any clause addressing errors in the
  design brief
- The Employer's Requirements or equivalent design brief — where
  the contractor bears design responsibility, this document defines
  the scope and performance standard of the design obligation
- The Contractor's design submittals and calculations (if in the
  warehouse)
- Design change notices and correspondence modifying design scope
- Defect records and technical investigation reports where design
  is cited as a cause
- RFI responses from the contract administrator that modified
  design requirements
- The governing law clause

**If the amendment document is not retrieved:**
State CANNOT CONFIRM design responsibility allocation and
CANNOT CONFIRM the applicable standard of care. Confidence cap:
GREY. The amendment document may transfer, limit, or modify the
standard form default — applying the standard form default without
amendment document confirmation is not permitted.

**If the Employer's Requirements or design brief are not retrieved
(where contractor bears design responsibility):**
State CANNOT CONFIRM the scope of the contractor's design
obligation. This document defines what the contractor is required
to design and to what performance standard.

### Layer 2b documents to retrieve (reference standards)

Call `search_chunks` with `layer_type = '2b'` to retrieve:
- Design responsibility provisions for the confirmed standard form
  (search by subject matter: "design responsibility contractor
  employer obligation")
- Standard of care provisions (search by subject matter: "standard
  of care fitness for purpose reasonable skill care design")
- Applicable law provisions if ingested (search by subject matter:
  "[governing law name] construction design liability structural
  defects")

**Purpose:** To establish the standard form design responsibility
framework and standard of care for structural comparison against
the retrieved amendment document. The actual allocation and
standard to apply is in the retrieved contract documents.

**If the governing standard form is not retrieved from Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE for the
design responsibility and standard of care provisions. Confidence
cap: AMBER. State which analytical steps are affected and proceed
only with what is confirmed from Layer 1.

---

## Analysis workflow

### Step 1 — Confirm design responsibility allocation
*Contract-type-specific*

From the retrieved Layer 2b standard form provisions and the
retrieved amendment document:

Identify the standard form's default allocation: does the governing
standard place design responsibility with the employer, the
contractor, or split it between them? Extract this from the Layer 2b
retrieval.

Identify amendments: does the retrieved amendment document modify
the standard form allocation? Apply the amendment document position,
not the standard form default, where an amendment is confirmed.

State the confirmed allocation and its source. If Layer 2b standard
form not retrieved: state CANNOT CONFIRM — STANDARD FORM NOT IN
WAREHOUSE. If amendment document not retrieved: state CANNOT CONFIRM
— AMENDMENT POSITION UNKNOWN.

### Step 2 — Confirm the standard of care
*Contract-type-specific*

From the retrieved Layer 2b standard form and the retrieved
amendment document: what standard of care applies to the
contractor's design obligation — fitness for purpose, reasonable
skill and care, or another standard? Has the standard form
standard been modified by the amendment document?

**The standard of care to apply is the one confirmed from the
retrieved documents.** If the amendment document has not been
retrieved: CANNOT CONFIRM — confidence cap GREY. If Layer 2b not
retrieved: CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE —
confidence cap AMBER.

### Step 3 — Assess the design brief (where contractor designs)
*Applies where contractor bears design responsibility*
*Not applicable where employer bears full design responsibility*

From the retrieved design brief or Employer's Requirements:
- Are the requirements clear, complete, and internally consistent?
- Do they contain errors or ambiguities that an experienced
  contractor exercising professional skill could not have
  identified at tender stage?

Check whether the retrieved amendment document contains a
provision addressing contractor entitlement where errors in the
design brief cause delay or cost. Extract from retrieved documents;
do not apply any standard form default on this point without
retrieved confirmation.

**Do not assess design brief deficiency without the retrieved
document.** If the design brief has not been retrieved: state
CANNOT ASSESS.

### Step 4 — Assess design submittals and approval status
*Applies where contractor bears design responsibility*

From the retrieved design submittals and submittal register:
- Were the contractor's design submittals reviewed and approved
  by the contract administrator?
- Were any submittals rejected and resubmitted?
- Is the approval status for the elements in question confirmed
  from retrieved documents?

If a defect is attributed to a design that was reviewed and
approved without objection: note the approval from the retrieved
documents. Whether approval transfers or shares responsibility
depends on the retrieved amendment document — state what the
amendment document says; do not assume.

### Step 5 — Assess defects attributable to design
*Contract-type-agnostic for the assessment framework;
contract-type-specific for the liability allocation*

From the retrieved defect records, NCR log, and technical
investigation reports:
- Is the defect described in the retrieved documents?
- Is the cause attributed to design, workmanship, materials, or
  a combination?
- Is the causal attribution in a retrieved technical document or
  is it asserted in a claim without supporting evidence?

**Do not characterise a defect as design-caused or workmanship-
caused without a retrieved document that supports the
characterisation.** If a technical report is referenced but not
retrieved: call tools to search.

### Step 6 — Assess jurisdiction-specific statutory liability
*Applies where applicable law retrieved from Layer 2b*

From the retrieved governing law clause and Layer 2b:
- Has applicable law been ingested in Layer 2b for the confirmed
  governing law?
- Does the retrieved applicable law impose statutory liability for
  structural defects beyond the contractual defects period?
- If yes: does the defect evidenced in the retrieved documents
  appear to engage that liability — structural defect, within the
  liability period from the confirmed handover date?

**Flag statutory structural liability only where:**
(a) Governing law confirmed from retrieved contract documents, AND
(b) Applicable law ingested in Layer 2b and retrieved, AND
(c) Structural defect evidenced in retrieved documents.

**If applicable law has not been ingested in Layer 2b:**
State CANNOT CONFIRM — APPLICABLE LAW NOT IN WAREHOUSE. Do not
characterise statutory liability from training knowledge.

---

## Classification and decision rules

**Design responsibility:**

Layer 2b standard form and amendment document both retrieved →
state confirmed allocation and source document
Layer 2b retrieved, amendment document not retrieved →
CANNOT CONFIRM — AMENDMENT POSITION UNKNOWN; confidence cap GREY
Amendment document retrieved, Layer 2b not retrieved →
CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE; confidence cap AMBER
Neither retrieved → CANNOT CONFIRM; confidence cap GREY

**Standard of care:**

Confirmed from retrieved documents → state the standard and source
Amendment document not retrieved → CANNOT CONFIRM; confidence cap GREY
Standard form not in Layer 2b → CANNOT CONFIRM — STANDARD FORM
NOT IN WAREHOUSE; confidence cap AMBER

**Defect causation:**

Design cause confirmed in retrieved technical documents →
DESIGN DEFECT — state the document and the finding
Workmanship cause confirmed in retrieved documents →
WORKMANSHIP DEFECT — state the document
Mixed or unclear → CAUSATION NOT DETERMINED FROM RETRIEVED DOCUMENTS
Defect asserted but not evidenced → NOT INDEPENDENTLY CONFIRMED
FROM RETRIEVED DOCUMENTS

**Statutory structural liability:**

Structural defect evidenced AND governing law confirmed AND
applicable law retrieved from Layer 2b →
STATUTORY STRUCTURAL LIABILITY POTENTIALLY ENGAGED — flag; state
the basis from retrieved documents
Governing law confirmed but applicable law not in Layer 2b →
CANNOT CONFIRM — APPLICABLE LAW NOT IN WAREHOUSE

---

## When to call tools

**Signal:** Amendment document design responsibility clause not
retrieved
**Action:** `search_chunks` with query "design responsibility
contractor employer amendment particular conditions clause";
`get_document` on amendment document ID
**Look for:** The design responsibility clause and any standard
of care amendment

**Signal:** Design brief or Employer's Requirements not retrieved
(where contractor designs)
**Action:** `get_related_documents` with document type "Employer's
Requirements", "Design Brief", "Performance Specification";
`search_chunks` with query "employer requirements performance
specification design brief scope"
**Look for:** The design brief defining the contractor's design
obligation

**Signal:** Technical report attributing defect cause referenced
but not retrieved
**Action:** `search_chunks` with query "[defect description]
technical report investigation cause"; `get_related_documents`
with document type "Technical Report", "Investigation Report"
**Look for:** The technical report establishing design or
workmanship causation

**Signal:** Layer 2b design responsibility provisions not retrieved
**Action:** `search_chunks` with `layer_type = '2b'` and query
"design responsibility contractor employer standard of care
fitness for purpose"
**Look for:** Standard form design responsibility and standard
of care provisions

**Signal:** Applicable law for statutory structural liability not
retrieved
**Action:** `search_chunks` with `layer_type = '2b'` and query
"[governing law name] structural defects statutory liability
construction long stop"
**Look for:** Applicable law provisions on statutory structural
liability

---

## Always flag — regardless of query

1. **Design responsibility not confirmed from retrieved documents**
   — flag; state that design liability cannot be assessed and what
   is missing from the warehouse.

2. **Governing standard not in Layer 2b** — flag; state that the
   design responsibility framework and standard of care cannot be
   confirmed from the warehouse and that confidence is capped at AMBER.

3. **Standard of care not confirmed from retrieved documents** —
   flag; state that whether fitness for purpose or reasonable skill
   and care applies cannot be confirmed.

4. **Defect cause not established from retrieved documents** —
   flag any defect where causation is asserted in a claim but not
   supported by a retrieved technical document.

5. **Design brief deficiency where contractor bears design
   responsibility** — flag any error or ambiguity in the retrieved
   design brief that may engage an entitlement provision in the
   retrieved amendment document.

6. **Statutory structural liability** — flag where structural defect
   evidenced AND governing law confirmed AND applicable law retrieved
   from Layer 2b; state the liability period and handover date from
   retrieved documents.

---

## Output format

```
## Design Liability Assessment

### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [standard form name — or NOT RETRIEVED]
Layer 2b provisions retrieved: [design responsibility, standard of
care, applicable law — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE]
Layer 2a source: [policy name — or NOT RETRIEVED / NOT APPLICABLE]
Layer 1 primary document: [amendment document name and reference —
or NOT RETRIEVED]
Layer 1 design brief: [Employer's Requirements or equivalent —
or NOT RETRIEVED / NOT APPLICABLE]
Provisions CANNOT CONFIRM: [list — or NONE]

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2b Reference Retrieved
[State whether design responsibility provisions, standard of care
provisions, and applicable law were retrieved from Layer 2b.
If not: state CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE
and list which analysis steps are affected. Confidence cap: AMBER.]

### Design Responsibility Allocation
Standard form retrieved: [YES — standard form name / NOT IN WAREHOUSE]
Standard form default: [EMPLOYER DESIGN / CONTRACTOR DESIGN /
SPLIT — describe / CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE]
Amendment document retrieved: [YES — reference / NOT RETRIEVED]
Amendment to design responsibility: [UNAMENDED / AMENDED — describe /
CANNOT CONFIRM — amendment document not retrieved]
Confirmed allocation: [EMPLOYER / CONTRACTOR — full scope /
CONTRACTOR — limited to [scope from amendment] /
SPLIT — describe / CANNOT CONFIRM]
Source: [document reference]
Standard of care: [confirmed standard and source /
CANNOT CONFIRM — amendment document not retrieved /
CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE]
Confidence cap: [GREEN / AMBER — Layer 2b not retrieved /
GREY — amendment document not retrieved]

### Design Brief Assessment (where contractor designs)
Design brief retrieved: [YES — reference / NOT FOUND /
NOT APPLICABLE — employer designs]
Deficiency identified: [YES — describe and source /
NONE IDENTIFIED / CANNOT ASSESS — not retrieved]
Amendment document entitlement provision: [CONFIRMED — describe /
NOT FOUND / NOT APPLICABLE]

### Design Submittal Status (where contractor designs)
[For each relevant design element:]
Element: [description]
Submittal reference: [from retrieved register / NOT FOUND]
Approval status: [APPROVED / REJECTED / UNDER REVIEW / NOT FOUND]
Source: [document reference]

### Defect Assessment
[For each defect in scope:]
**[Defect description]**
Evidenced in retrieved documents: [YES — source /
NOT INDEPENDENTLY CONFIRMED]
Cause attributed in retrieved documents: [DESIGN / WORKMANSHIP /
MIXED / NOT DETERMINED FROM RETRIEVED DOCUMENTS]
Source of causation: [document reference / NOT FOUND]
Liability allocation: [EMPLOYER / CONTRACTOR / SHARED /
CANNOT DETERMINE]

### Statutory Structural Liability
Governing law confirmed: [YES — law and source / CANNOT CONFIRM]
Applicable law in Layer 2b: [YES — provisions retrieved /
CANNOT CONFIRM — APPLICABLE LAW NOT IN WAREHOUSE]
Structural defect evidenced: [YES — describe and source /
NOT EVIDENCED / NOT ASSESSABLE]
Handover date: [from retrieved completion certificate / NOT FOUND]
Assessment: [STATUTORY STRUCTURAL LIABILITY POTENTIALLY ENGAGED /
NOT ENGAGED / CANNOT ASSESS]
Source: [Layer 2b applicable law reference]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any design responsibility position,
standard of care, or statutory liability conclusion from this section
without first confirming the applicable terms from retrieved project
documents and Layer 2b.*

**Design responsibility allocation — analytical reference:**
Standard forms differ fundamentally in how they allocate design
responsibility. Employer-design forms require the contractor to
construct in accordance with a design provided by the employer.
Contractor-design forms (design-and-build) require the contractor
to design to meet the employer's requirements or performance
specification. Hybrid forms assign specific design elements to the
contractor. In all cases, the amendment document may modify the
standard form default — the actual allocation must be retrieved
from the contract documents, not assumed from the standard form type.

**Standard of care — analytical reference:**
Design obligations typically carry either a fitness for purpose
standard (the design must achieve the required outcome regardless
of how the designer performed) or a reasonable skill and care
standard (the designer must perform to professional standards).
The distinction is significant: fitness for purpose is an absolute
standard; reasonable skill and care requires assessment of
professional conduct. The applicable standard depends on the
governing standard form and any amendment to it. Retrieve before
applying.

**Statutory structural liability — analytical reference:**
Many legal systems impose statutory long-stop liability on
contractors and designers for structural defects, operating in
parallel with the contractual defects liability period. The scope
(typically structural defects that threaten stability), duration
(varies by jurisdiction and legislation), and parties liable vary
by applicable law. This liability typically cannot be excluded by
contract. The governing law must be confirmed from the retrieved
contract documents, and the applicable law provision must be
retrieved from Layer 2b before this framework is applied.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies to
any contract form. All characterisations grounded in retrieved warehouse
documents only.*
