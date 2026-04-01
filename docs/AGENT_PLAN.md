# C1 — Agent Enhancement Plan
## From Stateless Specialists to True Domain Agents

**Version:** 1.4
**Status:** Active — Reference Document
**Last Updated:** March 2026

---

## Context

C1's six domain specialists were built in v1 as stateless Claude API calls — each receives retrieved document chunks, reasons, and returns findings. This plan upgrades them to true agents with tools, multi-round orchestration, and domain skill files.

**The principle governing this plan:**
- The flow (agentic loop, tool set, round structure) is the same for all six specialists
- The domain knowledge (skill files) is what differs between specialists
- Skill files are markdown — they can be deepened at any time without touching code
- Skill file authorship follows `SKILLS_STANDARDS.md` — the governing reference for all skill writing across all domains

---

## Design Principles — Locked Before Phase 1

These three decisions govern the architecture of the skill and agent system. They are locked. They must be implemented correctly in Phase 1 or everything built on top of them is wrong.

### Principle 1 — Dynamic skill loading, never hardcoded

The `SkillLoader` must load every markdown file present in a specialist's skill folder at runtime. It must never contain a hardcoded list of filenames.

A new skill is added by dropping a markdown file into the relevant folder and deploying. No code change. No configuration change. The agent picks it up automatically on the next query.

A skill is removed by deleting its file. A skill is updated by editing its file. In neither case does any code change.

This applies to all six specialists equally.

### Principle 2 — A new specialist requires no new agent code

The agentic loop, tool set, and output schema are identical for all specialists. They are defined once in `BaseSpecialist` and `tools.py`. They never change per specialist.

Adding a new specialist beyond the current six requires only:
- A new folder in `skills/` containing the domain skill files
- A new entry in `SpecialistConfig` — domain name, round assignment, max rounds
- A new entry in the orchestrator's domain routing table

No new Python class. No new tool. No new loop logic. If adding a specialist requires touching `base_specialist.py` or `tools.py`, that is a design failure.

### Principle 3 — Skills reason over the warehouse; the warehouse is the source of truth

Skill files encode generic construction domain knowledge — how to analyse, what to look for, what to flag, what frameworks to apply. They are reusable across every project on the platform.

Project-specific facts — which FIDIC edition governs, who the Engineer is, what the contract sum is, what the key dates are — are not in the skill files. They are in the project documents already in the warehouse. The agent retrieves these facts by calling tools against the warehouse, the same way it retrieves any other evidence.

The warehouse has two document layers, as defined in `README.md`:

**Layer 1 — Project-specific documents:** The 176 document types generated on a specific project (contracts, drawings, notices, correspondence, claims, reports, schedules, approvals). Retrieved via pgvector at query time.

**Layer 2 — Reference documents:** Global, static, non-project-specific documents providing the regulatory and standards framework (FIDIC conditions of contract, PMBOK, IFRS, applicable laws, government authority policies, DOA matrices). Retrieved via pgvector at query time.

The specialist reasons across all of this — its skill files tell it how, the warehouse gives it the evidence.

---

## Architecture Target

```
Orchestrator
    |
Round 1: Legal + Commercial
    | findings passed forward
Round 2: Claims + Schedule + Technical + Governance
    | (receive Round 1 findings as context)
Cross-Specialist Contradiction Pass
    |
Synthesis -> Confidence -> Audit Log -> Response
```

**Each specialist runs as a true agent:**
- Receives retrieved chunks from Layer 1 (project documents) and Layer 2 (reference documents)
- Receives query + (Round 2 only) Round 1 findings
- Assesses whether retrieved context is sufficient
- Calls tools if more information is needed
- Reasons over all evidence and returns structured findings
- Runs up to a configured maximum number of rounds

**Tools available to every specialist:**
1. `search_chunks(query, filters)` — refined semantic + full-text search against pgvector document_chunks, scoped to the project
2. `get_document(document_id)` — retrieve full document when chunks are insufficient
3. `get_contradictions(document_ids)` — check existing contradiction flags in database
4. `get_related_documents(document_type, date_range)` — find related documents by type

**Skill structure for every specialist (two layers):**
- Layer 1 — Flow: what to look for, when to call tools, what signals indicate insufficient context
- Layer 2 — Domain: the actual construction knowledge, FIDIC clauses, forensic frameworks

---

## Phase Status

| Phase | Description | Status |
|---|---|---|
| 1 | Agent Template | Complete |
| 2 | Multi-Round Orchestrator | Complete |
| 3 | Legal & Contractual Skills + Validation | Active — Prerequisites pending |
| 4 | Commercial & Financial Skills + Validation | Not Started |
| 5 | Claims & Disputes Skills + Validation Gate | Not Started |
| 6 | Remaining Three Specialists | Not Started |
| 7 | Cross-Specialist Contradiction Detection | Not Started |
| 8 | Iterative Skill Deepening | Ongoing — No Completion Date |

---

## Phase 1 — Agent Template

**Objective:** Build the reusable architecture all six specialists will share. Get this right before anything else moves.

**What gets built:**
- `BaseSpecialist` class — agentic loop: assess -> tool call if needed -> reason -> return
- Four shared tools: `search_chunks`, `get_document`, `get_contradictions`, `get_related_documents`
- `SkillLoader` — dynamically loads all markdown files from `skills/{domain}/` into the system prompt at runtime. No hardcoded filenames.
- `SpecialistConfig` — per-specialist configuration: domain name, round assignment, max rounds
- One stub specialist: Claims & Disputes — wired to template, minimal skill content, validates architecture only

**What does NOT get built:** Any other specialist. Real skill depth. Orchestrator changes.

**Completion criteria:**
- Stub Claims specialist calls tools correctly and returns structured findings
- SkillLoader dynamically loads all files in the folder — confirmed by adding and removing a test file without any code change
- Quality Guardian sign-off

---

## Phase 2 — Multi-Round Orchestrator

**Objective:** Rebuild orchestrator to support rounds with context handoff between them.

**What gets built:**
- Round 1 assignments: Legal & Contractual, Commercial & Financial
- Round 2 assignments: Claims & Disputes, Schedule & Programme, Technical & Design, Governance & Compliance
- Handoff mechanism: Round 1 structured findings passed as context to Round 2 specialists before they begin
- Updated synthesis: receives two-round findings, richer cross-domain input
- Audit log updated: records which round each finding originated from

**What does NOT get built:** Real skill depth for any specialist.

**Completion criteria:**
- Round 2 specialists demonstrably reference Round 1 findings in their reasoning
- Audit log shows round provenance
- Quality Guardian sign-off

---

## Phase 3 — Legal & Contractual Skills + Validation

**Objective:** Build the first complete skill set. Legal & Contractual is the correct starting domain — it has no upstream dependencies, runs in Round 1, and its findings are passed forward to Claims, Schedule, and Governance before they begin.

**Governing standard:** `SKILLS_STANDARDS.md`

**Skill files to build in `skills/legal/`:**
- `contract_assembly.md` — contract document completeness and hierarchy analysis
- `engineer_identification.md` — Engineer role identification and authority mapping
- `notice_and_instruction_compliance.md` — notice and instruction compliance assessment
- `entitlement_basis.md` — contractual entitlement basis identification
- `key_dates_and_securities.md` — key contractual dates and securities assessment

**Prerequisites before authorship begins:**
1. Review and approve `docs/research/legal_domain_research_summary.md` — exists, awaiting Yasser domain review
2. Ingest FIDIC General Conditions for all three books in use in the GCC via `scripts/ingest_reference.py`: Red Book (Construction) 1999 and 2017, Yellow Book (Plant & Design-Build) 1999 and 2017, Silver Book (EPC/Turnkey) 1999 and 2017 — HIGH deferred item from Phase C1, must complete before production use
3. Define five validation scenarios per `SKILLS_STANDARDS.md` Section 7 — one per skill file

**Validation gate — before Phase 4 starts:**
- Test against minimum five scenarios per `SKILLS_STANDARDS.md` Section 7
- Quality Guardian sign-off

---

## Phase 4 — Commercial & Financial Skills + Validation

**Objective:** Build Commercial & Financial skill set. Commercial runs in Round 1 in parallel with Legal. Its findings (contract sum, certified amounts, variation register, LD exposure) are passed to Claims in Round 2.

**Governing standard:** `SKILLS_STANDARDS.md`

**Skill files to build in `skills/commercial/`:** Defined during Phase 4 authorship session per `SKILLS_STANDARDS.md` Section 4. Domain research summary must be produced and approved before authorship begins.

**Key skill areas:**
- BOQ measurement and rate application
- Variation valuation methodology under FIDIC Clause 13
- Payment application and IPC assessment under FIDIC Clause 14
- Prolongation cost methodology and recoverable heads of claim
- Liquidated damages calculation and cap
- Final account structure and assessment

**Validation gate — before Phase 5 starts:**
- Test against minimum five scenarios per `SKILLS_STANDARDS.md` Section 7
- Quality Guardian sign-off

---

## Phase 5 — Claims & Disputes Skills + Validation Gate

**Objective:** Build Claims & Disputes skill set. Most forensically critical domain. Has upstream dependencies on both Legal and Commercial. Phases 3 and 4 must be complete before Phase 5 begins.

**Dependency note:** Claims specialist receives Legal (Round 1) and Commercial (Round 1) findings before it runs. A Claims skill file that duplicates Legal or Commercial analysis is a design failure.

**Governing standard:** `SKILLS_STANDARDS.md` — Section 6 contains Claims-specific additional standards.

**Skill files to build in `skills/claims/`:** Defined during Phase 5 authorship session per `SKILLS_STANDARDS.md` Sections 4 and 6. Domain research summary must be produced and approved before authorship begins.

**Key skill areas:**
- Notice compliance assessment — time bar, sufficiency, awareness date calculation
- Entitlement mapping — FIDIC clause to relief type
- Delay analysis methodology identification and assessment — SCL/AACE compliance
- Quantum assessment — heads of claim, methodology, recoverable costs
- Contradiction detection across claims document set
- Forensic credibility signals

**Validation gate — before Phase 6 starts:**
- Test against minimum five real claims scenarios per `SKILLS_STANDARDS.md` Section 7
- Specialist must correctly identify time bar compliance / non-compliance
- Specialist must detect at least one contradiction in a document set containing a known one
- If either fails, refine skill files and retest — do not proceed to Phase 6

---

## Phase 6 — Remaining Three Specialists

**Objective:** Build skill sets for Schedule & Programme, Governance & Compliance, and Technical & Design, one at a time.

**Governing standard:** `SKILLS_STANDARDS.md`

**Sequencing and dependencies:**

| Specialist | Round | Upstream dependency | Key skill areas |
|---|---|---|---|
| Schedule & Programme | Round 2 | Legal (FIDIC Cl. 8, EOT clause, milestones) | Programme validity, delay causation, float, SCL/AACE methodology, as-built vs baseline |
| Governance & Compliance | Round 2 | Legal (Engineer authority, delegation limits) | DOA compliance, approval chain, authority matrix, regulatory requirements |
| Technical & Design | Round 2 | Light — can proceed in parallel with Schedule/Governance | Specification compliance, RFI validity, design change assessment, submittal review |

**Rule:** Each specialist is a new folder in `skills/` and a new `SpecialistConfig` entry — no new agent code.

---

## Phase 7 — Cross-Specialist Contradiction Detection

**Objective:** Upgrade contradiction detection to operate across specialist findings, not just across documents.

**What gets built:**
- `cross_specialist_contradiction_pass()` in `src/agents/contradiction_cross.py` — currently a stub returning an empty list — replaced with real logic
- Post-Round 2 contradiction pass compares findings across all specialists
- Legal date finding checked against Schedule date finding for the same event
- Commercial VO value checked against Claims claimed amount for the same variation
- Cross-specialist contradictions written to `contradiction_flags` with `source = "specialist_conflict"`
- Frontend updated to display specialist-conflict contradictions distinctly from document contradictions

**Completion criteria:**
- At least one known cross-specialist contradiction correctly detected in test scenario
- Quality Guardian sign-off

---

## Phase 8 — Iterative Skill Deepening

**Objective:** Continuous improvement driven by real query failures. No sprint. No completion date.

**Process:**
1. Real user query produces weak or incorrect response
2. Identify which specialist fell short
3. Identify which skill file was missing the knowledge or had wrong guidance
4. Edit the markdown file — no code change required
5. Redeploy
6. Retest

No Claude Code involvement for skill deepening. Domain knowledge encoded in markdown files, refined based on evidence from real queries. All updates logged in `BUILD_LOG.md` per `SKILLS_STANDARDS.md` Section 9.

---

## Governing Rules

1. One phase at a time. No phase starts until the previous is approved.
2. Phase 1 is the highest-risk phase — if the template is wrong, everything built on it is wrong.
3. Phases 3, 4, and 5 each have a validation gate — do not proceed without passing it.
4. Phase 5 (Claims) must not begin until Phases 3 (Legal) and 4 (Commercial) are complete.
5. Quality Guardian reviews every phase before it is marked complete.
6. Skill files are markdown — they can be edited at any time without touching code.
7. The flow layer (agentic loop, tools, round structure) does not change per specialist. Only the skill files change.
8. SkillLoader must never contain a hardcoded list of skill files — it loads all files in the folder dynamically.
9. Adding a new specialist must never require changes to `base_specialist.py` or `tools.py`.
10. Every skill file set must be preceded by a domain research summary approved before authorship begins — per `SKILLS_STANDARDS.md` Section 4.3.
11. Project-specific facts (FIDIC edition, Engineer identity, contract sum, key dates) are never hardcoded into skill files — they are retrieved from the warehouse at query time.

---

## File Structure Reference

```
src/
└── agents/
    ├── base_specialist.py          <- Phase 1: shared agent template (complete)
    ├── tools.py                    <- Phase 1: four shared tools (complete)
    ├── skill_loader.py             <- Phase 1: dynamic markdown loader (complete)
    ├── specialist_config.py        <- Phase 1: per-domain configuration (complete)
    ├── contradiction_cross.py      <- Phase 2: stub — Phase 7 fills logic (complete)
    ├── orchestrator.py             <- Phase 2: multi-round rebuild (complete)
    └── specialists/
        └── __init__.py             <- placeholder; specialist files added per phase

skills/                             <- generic domain knowledge — reusable across all projects
├── legal/                          <- Phase 3
├── commercial/                     <- Phase 4
├── claims/
│   └── README.md                   <- Phase 1 placeholder -> Phase 5 skill files
├── schedule/                       <- Phase 6
├── governance/                     <- Phase 6
└── technical/                      <- Phase 6
```

The warehouse (Supabase pgvector) holds all project-specific evidence (Layer 1) and reference documents (Layer 2). Skills reason over the warehouse. Skills do not store project-specific facts.

---

## Document Control

| Field | Value |
|---|---|
| Owner | C1 Project |
| Version | 1.4 — Phase 3 activated; skill files named; prerequisites stated; stale claims.py removed from file structure; FIDIC scope expanded to Red, Yellow, and Silver Books |
| Updated when | Phase completed or plan revised |
| Location | `docs/AGENT_PLAN.md` |
| Related documents | `docs/SKILLS_STANDARDS.md`, `CLAUDE.md`, `README.md` |
