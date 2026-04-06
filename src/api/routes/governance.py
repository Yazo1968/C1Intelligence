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
    GovernanceRunRequest,
    GovernanceRunResponse,
    GovernanceStatusResponse,
    InterviewStatusResponse,
    PartyIdentityResponse,
    PartyRoleResponse,
    ReconciliationAnswerRequest,
    ReconciliationQuestionResponse,
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
            # Count party identities extracted so far
            try:
                parties_count_result = (
                    supabase.table("party_identities")
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

    # authority_events counts — populated in Phase 5; stub zeros for now
    counts = {"confirmed": 0, "flagged": 0, "inferred": 0}

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


@router.get("/parties", response_model=list[PartyIdentityResponse])
async def list_party_identities(
    project_id: uuid.UUID,
    user_id: AuthenticatedUser,
) -> list[PartyIdentityResponse]:
    """Return all party identities and their roles for a project."""
    supabase = get_supabase_client()
    _verify_project_access(supabase, project_id, user_id)

    try:
        identities_result = (
            supabase.table("party_identities")
            .select("*")
            .eq("project_id", str(project_id))
            .order("is_internal", desc=True)
            .order("party_category")
            .order("legal_name")
            .execute()
        )
    except Exception as exc:
        logger.error("party_identities_fetch_failed",
                     project_id=str(project_id), error=str(exc))
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="PARTY_IDENTITIES_FAILED",
            message=f"Failed to retrieve party identities: {exc}",
        )

    identities = identities_result.data or []
    if not identities:
        return []

    identity_ids = [row["id"] for row in identities]

    try:
        roles_result = (
            supabase.table("party_roles")
            .select("*")
            .in_("party_identity_id", identity_ids)
            .order("effective_from")
            .execute()
        )
    except Exception as exc:
        logger.error("party_roles_fetch_failed",
                     project_id=str(project_id), error=str(exc))
        roles_result = None

    roles_by_party: dict[str, list] = {}
    for role in (roles_result.data if roles_result else []):
        pid = role["party_identity_id"]
        roles_by_party.setdefault(pid, []).append(role)

    output = []
    for row in identities:
        party_roles_data = roles_by_party.get(row["id"], [])
        roles = [
            PartyRoleResponse(
                id=uuid.UUID(r["id"]),
                party_identity_id=uuid.UUID(r["party_identity_id"]),
                project_id=uuid.UUID(r["project_id"]),
                role_title=r["role_title"],
                role_category=r.get("role_category") or "unclassified",
                governing_instrument=r.get("governing_instrument"),
                governing_instrument_type=r.get("governing_instrument_type"),
                effective_from=r.get("effective_from"),
                effective_to=r.get("effective_to"),
                authority_scope=r.get("authority_scope"),
                financial_threshold=r.get("financial_threshold"),
                financial_currency=r.get("financial_currency"),
                appointment_status=r.get("appointment_status", "proposed"),
                source_clause=r.get("source_clause"),
                confirmation_status=r.get("confirmation_status", "confirmed"),
                created_at=r["created_at"],
            )
            for r in party_roles_data
        ]
        output.append(
            PartyIdentityResponse(
                id=uuid.UUID(row["id"]),
                project_id=uuid.UUID(row["project_id"]),
                entity_type=row["entity_type"],
                legal_name=row["legal_name"],
                trading_names=row.get("trading_names") or [],
                registration_number=row.get("registration_number"),
                party_category=row.get("party_category") or "unclassified",
                is_internal=bool(row.get("is_internal", False)),
                identification_status=row.get("identification_status", "confirmed"),
                roles=roles,
                created_at=row["created_at"],
            )
        )
    return output
