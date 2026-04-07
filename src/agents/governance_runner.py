"""
C1 — Governance Execution Layer
Implements Phase 1 (party identification) and Phase 2 (governance establishment)
for the governance feature. Called as background tasks from the governance API routes.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import date, datetime, timezone

from src.logging_config import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# SME query templates
# Requests JSON-only output — no narrative analysis text.
# The SME uses its tools to retrieve documents, then outputs structured JSON.
# JSON-only keeps output well within token limits and avoids delimiter issues.
# ---------------------------------------------------------------------------

PARTY_ID_QUERY = """
Use your search_chunks and get_document tools to retrieve all project contracts
and related documents: construction contract, appointment letters, delegation
letters, letters of award, sub-contract agreements, and any correspondence
naming parties or roles.

After completing your document retrieval, output ONLY a JSON object in the
following structure. No other text before or after the JSON.

{
  "organisations": [
    {
      "legal_name": "Full registered legal name exactly as in the contract execution block",
      "trading_names": ["Short name", "Abbreviation", "Any other variant found"],
      "registration_number": null,
      "party_category": "Select from the closed list below",
      "is_internal": false,
      "identification_status": "confirmed",
      "roles": [
        {
          "role_title": "Role title exactly as it appears in the source instrument",
          "role_category": "Select from the party_category closed list",
          "governing_instrument": "Name and date of the instrument that creates this role",
          "governing_instrument_type": "Select: main_contract | appointment_letter | delegation_letter | novation_agreement | board_resolution | correspondence | other",
          "effective_from": "YYYY-MM-DD or null if unknown",
          "effective_to": null,
          "authority_scope": "Brief plain-language description of what this role authorises the party to do",
          "financial_threshold": null,
          "financial_currency": null,
          "appointment_status": "Select: proposed | pending | executed",
          "source_clause": "Clause or section reference if stated, else null",
          "confirmation_status": "confirmed"
        }
      ]
    }
  ],
  "individuals": [
    {
      "legal_name": "Full name",
      "trading_names": ["Alternative name if any"],
      "registration_number": null,
      "party_category": "Select from closed list",
      "is_internal": false,
      "identification_status": "confirmed",
      "roles": [ ... same role structure as above ... ]
    }
  ]
}

Party category closed list — select the single best match:
Internal (Employer's organisation):
  employer | employer_representative | funder | parent_affiliate
Contract Administration:
  contract_administrator | resident_engineer | independent_certifier
Main Contractor:
  main_contractor | contractors_representative
Subcontractors:
  nominated_subcontractor | domestic_subcontractor |
  specialist_subcontractor | supplier_manufacturer
Consultants:
  design_consultant | cost_consultant | project_management_consultant |
  planning_consultant | clerk_of_works
Statutory and Regulatory:
  competent_authority | utility_authority | statutory_inspector
Dispute Resolution:
  dab_daab | arbitral_tribunal | expert_mediator
Financial and Legal:
  insurer | surety | legal_counsel
Other:
  unclassified

Appointment status:
  proposed  — party named or nominated; no binding appointment instrument found
  pending   — initiation document found; authorisation document not found
  executed  — binding instrument retrieved from warehouse

Confirmation status:
  confirmed — extracted from a retrieved document
  inferred  — deduced from context without a direct retrieved appointment instrument

Rules:
- legal_name is the authoritative name from the contract execution block.
- trading_names includes every name variant found across all retrieved documents.
- is_internal = true only if the party is part of the Employer's own organisation.
- A party may have multiple role entries in the roles array.
- If no individuals are found, use [].
- Output valid JSON only. No trailing commas. No markdown. No explanation.
"""

GOVERNANCE_EST_QUERY_TEMPLATE = """
Use your search_chunks and get_document tools to retrieve all project documents
containing authority events: appointment letters, delegation letters, termination
notices, replacement notices, novation agreements, letters of award, board
resolutions, and any correspondence that establishes, changes, or ends a
party's authority.

The confirmed party registry is:
{entity_registry_text}

After completing your document retrieval, output ONLY a JSON object in the
following structure. No other text before or after the JSON.

{{
  "events": [
    {{
      "event_type": "appointment",
      "party_legal_name": "Must match a legal_name from the registry above exactly",
      "role_title": "The role this event relates to — match the role_title from the registry if possible",
      "appointment_status": "executed",
      "event_date": "YYYY-MM-DD",
      "event_date_certain": true,
      "end_date": null,
      "initiated_by_legal_name": "Legal name of party who initiated this event",
      "authorised_by_legal_name": null,
      "authority_before": "What the party could do before this event — null for first appointment",
      "authority_after": "What the party can do as a result of this event",
      "financial_threshold_before": null,
      "financial_threshold_after": null,
      "source_instrument": "Title of the document evidencing this event",
      "source_clause": "Clause or section reference if stated",
      "instrument_status": "retrieved",
      "confirmation_status": "confirmed",
      "missing_action": null
    }}
  ]
}}

Rules:
- event_type must be one of: nomination, appointment, authority_grant, scope_addition,
  scope_reduction, role_transfer, novation, replacement, suspension, termination.
- party_legal_name MUST match exactly a legal_name from the registry above.
- role_title should match a role_title from that party's roles in the registry. If
  uncertain, use the party's primary role title.
- appointment_status: "executed" if a binding instrument was retrieved; "pending" if
  action was initiated but authorisation is unconfirmed; "proposed" if named only.
- event_date: ISO format YYYY-MM-DD. Use null if unknown.
- event_date_certain: false if the date is inferred or approximate.
- initiated_by_legal_name: the party who issued or proposed the action.
- authorised_by_legal_name: the party whose approval gave the action legal effect.
  Use null if not applicable or not confirmed from retrieved documents.
- instrument_status: "retrieved" if the source document is in the warehouse;
  "referenced_only" if mentioned but not retrieved; "absent" if no document found.
- confirmation_status: "confirmed" if grounded in a retrieved document; "assumed"
  only if declaring something not in any retrieved document.
- missing_action: describe what is required to execute this event — populate only
  for pending or proposed events; null for executed events.
- Include ALL identified events — confirmed, pending, and proposed.
- CRITICAL: Output ONLY the raw JSON object. No preamble, no explanation,
    no markdown fences, no code blocks. The very first character of your
    response must be {{ and the very last character must be }}. Any text
    before or after the JSON object means you have failed this task.
"""

# ---------------------------------------------------------------------------
# JSON parsing helpers
# ---------------------------------------------------------------------------

def _extract_json(text: str) -> dict | None:
    """
    Flexibly extract and parse a JSON object from SME output text.

    Tries four strategies in order:
    1. Parse the entire text as JSON (ideal — JSON-only output)
    2. Find a ```json ... ``` code block
    3. Find the first { and match to its correct closing } by counting braces
    4. Greedy fallback — last resort
    """
    import re as _re

    stripped = text.strip()

    # Strategy 1: entire text is JSON
    try:
        result = json.loads(stripped)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    # Strategy 2: ```json ... ``` code block — extract content between fences
    match = _re.search(r'```(?:json)?\s*(\{)', stripped, _re.DOTALL)
    if match:
        start = match.start(1)
        depth = 0
        for i, ch in enumerate(stripped[start:], start):
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    candidate = stripped[start:i + 1]
                    try:
                        result = json.loads(candidate)
                        if isinstance(result, dict):
                            return result
                    except json.JSONDecodeError:
                        break

    # Strategy 3: find first { and walk to matching closing } by brace count
    first_brace = stripped.find('{')
    if first_brace != -1:
        depth = 0
        for i, ch in enumerate(stripped[first_brace:], first_brace):
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    candidate = stripped[first_brace:i + 1]
                    try:
                        result = json.loads(candidate)
                        if isinstance(result, dict):
                            return result
                    except json.JSONDecodeError:
                        break

    logger.error(
        "governance_json_extract_failed",
        text_length=len(text),
        text_preview=text[:300],
    )
    return None


def _parse_date(value: str | None) -> date | None:
    """Parse ISO date string to date object. Returns None if null or unparseable."""
    if not value or str(value).lower() in ("null", "unknown", "none", ""):
        return None
    try:
        return date.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Phase 1 — Party and role identification
# ---------------------------------------------------------------------------

def run_party_identification(project_id: str, run_id: str) -> None:
    """
    Phase 1 of the governance execution layer.

    Invokes the Compliance SME with the party identification skill.
    Parses the JSON output and writes to party_identities and party_roles.
    Updates governance_run_log to parties_identified on success, failed on error.

    Called as a FastAPI BackgroundTask from the /run endpoint.
    """
    from src.clients import get_supabase_client

    supabase = get_supabase_client()

    logger.info(
        "governance_phase1_started",
        project_id=project_id,
        run_id=run_id,
    )

    VALID_APPOINTMENT_STATUSES = {"proposed", "pending", "executed"}
    VALID_INSTRUMENT_TYPES = {
        "main_contract", "appointment_letter", "delegation_letter",
        "novation_agreement", "board_resolution", "correspondence", "other",
    }

    try:
        _output, _rounds = _run_governance_llm(PARTY_ID_QUERY, project_id)

        logger.info(
            "governance_phase1_sme_complete",
            project_id=project_id,
            run_id=run_id,
            output_length=len(_output),
        )

        data = _extract_json(_output)
        if data is None:
            _mark_run_failed(
                supabase, run_id,
                "Phase 1: could not extract JSON from SME output. "
                f"Output length: {len(_output)}. "
                f"Preview: {_output[:200]}"
            )
            return

        organisations = data.get("organisations", [])
        individuals = data.get("individuals", [])

        if not organisations and not individuals:
            logger.warning(
                "governance_phase1_empty_registry",
                project_id=project_id,
                run_id=run_id,
            )

        total_parties = 0

        for item in organisations:
            legal_name = str(item.get("legal_name", "")).strip()
            if not legal_name:
                continue
            try:
                # Check for existing identity before insert
                existing = (
                    supabase.table("party_identities")
                    .select("id")
                    .eq("project_id", project_id)
                    .eq("legal_name", legal_name)
                    .execute()
                )
                if existing.data:
                    party_identity_id = existing.data[0]["id"]
                else:
                    result = supabase.table("party_identities").insert({
                        "project_id": project_id,
                        "entity_type": "organisation",
                        "legal_name": legal_name,
                        "trading_names": list(dict.fromkeys(
                            t for t in (item.get("trading_names") or []) if t
                        )),
                        "registration_number": item.get("registration_number") or None,
                        "party_category": item.get("party_category") or "unclassified",
                        "is_internal": bool(item.get("is_internal", False)),
                        "identification_status": item.get("identification_status", "confirmed"),
                        "assumption_id": None,
                    }).execute()
                    party_identity_id = result.data[0]["id"]
                    total_parties += 1
            except Exception as exc:
                logger.error(
                    "governance_identity_insert_failed",
                    legal_name=legal_name,
                    error=str(exc),
                )
                continue

            for role in item.get("roles", []):
                appt_status = role.get("appointment_status") or "proposed"
                if appt_status not in VALID_APPOINTMENT_STATUSES:
                    appt_status = "proposed"
                instr_type = role.get("governing_instrument_type") or "other"
                if instr_type not in VALID_INSTRUMENT_TYPES:
                    instr_type = "other"
                eff_from = _parse_date(role.get("effective_from"))
                eff_to = _parse_date(role.get("effective_to"))
                try:
                    supabase.table("party_roles").insert({
                        "party_identity_id": party_identity_id,
                        "project_id": project_id,
                        "role_title": role.get("role_title") or "unspecified",
                        "role_category": role.get("role_category") or "unclassified",
                        "governing_instrument": role.get("governing_instrument") or None,
                        "governing_instrument_type": instr_type,
                        "effective_from": eff_from.isoformat() if eff_from else None,
                        "effective_to": eff_to.isoformat() if eff_to else None,
                        "authority_scope": role.get("authority_scope") or None,
                        "financial_threshold": role.get("financial_threshold") or None,
                        "financial_currency": role.get("financial_currency") or None,
                        "appointment_status": appt_status,
                        "source_clause": role.get("source_clause") or None,
                        "confirmation_status": role.get("confirmation_status", "confirmed"),
                        "assumption_id": None,
                        "source_document_id": None,
                        "counterparty_id": None,
                        "preceding_role_id": None,
                    }).execute()
                except Exception as exc:
                    logger.error(
                        "governance_role_insert_failed",
                        legal_name=legal_name,
                        role_title=role.get("role_title"),
                        error=str(exc),
                    )

        for item in individuals:
            legal_name = str(item.get("legal_name", "")).strip()
            if not legal_name:
                continue
            try:
                # Check for existing identity before insert
                existing = (
                    supabase.table("party_identities")
                    .select("id")
                    .eq("project_id", project_id)
                    .eq("legal_name", legal_name)
                    .execute()
                )
                if existing.data:
                    party_identity_id = existing.data[0]["id"]
                else:
                    result = supabase.table("party_identities").insert({
                        "project_id": project_id,
                        "entity_type": "individual",
                        "legal_name": legal_name,
                        "trading_names": list(dict.fromkeys(
                            t for t in (item.get("trading_names") or []) if t
                        )),
                        "registration_number": item.get("registration_number") or None,
                        "party_category": item.get("party_category") or "unclassified",
                        "is_internal": bool(item.get("is_internal", False)),
                        "identification_status": item.get("identification_status", "confirmed"),
                        "assumption_id": None,
                    }).execute()
                    party_identity_id = result.data[0]["id"]
                    total_parties += 1
            except Exception as exc:
                logger.error(
                    "governance_identity_insert_failed",
                    legal_name=legal_name,
                    error=str(exc),
                )
                continue

            for role in item.get("roles", []):
                appt_status = role.get("appointment_status") or "proposed"
                if appt_status not in VALID_APPOINTMENT_STATUSES:
                    appt_status = "proposed"
                instr_type = role.get("governing_instrument_type") or "other"
                if instr_type not in VALID_INSTRUMENT_TYPES:
                    instr_type = "other"
                eff_from = _parse_date(role.get("effective_from"))
                eff_to = _parse_date(role.get("effective_to"))
                try:
                    supabase.table("party_roles").insert({
                        "party_identity_id": party_identity_id,
                        "project_id": project_id,
                        "role_title": role.get("role_title") or "unspecified",
                        "role_category": role.get("role_category") or "unclassified",
                        "governing_instrument": role.get("governing_instrument") or None,
                        "governing_instrument_type": instr_type,
                        "effective_from": eff_from.isoformat() if eff_from else None,
                        "effective_to": eff_to.isoformat() if eff_to else None,
                        "authority_scope": role.get("authority_scope") or None,
                        "financial_threshold": role.get("financial_threshold") or None,
                        "financial_currency": role.get("financial_currency") or None,
                        "appointment_status": appt_status,
                        "source_clause": role.get("source_clause") or None,
                        "confirmation_status": role.get("confirmation_status", "confirmed"),
                        "assumption_id": None,
                        "source_document_id": None,
                        "counterparty_id": None,
                        "preceding_role_id": None,
                    }).execute()
                except Exception as exc:
                    logger.error(
                        "governance_role_insert_failed",
                        legal_name=legal_name,
                        role_title=role.get("role_title"),
                        error=str(exc),
                    )

        generate_interview_questions(project_id, run_id, supabase)

        supabase.table("governance_run_log").update({
            "status": "parties_identified",
            "documents_scanned": _rounds,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", run_id).execute()

        logger.info(
            "governance_phase1_complete",
            project_id=project_id,
            run_id=run_id,
            total_parties=total_parties,
        )

    except Exception as exc:
        logger.error(
            "governance_phase1_unexpected_error",
            project_id=project_id,
            run_id=run_id,
            error=str(exc),
        )
        _mark_run_failed(supabase, run_id, str(exc))


# ---------------------------------------------------------------------------
# Phase 1.5 — Reconciliation interview question generation
# ---------------------------------------------------------------------------

def generate_interview_questions(
    project_id: str,
    run_id: str,
    supabase,
) -> None:
    """
    Generate reconciliation interview questions based on Phase 1 output.
    Reads party_identities and party_roles. Inserts into reconciliation_questions.
    Four detection rules applied in sequence. Each rule may produce 0..N questions.
    Questions are numbered sequentially starting from 1.
    Errors are logged but do not abort Phase 1 — the run proceeds even if
    question generation fails.
    """
    from collections import defaultdict

    try:
        identities_result = (
            supabase.table("party_identities")
            .select("id, legal_name, trading_names, party_category, is_internal, identification_status")
            .eq("project_id", project_id)
            .execute()
        )
        identities = identities_result.data or []

        roles_result = (
            supabase.table("party_roles")
            .select("id, party_identity_id, role_title, role_category, "
                    "appointment_status, confirmation_status, "
                    "effective_from, effective_to, governing_instrument")
            .eq("project_id", project_id)
            .execute()
        )
        roles = roles_result.data or []

    except Exception as exc:
        logger.error(
            "interview_questions_fetch_failed",
            project_id=project_id,
            run_id=run_id,
            error=str(exc),
        )
        return

    questions: list[dict] = []
    seq = 1

    # --- Rule 1: Inferred parties (identification_status = "inferred") ---
    # Type 3 — Missing party: party exists in documents but could not be
    # fully confirmed. Ask user to confirm or correct.
    for identity in identities:
        if identity.get("identification_status") == "inferred":
            questions.append({
                "project_id": project_id,
                "run_id": run_id,
                "question_type": "missing_party",
                "question_text": (
                    f"The party \"{identity['legal_name']}\" was identified in project documents "
                    f"but could not be confirmed from a retrieved appointment instrument. "
                    f"Please confirm whether this party holds a formal role on this project."
                ),
                "parties_referenced": [identity["id"]],
                "documents_referenced": [],
                "options_presented": [
                    "Yes — this party holds a confirmed role on this project",
                    "No — this party does not hold a formal role",
                    "I need to review further before answering",
                ],
                "answer_selected": None,
                "user_free_text": None,
                "answered_by": None,
                "answered_at": None,
                "sequence_number": seq,
            })
            seq += 1

    # --- Rule 2: Role conflict — multiple parties with the same role_category ---
    # Type 2 — Role conflict: two or more distinct parties hold the same
    # role_category simultaneously. Ask user which party governs.
    role_category_to_parties: dict[str, list] = defaultdict(list)
    for role in roles:
        if role.get("appointment_status") in ("executed", "pending"):
            cat = role.get("role_category") or "unclassified"
            pid = role.get("party_identity_id")
            if pid not in role_category_to_parties[cat]:
                role_category_to_parties[cat].append(pid)

    identity_name_map = {i["id"]: i["legal_name"] for i in identities}

    for cat, party_ids in role_category_to_parties.items():
        if len(party_ids) > 1 and cat != "unclassified":
            names = [identity_name_map.get(pid, pid) for pid in party_ids]
            names_str = " / ".join(names)
            options = [f"{n} governs this role" for n in names]
            options.append("Both parties hold this role simultaneously (legitimate overlap)")
            options.append("I need to review the instruments before answering")
            questions.append({
                "project_id": project_id,
                "run_id": run_id,
                "question_type": "role_conflict",
                "question_text": (
                    f"Multiple parties appear to hold the role category \"{cat}\": {names_str}. "
                    f"Please confirm which party governs this role, or confirm a legitimate overlap."
                ),
                "parties_referenced": party_ids,
                "documents_referenced": [],
                "options_presented": options,
                "answer_selected": None,
                "user_free_text": None,
                "answered_by": None,
                "answered_at": None,
                "sequence_number": seq,
            })
            seq += 1

    # --- Rule 3: Proposed roles (appointment_status = "proposed") ---
    # Party named in a document but no appointment instrument found.
    # Ask user to confirm contractual standing.
    for role in roles:
        if role.get("appointment_status") == "proposed":
            pid = role.get("party_identity_id")
            party_name = identity_name_map.get(pid, "Unknown party")
            instrument = role.get("governing_instrument") or "an unidentified instrument"
            questions.append({
                "project_id": project_id,
                "run_id": run_id,
                "question_type": "missing_party",
                "question_text": (
                    f"\"{party_name}\" is named as \"{role['role_title']}\" in {instrument}, "
                    f"but no executed appointment instrument was retrieved. "
                    f"Please confirm the appointment status of this party."
                ),
                "parties_referenced": [pid] if pid else [],
                "documents_referenced": [],
                "options_presented": [
                    "Formally appointed — I can confirm a binding instrument exists",
                    "Nominated only — no formal appointment instrument was ever issued",
                    "Appointment is pending — instrument is in progress",
                    "I need to review further before answering",
                ],
                "answer_selected": None,
                "user_free_text": None,
                "answered_by": None,
                "answered_at": None,
                "sequence_number": seq,
            })
            seq += 1

    # --- Rule 4: is_internal confirmation ---
    # Type 5 — Hierarchy placement: confirm which parties are internal
    # (part of the Employer's organisation). One question covering all parties
    # where is_internal = True, so the user can correct misclassifications.
    internal_parties = [i for i in identities if i.get("is_internal")]
    if internal_parties:
        names = [i["legal_name"] for i in internal_parties]
        names_str = ", ".join(names)
        questions.append({
            "project_id": project_id,
            "run_id": run_id,
            "question_type": "hierarchy_placement",
            "question_text": (
                f"The following parties were classified as internal to the Employer's "
                f"organisation: {names_str}. Please confirm this is correct or identify "
                f"any party that should be reclassified as external."
            ),
            "parties_referenced": [i["id"] for i in internal_parties],
            "documents_referenced": [],
            "options_presented": [
                "All listed parties are correctly classified as internal",
                "One or more parties are incorrectly classified — I will specify in comments",
            ],
            "answer_selected": None,
            "user_free_text": None,
            "answered_by": None,
            "answered_at": None,
            "sequence_number": seq,
        })
        seq += 1

    # --- Insert all generated questions ---
    for q in questions:
        try:
            supabase.table("reconciliation_questions").insert(q).execute()
        except Exception as exc:
            logger.error(
                "interview_question_insert_failed",
                project_id=project_id,
                run_id=run_id,
                question_type=q.get("question_type"),
                error=str(exc),
            )

    logger.info(
        "interview_questions_generated",
        project_id=project_id,
        run_id=run_id,
        total_questions=len(questions),
    )


# ---------------------------------------------------------------------------
# Phase 2 — Governance establishment
# ---------------------------------------------------------------------------

def run_governance_establishment(project_id: str, run_id: str) -> None:
    """
    Phase 2 of the governance execution layer.

    Reads party_identities and party_roles for the project.
    Invokes the Compliance SME with the governance establishment skill.
    Parses the JSON output and writes to authority_events.
    Updates governance_run_log to complete on success, failed on error.

    Called as a FastAPI BackgroundTask from the /interview endpoint
    once the reconciliation interview is complete.
    """
    from src.clients import get_supabase_client

    supabase = get_supabase_client()

    logger.info(
        "governance_phase2_started",
        project_id=project_id,
        run_id=run_id,
    )

    written = 0
    _rounds = 0

    try:
        # Load party_identities
        identities_result = (
            supabase.table("party_identities")
            .select("id, legal_name, trading_names, party_category, entity_type")
            .eq("project_id", project_id)
            .execute()
        )
        identities = identities_result.data or []

        if not identities:
            _mark_run_failed(
                supabase, run_id,
                "No party identities found — run Phase 1 first."
            )
            return

        # Load party_roles for all identities
        roles_result = (
            supabase.table("party_roles")
            .select("id, party_identity_id, role_title, appointment_status")
            .eq("project_id", project_id)
            .execute()
        )
        roles = roles_result.data or []

        # Build lookup maps
        # legal_name → identity_id
        identity_map: dict[str, str] = {}
        # identity_id → list of roles
        roles_by_identity: dict[str, list[dict]] = {}

        for identity in identities:
            identity_map[identity["legal_name"]] = identity["id"]
            # Also map trading names
            for trading_name in (identity.get("trading_names") or []):
                if trading_name and trading_name not in identity_map:
                    identity_map[trading_name] = identity["id"]
            roles_by_identity[identity["id"]] = []

        for role in roles:
            iid = role["party_identity_id"]
            if iid in roles_by_identity:
                roles_by_identity[iid].append(role)

        # Build entity registry text for the SME query
        registry_lines: list[str] = []
        for identity in identities:
            iid = identity["id"]
            party_roles_list = roles_by_identity.get(iid, [])
            role_titles = ", ".join(
                r['role_title'] for r in party_roles_list[:2]
            ) or "unspecified"
            registry_lines.append(
                f"- {identity['legal_name']} ({identity['party_category']})"
                f": {role_titles}"
            )
        entity_registry_text = "\n".join(registry_lines)

        query = GOVERNANCE_EST_QUERY_TEMPLATE.format(
            entity_registry_text=entity_registry_text
        )

        _output, _rounds = _run_governance_llm(query, project_id)

        logger.info(
            "governance_phase2_sme_complete",
            project_id=project_id,
            run_id=run_id,
            output_length=len(_output),
        )

        data = _extract_json(_output)
        if data is None:
            _mark_run_failed(
                supabase, run_id,
                "Phase 2: could not extract JSON from SME output. "
                f"Output length: {len(_output)}. "
                f"Preview: {_output[:200]}"
            )
            return

        events = data.get("events", [])

        VALID_EVENT_TYPES = {
            "nomination", "appointment", "authority_grant",
            "scope_addition", "scope_reduction", "role_transfer",
            "novation", "replacement", "suspension", "termination",
        }
        VALID_APPOINTMENT_STATUS = {"proposed", "pending", "executed"}
        VALID_INSTRUMENT_STATUS = {"retrieved", "referenced_only", "absent"}
        VALID_CONFIRMATION_STATUS = {"confirmed", "assumed"}

        for event in events:
            party_legal_name = str(event.get("party_legal_name", "")).strip()
            party_identity_id = identity_map.get(party_legal_name)

            if not party_identity_id:
                logger.warning(
                    "governance_event_party_not_found",
                    party_legal_name=party_legal_name,
                    project_id=project_id,
                )
                continue

            # Resolve party_role_id — required FK
            role_title = str(event.get("role_title", "")).strip()
            party_roles_for_identity = roles_by_identity.get(party_identity_id, [])
            party_role_id: str | None = None

            if role_title:
                # Exact match first
                for r in party_roles_for_identity:
                    if r["role_title"].lower() == role_title.lower():
                        party_role_id = r["id"]
                        break
                # Partial match fallback
                if not party_role_id:
                    for r in party_roles_for_identity:
                        if role_title.lower() in r["role_title"].lower():
                            party_role_id = r["id"]
                            break

            # Use first role as last resort if still not found
            if not party_role_id and party_roles_for_identity:
                party_role_id = party_roles_for_identity[0]["id"]
                logger.warning(
                    "governance_event_role_fallback",
                    party_legal_name=party_legal_name,
                    role_title=role_title,
                    fallback_role=party_roles_for_identity[0]["role_title"],
                )

            if not party_role_id:
                logger.warning(
                    "governance_event_no_role_found",
                    party_legal_name=party_legal_name,
                    project_id=project_id,
                )
                continue

            # Resolve actor IDs
            initiated_by_name = event.get("initiated_by_legal_name")
            initiated_by_id = (
                identity_map.get(str(initiated_by_name))
                if initiated_by_name and str(initiated_by_name).lower() not in ("null", "none", "")
                else None
            )

            authorised_by_name = event.get("authorised_by_legal_name")
            authorised_by_id = (
                identity_map.get(str(authorised_by_name))
                if authorised_by_name and str(authorised_by_name).lower() not in ("null", "none", "")
                else None
            )

            # Validate enum fields
            event_type = str(event.get("event_type", "")).strip()
            if event_type not in VALID_EVENT_TYPES:
                logger.warning(
                    "governance_event_invalid_type",
                    event_type=event_type,
                    party=party_legal_name,
                )
                continue

            appt_status = event.get("appointment_status", "proposed")
            if appt_status not in VALID_APPOINTMENT_STATUS:
                appt_status = "proposed"

            instrument_status = event.get("instrument_status", "retrieved")
            if instrument_status not in VALID_INSTRUMENT_STATUS:
                instrument_status = "retrieved"

            conf_status = event.get("confirmation_status", "confirmed")
            if conf_status not in VALID_CONFIRMATION_STATUS:
                conf_status = "confirmed"

            event_date = _parse_date(event.get("event_date"))
            end_date = _parse_date(event.get("end_date"))

            # Dedup: skip if an identical event already exists for this party,
            # role, event_type, and event_date
            try:
                existing_event = (
                    supabase.table("authority_events")
                    .select("id")
                    .eq("project_id", project_id)
                    .eq("party_identity_id", party_identity_id)
                    .eq("party_role_id", party_role_id)
                    .eq("event_type", event_type)
                    .eq("event_date", event_date.isoformat() if event_date else "null")
                    .execute()
                )
                if existing_event.data:
                    logger.info(
                        "governance_event_duplicate_skipped",
                        party=party_legal_name,
                        event_type=event_type,
                        event_date=str(event_date),
                    )
                    continue
            except Exception as dedup_exc:
                logger.warning(
                    "governance_event_dedup_check_failed",
                    party=party_legal_name,
                    error=str(dedup_exc),
                )
                # On dedup check failure, proceed with insert rather than skip

            try:
                supabase.table("authority_events").insert({
                    "project_id": project_id,
                    "party_role_id": party_role_id,
                    "party_identity_id": party_identity_id,
                    "event_type": event_type,
                    "appointment_status": appt_status,
                    "event_date": event_date.isoformat() if event_date else None,
                    "event_date_certain": bool(event.get("event_date_certain", True)),
                    "end_date": end_date.isoformat() if end_date else None,
                    "initiated_by_party_id": initiated_by_id,
                    "authorised_by_party_id": authorised_by_id,
                    "authority_before": event.get("authority_before") or None,
                    "authority_after": event.get("authority_after") or None,
                    "financial_threshold_before": event.get("financial_threshold_before") or None,
                    "financial_threshold_after": event.get("financial_threshold_after") or None,
                    "source_clause": event.get("source_clause") or None,
                    "instrument_status": instrument_status,
                    "confirmation_status": conf_status,
                    "missing_action": event.get("missing_action") or None,
                }).execute()
                written += 1
            except Exception as exc:
                logger.error(
                    "governance_authority_event_insert_failed",
                    party=party_legal_name,
                    event_type=event_type,
                    error=str(exc),
                )

        logger.info(
            "governance_phase2_complete",
            project_id=project_id,
            run_id=run_id,
            events_written=written,
        )

    except Exception as exc:
        logger.error(
            "governance_phase2_unexpected_error",
            project_id=project_id,
            run_id=run_id,
            error=str(exc),
        )
        _mark_run_failed(supabase, run_id, str(exc))
    finally:
        try:
            # Determine final status — complete if any events written,
            # failed if zero events and not already marked failed
            current_status_result = (
                supabase.table("governance_run_log")
                .select("status")
                .eq("id", run_id)
                .single()
                .execute()
            )
            current_status = (
                current_status_result.data.get("status")
                if current_status_result.data else "running"
            )
            # Only update if still running — don't overwrite failed status
            if current_status == "running":
                final_status = "complete" if written > 0 else "failed"
                supabase.table("governance_run_log").update({
                    "status": final_status,
                    "events_extracted": written,
                    "documents_scanned": _rounds,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                }).eq("id", run_id).execute()
                logger.info(
                    "governance_phase2_run_log_closed",
                    run_id=run_id,
                    final_status=final_status,
                    events_written=written,
                )
        except Exception as finally_exc:
            logger.error(
                "governance_phase2_run_log_close_failed",
                run_id=run_id,
                error=str(finally_exc),
            )


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_JSON_SYSTEM_PROMPT = (
    "You are a structured data extraction engine. "
    "You output ONLY valid JSON objects. "
    "You never output any text before or after the JSON. "
    "Your response always starts with { and ends with }. "
    "No markdown. No code fences. No explanation. Only JSON."
)

_SEARCH_TOOL = {
    "name": "search_chunks",
    "description": (
        "Search for relevant document chunks in the project's "
        "document warehouse using semantic similarity."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query.",
            },
            "top_k": {
                "type": "integer",
                "description": "Number of results to return (default 10).",
            },
        },
        "required": ["query"],
    },
}


def _run_governance_llm(user_query: str, project_id: str) -> tuple[str, int]:
    """
    Run a direct Anthropic API call with JSON-only system prompt and an
    agentic tool-use loop for search_chunks. Returns (output_text, rounds).
    """
    import anthropic as _anthropic
    from src.config import ANTHROPIC_API_KEY as _ANTHROPIC_API_KEY

    _client = _anthropic.Anthropic(api_key=_ANTHROPIC_API_KEY)

    _messages = [{"role": "user", "content": user_query}]

    _response = _client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=8000,
        system=_JSON_SYSTEM_PROMPT,
        tools=[_SEARCH_TOOL],
        messages=_messages,
    )

    _rounds = 0
    _max_rounds = 5

    while _response.stop_reason == "tool_use" and _rounds < _max_rounds:
        _rounds += 1
        _tool_results = []
        for _block in _response.content:
            if _block.type == "tool_use" and _block.name == "search_chunks":
                from src.agents.tools import execute_tool as _execute_tool
                _result = _execute_tool(
                    "search_chunks",
                    dict(_block.input),
                    project_id,
                )
                _tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": _block.id,
                    "content": str(_result),
                })

        _messages.append({"role": "assistant", "content": _response.content})
        _messages.append({"role": "user", "content": _tool_results})

        _response = _client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=8000,
            system=_JSON_SYSTEM_PROMPT,
            tools=[_SEARCH_TOOL],
            messages=_messages,
        )

    # Extract text output from final response
    _output = ""
    for _block in _response.content:
        if hasattr(_block, "text"):
            _output += _block.text

    return _output, _rounds


def _mark_run_failed(supabase, run_id: str, reason: str) -> None:
    """Update run_log to failed status."""
    try:
        supabase.table("governance_run_log").update({
            "status": "failed",
            "error_message": reason[:2000],
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", run_id).execute()
        logger.error("governance_run_marked_failed", run_id=run_id, reason=reason)
    except Exception as exc:
        logger.error("governance_run_failed_update_error", run_id=run_id, error=str(exc))
