export function Spinner({ className = '' }: { className?: string }) {
  return (
    <div className={`animate-spin rounded-full h-5 w-5 border-2 border-gray-300 border-t-navy-900 ${className}`} role="status">
      <span className="sr-only">Loading...</span>
    </div>
  );
}
