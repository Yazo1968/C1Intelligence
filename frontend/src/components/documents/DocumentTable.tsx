import { DocumentStatusBadge } from './DocumentStatusBadge';
import { EmptyState } from '../ui/EmptyState';
import type { DocumentResponse } from '../../api/types';

interface DocumentTableProps {
  documents: DocumentResponse[];
  loading: boolean;
}

export function DocumentTable({ documents, loading }: DocumentTableProps) {
  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-6 w-6 border-2 border-gray-300 border-t-navy-900" /></div>;
  }

  if (documents.length === 0) {
    return <EmptyState title="No documents" description="Upload your first document to get started." />;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 text-left">
            <th className="pb-2 pr-4 font-medium text-gray-500 text-xs uppercase tracking-wider">Filename</th>
            <th className="pb-2 pr-4 font-medium text-gray-500 text-xs uppercase tracking-wider">Type</th>
            <th className="pb-2 pr-4 font-medium text-gray-500 text-xs uppercase tracking-wider">Category</th>
            <th className="pb-2 pr-4 font-medium text-gray-500 text-xs uppercase tracking-wider">Tier</th>
            <th className="pb-2 pr-4 font-medium text-gray-500 text-xs uppercase tracking-wider">Status</th>
            <th className="pb-2 pr-4 font-medium text-gray-500 text-xs uppercase tracking-wider">Date</th>
            <th className="pb-2 font-medium text-gray-500 text-xs uppercase tracking-wider">Reference</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {documents.map((doc) => (
            <tr key={doc.id} className="hover:bg-gray-50 transition-colors">
              <td className="py-2.5 pr-4">
                <span className="font-medium text-navy-900 truncate block max-w-[200px]" title={doc.filename}>
                  {doc.filename}
                </span>
              </td>
              <td className="py-2.5 pr-4 text-gray-700">{doc.document_type_name ?? '—'}</td>
              <td className="py-2.5 pr-4 text-gray-500">{doc.category ?? '—'}</td>
              <td className="py-2.5 pr-4">
                {doc.tier ? (
                  <span className={`inline-flex items-center justify-center w-6 h-6 rounded text-xs font-bold ${
                    doc.tier === 1 ? 'bg-navy-900 text-white' : doc.tier === 2 ? 'bg-navy-900/20 text-navy-900' : 'bg-gray-100 text-gray-500'
                  }`}>
                    {doc.tier}
                  </span>
                ) : '—'}
              </td>
              <td className="py-2.5 pr-4"><DocumentStatusBadge status={doc.status} /></td>
              <td className="py-2.5 pr-4 text-gray-500 whitespace-nowrap">
                {doc.document_date ? new Date(doc.document_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'}
              </td>
              <td className="py-2.5 text-gray-500 font-mono text-xs">{doc.document_reference_number ?? '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
