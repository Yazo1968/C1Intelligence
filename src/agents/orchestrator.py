"""
C1 — Master Orchestrator
Receives a natural language query, routes to domain specialists,
detects contradictions, synthesizes response, and writes audit log.

Phase 2: Multi-round dispatch with context handoff.
- Round 1: Legal & Commercial (parallel via ThreadPoolExecutor)
- Round 2: Claims, Schedule, Technical, Governance (sequential, receives Round 1 findings)
- Cross-specialist contradiction pass (stub — Phase 5 replaces)

This is the only module that knows the full query flow.
"""

from __future__ import annotations

import uuid
from concurrent.futures import ThreadPoolExecutor

from src.clients import get_anthropic_client, get_gemini_client, get_supabase_client
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
    "schedule_programme": "schedule",
    "technical_design": "technical",
    "claims_disputes": "claims",
    "governance_compliance": "governance",
}


def process_query(request: QueryRequest) -> QueryResponse:
    """
    Full query pipeline (Phase 2 — multi-round):

    1.  Snapshot document IDs (freeze warehouse state)
    2.  Identify relevant domains (Claude)
    3.  Retrieve chunks via pgvector hybrid search
    4.  If empty → GREY confidence, skip specialists
    5a. Map domain names → config keys, split into Round 1 / Round 2
    5b. Round 1: run relevant specialists in parallel (ThreadPoolExecutor)
    5c. Round 2: run relevant specialists sequentially with Round 1 handoff
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
    round_2_keys: list[str] = []

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

        if config.round_assignment == 1:
            round_1_keys.append(config_key)
        else:
            round_2_keys.append(config_key)

    logger.info(
        "round_routing_complete",
        domains_engaged=domains_engaged,
        round_1_keys=round_1_keys,
        round_2_keys=round_2_keys,
    )

    # Convert retrieved chunks to dict format for BaseSpecialist.run()
    retrieved_chunks_dicts = [
        {
            "document_id": str(chunk.document_id) if chunk.document_id else "",
            "content": chunk.text,
            "chunk_index": idx,
            "document_type": chunk.document_type,
            "document_date": chunk.document_date,
            "document_reference": chunk.document_reference,
            "is_reference": chunk.is_reference,
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
                    BaseSpecialist(config=SPECIALIST_CONFIGS[key]).run,
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
                        "round_1_specialist_failed",
                        domain=key,
                        error=str(exc),
                    )

        logger.info(
            "round_1_complete",
            findings_count=len(round_1_findings),
        )

    # ------------------------------------------------------------------
    # Step 5c: Round 2 — sequential dispatch with Round 1 handoff
    # ------------------------------------------------------------------
    round_2_findings: list[SpecialistFindings] = []

    if round_2_keys:
        # Serialize Round 1 findings for handoff
        round_1_handoff: dict | None = None
        if round_1_findings:
            round_1_handoff = {
                f.domain: {
                    "findings": f.findings,
                    "confidence": f.confidence,
                    "sources_used": f.sources_used,
                }
                for f in round_1_findings
            }

        logger.info(
            "round_2_started",
            specialists=round_2_keys,
            round_1_findings_available=round_1_handoff is not None,
        )

        for key in round_2_keys:
            try:
                finding = BaseSpecialist(config=SPECIALIST_CONFIGS[key]).run(
                    query=request.query_text,
                    project_id=str(request.project_id),
                    retrieved_chunks=retrieved_chunks_dicts,
                    round_1_findings=round_1_handoff,
                )
                round_2_findings.append(finding)
            except Exception as exc:
                logger.error(
                    "round_2_specialist_failed",
                    domain=key,
                    error=str(exc),
                )

        logger.info(
            "round_2_complete",
            findings_count=len(round_2_findings),
        )

    # Combine all findings
    all_findings: list[SpecialistFindings] = round_1_findings + round_2_findings

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
    # Step 10: Build response text (deterministic)
    # ------------------------------------------------------------------
    response_text = build_response_text(
        all_findings, contradictions, confidence, request.query_text
    )

    # ------------------------------------------------------------------
    # Step 11: Write audit log (must succeed)
    # ------------------------------------------------------------------
    all_citations = _collect_all_citations(all_findings)

    # TODO Phase 2 — round_number per finding not yet stored.
    # Requires DB migration to add round_number column to query_log.
    # DB Architect micro-session required before this can be completed.
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
    )

    # ------------------------------------------------------------------
    # Step 12: Return response
    # ------------------------------------------------------------------
    logger.info(
        "query_processed",
        project_id=str(request.project_id),
        confidence=confidence.value,
        domains_engaged=domains_engaged,
        round_1_count=len(round_1_findings),
        round_2_count=len(round_2_findings),
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


def build_response_text(
    findings: list[SpecialistFindings],
    contradictions: list[ContradictionFlag],
    confidence: ConfidenceLevel,
    query_text: str,
) -> str:
    """
    Deterministic response assembly from SpecialistFindings.
    No LLM call — structured text composition.

    Uses findings (str) per domain and sources_used document IDs.
    """
    sections: list[str] = []

    # Header
    confidence_labels = {
        ConfidenceLevel.GREEN: "CONSISTENT — all documents agree",
        ConfidenceLevel.AMBER: "PARTIAL — incomplete or limited support",
        ConfidenceLevel.RED: "CONTRADICTION DETECTED — documents disagree",
        ConfidenceLevel.GREY: "INSUFFICIENT DATA — no relevant documents found",
    }
    sections.append(
        f"Confidence: {confidence.value} — {confidence_labels[confidence]}"
    )
    sections.append("")

    # Domain findings
    for finding in findings:
        # Map config key back to display name via DOMAIN_TO_CONFIG_KEY reverse lookup
        display_name = finding.domain
        for domain_name, config_key in DOMAIN_TO_CONFIG_KEY.items():
            if config_key == finding.domain:
                display_name = DOMAIN_DISPLAY_NAMES.get(domain_name, finding.domain)
                break

        round_label = f"Round {finding.round_number}"
        sections.append(f"## {display_name} [{round_label}]")
        sections.append("")
        sections.append(finding.findings)
        sections.append("")

        if finding.sources_used:
            sections.append("Sources referenced:")
            for doc_id in finding.sources_used:
                sections.append(f"  - Document: {doc_id}")
            sections.append("")

    # Contradictions section
    if contradictions:
        sections.append("## Contradictions Detected")
        sections.append("")
        for c in contradictions:
            sections.append(f"- **{c.field_name}**:")
            sections.append(
                f"  Document A ({c.document_a_reference}): {c.value_a}"
            )
            sections.append(
                f"  Document B ({c.document_b_reference}): {c.value_b}"
            )
            sections.append(f"  {c.description}")
            sections.append("")

    return "\n".join(sections)


def _grey_response(
    supabase_client,
    request: QueryRequest,
    domains_engaged: list[str],
    document_ids: list[uuid.UUID],
) -> QueryResponse:
    """
    Handle the GREY path: retrieval returned no relevant documents.
    Still writes an audit log entry.
    """
    response_text = (
        "Confidence: GREY — INSUFFICIENT DATA\n\n"
        "The document warehouse contains no documents relevant to this query. "
        "This may mean the required documents have not yet been uploaded, "
        "or the query does not match any content in the current project."
    )

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
