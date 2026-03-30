"""
C1 — Project Endpoints
Create and list projects.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, status

from src.clients import get_supabase_client
from src.logging_config import get_logger
from src.api.auth import AuthenticatedUser
from src.api.errors import error_response
from src.api.schemas import CreateProjectRequest, ProjectResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    body: CreateProjectRequest,
    user_id: AuthenticatedUser,
) -> ProjectResponse:
    """
    Create a new project.
    Inserts a project record in Supabase.
    """
    supabase_client = get_supabase_client()

    try:
        response = (
            supabase_client.table("projects")
            .insert({
                "name": body.name,
                "description": body.description,
                "owner_id": str(user_id),
            })
            .execute()
        )
    except Exception as exc:
        logger.error("project_creation_failed", error=str(exc))
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="PROJECT_CREATION_FAILED",
            message=f"Failed to create project record: {exc}",
        )

    project = response.data[0]
    project_id = uuid.UUID(project["id"])

    logger.info(
        "project_created",
        project_id=str(project_id),
        name=body.name,
    )

    return ProjectResponse(
        id=uuid.UUID(project["id"]),
        name=project["name"],
        description=project.get("description"),
        created_at=project["created_at"],
        updated_at=project["updated_at"],
    )


@router.get("", response_model=list[ProjectResponse])
async def list_projects(user_id: AuthenticatedUser) -> list[ProjectResponse]:
    """List all projects belonging to the authenticated user."""
    supabase_client = get_supabase_client()

    try:
        response = (
            supabase_client.table("projects")
            .select("*")
            .eq("owner_id", str(user_id))
            .order("created_at", desc=True)
            .execute()
        )
    except Exception as exc:
        logger.error("project_list_failed", error=str(exc))
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="PROJECT_LIST_FAILED",
            message=f"Failed to list projects: {exc}",
        )

    return [
        ProjectResponse(
            id=uuid.UUID(p["id"]),
            name=p["name"],
            description=p.get("description"),
            created_at=p["created_at"],
            updated_at=p["updated_at"],
        )
        for p in response.data
    ]
