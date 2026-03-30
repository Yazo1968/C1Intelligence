"""
C1 — Cross-Specialist Contradiction Detection (Stub)
Compares findings across specialists after Round 2 completes.
Phase 5 replaces the body of this function without touching the orchestrator flow.
"""

from __future__ import annotations

from src.logging_config import get_logger
from src.agents.models import SpecialistFindings

logger = get_logger(__name__)


def cross_specialist_contradiction_pass(findings: list[SpecialistFindings]) -> list:
    """
    Compare findings across all specialists for cross-domain contradictions.

    Phase 5 will implement:
    - Legal date vs Schedule date for same event
    - Commercial VO value vs Claims claimed amount for same variation
    - Cross-specialist contradictions written to contradiction_flags with source="specialist_conflict"

    Currently returns an empty list (stub).
    """
    logger.info("cross-specialist contradiction pass not yet implemented")
    return []
