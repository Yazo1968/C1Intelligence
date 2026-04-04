# Key Dates and Securities

**Skill type:** Mixed
- Contract-type-agnostic: the requirement to extract dates, periods,
  and security parameters from retrieved project documents, and to
  flag contradictions, absences, and anomalies
- Contract-type-specific: which documents contain these parameters
  differs by standard form; the completion certificate and defects
  period mechanisms differ by standard form and version
**Layer dependency:**
- Layer 1 — project documents: Contract Data / Appendix to Tender or
  equivalent schedule; Contract Agreement; any amendments; completion
  certificate (if issued); defects certificate (if issued); security
  instruments (bonds, guarantees); the commencement notice or notice to
  proceed; progress reports
- Layer 2b — reference standards: Governing standard form provisions
  for completion, defects period, and securities (whatever form is
  in the warehouse)
**Domain:** Legal & Contractual SME
**Invoked by:** Legal orchestrator

---

## When to apply this skill

Apply when a query concerns contractual dates, milestones, time periods,
or security instruments — including Commencement Date, Time for
Completion, Defects Notification Period or equivalent, milestone dates,
sectional completion, performance bonds, advance payment guarantees,
retention, and parent company guarantees. Also apply when assessing
whether a security instrument is current, correctly stated, for the
correct amount, or at risk of expiry.

---

## Before you begin

### Foundational requirements
Read contract_assembly findings first.

From contract_assembly:
- Confirmed standard form and version
- Confirmed source of key parameters (Contract Data, Appendix to Tender,
  Contract Agreement, or equivalent)
- Amendment provisions affecting time periods or security instruments
- Any supplemental agreements that may have modified original dates

**If standard form is UNCONFIRMED:** Proceed with extraction but flag
that version-specific analysis (completion certificate triggers, defects
period mechanism) cannot be applied without a confirmed standard form.

From notice_and_instruction_compliance:
- Commencement Date position — was a formal commencement notice issued
  and when?

From engineer_identification:
- Identity of the contract administrator — relevant to who issued the
  completion certificate and defects certificate.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- Contract Data, Appendix to Tender, or equivalent schedule —
  primary source of all dates and security parameters
- Contract Agreement — cross-check for key parameters
- Formation document — may state or confirm dates
- Any amendments or supplemental agreements modifying original dates
- Commencement notice or Notice to Proceed
- Completion certificate (if issued)
- Defects certificate or Performance Certificate (if issued)
- Performance bond / Performance Security instrument
- Advance Payment Guarantee instrument
- Retention release correspondence
- Parent company guarantee (if applicable)

**If the Contract Data / Appendix to Tender or equivalent is not retrieved:**
State CANNOT CONFIRM any contractual date, period, or security
parameter. Do not extract from any secondary source without
flagging the source hierarchy issue.

**If a security instrument is not retrieved:**
State CANNOT CONFIRM the terms, amount, validity period, or form
of that security instrument.

**For each date or parameter extracted:** State the source document
and its reference number. Do not state any value without a source.

### Layer 2b documents to retrieve (reference standards)

After confirming standard form, call `search_chunks` with
`layer_type = '2b'` to retrieve:
- The completion certificate provision for the confirmed standard form
  (search by subject matter: "completion taking over certificate works
  substantial completion")
- The defects period provision (search by subject matter: "defects
  notification period liability rectification certificate")
- The performance security provision (search by subject matter:
  "performance security bond amount reduction")
- The retention provision if in scope (search by subject matter:
  "retention release trigger payment")

**Purpose:** To establish the structural framework for assessing
whether the completion and defects mechanisms, and security provisions,
have operated correctly. The specific periods and amounts are in
Layer 1 — Layer 2b provides the framework for interpreting them.

**If the governing standard form is not retrieved from Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE for the
completion and security provisions. Do not describe these provisions
from training knowledge.

---

## Analysis workflow

### Step 1 — Extract all contractual dates and periods
*Contract-type-agnostic*

From the retrieved Contract Data, Appendix to Tender, or equivalent,
extract and record each of the following. For every item: state the
source document, the clause reference within that document, and the
value as stated. Do not calculate, convert, or adjust any value.

- Commencement Date (or the period within which it must occur)
- Time for Completion — overall, and per section if sectional
  completion is stated in the retrieved documents
- Milestone dates — only if stated in retrieved contract documents
  or an incorporated programme
- Defects Notification Period or equivalent — as stated in retrieved
  documents
- Period for Performance Security validity — as stated
- Period for Advance Payment Guarantee validity — as stated if applicable
- Retention percentage — as stated
- Retention first release trigger and amount — as stated
- Retention second release trigger and amount — as stated
- Any other time-limited obligation stated in the retrieved documents

**Cross-check:** If the same parameter appears in both the Contract
Data and the Contract Agreement with different values: flag the
contradiction immediately. Apply the order of precedence from
contract_assembly findings — if unconfirmed: state CANNOT DETERMINE
which value governs.

**If a parameter is not found in any retrieved document:**
State NOT FOUND IN RETRIEVED DOCUMENTS for that parameter. Do not
estimate, calculate, or apply any default.

### Step 2 — Confirm the actual Commencement Date
*Contract-type-agnostic*

The contractual Commencement Date triggers the Time for Completion
countdown. It may not be the date stated in the Contract Data —
it is the date on which commencement actually occurred per the
contract mechanism.

From the retrieved documents, identify:
- Whether a formal commencement notice was issued — retrieve it;
  state the date
- Whether any conditions precedent to commencement (site access,
  advance payment, bond submission) are stated in the retrieved
  contract documents and whether they were satisfied

**Do not calculate the commencement date.** State only what the
retrieved documents show. If the commencement notice has not been
retrieved: state CANNOT CONFIRM the actual Commencement Date from
the warehouse documents.

**If commencement was delayed:** State what the retrieved documents
show about the delay and its cause. Do not characterise the delay
as an employer or contractor event without retrieved evidence.

### Step 3 — Assess time extension history and adjusted completion date
*Contract-type-agnostic*

From the retrieved documents, identify:
- Any time extension claims submitted
- Any time extension granted — by determination or agreement
- The cumulative time extension granted (if determinable from
  retrieved documents)
- The adjusted contractual completion date (original date plus
  confirmed extension) — state only if both inputs are confirmed
  from retrieved documents

**Do not calculate an adjusted completion date unless both inputs
are confirmed from retrieved documents.**

Assess agreed damages exposure only from confirmed values:
- Original or adjusted completion date: from retrieved documents
- Actual completion date (from retrieved completion certificate)
- Agreed damages rate: from retrieved contract documents only
- Agreed damages cap: from retrieved documents only

**Do not calculate agreed damages liability.** State the inputs
confirmed from retrieved documents and flag any unconfirmed input.

### Step 4 — Assess completion certificate status
*Contract-type-specific*

From the retrieved documents:
- Has a completion certificate been issued? Retrieve it.
- If issued: state the date, issuing entity, and what was certified
  as complete (whole of works, section, or part)
- If issued: retrieve the defects period provision from Layer 2b to
  confirm what triggers the defects period countdown; check whether
  the amendment document modifies this
- If not issued: are there retrieved documents indicating the works
  are complete but the certificate has not been issued?

**If no completion certificate has been retrieved:** State CANNOT
CONFIRM completion certificate status. Do not assume the works are
complete or incomplete.

### Step 5 — Assess defects certificate status
*Contract-type-agnostic*

From the retrieved documents:
- Has a defects certificate or equivalent end-of-defects-period
  document been issued? Retrieve it.
- If issued: state the date and issuing entity
- If not issued: has the defects period expired based on retrieved
  dates? If both the completion certificate date and the defects
  period duration are confirmed from retrieved documents, and the
  resulting expiry date has passed: flag that the certificate may
  be overdue. State the basis from retrieved documents only.

**If the defects period has not been confirmed from retrieved
documents:** State CANNOT DETERMINE whether the certificate is overdue.

### Step 6 — Assess security instruments
*Contract-type-agnostic*

For each security instrument in the warehouse, assess:

**(a) Performance bond / Performance Security:**
- Issuing bank or surety: from retrieved instrument
- Amount: from retrieved instrument (state as retrieved — do not
  compare to a required amount unless that requirement is also
  confirmed from a retrieved document)
- Expiry date: from retrieved instrument
- Form: on-demand / conditional — from retrieved instrument
- Whether the required amount matches the contract requirement:
  only if both the bond amount AND the required percentage are
  confirmed from retrieved documents
- Whether the bond is current: compare expiry date to the project
  status established from retrieved documents only

**(b) Advance Payment Guarantee:**
Same framework as Performance Security. In addition: confirm the
advance payment amount from retrieved documents and whether the
guarantee amount reduces as the advance is recovered — only if the
mechanism is stated in the retrieved documents.

**(c) Retention:**
State the retention amounts as found in retrieved payment certificates
or financial records. Retrieve the release trigger from Layer 2b and
confirm any amendment from the amendment document. Do not calculate
retention amounts — extract from retrieved documents.

**(d) Parent company guarantee:**
Identify from retrieved documents. Note the issuing entity and
the obligations guaranteed.

**For any security instrument not retrieved:**
State NOT FOUND IN WAREHOUSE DOCUMENTS. Do not assess form or
adequacy of an instrument that has not been retrieved.

---

## Classification and decision rules

**Contractual dates:**

Date confirmed from retrieved Contract Data or Contract Agreement →
CONFIRMED — state value and source
Date found only in secondary documents (correspondence, progress
reports) → FOUND IN NON-PRIMARY DOCUMENTS — state value, source,
and note that primary source not retrieved
Date not found in any retrieved document → NOT FOUND IN RETRIEVED
DOCUMENTS — do not state a value

**Contradiction between documents:**

Same date/value in two retrieved documents at different hierarchy
levels → STATE BOTH — state which governs per confirmed precedence
or state CANNOT DETERMINE if precedence unconfirmed
Same date/value in two retrieved documents at same level →
CONTRADICTION — flag RED; state both values; cannot be resolved
from retrieved documents

**Completion certificate:**

Certificate retrieved → ISSUED — state date and scope
Not retrieved after searching → NOT FOUND IN WAREHOUSE — cannot
confirm completion status

**Defects certificate:**

Certificate retrieved → ISSUED — state date
Not retrieved AND defects period expiry confirmed from retrieved
dates → POTENTIALLY OVERDUE — flag; state the basis
Not retrieved AND defects period status unknown →
NOT FOUND IN WAREHOUSE — cannot confirm issuance status

**Security instruments:**

Instrument retrieved and within its stated validity period →
CURRENT — state expiry date and source
Instrument retrieved and past its stated expiry date → EXPIRED —
flag; state expiry date and source
Instrument not retrieved → NOT FOUND IN WAREHOUSE

---

## When to call tools

**Signal:** Contract Data or equivalent has not been retrieved and
key dates cannot be confirmed
**Action:** `search_chunks` with query "contract data appendix
tender time completion commencement date"; `get_related_documents`
with document type "Contract Data" or "Appendix to Tender"
**Look for:** The primary source of contractual dates and periods

**Signal:** A completion certificate is referenced in correspondence
but not retrieved
**Action:** `get_related_documents` with document type "Completion
Certificate" or "Taking-Over Certificate"; `search_chunks` with
query "completion certificate date"
**Look for:** The completion certificate document

**Signal:** A performance bond or other security instrument is
referenced in the Contract Agreement but not retrieved
**Action:** `get_related_documents` with document types "Performance
Bond", "Performance Security", "Advance Payment Guarantee",
"Parent Company Guarantee"
**Look for:** The instrument itself

**Signal:** Time extension has been claimed but no award or
determination has been retrieved
**Action:** `get_related_documents` with document type "Determination";
`search_chunks` with query "time extension granted awarded
determination"
**Look for:** Any document recording a granted time extension

**Signal:** Layer 2b completion, defects period, or security
provisions have not been retrieved
**Action:** `search_chunks` with `layer_type = '2b'` and query
"[standard form name] [provision subject]"
**Look for:** Standard form text for structural comparison

---

## Always flag — regardless of query

1. **Contract Data or equivalent not retrieved** — flag immediately;
   state that all date and security analysis is affected.

2. **Contradiction in key parameters between retrieved documents** —
   flag any contradiction in Time for Completion, agreed damages rate,
   defects period, or security amounts; state both values and sources.

3. **Completion certificate outstanding where works appear complete** —
   if retrieved records indicate completion but no certificate has been
   found, flag; state the forensic implication (defects period not
   started, agreed damages position unclear, retention not released).

4. **Defects certificate outstanding where defects period appears to
   have expired** — flag; state the period end date as derived from
   retrieved documents only.

5. **Security instrument expired or approaching expiry** — flag any
   instrument whose retrieved expiry date has passed or is within
   30 days, based on project status from retrieved documents only.

6. **Security amount not confirmed** — if the bond or guarantee amount
   cannot be compared to the required amount because the required
   percentage is not in a retrieved document: flag the gap; do not
   state whether the security amount is adequate.

7. **Governing standard not retrieved from Layer 2b** — flag when the
   completion or security provisions could not be retrieved; state what
   standard would need to be ingested to enable full analysis.

---

## Output format

```
## Key Dates and Securities Assessment

### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [standard form name — or NOT RETRIEVED]
Layer 2b provisions retrieved: [description — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE]
Layer 2a source: [policy name — or NOT RETRIEVED / NOT APPLICABLE]
Layer 1 primary document: [name and reference — or NOT RETRIEVED]
Layer 1 amendment document: [name — or NOT RETRIEVED / NOT APPLICABLE]
Provisions CANNOT CONFIRM: [list — or NONE]

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required for this analysis not found in the
warehouse. State which parameters cannot be confirmed as a result.]

### Layer 2b Reference Retrieved
[State whether the completion, defects period, and security provisions
for the confirmed standard form were retrieved from Layer 2b. If not:
state CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE and list
which analysis steps are affected.]

### Contractual Dates and Periods
[For each item — state value, source document, and source clause.
If not found: state NOT FOUND IN RETRIEVED DOCUMENTS.]

| Parameter | Value | Source document | Source clause | Status |
|---|---|---|---|---|
| Commencement Date (contractual) | | | | [CONFIRMED/NOT FOUND] |
| Actual Commencement Date | | | | [CONFIRMED/NOT FOUND] |
| Time for Completion | | | | [CONFIRMED/NOT FOUND] |
| Sectional completion (if any) | | | | [CONFIRMED/N/A/NOT FOUND] |
| Defects period | | | | [CONFIRMED/NOT FOUND] |
| [Other parameters as applicable] | | | | |

### Contradictions in Dates/Parameters
[List any contradiction found, or "None identified in retrieved documents."]

### Time Extension History and Adjusted Completion Date
Time extension claimed: [value from retrieved claim documents / NOT FOUND]
Time extension granted: [value from retrieved determination or agreement / NOT FOUND]
Adjusted completion date: [calculated from confirmed values only /
CANNOT CALCULATE — state which input is unconfirmed]
Agreed damages inputs confirmed from retrieved documents:
  Original/adjusted completion date: [confirmed value and source / NOT CONFIRMED]
  Actual completion date: [from retrieved completion certificate / NOT CONFIRMED]
  Agreed damages rate: [confirmed value and source / NOT CONFIRMED]
  Agreed damages cap: [confirmed value and source / NOT CONFIRMED]
Agreed damages exposure: CANNOT CALCULATE — state which inputs are unconfirmed

### Completion Certificate
Status: [ISSUED — date and scope / NOT FOUND IN WAREHOUSE]
Source: [document reference]
Defects period triggered: [YES — start date from certificate date and
confirmed defects period / CANNOT CONFIRM — certificate not retrieved /
CANNOT CONFIRM — defects period not retrieved from Layer 2b]

### Defects Certificate
Status: [ISSUED — date / NOT FOUND IN WAREHOUSE]
Source: [document reference]
Defects period expiry: [calculated from confirmed values only / CANNOT CALCULATE]
Certificate overdue: [YES — state basis from retrieved docs /
CANNOT ASSESS — defects period or completion certificate date not confirmed]

### Security Instruments

**Performance Security / Bond**
Retrieved: [YES / NO — NOT FOUND IN WAREHOUSE]
Issuing entity: [from retrieved instrument / CANNOT CONFIRM]
Amount: [from retrieved instrument / CANNOT CONFIRM]
Required amount: [from retrieved contract documents / CANNOT CONFIRM]
Adequacy: [CONFIRMED ADEQUATE / SHORTFALL / CANNOT ASSESS — required amount not retrieved]
Form: [on-demand / conditional — from retrieved instrument / CANNOT CONFIRM]
Expiry date: [from retrieved instrument / CANNOT CONFIRM]
Status: [CURRENT / EXPIRED / APPROACHING EXPIRY / CANNOT CONFIRM]

**Advance Payment Guarantee**
[Same structure, or NOT APPLICABLE]

**Retention**
Retention percentage: [from retrieved contract documents / CANNOT CONFIRM]
First release trigger: [from retrieved Layer 2b provision and amendment document / CANNOT CONFIRM]
Second release trigger: [from retrieved Layer 2b provision and amendment document / CANNOT CONFIRM]
Current retention position: [from retrieved payment certificates / NOT FOUND]

**Parent Company Guarantee**
[Instrument summary if retrieved, or NOT FOUND IN WAREHOUSE]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any period, amount, or trigger from
this section without first confirming it from retrieved project documents.*

**Security provisions — analytical reference:**
Most standard forms require performance security to be maintained until
a defects or performance certificate is issued. The required amount is
stated in the contract data — retrieve from Layer 1. Advance payment
guarantees typically reduce as the advance is recovered — the recovery
mechanism is in the contract. These are structural frameworks for
interpretation — all values and trigger events must come from retrieved
documents.

**Completion and defects period — analytical reference:**
Most standard forms have a two-stage process: a completion or
taking-over certificate that transfers risk and starts the defects
period, followed by a defects certificate or performance certificate
that ends the defects period and releases final retention. The duration
of the defects period is stated in the contract data — retrieve from
Layer 1. The mechanism may be amended by the project's amendment
document — always check. Do not assume any period or trigger event
without retrieved document confirmation.

**Security instrument forms — analytical reference:**
Security instruments in construction contracts are typically either
on-demand (callable without proof of breach) or conditional (requiring
proof of breach before calling). The form is stated in the instrument —
retrieve from Layer 1 to confirm. Do not assume the form from the
standard form alone.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies to
any contract form. All characterisations grounded in retrieved warehouse
documents only.*
