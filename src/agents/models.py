"""
C1 — Agent Layer Data Models
Pydantic models for the query orchestration pipeline.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field as dataclass_field
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
    domains: list[str] | None = None


@dataclass
class DomainRecommendation:
    """Domain relevance assessment from the Round 0 classifier."""
    domain: str
    relevance: str    # "PRIMARY" | "RELEVANT" | "NOT_APPLICABLE"
    reason: str       # one sentence


@dataclass
class Round0Assessment:
    """Output of the fast Round 0 assessment endpoint."""
    executive_brief: str
    documents_retrieved: list[str]
    domain_recommendations: list[DomainRecommendation]
    default_domains: list[str]   # PRIMARY domains pre-selected


class RetrievedChunk(BaseModel):
    """A single chunk from Layer 1 (project documents) or Layer 2 (reference documents).

    Layer 1 chunks are project-scoped and have document_id.
    Layer 2 chunks are platform-wide reference material (FIDIC, PMBOK, etc.)
    and are identified by is_reference=True.
    """
    text: str
    document_id: uuid.UUID | None = None
    chunk_index: int | None = None
    document_type: str | None = None
    document_date: str | None = None
    document_reference: str | None = None
    relevance_score: float | None = None
    is_reference: bool = False
    filename: str | None = None
    document_reference_number: str | None = None
    document_type_name: str | None = None
    citation_fields: list[str] | None = None


class RetrievalResult(BaseModel):
    """Output of pgvector hybrid retrieval (Layer 1 + Layer 2)."""
    chunks: list[RetrievedChunk] = Field(default_factory=list)
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


class LayerRetrievalStatus(str, Enum):
    RETRIEVED = "RETRIEVED"
    NOT_RETRIEVED = "NOT_RETRIEVED"
    PARTIAL = "PARTIAL"


class EvidenceRecord(BaseModel):
    """
    Records what was retrieved from each warehouse layer during specialist
    analysis. Populated by parsing the Evidence Declaration block from
    the specialist's output. Used to apply automatic confidence caps.
    """
    layer2b_status: LayerRetrievalStatus = LayerRetrievalStatus.NOT_RETRIEVED
    layer2b_source: str | None = None          # standard form name if retrieved
    layer2a_status: LayerRetrievalStatus = LayerRetrievalStatus.NOT_RETRIEVED
    layer2a_source: str | None = None          # policy name if retrieved
    layer1_primary_document: str | None = None
    layer1_amendment_document_status: LayerRetrievalStatus = (
        LayerRetrievalStatus.NOT_RETRIEVED
    )
    provisions_cannot_confirm: list[str] = Field(
        default_factory=list,
        description="Provisions where retrieval failed and output is CANNOT CONFIRM",
    )


class QueryResponse(BaseModel):
    """Final response returned to the API layer."""
    query_text: str
    response_text: str
    confidence: ConfidenceLevel
    domains_engaged: list[str]
    specialist_findings: list["SpecialistFindings"] = Field(default_factory=list)
    contradictions: list[ContradictionFlag] = Field(default_factory=list)
    document_ids_at_query_time: list[uuid.UUID] = Field(default_factory=list)
    audit_log_id: uuid.UUID | None = None
    routing_gaps: list[str] = Field(default_factory=list)


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
    evidence_record: EvidenceRecord | None = Field(
        default=None,
        description="Parsed from the Evidence Declaration block in the findings output",
    )
