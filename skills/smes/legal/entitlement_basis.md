# Entitlement Basis

**Skill type:** Contract-type-specific
The entitlement framework differs materially across Red, Yellow, and
Silver Books due to different risk allocation and design responsibility.
The specific FIDIC sub-clause that supports a claimed entitlement,
whether that sub-clause has been amended by Particular Conditions, and
what it requires the claimant to demonstrate — all of these are
book-specific and project-specific.
**Layer dependency:**
- Layer 1 — project documents: the claim document; Particular
  Conditions (entitlement clauses, Employer Risk Events, cost recovery
  provisions); Contract Agreement; relevant correspondence
- Layer 2 — reference standards: FIDIC General Conditions for the
  confirmed book and edition — the specific sub-clauses cited in the
  claim and the relevant entitlement framework
**Domain:** Legal & Contractual SME
**Invoked by:** Legal orchestrator

---

## When to apply this skill

Apply when a query concerns whether a Contractor or Employer has a
contractual entitlement to additional time, cost, or both — including
EOT claims, prolongation cost claims, variation entitlements,
unforeseeable conditions claims, suspension claims, or termination
compensation. Also apply when assessing whether the FIDIC clause cited
in a claim document actually supports the relief claimed, or whether
Particular Conditions amendments have modified or removed the
entitlement.

---

## Before you begin

### Foundational requirements
Read contract_assembly and notice_and_instruction_compliance findings
first.

From contract_assembly:
- Confirmed book type and edition — required to apply the correct
  entitlement framework
- Particular Conditions amendments — especially any that modify
  entitlement clauses, narrow Employer Risk Events, restrict cost
  recovery, or remove specific heads of claim

From notice_and_instruction_compliance:
- Time bar status for any notice corresponding to this claim
- If notice is POTENTIALLY TIME-BARRED: flag this at the start of
  the entitlement assessment. The entitlement analysis is secondary
  to the notice position. Proceed with entitlement assessment and
  note the time bar caveat throughout.

**If book type is UNCONFIRMED:** State CANNOT ASSESS entitlement
basis. The entitlement framework is book-specific — analysis without
confirmed book type will produce unreliable output.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The claim document (EOT claim, variation claim, or other) — required
  to identify the FIDIC clause cited and the relief claimed
- The Particular Conditions — required to confirm whether the cited
  clause has been amended and what the actual entitlement terms are
- The General Conditions — if not in Layer 1, retrieve from Layer 2
- Any Engineer's determination or Employer's Representative response
  to the claim
- Supporting correspondence and records referenced in the claim

**If the claim document is not retrieved:** State CANNOT ASSESS
entitlement basis. A claim document must be present to assess.

**If the Particular Conditions are not retrieved:** State CANNOT
CONFIRM whether the entitlement clause cited in the claim has been
amended. Do not assess entitlement against the General Conditions
text without confirming the Particular Conditions position.

### Layer 2 documents to retrieve (reference standards)

After confirming book type and the specific FIDIC sub-clause cited in
the claim, call `search_chunks` to retrieve from Layer 2:
- The specific sub-clause cited in the claim (for the confirmed book
  and edition) — to establish what the standard text says
- The entitlement clause (Clause 8.4/8.5 for EOT; Clause 13 for
  variations; the relevant sub-clause for the specific event type)

**Purpose:** To compare what the standard FIDIC clause says against
what the Particular Conditions say for this project. The entitlement
terms to apply are those in the retrieved Particular Conditions (as
amended), not the Layer 2 standard text. Layer 2 is the comparison
baseline only.

---

## Analysis workflow

### Step 1 — Identify the claimed entitlement and the clause cited
*Contract-type-agnostic*

From the retrieved claim document, identify:
- What relief is claimed: EOT only / Cost only / EOT + Cost /
  EOT + Cost + Profit / Termination compensation / Other
- Which FIDIC sub-clause is cited as the entitlement basis
- The nature of the event giving rise to the claim (as described
  in the claim document)

**Do not characterise the claim beyond what the retrieved document
states.** If the claim document does not cite a FIDIC sub-clause:
note this as a deficiency in the claim — a claim without a stated
contractual basis is procedurally deficient under both editions.

### Step 2 — Confirm the entitlement clause from the Particular Conditions
*Contract-type-specific*

From the retrieved Particular Conditions, confirm:
- Whether the sub-clause cited in the claim exists in the project
  contract (i.e. has not been deleted by Particular Conditions)
- Whether the sub-clause has been amended and if so how
- What relief the sub-clause as amended actually provides

**The entitlement clause to apply is the version in the retrieved
Particular Conditions.** If the Particular Conditions contain an
amendment to the cited sub-clause: apply the amended version and
state the amendment. If no amendment is found AND the Particular
Conditions have been fully retrieved: note that the General Conditions
version appears to apply — citing the Particular Conditions as source.
If the Particular Conditions have not been retrieved: state CANNOT
CONFIRM the applicable entitlement terms.

### Step 3 — Assess whether the event qualifies under the confirmed clause
*Contract-type-specific*

Apply the entitlement framework for the confirmed book type.
The key distinction is between the three books:

**Red Book (Construction):**
Design responsibility is the Employer's. Contractor Risk Events are
primarily execution-related. Employer Risk Events are defined in the
clause — retrieve from Layer 1 (PC as amended) and Layer 2 (standard
text for comparison). Do not characterise an event as an Employer
Risk Event unless it falls within the events as stated in the
retrieved Particular Conditions (or the confirmed unamended General
Conditions).

**Yellow Book (Plant & Design-Build):**
Design responsibility is the Contractor's. Contractor's design errors
are not Employer Risk Events. The Employer's Requirements deficiency
ground (Clause 1.9) may provide entitlement where a design failure
was unforeseeable at tender — this is Yellow Book specific and does
not exist in the Red Book. Check whether Clause 1.9 applies only
after retrieving the relevant clause from Layer 2 and confirming
any PC amendment from Layer 1.

**Silver Book (EPC/Turnkey):**
The Contractor bears most risk. The Employer Risk Events are
significantly narrower than in the Red or Yellow Book. Unforeseeable
physical conditions are not an Employer Risk Event in the standard
Silver Book — the Contractor bears this risk. Do not apply Red or
Yellow Book Employer Risk Event lists to a Silver Book project.

**For all books:** Retrieve the Employer Risk Event list from the
confirmed Particular Conditions (as amended). Do not apply the
General Conditions list without confirming it is unamended.

### Step 4 — Assess cost entitlement separately from time entitlement
*Contract-type-agnostic principle / contract-type-specific application*

EOT entitlement and Cost entitlement are separate assessments under
FIDIC. An event may entitle the Contractor to EOT without Cost (Neutral
Event), or to both EOT and Cost (Employer Risk Event), or to EOT and
Cost and Profit (specific clauses only). Profit is recoverable only
where the entitlement sub-clause expressly provides for it.

For each claimed head (time, cost, profit):
- Confirm the sub-clause cited in the claim
- Confirm whether that sub-clause provides for that head in the
  retrieved Particular Conditions
- If Profit is claimed and the sub-clause provides for Cost only:
  flag — Profit is not recoverable under that clause as retrieved

### Step 5 — Assess the required proof elements
*Contract-type-agnostic*

Every FIDIC entitlement sub-clause requires the claimant to demonstrate
specific elements to establish entitlement. From the retrieved Layer 2
clause text (compared against the Layer 1 Particular Conditions
version), identify the required proof elements.

For each element:
- Identify it from the retrieved clause text
- Assess whether the retrieved claim documents provide evidence for it
- Classify: DEMONSTRATED / NOT DEMONSTRATED / CANNOT ASSESS (evidence
  not in warehouse)

Do not characterise proof elements as demonstrated on the basis of
what the claim document asserts — assess against independent evidence
in the retrieved documents.

### Step 6 — Assess the Engineer's determination
*Contract-type-specific — Red Book and Yellow Book only*

If an Engineer's determination has been retrieved:
- Does the determination address the entitlement claimed?
- What position has the Engineer taken on the entitlement basis?
- Is the Engineer's position consistent with the retrieved clause text?
- Does the determination reveal any Employer consent issues (from
  engineer_identification findings)?

If no determination has been retrieved after searching:
State CANNOT ASSESS the Engineer's position on entitlement.

---

## Classification and decision rules

**Entitlement clause confirmed:**

Sub-clause exists and unamended in retrieved PC → clause governs as
per General Conditions standard text (cite PC as source of
confirmation)
Sub-clause amended in retrieved PC → apply amended version — state the
amendment and its effect
Sub-clause deleted in retrieved PC → NO CONTRACTUAL BASIS for this
claim under the cited clause — flag; state the deletion and source
Particular Conditions not retrieved → CANNOT CONFIRM entitlement
clause — do not proceed with entitlement assessment beyond flagging
this gap

**Event qualification:**

Event falls within Employer Risk Events as stated in retrieved PC →
IN SCOPE — proceed with proof element assessment
Event does not fall within Employer Risk Events as stated in retrieved
PC → OUT OF SCOPE under cited clause — flag; state which retrieved
clause provision excludes the event
Event is a Neutral Event under retrieved PC → EOT ONLY — no Cost
entitlement under this clause
Cannot determine event classification because PC not retrieved →
CANNOT CLASSIFY

**Proof elements:**

All required elements demonstrated in retrieved documents →
ENTITLEMENT ESTABLISHED FROM RETRIEVED DOCUMENTS
Some elements demonstrated, some absent from warehouse →
PARTIALLY DEMONSTRATED — state which elements are established and
which are not, and what documents would be needed
No proof elements demonstrated in retrieved documents →
CANNOT ESTABLISH ENTITLEMENT FROM WAREHOUSE DOCUMENTS

---

## When to call tools

**Signal:** Claim cites a sub-clause but the Particular Conditions
amendment to that sub-clause has not been retrieved
**Action:** `get_document` on the Particular Conditions document ID;
`search_chunks` with query "clause [number] particular conditions
[subject matter]"
**Look for:** The amendment to the cited clause in the PC

**Signal:** Claim references supporting documents (records, reports,
correspondence) that have not been retrieved
**Action:** `get_related_documents` with the document types referenced;
`search_chunks` with the event description and date range
**Look for:** The supporting documents evidencing the claimed event
and its impact

**Signal:** Layer 2 FIDIC clause for the cited sub-clause has not
been retrieved
**Action:** `search_chunks` with query "[FIDIC book name] [edition]
clause [number] [subject]"
**Look for:** The standard FIDIC text for the cited sub-clause for
comparison against the PC version

**Signal:** Engineer's determination has been referenced in the
correspondence but not retrieved
**Action:** `get_related_documents` with document type "Engineer's
Determination"; `search_chunks` with query "determination entitlement
[claim event description]"
**Look for:** The determination document and the Engineer's position
on entitlement

---

## Always flag — regardless of query

1. **Time bar caveat** — if notice_and_instruction_compliance findings
   show POTENTIALLY TIME-BARRED, always flag at the top: the
   entitlement analysis is secondary to the notice position; state
   in one sentence the consequence if the time bar is upheld.

2. **Entitlement clause deleted or restricted by Particular
   Conditions** — always flag when the cited clause has been removed
   or materially restricted; state what the restriction is and its
   forensic implication.

3. **Silver Book Employer Risk Event claim that would succeed under
   Red Book but not Silver Book** — always flag the book-specific
   risk allocation distinction; state why the event does or does not
   qualify under the Silver Book as retrieved.

4. **Profit claimed where retrieved clause provides Cost only** —
   always flag; state the clause reference and the Cost-only
   limitation as retrieved from the documents.

5. **Claim without stated FIDIC contractual basis** — always flag;
   a claim without a cited sub-clause is procedurally deficient under
   both 1999 and 2017 FIDIC.

---

## Output format

```
## Entitlement Basis Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required for this analysis not found in the
warehouse. State which analysis steps are affected.]

### Layer 2 Reference Retrieved
[State whether the relevant FIDIC clause(s) for the confirmed book
and edition were retrieved from Layer 2. If not: state analytical
knowledge applied.]

### Notice Position (from notice_and_instruction_compliance)
[State the notice classification — time bar caveat if applicable]

### Claim Summary
Relief claimed: [EOT / Cost / EOT + Cost / EOT + Cost + Profit / Other]
FIDIC clause cited: [sub-clause number, or NOT CITED IN CLAIM DOCUMENT]
Event description: [from retrieved claim document]
Source: [claim document reference]

### Entitlement Clause Confirmation
Sub-clause exists in retrieved PC: [YES / NO — DELETED / AMENDED /
CANNOT CONFIRM — PC not retrieved]
PC amendment: [describe amendment / NONE FOUND / CANNOT CONFIRM]
Source: [PC document reference]
Applicable clause terms: [from retrieved PC as amended / CANNOT CONFIRM]

### Event Qualification
Book type: [Red / Yellow / Silver — from contract_assembly]
Event classification: [Employer Risk Event / Neutral Event /
Contractor Risk Event / CANNOT CLASSIFY]
Classification basis: [cite the specific retrieved PC provision]
Time entitlement: [YES / NO / CANNOT CONFIRM]
Cost entitlement: [YES / NO — clause provides EOT only / CANNOT CONFIRM]
Profit entitlement: [YES — clause explicitly provides / NO — Cost only /
CANNOT CONFIRM]

### Proof Elements Assessment
| Element required by clause | Evidence in warehouse | Classification |
|---|---|---|
| [element from retrieved clause] | [document reference or ABSENT] | [DEMONSTRATED / NOT DEMONSTRATED / CANNOT ASSESS] |

### Engineer's Determination
Determination retrieved: [YES / NO — NOT FOUND IN WAREHOUSE]
Engineer's position on entitlement: [from retrieved determination /
CANNOT ASSESS]
Source: [document reference]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any entitlement classification or
proof element from this section without first confirming it from
retrieved project documents (Layer 1) and the relevant FIDIC clause
(Layer 2).*

**Book-level risk allocation — analytical reference:**
The three FIDIC books allocate risk differently. Red Book: Employer
takes design risk and physical conditions risk. Yellow Book: Contractor
takes design risk; Employer takes unforeseeable physical conditions
risk under Clause 4.12 (subject to PC amendment). Silver Book:
Contractor takes most risk including design and most physical
conditions. These are general structural positions — the actual
allocation for any project is the allocation in the retrieved
Particular Conditions.

**Entitlement structure — analytical reference:**
FIDIC entitlement sub-clauses follow a pattern: event occurs →
notice given → entitlement to EOT and/or Cost established by the
specific clause → detailed claim follows. Not all sub-clauses provide
both time and money. Some provide time only (Neutral Events). Some
provide time and cost. Some provide time, cost, and profit. The
specific provision in the retrieved Particular Conditions governs —
not the general pattern.

**FIDIC 2017 symmetric claims — analytical reference:**
Under FIDIC 2017, Employer claims are subject to the same notice
and proof requirements as Contractor claims. This symmetry does not
exist in FIDIC 1999. The edition must be confirmed from Layer 1
before applying this framework.
