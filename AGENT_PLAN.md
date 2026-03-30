# C1 — Agent Enhancement Plan
## From Stateless Specialists to True Domain Agents

**Version:** 1.1
**Status:** Active — Reference Document
**Last Updated:** March 2026

---

## Context

C1's six domain specialists were built in v1 as stateless Claude API calls — each receives retrieved document chunks, reasons, and returns findings. This plan upgrades them to true agents with tools, multi-round orchestration, and domain skill files.

**The principle governing this plan:**
- The flow (agentic loop, tool set, round structure) is the same for all six specialists
- The domain knowledge (skill files) is what differs between specialists
- Skill files are markdown — they can be deepened at any time without touching code

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

### Principle 3 — Skills and playbooks are separate layers

**Skills** (`skills/{domain}/`) encode generic construction domain knowledge. They are reusable across every project on the platform. A FIDIC notices skill file applies equally to a UAE project and a Qatar project. Skills are maintained by the platform owner and improve over time through Phase 6 iterative deepening.

**Playbooks** (`playbooks/{project_id}.md`) encode project-specific configuration. One file per project. A playbook contains: FIDIC edition governing this contract (1999 or 2017), jurisdiction, identified Engineer / PMC / Supervision Consultant, contract sum, project-specific escalation triggers, and any deviations from standard FIDIC that the contracts team has flagged.

At query time, the `SkillLoader` loads both — the generic skill files for the relevant domain AND the project playbook. The specialist reasons across both layers.

Changing a skill file improves every project immediately on next deploy. Changing a playbook file affects only that project. Neither change touches code.

---

## Architecture Target

```
Orchestrator
    ↓
Round 1: Legal + Commercial
    ↓ findings passed forward
Round 2: Claims + Schedule + Technical + Governance
    ↓ (receive Round 1 findings as context)
Cross-Specialist Contradiction Pass
    ↓
Synthesis → Confidence → Audit Log → Response
```

**Each specialist runs as a true agent:**
- Receives retrieved chunks + query + (Round 2 only) Round 1 findings
- Assesses whether retrieved context is sufficient
- Calls tools if more information is needed
- Reasons and returns structured findings
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
| 1 | Agent Template | ✅ Complete |
| 2 | Multi-Round Orchestrator | ✅ Complete |
| 3 | Claims & Disputes Skills + Validation | ⬜ Not Started |
| 4 | Remaining Five Specialists | ⬜ Not Started |
| 5 | Cross-Specialist Contradiction Detection | ⬜ Not Started |
| 6 | Iterative Skill Deepening | ⬜ Ongoing — No Completion Date |

---

## Phase 1 — Agent Template

**Objective:** Build the reusable architecture all six specialists will share. Get this right before anything else moves.

**What gets built:**
- `BaseSpecialist` class — agentic loop: assess → tool call if needed → reason → return
- Four shared tools: `search_chunks`, `get_document`, `get_contradictions`, `get_related_documents`
- `SkillLoader` — dynamically loads all markdown files from `skills/{domain}/` and `playbooks/{project_id}.md` into the system prompt at runtime. No hardcoded filenames.
- `SpecialistConfig` — per-specialist configuration: domain name, round assignment, max rounds
- One stub specialist: Claims & Disputes — wired to template, minimal skill content, validates architecture only

**What does NOT get built:** Any other specialist. Real skill depth. Orchestrator changes.

**Completion criteria:**
- Stub Claims specialist calls tools correctly and returns structured findings
- SkillLoader dynamically loads all files in the folder — confirmed by adding and removing a test file without any code change
- Project playbook is loaded alongside domain skills — confirmed by checking system prompt composition
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

## Phase 3 — Claims & Disputes Skills + Validation Gate

**Objective:** Build the first complete skill set. Validate before proceeding. This is the most critical phase.

**Skill files to build in `skills/claims/`:**

| File | Content |
|---|---|
| `FIDIC_notices.md` | Valid notice structure, 28-day time bar, awareness date calculation, notice sufficiency, 1999 vs 2017 differences |
| `delay_analysis.md` | Methodology identification, critical path assessment, concurrent delay signals, contemporaneous record requirements |
| `entitlement_matrix.md` | FIDIC clause to entitlement mapping, required evidence per clause, common entitlement failures |
| `contradiction_patterns.md` | High-risk field pairs in claims documents, what to flag, why it matters forensically |
| `forensic_signals.md` | What tells an experienced claims consultant something is wrong: missing notices, date gaps, inconsistent durations |

**Validation gate — before Phase 4 starts:**
- Test against minimum five real claims scenarios
- Specialist must correctly identify time bar compliance / non-compliance
- Specialist must detect at least one contradiction in a document set containing a known one
- If either fails, refine skill files and retest — do not proceed to Phase 4

---

## Phase 4 — Remaining Five Specialists

**Objective:** Replicate the validated skill structure across remaining specialists, one at a time.

**Sequence and focus areas:**

| Specialist | Key Skill Areas |
|---|---|
| Legal & Contractual | Contract hierarchy, notice obligations, governing law, Engineer role identification, entitlement basis |
| Commercial & Financial | BOQ rate application, variation valuation methodology, payment certificate analysis, LD calculation, final account |
| Schedule & Programme | Programme validity assessment, delay causation, float analysis, baseline vs as-built, SCL/AACE methodology signals |
| Governance & Compliance | DOA compliance, approval chain verification, authority matrix adherence, regulatory requirements |
| Technical & Design | Specification compliance, RFI validity and response adequacy, design change assessment, submittal review |

**Rule:** Each specialist follows the same pattern — build shallow skills, test against real documents, refine if needed, mark complete, move to next. Each new specialist is a new folder in `skills/` and a new `SpecialistConfig` entry — no new agent code.

---

## Phase 5 — Cross-Specialist Contradiction Detection

**Objective:** Upgrade contradiction detection to operate across specialist findings, not just across documents.

**What gets built:**
- Post-Round 2 contradiction pass compares findings across all specialists
- Legal date finding checked against Schedule date finding for the same event
- Commercial VO value checked against Claims claimed amount for the same variation
- Cross-specialist contradictions written to `contradiction_flags` with `source = "specialist_conflict"`
- Frontend updated to display specialist-conflict contradictions distinctly from document contradictions

**Completion criteria:**
- At least one known cross-specialist contradiction correctly detected in test scenario
- Quality Guardian sign-off

---

## Phase 6 — Iterative Skill Deepening

**Objective:** Continuous improvement driven by real query failures. No sprint. No completion date.

**Process:**
1. Real user query produces weak or incorrect response
2. Identify which specialist fell short
3. Identify which skill file was missing the knowledge or had wrong guidance
4. Edit the markdown file — no code change required
5. Redeploy
6. Retest

**This is where domain expertise becomes the product's competitive moat.**

No Claude Code involvement for skill deepening. No engineering. Domain knowledge encoded in markdown files, continuously refined based on evidence from real queries.

---

## Governing Rules

1. One phase at a time. No phase starts until the previous is approved.
2. Phase 1 is the highest-risk phase — if the template is wrong, everything built on it is wrong.
3. Phase 3 has a hard validation gate — do not proceed to Phase 4 without passing it.
4. Quality Guardian reviews every phase before it is marked complete.
5. Skill files are markdown — they can be edited at any time without touching code.
6. The flow layer (agentic loop, tools, round structure) does not change per specialist. Only the skill files change.
7. SkillLoader must never contain a hardcoded list of skill files — it loads all files in the folder dynamically.
8. Adding a new specialist must never require changes to `base_specialist.py` or `tools.py`.

---

## File Structure Reference

```
src/
└── agents/
    ├── base_specialist.py      ← Phase 1: shared agent template
    ├── tools.py                ← Phase 1: four shared tools
    ├── skill_loader.py         ← Phase 1: dynamic markdown loader
    ├── specialist_config.py    ← Phase 1: per-domain configuration
    ├── orchestrator.py         ← Phase 2: multi-round rebuild
    └── specialists/
        ├── claims.py           ← Phase 1 stub → Phase 3 complete
        ├── legal.py            ← Phase 4
        ├── commercial.py       ← Phase 4
        ├── schedule.py         ← Phase 4
        ├── governance.py       ← Phase 4
        └── technical.py        ← Phase 4

skills/                                       ← generic domain knowledge — reusable across all projects
├── claims/
│   ├── FIDIC_notices.md                      ← Phase 3
│   ├── delay_analysis.md                     ← Phase 3
│   ├── entitlement_matrix.md                 ← Phase 3
│   ├── contradiction_patterns.md             ← Phase 3
│   ├── forensic_signals.md                   ← Phase 3
│   └── [any future file]                     ← drop file here, no code change
├── legal/                                    ← Phase 4
├── commercial/                               ← Phase 4
├── schedule/                                 ← Phase 4
├── governance/                               ← Phase 4
└── technical/                                ← Phase 4

playbooks/                                    ← project-specific configuration — one file per project
└── {project_id}.md                           ← FIDIC edition, jurisdiction, Engineer, contract-specific positions
```

---

## Document Control

| Field | Value |
|---|---|
| Owner | C1 Project |
| Updated when | Phase completed or plan revised |
| Location | Repo root — `AGENT_PLAN.md` |
