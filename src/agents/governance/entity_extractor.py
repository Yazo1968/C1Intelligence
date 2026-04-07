"""
C1 — Entity Extractor (Governance Function 1)
Two-stage extraction. Stage 1 only: reads every document chunk for a project
in batches of 30, calls Claude once per batch, writes raw names to
entity_raw_extractions immediately after each batch.

The caller (governance.py background task) creates the run record and passes
run_id in. This function never creates or owns the run record.

Stage 2 (consolidation) is handled separately by consolidator.py.
"""

from __future__ import annotations

import json
import logging
import re
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
    """
    Returned after Stage 1 completes.
    Entity data is now in entity_raw_extractions — not in memory.
    """
    run_id: str
    chunks_processed: int = 0
    total_chunks: int = 0
    organisations_found: int = 0
    individuals_found: int = 0
    error: str | None = None


def run_entity_extraction(project_id: str, run_id: str) -> ExtractionResult:
    """
    Stage 1 entry point. Called by the governance background task after it
    has already created the entity_directory_runs record with status='extracting'.

    Reads all project chunks in batches of 30. After each batch:
    - Writes raw extracted names to entity_raw_extractions
    - Updates chunks_processed + running counts on entity_directory_runs

    Returns ExtractionResult with final counts. Entity data lives in DB.
    """
    supabase = get_supabase_client()
    anthropic = get_anthropic_client()

    # 1. Fetch all chunks for this project, ordered by chunk_index
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
            run_id=run_id,
            error="No documents found. Upload and ingest project documents before building the Entity Directory.",
        )

    # Update total_chunks now that we know it
    supabase.table("entity_directory_runs").update({
        "total_chunks": total,
    }).eq("id", run_id).execute()

    result = ExtractionResult(run_id=run_id, total_chunks=total)

    try:
        for batch_number, batch_start in enumerate(range(0, total, BATCH_SIZE)):
            batch = chunks[batch_start : batch_start + BATCH_SIZE]
            batch_result = _process_batch(anthropic, batch)

            # Write raw extractions to DB immediately
            rows = []
            for org in batch_result.organisations:
                rows.append({
                    "project_id": project_id,
                    "run_id": run_id,
                    "entity_type": "organisation",
                    "name": org.name,
                    "title": None,
                    "context": org.context,
                    "batch_number": batch_number,
                })
            for ind in batch_result.individuals:
                rows.append({
                    "project_id": project_id,
                    "run_id": run_id,
                    "entity_type": "individual",
                    "name": ind.name,
                    "title": ind.title,
                    "context": ind.context,
                    "batch_number": batch_number,
                })
            if rows:
                supabase.table("entity_raw_extractions").insert(rows).execute()

            # Update running totals on the run record
            result.chunks_processed += len(batch)
            result.organisations_found += len(batch_result.organisations)
            result.individuals_found += len(batch_result.individuals)

            supabase.table("entity_directory_runs").update({
                "chunks_processed": result.chunks_processed,
                "organisations_found": result.organisations_found,
                "individuals_found": result.individuals_found,
            }).eq("id", run_id).execute()

            logger.info(
                "Entity extraction: project=%s run=%s batch %d/%d "
                "(%d orgs, %d individuals so far)",
                project_id, run_id,
                batch_number + 1,
                (total + BATCH_SIZE - 1) // BATCH_SIZE,
                result.organisations_found,
                result.individuals_found,
            )

    except Exception as exc:  # noqa: BLE001
        logger.exception(
            "Entity extraction failed: project=%s run=%s", project_id, run_id
        )
        supabase.table("entity_directory_runs").update({
            "status": "failed",
            "error_message": str(exc),
        }).eq("id", run_id).execute()
        result.error = str(exc)

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
    """Parse Claude JSON response. Return empty BatchResult on any parse failure."""
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
