"""
C1 — Gemini File Search Store Manager
Manages the one-store-per-project invariant.
"""

from __future__ import annotations

import re
import uuid

from google import genai
from supabase import Client as SupabaseClient

from src.logging_config import get_logger
from src.ingestion.models import IngestionError

logger = get_logger(__name__)


def _sanitize_name(name: str) -> str:
    """Sanitize a project name for use in a Gemini store display name."""
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "-", name.lower())
    return sanitized[:50]


def create_store_for_project(
    gemini_client: genai.Client,
    supabase_client: SupabaseClient,
    project_id: uuid.UUID,
    project_name: str,
) -> str:
    """
    Create a Gemini File Search store for a project.
    Writes the store name to projects.gemini_store_name.
    Returns the Gemini store name (e.g., "fileSearchStores/abc123").
    """
    display_name = f"c1-{project_id}-{_sanitize_name(project_name)}"

    try:
        store = gemini_client.file_search_stores.create(
            config={"display_name": display_name}
        )
    except Exception as exc:
        raise IngestionError(
            stage="store_creation",
            message=f"Failed to create Gemini File Search store: {exc}",
        ) from exc

    store_name = store.name
    logger.info(
        "gemini_store_created",
        project_id=str(project_id),
        store_name=store_name,
        display_name=display_name,
    )

    try:
        supabase_client.table("projects").update(
            {"gemini_store_name": store_name}
        ).eq("id", str(project_id)).execute()
    except Exception as exc:
        # Attempt cleanup: delete the orphaned Gemini store
        try:
            gemini_client.file_search_stores.delete(name=store_name, config={"force": True})
        except Exception:
            logger.error(
                "gemini_store_cleanup_failed",
                store_name=store_name,
                project_id=str(project_id),
            )
        raise IngestionError(
            stage="store_creation",
            message=f"Created Gemini store but failed to update Supabase: {exc}",
        ) from exc

    return store_name


def get_store_name_for_project(
    supabase_client: SupabaseClient,
    project_id: uuid.UUID,
) -> str:
    """
    Read the Gemini store name for a project from Supabase.
    Raises IngestionError if not found or if gemini_store_name is null.
    """
    try:
        response = (
            supabase_client.table("projects")
            .select("gemini_store_name")
            .eq("id", str(project_id))
            .single()
            .execute()
        )
    except Exception as exc:
        raise IngestionError(
            stage="store_lookup",
            message=f"Failed to look up project {project_id}: {exc}",
        ) from exc

    store_name = response.data.get("gemini_store_name")
    if not store_name:
        raise IngestionError(
            stage="store_lookup",
            message=f"Project {project_id} has no Gemini File Search store. Create the store first.",
        )

    return store_name


def delete_store_for_project(
    gemini_client: genai.Client,
    supabase_client: SupabaseClient,
    project_id: uuid.UUID,
) -> None:
    """
    Delete the Gemini store for a project and clear the reference in Supabase.
    Uses force=True to delete even if documents remain.
    """
    store_name = get_store_name_for_project(supabase_client, project_id)

    try:
        gemini_client.file_search_stores.delete(name=store_name, config={"force": True})
    except Exception as exc:
        raise IngestionError(
            stage="store_deletion",
            message=f"Failed to delete Gemini store {store_name}: {exc}",
        ) from exc

    try:
        supabase_client.table("projects").update(
            {"gemini_store_name": None}
        ).eq("id", str(project_id)).execute()
    except Exception as exc:
        logger.error(
            "supabase_store_ref_clear_failed",
            project_id=str(project_id),
            store_name=store_name,
            error=str(exc),
        )
        raise IngestionError(
            stage="store_deletion",
            message=f"Deleted Gemini store but failed to clear Supabase reference: {exc}",
        ) from exc

    logger.info(
        "gemini_store_deleted",
        project_id=str(project_id),
        store_name=store_name,
    )
