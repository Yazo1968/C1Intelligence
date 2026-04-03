# Engineer Identification

**Skill type:** Mixed
- Contract-type-specific: the contract administrator role differs
  fundamentally between Red/Yellow Book (Engineer) and Silver Book
  (Employer's Representative). Authority scope, independence obligation,
  and determination mechanism are book-specific.
- Contract-type-agnostic: the requirement to identify the contract
  administrator from project documents, map delegated authority, and
  flag authority anomalies applies regardless of book type.
**Layer dependency:**
- Layer 1 — project documents: Contract Agreement, Particular
  Conditions, Engineer/Employer's Representative appointment letter,
  any delegation instruments, correspondence revealing actual authority
  exercised
- Layer 2 — reference standards: FIDIC Clause 3 (Engineer / Employer's
  Representative) for the relevant book and edition — structural
  comparison and authority scope
**Domain:** Legal & Contractual SME
**Invoked by:** Legal orchestrator

---

## When to apply this skill

Apply when a query concerns the identity, authority, or actions of the
contract administrator (Engineer or Employer's Representative), whether
a specific instruction or determination was within delegated authority,
whether the Engineer is acting with the required independence, or
whether a GCC split-role arrangement creates ambiguity about which
entity has authority for a specific action.

---

## Before you begin

### Foundational requirement
This skill requires the book type and edition to be confirmed.
Read the contract_assembly findings first. If book type is
UNCONFIRMED: state CANNOT ASSESS this skill. The contract administrator
role is fundamentally different between books — analysis without
confirmed book type is not possible.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The Particular Conditions (Clause 3 and any amendment)
- The Contract Data / Appendix to Tender (Engineer / Employer's
  Representative named entity)
- Engineer / Employer's Representative appointment letter or agreement
- Any delegation letters from the Engineer to a named representative
- Correspondence issued by the Engineer or Employer's Representative
  (to establish actual authority exercised in practice)
- Any Project Management Consultant (PMC) or Supervision Consultant
  appointment letter where a split-role arrangement may exist

**If the Particular Conditions are not retrieved:**
State CANNOT CONFIRM the Engineer's scope of authority, independence
position, or any amendment to the standard Clause 3 role.

**If no appointment document is retrieved:**
State CANNOT CONFIRM the identity of the named Engineer or Employer's
Representative from the project documents.

### Layer 2 documents to retrieve (reference standards)

After confirming book type from contract_assembly findings, call
`search_chunks` to retrieve from Layer 2:
- FIDIC Clause 3 for the confirmed book and edition (Engineer's duties
  and authority / Employer's Representative)
- FIDIC Clause 3.5 (1999) or Clause 3.7 (2017) — Engineer's
  determination provisions (Red and Yellow Book only)

**Purpose:** To establish what the standard FIDIC Clause 3 says, so
that Particular Conditions amendments can be assessed against the
baseline. Do not apply standard Clause 3 provisions without checking
whether they have been amended by the Particular Conditions.

---

## Analysis workflow

### Step 1 — Confirm the contract administrator role
*Contract-type-specific*

From the confirmed book type (contract_assembly findings) and the
retrieved Particular Conditions:

**Red Book / Yellow Book:**
The contract administrator is the Engineer. Retrieve the Engineer's
identity from the Contract Data or Appendix to Tender. The Engineer
acts on behalf of the Employer but has an independence obligation under
FIDIC when making determinations.

**Silver Book:**
There is no Engineer. The contract administrator is the Employer's
Representative. The Employer's Representative acts solely as the
Employer's agent — there is no independence obligation in the Silver
Book. Any reference to an "Engineer" in a Silver Book project is
anomalous — flag it.

**If book type is not confirmed:** State CANNOT IDENTIFY the contract
administrator role. Do not proceed.

### Step 2 — Identify the named contract administrator
*Contract-type-agnostic*

From the retrieved Contract Data, Appendix to Tender, or appointment
letter, identify:
- The named entity appointed as Engineer or Employer's Representative
- The named individual representative (if stated)
- The date of appointment (if retrievable)

**Do not assume any entity is the Engineer or Employer's Representative
without a retrieved document that names them.** If no appointment
document is found after searching: state CANNOT CONFIRM the identity
of the contract administrator from the warehouse documents.

### Step 3 — Assess delegated authority scope
*Contract-type-specific*

From the retrieved Particular Conditions, identify any amendment to
Clause 3 that defines or restricts the contract administrator's
authority. Key authority questions:

**Red Book / Yellow Book (contract-type-specific):**
- Is the Engineer's authority to approve variations restricted by a
  financial threshold requiring Employer consent? Extract the threshold
  from the Particular Conditions — do not apply any default.
- Is the Engineer required to obtain Employer consent before issuing
  specific instructions, determinations, or certificates? Extract from
  Particular Conditions.
- Does the Engineer have authority to grant EOT, determine claims, and
  issue payment certificates without Employer pre-approval? Extract
  from Particular Conditions.

**Silver Book (contract-type-specific):**
- The Employer's Representative acts on Employer instructions — there
  is no independence obligation. The scope of the Representative's
  authority is defined by the Employer's instructions, not by FIDIC.
  Retrieve the appointment letter or Employer instructions if available.

**If the Particular Conditions are not retrieved:**
State CANNOT CONFIRM the delegated authority scope. Do not state any
authority threshold or restriction.

### Step 4 — Assess Engineer's independence position
*Contract-type-specific — Red Book and Yellow Book only*
*Not applicable to Silver Book*

Under FIDIC (Red and Yellow, both editions), the Engineer must act
impartially when making determinations — not as the Employer's agent.
GCC Particular Conditions frequently modify this by requiring Employer
consent before the Engineer makes determinations, or by removing the
Engineer's independence obligation.

From the retrieved Particular Conditions, identify:
- Whether Clause 3.5 (1999) or Clause 3.7 (2017) has been amended
- Whether the Engineer is required to obtain Employer approval before
  making a determination or issuing a certificate
- Whether the independence obligation has been modified or removed

**Classify the Engineer's independence position based only on what
the retrieved Particular Conditions say.** If the Particular Conditions
have not been retrieved: state CANNOT ASSESS the independence position.

### Step 5 — Identify GCC split-role arrangements
*Contract-type-agnostic (pattern) / Contract-type-specific (implications)*

In GCC projects, the Engineer role is frequently split between a Project
Management Consultant (PMC) handling commercial and contractual
administration and a Supervision Consultant handling technical
supervision. This split is not recognised in standard FIDIC — it is a
GCC practice that creates ambiguity about which entity has authority
for which category of instruction.

From the retrieved documents, identify:
- Whether a PMC appointment document exists in the warehouse
- Whether a Supervision Consultant appointment document exists
- Whether the contract documents define which entity exercises which
  part of the Engineer's role
- Whether correspondence shows different entities acting as Engineer
  for different purposes

**Identify the split only from retrieved documents.** Do not assume
a split arrangement exists because a PMC or Supervision Consultant
appears in the warehouse — confirm from the documents which entity
is named as the Engineer in the contract and what authority each
entity has been delegated.

### Step 6 — Assess instructions and determinations issued
*Contract-type-agnostic*

If the query or context involves specific Engineer instructions or
determinations, assess for each:
- Was it issued by the named contract administrator or a delegated
  representative?
- Was it within the authority scope confirmed from the Particular
  Conditions?
- Was it issued in writing (required under all FIDIC books and editions)?
- Did it comply with the Clause 1.3 notice requirements (form, method,
  recipient)?

**Authority excess flag:** If a retrieved instruction or determination
was issued by an entity or individual whose authority cannot be confirmed
from the project documents, flag as AUTHORITY UNCONFIRMED. Do not
characterise this as valid or invalid without the authority source.

---

## Classification and decision rules

**Contract administrator identity:**
Named in retrieved Contract Data or appointment letter → CONFIRMED —
state entity and source document
Not found after searching → CANNOT CONFIRM — flag; state what was
searched and not found

**Delegated authority:**
Authority scope confirmed from retrieved Particular Conditions →
state scope and source document
Particular Conditions not retrieved → CANNOT CONFIRM authority scope

**Independence position (Red/Yellow only):**
Independence obligation present and unmodified in retrieved PC →
INDEPENDENT — cite source
Independence obligation modified in retrieved PC → MODIFIED — describe
the modification and cite source
Independence obligation absent from retrieved PC AND PC retrieved →
INDEPENDENCE OBLIGATION NOT FOUND IN RETRIEVED PC — flag
Particular Conditions not retrieved → CANNOT ASSESS

**Split-role arrangement:**
Confirmed from retrieved appointment documents → CONFIRMED SPLIT —
describe allocation and cite sources
Not found in retrieved documents → NOT IDENTIFIED FROM WAREHOUSE
DOCUMENTS — note this does not mean no split exists

---

## When to call tools

**Signal:** Contract Data or Appendix to Tender names an entity as
Engineer but no appointment letter has been retrieved
**Action:** `search_chunks` with query "[entity name] appointment
engineer"; `get_related_documents` with document type "Appointment
Letter" or "Consultant Agreement"
**Look for:** Appointment instrument confirming the entity's role and
scope

**Signal:** Instructions or correspondence in the warehouse reference
a PMC or Supervision Consultant acting as Engineer but no appointment
document establishes their authority
**Action:** `search_chunks` with query "PMC project management
consultant appointment authority engineer"; `get_related_documents`
with document type "Appointment Letter"
**Look for:** Appointment instrument defining which entity exercises
which part of the Engineer's role

**Signal:** Particular Conditions Clause 3 amendment is referenced
in the contract_assembly findings but the clause content has not been
retrieved
**Action:** `get_document` on the Particular Conditions document ID;
`search_chunks` with query "clause 3 engineer authority approval
Employer consent"
**Look for:** The specific amendment text — authority thresholds,
consent requirements, independence modifications

**Signal:** Layer 2 FIDIC Clause 3 has not been retrieved for the
confirmed book and edition
**Action:** `search_chunks` with query "[FIDIC book name] [edition]
clause 3 engineer authority"
**Look for:** Standard FIDIC Clause 3 text for structural comparison

---

## Always flag — regardless of query

1. **Silver Book with a document referencing an Engineer** — this is
   anomalous; the Silver Book has no Engineer; flag and identify the
   document that makes the reference.

2. **Engineer's independence modified or removed by Particular
   Conditions** — always flag; state the modification and its forensic
   implication for any determination or certificate in dispute.

3. **Instructions or determinations issued by an entity whose authority
   cannot be confirmed from retrieved documents** — always flag;
   state the instruction reference and what authority document is
   missing from the warehouse.

4. **Split-role arrangement confirmed or suspected but not formally
   documented in the retrieved contract documents** — always flag;
   state the split pattern identified and the absence of a formal
   authority allocation document.

5. **Employer consent requirement before Engineer determinations** —
   if the retrieved Particular Conditions require Employer consent
   before the Engineer can determine claims or certify payment, always
   flag; state the clause and its forensic implication for any
   contested determination.

---

## Output format

```
## Engineer Identification Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved relevant to this skill, with reference
numbers and dates.]

### Documents Not Retrieved
[List every document required for this analysis not found in the
warehouse. State which analysis steps are affected.]

### Layer 2 Reference Retrieved
[State whether FIDIC Clause 3 for the confirmed book and edition was
retrieved from Layer 2. If not: state that standard form text has been
applied from analytical knowledge.]

### Contract Administrator Role
Book type confirmed: [YES — from contract_assembly / NO — CANNOT ASSESS]
Role: [Engineer (Red/Yellow) / Employer's Representative (Silver) /
CANNOT CONFIRM]
Analysis gate: [PROCEED / CANNOT ASSESS — state reason]

### Named Contract Administrator
Identity: [entity name / CANNOT CONFIRM]
Source: [document name and reference, or NOT FOUND IN WAREHOUSE]
Named individual representative: [name if stated / NOT STATED IN
RETRIEVED DOCUMENTS]

### Delegated Authority Scope
Source: [Particular Conditions reference, or CANNOT CONFIRM]
Authority to grant EOT: [YES / RESTRICTED — state threshold and source /
CANNOT CONFIRM]
Authority to determine claims: [YES / REQUIRES EMPLOYER CONSENT —
state source / CANNOT CONFIRM]
Authority to certify payment: [YES / RESTRICTED — state threshold /
CANNOT CONFIRM]
Financial approval threshold: [value from retrieved PC / CANNOT CONFIRM]
Other restrictions: [from retrieved PC / NONE FOUND / CANNOT CONFIRM]

### Independence Position (Red/Yellow Book only)
Applicable: [YES / NOT APPLICABLE — Silver Book]
Independence obligation: [PRESENT AND UNMODIFIED / MODIFIED — describe /
NOT FOUND IN RETRIEVED PC / CANNOT ASSESS — PC not retrieved]
Source: [Particular Conditions reference]

### Split-Role Arrangement
Identified from retrieved documents: [YES — describe / NOT IDENTIFIED]
PMC appointment in warehouse: [YES — reference / NOT FOUND]
Supervision Consultant appointment in warehouse: [YES — reference /
NOT FOUND]
Authority allocation documented: [YES — describe / NOT DOCUMENTED IN
RETRIEVED DOCUMENTS]

### Instructions and Determinations Assessed
[For each instruction or determination in scope:]
Reference: [document reference]
Issuing entity: [named entity]
Authority confirmed: [YES — source / CANNOT CONFIRM — reason]
Form compliance: [COMPLIANT / ISSUE — describe]
Finding: [from retrieved documents only]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any value or position from this section
without first confirming it from retrieved project documents.*

**FIDIC Clause 3 — structural summary (analytical reference):**
Under Red Book and Yellow Book (both editions), Clause 3 defines the
Engineer's role and authority. The Engineer has an independence
obligation when making determinations under Clause 3.5 (1999) or
Clause 3.7 (2017). Under the 2017 editions, the Engineer's
determination is time-limited — failure to determine within the
prescribed period has a deemed rejection effect. The Silver Book
replaces the Engineer entirely with the Employer's Representative,
who has no independence obligation. Retrieve the specific clause text
from Layer 2 before applying its provisions.

**GCC split-role pattern (analytical reference):**
GCC government projects frequently appoint a PMC to handle commercial
and contractual administration and a Supervision Consultant to handle
technical supervision. This split is not addressed in standard FIDIC
and creates authority ambiguity. The presence of two consulting
entities in the project documents is the signal — confirm the
authority allocation from retrieved appointment documents.

**FIDIC 2017 Clause 3.7 — analytical reference:**
Under FIDIC 2017, the Engineer's determination is subject to a time
limit. Failure to issue a determination within the prescribed period
results in a deemed rejection which triggers the Notice of
Dissatisfaction (NOD) period. The prescribed period is stated in the
Contract Data — retrieve from Layer 1 before stating any period.
