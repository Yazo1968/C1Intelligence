"""
C1 — Base Specialist Agent
Shared agentic template for all six domain specialists.
Uses Anthropic SDK native tool_use for the agentic loop.

The loop: assess -> tool call if needed -> reason -> return.
Claude decides when to call tools. The loop inspects stop_reason:
- "tool_use": extract tool block, execute it, append result, loop
- "end_turn": extract text response, parse into SpecialistFindings, return

All specialists share this class. Domain behaviour comes from skill files
loaded dynamically by SkillLoader. No subclassing required.
"""

from __future__ import annotations

import json

from src.clients import get_anthropic_client
from src.config import CLAUDE_MODEL
from src.logging_config import get_logger
from src.agents.models import SpecialistFindings
from src.agents.skill_loader import SkillLoader
from src.agents.specialist_config import SpecialistConfig
from src.agents.tools import TOOL_DEFINITIONS, execute_tool

logger = get_logger(__name__)

# System prompt prefix applied to every specialist
_SYSTEM_PROMPT_PREFIX: str = """You are a specialist agent in the C1 Construction Documentation Intelligence Platform.
Your domain is: {domain}

Your role is to analyse retrieved document chunks and answer the user's query
from the perspective of your domain expertise. You have access to tools to
search for additional information if the initially provided context is insufficient.

RULES:
- Base your analysis ONLY on evidence from the documents. Never speculate.
- If two documents conflict on the same field, surface BOTH values. Never resolve contradictions.
- Cite specific documents by their document_id when making claims.
- If you lack sufficient evidence, state so clearly. Do not fabricate.
- When calling tools, be specific in your queries to retrieve relevant results.

At the end of your analysis, you MUST output a JSON block in the following format
(wrapped in ```json fences):

```json
{{
    "findings": "Your detailed analysis text here",
    "confidence": "GREEN|AMBER|RED|GREY",
    "sources_used": ["document-id-1", "document-id-2"],
    "flagged_contradictions": ["contradiction-flag-id-1"]
}}
```

Confidence definitions:
- GREEN: All retrieved documents are consistent on the queried field.
- AMBER: Field is present but only partially supported, or only one document covers it.
- RED: Two or more documents contain conflicting values for the same field.
- GREY: No relevant documents found — warehouse has no relevant data for this query.

"""

_ROUND_1_CONTEXT_HEADER: str = """
--- ROUND 1 FINDINGS (from other specialists — use as additional context) ---

{findings}

--- END ROUND 1 FINDINGS ---
"""


class BaseSpecialist:
    """
    Shared agentic loop for all domain specialists.

    Instantiate with a SpecialistConfig. Call run() with a query and context.
    The agent will reason, optionally call tools, and return SpecialistFindings.
    """

    def __init__(self, config: SpecialistConfig) -> None:
        self._config = config
        self._skill_loader = SkillLoader()

    @property
    def domain(self) -> str:
        """The specialist's domain name."""
        return self._config.domain

    @property
    def round_assignment(self) -> int:
        """Which orchestrator round this specialist runs in."""
        return self._config.round_assignment

    def run(
        self,
        query: str,
        project_id: str,
        retrieved_chunks: list[dict],
        round_1_findings: dict | None = None,
    ) -> SpecialistFindings:
        """
        Execute the agentic loop for this specialist.

        Args:
            query: The user's original query text.
            project_id: The project UUID string.
            retrieved_chunks: Pre-retrieved chunks from the retrieval layer.
            round_1_findings: Structured findings from Round 1 specialists
                (only provided to Round 2 specialists).

        Returns:
            SpecialistFindings with domain analysis, confidence, and sources.
        """
        logger.info(
            "specialist_run_started",
            domain=self._config.domain,
            project_id=project_id,
            round_assignment=self._config.round_assignment,
            max_tool_rounds=self._config.max_tool_rounds,
        )

        # --- Build system prompt from skills + playbook ---
        skill_content = self._skill_loader.load(self._config.domain, project_id)
        system_prompt = _SYSTEM_PROMPT_PREFIX.format(domain=self._config.domain)
        if skill_content:
            system_prompt += f"\n\n{skill_content}"

        # --- Build user message ---
        user_message = self._build_user_message(
            query, retrieved_chunks, round_1_findings
        )

        # --- Agentic loop ---
        anthropic_client = get_anthropic_client()
        messages: list[dict] = [{"role": "user", "content": user_message}]
        tools_called: list[str] = []
        tool_round: int = 0

        while tool_round <= self._config.max_tool_rounds:
            try:
                # On final round (max reached), call without tools to force text response
                call_kwargs: dict = {
                    "model": CLAUDE_MODEL,
                    "max_tokens": 4000,
                    "system": system_prompt,
                    "messages": messages,
                }
                if tool_round < self._config.max_tool_rounds:
                    call_kwargs["tools"] = TOOL_DEFINITIONS

                response = anthropic_client.messages.create(**call_kwargs)

            except Exception as exc:
                logger.error(
                    "specialist_api_error",
                    domain=self._config.domain,
                    project_id=project_id,
                    tool_round=tool_round,
                    error=str(exc),
                )
                return self._error_findings(
                    "Specialist failed to complete analysis due to API error.",
                    tools_called,
                )

            # --- Handle stop_reason ---
            if response.stop_reason == "tool_use":
                tool_round += 1

                # Extract tool use block(s) from response content
                tool_use_blocks = [
                    block for block in response.content if block.type == "tool_use"
                ]
                text_blocks = [
                    block for block in response.content if block.type == "text"
                ]

                # Append assistant message with full content
                messages.append({"role": "assistant", "content": response.content})

                # Execute each tool and build tool results
                tool_results: list[dict] = []
                for tool_block in tool_use_blocks:
                    tool_name = tool_block.name
                    tool_input = tool_block.input
                    tools_called.append(tool_name)

                    logger.info(
                        "specialist_tool_call",
                        domain=self._config.domain,
                        tool_name=tool_name,
                        tool_round=tool_round,
                    )

                    result = execute_tool(tool_name, tool_input, project_id)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_block.id,
                        "content": json.dumps(result, default=str),
                    })

                # Append tool results as user message
                messages.append({"role": "user", "content": tool_results})
                continue

            elif response.stop_reason == "end_turn":
                # Extract text response
                text_content = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        text_content += block.text

                return self._parse_findings(text_content, tools_called)

            else:
                # Unexpected stop_reason
                logger.warning(
                    "specialist_unexpected_stop_reason",
                    domain=self._config.domain,
                    stop_reason=response.stop_reason,
                )
                text_content = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        text_content += block.text

                if text_content:
                    return self._parse_findings(text_content, tools_called)

                return self._error_findings(
                    f"Unexpected stop_reason: {response.stop_reason}",
                    tools_called,
                )

        # Should not reach here, but safety net
        return self._error_findings(
            "Specialist exhausted all tool rounds without producing findings.",
            tools_called,
        )

    def _build_user_message(
        self,
        query: str,
        retrieved_chunks: list[dict],
        round_1_findings: dict | None,
    ) -> str:
        """Build the user message from query, Layer 1/Layer 2 chunks, and optional Round 1 findings."""
        parts: list[str] = [f"QUERY: {query}"]

        # Separate Layer 1 (project) and Layer 2 (reference) chunks
        layer1_chunks = [c for c in retrieved_chunks if not c.get("is_reference")]
        layer2_chunks = [c for c in retrieved_chunks if c.get("is_reference")]

        # Layer 1 — Project Document Chunks
        if layer1_chunks:
            parts.append("\n--- PROJECT DOCUMENT CHUNKS (Layer 1) ---\n")
            for i, chunk in enumerate(layer1_chunks):
                doc_id = chunk.get("document_id", "unknown")
                content = chunk.get("content", "")
                chunk_idx = chunk.get("chunk_index", i)
                parts.append(
                    f"[Chunk {chunk_idx} | Document: {doc_id}]\n{content}\n"
                )
            parts.append("--- END PROJECT DOCUMENT CHUNKS ---")
        elif not layer2_chunks:
            # Only show "no chunks" message if BOTH layers are empty
            parts.append(
                "\n[No document chunks were retrieved for this query. "
                "Use the search_chunks tool to find relevant documents.]\n"
            )

        # Layer 2 — Reference Document Chunks (omit section entirely if empty)
        if layer2_chunks:
            parts.append("\n--- REFERENCE DOCUMENT CHUNKS (Layer 2 — Standards and Regulations) ---\n")
            for chunk in layer2_chunks:
                doc_ref = chunk.get("document_reference", "unknown")
                doc_type = chunk.get("document_type", "unknown")
                content = chunk.get("content", "")
                parts.append(
                    f"[Reference: {doc_ref} | Standard: {doc_type}]\n{content}\n"
                )
            parts.append("--- END REFERENCE DOCUMENT CHUNKS ---")

        # Round 1 findings (for Round 2 specialists only)
        if round_1_findings:
            findings_text = json.dumps(round_1_findings, indent=2, default=str)
            parts.append(_ROUND_1_CONTEXT_HEADER.format(findings=findings_text))

        return "\n".join(parts)

    def _parse_findings(
        self, text: str, tools_called: list[str]
    ) -> SpecialistFindings:
        """
        Parse the specialist's text response into SpecialistFindings.
        Uses the narrative text before the JSON fence as findings.
        Falls back gracefully when the JSON block is missing or malformed.
        """
        json_block: dict = {}
        text_before_json = text

        try:
            json_start = text.index("```json")
            json_end = text.index("```", json_start + 7)
            json_str = text[json_start + 7 : json_end].strip()
            json_block = json.loads(json_str)
            # Use only the narrative before the JSON fence
            text_before_json = text[:json_start].strip()
        except (ValueError, json.JSONDecodeError) as exc:
            logger.warning(
                "specialist_json_parse_failed",
                domain=self._config.domain,
                error=str(exc),
            )

        if json_block:
            # Prefer the narrative text before the JSON fence.
            # Fall back to json_block["findings"] only if narrative is empty.
            findings_text = text_before_json or json_block.get("findings", text)
            confidence = json_block.get("confidence", "AMBER")
            if confidence not in ("GREEN", "AMBER", "RED", "GREY"):
                confidence = "AMBER"
            sources_used = json_block.get("sources_used", [])
            flagged = json_block.get("flagged_contradictions", [])
        else:
            # JSON completely absent or unparseable — use text before any JSON-like
            # content to avoid exposing raw JSON in the output
            findings_text = text_before_json
            confidence = "AMBER"
            sources_used = []
            flagged = []

        return SpecialistFindings(
            domain=self._config.domain,
            findings=findings_text,
            confidence=confidence,
            sources_used=sources_used,
            tools_called=tools_called,
            round_number=self._config.round_assignment,
            flagged_contradictions=flagged,
        )

    def _error_findings(
        self, message: str, tools_called: list[str]
    ) -> SpecialistFindings:
        """Return a GREY-confidence findings object for error cases."""
        return SpecialistFindings(
            domain=self._config.domain,
            findings=message,
            confidence="GREY",
            sources_used=[],
            tools_called=tools_called,
            round_number=self._config.round_assignment,
            flagged_contradictions=[],
        )
