"""
C1 -- Chunk Store
Writes embedded chunks to the document_chunks table in Supabase.
Atomic per document: all chunks succeed or all are rolled back.
"""

from __future__ import annotations

import uuid

from src.clients import get_supabase_client
from src.logging_config import get_logger
from src.ingestion.models import EmbeddedChunk, IngestionError
from src.ingestion.status_tracker import update_status

logger = get_logger(__name__)


def store_chunks(
    document_id: uuid.UUID,
    project_id: uuid.UUID,
    chunks: list[EmbeddedChunk],
) -> int:
    """
    Write all embedded chunks for a document to the document_chunks table.

    Uses a single bulk insert. If the insert fails, rolls back any partially
    written rows by calling delete_chunks_for_document, then updates the
    document status to FAILED.

    On success, updates the document status to STORED.

    Args:
        document_id: UUID of the document in the documents table.
        project_id: UUID of the project (denormalized for RLS).
        chunks: List of EmbeddedChunk objects to write.

    Returns:
        Count of chunks successfully written.

    Raises:
        IngestionError: If the insert or status update fails.
    """
    supabase_client = get_supabase_client()

    rows = [
        {
            "document_id": str(document_id),
            "project_id": str(project_id),
            "chunk_index": chunk.index,
            "content": chunk.content,
            "embedding": chunk.embedding,
            "token_count": chunk.token_count,
        }
        for chunk in chunks
    ]

    try:
        supabase_client.table("document_chunks").insert(rows).execute()
    except Exception as exc:
        logger.error(
            "chunk_store_failed",
            document_id=str(document_id),
            chunk_count=len(rows),
            error=str(exc),
        )

        # Rollback: delete any partially written chunks
        try:
            delete_chunks_for_document(document_id)
        except Exception as rollback_exc:
            logger.error(
                "chunk_rollback_failed",
                document_id=str(document_id),
                error=str(rollback_exc),
            )

        # Mark document as FAILED
        try:
            update_status(supabase_client, document_id, "FAILED",
                          error_message=f"Chunk store failed: {exc}")
        except IngestionError as status_exc:
            logger.error(
                "failed_to_mark_document_as_failed_after_chunk_error",
                document_id=str(document_id),
                error=status_exc.message,
            )

        raise IngestionError(
            stage="chunk_store",
            message=f"Chunk store failed for document {document_id}: {exc}",
            document_id=document_id,
        ) from exc

    # Success: update status to STORED
    try:
        update_status(supabase_client, document_id, "STORED")
    except IngestionError as exc:
        logger.error(
            "stored_status_update_failed",
            document_id=str(document_id),
            error=exc.message,
        )
        raise

    logger.info(
        "chunks_stored",
        document_id=str(document_id),
        chunk_count=len(chunks),
    )

    return len(chunks)


def delete_chunks_for_document(document_id: uuid.UUID) -> int:
    """
    Delete all chunks for a given document from document_chunks.

    Used for rollback on failed inserts and for document deletion cleanup.

    Args:
        document_id: UUID of the document whose chunks should be deleted.

    Returns:
        Count of rows deleted.
    """
    supabase_client = get_supabase_client()

    try:
        response = (
            supabase_client.table("document_chunks")
            .delete()
            .eq("document_id", str(document_id))
            .execute()
        )
    except Exception as exc:
        raise IngestionError(
            stage="chunk_delete",
            message=f"Failed to delete chunks for document {document_id}: {exc}",
            document_id=document_id,
        ) from exc

    deleted_count = len(response.data) if response.data else 0

    logger.info(
        "chunks_deleted",
        document_id=str(document_id),
        deleted_count=deleted_count,
    )

    return deleted_count
