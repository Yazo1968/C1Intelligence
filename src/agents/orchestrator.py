"""
C1 — Master Orchestrator
Receives a natural language query, routes to domain specialists,
detects contradictions, synthesizes response, and writes audit log.

Phase A: Tier-based dispatch.
- Tier 1 orchestrators (legal, commercial, financial) run in parallel via
  ThreadPoolExecutor using BaseOrchestrator. Each may invoke Tier 2 SMEs
  on-demand via the invoke_sme tool during their own agentic loop.
- Tier 2 SMEs (claims, schedule, technical) are not dispatched directly.
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
    ConfidenceLevel,
    ContradictionFlag,
    QueryRequest,
    QueryResponse,
    RetrievalResult,
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
    "claims_disputes": "claims",
}

_RISK_FRAMING_DIRECTIVE: str = """

--- RISK ASSESSMENT MODE ---

This query has been submitted in Risk Assessment Mode. In addition to
your standard domain assessment, you must frame your findings as risk
exposures. For each significant finding:

- State the risk description clearly
- Classify likelihood: HIGH / MEDIUM / LOW
- Classify impact: HIGH / MEDIUM / LOW
- Derive overall risk rating: HIGH (if either likelihood or impact is HIGH),
  MEDIUM (if both are MEDIUM, or one is MEDIUM and one is LOW),
  LOW (if both are LOW)
- State the recommended action in one sentence

Your FLAGS section must use the risk register format:
RISK [ID] | [Domain] | [Description] | Likelihood: [H/M/L] |
Impact: [H/M/L] | Rating: [HIGH/MEDIUM/LOW] | Action: [sentence]

--- END RISK ASSESSMENT MODE ---
"""


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
        logger.info("round_1_started", specialists=round_1_keys,
                    risk_mode=request.risk_mode)

        # Append risk framing directive to query text when risk_mode is active
        effective_query = request.query_text
        if request.risk_mode:
            effective_query = request.query_text + _RISK_FRAMING_DIRECTIVE

        with ThreadPoolExecutor(max_workers=len(round_1_keys)) as executor:
            futures = {
                key: executor.submit(
                    BaseOrchestrator(config=SPECIALIST_CONFIGS[key]).run,
                    query=effective_query,
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

    # Tier 2 SMEs (claims, schedule, technical) are invoked on-demand by
    # Tier 1 orchestrators via the invoke_sme tool. No direct Round 2 dispatch.
    all_findings: list[SpecialistFindings] = round_1_findings

    # ------------------------------------------------------------------
    # Step 6: Cross-specialist contradiction pass (stub — Phase 5)
    # ------------------------------------------------------------------
    cross_specialist_contradictions = cross_specialist_contradiction_pass(all_findings)

    # ------------------------------------------------------------------
    # Step 7: Detect document contradictions (Claude)
    # ------------------------------------------------------------------
    contradictions = detect_contradictions(anthropic_client, all_findings)

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
    )

    # ------------------------------------------------------------------
    # Step 11: Write audit log (must succeed)
    # ------------------------------------------------------------------
    all_citations = _collect_all_citations(all_findings)

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
    "claims_disputes": "No notice documents, EOT claims, or dispute correspondence found in the warehouse.",
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
            max_tokens=200,
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


def build_response_text(
    findings: list[SpecialistFindings],
    contradictions: list[ContradictionFlag],
    confidence: ConfidenceLevel,
    query_text: str,
    document_count: int = 0,
    audit_log_id: uuid.UUID | None = None,
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
    sections.append("## Executive Summary")
    sections.append("")
    sections.append(executive_summary)
    sections.append("")
    sections.append(f"**Overall Confidence:** {confidence.value}")
    sections.append(f"**Documents assessed:** {document_count}")
    sections.append("")
    sections.append("---")
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
            sections.append(finding.findings)
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
