import { useState } from 'react';
import type { Citation } from '../../api/types';

interface CitationInlineProps {
  citation: Citation;
}

export function CitationInline({ citation }: CitationInlineProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  const parts = [
    citation.document_type,
    citation.document_reference,
    citation.document_date,
  ].filter(Boolean);

  const label = parts.length > 0 ? parts.join(' | ') : 'Source';

  return (
    <span className="relative inline-block">
      <span
        className="inline-flex items-center px-1.5 py-0.5 mx-0.5 text-[11px] font-mono font-medium bg-navy-900 text-white rounded cursor-help leading-tight"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        {label}
      </span>
      {showTooltip && citation.excerpt && (
        <span className="absolute bottom-full left-0 mb-2 w-72 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-lg z-50 leading-relaxed">
          <span className="font-semibold block mb-1">Source Excerpt</span>
          {citation.excerpt}
        </span>
      )}
    </span>
  );
}
