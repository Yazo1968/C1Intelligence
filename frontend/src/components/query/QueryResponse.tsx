import { ConfidenceBadge } from './ConfidenceBadge';
import { SpecialistFindingCard } from './SpecialistFindingCard';
import { ContradictionAlert } from './ContradictionAlert';
import { Badge } from '../ui/Badge';
import type { QueryResponseSchema } from '../../api/types';

const domainLabels: Record<string, string> = {
  legal_contractual: 'Legal & Contractual',
  commercial_financial: 'Commercial & Financial',
  schedule_programme: 'Schedule & Programme',
  technical_design: 'Technical & Design',
  claims_disputes: 'Claims & Disputes',
  governance_compliance: 'Governance & Compliance',
};

export function QueryResponse({ response }: { response: QueryResponseSchema }) {
  return (
    <div className="space-y-5">
      {/* 1. Confidence Banner */}
      <ConfidenceBadge confidence={response.confidence} />

      {/* 2. Domains Engaged */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-xs text-gray-500 font-medium uppercase tracking-wider mr-1">Domains:</span>
        {response.domains_engaged.map((d) => (
          <Badge key={d} color="navy">{domainLabels[d] ?? d}</Badge>
        ))}
      </div>

      {/* 3. Specialist Findings */}
      {response.specialist_findings.length > 0 && (
        <div className="space-y-3">
          {response.specialist_findings.map((f, i) => (
            <SpecialistFindingCard key={i} finding={f} />
          ))}
        </div>
      )}

      {/* 4. Contradictions Section */}
      {response.contradictions.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-red-800 uppercase tracking-wider flex items-center gap-2">
            <span>&#9888;</span> Contradictions Detected
          </h3>
          {response.contradictions.map((c, i) => (
            <ContradictionAlert key={i} contradiction={c} />
          ))}
        </div>
      )}

      {/* 5. Audit Reference */}
      <div className="pt-3 border-t border-gray-200 flex items-center gap-4 text-xs text-gray-400">
        {response.audit_log_id && (
          <span>Audit Log ID: <span className="font-mono">{response.audit_log_id.slice(0, 8)}</span></span>
        )}
        <span>Documents in warehouse: {response.document_ids_at_query_time.length}</span>
      </div>
    </div>
  );
}
