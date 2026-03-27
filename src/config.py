"""
C1 — Configuration
Loads all settings from environment variables. Fails loud on missing required vars.
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)


def _require_env(name: str) -> str:
    """Return the value of an environment variable or raise if missing."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Required environment variable {name} is not set")
    return value


# ---------------------------------------------------------------------------
# API Keys & Credentials
# ---------------------------------------------------------------------------
GEMINI_API_KEY: str = _require_env("GEMINI_API_KEY")
ANTHROPIC_API_KEY: str = _require_env("ANTHROPIC_API_KEY")
SUPABASE_URL: str = _require_env("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY: str = _require_env("SUPABASE_SERVICE_ROLE_KEY")

# ---------------------------------------------------------------------------
# Model Configuration
# ---------------------------------------------------------------------------
CLAUDE_MODEL: str = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")

# ---------------------------------------------------------------------------
# Ingestion Constants
# ---------------------------------------------------------------------------
MAX_FILE_SIZE_BYTES: int = 100 * 1024 * 1024  # 100 MB — Gemini File Search limit
CLASSIFICATION_CONFIDENCE_THRESHOLD: float = 0.75

ALLOWED_EXTENSIONS: set[str] = {
    ".pdf", ".docx", ".xlsx", ".pptx", ".csv",
    ".jpg", ".jpeg", ".png",
}

ALLOWED_MIME_TYPES: dict[str, str] = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".csv": "text/csv",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}

# ---------------------------------------------------------------------------
# Gemini Polling
# ---------------------------------------------------------------------------
GEMINI_POLL_INTERVAL_SECONDS: int = 3
GEMINI_POLL_MAX_ATTEMPTS: int = 60  # 3 minutes max wait
