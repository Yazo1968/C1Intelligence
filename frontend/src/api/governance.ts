import { apiClient } from './client';
import type {
  GovernanceRunResponse,
  GovernanceStatusResponse,
  GovernanceEventResponse,
  GovernanceEventUpdateRequest,
} from './types';

export async function runGovernance(
  projectId: string,
  runType: 'full' | 'incremental' = 'full',
): Promise<GovernanceRunResponse> {
  return apiClient.post<GovernanceRunResponse>(
    `/projects/${projectId}/governance/run`,
    { run_type: runType },
  );
}

export async function getGovernanceStatus(
  projectId: string,
): Promise<GovernanceStatusResponse> {
  return apiClient.get<GovernanceStatusResponse>(
    `/projects/${projectId}/governance/status`,
  );
}

export async function listGovernanceEvents(
  projectId: string,
): Promise<GovernanceEventResponse[]> {
  return apiClient.get<GovernanceEventResponse[]>(
    `/projects/${projectId}/governance/events`,
  );
}

export async function updateGovernanceEvent(
  projectId: string,
  eventId: string,
  update: GovernanceEventUpdateRequest,
): Promise<GovernanceEventResponse> {
  return apiClient.patch<GovernanceEventResponse>(
    `/projects/${projectId}/governance/events/${eventId}`,
    update as unknown as Record<string, unknown>,
  );
}
