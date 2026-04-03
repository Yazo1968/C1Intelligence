import { useState } from 'react';
import type { Round0Assessment } from '../../api/queries';

const DOMAIN_LABELS: Record<string, string> = {
  legal_contractual: 'Legal & Contractual',
  commercial_financial: 'Commercial & Financial',
  financial_reporting: 'Financial & Reporting',
};

const RELEVANCE_BADGE: Record<string, string> = {
  PRIMARY: 'bg-navy-700 text-white',
  RELEVANT: 'bg-amber-100 text-amber-800',
  NOT_APPLICABLE: 'bg-gray-100 text-gray-400',
};

interface Round0CardProps {
  assessment: Round0Assessment;
  onRunAnalysis: (domains: string[]) => void;
  onRunAll: () => void;
  loading: boolean;
}

export function Round0Card({
  assessment,
  onRunAnalysis,
  onRunAll,
  loading,
}: Round0CardProps) {
  const [selected, setSelected] = useState<Set<string>>(
    new Set(assessment.default_domains)
  );

  const toggle = (domain: string, relevance: string) => {
    if (relevance === 'NOT_APPLICABLE') return;
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(domain)) {
        next.delete(domain);
      } else {
        next.add(domain);
      }
      return next;
    });
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5 space-y-4">
      {/* Brief */}
      <div>
        <p className="text-sm font-semibold text-navy-900 mb-1">Initial Assessment</p>
        <p className="text-sm text-gray-700">{assessment.executive_brief}</p>
      </div>

      {/* Documents retrieved */}
      {assessment.documents_retrieved.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
            Documents retrieved ({assessment.documents_retrieved.length})
          </p>
          <div className="flex flex-wrap gap-1">
            {assessment.documents_retrieved.map((doc) => (
              <span
                key={doc}
                className="inline-block bg-gray-50 border border-gray-200 rounded px-2 py-0.5 text-xs text-gray-600 truncate max-w-xs"
                title={doc}
              >
                {doc}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Domain grid */}
      <div>
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
          Select domains to analyse
        </p>
        <div className="space-y-2">
          {assessment.domain_recommendations.map((rec) => {
            const isSelectable = rec.relevance !== 'NOT_APPLICABLE';
            const isSelected = selected.has(rec.domain);
            return (
              <button
                key={rec.domain}
                type="button"
                disabled={!isSelectable || loading}
                onClick={() => toggle(rec.domain, rec.relevance)}
                className={`w-full text-left rounded-md border px-3 py-2 transition-colors ${
                  isSelectable
                    ? isSelected
                      ? 'border-navy-700 bg-navy-50'
                      : 'border-gray-200 hover:border-gray-300'
                    : 'border-gray-100 bg-gray-50 cursor-not-allowed opacity-60'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {isSelectable && (
                      <input
                        type="checkbox"
                        checked={isSelected}
                        readOnly
                        className="h-3.5 w-3.5 rounded border-gray-300 text-navy-700 pointer-events-none"
                      />
                    )}
                    <span className="text-sm font-medium text-navy-900">
                      {DOMAIN_LABELS[rec.domain] ?? rec.domain}
                    </span>
                  </div>
                  <span
                    className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                      RELEVANCE_BADGE[rec.relevance] ?? 'bg-gray-100 text-gray-500'
                    }`}
                  >
                    {rec.relevance.replace('_', ' ')}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-0.5 ml-5">{rec.reason}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex items-center gap-3 pt-1">
        <button
          type="button"
          disabled={selected.size === 0 || loading}
          onClick={() => onRunAnalysis(Array.from(selected))}
          className="px-4 py-2 rounded-md bg-navy-700 text-white text-sm font-medium disabled:opacity-50 hover:bg-navy-800 transition-colors"
        >
          Run Analysis ({selected.size} domain{selected.size !== 1 ? 's' : ''})
        </button>
        <button
          type="button"
          disabled={loading}
          onClick={onRunAll}
          className="px-4 py-2 rounded-md border border-gray-300 text-gray-700 text-sm font-medium disabled:opacity-50 hover:bg-gray-50 transition-colors"
        >
          Run All Domains
        </button>
      </div>
    </div>
  );
}
