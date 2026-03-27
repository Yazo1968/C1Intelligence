import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { AuditLogTable } from '../components/audit/AuditLogTable';
import { getQueryLog } from '../api/queries';
import { listProjects } from '../api/projects';
import type { QueryLogEntry, ProjectResponse } from '../api/types';

export function AuditLogPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<ProjectResponse | null>(null);
  const [entries, setEntries] = useState<QueryLogEntry[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    if (!projectId) return;
    try {
      const [logs, projects] = await Promise.all([
        getQueryLog(projectId),
        listProjects(),
      ]);
      setEntries(logs);
      const found = projects.find((p) => p.id === projectId);
      if (found) setProject(found);
    } catch { /* handled by API client */ }
    finally { setLoading(false); }
  }, [projectId]);

  useEffect(() => { fetchData(); }, [fetchData]);

  return (
    <AppShell
      title="Audit Log"
      subtitle={project?.name ? `${project.name} — Immutable query history` : 'Immutable query history'}
      projectName={project?.name}
    >
      <div className="max-w-6xl mx-auto px-6 py-6">
        <div className="mb-4">
          <p className="text-xs text-gray-500 uppercase tracking-wider font-medium">
            Forensic Audit Trail &mdash; {entries.length} quer{entries.length === 1 ? 'y' : 'ies'} recorded
          </p>
        </div>
        <AuditLogTable entries={entries} loading={loading} />
      </div>
    </AppShell>
  );
}
