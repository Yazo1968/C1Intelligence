import type { Contradiction } from '../../api/types';

export function ContradictionAlert({ contradiction }: { contradiction: Contradiction }) {
  const hasValues = contradiction.value_a || contradiction.value_b;

  return (
    <div className="border-l-4 border-red-500 bg-red-50 rounded-r-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-red-600 text-lg">&#9888;</span>
        <span className="font-semibold text-red-800 text-sm">
          Conflicting Field: {contradiction.field_name}
        </span>
      </div>

      {hasValues && (
        <div className="grid grid-cols-2 gap-4 text-sm mb-2">
          <div className="bg-white rounded-md border border-red-200 p-3">
            <p className="text-xs text-gray-500 mb-1 font-medium">
              {contradiction.document_a_reference || 'Source A'}
            </p>
            <p className="font-semibold text-navy-900">{contradiction.value_a}</p>
          </div>
          <div className="bg-white rounded-md border border-red-200 p-3">
            <p className="text-xs text-gray-500 mb-1 font-medium">
              {contradiction.document_b_reference || 'Source B'}
            </p>
            <p className="font-semibold text-navy-900">{contradiction.value_b}</p>
          </div>
        </div>
      )}

      {!hasValues && (contradiction.document_a_reference || contradiction.document_b_reference) && (
        <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
          <span className="font-medium">{contradiction.document_a_reference}</span>
          {contradiction.document_a_reference && contradiction.document_b_reference && (
            <span>vs</span>
          )}
          <span className="font-medium">{contradiction.document_b_reference}</span>
        </div>
      )}

      {contradiction.description && (
        <p className="text-sm text-red-700">{contradiction.description}</p>
      )}
    </div>
  );
}
