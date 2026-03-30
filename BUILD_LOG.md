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
