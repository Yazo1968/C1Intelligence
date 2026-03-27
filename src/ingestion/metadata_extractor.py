"""
C1 — Claude-Based Metadata Extraction
Extracts structured metadata fields from document text using Claude tool_use.
"""

from __future__ import annotations

import anthropic

from src.config import CLAUDE_MODEL
from src.logging_config import get_logger
from src.ingestion.models import ExtractedMetadata, IngestionError

logger = get_logger(__name__)

EXTRACTION_SYSTEM_PROMPT = """You are a construction document metadata extraction specialist for the GCC market (UAE, Saudi Arabia, Qatar).

You extract structured metadata from construction documents with precision.

DOCUMENT TYPE: {document_type_name}
CATEGORY: {category}

TASK:
Extract the following fields from the document text. If a field cannot be found in the document, return null for that field.

FIELDS:
- document_date: The primary date of the document (ISO format YYYY-MM-DD)
- document_reference_number: The document's reference, serial, or tracking number
- issuing_party_name: The organization that issued or authored the document
- receiving_party_name: The organization the document is addressed to
- fidic_clause_ref: Any FIDIC sub-clause reference (e.g., "Sub-Clause 20.1", "Clause 8.4")
- language: The language of the document ("EN", "AR", "EN-AR", or "EN-AR-CONFLICT")
- revision_number: The revision or version number if stated
- time_bar_deadline: If this is a notice with a contractual time bar, the deadline date (ISO format YYYY-MM-DD)
- document_status: The stated status (e.g., "EXECUTED", "DRAFT", "SUPERSEDED", "DISPUTED", "PENDING", "REJECTED", "EXPIRED")

FIDIC AWARENESS:
- If a FIDIC clause is referenced, note the sub-clause number exactly as stated.
- Sub-clause numbering differs between FIDIC 1999 and 2017 editions:
  - 8.4 [1999] = Extension of Time; 8.5 [2017] = Extension of Time
  - 3.5 [1999] = Engineer's Determination; 3.7 [2017] = Engineer's Determination
  - 20.1 [1999] = Notice of Claim; 20.2.1 [2017] = Notice of Claim
  - 20.4 [1999] = DAB Decision; 21.4 [2017] = DAAB Decision
- Notice of Claim has a 28-day time bar. If this is a claim notice and document_date is found, calculate time_bar_deadline = document_date + 28 days.

EXTRACTION RULES:
- Extract values exactly as they appear in the document. Do not infer or fabricate.
- For party names, use the full legal or organizational name as stated.
- For dates, convert to ISO format YYYY-MM-DD regardless of how they appear in the document.
- If the document is bilingual (English-Arabic), set language to "EN-AR". If the two languages contain conflicting content, set to "EN-AR-CONFLICT"."""

EXTRACTION_TOOL = {
    "name": "extract_metadata",
    "description": "Extract structured metadata from a construction document.",
    "input_schema": {
        "type": "object",
        "properties": {
            "document_date": {
                "type": ["string", "null"],
                "description": "Document date in YYYY-MM-DD format, or null if not found.",
            },
            "document_reference_number": {
                "type": ["string", "null"],
                "description": "Document reference/serial number, or null if not found.",
            },
            "issuing_party_name": {
                "type": ["string", "null"],
                "description": "Name of the issuing organization, or null if not found.",
            },
            "receiving_party_name": {
                "type": ["string", "null"],
                "description": "Name of the receiving organization, or null if not found.",
            },
            "fidic_clause_ref": {
                "type": ["string", "null"],
                "description": "FIDIC sub-clause reference, or null if not found.",
            },
            "language": {
                "type": ["string", "null"],
                "description": "Document language: EN, AR, EN-AR, or EN-AR-CONFLICT.",
            },
            "revision_number": {
                "type": ["string", "null"],
                "description": "Revision or version number, or null if not found.",
            },
            "time_bar_deadline": {
                "type": ["string", "null"],
                "description": "Time bar deadline in YYYY-MM-DD format, or null if not applicable.",
            },
            "document_status": {
                "type": ["string", "null"],
                "description": "Document status (EXECUTED, DRAFT, SUPERSEDED, etc.), or null if not found.",
            },
        },
        "required": [
            "document_date",
            "document_reference_number",
            "issuing_party_name",
            "receiving_party_name",
            "fidic_clause_ref",
            "language",
            "revision_number",
            "time_bar_deadline",
            "document_status",
        ],
    },
}


def extract_metadata(
    anthropic_client: anthropic.Anthropic,
    document_text: str,
    filename: str,
    document_type_name: str,
    category: str,
) -> ExtractedMetadata:
    """
    Send document text to Claude for metadata extraction.
    Uses tool_use to force structured JSON output.

    Returns ExtractedMetadata. Fields not found in the document are None.
    Raises IngestionError if the Claude API call fails.
    """
    system_prompt = EXTRACTION_SYSTEM_PROMPT.format(
        document_type_name=document_type_name,
        category=category,
    )

    # Use more text for extraction than classification — metadata may be
    # scattered throughout the document (headers, footers, signature blocks)
    truncated_text = document_text[:12000]
    if len(document_text) > 12000:
        truncated_text += "\n\n[... document truncated for metadata extraction ...]"

    user_message = f"FILENAME: {filename}\n\nDOCUMENT TEXT:\n{truncated_text}"

    try:
        response = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            system=system_prompt,
            tools=[EXTRACTION_TOOL],
            tool_choice={"type": "tool", "name": "extract_metadata"},
            messages=[{"role": "user", "content": user_message}],
        )
    except Exception as exc:
        raise IngestionError(
            stage="metadata_extraction",
            message=f"Claude API call failed: {exc}",
        ) from exc

    tool_result = _extract_tool_result(response, "extract_metadata")

    result = ExtractedMetadata(
        document_date=_parse_date_or_none(tool_result.get("document_date")),
        document_reference_number=tool_result.get("document_reference_number"),
        issuing_party_name=tool_result.get("issuing_party_name"),
        receiving_party_name=tool_result.get("receiving_party_name"),
        fidic_clause_ref=tool_result.get("fidic_clause_ref"),
        language=tool_result.get("language"),
        revision_number=tool_result.get("revision_number"),
        time_bar_deadline=_parse_date_or_none(tool_result.get("time_bar_deadline")),
        document_status=tool_result.get("document_status"),
    )

    logger.info(
        "metadata_extracted",
        filename=filename,
        fields_found=sum(
            1 for v in result.model_dump().values() if v is not None
        ),
    )

    return result


def _extract_tool_result(response: anthropic.types.Message, tool_name: str) -> dict:
    """Extract the input dict from a tool_use content block."""
    for block in response.content:
        if block.type == "tool_use" and block.name == tool_name:
            return block.input

    raise IngestionError(
        stage="metadata_extraction",
        message=f"Claude response did not contain a '{tool_name}' tool call.",
    )


def _parse_date_or_none(value: str | None) -> str | None:
    """
    Return the date string if it looks like a valid ISO date, otherwise None.
    We store as date in the DB — Pydantic model handles the conversion.
    """
    if not value or not isinstance(value, str):
        return None
    # Basic validation: must be YYYY-MM-DD format
    parts = value.split("-")
    if len(parts) != 3:
        return None
    try:
        int(parts[0])
        int(parts[1])
        int(parts[2])
    except ValueError:
        return None
    return value
