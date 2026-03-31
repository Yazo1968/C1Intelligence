# Legal & Contractual — Domain Research Summary
## Phase 3 Pre-Authorship Research · C1 Intelligence Platform

**Version:** 1.1
**Date:** March 2026
**Purpose:** Required by `SKILLS_STANDARDS.md` Section 4.3 before any Phase 3 skill authorship begins.

---

## 1. What the Legal & Contractual Specialist Does

The Legal & Contractual specialist in C1 is a forensic analysis agent, not a contract drafter. Its role is to read existing project documents from the warehouse and answer questions about the contractual position — what the contract says, whether obligations have been met, whether instructions are valid, what entitlement basis applies to a claimed event, and where documents contradict each other on legal and contractual matters.

**How it gets project-specific facts:** The agent retrieves them from the warehouse. The governing FIDIC edition is determined by reading the Particular Conditions and Contract Agreement (Layer 1 documents). The Engineer's identity is determined by reading the Engineer's appointment letter and contract. Key dates come from the Appendix to Tender / Contract Data. FIDIC standard conditions are available as Layer 2 reference documents. No project-specific facts are hardcoded into skill files.

The specialist's tasks fall into two categories:

**Foundational tasks** — performed regardless of the specific query, because this information underpins everything Claims, Schedule, and Governance will do:
- Identify which contract documents govern and in what order of precedence
- Identify who the Engineer is and what authority they have
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

### 2.1 FIDIC Red Book — Primary Governing Standard

Both 1999 and 2017 editions are in active use across the GCC. The 1999 edition dominates in Saudi Arabia (including NEOM, The Line, Trojena, Qiddiya), Abu Dhabi Government projects, and most established government projects. The 2017 edition is increasingly used on newer international projects and by sophisticated private sector employers.

Key differences that affect Legal & Contractual analysis:

| Issue | FIDIC 1999 | FIDIC 2017 |
|---|---|---|
| Document priority clause | 1.5 | 1.5 (unchanged) |
| Engineer's authority and role | Cl. 3 — acts for Employer but makes fair determinations | Cl. 3 — acts neutrally between parties when determining; enhanced impartiality language |
| Engineer's determination | Cl. 3.5 — no time limit specified | Cl. 3.7 — 84-day time limit; deemed rejection if no determination issued |
| Communications | Cl. 1.3 — notices in writing | Cl. 1.3 — notices in writing; additional requirements on form |
| Employer's claims | Cl. 2.5 — separate, asymmetric | Cl. 20 — symmetric with Contractor's claims |
| Claims procedure | Cl. 20.1 — Contractor only | Cl. 20.2 — both parties; same procedure |
| DAB/DAAB | Cl. 20.4 — DAB (adjudication only) | Cl. 21.4 — DAAB (avoidance + adjudication; standing board) |
| Advance warning | Not present | Cl. 8.4 — new obligation |
| Notice of Dissatisfaction | Cl. 20.4 — 28 days from DAB decision | Cl. 21.4 — 28 days from DAAB decision |

### 2.2 FIDIC Document Hierarchy

Under Clause 1.5 (both editions), in case of ambiguity or discrepancy, the following order of precedence applies (highest to lowest):

1. Contract Agreement
2. Letter of Acceptance
3. Letter of Tender (including Appendix to Tender / Contract Data)
4. Particular Conditions (Part II)
5. General Conditions (Part I)
6. Specification
7. Drawings
8. Schedules and any other documents listed in the Contract Agreement or Letter of Acceptance

The Particular Conditions override the General Conditions. This is where GCC-specific amendments live and is the single most important document for forensic legal analysis — the amendments in the Particular Conditions may remove, modify, or add to entitlements defined in the General Conditions.

### 2.3 FIDIC Golden Principles (2019)

FIDIC published five Golden Principles that govern how Particular Conditions may amend the General Conditions. GP3 requires that risk be allocated to the party that can control and bear the consequences of that risk. Particular Conditions that violate these principles are common in GCC projects and are forensically significant.

---

## 3. GCC-Specific Legal Practice

### 3.1 UAE

**Abu Dhabi:** The Abu Dhabi Government Conditions of Contract (ADGCC) is mandated for Abu Dhabi government department projects. Based on FIDIC 1999 Red and Yellow Books but heavily amended to shift risk from Employer to Contractor.

**Dubai:** Dubai procurement law does not recognise FIDIC contracts — it uses its own regulations. A project nominally using FIDIC in Dubai may have its contractual mechanisms overridden by Dubai procurement law. This is a critical forensic flag.

**Decennial liability:** UAE Civil Code Article 880 imposes 10-year joint liability on architect and contractor for defects that may lead to building collapse. Cannot be contracted out of. Runs in parallel with FIDIC defects liability provisions.

**DIFC Court guidance on Clause 20.1:** Key decisions (FIVE v Reem; Panther v Modern Executive) confirm the 28-day time bar is strictly enforced. Notices do not require a prescribed form but must be within time. Implied good faith obligations do not override a missed time bar.

**Dispute resolution:** LCIA and DIAC are common. DABs used on large projects but not standard.

### 3.2 Saudi Arabia

**Governing contract:** FIDIC 1999 Red Book dominates. Vision 2030 mega-projects use 1999 FIDIC as base.

**Critical amendments commonly seen:**
- DAB clause typically removed — replaced with SCCA arbitration as final resolution
- Clause 14.8 (financing charges) removed or modified — prohibited under Sharia law (riba)
- Liquidated damages: CTL Article 179 allows courts to reduce LDs if proved "excessive"
- Decennial liability under Saudi Building Code Implementing Regulations Article 29 — 10 years, joint liability

**Language:** Arabic has historically been the governing language for Saudi government contracts. Dual-language contracts present interpretation risks.

### 3.3 Qatar

FIDIC 1999 Red Book widely used. Qatar FIFA World Cup infrastructure projects used FIDIC extensively. Kuwait, Qatar, and Saudi Arabia tend toward litigation over arbitration compared to UAE which favours arbitration.

### 3.4 Engineer Role Fragmentation in GCC

A critical GCC-specific pattern: in many projects, the Engineer's role is split between a Supervision Consultant (SC) handling technical matters and a Construction Manager (CM) handling administrative matters. FIDIC does not provide for this split — it assumes one Engineer. This creates genuine ambiguity about who is "the Engineer" for the purpose of claim notices, payment certificates, and determinations.

The forensic task: identify from the contract documents and correspondence who is actually performing each Engineer function, and flag where the split creates gaps or contradictions.

---

## 4. Required Document Types for Legal Assessment

| Document type | Legal assessment purpose |
|---|---|
| Contract Agreement | Primary contract formation document; document hierarchy confirmation |
| Letter of Acceptance | Marks contract formation; may include qualifications or additional terms |
| Letter of Tender / Appendix to Tender / Contract Data | Project-specific parameters (Time for Completion, LD rate, retention, DNP period) |
| Particular Conditions (Part II) | Most critical document — all amendments to standard General Conditions |
| General Conditions (Part I) | FIDIC standard terms — read with Particular Conditions |
| Performance Security / Bond | Current? Correct form? Correct amount? On-demand or conditional? |
| Parent Company Guarantee | Current? Properly executed? |
| Insurance certificates | Coverage types, amounts, and beneficiaries |
| Engineer's appointment / Delegation notice | Who is the Engineer; delegated authority scope |
| Engineer's instructions | Valid? Within authority? Properly issued per Clause 1.3? |
| Contractual notices (all types) | Valid? In time? Correct form? Routed correctly? |
| Contract amendments / Supplemental agreements | What has been changed from the original contract? |
| Side letters | Do they override the main contract terms? |
| Novation agreements | Has the contract been novated? |
| Settlement agreements | What has been agreed and released? |

---

## 5. Proposed Skill Files — Task-Based

The original AGENT_PLAN.md heading list was topic-based. Research confirms skills must be task-based. Each skill file covers one discrete task the specialist performs.

| Skill file | Task it enables |
|---|---|
| `contract_assembly.md` | Contract document completeness check, hierarchy identification, Particular Conditions amendment mapping |
| `engineer_identification.md` | Engineer role identification, authority mapping, GCC split-role pattern, delegation validity |
| `notice_and_instruction_compliance.md` | Notice validity, instruction validity, Clause 1.3 compliance, routing and form requirements |
| `entitlement_basis.md` | FIDIC clause identification for claimed events, Particular Conditions modification check, GCC-specific entitlement patterns |
| `key_dates_and_securities.md` | Contractual dates (commencement, Time for Completion, DNP), bond and security validity, milestone identification |

**What was removed from the original list and why:**
- "Contradiction patterns" as a standalone skill is removed — contradictions are detected within each task, not in a separate file
- "GCC-specific contract administration patterns" as a standalone skill is removed — GCC-specific content is embedded within each of the five task-based skills

**What was added and why:**
- `key_dates_and_securities.md` is new — contractual dates and security instruments are foundational to Claims, Schedule, and Governance. The Legal specialist must extract and validate these for Round 2 specialists to use.

---

## 6. Research Verdict

The original AGENT_PLAN.md skill areas were directionally correct but topic-based rather than task-based, missing `key_dates_and_securities`, and had contradiction patterns and GCC content incorrectly proposed as standalone skills.

**Recommendation: proceed with the five task-based skill files defined in Section 5.**

---

*Document Control: Version 1.1 — March 2026 — Playbook references removed; warehouse architecture clarified*
