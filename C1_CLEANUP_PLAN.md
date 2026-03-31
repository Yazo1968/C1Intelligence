# C1 — Cleanup and Production-Readiness Plan
## Pre-Skills Build: Close All Open Issues and Establish Clean Foundation

**Version:** 1.0  
**Date:** March 2026  
**Status:** Active — Governing Document for Phases A through E  
**Purpose:** Complete reference for executing all cleanup and architecture completion work required before Phase 3 (Legal & Contractual Skills) of AGENT_PLAN.md can begin.

---

## 1. Context and Purpose

### 1.1 Where We Are

C1 is a live, deployed forensic construction documentation intelligence platform. The following is complete and working:

- Full document ingestion pipeline (Docling → classify → chunk → embed → store to pgvector)
- Multi-round agent orchestrator (Round 1: Legal + Commercial in parallel; Round 2: Claims + Schedule + Technical + Governance with Round 1 handoff)
- BaseSpecialist agentic loop (assess → tool call → reason → return findings)
- SkillLoader (dynamic markdown skill file loading)
- All six domain specialist stubs
- Full FastAPI backend (9 authenticated endpoints)
- React/TypeScript/Tailwind frontend
- Supabase schema (9 tables, 176 taxonomy rows, 6 migrations applied)
- pgvector hybrid retrieval (semantic + full-text via RPC functions)

**Deployment:**
- Frontend: https://c1intelligence.vercel.app (Vercel)
- Backend: https://web-production-6f2c4.up.railway.app (Railway, Pro plan, Dockerfile builder)
- Database: Supabase project `bkkujtvhdbroieffhfok` (EU West 1)
- Repository: github.com/Yazo1968/C1Intelligence (main branch)

### 1.2 Why This Plan Exists

A full codebase review on 2026-03-31 (reading all 119 files directly) identified a set of issues ranging from CRITICAL production risks to structural architectural gaps. Two decisions were also outstanding that needed resolution before work could begin.

Additionally, the CLAUDE.md behavioural contract in the repository is outdated — it does not reflect Phases 1 and 2 of AGENT_PLAN.md, the completed pgvector migration, or the locked architectural decisions made since the initial build. Every Claude Code session reads CLAUDE.md first. An outdated contract is a session reliability risk.

### 1.3 What This Plan Achieves

On completion of all five phases:

| Item | State |
|---|---|
| Production CORS | Fixed |
| Extension/parser alignment | Fixed |
| Dead code eliminated | Done |
| Spec/code consistency | Resolved (spec updated to match validated code) |
| Frontend stale types | Cleaned |
| Layer 2 reference documents | Implemented (two-table warehouse architecture) |
| Playbook mechanism | Working (DB-driven auto-generation) |
| File storage (forensic chain of custody) | Implemented (Supabase Storage) |
| CLAUDE.md | Fully current — accurate foundation for Phase 3 onwards |
| Phase 3 (Legal & Contractual Skills) | Unblocked |

---

## 2. Issues Register — Full Audit Findings

The following issues were identified by direct code review. They are the basis for the phased plan in Section 4.

### 2.1 CRITICAL

**Issue C1 — CORS wildcard in production**
- **File:** `src/api/main.py` line 22
- **Finding:** `allow_origins=["*"]` — any domain can make authenticated requests to the live backend. The comment says "Tighten in production" but this IS production.
- **Fix:** Replace with `["https://c1intelligence.vercel.app"]`

**Issue C2 — Extension/parser mismatch**
- **Files:** `src/config.py` (ALLOWED_EXTENSIONS), `src/ingestion/parser.py` (SUPPORTED_EXTENSIONS)
- **Finding:** `ALLOWED_EXTENSIONS` accepts `.pptx`, `.csv`, `.jpg`, `.jpeg`, `.png`. `SUPPORTED_EXTENSIONS` in the parser only handles `.pdf`, `.docx`, `.xlsx`. Uploading a PPTX creates a `documents` record at status `QUEUED`, transitions to `EXTRACTING`, then fails at the parse stage with an `IngestionError("Unsupported format")`. The user receives a `FAILED` document with no clear explanation at the upload stage. File validation must reject unsupported formats before any database record is created.
- **Fix:** Remove `.pptx`, `.csv`, `.jpg`, `.jpeg`, `.png` from `ALLOWED_EXTENSIONS` and `ALLOWED_MIME_TYPES`. The parser supports only three formats. Accepted types must match parseable types exactly.

### 2.2 HIGH

**Issue H1 — Dead file `src/agents/specialist.py`**
- **Finding:** The v1 specialist runner (`run_specialist` function, `SPECIALIST_TOOL` schema) is no longer imported by any module. The orchestrator uses `BaseSpecialist` from `base_specialist.py`. This 200+ line file is dead code. It creates confusion for any Claude Code session that reads it and assumes it is active.
- **Fix:** Delete the file entirely. No replacement needed.

**Issue H2 — Layer 2 reference documents not implemented**
- **Finding:** `README.md` Section 6.2 describes Layer 2 as global, static, non-project-specific reference documents (FIDIC conditions, PMBOK, IFRS, applicable laws, DOA matrices) that are ingested into the warehouse and retrieved via pgvector at query time. What exists in reality: all FIDIC knowledge is hardcoded as string constants inside `SPECIALIST_SYSTEM_PROMPTS` in `src/agents/prompts.py`. This means:
  - Agents cannot reason over actual FIDIC text — they reason over a hardcoded summary
  - Skills written in Phase 3 onwards cannot retrieve and cite specific FIDIC clauses from the warehouse
  - The two-layer warehouse architecture described in AGENT_PLAN.md v1.3 and SKILLS_STANDARDS.md does not actually exist
- **Fix:** Build Layer 2 as a separate set of tables (`reference_documents`, `reference_chunks`) with a dedicated ingestion script. See Phase C for full specification.

**Issue H3 — Frontend TypeScript types are stale**
- **Files:** `frontend/src/api/types.ts`, `frontend/src/components/projects/ProjectCard.tsx`
- **Finding:** `ProjectResponse` still declares `gemini_store_name: string | null`. `DocumentResponse` still declares `gemini_file_name` and `gemini_document_name`. These fields were removed from the backend schema in the pgvector migration (migration 004). `ProjectCard.tsx` renders "Store active" based on `project.gemini_store_name` — this condition can never be true since the field is never populated.
- **Fix:** Remove the three stale fields from `types.ts`. Remove the "Store active" logic from `ProjectCard.tsx`.

### 2.3 MEDIUM

**Issue M1 — Chunk target discrepancy**
- **Files:** `src/ingestion/chunker.py` (default `target_tokens=450`), `README.md` and `CLAUDE.md` (state 512)
- **Finding:** The code was validated at 450 tokens in the smoke test. Changing working code to match a pre-implementation spec introduces risk for no functional benefit. The spec should be updated to match the validated implementation.
- **Fix:** Update `README.md` and `CLAUDE.md` to state 450-token target. Add a comment in `chunker.py` noting that 450 was validated during smoke testing and supersedes the original 512 in the design spec.

**Issue M2 — Classification threshold discrepancy**
- **Files:** `src/config.py` (`CLASSIFICATION_CONFIDENCE_THRESHOLD = 0.75`), `README.md` (states 0.7)
- **Finding:** The code has been running at 0.75 since deployment. 0.75 is the correct value for a forensic platform — stricter is appropriate. The spec should be updated.
- **Fix:** Update `README.md` to state 0.75. Add a comment in `config.py` noting that 0.75 is correct for forensic use and supersedes the original 0.7.

**Issue M3 — Party IDs never populated**
- **Files:** `src/ingestion/metadata_extractor.py`, `src/ingestion/status_tracker.py`
- **Finding:** The metadata extractor correctly extracts `issuing_party_name` and `receiving_party_name` as text. `status_tracker.py`'s `update_document_metadata` writes other fields but never resolves party names to `parties` table UUIDs. `issuing_party_id` and `receiving_party_id` in `documents` are always NULL. Building party lookup requires a parties management API that does not exist.
- **Decision:** **Deferred.** Party names remain as text fields. No parties management feature is included in this plan. This will be a subsequent workstream after skills are complete.

**Issue M4 — Original file deleted after ingestion**
- **File:** `src/api/routes/documents.py`, the `finally` block at the end of `upload_document`
- **Finding:** `os.unlink(temp_path)` destroys the original uploaded file after chunking. The chunks and metadata are in Supabase but the source document is gone. This is inconsistent with C1's forensic positioning — auditors and legal counsel expect the original document to be retrievable.
- **Fix:** Integrate Supabase Storage. Store the original file before ingestion begins. See Phase D for specification.

**Issue M5 — Dockerfile CMD lacks `sh -c` wrapper**
- **File:** `Dockerfile`
- **Finding:** `CMD uvicorn src.api.main:app --host 0.0.0.0 --port $PORT` — Railway uses `railway.json`'s `startCommand` which has the `sh -c` wrapper, so the live deployment works. But running the container directly (local Docker testing, CI/CD pipelines) passes the literal string `$PORT` to uvicorn and fails with `Error: Invalid value for '--port'`.
- **Fix:** Change to `CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port $PORT"]`

### 2.4 LOW

**Issue L1 — Dead constants in `src/config.py`**
- **Finding:** `GEMINI_POLL_INTERVAL_SECONDS = 3` and `GEMINI_POLL_MAX_ATTEMPTS = 60` are Gemini File Search polling constants from before the pgvector migration. Nothing imports or uses them. The comment on `MAX_FILE_SIZE_BYTES` says "Gemini File Search limit" — the limit is still reasonable at 100MB but the comment is incorrect.
- **Fix:** Delete both constants. Fix the `MAX_FILE_SIZE_BYTES` comment.

**Issue L2 — Dead `raw_response_text` in `RetrievalResult`**
- **Files:** `src/agents/models.py`, `src/agents/retrieval.py`
- **Finding:** `RetrievalResult.raw_response_text` is always set to `""` in the retrieval layer. Leftover from when Gemini File Search returned a raw text response alongside grounding chunks.
- **Fix:** Remove the field from `RetrievalResult`. Remove the assignment in `retrieval.py`.

**Issue L3 — Unused `claims_specialist` instance**
- **File:** `src/agents/specialists/claims.py`
- **Finding:** `claims_specialist = BaseSpecialist(config=SPECIALIST_CONFIGS["claims"])` is instantiated at module level but never imported or used. The orchestrator instantiates specialists inline. This file has no purpose in the current architecture.
- **Fix:** Delete the file. The `src/agents/specialists/` directory and its `__init__.py` remain as the home for future specialist stubs if needed.

**Issue L4 — Accidental file at repo root**
- **File:** `The Gemini API enables Retrieval Au.md` (28 KB)
- **Finding:** Research notes accidentally committed to the repository root. Not referenced by any code or document.
- **Fix:** Delete from repository.

**Issue L5 — Playbook mechanism works but is entirely inert**
- **File:** `src/agents/skill_loader.py`
- **Finding:** `SkillLoader.load()` correctly loads `playbooks/{project_id}.md` when present and logs a warning on every query when absent. Since no project has a playbook file, every query log contains a warning that adds noise without adding information. The mechanism is sound but the data source needs to change.
- **Fix:** See Phase D — convert to DB-driven auto-generation.

---

## 3. Locked Decisions

The following two decisions were outstanding and are now resolved. They govern the build in Phases C and D.

### Decision 1 — Reference Document Ingestion Method
**Question:** Should Layer 2 reference documents (FIDIC, PMBOK, IFRS) be ingested via an API endpoint or a CLI script?

**Decision:** CLI script — `scripts/ingest_reference.py`. Run once locally by the platform owner. No API endpoint, no security surface. Reference documents are platform-managed assets, not user content. The script will be a simplified ingestion pipeline (parse → chunk → embed → store to `reference_chunks`) with no classification or metadata extraction steps. Reference documents are pre-categorised at ingestion time by passing explicit metadata to the script.

**Rationale:** An API endpoint creates unnecessary complexity and attack surface for something that will be run once (or rarely) by a single administrator. A CLI script is simpler, auditable, and consistent with how production reference data is typically managed.

### Decision 2 — Party ID Resolution
**Question:** Should `issuing_party_id` and `receiving_party_id` be populated during ingestion?

**Decision:** Deferred entirely. Party names stay as text fields in the `documents` table. This requires a parties management API (create party, list parties, assign roles) that does not exist and is not in scope for this plan.

**Rationale:** Party ID resolution is not blocking skills. The forensic value of linking documents to party records is real but implementing it correctly requires a full parties feature (create, list, role assignment, UI). That is a post-skills workstream.

---

## 4. Phased Build Plan

### Phase Sequencing Rationale

Phases A and B are pure cleanup — no new architecture, no risk. They must come first because Phase C and D work will be reviewed by the Quality Guardian, and having dead code and stale types in the codebase during that review creates noise.

Phase C (Layer 2) comes before Phase D (Playbooks + Storage) because the playbook auto-generation in Phase D needs to know the Layer 2 architecture exists and is stable before referencing it in documentation.

Phase E (CLAUDE.md rewrite) comes last because it captures the final state of everything.

---

### Phase A — Production Fixes + Code Cleanup
**Agents: API Engineer + Quality Guardian**  
**Scope: One session**

This phase eliminates the two CRITICAL issues and cleans up all dead code. Nothing architectural is touched.

**Tasks:**

1. **CORS fix** (`src/api/main.py`)
   - Change `allow_origins=["*"]` to `allow_origins=["https://c1intelligence.vercel.app"]`

2. **Extension/parser alignment** (`src/config.py`)
   - Remove `.pptx`, `.csv`, `.jpg`, `.jpeg`, `.png` from `ALLOWED_EXTENSIONS`
   - Remove corresponding entries from `ALLOWED_MIME_TYPES`
   - Result: both sets contain only `.pdf`, `.docx`, `.xlsx`

3. **Dockerfile CMD fix** (`Dockerfile`)
   - Change `CMD uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
   - To `CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port $PORT"]`

4. **Delete dead files**
   - `src/agents/specialist.py` — v1 specialist runner, not imported by anything
   - `src/agents/specialists/claims.py` — unused `claims_specialist` instance
   - `The Gemini API enables Retrieval Au.md` — accidental commit at repo root

5. **Dead constants removal** (`src/config.py`)
   - Delete `GEMINI_POLL_INTERVAL_SECONDS = 3`
   - Delete `GEMINI_POLL_MAX_ATTEMPTS = 60`
   - Fix `MAX_FILE_SIZE_BYTES` comment: remove "Gemini File Search limit", replace with "Maximum supported file size"

6. **Dead model field removal** (`src/agents/models.py`, `src/agents/retrieval.py`)
   - Remove `raw_response_text: str = ""` from `RetrievalResult`
   - Remove `raw_response_text=""` from the `RetrievalResult(...)` construction in `retrieval.py`

**What does NOT get touched:** Any pipeline logic, agent logic, database, frontend, README, CLAUDE.md.

**Completion criteria:**
- `grep -r "specialist.py\|claims_specialist\|GEMINI_POLL\|raw_response_text\|allow_origins.*\*" src/` returns zero matches
- CORS shows only the Vercel domain
- `ALLOWED_EXTENSIONS` contains exactly `{".pdf", ".docx", ".xlsx"}`
- Dead files confirmed deleted
- Dockerfile CMD uses `sh -c` wrapper
- Quality Guardian sign-off

---

### Phase B — Spec Alignment + Frontend Cleanup
**Agents: API Engineer + Quality Guardian**  
**Scope: One session**

This phase resolves spec/code inconsistencies and cleans the frontend of stale Gemini-era types. No functional changes.

**Tasks:**

1. **Classification threshold comment** (`src/config.py`)
   - Add comment: `# 0.75 validated post-deployment — stricter than original 0.70 spec; appropriate for forensic use`

2. **Chunk target comment** (`src/ingestion/chunker.py`)
   - Add comment to `target_tokens=450` default: `# 450 validated in smoke test (2026-03-30) — supersedes original 512-token design spec`

3. **Frontend types cleanup** (`frontend/src/api/types.ts`)
   - Remove `gemini_store_name: string | null` from `ProjectResponse`
   - Remove `gemini_file_name: string | null` from `DocumentResponse`
   - Remove `gemini_document_name: string | null` from `DocumentResponse`

4. **Frontend component cleanup** (`frontend/src/components/projects/ProjectCard.tsx`)
   - Remove the `project.gemini_store_name` check
   - Remove the "Store active" badge/text that depended on it

5. **README.md spec alignment**
   - Section 6.3: Update chunk size from 512 to 450 tokens
   - Section 6.3: Update classification confidence threshold from 0.7 to 0.75
   - Section 11 (Technical Stack table): Update chunking row to reflect 450-token target

6. **BUILD_LOG.md update**
   - Add entries for Phase A and Phase B completion

**Completion criteria:**
- Frontend TypeScript compiles without errors (`npm run build` in `frontend/` passes)
- `grep -r "gemini_store_name\|gemini_file_name\|gemini_document_name" frontend/src/` returns zero matches
- README values match code values (450 tokens, 0.75 threshold)
- Quality Guardian sign-off

---

### Phase C — Layer 2 Reference Document Architecture
**Agents: DB Architect (Session C1) + Ingestion Engineer (Session C1) + Agent Orchestrator (Session C2) + Quality Guardian (both sessions)**  
**Scope: Two sessions**

This is the most architecturally significant phase. It implements the two-layer warehouse described in `README.md` Section 6.2, `AGENT_PLAN.md` Section 3 (Principle 3), and `SKILLS_STANDARDS.md` Section 2.

#### Why This Matters

Skills authored in Phase 3 onwards are supposed to tell agents *how to analyse* — while the warehouse provides *the evidence*. If the FIDIC conditions of contract are not in the warehouse as retrievable documents, skills cannot instruct agents to retrieve and cite specific FIDIC clauses. The specialist system prompts in `prompts.py` contain FIDIC summaries as hardcoded strings. This is a placeholder. Layer 2 replaces it with real, retrievable, citeable documents.

#### Architecture Decision (Locked)

Layer 2 documents live in two dedicated tables: `reference_documents` and `reference_chunks`. They are **platform-wide** — not project-scoped. All authenticated users can retrieve from them. This keeps existing project-scoped `documents` and `document_chunks` unchanged.

---

#### Session C1 — DB Architect + Ingestion Engineer

**Task C1.1 — Migration 007** (`supabase/migrations/007_layer2_reference.sql`)

Create `reference_documents` table:
```
id               uuid         PK DEFAULT gen_random_uuid()
name             text         NOT NULL  (e.g., "FIDIC Red Book 1999 — General Conditions")
document_type    text         NOT NULL  (e.g., "FIDIC Conditions of Contract")
standard_body    text         NOT NULL  (e.g., "FIDIC", "PMI", "IASB", "UAE Government")
edition_year     text                   (e.g., "1999", "2017", "7th Edition")
jurisdiction     text                   (NULL = global; "UAE", "Saudi Arabia" for jurisdiction-specific)
description      text
status           text         NOT NULL CHECK (status IN ('ACTIVE', 'SUPERSEDED', 'DRAFT'))
created_at       timestamptz  NOT NULL DEFAULT now()
updated_at       timestamptz  NOT NULL DEFAULT now()
```

Create `reference_chunks` table:
```
id                    uuid         PK DEFAULT gen_random_uuid()
reference_document_id uuid         NOT NULL FK → reference_documents(id) ON DELETE CASCADE
chunk_index           integer      NOT NULL
content               text         NOT NULL
embedding             vector(3072) NOT NULL
token_count           integer
created_at            timestamptz  NOT NULL DEFAULT now()
```

RLS on both tables:
- `reference_documents`: SELECT for all authenticated users; INSERT/UPDATE/DELETE via service role only
- `reference_chunks`: SELECT for all authenticated users; INSERT/DELETE via service role only (no UPDATE — chunks are immutable)

GIN full-text index on `to_tsvector('english', content)` for `reference_chunks`.

`updated_at` trigger on `reference_documents`.

RPC function `search_chunks_reference_semantic(p_query_embedding vector(3072), p_top_k int DEFAULT 5)`:
- Queries `reference_chunks`
- Ordered by `embedding <=> p_query_embedding`
- Returns: `id, reference_document_id, chunk_index, content, token_count, similarity`
- No `project_id` filter — platform-wide

RPC function `search_chunks_reference_fulltext(p_query_text text, p_top_k int DEFAULT 5)`:
- Same pattern as `search_chunks_fulltext` but on `reference_chunks`
- Returns: `id, reference_document_id, chunk_index, content, token_count, rank`

Apply migration 007 to the live Supabase project (`bkkujtvhdbroieffhfok`).

**Task C1.2 — CLI Ingestion Script** (`scripts/ingest_reference.py`)

A standalone Python script. Not a FastAPI endpoint. Run from the command line by the platform owner to ingest FIDIC documents, PMBOK, and other reference materials.

Usage:
```bash
python scripts/ingest_reference.py \
  --file path/to/fidic_red_book_1999.pdf \
  --name "FIDIC Red Book 1999 — Conditions of Contract for Construction" \
  --document-type "FIDIC Conditions of Contract" \
  --standard-body "FIDIC" \
  --edition-year "1999" \
  --description "General Conditions (Part I) of the FIDIC Red Book 1999 edition"
```

CLI arguments:
- `--file` (required): Path to the document file
- `--name` (required): Full descriptive name
- `--document-type` (required): Type category (e.g., "FIDIC Conditions of Contract")
- `--standard-body` (required): Issuing body (e.g., "FIDIC", "PMI", "IASB")
- `--edition-year` (optional): Edition year or identifier
- `--jurisdiction` (optional, default None): Jurisdiction or None for global
- `--description` (optional): Additional description

Script flow:
1. Load environment variables from `.env` using `python-dotenv`
2. Validate the file (extension must be `.pdf`, `.docx`, or `.xlsx`; file must exist and be non-empty)
3. Parse with Docling via `src/ingestion/parser.py` (lazy import rule applies — `from docling...` inside function body)
4. Chunk with `src/ingestion/chunker.py` (450 tokens, 50 overlap)
5. Embed with `src/ingestion/embedder.py` (gemini-embedding-001, 3072 dims, batch 100)
6. Insert row into `reference_documents`
7. Bulk insert all chunks into `reference_chunks`
8. Print completion summary: document name, `reference_document_id`, chunk count

Error handling: if step 5, 6, or 7 fails, delete the `reference_documents` row (CASCADE deletes any partial chunks) and print the error message. Exit with non-zero status.

The script imports directly from `src/` — run from the repository root.

**Completion criteria for Session C1:**
- Migration 007 applies cleanly to live Supabase project
- `reference_documents` and `reference_chunks` tables exist with correct schema
- RLS confirmed: authenticated user can SELECT from both tables; INSERT blocked for authenticated (service role only)
- `ingest_reference.py` runs without error on a test PDF
- Test PDF appears in `reference_documents` with correct metadata
- Chunks appear in `reference_chunks` with non-null embeddings and correct `reference_document_id`
- `search_chunks_reference_semantic` RPC returns results for a test query
- Quality Guardian sign-off

---

#### Session C2 — Agent Orchestrator

**Task C2.1 — Update `RetrievedChunk` model** (`src/agents/models.py`)

Add field: `is_reference: bool = False`

**Task C2.2 — Update retrieval layer** (`src/agents/retrieval.py`)

`retrieve_chunks` currently performs two searches (Layer 1 semantic + full-text). Update to perform four:

1. Layer 1 semantic — existing `search_chunks_semantic` RPC (project-scoped, raises `AgentError` on failure)
2. Layer 1 full-text — existing `search_chunks_fulltext` RPC (project-scoped, non-fatal on failure)
3. Layer 2 reference semantic — new `search_chunks_reference_semantic` RPC (platform-wide, non-fatal on failure, `p_top_k=5`)
4. Layer 2 reference full-text — new `search_chunks_reference_fulltext` RPC (platform-wide, non-fatal on failure)

Layer 2 chunks get `is_reference=True` on their `RetrievedChunk` objects.

Deduplication: Layer 1 chunks deduplicate against each other. Layer 2 chunks deduplicate against each other. No cross-layer deduplication needed (different tables, different UUID namespaces — a UUID from `reference_chunks` can never collide with a UUID from `document_chunks`).

**Task C2.3 — Update metadata fetch and chunk construction** (`src/agents/retrieval.py`)

When `is_reference=True`, fetch `name` and `document_type` from `reference_documents` (not from the `documents` + `document_types` join used for Layer 1). Populate `document_reference` from `reference_documents.name`, `document_type` from `reference_documents.document_type`.

A separate `_fetch_reference_document_metadata(supabase_client, reference_document_ids)` function should handle this lookup, following the same pattern as `_fetch_document_metadata`.

**Task C2.4 — Update BaseSpecialist user message construction** (`src/agents/base_specialist.py`)

Update `_build_user_message` to separate Layer 1 and Layer 2 chunks into distinct labelled sections:

```
--- PROJECT DOCUMENT CHUNKS (Layer 1) ---

[Chunk {chunk_index} | Document: {document_id}]
{content}

--- REFERENCE DOCUMENT CHUNKS (Layer 2 — Standards and Regulations) ---

[Reference: {document_reference} | Standard: {document_type}]
{content}
```

If no reference chunks are retrieved, omit the Layer 2 section entirely (do not include an empty header).

**Completion criteria for Session C2:**
- After ingesting FIDIC 1999 via the CLI script, a query containing "Sub-Clause 20.1" or "notice of claim" returns at least one reference chunk with `is_reference=True`
- BaseSpecialist user message correctly separates Layer 1 and Layer 2 chunks in labelled sections
- Existing Layer 1 retrieval unchanged — project document queries still work
- Quality Guardian sign-off

---

### Phase D — Playbook Auto-Generation + File Storage
**Agents: DB Architect + Ingestion Engineer + Agent Orchestrator + Quality Guardian**  
**Scope: One session**

Two independent improvements — both complete in this session.

#### Part 1: Playbook Auto-Generation (Agent Orchestrator)

**Current state:** `SkillLoader.load()` looks for `playbooks/{project_id}.md`. No such files exist. Every query logs a warning. The mechanism is inert.

**Target state:** `SkillLoader.load()` queries Supabase to build a project-specific context block from existing database records. If a flat file exists, it takes precedence (manual override). If not, the DB query runs.

**Implementation in `src/agents/skill_loader.py`:**

Update the Layer 2 (playbook) section of `load()`:

1. Check if `playbooks/{project_id}.md` exists — if yes, read it and return it (current behaviour, unchanged)
2. If no flat file, import `get_supabase_client` from `src.clients` and query:
   - `contracts` table: `SELECT id, name, contract_type, fidic_edition WHERE project_id = {project_id}`
   - `parties` table: `SELECT id, name, role WHERE project_id = {project_id}`
3. Build and return a structured markdown string:

```markdown
--- PROJECT CONTEXT (auto-generated from database) ---

## Contracts on Record
[For each contract: name, type, FIDIC edition if set, else "FIDIC edition not specified"]

## Parties on Record
[For each party: name, role]

## FIDIC Edition
[If any contract has fidic_edition set: "Governing edition: {edition}"
 Else: "FIDIC edition not yet confirmed — determine from contract documents in the warehouse"]
```

4. If Supabase query raises an exception: log a warning, return empty string (graceful degradation)
5. If query returns empty results: return a brief string noting no contracts or parties are registered yet

**What this achieves:** Every query receives project-specific context from the database without requiring manually-authored flat files. When a user creates a project and adds a contract with `fidic_edition = '2017'`, that fact automatically appears in every specialist's system prompt.

The `playbooks/` directory and its `README.md` remain. Flat files are the manual override mechanism.

#### Part 2: File Storage — Forensic Chain of Custody (DB Architect + Ingestion Engineer)

**Task D.1 — Migration 008** (`supabase/migrations/008_document_storage.sql`):
```sql
ALTER TABLE documents ADD COLUMN storage_path text;
```
Apply to live Supabase project.

**Task D.2 — Supabase Storage integration** (`src/api/routes/documents.py`):

The challenge: `document_id` is created inside `ingest_document()` (via `create_document_record`), but the upload route needs the UUID to construct the storage path before calling the pipeline.

The fix: refactor `upload_document` to call `create_document_record` directly before calling the full pipeline, so the `document_id` is available for the Storage upload. The pipeline is then called starting from the `EXTRACTING` stage rather than the `QUEUED` stage.

Implementation:
1. Call `create_document_record(supabase_client, request)` to obtain `document_id`
2. Upload file bytes to Supabase Storage:
   ```python
   storage_path = f"{project_id}/{document_id}/{filename}"
   supabase_client.storage.from_("document-originals").upload(
       path=storage_path,
       file=content,
       file_options={"content-type": mime_type, "upsert": False}
   )
   ```
3. If upload succeeds: update `documents.storage_path = storage_path`
4. If upload fails: log warning and continue — storage failure must not block ingestion
5. Call `ingest_document()` with the pre-created `document_id` passed in (or proceed with the existing pipeline which will call `create_document_record` again — see note below)

**Note on pipeline refactoring:** The cleanest approach is to pass an optional `document_id` parameter to `ingest_document()` so it skips the `create_document_record` step when a record already exists. This is a small change to `src/ingestion/pipeline.py`. If this creates complexity, an acceptable alternative is to create the document record in the upload route and have the pipeline detect an existing record and skip creation. The Quality Guardian will confirm the chosen approach.

The `finally: os.unlink(temp_path)` block stays — temp file is cleaned from disk. Supabase Storage is the persistent record.

**Bucket configuration:** Bucket name `document-originals`, private access (no public URLs). Access via service role key only.

**Completion criteria for Phase D:**
- `SkillLoader.load()` returns project-specific DB context when no flat file exists
- Test: query against a project that has a contract with `fidic_edition = '1999'` — the FIDIC edition appears in the specialist's system prompt
- Graceful degradation: query still works for a project with no contracts or parties
- Migration 008 applied — `documents.storage_path` column exists
- Test upload: document appears in `document-originals` bucket with correct path `{project_id}/{document_id}/{filename}`
- `documents.storage_path` is populated after a successful upload
- Quality Guardian sign-off

---

### Phase E — CLAUDE.md Full Rewrite
**Not a Claude Code session.**  
**Author: Strategic partner (this document's author) in collaboration with Yasser. Committed to repository manually.**

CLAUDE.md is the behavioural contract that every Claude Code session reads first. The current version is outdated in the following specific ways:

- Shows original 7-step build sequence as "COMPLETE" — does not mention Phases 1 and 2 of AGENT_PLAN
- Does not describe `base_specialist.py`, `tools.py`, `skill_loader.py`, `specialist_config.py`, `contradiction_cross.py`
- Does not describe the Layer 2 warehouse architecture (after Phase C)
- Does not describe the playbook DB auto-generation (after Phase D)
- Does not describe Supabase Storage (after Phase D)
- States 512-token chunks and 0.7 threshold (both wrong — should be 450 and 0.75)
- Does not reference `SKILLS_STANDARDS.md`
- Lists files that no longer exist (`specialist.py`, `specialists/claims.py`)
- Repository structure section is stale
- Does not state that party ID resolution is deferred

The rewrite will produce a CLAUDE.md that:
1. Accurately reflects all completed build steps (original 7 + Phases A–D of cleanup)
2. Correctly describes the full agent architecture including Phase 1 and 2 additions
3. States the Layer 2 warehouse architecture (two-table, platform-wide)
4. States the playbook mechanism (DB-driven with flat file override)
5. States file storage (Supabase Storage, `document-originals` bucket)
6. Uses correct spec values (450 tokens, 0.75 threshold)
7. References `SKILLS_STANDARDS.md` as governing document for skill authorship
8. Shows the correct, current repository structure
9. States clearly that Phase 3 of AGENT_PLAN.md (Legal & Contractual Skills) is the next active workstream
10. States clearly that party ID resolution is deferred
11. Documents the `contradiction_cross.py` stub (returns empty list; Phase 7 of AGENT_PLAN fills logic)
12. Documents the `round_number` TODO in `orchestrator.py` (deferred — DB micro-session required)

---

## 5. Agent Team and Session Assignments

### The Five Agents

| Agent | Responsibility |
|---|---|
| **DB Architect** | Supabase schema, migrations, RLS policies, triggers, RPC functions, pgvector setup |
| **Ingestion Engineer** | Docling parsing, tiktoken chunking, Gemini embedding, pgvector storage, Claude classification, metadata extraction, tier validation, CLI scripts |
| **Agent Orchestrator** | Master orchestrator, BaseSpecialist, SkillLoader, tools, retrieval, contradiction detection, synthesis, specialist configs |
| **API Engineer** | FastAPI endpoints, Pydantic schemas, JWT auth middleware, error handling, CORS, route logic |
| **Quality Guardian** | Cross-cutting review — every phase, every agent, before anything is marked complete. Flags issues as CRITICAL / HIGH / MEDIUM / LOW. Has authority to send work back for revision. |

### Phase-to-Agent Mapping

| Phase | Primary Agent(s) | QG Review |
|---|---|---|
| A — Production Fixes + Cleanup | API Engineer | Mandatory |
| B — Spec Alignment + Frontend | API Engineer | Mandatory |
| C1 — Layer 2 DB + Ingestion Script | DB Architect + Ingestion Engineer | Mandatory |
| C2 — Layer 2 Retrieval Integration | Agent Orchestrator | Mandatory |
| D — Playbook Auto-Gen + Storage | Agent Orchestrator + DB Architect + Ingestion Engineer | Mandatory |
| E — CLAUDE.md Rewrite | Strategic partner (not Claude Code) | Yasser review |

### Session Opening Protocol

Every Claude Code session must open with this declaration:

```
SESSION: [Phase letter and name]
ACTIVE AGENT: [Agent name(s)]
SCOPE: [What is being built this session — specific and bounded]
NOT IN SCOPE: [What is explicitly excluded from this session]
OPEN QUESTIONS: [Any questions requiring answers before code is written]
```

Wait for Yasser's explicit confirmation of scope before writing any code.

### Quality Guardian Review Criteria

Checks every output for:
- Dead code (functions defined but not called)
- Unused imports
- Duplicated logic
- Inconsistent naming conventions
- Silent failures (exceptions swallowed without logging)
- Missing error handling on external calls (Supabase, Gemini API, Anthropic API)
- Missing type hints on new functions
- Print statements in production code (structlog only)
- Functions doing more than one thing

---

## 6. Session Prompt Templates

These are the exact prompts to paste at the start of each Claude Code session.

### Phase A

```
You are the API Engineer for C1. Read CLAUDE.md and README.md fully before starting.

SESSION: Phase A — Production Fixes + Code Cleanup
ACTIVE AGENT: API Engineer
SCOPE: Fix CRITICAL, HIGH (dead code only), and LOW issues from the architecture review. No new architecture. No logic changes. No database changes. No frontend changes beyond what is listed.

TASKS — complete one at a time, report, wait for confirmation before next:

1. src/api/main.py — change allow_origins=["*"] to allow_origins=["https://c1intelligence.vercel.app"]

2. src/config.py — remove .pptx, .csv, .jpg, .jpeg, .png from ALLOWED_EXTENSIONS and their entries from ALLOWED_MIME_TYPES. Result: both sets contain only .pdf, .docx, .xlsx.

3. Dockerfile — change CMD uvicorn src.api.main:app --host 0.0.0.0 --port $PORT to CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port $PORT"]

4. Delete these files entirely:
   - src/agents/specialist.py
   - src/agents/specialists/claims.py
   - "The Gemini API enables Retrieval Au.md" at the repo root

5. src/config.py — delete GEMINI_POLL_INTERVAL_SECONDS and GEMINI_POLL_MAX_ATTEMPTS. Change MAX_FILE_SIZE_BYTES comment to "Maximum supported file size" (remove "Gemini File Search limit").

6. src/agents/models.py — remove raw_response_text: str = "" from RetrievalResult. src/agents/retrieval.py — remove raw_response_text="" from the RetrievalResult(...) constructor.

After all six tasks are done, call Quality Guardian. Report what was changed, run grep -r "specialist.py|claims_specialist|GEMINI_POLL|raw_response_text|allow_origins.*\*" src/ to confirm zero matches, then wait for Quality Guardian sign-off before this session is marked complete.
```

### Phase B

```
You are the API Engineer for C1. Read CLAUDE.md and README.md fully before starting.

SESSION: Phase B — Spec Alignment + Frontend Cleanup + README Alignment
ACTIVE AGENT: API Engineer
SCOPE: Align spec documents with validated code values. Clean stale Gemini-era fields from the frontend TypeScript types. Bring README.md fully current. No functional logic changes.

TASKS — complete one at a time, report, wait for confirmation before next:

1. src/config.py — add this comment after CLASSIFICATION_CONFIDENCE_THRESHOLD = 0.75:
   # 0.75 validated post-deployment — stricter than original 0.70 spec; appropriate for forensic use

2. src/ingestion/chunker.py — add this comment to the target_tokens=450 default parameter:
   # 450 validated in smoke test (2026-03-30) — supersedes original 512-token design spec

3. frontend/src/api/types.ts — remove gemini_store_name from ProjectResponse; remove gemini_file_name and gemini_document_name from DocumentResponse.

4. frontend/src/components/projects/ProjectCard.tsx — remove the project.gemini_store_name conditional check and the "Store active" badge or display text that depends on it.

5. README.md spec values — update Section 6.3: chunk target from 512 to 450, threshold from 0.7 to 0.75. Update Section 11 Technical Stack table chunking row to reflect 450-token target.

6. README.md build status — add a "Current Build Status" subsection immediately after the Live Deployment table (before Section 1). Content:
   - AGENT_PLAN.md Phases 1 and 2 complete (BaseSpecialist, multi-round orchestrator)
   - pgvector migration complete (2026-03-30)
   - Active workstream: C1_CLEANUP_PLAN.md Phases A–E
   - Next milestone after cleanup: AGENT_PLAN.md Phase 3 — Legal & Contractual Skills

7. README.md repository structure (Section 17) — update to reflect current actual state:
   - src/agents/ contents: list base_specialist.py, tools.py, skill_loader.py, specialist_config.py, domain_router.py, retrieval.py, contradiction.py, contradiction_cross.py, synthesis.py, prompts.py, audit.py, models.py, orchestrator.py, specialists/__init__.py
   - Remove specialists.py (deleted in Phase A — no longer exists)
   - Add scripts/ directory with ingest_reference.py (Phase C deliverable — note as "added in Phase C")
   - Add docs/research/ directory with legal_domain_research_summary.md
   - Add AGENT_PLAN.md, SKILLS_STANDARDS.md, C1_CLEANUP_PLAN.md to root file list
   - Add supabase/migrations/007 and 008 (note as "added in Phases C and D")

8. BUILD_LOG.md — add Phase A and Phase B completion entries.

After all tasks, run cd frontend && npm run build to confirm TypeScript compiles without errors. Then run grep -r "gemini_store_name|gemini_file_name|gemini_document_name" frontend/src/ to confirm zero matches. Call Quality Guardian.
```

### Phase C1

```
You are the DB Architect and Ingestion Engineer for C1. Read CLAUDE.md and README.md fully before starting.

SESSION: Phase C1 — Layer 2 Reference Document Architecture (Database + Ingestion Script)
ACTIVE AGENTS: DB Architect, then Ingestion Engineer
SCOPE: Build the database tables and CLI ingestion script for Layer 2 reference documents. This implements the two-layer warehouse architecture in README.md Section 6.2 and AGENT_PLAN.md Principle 3.

BACKGROUND: Layer 2 reference documents are platform-wide (not project-scoped): FIDIC conditions of contract, PMBOK, IFRS, applicable laws. They live in reference_documents and reference_chunks tables separate from the project-scoped documents and document_chunks tables. All authenticated users can SELECT from them. Only service role can INSERT/UPDATE/DELETE.

DB ARCHITECT TASKS (complete first):

Task 1: Create supabase/migrations/007_layer2_reference.sql

reference_documents table:
- id uuid PK DEFAULT gen_random_uuid()
- name text NOT NULL
- document_type text NOT NULL
- standard_body text NOT NULL
- edition_year text (nullable)
- jurisdiction text (nullable — NULL means global)
- description text (nullable)
- status text NOT NULL CHECK IN ('ACTIVE','SUPERSEDED','DRAFT')
- created_at timestamptz NOT NULL DEFAULT now()
- updated_at timestamptz NOT NULL DEFAULT now()

reference_chunks table:
- id uuid PK DEFAULT gen_random_uuid()
- reference_document_id uuid NOT NULL FK → reference_documents(id) ON DELETE CASCADE
- chunk_index integer NOT NULL
- content text NOT NULL
- embedding vector(3072) NOT NULL
- token_count integer (nullable)
- created_at timestamptz NOT NULL DEFAULT now()
[No UPDATE policy — immutable like document_chunks]

RLS: reference_documents → SELECT for authenticated, INSERT/UPDATE/DELETE service role only. reference_chunks → SELECT for authenticated, INSERT/DELETE service role only.

GIN index: CREATE INDEX ON reference_chunks USING gin (to_tsvector('english', content))

updated_at trigger on reference_documents.

RPC functions:
- search_chunks_reference_semantic(p_query_embedding vector(3072), p_top_k int DEFAULT 5) — returns id, reference_document_id, chunk_index, content, token_count, 1-(embedding<=>p_query_embedding) as similarity, ORDER BY embedding<=>p_query_embedding
- search_chunks_reference_fulltext(p_query_text text, p_top_k int DEFAULT 5) — returns id, reference_document_id, chunk_index, content, token_count, ts_rank as rank, WHERE tsvector @@ plainto_tsquery, ORDER BY rank DESC

Apply migration 007 to Supabase project bkkujtvhdbroieffhfok.

INGESTION ENGINEER TASKS (after DB Architect is done):

Task 2: Create scripts/ingest_reference.py

CLI script using argparse. Arguments: --file (required), --name (required), --document-type (required), --standard-body (required), --edition-year (optional), --jurisdiction (optional, default None), --description (optional).

Script flow:
1. Load .env with python-dotenv
2. Validate file exists, extension is .pdf/.docx/.xlsx, size > 0
3. Parse with src/ingestion/parser.py (lazy Docling import inside parse_document function — do not change the import pattern)
4. Chunk with src/ingestion/chunker.py (450 token target, 50 overlap)
5. Embed with src/ingestion/embedder.py (gemini-embedding-001, 3072 dims)
6. Insert row to reference_documents using service role client
7. Bulk insert chunks to reference_chunks
8. On failure at step 5/6/7: delete the reference_documents row (CASCADE deletes chunks), print error, exit non-zero
9. On success: print "Ingested: {name} | ID: {reference_document_id} | Chunks: {count}"

Run from repository root. Import from src/ directly.

After both tasks complete, call Quality Guardian. Then confirm by ingesting a test PDF and verifying rows appear in both tables with a Supabase MCP query.
```

### Phase C2

```
You are the Agent Orchestrator for C1. Read CLAUDE.md and README.md fully before starting.

SESSION: Phase C2 — Layer 2 Retrieval Integration
ACTIVE AGENT: Agent Orchestrator
SCOPE: Integrate Layer 2 reference chunk retrieval into the existing hybrid search pipeline. Update RetrievedChunk model and BaseSpecialist message construction.

BACKGROUND: Migration 007 is applied. reference_documents and reference_chunks tables exist. search_chunks_reference_semantic and search_chunks_reference_fulltext RPCs are available. A test document has been ingested via scripts/ingest_reference.py.

TASKS — complete in order:

1. src/agents/models.py — add is_reference: bool = False to RetrievedChunk.

2. src/agents/retrieval.py — update retrieve_chunks to perform four searches:
   a. Layer 1 semantic (existing, raises AgentError on failure)
   b. Layer 1 full-text (existing, non-fatal)
   c. Layer 2 reference semantic — supabase_client.rpc("search_chunks_reference_semantic", {"p_query_embedding": query_embedding, "p_top_k": 5}).execute() — non-fatal on failure; set is_reference=True on resulting chunks
   d. Layer 2 reference full-text — non-fatal; set is_reference=True on resulting chunks
   Layer 1 chunks deduplicate against Layer 1. Layer 2 chunks deduplicate against Layer 2. No cross-layer deduplication needed.

3. src/agents/retrieval.py — add _fetch_reference_document_metadata(supabase_client, reference_document_ids) function that queries reference_documents for name and document_type. In _build_retrieved_chunks, when is_reference=True use reference document name for document_reference and document_type for document_type.

4. src/agents/base_specialist.py — update _build_user_message to produce two sections:

--- PROJECT DOCUMENT CHUNKS (Layer 1) ---
[project chunks]

--- REFERENCE DOCUMENT CHUNKS (Layer 2 — Standards and Regulations) ---
[reference chunks]

Omit Layer 2 section entirely if no reference chunks retrieved.

After implementation, call Quality Guardian. Confirm with a test query that reference chunks appear when relevant.
```

### Phase D

```
You are the Agent Orchestrator, DB Architect, and Ingestion Engineer for C1. Read CLAUDE.md and README.md fully before starting.

SESSION: Phase D — Playbook Auto-Generation + File Storage
SCOPE: Two independent improvements in one session.

PART 1 — PLAYBOOK AUTO-GENERATION (Agent Orchestrator)

Background: SkillLoader.load() looks for playbooks/{project_id}.md. No files exist. Every query logs a warning. Fix: auto-generate project context from Supabase when no flat file exists.

Task: Update src/agents/skill_loader.py — in the Layer 2 (playbook) section of load():
1. Check if playbooks/{project_id}.md exists. If yes: read it, return it (unchanged behaviour).
2. If no flat file: import get_supabase_client from src.clients. Query:
   - contracts: SELECT id, name, contract_type, fidic_edition WHERE project_id = {project_id}
   - parties: SELECT id, name, role WHERE project_id = {project_id}
3. Build this markdown block from results:

--- PROJECT CONTEXT (auto-generated from database) ---

## Contracts on Record
[one line per contract: name, type, FIDIC edition or "edition not specified"]

## Parties on Record
[one line per party: name, role]

## FIDIC Edition
[If any contract has fidic_edition: "Governing edition: {edition}" else "FIDIC edition not confirmed — determine from contract documents"]

4. If Supabase raises an exception: log warning with get_logger, return empty string.
5. If query returns empty: return "--- PROJECT CONTEXT ---\nNo contracts or parties have been registered for this project yet."

PART 2 — FILE STORAGE (DB Architect + Ingestion Engineer)

Task 1 (DB Architect): Create supabase/migrations/008_document_storage.sql:
ALTER TABLE documents ADD COLUMN storage_path text;
Apply to Supabase project bkkujtvhdbroieffhfok.

Task 2 (Ingestion Engineer): Update src/api/routes/documents.py and src/ingestion/pipeline.py to support pre-created document records.

The goal: before calling ingest_document(), create the document record and upload the original file to Supabase Storage, then pass the pre-created document_id to the pipeline so it skips create_document_record.

Specific changes:
a. src/ingestion/pipeline.py — add optional document_id: uuid.UUID | None = None parameter to ingest_document(). If document_id is provided, skip the create_document_record step (use the provided ID). If None, call create_document_record as before.
b. src/api/routes/documents.py — before calling ingest_document():
   i. Call create_document_record(supabase_client, request) to get document_id
   ii. Upload content bytes to Supabase Storage bucket "document-originals" at path "{project_id}/{document_id}/{filename}" using supabase_client.storage.from_("document-originals").upload(path=storage_path, file=content, file_options={"content-type": <mimetype>})
   iii. If upload succeeds: supabase_client.table("documents").update({"storage_path": storage_path}).eq("id", str(document_id)).execute()
   iv. If upload fails: logger.warning with error, continue — do not block ingestion
   v. Call ingest_document(file_path=temp_path, file_size_bytes=file_size, request=request, document_id=document_id)
c. The finally: os.unlink(temp_path) block stays unchanged.

After all tasks, call Quality Guardian. Test by uploading a document and confirming storage_path is populated in the documents table and the file appears in Supabase Storage.
```

---

## 7. Technical Reference for New Sessions

### 7.1 Locked Technology Stack

| Component | Technology | Notes |
|---|---|---|
| Document parsing | Docling | **Lazy import only** — inside `parse_document()` body, never at module level |
| Chunking | tiktoken cl100k_base | 450-token target, 50-token overlap (validated) |
| Embeddings | Gemini Embeddings API gemini-embedding-001 | 3072 dims, batched at 100 |
| Vector store | pgvector on Supabase | Sequential scan — no HNSW/IVFFlat at 3072 dims |
| AI agents | Anthropic Claude API claude-sonnet-4-6 | No LangChain, no LangGraph |
| Database | Supabase PostgreSQL | Project `bkkujtvhdbroieffhfok`, EU West 1 |
| Auth | Supabase Auth | JWT validation in `src/api/auth.py` |
| Backend | Python FastAPI | `src/api/` |
| Backend hosting | Railway | Dockerfile builder, Pro plan, `sh -c` start command |
| Frontend hosting | Vercel | `frontend/` directory, Vite preset |

### 7.2 Critical Implementation Rules (Never Violate)

**Docling lazy import:** `from docling.document_converter import DocumentConverter` must live inside the function body of `parse_document()`. Module-level import causes FastAPI startup crash via opencv.

**opencv pin:** Dockerfile must uninstall and reinstall `opencv-python-headless==4.13.0.92` after all pip installs.

**pgvector cap:** pgvector 0.8.0 caps HNSW/IVFFlat at 2000 dims. Do not attempt index creation at 3072 dims.

**Chunks are immutable:** No UPDATE RLS policy on `document_chunks` or `reference_chunks`. Write-once.

**RPC for vector search:** PostgREST cannot express `<=>`. Use `supabase_client.rpc(...)` for all similarity searches.

**Audit log is immutable:** `query_log` has a trigger blocking UPDATE and DELETE. Never attempt to modify it.

**No silent failures:** Every external call has a try/except. Every failure produces a declared state (FAILED status, GREY confidence, logged warning).

**Service role key only on backend:** `SUPABASE_SERVICE_ROLE_KEY` is used server-side only. Never exposed to frontend.

### 7.3 Architecture State After All Phases

**Agent architecture (Phase 1 + 2 of AGENT_PLAN.md — complete):**
- `src/agents/base_specialist.py` — shared agentic loop
- `src/agents/tools.py` — four shared tools (`search_chunks`, `get_document`, `get_contradictions`, `get_related_documents`)
- `src/agents/skill_loader.py` — dynamic markdown loading + DB-driven playbook (after Phase D)
- `src/agents/specialist_config.py` — `SPECIALIST_CONFIGS` dict
- `src/agents/contradiction_cross.py` — **stub** returning empty list (Phase 7 of AGENT_PLAN fills this)
- `src/agents/orchestrator.py` — multi-round with `DOMAIN_TO_CONFIG_KEY` mapping

**Domain-to-config mapping (locked):**
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

**Round assignments:**
- Round 1 (parallel via ThreadPoolExecutor): `legal`, `commercial`
- Round 2 (sequential with Round 1 handoff): `claims`, `schedule`, `technical`, `governance`

**Database tables after all phases (migrations 001–008):**

| Table | Layer | Scope |
|---|---|---|
| `projects` | — | Per-user |
| `contracts` | — | Per-project |
| `parties` | — | Per-project |
| `document_types` | — | Platform-wide (read-only) |
| `documents` | Layer 1 | Per-project |
| `document_chunks` | Layer 1 | Per-project, immutable |
| `reference_documents` | Layer 2 | Platform-wide, service role managed |
| `reference_chunks` | Layer 2 | Platform-wide, immutable |
| `contradiction_flags` | — | Per-project |
| `query_log` | — | Per-project, immutable |
| `classification_queue` | — | Per-project |

### 7.4 Deferred Items (Not In This Plan)

| Item | Reason deferred |
|---|---|
| Party ID resolution | Requires parties management API — post-skills workstream |
| Approval workflows | Phase 2 feature — correctly deferred from initial build |
| User roles beyond owner model | Phase 2 feature |
| Vector index (HNSW/IVFFlat) | pgvector 0.8.0 cap at 2000 dims; await Supabase upgrade |
| `round_number` in `query_log` | DB migration required; TODO comment in `orchestrator.py`; deferred until after skills |
| Document control system integration | Phase 2 feature (Aconex, Docutrack) |
| Five user roles and authority matrix | Phase 2 feature |
| Document download endpoint | Phase D deferred item — add GET /documents/{id}/download later |

---

## 8. What Comes After Phase E

Phase 3 of AGENT_PLAN.md — Legal & Contractual Skills. Governed entirely by `SKILLS_STANDARDS.md` v1.1.

Before skill authorship begins:
1. Review and approve `docs/research/legal_domain_research_summary.md` (already exists, current as of March 2026)
2. Ingest FIDIC Red Book 1999 and FIDIC Red Book 2017 General Conditions into the warehouse via `scripts/ingest_reference.py`
3. Define five validation scenarios per `SKILLS_STANDARDS.md` Section 7

Five skill files to author in `skills/legal/`:
- `contract_assembly.md`
- `engineer_identification.md`
- `notice_and_instruction_compliance.md`
- `entitlement_basis.md`
- `key_dates_and_securities.md`

Phase 3 is knowledge authorship, not code work. Claude Code is not used for skill file content. Skills are written in markdown, reviewed by Yasser as domain expert, and deployed by dropping files into the `skills/legal/` folder.

---

## 9. Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Date | March 2026 |
| Status | Active |
| Purpose | Upload to new Claude Code chat session alongside GitHub repo |
| Related documents | README.md, CLAUDE.md (current in repo), AGENT_PLAN.md v1.3, SKILLS_STANDARDS.md v1.1, docs/research/legal_domain_research_summary.md |
| After Phase E | Archive this document. Updated CLAUDE.md replaces it as the session contract. |
