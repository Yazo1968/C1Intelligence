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

import datetime
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


# =============================================================================
# Function 2 — Event Consolidation
# =============================================================================

from src.agents.governance.event_extractor import RawEvent


@dataclass
class ProposedEvent:
    event_type: str
    event_date: str | None
    event_date_certain: bool
    status_before: str | None
    status_after: str | None
    initiated_by: str | None
    authorised_by: str | None
    source_document: str | None
    source_excerpt: str | None
    sequence_number: int = 0
    chunk_index: int = 0


@dataclass
class ProposedQuestion:
    question_type: str      # date_conflict | missing_authorisation | overlapping_roles |
                            # termination_without_replacement | gap_in_timeline | ambiguous_event
    question_text: str
    event_indices: list[int] = field(default_factory=list)   # indices into ProposedEvent list


@dataclass
class ConsolidatedEventLog:
    events: list[ProposedEvent] = field(default_factory=list)
    questions: list[ProposedQuestion] = field(default_factory=list)


# ── Deduplication ─────────────────────────────────────────────────────────────

def _dedup_events(raw_events: list[RawEvent]) -> list[RawEvent]:
    """
    Remove duplicate events: same event_type + same event_date + same status_after.
    Keep the first occurrence (lowest chunk_index).
    """
    seen: set[tuple] = set()
    unique: list[RawEvent] = []
    for event in raw_events:
        key = (
            event.event_type,
            event.event_date or "",
            (event.status_after or "").lower().strip()[:80],
        )
        if key not in seen:
            seen.add(key)
            unique.append(event)
    return unique


# ── Sorting ───────────────────────────────────────────────────────────────────

def _sort_events(events: list[RawEvent]) -> list[RawEvent]:
    """
    Sort events: known dates ascending first, then unknown dates by chunk_index.
    """
    def sort_key(e: RawEvent):
        if e.event_date:
            try:
                parsed = datetime.date.fromisoformat(e.event_date)
                return (0, parsed, e.chunk_index)
            except ValueError:
                pass
        return (1, datetime.date.max, e.chunk_index)

    return sorted(events, key=sort_key)


# ── Question generation ───────────────────────────────────────────────────────

def _generate_questions(events: list[ProposedEvent]) -> list[ProposedQuestion]:
    questions: list[ProposedQuestion] = []

    # date_conflict: two events on the same known date with different status_after
    dated = [e for e in events if e.event_date and e.event_date_certain]
    by_date: dict[str, list[int]] = {}
    for i, e in enumerate(events):
        if e.event_date and e.event_date_certain:
            by_date.setdefault(e.event_date, []).append(i)
    for date, indices in by_date.items():
        if len(indices) >= 2:
            statuses = {events[i].status_after for i in indices if events[i].status_after}
            if len(statuses) > 1:
                questions.append(ProposedQuestion(
                    question_type="date_conflict",
                    question_text=(
                        f"Two or more events on {date} show different authority positions. "
                        f"Which event correctly reflects the outcome on that date?"
                    ),
                    event_indices=indices,
                ))

    # missing_authorisation: appointment or authority_grant with no authorised_by
    for i, e in enumerate(events):
        if e.event_type in ("appointment", "authority_grant") and not e.authorised_by:
            questions.append(ProposedQuestion(
                question_type="missing_authorisation",
                question_text=(
                    f"The {e.event_type} event"
                    + (f" on {e.event_date}" if e.event_date else "")
                    + " has no recorded authorising party. "
                    "Was this authorisation verbal, absent, or documented elsewhere?"
                ),
                event_indices=[i],
            ))

    # overlapping_roles: two appointment events with no termination between them
    appointments = [i for i, e in enumerate(events) if e.event_type == "appointment"]
    if len(appointments) >= 2:
        for j in range(len(appointments) - 1):
            idx_a = appointments[j]
            idx_b = appointments[j + 1]
            # Check if there is any termination/replacement between idx_a and idx_b
            between = [
                e.event_type for e in events[idx_a + 1 : idx_b]
                if e.event_type in ("termination", "replacement", "suspension", "role_transfer")
            ]
            if not between:
                questions.append(ProposedQuestion(
                    question_type="overlapping_roles",
                    question_text=(
                        "Two appointment events appear without a termination or replacement "
                        "between them. Was the first appointment superseded, or do both "
                        "appointments apply simultaneously?"
                    ),
                    event_indices=[idx_a, idx_b],
                ))

    # termination_without_replacement: termination is the last event in the log
    termination_indices = [
        i for i, e in enumerate(events)
        if e.event_type in ("termination", "suspension")
    ]
    if termination_indices:
        last_term = termination_indices[-1]
        if last_term == len(events) - 1:
            questions.append(ProposedQuestion(
                question_type="termination_without_replacement",
                question_text=(
                    "The log ends with a termination or suspension event. "
                    "Was this entity replaced, or did the role cease entirely?"
                ),
                event_indices=[last_term],
            ))

    return questions


# ── Main entry point ──────────────────────────────────────────────────────────

def consolidate_events(raw_events: list[RawEvent]) -> ConsolidatedEventLog:
    """
    Consolidate raw event extraction results.
    Called by the API route after run_event_extraction() returns.
    Zero LLM calls. Zero Supabase writes.
    """
    if not raw_events:
        return ConsolidatedEventLog()

    deduped = _dedup_events(raw_events)
    sorted_events = _sort_events(deduped)

    proposed: list[ProposedEvent] = []
    for seq, raw in enumerate(sorted_events):
        proposed.append(ProposedEvent(
            event_type=raw.event_type,
            event_date=raw.event_date,
            event_date_certain=raw.event_date_certain,
            status_before=raw.status_before,
            status_after=raw.status_after,
            initiated_by=raw.initiated_by,
            authorised_by=raw.authorised_by,
            source_document=raw.source_document,
            source_excerpt=raw.source_excerpt,
            sequence_number=seq,
            chunk_index=raw.chunk_index,
        ))

    questions = _generate_questions(proposed)

    return ConsolidatedEventLog(events=proposed, questions=questions)


# =============================================================================
# Function 1 — DB-backed consolidation (two-stage path)
# =============================================================================

def consolidate_from_db(project_id: str, run_id: str) -> ConsolidatedDirectory:
    """
    Stage 2 consolidation. Reads raw extractions from entity_raw_extractions
    for this run, then applies the same grouping and discrepancy detection
    as consolidate().

    Called by the governance background task after run_entity_extraction()
    returns successfully. Zero LLM calls. Writes nothing — caller writes
    the ConsolidatedDirectory to entities + entity_discrepancies.
    """
    from src.clients import get_supabase_client

    supabase = get_supabase_client()
    resp = (
        supabase.table("entity_raw_extractions")
        .select("entity_type, name, title, context")
        .eq("project_id", project_id)
        .eq("run_id", run_id)
        .execute()
    )
    rows = resp.data or []

    # Re-build RawEntity lists from DB rows
    raw_orgs: list[RawEntity] = []
    raw_inds: list[RawEntity] = []
    for row in rows:
        if row["entity_type"] == "organisation":
            raw_orgs.append(
                RawEntity(
                    name=row["name"],
                    context=row.get("context") or "",
                )
            )
        elif row["entity_type"] == "individual":
            raw_inds.append(
                RawEntity(
                    name=row["name"],
                    context=row.get("context") or "",
                    title=row.get("title"),
                )
            )

    # Re-use the existing grouping and discrepancy logic unchanged
    directory = ConsolidatedDirectory()

    org_groups = _group_entities(raw_orgs)
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

    ind_groups = _group_entities(raw_inds)
    for _key, entities in ind_groups:
        canonical = _pick_canonical(entities)
        variants = _collect_variants(entities, canonical)
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
