import { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';
import type { SpecialistFinding } from '../../api/types';
import { parseCitations } from './parseCitations';

const domainLabels: Record<string, string> = {
  legal_contractual: 'Legal & Contractual',
  commercial_financial: 'Commercial & Financial',
  schedule_programme: 'Schedule & Programme',
  technical_design: 'Technical & Design',
  claims_disputes: 'Claims & Disputes',
  governance_compliance: 'Governance & Compliance',
};

const PROSE_CLASSES = [
  'prose prose-sm max-w-none text-gray-700',
  'prose-headings:text-navy-900 prose-headings:font-semibold',
  'prose-strong:text-gray-900',
  'prose-ul:my-1 prose-li:my-0.5',
  'prose-table:text-xs prose-th:bg-gray-50 prose-th:font-medium',
  'prose-td:border prose-td:border-gray-200 prose-td:px-2 prose-td:py-1',
].join(' ');

export function SpecialistFindingCard({ finding }: { finding: SpecialistFinding }) {
  const domainLabel = domainLabels[finding.domain] ?? finding.domain;

  const processedMarkdown = useMemo(
    () => parseCitations(finding.findings),
    [finding.findings],
  );

  return (
    <div className="border border-gray-200 rounded-lg bg-white">
      <div className="px-4 py-3 border-b border-gray-100 bg-gray-50 rounded-t-lg">
        <h4 className="text-sm font-semibold text-navy-900">{domainLabel}</h4>
      </div>
      <div className="px-4 py-3">
        <div className={PROSE_CLASSES}>
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeRaw]}
            components={{
              div: ({ className, children, ...props }) =>
                className === 'citation-footnotes' ? (
                  <div className="mt-3 pt-2 border-t border-gray-100 space-y-0.5" {...props}>{children}</div>
                ) : <div {...props}>{children}</div>,
              span: ({ className, children, ...props }) =>
                className === 'citation-label' ? (
                  <span className="text-xs font-medium text-gray-400 uppercase tracking-wider block mb-1" {...props}>{children}</span>
                ) : <span {...props}>{children}</span>,
            }}
          >
            {processedMarkdown}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
