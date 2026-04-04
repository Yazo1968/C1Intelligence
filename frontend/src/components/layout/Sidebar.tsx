import { NavLink, useNavigate, useParams } from 'react-router-dom';

const navItems = [
  { label: 'Documents', tab: 'documents' },
  { label: 'Query', tab: 'query' },
  { label: 'Contradictions', tab: 'contradictions' },
  { label: 'Governance', tab: 'governance' },
];

interface SidebarProps {
  projectName?: string;
  activeTab?: string;
  onTabChange?: (tab: string) => void;
}

export function Sidebar({ projectName, activeTab, onTabChange }: SidebarProps) {
  const { projectId } = useParams();
  const navigate = useNavigate();

  const handleTabClick = (tab: string) => {
    if (onTabChange) {
      onTabChange(tab);
    } else if (projectId) {
      // When onTabChange is not available (e.g. on Audit Log page),
      // navigate back to the workspace. The tab will default to 'documents'.
      navigate(`/projects/${projectId}`);
    }
  };

  return (
    <aside className="w-64 bg-navy-900 text-white flex flex-col shrink-0 min-h-screen">
      <div className="p-5 border-b border-white/10">
        <NavLink to="/projects" className="text-lg font-bold tracking-tight hover:text-white/80 transition-colors">
          C1
        </NavLink>
        <p className="text-[10px] uppercase tracking-widest text-white/40 mt-0.5">Intelligence Platform</p>
      </div>

      {projectName && (
        <div className="px-5 py-3 border-b border-white/10">
          <p className="text-xs text-white/50 uppercase tracking-wider">Project</p>
          <p className="text-sm font-medium truncate mt-0.5">{projectName}</p>
        </div>
      )}

      {projectId && (
        <nav className="flex-1 py-3">
          {navItems.map((item) => (
            <button
              key={item.tab}
              onClick={() => handleTabClick(item.tab)}
              className={`w-full text-left px-5 py-2 text-sm transition-colors cursor-pointer ${
                activeTab === item.tab
                  ? 'bg-white/10 text-white font-medium'
                  : 'text-white/60 hover:text-white hover:bg-white/5'
              }`}
            >
              {item.label}
            </button>
          ))}

          <div className="mt-4 pt-4 border-t border-white/10">
            <NavLink
              to={`/projects/${projectId}/audit-log`}
              className={({ isActive }) =>
                `block px-5 py-2 text-sm transition-colors ${
                  isActive ? 'bg-white/10 text-white font-medium' : 'text-white/60 hover:text-white hover:bg-white/5'
                }`
              }
            >
              Audit Log
            </NavLink>
          </div>
        </nav>
      )}

      {!projectId && (
        <nav className="flex-1 py-3">
          <NavLink
            to="/projects"
            className={({ isActive }) =>
              `block px-5 py-2 text-sm transition-colors ${
                isActive ? 'bg-white/10 text-white font-medium' : 'text-white/60 hover:text-white hover:bg-white/5'
              }`
            }
          >
            All Projects
          </NavLink>
        </nav>
      )}
    </aside>
  );
}
