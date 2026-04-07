import { apiClient } from './client';
import type {
  EntityDirectoryRunResponse,
  EntityResponse,
  EntityDiscrepancyResponse,
  PatchEntityRequest,
  ResolveDiscrepancyRequest,
  EventLogRunResponse,
  EntityEventResponse,
  EventLogQuestionResponse,
  PatchEventRequest,
  AnswerQuestionRequest,
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

// ── Function 2: Event Log ─────────────────────────────────────────────────────

export function triggerEventRun(
  projectId: string,
  entityId: string,
): Promise<EventLogRunResponse> {
  return apiClient.post<EventLogRunResponse>(
    `${base(projectId)}/entities/${entityId}/events/run`,
    {},
  );
}

export function getEventRunStatus(
  projectId: string,
  entityId: string,
): Promise<EventLogRunResponse> {
  return apiClient.get<EventLogRunResponse>(
    `${base(projectId)}/entities/${entityId}/events/status`,
  );
}

export function listEvents(
  projectId: string,
  entityId: string,
): Promise<EntityEventResponse[]> {
  return apiClient.get<EntityEventResponse[]>(
    `${base(projectId)}/entities/${entityId}/events`,
  );
}

export function listEventQuestions(
  projectId: string,
  entityId: string,
): Promise<EventLogQuestionResponse[]> {
  return apiClient.get<EventLogQuestionResponse[]>(
    `${base(projectId)}/entities/${entityId}/events/questions`,
  );
}

export function patchEvent(
  projectId: string,
  entityId: string,
  eventId: string,
  body: PatchEventRequest,
): Promise<EntityEventResponse> {
  return apiClient.patch<EntityEventResponse>(
    `${base(projectId)}/entities/${entityId}/events/${eventId}`,
    { ...body },
  );
}

export function answerQuestion(
  projectId: string,
  entityId: string,
  questionId: string,
  body: AnswerQuestionRequest,
): Promise<EventLogQuestionResponse> {
  return apiClient.post<EventLogQuestionResponse>(
    `${base(projectId)}/entities/${entityId}/events/questions/${questionId}/answer`,
    { ...body },
  );
}

export function confirmEventLog(
  projectId: string,
  entityId: string,
): Promise<EventLogRunResponse> {
  return apiClient.post<EventLogRunResponse>(
    `${base(projectId)}/entities/${entityId}/events/confirm`,
    {},
  );
}
