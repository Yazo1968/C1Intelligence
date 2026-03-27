"""
C1 — Taxonomy Cache
Loads all 176 document types from Supabase and caches them in memory.
Provides lookup methods and a formatted string for Claude classification prompts.
"""

from __future__ import annotations

from supabase import Client as SupabaseClient

from src.logging_config import get_logger
from src.ingestion.models import DocumentTypeRow, IngestionError

logger = get_logger(__name__)


class TaxonomyCache:
    """
    In-memory cache of the document_types table.
    Load once at startup, reuse across all classification calls.
    """

    def __init__(self) -> None:
        self._types: list[DocumentTypeRow] = []
        self._by_id: dict[int, DocumentTypeRow] = {}
        self._by_name: dict[str, DocumentTypeRow] = {}
        self._prompt_text: str = ""
        self._loaded: bool = False

    @property
    def is_loaded(self) -> bool:
        """Whether the cache has been loaded from Supabase."""
        return self._loaded

    def load(self, supabase_client: SupabaseClient) -> None:
        """Load all document types from Supabase."""
        try:
            response = (
                supabase_client.table("document_types")
                .select("id, category, name, possible_formats, tier")
                .order("id")
                .execute()
            )
        except Exception as exc:
            raise IngestionError(
                stage="taxonomy_cache",
                message=f"Failed to load document types from Supabase: {exc}",
            ) from exc

        rows = response.data
        if not rows:
            raise IngestionError(
                stage="taxonomy_cache",
                message="document_types table is empty. Seed data missing.",
            )

        self._types = [DocumentTypeRow(**row) for row in rows]
        self._by_id = {dt.id: dt for dt in self._types}
        self._by_name = {dt.name.lower(): dt for dt in self._types}
        self._prompt_text = self._build_prompt_text()
        self._loaded = True

        logger.info("taxonomy_cache_loaded", count=len(self._types))

    def get_by_id(self, type_id: int) -> DocumentTypeRow | None:
        """Look up a document type by its integer ID."""
        return self._by_id.get(type_id)

    def get_by_name(self, name: str) -> DocumentTypeRow | None:
        """Look up a document type by name (case-insensitive)."""
        return self._by_name.get(name.lower())

    def get_all(self) -> list[DocumentTypeRow]:
        """Return all cached document types."""
        return list(self._types)

    def get_prompt_formatted_list(self) -> str:
        """
        Return the full taxonomy formatted for inclusion in a Claude system prompt.
        Grouped by category with clear structure for LLM consumption.
        """
        if not self._loaded:
            raise IngestionError(
                stage="taxonomy_cache",
                message="Taxonomy cache not loaded. Call load() first.",
            )
        return self._prompt_text

    def _build_prompt_text(self) -> str:
        """Build the formatted taxonomy string, grouped by category."""
        categories: dict[str, list[DocumentTypeRow]] = {}
        for dt in self._types:
            categories.setdefault(dt.category, []).append(dt)

        lines: list[str] = []
        for category, types in categories.items():
            lines.append(f"\n## {category}")
            for dt in types:
                formats = ", ".join(dt.possible_formats)
                lines.append(f"  ID:{dt.id} | Tier:{dt.tier} | {dt.name} | Formats: {formats}")

        return "\n".join(lines)
