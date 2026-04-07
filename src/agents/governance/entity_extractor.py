"""
C1 — Entity Extractor (Governance Function 1)
Reads every document chunk for a project in batches of 30.
Calls Claude once per batch to extract organisation and individual names.
Accumulates raw extractions across all batches.
Updates entity_directory_runs progress in Supabase as it goes.
Zero tool calls. No retrieval. Batch processing only.
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from dataclasses import dataclass, field

from src.clients import get_anthropic_client, get_supabase_client
from src.config import CLAUDE_MODEL

logger = logging.getLogger(__name__)

BATCH_SIZE = 30

_SYSTEM_PROMPT = """\
You are a document analysis assistant. Your only task is to identify the names
of organisations and individuals mentioned in the provided document chunks.

Rules:
- Extract names exactly as they appear in the text.
- Do not infer roles, relationships, or scope.
- Do not deduplicate — report every name variant you see.
- For individuals, extract a title prefix (Mr / Eng / Dr / Arch) only if
  it appears directly adjacent to the name in the text.
- Include a single sentence of context describing how the name appears.
- Return ONLY a valid JSON object. No preamble. No markdown fences.

Output schema:
{
  "organisations": [
    {"name": "Exact name as it appears", "context": "One sentence."}
  ],
  "individuals": [
    {"name": "Full name as it appears", "title": "Mr/Eng/Dr/Arch or null",
     "context": "One sentence."}
  ]
}
"""


@dataclass
class RawEntity:
    name: str
    context: str
    title: str | None = None          # individuals only


@dataclass
class BatchResult:
    organisations: list[RawEntity] = field(default_factory=list)
    individuals: list[RawEntity] = field(default_factory=list)


@dataclass
class ExtractionResult:
    run_id: str
    organisations: list[RawEntity] = field(default_factory=list)
    individuals: list[RawEntity] = field(default_factory=list)
    chunks_processed: int = 0
    total_chunks: int = 0
    error: str | None = None


def run_entity_extraction(project_id: str) -> ExtractionResult:
    """
    Main entry point. Called by the governance API route.
    Creates an entity_directory_runs record, processes all chunks,
    and returns accumulated raw extractions.
    Does NOT write to the entities table — that is consolidator's job.
    """
    supabase = get_supabase_client()
    anthropic = get_anthropic_client()

    # 1. Fetch all Layer 1 chunks for this project, ordered by chunk_index
    chunks_resp = (
        supabase.table("document_chunks")
        .select("id, content, chunk_index, document_id")
        .eq("project_id", project_id)
        .order("chunk_index", desc=False)
        .execute()
    )
    chunks = chunks_resp.data or []
    total = len(chunks)

    if total == 0:
        return ExtractionResult(
            run_id="",
            error="No documents found. Upload and ingest project documents before building the Entity Directory.",
        )

    # 2. Create run record
    run_resp = (
        supabase.table("entity_directory_runs")
        .insert({
            "project_id": project_id,
            "status": "running",
            "total_chunks": total,
            "chunks_processed": 0,
        })
        .execute()
    )
    run_id: str = run_resp.data[0]["id"]

    result = ExtractionResult(run_id=run_id, total_chunks=total)

    try:
        # 3. Process in batches
        for batch_start in range(0, total, BATCH_SIZE):
            batch = chunks[batch_start : batch_start + BATCH_SIZE]
            batch_result = _process_batch(anthropic, batch)
            result.organisations.extend(batch_result.organisations)
            result.individuals.extend(batch_result.individuals)
            result.chunks_processed += len(batch)

            # Update progress
            supabase.table("entity_directory_runs").update({
                "chunks_processed": result.chunks_processed,
            }).eq("id", run_id).execute()

            logger.info(
                "Entity extraction: project=%s run=%s batch %d/%d complete "
                "(%d orgs, %d individuals so far)",
                project_id, run_id,
                batch_start // BATCH_SIZE + 1,
                (total + BATCH_SIZE - 1) // BATCH_SIZE,
                len(result.organisations),
                len(result.individuals),
            )

    except Exception as exc:  # noqa: BLE001
        logger.exception("Entity extraction failed: project=%s run=%s", project_id, run_id)
        supabase.table("entity_directory_runs").update({
            "status": "failed",
            "error_message": str(exc),
        }).eq("id", run_id).execute()
        result.error = str(exc)
        return result

    # 4. Mark run as ready for consolidation (consolidator will set
    #    awaiting_confirmation once it has written entities)
    supabase.table("entity_directory_runs").update({
        "chunks_processed": total,
        "organisations_found": len(result.organisations),
        "individuals_found": len(result.individuals),
    }).eq("id", run_id).execute()

    return result


def _process_batch(anthropic_client, chunks: list[dict]) -> BatchResult:
    """Call Claude once with up to BATCH_SIZE chunks. Return extracted names."""
    user_content = _format_chunks(chunks)

    response = anthropic_client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2048,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    raw_text = response.content[0].text.strip()
    return _parse_response(raw_text)


def _format_chunks(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        parts.append(f"[Chunk {i}]\n{chunk.get('content', '').strip()}")
    return "\n\n".join(parts)


def _parse_response(raw: str) -> BatchResult:
    """Parse Claude's JSON response. Return empty BatchResult on any parse failure."""
    # Strip markdown fences if Claude added them despite instructions
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("Entity extractor: failed to parse LLM response as JSON")
        return BatchResult()

    result = BatchResult()
    for org in data.get("organisations", []):
        if isinstance(org, dict) and org.get("name"):
            result.organisations.append(
                RawEntity(name=org["name"], context=org.get("context", ""))
            )
    for ind in data.get("individuals", []):
        if isinstance(ind, dict) and ind.get("name"):
            result.individuals.append(
                RawEntity(
                    name=ind["name"],
                    context=ind.get("context", ""),
                    title=ind.get("title"),
                )
            )
    return result
