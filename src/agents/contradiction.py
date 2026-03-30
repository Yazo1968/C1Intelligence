"""
C1 — Contradiction Detection
Scans specialist findings for conflicting values across documents.
Writes detected contradictions to the contradiction_flags table (non-blocking).
"""

from __future__ import annotations

import uuid

import anthropic
from supabase import Client as SupabaseClient

from src.config import CLAUDE_MODEL
from src.logging_config import get_logger
from src.agents.models import (
    AgentError,
    ContradictionFlag,
    SpecialistFinding,
    SpecialistFindings,
)
from src.agents.prompts import CONTRADICTION_SYSTEM_PROMPT

logger = get_logger(__name__)

CONTRADICTION_TOOL = {
    "name": "contradiction_report",
    "description": "Report contradictions found across specialist findings from different documents.",
    "input_schema": {
        "type": "object",
        "properties": {
            "contradictions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "field_name": {
                            "type": "string",
                            "description": "The specific field or fact that is contradicted.",
                        },
                        "document_a_reference": {
                            "type": "string",
                            "description": "Reference of the first document.",
                        },
                        "value_a": {
                            "type": "string",
                            "description": "The value stated in the first document.",
                        },
                        "document_b_reference": {
                            "type": "string",
                            "description": "Reference of the second document.",
                        },
                        "value_b": {
                            "type": "string",
                            "description": "The value stated in the second document.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Explanation of the contradiction.",
                        },
                    },
                    "required": [
                        "field_name",
                        "document_a_reference",
                        "value_a",
                        "document_b_reference",
                        "value_b",
                        "description",
                    ],
                },
                "description": "List of detected contradictions. Empty if none found.",
            },
        },
        "required": ["contradictions"],
    },
}


def detect_contradictions(
    anthropic_client: anthropic.Anthropic,
    findings: list[SpecialistFindings] | list[SpecialistFinding],
) -> list[ContradictionFlag]:
    """
    Scan all specialist findings for conflicting values across documents.
    Uses Claude to detect contradictions.

    Accepts both SpecialistFindings (Phase 2+) and SpecialistFinding (v1 legacy).
    Returns list of ContradictionFlag (empty if none found).
    """
    # Need at least 2 findings with sources to have a contradiction
    if len(findings) < 2:
        return []

    # Check for sufficient source material
    if isinstance(findings[0], SpecialistFindings):
        has_sources = any(f.sources_used for f in findings)
    else:
        has_sources = any(
            kf.citations for f in findings for kf in f.key_findings
        )
    if not has_sources:
        return []

    findings_text = _format_findings_for_detection(findings)

    try:
        response = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            system=CONTRADICTION_SYSTEM_PROMPT,
            tools=[CONTRADICTION_TOOL],
            tool_choice={"type": "tool", "name": "contradiction_report"},
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Scan the following specialist findings for contradictions "
                        "between documents:\n\n"
                        f"{findings_text}"
                    ),
                }
            ],
        )
    except Exception as exc:
        logger.error("contradiction_detection_failed", error=str(exc))
        return []

    try:
        tool_result = _extract_tool_result(response, "contradiction_report")
    except AgentError:
        logger.error("contradiction_tool_result_missing")
        return []

    raw_contradictions = tool_result.get("contradictions", [])
    contradictions: list[ContradictionFlag] = []

    for rc in raw_contradictions:
        contradictions.append(
            ContradictionFlag(
                field_name=rc.get("field_name", ""),
                document_a_reference=rc.get("document_a_reference", ""),
                value_a=rc.get("value_a", ""),
                document_b_reference=rc.get("document_b_reference", ""),
                value_b=rc.get("value_b", ""),
                description=rc.get("description", ""),
            )
        )

    logger.info(
        "contradictions_detected",
        count=len(contradictions),
    )

    return contradictions


def write_contradiction_flags(
    supabase_client: SupabaseClient,
    project_id: uuid.UUID,
    contradictions: list[ContradictionFlag],
    doc_reference_to_id: dict[str, uuid.UUID],
) -> None:
    """
    Write detected contradictions to the contradiction_flags table.

    Non-blocking: if any individual write fails, log the error and continue.
    The response still returns to the user regardless.

    doc_reference_to_id maps document references (strings) to UUIDs.
    """
    if not contradictions:
        return

    for contradiction in contradictions:
        doc_a_id = doc_reference_to_id.get(contradiction.document_a_reference)
        doc_b_id = doc_reference_to_id.get(contradiction.document_b_reference)

        if doc_a_id is None or doc_b_id is None:
            logger.warning(
                "contradiction_write_skipped_unresolved_refs",
                doc_a_ref=contradiction.document_a_reference,
                doc_b_ref=contradiction.document_b_reference,
                doc_a_id_resolved=doc_a_id is not None,
                doc_b_id_resolved=doc_b_id is not None,
            )
            continue

        row = {
            "project_id": str(project_id),
            "document_a_id": str(doc_a_id),
            "document_b_id": str(doc_b_id),
            "field_name": contradiction.field_name,
            "description": contradiction.description,
        }

        try:
            supabase_client.table("contradiction_flags").insert(row).execute()
        except Exception as exc:
            logger.error(
                "contradiction_flag_write_failed",
                field_name=contradiction.field_name,
                error=str(exc),
            )
            # Non-blocking — continue with next contradiction

    logger.info(
        "contradiction_flags_written",
        project_id=str(project_id),
        attempted=len(contradictions),
    )


def _format_findings_for_detection(
    findings: list[SpecialistFindings] | list[SpecialistFinding],
) -> str:
    """Format all specialist findings into text for contradiction scanning."""
    sections: list[str] = []

    for finding in findings:
        if isinstance(finding, SpecialistFindings):
            # Phase 2+ format: findings text + sources_used IDs
            lines: list[str] = [f"=== {finding.domain.upper()} ==="]
            lines.append(f"\n{finding.findings}")
            if finding.sources_used:
                lines.append("\nSources referenced:")
                for doc_id in finding.sources_used:
                    lines.append(f"  - Document: {doc_id}")
            sections.append("\n".join(lines))
        else:
            # v1 legacy format: key_findings with citations
            lines = [f"=== {finding.domain.upper()} ==="]
            for kf in finding.key_findings:
                lines.append(f"\nFinding: {kf.statement}")
                for cite in kf.citations:
                    cite_parts: list[str] = []
                    if cite.document_reference:
                        cite_parts.append(f"Ref: {cite.document_reference}")
                    if cite.document_type:
                        cite_parts.append(f"Type: {cite.document_type}")
                    if cite.document_date:
                        cite_parts.append(f"Date: {cite.document_date}")
                    cite_header = " | ".join(cite_parts) if cite_parts else "Unknown"
                    lines.append(f"  Source [{cite_header}]: {cite.excerpt}")
            sections.append("\n".join(lines))

    return "\n\n".join(sections)


def _extract_tool_result(response: anthropic.types.Message, tool_name: str) -> dict:
    """Extract the input dict from a tool_use content block."""
    for block in response.content:
        if block.type == "tool_use" and block.name == tool_name:
            return block.input

    raise AgentError(
        stage="contradiction_detection",
        message=f"Claude response did not contain a '{tool_name}' tool call.",
    )
