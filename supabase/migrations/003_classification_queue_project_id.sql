-- =============================================================================
-- C1 — Construction Documentation Intelligence Platform
-- Migration 003: Add denormalized project_id to classification_queue
-- =============================================================================
-- Eliminates correlated subquery in RLS policies by storing project_id
-- directly on classification_queue. FK enforces referential integrity.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. Add project_id column with FK to projects
-- ---------------------------------------------------------------------------
ALTER TABLE classification_queue
    ADD COLUMN project_id uuid NOT NULL REFERENCES projects(id);

-- ---------------------------------------------------------------------------
-- 2. Drop old RLS policies that used correlated subqueries
-- ---------------------------------------------------------------------------
DROP POLICY classification_queue_select ON classification_queue;
DROP POLICY classification_queue_insert ON classification_queue;
DROP POLICY classification_queue_update ON classification_queue;
DROP POLICY classification_queue_delete ON classification_queue;

-- ---------------------------------------------------------------------------
-- 3. Create new RLS policies using direct project_id column
-- ---------------------------------------------------------------------------
CREATE POLICY classification_queue_select ON classification_queue
    FOR SELECT TO authenticated
    USING (is_project_owner(project_id));

CREATE POLICY classification_queue_insert ON classification_queue
    FOR INSERT TO authenticated
    WITH CHECK (is_project_owner(project_id));

CREATE POLICY classification_queue_update ON classification_queue
    FOR UPDATE TO authenticated
    USING (is_project_owner(project_id))
    WITH CHECK (is_project_owner(project_id));

CREATE POLICY classification_queue_delete ON classification_queue
    FOR DELETE TO authenticated
    USING (is_project_owner(project_id));

-- =============================================================================
-- END OF MIGRATION 003
-- =============================================================================
