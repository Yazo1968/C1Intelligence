const statusConfig: Record<string, { label: string; classes: string }> = {
  QUEUED: { label: 'Queued', classes: 'bg-gray-100 text-gray-600 border-gray-200' },
  EXTRACTING: { label: 'Extracting', classes: 'bg-blue-50 text-blue-700 border-blue-200' },
  CLASSIFYING: { label: 'Classifying', classes: 'bg-purple-50 text-purple-700 border-purple-200' },
  STORED: { label: 'Stored', classes: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  FAILED: { label: 'Failed', classes: 'bg-red-50 text-red-700 border-red-200' },
};

export function DocumentStatusBadge({ status }: { status: string }) {
  const config = statusConfig[status] ?? statusConfig.QUEUED;
  return (
    <span className={`inline-flex items-center px-2 py-0.5 text-xs font-medium rounded border ${config.classes}`}>
      {config.label}
    </span>
  );
}
