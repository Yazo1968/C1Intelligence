"""
C1 — Health Check Endpoint
No authentication required. Used for deployment health checks.
"""

from fastapi import APIRouter

from src.api.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Returns 200 OK. No auth required."""
    return HealthResponse(status="ok")
