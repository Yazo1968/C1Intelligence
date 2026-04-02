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

  const { processedMarkdown, footnotes } = useMemo(
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
          >
            {processedMarkdown}
          </ReactMarkdown>
        </div>

        {footnotes.length > 0 && (
          <div className="mt-4 pt-3 border-t border-gray-100">
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Sources</p>
            <ol className="space-y-1">
              {footnotes.map((fn, i) => (
                <li key={i} className="flex gap-2 text-xs text-gray-400 leading-relaxed">
                  <span className="shrink-0 font-medium">{i + 1}.</span>
                  <span>{fn}</span>
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>
    </div>
  );
}
