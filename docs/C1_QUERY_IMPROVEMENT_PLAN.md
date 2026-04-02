# C1 Intelligence — Query Pipeline Improvement Plan

**Version:** 1.0  
**Date:** April 2026  
**Status:** Active  
**Owner:** Yasser (Product Owner) — Strategic Partner (Claude)

---

## Objectives

1. Fix query pipeline reliability (state lost on Railway restart)
2. Produce professional-grade output for internal auditors, compliance officers, and board-level readers
3. Implement two-stage routing (Round 0 brief + user-controlled depth)
4. Reduce API costs via prompt caching

---

## Governing Rules

- One task per Claude Code session
- Quality Guardian review after every task — CRITICAL/HIGH findings block
- No task begins until the previous is verified in the live system
- Each task is committed and pushed before the next begins
- Agent assignments are explicit in every prompt

---

## Current State Assessment

### What is already built and working

- Query endpoint already returns HTTP 202 immediately
- Background task runs the full pipeline
- Frontend already polls `/queries/{query_id}/status` every 5 seconds
- All six domain specialists are wired and running
- Skill files for Legal & Contractual are deployed (5 files)
- FIDIC Layer 2 warehouse is populated (1,917 chunks across 6 books)

### Known defects requiring fixes

| # | Defect | Impact | Phase |
|---|---|---|---|
| 1 | `_query_status` is in-memory — lost on Railway restart | Query results disappear after any deployment or container restart | Phase 1 |
| 2 | Error handling in `submit_query` uses `error_response()` returns instead of HTTPException — may cause serialisation failures | Possible "Failed to fetch" on query submission | Phase 1 |
| 3 | Synthesis layer concatenates domain findings with no executive summary, no N/A declarations, no cross-domain structure | Output does not meet professional report standard | Phase 2 |
| 4 | System prompt prefix does not specify professional output standard — agents produce findings in variable format | Inconsistent output quality | Phase 2 |
| 5 | No two-stage routing — all domains activate on every query regardless of relevance | High cost, slow response, poor UX | Phase 3 |
| 6 | Skill files loaded as plain string — no prompt caching applied | Full input token cost on every query | Phase 4 |

---

## Phase 1 — Stabilise the Query Pipeline

### Task 1.1 — Persist query job state to Supabase

**Agent:** DB Architect + API Engineer  
**Files:** New migration `009_query_jobs.sql`, `src/api/routes/queries.py`  
**Prerequisite:** None

**Problem:**  
`_query_status` is a module-level Python dict. Railway restarts the container on every deployment and may restart under memory pressure. Any query in flight at restart time is lost permanently. The polling frontend receives a 404 and the user sees "Failed to fetch" or a stale loading state.

**What to build:**

*DB Architect — Migration 009:*

```sql
CREATE TABLE query_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    query_text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PROCESSING'
        CHECK (status IN ('PROCESSING', 'COMPLETE', 'FAILED')),
    response JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE query_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users access own query jobs"
    ON query_jobs FOR ALL
    USING (user_id = auth.uid());

CREATE INDEX idx_query_jobs_project_id ON query_jobs(project_id);
CREATE INDEX idx_query_jobs_status ON query_jobs(status);
```

*API Engineer — `queries.py`:*

- Remove `_query_status` dict entirely
- In `submit_query`: insert a `query_jobs` row (status = PROCESSING) using the **service role client** (not the user JWT client — the background task runs outside request context)
- In `_run_query_pipeline`: update the row to COMPLETE with `response` JSONB, or FAILED with `error_message`
- In `get_query_status`: read from `query_jobs` table instead of dict. Use service role client.
- All Supabase calls in the background task must use service role — the JWT has expired by the time the background task reads/writes

**Verification:**
1. Submit a query in the live app
2. Immediately trigger a Railway redeploy (push any trivial commit)
3. Continue polling — result should still be retrievable after restart
4. Check `query_jobs` table in Supabase and confirm row exists with COMPLETE status and response JSON

**QG checks:**
- Service role key used for background task writes (not anon/JWT key)
- RLS policy on `query_jobs` allows user to read own rows only
- Migration applied to live Supabase (not just file added to repo)
- `_query_status` dict fully removed — no remaining references

---

### Task 1.2 — Fix query submission error handling

**Agent:** API Engineer  
**Files:** `src/api/routes/queries.py`  
**Prerequisite:** Task 1.1 complete

**Problem:**  
`submit_query` calls `error_response()` and returns its result. FastAPI expects `HTTPException` to be raised, not a dict to be returned. Returning the wrong type from a typed endpoint may cause a serialisation error that produces an unhandled 500, which the browser reports as "Failed to fetch".

**What to build:**

Replace `error_response()` returns in `submit_query` with proper `raise HTTPException(...)`. Pattern:

```python
# Current — wrong
return error_response(
    status_code=status.HTTP_404_NOT_FOUND,
    error_code="PROJECT_NOT_FOUND",
    message=f"Project {project_id} not found or access denied.",
)

# Correct
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Project not found or access denied.",
)
```

Apply consistently to all error paths in `submit_query` and `get_query_status`.

**Verification:**  
Open the app, submit the query: *"What is the contract type, who are the parties, and what are the key contractual dates?"*  
Confirm: browser network tab shows 202 response to POST within 2 seconds, status message appears in UI, polling begins.

---

### Task 1.3 — End-to-end query verification (no Claude Code)

**Agent:** Yasser — live app test  
**Prerequisite:** Tasks 1.1 and 1.2 complete and deployed

Submit this query against the Alba project:

> *"What is the contract type, who are the parties, and what are the key contractual dates?"*

Wait for response. Screenshot the full output and bring it to the strategic partner for output quality assessment.

This screenshot determines whether Phase 2 changes are needed and exactly what they should target.

---

## Phase 2 — Professional Output Format

**Target audience:** Internal auditors, compliance/governance/risk officers, legal counsel, board members, lenders, dispute resolution professionals.

**Output standard:** The response must read like a section of an internal audit findings report or a legal due diligence memorandum — not like a chat answer. Every factual claim is cited. Every domain is declared even if not applicable. The most critical finding is visible at the top without reading the full report.

---

### Task 2.1 — Rewrite synthesis layer for executive report format

**Agent:** Agent Orchestrator  
**Files:** `src/agents/orchestrator.py` — `build_response_text` function only  
**Prerequisite:** Task 1.3 complete (output quality assessed)

**What to build:**

The new `build_response_text` must produce this structure:

```markdown
## Executive Summary

[3–5 sentences maximum. State: what was assessed, the overall confidence 
level, and the single most significant finding. Written at director level — 
no jargon, no hedging, no filler.]

**Overall Confidence:** GREEN / AMBER / RED / GREY
**Documents in warehouse at query time:** [count]

---

## Domain Assessments

### Legal & Contractual — [CONFIDENCE BADGE]

[findings content — preserved exactly as produced by the specialist]

---

### Commercial & Financial — [CONFIDENCE BADGE]

[findings content]

---

### Claims & Disputes — NOT ENGAGED

*This domain was not activated for this query. Claims & Disputes analysis 
requires notice documents, EOT claims, or dispute correspondence to be 
present in the warehouse.*

---

### Schedule & Programme — NOT ENGAGED

*[reason]*

---

### Technical & Design — NOT ENGAGED

*[reason]*

---

### Governance & Compliance — [CONFIDENCE BADGE]

[findings content]

---

## Contradictions Detected

[If any: each contradiction with both source documents, both values, 
and the field in conflict. If none: "No contradictions detected across 
the documents assessed."]

---

*Audit Reference: [id] · Query submitted: [timestamp]*
```

**Rules for the Executive Summary generation:**

The Executive Summary is the one place where a new Claude API call is needed — it synthesises across all domain findings into a coherent paragraph. This call uses a short, cheap prompt: pass all domain findings as context and ask for a 3-5 sentence executive summary. This is the only synthesis call in the pipeline.

**Rules for "NOT ENGAGED" declarations:**

A domain is declared NOT ENGAGED when it returned GREY confidence (no relevant documents found). The reason text is domain-specific:

| Domain | NOT ENGAGED reason |
|---|---|
| Claims & Disputes | Requires notice documents, EOT claims, or dispute correspondence in the warehouse |
| Schedule & Programme | Requires programme documents, delay records, or progress reports in the warehouse |
| Technical & Design | Requires specifications, drawings, RFIs, or NCRs in the warehouse |
| Governance & Compliance | Requires DOA matrix, committee minutes, or approval chain documents in the warehouse |
| Legal & Contractual | Requires contract documents in the warehouse |
| Commercial & Financial | Requires BOQ, IPC, payment application, or variation documents in the warehouse |

**Verification:**  
Run the same query as Task 1.3. Screenshot the new response. Confirm executive summary appears at top, all six domains are declared, contradictions section present.

---

### Task 2.2 — Upgrade system prompt for professional output

**Agent:** Agent Orchestrator  
**Files:** `src/agents/base_specialist.py` — `_SYSTEM_PROMPT_PREFIX` constant only  
**Prerequisite:** Task 2.1 complete and verified

**Problem:**  
The current system prompt tells the agent to produce a `findings` text string but does not specify what professional standard that text must meet. The result is variable — sometimes structured markdown, sometimes narrative prose.

**What to build:**

Add to `_SYSTEM_PROMPT_PREFIX` after the existing RULES block:

```
OUTPUT STANDARD:
Your findings are read by internal auditors, compliance officers, legal counsel, 
and board-level executives. Write accordingly.

- Use the exact output format defined in your skill files. Do not deviate.
- Every factual claim must cite its source document by document_id in the format:
  [Source: document_id, {document reference or filename}]
- Classify each finding: FLAG (requires attention) or INFORMATIONAL (noted, no action)
- Where a finding is a FLAG, state the implication in one sentence: what risk or 
  obligation does this create?
- If a required document is absent from the warehouse, state explicitly what is 
  missing and what analysis cannot be completed as a result.
- Write at director level. No jargon without definition. No hedging. No filler.
- Findings are not a summary of documents — they are an assessment of the 
  contractual position with conclusions.
```

**Verification:**  
Run the same query. Assess whether citations appear in the output and whether findings are classified as FLAG or INFORMATIONAL.

---

### Task 2.3 — Output quality review (no Claude Code)

**Agent:** Yasser — domain expert review  
**Prerequisite:** Task 2.2 complete and deployed

Run three queries against the Alba project:

1. *"What is the contract type, who are the parties, and what are the key contractual dates?"*
2. *"Does the contract have conflicts, gaps, or areas where it is silent on critical matters?"*
3. *"What are the performance security and retention obligations?"*

For each: screenshot the output. Assess against the professional standard. Bring findings to the strategic partner.

If output quality passes: proceed to Phase 3.  
If output quality has gaps: identify which skill files need deepening and address via Phase 8 (iterative skill deepening) before proceeding.

---

## Phase 3 — Two-Stage Routing (Round 0)

**Objective:** Replace the current model (all domains activate, one long wait) with a fast Round 0 brief that the user can read and act on, followed by user-confirmed deep analysis on selected domains.

**Benefits:**
- Timeout problem solved — Round 0 returns in 5–10 seconds
- Cost reduced — only engaged domains run at depth
- User control — professionals choose what depth they need
- Transparency — routing decisions are visible, not invisible

---

### Task 3.1 — Backend Round 0 classifier

**Agent:** Agent Orchestrator + API Engineer  
**Files:** `src/agents/orchestrator.py`, `src/api/routes/queries.py`, `src/api/schemas.py`  
**Prerequisite:** Phase 2 complete and output quality approved

**What to build:**

A new function `assess_query(request: QueryRequest) -> Round0Assessment` in `orchestrator.py`:

1. Run retrieval (same as full query) — get relevant chunks
2. Make a single Claude API call with a short prompt:
   - What documents were retrieved
   - What domains are relevant to this query and why
   - What is the headline finding from the retrieved context (1-2 sentences)
   - Which domains should run at depth vs are not applicable
3. Return structured `Round0Assessment`:

```python
@dataclass
class DomainRecommendation:
    domain: str          # e.g. "legal_contractual"
    relevance: str       # "PRIMARY" | "RELEVANT" | "NOT_APPLICABLE"
    reason: str          # one sentence

@dataclass  
class Round0Assessment:
    executive_brief: str              # 2-3 sentences
    documents_retrieved: list[str]    # document names found
    domain_recommendations: list[DomainRecommendation]
    default_domains: list[str]        # domains to run by default (PRIMARY ones)
```

New API endpoint: `POST /projects/{id}/query/assess`  
Returns `Round0AssessmentResponse` immediately (no async needed — fast single call).

**Verification:**  
Call the endpoint directly. Confirm response arrives in under 10 seconds with all six domains assessed and a headline brief.

---

### Task 3.2 — Frontend Round 0 display with domain selection

**Agent:** API Engineer (frontend)  
**Files:** `frontend/src/pages/ProjectWorkspacePage.tsx`, new `Round0Card` component  
**Prerequisite:** Task 3.1 complete

**What to build:**

New query flow:

1. User types query and clicks Submit
2. Frontend calls `/query/assess` (fast)
3. Round0Card renders:
   - Executive brief paragraph
   - Documents found (list)
   - Domain grid: each domain shown as a card with relevance badge (PRIMARY / RELEVANT / NOT APPLICABLE) and one-line reason
   - PRIMARY domains pre-selected, RELEVANT domains selectable, NOT APPLICABLE greyed out
   - "Run Analysis" button (runs selected domains) and "Run All" button
4. User clicks "Run Analysis" — full query runs with selected domains only
5. Full results render in the existing QueryResponse component

The Round0Card must communicate clearly that this is a preview, not the full analysis.

**Verification:**  
Submit a query in the live app. Confirm Round 0 card appears within 10 seconds, domains are displayed with correct relevance, user can select/deselect, and clicking "Run Analysis" triggers the full pipeline on selected domains only.

---

### Task 3.3 — Backend full query with domain filter

**Agent:** Agent Orchestrator  
**Files:** `src/agents/orchestrator.py`, `src/api/routes/queries.py`, `src/api/schemas.py`  
**Prerequisite:** Task 3.2 complete

**What to build:**

Extend `SubmitQueryRequest` with an optional `domains: list[str] | None` field. When provided, the orchestrator only activates the specified domains. When absent (or empty), all domains activate as before (backward compatible).

In `process_query`, before Round 1 dispatch:

```python
if request.domains:
    # Only activate requested domains
    round_1_specialists = [s for s in round_1_specialists if s.domain in request.domains]
    round_2_specialists = [s for s in round_2_specialists if s.domain in request.domains]
```

Domains not in the requested list are declared NOT ENGAGED in the synthesis output.

**Verification:**  
From the frontend, select only Legal & Commercial in Round 0, click Run Analysis. Confirm only those two domains appear in the full results. Confirm all other domains are declared NOT ENGAGED.

---

## Phase 4 — Prompt Caching

**Objective:** Reduce input token cost on specialist API calls by caching the static system prompt + skill files.

**Applicable model:** claude-sonnet-4-6 (current model) supports prompt caching.  
**Cache lifetime:** 5 minutes, resets on each use — stays warm for active query sessions.  
**Minimum cacheable tokens:** 1,024. Legal specialist skill files are ~1,900 lines — well above minimum.  
**Cost:** Cache write = full input token price. Cache hit = 10% of input token price (90% saving).

---

### Task 4.1 — Implement prompt caching in base_specialist

**Agent:** Agent Orchestrator  
**Files:** `src/agents/base_specialist.py` — the `messages.create` call only  
**Prerequisite:** Phase 3 complete (system prompt must be stable before caching it)

**What to build:**

The Anthropic SDK requires the `system` parameter to be passed as a list of content blocks (not a plain string) to enable caching:

```python
# Current — plain string, no caching
call_kwargs = {
    "model": CLAUDE_MODEL,
    "max_tokens": 4000,
    "system": system_prompt,
    "messages": messages,
}

# After — content block with cache_control
call_kwargs = {
    "model": CLAUDE_MODEL,
    "max_tokens": 4000,
    "system": [
        {
            "type": "text",
            "text": system_prompt,
            "cache_control": {"type": "ephemeral"}
        }
    ],
    "messages": messages,
}
```

The `system_prompt` string is unchanged — only the wrapping changes. The dynamic content (retrieved chunks, user query, Round 1 findings) remains in the `messages` array and is never cached.

Apply this change to every `messages.create` call in `base_specialist.py`.

**Verification:**  
Run two queries in quick succession (within 5 minutes). Check Railway logs for Anthropic API responses. Cache hit is confirmed when the `usage` object in the API response contains `cache_read_input_tokens > 0`. Log this explicitly:

```python
logger.info(
    "specialist_api_usage",
    domain=self._config.domain,
    input_tokens=response.usage.input_tokens,
    output_tokens=response.usage.output_tokens,
    cache_read_tokens=getattr(response.usage, "cache_read_input_tokens", 0),
    cache_write_tokens=getattr(response.usage, "cache_creation_input_tokens", 0),
)
```

**QG checks:**
- `cache_read_input_tokens` appears in logs on second query
- No change to specialist output — caching is transparent to the model
- Dynamic content (chunks, query text) is NOT inside the cached block

---

## Summary Table

| Phase | Task | Agent | Files | Verification |
|---|---|---|---|---|
| 1 | 1.1 Persist query state to Supabase | DB Architect + API Engineer | Migration 009, queries.py | Restart Railway mid-query, result survives |
| 1 | 1.2 Fix query submission error handling | API Engineer | queries.py | Browser shows 202 within 2s |
| 1 | 1.3 End-to-end query test | Yasser (live app) | — | Screenshot of first real response |
| 2 | 2.1 Rewrite synthesis layer | Agent Orchestrator | orchestrator.py | All 6 domains declared, exec summary present |
| 2 | 2.2 Upgrade system prompt | Agent Orchestrator | base_specialist.py | Citations appear, FLAG/INFORMATIONAL classification |
| 2 | 2.3 Output quality review | Yasser (live app) | — | 3 queries assessed against professional standard |
| 3 | 3.1 Round 0 classifier backend | Agent Orchestrator + API Engineer | orchestrator.py, queries.py, schemas.py | Round 0 response in <10s |
| 3 | 3.2 Round 0 frontend | API Engineer (frontend) | ProjectWorkspacePage.tsx, new Round0Card | Domain selection UI works end-to-end |
| 3 | 3.3 Domain filter in full query | Agent Orchestrator | orchestrator.py, queries.py | Selected domains only in results |
| 4 | 4.1 Prompt caching | Agent Orchestrator | base_specialist.py | cache_read_input_tokens > 0 in logs |

---

## Notes

**Do not build Round 0 and prompt caching simultaneously.** Prompt caching caches the system prompt. The system prompt is changed in Phase 2. Caching a system prompt that is about to change defeats the purpose. Phase 4 must follow Phase 2.

**Phase 3 validation gate:** Before Phase 3 begins, Phase 2 output quality must be assessed and approved by Yasser as domain expert. If output quality does not meet the professional standard after Phase 2, do not proceed — return to skill file deepening (AGENT_PLAN Phase 8) until it does.

**FIDIC ingestion operational note:** Layer 2 ingestion via `scripts/ingest_reference.py` must be run on Railway or a machine with sufficient RAM — not locally. This has been completed for all 6 FIDIC books. Any future reference document ingestion follows the same process.

---

*Document Control: Version 1.0 — April 2026 — Initial plan*
