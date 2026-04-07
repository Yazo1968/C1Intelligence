"""
C1 — Governance API Routes
Function 1: Entity Directory (7 endpoints)
All routes under /projects/{project_id}/governance/
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from src.api.auth import AuthenticatedUser
from src.api.errors import error_response
from src.api.schemas import (
    EntityDirectoryRunResponse,
    EntityResponse,
    EntityDiscrepancyResponse,
    PatchEntityRequest,
    ResolveDiscrepancyRequest,
)
from src.agents.governance.entity_extractor import run_entity_extraction
from src.agents.governance.consolidator import consolidate
from src.clients import get_supabase_client
from src.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/projects/{project_id}/governance",
    tags=["governance"],
)


# ---------------------------------------------------------------------------
# Helper — verify project exists and belongs to user
# ---------------------------------------------------------------------------

def _require_project(project_id: str, user_id: uuid.UUID) -> None:
    supabase = get_supabase_client()
    resp = (
        supabase.table("projects")
        .select("id")
        .eq("id", project_id)
        .eq("owner_id", str(user_id))
        .maybe_single()
        .execute()
    )
    if not resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "PROJECT_NOT_FOUND",
                    "message": "Project not found."},
        )


# ---------------------------------------------------------------------------
# Background task — runs extraction + consolidation, writes to DB
# ---------------------------------------------------------------------------

def _run_extraction_background(project_id: str, run_id_placeholder: str) -> None:
    """
    Called via BackgroundTasks. Runs entity extraction and consolidation,
    then writes entities and discrepancies to Supabase and sets run status
    to awaiting_confirmation.
    """
    supabase = get_supabase_client()
    try:
        # 1. Extract
        extraction = run_entity_extraction(project_id)

        if extraction.error:
            # run record already marked failed inside run_entity_extraction
            return

        run_id = extraction.run_id

        # 2. Consolidate
        directory = consolidate(extraction)

        # 3. Write entities
        entity_rows = []
        for org in directory.organisations:
            entity_rows.append({
                "project_id": project_id,
                "run_id": run_id,
                "entity_type": "organisation",
                "canonical_name": org.canonical_name,
                "name_variants": org.name_variants,
                "confirmation_status": "proposed",
            })
        for ind in directory.individuals:
            entity_rows.append({
                "project_id": project_id,
                "run_id": run_id,
                "entity_type": "individual",
                "canonical_name": ind.canonical_name,
                "name_variants": ind.name_variants,
                "title": ind.title,
                "confirmation_status": "proposed",
            })
        if entity_rows:
            supabase.table("entities").insert(entity_rows).execute()

        # 4. Write discrepancies
        disc_rows = []
        for disc in directory.discrepancies:
            disc_rows.append({
                "project_id": project_id,
                "run_id": run_id,
                "discrepancy_type": disc.discrepancy_type,
                "description": disc.description,
                "name_a": disc.name_a,
                "name_b": disc.name_b,
                "chunk_references": [],
            })
        if disc_rows:
            supabase.table("entity_discrepancies").insert(disc_rows).execute()

        # 5. Update run to awaiting_confirmation
        org_count = len(directory.organisations)
        ind_count = len(directory.individuals)
        supabase.table("entity_directory_runs").update({
            "status": "awaiting_confirmation",
            "organisations_found": org_count,
            "individuals_found": ind_count,
        }).eq("id", run_id).execute()

        logger.info(
            "Entity extraction complete: project=%s run=%s orgs=%d individuals=%d",
            project_id, run_id, org_count, ind_count,
        )

    except Exception as exc:  # noqa: BLE001
        logger.exception("Background extraction failed: project=%s", project_id)
        # Best-effort: mark any running run as failed
        try:
            supabase.table("entity_directory_runs").update({
                "status": "failed",
                "error_message": str(exc),
            }).eq("project_id", project_id).eq("status", "running").execute()
        except Exception:  # noqa: BLE001
            pass


# ---------------------------------------------------------------------------
# POST /directory/run — trigger extraction
# ---------------------------------------------------------------------------

@router.post(
    "/directory/run",
    response_model=EntityDirectoryRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_directory_run(
    project_id: str,
    background_tasks: BackgroundTasks,
    user_id: AuthenticatedUser,
) -> EntityDirectoryRunResponse:
    _require_project(project_id, user_id)
    supabase = get_supabase_client()

    # Create a placeholder run record immediately so frontend can poll
    run_resp = (
        supabase.table("entity_directory_runs")
        .insert({
            "project_id": project_id,
            "status": "running",
            "total_chunks": 0,
            "chunks_processed": 0,
        })
        .execute()
    )
    run = run_resp.data[0]

    # Schedule background work
    background_tasks.add_task(
        _run_extraction_background, project_id, run["id"]
    )

    return EntityDirectoryRunResponse(**run)


# ---------------------------------------------------------------------------
# GET /directory/status — poll run progress
# ---------------------------------------------------------------------------

@router.get(
    "/directory/status",
    response_model=EntityDirectoryRunResponse,
)
async def get_directory_status(
    project_id: str,
    user_id: AuthenticatedUser,
) -> EntityDirectoryRunResponse:
    _require_project(project_id, user_id)
    supabase = get_supabase_client()

    resp = (
        supabase.table("entity_directory_runs")
        .select("*")
        .eq("project_id", project_id)
        .order("triggered_at", desc=True)
        .limit(1)
        .maybe_single()
        .execute()
    )
    if not resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NO_RUN_FOUND",
                    "message": "No directory run found for this project."},
        )
    return EntityDirectoryRunResponse(**resp.data)


# ---------------------------------------------------------------------------
# GET /directory/entities — list proposed entities
# ---------------------------------------------------------------------------

@router.get(
    "/directory/entities",
    response_model=list[EntityResponse],
)
async def list_entities(
    project_id: str,
    user_id: AuthenticatedUser,
) -> list[EntityResponse]:
    _require_project(project_id, user_id)
    supabase = get_supabase_client()

    # Get latest run id
    run_resp = (
        supabase.table("entity_directory_runs")
        .select("id")
        .eq("project_id", project_id)
        .order("triggered_at", desc=True)
        .limit(1)
        .maybe_single()
        .execute()
    )
    if not run_resp.data:
        return []

    run_id = run_resp.data["id"]
    resp = (
        supabase.table("entities")
        .select("*")
        .eq("project_id", project_id)
        .eq("run_id", run_id)
        .order("entity_type")
        .order("canonical_name")
        .execute()
    )
    return [EntityResponse(**row) for row in (resp.data or [])]


# ---------------------------------------------------------------------------
# GET /directory/discrepancies — list unresolved discrepancies
# ---------------------------------------------------------------------------

@router.get(
    "/directory/discrepancies",
    response_model=list[EntityDiscrepancyResponse],
)
async def list_discrepancies(
    project_id: str,
    user_id: AuthenticatedUser,
) -> list[EntityDiscrepancyResponse]:
    _require_project(project_id, user_id)
    supabase = get_supabase_client()

    run_resp = (
        supabase.table("entity_directory_runs")
        .select("id")
        .eq("project_id", project_id)
        .order("triggered_at", desc=True)
        .limit(1)
        .maybe_single()
        .execute()
    )
    if not run_resp.data:
        return []

    run_id = run_resp.data["id"]
    resp = (
        supabase.table("entity_discrepancies")
        .select("*")
        .eq("project_id", project_id)
        .eq("run_id", run_id)
        .is_("resolution", "null")
        .execute()
    )
    return [EntityDiscrepancyResponse(**row) for row in (resp.data or [])]


# ---------------------------------------------------------------------------
# PATCH /directory/entities/{entity_id} — confirm / edit / reject
# ---------------------------------------------------------------------------

@router.patch(
    "/directory/entities/{entity_id}",
    response_model=EntityResponse,
)
async def patch_entity(
    project_id: str,
    entity_id: str,
    body: PatchEntityRequest,
    user_id: AuthenticatedUser,
) -> EntityResponse:
    _require_project(project_id, user_id)
    supabase = get_supabase_client()

    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "NO_FIELDS", "message": "No fields to update."},
        )

    resp = (
        supabase.table("entities")
        .update(updates)
        .eq("id", entity_id)
        .eq("project_id", project_id)
        .execute()
    )
    if not resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "ENTITY_NOT_FOUND", "message": "Entity not found."},
        )
    return EntityResponse(**resp.data[0])


# ---------------------------------------------------------------------------
# POST /directory/discrepancies/{discrepancy_id}/resolve
# ---------------------------------------------------------------------------

@router.post(
    "/directory/discrepancies/{discrepancy_id}/resolve",
    response_model=EntityDiscrepancyResponse,
)
async def resolve_discrepancy(
    project_id: str,
    discrepancy_id: str,
    body: ResolveDiscrepancyRequest,
    user_id: AuthenticatedUser,
) -> EntityDiscrepancyResponse:
    _require_project(project_id, user_id)
    supabase = get_supabase_client()

    updates: dict = {
        "resolution": body.resolution,
        "user_note": body.user_note,
    }
    if body.resolved_canonical:
        updates["resolved_canonical"] = body.resolved_canonical

    resp = (
        supabase.table("entity_discrepancies")
        .update(updates)
        .eq("id", discrepancy_id)
        .eq("project_id", project_id)
        .execute()
    )
    if not resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "DISCREPANCY_NOT_FOUND",
                    "message": "Discrepancy not found."},
        )
    return EntityDiscrepancyResponse(**resp.data[0])


# ---------------------------------------------------------------------------
# POST /directory/confirm — lock the directory
# ---------------------------------------------------------------------------

@router.post(
    "/directory/confirm",
    response_model=EntityDirectoryRunResponse,
)
async def confirm_directory(
    project_id: str,
    user_id: AuthenticatedUser,
) -> EntityDirectoryRunResponse:
    _require_project(project_id, user_id)
    supabase = get_supabase_client()

    # Guard: unresolved discrepancies must all be resolved first
    run_resp = (
        supabase.table("entity_directory_runs")
        .select("id")
        .eq("project_id", project_id)
        .order("triggered_at", desc=True)
        .limit(1)
        .maybe_single()
        .execute()
    )
    if not run_resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NO_RUN_FOUND",
                    "message": "No directory run found."},
        )
    run_id = run_resp.data["id"]

    unresolved = (
        supabase.table("entity_discrepancies")
        .select("id", count="exact")
        .eq("project_id", project_id)
        .eq("run_id", run_id)
        .is_("resolution", "null")
        .execute()
    )
    if unresolved.count and unresolved.count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error_code": "UNRESOLVED_DISCREPANCIES",
                    "message": f"{unresolved.count} discrepancies must be resolved before confirming."},
        )

    # Guard: at least one confirmed entity
    confirmed = (
        supabase.table("entities")
        .select("id", count="exact")
        .eq("project_id", project_id)
        .eq("run_id", run_id)
        .eq("confirmation_status", "confirmed")
        .execute()
    )
    if not confirmed.count or confirmed.count == 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error_code": "NO_CONFIRMED_ENTITIES",
                    "message": "At least one entity must be confirmed before locking the directory."},
        )

    import datetime
    resp = (
        supabase.table("entity_directory_runs")
        .update({
            "status": "confirmed",
            "completed_at": datetime.datetime.utcnow().isoformat(),
        })
        .eq("id", run_id)
        .execute()
    )
    return EntityDirectoryRunResponse(**resp.data[0])
