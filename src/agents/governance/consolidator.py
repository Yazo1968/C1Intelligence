"""
C1 — Entity Consolidator (Governance Function 1)
Pure Python post-processing of raw entity extraction results.
Zero LLM calls. Zero Supabase writes.

Responsibilities:
1. Normalise all extracted names (lowercase, strip punctuation)
2. Group name variants that normalise to the same string
3. Pick a canonical name (most frequently seen raw variant)
4. Detect discrepancies requiring user resolution
5. Return ConsolidatedDirectory ready for the API route to persist
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field

from src.agents.governance.entity_extractor import ExtractionResult, RawEntity


# ── Output dataclasses ────────────────────────────────────────────────────────

@dataclass
class ProposedEntity:
    entity_type: str                    # "organisation" | "individual"
    canonical_name: str                 # Most frequent raw variant
    name_variants: list[str]            # All other raw variants seen
    title: str | None                   # Individuals only
    context_sample: str                 # Context from first occurrence


@dataclass
class ProposedDiscrepancy:
    discrepancy_type: str               # "name_variant" | "possible_duplicate" | "ambiguous_individual"
    description: str
    name_a: str
    name_b: str | None


@dataclass
class ConsolidatedDirectory:
    organisations: list[ProposedEntity] = field(default_factory=list)
    individuals: list[ProposedEntity] = field(default_factory=list)
    discrepancies: list[ProposedDiscrepancy] = field(default_factory=list)


# ── Normalisation ─────────────────────────────────────────────────────────────

def _normalise(name: str) -> str:
    """
    Reduce a name to a stable comparison key.
    Lowercase, strip accents, remove punctuation except spaces, collapse whitespace.
    """
    # Unicode normalise and strip accents
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_approx = "".join(c for c in nfkd if not unicodedata.combining(c))
    # Lowercase
    lower = ascii_approx.lower()
    # Remove punctuation except spaces (keep hyphens as spaces)
    cleaned = re.sub(r"[-]", " ", lower)
    cleaned = re.sub(r"[^\w\s]", "", cleaned)
    # Collapse whitespace
    return re.sub(r"\s+", " ", cleaned).strip()


# ── Grouping ──────────────────────────────────────────────────────────────────

def _group_entities(
    raw_list: list[RawEntity],
) -> list[tuple[str, list[RawEntity]]]:
    """
    Group RawEntity entries by normalised name.
    Returns list of (normalised_key, [RawEntity, ...]) sorted by frequency desc.
    """
    groups: dict[str, list[RawEntity]] = {}
    for entity in raw_list:
        key = _normalise(entity.name)
        if not key:
            continue
        groups.setdefault(key, []).append(entity)
    # Sort groups by occurrence count descending
    return sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)


def _pick_canonical(entities: list[RawEntity]) -> str:
    """Return the most frequently seen raw name variant."""
    counts = Counter(e.name for e in entities)
    return counts.most_common(1)[0][0]


def _collect_variants(entities: list[RawEntity], canonical: str) -> list[str]:
    """Return unique raw variants excluding the canonical name."""
    seen = set()
    variants = []
    for e in entities:
        if e.name != canonical and e.name not in seen:
            seen.add(e.name)
            variants.append(e.name)
    return variants


# ── Discrepancy detection ─────────────────────────────────────────────────────

_LEGAL_SUFFIXES = re.compile(
    r"\b(llc|ltd|l\.l\.c|l\.t\.d|pjsc|llp|inc|co|corp|"
    r"establishment|est|trading|group|holding|holdings|"
    r"construction|development|contracting|consulting|"
    r"engineering|management|services|international|"
    r"middle\s*east|uae|dubai|abu\s*dhabi|sharjah)\b",
    re.IGNORECASE,
)


def _strip_legal_suffix(name: str) -> str:
    return _LEGAL_SUFFIXES.sub("", _normalise(name)).strip()


def _detect_organisation_discrepancies(
    groups: list[tuple[str, list[RawEntity]]],
) -> list[ProposedDiscrepancy]:
    """
    Detect possible duplicate organisations:
    Two groups whose suffix-stripped normalised names share a long common prefix
    (>= 6 chars) are flagged as possible_duplicate.
    """
    discrepancies: list[ProposedDiscrepancy] = []
    stripped = [(key, _strip_legal_suffix(key), groups_list) for key, groups_list in groups]

    checked: set[frozenset[str]] = set()
    for i, (key_a, core_a, entities_a) in enumerate(stripped):
        for key_b, core_b, entities_b in stripped[i + 1 :]:
            pair = frozenset([key_a, key_b])
            if pair in checked or not core_a or not core_b:
                continue
            # Common prefix length after stripping suffixes
            common = 0
            for ca, cb in zip(core_a, core_b):
                if ca == cb:
                    common += 1
                else:
                    break
            if common >= 6:
                checked.add(pair)
                canonical_a = _pick_canonical(entities_a)
                canonical_b = _pick_canonical(entities_b)
                discrepancies.append(
                    ProposedDiscrepancy(
                        discrepancy_type="possible_duplicate",
                        description=(
                            f'"{canonical_a}" and "{canonical_b}" share a common '
                            f"root name. They may be the same organisation under "
                            f"different registered names."
                        ),
                        name_a=canonical_a,
                        name_b=canonical_b,
                    )
                )
    return discrepancies


def _detect_individual_discrepancies(
    groups: list[tuple[str, list[RawEntity]]],
) -> list[ProposedDiscrepancy]:
    """
    Flag individuals whose normalised name is very short (<= 2 tokens)
    as ambiguous — they may be initials only.
    """
    discrepancies: list[ProposedDiscrepancy] = []
    for _key, entities in groups:
        canonical = _pick_canonical(entities)
        token_count = len(canonical.split())
        if token_count <= 1:
            discrepancies.append(
                ProposedDiscrepancy(
                    discrepancy_type="ambiguous_individual",
                    description=(
                        f'"{canonical}" appears to be a single name or initials only. '
                        f"Confirm this is a distinct individual."
                    ),
                    name_a=canonical,
                    name_b=None,
                )
            )
        # Name variant discrepancy: same group has 3+ distinct raw names
        variants = _collect_variants(entities, canonical)
        if len(variants) >= 2:
            discrepancies.append(
                ProposedDiscrepancy(
                    discrepancy_type="name_variant",
                    description=(
                        f'"{canonical}" appears under {len(variants) + 1} different '
                        f"name forms. Confirm these all refer to the same individual."
                    ),
                    name_a=canonical,
                    name_b=variants[0],
                )
            )
    return discrepancies


# ── Main entry point ──────────────────────────────────────────────────────────

def consolidate(extraction: ExtractionResult) -> ConsolidatedDirectory:
    """
    Consolidate raw extraction results into a ConsolidatedDirectory.
    Called by the API route after run_entity_extraction() returns.
    """
    directory = ConsolidatedDirectory()

    # Organisations
    org_groups = _group_entities(extraction.organisations)
    for _key, entities in org_groups:
        canonical = _pick_canonical(entities)
        variants = _collect_variants(entities, canonical)
        directory.organisations.append(
            ProposedEntity(
                entity_type="organisation",
                canonical_name=canonical,
                name_variants=variants,
                title=None,
                context_sample=entities[0].context,
            )
        )
    directory.discrepancies.extend(
        _detect_organisation_discrepancies(org_groups)
    )

    # Individuals
    ind_groups = _group_entities(extraction.individuals)
    for _key, entities in ind_groups:
        canonical = _pick_canonical(entities)
        variants = _collect_variants(entities, canonical)
        # Title: most common title seen for this individual (or None)
        titles = [e.title for e in entities if e.title]
        title = Counter(titles).most_common(1)[0][0] if titles else None
        directory.individuals.append(
            ProposedEntity(
                entity_type="individual",
                canonical_name=canonical,
                name_variants=variants,
                title=title,
                context_sample=entities[0].context,
            )
        )
    directory.discrepancies.extend(
        _detect_individual_discrepancies(ind_groups)
    )

    return directory
