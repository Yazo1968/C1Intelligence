# Notice and Instruction Compliance

**Skill type:** Mixed
- Contract-type-specific: notice requirements, time bar periods, and
  routing differ by standard form and version; amendment provisions
  affecting notice requirements are project-specific
- Contract-type-agnostic: the requirement to verify form, timing,
  routing, and content compliance applies regardless of standard form
**Layer dependency:**
- Layer 1 — project documents: the specific notice or instruction
  under assessment; amendment document (notice requirements and
  any amendments); contract data (notice periods, addresses);
  contemporaneous records establishing awareness date
- Layer 2b — reference standards: Notice provisions from the governing
  standard form (whatever form is in the warehouse) for the confirmed
  standard form and version
**Domain:** Legal & Contractual SME
**Invoked by:** Legal orchestrator

---

## When to apply this skill

Apply when a query concerns whether a notice or instruction was validly
issued — including notice of claim, notice of delay, contract
administrator instruction, variation instruction, suspension notice,
termination notice, or any contractual communication whose validity
depends on form, timing, or routing. Apply when assessing whether a
time bar has been triggered or whether a communication constitutes a
valid notice.

---

## Before you begin

### Foundational requirements
Read contract_assembly and engineer_identification findings first.

From contract_assembly extract:
- Confirmed standard form and version — required before any notice
  provision can be applied
- Amendment provisions affecting notice requirements or time bar periods
- Governing law and jurisdiction

From engineer_identification extract:
- Identity of the contract administrator
- Notice routing — which entity receives which category of notice
- Split-role pattern (if any)

**If standard form is UNCONFIRMED:** State CANNOT ASSESS notice
requirements. The applicable notice provision, time period, and
formal requirements depend on the confirmed standard form and version.

### Layer 1 documents to retrieve (project-specific)

**Critical — retrieve before any notice assessment begins:**
- The amendment document (notice provisions and any amendments)
- The contract data or equivalent schedule (notice addresses,
  prescribed periods, prescribed methods)
- The notice or instruction under assessment (full document)
- Contemporaneous records for the period around the event (site
  diaries, progress reports, correspondence) — required to assess
  the awareness date independently of the notice

**If the amendment document is not retrieved:**
State CANNOT CONFIRM the notice period, the required delivery method,
or the prescribed form. Do not apply any period or requirement as the
applicable standard. Every time bar calculation requires the notice
period to be extracted from the retrieved amendment document.

**If the contract data is not retrieved:**
State CANNOT CONFIRM the prescribed notice addresses or periods stated
in the contract data.

**If the notice document itself is not retrieved:**
State CANNOT ASSESS notice compliance. Do not assess a notice that
has not been retrieved.

### Layer 2b documents to retrieve (reference standards)

After confirming standard form, call `search_chunks` with
`layer_type = '2b'` to retrieve:
- The general notice provision for the confirmed standard form
  (search by subject matter: "notices written form delivery method
  receipt")
- The claim notice or notice of claim provision (search by subject
  matter: "notice of claim time bar contractor aware event")

**Purpose:** To establish the standard form notice requirements so
that the amendment position can be assessed. The notice period and
formal requirements to apply are those in the amendment document,
not the Layer 2b standard form defaults. Layer 2b provides the
baseline for comparison only.

**If the governing standard form is not retrieved from Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE for the notice
provisions. Do not apply notice requirements from training knowledge.

---

## Analysis workflow

### Step 1 — Establish the applicable notice requirements for this project
*Contract-type-specific*

From the retrieved amendment document and contract data:

**(a) Notice period:**
Extract the notice period for contractor claims from the amendment
document (retrieve the applicable claim notice provision from Layer 2b
first; then check the amendment document for any modification).

**The period to use is the period stated in the retrieved amendment
document.** If no amendment is found AND the amendment document has
been fully retrieved: note that no amendment was found and the General
Conditions period appears to apply — citing the amendment document as
the source of that finding. If the amendment document has not been
retrieved: state CANNOT CONFIRM the notice period. Do not state any
period.

**(b) Formal requirements:**
Extract the formal requirements for valid notices from the retrieved
amendment document and any notice-specific provision. The requirements
to apply are those in the retrieved project documents.

**(c) Notice addresses and delivery methods:**
Extract from the retrieved contract data. Do not assume any address
or delivery method.

**(d) Notice recipient:**
From engineer_identification findings: confirm the entity to whom
notices must be routed under the confirmed standard form and the
retrieved amendment document.

### Step 2 — Identify the notice or instruction under assessment
*Contract-type-agnostic*

From the retrieved document, identify:
- Document reference and date
- Issuing party
- Stated delivery method and recipient
- Content: what event or matter does the notice address?
- Contractual clause cited as the basis (if stated)

If multiple notices are being assessed, assess each separately.

### Step 3 — Establish the awareness date
*Contract-type-agnostic*

The time bar runs from the date the party became aware, or should
reasonably have become aware, of the event. This is not necessarily
the date stated in the notice.

From retrieved contemporaneous records (site diaries, progress reports,
correspondence, meeting minutes) — identify any document that records
the same event at a date earlier than the notice.

**If an earlier awareness date is evidenced in a retrieved document:
use that date for the time bar calculation — not the date stated in
the notice. State the evidence and its source.**

**If no contemporaneous records have been retrieved:** State CANNOT
CONFIRM the awareness date from the warehouse documents. Note that
the awareness date stated in the notice has not been independently
verified. This is a gap in the analysis, not a confirmation of the
stated date.

### Step 4 — Calculate the time bar position
*Contract-type-specific*

Days elapsed = notice date minus awareness date (as established in
Step 3).

Compare against the notice period extracted from the amendment
document in Step 1.

**This calculation requires both:**
- A confirmed awareness date from retrieved documents
- A confirmed notice period from the retrieved amendment document

**If either is unconfirmed:** State CANNOT CALCULATE time bar position.
Describe what is missing. Do not estimate or approximate.

### Step 5 — Assess form and content compliance
*Contract-type-specific (formal requirements differ by standard form
and version)*

For the retrieved notice, assess each formal requirement extracted
from the retrieved amendment document and contract data in Step 1.

**Do not apply formal requirements from the standard form text
without first confirming they have not been amended by the amendment
document.** Where a requirement has been confirmed from retrieved
documents, assess compliance against that requirement and cite the
source. Where a requirement cannot be confirmed: state CANNOT CONFIRM
whether this requirement applies.

Common requirements to assess from retrieved documents:
- Written form (confirm from the retrieved document itself)
- Signature (confirm from the retrieved document)
- Identification as a notice (confirm whether this formal requirement
  is present in the retrieved amendment document or standard form
  provision)
- Delivery method (compare against contract data)
- Recipient (compare against engineer_identification findings)
- Identification of the event (confirm from the notice content)
- Contractual clause cited (confirm from the notice content)

### Step 6 — Assess continuing notice obligations
*Contract-type-specific — applicable only if required by the confirmed
standard form and version*

Some standard forms require that, where a claim event is continuing,
the claimant must submit updated particulars at intervals. Retrieve
the applicable provision from Layer 2b to confirm whether this
obligation applies under the confirmed standard form. The interval
is stated in the contract data — extract from Layer 1.

**If the continuing notice obligation is not confirmed from retrieved
documents:** Do not apply it. Assess whether updated particulars are
present in the warehouse without specifying whether they meet a
frequency requirement.

### Step 7 — Assess employer claims notice
*Contract-type-specific — applicable only if required by the confirmed
standard form and version*

Some standard forms subject employer claims to the same notice
requirements as contractor claims. Retrieve the applicable provision
from Layer 2b to confirm whether this applies under the confirmed
standard form. If the employer has made deductions, set-offs, or
claims: assess whether a corresponding notice was issued by the
employer using the same framework as Steps 1–5.

---

## Classification and decision rules

**Time bar:**

Both awareness date confirmed AND notice period confirmed from
amendment document → calculate days elapsed and classify:
- Days elapsed within the notice period: WITHIN TIME
- Days elapsed exceed the notice period: POTENTIALLY TIME-BARRED —
  flag immediately; state awareness date source, notice date, days
  elapsed, notice period source

Awareness date NOT confirmed from retrieved records AND notice
period confirmed → AWARENESS DATE NOT INDEPENDENTLY VERIFIED —
calculate from the date stated in the notice but flag that the
calculation is based on an unverified awareness date; note the
risk of an earlier date

Notice period NOT confirmed (amendment document not retrieved) →
CANNOT CALCULATE TIME BAR — flag; state what is missing

Both unconfirmed → CANNOT ASSESS time bar position

**Form and content:**

All requirements confirmed from retrieved documents and met →
COMPLIANT — cite source for each requirement assessed

One or more requirements not met → DEFECTIVE — state each defect
specifically; cite the requirement source; state whether the defect
is curable or fatal

Requirements cannot be confirmed (amendment document or contract data
not retrieved) → CANNOT CONFIRM compliance with [specific requirement]
— state what is missing

No notice found for a claim present in the warehouse →
NO NOTICE FOUND — flag; call tools to search further; do not
conclude absence without exhausting search

**Recipient routing:**

Notice addressed to confirmed contract administrator → CORRECT ROUTING
Notice addressed to incorrect party per confirmed standard form →
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

**Signal:** The amendment document has not been retrieved and the
notice period cannot be confirmed
**Action:** `search_chunks` with query "particular conditions notice
claim period days"; `get_document` on the amendment document ID
if known
**Look for:** The notice provision and any period stated in the
amendment document

**Signal:** Layer 2b notice provision has not been retrieved
**Action:** `search_chunks` with `layer_type = '2b'` and query
"[standard form name] notice claim time bar awareness"
**Look for:** Standard form notice of claim provision for comparison
against the amendment document

---

## Always flag — regardless of query

1. **POTENTIALLY TIME-BARRED notice** — always flag when days elapsed
   exceed the confirmed notice period; state the consequence in one
   sentence: the right to the claim may be extinguished subject to the
   governing law position on strict enforcement.

2. **Notice period not confirmed from amendment document** — always
   flag when the notice period cannot be extracted from the retrieved
   amendment document; state that no time bar calculation can be made.

3. **Awareness date not independently verified** — always flag when
   no contemporaneous record has been retrieved that independently
   confirms the awareness date stated in the notice.

4. **No notice found for a claim present in the warehouse** — always
   flag after tools search returns nothing; state the claim reference
   and the absence.

5. **Notice recipient inconsistent with confirmed contract
   administrator** — always flag when a notice is addressed to an
   entity other than the confirmed contract administrator; state the
   routing issue and its potential effect on validity.

6. **Employer deductions or claims without corresponding notice** —
   if the confirmed standard form requires employer claims to follow
   the same notice procedure, and employer deductions exist without
   a retrieved employer notice: flag after confirming the requirement
   from Layer 2b.

7. **Governing standard not retrieved from Layer 2b** — flag when the
   notice provisions could not be retrieved; state that no time bar
   calculation or form compliance assessment can be made; state what
   standard would need to be ingested.

---

## Output format

```
## Notice and Instruction Compliance Assessment

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
[List every document retrieved, with reference numbers and dates.]

### Documents Not Retrieved
[List every document required for this analysis not found in the
warehouse. State which analysis steps are affected.]

### Layer 2b Reference Retrieved
[State whether the notice provisions for the confirmed standard form
were retrieved from Layer 2b. If not: state CANNOT CONFIRM —
STANDARD FORM NOT IN WAREHOUSE and list which analysis steps
are affected.]

### Applicable Notice Requirements (this project)
Notice period: [value from retrieved amendment document and contract
data / CANNOT CONFIRM — amendment document not retrieved]
Source: [amendment document reference and clause / NOT RETRIEVED]
Delivery method required: [from retrieved contract data / CANNOT CONFIRM]
Notice recipient: [from engineer_identification findings / CANNOT CONFIRM]
Formal requirements: [from retrieved amendment document and Layer 2b /
CANNOT CONFIRM]

### Notice Register

| # | Ref | Notice date | Awareness date | Source of awareness date | Days elapsed | Period | Classification |
|---|---|---|---|---|---|---|---|
| 1 | [ref] | [date] | [date / UNVERIFIED] | [doc or UNVERIFIED] | [N or CANNOT CALC] | [from amendment doc / NOT CONFIRMED] | [classification] |

### Findings by Notice

**[Notice reference]**
Classification: [COMPLIANT / DEFECTIVE / POTENTIALLY TIME-BARRED /
AWARENESS DATE NOT INDEPENDENTLY VERIFIED / CANNOT CALCULATE TIME BAR /
NO NOTICE FOUND / CANNOT ASSESS]
Notice date: [date — source document]
Awareness date: [date — source document, or STATED IN NOTICE ONLY —
NOT INDEPENDENTLY VERIFIED]
Days elapsed: [number, or CANNOT CALCULATE — reason]
Applicable notice period: [from retrieved amendment document / CANNOT CONFIRM]
Form compliance:
  - Written: [YES / NO — from retrieved document]
  - Delivery method: [method used vs required from contract data /
    CANNOT CONFIRM REQUIREMENT]
  - Recipient: [named recipient vs confirmed administrator /
    CORRECT / WRONG / CANNOT CONFIRM]
  - Event identified: [YES / NO — from notice content]
  - Contractual clause cited: [YES — clause / NO]
Continuing notices: [ASSESSED / NOT APPLICABLE / NOT CONFIRMED FROM
LAYER 2b]
Source documents: [list]
Finding: [from retrieved documents only]

### Employer Claims Notice Assessment
[Assessment if confirmed applicable from Layer 2b / NOT APPLICABLE —
standard form provision not requiring this / CANNOT CONFIRM — Layer 2b
not retrieved]

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

**Notice provisions — structural summary (analytical reference):**
Standard forms of contract impose notice requirements on parties wishing
to claim time extensions, additional cost, or other relief. These
provisions typically require notice within a specified period after the
party becomes aware of the event, delivered in writing to the contract
administrator. The specific period, form requirements, and consequences
of non-compliance vary significantly between standard forms and between
versions of the same standard form. Some standard forms are more
prescriptive about formal requirements than others. Retrieve the
applicable provision from Layer 2b before applying any requirement.

**Time bar — analytical reference:**
The notice period is stated in the contract — either in the general
conditions or as amended by the particular conditions. Amendment
documents frequently modify notice periods. Some amended forms use
shorter periods; some use longer periods. The period to apply is
always the period in the retrieved documents — never a default.

**Awareness date — analytical reference:**
The time bar runs from the date the claimant became aware or should
reasonably have become aware of the event. The objective test
("should have been aware") means site records and contemporaneous
correspondence can evidence an earlier awareness date than what
the notice states. Retrieve contemporaneous records to verify.

**Governing law — analytical reference:**
The enforceability of time bars and the consequences of non-compliance
vary by governing law. Some legal systems apply time bars strictly;
others apply good faith or waiver doctrines that may soften strict
enforcement. The governing law must be confirmed from the retrieved
contract documents — retrieve from Layer 1. Do not assume a governing
law or its approach to time bar enforcement.
