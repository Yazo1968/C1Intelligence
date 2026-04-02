# Prolongation Cost

**Skill type:** Contract-type-specific (recoverable heads of claim,
cost plus profit entitlement, and Engineer/Employer's Representative
authority differ by book and edition)
**Domain:** Claims & Disputes SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply this skill when retrieved chunks contain a prolongation cost
claim, a time-related cost submission, a query about the cost
consequences of a delay, or a request to assess whether prolongation
costs are recoverable and properly supported. Also apply when an EOT
has been awarded or claimed and a corresponding cost claim is expected
but has not been found in the warehouse.

---

## Before you begin

**Step 1 — Establish the governing contract type and entitlement basis.**
Read the Legal orchestrator findings and the EOT quantification
findings if available. Extract:
- FIDIC book and edition
- The delay event type: Employer Risk Event (EOT + Cost), Neutral
  Event (EOT only — no cost), or Contractor Risk Event (no entitlement)
- Whether the Particular Conditions amend the cost recovery provisions
  for the relevant clause

Cost entitlement is conditional on the event type. A prolongation
cost claim for a Neutral Event has no contractual basis. Do not
assess quantum before confirming entitlement.

**Step 2 — Extract the applicable cost recovery clause from the
Particular Conditions.**
The cost recovery clause varies by the entitlement event. Extract
the clause from the project's Particular Conditions — do not apply
General Conditions defaults. Key clauses to identify:
- The clause under which the EOT was claimed (this determines whether
  Cost, or Cost plus Profit, is recoverable)
- Any amendment to the definition of "Cost" in the Particular
  Conditions — GCC Particular Conditions sometimes exclude specific
  categories of cost from the definition

**Step 3 — Establish the prolongation period.**
The prolongation period is the period of EOT for which the cost
claim is made. Extract from the EOT findings:
- The EOT period claimed
- The EOT period awarded or agreed (if any)
- Whether the prolongation cost claim matches the EOT period or
  differs — a mismatch must be flagged

**Step 4 — Identify the cost methodology used.**
Actual cost (supported by site records) is the preferred and most
defensible methodology. Pre-agreed rates (where the contract
provides them) are also acceptable. Global claim is a last resort
only. Identify which methodology has been applied before assessing
the quantum.

---

## Analysis workflow

**Step 1 — Retrieve all prolongation cost documents.**
Call `get_related_documents` with document_type "Prolongation Cost
Claim". Call `search_chunks` with query "prolongation cost time-related
preliminaries site overhead staff costs". Compile all cost claim
documents.

**Step 2 — Assess each head of claim.**
Prolongation cost claims typically comprise the following heads.
Assess each separately — recoverable heads differ by contract type
and entitlement clause:

*Time-related site overheads:* Staff salaries and on-costs for
personnel retained on site during the prolongation period. Requires:
payroll records, staff deployment schedules, evidence that staff
were actually retained (not demobilised) during the period.

*Site establishment costs:* Accommodation, temporary facilities,
utilities, welfare facilities retained during the prolongation
period. Requires: invoices, hire agreements, utility bills for
the specific period.

*Plant and equipment:* Time-related costs for plant retained on
site during the prolongation period. Requires: plant hire records,
ownership cost calculations where Contractor-owned, evidence of
retention on site. Idle plant rates differ from working rates —
check whether the claim applies the correct rate.

*Finance charges:* Interest on capital employed or financing costs
incurred as a result of delayed payment caused by the prolongation.
Only recoverable where included in the definition of "Cost" under
the applicable FIDIC edition and not excluded by Particular
Conditions. Check the definition of "Cost" in the contract.

*Head office overhead contribution:* The contribution to Contractor's
head office overheads attributable to the prolonged period. Often
calculated using the Hudson formula, Emden formula, or Eichleay
formula. These formulaic approaches are used where actual head
office overhead records are not available — they are less preferred
than actual cost evidence. Identify which formula is used and
whether the inputs are supported by audited accounts.

*Profit:* Recoverable only where the entitlement clause provides
for Cost plus Profit — not all clauses do. Verify from the
applicable clause extracted from the Particular Conditions.

**Step 3 — Cross-check against contemporaneous records.**
For each head of claim, verify that the claimed costs are
evidenced by contemporaneous records covering the specific
prolongation period. Compare:
- Claimed staff costs vs. payroll records and site resource schedules
- Claimed plant costs vs. plant hire records
- Claimed establishment costs vs. invoices and delivery records

Flag any head of claim where the supporting records cover a
different period, a different scope, or are absent.

**Step 4 — Assess the prolongation period alignment.**
Compare the prolongation cost period claimed against the EOT period
established in eot_quantification findings. Flag any mismatch:
- Cost claimed for a longer period than the EOT — not supportable
  without separate entitlement for the excess period
- Cost claimed for a shorter period than the EOT — may indicate
  partial claim only, note this
- Cost claimed for a period that includes concurrent Contractor
  delay — the recoverable period may be reduced; see decision
  framework

**Step 5 — Assess the global claim position.**
If the claim is presented as a global claim (total cost minus
contract sum without individual causation links), assess whether
the global claim threshold has been satisfied:
- Is it truly impossible to link individual cost items to
  individual causation events?
- Is the aggregate quantum supported by records?
- Has the Contractor demonstrated that the global loss resulted
  from Employer default?

Flag a global claim where individual causation links could
reasonably have been established. Global claims face significant
credibility challenges in GCC arbitration.

**Step 6 — Assess the Engineer's or Employer's Representative's
response.**
Retrieve any determination or response to the prolongation cost
claim. Compare awarded costs against claimed costs. Identify
reasons for reduction or rejection.

---

## Classification and decision rules

**Entitlement confirmation:**

Delay event is Employer Risk Event AND cost recovery clause
confirmed from Particular Conditions:
→ Proceed with quantum assessment

Delay event is Neutral Event:
→ **NO COST ENTITLEMENT** — EOT only
→ Flag and do not assess quantum further unless the claim
  separately establishes a cost entitlement basis

Delay event is Contractor Risk Event:
→ **NO ENTITLEMENT** — flag and cease quantum assessment

Entitlement clause not confirmed from Particular Conditions:
→ Flag: cost recovery basis cannot be confirmed — assessment
  is conditional

**Profit recoverability:**

Applicable clause provides for "Cost plus Profit":
→ Profit head of claim is recoverable in principle — assess quantum

Applicable clause provides for "Cost" only:
→ Profit is not recoverable under this clause
→ Flag if profit is included in the claim

**Head office overhead formula:**

Actual head office overhead records provided:
→ Preferred — assess against audited accounts

Hudson, Emden, or Eichleay formula used without actual records:
→ Acceptable as secondary methodology — flag the limitation
→ Verify formula inputs are supported (contract sum, contract
  period, annual turnover from audited accounts)

**Concurrent delay cost period:**

Concurrent Contractor-caused delay identified during the
prolongation period:
→ The recoverable cost period may be reduced for the concurrent
  period — flag and state the affected period
→ Do not resolve the quantum — state both positions

---

## When to call tools

**Signal:** Staff costs claimed but no payroll records or resource
schedule retrieved.
**Action:** Call `search_chunks` with query "resource schedule
staff deployment site personnel [prolongation period dates]".
Call `get_related_documents` with document_type "Progress Report"
for the prolongation period.
**Look for:** Any document recording actual staff presence on site
during the prolongation period.

**Signal:** Plant costs claimed but no hire records retrieved.
**Action:** Call `search_chunks` with query "plant hire equipment
[prolongation period dates]".
**Look for:** Hire agreements, plant returns, or site records
showing plant on site during the period.

**Signal:** Finance charges claimed but the definition of "Cost"
in the contract has not been retrieved.
**Action:** Call `search_chunks` with query "definition cost
financing charges interest" and call `get_document` on the
contract agreement or General Conditions document.
**Look for:** The definition of "Cost" and whether financing
charges are expressly included or excluded.

**Signal:** Head office overhead claimed using a formula but
no audited accounts retrieved.
**Action:** Call `search_chunks` with query "audited accounts
annual turnover overhead".
**Look for:** Audited financial statements supporting the
formula inputs. If absent, flag the gap.

---

## Always flag — regardless of query

**Flag 1 — Cost claim for Neutral Event or Contractor Risk Event.**
If the entitlement basis established in EOT findings shows a
Neutral Event or Contractor Risk Event, flag immediately that
no cost entitlement exists under the applicable clause. State
the clause and the event classification.

**Flag 2 — Prolongation period exceeds awarded or agreed EOT.**
If the cost claim covers a longer period than the EOT awarded
or agreed, flag the excess. The cost claim for the excess period
has no established time entitlement foundation.

**Flag 3 — Profit claimed where clause provides Cost only.**
If the entitlement clause does not include Profit and the claim
includes a profit head, flag this as non-recoverable under the
applicable clause.

**Flag 4 — No contemporaneous cost records for any head of claim.**
If the claim is not supported by any contemporaneous records
for a material head, flag this as a credibility and evidential
risk. A prolongation cost claim built entirely on retrospective
schedules without site records is forensically weak.

**Flag 5 — Global claim presented where individual links are
possible.**
If the claim is structured as a global claim but the documents
in the warehouse would permit individual causation links to be
established, flag this as a methodological weakness. State
which documents support individual linkage.

---

## Output format
```
## Prolongation Cost Assessment

### Entitlement Basis
- FIDIC book and edition: [extracted]
- Delay event type: [Employer Risk / Neutral / Contractor Risk]
- Applicable cost recovery clause: [clause from Particular Conditions]
- Profit recoverable: [YES / NO — cite clause]
- Finance charges within Cost definition: [YES / NO / CANNOT CONFIRM]
- Particular Conditions amendments to cost provisions: [list or NONE FOUND]

### Prolongation Period
- EOT claimed: [days and period]
- EOT awarded/agreed: [days and period or NOT ESTABLISHED]
- Cost claim period: [dates]
- Alignment: [CONSISTENT / MISMATCH — detail]

### Heads of Claim Assessment

| Head | Amount claimed | Records present | Period covered | Assessment |
|---|---|---|---|---|
| Site staff | [amount] | [YES/PARTIAL/NO] | [dates] | [SUPPORTABLE/ISSUES/NOT SUPPORTABLE] |
| Site establishment | [amount] | [YES/PARTIAL/NO] | [dates] | [assessment] |
| Plant and equipment | [amount] | [YES/PARTIAL/NO] | [dates] | [assessment] |
| Finance charges | [amount] | [YES/PARTIAL/NO] | [dates] | [assessment] |
| Head office overhead | [amount] | [YES/PARTIAL/NO] | [dates] | [assessment] |
| Profit | [amount] | [YES/PARTIAL/NO] | [dates] | [assessment] |
| **Total** | [total] | | | |

### Findings by Head of Claim

**[Head of claim]**
Amount claimed: [amount]
Entitlement basis: [clause]
Methodology: [actual cost / formula / global]
Records: [description of supporting documents]
Period covered by records: [dates]
Assessment: [SUPPORTABLE / PARTIALLY SUPPORTABLE / NOT SUPPORTABLE /
CANNOT ASSESS]
Finding: [specific conclusion with source attribution]

### Concurrent Delay Adjustment
[Period affected and cost impact, or NOT APPLICABLE]

### Engineer's / Employer's Representative's Position
Amount awarded: [amount or NOT FOUND]
Reasons for reduction: [summary or NOT FOUND]
Source document: [reference]

### FLAGS
[Each flag with one-sentence implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences]
```

---

## Domain knowledge and standards

### Cost recoverability by clause — contract-type-specific

The heads of claim recoverable depend on the clause under which
the EOT event falls. The key distinction is whether the clause
provides for Cost only, or Cost plus Profit. This must always
be extracted from the Particular Conditions — do not apply
General Conditions defaults.

Under all three FIDIC books: "Cost" is defined in the contract.
The definition in the General Conditions typically includes
all expenditure reasonably incurred by the Contractor, including
overheads but excluding profit. Financing charges are expressly
included in the 2017 editions and included in the 1999 editions
where the definition encompasses "all expenditure". Verify
the definition in the project's contract documents.

**Silver Book specific:** The Silver Book allocates most risk
to the Contractor. Employer Risk Events are narrower. Cost
recovery under the Silver Book requires careful verification
against the Particular Conditions — many Silver Book projects
in the GCC have Particular Conditions that further restrict
the already narrow Employer Risk Event list.

### Head office overhead formulae

**Hudson formula:** (Head office overhead percentage from the
contract / 100) x (Contract sum / Contract period) x Delay period.
Inputs: the percentage must come from the contract documents
or the Contractor's priced bill — not assumed.

**Emden formula:** (Head office overhead + Profit from audited
accounts / Total turnover from audited accounts) x (Contract
sum / Contract period) x Delay period.
More defensible than Hudson where actual accounts are available.

**Eichleay formula:** US-developed, less commonly accepted in
GCC proceedings. Flag if used — it may face challenge before
ICC, DIAC, and ADCCAC tribunals.

All formula inputs must be verified against source documents.
A formula applied with assumed or unverified inputs is
challengeable on its face.

### GCC-specific practice

UAE: Abu Dhabi government projects frequently have Particular
Conditions that exclude or cap head office overhead recovery.
Extract the definition of Cost and any overhead limitation from
the Particular Conditions — do not assume the General Conditions
definition applies.

Saudi Arabia: government contracts often limit the categories
of recoverable cost and may exclude financing charges entirely.
Always verify against the Particular Conditions.

Qatar: on major infrastructure projects, cost substantiation
requirements are high — the Engineer or Employer's Representative
will typically require audited records, not formulaic calculations.
A claim submitted without audited support will face rejection
on evidential grounds regardless of entitlement.

Finance charges: in all GCC jurisdictions, the recoverability
of finance charges as part of "Cost" rather than as a separate
interest claim is significant because interest claims face
restrictions under Islamic finance principles in Saudi Arabia
and, to a lesser extent, in the UAE and Qatar. A claim for
finance charges within the definition of Cost is generally
more enforceable than a standalone interest claim in GCC
proceedings.
