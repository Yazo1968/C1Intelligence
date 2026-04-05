import { apiClient } from './client';
import type {
  GovernancePartyResponse,
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

export async function listGovernanceParties(
  projectId: string,
): Promise<GovernancePartyResponse[]> {
  return apiClient.get<GovernancePartyResponse[]>(
    `/projects/${projectId}/governance/parties`,
  );
}

export async function updateGovernanceParty(
  projectId: string,
  partyId: string,
  update: { confirmation_status: 'confirmed' | 'flagged' | 'inferred' },
): Promise<GovernancePartyResponse> {
  return apiClient.patch<GovernancePartyResponse>(
    `/projects/${projectId}/governance/parties/${partyId}`,
    update as unknown as Record<string, unknown>,
  );
}

export async function confirmParties(
  projectId: string,
): Promise<GovernanceRunResponse> {
  return apiClient.post<GovernanceRunResponse>(
    `/projects/${projectId}/governance/confirm-parties`,
    {},
  );
}
