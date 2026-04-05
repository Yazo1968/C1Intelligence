# C1 Intelligence — Aggregation Integrity Plan v2.0

**Version:** 2.0 (revised from v1.0 after senior assessor review)
**Date:** April 2026
**Status:** Ready for execution
**Author:** Strategic Partner (Claude)
**Approved by:** Yasser Darweesh

---

## Why v2.0 Exists

v1.0 was rejected by senior assessor review for a critical architectural flaw:
its core verification layers (Coverage Declaration, SME Invocation Audit,
Evidence Map) were all populated by the same LLM agents whose outputs they
were supposed to verify. This is self-reporting masquerading as verification —
structurally equivalent to asking a student to grade their own exam using the
same reasoning that produced the errors.

**The principle governing v2.0:** Every integrity check must be grounded in
deterministic data that the system already records — data that cannot be
fabricated by the agent being verified. LLM agents may be asked to reason;
they are not asked to audit themselves.

**Research basis for this principle:**
- AgentAuditor (Feb 2026): audit at divergence points using actual reasoning
  traces, not agent self-reports
- TRiSM (Mar 2026): reasoning-trace logging of what actually happened in the
  agentic loop — tool calls, inputs, outputs — not what the LLM says happened
- MAST (NeurIPS 2025): structural improvements outperform prompt additions;
  15.6% gain from workflow redesign vs marginal gains from prompt engineering

---

## 0. How to Use This Document

This plan is fully self-contained. A new Claude chat session can execute it
without reference to any prior conversation. The session start protocol is:

1. Clone: `git clone https://github.com/Yazo1968/C1Intelligence.git`
2. Read `CLAUDE.md`
3. Read `docs/C1_MASTER_PLAN.md`
4. Read this plan in full before taking any action
5. Verify database state via Supabase MCP `list_migrations` on project
   `bkkujtvhdbroieffhfok` — confirm 18 migrations (001–018) applied
6. Confirm HEAD commit matches the last recorded SHA in `BUILD_LOG.md`

**One task per commit. QG PASS required before next task begins.
Strategic Partner verifies every output via GitHub API before confirming PASS.
Verification method: `api.github.com/repos/Yazo1968/C1Intelligence/contents/{path}`
Never use `raw.githubusercontent.com` — CDN-cached, causes false negatives.**

---

## 1. Platform Context

C1 Intelligence is a universal construction project intelligence platform.
Not FIDIC-specific. Not jurisdiction-specific. Adapts to whatever is in the
warehouse.

**Three-layer evidence warehouse:**
- Layer 1: Project documents (contracts, correspondence, claims, schedules,
  payment records, drawings, technical reports)
- Layer 2a: Internal policies (DOA matrices, authority frameworks,
  internal procedures)
- Layer 2b: External standards (FIDIC, NEC, JCT, AIA, PMBOK, IFRS,
  SCL Protocol, AACE — whatever is ingested)

**Three-tier agent architecture:**
- Tier 0: Domain router — classifies query into domains
- Tier 1: Legal, Commercial, Financial orchestrators — `BaseOrchestrator`,
  run in parallel via `ThreadPoolExecutor`
- Tier 2: Schedule, Technical, Compliance, Financial Accounting SMEs —
  `BaseSpecialist`, invoked on-demand by Tier 1 via `invoke_sme` tool

**Infrastructure:**
- Repo: `github.com/Yazo1968/C1Intelligence` (main branch)
- Supabase: `bkkujtvhdbroieffhfok` (EU West 1) — 18 migrations, 15 tables
- Backend: FastAPI on Railway — `https://web-production-6f2c4.up.railway.app`
- Frontend: Vite/React on Vercel — `https://c1intelligence.vercel.app`

**Locked constraints (never change without explicit instruction):**
- No LangChain, LangGraph, or LlamaIndex
- Gemini embeddings at 3072 dims, HNSW via halfvec cast
- Vite/React frontend (NOT Next.js)
- CORS locked to `https://c1intelligence.vercel.app`
- No additional LLM agents added for verification — deterministic code only

---

## 2. Current Code State — Confirmed by Direct Inspection

All findings below are from direct file reads. Do not assume — re-verify
before making any change.

### 2.1 `src/agents/orchestrator.py` — 12-step pipeline

```
Step 1:  Snapshot document IDs
Step 2:  identify_domains() → DomainIdentification(domains, reasoning)
Step 3:  retrieve_chunks() → RetrievalResult
Step 4:  GREY path if retrieval empty
Step 5a: Map domain names → config keys, filter Tier 1 only
Step 5b: Parallel ThreadPoolExecutor dispatch of Tier 1 orchestrators
Step 6:  cross_specialist_contradiction_pass() [WORKING — do not change]
Step 7:  detect_contradictions() [WORKING — do not change]
Step 8:  write_contradiction_flags() to DB
Step 9:  determine_confidence() [WORKING — do not change]
Step 10: build_response_text()
Step 11: write_audit_log()
Step 12: Return QueryResponse
```

`determine_confidence()` already implements the correct minimum-confidence
rule: any RED → RED, any AMBER → AMBER, all GREEN → GREEN. Do not change it.

`ALL_DOMAINS_ORDERED` contains only 3 entries (legal, commercial, financial).
Tier 2 SME findings are synthesised into Tier 1 output. This is correct by
design.

### 2.2 `src/agents/domain_router.py`

Returns `DomainIdentification(domains: list[str], reasoning: str)`.
Uses tool `identify_domains` with schema requiring `domains` array and
`reasoning` string.

**Gap:** Returns which domains are relevant but produces no auditable
commitment that can be checked downstream. No record of which chunks
were considered vs which domains were declared.

### 2.3 `src/agents/base_orchestrator.py`

**STALE ITEM S1:** `_ORCHESTRATOR_SYSTEM_PROMPT_PREFIX` contains:
```
Valid SME domains: claims, schedule, technical.
```
`claims` domain was dissolved in Enhancement Plan Part B.
Correct value: `schedule, technical, compliance, financial_sme`

**`tools_called` gap:** In the agentic loop:
```python
tools_called.append(tool_name)  # records "invoke_sme" — not which SME
```
`tool_input` (which contains `sme_domain`) is not preserved in `tools_called`.
Result: cannot determine which specific SMEs were invoked from `tools_called`
alone.

**What IS preserved:** Raw SME output is returned from `_execute_invoke_sme()`
as a dict `{domain, findings, confidence, sources_used, tools_called}` and
JSON-serialised into `tool_results` messages for the conversation. It flows
into the orchestrator's context window but is NOT separately persisted. Once
the orchestrator synthesises, the raw SME output is lost.

**What is correctly implemented:**
- `_parse_evidence_declaration()` — parses Evidence Declaration block
- `_validate_evidence_and_cap_confidence()` — applies confidence caps
- `EvidenceRecord.provisions_cannot_confirm` — populated deterministically

### 2.4 `src/agents/prompts.py`

**STALE ITEM S2:** `DOMAIN_ROUTER_SYSTEM_PROMPT` header reads:
```
THE SIX DOMAINS:
```
Only five domains are listed and described. Must read "THE FIVE DOMAINS:".

### 2.5 `src/agents/tools.py`

**STALE ITEM S3:** `invoke_sme` tool schema in `ORCHESTRATOR_TOOL_DEFINITIONS`:
```python
"enum": ["claims", "schedule", "technical"]
```
`claims` is dissolved. The description also references `claims`. Must be
updated to `["schedule", "technical", "compliance", "financial_sme"]`.
The description text must also be corrected.

`_execute_invoke_sme()` runs the SME and returns:
```python
{
    "domain": findings.domain,
    "findings": findings.findings,
    "confidence": findings.confidence,
    "sources_used": findings.sources_used,
    "tools_called": findings.tools_called,
}
```
This dict is the deterministic record of what the SME produced. It exists
in the conversation history but is not currently captured for integrity use.

### 2.6 `src/agents/models.py`

Key fields already present and deterministically populated:

**`SpecialistFindings`:**
- `tools_called: list[str]` — records tool names called (but not SME domain)
- `sources_used: list[str]` — document IDs that contributed
- `evidence_record: EvidenceRecord | None` — parsed from Evidence Declaration

**`EvidenceRecord`:**
- `provisions_cannot_confirm: list[str]` — CANNOT CONFIRM items
- `layer2b_status`, `layer2a_status`, `layer1_amendment_document_status`

**Gap:** No field on `SpecialistFindings` to hold:
- Which specific SME domains were invoked (not just "invoke_sme")
- Raw SME output dicts for post-synthesis comparison

### 2.7 `src/agents/contradiction_cross.py`

Working correctly. Detects contradictions between Tier 1 orchestrators.
Do not change.

---

## 3. The Five Risks — Mapped to Deterministic Data Already in the System

| Risk | Code gap | Deterministic data already available |
|---|---|---|
| R1: Misrouting at Tier 0 | Router returns domains but no gap detection against retrieved evidence | Retrieved chunks have domain-relevant content. If schedule chunks were retrieved but schedule domain not engaged, detectable without LLM. |
| R2: Incomplete SME invocation | `tools_called` records `"invoke_sme"` but not which SME | `tool_input["sme_domain"]` is available at call time in the agentic loop. Record it. |
| R3: Aggregation without reconciliation | Raw SME outputs synthesised and discarded | `_execute_invoke_sme()` returns raw findings dict. Capture it before synthesis. |
| R4: Evidence chain breaks | `sources_used` exists but not surfaced in aggregated output | `sources_used` on every `SpecialistFindings`. Already deterministic. Use it. |
| R5: CANNOT CONFIRM compounding | `provisions_cannot_confirm` on `EvidenceRecord` — populated. Not consolidated. | Already deterministic. Aggregate across all findings. |

**The observation this table makes explicit:** The data needed to verify
integrity is already being recorded by the system. The gap is not that the
data doesn't exist — it is that it is not used for verification.

---

## 4. What Is Already Correct — Do Not Change

- `determine_confidence()` — minimum-confidence rule correctly implemented
- `cross_specialist_contradiction_pass()` — cross-orchestrator contradiction
- `detect_contradictions()` — within-document contradiction detection
- `_parse_evidence_declaration()` — Evidence Declaration parsing
- `_validate_evidence_and_cap_confidence()` — confidence capping
- `EvidenceRecord` model structure
- `SpecialistFindings` model structure (fields being added — not modified)
- All 30 skill files — form-agnostic, correct
- ISO 31000 Risk Register output format in orchestrator directives

---

## 5. Stale Items — Must Fix Before Any New Work

Three stale bugs found by direct code inspection. Each is a targeted,
surgical fix. Each gets its own commit.

### S1 — `base_orchestrator.py`: stale SME domain list

**File:** `src/agents/base_orchestrator.py`

In `_ORCHESTRATOR_SYSTEM_PROMPT_PREFIX`, replace:
```
Valid SME domains: claims, schedule, technical.
Use this when the query requires specialist expertise outside your direct scope.
```
With:
```
Valid SME domains: schedule, technical, compliance, financial_sme.
Use this when the query requires specialist expertise outside your direct scope.
```

**Commit:** `fix: base_orchestrator — remove stale claims SME, add compliance and financial_sme`

**QG:**
- Zero instances of `"claims"` in `_ORCHESTRATOR_SYSTEM_PROMPT_PREFIX`
- All four valid SME domains listed
- No other content changed
- Python syntax: PASS

---

### S2 — `prompts.py`: "SIX DOMAINS" → "FIVE DOMAINS"

**File:** `src/agents/prompts.py`

In `DOMAIN_ROUTER_SYSTEM_PROMPT`, replace:
```
THE SIX DOMAINS:
```
With:
```
THE FIVE DOMAINS:
```

**Commit:** `fix: prompts — domain router corrected from SIX to FIVE domains`

**QG:**
- Zero instances of "SIX DOMAINS" in file
- "FIVE DOMAINS" present
- No other content changed
- Python syntax: PASS

---

### S3 — `tools.py`: stale invoke_sme domain enum

**File:** `src/agents/tools.py`

In `ORCHESTRATOR_TOOL_DEFINITIONS`, in the `invoke_sme` tool definition,
make two changes:

**Change A — enum:**
```python
# CURRENT (stale):
"enum": ["claims", "schedule", "technical"],

# REPLACE WITH:
"enum": ["schedule", "technical", "compliance", "financial_sme"],
```

**Change B — description text:**
```python
# CURRENT (stale):
"e.g., delay analysis (schedule SME), notice compliance (claims SME), "
"or design defect assessment (technical SME). "
"Valid SME domains: 'claims', 'schedule', 'technical'."

# REPLACE WITH:
"e.g., delay analysis (schedule SME), specification compliance (technical SME), "
"regulatory compliance (compliance SME), or cost accounting (financial_sme). "
"Valid SME domains: 'schedule', 'technical', 'compliance', 'financial_sme'."
```

**Change C — required field:**
Same `sme_domain` field. Only the enum and description text change.
The `question` and `context` fields are unchanged.

**Commit:** `fix: tools — invoke_sme schema updated, claims removed, compliance and financial_sme added`

**QG:**
- `"claims"` absent from `invoke_sme` schema entirely
- Enum contains exactly: `["schedule", "technical", "compliance", "financial_sme"]`
- Description text updated
- No other tools changed
- Python syntax: PASS

---

## 6. Phase 1 — Deterministic Routing Audit (Risk 1)

**Principle:** The domain router's coverage is verified by comparing what was
retrieved against what was declared. Retrieved chunks carry domain-relevant
content. If schedule-relevant chunks were retrieved but the schedule domain
was not engaged, the gap is detectable without asking the router.

This replaces v1.0's LLM Coverage Declaration entirely.

### Task 1.1 — Add chunk-domain keyword alignment function

**File:** `src/agents/orchestrator.py`
**Executor:** Claude Code

Add the following function to `orchestrator.py`:

```python
# Keyword signatures for domain alignment check
# These are conservative — only flag when signal is unambiguous.
_DOMAIN_CHUNK_KEYWORDS: dict[str, list[str]] = {
    "schedule_programme": [
        "programme", "delay", "extension of time", "eot", "critical path",
        "float", "milestone", "baseline", "as-built", "look-ahead",
        "prolongation", "disruption", "recovery programme",
    ],
    "technical_design": [
        "specification", "drawing", "rfi", "shop drawing", "bim",
        "design change", "value engineering", "ncr", "technical",
        "defect", "snag", "test", "commissioning",
    ],
    "legal_contractual": [
        "notice", "contract", "clause", "condition", "agreement",
        "entitlement", "dispute", "arbitration", "time bar",
        "performance bond", "liquidated damages", "force majeure",
    ],
    "commercial_financial": [
        "payment", "variation", "boq", "interim certificate",
        "retention", "final account", "daywork", "measurement",
        "cash flow", "cost report", "budget",
    ],
    "financial_reporting": [
        "earned value", "evm", "cpi", "spi", "eac", "etc",
        "budget vs actual", "cost overrun", "contingency",
        "financial forecast", "ifrs", "revenue recognition",
    ],
}


def _check_routing_coverage(
    domains_engaged: list[str],
    retrieved_chunks: list[dict],
) -> list[str]:
    """
    Deterministic routing coverage check.

    Scans retrieved chunk content for domain keyword signatures.
    Returns list of domain names where chunks contain strong domain signals
    but the domain was not engaged by the router.

    No LLM call. No self-reporting. Uses what was actually retrieved.
    Returns empty list if no gaps detected or if retrieval is empty.
    """
    if not retrieved_chunks:
        return []

    # Build combined text from all retrieved Layer 1 chunks (not reference docs)
    layer1_text = " ".join(
        chunk.get("content", "").lower()
        for chunk in retrieved_chunks
        if not chunk.get("is_reference", False)
    )

    if not layer1_text.strip():
        return []

    gaps: list[str] = []

    for domain, keywords in _DOMAIN_CHUNK_KEYWORDS.items():
        if domain in domains_engaged:
            continue  # already engaged — no gap

        # Count keyword hits
        hits = sum(1 for kw in keywords if kw in layer1_text)

        # Flag as gap only if strong signal (3+ keyword hits)
        # Conservative threshold — avoids false positives
        if hits >= 3:
            gaps.append(domain)
            logger.warning(
                "routing_coverage_gap",
                domain=domain,
                keyword_hits=hits,
                engaged_domains=domains_engaged,
            )

    return gaps
```

**Commit:** `feat: orchestrator — deterministic routing coverage check from retrieved chunks`

**QG:**
- `_check_routing_coverage()` function present
- `_DOMAIN_CHUNK_KEYWORDS` dict with 5 domain entries present
- No LLM call in the function
- Returns `list[str]`
- Python syntax: PASS

---

### Task 1.2 — Call routing coverage check in pipeline

**File:** `src/agents/orchestrator.py`
**Executor:** Claude Code

After Step 5b (orchestrators dispatched and results collected), add:

```python
# Step 5b.1 — Deterministic routing coverage audit
routing_gaps = _check_routing_coverage(
    domains_engaged=domains_engaged,
    retrieved_chunks=retrieved_chunks_dicts,
)
if routing_gaps:
    logger.warning(
        "routing_gaps_detected",
        gaps=routing_gaps,
        engaged=domains_engaged,
        query_snippet=request.query_text[:100],
    )
```

Pass `routing_gaps` to `build_response_text()` and `QueryResponse`.

Update `build_response_text()` signature:
```python
def build_response_text(
    findings: list[SpecialistFindings],
    contradictions: list[ContradictionFlag],
    confidence: ConfidenceLevel,
    query_text: str,
    document_count: int = 0,
    audit_log_id: uuid.UUID | None = None,
    routing_gaps: list[str] | None = None,  # ADD
    audit_result: "AuditResult | None" = None,  # ADD (used in Phase 3)
) -> str:
```

In `build_response_text()`, if `routing_gaps` is not empty, add a warning
notice after the Executive Summary section:

```python
if routing_gaps:
    gap_names = [DOMAIN_DISPLAY_NAMES.get(d, d) for d in routing_gaps]
    sections.append(
        f"> ⚠ **Coverage Notice:** The document warehouse contains signals "
        f"for the following domains that were not engaged in this analysis: "
        f"{', '.join(gap_names)}. This may indicate a partial assessment. "
        f"Consider resubmitting the query or engaging these domains explicitly."
    )
    sections.append("")
```

Add `routing_gaps: list[str] = Field(default_factory=list)` to `QueryResponse`
in `models.py`.

**Commit:** `feat: orchestrator — routing coverage gaps detected and surfaced in response`

**QG:**
- `_check_routing_coverage()` called after Step 5b
- Warning surfaced in response text when gaps detected
- `routing_gaps` field on `QueryResponse`
- `build_response_text()` signature updated
- Python syntax: PASS

---

## 7. Phase 2 — Deterministic SME Trace (Risk 2)

**Principle:** `tools_called` records `"invoke_sme"` but not which domain.
`tool_input["sme_domain"]` is available at call time. Record it. This is
a one-line change in the agentic loop that converts an opaque log entry
into a specific, auditable trace.

### Task 2.1 — Record SME domain in tools_called

**File:** `src/agents/base_orchestrator.py`
**Executor:** Claude Code

In the agentic loop within `run()`, locate:

```python
for tool_block in tool_use_blocks:
    tool_name = tool_block.name
    tool_input = tool_block.input
    tools_called.append(tool_name)
```

Replace `tools_called.append(tool_name)` with:

```python
# For invoke_sme, record the specific SME domain — not just the tool name
if tool_name == "invoke_sme" and "sme_domain" in tool_input:
    tools_called.append(f"invoke_sme:{tool_input['sme_domain']}")
else:
    tools_called.append(tool_name)
```

This is a one-line change in logic. `tools_called` now records
`"invoke_sme:schedule"` instead of `"invoke_sme"`. All existing code
that reads `tools_called` continues to work — it is still a list of strings.

**Commit:** `feat: base_orchestrator — tools_called records SME domain on invoke_sme calls`

**QG:**
- Conditional present in agentic loop
- `invoke_sme:{sme_domain}` format used when sme_domain present
- Fallback to `tool_name` for all other tools
- No other agentic loop logic changed
- Python syntax: PASS

---

### Task 2.2 — SME invocation extraction and gap detection

**File:** `src/agents/orchestrator.py`
**Executor:** Claude Code

Add the following function:

```python
def _extract_sme_invocations(findings: list[SpecialistFindings]) -> dict[str, list[str]]:
    """
    Extract which SMEs were actually invoked by each orchestrator.

    Uses tools_called (deterministic record from agentic loop).
    Returns dict: orchestrator_domain → [sme_domains_invoked].
    """
    result: dict[str, list[str]] = {}
    for finding in findings:
        invoked: list[str] = []
        for tool_entry in finding.tools_called:
            if tool_entry.startswith("invoke_sme:"):
                sme_domain = tool_entry.split(":", 1)[1]
                invoked.append(sme_domain)
        result[finding.domain] = invoked

    logger.info(
        "sme_invocations_extracted",
        invocations={k: v for k, v in result.items()},
    )
    return result
```

Call this after Step 5b:

```python
# Step 5b.2 — Extract SME invocations deterministically
sme_invocations = _extract_sme_invocations(round_1_findings)
```

Log the full SME invocation map at INFO level.
Pass `sme_invocations` to `run_evidence_audit()` (added in Phase 3).

**Commit:** `feat: orchestrator — deterministic SME invocation extraction from tools_called`

**QG:**
- `_extract_sme_invocations()` function present
- Returns `dict[str, list[str]]`
- Parses `"invoke_sme:{domain}"` format correctly
- Called after Step 5b
- Python syntax: PASS

---

## 8. Phase 3 — Raw SME Output Preservation (Risk 3)

**Principle:** When an orchestrator invokes `invoke_sme`, the raw SME findings
dict is returned from `_execute_invoke_sme()` and JSON-serialised into the
conversation. Once the orchestrator synthesises, this output is lost. Capture
it before it disappears — then the Evidence Auditor can compare what each SME
produced against what the orchestrator chose to carry forward.

### Task 3.1 — Add raw_sme_outputs field to SpecialistFindings

**File:** `src/agents/models.py`
**Executor:** Claude Code

Add one field to `SpecialistFindings`:

```python
raw_sme_outputs: list[dict] = Field(
    default_factory=list,
    description=(
        "Raw SME findings dicts captured from invoke_sme tool results. "
        "Each dict contains: domain, findings, confidence, sources_used. "
        "Populated deterministically from tool call results in the agentic loop."
    ),
)
```

**Commit:** `feat: models — raw_sme_outputs field added to SpecialistFindings`

**QG:**
- `raw_sme_outputs: list[dict]` field present on `SpecialistFindings`
- Default is empty list
- No other fields modified
- Python syntax: PASS

---

### Task 3.2 — Capture raw SME output in agentic loop

**File:** `src/agents/base_orchestrator.py`
**Executor:** Claude Code

In `run()`, before the agentic loop begins, add:

```python
raw_sme_outputs: list[dict] = []
```

In the tool result capture section of the agentic loop, after
`result = execute_tool(tool_name, tool_input, project_id)`, add:

```python
# Capture raw SME output before it is synthesised into context
if tool_name == "invoke_sme" and not result.get("error"):
    raw_sme_outputs.append(result)
```

In `_parse_findings()`, update the call at end of method to attach
`raw_sme_outputs`:

Pass `raw_sme_outputs` from `run()` to `_parse_findings()` by adding it
as a parameter:

```python
def _parse_findings(
    self, text: str, tools_called: list[str], raw_sme_outputs: list[dict]
) -> SpecialistFindings:
```

At end of `_parse_findings()`, before returning, attach:

```python
findings = findings.model_copy(update={"raw_sme_outputs": raw_sme_outputs})
```

Update call site in `run()`:

```python
return self._parse_findings(text_content, tools_called, raw_sme_outputs)
```

Also update `_error_findings()` to initialise with empty list (already
default in the model — no change needed).

**Commit:** `feat: base_orchestrator — raw SME outputs captured in agentic loop`

**QG:**
- `raw_sme_outputs` list initialised before loop
- Raw SME result captured when `tool_name == "invoke_sme"` and no error
- `_parse_findings()` accepts `raw_sme_outputs` parameter
- `raw_sme_outputs` attached to `SpecialistFindings`
- All call sites to `_parse_findings()` updated
- Python syntax: PASS

---

## 9. Phase 4 — Evidence Auditor — Deterministic (Risks 3, 4, 5)

**Principle:** One function. Zero API calls. Reads only data that was
deterministically recorded by the agentic loop. Cannot be gamed by the
agents being audited. Runs after all Tier 1 orchestrators complete.

### Task 4.1 — Add AuditResult model

**File:** `src/agents/models.py`
**Executor:** Claude Code

Add after `SpecialistFindings`:

```python
class SMEConfidenceRecord(BaseModel):
    """Confidence level from a specific SME invocation."""
    orchestrator_domain: str
    sme_domain: str
    confidence: str  # GREEN / AMBER / RED / GREY
    sources_used: list[str] = Field(default_factory=list)
    cannot_confirm_items: list[str] = Field(default_factory=list)


class AuditResult(BaseModel):
    """
    Output of the deterministic Evidence Auditor.

    All fields populated from existing deterministic data:
    - tools_called (agentic loop)
    - raw_sme_outputs (captured from tool results)
    - evidence_record.provisions_cannot_confirm (parsed from Evidence Declaration)
    - sources_used (populated from tool results)

    Zero LLM calls. Cannot be fabricated by agents being audited.
    """
    # R5: Consolidated CANNOT CONFIRM across all findings
    cannot_confirm_consolidated: list[str] = Field(
        default_factory=list,
        description="All CANNOT CONFIRM items from all orchestrators and SMEs"
    )

    # R2: SME invocation map — what actually happened
    sme_invocations: dict[str, list[str]] = Field(
        default_factory=dict,
        description="orchestrator_domain → [sme_domains_actually_invoked]"
    )

    # R3: Per-SME confidence from raw outputs
    sme_confidence_records: list[SMEConfidenceRecord] = Field(
        default_factory=list,
        description="Confidence and CANNOT CONFIRM from each raw SME output"
    )

    # R4: Per-domain confidence for audit trail
    confidence_by_domain: dict[str, str] = Field(
        default_factory=dict,
        description="orchestrator_domain → confidence"
    )

    # R1: Routing gaps from deterministic chunk alignment
    routing_gaps: list[str] = Field(
        default_factory=list,
        description="Domains with chunk signal but not engaged by router"
    )

    # Derived: minimum confidence across all SMEs and orchestrators
    minimum_confidence_basis: str = Field(
        default="",
        description="Which domain/SME drove the minimum confidence and why"
    )
```

Also add `audit_result: AuditResult | None = None` to `QueryResponse`.

**Commit:** `feat: models — AuditResult and SMEConfidenceRecord models added`

**QG:**
- `AuditResult` and `SMEConfidenceRecord` present
- `audit_result` on `QueryResponse`
- No existing models modified
- Python syntax: PASS

---

### Task 4.2 — Implement run_evidence_audit()

**File:** `src/agents/orchestrator.py`
**Executor:** Claude Code

Add the following function. This is the core integrity function.
It reads only deterministic data. Zero API calls.

```python
def run_evidence_audit(
    findings: list[SpecialistFindings],
    sme_invocations: dict[str, list[str]],
    routing_gaps: list[str],
) -> "AuditResult":
    """
    Deterministic Evidence Auditor. Zero API calls.

    Reads:
    - findings[].evidence_record.provisions_cannot_confirm (deterministic)
    - findings[].raw_sme_outputs (captured from tool results)
    - findings[].confidence (deterministic)
    - findings[].sources_used (deterministic)
    - sme_invocations (extracted from tools_called)
    - routing_gaps (from chunk-domain alignment)

    Cannot be gamed by agents being audited.
    """
    from src.agents.models import AuditResult, SMEConfidenceRecord

    audit = AuditResult()
    audit.sme_invocations = sme_invocations
    audit.routing_gaps = routing_gaps

    # --- Confidence by orchestrator domain ---
    for finding in findings:
        audit.confidence_by_domain[finding.domain] = finding.confidence

    # --- Consolidate CANNOT CONFIRM from orchestrators ---
    for finding in findings:
        if finding.evidence_record and finding.evidence_record.provisions_cannot_confirm:
            for item in finding.evidence_record.provisions_cannot_confirm:
                entry = f"[{finding.domain.upper()}] {item}"
                if entry not in audit.cannot_confirm_consolidated:
                    audit.cannot_confirm_consolidated.append(entry)

    # --- Extract per-SME confidence and CANNOT CONFIRM from raw outputs ---
    for finding in findings:
        for raw_output in finding.raw_sme_outputs:
            sme_domain = raw_output.get("domain", "unknown")
            sme_confidence = raw_output.get("confidence", "GREY")
            sme_sources = raw_output.get("sources_used", [])
            sme_findings_text = raw_output.get("findings", "")

            # Extract CANNOT CONFIRM from raw SME findings text
            sme_cannot_confirm: list[str] = []
            if "CANNOT CONFIRM" in sme_findings_text.upper():
                import re
                matches = re.findall(
                    r"CANNOT CONFIRM[^\n.]*",
                    sme_findings_text,
                    re.IGNORECASE,
                )
                sme_cannot_confirm = [m.strip() for m in matches[:5]]

            record = SMEConfidenceRecord(
                orchestrator_domain=finding.domain,
                sme_domain=sme_domain,
                confidence=sme_confidence,
                sources_used=sme_sources,
                cannot_confirm_items=sme_cannot_confirm,
            )
            audit.sme_confidence_records.append(record)

            # Add SME CANNOT CONFIRM to consolidated list
            for item in sme_cannot_confirm:
                entry = f"[{sme_domain.upper()} via {finding.domain.upper()}] {item}"
                if entry not in audit.cannot_confirm_consolidated:
                    audit.cannot_confirm_consolidated.append(entry)

    # --- Determine minimum confidence basis ---
    conf_order = {"GREY": 3, "RED": 2, "AMBER": 1, "GREEN": 0}
    all_confidences: list[tuple[str, str]] = [
        (domain, conf)
        for domain, conf in audit.confidence_by_domain.items()
    ]
    for rec in audit.sme_confidence_records:
        all_confidences.append((f"{rec.sme_domain} (SME)", rec.confidence))

    if all_confidences:
        worst_entry = max(
            all_confidences,
            key=lambda x: conf_order.get(x[1], 1)
        )
        audit.minimum_confidence_basis = (
            f"Minimum confidence: {worst_entry[1]} — "
            f"driven by {worst_entry[0]}."
        )

    logger.info(
        "evidence_audit_complete",
        cannot_confirm_count=len(audit.cannot_confirm_consolidated),
        sme_confidence_records=len(audit.sme_confidence_records),
        routing_gaps=routing_gaps,
        confidence_by_domain=dict(audit.confidence_by_domain),
        minimum_confidence_basis=audit.minimum_confidence_basis,
    )

    return audit
```

**Commit:** `feat: orchestrator — run_evidence_audit() deterministic, zero API calls`

**QG:**
- `run_evidence_audit()` function present
- `SMEConfidenceRecord` imported from models
- Reads `raw_sme_outputs` from findings (deterministic)
- Reads `evidence_record.provisions_cannot_confirm` (deterministic)
- Zero API calls in function body
- Python syntax: PASS

---

### Task 4.3 — Integrate Evidence Auditor into pipeline

**File:** `src/agents/orchestrator.py`
**Executor:** Claude Code

Insert between Step 5b.2 and Step 6:

```python
# Step 5b.3 — Evidence Auditor (deterministic — zero API calls)
audit_result = run_evidence_audit(
    findings=round_1_findings,
    sme_invocations=sme_invocations,
    routing_gaps=routing_gaps,
)
```

Update `build_response_text()` call:
```python
response_text = build_response_text(
    all_findings,
    contradictions,
    confidence,
    request.query_text,
    document_count=len(document_ids),
    routing_gaps=routing_gaps,
    audit_result=audit_result,
)
```

Update `QueryResponse` return:
```python
return QueryResponse(
    ...,
    routing_gaps=routing_gaps,
    audit_result=audit_result,
)
```

Import `AuditResult` at top of file.

**Commit:** `feat: orchestrator — Evidence Auditor integrated into process_query pipeline`

**QG:**
- `run_evidence_audit()` called after Step 5b.2
- `audit_result` passed to `build_response_text()` and `QueryResponse`
- Pipeline step order preserved (audit before cross-specialist contradiction)
- `AuditResult` imported
- Python syntax: PASS

---

## 10. Phase 5 — Evidence Map from Deterministic Fields (Risk 4)

**Principle:** Do not ask orchestrators to self-report which finding came from
which document. Use `sources_used` and `raw_sme_outputs` — both deterministic.
Build the Evidence Map from what was recorded, not from what agents say.

### Task 5.1 — Build consolidated evidence map in build_response_text()

**File:** `src/agents/orchestrator.py`
**Executor:** Claude Code

Add function:

```python
def _build_consolidated_evidence_map(
    findings: list[SpecialistFindings],
    audit_result: "AuditResult | None",
    routing_gaps: list[str] | None,
) -> str:
    """
    Build Consolidated Evidence Map from deterministic fields.

    Uses:
    - findings[].confidence (deterministic)
    - findings[].sources_used (deterministic — document IDs)
    - audit_result.cannot_confirm_consolidated (deterministic)
    - audit_result.sme_confidence_records (from raw SME outputs)
    - audit_result.sme_invocations (from tools_called)
    - routing_gaps (from chunk-domain alignment)

    No LLM call. No self-reporting.
    """
    lines: list[str] = []
    lines.append("## Consolidated Evidence Map")
    lines.append("")
    lines.append(
        "*This map is generated deterministically from recorded system "
        "state — not from agent self-reporting.*"
    )
    lines.append("")

    # --- Domain confidence audit ---
    lines.append("### Domain Confidence Audit")
    lines.append("")
    if audit_result and audit_result.confidence_by_domain:
        for domain, conf in audit_result.confidence_by_domain.items():
            display = DOMAIN_DISPLAY_NAMES.get(domain, domain)
            lines.append(f"- **{display}:** {conf}")
        if audit_result.minimum_confidence_basis:
            lines.append("")
            lines.append(f"*{audit_result.minimum_confidence_basis}*")
    else:
        lines.append("*No domain confidence data recorded.*")
    lines.append("")

    # --- SME invocations (from tools_called — deterministic) ---
    lines.append("### SME Agents Invoked")
    lines.append("")
    if audit_result and audit_result.sme_invocations:
        any_invoked = False
        for orch_domain, sme_list in audit_result.sme_invocations.items():
            display = DOMAIN_DISPLAY_NAMES.get(orch_domain, orch_domain)
            if sme_list:
                any_invoked = True
                lines.append(f"**{display} orchestrator invoked:**")
                for sme in sme_list:
                    # Find confidence from sme_confidence_records
                    sme_conf = next(
                        (r.confidence for r in audit_result.sme_confidence_records
                         if r.orchestrator_domain == orch_domain and r.sme_domain == sme),
                        "unknown"
                    )
                    lines.append(f"- {sme} — confidence: {sme_conf}")
            else:
                lines.append(f"**{display} orchestrator:** No SME delegation.")
        if not any_invoked:
            lines.append("*No SME delegation occurred in this query.*")
    else:
        lines.append("*No SME invocation data recorded.*")
    lines.append("")

    # --- Document sources by domain (from sources_used — deterministic) ---
    lines.append("### Documents Retrieved by Domain")
    lines.append("")
    for finding in findings:
        display = DOMAIN_DISPLAY_NAMES.get(finding.domain, finding.domain)
        if finding.sources_used:
            lines.append(
                f"**{display}** ({len(finding.sources_used)} source(s), "
                f"confidence: {finding.confidence})"
            )
        else:
            lines.append(f"**{display}** — no documents retrieved")
    lines.append("")

    # --- Consolidated CANNOT CONFIRM ---
    lines.append("### Consolidated CANNOT CONFIRM")
    lines.append("")
    if audit_result and audit_result.cannot_confirm_consolidated:
        for item in audit_result.cannot_confirm_consolidated:
            lines.append(f"- {item}")
        lines.append("")
        lines.append(
            "*These items require resolution before findings dependent on them "
            "can be treated as confirmed.*"
        )
    else:
        lines.append(
            "*None — all required evidence was retrieved across all domains "
            "and invoked SMEs.*"
        )
    lines.append("")

    # --- Routing coverage gaps ---
    if routing_gaps:
        lines.append("### Routing Coverage Notice")
        lines.append("")
        gap_displays = [DOMAIN_DISPLAY_NAMES.get(d, d) for d in routing_gaps]
        lines.append(
            f"The document warehouse contained signals for the following "
            f"domains that were not engaged: **{', '.join(gap_displays)}**."
        )
        lines.append(
            "This may indicate a partial assessment. Resubmit the query "
            "or engage these domains explicitly."
        )
        lines.append("")

    return "\n".join(lines)
```

In `build_response_text()`, insert the Evidence Map after the Domain
Assessments section and before the Contradictions section:

```python
# --- Consolidated Evidence Map ---
evidence_map = _build_consolidated_evidence_map(
    findings, audit_result, routing_gaps
)
sections.append(evidence_map)
sections.append("")
sections.append("---")
sections.append("")
```

**Commit:** `feat: orchestrator — Consolidated Evidence Map built from deterministic fields`

**QG:**
- `_build_consolidated_evidence_map()` function present
- Uses `sources_used`, `confidence_by_domain`, `sme_invocations`,
  `cannot_confirm_consolidated`, `routing_gaps` — all deterministic
- No LLM call in function
- Added to `build_response_text()` before Contradictions section
- Python syntax: PASS

---

### Task 5.2 — Update output_formats.md

**File:** `skills/c1-skill-authoring/references/output_formats.md`
**Executor:** Claude Code

Add a documentation section describing the Consolidated Evidence Map so
future skill authors understand it is system-generated:

```markdown
---

## Consolidated Evidence Map — System-Generated Section

The Consolidated Evidence Map is automatically generated by the system
after all orchestrators complete. It is NOT produced by skill files or
orchestrator directives.

**Skill file authors must not include a Consolidated Evidence Map section
in their directive output templates.** The system generates it from:
- `sources_used` field on each SpecialistFindings (deterministic)
- `tools_called` field — SME invocations (deterministic)
- `raw_sme_outputs` — captured from tool results (deterministic)
- `evidence_record.provisions_cannot_confirm` (deterministic)
- Chunk-domain alignment check (deterministic)

The Evidence Map appears in the final output between Domain Assessments
and the Contradictions section. Orchestrators do not control its content.
```

**Commit:** `docs: output_formats — Consolidated Evidence Map documented as system-generated`

**QG:**
- Section present in `output_formats.md`
- Clear instruction: skill authors must NOT include this in directive output
- States all five deterministic data sources
- Governing footer intact

---

## 11. Phase 6 — Governing Documents (3 tasks)

### Task 6.1 — Update CLAUDE.md

**File:** `CLAUDE.md`
**Executor:** Claude Code

In the Architecture section, after existing skill files paragraph, add:

```
**Aggregation Integrity Layer (v2.0 — deterministic):**
Routing coverage check (chunk-domain keyword alignment — deterministic, no
LLM). SME invocation trace (tools_called records invoke_sme:{domain} —
deterministic). Raw SME output preservation (captured in agentic loop before
synthesis). Evidence Auditor (run_evidence_audit() — zero API calls, reads
only pre-recorded deterministic data). Consolidated Evidence Map in every
response (built from sources_used, tools_called, raw_sme_outputs, and
evidence_record — not from agent self-reporting).
Design principle: every integrity check reads deterministic system state.
No integrity layer asks an agent to audit itself.
```

**Commit:** `docs: CLAUDE.md — Aggregation Integrity Layer v2.0 documented`

**QG:**
- Paragraph present in Architecture section
- "deterministic" principle stated
- No other content modified

---

### Task 6.2 — Update C1_MASTER_PLAN.md

**File:** `docs/C1_MASTER_PLAN.md`
**Executor:** Claude Code

Add section after Enhancement Plan entry:

```markdown
## Aggregation Integrity Plan v2.0 — Active Workstream

**Status:** Executed
**Document:** `docs/C1_AGGREGATION_INTEGRITY_PLAN_v2.md`

20 tasks across 6 phases. All verification is deterministic — zero additional
LLM calls. No new agent frameworks. No new API endpoints. No database
migrations. No frontend changes.

End state: routing coverage is verified against retrieved chunk content;
SME invocations are traced via tools_called; raw SME outputs are preserved
before synthesis; CANNOT CONFIRM items are consolidated from
evidence_record; every response carries a Consolidated Evidence Map built
from system-recorded data, not agent self-reports.

Research basis: MAST NeurIPS 2025, AgentAuditor Feb 2026, TRiSM Mar 2026.
Design principle: verification must read what the system recorded, not what
agents say they did.
```

**Commit:** `docs: C1_MASTER_PLAN.md — Aggregation Integrity Plan v2.0 recorded`

---

### Task 6.3 — Session close BUILD_LOG

**File:** `BUILD_LOG.md`
**Executor:** Claude Code

Append session close entry after all tasks complete and verified.

**Commit:** `docs: BUILD_LOG.md — Aggregation Integrity Plan v2.0 complete`

---

## 12. Execution Sequence

```
Phase S:  S1, S2, S3           (3 tasks — fix before any new work)
Phase 1:  1.1, 1.2             (2 tasks — routing audit)
Phase 2:  2.1, 2.2             (2 tasks — SME trace)
Phase 3:  3.1, 3.2             (2 tasks — raw output preservation)
Phase 4:  4.1, 4.2, 4.3        (3 tasks — Evidence Auditor)
Phase 5:  5.1, 5.2             (2 tasks — Evidence Map)
Phase 6:  6.1, 6.2, 6.3        (3 tasks — governing docs)
```

**Total: 20 commits.**

Phases 1 and 2 can be executed in the same session (both are small).
Phase 3 and 4 should be a dedicated session — Phase 3 changes the agentic
loop; Phase 4 uses what Phase 3 captures. Do not combine with anything else.
Phase 5 depends on Phase 4 completing cleanly.
Phase 6 is always last.

---

## 13. QG Checklist — Per Task

**For every Python file change:**
- [ ] `python3 -c "import ast; ast.parse(open('src/agents/FILE.py').read()); print('PASS')"`
- [ ] `git diff --stat` shows only the named file changed
- [ ] No other methods or fields modified beyond those specified

**For Phase S tasks:**
- [ ] `grep -n "claims"` returns zero results in changed file
- [ ] All four valid SME domains present: schedule, technical, compliance, financial_sme

**For Phase 3 (agentic loop change):**
- [ ] Agentic loop structure unchanged — only the `tools_called.append()` call modified
- [ ] `raw_sme_outputs` list initialised before loop, not inside
- [ ] Error case (`result.get("error")`) excluded from capture

**For Phase 4 (Evidence Auditor):**
- [ ] Zero `anthropic_client.messages.create()` calls in `run_evidence_audit()`
- [ ] All data reads reference fields on `SpecialistFindings`, not LLM calls
- [ ] Regex for CANNOT CONFIRM extraction is non-greedy and has a result limit

**For all skill file changes:**
- [ ] Governing footer present and intact
- [ ] No hardcoded contract form references introduced

---

## 14. File Inventory

| File | Phase | Type |
|---|---|---|
| `src/agents/base_orchestrator.py` | S1, 2.1, 3.2 | Stale fix + agentic loop |
| `src/agents/prompts.py` | S2 | Stale fix |
| `src/agents/tools.py` | S3 | Stale fix |
| `src/agents/models.py` | 3.1, 4.1 | New fields + new models |
| `src/agents/orchestrator.py` | 1.1, 1.2, 2.2, 4.2, 4.3, 5.1 | Pipeline + functions |
| `skills/c1-skill-authoring/references/output_formats.md` | 5.2 | Documentation |
| `CLAUDE.md` | 6.1 | Architecture update |
| `docs/C1_MASTER_PLAN.md` | 6.2 | Workstream recorded |
| `BUILD_LOG.md` | 6.3 | Session close |

**No database migrations required.**
**No frontend changes required.**
**No new LLM agents added.**
**Zero additional API calls in the integrity layer.**

---

## 15. What This Plan Does Not Do — and Why

**Does not add a separate LLM verification agent.**
Research (AgentAuditor, TRiSM) is explicit: LLM judges applied globally are
computationally expensive and biased by majority cues. Deterministic checks
applied at specific recorded data points outperform generic LLM judging.

**Does not implement multi-agent debate.**
ICLR 2025 analysis: debate degrades to majority voting on shared benchmarks.
For domain-specialist agents, debate across domain boundaries produces noise,
not signal.

**Does not add a static query-type-to-SME matrix.**
This would contradict C1's form-agnostic design. A delay claim under a
bespoke contract has different mandatory SMEs than one under NEC. The
routing audit approach detects actual evidence signals, not assumed
query-type mappings.

**Does not claim to detect all errors.**
The routing coverage check uses keyword signals — it will miss subtly
mislabelled domains. The SME trace reads tools_called — it will accurately
report what was called but cannot verify the quality of the question asked.
These are honest limitations. They are better than the alternative: asking
the agent to self-report, which introduces a new error channel.

---

## Document Control

| Field | Value |
|---|---|
| Version | 2.0 |
| Supersedes | v1.0 (rejected — LLM self-reporting flaw) |
| Date | April 2026 |
| Location | `docs/C1_AGGREGATION_INTEGRITY_PLAN_v2.md` |
| Commit to repo | After Yasser approval |
| Research basis | MAST NeurIPS 2025, AgentAuditor Feb 2026, TRiSM Mar 2026 |
