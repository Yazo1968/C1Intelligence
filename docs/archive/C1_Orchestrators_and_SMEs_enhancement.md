# C1 Intelligence — Orchestrators and SMEs Enhancement Plan

**Version:** 2.3
**Date:** April 2026
**Status:** Active
**Author:** Strategic Partner (Claude) — based on independent expert examination
**Approved by:** Yasser Darweesh

---

## Context

This plan records all issues identified during an expert examination of the
C1 Intelligence orchestrator directives and SME skill files (26 files total:
3 orchestrators + 23 SMEs across Legal, Claims, Schedule, Technical, and
Compliance domains), together with a strategic architectural restructure
recommended as a consequence of that examination.

The plan is structured in two parts:

- **Part A** — Targeted remediation of all 8 issues identified in the expert
  examination. All fixes are applied to files in their current locations
  before any structural change occurs.
- **Part B** — Architectural restructure: dissolution of the Claims SME as a
  standalone domain and redistribution of its skills — and the backend code
  that routes to them — into the domains where they analytically belong.
- **Part C** — Assessment quality improvements to two Delay and Cost Analytics
  SME skills, ensuring the delay assessment output is forensically complete
  for boards, dispute panels, and forensic experts.
- **Part D** — Three new Financial SME skill files covering project finance
  assessment: cost control adequacy, contingency management, and lender/funder
  compliance. These skills are drafted by the Strategic Partner (Claude chat),
  not Claude Code, for the reasons stated in the Part D section.

Parts A, B, C, and D form a single coherent execution sequence. Part A must be
complete before Part B begins. Parts C and D execute after Part B is
structurally settled. The governing documents (CLAUDE.md, C1_MASTER_PLAN.md)
are updated last, after all parts are complete. Several Part A tasks were
revised from their original form to avoid creating content that Part B would
immediately supersede.

**Total tasks: 29. Total commits: 29 (one per task, with one approved
exception noted at A6.1).**

---

## Governing Rules

- One task per commit. Push immediately after Quality Guardian PASS.
- No task begins without Yasser's approval.
- Strategic partner verifies every output independently via GitHub API
  before confirming PASS.
- All skill file edits must comply with `skills/c1-skill-authoring/SKILL.md`.
- `BUILD_LOG.md` updated at session close.
- `docs/C1_MASTER_PLAN.md` updated when any phase or task status changes.

---

## Part A — Expert Examination Remediation

### Issue Index

| # | Issue | Severity | Tasks | Revision note |
|---|---|---|---|---|
| A1 | Retired engineer_identification references active in 4 SME files | Critical | A1.1–A1.4 | Unchanged |
| A2 | Notice compliance skill duplication and routing ambiguity | Significant | A2.1 only | A2.2 absorbed into B5 — orchestrators rewritten in full during Part B |
| A3 | Commercial orchestrator directive missing H1 title | Significant | A3.1 | Unchanged |
| A4 | Claims README is stale placeholder text | Significant | A4.1 | Revised — minimal fix only; full retirement handled in B4 |
| A5 | No cross-orchestrator synthesis mechanism | Moderate | A5.1 | Unchanged |
| A6 | Confidence scale not self-documented in SME files | Moderate | A6.1 | 23-file commit — approved exception; see note below |
| A7 | statutory_authority_mapping invocation undeclared | Minor | A7.1 | Unchanged |
| A8 | EVM skill missing fallback path | Minor | A8.1 | Unchanged |

**A6.1 exception note:** Task A6.1 touches 23 files in a single commit. This
is an approved exception to the one-task-per-commit rule. The change is purely
mechanical — identical one-line insertion in the output format section of each
file — with no logic changes. Splitting into 23 commits would produce no
additional safety. QG verifies all 23 files before PASS is confirmed.
Additionally, A6.1 must execute before Part B Tasks B2 and B3, so that the
confidence scale fix travels with the claims files when they are moved.

---

### A1 — Retired engineer_identification References (Critical)

**Problem:** Four SME skill files instruct the agent to read
`engineer_identification` findings to obtain the contract administrator
identity and notice routing. That skill is retired. An agent following these
instructions attempts to read findings from a skill that no longer exists,
breaking the pipeline or proceeding with an unconfirmed contract administrator
identity — infecting every downstream notice routing, instruction authority,
and time bar assessment.

**Correct reference:** `party_and_role_identification.md` for contract
administrator identity. `compliance_investigation.md` for authority
confirmation. The Compliance SME owns all party and role identification
as of Phase 6.

---

#### Task A1.1 — Fix `notice_and_instruction_compliance.md`

**File:** `skills/smes/legal/notice_and_instruction_compliance.md`

**Changes required:**

1. **"Before you begin / Foundational requirements"** — replace:
   > Read contract_assembly and engineer_identification findings first.
   >
   > From engineer_identification extract:
   > - Identity of the contract administrator
   > - Notice routing — which entity receives which category of notice
   > - Split-role pattern (if any)

   With:
   > Read contract_assembly findings first. Contract administrator identity
   > and notice routing are established by the Compliance SME
   > (`party_and_role_identification.md`). Read those findings before
   > proceeding if governance has been established; if not, flag that
   > notice routing compliance cannot be confirmed.
   >
   > From party_and_role_identification findings extract:
   > - Identity of the contract administrator
   > - Notice routing — which entity receives which category of notice
   > - Split-role pattern (if any)

2. **Step 1(d) "Notice recipient"** — replace *"From engineer_identification
   findings"* with *"From party_and_role_identification findings"*.

3. **Classification / "Recipient routing"** — replace any remaining instance
   of "engineer_identification findings" with
   "party_and_role_identification findings".

**Commit:** `fix: notice_and_instruction_compliance — replace retired engineer_identification references`

**QG criteria:** Zero instances of "engineer_identification" remain.
party_and_role_identification cited correctly as source for contract
administrator identity. Governing footer intact.

---

#### Task A1.2 — Fix `entitlement_basis.md`

**File:** `skills/smes/legal/entitlement_basis.md`

**Change:** In Step 6, replace *"(from engineer_identification findings)"*
with:
> (from party_and_role_identification findings — who held the contract
> administrator role on the determination date)

**Commit:** `fix: entitlement_basis — replace retired engineer_identification reference in Step 6`

**QG criteria:** Zero instances of "engineer_identification" remain.
Governing footer intact.

---

#### Task A1.3 — Fix `key_dates_and_securities.md`

**File:** `skills/smes/legal/key_dates_and_securities.md`

**Change:** In "Before you begin / Foundational requirements", replace:
> From engineer_identification:
> - Identity of the contract administrator — relevant to who issued the
>   completion certificate and defects certificate.

With:
> From party_and_role_identification findings:
> - Identity of the contract administrator — relevant to who issued the
>   completion certificate and defects certificate.

**Commit:** `fix: key_dates_and_securities — replace retired engineer_identification reference`

**QG criteria:** Zero instances of "engineer_identification" remain.
Governing footer intact.

---

#### Task A1.4 — Fix `programme_assessment.md`

**File:** `skills/smes/schedule/programme_assessment.md`

**Change:** In "Before you begin / Foundational requirements", replace:
> Contract administrator identity (from engineer_identification findings)

With:
> Contract administrator identity (from party_and_role_identification
> findings — the Compliance SME owns all party and role identification)

**Commit:** `fix: programme_assessment — replace retired engineer_identification reference`

**QG criteria:** Zero instances of "engineer_identification" remain.
Governing footer intact.

---

### A2 — Notice Compliance Skill Duplication (Significant)

**Problem:** Two skills cover overlapping notice compliance territory with
no stated boundary, creating routing ambiguity. The architectural boundary:

- `notice_and_instruction_compliance.md` (Legal SME) — general validity of
  notices and instructions as a contractual matter, assessed independently
  of any specific claim entitlement
- `notice_compliance.md` (Claims SME, moving to Legal SME in Part B) —
  notice compliance as a procedural gateway to claim entitlement

Task A2.2 (updating the Legal orchestrator delegation table) is absorbed into
Task B5. The orchestrator is rewritten in full during Part B — writing a
routing note now that references a Claims SME that Part B dissolves would
create content immediately superseded.

---

#### Task A2.1 — Clarify boundary in both notice skill files

**Files:**
- `skills/smes/legal/notice_and_instruction_compliance.md`
- `skills/smes/claims/notice_compliance.md`

**Change in legal SME file** — update "When to apply this skill" to open with:
> This skill governs the formal validity of notices and instructions as a
> contractual matter, assessed independently of any specific claim
> entitlement. Apply for variation instructions, suspension notices,
> termination notices, and any communication whose validity depends on
> form, timing, or routing. For notice compliance specifically as a
> procedural gateway to claim entitlement (EOT, prolongation cost,
> disruption, dispute resolution), route to `notice_compliance.md`.

**Change in claims SME file** — update "When to apply this skill" to open with:
> This skill governs notice compliance as a procedural gateway to claim
> entitlement — whether the prerequisites for a specific EOT, prolongation
> cost, disruption, or dispute resolution claim have been satisfied. For
> general validity of notices and instructions assessed independently of a
> specific claim entitlement, route to
> `notice_and_instruction_compliance.md`.

**Commit:** `fix: clarify notice compliance skill boundary — legal vs claims domain`

**QG criteria:** Both files open "When to apply" with an explicit routing
boundary. Governing footers intact.

---

### A3 — Commercial Orchestrator Missing H1 Title (Significant)

**Problem:** `skills/orchestrators/commercial/directive.md` opens with
`## Role`. No H1 title. Inconsistent with the other orchestrators.

---

#### Task A3.1 — Add H1 title to commercial orchestrator directive

**File:** `skills/orchestrators/commercial/directive.md`

**Change:** Insert at the very top of the file, before `## Role`:
```
# Commercial & Financial Orchestrator — Directive
```

**Commit:** `fix: commercial orchestrator directive — add missing H1 title`

**QG criteria:** File opens with `# Commercial & Financial Orchestrator —
Directive`. No other content changed. Governing footer intact.

---

### A4 — Claims README Stale Placeholder (Significant)

**Revised scope:** Minimal fix only — remove stale development scaffolding.
Full directory retirement is Task B4.

---

#### Task A4.1 — Minimal fix to claims README

**File:** `skills/smes/claims/README.md`

**Replace entire content with:**

```markdown
# Claims & Disputes — SME Skills

This directory contains five SME skill files. Directory structure is
pending architectural restructure — see the Enhancement Plan
(docs/C1_Orchestrators_and_SMEs_enhancement.md Part B).

## Skills currently in this directory

- `dispute_resolution_procedure.md`
- `disruption.md`
- `eot_quantification.md`
- `notice_compliance.md`
- `prolongation_cost.md`
```

**Commit:** `fix: claims README — remove stale placeholder, note pending restructure`

**QG criteria:** No reference to "AGENT_PLAN.md" or "Phase 3" remains.
No claims about permanent directory structure.

---

### A5 — No Cross-Orchestrator Synthesis Mechanism (Moderate)

**Problem:** When two or more Tier 1 orchestrators are invoked for the same
query, there is no documented mechanism for assembling a single integrated
board-level finding.

---

#### Task A5.1 — Create multi-orchestrator synthesis directive

**File:** `skills/orchestrators/synthesis_directive.md` (new file)

**Full content:**

```markdown
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

### 7. Consolidated FLAGS

Merge all FLAGS from all orchestrators into a single list. Remove
duplicates. Where a FLAG from one orchestrator is amplified by a FLAG
from another, combine them and state the joint effect in one sentence.

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
```

**Commit:** `feat: add multi-orchestrator synthesis directive`

**QG criteria:** File exists at `skills/orchestrators/synthesis_directive.md`.
All eight assembly sections present. Confidence aggregation rule (most
conservative) stated. Governing footer present.

---

### A6 — Confidence Scale Not Self-Documented in SME Files (Moderate)

**Problem:** Every SME output format uses GREEN / AMBER / RED / GREY
confidence classification but none defines what these levels mean.

**Approved exception:** 23 files in one commit. Mechanical repetitive change.
Must execute before B2 and B3 so the fix travels with moving files.

---

#### Task A6.1 — Add confidence scale reference to all SME output format sections

**Files:** All 23 SME skill files (listed below). Also check the four
compliance sub-skills not in the 23 and update where they carry a confidence
output section.

**Change in each file:** In the output format section, immediately before or
after the `Confidence: [GREEN / AMBER / RED / GREY]` line, insert:

```
*(Confidence scale: GREEN = all required evidence retrieved and findings
fully supported | AMBER = Layer 2b not retrieved or amendment position
unknown — findings provisional | RED = critical document absent —
findings materially constrained | GREY = standard form unconfirmed —
form-specific analysis suspended. Full definition:
skills/c1-skill-authoring/references/grounding_protocol.md)*
```

**Files:**
- `skills/smes/legal/contract_assembly.md`
- `skills/smes/legal/entitlement_basis.md`
- `skills/smes/legal/key_dates_and_securities.md`
- `skills/smes/legal/notice_and_instruction_compliance.md`
- `skills/smes/claims/dispute_resolution_procedure.md`
- `skills/smes/claims/disruption.md`
- `skills/smes/claims/eot_quantification.md`
- `skills/smes/claims/notice_compliance.md`
- `skills/smes/claims/prolongation_cost.md`
- `skills/smes/schedule/acceleration.md`
- `skills/smes/schedule/critical_path_analysis.md`
- `skills/smes/schedule/delay_identification.md`
- `skills/smes/schedule/evm_and_cost_reporting.md`
- `skills/smes/schedule/programme_assessment.md`
- `skills/smes/schedule/time_at_large.md`
- `skills/smes/technical/design_liability.md`
- `skills/smes/technical/ncr_management.md`
- `skills/smes/technical/rfi_and_submittal_review.md`
- `skills/smes/technical/site_execution.md`
- `skills/smes/technical/specification_compliance.md`
- `skills/smes/technical/testing_and_commissioning.md`
- `skills/smes/compliance/compliance_investigation.md`
- `skills/smes/compliance/doa_compliance.md`

Also check and update where applicable:
- `skills/smes/compliance/governance_establishment.md`
- `skills/smes/compliance/party_and_role_identification.md`
- `skills/smes/compliance/signatory_validation.md`
- `skills/smes/compliance/statutory_authority_mapping.md`

**Commit:** `fix: all SME files — add confidence scale reference to output format sections`

**QG criteria:** All applicable files contain the confidence scale inline
definition. Definition is identical across all files. No other content
changed. All governing footers intact.

---

### A7 — statutory_authority_mapping Invocation Gap (Minor)

**Problem:** `statutory_authority_mapping.md` declares it is invoked at
governance establishment Step 5, but `governance_establishment.md` does
not instruct the agent to call it.

---

#### Task A7.1 — Add explicit invocation in governance_establishment

**File:** `skills/smes/compliance/governance_establishment.md`

**Change:** Locate the step covering statutory authority identification.
Add an explicit invocation instruction:

> **Invoke `statutory_authority_mapping.md` at this step.** That skill
> retrieves all statutory authorities with jurisdiction over this project,
> maps required interactions to project milestones, and identifies which
> permits, NOCs, and approvals are documented in the warehouse. Its output
> feeds into the governance event log — statutory approvals are a distinct
> category of authority event alongside contractual party appointments.

**Commit:** `fix: governance_establishment — explicit invocation of statutory_authority_mapping`

**QG criteria:** `governance_establishment.md` explicitly names and invokes
`statutory_authority_mapping.md` at the statutory authority step. No other
content changed. Governing footer intact.

---

### A8 — EVM Skill Missing Fallback Path (Minor)

**Problem:** When no EVM report is in the warehouse, the skill stops at
CANNOT ASSESS for every metric, even though budget documents and payment
certificates may be present and can support a partial assessment.

---

#### Task A8.1 — Add fallback assessment path to evm_and_cost_reporting

**File:** `skills/smes/schedule/evm_and_cost_reporting.md`

**Change:** After the primary EVM extraction workflow, add:

```markdown
### Fallback — No EVM Reports in Warehouse

If no EVM report has been retrieved after exhausting tool searches, and
budget documents, payment certificates, or progress reports with financial
data ARE retrieved — proceed with a partial financial performance assessment
using only those documents. Do not calculate EVM metrics.

Extract from retrieved budget documents:
- Approved budget (BAC equivalent): state value and source
- Budget breakdown by cost category: state from retrieved documents

Extract from retrieved payment certificates and cost reports:
- Actual cost to date (AC equivalent): state value and source
- Certified amount to date: state value and source

Extract from retrieved progress reports:
- Percentage complete as reported: state value, report date, and source

State explicitly:
> No formal EVM report was found in the warehouse. This assessment is
> derived from budget, payment, and progress documents only. EVM metrics
> (CPI, SPI, EAC, ETC, VAC) cannot be extracted — they have not been
> reported in the retrieved documents.

Flag: EVM REPORTING NOT FOUND IN WAREHOUSE — list which financial
documents were retrieved. Set confidence to AMBER.

Do not produce SPI, CPI, EAC, ETC, or VAC values under the fallback
path. These are extracted metrics — if not in retrieved documents,
they are not available.
```

**Commit:** `fix: evm_and_cost_reporting — add fallback path when no EVM reports in warehouse`

**QG criteria:** Fallback section present and clearly labelled. EVM metric
calculation explicitly prohibited. Confidence set to AMBER. Flag instruction
included. Governing footer intact.

---

## Part B — Architectural Restructure: Dissolution of the Claims SME Domain

### The Problem

The Claims SME as currently structured mixes two categorically different
types of skill:

**Analytical skills** — continuous with the programme and delay analysis
work of the Schedule SME:
- EOT Quantification (delay methodology and critical path output)
- Prolongation Cost (cost translation of a confirmed time extension)
- Disruption (productivity loss measurement — measured mile, site records)

**Procedural skills** — legal procedural assessments already invoked by
the Legal orchestrator:
- Notice Compliance (procedural gateway to claim entitlement)
- Dispute Resolution Procedure (legal escalation pathway)

The current domain boundary sits in the middle of a continuous analytical
chain with no analytical justification. A delay analyst works continuously
from programme assessment through EOT quantification and prolongation cost
as a single exercise — the domain boundary fragments this without purpose.

### The Resolution

**Dissolve the Claims SME as a standalone domain.**

| Skill | Current location | New location |
|---|---|---|
| EOT Quantification | Claims SME | Delay and Cost Analytics SME |
| Prolongation Cost | Claims SME | Delay and Cost Analytics SME |
| Disruption | Claims SME | Delay and Cost Analytics SME |
| Notice Compliance | Claims SME | Legal SME |
| Dispute Resolution Procedure | Claims SME | Legal SME |

**Rename the Schedule SME** to **Delay and Cost Analytics SME**. Directory
name `skills/smes/schedule/` is retained to preserve git history. Only the
domain label in skill file headers and all code/orchestrator references
changes.

### Backend Architecture Affected

The domain routing stack has four layers — all must be updated. Failure to
update the code while restructuring the skill files produces a
production-breaking state where claims-related queries route to an empty
domain:

```
prompts.py       → ALL_DOMAINS + domain router system prompt
      ↓
orchestrator.py  → DOMAIN_TO_CONFIG_KEY mapping
      ↓
specialist_config.py → SPECIALIST_CONFIGS
      ↓
skill_loader.py  → loads files from skills/smes/{domain}/
```

### Broken Window Rule

Tasks B2, B3, B4, and B5 must be executed back-to-back in a single session
with no other work interleaved. Between B2/B3 (files moved) and B5
(orchestrators updated), the orchestrators reference a Claims SME with no
skills at its old location. This is an acceptable transient state only if it
is resolved within the same session. Similarly, the code tasks B_code1,
B_code2, and B_code3 must follow B5 without interruption.

---

### Task B1 — Update domain label in existing Schedule SME skill file headers

**Files:** All 6 skills currently in `skills/smes/schedule/`
- `acceleration.md`
- `critical_path_analysis.md`
- `delay_identification.md`
- `evm_and_cost_reporting.md`
- `programme_assessment.md`
- `time_at_large.md`

**Change in each file:**

Replace: `**Domain:** Schedule & Programme SME`
With: `**Domain:** Delay and Cost Analytics SME`

No analytical content changes.

**Commit:** `feat: schedule SME skills — update domain label to Delay and Cost Analytics SME`

**QG criteria:** All 6 files carry the updated domain label. No analytical
content changed. Governing footers intact.

---

### Task B2 — Move EOT Quantification, Prolongation Cost, Disruption

**From:** `skills/smes/claims/`
**To:** `skills/smes/schedule/`
**Files:** `eot_quantification.md`, `prolongation_cost.md`, `disruption.md`
**Method:** `git mv` for each file to preserve history.

**Content changes in each moved file:**
1. Domain label: replace `**Domain:** Claims & Disputes SME`
   with `**Domain:** Delay and Cost Analytics SME`
2. "Invoked by": update to include all three orchestrators where applicable.

No analytical content changes.

**Commit:** `feat: move eot_quantification, prolongation_cost, disruption to Delay and Cost Analytics SME`

**QG criteria:**
- All three files present at `skills/smes/schedule/`
- All three files absent from `skills/smes/claims/`
- Domain label updated in all three
- Git history preserved — verify with `git log --follow -- skills/smes/schedule/eot_quantification.md`
- No analytical content changed. Governing footers intact.

---

### Task B3 — Move Notice Compliance and Dispute Resolution Procedure

**From:** `skills/smes/claims/`
**To:** `skills/smes/legal/`
**Files:** `notice_compliance.md`, `dispute_resolution_procedure.md`
**Method:** `git mv` for each file to preserve history.

**Content changes in each moved file:**
1. Domain label: replace `**Domain:** Claims & Disputes SME`
   with `**Domain:** Legal & Contractual SME`
2. "Invoked by": update to be consistent with Legal SME conventions.

The routing boundary clarification from Task A2.1 (already applied to
`notice_compliance.md`) travels with the file.

**Commit:** `feat: move notice_compliance and dispute_resolution_procedure to Legal SME`

**QG criteria:**
- Both files present at `skills/smes/legal/`
- Both files absent from `skills/smes/claims/`
- Domain label updated in both
- Git history preserved — verify with `git log --follow`
- No analytical content changed. Governing footers intact.

---

### Task B4 — Retire the Claims SME directory

After B2 and B3, `skills/smes/claims/` contains only `README.md` and
`grounding_schema.json`. The grounding schema is addressed in B_schema.
The directory is retired with a redirect README.

**File:** `skills/smes/claims/README.md`

**Replace entire content with:**

```markdown
# Claims & Disputes — RETIRED DOMAIN

**Status:** Retired
**Retired in:** Enhancement Plan Part B (April 2026)

## What happened to the skills in this directory

The Claims & Disputes SME domain has been dissolved. Its five skill files
have been redistributed to the domains where they analytically belong.

| Skill | New location |
|---|---|
| `eot_quantification.md` | `skills/smes/schedule/` — Delay and Cost Analytics SME |
| `prolongation_cost.md` | `skills/smes/schedule/` — Delay and Cost Analytics SME |
| `disruption.md` | `skills/smes/schedule/` — Delay and Cost Analytics SME |
| `notice_compliance.md` | `skills/smes/legal/` — Legal SME |
| `dispute_resolution_procedure.md` | `skills/smes/legal/` — Legal SME |

## Why

EOT quantification, prolongation cost, and disruption are analytically
continuous with the programme and delay analysis work of the Schedule SME.
Placing a domain boundary between critical path analysis and EOT
quantification interrupted a single analytical chain with no analytical
justification. These three skills now complete the Delay and Cost Analytics
SME chain:

Programme Assessment → Delay Identification → Critical Path Analysis
→ EOT Quantification → Prolongation Cost → Disruption

Notice compliance and dispute resolution procedure are procedural legal
skills already invoked by the Legal orchestrator. They now sit with the
other Legal SME skills where they belong.
```

**Commit:** `feat: retire claims SME directory — redirect README to new skill locations`

**QG criteria:** README accurately describes all five skill new locations.
All claims skills confirmed absent from this directory.

---

### Task B_schema — Update grounding schemas

**Problem:** `skills/smes/claims/grounding_schema.json` is now orphaned in
the retired directory. `skills/smes/schedule/grounding_schema.json` needs
its description updated to reflect the enlarged domain scope.

**File 1: `skills/smes/claims/grounding_schema.json`** — delete this file.
The claims domain is retired. No agent will load from this directory.

**File 2: `skills/smes/schedule/grounding_schema.json`** — update the
`skill_group` and `description` fields:

```json
{
  "skill_group": "delay_and_cost_analytics_sme",
  "layer2b_required": true,
  "layer2a_required": false,
  "layer1_amendment_document_required": true,
  "confidence_cap_without_layer2b": "AMBER",
  "confidence_cap_without_amendment_document": "GREY",
  "description": "Delay and Cost Analytics SMEs require Layer 2b standard form provisions before characterising time extension mechanisms, agreed damages, programme obligations, entitlement bases for EOT and cost claims, or dispute procedures. Amendment document required for project-specific dates, rates, periods, and entitlement event lists."
}
```

**Commit:** `feat: update grounding schemas — retire claims schema, update schedule schema for enlarged scope`

**QG criteria:**
- `skills/smes/claims/grounding_schema.json` deleted
- `skills/smes/schedule/grounding_schema.json` has updated `skill_group`
  and `description` reflecting the enlarged domain
- Other grounding schemas (legal, compliance, technical, orchestrators)
  unchanged

---

### Task B5 — Update all three orchestrator directives

This task absorbs the original Task A2.2. The orchestrator directives are
updated in full to reflect the new domain structure. All "Claims SME"
references are removed. The new domain structure is written in once,
correctly, after all file moves are confirmed.

**Files:**
- `skills/orchestrators/legal/directive.md`
- `skills/orchestrators/commercial/directive.md`
- `skills/orchestrators/financial/directive.md`

---

**Legal orchestrator — changes:**

1. Remove the "Claims SMEs" subsection from SME Delegation Authority.

2. Add Notice Compliance and Dispute Resolution Procedure as Legal SME
   skills in the delegation table, with their own invocation triggers.

3. Add a Delay and Cost Analytics SME subsection for queries with a
   legal entitlement dimension requiring EOT quantification, prolongation
   cost, or disruption assessment.

4. Add the notice skill routing boundary (absorbing A2.2):
   > For general validity of notices and instructions assessed independently
   > of a specific claim entitlement (variation instructions, suspension,
   > termination) — invoke `notice_and_instruction_compliance.md`.
   > For notice compliance as a gateway to a specific claim entitlement
   > (EOT, prolongation cost, disruption) — invoke `notice_compliance.md`.

Updated Legal SME delegation (7 skills):
- Contract Assembly SME
- Entitlement Basis SME
- Notice and Instruction Compliance SME — general notice/instruction validity
- Key Dates and Securities SME
- Notice Compliance SME — claim entitlement gateway
- Dispute Resolution Procedure SME — escalation pathway
- Delay and Cost Analytics SME — for EOT, prolongation, disruption with
  a legal entitlement dimension

---

**Commercial orchestrator — changes:**

1. Replace all "Claims & Disputes SME" references with
   "Delay and Cost Analytics SME".

2. Update invocation triggers: EOT quantification, prolongation cost, and
   disruption quantum route to Delay and Cost Analytics SME.

3. Remove all references to "Claims SME".

---

**Financial orchestrator — changes:**

1. Replace all "Claims & Disputes SME" references with
   "Delay and Cost Analytics SME".

2. Claims exposure (EOT cost, prolongation, disruption) routes to
   Delay and Cost Analytics SME.

3. Remove all references to "Claims SME".

---

**Commit:** `feat: update all orchestrator directives — Delay and Cost Analytics SME, Legal SME absorbs claims skills`

**QG criteria:**
- Zero references to "Claims SME" or "Claims & Disputes SME" in any
  orchestrator directive
- Legal orchestrator lists 7 skills with notice boundary routing note
- Commercial and Financial orchestrators reference Delay and Cost Analytics
  SME for EOT/prolongation/disruption
- All governing footers intact

---

### Task B_code1 — Update `specialist_config.py`

**File:** `src/agents/specialist_config.py`

**Problem:** `SPECIALIST_CONFIGS` still contains `"claims"` as a domain
entry. After Part B, `skills/smes/claims/` has no skill files. Any query
routed to the claims domain will load an empty skill set.

**Change:** Remove the claims entry from `SPECIALIST_CONFIGS`:

```python
# Remove this entry:
"claims": SpecialistConfig(domain="claims", tier=2, round_assignment=2, max_tool_rounds=3),
```

No other entries change. The `"schedule"` entry remains — it covers the
enlarged Delay and Cost Analytics SME directory.

**Commit:** `fix: specialist_config — remove retired claims domain entry`

**QG criteria:** `SPECIALIST_CONFIGS` contains no `"claims"` key.
`"schedule"`, `"legal"`, `"commercial"`, `"financial"`, `"technical"`,
and `"compliance"` entries remain unchanged.

---

### Task B_code2 — Update `prompts.py`

**File:** `src/agents/prompts.py`

**Problem:** Three issues in this file:

1. `DOMAIN_CLAIMS_DISPUTES = "claims_disputes"` — constant still live
2. `ALL_DOMAINS` still includes `"claims_disputes"` — the domain router
   will route queries there; the skill_loader will find no skills
3. The domain router system prompt describes `claims_disputes` as covering
   EOT, prolongation, disruption, notices, and dispute procedures — all of
   which now live in `schedule_programme` and `legal_contractual`

**Changes required:**

1. Remove the line: `DOMAIN_CLAIMS_DISPUTES = "claims_disputes"`

2. Remove `"claims_disputes"` from `ALL_DOMAINS`.

3. Update the `schedule_programme` domain description in the domain router
   system prompt to include:
   - Extension of time (EOT) claims and delay analysis
   - Prolongation and time-related cost claims
   - Disruption claims, productivity analysis, measured mile assessment
   - Acceleration costs (directed and constructive)
   *(These were previously listed under `claims_disputes`.)*

4. Update the `legal_contractual` domain description to include:
   - Notice compliance as a gateway to claim entitlement (time bar,
     form, awareness date)
   - Dispute resolution procedure assessment (adjudication, dispute
     board, arbitration escalation)
   *(These were previously listed under `claims_disputes`.)*

5. Remove the `claims_disputes` entry from the domain description block
   in the system prompt entirely.

6. Update the example in the system prompt that references `claims_disputes`
   (currently: *"A delay claim query engages: claims_disputes...
   schedule_programme..."*) — rewrite to reflect that all delay and claim
   content now routes to `schedule_programme` and `legal_contractual`.

**Commit:** `fix: prompts.py — remove claims_disputes domain, redistribute to schedule_programme and legal_contractual`

**QG criteria:**
- Zero instances of `"claims_disputes"` or `DOMAIN_CLAIMS_DISPUTES` remain
- `ALL_DOMAINS` does not contain `"claims_disputes"`
- `schedule_programme` description covers EOT, prolongation, disruption
- `legal_contractual` description covers notice compliance and dispute
  resolution procedure
- Domain count in ALL_DOMAINS reduced by 1 (was 6, now 5)

---

### Task B_code3 — Update `orchestrator.py`

**File:** `src/agents/orchestrator.py`

**Problem:** Three references to `"claims_disputes"` remain:

1. `DOMAIN_TO_CONFIG_KEY` maps `"claims_disputes"` → `"claims"` — must
   be removed; any query returning `"claims_disputes"` from the domain
   router would otherwise attempt to load an empty domain
2. Line 486 (approximate): fallback message for `"claims_disputes"` —
   must be removed
3. Comment on Tier 2 SMEs (line ~234): *"Tier 2 SMEs (claims, schedule,
   technical)"* — update to remove "claims"

**Changes required:**

1. Remove from `DOMAIN_TO_CONFIG_KEY`:
   ```python
   "claims_disputes": "claims",
   ```

2. Remove from the fallback messages dict:
   ```python
   "claims_disputes": "No notice documents, EOT claims, or dispute correspondence found in the warehouse.",
   ```

3. Update the Tier 2 SME comment from:
   > Tier 2 SMEs (claims, schedule, technical) are invoked on-demand...
   
   To:
   > Tier 2 SMEs (schedule, technical, compliance) are invoked on-demand...

**Commit:** `fix: orchestrator.py — remove claims_disputes routing, update Tier 2 SME references`

**QG criteria:**
- Zero instances of `"claims_disputes"` or `"claims"` remain in
  `DOMAIN_TO_CONFIG_KEY` and fallback messages
- Tier 2 SME comment no longer references claims
- `DOMAIN_TO_CONFIG_KEY` maps the remaining 5 domains correctly

---

### Task B6 — Update CLAUDE.md

**File:** `CLAUDE.md`

**Changes in the Architecture section:**

Replace the current skill count and domain description with:

> **Skill files:** 3 orchestrator directives + 1 synthesis directive +
> 23 SME skill files = 27 files total.
>
> **Domains:** Legal SME (7 skills), Delay and Cost Analytics SME (9 skills),
> Technical SME (6 skills), Compliance SME (6 skills).
>
> Claims SME domain dissolved — 3 analytical skills moved to Delay and Cost
> Analytics SME; 2 procedural skills moved to Legal SME.
> `synthesis_directive.md` governs multi-orchestrator query assembly.
> `engineer_identification.md` retired.
> All files require the Evidence Declaration block in their output format.

Update the three-tier architecture description to reference the Delay and
Cost Analytics SME by its new name and remove all references to the
Claims SME.

Update the `DOMAIN_TO_CONFIG_KEY` locked decision entry to reflect the
removal of `claims_disputes`.

**Commit:** `docs: CLAUDE.md — update architecture for Enhancement Plan restructure`

**QG criteria:** CLAUDE.md accurately reflects 27 files, 5 active domains,
new domain names, dissolved Claims SME, and addition of synthesis_directive.md.

---

### Task B7 — Update C1_MASTER_PLAN.md

**File:** `docs/C1_MASTER_PLAN.md`

**Changes:**

1. Add a post-Phase 6 section titled "Enhancement Plan" recording this
   workstream as complete, with a reference to the Enhancement Plan document.

2. Add all files changed, moved, created, or deleted across Part A and Part B
   to the Files Affected table with their final status and commit references.

**Commit:** `docs: C1_MASTER_PLAN.md — record Enhancement Plan as completed workstream`

**QG criteria:** Master plan accurately reflects all Enhancement Plan changes.
All 29 tasks documented with commit references.

---

## Backlog Item (not in this plan — separate future task)

**`skill_loader._generate_project_context()` FIDIC hardcoding:**
The method queries the `contracts` table for `fidic_edition` and builds a
FIDIC-specific context block. This is a pre-existing form-specific reference
in form-agnostic code. It does not affect the Enhancement Plan and should not
be addressed here, but must be resolved in a future session before C1 is used
on non-FIDIC projects. Record in BUILD_LOG.md as a known backlog item.

---

## Part C — Assessment Quality: Delay Analysis Methodology and Classification

### Context

C1 does not conduct delay analysis — it assesses submitted delay analysis.
The distinction is the same as between drafting a contract and auditing one:
the assessor does not produce the document, but must know precisely what a
sound document looks like to identify where the submission falls short.

Two targeted improvements are needed to ensure the delay assessment is
forensically complete for the platform's target audience — boards, lenders,
auditors, and dispute resolution professionals:

1. The current methodology assessment step identifies what methodology was
   used and whether its data requirements were met. It does not assess whether
   the methodology was the **right choice** for the project conditions — which
   is the critical auditor judgment. An assessor must be able to state: "You
   used Impacted As-Planned on a complex project with concurrent events. That
   methodology cannot isolate causation here. A more appropriate methodology
   given the available records would have been TIA."

2. The current delay classification uses contractual risk allocation
   terminology (Employer Risk Event / Neutral Event / Contractor Risk Event).
   Boards, dispute panels, and forensic experts use the four-way forensic
   classification (Excusable Compensable / Excusable Non-Compensable /
   Non-Excusable / Concurrent). The platform must output both, bridged
   explicitly. The forensic classification is not a replacement — it is the
   industry-standard label for the same finding expressed in terms the
   target audience uses.

Both are targeted edits to two existing skill files. No new skills. No
restructure. No code changes.

---

### Task C1 — Add methodology appropriateness assessment to `eot_quantification.md`

**File:** `skills/smes/schedule/eot_quantification.md`

**Changes required:**

1. **Step 5 — Assess the delay analysis methodology**: after the per-methodology
   data requirement assessment blocks, add a methodology appropriateness
   sub-step that applies regardless of which methodology was identified:

   > **Assess methodology appropriateness for project conditions:**
   >
   > After confirming whether data requirements are met, assess whether the
   > methodology was appropriate for this project — not just whether it was
   > applied. Assess against the following factors from the retrieved documents:
   >
   > *Concurrent delay:* If the retrieved records evidence concurrent delay
   > events, assess whether the chosen methodology can isolate causation between
   > them. As-Planned vs As-Built and Impacted As-Planned cannot isolate
   > causation where concurrent events are present. Flag this directly and state
   > what methodology would have been more appropriate given the retrieved records.
   >
   > *Record quality:* Assess whether the project's retrievable records are
   > consistent with the requirements of the chosen methodology. A methodology
   > requiring frequent programme updates cannot be properly applied if only
   > the baseline programme is in the warehouse.
   >
   > *Project complexity:* If the retrieved documents indicate a complex project
   > — multiple concurrent events, overlapping critical paths, or significant
   > programme revisions — assess whether the chosen methodology is appropriate
   > for that complexity.
   >
   > State the appropriateness finding explicitly:
   > "[Methodology] is [APPROPRIATE / NOT APPROPRIATE] for the project
   > conditions evidenced in the retrieved documents."
   > If not appropriate: "A more appropriate methodology given the available
   > records would have been [X] because [specific reason from retrieved
   > documents]."

2. **Named methodology list**: add As-Built Critical Path as a named methodology
   alongside the existing five:

   > *As-Built Critical Path:* reconstructs a schedule exclusively from actual
   > progress records to identify the real critical path as executed — not the
   > planned or submitted path. Requires comprehensive as-built data from site
   > diaries, progress reports, and record drawings. From retrieved documents:
   > verify whether the as-built data in the warehouse is sufficient in detail
   > and completeness to support this reconstruction, and whether the claimed
   > critical path reflects the actual construction sequence evidenced in
   > retrieved records.

**Commit:** `fix: eot_quantification — add methodology appropriateness assessment and As-Built Critical Path`

**QG criteria:** Step 5 contains the methodology appropriateness sub-step
after the per-methodology blocks. All five original methodologies plus
As-Built Critical Path named. Appropriateness output explicitly required
(APPROPRIATE / NOT APPROPRIATE) with reasoning. Governing footer intact.

---

### Task C2 — Add forensic four-way classification to `delay_identification.md`

**File:** `skills/smes/schedule/delay_identification.md`

**Changes required:**

1. **Step 4** (currently "Assess excusable vs compensable distinction"):
   expand to formally establish the four-way forensic classification alongside
   the existing contractual classification, bridging the two explicitly:

   > **Four-way forensic classification** (alongside contractual classification):
   >
   > The four-way forensic classification is the standard used by dispute panels,
   > arbitrators, and forensic experts. Apply it to each event alongside the
   > contractual classification and bridge them explicitly — the forensic
   > classification is the industry-standard label for the same finding:
   >
   > — **Excusable Compensable:** event caused by an employer risk event under
   > the retrieved amendment document; entitles the contractor to both time
   > extension and cost. Contractual equivalent: Employer Risk Event.
   >
   > — **Excusable Non-Compensable:** event caused by a neutral event (force
   > majeure, adverse weather, or equivalent neutral category under the retrieved
   > amendment document); entitles the contractor to time extension but not cost.
   > Contractual equivalent: Neutral Event.
   >
   > — **Non-Excusable:** event caused by or attributable to the contractor;
   > no entitlement to time extension or cost. Contractual equivalent:
   > Contractor Risk Event.
   >
   > — **Concurrent:** employer-caused and contractor-caused delays overlap on
   > the critical path during the same period; entitlement depends on governing
   > law, contract terms, and the concurrent delay principles retrieved from
   > Layer 2b. This is a distinct classification — not a sub-category of the
   > others.
   >
   > Do not apply the forensic classification without first establishing the
   > contractual classification from the retrieved amendment document. The
   > forensic classification is derived from the contractual classification —
   > never applied independently.

2. **Delay Event Register** in the output format: add a Forensic classification
   column. Replace the current register header and example row:

   ```
   | # | Event description | Period | Duration | Contemporaneous evidence | Classification | Entitlement | Source |
   | 1 | [description] | [dates] | [days] | [EVIDENCED / NOT VERIFIED] | [ER/Neutral/CR/CANNOT CLASSIFY] | [Time+Cost / Time only / Nil / CANNOT CONFIRM] | [docs] |
   ```

   With:

   ```
   | # | Event description | Period | Duration | Contemporaneous evidence | Contractual classification | Forensic classification | Entitlement | Source |
   | 1 | [description] | [dates] | [days] | [EVIDENCED / NOT VERIFIED] | [ER/Neutral/CR/CANNOT CLASSIFY] | [Ex.Comp / Ex.Non-Comp / Non-Ex / Concurrent / CANNOT CLASSIFY] | [Time+Cost / Time only / Nil / CANNOT CONFIRM] | [docs] |
   ```

3. **Findings by Delay Event**: add a Forensic classification line after the
   existing Classification line:

   > Forensic classification: [EXCUSABLE COMPENSABLE / EXCUSABLE NON-COMPENSABLE /
   > NON-EXCUSABLE / CONCURRENT / CANNOT CLASSIFY]
   > Forensic classification basis: [derived from contractual classification /
   > CANNOT CLASSIFY — contractual classification not established]

**Commit:** `fix: delay_identification — add forensic four-way classification alongside contractual classification`

**QG criteria:** Step 4 formally establishes the four-way forensic
classification bridged to the contractual classification. Delay Event Register
has the Forensic classification column. Findings by Delay Event includes the
forensic classification line with CANNOT CLASSIFY fallback. All four
categories defined with their contractual equivalents. Governing footer intact.

---

## Part D — Financial SME Skills (New Domain)

### Context

The Financial & Reporting Orchestrator operates as a financial reporting
reader — it extracts metrics from retrieved documents and flags discrepancies.
That level of analysis is correct for the platform's purpose.

However, three areas material to the platform's primary audience (lenders,
boards, auditors, investors) are not covered anywhere in the current
architecture:

**1. Cost control adequacy and cost-at-completion credibility**
The Financial orchestrator extracts the EAC from retrieved EVM reports. It
does not assess whether that EAC is credible — whether the cost-to-complete
estimate is realistic given actual burn rate, committed-but-not-yet-incurred
costs, open variations, and remaining scope. An auditor does not just read the
EAC; they challenge it. That challenge capability is absent.

**2. Contingency management**
Contingency drawdown appears as a line item in the financial risk exposure
section of the orchestrator's output. There is no structured assessment of
whether drawdown is being governed responsibly, whether remaining contingency
is adequate relative to known and probable risks, or whether the contingency
governance framework is functioning.

**3. Lender and funder compliance**
The Financial orchestrator mentions lender and investor reporting as a scope
item but coverage is surface level — extract reported metrics, flag
discrepancies with underlying records. Financial covenant compliance,
drawdown condition evidencing, and LTA (Lender's Technical Advisor) reporting
obligation fulfilment are entirely absent. These are the specific instruments
lenders use and the platform's output quality standard names lenders as a
primary audience.

None of this overlaps with existing coverage. The Commercial orchestrator
handles the commercial position; the Financial orchestrator handles financial
performance reporting; the Compliance SME handles internal DOA compliance.
The three gaps above are genuinely unaddressed.

### Resolution

Add three Financial SME skill files under a new `skills/smes/financial/`
directory. The Financial orchestrator delegates to these SMEs for queries
with a financial controls, contingency, or lender compliance dimension —
following the same delegation pattern as the Legal orchestrator delegates to
its Legal SMEs.

A `grounding_schema.json` is created for the new domain. Code wiring
(specialist_config.py update for the new financial SME domain entry) is
addressed in Task D5.

### Execution model — Strategic Partner drafts, Claude Code commits

**Part D tasks are not executed by Claude Code from a specification.**
They are executed by the Strategic Partner (Claude chat) at execution time.

**Reason:** These are new skill files requiring nuanced domain authorship —
construction project finance, cost management standards, lender/funder
frameworks. The Strategic Partner reads the c1-skill-authoring references,
applies construction finance domain knowledge, and drafts each skill file in
full. Claude Code, executing from a task description alone, would produce
lower-quality skill content for a specialist domain of this complexity.

**Protocol for each Part D task:**
1. Strategic Partner reads `skills/c1-skill-authoring/SKILL.md` and all
   four reference files (`grounding_protocol.md`, `warehouse_retrieval.md`,
   `output_formats.md`, `validation_scenarios.md`)
2. Strategic Partner drafts the complete skill file content in the chat
   session and writes the file to the cloned repo using `bash_tool`
3. Strategic Partner confirms compliance with all four authoring principles
   before producing the commit prompt
4. Claude Code executes a minimal prompt: `git add [file] && git commit -m
   "[message]" && git push` — no authoring judgment required

Yasser approves each completed draft before the commit prompt is executed.
QG PASS is confirmed by Strategic Partner via GitHub API before moving to
the next task.

---

### Task D1 — Draft and create `cost_control_assessment.md`

**File:** `skills/smes/financial/cost_control_assessment.md` (new file)
**Author:** Strategic Partner (Claude chat)
**Skill type:** Mixed
- Contract-type-agnostic: the assessment framework for cost control
  adequacy, EAC credibility, and cost reporting quality applies regardless
  of contract form
- Contract-type-specific: the cost reporting obligations and format
  requirements differ by contract and Layer 2b standard; the contractual
  definition of cost governs what is recoverable

**Scope of assessment (to be built into the skill):**
- WBS and cost coding structure — is the cost breakdown adequate to
  support meaningful cost control and reporting?
- Committed vs incurred vs forecast — does the cost report distinguish
  between committed costs (contracted but not yet paid), incurred costs
  (paid), and forecast costs (estimated to complete)?
- EAC and cost-to-complete credibility — does the forecast completion cost
  reflect the actual burn rate, open variations, known risks, and remaining
  scope — or is it a carry-forward of the original budget?
- Cost report frequency and recency — is the cost reporting current?
- Variance explanation — are significant variances from budget explained
  with specific, retrieved source documents?
- CANNOT CONFIRM rules — if cost reports are absent or incomplete, state
  which assessments cannot be made and what documents are missing

**Invoked by:** Financial orchestrator
**Layer dependency:** Layer 1 (cost reports, budget documents, payment
certificates, variation orders); Layer 2a (internal financial reporting
policies if ingested); Layer 2b (applicable financial standards if ingested)

**Commit:** `feat: add cost_control_assessment SME skill — Financial domain`

**QG criteria:** Full skill structure per c1-skill-authoring/SKILL.md.
Evidence Declaration in output format. CANNOT CONFIRM rules present.
Governing footer present. No hardcoded figures or contract-form assumptions.

---

### Task D2 — Draft and create `contingency_management_assessment.md`

**File:** `skills/smes/financial/contingency_management_assessment.md`
(new file)
**Author:** Strategic Partner (Claude chat)
**Skill type:** Contract-type-agnostic
The framework for assessing contingency management applies regardless of
contract form. The contractual provisions governing contingency authority
are retrieved from Layer 2a (internal DOA) and Layer 2b.

**Scope of assessment (to be built into the skill):**
- Contingency baseline — what was the approved contingency allowance and
  what is its source document?
- Drawdown history — what has been drawn against contingency, for what
  reasons, approved by whom? Is the drawdown consistent with the DOA
  framework retrieved from Layer 2a?
- Remaining contingency adequacy — does the remaining contingency balance
  appear adequate relative to the known risks in retrieved risk register
  documents and open variations? State as an observation from retrieved
  documents — do not calculate risk-weighted exposure
- Governance — are contingency drawdowns being approved at the correct
  authority level under the retrieved DOA framework? This links to the
  Compliance SME (doa_compliance.md) for any specific transaction requiring
  authority confirmation
- Trend assessment — is the drawdown rate accelerating? State from
  retrieved documents only
- CANNOT CONFIRM rules — if risk register or DOA framework not retrieved,
  state which assessments are affected

**Invoked by:** Financial orchestrator
**Layer dependency:** Layer 1 (contingency drawdown records, risk register,
cost reports); Layer 2a (DOA framework, contingency governance policy);
Layer 2b (applicable standards if ingested)

**Commit:** `feat: add contingency_management_assessment SME skill — Financial domain`

**QG criteria:** Full skill structure per c1-skill-authoring/SKILL.md.
Evidence Declaration in output format. Explicit link to Compliance SME
for DOA authority confirmation. CANNOT CONFIRM rules present.
Governing footer present.

---

### Task D3 — Draft and create `lender_and_funder_compliance.md`

**File:** `skills/smes/financial/lender_and_funder_compliance.md` (new file)
**Author:** Strategic Partner (Claude chat)
**Skill type:** Contract-type-agnostic for the assessment framework;
contract-type-specific for the contractual reporting obligations

**Scope of assessment (to be built into the skill):**
- Lender/funder identification — identify from retrieved documents which
  lenders or funders have monitoring rights over this project and under
  what instrument
- LTA reporting obligations — what does the financing agreement require
  in terms of LTA reports: frequency, content, sign-off requirements?
  Retrieve from Layer 1 financing documents
- LTA report status — have the required LTA reports been produced at the
  required frequency? Retrieve and assess from the warehouse
- Financial covenant compliance — identify the financial covenants from
  retrieved financing documents (e.g. debt service cover ratio, loan-to-
  value, completion date covenant). For each covenant: state the threshold
  from retrieved documents, state the project's current position from
  retrieved financial data, assess compliance. CANNOT CONFIRM if covenant
  terms or current financial data not retrieved
- Drawdown conditions — for projects with staged drawdowns, assess whether
  the conditions for the next drawdown are evidenced in the retrieved
  documents (practical completion certificate, insurance confirmation,
  technical approval)
- Reporting discrepancies — flag any discrepancy between what is reported
  to lenders in retrieved LTA or investor reports and what the underlying
  project records show
- CANNOT CONFIRM rules — financing agreements and LTA terms may not be
  in the warehouse; state clearly what cannot be assessed and what documents
  would be needed

**Invoked by:** Financial orchestrator
**Layer dependency:** Layer 1 (financing agreements, LTA reports, covenant
compliance certificates, drawdown notices, completion certificates);
Layer 2a (internal financial reporting policies); Layer 2b (applicable
financial reporting standards if ingested)

**Commit:** `feat: add lender_and_funder_compliance SME skill — Financial domain`

**QG criteria:** Full skill structure per c1-skill-authoring/SKILL.md.
Evidence Declaration in output format. Covenant assessment explicitly
requires retrieved threshold values — no assumed thresholds.
CANNOT CONFIRM rules present. Governing footer present.

---

### Task D4 — Create `grounding_schema.json` for Financial SME domain

**File:** `skills/smes/financial/grounding_schema.json` (new file)
**Author:** Strategic Partner (Claude chat)

**Content:**
```json
{
  "skill_group": "financial_sme",
  "layer2b_required": false,
  "layer2a_required": true,
  "layer1_amendment_document_required": false,
  "confidence_cap_without_layer2a": "AMBER",
  "description": "Financial SMEs require Layer 2a internal policies and DOA
  frameworks before assessing contingency governance or authority compliance.
  Layer 1 cost reports, financing agreements, and LTA reports are the primary
  evidence base. Layer 2b financial reporting standards improve assessment
  quality when ingested but are not required to proceed."
}
```

**Note:** `layer2a_required: true` is the distinguishing characteristic of
this schema. Unlike the Legal, Schedule, and Technical SMEs which require
Layer 2b standard form provisions, the Financial SMEs depend primarily on
Layer 2a internal policies (DOA framework, financial reporting policies)
for governance compliance assessments.

**Commit:** `feat: add grounding_schema.json for Financial SME domain`

**QG criteria:** Valid JSON. `layer2a_required: true` correctly set.
Description accurately reflects the three Financial SME skills.

---

### Task D5 — Code wiring for Financial SME domain

**File:** `src/agents/specialist_config.py`
**Author:** Claude Code (standard task — no authoring judgment required)

**Change required:**

Add a Financial SME entry to `SPECIALIST_CONFIGS`:

```python
"financial_sme": SpecialistConfig(
    domain="financial_sme",
    tier=2,
    round_assignment=2,
    max_tool_rounds=3
),
```

This loads skills from `skills/smes/financial/` (the skill_loader will find
no `orchestrators/financial_sme/` directory and fall through to `smes/
financial_sme/` — note: directory must be named `financial_sme` to match,
OR the directory stays as `financial` and a legacy path is used).

**Implementation note:** At execution time, the Strategic Partner will
confirm the exact directory naming and loading path before issuing this
task to Claude Code. The domain name in specialist_config must match
the directory name used for the skill files. If the files are placed at
`skills/smes/financial/`, the domain key must be `"financial"` — but this
conflicts with the existing Tier 1 `"financial"` entry. The resolution
(separate directory name `financial_sme`, or merging into the orchestrator
directory) will be confirmed at that point.

Also update the Financial orchestrator directive (`skills/orchestrators/
financial/directive.md`) to add a Financial SME delegation section,
specifying when to invoke each of the three new skills.

**Commit:** `feat: code wiring for Financial SME domain — specialist_config and orchestrator directive`

**QG criteria:** Financial SME domain loadable. Skill_loader confirmed to
find the three skill files. Financial orchestrator directive contains
delegation instructions for all three skills.

---

## Complete Execution Sequence

29 tasks in execution order. Each requires Yasser's approval before starting.
Each requires QG PASS before the next begins. **Tasks B2–B_code3 must execute
in a single uninterrupted session (see Broken Window Rule). Part D tasks are
executed by Strategic Partner — see Part D execution model.**

| Order | Task | File(s) | Executor | Type | Notes |
|---|---|---|---|---|---|
| 1 | A1.1 | notice_and_instruction_compliance.md | Claude Code | Fix | Critical — broken reference |
| 2 | A1.2 | entitlement_basis.md | Claude Code | Fix | Critical — broken reference |
| 3 | A1.3 | key_dates_and_securities.md | Claude Code | Fix | Critical — broken reference |
| 4 | A1.4 | programme_assessment.md | Claude Code | Fix | Critical — broken reference |
| 5 | A3.1 | commercial/directive.md | Claude Code | Fix | Structural — quick |
| 6 | A4.1 | claims/README.md | Claude Code | Fix | Minimal — retirement in B4 |
| 7 | A2.1 | notice_and_instruction_compliance.md + notice_compliance.md | Claude Code | Fix | Must precede B3 move |
| 8 | A7.1 | governance_establishment.md | Claude Code | Fix | Independent |
| 9 | A8.1 | evm_and_cost_reporting.md | Claude Code | Fix | Independent |
| 10 | A6.1 | All 23 SME files | Claude Code | Fix | Approved exception — must precede B2/B3 |
| 11 | A5.1 | synthesis_directive.md | Claude Code | Create | New file — Part A complete |
| 12 | B1 | 6 schedule skill headers | Claude Code | Update | Rename domain before files arrive |
| 13 | B2 | eot_quantification, prolongation_cost, disruption | Claude Code | Move | git mv — BEGIN broken window session |
| 14 | B3 | notice_compliance, dispute_resolution_procedure | Claude Code | Move | git mv |
| 15 | B4 | claims/README.md | Claude Code | Retire | After moves confirmed |
| 16 | B_schema | claims + schedule grounding_schema.json | Claude Code | Update/Delete | — |
| 17 | B5 | All 3 orchestrator directives | Claude Code | Update | After all moves confirmed; absorbs A2.2 |
| 18 | B_code1 | specialist_config.py | Claude Code | Fix | Remove claims entry |
| 19 | B_code2 | prompts.py | Claude Code | Fix | Remove claims_disputes from ALL_DOMAINS and router prompt |
| 20 | B_code3 | orchestrator.py | Claude Code | Fix | Remove claims routing — END broken window session |
| 21 | C1 | eot_quantification.md | Claude Code | Fix | Methodology appropriateness + As-Built Critical Path |
| 22 | C2 | delay_identification.md | Claude Code | Fix | Forensic four-way classification |
| 23 | D1 | cost_control_assessment.md | Strategic Partner | Create | Full skill draft — SP reads c1-skill-authoring first |
| 24 | D2 | contingency_management_assessment.md | Strategic Partner | Create | Full skill draft |
| 25 | D3 | lender_and_funder_compliance.md | Strategic Partner | Create | Full skill draft |
| 26 | D4 | financial/grounding_schema.json | Strategic Partner | Create | SP drafts, Claude Code commits |
| 27 | D5 | specialist_config.py + financial/directive.md | Claude Code | Fix | Code wiring — loading path confirmed at execution time |
| 28 | B6 | CLAUDE.md | Claude Code | Update | After all parts complete |
| 29 | B7 | docs/C1_MASTER_PLAN.md | Claude Code | Update | Final — closes the workstream |

**Ordering rationale:**
- 1–4: Critical broken references — fix before any Legal domain query runs
- 5–6: Quick structural fixes with no dependencies
- 7: Fixes notice_compliance.md before it moves in task 14
- 8–9: Independent fixes
- 10: Confidence scale applied to claims files before they move (fixes travel with files)
- 11: New file — Part A closes cleanly
- 12: Domain label renamed before incoming files arrive
- 13–20: Single session — file moves, schema, orchestrators, code all resolved without interruption
- 21–22: Part C skill content improvements — structure settled, before governing documents
- 23–27: Part D new Financial SME skills — Strategic Partner drafts in sequence, code wiring last
- 28–29: Governing documents always last — updated with the complete final state of all four parts

---

## End State

After all 29 tasks complete and are verified:

**Skill file inventory (31 files):**
- 3 orchestrator directives + 1 synthesis directive
- Legal SME: 7 skills
- Delay and Cost Analytics SME: 9 skills (complete unbroken chain, forensically complete assessment)
- Technical SME: 6 skills (unchanged)
- Compliance SME: 6 skills (unchanged)
- Financial SME: 3 skills (new domain — cost control, contingency, lender compliance)

**Backend domain routing (5 active domains + 1 new Financial SME domain):**
`legal_contractual` → `legal` | `commercial_financial` → `commercial` |
`financial_reporting` → `financial` | `schedule_programme` → `schedule` |
`technical_construction` → `technical`
(claims_disputes removed from ALL_DOMAINS and DOMAIN_TO_CONFIG_KEY)
Financial SME domain: loaded by Financial orchestrator delegation — not
router-accessible directly.

**Continuous analytical chain — Delay and Cost Analytics SME:**
```
Programme Assessment → Delay Identification → Critical Path Analysis
→ EOT Quantification → Prolongation Cost → Disruption
→ Acceleration / Time at Large / EVM
```
One domain. No artificial boundary.

**Delay assessment quality:**
- `eot_quantification.md`: assesses whether methodology was applied correctly
  AND whether it was the right choice for project conditions. As-Built
  Critical Path included as a named methodology.
- `delay_identification.md`: outputs both contractual classification and the
  standard forensic four-way classification (Excusable Compensable /
  Excusable Non-Compensable / Non-Excusable / Concurrent), bridged explicitly.

**Project finance assessment (new):**
- `cost_control_assessment.md`: EAC credibility, committed vs incurred vs
  forecast cost tracking, cost control system adequacy.
- `contingency_management_assessment.md`: drawdown governance, remaining
  adequacy relative to known risks, DOA compliance link.
- `lender_and_funder_compliance.md`: covenant compliance, drawdown conditions,
  LTA reporting obligations, reported vs actual discrepancies.

**All 8 expert examination issues resolved.**

---

## Document Control

| Field | Value |
|---|---|
| Version | 2.3 |
| Date | April 2026 |
| Status | Active |
| Supersedes | Enhancement Plan v1.0, v2.0, v2.1, v2.2 |
| Location | `docs/C1_Orchestrators_and_SMEs_enhancement.md` |
