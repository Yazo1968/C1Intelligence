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
      "canonical_name": "Full formal legal name exactly as in the contract",
      "aliases": ["Short name", "Abbreviation"],
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

Rules:
- confirmation_status: "confirmed" = named explicitly in a retrieved document;
  "inferred" = deduced from context without a retrieved appointment instrument.
- terminus_node: true = cannot issue binding instructions downward;
  false = can instruct, delegate, or direct parties below it.
- Include ALL identified entities. If no individuals are found use [].
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
    Parses the JSON output and writes to governance_parties.
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

        for org in organisations:
            canonical_name = str(org.get("canonical_name", "")).strip()
            if not canonical_name:
                continue
            try:
                supabase.table("governance_parties").insert({
                    "project_id": project_id,
                    "entity_type": "organisation",
                    "canonical_name": canonical_name,
                    "aliases": org.get("aliases") or [],
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

        for ind in individuals:
            canonical_name = str(ind.get("canonical_name", "")).strip()
            if not canonical_name:
                continue
            try:
                supabase.table("governance_parties").insert({
                    "project_id": project_id,
                    "entity_type": "individual",
                    "canonical_name": canonical_name,
                    "aliases": ind.get("aliases") or [],
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
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", run_id).execute()
        logger.error("governance_run_marked_failed", run_id=run_id, reason=reason)
    except Exception as exc:
        logger.error("governance_run_failed_update_error", run_id=run_id, error=str(exc))
