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

**Next session:** Task 1.1 Part 2 — API Engineer — replace _query_status
in-memory dict with Supabase query_jobs persistence in src/api/routes/queries.py

---

## Deferred Items

| Item | Reason deferred | When to address |
|---|---|---|
| Vector similarity index (HNSW/IVFFlat) | pgvector 0.8.0 caps at 2000 dims; embeddings are 3072 dims | When Supabase upgrades pgvector |
| Party ID resolution (`issuing_party_id`, `receiving_party_id` always NULL) | Requires parties management API that does not exist | Post-skills workstream |
| `round_number` column in `query_log` | DB migration required; TODO in `orchestrator.py` | DB Architect micro-session after skills complete |
| Cross-specialist contradiction detection | `contradiction_cross.py` returns `[]` | AGENT_PLAN Phase 7 |
| Approval workflows | Phase 2 feature | Phase 2 |
| Five user roles and authority matrix | Phase 2 feature | Phase 2 |
| Document control system integration | Phase 2 feature | Phase 2 |
| Document download endpoint | Deferred from Phase D | After Phase D |
| CORS `allow_methods`/`allow_headers` tightening | `allow_methods=["*"]` and `allow_headers=["*"]` in `src/api/main.py` are acceptable for a known frontend but candidates for tightening | Future hardening session (not Phase A scope) |
| **Live end-to-end test of `scripts/ingest_reference.py`** (HIGH) | Docling and Gemini API unavailable in Claude Code environment — script created and code-reviewed but not executed against a real PDF | **Must be completed before AGENT_PLAN Phase 3 goes into production** |
| `function_search_path_mutable` on all RPC functions | Pre-existing Supabase security advisory affecting all 7 RPC functions across migrations 001, 006, and 007 — not introduced by Phase C1 | Future hardening session |
