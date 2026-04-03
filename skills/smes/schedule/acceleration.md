# Acceleration

**Skill type:** Mixed
- Contract-type-specific: the entitlement basis for directed and
  constructive acceleration depends on the retrieved Particular
  Conditions and the confirmed book type
- Contract-type-agnostic: the identification of acceleration
  measures, the assessment of acceleration costs, and the
  distinction between directed and constructive acceleration apply
  regardless of book type
**Layer dependency:**
- Layer 1 — project documents: acceleration instruction (if any);
  Particular Conditions (acceleration clause if any, EOT clause);
  Contract Data; correspondence surrounding the acceleration;
  resource records showing additional resources deployed;
  EOT claim and any response; cost records for acceleration measures
- Layer 2 — reference standards: FIDIC relevant clauses for the
  confirmed book and edition; SCL Protocol 2nd Edition 2017
  (acceleration principles)
**Domain:** Schedule & Programme SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when retrieved chunks contain an acceleration instruction,
an acceleration cost claim, correspondence about speeding up the
works, or evidence of additional resources deployed beyond the
baseline programme. Apply when an EOT has been denied or not
responded to and the Contractor appears to have accelerated to
meet the original completion date — assess for constructive
acceleration.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings and eot_quantification
findings (if available).

From the invoking orchestrator extract:
- Confirmed FIDIC book and edition
- Whether an acceleration clause exists in the retrieved
  Particular Conditions

From eot_quantification findings (if available):
- Whether an EOT was claimed and what the response was (if any)
- Whether the EOT was denied or not responded to within the
  prescribed period

**Two distinct types of acceleration must be assessed separately:**

**Directed acceleration:** A formal instruction from the Engineer
or Employer's Representative to accelerate the works. Creates a
direct contractual entitlement to recover acceleration costs.

**Constructive acceleration:** No formal instruction, but the
Contractor has been denied an EOT it is entitled to (or the EOT
has not been responded to) and has accelerated to avoid LDs.
Constructive acceleration requires the Contractor to demonstrate
all three conditions from the retrieved documents.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- Any acceleration instruction issued by the Engineer or
  Employer's Representative
- The Particular Conditions — any acceleration clause and the
  EOT clause
- Contract Data — prescribed EOT response period
- The EOT claim and the Engineer's response (for constructive
  acceleration)
- Correspondence surrounding the acceleration — letters requesting
  acceleration, notices of constructive acceleration
- Resource records showing additional resources deployed during
  the acceleration period (manpower reports, plant returns)
- Cost records for overtime, additional shifts, additional plant
- The programme — baseline and updates showing the acceleration
  period

**If no acceleration instruction is retrieved:**
Assess for constructive acceleration using the conditions below.
Do not conclude directed acceleration without a retrieved instruction.

**If no cost records are retrieved:**
State CANNOT VERIFY acceleration costs from warehouse documents.

### Layer 2 documents to retrieve (reference standards)

Call `search_chunks` to retrieve from Layer 2:
- FIDIC acceleration clause for the confirmed book and edition
  (if a standard form acceleration clause exists)
- SCL Protocol 2nd Edition 2017 — acceleration principles and
  constructive acceleration conditions

**Purpose:** To establish the standard FIDIC acceleration framework
and the SCL Protocol constructive acceleration conditions. The
project-specific terms are in the retrieved Particular Conditions.

---

## Analysis workflow

### Step 1 — Identify the type of acceleration from retrieved documents
*Contract-type-agnostic*

From the retrieved documents, determine:
- Has a formal acceleration instruction been issued? Retrieve it.
- If no instruction: is there evidence in retrieved documents that
  the Contractor accelerated to meet the original completion date
  following an EOT denial or non-response?

**Directed and constructive acceleration are mutually exclusive
scenarios.** Identify which applies from the retrieved documents
before proceeding.

### Step 2 — Assess directed acceleration entitlement
*Contract-type-specific*
*Only if a formal acceleration instruction has been retrieved*

From the retrieved Particular Conditions:
- Is there an express acceleration clause? Extract it.
- Does the retrieved clause provide for reimbursement of
  acceleration costs? What are the conditions?
- Was the instruction issued by the correct authority (confirmed
  from engineer_identification findings)?
- Was it issued in writing and in compliance with the Clause 1.3
  notice requirements confirmed from the retrieved contract?

**If no acceleration clause exists in the retrieved Particular
Conditions and the General Conditions have been retrieved from
Layer 2:** Note the absence and state that the entitlement basis
must be assessed under the general Employer instruction framework.

If the Particular Conditions have not been retrieved: state
CANNOT CONFIRM the entitlement basis for directed acceleration.

### Step 3 — Assess constructive acceleration conditions
*Contract-type-agnostic*
*Only if no formal acceleration instruction has been retrieved*

Constructive acceleration requires all three of the following
conditions to be established from retrieved documents:

**Condition 1 — EOT entitlement exists:**
The Contractor was entitled to an EOT for an Employer Risk Event
or other qualifying event under the retrieved PC. This condition
is assessed from eot_quantification findings — do not reassess
here. State the eot_quantification conclusion.

**Condition 2 — EOT denied or not responded to:**
The Engineer or Employer's Representative either:
- Denied the EOT claim (retrieve the denial letter), or
- Failed to respond within the prescribed period (confirm the
  period from the retrieved Contract Data)

If the prescribed EOT response period cannot be confirmed from
the retrieved Contract Data: state CANNOT CONFIRM whether the
non-response condition is met.

**Condition 3 — Contractor gave notice of constructive
acceleration and its cost:**
The Contractor must have notified the Employer/Engineer that it
was accelerating and stated the cost. Retrieve the notice.

If no notice has been retrieved after searching: state CANNOT
CONFIRM the notice condition is met. Note that absent a
constructive acceleration notice, the claim faces a procedural
challenge regardless of the underlying entitlement.

**If any condition is not met or cannot be confirmed from retrieved
documents:** State CONSTRUCTIVE ACCELERATION CONDITIONS NOT FULLY
ESTABLISHED FROM RETRIEVED DOCUMENTS — state which conditions are
met and which are not.

### Step 4 — Identify acceleration measures from retrieved records
*Contract-type-agnostic*

From the retrieved resource records, manpower reports, and
programme updates, identify:
- What additional resources were deployed during the acceleration
  period? (Additional labour gangs, additional shifts, overtime,
  additional plant)
- When were the additional resources deployed? (State the period
  from retrieved records)
- Is the deployment of additional resources evidenced in
  contemporaneous records?

**Do not accept the claim's description of acceleration measures
without corroborating retrieved records.** If resource records
for the acceleration period have not been retrieved: state
CANNOT VERIFY the acceleration measures from warehouse documents.

### Step 5 — Assess acceleration costs
*Contract-type-agnostic*

From the retrieved cost records:
- What costs are claimed? List from the retrieved cost claim.
- Are the claimed costs evidenced by retrieved records
  (timesheets, overtime payroll, plant hire invoices)?
- Are the rates applied consistent with the retrieved contract
  rates or actual records?
- Does the claimed cost period correspond to the acceleration
  period evidenced in the retrieved records?

For each head of acceleration cost, assess the same evidential
standard as prolongation_cost: actual cost supported by
retrieved records, verifiable rates, period consistent with
retrieved resource deployment.

**Do not verify any acceleration cost without a retrieved
source document.**

### Step 6 — Assess the contract administrator's response
*Contract-type-specific*

From the retrieved determination or response:
- Has the Engineer or Employer's Representative responded to
  the acceleration claim?
- What position has been taken on entitlement and quantum?

If no response has been retrieved: state CANNOT ASSESS the
contract administrator's position on acceleration.

---

## Classification and decision rules

**Directed acceleration:**

Formal instruction retrieved, authority confirmed, acceleration
clause in retrieved PC providing for reimbursement →
DIRECTED ACCELERATION ESTABLISHED — proceed with cost assessment
Formal instruction retrieved but no acceleration clause in
retrieved PC → ENTITLEMENT BASIS UNCERTAIN — flag; the
instruction may still create an obligation to pay under general
principles; note that the basis should be assessed legally
Instruction retrieved but authority not confirmed →
AUTHORITY UNCONFIRMED — flag; the instruction may not be binding
without confirmed authority

**Constructive acceleration:**

All three conditions evidenced in retrieved documents →
CONSTRUCTIVE ACCELERATION CONDITIONS ESTABLISHED — proceed
with cost assessment
Two conditions met, one not established from retrieved documents →
CONDITIONS PARTIALLY ESTABLISHED — flag; state which condition
is missing and its evidential basis
Eot_quantification shows no EOT entitlement →
CONSTRUCTIVE ACCELERATION FAILS AT CONDITION 1 — no EOT
entitlement to support the acceleration claim
No constructive acceleration notice retrieved →
CONDITION 3 NOT MET FROM RETRIEVED DOCUMENTS — flag; state
the procedural vulnerability

**Acceleration cost:**

Cost evidenced by retrieved records for the acceleration period →
SUPPORTED — state quantum and source documents
Cost claimed but records not retrieved for acceleration period →
CANNOT VERIFY FROM WAREHOUSE DOCUMENTS — flag

---

## When to call tools

**Signal:** Acceleration instruction referenced in correspondence
but not retrieved
**Action:** `get_related_documents` with document type "Engineer's
Instruction"; `search_chunks` with query "acceleration instruction
directed accelerate completion"
**Look for:** A formal instruction to accelerate

**Signal:** EOT claim response not retrieved — cannot confirm
whether EOT was denied
**Action:** `get_related_documents` with document type "Engineer's
Determination"; `search_chunks` with query "EOT extension time
response determination [claim reference]"
**Look for:** The Engineer's response to the EOT claim

**Signal:** Constructive acceleration notice referenced in claim
but not retrieved
**Action:** `search_chunks` with query "constructive acceleration
notice cost claim"; `get_related_documents` with document type
"Contractor's Letter", "Notice"
**Look for:** The Contractor's notice of constructive acceleration
and its cost

**Signal:** Resource records for acceleration period not retrieved
**Action:** `search_chunks` with query "manpower overtime additional
resources [acceleration period dates]"; `get_related_documents`
with document types "Manpower Report", "Resource Schedule"
**Look for:** Records showing additional resources during the
acceleration period

---

## Always flag — regardless of query

1. **Directed acceleration instruction issued without authority
   confirmation** — flag; state that the instruction's validity
   depends on authority confirmation from engineer_identification
   findings.

2. **Constructive acceleration claim where Condition 3 (notice)
   is not met from retrieved documents** — flag; state the
   procedural vulnerability in the absence of a retrieved notice.

3. **Acceleration costs claimed but no contemporaneous resource
   records retrieved** — flag; state that the quantum cannot be
   independently verified from warehouse documents.

4. **Overlap between acceleration cost claim and prolongation cost
   claim for the same period** — flag; the Contractor cannot recover
   both prolongation costs and acceleration costs for the same
   period without clear delineation — state the overlap period and
   the two claims.

5. **EOT entitlement not established from eot_quantification
   findings but constructive acceleration claimed** — flag;
   constructive acceleration cannot succeed without the underlying
   EOT entitlement.

---

## Output format

```
## Acceleration Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2 Reference Retrieved
[State whether FIDIC acceleration clause and SCL Protocol were
retrieved. If not: state analytical knowledge applied.]

### Acceleration Type Identified
Type: [DIRECTED / CONSTRUCTIVE / CANNOT DETERMINE]
Basis: [from retrieved documents]

### Directed Acceleration (if applicable)
Instruction retrieved: [YES — reference and date / NOT FOUND]
Issuing authority: [confirmed from engineer_identification /
CANNOT CONFIRM]
Acceleration clause in retrieved PC: [YES — describe / NOT FOUND /
CANNOT CONFIRM — PC not retrieved]
Entitlement basis: [from retrieved PC / UNCERTAIN — no clause found /
CANNOT CONFIRM]

### Constructive Acceleration (if applicable)
Condition 1 — EOT entitlement: [ESTABLISHED — from eot_quantification /
NOT ESTABLISHED / CANNOT CONFIRM]
Condition 2 — EOT denied or no response:
  Denial letter retrieved: [YES — date / NOT FOUND]
  Response period from Contract Data: [value / CANNOT CONFIRM]
  Assessment: [CONDITION MET / NOT MET / CANNOT CONFIRM]
Condition 3 — Acceleration notice issued:
  Notice retrieved: [YES — reference / NOT FOUND]
  Assessment: [CONDITION MET / NOT MET — notice not retrieved]
Overall: [CONDITIONS ESTABLISHED / PARTIALLY ESTABLISHED — state gap /
NOT ESTABLISHED]

### Acceleration Measures
Resource records retrieved: [YES — period and description / NOT FOUND]
Additional resources evidenced: [describe from retrieved records /
CANNOT VERIFY — records not retrieved]
Period of acceleration: [from retrieved records / CANNOT CONFIRM]

### Acceleration Cost Assessment

| Head | Amount claimed | Records retrieved | Period | Assessment |
|---|---|---|---|---|
| Overtime | [amount] | [YES/NO] | [dates] | [SUPPORTED/CANNOT VERIFY] |
| Additional resources | [amount] | [YES/NO] | [dates] | [assessment] |
| Additional plant | [amount] | [YES/NO] | [dates] | [assessment] |
| [other heads] | | | | |
| Total | [total] | | | |

### Contract Administrator Position
Response retrieved: [YES — reference / NOT FOUND IN WAREHOUSE]
Position on entitlement: [from retrieved response / CANNOT ASSESS]
Position on quantum: [from retrieved response / CANNOT ASSESS]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any acceleration principle or condition
from this section without first confirming the applicable terms from
retrieved project documents.*

**FIDIC acceleration — analytical reference:**
FIDIC does not contain a standard directed acceleration clause as
a standalone provision in the same way as some bespoke forms. The
Employer can instruct variations under Clause 13, which may include
an instruction to accelerate. Whether acceleration is specifically
provided for in the Particular Conditions is project-specific —
extract from Layer 1. The absence of an express clause does not
necessarily mean acceleration costs are irrecoverable — the
entitlement basis must be assessed from the retrieved documents.

**SCL Protocol constructive acceleration — analytical reference:**
The SCL Protocol recognises constructive acceleration where the
Contractor has been denied an EOT it is entitled to and has
accelerated to avoid LDs. The three conditions are: (1) EOT
entitlement exists; (2) the entitlement was denied or not responded
to; (3) the Contractor gave notice of acceleration and its cost.
All three conditions must be established from retrieved documents
before constructive acceleration can be assessed. Retrieve the
Protocol from Layer 2 and apply its principles only after
confirming them against the retrieved contract terms.
