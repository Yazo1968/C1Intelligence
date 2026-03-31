"""
C1 -- Document Chunker
Splits parsed document text into semantically coherent chunks for embedding.
Uses tiktoken (cl100k_base) for all token counting.
"""

from __future__ import annotations

import re

import tiktoken

from src.logging_config import get_logger
from src.ingestion.models import Chunk, ParsedDocument

logger = get_logger(__name__)

# Singleton encoding instance -- loaded once, reused across all calls
_encoding: tiktoken.Encoding | None = None


def _get_encoding() -> tiktoken.Encoding:
    """Return the singleton tiktoken encoding."""
    global _encoding
    if _encoding is None:
        _encoding = tiktoken.get_encoding("cl100k_base")
    return _encoding


def count_tokens(text: str) -> int:
    """Count tokens in a text string using cl100k_base encoding."""
    return len(_get_encoding().encode(text))


def chunk_document(
    parsed: ParsedDocument,
    target_tokens: int = 450,  # 450 validated in smoke test (2026-03-30) — supersedes original 512-token design spec
    overlap_tokens: int = 50,
) -> list[Chunk]:
    """
    Split a parsed document into semantically coherent chunks.

    Strategy:
    - If sections exist: chunk within sections, never crossing section boundaries.
    - Target 400-500 tokens per chunk (configurable).
    - 50-token overlap between consecutive chunks (configurable).
    - Never break mid-sentence (uses . ? ! as boundaries).

    Args:
        parsed: A ParsedDocument from the parser.
        target_tokens: Target token count per chunk (default 450).
        overlap_tokens: Token overlap between consecutive chunks (default 50).

    Returns:
        Ordered list of Chunk objects. Empty list if no extractable text.
    """
    if not parsed.text or not parsed.text.strip():
        return []

    chunks: list[Chunk] = []

    if parsed.sections:
        # Section-aware chunking: never split across section boundaries
        for section in parsed.sections:
            heading = section.get("heading")
            content = section.get("content", "")
            if not content or not content.strip():
                continue

            section_text = content.strip()
            section_token_count = count_tokens(section_text)

            if section_token_count > target_tokens * 10:
                logger.warning(
                    "unusually_large_section",
                    heading=heading,
                    token_count=section_token_count,
                )

            section_chunks = _split_text_into_chunks(
                section_text, target_tokens, overlap_tokens, heading
            )
            chunks.extend(section_chunks)
    else:
        # No structure: chunk the full text
        chunks = _split_text_into_chunks(
            parsed.text.strip(), target_tokens, overlap_tokens, section_heading=None
        )

    # Assign sequential zero-based indexes
    for i, chunk in enumerate(chunks):
        chunk.index = i

    logger.info(
        "document_chunked",
        total_chunks=len(chunks),
        total_tokens=sum(c.token_count for c in chunks),
        has_sections=bool(parsed.sections),
    )

    return chunks


def _split_text_into_chunks(
    text: str,
    target_tokens: int,
    overlap_tokens: int,
    section_heading: str | None,
) -> list[Chunk]:
    """
    Split a block of text into overlapping chunks at sentence boundaries.

    For sections shorter than overlap_tokens: returns a single chunk, no overlap.
    Never returns a chunk with token_count of 0.
    """
    text_token_count = count_tokens(text)

    # Short section: return as a single chunk, no overlap
    if text_token_count <= target_tokens:
        if text_token_count == 0:
            return []
        return [
            Chunk(
                index=0,
                content=text,
                token_count=text_token_count,
                section_heading=section_heading,
            )
        ]

    sentences = _split_into_sentences(text)
    chunks: list[Chunk] = []
    current_sentences: list[str] = []
    current_token_count: int = 0

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)

        # If a single sentence exceeds the target, it becomes its own chunk
        if sentence_tokens > target_tokens and not current_sentences:
            chunks.append(
                Chunk(
                    index=0,
                    content=sentence.strip(),
                    token_count=sentence_tokens,
                    section_heading=section_heading,
                )
            )
            continue

        # Adding this sentence would exceed target: finalize current chunk
        if current_token_count + sentence_tokens > target_tokens and current_sentences:
            chunk_text = " ".join(current_sentences).strip()
            chunk_token_count = count_tokens(chunk_text)
            if chunk_token_count > 0:
                chunks.append(
                    Chunk(
                        index=0,
                        content=chunk_text,
                        token_count=chunk_token_count,
                        section_heading=section_heading,
                    )
                )

            # Apply overlap: carry trailing sentences into the next chunk
            overlap_sentences, overlap_count = _compute_overlap(
                current_sentences, overlap_tokens
            )
            current_sentences = overlap_sentences
            current_token_count = overlap_count

        current_sentences.append(sentence)
        current_token_count += sentence_tokens

    # Flush remaining sentences
    if current_sentences:
        chunk_text = " ".join(current_sentences).strip()
        chunk_token_count = count_tokens(chunk_text)
        if chunk_token_count > 0:
            chunks.append(
                Chunk(
                    index=0,
                    content=chunk_text,
                    token_count=chunk_token_count,
                    section_heading=section_heading,
                )
            )

    return chunks


def _split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences using period, question mark, and exclamation mark
    as boundaries. Preserves the delimiter at the end of each sentence.
    """
    raw_parts = re.split(r"(?<=[.?!])\s+", text)
    return [part.strip() for part in raw_parts if part.strip()]


def _compute_overlap(
    sentences: list[str],
    overlap_tokens: int,
) -> tuple[list[str], int]:
    """
    Select trailing sentences from the current chunk to carry into the next chunk
    as overlap. Selects sentences from the end until reaching overlap_tokens.

    Returns (overlap_sentences, overlap_token_count).
    """
    overlap_sentences: list[str] = []
    overlap_count: int = 0

    for sentence in reversed(sentences):
        sentence_tokens = count_tokens(sentence)
        if overlap_count + sentence_tokens > overlap_tokens and overlap_sentences:
            break
        overlap_sentences.insert(0, sentence)
        overlap_count += sentence_tokens

    return overlap_sentences, overlap_count
