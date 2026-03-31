# C1 — Skills Standards and Requirements
## Governing Reference for All Agent Skill File Authorship

**Version:** 1.1
**Status:** Active — Governing Document
**Location:** `docs/SKILLS_STANDARDS.md`
**Applies to:** All six domain specialists — Legal & Contractual, Commercial & Financial, Schedule & Programme, Technical & Design, Claims & Disputes, Governance & Compliance

---

## 1. Purpose

This document defines the standards and requirements for writing skill files for any C1 agent. It governs how skill files are structured, what they must contain, how domain research is conducted before authorship begins, what quality standard a file must meet, and how files are validated before deployment.

This document eliminates the need to re-establish these standards for every phase of skill authorship. Any person authoring skill files for any C1 agent — regardless of domain — reads this document first and follows it completely.

---

## 2. What a Skill File Is

A skill file is a markdown file that tells a C1 domain specialist agent how to perform a specific task. It is not a reference document, a knowledge base entry, or a training guide. It is an operational instruction file.

The agent reads the skill file as part of its system prompt. It then applies the instructions when reasoning over retrieved document chunks in response to a user query. The agent uses its own intelligence (Claude) to interpret and apply the skill — the skill file provides the framework, not a rigid script.

**The warehouse is the source of truth for project-specific facts.** The skill file tells the agent how to analyse. The warehouse — via pgvector retrieval — provides the evidence. Project-specific facts (FIDIC edition, Engineer identity, contract sum, key dates) are never hardcoded into skill files. The agent retrieves them from the project documents already in the warehouse.

The warehouse has two document layers:
- **Layer 1 — Project-specific documents:** Contracts, drawings, notices, correspondence, claims, reports, schedules, approvals — the 176 document types from the taxonomy. Retrieved via pgvector at query time.
- **Layer 2 — Reference documents:** FIDIC conditions of contract, PMBOK, IFRS, applicable laws, government authority policies, DOA matrices. Global, static, non-project-specific. Retrieved via pgvector at query time.

**A skill file contains:**
- When to activate (trigger conditions)
- What to do, step by step (workflow)
- How to classify findings (decision framework)
- When to call tools for more evidence (insufficiency indicators)
- What to flag regardless of the query (mandatory flags)
- What the output must look like (output format)
- The domain knowledge that underpins the above (standards, frameworks, references)

**A skill file does NOT contain:**
- Code or logic
- Generic definitions that the agent already knows
- Verbatim reproduction of contract clauses
- Project-specific facts (FIDIC edition, Engineer, contract sum, key dates) — these come from the warehouse
- Content that could apply equally to any domain without modification

---

## 3. Skill File Structure — Mandatory for Every File

Every skill file must follow this structure in this order. Sections may not be omitted.

### 3.1 Activation Header

```
## When to apply this skill
```

One to three sentences stating which query types or document patterns activate this skill. Be specific. "When a delay is mentioned" is too vague. "When retrieved chunks contain a Notice of Delay, an EOT claim submission, or a reference to a specific delay event" is correct.

### 3.2 Pre-Flight Check

```
## Before you begin
```

What the agent must verify before starting its analysis. Typically: confirm which Round 1 findings are available (for Round 2 specialists), and identify any foundational facts already established by upstream specialists that this skill should not duplicate. This prevents redundant retrieval and ensures the skill builds on — rather than restates — what has already been found.

For Round 2 specialists (Claims, Schedule, Technical, Governance): this section must explicitly list which Round 1 findings to read and what to extract from them before beginning.

For Round 1 specialists (Legal, Commercial): this section confirms what needs to be retrieved from the warehouse before the analysis begins.

### 3.3 Workflow

```
## Analysis workflow
```

Numbered steps. Each step is a discrete action: retrieve something, assess something, classify something, flag something. Steps must be sequenced correctly — the order matters. Earlier steps may gate later steps (e.g. if notice is time-barred, flag it and note the entitlement impact before proceeding to quantum).

Maximum depth: 8 steps per skill. If more than 8 steps are needed, the skill is doing too much and should be split into two files.

### 3.4 Decision Framework

```
## Classification and decision rules
```

The explicit criteria the agent uses to classify its findings. Must use structured if/then logic or tables. For every classification outcome, the criteria must be stated — not left to inference.

Examples of the type of content required:
- "If the notice date is more than 28 days after the awareness date: classify as POTENTIALLY TIME-BARRED. Flag immediately regardless of other findings."
- "If the delay is caused by an Employer Risk Event and critical path impact is demonstrated: entitlement is EOT + Cost. If delay is neutral event: entitlement is EOT only."

### 3.5 Insufficiency Indicators

```
## When to call tools
```

The specific conditions under which the agent must call a tool to retrieve more evidence before concluding. Phrased as observable signals in the retrieved chunks, not abstract principles.

For each condition, state: the signal, the tool to call, and what to look for in the result.

The four available tools are:
- `search_chunks(query, filters)` — refined search against pgvector
- `get_document(document_id)` — retrieve full document when chunks are insufficient
- `get_contradictions(document_ids)` — check existing contradiction flags
- `get_related_documents(document_type, date_range)` — find related documents by type

### 3.6 Mandatory Flags

```
## Always flag — regardless of query
```

A list of conditions that must always be surfaced in the output, even if the user's query did not ask about them. These are the forensically critical signals that an expert would never omit from a review.

Every skill file must have at least three mandatory flags. If a domain has no forensically critical conditions that apply regardless of the query, the skill file is not deep enough.

### 3.7 Output Format

```
## Output format
```

The exact structure the agent's findings text must follow for this skill. Headings, sequence, and required fields. If a finding requires a table, specify the columns. If a finding requires a confidence classification, specify the classification criteria.

The output format must be consistent with `SpecialistFindings.findings` (a structured text string) and must be readable by the synthesis layer and by a human reviewer.

### 3.8 Domain Knowledge

```
## Domain knowledge and standards
```

The substantive knowledge that underpins the workflow. This section is where FIDIC clauses, SCL Protocol principles, AACE methodology guidance, GCC-specific patterns, and forensic signals live. This is the only section where reference material is appropriate.

Rules for this section:
- Every claim must cite a source (FIDIC sub-clause, SCL Protocol core principle, AACE RP 29R-03 MIP number, etc.)
- Both FIDIC 1999 and 2017 must be addressed where they differ
- GCC-specific practice must be explicitly identified as such, not conflated with general FIDIC guidance
- Content must be actionable — "know this and apply it", not "here is a summary of the standard"

---

## 4. Domain Research Requirements

No skill file may be written without prior domain research. The research validates that the skill covers the tasks professionals actually perform, uses the methodologies the industry recognises, references the correct standards, and handles the document types and formats that appear in real projects.

### 4.1 Governing Standards by Domain

The following standards must be understood before authoring skill files for the relevant domain. For each domain, the author must be able to identify: the governing framework, the accepted methodologies, the required document types, and the output formats used by professional practitioners.

| Domain | Primary Standards | Methodology Frameworks | Key Document Types |
|---|---|---|---|
| Claims & Disputes | FIDIC Red Book 1999 & 2017 Cl. 20/21 | SCL Protocol 2nd Ed. 2017; AACE RP 29R-03 | Notice of Claim, EOT Claim, Delay Analysis Report, Expert Report, DAB/DAAB Decision |
| Schedule & Programme | FIDIC Cl. 8; SCL Protocol 2017 | TIA, As-Planned vs As-Built, Windows Analysis, Collapsed As-Built, Impacted As-Planned | Baseline Programme, Revised Programme, As-Built Programme, Progress Reports |
| Legal & Contractual | FIDIC Red Book 1999 & 2017 | Contract hierarchy analysis; notice sufficiency doctrine | Contract Agreement, Particular Conditions, Engineer's Instructions, Notices, Determinations |
| Commercial & Financial | FIDIC Cl. 12, 13, 14; IFRS 15 | BOQ measurement; variation valuation; prolongation cost methodology | BOQ, IPC, Variation Order, Payment Application, Final Account |
| Technical & Design | FIDIC Cl. 5, 7; relevant engineering standards | Specification compliance assessment; design change impact | Specifications, Drawings, RFIs, Shop Drawing Submittals, NCRs |
| Governance & Compliance | FIDIC Cl. 3; applicable authority matrices | DOA compliance; approval chain verification | Project Charter, DOA Matrix, Committee Minutes, Audit Reports |

### 4.2 Research Depth Required

Before authoring skill files for a domain, the author must be able to answer all of the following:

**Methodology questions:**
- What methodologies do professional practitioners use in this domain?
- Which methodologies are accepted by GCC arbitration tribunals?
- Where do the SCL Protocol and AACE RP 29R-03 agree and differ on this domain?
- What does FIDIC require the agent to prove, and what methodology governs how to prove it?

**Document questions:**
- What document types appear in this domain on a typical GCC project?
- What are the required fields and formats of each document type?
- What constitutes a sufficient document versus a defective one in this domain?
- What contradiction patterns recur across document types in this domain?

**GCC-specific questions:**
- How do UAE, Saudi Arabia, and Qatar practice differ from generic FIDIC guidance in this domain?
- What authority requirements apply (DIFC Court guidance, local arbitration centre practice, government authority approval chains)?
- What language and dual-document issues arise in this domain?

### 4.3 Research Validation

Before beginning skill authorship, the author must produce a one-page domain research summary that answers the questions in 4.2. This summary is reviewed and approved before any skill file is drafted. The summary becomes part of the project record.

---

## 5. Skill File Quality Standard

Every skill file is assessed against the following criteria before it is committed.

### 5.1 Operational, Not Informational

The skill file tells the agent what to do, not what the rules are. The test: remove all domain knowledge from Section 3.8. Can the agent still follow the workflow? If the workflow references knowledge that only exists in Section 3.8 without bridging it back to action steps, the skill is not operational.

### 5.2 GCC-Specific Where It Matters

Generic FIDIC commentary is available everywhere. The skill must encode what is specific to the GCC market: DIFC Court interpretations of FIDIC notice provisions, Saudi arbitration centre practice, Qatar FIFA infrastructure project patterns, UAE authority approval requirements. Where GCC practice deviates from or supplements generic FIDIC guidance, the skill must address both.

### 5.3 Edition-Specific Where It Matters

Where FIDIC 1999 and 2017 differ in a way that affects the analysis — clause numbering, time periods, procedural requirements, symmetric vs. asymmetric obligations — both editions must be addressed. The agent determines which edition governs by reading the project's contract documents from the warehouse.

Key differences that must always be addressed in any skill file that references FIDIC claims procedure:

| Issue | FIDIC 1999 | FIDIC 2017 |
|---|---|---|
| Notice of Claim clause | 20.1 | 20.2.1 |
| Time bar | 28 days from awareness | 28 days from awareness |
| Detailed claim submission | 42 days | 84 days |
| Employer's Claims | Clause 2.5 (separate) | Clause 20 (symmetric with Contractor) |
| Engineer's Determination | Clause 3.5 | Clause 3.7 (time-limited) |
| Dispute Adjudication Board | Clause 20.4 (DAB) | Clause 21.4 (DAAB) |
| EOT clause | 8.4 | 8.5 (8.4 in 2017 = Advance Warning) |
| Notice of Dissatisfaction | Clause 20 | Clause 21 (28 days from determination) |

### 5.4 Instructional Framing

The skill file is written so the agent knows what to do, not just what the rules are. Preferred framing: "When you see X, do Y because Z." Not: "Under FIDIC Clause 20.1, the contractor must give notice within 28 days."

### 5.5 No Silent Gaps

Every failure mode must be addressed. If the retrieved chunks contain no notice document, the skill must tell the agent what to do. If the programme is missing, the skill must tell the agent what to flag. If the FIDIC edition cannot be determined from the retrieved documents, the skill must provide a fallback.

### 5.6 Output Format Consistency

The output format defined in Section 3.7 of the skill file must produce findings that the synthesis layer can process. The findings text must be structured, source-attributed, and classified by confidence level. Unstructured narrative is not acceptable.

---

## 6. Claims & Disputes Domain: Specific Standards

Claims & Disputes is the most forensically sensitive domain. It requires additional standards beyond the general requirements above.

### 6.1 Professional Framework

Claims & Disputes skill files must be consistent with the working methodology of professional claims consultants, quantum experts, and forensic delay analysts as defined by the following:

**SCL Delay and Disruption Protocol, 2nd Edition (2017):** The governing framework for delay analysis methodology in the GCC market. Key principles: contemporary analysis is preferred over retrospective; no single methodology is universally preferred for retrospective analysis; concurrent delay must be addressed; float is a shared resource absent express contractual stipulation; records are the foundation of every delay claim.

**AACE International Recommended Practice 29R-03 — Forensic Schedule Analysis:** The forensic methodology standard. Defines nine schedule analysis methodologies across a five-layer taxonomy. Complements rather than conflicts with the SCL Protocol — FIDIC defines what must be proved and when; SCL/AACE define how to prove it.

**FIDIC Red Book 1999 and 2017:** The contractual framework. Defines entitlement, notice obligations, time bars, and the claims resolution procedure. Does not prescribe delay analysis methodology — that is left to SCL/AACE.

### 6.2 Professional Claim Assessment Workflow

Professional claims consultants assess claims in the following sequence. Skill files must reflect this sequence:

1. **Notice compliance** — Was the required notice given? Was it within the time bar? Was it sufficient in form and content? This gates everything else.
2. **Entitlement** — Does the FIDIC clause cited support the relief claimed? Is the required evidence present?
3. **Causation** — Is there a demonstrable causal link between the event and the claimed impact?
4. **Delay analysis** — What methodology has been applied? Is it appropriate? Does it comply with SCL/AACE standards?
5. **Quantum** — Is the cost claim properly supported? Are the heads of claim recoverable under the applicable FIDIC clause?
6. **Contradiction and credibility** — Are there contradictions between documents? Are there forensic signals that indicate reconstruction, inflation, or procedural deficiency?

### 6.3 Accepted Delay Analysis Methodologies

Skill files that address delay analysis must reference these methodologies by name and be able to identify which is being used in a document:

| Methodology | When typically used | Key data requirement |
|---|---|---|
| Time Impact Analysis (TIA) | Contemporaneous; prospective or near-contemporaneous retrospective | Programme updates, fragnets |
| As-Planned vs As-Built | Retrospective; simple projects or limited records | Baseline programme, as-built records |
| Impacted As-Planned | Retrospective; theoretical modelling | Baseline programme only — limited reliability |
| Collapsed As-Built | Retrospective; complex projects | As-built programme, delay events |
| Windows Analysis (Time Slice) | Retrospective; complex concurrent delay | Programme updates across defined periods |

### 6.4 Required Document Types for Claims Assessment

| Document type | Purpose in claims assessment |
|---|---|
| Notice of Claim / Notice of Delay | Triggers entitlement assessment and time bar check |
| EOT Claim submission | Full entitlement, causation, and quantum assessment |
| Delay Analysis Report | Methodology identification, critical path assessment |
| Quantum/Prolongation Cost Report | Cost methodology and heads of claim assessment |
| Contemporary records | Credibility and evidential basis assessment |
| Programme records | Delay analysis foundation |
| Expert Report | Methodology and opinion assessment |
| Engineer's Determination | Entitlement position and response to claim |
| DAB/DAAB Decision | Adjudication outcome |
| Notice of Dissatisfaction | Escalation trigger |
| Correspondence | Contemporaneous record and notice compliance |

### 6.5 Output Format for Claims Findings

Claims findings must follow this structure:

```
## Claims & Disputes Assessment

### Notice Compliance
[Claim reference] — [COMPLIANT / POTENTIALLY TIME-BARRED / NON-COMPLIANT / CANNOT ASSESS]
Awareness date: [date or "not determinable from documents"]
Notice date: [date or "not found in documents"]
Days elapsed: [number or "cannot calculate"]
Applicable clause: [FIDIC 1999 Cl. 20.1 / FIDIC 2017 Cl. 20.2.1]
Source documents: [document references]
Finding: [specific finding with source attribution]

### Entitlement Basis
Claimed under: [FIDIC clause]
Entitlement type: [EOT + Cost + Profit / EOT + Cost / EOT only / No entitlement / Cannot assess]
Required evidence present: [YES / PARTIAL / NO]
Finding: [specific finding with source attribution]

### Delay Analysis
Methodology identified: [methodology name or "not identifiable"]
SCL/AACE compliance: [COMPLIANT / ISSUES IDENTIFIED / CANNOT ASSESS]
Critical path impact demonstrated: [YES / PARTIAL / NO / NOT ADDRESSED]
Concurrent delay addressed: [YES / NO / NOT APPLICABLE]
Finding: [specific finding with source attribution]

### Quantum
Heads of claim: [list]
Recoverable under contract: [YES / PARTIAL / NO / CANNOT ASSESS]
Methodology appropriate: [YES / ISSUES IDENTIFIED / CANNOT ASSESS]
Finding: [specific finding with source attribution]

### Contradictions Flagged
[List of contradictions with source documents for each, or "None detected"]

### Forensic Signals
[List of signals identified, or "None detected"]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences maximum]
```

---

## 7. Validation Gate

Before any skill file set is deployed to production, it must pass the following validation tests. These tests apply to every domain — the specific scenarios differ but the structure is the same.

### 7.1 Positive Detection Test

Given a document set containing a known condition that the skill is designed to detect, the specialist must correctly identify and flag the condition. Pass criteria: condition identified, source document cited, classification correct.

### 7.2 Contradiction Detection Test

Given a document set containing a known contradiction between two documents, the specialist must detect and surface it with both source documents identified. Pass criteria: contradiction flagged, both documents cited, both values stated.

### 7.3 Negative Test

Given a document set that does not contain the condition the skill detects, the specialist must not fabricate a finding. Pass criteria: relevant section states the condition was not found.

### 7.4 Insufficient Context Test

Given a document set where a key document is missing, the specialist must call the appropriate tool before concluding, and flag the absence if the search returns nothing. Pass criteria: tool call evidenced in `tools_called`; absence flagged in output.

### 7.5 Validation Minimum

A minimum of five test scenarios per domain, covering at least one of each test type above. Scenarios must be defined before skill authorship begins.

---

## 8. Skill Sequencing and Dependencies

Some specialists depend on the outputs of others. Skill files must reflect these dependencies in their Pre-Flight Check (Section 3.2).

| Specialist | Depends on | Reason |
|---|---|---|
| Claims & Disputes | Legal & Contractual (Round 1) | Needs: governing FIDIC edition determination, contract hierarchy, notice obligations, Engineer identification |
| Claims & Disputes | Commercial & Financial (Round 1) | Needs: contract sum, certified amounts, variation register, LD cap |
| Schedule & Programme | Legal & Contractual (Round 1) | Needs: contractual milestones, EOT clause, programme submission requirement |
| Governance & Compliance | Legal & Contractual (Round 1) | Needs: Engineer's authority, delegation limits, contractual approval requirements |

The authorship sequence is:
1. Legal & Contractual skills (no upstream dependencies)
2. Commercial & Financial skills (no upstream dependencies)
3. Claims & Disputes skills (depends on Legal and Commercial)
4. Schedule & Programme skills (depends on Legal)
5. Governance & Compliance skills (depends on Legal)
6. Technical & Design skills (lightest dependencies)

---

## 9. Skill File Maintenance

Skill files are updated when:
- A real user query produces a weak or incorrect response traceable to a gap in the skill file
- A new FIDIC guidance note, SCL Protocol update, or AACE revision affects the methodology
- A GCC court or arbitration decision establishes new precedent relevant to the domain
- The validation gate reveals a gap

Updating a skill file requires no code change. Edit the markdown file, deploy, retest. This is Phase 8 of AGENT_PLAN.md.

All updates must be logged in `BUILD_LOG.md` with: the query or event that triggered the update, which file was changed, what was changed, and the date.

---

## 10. Document Control

| Field | Value |
|---|---|
| Version | 1.1 — Playbook concept removed; warehouse two-layer architecture clarified |
| Date | March 2026 |
| Location | `docs/SKILLS_STANDARDS.md` |
| Updated when | Standard revised, new domain added, or validation practice updated |
| Related documents | `docs/AGENT_PLAN.md`, `CLAUDE.md`, `README.md` |
