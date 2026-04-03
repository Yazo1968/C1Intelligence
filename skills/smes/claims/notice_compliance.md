# Notice Compliance

**Skill type:** Mixed
- Contract-type-specific: notice clause numbers, time bar periods,
  formal requirements, and routing differ by FIDIC book and edition;
  Particular Conditions amendments are project-specific
- Contract-type-agnostic: the requirement to verify form, timing,
  routing, and content compliance applies regardless of book type
**Layer dependency:**
- Layer 1 — project documents: the notice document under assessment;
  Particular Conditions (notice clause and Clause 1.3 amendments);
  Contract Data (prescribed periods, addresses, delivery methods);
  contemporaneous records establishing awareness date
- Layer 2 — reference standards: FIDIC Clause 1.3 and the relevant
  notice clause (20.1 for 1999 / 20.2.1 for 2017) for the confirmed
  book and edition
**Domain:** Claims & Disputes SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when retrieved chunks contain a Notice of Claim, Notice of Delay,
Notice of Potential Claim, or any letter asserting a right to additional
time or money. Apply when a query concerns whether a notice was validly
given, defective, or time-barred. Apply when a claim submission is
present in the warehouse but no corresponding notice has been found.

---

## Before you begin

### Foundational requirements

This skill is contract-type-specific. Before any notice assessment
begins the following must be established from the invoking orchestrator
findings or by retrieval:

- FIDIC book: Red Book / Yellow Book / Silver Book
- FIDIC edition: 1999 or 2017
- Contract administrator identity (Engineer or Employer's Representative)

**If book type is UNCONFIRMED:** State CANNOT ASSESS notice clause
requirements. The applicable clause number, period, and formal
requirements depend on the confirmed book type and edition. Do not
proceed.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The Particular Conditions — specifically the notice clause and
  Clause 1.3 amendments
- The Contract Data / Appendix to Tender — notice periods, prescribed
  delivery methods, notice addresses
- The notice document under assessment (full document)
- Contemporaneous records for the period around the event: site
  diaries, progress reports, RFIs, correspondence, meeting minutes

**If the Particular Conditions are not retrieved:**
State CANNOT CONFIRM the notice period, delivery method, or formal
requirements. Do not apply any period or requirement. Do not state
any notice period. Every time bar calculation depends on the notice
period extracted from the retrieved Particular Conditions.

**If the notice document itself is not retrieved:**
State CANNOT ASSESS notice compliance. Do not proceed with assessment
of a notice that has not been retrieved.

**If no contemporaneous records are retrieved:**
State that the awareness date stated in the notice has not been
independently verified from warehouse documents. This is a gap in
the analysis, not a confirmation of the stated date.

### Layer 2 documents to retrieve (reference standards)

After confirming book type, call `search_chunks` to retrieve from
Layer 2:
- FIDIC Clause 1.3 for the confirmed book and edition
- FIDIC Clause 20.1 (1999 editions) or Clause 20.2.1 (2017 editions)
  for the confirmed book

**Purpose:** To establish the standard FIDIC baseline so that
Particular Conditions amendments can be assessed against it. The
notice period and formal requirements to apply are always those in
the retrieved Particular Conditions — not the Layer 2 standard form
defaults. Layer 2 is the comparison baseline only.

---

## Analysis workflow

### Step 1 — Establish the applicable notice requirements for this project
*Contract-type-specific*

From the retrieved Particular Conditions and Contract Data extract:

**(a) Notice period:**
The period within which notice must be given after the claimant
became aware of the event. This is the period stated in the retrieved
Particular Conditions — not the standard form default.

If no amendment is found AND the Particular Conditions have been
fully retrieved: note that no amendment was found and the General
Conditions period appears to apply — cite the Particular Conditions
document as the source. If the Particular Conditions have not been
retrieved: state CANNOT CONFIRM the notice period. Do not state
any period.

**(b) Formal requirements:**
Extract from the retrieved Particular Conditions amendment to
Clause 1.3 and any notice-specific clause. Apply only what the
retrieved documents state.

**(c) Delivery method and notice addresses:**
Extract from the retrieved Contract Data. Do not assume any method
or address.

**(d) Notice recipient:**
- Red Book / Yellow Book: notices go to the Engineer as confirmed
  from the invoking orchestrator findings
- Silver Book: notices go to the Employer's Representative — there
  is no Engineer on a Silver Book project

### Step 2 — Identify the notice under assessment
*Contract-type-agnostic*

From the retrieved notice document:
- Document reference and date
- Issuing party
- Stated delivery method and recipient
- Event described: what does the notice say happened?
- FIDIC clause cited (if stated)

If multiple notices are being assessed, assess each separately.

### Step 3 — Establish the awareness date
*Contract-type-agnostic*

The time bar runs from the date the party became aware, or should
reasonably have become aware, of the event. This is not necessarily
the date stated in the notice.

From retrieved contemporaneous records, identify any document that
records the same event at a date earlier than the notice date.

**If an earlier date is evidenced in a retrieved document:** Use
that date for the time bar calculation — not the date stated in
the notice. State the earlier-date document and its reference.

**If no contemporaneous records have been retrieved:** State CANNOT
CONFIRM the awareness date from warehouse documents. Note that the
date stated in the notice has not been independently verified. Flag
this gap — an earlier awareness date evidenced by documents not in
the warehouse cannot be excluded.

### Step 4 — Calculate the time bar position
*Contract-type-specific*

Days elapsed = notice date minus awareness date (from Step 3).

Compare against the notice period extracted from the Particular
Conditions in Step 1.

**Both inputs are required:**
- A confirmed awareness date from retrieved documents
- A confirmed notice period from the retrieved Particular Conditions

**If either is unconfirmed:** State CANNOT CALCULATE time bar
position. State what is missing. Do not estimate or approximate.

### Step 5 — Assess form and content compliance
*Contract-type-specific (formal requirements differ by edition)*

For the retrieved notice, assess each formal requirement extracted
from the retrieved Particular Conditions and Contract Data in Step 1.

Do not apply requirements from the standard FIDIC text without first
confirming they have not been amended by the Particular Conditions.
Where a requirement cannot be confirmed from retrieved documents:
state CANNOT CONFIRM whether this requirement applies.

Requirements to assess from retrieved documents:
- Written form: confirm from the retrieved document
- Delivery method: compare against retrieved Contract Data
- Recipient: compare against invoking orchestrator findings
- Event identified: confirm from notice content
- FIDIC clause cited: confirm from notice content
- Signature (2017 editions): confirm whether this requirement is
  in the retrieved PC and whether the document satisfies it
- Identification as a "Notice" defined term (2017 editions):
  confirm from retrieved PC and document

### Step 6 — Assess continuing notice obligations
*Contract-type-specific — 2017 editions only*
*Not applicable to 1999 editions*

Under FIDIC 2017, where a claim event is continuing, updated
particulars must be submitted at intervals. The interval is in
the Contract Data — extract from Layer 1. Do not apply any interval
without confirming from retrieved Contract Data.

**If Contract Data not retrieved:** State CANNOT CONFIRM the required
update interval.

### Step 7 — Assess Employer claims (FIDIC 2017 only)
*Contract-type-specific — 2017 editions only*
*Not applicable to 1999 editions*

Under FIDIC 2017, Employer claims are subject to the same notice
requirements as Contractor claims. If Employer deductions, set-offs,
or claims are present in the warehouse: apply the same Steps 1–5
framework and assess whether a corresponding Employer notice exists.

---

## Classification and decision rules

**Time bar:**

Both awareness date confirmed AND notice period confirmed from PC:
- Days within period → WITHIN TIME
- Days exceed period → POTENTIALLY TIME-BARRED — flag immediately;
  state awareness date and source, notice date, days elapsed, notice
  period and its source

Awareness date NOT confirmed from retrieved records AND notice period
confirmed → AWARENESS DATE NOT INDEPENDENTLY VERIFIED — calculate
from the date stated in the notice but flag that the calculation
relies on an unverified date; note the risk of an earlier date

Notice period NOT confirmed (PC not retrieved) →
CANNOT CALCULATE TIME BAR — state what is missing

Both unconfirmed → CANNOT ASSESS time bar position

**Form and content:**

All requirements confirmed from retrieved documents and met →
COMPLIANT — cite source for each requirement

One or more requirements not met → DEFECTIVE — state each defect
specifically and its source; state whether curable or fatal

Requirements cannot be confirmed (PC or Contract Data not retrieved)
→ CANNOT CONFIRM compliance with [specific requirement]

No notice found for a claim in the warehouse →
NO NOTICE FOUND — call tools to search; do not conclude absence
without exhausting search

**Recipient routing:**

Notice addressed to confirmed contract administrator →
CORRECT ROUTING
Notice addressed to incorrect party for confirmed book type →
DEFECTIVE — WRONG RECIPIENT — state correct recipient and source
Recipient cannot be confirmed → CANNOT CONFIRM routing compliance

---

## When to call tools

**Signal:** A claim is present but no corresponding notice retrieved
**Action:** `search_chunks` with query "[event description] notice
claim"; `get_related_documents` with document types "Notice of Claim",
"Notice of Delay"
**Look for:** A notice document predating the claim referencing the
same event

**Signal:** Notice states an awareness date but no contemporaneous
records for that period have been retrieved
**Action:** `search_chunks` with query "[event description]
[approximate date range]"; `get_related_documents` with document
types "Site Diary", "Daily Report", "Progress Report"
**Look for:** Any document recording the same event at an earlier date

**Signal:** Particular Conditions not retrieved — notice period
cannot be confirmed
**Action:** `search_chunks` with query "particular conditions notice
claim period days clause 20"; `get_document` on PC document ID
if known from orchestrator findings
**Look for:** The notice clause and any period stated in the PC

**Signal:** Layer 2 FIDIC notice clause not retrieved
**Action:** `search_chunks` with query "[FIDIC book] [edition] clause
20 notice claim time bar"
**Look for:** Standard FIDIC Clause 20.1 (1999) or 20.2.1 (2017) text

---

## Always flag — regardless of query

1. **POTENTIALLY TIME-BARRED** — state the consequence: the right
   to the claim may be extinguished subject to the governing law
   position on strict enforcement.

2. **Notice period not confirmed from Particular Conditions** — state
   that no time bar calculation can be made.

3. **Awareness date not independently verified** — state that the
   analysis relies on the date stated in the notice which has not
   been confirmed by contemporaneous records.

4. **No notice found for a claim in the warehouse** — state the
   claim reference and the absence after tool search.

5. **Silver Book: notice addressed to an Engineer** — the Silver Book
   has no Engineer; state correct recipient.

6. **FIDIC 2017: Employer deductions without a corresponding
   Employer notice** — state the absence and its implication.

---

## Output format

```
## Notice Compliance Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2 Reference Retrieved
[State whether FIDIC Clause 1.3 and the notice clause were retrieved
from Layer 2. If not: state analytical knowledge applied.]

### Applicable Notice Requirements (this project)
Notice period: [value from retrieved PC / CANNOT CONFIRM — PC not retrieved]
Source: [PC reference and clause / NOT RETRIEVED]
Delivery method required: [from retrieved Contract Data / CANNOT CONFIRM]
Notice recipient: [from orchestrator findings / CANNOT CONFIRM]
Formal requirements (2017 specific): [from retrieved PC / CANNOT CONFIRM]

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
Awareness date: [date — source / STATED IN NOTICE ONLY — NOT VERIFIED]
Days elapsed: [number / CANNOT CALCULATE — reason]
Applicable notice period: [from retrieved PC / CANNOT CONFIRM]
Form compliance:
  Written: [YES / NO]
  Delivery method: [used vs required from Contract Data / CANNOT CONFIRM REQUIREMENT]
  Recipient: [named vs confirmed administrator / CORRECT / WRONG / CANNOT CONFIRM]
  Event identified: [YES / NO]
  FIDIC clause cited: [YES — clause / NO]
Continuing notices (2017 only): [ASSESSED / NOT APPLICABLE]
Source documents: [list with references]
Finding: [from retrieved documents only]

### Employer Claims (FIDIC 2017 only)
[Assessment or NOT APPLICABLE]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any period, requirement, or position
from this section without first confirming it from retrieved project
documents.*

**FIDIC notice provisions — structural summary (analytical reference):**
FIDIC 1999 Clause 1.3 requires notices in writing delivered by the
specified method. The 2017 edition strengthened formal requirements —
notices must satisfy five conditions including being identified as
a "Notice" (the defined term) and signed by the issuing party's
representative. The 2017 edition is more prescriptive. Retrieve the
applicable clause from Layer 2 to confirm the standard text, then
check the Particular Conditions for any amendment. The amendment
governs — not the standard text.

**Time bar — analytical reference:**
The FIDIC General Conditions contain a standard form default period.
GCC Particular Conditions routinely amend this — sometimes shorter,
sometimes extended. Government Employer forms in some jurisdictions
use very short periods. The period to apply is always from the
retrieved Particular Conditions. Never apply any default period
without retrieved Particular Conditions confirmation.

**Awareness date — analytical reference:**
The time bar runs from when the party became aware or should
reasonably have become aware. The objective test means contemporaneous
records can evidence an earlier date than the notice states. Retrieve
contemporaneous records to verify the date independently.

**GCC jurisdictional context — analytical reference:**
UAE onshore courts have applied UAE Civil Code Art. 246 good faith
doctrine in limited cases. DIFC Court follows English common law —
strict enforcement. Saudi Arabia and Qatar: strict enforcement is
the norm. These are contextual flags for jurisdictional risk — the
actual governing law must be confirmed from the retrieved contract.
