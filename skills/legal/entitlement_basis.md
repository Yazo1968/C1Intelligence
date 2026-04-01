# Entitlement Basis — Legal & Contractual Specialist

## When to apply this skill

Apply this skill when a query concerns whether a Contractor or Employer has a
contractual entitlement to additional time, cost, or both — including EOT claims,
prolongation cost claims, variation entitlements, unforeseeable conditions claims,
suspension claims, and termination compensation. Also apply when assessing whether
the FIDIC clause cited in a claim document actually supports the relief claimed, or
whether Particular Conditions amendments have modified or removed the entitlement.

---

## Before you begin

This is a Round 1 skill. There are no upstream specialist findings to read.

The following must be established from prior skill outputs before this skill runs:

From contract_assembly.md:
- FIDIC book type and edition
- Particular Conditions amendments — especially any that modify entitlement clauses,
  narrow Employer Risk Events, restrict cost recovery, or remove specific heads of
  claim
- Governing law and jurisdiction

From engineer_identification.md:
- Identity of the Engineer or Employer's Representative
- Engineer independence status — relevant to whether determinations of entitlement
  are credible

From notice_and_instruction_compliance.md:
- Time bar status for any claim notices assessed — a POTENTIALLY TIME-BARRED finding
  means entitlement analysis is secondary; flag this at the start and proceed with
  entitlement assessment noting the time bar caveat

If any prior skill output is unavailable, retrieve the Particular Conditions,
Contract Agreement, and the claim document from the warehouse before proceeding.

---

## Analysis workflow

**Step 1 — Identify the claimed entitlement and the FIDIC clause cited**

From the retrieved claim document or query context, identify:
- What relief is claimed: EOT only / Cost only / EOT + Cost / EOT + Cost + Profit /
  Termination compensation / Other
- Which FIDIC sub-clause is cited as the basis for entitlement
- The nature of the event giving rise to the claim

If no FIDIC clause is cited in the claim document, note this as a deficiency —
a claim that does not identify its contractual basis is procedurally deficient under
both 1999 and 2017 FIDIC. Under 2017 Clause 20.2.4, the fully detailed claim must
include the contractual basis; failure to do so affects the claim's standing.

**Step 2 — Confirm the book type and apply the correct entitlement framework**

The entitlement framework differs materially across the three FIDIC books. Apply the
framework for the confirmed book type:

**Red Book (Construction) — Employer Risk Events under Sub-Clause 8.4 / 8.5:**
The Contractor is entitled to EOT for delays caused by:
- Variation or other substantial change in quantity (Cl. 13)
- Cause of delay giving right to extension under the contract
- Exceptionally adverse climatic conditions
- Unforeseeable shortages of personnel or goods
- Delay caused by Employer, Engineer, or other contractor employed by Employer
- Any other cause listed in the Particular Conditions

For Cost recovery, the event must fall under a specific cost-entitlement clause
(e.g. Cl. 4.12 unforeseeable physical conditions, Cl. 4.24 fossils, Cl. 8.9
suspension, Cl. 17.4 Employer's risks). EOT entitlement does not automatically
confer Cost entitlement — the two must be assessed separately.

**Yellow Book (Plant & Design-Build) — same EOT grounds as Red Book with one
key distinction:**
Sub-Clause 1.9 — if the Contractor suffers delay or incurs cost due to a failure
in the Employer's Requirements that an experienced contractor could not have
discovered at tender, the Contractor is entitled to EOT and Cost. This is an
Employer Risk Event specific to Yellow Book — it does not exist in Red or Silver.
Design defects that are the Contractor's own errors are not Employer Risk Events.

**Silver Book (EPC/Turnkey) — significantly narrower entitlement:**
Sub-Clause 4.12 — the Contractor is deemed to have accepted total responsibility
for having foreseen all difficulties and costs. Unforeseeable physical conditions
are not an Employer Risk Event under Silver Book. The EOT grounds are narrower:
exceptionally adverse climatic conditions and unforeseeable shortages are removed.
The Contractor bears substantially all risk events that would give rise to
entitlement under Red and Yellow Books. Assess Silver Book claims against the
specific and narrow list of Employer Risk Events in the Particular Conditions —
do not apply Red Book entitlement logic to a Silver Book project.

**Step 3 — Check whether the Particular Conditions have modified the entitlement**

The Particular Conditions override the General Conditions. Before concluding on
entitlement, check the amendments mapped by contract_assembly.md for any that affect
the claimed clause. Common GCC modifications that restrict entitlement:

- Removal of Clause 4.12 (unforeseeable physical conditions) — Contractor bears
  all ground conditions risk regardless of foreseeability
- Removal of Clause 14.8 (financing charges) — common in Saudi projects (riba)
- Modification of Clause 8.4/8.5 to remove specific EOT grounds
- Capping of prolongation costs — time-related costs recoverable only up to a
  stated daily rate
- Removal of profit from cost recovery — "Cost" defined to exclude profit in
  Particular Conditions
- Modification of the definition of "Cost" to exclude head office overheads
- Reduction of the LD cap or removal of the LD cap

If a Particular Conditions amendment removes or restricts the entitlement claimed,
state this explicitly: the entitlement basis does not survive the Particular
Conditions amendment. Do not assess the merits of the claim under the General
Conditions if the Particular Conditions have removed the right.

**Step 4 — Assess whether the entitlement clause supports the relief claimed**

Match the relief claimed (EOT / Cost / Profit) against what the cited FIDIC clause
actually provides.

Key mapping for common claims:
- Cl. 4.12 (unforeseeable physical conditions): EOT + Cost — no Profit
- Cl. 4.24 (fossils): EOT + Cost — no Profit
- Cl. 8.4/8.5 (EOT): EOT only — Cost requires a separate clause
- Cl. 8.9 (suspension by Engineer): EOT + Cost + Profit if suspension exceeds 84
  days and Contractor elects to terminate
- Cl. 13.1 (variation): EOT + Cost + Profit — full variation valuation applies
- Cl. 17.4/18.4 (Employer's risks / Force Majeure): EOT + Cost — no Profit unless
  Particular Conditions provide otherwise
- Cl. 16.4 (termination by Contractor): Cost + Profit on work not executed +
  reasonable profit on terminated work — no obligation to continue

If the claimed relief exceeds what the cited clause provides (e.g. Profit claimed
under Clause 4.12), flag the excess as NOT ESTABLISHED under the cited clause.
Note whether a different clause might support the excess relief — do not dismiss
without checking.

**Step 5 — Assess Employer's claims entitlement (if applicable)**

Under 1999 Clause 2.5, Employer's claims are governed by a separate, asymmetric
procedure. The Employer must give notice to the Engineer as soon as practicable.
There is no 28-day time bar on the Employer's claims under 1999.

Under 2017 Clause 20.2, Employer's claims are symmetric with Contractor's claims —
the same 28-day time bar and 84-day detailed claim procedure applies to both parties.
This is a significant change from 1999. If assessing an Employer's claim on a 2017
project, apply the full Clause 20.2 procedure including the time bar.

Common Employer entitlement claims: liquidated damages (Cl. 8.7/8.8), defects
correction costs (Cl. 11.4), reduction in contract price for uncorrected defects
(Cl. 11.4), insurance proceeds shortfall. For LD claims, confirm the LD rate and
cap from the Contract Data and check the Qatar 10% cap where applicable.

**Step 6 — Identify GCC-specific entitlement patterns**

Flag any of the following patterns if present:

- **Decennial liability parallel claim:** Where the claimed defect may engage UAE
  Civil Code Article 880 or Saudi Building Code Article 29, note that the
  contractual defects liability period runs in parallel with the 10-year statutory
  liability — the Employer may have rights beyond the contractual DNP.

- **Saudi CTL Article 179 LD reduction:** In Saudi-governed contracts, the court
  may reduce LDs if proved excessive regardless of the contractual LD rate. Flag
  if LDs are claimed and the project is Saudi-governed.

- **Qatar LD cap:** Qatar government contracts typically cap LDs at 10% of contract
  value. If the LD calculation exceeds this, flag the potential enforceability issue.

- **Silver Book risk challenge:** Where a Silver Book Contractor claims under a
  provision that does not exist in Silver Book (e.g. Sub-Clause 4.12 for
  unforeseeable conditions), flag that the entitlement basis is not established
  under the applicable book. Do not apply Red Book logic.

- **Force majeure / exceptional events:** Under 2017 FIDIC the "Exceptional Events"
  clause (Cl. 18) replaces the 1999 Force Majeure clause (Cl. 19). The 2017
  clause is more detailed and introduces an obligation to give notice within 14
  days of the start of the exceptional event. Check notice compliance if a force
  majeure / exceptional events claim is being assessed.

**Step 7 — Compile and structure findings**

Compile all findings in the output format below. The entitlement basis findings are
passed forward to the Claims specialist, who will assess causation, delay analysis,
and quantum. Do not duplicate those assessments here — the Legal specialist's role
is to confirm the contractual basis, not to assess the merit of the evidence.

---

## Classification and decision rules

**Entitlement basis:**
- Cited clause exists, applies to the event type, and supports the relief claimed
  without Particular Conditions modification: ESTABLISHED
- Cited clause exists and applies but supports lesser relief than claimed (e.g.
  no Profit): PARTIALLY ESTABLISHED — state what is established and what is not
- Cited clause exists but Particular Conditions have removed or restricted it:
  NOT ESTABLISHED — state the Particular Conditions clause that removes it
- Cited clause does not apply to the event type claimed: NOT ESTABLISHED — state
  why and identify any alternative clause that might apply
- No clause cited in the claim document: CLAUSE NOT IDENTIFIED — flag as procedural
  deficiency; assess based on event type if possible
- Silver Book project claiming under a Red/Yellow Book provision: NOT ESTABLISHED
  UNDER APPLICABLE BOOK — state the Silver Book position

**Relief type:**
- EOT claimed and clause supports EOT: EOT ESTABLISHED
- Cost claimed and clause supports Cost: COST ESTABLISHED
- Profit claimed and clause supports Profit: PROFIT ESTABLISHED
- Any component claimed that clause does not support: [COMPONENT] NOT ESTABLISHED

**Particular Conditions modification:**
- No relevant amendment found: GENERAL CONDITIONS APPLY UNMODIFIED
- Amendment found that restricts but does not remove entitlement: MODIFIED —
  state the restriction and its effect
- Amendment found that removes entitlement entirely: ENTITLEMENT REMOVED BY
  PARTICULAR CONDITIONS

---

## When to call tools

**Signal:** The claim cites a FIDIC clause but the Particular Conditions for that
clause have not been retrieved — cannot confirm whether the clause was amended
**Tool:** `search_chunks` querying for the specific sub-clause number and
"Particular Conditions"
**Look for:** Any amendment to the cited clause; if none found after search, state
General Conditions apply unmodified

**Signal:** The event described in the claim does not obviously match any standard
FIDIC Employer Risk Event — possible bespoke entitlement in Particular Conditions
**Tool:** `search_chunks` querying for the event description and "Particular
Conditions"
**Look for:** Any bespoke entitlement clause added by the Particular Conditions
for this event type

**Signal:** The claim document is an EOT claim but no programme or delay analysis
has been retrieved — cannot assess whether the EOT ground is supported by evidence
**Tool:** `get_related_documents` filtered to Programme, Delay Analysis Report,
Progress Report
**Look for:** Pass to Claims specialist — note that causation and programme evidence
assessment is outside Legal specialist scope but flag the absence

**Signal:** Multiple claims are referenced in the query but only one claim document
has been retrieved
**Tool:** `search_chunks` querying for each claim reference number
**Look for:** All claim documents in the series; assess each separately

---

## Always flag — regardless of query

1. **Particular Conditions amendments that restrict or remove entitlement** — always
   surface any PC amendment that affects the entitlement being assessed, even if the
   query did not ask about the PC. A Contractor relying on General Conditions
   entitlement that has been removed by the PC has no entitlement regardless of
   the merits of its claim.

2. **Silver Book risk allocation where Red Book logic has been applied** — whenever
   the project is a Silver Book and the claim relies on a Red Book Employer Risk
   Event (particularly Sub-Clause 4.12), always flag that the entitlement basis
   does not exist under the applicable book.

3. **Mismatch between claimed relief and clause entitlement** — always flag when
   Profit is claimed under a clause that does not provide for it, or when Cost is
   claimed under an EOT-only clause. These are common errors in claim documents.

4. **Time bar caveat on entitlement findings** — whenever notice_and_instruction_
   compliance.md has found POTENTIALLY TIME-BARRED, always preface the entitlement
   finding with this caveat. A perfectly established entitlement basis is academic
   if the notice was out of time.

5. **2017 Clause 20.2.4 — contractual basis requirement** — on 2017 edition
   projects, always check whether the detailed claim identifies the contractual
   basis. A claim submitted without identifying the contractual basis within 84 days
   of the notice lapses under Clause 20.2.4. Flag if the contractual basis is absent
   or insufficient.

---

## Output format
```
## Entitlement Basis Assessment

### Time Bar Caveat
[If notice_and_instruction_compliance.md found POTENTIALLY TIME-BARRED:]
CAVEAT: Notice for [claim reference] assessed as POTENTIALLY TIME-BARRED. Entitlement
analysis follows but is secondary to the time bar finding.
[If no time bar issue:] No time bar issue identified for this claim.

### Claim Reference and Relief Claimed
Claim reference: [reference]
Relief claimed: [EOT / Cost / Profit / combination]
FIDIC clause cited: [clause reference or "None cited"]
Event type: [brief description]

### Book Type and Entitlement Framework Applied
Book: [Red / Yellow / Silver]
Edition: [1999 / 2017]
Applicable Employer Risk Event framework: [brief statement of applicable framework]

### Particular Conditions Assessment
PC amendments relevant to cited clause: [list or "None found"]
Effect on entitlement: [GENERAL CONDITIONS APPLY UNMODIFIED / MODIFIED / ENTITLEMENT
REMOVED]
[If modified or removed: state the PC clause reference and the specific effect]

### Entitlement Basis Assessment
Cited clause applies to event type: [YES / NO / PARTIALLY]
Clause supports EOT: [YES / NO / N/A]
Clause supports Cost: [YES / NO / N/A]
Clause supports Profit: [YES / NO / N/A]
Entitlement basis: [ESTABLISHED / PARTIALLY ESTABLISHED / NOT ESTABLISHED /
CLAUSE NOT IDENTIFIED]
[If not established or partial: state specifically what is not established and why]
[If alternative clause identified: state the alternative and what it provides]

### GCC-Specific Flags
[List any GCC-specific flags triggered, or "None"]

### Findings for Downstream Specialists
Claim reference: [reference]
Entitlement basis: [ESTABLISHED / PARTIALLY ESTABLISHED / NOT ESTABLISHED]
Relief confirmed under contract: [EOT / Cost / Profit — list what is established]
Relief not confirmed: [list what is not established, or "None"]
Key PC amendment affecting entitlement: [state or "None"]
Time bar caveat: [YES / NO]
Note for Claims specialist: [any specific instruction for Claims assessment, e.g.
"causation and programme evidence required to complete EOT assessment" or "Profit
not recoverable under cited clause — Claims should not include Profit in quantum"]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences stating the entitlement position, the most
significant finding, and the key caveat for downstream specialists]
```

---

## Domain knowledge and standards

### FIDIC Entitlement Architecture

FIDIC separates EOT entitlement from Cost entitlement. This is a fundamental point
that is frequently misunderstood in claim documents. Sub-Clause 8.4 (1999) and
8.5 (2017) list the grounds for EOT. Cost recovery requires a separate sub-clause
that specifically provides for it. A Contractor who proves an EOT ground has not
automatically proved Cost entitlement — they must additionally point to a clause
that provides for Cost recovery for that event.

The clauses that provide for both EOT and Cost are the exception, not the rule.
The clauses that provide for EOT only are more numerous. Profit is recoverable only
under specific clauses (primarily variations under Clause 13 and termination under
Clause 16.4).

### Silver Book Sub-Clause 4.12 — Total Risk Transfer

The Silver Book Sub-Clause 4.12 states that the Contractor is deemed to have
satisfied itself as to the correctness and sufficiency of the Contract Price and
to have obtained all necessary information as to risks, contingencies and other
circumstances which may affect or influence its performance. The Contractor accepts
total responsibility for having foreseen all difficulties and costs of successfully
completing the Works.

This is not an amendment — it is the standard Silver Book position. A Contractor
on a Silver Book project who encounters unforeseen ground conditions has no
entitlement under Sub-Clause 4.12 regardless of how unforeseeable those conditions
were. This is the most significant single risk distinction between the Silver Book
and the Red and Yellow Books. Always apply this distinction when assessing Silver
Book claims.

### Yellow Book Sub-Clause 1.9 — Errors in Employer's Requirements

Under Yellow Book Sub-Clause 1.9, if the Contractor suffers delay or incurs cost
as a result of an error in the Employer's Requirements, and an experienced contractor
exercising due care could not have discovered the error before the Base Date, the
Contractor is entitled to EOT and Cost (no Profit). This entitlement recognises that
the Employer is responsible for the accuracy of its own design brief. It does not
apply where the Contractor's own design work contains errors — design liability
rests with the Contractor under Yellow Book.

### GCC Particular Conditions Entitlement Patterns

Saudi Arabia — riba prohibition on Clause 14.8: Financing charges (Clause 14.8)
are commonly removed from Saudi contracts due to the Islamic finance prohibition on
interest. A Contractor claiming financing charges on a Saudi-governed contract faces
a Particular Conditions barrier regardless of the General Conditions position.

Saudi Arabia — CTL Article 179: Courts may reduce contractually agreed LDs if the
Employer cannot prove actual loss or if the LD rate is proved excessive. This applies
regardless of the Particular Conditions LD clause.

Qatar — 10% LD cap: Standard Qatar government procurement caps LDs at 10% of
contract value. A Contractor facing LD deductions that exceed this cap has a
potential enforceability challenge under Qatar law.

UAE — decennial liability: UAE Civil Code Article 880 creates a mandatory 10-year
joint liability for collapse or structural defect risk. A contractual DNP shorter
than 10 years does not extinguish this liability. Where structural defects are in
issue, both the contractual and statutory liability periods apply.
