# C1 Intelligence — Claude Code Operational Contract

**Version:** 1.0
**Read at:** Every session start, before any action
**Authority:** This file governs all Claude Code behaviour on this repo

---

## What C1 Is

C1 Intelligence is a **universal construction project intelligence platform**.
It investigates, audits, and produces expert-level findings on any construction
project by reasoning against three layers of evidence:

- **Layer 1 — Project:** The project's own documents — contracts of any form,
  correspondence, notices, claims, schedules, payment records, drawings,
  technical reports
- **Layer 2a — Internal:** The organisation's own policies, DOA matrices,
  authority frameworks, internal procedures and standards
- **Layer 2b — External:** Standard forms of contract (FIDIC, NEC, JCT, AIA,
  or any other), professional standards (PMBOK, IFRS, SCL Protocol, AACE),
  applicable laws and regulations

C1 works with whatever the user has ingested. If the warehouse contains FIDIC
contracts and PMBOK standards, C1 reasons against those. If it contains NEC4
and IFRS, C1 reasons against those. The platform is not a FIDIC tool, a GCC
tool, or a tool for any specific contract form. It is a construction
intelligence platform that applies the standards and frameworks present in
the warehouse to the project documents present in the warehouse.

---

## Core Intelligence Principle

**Agents reason from retrieved evidence only.**

Every factual claim in an agent's output must trace to a specific retrieved
document from one of the three warehouse layers. If a provision, clause, or
standard was not retrieved, the correct output is CANNOT CONFIRM — never a
characterisation drawn from training knowledge.

This principle applies to all agents at all tiers. It is not negotiable.

---

## The Grounding Protocol

When an agent encounters a clause deletion, amendment, or reference in a
Layer 1 project document:

1. Retrieve the governing provision from Layer 2b (whatever standard form
   is in the warehouse) using `search_chunks`
2. Retrieve the Layer 1 project-specific position (Particular Conditions
   or equivalent amendment document)
3. Apply the Layer 1 position — not the Layer 2b default
4. If Layer 2b retrieval returns no result: state CANNOT CONFIRM —
   STANDARD FORM NOT RETRIEVED. Do not characterise from training knowledge.
5. If Layer 1 amendment document not retrieved: state CANNOT CONFIRM —
   AMENDMENT POSITION UNKNOWN

Every agent output must include an Evidence Declaration block as its first
section. See `skills/c1-skill-authoring/references/grounding_protocol.md`.

---

## Working Model

**Yasser Darweesh** — Product owner, domain expert (~30 years construction),
non-technical. All decisions require his approval. He does not write code.

**Claude (chat session)** — Strategic partner. Reads governing documents,
makes decisions, writes skill files, produces exact Claude Code prompts ready
to paste. Verifies every output independently via GitHub API and Supabase MCP
before confirming complete.

**Claude Code** — Execution agent. Implements instructions. One task per
commit. Every task committed and pushed immediately after Quality Guardian PASS.

**Five agents:** DB Architect, Ingestion Engineer, Agent Orchestrator,
API Engineer, Quality Guardian.

**One task per commit. Push immediately after QG PASS. No batching.**

---

## Active Plans

**`docs/C1_MASTER_PLAN.md`** — The single governing plan for all remaining
platform work. Read this to understand what is in progress and what comes next.
All previous plan documents are superseded.

---

## Repository and Infrastructure

**Repo:** `github.com/Yazo1968/C1Intelligence` (main branch)
**Supabase:** `bkkujtvhdbroieffhfok` (EU West 1)
**Frontend:** `https://c1intelligence.vercel.app`
**Backend:** `https://web-production-6f2c4.up.railway.app`

**GitHub verification:** Always use `api.github.com/repos/Yazo1968/C1Intelligence/contents/{path}`
Never use `raw.githubusercontent.com` — CDN-cached, can serve stale content.

**Supabase verification:** `execute_sql` against `information_schema` for schema
state. `list_migrations` for applied migrations.

---

## Architecture

**Three-tier agents:**
- Tier 0: Main orchestrator (router)
- Tier 1: Legal, Commercial, Financial orchestrators (BaseOrchestrator,
  directive files in `skills/orchestrators/`)
- Tier 2: Schedule & Programme, Technical, Compliance, Financial &
  Accounting SMEs (BaseSpecialist, skill files in `skills/smes/`)

**Skill authoring:** All skill files authored using `skills/c1-skill-authoring/`.
Read this skill before building or rebuilding any file under `skills/`.

**Skill files:** 3 orchestrator directives + 1 synthesis directive
+ 26 SME skill files = 30 files total.

**Aggregation Integrity Layer (v2.0 — deterministic):**
Routing coverage check (chunk-domain keyword alignment — deterministic, no LLM). SME invocation trace (tools_called records invoke_sme:{domain} — deterministic). Raw SME output preservation (captured in agentic loop before synthesis). Evidence Auditor (run_evidence_audit() — zero API calls, reads only pre-recorded deterministic data). Consolidated Evidence Map in every response (built from sources_used, tools_called, raw_sme_outputs, and evidence_record — not from agent self-reporting).
Design principle: every integrity check reads deterministic system state. No integrity layer asks an agent to audit itself.

**Governance Authority Log (three-level model):**
Level 1 — party_identities: legal identity register, one record per legal
entity, party_category taxonomy (27 categories), is_internal flag.
Level 2 — party_roles: one record per role per party, multi-role per party
supported, appointment_status (proposed/pending/executed).
Level 3 — authority_events: chronological authority event log, 10 event
types, initiated_by and authorised_by actor fields, missing_action for
pending/proposed events.
Supporting tables: assumption_register (user declarations with provenance),
reconciliation_questions (interview record).
get_party_authority() tool: deterministic, zero LLM calls, reads
authority_events chronologically to return a party's authority position
at any given date. Called by Compliance SME before any authority assessment.

**Domains:**
- Legal & Contractual SME: 7 skills (contract_assembly,
  entitlement_basis, key_dates_and_securities,
  notice_and_instruction_compliance, notice_compliance,
  dispute_resolution_procedure, and a seventh skill as applicable)
- Schedule & Programme SME: 9 skills (acceleration,
  critical_path_analysis, delay_identification,
  evm_and_cost_reporting, programme_assessment, time_at_large,
  eot_quantification, prolongation_cost, disruption)
- Technical & Construction SME: 6 skills (unchanged)
- Compliance SME: 6 skills (unchanged)
- Financial & Accounting SME: 3 skills (cost_control_assessment,
  multi_contract_account_reconciliation,
  financial_reporting_compliance)

Claims SME domain dissolved — 3 analytical skills moved to Delay
and Cost Analytics SME; 2 procedural skills moved to Legal SME.
synthesis_directive.md governs multi-orchestrator query assembly.
engineer_identification.md retired.
All files require the Evidence Declaration block in their output format.
Orchestrator FLAGS follow ISO 31000:2018 risk register format (nine-field
entries: Description, Cause, Consequence, Likelihood, Inherent Rating,
Existing Controls, Treatment, Residual Rating, Status). Risk report toggle
removed — risk output is built into every orchestrator response.

---

## Locked Technical Decisions — Never Change Without Explicit Instruction

- Docling lazy import only; `opencv-python-headless==4.13.0.92` pinned
- tiktoken 450-token chunks, 0.75 classification threshold
- Gemini embeddings 3072 dims
- HNSW indexes via `halfvec(3072)` cast (Migration 016)
- Railway Dockerfile builder; `sh -c 'uvicorn src.api.main:app --host 0.0.0.0 --port $PORT'`
- Railway Pro plan required
- Vercel Vite/React (NOT Next.js); root dir: `frontend/`
- Frontend is Vite/React — NOT Next.js. Never add "use client" directives. Never use Next.js APIs, routing, or conventions.
- CORS locked to `https://c1intelligence.vercel.app`
- `claude-sonnet-4-6` — no LangChain, no LangGraph, no LlamaIndex
- `DOMAIN_TO_CONFIG_KEY`: `legal_contractual→legal`, `commercial_financial→commercial`,
  `financial_reporting→financial`, `schedule_programme→schedule`,
  `technical_design→technical`
  Financial & Accounting SME (`financial_sme`) is loaded by Financial
  orchestrator delegation — not router-accessible directly.

---

## Database State

**21 migrations applied (001–021):**
- 014: `round_number` in `query_log`
- 015: `SET search_path` on all 5 RPC functions
- 016: HNSW halfvec(3072) indexes on `document_chunks` and `reference_chunks`
- 017: `evidence_records` column on `query_log`; EvidenceRecord schema enforcement
- 018: `governance_run_log` table (retained from prototype)
- 021: `party_identities`, `party_roles`, `authority_events`,
  `assumption_register`, `reconciliation_questions` tables created.
  Prototype tables `governance_parties` and `governance_events` dropped.

**18 tables** including `query_jobs`, `reference_documents` (with `layer_type`
2a/2b + `jurisdiction` columns), `contradiction_flags`, `governance_run_log`,
`party_identities`, `party_roles`, `authority_events`, `assumption_register`,
`reconciliation_questions`.

**4 RPC functions:** `search_chunks_semantic`, `search_chunks_fulltext`,
`search_chunks_reference_semantic`, `search_chunks_reference_fulltext`
(last two have `p_layer_type` + `p_jurisdiction` filters).

**Layer 2b currently ingested:** 6 FIDIC books (1,917 chunks, tagged
`2b/international`). More external references to be ingested as needed.

---

## Session Close Protocol

Every session closes with:
1. One task per commit — no batching
2. QG PASS confirmed by strategic partner (Claude chat) via GitHub API + Supabase MCP
3. `BUILD_LOG.md` updated with full completion entry
4. `docs/C1_MASTER_PLAN.md` updated if any phase/task status changed
5. `CLAUDE.md` updated if any locked decision changed

---

## Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Date | April 2026 |
| Supersedes | CLAUDE.md v0.3 |
