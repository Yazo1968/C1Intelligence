"""
C1 — Claude-Based Document Classification
Classifies documents against the 176-type taxonomy using Claude tool_use
for structured output. Also extracts text previews from Gemini-uploaded files.
"""

from __future__ import annotations

import json

import anthropic
from google import genai
from google.genai import types as genai_types

from src.config import CLAUDE_MODEL, CLASSIFICATION_CONFIDENCE_THRESHOLD, GEMINI_MODEL
from src.logging_config import get_logger
from src.ingestion.models import ClassificationResult, IngestionError

logger = get_logger(__name__)

CLASSIFICATION_SYSTEM_PROMPT = """You are a construction document classification specialist for the GCC market (UAE, Saudi Arabia, Qatar).

You classify documents against a predefined taxonomy of 176 types across 10 categories.

TAXONOMY:
{taxonomy}

TASK:
Analyze the document text below and classify it against exactly one type from the taxonomy.

RULES:
- Return exactly one document type ID from the taxonomy.
- Provide a confidence score between 0.0 and 1.0:
  - 1.0 = absolute certainty the document matches this type.
  - 0.75+ = confident match.
  - Below 0.75 = uncertain, will be queued for human review.
- The document content is the primary signal. The filename is a weak secondary signal.
- If the document could match multiple types, choose the most specific match and explain alternatives in your reasoning.
- If you cannot determine the type at all, pick the closest match and give a low confidence score.
{user_type_instruction}"""

USER_TYPE_INSTRUCTION_TEMPLATE = """
IMPORTANT — USER PRE-SELECTION:
The user selected document type ID {type_id} ("{type_name}") at upload time.
Validate whether the document content matches this selection.
If it matches, use it and assign high confidence.
If it does not match, classify independently and explain the mismatch in your reasoning."""

CLASSIFICATION_TOOL = {
    "name": "classify_document",
    "description": "Classify a construction document against the C1 taxonomy.",
    "input_schema": {
        "type": "object",
        "properties": {
            "document_type_id": {
                "type": "integer",
                "description": "The ID of the matching document type from the taxonomy.",
            },
            "document_type_name": {
                "type": "string",
                "description": "The name of the matching document type.",
            },
            "category": {
                "type": "string",
                "description": "The category of the matching document type.",
            },
            "tier": {
                "type": "integer",
                "description": "The tier (1, 2, or 3) of the matching document type.",
            },
            "confidence": {
                "type": "number",
                "description": "Confidence score between 0.0 and 1.0.",
            },
            "reasoning": {
                "type": "string",
                "description": "Explanation for the classification decision.",
            },
        },
        "required": [
            "document_type_id",
            "document_type_name",
            "category",
            "tier",
            "confidence",
            "reasoning",
        ],
    },
}


def extract_text_preview(
    gemini_client: genai.Client,
    gemini_file_uri: str,
) -> str:
    """
    Use Gemini generate_content with an uploaded file's full URI to extract
    a text representation of the document for Claude to classify.

    Args:
        gemini_file_uri: Full Gemini file URI
            (e.g., "https://generativelanguage.googleapis.com/v1beta/files/abc123").

    Returns the extracted text string.
    Raises IngestionError if extraction fails.
    """
    try:
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                genai_types.Content(
                    parts=[
                        genai_types.Part(
                            file_data=genai_types.FileData(file_uri=gemini_file_uri)
                        ),
                        genai_types.Part(
                            text=(
                                "Extract the full text content of this document. "
                                "Return only the raw text, preserving the structure "
                                "(headings, paragraphs, tables). No commentary or summary."
                            )
                        ),
                    ]
                )
            ],
        )
    except Exception as exc:
        raise IngestionError(
            stage="text_extraction",
            message=f"Failed to extract text from Gemini file {gemini_file_uri}: {exc}",
        ) from exc

    text = response.text
    if not text or not text.strip():
        raise IngestionError(
            stage="text_extraction",
            message=f"Gemini returned empty text for file {gemini_file_uri}.",
        )

    logger.info(
        "text_extracted",
        gemini_file_uri=gemini_file_uri,
        text_length=len(text),
    )

    return text


def classify_document(
    anthropic_client: anthropic.Anthropic,
    document_text: str,
    filename: str,
    taxonomy_prompt: str,
    user_selected_type_id: int | None = None,
    user_selected_type_name: str | None = None,
) -> ClassificationResult:
    """
    Send document text to Claude for classification against the taxonomy.
    Uses tool_use to force structured JSON output.

    Returns ClassificationResult with needs_queue set based on confidence threshold.
    Raises IngestionError if the Claude API call fails or response is unparseable.
    """
    # Build the user type instruction if a pre-selection was made
    user_type_instruction = ""
    if user_selected_type_id is not None and user_selected_type_name is not None:
        user_type_instruction = USER_TYPE_INSTRUCTION_TEMPLATE.format(
            type_id=user_selected_type_id,
            type_name=user_selected_type_name,
        )

    system_prompt = CLASSIFICATION_SYSTEM_PROMPT.format(
        taxonomy=taxonomy_prompt,
        user_type_instruction=user_type_instruction,
    )

    # Truncate document text to avoid excessive token usage
    # First ~8000 chars should be sufficient for classification
    truncated_text = document_text[:8000]
    if len(document_text) > 8000:
        truncated_text += "\n\n[... document truncated for classification ...]"

    user_message = f"FILENAME: {filename}\n\nDOCUMENT TEXT:\n{truncated_text}"

    try:
        response = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            system=system_prompt,
            tools=[CLASSIFICATION_TOOL],
            tool_choice={"type": "tool", "name": "classify_document"},
            messages=[{"role": "user", "content": user_message}],
        )
    except Exception as exc:
        raise IngestionError(
            stage="classification",
            message=f"Claude API call failed: {exc}",
        ) from exc

    # Extract the tool use result
    tool_result = _extract_tool_result(response, "classify_document")

    confidence = float(tool_result["confidence"])
    needs_queue = confidence < CLASSIFICATION_CONFIDENCE_THRESHOLD

    result = ClassificationResult(
        document_type_id=int(tool_result["document_type_id"]),
        document_type_name=str(tool_result["document_type_name"]),
        category=str(tool_result["category"]),
        tier=int(tool_result["tier"]),
        confidence=confidence,
        reasoning=str(tool_result["reasoning"]),
        needs_queue=needs_queue,
    )

    logger.info(
        "document_classified",
        filename=filename,
        document_type_id=result.document_type_id,
        document_type_name=result.document_type_name,
        confidence=result.confidence,
        needs_queue=result.needs_queue,
    )

    return result


def _extract_tool_result(response: anthropic.types.Message, tool_name: str) -> dict:
    """Extract the input dict from a tool_use content block in Claude's response."""
    for block in response.content:
        if block.type == "tool_use" and block.name == tool_name:
            return block.input

    raise IngestionError(
        stage="classification",
        message=f"Claude response did not contain a '{tool_name}' tool call.",
    )
