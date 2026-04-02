# Key Dates and Securities — Legal & Contractual Specialist

## When to apply this skill

Apply this skill when a query concerns contractual dates, milestones, time periods,
or security instruments — including the Commencement Date, Time for Completion,
Defects Notification Period, milestone dates, sectional completion dates, performance
bonds, advance payment guarantees, retention, and parent company guarantees. Also
apply when assessing whether a security instrument is current, in the correct form,
for the correct amount, and has been validly called or is at risk of expiry.

---

## Before you begin

This is a Round 1 skill. There are no upstream specialist findings to read.

The following must be established from prior skill outputs before this skill runs:

From contract_assembly.md:
- FIDIC book type and edition
- Contract Data / Appendix to Tender (source of all contractual dates and security
  parameters)
- Particular Conditions amendments affecting time periods or security instruments
- Any supplemental agreements or amendments that may have modified original dates

From engineer_identification.md:
- Identity of the Engineer or Employer's Representative — relevant to who issued
  the Taking-Over Certificate and Performance Certificate that mark the end of
  key periods

From notice_and_instruction_compliance.md:
- Commencement Date confirmation — was a formal Notice to Proceed issued and
  when was it received?

If any prior skill output is unavailable, retrieve the Contract Data, Appendix to
Tender, Contract Agreement, and any security instruments from the warehouse before
proceeding.

---

## Analysis workflow

**Step 1 — Extract all contractual dates from the Contract Data**

From the Contract Data or Appendix to Tender, extract and record the following
dates and periods. For each, note the source document and clause reference:

- Commencement Date (or the period within which it must occur after the Letter of
  Acceptance / Contract Agreement)
- Time for Completion (overall, and per section if sectional completion applies)
- Milestone dates (if any, from the programme schedule incorporated into the contract)
- Defects Notification Period (DNP) — duration from Taking-Over
- Period for Performance Security validity
- Period for Advance Payment Guarantee validity (if applicable)
- Retention percentage and release conditions
- Any other time-limited obligation stated in the Contract Data

Cross-check each extracted date against the Contract Agreement and Letter of
Acceptance. If a date appears differently in two documents, flag the contradiction
immediately and apply the document hierarchy from contract_assembly.md to determine
which governs.

**Step 2 — Confirm the actual Commencement Date**

The contractual Commencement Date triggers the Time for Completion countdown. It is
not necessarily the date stated in the Contract Data — it is the date on which the
Notice to Proceed was received (if the contract defines commencement by notice) or
the date the conditions precedent to commencement were satisfied.

From the warehouse, identify:
- Whether a formal Notice to Proceed or Engineer's notice of Commencement Date was
  issued
- The date on which it was received by the Contractor
- Whether the conditions precedent to commencement (mobilisation, site access,
  advance payment, bond submission) were satisfied on that date

If commencement was delayed beyond the date stated in the Contract Data due to
Employer failure to give access or issue the notice, flag this — delayed
commencement caused by the Employer is a potential EOT ground and cost entitlement
under Clause 8.1.

**Step 3 — Identify all EOT grants and revised completion dates**

From the retrieved documents, identify any extensions of time that have been
granted. For each EOT grant:
- The instruction or determination reference
- The number of days granted
- The revised Time for Completion
- Whether the grant was from the Engineer (Red/Yellow) or Employer's Representative
  (Silver)
- Whether the grant was agreed, determined, or issued unilaterally

Compile the current contractual completion date: original Time for Completion plus
all granted EOTs. This is the date against which actual completion or current
programme is assessed. Flag if EOT claims are pending that may further extend this
date — pass to Claims specialist.

**Step 4 — Assess liquidated damages exposure**

From the Contract Data, confirm:
- The LD rate (per day or per week)
- The LD cap (maximum LD amount, if stated)
- Whether LDs have been deducted from any IPC

Calculate the maximum LD exposure: LD rate × delay period to current date (or to
actual completion if the project is complete). Compare against the LD cap.

Apply GCC-specific flags:
- Qatar: government contracts typically cap LDs at 10% of contract value — confirm
  whether the contractual cap is consistent with this or whether there is a gap
- Saudi Arabia: CTL Article 179 allows courts to reduce LDs if proved excessive —
  flag if LD exposure is large relative to contract value
- UAE: no statutory LD cap but courts may reduce manifestly excessive LDs under
  good faith principles — flag if LD rate appears unusually high

**Step 5 — Assess performance security and bonds**

For each security instrument referenced in the contract (Performance Bond, Advance
Payment Guarantee, Retention Bond, Parent Company Guarantee), assess:

- Is the instrument present in the warehouse?
- Is it in the correct form — on-demand or conditional? The contract will specify
  the required form. An on-demand bond can be called without proving breach — a
  conditional bond requires the Employer to prove entitlement. This distinction is
  forensically critical.
- Is the amount correct per the Contract Data?
- What is the expiry date? Has it expired or is it at risk of expiry before the
  relevant contractual period ends?
- Under 2017 FIDIC: has the Employer given written notification before calling the
  bond? Clause 4.2 (2017) requires written notice to the Contractor before the
  Employer calls the Performance Security.
- Has the bond been called? If so, was the call valid per the bond terms and the
  contract?

If a security instrument is referenced in the Contract Agreement but not present
in the warehouse, call tools to search for it. Do not classify the security
position without the instrument document.

**Step 6 — Identify the Defects Notification Period and its implications**

From the Contract Data and any Taking-Over Certificate retrieved, establish:
- The DNP start date: date of Taking-Over Certificate for the whole works (or
  section, if sectional completion)
- The DNP duration from the Contract Data
- The DNP end date: DNP start + DNP duration
- Whether the DNP has expired, is current, or has not yet started
- Whether the Performance Certificate has been issued (marks end of Contractor's
  obligations under the contract)

Flag if:
- The DNP has expired but the Performance Certificate has not been issued — the
  Engineer/Employer's Representative is in delay in issuing the certificate and
  the Contractor may have a claim for release of retention
- Defects are being notified after the DNP expiry — the Employer's right to
  require defects correction under the contract may have expired (subject to
  decennial liability for structural defects)
- The DNP was extended by the Engineer — confirm the extension was validly issued
  and within the Engineer's authority

**Step 7 — Compile and structure findings**

Compile all findings in the output format below. The key dates extracted here are
foundational facts for every downstream specialist — Schedule needs the
Commencement Date and Time for Completion; Claims needs the LD rate and cap;
Governance needs the DNP and Performance Certificate status.

---

## Classification and decision rules

**Commencement Date:**
- Confirmed from Notice to Proceed with conditions precedent satisfied: CONFIRMED
- Notice to Proceed issued but conditions precedent not confirmed as satisfied:
  CONDITIONALLY CONFIRMED — flag outstanding conditions
- No Notice to Proceed found in warehouse: UNCONFIRMED — call tools; flag absence
- Commencement delayed beyond Contract Data date: DELAYED COMMENCEMENT — state
  cause and flag potential EOT entitlement

**Time for Completion and revised completion date:**
- Original date confirmed, no EOTs granted: ORIGINAL DATE CURRENT
- EOTs granted — revised date calculable: REVISED DATE CONFIRMED — state revised date
- EOT claims pending — revised date uncertain: REVISED DATE UNCERTAIN — state current
  confirmed date and flag pending claims
- Contradiction between documents on original date: CONTRADICTED — state both
  values and which governs per hierarchy

**Liquidated damages:**
- No delay beyond current contractual completion date: NO LD EXPOSURE CURRENTLY
- Delay exists — LD exposure calculable: STATE EXPOSURE — rate × days × cap check
- LD cap reached: LD CAP REACHED — Employer's LD entitlement is exhausted
- LD rate or cap contradicted between documents: CONTRADICTED — state both values

**Security instruments:**
- Instrument present, correct form, correct amount, not expired: VALID
- Instrument present but expiring within 30 days: AT RISK — flag immediately
- Instrument present but expired: EXPIRED — flag; Employer has no live security
- Instrument referenced in contract but not in warehouse: NOT CONFIRMED — call tools
- Instrument in wrong form (e.g. conditional when on-demand required): FORM DEFECT

**DNP and Performance Certificate:**
- DNP current, Performance Certificate not yet due: CURRENT
- DNP expired, Performance Certificate issued: COMPLETE
- DNP expired, Performance Certificate not issued: ENGINEER IN DELAY — flag
- Taking-Over Certificate not issued: DNP NOT STARTED

---

## When to call tools

**Signal:** Contract Data states a Commencement Date but no Notice to Proceed has
been retrieved
**Tool:** `search_chunks` querying for "Notice to Proceed", "Commencement Date",
"site access"
**Look for:** The formal notice and any correspondence about delayed commencement

**Signal:** Contract Agreement references a Performance Bond and/or Advance Payment
Guarantee but neither document has been retrieved
**Tool:** `get_related_documents` filtered to Performance Security, Bond, Guarantee
**Look for:** The bond documents; if not found, flag as NOT CONFIRMED and note
that security validity cannot be assessed without the instrument

**Signal:** EOT determinations are referenced in correspondence but no formal EOT
grant documents have been retrieved
**Tool:** `search_chunks` querying for "extension of time", "EOT", "revised
completion date"
**Look for:** Engineer's determinations or instructions granting EOT; compile the
full EOT history

**Signal:** A Taking-Over Certificate or Performance Certificate is referenced in
correspondence but has not been retrieved
**Tool:** `get_related_documents` filtered to Taking-Over Certificate, Performance
Certificate
**Look for:** The certificate documents; confirm the date and scope (whole works
or section)

**Signal:** Sectional completion is referenced in the query or documents but the
Contract Data for each section has not been retrieved
**Tool:** `search_chunks` querying for "section", "sectional completion", "Section
Time for Completion"
**Look for:** The Contract Data entries for each section; assess each section
separately

---

## Always flag — regardless of query

1. **Any security instrument at risk of expiry within 30 days** — always flag
   immediately regardless of the query. An expiring bond is a time-critical issue
   that requires immediate action. If the Performance Bond expires before the
   Taking-Over Certificate is issued, the Employer loses its on-demand security.

2. **Delayed commencement caused by the Employer** — always flag if the actual
   Commencement Date was later than the Contract Data date due to Employer failure
   to give site access, issue the notice, or satisfy conditions precedent. This is
   a potential EOT and cost entitlement ground that Claims must assess.

3. **LD cap reached or close to being reached** — always flag if the LD exposure
   calculation is at or approaching the contractual cap. Once the cap is reached
   the Employer's LD entitlement is exhausted — a fact that changes the commercial
   dynamics of the project significantly.

4. **DNP expired without Performance Certificate issued** — always flag. The
   Engineer or Employer's Representative is in delay in issuing the certificate.
   The Contractor may have grounds to claim release of retention and closure of
   its outstanding obligations.

5. **Contradiction between documents on any key date or rate** — always surface
   contradictions on Time for Completion, LD rate, LD cap, DNP duration, and
   retention percentage. These are the parameters most frequently disputed and
   any contradiction must be resolved by applying the document hierarchy.

---

## Output format
```
## Key Dates and Securities Assessment

### Contractual Dates
| Parameter | Contract Data value | Source document | Status |
|---|---|---|---|
| Commencement Date | | | [CONFIRMED / UNCONFIRMED / DELAYED] |
| Time for Completion | | | [ORIGINAL / REVISED / CONTRADICTED] |
| Revised completion date (if EOTs granted) | | | |
| Milestone dates (if any) | | | |
| Defects Notification Period | | | [CURRENT / EXPIRED / NOT STARTED] |
| Performance Certificate issued | | | [YES / NO / DATE] |

Commencement Date detail:
Notice to Proceed issued: [YES — date / NO — not found]
Conditions precedent satisfied: [YES / NO / CANNOT CONFIRM]
Delayed commencement flag: [YES — state cause / NO]

### Revised Completion Date
Original Time for Completion: [date]
EOTs granted: [list each grant with reference, days, and authority]
Current contractual completion date: [date]
Pending EOT claims: [list or "None identified"]
Revised date status: [CONFIRMED / UNCERTAIN — pending claims]

### Liquidated Damages Exposure
LD rate: [rate] per [day/week] — source: [document]
LD cap: [amount or "None stated"] — source: [document]
Current delay (if any): [days beyond current contractual completion date]
Current LD exposure: [rate × days]
LD cap reached: [YES / NO / N/A]
GCC-specific flags: [Qatar cap / Saudi CTL / UAE good faith — or "None"]

### Security Instruments
[For each instrument:]
**[Instrument type]**
Present in warehouse: [YES / NO]
Form: [On-demand / Conditional / CANNOT CONFIRM]
Amount: [amount] — required per Contract Data: [amount] — [CORRECT / DISCREPANCY]
Expiry date: [date]
Status: [VALID / AT RISK / EXPIRED / NOT CONFIRMED / FORM DEFECT]
2017 call notification requirement: [APPLICABLE / NOT APPLICABLE (1999)]
Called by Employer: [YES — date and validity assessment / NO]

### Defects Notification Period
Taking-Over Certificate issued: [YES — date / NO]
DNP start date: [date or "Not started"]
DNP duration: [period from Contract Data]
DNP end date: [date or "Not calculable"]
DNP status: [CURRENT / EXPIRED / NOT STARTED]
Performance Certificate issued: [YES — date / NO]
Engineer/ER delay in issuing Performance Certificate: [YES — flag / NO]

### Foundational Facts for Downstream Specialists
Commencement Date: [date] [CONFIRMED / UNCONFIRMED]
Current contractual completion date: [date]
Time for Completion (original): [period and date]
LD rate: [rate]
LD cap: [amount or "None"]
Current LD exposure: [amount or "None"]
DNP expiry: [date]
Performance Certificate status: [issued / not issued]
Security instruments: [summary of status of each]
Delayed commencement flag: [YES / NO]
LD cap reached flag: [YES / NO]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences stating the key dates position, the most
significant security or timing finding, and any immediate action flags]
```

---

## Domain knowledge and standards

### FIDIC Time Period Architecture

FIDIC contracts operate on a sequence of time periods that build on each other:

1. **Contract formation to Commencement Date** — the period between Letter of
   Acceptance (Red/Yellow) or Contract Agreement (Silver) and the Commencement Date.
   The Employer must give the Contractor at least 7 days notice of the Commencement
   Date (Cl. 8.1). Failure to do so is an Employer default.

2. **Commencement Date to Taking-Over** — the Time for Completion. This is the
   period within which the Contractor must complete the Works. It runs from the
   Commencement Date, not the contract signing date.

3. **Taking-Over to Performance Certificate** — the Defects Notification Period.
   The Contractor remains obligated to correct notified defects. Retention (second
   half) is released on the Performance Certificate.

4. **Performance Certificate** — marks the end of the Contractor's obligations under
   the contract (subject to decennial liability). The Engineer must issue the
   Performance Certificate within 28 days of the later of expiry of the DNP and
   correction of all notified defects.

Understanding this sequence is essential — a claim or dispute that references dates
must be placed correctly in this sequence to be meaningful.

### Security Instruments — On-Demand vs Conditional

The distinction between an on-demand bond and a conditional bond is one of the most
significant forensic issues in construction security assessment.

An **on-demand bond** (also called an unconditional bond or demand guarantee) can be
called by the Employer on first written demand without proving breach or loss. The
bank or surety pays on demand and recovers separately. FIDIC standard Performance
Security (Annex to Particular Conditions) is an on-demand form.

A **conditional bond** (also called a default bond or see-to-it bond) can only be
called after proving the Contractor's breach and the Employer's loss. The surety's
liability mirrors the Contractor's liability under the contract. Calling a
conditional bond requires a court judgment or arbitral award in most jurisdictions.

In GCC practice, on-demand bonds are standard for performance security. A Contractor
whose contract requires an on-demand bond but who provides a conditional bond has
not complied with the contract — the Employer may be entitled to reject it. When
assessing a bond, always determine which form is required by the contract and which
form has been provided.

**FIDIC 2017 change:** Clause 4.2 (2017) requires the Employer to give written
notification to the Contractor before making a call on the Performance Security,
stating the nature of the default. This is a new protection introduced in 2017
that does not exist in 1999. On a 2017 project, a bond call without prior written
notification may be challengeable.

### GCC Security Practice

**UAE:** On-demand bank guarantees from UAE-licensed banks are standard. Courts
will enforce on-demand bonds without looking behind the demand, subject to fraud
exception. The fraud exception is narrowly construed — a Contractor resisting a
bond call must show clear fraud, not merely dispute the underlying claim.

**Saudi Arabia:** Performance bonds from Saudi-licensed banks or approved
international banks. SAMA-regulated bank guarantees are standard. Saudi courts
and arbitration centres enforce on-demand bonds but will examine whether the call
conditions have been met.

**Qatar:** On-demand bonds from Qatar-licensed banks standard on public works
projects. Qatar courts apply similar principles to UAE on enforcement.

### Retention

FIDIC standard retention: 5% of each IPC, up to a retention limit of 5% of the
contract sum. First half released on Taking-Over Certificate. Second half released
on Performance Certificate (or expiry of DNP if defects have been corrected).

Particular Conditions commonly modify retention: higher percentage, higher limit,
deferred release conditions, or replacement by retention bond. Always extract the
actual retention terms from the Contract Data and note any amendments.
