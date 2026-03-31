# C1 — Retrieval Migration Plan
## Gemini File Search → Supabase pgvector

**Version:** 1.0
**Status:** Active — Reference Document
**Last Updated:** 2026-03-30

---

## Context

C1 was built using Google Gemini File Search as the document ingestion and retrieval layer. Production testing revealed unacceptable operational risks: unverifiable deletion, black-box chunking, broken metadata filtering, persistent 503 upload failures, zero audit logging, and absolute vendor lock-in.

This plan replaces Gemini File Search with a self-owned pgvector pipeline running inside the existing stack. No new platforms. No new accounts.

---

## What Changes and What Stays

**Stays unchanged:**
- Supabase project `bkkujtvhdbroieffhfok` — same project, schema builds on top
- Vercel frontend — no changes
- Railway FastAPI backend — ingestion and retrieval code inside it changes, the platform does not
- Claude API agents — orchestrator and all specialists unchanged
- All 8 existing tables — projects, contracts, parties, document_types, documents, contradiction_flags, query_log, classification_queue
- 176 taxonomy seed rows
- All RLS policies and triggers

**Replaced:**
- Gemini File Search store management → removed entirely
- `src/ingestion/` — rebuilt using Docling (parsing) + Gemini Embeddings API (vectors)
- `src/agents/retrieval.py` — rebuilt using pgvector similarity search + PostgreSQL full-text search

**Removed from database:**
- `projects.gemini_store_name` column — no longer needed
- `documents.gemini_file_uri` column — replaced by chunk references in `document_chunks`

**Added to database:**
- `pgvector` extension
- `document_chunks` table

**Embedding model:**
- Gemini Embeddings API (`gemini-embedding-001`) called directly — 3072 dimensions
- Same API key already in `.env` — no new credentials needed

---

## Migration Steps

| Step | Description | Agent | Status |
|---|---|---|---|
| 1 | Database migration — pgvector extension + `document_chunks` table + remove Gemini columns | DB Architect | ✅ Complete |
| 2 | Ingestion pipeline rebuild — Docling parsing + chunking + Gemini embedding + Supabase storage | Ingestion Engineer | ✅ Complete |
| 3 | Retrieval layer rebuild — pgvector similarity search + full-text hybrid search | Agent Orchestrator | ✅ Complete |
| 4 | Cleanup — remove all Gemini File Search store management code | API Engineer | ✅ Complete |
| 5 | End-to-end smoke test — upload, chunk, embed, query, verify audit log | Quality Guardian | ✅ Complete |

---

## Step 1 — Database Migration (`004_pgvector.sql`)

**What gets built:**
- Enable `pgvector` extension
- Create `document_chunks` table:
  - `id` — uuid, primary key
  - `document_id` — uuid, FK to `documents.id`
  - `project_id` — uuid, FK to `projects.id` (denormalized for RLS)
  - `chunk_index` — integer (order of chunk within document)
  - `content` — text (raw chunk text)
  - `embedding` — vector(3072)
  - `token_count` — integer
  - `created_at` — timestamptz
- HNSW index on `embedding` column for fast similarity search
- GIN index on `tsvector` generated from `content` for full-text search
- RLS enabled — project-owner scoped, same pattern as all other tables
- Remove `gemini_store_name` from `projects` table
- Remove `gemini_file_uri` from `documents` table

**Completion criteria:** Migration applies cleanly against existing schema. Quality Guardian sign-off.

---

## Step 2 — Ingestion Pipeline Rebuild

**What gets built in `src/ingestion/`:**
- `parser.py` — Docling extracts text from PDF, DOCX, XLSX. Handles scanned documents (OCR), tables, multi-column layouts. Returns structured text with section boundaries preserved.
- `chunker.py` — Splits extracted text into semantically coherent chunks. Respects section boundaries. Target chunk size: 400-500 tokens with 50-token overlap. No mid-sentence or mid-clause breaks.
- `embedder.py` — Calls Gemini Embeddings API (`gemini-embedding-001`) for each chunk. Returns 3072-dimension vectors. Handles batching for documents with many chunks.
- `store.py` — Writes chunks and embeddings to `document_chunks` table in Supabase. Atomic: if any chunk fails, all chunks for that document are rolled back. Document status updated to `STORED` or `FAILED`.
- `pipeline.py` — Orchestrates the full flow: parse → classify → extract metadata → chunk → embed → store. Status tracked at every step.

**What is removed:** All Gemini File Search store management code. `store_manager.py` deleted entirely.

**Completion criteria:** Upload a real PDF, verify chunks appear in `document_chunks` with embeddings, verify document status is `STORED`. Quality Guardian sign-off.

---

## Step 3 — Retrieval Layer Rebuild

**What gets built in `src/agents/retrieval.py`:**
- Vector similarity search: `embedding <=> query_vector` cosine distance using pgvector, filtered by `project_id`
- Full-text search: PostgreSQL `tsvector`/`tsquery` for exact-match on spec numbers, RFI IDs, clause references, reference numbers
- Hybrid merge: combine vector and full-text results, deduplicate, rank by combined score
- Project scoping: all searches filtered to the querying user's project — cross-project retrieval is impossible
- Returns: ranked chunks with `document_id`, `content`, `chunk_index`, similarity score — same interface the orchestrator expects

**Completion criteria:** A natural language query returns relevant chunks. A spec number query returns exact-match results. Quality Guardian sign-off.

---

## Step 4 — Cleanup

**What gets removed:**
- `src/ingestion/store_manager.py` — deleted entirely
- Any remaining Gemini File Search imports or references across all files
- Project creation endpoint no longer creates a Gemini store
- No dead code, no commented-out code

**Completion criteria:** `grep -r "file_search" src/` returns nothing. Quality Guardian sign-off.

---

## Step 5 — End-to-End Smoke Test

**Test sequence:**
1. Upload a real PDF document — verify `document_chunks` table has rows with non-null embeddings
2. Submit a natural language query — verify chunks are retrieved from Supabase, not Gemini
3. Verify agent response includes source citations from the uploaded document
4. Verify `query_log` has the new entry with correct document IDs
5. Delete the document — verify chunks are deleted from `document_chunks` (cascading delete or explicit cleanup)
6. Re-submit the same query — verify GREY confidence (no documents in warehouse)

**Completion criteria:** All 6 steps pass. Deletion is verified by row count before and after.

---

## Environment Variables

No new environment variables needed. Existing `.env` already contains:
- `GEMINI_API_KEY` — used for embeddings API call (different endpoint from File Search)
- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` — unchanged

---

## Governing Rules

1. One step at a time. No step starts until the previous is approved.
2. Quality Guardian reviews every step before it is marked complete.
3. No dead code. When Gemini File Search code is removed, it is deleted — not commented out.
4. Deletion must be verified in the smoke test — not assumed.
5. The agent layer (orchestrator, specialists) does not change during this migration.

---

## Document Control

| Field | Value |
|---|---|
| Owner | C1 Project |
| Updated when | Step completed or plan revised |
| Location | Repo root — `RETRIEVAL_MIGRATION.md` |
