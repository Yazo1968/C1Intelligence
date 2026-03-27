-- =============================================================================
-- C1 — Construction Documentation Intelligence Platform
-- Migration 001: Initial Schema
-- =============================================================================
-- Creates all 8 tables, immutability trigger on query_log, RLS on all tables,
-- and seeds 176 document types from C1_TAXONOMY_v0.4.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. projects
-- ---------------------------------------------------------------------------
CREATE TABLE projects (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    name            text        NOT NULL,
    description     text,
    gemini_store_name text,
    owner_id        uuid        NOT NULL REFERENCES auth.users(id),
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------------
-- 2. contracts
-- ---------------------------------------------------------------------------
CREATE TABLE contracts (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      uuid        NOT NULL REFERENCES projects(id),
    name            text        NOT NULL,
    contract_type   text,
    fidic_edition   text        CHECK (fidic_edition IN ('1999', '2017')),
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE contracts ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------------
-- 3. parties
-- ---------------------------------------------------------------------------
CREATE TABLE parties (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      uuid        NOT NULL REFERENCES projects(id),
    name            text        NOT NULL,
    role            text        NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE parties ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------------
-- 4. document_types
-- ---------------------------------------------------------------------------
CREATE TABLE document_types (
    id              integer     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category        text        NOT NULL,
    name            text        NOT NULL,
    possible_formats text[]     NOT NULL DEFAULT '{}',
    tier            smallint    NOT NULL CHECK (tier IN (1, 2, 3)),
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE document_types ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------------
-- 5. documents
-- ---------------------------------------------------------------------------
CREATE TABLE documents (
    id                          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id                  uuid        NOT NULL REFERENCES projects(id),
    document_type_id            integer     REFERENCES document_types(id),
    contract_id                 uuid        REFERENCES contracts(id),
    filename                    text        NOT NULL,
    status                      text        NOT NULL CHECK (status IN ('QUEUED', 'EXTRACTING', 'CLASSIFYING', 'STORED', 'FAILED')),
    gemini_file_name            text,
    gemini_document_name        text,
    document_date               date,
    document_reference_number   text,
    issuing_party_id            uuid        REFERENCES parties(id),
    receiving_party_id          uuid        REFERENCES parties(id),
    fidic_clause_ref            text,
    document_status             text,
    language                    text,
    revision_number             text,
    time_bar_deadline           date,
    upload_notes                text,
    uploaded_by                 uuid        NOT NULL REFERENCES auth.users(id),
    created_at                  timestamptz NOT NULL DEFAULT now(),
    updated_at                  timestamptz NOT NULL DEFAULT now(),

    -- Composite unique needed for contradiction_flags same-project enforcement
    UNIQUE (id, project_id)
);

ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------------
-- 6. contradiction_flags
-- ---------------------------------------------------------------------------
CREATE TABLE contradiction_flags (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      uuid        NOT NULL REFERENCES projects(id),
    document_a_id   uuid        NOT NULL,
    document_b_id   uuid        NOT NULL,
    field_name      text        NOT NULL,
    description     text,
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now(),

    -- Composite FKs enforce that both documents belong to the same project
    FOREIGN KEY (document_a_id, project_id) REFERENCES documents(id, project_id),
    FOREIGN KEY (document_b_id, project_id) REFERENCES documents(id, project_id)
);

ALTER TABLE contradiction_flags ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------------
-- 7. query_log
-- ---------------------------------------------------------------------------
CREATE TABLE query_log (
    id                          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id                  uuid        NOT NULL REFERENCES projects(id),
    user_id                     uuid        NOT NULL REFERENCES auth.users(id),
    query_text                  text        NOT NULL,
    response_text               text        NOT NULL,
    confidence                  text        NOT NULL CHECK (confidence IN ('GREEN', 'AMBER', 'RED', 'GREY')),
    domains_engaged             text[],
    document_ids_at_query_time  uuid[],
    citations                   jsonb,
    created_at                  timestamptz NOT NULL DEFAULT now(),
    updated_at                  timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE query_log ENABLE ROW LEVEL SECURITY;

-- Immutability trigger: block all UPDATE and DELETE on query_log
CREATE OR REPLACE FUNCTION prevent_query_log_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'query_log is immutable. UPDATE and DELETE operations are not permitted.';
    RETURN NULL;
END;
$$;

CREATE TRIGGER trg_query_log_immutable
    BEFORE UPDATE OR DELETE ON query_log
    FOR EACH ROW
    EXECUTE FUNCTION prevent_query_log_mutation();

-- ---------------------------------------------------------------------------
-- 8. classification_queue
-- ---------------------------------------------------------------------------
CREATE TABLE classification_queue (
    id                uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id       uuid        NOT NULL REFERENCES documents(id),
    reason            text        NOT NULL,
    suggested_type_id integer     REFERENCES document_types(id),
    resolved          boolean     NOT NULL DEFAULT false,
    resolved_by       uuid        REFERENCES auth.users(id),
    resolved_at       timestamptz,
    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE classification_queue ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------------
-- updated_at auto-update trigger function
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

-- Apply to all tables except query_log (immutable — trigger blocks updates anyway)
CREATE TRIGGER trg_projects_updated_at
    BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_contracts_updated_at
    BEFORE UPDATE ON contracts FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_parties_updated_at
    BEFORE UPDATE ON parties FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_document_types_updated_at
    BEFORE UPDATE ON document_types FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_documents_updated_at
    BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_contradiction_flags_updated_at
    BEFORE UPDATE ON contradiction_flags FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_classification_queue_updated_at
    BEFORE UPDATE ON classification_queue FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =============================================================================
-- SEED: 176 document types from C1_TAXONOMY_v0.4.xlsx
-- =============================================================================

-- ---- Governance (16 types) ----
INSERT INTO document_types (category, name, possible_formats, tier) VALUES
('Governance', 'Project Charter', ARRAY['PDF','DOCX'], 2),
('Governance', 'Governance Framework', ARRAY['PDF','DOCX'], 2),
('Governance', 'Delegation of Authority (DOA)', ARRAY['PDF','DOCX','XLSX'], 2),
('Governance', 'Approval Matrix', ARRAY['PDF','XLSX'], 2),
('Governance', 'Organisation Chart', ARRAY['PDF'], 3),
('Governance', 'Committee / Steering Meeting Minutes', ARRAY['PDF','DOCX'], 2),
('Governance', 'Executive / Board Reports', ARRAY['PDF','PPTX','DOCX'], 1),
('Governance', 'Stage Gate Approvals', ARRAY['PDF','DOCX'], 1),
('Governance', 'Budget Approval', ARRAY['PDF','DOCX'], 1),
('Governance', 'Funding Approval', ARRAY['PDF','DOCX'], 1),
('Governance', 'Policies', ARRAY['PDF','DOCX'], 2),
('Governance', 'Procedures', ARRAY['PDF','DOCX'], 2),
('Governance', 'Audit Plan', ARRAY['PDF','DOCX'], 2),
('Governance', 'Audit Report', ARRAY['PDF','DOCX'], 1),
('Governance', 'Investigation Report', ARRAY['PDF','DOCX'], 1),
('Governance', 'Compliance Report', ARRAY['PDF','DOCX'], 1);

-- ---- Legal & Contractual (28 types) ----
INSERT INTO document_types (category, name, possible_formats, tier) VALUES
('Legal & Contractual', 'Contract Agreement (Main Contract)', ARRAY['PDF'], 1),
('Legal & Contractual', 'Contract Agreement (Consultant Appointment)', ARRAY['PDF'], 1),
('Legal & Contractual', 'Contract Agreement (Package Contract)', ARRAY['PDF'], 1),
('Legal & Contractual', 'Interface Agreement', ARRAY['PDF'], 1),
('Legal & Contractual', 'Letter of Acceptance / Award (LOA)', ARRAY['PDF'], 1),
('Legal & Contractual', 'Letter of Intent (LOI)', ARRAY['PDF'], 1),
('Legal & Contractual', 'Letter of Tender', ARRAY['PDF'], 1),
('Legal & Contractual', 'General Conditions (FIDIC)', ARRAY['PDF'], 2),
('Legal & Contractual', 'Particular Conditions', ARRAY['PDF','DOCX'], 1),
('Legal & Contractual', 'Contract Data / Appendix to Tender', ARRAY['PDF','DOCX'], 1),
('Legal & Contractual', 'Employer''s Requirements', ARRAY['PDF','DOCX'], 1),
('Legal & Contractual', 'Contractor''s Proposal', ARRAY['PDF','DOCX'], 1),
('Legal & Contractual', 'Addenda (Pre-Contract)', ARRAY['PDF','DOCX'], 2),
('Legal & Contractual', 'Tender Clarifications', ARRAY['PDF','DOCX'], 2),
('Legal & Contractual', 'Performance Bond', ARRAY['PDF'], 1),
('Legal & Contractual', 'Advance Payment Guarantee', ARRAY['PDF'], 1),
('Legal & Contractual', 'Retention Bond', ARRAY['PDF'], 1),
('Legal & Contractual', 'Parent Company Guarantee', ARRAY['PDF'], 1),
('Legal & Contractual', 'Insurance Policies (CAR, TPL, PI, Decennial)', ARRAY['PDF'], 1),
('Legal & Contractual', 'Contractual Notices (General)', ARRAY['PDF','DOCX'], 1),
('Legal & Contractual', 'Engineer''s Instructions', ARRAY['PDF','DOCX'], 1),
('Legal & Contractual', 'Engineer''s Determinations (FIDIC 3.7 [2017] / 3.5 [1999])', ARRAY['PDF','DOCX'], 1),
('Legal & Contractual', 'Contract Amendments / Addenda (Post-Contract)', ARRAY['PDF'], 1),
('Legal & Contractual', 'Side Letters', ARRAY['PDF'], 1),
('Legal & Contractual', 'Novation Agreement', ARRAY['PDF'], 1),
('Legal & Contractual', 'Collateral Warranty', ARRAY['PDF'], 1),
('Legal & Contractual', 'Settlement Agreement / Deed', ARRAY['PDF'], 1),
('Legal & Contractual', 'Dispute Notice / Notice of Dissatisfaction (NOD)', ARRAY['PDF','DOCX'], 1);

-- ---- Commercial & Financial (18 types) ----
INSERT INTO document_types (category, name, possible_formats, tier) VALUES
('Commercial & Financial', 'Bill of Quantities (BOQ)', ARRAY['PDF','XLSX'], 1),
('Commercial & Financial', 'Schedule of Prices / Rates', ARRAY['PDF','XLSX'], 1),
('Commercial & Financial', 'Cost Breakdown Structure (CBS)', ARRAY['PDF','XLSX'], 2),
('Commercial & Financial', 'Payment Application / Contractor''s Statement', ARRAY['PDF','XLSX'], 1),
('Commercial & Financial', 'Interim Payment Certificate (IPC) (FIDIC 14.6)', ARRAY['PDF'], 1),
('Commercial & Financial', 'Invoice', ARRAY['PDF'], 2),
('Commercial & Financial', 'Payment Record / Remittance Advice', ARRAY['PDF','XLSX'], 1),
('Commercial & Financial', 'Final Statement (Contractor''s)', ARRAY['PDF','XLSX'], 1),
('Commercial & Financial', 'Final Account', ARRAY['PDF','XLSX'], 1),
('Commercial & Financial', 'Final Payment Certificate (FIDIC 14.13)', ARRAY['PDF'], 1),
('Commercial & Financial', 'Variation Proposal / Contractor''s Quotation', ARRAY['PDF','DOCX','XLSX'], 1),
('Commercial & Financial', 'Variation Order (VO) (FIDIC Clause 13)', ARRAY['PDF','DOCX'], 1),
('Commercial & Financial', 'Daywork Sheets', ARRAY['PDF','XLSX'], 2),
('Commercial & Financial', 'Measurement Sheets', ARRAY['PDF','XLSX'], 2),
('Commercial & Financial', 'Cash Flow Forecast', ARRAY['PDF','XLSX'], 2),
('Commercial & Financial', 'Cost Report', ARRAY['PDF','XLSX','PPTX'], 1),
('Commercial & Financial', 'Project Budget', ARRAY['PDF','XLSX'], 1),
('Commercial & Financial', 'Liquidated Damages Notice & Calculation (FIDIC 8.7/8.8)', ARRAY['PDF','DOCX'], 1);

-- ---- PM & Controls (24 types) ----
INSERT INTO document_types (category, name, possible_formats, tier) VALUES
('PM & Controls', 'Business Case', ARRAY['PDF','DOCX','PPTX'], 2),
('PM & Controls', 'Feasibility Study', ARRAY['PDF','DOCX'], 2),
('PM & Controls', 'Project Management Plan (PMP)', ARRAY['PDF','DOCX'], 2),
('PM & Controls', 'Work Breakdown Structure (WBS)', ARRAY['PDF','XLSX'], 2),
('PM & Controls', 'Baseline Programme (FIDIC 8.3)', ARRAY['PDF','XER','MPP'], 1),
('PM & Controls', 'Revised Programme', ARRAY['PDF','XER','MPP'], 1),
('PM & Controls', 'Recovery Programme', ARRAY['PDF','XER','MPP'], 1),
('PM & Controls', 'Master Programme (Programme-wide)', ARRAY['PDF','XER','MPP'], 1),
('PM & Controls', 'Look-Ahead Schedule (3 / 6-week)', ARRAY['PDF','XLSX','XER'], 2),
('PM & Controls', 'As-Built Programme', ARRAY['PDF','XER','MPP'], 1),
('PM & Controls', 'Cost Baseline', ARRAY['PDF','XLSX'], 2),
('PM & Controls', 'Risk Management Plan', ARRAY['PDF','DOCX'], 2),
('PM & Controls', 'Risk Register', ARRAY['PDF','XLSX'], 1),
('PM & Controls', 'Quality Management Plan', ARRAY['PDF','DOCX'], 2),
('PM & Controls', 'HSE Plan', ARRAY['PDF','DOCX'], 2),
('PM & Controls', 'Procurement Plan', ARRAY['PDF','DOCX'], 2),
('PM & Controls', 'Communication Plan', ARRAY['PDF','DOCX'], 3),
('PM & Controls', 'Interface Management Plan', ARRAY['PDF','DOCX'], 2),
('PM & Controls', 'Monthly Progress Report', ARRAY['PDF','DOCX','PPTX'], 1),
('PM & Controls', 'KPI Reports', ARRAY['PDF','XLSX','PPTX'], 1),
('PM & Controls', 'Earned Value Report', ARRAY['PDF','XLSX'], 1),
('PM & Controls', 'Issue Log', ARRAY['PDF','XLSX'], 2),
('PM & Controls', 'Change Log / Variation Register', ARRAY['PDF','XLSX'], 2),
('PM & Controls', 'Lessons Learned Report', ARRAY['PDF','DOCX'], 3);

-- ---- Engineering & Design (14 types) ----
INSERT INTO document_types (category, name, possible_formats, tier) VALUES
('Engineering & Design', 'Design Basis Report', ARRAY['PDF','DOCX'], 1),
('Engineering & Design', 'Design Criteria', ARRAY['PDF','DOCX'], 2),
('Engineering & Design', 'Calculations', ARRAY['PDF','DOCX','XLSX'], 2),
('Engineering & Design', 'Drawings — Issued for Construction (IFC)', ARRAY['PDF','DWG','DXF','RVT'], 2),
('Engineering & Design', 'Specifications', ARRAY['PDF','DOCX'], 2),
('Engineering & Design', 'Shop Drawings / Submittals', ARRAY['PDF','DWG','DXF'], 2),
('Engineering & Design', 'Technical Reports', ARRAY['PDF','DOCX'], 1),
('Engineering & Design', 'BIM Models / BIM Execution Plan', ARRAY['PDF','RVT','IFC','NWD'], 2),
('Engineering & Design', 'Clash Reports', ARRAY['PDF','NWD'], 2),
('Engineering & Design', 'Value Engineering Reports', ARRAY['PDF','DOCX'], 1),
('Engineering & Design', 'Design Review Reports', ARRAY['PDF','DOCX'], 1),
('Engineering & Design', 'Design Change Notices (DCN)', ARRAY['PDF','DOCX'], 1),
('Engineering & Design', 'Request for Information (RFI)', ARRAY['PDF','DOCX'], 1),
('Engineering & Design', 'Response to RFI', ARRAY['PDF','DOCX'], 1);

-- ---- Procurement (12 types) ----
INSERT INTO document_types (category, name, possible_formats, tier) VALUES
('Procurement', 'Procurement Plan', ARRAY['PDF','DOCX'], 2),
('Procurement', 'Vendor Prequalification Records', ARRAY['PDF','DOCX','XLSX'], 2),
('Procurement', 'Tender Documents (Sub-packages)', ARRAY['PDF','DOCX'], 2),
('Procurement', 'Bid Evaluation Reports', ARRAY['PDF','DOCX','XLSX'], 1),
('Procurement', 'Purchase Orders', ARRAY['PDF','DOCX'], 2),
('Procurement', 'Subcontracts', ARRAY['PDF'], 1),
('Procurement', 'Vendor / Shop Drawings', ARRAY['PDF','DWG'], 2),
('Procurement', 'Vendor Datasheets / Product Data Sheets', ARRAY['PDF'], 2),
('Procurement', 'Factory Acceptance Test (FAT) Reports', ARRAY['PDF'], 2),
('Procurement', 'Material Certificates / Mill Certificates', ARRAY['PDF'], 1),
('Procurement', 'Delivery Notes / Waybills', ARRAY['PDF'], 2),
('Procurement', 'Shipping / Import Documents', ARRAY['PDF'], 2);

-- ---- Construction (19 types) ----
INSERT INTO document_types (category, name, possible_formats, tier) VALUES
('Construction', 'Method Statements', ARRAY['PDF','DOCX'], 2),
('Construction', 'Temporary Works Design', ARRAY['PDF','DWG'], 2),
('Construction', 'Work Permits / Permit to Work (PTW)', ARRAY['PDF','DOCX'], 2),
('Construction', 'Site Instructions (SI)', ARRAY['PDF','DOCX'], 1),
('Construction', 'Daily Site Reports', ARRAY['PDF','DOCX'], 1),
('Construction', 'Site Diaries / Engineer''s Diary', ARRAY['PDF','DOCX'], 1),
('Construction', 'Progress Photographs', ARRAY['JPG','PDF'], 2),
('Construction', 'Resource Reports (Labour & Plant)', ARRAY['PDF','XLSX'], 1),
('Construction', 'Equipment Utilisation Reports', ARRAY['PDF','XLSX'], 2),
('Construction', 'Field Change Requests', ARRAY['PDF','DOCX'], 2),
('Construction', 'Survey / Setting Out Records', ARRAY['PDF','DWG','XLSX'], 1),
('Construction', 'Meeting Minutes (Progress / Technical / Commercial)', ARRAY['PDF','DOCX'], 1),
('Construction', 'Early Warning Notices', ARRAY['PDF','DOCX'], 1),
('Construction', 'Suspension Notice — by Engineer (FIDIC 8.8)', ARRAY['PDF','DOCX'], 1),
('Construction', 'Suspension Notice — by Contractor (FIDIC 16.1)', ARRAY['PDF','DOCX'], 1),
('Construction', 'Termination Notice — by Employer (FIDIC 15.2)', ARRAY['PDF','DOCX'], 1),
('Construction', 'Termination Notice — by Contractor (FIDIC 16.2)', ARRAY['PDF','DOCX'], 1),
('Construction', 'Force Majeure / Exceptional Event Notice (FIDIC Cl. 18 [2017] / 19 [1999])', ARRAY['PDF','DOCX'], 1),
('Construction', 'Acceleration Instruction / Agreement', ARRAY['PDF','DOCX'], 1);

-- ---- Quality & HSE (12 types) ----
INSERT INTO document_types (category, name, possible_formats, tier) VALUES
('Quality & HSE', 'Project Quality Plan (PQP)', ARRAY['PDF','DOCX'], 2),
('Quality & HSE', 'Inspection & Test Plans (ITP)', ARRAY['PDF','DOCX','XLSX'], 2),
('Quality & HSE', 'Material Inspection Requests (MIR)', ARRAY['PDF','DOCX'], 2),
('Quality & HSE', 'Work Inspection Requests (WIR)', ARRAY['PDF','DOCX'], 2),
('Quality & HSE', 'Inspection Reports', ARRAY['PDF','DOCX'], 1),
('Quality & HSE', 'Test Reports', ARRAY['PDF','DOCX','XLSX'], 1),
('Quality & HSE', 'Non-Conformance Reports (NCR)', ARRAY['PDF','DOCX'], 1),
('Quality & HSE', 'Corrective Action Reports (CAR)', ARRAY['PDF','DOCX'], 1),
('Quality & HSE', 'Preventive Action Reports (PAR)', ARRAY['PDF','DOCX'], 2),
('Quality & HSE', 'Safety Reports (Weekly / Monthly)', ARRAY['PDF','DOCX'], 1),
('Quality & HSE', 'Incident / Accident Reports', ARRAY['PDF','DOCX'], 1),
('Quality & HSE', 'Environmental Reports', ARRAY['PDF','DOCX'], 1);

-- ---- Claims & Disputes (14 types) ----
INSERT INTO document_types (category, name, possible_formats, tier) VALUES
('Claims & Disputes', 'Notice of Claim (FIDIC 20.2.1 [2017] / 20.1 [1999])', ARRAY['PDF','DOCX'], 1),
('Claims & Disputes', 'Notice of Delay (FIDIC 8.5 [2017] / 8.4 [1999])', ARRAY['PDF','DOCX'], 1),
('Claims & Disputes', 'Extension of Time (EOT) Claim', ARRAY['PDF','DOCX'], 1),
('Claims & Disputes', 'Prolongation / Additional Cost Claim', ARRAY['PDF','DOCX','XLSX'], 1),
('Claims & Disputes', 'Disruption Claim', ARRAY['PDF','DOCX','XLSX'], 1),
('Claims & Disputes', 'Acceleration Claim', ARRAY['PDF','DOCX','XLSX'], 1),
('Claims & Disputes', 'Employer''s Claim (FIDIC 2.5 [1999] / 20.2 [2017])', ARRAY['PDF','DOCX'], 1),
('Claims & Disputes', 'Delay Analysis Report', ARRAY['PDF','DOCX','XER'], 1),
('Claims & Disputes', 'Expert Reports (Delay / Quantum / Technical)', ARRAY['PDF','DOCX'], 1),
('Claims & Disputes', 'Engineer''s Determination (FIDIC 3.7 [2017] / 3.5 [1999])', ARRAY['PDF','DOCX'], 1),
('Claims & Disputes', 'Notice of Dissatisfaction (NOD)', ARRAY['PDF','DOCX'], 1),
('Claims & Disputes', 'DAB / DAAB Decision (FIDIC 21.4 [2017] / 20.4 [1999])', ARRAY['PDF','DOCX'], 1),
('Claims & Disputes', 'Arbitration Notice / Request for Arbitration', ARRAY['PDF','DOCX'], 1),
('Claims & Disputes', 'Claim Settlement / Settlement Deed', ARRAY['PDF'], 1);

-- ---- Testing & Handover (19 types) ----
INSERT INTO document_types (category, name, possible_formats, tier) VALUES
('Testing & Handover', 'Testing Procedures', ARRAY['PDF','DOCX'], 2),
('Testing & Handover', 'Pre-Commissioning Reports', ARRAY['PDF','DOCX','XLSX'], 1),
('Testing & Handover', 'Commissioning Reports / Tests on Completion (FIDIC Cl. 9)', ARRAY['PDF','DOCX','XLSX'], 1),
('Testing & Handover', 'Performance Test Reports', ARRAY['PDF','DOCX','XLSX'], 1),
('Testing & Handover', 'Reliability Test Reports', ARRAY['PDF','DOCX'], 1),
('Testing & Handover', 'System Completion Certificates', ARRAY['PDF'], 1),
('Testing & Handover', 'Taking-Over Request — Contractor''s Application', ARRAY['PDF','DOCX'], 2),
('Testing & Handover', 'Taking-Over Certificate (FIDIC 10.1)', ARRAY['PDF'], 1),
('Testing & Handover', 'Snagging / Punch List', ARRAY['PDF','XLSX'], 2),
('Testing & Handover', 'Defects Notification & Rectification Notice (FIDIC Cl. 11)', ARRAY['PDF','DOCX'], 1),
('Testing & Handover', 'As-Built Drawings', ARRAY['PDF','DWG','RVT'], 2),
('Testing & Handover', 'O&M Manuals', ARRAY['PDF','DOCX'], 2),
('Testing & Handover', 'Training Records', ARRAY['PDF','DOCX'], 3),
('Testing & Handover', 'Asset Register', ARRAY['PDF','XLSX'], 2),
('Testing & Handover', 'Warranties & Guarantees (Equipment / Works)', ARRAY['PDF'], 1),
('Testing & Handover', 'Final Payment Certificate (FIDIC 14.13)', ARRAY['PDF'], 1),
('Testing & Handover', 'Performance / Defects Certificate (FIDIC 11.9)', ARRAY['PDF'], 1),
('Testing & Handover', 'Handover Certificate (Operational)', ARRAY['PDF'], 1),
('Testing & Handover', 'Authority Completion / Occupation Certificate', ARRAY['PDF'], 1);

-- =============================================================================
-- END OF MIGRATION 001
-- =============================================================================
