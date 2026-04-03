# CLAUDE.md — Behavioural Contract for Claude Code

This file governs how Claude Code works on the C1 project.
Read it fully before doing anything in any session. Follow it in every prompt.

---

## The Single Most Important Rule

**One task at a time. Complete it fully. Report clearly. Wait for Yasser's approval before moving to the next.**

Do not anticipate. Do not build ahead. Do not assume scope expands beyond what was stated.
When a task is complete, say so clearly, show what changed, and wait.

---

## What You Are Building

C1 is a forensic construction documentation intelligence platform for the GCC market (UAE, Saudi Arabia, Qatar). It ingests project documents, reasons across them using a three-tier multi-agent architecture, detects contradictions between documents, and produces forensic-grade responses with full source attribution and confidence classification.

Read `README.md` fully before writing any code in any session. It is the single source of truth for what C1 is, what it does, and how it is structured.

---

## Governing Documents — Read These First

Every session, before writing any code, confirm which governing document applies to the current task and read the relevant section:

| Document | Purpose | When to read |
|---|---|---|
| `README.md` | Platform architecture, warehouse design, API endpoints | Every session |
| `CLAUDE.md` | This file — behavioural contract | Every session |
| `docs/SKILLS_STANDARDS.md` | Skill file authorship standards — governs all skill file content | When working on skill files |
| `docs/C1_REMAINING_WORK.md` | Active forward-looking task register — what to build next | At session start |
| `BUILD_LOG.md` | Completion record and deferred items | Read at session start; update at session end |
| `docs/archive/C1_MULTIAGENT_ARCHITECTURE_PLAN.md` | Archived — fully executed — reference for architecture decisions | Reference only |
| `docs/archive/C1_QUERY_IMPROVEMENT_PLAN.md` | Archived — fully executed — reference for query pipeline decisions | Reference only |

**These documents must be kept current.** When a task completes, the relevant governing document is updated before the session is closed. The Quality Guardian confirms the document accurately reflects what was built. A task is not complete until the document is updated and committed.

---

## Current Active Workstreams

Both original workstreams are fully complete. The active reference for what to build next is `docs/C1_REMAINING_WORK.md`.

The highest-priority items are:
1. `round_number` column in `query_log` — Migration 014 + TODO removal
2. Document download endpoint
3. Duplicate Executive Summary header (cosmetic)
4. SKILLS_STANDARDS.md Section 7 internal numbering (cosmetic)

Read `docs/C1_REMAINING_WORK.md` at session open to confirm the current state of each item.

---

## Technology Stack — Locked. Do Not Change.

| Component | Technology | Critical constraint |
|---|---|---|
| Document parsing | Docling | **Lazy import only** — `from docling...` inside function body, never module level |
| Chunking | tiktoken cl100k_base | **450-token target**, 50-token overlap (validated 2026-03-30) |
| Embeddings | Gemini Embeddings API gemini-embedding-001 | 3072 dimensions, batched at 100 |
| Vector store | pgvector on Supabase | Sequential scan — **no HNSW/IVFFlat at 3072 dims** (pgvector 0.8.0 cap) |
| AI agents | Anthropic Claude API | claude-sonnet-4-6 — no LangChain, no LangGraph, no LlamaIndex |
| Database | Supabase PostgreSQL | Project `bkkujtvhdbroieffhfok`, EU West 1 |
| Auth | Supabase Auth | JWT validation server-side only |
| Backend | Python FastAPI | `src/api/` |
| Backend hosting | Railway | Dockerfile builder — **never switch to Nixpacks** |
| Frontend hosting | Vercel | `frontend/` directory, Vite preset — **this is a Vite/React app, not Next.js** |

Do not introduce any orchestration framework. Build directly against the Gemini and Anthropic SDKs.

---

## Architecture Boundaries — Non-Negotiable

**Ingestion pipeline handles (`src/ingestion/`):**
- Docling document parsing (PDF text + OCR, DOCX, XLSX) — lazy import
- Section-aware chunking — tiktoken cl100k_base, 450-token target, 50-token overlap
- Embedding — Gemini Embeddings API, 3072 dims, batched at 100
- Chunk storage — pgvector on Supabase (`document_chunks` table, immutable after write)
- Claude-based taxonomy classification (0.75 confidence threshold)
- Claude-based metadata extraction
- Tier-based field validation
- Original file preserved to Supabase Storage (`document-originals` bucket) before ingestion begins

**Reference document ingestion handles (`scripts/ingest_reference.py`):**
- CLI script for Layer 2 reference documents (FIDIC, laws, standards)
- Flags: `--file`, `--name`, `--document-type`, `--standard-body`, `--edition-year`,
  `--layer` (2a or 2b, default 2b), `--jurisdiction` (international/uae/ksa/qatar), `--description`
- Same parse → chunk → embed pipeline as project documents
- Stores to `reference_documents` + `reference_chunks` tables (platform-wide, not project-scoped)

**Claude API handles:**
- Document classification against the 176-type taxonomy
- Metadata extraction from document content
- Three-tier agent architecture (Tier 1 orchestrators + Tier 2 SMEs)
- Round 0 domain triage (fast, synchronous)
- Master orchestration (parallel Round 1 dispatch)
- Contradiction detection (intra-document and cross-specialist stub)
- Response synthesis

**Supabase handles:**
- All relational data — projects, contracts, parties, document types
- Layer 1 document registry (`documents` table, includes `storage_path`) and chunks (`document_chunks`)
- Layer 2 reference documents (`reference_documents` with `layer_type` + `jurisdiction`) and chunks (`reference_chunks`)
- Contradiction flags (project-scoped)
- Async query jobs (`query_jobs` table — PROCESSING/COMPLETE/FAILED)
- Immutable audit log (`query_log` — UPDATE and DELETE blocked by trigger)
- Classification queue
- File storage — original uploaded documents (`document-originals` bucket, private)
- Row Level Security — users access their own project data only

**FastAPI backend handles:**
- All requests from frontend
- JWT validation before any action
- Orchestration of ingestion pipeline, Claude API, and Supabase
- All API keys and credentials server-side only — never exposed to frontend

Do not move responsibilities between these systems without explicit instruction.

---

## Agent Team

Five agents work on C1. Every session opens with a declaration of which agent(s) are active. No agent touches another agent's ownership boundary without explicit instruction.

| Agent | Owns |
|---|---|
| **DB Architect** | `supabase/migrations/`, RLS policies, triggers, RPC functions, pgvector setup, schema design |
| **Ingestion Engineer** | `src/ingestion/`, `scripts/ingest_reference.py`, Docling, chunker, embedder, store, classifier, metadata extractor, validator, pipeline, status tracker |
| **Agent Orchestrator** | `src/agents/`, orchestrator, BaseOrchestrator, BaseSpecialist, SkillLoader, tools, retrieval, contradiction detection, synthesis, specialist configs, domain router |
| **API Engineer** | `src/api/`, FastAPI routes, Pydantic schemas, auth middleware, error handlers, CORS; also `frontend/` |
| **Quality Guardian** | Cross-cutting review of all output — every task, every agent, every session |

### Within-Session Collaboration

Some tasks require multiple agents in the same session. The order is always explicit and declared at session opening. Rules:

1. **Sequential within session:** The first agent completes its full scope and reports clearly before the second begins.
2. **Declared handoff:** When the first agent finishes: "Handoff to [Agent]. The following outputs are ready: [list]. Assumptions the next agent depends on: [list]."
3. **No boundary crossing:** If Agent A's task requires a change in Agent B's files, Agent A flags it and waits.
4. **Quality Guardian reviews after each agent's tasks complete.**

### Quality Guardian Rules

#### When Quality Guardian is invoked

Quality Guardian is invoked **after every individual task completes** — not only at session end. Every time an agent reports a task done, Quality Guardian reviews before the next task begins.

Quality Guardian is never skipped.

#### What Quality Guardian does

1. Reviews the output against the task specification
2. Classifies every finding: CRITICAL / HIGH / MEDIUM / LOW
3. **If no findings:** States "Quality Guardian: PASS — [task] approved. No issues found."
4. **If findings exist:**
   ```
   Quality Guardian: [SEVERITY] — [Agent] — [File/function] — [Issue] — [Required action]
   ```
   Then instructs the responsible agent to address before the task is marked complete.
5. After corrections: re-reviews. PASS or issues another instruction.
6. MEDIUM and LOW findings that are acceptable to carry forward are logged in `BUILD_LOG.md`.

#### Quality Guardian never does

- Never passes a task with unresolved CRITICAL or HIGH findings
- Never accepts "it works" as a substitute for "it is correct"
- Never instructs an agent to touch files outside its ownership boundary

#### Quality Guardian checklist

**Code correctness:** Dead code, unused imports, functions doing more than one thing, inconsistent naming

**Failure handling:** Silent failures, missing try/except on external calls, missing declared failure state

**Code standards:** Missing type hints, print statements in production code, hard-coded values

**Architecture compliance:** Boundary violations, Docling imported at module level, new vector index at 3072 dims, sensitive data in logs

**Spec compliance:** Output matches task specification, governing documents updated, completion criteria met

---

## Session Protocol — Mandatory for Every Session

### At Session Opening (before writing any code)

1. Declare the session: active agent(s), task, scope, what is NOT in scope
2. Read `docs/C1_REMAINING_WORK.md` and `BUILD_LOG.md` to confirm current state
3. Run the pre-task consistency check (see below)
4. State any open questions before starting
5. Wait for Yasser's confirmation before writing any code

### Pre-Task Consistency Check

Before writing any code, answer these questions explicitly:

- What was completed previously? (Read `BUILD_LOG.md`)
- Does the current codebase match what was reported? (Read the relevant files)
- Does the current task depend on previous output? If yes, confirm it exists and is correct
- Does the current task risk conflicting with anything already built? If yes, state the conflict
- Does the current task make assumptions about the DB schema, API contracts, or model interfaces? If yes, confirm against actual code

If any check reveals a gap or inconsistency, stop and report to Yasser before writing any code.

### Commit Protocol — Mandatory

**Each task must be committed and pushed to GitHub immediately after Quality Guardian PASS.**
One task — one commit — one push.

Commit message format: `[type]: [description]`
Example: `feat: Migration 014 — round_number column in query_log`

### At Session Close

1. State exactly what was built — file by file
2. State what was NOT completed and why (if applicable)
3. State any new deferred items discovered
4. Update `BUILD_LOG.md` with the session's completion entry
5. Update `docs/C1_REMAINING_WORK.md` to mark completed items
6. Confirm all files are committed and pushed
7. State what the next session should pick up

---

## Agent Architecture State

### Three-Tier Architecture

```
Tier 0 — Main Orchestrator (router only)
    ↓ parallel Round 1 dispatch
Tier 1 — Domain Orchestrators (BaseOrchestrator)
    Legal & Contractual  |  Commercial & Financial  |  Financial & Reporting
    ↓ invoke_sme tool (on demand)
Tier 2 — SME Agents (BaseSpecialist)
    Claims & Disputes  |  Schedule & Programme  |  Technical & Construction
```

**Tier 1 orchestrators:** Loaded via `BaseOrchestrator`, directive files at
`skills/orchestrators/{domain}/directive.md`. Dispatch to Tier 2 via `invoke_sme`
tool. All three run in parallel via `ThreadPoolExecutor`.

**Tier 2 SMEs:** Loaded via `BaseSpecialist`, skill files at
`skills/smes/{domain}/*.md`. Invoked on-demand by Tier 1 orchestrators.

**Round 0 (pre-analysis triage):**
- `POST /projects/{id}/query/assess` — synchronous, fast
- Single Claude API call returns `Round0Assessment` with PRIMARY/RELEVANT/NOT_APPLICABLE
  per domain and a 2-sentence executive brief
- Frontend shows Round0Card — user selects domains before full analysis runs

**Domain name mapping (locked):**
```python
DOMAIN_TO_CONFIG_KEY = {
    "legal_contractual": "legal",
    "commercial_financial": "commercial",
    "financial_reporting": "financial",
}
```

**Risk mode:** `risk_mode: bool = False` on `QueryRequest` and `SubmitQueryRequest`.
When True, `_RISK_FRAMING_DIRECTIVE` is appended to the query for all Tier 1 orchestrators.
Frontend: amber checkbox in `QueryInput.tsx`.

**Domain filtering:** `domains: list[str] | None = None` on `QueryRequest`.
When provided, only those domains run. Absent = all domains (backward compatible).

**Prompt caching:** Both `BaseOrchestrator` and `BaseSpecialist` wrap the system
prompt in `cache_control: ephemeral` on every `messages.create` call.
90% cost saving on cache hits (5-minute cache lifetime).

### Key Files in `src/agents/`

| File | Purpose |
|---|---|
| `orchestrator.py` | Main orchestrator, `process_query`, `assess_query`, `_RISK_FRAMING_DIRECTIVE` |
| `base_orchestrator.py` | Tier 1 base class — directive loading, `invoke_sme` tool, prompt caching |
| `base_specialist.py` | Tier 2 base class — skill loading, agentic loop, prompt caching |
| `tools.py` | `TOOL_DEFINITIONS` (4 shared tools) + `ORCHESTRATOR_TOOL_DEFINITIONS` (includes `invoke_sme`) |
| `skill_loader.py` | Dynamic markdown loading — orchestrators from `skills/orchestrators/`, SMEs from `skills/smes/` |
| `specialist_config.py` | `SPECIALIST_CONFIGS` dict — tier, round assignment, max tool rounds |
| `domain_router.py` | Claude-based domain identification |
| `retrieval.py` | Four-search hybrid pipeline |
| `contradiction.py` | Intra-document contradiction detection + write-back |
| `contradiction_cross.py` | **Stub — returns `[]`** — Phase 7 fills this |
| `models.py` | All agent data models including `QueryRequest` (risk_mode, domains), `DomainRecommendation`, `Round0Assessment`, `RetrievedChunk` (is_reference), `SpecialistFindings` |
| `prompts.py` | Domain routing system prompt, specialist system prompts |
| `audit.py` | Immutable `query_log` writes |

### Skill Files

```
skills/
├── orchestrators/
│   ├── legal/directive.md
│   ├── commercial/directive.md
│   └── financial/directive.md
└── smes/
    ├── legal/          (5 files)
    ├── claims/         (5 files)
    ├── schedule/       (6 files)
    └── technical/      (6 files)
```

22 skill files total. SkillLoader scans `*.md` files dynamically — no hardcoded filenames.
Governed by `docs/SKILLS_STANDARDS.md` v1.3.

### Retrieval Pipeline — Four-Search Flow

`retrieve_chunks` in `retrieval.py`:

1. Embed query (Gemini, shared across all four searches)
2. Layer 1 semantic — `search_chunks_semantic` RPC (project-scoped, raises `AgentError` on failure)
3. Layer 1 full-text — `search_chunks_fulltext` RPC (project-scoped, non-fatal)
4. Layer 2 reference semantic — `search_chunks_reference_semantic` RPC (platform-wide, optional `p_layer_type`, `p_jurisdiction` filters)
5. Layer 2 reference full-text — `search_chunks_reference_fulltext` RPC (platform-wide, same filters)
6. Merge and deduplicate within each layer
7. Enrich with metadata
8. Build `RetrievedChunk` list (Layer 1: `is_reference=False`; Layer 2: `is_reference=True`)

### Two-Layer Warehouse

**Layer 1 — Project documents** (`documents` + `document_chunks`):
- Project-scoped (RLS), 176 document types, immutable chunks
- Original files in `document-originals` Supabase Storage bucket

**Layer 2 — Reference documents** (`reference_documents` + `reference_chunks`):
- Platform-wide, `layer_type` column (2a = internal, 2b = external), `jurisdiction` column
- 6 FIDIC books ingested (1,917 chunks), all tagged `layer_type=2b`, `jurisdiction=international`
- Ingested via `scripts/ingest_reference.py` with `--layer` and `--jurisdiction` flags

### Async Query Pipeline

Queries run as background tasks:
1. `POST /query` → insert `query_jobs` row (PROCESSING) → start background task → return `query_id`
2. Background task: `process_query()` → update `query_jobs` (COMPLETE/FAILED)
3. `GET /queries/{id}/status` → poll for result

### `contradiction_cross.py` Status

Returns `[]` intentionally. Do not treat as a bug. Phase 7 fills the logic.

---

## Database State

**13 migrations applied (001–013):**

| Migration | Purpose |
|---|---|
| 001 | Initial schema — 8 tables, triggers, 176-row taxonomy seed |
| 002 | RLS policies |
| 003 | Classification queue project_id |
| 004 | pgvector extension, `document_chunks` table |
| 005 | `document_chunks` immutable (no UPDATE RLS) |
| 006 | `search_chunks_semantic` + `search_chunks_fulltext` RPC functions |
| 007 | `reference_documents` + `reference_chunks` tables + Layer 2 RPC functions |
| 008 | `storage_path` column on `documents` |
| 009 | `query_jobs` table (async query pipeline) |
| 010 | Retrieval metadata enrichment |
| 011 | `citation_fields` column on `document_types` |
| 012 | `layer_type` column on `reference_documents` (2a/2b split) |
| 013 | `p_layer_type` and `p_jurisdiction` filters on Layer 2 RPC functions |

**Tables:** projects, contracts, parties, document_types, documents, document_chunks,
reference_documents, reference_chunks, contradiction_flags, query_log, classification_queue,
query_jobs

**4 RPC functions:** `search_chunks_semantic`, `search_chunks_fulltext`,
`search_chunks_reference_semantic`, `search_chunks_reference_fulltext`

**Known TODO in `orchestrator.py`:** `round_number` is not written to `query_log` —
a TODO comment marks the location. Migration 014 will add the column. See `docs/C1_REMAINING_WORK.md`.

---

## Code Quality Standards

**One responsibility per function.** If a function does two things, split it.

**Explicit over implicit.** Name things clearly. No single-letter variables outside list comprehensions.

**Error handling is not optional.** Every external call (Gemini API, Anthropic API, Supabase) has a try/except with a meaningful error path.

**Every failure mode has a declared state.** Nothing disappears silently.

**Type hints on all functions.**

**No print statements in production code.** Use structlog via `get_logger(__name__)`. CLI scripts (`scripts/`) may use `print()`.

---

## Database Rules

**`query_log` is immutable.** Trigger blocks UPDATE and DELETE. This is a forensic audit trail.

**`document_chunks` and `reference_chunks` are immutable.** No UPDATE RLS. Write-once.

**Retrieval uses RPC functions.** The `<=>` operator cannot be expressed through PostgREST.

**pgvector dimension cap.** pgvector 0.8.0 caps HNSW/IVFFlat at 2000 dims. Embeddings are 3072 dims. Do not attempt to create an HNSW or IVFFlat index.

**Row Level Security is enabled on all tables.**

---

## Ingestion Pipeline Rules

**Docling import is lazy.** `from docling.document_converter import DocumentConverter` is imported inside the function body — not at module level.

**opencv-python-headless must be pinned.** Dockerfile uninstalls opencv-python and reinstalls opencv-python-headless==4.13.0.92.

**Accepted file types: .pdf, .docx, .xlsx only.**

**Chunks are immutable.** Write-once. CASCADE DELETE from parent document.

**Classification confidence threshold is 0.75.**

**Chunk target is 450 tokens** with 50-token overlap.

**Original file is preserved.** Stored in Supabase Storage before ingestion begins.

---

## Confidence States

| State | When |
|---|---|
| GREEN | All retrieved documents consistent on the queried field |
| AMBER | Partial support, or only one document covers the field |
| RED | Two or more documents contain conflicting values, or contradictions detected |
| GREY | Zero relevant chunks retrieved — warehouse has no relevant documents |

---

## FIDIC Awareness

C1 operates across all three FIDIC books in common use in the GCC. Skills handle all three.

**Red Book (Construction):** Employer designs, Contractor builds. Engineer has supervisory and certifying role.

**Yellow Book (Plant & Design-Build):** Contractor designs and builds. Engineer role retained. Design responsibility affects defects liability and variation entitlement.

**Silver Book (EPC/Turnkey):** Contractor takes full design, construction, and risk responsibility. Employer's Representative replaces the Engineer. Narrower Employer Risk Events.

Both 1999 and 2017 editions of each book are in active use in the GCC. The governing edition must always be confirmed from the contract documents in the warehouse — never assumed.

**6 FIDIC books are ingested in Layer 2 (1,917 chunks total):**
- Red Book 1999 and 2017
- Yellow Book 1999 and 2017
- Silver Book 1999 and 2017

---

## Deployment

| Component | Platform | URL |
|---|---|---|
| Frontend | Vercel | https://c1intelligence.vercel.app |
| Backend API | Railway | https://web-production-6f2c4.up.railway.app |
| Database | Supabase | Project `bkkujtvhdbroieffhfok` (eu-west-1) |
| Source code | GitHub | Yazo1968/C1Intelligence (main branch) |

**Environment Variables:**

Railway (backend): `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`

Vercel (frontend): `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY` (JWT format starting with `eyJ...` — NOT the `sb_publishable_` format), `VITE_API_BASE_URL`

**Deployment Notes:**
- Railway uses Dockerfile builder — `railway.json` sets `"builder": "DOCKERFILE"`. Do NOT switch to NIXPACKS.
- Start command: `sh -c 'uvicorn src.api.main:app --host 0.0.0.0 --port $PORT'`
- Railway Pro plan required for Docling build time
- Vercel project root: `frontend/`, framework preset: Vite
- GitHub pushes to `main` auto-trigger Railway and Vercel redeployments

---

## Repository Structure

```
/
├── README.md
├── CLAUDE.md
├── BUILD_LOG.md
├── requirements.txt
├── Dockerfile
├── railway.json
├── .env.example
├── .gitignore
├── scripts/
│   └── ingest_reference.py
├── docs/
│   ├── SKILLS_STANDARDS.md        ← v1.3 — governs all skill authorship
│   ├── C1_REMAINING_WORK.md       ← active task register
│   └── archive/
│       ├── C1_MULTIAGENT_ARCHITECTURE_PLAN.md
│       ├── C1_QUERY_IMPROVEMENT_PLAN.md
│       └── C1_TAXONOMY_v0.4.xlsx
├── supabase/
│   └── migrations/
│       ├── 001_initial_schema.sql
│       ├── 002_rls_policies.sql
│       ├── 003_classification_queue_project_id.sql
│       ├── 004_pgvector.sql
│       ├── 005_document_chunks_immutable.sql
│       ├── 006_retrieval_functions.sql
│       ├── 007_layer2_reference.sql
│       ├── 008_document_storage.sql
│       ├── 009_query_jobs.sql
│       ├── 010_retrieval_metadata.sql
│       ├── 011_document_type_citation_fields.sql
│       ├── 012_layer2_split_jurisdiction.sql
│       └── 013_layer2_retrieval_filters.sql
├── src/
│   ├── config.py
│   ├── clients.py
│   ├── logging_config.py
│   ├── ingestion/
│   │   ├── pipeline.py
│   │   ├── parser.py              ← Docling (lazy import)
│   │   ├── chunker.py             ← tiktoken, 450-token target
│   │   ├── embedder.py            ← Gemini Embeddings API
│   │   ├── store.py
│   │   ├── classifier.py          ← 0.75 threshold
│   │   ├── metadata_extractor.py
│   │   ├── validator.py
│   │   ├── status_tracker.py
│   │   ├── taxonomy_cache.py
│   │   ├── file_validation.py
│   │   └── models.py
│   ├── agents/
│   │   ├── orchestrator.py        ← process_query, assess_query, _RISK_FRAMING_DIRECTIVE
│   │   ├── base_orchestrator.py   ← Tier 1 base class
│   │   ├── base_specialist.py     ← Tier 2 base class
│   │   ├── tools.py               ← TOOL_DEFINITIONS + ORCHESTRATOR_TOOL_DEFINITIONS
│   │   ├── skill_loader.py
│   │   ├── specialist_config.py
│   │   ├── domain_router.py
│   │   ├── retrieval.py           ← four-search hybrid pipeline
│   │   ├── contradiction.py
│   │   ├── contradiction_cross.py ← STUB returns []
│   │   ├── synthesis.py
│   │   ├── prompts.py
│   │   ├── audit.py
│   │   └── models.py              ← QueryRequest, Round0Assessment, SpecialistFindings
│   └── api/
│       ├── main.py                ← CORS locked to https://c1intelligence.vercel.app
│       ├── auth.py
│       ├── errors.py
│       ├── schemas.py             ← SubmitQueryRequest (risk_mode, domains), Round0AssessmentResponse
│       └── routes/
│           ├── health.py
│           ├── projects.py
│           ├── documents.py
│           └── queries.py         ← /query, /query/assess, /queries/{id}/status
├── skills/
│   ├── orchestrators/
│   │   ├── legal/directive.md
│   │   ├── commercial/directive.md
│   │   └── financial/directive.md
│   └── smes/
│       ├── legal/                 ← 5 skill files
│       ├── claims/                ← 5 skill files
│       ├── schedule/              ← 6 skill files
│       └── technical/             ← 6 skill files
├── playbooks/
│   └── README.md
└── frontend/
    └── src/
        ├── api/
        │   ├── client.ts
        │   ├── documents.ts
        │   ├── projects.ts
        │   ├── queries.ts         ← assessQuery, submitQuery (risk_mode, domains)
        │   └── types.ts
        ├── auth/
        ├── components/
        │   ├── documents/
        │   ├── layout/
        │   ├── projects/
        │   ├── query/
        │   │   ├── QueryInput.tsx     ← risk mode toggle
        │   │   ├── QueryResponse.tsx
        │   │   ├── Round0Card.tsx     ← domain selection card
        │   │   └── ContradictionAlert.tsx
        │   └── ui/
        └── pages/
            ├── ProjectWorkspacePage.tsx
            ├── ProjectsPage.tsx
            ├── LoginPage.tsx
            └── AuditLogPage.tsx
```

---

## What You Must Never Do

**Never build ahead of instructions.**

**Never make architectural decisions without asking.**

**Never leave silent failures.** Every error produces a declared output.

**Never store sensitive data in logs.** Document content, party names, and financial figures must not appear in error logs.

**Never resolve contradictions.** Surface both versions. State which document says what.

**Never go beyond the evidence.** C1 surfaces what documents say. It does not predict outcomes, give legal advice, or render judgements.

**Never hardcode secrets.**

**Never accumulate dead code.** When an approach changes, delete the old code.

**Never touch a file outside your agent's ownership boundary without explicit instruction.**

**Never commit multiple tasks in a single commit.** One task — one commit — one push.

---

## The Reminder That Governs Everything

You are building a forensic intelligence platform used by auditors, legal counsel, and board members to understand the truth about a construction project. Every architectural decision must be defensible. Every output must be traceable. Every failure must be visible. Every session must leave the codebase and its governing documents in a state that is better than when the session started.

Build accordingly.
