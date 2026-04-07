import { apiClient } from './client';
import type {
  EntityDirectoryRunResponse,
  EntityResponse,
  EntityDiscrepancyResponse,
  PatchEntityRequest,
  ResolveDiscrepancyRequest,
} from './types';

const base = (projectId: string) =>
  `/projects/${projectId}/governance`;

// ── Function 1: Entity Directory ──────────────────────────────────────────────

export function triggerDirectoryRun(
  projectId: string,
): Promise<EntityDirectoryRunResponse> {
  return apiClient.post<EntityDirectoryRunResponse>(
    `${base(projectId)}/directory/run`,
    {},
  );
}

export function getDirectoryStatus(
  projectId: string,
): Promise<EntityDirectoryRunResponse> {
  return apiClient.get<EntityDirectoryRunResponse>(
    `${base(projectId)}/directory/status`,
  );
}

export function listEntities(
  projectId: string,
): Promise<EntityResponse[]> {
  return apiClient.get<EntityResponse[]>(
    `${base(projectId)}/directory/entities`,
  );
}

export function listDiscrepancies(
  projectId: string,
): Promise<EntityDiscrepancyResponse[]> {
  return apiClient.get<EntityDiscrepancyResponse[]>(
    `${base(projectId)}/directory/discrepancies`,
  );
}

export function patchEntity(
  projectId: string,
  entityId: string,
  body: PatchEntityRequest,
): Promise<EntityResponse> {
  return apiClient.patch<EntityResponse>(
    `${base(projectId)}/directory/entities/${entityId}`,
    { ...body },
  );
}

export function resolveDiscrepancy(
  projectId: string,
  discrepancyId: string,
  body: ResolveDiscrepancyRequest,
): Promise<EntityDiscrepancyResponse> {
  return apiClient.post<EntityDiscrepancyResponse>(
    `${base(projectId)}/directory/discrepancies/${discrepancyId}/resolve`,
    { ...body },
  );
}

export function confirmDirectory(
  projectId: string,
): Promise<EntityDirectoryRunResponse> {
  return apiClient.post<EntityDirectoryRunResponse>(
    `${base(projectId)}/directory/confirm`,
    {},
  );
}
