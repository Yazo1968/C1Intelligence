# C1 — Construction Documentation Intelligence Platform

**Codename:** C1
**Version:** 0.3 — Live
**Status:** Confidential — Live
**Market:** GCC — UAE, Saudi Arabia, Qatar
**Date:** April 2026

### Live Deployment

| Component | URL |
|---|---|
| Frontend | https://c1intelligence.vercel.app |
| Backend API | https://web-production-6f2c4.up.railway.app |
| Health Check | https://web-production-6f2c4.up.railway.app/health |

### Build Status

| Milestone | Status |
|---|---|
| Original build — schema, ingestion, orchestrator, specialists, contradiction, API, frontend | ✅ Complete — 2026-03-28 |
| pgvector migration — Gemini File Search replaced with self-owned pipeline | ✅ Complete — 2026-03-30 |
| Production fixes, spec alignment, Layer 2, playbooks, file storage | ✅ Complete |
| Query pipeline improvements — citation quality, output format, footnotes | ✅ Complete |
| Three-tier multi-agent architecture — Legal, Commercial, Financial orchestrators + 4 SME domains | ✅ Complete |
| 22 SME skill files across Legal, Claims, Schedule & Programme, Technical & Construction | ✅ Complete |
| Risk reporting mode, Round 0 domain triage, domain filtering, prompt caching | ✅ Complete |
| Layer 2 split — layer_type + jurisdiction tagging, 6 FIDIC books ingested (1,917 chunks) | ✅ Complete |

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

**Cross-domain intelligence** — The system does not answer in silos. A legal query surfaces cost, schedule, and risk implications. A financial query surfaces contractual and compliance dimensions.

**Contradiction preservation** — When the same information appears in multiple documents with different values, C1 does not resolve the contradiction. It retains all versions, records the source of each, and flags the discrepancy. This is a core feature, not a deficiency.

---

## 4. Who C1 Serves

C1 is designed for a limited number of senior, high-permission users:

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
Documents generated in the course of a specific project by any party: contracts, drawings, specifications, correspondence, claims, notices, reports, valuations, schedules, approvals. These are classified across 10 categories and 176 document types. Full taxonomy is in `docs/archive/C1_TAXONOMY_v0.4.xlsx`.

Stored in: `documents` table (metadata and status) + `document_chunks` table (chunked text and 3072-dim embeddings). Project-scoped — users can only access their own project's documents.

**Layer 2 — Reference documents**
Global, static, non-project-specific documents that provide the regulatory, legal, and standards framework against which project conduct is evaluated. Subdivided by layer type and jurisdiction:
- `layer_type = '2a'` — internal reference documents (organisation policies, DOA matrices)
- `layer_type = '2b'` — external reference standards (FIDIC, laws, professional standards)
- `jurisdiction` — international, uae, ksa, or qatar (for 2b documents)

Currently ingested (1,917 chunks):
- FIDIC Red Book 1999 and 2017 General Conditions
- FIDIC Yellow Book 1999 and 2017 General Conditions
- FIDIC Silver Book 1999 and 2017 General Conditions

Stored in: `reference_documents` + `reference_chunks` tables. Platform-wide. Managed by the platform owner via `scripts/ingest_reference.py`.

### 6.3 Document Ingestion

**Ingestion pipeline (in order):**

1. **Parsing** — Docling extracts structured text from PDF (text-based and OCR/scanned), DOCX, and XLSX files.
2. **Classification** — Claude AI classifies the document against the 176-type taxonomy. Confidence threshold: 0.75.
3. **Metadata extraction** — Claude AI extracts structured metadata (dates, parties, contract references, FIDIC sub-clauses, financial figures).
4. **Chunking** — tiktoken cl100k_base splits the document into section-aware chunks (450-token target, 50-token overlap).
5. **Embedding** — Gemini Embeddings API (gemini-embedding-001) generates 3072-dimension vectors, batched at 100.
6. **Storage** — Chunks and embeddings written atomically to `document_chunks`. On failure, chunks are rolled back.
7. **File preservation** — Original uploaded file stored in Supabase Storage (`document-originals` bucket) before ingestion begins.

**Processing status:** `QUEUED` → `EXTRACTING` → `CLASSIFYING` → `STORED` / `FAILED`

**Accepted formats:** PDF, DOCX, XLSX only.

---

## 7. Roles, Access, and Authority Matrix

Five user roles and approval workflows are Phase 2 features — correctly deferred from the initial build.

---

## 8. Intelligence and Query Layer

### 8.1 Purpose

The intelligence layer accepts natural language queries and returns substantive, cross-referenced, source-attributed responses drawn from the documents in the warehouse at the time of the query.

### 8.2 Query Flow

```
User submits query
    ↓
Round 0 — fast synchronous triage (POST /query/assess, ~5 seconds)
    Single Claude API call → domain relevance classification (PRIMARY/RELEVANT/NOT_APPLICABLE)
    + 2-sentence executive brief + documents retrieved list
    ↓
User reviews Round 0 card — selects which domains to run
    ↓
Full analysis (POST /query — async, background task)
    ↓
Hybrid Retrieval (pgvector on Supabase):
    Layer 1 — Semantic + Full-text (project documents)
    Layer 2 — Semantic + Full-text (FIDIC, laws, standards) with optional layer/jurisdiction filters
    ↓
Tier 1 — Parallel Dispatch via ThreadPoolExecutor:
    Legal & Contractual  |  Commercial & Financial  |  Financial & Reporting
    (Each loads its directive.md, may invoke Tier 2 SMEs via invoke_sme tool)
    ↓
Tier 2 — On-demand SME invocation:
    Claims & Disputes  |  Schedule & Programme  |  Technical & Construction
    (Each loads its skill files dynamically)
    ↓
Cross-Specialist Contradiction Pass (stub — fills in Phase 7)
    ↓
Intra-Document Contradiction Detection
    ↓
Confidence Classification — GREEN / AMBER / RED / GREY
    ↓
Response Synthesis — unified cross-domain answer with full source attribution
    ↓
Audit Log — immutable record written to Supabase query_log
    ↓
User polls GET /queries/{id}/status until COMPLETE
```

### 8.3 Risk Reporting Mode

Any query can be submitted in Risk Report mode (`risk_mode: true`). When active:
- All Tier 1 orchestrators receive a risk-framing directive
- Findings are structured as risk exposures with likelihood, impact, and severity rating
- Frontend: amber checkbox on the query input; button label changes to "Generate Risk Report"

### 8.4 Three-Tier Agent Architecture

**Tier 0 — Main Orchestrator:**
Routes queries to Tier 1 orchestrators. No domain analysis at this tier.

**Tier 1 — Domain Orchestrators (BaseOrchestrator):**
Senior professional role per domain. Loads `skills/orchestrators/{domain}/directive.md`. Conducts direct analysis and delegates to Tier 2 SMEs via the `invoke_sme` tool. Three orchestrators: Legal & Contractual, Commercial & Financial, Financial & Reporting.

**Tier 2 — SME Agents (BaseSpecialist):**
Deep domain specialists. Load all `*.md` files from `skills/smes/{domain}/` dynamically. Invoked on-demand by Tier 1 orchestrators. Four SME domains: Legal (5 skills), Claims & Disputes (5 skills), Schedule & Programme (6 skills), Technical & Construction (6 skills).

### 8.5 Skill Files

22 skill files total across 4 SME domains. Authored against `docs/SKILLS_STANDARDS.md` v1.3.
All skill files apply four mandatory warehouse-grounding principles:
1. No assumption, extrapolation, or inference beyond retrieved documents
2. Contract-type distinction (Red/Yellow/Silver Book) always explicit
3. Layer 1 (project documents) and Layer 2 (reference standards) always distinguished
4. CANNOT ASSESS is the opening state — not a fallback

### 8.6 Prompt Caching

Both `BaseOrchestrator` and `BaseSpecialist` wrap the system prompt in `cache_control: ephemeral`. 90% input token cost saving on cache hits within a 5-minute window.

### 8.7 Confidence States

| State | Meaning |
|---|---|
| 🟢 GREEN | Answer is consistent across all retrieved documents |
| 🟡 AMBER | Answer is present but incomplete or partially supported |
| 🔴 RED | Contradiction detected between documents |
| ⬜ GREY | Insufficient documents in the warehouse to answer |

### 8.8 Auditability

Every query and every response is logged with a timestamp, the identity of the querying user, and the precise set of documents in the warehouse at the time of the query. This log is immutable and cannot be altered after the fact.

---

## 9. Standards and Regulatory Framework

**FIDIC** — Red, Yellow, and Silver Books in both 1999 and 2017 editions. All six books are ingested into the Layer 2 reference warehouse (1,917 chunks). The governing book and edition must always be confirmed from the project's contract documents.

**PMBOK** — Professional project management framework underpinning programme and delivery assessment.

**IFRS** — Financial reporting standard applicable to project accounting, valuations, and financial compliance.

**SCL Protocol 2nd Edition 2017** — Delay methodology framework applied by the Schedule & Programme SME and Claims SME.

**AACE RP 29R-03** — Delay analysis methodology classification framework.

---

## 10. Illustrative Use Cases

### 10.1 Dispute and Claim Assessment
A legal team uploads all project correspondence, notices, claims, and schedule records. They query the platform to reconstruct the timeline of events, identify contradictions between the contractor's claimed delay durations and the programmatic record, and assess the contractual validity of each notice. The platform surfaces the legal, schedule, and commercial dimensions simultaneously.

### 10.2 Board-Level Project Audit
A board investigating a cost overrun uses C1 to interrogate the financial and contractual record. The platform identifies discrepancies between approved budgets, variation orders, and reported costs, and surfaces governance and compliance dimensions of decisions made during the project.

### 10.3 Lender Due Diligence
A lender reviewing a distressed project uses C1 to assess the status of contractual obligations, the financial exposure across all active contracts, and the risk profile of ongoing claims.

### 10.4 Risk Assessment Report
A risk officer submits queries in Risk Report mode to receive structured risk registers — each finding classified with likelihood, impact, and severity — across legal, commercial, schedule, and financial dimensions simultaneously.

---

## 11. Technical Stack

| Component | Technology | Purpose |
|---|---|---|
| Document parsing | Docling | PDF (text + OCR), DOCX, XLSX text extraction → structured markdown |
| Chunking | tiktoken cl100k_base | Section-aware splitting (450-token target, 50-token overlap) |
| Embeddings | Gemini Embeddings API (gemini-embedding-001) | 3072-dimension dense vectors, batched at 100 |
| Vector store & retrieval | pgvector on Supabase | Cosine similarity + tsvector full-text, hybrid RPC, sequential scan |
| AI agents & reasoning | Anthropic Claude API (claude-sonnet-4-6) | Classification, metadata extraction, three-tier agents, orchestration, synthesis |
| Structured database | Supabase (PostgreSQL) | Relational metadata, chunk storage, contradiction flags, immutable audit log |
| Authentication | Supabase Auth | User accounts, sessions, JWT tokens, row-level security |
| File storage | Supabase Storage | Original uploaded documents (forensic chain of custody) |
| Backend / API | Python — FastAPI | Business logic layer exposing intelligence to the frontend |
| Frontend | React + TypeScript + Tailwind CSS (Vite) | Document upload, querying, Round 0 card, audit log, confidence display |
| Backend hosting | Railway (Dockerfile builder) | Hosts the FastAPI backend |
| Frontend hosting | Vercel (Vite preset) | Hosts and serves the React frontend |

---

## 12. Database Tables

| Table | Layer | Scope | Purpose |
|---|---|---|---|
| `projects` | — | Per-user | Each project loaded into C1 |
| `contracts` | — | Per-project | Each contract within a project |
| `parties` | — | Per-project | Each party with their role |
| `document_types` | — | Platform | 176 document types seeded from taxonomy v0.4; includes `citation_fields` column |
| `documents` | Layer 1 | Per-project | Every project document — metadata, classification, status, `storage_path` |
| `document_chunks` | Layer 1 | Per-project | Chunked text + 3072-dim embeddings (immutable) |
| `reference_documents` | Layer 2 | Platform | FIDIC, laws, standards — includes `layer_type` (2a/2b) and `jurisdiction` columns |
| `reference_chunks` | Layer 2 | Platform | Chunked reference text + 3072-dim embeddings (immutable) |
| `contradiction_flags` | — | Per-project | Detected contradictions between document pairs |
| `query_log` | — | Per-project | Immutable audit trail — every query and response |
| `query_jobs` | — | Per-project | Async query pipeline status (PROCESSING/COMPLETE/FAILED) |
| `classification_queue` | — | Per-project | Documents pending manual classification |

---

## 13. Document Taxonomy Summary

176 document types across 10 categories. Full taxonomy in `docs/archive/C1_TAXONOMY_v0.4.xlsx`.

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
2. **Multi-domain structured querying** — no platform delivers simultaneous cross-domain intelligence across legal, commercial, schedule, risk, and financial dimensions aligned to FIDIC, PMBOK, and IFRS
3. **Independence from project parties** — C1 targets independent oversight users (auditors, court experts, lenders, boards) — an unaddressed segment in construction technology
4. **FIDIC-native reasoning** — 22 skill files purpose-built for Red, Yellow, and Silver Book forensic analysis in the GCC context
5. **Document control system ingestion as a forensic pipeline** — Phase 2 integration with Aconex, Docutrack as structured forensic data sources

---

## 15. Items Deferred to Subsequent Phases

- `round_number` column in `query_log` — Migration 014 pending
- Document download endpoint — `GET /projects/{id}/documents/{id}/download`
- Five user roles and their precise permission sets
- Approval workflow layer
- Party ID resolution — `issuing_party_id` and `receiving_party_id` always NULL
- Cross-specialist contradiction detection — `contradiction_cross.py` is a stub
- Integration architecture for document control systems (Phase 2)
- HNSW/IVFFlat vector index — blocked on Supabase pgvector upgrade
- CORS `allow_methods`/`allow_headers` tightening
- `function_search_path_mutable` on RPC functions
- Pricing model and commercial structure
- Platform permanent name (currently codename C1)

See `docs/C1_REMAINING_WORK.md` for the full task register with details.

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
- `VITE_SUPABASE_PUBLISHABLE_KEY` — Supabase anon key (JWT format starting with `eyJ...`)
- `VITE_API_BASE_URL` — Backend URL (e.g., `http://localhost:8000`)

### Database Migrations

Apply migrations 001–013 in order against your Supabase project. See `supabase/migrations/`.

### Ingesting Reference Documents (Layer 2)

```bash
python scripts/ingest_reference.py \
  --file path/to/fidic_red_book_1999.pdf \
  --name "FIDIC Red Book 1999 — Conditions of Contract for Construction" \
  --document-type "FIDIC Conditions of Contract" \
  --standard-body "FIDIC" \
  --edition-year "1999" \
  --layer 2b \
  --jurisdiction international \
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
| `POST` | `/projects/{id}/query/assess` | Yes | Fast Round 0 domain triage (synchronous, ~5s) |
| `POST` | `/projects/{id}/query` | Yes | Submit full query (async — returns query_id) |
| `GET` | `/projects/{id}/queries/{query_id}/status` | Yes | Poll for query result |
| `GET` | `/projects/{id}/query-log` | Yes | Retrieve immutable audit log |
| `GET` | `/projects/{id}/contradictions` | Yes | List contradiction flags |

All authenticated endpoints require `Authorization: Bearer <jwt>` from Supabase Auth.

---

## 18. Repository Structure

```
/
├── README.md
├── CLAUDE.md                          ← Behavioural contract for Claude Code
├── BUILD_LOG.md                       ← Completion log and deferred items
├── requirements.txt
├── Dockerfile
├── Procfile                           ← Legacy reference only
├── railway.json                       ← Dockerfile builder, sh -c start command
├── .env.example
├── .gitignore
├── scripts/
│   └── ingest_reference.py           ← Layer 2 CLI ingestion (--layer, --jurisdiction)
├── docs/
│   ├── SKILLS_STANDARDS.md           ← v1.3 — governs all skill authorship
│   ├── C1_REMAINING_WORK.md          ← active task register
│   └── archive/
│       ├── C1_MULTIAGENT_ARCHITECTURE_PLAN.md
│       ├── C1_QUERY_IMPROVEMENT_PLAN.md
│       └── C1_TAXONOMY_v0.4.xlsx
├── supabase/
│   └── migrations/                   ← 001–013 applied
├── src/
│   ├── config.py
│   ├── clients.py
│   ├── logging_config.py
│   ├── ingestion/                    ← parse, classify, chunk, embed, store
│   ├── agents/
│   │   ├── orchestrator.py           ← process_query, assess_query
│   │   ├── base_orchestrator.py      ← Tier 1 base class
│   │   ├── base_specialist.py        ← Tier 2 base class
│   │   ├── tools.py
│   │   ├── skill_loader.py
│   │   ├── specialist_config.py
│   │   ├── domain_router.py
│   │   ├── retrieval.py              ← four-search hybrid
│   │   ├── contradiction.py
│   │   ├── contradiction_cross.py    ← stub returns []
│   │   ├── synthesis.py
│   │   ├── prompts.py
│   │   ├── audit.py
│   │   └── models.py
│   └── api/
│       ├── main.py
│       ├── auth.py
│       ├── errors.py
│       ├── schemas.py
│       └── routes/
│           ├── health.py
│           ├── projects.py
│           ├── documents.py
│           └── queries.py
├── skills/
│   ├── orchestrators/
│   │   ├── legal/directive.md
│   │   ├── commercial/directive.md
│   │   └── financial/directive.md
│   └── smes/
│       ├── legal/                    ← 5 skill files
│       ├── claims/                   ← 5 skill files
│       ├── schedule/                 ← 6 skill files
│       └── technical/               ← 6 skill files
├── playbooks/
│   └── README.md
└── frontend/
    └── src/
        ├── api/
        ├── auth/
        ├── components/
        │   └── query/
        │       ├── QueryInput.tsx    ← risk mode toggle
        │       ├── Round0Card.tsx    ← domain selection
        │       └── QueryResponse.tsx
        └── pages/
```

---

## 19. Document Control

| Field | Value |
|---|---|
| Version | 0.3 — Three-tier multi-agent architecture complete, 22 skill files, Round 0, risk mode, Layer 2 split |
| Date | April 2026 |
| Status | Confidential — Live |
| Codename | C1 |
