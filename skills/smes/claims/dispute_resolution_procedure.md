# Dispute Resolution Procedure

**Skill type:** Contract-type-specific
The dispute resolution mechanism differs fundamentally by FIDIC book
and edition. The Silver Book has no Engineer determination step.
FIDIC 2017 introduces deemed rejection where the 1999 edition does
not. GCC Particular Conditions frequently replace the standard FIDIC
DAB/DAAB with local arbitration centre rules or government dispute
committees. All of these must be confirmed from the retrieved
Particular Conditions — not assumed.
**Layer dependency:**
- Layer 1 — project documents: Particular Conditions (dispute
  resolution clause); Contract Data (prescribed periods); DAB/DAAB
  decision; Notice of Dissatisfaction; arbitration notice; Engineer's
  determination; claim correspondence establishing the dispute history
- Layer 2 — reference standards: FIDIC Clause 20 (1999) or Clause 21
  (2017) dispute resolution procedure for the confirmed book and
  edition
**Domain:** Claims & Disputes SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when retrieved chunks contain a DAB or DAAB decision, a Notice
of Dissatisfaction, an arbitration notice, or a query about whether a
dispute has been properly escalated. Apply when a claim has been
rejected or not responded to and the next procedural step is in
question. Apply when assessing limitation periods for unresolved
disputes.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings and the claim history from
notice_compliance and eot_quantification findings.

From the invoking orchestrator extract:
- Confirmed FIDIC book and edition
- Dispute resolution mechanism as stated in the retrieved Particular
  Conditions
- Governing law as confirmed from retrieved documents
- Arbitration rules and seat as stated in the retrieved Particular
  Conditions

**If book type is UNCONFIRMED:** State CANNOT ASSESS the applicable
dispute resolution procedure. The procedure differs materially between
books and editions — analysis without confirmed book type is not
possible.

**If the Particular Conditions have not been retrieved:**
State CANNOT CONFIRM the dispute resolution mechanism, the prescribed
periods, or the arbitration rules. Do not apply the General Conditions
mechanism without confirming it has not been amended or replaced.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The Particular Conditions — specifically the dispute resolution
  clause and any amendment or replacement of the standard FIDIC
  mechanism
- The Contract Data — all prescribed periods (determination period,
  DAB/DAAB decision period, NOD period, amicable settlement period)
- The Engineer's determination (Red/Yellow only)
- The DAB or DAAB decision (if issued)
- The Notice of Dissatisfaction (if issued)
- The arbitration notice (if issued)
- The original claim submission and Engineer's response establishing
  the dispute history

**For each prescribed period:** Extract from the retrieved Contract
Data. Do not apply any period from the standard FIDIC text without
confirming it has not been amended in the retrieved Contract Data.

**If the Contract Data is not retrieved:**
State CANNOT CONFIRM any prescribed period. Do not state any period.

**If the dispute resolution clause in the Particular Conditions has
not been retrieved:**
State CANNOT CONFIRM the applicable mechanism. Do not assume the
General Conditions DAB/DAAB process applies.

### Layer 2 documents to retrieve (reference standards)

After confirming book type, call `search_chunks` to retrieve from
Layer 2:
- FIDIC Clause 20 dispute resolution procedure (1999) or Clause 21
  (2017) for the confirmed book and edition — the standard mechanism
  for structural comparison

**Purpose:** To establish the standard FIDIC dispute resolution
structure so that any Particular Conditions amendment or replacement
can be assessed against it. The mechanism to apply is always the
version in the retrieved Particular Conditions.

---

## Analysis workflow

### Step 1 — Confirm the applicable dispute resolution mechanism
*Contract-type-specific*

From the retrieved Particular Conditions:
- What dispute resolution mechanism is specified? Is the standard
  FIDIC DAB/DAAB retained or replaced?
- If retained: what amendments have been made to the standard
  procedure or to the prescribed periods?
- If replaced: what mechanism replaces it (local arbitration centre
  rules, government dispute committee, courts)?

**The mechanism to apply is the version in the retrieved Particular
Conditions.** Do not apply the General Conditions mechanism without
confirmation.

If the Particular Conditions have not been retrieved: state CANNOT
CONFIRM the applicable mechanism. Flag this as a critical gap.

### Step 2 — Extract all prescribed periods from the Contract Data
*Contract-type-specific*

From the retrieved Contract Data extract:
- Period for Engineer's determination (Red/Yellow only — 2017 editions)
- Period for DAB/DAAB decision
- Period for Notice of Dissatisfaction after determination or decision
- Period for amicable settlement attempt
- Any other prescribed period stated in the retrieved Contract Data

**Do not apply any period from the standard FIDIC General Conditions
without first confirming it has not been amended in the retrieved
Contract Data.** If the Contract Data has not been retrieved: state
CANNOT CONFIRM any prescribed period.

### Step 3 — Map the dispute history from retrieved documents
*Contract-type-agnostic*

From all retrieved documents, establish the sequence of steps that
have occurred:
- When was the claim submitted?
- When was the Engineer's determination issued (Red/Yellow only)?
- When was the dispute referred to the DAB/DAAB?
- When was the DAB/DAAB decision issued?
- Was a Notice of Dissatisfaction issued?
- Has arbitration been commenced?

**Establish each step only from retrieved documents.** If a step
cannot be confirmed from retrieved documents: state NOT CONFIRMED
FROM WAREHOUSE DOCUMENTS for that step.

### Step 4 — Assess each procedural step in sequence
*Contract-type-specific*

Apply the procedure confirmed from the retrieved Particular Conditions.
The sequence must be applied in order — each step gates the next.

**(a) Engineer's determination — Red Book and Yellow Book only**
*Not applicable to Silver Book*

Has the claim been submitted to the Engineer for determination?
Retrieve the determination. Was it issued within the period confirmed
from the retrieved Contract Data?

Under FIDIC 2017: if the determination period has elapsed and no
determination was issued — from retrieved documents confirm whether
a deemed rejection has occurred. The deemed rejection triggers the
NOD period. Confirm the deemed rejection trigger from the retrieved
Contract Data period — not from the standard form default.

Under FIDIC 1999: there is no express time limit on the Engineer's
determination in the standard General Conditions. A failure to
determine does not automatically trigger NOD rights unless the
retrieved Particular Conditions include a deemed determination
mechanism. Confirm from retrieved documents.

**(b) DAB/DAAB referral**

Has the dispute been referred? Retrieve the referral document.
Was it made within the permitted period confirmed from retrieved
Contract Data? Was the DAB/DAAB properly constituted — confirm the
appointment mechanism from the retrieved Particular Conditions.

**(c) DAB/DAAB decision**

Has a decision been issued? Retrieve it. Was it issued within the
period confirmed from retrieved Contract Data?

The decision is binding on an interim basis — confirm this from the
retrieved FIDIC clause (Layer 2) and check whether the retrieved
Particular Conditions amend this position.

Has the party required to comply done so? Assess from retrieved
payment certificates or correspondence.

**(d) Notice of Dissatisfaction**

Has an NOD been issued? Retrieve it. Was it issued within the period
confirmed from the retrieved Contract Data?

**If no NOD has been retrieved after searching AND the NOD period
appears to have elapsed from retrieved dates:**
Flag immediately that the DAB/DAAB decision may be final and binding.
State the decision date, the NOD period from retrieved Contract Data
(or state CANNOT CONFIRM if not retrieved), and the consequence.

**If the NOD period cannot be confirmed because the Contract Data
has not been retrieved:**
State CANNOT CONFIRM whether the decision is final and binding.

**(e) Arbitration**

Has arbitration been commenced? Retrieve the notice. Under the
rules and at the seat confirmed from the retrieved Particular
Conditions? Within any limitation period stated in the retrieved
documents?

### Step 5 — Assess limitation periods
*Contract-type-agnostic*

From retrieved documents:
- Is there an express limitation period in the retrieved Particular
  Conditions or Contract Agreement?
- What is the governing law confirmed from retrieved documents?

**Do not state any limitation period without a retrieved source.**
If no express limitation period is in the retrieved contract documents:
state the governing law confirmed from retrieved documents and note
that the applicable limitation period under that governing law cannot
be confirmed from the warehouse — it would require legal advice on
the applicable statutory period.

---

## Classification and decision rules

**DAB/DAAB decision status:**

Decision retrieved, NOD period confirmed from retrieved Contract Data,
NOD period has elapsed and no NOD retrieved →
POTENTIALLY FINAL AND BINDING — flag immediately; state decision date,
NOD period source, and consequence

Decision retrieved, NOD issued within confirmed period →
INTERIM BINDING — must be complied with; subject to arbitration

Decision retrieved, NOD period not confirmed (Contract Data not
retrieved) → CANNOT CONFIRM whether decision is final or interim —
flag; state what is missing

Decision not retrieved after searching →
NOT FOUND IN WAREHOUSE — cannot confirm issuance or status

**Notice of Dissatisfaction:**

NOD retrieved, issued within confirmed period → TIMELY
NOD retrieved, issued outside confirmed period → POTENTIALLY LATE —
flag; state the period from retrieved Contract Data and the days
elapsed
NOD not retrieved AND NOD period appears elapsed → POTENTIALLY NOT
ISSUED — flag; consequence stated
NOD period not confirmed (Contract Data not retrieved) →
CANNOT CONFIRM NOD timeliness

**Silver Book:**

Silver Book confirmed AND dispute resolution steps show an Engineer
determination step → FLAG — Silver Book has no Engineer determination;
the Engineer determination step does not apply; assess whether the
Particular Conditions introduce a bespoke mechanism

**Limitation period:**

Express period in retrieved contract documents → state period and source
No express period in retrieved contract documents → CANNOT CONFIRM
from warehouse — state governing law and flag that statutory period
requires legal advice

---

## When to call tools

**Signal:** DAB or DAAB decision referenced in correspondence but
not retrieved
**Action:** `get_related_documents` with document types "DAB Decision",
"DAAB Decision"; `search_chunks` with query "adjudication board
decision [claim reference]"
**Look for:** The decision document, its date, and the party required
to comply

**Signal:** Dispute resolution clause in PC not retrieved
**Action:** `search_chunks` with query "dispute resolution arbitration
particular conditions seat rules"; `get_document` on the PC document
ID if known
**Look for:** The arbitration clause — rules, seat, and any amendments
or replacements of the standard FIDIC mechanism

**Signal:** NOD referenced but its date cannot be confirmed
**Action:** `get_document` on the NOD document ID if available;
`search_chunks` with query "notice dissatisfaction [party]
[approximate date]"
**Look for:** The full NOD document with its date

**Signal:** Contract Data not retrieved — prescribed periods unknown
**Action:** `search_chunks` with query "contract data prescribed
periods determination DAB notice dissatisfaction"; `get_document`
on the Contract Data document ID if known
**Look for:** The periods prescribed for each step in the dispute
procedure

**Signal:** Layer 2 FIDIC dispute resolution clause not retrieved
**Action:** `search_chunks` with query "[FIDIC book] [edition]
clause 20 21 dispute adjudication DAB DAAB"
**Look for:** Standard FIDIC Clause 20 (1999) or Clause 21 (2017)
for the confirmed book

---

## Always flag — regardless of query

1. **DAB/DAAB decision with no NOD found** — if a decision is in
   the warehouse and no NOD has been found after searching: flag
   immediately; state the decision date, the NOD period from
   retrieved Contract Data (or CANNOT CONFIRM), and that the
   decision may be final and binding.

2. **Non-compliance with binding DAB/DAAB decision** — if a binding
   decision requires payment or action and no compliance evidence
   is in the retrieved documents: flag; state the decision requirement.

3. **Procedural step skipped or out of sequence from retrieved
   documents** — flag; state the step and its potential effect on
   the arbitration.

4. **Limitation period approaching or potentially elapsed based on
   retrieved dates** — flag; state what has been retrieved to support
   this assessment.

5. **Particular Conditions replace standard FIDIC dispute resolution
   mechanism** — always flag; state the replacement mechanism from
   retrieved documents and note that the standard FIDIC DAB/DAAB
   process does not apply.

6. **Contract Data not retrieved — prescribed periods unknown** —
   flag; state that timeliness of each procedural step cannot be
   confirmed.

---

## Output format

```
## Dispute Resolution Procedure Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2 Reference Retrieved
[State whether FIDIC Clause 20/21 for the confirmed book and edition
was retrieved from Layer 2. If not: state analytical knowledge applied.]

### Applicable Dispute Resolution Mechanism
Source: [Particular Conditions reference / CANNOT CONFIRM — PC not retrieved]
Mechanism: [Standard FIDIC DAB/DAAB retained / REPLACED — state replacement /
CANNOT CONFIRM]
Amendments to standard mechanism: [from retrieved PC / NONE FOUND / CANNOT CONFIRM]

### Prescribed Periods (from retrieved Contract Data)
[For each period — state the value and source. If not retrieved:
state CANNOT CONFIRM.]
Engineer's determination period: [value and source / CANNOT CONFIRM]
DAB/DAAB decision period: [value and source / CANNOT CONFIRM]
NOD period: [value and source / CANNOT CONFIRM]
Amicable settlement period: [value and source / CANNOT CONFIRM]

### Dispute Register

| # | Claim ref | Determination | DAB/DAAB decision | NOD | Arbitration | Status |
|---|---|---|---|---|---|---|
| 1 | [ref] | [date/NOT ISSUED/NOT CONFIRMED/N/A] | [date/NOT ISSUED/NOT FOUND] | [date/NOT FOUND] | [date/NOT COMMENCED] | [status] |

### Findings by Dispute

**[Claim reference]**

*Engineer's Determination (Red/Yellow only):*
Applicable: [YES / NOT APPLICABLE — Silver Book]
Submitted: [YES — date / NO / NOT CONFIRMED]
Determination issued: [YES — date / NO / DEEMED REJECTED — basis from
retrieved documents]
Within prescribed period: [YES / NO / CANNOT CONFIRM — period not retrieved]
Source: [document reference]

*DAB/DAAB Referral:*
Referred: [YES — date / NO / NOT CONFIRMED FROM WAREHOUSE]
Within permitted period: [YES / NO / CANNOT CONFIRM — period not retrieved]
Constitution confirmed: [YES — source / NOT CONFIRMED FROM RETRIEVED DOCUMENTS]
Source: [document reference]

*DAB/DAAB Decision:*
Issued: [YES — date / NOT FOUND IN WAREHOUSE]
Within prescribed period: [YES / NO / CANNOT CONFIRM — period not retrieved]
Decision status: [INTERIM BINDING / POTENTIALLY FINAL AND BINDING /
CANNOT CONFIRM]
Compliance by obligated party: [YES — source / NO — source / NOT ASSESSABLE]
Source: [document reference]

*Notice of Dissatisfaction:*
Issued: [YES — date and issuing party / NOT FOUND IN WAREHOUSE]
Within prescribed period: [YES / NO — days elapsed vs period from
retrieved Contract Data / CANNOT CONFIRM — period not retrieved]
Effect: [Decision remains interim binding / Decision POTENTIALLY FINAL
AND BINDING / CANNOT CONFIRM]
Source: [document reference]

*Arbitration:*
Commenced: [YES — date / NOT COMMENCED / NOT CONFIRMED]
Rules: [from retrieved PC / CANNOT CONFIRM]
Seat: [from retrieved PC / CANNOT CONFIRM]
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

**FIDIC dispute resolution structure — analytical reference:**
FIDIC 1999 (all books): Engineer determination → DAB referral →
DAB decision (interim binding) → NOD → amicable settlement →
ICC arbitration (all periods from Contract Data). The 1999 edition
has no deemed rejection for failure to determine. FIDIC 2017:
Engineer determination with time limit (deemed rejection on expiry)
→ DAAB referral → DAAB decision (interim binding) → NOD →
amicable settlement → ICC arbitration. Silver Book (both editions):
no Engineer determination step — dispute goes directly to DAB/DAAB.
All periods are General Conditions defaults that may be amended in
the Contract Data — retrieve from Layer 1 before applying any period.

**Pay-now-argue-later — analytical reference:**
A DAB/DAAB decision is binding on an interim basis under all FIDIC
books and editions. The party required to comply must do so even
if an NOD has been issued. Failure to comply is a separate contractual
breach. Under FIDIC 2017, non-compliance can be referred to
arbitration separately from the underlying dispute. Confirm this
principle from the retrieved Layer 2 clause — check whether the
retrieved Particular Conditions amend it.

**GCC arbitration institutions — analytical reference:**
ICC is the most common for international contracts. DIAC for DIFC
law or Dubai-specified contracts. ADCCAC for Abu Dhabi government
contracts. SCCA for Saudi disputes. QICCA for Qatar disputes.
Government project Particular Conditions frequently specify local
institutions or government dispute committees — the institution in
the retrieved Particular Conditions governs.

**Limitation periods — analytical reference:**
UAE Civil Code: 15 years general; 10 years commercial. Saudi Arabia:
varies by claim type. Qatar Civil Code: 10 years general. These are
general statutory positions for contextual reference only — the
governing law must be confirmed from retrieved documents and the
applicable period requires legal advice if not expressly stated
in the retrieved contract.
