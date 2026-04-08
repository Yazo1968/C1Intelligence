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

**`docs/C1_GOVERNANCE_REDESIGN.md`** — Active workstream.
Clean-slate governance redesign. Phase 0 (obliteration) is next.
Previous implementation superseded in full.

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

**Query Engine — UNDER REDESIGN (new session)**
The three-tier agentic query engine (Tier 0 router, Tier 1 orchestrators,
Tier 2 SMEs, agentic tool loops) is retired. It produced correct output
but was too slow (3-5 min), too expensive ($3-5/query), and not scalable
to large document sets.

Replacement architecture: single large-context call using Gemini.
- Model: Gemini 2.0 Flash (fast, cheap, 1M token context window)
- Approach: load full document content into context, single inference call,
  structured JSON output
- No retrieval sampling, no tool rounds, no orchestrator chains
- Target: <30 seconds per query, <$0.10 per query
- Gemini client already exists in src/clients.py for embeddings — reuse it

Files to replace in new session:
  src/agents/orchestrator.py — main query pipeline
  src/agents/base_orchestrator.py — agentic loop base class
  src/agents/base_specialist.py — SME base class
  src/agents/domain_router.py — Claude-based domain router
  src/agents/prompts.py — agent system prompts
  src/agents/specialist_config.py — agent config

Files to RETAIN (untouched by query engine redesign):
  src/agents/governance/ — all governance extraction (stays on Claude)
  src/agents/tools.py — tool definitions (may be simplified)
  src/agents/retrieval.py — chunk retrieval (repurposed for doc loading)
  src/agents/audit.py — audit log writing
  src/agents/contradiction.py — contradiction detection
  src/agents/models.py — data models (QueryRequest, QueryResponse, etc.)
  src/agents/skill_loader.py — skill file loader

Skill files (skills/orchestrators/, skills/smes/) — retained as domain
knowledge reference but repurposed as structured analysis instructions
for the single Gemini call, not as agentic directives.

**Governance Feature — COMPLETE, STAYS ON CLAUDE**
Entity extraction and event extraction use Claude (claude-sonnet-4-6).
Do not change governance agents to Gemini.

**Database — 23 migrations applied (001–023)**
All tables intact. Query engine redesign requires no schema changes.
Next migration if needed: 024.

**Gemini SDK in use:**
  from google import genai
  client = genai.Client(api_key=GEMINI_API_KEY)
  Embeddings: gemini-embedding-001 at 3072 dims (locked — do not change)
  Query inference: gemini-2.0-flash-001 (new)

**Current platform HEAD: 906a19b** (last stable before query engine work)
Note: commits after 906a19b (35a4490, 2ef7361, 0ca6213, 906a19b) contain
partial fixes to the old engine — they are on main but the engine itself
is being replaced. New session should read these files but not extend them.

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

**23 migrations applied (001–023):**
- 014: `round_number` in `query_log`
- 015: `SET search_path` on all 5 RPC functions
- 016: HNSW halfvec(3072) indexes on `document_chunks` and `reference_chunks`
- 017: `evidence_records` column on `query_log`; EvidenceRecord schema
- 018: `governance_run_log` table (superseded — dropped in 022)
- 019–021: old governance execution schema (superseded — dropped in 022)
- 022: governance redesign — 8 old tables dropped, 6 new tables created
  (`entity_directory_runs`, `entities`, `entity_discrepancies`,
  `event_log_runs`, `entity_events`, `event_log_questions`)
- 023: `entity_raw_extractions` staging table for two-stage entity extraction

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
