"""
C1 — Tier-Based Metadata Validation
Checks that extracted metadata meets requirements for the document's tier level.
Flags gaps but does not block ingestion.
"""

from __future__ import annotations

from src.ingestion.models import ExtractedMetadata, ValidationGap, ValidationResult

# Tier 1 documents (Critical): money, time, liability, contractual enforceability
# Must have: reference number, date, issuing party, receiving party
TIER_REQUIRED_FIELDS: dict[int, list[str]] = {
    1: [
        "document_reference_number",
        "document_date",
        "issuing_party_name",
        "receiving_party_name",
    ],
    2: [
        "document_date",
    ],
    3: [],
}

TIER_RECOMMENDED_FIELDS: dict[int, list[str]] = {
    1: [
        "fidic_clause_ref",
        "language",
        "revision_number",
    ],
    2: [
        "document_reference_number",
        "issuing_party_name",
        "receiving_party_name",
    ],
    3: [
        "document_date",
        "document_reference_number",
    ],
}

FIELD_DISPLAY_NAMES: dict[str, str] = {
    "document_reference_number": "Document Reference Number",
    "document_date": "Document Date",
    "issuing_party_name": "Issuing Party",
    "receiving_party_name": "Receiving Party",
    "fidic_clause_ref": "FIDIC Clause Reference",
    "language": "Language",
    "revision_number": "Revision Number",
}


def validate_metadata_for_tier(
    extracted: ExtractedMetadata,
    tier: int,
) -> ValidationResult:
    """
    Check extracted metadata against tier-specific requirements.

    Tier 1 (Critical) REQUIRES: reference number, date, issuing party, receiving party.
    Tier 2 (Important) REQUIRES: date.
    Tier 3 (Supporting) REQUIRES: nothing.

    Gaps are informational — they flag missing fields but do not block ingestion.
    """
    gaps: list[ValidationGap] = []
    metadata_dict = extracted.model_dump()

    # Check required fields
    required_fields = TIER_REQUIRED_FIELDS.get(tier, [])
    for field_name in required_fields:
        value = metadata_dict.get(field_name)
        if value is None or (isinstance(value, str) and not value.strip()):
            display = FIELD_DISPLAY_NAMES.get(field_name, field_name)
            gaps.append(
                ValidationGap(
                    field_name=field_name,
                    requirement_level="REQUIRED",
                    message=f"Tier {tier} document is missing required field: {display}",
                )
            )

    # Check recommended fields
    recommended_fields = TIER_RECOMMENDED_FIELDS.get(tier, [])
    for field_name in recommended_fields:
        value = metadata_dict.get(field_name)
        if value is None or (isinstance(value, str) and not value.strip()):
            display = FIELD_DISPLAY_NAMES.get(field_name, field_name)
            gaps.append(
                ValidationGap(
                    field_name=field_name,
                    requirement_level="RECOMMENDED",
                    message=f"Tier {tier} document is missing recommended field: {display}",
                )
            )

    has_required = any(g.requirement_level == "REQUIRED" for g in gaps)
    has_recommended = any(g.requirement_level == "RECOMMENDED" for g in gaps)

    return ValidationResult(
        tier=tier,
        gaps=gaps,
        has_required_gaps=has_required,
        has_recommended_gaps=has_recommended,
    )
