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


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------
class SubmitQueryRequest(BaseModel):
    query_text: str
    risk_mode: bool = False
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
