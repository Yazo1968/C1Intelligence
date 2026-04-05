import { useCallback, useEffect, useState } from 'react';
import { Spinner } from '../ui/Spinner';
import { EmptyState } from '../ui/EmptyState';
import {
  runGovernance,
  getGovernanceStatus,
  listGovernanceEvents,
  updateGovernanceEvent,
  listGovernanceParties,
  updateGovernanceParty,
  confirmParties,
} from '../../api/governance';
import type { GovernanceStatusResponse, GovernanceEventResponse, GovernancePartyResponse } from '../../api/types';

interface GovernancePanelProps {
  projectId: string;
}

const STATUS_LABELS: Record<string, { label: string; colour: string }> = {
  not_established: { label: 'Not Established', colour: 'bg-gray-100 text-gray-600' },
  processing: { label: 'Processing…', colour: 'bg-blue-100 text-blue-700' },
  parties_identified: { label: 'Parties Identified', colour: 'bg-amber-100 text-amber-700' },
  established: { label: 'Established', colour: 'bg-green-100 text-green-700' },
  stale: { label: 'Stale', colour: 'bg-amber-100 text-amber-700' },
  failed: { label: 'Run Failed', colour: 'bg-red-100 text-red-700' },
};

const EXTRACTION_LABELS: Record<string, { label: string; colour: string }> = {
  confirmed: { label: 'Confirmed', colour: 'bg-green-100 text-green-700' },
  flagged: { label: 'Flagged', colour: 'bg-red-100 text-red-700' },
  inferred: { label: 'Inferred', colour: 'bg-amber-100 text-amber-700' },
};

const DIMENSION_LABELS: Record<string, string> = {
  layer_1: 'Contractual',
  layer_2a: 'Internal DOA',
  layer_2b: 'Statutory',
};

export function GovernancePanel({ projectId }: GovernancePanelProps) {
  const [status, setStatus] = useState<GovernanceStatusResponse | null>(null);
  const [events, setEvents] = useState<GovernanceEventResponse[]>([]);
  const [statusLoading, setStatusLoading] = useState(true);
  const [eventsLoading, setEventsLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [parties, setParties] = useState<GovernancePartyResponse[]>([]);
  const [partiesLoading, setPartiesLoading] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [updatingPartyId, setUpdatingPartyId] = useState<string | null>(null);

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

  const fetchEvents = useCallback(async () => {
    setEventsLoading(true);
    try {
      const e = await listGovernanceEvents(projectId);
      setEvents(e);
    } catch {
      setError('Failed to load governance events.');
    } finally {
      setEventsLoading(false);
    }
  }, [projectId]);

  const fetchParties = useCallback(async () => {
    setPartiesLoading(true);
    try {
      const p = await listGovernanceParties(projectId);
      setParties(p);
    } catch {
      setError('Failed to load governance parties.');
    } finally {
      setPartiesLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  useEffect(() => {
    if (status && status.status !== 'not_established') {
      fetchEvents();
    }
  }, [status, fetchEvents]);

  useEffect(() => {
    if (status && status.status === 'parties_identified') {
      fetchParties();
    }
  }, [status, fetchParties]);

  const handleRun = async () => {
    setRunning(true);
    setError(null);
    const runType = status?.status === 'not_established' ? 'full' : 'incremental';
    try {
      await runGovernance(projectId, runType);
      await pollUntilResolved();
    } catch {
      setError('Failed to trigger governance run. Please try again.');
    } finally {
      setRunning(false);
    }
  };

  const handleConfirmParties = async () => {
    setConfirming(true);
    setError(null);
    try {
      await confirmParties(projectId);
      await fetchStatus();
      await fetchEvents();
    } catch {
      setError('Failed to trigger governance establishment. Please try again.');
    } finally {
      setConfirming(false);
    }
  };

  const pollUntilResolved = useCallback(async () => {
    const maxAttempts = 36; // 3 minutes at 5s intervals
    for (let i = 0; i < maxAttempts; i++) {
      await new Promise((resolve) => setTimeout(resolve, 5000));
      try {
        const s = await getGovernanceStatus(projectId);
        setStatus(s);
        if (s.status === 'parties_identified') {
          await fetchParties();
          return;
        }
        if (s.status === 'established' || s.status === 'stale') {
          await fetchEvents();
          return;
        }
        if (s.status === 'failed' || s.status === 'not_established') {
          return;
        }
        // status === 'processing' — keep polling
      } catch {
        return;
      }
    }
  }, [projectId, fetchParties, fetchEvents]);

  const handleUpdatePartyStatus = async (
    partyId: string,
    newStatus: 'confirmed' | 'flagged' | 'inferred',
  ) => {
    setUpdatingPartyId(partyId);
    try {
      const updated = await updateGovernanceParty(projectId, partyId, {
        confirmation_status: newStatus,
      });
      setParties((prev) =>
        prev.map((p) => (p.id === updated.id ? updated : p)),
      );
    } catch {
      setError('Failed to update party status.');
    } finally {
      setUpdatingPartyId(null);
    }
  };

  const handleUpdateStatus = async (
    eventId: string,
    newStatus: 'confirmed' | 'flagged' | 'inferred',
  ) => {
    setUpdatingId(eventId);
    try {
      const updated = await updateGovernanceEvent(projectId, eventId, {
        extraction_status: newStatus,
      });
      setEvents((prev) =>
        prev.map((e) => (e.id === updated.id ? updated : e)),
      );
    } catch {
      setError('Failed to update event status.');
    } finally {
      setUpdatingId(null);
    }
  };

  const pendingCount = events.filter((e) => e.extraction_status === 'inferred').length;

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
                <span
                  className={`inline-block text-xs font-medium px-2 py-0.5 rounded-full ${statusInfo?.colour}`}
                >
                  {statusInfo?.label}
                </span>
                {status?.status === 'processing' && (
                  <p className="text-xs text-blue-600 mt-1">
                    Analysing project documents… this may take 1–2 minutes.
                  </p>
                )}
                {status?.status === 'failed' && (
                  <p className="text-xs text-red-600 mt-1">
                    The last run failed. Check your documents are ingested and try again.
                  </p>
                )}
                {status.last_run_at && (
                  <p className="text-xs text-gray-500">
                    Last run: {new Date(status.last_run_at).toLocaleString()}
                  </p>
                )}
                {status.status !== 'not_established' && (
                  <p className="text-xs text-gray-500">
                    {status.events_confirmed} confirmed · {status.events_flagged} flagged · {status.events_inferred} inferred
                  </p>
                )}
                {pendingCount > 0 && (
                  <p className="text-xs text-amber-600 font-medium">
                    {pendingCount} event{pendingCount !== 1 ? 's' : ''} pending review
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
              <span className="flex items-center gap-2"><Spinner className="h-3 w-3" />Running...</span>
            ) : status?.status === 'not_established' ? (
              'Establish Governance'
            ) : status?.status === 'parties_identified' ? (
              'Re-run Party Identification'
            ) : (
              'Refresh Governance'
            )}
          </button>
        </div>

        {status?.status === 'stale' && (
          <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-md text-xs text-amber-700">
            New documents have been ingested since the last governance run. Refresh recommended before running compliance-dependent queries.
          </div>
        )}

        {status?.status === 'not_established' && (
          <div className="mt-3 p-3 bg-gray-50 border border-gray-200 rounded-md text-xs text-gray-600">
            Governance has not been established. Run governance establishment before submitting compliance-dependent queries. This will scan all ingested documents to extract authority events.
          </div>
        )}
      </div>

      {status?.status === 'parties_identified' && (
        <div className="bg-white border border-gray-200 rounded-lg">
          <div className="px-5 py-4 border-b border-gray-100 flex items-start justify-between gap-4">
            <div>
              <h3 className="text-sm font-semibold text-navy-900">Identified Parties</h3>
              <p className="text-xs text-gray-500 mt-0.5">
                Review each identified party extracted from your project documents.
                Confirm parties that are correctly identified. Flag any entry that
                is incorrect or uncertain — flagged parties are excluded from the
                governance analysis.
              </p>
            </div>
            <button
              onClick={handleConfirmParties}
              disabled={
                confirming ||
                partiesLoading ||
                parties.filter((p) => p.confirmation_status === 'confirmed').length === 0
              }
              className="shrink-0 px-4 py-2 text-sm font-medium bg-green-700 text-white rounded-md hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {confirming ? (
                <span className="flex items-center gap-2">
                  <Spinner className="h-3 w-3" />Running...
                </span>
              ) : (
                'Confirm Parties & Establish Governance'
              )}
            </button>
          </div>

          {partiesLoading ? (
            <div className="flex justify-center py-12">
              <Spinner className="h-6 w-6" />
            </div>
          ) : parties.length === 0 ? (
            <div className="p-5">
              <EmptyState
                title="No parties identified"
                description="Party identification is still running or produced no results."
              />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-gray-50 text-left">
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">Type</th>
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">Party Name</th>
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">Role</th>
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">Has Downward Authority</th>
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {parties.map((party) => {
                    const isUpdating = updatingPartyId === party.id;
                    const statusColour =
                      party.confirmation_status === 'confirmed'
                        ? 'bg-green-100 text-green-700'
                        : party.confirmation_status === 'flagged'
                        ? 'bg-red-100 text-red-700'
                        : 'bg-amber-100 text-amber-700';
                    return (
                      <tr key={party.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3 capitalize text-gray-600">{party.entity_type}</td>
                        <td className="px-4 py-3 font-medium text-navy-900 max-w-[200px] truncate" title={party.canonical_name}>
                          {party.canonical_name}
                        </td>
                        <td
                          className="px-4 py-3 text-gray-600 max-w-[220px]"
                          style={{ whiteSpace: 'normal', wordBreak: 'break-word' }}
                          title={party.contractual_role ?? ''}
                        >
                          {party.contractual_role ?? '—'}
                        </td>
                        <td className="px-4 py-3 text-gray-500">
                          {party.terminus_node ? 'No' : 'Yes'}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${statusColour}`}>
                            {party.confirmation_status.charAt(0).toUpperCase() + party.confirmation_status.slice(1)}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          {isUpdating ? (
                            <Spinner className="h-3 w-3" />
                          ) : (
                            <div className="flex items-center gap-2">
                              {party.confirmation_status !== 'confirmed' && (
                                <button
                                  onClick={() => handleUpdatePartyStatus(party.id, 'confirmed')}
                                  className="text-green-700 hover:underline font-medium"
                                >
                                  Confirm
                                </button>
                              )}
                              {party.confirmation_status !== 'flagged' && (
                                <button
                                  onClick={() => handleUpdatePartyStatus(party.id, 'flagged')}
                                  className="text-red-600 hover:underline font-medium"
                                >
                                  Flag
                                </button>
                              )}
                            </div>
                          )}
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

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Event log */}
      {status && status.status !== 'not_established' && (
        <div className="bg-white border border-gray-200 rounded-lg">
          <div className="px-5 py-4 border-b border-gray-100">
            <h3 className="text-sm font-semibold text-navy-900">Governance Event Log</h3>
            <p className="text-xs text-gray-500 mt-0.5">
              Review each event and confirm, or flag for further investigation.
            </p>
          </div>

          {eventsLoading ? (
            <div className="flex justify-center py-12"><Spinner className="h-6 w-6" /></div>
          ) : events.length === 0 ? (
            <div className="p-5">
              <EmptyState
                title="No events extracted"
                description="Run governance establishment to extract authority events from your project documents."
              />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-gray-50 text-left">
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">Type</th>
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">Date</th>
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">Role</th>
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">Dimension</th>
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">Source</th>
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-4 py-3 font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {events.map((event) => {
                    const extractionInfo = EXTRACTION_LABELS[event.extraction_status];
                    const isUpdating = updatingId === event.id;
                    return (
                      <tr key={event.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3 capitalize font-medium text-navy-900">
                          {event.event_type}
                        </td>
                        <td className="px-4 py-3 text-gray-600">
                          {event.effective_date}
                          {event.end_date && (
                            <span className="text-gray-400"> → {event.end_date}</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-gray-700 max-w-[180px] truncate" title={event.role}>
                          {event.role}
                        </td>
                        <td className="px-4 py-3 text-gray-600">
                          {DIMENSION_LABELS[event.authority_dimension] ?? event.authority_dimension}
                        </td>
                        <td className="px-4 py-3 text-gray-500 max-w-[140px] truncate" title={event.contract_source ?? ''}>
                          {event.contract_source ?? '—'}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${extractionInfo.colour}`}>
                            {extractionInfo.label}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          {isUpdating ? (
                            <Spinner className="h-3 w-3" />
                          ) : (
                            <div className="flex items-center gap-2">
                              {event.extraction_status !== 'confirmed' && (
                                <button
                                  onClick={() => handleUpdateStatus(event.id, 'confirmed')}
                                  className="text-green-700 hover:underline font-medium"
                                >
                                  Confirm
                                </button>
                              )}
                              {event.extraction_status !== 'flagged' && (
                                <button
                                  onClick={() => handleUpdateStatus(event.id, 'flagged')}
                                  className="text-red-600 hover:underline font-medium"
                                >
                                  Flag
                                </button>
                              )}
                            </div>
                          )}
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
