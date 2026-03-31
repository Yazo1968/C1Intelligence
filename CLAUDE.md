# CLAUDE.md — Behavioural Contract for Claude Code

This file governs how Claude Code works on the C1 project.
Read it fully before doing anything. Follow it in every session.

---

## The Single Most Important Rule

**One thing at a time. Wait for approval before moving to the next.**

You will be instructed step by step. Do not anticipate the next step. Do not build ahead. Do not assume scope. When a task is complete, say so clearly and wait.

---

## What You Are Building

C1 is a construction documentation intelligence platform for the GCC market. It ingests project documents, reasons across them using AI agents, detects contradictions between documents, and produces forensic-grade responses with full source attribution and confidence classification.

Read `README.md` fully before writing any code. It is the single source of truth for what C1 is, what it does, and how it works.
Read `docs/taxonomy/C1_TAXONOMY_v0.4.xlsx` before touching anything database-related.

---

## Technology Stack — Locked. Do Not Change.

| Component | Technology |
|---|---|
| Document parsing | Docling (PDF, DOCX, XLSX — text and OCR) |
| Chunking | tiktoken cl100k_base (section-aware, 512-token target) |
| Embeddings | Gemini Embeddings API (gemini-embedding-001, 3072 dimensions) |
| Vector store & retrieval | pgvector on Supabase — cosine similarity + tsvector full-text |
| AI agents & reasoning | Anthropic Claude API (claude-sonnet-4-6 or latest sonnet) |
| Structured database | Supabase (PostgreSQL) |
| Authentication | Supabase Auth |
| Backend / API | Python — FastAPI |
| Backend hosting | Railway (Dockerfile builder) |
| Frontend hosting | Vercel |
| Language | Python |

Do not introduce LangChain, LangGraph, LlamaIndex, or any other orchestration framework. Build directly against the Gemini and Anthropic SDKs.

---

## Architecture Boundaries — Non-Negotiable

**Ingestion pipeline handles (`src/ingestion/`):**
- Document parsing — Docling (PDF text extraction, DOCX, XLSX, OCR for scanned PDFs)
- Section-aware chunking — tiktoken cl100k_base (512-token target, 50-token overlap)
- Embedding — Gemini Embeddings API (gemini-embedding-001, 3072 dimensions, batched at 100)
- Chunk storage — pgvector on Supabase (`document_chunks` table, immutable after write)
- Hybrid retrieval — pgvector cosine similarity + PostgreSQL tsvector full-text (via RPC functions)

**Claude API handles:**
- Document classification (matching to taxonomy)
- Metadata extraction from document content
- All domain reasoning (6 specialist agents)
- Master orchestration
- Contradiction detection
- Response synthesis

**Supabase handles:**
- Structured relational data — projects, parties, contracts, document types
- User authentication and session management (Supabase Auth)
- Document registry — metadata, classification, processing status (`documents` table)
- Document chunks and embeddings — `document_chunks` table (immutable, CASCADE DELETE from documents)
- Retrieval RPC functions — `search_chunks_semantic` and `search_chunks_fulltext`
- Contradiction flags (project-scoped — never cross-project)
- Immutable query audit log (UPDATE and DELETE blocked by trigger)
- Classification queue for documents that cannot be auto-classified
- Row Level Security — users only access their own project data

**FastAPI backend handles:**
- Receives all requests from the frontend
- Validates authentication via Supabase Auth JWT before any action
- Orchestrates calls between ingestion pipeline, Claude API, and Supabase
- Exposes endpoints: create project, upload document, submit query, retrieve audit log
- All API keys and credentials managed server-side — never exposed to the frontend

Do not move responsibilities between these systems without explicit instruction.

---

## Build Sequence — Strict Order

Build in this sequence. Do not start a step until the previous one is approved:

1. ~~Supabase schema — tables, RLS, triggers, seed taxonomy~~ **COMPLETE** (migrations 001–003)
2. ~~Gemini ingestion layer~~ **COMPLETE** (`src/ingestion/`)
3. ~~Master orchestrator~~ **COMPLETE** (`src/agents/orchestrator.py`)
4. ~~Domain specialists~~ **COMPLETE** (`src/agents/specialists.py` — 6 agents)
5. ~~Contradiction detection~~ **COMPLETE** (`src/agents/contradiction.py` — non-blocking write-back)
6. ~~FastAPI layer~~ **COMPLETE** (`src/api/` — 9 authenticated endpoints)
7. ~~Frontend~~ **COMPLETE** (`frontend/` — React/TypeScript/Tailwind)

All 7 steps complete. End-to-end tested and deployed as of 2026-03-28.

**pgvector migration complete as of 2026-03-30.** Gemini File Search replaced with self-owned ingestion pipeline. All 5 smoke tests passed.

Each step is handed to one agent. Other agents wait.

---

## Agent Team

| # | Role | Responsibility |
|---|---|---|
| 1 | DB Architect | Supabase schema and migrations |
| 2 | Ingestion Engineer | Docling parsing + chunking + Gemini embedding + pgvector storage + Claude classification |
| 3 | Agent Orchestrator | Master orchestrator + domain specialists + contradiction detection |
| 4 | API Engineer | FastAPI or similar — exposes the intelligence layer |
| 5 | Quality Guardian | Reviews all output before it is finalised — cross-cutting |

**Quality Guardian rules:**
- Reviews every agent's output before it is marked complete
- Flags: dead code, unused imports, duplicated logic, inconsistent naming, over-abstraction, missing error handling, silent failures
- Has authority to send work back for revision
- Does not block delivery — flags issues with severity (CRITICAL / HIGH / MEDIUM / LOW)

---

## What You Must Never Do

**Never build ahead of instructions.**
If you are told to build the schema, build only the schema. Do not start the ingestion layer. Do not scaffold the agents. Do not create placeholder files.

**Never make architectural decisions without asking.**
If something is ambiguous, ask. If two approaches exist, present them and wait for a decision. Do not pick one and proceed.

**Never leave silent failures.**
Every error must produce a declared output. Log it, store it, surface it. Never swallow an exception silently.

**Never store sensitive data in logs or error messages.**
Document content, party names, and financial figures must not appear in error logs.

**Never resolve contradictions.**
When two documents contain conflicting values for the same field, surface both. State which document says what. Do not choose one. Do not average them. Do not summarise them into one coherent answer.

**Never go beyond the evidence.**
C1 surfaces what documents say. It does not predict outcomes, give legal advice, or render judgements. If a document implies something, state what the document says — not what it means.

**Never hardcode secrets.**
API keys, database URLs, and credentials live in environment variables only. Never in code. Never in comments.

**Never accumulate dead code.**
When an approach changes, delete the old code. Do not comment it out. Do not leave it "just in case."

---

## Code Quality Standards

**One responsibility per function.** If a function does two things, split it.

**Explicit over implicit.** Name things clearly. No single-letter variables outside of list comprehensions.

**Error handling is not optional.** Every external call (Gemini API, Anthropic API, Supabase) has a try/except with a meaningful error path.

**Every failure mode has a declared state.** A document that fails classification goes to `classification_queue`. A query that fails retrieval returns GREY confidence. Nothing disappears silently.

**Type hints on all functions.** No untyped Python.

**No print statements in production code.** Use structured logging.

---

## Database Rules

**Every table has `created_at` and `updated_at` timestamps.**

**`query_log` is immutable.** Triggers block UPDATE and DELETE. This is a forensic audit trail. It cannot be altered.

**`contradiction_flags` are project-scoped.** A contradiction can only exist between two documents in the same project.

**No orphaned foreign keys.** Every FK relationship is enforced at the database level.

**Row Level Security is enabled on all tables.**

---

## Ingestion Pipeline Rules

**Every document has a record in `documents` before any processing begins.** Status transitions: `QUEUED` → `EXTRACTING` → `CLASSIFYING` → `STORED` / `FAILED`. Nothing is processed silently.

**Docling import is lazy.** `from docling.document_converter import DocumentConverter` is imported inside the function body of `parse_document()` — not at module level. This prevents a startup crash caused by opencv transitive dependencies loading at FastAPI startup.

**opencv-python-headless must be pinned and reinstalled explicitly in the Dockerfile.** Docling's transitive dependencies pull in `opencv-python` (non-headless), which requires `libxcb.so.1` — absent in slim containers. The Dockerfile explicitly uninstalls `opencv-python` and reinstalls `opencv-python-headless==4.13.0.92` after all dependencies are installed.

**Chunks are immutable.** `document_chunks` has no UPDATE RLS policy. Chunks are write-once. To replace a document's chunks, delete the document (CASCADE deletes all chunks) and re-ingest.

**CASCADE DELETE is enforced at the DB level.** `document_chunks.document_id` is a FK to `documents.id` with `ON DELETE CASCADE`. Deleting a document automatically deletes all its chunks. This is non-negotiable.

**Retrieval uses two RPC functions.** `search_chunks_semantic` (cosine similarity via pgvector) and `search_chunks_fulltext` (PostgreSQL tsvector). Full-text failure is non-fatal — semantic-only results are returned. Both are project-scoped; no cross-project chunk access is possible.

**Processing status is always visible.** Every document has a status in `documents.status`. A document that fails at any stage gets status `FAILED` with the error stored. Documents that cannot be classified go to `classification_queue`. Nothing disappears silently.

**Vector index is deferred.** pgvector 0.8.0 on Supabase caps HNSW and IVFFlat at 2000 dimensions. Embeddings are 3072 dimensions. Sequential scan is used until Supabase upgrades pgvector or the embedding dimension is reduced. Do not attempt to create an HNSW or IVFFlat index at 3072 dims — it will fail.

---

## Confidence States — Exact Definitions

| State | When to use |
|---|---|
| GREEN | All retrieved documents are consistent on the queried field |
| AMBER | Field is present but only partially supported, or only one document covers it |
| RED | Two or more documents contain conflicting values for the same field |
| GREY | Retrieval returned zero relevant chunks — warehouse has no relevant documents |

GREY is only assigned when retrieval returns nothing. It is not a fallback for uncertainty.

---

## FIDIC Awareness

The domain specialists must understand:
- FIDIC Red Book 1999 and 2017 editions are both in use
- Sub-clause numbering differs between editions (e.g., 8.4 [1999] is 8.5 [2017])
- Notice of Claim has a 28-day time bar — this is one of the most important forensic flags
- The Engineer role may be filled by PMC, Supervision Consultant, or a dedicated firm — the AI infers this from contracts in the database
- Contradiction between the same field in different documents is never resolved — both versions are always surfaced

---

## Session Discipline

At the start of every session:
1. State what you are building in this session
2. State what you are NOT building
3. State any open questions that need answering before you start
4. Wait for confirmation before writing any code

At the end of every session:
1. State what was built
2. State what was not completed and why
3. State what the next session should pick up
4. Confirm all files are committed to the repository

---

## The Reminder That Governs Everything

You are building a forensic intelligence platform used by auditors, legal counsel, and board members to understand the truth about a construction project. Every architectural decision must be defensible. Every output must be traceable. Every failure must be visible.

Build accordingly.

---

## Deployment — Live. Initial: 2026-03-28. pgvector migration: 2026-03-30.

| Component | Platform | URL |
|---|---|---|
| Frontend | Vercel | https://c1intelligence.vercel.app |
| Backend API | Railway | https://web-production-6f2c4.up.railway.app |
| Database | Supabase | Project `bkkujtvhdbroieffhfok` (eu-west-1) |
| Source code | GitHub | Yazo1968/C1Intelligence (main branch) |

### Environment Variables

**Railway (backend) — 4 variables:**
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`

**Vercel (frontend) — 3 variables:**
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_PUBLISHABLE_KEY` — uses the anon JWT key (`eyJ...`), NOT the `sb_publishable_` format
- `VITE_API_BASE_URL` — points to the Railway backend URL

### Deployment Notes

- **Railway uses Dockerfile builder** — `railway.json` sets `"builder": "DOCKERFILE"`. Do NOT switch to NIXPACKS; it cannot handle the docling/opencv dependency chain.
- **`$PORT` must be wrapped in `sh -c`** — Railway's Dockerfile builder does not expand environment variables in exec-form CMD. The `startCommand` in `railway.json` is: `sh -c 'uvicorn src.api.main:app --host 0.0.0.0 --port $PORT'`
- The `Procfile` still exists for reference but `railway.json` startCommand takes precedence.
- Vercel project root directory is set to `frontend/`, framework preset is Vite.
- GitHub pushes to `main` auto-trigger both Railway and Vercel redeployments.

---

## Repository Structure — Current

```
/
├── README.md                           ← Single source of truth
├── CLAUDE.md                           ← This file — behavioural contract
├── docs/
│   ├── migrations/
│   │   └── RETRIEVAL_MIGRATION.md      ← pgvector migration record (complete)
│   └── taxonomy/
│       └── C1_TAXONOMY_v0.4.xlsx       ← 176 document types, 10 categories
├── requirements.txt                    ← Python dependencies
├── Dockerfile                          ← Railway container build (Dockerfile builder)
├── Procfile                            ← Legacy start command (reference only)
├── railway.json                        ← Railway config — DOCKERFILE builder, sh -c startCommand
├── .env                                ← Local secrets (gitignored)
├── .env.example                        ← Placeholder template
├── .gitignore
├── supabase/
│   └── migrations/
│       ├── 001_initial_schema.sql      ← 8 tables, triggers, 176-row seed
│       ├── 002_rls_policies.sql        ← Row Level Security policies
│       ├── 003_classification_queue_project_id.sql
│       ├── 004_pgvector.sql            ← pgvector extension, document_chunks table, RLS, RPC functions
│       ├── 005_document_chunks_immutable.sql ← Removes UPDATE RLS (chunks are write-once)
│       └── 006_retrieval_functions.sql ← search_chunks_semantic + search_chunks_fulltext RPCs
├── src/
│   ├── config.py                       ← Environment variable loading
│   ├── clients.py                      ← Supabase + Gemini client singletons
│   ├── logging_config.py               ← Structured logging (structlog)
│   ├── ingestion/                      ← Self-owned ingestion pipeline
│   │   ├── parser.py                   ← Docling document parsing (lazy import — see ingestion rules)
│   │   ├── chunker.py                  ← Section-aware chunking with tiktoken
│   │   ├── embedder.py                 ← Gemini Embeddings API (batched, 3072 dims)
│   │   ├── store.py                    ← Atomic pgvector chunk storage + rollback
│   │   ├── classifier.py               ← Claude-based taxonomy classification
│   │   ├── metadata_extractor.py       ← Claude-based metadata extraction
│   │   ├── validator.py                ← Tier-based field validation
│   │   ├── pipeline.py                 ← Full ingestion orchestration
│   │   └── models.py                   ← Ingestion data models (ParsedDocument, Chunk, EmbeddedChunk)
│   ├── agents/                         ← Intelligence layer
│   │   ├── orchestrator.py             ← Master orchestrator
│   │   ├── specialists.py              ← 6 domain specialist agents
│   │   ├── contradiction.py            ← Contradiction detection + write-back
│   │   ├── retrieval.py                ← pgvector hybrid retrieval (semantic + full-text)
│   │   ├── synthesis.py                ← Response synthesis + confidence
│   │   └── models.py                   ← Agent data models
│   └── api/                            ← FastAPI backend
│       ├── main.py                     ← App entry point
│       ├── auth.py                     ← JWT validation middleware
│       ├── errors.py                   ← Structured error handlers
│       ├── schemas.py                  ← Pydantic request/response models
│       └── routes/
│           ├── health.py               ← GET /health (no auth)
│           ├── projects.py             ← POST/GET /projects
│           ├── documents.py            ← POST/GET documents
│           └── queries.py              ← POST query, GET audit log, GET contradictions
├── frontend/                           ← React + TypeScript + Tailwind
│   ├── src/
│   │   ├── config.ts                   ← Environment variable loading
│   │   ├── lib/supabase.ts             ← Supabase client
│   │   ├── lib/api.ts                  ← Backend API client
│   │   ├── contexts/AuthContext.tsx     ← Auth state management
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── ProjectsPage.tsx
│   │   │   ├── ProjectPage.tsx
│   │   │   └── AuditLogPage.tsx
│   │   └── components/
│   │       ├── DocumentsPanel.tsx
│   │       ├── QueryPanel.tsx
│   │       └── QueryResponse.tsx       ← Most important UI component
│   └── ...
└── tests/                              ← Test suite (to be built)
```
