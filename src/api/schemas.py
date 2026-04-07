"""
C1 — API Request/Response Schemas
Pydantic models for FastAPI endpoint inputs and outputs.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------
class CreateProjectRequest(BaseModel):
    name: str
    description: str | None = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------
class DocumentResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    document_type_id: int | None
    document_type_name: str | None = None
    category: str | None = None
    contract_id: uuid.UUID | None
    filename: str
    status: str
    tier: int | None = None
    document_date: date | None
    document_reference_number: str | None
    issuing_party_id: uuid.UUID | None
    receiving_party_id: uuid.UUID | None
    fidic_clause_ref: str | None
    document_status: str | None
    language: str | None
    revision_number: str | None
    time_bar_deadline: date | None
    upload_notes: str | None
    uploaded_by: uuid.UUID
    created_at: datetime
    updated_at: datetime


class DocumentUploadResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    queued_for_review: bool = False
    classification: dict[str, Any] | None = None
    validation_gaps: list[dict[str, Any]] | None = None
    error_message: str | None = None
    message: str | None = None


class DocumentStatusResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    filename: str


class DocumentDownloadResponse(BaseModel):
    download_url: str
    filename: str
    expires_in: int = 60


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------
class SubmitQueryRequest(BaseModel):
    query_text: str
    domains: list[str] | None = None


class QueryAcceptedResponse(BaseModel):
    query_id: uuid.UUID
    status: str
    message: str


class QueryStatusResponse(BaseModel):
    query_id: uuid.UUID
    status: str
    response: dict[str, Any] | None = None


class QueryResponseSchema(BaseModel):
    query_text: str
    response_text: str
    confidence: str
    domains_engaged: list[str]
    specialist_findings: list[dict[str, Any]]
    contradictions: list[dict[str, Any]]
    document_ids_at_query_time: list[uuid.UUID]
    audit_log_id: uuid.UUID | None


class DomainRecommendationSchema(BaseModel):
    domain: str
    relevance: str
    reason: str


class Round0AssessmentResponse(BaseModel):
    executive_brief: str
    documents_retrieved: list[str]
    domain_recommendations: list[DomainRecommendationSchema]
    default_domains: list[str]


# ---------------------------------------------------------------------------
# Query Log
# ---------------------------------------------------------------------------
class QueryLogEntry(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    query_text: str
    response_text: str
    confidence: str
    domains_engaged: list[str] | None
    document_ids_at_query_time: list[uuid.UUID] | None
    citations: Any | None
    created_at: datetime


# ---------------------------------------------------------------------------
# Contradictions
# ---------------------------------------------------------------------------
class ContradictionResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    document_a_id: uuid.UUID
    document_b_id: uuid.UUID
    field_name: str
    description: str | None
    created_at: datetime


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str = "ok"


# =============================================================================
# Governance — Function 1: Entity Directory
# =============================================================================

class EntityDirectoryRunResponse(BaseModel):
    id: str
    project_id: str
    status: str
    chunks_processed: int
    total_chunks: int
    organisations_found: int
    individuals_found: int
    error_message: str | None = None

class EntityResponse(BaseModel):
    id: str
    project_id: str
    run_id: str
    entity_type: str
    canonical_name: str
    name_variants: list[str]
    short_address: str | None = None
    title: str | None = None
    confirmation_status: str
    user_note: str | None = None

class EntityDiscrepancyResponse(BaseModel):
    id: str
    project_id: str
    run_id: str
    discrepancy_type: str
    description: str
    name_a: str
    name_b: str | None = None
    chunk_references: list[str]
    resolution: str | None = None
    resolved_canonical: str | None = None
    user_note: str | None = None

class PatchEntityRequest(BaseModel):
    canonical_name: str | None = None
    confirmation_status: str | None = None   # confirmed | rejected
    user_note: str | None = None
    name_variants: list[str] | None = None
    # Full replacement of name_variants array.
    # Frontend sends the complete updated list.

class ResolveDiscrepancyRequest(BaseModel):
    resolution: str                          # same_entity | different_entities | correction
    resolved_canonical: str | None = None
    user_note: str | None = None


# =============================================================================
# Governance — Function 2: Event Log
# =============================================================================

class EventLogRunResponse(BaseModel):
    id: str
    project_id: str
    entity_id: str
    status: str
    triggered_at: str
    completed_at: str | None = None
    chunks_scanned: int
    events_extracted: int
    error_message: str | None = None

class EntityEventResponse(BaseModel):
    id: str
    project_id: str
    entity_id: str
    run_id: str
    event_type: str
    event_date: str | None = None
    event_date_certain: bool
    status_before: str | None = None
    status_after: str | None = None
    initiated_by: str | None = None
    authorised_by: str | None = None
    source_document: str | None = None
    source_excerpt: str | None = None
    confirmation_status: str
    user_note: str | None = None
    sequence_number: int

class EventLogQuestionResponse(BaseModel):
    id: str
    project_id: str
    run_id: str
    entity_id: str
    question_text: str
    question_type: str
    events_referenced: list[str]
    answer: str | None = None
    sequence_number: int

class PatchEventRequest(BaseModel):
    event_type: str | None = None
    event_date: str | None = None
    event_date_certain: bool | None = None
    status_before: str | None = None
    status_after: str | None = None
    initiated_by: str | None = None
    authorised_by: str | None = None
    confirmation_status: str | None = None   # confirmed | disputed | rejected
    user_note: str | None = None

class AnswerQuestionRequest(BaseModel):
    answer: str

class AbsorbEntityRequest(BaseModel):
    source_entity_id: str
    # The entity being absorbed (will be marked merged).
    # Its canonical_name and name_variants are moved into the
    # target entity's name_variants list.

