"""
C1 -- pgvector Retrieval (Two-Layer Warehouse)
Queries document_chunks (Layer 1, project-scoped) and reference_chunks
(Layer 2, platform-wide) via Supabase RPC functions for hybrid search:
  - Layer 1: semantic + full-text on project documents
  - Layer 2: semantic + full-text on reference documents (FIDIC, PMBOK, etc.)
Merges, deduplicates within each layer, enriches with document metadata,
and returns RetrievalResult compatible with the orchestrator.
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
    reference_top_k: int = 5,
) -> RetrievalResult:
    """
    Two-layer hybrid retrieval: Layer 1 (project documents) + Layer 2
    (reference documents). Each layer uses semantic + full-text search,
    merged and deduplicated within its own layer.

    Args:
        supabase_client: Supabase client for RPC calls and metadata lookups.
        gemini_client: Gemini client for query embedding.
        query_text: Natural language query from the user.
        project_id: UUID of the project to scope Layer 1 search.
        top_k: Maximum number of Layer 1 chunks to return after merge.
        reference_top_k: Maximum number of Layer 2 chunks to return after merge.

    Returns:
        RetrievalResult with ranked chunks (Layer 1 + Layer 2) and is_empty flag.

    Raises:
        AgentError: If query embedding or Layer 1 semantic search fails.
    """
    # ------------------------------------------------------------------
    # Step 1: Embed the query (shared across all four searches)
    # ------------------------------------------------------------------
    query_embedding = _embed_query(gemini_client, query_text)

    # ------------------------------------------------------------------
    # Step 2: Layer 1 — semantic search (project-scoped, fatal on failure)
    # ------------------------------------------------------------------
    semantic_results = _search_semantic(supabase_client, project_id, query_embedding, top_k)

    # ------------------------------------------------------------------
    # Step 3: Layer 1 — full-text search (project-scoped, non-fatal)
    # ------------------------------------------------------------------
    fulltext_results = _search_fulltext(supabase_client, project_id, query_text, top_k)

    # ------------------------------------------------------------------
    # Step 4: Layer 2 — reference semantic search (platform-wide, non-fatal)
    # ------------------------------------------------------------------
    ref_semantic_results = _search_reference_semantic(
        supabase_client, query_embedding, reference_top_k
    )

    # ------------------------------------------------------------------
    # Step 5: Layer 2 — reference full-text search (platform-wide, non-fatal)
    # ------------------------------------------------------------------
    ref_fulltext_results = _search_reference_fulltext(
        supabase_client, query_text, reference_top_k
    )

    # ------------------------------------------------------------------
    # Step 6: Merge and deduplicate within each layer
    # ------------------------------------------------------------------
    layer1_merged = _merge_and_deduplicate(semantic_results, fulltext_results, top_k)
    layer2_merged = _merge_and_deduplicate(ref_semantic_results, ref_fulltext_results, reference_top_k)

    # ------------------------------------------------------------------
    # Step 7: Enrich with document metadata (each layer separately)
    # ------------------------------------------------------------------
    layer1_metadata = _fetch_document_metadata(supabase_client, layer1_merged)
    layer2_metadata = _fetch_reference_document_metadata(supabase_client, layer2_merged)

    # ------------------------------------------------------------------
    # Step 8: Build RetrievedChunk list (Layer 1 first, then Layer 2)
    # ------------------------------------------------------------------
    layer1_chunks = _build_retrieved_chunks(layer1_merged, layer1_metadata, is_reference=False)
    layer2_chunks = _build_retrieved_chunks(layer2_merged, layer2_metadata, is_reference=True)
    retrieved_chunks = layer1_chunks + layer2_chunks

    is_empty = len(retrieved_chunks) == 0

    logger.info(
        "retrieval_completed",
        project_id=str(project_id),
        query_text_length=len(query_text),
        layer1_semantic_hits=len(semantic_results),
        layer1_fulltext_hits=len(fulltext_results),
        layer1_merged=len(layer1_merged),
        layer2_semantic_hits=len(ref_semantic_results),
        layer2_fulltext_hits=len(ref_fulltext_results),
        layer2_merged=len(layer2_merged),
        total_chunks=len(retrieved_chunks),
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


def _search_reference_semantic(
    supabase_client: SupabaseClient,
    query_embedding: list[float],
    top_k: int,
) -> list[dict]:
    """
    Call the search_chunks_reference_semantic RPC function (Layer 2).

    Platform-wide — no project_id filter.
    On failure: logs warning and returns empty list (non-fatal).
    """
    try:
        response = supabase_client.rpc(
            "search_chunks_reference_semantic",
            {
                "p_query_embedding": query_embedding,
                "p_top_k": top_k,
            },
        ).execute()
    except Exception as exc:
        logger.warning(
            "reference_semantic_search_failed",
            error=str(exc),
        )
        return []

    return response.data or []


def _search_reference_fulltext(
    supabase_client: SupabaseClient,
    query_text: str,
    top_k: int,
) -> list[dict]:
    """
    Call the search_chunks_reference_fulltext RPC function (Layer 2).

    Platform-wide — no project_id filter.
    On failure: logs warning and returns empty list (non-fatal).
    """
    try:
        response = supabase_client.rpc(
            "search_chunks_reference_fulltext",
            {
                "p_query_text": query_text,
                "p_top_k": top_k,
            },
        ).execute()
    except Exception as exc:
        logger.warning(
            "reference_fulltext_search_failed",
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


def _fetch_reference_document_metadata(
    supabase_client: SupabaseClient,
    merged_chunks: list[dict],
) -> dict[str, dict]:
    """
    Fetch reference document metadata for all unique reference_document_ids
    in the merged Layer 2 results.

    Returns a dict keyed by reference_document_id string with values containing:
        name, document_type.

    On failure: logs warning, returns empty dict.
    Enrichment failure must not block retrieval.
    """
    if not merged_chunks:
        return {}

    unique_ref_ids = list({
        row["reference_document_id"]
        for row in merged_chunks
        if row.get("reference_document_id")
    })
    if not unique_ref_ids:
        return {}

    try:
        response = (
            supabase_client.table("reference_documents")
            .select("id, name, document_type")
            .in_("id", unique_ref_ids)
            .execute()
        )
    except Exception as exc:
        logger.warning(
            "reference_document_metadata_fetch_failed",
            error=str(exc),
        )
        return {}

    ref_docs = response.data or []
    if not ref_docs:
        return {}

    metadata: dict[str, dict] = {}
    for doc in ref_docs:
        metadata[doc["id"]] = {
            "name": doc.get("name"),
            "document_type": doc.get("document_type"),
        }

    return metadata


def _build_retrieved_chunks(
    merged: list[dict],
    doc_metadata: dict[str, dict],
    is_reference: bool = False,
) -> list[RetrievedChunk]:
    """
    Convert merged search results into RetrievedChunk objects,
    enriched with document metadata where available.

    For Layer 1 (is_reference=False): uses document_id key and project document metadata.
    For Layer 2 (is_reference=True): uses reference_document_id key and reference document metadata.

    Metadata fields are populated from two sources (RPC row data takes priority,
    enriched metadata dict is fallback):
    - filename, document_reference_number, document_date, document_type_name
    """
    chunks: list[RetrievedChunk] = []

    # Layer 2 rows use reference_document_id; Layer 1 rows use document_id
    id_key = "reference_document_id" if is_reference else "document_id"

    for row in merged:
        doc_id_str = row.get(id_key, "")
        meta = doc_metadata.get(doc_id_str, {})

        if is_reference:
            # Layer 2: use reference document name and document_type
            doc_reference = meta.get("name")
            doc_type = meta.get("document_type")
            date_str = None  # Reference documents don't have a document_date field
            # RPC row fields (from migration 010 JOIN), fallback to enriched metadata
            filename = row.get("filename") or meta.get("name")
            doc_ref_number = row.get("document_reference_number") or meta.get("edition_year")
            doc_type_name = row.get("document_type_name") or meta.get("document_type")
        else:
            # Layer 1: use document_reference_number, fall back to filename
            doc_reference = meta.get("document_reference_number") or meta.get("filename")
            doc_type = meta.get("document_type_name")
            doc_date = meta.get("document_date")
            date_str = str(doc_date) if doc_date else None
            # RPC row fields (from migration 010 JOIN), fallback to enriched metadata
            filename = row.get("filename") or meta.get("filename")
            doc_ref_number = row.get("document_reference_number") or meta.get("document_reference_number")
            row_date = row.get("document_date")
            date_str = str(row_date) if row_date else date_str
            doc_type_name = row.get("document_type_name") or meta.get("document_type_name")

        # Use similarity for semantic results, rank for full-text-only
        score = row.get("similarity") if row.get("_source") == "semantic" else row.get("rank")

        try:
            doc_uuid = uuid.UUID(doc_id_str) if doc_id_str else None
        except ValueError:
            doc_uuid = None

        chunks.append(
            RetrievedChunk(
                text=row.get("content", ""),
                document_id=doc_uuid,
                chunk_index=row.get("chunk_index"),
                document_type=doc_type,
                document_date=date_str,
                document_reference=doc_reference,
                relevance_score=float(score) if score is not None else None,
                is_reference=is_reference,
                filename=filename,
                document_reference_number=doc_ref_number,
                document_type_name=doc_type_name,
            )
        )

    return chunks
