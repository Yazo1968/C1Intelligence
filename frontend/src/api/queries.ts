import { apiClient } from './client';
import type { QueryResponseSchema, QueryLogEntry, ContradictionResponse } from './types';

export function submitQuery(projectId: string, queryText: string): Promise<QueryResponseSchema> {
  return apiClient.post<QueryResponseSchema>(`/projects/${projectId}/query`, { query_text: queryText });
}

export function getQueryLog(projectId: string): Promise<QueryLogEntry[]> {
  return apiClient.get<QueryLogEntry[]>(`/projects/${projectId}/query-log`);
}

export function getContradictions(projectId: string): Promise<ContradictionResponse[]> {
  return apiClient.get<ContradictionResponse[]>(`/projects/${projectId}/contradictions`);
}
