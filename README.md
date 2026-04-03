# C1 Intelligence

**Version:** 1.0
**Status:** Confidential — Live
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
| Schema, ingestion, orchestrator, specialists, contradiction, API, frontend | ✅ Complete |
| pgvector migration — self-owned embedding pipeline | ✅ Complete |
| Production fixes, Layer 2 warehouse, file storage | ✅ Complete |
| Query pipeline — citation quality, output format | ✅ Complete |
| Three-tier multi-agent architecture — orchestrators + SME domains | ✅ Complete |
| Risk reporting mode, Round 0 domain triage, domain filtering | ✅ Complete |
| Layer 2 split — layer_type 2a/2b + jurisdiction tagging | ✅ Complete |
| Platform identity overhaul — universal form-agnostic architecture | ✅ Complete |

---

## 1. What C1 Is

C1 Intelligence is a universal construction project intelligence platform.
It investigates, audits, and produces expert-level findings on any
construction project by reasoning across three layers of evidence:

- **Layer 1 — Project:** The project's own documents — contracts of any form,
  correspondence, notices, claims, schedules, payment records, drawings,
  technical reports
- **Layer 2a — Internal:** The organisation's own policies, DOA matrices,
  authority frameworks, internal procedures
- **Layer 2b — External:** Standard forms of contract (FIDIC, NEC, JCT, AIA,
  or any other), professional standards (PMBOK, IFRS, SCL Protocol, AACE),
  applicable laws and regulations

C1 works with whatever the user has ingested. The platform is not tied to
any specific contract form, jurisdiction, or standards framework. If the
warehouse contains FIDIC contracts and PMBOK standards, C1 reasons against
those. If it contains NEC4 and IFRS, C1 reasons against those.

C1 is not a project management system, a document management system, or an
operations tool. It is an independent intelligence and decision-support layer
that serves users who need the truth about a project — regardless of which
party they represent.

---

## 2. The Problem C1 Solves

### 2.1 Fragmentation
Project documentation is distributed across the owner's systems, the PMC's
systems, the contractor's systems, sub-consultants, and document control
platforms. These systems are rarely integrated. There is no single source
of truth.

### 2.2 Inconsistency and Contradiction
The same information often appears in multiple documents with conflicting
values — claim amounts, delay durations, contractual milestones, cost
figures. C1 does not resolve contradictions. It retains all versions,
records the source of each, and flags every discrepancy.

### 2.3 Lack of Cross-Domain Awareness
Project issues are never single-domain. A delay has cost, contractual, and
risk implications simultaneously. C1 synthesises across all domains in
response to a single query.

### 2.4 Absence of Independent Intelligence
Operational systems are operated by the parties being audited. An audit
department, a board, a lender, or a court expert needs a view that is
independent of operations. C1 provides that view.

---

## 3. Core Principles

**Retrieval-first reasoning** — Agents reason from retrieved evidence only.
Every factual claim traces to a specific retrieved document. If a provision
was not retrieved from the warehouse, the output is CANNOT CONFIRM — never
a characterisation from training knowledge.

**Neutrality** — No party allegiance. Outputs reflect the documentation.

**Auditability** — Every query, response, and document set is logged
immutably with a timestamp.

**Cross-domain intelligence** — Legal, commercial, financial, schedule, and
technical dimensions are assessed simultaneously.

**Contradiction preservation** — Contradictions are surfaced, not resolved.

---

## 4. Who C1 Serves

- Audit departments conducting forensic project reviews
- Compliance and governance officers
- Board members and executive leadership on distressed or complex projects
- Legal counsel preparing or defending claims
- Court-appointed or arbitration experts
- Lenders and investors conducting due diligence
- Risk officers assessing exposure at key milestones

---

## 5. Core Architecture

### 5.1 Three-Layer Warehouse

**Layer 1 — Project documents**
Documents generated in the course of a specific project. Classified across
10 categories and 176 document types. Stored in `documents` +
`document_chunks` tables. Project-scoped.

**Layer 2a — Internal reference documents**
Organisation policies, DOA matrices, authority frameworks. Stored in
`reference_documents` with `layer_type = '2a'`. Platform-wide.

**Layer 2b — External reference documents**
Standard forms, laws, professional standards — whatever the platform owner
has ingested. Stored in `reference_documents` with `layer_type = '2b'` and
`jurisdiction` column. Platform-wide.

Currently ingested in Layer 2b: 6 FIDIC books (1,917 chunks). Additional
standards ingested via `scripts/ingest_reference.py` as needed.

### 5.2 Document Ingestion

1. **Parsing** — Docling (PDF text + OCR, DOCX, XLSX)
2. **Classification** — Claude AI against 176-type taxonomy (0.75 threshold)
3. **Metadata extraction** — Claude AI extracts structured fields
4. **Chunking** — tiktoken cl100k_base (450-token target, 50-token overlap)
5. **Embedding** — Gemini Embeddings API, 3072-dimension vectors
6. **Storage** — Atomic write to `document_chunks`
7. **File preservation** — Original stored in Supabase Storage

### 5.3 Query Flow

```
User submits query
    ↓
Round 0 — fast domain triage (~5s, synchronous)
    ↓
User selects domains to run
    ↓
Full analysis (async background task)
    ↓
Hybrid retrieval — Layer 1 + Layer 2 (pgvector, 4-search)
    ↓
Tier 1 — Legal, Commercial, Financial orchestrators (parallel)
    Each loads directive.md, may invoke Tier 2 SMEs
    ↓
Tier 2 — Claims, Schedule, Technical SMEs (on-demand)
    Each loads skill files from skills/smes/{domain}/
    ↓
Cross-specialist contradiction detection
    ↓
Confidence classification — GREEN / AMBER / RED / GREY
    ↓
Response synthesis — unified cross-domain answer
    ↓
Immutable audit log written to query_log
```

### 5.4 Agent Architecture

**Tier 0** — Main orchestrator (router)
**Tier 1** — Legal, Commercial, Financial orchestrators (BaseOrchestrator)
**Tier 2** — Claims, Schedule, Technical SMEs (BaseSpecialist)

All skill files authored using `skills/c1-skill-authoring/`.
All skill files enforce the Evidence Declaration block and retrieval-first
grounding protocol defined in `skills/c1-skill-authoring/references/`.

---

## 6. Confidence States

| State | Meaning |
|---|---|
| 🟢 GREEN | Answer consistent across all retrieved documents |
| 🟡 AMBER | Present but incomplete or partially supported |
| 🔴 RED | Contradiction detected between documents |
| ⬜ GREY | Insufficient documents in warehouse to answer |

---

## 7. Technical Stack

| Component | Technology |
|---|---|
| Document parsing | Docling |
| Chunking | tiktoken cl100k_base |
| Embeddings | Gemini Embeddings API (3072-dim) |
| Vector store | pgvector on Supabase (HNSW halfvec indexes) |
| AI agents | Anthropic Claude API (claude-sonnet-4-6) |
| Database | Supabase PostgreSQL |
| Auth | Supabase Auth |
| File storage | Supabase Storage |
| Backend | FastAPI on Railway (Dockerfile builder) |
| Frontend | React + TypeScript + Tailwind CSS (Vite) on Vercel |

---

## 8. Database Tables

| Table | Purpose |
|---|---|
| `projects` | Each project loaded into C1 |
| `documents` | Project document metadata and status |
| `document_chunks` | Chunked text + embeddings (Layer 1) |
| `reference_documents` | External/internal reference standards (Layer 2a/2b) |
| `reference_chunks` | Reference text + embeddings (Layer 2) |
| `contradiction_flags` | Detected contradictions between document pairs |
| `query_log` | Immutable audit trail |
| `query_jobs` | Async query pipeline status |
| `document_types` | 176-type taxonomy |
| `parties` | Project parties and roles |
| `contracts` | Contracts within a project |
| `classification_queue` | Documents pending manual classification |

---

## 9. API Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/projects` | Create project |
| GET | `/projects` | List projects |
| POST | `/projects/{id}/documents` | Upload document |
| GET | `/projects/{id}/documents` | List documents |
| GET | `/projects/{id}/documents/{doc_id}/download` | Download document |
| POST | `/projects/{id}/query/assess` | Round 0 triage |
| POST | `/projects/{id}/query` | Submit full query |
| GET | `/projects/{id}/queries/{id}/status` | Poll query status |
| GET | `/projects/{id}/query-log` | Audit log |
| GET | `/projects/{id}/contradictions` | Contradiction flags |

---

## 10. Getting Started

### Prerequisites
- Python 3.13+, Node.js 20+
- Supabase project with migrations 001–016 applied
- API keys: Anthropic, Gemini

### Local Development

```bash
git clone https://github.com/Yazo1968/C1Intelligence.git
cd C1Intelligence
cp .env.example .env
pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

cd frontend
npm install
npm run dev
```

### Ingesting Layer 2b Reference Documents

```bash
python scripts/ingest_reference.py \
  --file path/to/standard.pdf \
  --name "Standard name and edition" \
  --layer 2b \
  --jurisdiction international
```

---

## 11. Repository Structure

```
/
├── CLAUDE.md                          ← Session contract for Claude Code
├── README.md
├── BUILD_LOG.md
├── docs/
│   ├── C1_MASTER_PLAN.md             ← Active governing plan
│   ├── SKILLS_STANDARDS.md           ← Warehouse-grounding principles
│   └── archive/                      ← Superseded plans
├── skills/
│   ├── c1-skill-authoring/           ← Skill authorship governance
│   ├── orchestrators/                ← Tier 1 directive files
│   └── smes/                         ← Tier 2 skill files
├── src/
│   ├── agents/                       ← Intelligence layer
│   ├── ingestion/                    ← Document pipeline
│   └── api/                          ← FastAPI routes
├── supabase/migrations/              ← 001–016 applied
├── scripts/
│   └── ingest_reference.py
└── frontend/
```

---

## 12. Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Date | April 2026 |
| Supersedes | README.md v0.3 |
