# Key Dates and Securities

**Skill type:** Mixed
- Contract-type-agnostic: the requirement to extract dates, periods,
  and security parameters from retrieved project documents, and to
  flag contradictions, absences, and anomalies
- Contract-type-specific: which documents contain these parameters
  differs by book (Appendix to Tender vs Contract Data vs negotiated
  agreement); the Taking-Over Certificate and Performance Certificate
  mechanisms differ by book and edition
**Layer dependency:**
- Layer 1 — project documents: Contract Data / Appendix to Tender;
  Contract Agreement; any amendments; the Taking-Over Certificate;
  the Performance Certificate; security instruments (bonds, guarantees);
  the Notice to Proceed or Commencement notice; progress reports
- Layer 2 — reference standards: FIDIC clauses governing commencement,
  completion, DNP, and securities for the confirmed book and edition
**Domain:** Legal & Contractual SME
**Invoked by:** Legal orchestrator

---

## When to apply this skill

Apply when a query concerns contractual dates, milestones, time
periods, or security instruments — including Commencement Date, Time
for Completion, Defects Notification Period, milestone dates, sectional
completion, performance bonds, advance payment guarantees, retention,
and parent company guarantees. Also apply when assessing whether a
security instrument is current, correctly stated, for the correct
amount, or at risk of expiry.

---

## Before you begin

### Foundational requirements
Read contract_assembly findings first.

From contract_assembly:
- Confirmed book type and edition
- Confirmed source of key parameters (Contract Data / Appendix to
  Tender / Contract Agreement)
- Particular Conditions amendments affecting time periods or security
  instruments
- Any supplemental agreements that may have modified original dates

**If book type is UNCONFIRMED:** Proceed with extraction but flag
that edition-specific analysis (Taking-Over, DNP trigger) cannot
be applied without confirmed book type.

From notice_and_instruction_compliance:
- Commencement Date position — was a formal Notice to Proceed or
  Commencement notice issued and when?

From engineer_identification:
- Identity of the Engineer or Employer's Representative — relevant
  to who issued the Taking-Over Certificate and Performance Certificate

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- Contract Data or Appendix to Tender — primary source of all dates
  and security parameters
- Contract Agreement — cross-check for key parameters
- Letter of Acceptance (Red/Yellow) — may state or confirm dates
- Any amendments or supplemental agreements modifying original dates
- Notice to Proceed or Commencement Date notice
- Taking-Over Certificate (if issued)
- Performance Certificate (if issued)
- Performance bond / Performance Security instrument
- Advance Payment Guarantee instrument
- Retention release correspondence
- Parent company guarantee (if applicable)

**If the Contract Data / Appendix to Tender is not retrieved:**
State CANNOT CONFIRM any contractual date, period, or security
parameter. Do not extract from any secondary source without
flagging the source hierarchy issue.

**If a security instrument is not retrieved:**
State CANNOT CONFIRM the terms, amount, validity period, or form
of that security instrument.

**For each date or parameter extracted:** State the source document
and its reference number. Do not state any value without a source.

### Layer 2 documents to retrieve (reference standards)

After confirming book type, call `search_chunks` to retrieve from
Layer 2:
- FIDIC clause governing the Taking-Over Certificate for the
  confirmed book and edition (Clause 10.1)
- FIDIC clause governing the Performance Certificate
- FIDIC clause governing the Performance Security (Clause 4.2)
- FIDIC clause governing retention (Clause 14.9) if retention is
  in scope

**Purpose:** To establish the structural framework for assessing
whether the Taking-Over and Performance Certificate mechanisms, and
security provisions, have operated correctly. The specific periods
and amounts are in Layer 1 — Layer 2 provides the framework for
interpreting them.

---

## Analysis workflow

### Step 1 — Extract all contractual dates and periods
*Contract-type-agnostic*

From the retrieved Contract Data or Appendix to Tender, extract and
record each of the following. For every item: state the source
document, the clause reference within that document, and the value
as stated. Do not calculate, convert, or adjust any value.

- Commencement Date (or the period within which it must occur) —
  as stated in the retrieved Contract Data
- Time for Completion — overall, and per section if sectional
  completion is stated in the retrieved documents
- Milestone dates — only if stated in retrieved contract documents
  or an incorporated programme
- Defects Notification Period — as stated in retrieved Contract Data
- Period for Performance Security validity — as stated in retrieved
  documents
- Period for Advance Payment Guarantee validity — as stated if
  applicable
- Retention percentage — as stated in retrieved documents
- Retention first release trigger and amount — as stated
- Retention second release trigger and amount — as stated
- Any other time-limited obligation stated in the retrieved Contract
  Data

**Cross-check:** If the same parameter appears in both the Contract
Data and the Contract Agreement with different values: flag the
contradiction immediately. Apply the order of precedence from
contract_assembly findings to identify which governs — if order of
precedence is unconfirmed: state CANNOT DETERMINE which value governs.

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
- Whether a formal Notice to Proceed or Engineer's Commencement
  notice was issued — retrieve it; state the date
- Whether any conditions precedent to commencement (site access,
  advance payment, bond submission) are stated in the retrieved
  contract documents and whether they were satisfied

**Do not calculate the commencement date.** State only what the
retrieved documents show. If the Notice to Proceed has not been
retrieved: state CANNOT CONFIRM the actual Commencement Date from
the warehouse documents. Note that the date in the Contract Data
may be the stated contractual date but actual commencement may
differ — this gap cannot be resolved without the notice.

**If commencement was delayed:** State what the retrieved documents
show about the delay and its cause. Do not characterise the delay
as an Employer or Contractor event without retrieved evidence.

### Step 3 — Assess EOT history and adjusted completion date
*Contract-type-agnostic*

From the retrieved documents, identify:
- Any EOT claims submitted — retrieve from the warehouse
- Any EOT granted — by Engineer determination or agreement
- The cumulative EOT granted (if determinable from retrieved
  documents)
- The adjusted contractual completion date (original date plus
  confirmed EOT) — state only if both the original date and the
  granted EOT are confirmed from retrieved documents

**Do not calculate an adjusted completion date unless both inputs
are confirmed from retrieved documents.** If either is unconfirmed:
state CANNOT CALCULATE adjusted completion date.

Assess LD exposure only from confirmed values:
- Original or adjusted completion date: from retrieved documents
- Actual completion date (from Taking-Over Certificate if retrieved)
- LD rate: from retrieved Contract Data only
- LD cap: from retrieved Contract Data or Particular Conditions only

**Do not calculate LD liability.** State the inputs confirmed from
retrieved documents and flag any input that is unconfirmed.

### Step 4 — Assess Taking-Over Certificate status
*Contract-type-specific*

From the retrieved documents:
- Has a Taking-Over Certificate (TOC) been issued? Retrieve it.
- If issued: state the date, issuing entity, and what was taken over
  (whole of Works, section, or part)
- If issued: does the TOC date trigger the DNP countdown? — confirm
  the DNP trigger from the retrieved Particular Conditions; if PC not
  retrieved: state CANNOT CONFIRM the trigger mechanism
- If not issued: are there retrieved documents indicating the Works
  are complete but the TOC has not been issued?

**If no TOC has been retrieved:** State CANNOT CONFIRM TOC status.
Do not assume the Works are complete or incomplete.

### Step 5 — Assess Performance Certificate status
*Contract-type-agnostic*

From the retrieved documents:
- Has a Performance Certificate been issued? Retrieve it.
- If issued: state the date and issuing entity
- If not issued: has the DNP period expired based on retrieved dates?
  If both the TOC date and the DNP period are confirmed from retrieved
  documents, and the resulting DNP expiry date has passed: flag that
  the Performance Certificate may be overdue. State the basis for
  this assessment from retrieved documents only.

**If the DNP period has not been confirmed from retrieved documents:**
State CANNOT DETERMINE whether the Performance Certificate is overdue.

### Step 6 — Assess security instruments
*Contract-type-agnostic*

For each security instrument in the warehouse, assess:

**(a) Performance bond / Performance Security:**
- Issuing bank or surety: from retrieved instrument
- Amount: from retrieved instrument (state as retrieved — do not
  compare to a "required" amount unless the required amount is
  also confirmed from a retrieved document)
- Expiry date: from retrieved instrument
- Form: on-demand / conditional — from retrieved instrument
- Whether the required amount matches the contract requirement:
  only if both the bond amount AND the required percentage are
  confirmed from retrieved documents
- Whether the bond is current: compare expiry date to the current
  project status as established from retrieved documents only

**(b) Advance Payment Guarantee:**
Same framework as Performance Security. In addition: confirm the
advance payment amount from the retrieved Contract Data and whether
the guarantee amount reduces as the advance is recovered — only
if the mechanism is stated in the retrieved documents.

**(c) Retention:**
State the retention amounts as found in the retrieved payment
certificates or financial records. Confirm the release trigger
from the retrieved Particular Conditions. Do not calculate
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

**Taking-Over Certificate:**

TOC retrieved → ISSUED — state date and scope
TOC not retrieved after searching → NOT FOUND IN WAREHOUSE — cannot
confirm issuance or completion status

**Performance Certificate:**

Performance Certificate retrieved → ISSUED — state date
Performance Certificate not retrieved AND DNP expiry confirmed from
retrieved dates → POTENTIALLY OVERDUE — flag; state the basis
Performance Certificate not retrieved AND DNP status unknown →
NOT FOUND IN WAREHOUSE — cannot confirm issuance status

**Security instruments:**

Instrument retrieved and within its stated validity period →
CURRENT — state expiry date and source
Instrument retrieved and past its stated expiry date → EXPIRED —
flag; state expiry date and source
Instrument not retrieved → NOT FOUND IN WAREHOUSE

---

## When to call tools

**Signal:** Contract Data or Appendix to Tender has not been retrieved
and key dates cannot be confirmed
**Action:** `search_chunks` with query "contract data appendix tender
time completion commencement date"; `get_related_documents` with
document type "Contract Data" or "Appendix to Tender"
**Look for:** The primary source of contractual dates and periods

**Signal:** A Taking-Over Certificate is referenced in correspondence
but not retrieved
**Action:** `get_related_documents` with document type "Taking-Over
Certificate"; `search_chunks` with query "taking over certificate
completion date"
**Look for:** The Taking-Over Certificate document

**Signal:** A performance bond or other security instrument is
referenced in the Contract Agreement but not retrieved
**Action:** `get_related_documents` with document types "Performance
Bond", "Performance Security", "Advance Payment Guarantee",
"Parent Company Guarantee"
**Look for:** The instrument itself

**Signal:** EOT has been claimed but no EOT award or Engineer's
determination has been retrieved
**Action:** `get_related_documents` with document type "Engineer's
Determination"; `search_chunks` with query "extension of time
granted awarded EOT determination"
**Look for:** Any document recording a granted EOT and the period
awarded

**Signal:** Layer 2 FIDIC clauses for Taking-Over, DNP, or securities
have not been retrieved
**Action:** `search_chunks` with query "[FIDIC book] [edition]
clause [10 / 4.2 / 14.9] [subject]"
**Look for:** Standard FIDIC text for structural comparison

---

## Always flag — regardless of query

1. **Contract Data or Appendix to Tender not retrieved** — flag
   immediately; state that all date and security analysis is affected.

2. **Contradiction in key parameters between retrieved documents**
   — flag any contradiction in Time for Completion, LD rate, DNP,
   or security amounts; state both values and their sources.

3. **Taking-Over Certificate outstanding where Works appear complete**
   — if retrieved records indicate completion but no TOC has been
   found, flag; state the forensic implication (DNP not started,
   LD position unclear, retention not released).

4. **Performance Certificate outstanding where DNP appears to have
   expired** — flag; state the DNP end date as derived from retrieved
   documents only and the consequence of non-issuance.

5. **Security instrument expired or approaching expiry** — flag any
   instrument whose retrieved expiry date has passed or is within
   30 days, based on project status as established from retrieved
   documents only.

6. **Security amount not confirmed** — if the bond or guarantee
   amount cannot be compared to the required amount because the
   required percentage is not in a retrieved document: flag the gap;
   do not state whether the security amount is adequate.

---

## Output format

```
## Key Dates and Securities Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required for this analysis not found in the
warehouse. State which parameters cannot be confirmed as a result.]

### Layer 2 Reference Retrieved
[State whether FIDIC clauses for Taking-Over, DNP, and securities
were retrieved from Layer 2. If not: state analytical knowledge applied.]

### Contractual Dates and Periods
[For each item — state value, source document, and source clause.
If not found: state NOT FOUND IN RETRIEVED DOCUMENTS.]

| Parameter | Value | Source document | Source clause | Status |
|---|---|---|---|---|
| Commencement Date (contractual) | | | | [CONFIRMED/NOT FOUND] |
| Actual Commencement Date | | | | [CONFIRMED/NOT FOUND] |
| Time for Completion | | | | [CONFIRMED/NOT FOUND] |
| Sectional completion (if any) | | | | [CONFIRMED/N/A/NOT FOUND] |
| Defects Notification Period | | | | [CONFIRMED/NOT FOUND] |
| [Other parameters as applicable] | | | | |

### Contradictions in Dates/Parameters
[List any contradiction found, or "None identified in retrieved documents."]

### EOT History and Adjusted Completion Date
EOT claimed: [value from retrieved claim documents / NOT FOUND]
EOT granted: [value from retrieved determination or agreement / NOT FOUND]
Adjusted completion date: [calculated from confirmed values only /
CANNOT CALCULATE — state which input is unconfirmed]
LD inputs confirmed from retrieved documents:
  Original/adjusted completion date: [confirmed value and source / NOT CONFIRMED]
  Actual completion date: [from retrieved TOC / NOT CONFIRMED]
  LD rate: [confirmed value and source / NOT CONFIRMED]
  LD cap: [confirmed value and source / NOT CONFIRMED]
LD exposure: CANNOT CALCULATE — state which inputs are unconfirmed

### Taking-Over Certificate
Status: [ISSUED — date and scope / NOT FOUND IN WAREHOUSE]
Source: [document reference]
DNP triggered: [YES — start date from TOC date and confirmed DNP period /
CANNOT CONFIRM — TOC not retrieved / CANNOT CONFIRM — DNP period not retrieved]

### Performance Certificate
Status: [ISSUED — date / NOT FOUND IN WAREHOUSE]
Source: [document reference]
DNP period expiry: [calculated from confirmed values only / CANNOT CALCULATE]
Performance Certificate overdue: [YES — state basis from retrieved docs /
CANNOT ASSESS — DNP period or TOC date not confirmed]

### Security Instruments

**Performance Security / Bond**
Retrieved: [YES / NO — NOT FOUND IN WAREHOUSE]
Issuing entity: [from retrieved instrument / CANNOT CONFIRM]
Amount: [from retrieved instrument / CANNOT CONFIRM]
Required amount: [from retrieved Contract Data / CANNOT CONFIRM]
Adequacy: [CONFIRMED ADEQUATE / SHORTFALL / CANNOT ASSESS — required amount not retrieved]
Form: [on-demand / conditional — from retrieved instrument / CANNOT CONFIRM]
Expiry date: [from retrieved instrument / CANNOT CONFIRM]
Status: [CURRENT / EXPIRED / APPROACHING EXPIRY / CANNOT CONFIRM]

**Advance Payment Guarantee**
[Same structure, or NOT APPLICABLE]

**Retention**
Retention percentage: [from retrieved Contract Data / CANNOT CONFIRM]
First release trigger: [from retrieved PC / CANNOT CONFIRM]
Second release trigger: [from retrieved PC / CANNOT CONFIRM]
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
this section without first confirming it from retrieved project
documents.*

**FIDIC security provisions — structural summary (analytical reference):**
Under FIDIC (all books, both editions), the Performance Security must
be maintained until the Performance Certificate is issued. The required
amount is stated in the Contract Data — retrieve from Layer 1. The
Advance Payment Guarantee reduces as the advance is recovered — the
recovery mechanism is in the contract; retrieve from Layer 1. These
are structural frameworks for interpretation — all values and trigger
events must come from retrieved documents.

**Taking-Over and DNP — analytical reference:**
The Taking-Over Certificate triggers the DNP and the first retention
release. The Performance Certificate ends the DNP and triggers the
second retention release. The duration of the DNP is in the Contract
Data — retrieve from Layer 1. The standard FIDIC DNP is one year from
Taking-Over for the whole of the Works — this is a General Conditions
default that may be amended by Particular Conditions. Always retrieve
from Layer 1 before stating any DNP period.

**GCC security practices — analytical reference:**
On-demand bonds are standard in the GCC — the Employer can call the
bond without establishing a contractual breach. Conditional bonds
require proof of breach before calling. The form is stated in the
instrument — retrieve from Layer 1 to confirm. UAE, Saudi Arabia,
and Qatar courts have generally upheld on-demand bond calls even
where the underlying dispute is in arbitration, except where fraud
is clearly established. This is analytical context only — the
instrument form must be confirmed from the retrieved document.
