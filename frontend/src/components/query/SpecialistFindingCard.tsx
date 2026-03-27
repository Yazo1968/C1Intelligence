import { CitationInline } from './CitationInline';
import type { SpecialistFinding } from '../../api/types';

const domainLabels: Record<string, string> = {
  legal_contractual: 'Legal & Contractual',
  commercial_financial: 'Commercial & Financial',
  schedule_programme: 'Schedule & Programme',
  technical_design: 'Technical & Design',
  claims_disputes: 'Claims & Disputes',
  governance_compliance: 'Governance & Compliance',
};

export function SpecialistFindingCard({ finding }: { finding: SpecialistFinding }) {
  const domainLabel = domainLabels[finding.domain] ?? finding.domain;

  return (
    <div className="border border-gray-200 rounded-lg bg-white">
      <div className="px-4 py-3 border-b border-gray-100 bg-gray-50 rounded-t-lg">
        <h4 className="text-sm font-semibold text-navy-900">{domainLabel}</h4>
      </div>
      <div className="px-4 py-3 space-y-3">
        <p className="text-sm text-gray-700 leading-relaxed">{finding.analysis}</p>

        {finding.key_findings.length > 0 && (
          <ul className="space-y-2">
            {finding.key_findings.map((kf, i) => (
              <li key={i} className="flex gap-2 text-sm">
                <span className="text-navy-700 mt-0.5 shrink-0">&bull;</span>
                <span className="text-gray-800 leading-relaxed">
                  {kf.statement}
                  {kf.citations.map((c, j) => (
                    <CitationInline key={j} citation={c} />
                  ))}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
