import { apiClient } from './client';
import type {
  GovernanceRunResponse,
  GovernanceStatusResponse,
  PartyIdentityResponse,
  ReconciliationQuestionResponse,
  ReconciliationAnswerRequest,
  InterviewStatusResponse,
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
): Promise<ReconciliationQuestionResponse | null> {
  return apiClient.get<ReconciliationQuestionResponse | null>(
    `/projects/${projectId}/governance/interview/next-question`,
  );
}

export async function submitInterviewAnswer(
  projectId: string,
  questionId: string,
  answer: ReconciliationAnswerRequest,
): Promise<ReconciliationQuestionResponse> {
  return apiClient.post<ReconciliationQuestionResponse>(
    `/projects/${projectId}/governance/interview/questions/${questionId}/answer`,
    answer as unknown as Record<string, unknown>,
  );
}
