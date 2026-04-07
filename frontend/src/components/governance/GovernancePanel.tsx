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
} from '../../api/governance';
import type {
  EntityDirectoryRunResponse,
  EntityResponse,
  EntityDiscrepancyResponse,
} from '../../api/types';

// ── Props ─────────────────────────────────────────────────────────────────────

interface GovernancePanelProps {
  projectId: string;
}

// ── Constants ─────────────────────────────────────────────────────────────────

const POLL_INTERVAL_MS = 5_000;

// ── Helpers ───────────────────────────────────────────────────────────────────

function statusBadge(status: EntityDirectoryRunResponse['status']) {
  if (status === 'running')
    return <Badge color="navy">Processing</Badge>;
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
  const isRunning = run?.status === 'running';
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
            {isRunning && run && (
              <div className="space-y-1.5 pt-1">
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Reading documents — {run.chunks_processed} of {run.total_chunks} chunks processed</span>
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

      {/* State confirmed — read-only entity list */}
      {isConfirmed && (
        <div className="space-y-4">
          <EntitySection
            title="Organisations"
            entities={orgs}
            expanded={orgsExpanded}
            onToggle={() => setOrgsExpanded((v) => !v)}
            onPatch={handlePatchEntity}
            onConfirmAll={() => handleConfirmAll('organisation')}
            readOnly
          />
          <EntitySection
            title="Individuals"
            entities={inds}
            expanded={indsExpanded}
            onToggle={() => setIndsExpanded((v) => !v)}
            onPatch={handlePatchEntity}
            onConfirmAll={() => handleConfirmAll('individual')}
            readOnly
          />
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
