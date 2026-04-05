# Multi-Contract Account Reconciliation

**Skill type:** Mixed
- Contract-type-agnostic: the reconciliation framework — contracted
  sum plus approved variations versus certified or invoiced amounts
  versus paid amounts versus retention — applies regardless of
  contract form or procurement route
- Contract-type-specific: the mechanism for payment certification,
  variation valuation, and retention release differs by contract form
  and is retrieved from each contract document in Layer 1

**Layer dependency:**
- Layer 1 — project documents: all contract documents in the warehouse
  (main contract, subcontracts, consultancy agreements, purchase orders,
  task orders, and all variations and change orders to each); payment
  applications and invoices; payment certificates; payment records
  (bank confirmations, remittance advice, or equivalent); retention
  records; project cost reports; variation registers
- Layer 2a — internal documents: internal financial reporting policy;
  accounts payable and receivable procedures; three-way matching
  requirements; DOA matrix for payment approval
- Layer 2b — reference standards: governing contract standard for each
  contract type identified in Layer 1 (if ingested) — for payment
  certification timing, variation valuation basis, and retention
  release provisions

**Domain:** Financial & Accounting SME

**Invoked by:** Financial & Reporting Orchestrator

---

## When to apply this skill

Apply when a query requires reconciliation of the financial account for
one or more contracts in the warehouse: confirming whether the contracted
sum plus approved variations is consistent with the amounts invoiced or
certified, whether certified amounts have been paid, and whether the
project cost report reflects the aggregate of all contract accounts.

Apply when the Financial Orchestrator or an audit query requires
verification that the project's reported financial position is
arithmetically consistent across all contractual instruments — not
just the main contract.

Apply when a query asks whether a three-way match exists between: (a)
the contracted and varied scope; (b) the amounts invoiced or certified;
and (c) the amounts paid and recorded in the cost report.

Do not apply for: assessment of whether specific payment certificates
were issued correctly under the contract (Commercial Orchestrator scope);
assessment of the cost control system quality (route to
`cost_control_assessment.md`); or assessment of compliance with
financial reporting standards (route to
`financial_reporting_compliance.md`).

---

## Before you begin

Read the Financial Orchestrator findings and Commercial Orchestrator
findings before proceeding. From those findings extract:
- The approved contract sum and latest certified amount for the main
  contract — already established by the Commercial Orchestrator
- Any payment disputes or deductions already identified
- The overall budget vs actual position established by the Financial
  Orchestrator

Do not re-derive figures the orchestrators have already confirmed.
This skill reconciles across all contracts — it does not re-examine
the main contract payment position in isolation.

### Layer 1 documents to retrieve

Call `search_chunks` and `get_related_documents` to retrieve, for
each contract in the warehouse:
- The contract document — to establish the original contracted sum,
  payment terms, retention provisions, and variation mechanism
- All variation orders, change orders, or supplemental agreements —
  to establish the current approved contract sum
- Payment applications or invoices submitted under each contract
- Payment certificates or payment notices issued under each contract
- Payment records — bank confirmations, remittance advice, or
  equivalent — confirming amounts actually paid
- Retention records — amounts deducted and any amounts released
- The project cost report — to reconcile contract-level accounts
  against the aggregate project financial position

**If a contract document exists in the warehouse but its payment
records are absent:** Proceed with what is retrieved. Flag the gap.
Do not assume payment was made.

**If no contract documents are retrieved:** State CANNOT ASSESS —
no contract documents found in the warehouse. Do not proceed.

### Layer 2a documents to retrieve

Call `search_chunks` with `layer_type = '2a'` to retrieve:
- Accounts payable and receivable procedures — required matching
  process between invoice, certification, and payment
- Three-way matching requirements — whether internal policy requires
  purchase order, delivery confirmation, and invoice to be matched
  before payment approval
- DOA matrix — authority levels for payment approval by value

**If Layer 2a not retrieved:** State CANNOT CONFIRM — INTERNAL POLICY
NOT RETRIEVED. Proceed with Layer 1 reconciliation only. Flag that
compliance with internal accounts procedures cannot be assessed.

### Layer 2b documents to retrieve

After identifying the contract form for each contract in Layer 1,
call `search_chunks` with `layer_type = '2b'` to retrieve the
payment certification timing, variation valuation basis, and retention
release provisions for each contract type. Query by subject matter —
not by clause number.

If the governing standard for a contract type is not in Layer 2b:
record as CANNOT CONFIRM — STANDARD NOT IN WAREHOUSE for that
contract type. Proceed with Layer 1 documents only for that contract.

---

## Analysis workflow

### Step 1 — Identify all contracts in the warehouse

List every contract-type instrument retrieved from Layer 1:
- Main contract — parties, contract sum, date
- Subcontracts — parties, contracted scope, contract sum, date
- Consultancy agreements — parties, contracted scope, fee, date
- Purchase orders — supplier, scope, value, date
- Task orders — contractor, scope, value, date

For each instrument: state the original contracted sum and the current
approved contract sum (original plus all approved variations) from
retrieved documents.

If a contract is referenced in the cost report or payment records but
its contract document is not in the warehouse: flag as CANNOT CONFIRM
— CONTRACT DOCUMENT NOT RETRIEVED for that instrument. State what
payment records exist without a matching contract document.

### Step 2 — Reconcile the contract account for each instrument

For each contract identified in Step 1, perform the following
reconciliation from retrieved documents:

**Account structure:**
```
Original contract sum:           [from retrieved contract document]
Approved variations to date:     [from retrieved variation register]
Current approved contract sum:   [original + approved variations]

Amount invoiced or applied for:  [from retrieved payment applications
                                  or invoices — cumulative to date]
Amount certified or approved:    [from retrieved payment certificates
                                  or payment approvals — cumulative]
Amount paid:                     [from retrieved payment records —
                                  cumulative to date]
Retention deducted:              [from retrieved records]
Retention released:              [from retrieved records]
Net retention held:              [deducted minus released]
Outstanding balance (certified
but not paid):                   [certified minus paid]
```

For each figure: state the source document and reference.
Where a figure cannot be confirmed from retrieved documents: state
CANNOT CONFIRM and identify the missing document.

### Step 3 — Identify reconciliation gaps

For each contract account:

**Variation gap:** Is the sum of approved variations in the retrieved
variation register consistent with the variation total in the current
approved contract sum? If there is a discrepancy: identify the
unaccounted variation from retrieved documents.

**Certification gap:** Is the amount certified consistent with the
amount invoiced or applied for? If less was certified than applied for:
identify the deduction from retrieved documents. If no certification
document was retrieved: flag as CANNOT CONFIRM.

**Payment gap:** Is the amount paid consistent with the amount certified?
If certified amounts have not been paid: state the outstanding balance,
the certification date, and the applicable payment timing provision
retrieved from Layer 2b. If the payment timing provision was not
retrieved: state CANNOT CONFIRM — payment timing compliance cannot
be assessed.

**Retention gap:** Is the retention deducted consistent with the
retention percentage and cap stated in the retrieved contract document?
If retention has been deducted beyond the contractual cap: flag. If
retention has been released without a retrieved release trigger being
met: flag.

### Step 4 — Reconcile contract accounts to project cost report

From the retrieved project cost report:
- Does the aggregate of all contract account totals (approved contract
  sums, variations, amounts paid) reconcile to the cost report figures?
- Are all contract instruments separately identified in the cost report,
  or are some aggregated or omitted?
- Is the cost report figure for each contract consistent with the
  independently reconciled account in Step 2?

State any discrepancy between the contract-level reconciliation and
the project cost report. A discrepancy indicates either an error in
cost allocation, an unrecorded payment, or an unrecorded contract
instrument. State the finding from retrieved documents only.

### Step 5 — Assess three-way matching compliance

From retrieved Layer 2a accounts payable procedure:
- Does internal policy require a three-way match between: (a) purchase
  order or contract; (b) delivery confirmation, progress certificate,
  or service acceptance; and (c) invoice or payment application?
- For each payment made under each contract: is the three-way match
  evidenced in the retrieved documents?
- Where payment was made without a matching certification or acceptance
  record: flag as a potential internal control deficiency.

CANNOT ASSESS if Layer 2a policy was not retrieved. Proceed with the
Layer 1 reconciliation and flag the Layer 2a gap.

### Step 6 — Assess payment authority compliance

For each payment identified in Step 2: was the payment approved at
the correct authority level under the retrieved DOA framework? Where
a payment value exceeds a DOA threshold that requires escalated
approval: invoke `doa_compliance.md` for that transaction.

CANNOT CONFIRM payment authority compliance if the DOA matrix was not
retrieved from Layer 2a.

---

## Classification and decision rules

**GREEN:** All contract accounts reconcile — variation registers,
certification records, and payment records are consistent; cost report
reflects the aggregate of all contract accounts; three-way matching
evidenced; payment authority confirmed.

**AMBER:** One or more reconciliation gaps identified — discrepancy
between variation register and approved contract sum; certified amounts
not consistent with cost report; retention inconsistency; one or more
contracts without complete payment records; Layer 2a not retrieved.

**RED:** Material unreconciled discrepancy — payment made without
a retrieved certification or contract instrument; cost report materially
inconsistent with contract account aggregate; payment made in excess
of certified amount without a retrieved authorisation.

**GREY:** No contract documents or payment records retrieved — account
reconciliation cannot be performed from the warehouse.

---

## When to call tools

- Call `search_chunks` to retrieve contract documents, payment
  applications, certificates, and payment records from Layer 1
- Call `search_chunks` with `layer_type = '2a'` for internal accounts
  procedures and DOA matrix
- Call `search_chunks` with `layer_type = '2b'` for payment timing
  and retention provisions under each contract type
- Call `get_related_documents` when retrieved chunks indicate a payment
  certificate or contract document exists — retrieve the full document
- Invoke `doa_compliance.md` for any payment requiring authority
  confirmation under the retrieved DOA framework
- Always call tools before concluding any document is absent

---

## Always flag — regardless of query

- **Payment made without retrieved certification** — when payment
  records show an amount paid under a contract with no corresponding
  payment certificate or acceptance record in the warehouse
- **Approved contract sum inconsistent with variation register** — when
  the sum of retrieved variations does not reconcile to the current
  contract sum stated in retrieved cost or payment records
- **Cost report does not reflect all contract instruments** — when a
  contract, PO, or task order in the warehouse is absent from the
  project cost report
- **Outstanding certified amounts unpaid beyond contractual timing** —
  when payment timing provision is retrieved and payment records show
  non-payment beyond that period
- **Retention deducted inconsistent with contract provisions** — when
  deduction exceeds contractual cap or release has occurred without
  retrieved trigger being met
- **Three-way match absent** — when payment was made without a
  retrievable purchase order, certification, and invoice match
- **Contract instrument without a contract document in warehouse** —
  when cost or payment records reference a contract whose document
  has not been retrieved

---

## Output format

```
## Multi-Contract Account Reconciliation

### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [standard name per contract type — or NOT RETRIEVED]
Layer 2b provisions retrieved: [payment timing, variation valuation,
  retention — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE]
Layer 2a source: [policy name — or NOT RETRIEVED / NOT APPLICABLE]
Layer 1 primary document: [list all contract documents retrieved]
Layer 1 amendment document: [variation orders and supplemental
  agreements — or NOT RETRIEVED / NONE]
Provisions CANNOT CONFIRM: [list — or NONE]

### Documents Retrieved (Layer 1)
[Every retrieved contract document, variation register, payment
application, certificate, and payment record — with reference and date]

### Documents Not Retrieved
[Every required document absent — which steps are affected.
If nothing missing: "None."]

### Layer 2b Reference
[Retrieved standards and relevant provisions per contract type — or:
CANNOT CONFIRM — [standard name] NOT IN WAREHOUSE]

### Contract Inventory
[List of all contract instruments identified in the warehouse —
type, parties, original sum, current approved sum]

### Contract Account Reconciliations
[For each contract:]
[Contract name/reference]
Original sum: [amount — source]
Approved variations: [amount — source]
Current approved sum: [amount]
Invoiced/applied: [amount — source]
Certified/approved: [amount — source]
Paid: [amount — source]
Retention held: [amount — source]
Outstanding (certified not paid): [amount]
Reconciliation status: [RECONCILED / GAP IDENTIFIED — describe gap /
  CANNOT CONFIRM — state missing document]

### Cost Report Reconciliation
[GREEN / AMBER / RED / GREY / CANNOT ASSESS]
[Comparison of contract account aggregate to project cost report.
State any discrepancy and its possible cause from retrieved documents.]

### Three-Way Matching Assessment
[GREEN / AMBER / RED / GREY / CANNOT ASSESS]
[Finding — state whether internal policy was retrieved and whether
matching is evidenced for payments in retrieved records]

### Payment Authority Assessment
[GREEN / AMBER / RED / GREY / CANNOT ASSESS]
[Per payment requiring DOA confirmation — state outcome from
doa_compliance.md or CANNOT CONFIRM if DOA not retrieved]

### FLAGS
FLAG: [finding] — [forensic implication in one sentence]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
*(Confidence scale: GREEN = all required evidence retrieved and findings
fully supported | AMBER = Layer 2b not retrieved or amendment position
unknown -- findings provisional | RED = critical document absent --
findings materially constrained | GREY = standard form unconfirmed --
form-specific analysis suspended. Full definition:
skills/c1-skill-authoring/references/grounding_protocol.md)*
Summary: [two to three sentences — retrieved facts only]
```

---

## Domain knowledge and standards

A project account is the financial consequence of its contractual
instruments. Reconciliation proceeds contract by contract from the
retrieved documents — not from the cost report downward. Where a
contract type's governing standard is not in Layer 2b, payment timing
and retention compliance cannot be assessed against the standard form;
the Layer 1 contract document terms govern instead. Three-way matching
and payment authority assessment require Layer 2a retrieval — without
it, internal control compliance cannot be confirmed. The agent does not
calculate figures — it reconciles what retrieved documents show.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies
to any contract form. All characterisations grounded in retrieved warehouse
documents only.*
