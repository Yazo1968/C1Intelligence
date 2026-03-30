"""
C1 — Master Orchestrator
Receives a natural language query, routes to domain specialists,
detects contradictions, synthesizes response, and writes audit log.

This is the only module that knows the full query flow.
"""

from __future__ import annotations

import uuid

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
    SpecialistFinding,
)
from src.agents.prompts import DOMAIN_DISPLAY_NAMES, SPECIALIST_SYSTEM_PROMPTS
from src.agents.retrieval import retrieve_chunks
from src.agents.domain_router import identify_domains
from src.agents.specialist import run_specialist
from src.agents.contradiction import detect_contradictions, write_contradiction_flags
from src.agents.audit import snapshot_document_ids, write_audit_log

logger = get_logger(__name__)


def process_query(request: QueryRequest) -> QueryResponse:
    """
    Full query pipeline:

    1.  Snapshot document IDs (freeze warehouse state)
    2.  Identify relevant domains (Claude)
    3.  Retrieve chunks via pgvector hybrid search
    4.  If empty → GREY confidence, skip specialists
    5.  Run specialists for each relevant domain
    6.  Detect contradictions (Claude)
    7.  Write contradiction flags to DB (non-blocking)
    8.  Determine confidence (deterministic)
    9.  Build response text (deterministic)
    10. Write audit log (must succeed)
    11. Return QueryResponse
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
    # Step 5: Run domain specialists (sequential)
    # ------------------------------------------------------------------
    findings: list[SpecialistFinding] = []
    for domain in domains_engaged:
        prompt = SPECIALIST_SYSTEM_PROMPTS.get(domain)
        if prompt is None:
            logger.warning("unknown_domain_skipped", domain=domain)
            continue

        try:
            finding = run_specialist(
                anthropic_client, domain, request.query_text,
                retrieval.chunks, prompt,
            )
            findings.append(finding)
        except AgentError as exc:
            logger.error(
                "specialist_failed",
                domain=domain,
                error=exc.message,
            )
            # Skip failed domain, continue with others

    # ------------------------------------------------------------------
    # Step 6: Detect contradictions
    # ------------------------------------------------------------------
    contradictions = detect_contradictions(anthropic_client, findings)

    # ------------------------------------------------------------------
    # Step 7: Write contradiction flags (non-blocking)
    # ------------------------------------------------------------------
    if contradictions:
        doc_ref_to_id = _build_doc_reference_map(retrieval)
        write_contradiction_flags(
            supabase_client, request.project_id, contradictions, doc_ref_to_id
        )

    # ------------------------------------------------------------------
    # Step 8: Determine confidence (deterministic)
    # ------------------------------------------------------------------
    confidence = determine_confidence(findings, contradictions, retrieval)

    # ------------------------------------------------------------------
    # Step 9: Build response text (deterministic)
    # ------------------------------------------------------------------
    all_citations = _collect_all_citations(findings)
    response_text = build_response_text(
        findings, contradictions, confidence, request.query_text
    )

    # ------------------------------------------------------------------
    # Step 10: Write audit log (must succeed)
    # ------------------------------------------------------------------
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
    # Step 11: Return response
    # ------------------------------------------------------------------
    logger.info(
        "query_processed",
        project_id=str(request.project_id),
        confidence=confidence.value,
        domains_engaged=domains_engaged,
        specialist_count=len(findings),
        contradiction_count=len(contradictions),
        audit_log_id=str(audit_log_id),
    )

    return QueryResponse(
        query_text=request.query_text,
        response_text=response_text,
        confidence=confidence,
        domains_engaged=domains_engaged,
        specialist_findings=findings,
        contradictions=contradictions,
        document_ids_at_query_time=document_ids,
        audit_log_id=audit_log_id,
    )


def determine_confidence(
    findings: list[SpecialistFinding],
    contradictions: list[ContradictionFlag],
    retrieval: RetrievalResult,
) -> ConfidenceLevel:
    """
    Deterministic confidence classification. No LLM call.

    GREY  — retrieval returned no relevant documents
    RED   — contradictions detected between documents
    AMBER — partial coverage (some specialists found nothing, or few citations)
    GREEN — consistent findings across all specialists
    """
    if retrieval.is_empty:
        return ConfidenceLevel.GREY

    if contradictions:
        return ConfidenceLevel.RED

    # AMBER if any specialist had no findings, or total citations are sparse
    if not findings:
        return ConfidenceLevel.AMBER

    for finding in findings:
        if not finding.key_findings:
            return ConfidenceLevel.AMBER

    total_citations = sum(
        len(kf.citations)
        for f in findings
        for kf in f.key_findings
    )
    if total_citations < 2:
        return ConfidenceLevel.AMBER

    return ConfidenceLevel.GREEN


def build_response_text(
    findings: list[SpecialistFinding],
    contradictions: list[ContradictionFlag],
    confidence: ConfidenceLevel,
    query_text: str,
) -> str:
    """
    Deterministic response assembly from specialist findings.
    No LLM call — structured text composition.
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
        display_name = DOMAIN_DISPLAY_NAMES.get(finding.domain, finding.domain)
        sections.append(f"## {display_name}")
        sections.append("")
        sections.append(finding.analysis)
        sections.append("")

        for kf in finding.key_findings:
            sections.append(f"- {kf.statement}")
            for cite in kf.citations:
                cite_parts: list[str] = []
                if cite.document_reference:
                    cite_parts.append(cite.document_reference)
                if cite.document_type:
                    cite_parts.append(cite.document_type)
                if cite.document_date:
                    cite_parts.append(cite.document_date)
                cite_label = " | ".join(cite_parts) if cite_parts else "Source"
                sections.append(f"  [{cite_label}]")
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


def _collect_all_citations(findings: list[SpecialistFinding]) -> list[SourceCitation]:
    """Collect all citations from all findings for the audit log."""
    citations: list[SourceCitation] = []
    for finding in findings:
        for kf in finding.key_findings:
            citations.extend(kf.citations)
    return citations
