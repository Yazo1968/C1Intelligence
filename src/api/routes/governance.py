"""
C1 — Governance Endpoints
Trigger governance establishment, retrieve event log, manage events.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from src.clients import get_supabase_client
from src.logging_config import get_logger
from src.api.auth import AuthenticatedUser
from src.api.errors import error_response
from src.api.schemas import (
    ConfirmPartiesRequest,
    GovernanceEventCreateRequest,
    GovernanceEventResponse,
    GovernanceEventUpdateRequest,
    GovernancePartyResponse,
    GovernancePartyUpdateRequest,
    GovernanceRunRequest,
    GovernanceRunResponse,
    GovernanceStatusResponse,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/projects/{project_id}/governance", tags=["governance"])


def _verify_project_access(supabase, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
    """Raise 404 if the project does not exist or does not belong to the user."""
    try:
        supabase.table("projects").select("id").eq(
            "id", str(project_id)
        ).eq("owner_id", str(user_id)).single().execute()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied.",
        )


@router.post("/run", response_model=GovernanceRunResponse, status_code=status.HTTP_202_ACCEPTED)
async def run_governance(
    project_id: uuid.UUID,
    body: GovernanceRunRequest,
    user_id: AuthenticatedUser,
    background_tasks: BackgroundTasks,
) -> GovernanceRunResponse:
    """
    Trigger governance establishment or incremental refresh for a project.
    Creates a governance_run_log entry and returns its ID.
    The Compliance SME processes the run asynchronously.
    """
    supabase = get_supabase_client()
    _verify_project_access(supabase, project_id, user_id)

    now = datetime.now(timezone.utc)

    try:
        response = (
            supabase.table("governance_run_log")
            .insert({
                "project_id": str(project_id),
                "run_type": body.run_type,
                "triggered_at": now.isoformat(),
                "status": "running",
            })
            .execute()
        )
    except Exception as exc:
        logger.error("governance_run_insert_failed", project_id=str(project_id), error=str(exc))
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="GOVERNANCE_RUN_FAILED",
            message=f"Failed to create governance run: {exc}",
        )

    run = response.data[0]

    # Launch Phase 1 in background
    from src.agents.governance_runner import run_party_identification
    background_tasks.add_task(
        run_party_identification,
        str(project_id),
        run["id"],
    )

    logger.info(
        "governance_run_triggered",
        project_id=str(project_id),
        run_id=run["id"],
        run_type=body.run_type,
    )

    return GovernanceRunResponse(
        run_id=uuid.UUID(run["id"]),
        project_id=project_id,
        run_type=run["run_type"],
        status=run["status"],
        triggered_at=run["triggered_at"],
    )


@router.get("/status", response_model=GovernanceStatusResponse)
async def get_governance_status(
    project_id: uuid.UUID,
    user_id: AuthenticatedUser,
) -> GovernanceStatusResponse:
    """
    Return the governance readiness state for a project.
    States: not_established | established | stale
    """
    supabase = get_supabase_client()
    _verify_project_access(supabase, project_id, user_id)

    # Get the most recent completed run
    try:
        run_result = (
            supabase.table("governance_run_log")
            .select("id, triggered_at, status")
            .eq("project_id", str(project_id))
            .eq("status", "complete")
            .order("triggered_at", desc=True)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        logger.error("governance_status_run_fetch_failed", project_id=str(project_id), error=str(exc))
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="GOVERNANCE_STATUS_FAILED",
            message=f"Failed to retrieve governance status: {exc}",
        )

    if not run_result.data:
        # Check for parties_identified run (Phase 1 complete, awaiting confirmation)
        try:
            parties_run_result = (
                supabase.table("governance_run_log")
                .select("id, triggered_at")
                .eq("project_id", str(project_id))
                .eq("status", "parties_identified")
                .order("triggered_at", desc=True)
                .limit(1)
                .execute()
            )
        except Exception:
            parties_run_result = None

        if parties_run_result and parties_run_result.data:
            # Count parties extracted so far
            try:
                parties_count_result = (
                    supabase.table("governance_parties")
                    .select("id", count="exact")
                    .eq("project_id", str(project_id))
                    .execute()
                )
                parties_count = parties_count_result.count or 0
            except Exception:
                parties_count = 0

            return GovernanceStatusResponse(
                project_id=project_id,
                status="parties_identified",
                last_run_at=parties_run_result.data[0]["triggered_at"],
                last_run_id=uuid.UUID(parties_run_result.data[0]["id"]),
                events_confirmed=0,
                events_flagged=0,
                events_inferred=0,
                parties_count=parties_count,
            )

        # Check for in-progress or failed run
        try:
            latest_run_result = (
                supabase.table("governance_run_log")
                .select("id, status, triggered_at")
                .eq("project_id", str(project_id))
                .order("triggered_at", desc=True)
                .limit(1)
                .execute()
            )
        except Exception:
            latest_run_result = None

        if latest_run_result and latest_run_result.data:
            latest = latest_run_result.data[0]
            if latest["status"] == "running":
                return GovernanceStatusResponse(
                    project_id=project_id,
                    status="processing",
                    last_run_at=latest["triggered_at"],
                    last_run_id=uuid.UUID(latest["id"]),
                    events_confirmed=0,
                    events_flagged=0,
                    events_inferred=0,
                    parties_count=0,
                )
            if latest["status"] == "failed":
                return GovernanceStatusResponse(
                    project_id=project_id,
                    status="failed",
                    last_run_at=latest["triggered_at"],
                    last_run_id=uuid.UUID(latest["id"]),
                    events_confirmed=0,
                    events_flagged=0,
                    events_inferred=0,
                    parties_count=0,
                )

        return GovernanceStatusResponse(
            project_id=project_id,
            status="not_established",
            last_run_at=None,
            last_run_id=None,
            events_confirmed=0,
            events_flagged=0,
            events_inferred=0,
            parties_count=0,
        )

    last_run = run_result.data[0]
    last_run_at = last_run["triggered_at"]
    last_run_id = uuid.UUID(last_run["id"])

    # Count events by extraction_status
    try:
        events_result = (
            supabase.table("governance_events")
            .select("extraction_status")
            .eq("project_id", str(project_id))
            .execute()
        )
    except Exception as exc:
        logger.error("governance_status_events_fetch_failed", project_id=str(project_id), error=str(exc))
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="GOVERNANCE_STATUS_FAILED",
            message=f"Failed to retrieve event counts: {exc}",
        )

    counts = {"confirmed": 0, "flagged": 0, "inferred": 0}
    for row in events_result.data:
        s = row.get("extraction_status", "inferred")
        if s in counts:
            counts[s] += 1

    # Check for documents ingested after the last run — if so, status is stale
    try:
        docs_result = (
            supabase.table("documents")
            .select("id")
            .eq("project_id", str(project_id))
            .gt("created_at", last_run_at)
            .limit(1)
            .execute()
        )
        governance_status = "stale" if docs_result.data else "established"
    except Exception:
        governance_status = "established"

    return GovernanceStatusResponse(
        project_id=project_id,
        status=governance_status,
        last_run_at=last_run_at,
        last_run_id=last_run_id,
        events_confirmed=counts["confirmed"],
        events_flagged=counts["flagged"],
        events_inferred=counts["inferred"],
    )


@router.get("/events", response_model=list[GovernanceEventResponse])
async def list_governance_events(
    project_id: uuid.UUID,
    user_id: AuthenticatedUser,
) -> list[GovernanceEventResponse]:
    """Return all governance events for a project ordered by effective date."""
    supabase = get_supabase_client()
    _verify_project_access(supabase, project_id, user_id)

    try:
        response = (
            supabase.table("governance_events")
            .select("*")
            .eq("project_id", str(project_id))
            .order("effective_date", desc=False)
            .execute()
        )
    except Exception as exc:
        logger.error("governance_events_fetch_failed", project_id=str(project_id), error=str(exc))
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="GOVERNANCE_EVENTS_FAILED",
            message=f"Failed to retrieve governance events: {exc}",
        )

    return [
        GovernanceEventResponse(
            id=uuid.UUID(row["id"]),
            project_id=uuid.UUID(row["project_id"]),
            event_type=row["event_type"],
            effective_date=row["effective_date"],
            end_date=row.get("end_date"),
            party_id=uuid.UUID(row["party_id"]),
            role=row["role"],
            appointed_by_party_id=(
                uuid.UUID(row["appointed_by_party_id"])
                if row.get("appointed_by_party_id") else None
            ),
            authority_dimension=row["authority_dimension"],
            contract_source=row.get("contract_source"),
            scope=row.get("scope"),
            terminus_node=row["terminus_node"],
            source_document_id=(
                uuid.UUID(row["source_document_id"])
                if row.get("source_document_id") else None
            ),
            extraction_status=row["extraction_status"],
            created_at=row["created_at"],
        )
        for row in response.data
    ]


@router.patch("/events/{event_id}", response_model=GovernanceEventResponse)
async def update_governance_event(
    project_id: uuid.UUID,
    event_id: uuid.UUID,
    body: GovernanceEventUpdateRequest,
    user_id: AuthenticatedUser,
) -> GovernanceEventResponse:
    """
    Confirm, correct, or flag a governance event.
    Only fields provided in the request body are updated.
    """
    supabase = get_supabase_client()
    _verify_project_access(supabase, project_id, user_id)

    # Build update payload from only the fields that were provided
    updates: dict = {}
    if body.extraction_status is not None:
        updates["extraction_status"] = body.extraction_status
    if body.role is not None:
        updates["role"] = body.role
    if body.effective_date is not None:
        updates["effective_date"] = body.effective_date.isoformat()
    if body.end_date is not None:
        updates["end_date"] = body.end_date.isoformat()
    if body.scope is not None:
        updates["scope"] = body.scope
    if body.contract_source is not None:
        updates["contract_source"] = body.contract_source

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update.",
        )

    try:
        response = (
            supabase.table("governance_events")
            .update(updates)
            .eq("id", str(event_id))
            .eq("project_id", str(project_id))
            .execute()
        )
    except Exception as exc:
        logger.error("governance_event_update_failed", event_id=str(event_id), error=str(exc))
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="GOVERNANCE_EVENT_UPDATE_FAILED",
            message=f"Failed to update governance event: {exc}",
        )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Governance event not found.",
        )

    row = response.data[0]

    logger.info(
        "governance_event_updated",
        event_id=str(event_id),
        extraction_status=row["extraction_status"],
    )

    return GovernanceEventResponse(
        id=uuid.UUID(row["id"]),
        project_id=uuid.UUID(row["project_id"]),
        event_type=row["event_type"],
        effective_date=row["effective_date"],
        end_date=row.get("end_date"),
        party_id=uuid.UUID(row["party_id"]),
        role=row["role"],
        appointed_by_party_id=(
            uuid.UUID(row["appointed_by_party_id"])
            if row.get("appointed_by_party_id") else None
        ),
        authority_dimension=row["authority_dimension"],
        contract_source=row.get("contract_source"),
        scope=row.get("scope"),
        terminus_node=row["terminus_node"],
        source_document_id=(
            uuid.UUID(row["source_document_id"])
            if row.get("source_document_id") else None
        ),
        extraction_status=row["extraction_status"],
        created_at=row["created_at"],
    )


@router.post("/events", response_model=GovernanceEventResponse, status_code=status.HTTP_201_CREATED)
async def create_governance_event(
    project_id: uuid.UUID,
    body: GovernanceEventCreateRequest,
    user_id: AuthenticatedUser,
) -> GovernanceEventResponse:
    """
    Manually add a governance event not extracted by the Compliance SME.
    Always created with extraction_status = confirmed unless overridden.
    """
    supabase = get_supabase_client()
    _verify_project_access(supabase, project_id, user_id)

    try:
        response = (
            supabase.table("governance_events")
            .insert({
                "project_id": str(project_id),
                "event_type": body.event_type,
                "effective_date": body.effective_date.isoformat(),
                "end_date": body.end_date.isoformat() if body.end_date else None,
                "party_id": str(body.party_id),
                "role": body.role,
                "appointed_by_party_id": (
                    str(body.appointed_by_party_id) if body.appointed_by_party_id else None
                ),
                "authority_dimension": body.authority_dimension,
                "contract_source": body.contract_source,
                "scope": body.scope,
                "terminus_node": body.terminus_node,
                "source_document_id": (
                    str(body.source_document_id) if body.source_document_id else None
                ),
                "extraction_status": body.extraction_status,
            })
            .execute()
        )
    except Exception as exc:
        logger.error("governance_event_create_failed", project_id=str(project_id), error=str(exc))
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="GOVERNANCE_EVENT_CREATE_FAILED",
            message=f"Failed to create governance event: {exc}",
        )

    row = response.data[0]

    logger.info(
        "governance_event_created",
        project_id=str(project_id),
        event_id=row["id"],
        event_type=row["event_type"],
    )

    return GovernanceEventResponse(
        id=uuid.UUID(row["id"]),
        project_id=uuid.UUID(row["project_id"]),
        event_type=row["event_type"],
        effective_date=row["effective_date"],
        end_date=row.get("end_date"),
        party_id=uuid.UUID(row["party_id"]),
        role=row["role"],
        appointed_by_party_id=(
            uuid.UUID(row["appointed_by_party_id"])
            if row.get("appointed_by_party_id") else None
        ),
        authority_dimension=row["authority_dimension"],
        contract_source=row.get("contract_source"),
        scope=row.get("scope"),
        terminus_node=row["terminus_node"],
        source_document_id=(
            uuid.UUID(row["source_document_id"])
            if row.get("source_document_id") else None
        ),
        extraction_status=row["extraction_status"],
        created_at=row["created_at"],
    )


@router.get("/parties", response_model=list[GovernancePartyResponse])
async def list_governance_parties(
    project_id: uuid.UUID,
    user_id: AuthenticatedUser,
) -> list[GovernancePartyResponse]:
    """Return all governance parties (entity registry) for a project."""
    supabase = get_supabase_client()
    _verify_project_access(supabase, project_id, user_id)

    try:
        response = (
            supabase.table("governance_parties")
            .select("*")
            .eq("project_id", str(project_id))
            .order("entity_type", desc=False)
            .order("canonical_name", desc=False)
            .execute()
        )
    except Exception as exc:
        logger.error("governance_parties_fetch_failed", project_id=str(project_id), error=str(exc))
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="GOVERNANCE_PARTIES_FAILED",
            message=f"Failed to retrieve governance parties: {exc}",
        )

    return [
        GovernancePartyResponse(
            id=uuid.UUID(row["id"]),
            project_id=uuid.UUID(row["project_id"]),
            entity_type=row["entity_type"],
            canonical_name=row["canonical_name"],
            aliases=row.get("aliases") or [],
            contractual_role=row.get("contractual_role"),
            terminus_node=row["terminus_node"],
            confirmation_status=row["confirmation_status"],
            created_at=row["created_at"],
        )
        for row in response.data
    ]


@router.patch("/parties/{party_id}", response_model=GovernancePartyResponse)
async def update_governance_party(
    project_id: uuid.UUID,
    party_id: uuid.UUID,
    body: GovernancePartyUpdateRequest,
    user_id: AuthenticatedUser,
) -> GovernancePartyResponse:
    """Confirm or flag a governance party in the entity registry."""
    supabase = get_supabase_client()
    _verify_project_access(supabase, project_id, user_id)

    updates: dict = {}
    if body.confirmation_status is not None:
        valid = {"confirmed", "flagged", "inferred"}
        if body.confirmation_status not in valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"confirmation_status must be one of: {valid}",
            )
        updates["confirmation_status"] = body.confirmation_status

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update.",
        )

    try:
        response = (
            supabase.table("governance_parties")
            .update(updates)
            .eq("id", str(party_id))
            .eq("project_id", str(project_id))
            .execute()
        )
    except Exception as exc:
        logger.error("governance_party_update_failed", party_id=str(party_id), error=str(exc))
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="GOVERNANCE_PARTY_UPDATE_FAILED",
            message=f"Failed to update governance party: {exc}",
        )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Governance party not found.",
        )

    row = response.data[0]
    return GovernancePartyResponse(
        id=uuid.UUID(row["id"]),
        project_id=uuid.UUID(row["project_id"]),
        entity_type=row["entity_type"],
        canonical_name=row["canonical_name"],
        aliases=row.get("aliases") or [],
        contractual_role=row.get("contractual_role"),
        terminus_node=row["terminus_node"],
        confirmation_status=row["confirmation_status"],
        created_at=row["created_at"],
    )


@router.post("/confirm-parties", response_model=GovernanceRunResponse,
             status_code=status.HTTP_202_ACCEPTED)
async def confirm_parties(
    project_id: uuid.UUID,
    body: ConfirmPartiesRequest,
    user_id: AuthenticatedUser,
    background_tasks: BackgroundTasks,
) -> GovernanceRunResponse:
    """
    Confirm the entity registry and trigger Phase 2 governance establishment.
    Requires at least one confirmed party to proceed.
    """
    from src.agents.governance_runner import run_governance_establishment

    supabase = get_supabase_client()
    _verify_project_access(supabase, project_id, user_id)

    # Verify at least one confirmed party exists
    try:
        confirmed_result = (
            supabase.table("governance_parties")
            .select("id", count="exact")
            .eq("project_id", str(project_id))
            .eq("confirmation_status", "confirmed")
            .execute()
        )
        confirmed_count = confirmed_result.count or 0
    except Exception as exc:
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="GOVERNANCE_CONFIRM_FAILED",
            message=f"Failed to check confirmed parties: {exc}",
        )

    if confirmed_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No confirmed parties. Confirm at least one party before establishing governance.",
        )

    now = datetime.now(timezone.utc)

    try:
        response = (
            supabase.table("governance_run_log")
            .insert({
                "project_id": str(project_id),
                "run_type": "full",
                "triggered_at": now.isoformat(),
                "status": "running",
                "phase": 2,
            })
            .execute()
        )
    except Exception as exc:
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="GOVERNANCE_RUN_FAILED",
            message=f"Failed to create Phase 2 run: {exc}",
        )

    run = response.data[0]

    background_tasks.add_task(
        run_governance_establishment,
        str(project_id),
        run["id"],
    )

    logger.info(
        "governance_phase2_triggered",
        project_id=str(project_id),
        run_id=run["id"],
        confirmed_parties=confirmed_count,
    )

    return GovernanceRunResponse(
        run_id=uuid.UUID(run["id"]),
        project_id=project_id,
        run_type=run["run_type"],
        status=run["status"],
        triggered_at=run["triggered_at"],
    )
