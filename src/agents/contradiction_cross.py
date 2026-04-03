"""
C1 — Cross-Specialist Contradiction Detection
Compares findings across domain specialists after all orchestrators complete.
Identifies cases where two specialists reach conflicting conclusions about
the same fact, date, value, or contractual position on the same project.
"""

from __future__ import annotations

import anthropic

from src.config import CLAUDE_MODEL
from src.logging_config import get_logger
from src.agents.models import ContradictionFlag, SpecialistFindings
from src.agents.contradiction import CONTRADICTION_TOOL

logger = get_logger(__name__)

_CROSS_SPECIALIST_SYSTEM_PROMPT = """
You are a senior construction contract analyst reviewing findings from multiple
domain specialists who have independently analysed the same project documents.

Your task is to identify contradictions BETWEEN specialists — cases where two
specialists have reached conflicting conclusions about the same fact, date,
value, or contractual position.

Focus on:
- Dates: completion dates, extension of time positions, notice deadlines,
  time bar dates
- Values: contract sums, claimed amounts, certified amounts, variation values,
  retention amounts
- Factual positions: which party bears risk for an event, whether a notice
  was validly issued, whether an entitlement exists under the contract

Only flag genuine contradictions where two specialists address the same subject
but reach different conclusions. Do not flag:
- Cases where specialists address different subjects
- Cases where one specialist simply provides more detail than another
- Cases where one specialist says "CANNOT ASSESS" due to missing documents

For each contradiction:
- field_name: the specific fact or date that is contradicted
- document_a_reference: the domain of the first specialist (e.g. "LEGAL")
- value_a: what the first specialist concludes
- document_b_reference: the domain of the second specialist (e.g. "SCHEDULE")
- value_b: what the second specialist concludes
- description: one sentence explaining why these positions conflict
""".strip()


def cross_specialist_contradiction_pass(
    anthropic_client: anthropic.Anthropic,
    findings: list[SpecialistFindings],
) -> list[ContradictionFlag]:
    """
    Compare findings across all domain specialists for cross-domain contradictions.

    Requires at least two findings with non-empty content. Returns empty list
    if fewer than two findings are available or if no contradictions are found.
    Non-fatal: returns [] on any API or parsing error.
    """
    if len(findings) < 2:
        return []

    if not any(f.findings.strip() for f in findings):
        return []

    findings_text = _format_findings_for_cross_detection(findings)

    try:
        response = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            system=_CROSS_SPECIALIST_SYSTEM_PROMPT,
            tools=[CONTRADICTION_TOOL],
            tool_choice={"type": "tool", "name": "contradiction_report"},
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Review the following specialist findings and identify "
                        "any contradictions between them:\n\n"
                        f"{findings_text}"
                    ),
                }
            ],
        )
    except Exception as exc:
        logger.error("cross_specialist_contradiction_failed", error=str(exc))
        return []

    try:
        tool_result = _extract_tool_result(response)
    except Exception as exc:
        logger.error("cross_specialist_contradiction_tool_missing", error=str(exc))
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
        "cross_specialist_contradictions_detected",
        count=len(contradictions),
        domains=[f.domain for f in findings],
    )

    return contradictions


def _format_findings_for_cross_detection(findings: list[SpecialistFindings]) -> str:
    """Format specialist findings for cross-domain contradiction scanning."""
    sections: list[str] = []
    for finding in findings:
        domain_label = finding.domain.upper()
        sections.append(f"=== {domain_label} ===\n{finding.findings.strip()}")
    return "\n\n".join(sections)


def _extract_tool_result(response: anthropic.types.Message) -> dict:
    """Extract the contradiction_report tool result from the Claude response."""
    for block in response.content:
        if block.type == "tool_use" and block.name == "contradiction_report":
            return block.input
    raise ValueError("Claude response did not contain a contradiction_report tool call.")
