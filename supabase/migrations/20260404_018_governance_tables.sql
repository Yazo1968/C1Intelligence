-- governance_parties: entity registry
CREATE TABLE governance_parties (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  entity_type text NOT NULL CHECK (entity_type IN ('organisation', 'individual')),
  canonical_name text NOT NULL,
  aliases text[] NOT NULL DEFAULT '{}',
  contractual_role text,
  terminus_node boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_governance_parties_project ON governance_parties(project_id);

-- governance_events: authority event log
CREATE TABLE governance_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  event_type text NOT NULL CHECK (event_type IN ('appointment','delegation','termination','replacement','modification','suspension')),
  effective_date date NOT NULL,
  end_date date,
  party_id uuid NOT NULL REFERENCES governance_parties(id) ON DELETE CASCADE,
  role text NOT NULL,
  appointed_by_party_id uuid REFERENCES governance_parties(id),
  authority_dimension text NOT NULL CHECK (authority_dimension IN ('layer_1','layer_2a','layer_2b')),
  contract_source text,
  scope text,
  terminus_node boolean NOT NULL DEFAULT false,
  source_document_id uuid REFERENCES documents(id),
  extraction_status text NOT NULL DEFAULT 'inferred' CHECK (extraction_status IN ('confirmed','flagged','inferred')),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_governance_events_project ON governance_events(project_id);
CREATE INDEX idx_governance_events_party ON governance_events(party_id);
CREATE INDEX idx_governance_events_effective_date ON governance_events(effective_date);

-- governance_run_log: records each governance run
CREATE TABLE governance_run_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  run_type text NOT NULL CHECK (run_type IN ('full','incremental')),
  triggered_at timestamptz NOT NULL DEFAULT now(),
  documents_scanned integer NOT NULL DEFAULT 0,
  events_extracted integer NOT NULL DEFAULT 0,
  status text NOT NULL DEFAULT 'running' CHECK (status IN ('running','complete','failed')),
  completed_at timestamptz
);

CREATE INDEX idx_governance_run_log_project ON governance_run_log(project_id);
