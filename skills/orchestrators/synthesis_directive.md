# Multi-Orchestrator Synthesis Directive

**Governed by:** skills/c1-skill-authoring/SKILL.md
**Invoked by:** Tier 0 router when two or more Tier 1 orchestrators
have been invoked for the same query.

---

## Purpose

When Legal, Commercial, and/or Financial orchestrators all contribute
findings to a single query, their outputs must be assembled into one
integrated assessment. This directive governs that assembly. It does
not replace or modify any orchestrator's output — it defines how they
are presented together and makes all interactions between findings
explicit.

---

## When to apply

Apply when the Tier 0 router has invoked two or more of:
- Legal & Compliance Orchestrator
- Commercial & Financial Orchestrator
- Financial & Reporting Orchestrator

Do not apply for single-orchestrator queries.

---

## Assembly structure

Present the integrated finding in this order:

### 1. Combined Evidence Declaration

Merge all Evidence Declarations from the invoked orchestrators.
List each Layer 2b source once. Consolidate all CANNOT CONFIRM items
across all orchestrators into a single list. Flag any orchestrator
that could not retrieve its required Layer 2b standard.

### 2. Governing Framework

The Legal orchestrator's confirmed standard form and amendment document
status is the governing framework for the integrated assessment.
Commercial and Financial findings are conditional on this framework
being confirmed. If the standard form is UNCONFIRMED: all findings
that depend on a confirmed contractual framework must be flagged as
conditional.

### 3. Legal and Compliance Findings

Present the Legal orchestrator's findings in full, including any
Compliance SME synthesis already performed within that output.

### 4. Commercial Findings

Present the Commercial orchestrator's findings. Where a commercial
finding depends on a legal position, state the dependency explicitly:
> This commercial finding is conditional on the Legal finding that
> [specific legal position]. If that position changes, this commercial
> assessment must be reviewed.

### 5. Financial Findings

Present the Financial orchestrator's findings. Where a financial
figure depends on a commercial or legal position, state the
dependency explicitly.

### 6. Interaction Assessment

State how the findings interact. Address each of the following where
applicable:
- Does any legal finding qualify a commercial position?
- Does any compliance finding challenge a commercial or financial
  assessment?
- Does any financial exposure depend on an unresolved legal or
  commercial matter?
- Are there FLAGS from one orchestrator that compound FLAGS from
  another?

### 7. Consolidated Risk Register

Merge all Risk Register entries from all invoked orchestrators into a
single ISO 31000:2018 compliant risk register. Apply the following rules:

**Ranking:** Present entries in descending order of Inherent Rating —
CRITICAL first, then HIGH, then MEDIUM, then LOW.

**Deduplication:** Where two orchestrators have raised entries describing
the same underlying event, merge them into one entry. State both domain
perspectives in the Description. Take the higher of the two Inherent Ratings.

**Numbering:** Assign sequential IDs across all entries — RISK-001,
RISK-002, RISK-003... regardless of which orchestrator produced the entry.
Prefix the Category with the originating domain where relevant.

**Compound Risk identification:** After listing all entries, identify
where two or more entries interact to produce a joint consequence greater
than either alone. For each compound risk:

COMPOUND: RISK-[ID] + RISK-[ID]
Joint effect: [one sentence — what the combined exposure or consequence is,
from retrieved documents]
Combined Rating: [CRITICAL / HIGH / MEDIUM / LOW — use the higher of the two,
or escalate one level if the interaction materially amplifies the exposure]

**CANNOT ASSESS entries:** Include all entries where Likelihood or Residual
Rating is CANNOT ASSESS. Do not suppress them — an unassessed risk is still
a risk. State clearly what document is missing that prevents the assessment.

**Entry format:** Use the nine-field ISO 31000 format defined in
skills/c1-skill-authoring/references/output_formats.md for every entry.

### 8. Integrated Assessment

Confidence: [most conservative confidence rating across all
orchestrators — never higher than the lowest individual rating]

Summary: [three to five sentences — integrated position only. State
the overall finding and the most material open issues in order of
severity. No orchestrator-specific language. No repetition of
individual findings.]

---

## Output quality standard

Write as a single document produced by a senior multi-disciplinary
team — not as a relay of separate reports. Every interaction between
findings must be explicit. The reader — a board member, lender,
auditor, or dispute panel — receives one coherent assessment, not
three separate reports assembled side by side.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies to
any contract form. All characterisations grounded in retrieved warehouse
documents only.*
