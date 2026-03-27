"""
C1 — Gemini File Search Retrieval
Queries a project's File Search store and normalizes grounding metadata into chunks.
"""

from __future__ import annotations

import uuid

from google import genai
from google.genai import types as genai_types

from src.config import GEMINI_MODEL
from src.logging_config import get_logger
from src.agents.models import AgentError, RetrievedChunk, RetrievalResult

logger = get_logger(__name__)


def retrieve_chunks(
    gemini_client: genai.Client,
    store_name: str,
    query_text: str,
    project_id: uuid.UUID,
) -> RetrievalResult:
    """
    Query Gemini File Search for chunks relevant to the query,
    filtered to the specified project.

    Returns RetrievalResult with parsed chunks and is_empty flag.
    """
    metadata_filter = f'project_id="{project_id}"'

    try:
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=query_text,
            config=genai_types.GenerateContentConfig(
                tools=[
                    genai_types.Tool(
                        file_search=genai_types.FileSearch(
                            file_search_store_names=[store_name],
                            metadata_filter=metadata_filter,
                        )
                    )
                ]
            ),
        )
    except Exception as exc:
        raise AgentError(
            stage="retrieval",
            message=f"Gemini File Search query failed: {exc}",
        ) from exc

    # Extract response text
    raw_text = ""
    if response.candidates and response.candidates[0].content:
        parts = response.candidates[0].content.parts
        if parts:
            raw_text = "".join(p.text for p in parts if hasattr(p, "text") and p.text)

    # Parse grounding metadata into structured chunks
    chunks = _parse_grounding_metadata(response)

    is_empty = len(chunks) == 0 and not raw_text.strip()

    logger.info(
        "retrieval_completed",
        project_id=str(project_id),
        chunks_found=len(chunks),
        is_empty=is_empty,
        response_text_length=len(raw_text),
    )

    return RetrievalResult(
        chunks=chunks,
        raw_response_text=raw_text,
        is_empty=is_empty,
    )


def _parse_grounding_metadata(response: genai_types.GenerateContentResponse) -> list[RetrievedChunk]:
    """
    Extract chunks from Gemini's grounding_metadata.

    The grounding_metadata structure contains:
    - grounding_chunks: list of chunks with retrieved_context (uri, title)
    - grounding_supports: maps response segments to chunk indices

    This function is defensive — unexpected metadata shapes log warnings
    rather than crashing.
    """
    chunks: list[RetrievedChunk] = []

    if not response.candidates:
        return chunks

    candidate = response.candidates[0]
    grounding = getattr(candidate, "grounding_metadata", None)

    if grounding is None:
        return chunks

    grounding_chunks = getattr(grounding, "grounding_chunks", None)
    if not grounding_chunks:
        return chunks

    for gc in grounding_chunks:
        retrieved_context = getattr(gc, "retrieved_context", None)
        if retrieved_context is None:
            logger.warning("grounding_chunk_missing_context", chunk=str(gc))
            continue

        uri = getattr(retrieved_context, "uri", "") or ""
        title = getattr(retrieved_context, "title", "") or ""
        text = getattr(gc, "chunk", None)
        if text is None:
            text = getattr(gc, "text", "") or ""

        # Attempt to extract supabase_document_id from the URI or title metadata
        document_id = _extract_document_id_from_uri(uri)

        chunks.append(
            RetrievedChunk(
                text=str(text),
                document_id=document_id,
                document_type=None,
                document_date=None,
                document_reference=title or uri,
                relevance_score=None,
            )
        )

    return chunks


def _extract_document_id_from_uri(uri: str) -> uuid.UUID | None:
    """
    Attempt to extract a UUID from a Gemini document URI.
    Returns None if no valid UUID is found.
    """
    if not uri:
        return None

    # Look for UUID patterns in the URI
    parts = uri.replace("/", " ").replace("_", " ").replace("-", " ").split()
    # Reconstruct potential UUIDs by checking segments
    for segment in uri.split("/"):
        segment = segment.strip()
        try:
            return uuid.UUID(segment)
        except ValueError:
            continue

    return None
