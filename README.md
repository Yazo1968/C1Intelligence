# C1 — Construction Documentation Intelligence Platform

**Codename:** C1
**Version:** Pre-PRD v0.1
**Status:** Confidential — Active Development
**Market:** GCC — UAE, Saudi Arabia, Qatar
**Date:** March 2026

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

**Contradiction preservation** — When the same information appears in multiple documents with different values, C1 does not resolve the contradiction. It retains all versions, records the source of each, and flags the discrepancy. This is a core feature, not a deficiency. The ability to surface and interrogate contradictions is precisely what makes the platform valuable in audit, legal, and dispute contexts.

---

## 4. Who C1 Serves

C1 is designed for a limited number of senior, high-permission users. It is not a mass-user platform. It serves individuals and teams who require independent, authoritative insight into a project's documentation record:

- Audit departments conducting forensic project reviews
- Compliance and governance officers monitoring contractual adherence
- Board members and executive leadership requiring decision-support on distressed or complex projects
- Legal counsel preparing or defending claims and disputes
- Court-appointed or arbitration experts conducting independent project assessments
- Lenders and investors conducting due diligence on active or distressed projects
- Risk officers assessing exposure at key project milestones

The buyer can be any party who needs the truth: a project owner auditing their delivery chain, a contractor defending a claim, a law firm representing either side, or a regulatory body reviewing compliance. The platform's value is party-agnostic.

---

## 5. What C1 Is Not

- Not a project management system (Primavera, MS Project, Procore)
- Not a document management or document control system (Aconex, Docutrack, SharePoint)
- Not an ERP or financial management system
- Not a collaboration or communication tool
- Not intended to replace operational workflows or systems

The operational technology market for construction is saturated. C1 occupies the space above it.

---

## 6. Core Architecture

### 6.1 The Data Warehouse

The foundation of C1 is a structured data warehouse purpose-built for construction documentation. Unlike a document repository, the warehouse is not a passive store of files. It is an active, categorised, structured environment where documents are ingested, classified, and their content — including all metadata — is parsed, indexed, and made available for intelligent querying.

The warehouse does not resolve contradictions. It retains all versions of conflicting information, records the source and metadata of each, and flags discrepancies. This is the core forensic value of the platform.

### 6.2 Document Taxonomy — Two Layers

All documents within the warehouse are classified according to a predefined taxonomy structured in two layers:

**Layer 1 — Project-specific documents**
Documents generated in the course of a specific project by any party: contracts, drawings, specifications, correspondence, claims, notices, reports, valuations, schedules, approvals. These are classified across 10 categories and 176 document types. Full taxonomy is in `C1_TAXONOMY_v0.4.xlsx`.

**Layer 2 — Reference documents**
Global, static, non-project-specific documents that provide the regulatory, legal, and standards framework against which project conduct is evaluated. These include:
- FIDIC conditions of contract (1999 and 2017 editions)
- PMBOK and other professional project management standards
- IFRS accounting standards applicable to project accounting and valuations
- Applicable laws and regulations (jurisdiction-specific)
- Government authority policies and requirements
- Delegation of Authority matrices
- Market benchmarks and cost data

Reference documents may be ingested manually, extracted from integrated document control systems, or sourced via pre-approved API or MCP connections to authoritative external sources. All reference document sources are subject to a defined authority matrix and approval flow.

### 6.3 Document Ingestion — Phase 1 (Manual Upload)

C1 Phase 1 uses Google Gemini File Search as the document ingestion and retrieval engine. Gemini handles upload, OCR, text extraction, chunking, embedding, and semantic indexing. C1 applies a governance layer on top of Gemini that handles classification, validation, and approval.

The ingestion governance process for every manually uploaded document:

1. **Document classification** — the user selects the document type from the taxonomy at the point of upload. Claude AI validates the classification by comparing the document content against the selected type.

2. **Validation** — if the document does not match the selected type (e.g. a contract uploaded as a notice), the system flags the discrepancy and asks the user to confirm or reclassify.

3. **Gap identification** — if the document is correctly classified but missing required metadata fields, the system prompts the user to supply the missing data.

4. **User override** — if the user proceeds despite flags or gaps, the document is ingested together with all flags, questions raised, and the user's responses as embedded notes. This transfers accountability to the user and creates an auditable record of the conscious decision.

5. **Approval flow** — each document type is linked to one of three predefined approval workflows, each requiring action from designated roles within the platform's authority matrix before the document is admitted to the warehouse. No document ingestion is a unilateral act.

### 6.4 Document Ingestion — Phase 2 (Integrated System Ingestion)

Phase 2 will add direct integration with document control systems (Aconex, Docutrack, and similar). Documents extracted from integrated systems carry an established chain of custody from their source system. C1 inherits this chain of custody and does not re-validate it. The platform logs the source, extraction timestamp, and document metadata at the point of ingestion.

---

## 7. Roles, Access, and Authority Matrix

C1 operates on a defined role-based access control model with five user roles. Each role carries specific permissions governing what documents can be uploaded, what queries can be made, and what approval actions can be taken.

No document ingestion decision is a unilateral act. All manually uploaded documents pass through one of three approval flows before entering the warehouse. The authority matrix ensures no single user can admit documents to the warehouse without appropriate oversight, creating a defensible and compliant ingestion record.

The five roles and three approval flow types will be defined in detail in a subsequent specification.

---

## 8. Intelligence and Query Layer

### 8.1 Purpose

The intelligence layer accepts natural language queries and returns substantive, cross-referenced, source-attributed responses drawn from the documents in the warehouse at the time of the query.

### 8.2 Multi-Domain Response Architecture

A query posed in one domain — legal, financial, schedule, risk, or compliance — does not receive a tunnel-visioned response. The orchestration layer identifies which domains are relevant and engages the appropriate domain reasoning, then aggregates a unified response that surfaces the full landscape of implications.

A query about the validity of a delay claim surfaces not only the legal and contractual position, but also the schedule evidence, the cost implications, the risk exposure, and any compliance or governance dimensions.

### 8.3 Agent Architecture

```
User Query
    ↓
Master Orchestrator (Claude API)
    ↓
Domain Identification — which of 6 domains are relevant?
    ↓
Gemini File Search — retrieves relevant document chunks with citations
    ↓
Domain Specialists (Claude API):
    Legal & Contractual / Commercial & Financial / Schedule & Programme /
    Technical & Design / Claims & Disputes / Governance & Compliance
    ↓
Contradiction Detection — flags conflicts across retrieved documents
    ↓
Confidence Classification — GREEN / AMBER / RED / GREY
    ↓
Response Synthesis — unified cross-domain answer with full source attribution
    ↓
Audit Log — immutable record written to Supabase query_log
    ↓
User
```

### 8.4 Confidence States

Every C1 response carries one of four confidence states:

| State | Meaning |
|---|---|
| 🟢 GREEN | Answer is consistent across all retrieved documents |
| 🟡 AMBER | Answer is present but incomplete or partially supported |
| 🔴 RED | Contradiction detected between documents |
| ⬜ GREY | Insufficient documents in the warehouse to answer |

### 8.5 Auditability of Responses

Every query and every response is logged with a timestamp, the identity of the querying user, and the precise set of documents in the warehouse at the time of the query. This log is immutable and cannot be altered after the fact. It is the forensic record of what was known, what was asked, and what answer was provided — at any given point in time.

---

## 9. Standards and Regulatory Framework

C1 is designed to operate within internationally recognised professional and contractual standards:

- **FIDIC** — governing contractual standard for the majority of construction projects in the platform's target markets. Both 1999 and 2017 Red Book editions are supported. Sub-clause differences between editions are mapped and handled.
- **PMBOK** — professional project management framework underpinning programme and delivery assessment.
- **IFRS** — financial reporting standard applicable to project accounting, valuations, and financial compliance.

The platform is geographically neutral. Jurisdiction-specific regulations and authority requirements are incorporated as reference documents within the taxonomy and governed accordingly.

---

## 10. Illustrative Use Cases

### 10.1 Dispute and Claim Assessment
A legal team preparing for arbitration uploads all project correspondence, notices, claims, and schedule records to the warehouse. They query the platform to reconstruct the timeline of events, identify contradictions between the contractor's claimed delay durations and the programmatic record, and assess the contractual validity of each notice. The platform surfaces the legal, schedule, and commercial dimensions simultaneously. Every query and response is timestamped and exportable as evidence.

### 10.2 Board-Level Project Audit
A board of directors investigating a cost overrun on a major development uses C1 to interrogate the financial and contractual record. The platform identifies discrepancies between approved budgets, variation orders, and reported costs. It surfaces the governance and compliance dimensions of decisions made during the project, flags where required approvals were absent, and provides the board with an independent, documented assessment without relying on the delivery team's narrative.

### 10.3 Lender Due Diligence
A lender reviewing a distressed project uses C1 to assess the status of contractual obligations, the financial exposure across all active contracts, and the risk profile of ongoing claims. The platform aggregates this across all documentation in the warehouse and provides a structured, sourced assessment that the lender can use to inform their position.

### 10.4 Compliance Review
A compliance officer conducting a periodic review of a portfolio of projects uses C1 to verify that contractual obligations, regulatory requirements, and internal governance policies have been met. The platform cross-references project documents against the applicable reference document library and flags non-conformances for escalation.

---

## 11. Technical Stack

| Component | Technology | Purpose |
|---|---|---|
| Document ingestion & retrieval | Google Gemini File Search API | Upload, OCR, chunking, embedding, semantic indexing, retrieval, citations |
| AI agents & reasoning | Anthropic Claude API | Classification, metadata extraction, domain specialists, orchestration, contradiction detection |
| Structured database | Supabase (PostgreSQL) | Relational metadata, contradiction flags, immutable audit log |
| Authentication | Supabase Auth | User accounts, sessions, JWT tokens, row-level security |
| Backend / API | Python — FastAPI | Business logic layer exposing intelligence to the frontend |
| Frontend | To be defined | User interface for document upload, querying, and results |
| Backend hosting | Railway | Hosts the FastAPI backend — deploys directly from GitHub |
| Frontend hosting | Vercel | Hosts and serves the frontend |

### Deployment Architecture

```
User (browser)
    ↓
Vercel — serves the frontend
    ↓  authenticated request (JWT token from Supabase Auth)
FastAPI backend (Railway)
    ↓                    ↓                         ↓
Gemini File Search    Claude API               Supabase
(document content)    (agents & reasoning)     (metadata + auth + audit)
```

### Responsibility Boundaries

**Gemini File Search handles:**
- Document upload, OCR, text extraction
- Chunking and embedding
- Semantic indexing and retrieval
- Citation generation
- Document-level metadata as key-value pairs (project ID, document type, tier, date) — used for filtering at retrieval time

**Claude API handles:**
- Document classification against the taxonomy
- Metadata extraction from document content
- All six domain specialist agents
- Master orchestration
- Contradiction detection
- Response synthesis

**Supabase handles:**
- Projects, parties, contracts, document types — relational structured data
- Document registry — each document's Gemini reference, classification, processing status
- Contradiction flags (project-scoped — never cross-project)
- Immutable query audit log (UPDATE and DELETE blocked by database trigger)
- Classification queue for documents that cannot be auto-classified
- User authentication, sessions, and row-level security

**FastAPI backend handles:**
- Receives requests from the frontend
- Validates user authentication via Supabase Auth JWT
- Orchestrates calls to Gemini, Claude, and Supabase
- Exposes endpoints: create project, upload document, submit query, retrieve audit log

**Vercel handles:**
- Serves the frontend application to users
- No business logic, no API keys, no direct access to backend services

---

## 12. Database Tables

| Table | Purpose |
|---|---|
| `projects` | Each project loaded into C1 |
| `contracts` | Each contract within a project |
| `parties` | Each party with their role from the Party Register |
| `document_types` | 176 document types seeded from taxonomy v0.4 |
| `documents` | Every document ingested — metadata, Gemini reference, classification, status |
| `contradiction_flags` | Detected contradictions between document pairs (project-scoped) |
| `query_log` | Immutable audit trail — every query and response |
| `classification_queue` | Documents pending manual classification |

---

## 13. Document Taxonomy Summary

176 document types across 10 categories. Full taxonomy with formats, tiers, and FIDIC clause references in `C1_TAXONOMY_v0.4.xlsx`.

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

## 15. Items to Be Defined in Subsequent Specifications

- The five user roles and their precise permission sets
- The three document approval flow types and document types mapped to each
- The authority matrix governing reference document ingestion from external sources
- The technical architecture of the approval workflow layer
- The integration architecture for document control systems (Phase 2)
- Pricing model and commercial structure
- Platform permanent name (currently codename C1)

---

## 16. Repository Structure

```
/
├── README.md                    ← This file — single source of truth
├── CLAUDE.md                    ← Behavioural contract for Claude Code
├── C1_TAXONOMY_v0.4.xlsx        ← Document taxonomy (176 types, 10 categories)
├── supabase/
│   └── migrations/              ← Database schema migrations
├── src/
│   ├── agents/                  ← Master orchestrator + 6 domain specialists
│   ├── ingestion/               ← Gemini File Search integration + governance layer
│   └── api/                     ← FastAPI backend
└── tests/                       ← Test suite
```

---

## 17. Document Control

| Field | Value |
|---|---|
| Version | 0.1 Draft |
| Date | March 2026 |
| Status | Confidential — Internal Working Document |
| Codename | C1 |
