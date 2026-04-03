# Entitlement Basis

**Skill type:** Contract-type-specific
The entitlement framework differs materially across standard forms due to
different risk allocation and design responsibility. The specific provision
that supports a claimed entitlement, whether that provision has been amended
by the project's amendment document, and what it requires the claimant to
demonstrate — all of these are standard-form-specific and project-specific.
**Layer dependency:**
- Layer 1 — project documents: the claim document; amendment document
  (entitlement clauses, employer risk events, cost recovery provisions);
  Contract Agreement; relevant correspondence
- Layer 2b — reference standards: Governing standard form for the confirmed
  contract — the specific provisions cited in the claim and the relevant
  entitlement framework
**Domain:** Legal & Contractual SME
**Invoked by:** Legal orchestrator

---

## When to apply this skill

Apply when a query concerns whether a Contractor or Employer has a
contractual entitlement to additional time, cost, or both — including
time extension claims, prolongation cost claims, variation entitlements,
unforeseeable conditions claims, suspension claims, or termination
compensation. Also apply when assessing whether the clause cited in a
claim document actually supports the relief claimed, or whether amendment
provisions have modified or removed the entitlement.

---

## Before you begin

### Foundational requirements
Read contract_assembly and notice_and_instruction_compliance findings first.

From contract_assembly:
- Confirmed standard form and version — required to retrieve the correct
  entitlement framework from Layer 2b
- Amendment provisions — especially any that modify entitlement clauses,
  narrow employer risk events, restrict cost recovery, or remove specific
  heads of claim

From notice_and_instruction_compliance:
- Time bar status for any notice corresponding to this claim
- If notice is POTENTIALLY TIME-BARRED: flag this at the start of
  the entitlement assessment. The entitlement analysis is secondary
  to the notice position. Proceed with entitlement assessment and
  note the time bar caveat throughout.

**If standard form is UNCONFIRMED:** State CANNOT ASSESS entitlement
basis. The entitlement framework is standard-form-specific — analysis
without a confirmed standard form will produce unreliable output.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The claim document (time extension claim, variation claim, or other) —
  required to identify the clause cited and the relief claimed
- The amendment document — required to confirm whether the cited clause
  has been amended and what the actual entitlement terms are
- The General Conditions — if not in Layer 1, retrieve from Layer 2b
- Any contract administrator determination or employer response to the claim
- Supporting correspondence and records referenced in the claim

**If the claim document is not retrieved:** State CANNOT ASSESS
entitlement basis. A claim document must be present to assess.

**If the amendment document is not retrieved:** State CANNOT
CONFIRM whether the entitlement clause cited in the claim has been
amended. Do not assess entitlement against the General Conditions
text without confirming the amendment position.

### Layer 2b documents to retrieve (reference standards)

After confirming the standard form and the specific clause cited in
the claim, call `search_chunks` with `layer_type = '2b'` to retrieve:
- The specific clause cited in the claim — search by subject matter,
  not by clause number (e.g. "time extension entitlement employer
  risk event")
- The employer risk event list for the confirmed standard form —
  search by subject matter: "employer risk events contractor
  entitlement time cost"
- The cost recovery provisions — search by subject matter: "cost
  definition profit contractor entitlement"

**Purpose:** To compare what the standard form clause says against
what the amendment document says for this project. The entitlement
terms to apply are those in the retrieved amendment document (as
amended), not the Layer 2b standard form text. Layer 2b is the
comparison baseline only.

**If the governing standard form is not retrieved from Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE for the
entitlement provisions. Do not describe entitlement terms from
training knowledge.

---

## Analysis workflow

### Step 1 — Identify the claimed entitlement and the clause cited
*Contract-type-agnostic*

From the retrieved claim document, identify:
- What relief is claimed: time extension only / cost only /
  time extension + cost / time extension + cost + profit /
  termination compensation / other
- Which clause is cited as the entitlement basis
- The nature of the event giving rise to the claim (as described
  in the claim document)

**Do not characterise the claim beyond what the retrieved document
states.** If the claim document does not cite a clause: note this as
a deficiency in the claim — a claim without a stated contractual
basis is procedurally deficient under most standard forms.

### Step 2 — Confirm the entitlement clause from the amendment document
*Contract-type-specific*

From the retrieved amendment document, confirm:
- Whether the clause cited in the claim exists in the project contract
  (i.e. has not been deleted by the amendment document)
- Whether the clause has been amended and if so how
- What relief the clause as amended actually provides

**The entitlement clause to apply is the version in the retrieved
amendment document.** If the amendment document contains an amendment
to the cited clause: apply the amended version and state the amendment.
If no amendment is found AND the amendment document has been fully
retrieved: note that the General Conditions version appears to apply —
citing the amendment document as source.
If the amendment document has not been retrieved: state CANNOT
CONFIRM the applicable entitlement terms.

### Step 3 — Assess risk allocation under the confirmed standard form
*Contract-type-specific*

The risk allocation between the parties — which events entitle the
Contractor to time, cost, or both — differs by standard form. Retrieve
the employer risk event list and the risk allocation framework from
Layer 2b.

**Do not apply a risk allocation framework from training knowledge.**
Retrieve the employer risk event list for the confirmed standard form
from Layer 2b. Check whether the amendment document has modified that
list. Apply the retrieved and confirmed list only.

If Layer 2b retrieval returns no result for the risk allocation
provisions: state CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE.
Do not classify the event as an employer or contractor risk event
without the retrieved provision.

For each event claimed:
- Retrieve the employer risk event provision from Layer 2b
- Check the amendment document for any modification to that provision
- Assess whether the claimed event falls within the confirmed provision
- Classify: EMPLOYER RISK EVENT / NEUTRAL EVENT / CONTRACTOR RISK
  EVENT / CANNOT CLASSIFY (if standard form not retrieved)

### Step 4 — Assess cost entitlement separately from time entitlement
*Contract-type-agnostic principle / contract-type-specific application*

Time entitlement and cost entitlement are separate assessments under
most standard forms. An event may entitle the Contractor to a time
extension without cost, or to both time and cost, or to time, cost,
and profit. Profit is recoverable only where the entitlement provision
expressly provides for it.

For each claimed head (time, cost, profit):
- Retrieve the provision cited in the claim from Layer 2b
- Confirm from the amendment document whether that provision has
  been amended
- Confirm whether that provision provides for that head
- If profit is claimed and the retrieved provision provides for cost
  only: flag — profit is not recoverable under that provision as retrieved

### Step 5 — Assess the required proof elements
*Contract-type-agnostic*

Every entitlement provision requires the claimant to demonstrate
specific elements to establish entitlement. From the retrieved Layer 2b
clause text (confirmed against the amendment document version), identify
the required proof elements.

For each element:
- Identify it from the retrieved clause text
- Assess whether the retrieved claim documents provide evidence for it
- Classify: DEMONSTRATED / NOT DEMONSTRATED / CANNOT ASSESS (evidence
  not in warehouse)

Do not characterise proof elements as demonstrated on the basis of
what the claim document asserts — assess against independent evidence
in the retrieved documents.

### Step 6 — Assess the contract administrator's determination
*Contract-type-agnostic*

If a contract administrator determination has been retrieved:
- Does the determination address the entitlement claimed?
- What position has the contract administrator taken on the entitlement?
- Is the contract administrator's position consistent with the
  retrieved clause text?
- Does the determination reveal any employer consent issues (from
  engineer_identification findings)?

If no determination has been retrieved after searching:
State CANNOT ASSESS the contract administrator's position on entitlement.

---

## Classification and decision rules

**Entitlement clause confirmed:**

Clause exists and unamended in retrieved amendment document → clause
governs as per General Conditions standard text (cite amendment
document as source of confirmation)
Clause amended in retrieved amendment document → apply amended version —
state the amendment and its effect
Clause deleted in retrieved amendment document → NO CONTRACTUAL BASIS
for this claim under the cited clause — flag; state the deletion and source
Amendment document not retrieved → CANNOT CONFIRM entitlement
clause — do not proceed with entitlement assessment beyond flagging
this gap

**Event qualification:**

Event falls within employer risk events as stated in retrieved
documents → IN SCOPE — proceed with proof element assessment
Event does not fall within employer risk events as stated in retrieved
documents → OUT OF SCOPE under cited clause — flag; state which
retrieved provision excludes the event
Event is a neutral event under retrieved documents → TIME ONLY —
no cost entitlement under this clause
Cannot determine event classification because standard form not
retrieved from Layer 2b → CANNOT CLASSIFY

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

**Signal:** Claim cites a clause but the amendment document provision
for that clause has not been retrieved
**Action:** `get_document` on the amendment document ID;
`search_chunks` with query "[clause subject matter] particular
conditions amendment"
**Look for:** The amendment to the cited clause

**Signal:** Claim references supporting documents (records, reports,
correspondence) that have not been retrieved
**Action:** `get_related_documents` with the document types referenced;
`search_chunks` with the event description and date range
**Look for:** The supporting documents evidencing the claimed event
and its impact

**Signal:** Layer 2b entitlement provision for the cited clause has
not been retrieved
**Action:** `search_chunks` with `layer_type = '2b'` and query
"[standard form name] [clause subject matter]"
**Look for:** The standard form text for the cited provision for
comparison against the amendment document version

**Signal:** Contract administrator determination has been referenced
in correspondence but not retrieved
**Action:** `get_related_documents` with document type "Determination";
`search_chunks` with query "determination entitlement [claim event
description]"
**Look for:** The determination document

---

## Always flag — regardless of query

1. **Time bar caveat** — if notice_and_instruction_compliance findings
   show POTENTIALLY TIME-BARRED, always flag at the top: the
   entitlement analysis is secondary to the notice position; state
   in one sentence the consequence if the time bar is upheld.

2. **Entitlement clause deleted or restricted by amendment document** —
   always flag when the cited clause has been removed or materially
   restricted; state what the restriction is and its forensic implication.

3. **Risk allocation differs by standard form** — always retrieve and
   confirm the employer risk event list from Layer 2b before classifying
   any event; flag if standard form not retrieved.

4. **Profit claimed where retrieved provision provides cost only** —
   always flag; state the provision reference and the cost-only
   limitation as retrieved from the documents.

5. **Claim without stated contractual basis** — always flag;
   a claim without a cited clause is procedurally deficient under
   most standard forms.

6. **Governing standard not retrieved from Layer 2b** — flag when the
   entitlement provisions could not be retrieved; state what analysis
   cannot proceed and what standard would need to be ingested.

---

## Output format

```
## Entitlement Basis Assessment

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
[List every document required for this analysis not found in the
warehouse. State which analysis steps are affected.]

### Layer 2b Reference Retrieved
[State whether the entitlement provisions for the confirmed standard
form were retrieved from Layer 2b. If not: state CANNOT CONFIRM —
STANDARD FORM NOT IN WAREHOUSE and list which analysis steps
are affected.]

### Notice Position (from notice_and_instruction_compliance)
[State the notice classification — time bar caveat if applicable]

### Claim Summary
Relief claimed: [time extension / cost / time + cost / time + cost + profit / other]
Clause cited: [clause reference, or NOT CITED IN CLAIM DOCUMENT]
Event description: [from retrieved claim document]
Source: [claim document reference]

### Entitlement Clause Confirmation
Clause exists in retrieved amendment document: [YES / NO — DELETED /
AMENDED / CANNOT CONFIRM — amendment document not retrieved]
Amendment: [describe amendment / NONE FOUND / CANNOT CONFIRM]
Source: [amendment document reference]
Applicable clause terms: [from retrieved amendment document as amended /
CANNOT CONFIRM]

### Event Qualification
Standard form: [from contract_assembly]
Employer risk event list: [RETRIEVED FROM LAYER 2b / CANNOT CONFIRM —
STANDARD FORM NOT IN WAREHOUSE]
Event classification: [EMPLOYER RISK EVENT / NEUTRAL EVENT /
CONTRACTOR RISK EVENT / CANNOT CLASSIFY]
Classification basis: [cite the specific retrieved provision]
Time entitlement: [YES / NO / CANNOT CONFIRM]
Cost entitlement: [YES / NO — provision provides time only / CANNOT CONFIRM]
Profit entitlement: [YES — provision explicitly provides / NO — cost only /
CANNOT CONFIRM]

### Proof Elements Assessment
| Element required by clause | Evidence in warehouse | Classification |
|---|---|---|
| [element from retrieved clause] | [document reference or ABSENT] | [DEMONSTRATED / NOT DEMONSTRATED / CANNOT ASSESS] |

### Contract Administrator's Determination
Determination retrieved: [YES / NO — NOT FOUND IN WAREHOUSE]
Position on entitlement: [from retrieved determination / CANNOT ASSESS]
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
retrieved project documents (Layer 1) and the relevant standard form
provision (Layer 2b).*

**Risk allocation — analytical reference:**
Standard forms of contract allocate risk between employer and contractor
in different ways. Some forms allocate more risk to the employer (design,
physical conditions, certain force majeure events). Others allocate
more risk to the contractor (design-build and EPC forms typically
allocate more risk to the contractor, including design risk and, in
some forms, physical conditions risk). The applicable allocation must
be retrieved from the governing standard form in Layer 2b and confirmed
against the amendment document in Layer 1.

**Entitlement structure — analytical reference:**
Most standard form entitlement provisions follow a pattern: qualifying
event occurs → notice given within the prescribed period → entitlement
to time extension and/or cost established by the specific provision →
detailed particulars submitted. Not all provisions provide both time
and cost. Some provide time only. Some provide time and cost. Some
provide time, cost, and profit. The specific provision in the retrieved
documents governs — not any general pattern.

**Proof elements — analytical reference:**
Entitlement provisions in standard forms typically require the claimant
to demonstrate: (a) that the event occurred; (b) that the event was
caused by the other party or is within the specified risk category;
(c) the impact of the event on the programme; and (d) the quantum of
the cost claimed. The specific elements required depend on the
provision — retrieve from Layer 2b before assessing.
