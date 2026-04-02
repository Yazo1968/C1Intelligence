import { apiClient } from './client';
import type { DocumentResponse, DocumentStatusResponse, DocumentUploadResponse } from './types';

export function listDocuments(projectId: string): Promise<DocumentResponse[]> {
  return apiClient.get<DocumentResponse[]>(`/projects/${projectId}/documents`);
}

export function getDocument(projectId: string, docId: string): Promise<DocumentResponse> {
  return apiClient.get<DocumentResponse>(`/projects/${projectId}/documents/${docId}`);
}

export function getDocumentStatus(projectId: string, docId: string): Promise<DocumentStatusResponse> {
  return apiClient.get<DocumentStatusResponse>(`/projects/${projectId}/documents/${docId}/status`);
}

export function uploadDocument(
  projectId: string,
  file: File,
  opts?: { contract_id?: string; user_selected_type_id?: number; upload_notes?: string },
): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  if (opts?.contract_id) formData.append('contract_id', opts.contract_id);
  if (opts?.user_selected_type_id != null) formData.append('user_selected_type_id', String(opts.user_selected_type_id));
  if (opts?.upload_notes) formData.append('upload_notes', opts.upload_notes);
  return apiClient.postFormData<DocumentUploadResponse>(`/projects/${projectId}/documents`, formData);
}
