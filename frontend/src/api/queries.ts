import { apiClient } from './client';
import type { QueryAcceptedResponse, QueryStatusResponse, QueryLogEntry, ContradictionResponse } from './types';

export function submitQuery(
  projectId: string,
  queryText: string,
  riskMode: boolean = false
): Promise<QueryAcceptedResponse> {
  return apiClient.post<QueryAcceptedResponse>(`/projects/${projectId}/query`, {
    query_text: queryText,
    risk_mode: riskMode,
  });
}

export function getQueryStatus(projectId: string, queryId: string): Promise<QueryStatusResponse> {
  return apiClient.get<QueryStatusResponse>(`/projects/${projectId}/queries/${queryId}/status`);
}

export function getQueryLog(projectId: string): Promise<QueryLogEntry[]> {
  return apiClient.get<QueryLogEntry[]>(`/projects/${projectId}/query-log`);
}

export function getContradictions(projectId: string): Promise<ContradictionResponse[]> {
  return apiClient.get<ContradictionResponse[]>(`/projects/${projectId}/contradictions`);
}
