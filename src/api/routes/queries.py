"""
C1 — Query, Audit Log, and Contradiction Endpoints
Submit queries, retrieve audit logs, and list contradiction flags.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, status

from src.clients import get_supabase_client
from src.logging_config import get_logger
from src.api.auth import AuthenticatedUser
from src.api.errors import error_response
from src.api.schemas import (
    ContradictionResponse,
    QueryLogEntry,
    QueryResponseSchema,
    SubmitQueryRequest,
)
from src.agents.models import AgentError, QueryRequest
from src.agents.orchestrator import process_query

logger = get_logger(__name__)

router = APIRouter(prefix="/projects/{project_id}", tags=["queries"])


@router.post("/query", response_model=QueryResponseSchema, status_code=status.HTTP_200_OK)
async def submit_query(
    project_id: uuid.UUID,
    body: SubmitQueryRequest,
    user_id: AuthenticatedUser,
) -> QueryResponseSchema:
    """
    Submit a natural language query against a project's document warehouse.
    Runs the full orchestrator pipeline: domain routing → retrieval →
    specialists → contradiction detection → synthesis → audit log.
    """
    # Verify project access (RLS will enforce, but give clear error early)
    supabase_client = get_supabase_client()
    try:
        supabase_client.table("projects").select("id").eq(
            "id", str(project_id)
        ).eq("owner_id", str(user_id)).single().execute()
    except Exception:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="PROJECT_NOT_FOUND",
            message=f"Project {project_id} not found or access denied.",
        )

    request = QueryRequest(
        project_id=project_id,
        user_id=user_id,
        query_text=body.query_text,
    )

    try:
        result = process_query(request)
    except AgentError as exc:
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=f"AGENT_{exc.stage.upper()}",
            message=exc.message,
        )

    return QueryResponseSchema(
        query_text=result.query_text,
        response_text=result.response_text,
        confidence=result.confidence.value,
        domains_engaged=result.domains_engaged,
        specialist_findings=[
            {
                "domain": f.domain,
                "analysis": f.analysis,
                "key_findings": [
                    {
                        "statement": kf.statement,
                        "citations": [
                            {
                                "document_id": str(c.document_id) if c.document_id else None,
                                "document_type": c.document_type,
                                "document_date": c.document_date,
                                "document_reference": c.document_reference,
                                "excerpt": c.excerpt,
                            }
                            for c in kf.citations
                        ],
                    }
                    for kf in f.key_findings
                ],
            }
            for f in result.specialist_findings
        ],
        contradictions=[
            {
                "field_name": c.field_name,
                "document_a_reference": c.document_a_reference,
                "value_a": c.value_a,
                "document_b_reference": c.document_b_reference,
                "value_b": c.value_b,
                "description": c.description,
            }
            for c in result.contradictions
        ],
        document_ids_at_query_time=result.document_ids_at_query_time,
        audit_log_id=result.audit_log_id,
    )


@router.get("/query-log", response_model=list[QueryLogEntry])
async def get_query_log(
    project_id: uuid.UUID,
    user_id: AuthenticatedUser,
) -> list[QueryLogEntry]:
    """Retrieve the immutable audit log for a project."""
    supabase_client = get_supabase_client()

    try:
        response = (
            supabase_client.table("query_log")
            .select("*")
            .eq("project_id", str(project_id))
            .order("created_at", desc=True)
            .execute()
        )
    except Exception as exc:
        logger.error("query_log_fetch_failed", error=str(exc))
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="QUERY_LOG_FAILED",
            message=f"Failed to retrieve query log: {exc}",
        )

    return [
        QueryLogEntry(
            id=uuid.UUID(row["id"]),
            project_id=uuid.UUID(row["project_id"]),
            user_id=uuid.UUID(row["user_id"]),
            query_text=row["query_text"],
            response_text=row["response_text"],
            confidence=row["confidence"],
            domains_engaged=row.get("domains_engaged"),
            document_ids_at_query_time=(
                [uuid.UUID(d) for d in row["document_ids_at_query_time"]]
                if row.get("document_ids_at_query_time")
                else None
            ),
            citations=row.get("citations"),
            created_at=row["created_at"],
        )
        for row in response.data
    ]


@router.get("/contradictions", response_model=list[ContradictionResponse])
async def list_contradictions(
    project_id: uuid.UUID,
    user_id: AuthenticatedUser,
) -> list[ContradictionResponse]:
    """List all contradiction flags for a project."""
    supabase_client = get_supabase_client()

    try:
        response = (
            supabase_client.table("contradiction_flags")
            .select("*")
            .eq("project_id", str(project_id))
            .order("created_at", desc=True)
            .execute()
        )
    except Exception as exc:
        logger.error("contradictions_fetch_failed", error=str(exc))
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="CONTRADICTIONS_FAILED",
            message=f"Failed to retrieve contradictions: {exc}",
        )

    return [
        ContradictionResponse(
            id=uuid.UUID(row["id"]),
            project_id=uuid.UUID(row["project_id"]),
            document_a_id=uuid.UUID(row["document_a_id"]),
            document_b_id=uuid.UUID(row["document_b_id"]),
            field_name=row["field_name"],
            description=row.get("description"),
            created_at=row["created_at"],
        )
        for row in response.data
    ]
