---
name: c1-skill-authoring
description: Build, rebuild, or validate C1 agent skill files and orchestrator
directives. Use this skill whenever creating or modifying any file under
skills/orchestrators/ or skills/smes/, rebuilding existing skill files as part
of the master plan, validating that a skill meets the evidence declaration
protocol, or checking whether a skill correctly enforces three-layer warehouse
retrieval. This skill governs all C1 agent skill authorship. Always use it
when the task involves any file under skills/.
---

# C1 Skill Authoring

C1 agent skills are operational instruction files. They tell an LLM how to
reason over construction project documents using a three-layer warehouse.
Every skill you build must enforce one non-negotiable principle:

**The agent may only characterise what it retrieved.**

---

## Governing Principles

These four principles govern every C1 skill file and orchestrator directive.
This is the single authoritative reference — docs/SKILLS_STANDARDS.md has
been archived. A skill that violates any of these principles fails the
quality gate.

**Principle 1 — No assumption, extrapolation, or inference.**
An agent may only state what retrieved documents support. If a required
document is not in the warehouse, the output is CANNOT CONFIRM — not an
estimate, not a default, not training knowledge applied as a substitute.
Every value, date, period, amount, and clause description must trace to a
specific retrieved document.

**Principle 2 — Contract type and standard form always identified.**
Every analytical step that involves a contractual provision must first
identify the governing standard from Layer 1 project documents. The agent
does not assume which contract form is in use. It identifies it from Layer 1,
then retrieves the relevant provision from Layer 2b. Where the analysis
differs depending on the contract form, this must be stated explicitly
in the skill file.

**Principle 3 — Three-layer retrieval always distinguished.**
Every skill file must explicitly distinguish between Layer 1 facts (what
this project agreed), Layer 2a policy (what the organisation requires
internally), and Layer 2b standards (what the governing external standard
says). The retrieval sequence is always: identify from Layer 1 → retrieve
from Layer 2b → retrieve amendment position from Layer 1 → apply Layer 1
position. If the governing standard is not in Layer 2b: CANNOT CONFIRM.
If the amendment document is not in Layer 1: CANNOT CONFIRM the amendment.

**Principle 4 — CANNOT CONFIRM is the opening state.**
The agent starts from zero evidence. CANNOT CONFIRM is not a fallback —
it is the correct output for any step where required evidence was not
retrieved. The skill must instruct the agent to call tools to search
before concluding a document is absent. After a tool search returns
nothing: state CANNOT CONFIRM, list the missing document, and state
which steps cannot proceed.

If a provision from the governing contract standard was not retrieved from
Layer 2b, the output for that provision is CANNOT CONFIRM. If an internal
policy was not retrieved from Layer 2a, the output is CANNOT CONFIRM. The
agent never fills a retrieval gap with training knowledge.

---

## Reference files — load when needed

| File | Load when |
|---|---|
| `references/grounding_protocol.md` | Always — before writing any skill file |
| `references/warehouse_retrieval.md` | When writing retrieval instructions or Before you begin sections |
| `references/output_formats.md` | When defining the output format section |
| `references/validation_scenarios.md` | When testing a completed skill draft |

---

## Workflow

### Step 1 — Identify what is being built

**Orchestrator directive** (`skills/orchestrators/{domain}/directive.md`)
Tier 1. Governs what the orchestrator analyses directly and what it delegates.

**SME skill file** (`skills/smes/{domain}/{skill}.md`)
Tier 2. Governs how a specialist performs a specific analytical task.

If rebuilding: read the existing file first. Note what is present, what is
missing, and what needs to change.

### Step 2 — Read grounding_protocol.md

Non-negotiable. Every C1 skill file must implement the Evidence Declaration
block and the retrieval rules. Do not write a single line before reading it.

### Step 3 — Read warehouse_retrieval.md

Understand the three-layer model before writing any retrieval instruction.
The skill must correctly distinguish Layer 1 (project), Layer 2a (internal),
and Layer 2b (external) in its Before you begin section.

### Step 4 — Draft the skill file

**SME skill file structure (mandatory, in this order):**
```
# [Skill Name]
[Header: skill type, layer dependency, domain, invoked by]
## When to apply this skill
## Before you begin
   ### Layer 1 documents to retrieve
   ### Layer 2a documents to retrieve (if applicable)
   ### Layer 2b documents to retrieve
## Analysis workflow
## Classification and decision rules
## When to call tools
## Always flag — regardless of query
## Output format  ← must include Evidence Declaration block
## Domain knowledge and standards
```

**Orchestrator directive structure (mandatory, in this order):**
```
## Role
## Scope of Direct Analysis
## Layer 2 Grounding Mandate  ← mandatory section
## SME Delegation Authority
## Output Structure  ← must include Evidence Declaration block
## Output Quality Standard
```

### Step 5 — Apply the grounding protocol

Before finalising, verify against `references/grounding_protocol.md`:
- Before you begin: Layer 2b retrieval mandatory before any standard form characterisation?
- Output format: Evidence Declaration block present?
- Decision rules: CANNOT CONFIRM outcomes with confidence caps?
- Always flag: "governing standard not in Layer 2b" present?

### Step 6 — Test using validation_scenarios.md

Run Tests A, B, C (mandatory for every skill) plus domain-specific tests.
State results explicitly. Fail = revise and retest before committing.

### Step 7 — Commit

One file per commit.
SME skill: `feat: rebuild [skill name] — evidence declaration, form-agnostic`
Orchestrator: `feat: rebuild [domain] orchestrator directive — Layer 2 grounding mandate`

---

## Non-negotiable rules

**1. Evidence Declaration block always present.**
Every output format must include it as the first section.

**2. Layer 2b retrieval mandatory before any standard form characterisation.**
The Before you begin section must explicitly instruct the agent to call
search_chunks to retrieve the relevant provision before characterising it.
The standard form may be FIDIC, NEC, JCT, AIA, or any other — the skill
does not assume which one. It retrieves whatever is in Layer 2b.

**3. CANNOT CONFIRM is always a valid output.**
Every decision framework must include explicit CANNOT CONFIRM outcomes.

**4. No standard form knowledge hardcoded.**
Clause numbers, procedure steps, time periods — none of these belong in a
skill file. They belong in the Layer 2b warehouse. The skill tells the agent
to retrieve and apply, not to assume.

**5. Form-agnostic analytical steps.**
Steps that reference a contractual procedure must describe the analytical
reasoning pattern, not the specific standard form procedure. The agent
identifies which standard applies from Layer 1, retrieves it from Layer 2b,
and applies what it finds.

**6. Internal policies retrieved from Layer 2a.**
Where an analysis step requires checking against internal policy (DOA,
authority matrix, internal procedure), the skill must instruct retrieval
from Layer 2a, not assume what the policy says.

---

## Quick grounding checklist

Before committing any skill file:

- [ ] Evidence Declaration block present in output format
- [ ] Layer 2b retrieval mandated before any standard form characterisation
- [ ] Layer 2a retrieval included where internal policy is relevant
- [ ] CANNOT CONFIRM outcomes present in decision framework
- [ ] Confidence cap (AMBER / GREY) stated when retrieval fails
- [ ] Always flag includes "governing standard not retrieved from Layer 2b"
- [ ] No clause numbers, time periods, or procedure steps hardcoded
- [ ] No specific contract form (FIDIC / NEC / JCT) assumed
- [ ] Output format consistent with SpecialistFindings.findings structure
