import { apiClient } from './client';
import type { ProjectResponse } from './types';

export function listProjects(): Promise<ProjectResponse[]> {
  return apiClient.get<ProjectResponse[]>('/projects');
}

export function createProject(name: string, description?: string): Promise<ProjectResponse> {
  return apiClient.post<ProjectResponse>('/projects', { name, description: description ?? null });
}
