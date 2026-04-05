"""
C1 — Specialist Configuration
Per-domain configuration for each specialist agent.
Defines domain name, tier (1 = orchestrator, 2 = SME), round assignment, and max tool rounds.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SpecialistConfig(BaseModel):
    """Configuration for a single domain specialist or orchestrator."""

    domain: str
    tier: int = Field(ge=1, le=2, description="1 = Tier 1 orchestrator, 2 = Tier 2 SME")
    round_assignment: int = Field(ge=1, le=2, description="Round 1 or Round 2")
    max_tool_rounds: int = Field(
        ge=1, description="Maximum agentic tool-call iterations before forcing return"
    )


SPECIALIST_CONFIGS: dict[str, SpecialistConfig] = {
    "legal": SpecialistConfig(domain="legal", tier=1, round_assignment=1, max_tool_rounds=3),
    "commercial": SpecialistConfig(domain="commercial", tier=1, round_assignment=1, max_tool_rounds=3),
    "financial": SpecialistConfig(domain="financial", tier=1, round_assignment=1, max_tool_rounds=3),
    "schedule": SpecialistConfig(domain="schedule", tier=2, round_assignment=2, max_tool_rounds=3),
    "technical": SpecialistConfig(domain="technical", tier=2, round_assignment=2, max_tool_rounds=3),
}
