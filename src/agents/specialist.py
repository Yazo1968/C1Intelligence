"""
C1 — Domain Specialist Runner
Shared function that runs any of the six domain specialists.
All specialists use the same tool schema — only the system prompt differs.
"""

from __future__ import annotations

import anthropic

from src.config import CLAUDE_MODEL
from src.logging_config import get_logger
from src.agents.models import (
    AgentError,
    KeyFinding,
    RetrievedChunk,
    SourceCitation,
    SpecialistFinding,
)

logger = get_logger(__name__)

SPECIALIST_TOOL = {
    "name": "specialist_finding",
    "description": "Return a structured finding from a domain specialist analysis.",
    "input_schema": {
        "type": "object",
        "properties": {
            "analysis": {
                "type": "string",
                "description": "Domain-specific analysis of the query based on retrieved documents.",
            },
            "key_findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "statement": {
                            "type": "string",
                            "description": "A factual finding supported by the documents.",
                        },
                        "citations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "document_reference": {
                                        "type": "string",
                                        "description": "Reference number or title of the source document.",
                                    },
                                    "document_type": {
                                        "type": ["string", "null"],
                                        "description": "Type of the source document from the taxonomy.",
                                    },
                                    "document_date": {
                                        "type": ["string", "null"],
                                        "description": "Date of the source document (YYYY-MM-DD).",
                                    },
                                    "excerpt": {
                                        "type": "string",
                                        "description": "The specific text from the document supporting this finding.",
                                    },
                                },
                                "required": ["document_reference", "excerpt"],
                            },
                            "description": "Source citations for this finding. Every finding MUST have at least one citation.",
                        },
                    },
                    "required": ["statement", "citations"],
                },
                "description": "List of key findings, each supported by document citations.",
            },
        },
        "required": ["analysis", "key_findings"],
    },
}


def run_specialist(
    anthropic_client: anthropic.Anthropic,
    domain: str,
    query_text: str,
    chunks: list[RetrievedChunk],
    system_prompt: str,
) -> SpecialistFinding:
    """
    Run a single domain specialist. All six specialists use this function
    with different system prompts.

    Returns a SpecialistFinding with analysis, key findings, and citations.
    """
    formatted_chunks = _format_chunks_for_specialist(chunks)

    user_message = (
        f"QUERY: {query_text}\n\n"
        f"RETRIEVED DOCUMENTS:\n{formatted_chunks}\n\n"
        f"Analyze the retrieved documents to answer the query within your domain. "
        f"Every claim must cite a specific document."
    )

    try:
        response = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            system=system_prompt,
            tools=[SPECIALIST_TOOL],
            tool_choice={"type": "tool", "name": "specialist_finding"},
            messages=[{"role": "user", "content": user_message}],
        )
    except Exception as exc:
        raise AgentError(
            stage=f"specialist_{domain}",
            message=f"Claude specialist call failed for {domain}: {exc}",
        ) from exc

    tool_result = _extract_tool_result(response, "specialist_finding", domain)

    finding = _parse_specialist_result(domain, tool_result)

    logger.info(
        "specialist_completed",
        domain=domain,
        finding_count=len(finding.key_findings),
    )

    return finding


def _format_chunks_for_specialist(chunks: list[RetrievedChunk]) -> str:
    """Format retrieved chunks into a numbered list for the specialist's user message."""
    if not chunks:
        return "(No documents retrieved)"

    lines: list[str] = []
    for idx, chunk in enumerate(chunks, 1):
        header_parts: list[str] = []
        if chunk.document_reference:
            header_parts.append(f"Ref: {chunk.document_reference}")
        if chunk.document_type:
            header_parts.append(f"Type: {chunk.document_type}")
        if chunk.document_date:
            header_parts.append(f"Date: {chunk.document_date}")
        header = " | ".join(header_parts) if header_parts else "Unknown source"

        lines.append(f"--- Document {idx} [{header}] ---")
        lines.append(chunk.text)
        lines.append("")

    return "\n".join(lines)


def _parse_specialist_result(domain: str, tool_result: dict) -> SpecialistFinding:
    """Parse Claude's tool_use output into a SpecialistFinding model."""
    analysis = tool_result.get("analysis", "")
    raw_findings = tool_result.get("key_findings", [])

    key_findings: list[KeyFinding] = []
    for rf in raw_findings:
        citations: list[SourceCitation] = []
        for rc in rf.get("citations", []):
            citations.append(
                SourceCitation(
                    document_reference=rc.get("document_reference", ""),
                    document_type=rc.get("document_type"),
                    document_date=rc.get("document_date"),
                    excerpt=rc.get("excerpt", ""),
                )
            )
        key_findings.append(
            KeyFinding(
                statement=rf.get("statement", ""),
                citations=citations,
            )
        )

    return SpecialistFinding(
        domain=domain,
        analysis=analysis,
        key_findings=key_findings,
    )


def _extract_tool_result(
    response: anthropic.types.Message, tool_name: str, domain: str
) -> dict:
    """Extract the input dict from a tool_use content block."""
    for block in response.content:
        if block.type == "tool_use" and block.name == tool_name:
            return block.input

    raise AgentError(
        stage=f"specialist_{domain}",
        message=f"Claude response did not contain a '{tool_name}' tool call.",
    )
