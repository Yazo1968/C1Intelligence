# Engineer Identification

**Skill type:** Mixed
- Contract-type-specific: the contract administrator role, authority scope,
  independence obligation, and determination mechanism differ by standard form
  — the role must be identified from retrieved documents before any
  form-specific analysis
- Contract-type-agnostic: the requirement to identify the contract
  administrator from project documents, map delegated authority, and
  flag authority anomalies applies regardless of standard form
**Layer dependency:**
- Layer 1 — project documents: Contract Agreement, amendment document,
  contract administrator appointment letter, any delegation instruments,
  correspondence revealing actual authority exercised
- Layer 2b — reference standards: Contract administrator provisions from
  the governing standard form (whatever form is in the warehouse) —
  for authority scope and independence obligation assessment
**Domain:** Legal & Contractual SME
**Invoked by:** Legal orchestrator

---

## When to apply this skill

Apply when a query concerns the identity, authority, or actions of the
contract administrator, whether a specific instruction or determination
was within delegated authority, whether the contract administrator is
acting with any required independence, or whether a split-role
arrangement creates ambiguity about which entity has authority for a
specific action.

---

## Before you begin

### Foundational requirement
This skill requires the standard form and version to be confirmed.
Read the contract_assembly findings first. If standard form is
UNCONFIRMED: state CANNOT ASSESS this skill. The contract administrator
role differs fundamentally between standard forms — analysis without
a confirmed standard form is not possible.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The amendment document (contract administrator provisions and any amendment)
- The contract data, appendix to tender, or equivalent schedule
  (contract administrator named entity)
- Contract administrator appointment letter or agreement
- Any delegation letters from the contract administrator to a named
  representative
- Correspondence issued by the contract administrator
  (to establish actual authority exercised in practice)
- Any consultant appointment letter where a split-role arrangement
  may exist

**If the amendment document is not retrieved:**
State CANNOT CONFIRM the contract administrator's scope of authority,
independence position, or any amendment to the standard role.

**If no appointment document is retrieved:**
State CANNOT CONFIRM the identity of the named contract administrator
from the project documents.

### Layer 2b documents to retrieve (reference standards)

After confirming standard form from contract_assembly findings, call
`search_chunks` with `layer_type = '2b'` to retrieve:
- Contract administrator provisions for the confirmed standard form
  (search by subject matter: "contract administrator engineer authority
  duties")
- Determination provisions (search by subject matter: "determination
  fair engineer independent")

**Purpose:** To establish what the standard form says about the contract
administrator role, so that amendment provisions can be assessed against
the baseline. Do not apply standard form provisions without checking
whether they have been amended by the project's amendment document.

**If the governing standard form is not retrieved from Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE for the contract
administrator role provisions. Do not describe the role from training
knowledge.

---

## Analysis workflow

### Step 1 — Confirm the contract administrator role
*Contract-type-specific*

From the confirmed standard form (contract_assembly findings) and the
retrieved amendment document, identify the contract administrator role
as defined in the governing standard form. Different standard forms use
different roles with different titles and different scopes of authority
and independence:

- Some standard forms appoint an independent contract administrator
  (with an obligation to act impartially when making determinations)
- Some standard forms appoint the employer's own representative
  (acting as the employer's agent with no independence obligation)
- Some standard forms have a hybrid arrangement
- Bespoke contracts may define the role differently

**Retrieve the relevant provision from Layer 2b to confirm which model
the governing standard form uses.** If Layer 2b retrieval returns no
result: state CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE.
Do not characterise the role from training knowledge.

**If standard form is not confirmed:** State CANNOT IDENTIFY the
contract administrator role. Do not proceed.

### Step 2 — Identify the named contract administrator
*Contract-type-agnostic*

From the retrieved contract data, appendix to tender, or appointment
letter, identify:
- The named entity appointed as contract administrator
- The named individual representative (if stated)
- The date of appointment (if retrievable)

**Do not assume any entity is the contract administrator without a
retrieved document that names them.** If no appointment document is
found after searching: state CANNOT CONFIRM the identity of the
contract administrator from the warehouse documents.

### Step 3 — Assess delegated authority scope
*Contract-type-specific*

From the retrieved amendment document, identify any amendment that
defines or restricts the contract administrator's authority.
Key authority questions:

- Is the contract administrator's authority to approve variations
  restricted by a financial threshold requiring employer consent?
  Extract the threshold from the amendment document — do not apply
  any default.
- Is the contract administrator required to obtain employer consent
  before issuing specific instructions, determinations, or certificates?
  Extract from the amendment document.
- Does the contract administrator have authority to grant time
  extensions, determine claims, and issue payment certificates without
  employer pre-approval? Extract from the amendment document.

**If the amendment document is not retrieved:**
State CANNOT CONFIRM the delegated authority scope. Do not state any
authority threshold or restriction.

### Step 4 — Assess independence position
*Contract-type-specific*

Some standard forms impose an independence or impartiality obligation
on the contract administrator when making determinations. This
obligation may be modified or removed by the project's amendment
document.

From the retrieved Layer 2b standard form provisions and the retrieved
amendment document, identify:
- Whether the governing standard form imposes an independence obligation
  (from Layer 2b — if not retrieved: CANNOT CONFIRM)
- Whether the amendment document modifies that obligation
- Whether the contract administrator is required to obtain employer
  approval before making determinations or issuing certificates

**Classify the independence position based only on what the retrieved
documents say.** If the amendment document has not been retrieved:
state CANNOT ASSESS the independence position.

### Step 5 — Identify split-role arrangements
*Contract-type-agnostic*

On some projects, the contract administrator role is split between
multiple entities — for example, one entity handling commercial and
contractual administration and another handling technical supervision.
This split may or may not be recognised in the governing standard form.
If it is not, it creates ambiguity about which entity has authority for
which category of instruction.

From the retrieved documents, identify:
- Whether multiple consultant appointment documents exist in the
  warehouse that may indicate a split arrangement
- Whether the contract documents define which entity exercises which
  part of the contract administrator's role
- Whether correspondence shows different entities acting as contract
  administrator for different purposes

**Identify the split only from retrieved documents.** Do not assume
a split arrangement exists. Confirm from the documents which entity
is named as the contract administrator and what authority each entity
has been delegated.

### Step 6 — Assess instructions and determinations issued
*Contract-type-agnostic*

If the query or context involves specific instructions or determinations,
assess for each:
- Was it issued by the named contract administrator or a delegated
  representative?
- Was it within the authority scope confirmed from the amendment document?
- Was it issued in writing (confirm the form requirement from the
  retrieved standard form provisions)?
- Did it comply with the notice requirements stated in the retrieved
  contract documents?

**Authority excess flag:** If a retrieved instruction or determination
was issued by an entity or individual whose authority cannot be confirmed
from the project documents, flag as AUTHORITY UNCONFIRMED. Do not
characterise this as valid or invalid without the authority source.

---

## Classification and decision rules

**Contract administrator identity:**
Named in retrieved contract data or appointment letter → CONFIRMED —
state entity and source document
Not found after searching → CANNOT CONFIRM — flag; state what was
searched and not found

**Delegated authority:**
Authority scope confirmed from retrieved amendment document →
state scope and source document
Amendment document not retrieved → CANNOT CONFIRM authority scope

**Independence position:**
Independence obligation confirmed from Layer 2b AND unmodified in
retrieved amendment document → INDEPENDENT — cite sources
Independence obligation confirmed from Layer 2b AND modified in
retrieved amendment document → MODIFIED — describe the modification
and cite sources
Layer 2b not retrieved → CANNOT CONFIRM — STANDARD FORM NOT IN
WAREHOUSE — independence position cannot be assessed
Amendment document not retrieved → CANNOT ASSESS

**Split-role arrangement:**
Confirmed from retrieved appointment documents → CONFIRMED SPLIT —
describe allocation and cite sources
Not found in retrieved documents → NOT IDENTIFIED FROM WAREHOUSE
DOCUMENTS — note this does not mean no split exists

---

## When to call tools

**Signal:** Contract data or appendix names an entity as contract
administrator but no appointment letter has been retrieved
**Action:** `search_chunks` with query "[entity name] appointment
contract administrator"; `get_related_documents` with document type
"Appointment Letter" or "Consultant Agreement"
**Look for:** Appointment instrument confirming the entity's role and scope

**Signal:** Instructions or correspondence reference a consultant
acting as contract administrator but no appointment document establishes
their authority
**Action:** `search_chunks` with query "appointment authority contract
administrator"; `get_related_documents` with document type
"Appointment Letter"
**Look for:** Appointment instrument defining which entity exercises
which part of the contract administrator's role

**Signal:** Amendment document references a contract administrator
authority amendment but the clause content has not been retrieved
**Action:** `get_document` on the amendment document ID; `search_chunks`
with query "contract administrator authority approval employer consent"
**Look for:** The specific amendment text — authority thresholds,
consent requirements, independence modifications

**Signal:** Layer 2b contract administrator provisions have not been
retrieved for the confirmed standard form
**Action:** `search_chunks` with `layer_type = '2b'` and query
"[standard form name] contract administrator engineer authority"
**Look for:** Standard form contract administrator provisions for
structural comparison

---

## Always flag — regardless of query

1. **Contract administrator role not confirmed from Layer 2b** — flag
   when the governing standard form's contract administrator provisions
   were not retrieved; state that independence position and authority
   scope cannot be confirmed.

2. **Independence modified or removed by amendment document** — always
   flag; state the modification and its forensic implication for any
   determination or certificate in dispute.

3. **Instructions or determinations issued by an entity whose authority
   cannot be confirmed from retrieved documents** — always flag;
   state the instruction reference and what authority document is
   missing from the warehouse.

4. **Split-role arrangement confirmed or suspected but not formally
   documented in the retrieved contract documents** — always flag;
   state the split pattern identified and the absence of a formal
   authority allocation document.

5. **Employer consent requirement before contract administrator
   determinations** — if the retrieved amendment document requires
   employer consent before the contract administrator can determine
   claims or certify payment, always flag; state the clause and its
   forensic implication for any contested determination.

6. **Governing standard not retrieved from Layer 2b** — flag when the
   contract administrator role provisions could not be retrieved; state
   what standard would need to be ingested to resolve it.

---

## Output format

```
## Engineer Identification Assessment

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
[List every document retrieved relevant to this skill, with reference
numbers and dates.]

### Documents Not Retrieved
[List every document required for this analysis not found in the
warehouse. State which analysis steps are affected.]

### Layer 2b Reference Retrieved
[State whether the contract administrator provisions for the confirmed
standard form were retrieved from Layer 2b. If not: state CANNOT CONFIRM —
STANDARD FORM NOT IN WAREHOUSE and list which analysis steps
are affected.]

### Contract Administrator Role
Standard form confirmed: [YES — from contract_assembly / NO — CANNOT ASSESS]
Role title: [title as stated in retrieved standard form / CANNOT CONFIRM]
Independence obligation: [CONFIRMED FROM LAYER 2b / NOT FOUND IN LAYER 2b /
CANNOT CONFIRM — standard form not retrieved]
Analysis gate: [PROCEED / CANNOT ASSESS — state reason]

### Named Contract Administrator
Identity: [entity name / CANNOT CONFIRM]
Source: [document name and reference, or NOT FOUND IN WAREHOUSE]
Named individual representative: [name if stated / NOT STATED IN
RETRIEVED DOCUMENTS]

### Delegated Authority Scope
Source: [amendment document reference, or CANNOT CONFIRM]
Authority to grant time extensions: [YES / RESTRICTED — state threshold
and source / CANNOT CONFIRM]
Authority to determine claims: [YES / REQUIRES EMPLOYER CONSENT —
state source / CANNOT CONFIRM]
Authority to certify payment: [YES / RESTRICTED — state threshold /
CANNOT CONFIRM]
Financial approval threshold: [value from retrieved amendment document /
CANNOT CONFIRM]
Other restrictions: [from retrieved amendment document / NONE FOUND /
CANNOT CONFIRM]

### Independence Position
Applicable: [YES — confirmed from Layer 2b / NOT APPLICABLE — standard
form does not impose independence obligation / CANNOT CONFIRM — Layer 2b
not retrieved]
Independence obligation: [PRESENT AND UNMODIFIED / MODIFIED — describe /
NOT FOUND IN RETRIEVED AMENDMENT DOCUMENT / CANNOT ASSESS]
Source: [amendment document reference and Layer 2b source]

### Split-Role Arrangement
Identified from retrieved documents: [YES — describe / NOT IDENTIFIED]
First consultant appointment in warehouse: [YES — reference / NOT FOUND]
Second consultant appointment in warehouse: [YES — reference / NOT FOUND]
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

**Contract administrator models — analytical reference:**
Standard forms of contract vary in how they define the contract
administrator role. Some appoint an independent professional who owes
duties to both parties when making determinations. Some appoint the
employer's own representative who acts solely as the employer's agent.
Some use a hybrid model. The applicable model must be retrieved from
the governing standard form in Layer 2b — do not assume which model
applies.

**Split-role patterns — analytical reference:**
On complex projects, the contract administration function is sometimes
divided between entities — one handling commercial and contractual
matters and another handling technical supervision. This arrangement
is not addressed in most standard forms and creates authority ambiguity.
The presence of multiple consulting entities in the project documents
is the signal — confirm the authority allocation from retrieved
appointment documents.

**Determination time limits — analytical reference:**
Some standard forms impose time limits on the contract administrator
to issue determinations. Failure to determine within the prescribed
period may have procedural consequences (such as deemed rejection or
deemed acceptance). The prescribed period and its consequences must be
retrieved from the governing standard form in Layer 2b and confirmed
against any amendment in Layer 1.
