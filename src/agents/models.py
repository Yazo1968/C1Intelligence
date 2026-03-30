"""
C1 — Agent Layer Data Models
Pydantic models for the query orchestration pipeline.
"""

from __future__ import annotations

import uuid
from enum import Enum

from pydantic import BaseModel, Field


class AgentError(Exception):
    """Raised when any stage of the agent pipeline fails."""

    def __init__(self, stage: str, message: str) -> None:
        self.stage = stage
        self.message = message
        super().__init__(f"[{stage}] {message}")


class QueryRequest(BaseModel):
    """Incoming query from the API layer."""
    project_id: uuid.UUID
    user_id: uuid.UUID
    query_text: str


class RetrievedChunk(BaseModel):
    """A single chunk returned by Gemini File Search with citation info."""
    text: str
    document_id: uuid.UUID | None = None
    document_type: str | None = None
    document_date: str | None = None
    document_reference: str | None = None
    relevance_score: float | None = None


class RetrievalResult(BaseModel):
    """Output of Gemini File Search retrieval."""
    chunks: list[RetrievedChunk] = Field(default_factory=list)
    raw_response_text: str = ""
    is_empty: bool = True


class DomainIdentification(BaseModel):
    """Output of Claude domain routing."""
    domains: list[str]
    reasoning: str


class SourceCitation(BaseModel):
    """A citation linking a claim to a source document."""
    document_id: uuid.UUID | None = None
    document_type: str | None = None
    document_date: str | None = None
    document_reference: str | None = None
    excerpt: str = ""


class KeyFinding(BaseModel):
    """A single finding from a specialist."""
    statement: str
    citations: list[SourceCitation] = Field(default_factory=list)


class SpecialistFinding(BaseModel):
    """Output of a single domain specialist."""
    domain: str
    analysis: str
    key_findings: list[KeyFinding] = Field(default_factory=list)


class ContradictionFlag(BaseModel):
    """A detected contradiction between two documents."""
    document_a_id: uuid.UUID | None = None
    document_b_id: uuid.UUID | None = None
    document_a_reference: str = ""
    document_b_reference: str = ""
    field_name: str
    value_a: str
    value_b: str
    description: str


class ConfidenceLevel(str, Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"
    GREY = "GREY"


class QueryResponse(BaseModel):
    """Final response returned to the API layer."""
    query_text: str
    response_text: str
    confidence: ConfidenceLevel
    domains_engaged: list[str]
    specialist_findings: list[SpecialistFinding] = Field(default_factory=list)
    contradictions: list[ContradictionFlag] = Field(default_factory=list)
    document_ids_at_query_time: list[uuid.UUID] = Field(default_factory=list)
    audit_log_id: uuid.UUID | None = None


# =============================================================================
# Phase 1 — Agentic Specialist Models (AGENT_PLAN.md)
# =============================================================================


class SpecialistFindings(BaseModel):
    """
    Output of a single agentic specialist run.
    Used by BaseSpecialist (Phase 1+). Distinct from the legacy SpecialistFinding
    model above, which remains in use by the v1 orchestrator until Phase 2.
    """

    domain: str
    findings: str
    confidence: str  # GREEN / AMBER / RED / GREY
    sources_used: list[str] = Field(
        default_factory=list, description="document_ids that contributed"
    )
    tools_called: list[str] = Field(
        default_factory=list, description="Tool names called during this run"
    )
    round_number: int = Field(description="1 or 2")
    flagged_contradictions: list[str] = Field(
        default_factory=list, description="contradiction_flag IDs surfaced"
    )
