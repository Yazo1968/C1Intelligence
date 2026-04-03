# C1 Intelligence — Multi-Agent Architecture Plan

**Version:** 1.0
**Date:** April 2026
**Status:** Reference document for new session execution
**Owner:** Yasser (Product Owner) — Strategic Partner (Claude)

---

## Purpose

This document is the complete reference for redesigning C1's agent
architecture from six flat parallel specialists into a proper
three-tier multi-agent system. It must be read in full at the start
of any execution session before any code is touched.

---

## The Problem With the Current Architecture

The current system has six equal specialists (legal, commercial,
schedule, technical, claims, governance) all running as flat peers.
Each independently retrieves documents and produces findings. This is
wrong for two reasons:

1. It does not reflect how professional services actually work. A
   lawyer does not independently retrieve documents the same way a
   delay analyst does. A QS does not produce the same type of output
   as a design expert. These are fundamentally different professional
   roles operating at different levels.

2. "Governance & Compliance" is not a forensic discipline. It is an
   output of the other disciplines. It must be removed.

---

## The Target Architecture

### Three-Tier Model

**Tier 1 — Domain Orchestrators**
Professional leads. Own client-facing output. Instruct SMEs.
Do not retrieve documents directly — they frame questions for SMEs.
Agents: Legal, Commercial, Financial, Risk

**Tier 2 — SME Agents**
Subject matter experts. Respond to targeted instructions from any
Tier 1 orchestrator. Hold all skill files. Retrieve documents.
Agents: Claims & Disputes, Schedule & Programme, Technical & Construction

**Tier 0 — Main Orchestrator**
Entry point and traffic controller. Detects project context, activates
the correct Tier 1 orchestrators, sequences rounds, manages the query
job lifecycle. Makes no substantive analytical judgements.

---

## Tier 0 — Main Orchestrator

### Role
- Receives the query and project_id
- Queries Supabase for project context: jurisdiction (derived from
  contract law field), contract type, parties
- Calls domain_router to identify which Tier 1 orchestrators are
  relevant to this query
- Activates Tier 1 orchestrators in correct sequence (Legal and
  Commercial in parallel first, Financial if relevant, Risk if
  requested)
- Passes Tier 1 findings to synthesis layer
- Owns the query_jobs record lifecycle (PROCESSING → COMPLETE/FAILED)
- Owns the audit log write

### What it does NOT do
- Does not retrieve documents
- Does not make analytical judgements
- Does not write skill files
- Does not hold domain knowledge

### Implementation note
Currently `src/agents/orchestrator.py` handles both orchestration
and some analytical logic. In the new architecture, orchestrator.py
becomes a pure router. Analytical logic moves entirely to the Tier 1
orchestrators.

---

## Tier 1 — Domain Orchestrators

### Architecture principle
Each Tier 1 orchestrator is implemented as a class that:
1. Receives the query, project context, and pre-retrieved chunks
2. Determines which SMEs it needs to invoke for this specific query
3. Invokes those SMEs with targeted, specific questions (not the
   user's raw query)
4. Synthesises SME responses into its own professional opinion
5. Returns a DomainFindings object with its assessment

### Orchestrator directives (not skill files)
Each Tier 1 orchestrator has a directive file (markdown) that defines:
- Professional role and output standard
- Which SMEs it can instruct and for what purpose
- Output format requirements
- Quality standard expected

Directive files live in: `skills/orchestrators/[domain]/directive.md`
They are lighter than skill files — role definition, not analytical
frameworks.

---

### Legal Orchestrator

**Professional role:** Senior legal counsel assessing the contractual
and compliance position.

**Can instruct:**
- Claims & Disputes SME: for notice compliance, time bar assessment,
  entitlement basis analysis
- Schedule & Programme SME: for time-related legal questions (delay,
  time at large, extension entitlement)
- Technical & Construction SME: for design liability, defect
  liability, specification non-compliance with legal implications

**Own output (does not delegate to SME):**
- Contract assembly assessment (FIDIC book type, document hierarchy,
  order of precedence, completeness)
- Party identification and contract administrator identity
- Key contractual dates and securities
- Particular Conditions amendments assessment
- Governing law and dispute resolution mechanism
- External compliance: statutory obligations (decennial liability,
  UAE Civil Code, jurisdiction-specific law)
- Internal compliance: DOA compliance, approval authority, procurement
  governance (draws from L2a)

**Skill files (current — 5 built, reclassify as Legal SME skills):**
These currently sit with the legal specialist. In the new architecture
they move to the Legal SME (see below). The Legal orchestrator uses
its directive to instruct the Legal SME for these assessments.

**Layer 2 usage:**
- L2b: FIDIC General Conditions, jurisdiction law (UAE/KSA/Qatar)
- L2a: Internal DOA matrix, procurement policies, approval thresholds

---

### Commercial Orchestrator

**Professional role:** Senior quantity surveyor / commercial manager
assessing the commercial and contractual commercial position.

**Can instruct:**
- Claims & Disputes SME: for variation and change entitlement,
  dispute on valuations
- Schedule & Programme SME: for programme-cost relationships,
  delay cost, prolongation
- Technical & Construction SME: for technical basis of valuations,
  materials and workmanship costs, defect rectification costs

**Own output:**
- Payment certification assessment (IPC review, payment application,
  deductions)
- Variations and change control (VO pricing, BOQ, dayworks)
- Cost reimbursement (open-book, cost-plus, overhead and profit)
- Retention and securities (retention calculations, bond instruments)
- Final account status

**Skill files:** None at present. To be authored in Phase 3 of this
plan.

**Layer 2 usage:**
- L2b: FIDIC Cl.12/13/14, jurisdiction payment law, VAT regulations

---

### Financial Orchestrator

**Professional role:** Project financial controller / CFO-level
assessment of financial exposure and performance.

**Can instruct:**
- Schedule & Programme SME: for EVM data (earned value, planned
  value, actual cost, schedule variance, cost variance)
- Commercial orchestrator output: as input to financial forecasting
- Claims & Disputes SME: for financial exposure from claims

**Own output:**
- Budget vs actual analysis
- Earned Value Management (EVM) metrics: CPI, SPI, EAC, ETC, VAC
- Cash flow assessment
- Cost overrun / underrun analysis
- Financial risk exposure quantification
- Lender/investor-level financial reporting

**Skill files:** None at present. To be authored in Phase 4 of this
plan.

**Layer 2 usage:**
- L2b: IFRS standards, jurisdiction financial reporting requirements
- L2a: Internal budget frameworks, financial approval thresholds

**Note:** This is a new orchestrator not present in the current
system. Requires new SpecialistConfig entry and directive file.

---

### Risk Orchestrator

**Professional role:** Risk is a reporting mode, not a standalone
agent. It is activated by a "risk report" query and reframes what
Legal, Commercial, and Financial produce.

**Mechanism:**
When Risk is activated, the main orchestrator passes a risk-framing
context alongside the query to Legal, Commercial, and Financial.
Each of those orchestrators produces its output with risk-oriented
framing — flagging exposures, quantifying likelihood, rating severity.

Risk does NOT run as a separate agent after the others. It modifies
what the others are asked to produce.

**Output:** A cross-domain risk register synthesised from Legal,
Commercial, and Financial risk-framed findings. Contains:
- Risk ID
- Domain (legal/commercial/financial)
- Description
- Likelihood (HIGH/MEDIUM/LOW)
- Impact (HIGH/MEDIUM/LOW)
- Overall rating (HIGH/MEDIUM/LOW)
- Recommended action

**Implementation:** Risk activation is a flag on the query request
(`risk_mode: bool`). When true, the system prompt for each Tier 1
orchestrator includes the risk framing directive. The synthesis layer
assembles findings into risk register format.

---

## Tier 2 — SME Agents

### Architecture principle
- All skill files live with SMEs
- An SME is invoked with a specific targeted question from a Tier 1
  orchestrator, not the user's raw query
- An SME can be invoked by multiple Tier 1 orchestrators on the
  same query (Legal asks one question, Commercial asks another)
- SMEs retrieve documents using the existing hybrid retrieval
  (Layer 1 + Layer 2)
- SMEs return structured findings to the invoking orchestrator,
  not to the synthesis layer directly
- SME output is consumed by Tier 1 orchestrators, not shown
  directly to the user

### Implementation note
SMEs use the existing BaseSpecialist agentic loop. The change is:
- Their input is a targeted question from a Tier 1 orchestrator
  (not the user's raw query)
- Their output goes back to the orchestrator that invoked them
- They may be invoked multiple times per query by different
  orchestrators

---

### Legal SME

**Absorbs:** The five current legal skill files (reclassified from
the Legal specialist to the Legal SME)

**Skills:**
1. `contract_assembly.md` — FIDIC book type, document hierarchy,
   order of precedence, document completeness (BUILT ✅)
2. `engineer_identification.md` — contract administrator identity,
   authority levels, notice routing (BUILT ✅)
3. `notice_and_instruction_compliance.md` — time bars, Sub-Clause
   20.1/20.2, formal instructions (BUILT ✅)
4. `entitlement_basis.md` — contractual basis for claims, Particular
   Conditions amendments, variation entitlement (BUILT ✅)
5. `key_dates_and_securities.md` — commencement, completion, DNP,
   performance bond, retention (BUILT ✅)

**Invoked by:** Legal orchestrator (primary), Risk (when activated)

**Layer 2:** L2b — FIDIC General Conditions

---

### Claims & Disputes SME

**Skills (all to be authored):**
1. `notice_compliance.md` — notice requirements, time bars,
   form and content of valid notices, Sub-Clause 20.2.1 (2017) /
   20.1 (1999)
2. `eot_quantification.md` — delay event analysis, concurrent delay,
   as-built programme, SCL Protocol methodology
3. `prolongation_cost.md` — prolongation cost assessment, site
   overhead, staff costs, finance charges
4. `disruption.md` — loss of productivity, measured mile, global
   claim assessment
5. `dispute_resolution_procedure.md` — DAB/DAAB process, NOD,
   arbitration procedure, limitation periods

**Invoked by:** Legal orchestrator, Commercial orchestrator,
Risk (when activated)

**Layer 2:** L2b — FIDIC Cl.20/21, ICC Rules, DIAC Rules,
jurisdiction dispute law

---

### Schedule & Programme SME

**Skills (all to be authored, enhanced with cost/EVM):**
1. `programme_assessment.md` — baseline programme review, as-built
   comparison, update analysis, Primavera/P6 standards
2. `critical_path_analysis.md` — CPM methodology, float analysis,
   critical activity identification, TIA methodology
3. `delay_identification.md` — delay events, excusable vs
   compensable, employer risk events, contractor risk events
4. `acceleration.md` — acceleration instructions, cost of
   acceleration, time-cost tradeoff
5. `time_at_large.md` — prevention principle, LD enforceability,
   reasonable time
6. `evm_and_cost_reporting.md` — Earned Value Management, CPI/SPI,
   EAC/ETC/VAC, cost performance reporting, budget vs actual ← NEW

**Invoked by:** Legal orchestrator, Commercial orchestrator,
Financial orchestrator, Risk (when activated)

**Layer 2:** L2b — FIDIC Cl.8, SCL Delay and Disruption Protocol,
Primavera standards, AACE International

---

### Technical & Construction SME

**Name change from "Technical & Design" — scope expanded to include
site activities**

**Skills (all to be authored):**
1. `design_liability.md` — design responsibility scope, fitness for
   purpose, professional indemnity, decennial liability (Art.880)
2. `specification_compliance.md` — spec requirements, material
   compliance, workmanship standards, non-conformance
3. `rfi_and_submittal_review.md` — RFI log analysis, submittal
   register, design development, Engineer responses
4. `ncr_management.md` — non-conformance records, remediation,
   defect patterns, root cause
5. `site_execution.md` — site diaries, progress records, method
   statements, work permits, inspection records, resource reports ← NEW
6. `testing_and_commissioning.md` — test certificates, TAC/DLP
   defects, handover obligations, Taking-Over Certificate

**Invoked by:** Legal orchestrator, Commercial orchestrator,
Financial orchestrator (for cost of defects), Risk (when activated)

**Layer 2:** L2b — FIDIC Cl.4/7/9/10/11/12, UAE building codes,
ISO standards, Dubai/Abu Dhabi Municipality regulations

---

## Data Warehouse — Revised Layer Structure

### Layer 1 — Project documents (unchanged)
Project-specific uploaded documents. RLS scoped per project.
Tables: `documents`, `document_chunks`
Ingestion: Docling via upload endpoint

### Layer 2a — Internal reference (NEW — currently conflated with L2b)
Organisation-specific. Policies, DOA matrices, procurement procedures,
delegation frameworks, internal governance documents.
Platform-wide but organisation-specific — future: org-scoped.
Tables: `reference_documents`, `reference_chunks` (tag: `internal`)
Ingestion: CLI script with `--layer 2a` flag

### Layer 2b — Eternal reference (currently: all of Layer 2)
Universal and jurisdiction-tagged. FIDIC books, local construction
law, regulations, standards (ISO, AACE, SCL Protocol).
Structured by jurisdiction: UAE, KSA, Qatar, International.
Tables: `reference_documents`, `reference_chunks` (tag: `eternal`,
`jurisdiction` column)
Ingestion: CLI script with `--layer 2b --jurisdiction [uae|ksa|qatar]`
Current content: 6 FIDIC books, 1,917 chunks (all L2b, international)

### Migration required
Add `layer_type TEXT CHECK (layer_type IN ('2a', '2b'))` column to
`reference_documents`. Add `jurisdiction TEXT` column for L2b docs.
All existing 6 FIDIC reference documents tagged as `2b`,
`jurisdiction = 'international'`.

---

## Current State — What Is Built vs What Needs Building

### Built and working ✅
- BaseSpecialist agentic loop (tools, multi-round, JSON output)
- Hybrid retrieval (L1 + L2, 4-search)
- Citation metadata pipeline (document name, ref, date, citation_fields)
- Professional report format (executive summary, 6 domains declared,
  FLAGS, footnote citations)
- Async query pipeline (query_jobs, Supabase persistence)
- Markdown rendering with remark-gfm
- 22 SME skill files across 4 domains: Legal (5), Claims (5),
  Schedule & Programme (6), Technical & Construction (6) — all
  authored against SKILLS_STANDARDS.md v1.3
- Migration 001–011 applied

### Needs building (this plan)
- Three-tier orchestration architecture
- Tier 1: Legal, Commercial, Financial orchestrators with directive files
- Risk reporting mode
- SME invocation mechanism (Tier 1 → Tier 2 tool calls)
- Legal SME (reclassify existing skill files)
- Claims & Disputes SME (5 skill files)
- Schedule & Programme SME (6 skill files including EVM)
- Technical & Construction SME (6 skill files)
- Layer 2a/2b split (migration + tagging)
- Round 0 routing (from C1_QUERY_IMPROVEMENT_PLAN.md Phase 3)
- Prompt caching (from C1_QUERY_IMPROVEMENT_PLAN.md Phase 4)

---

## Implementation Phases

---

### Phase A — Foundation: Three-Tier Architecture

**Prerequisite:** None
**Goal:** Replace flat six-specialist model with three-tier model
**No skill files authored in this phase — architecture only**

#### Task A.1 — Rename and reclassify existing domains

**Agent:** Agent Orchestrator + DB Architect

Rename `governance` domain to nothing — remove it entirely.
Add `financial` domain as new Tier 1 orchestrator.
Reclassify `legal`, `commercial` as Tier 1 orchestrators.
Reclassify `claims`, `schedule`, `technical` as Tier 2 SMEs.

Changes:
- `specialist_config.py`: Add round type field `tier: int`
  (1 = orchestrator, 2 = SME). Remove `governance`. Add `financial`.
  Update round_assignment values.
- `orchestrator.py`: Remove governance from DOMAIN_TO_CONFIG_KEY
  and ALL_DOMAINS_ORDERED. Add financial. Update NOT_ENGAGED_REASONS.
- `prompts.py`: Update DOMAIN_DISPLAY_NAMES. Add financial.
- `skills/`: Create `skills/orchestrators/` directory for directive
  files. Rename `skills/legal/` → `skills/smes/legal/`.
  Create `skills/smes/claims/`, `skills/smes/schedule/`,
  `skills/smes/technical/` (empty, ready for skill files).
- `skill_loader.py`: Update path logic to load from new locations.

#### Task A.2 — SME invocation tool

**Agent:** Agent Orchestrator

Add a new tool `invoke_sme` to `tools.py` that a Tier 1
orchestrator can call to get a targeted response from a Tier 2 SME.

```python
def invoke_sme(
    sme_domain: str,        # "claims" | "schedule" | "technical"
    question: str,          # specific targeted question
    project_id: str,
    retrieved_chunks: list[dict],
    context: str | None,    # relevant context from orchestrator
) -> dict:                  # SME findings as structured dict
```

The tool instantiates the requested SME, runs it with the targeted
question (not the user's raw query), and returns the findings.

This replaces the current ThreadPoolExecutor parallel model for
SME activation. Tier 1 orchestrators decide when and whether to
invoke SMEs based on what the query needs.

#### Task A.3 — Tier 1 orchestrator base class

**Agent:** Agent Orchestrator

Create `src/agents/base_orchestrator.py`:
- Similar to BaseSpecialist but for Tier 1 orchestrators
- Has access to `invoke_sme` tool
- Has access to `search_chunks` tool (for its own retrieval needs)
- Loads directive file instead of skill files
- Returns `DomainFindings` (same schema as current SpecialistFindings)
- System prompt framing: professional lead, not SME

#### Task A.4 — Directive files for existing Tier 1 orchestrators

**Agent:** Yasser + Strategic Partner (knowledge authorship)

Write directive files for Legal and Commercial orchestrators.
These define professional role, SME instruction authority, output
format. Not skill files — lighter, higher level.

Files to create:
- `skills/orchestrators/legal/directive.md`
- `skills/orchestrators/commercial/directive.md`

#### Task A.5 — Update main orchestrator routing

**Agent:** Agent Orchestrator

Update `orchestrator.py` `process_query` function:
- Round 1: Activate Legal and Commercial as Tier 1 orchestrators
  (each may invoke SMEs internally)
- Round 2: Activate Financial if query is financial in nature
- Round 3: If risk_mode, add risk framing to all Tier 1 prompts
- Remove the separate Round 2 for claims/schedule/technical —
  these are now invoked by Tier 1 orchestrators as needed

**Verification:** Run query "What is the contract type, who are the
parties, and what are the key contractual dates?" — output should
be identical in quality to current system.

---

### Phase B — Skill Migration and New SME Skill Files

**Prerequisite:** Phase A complete and verified

#### Task B.1 — Legal SME skill files ✅ COMPLETE

Five Legal SME skill files redrafted against SKILLS_STANDARDS.md v1.3
and committed to `skills/smes/legal/`. Commit: `8bccc5b`

#### Task B.2 — Claims & Disputes SME skill files ✅ COMPLETE

5 skill files committed to `skills/smes/claims/`. Commit: `8bccc5b`

#### Task B.3 — Schedule & Programme SME skill files ✅ COMPLETE

6 skill files committed to `skills/smes/schedule/`. Commit: `efdb009`

#### Task B.4 — Technical & Construction SME skill files ✅ COMPLETE

6 skill files committed to `skills/smes/technical/`. Commit: `cca32c2`

---

### Phase C — Financial Orchestrator

**Prerequisite:** Phase B complete

#### Task C.1 — Financial orchestrator implementation

**Agent:** Agent Orchestrator

Add financial as a full Tier 1 orchestrator:
- New `SpecialistConfig` entry with tier=1
- Directive file: `skills/orchestrators/financial/directive.md`
- Invokes Schedule SME for EVM data
- Invokes Commercial orchestrator output as financial input
- Produces: budget vs actual, EVM metrics, cash flow, financial
  exposure quantification

#### Task C.2 — Financial orchestrator directive file

**Agent:** Yasser + Strategic Partner (knowledge authorship)

Write `skills/orchestrators/financial/directive.md` defining the
CFO/project controller role, EVM output format, financial reporting
standard.

---

### Phase D — Risk Reporting Mode

**Prerequisite:** Phase C complete

#### Task D.1 — Risk mode flag and framing

**Agent:** Agent Orchestrator

Add `risk_mode: bool` to `SubmitQueryRequest` schema.
When `risk_mode=True`:
- Each Tier 1 orchestrator receives an additional risk-framing
  directive in its system prompt
- The risk directive instructs them to frame findings as risk
  exposures with likelihood, impact, and severity rating
- Synthesis layer assembles output as a risk register when
  risk_mode is True

#### Task D.2 — Frontend risk report trigger

**Agent:** API Engineer (frontend)

Add a "Risk Report" button/toggle to the query interface.
Sets `risk_mode=True` on submission.
Renders risk register format in output (table: ID, domain,
description, likelihood, impact, rating, action).

---

### Phase E — Layer 2 Split and Jurisdiction Tagging

**Prerequisite:** Phase A complete (can run in parallel with B, C, D)

#### Task E.1 — Migration: layer_type and jurisdiction columns

**Agent:** DB Architect (Claude can apply via Supabase MCP)

```sql
ALTER TABLE reference_documents
ADD COLUMN layer_type TEXT NOT NULL DEFAULT '2b'
  CHECK (layer_type IN ('2a', '2b'));

ALTER TABLE reference_documents
ADD COLUMN jurisdiction TEXT;

-- Tag existing FIDIC books
UPDATE reference_documents
SET layer_type = '2b', jurisdiction = 'international';
```

#### Task E.2 — Update ingest_reference.py CLI

**Agent:** Ingestion Engineer

Add `--layer` flag (`2a` or `2b`) and `--jurisdiction` flag to
`scripts/ingest_reference.py`.
Populate `layer_type` and `jurisdiction` columns on ingestion.

#### Task E.3 — Update retrieval to pass layer context

**Agent:** Ingestion Engineer

The RPC functions currently search all reference_chunks.
Add optional `p_layer_type` and `p_jurisdiction` parameters.
Tier 1 orchestrators can specify which layer to retrieve from —
Legal retrieves L2b (FIDIC), also L2a (DOA policies).

---

### Phase F — Round 0 Routing and Prompt Caching

**Prerequisite:** Phase A complete
**Source:** C1_QUERY_IMPROVEMENT_PLAN.md Tasks 3.1–3.3 and 4.1

These tasks are defined in detail in C1_QUERY_IMPROVEMENT_PLAN.md
and are not repeated here. Execute after Phase A is stable.

---

## Governing Rules for Execution

1. One task at a time. QG review after every task. No task begins
   until the previous is verified in the live system.

2. After any architectural change, run the validation query:
   "What is the contract type, who are the parties, and what are
   the key contractual dates?" Output quality must be equal to or
   better than the current system before proceeding.

3. Skill file authorship (Phases B, C, D) follows SKILLS_STANDARDS.md
   v1.2. Yasser reviews every skill file as domain expert before
   commit.

4. The five existing Legal skill files are the quality benchmark
   for all new skill file authorship.

5. The main orchestrator never makes analytical judgements.
   If orchestrator.py is gaining analytical logic, that is a
   design failure — move it to the relevant Tier 1 orchestrator.

6. SME skill files contain no hardcoded project facts. All
   project-specific data comes from the warehouse.

7. Directive files are lighter than skill files — role definition
   and output format only. No analytical frameworks in directives.

---

## Key Technical References

**Repository:** github.com/Yazo1968/C1Intelligence (main branch)
**Frontend:** https://c1intelligence.vercel.app (Vercel)
**Backend:** https://web-production-6f2c4.up.railway.app (Railway)
**Supabase:** bkkujtvhdbroieffhfok (EU West 1)

**Stack (locked):** Docling + tiktoken 450-token chunks + Gemini
embeddings gemini-embedding-001 3072 dims + pgvector sequential scan
+ Claude API claude-sonnet-4-6 + FastAPI + Supabase + Vercel + Railway

**Key files to read at session start (always):**
- `CLAUDE.md` — behavioural contract
- `docs/AGENT_PLAN.md` — v1.4 (superseded by this document for
  architecture, but still governs skill authorship standards)
- `docs/SKILLS_STANDARDS.md` — v1.2, governs all skill authorship
- `docs/C1_QUERY_IMPROVEMENT_PLAN.md` — v1.1, Phases 3+4 still active
- `docs/C1_MULTIAGENT_ARCHITECTURE_PLAN.md` — this document

**Supabase state at plan creation:**
- 12 tables, 11 migrations applied (001–011)
- 4 RPC functions returning full document metadata + citation_fields
- 176 document types with citation_fields set
- 6 FIDIC reference books, 1,917 chunks (all Layer 2)
- query_jobs table live

**Agent files (current):**
- `src/agents/base_specialist.py` — agentic loop (becomes base for SMEs)
- `src/agents/orchestrator.py` — main orchestrator (to be refactored)
- `src/agents/specialist_config.py` — domain config (to be extended)
- `src/agents/tools.py` — search_chunks tool (invoke_sme to be added)
- `src/agents/retrieval.py` — hybrid retrieval (L1+L2, 4-search)
- `src/agents/skill_loader.py` — dynamic skill loading from DB
- `src/agents/domain_router.py` — query-to-domain mapping

**Skills (current):**
- `skills/legal/` — 5 skill files (to migrate to `skills/smes/legal/`)
- `skills/claims/` — empty (claims SME skills to be authored)

---

## What This Plan Does Not Change

- The BaseSpecialist agentic loop — SMEs use it unchanged
- The hybrid retrieval pipeline — unchanged
- The citation quality pipeline — unchanged
- The professional report format — unchanged
- The async query pipeline — unchanged
- The frontend rendering — unchanged (except risk register in Phase D)
- SKILLS_STANDARDS.md — still governs all skill authorship
- The 450-token chunk size and 3072-dim embedding — locked

---

*Document Control: Version 1.0 — April 2026 — Initial multi-agent
architecture plan. Supersedes AGENT_PLAN.md v1.4 for architecture
decisions. AGENT_PLAN.md v1.4 remains authoritative for skill
authorship standards and Phase 1-3 history.*
