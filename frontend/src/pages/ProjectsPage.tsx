import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { ProjectCard } from '../components/projects/ProjectCard';
import { CreateProjectDialog } from '../components/projects/CreateProjectDialog';
import { Button } from '../components/ui/Button';
import { EmptyState } from '../components/ui/EmptyState';
import { Spinner } from '../components/ui/Spinner';
import { listProjects } from '../api/projects';
import type { ProjectResponse } from '../api/types';

export function ProjectsPage() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);

  const fetchProjects = useCallback(async () => {
    try {
      const data = await listProjects();
      setProjects(data);
    } catch {
      // Error handled by API client (401 → redirect)
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchProjects(); }, [fetchProjects]);

  return (
    <AppShell title="Projects">
      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold text-navy-900">Your Projects</h2>
            <p className="text-sm text-gray-500 mt-0.5">{projects.length} project{projects.length !== 1 ? 's' : ''}</p>
          </div>
          <Button onClick={() => setShowCreate(true)}>New Project</Button>
        </div>

        {loading ? (
          <div className="flex justify-center py-16"><Spinner className="h-8 w-8" /></div>
        ) : projects.length === 0 ? (
          <EmptyState
            title="No projects yet"
            description="Create your first project to start uploading documents."
            action={<Button onClick={() => setShowCreate(true)}>New Project</Button>}
          />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.map((p) => (
              <ProjectCard key={p.id} project={p} onClick={() => navigate(`/projects/${p.id}`)} />
            ))}
          </div>
        )}
      </div>

      <CreateProjectDialog
        open={showCreate}
        onClose={() => setShowCreate(false)}
        onCreated={fetchProjects}
      />
    </AppShell>
  );
}
