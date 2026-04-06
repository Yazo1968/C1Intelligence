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


@router.get("/interview", response_model=InterviewStatusResponse)
async def get_interview_status(
    project_id: uuid.UUID,
    user_id: AuthenticatedUser,
) -> InterviewStatusResponse:
    """
    Return the reconciliation interview status for the most recent run.
    Shows total questions, how many are answered, and whether the interview
    is complete (all questions answered).
    """
    supabase = get_supabase_client()
    _verify_project_access(supabase, project_id, user_id)

    # Get the most recent run in parties_identified status
    try:
        run_result = (
            supabase.table("governance_run_log")
            .select("id")
            .eq("project_id", str(project_id))
            .eq("status", "parties_identified")
            .order("triggered_at", desc=True)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        logger.error("interview_status_run_fetch_failed",
                     project_id=str(project_id), error=str(exc))
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERVIEW_STATUS_FAILED",
            message=f"Failed to retrieve interview status: {exc}",
        )

    if not run_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No party identification run found. Run Phase 1 first.",
        )

    run_id = run_result.data[0]["id"]

    try:
        questions_result = (
            supabase.table("reconciliation_questions")
            .select("id, answer_selected")
            .eq("project_id", str(project_id))
            .eq("run_id", run_id)
            .execute()
        )
    except Exception as exc:
        logger.error("interview_questions_fetch_failed",
                     project_id=str(project_id), error=str(exc))
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERVIEW_STATUS_FAILED",
            message=f"Failed to retrieve questions: {exc}",
        )

    questions = questions_result.data or []
    total = len(questions)
    answered = sum(1 for q in questions if q.get("answer_selected"))
    pending = total - answered

    return InterviewStatusResponse(
        project_id=project_id,
        run_id=uuid.UUID(run_id),
        total_questions=total,
        answered=answered,
        pending=pending,
        complete=(total > 0 and pending == 0),
    )


@router.get("/interview/next-question",
            response_model=ReconciliationQuestionResponse)
async def get_next_interview_question(
    project_id: uuid.UUID,
    user_id: AuthenticatedUser,
) -> ReconciliationQuestionResponse:
    """
    Return the next unanswered reconciliation question for the most recent run,
    ordered by sequence_number. Returns 404 when all questions are answered.
    """
    supabase = get_supabase_client()
    _verify_project_access(supabase, project_id, user_id)

    # Get the most recent parties_identified run
    try:
        run_result = (
            supabase.table("governance_run_log")
            .select("id")
            .eq("project_id", str(project_id))
            .eq("status", "parties_identified")
            .order("triggered_at", desc=True)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERVIEW_QUESTION_FAILED",
            message=f"Failed to retrieve run: {exc}",
        )

    if not run_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No party identification run found.",
        )

    run_id = run_result.data[0]["id"]

    try:
        q_result = (
            supabase.table("reconciliation_questions")
            .select("*")
            .eq("project_id", str(project_id))
            .eq("run_id", run_id)
            .is_("answer_selected", "null")
            .order("sequence_number")
            .limit(1)
            .execute()
        )
    except Exception as exc:
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERVIEW_QUESTION_FAILED",
            message=f"Failed to retrieve next question: {exc}",
        )

    if not q_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="All questions answered. Interview is complete.",
        )

    q = q_result.data[0]
    return ReconciliationQuestionResponse(
        id=uuid.UUID(q["id"]),
        project_id=uuid.UUID(q["project_id"]),
        run_id=uuid.UUID(q["run_id"]),
        question_type=q["question_type"],
        question_text=q["question_text"],
        parties_referenced=[uuid.UUID(p) for p in (q.get("parties_referenced") or [])],
        documents_referenced=[uuid.UUID(d) for d in (q.get("documents_referenced") or [])],
        options_presented=q.get("options_presented") or [],
        answer_selected=q.get("answer_selected"),
        user_free_text=q.get("user_free_text"),
        answered_at=q.get("answered_at"),
        sequence_number=q["sequence_number"],
        created_at=q["created_at"],
    )


@router.post(
    "/interview/questions/{question_id}/answer",
    response_model=ReconciliationQuestionResponse,
)
async def submit_interview_answer(
    project_id: uuid.UUID,
    question_id: uuid.UUID,
    body: ReconciliationAnswerRequest,
    user_id: AuthenticatedUser,
) -> ReconciliationQuestionResponse:
    """
    Record the user's answer to a reconciliation question.
    answer_selected must match one of the options_presented for this question.
    Records answered_by (user_id) and answered_at (now).
    """
    supabase = get_supabase_client()
    _verify_project_access(supabase, project_id, user_id)

    # Fetch the question first to validate it belongs to this project
    try:
        q_result = (
            supabase.table("reconciliation_questions")
            .select("*")
            .eq("id", str(question_id))
            .eq("project_id", str(project_id))
            .single()
            .execute()
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found.",
        )

    q = q_result.data

    # Validate answer is one of the presented options
    options = q.get("options_presented") or []
    if options and body.answer_selected not in options:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"answer_selected must be one of the presented options. "
                f"Received: {body.answer_selected!r}"
            ),
        )

    now = datetime.now(timezone.utc)

    try:
        update_result = (
            supabase.table("reconciliation_questions")
            .update({
                "answer_selected": body.answer_selected,
                "user_free_text": body.user_free_text,
                "answered_by": str(user_id),
                "answered_at": now.isoformat(),
            })
            .eq("id", str(question_id))
            .eq("project_id", str(project_id))
            .execute()
        )
    except Exception as exc:
        logger.error("interview_answer_update_failed",
                     question_id=str(question_id), error=str(exc))
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERVIEW_ANSWER_FAILED",
            message=f"Failed to record answer: {exc}",
        )

    updated = update_result.data[0]

    logger.info(
        "interview_answer_recorded",
        project_id=str(project_id),
        question_id=str(question_id),
        question_type=updated["question_type"],
        answer=body.answer_selected,
    )

    return ReconciliationQuestionResponse(
        id=uuid.UUID(updated["id"]),
        project_id=uuid.UUID(updated["project_id"]),
        run_id=uuid.UUID(updated["run_id"]),
        question_type=updated["question_type"],
        question_text=updated["question_text"],
        parties_referenced=[uuid.UUID(p) for p in (updated.get("parties_referenced") or [])],
        documents_referenced=[uuid.UUID(d) for d in (updated.get("documents_referenced") or [])],
        options_presented=updated.get("options_presented") or [],
        answer_selected=updated.get("answer_selected"),
        user_free_text=updated.get("user_free_text"),
        answered_at=updated.get("answered_at"),
        sequence_number=updated["sequence_number"],
        created_at=updated["created_at"],
    )


@router.post("/extract-events", response_model=GovernanceRunResponse,
             status_code=status.HTTP_202_ACCEPTED)
async def extract_authority_events(
    project_id: uuid.UUID,
    user_id: AuthenticatedUser,
    background_tasks: BackgroundTasks,
) -> GovernanceRunResponse:
    """
    Trigger Phase 2 — authority event extraction.
    Requires the reconciliation interview to be complete.
    Creates a phase=2 run_log entry and launches run_governance_establishment
    as a background task.
    """
    from src.agents.governance_runner import run_governance_establishment

    supabase = get_supabase_client()
    _verify_project_access(supabase, project_id, user_id)

    # Verify interview is complete
    try:
        run_result = (
            supabase.table("governance_run_log")
            .select("id")
            .eq("project_id", str(project_id))
            .eq("status", "parties_identified")
            .order("triggered_at", desc=True)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="GOVERNANCE_RUN_FETCH_FAILED",
            message=f"Failed to check interview status: {exc}",
        )

    if not run_result.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reconciliation interview not complete. Complete the interview before extracting authority events.",
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
    )

    return GovernanceRunResponse(
        run_id=uuid.UUID(run["id"]),
        project_id=project_id,
        run_type=run["run_type"],
        status=run["status"],
        triggered_at=run["triggered_at"],
    )


@router.get("/authority-events")
async def list_authority_events(
    project_id: uuid.UUID,
    user_id: AuthenticatedUser,
) -> list[dict]:
    """Return all authority events for a project with party and role names."""
    supabase = get_supabase_client()
    _verify_project_access(supabase, project_id, user_id)

    try:
        # Query 1: authority_events (plain — no joins)
        ae_result = (
            supabase.table("authority_events")
            .select(
                "id, event_type, appointment_status, event_date, "
                "event_date_certain, authority_after, financial_threshold_after, "
                "financial_currency, instrument_status, confirmation_status, "
                "missing_action, source_clause, "
                "party_identity_id, party_role_id, "
                "initiated_by_party_id, authorised_by_party_id"
            )
            .eq("project_id", str(project_id))
            .order("event_date", desc=False)
            .execute()
        )
        raw_events = ae_result.data or []

        if not raw_events:
            return []

        # Query 2: party_identities — fetch all for this project
        pi_result = (
            supabase.table("party_identities")
            .select("id, legal_name, party_category")
            .eq("project_id", str(project_id))
            .execute()
        )
        pi_map = {
            row["id"]: row for row in (pi_result.data or [])
        }

        # Query 3: party_roles — fetch all for this project
        pr_result = (
            supabase.table("party_roles")
            .select("id, role_title")
            .eq("project_id", str(project_id))
            .execute()
        )
        pr_map = {
            row["id"]: row for row in (pr_result.data or [])
        }

    except Exception as exc:
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="AUTHORITY_EVENTS_FETCH_FAILED",
            message=f"Failed to fetch authority events: {exc}",
        )

    events = []
    for row in raw_events:
        party = pi_map.get(row.get("party_identity_id") or "") or {}
        role = pr_map.get(row.get("party_role_id") or "") or {}
        initiated = pi_map.get(row.get("initiated_by_party_id") or "") or {}
        authorised = pi_map.get(row.get("authorised_by_party_id") or "") or {}

        events.append({
            "id": row["id"],
            "event_type": row["event_type"],
            "appointment_status": row["appointment_status"],
            "event_date": row.get("event_date"),
            "event_date_certain": row.get("event_date_certain", True),
            "party_legal_name": party.get("legal_name", ""),
            "party_category": party.get("party_category", ""),
            "role_title": role.get("role_title", ""),
            "authority_after": row.get("authority_after"),
            "financial_threshold_after": row.get("financial_threshold_after"),
            "financial_currency": row.get("financial_currency"),
            "initiated_by_legal_name": initiated.get("legal_name"),
            "authorised_by_legal_name": authorised.get("legal_name"),
            "instrument_status": row.get("instrument_status", "retrieved"),
            "confirmation_status": row.get("confirmation_status", "confirmed"),
            "missing_action": row.get("missing_action"),
            "source_clause": row.get("source_clause"),
        })

    return events
