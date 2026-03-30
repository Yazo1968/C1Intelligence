"""
C1 -- Document Embedder
Generates 3072-dimension vector embeddings for document chunks
using the Gemini Embeddings API (gemini-embedding-001).
"""

from __future__ import annotations

from src.clients import get_gemini_client
from src.logging_config import get_logger
from src.ingestion.models import Chunk, EmbeddedChunk, IngestionError

logger = get_logger(__name__)

EMBEDDING_MODEL: str = "gemini-embedding-001"
EMBEDDING_DIMENSIONS: int = 3072
BATCH_SIZE: int = 100


def embed_chunks(chunks: list[Chunk]) -> list[EmbeddedChunk]:
    """
    Generate embeddings for a list of chunks using Gemini Embeddings API.

    Sends chunks in batches of 100. Validates every returned vector
    has exactly 3072 dimensions.

    Args:
        chunks: List of Chunk objects from the chunker.

    Returns:
        List of EmbeddedChunk objects with 3072-dimension embeddings.

    Raises:
        IngestionError: If any batch fails or any vector has wrong dimensions.
            On failure, raises immediately -- does not continue with remaining batches.
    """
    if not chunks:
        return []

    gemini_client = get_gemini_client()
    total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE

    logger.info(
        "embedding_started",
        total_chunks=len(chunks),
        total_batches=total_batches,
        model=EMBEDDING_MODEL,
        dimensions=EMBEDDING_DIMENSIONS,
    )

    embedded_chunks: list[EmbeddedChunk] = []

    for batch_index in range(total_batches):
        start = batch_index * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(chunks))
        batch = chunks[start:end]
        batch_texts = [chunk.content for chunk in batch]

        try:
            response = gemini_client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=batch_texts,
                config={"output_dimensionality": EMBEDDING_DIMENSIONS},
            )
        except Exception as exc:
            raise IngestionError(
                stage="embedding",
                message=f"Embedding failed for batch {batch_index}: {exc}",
            ) from exc

        try:
            embeddings = response.embeddings
        except AttributeError as exc:
            raise IngestionError(
                stage="embedding",
                message=f"Embedding failed for batch {batch_index}: unexpected response format - {exc}",
            ) from exc

        if len(embeddings) != len(batch):
            raise IngestionError(
                stage="embedding",
                message=(
                    f"Embedding failed for batch {batch_index}: "
                    f"expected {len(batch)} embeddings, got {len(embeddings)}"
                ),
            )

        for i, (chunk, embedding_obj) in enumerate(zip(batch, embeddings)):
            try:
                vector = embedding_obj.values
            except AttributeError:
                vector = list(embedding_obj)

            if len(vector) != EMBEDDING_DIMENSIONS:
                chunk_global_index = start + i
                raise IngestionError(
                    stage="embedding",
                    message=(
                        f"Embedding dimension mismatch at chunk {chunk_global_index}: "
                        f"expected {EMBEDDING_DIMENSIONS}, got {len(vector)}"
                    ),
                )

            embedded_chunks.append(
                EmbeddedChunk(
                    index=chunk.index,
                    content=chunk.content,
                    token_count=chunk.token_count,
                    section_heading=chunk.section_heading,
                    embedding=list(vector),
                )
            )

        logger.debug(
            "embedding_batch_complete",
            batch_index=batch_index,
            batch_size=len(batch),
        )

    logger.info(
        "embedding_complete",
        total_chunks_embedded=len(embedded_chunks),
    )

    return embedded_chunks
