# NCR Management

**Skill type:** Mixed
- Contract-type-agnostic: the review of NCR logs, assessment of
  non-conformance patterns, and evaluation of close-out status
  applies regardless of standard form or version
- Contract-type-specific: the contractual consequence of unresolved
  NCRs — the rectification obligation, the right to withhold payment,
  the right to refuse completion acceptance — must be confirmed from
  the retrieved governing standard in Layer 2b and the amendment
  document
**Layer dependency:**
- Layer 1 — project documents: NCR log; individual NCR forms;
  corrective action reports; re-inspection records; close-out
  records; amendment document (quality, rectification, and defects
  clauses); completion certificate (to assess NCR status at handover);
  Contract Data or equivalent (defects liability period); project
  specification (to confirm the requirement breached)
- Layer 2b — reference standards: quality and workmanship provisions
  for the confirmed standard form; defects liability provisions
  (if ingested)
- Layer 2a — internal standards: quality management procedures,
  NCR management policies (if applicable)
**Domain:** Technical & Construction SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when a query concerns the NCR record for a project or specific
work package, whether non-conformances have been properly recorded
and closed out, whether there are patterns of quality failure, or
whether outstanding NCRs at handover create a contractual liability.
Apply when assessing the overall quality management position on
a project.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings.

From the invoking orchestrator extract:
- Confirmed standard form and version
- Completion certificate date (if issued) — marks the boundary
  between the construction phase NCR obligation and the defects
  liability period obligation
- Defects liability period as confirmed from retrieved Contract
  Data or equivalent

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The NCR log (full register)
- Individual NCR forms for NCRs relevant to the query
- Corrective action reports
- Re-inspection records and close-out documentation
- The completion certificate (to establish the handover date)
- The project specification — sections relevant to NCRs in the log
- The amendment document — quality, rectification, and defects
  clauses

**If the NCR log is not retrieved:**
State CANNOT ASSESS the NCR position from warehouse documents.
Call tools to search before concluding. If still not found:
flag the absence — an NCR log should exist on any project with
formal quality management.

**If individual NCR forms are not retrieved for NCRs referenced
in the log:**
State the NCR references from the log but note that the detailed
description and close-out status cannot be confirmed from warehouse
documents for those NCRs.

### Layer 2b documents to retrieve (reference standards)

Call `search_chunks` with `layer_type = '2b'` to retrieve:
- Quality and workmanship obligations for the confirmed standard
  form (search by subject matter: "quality workmanship materials
  plant obligation")
- Defects liability provisions for the confirmed standard form
  (search by subject matter: "defects liability rectification
  defects period")

**Purpose:** To establish the standard form quality and defects
framework for comparison against the retrieved amendment document.
The specific obligations and periods are in the retrieved amendment
document and Contract Data.

**If the governing standard form is not retrieved from Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE for the
quality and defects provisions. Confidence cap: AMBER. Proceed
with Layer 1 documents only.

---

## Analysis workflow

### Step 1 — Assess the NCR log
*Contract-type-agnostic*

From the retrieved NCR log:
- Total number of NCRs raised
- Number closed (and close-out date range)
- Number open at the time of the query
- Number open at the completion certificate date (if the certificate
  has been retrieved and its date confirmed)
- Date range of NCR activity

**Extract all figures from the retrieved log.** Do not estimate.

### Step 2 — Assess each NCR (or a material sample)
*Contract-type-agnostic*

For each NCR in scope:
- NCR reference and date raised
- Description of the non-conformance from the retrieved NCR form
- Trade or work package affected
- Specification clause breached (from the retrieved NCR or
  specification — confirm from retrieved document)
- Corrective action required
- Close-out status: OPEN / CLOSED — state close-out date from
  retrieved records / CANNOT CONFIRM close-out

**Do not mark an NCR as closed without a retrieved close-out
record.** The log may show a status but close-out must be confirmed
from the retrieved close-out document or re-inspection record.

### Step 3 — Assess NCR patterns
*Contract-type-agnostic*

From the retrieved NCR log and individual NCRs:
- Is there a pattern of NCRs on the same trade, material, or
  system? (Multiple NCRs for the same sub-contractor, material,
  or specification clause)
- Is there a pattern in timing? (NCRs clustering in a specific
  period may indicate a supervision gap or resource issue)
- Are there repeat NCRs — the same non-conformance raised multiple
  times after a previous close-out, indicating the corrective
  action was not effective?

**Identify patterns only from retrieved documents.** State the
specific NCR references that constitute the pattern.

### Step 4 — Assess NCR status at completion acceptance
*Contract-type-agnostic*

From the retrieved completion certificate date and the NCR log:
- How many NCRs were open at the completion certificate date?
- Were open NCRs recorded on the completion certificate or in
  the outstanding works / snagging list?

**If the completion certificate date is confirmed from retrieved
documents:** Cross-reference against the NCR log to identify
open NCRs at that date.

**If the completion certificate has not been retrieved:**
State CANNOT CONFIRM the NCR position at handover.

Forensic significance: if the employer accepted handover with
open NCRs recorded, the employer may have accepted the works
subject to those items being remedied during the defects liability
period. If open NCRs were not recorded at handover: the employer's
right to refuse acceptance for those items may have been affected.
Flag and note that legal advice may be required on the contractual
consequence.

### Step 5 — Assess defects liability period vs construction phase NCRs
*Contract-type-specific*

From the retrieved defects liability period (confirmed from
Contract Data or equivalent) and the completion certificate date:
- Are there NCRs or defect records raised after the completion
  certificate date that fall within the defects liability period?
- These are defects liability period items — treat under the
  defects liability framework in the retrieved amendment document,
  which differs from the construction phase NCR framework

**Separate construction phase NCRs from defects liability period
items in the output.** The contractual framework for each differs —
extract the applicable provisions from the retrieved amendment
document.

### Step 6 — Assess rectification and close-out obligation
*Contract-type-specific*

From the retrieved amendment document and Layer 2b provisions:
- What is the contractual mechanism for instructing rectification?
- Who bears the cost of rectification?
- Is there a payment withholding mechanism for open NCRs?

**The rectification terms to apply are those in the retrieved
amendment document.** Do not apply any standard form position
without retrieved confirmation. If Layer 2b not retrieved: state
CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE.

---

## Classification and decision rules

**NCR status:**

Close-out record retrieved → CLOSED — state date and source
Close-out not in any retrieved document → CANNOT CONFIRM CLOSE-OUT
NCR log shows open at date of query → OPEN
NCR open at confirmed completion certificate date →
OPEN AT HANDOVER — flag

**NCR pattern:**

Three or more NCRs on the same trade, material, or specification
clause → PATTERN IDENTIFIED — state the NCRs and the common factor
Repeat NCR (same non-conformance after previous close-out) →
REPEAT NON-CONFORMANCE — flag; state the recurrence
No pattern from retrieved documents → NO PATTERN IDENTIFIED

**Defects liability period items:**

NCR or defect raised after completion certificate date and within
confirmed defects liability period → DEFECTS LIABILITY PERIOD ITEM
— treat under the defects liability framework
Defect raised after defects liability period expiry → POST-LIABILITY
PERIOD DEFECT — state the forensic implication

---

## When to call tools

**Signal:** NCR log not retrieved
**Action:** `get_related_documents` with document type "NCR Log",
"Non-Conformance Report Log"; `search_chunks` with query "NCR
non-conformance log register quality"
**Look for:** The full NCR register

**Signal:** Individual NCR close-out not confirmed
**Action:** `search_chunks` with query "NCR [reference] close-out
corrective action completed"; `get_related_documents` with
document type "Corrective Action Report", "Re-inspection Record"
**Look for:** The close-out record confirming the non-conformance
has been rectified

**Signal:** Specification clause for an NCR not confirmed
**Action:** `search_chunks` with query "[NCR subject] specification
clause requirement"; `get_related_documents` with document type
"Project Specification"
**Look for:** The specification section the NCR references

**Signal:** Completion certificate not retrieved — cannot confirm
NCR status at handover
**Action:** `get_related_documents` with document type "Completion
Certificate", "Taking-Over Certificate", "Certificate of Practical
Completion"; `search_chunks` with query "completion certificate
handover acceptance date"
**Look for:** The completion certificate and its date

**Signal:** Layer 2b quality and defects provisions not retrieved
**Action:** `search_chunks` with `layer_type = '2b'` and query
"quality workmanship materials defects liability rectification
[standard form name]"
**Look for:** Standard form quality and defects liability provisions

---

## Always flag — regardless of query

1. **Open NCRs at the confirmed completion certificate date** —
   flag; state the number, the NCR references, and the forensic
   implication for the handover position.

2. **Repeat NCRs — same non-conformance recurring** — flag; state
   the pattern with NCR references; the implication is that the
   corrective action is ineffective.

3. **Pattern of NCRs on the same trade or material** — flag; state
   the trade or material and the NCR references; the implication is
   a systemic quality failure in that area.

4. **NCR close-out not confirmed from retrieved documents** — flag
   each NCR where the log shows closed but no close-out record has
   been retrieved.

5. **NCR log absent from the warehouse** — flag; state that the
   quality management record cannot be assessed from warehouse
   documents.

6. **Governing standard not in Layer 2b** — flag; state that the
   rectification obligation and defects liability framework cannot
   be confirmed from the warehouse and that confidence is capped
   at AMBER.

---

## Output format

```
## NCR Management Assessment

### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [standard form name — or NOT RETRIEVED]
Layer 2b provisions retrieved: [quality/workmanship, defects
liability — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE]
Layer 2a source: [policy name — or NOT RETRIEVED / NOT APPLICABLE]
Layer 1 primary document: [NCR log reference — or NOT RETRIEVED]
Layer 1 amendment document: [name — or NOT RETRIEVED]
Provisions CANNOT CONFIRM: [list — or NONE]

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2b Reference Retrieved
[State whether quality/workmanship and defects liability provisions
were retrieved from Layer 2b. If not: state CANNOT CONFIRM —
STANDARD FORM NOT IN WAREHOUSE and list affected analysis steps.
Confidence cap: AMBER.]

### NCR Log Summary
NCR log retrieved: [YES — reference / NOT FOUND IN WAREHOUSE]
Total NCRs in retrieved log: [number]
Closed: [number]
Open at date of query: [number]
Open at completion certificate date: [number /
CANNOT CONFIRM — completion certificate not retrieved]
Date range: [from retrieved log]

### NCR Register

| NCR # | Date | Trade/Work | Spec clause | Corrective action | Status | Close-out confirmed |
|---|---|---|---|---|---|---|
| [#] | [date] | [trade] | [clause / NOT CONFIRMED] | [from NCR] | [OPEN/CLOSED] | [YES — source / CANNOT CONFIRM] |

### Findings by NCR (for NCRs of significance)

**NCR [reference]**
Date raised: [from log or form]
Description: [from retrieved NCR form / SUMMARY FROM LOG ONLY]
Specification clause: [from retrieved NCR or specification /
NOT CONFIRMED]
Corrective action: [from retrieved NCR]
Close-out status: [CLOSED — date and source / OPEN /
CANNOT CONFIRM — no close-out record retrieved]
Classification: [CONSTRUCTION PHASE NCR / DEFECTS LIABILITY
PERIOD ITEM / CANNOT CLASSIFY — completion certificate date
not confirmed]

### Pattern Analysis
Patterns identified: [YES — describe with NCR references /
NO PATTERNS IDENTIFIED FROM RETRIEVED DOCUMENTS]
Repeat NCRs: [YES — describe / NONE IDENTIFIED]

### NCR Position at Handover
Completion certificate date: [from retrieved certificate /
NOT CONFIRMED]
Open NCRs at handover: [number and references / CANNOT CONFIRM]
Recorded on completion certificate or snagging list: [YES / NO /
CANNOT CONFIRM]
Forensic note: [one sentence on the implication from retrieved
documents]

### Defects Liability Period Items (separate from construction phase NCRs)
[List of defects raised during the confirmed defects liability
period, or NONE IDENTIFIED / CANNOT ASSESS — defects liability
period not confirmed]

### Rectification Position
Contractual mechanism: [from retrieved amendment document /
CANNOT CONFIRM]
Cost allocation: [from retrieved amendment document and Layer 2b /
CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE]
Payment withholding: [from retrieved amendment document /
NOT STATED / CANNOT CONFIRM]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
*(Confidence scale: GREEN = all required evidence retrieved and findings fully supported | AMBER = Layer 2b not retrieved or amendment position unknown -- findings provisional | RED = critical document absent -- findings materially constrained | GREY = standard form unconfirmed -- form-specific analysis suspended. Full definition: skills/c1-skill-authoring/references/grounding_protocol.md)*
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any rectification obligation,
defects liability position, or quality standard from this section
without first confirming it from the retrieved project documents
and Layer 2b.*

**Quality and workmanship obligations — analytical reference:**
Standard forms consistently require that materials and workmanship
comply with the contract specification. The contract administrator
(under most standard forms) may reject non-conforming work and
instruct rectification. The contractor's rectification obligation
typically covers construction phase NCRs at the contractor's cost
where the non-conformance results from the contractor's failure to
meet the specification. The specific mechanism — inspection,
rejection, instruction, and rectification — is in the standard
form and the amendment document; retrieve before applying.

**Defects liability period — analytical reference:**
After completion acceptance, most standard forms provide for a
defects liability period during which defects are notified by the
contract administrator and remedied by the contractor. The duration
is in the Contract Data or equivalent — retrieve from Layer 1.
The contractual name for this period varies by standard form.
After the defects liability period, the contractor's contractual
liability for defects typically ends (subject to any statutory
long-stop liability under applicable law). Retrieve the period
and the defects notification mechanism from Layer 2b and the
amendment document before applying this framework.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies to
any contract form. All characterisations grounded in retrieved warehouse
documents only.*
