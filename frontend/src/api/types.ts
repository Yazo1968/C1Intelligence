// TypeScript interfaces mirroring backend Pydantic schemas exactly

export interface ProjectResponse {
  id: string;
  name: string;
  description: string | null;
  gemini_store_name: string | null;
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
  gemini_file_name: string | null;
  gemini_document_name: string | null;
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
}

export interface Citation {
  document_id: string | null;
  document_type: string | null;
  document_date: string | null;
  document_reference: string | null;
  excerpt: string | null;
}

export interface KeyFinding {
  statement: string;
  citations: Citation[];
}

export interface SpecialistFinding {
  domain: string;
  analysis: string;
  key_findings: KeyFinding[];
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
