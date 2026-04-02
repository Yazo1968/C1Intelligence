"""
C1 -- Document Parser
Extracts structured text from uploaded documents using Docling.
Supports PDF (text-based and scanned/OCR), DOCX, and XLSX.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from src.logging_config import get_logger
from src.ingestion.models import IngestionError, ParsedDocument

logger = get_logger(__name__)

SUPPORTED_EXTENSIONS: set[str] = {".pdf", ".docx", ".xlsx"}

EXTENSION_TO_FORMAT: dict[str, str] = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".xlsx": "xlsx",
}


def parse_document(file_path: str, filename: str) -> ParsedDocument:
    """
    Parse a document file and extract structured text using Docling.

    Args:
        file_path: Absolute path to the file on disk.
        filename: Original filename (used to determine extension).

    Returns:
        ParsedDocument with extracted text, sections, page count, and format.

    Raises:
        IngestionError: If the format is unsupported or parsing fails.
    """
    extension = os.path.splitext(filename)[1].lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise IngestionError(
            stage="parse",
            message=f"Unsupported format: {extension}",
        )

    detected_format = EXTENSION_TO_FORMAT[extension]

    logger.info(
        "parsing_document",
        filename=filename,
        format=detected_format,
        file_path=file_path,
    )

    try:
        from docling.document_converter import DocumentConverter

        converter = DocumentConverter()
        result = converter.convert(Path(file_path))
    except Exception as exc:
        raise IngestionError(
            stage="parse",
            message=f"Parse failed: {exc}",
        ) from exc

    try:
        document = result.document
        full_text = document.export_to_markdown()
    except Exception as exc:
        raise IngestionError(
            stage="parse",
            message=f"Parse failed: text export error - {exc}",
        ) from exc

    if not full_text or not full_text.strip():
        raise IngestionError(
            stage="parse",
            message=f"Parse failed: no extractable text found in {filename}",
        )

    sections = _extract_sections_from_markdown(full_text)
    page_count = _extract_page_count(result, detected_format)

    logger.info(
        "document_parsed",
        filename=filename,
        format=detected_format,
        text_length=len(full_text),
        section_count=len(sections),
        page_count=page_count,
    )

    return ParsedDocument(
        text=full_text,
        sections=sections,
        page_count=page_count,
        format=detected_format,
    )


def _extract_sections_from_markdown(markdown_text: str) -> list[dict[str, str | None]]:
    """
    Parse markdown text to extract sections based on heading markers.

    Returns a list of {"heading": str | None, "content": str} dicts.
    Content before the first heading gets heading=None.
    Returns an empty list if no structure can be determined.
    """
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    matches = list(heading_pattern.finditer(markdown_text))

    if not matches:
        return []

    sections: list[dict[str, str | None]] = []

    # Content before the first heading
    pre_heading_text = markdown_text[: matches[0].start()].strip()
    if pre_heading_text:
        sections.append({"heading": None, "content": pre_heading_text})

    for i, match in enumerate(matches):
        heading_text = match.group(2).strip()
        content_start = match.end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown_text)
        content = markdown_text[content_start:content_end].strip()

        if heading_text or content:
            sections.append({"heading": heading_text, "content": content})

    return sections


def _extract_page_count(result: object, detected_format: str) -> int | None:
    """
    Extract page count from the Docling conversion result.
    Only applicable for PDFs. Returns None for other formats.
    """
    if detected_format != "pdf":
        return None

    try:
        document = result.document  # type: ignore[attr-defined]
        if hasattr(document, "pages") and document.pages is not None:
            return len(document.pages)
    except Exception:
        pass

    return None


def parse_document_text_layer(file_path: str, filename: str) -> ParsedDocument:
    """
    Parse a text-based digital PDF using PyMuPDF (fitz) for direct text
    extraction. No OCR, no page rendering, no layout analysis.

    Use this for Layer 2 reference documents (FIDIC, PMBOK, etc.) that are
    always digital text-layer PDFs. For Layer 1 project documents that may
    be scanned, use parse_document() which uses Docling with full OCR.

    Args:
        file_path: Absolute path to the PDF file on disk.
        filename: Original filename (used for logging).

    Returns:
        ParsedDocument with extracted text, sections, page count, and format.

    Raises:
        IngestionError: If parsing fails or no text is extracted.
    """
    logger.info(
        "parsing_document_text_layer",
        filename=filename,
        file_path=file_path,
    )

    try:
        import fitz  # PyMuPDF — lazy import
    except ImportError as exc:
        raise IngestionError(
            stage="parse",
            message="PyMuPDF (fitz) is not installed. Run: pip install pymupdf",
        ) from exc

    try:
        doc = fitz.open(file_path)
        page_texts: list[str] = []
        for page in doc:
            text = page.get_text()
            if text and text.strip():
                page_texts.append(text)
        page_count = len(doc)
        doc.close()
    except Exception as exc:
        raise IngestionError(
            stage="parse",
            message=f"PyMuPDF parse failed: {exc}",
        ) from exc

    full_text = "\n\n".join(page_texts)

    if not full_text or not full_text.strip():
        raise IngestionError(
            stage="parse",
            message=f"Parse failed: no extractable text found in {filename}",
        )

    sections = _extract_sections_from_markdown(full_text)

    logger.info(
        "document_parsed_text_layer",
        filename=filename,
        text_length=len(full_text),
        section_count=len(sections),
        page_count=page_count,
        pages_with_text=len(page_texts),
    )

    return ParsedDocument(
        text=full_text,
        sections=sections,
        page_count=page_count,
        format="pdf",
    )
