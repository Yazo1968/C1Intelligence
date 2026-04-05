# Contract Assembly

**Skill type:** Mixed
- Contract-type-agnostic: the requirement to retrieve and verify the contract
  document hierarchy, identify amendments, and flag missing documents
- Contract-type-specific: the expected document hierarchy, the role of the
  contract administrator, and the formation mechanism differ by standard form
  — identify which standard form applies before any form-specific analysis
**Layer dependency:**
- Layer 1 — project documents: Contract Agreement, Letter of Acceptance or
  equivalent formation document, Particular Conditions or Special Conditions
  or equivalent amendment document, General Conditions, and all other
  contract documents
- Layer 2b — reference standards: Governing standard form for this project
  (whatever form is ingested in the warehouse) — for structural comparison
  and provision interpretation
**Domain:** Legal & Contractual SME
**Invoked by:** Legal orchestrator

---

## When to apply this skill

Apply at the start of every Legal & Contractual analysis regardless of the
query. Contract assembly is the foundational skill — the document hierarchy,
particular conditions amendments, and document completeness must be established
before any other legal analysis can proceed. Also apply directly when a query
concerns document precedence, contract completeness, or contractual term
interpretation.

---

## Before you begin

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- Contract Agreement
- Formation document (Letter of Acceptance, Letter of Award, or equivalent
  — name varies by standard form)
- Tender or offer document and any appendix or contract data schedule
- Particular Conditions, Special Conditions, Z Clauses, or equivalent
  amendment document (all parts)
- General Conditions (confirm governing standard form from cover or header)
- Employer's Requirements (where the standard form allocates design to the
  Contractor)
- Contractor's Proposal (where submitted as a contract document)
- Any amendments, supplemental agreements, side letters, novation agreements

**If the amendment document (Particular Conditions or equivalent) is not retrieved:**
State CANNOT ASSESS for all steps that depend on the amendment position.
Do not apply General Conditions text as if unamended. Flag this as a
critical gap in every section of the output.

**If the Contract Agreement is not retrieved:**
State CANNOT ASSESS for contract formation, order of precedence, and
any parameter that appears only in the Contract Agreement.

**If no contract documents are retrieved at all:**
State CANNOT ASSESS for this entire skill. Do not proceed.

### Layer 2b documents to retrieve (reference standards)

After identifying the governing standard form from Layer 1, call
`search_chunks` with `layer_type = '2b'` to retrieve:
- The order of precedence / priority of documents provision from
  the governing standard form (search by subject matter:
  "order of precedence priority of documents")
- The document hierarchy list for the identified standard form

**Purpose of Layer 2b retrieval:** To establish what the standard form
says so that any amendment document can be assessed against the baseline.
Layer 2b provides the interpretive framework. Layer 1 provides what this
project actually agreed.

**If the governing standard form is not retrieved from Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE for any provision
that requires comparison to the standard form baseline. Do not describe
standard form provisions from training knowledge. Flag that the governing
standard form should be ingested into Layer 2b to enable full analysis.

---

## Analysis workflow

### Step 1 — Identify the governing standard form and version
*Contract-type-specific*

Read the retrieved contract documents. Identify:
- The governing standard form (from the cover, header, or explicit statement
  in the retrieved documents — do not assume)
- The version or edition of that standard form

The standard form and version must be stated in the retrieved documents.
Do not infer from contextual signals alone.

**If the standard form cannot be confirmed from retrieved documents:**
Classify as STANDARD FORM UNCONFIRMED. State what was retrieved and why
the standard form cannot be determined. Set output confidence to GREY.
Do not proceed with form-specific steps. Flag that all downstream
analysis is suspended pending standard form confirmation.

**If the version/edition cannot be confirmed from retrieved documents:**
Classify as VERSION UNCONFIRMED. State what was retrieved and why.
Do not apply version-specific provisions. Flag for each
version-dependent step that it CANNOT BE ASSESSED.

### Step 2 — Assess document completeness against the retrieved hierarchy
*Contract-type-specific*

Based on the standard form confirmed in Step 1, assess which documents are
expected. The expected document set is defined in the governing standard form
General Conditions — retrieve from Layer 2b for comparison.

For each document in the expected set: classify as PRESENT, ABSENT,
or PARTIALLY PRESENT (retrieved but appears truncated or incomplete).

**Flag every absent document.** Do not proceed with any analysis step
that requires an absent document. State explicitly which analysis steps
are suspended as a result.

Critical absences:
- Amendment document absent → CANNOT ASSESS amendment position,
  time bar, entitlement modifications, or any clause-specific analysis
- Contract Agreement absent → CANNOT ASSESS contract formation,
  contract sum, or parameters stated only in the Contract Agreement
- General Conditions absent → retrieve from Layer 2b as the baseline;
  flag that the project-specific version has not been confirmed

### Step 3 — Establish the effective order of precedence
*Contract-type-specific*

From the retrieved amendment document, identify any amendment to the
order of precedence clause (retrieve from Layer 2b to confirm the
standard form clause — search by subject matter: "priority of documents
order of precedence").

**The order of precedence to apply is the order stated in the retrieved
amendment document.** Do not apply the General Conditions order
without first confirming it has not been amended.

If no amendment to the order of precedence is found and the amendment
document has been retrieved and reviewed: note that no amendment was
found and the General Conditions order appears to apply — citing the
amendment document as the source of that finding.

If the amendment document has not been retrieved: state CANNOT
CONFIRM order of precedence. Do not state any hierarchy as governing.

### Step 4 — Map amendment document provisions
*Contract-type-specific and contract-type-agnostic elements*

Read all retrieved amendment document chunks. For every amendment to
the General Conditions, record:
- The clause amended (cite the clause reference)
- What the amendment does: substitutes / adds / deletes / restricts
- The forensic significance of the amendment

**Do not characterise the effect of an amendment by applying General
Conditions text that you have not retrieved from Layer 2b.** If the
Layer 2b standard text for the amended clause was not retrieved,
describe what the amendment document says and note that comparison
to the standard form requires Layer 2b retrieval.

Forensically significant amendments — flag any of the following:
- Removal or modification of the dispute avoidance/adjudication mechanism
- Modification of the notice or time bar provisions
- Transfer of employer risk events to contractor risk
- Restriction of the contract administrator's authority or independence
- Modification of the agreed damages rate or cap
- Removal or restriction of cost recovery heads
- Any clause that removes or limits a party's right to claim
- Any clause that appears inconsistent with the fundamental structure
  of the governing standard form

### Step 5 — Check for contradictions between documents
*Contract-type-agnostic*

For key parameters that may appear in more than one retrieved document
(Time for Completion, agreed damages rate, retention percentage, defects
notification period, contract sum, commencement date), compare the values
across all retrieved documents.

**Both values must be stated. Do not resolve the contradiction by
choosing one.**

If the same parameter appears in two documents at different hierarchy
levels: state which governs per the order of precedence established in
Step 3. If the order of precedence is unconfirmed (amendment document
not retrieved): state CANNOT DETERMINE which value governs.

If the same parameter appears in two documents at the same hierarchy
level: classify as UNRESOLVABLE CONTRADICTION from the retrieved
documents. Flag as RED.

### Step 6 — Identify governing law and dispute resolution mechanism
*Contract-type-specific*

From the retrieved amendment document and contract data, identify:
- The governing law of the contract (must be stated in retrieved documents)
- The dispute resolution mechanism as stated in the retrieved documents
- The seat and rules of arbitration if stated

**Do not assume any governing law or dispute resolution mechanism.**
If the amendment document has not been retrieved: state CANNOT
CONFIRM governing law or dispute resolution mechanism.

---

## Classification and decision rules

**Document completeness:**
All expected documents present → COMPLETE
Amendment document or Contract Agreement absent → CRITICALLY
INCOMPLETE — downstream analysis severely constrained; state which
steps cannot proceed
One or more secondary documents absent → PARTIAL — flag each absence
and its effect on analysis

**Standard form:**
Confirmed from retrieved documents → state standard form, version, and source
Cannot be confirmed → STANDARD FORM UNCONFIRMED — output confidence GREY —
downstream specialists cannot proceed with form-specific analysis

**Amendment provisions:**
Amendment found and recorded → state clause, effect, and forensic significance
No amendment found to a clause AND amendment document retrieved →
state "no amendment found" citing the amendment document as source
No amendment found AND amendment document not retrieved → state
CANNOT CONFIRM amendment status for this clause

**Contradictions:**
Same parameter in documents at different hierarchy levels, hierarchy
confirmed → state both values, state which governs, cite both sources
Same parameter in documents at different hierarchy levels, hierarchy
not confirmed → state both values, state CANNOT DETERMINE which governs
Same parameter in documents at same hierarchy level → UNRESOLVABLE
from retrieved documents — flag RED

---

## When to call tools

**Signal:** Contract Agreement or formation document references
additional incorporated documents not retrieved
**Action:** `get_document` on the Contract Agreement / formation
document ID
**Look for:** Full list of incorporated documents and additional terms

**Signal:** Amendment document chunks appear truncated — numbering
suggests provisions are missing
**Action:** `get_document` on the amendment document ID
**Look for:** Complete amendment list — confirm no forensically
significant clauses have been missed

**Signal:** A parameter appears in chunks but the source document is
not a primary contract document — may be in a supplemental agreement
**Action:** `search_chunks` with the parameter as query; then
`get_related_documents` with document types: Contract Amendment,
Supplemental Agreement, Side Letter
**Look for:** Any document that modifies the parameter post-execution

**Signal:** Standard form is unclear — contract documents use
recognisable contract language but do not identify the governing form
**Action:** `search_chunks` querying the contract administrator title,
design responsibility provisions, and document nomenclature
**Look for:** Terms that identify the governing standard form —
note as contextual signals only; do not confirm standard form from
signals alone if the contract documents do not confirm it explicitly

**Signal:** Layer 2b governing standard form has not been retrieved
**Action:** `search_chunks` with `layer_type = '2b'` and query
"[standard form name] [provision subject]"
**Look for:** The relevant standard form text for comparison against
the amendment provisions

---

## Always flag — regardless of query

1. **Standard form and version** — always state the confirmed standard
   form and version and the source document. If unconfirmed, flag explicitly.
   Every downstream analysis depends on this.

2. **Amendment document absent or not fully retrieved** — always flag
   if the amendment document was not retrieved or appears incomplete.
   State which downstream analysis steps cannot proceed.

3. **Any amendment that removes or restricts entitlement, procedural
   rights, or risk allocation** — always surface these regardless of
   the query.

4. **Contradictions between documents on key parameters** — Time for
   Completion, agreed damages rate, contract sum, defects notification
   period. Surface any contradiction found regardless of the query.

5. **Side letters, supplemental agreements, or novation agreements** —
   if present in the warehouse, always flag their existence and state
   what they purport to change.

6. **Governing standard not retrieved from Layer 2b** — flag when any
   provision characterisation is based on CANNOT CONFIRM status. State
   which provision was not retrieved, what analysis cannot proceed as a
   result, and what standard would need to be ingested to resolve it.

---

## Output format

```
## Contract Assembly Assessment

### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [standard form name — or NOT RETRIEVED]
Layer 2b provisions retrieved: [description — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE]
Layer 2a source: [policy name — or NOT RETRIEVED / NOT APPLICABLE]
Layer 1 primary document: [name and reference — or NOT RETRIEVED]
Layer 1 amendment document: [Particular Conditions / Special Conditions /
  equivalent — or NOT RETRIEVED / NOT APPLICABLE]
Provisions CANNOT CONFIRM: [list — or NONE]

### Documents Retrieved (Layer 1)
[List every document retrieved with its document reference number and date.
List every expected document that was NOT retrieved.]

### Documents Not Retrieved
[List every document that was required for this analysis but not found
in the warehouse. For each: state which analysis steps are affected.]

### Layer 2b Reference Retrieved
[State whether the governing standard form was retrieved from Layer 2b.
If not: state CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE and
list which analysis steps are affected.]

### Governing Standard Form and Version
Confirmed: [YES / NO]
Standard form: [name of standard form identified from retrieved documents / UNCONFIRMED]
Version/Edition: [version identified from retrieved documents / UNCONFIRMED]
Source: [document name and reference number]
Analysis gate: [PROCEED / SUSPENDED — state reason if suspended]

### Document Completeness
| Document | Expected | Status | Analysis impact if absent |
|---|---|---|---|
| Contract Agreement | Yes | [PRESENT/ABSENT/PARTIAL] | [impact] |
| Formation document | [Yes/No/N/A] | [status] | [impact] |
| Amendment document | Yes | [PRESENT/ABSENT/PARTIAL] | [impact] |
| General Conditions | Yes | [PRESENT/ABSENT — Layer 2b used] | [impact] |
| [other documents per standard form] | | | |
Overall: [COMPLETE / PARTIAL / CRITICALLY INCOMPLETE]

### Order of Precedence
Source: [amendment document reference, or CANNOT CONFIRM]
[State the hierarchy as confirmed from retrieved documents, or state
CANNOT CONFIRM and why]

### Amendment Document Provisions
[For each amendment found:]
Clause [X.X]: [what the amendment does]
Source: [amendment document reference, page/clause if identifiable]
Forensic significance: [STANDARD / SIGNIFICANT]
[If SIGNIFICANT: state the forensic impact in one sentence]

[If no amendments found AND amendment document retrieved:]
No amendments to General Conditions identified in retrieved
amendment document. Source: [document reference].

[If amendment document not retrieved:]
CANNOT ASSESS — Amendment document not retrieved.

### Contradictions Between Documents
[For each contradiction:]
Parameter: [name]
Document A: [name, reference] — value: [X]
Document B: [name, reference] — value: [Y]
Governing document: [per confirmed hierarchy / CANNOT DETERMINE]

[If none found:]
No contradictions identified across retrieved documents.

### Governing Law and Dispute Resolution
Governing law: [from retrieved documents, or CANNOT CONFIRM]
Source: [document reference]
Dispute resolution: [from retrieved documents, or CANNOT CONFIRM]
Arbitration rules and seat: [from retrieved documents, or CANNOT CONFIRM]

### Foundational Facts for Downstream Skills
[Only populate from retrieved documents. State CANNOT CONFIRM for any
item not found in the warehouse.]
Standard form: [value] Source: [document]
Version/Edition: [value] Source: [document]
Time for Completion: [value] Source: [document]
Agreed damages rate: [value] Source: [document]
Defects notification period: [value] Source: [document]
Contract sum: [value] Source: [document]
Governing law: [value] Source: [document]
Dispute resolution: [value] Source: [document]
Contract administrator role: [title as stated in contract / CANNOT CONFIRM] Source: [document]

### FLAGS
[Each flag on a separate line. State the flag and its forensic
implication in one sentence.]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
*(Confidence scale: GREEN = all required evidence retrieved and findings fully supported | AMBER = Layer 2b not retrieved or amendment position unknown -- findings provisional | RED = critical document absent -- findings materially constrained | GREY = standard form unconfirmed -- form-specific analysis suspended. Full definition: skills/c1-skill-authoring/references/grounding_protocol.md)*
Summary: [two to three sentences — only facts from retrieved documents]
```

---

## Analytical framework
*Reference only — do not apply any value from this section without
first confirming it from retrieved project documents.*

**Standard form document hierarchy — analytical reference:**
Most standard forms of contract organise documents in a hierarchy with
the contract agreement or acceptance at the top, followed by any
particular or special conditions, then the general conditions, and then
technical documents such as specifications and drawings. The exact
hierarchy, document names, and order of precedence vary by standard
form and may be amended by particular conditions. Always retrieve the
priority of documents provision from Layer 2b and confirm the project
position from Layer 1 before stating any hierarchy.

**Amendment assessment principles — analytical reference:**
When assessing whether a particular conditions amendment is forensically
significant, consider: whether it removes or restricts a party's
entitlement to claim; whether it alters the balance of risk in a
fundamental way; whether it modifies dispute resolution or notice
mechanisms in a way that makes compliance impractical; and whether it
restricts the contract administrator's independence. These are general
assessment principles — the actual amendment must be confirmed from
the retrieved documents before any characterisation of its effect.

**Contract formation mechanisms — analytical reference:**
Standard forms of contract use different formation mechanisms. Some use
a letter of acceptance as the contract formation event; others use a
signed contract agreement; others use a notice to proceed. The mechanism
applicable to this project must be confirmed from the retrieved documents.
Do not assume any formation mechanism.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies to
any contract form. All characterisations grounded in retrieved warehouse
documents only.*
