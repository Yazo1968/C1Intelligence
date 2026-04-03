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

## Phase 4 — Skill Files: Rebuild All 20 Files

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

## Phase 5 — Code Enforcement: EvidenceRecord and Grounding Schemas

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
| Party ID resolution | Medium | Requires parties management API |
| Approval workflows | Large | Workflow engine, notifications, DOA enforcement |
| Five user roles and authority matrix | Large | Read/write/query permissions per role |
| Document control system integration | Large | Aconex, Docutrack ingestion pipeline |

---

## Files Affected by This Plan

| File | Current State | Action |
|---|---|---|
| `CLAUDE.md` | v0.3 — FIDIC/GCC identity | Rewritten v1.0 ✅ this session |
| `README.md` | v0.3 — FIDIC/GCC references | Updated v1.0 ✅ this session |
| `src/agents/prompts.py` | FIDIC hardcoded | Phase 1 |
| `skills/c1-skill-authoring/` | Wrong — FIDIC-specific | Phase 2 ✅ this session |
| `docs/SKILLS_STANDARDS.md` | 509 lines, FIDIC-specific | Phase 3 ✅ this session |
| All 20 skill files | FIDIC-specific | Phase 4 |
| `src/agents/models.py` | Missing EvidenceRecord | Phase 5 |
| `src/agents/base_specialist.py` | No validation | Phase 5 |
| `src/agents/base_orchestrator.py` | No validation | Phase 5 |
| `src/agents/skill_loader.py` | No schema loading | Phase 5 |
| New `grounding_schema.json` files | Do not exist | Phase 5 |
| Migration 017 | Does not exist | Phase 5 |
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
