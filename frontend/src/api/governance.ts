import { apiClient } from './client';
import type {
  AuthorityEventResponse,
  GovernanceRunResponse,
  GovernanceStatusResponse,
  InterviewStatusResponse,
  PartyIdentityResponse,
  ReconciliationQuestionResponse,
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

export async function listPartyIdentities(
  projectId: string,
): Promise<PartyIdentityResponse[]> {
  return apiClient.get<PartyIdentityResponse[]>(
    `/projects/${projectId}/governance/parties`,
  );
}

export async function getInterviewStatus(
  projectId: string,
): Promise<InterviewStatusResponse> {
  return apiClient.get<InterviewStatusResponse>(
    `/projects/${projectId}/governance/interview`,
  );
}

export async function getNextInterviewQuestion(
  projectId: string,
): Promise<ReconciliationQuestionResponse> {
  return apiClient.get<ReconciliationQuestionResponse>(
    `/projects/${projectId}/governance/interview/next-question`,
  );
}

export async function submitInterviewAnswer(
  projectId: string,
  questionId: string,
  answer: string,
  freeText?: string,
): Promise<ReconciliationQuestionResponse> {
  return apiClient.post<ReconciliationQuestionResponse>(
    `/projects/${projectId}/governance/interview/questions/${questionId}/answer`,
    { answer_selected: answer, user_free_text: freeText ?? null },
  );
}

export async function extractAuthorityEvents(
  projectId: string,
): Promise<GovernanceRunResponse> {
  return apiClient.post<GovernanceRunResponse>(
    `/projects/${projectId}/governance/extract-events`,
    {},
  );
}

export async function listAuthorityEvents(
  projectId: string,
): Promise<AuthorityEventResponse[]> {
  return apiClient.get<AuthorityEventResponse[]>(
    `/projects/${projectId}/governance/authority-events`,
  );
}
