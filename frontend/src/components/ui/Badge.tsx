interface BadgeProps {
  children: React.ReactNode;
  color?: 'navy' | 'gray' | 'green' | 'amber' | 'red';
}

const colors = {
  navy: 'bg-navy-900/10 text-navy-900 border-navy-900/20',
  gray: 'bg-gray-100 text-gray-600 border-gray-200',
  green: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  amber: 'bg-amber-50 text-amber-700 border-amber-200',
  red: 'bg-red-50 text-red-700 border-red-200',
};

export function Badge({ children, color = 'navy' }: BadgeProps) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 text-xs font-medium rounded border ${colors[color]}`}>
      {children}
    </span>
  );
}
