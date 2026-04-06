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
  listAuthorityEvents,
} from '../../api/governance';
import type {
  GovernanceStatusResponse,
  PartyIdentityResponse,
  ReconciliationQuestionResponse,
  InterviewStatusResponse,
  AuthorityEventResponse,
} from '../../api/types';

interface GovernancePanelProps {
  projectId: string;
}

const STATUS_LABELS: Record<string, { label: string; colour: string }> = {
  not_established: { label: 'Not Established', colour: 'bg-gray-100 text-gray-600' },
  processing: { label: 'Processing\u2026', colour: 'bg-blue-100 text-blue-700' },
  parties_identified: { label: 'Parties Identified', colour: 'bg-amber-100 text-amber-700' },
  established: { label: 'Established', colour: 'bg-green-100 text-green-700' },
  stale: { label: 'Stale', colour: 'bg-amber-100 text-amber-700' },
  failed: { label: 'Run Failed', colour: 'bg-red-100 text-red-700' },
};

const APPOINTMENT_LABELS: Record<string, { label: string; colour: string }> = {
  executed: { label: 'Executed', colour: 'bg-green-100 text-green-700' },
  pending: { label: 'Pending', colour: 'bg-amber-100 text-amber-700' },
  proposed: { label: 'Proposed', colour: 'bg-gray-100 text-gray-500' },
};

const CATEGORY_LABELS: Record<string, string> = {
  employer: 'Employer',
  employer_representative: 'Employer Representative',
  funder: 'Funder',
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
  cost_consultant: 'Cost Consultant',
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
  surety: 'Surety',
  legal_counsel: 'Legal Counsel',
  unclassified: 'Unclassified',
};

export function GovernancePanel({ projectId }: GovernancePanelProps) {
  const [status, setStatus] = useState<GovernanceStatusResponse | null>(null);
  const [statusLoading, setStatusLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Party identities (Phase 1 output)
  const [parties, setParties] = useState<PartyIdentityResponse[]>([]);
  const [partiesLoading, setPartiesLoading] = useState(false);
  const [expandedPartyId, setExpandedPartyId] = useState<string | null>(null);

  // Reconciliation interview
  const [interviewStatus, setInterviewStatus] =
    useState<InterviewStatusResponse | null>(null);
  const [currentQuestion, setCurrentQuestion] =
    useState<ReconciliationQuestionResponse | null>(null);
  const [questionLoading, setQuestionLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [freeText, setFreeText] = useState<string>('');

  // Authority events (Phase 2 output)
  const [events, setEvents] = useState<AuthorityEventResponse[]>([]);
  const [eventsLoading, setEventsLoading] = useState(false);
  const [extracting, setExtracting] = useState(false);

  // -----------------------------------------------------------------------
  // Data fetchers
  // -----------------------------------------------------------------------

  const fetchStatus = useCallback(async () => {
    setStatusLoading(true);
    try {
      const s = await getGovernanceStatus(projectId);
      setStatus(s);
      return s;
    } catch {
      setError('Failed to load governance status.');
      return null;
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

  const fetchInterviewStatus = useCallback(async () => {
    try {
      const s = await getInterviewStatus(projectId);
      setInterviewStatus(s);
      return s;
    } catch {
      // No interview run yet -- not an error
      return null;
    }
  }, [projectId]);

  const fetchNextQuestion = useCallback(async () => {
    setQuestionLoading(true);
    try {
      const q = await getNextInterviewQuestion(projectId);
      setCurrentQuestion(q);
      setSelectedAnswer('');
      setFreeText('');
    } catch {
      // 404 = all questions answered -- not an error
      setCurrentQuestion(null);
    } finally {
      setQuestionLoading(false);
    }
  }, [projectId]);

  const fetchEvents = useCallback(async () => {
    setEventsLoading(true);
    try {
      const e = await listAuthorityEvents(projectId);
      setEvents(e);
    } catch {
      setError('Failed to load authority events.');
    } finally {
      setEventsLoading(false);
    }
  }, [projectId]);

  // -----------------------------------------------------------------------
  // Initial load and status-driven side effects
  // -----------------------------------------------------------------------

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  useEffect(() => {
    if (!status) return;
    if (status.status === 'parties_identified') {
      fetchParties();
      fetchInterviewStatus().then((s) => {
        if (s && !s.interview_complete) fetchNextQuestion();
      });
    }
    if (
      status.status === 'established' ||
      status.status === 'stale'
    ) {
      fetchEvents();
    }
  }, [status, fetchParties, fetchInterviewStatus, fetchNextQuestion, fetchEvents]);

  // -----------------------------------------------------------------------
  // Polling
  // -----------------------------------------------------------------------

  const pollUntilResolved = useCallback(async () => {
    const MAX = 36; // 3 minutes at 5s intervals
    for (let i = 0; i < MAX; i++) {
      await new Promise((r) => setTimeout(r, 5000));
      try {
        const s = await getGovernanceStatus(projectId);
        setStatus(s);
        if (s.status === 'parties_identified') {
          await fetchParties();
          const iv = await fetchInterviewStatus();
          if (iv && !iv.interview_complete) await fetchNextQuestion();
          return;
        }
        if (s.status === 'established' || s.status === 'stale') {
          await fetchEvents();
          return;
        }
        if (s.status === 'failed' || s.status === 'not_established') return;
      } catch {
        return;
      }
    }
  }, [projectId, fetchParties, fetchInterviewStatus, fetchNextQuestion, fetchEvents]);

  // -----------------------------------------------------------------------
  // Actions
  // -----------------------------------------------------------------------

  const handleRun = async () => {
    setRunning(true);
    setError(null);
    try {
      const runType =
        status?.status === 'not_established' ? 'full' : 'incremental';
      await runGovernance(projectId, runType);
      await pollUntilResolved();
    } catch {
      setError('Failed to trigger governance run. Please try again.');
    } finally {
      setRunning(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!currentQuestion || !selectedAnswer) return;
    setSubmitting(true);
    setError(null);
    try {
      await submitInterviewAnswer(
        projectId,
        currentQuestion.id,
        selectedAnswer,
        freeText || undefined,
      );
      // Refresh interview status and load next question
      const iv = await fetchInterviewStatus();
      setInterviewStatus(iv);
      if (iv && iv.interview_complete) {
        setCurrentQuestion(null);
      } else {
        await fetchNextQuestion();
      }
    } catch {
      setError('Failed to record answer. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleExtractEvents = async () => {
    setExtracting(true);
    setError(null);
    try {
      await extractAuthorityEvents(projectId);
      await pollUntilResolved();
    } catch {
      setError('Failed to trigger event extraction. Please try again.');
    } finally {
      setExtracting(false);
    }
  };

  // -----------------------------------------------------------------------
  // Render helpers
  // -----------------------------------------------------------------------

  const internalParties = parties.filter((p) => p.is_internal);
  const externalParties = parties.filter((p) => !p.is_internal);

  const renderPartyTable = (list: PartyIdentityResponse[]) => {
    if (list.length === 0)
      return (
        <p className="text-xs text-gray-400 px-4 py-3 italic">
          None identified.
        </p>
      );
    return (
      <div className="divide-y divide-gray-100">
        {list.map((party) => {
          const isExpanded = expandedPartyId === party.id;
          return (
            <div key={party.id}>
              {/* Party header row */}
              <button
                onClick={() =>
                  setExpandedPartyId(isExpanded ? null : party.id)
                }
                className="w-full flex items-start justify-between gap-3 px-4 py-3 text-left hover:bg-gray-50 transition-colors"
              >
                <div className="min-w-0">
                  <p className="text-sm font-medium text-navy-900 truncate">
                    {party.legal_name}
                  </p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-xs text-gray-500 capitalize">
                      {party.entity_type}
                    </span>
                    <span className="text-gray-300">&middot;</span>
                    <span className="text-xs text-gray-500">
                      {CATEGORY_LABELS[party.party_category] ??
                        party.party_category}
                    </span>
                    {party.trading_names.length > 0 && (
                      <>
                        <span className="text-gray-300">&middot;</span>
                        <span className="text-xs text-gray-400">
                          also: {party.trading_names.join(', ')}
                        </span>
                      </>
                    )}
                  </div>
                </div>
                <span className="text-xs text-gray-400 shrink-0 mt-0.5">
                  {party.roles.length} role
                  {party.roles.length !== 1 ? 's' : ''}{' '}
                  {isExpanded ? '\u25B2' : '\u25BC'}
                </span>
              </button>

              {/* Expanded roles */}
              {isExpanded && party.roles.length > 0 && (
                <div className="bg-gray-50 border-t border-gray-100 px-4 py-3 space-y-2">
                  {party.roles.map((role) => {
                    const appt =
                      APPOINTMENT_LABELS[role.appointment_status] ??
                      APPOINTMENT_LABELS['proposed'];
                    return (
                      <div
                        key={role.id}
                        className="bg-white border border-gray-200 rounded-md p-3 text-xs"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <p className="font-medium text-navy-900">
                            {role.role_title}
                          </p>
                          <span
                            className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium shrink-0 ${appt.colour}`}
                          >
                            {appt.label}
                          </span>
                        </div>
                        {role.governing_instrument && (
                          <p className="text-gray-500 mt-1">
                            Instrument:{' '}
                            <span className="text-gray-700">
                              {role.governing_instrument}
                            </span>
                          </p>
                        )}
                        {role.authority_scope && (
                          <p className="text-gray-500 mt-1">
                            Scope:{' '}
                            <span className="text-gray-700">
                              {role.authority_scope}
                            </span>
                          </p>
                        )}
                        {role.financial_threshold && (
                          <p className="text-gray-500 mt-1">
                            Threshold:{' '}
                            <span className="text-gray-700">
                              {role.financial_currency
                                ? `${role.financial_currency} `
                                : ''}
                              {role.financial_threshold}
                            </span>
                          </p>
                        )}
                        {(role.effective_from || role.effective_to) && (
                          <p className="text-gray-500 mt-1">
                            Period:{' '}
                            <span className="text-gray-700">
                              {role.effective_from ?? '\u2014'} \u2192{' '}
                              {role.effective_to ?? 'ongoing'}
                            </span>
                          </p>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  const statusInfo = status ? STATUS_LABELS[status.status] : null;

  // -----------------------------------------------------------------------
  // Render
  // -----------------------------------------------------------------------

  return (
    <div className="space-y-6">
      {/* ---------------------------------------------------------------- */}
      {/* Readiness card */}
      {/* ---------------------------------------------------------------- */}
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-base font-semibold text-navy-900">
              Governance Readiness
            </h2>
            {statusLoading ? (
              <div className="mt-2">
                <Spinner className="h-4 w-4" />
              </div>
            ) : status ? (
              <div className="mt-2 space-y-1">
                <span
                  className={`inline-block text-xs font-medium px-2 py-0.5 rounded-full ${statusInfo?.colour}`}
                >
                  {statusInfo?.label}
                </span>
                {status.status === 'processing' && (
                  <p className="text-xs text-blue-600 mt-1">
                    Analysing project documents... this may take 1-2 minutes.
                  </p>
                )}
                {status.status === 'failed' && (
                  <p className="text-xs text-red-600 mt-1">
                    The last run failed. Check documents are ingested and
                    try again.
                  </p>
                )}
                {status.last_run_at && (
                  <p className="text-xs text-gray-500">
                    Last run:{' '}
                    {new Date(status.last_run_at).toLocaleString()}
                  </p>
                )}
                {status.status === 'not_established' && (
                  <p className="text-xs text-gray-500 mt-1">
                    Governance has not been established for this project.
                    Run party identification to begin.
                  </p>
                )}
                {status.status === 'stale' && (
                  <p className="text-xs text-amber-600 mt-1">
                    New documents have been ingested since the last run.
                    Refresh recommended.
                  </p>
                )}
              </div>
            ) : null}
          </div>

          <button
            onClick={handleRun}
            disabled={running || statusLoading}
            className="shrink-0 px-4 py-2 text-sm font-medium bg-navy-900 text-white rounded-md hover:bg-navy-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {running ? (
              <span className="flex items-center gap-2">
                <Spinner className="h-3 w-3" />
                Running...
              </span>
            ) : status?.status === 'not_established' ? (
              'Establish Governance'
            ) : (
              'Refresh Governance'
            )}
          </button>
        </div>
      </div>

      {/* ---------------------------------------------------------------- */}
      {/* Error banner */}
      {/* ---------------------------------------------------------------- */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* ---------------------------------------------------------------- */}
      {/* Parties identified -- shown when status = parties_identified */}
      {/* ---------------------------------------------------------------- */}
      {status?.status === 'parties_identified' && (
        <>
          {/* Party identity register */}
          <div className="bg-white border border-gray-200 rounded-lg">
            <div className="px-5 py-4 border-b border-gray-100">
              <h3 className="text-sm font-semibold text-navy-900">
                Identified Parties
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">
                Parties and roles extracted from project documents. Click a
                party to expand their role records.
              </p>
            </div>

            {partiesLoading ? (
              <div className="flex justify-center py-10">
                <Spinner className="h-5 w-5" />
              </div>
            ) : parties.length === 0 ? (
              <div className="p-5">
                <EmptyState
                  title="No parties identified"
                  description="Party identification is still running or produced no results."
                />
              </div>
            ) : (
              <>
                {/* Internal tab */}
                {internalParties.length > 0 && (
                  <div>
                    <div className="px-4 py-2 bg-gray-50 border-b border-gray-100">
                      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        Internal -- Employer's Organisation (
                        {internalParties.length})
                      </p>
                    </div>
                    {renderPartyTable(internalParties)}
                  </div>
                )}

                {/* External tab */}
                {externalParties.length > 0 && (
                  <div>
                    <div className="px-4 py-2 bg-gray-50 border-b border-gray-100">
                      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        External ({externalParties.length})
                      </p>
                    </div>
                    {renderPartyTable(externalParties)}
                  </div>
                )}
              </>
            )}
          </div>

          {/* Reconciliation interview */}
          <div className="bg-white border border-gray-200 rounded-lg">
            <div className="px-5 py-4 border-b border-gray-100">
              <h3 className="text-sm font-semibold text-navy-900">
                Reconciliation Interview
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">
                Answer each question to resolve ambiguities before
                authority event extraction begins.
              </p>
              {/* Progress bar */}
              {interviewStatus && interviewStatus.total_questions > 0 && (
                <div className="mt-3">
                  <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                    <span>
                      {interviewStatus.answered_questions} of{' '}
                      {interviewStatus.total_questions} answered
                    </span>
                    <span>
                      {Math.round(
                        (interviewStatus.answered_questions /
                          interviewStatus.total_questions) *
                          100,
                      )}
                      %
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div
                      className="bg-navy-900 h-1.5 rounded-full transition-all"
                      style={{
                        width: `${Math.round(
                          (interviewStatus.answered_questions /
                            interviewStatus.total_questions) *
                            100,
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              )}
            </div>

            {questionLoading ? (
              <div className="flex justify-center py-10">
                <Spinner className="h-5 w-5" />
              </div>
            ) : interviewStatus?.interview_complete ||
              (!currentQuestion && !questionLoading) ? (
              <div className="px-5 py-5 space-y-4">
                <div className="flex items-center gap-2 text-sm text-green-700 font-medium">
                  <span>{'\u2713'}</span>
                  <span>
                    {interviewStatus?.total_questions === 0
                      ? 'No reconciliation questions were generated for this run.'
                      : 'All questions answered. Ready to extract authority events.'}
                  </span>
                </div>
                <button
                  onClick={handleExtractEvents}
                  disabled={extracting}
                  className="px-4 py-2 text-sm font-medium bg-green-700 text-white rounded-md hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {extracting ? (
                    <span className="flex items-center gap-2">
                      <Spinner className="h-3 w-3" />
                      Extracting...
                    </span>
                  ) : (
                    'Extract Authority Events'
                  )}
                </button>
              </div>
            ) : currentQuestion ? (
              <div className="px-5 py-5 space-y-4">
                <p className="text-sm text-navy-900">
                  {currentQuestion.question_text}
                </p>

                <div className="space-y-2">
                  {currentQuestion.options_presented.map((opt) => (
                    <label
                      key={opt}
                      className={`flex items-start gap-3 p-3 border rounded-md cursor-pointer transition-colors ${
                        selectedAnswer === opt
                          ? 'border-navy-900 bg-navy-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name="interview-answer"
                        value={opt}
                        checked={selectedAnswer === opt}
                        onChange={() => setSelectedAnswer(opt)}
                        className="mt-0.5 shrink-0"
                      />
                      <span className="text-sm text-gray-700">{opt}</span>
                    </label>
                  ))}
                </div>

                <div>
                  <label className="block text-xs text-gray-500 mb-1">
                    Additional comments (optional)
                  </label>
                  <textarea
                    value={freeText}
                    onChange={(e) => setFreeText(e.target.value)}
                    rows={2}
                    className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm text-gray-700 focus:outline-none focus:border-navy-900 resize-none"
                    placeholder="Any additional context..."
                  />
                </div>

                <button
                  onClick={handleSubmitAnswer}
                  disabled={!selectedAnswer || submitting}
                  className="px-4 py-2 text-sm font-medium bg-navy-900 text-white rounded-md hover:bg-navy-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {submitting ? (
                    <span className="flex items-center gap-2">
                      <Spinner className="h-3 w-3" />
                      Saving...
                    </span>
                  ) : (
                    'Submit Answer'
                  )}
                </button>
              </div>
            ) : null}
          </div>
        </>
      )}

      {/* ---------------------------------------------------------------- */}
      {/* Authority Event Log -- shown when established / stale */}
      {/* ---------------------------------------------------------------- */}
      {(status?.status === 'established' || status?.status === 'stale') && (
        <div className="bg-white border border-gray-200 rounded-lg">
          <div className="px-5 py-4 border-b border-gray-100">
            <h3 className="text-sm font-semibold text-navy-900">
              Authority Event Log
            </h3>
            <p className="text-xs text-gray-500 mt-0.5">
              Chronological record of all authority events extracted from
              project documents.
            </p>
          </div>

          {eventsLoading ? (
            <div className="flex justify-center py-12">
              <Spinner className="h-6 w-6" />
            </div>
          ) : events.length === 0 ? (
            <div className="p-5">
              <EmptyState
                title="No authority events"
                description="No authority events have been extracted yet."
              />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-gray-50 text-left">
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">
                      Event
                    </th>
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">
                      Authority After
                    </th>
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">
                      Threshold
                    </th>
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">
                      Missing Action
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {events.map((event) => {
                    const appt =
                      APPOINTMENT_LABELS[event.appointment_status] ??
                      APPOINTMENT_LABELS['proposed'];
                    return (
                      <tr
                        key={event.id}
                        className="hover:bg-gray-50 transition-colors"
                      >
                        <td className="px-4 py-3 capitalize font-medium text-navy-900">
                          {event.event_type}
                        </td>
                        <td className="px-4 py-3 text-gray-600">
                          {event.event_date ?? '\u2014'}
                          {!event.event_date_certain && (
                            <span className="text-amber-500 ml-1"
                                  title="Date uncertain">~</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-gray-700 max-w-[200px]"
                            style={{ whiteSpace: 'normal', wordBreak: 'break-word' }}>
                          {event.authority_after ?? '\u2014'}
                        </td>
                        <td className="px-4 py-3 text-gray-600">
                          {event.financial_threshold_after ?? '\u2014'}
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${appt.colour}`}
                          >
                            {appt.label}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-amber-700 max-w-[160px]"
                            style={{ whiteSpace: 'normal', wordBreak: 'break-word' }}>
                          {event.missing_action ?? '\u2014'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
