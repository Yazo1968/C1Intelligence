"""
C1 — Base Orchestrator Agent
Shared agentic base class for all Tier 1 domain orchestrators
(legal, commercial, financial).

Tier 1 orchestrators differ from Tier 2 SMEs in three ways:
- They use ORCHESTRATOR_TOOL_DEFINITIONS, which includes invoke_sme
- They load directive files from skills/orchestrators/{domain}/
- Their system prompt frames them as professional leads who synthesise
  SME input, not as document analysts

The agentic loop (assess → tool call → reason → return) is identical
to BaseSpecialist. The run() signature is identical so orchestrator.py
can dispatch both types uniformly.
"""

from __future__ import annotations

import json

from src.clients import get_anthropic_client
from src.config import CLAUDE_MODEL
from src.logging_config import get_logger
from src.agents.models import EvidenceRecord, LayerRetrievalStatus, SpecialistFindings
from src.agents.skill_loader import SkillLoader
from src.agents.specialist_config import SpecialistConfig
from src.agents.tools import ORCHESTRATOR_TOOL_DEFINITIONS, execute_tool

logger = get_logger(__name__)

# System prompt prefix for all Tier 1 orchestrators
_ORCHESTRATOR_SYSTEM_PROMPT_PREFIX: str = """You are the {domain} orchestrator in the C1 Construction Documentation Intelligence Platform.

Your role is to deliver a senior professional assessment of the {domain} position on this project. You are not a document analyst — you are a professional lead who reads documents, forms conclusions, and where necessary delegates specific technical questions to specialist SME agents.

YOU HAVE TWO TOOLS:

1. search_chunks — retrieve relevant document chunks directly for your own analysis.
   Use this to read contracts, notices, correspondence, and other project documents.

2. invoke_sme — invoke a Tier 2 SME agent with a targeted question.
   Valid SME domains: schedule, technical, compliance, financial_sme.
   Use this when the query requires specialist expertise outside your direct scope.
   Frame a precise, specific question for the SME — not the user's raw query.
   You may invoke multiple SMEs on the same query if needed.
   SME findings are INPUT to your assessment. Synthesise them. Do not relay them verbatim.

RULES:
- Base your conclusions ONLY on evidence from the documents. Never speculate.
- If two documents conflict on the same field, surface BOTH values. Never resolve contradictions.
- If you invoke an SME, use their findings as supporting evidence, not as your output.
- If you lack sufficient evidence, state so explicitly. Do not fabricate.
- Cite specific documents using the source label provided in each chunk result.

At the end of your analysis, you MUST output a JSON block in the following format
(wrapped in ```json fences):
```json
{{{{
    "findings": "Your detailed professional assessment here",
    "confidence": "GREEN|AMBER|RED|GREY",
    "sources_used": ["document-id-1", "document-id-2"],
    "flagged_contradictions": ["contradiction-flag-id-1"]
}}}}
```

Confidence definitions:
- GREEN: All retrieved documents are consistent on the queried field.
- AMBER: Field is present but only partially supported, or only one document covers it.
- RED: Two or more documents contain conflicting values for the same field.
- GREY: No relevant documents found — warehouse has no relevant data for this query.

OUTPUT STANDARD:
Your findings are read by boards, lenders, legal counsel, and auditors. Write accordingly.

- Use the exact output format defined in your directive file. Do not deviate.
- Every factual claim must cite its source. Each search result includes a "source"
  field — use it exactly as provided, then append the clause or section if
  identifiable from the content.

  Format: [source field value, clause/section if identifiable]

  Examples:
    [Contract Agreement, Ref. CONTRACT-001, 2024-01-15, Clause 4.4]
    [Special Conditions of Contract, Section 3.2]
    [Governing Standard — retrieved from warehouse, Clause 20.1]

  Rules:
    - Always use the source field. Never substitute a document UUID.
    - NEVER write "Chunk N", "chunk_index", or any internal chunk reference.
    - NEVER write raw document UUIDs in your findings.

- Classify each finding: FLAG (requires attention) or INFORMATIONAL (noted).
- Where a finding is a FLAG, state the implication in one sentence.
- If a required document is absent, state explicitly what is missing and what
  cannot be assessed as a result.
- Write at director level. No jargon without definition. No hedging. No filler.
- Your output is a professional opinion with conclusions — not a document summary.

"""

_ROUND_1_CONTEXT_HEADER: str = """
--- CONTEXT FROM OTHER DOMAIN ORCHESTRATORS ---

{findings}

--- END CONTEXT ---
"""


class BaseOrchestrator:
    """
    Shared agentic base class for all Tier 1 domain orchestrators.

    Instantiate with a SpecialistConfig where tier=1. Call run() with a
    query and context. The orchestrator will reason, call tools (including
    invoke_sme for Tier 2 delegation), and return SpecialistFindings.
    """

    def __init__(self, config: SpecialistConfig) -> None:
        if config.tier != 1:
            raise ValueError(
                f"BaseOrchestrator requires tier=1 config. "
                f"Got tier={config.tier} for domain '{config.domain}'. "
                f"Use BaseSpecialist for Tier 2 SMEs."
            )
        self._config = config
        self._skill_loader = SkillLoader()
        self._grounding_schema: dict | None = (
            self._skill_loader.load_grounding_schema(config.domain)
        )

    @property
    def domain(self) -> str:
        """The orchestrator's domain name."""
        return self._config.domain

    @property
    def round_assignment(self) -> int:
        """Which orchestrator round this domain runs in."""
        return self._config.round_assignment

    def run(
        self,
        query: str,
        project_id: str,
        retrieved_chunks: list[dict],
        round_1_findings: dict | None = None,
    ) -> SpecialistFindings:
        """
        Execute the agentic loop for this orchestrator.

        Args:
            query: The user's original query text.
            project_id: The project UUID string.
            retrieved_chunks: Pre-retrieved chunks from the retrieval layer.
            round_1_findings: Context from other Tier 1 orchestrators
                (provided when this orchestrator runs after others).

        Returns:
            SpecialistFindings with domain assessment, confidence, and sources.
        """
        logger.info(
            "orchestrator_run_started",
            domain=self._config.domain,
            project_id=project_id,
            round_assignment=self._config.round_assignment,
            max_tool_rounds=self._config.max_tool_rounds,
        )

        # --- Build system prompt from directive file ---
        directive_content = self._skill_loader.load(self._config.domain, project_id)
        system_prompt = _ORCHESTRATOR_SYSTEM_PROMPT_PREFIX.format(
            domain=self._config.domain
        )
        if directive_content:
            system_prompt += f"\n\n{directive_content}"

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
                call_kwargs: dict = {
                    "model": CLAUDE_MODEL,
                    "max_tokens": 4000,
                    "system": [
                        {
                            "type": "text",
                            "text": system_prompt,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                    "messages": messages,
                }
                if tool_round < self._config.max_tool_rounds:
                    call_kwargs["tools"] = ORCHESTRATOR_TOOL_DEFINITIONS

                response = anthropic_client.messages.create(**call_kwargs)

            except Exception as exc:
                logger.error(
                    "orchestrator_api_error",
                    domain=self._config.domain,
                    project_id=project_id,
                    tool_round=tool_round,
                    error=str(exc),
                )
                return self._error_findings(
                    "Orchestrator failed to complete analysis due to API error.",
                    tools_called,
                )

            if response.stop_reason == "tool_use":
                tool_round += 1

                tool_use_blocks = [
                    block for block in response.content if block.type == "tool_use"
                ]

                messages.append({"role": "assistant", "content": response.content})

                tool_results: list[dict] = []
                for tool_block in tool_use_blocks:
                    tool_name = tool_block.name
                    tool_input = tool_block.input
                    # For invoke_sme, record the specific SME domain — not just the tool name
                    if tool_name == "invoke_sme" and "sme_domain" in tool_input:
                        tools_called.append(f"invoke_sme:{tool_input['sme_domain']}")
                    else:
                        tools_called.append(tool_name)

                    logger.info(
                        "orchestrator_tool_call",
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

                messages.append({"role": "user", "content": tool_results})
                continue

            elif response.stop_reason == "end_turn":
                text_content = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        text_content += block.text
                return self._parse_findings(text_content, tools_called)

            else:
                logger.warning(
                    "orchestrator_unexpected_stop_reason",
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

        return self._error_findings(
            "Orchestrator exhausted all tool rounds without producing findings.",
            tools_called,
        )

    def _build_user_message(
        self,
        query: str,
        retrieved_chunks: list[dict],
        round_1_findings: dict | None,
    ) -> str:
        """Build the user message from query, Layer 1/Layer 2 chunks, and optional context."""
        parts: list[str] = [f"QUERY: {query}"]

        layer1_chunks = [c for c in retrieved_chunks if not c.get("is_reference")]
        layer2_chunks = [c for c in retrieved_chunks if c.get("is_reference")]

        if layer1_chunks:
            parts.append("\n--- PROJECT DOCUMENT CHUNKS (Layer 1) ---\n")
            for chunk in layer1_chunks:
                content = chunk.get("content", "")
                source_label = self._build_chunk_source_label(chunk)
                parts.append(f"[source: {source_label}]\n{content}\n")
            parts.append("--- END PROJECT DOCUMENT CHUNKS ---")
        elif not layer2_chunks:
            parts.append(
                "\n[No document chunks were retrieved for this query. "
                "Use the search_chunks tool to find relevant documents.]\n"
            )

        if layer2_chunks:
            parts.append("\n--- REFERENCE DOCUMENT CHUNKS (Layer 2 — Standards and Regulations) ---\n")
            for chunk in layer2_chunks:
                content = chunk.get("content", "")
                source_label = self._build_chunk_source_label(chunk)
                parts.append(f"[source: {source_label}]\n{content}\n")
            parts.append("--- END REFERENCE DOCUMENT CHUNKS ---")

        if round_1_findings:
            findings_text = json.dumps(round_1_findings, indent=2, default=str)
            parts.append(_ROUND_1_CONTEXT_HEADER.format(findings=findings_text))

        return "\n".join(parts)

    @staticmethod
    def _build_chunk_source_label(chunk: dict) -> str:
        """Build a human-readable source label from chunk metadata fields."""
        parts: list[str] = []
        if chunk.get("document_type") or chunk.get("document_type_name"):
            parts.append(chunk.get("document_type") or chunk.get("document_type_name"))
        elif chunk.get("document_reference"):
            parts.append(chunk["document_reference"])
        elif chunk.get("filename"):
            parts.append(chunk["filename"])
        if chunk.get("document_reference_number"):
            parts.append(f"Ref. {chunk['document_reference_number']}")
        if chunk.get("document_date"):
            parts.append(str(chunk["document_date"]))
        return ", ".join(parts) if parts else "Unknown source"

    def _parse_findings(
        self, text: str, tools_called: list[str]
    ) -> SpecialistFindings:
        """
        Parse the orchestrator's text response into SpecialistFindings.
        Identical logic to BaseSpecialist._parse_findings.
        """
        json_block: dict = {}
        text_before_json = text

        try:
            json_start = text.index("```json")
            json_end = text.index("```", json_start + 7)
            json_str = text[json_start + 7 : json_end].strip()
            json_block = json.loads(json_str)
            text_before_json = text[:json_start].strip()
        except (ValueError, json.JSONDecodeError) as exc:
            logger.warning(
                "orchestrator_json_parse_failed",
                domain=self._config.domain,
                error=str(exc),
            )

        if json_block:
            findings_text = text_before_json or json_block.get("findings", text)
            confidence = json_block.get("confidence", "AMBER")
            if confidence not in ("GREEN", "AMBER", "RED", "GREY"):
                confidence = "AMBER"
            sources_used = json_block.get("sources_used", [])
            flagged = json_block.get("flagged_contradictions", [])
        else:
            findings_text = text_before_json
            confidence = "AMBER"
            sources_used = []
            flagged = []

        findings = SpecialistFindings(
            domain=self._config.domain,
            findings=findings_text,
            confidence=confidence,
            sources_used=sources_used,
            tools_called=tools_called,
            round_number=self._config.round_assignment,
            flagged_contradictions=flagged,
        )
        return self._validate_evidence_and_cap_confidence(findings)

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

    def _parse_evidence_declaration(self, findings_text: str) -> EvidenceRecord:
        """
        Parse the Evidence Declaration block from the orchestrator's findings text.

        Looks for a '### Evidence Declaration' section and extracts the
        layer retrieval status fields. Returns a default EvidenceRecord
        (all NOT_RETRIEVED) if the block is absent or unparseable.
        """
        import re

        record = EvidenceRecord()

        match = re.search(
            r"###\s+Evidence Declaration\s*\n(.*?)(?=\n###|\Z)",
            findings_text,
            re.DOTALL | re.IGNORECASE,
        )
        if not match:
            return record

        block = match.group(1)

        def _extract(pattern: str) -> str | None:
            m = re.search(pattern, block, re.IGNORECASE)
            return m.group(1).strip() if m else None

        def _parse_status(raw: str | None) -> LayerRetrievalStatus:
            if raw is None:
                return LayerRetrievalStatus.NOT_RETRIEVED
            upper = raw.upper()
            if upper.startswith("YES"):
                return LayerRetrievalStatus.RETRIEVED
            if upper.startswith("PARTIAL"):
                return LayerRetrievalStatus.PARTIAL
            return LayerRetrievalStatus.NOT_RETRIEVED

        # Layer 2b
        record.layer2b_status = _parse_status(
            _extract(r"Layer 2b retrieved:\s*\[?([^\]\n]+)\]?")
        )
        l2b_src = _extract(r"Layer 2b source:\s*\[?([^\]\n]+)\]?")
        if l2b_src and "NOT RETRIEVED" not in l2b_src.upper():
            record.layer2b_source = l2b_src

        # Layer 2a
        l2a_raw = _extract(r"Layer 2a retrieved:\s*\[?([^\]\n]+)\]?")
        if l2a_raw and "NOT APPLICABLE" in l2a_raw.upper():
            record.layer2a_status = LayerRetrievalStatus.NOT_RETRIEVED
        else:
            record.layer2a_status = _parse_status(l2a_raw)
        l2a_src = _extract(r"Layer 2a source:\s*\[?([^\]\n]+)\]?")
        if l2a_src and "NOT RETRIEVED" not in l2a_src.upper() and "NOT APPLICABLE" not in l2a_src.upper():
            record.layer2a_source = l2a_src

        # Layer 1 primary document
        l1_primary = _extract(r"Layer 1 primary document:\s*\[?([^\]\n]+)\]?")
        if l1_primary and "NOT RETRIEVED" not in l1_primary.upper():
            record.layer1_primary_document = l1_primary

        # Layer 1 amendment document
        amend_raw = _extract(r"Layer 1 amendment document:\s*\[?([^\]\n]+)\]?")
        if amend_raw and "NOT RETRIEVED" not in amend_raw.upper() and "NOT APPLICABLE" not in amend_raw.upper():
            record.layer1_amendment_document_status = LayerRetrievalStatus.RETRIEVED
        else:
            record.layer1_amendment_document_status = LayerRetrievalStatus.NOT_RETRIEVED

        # Provisions CANNOT CONFIRM
        cannot_raw = _extract(r"Provisions CANNOT CONFIRM:\s*\[?([^\]\n]+)\]?")
        if cannot_raw and cannot_raw.upper() != "NONE":
            record.provisions_cannot_confirm = [
                p.strip() for p in cannot_raw.split(",") if p.strip()
            ]

        return record

    def _apply_confidence_cap(
        self, findings: SpecialistFindings, cap: str
    ) -> SpecialistFindings:
        """
        Downgrade confidence if it is higher than the cap level.

        Cap order (worst to best): GREY=3, RED=2, AMBER=1, GREEN=0.
        If current confidence has a lower order number than the cap,
        downgrade to the cap.
        """
        cap_order = {"GREEN": 0, "AMBER": 1, "RED": 2, "GREY": 3}
        current = findings.confidence
        if cap_order.get(current, 0) < cap_order.get(cap, 3):
            logger.warning(
                "confidence_capped",
                domain=self._config.domain,
                original_confidence=current,
                capped_to=cap,
            )
            return findings.model_copy(update={"confidence": cap})
        return findings

    def _validate_evidence_and_cap_confidence(
        self, findings: SpecialistFindings
    ) -> SpecialistFindings:
        """
        Parse the Evidence Declaration block and apply confidence caps
        per the loaded grounding schema.

        Called at the end of _parse_findings(). Returns findings unchanged
        if no grounding schema is loaded for this domain.
        """
        if self._grounding_schema is None:
            return findings

        evidence = self._parse_evidence_declaration(findings.findings)

        # Cap for missing Layer 2b
        if (
            self._grounding_schema.get("layer2b_required")
            and evidence.layer2b_status == LayerRetrievalStatus.NOT_RETRIEVED
        ):
            cap = self._grounding_schema.get("confidence_cap_without_layer2b", "AMBER")
            findings = self._apply_confidence_cap(findings, cap)

        # Cap for missing amendment document
        if (
            self._grounding_schema.get("layer1_amendment_document_required")
            and evidence.layer1_amendment_document_status
            == LayerRetrievalStatus.NOT_RETRIEVED
        ):
            cap = self._grounding_schema.get(
                "confidence_cap_without_amendment_document", "GREY"
            )
            findings = self._apply_confidence_cap(findings, cap)

        # Cap for missing Layer 2a (when required)
        if (
            self._grounding_schema.get("layer2a_required")
            and evidence.layer2a_status == LayerRetrievalStatus.NOT_RETRIEVED
        ):
            cap = self._grounding_schema.get("confidence_cap_without_layer2a", "AMBER")
            findings = self._apply_confidence_cap(findings, cap)

        findings = findings.model_copy(update={"evidence_record": evidence})
        return findings
