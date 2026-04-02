import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ConfidenceBadge } from '../query/ConfidenceBadge';
import { Badge } from '../ui/Badge';
import { EmptyState } from '../ui/EmptyState';
import type { QueryLogEntry } from '../../api/types';

const domainLabels: Record<string, string> = {
  legal_contractual: 'Legal',
  commercial_financial: 'Commercial',
  schedule_programme: 'Schedule',
  technical_design: 'Technical',
  claims_disputes: 'Claims',
  governance_compliance: 'Governance',
};

export function AuditLogTable({ entries, loading }: { entries: QueryLogEntry[]; loading: boolean }) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-6 w-6 border-2 border-gray-300 border-t-navy-900" /></div>;
  }

  if (entries.length === 0) {
    return <EmptyState title="No queries yet" description="Submit a query from the project workspace to see the audit trail." />;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 text-left">
            <th className="pb-2 pr-4 font-medium text-gray-500 text-xs uppercase tracking-wider">Timestamp</th>
            <th className="pb-2 pr-4 font-medium text-gray-500 text-xs uppercase tracking-wider">Query</th>
            <th className="pb-2 pr-4 font-medium text-gray-500 text-xs uppercase tracking-wider">Confidence</th>
            <th className="pb-2 pr-4 font-medium text-gray-500 text-xs uppercase tracking-wider">Domains</th>
            <th className="pb-2 font-medium text-gray-500 text-xs uppercase tracking-wider">Docs</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {entries.map((entry) => (
            <tr key={entry.id} className="group">
              <td colSpan={5} className="p-0">
                <button
                  onClick={() => setExpandedId(expandedId === entry.id ? null : entry.id)}
                  className="w-full text-left hover:bg-gray-50 transition-colors cursor-pointer"
                >
                  <div className="flex items-center py-2.5">
                    <span className="pr-4 text-gray-500 whitespace-nowrap w-40">
                      {new Date(entry.created_at).toLocaleString('en-GB', {
                        day: 'numeric', month: 'short', year: 'numeric',
                        hour: '2-digit', minute: '2-digit',
                      })}
                    </span>
                    <span className="pr-4 text-navy-900 truncate flex-1">{entry.query_text}</span>
                    <span className="pr-4 shrink-0">
                      <ConfidenceBadge confidence={entry.confidence} size="sm" />
                    </span>
                    <span className="pr-4 shrink-0 flex gap-1 flex-wrap">
                      {entry.domains_engaged?.map((d) => (
                        <Badge key={d} color="gray">{domainLabels[d] ?? d}</Badge>
                      ))}
                    </span>
                    <span className="text-gray-500 shrink-0 w-10 text-center">
                      {entry.document_ids_at_query_time?.length ?? 0}
                    </span>
                  </div>
                </button>

                {expandedId === entry.id && (
                  <div className="px-4 pb-4 bg-gray-50 border-t border-gray-100">
                    <div className="max-w-3xl py-3">
                      <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">Full Response</h4>
                      <div className="prose prose-sm max-w-none text-gray-700 prose-headings:text-navy-900 prose-headings:font-semibold prose-strong:text-gray-900 prose-ul:my-1 prose-li:my-0.5 prose-table:text-xs prose-th:bg-gray-50 prose-th:font-medium prose-td:border prose-td:border-gray-200 prose-td:px-2 prose-td:py-1">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{entry.response_text}</ReactMarkdown>
                      </div>
                      <p className="mt-3 text-xs text-gray-400 font-mono">
                        Audit Log ID: {entry.id}
                      </p>
                    </div>
                  </div>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
