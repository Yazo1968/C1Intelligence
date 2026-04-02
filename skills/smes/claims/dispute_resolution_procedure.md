# Dispute Resolution Procedure

**Skill type:** Contract-type-specific (dispute resolution mechanism
differs significantly by FIDIC book and edition; arbitration rules
are contract-specific)
**Domain:** Claims & Disputes SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply this skill when retrieved chunks contain a DAB or DAAB
decision, a Notice of Dissatisfaction, an arbitration notice,
a query about whether a dispute has been properly escalated,
a query about limitation periods, or a request to assess
the procedural status of a dispute. Also apply when a claim
has been rejected or not responded to and the next procedural
step is in question.

---

## Before you begin

**Step 1 — Establish the governing contract type and dispute
resolution mechanism.**
Read the Legal orchestrator findings. Extract:
- FIDIC book and edition — the dispute resolution mechanism
  differs materially between editions and between books
- The arbitration rules specified in the Particular Conditions
- The seat of arbitration
- The governing law
- Whether the Particular Conditions amend or replace the
  standard FIDIC dispute resolution procedure

Do not assume the General Conditions dispute resolution
mechanism applies. GCC Particular Conditions frequently
replace the standard FIDIC DAB/DAAB with local arbitration
centre rules or government dispute committees.

**Step 2 — Establish the claim history.**
Before assessing the dispute procedure, confirm:
- The original claim submission and its date
- The Engineer's determination (Red/Yellow) or absence thereof
- The Notice of Dissatisfaction (if any) and its date
- The current procedural stage

The dispute resolution procedure is sequential — each step
gates the next. A step that has not been properly completed
may invalidate subsequent steps.

**Step 3 — Identify all relevant deadlines.**
Dispute resolution is time-critical. Extract all deadlines
from the Particular Conditions — not from the General
Conditions defaults. Key deadlines to extract:
- Period for Engineer's determination (Red/Yellow only)
- Period for DAB/DAAB decision
- Period to issue Notice of Dissatisfaction after determination
  or DAB/DAAB decision
- Limitation period for arbitration

---

## Analysis workflow

**Step 1 — Retrieve all dispute resolution documents.**
Call `get_related_documents` with document_type "DAB Decision"
and "DAAB Decision". Call `get_related_documents` with
document_type "Notice of Dissatisfaction". Call `search_chunks`
with query "dispute adjudication arbitration notice dissatisfaction
DAB DAAB". Compile all dispute documents.

**Step 2 — Map the dispute to the correct procedure by book
and edition.**

Apply the correct procedure for the identified contract type —
see Domain Knowledge section. The procedure differs materially
between 1999 and 2017 and between Red/Yellow and Silver.

**Step 3 — Assess each procedural step in sequence.**

*Step 3a — Engineer's determination (Red/Yellow only):*
Was the claim submitted to the Engineer for determination?
Was the determination issued within the period extracted from
the Particular Conditions? Under FIDIC 2017 Cl. 3.7, a failure
to determine within the prescribed period results in deemed
rejection — this triggers the NOD period. Under FIDIC 1999
Cl. 3.5, there is no express time limit — a failure to
determine does not automatically trigger NOD rights.

*Step 3b — DAB/DAAB referral:*
Was the dispute referred to the DAB (1999) or DAAB (2017)?
Was the referral made within the permitted period? Was the
DAB/DAAB properly constituted — extract the appointment
mechanism from the Particular Conditions and verify it
was followed.

*Step 3c — DAB/DAAB decision:*
Was a decision issued? Within the period specified in the
Particular Conditions? Is the decision binding pending
arbitration (interim binding — the FIDIC standard position)?
Has either party complied with the decision?

*Step 3d — Notice of Dissatisfaction:*
Was a Notice of Dissatisfaction (NOD) issued? Within the
period extracted from the Particular Conditions? By the
correct party? A failure to issue a timely NOD renders the
DAB/DAAB decision final and binding — this is one of the
most significant procedural traps in FIDIC dispute resolution.
If no NOD was issued, flag immediately.

*Step 3e — Arbitration:*
Has arbitration been commenced? Under the rules specified in
the Particular Conditions? At the seat specified? Within any
applicable limitation period?

**Step 4 — Assess compliance with pay-now-argue-later.**
Under FIDIC (both editions), a DAB/DAAB decision is binding
on an interim basis — the party required to pay must do so
even if it has issued a NOD and intends to refer the matter
to arbitration. Non-compliance with a binding decision is
itself a contractual breach. Assess whether the party obliged
to comply with the decision has done so.

**Step 5 — Assess limitation periods.**
Extract the applicable limitation period from the Particular
Conditions and the governing law. Identify the date from which
the limitation period runs for any dispute not yet referred
to arbitration. Flag any dispute where the limitation period
is approaching or may have elapsed.

---

## Classification and decision rules

**DAB/DAAB decision status:**

Decision issued, no NOD within the Particular Conditions period:
→ **FINAL AND BINDING** — flag immediately; the decision cannot
  be reopened in arbitration absent fraud or serious procedural
  irregularity

Decision issued, NOD issued within period by either party:
→ **INTERIM BINDING** — must be complied with; subject to
  arbitration for final determination

Decision not issued within the period specified in the
Particular Conditions:
→ Deemed rejection under 2017 Cl. 21.4.4 — NOD period
  triggered; assess whether NOD was issued within time
→ Under 1999: no deemed rejection — different analysis applies;
  the absence of a decision does not automatically trigger
  NOD rights without a deemed determination mechanism in
  the Particular Conditions

**Notice of Dissatisfaction:**

NOD issued within the period extracted from the Particular
Conditions:
→ **TIMELY** — dispute is open for arbitration

NOD not issued within the period:
→ **DECISION FINAL AND BINDING** — flag immediately with
  one-sentence implication

NOD period cannot be confirmed (Particular Conditions not
in warehouse):
→ **CANNOT ASSESS** — flag; state the NOD period must be
  confirmed before the finality of the decision can be determined

**Silver Book — no Engineer determination:**

Silver Book (all editions) has no Engineer determination
mechanism. Disputes go directly to DAB (1999) or DAAB (2017).
If a Silver Book contract shows an Engineer's determination
step in the dispute process, flag this as inconsistent with
the contract type — verify whether a bespoke procedure has
been inserted by Particular Conditions.

---

## When to call tools

**Signal:** A DAB or DAAB decision is referenced in the claim
but has not been retrieved.
**Action:** Call `get_related_documents` with document_type
"DAB Decision" or "DAAB Decision". Call `search_chunks` with
query "adjudication board decision [claim reference]".
**Look for:** The decision document, its date, and the
party required to comply.

**Signal:** The dispute resolution clause in the Particular
Conditions has not been retrieved and the arbitration rules
and seat cannot be confirmed.
**Action:** Call `search_chunks` with query "arbitration
dispute resolution particular conditions seat rules".
Call `get_document` on the Particular Conditions document
if its ID is known from Legal orchestrator findings.
**Look for:** The arbitration clause — rules, seat, and
any amendments to the standard FIDIC procedure.

**Signal:** A NOD has been referenced but its date cannot
be confirmed from the retrieved chunks.
**Action:** Call `get_document` on the NOD document if
its ID is available. Call `search_chunks` with query
"notice dissatisfaction [party] [approximate date]".
**Look for:** The full NOD document with its date to
verify timeliness against the Particular Conditions period.

**Signal:** Limitation period is potentially in issue but
the governing law limitation period has not been established.
**Action:** Call `search_chunks` with query "governing law
limitation period prescription".
**Look for:** The governing law clause in the contract and
any express limitation provision in the Particular Conditions.

---

## Always flag — regardless of query

**Flag 1 — DAB/DAAB decision with no NOD found.**
If a DAB or DAAB decision is in the warehouse and no
corresponding NOD has been found after searching, flag
immediately. State: the decision date, the NOD period
extracted from the Particular Conditions (or that it could
not be confirmed), and the consequence — the decision may
be final and binding.

**Flag 2 — Non-compliance with binding DAB/DAAB decision.**
If a binding decision requires a payment or action and no
evidence of compliance has been found, flag this. State the
decision requirement and the absence of compliance evidence.

**Flag 3 — Procedural step skipped or out of sequence.**
If the dispute escalation shows a step has been skipped
(e.g., arbitration commenced without a prior NOD, NOD issued
without a prior determination), flag the procedural irregularity
and state its potential effect on the arbitration.

**Flag 4 — Limitation period approaching or elapsed.**
If the limitation period for any unresolved dispute is
within 90 days or appears to have elapsed, flag immediately.
State the applicable period, the trigger date, and the
current date.

**Flag 5 — Particular Conditions replace standard FIDIC
procedure.**
If the Particular Conditions substitute a different dispute
resolution mechanism (local arbitration centre, government
dispute committee, courts), flag this. State the substituted
mechanism and confirm the applicable procedural rules.

---

## Output format
```
## Dispute Resolution Procedure Assessment

### Contract Basis
- FIDIC book and edition: [extracted]
- Dispute resolution mechanism: [DAB/DAAB + arbitration /
  modified by Particular Conditions — state modification]
- Arbitration rules: [from Particular Conditions]
- Seat of arbitration: [from Particular Conditions]
- Governing law: [from Legal orchestrator or retrieved]
- Particular Conditions amendments to dispute procedure:
  [list or NONE FOUND]

### Dispute Register

| # | Claim ref | Determination | DAB/DAAB decision | NOD | Arbitration | Status |
|---|---|---|---|---|---|---|
| 1 | [ref] | [date/NOT ISSUED/N/A] | [date/NOT ISSUED] | [date/NOT ISSUED] | [date/NOT COMMENCED] | [status] |

### Findings by Dispute

**[Claim reference]**

*Engineer's Determination (Red/Yellow only):*
Submitted: [YES — date / NO]
Determination issued: [YES — date / NO / DEEMED REJECTED]
Within period: [YES / NO / CANNOT CONFIRM — period not extracted]
Source: [document reference]

*DAB/DAAB Referral:*
Referred: [YES — date / NO]
Within permitted period: [YES / NO / CANNOT CONFIRM]
DAB/DAAB constitution: [CONFIRMED / NOT CONFIRMED]
Source: [document reference]

*DAB/DAAB Decision:*
Decision issued: [YES — date / NO]
Within period: [YES / NO / CANNOT CONFIRM]
Decision status: [INTERIM BINDING / FINAL AND BINDING / NOT ISSUED]
Compliance by obligated party: [YES / NO / NOT ASSESSABLE]
Source: [document reference]

*Notice of Dissatisfaction:*
NOD issued: [YES — date and issuing party / NO]
Within period: [YES / NO / CANNOT CONFIRM — state period and source]
Effect: [Decision remains interim binding / Decision is final and
binding / Cannot assess]
Source: [document reference]

*Arbitration:*
Commenced: [YES — date / NO]
Under rules: [rules from Particular Conditions]
At seat: [seat from Particular Conditions]
Within limitation period: [YES / NO / CANNOT CONFIRM]
Source: [document reference]

*Limitation Period:*
Applicable period: [period and source]
Trigger date: [date]
Expiry date: [date or CANNOT CALCULATE]
Status: [WITHIN PERIOD / APPROACHING — days remaining /
POTENTIALLY ELAPSED / CANNOT ASSESS]

Finding: [specific conclusion with source attribution]

### FLAGS
[Each flag with one-sentence implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences]
```

---

## Domain knowledge and standards

### Dispute resolution procedure by book and edition

**Red Book and Yellow Book — 1999:**
1. Engineer's determination (Cl. 3.5) — no time limit on
   the Engineer to determine; failure to determine does not
   automatically trigger NOD rights unless the Particular
   Conditions include a deemed determination mechanism
2. Either party may refer to DAB (Cl. 20.4) — the DAB is
   typically a standing three-member board appointed at the
   outset of the project
3. DAB issues decision — binding on both parties on an interim
   basis
4. Either party may issue NOD within the period in the
   Particular Conditions (default 28 days in General Conditions
   — always extract from Particular Conditions)
5. If no NOD: decision is final and binding
6. If NOD: dispute open for ICC arbitration (default — check
   Particular Conditions) after amicable settlement attempt
   (56 days from NOD in General Conditions — extract from PC)

**Red Book and Yellow Book — 2017:**
1. Engineer's determination (Cl. 3.7) — time-limited;
   failure within the period results in deemed rejection
   which triggers the NOD period
2. Either party may refer to DAAB (Cl. 21.4) — the DAAB is
   a standing or ad hoc board; appointment mechanism in
   Particular Conditions
3. DAAB issues decision — interim binding
4. NOD within period in Particular Conditions (default 28 days)
5. If no NOD: decision final and binding
6. If NOD: ICC arbitration (default) after amicable settlement
   attempt (28 days from NOD in 2017 — extract from PC)

**Silver Book — 1999:**
No Engineer determination mechanism. Dispute goes directly to:
1. DAB referral (Cl. 20.4)
2. DAB decision — interim binding
3. NOD within period in Particular Conditions
4. If no NOD: final and binding
5. If NOD: ICC arbitration after amicable settlement attempt

**Silver Book — 2017:**
No Engineer determination mechanism. Dispute goes directly to:
1. DAAB referral (Cl. 21.4)
2. DAAB decision — interim binding
3. NOD within period in Particular Conditions
4. If no NOD: final and binding
5. If NOD: ICC arbitration after amicable settlement attempt

All time periods in the above are General Conditions defaults.
**Extract all periods from the Particular Conditions.**

### Pay-now-argue-later

A fundamental FIDIC principle across all books and editions:
a DAB or DAAB decision is binding on an interim basis. The
party required to comply must do so even if it has issued a
NOD. Failure to comply is a contractual breach independent
of the merits of the underlying dispute. Under FIDIC 2017,
failure to comply with a binding decision can be referred
to arbitration as a separate breach without waiting for the
underlying dispute to be resolved.

### GCC-specific arbitration practice

**ICC (International Chamber of Commerce):** The default
and most common arbitration institution for international
construction contracts in the GCC. UAE, Saudi Arabia, and
Qatar are all parties to the New York Convention — ICC
awards are enforceable. Emergency arbitrator provisions
are available and used for urgent payment enforcement.

**DIAC (Dubai International Arbitration Centre):** Governs
disputes under DIFC law or where DIAC is specified. New
DIAC Rules (2022) align with international best practice.
Enforceable onshore in Dubai through DIFC-Dubai enforcement
mechanism.

**ADCCAC (Abu Dhabi Commercial Conciliation and Arbitration
Centre):** Used for Abu Dhabi government contracts.
Government project Particular Conditions frequently specify
ADCCAC rather than ICC.

**SCCA (Saudi Centre for Commercial Arbitration):** Growing
institution for Saudi disputes. Government contracts may
specify SCCA or government dispute committees. Saudi Arabia
ratified the New York Convention in 1994 — awards are
generally enforceable but Saudi courts have occasionally
applied public policy exceptions.

**QICCA (Qatar International Centre for Conciliation and
Arbitration):** Used for Qatar disputes. Qatar adopted the
UNCITRAL Model Law (Law No. 2 of 2017) — modern arbitration
framework. Major Qatar government contracts frequently
specify QICCA.

**DAB appointments in practice:** On GCC projects, standing
DABs (appointed at project outset) are less common than the
FIDIC model assumes. Ad hoc DABs (appointed only when a
dispute arises) are more prevalent — this has implications
for timeliness of dispute resolution. Employer resistance
to DAB appointment is a recurring issue, particularly on
UAE government projects. Flag where no DAB or DAAB has
been constituted on a project with active disputes.

**Limitation periods:** UAE: 15 years general limitation
under Civil Code (Art. 473); commercial contracts 10 years.
Saudi Arabia: varies by claim type — commercial claims
generally 5 years. Qatar: 10 years general limitation
(Civil Code Art. 419). These are general positions — the
governing law and any express contractual limitation
provision in the Particular Conditions take precedence.
Always extract from the project documents.
