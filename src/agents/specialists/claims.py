"""C1 — Claims & Disputes Specialist (Phase 1 stub)."""

from src.agents.base_specialist import BaseSpecialist
from src.agents.specialist_config import SPECIALIST_CONFIGS

claims_specialist = BaseSpecialist(config=SPECIALIST_CONFIGS["claims"])
