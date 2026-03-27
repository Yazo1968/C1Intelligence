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
Read `C1_TAXONOMY_v0.4.xlsx` before touching anything database-related.

---

## Technology Stack — Locked. Do Not Change.

| Component | Technology |
|---|---|
| Document ingestion & retrieval | Google Gemini File Search API |
| AI agents & reasoning | Anthropic Claude API (claude-sonnet-4-5 or latest sonnet) |
| Structured database | Supabase (PostgreSQL) |
| Authentication | Supabase Auth |
| Backend / API | Python — FastAPI |
| Backend hosting | Railway |
| Frontend hosting | Vercel |
| Language | Python |

Do not introduce LangChain, LangGraph, LlamaIndex, or any other orchestration framework. Build directly against the Gemini and Anthropic SDKs.

---

## Architecture Boundaries — Non-Negotiable

**Gemini File Search handles:**
- Document upload
- OCR and text extraction
- Chunking and embedding
- Semantic retrieval
- Citation generation

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
- Document registry — metadata, Gemini document reference, classification, processing status
- Contradiction flags (project-scoped — never cross-project)
- Immutable query audit log (UPDATE and DELETE blocked by trigger)
- Classification queue for documents that cannot be auto-classified
- Row Level Security — users only access their own project data

**FastAPI backend handles:**
- Receives all requests from the frontend
- Validates authentication via Supabase Auth JWT before any action
- Orchestrates calls between Gemini, Claude API, and Supabase
- Exposes endpoints: create project, upload document, submit query, retrieve audit log
- All API keys and credentials managed server-side — never exposed to the frontend

Do not move responsibilities between these systems without explicit instruction.

---

## Build Sequence — Strict Order

Build in this sequence. Do not start a step until the previous one is approved:

1. Supabase schema — tables, RLS, triggers, seed taxonomy
2. Gemini ingestion layer — document upload to Gemini File Search, metadata tagging on upload, Claude-based classification against taxonomy, metadata extraction, validation, gap identification, user override handling, classification queue routing, processing status tracking
3. Master orchestrator — receives query, identifies domains, calls Gemini retrieval, routes to specialists
4. Domain specialists — six specialist agents with FIDIC-aware system prompts
5. Contradiction detection — LLM detection + write-back to contradiction_flags table
6. FastAPI layer — exposes all functionality via authenticated endpoints
7. Frontend

Each step is handed to one agent. Other agents wait.

---

## Agent Team

| # | Role | Responsibility |
|---|---|---|
| 1 | DB Architect | Supabase schema and migrations |
| 2 | Ingestion Engineer | Gemini File Search integration + metadata extraction |
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

## Gemini File Search Rules

**One File Search store per project.** When a project is created in C1, a corresponding Gemini File Search store is created.

**Every document uploaded to Gemini must be tagged with metadata at upload time.** Minimum required metadata fields on every Gemini document:
- `project_id` — links back to the Supabase projects table
- `document_type` — the classified type from the taxonomy
- `tier` — 1, 2, or 3
- `document_date` — date of the document
- `supabase_document_id` — the UUID of the corresponding record in the documents table

This metadata enables filtering at retrieval time — queries can be scoped to a project, a document type, a tier, or a date range without retrieving irrelevant documents.

**Every document uploaded to Gemini also has a record in the `documents` table** with its Gemini document reference, extracted metadata, classification, and processing status.

**Processing status is always visible.** Every document has a status: `QUEUED` / `EXTRACTING` / `CLASSIFYING` / `STORED` / `FAILED`. This is stored in `documents.status`.

**Documents that cannot be classified go to `classification_queue`.** Never discard a document silently.

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
