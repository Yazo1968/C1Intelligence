# C1 Intelligence — Agent Grounding & Epistemic Guardrails Plan

**Version:** 1.0
**Date:** April 2026
**Status:** Approved for execution — this document is the governing reference
**Owner:** Yasser Darweesh (Product Owner)
**Strategic Partner:** Claude (chat session)

---

## Executive Summary

A production query revealed that the Legal orchestrator described a
deleted FIDIC sub-clause using hallucinated content ("Fresh Milk /
Unfulfilled Obligations at Completion") rather than retrieving the
clause text from the Layer 2 reference warehouse. The cross-specialist
contradiction detection correctly flagged the inconsistency — but the
root cause was not caught before output was produced.

The root cause is systemic: the current skill files and orchestrator
directives contain grounding instructions but do not enforce them as
structural constraints. The agents can skip Layer 2 retrieval and
generate plausible-sounding content, and nothing in the current
architecture stops them.

This plan addresses the problem at two levels:

- **Phase 1 — Prompt-level guardrails:** Rebuild all skill files and
  orchestrator directives with a rigorous two-layer grounding protocol
  using the Claude skill-builder tool. Update SKILLS_STANDARDS.md to
  v2.0 as the governing standard.

- **Phase 2 — Code-level enforcement:** Add JSON schema validation
  files alongside each skill and orchestrator directive. Update
  BaseSpecialist and BaseOrchestrator to load these schemas and enforce
  evidence declarations before accepting outputs. Cap confidence
  automatically when required Layer 2 fields are CANNOT_CONFIRM.

Phase 1 reduces the frequency of the problem immediately. Phase 2
makes the enforcement hard and auditable. Both phases are required for
an enterprise-grade platform.

---

## Current State — What Exists

### Architecture overview
- 3 Tier 1 orchestrators: Legal, Commercial, Financial
- 3 Tier 2 SME groups: Claims (5 files), Schedule (6 files), Technical
  (6 files) = 17 SME files
- 3 orchestrator directive files
- 22 skill files total
- SKILLS_STANDARDS.md v1.4 governs authorship
- BaseOrchestrator and BaseSpecialist in Python handle agent execution
- Two-layer warehouse: Layer 1 (project docs) + Layer 2 (FIDIC, laws,
  standards)

### What the current skill files do well
- Clear domain scope definitions
- SME delegation authority defined
- Output structure specified
- Section 6 of SKILLS_STANDARDS.md (warehouse-grounding principles)
  contains the right conceptual framework
- Layer 2 retrieval is mentioned in the Pre-Flight Check of key skills

### What is missing
- **Orchestrator directives have no Layer 2 grounding mandate.** They
  define output structure and scope but do not require the orchestrator
  to retrieve Layer 2 before characterising FIDIC clause amendments.
- **The grounding rule is advisory, not structural.** "Do not
  characterise without Layer 2 retrieval" is an instruction the model
  can skip. There is no output field that makes the skip visible.
- **No mandatory evidence declaration.** The output format does not
  require the agent to explicitly state what was retrieved from Layer 2
  and what was not. Silence about retrieval failure is indistinguishable
  from successful retrieval.
- **No confidence cap logic.** If Layer 2 is not retrieved, the agent
  can still produce a GREEN confidence output. There is no automatic
  downgrade.
- **No runtime validation.** The Python pipeline accepts any text from
  the agent. There is no code-level check that required evidence fields
  have been populated.

---

## What the Skill-Builder Tool Is

The skill-builder (`/mnt/skills/examples/skill-creator/SKILL.md`) is a
meta-skill for creating and improving skill files. It operates as a
structured draft → test → review → improve loop. In Claude.ai (where
this project is managed) it runs inline without subagents.

**What it produces:**
- Markdown skill files with YAML frontmatter (name, description,
  compatibility)
- Structured instruction bodies following the anatomy defined in the
  skill-creator
- Optional bundled resources: scripts (for deterministic tasks),
  references (documentation loaded into context), assets (templates)

**How it is used in this plan:**
The skill-builder is invoked for each skill file and orchestrator
directive rebuild. The strategic partner (Claude chat) uses it to
produce a draft of each rebuilt file, tests the draft against defined
scenarios, reviews the output, and iterates before committing. This is
not a one-shot rewrite — it is a disciplined authorship process for
each file.

**What it cannot produce:**
It cannot produce Python code, JSON schemas, or runtime validation
logic. Phase 2 requires Claude Code for those outputs.

---

## Phase 1 — Prompt-Level Guardrails

**Objective:** Every skill file and orchestrator directive is rebuilt
so that the two-layer grounding protocol is a structural requirement,
not an advisory instruction. The agent cannot produce output about a
FIDIC clause without explicitly declaring whether Layer 2 was retrieved,
and the output format enforces this declaration.

**Agent:** Strategic Partner (Claude chat) using skill-builder tool
**Executor:** Claude Code (commits and pushes)
**Governing document:** SKILLS_STANDARDS.md v2.0 (produced in Task 1.1)
**Commit protocol:** One task per commit after QG PASS

---

### Task 1.1 — Update SKILLS_STANDARDS.md to v2.0

**What:** Rewrite Section 6 (Warehouse-Grounding Principles) and add
a new Section 9 (Mandatory Evidence Declaration Protocol). This becomes
the governing standard before any skill file is touched.

**Why first:** Every skill rebuild in Tasks 1.2–1.4 references the
standard. The standard must be finalised before authorship begins.

**New Section 9 — Mandatory Evidence Declaration Protocol:**

Every skill file must include an Evidence Declaration output block. This
block is mandatory and must appear as the first section of every output.
It is not optional and may not be omitted regardless of the query.

The Evidence Declaration block has the following structure:

```
### Evidence Declaration
Layer 2 retrieved: [YES / NO / PARTIAL]
Layer 2 source: [document name and version, e.g. "FIDIC Yellow Book 1999
  General Conditions" — or NOT RETRIEVED]
Layer 2 clauses retrieved: [list of clause numbers retrieved, or NONE]
Layer 1 primary document: [document name and reference number, or
  NOT RETRIEVED]
Layer 1 Particular Conditions retrieved: [YES / NO / PARTIAL]
```

**Hard rule — no characterisation without retrieval:**

If `Layer 2 retrieved: NO` for a specific clause:
- The clause deletion or amendment must be noted as confirmed from
  Layer 1
- The subject matter and effect of the clause MUST be stated as
  CANNOT CONFIRM — LAYER 2 NOT RETRIEVED
- No description of what the clause covered is permitted
- The confidence for that finding must be capped at AMBER

If `Layer 1 Particular Conditions retrieved: NO`:
- The amendment position for any FIDIC clause is CANNOT CONFIRM
- The agent must not apply Layer 2 standard text as if it governs
  this project
- The confidence for any clause-dependent finding must be capped at GREY

**Addition to Section 6.3 (Layer 1 and Layer 2 Retrieval):**

Add the following hard classification rule:

> For every Particular Conditions amendment to a numbered FIDIC clause,
> the agent MUST perform a Layer 2 retrieval for that clause number
> before characterising its subject matter or effect. The retrieval
> must be recorded in the Evidence Declaration block. If the retrieval
> returns no result, the output for that clause's subject matter is
> CANNOT CONFIRM — LAYER 2 NOT RETRIEVED. The word CANNOT CONFIRM is
> not a failure state — it is the correct forensic output when evidence
> is absent.

**Deliverable:** `docs/SKILLS_STANDARDS.md` v2.0
**Commit:** `docs: SKILLS_STANDARDS.md v2.0 — mandatory evidence declaration protocol`

---

### Task 1.2 — Rebuild Orchestrator Directives (3 files)

**What:** Rebuild all three Tier 1 orchestrator directives using the
skill-builder tool. Each directive currently defines output structure
and scope but contains no Layer 2 grounding mandate.

**Skill-builder process for each file:**
1. Strategic partner reads the current directive and identifies gaps
2. Skill-builder is invoked to draft the rebuilt directive
3. Draft is tested against 3 scenarios (see test scenarios below)
4. Output is reviewed and iterated
5. Final file is committed

**What each rebuilt directive must contain:**

**(a) Layer 2 grounding mandate — added to the Role section:**

> Before characterising the effect of any Particular Conditions
> amendment to a numbered FIDIC clause, you must retrieve that clause
> from Layer 2 using the search_chunks tool. If Layer 2 retrieval
> returns no result for that clause, you must state CANNOT CONFIRM —
> LAYER 2 NOT RETRIEVED for the clause characterisation. You may not
> describe the subject matter of a deleted or amended clause from
> inference or training knowledge.

**(b) Evidence Declaration block — mandatory first section of output:**

Every orchestrator output must begin with the Evidence Declaration block
as defined in SKILLS_STANDARDS.md v2.0 Section 9.

**(c) Layer 2 retrieval trigger — added to Scope of Direct Analysis:**

In the Particular Conditions amendments section, add:

> For each amendment that deletes or substitutes a FIDIC General
> Conditions clause, call search_chunks with the query "[FIDIC book
> name] [edition year] clause [number]" to retrieve the standard text.
> Record the result in the Evidence Declaration block. Do not proceed
> to characterise the amendment's effect without this retrieval.

**Files to rebuild:**
- `skills/orchestrators/legal/directive.md`
- `skills/orchestrators/commercial/directive.md`
- `skills/orchestrators/financial/directive.md`

**Test scenarios for each directive:**

*Scenario A — Layer 2 available:* Query about a Particular Conditions
clause deletion where the clause IS in the Layer 2 warehouse. Agent
must retrieve it, cite it, and correctly characterise the deletion.
Expected output: clause subject matter from Layer 2, FIDIC reference
cited, confidence GREEN or AMBER.

*Scenario B — Layer 2 not retrievable:* Query about a Particular
Conditions clause deletion where retrieval returns no result. Agent
must state CANNOT CONFIRM — LAYER 2 NOT RETRIEVED. Expected output: no
clause description, CANNOT CONFIRM stated, confidence capped at AMBER.

*Scenario C — Particular Conditions not retrieved:* Query where Layer 1
Particular Conditions are absent from the warehouse. Agent must not
apply Layer 2 defaults. Expected output: CANNOT CONFIRM for all
clause-dependent analysis, GREY confidence.

**Commits:** One per directive file after QG PASS
- `feat: rebuild legal orchestrator directive — Layer 2 grounding mandate`
- `feat: rebuild commercial orchestrator directive — Layer 2 grounding mandate`
- `feat: rebuild financial orchestrator directive — Layer 2 grounding mandate`

---

### Task 1.3 — Rebuild SME Skill Files (17 files)

**What:** Rebuild all 17 SME skill files using the skill-builder tool.
The rebuild adds the Evidence Declaration block and the mandatory Layer 2
retrieval requirement to every file. Files that already have strong
grounding instructions (e.g. contract_assembly.md) receive targeted
strengthening. Files with weaker instructions receive more extensive
rebuilds.

**Skill-builder process:** Same as Task 1.2 — draft, test (5 scenarios
per file per SKILLS_STANDARDS.md Section 8.5), review, iterate, commit.

**Rebuild priority order:**

Priority 1 — Legal SMEs (highest forensic sensitivity, most FIDIC
clause references):
1. `skills/smes/legal/contract_assembly.md`
   - Already has Layer 2 instructions but the prohibition language is
     advisory. Strengthen Step 4 to a hard classification rule.
   - Add Evidence Declaration block to output format.
2. `skills/smes/legal/entitlement_basis.md`
   - Already has Layer 2 retrieval for cited clauses. Add the hard
     CANNOT CONFIRM rule and Evidence Declaration block.
3. `skills/smes/legal/notice_and_instruction_compliance.md`
   - Add Layer 2 retrieval for notice clause (Cl. 1.3, Cl. 20.1/20.2.1)
     as mandatory before time bar calculation. Evidence Declaration block.
4. `skills/smes/legal/engineer_identification.md`
   - Add Layer 2 retrieval for Engineer authority clauses (Cl. 3.1, 3.5).
5. `skills/smes/legal/key_dates_and_securities.md`
   - Add Layer 2 retrieval for dates and securities clauses.

Priority 2 — Claims SMEs (depend on Legal SME outputs):
6. `skills/smes/claims/notice_compliance.md`
7. `skills/smes/claims/eot_quantification.md`
8. `skills/smes/claims/prolongation_cost.md`
9. `skills/smes/claims/disruption.md`
10. `skills/smes/claims/dispute_resolution_procedure.md`

Priority 3 — Schedule SMEs:
11. `skills/smes/schedule/programme_assessment.md`
12. `skills/smes/schedule/delay_identification.md`
13. `skills/smes/schedule/critical_path_analysis.md`
14. `skills/smes/schedule/time_at_large.md`
15. `skills/smes/schedule/acceleration.md`
16. `skills/smes/schedule/evm_and_cost_reporting.md`

Priority 4 — Technical SMEs:
17. `skills/smes/technical/specification_compliance.md`
    (Others in this group have lower FIDIC clause dependency — rebuild
    after specification_compliance is complete and pattern is established)

**What every rebuilt skill file must include:**

**(a) Evidence Declaration block in output format** — as the first
output section, matching the structure in SKILLS_STANDARDS.md v2.0
Section 9.

**(b) Strengthened Layer 2 retrieval instruction** — in the
Before You Begin section, the Layer 2 retrieval instruction must be
a mandatory step with explicit consequences if retrieval fails:

> Call search_chunks for the Layer 2 FIDIC clause(s) relevant to
> this skill before beginning analysis. If retrieval fails: record
> Layer 2 retrieved: NO in the Evidence Declaration block. Do not
> describe the subject matter or effect of any FIDIC clause from
> inference. State CANNOT CONFIRM — LAYER 2 NOT RETRIEVED for any
> finding that depends on clause text not retrieved.

**(c) Hard classification rules for CANNOT CONFIRM** — the Decision
Framework must include explicit classification outcomes for the case
where Layer 2 was not retrieved, matching the rules in
SKILLS_STANDARDS.md v2.0.

**Commits:** One per skill file after QG PASS.
Commit message format: `feat: rebuild [skill name] skill — evidence declaration protocol`

---

### Task 1.4 — End-to-End Validation Queries

**What:** Run three validation queries against the rebuilt skills using
real or realistic documents. These queries specifically test the grounding
behaviour.

**Test query 1 — Particular Conditions deletion (standard numbering):**
Upload a contract where the Particular Conditions delete a standard FIDIC
clause that exists in Layer 2 (e.g. Sub-Clause 8.4 EOT). Query: "What
was deleted from the standard FIDIC form and what is the effect?"
Expected: Agent retrieves Layer 2 clause, cites it, characterises the
deletion correctly.

**Test query 2 — Particular Conditions deletion (custom numbering):**
Upload a contract where the Particular Conditions use custom numbering
that does not match the standard FIDIC structure. Query: "What was
deleted and what is the effect?" Expected: Agent retrieves Layer 2
clause for the stated number, finds it does not match the context,
states CANNOT CONFIRM the subject matter from Layer 2 — standard form
clause [X] does not correspond to this contract's custom numbering —
flags the numbering discrepancy explicitly.

**Test query 3 — No Particular Conditions in warehouse:**
Upload only the Contract Agreement, without the Particular Conditions.
Query: "What are the key amendments to the FIDIC standard form?"
Expected: Agent states CANNOT ASSESS — Particular Conditions not
retrieved — and does not apply Layer 2 defaults as if they govern the
project.

**Pass criteria for each test:** Evidence Declaration block present;
CANNOT CONFIRM used correctly where retrieval failed; no hallucinated
clause descriptions; confidence correctly capped.

**Deliverable:** Validation results recorded in BUILD_LOG.md.

---

### Task 1.5 — Phase 1 Governing Document Updates

**What:** Update all governing documents to reflect Phase 1 completion.

- `docs/SKILLS_STANDARDS.md` — already updated in Task 1.1; confirm
  version is v2.0 and all cross-references are correct
- `docs/C1_REMAINING_WORK.md` — add Phase 2 as the next active
  workstream; remove Phase 1 items as each completes
- `BUILD_LOG.md` — Phase 1 completion entry
- `CLAUDE.md` — update Agent Architecture State section to reflect that
  all skill files now enforce the evidence declaration protocol

**Commit:** `chore: Phase 1 complete — governing docs updated`

---

## Phase 2 — Code-Level Enforcement

**Objective:** Add runtime validation that makes the evidence declaration
protocol structurally enforced in the Python pipeline. The agent cannot
produce a characterisation of a FIDIC clause without the Layer 2
retrieval confirmation being recorded in a machine-readable format that
the Python layer can validate. Confidence is automatically capped when
required evidence fields are missing.

**Agent:** DB Architect (schema if needed), Agent Orchestrator (Python)
**Executor:** Claude Code
**Governing document:** This plan + SKILLS_STANDARDS.md v2.0
**Prerequisite:** Phase 1 fully complete and validated

---

### Task 2.1 — Design the EvidenceRecord Model

**What:** Add a new Pydantic model `EvidenceRecord` to
`src/agents/models.py`. This model captures what Layer 1 and Layer 2
documents were retrieved by a specialist, and what could not be
confirmed.

**Model design:**

```python
class LayerRetrievalStatus(str, Enum):
    RETRIEVED = "RETRIEVED"
    NOT_RETRIEVED = "NOT_RETRIEVED"
    PARTIAL = "PARTIAL"

class ClauseEvidence(BaseModel):
    """Evidence record for a single FIDIC clause reference."""
    clause_number: str
    layer2_status: LayerRetrievalStatus
    layer2_source: str | None = None  # document name if retrieved
    layer2_content_confirmed: bool = False
    cannot_confirm_reason: str | None = None  # populated if NOT_RETRIEVED

class EvidenceRecord(BaseModel):
    """
    Tracks what was retrieved from Layer 1 and Layer 2 during
    specialist analysis. Populated by the specialist during its
    agentic loop and validated before findings are accepted.
    """
    layer1_primary_document: str | None = None
    layer1_particular_conditions_status: LayerRetrievalStatus = (
        LayerRetrievalStatus.NOT_RETRIEVED
    )
    layer2_status: LayerRetrievalStatus = LayerRetrievalStatus.NOT_RETRIEVED
    layer2_source: str | None = None
    clauses_retrieved: list[ClauseEvidence] = Field(default_factory=list)
    clauses_cannot_confirm: list[str] = Field(
        default_factory=list,
        description="Clause numbers where Layer 2 retrieval failed"
    )
```

**Updated SpecialistFindings:**

Add `evidence_record: EvidenceRecord | None = None` to the
`SpecialistFindings` model.

**File:** `src/agents/models.py`
**Commit:** `feat: EvidenceRecord model — Phase 2 grounding enforcement`

---

### Task 2.2 — Design the Grounding Schema Files

**What:** Add a `grounding_schema.json` file alongside each orchestrator
directive and key SME skill file. This JSON schema defines which evidence
fields are required for that skill, which are optional, and what
confidence cap applies when a required field is CANNOT_CONFIRM.

**Schema structure for each file:**

```json
{
  "skill": "legal_orchestrator",
  "layer2_required": true,
  "layer2_applies_to": ["particular_conditions_amendments"],
  "confidence_cap_without_layer2": "AMBER",
  "confidence_cap_without_particular_conditions": "GREY",
  "required_clause_retrieval": [
    {
      "trigger": "particular_conditions_deletion",
      "retrieval_required": "layer2_clause_text",
      "cannot_confirm_action": "cap_confidence_AMBER"
    }
  ],
  "mandatory_output_fields": [
    "evidence_declaration",
    "layer2_status",
    "layer1_particular_conditions_status"
  ]
}
```

**Files to create:**
- `skills/orchestrators/legal/grounding_schema.json`
- `skills/orchestrators/commercial/grounding_schema.json`
- `skills/orchestrators/financial/grounding_schema.json`
- `skills/smes/legal/grounding_schema.json`
- `skills/smes/claims/grounding_schema.json`
- `skills/smes/schedule/grounding_schema.json`
- `skills/smes/technical/grounding_schema.json`

**Commit:** `feat: grounding schema files for all orchestrators and SME groups`

---

### Task 2.3 — Update SkillLoader to Load Grounding Schemas

**What:** Update `src/agents/skill_loader.py` to optionally load the
`grounding_schema.json` file alongside the markdown skill file. Return
the schema as part of the skill loading result so that
BaseSpecialist and BaseOrchestrator can access it.

**Changes to skill_loader.py:**

Add method `load_grounding_schema(domain: str) -> dict | None`:
- Looks for `grounding_schema.json` in the same directory as the
  skill markdown file
- Returns the parsed JSON if found, None if not present
- Non-fatal: absence of grounding schema does not block execution
  (backward compatible)

**File:** `src/agents/skill_loader.py`
**Commit:** `feat: SkillLoader loads grounding_schema.json alongside skill markdown`

---

### Task 2.4 — Update BaseSpecialist for Evidence Validation

**What:** Update `src/agents/base_specialist.py` to:

1. Load the grounding schema for the domain at initialisation
2. After the agentic loop completes, parse the Evidence Declaration
   block from the specialist's findings text
3. Validate the evidence declaration against the grounding schema
4. Apply automatic confidence caps where required

**Validation logic:**

```python
def _validate_evidence_and_cap_confidence(
    self,
    findings: SpecialistFindings,
    grounding_schema: dict | None,
) -> SpecialistFindings:
    """
    Parse the Evidence Declaration block from findings text.
    Apply confidence caps per the grounding schema.
    Return updated SpecialistFindings.
    """
    if grounding_schema is None:
        return findings  # no schema — pass through unchanged

    evidence = self._parse_evidence_declaration(findings.findings)

    # Apply confidence caps
    if (
        grounding_schema.get("layer2_required")
        and evidence.layer2_status == LayerRetrievalStatus.NOT_RETRIEVED
    ):
        cap = grounding_schema.get("confidence_cap_without_layer2", "AMBER")
        findings = self._apply_confidence_cap(findings, cap)
        logger.warning(
            "confidence_capped_layer2_not_retrieved",
            domain=findings.domain,
            cap=cap,
        )

    if (
        evidence.layer1_particular_conditions_status
        == LayerRetrievalStatus.NOT_RETRIEVED
    ):
        cap = grounding_schema.get(
            "confidence_cap_without_particular_conditions", "GREY"
        )
        findings = self._apply_confidence_cap(findings, cap)
        logger.warning(
            "confidence_capped_particular_conditions_not_retrieved",
            domain=findings.domain,
            cap=cap,
        )

    findings.evidence_record = evidence
    return findings
```

**File:** `src/agents/base_specialist.py`
**Commit:** `feat: BaseSpecialist validates evidence declaration and caps confidence`

---

### Task 2.5 — Update BaseOrchestrator for Evidence Validation

**What:** Apply the same evidence validation logic to BaseOrchestrator
(Tier 1). Orchestrators analyse Particular Conditions directly — they
are the primary source of the "Fresh Milk" failure mode. The validation
must be applied to their outputs before they are returned to the main
orchestrator.

**Changes to base_orchestrator.py:**

Load grounding schema in `__init__` via updated SkillLoader.
After `_parse_response()`, call `_validate_evidence_and_cap_confidence()`
with the grounding schema.

Log a warning whenever confidence is automatically capped, including
the domain, the reason (Layer 2 not retrieved / Particular Conditions
not retrieved), and the original vs capped confidence level.

**File:** `src/agents/base_orchestrator.py`
**Commit:** `feat: BaseOrchestrator validates evidence declaration and caps confidence`

---

### Task 2.6 — Expose Evidence in Query Response

**What:** Surface the evidence record in the query response so that
users and auditors can see what was retrieved. This is a transparency
feature — it makes the grounding status visible in the response, not
just in the logs.

**Changes:**

In `build_response_text()` in `orchestrator.py`, add an optional
Evidence Summary section to each specialist finding card:

```
### Evidence Summary
Layer 2 (FIDIC [book] [edition]): RETRIEVED / NOT RETRIEVED
Particular Conditions: RETRIEVED / NOT RETRIEVED
Confidence cap applied: YES (reason) / NO
```

This section appears at the bottom of each domain assessment, below
the FLAGS summary. It is not shown when all evidence was retrieved
successfully (i.e. only shown when something was NOT_RETRIEVED or
a cap was applied).

**File:** `src/agents/orchestrator.py`
**Commit:** `feat: Evidence Summary section in query response when grounding gaps exist`

---

### Task 2.7 — Add evidence_record Column to query_log

**What:** Persist the evidence records to the `query_log` table so that
grounding gaps are auditable at the database level.

**Migration 017:**

```sql
ALTER TABLE query_log
ADD COLUMN evidence_records JSONB;
```

**Update audit.py:**

Add `evidence_records: list[dict] | None = None` parameter to
`write_audit_log` and include it in the row dict.

**Update orchestrator.py:**

Collect evidence records from all findings and pass to `write_audit_log`.

**Files:** New migration SQL, `src/agents/audit.py`, `src/agents/orchestrator.py`
**Commit:** `feat: Migration 017 — evidence_records column in query_log`

---

### Task 2.8 — End-to-End Validation

**What:** Repeat the three validation queries from Phase 1 Task 1.4
against the rebuilt system with Phase 2 enforcement active.

**Additional checks for Phase 2:**

- Query 2 (Layer 2 not retrievable): verify that `confidence` in the
  response is AMBER (not GREEN), and that the Evidence Summary section
  appears in the domain assessment
- Query 3 (no Particular Conditions): verify confidence is GREY and
  evidence_records in query_log shows NOT_RETRIEVED for both Layer 1
  and Layer 2

**Deliverable:** Validation results recorded in BUILD_LOG.md.

---

### Task 2.9 — Phase 2 Governing Document Updates

**What:** Update all governing documents to reflect Phase 2 completion.

- `docs/SKILLS_STANDARDS.md` — add Section 12: Code-Level Enforcement.
  Document the grounding schema format, the confidence cap rules, and
  the evidence_records column in query_log.
- `CLAUDE.md` — update Database State (migration 017), Agent
  Architecture State (evidence validation in BaseSpecialist and
  BaseOrchestrator), Key Files table.
- `BUILD_LOG.md` — Phase 2 completion entry.
- `docs/C1_REMAINING_WORK.md` — mark both phases complete.

**Commit:** `chore: Phase 2 complete — governing docs updated`

---

## Summary Table

| Task | Phase | Agent | Effort | Prerequisite |
|---|---|---|---|---|
| 1.1 SKILLS_STANDARDS.md v2.0 | 1 | Strategic Partner | Small | None |
| 1.2 Rebuild 3 orchestrator directives | 1 | Skill-builder + Agent Orchestrator | Medium | 1.1 |
| 1.3 Rebuild 17 SME skill files | 1 | Skill-builder + Agent Orchestrator | Large | 1.1, 1.2 |
| 1.4 Validation queries | 1 | Quality Guardian | Small | 1.2, 1.3 |
| 1.5 Phase 1 governing docs | 1 | Strategic Partner | Small | 1.4 |
| 2.1 EvidenceRecord model | 2 | Agent Orchestrator | Small | Phase 1 complete |
| 2.2 Grounding schema files | 2 | Agent Orchestrator | Small | 2.1 |
| 2.3 SkillLoader update | 2 | Agent Orchestrator | Small | 2.2 |
| 2.4 BaseSpecialist validation | 2 | Agent Orchestrator | Medium | 2.3 |
| 2.5 BaseOrchestrator validation | 2 | Agent Orchestrator | Medium | 2.4 |
| 2.6 Evidence in query response | 2 | Agent Orchestrator | Small | 2.5 |
| 2.7 Migration 017 + audit.py | 2 | DB Architect + Agent Orchestrator | Small | 2.5 |
| 2.8 End-to-end validation | 2 | Quality Guardian | Small | 2.7 |
| 2.9 Phase 2 governing docs | 2 | Strategic Partner | Small | 2.8 |

---

## Important Constraints — Do Not Change

- No new external frameworks (no Guardrails AI, no NeMo, no LangChain)
- No changes to the ingestion pipeline or embedding dimensions
- No changes to the FIDIC Layer 2 documents already ingested
- Grounding schema JSON files are read-only reference files, not
  executable code — they are loaded by Python but contain no logic
- Confidence cap logic is deterministic — it does not call the Claude
  API; it operates on the evidence declaration parsed from the findings
  text
- All changes are backward compatible — absence of a grounding schema
  file does not break existing functionality

---

## What This Does Not Solve

This plan addresses grounding failures where the agent skips Layer 2
retrieval. It does not address:

1. **Cases where the Layer 2 document does not contain the answer.**
   If the relevant FIDIC clause is not in the warehouse (e.g. a rare
   sub-clause from a 2017 book that was not chunked), retrieval will
   return no result and the output will correctly be CANNOT CONFIRM.
   The fix for this is to improve Layer 2 ingestion coverage.

2. **Cases where the Particular Conditions use a completely custom
   numbering scheme.** When a contract renumbers the FIDIC structure
   entirely, the agent must flag that Layer 2 standard clause numbers
   do not correspond to the project's custom numbering. This requires
   domain awareness in the skill files — the plan adds this as a
   mandatory flag in the rebuilt contract_assembly skill.

3. **Hallucinations unrelated to FIDIC clause characterisation.**
   The confidence cap and evidence declaration apply to FIDIC clause
   references. They do not prevent all hallucination in other parts
   of the output. The broader mitigation for hallucination is the
   warehouse-grounding principles in SKILLS_STANDARDS.md v2.0.

---

## Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Date | April 2026 |
| Status | Approved — governing reference for execution |
| Next review | After Phase 1 Task 1.4 validation results |
| Location | `docs/C1_AGENT_GROUNDING_PLAN.md` |
