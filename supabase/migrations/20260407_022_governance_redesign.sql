-- Migration 022: Governance Redesign (Clean Slate)
-- Drops all old governance tables. Creates new governance schema.

-- ── PHASE 0: DROP OLD TABLES ─────────────────────────────────────────────────

DROP TABLE IF EXISTS reconciliation_questions CASCADE;
DROP TABLE IF EXISTS assumption_register CASCADE;
DROP TABLE IF EXISTS authority_events CASCADE;
DROP TABLE IF EXISTS party_roles CASCADE;
DROP TABLE IF EXISTS party_identities CASCADE;
DROP TABLE IF EXISTS governance_run_log CASCADE;
DROP TABLE IF EXISTS parties CASCADE;
DROP TABLE IF EXISTS contracts CASCADE;

-- ── PHASE 1: NEW TABLES ──────────────────────────────────────────────────────

CREATE TABLE entity_directory_runs (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    status              text NOT NULL DEFAULT 'running',
    triggered_at        timestamptz NOT NULL DEFAULT now(),
    completed_at        timestamptz,
    chunks_processed    integer NOT NULL DEFAULT 0,
    total_chunks        integer NOT NULL DEFAULT 0,
    organisations_found integer NOT NULL DEFAULT 0,
    individuals_found   integer NOT NULL DEFAULT 0,
    error_message       text,
    created_at          timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE entities (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    run_id              uuid NOT NULL REFERENCES entity_directory_runs(id),
    entity_type         text NOT NULL,
    canonical_name      text NOT NULL,
    name_variants       text[] NOT NULL DEFAULT '{}',
    short_address       text,
    title               text,
    confirmation_status text NOT NULL DEFAULT 'proposed',
    user_note           text,
    created_at          timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE entity_discrepancies (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    run_id              uuid NOT NULL REFERENCES entity_directory_runs(id),
    discrepancy_type    text NOT NULL,
    description         text NOT NULL,
    name_a              text NOT NULL,
    name_b              text,
    chunk_references    text[] NOT NULL DEFAULT '{}',
    resolution          text,
    resolved_canonical  text,
    resolved_by         uuid REFERENCES auth.users(id),
    resolved_at         timestamptz,
    user_note           text,
    created_at          timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE event_log_runs (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    entity_id           uuid NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    status              text NOT NULL DEFAULT 'running',
    triggered_at        timestamptz NOT NULL DEFAULT now(),
    completed_at        timestamptz,
    chunks_scanned      integer NOT NULL DEFAULT 0,
    events_extracted    integer NOT NULL DEFAULT 0,
    error_message       text,
    created_at          timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE entity_events (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    entity_id           uuid NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    run_id              uuid NOT NULL REFERENCES event_log_runs(id),
    event_type          text NOT NULL,
    event_date          date,
    event_date_certain  boolean NOT NULL DEFAULT true,
    status_before       text,
    status_after        text,
    initiated_by        text,
    authorised_by       text,
    source_document     text,
    source_excerpt      text,
    confirmation_status text NOT NULL DEFAULT 'proposed',
    user_note           text,
    sequence_number     integer NOT NULL DEFAULT 0,
    created_at          timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE event_log_questions (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    run_id              uuid NOT NULL REFERENCES event_log_runs(id),
    entity_id           uuid NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    question_text       text NOT NULL,
    question_type       text NOT NULL,
    events_referenced   uuid[] NOT NULL DEFAULT '{}',
    answer              text,
    answered_by         uuid REFERENCES auth.users(id),
    answered_at         timestamptz,
    sequence_number     integer NOT NULL DEFAULT 0,
    created_at          timestamptz NOT NULL DEFAULT now()
);
