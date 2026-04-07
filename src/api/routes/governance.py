"""
C1 — Governance API Routes
Function 1: Entity Directory (7 endpoints)
All routes under /projects/{project_id}/governance/
"""

from __future__ import annotations

import datetime
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
    EventLogRunResponse,
    EntityEventResponse,
    EventLogQuestionResponse,
    PatchEventRequest,
    AnswerQuestionRequest,
)
from src.agents.governance.entity_extractor import run_entity_extraction
from src.agents.governance.event_extractor import (
    run_event_extraction,
    EntityInput,
)
from src.agents.governance.consolidator import (
    consolidate,
    consolidate_from_db,
    consolidate_events,
)
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

def _run_extraction_background(project_id: str, run_id: str) -> None:
    """
    Two-stage background task:
      Stage 1 (extracting): run_entity_extraction writes batches to
        entity_raw_extractions progressively. run record status = 'extracting'.
      Stage 2 (consolidating): consolidate_from_db reads staging table,
        groups variants, detects discrepancies, writes to entities +
        entity_discrepancies. run record status = 'consolidating'.
    On completion: status flips to 'awaiting_confirmation'.
    """
    supabase = get_supabase_client()
    try:
        # ── Stage 1: Extract ────────────────────────────────────────────────
        extraction = run_entity_extraction(project_id, run_id)

        if extraction.error:
            # extractor already marked run as failed
            return

        # ── Stage 2: Consolidate ────────────────────────────────────────────
        supabase.table("entity_directory_runs").update({
            "status": "consolidating",
        }).eq("id", run_id).execute()

        directory = consolidate_from_db(project_id, run_id)

        # Write consolidated entities
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

        # Write discrepancies
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

        # Flip to awaiting_confirmation
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
        logger.exception("Background extraction failed: project=%s run=%s", project_id, run_id)
        try:
            supabase.table("entity_directory_runs").update({
                "status": "failed",
                "error_message": str(exc),
            }).eq("id", run_id).eq("status", "consolidating").execute()
            # Also cover extracting state in case failure was in Stage 1
            supabase.table("entity_directory_runs").update({
                "status": "failed",
                "error_message": str(exc),
            }).eq("id", run_id).eq("status", "extracting").execute()
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
            "status": "extracting",
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


# ===========================================================================
# Function 2 — Event Log
# ===========================================================================

# ---------------------------------------------------------------------------
# Background task — event extraction + consolidation + DB writes
# ---------------------------------------------------------------------------

def _run_event_extraction_background(
    project_id: str,
    entity_id: str,
    run_id: str,
) -> None:
    supabase = get_supabase_client()
    try:
        # Fetch entity record for name and variants
        entity_resp = (
            supabase.table("entities")
            .select("canonical_name, name_variants")
            .eq("id", entity_id)
            .eq("project_id", project_id)
            .maybe_single()
            .execute()
        )
        if not entity_resp.data:
            supabase.table("event_log_runs").update({
                "status": "failed",
                "error_message": "Entity record not found.",
            }).eq("id", run_id).execute()
            return

        entity_data = entity_resp.data
        entity_input = EntityInput(
            entity_id=entity_id,
            project_id=project_id,
            canonical_name=entity_data["canonical_name"],
            name_variants=entity_data.get("name_variants") or [],
        )

        # Extract
        extraction = run_event_extraction(entity_input)

        # Update chunks_scanned
        supabase.table("event_log_runs").update({
            "chunks_scanned": extraction.chunks_scanned,
        }).eq("id", run_id).execute()

        if extraction.error:
            supabase.table("event_log_runs").update({
                "status": "failed",
                "error_message": extraction.error,
            }).eq("id", run_id).execute()
            return

        # Consolidate
        event_log = consolidate_events(extraction.raw_events)

        # Write events
        event_rows = []
        for event in event_log.events:
            event_rows.append({
                "project_id": project_id,
                "entity_id": entity_id,
                "run_id": run_id,
                "event_type": event.event_type,
                "event_date": event.event_date,
                "event_date_certain": event.event_date_certain,
                "status_before": event.status_before,
                "status_after": event.status_after,
                "initiated_by": event.initiated_by,
                "authorised_by": event.authorised_by,
                "source_document": event.source_document,
                "source_excerpt": event.source_excerpt,
                "confirmation_status": "proposed",
                "sequence_number": event.sequence_number,
            })

        inserted_event_ids: list[str] = []
        if event_rows:
            inserted = supabase.table("entity_events").insert(event_rows).execute()
            inserted_event_ids = [row["id"] for row in (inserted.data or [])]

        # Write questions — map event_indices to real inserted event IDs
        question_rows = []
        for question in event_log.questions:
            referenced_ids = [
                inserted_event_ids[i]
                for i in question.event_indices
                if i < len(inserted_event_ids)
            ]
            question_rows.append({
                "project_id": project_id,
                "run_id": run_id,
                "entity_id": entity_id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "events_referenced": referenced_ids,
                "sequence_number": len(question_rows),
            })
        if question_rows:
            supabase.table("event_log_questions").insert(question_rows).execute()

        # Update run to awaiting_confirmation
        supabase.table("event_log_runs").update({
            "status": "awaiting_confirmation",
            "events_extracted": len(event_rows),
            "completed_at": datetime.datetime.utcnow().isoformat(),
        }).eq("id", run_id).execute()

        logger.info(
            "Event extraction complete: entity=%s run=%s events=%d questions=%d",
            entity_id, run_id, len(event_rows), len(question_rows),
        )

    except Exception as exc:  # noqa: BLE001
        logger.exception(
            "Background event extraction failed: entity=%s run=%s", entity_id, run_id
        )
        try:
            supabase.table("event_log_runs").update({
                "status": "failed",
                "error_message": str(exc),
            }).eq("id", run_id).execute()
        except Exception:  # noqa: BLE001
            pass


# ---------------------------------------------------------------------------
# Helper — require entity belongs to project and is confirmed
# ---------------------------------------------------------------------------

def _require_entity(project_id: str, entity_id: str) -> None:
    supabase = get_supabase_client()
    resp = (
        supabase.table("entities")
        .select("id, confirmation_status")
        .eq("id", entity_id)
        .eq("project_id", project_id)
        .maybe_single()
        .execute()
    )
    if not resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "ENTITY_NOT_FOUND", "message": "Entity not found."},
        )
    if resp.data["confirmation_status"] != "confirmed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": "ENTITY_NOT_CONFIRMED",
                "message": "Entity must be confirmed before running event extraction.",
            },
        )


# ---------------------------------------------------------------------------
# POST /entities/{entity_id}/events/run
# ---------------------------------------------------------------------------

@router.post(
    "/entities/{entity_id}/events/run",
    response_model=EventLogRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_event_run(
    project_id: str,
    entity_id: str,
    background_tasks: BackgroundTasks,
    user_id: AuthenticatedUser,
) -> EventLogRunResponse:
    _require_project(project_id, user_id)
    _require_entity(project_id, entity_id)
    supabase = get_supabase_client()

    run_resp = (
        supabase.table("event_log_runs")
        .insert({
            "project_id": project_id,
            "entity_id": entity_id,
            "status": "running",
            "chunks_scanned": 0,
            "events_extracted": 0,
        })
        .execute()
    )
    run = run_resp.data[0]

    background_tasks.add_task(
        _run_event_extraction_background, project_id, entity_id, run["id"]
    )
    return EventLogRunResponse(**run)


# ---------------------------------------------------------------------------
# GET /entities/{entity_id}/events/status
# ---------------------------------------------------------------------------

@router.get(
    "/entities/{entity_id}/events/status",
    response_model=EventLogRunResponse,
)
async def get_event_run_status(
    project_id: str,
    entity_id: str,
    user_id: AuthenticatedUser,
) -> EventLogRunResponse:
    _require_project(project_id, user_id)
    supabase = get_supabase_client()

    resp = (
        supabase.table("event_log_runs")
        .select("*")
        .eq("project_id", project_id)
        .eq("entity_id", entity_id)
        .order("triggered_at", desc=True)
        .limit(1)
        .maybe_single()
        .execute()
    )
    if not resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NO_RUN_FOUND",
                    "message": "No event log run found for this entity."},
        )
    return EventLogRunResponse(**resp.data)


# ---------------------------------------------------------------------------
# GET /entities/{entity_id}/events
# ---------------------------------------------------------------------------

@router.get(
    "/entities/{entity_id}/events",
    response_model=list[EntityEventResponse],
)
async def list_events(
    project_id: str,
    entity_id: str,
    user_id: AuthenticatedUser,
) -> list[EntityEventResponse]:
    _require_project(project_id, user_id)
    supabase = get_supabase_client()

    run_resp = (
        supabase.table("event_log_runs")
        .select("id")
        .eq("project_id", project_id)
        .eq("entity_id", entity_id)
        .order("triggered_at", desc=True)
        .limit(1)
        .maybe_single()
        .execute()
    )
    if not run_resp.data:
        return []

    run_id = run_resp.data["id"]
    resp = (
        supabase.table("entity_events")
        .select("*")
        .eq("project_id", project_id)
        .eq("entity_id", entity_id)
        .eq("run_id", run_id)
        .order("sequence_number")
        .execute()
    )
    return [EntityEventResponse(**row) for row in (resp.data or [])]


# ---------------------------------------------------------------------------
# GET /entities/{entity_id}/events/questions
# ---------------------------------------------------------------------------

@router.get(
    "/entities/{entity_id}/events/questions",
    response_model=list[EventLogQuestionResponse],
)
async def list_event_questions(
    project_id: str,
    entity_id: str,
    user_id: AuthenticatedUser,
) -> list[EventLogQuestionResponse]:
    _require_project(project_id, user_id)
    supabase = get_supabase_client()

    run_resp = (
        supabase.table("event_log_runs")
        .select("id")
        .eq("project_id", project_id)
        .eq("entity_id", entity_id)
        .order("triggered_at", desc=True)
        .limit(1)
        .maybe_single()
        .execute()
    )
    if not run_resp.data:
        return []

    run_id = run_resp.data["id"]
    resp = (
        supabase.table("event_log_questions")
        .select("*")
        .eq("project_id", project_id)
        .eq("run_id", run_id)
        .is_("answer", "null")
        .order("sequence_number")
        .execute()
    )
    return [EventLogQuestionResponse(**row) for row in (resp.data or [])]


# ---------------------------------------------------------------------------
# PATCH /entities/{entity_id}/events/{event_id}
# ---------------------------------------------------------------------------

@router.patch(
    "/entities/{entity_id}/events/{event_id}",
    response_model=EntityEventResponse,
)
async def patch_event(
    project_id: str,
    entity_id: str,
    event_id: str,
    body: PatchEventRequest,
    user_id: AuthenticatedUser,
) -> EntityEventResponse:
    _require_project(project_id, user_id)
    supabase = get_supabase_client()

    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "NO_FIELDS", "message": "No fields to update."},
        )

    resp = (
        supabase.table("entity_events")
        .update(updates)
        .eq("id", event_id)
        .eq("entity_id", entity_id)
        .eq("project_id", project_id)
        .execute()
    )
    if not resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "EVENT_NOT_FOUND", "message": "Event not found."},
        )
    return EntityEventResponse(**resp.data[0])


# ---------------------------------------------------------------------------
# POST /entities/{entity_id}/events/questions/{question_id}/answer
# ---------------------------------------------------------------------------

@router.post(
    "/entities/{entity_id}/events/questions/{question_id}/answer",
    response_model=EventLogQuestionResponse,
)
async def answer_question(
    project_id: str,
    entity_id: str,
    question_id: str,
    body: AnswerQuestionRequest,
    user_id: AuthenticatedUser,
) -> EventLogQuestionResponse:
    _require_project(project_id, user_id)
    supabase = get_supabase_client()

    resp = (
        supabase.table("event_log_questions")
        .update({
            "answer": body.answer,
            "answered_at": datetime.datetime.utcnow().isoformat(),
        })
        .eq("id", question_id)
        .eq("entity_id", entity_id)
        .eq("project_id", project_id)
        .execute()
    )
    if not resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "QUESTION_NOT_FOUND",
                    "message": "Question not found."},
        )
    return EventLogQuestionResponse(**resp.data[0])


# ---------------------------------------------------------------------------
# POST /entities/{entity_id}/events/confirm
# ---------------------------------------------------------------------------

@router.post(
    "/entities/{entity_id}/events/confirm",
    response_model=EventLogRunResponse,
)
async def confirm_event_log(
    project_id: str,
    entity_id: str,
    user_id: AuthenticatedUser,
) -> EventLogRunResponse:
    _require_project(project_id, user_id)
    supabase = get_supabase_client()

    run_resp = (
        supabase.table("event_log_runs")
        .select("id, status")
        .eq("project_id", project_id)
        .eq("entity_id", entity_id)
        .order("triggered_at", desc=True)
        .limit(1)
        .maybe_single()
        .execute()
    )
    if not run_resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NO_RUN_FOUND", "message": "No event log run found."},
        )
    run_id = run_resp.data["id"]

    # Guard: unanswered questions must be resolved first
    unanswered = (
        supabase.table("event_log_questions")
        .select("id", count="exact")
        .eq("project_id", project_id)
        .eq("run_id", run_id)
        .is_("answer", "null")
        .execute()
    )
    if unanswered.count and unanswered.count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": "UNANSWERED_QUESTIONS",
                "message": f"{unanswered.count} questions must be answered before confirming.",
            },
        )

    resp = (
        supabase.table("event_log_runs")
        .update({
            "status": "confirmed",
            "completed_at": datetime.datetime.utcnow().isoformat(),
        })
        .eq("id", run_id)
        .execute()
    )
    return EventLogRunResponse(**resp.data[0])

