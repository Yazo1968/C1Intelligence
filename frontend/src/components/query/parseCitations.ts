/**
 * parseCitations — Extract bracketed citations from markdown, replace with
 * numbered superscripts, and return a deduplicated footnote list.
 *
 * Citations are bracketed strings containing document-type keywords
 * (e.g., Contract, FIDIC, Ref., Sub-Clause). Normal markdown links
 * like [text](url) are not matched because the regex requires the
 * bracket content to contain a citation keyword.
 */

const CITATION_PATTERN =
  /\[([^\]]{10,}(?:Ref\.|Sub-Clause|Clause|Source:|Contract|Agreement|Award|Letter|Schedule|Programme|Report|Notice|Certificate|Conditions|FIDIC|Appendix|Drawing|NCR|RFI|Invoice|Payment)[^\]]*)\]/g;

export function parseCitations(markdown: string): {
  processedMarkdown: string;
  footnotes: string[];
} {
  if (!markdown) {
    return { processedMarkdown: markdown, footnotes: [] };
  }

  const footnotes: string[] = [];
  const citationToIndex = new Map<string, number>();

  const processedMarkdown = markdown.replace(
    CITATION_PATTERN,
    (_match: string, citationText: string) => {
      const trimmed = citationText.trim();

      // Deduplicate — same citation text gets the same footnote number
      let index = citationToIndex.get(trimmed);
      if (index === undefined) {
        index = footnotes.length + 1;
        citationToIndex.set(trimmed, index);
        footnotes.push(trimmed);
      }

      return `<sup>${index}</sup>`;
    },
  );

  return { processedMarkdown, footnotes };
}
