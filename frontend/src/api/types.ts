// TypeScript interfaces mirroring backend Pydantic schemas exactly

export interface ProjectResponse {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentResponse {
  id: string;
  project_id: string;
  document_type_id: number | null;
  document_type_name: string | null;
  category: string | null;
  contract_id: string | null;
  filename: string;
  status: 'QUEUED' | 'EXTRACTING' | 'CLASSIFYING' | 'STORED' | 'FAILED';
  tier: number | null;
  document_date: string | null;
  document_reference_number: string | null;
  issuing_party_id: string | null;
  receiving_party_id: string | null;
  fidic_clause_ref: string | null;
  document_status: string | null;
  language: string | null;
  revision_number: string | null;
  time_bar_deadline: string | null;
  upload_notes: string | null;
  uploaded_by: string;
  created_at: string;
  updated_at: string;
}

export interface ClassificationInfo {
  document_type_id: number;
  document_type_name: string;
  category: string;
  tier: number;
  confidence: number;
  reasoning: string;
}

export interface ValidationGap {
  field_name: string;
  requirement_level: string;
  message: string;
}

export interface DocumentUploadResponse {
  document_id: string;
  status: string;
  queued_for_review: boolean;
  classification: ClassificationInfo | null;
  validation_gaps: ValidationGap[] | null;
  error_message: string | null;
  message: string | null;
}

export interface DocumentDownloadResponse {
  download_url: string;
  filename: string;
  expires_in: number;
}

export interface DocumentStatusResponse {
  document_id: string;
  status: 'QUEUED' | 'EXTRACTING' | 'CLASSIFYING' | 'STORED' | 'FAILED';
  filename: string;
}

export interface SpecialistFinding {
  domain: string;
  findings: string;
  confidence: string;
  sources_used: string[];
  tools_called: string[];
  round_number: number;
  flagged_contradictions: string[];
}

export interface Contradiction {
  field_name: string;
  document_a_reference: string;
  value_a: string;
  document_b_reference: string;
  value_b: string;
  description: string;
}

export type Confidence = 'GREEN' | 'AMBER' | 'RED' | 'GREY';

export interface QueryAcceptedResponse {
  query_id: string;
  status: string;
  message: string;
}

export interface QueryStatusResponse {
  query_id: string;
  status: 'PROCESSING' | 'COMPLETE' | 'FAILED';
  response: QueryResponseSchema | null;
}

export interface QueryResponseSchema {
  query_text: string;
  response_text: string;
  confidence: Confidence;
  domains_engaged: string[];
  specialist_findings: SpecialistFinding[];
  contradictions: Contradiction[];
  document_ids_at_query_time: string[];
  audit_log_id: string | null;
}

export interface QueryLogEntry {
  id: string;
  project_id: string;
  user_id: string;
  query_text: string;
  response_text: string;
  confidence: Confidence;
  domains_engaged: string[] | null;
  document_ids_at_query_time: string[] | null;
  citations: unknown;
  created_at: string;
}

export interface ContradictionResponse {
  id: string;
  project_id: string;
  document_a_id: string;
  document_b_id: string;
  field_name: string;
  description: string | null;
  created_at: string;
}

export interface ApiError {
  error_code: string;
  message: string;
  document_id?: string;
  query_id?: string;
}

// ---------------------------------------------------------------------------
// Governance — Three-Level Model
// ---------------------------------------------------------------------------

export interface GovernanceRunResponse {
  run_id: string;
  project_id: string;
  run_type: string;
  status: string;
  triggered_at: string;
}

export interface GovernanceStatusResponse {
  project_id: string;
  status:
    | 'not_established'
    | 'processing'
    | 'parties_identified'
    | 'established'
    | 'stale'
    | 'failed';
  last_run_at: string | null;
  last_run_id: string | null;
  events_confirmed: number;
  events_flagged: number;
  events_inferred: number;
  parties_count: number;
}

export interface PartyRoleResponse {
  id: string;
  party_identity_id: string;
  project_id: string;
  role_title: string;
  role_category: string;
  governing_instrument: string | null;
  governing_instrument_type: string | null;
  effective_from: string | null;
  effective_to: string | null;
  authority_scope: string | null;
  financial_threshold: string | null;
  financial_currency: string | null;
  appointment_status: 'proposed' | 'pending' | 'executed';
  source_clause: string | null;
  confirmation_status: 'confirmed' | 'assumed';
  created_at: string;
}

export interface PartyIdentityResponse {
  id: string;
  project_id: string;
  entity_type: 'organisation' | 'individual';
  legal_name: string;
  trading_names: string[];
  registration_number: string | null;
  party_category: string;
  is_internal: boolean;
  identification_status: 'confirmed' | 'assumed';
  roles: PartyRoleResponse[];
  created_at: string;
}

export interface ReconciliationQuestionResponse {
  id: string;
  project_id: string;
  run_id: string;
  question_type: string;
  question_text: string;
  parties_referenced: string[];
  documents_referenced: string[];
  options_presented: string[];
  answer_selected: string | null;
  user_free_text: string | null;
  answered_at: string | null;
  sequence_number: number;
  created_at: string;
}

export interface InterviewStatusResponse {
  project_id: string;
  run_id: string;
  total_questions: number;
  answered_questions: number;
  pending_questions: number;
  interview_complete: boolean;
}

export interface AuthorityEventResponse {
  id: string;
  project_id: string;
  party_role_id: string;
  party_identity_id: string;
  event_type: string;
  appointment_status: 'proposed' | 'pending' | 'executed';
  event_date: string | null;
  event_date_certain: boolean;
  end_date: string | null;
  authority_before: string | null;
  authority_after: string | null;
  financial_threshold_before: string | null;
  financial_threshold_after: string | null;
  missing_action: string | null;
  instrument_status: string;
  confirmation_status: 'confirmed' | 'assumed';
  source_clause: string | null;
  created_at: string;
}
