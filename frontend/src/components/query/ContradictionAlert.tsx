import type { Contradiction } from '../../api/types';

export function ContradictionAlert({ contradiction }: { contradiction: Contradiction }) {
  return (
    <div className="border-l-4 border-red-500 bg-red-50 rounded-r-lg p-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-red-600 text-lg">&#9888;</span>
        <span className="font-semibold text-red-800 text-sm">
          Conflicting Field: {contradiction.field_name}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="bg-white rounded-md border border-red-200 p-3">
          <p className="text-xs text-gray-500 mb-1 font-medium">Document A</p>
          <p className="font-mono text-xs text-gray-600 mb-1">{contradiction.document_a_reference}</p>
          <p className="font-semibold text-navy-900">{contradiction.value_a}</p>
        </div>
        <div className="bg-white rounded-md border border-red-200 p-3">
          <p className="text-xs text-gray-500 mb-1 font-medium">Document B</p>
          <p className="font-mono text-xs text-gray-600 mb-1">{contradiction.document_b_reference}</p>
          <p className="font-semibold text-navy-900">{contradiction.value_b}</p>
        </div>
      </div>

      {contradiction.description && (
        <p className="mt-3 text-sm text-red-700">{contradiction.description}</p>
      )}
    </div>
  );
}
