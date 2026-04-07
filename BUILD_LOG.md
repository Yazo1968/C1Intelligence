# C1 — Retrieval Migration Build Log

Tracks completion status and deferred issues for each migration step.

---

## Step 1 — Database Migration (DB Architect) — ✅ Complete

- Applied `004_pgvector.sql`: pgvector extension, `document_chunks` table, GIN full-text index, RLS (3 policies — SELECT, INSERT, DELETE), removed `gemini_store_name` from `projects`, removed `gemini_file_name` and `gemini_document_name` from `documents`.
- Applied `005_document_chunks_immutable.sql`: removed UPDATE policy — chunks are write-once by design.
- Vector similarity index (HNSW/IVFFlat) deferred — pgvector 0.8.0 on Supabase caps both at 2000 dimensions; sequential scan acceptable at current volumes. Future DDL documented in migration file.

---

## Step 2 — Ingestion Pipeline Rebuild (Ingestion Engineer) — ✅ Complete

**Built:**
- `src/ingestion/parser.py` — Docling-based parsing (PDF/DOCX/XLSX, OCR, section extraction)
- `src/ingestion/chunker.py` — Section-aware chunking, tiktoken cl100k_base, sentence boundaries, 50-token overlap
- `src/ingestion/embedder.py` — Gemini Embeddings API (gemini-embedding-001, 3072 dims, batched at 100)
- `src/ingestion/store.py` — Atomic Supabase pgvector storage with rollback
- `src/ingestion/pipeline.py` — Rebuilt end-to-end flow
- `src/ingestion/models.py` — Added ParsedDocument, Chunk, EmbeddedChunk dataclasses
- `requirements.txt` — Added docling>=2.0.0, tiktoken>=0.7.0

**Deleted:**
- `src/ingestion/store_manager.py`
- `src/ingestion/uploader.py`

**Deferred to Step 4 (3 LOW issues):**
1. `classifier.py` — `extract_text_preview` function is dead code (replaced by Docling parser, no longer called)
2. `status_tracker.py` — `gemini_file_name` and `gemini_document_name` parameters in `update_document_metadata` reference columns that no longer exist (harmless: pipeline no longer passes them)
3. Residual `store_manager`/`gemini_store_name` references outside ingestion layer: `agents/orchestrator.py` (imports `get_store_name_for_project`), `api/routes/projects.py` (imports `create_store_for_project`, references `gemini_store_name`), `api/schemas.py` (field `gemini_store_name`)

---

## Step 3 — Retrieval Layer Rebuild (Agent Orchestrator) — ✅ Complete

**Built:**
- `supabase/migrations/006_retrieval_functions.sql` — two PostgreSQL RPC functions (`search_chunks_semantic`, `search_chunks_fulltext`) for pgvector cosine similarity and tsvector full-text search
- `src/agents/retrieval.py` — rebuilt: query embedding via Gemini, semantic + full-text hybrid search via Supabase RPC, merge/dedup, document metadata enrichment
- `src/agents/orchestrator.py` — one line changed: `retrieve_chunks` call updated to new signature (`supabase_client, gemini_client, query_text, project_id`)

**Design decisions:**
- Full-text search failure is non-fatal (logs warning, returns semantic-only results)
- Document metadata enrichment failure is non-fatal (logs warning, returns chunks with None metadata)
- Deduplication favours semantic results over full-text when a chunk appears in both

**Known intermediate state (HIGH, expected):**
- `orchestrator.py` line 15 imports `get_store_name_for_project` from deleted `store_manager.py` — will cause `ImportError` at runtime. This is the known gap between Steps 2-4. The application is not expected to function until Step 4 removes this import. No action taken — Step 4 is explicitly responsible for this cleanup.

---

## Step 4 — Cleanup (API Engineer) — ✅ Complete

**Removed from 6 files:**
- `src/agents/orchestrator.py` — `store_manager` import, `IngestionError` import, `store_name` lookup block, renumbered steps 3-11
- `src/api/routes/projects.py` — `store_manager` import, `get_gemini_client` import, entire Gemini store creation block + rollback logic, `gemini_store_name` from response constructors
- `src/api/schemas.py` — `gemini_store_name` from `ProjectResponse`, `gemini_file_name` and `gemini_document_name` from `DocumentResponse`
- `src/api/routes/documents.py` — `gemini_file_name` and `gemini_document_name` from `_to_document_response`
- `src/ingestion/classifier.py` — `extract_text_preview` function deleted, orphaned imports removed (`json`, `genai`, `genai_types`, `GEMINI_MODEL`)
- `src/ingestion/status_tracker.py` — `gemini_file_name` and `gemini_document_name` parameters removed from `update_document_metadata`

**Verification:**
- `grep -r "store_manager|uploader|gemini_store_name|gemini_file_uri|get_store_name|file_search|FileSearch|grounding_metadata|extract_text_preview|gemini_file_name|gemini_document_name" src/` returns zero matches
- Step 3 HIGH issue resolved: `store_manager` import removed from orchestrator — application is now importable without `ImportError`
- All 3 LOW issues from Step 2 resolved

**No issues found.**

---

## Step 5 — End-to-End Smoke Test (Quality Guardian) — ✅ Complete

**Date:** 2026-03-30

**Pre-flight baseline:**
- `document_chunks` for test project: 0 rows
- `documents` for test project: 3 rows

**Tests executed:**

**Test 1 — Upload and chunk verification:** PASS
- PDF created programmatically (FIDIC Sub-Clause 8.4 Notice of Delay, 300+ words) using reportlab
- JWT obtained via Supabase Auth for `smoketest@c1.local`
- POST `/projects/f1049a59.../documents` → HTTP 201, `status=STORED`, `document_id=3612973c-9c17-4e9f-b0b5-db0da294d020`
- Classification: "Notice of Delay (FIDIC 8.5 [2017] / 8.4 [1999])", confidence=0.99, taxonomy ID 145
- `document_chunks` count: 7, all 7 with non-null embeddings, `documents.status=STORED`

**Test 2 — Natural language query:** PASS
- POST `/projects/f1049a59.../query` → HTTP 200
- `confidence=AMBER` (not GREY — content retrieved from pgvector), `response_text` non-empty (3 specialist domain findings)
- `document_ids_at_query_time` contains uploaded document UUID `3612973c-9c17-4e9f-b0b5-db0da294d020`
- Note: API response uses `document_ids_at_query_time` for source attribution (not `citations` field)

**Test 3 — Audit log entry:** PASS
- `query_log` row `id=c085a117-53a4-47fb-9fe7-11ee1dc30aaa` present, matches `audit_log_id` from API response
- `document_ids_at_query_time` contains `3612973c-9c17-4e9f-b0b5-db0da294d020`
- `confidence=AMBER` matches API response

**Test 4 — Document deletion and chunk cascade:** PASS
- Pre-deletion chunk count: 7
- `DELETE FROM documents WHERE id = '3612973c-...'` executed
- Post-deletion chunk count: 0 — FK CASCADE DELETE confirmed working

**Test 5 — GREY confidence after deletion:** PASS
- POST `/projects/f1049a59.../query` (fresh JWT) → HTTP 200
- `confidence=GREY`, response_text: "The document warehouse contains no documents relevant to this query"

**Post-test cleanup:**
- `test_notice_of_delay.pdf` deleted
- `grep -r --include="*.py" "store_manager|...|grounding_metadata" src/` → zero matches (exit code 1)
- `.pyc` binary cache files matched (expected — stale compiled artifacts), source `.py` files clean

**No issues found. Migration fully verified end-to-end.**

---

## AGENT_PLAN Phase 1 — Agent Template (Agent Orchestrator) — ✅ Complete

Built: `BaseSpecialist`, `SkillLoader`, four shared tools (`search_chunks`, `get_document`, `get_contradictions`, `get_related_documents`), `SpecialistConfig`, stub Claims specialist. Quality Guardian: 7/7 checks passed.

---

## AGENT_PLAN Phase 2 — Multi-Round Orchestrator (Agent Orchestrator) — ✅ Complete

Built: `DOMAIN_TO_CONFIG_KEY` mapping, Round 1 parallel dispatch via `ThreadPoolExecutor`, Round 2 sequential dispatch with Round 1 handoff, `contradiction_cross.py` stub, downstream functions adapted for `SpecialistFindings` model. Quality Guardian: 7/7 checks passed.

---

## C1_CLEANUP_PLAN Phase A — Production Fixes + Code Cleanup (API Engineer) — ✅ Complete

**Date:** 2026-03-31
**Active agent:** API Engineer
**Quality Guardian:** PASS on all 6 tasks individually + combined final review

**Task 1 — CORS origin fix:**
- `src/api/main.py:36` — `allow_origins=["*"]` → `allow_origins=["https://c1intelligence.vercel.app"]`
- Stale TODO comment removed

**Task 2 — Remove unsupported file types:**
- `src/config.py` — `ALLOWED_EXTENSIONS` reduced from 8 entries to 3 (`.pdf`, `.docx`, `.xlsx`)
- `src/config.py` — `ALLOWED_MIME_TYPES` reduced from 8 entries to 3 (matching extensions)

**Task 3 — Dockerfile CMD fix:**
- `Dockerfile:13` — shell form `CMD uvicorn ...` → exec form `CMD ["sh", "-c", "uvicorn ..."]`
- Aligns with `railway.json` `sh -c` wrapper convention

**Task 4 — Delete dead files:**
- `src/agents/specialist.py` — deleted (superseded by `base_specialist.py` in AGENT_PLAN Phase 1)
- `src/agents/specialists/claims.py` — deleted (superseded by config-driven specialists in AGENT_PLAN Phase 1)
- `The Gemini API enables Retrieval Au.md` — already absent at repo root (no action needed)

**Task 5 — Remove Gemini polling remnants:**
- `src/config.py:37` — comment changed from "Gemini File Search limit" to "Maximum supported file size"
- `src/config.py` — deleted `GEMINI_POLL_INTERVAL_SECONDS`, `GEMINI_POLL_MAX_ATTEMPTS`, and `# Gemini Polling` section header

**Task 6 — Remove dead field from RetrievalResult:**
- `src/agents/models.py:43` — deleted `raw_response_text: str = ""`
- `src/agents/retrieval.py:94` — deleted `raw_response_text=""` from constructor call
- Note: `models.py` and `retrieval.py` are Agent Orchestrator boundary files; changes were explicitly instructed in the Phase A task list and are not a boundary violation

**Final verification:** `grep -rE --include="*.py" "specialist\.py|claims_specialist|GEMINI_POLL|raw_response_text|allow_origins.*\*" src/` — zero matches in source files.

---

## C1_CLEANUP_PLAN Phase B — Spec Alignment + Frontend Cleanup + README Alignment (API Engineer) — ✅ Complete

**Date:** 2026-03-31
**Active agent:** API Engineer
**Quality Guardian:** PASS on all 8 tasks — self-checked after each task, independently confirmed by session coordinator

**Task 1 — Classification threshold provenance comment:**
- `src/config.py:38` — added inline comment documenting 0.75 validated post-deployment, stricter than original 0.70 spec

**Task 2 — Chunk target provenance comment:**
- `src/ingestion/chunker.py:37` — added inline comment documenting 450 validated in smoke test (2026-03-30), supersedes original 512-token spec

**Task 3 — Remove stale Gemini fields from frontend types:**
- `frontend/src/api/types.ts` — removed `gemini_store_name` from `ProjectResponse`
- `frontend/src/api/types.ts` — removed `gemini_file_name` and `gemini_document_name` from `DocumentResponse`

**Task 4 — Remove Gemini store badge from ProjectCard:**
- `frontend/src/components/projects/ProjectCard.tsx:24` — removed `{project.gemini_store_name && <span>Store active</span>}` conditional

**Task 5 — README spec values (verification only):**
- No changes needed. README already contained correct values: 450-token target (lines 139, 271, 506) and 0.75 threshold (lines 135, 509). No stale 512 or 0.70 values found. Updated in a prior session not fully captured in BUILD_LOG.

**Task 6 — README Current Build Status (verification only):**
- No changes needed. Subsection already present at lines 17–27 with correct content (AGENT_PLAN Phases 1+2 complete, pgvector migration, active workstream, next milestone).

**Task 7 — README repository structure (verification only):**
- No changes needed. Section 18 already reflects current state: correct `src/agents/` listing (no stale `specialist.py`), `scripts/ingest_reference.py`, `docs/research/`, all governing docs at root, migrations 007–008.

**Task 8 — BUILD_LOG.md entry + final verification:**
- This entry. Frontend build and grep verification results below.

**Observation:** Tasks 5, 6, and 7 were verification-only — the README was already updated during prior sessions. This confirms the README is current but also indicates those prior updates were not recorded in BUILD_LOG.md at the time.

**Final verification:** `npm run build` in `frontend/` — `tsc -b && vite build` succeeded, 97 modules transformed, zero TypeScript errors. `grep -r "gemini_store_name|gemini_file_name|gemini_document_name" frontend/src/` — zero matches.

---

## C1_CLEANUP_PLAN Phase C1 — Layer 2 Reference Document Architecture (DB Architect + Ingestion Engineer) — ✅ Complete

**Date:** 2026-03-31
**Active agents:** DB Architect (Task 1), then Ingestion Engineer (Task 2)
**Quality Guardian:** PASS on both tasks individually + combined cross-task review

**Task 1 — Migration 007 (DB Architect):**
- `supabase/migrations/007_layer2_reference.sql` — 131 lines, applied to live Supabase project `bkkujtvhdbroieffhfok`
- `reference_documents` table created: 10 columns (id, name, document_type, standard_body, edition_year, jurisdiction, description, status CHECK, created_at, updated_at)
- `reference_chunks` table created: 7 columns (id, reference_document_id FK CASCADE, chunk_index, content, embedding vector(3072), token_count, created_at) — no updated_at, immutable
- RLS enabled on both tables: 7 policies total (SELECT for authenticated on both; INSERT/UPDATE/DELETE service_role on reference_documents; INSERT/DELETE service_role on reference_chunks — no UPDATE policy, immutable)
- GIN full-text index: `idx_reference_chunks_fulltext` on `to_tsvector('english', content)`
- `updated_at` trigger: `trg_reference_documents_updated_at` reuses existing `set_updated_at()` from migration 001
- RPC function `search_chunks_reference_semantic(p_query_embedding vector(3072), p_top_k int DEFAULT 5)` — platform-wide, no project_id filter
- RPC function `search_chunks_reference_fulltext(p_query_text text, p_top_k int DEFAULT 5)` — platform-wide, no project_id filter
- Database now has 11 tables (was 9), migration version `20260331121214`

**Task 2 — CLI Ingestion Script (Ingestion Engineer):**
- `scripts/ingest_reference.py` — 202 lines, standalone CLI script
- 7 CLI arguments: `--file` (required), `--name` (required), `--document-type` (required), `--standard-body` (required), `--edition-year` (optional), `--jurisdiction` (optional), `--description` (optional)
- Reuses existing pipeline: `parse_document` (Docling, lazy import preserved), `chunk_document` (450 tokens, 50 overlap), `embed_chunks` (Gemini, 3072 dims)
- Inserts to `reference_documents` then bulk inserts to `reference_chunks` in batches of 50
- Error handling: all failure paths exit non-zero with stderr messages; rollback on partial insert (CASCADE deletes any partial chunks)
- Uses `get_supabase_client()` (service role key) — bypasses RLS for INSERT
- Success output: `"Ingested: {name} | ID: {id} | Chunks: {count}"`

**Cross-task verification:** Script INSERT column names match table schema from Task 1. FK relationship confirmed. Service role client bypasses RLS correctly for INSERT operations.

---

## C1_CLEANUP_PLAN Phase C2 — Layer 2 Retrieval Integration (Agent Orchestrator) — ✅ Complete

**Date:** 2026-03-31
**Active agent:** Agent Orchestrator
**Quality Guardian:** PASS on all 4 tasks individually + combined review

**Task 1 — Add `is_reference` field to RetrievedChunk:**
- `src/agents/models.py` — added `is_reference: bool = False` to `RetrievedChunk`
- Updated `RetrievedChunk` docstring: removed stale Gemini File Search reference, now describes Layer 1 vs Layer 2 chunks
- Updated `RetrievalResult` docstring: "Output of Gemini File Search retrieval" → "Output of pgvector hybrid retrieval (Layer 1 + Layer 2)"

**Task 2 — Extend `retrieve_chunks` to two-layer hybrid search:**
- `src/agents/retrieval.py` — `retrieve_chunks` expanded from 6-step to 8-step flow
- Added `reference_top_k: int = 5` parameter (improvement over spec: exposed rather than hardcoded)
- New function `_search_reference_semantic` — calls `search_chunks_reference_semantic` RPC, platform-wide, non-fatal
- New function `_search_reference_fulltext` — calls `search_chunks_reference_fulltext` RPC, platform-wide, non-fatal
- Layer 1 and Layer 2 merge/dedup run separately (no cross-layer dedup)
- Layer 2 chunks marked with `is_reference=True`
- Logging updated with layer-specific hit counts
- Module docstring updated to describe two-layer architecture

**Task 3 — Reference document metadata enrichment:**
- `src/agents/retrieval.py` — new function `_fetch_reference_document_metadata`
- Queries `reference_documents` table for `name` and `document_type` given unique `reference_document_id` values
- Non-fatal: logs warning and returns empty dict on failure
- `_build_retrieved_chunks` updated to accept `is_reference` parameter: Layer 2 chunks use `reference_document_id` key, `name` for reference, `document_type` for type
- File now has 10 functions (was 8)

**Task 4 — Specialist message construction with Layer 1/Layer 2 separation:**
- `src/agents/base_specialist.py` — `_build_user_message` now separates chunks into two labelled sections:
  - `--- PROJECT DOCUMENT CHUNKS (Layer 1) ---` with `[Chunk {idx} | Document: {doc_id}]` format
  - `--- REFERENCE DOCUMENT CHUNKS (Layer 2 — Standards and Regulations) ---` with `[Reference: {doc_ref} | Standard: {doc_type}]` format
- Layer 2 section omitted entirely when no reference chunks present (no empty header)
- "No chunks" message only shown when both layers are empty
- `src/agents/orchestrator.py` — chunk dict conversion updated to include `"is_reference": chunk.is_reference`

**Files changed:** `src/agents/models.py`, `src/agents/retrieval.py`, `src/agents/base_specialist.py`, `src/agents/orchestrator.py`

---

## C1_CLEANUP_PLAN Phase D — Playbook Auto-Generation + File Storage (Agent Orchestrator + DB Architect + Ingestion Engineer) — ✅ Complete

**Date:** 2026-03-31
**Active agents:** Agent Orchestrator (Task 1), DB Architect (Task 2), Ingestion Engineer (Task 3)
**Quality Guardian:** PASS on all 3 tasks individually + combined review
**Commit protocol:** Tasks committed and pushed individually after QG PASS for independent verification

**Task 1 — Playbook auto-generation from Supabase (Agent Orchestrator):**
- `src/agents/skill_loader.py` — replaced `skill_loader_playbook_missing` warning with DB-driven auto-generation
- New method `_generate_project_context`: queries `contracts` and `parties` tables, builds markdown block with Contracts on Record, Parties on Record, FIDIC Edition sections
- `get_supabase_client` lazy imported inside method body (avoids circular import)
- Graceful degradation: DB error → returns header + error message; both queries empty → returns informative empty-state message
- Flat file override preserved: `playbooks/{project_id}.md` still takes precedence if it exists
- Commit: `390b243`

**Task 2 — Migration 008 (DB Architect):**
- `supabase/migrations/008_document_storage.sql` — `ALTER TABLE documents ADD COLUMN storage_path text;`
- Migration applied directly to live Supabase project by session coordinator (confirmed: column present, text type, nullable)
- SQL file created locally to keep repo in sync with live database
- Commit: `390b243` (bundled with Task 1)

**Task 3 — File storage upload + pipeline modification (Ingestion Engineer):**
- `src/ingestion/pipeline.py` — added optional `document_id: uuid.UUID | None = None` parameter to `ingest_document()`; when provided, Step 2 (create_document_record) is skipped
- `src/api/routes/documents.py` — new flow in `upload_document`:
  1. `create_document_record()` called before pipeline to obtain `document_id`
  2. Original file uploaded to Supabase Storage bucket `document-originals` at `{project_id}/{document_id}/{filename}`
  3. `documents.storage_path` updated on successful upload
  4. Storage failure is non-fatal — logged as warning, ingestion continues
  5. `ingest_document()` called with `document_id` so pipeline skips record creation
- New imports: `ALLOWED_MIME_TYPES` from config, `create_document_record` from status_tracker
- Commit: `0fa8164`

**Independently verified by session coordinator:** Supabase column confirmed, all four files verified on GitHub main branch against spec.

---

## AGENT_PLAN Phase 3 — Legal & Contractual Skill Files (Agent Orchestrator) — ✅ Skill files complete

**Date:** 2026-04-01
**Active agent:** Agent Orchestrator
**Quality Guardian:** PASS on all five skill files individually
**Commit protocol:** Each file committed and pushed individually after QG PASS and independent verification by session coordinator

**Five skill files created in skills/legal/:**
- `contract_assembly.md` — contract document completeness, hierarchy identification, Particular Conditions amendment mapping. Commit: `965c350` (398 lines)
- `engineer_identification.md` — Engineer role identification, authority mapping, GCC split-role pattern, delegation validity, Silver Book Employer's Representative. Commit: `4d57e2c` (372 lines)
- `notice_and_instruction_compliance.md` — notice validity, instruction validity, Clause 1.3 compliance, 28-day time bar assessment, routing compliance, Qatar Article 418 caveat. Commit: `bd0e01b` (395 lines)
- `entitlement_basis.md` — FIDIC clause identification for claimed events, Particular Conditions modification check, Red/Yellow/Silver Book entitlement framework, GCC-specific entitlement patterns. Commit: `adf8cc7` (400 lines)
- `key_dates_and_securities.md` — contractual dates, EOT history, LD exposure, bond and security validity, DNP and Performance Certificate status. Commit: `b413126` (427 lines)

**All three FIDIC books (Red, Yellow, Silver) and both editions (1999, 2017) addressed in every skill file.**

**Governing documents used:** AGENT_PLAN.md v1.4, SKILLS_STANDARDS.md v1.2, legal_domain_research_summary.md v1.2

**Remaining before Phase 3 validation gate:**
- FIDIC reference document ingestion via scripts/ingest_reference.py (HIGH — deferred from Phase C1, must complete before production use)
- Five validation scenarios to be executed against the live platform

---

## FIDIC Layer 2 Ingestion — Reference Documents (Ingestion Engineer) — ✅ Complete

**Date:** 2026-04-01
**Active agent:** Ingestion Engineer

**Six FIDIC General Conditions ingested into reference_documents and reference_chunks:**
- FIDIC Red Book 1999 — 237 chunks
- FIDIC Red Book 2017 — 312 chunks
- FIDIC Yellow Book 1999 — 217 chunks
- FIDIC Yellow Book 2017 — 463 chunks
- FIDIC Silver Book 1999 — 241 chunks
- FIDIC Silver Book 2017 — 447 chunks

**Total: 6 documents, 1,917 chunks, 830,188 tokens. All ACTIVE in Supabase. Verified by session coordinator.**

**Operational note:** Layer 2 ingestion via scripts/ingest_reference.py must be run on Railway or a machine with sufficient RAM. Local execution on a standard Windows machine fails due to Docling memory requirements on large PDFs. Docling remains the sole parser across Layer 1 and Layer 2.

**HIGH deferred item from Phase C1 — now closed.**

---

## Session — Query Pipeline Improvements (Strategic Planning) — ✅ Session Complete

**Date:** 2026-04-02
**Work completed:**
- Async document upload with status polling implemented — commit `4c52238`
- Markdown rendering for specialist findings — commit `1647cc3`
- query_jobs migration 009 applied to live Supabase (table live, RLS enabled)
- C1_QUERY_IMPROVEMENT_PLAN.md produced — 4 phases, 10 tasks
- PyMuPDF revert (Docling sole parser restored) — commit `6491e07`
- FIDIC Layer 2 ingestion complete — 6 books, 1917 chunks, verified in Supabase
- Phase 3 Legal skill files complete — 5 files, all verified

**Note:** C1_QUERY_IMPROVEMENT_PLAN.md Phases 1 and 2 now fully complete (Tasks 1.1–1.5, 2.1–2.4). C1_MULTIAGENT_ARCHITECTURE_PLAN.md Phase A complete. Next: Phase B (skill migration and new SME skill files) per C1_MULTIAGENT_ARCHITECTURE_PLAN.md.

---

## C1_MULTIAGENT_ARCHITECTURE_PLAN Phase A — Three-Tier Architecture Foundation — ✅ Complete

**Date:** 2026-04-02
**Active agent:** Agent Orchestrator (all tasks)
**Quality Guardian:** PASS on all five tasks individually + Phase A validation query
**Governing document:** docs/C1_MULTIAGENT_ARCHITECTURE_PLAN.md v1.0

**Task A.1 — Domain reclassification.** Commit: `a6512e7`
- `tier` field added to `SpecialistConfig` (tier=1 = orchestrator, tier=2 = SME)
- `governance` domain removed entirely from all data structures
- `financial` domain added as new Tier 1 orchestrator
- `legal` and `commercial` reclassified as tier=1; `claims`, `schedule`, `technical` reclassified as tier=2
- `DOMAIN_FINANCIAL_REPORTING` constant added to prompts.py; governance constant deleted
- `DOMAIN_DISPLAY_NAMES` updated; governance specialist system prompt removed (dead code)
- `DOMAIN_ROUTER_SYSTEM_PROMPT` updated — governance description replaced with financial
- `skills/` restructured: `skills/legal/` → `skills/smes/legal/` (5 skill files); `skills/orchestrators/` created with legal, commercial, financial subdirs; `skills/smes/` created with claims, schedule, technical subdirs; `skills/governance/` deleted
- `skill_loader.py` updated: three-path resolution — orchestrators/ → smes/ → legacy fallback

**Task A.2 — SME invocation tool.** Commit: `b4c9a09`
- `invoke_sme` executor added to `tools.py`
- `ORCHESTRATOR_TOOL_DEFINITIONS` exported — extends `TOOL_DEFINITIONS` with `invoke_sme`
- `invoke_sme` validates tier=2 before proceeding; runs retrieval for targeted question; instantiates SME via `BaseSpecialist`; returns structured findings
- All imports inside executor are lazy (avoids circular import with `base_specialist.py`)

**Task A.3 — BaseOrchestrator base class.** Commit: `891e4a7`
- `src/agents/base_orchestrator.py` created (388 lines)
- Tier=1 validation on instantiation — raises `ValueError` for tier=2 configs
- Uses `ORCHESTRATOR_TOOL_DEFINITIONS` (includes `invoke_sme`)
- Loads directive files via `SkillLoader` (resolves to `skills/orchestrators/{domain}/`)
- System prompt frames agent as senior professional lead, not document analyst
- `run()` signature identical to `BaseSpecialist.run()` for uniform dispatch
- Returns `SpecialistFindings` — no new model introduced

**Task A.4 — Directive files for Legal and Commercial orchestrators.** Commit: `ad18d55`
- `skills/orchestrators/legal/directive.md` created (92 lines) — senior legal counsel role, 6 direct analysis areas, 3 SME delegation authorities, 8-section output structure
- `skills/orchestrators/commercial/directive.md` created (88 lines) — senior QS/commercial manager role, 5 direct analysis areas, 3 SME delegation authorities, 7-section output structure
- All five Legal SME skill files in `skills/smes/legal/` confirmed untouched

**Task A.5 — Main orchestrator routing update.** Commit: `1216704`
- `BaseOrchestrator` imported into `orchestrator.py`; used for all Round 1 dispatch
- Tier=1 routing: domains with `config.tier == 1` go to `round_1_keys`; tier=2 domains silently skipped
- Round 2 SME dispatch block entirely removed — Tier 2 SMEs invoked on-demand via `invoke_sme`
- `ALL_DOMAINS_ORDERED` reduced from 6 to 3 (Tier 1 only) — output declares Legal, Commercial, Financial
- `round_2_keys` and `round_2_findings` variables eliminated

**Phase A validation query:** "What is the contract type, who are the parties, and what are the key contractual dates?"
- Result: AMBER confidence, `legal_contractual` engaged, forensic-grade output produced
- Legal orchestrator correctly identified FIDIC 1999 Yellow Book, both parties, contract reference, key dates and gaps
- Output quality equal to pre-Phase A standard — PASS

---

## C1_MULTIAGENT_ARCHITECTURE_PLAN Phase B — Skill Migration and SME Skill Files — ✅ Complete

**Date:** April 2026
**Active agent:** Yasser (domain expert) + Strategic Partner (knowledge authorship)
**Quality Guardian:** PASS on all skill files — reviewed against SKILLS_STANDARDS.md v1.3
**Governing document:** docs/C1_MULTIAGENT_ARCHITECTURE_PLAN.md v1.0

**Task B.1 — Legal SME skill files (migrate existing).**
Five existing Legal skill files confirmed in `skills/smes/legal/` from Task A.1.
All five redrafted in this phase against SKILLS_STANDARDS.md v1.3 warehouse-grounding
principles (Section 6). Commit: `8bccc5b`
- `contract_assembly.md` — FIDIC book/edition confirmation gate, Layer 1/Layer 2
  retrieval separation, CANNOT ASSESS as opening state, Documents Not Retrieved section
- `engineer_identification.md` — contract administrator identity from retrieved documents
  only, split-role confirmation from retrieved appointment documents, independence position
  from retrieved PC only
- `notice_and_instruction_compliance.md` — notice period from retrieved PC only (no defaults),
  awareness date independently verified from contemporaneous records, time bar calculation
  requires both confirmed inputs
- `entitlement_basis.md` — entitlement clause confirmed from retrieved PC before any
  assessment, event classification from retrieved PC provision only, proof elements from
  retrieved evidence not claim assertions
- `key_dates_and_securities.md` — all dates from retrieved Contract Data with source cited,
  no LD calculation without all confirmed inputs, security adequacy only if both bond amount
  and required percentage are in retrieved documents

**Task B.2 — Claims & Disputes SME skill files.** Commit: `8bccc5b`
Five skill files created in `skills/smes/claims/`:
- `notice_compliance.md` — notice period from retrieved PC, awareness date from
  contemporaneous records, time bar CANNOT CALCULATE if either input unconfirmed
- `eot_quantification.md` — entitlement event list from retrieved PC, baseline programme
  required before analysis, methodology identified from retrieved documents not assumed
- `prolongation_cost.md` — cost entitlement basis from retrieved PC, each head assessed
  against retrieved records, no formula verification without retrieved audited accounts
- `disruption.md` — causation from retrieved documents only, measured mile requires
  retrieved baseline and disrupted period records, global claim assessed against warehouse
  records
- `dispute_resolution_procedure.md` — mechanism from retrieved PC (not assumed), all
  periods from retrieved Contract Data, NOD timeliness CANNOT CONFIRM if Contract Data
  not retrieved

**Task B.3 — Schedule & Programme SME skill files.** Commit: `efdb009`
Six skill files created in `skills/smes/schedule/`:
- `programme_assessment.md` — submission requirements from retrieved Contract Data,
  acceptance status from retrieved response letter only, no default applied
- `critical_path_analysis.md` — critical path from retrieved CPM programme, float
  ownership from retrieved PC, delay impact from retrieved programme update at event date
- `delay_identification.md` — entitlement event list from retrieved PC before any
  classification, contemporaneous records required for event identification
- `acceleration.md` — directed vs constructive identified from retrieved documents,
  all three constructive acceleration conditions from retrieved documents, costs from
  retrieved records
- `time_at_large.md` — prevention principle from retrieved documents only, LD rate and
  cap from retrieved Contract Data, legal conclusion flagged as requiring legal advice
- `evm_and_cost_reporting.md` — EVM metrics extracted from retrieved reports (not
  calculated), BAC from retrieved budget document, AC cross-verified against retrieved
  payment certificates

**Task B.4 — Technical & Construction SME skill files.** Commit: `cca32c2`
Six skill files created in `skills/smes/technical/`:
- `design_liability.md` — design responsibility from retrieved PC and confirmed book
  type, standard of care from retrieved PC, decennial liability flagged only where
  governing law confirmed as UAE/Saudi/Qatar AND structural defect evidenced
- `specification_compliance.md` — specification requirement from retrieved spec,
  test result from retrieved certificate, both required before compliance assessment
- `rfi_and_submittal_review.md` — response period from retrieved PC/Contract Data
  (no default), delay impact requires retrieved programme, variation risk from
  retrieved RFI response content
- `ncr_management.md` — close-out from retrieved close-out record (log status not
  sufficient), pattern from multiple retrieved instances, DNP vs construction phase
  NCRs separated by confirmed TOC date
- `site_execution.md` — factual record from retrieved site diaries, method statement
  compliance from retrieved approved method statement, resource figures from retrieved
  reports
- `testing_and_commissioning.md` — test results from retrieved certificates, TOC
  mechanism from retrieved PC, DNP calculation only from confirmed TOC date and
  confirmed DNP period

**Quality standards applied across all skill files (SKILLS_STANDARDS.md v1.3 Section 6):**
- No assumption, extrapolation, or inference of any value not in retrieved documents
- Contract-type-specific vs contract-type-agnostic items labelled in every workflow step
- Layer 1 (project documents) and Layer 2 (reference standards) explicitly distinguished
- CANNOT ASSESS is the opening state — not a fallback

---

## C1_MULTIAGENT_ARCHITECTURE_PLAN Phase C, D, E — Financial Orchestrator, Risk Mode, Layer 2 Split — ✅ Complete

**Date:** April 2026
**Governing document:** docs/C1_MULTIAGENT_ARCHITECTURE_PLAN.md v1.0

**Phase C — Financial Orchestrator:**
No code change required — financial domain was fully wired in Phase A.
Task C.2: `skills/orchestrators/financial/directive.md` created (109 lines).
Commit: `ac87569`

**Phase D — Risk Reporting Mode:**
Task D.1: `risk_mode: bool = False` added to `QueryRequest` (models.py) and
`SubmitQueryRequest` (schemas.py). `_RISK_FRAMING_DIRECTIVE` constant added to
orchestrator.py. When `risk_mode=True`, directive appended to effective query
for all Tier 1 orchestrators. `risk_mode` passed through queries.py.
Commit: `6d1fcc9`

Task D.2: Frontend risk report toggle added to `QueryInput.tsx` (amber-styled
checkbox). `submitQuery` in `queries.ts` accepts `riskMode` parameter and sends
`risk_mode` in request body. `handleQuery` in `ProjectWorkspacePage.tsx`
accepts and passes `riskMode`. Button label and loading message change when
risk mode is active. Commit: `560c962`

**Phase E — Layer 2 Split and Jurisdiction Tagging:**
Task E.1: Migration 012 applied to Supabase — `layer_type TEXT NOT NULL DEFAULT '2b'`
column added to `reference_documents` with CHECK constraint `('2a', '2b')`.
All 6 existing FIDIC books tagged `layer_type = '2b'`, `jurisdiction = 'international'`.
Column comments added.

Task E.2: `scripts/ingest_reference.py` updated — `--layer` flag added
(choices: `2a`, `2b`, default: `2b`), `layer_type: args.layer` written to
`reference_documents` insert dict, docstring and `--jurisdiction` help updated.
Commit: `047ac02`

Task E.3: Migration 013 applied to Supabase — both reference search RPC
functions (`search_chunks_reference_semantic`, `search_chunks_reference_fulltext`)
replaced with updated versions accepting optional `p_layer_type TEXT DEFAULT NULL`
and `p_jurisdiction TEXT DEFAULT NULL` parameters. NULL = no filter (backward
compatible). Non-NULL filters to the specified layer/jurisdiction. Both functions
also now return `name`, `document_type`, `layer_type`, `jurisdiction` columns.
Migration SQL file created at `supabase/migrations/013_layer2_retrieval_filters.sql`.
Commit: `d09076d`

**Supabase state after Phase E:** 10 tracked migrations (004–013),
13 total migrations applied (001–013). 4 RPC functions. 6 FIDIC reference
documents, all Layer 2b international.

---

## C1_MULTIAGENT_ARCHITECTURE_PLAN Phase F + C1_QUERY_IMPROVEMENT_PLAN Phases 3 & 4 — ✅ Complete

**Date:** April 2026
**Governing documents:** docs/C1_MULTIAGENT_ARCHITECTURE_PLAN.md v1.0,
docs/C1_QUERY_IMPROVEMENT_PLAN.md v1.3

**Task 3.1 — Round 0 backend classifier.** Commit: `0a9886f`
`assess_query()` function added to `orchestrator.py`. Retrieval + single Claude
API call returns `Round0Assessment` with PRIMARY/RELEVANT/NOT_APPLICABLE per
domain and a 2-sentence executive brief. Synchronous `POST /query/assess`
endpoint added. `DomainRecommendation` and `Round0Assessment` dataclasses added
to `models.py`. `DomainRecommendationSchema` and `Round0AssessmentResponse`
added to `schemas.py`. Graceful fallback on Claude API failure.

**Task 3.2 — Round 0 frontend.** Commit: `9373fd4`
`assessQuery()` in `queries.ts`. `Round0Card.tsx` (147 lines): executive brief,
document list, domain grid with relevance badges, checkbox selection, Run
Analysis and Run All buttons. `ProjectWorkspacePage.tsx` updated to two-step
flow: `handleAssess` → Round0Card → `handleQuery`. Query text and risk mode
stored in refs for Round0Card callbacks. `submitQuery` updated to accept
optional `domains` parameter.

**Task 3.3 — Domain filter in full query.** Commit: `7c3faf1`
`domains: list[str] | None = None` added to `QueryRequest` and
`SubmitQueryRequest`. Domain filter applied in `process_query` before
round_1_keys dispatch. Backward compatible — absent = all domains activated.

**Task 4.1 — Prompt caching.** Commit: `7c3faf1`
`cache_control: ephemeral` applied to system prompt in `messages.create` in
both `base_orchestrator.py` and `base_specialist.py`. 90% input token cost
saving on cache hits. Cache lifetime: 5 minutes.

**Both active workstreams are now fully complete:**
- C1_QUERY_IMPROVEMENT_PLAN.md v1.3: all four phases complete (Tasks 1.1–4.1)
- C1_MULTIAGENT_ARCHITECTURE_PLAN.md v1.0: all six phases complete (A–F)

**Final platform state:**
- 3 Tier 1 orchestrators: Legal, Commercial, Financial (with directive files)
- 4 Tier 2 SME domains: Legal (5 skills), Claims (5 skills), Schedule (6 skills),
  Technical (6 skills) — 22 skill files total
- 13 Supabase migrations applied (001–013)
- Layer 2 warehouse: 6 FIDIC books, 1,917 chunks, tagged 2b/international
- Risk mode available on all queries
- Round 0 triage on every query submission
- Prompt caching on all agent calls

---

## Session — Item 1, 3, 4 from C1_REMAINING_WORK.md — ✅ Complete

**Date:** 2026-04-03
**Active agents:** DB Architect (migration SQL file), Agent Orchestrator (Python + markdown), Quality Guardian
**Quality Guardian:** PASS on all three items individually + independent verification by session coordinator

**Item 1 — `round_number` column in `query_log`:**
- `supabase/migrations/014_query_log_round_number.sql` — created and committed
- Migration 014 applied to live Supabase project `bkkujtvhdbroieffhfok` by session coordinator
- `src/agents/audit.py` — `round_number: int | None = None` added as final parameter to `write_audit_log`; `"round_number": round_number` added to row dict
- `src/agents/orchestrator.py` — three-line TODO comment removed; `round_number_to_log` computed in `process_query` and passed to both `write_audit_log` call sites; `_grey_response` passes `round_number=None`
- Commit: feat: Migration 014 — round_number column in query_log

**Item 3 — Duplicate Executive Summary header:**
- `src/agents/orchestrator.py` — removed `sections.append("## Executive Summary")` and trailing empty string from `build_response_text`. The generated summary from `_generate_executive_summary()` provides its own header. `_grey_response` header untouched (correct — plain text, not generated).
- Commit: fix: remove duplicate Executive Summary header in build_response_text

**Item 4 — SKILLS_STANDARDS.md Section 7 internal numbering:**
- `docs/SKILLS_STANDARDS.md` — sub-sections 6.1–6.5 within Section 7 renamed to 7.1–7.5. Version bumped from 1.3 to 1.4. Document Control table updated.
- Commit: docs: SKILLS_STANDARDS.md v1.4 — fix Section 7 internal numbering

**Database state after this session:** 14 migrations applied (001–014).
**C1_REMAINING_WORK.md after this session:** Items 1, 3, 4 removed. Item 2 (document download endpoint) is the next HIGH priority actionable item.

## Deferred Items

| Item | Reason deferred | When to address |
|---|---|---|
| Vector similarity index (HNSW/IVFFlat) | pgvector 0.8.0 caps at 2000 dims; embeddings are 3072 dims | When Supabase upgrades pgvector |
| Party ID resolution (`issuing_party_id`, `receiving_party_id` always NULL) | Requires parties management API that does not exist | Post-skills workstream |
| `round_number` column in `query_log` | DB migration required; TODO in `orchestrator.py` | DB Architect micro-session after skills complete |
| Cross-specialist contradiction detection | `contradiction_cross.py` returns `[]` | AGENT_PLAN Phase 7 |

---

## Session — Items 11, 12 from C1_REMAINING_WORK.md — ✅ Complete

**Date:** 2026-04-03
**Active agents:** API Engineer (Item 11), DB Architect (Item 12), Quality Guardian
**Quality Guardian:** PASS on both commits

**Item 11 — CORS tightening:**
- `src/api/main.py` — allow_methods changed from ["*"] to ["GET", "POST", "DELETE", "OPTIONS"]; allow_headers changed from ["*"] to ["Authorization", "Content-Type"]
- Commit: `cb21aec`

**Item 12 — RPC function search_path:**
- `supabase/migrations/015_rpc_search_path.sql` — created; five functions rewritten with fixed search_path
- Applied to live Supabase by session coordinator (version 20260403083419)
- Note: set_updated_at, search_chunks_fulltext, search_chunks_reference_fulltext use SET search_path = public. search_chunks_semantic and search_chunks_reference_semantic use SET search_path = public, extensions (pgvector <=> operator lives in extensions schema on Supabase — applying public-only caused operator resolution failure on first attempt)
- Commit: `f035f63` (SQL file); corrected and applied to Supabase by session coordinator

**Database state after this session:** 15 migrations applied (001–015).
**C1_REMAINING_WORK.md after this session:** Security hardening category empty and removed. Remaining: Category 1 (pgvector index, blocked on Supabase upgrade) and Category 2 (Phase 2 product features).

---

## Session — Item 2 from C1_REMAINING_WORK.md — ✅ Complete

**Date:** 2026-04-03
**Active agents:** API Engineer (backend + frontend), Quality Guardian
**Quality Guardian:** PASS on both commits individually + independent verification by session coordinator

**Item 2 — Document download endpoint:**
- `src/api/schemas.py` — added `DocumentDownloadResponse` (download_url, filename, expires_in)
- `src/api/routes/documents.py` — added `GET /{document_id}/download` endpoint; registered before `GET /{document_id}` to prevent FastAPI path parameter capture; generates 60-second signed URL from `document-originals` Supabase Storage bucket; returns 404 if `storage_path` is NULL
- `frontend/src/api/types.ts` — added `DocumentDownloadResponse` interface
- `frontend/src/api/documents.ts` — added `getDocumentDownloadUrl` function
- `frontend/src/components/documents/DocumentTable.tsx` — added `DownloadButton` component with loading state; download column added to table; button renders only for `status === 'STORED'` rows; opens signed URL in new tab
- Commits: `1fa4f33` (backend), `c786183` (frontend)

**C1_REMAINING_WORK.md after this session:** Category 1 (Actionable Now) is empty.
Next priority: Category 3 security hardening (Items 11, 12) or Category 2 Phase 2 features — requires Yasser's direction.
| Approval workflows | Phase 2 feature | Phase 2 |
| Five user roles and authority matrix | Phase 2 feature | Phase 2 |

---

## Session — Feature 1: Cross-Specialist Contradiction Detection — ✅ Complete

**Date:** 2026-04-03
**Active agent:** Agent Orchestrator, Quality Guardian
**Quality Guardian:** PASS — independently verified by session coordinator

**What was built:**
- `src/agents/contradiction_cross.py` — replaced stub with full Claude-based
  implementation. Uses `CONTRADICTION_TOOL` imported from `contradiction.py`
  (not redefined). System prompt focused on dates, values, and factual positions
  across domain specialists. Returns `list[ContradictionFlag]`. Non-fatal on
  any API or parsing error.
- `src/agents/orchestrator.py` — two changes: `anthropic_client` now passed
  to `cross_specialist_contradiction_pass`; results merged into `contradictions`
  immediately after `detect_contradictions` so that write-back, confidence
  scoring, and response assembly all handle cross-specialist flags without
  further changes.
- Commit: `72e1608`

**Known limitation:** Cross-specialist contradiction flags use domain names
as document references (e.g. "LEGAL", "SCHEDULE"). The DB write-back in
`write_contradiction_flags` resolves references to document UUIDs — this
resolution will fail gracefully for domain-name references and log a warning.
The contradiction still surfaces correctly in the query response text.

**C1_REMAINING_WORK.md after this session:** Item 7 removed. Remaining Phase 2
items: Party ID resolution, approval workflows, user roles, document control
integration.

---

## Session — UI Housekeeping: domain labels + Contradictions tab fix — ✅ Complete

**Date:** 2026-04-03
**Active agent:** API Engineer, Quality Guardian
**Quality Guardian:** PASS on both commits + independently verified

**Commit 1 — Domain label map corrections (`20ea713`):**
- `SpecialistFindingCard.tsx` — domainLabels replaced with config-key-based
  map (legal/commercial/financial). Previous map used full domain names which
  never matched SpecialistFindings.domain. All stale entries removed.
- `QueryResponse.tsx` — domainLabels corrected for domains_engaged display.
  Added missing financial_reporting entry. Removed stale schedule_programme,
  technical_design, claims_disputes, governance_compliance.
- `AuditLogTable.tsx` — same correction. Three entries only.

**Commit 2 — Contradictions tab fix (`f38e61a`):**
- `ContradictionAlert.tsx` — value boxes now conditional on hasValues.
  When value_a/value_b are empty, shows document references as plain labels
  with the description. Handles both query-time contradictions (with values)
  and stored flags (description only).
- `ProjectWorkspacePage.tsx` — Contradictions tab now resolves document_a_id
  and document_b_id to filenames using the documents array already in state.
  Falls back to first 8 chars of UUID if document not found.
| Document control system integration | Phase 2 feature | Phase 2 |
| Document download endpoint | Deferred from Phase D | After Phase D |
| CORS `allow_methods`/`allow_headers` tightening | `allow_methods=["*"]` and `allow_headers=["*"]` in `src/api/main.py` are acceptable for a known frontend but candidates for tightening | Future hardening session (not Phase A scope) |
| `function_search_path_mutable` on all RPC functions | Pre-existing Supabase security advisory affecting all 7 RPC functions across migrations 001, 006, and 007 — not introduced by Phase C1 | Future hardening session |

---

## Session — Migration 016: HNSW indexes + Feature 1 cross-specialist contradiction — ✅ Complete

**Date:** 2026-04-03
**Active agents:** DB Architect (Migration 016), Agent Orchestrator (Feature 1), Quality Guardian
**Quality Guardian:** PASS on all items — independently verified by session coordinator

**Feature 1 — Cross-specialist contradiction detection:**
- `src/agents/contradiction_cross.py` — stub replaced with full Claude-based
  implementation. Imports CONTRADICTION_TOOL from contradiction.py. System
  prompt focused on dates, values, and factual positions across specialists.
  Returns list[ContradictionFlag] in all code paths. Non-fatal on error.
- `src/agents/orchestrator.py` — anthropic_client passed to
  cross_specialist_contradiction_pass; results merged into contradictions
  list before confidence scoring and response assembly.
- Known limitation: cross-specialist flags use domain names as document
  references — DB write-back skips these gracefully with a warning log.
  Flags still surface correctly in the query response.
- Commit: `72e1608`

**Migration 016 — HNSW halfvec indexes:**
- `supabase/migrations/016_hnsw_halfvec_indexes.sql` — HNSW indexes on
  document_chunks and reference_chunks using halfvec(3072) cast.
  halfvec type supports up to 4,000 dimensions, covering our 3,072-dimension
  embeddings. Cosine distance matches the <=> operator in all four retrieval
  RPC functions. Both indexes confirmed live in Supabase.
- Applied to live Supabase by session coordinator (version 20260403093332).
- This resolves the previously documented external dependency. The halfvec
  cast technique was present in Supabase documentation all along — it was
  incorrectly documented as blocked in earlier sessions. That was an error
  by the session coordinator.
- Commit: `55e4967`

**Note — check_pgvector_version migration:**
- A migration named check_pgvector_version (version 20260403084941) is
  tracked in Supabase. This was created accidentally when apply_migration
  was used instead of execute_sql to check the pgvector version. The
  migration body is a SELECT statement and has no effect on the schema.
  It is harmless but is recorded here for completeness.

**Database state after this session:** 16 migrations applied (001–016).
HNSW indexes live on both chunk tables. C1 is now enterprise-scale ready
for retrieval performance.

**C1_REMAINING_WORK.md after this session:** External dependency category
removed entirely. One category remains: Phase 2 product features (4 items).
| Duplicate `## Executive Summary` header in response output | `build_response_text` emits `## Executive Summary` then the generated summary begins with `## EXECUTIVE SUMMARY` — cosmetic double header | LOW — housekeeping session |
| Section 7 (Claims domain) internal sub-section numbering | SKILLS_STANDARDS.md v1.3 — Section 7 (renamed from 6) internal sub-sections still numbered 6.1–6.5 | LOW — cosmetic; fix in next SKILLS_STANDARDS update |

---

## Session — Platform Identity Overhaul — ✅ Complete

**Date:** 2026-04-03

CLAUDE.md rewritten v1.0 — universal construction intelligence platform,
three-layer warehouse (Layer 1/2a/2b), grounding principle, pointer to
C1_MASTER_PLAN.md.

docs/C1_MASTER_PLAN.md created v1.0 — six phases: (1) prompts.py
form-agnostic rewrite, (2) c1-skill-authoring rebuilt, (3) SKILLS_STANDARDS.md
lightweight, (4) all 20 skill files rebuild, (5) code enforcement,
(6) product features.

skills/c1-skill-authoring/ rebuilt — five files, three-layer warehouse,
fully form-agnostic. warehouse_retrieval.md replaces fidic_framework.md.

docs/SKILLS_STANDARDS.md v2.0 — lightweight 104 lines, four
warehouse-grounding principles, operational guidance in skill.

Archived: C1_INTELLIGENCE_GROUNDING_PLAN.md, C1_PHASE2_PLAN.md,
C1_REMAINING_WORK.md.

Next session: Phase 1 — src/agents/prompts.py form-agnostic rewrite.

---

## Session — Phase 1: Form-Agnostic System Prompts — ✅ Complete

**Date:** 2026-04-03
**Commit:** 69966661f922c4ecf839a12d334a3864bd29a8e8

src/agents/prompts.py rewritten — all hardcoded FIDIC clause numbers,
edition cross-references (1999/2017), GCC market framing, and FIDIC AWARENESS
blocks removed from all specialist prompts. Replaced with three-layer retrieval
protocol (Layer 2b → Layer 1 → Layer 2a) and CANNOT CONFIRM rules for when
retrieval fails. Evidence Declaration block mandated in _SPECIALIST_RULES Rule 7.
DOMAIN_FINANCIAL_REPORTING specialist prompt added (was absent in previous file).
CONTRADICTION_SYSTEM_PROMPT updated to universal platform identity.
Domain constants (lines 1–33) preserved unchanged.

QG PASS: 9 residual FIDIC/GCC patterns absent, 4 required patterns present,
verified via GitHub API on committed file.

Next session: Phase 2 — rebuild skills/c1-skill-authoring/ (5 files,
three-layer warehouse, form-agnostic). Prerequisite: Phase 1 ✅

---

## Session — Phase 4: Skill Files Rebuild (17 of 20) — ✅ Partial Complete

**Date:** 2026-04-03

Phase 4 executed across one long session. 17 of 20 skill files rebuilt —
all orchestrator directives and three SME domains complete. Technical SME
domain (6 files) written and QG-passed but not committed due to outputs
mount I/O failure at session end. Technical files to be committed in next
session.

Orchestrator directives (3): 7514a85, 00f62b6, bf10e37
Legal SME (5): 2889d9d, 62982ea, 90e10c5, d002235, a732250
Claims SME (5): af46b5b, fd800e2, 8351df6, 4f1f0f8, 93c6b77
Schedule SME (6): 99ca558, b054492, 2243719, fad4065, 8452a1d, d1b7bb1

Technical SME (6) — NOT YET COMMITTED:
skills/smes/technical/design_liability.md
skills/smes/technical/testing_and_commissioning.md
skills/smes/technical/specification_compliance.md
skills/smes/technical/site_execution.md
skills/smes/technical/ncr_management.md
skills/smes/technical/rfi_and_submittal_review.md

All rebuilt: FIDIC removed, GCC removed, Evidence Declaration added,
layer_type Layer 2b retrieval, CANNOT CONFIRM rules, STANDARD FORM NOT
IN WAREHOUSE consistent throughout.

Next session: rebuild 6 Technical SME files and commit.

## Session — April 2026 (Phase 4 Technical SME — continued)

Task: Rebuild skills/smes/technical/design_liability.md — form-agnostic
Status: COMPLETE
Commit: d36b660
Changes: Replaced Red/Yellow/Silver Book design responsibility workflow with retrieve-first framework (Layer 2b + amendment document). Removed all FIDIC clause numbers. Replaced decennial liability GCC framing with jurisdiction-agnostic statutory structural liability (applicable law from Layer 2b). Evidence Declaration block added to output format.

Task: Rebuild skills/smes/technical/ncr_management.md — form-agnostic
Status: COMPLETE
Commit: ceb0327
Changes: Removed FIDIC Clause 7 and 11 references. Replaced "DNP" with "defects liability period" throughout. Replaced "Taking-Over Certificate" with "completion certificate". Layer 2b subject-matter searches. Evidence Declaration block added.

Task: Rebuild skills/smes/technical/rfi_and_submittal_review.md — form-agnostic
Status: COMPLETE
Commit: 643ddf1
Changes: Removed FIDIC Clause 1.9 reference. Employer risk event entitlement is now Layer 2b retrieval. Evidence Declaration block added.

Task: Rebuild skills/smes/technical/site_execution.md — form-agnostic
Status: COMPLETE
Commit: d38e42e
Changes: Removed FIDIC Clause 4.1 reference. Weather exceptionality note added (requires Layer 2b — skill states factual record only). Evidence Declaration block added.

Task: Rebuild skills/smes/technical/specification_compliance.md — form-agnostic
Status: COMPLETE
Commit: 83240db
Changes: Removed FIDIC Clauses 7 and 11. Layer 2b subject-matter searches for quality, testing, and defects. Evidence Declaration block added.

Task: Rebuild skills/smes/technical/testing_and_commissioning.md — form-agnostic
Status: COMPLETE
Commit: 5fd82b4
Changes: "Taking-Over Certificate" → "completion certificate". "DNP" → "defects liability period". "Performance Certificate" → "final certificate". Clauses 9, 10, 11 removed, replaced with Layer 2b subject-matter searches. GCC authority inspections section removed. Evidence Declaration block added.

## Session — April 2026 (Phase 5 — Code Enforcement)

Task: Add EvidenceRecord model to src/agents/models.py
Status: COMPLETE
Commit: d1252e6
Changes: LayerRetrievalStatus enum (RETRIEVED/NOT_RETRIEVED/PARTIAL). EvidenceRecord model tracking Layer 2b/2a/1 retrieval status, sources, and provisions_cannot_confirm list. evidence_record field added to SpecialistFindings.

Task: Add load_grounding_schema() to src/agents/skill_loader.py
Status: COMPLETE
Commit: 1aafbcd
Changes: New method loads grounding_schema.json from skill group directory using same resolution order as load(). Returns parsed JSON or None. Non-fatal on absence.

Task: Create grounding_schema.json for all skill groups
Status: COMPLETE
Commit: dcef002
Changes: 7 JSON files created — skills/orchestrators/legal/, commercial/, financial/ and skills/smes/legal/, claims/, schedule/, technical/. Each defines layer2b_required, layer2a_required, layer1_amendment_document_required, and confidence cap rules. Technical SME uses AMBER (not GREY) for missing amendment document.

Task: BaseSpecialist parses Evidence Declaration and caps confidence
Status: COMPLETE
Commit: 0e69fc6
Changes: __init__ loads grounding schema. _parse_findings() passes output through _validate_evidence_and_cap_confidence(). Three new methods: _parse_evidence_declaration() (regex parser), _apply_confidence_cap() (GREY > RED > AMBER > GREEN ordering), _validate_evidence_and_cap_confidence() (orchestrates both).

Task: BaseOrchestrator parses Evidence Declaration and caps confidence
Status: COMPLETE
Commit: 41b9c84
Changes: Identical changes to base_orchestrator.py — grounding schema loaded, _parse_findings() patched, same three new methods added for Tier 1 orchestrators.

Task: Evidence Summary section in query response
Status: COMPLETE
Commit: 33d3e08
Changes: New _build_evidence_summary() function in orchestrator.py. Appended to domain assessment block in build_response_text() only when grounding gaps exist (Layer 2b not retrieved, amendment document not retrieved, or provisions_cannot_confirm populated). Returns empty string on clean responses.

Task: Migration 017 + audit.py + orchestrator.py — evidence_records persisted to query_log
Status: COMPLETE
Commit: d487ffb
Migration applied: 017_evidence_records — evidence_records JSONB column added to query_log.
Changes: audit.py write_audit_log() accepts evidence_records parameter. orchestrator.py _collect_evidence_records() helper serialises EvidenceRecord objects. Step 11 passes evidence records to audit log write. GREY path unchanged.

## Session — April 2026 (Phase 6 discussion — Compliance Feature)

Task: Compliance Feature Plan — discussion and drafting
Status: DRAFT — not approved for execution
Document: docs/C1_COMPLIANCE_FEATURE_PLAN.md v0.2

Key decisions made this session:
- Party ID resolution expanded into a full Compliance Feature covering dynamic authority matrix across all three warehouse layers (Layer 1 contractual, Layer 2a internal DOA, Layer 2b statutory)
- Authority model is an event log (not a snapshot org chart) — appointment, delegation, termination, replacement, modification, suspension events each with source document and effective date
- Authority structure is a directed graph with downward authority, upward standing, and terminus nodes
- Governance establishment is a user-triggered prerequisite before compliance-dependent queries
- Legal orchestrator renamed to Legal & Compliance — synthesises legal SME and Compliance SME outputs via AI (BaseOrchestrator), not client-side code
- engineer_identification.md retired — party and role identification moves entirely to Compliance SME
- Compliance SME has 6 skill files: party_and_role_identification, governance_establishment, signatory_validation, doa_compliance, statutory_authority_mapping, compliance_investigation
- Compliance SME feeds Legal & Compliance (primary), Commercial, Financial, and Technical orchestrators
- Governance page added to frontend with event log table, trigger button, user review workflow, and governance readiness indicator
- Org chart visualisation deferred to future phase

No code changes this session. No migrations. Plan is in discussion — execution requires product approval.

---

## Session — April 2026 (Phase 6, Compliance Feature — Tasks 6.1–6.3)

**Commits this session:**
- 1816bec — docs: CLAUDE.md corrected migration count to 17 post Phase 5
- e4c0564 — feat: migration 018 — governance_parties, governance_events, governance_run_log
- 3eae681 — feat: compliance SME skill 1/6 — party_and_role_identification
- 89d19bc — feat: compliance SME skill 2/6 — governance_establishment
- 892582c — feat: compliance SME skill 3/6 — signatory_validation
- af161dd — feat: compliance SME skill 4/6 — doa_compliance
- 9d4570a — feat: compliance SME skill 5/6 — statutory_authority_mapping
- 2303947 — feat: compliance SME skill 6/6 — compliance_investigation
- 65303d8 — feat: legal orchestrator → Legal & Compliance, Compliance SME integrated
- a919b60 — feat: commercial directive — Compliance SME invocation for party standing
- 33e9be0 — feat: financial directive — Compliance SME invocation for DOA compliance
- df3e527 — feat: retire engineer_identification.md — party ID moves to Compliance SME

**Completed:**
- Task 6.1: Migration 018 — governance_parties, governance_events, governance_run_log (18 migrations total, 15 tables)
- Task 6.2: All 6 Compliance SME skill files created under skills/smes/compliance/
- Task 6.3: Legal orchestrator renamed Legal & Compliance with full Compliance SME integration; commercial and financial directives updated; engineer_identification.md retired

**Remaining in Phase 6:**
- Task 6.4: 5 new governance API endpoints
- Task 6.5: Governance frontend page + dashboard indicator

**Database state at session close:**
- Supabase: bkkujtvhdbroieffhfok (EU West 1)
- 18 migrations applied (001–018)
- 15 tables

---

## Session — April 2026 (Phase 6, Compliance Feature — Tasks 6.4–6.5 + Session Close)

**Commits this session:**
- e6be53e — docs: CLAUDE.md corrected migration count to 18 and table count to 15
- f2fd798 — docs: C1_MASTER_PLAN.md Phase 6 Compliance Feature progress updated
- 26dbf39 — docs: BUILD_LOG.md session close Phase 6 Tasks 6.1–6.3
- 18448da — feat: governance API — 5 endpoints, schemas, CORS PATCH
- 3f64c9b — feat: governance frontend — GovernancePanel, event log, readiness indicator, sidebar tab

**Completed:**
- Task 6.4: 5 governance API endpoints (run, status, events, update event, create event); PATCH added to CORS; 6 governance schemas added to schemas.py
- Task 6.5: GovernancePanel component (readiness card, event log table, confirm/flag actions); governance.ts API client; patch method on apiClient; Governance tab in Sidebar; GovernancePage rendered in ProjectWorkspacePage

**Phase 6 — Compliance Feature: COMPLETE**
All tasks complete: 6.1 (Migration 018), 6.2 (Compliance SME skills), 6.3 (orchestrator updates), 6.4 (API), 6.5 (Frontend).

**Database state at session close:**
- Supabase: bkkujtvhdbroieffhfok (EU West 1)
- 18 migrations applied (001–018)
- 15 tables

**Platform state at session close:**
- 26 skill files (3 orchestrator directives + 23 SME skills)
- Legal orchestrator renamed Legal & Compliance
- Compliance SME: 6 skill files under skills/smes/compliance/
- Governance API: 5 endpoints live on Railway
- Governance frontend: live on Vercel

---

## Session — April 2026 (Phase 6 Compliance Remediation)

**Context:**
Post-Phase 6 quality review identified that the compliance SME skill files
and legal orchestrator directive did not conform to the mandatory c1-skill-authoring
SKILL.md structure. The commercial and financial directives were confirmed
already correct. Remediation executed as downloadable files generated by
strategic partner and committed directly.

**Commits this session:**
- cb2878d — fix: rebuild compliance SME skills — correct SKILL.md structure and Evidence Declaration format
- 5aa10b5 — fix: legal orchestrator directive — correct mandatory structure, Layer 2 Grounding Mandate, Output Structure
- b763f0a — fix: add grounding_schema.json for compliance SME — Phase 5 runtime enforcement

**Completed:**
- All 6 compliance SME skill files rebuilt to mandatory SKILL.md structure:
  correct section order (When to apply, Before you begin with Layer 1/2a/2b
  subsections, Analysis workflow, Classification and decision rules, When to
  call tools, Always flag, Output format, Domain knowledge and standards),
  correct Evidence Declaration format matching Phase 4 skills
- Legal & Compliance orchestrator directive rebuilt with all mandatory sections:
  Scope of Direct Analysis, Layer 2 Grounding Mandate, SME Delegation Authority,
  Output Structure, Output Quality Standard
- grounding_schema.json created for Compliance SME — registers layer2b_required,
  layer2a_required, governance_event_log_required, and confidence caps, connecting
  the Compliance SME to the Phase 5 runtime grounding enforcement
- Commercial and financial directives confirmed already correct — no changes required

**Findings from quality review:**
- c1-skill-authoring SKILL.md and references were not followed when skills were
  originally drafted (strategic partner drafted content directly, bypassing the
  mandatory structure)
- Substantive analytical content was correct in all files — CANNOT CONFIRM rules,
  three-layer retrieval, form-agnostic language all intact
- Structural and format issues only — now fully resolved

**Platform state at session close:**
- 26 skill files — all now fully compliant with SKILL.md mandatory structure
- All compliance SME skills: correct Evidence Declaration format
- grounding_schema.json present for all skill groups

---

## Session — April 2026 (Enhancement Plan — Strategic Analysis)

**Context:**
No code was written this session. This was a strategic analysis session
producing the Enhancement Plan for the orchestrators and SMEs — a
comprehensive review, gap analysis, and remediation plan covering all
orchestrator directives and all 26 SME skill files.

**Commits this session:**
- 0519a79 — docs: add C1_Orchestrators_and_SMEs_enhancement.md
- 190dfb8 — docs: update C1_Orchestrators_and_SMEs_enhancement.md (final v2.3)

**Work completed:**
- Independent expert examination of all 26 skill files. 8 issues identified.
- Enhancement Plan v2.3 produced: 29 tasks, Parts A–D.
  - Part A (11 tasks): remediation of 8 expert examination findings
  - Part B (9 tasks): Claims SME dissolution and backend code changes
  - Part C (2 tasks): delay assessment quality improvements
  - Part D (5 tasks): 3 new Financial SME skills — drafted by Strategic Partner

**Platform state at session close:**
- No migrations, no code changes, no skill file changes this session
- Enhancement Plan committed at docs/C1_Orchestrators_and_SMEs_enhancement.md
- 18 migrations, 15 tables, 26 skill files — all unchanged
- Production live and unchanged
- Next session: push this BUILD_LOG entry, then execute from Task A1.1

---
## Session — Part A Complete

**Date:** April 2026
**Commits:** d9c277e, a35021f, 0c5ce16, 92c37b5, 2555457, cbb7797,
f9df792, 1240d85, 2a5739d, a25d1e6, 81e6ecf

**Tasks completed:**
- A1.1: notice_and_instruction_compliance.md — retired engineer_identification references replaced
- A1.2: entitlement_basis.md — retired engineer_identification reference replaced
- A1.3: key_dates_and_securities.md — retired engineer_identification reference replaced
- A1.4: programme_assessment.md — retired engineer_identification reference replaced
- A3.1: commercial/directive.md — missing H1 title added
- A4.1: claims/README.md — stale placeholder removed, pending restructure noted
- A2.1: notice_and_instruction_compliance.md + notice_compliance.md — routing boundary clarified
- A7.1: governance_establishment.md — explicit statutory_authority_mapping invocation added
- A8.1: evm_and_cost_reporting.md — fallback path added for missing EVM reports
- A6.1: All 27 SME skill files — confidence scale reference added to output format sections
- A5.1: synthesis_directive.md — new file created, multi-orchestrator assembly directive

**Part A status:** COMPLETE — all 11 tasks verified by strategic partner via GitHub API.

**Next session:** Part B — Broken Window session. Tasks B1 through B_code3
must execute without interruption in a single session. Do not start Part B
without confirming full session availability.

**Known backlog item (not in Enhancement Plan):**
skill_loader._generate_project_context() contains a FIDIC-specific query
against the contracts table (fidic_edition column). This is a pre-existing
form-specific reference in form-agnostic code. Does not affect Enhancement
Plan. Must be resolved in a future session before C1 is used on non-FIDIC
projects.

---
## Session — Part B Complete (Broken Window Session)

**Date:** April 2026
**Commits:** 0f4ac18, 9d02c69, 3972b43, 3723c51, 8d15f28, b409b66,
489cf65, 41fb74d, c340677

**Tasks completed:**
- B1: schedule SME skills (6 files) — domain label updated to Delay and Cost Analytics SME
- B2: eot_quantification, prolongation_cost, disruption — moved to skills/smes/schedule/ via git mv, domain label updated
- B3: notice_compliance, dispute_resolution_procedure — moved to skills/smes/legal/ via git mv, domain label updated
- B4: claims/README.md — retired domain redirect README written
- B_schema: claims grounding_schema.json deleted; schedule grounding_schema.json updated to delay_and_cost_analytics_sme
- B5: all 3 orchestrator directives updated — Claims SME dissolved, Delay and Cost Analytics SME named, Legal SME absorbs notice_compliance and dispute_resolution_procedure, routing boundary documented
- B_code1: specialist_config.py — claims domain entry removed, 5 domains remain
- B_code2: prompts.py — claims_disputes constant, ALL_DOMAINS entry, domain description, and fallback removed; schedule_programme and legal_contractual descriptions updated
- B_code3: orchestrator.py — claims_disputes removed from DOMAIN_TO_CONFIG_KEY and NOT_ENGAGED_REASONS; Tier 2 SME comment updated

**Part B status:** COMPLETE — all 9 tasks verified by strategic partner via GitHub API and HTTP status checks.

**Next session:** Part C tasks C1 and C2, then Part D (Strategic Partner drafts).

---
## Session — Enhancement Plan Complete

**Date:** April 2026
**Commits this session:** 7e2a0ef, 00d4cfc, 4b3ab3d, f09ae3d,
3a31ab8, a2105b2, f1520bb, 1e230cc, e290185

**Tasks completed:**
- C1: eot_quantification — methodology appropriateness assessment
  and As-Built Critical Path added
- C2: delay_identification — forensic four-way classification added
- D1: cost_control_assessment.md — new Financial & Accounting SME skill
- D2: multi_contract_account_reconciliation.md — new skill
- D3: financial_reporting_compliance.md — new skill
- D4: grounding_schema.json — Financial & Accounting SME domain schema
- D5: specialist_config.py + financial directive — code wiring complete
- B6: CLAUDE.md — architecture updated for Enhancement Plan end state
- B7: C1_MASTER_PLAN.md — Enhancement Plan recorded as complete

**Enhancement Plan v2.3 status:** ALL 29 TASKS COMPLETE
All tasks verified by strategic partner via GitHub API.

**Platform end state:**
- 30 skill files (3 orchestrators + 1 synthesis + 26 SMEs)
- 5 active SME domains: Legal (7), Delay & Cost Analytics (9),
  Technical (6), Compliance (6), Financial & Accounting (3)
- Claims SME dissolved
- Financial & Accounting SME added
- 18 migrations, 15 tables — unchanged
- Production live and unchanged

---
## Session — Risk Report Feature Removed

**Date:** April 2026
**Commit:** f752a47

**Change:** Risk Report feature removed without trace.
Files changed: src/agents/orchestrator.py, src/agents/models.py,
frontend/src/api/queries.ts,
frontend/src/pages/ProjectWorkspacePage.tsx (4 files, 46 deletions)

**Reason:** Feature was architecturally unsound — wrapping any
finding in a risk template regardless of materiality or relevance.
Finding classification (FLAG / INFORMATIONAL / CANNOT ASSESS) with
explicit forensic implications is already built into every skill file
and orchestrator directive. The risk framing layer was redundant and
potentially misleading for the platform's target audience.

**Platform state:** Production deployment will reflect removal on
next Railway build. No database changes. No migration required.

---
## Session — ISO 31000 Risk Register Enhancement Complete

**Date:** April 2026
**Commits:** 6bbd22e, 4008575, 108ed51, bb52d35, 12c302d, 43fe125

**Changes:**
- R1: grounding_protocol.md — ISO 31000:2018 FLAGS standard defined (orchestrator vs SME level). output_formats.md — full nine-field risk register entry format, Risk Rating Matrix, Status definitions, Likelihood and Residual Rating derivation rules added
- R2: output_formats.md — orchestrator directive output template FLAGS Summary replaced with ISO 31000 Risk Register template
- R3: legal/directive.md — FLAGS output updated to ISO 31000 Risk Register format
- R4: commercial/directive.md — FLAGS output updated to ISO 31000 Risk Register format
- R5: financial/directive.md — FLAGS output updated to ISO 31000 Risk Register format
- R6: synthesis_directive.md — Section 7 Consolidated FLAGS replaced with ISO 31000 Consolidated Risk Register with CRITICAL-first ranking, compound risk identification, and COMPOUND notation

**Risk register fields per entry:** Risk ID, Category, Description, Cause, Consequence (H/M/L), Likelihood (H/M/L or CANNOT ASSESS), Inherent Rating (CRITICAL/HIGH/MEDIUM/LOW), Existing Controls, Treatment (AVOID/REDUCE/TRANSFER/ACCEPT), Residual Rating, Status (OPEN/REALIZED/TREATED/EXPIRED/ACCEPTED)

**Standard:** ISO 31000:2018 — internationally recognised risk management framework used by construction, audit, and lender communities

**No new agents. No new orchestrators. No extra API calls.**
Six skill/reference files changed. SME skill files unchanged.
Database unchanged. No migration required.

---
## Session — ISO 31000 Risk Register Enhancement Complete

**Date:** April 2026
**Commits:** 6bbd22e, 4008575, 108ed51, bb52d35, 12c302d, 43fe125, e935a0e

**Changes:**
- R1: grounding_protocol.md + output_formats.md — ISO 31000:2018 FLAGS standard defined. Nine-field risk register entry format, Risk Rating Matrix, Status definitions, Likelihood and Residual Rating derivation rules
- R2: output_formats.md — orchestrator template FLAGS Summary replaced with ISO 31000 Risk Register template
- R3: legal/directive.md — FLAGS output updated to ISO 31000 Risk Register format
- R4: commercial/directive.md — FLAGS output updated to ISO 31000 Risk Register format
- R5: financial/directive.md — FLAGS output updated to ISO 31000 Risk Register format
- R6: synthesis_directive.md — Section 7 Consolidated FLAGS replaced with ISO 31000 Consolidated Risk Register (CRITICAL-first ranking, COMPOUND notation, deduplication, CANNOT ASSESS preservation)
- R7: README.md + CLAUDE.md — ISO 31000 output recorded, risk_mode removal noted

**Risk register fields per entry (ISO 31000:2018):**
Risk ID | Category | Description | Cause | Consequence (H/M/L) |
Likelihood (H/M/L or CANNOT ASSESS) | Inherent Rating (CRITICAL/HIGH/MEDIUM/LOW) |
Existing Controls | Treatment (AVOID/REDUCE/TRANSFER/ACCEPT) |
Residual Rating | Status (OPEN/REALIZED/TREATED/EXPIRED/ACCEPTED)

**Risk Report toggle previously removed:** f752a47 (no trace in frontend or backend)

**No new agents. No new orchestrators. No extra API calls.**
Six skill/reference files changed. SME skill files unchanged.
Database unchanged. No migration required.

---
## Session — QueryInput Risk Report Fix + ISO 31000 Risk Register Enhancement

**Date:** April 2026

**Additional fix — QueryInput.tsx (c21d9eb):**
Risk Report checkbox was missed in the original removal (f752a47).
The checkbox and all riskMode logic were implemented in
frontend/src/components/query/QueryInput.tsx — a component file
not named in the original removal task. Fix applied and deployed.
Zero risk references now in any frontend file. Verified via live
Vercel deployment dpl_Dxvfj2ZptvCsd5H7XnuwYKw2AtvK.

**Risk Register Enhancement commits:**
6bbd22e, 4008575, 108ed51, bb52d35, 12c302d, 43fe125, e935a0e

**ISO 31000:2018 Risk Register now built into all orchestrator outputs.**
No new agents. No new orchestrators. No extra API calls.
Six skill/reference files changed. SME skill files unchanged.
Database unchanged. No migration required.

---
## Session — Aggregation Integrity Plan v2.0

**Date:** April 2026

**Work completed:**
- Aggregation Integrity Plan v2.0 authored and approved
- Plan supersedes v1.0 (rejected: LLM self-reporting flaw)
- All 20 tasks defined, sequenced, and QG criteria specified
- Three stale bugs identified during direct code inspection:
  S1: base_orchestrator.py — stale "claims" SME domain reference
  S2: prompts.py — "SIX DOMAINS" should be "FIVE DOMAINS"
  S3: tools.py — invoke_sme enum still contains "claims"
- Plan committed to docs/C1_AGGREGATION_INTEGRITY_PLAN_v2.md
- No code changed this session — plan only

**Design principle:** All integrity checks read deterministic system state
(tools_called, raw_sme_outputs, sources_used, evidence_record). Zero
additional LLM calls. No new agent frameworks. No DB migrations.

**Research basis:** MAST NeurIPS 2025, AgentAuditor Feb 2026, TRiSM Mar 2026.

---

## Session — Aggregation Integrity Plan v2.0

**Date:** April 2026
**Status:** COMPLETE
**Phases:** S, 1, 2, 3, 4, 5, 6 — all 20 tasks complete

### Summary

Implemented the Aggregation Integrity Layer v2.0. All verification is
deterministic — zero additional LLM calls. No database migrations.
No frontend changes. No new agent frameworks.

### What was built

**Phase S — Stale bug fixes (3 commits):**
- S1: base_orchestrator.py — removed stale claims SME domain, added compliance and financial_sme
- S2: prompts.py — domain router corrected from SIX to FIVE domains
- S3: tools.py — invoke_sme enum updated, claims removed, compliance and financial_sme added

**Phase 1 — Deterministic routing audit (2 commits):**
- 1.1: orchestrator.py — _DOMAIN_CHUNK_KEYWORDS dict and _check_routing_coverage() added
- 1.2: orchestrator.py + models.py — routing gaps detected, surfaced in response, QueryResponse field added

**Phase 2 — Deterministic SME trace (2 commits):**
- 2.1: base_orchestrator.py — tools_called records invoke_sme:{domain}
- 2.2: orchestrator.py — _extract_sme_invocations() added and called as Step 5b.2

**Phase 3 — Raw SME output preservation (2 commits):**
- 3.1: models.py — raw_sme_outputs field added to SpecialistFindings
- 3.2: base_orchestrator.py — raw SME outputs captured in agentic loop, threaded through _parse_findings()

**Phase 4 — Evidence Auditor (3 commits):**
- 4.1: models.py — AuditResult and SMEConfidenceRecord models added, audit_result on QueryResponse
- 4.2: orchestrator.py — run_evidence_audit() implemented, zero API calls
- 4.3: orchestrator.py — Evidence Auditor integrated as Step 5b.3 in process_query() pipeline

**Phase 5 — Evidence Map (2 commits):**
- 5.1: orchestrator.py — _build_consolidated_evidence_map() added, called in build_response_text()
- 5.2: output_formats.md — Consolidated Evidence Map documented as system-generated

**Phase 6 — Governing documents (3 commits):**
- 6.1: CLAUDE.md — Aggregation Integrity Layer v2.0 documented in Architecture section
- 6.2: C1_MASTER_PLAN.md — Plan recorded as complete with full commit log
- 6.3: BUILD_LOG.md — this entry

### Commit log

S1:  7ff3d0f
S2:  96526af
S3:  d4d050f
1.1: 20254fc
1.2: 0e97785
2.1: 59735e0
2.2: 445fe05
3.1: 1da9344
3.2: 8362368
4.1: daca8d9
4.2: 8c6893b
4.3: b7aeea6
5.1: 5e0de3b
5.2: 51f5023
6.1: 18e29c7
6.2: c1400bb
6.3: this commit

### Database state
18 migrations (001–018) — unchanged. No migrations added.

### Files changed
src/agents/base_orchestrator.py
src/agents/orchestrator.py
src/agents/models.py
src/agents/prompts.py
src/agents/tools.py
skills/c1-skill-authoring/references/output_formats.md
CLAUDE.md
docs/C1_MASTER_PLAN.md
BUILD_LOG.md

---

## Session — Governance Execution Plan

**Date:** April 2026
**Status:** COMPLETE
**Tasks:** A1–E1 — all 10 tasks complete

### Summary

Implemented the governance execution layer — the missing backend processing
that makes the Establish Governance button functional. Two-phase design
with a user confirmation gate between phases, faithful to the
party_and_role_identification and governance_establishment skill files.

### What was built

**Migration 019 (applied directly via Supabase MCP):**
- governance_parties.confirmation_status column
- governance_run_log.parties_identified status + phase column

**B1 — specialist_config.py:**
- compliance SME added to SPECIALIST_CONFIGS (tier 2, max_tool_rounds 5)

**B2 — src/agents/governance_runner.py (new file):**
- run_party_identification() — Phase 1: invokes Compliance SME, parses
  ~~~json_registry block, writes to governance_parties, sets run_log to parties_identified
- run_governance_establishment() — Phase 2: fetches confirmed parties, invokes
  Compliance SME with entity registry context, parses ~~~json_events block,
  resolves party names to IDs, writes to governance_events, sets run_log to complete
- _parse_json_block(), _parse_date(), _mark_run_failed() helpers

**C1 — schemas.py:**
- GovernancePartyResponse, ConfirmPartiesRequest, GovernancePartyUpdateRequest
- parties_count added to GovernanceStatusResponse

**C2 — governance.py:**
- /run launches run_party_identification as background task
- /status detects parties_identified state

**C3 — governance.py:**
- GET /parties — list entity registry
- PATCH /parties/{party_id} — confirm or flag a party
- POST /confirm-parties — trigger Phase 2

**D1 — frontend/src/api/types.ts:**
- GovernancePartyResponse interface
- GovernanceStatusResponse updated: parties_identified status, parties_count field

**D2 — frontend/src/api/governance.ts:**
- listGovernanceParties, updateGovernanceParty, confirmParties

**D3 — frontend/src/components/governance/GovernancePanel.tsx:**
- Entity registry table with Confirm/Flag actions per party
- "Confirm Parties & Establish Governance" button (disabled until ≥1 confirmed)
- parties_identified status badge and state handling

### Commit log

Migration 019: applied directly via Supabase MCP
Plan doc:  636fd0f
B1:        8ec3ff4
B2:        c4b327f
C1:        ae32949
C2:        33d0496
C3:        491d423
D1:        0984edc
D2:        8e8706f
D3:        349b476
E1:        this commit

### Database state
20 migrations (001–019 + check_pgvector_version diagnostic). No new tables.
governance_parties: +confirmation_status column.
governance_run_log: +phase column, parties_identified status added.

### Files changed
src/agents/specialist_config.py
src/agents/governance_runner.py (new)
src/api/schemas.py
src/api/routes/governance.py
frontend/src/api/types.ts
frontend/src/api/governance.ts
frontend/src/components/governance/GovernancePanel.tsx
docs/C1_GOVERNANCE_EXECUTION_PLAN.md (new)
BUILD_LOG.md

---

## Session — Governance Authority Log Design + Prep

**Date:** April 2026
**Status:** COMPLETE

### What was done

**Design:**
- C1_GOVERNANCE_AUTHORITY_LOG_DESIGN.md written and committed (429d205)
- Three-level data model: party_identities, party_roles, authority_events
- Supporting tables: assumption_register, reconciliation_questions
- Party category taxonomy (20 categories), event type taxonomy (10 types)
- Appointment status model: Proposed / Pending / Executed
- Reconciliation interview design (8 question types)
- Compliance agent integration pattern (get_party_authority deterministic function)
- Full audit of existing codebase — bugs, dead code, design flaws documented

**Migration 021 (applied directly via Supabase MCP):**
- Created: party_identities, party_roles, authority_events,
  assumption_register, reconciliation_questions
- Dropped: governance_parties, governance_events (prototype tables)
- Updated: governance_run_log (reconciliation fields added)
- Total migrations: 21 (001-021)

**Docs cleanup:**
- Archived: C1_AGGREGATION_INTEGRITY_PLAN_v2.md,
  C1_GOVERNANCE_EXECUTION_PLAN.md, C1_Orchestrators_and_SMEs_enhancement.md
- Active docs remaining: C1_MASTER_PLAN.md, C1_GOVERNANCE_AUTHORITY_LOG_DESIGN.md

**Dead code removed:**
- src/agents/specialists/ — empty directory
- Procfile — superseded by railway.json
- risk_mode parameter — from schemas.py, queries.py

### Commit log
Design doc:     429d205
Docs archive:   2c258b5
Specialists rm: 4f82323
Procfile rm:    b7d7551
risk_mode rm:   36a8bd6
Master plan:    c42953d
BUILD_LOG:      bdad53c

---

## Session — Governance Authority Log Phases 2–7

**Date:** April 2026
**Status:** COMPLETE (Phase 8 deferred)

### What was built

**Phase 2 — governance_runner.py Phase 1 rewrite:**
PARTY_ID_QUERY replaced with three-level model prompt. run_party_identification()
writes to party_identities + party_roles instead of dropped governance_parties.
Validation for appointment_status (3 values) and governing_instrument_type (7 values).

**Phase 3a — schemas.py + governance.py API layer cleanup:**
Removed 6 stale schema classes and 6 stale endpoints from the prototype model.
Added 5 new schema classes (PartyRoleResponse, PartyIdentityResponse,
ReconciliationQuestionResponse, ReconciliationAnswerRequest, InterviewStatusResponse).
New GET /parties endpoint returns nested PartyIdentityResponse with roles.
get_governance_status reads party_identities instead of governance_parties.

**Phase 3b — Reconciliation interview backend:**
generate_interview_questions() added to governance_runner.py — 4 detection
rules produce questions for inferred parties, role conflicts, proposed roles,
and is_internal confirmation. Three interview endpoints in governance.py:
GET /interview, GET /interview/next-question, POST /interview/questions/{id}/answer.

**Phase 4a — Frontend types + API:**
types.ts and governance.ts fully replaced — stale interfaces removed, new
three-level model interfaces added. Four new API functions:
listPartyIdentities, getInterviewStatus, getNextInterviewQuestion,
submitInterviewAnswer.

**Phase 4b — GovernancePanel rewrite:**
Complete rewrite. Reconciliation interview UI: progress bar, one question
at a time, radio options, free text, skip. Identified Parties: collapsible
cards with nested roles showing appointment_status, authority_scope,
financial thresholds. Authority log placeholder for Phase 8.

**Phase 5 — governance_runner.py Phase 2 rewrite:**
run_governance_establishment() reads from party_identities + party_roles.
Writes to authority_events with full Level 3 field set. Role resolution
with exact/partial/fallback matching. 10 event types. Separate
initiated_by and authorised_by actor fields.

**Phase 6 — Compliance agent integration:**
get_party_authority() deterministic tool added to tools.py. Zero LLM calls.
Reads authority_events chronologically. Returns authority position,
appointment_status, financial_threshold, assumption warnings. Registered
in TOOL_DEFINITIONS and _TOOL_EXECUTORS.

**Phase 7 — skill_loader rewrite:**
_generate_project_context() reads party_identities + party_roles. Dead
contracts and parties table references removed. FIDIC-specific fidic_edition
reference removed. Internal/external party split. Graceful degradation.

### Commit log
Phase 2:   1250038
Phase 3a:  680638b
Phase 3b:  e28a7ed
Phase 4a:  d7aa392
Phase 4b:  5cf1262
Phase 5:   95bc27c
Phase 6:   7a8726b
Phase 7:   de445da
Phase 9:   0e4e0d7, 14dd54b, this commit

### Deferred
Phase 8 — Frontend authority event log display: placeholder in GovernancePanel.
Requires authority_events to be populated by a full governance run.
Standalone task — does not block compliance agent or query pipeline.

### Database state
21 migrations unchanged. Five new tables from Migration 021 all populated
by the new governance runner.

---

## Session — Output Quality Fixes + Governance Redesign Decision

**Date:** April 2026
**Status:** COMPLETE

### Output Quality Fixes

Six issues identified from live query output inspection and fixed:

1. Evidence Declaration block was rendering in client-facing response —
   stripped in orchestrator.py before render.
2. Consolidated Evidence Map was rendering in client-facing response —
   removed from response, retained in audit log only.
3. chunk_index references appearing in agent output — prohibition
   strengthened in base_orchestrator.py system prompt.
4. Agent narrating its own process ("I now have a complete evidential
   picture") — meta-commentary ban added to system prompt.
5. Technical layer labels (Layer 2b, Layer 1) visible to users —
   reworded to plain professional English.
6. Risk Register not appearing in assessments — MANDATORY instruction
   added to all three orchestrator directives.
7. Confidence capping to GREY when Particular Conditions embedded in
   contract — grounding schema cap changed GREY→AMBER for all three
   orchestrators.

Commits: c8b25b6, 034d9ae, 913c713, cfef971, 5938a3e

### Governance Feature Bug Fixes (v1 — now retired)

- Interview status field names misaligned backend/frontend — fixed.
- Party identity duplicates on re-run — dedup check added.
- Run log stuck on "running" after Railway timeout — finally block added.
- Authority events duplicated on double-trigger — dedup check added.
- Governance status shadowed by newer running runs — precedence logic fixed.
- Extract-events endpoint had no concurrency guard — 409 guard added.

Commits: a303b5b, c4ec7cc, 5fa1735

### Governance Redesign Decision

Root cause analysis of governance extraction failures revealed a
fundamental architectural flaw: single unbounded LLM call attempting
to read all project documents and extract all authority events at once.
Token limit failure at 208,529 tokens (200,000 limit) on a single
one-document test project. Would fail catastrophically on real projects
with hundreds of documents.

Decision: obliterate v1 implementation completely and redesign from
first principles, guided by domain expertise.

New design approved:
- Function 1: batch chunk processing to identify entity names only —
  no roles, no scope, no relationships. User confirms.
- Function 2: per-entity event extraction using fulltext search on
  confirmed entity names. Batch processing. User confirms.
- Maps exactly to how a construction lawyer builds an authority register.
- Scales to any project size — token usage bounded per call regardless
  of warehouse size.

Design document: docs/C1_GOVERNANCE_REDESIGN.md
Old design archived: docs/archive/C1_GOVERNANCE_AUTHORITY_LOG_DESIGN.md

### Platform state at session close
HEAD: 5fa1735
21 migrations (001–021)
Next: Migration 022 — governance redesign Phase 0

---

## Session: Governance Redesign — Phases 0–5 Complete
**Date:** April 2026
**Strategic Partner:** Claude (chat)
**Execution Agent:** Claude Code

### Objective
Full implementation of the Governance Feature Redesign (C1_GOVERNANCE_REDESIGN.md v2.1).
Clean-slate obliteration of v1 governance and complete rebuild.

### Phase 0 — Obliterate
- 0.1 `8a5ab2c` — Migration 022: 8 old tables dropped, 6 new tables created
  (`entity_directory_runs`, `entities`, `entity_discrepancies`,
  `event_log_runs`, `entity_events`, `event_log_questions`)
- 0.2 `6b0efa0` — Deleted `governance_runner.py` and old `governance.py` routes
- 0.3 `f5aecc4` — Cleaned `schemas.py`, `main.py`, `tools.py`, `skill_loader.py`
- 0.4 `a534ed9` — Deleted `governance_establishment.md` and `party_and_role_identification.md`
- 0.5 `1d2b4e9` — Frontend cleaned: `types.ts`, `governance.ts`, `GovernancePanel.tsx`, `ProjectWorkspacePage.tsx`

### Phase 1 — Function 1 Backend
- 1.1 `193e3d2` — `entity_extractor.py`: batch chunk processor (30 chunks/call)
- 1.2 `f104c34` — `consolidator.py`: name grouping, discrepancy detection
- 1.3 `afd1c32` — Function 1 Pydantic schemas (5 classes)
- 1.4 `85cd82f` — Function 1 API routes (7 endpoints)

### Phase 2 — Function 1 Frontend
- 2.1 `db6ab11` — Function 1 TypeScript interfaces (5)
- 2.2 `a4f0e6b` — Function 1 API client (7 functions)
- 2.3 `da36527` — GovernancePanel: States A, B-Running, B-Review, confirmed read-only

### Phase 3 — Function 2 Backend
- 3.1 `a0f20d1` — `event_extractor.py`: per-entity fulltext search + batched LLM extraction
- 3.2 `f9ffa8d` — `consolidator.py` extended: event dedup, sequencing, question generation
- 3.3 `6225e57` — Function 2 Pydantic schemas (5 classes)
- 3.4 `aa42d86` — Function 2 API routes (7 endpoints)

### Phase 4 — Function 2 Frontend
- 4.1 `dedb428` — Function 2 TypeScript interfaces (5)
- 4.2 `ce2fb20` — Function 2 API client (7 functions)
- 4.3 `663b452` — State C entity directory + EventLogPanel slide-over + QuestionCard + EventCard

### Phase 5 — Compliance Agent Integration
- 5.1 `af6ff3d` — `get_entity_authority` tool: deterministic lookup, zero LLM calls
- 5.2 `9ece625` — `_generate_project_context()` rebuilt to read confirmed `entities` table

### Bugs caught by Claude Code before writing (saved from runtime failures)
1. Task 1.1: `.eq("layer_type", "1")` — `document_chunks` has no `layer_type` column. Removed.
2. Task 1.4: `.eq("user_id", ...)` — `projects` table uses `owner_id`. Corrected.
3. Task 2.2: `as Record<string, unknown>` TS cast on required-field type rejected. Replaced with `{ ...body }` spread.
4. Task 2.3: `GovernancePanel.tsx` omitted from task 0.5 obliteration prompt despite being listed in spec Section 2.5. Added as stub.
5. Task 3.4: Local `import datetime` inside `confirm_directory()` made redundant by module-level import added in same task. Removed.

### End state
- 22 numbered migrations (001–022)
- 6 new governance tables live in Supabase
- All old governance tables, files, and frontend code obliterated
- Function 1 (Entity Directory) end-to-end: DB → 4 backend files → 14 API routes → full frontend UI
- Function 2 (Event Log) end-to-end: DB → 4 backend files → 14 API routes → full frontend UI
- `get_entity_authority` tool available to all agents
- `_generate_project_context()` injects confirmed entity names into agent system prompts
- HEAD: `9ece625`
