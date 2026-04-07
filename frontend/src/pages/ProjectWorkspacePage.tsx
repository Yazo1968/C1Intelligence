import { useCallback, useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { DocumentTable } from '../components/documents/DocumentTable';
import { DocumentUploadForm } from '../components/documents/DocumentUploadForm';
import { QueryInput } from '../components/query/QueryInput';
import { QueryResponse } from '../components/query/QueryResponse';
import { Round0Card } from '../components/query/Round0Card';
import { ContradictionAlert } from '../components/query/ContradictionAlert';
import { EmptyState } from '../components/ui/EmptyState';
import { Spinner } from '../components/ui/Spinner';
import { listDocuments } from '../api/documents';
import { assessQuery, submitQuery, getQueryStatus, getContradictions } from '../api/queries';
import { listProjects } from '../api/projects';
import type { DocumentResponse, QueryResponseSchema, ContradictionResponse, ProjectResponse } from '../api/types';
import type { Round0Assessment } from '../api/queries';
import { GovernancePanel } from '../components/governance/GovernancePanel';

const QUERY_POLL_INTERVAL_MS = 5_000;
const QUERY_POLL_MAX_MS = 15 * 60 * 1_000; // 15 minutes

export function ProjectWorkspacePage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [activeTab, setActiveTab] = useState('documents');
  const [project, setProject] = useState<ProjectResponse | null>(null);

  // Documents state
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [docsLoading, setDocsLoading] = useState(true);

  // Query state
  const [queryResponse, setQueryResponse] = useState<QueryResponseSchema | null>(null);
  const [queryLoading, setQueryLoading] = useState(false);
  const [queryError, setQueryError] = useState<string | null>(null);
  const [queryStatusMessage, setQueryStatusMessage] = useState<string | null>(null);
  const queryPollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const queryPollStartRef = useRef<number>(0);

  // Round 0 assessment state
  const [round0Assessment, setRound0Assessment] = useState<Round0Assessment | null>(null);
  const lastQueryTextRef = useRef<string>('');

  // Contradictions state
  const [contradictions, setContradictions] = useState<ContradictionResponse[]>([]);
  const [contradictionsLoading, setContradictionsLoading] = useState(false);

  const stopQueryPolling = useCallback(() => {
    if (queryPollRef.current) {
      clearInterval(queryPollRef.current);
      queryPollRef.current = null;
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => stopQueryPolling();
  }, [stopQueryPolling]);

  const fetchDocuments = useCallback(async () => {
    if (!projectId) return;
    setDocsLoading(true);
    try {
      const data = await listDocuments(projectId);
      setDocuments(data);
    } catch { /* handled by API client */ }
    finally { setDocsLoading(false); }
  }, [projectId]);

  const fetchProject = useCallback(async () => {
    if (!projectId) return;
    try {
      const projects = await listProjects();
      const found = projects.find((p) => p.id === projectId);
      if (found) setProject(found);
    } catch { /* handled by API client */ }
  }, [projectId]);

  const fetchContradictions = useCallback(async () => {
    if (!projectId) return;
    setContradictionsLoading(true);
    try {
      const data = await getContradictions(projectId);
      setContradictions(data);
    } catch { /* handled by API client */ }
    finally { setContradictionsLoading(false); }
  }, [projectId]);

  useEffect(() => { fetchProject(); }, [fetchProject]);
  useEffect(() => { fetchDocuments(); }, [fetchDocuments]);
  useEffect(() => {
    if (activeTab === 'contradictions') fetchContradictions();
  }, [activeTab, fetchContradictions]);

  const handleAssess = async (queryText: string) => {
    if (!projectId) return;
    setQueryError(null);
    setQueryResponse(null);
    setRound0Assessment(null);
    setQueryLoading(true);
    setQueryStatusMessage('Assessing query...');
    stopQueryPolling();
    lastQueryTextRef.current = queryText;

    try {
      const result = await assessQuery(projectId, queryText);
      setRound0Assessment(result);
      setQueryLoading(false);
      setQueryStatusMessage(null);
    } catch (err) {
      setQueryError(err instanceof Error ? err.message : 'Assessment failed');
      setQueryLoading(false);
      setQueryStatusMessage(null);
    }
  };

  const handleQuery = async (queryText: string, domains?: string[]) => {
    if (!projectId) return;
    setQueryError(null);
    setQueryResponse(null);
    setQueryLoading(true);
    setQueryStatusMessage('Submitting query...');
    stopQueryPolling();

    try {
      const res = await submitQuery(projectId, queryText, domains);
      const queryId = res.query_id;
      setQueryStatusMessage('Analysing documents across specialist domains...');

      queryPollStartRef.current = Date.now();
      queryPollRef.current = setInterval(async () => {
        if (Date.now() - queryPollStartRef.current > QUERY_POLL_MAX_MS) {
          stopQueryPolling();
          setQueryLoading(false);
          setQueryStatusMessage(null);
          setQueryError('Query timed out. The analysis may still be running — check the Audit Log.');
          return;
        }

        try {
          const statusRes = await getQueryStatus(projectId, queryId);
          if (statusRes.status === 'COMPLETE' && statusRes.response) {
            stopQueryPolling();
            setQueryResponse(statusRes.response);
            setQueryLoading(false);
            setQueryStatusMessage(null);
          } else if (statusRes.status === 'FAILED') {
            stopQueryPolling();
            setQueryLoading(false);
            setQueryStatusMessage(null);
            setQueryError('Query analysis failed. Please try again.');
          }
        } catch {
          // Transient network error — keep polling
        }
      }, QUERY_POLL_INTERVAL_MS);

    } catch (err) {
      setQueryError(err instanceof Error ? err.message : 'Query failed');
      setQueryLoading(false);
      setQueryStatusMessage(null);
    }
  };

  const getDocLabel = (docId: string) => {
    const doc = documents.find((d) => d.id === docId);
    return doc ? doc.filename : docId.slice(0, 8) + '...';
  };

  if (!projectId) return null;

  return (
    <AppShell
      title={project?.name ?? 'Project'}
      subtitle={project?.description ?? undefined}
      projectName={project?.name}
      activeTab={activeTab}
      onTabChange={setActiveTab}
    >
      <div className="max-w-5xl mx-auto px-6 py-6">
        {/* Documents Tab */}
        {activeTab === 'documents' && (
          <>
            <DocumentUploadForm projectId={projectId} onUploaded={fetchDocuments} />
            <DocumentTable documents={documents} loading={docsLoading} />
          </>
        )}

        {/* Query Tab */}
        {activeTab === 'query' && (
          <div className="space-y-5">
            <QueryInput onSubmit={handleAssess} loading={queryLoading} />

            {round0Assessment && !queryResponse && (
              <Round0Card
                assessment={round0Assessment}
                loading={queryLoading}
                onRunAnalysis={(domains) => {
                  handleQuery(lastQueryTextRef.current, domains);
                }}
                onRunAll={() => {
                  handleQuery(lastQueryTextRef.current);
                }}
              />
            )}

            {queryLoading && queryStatusMessage && (
              <div className="flex items-center gap-2 text-sm text-navy-700">
                <Spinner className="h-4 w-4" />
                <span>{queryStatusMessage}</span>
              </div>
            )}

            {queryError && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4 text-sm text-red-700">
                {queryError}
              </div>
            )}

            {queryResponse && <QueryResponse response={queryResponse} />}
          </div>
        )}

        {/* Governance Tab */}
        {activeTab === 'governance' && projectId && (
          <GovernancePanel projectId={projectId} />
        )}

        {/* Contradictions Tab */}
        {activeTab === 'contradictions' && (
          <div>
            <h2 className="text-lg font-semibold text-navy-900 mb-4">Contradiction Flags</h2>
            {contradictionsLoading ? (
              <div className="flex justify-center py-12"><Spinner className="h-6 w-6" /></div>
            ) : contradictions.length === 0 ? (
              <EmptyState
                title="No contradictions detected"
                description="When documents contain conflicting values for the same field, they will appear here."
              />
            ) : (
              <div className="space-y-3">
                {contradictions.map((c) => (
                  <ContradictionAlert
                    key={c.id}
                    contradiction={{
                      field_name: c.field_name,
                      document_a_reference: getDocLabel(c.document_a_id),
                      value_a: '',
                      document_b_reference: getDocLabel(c.document_b_id),
                      value_b: '',
                      description: c.description ?? '',
                    }}
                  />
                ))}
              </div>
            )}
          </div>
        )}

      </div>
    </AppShell>
  );
}
