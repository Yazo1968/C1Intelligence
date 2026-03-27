"""
C1 — Audit Log and Document Snapshot
Writes immutable query_log entries and snapshots document IDs at query time.
"""

from __future__ import annotations

import json
import uuid
from typing import Any

from supabase import Client as SupabaseClient

from src.logging_config import get_logger
from src.agents.models import AgentError, ConfidenceLevel, SourceCitation

logger = get_logger(__name__)


def snapshot_document_ids(
    supabase_client: SupabaseClient,
    project_id: uuid.UUID,
) -> list[uuid.UUID]:
    """
    Capture the current set of STORED document IDs for a project.
    Called at the start of query processing to freeze the warehouse state.

    This snapshot is written to query_log.document_ids_at_query_time for
    forensic reconstruction: "at the time this query was answered,
    these were the documents in the system."
    """
    try:
        response = (
            supabase_client.table("documents")
            .select("id")
            .eq("project_id", str(project_id))
            .eq("status", "STORED")
            .execute()
        )
    except Exception as exc:
        raise AgentError(
            stage="document_snapshot",
            message=f"Failed to snapshot document IDs for project {project_id}: {exc}",
        ) from exc

    doc_ids = [uuid.UUID(row["id"]) for row in response.data]

    logger.info(
        "document_snapshot_taken",
        project_id=str(project_id),
        document_count=len(doc_ids),
    )

    return doc_ids


def write_audit_log(
    supabase_client: SupabaseClient,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    query_text: str,
    response_text: str,
    confidence: ConfidenceLevel,
    domains_engaged: list[str],
    document_ids: list[uuid.UUID],
    citations: list[SourceCitation],
) -> uuid.UUID:
    """
    Write an immutable entry to the query_log table.

    This write MUST succeed before the orchestrator returns a response.
    If it fails, the orchestrator raises AgentError — no response is
    delivered without a forensic audit trail.

    Returns the UUID of the created audit log entry.
    """
    citations_json = _serialize_citations(citations)

    row = {
        "project_id": str(project_id),
        "user_id": str(user_id),
        "query_text": query_text,
        "response_text": response_text,
        "confidence": confidence.value,
        "domains_engaged": domains_engaged,
        "document_ids_at_query_time": [str(d) for d in document_ids],
        "citations": citations_json,
    }

    try:
        response = (
            supabase_client.table("query_log")
            .insert(row)
            .execute()
        )
    except Exception as exc:
        raise AgentError(
            stage="audit_log",
            message=f"Failed to write audit log entry: {exc}",
        ) from exc

    audit_log_id = uuid.UUID(response.data[0]["id"])

    logger.info(
        "audit_log_written",
        audit_log_id=str(audit_log_id),
        project_id=str(project_id),
        user_id=str(user_id),
        confidence=confidence.value,
        domains_engaged=domains_engaged,
    )

    return audit_log_id


def _serialize_citations(citations: list[SourceCitation]) -> list[dict[str, Any]]:
    """Convert SourceCitation models to JSON-serializable dicts for the citations column."""
    return [
        {
            "document_id": str(c.document_id) if c.document_id else None,
            "document_type": c.document_type,
            "document_date": c.document_date,
            "document_reference": c.document_reference,
            "excerpt": c.excerpt,
        }
        for c in citations
    ]
