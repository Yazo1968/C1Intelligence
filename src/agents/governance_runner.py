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
notices, replacement notices, letters of award, and any correspondence that
establishes, changes, or ends a party's authority.

The confirmed entity registry is:
{entity_registry_text}

After completing your document retrieval, output ONLY a JSON object in the
following structure. No other text before or after the JSON.

{{
  "events": [
    {{
      "event_type": "appointment",
      "effective_date": "YYYY-MM-DD",
      "end_date": null,
      "party_canonical_name": "Must match a canonical_name from the registry above",
      "role": "The functional role or authority position",
      "appointed_by_canonical_name": null,
      "authority_dimension": "layer_1",
      "contract_source": "Instrument title",
      "scope": "What the appointment covers",
      "terminus_node": false,
      "extraction_status": "confirmed"
    }}
  ]
}}

Rules:
- event_type: appointment / delegation / termination / replacement / modification / suspension
- effective_date: ISO format YYYY-MM-DD. Use null if unknown.
- end_date: null if ongoing or not stated.
- party_canonical_name: MUST match exactly a canonical_name from the registry.
- authority_dimension: "layer_1" (contractual) / "layer_2a" (internal DOA) / "layer_2b" (statutory)
- extraction_status: "confirmed" or "inferred"
- Output valid JSON only. No trailing commas. No markdown. No explanation.
"""

# ---------------------------------------------------------------------------
# JSON parsing helpers
# ---------------------------------------------------------------------------

def _extract_json(text: str) -> dict | None:
    """
    Flexibly extract and parse a JSON object from SME output text.

    Tries three strategies in order:
    1. Parse the entire text as JSON (ideal — JSON-only output)
    2. Find a ```json ... ``` code block (standard backtick markdown)
    3. Find the first complete top-level JSON object with regex

    Returns parsed dict or None on all failures.
    """
    # Strategy 1: entire text is JSON
    stripped = text.strip()
    try:
        result = json.loads(stripped)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    # Strategy 2: ```json ... ``` code block
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', stripped, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group(1))
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

    # Strategy 3: first top-level { ... } block
    match = re.search(r'(\{.*\})', stripped, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group(1))
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

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
    from src.agents.specialist_config import SPECIALIST_CONFIGS
    from src.agents.base_specialist import BaseSpecialist
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
        config = SPECIALIST_CONFIGS["compliance"]
        sme = BaseSpecialist(config=config)

        findings = sme.run(
            query=PARTY_ID_QUERY,
            project_id=project_id,
            retrieved_chunks=[],
            round_1_findings=None,
        )

        logger.info(
            "governance_phase1_sme_complete",
            project_id=project_id,
            run_id=run_id,
            confidence=findings.confidence,
            findings_length=len(findings.findings),
        )

        data = _extract_json(findings.findings)
        if data is None:
            _mark_run_failed(
                supabase, run_id,
                "Phase 1: could not extract JSON from SME output. "
                f"Output length: {len(findings.findings)}. "
                f"Preview: {findings.findings[:200]}"
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
                result = supabase.table("party_identities").insert({
                    "project_id": project_id,
                    "entity_type": "organisation",
                    "legal_name": legal_name,
                    "trading_names": item.get("trading_names") or [],
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
                result = supabase.table("party_identities").insert({
                    "project_id": project_id,
                    "entity_type": "individual",
                    "legal_name": legal_name,
                    "trading_names": item.get("trading_names") or [],
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
            "documents_scanned": len(findings.sources_used),
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

    Fetches confirmed parties from governance_parties.
    Invokes the Compliance SME with the governance establishment skill.
    Parses the JSON output and writes to governance_events.
    Updates governance_run_log to complete on success, failed on error.

    Called as a FastAPI BackgroundTask from the /confirm-parties endpoint.
    """
    from src.agents.specialist_config import SPECIALIST_CONFIGS
    from src.agents.base_specialist import BaseSpecialist
    from src.clients import get_supabase_client

    supabase = get_supabase_client()

    logger.info(
        "governance_phase2_started",
        project_id=project_id,
        run_id=run_id,
    )

    try:
        parties_result = (
            supabase.table("governance_parties")
            .select("id, canonical_name, entity_type, contractual_role, confirmation_status")
            .eq("project_id", project_id)
            .execute()
        )
        parties = parties_result.data or []

        if not parties:
            _mark_run_failed(supabase, run_id, "No parties in registry — run Phase 1 first.")
            return

        party_id_map: dict[str, str] = {}
        registry_lines: list[str] = []
        for p in parties:
            party_id_map[p["canonical_name"]] = p["id"]
            registry_lines.append(
                f"- {p['canonical_name']} ({p['entity_type']}) — "
                f"role: {p.get('contractual_role') or 'unspecified'} — "
                f"status: {p['confirmation_status']}"
            )
        entity_registry_text = "\n".join(registry_lines)

        query = GOVERNANCE_EST_QUERY_TEMPLATE.format(
            entity_registry_text=entity_registry_text
        )

        config = SPECIALIST_CONFIGS["compliance"]
        sme = BaseSpecialist(config=config)

        findings = sme.run(
            query=query,
            project_id=project_id,
            retrieved_chunks=[],
            round_1_findings=None,
        )

        logger.info(
            "governance_phase2_sme_complete",
            project_id=project_id,
            run_id=run_id,
            confidence=findings.confidence,
            findings_length=len(findings.findings),
        )

        data = _extract_json(findings.findings)
        if data is None:
            _mark_run_failed(
                supabase, run_id,
                "Phase 2: could not extract JSON from SME output. "
                f"Output length: {len(findings.findings)}. "
                f"Preview: {findings.findings[:200]}"
            )
            return

        events = data.get("events", [])
        written = 0

        for event in events:
            party_name = str(event.get("party_canonical_name", "")).strip()
            party_id = party_id_map.get(party_name)

            if not party_id:
                logger.warning(
                    "governance_event_party_not_found",
                    party_canonical_name=party_name,
                    project_id=project_id,
                )
                continue

            appointed_by_name = event.get("appointed_by_canonical_name")
            appointed_by_id = (
                party_id_map.get(str(appointed_by_name))
                if appointed_by_name and str(appointed_by_name).lower() not in ("null", "none", "")
                else None
            )

            effective_date = _parse_date(event.get("effective_date"))
            end_date = _parse_date(event.get("end_date"))

            event_type = str(event.get("event_type", "")).strip()
            valid_types = {
                "appointment", "delegation", "termination",
                "replacement", "modification", "suspension"
            }
            if event_type not in valid_types:
                logger.warning(
                    "governance_event_invalid_type",
                    event_type=event_type,
                    party=party_name,
                )
                continue

            authority_dimension = event.get("authority_dimension", "layer_1")
            if authority_dimension not in {"layer_1", "layer_2a", "layer_2b"}:
                authority_dimension = "layer_1"

            extraction_status = event.get("extraction_status", "inferred")
            if extraction_status not in {"confirmed", "inferred", "flagged"}:
                extraction_status = "inferred"

            try:
                supabase.table("governance_events").insert({
                    "project_id": project_id,
                    "event_type": event_type,
                    "effective_date": (
                        effective_date.isoformat()
                        if effective_date
                        else datetime.now(timezone.utc).date().isoformat()
                    ),
                    "end_date": end_date.isoformat() if end_date else None,
                    "party_id": party_id,
                    "role": event.get("role") or "unspecified",
                    "appointed_by_party_id": appointed_by_id,
                    "authority_dimension": authority_dimension,
                    "contract_source": event.get("contract_source") or None,
                    "scope": event.get("scope") or None,
                    "terminus_node": bool(event.get("terminus_node", False)),
                    "extraction_status": extraction_status,
                }).execute()
                written += 1
            except Exception as exc:
                logger.error(
                    "governance_event_insert_failed",
                    party=party_name,
                    event_type=event_type,
                    error=str(exc),
                )

        supabase.table("governance_run_log").update({
            "status": "complete",
            "events_extracted": written,
            "documents_scanned": len(findings.sources_used),
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", run_id).execute()

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


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

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
