"""
C1 — Specialist Configuration
Per-domain configuration for each specialist agent.
Defines domain name, round assignment, and max tool rounds.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SpecialistConfig(BaseModel):
    """Configuration for a single domain specialist."""

    domain: str
    round_assignment: int = Field(ge=1, le=2, description="Round 1 or Round 2")
    max_tool_rounds: int = Field(
        ge=1, description="Maximum agentic tool-call iterations before forcing return"
    )


SPECIALIST_CONFIGS: dict[str, SpecialistConfig] = {
    "claims": SpecialistConfig(domain="claims", round_assignment=2, max_tool_rounds=3),
    "legal": SpecialistConfig(domain="legal", round_assignment=1, max_tool_rounds=3),
    "commercial": SpecialistConfig(
        domain="commercial", round_assignment=1, max_tool_rounds=3
    ),
    "schedule": SpecialistConfig(
        domain="schedule", round_assignment=2, max_tool_rounds=3
    ),
    "governance": SpecialistConfig(
        domain="governance", round_assignment=2, max_tool_rounds=3
    ),
    "technical": SpecialistConfig(
        domain="technical", round_assignment=2, max_tool_rounds=3
    ),
}
