"""
C1 — Document Endpoints
Upload, list, and retrieve documents within a project.
"""

from __future__ import annotations

import os
import tempfile
import uuid

from fastapi import APIRouter, File, Form, UploadFile, status

from src.clients import get_supabase_client
from src.logging_config import get_logger
from src.api.auth import AuthenticatedUser
from src.api.errors import error_response
from src.api.schemas import DocumentResponse, DocumentUploadResponse
from src.ingestion.models import IngestionError, UploadRequest
from src.ingestion.pipeline import ingest_document

logger = get_logger(__name__)

router = APIRouter(prefix="/projects/{project_id}/documents", tags=["documents"])


@router.post("", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    project_id: uuid.UUID,
    user_id: AuthenticatedUser,
    file: UploadFile = File(...),
    contract_id: uuid.UUID | None = Form(None),
    user_selected_type_id: int | None = Form(None),
    upload_notes: str | None = Form(None),
) -> DocumentUploadResponse:
    """
    Upload a document to a project. Runs the full ingestion pipeline:
    validation → Gemini upload → classification → metadata extraction → storage.
    """
    # Verify the project belongs to the user (RLS will enforce this,
    # but we check early to give a clear error)
    supabase_client = get_supabase_client()
    try:
        project_response = (
            supabase_client.table("projects")
            .select("id")
            .eq("id", str(project_id))
            .eq("owner_id", str(user_id))
            .single()
            .execute()
        )
    except Exception:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="PROJECT_NOT_FOUND",
            message=f"Project {project_id} not found or access denied.",
        )

    # Read file content and save to a temp file for the pipeline
    content = await file.read()
    file_size = len(content)
    filename = file.filename or "unnamed"

    temp_path: str | None = None
    try:
        # Write to temp file — pipeline expects a file path
        suffix = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            temp_path = tmp.name

        request = UploadRequest(
            project_id=project_id,
            filename=filename,
            uploaded_by=user_id,
            upload_notes=upload_notes,
            contract_id=contract_id,
            user_selected_type_id=user_selected_type_id,
        )

        result = ingest_document(
            file_path=temp_path,
            file_size_bytes=file_size,
            request=request,
        )

        classification_dict = None
        if result.classification:
            classification_dict = {
                "document_type_id": result.classification.document_type_id,
                "document_type_name": result.classification.document_type_name,
                "category": result.classification.category,
                "tier": result.classification.tier,
                "confidence": result.classification.confidence,
                "reasoning": result.classification.reasoning,
            }

        validation_gaps = None
        if result.validation and result.validation.gaps:
            validation_gaps = [
                {
                    "field_name": g.field_name,
                    "requirement_level": g.requirement_level,
                    "message": g.message,
                }
                for g in result.validation.gaps
            ]

        return DocumentUploadResponse(
            document_id=result.document_id,
            status=result.status,
            queued_for_review=result.queued_for_review,
            classification=classification_dict,
            validation_gaps=validation_gaps,
            error_message=result.error_message,
        )

    except IngestionError as exc:
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=f"INGESTION_{exc.stage.upper()}",
            message=exc.message,
            document_id=exc.document_id,
        )
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    project_id: uuid.UUID,
    user_id: AuthenticatedUser,
) -> list[DocumentResponse]:
    """List all documents in a project with status, type, tier, and metadata."""
    supabase_client = get_supabase_client()

    try:
        response = (
            supabase_client.table("documents")
            .select("*, document_types(name, category, tier)")
            .eq("project_id", str(project_id))
            .order("created_at", desc=True)
            .execute()
        )
    except Exception as exc:
        logger.error("document_list_failed", error=str(exc))
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DOCUMENT_LIST_FAILED",
            message=f"Failed to list documents: {exc}",
        )

    return [_to_document_response(d) for d in response.data]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    project_id: uuid.UUID,
    document_id: uuid.UUID,
    user_id: AuthenticatedUser,
) -> DocumentResponse:
    """Get a single document record with full metadata."""
    supabase_client = get_supabase_client()

    try:
        response = (
            supabase_client.table("documents")
            .select("*, document_types(name, category, tier)")
            .eq("id", str(document_id))
            .eq("project_id", str(project_id))
            .single()
            .execute()
        )
    except Exception:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="DOCUMENT_NOT_FOUND",
            message=f"Document {document_id} not found in project {project_id}.",
        )

    return _to_document_response(response.data)


def _to_document_response(row: dict) -> DocumentResponse:
    """Convert a Supabase row (with joined document_types) to a DocumentResponse."""
    doc_type = row.get("document_types") or {}

    return DocumentResponse(
        id=uuid.UUID(row["id"]),
        project_id=uuid.UUID(row["project_id"]),
        document_type_id=row.get("document_type_id"),
        document_type_name=doc_type.get("name"),
        category=doc_type.get("category"),
        contract_id=uuid.UUID(row["contract_id"]) if row.get("contract_id") else None,
        filename=row["filename"],
        status=row["status"],
        tier=doc_type.get("tier"),
        gemini_file_name=row.get("gemini_file_name"),
        gemini_document_name=row.get("gemini_document_name"),
        document_date=row.get("document_date"),
        document_reference_number=row.get("document_reference_number"),
        issuing_party_id=uuid.UUID(row["issuing_party_id"]) if row.get("issuing_party_id") else None,
        receiving_party_id=uuid.UUID(row["receiving_party_id"]) if row.get("receiving_party_id") else None,
        fidic_clause_ref=row.get("fidic_clause_ref"),
        document_status=row.get("document_status"),
        language=row.get("language"),
        revision_number=row.get("revision_number"),
        time_bar_deadline=row.get("time_bar_deadline"),
        upload_notes=row.get("upload_notes"),
        uploaded_by=uuid.UUID(row["uploaded_by"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
