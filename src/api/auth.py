"""
C1 — Supabase Auth JWT Validation
Extracts and validates the JWT from the Authorization header.
Returns the authenticated user ID for downstream RLS enforcement.
"""

from __future__ import annotations

import uuid
from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, Request, status

from src.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
from src.logging_config import get_logger

logger = get_logger(__name__)


async def get_current_user_id(request: Request) -> uuid.UUID:
    """
    Dependency that validates the Supabase Auth JWT from the Authorization header.
    Returns the authenticated user's UUID.
    Raises 401 if the token is missing, invalid, or expired.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "MISSING_AUTH_HEADER", "message": "Authorization header is required."},
        )

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "INVALID_AUTH_FORMAT", "message": "Authorization header must be 'Bearer <token>'."},
        )

    token = parts[1]

    # Validate token by calling Supabase Auth API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": SUPABASE_SERVICE_ROLE_KEY,
                },
                timeout=10.0,
            )
    except httpx.RequestError as exc:
        logger.error("supabase_auth_request_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error_code": "AUTH_SERVICE_UNAVAILABLE", "message": "Authentication service is unavailable."},
        ) from exc

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "INVALID_TOKEN", "message": "Invalid or expired authentication token."},
        )

    user_data = response.json()
    user_id_str = user_data.get("id")

    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "INVALID_USER", "message": "Token does not contain a valid user ID."},
        )

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "INVALID_USER_ID", "message": "User ID in token is not a valid UUID."},
        ) from exc

    return user_id


# Type alias for use as a FastAPI dependency
AuthenticatedUser = Annotated[uuid.UUID, Depends(get_current_user_id)]
