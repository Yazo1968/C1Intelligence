# Dispute Resolution Procedure

**Skill type:** Contract-type-specific
The dispute resolution mechanism differs by standard form and version.
Some standard forms include a contract administrator determination step
before escalation; others proceed directly to adjudication or arbitration.
Some standard forms use a dispute board; others use adjudication alone.
Amendment documents frequently replace or modify the standard mechanism
entirely. All of these must be confirmed from the retrieved amendment
document — not assumed.
**Layer dependency:**
- Layer 1 — project documents: Amendment document (dispute resolution
  clause); Contract Data (prescribed periods); adjudication or dispute
  board decision; notice of dissatisfaction or equivalent; arbitration
  notice; contract administrator determination; claim correspondence
  establishing the dispute history
- Layer 2b — reference standards: Dispute resolution provision from
  the governing standard form (whatever is in the warehouse)
**Domain:** Claims & Disputes SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when retrieved documents contain an adjudication or dispute board
decision, a notice of dissatisfaction or equivalent, an arbitration
notice, or a query about whether a dispute has been properly escalated.
Apply when a claim has been rejected or not responded to and the next
procedural step is in question. Apply when assessing limitation periods
for unresolved disputes.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings and the claim history from
notice_compliance and eot_quantification findings.

From the invoking orchestrator extract:
- Confirmed standard form and version
- Dispute resolution mechanism as stated in the retrieved amendment
  document
- Governing law as confirmed from retrieved documents
- Arbitration rules and seat as stated in the retrieved amendment
  document

**If standard form is UNCONFIRMED:** State CANNOT ASSESS the applicable
dispute resolution procedure. The procedure differs materially between
standard forms — analysis without a confirmed standard form is not
possible.

**If the amendment document has not been retrieved:**
State CANNOT CONFIRM the dispute resolution mechanism, the prescribed
periods, or the arbitration rules. Do not apply the General Conditions
mechanism without confirming it has not been amended or replaced.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The amendment document — specifically the dispute resolution clause
  and any amendment or replacement of the standard mechanism
- The Contract Data — all prescribed periods (determination period,
  dispute board decision period, notice of dissatisfaction period,
  amicable settlement period)
- The contract administrator determination (where applicable under
  the confirmed standard form)
- The adjudication or dispute board decision (if issued)
- The notice of dissatisfaction or equivalent (if issued)
- The arbitration notice (if issued)
- The original claim submission and response establishing the dispute
  history

**For each prescribed period:** Extract from the retrieved Contract
Data. Do not apply any period from the standard form without
confirming it has not been amended in the retrieved Contract Data.

**If the Contract Data is not retrieved:**
State CANNOT CONFIRM any prescribed period. Do not state any period.

**If the dispute resolution clause in the amendment document has not
been retrieved:**
State CANNOT CONFIRM the applicable mechanism. Do not assume the
General Conditions mechanism applies.

### Layer 2b documents to retrieve (reference standards)

After confirming standard form, call `search_chunks` with
`layer_type = '2b'` to retrieve:
- The dispute resolution provision for the confirmed standard form
  (search by subject matter: "dispute resolution adjudication
  arbitration procedure escalation")

**Purpose:** To establish the standard form dispute resolution
structure so that any amendment or replacement can be assessed
against it. The mechanism to apply is always the version in the
retrieved amendment document.

**If the governing standard form is not retrieved from Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE for the
dispute resolution provisions. Do not describe the standard mechanism
from training knowledge.

---

## Analysis workflow

### Step 1 — Confirm the applicable dispute resolution mechanism
*Contract-type-specific*

From the retrieved amendment document:
- What dispute resolution mechanism is specified? Is the standard
  form mechanism retained or replaced?
- If retained: what amendments have been made to the standard
  procedure or to the prescribed periods?
- If replaced: what mechanism replaces it (specific arbitration
  centre rules, government dispute committee, courts)?

**The mechanism to apply is the version in the retrieved amendment
document.** Do not apply the General Conditions mechanism without
confirmation.

If the amendment document has not been retrieved: state CANNOT
CONFIRM the applicable mechanism. Flag this as a critical gap.

### Step 2 — Extract all prescribed periods from the Contract Data
*Contract-type-specific*

From the retrieved Contract Data extract each prescribed period for
the confirmed mechanism. Periods to look for (names vary by standard
form — extract whatever the retrieved documents state):
- Period for contract administrator determination (where applicable
  under the confirmed standard form)
- Period for adjudication or dispute board decision
- Period for notice of dissatisfaction or equivalent after
  determination or decision
- Period for amicable settlement attempt
- Any other prescribed period in the retrieved Contract Data

**Do not apply any period from the standard form General Conditions
without first confirming it has not been amended in the retrieved
Contract Data.** If the Contract Data has not been retrieved: state
CANNOT CONFIRM any prescribed period.

### Step 3 — Map the dispute history from retrieved documents
*Contract-type-agnostic*

From all retrieved documents, establish the sequence of steps that
have occurred:
- When was the claim submitted?
- When was the contract administrator determination issued
  (where applicable under the confirmed standard form)?
- When was the dispute referred to adjudication or the dispute board?
- When was the adjudication or dispute board decision issued?
- Was a notice of dissatisfaction or equivalent issued?
- Has arbitration been commenced?

**Establish each step only from retrieved documents.** If a step
cannot be confirmed from retrieved documents: state NOT CONFIRMED
FROM WAREHOUSE DOCUMENTS for that step.

### Step 4 — Assess each procedural step in sequence
*Contract-type-specific*

Apply the procedure confirmed from the retrieved amendment document.
The sequence must be applied in order — each step gates the next.

**(a) Contract administrator determination**

Retrieve the provision from Layer 2b to confirm whether the governing
standard form includes a mandatory determination step before escalation.
Check the amendment document to confirm whether this step has been
retained, modified, or removed.

If a determination step applies under the confirmed documents:
Has the claim been submitted for determination? Retrieve the
determination. Was it issued within the period confirmed from the
retrieved Contract Data? If the determination period has elapsed
and no determination was issued: confirm from the retrieved Contract
Data and standard form provision whether a deemed rejection or
deemed determination mechanism applies — confirm from retrieved
documents only, not from training knowledge.

**(b) Adjudication or dispute board referral**

Has the dispute been referred? Retrieve the referral document.
Was it made within the permitted period confirmed from retrieved
documents? Was the adjudication body or dispute board properly
constituted — confirm the appointment mechanism from the retrieved
amendment document.

**(c) Adjudication or dispute board decision**

Has a decision been issued? Retrieve it. Was it issued within the
period confirmed from retrieved Contract Data?

Retrieve the applicable provision from Layer 2b to confirm the
binding status of the decision under the governing standard form.
Check the amendment document to confirm whether this has been
modified. Assess compliance from retrieved documents.

**(d) Notice of dissatisfaction or equivalent**

Has a notice of dissatisfaction or equivalent been issued? Retrieve
it. Was it issued within the period confirmed from the retrieved
Contract Data?

**If no notice of dissatisfaction has been retrieved after searching
AND the period appears to have elapsed from retrieved dates:**
Flag immediately that the decision may be final and binding.
State the decision date, the period from retrieved Contract Data
(or state CANNOT CONFIRM if not retrieved), and the consequence.

**If the period cannot be confirmed because the Contract Data has
not been retrieved:**
State CANNOT CONFIRM whether the decision is final and binding.

**(e) Arbitration**

Has arbitration been commenced? Retrieve the notice. Under the
rules and at the seat confirmed from the retrieved amendment
document? Within any limitation period stated in retrieved documents?

### Step 5 — Assess limitation periods
*Contract-type-agnostic*

From retrieved documents:
- Is there an express limitation period in the retrieved amendment
  document or Contract Agreement?
- What is the governing law confirmed from retrieved documents?

**Do not state any limitation period without a retrieved source.**
If no express limitation period is in the retrieved contract documents:
state the governing law confirmed from retrieved documents and note
that the applicable limitation period under that governing law cannot
be confirmed from the warehouse — it would require legal advice on
the applicable statutory period.

---

## Classification and decision rules

**Dispute board / adjudication decision status:**

Decision retrieved, dissatisfaction period confirmed from retrieved
Contract Data, period has elapsed, no notice retrieved →
POTENTIALLY FINAL AND BINDING — flag immediately; state decision
date, period source, and consequence

Decision retrieved, notice of dissatisfaction issued within confirmed
period → INTERIM BINDING — must be complied with; subject to arbitration

Decision retrieved, dissatisfaction period not confirmed →
CANNOT CONFIRM whether decision is final or interim — flag

Decision not retrieved after searching →
NOT FOUND IN WAREHOUSE — cannot confirm issuance or status

**Notice of dissatisfaction:**

Retrieved, issued within confirmed period → TIMELY
Retrieved, issued outside confirmed period → POTENTIALLY LATE —
flag; state period from retrieved Contract Data and days elapsed
Not retrieved AND period appears elapsed → POTENTIALLY NOT ISSUED —
flag; state consequence
Period not confirmed → CANNOT CONFIRM timeliness

**Contract administrator determination step:**

Confirmed applicable from Layer 2b AND amendment document →
assess whether step was completed
Not applicable under confirmed standard form → NOT APPLICABLE —
state basis from retrieved documents

**Limitation period:**

Express period in retrieved contract documents → state period and source
No express period in retrieved contract documents → CANNOT CONFIRM
from warehouse — state governing law and flag that statutory period
requires legal advice

---

## When to call tools

**Signal:** Dispute board or adjudication decision referenced in
correspondence but not retrieved
**Action:** `get_related_documents` with document types "Dispute Board
Decision", "Adjudication Decision"; `search_chunks` with query
"adjudication decision board [claim reference]"
**Look for:** The decision document, its date, and the party required
to comply

**Signal:** Dispute resolution clause in amendment document not
retrieved
**Action:** `search_chunks` with query "dispute resolution arbitration
particular conditions seat rules"; `get_document` on the amendment
document ID if known
**Look for:** The arbitration clause — rules, seat, and any amendments
or replacements of the standard mechanism

**Signal:** Notice of dissatisfaction referenced but its date cannot
be confirmed
**Action:** `get_document` on the notice document if available;
`search_chunks` with query "notice dissatisfaction [party]
[approximate date]"
**Look for:** The full notice with its date

**Signal:** Contract Data not retrieved — prescribed periods unknown
**Action:** `search_chunks` with query "contract data prescribed
periods determination notice dissatisfaction"; `get_document`
on the Contract Data document ID if known
**Look for:** The periods prescribed for each step in the dispute
procedure

**Signal:** Layer 2b dispute resolution provision not retrieved
**Action:** `search_chunks` with `layer_type = '2b'` and query
"[standard form name] dispute resolution adjudication arbitration"
**Look for:** Standard form dispute resolution provision

---

## Always flag — regardless of query

1. **Decision with no notice of dissatisfaction found** — if a decision
   is in the warehouse and no notice of dissatisfaction has been found
   after searching: flag immediately; state the decision date, the
   period from retrieved Contract Data (or CANNOT CONFIRM), and that
   the decision may be final and binding.

2. **Non-compliance with binding decision** — if a binding decision
   requires payment or action and no compliance evidence is in the
   retrieved documents: flag; state the decision requirement.

3. **Procedural step skipped or out of sequence from retrieved
   documents** — flag; state the step and its potential effect on
   the arbitration.

4. **Limitation period approaching or potentially elapsed based on
   retrieved dates** — flag; state what has been retrieved to support
   this assessment.

5. **Amendment document replaces standard dispute resolution
   mechanism** — always flag; state the replacement mechanism from
   retrieved documents.

6. **Contract Data not retrieved — prescribed periods unknown** —
   flag; state that timeliness of each procedural step cannot be
   confirmed.

7. **Governing standard not retrieved from Layer 2b** — flag when
   the standard form dispute resolution provision could not be
   retrieved; state what standard would need to be ingested.

---

## Output format

```
## Dispute Resolution Procedure Assessment

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
[State whether the dispute resolution provision for the confirmed
standard form was retrieved from Layer 2b. If not: state CANNOT CONFIRM —
STANDARD FORM NOT IN WAREHOUSE and list which analysis steps
are affected.]

### Applicable Dispute Resolution Mechanism
Source: [amendment document reference / CANNOT CONFIRM — not retrieved]
Mechanism: [standard form mechanism retained / REPLACED — state replacement /
CANNOT CONFIRM]
Amendments to standard mechanism: [from retrieved amendment document /
NONE FOUND / CANNOT CONFIRM]

### Prescribed Periods (from retrieved Contract Data)
[For each period — state the value and source. If not retrieved:
state CANNOT CONFIRM.]
Determination period: [value and source / CANNOT CONFIRM / NOT APPLICABLE]
Adjudication/board decision period: [value and source / CANNOT CONFIRM]
Dissatisfaction notice period: [value and source / CANNOT CONFIRM]
Amicable settlement period: [value and source / CANNOT CONFIRM]

### Dispute Register

| # | Claim ref | Determination | Board decision | Dissatisfaction notice | Arbitration | Status |
|---|---|---|---|---|---|---|
| 1 | [ref] | [date/NOT ISSUED/NOT CONFIRMED/N/A] | [date/NOT ISSUED/NOT FOUND] | [date/NOT FOUND] | [date/NOT COMMENCED] | [status] |

### Findings by Dispute

**[Claim reference]**

*Contract Administrator Determination:*
Applicable under confirmed standard form: [YES / NOT APPLICABLE /
CANNOT CONFIRM — Layer 2b not retrieved]
Submitted: [YES — date / NO / NOT CONFIRMED]
Determination issued: [YES — date / NO / DEEMED — basis from
retrieved documents]
Within prescribed period: [YES / NO / CANNOT CONFIRM — period not retrieved]
Source: [document reference]

*Adjudication / Dispute Board Referral:*
Referred: [YES — date / NO / NOT CONFIRMED FROM WAREHOUSE]
Within permitted period: [YES / NO / CANNOT CONFIRM — period not retrieved]
Constitution confirmed: [YES — source / NOT CONFIRMED FROM RETRIEVED DOCUMENTS]
Source: [document reference]

*Decision:*
Issued: [YES — date / NOT FOUND IN WAREHOUSE]
Within prescribed period: [YES / NO / CANNOT CONFIRM — period not retrieved]
Decision status: [INTERIM BINDING / POTENTIALLY FINAL AND BINDING /
CANNOT CONFIRM]
Compliance by obligated party: [YES — source / NO — source / NOT ASSESSABLE]
Source: [document reference]

*Notice of Dissatisfaction / Equivalent:*
Issued: [YES — date and issuing party / NOT FOUND IN WAREHOUSE]
Within prescribed period: [YES / NO — days elapsed vs period from
retrieved Contract Data / CANNOT CONFIRM — period not retrieved]
Effect: [Decision remains interim binding / Decision POTENTIALLY FINAL
AND BINDING / CANNOT CONFIRM]
Source: [document reference]

*Arbitration:*
Commenced: [YES — date / NOT COMMENCED / NOT CONFIRMED]
Rules: [from retrieved amendment document / CANNOT CONFIRM]
Seat: [from retrieved amendment document / CANNOT CONFIRM]
Within limitation period: [YES / NO / CANNOT CONFIRM — period not
established from retrieved documents]
Source: [document reference]

*Limitation Period:*
Express period in retrieved documents: [YES — value and source / NOT FOUND]
Governing law: [from retrieved documents / CANNOT CONFIRM]
Assessment: [WITHIN PERIOD — basis / POTENTIALLY ELAPSED — basis /
CANNOT CONFIRM FROM RETRIEVED DOCUMENTS]

Finding: [from retrieved documents only]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any procedural step, period, or
mechanism from this section without first confirming it from retrieved
project documents.*

**Dispute resolution structure — analytical reference:**
Standard forms of contract provide a structured escalation process
for disputes. Most include some form of binding interim decision
mechanism (adjudication board, dispute board, or equivalent) before
arbitration. Some include a mandatory contract administrator
determination step. The exact sequence, time periods, and
consequences of non-compliance vary by standard form and version.
Amendment documents frequently modify or replace the standard
mechanism. Always retrieve the applicable provision from Layer 2b
and confirm the project-specific position from Layer 1.

**Interim binding decisions — analytical reference:**
Most standard form dispute board or adjudication mechanisms produce
decisions that are binding on an interim basis — meaning the parties
must comply even if a notice of dissatisfaction has been issued.
Failure to comply is typically a separate contractual breach that
can be referred to arbitration independently of the underlying
dispute. Confirm this principle from the retrieved Layer 2b provision
and check whether the amendment document modifies it.

**Limitation periods — analytical reference:**
The applicable limitation period for commencing arbitration or legal
proceedings depends on the governing law. Express limitation periods
may appear in the contract. Where no express period is stated, the
applicable statutory period under the confirmed governing law applies.
The governing law must be confirmed from the retrieved contract
documents — do not assume.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies to
any contract form. All characterisations grounded in retrieved warehouse
documents only.*
