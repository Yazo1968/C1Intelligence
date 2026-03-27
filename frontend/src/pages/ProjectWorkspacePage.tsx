import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { DocumentTable } from '../components/documents/DocumentTable';
import { DocumentUploadForm } from '../components/documents/DocumentUploadForm';
import { QueryInput } from '../components/query/QueryInput';
import { QueryResponse } from '../components/query/QueryResponse';
import { ContradictionAlert } from '../components/query/ContradictionAlert';
import { EmptyState } from '../components/ui/EmptyState';
import { Spinner } from '../components/ui/Spinner';
import { listDocuments } from '../api/documents';
import { submitQuery, getContradictions } from '../api/queries';
import { listProjects } from '../api/projects';
import type { DocumentResponse, QueryResponseSchema, ContradictionResponse, ProjectResponse } from '../api/types';

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

  // Contradictions state
  const [contradictions, setContradictions] = useState<ContradictionResponse[]>([]);
  const [contradictionsLoading, setContradictionsLoading] = useState(false);

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

  const handleQuery = async (queryText: string) => {
    if (!projectId) return;
    setQueryError(null);
    setQueryLoading(true);
    try {
      const res = await submitQuery(projectId, queryText);
      setQueryResponse(res);
    } catch (err) {
      setQueryError(err instanceof Error ? err.message : 'Query failed');
    } finally {
      setQueryLoading(false);
    }
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
            <QueryInput onSubmit={handleQuery} loading={queryLoading} />

            {queryError && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4 text-sm text-red-700">
                {queryError}
              </div>
            )}

            {queryResponse && <QueryResponse response={queryResponse} />}
          </div>
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
                      document_a_reference: c.document_a_id,
                      value_a: '',
                      document_b_reference: c.document_b_id,
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
