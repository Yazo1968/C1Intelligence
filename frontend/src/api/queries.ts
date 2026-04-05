import { apiClient } from './client';
import type { QueryAcceptedResponse, QueryStatusResponse, QueryLogEntry, ContradictionResponse } from './types';

export interface DomainRecommendation {
  domain: string;
  relevance: 'PRIMARY' | 'RELEVANT' | 'NOT_APPLICABLE';
  reason: string;
}

export interface Round0Assessment {
  executive_brief: string;
  documents_retrieved: string[];
  domain_recommendations: DomainRecommendation[];
  default_domains: string[];
}

export function submitQuery(
  projectId: string,
  queryText: string,
  domains?: string[]
): Promise<QueryAcceptedResponse> {
  return apiClient.post<QueryAcceptedResponse>(`/projects/${projectId}/query`, {
    query_text: queryText,
    ...(domains && domains.length > 0 ? { domains } : {}),
  });
}

export function assessQuery(
  projectId: string,
  queryText: string
): Promise<Round0Assessment> {
  return apiClient.post<Round0Assessment>(
    `/projects/${projectId}/query/assess`,
    { query_text: queryText }
  );
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
