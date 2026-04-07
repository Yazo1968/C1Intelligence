import { useCallback, useEffect, useRef, useState } from 'react';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { Spinner } from '../ui/Spinner';
import {
  triggerDirectoryRun,
  getDirectoryStatus,
  listEntities,
  listDiscrepancies,
  patchEntity,
  resolveDiscrepancy,
  confirmDirectory,
  triggerEventRun,
  getEventRunStatus,
  listEvents,
  listEventQuestions,
  patchEvent,
  answerQuestion,
  confirmEventLog,
} from '../../api/governance';
import type {
  EntityDirectoryRunResponse,
  EntityResponse,
  EntityDiscrepancyResponse,
  EventLogRunResponse,
  EntityEventResponse,
  EventLogQuestionResponse,
} from '../../api/types';

// ── Props ─────────────────────────────────────────────────────────────────────

interface GovernancePanelProps {
  projectId: string;
}

// ── Constants ─────────────────────────────────────────────────────────────────

const POLL_INTERVAL_MS = 5_000;

// ── Helpers ───────────────────────────────────────────────────────────────────

function statusBadge(status: EntityDirectoryRunResponse['status']) {
  if (status === 'running' || status === 'extracting')
    return <Badge color="navy">Processing</Badge>;
  if (status === 'consolidating')
    return <Badge color="navy">Consolidating</Badge>;
  if (status === 'awaiting_confirmation')
    return <Badge color="amber">Ready for Review</Badge>;
  if (status === 'confirmed')
    return <Badge color="green">Confirmed</Badge>;
  return <Badge color="gray">Not Built</Badge>;
}

// ── Main component ────────────────────────────────────────────────────────────

export function GovernancePanel({ projectId }: GovernancePanelProps) {
  const [run, setRun] = useState<EntityDirectoryRunResponse | null>(null);
  const [entities, setEntities] = useState<EntityResponse[]>([]);
  const [discrepancies, setDiscrepancies] = useState<EntityDiscrepancyResponse[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [building, setBuilding] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [orgsExpanded, setOrgsExpanded] = useState(true);
  const [indsExpanded, setIndsExpanded] = useState(true);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Event log state
  const [eventLogRuns, setEventLogRuns] = useState<
    Record<string, EventLogRunResponse>
  >({});
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);
  const eventPollRefs = useRef<Record<string, ReturnType<typeof setInterval>>>({});

  // ── Polling ────────────────────────────────────────────────────────────────

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const loadReviewData = useCallback(async () => {
    try {
      const [ents, discs] = await Promise.all([
        listEntities(projectId),
        listDiscrepancies(projectId),
      ]);
      setEntities(ents);
      setDiscrepancies(discs);
    } catch {
      // Non-fatal — panel will show empty sections
    }
  }, [projectId]);

  const startPolling = useCallback(() => {
    stopPolling();
    pollRef.current = setInterval(async () => {
      try {
        const status = await getDirectoryStatus(projectId);
        setRun(status);
        if (status.status === 'awaiting_confirmation') {
          stopPolling();
          await loadReviewData();
        } else if (status.status === 'failed') {
          stopPolling();
          setError(status.error_message ?? 'Extraction failed. Please try again.');
        }
      } catch {
        stopPolling();
      }
    }, POLL_INTERVAL_MS);
  }, [projectId, stopPolling, loadReviewData]);

  // ── Initial load ───────────────────────────────────────────────────────────

  useEffect(() => {
    let cancelled = false;
    async function init() {
      try {
        const status = await getDirectoryStatus(projectId);
        if (cancelled) return;
        setRun(status);
        if (status.status === 'running') {
          startPolling();
        } else if (
          status.status === 'awaiting_confirmation' ||
          status.status === 'confirmed'
        ) {
          await loadReviewData();
        }
      } catch {
        // No run yet — State A (no error shown)
      }
    }
    init();
    return () => {
      cancelled = true;
      stopPolling();
      Object.keys(eventPollRefs.current).forEach(stopEventPoll);
    };
  }, [projectId, startPolling, stopPolling, loadReviewData]);

  // ── Actions ────────────────────────────────────────────────────────────────

  async function handleBuild() {
    setError(null);
    setBuilding(true);
    try {
      const newRun = await triggerDirectoryRun(projectId);
      setRun(newRun);
      startPolling();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to start extraction.');
    } finally {
      setBuilding(false);
    }
  }

  async function handleConfirmAll(type: 'organisation' | 'individual') {
    const targets = entities.filter(
      (e) => e.entity_type === type && e.confirmation_status === 'proposed',
    );
    await Promise.all(
      targets.map((e) =>
        patchEntity(projectId, e.id, { confirmation_status: 'confirmed' }),
      ),
    );
    await loadReviewData();
  }

  async function handlePatchEntity(
    entityId: string,
    updates: { canonical_name?: string; confirmation_status?: 'confirmed' | 'rejected'; user_note?: string },
  ) {
    try {
      await patchEntity(projectId, entityId, updates);
      await loadReviewData();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to update entity.');
    }
  }

  async function handleResolveDiscrepancy(
    discrepancyId: string,
    resolution: 'same_entity' | 'different_entities' | 'correction',
    resolvedCanonical?: string,
  ) {
    try {
      await resolveDiscrepancy(projectId, discrepancyId, {
        resolution,
        resolved_canonical: resolvedCanonical,
      });
      setDiscrepancies((prev) => prev.filter((d) => d.id !== discrepancyId));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to resolve discrepancy.');
    }
  }

  async function handleConfirmDirectory() {
    setError(null);
    setConfirming(true);
    try {
      const updated = await confirmDirectory(projectId);
      setRun(updated);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to confirm directory.');
    } finally {
      setConfirming(false);
    }
  }

  // ── Event log helpers ────────────────────────────────────────────────────

  function stopEventPoll(entityId: string) {
    if (eventPollRefs.current[entityId]) {
      clearInterval(eventPollRefs.current[entityId]);
      delete eventPollRefs.current[entityId];
    }
  }

  async function handleBuildEventLog(entityId: string) {
    try {
      const newRun = await triggerEventRun(projectId, entityId);
      setEventLogRuns((prev) => ({ ...prev, [entityId]: newRun }));
      // Poll for completion
      stopEventPoll(entityId);
      eventPollRefs.current[entityId] = setInterval(async () => {
        try {
          const status = await getEventRunStatus(projectId, entityId);
          setEventLogRuns((prev) => ({ ...prev, [entityId]: status }));
          if (status.status !== 'running') {
            stopEventPoll(entityId);
          }
        } catch {
          stopEventPoll(entityId);
        }
      }, POLL_INTERVAL_MS);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to start event extraction.');
    }
  }

  function handleOpenEventLog(entityId: string) {
    setSelectedEntityId(entityId);
  }

  function handleCloseEventLog() {
    setSelectedEntityId(null);
  }

  async function handleEventLogConfirmed(entityId: string) {
    const updated = await getEventRunStatus(projectId, entityId);
    setEventLogRuns((prev) => ({ ...prev, [entityId]: updated }));
    setSelectedEntityId(null);
  }

  // ── Derived state ──────────────────────────────────────────────────────────

  const orgs = entities.filter((e) => e.entity_type === 'organisation');
  const inds = entities.filter((e) => e.entity_type === 'individual');
  const unresolvedCount = discrepancies.length;
  const confirmedCount = entities.filter(
    (e) => e.confirmation_status === 'confirmed',
  ).length;
  const canConfirmDirectory =
    unresolvedCount === 0 && confirmedCount > 0;

  // ── Render ─────────────────────────────────────────────────────────────────

  const noRunYet = !run || run.status === 'failed';
  const isRunning = run?.status === 'extracting' || run?.status === 'running';
  const isConsolidating = run?.status === 'consolidating';
  const isReview = run?.status === 'awaiting_confirmation';
  const isConfirmed = run?.status === 'confirmed';

  return (
    <div className="space-y-4">

      {/* Error banner */}
      {error && (
        <div className="flex items-start justify-between gap-3 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="shrink-0 text-red-400 hover:text-red-600">✕</button>
        </div>
      )}

      {/* Header card */}
      <div className="rounded-lg border border-gray-200 bg-white p-5">
        <div className="flex items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h2 className="text-base font-semibold text-gray-900">Entity Directory</h2>
              {run ? statusBadge(run.status) : <Badge color="gray">Not Built</Badge>}
            </div>

            {/* State A description */}
            {noRunYet && (
              <p className="text-sm text-gray-500">
                C1 reads every project document and identifies all organisations and
                individuals by name. No roles, scope, or relationships are inferred —
                names only. You review and confirm the result before proceeding.
              </p>
            )}

            {/* State B-Running progress */}
            {(isRunning || isConsolidating) && run && (
              <div className="space-y-1.5 pt-1">
                {isRunning ? (
                  <>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>
                        Reading documents — {run.chunks_processed} of {run.total_chunks} chunks processed
                        {run.organisations_found > 0 || run.individuals_found > 0 ? (
                          <span className="ml-2 text-gray-400">
                            · {run.organisations_found} org{run.organisations_found !== 1 ? 's' : ''},{' '}
                            {run.individuals_found} individual{run.individuals_found !== 1 ? 's' : ''} found so far
                          </span>
                        ) : null}
                      </span>
                      <span>
                        {run.total_chunks > 0
                          ? Math.round((run.chunks_processed / run.total_chunks) * 100)
                          : 0}%
                      </span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-gray-100">
                      <div
                        className="h-2 rounded-full bg-navy-900 transition-all duration-500"
                        style={{
                          width: run.total_chunks > 0
                            ? `${Math.round((run.chunks_processed / run.total_chunks) * 100)}%`
                            : '0%',
                        }}
                      />
                    </div>
                    <p className="text-xs text-gray-400">
                      This may take a few minutes depending on project size.
                    </p>
                  </>
                ) : (
                  <p className="text-sm text-gray-500">
                    Consolidating results — grouping name variants and detecting discrepancies...
                  </p>
                )}
              </div>
            )}

            {/* State B-Review summary */}
            {isReview && run && (
              <p className="text-sm text-gray-500">
                Found {run.organisations_found} organisation{run.organisations_found !== 1 ? 's' : ''} and{' '}
                {run.individuals_found} individual{run.individuals_found !== 1 ? 's' : ''}.
                {unresolvedCount > 0 && (
                  <span className="ml-1 text-amber-600 font-medium">
                    {unresolvedCount} discrepanc{unresolvedCount !== 1 ? 'ies' : 'y'} require resolution before confirming.
                  </span>
                )}
              </p>
            )}
          </div>

          {/* Action button */}
          <div className="shrink-0">
            {noRunYet && (
              <Button onClick={handleBuild} disabled={building}>
                {building ? (
                  <span className="flex items-center gap-2"><Spinner className="h-4 w-4" /> Building...</span>
                ) : (
                  'Build Entity Directory'
                )}
              </Button>
            )}
            {isReview && (
              <Button
                onClick={handleConfirmDirectory}
                disabled={!canConfirmDirectory || confirming}
                className="bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-400"
              >
                {confirming ? (
                  <span className="flex items-center gap-2"><Spinner className="h-4 w-4" /> Confirming...</span>
                ) : (
                  'Confirm Directory'
                )}
              </Button>
            )}
            {isConfirmed && (
              <Button variant="secondary" onClick={handleBuild} disabled={building}>
                Rebuild Directory
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* State B-Review content */}
      {isReview && (
        <div className="space-y-4">

          {/* Discrepancies section */}
          {unresolvedCount > 0 && (
            <div className="rounded-lg border border-amber-200 bg-white p-5 space-y-3">
              <h3 className="text-sm font-semibold text-gray-700">
                Resolve Discrepancies ({unresolvedCount} remaining)
              </h3>
              <div className="space-y-3">
                {discrepancies.map((disc) => (
                  <DiscrepancyCard
                    key={disc.id}
                    discrepancy={disc}
                    onResolve={handleResolveDiscrepancy}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Organisations section */}
          <EntitySection
            title="Organisations"
            entities={orgs}
            expanded={orgsExpanded}
            onToggle={() => setOrgsExpanded((v) => !v)}
            onPatch={handlePatchEntity}
            onConfirmAll={() => handleConfirmAll('organisation')}
          />

          {/* Individuals section */}
          <EntitySection
            title="Individuals"
            entities={inds}
            expanded={indsExpanded}
            onToggle={() => setIndsExpanded((v) => !v)}
            onPatch={handlePatchEntity}
            onConfirmAll={() => handleConfirmAll('individual')}
          />
        </div>
      )}

      {/* State C — confirmed directory with event log controls */}
      {isConfirmed && (
        <div className="space-y-4">
          <StateCEntitySection
            title="Organisations"
            entities={orgs}
            expanded={orgsExpanded}
            onToggle={() => setOrgsExpanded((v) => !v)}
            eventLogRuns={eventLogRuns}
            onBuildEventLog={handleBuildEventLog}
            onOpenEventLog={handleOpenEventLog}
          />
          <StateCEntitySection
            title="Individuals"
            entities={inds}
            expanded={indsExpanded}
            onToggle={() => setIndsExpanded((v) => !v)}
            eventLogRuns={eventLogRuns}
            onBuildEventLog={handleBuildEventLog}
            onOpenEventLog={handleOpenEventLog}
          />
          {/* Event Log slide-over panel */}
          {selectedEntityId && (
            <EventLogPanel
              projectId={projectId}
              entityId={selectedEntityId}
              entity={entities.find((e) => e.id === selectedEntityId)!}
              eventLogRun={eventLogRuns[selectedEntityId] ?? null}
              onClose={handleCloseEventLog}
              onConfirmed={handleEventLogConfirmed}
              onBuild={handleBuildEventLog}
              patchEventFn={(eventId, body) => patchEvent(projectId, selectedEntityId, eventId, body)}
              answerQuestionFn={(questionId, answer) =>
                answerQuestion(projectId, selectedEntityId, questionId, { answer })
              }
              confirmFn={() => confirmEventLog(projectId, selectedEntityId)}
              listEventsFn={() => listEvents(projectId, selectedEntityId)}
              listQuestionsFn={() => listEventQuestions(projectId, selectedEntityId)}
            />
          )}
        </div>
      )}
    </div>
  );
}

// ── DiscrepancyCard ───────────────────────────────────────────────────────────

interface DiscrepancyCardProps {
  discrepancy: EntityDiscrepancyResponse;
  onResolve: (
    id: string,
    resolution: 'same_entity' | 'different_entities' | 'correction',
    canonical?: string,
  ) => void;
}

function DiscrepancyCard({ discrepancy, onResolve }: DiscrepancyCardProps) {
  const [correctionInput, setCorrectionInput] = useState('');
  const [showCorrection, setShowCorrection] = useState(false);

  return (
    <div className="rounded-md border border-amber-100 bg-amber-50 p-4 space-y-3">
      <div className="flex items-start gap-2">
        <span className="text-amber-500 mt-0.5">⚠</span>
        <div className="space-y-1">
          <p className="text-sm font-medium text-gray-800 capitalize">
            {discrepancy.discrepancy_type.replace('_', ' ')}
          </p>
          <p className="text-sm text-gray-600">{discrepancy.description}</p>
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        <Button
          size="sm"
          variant="secondary"
          onClick={() => onResolve(discrepancy.id, 'same_entity', discrepancy.name_a)}
        >
          Same entity — keep "{discrepancy.name_a}"
        </Button>
        {discrepancy.name_b && (
          <Button
            size="sm"
            variant="secondary"
            onClick={() => onResolve(discrepancy.id, 'same_entity', discrepancy.name_b!)}
          >
            Same entity — keep "{discrepancy.name_b}"
          </Button>
        )}
        <Button
          size="sm"
          variant="secondary"
          onClick={() => onResolve(discrepancy.id, 'different_entities')}
        >
          Different entities
        </Button>
        <Button
          size="sm"
          variant="secondary"
          onClick={() => setShowCorrection((v) => !v)}
        >
          Enter correct name
        </Button>
      </div>
      {showCorrection && (
        <div className="flex gap-2">
          <input
            type="text"
            value={correctionInput}
            onChange={(e) => setCorrectionInput(e.target.value)}
            placeholder="Correct canonical name"
            className="flex-1 rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-navy-900/20"
          />
          <Button
            size="sm"
            disabled={!correctionInput.trim()}
            onClick={() => onResolve(discrepancy.id, 'correction', correctionInput.trim())}
          >
            Save
          </Button>
        </div>
      )}
    </div>
  );
}

// ── EntitySection ─────────────────────────────────────────────────────────────

interface EntitySectionProps {
  title: string;
  entities: EntityResponse[];
  expanded: boolean;
  onToggle: () => void;
  onPatch: (
    id: string,
    updates: { canonical_name?: string; confirmation_status?: 'confirmed' | 'rejected' },
  ) => void;
  onConfirmAll: () => void;
  readOnly?: boolean;
}

function EntitySection({
  title,
  entities,
  expanded,
  onToggle,
  onPatch,
  onConfirmAll,
  readOnly = false,
}: EntitySectionProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white">
      <div className="flex items-center justify-between px-5 py-3 border-b border-gray-100">
        <button
          onClick={onToggle}
          className="flex items-center gap-2 text-sm font-semibold text-gray-700 hover:text-gray-900"
        >
          <span>{expanded ? '▾' : '▸'}</span>
          {title} ({entities.length})
        </button>
        {!readOnly && entities.some((e) => e.confirmation_status === 'proposed') && (
          <button
            onClick={onConfirmAll}
            className="text-xs text-navy-900 hover:underline"
          >
            Confirm all
          </button>
        )}
      </div>
      {expanded && (
        <div className="divide-y divide-gray-50">
          {entities.length === 0 ? (
            <p className="px-5 py-4 text-sm text-gray-400">None found.</p>
          ) : (
            entities.map((entity) => (
              <EntityRow
                key={entity.id}
                entity={entity}
                onPatch={onPatch}
                readOnly={readOnly}
              />
            ))
          )}
        </div>
      )}
    </div>
  );
}

// ── EntityRow ─────────────────────────────────────────────────────────────────

interface EntityRowProps {
  entity: EntityResponse;
  onPatch: (
    id: string,
    updates: { canonical_name?: string; confirmation_status?: 'confirmed' | 'rejected' },
  ) => void;
  readOnly?: boolean;
}

function EntityRow({ entity, onPatch, readOnly = false }: EntityRowProps) {
  const [editing, setEditing] = useState(false);
  const [editValue, setEditValue] = useState(entity.canonical_name);

  const isConfirmed = entity.confirmation_status === 'confirmed';
  const isRejected = entity.confirmation_status === 'rejected';

  const borderColor = isConfirmed
    ? 'border-l-emerald-500'
    : isRejected
    ? 'border-l-gray-300'
    : 'border-l-gray-200';

  return (
    <div
      className={`flex items-start justify-between gap-4 px-5 py-3 border-l-2 ${borderColor} ${isRejected ? 'opacity-50' : ''}`}
    >
      <div className="space-y-0.5 min-w-0">
        <div className="flex items-center gap-2">
          {isConfirmed && <span className="text-emerald-500 text-xs">✓</span>}
          <p className={`text-sm font-medium text-gray-900 ${isRejected ? 'line-through' : ''}`}>
            {entity.title ? `${entity.title} ` : ''}{entity.canonical_name}
          </p>
        </div>
        {entity.name_variants.length > 0 && (
          <p className="text-xs text-gray-400">
            Also found as: {entity.name_variants.join(', ')}
          </p>
        )}
        {entity.short_address && (
          <p className="text-xs text-gray-400">{entity.short_address}</p>
        )}
        {editing && (
          <div className="flex gap-2 mt-2">
            <input
              type="text"
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              className="flex-1 rounded-md border border-gray-300 px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-navy-900/20"
            />
            <Button
              size="sm"
              disabled={!editValue.trim() || editValue === entity.canonical_name}
              onClick={() => {
                onPatch(entity.id, { canonical_name: editValue.trim() });
                setEditing(false);
              }}
            >
              Save
            </Button>
            <Button size="sm" variant="secondary" onClick={() => { setEditing(false); setEditValue(entity.canonical_name); }}>
              Cancel
            </Button>
          </div>
        )}
      </div>
      {!readOnly && !editing && (
        <div className="flex items-center gap-1 shrink-0">
          {!isConfirmed && !isRejected && (
            <Button
              size="sm"
              variant="secondary"
              onClick={() => onPatch(entity.id, { confirmation_status: 'confirmed' })}
            >
              Confirm
            </Button>
          )}
          <Button size="sm" variant="secondary" onClick={() => setEditing(true)}>
            Edit
          </Button>
          {!isRejected && (
            <button
              onClick={() => onPatch(entity.id, { confirmation_status: 'rejected' })}
              className="text-gray-400 hover:text-red-500 px-1"
              title="Reject"
            >
              ✕
            </button>
          )}
        </div>
      )}
    </div>
  );
}

// ── StateCEntitySection ───────────────────────────────────────────────────────

interface StateCEntitySectionProps {
  title: string;
  entities: EntityResponse[];
  expanded: boolean;
  onToggle: () => void;
  eventLogRuns: Record<string, EventLogRunResponse>;
  onBuildEventLog: (entityId: string) => void;
  onOpenEventLog: (entityId: string) => void;
}

function StateCEntitySection({
  title,
  entities,
  expanded,
  onToggle,
  eventLogRuns,
  onBuildEventLog,
  onOpenEventLog,
}: StateCEntitySectionProps) {
  const confirmed = entities.filter((e) => e.confirmation_status === 'confirmed');
  return (
    <div className="rounded-lg border border-gray-200 bg-white">
      <button
        onClick={onToggle}
        className="flex w-full items-center gap-2 px-5 py-3 text-sm font-semibold text-gray-700 hover:text-gray-900 border-b border-gray-100"
      >
        <span>{expanded ? '▾' : '▸'}</span>
        {title} ({confirmed.length})
      </button>
      {expanded && (
        <div className="divide-y divide-gray-50">
          {confirmed.length === 0 ? (
            <p className="px-5 py-4 text-sm text-gray-400">None confirmed.</p>
          ) : (
            confirmed.map((entity) => {
              const run = eventLogRuns[entity.id] ?? null;
              return (
                <div
                  key={entity.id}
                  className="flex items-center justify-between gap-4 px-5 py-3"
                >
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {entity.title ? `${entity.title} ` : ''}{entity.canonical_name}
                    </p>
                    {entity.short_address && (
                      <p className="text-xs text-gray-400">{entity.short_address}</p>
                    )}
                  </div>
                  <div className="shrink-0">
                    {!run && (
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => onBuildEventLog(entity.id)}
                      >
                        Build Event Log +
                      </Button>
                    )}
                    {run?.status === 'running' && (
                      <span className="flex items-center gap-1.5 text-xs text-gray-500">
                        <Spinner className="h-3 w-3" /> Extracting events...
                      </span>
                    )}
                    {run?.status === 'awaiting_confirmation' && (
                      <Button
                        size="sm"
                        className="bg-amber-500 hover:bg-amber-600 text-white"
                        onClick={() => onOpenEventLog(entity.id)}
                      >
                        {run.events_extracted} events · Review →
                      </Button>
                    )}
                    {run?.status === 'confirmed' && (
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => onOpenEventLog(entity.id)}
                      >
                        Confirmed · {run.events_extracted} events ✓
                      </Button>
                    )}
                    {run?.status === 'failed' && (
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => onBuildEventLog(entity.id)}
                        className="text-red-600 border-red-300"
                      >
                        Retry
                      </Button>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}

// ── EventLogPanel (slide-over) ────────────────────────────────────────────────

interface EventLogPanelProps {
  projectId: string;
  entityId: string;
  entity: EntityResponse;
  eventLogRun: EventLogRunResponse | null;
  onClose: () => void;
  onConfirmed: (entityId: string) => void;
  onBuild: (entityId: string) => void;
  patchEventFn: (eventId: string, body: Record<string, unknown>) => Promise<EntityEventResponse>;
  answerQuestionFn: (questionId: string, answer: string) => Promise<EventLogQuestionResponse>;
  confirmFn: () => Promise<EventLogRunResponse>;
  listEventsFn: () => Promise<EntityEventResponse[]>;
  listQuestionsFn: () => Promise<EventLogQuestionResponse[]>;
}

function EventLogPanel({
  entityId,
  entity,
  eventLogRun,
  onClose,
  onConfirmed,
  onBuild,
  patchEventFn,
  answerQuestionFn,
  confirmFn,
  listEventsFn,
  listQuestionsFn,
}: EventLogPanelProps) {
  const [events, setEvents] = useState<EntityEventResponse[]>([]);
  const [questions, setQuestions] = useState<EventLogQuestionResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [questionsExpanded, setQuestionsExpanded] = useState(true);

  const canConfirm =
    eventLogRun?.status === 'awaiting_confirmation' &&
    questions.length === 0 &&
    !confirming;

  const loadData = useCallback(async () => {
    if (!eventLogRun || eventLogRun.status === 'running') return;
    try {
      const [evts, qs] = await Promise.all([listEventsFn(), listQuestionsFn()]);
      setEvents(evts);
      setQuestions(qs);
    } catch {
      // non-fatal
    } finally {
      setLoading(false);
    }
  }, [eventLogRun, listEventsFn, listQuestionsFn]);

  useEffect(() => {
    setLoading(true);
    loadData();
  }, [loadData]);

  async function handleConfirm() {
    setConfirming(true);
    try {
      await confirmFn();
      onConfirmed(entityId);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to confirm event log.');
    } finally {
      setConfirming(false);
    }
  }

  async function handlePatchEvent(eventId: string, updates: Record<string, unknown>) {
    try {
      const updated = await patchEventFn(eventId, updates);
      setEvents((prev) => prev.map((e) => (e.id === eventId ? updated : e)));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to update event.');
    }
  }

  async function handleAnswerQuestion(questionId: string, answer: string) {
    try {
      await answerQuestionFn(questionId, answer);
      setQuestions((prev) => prev.filter((q) => q.id !== questionId));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to submit answer.');
    }
  }

  return (
    <div className="fixed inset-y-0 right-0 z-50 flex w-full max-w-2xl flex-col border-l border-gray-200 bg-white shadow-2xl">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 border-b border-gray-200 px-6 py-4">
        <div>
          <h2 className="text-base font-semibold text-gray-900">{entity.canonical_name}</h2>
          {entity.name_variants.length > 0 && (
            <p className="mt-0.5 text-xs text-gray-400">
              Also known as: {entity.name_variants.join(', ')}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {canConfirm && (
            <Button
              size="sm"
              className="bg-emerald-600 hover:bg-emerald-700 text-white"
              onClick={handleConfirm}
              disabled={confirming}
            >
              {confirming ? (
                <span className="flex items-center gap-1.5"><Spinner className="h-3 w-3" /> Confirming...</span>
              ) : (
                'Confirm Event Log'
              )}
            </Button>
          )}
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-lg leading-none"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mx-6 mt-3 flex items-start justify-between gap-2 rounded border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
          <span>{error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">

        {/* Running state */}
        {eventLogRun?.status === 'running' && (
          <div className="flex flex-col items-center justify-center py-16 gap-3 text-gray-500">
            <Spinner className="h-6 w-6" />
            <p className="text-sm">Extracting event log...</p>
            <p className="text-xs text-gray-400">Searching documents for mentions of this entity.</p>
          </div>
        )}

        {/* No run yet */}
        {!eventLogRun && (
          <div className="flex flex-col items-center justify-center py-16 gap-3">
            <p className="text-sm text-gray-500">No event log has been built for this entity.</p>
            <Button onClick={() => onBuild(entityId)}>Build Event Log</Button>
          </div>
        )}

        {/* Questions */}
        {eventLogRun && eventLogRun.status !== 'running' && questions.length > 0 && (
          <div className="rounded-lg border border-amber-200 bg-amber-50">
            <button
              onClick={() => setQuestionsExpanded((v) => !v)}
              className="flex w-full items-center justify-between px-4 py-3 text-sm font-semibold text-amber-800"
            >
              <span>⚠ Questions requiring resolution ({questions.length})</span>
              <span>{questionsExpanded ? '▾' : '▸'}</span>
            </button>
            {questionsExpanded && (
              <div className="divide-y divide-amber-100 px-4 pb-4 space-y-3 pt-2">
                {questions.map((q) => (
                  <QuestionCard
                    key={q.id}
                    question={q}
                    events={events}
                    onAnswer={handleAnswerQuestion}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Events */}
        {eventLogRun && eventLogRun.status !== 'running' && !loading && (
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-gray-700">
              Event Log{events.length > 0 ? ` (${events.length})` : ''}
            </h3>
            {events.length === 0 ? (
              <p className="text-sm text-gray-400">
                No authority events were found for this entity in the project documents.
              </p>
            ) : (
              events.map((event) => (
                <EventCard
                  key={event.id}
                  event={event}
                  onPatch={handlePatchEvent}
                  readOnly={eventLogRun.status === 'confirmed'}
                />
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ── QuestionCard ──────────────────────────────────────────────────────────────

interface QuestionCardProps {
  question: EventLogQuestionResponse;
  events: EntityEventResponse[];
  onAnswer: (questionId: string, answer: string) => void;
}

function QuestionCard({ question, onAnswer }: QuestionCardProps) {
  const [answer, setAnswer] = useState('');

  return (
    <div className="space-y-2 pt-3">
      <p className="text-xs font-medium text-amber-800 uppercase tracking-wide">
        {question.question_type.replace(/_/g, ' ')}
      </p>
      <p className="text-sm text-gray-700">{question.question_text}</p>
      <div className="flex gap-2">
        <input
          type="text"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Your answer..."
          className="flex-1 rounded border border-gray-300 px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-navy-900/20"
        />
        <Button
          size="sm"
          disabled={!answer.trim()}
          onClick={() => onAnswer(question.id, answer.trim())}
        >
          Submit
        </Button>
      </div>
    </div>
  );
}

// ── EventCard ─────────────────────────────────────────────────────────────────

interface EventCardProps {
  event: EntityEventResponse;
  onPatch: (eventId: string, updates: Record<string, unknown>) => void;
  readOnly?: boolean;
}

function EventCard({ event, onPatch, readOnly = false }: EventCardProps) {
  const [excerptOpen, setExcerptOpen] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editNote, setEditNote] = useState(event.user_note ?? '');

  const borderColor =
    event.confirmation_status === 'confirmed'
      ? 'border-l-emerald-500'
      : event.confirmation_status === 'disputed'
      ? 'border-l-amber-500'
      : event.confirmation_status === 'rejected'
      ? 'border-l-gray-300'
      : 'border-l-gray-200';

  return (
    <div
      className={`rounded-lg border border-gray-200 border-l-2 ${borderColor} p-4 space-y-2 ${
        event.confirmation_status === 'rejected' ? 'opacity-50' : ''
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            {event.event_type.replace(/_/g, ' ')}
          </span>
          {event.event_date && (
            <span className="ml-2 text-xs text-gray-400">
              {event.event_date}
              {!event.event_date_certain && ' (approx.)'}
            </span>
          )}
          {!event.event_date && (
            <span className="ml-2 text-xs text-gray-400">date unknown</span>
          )}
        </div>
        {!readOnly && !editing && (
          <div className="flex items-center gap-1 shrink-0">
            {event.confirmation_status !== 'confirmed' && (
              <Button
                size="sm"
                variant="secondary"
                onClick={() => onPatch(event.id, { confirmation_status: 'confirmed' })}
              >
                ✓
              </Button>
            )}
            <Button size="sm" variant="secondary" onClick={() => setEditing(true)}>
              ✎
            </Button>
            {event.confirmation_status !== 'rejected' && (
              <button
                onClick={() => onPatch(event.id, { confirmation_status: 'rejected' })}
                className="text-gray-400 hover:text-red-500 px-1 text-sm"
              >
                ✕
              </button>
            )}
          </div>
        )}
      </div>

      {event.status_before && (
        <p className="text-xs text-gray-500">
          <span className="font-medium">Before:</span> {event.status_before}
        </p>
      )}
      {event.status_after && (
        <p className="text-xs text-gray-700">
          <span className="font-medium">After:</span> {event.status_after}
        </p>
      )}
      {event.initiated_by && (
        <p className="text-xs text-gray-500">
          <span className="font-medium">Initiated by:</span> {event.initiated_by}
        </p>
      )}
      {event.authorised_by && (
        <p className="text-xs text-gray-500">
          <span className="font-medium">Authorised by:</span> {event.authorised_by}
        </p>
      )}
      {event.source_document && (
        <p className="text-xs text-gray-400">
          <span className="font-medium">Source:</span> {event.source_document}
        </p>
      )}
      {event.source_excerpt && (
        <div>
          <button
            onClick={() => setExcerptOpen((v) => !v)}
            className="text-xs text-navy-900 hover:underline"
          >
            {excerptOpen ? '▾ Hide excerpt' : '▸ Source excerpt'}
          </button>
          {excerptOpen && (
            <blockquote className="mt-1 border-l-2 border-gray-200 pl-3 text-xs text-gray-500 italic">
              {event.source_excerpt}
            </blockquote>
          )}
        </div>
      )}

      {editing && (
        <div className="space-y-2 pt-1">
          <textarea
            value={editNote}
            onChange={(e) => setEditNote(e.target.value)}
            placeholder="Add a note about this event..."
            rows={2}
            className="w-full rounded border border-gray-300 px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-navy-900/20"
          />
          <div className="flex gap-2">
            <Button
              size="sm"
              onClick={() => {
                onPatch(event.id, { user_note: editNote });
                setEditing(false);
              }}
            >
              Save
            </Button>
            <Button size="sm" variant="secondary" onClick={() => setEditing(false)}>
              Cancel
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
