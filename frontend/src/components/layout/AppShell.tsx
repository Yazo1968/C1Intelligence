import { TopBar } from './TopBar';
import { Sidebar } from './Sidebar';

interface AppShellProps {
  title: string;
  subtitle?: string;
  projectName?: string;
  activeTab?: string;
  onTabChange?: (tab: string) => void;
  children: React.ReactNode;
}

export function AppShell({ title, subtitle, projectName, activeTab, onTabChange, children }: AppShellProps) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar projectName={projectName} activeTab={activeTab} onTabChange={onTabChange} />
      <div className="flex-1 flex flex-col min-w-0">
        <TopBar title={title} subtitle={subtitle} />
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
