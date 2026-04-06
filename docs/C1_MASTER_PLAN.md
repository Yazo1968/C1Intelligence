# C1 Intelligence — Master Plan

**Version:** 1.0
**Date:** April 2026
**Status:** Active — governing reference for all remaining platform work
**Supersedes:** C1_INTELLIGENCE_GROUNDING_PLAN.md, C1_PHASE2_PLAN.md,
C1_REMAINING_WORK.md (all archived)

---

## Context — Why This Plan Exists

C1 was built with two foundational errors that must be corrected before
the platform can scale to its intended purpose:

**Error 1 — FIDIC-first architecture.**
The agent system prompts in `src/agents/prompts.py` contain hardcoded FIDIC
clause knowledge. The skill files contain FIDIC-specific workflows. The
platform documentation describes C1 as a FIDIC/GCC tool. C1 is not a FIDIC
tool — it is a universal construction intelligence platform that reasons
against whatever standards the user has ingested. A project using NEC4 and
IFRS should work exactly as well as one using FIDIC and PMBOK.

**Error 2 — Knowledge in the wrong layer.**
Standard form knowledge (what a clause says, how a procedure works) belongs
exclusively in the Layer 2b warehouse. Agents retrieve it at query time and
reason against it. It must not be baked into system prompts or skill files,
because that creates a "false confidence" effect: agents think they already
know the answer and skip retrieval. This is the root cause of the "Fresh Milk"
hallucination incident — the agent described a deleted FIDIC clause without
retrieving from Layer 2b because it already had FIDIC knowledge in its
system prompt.

**The correct architecture:**
- `prompts.py` — reasoning frameworks only, no domain-specific standards knowledge
- Skill files — how to analyse, what to retrieve, how to classify, output format
- Layer 2b warehouse — all standard form knowledge, laws, regulations, standards
- Agents retrieve Layer 2b at query time and apply what they find

---

## Platform Identity (Correct Version)

C1 Intelligence is a universal construction project intelligence platform.
It investigates, audits, and produces expert-level findings on any construction
project by reasoning across three evidence layers:

- **Layer 1 — Project:** Contracts of any form, correspondence, notices, claims,
  schedules, payment records, drawings, technical reports
- **Layer 2a — Internal:** Organisation policies, DOA matrices, authority
  frameworks, internal procedures
- **Layer 2b — External:** Standard forms (FIDIC, NEC, JCT, AIA, any other),
  professional standards (PMBOK, IFRS, SCL Protocol, AACE), laws, regulations

The platform's six analysis domains (Legal, Commercial, Financial, Claims,
Schedule, Technical) are universal construction audit disciplines. They are not
FIDIC-specific. They apply to any project regardless of the contract form in use.

---

## Phase 1 — Core Intelligence Fix: Form-Agnostic System Prompts

**Priority:** Critical — this is the highest-impact single change in the platform
**Files:** `src/agents/prompts.py`
**Agent:** Agent Orchestrator
**Prerequisite:** None

### What to change

`prompts.py` contains SPECIALIST_SYSTEM_PROMPTS with hardcoded FIDIC clause
numbers, edition cross-references, and GCC-specific assumptions. These must
be replaced with form-agnostic reasoning frameworks.

**The correct system prompt pattern for each specialist:**

1. State the specialist's role and analytical scope (universal, not FIDIC-specific)
2. Instruct the agent to retrieve the governing contract standard from Layer 2b
   before applying any contractual framework
3. Instruct the agent to retrieve applicable internal policies from Layer 2a
4. Apply retrieved standards — never assumed ones
5. If the governing standard is not in Layer 2b: state what is missing and
   what analysis cannot proceed

**Remove from each prompt:**
- All specific clause numbers (20.1, 14.6, 8.4, etc.)
- All edition-specific cross-references (1999 vs 2017)
- All references to DAB, DAAB, or any FIDIC-specific mechanism
- All GCC market framing

**Replace with:**
Instructions to retrieve the governing contract standard from Layer 2b,
identify the relevant provision, and apply it. The Evidence Declaration block
instruction must be present in every prompt.

**Also update:**
- DOMAIN_ROUTER_SYSTEM_PROMPT: remove "GCC market (UAE, Saudi Arabia, Qatar)"
  — replace with universal construction project scope
- `_SPECIALIST_RULES` Rule 6: remove "Reference FIDIC sub-clause numbers" —
  replace with "Reference the specific provision from the governing standard
  retrieved from Layer 2b"

### Output
- Rebuilt `src/agents/prompts.py`
- Commit: `fix: prompts.py — form-agnostic system prompts, remove hardcoded FIDIC`

---

## Phase 2 — Skill Authoring Infrastructure: Rebuild c1-skill-authoring

**Priority:** High — governs all subsequent skill file work
**Files:** `skills/c1-skill-authoring/` (5 files)
**Agent:** Agent Orchestrator (using skill-creator tool)
**Prerequisite:** Phase 1 complete

### What to build

A correctly structured `c1-skill-authoring` skill with three-layer warehouse
model throughout. No FIDIC-specific content. No hardcoded standards knowledge.

**Structure:**
```
skills/c1-skill-authoring/
├── SKILL.md                          — workflow, checklist, reference file pointers
└── references/
    ├── grounding_protocol.md         — Evidence Declaration rules, CANNOT CONFIRM,
    │                                   confidence caps — form-agnostic
    ├── warehouse_retrieval.md        — three-layer model, what each layer contains,
    │                                   retrieval patterns, Layer 2b examples
    ├── output_formats.md             — universal output templates
    └── validation_scenarios.md       — form-agnostic test scenarios
```

**Key content requirements:**

`warehouse_retrieval.md` replaces the incorrectly built `fidic_framework.md`.
It describes:
- Layer 1 (project documents) — what they are, how to retrieve
- Layer 2a (internal standards) — what they are, how to retrieve
- Layer 2b (external standards) — what they are, examples only (FIDIC is one
  example among many), how to retrieve
- The retrieval-first reasoning pattern
- What to do when a required standard is not in the warehouse

`grounding_protocol.md` must be form-agnostic throughout. Replace every
instance of "FIDIC clause" with "standard form provision from Layer 2b."

`validation_scenarios.md` must be form-agnostic. Tests verify the retrieval
behaviour, not FIDIC-specific knowledge.

### Output
- 5 files under `skills/c1-skill-authoring/`
- Commit: `feat: rebuild c1-skill-authoring — three-layer warehouse, form-agnostic`

---

## Phase 3 — Standards Document: Lightweight SKILLS_STANDARDS.md

**Priority:** Medium
**Files:** `docs/SKILLS_STANDARDS.md`
**Agent:** Agent Orchestrator
**Prerequisite:** Phase 2 complete

### What to change

The current `docs/SKILLS_STANDARDS.md` v1.4 is 509 lines. It contains:
- Section 5.3: FIDIC edition-specific comparison table — must be removed
- Section 7: Claims domain with FIDIC-specific standards — must be made
  form-agnostic
- Section 6: Warehouse-grounding principles — keep, make authoritative
- Operational instruction content — moves into c1-skill-authoring skill

Convert to a lightweight (max 100 lines) human-readable reference that:
- States the platform's four warehouse-grounding principles (Section 6 content)
- States that operational skill authorship guidance is in `skills/c1-skill-authoring/`
- Removes all FIDIC-specific and edition-specific content

### Output
- Rebuilt `docs/SKILLS_STANDARDS.md` v2.0 (lightweight)
- Commit: `docs: SKILLS_STANDARDS.md v2.0 — lightweight, form-agnostic`

---

## Phase 4 — Skill Files: Rebuild All 20 Files ✅ COMPLETE

**Priority:** High
**Files:** 3 orchestrator directives + 17 SME skill files
**Agent:** Agent Orchestrator (using c1-skill-authoring skill)
**Prerequisite:** Phases 1, 2, 3 complete

### Scope

20 files total across 4 groups:

**Orchestrator directives (3):**
- `skills/orchestrators/legal/directive.md`
- `skills/orchestrators/commercial/directive.md`
- `skills/orchestrators/financial/directive.md`

**Legal SME skills (5):**
- `contract_assembly.md`, `engineer_identification.md`,
  `entitlement_basis.md`, `key_dates_and_securities.md`,
  `notice_and_instruction_compliance.md`

**Claims SME skills (5):**
- `dispute_resolution_procedure.md`, `disruption.md`,
  `eot_quantification.md`, `notice_compliance.md`, `prolongation_cost.md`

**Schedule SME skills (6):**
- `acceleration.md`, `critical_path_analysis.md`, `delay_identification.md`,
  `evm_and_cost_reporting.md`, `programme_assessment.md`, `time_at_large.md`

**Technical SME skills (6):**
- `design_liability.md`, `ncr_management.md`, `rfi_and_submittal_review.md`,
  `site_execution.md`, `specification_compliance.md`,
  `testing_and_commissioning.md`

### What every rebuilt file must contain

1. **Evidence Declaration block** in output format — mandatory first section
2. **Layer 2b retrieval instruction** — before any standard form provision
   is characterised, retrieve it from Layer 2b using `search_chunks`
3. **Layer 2a retrieval instruction** — retrieve applicable internal policies
4. **CANNOT CONFIRM rules** — explicit outcomes for when retrieval fails
5. **Confidence cap rules** — AMBER when Layer 2b not retrieved; GREY when
   amendment document absent
6. **Form-agnostic analytical steps** — no hardcoded clause numbers, no
   edition-specific assumptions, no contract-form assumptions
7. **Always flag** — includes "governing standard not in Layer 2b" as a
   mandatory flag

### Priority order

1. Orchestrator directives (highest impact — Tier 1)
2. Legal SME skills (most FIDIC-specific in current form)
3. Claims SME skills (depend on Legal)
4. Schedule SME skills
5. Technical SME skills

### Output
- One commit per file after QG PASS
- Commit format: `feat: rebuild [skill name] — evidence declaration, form-agnostic`

---

## Phase 5 — Code Enforcement: EvidenceRecord and Grounding Schemas ✅ COMPLETE

**Priority:** Medium (Phase 4 provides prompt-level guardrails; Phase 5
makes them code-enforced)
**Files:** `src/agents/models.py`, `src/agents/base_specialist.py`,
`src/agents/base_orchestrator.py`, `src/agents/skill_loader.py`,
`src/agents/orchestrator.py`, `src/agents/audit.py`, new migration,
and `grounding_schema.json` files alongside skill files
**Agent:** DB Architect + Agent Orchestrator
**Prerequisite:** Phase 4 complete

### What to build

A runtime validation layer that:
1. Parses the Evidence Declaration block from every agent output
2. Validates it against a schema that defines what retrieval is required
3. Automatically caps confidence when required evidence is missing
4. Persists evidence records to `query_log` for auditability
5. Surfaces grounding gaps in the query response when they occur

Detailed specification: see `docs/C1_INTELLIGENCE_GROUNDING_PLAN.md` —
Tasks 2.1 through 2.9. That plan's technical specification remains valid;
only the context (universal platform, not FIDIC-specific) changes.

---

## Phase 6 — Product Features

**Priority:** Product decision required for each
**Prerequisite:** Phases 1–5 complete (or running in parallel for features
that do not interact with the intelligence layer)

| Item | Scope | Notes |
|---|---|---|
| Compliance feature | Complete ✅ | Migration 018 ✅ e4c0564. 6 Compliance SME skills ✅ (rebuilt cb2878d — correct SKILL.md structure and Evidence Declaration format). Legal & Compliance orchestrator ✅ (rebuilt 5aa10b5 — correct mandatory structure). Commercial + Financial directives ✅. engineer_identification.md retired ✅. 5 API endpoints ✅ 18448da. Governance frontend ✅ 3f64c9b. grounding_schema.json for Compliance SME ✅ b763f0a. |
| Approval workflows | Large | Workflow engine, notifications, DOA enforcement |
| Five user roles and authority matrix | Large | Read/write/query permissions per role |
| Document control system integration | Large | Aconex, Docutrack ingestion pipeline |

---

## Files Affected by This Plan

| File | Current State | Action |
|---|---|---|
| `CLAUDE.md` | v0.3 — FIDIC/GCC identity | Rewritten v1.0 ✅ this session |
| `README.md` | v0.3 — FIDIC/GCC references | Updated v1.0 ✅ this session |
| `src/agents/prompts.py` | FIDIC hardcoded | Phase 1 ✅ 69966661 |
| `skills/c1-skill-authoring/` | Wrong — FIDIC-specific | Phase 2 ✅ this session |
| `docs/SKILLS_STANDARDS.md` | 509 lines, FIDIC-specific | Phase 3 ✅ this session |
| `skills/orchestrators/legal/directive.md` | FIDIC-specific | Phase 4 ✅ 7514a85 |
| `skills/orchestrators/commercial/directive.md` | FIDIC-specific | Phase 4 ✅ 00f62b6 |
| `skills/orchestrators/financial/directive.md` | FIDIC-specific | Phase 4 ✅ bf10e37 |
| `skills/smes/legal/contract_assembly.md` | FIDIC-specific | Phase 4 ✅ 2889d9d |
| `skills/smes/legal/engineer_identification.md` | FIDIC-specific | Phase 4 ✅ 62982ea |
| `skills/smes/legal/entitlement_basis.md` | FIDIC-specific | Phase 4 ✅ 90e10c5 |
| `skills/smes/legal/key_dates_and_securities.md` | FIDIC-specific | Phase 4 ✅ d002235 |
| `skills/smes/legal/notice_and_instruction_compliance.md` | FIDIC-specific | Phase 4 ✅ a732250 |
| `skills/smes/claims/dispute_resolution_procedure.md` | FIDIC-specific | Phase 4 ✅ af46b5b |
| `skills/smes/claims/disruption.md` | FIDIC-specific | Phase 4 ✅ fd800e2 |
| `skills/smes/claims/eot_quantification.md` | FIDIC-specific | Phase 4 ✅ 8351df6 |
| `skills/smes/claims/notice_compliance.md` | FIDIC-specific | Phase 4 ✅ 4f1f0f8 |
| `skills/smes/claims/prolongation_cost.md` | FIDIC-specific | Phase 4 ✅ 93c6b77 |
| `skills/smes/schedule/acceleration.md` | FIDIC-specific | Phase 4 ✅ 99ca558 |
| `skills/smes/schedule/critical_path_analysis.md` | FIDIC-specific | Phase 4 ✅ b054492 |
| `skills/smes/schedule/delay_identification.md` | FIDIC-specific | Phase 4 ✅ 2243719 |
| `skills/smes/schedule/evm_and_cost_reporting.md` | FIDIC-specific | Phase 4 ✅ fad4065 |
| `skills/smes/schedule/programme_assessment.md` | FIDIC-specific | Phase 4 ✅ 8452a1d |
| `skills/smes/schedule/time_at_large.md` | FIDIC-specific | Phase 4 ✅ d1b7bb1 |
| `skills/smes/technical/design_liability.md` | FIDIC-specific | Phase 4 ✅ d36b660 |
| `skills/smes/technical/ncr_management.md` | FIDIC-specific | Phase 4 ✅ ceb0327 |
| `skills/smes/technical/rfi_and_submittal_review.md` | FIDIC-specific | Phase 4 ✅ 643ddf1 |
| `skills/smes/technical/site_execution.md` | FIDIC-specific | Phase 4 ✅ d38e42e |
| `skills/smes/technical/specification_compliance.md` | FIDIC-specific | Phase 4 ✅ 83240db |
| `skills/smes/technical/testing_and_commissioning.md` | FIDIC-specific | Phase 4 ✅ 5fd82b4 |
| `src/agents/models.py` | Missing EvidenceRecord | Phase 5 ✅ d1252e6 |
| `src/agents/base_specialist.py` | No validation | Phase 5 ✅ 0e69fc6 |
| `src/agents/base_orchestrator.py` | No validation | Phase 5 ✅ 41b9c84 |
| `src/agents/skill_loader.py` | No schema loading | Phase 5 ✅ 1aafbcd |
| New `grounding_schema.json` files | Do not exist | Phase 5 ✅ dcef002 |
| `src/agents/orchestrator.py` | No evidence surfacing | Phase 5 ✅ 33d3e08 |
| `src/agents/audit.py` | No evidence_records column | Phase 5 ✅ d487ffb |
| Migration 017 | Does not exist | Phase 5 ✅ d487ffb (applied) |
| `docs/C1_REMAINING_WORK.md` | Outdated | Superseded by this plan |
| `docs/C1_INTELLIGENCE_GROUNDING_PLAN.md` | Symptom-level | Superseded, move to archive |
| `docs/C1_PHASE2_PLAN.md` | Outdated | Superseded, move to archive |

---

## Session Protocol

Each phase executes in a dedicated session or set of sessions.
At the start of every session:
1. Read `CLAUDE.md` — the operational contract
2. Read this plan — identify the current phase and next task
3. Confirm current state before any action

At the close of every session:
1. One task per commit, QG PASS verified
2. Update this plan — mark completed tasks
3. Update `BUILD_LOG.md`

---

## Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Date | April 2026 |
| Supersedes | C1_INTELLIGENCE_GROUNDING_PLAN.md, C1_PHASE2_PLAN.md, C1_REMAINING_WORK.md |

---

## Enhancement Plan — COMPLETE

**Status:** Complete
**Document:** `docs/C1_Orchestrators_and_SMEs_enhancement.md` v2.3
**Completed:** April 2026

29 tasks across 4 parts — all complete and verified.

| Part | Scope | Tasks | Status |
|---|---|---|---|
| A | Expert examination remediation — 8 issues | 11 | Complete ✅ |
| B | Claims SME dissolution + backend code changes | 9 | Complete ✅ |
| C | Delay assessment quality improvements | 2 | Complete ✅ |
| D | Financial & Accounting SME — 3 new skills | 5 | Complete ✅ |
| Governing docs | CLAUDE.md + C1_MASTER_PLAN.md | 2 | Complete ✅ |

### End state

**Skill file inventory (30 files):**
- 3 orchestrator directives + 1 synthesis directive
- Legal & Contractual SME: 7 skills
- Delay and Cost Analytics SME: 9 skills
- Technical & Construction SME: 6 skills (unchanged)
- Compliance SME: 6 skills (unchanged)
- Financial & Accounting SME: 3 skills (new domain)

**Backend domain routing (5 router-accessible domains):**
`legal_contractual→legal` | `commercial_financial→commercial` |
`financial_reporting→financial` | `schedule_programme→schedule` |
`technical_construction→technical`
`claims_disputes` removed from ALL_DOMAINS and DOMAIN_TO_CONFIG_KEY.
`financial_sme` loaded by Financial orchestrator delegation only.

**Part A — 11 tasks (commits):**
d9c277e A1.1 notice_and_instruction_compliance — retired reference fixed
a35021f A1.2 entitlement_basis — retired reference fixed
0c5ce16 A1.3 key_dates_and_securities — retired reference fixed
92c37b5 A1.4 programme_assessment — retired reference fixed
2555457 A3.1 commercial directive — missing H1 title added
cbb7797 A4.1 claims README — stale placeholder removed
f9df792 A2.1 notice compliance skill boundary clarified in both files
1240d85 A7.1 governance_establishment — statutory_authority_mapping invoked
2a5739d A8.1 evm_and_cost_reporting — fallback path added
a25d1e6 A6.1 all 27 SME files — confidence scale added to output sections
81e6ecf A5.1 synthesis_directive.md — new file created

**Part B — 9 tasks (Broken Window session):**
0f4ac18 B1 schedule SME domain labels updated
9d02c69 B2 eot_quantification, prolongation_cost, disruption moved to schedule
3972b43 B3 notice_compliance, dispute_resolution_procedure moved to legal
3723c51 B4 claims directory retired
8d15f28 B_schema claims schema deleted, schedule schema updated
b409b66 B5 all 3 orchestrator directives updated
489cf65 B_code1 specialist_config — claims entry removed
41fb74d B_code2 prompts.py — claims_disputes removed
c340677 B_code3 orchestrator.py — claims routing removed

**Part C — 2 tasks:**
7e2a0ef C1 eot_quantification — methodology appropriateness + As-Built Critical Path
00d4cfc C2 delay_identification — forensic four-way classification added

**Part D — 5 tasks:**
4b3ab3d D1 cost_control_assessment.md — new Financial & Accounting SME skill
f09ae3d D2 multi_contract_account_reconciliation.md — new skill
3a31ab8 D3 financial_reporting_compliance.md — new skill
a2105b2 D4 grounding_schema.json — Financial & Accounting SME domain
f1520bb D5 specialist_config + financial directive — code wiring

**Known backlog item:**
`skill_loader._generate_project_context()` contains a FIDIC-specific
query against the `contracts` table (`fidic_edition` column). Pre-existing
form-specific reference in form-agnostic code. Does not affect the
Enhancement Plan. Must be resolved before C1 is used on non-FIDIC projects.

---

## Aggregation Integrity Plan v2.0 — Complete

**Status:** Complete
**Document:** `docs/C1_AGGREGATION_INTEGRITY_PLAN_v2.md`

20 tasks across 6 phases. All verification is deterministic — zero additional
LLM calls. No new agent frameworks. No new API endpoints. No database
migrations. No frontend changes.

End state: routing coverage is verified against retrieved chunk content;
SME invocations are traced via tools_called; raw SME outputs are preserved
before synthesis; CANNOT CONFIRM items are consolidated from
evidence_record; every response carries a Consolidated Evidence Map built
from system-recorded data, not agent self-reports.

Research basis: MAST NeurIPS 2025, AgentAuditor Feb 2026, TRiSM Mar 2026.
Design principle: verification must read what the system recorded, not what
agents say they did.

### Commits

Phase S:  7ff3d0f, 96526af, d4d050f
Phase 1:  20254fc, 0e97785
Phase 2:  445fe05, 59735e0
Phase 3:  1da9344, 8362368
Phase 4:  daca8d9, 8c6893b, b7aeea6
Phase 5:  5e0de3b, 51f5023
Phase 6:  18e29c7 (+ 6.2 and 6.3 commits to follow)

---

## Governance Authority Log — Active Workstream

**Status:** Design approved — ready for execution
**Design document:** `docs/C1_GOVERNANCE_AUTHORITY_LOG_DESIGN.md`
**Migration 021:** Applied — five new tables (party_identities, party_roles,
authority_events, assumption_register, reconciliation_questions).
Prototype tables governance_parties and governance_events dropped.

**Build sequence (9 phases):**
Phase 0: Housekeeping — dead code removal ✅ this session
Phase 1: Migration 021 ✅ applied directly via Supabase MCP
Phase 2: governance_runner.py Phase 1 rewrite — next session
Phase 3: Reconciliation interview backend — next session
Phase 4: Reconciliation interview frontend — next session
Phase 5: governance_runner.py Phase 2 rewrite — next session
Phase 6: Compliance agent integration — next session
Phase 7: skill_loader rewrite — next session
Phase 8: Frontend authority log display — next session
Phase 9: Governing documents — next session

**Prep work completed this session:**
- Migration 021 applied
- docs archived: C1_AGGREGATION_INTEGRITY_PLAN_v2.md,
  C1_GOVERNANCE_EXECUTION_PLAN.md, C1_Orchestrators_and_SMEs_enhancement.md
- Dead code removed: src/agents/specialists/, Procfile, risk_mode parameter
- Active docs: C1_MASTER_PLAN.md, C1_GOVERNANCE_AUTHORITY_LOG_DESIGN.md
