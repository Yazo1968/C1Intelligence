"""
C1 -- pgvector Retrieval
Queries document_chunks via Supabase RPC functions for hybrid search:
  - Semantic (vector cosine similarity via pgvector)
  - Full-text (PostgreSQL tsvector/tsquery)
Merges, deduplicates, enriches with document metadata, and returns
RetrievalResult compatible with the orchestrator.
"""

from __future__ import annotations

import uuid

from google import genai
from supabase import Client as SupabaseClient

from src.logging_config import get_logger
from src.agents.models import AgentError, RetrievedChunk, RetrievalResult

logger = get_logger(__name__)

EMBEDDING_MODEL: str = "gemini-embedding-001"
EMBEDDING_DIMENSIONS: int = 3072


def retrieve_chunks(
    supabase_client: SupabaseClient,
    gemini_client: genai.Client,
    query_text: str,
    project_id: uuid.UUID,
    top_k: int = 20,
) -> RetrievalResult:
    """
    Hybrid retrieval: semantic vector search + full-text search,
    merged, deduplicated, enriched with document metadata.

    Args:
        supabase_client: Supabase client for RPC calls and metadata lookups.
        gemini_client: Gemini client for query embedding.
        query_text: Natural language query from the user.
        project_id: UUID of the project to scope the search.
        top_k: Maximum number of chunks to return after merge.

    Returns:
        RetrievalResult with ranked chunks and is_empty flag.

    Raises:
        AgentError: If query embedding or semantic search fails.
    """
    # ------------------------------------------------------------------
    # Step 1: Embed the query
    # ------------------------------------------------------------------
    query_embedding = _embed_query(gemini_client, query_text)

    # ------------------------------------------------------------------
    # Step 2: Semantic search
    # ------------------------------------------------------------------
    semantic_results = _search_semantic(supabase_client, project_id, query_embedding, top_k)

    # ------------------------------------------------------------------
    # Step 3: Full-text search (supplementary — failure does not block)
    # ------------------------------------------------------------------
    fulltext_results = _search_fulltext(supabase_client, project_id, query_text, top_k)

    # ------------------------------------------------------------------
    # Step 4: Merge and deduplicate
    # ------------------------------------------------------------------
    merged = _merge_and_deduplicate(semantic_results, fulltext_results, top_k)

    # ------------------------------------------------------------------
    # Step 5: Enrich with document metadata
    # ------------------------------------------------------------------
    doc_metadata = _fetch_document_metadata(supabase_client, merged)

    # ------------------------------------------------------------------
    # Step 6: Build RetrievedChunk list
    # ------------------------------------------------------------------
    retrieved_chunks = _build_retrieved_chunks(merged, doc_metadata)

    is_empty = len(retrieved_chunks) == 0

    logger.info(
        "retrieval_completed",
        project_id=str(project_id),
        query_text_length=len(query_text),
        semantic_hits=len(semantic_results),
        fulltext_hits=len(fulltext_results),
        merged_total=len(merged),
        is_empty=is_empty,
    )

    return RetrievalResult(
        chunks=retrieved_chunks,
        is_empty=is_empty,
    )


def _embed_query(gemini_client: genai.Client, query_text: str) -> list[float]:
    """
    Embed the query text using Gemini Embeddings API.

    Returns a 3072-dimension vector.
    Raises AgentError on failure.
    """
    try:
        response = gemini_client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=query_text,
            config={"output_dimensionality": EMBEDDING_DIMENSIONS},
        )
    except Exception as exc:
        raise AgentError(
            stage="retrieval",
            message=f"Query embedding failed: {exc}",
        ) from exc

    try:
        embedding = response.embeddings[0].values
    except (AttributeError, IndexError) as exc:
        raise AgentError(
            stage="retrieval",
            message=f"Query embedding failed: unexpected response format - {exc}",
        ) from exc

    if len(embedding) != EMBEDDING_DIMENSIONS:
        raise AgentError(
            stage="retrieval",
            message=(
                f"Query embedding failed: expected {EMBEDDING_DIMENSIONS} dimensions, "
                f"got {len(embedding)}"
            ),
        )

    return list(embedding)


def _search_semantic(
    supabase_client: SupabaseClient,
    project_id: uuid.UUID,
    query_embedding: list[float],
    top_k: int,
) -> list[dict]:
    """
    Call the search_chunks_semantic RPC function.

    Raises AgentError on failure.
    """
    try:
        response = supabase_client.rpc(
            "search_chunks_semantic",
            {
                "p_project_id": str(project_id),
                "p_query_embedding": query_embedding,
                "p_top_k": top_k,
            },
        ).execute()
    except Exception as exc:
        raise AgentError(
            stage="retrieval",
            message=f"Semantic search failed: {exc}",
        ) from exc

    return response.data or []


def _search_fulltext(
    supabase_client: SupabaseClient,
    project_id: uuid.UUID,
    query_text: str,
    top_k: int,
) -> list[dict]:
    """
    Call the search_chunks_fulltext RPC function.

    On failure: logs warning and returns empty list.
    Full-text search is supplementary -- its failure must not block semantic results.
    """
    try:
        response = supabase_client.rpc(
            "search_chunks_fulltext",
            {
                "p_project_id": str(project_id),
                "p_query_text": query_text,
                "p_top_k": top_k,
            },
        ).execute()
    except Exception as exc:
        logger.warning(
            "fulltext_search_failed",
            project_id=str(project_id),
            error=str(exc),
        )
        return []

    return response.data or []


def _merge_and_deduplicate(
    semantic_results: list[dict],
    fulltext_results: list[dict],
    top_k: int,
) -> list[dict]:
    """
    Merge semantic and full-text results into a single deduplicated list.

    - If a chunk appears in both, keep the semantic result (carries similarity score).
    - Semantic results come first (sorted by similarity desc), then full-text-only
      results (sorted by rank desc).
    - Capped at top_k total chunks.
    """
    seen_ids: set[str] = set()
    merged: list[dict] = []

    # Semantic results first (already ordered by similarity desc from SQL)
    for row in semantic_results:
        chunk_id = row.get("id", "")
        if chunk_id not in seen_ids:
            seen_ids.add(chunk_id)
            row["_source"] = "semantic"
            merged.append(row)

    # Full-text results: only add chunks not already seen
    for row in fulltext_results:
        chunk_id = row.get("id", "")
        if chunk_id not in seen_ids:
            seen_ids.add(chunk_id)
            row["_source"] = "fulltext"
            merged.append(row)

    return merged[:top_k]


def _fetch_document_metadata(
    supabase_client: SupabaseClient,
    merged_chunks: list[dict],
) -> dict[str, dict]:
    """
    Fetch document metadata for all unique document_ids in the merged results.

    Returns a dict keyed by document_id string with values containing:
        document_reference_number, document_date, document_type_name, filename.

    On failure: logs warning, returns empty dict.
    Enrichment failure must not block retrieval.
    """
    if not merged_chunks:
        return {}

    unique_doc_ids = list({row["document_id"] for row in merged_chunks if row.get("document_id")})
    if not unique_doc_ids:
        return {}

    # Fetch documents
    try:
        doc_response = (
            supabase_client.table("documents")
            .select("id, filename, document_reference_number, document_date, document_type_id")
            .in_("id", unique_doc_ids)
            .execute()
        )
    except Exception as exc:
        logger.warning(
            "document_metadata_fetch_failed",
            error=str(exc),
        )
        return {}

    documents = doc_response.data or []
    if not documents:
        return {}

    # Collect unique document_type_ids for bulk lookup
    type_ids = list({
        doc["document_type_id"]
        for doc in documents
        if doc.get("document_type_id") is not None
    })

    type_name_map: dict[int, str] = {}
    if type_ids:
        try:
            type_response = (
                supabase_client.table("document_types")
                .select("id, name")
                .in_("id", type_ids)
                .execute()
            )
            for dt in (type_response.data or []):
                type_name_map[dt["id"]] = dt["name"]
        except Exception as exc:
            logger.warning(
                "document_type_names_fetch_failed",
                error=str(exc),
            )

    # Build metadata map
    metadata: dict[str, dict] = {}
    for doc in documents:
        doc_id_str = doc["id"]
        type_id = doc.get("document_type_id")
        metadata[doc_id_str] = {
            "document_reference_number": doc.get("document_reference_number"),
            "document_date": doc.get("document_date"),
            "document_type_name": type_name_map.get(type_id) if type_id else None,
            "filename": doc.get("filename"),
        }

    return metadata


def _build_retrieved_chunks(
    merged: list[dict],
    doc_metadata: dict[str, dict],
) -> list[RetrievedChunk]:
    """
    Convert merged search results into RetrievedChunk objects,
    enriched with document metadata where available.
    """
    chunks: list[RetrievedChunk] = []

    for row in merged:
        doc_id_str = row.get("document_id", "")
        meta = doc_metadata.get(doc_id_str, {})

        # Use document_reference_number if available, fall back to filename
        doc_reference = meta.get("document_reference_number") or meta.get("filename")

        # Use similarity for semantic results, rank for full-text-only
        score = row.get("similarity") if row.get("_source") == "semantic" else row.get("rank")

        doc_date = meta.get("document_date")
        date_str = str(doc_date) if doc_date else None

        try:
            doc_uuid = uuid.UUID(doc_id_str) if doc_id_str else None
        except ValueError:
            doc_uuid = None

        chunks.append(
            RetrievedChunk(
                text=row.get("content", ""),
                document_id=doc_uuid,
                document_type=meta.get("document_type_name"),
                document_date=date_str,
                document_reference=doc_reference,
                relevance_score=float(score) if score is not None else None,
            )
        )

    return chunks
