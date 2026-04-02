"""
C1 — Query, Audit Log, and Contradiction Endpoints
Submit queries, retrieve audit logs, and list contradiction flags.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, status

from src.clients import get_supabase_client
from src.logging_config import get_logger
from src.api.auth import AuthenticatedUser
from src.api.errors import error_response
from src.api.schemas import (
    ContradictionResponse,
    QueryAcceptedResponse,
    QueryLogEntry,
    QueryResponseSchema,
    QueryStatusResponse,
    SubmitQueryRequest,
)
from src.agents.models import AgentError, QueryRequest
from src.agents.orchestrator import process_query

logger = get_logger(__name__)

router = APIRouter(prefix="/projects/{project_id}", tags=["queries"])

# In-memory store for query processing status.
# Keyed by query_id (str), values are dicts with "status" and optional "response"/"error".
_query_status: dict[str, dict[str, Any]] = {}


def _run_query_pipeline(
    query_id: str,
    request: QueryRequest,
) -> None:
    """Run the query pipeline in a background thread and store results."""
    try:
        logger.info(
            "background_query_started",
            query_id=query_id,
            project_id=str(request.project_id),
        )

        result = process_query(request)

        response_data = {
            "query_text": result.query_text,
            "response_text": result.response_text,
            "confidence": result.confidence.value,
            "domains_engaged": result.domains_engaged,
            "specialist_findings": [
                {
                    "domain": f.domain,
                    "findings": f.findings,
                    "confidence": f.confidence,
                    "sources_used": f.sources_used,
                    "tools_called": f.tools_called,
                    "round_number": f.round_number,
                    "flagged_contradictions": f.flagged_contradictions,
                }
                for f in result.specialist_findings
            ],
            "contradictions": [
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
            "document_ids_at_query_time": [
                str(d) for d in result.document_ids_at_query_time
            ],
            "audit_log_id": str(result.audit_log_id) if result.audit_log_id else None,
        }

        _query_status[query_id] = {
            "status": "COMPLETE",
            "response": response_data,
        }

        logger.info(
            "background_query_complete",
            query_id=query_id,
            confidence=result.confidence.value,
        )

    except AgentError as exc:
        logger.error(
            "background_query_agent_error",
            query_id=query_id,
            stage=exc.stage,
            error=exc.message,
        )
        _query_status[query_id] = {
            "status": "FAILED",
            "error": exc.message,
        }

    except Exception as exc:
        logger.error(
            "background_query_unexpected_error",
            query_id=query_id,
            error=str(exc),
        )
        _query_status[query_id] = {
            "status": "FAILED",
            "error": str(exc),
        }


@router.post("/query", response_model=QueryAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_query(
    project_id: uuid.UUID,
    body: SubmitQueryRequest,
    user_id: AuthenticatedUser,
    background_tasks: BackgroundTasks,
) -> QueryAcceptedResponse:
    """
    Submit a natural language query against a project's document warehouse.
    Returns immediately with a query_id. The pipeline runs in the background.
    Poll GET /projects/{id}/queries/{query_id}/status for results.
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

    query_id = str(uuid.uuid4())

    request = QueryRequest(
        project_id=project_id,
        user_id=user_id,
        query_text=body.query_text,
    )

    # Mark as processing before launching background task
    _query_status[query_id] = {"status": "PROCESSING"}

    background_tasks.add_task(_run_query_pipeline, query_id, request)

    return QueryAcceptedResponse(
        query_id=uuid.UUID(query_id),
        status="PROCESSING",
        message="Query received. Analysis has started.",
    )


@router.get("/queries/{query_id}/status", response_model=QueryStatusResponse)
async def get_query_status(
    project_id: uuid.UUID,
    query_id: uuid.UUID,
    user_id: AuthenticatedUser,
) -> QueryStatusResponse:
    """Get the processing status of an async query. Returns the full response when complete."""
    status_entry = _query_status.get(str(query_id))

    if not status_entry:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="QUERY_NOT_FOUND",
            message=f"Query {query_id} not found.",
        )

    return QueryStatusResponse(
        query_id=query_id,
        status=status_entry["status"],
        response=status_entry.get("response"),
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
