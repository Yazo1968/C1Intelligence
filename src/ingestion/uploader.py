"""
C1 — Gemini Two-Step Upload
Step 1: Upload file via Files API (temporary File object, 48h TTL).
Step 2: Import into File Search store with custom metadata.

Split across the pipeline: step 1 happens before classification,
step 2 happens after classification (when document_type and tier are known).
"""

from __future__ import annotations

import time
from typing import Any

from google import genai

from src.config import GEMINI_POLL_INTERVAL_SECONDS, GEMINI_POLL_MAX_ATTEMPTS
from src.logging_config import get_logger
from src.ingestion.models import IngestionError

logger = get_logger(__name__)


def poll_operation(
    gemini_client: genai.Client,
    operation: Any,
    max_attempts: int = GEMINI_POLL_MAX_ATTEMPTS,
    interval_seconds: int = GEMINI_POLL_INTERVAL_SECONDS,
) -> Any:
    """
    Poll a Gemini long-running operation until done.
    Raises IngestionError if max_attempts exceeded.
    """
    attempts = 0
    while not operation.done:
        if attempts >= max_attempts:
            raise IngestionError(
                stage="gemini_poll",
                message=(
                    f"Gemini operation did not complete after "
                    f"{max_attempts * interval_seconds} seconds."
                ),
            )
        time.sleep(interval_seconds)
        operation = gemini_client.operations.get(operation)
        attempts += 1

    return operation


def upload_file_to_gemini(
    gemini_client: genai.Client,
    file_path: str,
    display_name: str,
) -> tuple[str, str]:
    """
    Step 1: Upload a file to the Gemini Files API.
    Returns a tuple of (file_name, file_uri):
      - file_name: short reference (e.g., "files/abc123") — used for store import
      - file_uri: full URI (e.g., "https://generativelanguage.googleapis.com/v1beta/files/abc123")
                  — required by generate_content FileData
    The File object has a 48-hour TTL and is deleted automatically.
    """
    try:
        file_obj = gemini_client.files.upload(
            file=file_path,
            config={"display_name": display_name},
        )
    except Exception as exc:
        raise IngestionError(
            stage="gemini_file_upload",
            message=f"Failed to upload file to Gemini Files API: {exc}",
        ) from exc

    logger.info(
        "gemini_file_uploaded",
        file_name=file_obj.name,
        file_uri=file_obj.uri,
        display_name=display_name,
    )

    return file_obj.name, file_obj.uri


def import_to_store_with_metadata(
    gemini_client: genai.Client,
    store_name: str,
    gemini_file_name: str,
    metadata: dict[str, str | int],
) -> str:
    """
    Step 2: Import an already-uploaded file into a File Search store
    with custom metadata for retrieval-time filtering.

    Required metadata keys: project_id, document_type, tier, document_date, supabase_document_id.

    Returns the Gemini document name within the store.
    """
    custom_metadata = _build_custom_metadata(metadata)

    try:
        operation = gemini_client.file_search_stores.import_file(
            file_search_store_name=store_name,
            file_name=gemini_file_name,
            config={"custom_metadata": custom_metadata},
        )
    except Exception as exc:
        raise IngestionError(
            stage="gemini_store_import",
            message=f"Failed to import file into Gemini store: {exc}",
        ) from exc

    operation = poll_operation(gemini_client, operation)

    # The operation result contains the document reference
    document_name = getattr(operation, "name", None) or gemini_file_name

    logger.info(
        "gemini_document_imported",
        store_name=store_name,
        gemini_file_name=gemini_file_name,
        document_name=document_name,
        metadata_keys=list(metadata.keys()),
    )

    return document_name


def _build_custom_metadata(metadata: dict[str, str | int]) -> list[dict[str, Any]]:
    """
    Convert a flat dict into Gemini's custom_metadata format.
    String values use 'string_value', numeric values use 'numeric_value'.
    """
    result: list[dict[str, Any]] = []
    for key, value in metadata.items():
        if isinstance(value, int):
            result.append({"key": key, "numeric_value": value})
        else:
            result.append({"key": key, "string_value": str(value)})
    return result
