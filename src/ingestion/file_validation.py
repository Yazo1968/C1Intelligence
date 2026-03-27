"""
C1 — File Validation
Validates incoming files before any Gemini interaction.
"""

import os

from src.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES
from src.ingestion.models import IngestionError


def validate_file(filename: str, file_size_bytes: int) -> None:
    """
    Validate that a file is acceptable for ingestion.

    Raises IngestionError if:
    - File extension is not in ALLOWED_EXTENSIONS
    - File size exceeds MAX_FILE_SIZE_BYTES (100 MB)
    - File is empty (0 bytes)
    """
    extension = os.path.splitext(filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise IngestionError(
            stage="file_validation",
            message=(
                f"Unsupported file type '{extension}'. "
                f"Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            ),
        )

    if file_size_bytes == 0:
        raise IngestionError(
            stage="file_validation",
            message="File is empty (0 bytes).",
        )

    if file_size_bytes > MAX_FILE_SIZE_BYTES:
        size_mb = file_size_bytes / (1024 * 1024)
        limit_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
        raise IngestionError(
            stage="file_validation",
            message=f"File size ({size_mb:.1f} MB) exceeds maximum ({limit_mb:.0f} MB).",
        )
