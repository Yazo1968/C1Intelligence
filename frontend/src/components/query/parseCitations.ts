/**
 * parseCitations — Section-aware citation processing.
 *
 * Splits markdown on ## headings, processes citations independently
 * per section (numbering resets from 1 in each section), and embeds
 * footnote blocks directly after each section's content.
 *
 * Citations are bracketed strings containing document-type keywords
 * (e.g., Contract, FIDIC, Ref., Sub-Clause). Normal markdown links
 * like [text](url) are not matched.
 */

const CITATION_PATTERN =
  /\[([^\]]{10,}(?:Ref\.|Sub-Clause|Clause|Source:|Contract|Agreement|Award|Letter|Schedule|Programme|Report|Notice|Certificate|Conditions|FIDIC|Appendix|Drawing|NCR|RFI|Invoice|Payment)[^\]]*)\]/g;

/**
 * Split markdown into sections on ## headings.
 * Each section includes its heading line and all content until the next heading.
 */
function splitSections(markdown: string): string[] {
  const lines = markdown.split('\n');
  const sections: string[] = [];
  let current: string[] = [];

  for (const line of lines) {
    if (/^#{1,3}\s/.test(line) && current.length > 0) {
      sections.push(current.join('\n'));
      current = [line];
    } else {
      current.push(line);
    }
  }

  if (current.length > 0) {
    sections.push(current.join('\n'));
  }

  return sections;
}

/**
 * Process citations within a single section.
 * Returns the section text with superscripts and an appended footnote block.
 */
function processSection(section: string): string {
  const footnotes: string[] = [];
  const citationToIndex = new Map<string, number>();

  const processed = section.replace(
    CITATION_PATTERN,
    (_match: string, citationText: string) => {
      const trimmed = citationText.trim();

      let index = citationToIndex.get(trimmed);
      if (index === undefined) {
        index = footnotes.length + 1;
        citationToIndex.set(trimmed, index);
        footnotes.push(trimmed);
      }

      return `<sup>${index}</sup>`;
    },
  );

  if (footnotes.length === 0) {
    return processed;
  }

  const footnoteLines = footnotes
    .map((fn, i) => `${i + 1}. ${fn}`)
    .join('\n');

  return `${processed}\n\n<div class="citation-footnotes">\n<span class="citation-label">Sources</span>\n\n${footnoteLines}\n</div>`;
}

export function parseCitations(markdown: string): string {
  if (!markdown) {
    return '';
  }

  const sections = splitSections(markdown);
  return sections.map(processSection).join('\n\n');
}
