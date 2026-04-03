# NCR Management

**Skill type:** Contract-type-agnostic for the assessment framework
The review of NCR logs, assessment of non-conformance patterns,
and evaluation of close-out status applies regardless of FIDIC
book or edition. The contractual consequence of unresolved NCRs
(rectification obligation, right to withhold payment, right to
reject Taking-Over) is contract-type-specific and must be confirmed
from the retrieved Particular Conditions.
**Layer dependency:**
- Layer 1 — project documents: NCR log; individual NCR forms;
  corrective action reports; re-inspection records; close-out
  records; Particular Conditions (defects and testing clauses);
  Taking-Over Certificate (to assess NCR status at handover);
  specification (to confirm the requirement breached)
- Layer 2 — reference standards: FIDIC Clause 7 (Plant, Materials
  and Workmanship) and Clause 11 (Defects After Taking Over) for
  the confirmed book and edition
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
- Confirmed FIDIC book and edition
- Taking-Over Certificate date (if issued) — marks the boundary
  between the construction phase NCR obligation and the DNP defects
  obligation
- DNP period as confirmed from retrieved Contract Data

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The NCR log (full register)
- Individual NCR forms for NCRs relevant to the query
- Corrective action reports
- Re-inspection records and close-out documentation
- The Taking-Over Certificate (to establish the handover date)
- The project specification — for the sections relevant to NCRs
  in the log
- The Particular Conditions — defects and testing clauses

**If the NCR log is not retrieved:**
State CANNOT ASSESS the NCR position from warehouse documents.
Call tools to search before concluding. If still not found:
flag the absence — an NCR log should exist on any project with
formal quality management.

**If individual NCR forms are not retrieved for NCRs referenced
in the log:**
State the NCR references from the log but note that the detailed
description and close-out status cannot be confirmed from
warehouse documents for those NCRs.

### Layer 2 documents to retrieve (reference standards)

Call `search_chunks` to retrieve from Layer 2:
- FIDIC Clause 7 for the confirmed book and edition
- FIDIC Clause 11 (Defects After Taking Over) for the confirmed
  book and edition

**Purpose:** To establish the FIDIC framework for the rectification
obligation and defects liability. The specific obligations and
periods are in the retrieved Particular Conditions and Contract Data.

---

## Analysis workflow

### Step 1 — Assess the NCR log
*Contract-type-agnostic*

From the retrieved NCR log:
- Total number of NCRs raised
- Number closed (and close-out date range)
- Number open at the time of the query
- Number open at the Taking-Over Certificate date (if the TOC
  has been retrieved and its date confirmed)
- Date range of NCR activity

**Extract all figures from the retrieved log.** Do not estimate.

### Step 2 — Assess each NCR (or a material sample)
*Contract-type-agnostic*

For each NCR in scope (all NCRs for a full assessment, or those
relevant to the query):
- NCR reference and date raised
- Description of the non-conformance from the retrieved NCR form
- Trade or work package affected
- Specification clause breached (from the retrieved NCR or
  specification — confirm from retrieved document)
- Corrective action required
- Close-out status: OPEN / CLOSED — state close-out date from
  retrieved records / CANNOT CONFIRM close-out

**Do not mark an NCR as closed without a retrieved close-out
record.** The log may show a status but the close-out must be
confirmed from the retrieved close-out document or re-inspection
record.

### Step 3 — Assess NCR patterns
*Contract-type-agnostic*

From the retrieved NCR log and individual NCRs:
- Is there a pattern of NCRs on the same trade, material,
  or system? (Multiple NCRs for the same sub-contractor, for
  the same material, or for the same specification clause)
- Is there a pattern in the timing? (NCRs clustering in a
  specific period may indicate a supervision gap or resource issue)
- Is there a pattern of repeat NCRs — the same non-conformance
  raised multiple times after a previous close-out, indicating
  the corrective action was not effective?

**Identify patterns only from retrieved documents.** State the
specific NCR references that constitute the pattern.

### Step 4 — Assess NCR status at Taking-Over
*Contract-type-agnostic*

From the retrieved Taking-Over Certificate date and the NCR log:
- How many NCRs were open at the Taking-Over Certificate date?
- Were open NCRs recorded on the Taking-Over Certificate or in
  the snagging list?

**If the Taking-Over Certificate date is known from retrieved
documents:** Cross-reference against the NCR log to identify
open NCRs at that date.

**If the Taking-Over Certificate has not been retrieved:**
State CANNOT CONFIRM the NCR position at handover.

Forensic significance: if the Employer accepted the Taking-Over
with open NCRs recorded, the Employer may have accepted the
works subject to those items being remedied during the DNP.
If open NCRs were not recorded on the Taking-Over Certificate:
the Employer's right to refuse Taking-Over for those items may
have been waived. This is a contractual analysis — flag and
note that legal advice may be required.

### Step 5 — Assess DNP defects vs construction phase NCRs
*Contract-type-specific*

From the retrieved DNP period (confirmed from Contract Data) and
the Taking-Over Certificate date:
- Are there NCRs or defect records raised after the Taking-Over
  Certificate date that fall within the DNP?
- These are DNP defects under FIDIC Clause 11 — different
  from construction phase NCRs

**Separate construction phase NCRs from DNP defects in the
output.** The contractual framework for each differs — extract
the applicable provisions from the retrieved Particular Conditions.

### Step 6 — Assess rectification and close-out
*Contract-type-specific*

From the retrieved Particular Conditions:
- What is the contractual mechanism for instructing rectification?
- Who bears the cost of rectification (Contractor's obligation
  under Clause 7 for workmanship/materials non-conformances)?
- Is there a payment withholding mechanism for open NCRs?

**The rectification terms to apply are those in the retrieved
Particular Conditions.** Do not apply standard form provisions
without PC confirmation.

---

## Classification and decision rules

**NCR status:**

Close-out record retrieved → CLOSED — state date
Close-out not in any retrieved document → CANNOT CONFIRM CLOSE-OUT
NCR log shows open at date of query → OPEN
NCR open at confirmed Taking-Over Certificate date →
OPEN AT HANDOVER — flag

**NCR pattern:**

Three or more NCRs on the same trade, material, or specification
clause → PATTERN IDENTIFIED — state the NCRs and the common
factor
Repeat NCR (same non-conformance after previous close-out) →
REPEAT NON-CONFORMANCE — flag; state the recurrence
No pattern from retrieved documents → NO PATTERN IDENTIFIED

**DNP defects:**

NCR/defect raised after TOC date and within confirmed DNP period
→ DNP DEFECT under Clause 11 — treat under DNP framework
Defect raised after DNP expiry → POST-DNP DEFECT — state the
forensic implication (Contractor's liability under FIDIC may
have ended, subject to decennial liability where applicable)

---

## When to call tools

**Signal:** NCR log not retrieved
**Action:** `get_related_documents` with document type "NCR Log",
"Non-Conformance Report Log"; `search_chunks` with query
"NCR non-conformance log register quality"
**Look for:** The full NCR register

**Signal:** Individual NCR close-out not confirmed
**Action:** `search_chunks` with query "NCR [reference] close-out
corrective action completed"; `get_related_documents` with
document type "Corrective Action Report", "Re-inspection Record"
**Look for:** The close-out record or re-inspection confirming
the non-conformance has been rectified

**Signal:** Specification clause for an NCR not confirmed
**Action:** `search_chunks` with query "[NCR subject] specification
clause requirement"; `get_related_documents` with document type
"Project Specification"
**Look for:** The specification section the NCR references

**Signal:** Taking-Over Certificate not retrieved — cannot
confirm NCR status at handover
**Action:** `get_related_documents` with document type "Taking-Over
Certificate"; `search_chunks` with query "taking over certificate
handover completion"
**Look for:** The Taking-Over Certificate and its date

---

## Always flag — regardless of query

1. **Open NCRs at the confirmed Taking-Over Certificate date** —
   flag; state the number, the NCR references, and the forensic
   implication for the handover position.

2. **Repeat NCRs — same non-conformance recurring** — flag; state
   the pattern with NCR references; the forensic implication is
   that the corrective action is ineffective.

3. **Pattern of NCRs on the same trade or material** — flag; state
   the trade/material and the NCR references; the implication is
   a systemic quality failure in that area.

4. **NCR close-out not confirmed from retrieved documents** —
   flag each NCR where the log shows closed but no close-out
   record has been retrieved; state that close-out cannot be
   confirmed.

5. **NCR log absent from the warehouse** — flag; state that the
   quality management record cannot be assessed from warehouse
   documents.

---

## Output format

```
## NCR Management Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2 Reference Retrieved
[State whether FIDIC Clause 7 and 11 were retrieved. If not:
state analytical knowledge applied.]

### NCR Log Summary
NCR log retrieved: [YES — reference / NOT FOUND IN WAREHOUSE]
Total NCRs in retrieved log: [number]
Closed: [number]
Open at date of query: [number]
Open at Taking-Over Certificate date: [number / CANNOT CONFIRM — TOC not retrieved]
Date range: [from retrieved log]

### NCR Register

| NCR # | Date | Trade/Work | Spec clause | Corrective action | Status | Close-out confirmed |
|---|---|---|---|---|---|---|
| [#] | [date] | [trade] | [clause / NOT CONFIRMED] | [from NCR] | [OPEN/CLOSED] | [YES — source / CANNOT CONFIRM] |

### Findings by NCR (for NCRs of significance)

**NCR [reference]**
Date raised: [from log/form]
Description: [from retrieved NCR form / SUMMARY FROM LOG ONLY]
Specification clause: [from retrieved NCR or specification / NOT CONFIRMED]
Corrective action: [from retrieved NCR]
Close-out status: [CLOSED — date and source / OPEN /
CANNOT CONFIRM — no close-out record retrieved]
DNP classification: [CONSTRUCTION PHASE NCR / DNP DEFECT /
CANNOT CLASSIFY — TOC date not confirmed]

### Pattern Analysis
Patterns identified: [YES — describe with NCR references /
NO PATTERNS IDENTIFIED FROM RETRIEVED DOCUMENTS]
Repeat NCRs: [YES — describe / NONE IDENTIFIED]

### NCR Position at Taking-Over
Taking-Over Certificate date: [from retrieved TOC / NOT CONFIRMED]
Open NCRs at Taking-Over: [number and references / CANNOT CONFIRM]
Recorded on TOC/snagging list: [YES / NO / CANNOT CONFIRM]
Forensic note: [one sentence on the implication from retrieved documents]

### DNP Defects (separate from construction phase NCRs)
[List of defects raised during the confirmed DNP period,
or NONE IDENTIFIED / CANNOT ASSESS — DNP period not confirmed]

### Rectification Position
Contractual mechanism: [from retrieved PC / CANNOT CONFIRM]
Cost allocation: [CONTRACTOR — Clause 7 / EMPLOYER / CANNOT CONFIRM]
Payment withholding: [from retrieved PC / NOT STATED / CANNOT CONFIRM]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any rectification obligation or
liability position from this section without first confirming it
from the retrieved project documents.*

**FIDIC Clause 7 and 11 — analytical reference:**
Clause 7 requires the Contractor to provide materials and
workmanship in accordance with the contract. The Engineer
(Red/Yellow) or Employer's Representative (Silver) may reject
non-conforming work and instruct rectification. After Taking-Over,
defects are addressed under Clause 11 during the DNP — the
Contractor must remedy defects notified before the end of the DNP.
The DNP duration is in the Contract Data — retrieve from Layer 1.
After the Performance Certificate, the Contractor's liability
for defects under FIDIC ends (subject to decennial liability
where applicable). Retrieve the specific clauses from Layer 2
and check the PC for amendments.
