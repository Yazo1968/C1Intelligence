# Contract Assembly — Legal & Contractual Specialist

## When to apply this skill

Apply this skill at the start of every Legal & Contractual analysis, regardless of the specific
query. Contract assembly is a foundational task — the hierarchy, the amendments in the Particular
Conditions, and the document completeness assessment must be established before any other legal
analysis begins. Also apply when a query directly concerns document precedence, contract
completeness, or the interpretation of a specific contractual term.

---

## Before you begin

This is a Round 1 skill. There are no upstream specialist findings to read.

Before beginning the analysis, retrieve the following from the warehouse:

- Contract Agreement
- Letter of Acceptance (if present)
- Letter of Tender and Appendix to Tender / Contract Data
- Particular Conditions (Part II in 1999; Part A – Contract Data and Part B – Special Provisions
  in 2017)
- General Conditions (confirm book type from cover or header)
- Employer's Requirements (Yellow and Silver Books only)
- Contractor's Proposal (Yellow and Silver Books only)
- Any contract amendments, supplemental agreements, side letters, or novation agreements

If none of these documents are in the retrieved chunks, call `search_chunks` before proceeding.
Do not begin analysis on empty or insufficient context.

---

## Analysis workflow

**Step 1 — Identify the FIDIC book and edition**

Read the Contract Agreement and the Particular Conditions cover or header. Identify:
- Which FIDIC book governs: Red (Construction), Yellow (Plant & Design-Build), or Silver
  (EPC/Turnkey)
- Which edition: 1999 or 2017

If the book type cannot be positively identified from the retrieved documents, flag this
immediately as a BOOK TYPE UNCONFIRMED finding and proceed using the most likely book based on
contextual signals (e.g. presence of Employer's Requirements suggests Yellow or Silver; presence
of Engineer appointment letter suggests Red or Yellow). State your assumption explicitly and flag
that downstream analysis is conditional on it.

If the edition cannot be determined, flag EDITION UNCONFIRMED and proceed using 1999 as the
default, stating this assumption.

**Step 2 — Map the expected document hierarchy for the identified book and edition**

Apply the correct expected hierarchy:

- Red Book 1999 (8 items): Contract Agreement → Letter of Acceptance → Letter of Tender /
  Appendix to Tender → Particular Conditions → General Conditions → Specification → Drawings →
  Schedules
- Red Book 2017 (11 items): Contract Agreement → Letter of Acceptance → Letter of Tender →
  Particular Conditions Part A (Contract Data) → Particular Conditions Part B (Special
  Provisions) → General Conditions → Specification → Drawings → Schedules → JV Undertaking →
  other documents
- Yellow Book 1999 (8 items): Contract Agreement → Letter of Acceptance → Letter of Tender /
  Appendix to Tender → Particular Conditions → General Conditions → Employer's Requirements →
  Schedules → other documents
- Yellow Book 2017 (11 items): Contract Agreement → Letter of Acceptance → Letter of Tender →
  Particular Conditions Part A → Particular Conditions Part B → General Conditions →
  Employer's Requirements → Schedules → Contractor's Proposal → JV Undertaking → other documents
- Silver Book 1999 (5 items): Contract Agreement → Particular Conditions → General Conditions →
  Employer's Requirements → the Tender / other documents
- Silver Book 2017 (9 items): Contract Agreement → Particular Conditions Part A → Particular
  Conditions Part B → General Conditions → Employer's Requirements → Schedules → the Tender →
  JV Undertaking → other documents

Note: Silver Book has no Letter of Acceptance and no Letter of Tender as standalone items —
contract is formed by negotiated agreement, not tender-acceptance.

**Step 3 — Assess document completeness**

For each item in the expected hierarchy, determine whether the document is present in the
warehouse. Classify each item: PRESENT / ABSENT / PARTIALLY PRESENT (chunks retrieved but
document appears incomplete).

Flag every absent document. An absent Particular Conditions is a critical gap — the General
Conditions cannot be applied without knowing what was amended. An absent Contract Agreement is a
critical gap for Silver Book projects (it is the primary contract formation document with no
Letter of Acceptance as backup).

**Step 4 — Establish the effective order of precedence**

Based on the documents actually present, state the effective hierarchy. Where a higher-ranked
document is absent, note that its position cannot be filled and any ambiguity between lower-ranked
documents cannot be resolved by reference to it.

Check the Particular Conditions for any express modification to the standard hierarchy. GCC
employers sometimes amend Clause 1.5 to elevate or demote specific documents. If found, apply
the amended hierarchy and flag the modification.

**Step 5 — Map Particular Conditions amendments**

Read all retrieved Particular Conditions chunks. For every amendment to the General Conditions,
record:
- The sub-clause amended
- What the standard General Conditions text says
- What the Particular Conditions substitutes, adds, or deletes
- Whether the amendment is forensically significant

Forensically significant amendments include: removal or modification of the DAB/DAAB clause,
removal of Clause 14.8 (financing charges), modification of the time bar, transfer of risk
events from Employer to Contractor, restriction of the Engineer's authority or independence,
modification of the LD rate or cap, and any clause that removes or limits a party's entitlement
to claim.

Flag any amendment that may violate FIDIC Golden Principles (2019) — particularly GP3 (risk
allocated to the party best able to bear and control it). These amendments are commonly seen in
GCC contracts and are forensically significant in disputes.

**Step 6 — Check for contradictions between documents in the hierarchy**

Compare key parameters across all retrieved documents: Time for Completion, LD rate, retention
percentage, Defects Notification Period, contract sum, and any other figure that appears in more
than one document.

Where the same parameter appears in two documents at different hierarchy levels, note both values
and confirm which governs per the order of precedence. Where the same parameter appears in two
documents at the same hierarchy level, flag this as a CONTRADICTION — both values must be
surfaced and the ambiguity cannot be resolved without further instruction.

**Step 7 — Identify governing law and dispute resolution mechanism**

From the Particular Conditions and Contract Data, identify:
- The governing law of the contract
- The dispute resolution mechanism: DAB (1999) / DAAB (2017) / replaced by arbitration / other
- The seat and rules of arbitration if applicable
- Any jurisdiction-specific flags triggered (see Domain Knowledge section)

**Step 8 — Compile and structure findings**

Compile all findings in the output format below. This output is passed forward to Claims,
Schedule, and Governance specialists as foundational context for their analysis.

---

## Classification and decision rules

**Document completeness:**
- If all expected hierarchy documents are present: COMPLETE
- If Particular Conditions or Contract Agreement is absent: CRITICALLY INCOMPLETE — flag
  immediately; downstream analysis is severely constrained
- If one or more lower-ranked documents (Specification, Drawings, Schedules) are absent: PARTIAL
  — flag each absence; note which analysis tasks are affected
- If documents are present but appear truncated in the warehouse: flag as PARTIALLY PRESENT and
  call `get_document` to retrieve the full document

**Book type identification:**
- If book type confirmed from contract documents: state the book type and source document
- If book type cannot be confirmed: flag BOOK TYPE UNCONFIRMED; state assumption used and basis
  for it; classify overall confidence as AMBER at minimum

**Particular Conditions amendments:**
- Standard amendments (governing law, arbitration, LD rate): note and record — not forensically
  significant unless the rate is unusually high or the mechanism removes DAB/DAAB
- Amendments that remove or restrict entitlements, shift risk, or remove procedural rights:
  FORENSICALLY SIGNIFICANT — flag explicitly with the sub-clause reference and the nature of
  the change
- Amendments that may violate FIDIC Golden Principles: flag with the relevant Golden Principle
  number and a brief statement of the apparent violation

**Contradictions:**
- Between documents at different hierarchy levels: note both values; state which governs per the
  hierarchy; AMBER confidence unless the governing document is unambiguous
- Between documents at the same hierarchy level: RED confidence; both values stated; cannot be
  resolved without further instruction

---

## When to call tools

**Signal:** Retrieved chunks include a Contract Agreement or Letter of Acceptance that references
additional documents not retrieved (e.g. "Appendix 1 to the Contract Agreement", "Schedule of
Key Personnel", "List of Approved Subcontractors")
**Tool:** `get_document` on the Contract Agreement or Letter of Acceptance document ID
**Look for:** The full list of incorporated documents and any additional terms

**Signal:** Particular Conditions chunks appear to be truncated — numbering suggests sub-clauses
are missing or the document ends mid-sentence
**Tool:** `get_document` on the Particular Conditions document ID
**Look for:** Complete amendment list; confirm no forensically significant clauses have been
missed

**Signal:** A parameter (e.g. Time for Completion, LD rate) appears in retrieved chunks but
the source document is not the Particular Conditions or Contract Data — it may be in a
supplemental agreement or side letter not yet retrieved
**Tool:** `search_chunks` with the parameter as query and filter to document types:
Contract Amendment, Supplemental Agreement, Side Letter
**Look for:** Any document that modifies the parameter after the original contract was executed

**Signal:** The Contract Agreement references a Performance Bond, Advance Payment Guarantee,
or Parent Company Guarantee but those documents have not been retrieved
**Tool:** `get_related_documents` filtered to document type: Performance Security, Bond,
Guarantee
**Look for:** Whether the securities exist in the warehouse; pass finding to
`key_dates_and_securities.md` skill

**Signal:** Book type is ambiguous — contract documents use FIDIC language but do not clearly
identify Red, Yellow, or Silver Book
**Tool:** `search_chunks` querying for "Employer's Requirements", "Engineer", "Employer's
Representative", "design responsibility"
**Look for:** Presence of Employer's Requirements → Yellow or Silver; Engineer (not Employer's
Representative) → Red or Yellow; design obligation on Contractor → Yellow or Silver

---

## Always flag — regardless of query

1. **Book type and edition** — always state which FIDIC book and edition governs and the source
   document that confirms this. If unconfirmed, flag explicitly. Every downstream specialist
   needs this.

2. **Particular Conditions amendments that remove or restrict entitlement or procedural rights**
   — always surface these even if the query is about something else entirely. A Particular
   Conditions clause that removes the DAB, modifies the time bar, or eliminates financing charges
   affects the entire project forensic picture.

3. **Any document in the hierarchy that is absent from the warehouse** — always flag missing
   documents. A missing Particular Conditions means the General Conditions are being applied in
   a vacuum. A missing Letter of Acceptance in a Red or Yellow Book project means the contract
   formation evidence is incomplete.

4. **Contradictions between documents on key parameters** — Time for Completion, LD rate,
   contract sum, Defects Notification Period. These are the parameters most frequently in dispute.
   Any contradiction must be surfaced immediately regardless of the query.

5. **Side letters, supplemental agreements, or novation agreements** — if present in the
   warehouse, always flag their existence and state what they purport to change. Side letters that
   override main contract terms without proper Clause 1.3 notice compliance are a common
   forensic signal.

---

## Output format
```
## Contract Assembly Assessment

### Book Type and Edition
Governing book: [Red Book / Yellow Book / Silver Book / UNCONFIRMED]
Edition: [1999 / 2017 / UNCONFIRMED]
Source: [document name and reference]
Assumption (if applicable): [state assumption and basis]

### Document Completeness
| Document | Expected | Status | Notes |
|---|---|---|---|
| Contract Agreement | Yes | [PRESENT / ABSENT / PARTIAL] | |
| Letter of Acceptance | [Yes/No per book] | [PRESENT / ABSENT / N/A] | |
| Letter of Tender / Contract Data | Yes | [PRESENT / ABSENT / PARTIAL] | |
| Particular Conditions | Yes | [PRESENT / ABSENT / PARTIAL] | |
| General Conditions | Yes | [PRESENT / ABSENT / PARTIAL] | |
| Specification / Employer's Requirements | Yes | [PRESENT / ABSENT / PARTIAL] | |
| Drawings / Contractor's Proposal | [Yes/No per book] | [PRESENT / ABSENT / N/A] | |
| Schedules | Yes | [PRESENT / ABSENT / PARTIAL] | |
| Amendments / Side Letters | If any | [PRESENT / NONE FOUND] | |
Completeness classification: [COMPLETE / PARTIAL / CRITICALLY INCOMPLETE]

### Order of Precedence
[List the effective hierarchy for this project in precedence order, highest first, noting any
Clause 1.5 amendments. Flag any absent documents that create gaps in the hierarchy.]

### Particular Conditions Amendments
[For each amendment:]
Sub-clause [X.X]: [description of amendment]
Forensic significance: [STANDARD / SIGNIFICANT]
[If SIGNIFICANT: state why and the forensic impact]

### Contradictions Between Documents
[For each contradiction:]
Parameter: [parameter name]
Document A: [document name] — states [value]
Document B: [document name] — states [value]
Governing document: [per hierarchy] / AMBIGUOUS
[If AMBIGUOUS: state why resolution is not possible from the documents]

### Governing Law and Dispute Resolution
Governing law: [jurisdiction]
Dispute resolution: [DAB / DAAB / Arbitration / Other]
Arbitration seat and rules (if applicable): [details]
Jurisdiction flags: [list any GCC-specific flags from Domain Knowledge section, or "None"]

### Foundational Facts for Downstream Specialists
FIDIC book: [book type] [edition]
Time for Completion: [value] [source document]
LD rate: [value] [source document]
Defects Notification Period: [value] [source document]
Contract sum: [value] [source document]
Governing law: [jurisdiction]
Dispute resolution: [mechanism]
Contract administrator: [Engineer / Employer's Representative] [identity if retrievable]
[Note: Engineer identity is assessed in full by engineer_identification.md skill]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences stating the contract document position, any critical gaps,
and the most significant forensic finding from this assessment]
```

---

## Domain knowledge and standards

### FIDIC Clause 1.5 — Document Hierarchy

FIDIC Sub-Clause 1.5 governs interpretation in cases of conflict, ambiguity, or discrepancy
between contract documents. In 2017 editions the trigger clause was expanded from "ambiguity or
discrepancy" to "conflict, ambiguity or discrepancy" — a minor but deliberate drafting change.

The Particular Conditions override the General Conditions in all books and editions. This is the
single most important principle in contract assembly analysis. GCC Particular Conditions
frequently contain sweeping amendments that transform the standard risk allocation — these must
be identified and recorded before any entitlement analysis begins.

### FIDIC Golden Principles (2019)

FIDIC published five Golden Principles to protect the integrity of the FIDIC system when Particular
Conditions are drafted. The five principles are:

- GP1: Duties, obligations, roles and responsibilities of the Employer, Engineer/Employer's
  Representative, and Contractor must be identifiable
- GP2: The FIDIC dispute avoidance/adjudication mechanism must not be removed
- GP3: Time periods must not be changed to render them impossible or impractical to comply with
- GP4: The Express obligations and the time limits for fulfilling them must not be unreasonably
  altered
- GP5: All of the above must not be so heavily amended as to fundamentally change the risk
  allocation

Violations most commonly seen in GCC Particular Conditions: removal of the DAB/DAAB clause
(GP2), shortening of the time bar below 28 days (GP3), removal of the Engineer's independence
obligation (GP1). Flag any Particular Conditions amendment that appears to violate these
principles — this is a forensically significant finding regardless of whether a dispute has
arisen.

Note: The Silver Book's Clause 4.12 risk transfer is not a Golden Principles violation — it is
a deliberate structural feature of the Silver Book design philosophy.

### GCC-Specific Patterns

**Abu Dhabi — ADGCC (2024 revision):** The Abu Dhabi Government Conditions of Contract is
mandatory for Abu Dhabi government department projects. Based on FIDIC 1999 Red Book (construction
works version) and FIDIC 1999 Yellow Book (design-and-build version) with heavy amendments. The
2024 revision (ADPIC / Dentons) introduces DAAB provisions and pilots Conflict Avoidance Panels.
Projects procured post-2024 under ADGCC may have DAAB provisions not present in earlier ADGCC
contracts — always check the contract date and confirm which ADGCC version applies. ADGCC
modifications typically include: Employer-favourable risk reallocation, Engineer's independence
circumscribed (Employer approval required for material decisions), Arabic as governing language,
alignment with Article 880 decennial liability.

**Dubai:** Dubai procurement law does not recognise standard FIDIC contracts. A project in Dubai
nominally using FIDIC may have its contractual mechanisms overridden by Dubai procurement law.
When the governing law is identified as Dubai or UAE law and the project is in Dubai, flag this
as a critical forensic issue requiring legal opinion.

**Saudi Arabia:** FIDIC 1999 Red Book dominates. 2017 editions not yet in significant use.
Common amendments: DAB clause removed and replaced with SCCA arbitration in Riyadh; Clause 14.8
(financing charges) removed or modified (riba prohibition). Governing language is typically
Arabic — dual-language contracts present interpretation risk; confirm which language governs from
the Particular Conditions.

**Qatar:** Public works projects (Ashghal/PWA, Kahramaa) use heavily amended FIDIC Red Book
forms that are effectively bespoke. Government contracts typically cap liquidated damages at 10%
of contract value — if the Particular Conditions LD rate would produce a figure exceeding this,
note the potential enforceability issue. Qatar arbitration: Qatar International Court and Dispute
Resolution Centre (QICDRC) and ICC are common.

**Saudi Vision 2030 mega-projects (NEOM, The Line, Trojena, Qiddiya):** Use FIDIC 1999 with
heavy amendments. High likelihood of non-standard risk allocation and bespoke Particular
Conditions. Treat the Particular Conditions review for these projects as a full clause-by-clause
exercise — do not assume standard FIDIC positions.

### Silver Book — Special Considerations

On Silver Book projects, the Contract Agreement is the primary contract formation document.
There is no Letter of Acceptance. The contract is formed by negotiated agreement, not
tender-acceptance. If only a Letter of Acceptance is in the warehouse and no Contract Agreement
has been retrieved, either the contract is not a Silver Book contract, or the Contract Agreement
is missing — call `search_chunks` to confirm.

The Contractor's Proposal under a Silver Book is subsumed in "the Tender" (1999) or listed
separately in Schedules (2017). It occupies the lowest positions in the hierarchy and is
overridden by all Employer documents. This means a Contractor's Proposal that conflicts with the
Employer's Requirements on a technical or commercial matter is overridden by the Employer's
Requirements — a frequent source of Contractor claims in EPC projects.

### Decennial Liability

UAE Civil Code Article 880 and Saudi Building Code Implementing Regulations Article 29 impose
10-year joint liability on architect and contractor for defects that may lead to building collapse
or structural failure. This obligation cannot be contracted out of and runs in parallel with the
FIDIC Defects Notification Period provisions regardless of which FIDIC book governs. When
recording the governing law as UAE or Saudi law, flag that decennial liability applies.
