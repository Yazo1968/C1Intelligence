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


# ---------------------------------------------------------------------------
# Governance
# ---------------------------------------------------------------------------
class GovernanceRunRequest(BaseModel):
    run_type: str = Field(default="full", pattern="^(full|incremental)$")


class ConfirmPartiesRequest(BaseModel):
    pass  # Empty body — confirms all non-flagged parties for the project


class GovernancePartyUpdateRequest(BaseModel):
    confirmation_status: str | None = None  # confirmed / inferred / flagged


class GovernanceRunResponse(BaseModel):
    run_id: uuid.UUID
    project_id: uuid.UUID
    run_type: str
    status: str
    triggered_at: datetime


class GovernanceStatusResponse(BaseModel):
    project_id: uuid.UUID
    status: str  # not_established | established | stale
    last_run_at: datetime | None
    last_run_id: uuid.UUID | None
    events_confirmed: int
    events_flagged: int
    events_inferred: int
    parties_count: int = 0


class GovernancePartyResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    entity_type: str  # organisation / individual
    canonical_name: str
    aliases: list[str]
    contractual_role: str | None
    terminus_node: bool
    confirmation_status: str  # confirmed / inferred / flagged
    created_at: str


class GovernanceEventResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    event_type: str
    effective_date: date
    end_date: date | None
    party_id: uuid.UUID
    role: str
    appointed_by_party_id: uuid.UUID | None
    authority_dimension: str
    contract_source: str | None
    scope: str | None
    terminus_node: bool
    source_document_id: uuid.UUID | None
    extraction_status: str
    created_at: datetime


class GovernanceEventUpdateRequest(BaseModel):
    extraction_status: str = Field(pattern="^(confirmed|flagged|inferred)$")
    role: str | None = None
    effective_date: date | None = None
    end_date: date | None = None
    scope: str | None = None
    contract_source: str | None = None


class GovernanceEventCreateRequest(BaseModel):
    event_type: str = Field(pattern="^(appointment|delegation|termination|replacement|modification|suspension)$")
    effective_date: date
    end_date: date | None = None
    party_id: uuid.UUID
    role: str
    appointed_by_party_id: uuid.UUID | None = None
    authority_dimension: str = Field(pattern="^(layer_1|layer_2a|layer_2b)$")
    contract_source: str | None = None
    scope: str | None = None
    terminus_node: bool = False
    source_document_id: uuid.UUID | None = None
    extraction_status: str = Field(default="confirmed", pattern="^(confirmed|flagged|inferred)$")
