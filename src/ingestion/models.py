"""
C1 — Ingestion Data Models
Pydantic models for all data flowing through the ingestion pipeline.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from pydantic import BaseModel, Field


class IngestionError(Exception):
    """Raised when any stage of the ingestion pipeline fails."""

    def __init__(self, stage: str, message: str, document_id: uuid.UUID | None = None) -> None:
        self.stage = stage
        self.message = message
        self.document_id = document_id
        super().__init__(f"[{stage}] {message}")


class UploadRequest(BaseModel):
    """Incoming request from the API layer."""
    project_id: uuid.UUID
    filename: str
    uploaded_by: uuid.UUID
    upload_notes: str | None = None
    contract_id: uuid.UUID | None = None
    user_selected_type_id: int | None = None


class DocumentTypeRow(BaseModel):
    """A single row from the document_types table."""
    id: int
    category: str
    name: str
    possible_formats: list[str]
    tier: int


class ClassificationResult(BaseModel):
    """Output of Claude classification."""
    document_type_id: int
    document_type_name: str
    category: str
    tier: int
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    needs_queue: bool


class ExtractedMetadata(BaseModel):
    """Output of Claude metadata extraction."""
    document_date: date | None = None
    document_reference_number: str | None = None
    issuing_party_name: str | None = None
    receiving_party_name: str | None = None
    fidic_clause_ref: str | None = None
    language: str | None = None
    revision_number: str | None = None
    time_bar_deadline: date | None = None
    document_status: str | None = None


class ValidationGap(BaseModel):
    """A single missing-metadata flag."""
    field_name: str
    requirement_level: str  # "REQUIRED" or "RECOMMENDED"
    message: str


class ValidationResult(BaseModel):
    """Output of tier-based validation."""
    tier: int
    gaps: list[ValidationGap] = Field(default_factory=list)
    has_required_gaps: bool = False
    has_recommended_gaps: bool = False


class IngestionResult(BaseModel):
    """Final result returned by the pipeline."""
    document_id: uuid.UUID
    status: str
    classification: ClassificationResult | None = None
    extracted_metadata: ExtractedMetadata | None = None
    validation: ValidationResult | None = None
    queued_for_review: bool = False
    error_message: str | None = None
