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

C1 is a forensic construction documentation intelligence platform for the GCC market (UAE, Saudi Arabia, Qatar). It ingests project documents, reasons across them using AI agents, detects contradictions between documents, and produces forensic-grade responses with full source attribution and confidence classification.

Read `README.md` fully before writing any code in any session. It is the single source of truth for what C1 is, what it does, and how it is structured.

---

## Governing Documents — Read These First

Every session, before writing any code, confirm which governing document applies to the current task and read the relevant section:

| Document | Purpose | When to read |
|---|---|---|
| `README.md` | Platform architecture, warehouse design, API endpoints | Every session |
| `CLAUDE.md` | This file — behavioural contract | Every session |
| `docs/AGENT_PLAN.md` | Agent architecture phases 1–8 — **current active workstream** | Every session |
| `docs/SKILLS_STANDARDS.md` | Skill file authorship standards — governs all skill file content | When working on skill files |
| `BUILD_LOG.md` | Completion record and deferred items | Read at session start; update at session end |
| `C1_CLEANUP_PLAN.md` | **Archived** — Phases A–E complete. Reference only if a historical decision needs tracing. | Do not treat as active workstream |

**These documents must be kept current.** When a phase or task completes, the relevant governing document is updated before the session is closed. The Quality Guardian confirms the document accurately reflects what was built. A phase is not complete until the document is updated and committed.

---

## Current Active Workstream

**`docs/AGENT_PLAN.md` — Phase 3: Legal & Contractual Skills**

This is the active workstream. Read `docs/AGENT_PLAN.md` and `docs/SKILLS_STANDARDS.md` fully before starting any session in this workstream.

Phase 3 is knowledge authorship, not code work. Skill files are written in markdown, reviewed by Yasser as domain expert, and deployed by dropping files into `skills/legal/`. Claude Code is not used for skill file content. See `docs/SKILLS_STANDARDS.md` v1.1 for the full authorship standard.

Before Phase 3 skills are used in production, the following must be completed:
1. Review and approve `docs/research/legal_domain_research_summary.md`
2. Ingest FIDIC General Conditions for all three books in use in the GCC via `scripts/ingest_reference.py`: Red Book (Construction) 1999 and 2017, Yellow Book (Plant & Design-Build) 1999 and 2017, Silver Book (EPC/Turnkey) 1999 and 2017
3. Define five validation scenarios per `SKILLS_STANDARDS.md` Section 7

Five skill files to author in `skills/legal/`:
- `contract_assembly.md`
- `engineer_identification.md`
- `notice_and_instruction_compliance.md`
- `entitlement_basis.md`
- `key_dates_and_securities.md`

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
| Frontend hosting | Vercel | `frontend/` directory, Vite preset |

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
- CLI script for Layer 2 reference documents (FIDIC, PMBOK, IFRS, laws)
- Same parse → chunk → embed pipeline as project documents
- Stores to `reference_documents` + `reference_chunks` tables (platform-wide, not project-scoped)
- Run once by platform owner, not via API endpoint

**Claude API handles:**
- Document classification against the 176-type taxonomy
- Metadata extraction from document content
- All six domain specialist agents via BaseSpecialist
- Master orchestration (multi-round dispatch)
- Contradiction detection (intra-document and cross-specialist stub)
- Response synthesis

**Supabase handles:**
- All relational data — projects, contracts, parties, document types
- Layer 1 document registry (`documents` table, includes `storage_path`) and chunks (`document_chunks`)
- Layer 2 reference documents (`reference_documents`) and chunks (`reference_chunks`)
- Contradiction flags (project-scoped)
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
| **Agent Orchestrator** | `src/agents/`, orchestrator, BaseSpecialist, SkillLoader, tools, retrieval, contradiction detection, synthesis, specialist configs, domain router |
| **API Engineer** | `src/api/`, FastAPI routes, Pydantic schemas, auth middleware, error handlers, CORS |
| **Quality Guardian** | Cross-cutting review of all output — every phase, every agent, every session |

### Within-Session Collaboration (When Multiple Agents Work in One Session)

Some phases require multiple agents in the same session. The order is always explicit and declared at session opening. Rules:

1. **Sequential within session:** The first agent completes its full scope and reports clearly before the second agent begins. Agents do not work simultaneously on interdependent files.
2. **Declared handoff:** When the first agent finishes, it states: "Handoff to [Agent Name]. The following outputs are ready: [list]. The following assumptions the next agent depends on: [list]."
3. **No boundary crossing:** If Agent A's task requires a change in Agent B's files, Agent A flags it and waits. It does not make the change unilaterally.
4. **Quality Guardian reviews after each agent's tasks complete**, and also performs a combined review of all outputs once the final agent finishes. See Quality Guardian Rules below for the full process.

### Quality Guardian Rules

#### When Quality Guardian is invoked

Quality Guardian is invoked **after every individual task completes** — not only at the end of a session. Every time an agent reports a task done, Quality Guardian reviews that output before the next task begins. For multi-agent sessions, Quality Guardian also performs a combined review of all outputs after the final agent completes.

Quality Guardian is never skipped. It is not optional when time is short. It is not skipped because a task seems simple.

#### What Quality Guardian does when invoked

1. **Reviews the output** against the task specification and the checklist below
2. **Classifies every finding** with a severity: CRITICAL / HIGH / MEDIUM / LOW
3. **If no findings:** States "Quality Guardian: PASS — [task name] approved. No issues found." The next task may proceed.
4. **If findings exist:** States each finding clearly in this format:

   ```
   Quality Guardian: [SEVERITY] — [Agent Name] — [File/function] — [Issue description] — [Required corrective action]
   ```

   Then instructs the responsible agent directly:

   ```
   [Agent Name]: address the above before this task is marked complete. Report back when corrected.
   ```

5. **After the agent reports corrections:** Quality Guardian re-reviews the specific items that were flagged. If resolved: PASS. If not resolved or new issues introduced: issues another corrective instruction. This cycle repeats until all CRITICAL and HIGH findings are resolved.
6. **MEDIUM and LOW findings** that are acceptable to carry forward are logged in `BUILD_LOG.md` with the task reference. They do not block the current task but must be addressed in the next appropriate session.

#### What Quality Guardian never does

- Never passes a task with unresolved CRITICAL or HIGH findings
- Never merges MEDIUM/LOW findings into vague summary language — every finding is stated precisely with a required action
- Never instructs an agent outside that agent's ownership boundary to fix something
- Never accepts "it works" as a substitute for "it is correct"

#### Quality Guardian checklist

Applied to every task output:

**Code correctness:**
- Dead code — functions defined but not called anywhere
- Unused imports
- Functions doing more than one thing
- Inconsistent naming with the rest of the codebase

**Failure handling:**
- Silent failures — exceptions swallowed without logging
- Missing try/except on every external call (Supabase, Gemini API, Anthropic API)
- Missing declared failure state (every failure must produce a visible output — status update, log entry, or error response)

**Code standards:**
- Missing type hints on new functions
- Print statements in production code (structlog only — `get_logger(__name__)`)
- Hard-coded values that should be config or constants

**Architecture compliance:**
- Boundary violations — agent touching files outside its ownership
- Docling imported at module level (must be lazy — inside function body only)
- New vector index attempted at 3072 dims (will fail — pgvector 0.8.0 cap)
- Sensitive data in log messages

**Spec compliance:**
- Task output matches what was specified in `docs/AGENT_PLAN.md` or `docs/SKILLS_STANDARDS.md`
- Governing documents updated if the task required it
- Completion criteria from the governing document are met

---

## Session Protocol — Mandatory for Every Session

### At Session Opening (before writing any code)

1. Declare the session: active agent(s), phase/task, scope, what is NOT in scope
2. Read the relevant governing document for this session's task
3. **Run the pre-task consistency check** (see below)
4. State any open questions that need answering before starting
5. Wait for Yasser's confirmation before writing any code

### Pre-Task Consistency Check

Before writing any code, answer these questions explicitly:

- What was completed in the previous session? (Read `BUILD_LOG.md` to confirm)
- Does the current codebase match what the previous session reported? (Read the relevant files)
- Does the current task depend on any output from the previous session? If yes, confirm that output exists and is correct before proceeding
- Does the current task risk conflicting with anything already built? If yes, state the conflict and how it will be avoided
- Does the current task make any assumptions about the database schema, API contracts, or model interfaces? If yes, confirm those assumptions against the actual code before proceeding

If any check reveals a gap or inconsistency with a previous session's reported output, stop and report the discrepancy to Yasser before writing any code.

### Commit Protocol — Mandatory

**Each task must be committed and pushed to GitHub immediately after Quality Guardian PASS.** Do not accumulate multiple tasks into a single commit. One task — one commit — one push. This allows the session coordinator to independently verify each change before the next task begins.

Commit message format: `[agent]: [phase] [task description]`
Example: `feat: Phase 3 Task 1 — contract_assembly skill file`

### At Session Close

1. State exactly what was built — file by file, function by function where relevant
2. State what was NOT completed and why (if applicable)
3. State any new deferred items discovered during this session
4. Update `BUILD_LOG.md` with the session's completion entry
5. Update the relevant governing document if the session completed a phase or changed an architectural decision
6. Confirm all files are committed and pushed to the repository
7. State what the next session should pick up and any dependencies it needs to be aware of

---

## Living Document Protocol

The following documents must be updated when relevant work is completed. Never mark a session complete without doing this.

| Event | Document to update |
|---|---|
| AGENT_PLAN phase complete | `BUILD_LOG.md`, `docs/AGENT_PLAN.md` (phase status table) |
| New deferred item identified | `BUILD_LOG.md` (Deferred Items section) |
| Architectural decision made or changed | `CLAUDE.md` and `README.md` |

---

## Deferred Items Register

The following items are known, acknowledged, and explicitly not being addressed in the current workstream. Do not raise them as issues. Do not attempt to fix them. Log any newly discovered deferred items in `BUILD_LOG.md`.

| Item | Reason deferred | When to address |
|---|---|---|
| Party ID resolution (`issuing_party_id`, `receiving_party_id` always NULL) | Requires parties management API (create, list, assign roles) that does not exist | Post-skills workstream |
| `round_number` column in `query_log` | DB migration required; TODO comment in `orchestrator.py` | DB Architect micro-session after skills complete |
| Vector index (HNSW/IVFFlat) | pgvector 0.8.0 caps at 2000 dims; embeddings are 3072 dims | When Supabase upgrades pgvector |
| Approval workflows | Phase 2 feature — correctly deferred from initial build | Phase 2 |
| Five user roles and authority matrix | Phase 2 feature | Phase 2 |
| Document control system integration (Aconex, Docutrack) | Phase 2 feature | Phase 2 |
| Document download endpoint (`GET /documents/{id}/download`) | Deferred from Phase D | Small task after Phase D — add before Phase 2 |
| Cross-specialist contradiction detection | `contradiction_cross.py` is a stub returning `[]` | AGENT_PLAN Phase 7 |
| CORS `allow_methods` / `allow_headers` tightening | Currently `["*"]` — acceptable for known frontend but not hardened | Future hardening session |
| Live end-to-end test of `scripts/ingest_reference.py` | Docling + Gemini API unavailable in Claude Code environment | Must run before AGENT_PLAN Phase 3 goes into production |
| `function_search_path_mutable` on all RPC functions | Pre-existing pattern across all project RPC functions | Future hardening session |

---

## Completed Build History

### Original Build (2026-03-28)

All seven original steps complete and deployed:
1. ~~Supabase schema~~ — migrations 001–003 applied (9 tables, triggers, 176-row taxonomy seed, RLS)
2. ~~Ingestion pipeline~~ — `src/ingestion/` complete (parse, classify, extract, chunk, embed, store)
3. ~~Master orchestrator~~ — `src/agents/orchestrator.py`
4. ~~Domain specialists~~ — six specialist stubs, system prompts in `src/agents/prompts.py`
5. ~~Contradiction detection~~ — `src/agents/contradiction.py` (non-blocking write-back)
6. ~~FastAPI layer~~ — `src/api/` (9 authenticated endpoints)
7. ~~Frontend~~ — React/TypeScript/Tailwind, deployed to Vercel

### pgvector Migration (2026-03-30)

Gemini File Search replaced with self-owned pgvector pipeline. Migrations 004–006 applied. Smoke test passed (5/5 tests). See `docs/migrations/RETRIEVAL_MIGRATION.md`.

### AGENT_PLAN.md Phase 1 — Agent Template (Complete)

Built: `BaseSpecialist`, `SkillLoader`, four shared tools (`search_chunks`, `get_document`, `get_contradictions`, `get_related_documents`), `SpecialistConfig`, stub Claims specialist. Quality Guardian: 7/7 checks passed.

### AGENT_PLAN.md Phase 2 — Multi-Round Orchestrator (Complete)

Built: `DOMAIN_TO_CONFIG_KEY` mapping, Round 1 parallel dispatch via `ThreadPoolExecutor`, Round 2 sequential dispatch with Round 1 handoff, `contradiction_cross.py` stub, downstream functions adapted for `SpecialistFindings` model. Quality Guardian: 7/7 checks passed.

### C1_CLEANUP_PLAN.md — Phases A–E (Complete, 2026-03-31)

All five phases complete. See `BUILD_LOG.md` for full details.

- **Phase A** — CORS wildcard fixed, unsupported file types removed, Dockerfile CMD corrected, dead files deleted (`specialist.py`, `specialists/claims.py`), dead constants and dead model field removed.
- **Phase B** — Spec values aligned (450 tokens, 0.75 threshold documented), stale Gemini-era frontend types removed, README brought current.
- **Phase C1** — Layer 2 database tables created (`reference_documents`, `reference_chunks`), RLS policies, RPC functions (`search_chunks_reference_semantic`, `search_chunks_reference_fulltext`), CLI ingestion script (`scripts/ingest_reference.py`).
- **Phase C2** — Layer 2 retrieval integrated into hybrid search pipeline. `RetrievedChunk` extended with `is_reference` field. `_build_user_message` updated with labelled Layer 1 / Layer 2 sections.
- **Phase D** — Playbook auto-generation from Supabase DB (replaces inert flat-file mechanism). File storage added: original documents preserved to `document-originals` bucket. Migration 008 applied (`storage_path` on `documents`).
- **Phase E** — This CLAUDE.md rewrite.

---

## Agent Architecture State

### What Is Built and How It Works

**Round structure:**
- Round 1 (parallel via `ThreadPoolExecutor`): `legal`, `commercial`
- Round 2 (sequential with Round 1 handoff): `claims`, `schedule`, `technical`, `governance`

**Domain name mapping (locked):**
`identify_domains()` returns full domain names (e.g., `"legal_contractual"`). `SPECIALIST_CONFIGS` uses short keys (e.g., `"legal"`). `DOMAIN_TO_CONFIG_KEY` in `orchestrator.py` bridges these.

```python
DOMAIN_TO_CONFIG_KEY = {
    "legal_contractual": "legal",
    "commercial_financial": "commercial",
    "schedule_programme": "schedule",
    "technical_design": "technical",
    "claims_disputes": "claims",
    "governance_compliance": "governance",
}
```

**Key files in `src/agents/`:**
- `orchestrator.py` — master orchestrator, multi-round dispatch
- `base_specialist.py` — shared agentic loop (assess → tool call → reason → return); `_build_user_message` produces labelled Layer 1 and Layer 2 sections
- `tools.py` — four shared tools available to all specialists
- `skill_loader.py` — dynamic markdown loading from `skills/{domain}/`; DB-driven playbook auto-generation via `_generate_project_context()` (flat file override if `playbooks/{project_id}.md` exists)
- `specialist_config.py` — `SPECIALIST_CONFIGS` dict
- `domain_router.py` — Claude-based domain identification
- `retrieval.py` — four-search hybrid pipeline: Layer 1 semantic + Layer 1 full-text + Layer 2 reference semantic + Layer 2 reference full-text; Layer 2 chunks flagged with `is_reference=True`
- `contradiction.py` — intra-document contradiction detection + write-back
- `contradiction_cross.py` — **stub, returns empty list** — AGENT_PLAN Phase 7 fills this
- `prompts.py` — system prompts for domain routing, six specialists, contradiction detection
- `models.py` — all agent data models including `SpecialistFindings` (active model) and `RetrievedChunk` (with `is_reference` field)
- `audit.py` — `query_log` write and document snapshot

**`SpecialistFindings` is the active model** (not v1 `SpecialistFinding`). All downstream functions use `SpecialistFindings`.

**`contradiction_cross.py` status:** Returns `[]`. This is intentional. AGENT_PLAN Phase 7 will fill the logic. Do not treat the empty return as a bug.

**`prompts.py` status:** Contains hardcoded FIDIC knowledge in `SPECIALIST_SYSTEM_PROMPTS`. Layer 2 retrieval now supplements this with actual FIDIC document chunks from the warehouse when reference documents have been ingested. The hardcoded strings are a baseline fallback, not a replacement for Layer 2.

**`orchestrator.py` known TODO:** `round_number` is not written to `query_log` — a TODO comment marks the location. This requires a DB migration to add the column. Deferred — see Deferred Items Register.

### Retrieval Pipeline — Four-Search Flow

`retrieve_chunks` in `retrieval.py` performs eight steps:

1. Embed query (Gemini, shared across all four searches)
2. Layer 1 semantic search — `search_chunks_semantic` RPC (project-scoped, raises `AgentError` on failure)
3. Layer 1 full-text search — `search_chunks_fulltext` RPC (project-scoped, non-fatal)
4. Layer 2 reference semantic search — `search_chunks_reference_semantic` RPC (platform-wide, non-fatal, `p_top_k=5`)
5. Layer 2 reference full-text search — `search_chunks_reference_fulltext` RPC (platform-wide, non-fatal)
6. Merge and deduplicate within each layer (Layer 1 deduplicates against Layer 1; Layer 2 against Layer 2)
7. Enrich with metadata (Layer 1 from `documents` + `document_types`; Layer 2 from `reference_documents`)
8. Build `RetrievedChunk` list (Layer 1 first with `is_reference=False`; Layer 2 with `is_reference=True`)

### Playbook Mechanism — DB-Driven

`SkillLoader.load()` in `skill_loader.py`:

1. **Layer 1 (skills):** Scans `skills/{domain}/*.md` alphabetically — no hardcoded file list.
2. **Layer 2 (playbook):** Checks for `playbooks/{project_id}.md`. If present: reads it (manual override). If absent: calls `_generate_project_context(project_id)` which queries `contracts` and `parties` tables to produce a structured markdown block with contract names, FIDIC edition, and party roles. Graceful degradation: DB failure returns empty string; skills still load.

### Two-Layer Warehouse Architecture

**Layer 1 — Project documents** (`documents` + `document_chunks`):
- Project-scoped (RLS enforces per-project access)
- 176 document types from taxonomy
- Ingested via `POST /projects/{id}/documents`
- Original file stored to `document-originals` Supabase Storage bucket; path in `documents.storage_path`
- Immutable chunks (no UPDATE RLS)

**Layer 2 — Reference documents** (`reference_documents` + `reference_chunks`):
- Platform-wide (all authenticated users can SELECT)
- FIDIC, PMBOK, IFRS, applicable laws, government authority documents
- Ingested via `scripts/ingest_reference.py` (CLI, service role only)
- Immutable chunks (no UPDATE RLS)

---

## What You Must Never Do

**Never build ahead of instructions.**
If told to fix CORS, fix only CORS. Do not also fix the extension mismatch or anything else not in the instruction.

**Never make architectural decisions without asking.**
If two approaches exist, present them and wait for a decision. Do not pick one and proceed.

**Never leave silent failures.**
Every error produces a declared output. Log it, store it, surface it. Never swallow an exception silently.

**Never store sensitive data in logs.**
Document content, party names, and financial figures must not appear in error logs.

**Never resolve contradictions.**
When two documents conflict on the same field, surface both. State which document says what. Do not choose one.

**Never go beyond the evidence.**
C1 surfaces what documents say. It does not predict outcomes, give legal advice, or render judgements.

**Never hardcode secrets.**
API keys, database URLs, and credentials live in environment variables only.

**Never accumulate dead code.**
When an approach changes, delete the old code. Do not comment it out.

**Never touch a file outside your agent's ownership boundary without explicit instruction.**

**Never start the next task without completing the session protocol for the current one.**

**Never commit multiple tasks in a single commit.** One task — one commit — one push.

---

## Code Quality Standards

**One responsibility per function.** If a function does two things, split it.

**Explicit over implicit.** Name things clearly. No single-letter variables outside list comprehensions.

**Error handling is not optional.** Every external call (Gemini API, Anthropic API, Supabase) has a try/except with a meaningful error path.

**Every failure mode has a declared state.** Classification failure → `classification_queue`. Retrieval failure → GREY confidence. Storage failure → logged warning, ingestion continues. Nothing disappears silently.

**Type hints on all functions.**

**No print statements in production code.** Use structlog via `get_logger(__name__)`. CLI scripts (`scripts/`) may use `print()` — they are not production server code.

---

## Database Rules

**`query_log` is immutable.** Trigger blocks UPDATE and DELETE. This is a forensic audit trail.

**`document_chunks` and `reference_chunks` are immutable.** No UPDATE RLS policy. Write-once. To replace content, delete the parent document (CASCADE deletes chunks) and re-ingest.

**`contradiction_flags` are project-scoped.** A contradiction can only exist between two documents in the same project.

**Retrieval uses RPC functions.** The `<=>` cosine distance operator cannot be expressed through PostgREST. All vector similarity searches use `supabase_client.rpc(...)`.

**No orphaned foreign keys.** Every FK is enforced at database level.

**Row Level Security is enabled on all tables.**

**pgvector dimension cap.** pgvector 0.8.0 on Supabase caps HNSW/IVFFlat at 2000 dimensions. Embeddings are 3072 dimensions. Sequential scan is used. Do not attempt to create an HNSW or IVFFlat index — it will fail.

---

## Ingestion Pipeline Rules

**Docling import is lazy.** `from docling.document_converter import DocumentConverter` is imported inside the function body of `parse_document()` — not at module level. This prevents a startup crash caused by opencv transitive dependencies loading at FastAPI startup.

**opencv-python-headless must be pinned.** Dockerfile explicitly uninstalls opencv-python and reinstalls opencv-python-headless==4.13.0.92 after all pip installs.

**Accepted file types are .pdf, .docx, .xlsx only.** `ALLOWED_EXTENSIONS` and `ALLOWED_MIME_TYPES` in `src/config.py` contain exactly these three types. Do not add others without also extending the parser.

**Chunks are immutable.** Write-once. CASCADE DELETE from parent document deletes all chunks.

**CASCADE DELETE is enforced at the DB level.** `document_chunks.document_id` FK has `ON DELETE CASCADE`.

**Retrieval uses four RPC functions.** Layer 1: `search_chunks_semantic` and `search_chunks_fulltext` (project-scoped). Layer 2: `search_chunks_reference_semantic` and `search_chunks_reference_fulltext` (platform-wide).

**Classification confidence threshold is 0.75.** Documents below threshold go to `classification_queue`. Stricter than original 0.70 spec — 0.75 is correct for a forensic platform.

**Chunk target is 450 tokens.** With 50-token overlap. Validated in smoke test 2026-03-30. Supersedes original 512 spec.

**Processing status is always visible.** `QUEUED` → `EXTRACTING` → `CLASSIFYING` → `STORED` / `FAILED`. Nothing disappears silently.

**Original file is preserved.** Uploaded files are stored in Supabase Storage (`document-originals` bucket) at `{project_id}/{document_id}/{filename}` before ingestion begins. `documents.storage_path` is populated on success. Storage failure is non-fatal — ingestion continues.

---

## Confidence States

| State | When |
|---|---|
| GREEN | All retrieved documents consistent on the queried field |
| AMBER | Partial support, or only one document covers the field, or a specialist returned GREY (partial coverage treated as AMBER at orchestrator level) |
| RED | Two or more documents contain conflicting values, or contradictions detected |
| GREY | Orchestrator-level only: retrieval returned zero relevant chunks — warehouse has no relevant documents |

GREY at the orchestrator level means `retrieval.is_empty=True`. GREY from an individual specialist means that specialist found no relevant content — the orchestrator maps this to AMBER at the response level (partial coverage). These are distinct events.

---

## FIDIC Awareness

C1 operates across all three FIDIC books in common use in the GCC market. Skills must handle all three — a project may use any one of them.

**Red Book (Conditions of Contract for Construction):**
- Employer designs, Contractor builds
- Engineer has supervisory and certifying role with defined authority under the contract
- Standard clause structure: Clause 20 (1999) / Clauses 20–21 (2017) govern claims
- Most common on building, civil works, and infrastructure projects

**Yellow Book (Conditions of Contract for Plant & Design-Build):**
- Contractor designs and builds — design responsibility shifts entirely to Contractor
- Engineer role retained with similar supervisory/certifying function
- Affects defects liability, specification compliance, and variation entitlement
- Common on MEP, process plant, and infrastructure projects in the GCC

**Silver Book (Conditions of Contract for EPC/Turnkey):**
- Contractor takes full design, construction, and risk responsibility
- No Engineer in the traditional sense — Employer's Representative replaces the Engineer with materially different authority
- Significantly fewer Employer Risk Events — Contractor bears most project risk
- No Engineer's determination mechanism — disputes escalate directly to DAB/DAAB
- Used on large EPC projects, oil and gas related works, and PPP projects particularly in Saudi Arabia and Qatar

**Key forensic distinctions across all three books:**
- The 28-day Notice of Claim time bar applies across all three books — it is the most critical forensic flag regardless of which book governs
- Engineer authority differs materially: Red/Yellow retain the Engineer's determination role; Silver does not
- Design responsibility affects entitlement basis: on Yellow/Silver, Contractor-design deficiencies are not Employer Risk Events
- Sub-clause numbering is broadly similar across Red and Yellow; Silver differs in important ways
- Both 1999 and 2017 editions of each book are in active use in the GCC — the governing edition must always be determined from the contract documents in the warehouse, never assumed

**GCC-specific patterns:**
- The Engineer role may be split between PMC and Supervision Consultant on GCC projects — this creates genuine ambiguity that must be flagged, not resolved
- Contradiction between the same field in different documents is never resolved — both versions are always surfaced
- Layer 2 reference documents (Red, Yellow, and Silver Book General Conditions, 1999 and 2017) must be ingested via `scripts/ingest_reference.py` before Phase 3 skills are used in production

---

## Deployment

| Component | Platform | URL |
|---|---|---|
| Frontend | Vercel | https://c1intelligence.vercel.app |
| Backend API | Railway | https://web-production-6f2c4.up.railway.app |
| Database | Supabase | Project `bkkujtvhdbroieffhfok` (eu-west-1) |
| Source code | GitHub | Yazo1968/C1Intelligence (main branch) |

### Environment Variables

**Railway (backend):** `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`

**Vercel (frontend):** `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY` (anon JWT key starting with `eyJ...` — NOT the `sb_publishable_` format), `VITE_API_BASE_URL`

### Deployment Notes

- **Railway uses Dockerfile builder** — `railway.json` sets `"builder": "DOCKERFILE"`. Do NOT switch to NIXPACKS.
- **Start command uses `sh -c` wrapper** — `railway.json` startCommand: `sh -c 'uvicorn src.api.main:app --host 0.0.0.0 --port $PORT'`. The Dockerfile CMD also uses this wrapper.
- Railway Pro plan required for Docling build time.
- Vercel project root directory: `frontend/`, framework preset: Vite.
- GitHub pushes to `main` auto-trigger Railway and Vercel redeployments.

---

## Repository Structure

```
/
├── README.md                            ← Single source of truth for platform
├── CLAUDE.md                            ← This file — behavioural contract
├── BUILD_LOG.md                         ← Completion log and deferred items
├── C1_CLEANUP_PLAN.md                   ← Archived — Phases A–E complete
├── requirements.txt
├── Dockerfile
├── Procfile                             ← Legacy reference only
├── railway.json
├── .env.example
├── .gitignore
├── scripts/
│   └── ingest_reference.py             ← CLI script for Layer 2 reference ingestion
├── docs/
│   ├── AGENT_PLAN.md                   ← Agent enhancement plan (v1.3) — active workstream
│   ├── SKILLS_STANDARDS.md             ← Skill file authorship standards (v1.1)
│   ├── migrations/
│   │   └── RETRIEVAL_MIGRATION.md
│   ├── research/
│   │   └── legal_domain_research_summary.md
│   └── taxonomy/
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
│       └── 008_document_storage.sql
├── src/
│   ├── config.py
│   ├── clients.py
│   ├── logging_config.py
│   ├── ingestion/
│   │   ├── pipeline.py                 ← Accepts optional document_id param
│   │   ├── parser.py                   ← Docling (lazy import)
│   │   ├── chunker.py                  ← tiktoken, 450-token target
│   │   ├── embedder.py                 ← Gemini Embeddings API
│   │   ├── store.py                    ← pgvector storage + rollback
│   │   ├── classifier.py               ← Claude classification, 0.75 threshold
│   │   ├── metadata_extractor.py
│   │   ├── validator.py
│   │   ├── status_tracker.py
│   │   ├── taxonomy_cache.py
│   │   ├── file_validation.py
│   │   └── models.py
│   ├── agents/
│   │   ├── orchestrator.py             ← Multi-round dispatch, DOMAIN_TO_CONFIG_KEY
│   │   ├── base_specialist.py          ← Shared agentic loop, Layer 1/2 message sections
│   │   ├── tools.py                    ← Four shared tools
│   │   ├── skill_loader.py             ← Dynamic skill loading + DB-driven playbook
│   │   ├── specialist_config.py        ← SPECIALIST_CONFIGS dict
│   │   ├── domain_router.py
│   │   ├── retrieval.py                ← Four-search hybrid pipeline (Layer 1 + Layer 2)
│   │   ├── contradiction.py            ← Intra-document detection
│   │   ├── contradiction_cross.py      ← STUB — returns [] — AGENT_PLAN Phase 7 fills this
│   │   ├── synthesis.py
│   │   ├── prompts.py
│   │   ├── audit.py
│   │   ├── models.py                   ← RetrievedChunk (is_reference), SpecialistFindings
│   │   └── specialists/
│   │       └── __init__.py
│   └── api/
│       ├── main.py                     ← CORS locked to https://c1intelligence.vercel.app
│       ├── auth.py
│       ├── errors.py
│       ├── schemas.py
│       └── routes/
│           ├── health.py
│           ├── projects.py
│           ├── documents.py            ← Storage upload before ingestion
│           └── queries.py
├── skills/
│   ├── legal/                          ← AGENT_PLAN Phase 3 — active
│   ├── commercial/                     ← Phase 4
│   ├── claims/
│   │   └── README.md                   ← Placeholder
│   ├── schedule/                       ← Phase 6
│   ├── governance/                     ← Phase 6
│   └── technical/                      ← Phase 6
├── playbooks/
│   └── README.md                       ← Flat file manual override; DB-driven auto-generation is default
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── documents.ts
│   │   │   ├── projects.ts
│   │   │   ├── queries.ts
│   │   │   └── types.ts
│   │   ├── auth/
│   │   │   ├── AuthContext.tsx
│   │   │   ├── AuthGuard.tsx
│   │   │   └── supabase.ts
│   │   ├── components/
│   │   │   ├── audit/
│   │   │   ├── documents/
│   │   │   ├── layout/
│   │   │   ├── projects/
│   │   │   ├── query/
│   │   │   └── ui/
│   │   ├── pages/
│   │   │   ├── AuditLogPage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   ├── ProjectsPage.tsx
│   │   │   └── ProjectWorkspacePage.tsx
│   │   ├── config.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── ...
└── tests/                              ← Test suite (to be built)
```

---

## The Reminder That Governs Everything

You are building a forensic intelligence platform used by auditors, legal counsel, and board members to understand the truth about a construction project. Every architectural decision must be defensible. Every output must be traceable. Every failure must be visible. Every session must leave the codebase and its governing documents in a state that is better than when the session started.

Build accordingly.
