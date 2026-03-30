"""
C1 — Document Status Tracking
Manages the document lifecycle in Supabase: creation, status transitions,
metadata updates, classification queue, and user overrides.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from supabase import Client as SupabaseClient

from src.logging_config import get_logger
from src.ingestion.models import (
    ClassificationResult,
    ExtractedMetadata,
    IngestionError,
    UploadRequest,
)

logger = get_logger(__name__)

VALID_TRANSITIONS: dict[str, list[str]] = {
    "QUEUED": ["EXTRACTING", "FAILED"],
    "EXTRACTING": ["CLASSIFYING", "FAILED"],
    "CLASSIFYING": ["STORED", "FAILED"],
    "FAILED": ["FAILED"],  # Allow re-marking as FAILED (idempotent)
}


def create_document_record(
    supabase_client: SupabaseClient,
    request: UploadRequest,
) -> uuid.UUID:
    """
    Insert a new row into documents with status='QUEUED'.
    Returns the new document UUID.
    """
    row = {
        "project_id": str(request.project_id),
        "filename": request.filename,
        "status": "QUEUED",
        "uploaded_by": str(request.uploaded_by),
        "upload_notes": request.upload_notes,
    }

    if request.contract_id is not None:
        row["contract_id"] = str(request.contract_id)

    try:
        response = (
            supabase_client.table("documents")
            .insert(row)
            .execute()
        )
    except Exception as exc:
        raise IngestionError(
            stage="document_creation",
            message=f"Failed to create document record: {exc}",
        ) from exc

    document_id = uuid.UUID(response.data[0]["id"])

    logger.info(
        "document_record_created",
        document_id=str(document_id),
        project_id=str(request.project_id),
        filename=request.filename,
    )

    return document_id


def update_status(
    supabase_client: SupabaseClient,
    document_id: uuid.UUID,
    new_status: str,
    error_message: str | None = None,
) -> None:
    """
    Transition a document to a new status.
    Validates the transition is legal before writing.
    """
    # Read current status
    try:
        response = (
            supabase_client.table("documents")
            .select("status")
            .eq("id", str(document_id))
            .single()
            .execute()
        )
    except Exception as exc:
        raise IngestionError(
            stage="status_update",
            message=f"Failed to read current status for document {document_id}: {exc}",
            document_id=document_id,
        ) from exc

    current_status = response.data["status"]
    allowed = VALID_TRANSITIONS.get(current_status, [])

    if new_status not in allowed:
        raise IngestionError(
            stage="status_update",
            message=(
                f"Invalid status transition: {current_status} → {new_status}. "
                f"Allowed transitions from {current_status}: {allowed}"
            ),
            document_id=document_id,
        )

    update_data: dict = {"status": new_status}
    if error_message is not None:
        update_data["upload_notes"] = error_message

    try:
        supabase_client.table("documents").update(update_data).eq(
            "id", str(document_id)
        ).execute()
    except Exception as exc:
        raise IngestionError(
            stage="status_update",
            message=f"Failed to update status to {new_status}: {exc}",
            document_id=document_id,
        ) from exc

    logger.info(
        "document_status_updated",
        document_id=str(document_id),
        from_status=current_status,
        to_status=new_status,
    )


def update_document_metadata(
    supabase_client: SupabaseClient,
    document_id: uuid.UUID,
    classification: ClassificationResult | None = None,
    extracted: ExtractedMetadata | None = None,
) -> None:
    """
    Update the document record with classification results and extracted metadata.
    """
    update_data: dict = {}

    if classification is not None:
        update_data["document_type_id"] = classification.document_type_id

    if extracted is not None:
        if extracted.document_date is not None:
            update_data["document_date"] = str(extracted.document_date)
        if extracted.document_reference_number is not None:
            update_data["document_reference_number"] = extracted.document_reference_number
        if extracted.fidic_clause_ref is not None:
            update_data["fidic_clause_ref"] = extracted.fidic_clause_ref
        if extracted.document_status is not None:
            update_data["document_status"] = extracted.document_status
        if extracted.language is not None:
            update_data["language"] = extracted.language
        if extracted.revision_number is not None:
            update_data["revision_number"] = extracted.revision_number
        if extracted.time_bar_deadline is not None:
            update_data["time_bar_deadline"] = str(extracted.time_bar_deadline)

    if not update_data:
        return

    try:
        supabase_client.table("documents").update(update_data).eq(
            "id", str(document_id)
        ).execute()
    except Exception as exc:
        raise IngestionError(
            stage="metadata_update",
            message=f"Failed to update document metadata: {exc}",
            document_id=document_id,
        ) from exc

    logger.info(
        "document_metadata_updated",
        document_id=str(document_id),
        fields_updated=list(update_data.keys()),
    )


def add_to_classification_queue(
    supabase_client: SupabaseClient,
    document_id: uuid.UUID,
    project_id: uuid.UUID,
    reason: str,
    suggested_type_id: int | None,
) -> None:
    """Insert a row into classification_queue for manual review."""
    row: dict = {
        "document_id": str(document_id),
        "project_id": str(project_id),
        "reason": reason,
    }
    if suggested_type_id is not None:
        row["suggested_type_id"] = suggested_type_id

    try:
        supabase_client.table("classification_queue").insert(row).execute()
    except Exception as exc:
        raise IngestionError(
            stage="classification_queue",
            message=f"Failed to add document to classification queue: {exc}",
            document_id=document_id,
        ) from exc

    logger.info(
        "document_queued_for_classification",
        document_id=str(document_id),
        project_id=str(project_id),
        reason=reason,
        suggested_type_id=suggested_type_id,
    )


def apply_user_override(
    supabase_client: SupabaseClient,
    document_id: uuid.UUID,
    override_classification_id: int | None,
    acknowledged_gaps: list[str],
    user_id: uuid.UUID,
) -> None:
    """
    Record a user override decision when the user proceeds despite flags or gaps.
    Creates an auditable accountability trail.
    """
    override_record = json.dumps({
        "override": True,
        "acknowledged_gaps": acknowledged_gaps,
        "override_by": str(user_id),
        "override_at": datetime.now(timezone.utc).isoformat(),
    })

    update_data: dict = {"upload_notes": override_record}

    if override_classification_id is not None:
        update_data["document_type_id"] = override_classification_id

    try:
        supabase_client.table("documents").update(update_data).eq(
            "id", str(document_id)
        ).execute()
    except Exception as exc:
        raise IngestionError(
            stage="user_override",
            message=f"Failed to record user override: {exc}",
            document_id=document_id,
        ) from exc

    # Resolve the classification queue entry if one exists
    try:
        supabase_client.table("classification_queue").update({
            "resolved": True,
            "resolved_by": str(user_id),
            "resolved_at": datetime.now(timezone.utc).isoformat(),
        }).eq("document_id", str(document_id)).eq("resolved", False).execute()
    except Exception as exc:
        # Non-fatal — the override itself was recorded
        logger.error(
            "classification_queue_resolve_failed",
            document_id=str(document_id),
            error=str(exc),
        )

    logger.info(
        "user_override_applied",
        document_id=str(document_id),
        override_classification_id=override_classification_id,
        acknowledged_gaps_count=len(acknowledged_gaps),
    )
