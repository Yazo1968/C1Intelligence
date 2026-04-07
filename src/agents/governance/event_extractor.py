"""
C1 — Event Extractor (Governance Function 2)
Per-entity event log extraction.
1. Fulltext search retrieves all chunks mentioning the entity by any name variant.
2. Chunks sorted by chunk_index (chronological document order).
3. Processed in batches of 30 — one LLM call per batch.
4. Raw events accumulated across all batches and returned to caller.
   Deduplication and sequencing is handled by consolidator.py.
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
FULLTEXT_CHUNK_LIMIT = 10_000   # retrieve all matching chunks — no cap

_STOPWORDS = frozenset({"and", "the", "for", "of", "in", "at", "to", "a", "an"})
_SKIP_SUFFIXES = frozenset({"llc", "ltd", "llp", "inc", "co", "corp", "pjsc",
                             "est", "group", "holding", "holdings"})

def _build_search_terms(entity: EntityInput) -> list[str]:
    """
    Build deduplicated ILIKE search terms from entity canonical name and variants.
    For each full name, also generates a short-form term (the first meaningful
    word >= 4 chars) to catch abbreviated mentions in documents.
    """
    all_names = [entity.canonical_name] + (entity.name_variants or [])
    terms: list[str] = []
    seen: set[str] = set()

    for name in all_names:
        name = name.strip()
        if not name:
            continue
        key = name.lower()
        if key not in seen:
            seen.add(key)
            terms.append(name)

        # Generate short-form: first word that is meaningful (>= 4 chars,
        # not a stopword or legal suffix)
        words = name.split()
        for word in words:
            clean = word.strip(".,;:()'\"").lower()
            if (
                len(clean) >= 4
                and clean not in _STOPWORDS
                and clean not in _SKIP_SUFFIXES
            ):
                if clean not in seen:
                    seen.add(clean)
                    terms.append(word.strip(".,;:()'\""))
                break   # only first meaningful word per name

    return terms


# ── Input / output dataclasses ────────────────────────────────────────────────

@dataclass
class EntityInput:
    """Minimal entity data required by the extractor."""
    entity_id: str
    project_id: str
    canonical_name: str
    name_variants: list[str]   # may be empty


@dataclass
class RawEvent:
    event_type: str
    event_date: str | None          # "YYYY-MM-DD" or null
    event_date_certain: bool
    status_before: str | None
    status_after: str | None
    initiated_by: str | None
    authorised_by: str | None
    source_document: str | None
    source_excerpt: str | None
    chunk_index: int = 0            # set by extractor from the chunk that produced this event


@dataclass
class EventExtractionResult:
    run_id: str
    entity_id: str
    raw_events: list[RawEvent] = field(default_factory=list)
    chunks_scanned: int = 0
    error: str | None = None


# ── System prompt ─────────────────────────────────────────────────────────────

def _build_system_prompt(entity: EntityInput) -> str:
    variants_line = ""
    if entity.name_variants:
        variants_line = (
            f"\nThe entity is also referred to by these name variants: "
            + ", ".join(f'"{v}"' for v in entity.name_variants)
        )
    return f"""\
You are a document analysis assistant. Your task is to extract authority events
involving a specific entity from the provided document chunks.

The entity is: "{entity.canonical_name}"{variants_line}

An authority event is any documented change in this entity's contractual standing,
authority, scope, or role. Extract only events that are explicitly evidenced in
the text. Do not infer or fabricate.

Valid event_type values (use exactly):
  nomination | appointment | authority_grant | scope_addition |
  scope_reduction | role_transfer | novation | replacement |
  suspension | termination

Rules:
- Extract the event date as YYYY-MM-DD if stated. If approximate or inferred,
  set event_date_certain to false.
- status_before: what was this entity's position immediately before this event?
  Set to null if this is the first known event or if not determinable.
- status_after: what is this entity's position after this event?
- source_excerpt: verbatim text from the chunk, maximum 100 words.
- If no authority events for this entity appear in these chunks, return
  an empty events array.
- Return ONLY a valid JSON object. No preamble. No markdown fences.

Output schema:
{{
  "events": [
    {{
      "event_type": "appointment",
      "event_date": "2023-06-19",
      "event_date_certain": true,
      "status_before": "No contractual standing",
      "status_after": "Appointed as Main Contractor",
      "initiated_by": "Name as it appears in text",
      "authorised_by": "Name as it appears, or null",
      "source_document": "Document name or reference",
      "source_excerpt": "Verbatim excerpt up to 100 words"
    }}
  ]
}}
"""


# ── Main entry point ──────────────────────────────────────────────────────────

def run_event_extraction(entity: EntityInput) -> EventExtractionResult:
    """
    Main entry point. Called by the governance API route after it creates
    an event_log_runs record.
    Returns raw events for the consolidator to process.
    Does NOT write to entity_events — that is the API route's responsibility.
    """
    supabase = get_supabase_client()
    anthropic = get_anthropic_client()

    # 2. Build search terms and find all matching chunks via ILIKE.
    # ILIKE substring matching is used instead of tsquery because entity names
    # are proper nouns — AND-logic tsquery misses abbreviated mentions.
    search_terms = _build_search_terms(entity)

    chunk_map: dict[str, dict] = {}   # chunk_id → chunk row
    for term in search_terms:
        try:
            resp = (
                supabase.table("document_chunks")
                .select("id, content, chunk_index, document_id")
                .eq("project_id", entity.project_id)
                .ilike("content", f"%{term}%")
                .execute()
            )
            for row in (resp.data or []):
                chunk_map[row["id"]] = row
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "ILIKE search failed for term '%s': %s", term, exc
            )

    if not chunk_map:
        return EventExtractionResult(
            run_id="",
            entity_id=entity.entity_id,
            chunks_scanned=0,
        )

    # 3. Sort by chunk_index (chronological document order)
    chunks = sorted(chunk_map.values(), key=lambda c: c.get("chunk_index", 0))

    result = EventExtractionResult(
        run_id="",   # set by caller
        entity_id=entity.entity_id,
        chunks_scanned=len(chunks),
    )

    system_prompt = _build_system_prompt(entity)

    # 4. Process in batches
    for batch_start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[batch_start : batch_start + BATCH_SIZE]
        batch_events = _process_batch(anthropic, system_prompt, entity, batch)
        # Tag each event with the chunk_index of its batch midpoint for ordering
        midpoint_chunk_index = batch[len(batch) // 2].get("chunk_index", batch_start)
        for event in batch_events:
            event.chunk_index = midpoint_chunk_index
        result.raw_events.extend(batch_events)

        logger.info(
            "Event extraction: entity=%s batch %d/%d (%d events so far)",
            entity.canonical_name,
            batch_start // BATCH_SIZE + 1,
            (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE,
            len(result.raw_events),
        )

    return result


# ── Batch processing ──────────────────────────────────────────────────────────

def _process_batch(
    anthropic_client,
    system_prompt: str,
    entity: EntityInput,
    chunks: list[dict],
) -> list[RawEvent]:
    user_content = _format_chunks(chunks)
    response = anthropic_client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=3000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    raw_text = response.content[0].text.strip()
    return _parse_response(raw_text)


def _format_chunks(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        doc_ref = chunk.get("document_reference_number") or chunk.get("filename") or ""
        header = f"[Chunk {i}]"
        if doc_ref:
            header += f" Source: {doc_ref}"
        parts.append(f"{header}\n{chunk.get('content', '').strip()}")
    return "\n\n".join(parts)


def _parse_response(raw: str) -> list[RawEvent]:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("Event extractor: failed to parse LLM response as JSON")
        return []

    events: list[RawEvent] = []
    for item in data.get("events", []):
        if not isinstance(item, dict):
            continue
        event_type = item.get("event_type", "").strip()
        if not event_type:
            continue
        events.append(
            RawEvent(
                event_type=event_type,
                event_date=item.get("event_date") or None,
                event_date_certain=bool(item.get("event_date_certain", True)),
                status_before=item.get("status_before") or None,
                status_after=item.get("status_after") or None,
                initiated_by=item.get("initiated_by") or None,
                authorised_by=item.get("authorised_by") or None,
                source_document=item.get("source_document") or None,
                source_excerpt=item.get("source_excerpt") or None,
            )
        )
    return events
