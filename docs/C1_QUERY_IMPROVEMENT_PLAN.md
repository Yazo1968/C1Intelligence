# C1 Intelligence — Query Pipeline Improvement Plan

**Version:** 1.2
**Date:** April 2026
**Status:** Active
**Owner:** Yasser (Product Owner) — Strategic Partner (Claude)

---

## Objectives

1. Fix query pipeline reliability (state lost on Railway restart)
2. Produce professional-grade output for internal auditors, compliance officers, and board-level readers
3. Fix citation quality — document names, references, and clauses instead of UUIDs and chunk numbers
4. Implement footnote/superscript citation rendering (professional report standard)
5. Implement two-stage routing (Round 0 brief + user-controlled depth)
6. Reduce API costs via prompt caching

---

## Governing Rules

- One task per Claude Code session
- Quality Guardian review after every task — CRITICAL/HIGH findings block
- No task begins until the previous is verified in the live system
- Each task is committed and pushed before the next begins
- Agent assignments are explicit in every prompt

---

## Current State Assessment

### What is built and working

- Query endpoint returns HTTP 202 immediately — async with Supabase persistence ✅
- query_jobs table live in Supabase (Migration 009) ✅
- Frontend polls `/queries/{query_id}/status` every 5 seconds ✅
- Async document upload with status polling ✅
- Markdown rendering with remark-gfm (tables, headings, bold) ✅
- All six domain specialists wired and running ✅
- Skill files for Legal & Contractual deployed (5 files) ✅
- FIDIC Layer 2 warehouse populated (1,917 chunks across 6 books) ✅
- Executive report format: all 6 domains declared, exec summary, FLAGS ✅
- System prompt upgraded for professional output standard ✅
- Intelligence quality confirmed: contradictions detected, Particular Conditions amendments flagged, forensic observations produced ✅

### Known defects — status

| # | Defect | Impact | Status |
|---|---|---|---|
| 1 | `_query_status` in-memory — lost on restart | Query results lost on Railway restart | ✅ Fixed — `c7e9fb4` |
| 2 | Error handling uses `error_response()` returns | "Failed to fetch" on query submission | ✅ Fixed — `c7e9fb4` |
| 3 | Synthesis layer: no executive summary, no N/A declarations | Output not professional | ✅ Fixed — `7c2a461` |
| 4 | System prompt: no professional output standard | Inconsistent format, verbose prose | ✅ Fixed — `7c2a461` |
| 5 | Citations use UUID + chunk number | Meaningless to auditors — not professional | ✅ Fixed — `f9f6f1a`, `d80506b`, `350e253` |
| 6 | No footnote/superscript citation rendering | Inline brackets instead of professional footnote format | ✅ Fixed — `310de5d` |
| 7 | No two-stage routing — all domains activate on every query | High cost, slow response, poor UX | 🔴 Active — Phase 3 |
| 8 | Skill files loaded as plain string — no prompt caching | Full input token cost on every query | 🔴 Active — Phase 4 |

---

## Phase 1 — Stabilise the Query Pipeline

### Task 1.1 — Persist query job state to Supabase ✅ COMPLETE

**Commit:** `c7e9fb4`
**What was done:** Replaced `_query_status` in-memory dict with Supabase `query_jobs` table. Migration 009 applied. Service role client used in background task. HTTPException used for all error paths.

---

### Task 1.2 — Fix query submission error handling ✅ COMPLETE

**Commit:** `c7e9fb4` (combined with 1.1)
**What was done:** All `error_response()` returns in `submit_query` and `get_query_status` replaced with `raise HTTPException(...)`.

---

### Task 1.3 — End-to-end query verification ✅ COMPLETE

**Result:** Query confirmed working end-to-end. Intelligence quality assessed as forensic-grade. Legal specialist correctly identified FIDIC Yellow Book 1999, detected two contradictions (Commencement Date, Advance Payment), flagged deletion of Clauses 10.4, 12.2, 11.8, and surfaced six forensically significant observations from a single contract document.

---

### Task 1.4 — Fix citation quality ✅ COMPLETE

**Commit:** `f9f6f1a`
**Agent:** Ingestion Engineer + Agent Orchestrator
**Files:** `src/agents/retrieval.py`, `src/agents/models.py`, `src/agents/tools.py`, `src/agents/base_specialist.py`, migration `010_retrieval_metadata.sql`
**What was done:** `RetrievedChunk` extended with `filename`, `document_reference_number`, `document_date`, `document_type_name`. RPC functions updated via migration 010 to JOIN with `documents` table and return metadata fields. `search_chunks` tool result formatter updated to surface metadata to the agent. Citation instruction in `_SYSTEM_PROMPT_PREFIX` updated — agent instructed to use document name, reference, date, and clause. UUID citations eliminated.

**Problem:**
Citations currently appear as `[Source: 54a0ef82-c8c7-48e5-bda0-5c1d480c7bc8, Chunk 10]`. The UUID is meaningless to an auditor. The chunk number is an internal index. Professional citations must identify the document by name, reference number, date, and the clause or section where the evidence appears.

**Target citation format:**
```
[Contract Agreement, Ref. YD_PROC_PRD-000097.01_CA_23-086, 6 July 2023, Sub-Clause 1.1.7]
[Letter of Award, Ref. YD_PRD-000097.01_Cont-LOA_23-069, 19 June 2023]
[Particular Conditions of Contract, Sub-Clause 4.4]
```

**Root cause:**
The `search_chunks` tool and retrieval layer return `document_id` and `content` to the specialist agent but not the document's human-readable metadata (filename, reference number, date, document type name). The agent cannot cite what it cannot see.

**What to build:**

*Ingestion Engineer — `src/agents/models.py`:*

Extend `RetrievedChunk` to include document metadata:
```python
@dataclass
class RetrievedChunk:
    document_id: str
    chunk_index: int
    content: str
    score: float
    is_reference: bool
    # New fields:
    filename: str | None = None
    document_reference_number: str | None = None
    document_date: str | None = None
    document_type_name: str | None = None
```

*Ingestion Engineer — `src/agents/retrieval.py`:*

Update both Layer 1 RPC functions (`search_chunks_semantic`, `search_chunks_fulltext`) to JOIN with the `documents` table and return the four metadata fields alongside each chunk. Also update the reference chunk retrieval to JOIN with `reference_documents`.

Apply a new migration (010) that replaces the existing RPC functions with updated versions returning the additional columns. The existing functions are defined in migration 006 — migration 010 uses `CREATE OR REPLACE FUNCTION` to update them in place.

*Agent Orchestrator — `src/agents/base_specialist.py`:*

Update the citation instruction in `_SYSTEM_PROMPT_PREFIX`:

```
Every factual claim must cite its source using this format:
[Document Type/Name, Ref. {reference_number if available}, {date if available}, {clause or section if identifiable from content}]

Examples:
[Contract Agreement, Ref. YD_PROC_PRD-000097.01_CA_23-086, 6 July 2023, Sub-Clause 1.1.7]
[Letter of Award, Ref. YD_PRD-000097.01_Cont-LOA_23-069, 19 June 2023]
[Particular Conditions, Clause 10.4]

If document metadata is unavailable, use: [filename, Chunk chunk_index]
Never use document UUIDs in citations.
```

*Agent Orchestrator — `src/agents/tools.py`:*

Update the `search_chunks` tool result formatting to include the new metadata fields so the agent sees them in tool call results alongside the content.

**Verification:**
Run the query: *"What is the contract type, who are the parties, and what are the key contractual dates?"*
Confirm citations read as document names and references, not UUIDs and chunk numbers.

**QG checks:**
- No UUID appears in any citation in the output
- Document reference numbers appear where extracted during ingestion
- Dates appear where available
- Clause/section references appear where identifiable from chunk content
- Existing retrieval functionality unchanged — scores, content, is_reference flag preserved

---

### Task 1.5 — citation_fields from document_types wired into source labels ✅ COMPLETE

**Commits:** `d80506b` (citation_fields wired), `350e253` (chunk index removed from source labels), `d73ed95` (agent prohibited from writing Chunk N)
**Agent:** Ingestion Engineer + Agent Orchestrator
**What was done:** `citation_fields` column from `document_types` table wired into the source label builder so domain-specific citation prefixes (e.g. Sub-Clause, Article, Clause) are used correctly per document type. Chunk index (`Chunk N`) removed entirely from all source label output. Agent system prompt updated to explicitly prohibit writing "Chunk N" or any internal index reference in findings text.

---

## Phase 2 — Professional Output Format

### Task 2.1 — Rewrite synthesis layer for executive report format ✅ COMPLETE

**Commit:** `7c2a461`
**What was done:** `build_response_text` fully rewritten. Executive summary via Claude API call with fallback. All 6 domains declared with NOT_ENGAGED_REASONS dict. Contradictions section. Audit footer with timestamp. `_generate_executive_summary`, `ALL_DOMAINS_ORDERED`, `NOT_ENGAGED_REASONS`, `_config_key_to_display_name` added.

---

### Task 2.2 — Upgrade system prompt for professional output ✅ COMPLETE

**Commit:** `7c2a461` (combined with 2.1)
**What was done:** OUTPUT STANDARD block added to `_SYSTEM_PROMPT_PREFIX`. FLAG/INFORMATIONAL classification, citation format instruction, missing document declaration, director-level writing standard.

---

### Task 2.3 — Output quality review ✅ COMPLETE

**Result:** Output confirmed forensic-grade on first real query against an actual Abu Dhabi contract. Tables rendering correctly. FLAGS classified. Particular Conditions amendments detected. Two issues identified: citation format (Task 1.4) and footnote rendering (Task 2.4).

---

### Task 2.4 — Footnote/superscript citation rendering ✅ COMPLETE

**Commit:** `310de5d`
**Agent:** API Engineer (frontend)
**Files:** `frontend/src/components/query/SpecialistFindingCard.tsx`, new `parseCitations` utility
**What was done:** `parseCitations` utility built — scans markdown for citation bracket patterns, replaces inline citations with superscript numbers, builds numbered footnote list. `SpecialistFindingCard` updated to pass findings through `parseCitations` before rendering. Footnote section rendered below findings with separator line, text-xs sizing, and muted colour. Citations render as superscripts in text with full citation detail in section footer.

**Problem:**
Professional audit reports, legal opinions, and due diligence memoranda use numbered superscript citations in text with full citation details in a footnote section at the bottom of each section. Inline `[Source: ...]` brackets are functional but not at the professional presentation standard required by the target audience.

**Target rendering:**

In-text:
*"The Commencement Date is fixed at 23 June 2023.¹ The Letter of Award Appendix states the date as contingent on a Notice to Proceed.²"*

Section footer:
```
───────────────────────────────────────
¹ Contract Agreement, Ref. YD_PROC_PRD-000097.01_CA_23-086, 6 July 2023, Sub-Clause 1.1.7
² Letter of Award, Ref. YD_PRD-000097.01_Cont-LOA_23-069, 19 June 2023, Attachment A
```

**What to build:**

A `parseCitations(markdown: string)` utility that:
1. Scans the markdown string for `[Source: ...]` or `[Document Name, ...]` patterns
2. Replaces each with a superscript number: `<sup>N</sup>`
3. Builds a numbered footnote list from the extracted citations
4. Returns: `{ processedMarkdown: string, footnotes: string[] }`

In `SpecialistFindingCard`:
- Pass `finding.findings` through `parseCitations` before rendering
- Render processed markdown via ReactMarkdown as before
- Render footnote list below findings in a visually distinct section:
  - Smaller font (text-xs), muted colour (text-gray-500), top border separator
  - Each footnote on its own line: `¹ citation text`

**Verification:**
Run a query. Confirm superscript numbers appear at citation points in text, footnote section appears at the bottom of each domain card, and footnotes are numbered sequentially within each domain.

---

## Phase 3 — Two-Stage Routing (Round 0)

**Objective:** Replace the current model (all domains activate, one long wait) with a fast Round 0 brief that the user can read and act on, followed by user-confirmed deep analysis on selected domains.

**Benefits:**
- Initial response in 5–10 seconds
- Cost reduced — only selected domains run at depth
- User control — professionals choose what depth they need
- Documents retrieved shown before analysis runs
- Routing decisions transparent, not invisible

**Prerequisite:** Phase 2 complete including Tasks 1.4 and 2.4.

---

### Task 3.1 — Backend Round 0 classifier

**Agent:** Agent Orchestrator + API Engineer
**Files:** `src/agents/orchestrator.py`, `src/api/routes/queries.py`, `src/api/schemas.py`

**What to build:**

New function `assess_query(request: QueryRequest) -> Round0Assessment`:
1. Run retrieval — same as full query
2. Single Claude API call: domain relevance assessment + headline finding
3. Return structured assessment with PRIMARY / RELEVANT / NOT_APPLICABLE per domain

```python
@dataclass
class DomainRecommendation:
    domain: str
    relevance: str    # "PRIMARY" | "RELEVANT" | "NOT_APPLICABLE"
    reason: str       # one sentence

@dataclass
class Round0Assessment:
    executive_brief: str
    documents_retrieved: list[str]
    domain_recommendations: list[DomainRecommendation]
    default_domains: list[str]   # PRIMARY domains pre-selected
```

New endpoint: `POST /projects/{id}/query/assess` — synchronous, fast.

**Verification:** Response in under 10 seconds with all 6 domains assessed.

---

### Task 3.2 — Frontend Round 0 display with domain selection

**Agent:** API Engineer (frontend)
**Files:** `frontend/src/pages/ProjectWorkspacePage.tsx`, new `Round0Card` component

**New query flow:**
1. Submit → `/query/assess` (fast)
2. Round0Card: brief, documents, domain grid with relevance badges
3. PRIMARY pre-selected, RELEVANT selectable, NOT_APPLICABLE greyed out
4. "Run Analysis" (selected) or "Run All" buttons
5. Full results in existing QueryResponse component

**Verification:** Round 0 card in <10s, domain selection works, Run Analysis triggers full pipeline on selected domains only.

---

### Task 3.3 — Backend full query with domain filter

**Agent:** Agent Orchestrator
**Files:** `src/agents/orchestrator.py`, `src/api/routes/queries.py`, `src/api/schemas.py`

Extend `SubmitQueryRequest` with optional `domains: list[str] | None`. Orchestrator activates only specified domains. Absent = all domains (backward compatible).

**Verification:** Select only Legal & Commercial, confirm only those two appear in results.

---

## Phase 4 — Prompt Caching

**Objective:** Reduce input token cost by caching the static system prompt + skill files per specialist.

**Applicable model:** claude-sonnet-4-6
**Cache lifetime:** 5 minutes, resets on use
**Cost:** Write = full price. Hit = 10% of input price (90% saving)
**Prerequisite:** Phase 3 complete — system prompt must be stable

---

### Task 4.1 — Implement prompt caching in base_specialist

**Agent:** Agent Orchestrator
**Files:** `src/agents/base_specialist.py` — the `messages.create` call only

```python
# Before
"system": system_prompt

# After
"system": [{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}]
```

Log cache usage on every API call. Confirm `cache_read_input_tokens > 0` in Railway logs on second query within 5 minutes.

---

## Summary Table

| Phase | Task | Agent | Status | Commit |
|---|---|---|---|---|
| 1 | 1.1 Persist query state to Supabase | DB Architect + API Engineer | ✅ Complete | `c7e9fb4` |
| 1 | 1.2 Fix query submission error handling | API Engineer | ✅ Complete | `c7e9fb4` |
| 1 | 1.3 End-to-end query test | Yasser | ✅ Complete | — |
| 1 | 1.4 Fix citation quality | Ingestion Engineer + Agent Orchestrator | ✅ Complete | `f9f6f1a` |
| 1 | 1.5 citation_fields wired into source labels | Ingestion Engineer + Agent Orchestrator | ✅ Complete | `d80506b`, `350e253`, `d73ed95` |
| 2 | 2.1 Rewrite synthesis layer | Agent Orchestrator | ✅ Complete | `7c2a461` |
| 2 | 2.2 Upgrade system prompt | Agent Orchestrator | ✅ Complete | `7c2a461` |
| 2 | 2.3 Output quality review | Yasser | ✅ Complete | — |
| 2 | 2.4 Footnote/superscript citation rendering | API Engineer (frontend) | ✅ Complete | `310de5d` |
| 3 | 3.1 Round 0 classifier backend | Agent Orchestrator + API Engineer | 🔴 Pending 2.4 | — |
| 3 | 3.2 Round 0 frontend | API Engineer (frontend) | 🔴 Pending 3.1 | — |
| 3 | 3.3 Domain filter in full query | Agent Orchestrator | 🔴 Pending 3.2 | — |
| 4 | 4.1 Prompt caching | Agent Orchestrator | 🔴 Pending Phase 3 | — |

---

## Notes

**Task 1.4 before Task 2.4.** Citations must be meaningful (document names, not UUIDs) before rendering as footnotes.

**Task 2.4 before Phase 3.** Professional output including citation rendering must be complete before building Round 0 routing on top.

**Phase 4 last.** System prompt caches should only be built once the prompt is stable.

**Phase 3 validation gate.** Before Phase 3 begins, citation quality must be verified and approved.

**FIDIC ingestion note.** Layer 2 ingestion must run on Railway — not locally. All 6 books complete (1,917 chunks).

---

*Document Control: Version 1.2 — April 2026 — Tasks 1.4, 1.5, and 2.4 marked complete with commits; Task 1.5 (citation_fields + chunk index removal) added; defects table updated; Phases 1 and 2 now fully complete.*
