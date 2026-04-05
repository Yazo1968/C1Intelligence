# C1 Output Formats — Mandatory Templates

---

## Evidence Declaration Block — Universal Template

First section of every output. Do not modify field names.

```
### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [standard name — or NOT RETRIEVED]
Layer 2b provisions retrieved: [description — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE]
Layer 2a source: [policy name — or NOT RETRIEVED / NOT APPLICABLE]
Layer 1 primary document: [name and reference — or NOT RETRIEVED]
Layer 1 amendment document: [name — or NOT RETRIEVED / NOT APPLICABLE]
Provisions CANNOT CONFIRM: [list — or NONE]
```

---

## Orchestrator Directive Output Template

```
### Evidence Declaration
[Universal template above]

### Executive Summary
[Two to four sentences. Overall position, confidence, single most
important finding. No source citations — synthesis only.]

### [Domain assessment sections]
- Findings from retrieved documents only
- Every finding cites source document by name and reference number
- FLAG / INFORMATIONAL / CANNOT ASSESS classification
- One-sentence implication for every FLAG

### SME Findings
[Synthesise SME findings — do not relay verbatim]

### FLAGS Summary
FLAG [N]: [finding] — [implication in one sentence]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [Two to three sentences — retrieved facts only]
```

---

## SME Skill File Output Template

```
## [Skill Name] Assessment

### Evidence Declaration
[Universal template above]

### Documents Retrieved (Layer 1)
[Every retrieved document with reference and date]

### Documents Not Retrieved
[Every required document absent from warehouse.
State which steps are affected. If nothing missing: "None."]

### Layer 2b Reference
[What was retrieved, from which standard. If nothing:
state which standard was expected and not found.]

### [Skill-specific sections]
[Each section begins with: [GREEN / AMBER / RED / GREY / CANNOT ASSESS]
Every finding cites its source document.]

### FLAGS
FLAG: [finding] — [forensic implication in one sentence]
[Include a flag for every CANNOT CONFIRM provision]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
[If GREY: state which critical document was missing]
Summary: [Two to three sentences — retrieved facts only]
```

---

## Classification Scheme

| Colour | Meaning |
|---|---|
| GREEN | Finding confirmed from retrieved documents, no material issues |
| AMBER | Material issues or gaps — one or more flags raised, or required document not retrieved |
| RED | Critical issue — contradiction, deleted entitlement, unresolvable gap |
| GREY | Cannot assess — critical document absent from warehouse |

**CANNOT ASSESS** — for individual findings within an output when a required
document was not retrieved. Different from GREY (which is overall confidence).

**FLAG — Orchestrator level (ISO 31000:2018 risk register format)**

At orchestrator level every FLAG is a structured risk register entry per
ISO 31000:2018. The simple one-sentence format is for SME internal output
only and does not reach the user. Orchestrator FLAGS use this nine-field format:

RISK-[ID] | [Category]
Description:       [what has happened or could happen — from retrieved documents only]
Cause:             [root cause — from retrieved documents only]
Consequence:       [HIGH / MEDIUM / LOW] — [financial or contractual impact from retrieved documents]
Likelihood:        [HIGH / MEDIUM / LOW] — [basis from retrieved documents — or: CANNOT ASSESS — state which document is missing]
Inherent Rating:   [CRITICAL / HIGH / MEDIUM / LOW]
Existing Controls: [mitigations evidenced in retrieved documents — or: NONE EVIDENCED]
Treatment:         [AVOID / REDUCE / TRANSFER / ACCEPT] — [specific action from retrieved documents]
Residual Rating:   [CRITICAL / HIGH / MEDIUM / LOW — or: CANNOT ASSESS — controls not evidenced in warehouse]
Status:            [OPEN / REALIZED / TREATED / EXPIRED / ACCEPTED]

Risk Category values: Legal & Contractual | Commercial & Financial |
Technical & Construction | Schedule & Programme | Compliance & Governance |
Financial & Accounting

Risk Rating Matrix (Likelihood x Consequence = Inherent Rating):
  High Likelihood   + High Consequence   = CRITICAL
  High Likelihood   + Medium Consequence = HIGH
  High Likelihood   + Low Consequence    = MEDIUM
  Medium Likelihood + High Consequence   = HIGH
  Medium Likelihood + Medium Consequence = MEDIUM
  Medium Likelihood + Low Consequence    = LOW
  Low Likelihood    + High Consequence   = MEDIUM
  Low Likelihood    + Medium Consequence = LOW
  Low Likelihood    + Low Consequence    = LOW

Risk Status definitions:
  OPEN      — risk is active, not yet controlled or treated
  REALIZED  — risk has materialised and is documented in retrieved evidence
  TREATED   — controls in place, residual risk remains, evidenced in retrieved documents
  EXPIRED   — risk window has closed, no further action required
  ACCEPTED  — risk acknowledged and formally accepted, no further treatment planned

Likelihood derivation rules: Derive Likelihood from retrieved documents
where evidence supports it. A condition already met from retrieved documents
(e.g. notice issued beyond the contractual period) = HIGH. A risk dependent
on future events not evidenced in retrieved documents = CANNOT ASSESS.
Do not estimate Likelihood from training knowledge.

Residual Rating derivation rules: Requires evidence of existing controls
in retrieved documents (remediation actions, insurance certificates, extension
grants, payment of disputed amounts, or equivalent). If no controls are
evidenced: CANNOT ASSESS — controls not evidenced in warehouse.
Do not assume controls exist.

**FLAG — SME level (internal format — not user-facing)**

At SME level FLAGS use the simple format for internal orchestrator consumption:
FLAG: [finding] — [forensic implication in one sentence]
Include a flag for every CANNOT CONFIRM provision.
SME FLAGS are synthesised by the orchestrator into risk register entries.
They do not reach the user in this simple format.

**INFORMATIONAL** — Noted for completeness, no risk or issue.

---

## Source Citation Format

```
[Document name, Ref. {reference}, {date}, {clause/section if applicable}]
```

Examples:
```
[Contract Agreement, Ref. YD-001-CA, 2023-07-06, Clause 4.4]
[NEC4 ECC General Conditions, Clause 61.3]
[FIDIC Yellow Book 1999 General Conditions, Sub-Clause 11.8]
[Internal DOA Matrix v2.1, Section 3.2 — Procurement Authority]
```

If a fact cannot be sourced to a retrieved document: it may not appear
in the output.
