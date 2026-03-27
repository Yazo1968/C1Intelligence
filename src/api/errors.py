"""
C1 — Structured Error Handling
Every endpoint returns structured JSON errors — never raw exceptions.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from src.logging_config import get_logger
from src.ingestion.models import IngestionError
from src.agents.models import AgentError

logger = get_logger(__name__)


def error_response(
    status_code: int,
    error_code: str,
    message: str,
    document_id: uuid.UUID | None = None,
    query_id: uuid.UUID | None = None,
) -> JSONResponse:
    """Build a structured JSON error response."""
    body: dict[str, Any] = {
        "error_code": error_code,
        "message": message,
    }
    if document_id is not None:
        body["document_id"] = str(document_id)
    if query_id is not None:
        body["query_id"] = str(query_id)

    return JSONResponse(status_code=status_code, content=body)


async def ingestion_error_handler(request: Request, exc: IngestionError) -> JSONResponse:
    """Handle IngestionError raised during document ingestion."""
    logger.error(
        "ingestion_error",
        stage=exc.stage,
        message=exc.message,
        document_id=str(exc.document_id) if exc.document_id else None,
    )
    return error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code=f"INGESTION_{exc.stage.upper()}",
        message=exc.message,
        document_id=exc.document_id,
    )


async def agent_error_handler(request: Request, exc: AgentError) -> JSONResponse:
    """Handle AgentError raised during query processing."""
    logger.error(
        "agent_error",
        stage=exc.stage,
        message=exc.message,
    )
    return error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code=f"AGENT_{exc.stage.upper()}",
        message=exc.message,
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions. Never expose raw tracebacks."""
    logger.error(
        "unhandled_error",
        error_type=type(exc).__name__,
        error=str(exc),
    )
    return error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_ERROR",
        message="An unexpected error occurred. Please try again.",
    )
