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
    parties_count: int = 0  # Count from party_identities


class PartyRoleResponse(BaseModel):
    id: uuid.UUID
    party_identity_id: uuid.UUID
    project_id: uuid.UUID
    role_title: str
    role_category: str
    governing_instrument: str | None
    governing_instrument_type: str | None
    effective_from: date | None
    effective_to: date | None
    authority_scope: str | None
    financial_threshold: str | None
    financial_currency: str | None
    appointment_status: str   # proposed | pending | executed
    source_clause: str | None
    confirmation_status: str  # confirmed | assumed
    created_at: datetime


class PartyIdentityResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    entity_type: str           # organisation | individual
    legal_name: str
    trading_names: list[str]
    registration_number: str | None
    party_category: str
    is_internal: bool
    identification_status: str  # confirmed | assumed
    roles: list[PartyRoleResponse]
    created_at: datetime


class ReconciliationQuestionResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    run_id: uuid.UUID
    question_type: str
    question_text: str
    parties_referenced: list[uuid.UUID]
    documents_referenced: list[uuid.UUID]
    options_presented: list[str]
    answer_selected: str | None
    user_free_text: str | None
    answered_at: datetime | None
    sequence_number: int
    created_at: datetime


class ReconciliationAnswerRequest(BaseModel):
    answer_selected: str
    user_free_text: str | None = None


class InterviewStatusResponse(BaseModel):
    project_id: uuid.UUID
    run_id: uuid.UUID
    total_questions: int
    answered: int
    pending: int
    complete: bool
