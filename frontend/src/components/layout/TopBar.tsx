import { useAuth } from '../../auth/AuthContext';

interface TopBarProps {
  title: string;
  subtitle?: string;
}

export function TopBar({ title, subtitle }: TopBarProps) {
  const { user, signOut } = useAuth();

  return (
    <header className="h-14 border-b border-gray-200 bg-white flex items-center justify-between px-6 shrink-0">
      <div>
        <h1 className="text-lg font-semibold text-navy-900 leading-tight">{title}</h1>
        {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
      </div>
      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-500">{user?.email}</span>
        <button
          onClick={signOut}
          className="text-sm text-gray-500 hover:text-navy-900 transition-colors cursor-pointer"
        >
          Sign Out
        </button>
      </div>
    </header>
  );
}
