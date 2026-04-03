# Notice and Instruction Compliance

**Skill type:** Mixed
- Contract-type-specific: notice requirements, time bar periods, and
  routing differ by FIDIC book and edition; Particular Conditions
  amendments to notice provisions are project-specific
- Contract-type-agnostic: the requirement to verify form, timing,
  routing, and content compliance applies regardless of book type
**Layer dependency:**
- Layer 1 — project documents: the specific notice or instruction
  under assessment; Particular Conditions (Clause 1.3 and notice
  clause amendments); Contract Data (notice periods, addresses);
  contemporaneous records establishing awareness date
- Layer 2 — reference standards: FIDIC Clause 1.3 (notices) and the
  relevant notice clause (Clause 20.1 for 1999 / Clause 20.2.1 for
  2017) for the confirmed book and edition
**Domain:** Legal & Contractual SME
**Invoked by:** Legal orchestrator

---

## When to apply this skill

Apply when a query concerns whether a notice or instruction was validly
issued — including Notice of Claim, Notice of Delay, Engineer's
Instruction, variation instruction, suspension notice, termination
notice, or any contractual communication whose validity depends on
form, timing, or routing. Apply when assessing whether a time bar has
been triggered or whether a communication constitutes a valid notice.

---

## Before you begin

### Foundational requirements
Read contract_assembly and engineer_identification findings first.

From contract_assembly extract:
- Confirmed FIDIC book and edition — required before any notice
  clause reference can be applied
- Particular Conditions amendments to Clause 1.3 and to the notice
  clause (Clause 20.1 / 20.2.1 or equivalent)
- Governing law and jurisdiction

From engineer_identification extract:
- Identity of the Engineer or Employer's Representative
- Notice routing — which entity receives which category of notice
- Split-role pattern (if any)

**If book type is UNCONFIRMED:** State CANNOT ASSESS notice clause
requirements. The applicable notice clause number, time period, and
formal requirements depend on the confirmed book type and edition.

### Layer 1 documents to retrieve (project-specific)

**Critical — retrieve before any notice assessment begins:**
- The Particular Conditions (Clause 1.3 and the notice clause)
- The Contract Data / Appendix to Tender (notice addresses, prescribed
  periods, prescribed methods)
- The notice or instruction under assessment (full document)
- Contemporaneous records for the period around the event (site
  diaries, progress reports, correspondence, RFIs) — required to
  assess the awareness date independently of the notice

**If the Particular Conditions are not retrieved:**
State CANNOT CONFIRM the notice period, the required delivery method,
or the prescribed form. Do not apply any period or requirement as the
applicable standard. Every time bar calculation requires the notice
period to be extracted from the retrieved Particular Conditions.

**If the Contract Data is not retrieved:**
State CANNOT CONFIRM the prescribed notice addresses or periods stated
in the Contract Data.

**If the notice document itself is not retrieved:**
State CANNOT ASSESS notice compliance. Do not assess a notice that
has not been retrieved.

### Layer 2 documents to retrieve (reference standards)

After confirming book type, call `search_chunks` to retrieve from
Layer 2:
- FIDIC Clause 1.3 (notices) for the confirmed book and edition
- FIDIC Clause 20.1 (1999) or Clause 20.2.1 (2017) for the confirmed
  book and edition

**Purpose:** To establish the standard FIDIC notice requirements so
that the Particular Conditions amendment position can be assessed.
The notice period and formal requirements to apply are those in the
Particular Conditions, not the Layer 2 standard form defaults. Layer
2 provides the baseline for comparison only.

---

## Analysis workflow

### Step 1 — Establish the applicable notice requirements for this project
*Contract-type-specific*

From the retrieved Particular Conditions and Contract Data:

**(a) Notice period:**
Extract the notice period for Contractor claims from the Particular
Conditions amendment to the notice clause (Clause 20.1 / 20.2.1 or
the equivalent as amended). This is the period within which the
Contractor must give notice after becoming aware of the event.

**The period to use is the period stated in the retrieved Particular
Conditions.** If no amendment is found AND the Particular Conditions
have been fully retrieved: note that no amendment was found and the
General Conditions period appears to apply — citing the Particular
Conditions as the source of that finding. If the Particular Conditions
have not been retrieved: state CANNOT CONFIRM the notice period.
Do not state any period.

**(b) Formal requirements:**
Extract the formal requirements for valid notices from the retrieved
Particular Conditions amendment to Clause 1.3 and any notice-specific
clause. The requirements to apply are those in the retrieved project
documents.

**(c) Notice addresses and delivery methods:**
Extract from the retrieved Contract Data. Do not assume any address
or delivery method.

**(d) Notice recipient:**
From engineer_identification findings:
- Red Book / Yellow Book: notices go to the Engineer (or the entity
  confirmed as the Engineer from retrieved documents)
- Silver Book: notices go to the Employer's Representative (no Engineer)

### Step 2 — Identify the notice or instruction under assessment
*Contract-type-agnostic*

From the retrieved document, identify:
- Document reference and date
- Issuing party
- Stated delivery method and recipient
- Content: what event or matter does the notice address?
- FIDIC clause cited as the basis (if stated)

If multiple notices are being assessed, assess each separately.

### Step 3 — Establish the awareness date
*Contract-type-agnostic*

The time bar runs from the date the party became aware, or should
reasonably have become aware, of the event. This is not necessarily
the date stated in the notice.

From retrieved contemporaneous records (site diaries, progress reports,
correspondence, RFIs, meeting minutes) — identify any document that
records the same event at a date earlier than the notice.

**If an earlier awareness date is evidenced in a retrieved document:
use that date for the time bar calculation — not the date stated in
the notice. State the evidence and its source.**

**If no contemporaneous records have been retrieved:** State CANNOT
CONFIRM the awareness date from the warehouse documents. Note that
the awareness date stated in the notice has not been independently
verified from contemporaneous records. This is a gap in the analysis,
not a confirmation of the stated date.

### Step 4 — Calculate the time bar position
*Contract-type-specific*

Days elapsed = notice date minus awareness date (as established in
Step 3).

Compare against the notice period extracted from the Particular
Conditions in Step 1.

**This calculation requires both:**
- A confirmed awareness date from retrieved documents
- A confirmed notice period from the retrieved Particular Conditions

**If either is unconfirmed:** State CANNOT CALCULATE time bar position.
Describe what is missing. Do not estimate or approximate.

### Step 5 — Assess form and content compliance
*Contract-type-specific (formal requirements differ by edition)*

For the retrieved notice, assess each formal requirement extracted
from the retrieved Particular Conditions and Contract Data in Step 1.

**Do not apply formal requirements from the standard FIDIC text
without first confirming they have not been amended by the Particular
Conditions.** Where a requirement has been confirmed from retrieved
documents, assess compliance against that requirement and cite the
source. Where a requirement cannot be confirmed from retrieved
documents: state CANNOT CONFIRM whether this requirement applies.

Common requirements to assess from retrieved documents:
- Written form (confirm from the retrieved document itself)
- Signature (confirm from the retrieved document)
- Identification as a Notice (relevant to 2017 editions — confirm
  whether this formal requirement is present in the retrieved PC)
- Delivery method (compare against Contract Data)
- Recipient (compare against engineer_identification findings)
- Identification of the event (confirm from the notice content)
- FIDIC clause reference (confirm from the notice content)

### Step 6 — Assess continuing notice obligations (FIDIC 2017 only)
*Contract-type-specific — 2017 editions only*
*Not applicable to 1999 editions*

Under FIDIC 2017, where a claim event is continuing, the Contractor
must submit updated particulars at intervals. The interval is stated
in the Contract Data — extract from Layer 1. Do not apply any interval
from the standard form without confirming from the retrieved Contract
Data.

**If Contract Data not retrieved:** State CANNOT CONFIRM the required
update interval. Assess whether updated particulars are present in
the warehouse without specifying whether they meet a frequency
requirement.

### Step 7 — Assess Employer claims (FIDIC 2017 only)
*Contract-type-specific — 2017 editions only*
*Not applicable to 1999 editions*

Under FIDIC 2017, Employer claims are subject to the same notice
requirements as Contractor claims. If the Employer has made deductions,
set-offs, or claims: assess whether a corresponding notice was issued
by the Employer using the same framework as Steps 1–5.

---

## Classification and decision rules

**Time bar:**

Both awareness date confirmed AND notice period confirmed from PC →
calculate days elapsed and classify:
- Days elapsed within the notice period: WITHIN TIME
- Days elapsed exceed the notice period: POTENTIALLY TIME-BARRED —
  flag immediately; state awareness date source, notice date, days
  elapsed, notice period source

Awareness date NOT confirmed from retrieved records AND notice period
confirmed → AWARENESS DATE NOT INDEPENDENTLY VERIFIED — calculate
from the date stated in the notice but flag that the calculation is
based on an unverified awareness date; note the risk of an earlier date

Notice period NOT confirmed (PC not retrieved) → CANNOT CALCULATE
TIME BAR — flag; state what is missing

Both unconfirmed → CANNOT ASSESS time bar position

**Form and content:**

All requirements confirmed from retrieved documents and met →
COMPLIANT — cite source for each requirement assessed

One or more requirements not met → DEFECTIVE — state each defect
specifically; cite the requirement source; state whether the defect
is curable or fatal

Requirements cannot be confirmed (PC or Contract Data not retrieved) →
CANNOT CONFIRM compliance with [specific requirement] — state what
is missing

No notice found for a claim present in the warehouse →
NO NOTICE FOUND — flag; call tools to search further; do not
conclude absence without exhausting search

**Recipient routing:**

Notice addressed to confirmed contract administrator → CORRECT ROUTING
Notice addressed to incorrect party per confirmed book type →
DEFECTIVE — WRONG RECIPIENT — state correct recipient and source
Recipient cannot be confirmed (engineer_identification findings
incomplete) → CANNOT CONFIRM routing compliance

---

## When to call tools

**Signal:** A claim is present in the warehouse but no corresponding
notice has been retrieved
**Action:** `search_chunks` with query "[event description] notice
claim"; `get_related_documents` with document type "Notice of Claim"
and "Notice of Delay"
**Look for:** A notice document predating the claim and referencing
the same event

**Signal:** The notice states an awareness date but no contemporaneous
records for that period have been retrieved
**Action:** `search_chunks` with query "[event description]
[approximate date range]"; `get_related_documents` with document
types "Site Diary", "Daily Report", "Progress Report" for the
relevant period
**Look for:** Any document recording the same event at an earlier date

**Signal:** The Particular Conditions have not been retrieved and the
notice period cannot be confirmed
**Action:** `search_chunks` with query "particular conditions notice
claim period days clause 20"; `get_document` on the Particular
Conditions document ID if known
**Look for:** The notice clause and any period stated in the PC

**Signal:** Layer 2 FIDIC notice clause has not been retrieved
**Action:** `search_chunks` with query "[FIDIC book] [edition year]
clause 20 notice claim time bar"
**Look for:** Standard FIDIC Clause 20.1 (1999) or 20.2.1 (2017)
text for the confirmed book

---

## Always flag — regardless of query

1. **POTENTIALLY TIME-BARRED notice** — always flag when days elapsed
   exceed the confirmed notice period; state the consequence in one
   sentence: the right to the claim may be extinguished subject to the
   governing law position on strict enforcement.

2. **Notice period not confirmed from Particular Conditions** — always
   flag when the notice period cannot be extracted from retrieved PC;
   state that no time bar calculation can be made.

3. **Awareness date not independently verified** — always flag when
   no contemporaneous record has been retrieved that independently
   confirms the awareness date stated in the notice.

4. **No notice found for a claim present in the warehouse** — always
   flag after tools search returns nothing; state the claim reference
   and the absence.

5. **Silver Book: notice addressed to an Engineer** — always flag; the
   Silver Book has no Engineer; state correct recipient.

6. **FIDIC 2017: Employer deductions without corresponding Employer
   notice** — always flag when Employer deductions exist in the
   warehouse and no Employer notice under Clause 20.2.1 has been found.

---

## Output format

```
## Notice and Instruction Compliance Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved, with reference numbers and dates.]

### Documents Not Retrieved
[List every document required for this analysis not found in the
warehouse. State which analysis steps are affected.]

### Layer 2 Reference Retrieved
[State whether FIDIC Clause 1.3 and the relevant notice clause were
retrieved from Layer 2. If not: state analytical knowledge applied.]

### Applicable Notice Requirements (this project)
Notice period: [value from retrieved PC and Contract Data / CANNOT CONFIRM — PC not retrieved]
Source: [Particular Conditions reference and clause / NOT RETRIEVED]
Delivery method required: [from retrieved Contract Data / CANNOT CONFIRM]
Notice recipient: [from engineer_identification findings / CANNOT CONFIRM]
Edition-specific formal requirements: [from retrieved PC / CANNOT CONFIRM]

### Notice Register

| # | Ref | Notice date | Awareness date | Source of awareness date | Days elapsed | Period | Classification |
|---|---|---|---|---|---|---|---|
| 1 | [ref] | [date] | [date / UNVERIFIED] | [doc or UNVERIFIED] | [N or CANNOT CALC] | [from PC / NOT CONFIRMED] | [classification] |

### Findings by Notice

**[Notice reference]**
Classification: [COMPLIANT / DEFECTIVE / POTENTIALLY TIME-BARRED /
AWARENESS DATE NOT INDEPENDENTLY VERIFIED / CANNOT CALCULATE TIME BAR /
NO NOTICE FOUND / CANNOT ASSESS]
Notice date: [date — source document]
Awareness date: [date — source document, or STATED IN NOTICE ONLY —
NOT INDEPENDENTLY VERIFIED]
Days elapsed: [number, or CANNOT CALCULATE — reason]
Applicable notice period: [from retrieved PC / CANNOT CONFIRM]
Form compliance:
  - Written: [YES / NO — from retrieved document]
  - Delivery method: [method used vs required from Contract Data / CANNOT CONFIRM REQUIREMENT]
  - Recipient: [named recipient vs confirmed administrator / CORRECT / WRONG / CANNOT CONFIRM]
  - Event identified: [YES / NO — from notice content]
  - FIDIC clause cited: [YES — clause / NO]
Continuing notices (2017 only): [ASSESSED / NOT APPLICABLE]
Source documents: [list]
Finding: [from retrieved documents only]

### Employer Claims (FIDIC 2017 only)
[Assessment or NOT APPLICABLE for 1999 editions]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any period, threshold, or requirement
from this section without first confirming it from retrieved project
documents.*

**FIDIC notice provisions — structural summary (analytical reference):**
FIDIC 1999 Clause 1.3 requires notices to be in writing and delivered
by the specified method to the specified address. The 2017 edition
significantly strengthened the formal requirements — notices must
satisfy five conditions including being identified as a "Notice"
(the defined term) and signed by the issuing party's representative.
The key difference between 1999 and 2017 is the formality level —
2017 is more prescriptive. Retrieve the applicable clause from
Layer 2 to confirm what the standard says, then check the Particular
Conditions for any amendment.

**Time bar — analytical reference:**
The 28-day period stated in the FIDIC General Conditions is the
standard form default. GCC Particular Conditions routinely amend
this — sometimes shorter (14 or 21 days), sometimes extended.
Some GCC government Employer forms use 7-day periods. The period
to apply is always the period in the retrieved Particular Conditions,
not the General Conditions default. Never apply any default without
retrieved Particular Conditions confirmation.

**Awareness date — analytical reference:**
The time bar runs from the date the claimant became aware or should
reasonably have become aware of the event. The objective test
("should have been aware") means site records and contemporaneous
correspondence can evidence an earlier awareness date than what
the notice states. Retrieve contemporaneous records to verify.

**GCC jurisdictional context — analytical reference:**
UAE onshore courts have applied the good faith doctrine (UAE Civil
Code Art. 246) in limited cases to soften strict time bar enforcement.
DIFC Court follows English common law — strict enforcement applies.
Saudi Arabia and Qatar: strict enforcement is the norm. These are
contextual frameworks for flagging jurisdictional risk — the actual
governing law must be confirmed from the retrieved contract documents.
