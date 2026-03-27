import type { ProjectResponse } from '../../api/types';

interface ProjectCardProps {
  project: ProjectResponse;
  onClick: () => void;
}

export function ProjectCard({ project, onClick }: ProjectCardProps) {
  const created = new Date(project.created_at).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'short', year: 'numeric',
  });

  return (
    <button
      onClick={onClick}
      className="bg-white border border-gray-200 rounded-lg p-5 text-left hover:border-navy-700 hover:shadow-sm transition-all cursor-pointer w-full"
    >
      <h3 className="text-base font-semibold text-navy-900 truncate">{project.name}</h3>
      {project.description && (
        <p className="text-sm text-gray-500 mt-1 line-clamp-2">{project.description}</p>
      )}
      <div className="mt-4 flex items-center gap-3 text-xs text-gray-400">
        <span>Created {created}</span>
        {project.gemini_store_name && <span className="text-emerald-600">Store active</span>}
      </div>
    </button>
  );
}
