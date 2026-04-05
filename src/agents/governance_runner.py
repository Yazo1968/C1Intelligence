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
# ---------------------------------------------------------------------------

PARTY_ID_QUERY = """
Execute the party and role identification skill for this project.

Scan all project documents to identify every organisation and individual,
resolve aliases, and produce the entity registry as described in your skill file.

After your complete analysis text, append EXACTLY the following block.
Use triple-tilde delimiters exactly as shown. Do not omit this block.

~~~json_registry
{
  "organisations": [
    {
      "canonical_name": "Full formal legal name",
      "aliases": ["Alias 1", "Alias 2"],
      "contractual_role": "Role title as it appears in the contract",
      "terminus_node": false,
      "confirmation_status": "confirmed"
    }
  ],
  "individuals": [
    {
      "canonical_name": "Full name",
      "aliases": ["Alternative name"],
      "contractual_role": "Role title",
      "terminus_node": true,
      "confirmation_status": "inferred"
    }
  ]
}
~~~json_registry

Rules for the JSON block:
- confirmation_status: "confirmed" = explicitly named in a retrieved document;
  "inferred" = deduced from context without an explicit appointment instrument.
- terminus_node: true = cannot issue contractually binding instructions downward;
  false = can instruct, delegate, or direct parties below it.
- Include ALL identified entities — organisations and individuals.
- If no individuals are identified: use an empty array [].
- Use only valid JSON. No trailing commas.
"""

GOVERNANCE_EST_QUERY_TEMPLATE = """
Execute the governance establishment skill for this project.

The confirmed entity registry is provided below. Use the canonical names
exactly as listed to link every authority event to the correct party.

CONFIRMED ENTITY REGISTRY:
{entity_registry_text}

Scan all project documents to extract every authority event:
appointment, delegation, termination, replacement, modification, suspension.

After your complete analysis text, append EXACTLY the following block.
Use triple-tilde delimiters exactly as shown. Do not omit this block.

~~~json_events
{{
  "events": [
    {{
      "event_type": "appointment",
      "effective_date": "YYYY-MM-DD",
      "end_date": null,
      "party_canonical_name": "Canonical name matching the entity registry exactly",
      "role": "The functional role or authority position",
      "appointed_by_canonical_name": null,
      "authority_dimension": "layer_1",
      "contract_source": "Instrument title",
      "scope": "What the appointment covers or what authority is delegated",
      "terminus_node": false,
      "extraction_status": "confirmed"
    }}
  ]
}}
~~~json_events

Rules for the JSON block:
- event_type: one of appointment / delegation / termination / replacement /
  modification / suspension.
- effective_date: ISO format YYYY-MM-DD. Use null if unknown.
- end_date: null if ongoing or not stated.
- party_canonical_name: MUST match exactly a canonical_name from the entity
  registry above. Do not invent new names.
- appointed_by_canonical_name: null if not applicable or not retrieved.
- authority_dimension: "layer_1" (contractual) / "layer_2a" (internal DOA) /
  "layer_2b" (statutory).
- extraction_status: "confirmed" or "inferred".
- Use only valid JSON. No trailing commas.
"""

# ---------------------------------------------------------------------------
# JSON parsing helpers
# ---------------------------------------------------------------------------

def _parse_json_block(text: str, delimiter: str) -> dict | None:
    """
    Extract and parse a delimited JSON block from SME output text.

    Looks for content between ~~~{delimiter} ... ~~~{delimiter}.
    Returns parsed dict or None if not found or invalid JSON.
    """
    pattern = rf"~~~{re.escape(delimiter)}\s*(.*?)\s*~~~{re.escape(delimiter)}"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        logger.error(
            "governance_json_block_not_found",
            delimiter=delimiter,
            text_length=len(text),
        )
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        logger.error(
            "governance_json_parse_failed",
            delimiter=delimiter,
            error=str(exc),
            raw=match.group(1)[:500],
        )
        return None


def _parse_date(value: str | None) -> date | None:
    """Parse ISO date string to date object. Returns None if null or unparseable."""
    if not value or value.lower() in ("null", "unknown", ""):
        return None
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Phase 1 — Party and role identification
# ---------------------------------------------------------------------------

def run_party_identification(project_id: str, run_id: str) -> None:
    """
    Phase 1 of the governance execution layer.

    Invokes the Compliance SME with the party identification skill.
    Parses the structured JSON output and writes to governance_parties.
    Updates governance_run_log to parties_identified on success, failed on error.

    Called as a FastAPI BackgroundTask from the /run endpoint.
    """
    from src.agents.specialist_config import SPECIALIST_CONFIGS
    from src.agents.base_specialist import BaseSpecialist
    from src.clients import get_supabase_client

    supabase = get_supabase_client()
    now = datetime.now(timezone.utc)

    logger.info(
        "governance_phase1_started",
        project_id=project_id,
        run_id=run_id,
    )

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
        )

        # Parse JSON registry block from findings text
        data = _parse_json_block(findings.findings, "json_registry")
        if data is None:
            _mark_run_failed(supabase, run_id, "Phase 1 SME did not produce a parseable JSON registry block.")
            return

        organisations = data.get("organisations", [])
        individuals = data.get("individuals", [])

        if not organisations and not individuals:
            logger.warning(
                "governance_phase1_empty_registry",
                project_id=project_id,
                run_id=run_id,
            )

        # Write organisations to governance_parties
        for org in organisations:
            canonical_name = org.get("canonical_name", "").strip()
            if not canonical_name:
                continue
            try:
                supabase.table("governance_parties").insert({
                    "project_id": project_id,
                    "entity_type": "organisation",
                    "canonical_name": canonical_name,
                    "aliases": org.get("aliases", []),
                    "contractual_role": org.get("contractual_role") or None,
                    "terminus_node": bool(org.get("terminus_node", False)),
                    "confirmation_status": org.get("confirmation_status", "inferred"),
                }).execute()
            except Exception as exc:
                logger.error(
                    "governance_party_insert_failed",
                    canonical_name=canonical_name,
                    error=str(exc),
                )

        # Write individuals to governance_parties
        for ind in individuals:
            canonical_name = ind.get("canonical_name", "").strip()
            if not canonical_name:
                continue
            try:
                supabase.table("governance_parties").insert({
                    "project_id": project_id,
                    "entity_type": "individual",
                    "canonical_name": canonical_name,
                    "aliases": ind.get("aliases", []),
                    "contractual_role": ind.get("contractual_role") or None,
                    "terminus_node": bool(ind.get("terminus_node", True)),
                    "confirmation_status": ind.get("confirmation_status", "inferred"),
                }).execute()
            except Exception as exc:
                logger.error(
                    "governance_party_insert_failed",
                    canonical_name=canonical_name,
                    error=str(exc),
                )

        total_parties = len(organisations) + len(individuals)

        # Update run_log to parties_identified
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
# Phase 2 — Governance establishment
# ---------------------------------------------------------------------------

def run_governance_establishment(project_id: str, run_id: str) -> None:
    """
    Phase 2 of the governance execution layer.

    Fetches confirmed parties from governance_parties.
    Invokes the Compliance SME with the governance establishment skill.
    Parses the structured JSON output and writes to governance_events.
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
        # Fetch all parties (confirmed + inferred — SME needs full picture)
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

        # Build entity registry text and lookup map
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
        )

        # Parse JSON events block
        data = _parse_json_block(findings.findings, "json_events")
        if data is None:
            _mark_run_failed(supabase, run_id, "Phase 2 SME did not produce a parseable JSON events block.")
            return

        events = data.get("events", [])
        written = 0

        for event in events:
            party_name = event.get("party_canonical_name", "").strip()
            party_id = party_id_map.get(party_name)

            if not party_id:
                logger.warning(
                    "governance_event_party_not_found",
                    party_canonical_name=party_name,
                    project_id=project_id,
                )
                continue

            appointed_by_name = event.get("appointed_by_canonical_name")
            appointed_by_id = party_id_map.get(appointed_by_name) if appointed_by_name else None

            effective_date = _parse_date(event.get("effective_date"))
            end_date = _parse_date(event.get("end_date"))

            if effective_date is None:
                # Still write the event but flag unknown date
                logger.warning(
                    "governance_event_unknown_date",
                    party=party_name,
                    event_type=event.get("event_type"),
                )

            event_type = event.get("event_type", "").strip()
            valid_types = {"appointment","delegation","termination","replacement","modification","suspension"}
            if event_type not in valid_types:
                logger.warning(
                    "governance_event_invalid_type",
                    event_type=event_type,
                    party=party_name,
                )
                continue

            authority_dimension = event.get("authority_dimension", "layer_1")
            valid_dimensions = {"layer_1", "layer_2a", "layer_2b"}
            if authority_dimension not in valid_dimensions:
                authority_dimension = "layer_1"

            extraction_status = event.get("extraction_status", "inferred")
            if extraction_status not in {"confirmed", "inferred", "flagged"}:
                extraction_status = "inferred"

            try:
                supabase.table("governance_events").insert({
                    "project_id": project_id,
                    "event_type": event_type,
                    "effective_date": effective_date.isoformat() if effective_date else datetime.now(timezone.utc).date().isoformat(),
                    "end_date": end_date.isoformat() if end_date else None,
                    "party_id": party_id,
                    "role": event.get("role", "unspecified"),
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

        # Update run_log to complete
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
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", run_id).execute()
        logger.error("governance_run_marked_failed", run_id=run_id, reason=reason)
    except Exception as exc:
        logger.error("governance_run_failed_update_error", run_id=run_id, error=str(exc))
