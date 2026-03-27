import type { Confidence } from '../../api/types';

const config: Record<Confidence, { bg: string; icon: string; label: string; description: string }> = {
  GREEN: {
    bg: 'bg-emerald-50 border-emerald-500 text-emerald-800',
    icon: '\u{1F7E2}',
    label: 'Consistent',
    description: 'All retrieved documents agree on the queried information.',
  },
  AMBER: {
    bg: 'bg-amber-50 border-amber-500 text-amber-800',
    icon: '\u{1F7E1}',
    label: 'Partial',
    description: 'Evidence is incomplete or supported by a single source only.',
  },
  RED: {
    bg: 'bg-red-50 border-red-500 text-red-800',
    icon: '\u{1F534}',
    label: 'Contradiction Detected',
    description: 'Documents contain conflicting values for the same field.',
  },
  GREY: {
    bg: 'bg-gray-100 border-gray-400 text-gray-600',
    icon: '\u2B1C',
    label: 'Insufficient Evidence',
    description: 'No relevant documents found in the warehouse.',
  },
};

interface ConfidenceBadgeProps {
  confidence: Confidence;
  size?: 'sm' | 'lg';
}

export function ConfidenceBadge({ confidence, size = 'lg' }: ConfidenceBadgeProps) {
  const c = config[confidence];

  if (size === 'sm') {
    return (
      <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 text-xs font-semibold rounded border ${c.bg}`}>
        <span>{c.icon}</span> {c.label}
      </span>
    );
  }

  return (
    <div className={`rounded-lg border-l-4 px-5 py-4 ${c.bg}`}>
      <div className="flex items-center gap-3">
        <span className="text-2xl">{c.icon}</span>
        <div>
          <p className="text-lg font-semibold">{c.label}</p>
          <p className="text-sm opacity-80">{c.description}</p>
        </div>
      </div>
    </div>
  );
}
