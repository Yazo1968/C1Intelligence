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

// =============================================================================
// Governance — Function 1: Entity Directory
// =============================================================================

export interface EntityDirectoryRunResponse {
  id: string;
  project_id: string;
  status: 'running' | 'awaiting_confirmation' | 'confirmed' | 'failed';
  chunks_processed: number;
  total_chunks: number;
  organisations_found: number;
  individuals_found: number;
  error_message: string | null;
}

export interface EntityResponse {
  id: string;
  project_id: string;
  run_id: string;
  entity_type: 'organisation' | 'individual';
  canonical_name: string;
  name_variants: string[];
  short_address: string | null;
  title: string | null;
  confirmation_status: 'proposed' | 'confirmed' | 'merged' | 'rejected';
  user_note: string | null;
}

export interface EntityDiscrepancyResponse {
  id: string;
  project_id: string;
  run_id: string;
  discrepancy_type: 'name_variant' | 'possible_duplicate' | 'ambiguous_individual';
  description: string;
  name_a: string;
  name_b: string | null;
  chunk_references: string[];
  resolution: string | null;
  resolved_canonical: string | null;
  user_note: string | null;
}

export interface PatchEntityRequest {
  canonical_name?: string;
  confirmation_status?: 'confirmed' | 'rejected';
  user_note?: string;
}

export interface ResolveDiscrepancyRequest {
  resolution: 'same_entity' | 'different_entities' | 'correction';
  resolved_canonical?: string;
  user_note?: string;
}

// =============================================================================
// Governance — Function 2: Event Log
// =============================================================================

export interface EventLogRunResponse {
  id: string;
  project_id: string;
  entity_id: string;
  status: 'running' | 'awaiting_confirmation' | 'confirmed' | 'failed';
  triggered_at: string;
  completed_at: string | null;
  chunks_scanned: number;
  events_extracted: number;
  error_message: string | null;
}

export interface EntityEventResponse {
  id: string;
  project_id: string;
  entity_id: string;
  run_id: string;
  event_type: string;
  event_date: string | null;
  event_date_certain: boolean;
  status_before: string | null;
  status_after: string | null;
  initiated_by: string | null;
  authorised_by: string | null;
  source_document: string | null;
  source_excerpt: string | null;
  confirmation_status: 'proposed' | 'confirmed' | 'disputed' | 'rejected';
  user_note: string | null;
  sequence_number: number;
}

export interface EventLogQuestionResponse {
  id: string;
  project_id: string;
  run_id: string;
  entity_id: string;
  question_text: string;
  question_type:
    | 'date_conflict'
    | 'missing_authorisation'
    | 'overlapping_roles'
    | 'termination_without_replacement'
    | 'gap_in_timeline'
    | 'ambiguous_event';
  events_referenced: string[];
  answer: string | null;
  sequence_number: number;
}

export interface PatchEventRequest {
  event_type?: string;
  event_date?: string;
  event_date_certain?: boolean;
  status_before?: string;
  status_after?: string;
  initiated_by?: string;
  authorised_by?: string;
  confirmation_status?: 'confirmed' | 'disputed' | 'rejected';
  user_note?: string;
}

export interface AnswerQuestionRequest {
  answer: string;
}
