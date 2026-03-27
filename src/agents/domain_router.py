"""
C1 — Domain Router
Uses Claude to identify which of the six specialist domains are relevant to a query.
"""

from __future__ import annotations

import anthropic

from src.config import CLAUDE_MODEL
from src.logging_config import get_logger
from src.agents.models import AgentError, DomainIdentification
from src.agents.prompts import ALL_DOMAINS, DOMAIN_ROUTER_SYSTEM_PROMPT

logger = get_logger(__name__)

DOMAIN_ROUTER_TOOL = {
    "name": "identify_domains",
    "description": "Identify which specialist domains are relevant to a construction project query.",
    "input_schema": {
        "type": "object",
        "properties": {
            "domains": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ALL_DOMAINS,
                },
                "description": "Which domains are relevant to this query.",
            },
            "reasoning": {
                "type": "string",
                "description": "Why these domains were selected.",
            },
        },
        "required": ["domains", "reasoning"],
    },
}


def identify_domains(
    anthropic_client: anthropic.Anthropic,
    query_text: str,
) -> DomainIdentification:
    """
    Ask Claude which of the six specialist domains are relevant to the query.
    Returns DomainIdentification with list of domain names and reasoning.
    """
    try:
        response = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=512,
            system=DOMAIN_ROUTER_SYSTEM_PROMPT,
            tools=[DOMAIN_ROUTER_TOOL],
            tool_choice={"type": "tool", "name": "identify_domains"},
            messages=[{"role": "user", "content": query_text}],
        )
    except Exception as exc:
        raise AgentError(
            stage="domain_routing",
            message=f"Claude domain routing failed: {exc}",
        ) from exc

    tool_result = _extract_tool_result(response, "identify_domains")

    domains = tool_result.get("domains", [])
    reasoning = tool_result.get("reasoning", "")

    # Validate that all returned domains are known
    valid_domains = [d for d in domains if d in ALL_DOMAINS]
    if not valid_domains:
        raise AgentError(
            stage="domain_routing",
            message="Claude returned no valid domains for this query.",
        )

    result = DomainIdentification(domains=valid_domains, reasoning=reasoning)

    logger.info(
        "domains_identified",
        domains=result.domains,
        domain_count=len(result.domains),
        reasoning=result.reasoning[:200],
    )

    return result


def _extract_tool_result(response: anthropic.types.Message, tool_name: str) -> dict:
    """Extract the input dict from a tool_use content block."""
    for block in response.content:
        if block.type == "tool_use" and block.name == tool_name:
            return block.input

    raise AgentError(
        stage="domain_routing",
        message=f"Claude response did not contain a '{tool_name}' tool call.",
    )
