# C1 — Construction Documentation Intelligence Platform

**Codename:** C1  
**Version:** 0.2 — Live  
**Status:** Confidential — Live  
**Market:** GCC — UAE, Saudi Arabia, Qatar  
**Date:** March 2026

### Live Deployment

| Component | URL |
|---|---|
| Frontend | https://c1intelligence.vercel.app |
| Backend API | https://web-production-6f2c4.up.railway.app |
| Health Check | https://web-production-6f2c4.up.railway.app/health |

### Current Build Status

| Milestone | Status |
|---|---|
| Original build — 7 steps (schema, ingestion, orchestrator, specialists, contradiction, API, frontend) | ✅ Complete — 2026-03-28 |
| pgvector migration — Gemini File Search replaced with self-owned pipeline | ✅ Complete — 2026-03-30 |
| AGENT_PLAN.md Phase 1 — BaseSpecialist, SkillLoader, four shared tools | ✅ Complete |
| AGENT_PLAN.md Phase 2 — Multi-round orchestrator, ThreadPoolExecutor parallel dispatch | ✅ Complete |
| C1_CLEANUP_PLAN.md Phases A–E — production fixes, spec alignment, Layer 2, playbooks, file storage | 🔄 Active workstream |
| AGENT_PLAN.md Phase 3 — Legal & Contractual Skills | ⬜ Blocked pending cleanup completion |

---

## 1. What C1 Is

C1 is a construction documentation intelligence platform designed to ingest, structure, cross-reference, and interrogate the full body of documentation generated across a construction or real estate development project.

It is not a project management system. It is not a document management system. It is not an operations tool. It is not a chatbot.

It is an independent intelligence and decision-support layer that sits above all operational systems and serves users who need the truth — regardless of which party they represent.

C1 does not compete with Procore, Aconex, Oracle Primavera, or any ERP system. It reads from them, aggregates across them, and reasons over them. Its core value is neutrality, auditability, and cross-domain intelligence.

---

## 2. The Problem C1 Solves

### 2.1 Fragmentation
On any given project, documentation is distributed across the owner's systems, the PMC's systems, the contractor's systems, sub-consultants, and various document control platforms. These systems are rarely integrated. There is no single source of truth.

### 2.2 Inconsistency and Contradiction
The same information often appears in multiple documents with different values:
- A claim amount in a legal notice that differs from the amount in the supporting claim document
- A delay duration in a notice of delay that differs from the delay logged in the Primavera schedule
- Contractual milestones that contradict approved programme revisions
- Cost figures in BOQs, valuations, and financial reports that diverge across document versions

### 2.3 Lack of Cross-Domain Awareness
Project issues are rarely single-domain. A delay has cost implications, contractual implications, and risk implications simultaneously. No existing tool synthesises across these domains in response to a single query.

### 2.4 Absence of Independent Intelligence
Operational systems are operated by the parties being audited or evaluated. An audit department, a board, a court expert, or a lender needs a view of the project that is independent of operations. No such tool currently exists in construction.

---

## 3. Core Principles

**Neutrality** — The system has no party allegiance. Its outputs reflect the documentation, not an interpretation favourable to any stakeholder.

**Auditability** — Every query, every response, and every document set on which a response was based is logged with a timestamp. The platform is a defensible record of what was known at any given point in time.

**Cross-domain intelligence** — The system does not answer in silos. A legal query surfaces cost, schedule, and risk implications. A financial query surfaces contractual and compliance dimensions. The user receives the full landscape, not just the answer to the narrow question asked.

**Contradiction preservation** — When the same information appears in multiple documents with different values, C1 does not resolve the contradiction. It retains all versions, records the source of each, and flags the discrepancy. This is a core feature, not a deficiency.

---

## 4. Who C1 Serves

C1 is designed for a limited number of senior, high-permission users. It serves individuals and teams who require independent, authoritative insight into a project's documentation record:

- Audit departments conducting forensic project reviews
- Compliance and governance officers monitoring contractual adherence
- Board members and executive leadership requiring decision-support on distressed or complex projects
- Legal counsel preparing or defending claims and disputes
- Court-appointed or arbitration experts conducting independent project assessments
- Lenders and investors conducting due diligence on active or distressed projects
- Risk officers assessing exposure at key project milestones

---

## 5. What C1 Is Not

- Not a project management system
- Not a document management or document control system
- Not an ERP or financial management system
- Not a collaboration or communication tool
- Not intended to replace operational workflows or systems

---

## 6. Core Architecture

### 6.1 The Data Warehouse

The foundation of C1 is a structured data warehouse purpose-built for construction documentation. Unlike a document repository, the warehouse is not a passive store of files. It is an active, categorised, structured environment where documents are ingested, classified, and their content is parsed, indexed, and made available for intelligent querying.

The warehouse does not resolve contradictions. It retains all versions of conflicting information, records the source and metadata of each, and flags discrepancies.

### 6.2 Document Taxonomy — Two Layers

All documents within the warehouse are classified according to a predefined taxonomy structured in two layers:

**Layer 1 — Project-specific documents**
Documents generated in the course of a specific project by any party: contracts, drawings, specifications, correspondence, claims, notices, reports, valuations, schedules, approvals. These are classified across 10 categories and 176 document types. Full taxonomy is in `docs/taxonomy/C1_TAXONOMY_v0.4.xlsx`.

Stored in: `documents` table (metadata and status) + `document_chunks` table (chunked text and 3072-dim embeddings). Project-scoped — users can only access their own project's documents.

**Layer 2 — Reference documents**
Global, static, non-project-specific documents that provide the regulatory, legal, and standards framework against which project conduct is evaluated. These include:
- FIDIC conditions of contract (1999 and 2017 editions)
- PMBOK and other professional project management standards
- IFRS accounting standards applicable to project accounting and valuations
- Applicable laws and regulations (jurisdiction-specific)
- Government authority policies and requirements
- Delegation of Authority matrices
- Market benchmarks and cost data

Stored in: `reference_documents` table + `reference_chunks` table. Platform-wide — accessible to all authenticated users. Managed by the platform owner via `scripts/ingest_reference.py`. Not user-uploaded.

### 6.3 Document Ingestion — Phase 1 (Manual Upload)

C1 Phase 1 uses a self-owned ingestion pipeline. All stages of document processing are handled without dependency on a third-party document search service.

**Ingestion pipeline (in order):**

1. **Parsing** — Docling extracts structured text from PDF (text-based and OCR/scanned), DOCX, and XLSX files. Output is full markdown text plus section headings.

2. **Classification** — Claude AI classifies the document against the 176-type taxonomy. Confidence threshold of 0.75 required for auto-classification; documents below threshold go to `classification_queue`.

3. **Metadata extraction** — Claude AI extracts structured metadata from document content (dates, parties, contract references, FIDIC sub-clauses, financial figures).

4. **Chunking** — tiktoken cl100k_base splits the document into section-aware chunks (450-token target, 50-token overlap). Section headings are preserved per chunk for attribution.

5. **Embedding** — Gemini Embeddings API (gemini-embedding-001) generates 3072-dimension vectors for each chunk, batched at 100.

6. **Storage** — Chunks and embeddings are written atomically to `document_chunks` in Supabase pgvector. On any failure, chunks are rolled back and `documents.status` is set to `FAILED`.

7. **File preservation** — The original uploaded file is stored in Supabase Storage (`document-originals` bucket) at `{project_id}/{document_id}/{filename}` before ingestion begins. This preserves the forensic chain of custody.

**Processing status is always visible:** `QUEUED` → `EXTRACTING` → `CLASSIFYING` → `STORED` / `FAILED`.

**Accepted formats:** PDF, DOCX, XLSX only.

### 6.4 Document Ingestion — Phase 2 (Integrated System Ingestion)

Phase 2 will add direct integration with document control systems (Aconex, Docutrack, and similar). Documents extracted from integrated systems carry an established chain of custody from their source system.

---

## 7. Roles, Access, and Authority Matrix

C1 operates on a defined role-based access control model. The five user roles and three approval flow types will be defined in a subsequent specification. Approval workflows are a Phase 2 feature — correctly deferred from the initial build.

---

## 8. Intelligence and Query Layer

### 8.1 Purpose

The intelligence layer accepts natural language queries and returns substantive, cross-referenced, source-attributed responses drawn from the documents in the warehouse at the time of the query.

### 8.2 Multi-Domain Response Architecture

A query posed in one domain — legal, financial, schedule, risk, or compliance — does not receive a tunnel-visioned response. The orchestration layer identifies which domains are relevant and engages the appropriate domain reasoning, then aggregates a unified response that surfaces the full landscape of implications.

### 8.3 Agent Architecture

```
User Query
    ↓
Master Orchestrator (Claude API)
    ↓
Domain Identification — which of 6 domains are relevant?
    ↓
Hybrid Retrieval (pgvector on Supabase):
    Layer 1 — Semantic search (cosine similarity, gemini-embedding-001) — project documents
    Layer 1 — Full-text search (PostgreSQL tsvector) — project documents
    Layer 2 — Semantic search — reference documents (FIDIC, PMBOK, IFRS, laws)
    → top-k chunks with content, section heading, document metadata
    ↓
Round 1 — Parallel Dispatch (ThreadPoolExecutor):
    Legal & Contractual + Commercial & Financial
    ↓
Round 2 — Sequential Dispatch (with Round 1 findings as context):
    Claims & Disputes / Schedule & Programme / Technical & Design / Governance & Compliance
    ↓
Cross-Specialist Contradiction Pass (stub — AGENT_PLAN Phase 7)
    ↓
Intra-Document Contradiction Detection — flags conflicts across retrieved documents
    ↓
Confidence Classification — GREEN / AMBER / RED / GREY
    ↓
Response Synthesis — unified cross-domain answer with full source attribution
    ↓
Audit Log — immutable record written to Supabase query_log
    ↓
User
```

**Each domain specialist runs as a true agent (AGENT_PLAN Phase 1 + 2):**
- Receives retrieved chunks from Layer 1 (project documents) and Layer 2 (reference documents)
- Receives query + (Round 2 only) Round 1 findings as context
- Assesses whether retrieved context is sufficient
- Calls tools if more information is needed (up to configured max tool rounds)
- Reasons over all evidence and returns structured findings

**Domain-to-config key mapping:**
`identify_domains()` returns full names (e.g., `"legal_contractual"`). `SPECIALIST_CONFIGS` uses short keys (e.g., `"legal"`). `DOMAIN_TO_CONFIG_KEY` in `orchestrator.py` bridges these.

**`contradiction_cross.py` is a stub** returning an empty list. AGENT_PLAN Phase 7 will implement real cross-specialist contradiction logic.

### 8.4 Skill Files

Each specialist loads domain knowledge from markdown skill files in `skills/{domain}/` at runtime. The SkillLoader scans all `.md` files in the folder dynamically — no hardcoded filenames. Dropping a new skill file into the folder and deploying is sufficient to add it; no code change required.

Skill file authorship is governed by `SKILLS_STANDARDS.md`.

### 8.5 Confidence States

Every C1 response carries one of four confidence states:

| State | Meaning |
|---|---|
| 🟢 GREEN | Answer is consistent across all retrieved documents |
| 🟡 AMBER | Answer is present but incomplete or partially supported |
| 🔴 RED | Contradiction detected between documents |
| ⬜ GREY | Insufficient documents in the warehouse to answer |

### 8.6 Auditability of Responses

Every query and every response is logged with a timestamp, the identity of the querying user, and the precise set of documents in the warehouse at the time of the query. This log is immutable and cannot be altered after the fact.

---

## 9. Standards and Regulatory Framework

- **FIDIC** — Red Book 1999 and 2017 editions. Sub-clause differences between editions are mapped and handled. Both editions available as Layer 2 reference documents.
- **PMBOK** — professional project management framework underpinning programme and delivery assessment.
- **IFRS** — financial reporting standard applicable to project accounting, valuations, and financial compliance.

---

## 10. Illustrative Use Cases

### 10.1 Dispute and Claim Assessment
A legal team uploads all project correspondence, notices, claims, and schedule records. They query the platform to reconstruct the timeline of events, identify contradictions between the contractor's claimed delay durations and the programmatic record, and assess the contractual validity of each notice. The platform surfaces the legal, schedule, and commercial dimensions simultaneously.

### 10.2 Board-Level Project Audit
A board investigating a cost overrun uses C1 to interrogate the financial and contractual record. The platform identifies discrepancies between approved budgets, variation orders, and reported costs, and surfaces governance and compliance dimensions of decisions made during the project.

### 10.3 Lender Due Diligence
A lender reviewing a distressed project uses C1 to assess the status of contractual obligations, the financial exposure across all active contracts, and the risk profile of ongoing claims.

### 10.4 Compliance Review
A compliance officer uses C1 to verify that contractual obligations, regulatory requirements, and internal governance policies have been met. The platform cross-references project documents against the applicable reference document library and flags non-conformances.

---

## 11. Technical Stack

| Component | Technology | Purpose |
|---|---|---|
| Document parsing | Docling | PDF (text + OCR), DOCX, XLSX text extraction → structured markdown |
| Chunking | tiktoken cl100k_base | Section-aware splitting (450-token target, 50-token overlap) |
| Embeddings | Gemini Embeddings API (gemini-embedding-001) | 3072-dimension dense vectors, batched at 100 |
| Vector store & retrieval | pgvector on Supabase | Cosine similarity + tsvector full-text, hybrid RPC, sequential scan |
| AI agents & reasoning | Anthropic Claude API | Classification, metadata extraction, domain specialists, orchestration, contradiction detection |
| Structured database | Supabase (PostgreSQL) | Relational metadata, chunk storage, contradiction flags, immutable audit log |
| Authentication | Supabase Auth | User accounts, sessions, JWT tokens, row-level security |
| File storage | Supabase Storage | Original uploaded documents (forensic chain of custody) |
| Backend / API | Python — FastAPI | Business logic layer exposing intelligence to the frontend |
| Frontend | React + TypeScript + Tailwind CSS | Document upload, querying, audit log, confidence display |
| Backend hosting | Railway (Dockerfile builder) | Hosts the FastAPI backend — deploys from GitHub via Dockerfile |
| Frontend hosting | Vercel | Hosts and serves the frontend |

### Deployment Architecture

```
User (browser)
    ↓
Vercel — serves the frontend
    ↓  authenticated request (JWT token from Supabase Auth)
FastAPI backend (Railway)
    ↓                         ↓                         ↓
Ingestion pipeline         Claude API               Supabase
(Docling + tiktoken        (agents & reasoning)     (metadata + chunks + embeddings
 + Gemini Embeddings                                 + reference docs + auth
 → pgvector)                                         + audit + storage)
```

---

## 12. Database Tables

| Table | Layer | Scope | Purpose |
|---|---|---|---|
| `projects` | — | Per-user | Each project loaded into C1 |
| `contracts` | — | Per-project | Each contract within a project |
| `parties` | — | Per-project | Each party with their role |
| `document_types` | — | Platform (read-only) | 176 document types seeded from taxonomy v0.4 |
| `documents` | Layer 1 | Per-project | Every project document ingested — metadata, classification, status, storage path |
| `document_chunks` | Layer 1 | Per-project | Chunked text + 3072-dim embeddings (immutable, CASCADE DELETE from documents) |
| `reference_documents` | Layer 2 | Platform | FIDIC, PMBOK, IFRS, laws — platform-wide reference standards |
| `reference_chunks` | Layer 2 | Platform | Chunked reference text + 3072-dim embeddings (immutable) |
| `contradiction_flags` | — | Per-project | Detected contradictions between document pairs |
| `query_log` | — | Per-project | Immutable audit trail — every query and response |
| `classification_queue` | — | Per-project | Documents pending manual classification |

---

## 13. Document Taxonomy Summary

176 document types across 10 categories. Full taxonomy with formats, tiers, and FIDIC clause references in `docs/taxonomy/C1_TAXONOMY_v0.4.xlsx`.

| Category | Types |
|---|---|
| Governance | 16 |
| Legal & Contractual | 28 |
| Commercial & Financial | 18 |
| PM & Controls | 24 |
| Engineering & Design | 14 |
| Procurement | 12 |
| Construction | 19 |
| Quality & HSE | 12 |
| Claims & Disputes | 14 |
| Testing & Handover | 19 |

**Tiers:**
- **Tier 1 — Critical:** Directly affects money, time, liability, or contractual enforceability
- **Tier 2 — Important:** Used for control, monitoring, planning, or analysis
- **Tier 3 — Supporting:** Execution evidence, technical detail, logs, registers

---

## 14. Competitive Positioning

C1's five most defensible differentiators:

1. **Contradiction preservation as forensic architecture** — no evaluated tool treats the preservation and surfacing of contradictions across documents as a design principle
2. **Multi-domain structured querying** — no platform delivers simultaneous cross-domain intelligence across legal, commercial, schedule, risk, compliance, and financial dimensions aligned to FIDIC, PMBOK, and IFRS
3. **Independence from project parties** — C1 targets independent oversight users (auditors, court experts, lenders, boards) — an unaddressed segment in construction technology
4. **Document control system ingestion as a forensic pipeline** — Phase 2 integration with Aconex, Docutrack as structured forensic data sources
5. **Construction-specific domain ontology** — purpose-built understanding of FIDIC clause hierarchies, PMBOK process frameworks, and construction document classification

---

## 15. Items Deferred to Subsequent Phases

- Five user roles and their precise permission sets
- Three document approval flow types and document types mapped to each
- Authority matrix governing reference document ingestion from external sources
- Integration architecture for document control systems (Phase 2)
- Party ID resolution — `issuing_party_id` and `receiving_party_id` stay as text fields until a parties management API is built
- Approval workflow layer
- Pricing model and commercial structure
- Platform permanent name (currently codename C1)

---

## 16. Getting Started

### Prerequisites

- Python 3.13+
- Node.js 20+
- A Supabase project with migrations applied
- API keys for Gemini and Anthropic Claude

### Local Development

```bash
# Clone the repository
git clone https://github.com/Yazo1968/C1Intelligence.git
cd C1Intelligence

# Copy environment template and fill in real values
cp .env.example .env

# Install backend dependencies
pip install -r requirements.txt

# Start the backend
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# In a separate terminal — install and start the frontend
cd frontend
npm install
npm run dev
```

### Environment Variables

**Backend (.env):**
- `SUPABASE_URL` — Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` — Supabase service role key (server-side only)
- `ANTHROPIC_API_KEY` — Anthropic Claude API key
- `GEMINI_API_KEY` — Google Gemini API key

**Frontend (frontend/.env.local):**
- `VITE_SUPABASE_URL` — Supabase project URL
- `VITE_SUPABASE_PUBLISHABLE_KEY` — Supabase anon key (public, safe for frontend). Use the JWT format starting with `eyJ...` — not the `sb_publishable_` format.
- `VITE_API_BASE_URL` — Backend URL (e.g., `http://localhost:8000`)

### Database Migrations

Apply migrations in order against your Supabase project:

| Migration | Purpose |
|---|---|
| `001_initial_schema.sql` | 8 tables, triggers, 176-row taxonomy seed |
| `002_rls_policies.sql` | Row Level Security policies |
| `003_classification_queue_project_id.sql` | Denormalized project_id |
| `004_pgvector.sql` | pgvector extension, `document_chunks` table, RLS, initial RPC functions |
| `005_document_chunks_immutable.sql` | Removes UPDATE RLS (chunks are write-once) |
| `006_retrieval_functions.sql` | `search_chunks_semantic` + `search_chunks_fulltext` RPCs |
| `007_layer2_reference.sql` | `reference_documents` + `reference_chunks` tables, Layer 2 RPC functions |
| `008_document_storage.sql` | `storage_path` column on `documents` |

Migrations 007 and 008 are added during C1_CLEANUP_PLAN.md Phases C and D respectively.

### Ingesting Reference Documents (Layer 2)

After migrations 007 is applied, ingest FIDIC and other reference documents via the CLI script:

```bash
python scripts/ingest_reference.py \
  --file path/to/fidic_red_book_1999.pdf \
  --name "FIDIC Red Book 1999 — Conditions of Contract for Construction" \
  --document-type "FIDIC Conditions of Contract" \
  --standard-body "FIDIC" \
  --edition-year "1999" \
  --description "General Conditions (Part I) — FIDIC Red Book 1999 edition"
```

Run from the repository root. Requires `.env` with all four backend environment variables.

---

## 17. API Endpoints

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/health` | No | Deployment health check |
| `POST` | `/projects` | Yes | Create project |
| `GET` | `/projects` | Yes | List user's projects |
| `POST` | `/projects/{id}/documents` | Yes | Upload + classify document |
| `GET` | `/projects/{id}/documents` | Yes | List project documents |
| `GET` | `/projects/{id}/documents/{doc_id}` | Yes | Get document detail |
| `POST` | `/projects/{id}/query` | Yes | Submit natural language query |
| `GET` | `/projects/{id}/query-log` | Yes | Retrieve immutable audit log |
| `GET` | `/projects/{id}/contradictions` | Yes | List contradiction flags |

All authenticated endpoints require `Authorization: Bearer <jwt>` from Supabase Auth.

---

## 18. Repository Structure

```
/
├── README.md                            ← This file — single source of truth
├── CLAUDE.md                            ← Behavioural contract for Claude Code
├── AGENT_PLAN.md                        ← Agent enhancement plan v1.3
├── SKILLS_STANDARDS.md                  ← Skill file authorship standards v1.1
├── BUILD_LOG.md                         ← Completion log and deferred items register
├── C1_CLEANUP_PLAN.md                   ← Active workstream plan (Phases A–E)
├── requirements.txt
├── Dockerfile
├── Procfile                             ← Legacy reference only (railway.json takes precedence)
├── railway.json                         ← Railway config — Dockerfile builder, sh -c start command
├── .env.example
├── .gitignore
├── scripts/
│   └── ingest_reference.py             ← CLI script for Layer 2 reference doc ingestion (Phase C)
├── docs/
│   ├── migrations/
│   │   └── RETRIEVAL_MIGRATION.md      ← pgvector migration record
│   ├── research/
│   │   └── legal_domain_research_summary.md  ← Phase 3 pre-authorship research
│   └── taxonomy/
│       └── C1_TAXONOMY_v0.4.xlsx       ← 176 document types, 10 categories
├── supabase/
│   └── migrations/
│       ├── 001_initial_schema.sql      ← 8 tables, triggers, 176-row seed
│       ├── 002_rls_policies.sql        ← Row Level Security policies
│       ├── 003_classification_queue_project_id.sql
│       ├── 004_pgvector.sql            ← pgvector, document_chunks, RLS, RPC functions
│       ├── 005_document_chunks_immutable.sql
│       ├── 006_retrieval_functions.sql ← search_chunks_semantic + search_chunks_fulltext
│       ├── 007_layer2_reference.sql    ← reference_documents + reference_chunks (Phase C)
│       └── 008_document_storage.sql   ← storage_path column on documents (Phase D)
├── src/
│   ├── config.py                       ← Environment variable loading
│   ├── clients.py                      ← Supabase + Gemini + Anthropic client singletons
│   ├── logging_config.py               ← Structured logging (structlog)
│   ├── ingestion/
│   │   ├── pipeline.py                 ← Full ingestion orchestration
│   │   ├── parser.py                   ← Docling document parsing (lazy import)
│   │   ├── chunker.py                  ← Section-aware chunking, 450-token target
│   │   ├── embedder.py                 ← Gemini Embeddings API (3072 dims, batched)
│   │   ├── store.py                    ← Atomic pgvector chunk storage + rollback
│   │   ├── classifier.py               ← Claude classification, 0.75 threshold
│   │   ├── metadata_extractor.py       ← Claude metadata extraction
│   │   ├── validator.py                ← Tier-based field validation
│   │   ├── status_tracker.py           ← Document lifecycle management
│   │   ├── taxonomy_cache.py           ← In-memory taxonomy cache
│   │   ├── file_validation.py          ← Extension and size validation
│   │   └── models.py                   ← Ingestion data models
│   ├── agents/
│   │   ├── orchestrator.py             ← Master orchestrator, multi-round dispatch
│   │   ├── base_specialist.py          ← Shared agentic loop (all 6 specialists)
│   │   ├── tools.py                    ← Four shared tools available to all specialists
│   │   ├── skill_loader.py             ← Dynamic skill loading + DB-driven playbook
│   │   ├── specialist_config.py        ← SPECIALIST_CONFIGS dict
│   │   ├── domain_router.py            ← Claude-based domain identification
│   │   ├── retrieval.py                ← Layer 1 + Layer 2 hybrid retrieval
│   │   ├── contradiction.py            ← Intra-document contradiction detection
│   │   ├── contradiction_cross.py      ← Cross-specialist stub (Phase 7 fills logic)
│   │   ├── synthesis.py                ← Response synthesis + confidence
│   │   ├── prompts.py                  ← System prompts for all agents
│   │   ├── audit.py                    ← Immutable query log writes
│   │   ├── models.py                   ← Agent data models (SpecialistFindings etc.)
│   │   └── specialists/
│   │       └── __init__.py
│   └── api/
│       ├── main.py                     ← FastAPI app entry point
│       ├── auth.py                     ← JWT validation middleware
│       ├── errors.py                   ← Structured error handlers
│       ├── schemas.py                  ← Pydantic request/response models
│       └── routes/
│           ├── health.py
│           ├── projects.py
│           ├── documents.py
│           └── queries.py
├── skills/
│   ├── legal/                          ← AGENT_PLAN Phase 3 (not started)
│   ├── commercial/                     ← AGENT_PLAN Phase 4
│   ├── claims/
│   │   └── README.md                   ← Placeholder
│   ├── schedule/                       ← AGENT_PLAN Phase 6
│   ├── governance/                     ← AGENT_PLAN Phase 6
│   └── technical/                      ← AGENT_PLAN Phase 6
├── playbooks/
│   └── README.md                       ← Flat file override; DB-driven after Phase D
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts               ← Authenticated API client
│   │   │   ├── documents.ts
│   │   │   ├── projects.ts
│   │   │   ├── queries.ts
│   │   │   └── types.ts                ← TypeScript interfaces mirroring backend schemas
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

Note: `scripts/ingest_reference.py` and migrations 007–008 are deliverables of C1_CLEANUP_PLAN.md Phases C and D. They are shown here as the target state.

---

## 19. Document Control

| Field | Value |
|---|---|
| Version | 0.2 — pgvector migration + AGENT_PLAN Phases 1–2 complete |
| Date | March 2026 (initial: 2026-03-28, pgvector: 2026-03-30) |
| Status | Confidential — Live |
| Codename | C1 |
