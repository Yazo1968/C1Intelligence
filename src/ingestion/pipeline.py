"""
C1 -- Ingestion Pipeline
Orchestrates the full ingestion flow for a single document upload.
This is the only module that knows the complete flow.

Flow: validate -> create record -> parse -> classify -> extract metadata ->
      validate metadata -> chunk -> embed -> store

All document parsing is handled by Docling (local).
All embedding is handled by Gemini Embeddings API.
All storage is handled by Supabase pgvector.
"""

from __future__ import annotations

import uuid

from supabase import Client as SupabaseClient

from src.clients import get_anthropic_client, get_supabase_client
from src.logging_config import get_logger
from src.ingestion.models import (
    ClassificationResult,
    ExtractedMetadata,
    IngestionError,
    IngestionResult,
    UploadRequest,
    ValidationResult,
)
from src.ingestion.file_validation import validate_file
from src.ingestion.parser import parse_document
from src.ingestion.chunker import chunk_document
from src.ingestion.embedder import embed_chunks
from src.ingestion.store import store_chunks
from src.ingestion.taxonomy_cache import TaxonomyCache
from src.ingestion.classifier import classify_document
from src.ingestion.metadata_extractor import extract_metadata
from src.ingestion.tier_validator import validate_metadata_for_tier
from src.ingestion.status_tracker import (
    add_to_classification_queue,
    create_document_record,
    update_document_metadata,
    update_status,
)

logger = get_logger(__name__)

# Module-level taxonomy cache -- loaded once, reused across all ingestion calls
_taxonomy_cache = TaxonomyCache()


def ensure_taxonomy_loaded() -> None:
    """Load the taxonomy cache if not already loaded."""
    if not _taxonomy_cache.is_loaded:
        _taxonomy_cache.load(get_supabase_client())


def ingest_document(
    file_path: str,
    file_size_bytes: int,
    request: UploadRequest,
) -> IngestionResult:
    """
    Full ingestion pipeline for a single document.

    Flow:
    1.  Validate file (extension, size)
    2.  Create document record (status=QUEUED)
    3.  Transition -> EXTRACTING
    4.  Parse document with Docling
    5.  Transition -> CLASSIFYING
    6.  Claude classification against taxonomy
    7.  Claude metadata extraction (non-fatal on failure)
    8.  Tier-based validation (flag gaps, don't block)
    9.  Update document record with classification and metadata
    10. Chunk document
    11. Embed chunks via Gemini Embeddings API
    12. Store chunks to Supabase pgvector (handles STORED/FAILED status)

    Every step has explicit error handling. No document is silently discarded.
    """
    anthropic_client = get_anthropic_client()
    supabase_client = get_supabase_client()

    ensure_taxonomy_loaded()

    document_id: uuid.UUID | None = None
    classification: ClassificationResult | None = None
    extracted: ExtractedMetadata | None = None
    validation: ValidationResult | None = None
    queued_for_review: bool = False

    # ------------------------------------------------------------------
    # Step 1: Validate file
    # ------------------------------------------------------------------
    try:
        validate_file(request.filename, file_size_bytes)
    except IngestionError as exc:
        logger.error("file_validation_failed", filename=request.filename, error=exc.message)
        return IngestionResult(
            document_id=uuid.UUID(int=0),
            status="FAILED",
            error_message=exc.message,
        )

    # ------------------------------------------------------------------
    # Step 2: Create document record (status=QUEUED)
    # ------------------------------------------------------------------
    try:
        document_id = create_document_record(supabase_client, request)
    except IngestionError as exc:
        logger.error("document_creation_failed", error=exc.message)
        return IngestionResult(
            document_id=uuid.UUID(int=0),
            status="FAILED",
            error_message=exc.message,
        )

    # ------------------------------------------------------------------
    # Step 3: Transition -> EXTRACTING
    # ------------------------------------------------------------------
    try:
        update_status(supabase_client, document_id, "EXTRACTING")
    except IngestionError as exc:
        return _fail_document(supabase_client, document_id, exc.message)

    # ------------------------------------------------------------------
    # Step 4: Parse document with Docling
    # ------------------------------------------------------------------
    try:
        parsed = parse_document(file_path, request.filename)
    except IngestionError as exc:
        return _fail_document(supabase_client, document_id, exc.message)

    document_text = parsed.text

    # ------------------------------------------------------------------
    # Step 5: Transition -> CLASSIFYING
    # ------------------------------------------------------------------
    try:
        update_status(supabase_client, document_id, "CLASSIFYING")
    except IngestionError as exc:
        return _fail_document(supabase_client, document_id, exc.message)

    # ------------------------------------------------------------------
    # Step 6: Claude classification
    # ------------------------------------------------------------------
    user_selected_type_name: str | None = None
    if request.user_selected_type_id is not None:
        dt = _taxonomy_cache.get_by_id(request.user_selected_type_id)
        if dt is not None:
            user_selected_type_name = dt.name

    try:
        classification = classify_document(
            anthropic_client=anthropic_client,
            document_text=document_text,
            filename=request.filename,
            taxonomy_prompt=_taxonomy_cache.get_prompt_formatted_list(),
            user_selected_type_id=request.user_selected_type_id,
            user_selected_type_name=user_selected_type_name,
        )
    except IngestionError as exc:
        return _fail_document(supabase_client, document_id, exc.message)

    # Handle low confidence or user-selection mismatch
    if classification.needs_queue:
        queued_for_review = True
        reason = (
            f"Classification confidence ({classification.confidence:.2f}) "
            f"below threshold. Suggested: {classification.document_type_name}. "
            f"Reasoning: {classification.reasoning}"
        )
        try:
            add_to_classification_queue(
                supabase_client,
                document_id,
                request.project_id,
                reason,
                classification.document_type_id,
            )
        except IngestionError as exc:
            logger.error(
                "classification_queue_insert_failed",
                document_id=str(document_id),
                error=exc.message,
            )
            # Non-fatal -- continue with the low-confidence classification

    # Check for user-selection mismatch
    if (
        request.user_selected_type_id is not None
        and classification.document_type_id != request.user_selected_type_id
        and not classification.needs_queue  # Don't double-queue
    ):
        queued_for_review = True
        reason = (
            f"User selected type ID {request.user_selected_type_id} "
            f"but AI classified as {classification.document_type_name} "
            f"(ID {classification.document_type_id}). "
            f"Reasoning: {classification.reasoning}"
        )
        try:
            add_to_classification_queue(
                supabase_client,
                document_id,
                request.project_id,
                reason,
                classification.document_type_id,
            )
        except IngestionError as exc:
            logger.error(
                "classification_queue_insert_failed",
                document_id=str(document_id),
                error=exc.message,
            )

    # ------------------------------------------------------------------
    # Step 7: Claude metadata extraction (non-fatal on failure)
    # ------------------------------------------------------------------
    try:
        extracted = extract_metadata(
            anthropic_client=anthropic_client,
            document_text=document_text,
            filename=request.filename,
            document_type_name=classification.document_type_name,
            category=classification.category,
        )
    except IngestionError as exc:
        logger.warning(
            "metadata_extraction_failed",
            document_id=str(document_id),
            error=exc.message,
        )
        # Continue -- metadata extraction failure is non-fatal

    # ------------------------------------------------------------------
    # Step 8: Tier-based validation (flag gaps, don't block)
    # ------------------------------------------------------------------
    if extracted is not None:
        validation = validate_metadata_for_tier(extracted, classification.tier)
        if validation.has_required_gaps:
            logger.warning(
                "tier_validation_gaps",
                document_id=str(document_id),
                tier=classification.tier,
                gap_count=len(validation.gaps),
                gaps=[g.message for g in validation.gaps if g.requirement_level == "REQUIRED"],
            )

    # ------------------------------------------------------------------
    # Step 9: Update document record with classification and metadata
    # ------------------------------------------------------------------
    try:
        update_document_metadata(
            supabase_client,
            document_id,
            classification=classification,
            extracted=extracted,
        )
    except IngestionError as exc:
        return _fail_document(supabase_client, document_id, exc.message)

    # ------------------------------------------------------------------
    # Step 10: Chunk document
    # ------------------------------------------------------------------
    try:
        chunks = chunk_document(parsed)
    except Exception as exc:
        return _fail_document(
            supabase_client, document_id, f"Chunking failed: {exc}"
        )

    if not chunks:
        return _fail_document(
            supabase_client, document_id,
            "No extractable text found in document",
        )

    # ------------------------------------------------------------------
    # Step 11: Embed chunks via Gemini Embeddings API
    # ------------------------------------------------------------------
    try:
        embedded_chunks = embed_chunks(chunks)
    except IngestionError as exc:
        return _fail_document(supabase_client, document_id, exc.message)

    # ------------------------------------------------------------------
    # Step 12: Store chunks to Supabase pgvector
    # store_chunks handles its own rollback and status update
    # (STORED on success, FAILED on failure)
    # ------------------------------------------------------------------
    try:
        chunk_count = store_chunks(document_id, request.project_id, embedded_chunks)
    except IngestionError as exc:
        # store_chunks already set status to FAILED and rolled back
        return IngestionResult(
            document_id=document_id,
            status="FAILED",
            classification=classification,
            extracted_metadata=extracted,
            validation=validation,
            queued_for_review=queued_for_review,
            error_message=exc.message,
        )

    logger.info(
        "document_ingested_successfully",
        document_id=str(document_id),
        document_type=classification.document_type_name,
        confidence=classification.confidence,
        chunk_count=chunk_count,
        queued_for_review=queued_for_review,
    )

    return IngestionResult(
        document_id=document_id,
        status="STORED",
        classification=classification,
        extracted_metadata=extracted,
        validation=validation,
        queued_for_review=queued_for_review,
    )


def _fail_document(
    supabase_client: SupabaseClient,
    document_id: uuid.UUID,
    error_message: str,
) -> IngestionResult:
    """
    Mark a document as FAILED and return an IngestionResult.
    Used when any pipeline step encounters a fatal error.
    """
    logger.error(
        "document_ingestion_failed",
        document_id=str(document_id),
        error=error_message,
    )

    try:
        update_status(supabase_client, document_id, "FAILED", error_message=error_message)
    except IngestionError as inner_exc:
        logger.error(
            "failed_to_mark_document_as_failed",
            document_id=str(document_id),
            original_error=error_message,
            status_update_error=inner_exc.message,
        )

    return IngestionResult(
        document_id=document_id,
        status="FAILED",
        error_message=error_message,
    )
