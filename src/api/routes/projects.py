"""
C1 — Project Endpoints
Create and list projects. Project creation is atomic:
both Supabase record and Gemini store must succeed or both roll back.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, status

from src.clients import get_gemini_client, get_supabase_client
from src.logging_config import get_logger
from src.api.auth import AuthenticatedUser
from src.api.errors import error_response
from src.api.schemas import CreateProjectRequest, ProjectResponse
from src.ingestion.store_manager import create_store_for_project

logger = get_logger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    body: CreateProjectRequest,
    user_id: AuthenticatedUser,
) -> ProjectResponse:
    """
    Create a new project. Atomic operation:
    1. Insert project record in Supabase
    2. Create Gemini File Search store
    3. Write store name back to project record

    If Gemini store creation fails, the Supabase record is deleted.
    """
    supabase_client = get_supabase_client()
    gemini_client = get_gemini_client()

    # Step 1: Create Supabase record
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

    # Step 2: Create Gemini store (rolls back Supabase record on failure)
    try:
        create_store_for_project(
            gemini_client, supabase_client, project_id, body.name
        )
    except Exception as exc:
        logger.error(
            "gemini_store_creation_failed_rolling_back",
            project_id=str(project_id),
            error=str(exc),
        )
        # Roll back: delete the Supabase project record
        try:
            supabase_client.table("projects").delete().eq("id", str(project_id)).execute()
        except Exception as rollback_exc:
            logger.error(
                "project_rollback_failed",
                project_id=str(project_id),
                error=str(rollback_exc),
            )

        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="GEMINI_STORE_CREATION_FAILED",
            message=f"Failed to create Gemini store. Project rolled back: {exc}",
        )

    # Re-fetch the project to get the updated gemini_store_name
    try:
        response = (
            supabase_client.table("projects")
            .select("*")
            .eq("id", str(project_id))
            .single()
            .execute()
        )
        project = response.data
    except Exception:
        pass  # Use the original project data if re-fetch fails

    logger.info(
        "project_created",
        project_id=str(project_id),
        name=body.name,
    )

    return ProjectResponse(
        id=uuid.UUID(project["id"]),
        name=project["name"],
        description=project.get("description"),
        gemini_store_name=project.get("gemini_store_name"),
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
            gemini_store_name=p.get("gemini_store_name"),
            created_at=p["created_at"],
            updated_at=p["updated_at"],
        )
        for p in response.data
    ]
