# Prolongation Cost

**Skill type:** Contract-type-specific
Cost entitlement, recoverable heads, and whether Profit is recoverable
depend on which FIDIC sub-clause the entitlement event falls under.
This differs by book and edition. The definition of "Cost" in the
retrieved contract may exclude specific categories. All of these must
be extracted from the retrieved Particular Conditions — not assumed
from the standard form.
**Layer dependency:**
- Layer 1 — project documents: prolongation cost claim submission;
  Particular Conditions (cost recovery clause, definition of Cost);
  Contract Data; site records (payroll, plant hire, establishment
  invoices); payment certificates; Engineer's determination or response
- Layer 2 — reference standards: FIDIC cost recovery sub-clause for
  the confirmed book and edition; the definition of "Cost" in the
  General Conditions
**Domain:** Claims & Disputes SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when retrieved chunks contain a prolongation cost claim, a
time-related cost submission, or a query about the cost consequences
of a delay. Apply when an EOT has been claimed or awarded and a
corresponding cost claim is expected but has not been found.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings, notice_compliance findings,
and eot_quantification findings.

From the invoking orchestrator and eot_quantification extract:
- Confirmed FIDIC book and edition
- The delay event type as established from retrieved documents:
  Employer Risk Event (EOT + Cost entitlement), Neutral Event
  (EOT only — no cost entitlement), or Contractor Risk Event
  (no entitlement)
- The EOT period claimed and any EOT period confirmed or awarded

**Cost entitlement is conditional on the event type established from
retrieved documents.** If the event type has not been confirmed from
retrieved Particular Conditions: state CANNOT CONFIRM cost entitlement
basis. Do not assess quantum.

If the event is a Neutral Event from retrieved documents: state NO
COST ENTITLEMENT under the applicable clause as retrieved. Do not
proceed with quantum assessment.

From notice_compliance:
- Time bar status — if POTENTIALLY TIME-BARRED: flag at the start

**If book type is UNCONFIRMED:** State CANNOT ASSESS cost entitlement.
The recoverable heads and the definition of Cost differ by book.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The prolongation cost claim submission
- The Particular Conditions — specifically the cost recovery clause
  and the definition of "Cost"
- The Contract Data — for any prescribed cost parameters
- Site records covering the prolongation period:
  - Payroll records and staff deployment schedules
  - Plant hire records and plant returns
  - Site establishment invoices (accommodation, utilities, welfare)
- Payment certificates for the prolongation period
- The Engineer's determination or response to the cost claim

**If the Particular Conditions are not retrieved:**
State CANNOT CONFIRM the cost recovery clause, the definition of Cost,
or whether Profit is recoverable. Do not assess any head of claim.

**If no contemporaneous site records are retrieved:**
State that the cost claim has not been independently verified from
warehouse records. Flag this for every head of claim affected.

**For each document retrieved:** State its reference number and the
period it covers.

### Layer 2 documents to retrieve (reference standards)

After confirming book type and the cost entitlement clause, call
`search_chunks` to retrieve from Layer 2:
- The specific cost recovery sub-clause for the confirmed book and
  edition (the clause under which the EOT event falls)
- The definition of "Cost" in the FIDIC General Conditions for the
  confirmed book and edition

**Purpose:** To establish what the standard FIDIC clause provides
so that any Particular Conditions amendment can be assessed against
it. The cost recovery terms to apply are those in the retrieved
Particular Conditions — not the Layer 2 standard text.

---

## Analysis workflow

### Step 1 — Confirm the cost recovery clause and definition of Cost
*Contract-type-specific*

From the retrieved Particular Conditions:
- Identify the sub-clause under which the entitlement event falls
  (as established in eot_quantification findings)
- Confirm whether that sub-clause provides for Cost only, or
  Cost plus Profit — extract from the retrieved PC
- Retrieve the definition of "Cost" from the retrieved Particular
  Conditions or General Conditions — confirm whether financing
  charges are included or excluded

**The definition of Cost and the recoverable heads are the version
in the retrieved Particular Conditions.** Do not apply the General
Conditions definition without confirming it has not been amended.
If the Particular Conditions have not been retrieved: state CANNOT
CONFIRM the definition of Cost or whether Profit is recoverable.

### Step 2 — Confirm the prolongation period
*Contract-type-agnostic*

The prolongation period is the period of EOT for which the cost claim
is made. From retrieved documents:
- What period does the cost claim cover?
- What is the EOT period claimed (from eot_quantification findings)?
- What is the EOT period awarded or agreed (if any, from retrieved
  determination)?

Compare the cost claim period against the established EOT period.

**If the cost claim covers a longer period than the established EOT:**
Flag — the excess period has no established time entitlement
foundation. Do not assess quantum for the excess period.

**If the EOT period has not been confirmed from retrieved documents:**
State CANNOT CONFIRM whether the prolongation cost period is within
the established entitlement period.

### Step 3 — Assess each head of claim
*Contract-type-agnostic for the assessment framework;
contract-type-specific for recoverability*

For each head of claim, assess two questions:
(a) Is it recoverable under the confirmed cost recovery clause?
(b) Is it evidenced by retrieved documents?

**Assess only the heads of claim that appear in the retrieved claim
submission.** Do not introduce heads of claim that are not in the
retrieved documents.

**Time-related site overheads (staff costs):**
Recoverability: from the definition of Cost in retrieved PC.
Evidence: retrieve payroll records and staff deployment schedules
for the prolongation period. If not retrieved: state CANNOT VERIFY
from warehouse documents. Do not assess quantum without records.

**Site establishment costs:**
Recoverability: from definition of Cost in retrieved PC.
Evidence: retrieve invoices and hire agreements for the prolongation
period. If not retrieved: state CANNOT VERIFY.

**Plant and equipment:**
Recoverability: from definition of Cost in retrieved PC.
Evidence: retrieve plant hire records and plant returns for the period.
Note: idle plant rates differ from working plant rates — identify
which rate is applied in the claim and whether it is consistent with
the retrieved records.

**Finance charges:**
Recoverability: from the definition of Cost in the retrieved
Particular Conditions or General Conditions. Finance charges are
only recoverable if expressly included in the definition — confirm
from retrieved documents. Do not apply any position on finance
charge recoverability without retrieved confirmation.

**Head office overhead:**
Recoverability: from definition of Cost in retrieved PC — confirm
whether overhead is expressly included or excluded.
Evidence and methodology: identify from the retrieved claim document
whether actual costs or a formula (Hudson, Emden, or Eichleay) is
used. For actual costs: retrieve audited accounts or overhead records.
For formula: retrieve the inputs used (annual turnover, contract sum,
contract period). If formula inputs are not supported by retrieved
audited accounts: state that the inputs cannot be verified from
warehouse documents.

**Profit:**
Recoverability: only if the retrieved cost recovery clause expressly
provides for Cost plus Profit. If the retrieved clause provides for
Cost only: state NOT RECOVERABLE under the retrieved clause. Do not
assess Profit quantum if the clause does not support it.

### Step 4 — Cross-check records against the claimed period
*Contract-type-agnostic*

For each head of claim, verify that the retrieved records cover the
specific prolongation period claimed. If the retrieved records cover
a different period, different scope, or are absent for the claimed
period: state this specifically. Do not accept a period that is not
confirmed from retrieved records.

### Step 5 — Assess concurrent delay adjustment
*Contract-type-agnostic*

From eot_quantification findings, identify whether any concurrent
Contractor-caused delay was identified during the prolongation period.

If concurrent delay was identified: state the affected period and
note that the recoverable cost period may be reduced for that period.
Do not calculate a reduced quantum — state the concurrent delay period
and its potential effect on cost entitlement from the retrieved
eot_quantification analysis.

### Step 6 — Assess the Engineer's or Employer's Representative's response
*Contract-type-specific*

From the retrieved determination or response:
- What amount was awarded (if any)?
- What reasons were given for reduction or rejection?

If not retrieved after searching: state CANNOT ASSESS the contract
administrator's position on cost.

---

## Classification and decision rules

**Cost entitlement confirmed:**

Event type confirmed as Employer Risk Event from retrieved PC AND
cost recovery clause confirmed from retrieved PC → PROCEED with
quantum assessment
Event type confirmed as Neutral Event from retrieved PC →
NO COST ENTITLEMENT — flag; do not assess quantum
Event type not confirmed (PC not retrieved) →
CANNOT CONFIRM COST ENTITLEMENT — flag

**Profit recoverability:**

Retrieved clause provides Cost plus Profit →
PROFIT RECOVERABLE IN PRINCIPLE — assess quantum
Retrieved clause provides Cost only →
PROFIT NOT RECOVERABLE under retrieved clause — flag if claimed
Clause not retrieved → CANNOT CONFIRM Profit recoverability

**Head of claim evidence:**

Head evidenced by retrieved records covering the prolongation period
→ SUPPORTED — state quantum and source documents
Head partially evidenced (records cover part of the period) →
PARTIALLY SUPPORTED — state what is evidenced and what is not
Head not evidenced by any retrieved records →
CANNOT VERIFY FROM WAREHOUSE DOCUMENTS — flag; state what is missing

**Formula methodology:**

Formula inputs supported by retrieved audited accounts →
VERIFIABLE — assess inputs against retrieved accounts
Formula inputs not supported by retrieved audited accounts →
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

**Signal:** Definition of Cost not found in retrieved PC
**Action:** `get_document` on the Particular Conditions document ID;
`search_chunks` with query "definition cost financing charges overhead"
**Look for:** The definition of Cost in the PC or General Conditions

**Signal:** Head office overhead formula used but no audited accounts
retrieved
**Action:** `search_chunks` with query "audited accounts annual
turnover overhead"
**Look for:** Audited financial statements supporting the formula inputs

**Signal:** Layer 2 cost recovery clause not retrieved
**Action:** `search_chunks` with query "[FIDIC book] [edition]
clause [number] cost profit [subject]"
**Look for:** Standard FIDIC text for the cost recovery clause

---

## Always flag — regardless of query

1. **Cost claim for Neutral Event or Contractor Risk Event** — state
   the event classification from retrieved documents and that no cost
   entitlement exists under the applicable clause as retrieved.

2. **Prolongation period exceeds established EOT period** — state
   the excess period and that no time entitlement foundation has been
   established for it.

3. **Profit claimed where retrieved clause provides Cost only** —
   state the clause reference and the Cost-only limitation from
   retrieved documents.

4. **No contemporaneous records for any head of claim** — state the
   absence and its evidential impact.

5. **Formula inputs not verified from retrieved audited accounts** —
   state which inputs cannot be confirmed and that the formula result
   cannot be verified.

---

## Output format

```
## Prolongation Cost Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2 Reference Retrieved
[State whether the cost recovery clause and definition of Cost were
retrieved from Layer 2. If not: state analytical knowledge applied.]

### Entitlement Basis
Event type: [Employer Risk Event / Neutral Event / Contractor Risk Event /
CANNOT CONFIRM — PC not retrieved]
Cost recovery clause: [from retrieved PC / CANNOT CONFIRM]
Profit recoverable: [YES — clause reference / NO — Cost only / CANNOT CONFIRM]
Finance charges in Cost definition: [YES / NO / CANNOT CONFIRM]
Source: [PC document reference]

### Prolongation Period
EOT claimed: [days and period from eot_quantification]
EOT established or awarded: [days and period / NOT CONFIRMED]
Cost claim period: [dates from retrieved claim]
Alignment: [CONSISTENT / MISMATCH — describe excess / CANNOT CONFIRM]

### Heads of Claim Assessment

| Head | Amount claimed | Records retrieved | Period covered by records | Recoverability | Assessment |
|---|---|---|---|---|---|
| Site staff | [amount] | [YES/PARTIAL/NO] | [dates or N/A] | [from retrieved PC] | [SUPPORTED/PARTIAL/CANNOT VERIFY] |
| Site establishment | [amount] | [YES/PARTIAL/NO] | [dates or N/A] | [from retrieved PC] | [assessment] |
| Plant and equipment | [amount] | [YES/PARTIAL/NO] | [dates or N/A] | [from retrieved PC] | [assessment] |
| Finance charges | [amount] | [YES/PARTIAL/NO] | [dates or N/A] | [from retrieved PC] | [assessment] |
| Head office overhead | [amount] | [YES/PARTIAL/NO] | [dates or N/A] | [from retrieved PC] | [assessment] |
| Profit | [amount] | [YES/PARTIAL/NO] | [dates or N/A] | [from retrieved PC] | [assessment] |
| Total | [total] | | | | |

### Findings by Head of Claim
[For each head:]
**[Head name]**
Amount claimed: [amount]
Recoverability: [from retrieved clause / CANNOT CONFIRM]
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
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any recoverability position, formula,
or cost definition from this section without first confirming it from
retrieved project documents.*

**FIDIC Cost definition — analytical reference:**
The FIDIC General Conditions define "Cost" to include all expenditure
reasonably incurred including overhead but generally excluding profit.
Financing charges are included in the 2017 editions and may be
included in 1999 editions depending on the precise definition wording.
GCC Particular Conditions frequently amend the definition — Abu Dhabi
government projects sometimes exclude or cap overhead recovery; Saudi
Arabia government contracts may exclude financing charges. The
definition in the retrieved Particular Conditions governs.

**Head office overhead formula — analytical reference:**
Hudson formula uses the overhead percentage from the contract.
Emden formula uses actual audited accounts — more defensible where
accounts are available. Eichleay formula is US-developed and faces
challenge in GCC proceedings. Identify which formula is used from
the retrieved claim documents and verify inputs against retrieved
financial records. A formula applied with unverified inputs cannot
be assessed.

**Silver Book cost entitlement — analytical reference:**
The Silver Book allocates most risk to the Contractor. Employer Risk
Events are narrower than in the Red or Yellow Book. Cost recovery
under the Silver Book requires careful verification against the
retrieved Particular Conditions — the standard form Employer Risk
Event list is already narrow and GCC Silver Book Particular Conditions
frequently restrict it further.
