# Contract Assembly

**Skill type:** Mixed
- Contract-type-agnostic: the requirement to retrieve and verify the contract
  document hierarchy, identify amendments, and flag missing documents
- Contract-type-specific: the expected document hierarchy, the role of the
  contract administrator, and the formation mechanism differ by FIDIC book
  and edition
**Layer dependency:**
- Layer 1 — project documents: Contract Agreement, Letter of Acceptance,
  Particular Conditions, General Conditions, and all other contract documents
- Layer 2 — reference standards: FIDIC General Conditions (relevant book and
  edition) for structural comparison and clause interpretation
**Domain:** Legal & Contractual SME
**Invoked by:** Legal orchestrator

---

## When to apply this skill

Apply at the start of every Legal & Contractual analysis regardless of the
query. Contract assembly is the foundational skill — the document hierarchy,
Particular Conditions amendments, and document completeness must be established
before any other legal analysis can proceed. Also apply directly when a query
concerns document precedence, contract completeness, or contractual term
interpretation.

---

## Before you begin

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- Contract Agreement
- Letter of Acceptance (Red Book, Yellow Book)
- Letter of Tender / Appendix to Tender / Contract Data
- Particular Conditions (all parts)
- General Conditions (confirm book from cover or header)
- Employer's Requirements (Yellow Book, Silver Book only)
- Contractor's Proposal (Yellow Book, Silver Book only)
- Any amendments, supplemental agreements, side letters, novation agreements

**If the Particular Conditions are not retrieved:**
State CANNOT ASSESS for all steps that depend on the amendment position.
Do not apply General Conditions text as if unamended. Flag this as a
critical gap in every section of the output.

**If the Contract Agreement is not retrieved:**
State CANNOT ASSESS for contract formation, order of precedence, and
any parameter that appears only in the Contract Agreement.

**If no contract documents are retrieved at all:**
State CANNOT ASSESS for this entire skill. Do not proceed.

### Layer 2 documents to retrieve (reference standards)

After establishing the book type and edition from Layer 1, call
`search_chunks` to retrieve the relevant FIDIC General Conditions clauses
from Layer 2:
- Clause 1.5 (priority of documents / order of precedence)
- The document hierarchy list for the identified book and edition

**Purpose of Layer 2 retrieval:** To establish what the standard FIDIC
text says so that any Particular Conditions amendment can be assessed
against the baseline. Layer 2 provides the interpretive framework.
Layer 1 provides what this project actually agreed.

**If Layer 2 FIDIC is not retrieved:**
You may apply your analytical knowledge of the standard FIDIC text as
the interpretive framework, but note in the output that the Layer 2
reference was not retrieved and the standard text has been applied from
training knowledge rather than from the ingested reference document.

---

## Analysis workflow

### Step 1 — Identify the FIDIC book and edition
*Contract-type-specific*

Read the retrieved Contract Agreement and Particular Conditions. Identify:
- FIDIC book: Red Book (Construction) / Yellow Book (Plant & Design-Build) /
  Silver Book (EPC/Turnkey)
- Edition: 1999 or 2017

The book type and edition must be stated in the retrieved documents.
Do not infer from contextual signals alone.

**If book type cannot be confirmed from retrieved documents:**
Classify as BOOK TYPE UNCONFIRMED. State what was retrieved and why
the book type cannot be determined. Set output confidence to GREY.
Do not proceed with book-type-specific steps. Flag that all downstream
analysis is suspended pending book type confirmation.

**If edition cannot be confirmed from retrieved documents:**
Classify as EDITION UNCONFIRMED. State what was retrieved and why.
Do not apply edition-specific clause references. Flag for each
edition-dependent step that it CANNOT BE ASSESSED.

### Step 2 — Assess document completeness against the retrieved hierarchy
*Contract-type-specific*

Based on the book type confirmed in Step 1, assess which documents are
expected. The expected document set for each book is defined in the FIDIC
General Conditions — retrieve from Layer 2 for comparison.

For each document in the expected set: classify as PRESENT, ABSENT,
or PARTIALLY PRESENT (retrieved but appears truncated or incomplete).

**Flag every absent document.** Do not proceed with any analysis step
that requires an absent document. State explicitly which analysis steps
are suspended as a result.

Critical absences:
- Particular Conditions absent → CANNOT ASSESS amendment position,
  time bar, entitlement modifications, or any clause-specific analysis
- Contract Agreement absent → CANNOT ASSESS contract formation,
  contract sum, or parameters stated only in the Contract Agreement
- General Conditions absent → retrieve from Layer 2 as the baseline;
  flag that the project-specific version has not been confirmed

### Step 3 — Establish the effective order of precedence
*Contract-type-specific*

From the retrieved Particular Conditions, identify any amendment to the
order of precedence clause (Clause 1.5 in all books and editions).

**The order of precedence to apply is the order stated in the retrieved
Particular Conditions.** Do not apply the General Conditions order
without first confirming it has not been amended.

If no Particular Conditions amendment to Clause 1.5 is found and the
Particular Conditions have been retrieved and reviewed: note that no
amendment was found and the General Conditions order appears to apply —
citing the Particular Conditions document as the source of that finding.

If the Particular Conditions have not been retrieved: state CANNOT
CONFIRM order of precedence. Do not state any hierarchy as governing.

### Step 4 — Map Particular Conditions amendments
*Contract-type-specific and contract-type-agnostic elements*

Read all retrieved Particular Conditions chunks. For every amendment to
the General Conditions, record:
- The sub-clause amended (cite the sub-clause number)
- What the amendment does: substitutes / adds / deletes / restricts
- The forensic significance of the amendment

**Do not characterise the effect of an amendment by applying General
Conditions text that you have not retrieved from Layer 2.** If the
Layer 2 standard text for the amended clause was not retrieved, describe
what the Particular Conditions say and note that comparison to the
standard form requires Layer 2 retrieval.

Forensically significant amendments — flag any of the following:
- Removal or modification of the DAB/DAAB clause
- Modification of the notice or time bar provisions
- Transfer of Employer Risk Events to Contractor risk
- Restriction of the Engineer's authority or independence obligation
- Modification of the LD rate or LD cap
- Removal or restriction of cost recovery heads (e.g. financing charges)
- Any clause that removes or limits a party's right to claim
- Any clause inconsistent with FIDIC Golden Principles GP1–GP5

*Contract-type-specific note:* The Silver Book has no Engineer. Any
Particular Conditions provision referencing an Engineer on a Silver Book
project is anomalous — flag it.

### Step 5 — Check for contradictions between documents
*Contract-type-agnostic*

For key parameters that may appear in more than one retrieved document
(Time for Completion, LD rate, retention percentage, DNP, contract sum,
commencement date), compare the values across all retrieved documents.

**Both values must be stated. Do not resolve the contradiction by
choosing one.**

If the same parameter appears in two documents at different hierarchy
levels: state which governs per the order of precedence established in
Step 3. If the order of precedence is unconfirmed (Particular Conditions
not retrieved): state CANNOT DETERMINE which value governs.

If the same parameter appears in two documents at the same hierarchy
level: classify as UNRESOLVABLE CONTRADICTION from the retrieved
documents. Flag as RED.

### Step 6 — Identify governing law and dispute resolution mechanism
*Contract-type-specific*

From the retrieved Particular Conditions and Contract Data, identify:
- The governing law of the contract (must be stated in retrieved documents)
- The dispute resolution mechanism as amended by Particular Conditions
- The seat and rules of arbitration if stated

**Do not assume any governing law or dispute resolution mechanism.**
If the Particular Conditions have not been retrieved: state CANNOT
CONFIRM governing law or dispute resolution mechanism.

---

## Classification and decision rules

**Document completeness:**
All expected documents present → COMPLETE
Particular Conditions or Contract Agreement absent → CRITICALLY
INCOMPLETE — downstream analysis severely constrained; state which
steps cannot proceed
One or more secondary documents absent → PARTIAL — flag each absence
and its effect on analysis

**Book type:**
Confirmed from retrieved documents → state book type and source
Cannot be confirmed → BOOK TYPE UNCONFIRMED — output confidence GREY —
downstream specialists cannot proceed with book-specific analysis

**Particular Conditions amendments:**
Amendment found and recorded → state sub-clause, effect, and
forensic significance
No amendment found to a clause AND Particular Conditions retrieved →
state "no amendment found" citing the Particular Conditions as source
No amendment found AND Particular Conditions not retrieved → state
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

**Signal:** Contract Agreement or Letter of Acceptance references
additional incorporated documents not retrieved
**Action:** `get_document` on the Contract Agreement / Letter of
Acceptance document ID
**Look for:** Full list of incorporated documents and additional terms

**Signal:** Particular Conditions chunks appear truncated — numbering
suggests sub-clauses are missing
**Action:** `get_document` on the Particular Conditions document ID
**Look for:** Complete amendment list — confirm no forensically
significant clauses have been missed

**Signal:** A parameter appears in chunks but the source document is
not a primary contract document — may be in a supplemental agreement
**Action:** `search_chunks` with the parameter as query; then
`get_related_documents` with document types: Contract Amendment,
Supplemental Agreement, Side Letter
**Look for:** Any document that modifies the parameter post-execution

**Signal:** Book type is unclear — contract documents use FIDIC language
but do not identify Red, Yellow, or Silver
**Action:** `search_chunks` querying "Employer's Requirements",
"Engineer", "Employer's Representative", "design responsibility"
**Look for:** Presence of Employer's Requirements and Contractor design
obligation suggests Yellow or Silver; Engineer (not Employer's
Representative) as contract administrator suggests Red or Yellow.
Note: contextual signals only — do not confirm book type from signals
alone if the contract documents do not confirm it explicitly.

**Signal:** Layer 2 FIDIC General Conditions for the identified book and
edition have not been retrieved
**Action:** `search_chunks` with query "[book name] [edition year]
general conditions [clause number]"
**Look for:** The relevant FIDIC standard text for comparison against
the Particular Conditions amendments

---

## Always flag — regardless of query

1. **Book type and edition** — always state the confirmed book type and
   edition and the source document. If unconfirmed, flag explicitly.
   Every downstream analysis depends on this.

2. **Particular Conditions absent or not fully retrieved** — always flag
   if the Particular Conditions were not retrieved or appear incomplete.
   State which downstream analysis steps cannot proceed.

3. **Any Particular Conditions amendment that removes or restricts
   entitlement, procedural rights, or risk allocation** — always surface
   these regardless of the query.

4. **Contradictions between documents on key parameters** — Time for
   Completion, LD rate, contract sum, DNP. Surface any contradiction
   found regardless of the query.

5. **Side letters, supplemental agreements, or novation agreements** —
   if present in the warehouse, always flag their existence and state
   what they purport to change.

6. **Silver Book: absence of Engineer** — if a Silver Book is confirmed
   and any document references an Engineer, flag the anomaly.

---

## Output format

```
## Contract Assembly Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved with its document reference number and date.
List every expected document that was NOT retrieved.]

### Documents Not Retrieved
[List every document that was required for this analysis but not found
in the warehouse. For each: state which analysis steps are affected.]

### Layer 2 Reference Retrieved
[State whether FIDIC General Conditions for the identified book and
edition were retrieved from Layer 2. If not: state that standard form
text has been applied from analytical knowledge, not from the ingested
reference document.]

### Book Type and Edition
Confirmed: [YES / NO]
Book: [Red Book / Yellow Book / Silver Book / UNCONFIRMED]
Edition: [1999 / 2017 / UNCONFIRMED]
Source: [document name and reference number]
Analysis gate: [PROCEED / SUSPENDED — state reason if suspended]

### Document Completeness
| Document | Expected | Status | Analysis impact if absent |
|---|---|---|---|
| Contract Agreement | Yes | [PRESENT/ABSENT/PARTIAL] | [impact] |
| Letter of Acceptance | [Yes/No/N/A per book] | [status] | [impact] |
| Particular Conditions | Yes | [PRESENT/ABSENT/PARTIAL] | [impact] |
| General Conditions | Yes | [PRESENT/ABSENT — Layer 2 used] | [impact] |
| [other documents per book] | | | |
Overall: [COMPLETE / PARTIAL / CRITICALLY INCOMPLETE]

### Order of Precedence
Source: [Particular Conditions document reference, or CANNOT CONFIRM]
[State the hierarchy as confirmed from retrieved documents, or state
CANNOT CONFIRM and why]

### Particular Conditions Amendments
[For each amendment found:]
Sub-clause [X.X]: [what the amendment does]
Source: [Particular Conditions reference, page/clause if identifiable]
Forensic significance: [STANDARD / SIGNIFICANT]
[If SIGNIFICANT: state the forensic impact in one sentence]

[If no amendments found AND Particular Conditions retrieved:]
No amendments to General Conditions identified in retrieved
Particular Conditions. Source: [document reference].

[If Particular Conditions not retrieved:]
CANNOT ASSESS — Particular Conditions not retrieved.

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
FIDIC book: [value] Source: [document]
FIDIC edition: [value] Source: [document]
Time for Completion: [value] Source: [document]
LD rate: [value] Source: [document]
DNP: [value] Source: [document]
Contract sum: [value] Source: [document]
Governing law: [value] Source: [document]
Dispute resolution: [value] Source: [document]
Contract administrator role: [Engineer / Employer's Representative /
CANNOT CONFIRM] Source: [document]

### FLAGS
[Each flag on a separate line. State the flag and its forensic
implication in one sentence.]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — only facts from retrieved documents]
```

---

## Analytical framework
*Reference only — do not apply any value from this section without
first confirming it from retrieved project documents.*

**FIDIC document hierarchy structure (analytical reference):**
The FIDIC system places the Contract Agreement at the top of the
hierarchy, followed by the Letter of Acceptance (where applicable),
the Appendix to Tender or Contract Data, the Particular Conditions,
and the General Conditions. Technical documents (Specification,
Drawings, Schedules, Employer's Requirements) rank below the
contractual documents. The exact list and order differ by book and
edition and are subject to Clause 1.5 and any Particular Conditions
amendment. Retrieve from Layer 2 and confirm against Layer 1.

**Silver Book contract formation:**
The Silver Book uses negotiated contract formation. There is no Letter
of Acceptance as a standalone contract formation document. The Contract
Agreement is the primary formation document. Retrieve from Layer 1 to
confirm.

**FIDIC Golden Principles (2019) — analytical reference:**
FIDIC published five Golden Principles to protect the integrity of the
FIDIC system when Particular Conditions are drafted. GP1 — party roles
and responsibilities must be identifiable. GP2 — dispute
avoidance/adjudication mechanism must not be removed. GP3 — time
periods must not be changed to render compliance impossible or
impractical. GP4 — express obligations and time limits must not be
unreasonably altered. GP5 — risk allocation must not be fundamentally
changed. Use these as the framework for assessing whether a Particular
Conditions amendment is forensically significant. The assessment of
whether an amendment violates a Golden Principle must be based on
what the retrieved amendment actually says.

**GCC contractual patterns — analytical reference:**
Abu Dhabi government projects may use the ADGCC (Abu Dhabi Government
Conditions of Contract). Dubai procurement law may affect standard FIDIC
mechanisms. Saudi Arabia government contracts frequently replace the
DAB clause and remove financing charge recovery. Qatar public works
projects use heavily amended FIDIC forms. These patterns are provided
as analytical context — the actual amendment position must always be
confirmed from the retrieved Particular Conditions.
