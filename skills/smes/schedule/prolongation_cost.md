# Prolongation Cost

**Skill type:** Contract-type-specific
Cost entitlement, recoverable heads, and whether profit is recoverable
depend on which provision the entitlement event falls under. This differs
by standard form and version. The definition of cost in the retrieved
contract may exclude specific categories. All of these must be extracted
from the retrieved amendment document — not assumed from the standard form.
**Layer dependency:**
- Layer 1 — project documents: prolongation cost claim submission;
  amendment document (cost recovery provision, definition of cost);
  Contract Data; site records (payroll, plant hire, establishment
  invoices); payment certificates; contract administrator determination
  or response
- Layer 2b — reference standards: cost recovery provision for the
  confirmed standard form and version; definition of cost in the
  General Conditions
**Domain:** Delay and Cost Analytics SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when retrieved documents contain a prolongation cost claim, a
time-related cost submission, or a query about the cost consequences
of a delay. Apply when a time extension has been claimed or awarded
and a corresponding cost claim is expected but has not been found.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings, notice_compliance findings,
and eot_quantification findings.

From the invoking orchestrator and eot_quantification extract:
- Confirmed standard form and version
- The delay event type as established from retrieved documents:
  employer risk event (time extension + cost entitlement), neutral
  event (time extension only — no cost entitlement), or contractor
  risk event (no entitlement)
- The time extension period claimed and any period confirmed or awarded

**Cost entitlement is conditional on the event type established from
retrieved documents.** If the event type has not been confirmed from
the retrieved amendment document: state CANNOT CONFIRM cost entitlement
basis. Do not assess quantum.

If the event is a neutral event from retrieved documents: state NO
COST ENTITLEMENT under the applicable provision as retrieved. Do not
proceed with quantum assessment.

From notice_compliance:
- Time bar status — if POTENTIALLY TIME-BARRED: flag at the start

**If standard form is UNCONFIRMED:** State CANNOT ASSESS cost
entitlement. The recoverable heads and the definition of cost differ
by standard form.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The prolongation cost claim submission
- The amendment document — specifically the cost recovery provision
  and the definition of cost
- The Contract Data — for any prescribed cost parameters
- Site records covering the prolongation period:
  - Payroll records and staff deployment schedules
  - Plant hire records and plant returns
  - Site establishment invoices (accommodation, utilities, welfare)
- Payment certificates for the prolongation period
- The contract administrator determination or response (if any)

**If the amendment document is not retrieved:**
State CANNOT CONFIRM the cost recovery provision, the definition of
cost, or whether profit is recoverable. Do not assess any head of
claim.

**If no contemporaneous site records are retrieved:**
State that the cost claim has not been independently verified from
warehouse records. Flag this for every head of claim affected.

**For each document retrieved:** State its reference number and the
period it covers.

### Layer 2b documents to retrieve (reference standards)

After confirming standard form and the cost entitlement provision,
call `search_chunks` with `layer_type = '2b'` to retrieve:
- The cost recovery provision for the confirmed standard form
  (search by subject matter: "cost recovery entitlement time
  extension employer risk event")
- The definition of cost in the General Conditions for the confirmed
  standard form (search by subject matter: "definition cost overhead
  profit financing charges")

**Purpose:** To establish what the standard form provision provides
so that any amendment can be assessed against it. The cost recovery
terms to apply are those in the retrieved amendment document — not
the Layer 2b standard text.

**If the governing standard form is not retrieved from Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE for the cost
provisions. Do not describe cost recoverability from training knowledge.

---

## Analysis workflow

### Step 1 — Confirm the cost recovery provision and definition of cost
*Contract-type-specific*

From the retrieved amendment document:
- Identify the provision under which the entitlement event falls
  (as established in eot_quantification findings)
- Confirm whether that provision provides for cost only, or cost
  plus profit — extract from the retrieved amendment document
- Retrieve the definition of cost from the retrieved amendment
  document or General Conditions — confirm whether financing charges
  are included or excluded

**The definition of cost and the recoverable heads are the version
in the retrieved amendment document.** Do not apply the General
Conditions definition without confirming it has not been amended.
If the amendment document has not been retrieved: state CANNOT
CONFIRM the definition of cost or whether profit is recoverable.

### Step 2 — Confirm the prolongation period
*Contract-type-agnostic*

The prolongation period is the period of time extension for which
the cost claim is made. From retrieved documents:
- What period does the cost claim cover?
- What is the time extension period claimed (from eot_quantification)?
- What is the time extension period awarded or agreed (if any)?

Compare the cost claim period against the established time extension
period.

**If the cost claim covers a longer period than the established time
extension:** Flag — the excess period has no established time
entitlement foundation. Do not assess quantum for the excess period.

**If the time extension period has not been confirmed from retrieved
documents:** State CANNOT CONFIRM whether the prolongation cost period
is within the established entitlement period.

### Step 3 — Assess each head of claim
*Contract-type-agnostic for the assessment framework;
contract-type-specific for recoverability*

For each head of claim, assess two questions:
(a) Is it recoverable under the confirmed cost recovery provision?
(b) Is it evidenced by retrieved documents?

**Assess only the heads of claim that appear in the retrieved claim
submission.** Do not introduce heads of claim not in the retrieved
documents.

**Time-related site overheads (staff costs):**
Recoverability: from the definition of cost in retrieved amendment
document. Evidence: retrieve payroll records and staff deployment
schedules for the prolongation period. If not retrieved: state CANNOT
VERIFY from warehouse documents. Do not assess quantum without records.

**Site establishment costs:**
Recoverability: from definition of cost in retrieved amendment
document. Evidence: retrieve invoices and hire agreements for the
prolongation period. If not retrieved: state CANNOT VERIFY.

**Plant and equipment:**
Recoverability: from definition of cost in retrieved amendment
document. Evidence: retrieve plant hire records and plant returns
for the period. Note: idle rates differ from working rates — identify
which rate is applied in the claim and whether it is consistent with
the retrieved records.

**Finance charges:**
Recoverability: from the definition of cost in the retrieved amendment
document or General Conditions. Finance charges are only recoverable
if expressly included in the definition — confirm from retrieved
documents. Do not apply any position on finance charge recoverability
without retrieved confirmation.

**Head office overhead:**
Recoverability: from definition of cost in retrieved amendment
document — confirm whether overhead is expressly included or excluded.
Evidence and methodology: identify from the retrieved claim document
whether actual costs or a formula is used. For actual costs: retrieve
audited accounts or overhead records. For formula: retrieve the inputs
used (annual turnover, contract sum, contract period). If formula
inputs are not supported by retrieved audited accounts: state that
the inputs cannot be verified from warehouse documents.

**Profit:**
Recoverability: only if the retrieved cost recovery provision
expressly provides for cost plus profit. If the retrieved provision
provides for cost only: state NOT RECOVERABLE under the retrieved
provision. Do not assess profit quantum if the provision does not
support it.

### Step 4 — Cross-check records against the claimed period
*Contract-type-agnostic*

For each head of claim, verify that the retrieved records cover the
specific prolongation period claimed. If the retrieved records cover
a different period, different scope, or are absent for the claimed
period: state this specifically. Do not accept a period not confirmed
from retrieved records.

### Step 5 — Assess concurrent delay adjustment
*Contract-type-agnostic*

From eot_quantification findings, identify whether any concurrent
contractor-caused delay was identified during the prolongation period.

If concurrent delay was identified: state the affected period and
note that the recoverable cost period may be reduced for that period.
Do not calculate a reduced quantum — state the concurrent delay period
and its potential effect from the retrieved eot_quantification analysis.

### Step 6 — Assess the contract administrator's response
*Contract-type-specific*

From the retrieved determination or response:
- What amount was awarded (if any)?
- What reasons were given for reduction or rejection?

If not retrieved after searching: state CANNOT ASSESS the contract
administrator's position on cost.

---

## Classification and decision rules

**Cost entitlement confirmed:**

Event type confirmed as employer risk event from retrieved amendment
document AND cost recovery provision confirmed → PROCEED with quantum
Event type confirmed as neutral event from retrieved amendment document
→ NO COST ENTITLEMENT — flag; do not assess quantum
Event type not confirmed (amendment document not retrieved) →
CANNOT CONFIRM COST ENTITLEMENT — flag

**Profit recoverability:**

Retrieved provision provides cost plus profit →
PROFIT RECOVERABLE IN PRINCIPLE — assess quantum
Retrieved provision provides cost only →
PROFIT NOT RECOVERABLE under retrieved provision — flag if claimed
Provision not retrieved → CANNOT CONFIRM profit recoverability

**Head of claim evidence:**

Head evidenced by retrieved records covering the prolongation period
→ SUPPORTED — state quantum and source documents
Head partially evidenced (records cover part of the period) →
PARTIALLY SUPPORTED — state what is evidenced and what is not
Head not evidenced by any retrieved records →
CANNOT VERIFY FROM WAREHOUSE DOCUMENTS — flag

**Formula methodology:**

Inputs supported by retrieved audited accounts →
VERIFIABLE — assess inputs against retrieved accounts
Inputs not supported by retrieved audited accounts →
INPUTS NOT VERIFIED FROM WAREHOUSE DOCUMENTS — flag

---

## When to call tools

**Signal:** Payroll records not retrieved for the prolongation period
**Action:** `search_chunks` with query "payroll resource schedule
staff site [prolongation period dates]"; `get_related_documents`
with document type "Progress Report" for the period
**Look for:** Staff presence records for the prolongation period

**Signal:** Plant hire records not retrieved
**Action:** `search_chunks` with query "plant hire equipment
[prolongation period dates]"
**Look for:** Hire agreements, plant returns, or site records showing
plant retained during the period

**Signal:** Definition of cost not found in retrieved amendment document
**Action:** `get_document` on the amendment document ID;
`search_chunks` with query "definition cost financing charges overhead"
**Look for:** The definition of cost in the amendment document or
General Conditions

**Signal:** Head office overhead formula used but no audited accounts
retrieved
**Action:** `search_chunks` with query "audited accounts annual
turnover overhead"
**Look for:** Audited financial statements supporting the formula inputs

**Signal:** Layer 2b cost recovery provision not retrieved
**Action:** `search_chunks` with `layer_type = '2b'` and query
"[standard form name] cost recovery entitlement employer risk"
**Look for:** Standard form text for the cost recovery provision

---

## Always flag — regardless of query

1. **Cost claim for neutral event or contractor risk event** — state
   the event classification from retrieved documents and that no cost
   entitlement exists under the applicable provision as retrieved.

2. **Prolongation period exceeds established time extension period**
   — state the excess period and that no time entitlement foundation
   has been established for it.

3. **Profit claimed where retrieved provision provides cost only** —
   state the provision reference and the cost-only limitation from
   retrieved documents.

4. **No contemporaneous records for any head of claim** — state the
   absence and its evidential impact.

5. **Formula inputs not verified from retrieved audited accounts** —
   state which inputs cannot be confirmed and that the formula result
   cannot be verified.

6. **Governing standard not retrieved from Layer 2b** — flag when the
   cost provisions could not be retrieved; state what standard would
   need to be ingested.

---

## Output format

```
## Prolongation Cost Assessment

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
[State whether the cost recovery provision and definition of cost were
retrieved from Layer 2b. If not: state CANNOT CONFIRM —
STANDARD FORM NOT IN WAREHOUSE and list which analysis steps
are affected.]

### Entitlement Basis
Event type: [Employer Risk Event / Neutral Event / Contractor Risk Event /
CANNOT CONFIRM — amendment document not retrieved]
Cost recovery provision: [from retrieved amendment document / CANNOT CONFIRM]
Profit recoverable: [YES — provision reference / NO — cost only / CANNOT CONFIRM]
Finance charges in cost definition: [YES / NO / CANNOT CONFIRM]
Source: [amendment document reference]

### Prolongation Period
Time extension claimed: [days and period from eot_quantification]
Time extension established or awarded: [days and period / NOT CONFIRMED]
Cost claim period: [dates from retrieved claim]
Alignment: [CONSISTENT / MISMATCH — describe excess / CANNOT CONFIRM]

### Heads of Claim Assessment

| Head | Amount claimed | Records retrieved | Period covered | Recoverability | Assessment |
|---|---|---|---|---|---|
| Site staff | [amount] | [YES/PARTIAL/NO] | [dates or N/A] | [from retrieved amendment doc] | [SUPPORTED/PARTIAL/CANNOT VERIFY] |
| Site establishment | [amount] | [YES/PARTIAL/NO] | [dates or N/A] | [from retrieved amendment doc] | [assessment] |
| Plant and equipment | [amount] | [YES/PARTIAL/NO] | [dates or N/A] | [from retrieved amendment doc] | [assessment] |
| Finance charges | [amount] | [YES/PARTIAL/NO] | [dates or N/A] | [from retrieved amendment doc] | [assessment] |
| Head office overhead | [amount] | [YES/PARTIAL/NO] | [dates or N/A] | [from retrieved amendment doc] | [assessment] |
| Profit | [amount] | [YES/PARTIAL/NO] | [dates or N/A] | [from retrieved amendment doc] | [assessment] |
| Total | [total] | | | | |

### Findings by Head of Claim
[For each head:]
**[Head name]**
Amount claimed: [amount]
Recoverability: [from retrieved provision / CANNOT CONFIRM]
Methodology: [actual cost / formula — name / not stated in retrieved documents]
Records retrieved: [description — period and document references]
Assessment: [SUPPORTED / PARTIALLY SUPPORTED / CANNOT VERIFY FROM WAREHOUSE]
Finding: [from retrieved documents only]

### Concurrent Delay Adjustment
[From eot_quantification findings — period and potential cost impact,
or NOT IDENTIFIED / NOT APPLICABLE]

### Contract Administrator Position
Amount awarded: [from retrieved determination / NOT FOUND IN WAREHOUSE]
Reasons: [from retrieved determination / NOT FOUND]
Source: [document reference]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
*(Confidence scale: GREEN = all required evidence retrieved and findings fully supported | AMBER = Layer 2b not retrieved or amendment position unknown -- findings provisional | RED = critical document absent -- findings materially constrained | GREY = standard form unconfirmed -- form-specific analysis suspended. Full definition: skills/c1-skill-authoring/references/grounding_protocol.md)*
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any recoverability position, formula,
or cost definition from this section without first confirming it from
retrieved project documents.*

**Cost definition — analytical reference:**
Standard forms of contract define cost to include expenditure
reasonably incurred including overhead, but the treatment of profit
and financing charges varies. Some standard forms include financing
charges in the cost definition; others do not. Some versions add
profit for specific categories of entitlement event. Amendment
documents frequently modify the definition — the definition in the
retrieved amendment document governs.

**Head office overhead formula — analytical reference:**
Various formulas are used to calculate head office overhead in
prolongation claims (Hudson, Emden, Eichleay, and others). These
formulas require financial inputs (annual turnover, overhead
percentage, contract sum and period) that should be supported by
audited financial statements. Identify which formula is used from
the retrieved claim documents and verify inputs against retrieved
financial records. A formula applied with unverified inputs cannot
be assessed.

**Risk allocation and cost entitlement — analytical reference:**
Standard forms vary in how broadly they define employer risk events
that give rise to cost entitlement. Some forms narrow the employer
risk event list significantly compared to others. Amendment documents
frequently restrict it further. The applicable risk allocation must
be retrieved from the governing standard form in Layer 2b and
confirmed against the amendment document in Layer 1.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies to
any contract form. All characterisations grounded in retrieved warehouse
documents only.*
