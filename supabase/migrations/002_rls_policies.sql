-- =============================================================================
-- C1 — Construction Documentation Intelligence Platform
-- Migration 002: Row Level Security Policies
-- =============================================================================
-- All tables had RLS enabled in 001 with deny-all default.
-- This migration adds explicit policies for authenticated users.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Helper: check if the current user owns a given project
-- Used by all project-scoped tables to enforce ownership.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION is_project_owner(p_project_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
AS $$
    SELECT EXISTS (
        SELECT 1 FROM projects
        WHERE id = p_project_id
        AND owner_id = auth.uid()
    );
$$;

-- ---------------------------------------------------------------------------
-- 1. projects — owner-only access
-- ---------------------------------------------------------------------------
CREATE POLICY projects_select ON projects
    FOR SELECT TO authenticated
    USING (owner_id = auth.uid());

CREATE POLICY projects_insert ON projects
    FOR INSERT TO authenticated
    WITH CHECK (owner_id = auth.uid());

CREATE POLICY projects_update ON projects
    FOR UPDATE TO authenticated
    USING (owner_id = auth.uid())
    WITH CHECK (owner_id = auth.uid());

CREATE POLICY projects_delete ON projects
    FOR DELETE TO authenticated
    USING (owner_id = auth.uid());

-- ---------------------------------------------------------------------------
-- 2. contracts — project-owner access
-- ---------------------------------------------------------------------------
CREATE POLICY contracts_select ON contracts
    FOR SELECT TO authenticated
    USING (is_project_owner(project_id));

CREATE POLICY contracts_insert ON contracts
    FOR INSERT TO authenticated
    WITH CHECK (is_project_owner(project_id));

CREATE POLICY contracts_update ON contracts
    FOR UPDATE TO authenticated
    USING (is_project_owner(project_id))
    WITH CHECK (is_project_owner(project_id));

CREATE POLICY contracts_delete ON contracts
    FOR DELETE TO authenticated
    USING (is_project_owner(project_id));

-- ---------------------------------------------------------------------------
-- 3. parties — project-owner access
-- ---------------------------------------------------------------------------
CREATE POLICY parties_select ON parties
    FOR SELECT TO authenticated
    USING (is_project_owner(project_id));

CREATE POLICY parties_insert ON parties
    FOR INSERT TO authenticated
    WITH CHECK (is_project_owner(project_id));

CREATE POLICY parties_update ON parties
    FOR UPDATE TO authenticated
    USING (is_project_owner(project_id))
    WITH CHECK (is_project_owner(project_id));

CREATE POLICY parties_delete ON parties
    FOR DELETE TO authenticated
    USING (is_project_owner(project_id));

-- ---------------------------------------------------------------------------
-- 4. document_types — read-only for all authenticated users
-- ---------------------------------------------------------------------------
CREATE POLICY document_types_select ON document_types
    FOR SELECT TO authenticated
    USING (true);

-- No INSERT, UPDATE, or DELETE policies. Seed data only.

-- ---------------------------------------------------------------------------
-- 5. documents — project-owner access
-- ---------------------------------------------------------------------------
CREATE POLICY documents_select ON documents
    FOR SELECT TO authenticated
    USING (is_project_owner(project_id));

CREATE POLICY documents_insert ON documents
    FOR INSERT TO authenticated
    WITH CHECK (is_project_owner(project_id));

CREATE POLICY documents_update ON documents
    FOR UPDATE TO authenticated
    USING (is_project_owner(project_id))
    WITH CHECK (is_project_owner(project_id));

CREATE POLICY documents_delete ON documents
    FOR DELETE TO authenticated
    USING (is_project_owner(project_id));

-- ---------------------------------------------------------------------------
-- 6. contradiction_flags — project-owner access
-- ---------------------------------------------------------------------------
CREATE POLICY contradiction_flags_select ON contradiction_flags
    FOR SELECT TO authenticated
    USING (is_project_owner(project_id));

CREATE POLICY contradiction_flags_insert ON contradiction_flags
    FOR INSERT TO authenticated
    WITH CHECK (is_project_owner(project_id));

CREATE POLICY contradiction_flags_update ON contradiction_flags
    FOR UPDATE TO authenticated
    USING (is_project_owner(project_id))
    WITH CHECK (is_project_owner(project_id));

CREATE POLICY contradiction_flags_delete ON contradiction_flags
    FOR DELETE TO authenticated
    USING (is_project_owner(project_id));

-- ---------------------------------------------------------------------------
-- 7. query_log — project-owner SELECT and INSERT only
--    UPDATE and DELETE are already blocked by the immutability trigger.
--    No UPDATE/DELETE policies needed — the trigger is the enforcement layer.
-- ---------------------------------------------------------------------------
CREATE POLICY query_log_select ON query_log
    FOR SELECT TO authenticated
    USING (is_project_owner(project_id));

CREATE POLICY query_log_insert ON query_log
    FOR INSERT TO authenticated
    WITH CHECK (is_project_owner(project_id));

-- ---------------------------------------------------------------------------
-- 8. classification_queue — project-owner access via document's project
-- ---------------------------------------------------------------------------
CREATE POLICY classification_queue_select ON classification_queue
    FOR SELECT TO authenticated
    USING (
        is_project_owner(
            (SELECT d.project_id FROM documents d WHERE d.id = document_id)
        )
    );

CREATE POLICY classification_queue_insert ON classification_queue
    FOR INSERT TO authenticated
    WITH CHECK (
        is_project_owner(
            (SELECT d.project_id FROM documents d WHERE d.id = document_id)
        )
    );

CREATE POLICY classification_queue_update ON classification_queue
    FOR UPDATE TO authenticated
    USING (
        is_project_owner(
            (SELECT d.project_id FROM documents d WHERE d.id = document_id)
        )
    )
    WITH CHECK (
        is_project_owner(
            (SELECT d.project_id FROM documents d WHERE d.id = document_id)
        )
    );

CREATE POLICY classification_queue_delete ON classification_queue
    FOR DELETE TO authenticated
    USING (
        is_project_owner(
            (SELECT d.project_id FROM documents d WHERE d.id = document_id)
        )
    );

-- =============================================================================
-- END OF MIGRATION 002
-- =============================================================================
