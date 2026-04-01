# Legal & Contractual — Domain Research Summary
## Phase 3 Pre-Authorship Research · C1 Intelligence Platform

**Version:** 1.2
**Date:** April 2026
**Purpose:** Required by `SKILLS_STANDARDS.md` Section 4.3 before any Phase 3 skill authorship begins.
**Changes from v1.1:** Extended to cover FIDIC Yellow Book (Plant & Design-Build) and Silver Book (EPC/Turnkey) in both 1999 and 2017 editions across all sections. ADGCC 2024 revision added. Qatar Article 418 time bar issue added. Saudi Civil Transactions Law 2023 added.

---

## 1. What the Legal & Contractual Specialist Does

The Legal & Contractual specialist in C1 is a forensic analysis agent, not a contract drafter. Its role is to read existing project documents from the warehouse and answer questions about the contractual position — what the contract says, whether obligations have been met, whether instructions are valid, what entitlement basis applies to a claimed event, and where documents contradict each other on legal and contractual matters.

**How it gets project-specific facts:** The agent retrieves them from the warehouse. The governing FIDIC edition and book type are determined by reading the Particular Conditions and Contract Agreement (Layer 1 documents). The Engineer's identity (or Employer's Representative in Silver Book) is determined by reading the appointment letter and contract. Key dates come from the Appendix to Tender / Contract Data. FIDIC standard conditions are available as Layer 2 reference documents. No project-specific facts are hardcoded into skill files.

The specialist's tasks fall into two categories:

**Foundational tasks** — performed regardless of the specific query, because this information underpins everything Claims, Schedule, and Governance will do:
- Identify which FIDIC book and edition governs
- Identify which contract documents govern and in what order of precedence
- Identify who the Engineer is (Red/Yellow) or Employer's Representative is (Silver) and what authority they have
- Map the key contractual dates and milestones
- Identify the governing law and dispute resolution mechanism

**Query-driven tasks** — performed in response to the specific query:
- Assess whether a notice or instruction complied with contractual requirements
- Identify the FIDIC clause that provides the contractual basis for a claimed entitlement
- Assess whether a variation was properly instructed
- Assess the status of bonds and securities
- Flag contradictions between contractual documents

---

## 2. Governing Standards and Framework

### 2.1 FIDIC Rainbow Suite — Three Books in Active Use in the GCC

C1 handles all three FIDIC books. A project may use any one of them. The book type must be identified from the contract documents before any other legal analysis begins, because it determines the identity of the contract administrator, design responsibility, risk allocation, and document hierarchy.

**Which book for which sector (GCC practice):**
- **Red Book (Construction)** — dominates traditional construction: building works, civil engineering, roads, bridges, public infrastructure. Most common FIDIC form across UAE and Saudi Arabia.
- **Yellow Book (Plant & Design-Build)** — used for design-and-build projects: water treatment, industrial plant, MEP installations. UAE has seen increasing adoption as design-and-build procurement grows.
- **Silver Book (EPC/Turnkey)** — used for EPC/turnkey projects: power plants, process plants, petrochemical complexes. Major NOCs (ADNOC, Saudi Aramco, QatarEnergy) typically use bespoke EPC contracts that draw on Silver Book principles rather than unmodified Silver Book terms. BOOT/PPP/concession schemes use bespoke contracts with Silver Book risk allocation principles underlying the EPC element.

**Saudi Vision 2030 mega-projects** (NEOM, The Line, Trojena, Oxagon, New Murabba, Qiddiya) predominantly use FIDIC 1999 with heavy amendments — the 2017 editions have not yet gained significant traction in the Kingdom. **Qatar public works** (Ashghal/PWA, Kahramaa) primarily use Red Book-based forms.

Both 1999 and 2017 editions are in active use across the GCC. The 1999 edition dominates in Saudi Arabia and most established government projects. The 2017 edition is increasingly used on newer international projects and by sophisticated private sector employers.

#### Five structural differentiators across the three books

The three books share approximately 80% identical general conditions text. They diverge on five structural pillars that produce materially different forensic outcomes:

| Differentiator | Red Book | Yellow Book | Silver Book |
|---|---|---|---|
| Contract administrator | Engineer (Clause 3) — acts for Employer but makes fair/neutral determinations | Engineer (Clause 3) — identical to Red Book | Employer's Representative (Clause 3) — Employer's agent, no independent determination obligation |
| Design responsibility | Employer designs; Contractor builds; Contractor design only where specified | Contractor designs and builds; latent errors in Employer's Requirements are Employer's risk (Sub-Clause 1.9) | Contractor designs and builds; Contractor responsible for accuracy of Employer's Requirements; near-total design risk transfer |
| Document hierarchy | Contract Agreement → Letter of Acceptance → Letter of Tender → PC → GC → **Specification** → Drawings → Schedules | Contract Agreement → Letter of Acceptance → Letter of Tender → PC → GC → **Employer's Requirements** → [Contractor's Proposal] → Schedules | Contract Agreement → PC → GC → **Employer's Requirements** → the Tender [no Letter of Acceptance] |
| Unforeseeable physical conditions | Contractor entitled to time and cost (Sub-Clause 4.12) | Contractor entitled to time and cost (Sub-Clause 4.12) | Contractor bears all risk — "accepts total responsibility for having foreseen all difficulties and costs" (Sub-Clause 4.12) |
| EOT grounds | Full list including adverse climatic conditions (Sub-Clause 8.4) | Full list including adverse climatic conditions (Sub-Clause 8.4) | Adverse climatic conditions and unforeseeable shortages removed — narrower entitlement |

#### FIDIC 1999 vs 2017 differences (apply across all three books where noted)

| Issue | FIDIC 1999 | FIDIC 2017 |
|---|---|---|
| Document priority clause | 1.5 | 1.5 (trigger changed from "ambiguity or discrepancy" to "conflict, ambiguity or discrepancy") |
| Engineer's determination (Red/Yellow) | Cl. 3.5 — no time limit; duty is fairness only | Cl. 3.7 — 42-day consultation + 42-day determination (84 days total); deemed rejection if no determination; Engineer must act "neutrally" |
| Employer's Representative determination (Silver) | Cl. 3.5 — same wording as Red/Yellow 1999 but Employer makes determination — irreconcilable conflict of interest | Cl. 3.5 — 84-day timetable adopted; no express "neutrality" obligation (deliberately omitted from Silver Book) |
| Contractor's claims | Cl. 20.1 — Contractor only; 28-day notice time bar; 42-day detailed claim | Cl. 20.2 — both parties symmetric; 28-day notice time bar retained; 84-day detailed claim; legal basis statement required within 84 days or Notice lapses; 14-day safety net |
| Employer's claims | Cl. 2.5 — separate, asymmetric, no time bar | Cl. 20.2 — symmetric with Contractor claims |
| Dispute board | Red Book: standing DAB (Cl. 20.4); Yellow/Silver: ad hoc DAB | All three books: standing DAAB (Cl. 21.1) — harmonised; avoidance function added (Cl. 21.3) |
| Notice of Dissatisfaction | Cl. 20.4 — 28 days from DAB decision | Cl. 21.4 — 28 days from DAAB decision |
| EOT clause | 8.4 | 8.5 (8.4 in 2017 = Advance Warning obligation) |
| Advance Warning | Not present | Cl. 8.4 — new obligation (Red and Yellow Books) |
| Notice form requirements | Cl. 1.3 — in writing; no defined term "Notice" | Cl. 1.3 — defined term "Notice" (capital N); five formal requirements: in writing, signed original or electronic from assigned address, identified as a Notice, delivered by specified method, sent to Contract Data address; ~80 places in 2017 Red Book require formal Notices |
| Payment certification | Engineer issues IPC | Red/Yellow: Engineer issues IPC; Silver: Employer gives notice of amount "fairly considers due" — no independently issued IPC |
| Performance Security | Employer calls without notice | Employer must give written notification before calling; return within 21 days after Performance Certificate; adjustment if Contract Price changes >20% |

### 2.2 FIDIC Document Hierarchy — Book-by-Book

Document hierarchy is the first task of `contract_assembly.md`. The hierarchy differs meaningfully across books and editions.

**Red Book 1999 (8 items):**
Contract Agreement *(if any)* → Letter of Acceptance → Letter of Tender → Particular Conditions → General Conditions → Specification → Drawings → Schedules and any other documents

**Red Book 2017 (11 items):**
Contract Agreement *(mandatory, no "if any")* → Letter of Acceptance → Letter of Tender → Particular Conditions Part A – Contract Data → Particular Conditions Part B – Special Provisions → General Conditions → Specification → Drawings → Schedules → JV Undertaking *(if applicable)* → any other documents

**Yellow Book 1999 (8 items):**
Contract Agreement *(if any)* → Letter of Acceptance → Letter of Tender → Particular Conditions → General Conditions → **Employer's Requirements** → Schedules → any other documents
*Note: "Employer's Requirements" replaces both "Specification" and "Drawings." Drawings are removed as a standalone item because the Contractor produces them. Contractor's Proposal falls under the catch-all.*

**Yellow Book 2017 (11 items):**
Contract Agreement → Letter of Acceptance → Letter of Tender → Particular Conditions Part A – Contract Data → Particular Conditions Part B – Special Provisions → General Conditions → **Employer's Requirements** → Schedules → **Contractor's Proposal** *(explicitly listed at position 9, below Employer's Requirements — confirming Employer documents prevail over Contractor documents on conflict)* → JV Undertaking → any other documents

**Silver Book 1999 (5 items):**
Contract Agreement *(mandatory)* → Particular Conditions → General Conditions → **Employer's Requirements** → the Tender and any other documents
*Note: Only 5 items — no Letter of Acceptance or Letter of Tender because EPC/Turnkey contracts follow a negotiated-agreement model, not tender-acceptance. Contractor's Proposal is subsumed within "the Tender."*

**Silver Book 2017 (9 items):**
Contract Agreement → Particular Conditions Part A – Contract Data → Particular Conditions Part B – Special Provisions → General Conditions → **Employer's Requirements** → Schedules → the Tender → JV Undertaking → any other documents
*Note: Still no Letter of Acceptance or Letter of Tender.*

**Governing principle consistent across all books and editions:** The Particular Conditions override the General Conditions. Employer's Requirements occupies the same relative rank position across Yellow and Silver Books — immediately after General Conditions, before any Contractor documents. The 2017 editions narrow the trigger for applying the hierarchy from "ambiguity or discrepancy" to "conflict, ambiguity or discrepancy."

### 2.3 FIDIC Golden Principles (2019)

FIDIC published five Golden Principles that govern how Particular Conditions may amend the General Conditions. GP3 requires that risk be allocated to the party that can control and bear the consequences of that risk. Particular Conditions that violate these principles are common in GCC projects and are forensically significant. Note: the Silver Book's Clause 4.12 risk transfer to the Contractor is not a Golden Principle violation — it is a deliberate feature of the Silver Book's design philosophy, not a Particular Conditions amendment.

---

## 3. GCC-Specific Legal Practice

### 3.1 UAE

**Abu Dhabi:** The Abu Dhabi Government Conditions of Contract (ADGCC) is mandatory for private sector entities contracting with Abu Dhabi government entities on capital projects. It comprises two separate versions: a construction works contract based on FIDIC 1999 Red Book and a design-and-build contract based on FIDIC 1999 Yellow Book.

The ADGCC was **revised in 2024** by the Abu Dhabi Projects and Infrastructure Centre (ADPIC) under the Department of Municipalities and Transport, with Dentons as legal advisor. The 2024 revision incorporates FIDIC 2017-aligned features including mandatory DAABs and pilots Conflict Avoidance Panels. ADPIC received the FIDIC Contract Users Award 2024 for this revision. Whether the 2024 version formally migrates to the FIDIC 2017 base text or retains the 1999 base with 2017-style enhancements has not been publicly confirmed. Forensic significance: projects procured post-2024 under ADGCC may have DAAB provisions not present in earlier ADGCC contracts.

Key ADGCC modifications to standard FIDIC: Employer-favourable risk reallocation, Engineer's independence circumscribed (Employer approval required for material decisions), UAE law as governing law, bilingual contract requirements (Arabic prevails), alignment with Article 880 decennial liability, and (post-2024) mandatory dispute board provisions.

**Dubai:** Dubai procurement law does not recognise FIDIC contracts — it uses its own procurement regulations. A project nominally using FIDIC in Dubai may have its contractual mechanisms overridden by Dubai procurement law. This is a critical forensic flag.

**Decennial liability:** UAE Civil Code Article 880 imposes 10-year joint liability on architect and contractor for defects that may lead to building collapse. Cannot be contracted out of. Runs in parallel with FIDIC defects liability provisions. Applies regardless of which FIDIC book governs.

**DIFC Court guidance on Clause 20.1:** Key decisions (FIVE v Reem; Panther v Modern Executive) confirm the 28-day time bar is strictly enforced. Notices do not require a prescribed form but must be within time. Implied good faith obligations do not override a missed time bar.

**UAE courts and Silver Book:** UAE courts routinely appoint their own technical experts rather than deferring to contractual decision-makers, so the Engineer/Employer's Representative distinction has limited impact at litigation stage. UAE Civil Code Article 246 good faith obligations provide potential grounds to challenge self-interested Employer's Representative determinations.

**Dispute resolution:** LCIA and DIAC are common. DAABs have gained traction following the 2024 ADGCC revision but are not yet universal.

### 3.2 Saudi Arabia

**Governing contract:** FIDIC 1999 Red Book dominates. Vision 2030 mega-projects use 1999 FIDIC as base. 2017 editions not yet in significant use in the Kingdom.

**Critical amendments commonly seen:**
- DAB clause typically removed — replaced with SCCA arbitration in Riyadh as final resolution
- Clause 14.8 (financing charges) removed or modified — prohibited under Sharia law (riba)
- Liquidated damages: Civil Transactions Law (CTL) **Article 179** allows courts to reduce LDs if proved "excessive"
- New: **CTL Article 95** (2023 Civil Transactions Law) introduces good faith obligations that apply to contract performance and interpretation — relevant to Employer's Representative determinations and certifications
- Decennial liability under Saudi Building Code Implementing Regulations Article 29 — 10 years, joint liability

**Language:** Arabic has historically been the governing language for Saudi government contracts. Dual-language contracts present interpretation risks.

### 3.3 Qatar

FIDIC 1999 Red Book widely used. Qatar FIFA World Cup infrastructure projects used FIDIC extensively. Government contracts cap liquidated damages at **10% of contract value**. Most state entities (Ashghal, Qatar Rail, Qatar Foundation) use heavily amended FIDIC forms that are essentially bespoke.

**New — time bar enforceability:** **Qatar Civil Code Article 418** limits contractual shortening of prescription periods. This raises enforceability questions about the Sub-Clause 20.1 (1999) / Sub-Clause 20.2.1 (2017) 28-day time bar in Qatar-seated disputes. A contractor who missed the time bar may argue Article 418 renders the contractual shortening unenforceable. This is forensically significant — a notice compliance finding in Qatar must be flagged as subject to this enforceability question.

Kuwait, Qatar, and Saudi Arabia tend toward litigation over arbitration compared to UAE which favours arbitration. Silver Book Employer's Representative determinations: Qatar courts, like UAE courts, routinely appoint their own technical experts — Qatar proportionality principles provide potential grounds to challenge self-interested determinations.

### 3.4 Engineer Role Fragmentation in GCC

A critical GCC-specific pattern: in many Red Book and Yellow Book projects, the Engineer's role is split between a Supervision Consultant (SC) handling technical matters and a Construction Manager (CM) or Project Management Consultant (PMC) handling administrative matters. FIDIC does not provide for this split — it assumes one Engineer. This creates genuine ambiguity about who is "the Engineer" for the purpose of claim notices, payment certificates, and determinations.

The forensic task: identify from the contract documents and correspondence who is actually performing each Engineer function, and flag where the split creates gaps or contradictions.

**Note for Silver Book projects:** The Engineer role fragmentation issue does not arise because there is no Engineer. However, the equivalent issue arises if the Employer's Representative delegates authority — the delegation must be documented and its scope verified, because challenges to determinations made outside the delegated scope are a known pattern.

---

## 4. Required Document Types for Legal Assessment

| Document type | Legal assessment purpose | Book-specific notes |
|---|---|---|
| Contract Agreement | Primary contract formation document; book type identification; document hierarchy confirmation | Silver Book 1999: mandatory (no "if any"); no Letter of Acceptance |
| Letter of Acceptance | Marks contract formation; may include qualifications or additional terms | Not present in Silver Book — contract formed by negotiated agreement |
| Letter of Tender / Appendix to Tender / Contract Data | Project-specific parameters (Time for Completion, LD rate, retention, DNP period) | All books; "Appendix to Tender" in 1999; "Contract Data" in 2017 |
| Particular Conditions (Part II / Part A and B) | Most critical document — all amendments to standard General Conditions | All books; 2017 splits into Part A (Contract Data) and Part B (Special Provisions) |
| General Conditions (Part I) | FIDIC standard terms — read with Particular Conditions | All books; book type determines which standard conditions apply |
| Employer's Requirements | Design brief; defines Contractor's design obligations | Yellow and Silver Books only — not present in Red Book |
| Contractor's Proposal | Contractor's design response to Employer's Requirements | Yellow and Silver Books; in Yellow Book 2017 explicitly ranked in hierarchy (position 9) |
| Performance Security / Bond | Current? Correct form? Correct amount? On-demand or conditional? | All books; 2017: Employer must give written notice before calling |
| Parent Company Guarantee | Current? Properly executed? | All books |
| Insurance certificates | Coverage types, amounts, and beneficiaries | All books |
| Engineer's appointment / Delegation notice | Who is the Engineer; delegated authority scope | Red and Yellow Books only |
| Employer's Representative appointment | Who is the Employer's Representative; delegated authority scope | Silver Book only |
| Engineer's / Employer's Representative's instructions | Valid? Within authority? Properly issued per Clause 1.3? | All books; decision-maker identity differs |
| Contractual notices (all types) | Valid? In time? Correct form? Routed correctly? | All books; 2017 formal Notice requirements apply |
| Contract amendments / Supplemental agreements | What has been changed from the original contract? | All books |
| Side letters | Do they override the main contract terms? | All books |
| Novation agreements | Has the contract been novated? | All books |
| Settlement agreements | What has been agreed and released? | All books |

---

## 5. Proposed Skill Files — Task-Based

The five skill files are confirmed task-based. Each covers one discrete task the specialist performs. The Yellow and Silver Book implications for each are noted below — these must be reflected in the skill file content.

| Skill file | Task | Yellow Book notes | Silver Book notes |
|---|---|---|---|
| `contract_assembly.md` | Contract document completeness check, hierarchy identification, Particular Conditions amendment mapping | Employer's Requirements replaces Specification and Drawings in hierarchy; Contractor's Proposal explicitly ranked in 2017 | Hierarchy is shortest (5 items in 1999, 9 in 2017); no Letter of Acceptance; contract formed by negotiated agreement; Contractor's Proposal subsumed in "the Tender" |
| `engineer_identification.md` | Engineer role identification, authority mapping, GCC split-role pattern, delegation validity | Engineer role identical to Red Book | No Engineer — identify Employer's Representative under Clause 3; flag absence of independent certifier; flag conflict of interest in determinations; check delegation scope; 2017: no "neutrality" obligation on Employer's Representative |
| `notice_and_instruction_compliance.md` | Notice validity, instruction validity, Clause 1.3 compliance, routing and form requirements | Notice requirements identical to Red Book; routing to Engineer | Notice requirements identical procedurally; notices routed to Employer or Employer's Representative, not Engineer; 2017 formal Notice requirements apply equally |
| `entitlement_basis.md` | FIDIC clause identification for claimed events, Particular Conditions modification check, GCC-specific entitlement patterns | Design entitlement under Sub-Clause 1.9 for latent errors in Employer's Requirements — Employer's risk; fitness-for-purpose obligation on Contractor; EOT grounds include adverse climatic conditions | Sub-Clause 4.12 risk transfer — Contractor "accepts total responsibility for having foreseen all difficulties"; no Sub-Clause 1.9 relief for latent errors; EOT grounds narrower (adverse climatic conditions removed); Silver Book Particular Conditions often further restrict entitlement — check carefully |
| `key_dates_and_securities.md` | Contractual dates (commencement, Time for Completion, DNP), bond and security validity, milestone identification | Time for Completion, DNP, and security instruments operate identically to Red Book | Time for Completion, DNP, and security instruments operate identically; Performance Security: 2017 written notification requirement before calling applies equally |

**Confirmed across all three books:** The 28-day Notice of Claim time bar (Clause 20.1 in 1999; Clause 20.2.1 in 2017) is substantively identical across Red, Yellow, and Silver Books. The only mechanical difference is the decision-maker: Engineer in Red/Yellow, Employer or Employer's Representative in Silver. Claims procedure, deadlines, and time-bar consequences are the same. Note Qatar-specific enforceability caveat at Section 3.3.

---

## 6. Research Verdict

The five task-based skill files defined in Section 5 are confirmed as the correct scope for Phase 3. The Yellow and Silver Book content does not require additional skill files — it requires each of the five skills to handle all three books. The key additions from this research:

- `engineer_identification.md` has the most significant Yellow/Silver variation — the Silver Book task is fundamentally different (Employer's Representative, no independence, conflict of interest flag)
- `entitlement_basis.md` has the second most significant variation — Silver Book Sub-Clause 4.12 risk transfer eliminates entitlements that exist in Red and Yellow Books
- `contract_assembly.md` requires book-specific hierarchy logic for all six book/edition combinations
- `notice_and_instruction_compliance.md` and `key_dates_and_securities.md` are substantially harmonised across books — the procedure is the same, the decision-maker identity differs

**Proceed with authorship of the five skill files in the order listed.**

---

*Document Control: Version 1.2 — April 2026 — Yellow Book and Silver Book coverage added across all sections; ADGCC 2024 revision added; Qatar Article 418 time bar enforceability added; Saudi CTL 2023 Article 95 added*
