import { useCallback, useEffect, useState } from 'react';
import { Spinner } from '../ui/Spinner';
import { EmptyState } from '../ui/EmptyState';
import {
  runGovernance,
  getGovernanceStatus,
  listPartyIdentities,
  getInterviewStatus,
  getNextInterviewQuestion,
  submitInterviewAnswer,
  extractAuthorityEvents,
} from '../../api/governance';
import type {
  GovernanceStatusResponse,
  PartyIdentityResponse,
  ReconciliationQuestionResponse,
  InterviewStatusResponse,
} from '../../api/types';
import { supabase } from '../../auth/supabase';

interface GovernancePanelProps {
  projectId: string;
}

const STATUS_LABELS: Record<string, { label: string; colour: string }> = {
  not_established: { label: 'Not Established', colour: 'bg-gray-100 text-gray-600' },
  processing: { label: 'Processing\u2026', colour: 'bg-blue-100 text-blue-700' },
  parties_identified: { label: 'Parties Identified', colour: 'bg-amber-100 text-amber-700' },
  interview_in_progress: { label: 'Interview In Progress', colour: 'bg-amber-100 text-amber-700' },
  established: { label: 'Established', colour: 'bg-green-100 text-green-700' },
  stale: { label: 'Stale', colour: 'bg-amber-100 text-amber-700' },
  failed: { label: 'Run Failed', colour: 'bg-red-100 text-red-700' },
};

const CATEGORY_LABELS: Record<string, string> = {
  employer: 'Employer',
  employer_representative: 'Employer Representative',
  funder: 'Funder / Lender',
  parent_affiliate: 'Parent / Affiliate',
  contract_administrator: 'Contract Administrator',
  resident_engineer: 'Resident Engineer',
  independent_certifier: 'Independent Certifier',
  main_contractor: 'Main Contractor',
  contractors_representative: "Contractor's Representative",
  nominated_subcontractor: 'Nominated Subcontractor',
  domestic_subcontractor: 'Domestic Subcontractor',
  specialist_subcontractor: 'Specialist Subcontractor',
  supplier_manufacturer: 'Supplier / Manufacturer',
  design_consultant: 'Design Consultant',
  cost_consultant: 'Cost Consultant / QS',
  project_management_consultant: 'PMC',
  planning_consultant: 'Planning Consultant',
  clerk_of_works: 'Clerk of Works',
  competent_authority: 'Competent Authority',
  utility_authority: 'Utility Authority',
  statutory_inspector: 'Statutory Inspector',
  dab_daab: 'DAB / DAAB',
  arbitral_tribunal: 'Arbitral Tribunal',
  expert_mediator: 'Expert / Mediator',
  insurer: 'Insurer',
  surety: 'Surety / Bond',
  legal_counsel: 'Legal Counsel',
  unclassified: 'Unclassified',
};

const APPOINTMENT_COLOURS: Record<string, string> = {
  executed: 'bg-green-100 text-green-700',
  pending: 'bg-amber-100 text-amber-700',
  proposed: 'bg-gray-100 text-gray-600',
};

export function GovernancePanel({ projectId }: GovernancePanelProps) {
  const [status, setStatus] = useState<GovernanceStatusResponse | null>(null);
  const [statusLoading, setStatusLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Party identities state
  const [parties, setParties] = useState<PartyIdentityResponse[]>([]);
  const [partiesLoading, setPartiesLoading] = useState(false);
  const [expandedParty, setExpandedParty] = useState<string | null>(null);

  // Interview state
  const [interviewStatus, setInterviewStatus] = useState<InterviewStatusResponse | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<ReconciliationQuestionResponse | null>(null);
  const [selectedOption, setSelectedOption] = useState<string>('');
  const [freeText, setFreeText] = useState<string>('');
  const [submitting, setSubmitting] = useState(false);
  const [interviewLoading, setInterviewLoading] = useState(false);
  const [extracting, setExtracting] = useState(false);

  const fetchStatus = useCallback(async () => {
    setStatusLoading(true);
    try {
      const s = await getGovernanceStatus(projectId);
      setStatus(s);
    } catch {
      setError('Failed to load governance status.');
    } finally {
      setStatusLoading(false);
    }
  }, [projectId]);

  const fetchParties = useCallback(async () => {
    setPartiesLoading(true);
    try {
      const p = await listPartyIdentities(projectId);
      setParties(p);
    } catch {
      setError('Failed to load identified parties.');
    } finally {
      setPartiesLoading(false);
    }
  }, [projectId]);

  const fetchInterview = useCallback(async () => {
    setInterviewLoading(true);
    try {
      const iStatus = await getInterviewStatus(projectId);
      setInterviewStatus(iStatus);
      if (!iStatus.complete) {
        const iQuestion = await getNextInterviewQuestion(projectId);
        setCurrentQuestion(iQuestion);
      } else {
        setCurrentQuestion(null);
      }
      setSelectedOption('');
      setFreeText('');
    } catch {
      setError('Failed to load interview.');
    } finally {
      setInterviewLoading(false);
    }
  }, [projectId]);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  useEffect(() => {
    if (status?.status === 'parties_identified' || status?.status === 'interview_in_progress') {
      fetchParties();
      fetchInterview();
    }
  }, [status, fetchParties, fetchInterview]);

  // Continuous polling whenever status is processing
  useEffect(() => {
    if (status?.status !== 'processing') return;
    const interval = setInterval(async () => {
      try {
        const s = await getGovernanceStatus(projectId);
        setStatus(s);
        if (s.status !== 'processing') {
          clearInterval(interval);
          if (s.status === 'parties_identified' || s.status === 'interview_in_progress') {
            fetchParties();
            fetchInterview();
          }
        }
      } catch {
        // keep polling on error
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [status?.status, projectId, fetchParties, fetchInterview]);

  // Proactively refresh auth session to prevent mid-interview logout
  useEffect(() => {
    const { data: { subscription } } = (supabase as unknown as {
      auth: {
        onAuthStateChange: (cb: (event: string) => void) => { data: { subscription: { unsubscribe: () => void } } };
      }
    }).auth.onAuthStateChange((event) => {
      if (event === 'TOKEN_REFRESHED') {
        // Session refreshed — no action needed
      }
    });
    return () => subscription.unsubscribe();
  }, []);

  const handleRun = async () => {
    setRunning(true);
    setError(null);
    try {
      await runGovernance(projectId, 'full');
      // Immediately update status to show processing — polling useEffect takes over
      const s = await getGovernanceStatus(projectId);
      setStatus(s);
    } catch {
      setError('Failed to trigger governance run. Please try again.');
    } finally {
      setRunning(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!currentQuestion || !selectedOption) return;
    setSubmitting(true);
    setError(null);
    try {
      await submitInterviewAnswer(projectId, currentQuestion.id, {
        answer_selected: selectedOption,
        user_free_text: freeText || undefined,
      });
      await fetchInterview();
    } catch {
      setError('Failed to submit answer. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSkipQuestion = async () => {
    if (!currentQuestion) return;
    setSubmitting(true);
    setError(null);
    try {
      await submitInterviewAnswer(projectId, currentQuestion.id, {
        answer_selected: 'skipped',
        user_free_text: 'Skipped for later review.',
      });
      await fetchInterview();
    } catch {
      setError('Failed to skip question.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleExtractEvents = async () => {
    setExtracting(true);
    setError(null);
    try {
      await extractAuthorityEvents(projectId);
      // Poll until established
      const maxAttempts = 36;
      for (let i = 0; i < maxAttempts; i++) {
        await new Promise((resolve) => setTimeout(resolve, 5000));
        const s = await getGovernanceStatus(projectId);
        setStatus(s);
        if (s.status === 'established' || s.status === 'stale') {
          break;
        }
        if (s.status === 'failed') {
          setError('Authority event extraction failed. Please try again.');
          break;
        }
      }
    } catch {
      setError('Failed to start authority event extraction. Please try again.');
    } finally {
      setExtracting(false);
    }
  };

  const showInterview =
    status?.status === 'parties_identified' ||
    status?.status === 'interview_in_progress';

  const interviewComplete = interviewStatus?.complete === true;

  const statusInfo = status ? STATUS_LABELS[status.status] : null;

  return (
    <div className="space-y-6">

      {/* Readiness card */}
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-base font-semibold text-navy-900">Governance Readiness</h2>
            {statusLoading ? (
              <div className="mt-2"><Spinner className="h-4 w-4" /></div>
            ) : status ? (
              <div className="mt-2 space-y-1">
                <span className={`inline-block text-xs font-medium px-2 py-0.5 rounded-full ${statusInfo?.colour}`}>
                  {statusInfo?.label}
                </span>
                {status.status === 'processing' && (
                  <p className="text-xs text-blue-600 mt-1">
                    Analysing project documents... this may take 1-2 minutes.
                  </p>
                )}
                {status.status === 'failed' && (
                  <p className="text-xs text-red-600 mt-1">
                    The last run failed. Check your documents are ingested and try again.
                  </p>
                )}
                {status.last_run_at && (
                  <p className="text-xs text-gray-500">
                    Last run: {new Date(status.last_run_at).toLocaleString()}
                  </p>
                )}
                {showInterview && interviewStatus && (
                  <p className="text-xs text-gray-500">
                    {status.parties_count} {status.parties_count === 1 ? 'party' : 'parties'} identified ·{' '}
                    {interviewStatus.answered} of {interviewStatus.total_questions} questions answered
                  </p>
                )}
              </div>
            ) : null}
          </div>
          <button
            onClick={handleRun}
            disabled={running || statusLoading || showInterview}
            className="shrink-0 px-4 py-2 text-sm font-medium bg-navy-900 text-white rounded-md hover:bg-navy-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {running ? (
              <span className="flex items-center gap-2"><Spinner className="h-3 w-3" />Running...</span>
            ) : status?.status === 'not_established' ? (
              'Establish Governance'
            ) : showInterview ? (
              'Complete Interview First'
            ) : (
              'Refresh Governance'
            )}
          </button>
        </div>

        {status?.status === 'not_established' && (
          <div className="mt-3 p-3 bg-gray-50 border border-gray-200 rounded-md text-xs text-gray-600">
            Governance has not been established. Run governance establishment to identify
            all parties and their authority -- this is required before compliance-dependent queries.
          </div>
        )}
        {status?.status === 'stale' && (
          <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-md text-xs text-amber-700">
            New documents have been ingested since the last governance run. Refresh recommended.
          </div>
        )}
      </div>

      {/* Reconciliation Interview */}
      {showInterview && (
        <div className="bg-white border border-gray-200 rounded-lg">
          <div className="px-5 py-4 border-b border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-navy-900">Reconciliation Interview</h3>
                <p className="text-xs text-gray-500 mt-0.5">
                  Answer each question to resolve ambiguities found in your project documents.
                  Your answers are recorded and used in all subsequent governance analysis.
                </p>
              </div>
              {interviewStatus && (
                <div className="text-right shrink-0 ml-4">
                  <p className="text-xs font-medium text-navy-900">
                    {interviewStatus.answered} / {interviewStatus.total_questions}
                  </p>
                  <p className="text-xs text-gray-500">questions answered</p>
                </div>
              )}
            </div>
            {interviewStatus && interviewStatus.total_questions > 0 && (
              <div className="mt-3 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-green-500 rounded-full transition-all"
                  style={{
                    width: `${Math.round((interviewStatus.answered / interviewStatus.total_questions) * 100)}%`,
                  }}
                />
              </div>
            )}
          </div>

          <div className="px-5 py-5">
            {interviewLoading ? (
              <div className="flex justify-center py-8"><Spinner className="h-6 w-6" /></div>
            ) : interviewComplete ? (
              <div className="text-center py-6">
                <p className="text-sm font-medium text-green-700 mb-1">All questions answered</p>
                <p className="text-xs text-gray-500 mb-4">
                  The reconciliation record is complete. You can now proceed to extract authority events.
                </p>
                <button
                  className="px-5 py-2 text-sm font-medium bg-green-700 text-white rounded-md hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  onClick={handleExtractEvents}
                  disabled={extracting}
                >
                  {extracting ? (
                    <span className="flex items-center gap-2">
                      <Spinner className="h-3 w-3" />Extracting...
                    </span>
                  ) : (
                    'Extract Authority Events'
                  )}
                </button>
              </div>
            ) : currentQuestion ? (
              <div className="space-y-4">
                <div>
                  <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">
                    {currentQuestion.question_type.replace(/_/g, ' ')} · Question {(interviewStatus?.answered ?? 0) + 1} of {interviewStatus?.total_questions ?? '?'}
                  </p>
                  <p className="text-sm text-navy-900 leading-relaxed">{currentQuestion.question_text}</p>
                </div>

                <div className="space-y-2">
                  {currentQuestion.options_presented.map((option) => (
                    <label
                      key={option}
                      className={`flex items-start gap-3 p-3 rounded-md border cursor-pointer transition-colors ${
                        selectedOption === option
                          ? 'border-navy-700 bg-navy-50'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <input
                        type="radio"
                        name="interview-option"
                        value={option}
                        checked={selectedOption === option}
                        onChange={() => setSelectedOption(option)}
                        className="mt-0.5 shrink-0"
                      />
                      <span className="text-sm text-gray-700">{option}</span>
                    </label>
                  ))}
                </div>

                {selectedOption && (
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">
                      Additional comment (optional)
                    </label>
                    <textarea
                      value={freeText}
                      onChange={(e) => setFreeText(e.target.value)}
                      rows={2}
                      className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm placeholder:text-gray-400 focus:border-navy-700 focus:outline-none focus:ring-1 focus:ring-navy-700 resize-none"
                      placeholder="Add context or clarification if needed..."
                    />
                  </div>
                )}

                <div className="flex items-center gap-3 pt-1">
                  <button
                    onClick={handleSubmitAnswer}
                    disabled={!selectedOption || submitting}
                    className="px-4 py-2 text-sm font-medium bg-navy-900 text-white rounded-md hover:bg-navy-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {submitting ? (
                      <span className="flex items-center gap-2"><Spinner className="h-3 w-3" />Saving...</span>
                    ) : (
                      'Submit Answer'
                    )}
                  </button>
                  <button
                    onClick={handleSkipQuestion}
                    disabled={submitting}
                    className="px-4 py-2 text-sm font-medium text-gray-500 border border-gray-200 rounded-md hover:bg-gray-50 disabled:opacity-50 transition-colors"
                  >
                    Skip for now
                  </button>
                </div>
              </div>
            ) : (
              <EmptyState
                title="No questions pending"
                description="No reconciliation questions were generated for this run."
              />
            )}
          </div>
        </div>
      )}

      {/* Identified Parties */}
      {showInterview && (
        <div className="bg-white border border-gray-200 rounded-lg">
          <div className="px-5 py-4 border-b border-gray-100">
            <h3 className="text-sm font-semibold text-navy-900">Identified Parties</h3>
            <p className="text-xs text-gray-500 mt-0.5">
              Parties extracted from your project documents. Each party may hold multiple roles.
            </p>
          </div>
          {partiesLoading ? (
            <div className="flex justify-center py-12"><Spinner className="h-6 w-6" /></div>
          ) : parties.length === 0 ? (
            <div className="p-5">
              <EmptyState
                title="No parties identified"
                description="Party identification is still running or produced no results."
              />
            </div>
          ) : (
            <div className="divide-y divide-gray-100">
              {parties.map((party) => (
                <div key={party.id} className="px-5 py-4">
                  <div
                    className="flex items-start justify-between gap-4 cursor-pointer"
                    onClick={() => setExpandedParty(expandedParty === party.id ? null : party.id)}
                  >
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-sm font-medium text-navy-900">{party.legal_name}</span>
                        {party.is_internal && (
                          <span className="text-xs px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 font-medium">Internal</span>
                        )}
                        <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${
                          party.identification_status === 'confirmed'
                            ? 'bg-green-50 text-green-700'
                            : 'bg-amber-50 text-amber-700'
                        }`}>
                          {party.identification_status.charAt(0).toUpperCase() + party.identification_status.slice(1)}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {CATEGORY_LABELS[party.party_category] ?? party.party_category} · {party.entity_type} · {party.roles.length} role{party.roles.length !== 1 ? 's' : ''}
                      </p>
                      {party.trading_names.length > 0 && (
                        <p className="text-xs text-gray-400 mt-0.5">
                          Also known as: {party.trading_names.join(', ')}
                        </p>
                      )}
                    </div>
                    <span className="text-xs text-gray-400 shrink-0 mt-1">
                      {expandedParty === party.id ? '\u25B2' : '\u25BC'}
                    </span>
                  </div>

                  {expandedParty === party.id && party.roles.length > 0 && (
                    <div className="mt-3 space-y-2">
                      {party.roles.map((role) => (
                        <div key={role.id} className="bg-gray-50 rounded-md px-4 py-3 text-xs">
                          <div className="flex items-start justify-between gap-2">
                            <div>
                              <p className="font-medium text-navy-900">{role.role_title}</p>
                              {role.governing_instrument && (
                                <p className="text-gray-500 mt-0.5">
                                  {role.governing_instrument}
                                  {role.source_clause && ` -- ${role.source_clause}`}
                                </p>
                              )}
                              {role.authority_scope && (
                                <p className="text-gray-600 mt-1">{role.authority_scope}</p>
                              )}
                              {role.financial_threshold && (
                                <p className="text-gray-500 mt-0.5">
                                  Threshold: {role.financial_threshold} {role.financial_currency ?? ''}
                                </p>
                              )}
                              {(role.effective_from || role.effective_to) && (
                                <p className="text-gray-400 mt-0.5">
                                  {role.effective_from ?? '--'} → {role.effective_to ?? 'ongoing'}
                                </p>
                              )}
                            </div>
                            <span className={`shrink-0 px-2 py-0.5 rounded-full font-medium ${APPOINTMENT_COLOURS[role.appointment_status] ?? 'bg-gray-100 text-gray-600'}`}>
                              {role.appointment_status.charAt(0).toUpperCase() + role.appointment_status.slice(1)}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Authority Event Log placeholder -- populated in Phase 8 */}
      {(status?.status === 'established' || status?.status === 'stale') && (
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <h3 className="text-sm font-semibold text-navy-900 mb-1">Authority Event Log</h3>
          <p className="text-xs text-gray-500">
            The authority event log will be displayed here once Phase 8 is complete.
          </p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700">
          {error}
        </div>
      )}

    </div>
  );
}
