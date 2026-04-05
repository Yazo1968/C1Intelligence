"""
C1 — Shared Agent Tools
Tool definitions and executors for all agent types.

TOOL_DEFINITIONS — four tools available to all agents (SMEs and orchestrators):
1. search_chunks — semantic + full-text search against pgvector document_chunks
2. get_document — retrieve document metadata and all chunks
3. get_contradictions — check existing contradiction flags for given documents
4. get_related_documents — find documents by type and optional date range

ORCHESTRATOR_TOOL_DEFINITIONS — the above four plus:
5. invoke_sme — call a Tier 2 SME with a targeted question (Tier 1 orchestrators only)

Tier 1 orchestrators (legal, commercial, financial) use ORCHESTRATOR_TOOL_DEFINITIONS.
Tier 2 SMEs (claims, schedule, technical) use TOOL_DEFINITIONS.
"""

from __future__ import annotations

from typing import Callable

from src.clients import get_supabase_client, get_gemini_client
from src.logging_config import get_logger

logger = get_logger(__name__)

# Gemini embedding config — must match ingestion pipeline
EMBEDDING_MODEL: str = "gemini-embedding-001"
EMBEDDING_DIMENSIONS: int = 3072


# =============================================================================
# Anthropic Tool Definitions (passed to tools= parameter)
# =============================================================================

TOOL_DEFINITIONS: list[dict] = [
    {
        "name": "search_chunks",
        "description": (
            "Search for relevant document chunks in the project's document warehouse. "
            "Uses semantic similarity (vector cosine) and full-text search. "
            "Call this when the initially retrieved chunks are insufficient to answer "
            "the query, or when you need to search for a specific topic, clause, or term."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query — a natural language question or key terms.",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of top results to return. Default 10.",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_document",
        "description": (
            "Retrieve a full document's metadata and all its chunks, ordered by chunk index. "
            "Call this when you have a document_id from a chunk but need the complete document "
            "context — e.g., to read surrounding sections or check document-level metadata."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "UUID of the document to retrieve.",
                },
            },
            "required": ["document_id"],
        },
    },
    {
        "name": "get_contradictions",
        "description": (
            "Check existing contradiction flags involving the specified documents. "
            "Call this to see if any contradictions have already been detected between "
            "documents you are analysing."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "document_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of document UUIDs to check for contradiction flags.",
                },
            },
            "required": ["document_ids"],
        },
    },
    {
        "name": "get_related_documents",
        "description": (
            "Find documents in the project by document type and optional date range. "
            "Call this when you need to locate related documents — e.g., all Variation Orders, "
            "all Notices of Claim, or all Payment Certificates within a date range."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "document_type": {
                    "type": "string",
                    "description": "The document type name to search for (e.g., 'Notice of Claim').",
                },
                "date_from": {
                    "type": "string",
                    "description": "Start date filter (ISO format YYYY-MM-DD). Optional.",
                },
                "date_to": {
                    "type": "string",
                    "description": "End date filter (ISO format YYYY-MM-DD). Optional.",
                },
            },
            "required": ["document_type"],
        },
    },
]

ORCHESTRATOR_TOOL_DEFINITIONS: list[dict] = TOOL_DEFINITIONS + [
    {
        "name": "invoke_sme",
        "description": (
            "Invoke a Tier 2 SME agent with a targeted, specific question. "
            "Use this when the query requires specialist expertise beyond your orchestrator scope — "
            "e.g., delay analysis (schedule SME), specification compliance (technical SME), "
            "regulatory compliance (compliance SME), or cost accounting (financial_sme). "
            "The SME will retrieve relevant documents and return structured findings. "
            "Ask one focused question per invocation. "
            "Valid SME domains: 'schedule', 'technical', 'compliance', 'financial_sme'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sme_domain": {
                    "type": "string",
                    "enum": ["schedule", "technical", "compliance", "financial_sme"],
                    "description": "The Tier 2 SME domain to invoke.",
                },
                "question": {
                    "type": "string",
                    "description": (
                        "The specific targeted question for the SME. "
                        "This is NOT the user's raw query — it is a focused question "
                        "derived from your orchestrator analysis. Be precise."
                    ),
                },
                "context": {
                    "type": "string",
                    "description": (
                        "Optional additional context to pass to the SME — "
                        "e.g., relevant findings you have already established, "
                        "or constraints the SME should be aware of."
                    ),
                },
            },
            "required": ["sme_domain", "question"],
        },
    },
]


# =============================================================================
# Tool Executors
# =============================================================================


def _generate_query_embedding(query: str) -> list[float]:
    """
    Generate a 3072-dimension embedding for a search query using Gemini.

    Args:
        query: The search query text.

    Returns:
        List of 3072 floats.

    Raises:
        RuntimeError: If embedding generation fails.
    """
    gemini_client = get_gemini_client()
    response = gemini_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=[query],
        config={"output_dimensionality": EMBEDDING_DIMENSIONS},
    )
    embeddings = response.embeddings
    if not embeddings or len(embeddings) == 0:
        raise RuntimeError("Gemini returned no embeddings for query")

    vector = embeddings[0].values if hasattr(embeddings[0], "values") else list(embeddings[0])
    if len(vector) != EMBEDDING_DIMENSIONS:
        raise RuntimeError(
            f"Query embedding dimension mismatch: expected {EMBEDDING_DIMENSIONS}, got {len(vector)}"
        )
    return vector


def _build_source_label(chunk: dict) -> str:
    """
    Build a human-readable source label from chunk metadata fields.

    Uses citation_fields from the document_types table when available —
    an ordered list of which fields to include (e.g., ['type_name', 'reference_number', 'date']).
    Falls back to the default order when citation_fields is not set.

    Examples:
      "Contract Agreement, Ref. YD_PROC_PRD-000097.01, 2023-07-06"
      "Non-Conformance Report, Ref. NCR-0042, 2024-03-14"
      "FIDIC Conditions of Contract, Ref. 2017"
    """
    citation_fields: list[str] = chunk.get("citation_fields") or [
        "type_name", "reference_number", "date",
    ]
    parts: list[str] = []

    for field in citation_fields:
        if field == "type_name":
            value = chunk.get("document_type_name") or chunk.get("filename")
            if value:
                parts.append(value)
        elif field == "reference_number":
            value = chunk.get("document_reference_number")
            if value:
                parts.append(f"Ref. {value}")
        elif field == "date":
            value = chunk.get("document_date")
            if value:
                parts.append(str(value))

    if not parts:
        # No identifiers available — use chunk index as last resort
        chunk_index = chunk.get("chunk_index")
        if chunk_index is not None:
            parts.append(f"Chunk {chunk_index}")
        else:
            parts.append(chunk.get("filename") or "Unknown source")

    return ", ".join(parts)


def _execute_search_chunks(tool_input: dict, project_id: str) -> dict:
    """
    Execute search_chunks: semantic + full-text search against document_chunks.

    Semantic search requires a query embedding generated via Gemini.
    Full-text search failure is non-fatal — semantic-only results are returned.
    Each result includes a human-readable "source" label built from metadata.
    """
    query_text: str = tool_input["query"]
    top_k: int = tool_input.get("top_k", 10)

    supabase = get_supabase_client()
    results: list[dict] = []
    seen_ids: set[str] = set()

    # --- Semantic search (primary) ---
    try:
        query_embedding = _generate_query_embedding(query_text)
        semantic_response = supabase.rpc(
            "search_chunks_semantic",
            {
                "p_project_id": project_id,
                "p_query_embedding": query_embedding,
                "p_top_k": top_k,
            },
        ).execute()

        for chunk in semantic_response.data or []:
            chunk_id = str(chunk.get("id", ""))
            if chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                source_label = _build_source_label(chunk)
                results.append({
                    "id": chunk_id,
                    "document_id": str(chunk.get("document_id", "")),
                    "chunk_index": chunk.get("chunk_index"),
                    "content": chunk.get("content", ""),
                    "token_count": chunk.get("token_count"),
                    "score": chunk.get("similarity"),
                    "search_type": "semantic",
                    "source": source_label,
                })
    except Exception as exc:
        logger.error(
            "tool_search_chunks_semantic_error",
            query=query_text[:100],
            error=str(exc),
        )
        return {"error": True, "message": f"Semantic search failed: {exc}"}

    # --- Full-text search (supplementary, non-fatal) ---
    try:
        fulltext_response = supabase.rpc(
            "search_chunks_fulltext",
            {
                "p_project_id": project_id,
                "p_query_text": query_text,
                "p_top_k": top_k,
            },
        ).execute()

        for chunk in fulltext_response.data or []:
            chunk_id = str(chunk.get("id", ""))
            if chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                source_label = _build_source_label(chunk)
                results.append({
                    "id": chunk_id,
                    "document_id": str(chunk.get("document_id", "")),
                    "chunk_index": chunk.get("chunk_index"),
                    "content": chunk.get("content", ""),
                    "token_count": chunk.get("token_count"),
                    "score": chunk.get("rank"),
                    "search_type": "fulltext",
                    "source": source_label,
                })
    except Exception as exc:
        logger.warning(
            "tool_search_chunks_fulltext_error",
            query=query_text[:100],
            error=str(exc),
        )
        # Non-fatal: return semantic-only results

    return {"chunks": results, "total": len(results)}


def _execute_get_document(tool_input: dict, project_id: str) -> dict:
    """
    Retrieve document metadata and all its chunks ordered by chunk_index.
    """
    document_id: str = tool_input["document_id"]
    supabase = get_supabase_client()

    # --- Document metadata ---
    doc_response = (
        supabase.table("documents")
        .select("*")
        .eq("id", document_id)
        .eq("project_id", project_id)
        .execute()
    )

    if not doc_response.data:
        return {"error": True, "message": f"Document {document_id} not found in project"}

    document = doc_response.data[0]

    # --- Document chunks ---
    chunks_response = (
        supabase.table("document_chunks")
        .select("id, chunk_index, content, token_count")
        .eq("document_id", document_id)
        .eq("project_id", project_id)
        .order("chunk_index")
        .execute()
    )

    return {
        "document": {
            "id": str(document.get("id", "")),
            "filename": document.get("filename", ""),
            "status": document.get("status", ""),
            "document_date": str(document.get("document_date", "")),
            "document_reference_number": document.get("document_reference_number", ""),
            "fidic_clause_ref": document.get("fidic_clause_ref", ""),
            "document_status": document.get("document_status", ""),
        },
        "chunks": [
            {
                "id": str(chunk.get("id", "")),
                "chunk_index": chunk.get("chunk_index"),
                "content": chunk.get("content", ""),
                "token_count": chunk.get("token_count"),
            }
            for chunk in (chunks_response.data or [])
        ],
        "chunk_count": len(chunks_response.data or []),
    }


def _execute_get_contradictions(tool_input: dict, project_id: str) -> dict:
    """
    Query contradiction_flags for flags involving the given document IDs.
    """
    document_ids: list[str] = tool_input["document_ids"]
    supabase = get_supabase_client()

    # Get flags where either document_a_id or document_b_id is in the list
    response = (
        supabase.table("contradiction_flags")
        .select("*")
        .eq("project_id", project_id)
        .or_(
            ",".join(
                [f"document_a_id.eq.{did}" for did in document_ids]
                + [f"document_b_id.eq.{did}" for did in document_ids]
            )
        )
        .execute()
    )

    flags = [
        {
            "id": str(flag.get("id", "")),
            "document_a_id": str(flag.get("document_a_id", "")),
            "document_b_id": str(flag.get("document_b_id", "")),
            "field_name": flag.get("field_name", ""),
            "description": flag.get("description", ""),
            "created_at": str(flag.get("created_at", "")),
        }
        for flag in (response.data or [])
    ]

    return {"contradiction_flags": flags, "total": len(flags)}


def _execute_get_related_documents(tool_input: dict, project_id: str) -> dict:
    """
    Find documents by type name and optional date range within a project.
    """
    document_type: str = tool_input["document_type"]
    date_from: str | None = tool_input.get("date_from")
    date_to: str | None = tool_input.get("date_to")
    supabase = get_supabase_client()

    # First, find the document_type_id by name
    type_response = (
        supabase.table("document_types")
        .select("id")
        .ilike("name", f"%{document_type}%")
        .execute()
    )

    type_ids = [t["id"] for t in (type_response.data or [])]
    if not type_ids:
        return {"documents": [], "total": 0, "message": f"No document type matching '{document_type}'"}

    # Query documents matching those type IDs in this project
    query = (
        supabase.table("documents")
        .select("id, filename, status, document_date, document_reference_number, document_type_id, fidic_clause_ref")
        .eq("project_id", project_id)
        .in_("document_type_id", type_ids)
    )

    if date_from:
        query = query.gte("document_date", date_from)
    if date_to:
        query = query.lte("document_date", date_to)

    response = query.execute()

    documents = [
        {
            "id": str(doc.get("id", "")),
            "filename": doc.get("filename", ""),
            "status": doc.get("status", ""),
            "document_date": str(doc.get("document_date", "")),
            "document_reference_number": doc.get("document_reference_number", ""),
            "fidic_clause_ref": doc.get("fidic_clause_ref", ""),
        }
        for doc in (response.data or [])
    ]

    return {"documents": documents, "total": len(documents)}


def _execute_invoke_sme(tool_input: dict, project_id: str) -> dict:
    """
    Invoke a Tier 2 SME agent with a targeted question from a Tier 1 orchestrator.

    Validates the requested domain is a Tier 2 SME. Runs retrieval for the
    targeted question. Instantiates the SME via BaseSpecialist and runs it.
    Returns the SME's findings as a structured dict.

    All imports are lazy to avoid circular imports — base_specialist imports
    tools.py, so tools.py must not import base_specialist at module level.
    """
    # --- Lazy imports (avoid circular: base_specialist imports tools.py) ---
    from src.agents.specialist_config import SPECIALIST_CONFIGS
    from src.agents.retrieval import retrieve_chunks
    from src.agents.base_specialist import BaseSpecialist
    from src.clients import get_supabase_client as _get_supabase, get_gemini_client as _get_gemini

    sme_domain: str = tool_input["sme_domain"]
    question: str = tool_input["question"]
    context: str | None = tool_input.get("context")

    # --- Validate domain is Tier 2 SME ---
    config = SPECIALIST_CONFIGS.get(sme_domain)
    if config is None or config.tier != 2:
        valid_smes = [k for k, v in SPECIALIST_CONFIGS.items() if v.tier == 2]
        return {
            "error": True,
            "message": (
                f"'{sme_domain}' is not a valid Tier 2 SME domain. "
                f"Valid domains: {valid_smes}"
            ),
        }

    # --- Build targeted query — include context if provided ---
    targeted_query = question
    if context:
        targeted_query = f"{question}\n\nContext from orchestrator:\n{context}"

    # --- Retrieve chunks for the targeted question ---
    try:
        gemini_client = _get_gemini()
        supabase_client = _get_supabase()
        retrieval_result = retrieve_chunks(
            supabase_client=supabase_client,
            gemini_client=gemini_client,
            query_text=question,
            project_id=project_id,
        )
    except Exception as exc:
        logger.error(
            "invoke_sme_retrieval_error",
            sme_domain=sme_domain,
            project_id=project_id,
            error=str(exc),
        )
        return {"error": True, "message": f"Retrieval failed for SME '{sme_domain}': {exc}"}

    # --- Convert RetrievedChunk objects to dicts for BaseSpecialist ---
    chunks_as_dicts: list[dict] = [
        {
            "content": chunk.text,
            "document_id": str(chunk.document_id) if chunk.document_id else "",
            "chunk_index": chunk.chunk_index,
            "score": chunk.relevance_score,
            "is_reference": chunk.is_reference,
            "filename": chunk.filename,
            "document_reference_number": chunk.document_reference_number,
            "document_date": chunk.document_date,
            "document_type": chunk.document_type,
            "document_type_name": chunk.document_type_name,
            "document_reference": chunk.document_reference,
        }
        for chunk in retrieval_result.chunks
    ]

    # --- Instantiate and run the SME ---
    try:
        sme = BaseSpecialist(config=config)
        findings = sme.run(
            query=targeted_query,
            project_id=project_id,
            retrieved_chunks=chunks_as_dicts,
            round_1_findings=None,
        )
    except Exception as exc:
        logger.error(
            "invoke_sme_execution_error",
            sme_domain=sme_domain,
            project_id=project_id,
            error=str(exc),
        )
        return {"error": True, "message": f"SME '{sme_domain}' failed to produce findings: {exc}"}

    logger.info(
        "invoke_sme_complete",
        sme_domain=sme_domain,
        project_id=project_id,
        confidence=findings.confidence,
        tools_called=findings.tools_called,
    )

    return {
        "domain": findings.domain,
        "findings": findings.findings,
        "confidence": findings.confidence,
        "sources_used": findings.sources_used,
        "tools_called": findings.tools_called,
    }


# =============================================================================
# Tool Dispatcher
# =============================================================================

_TOOL_EXECUTORS: dict[str, Callable] = {
    "search_chunks": _execute_search_chunks,
    "get_document": _execute_get_document,
    "get_contradictions": _execute_get_contradictions,
    "get_related_documents": _execute_get_related_documents,
    "invoke_sme": _execute_invoke_sme,
}


def execute_tool(tool_name: str, tool_input: dict, project_id: str) -> dict:
    """
    Dispatch a tool call to the correct executor.

    Args:
        tool_name: The name of the tool to execute.
        tool_input: The input parameters for the tool.
        project_id: The project UUID string (all tools are project-scoped).

    Returns:
        Dict with tool results. On failure, returns {"error": True, "message": "..."}.

    Raises:
        ValueError: If tool_name is not recognized.
    """
    executor = _TOOL_EXECUTORS.get(tool_name)
    if executor is None:
        raise ValueError(f"Unknown tool: {tool_name}")

    logger.info(
        "tool_execution_started",
        tool_name=tool_name,
        project_id=project_id,
    )

    try:
        result = executor(tool_input, project_id)
        logger.info(
            "tool_execution_complete",
            tool_name=tool_name,
            project_id=project_id,
        )
        return result
    except Exception as exc:
        logger.error(
            "tool_execution_failed",
            tool_name=tool_name,
            project_id=project_id,
            error=str(exc),
        )
        return {"error": True, "message": f"Tool {tool_name} failed: {exc}"}
