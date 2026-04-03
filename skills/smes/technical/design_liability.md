# Design Liability

**Skill type:** Contract-type-specific
Design responsibility allocation differs fundamentally across the
three FIDIC books. Under the Red Book, design is the Employer's
responsibility. Under the Yellow and Silver Books, design is the
Contractor's responsibility. The scope of the Contractor's design
obligation — and the standard of care that applies — must be
confirmed from the retrieved Particular Conditions, which may
modify the standard form allocation.
**Layer dependency:**
- Layer 1 — project documents: Particular Conditions (design
  responsibility clause); Employer's Requirements (Yellow/Silver);
  Contractor's design submittals; design change notices; RFI
  responses that affected design; defect records attributable to
  design; correspondence on design responsibility; governing law
  clause
- Layer 2 — reference standards: FIDIC Clause 4 and Clause 5
  (design by Contractor) for the confirmed book and edition;
  applicable decennial liability law (UAE Civil Code Art. 880,
  Saudi Building Code, Qatar Civil Code) where governing law
  confirmed
**Domain:** Technical & Construction SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when a query concerns which party bears design responsibility,
whether a defect is attributable to design or workmanship, whether
the Employer's Requirements are deficient, whether a Contractor
design obligation has been fulfilled, or whether decennial liability
is engaged. Apply when assessing the liability basis for any defect
claim where design involvement is asserted.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings first.

From the invoking orchestrator extract:
- Confirmed FIDIC book and edition
- Governing law as confirmed from retrieved contract documents
- Particular Conditions amendments to the design responsibility
  clause

**Book type is critical for this skill.** The entire design
liability framework is different between Red Book (Employer designs)
and Yellow/Silver Book (Contractor designs). If book type is
UNCONFIRMED: state CANNOT ASSESS design liability allocation.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The Particular Conditions — design responsibility clause,
  Clause 4 amendments, Clause 5 (Yellow/Silver) or equivalent
- The Employer's Requirements (Yellow/Silver) — the design brief
  that defines the Contractor's design obligation
- The Contractor's design submittals and design calculations
  (if in the warehouse)
- Design change notices and any correspondence modifying the
  design scope
- Defect or NCR records where design is cited as the cause
- RFI responses from the Engineer that may have modified design
  requirements
- The governing law clause

**If the Particular Conditions are not retrieved:**
State CANNOT CONFIRM design responsibility allocation. Do not apply
book-type default without PC confirmation — the PC may transfer
or modify design responsibility.

**If the Employer's Requirements are not retrieved (Yellow/Silver):**
State CANNOT CONFIRM the scope of the Contractor's design
obligation. The Employer's Requirements define what the Contractor
is required to design and to what performance standard.

### Layer 2 documents to retrieve (reference standards)

Call `search_chunks` to retrieve from Layer 2:
- FIDIC Clause 4.1 (Contractor's General Obligations) and
  Clause 5 (Design by Contractor — Yellow/Silver) for the
  confirmed book and edition
- Applicable decennial liability provision if governing law is
  UAE, Saudi Arabia, or Qatar — retrieve from Layer 2 if available

**Purpose:** To establish the standard FIDIC design responsibility
framework for comparison against the retrieved Particular Conditions.
The actual allocation is in the retrieved PC.

---

## Analysis workflow

### Step 1 — Confirm design responsibility allocation
*Contract-type-specific*

From the confirmed book type and the retrieved Particular Conditions:

**Red Book:**
Design is the Employer's responsibility. The Contractor's obligation
is to construct in accordance with the design provided by the
Employer (through the Engineer). The Contractor bears no design
liability for work constructed in accordance with the Employer's
design unless the Contractor has expressly undertaken design
responsibility for specific elements in the Particular Conditions.

**Yellow Book:**
The Contractor is responsible for design of the whole of the Works
unless the Particular Conditions carve out specific elements.
Confirm the scope of the Contractor's design obligation from the
retrieved Particular Conditions and Employer's Requirements.

**Silver Book:**
The Contractor bears full design and build responsibility. The
Contractor satisfies itself as to the Employer's Requirements and
takes full responsibility for the design. The standard of care
under the Silver Book standard form is fitness for purpose —
confirm whether the retrieved Particular Conditions modify this.

**In all cases:** Extract the actual design responsibility terms
from the retrieved Particular Conditions. Do not apply book-type
defaults without confirmation.

### Step 2 — Confirm the standard of care
*Contract-type-specific*

From the retrieved Particular Conditions:
- Does the Contractor's design obligation carry a fitness for
  purpose standard or a reasonable skill and care standard?
- Has the standard form standard of care been modified?

Under standard FIDIC Yellow Book (both editions), the Contractor's
design obligation is to exercise the degree of skill, care, and
diligence to be expected of a qualified engineer. Under the Silver
Book, the standard is effectively fitness for purpose — the
Contractor is responsible if the Works do not achieve the
performance requirements in the Employer's Requirements.

**The standard of care to apply is the one in the retrieved
Particular Conditions.** If the PC has not been retrieved: state
CANNOT CONFIRM the applicable standard of care.

### Step 3 — Assess the Employer's Requirements for deficiency
*Contract-type-specific — Yellow and Silver Book only*
*Not applicable to Red Book*

From the retrieved Employer's Requirements:
- Are the requirements clear, complete, and internally consistent?
- Do they contain any errors or ambiguities that a Contractor
  exercising reasonable skill and care at tender stage could not
  have identified?

Under FIDIC Yellow Book Clause 1.9, if the Contractor suffers
delay or cost due to an error in the Employer's Requirements that
an experienced contractor could not have discovered at tender stage,
the Contractor is entitled to EOT and Cost. This is a Yellow
Book-specific provision — confirm its existence and any amendment
in the retrieved Particular Conditions.

**Do not assess Employer's Requirements deficiency without the
retrieved document.** If the Employer's Requirements have not been
retrieved: state CANNOT ASSESS.

### Step 4 — Assess design submittals and approval status
*Contract-type-specific — Yellow and Silver Book only*
*Not applicable to Red Book*

From the retrieved design submittals and submittal register:
- Were the Contractor's design submittals reviewed and approved
  by the Engineer or Employer's Representative?
- Were any submittals rejected and resubmitted?
- Is the design approval status for the elements in question
  confirmed from retrieved documents?

**If a defect is attributed to a design that was reviewed and
approved by the Engineer without objection:** note the approval
from the retrieved documents. The forensic significance of Engineer
approval depends on whether it transfers responsibility — confirm
from the retrieved Particular Conditions.

### Step 5 — Assess defects attributable to design
*Contract-type-agnostic for the assessment framework;
contract-type-specific for the liability allocation*

From the retrieved defect records, NCR log, and any technical
reports:
- Is the defect described in the retrieved documents?
- Is the cause attributed to design, workmanship, materials, or
  a combination?
- Is the causal attribution in the retrieved documents or is it
  asserted in a claim without supporting technical evidence?

**Do not characterise a defect as design-caused or workmanship-
caused without a retrieved document that supports the
characterisation.** If a technical report is referenced but not
retrieved: call tools to search.

### Step 6 — Assess decennial liability engagement
*Contract-type-agnostic (applies to all book types)*
*Jurisdictionally specific — UAE, Saudi Arabia, Qatar only*

From the retrieved governing law clause:
- Is the governing law UAE law, Saudi law, or Qatar law?

If yes: decennial liability applies by operation of law regardless
of which FIDIC book governs and regardless of the contractual
defects liability period.

**Decennial liability conditions (from retrieved documents and
applicable law in Layer 2):**
- The defect must threaten the stability of the building or
  its structural integrity
- The 10-year period runs from handover (Taking-Over Certificate
  date — retrieve from Layer 1)
- Joint and several liability on the architect/designer and
  contractor
- Cannot be excluded by contract

**Flag decennial liability only where:**
(a) The governing law is confirmed as UAE, Saudi, or Qatar from
retrieved contract documents, AND
(b) The defect described in retrieved documents appears to relate
to structural integrity

**Do not flag decennial liability without both conditions being
confirmed from retrieved documents.**

---

## Classification and decision rules

**Design responsibility:**

Red Book, no PC amendment transferring design → EMPLOYER'S DESIGN
RESPONSIBILITY — Contractor liable for workmanship, not design
Red Book, PC amendment transferring specific design elements to
Contractor → SPLIT RESPONSIBILITY — state the elements from the
retrieved PC
Yellow/Silver Book, no PC amendment limiting scope → CONTRACTOR'S
DESIGN RESPONSIBILITY — full scope unless Employer's Requirements
limit it
Yellow/Silver Book, PC amendment limiting scope → PARTIAL
CONTRACTOR DESIGN RESPONSIBILITY — state the scope from retrieved PC
PC not retrieved → CANNOT CONFIRM design responsibility allocation

**Standard of care:**

Confirmed from retrieved PC → state the standard and source
Not confirmed (PC not retrieved) → CANNOT CONFIRM standard of care

**Defect causation:**

Design cause confirmed in retrieved technical documents →
DESIGN DEFECT — state the document and the finding
Workmanship cause confirmed in retrieved documents →
WORKMANSHIP DEFECT — state the document
Mixed or unclear from retrieved documents →
CAUSATION NOT DETERMINED FROM RETRIEVED DOCUMENTS — flag
Defect asserted in claim but not evidenced in retrieved records →
NOT INDEPENDENTLY CONFIRMED FROM RETRIEVED DOCUMENTS

**Decennial liability:**

Structural defect evidenced in retrieved documents AND governing
law confirmed as UAE/Saudi/Qatar → DECENNIAL LIABILITY POTENTIALLY
ENGAGED — flag; state the basis from retrieved documents
Defect not structural or governing law not confirmed →
DECENNIAL LIABILITY NOT ENGAGED or CANNOT ASSESS

---

## When to call tools

**Signal:** Particular Conditions design clause not retrieved
**Action:** `search_chunks` with query "design responsibility
Contractor Employer particular conditions clause 4 5";
`get_document` on PC document ID
**Look for:** The design responsibility clause and any standard
of care amendment

**Signal:** Employer's Requirements not retrieved (Yellow/Silver)
**Action:** `get_related_documents` with document type "Employer's
Requirements"; `search_chunks` with query "employer requirements
performance specification design brief"
**Look for:** The Employer's Requirements document

**Signal:** Technical report attributing defect cause referenced
but not retrieved
**Action:** `search_chunks` with query "[defect description]
technical report investigation cause"; `get_related_documents`
with document type "Technical Report", "Investigation Report"
**Look for:** The technical report establishing design or
workmanship causation

**Signal:** Design submittal approval status not confirmed
**Action:** `get_related_documents` with document type "Submittal
Register", "Design Submittal"; `search_chunks` with query
"design approved submittal [element description]"
**Look for:** The submittal register and approval status for
the element in question

**Signal:** Layer 2 FIDIC Clause 5 or decennial liability
provision not retrieved
**Action:** `search_chunks` with query "[FIDIC book] [edition]
clause 5 design Contractor"; `search_chunks` with query
"UAE Civil Code article 880 decennial liability"
**Look for:** Standard FIDIC design clause and applicable
decennial liability provision

---

## Always flag — regardless of query

1. **Book type-based design responsibility** — always state
   which party bears design responsibility and the source document.
   If UNCONFIRMED: flag that design liability cannot be assessed.

2. **Standard of care not confirmed from retrieved PC** — flag;
   state that the applicable standard (fitness for purpose vs
   reasonable skill and care) cannot be confirmed.

3. **Defect cause not established from retrieved documents** —
   flag any defect where causation is asserted in the claim but
   not supported by a retrieved technical document.

4. **Employer's Requirements deficiency (Yellow/Silver)** — flag
   any error or ambiguity in the retrieved Employer's Requirements
   that may engage Clause 1.9 entitlement.

5. **Decennial liability** — flag where structural defect and
   UAE/Saudi/Qatar governing law are both confirmed from retrieved
   documents; state the 10-year period and Taking-Over Certificate
   date.

---

## Output format

```
## Design Liability Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2 Reference Retrieved
[State whether FIDIC Clause 4/5 and decennial liability provisions
were retrieved. If not: state analytical knowledge applied.]

### Design Responsibility Allocation
FIDIC book: [from orchestrator findings]
Design responsibility: [EMPLOYER / CONTRACTOR — full scope /
CONTRACTOR — limited to [scope from PC] / SPLIT / CANNOT CONFIRM]
Source: [PC reference and clause]
Standard of care: [FITNESS FOR PURPOSE / REASONABLE SKILL AND CARE /
AMENDED — describe / CANNOT CONFIRM]
Source: [PC reference]

### Employer's Requirements Assessment (Yellow/Silver only)
Retrieved: [YES — reference / NOT FOUND / NOT APPLICABLE — Red Book]
Deficiency identified: [YES — describe and source / NONE IDENTIFIED /
CANNOT ASSESS — not retrieved]
Clause 1.9 engagement: [POTENTIALLY ENGAGED / NOT ENGAGED /
CANNOT ASSESS / NOT APPLICABLE — Red Book]

### Design Submittal Status (Yellow/Silver only)
[For each relevant design element:]
Element: [description]
Submittal reference: [from retrieved register / NOT FOUND]
Approval status: [APPROVED / REJECTED / UNDER REVIEW / NOT FOUND]
Source: [document reference]

### Defect Assessment
[For each defect in scope:]
**[Defect description]**
Evidenced in retrieved documents: [YES — source / NOT INDEPENDENTLY CONFIRMED]
Cause attributed in retrieved documents: [DESIGN / WORKMANSHIP /
MIXED / NOT DETERMINED FROM RETRIEVED DOCUMENTS]
Source of causation: [document reference / NOT FOUND]
Liability allocation: [EMPLOYER — Employer's design / CONTRACTOR —
Contractor's design / SHARED / CANNOT DETERMINE]

### Decennial Liability
Governing law confirmed: [YES — law and source / CANNOT CONFIRM]
Structural defect evidenced: [YES — describe and source / NOT EVIDENCED /
NOT ASSESSABLE]
Taking-Over Certificate date: [from retrieved TOC / NOT FOUND]
Assessment: [DECENNIAL LIABILITY POTENTIALLY ENGAGED / NOT ENGAGED /
CANNOT ASSESS]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any design liability position or
standard of care from this section without first confirming the
applicable terms from retrieved project documents.*

**FIDIC design responsibility — analytical reference:**
Red Book: Contractor constructs per Employer's design. No design
liability unless PC transfers specific elements. Yellow Book:
Contractor designs and constructs per Employer's Requirements.
Standard is reasonable skill and care unless PC amends. Silver Book:
Contractor takes full responsibility for design to meet the
Employer's Requirements — effectively fitness for purpose. The PC
may modify any of these positions — retrieve from Layer 1 first.

**Decennial liability — analytical reference:**
UAE Civil Code Art. 880, Saudi Building Code Implementing
Regulations, and Qatar Civil Code all impose 10-year joint liability
on contractors and architects for structural defects. This runs
in parallel with the FIDIC DNP and cannot be excluded. It applies
to structural defects only — defects that threaten stability.
The 10-year period runs from the date of handover (Taking-Over
Certificate). Confirm the governing law and the Taking-Over
Certificate date from Layer 1 before applying this framework.

**Yellow Book Clause 1.9 — analytical reference:**
If the Contractor suffers delay or cost due to an error in the
Employer's Requirements that an experienced contractor could not
reasonably have discovered at tender stage, the Contractor is
entitled to EOT and Cost. This is a Yellow Book-specific provision.
The Contractor bears the risk of errors discoverable at tender.
The threshold is what an experienced contractor would have
identified — a professional standard assessed from the retrieved
Employer's Requirements.
