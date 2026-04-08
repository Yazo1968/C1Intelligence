"""
C1 — Master Orchestrator
Receives a natural language query, routes to domain specialists,
detects contradictions, synthesizes response, and writes audit log.

Phase A: Tier-based dispatch.
- Tier 1 orchestrators (legal, commercial, financial) run in parallel via
  ThreadPoolExecutor using BaseOrchestrator. Each may invoke Tier 2 SMEs
  on-demand via the invoke_sme tool during their own agentic loop.
- Tier 2 SMEs (schedule, technical, compliance) are not dispatched directly.
  They are invoked by Tier 1 orchestrators as needed.
- Cross-specialist contradiction pass (stub — Phase 7 replaces)

This is the only module that knows the full query flow.
"""

from __future__ import annotations

import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from src.clients import get_anthropic_client, get_gemini_client, get_supabase_client
from src.config import CLAUDE_MODEL
from src.logging_config import get_logger
from src.agents.models import (
    AgentError,
    AuditResult,
    ConfidenceLevel,
    ContradictionFlag,
    QueryRequest,
    QueryResponse,
    RetrievalResult,
    SMEConfidenceRecord,
    SourceCitation,
    SpecialistFindings,
)
from src.agents.prompts import DOMAIN_DISPLAY_NAMES
from src.agents.retrieval import retrieve_chunks
from src.agents.domain_router import identify_domains
from src.agents.base_specialist import BaseSpecialist
from src.agents.base_orchestrator import BaseOrchestrator
from src.agents.specialist_config import SPECIALIST_CONFIGS
from src.agents.contradiction import detect_contradictions, write_contradiction_flags
from src.agents.contradiction_cross import cross_specialist_contradiction_pass
from src.agents.audit import snapshot_document_ids, write_audit_log

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Domain name mapping: identify_domains() returns strings from prompts.py
# (e.g., "legal_contractual"), but SPECIALIST_CONFIGS uses short keys
# (e.g., "legal"). This mapping bridges the two without changing either.
# ---------------------------------------------------------------------------
DOMAIN_TO_CONFIG_KEY: dict[str, str] = {
    "legal_contractual": "legal",
    "commercial_financial": "commercial",
    "financial_reporting": "financial",
    "schedule_programme": "schedule",
    "technical_design": "technical",
}

# Keyword signatures for domain alignment check
# Conservative — only flag when signal is unambiguous.
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


def run_evidence_audit(
    findings: list[SpecialistFindings],
    sme_invocations: dict[str, list[str]],
    routing_gaps: list[str],
) -> AuditResult:
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


def process_query(request: QueryRequest) -> QueryResponse:
    """
    Full query pipeline (Phase 2 — multi-round):

    1.  Snapshot document IDs (freeze warehouse state)
    2.  Identify relevant domains (Claude)
    3.  Retrieve chunks via pgvector hybrid search
    4.  If empty → GREY confidence, skip specialists
    5a. Map domain names → config keys, split into Round 1 / Round 2
    5b. Round 1: run Tier 1 orchestrators in parallel (ThreadPoolExecutor)
    5c. (Tier 2 SMEs invoked on-demand by orchestrators via invoke_sme)
    6.  Cross-specialist contradiction pass (stub — Phase 5)
    7.  Detect document contradictions (Claude)
    8.  Write contradiction flags to DB (non-blocking)
    9.  Determine confidence (deterministic)
    10. Build response text (deterministic)
    11. Write audit log (must succeed)
    12. Return QueryResponse
    """
    gemini_client = get_gemini_client()
    anthropic_client = get_anthropic_client()
    supabase_client = get_supabase_client()

    # ------------------------------------------------------------------
    # Step 1: Snapshot document IDs
    # ------------------------------------------------------------------
    document_ids = snapshot_document_ids(supabase_client, request.project_id)

    # ------------------------------------------------------------------
    # Step 2: Identify relevant domains
    # ------------------------------------------------------------------
    domain_result = identify_domains(anthropic_client, request.query_text)
    domains_engaged = domain_result.domains

    # ------------------------------------------------------------------
    # Step 3: Retrieve chunks via pgvector hybrid search
    # ------------------------------------------------------------------
    retrieval = retrieve_chunks(
        supabase_client, gemini_client, request.query_text, request.project_id
    )

    # ------------------------------------------------------------------
    # Step 4: GREY path — no documents found
    # ------------------------------------------------------------------
    if retrieval.is_empty:
        return _grey_response(
            supabase_client, request, domains_engaged, document_ids
        )

    # ------------------------------------------------------------------
    # Step 5a: Map domain names to config keys, split into rounds
    # ------------------------------------------------------------------
    round_1_keys: list[str] = []

    for domain_name in domains_engaged:
        config_key = DOMAIN_TO_CONFIG_KEY.get(domain_name)
        if config_key is None:
            logger.warning(
                "domain_mapping_not_found",
                domain_name=domain_name,
            )
            continue

        config = SPECIALIST_CONFIGS.get(config_key)
        if config is None:
            logger.warning(
                "specialist_config_not_found",
                config_key=config_key,
            )
            continue

        if config.tier == 1:
            round_1_keys.append(config_key)
        # Tier 2 SMEs are not dispatched directly — invoked via invoke_sme

    # If caller specified domains, filter round_1_keys to only those requested
    if request.domains:
        requested_config_keys = {
            DOMAIN_TO_CONFIG_KEY.get(d, d) for d in request.domains
        }
        round_1_keys = [k for k in round_1_keys if k in requested_config_keys]

    logger.info(
        "round_routing_complete",
        domains_engaged=domains_engaged,
        round_1_keys=round_1_keys,
        domain_filter=request.domains,
    )

    # Convert retrieved chunks to dict format for BaseSpecialist.run()
    retrieved_chunks_dicts = [
        {
            "document_id": str(chunk.document_id) if chunk.document_id else "",
            "content": chunk.text,
            "chunk_index": chunk.chunk_index if chunk.chunk_index is not None else idx,
            "document_type": chunk.document_type,
            "document_date": chunk.document_date,
            "document_reference": chunk.document_reference,
            "is_reference": chunk.is_reference,
            "filename": chunk.filename,
            "document_reference_number": chunk.document_reference_number,
            "document_type_name": chunk.document_type_name,
        }
        for idx, chunk in enumerate(retrieval.chunks)
    ]

    # ------------------------------------------------------------------
    # Step 5b: Round 1 — parallel dispatch (Legal, Commercial)
    # ------------------------------------------------------------------
    round_1_findings: list[SpecialistFindings] = []

    if round_1_keys:
        logger.info("round_1_started", specialists=round_1_keys)

        with ThreadPoolExecutor(max_workers=len(round_1_keys)) as executor:
            futures = {
                key: executor.submit(
                    BaseOrchestrator(config=SPECIALIST_CONFIGS[key]).run,
                    query=request.query_text,
                    project_id=str(request.project_id),
                    retrieved_chunks=retrieved_chunks_dicts,
                    round_1_findings=None,
                )
                for key in round_1_keys
            }

            for key, future in futures.items():
                try:
                    finding = future.result()
                    round_1_findings.append(finding)
                except Exception as exc:
                    logger.error(
                        "round_1_orchestrator_failed",
                        domain=key,
                        error=str(exc),
                    )

        logger.info(
            "round_1_complete",
            findings_count=len(round_1_findings),
        )

    # Tier 2 SMEs (schedule, technical, compliance) are invoked on-demand by
    # Tier 1 orchestrators via the invoke_sme tool. No direct Round 2 dispatch.
    all_findings: list[SpecialistFindings] = round_1_findings

    # ------------------------------------------------------------------
    # Step 5b.1 — Deterministic routing coverage audit
    # ------------------------------------------------------------------
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

    # Step 5b.2 — Extract SME invocations deterministically
    sme_invocations = _extract_sme_invocations(round_1_findings)

    # Step 5b.3 — Evidence Auditor (deterministic — zero API calls)
    audit_result = run_evidence_audit(
        findings=round_1_findings,
        sme_invocations=sme_invocations,
        routing_gaps=routing_gaps,
    )

    # ------------------------------------------------------------------
    # Step 6: Cross-specialist contradiction pass (stub — Phase 5)
    # ------------------------------------------------------------------
    cross_specialist_contradictions = cross_specialist_contradiction_pass(
        anthropic_client, all_findings
    )

    # ------------------------------------------------------------------
    # Step 7: Detect document contradictions (Claude)
    # ------------------------------------------------------------------
    contradictions = detect_contradictions(anthropic_client, all_findings)
    contradictions = contradictions + cross_specialist_contradictions

    # ------------------------------------------------------------------
    # Step 8: Write contradiction flags (non-blocking)
    # ------------------------------------------------------------------
    if contradictions:
        doc_ref_to_id = _build_doc_reference_map(retrieval)
        write_contradiction_flags(
            supabase_client, request.project_id, contradictions, doc_ref_to_id
        )

    # ------------------------------------------------------------------
    # Step 9: Determine confidence (deterministic)
    # ------------------------------------------------------------------
    confidence = determine_confidence(all_findings, contradictions, retrieval)

    # ------------------------------------------------------------------
    # Step 10: Build response text (includes executive summary via Claude)
    # ------------------------------------------------------------------
    response_text = build_response_text(
        all_findings,
        contradictions,
        confidence,
        request.query_text,
        document_count=len(document_ids),
        routing_gaps=routing_gaps,
        audit_result=audit_result,
    )

    # ------------------------------------------------------------------
    # Step 11: Write audit log (must succeed)
    # ------------------------------------------------------------------
    all_citations = _collect_all_citations(all_findings)
    all_evidence_records = _collect_evidence_records(all_findings)

    round_number_to_log: int | None = max((f.round_number for f in all_findings), default=None)
    audit_log_id = write_audit_log(
        supabase_client=supabase_client,
        project_id=request.project_id,
        user_id=request.user_id,
        query_text=request.query_text,
        response_text=response_text,
        confidence=confidence,
        domains_engaged=domains_engaged,
        document_ids=document_ids,
        citations=all_citations,
        round_number=round_number_to_log,
        evidence_records=all_evidence_records or None,
    )

    # ------------------------------------------------------------------
    # Step 12: Return response
    # ------------------------------------------------------------------
    logger.info(
        "query_processed",
        project_id=str(request.project_id),
        confidence=confidence.value,
        domains_engaged=domains_engaged,
        orchestrator_count=len(round_1_findings),
        contradiction_count=len(contradictions),
        cross_specialist_contradictions=len(cross_specialist_contradictions),
        audit_log_id=str(audit_log_id),
    )

    return QueryResponse(
        query_text=request.query_text,
        response_text=response_text,
        confidence=confidence,
        domains_engaged=domains_engaged,
        specialist_findings=all_findings,
        contradictions=contradictions,
        document_ids_at_query_time=document_ids,
        audit_log_id=audit_log_id,
        routing_gaps=routing_gaps,
        audit_result=audit_result,
    )


def assess_query(request: QueryRequest) -> "Round0Assessment":
    """
    Fast Round 0 assessment: retrieval + single Claude API call.
    Returns domain relevance classification and headline brief.
    Synchronous — designed to return in under 10 seconds.
    """
    from src.agents.models import DomainRecommendation, Round0Assessment

    gemini_client = get_gemini_client()
    anthropic_client = get_anthropic_client()
    supabase_client = get_supabase_client()

    # Step 1: Retrieve chunks
    retrieval = retrieve_chunks(
        supabase_client, gemini_client, request.query_text, request.project_id
    )

    # Step 2: Collect retrieved document names for display
    seen: set[str] = set()
    documents_retrieved: list[str] = []
    for chunk in retrieval.chunks:
        label = chunk.document_type_name or chunk.filename or str(chunk.document_id)
        if label and label not in seen:
            seen.add(label)
            documents_retrieved.append(label)

    # Step 3: Build context from retrieved chunks (truncated for speed)
    chunk_context = "\n\n".join(
        f"[{chunk.document_type_name or chunk.filename or 'Document'}]\n{chunk.text[:300]}"
        for chunk in retrieval.chunks[:8]
    )

    if not chunk_context:
        chunk_context = "No documents retrieved for this query."

    # Step 4: Single Claude API call — domain assessment + brief
    prompt = f"""You are assessing a construction project query for document relevance.

Query: {request.query_text}

Retrieved document excerpts:
{chunk_context}

The three active analysis domains are:
1. legal_contractual — contracts, notices, entitlement, time bars, securities
2. commercial_financial — payment, variations, BOQ, retention, final account
3. financial_reporting — EVM, budget vs actual, cost performance, cash flow

For each domain, classify as:
- PRIMARY: the query is directly about this domain
- RELEVANT: this domain provides supporting context
- NOT_APPLICABLE: this domain is not relevant to this query

Respond in this exact JSON format with no other text:
{{{{
  "executive_brief": "Two sentences maximum. What the documents show about this query.",
  "domains": [
    {{{{"domain": "legal_contractual", "relevance": "PRIMARY|RELEVANT|NOT_APPLICABLE", "reason": "One sentence."}}}},
    {{{{"domain": "commercial_financial", "relevance": "PRIMARY|RELEVANT|NOT_APPLICABLE", "reason": "One sentence."}}}},
    {{{{"domain": "financial_reporting", "relevance": "PRIMARY|RELEVANT|NOT_APPLICABLE", "reason": "One sentence."}}}}
  ]
}}}}"""

    try:
        response = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        import json as _json
        data = _json.loads(raw)
    except Exception as exc:
        logger.warning("assess_query_claude_failed", error=str(exc))
        data = {
            "executive_brief": "Assessment could not be completed. Proceeding with full analysis.",
            "domains": [
                {"domain": "legal_contractual", "relevance": "RELEVANT", "reason": "Unable to assess — run full analysis."},
                {"domain": "commercial_financial", "relevance": "RELEVANT", "reason": "Unable to assess — run full analysis."},
                {"domain": "financial_reporting", "relevance": "RELEVANT", "reason": "Unable to assess — run full analysis."},
            ]
        }

    recommendations = [
        DomainRecommendation(
            domain=d["domain"],
            relevance=d.get("relevance", "RELEVANT"),
            reason=d.get("reason", ""),
        )
        for d in data.get("domains", [])
    ]

    default_domains = [
        r.domain for r in recommendations if r.relevance == "PRIMARY"
    ]
    if not default_domains:
        default_domains = [r.domain for r in recommendations
                           if r.relevance != "NOT_APPLICABLE"]

    logger.info(
        "assess_query_complete",
        project_id=str(request.project_id),
        default_domains=default_domains,
    )

    return Round0Assessment(
        executive_brief=data.get("executive_brief", ""),
        documents_retrieved=documents_retrieved,
        domain_recommendations=recommendations,
        default_domains=default_domains,
    )


def determine_confidence(
    findings: list[SpecialistFindings],
    contradictions: list[ContradictionFlag],
    retrieval: RetrievalResult,
) -> ConfidenceLevel:
    """
    Deterministic confidence classification from SpecialistFindings.

    Derives confidence from the per-specialist confidence values
    already computed by each BaseSpecialist.

    GREY  — retrieval returned no relevant documents
    RED   — any specialist flagged RED, or contradictions detected
    AMBER — any specialist flagged AMBER
    GREEN — all specialists report GREEN
    """
    if retrieval.is_empty:
        return ConfidenceLevel.GREY

    if contradictions:
        return ConfidenceLevel.RED

    if not findings:
        return ConfidenceLevel.AMBER

    # Derive from per-specialist confidence values
    confidence_values = [f.confidence for f in findings]

    if any(c == "RED" for c in confidence_values):
        return ConfidenceLevel.RED

    if any(c == "AMBER" for c in confidence_values):
        return ConfidenceLevel.AMBER

    if any(c == "GREY" for c in confidence_values):
        return ConfidenceLevel.AMBER  # GREY from a specialist means partial coverage

    return ConfidenceLevel.GREEN


NOT_ENGAGED_REASONS: dict[str, str] = {
    "legal_contractual": "No contract documents found in the warehouse for this query.",
    "commercial_financial": "No BOQ, IPC, payment, or variation documents found in the warehouse.",
    "financial_reporting": "No budget documents, cost reports, cash flow statements, or EVM data found in the warehouse.",
    "schedule_programme": "No programme documents, delay records, or progress reports found in the warehouse.",
    "technical_design": "No specifications, drawings, RFIs, or NCRs found in the warehouse.",
}

# Only Tier 1 orchestrator domains appear as top-level output sections.
# Tier 2 SME findings are synthesised into Tier 1 orchestrator output.
ALL_DOMAINS_ORDERED: list[str] = [
    "legal_contractual",
    "commercial_financial",
    "financial_reporting",
]


def _generate_executive_summary(
    findings: list[SpecialistFindings],
    confidence: ConfidenceLevel,
) -> str:
    """
    Generate a 3-sentence executive summary via a single Claude API call.
    Falls back to a static message on any failure.
    """
    fallback = "Analysis complete. See domain assessments below for full findings."

    if not findings:
        return fallback

    # Build context from all domain findings
    findings_context_parts: list[str] = []
    for f in findings:
        display_name = _config_key_to_display_name(f.domain)
        findings_context_parts.append(f"### {display_name}\n{f.findings}")

    findings_context = "\n\n".join(findings_context_parts)

    try:
        anthropic_client = get_anthropic_client()
        response = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=600,
            system="You are a senior construction contract analyst. Write a 3-sentence executive summary for a director-level reader. Be direct. State what was assessed, the confidence level, and the single most important finding.",
            messages=[
                {
                    "role": "user",
                    "content": f"Overall confidence: {confidence.value}\n\n{findings_context}",
                }
            ],
        )
        summary = response.content[0].text.strip()
        if summary:
            return summary
        return fallback
    except Exception as exc:
        logger.warning("executive_summary_generation_failed", error=str(exc))
        return fallback


def _config_key_to_display_name(config_key: str) -> str:
    """Map a specialist config key (e.g., 'legal') to display name (e.g., 'Legal & Contractual')."""
    for domain_name, key in DOMAIN_TO_CONFIG_KEY.items():
        if key == config_key:
            return DOMAIN_DISPLAY_NAMES.get(domain_name, config_key)
    return config_key


def _build_evidence_summary(finding: "SpecialistFindings") -> str:
    """
    Build an Evidence Summary section for a domain assessment.

    Returns a non-empty string only when there are grounding gaps —
    i.e. when Layer 2b, the amendment document, or Layer 2a was not
    retrieved, or when a confidence cap was applied.

    Returns empty string when all required evidence was present,
    so the section is omitted from clean responses.
    """
    from src.agents.models import LayerRetrievalStatus

    er = finding.evidence_record
    if er is None:
        return ""

    lines: list[str] = []

    # Layer 2b gap
    if er.layer2b_status == LayerRetrievalStatus.NOT_RETRIEVED:
        lines.append("- **Governing contract standard:** The applicable standard form of "
                     "contract was not found in the document warehouse. Findings on "
                     "standard form provisions are based on the project documents only.")
    elif er.layer2b_status == LayerRetrievalStatus.PARTIAL:
        lines.append("- **Governing contract standard:** Partially retrieved "
                     f"— source: {er.layer2b_source or 'unspecified'}.")

    # Amendment document gap
    if er.layer1_amendment_document_status == LayerRetrievalStatus.NOT_RETRIEVED:
        lines.append("- **Project-specific contract terms:** The Particular Conditions or "
                     "equivalent amendment document was not separately retrieved. "
                     "Standard form provisions apply unless varied by the main contract "
                     "document.")

    # Layer 2a gap (only relevant when required by schema)
    if er.layer2a_status == LayerRetrievalStatus.NOT_RETRIEVED and er.layer2a_source is None:
        # Only surface Layer 2a gap if it was expected (source field was populated by schema)
        # For most domains Layer 2a is not required — suppress to avoid noise
        pass

    # Provisions CANNOT CONFIRM
    if er.provisions_cannot_confirm:
        items = "; ".join(er.provisions_cannot_confirm)
        lines.append(f"- **Could not confirm from retrieved documents:** {items}")

    if not lines:
        return ""

    summary = "*The following limitations apply to this assessment:*\n"
    summary += "\n".join(lines)
    return summary


def _strip_evidence_declaration(findings_text: str) -> str:
    """
    Remove the Evidence Declaration block from agent findings text
    before rendering to the client-facing response.

    The block has already been parsed into evidence_record by
    _parse_evidence_declaration(). It must not appear in client output.

    Handles heading variants: ## or ### followed by
    "Evidence Declaration" or "EVIDENCE DECLARATION" (case-insensitive).
    Strips from the heading line to the next heading of equal or higher
    level, or to the first numbered section (e.g. "1. "), or to "---".
    """
    import re
    # Match ## or ### Evidence Declaration block
    # Strip to next heading (##/###), numbered section, or horizontal rule
    cleaned = re.sub(
        r'\n?#{2,3}\s+EVIDENCE DECLARATION\s*\n.*?(?=\n#{1,3}\s|\n\d+\.\s|\n---|\Z)',
        '',
        findings_text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # Also strip any standalone Evidence Declaration line at the start
    cleaned = re.sub(
        r'^#{2,3}\s+EVIDENCE DECLARATION\s*\n.*?(?=\n#{1,3}\s|\n\d+\.\s|\n---|\Z)',
        '',
        cleaned,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return cleaned.strip()


def _clean_output_terminology(text: str) -> str:
    """Replace internal architecture terms in any client-facing output."""
    replacements = [
        ("the document warehouse", "the document set"),
        ("the warehouse", "the document set"),
        ("not in the warehouse", "not in the document set"),
        ("not found in the warehouse", "not found in the document set"),
        ("ingested into the warehouse", "uploaded to the document set"),
        ("ingested", "uploaded"),
        ("warehouse", "document set"),
        ("Layer 2b", "the applicable standard form"),
        ("Layer 2a", "internal policy documents"),
        ("Layer 1", "project documents"),
        ("layer 2b", "the applicable standard form"),
        ("layer 2a", "internal policy documents"),
        ("layer 1", "project documents"),
    ]
    result = text
    for old, new in replacements:
        result = result.replace(old, new)
    return result


def build_response_text(
    findings: list[SpecialistFindings],
    contradictions: list[ContradictionFlag],
    confidence: ConfidenceLevel,
    query_text: str,
    document_count: int = 0,
    audit_log_id: uuid.UUID | None = None,
    routing_gaps: list[str] | None = None,
    audit_result: "AuditResult | None" = None,
) -> str:
    """
    Professional report assembly from SpecialistFindings.

    Produces an executive report with:
    - Executive summary (single Claude API call)
    - All six domains declared (engaged or NOT ENGAGED)
    - Contradictions section
    - Audit reference footer
    """
    sections: list[str] = []

    # --- Executive Summary ---
    executive_summary = _generate_executive_summary(findings, confidence)
    sections.append(_clean_output_terminology(executive_summary))
    sections.append("")
    sections.append(f"**Overall Confidence:** {confidence.value}")
    sections.append(f"**Documents assessed:** {document_count}")
    sections.append("")
    sections.append("---")
    sections.append("")

    if routing_gaps:
        gap_names = [DOMAIN_DISPLAY_NAMES.get(d, d) for d in routing_gaps]
        sections.append(
            f"> ⚠ **Coverage Notice:** This analysis did not cover the following "
            f"domains, which may have relevant content in the project documents: "
            f"{', '.join(gap_names)}. Consider re-running the query with these "
            f"domains selected for a more complete assessment."
        )
        sections.append("")

    # --- Domain Assessments ---
    sections.append("## Domain Assessments")
    sections.append("")

    # Build lookup: config_key -> SpecialistFindings
    findings_by_key: dict[str, SpecialistFindings] = {
        f.domain: f for f in findings
    }

    for domain_name in ALL_DOMAINS_ORDERED:
        display_name = DOMAIN_DISPLAY_NAMES.get(domain_name, domain_name)
        config_key = DOMAIN_TO_CONFIG_KEY.get(domain_name, domain_name)
        finding = findings_by_key.get(config_key)

        if finding:
            badge = finding.confidence
            sections.append(f"### {display_name} — {badge}")
            sections.append("")
            sections.append(_clean_output_terminology(
                _strip_evidence_declaration(finding.findings)
            ))
            sections.append("")
            evidence_summary = _build_evidence_summary(finding)
            if evidence_summary:
                sections.append(evidence_summary)
                sections.append("")
        else:
            reason = NOT_ENGAGED_REASONS.get(domain_name, "Not applicable to this query.")
            sections.append(f"### {display_name} — NOT ENGAGED")
            sections.append("")
            sections.append(f"*Not applicable to this query. {reason}*")
            sections.append("")

        sections.append("---")
        sections.append("")

    # --- Contradictions ---
    sections.append("## Contradictions Detected")
    sections.append("")
    if contradictions:
        for c in contradictions:
            sections.append(f"- **{c.field_name}**:")
            sections.append(
                f"  - Document A ({c.document_a_reference}): {c.value_a}"
            )
            sections.append(
                f"  - Document B ({c.document_b_reference}): {c.value_b}"
            )
            sections.append(f"  - {c.description}")
            sections.append("")
    else:
        sections.append("No contradictions detected across the documents assessed.")
        sections.append("")

    sections.append("---")
    sections.append("")

    # --- Audit footer ---
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    audit_ref = str(audit_log_id) if audit_log_id else "pending"
    sections.append(f"*Audit Reference: {audit_ref} · Query submitted: {timestamp}*")

    return "\n".join(sections)


def _grey_response(
    supabase_client,
    request: QueryRequest,
    domains_engaged: list[str],
    document_ids: list[uuid.UUID],
) -> QueryResponse:
    """
    Handle the GREY path: retrieval returned no relevant documents.
    Still writes an audit log entry and produces a professional-format report.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Build all six domains as NOT ENGAGED
    domain_sections: list[str] = []
    for domain_name in ALL_DOMAINS_ORDERED:
        display_name = DOMAIN_DISPLAY_NAMES.get(domain_name, domain_name)
        reason = NOT_ENGAGED_REASONS.get(domain_name, "Not applicable to this query.")
        domain_sections.append(f"### {display_name} — NOT ENGAGED")
        domain_sections.append("")
        domain_sections.append(f"*Not applicable to this query. {reason}*")
        domain_sections.append("")
        domain_sections.append("---")
        domain_sections.append("")

    response_text = "\n".join([
        "## Executive Summary",
        "",
        "The document warehouse contains no documents relevant to this query. "
        "This may mean the required documents have not yet been uploaded, "
        "or the query does not match any content in the current project.",
        "",
        "**Overall Confidence:** GREY",
        f"**Documents assessed:** {len(document_ids)}",
        "",
        "---",
        "",
        "## Domain Assessments",
        "",
        *domain_sections,
        "## Contradictions Detected",
        "",
        "No contradictions detected across the documents assessed.",
        "",
        "---",
        "",
        f"*Query submitted: {timestamp}*",
    ])

    audit_log_id = write_audit_log(
        supabase_client=supabase_client,
        project_id=request.project_id,
        user_id=request.user_id,
        query_text=request.query_text,
        response_text=response_text,
        confidence=ConfidenceLevel.GREY,
        domains_engaged=domains_engaged,
        document_ids=document_ids,
        citations=[],
        round_number=None,
    )

    logger.info(
        "query_grey_response",
        project_id=str(request.project_id),
        audit_log_id=str(audit_log_id),
    )

    return QueryResponse(
        query_text=request.query_text,
        response_text=response_text,
        confidence=ConfidenceLevel.GREY,
        domains_engaged=domains_engaged,
        document_ids_at_query_time=document_ids,
        audit_log_id=audit_log_id,
    )


def _build_doc_reference_map(retrieval: RetrievalResult) -> dict[str, uuid.UUID]:
    """
    Build a mapping from document reference strings to UUIDs,
    used to resolve contradiction flag document IDs.
    """
    ref_map: dict[str, uuid.UUID] = {}
    for chunk in retrieval.chunks:
        if chunk.document_reference and chunk.document_id:
            ref_map[chunk.document_reference] = chunk.document_id
    return ref_map


def _collect_all_citations(findings: list[SpecialistFindings]) -> list[SourceCitation]:
    """
    Collect citations from SpecialistFindings for the audit log.

    Constructs minimal SourceCitation objects with document_id populated
    from each string in sources_used. The rich citation structure
    (document_type, date, excerpt) is not available from the new model.
    """
    citations: list[SourceCitation] = []
    seen_ids: set[str] = set()

    for finding in findings:
        for doc_id_str in finding.sources_used:
            if doc_id_str not in seen_ids:
                seen_ids.add(doc_id_str)
                try:
                    citations.append(
                        SourceCitation(document_id=uuid.UUID(doc_id_str))
                    )
                except ValueError:
                    logger.warning(
                        "invalid_document_id_in_sources",
                        document_id=doc_id_str,
                        domain=finding.domain,
                    )

    return citations


def _collect_evidence_records(findings: list[SpecialistFindings]) -> list[dict]:
    """
    Collect serialised EvidenceRecord dicts from all specialist findings.
    Only includes findings that have an evidence_record populated.
    """
    records: list[dict] = []
    for f in findings:
        if f.evidence_record is not None:
            records.append({
                "domain": f.domain,
                "layer2b_status": f.evidence_record.layer2b_status.value,
                "layer2b_source": f.evidence_record.layer2b_source,
                "layer2a_status": f.evidence_record.layer2a_status.value,
                "layer2a_source": f.evidence_record.layer2a_source,
                "layer1_primary_document": f.evidence_record.layer1_primary_document,
                "layer1_amendment_document_status": (
                    f.evidence_record.layer1_amendment_document_status.value
                ),
                "provisions_cannot_confirm": f.evidence_record.provisions_cannot_confirm,
            })
    return records
