# Notice Compliance

**Skill type:** Mixed
- Contract-type-specific: notice provisions, time bar periods, formal
  requirements, and routing differ by standard form and version;
  amendment provisions are project-specific
- Contract-type-agnostic: the requirement to verify form, timing,
  routing, and content compliance applies regardless of standard form
**Layer dependency:**
- Layer 1 — project documents: the notice document under assessment;
  amendment document (notice provision and general notice requirement
  amendments); Contract Data (prescribed periods, addresses, delivery
  methods); contemporaneous records establishing awareness date
- Layer 2b — reference standards: notice provisions from the governing
  standard form (whatever form is in the warehouse)
**Domain:** Legal & Contractual SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

This skill governs notice compliance as a procedural gateway to claim
entitlement — whether the prerequisites for a specific EOT, prolongation
cost, disruption, or dispute resolution claim have been satisfied. For
general validity of notices and instructions assessed independently of a
specific claim entitlement, route to
`notice_and_instruction_compliance.md`.

Apply when retrieved documents contain a notice of claim, notice of
delay, notice of potential claim, or any letter asserting a right to
additional time or money. Apply when a query concerns whether a notice
was validly given, defective, or time-barred. Apply when a claim
submission is present in the warehouse but no corresponding notice
has been found.

---

## Before you begin

### Foundational requirements

This skill is contract-type-specific. Before any notice assessment
begins the following must be established from the invoking orchestrator
findings or by retrieval:

- Confirmed standard form and version
- Contract administrator identity (from orchestrator findings)

**If standard form is UNCONFIRMED:** State CANNOT ASSESS notice
requirements. The applicable notice provision, time period, and formal
requirements depend on the confirmed standard form and version. Do not
proceed.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The amendment document — specifically the notice provision and
  general notice requirement amendments
- The Contract Data — notice periods, prescribed delivery methods,
  notice addresses
- The notice document under assessment (full document)
- Contemporaneous records for the period around the event: site
  diaries, progress reports, RFIs, correspondence, meeting minutes

**If the amendment document is not retrieved:**
State CANNOT CONFIRM the notice period, delivery method, or formal
requirements. Do not apply any period or requirement. Every time bar
calculation depends on the notice period extracted from the retrieved
amendment document.

**If the notice document itself is not retrieved:**
State CANNOT ASSESS notice compliance. Do not proceed with assessment
of a notice that has not been retrieved.

**If no contemporaneous records are retrieved:**
State that the awareness date stated in the notice has not been
independently verified from warehouse documents. This is a gap in the
analysis, not a confirmation of the stated date.

### Layer 2b documents to retrieve (reference standards)

After confirming standard form, call `search_chunks` with
`layer_type = '2b'` to retrieve:
- The general notice provision for the confirmed standard form
  (search by subject matter: "notices written form delivery method
  receipt")
- The claim notice provision (search by subject matter: "notice of
  claim time bar contractor aware event")

**Purpose:** To establish the standard form notice requirements so
that amendment provisions can be assessed against the baseline. The
notice period and formal requirements to apply are always those in
the retrieved amendment document — not the Layer 2b standard form
defaults. Layer 2b is the comparison baseline only.

**If the governing standard form is not retrieved from Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE for the notice
provisions. Do not apply notice requirements from training knowledge.

---

## Analysis workflow

### Step 1 — Establish the applicable notice requirements for this project
*Contract-type-specific*

From the retrieved amendment document and Contract Data extract:

**(a) Notice period:**
The period within which notice must be given after the claimant
became aware of the event. This is the period stated in the retrieved
amendment document — not any standard form default.

If no amendment is found AND the amendment document has been fully
retrieved: note that no amendment was found and the General Conditions
period appears to apply — citing the amendment document as the source.
If the amendment document has not been retrieved: state CANNOT CONFIRM
the notice period. Do not state any period.

**(b) Formal requirements:**
Extract from the retrieved amendment document and any notice-specific
provision. Apply only what the retrieved documents state.

**(c) Delivery method and notice addresses:**
Extract from the retrieved Contract Data. Do not assume any method
or address.

**(d) Notice recipient:**
From the invoking orchestrator findings: confirm the entity to whom
notices must be routed under the confirmed standard form and the
retrieved amendment document.

### Step 2 — Identify the notice under assessment
*Contract-type-agnostic*

From the retrieved notice document:
- Document reference and date
- Issuing party
- Stated delivery method and recipient
- Event described: what does the notice say happened?
- Contractual clause cited (if stated)

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

Compare against the notice period extracted from the amendment
document in Step 1.

**Both inputs are required:**
- A confirmed awareness date from retrieved documents
- A confirmed notice period from the retrieved amendment document

**If either is unconfirmed:** State CANNOT CALCULATE time bar position.
State what is missing. Do not estimate or approximate.

### Step 5 — Assess form and content compliance
*Contract-type-specific (formal requirements differ by standard form
and version)*

For the retrieved notice, assess each formal requirement extracted
from the retrieved amendment document and Contract Data in Step 1.

Do not apply requirements from the standard form text without first
confirming they have not been amended by the amendment document.
Where a requirement cannot be confirmed from retrieved documents:
state CANNOT CONFIRM whether this requirement applies.

Requirements to assess from retrieved documents:
- Written form: confirm from the retrieved document
- Delivery method: compare against retrieved Contract Data
- Recipient: compare against invoking orchestrator findings
- Event identified: confirm from notice content
- Clause cited: confirm from notice content
- Signature requirement: confirm whether this is in the retrieved
  amendment document and whether the document satisfies it
- Identification as a defined notice type: confirm from the retrieved
  amendment document whether this formal requirement applies and
  whether the document satisfies it

### Step 6 — Assess continuing notice obligations
*Contract-type-specific — applicable only if required by the confirmed
standard form and version*

Some standard forms require that, where a claim event is continuing,
the claimant must submit updated particulars at intervals. Retrieve
the applicable provision from Layer 2b to confirm whether this applies
under the confirmed standard form. The interval is stated in the
Contract Data — extract from Layer 1.

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
amendment document:
- Days within period → WITHIN TIME
- Days exceed period → POTENTIALLY TIME-BARRED — flag immediately;
  state awareness date and source, notice date, days elapsed, notice
  period and its source

Awareness date NOT confirmed from retrieved records AND notice period
confirmed → AWARENESS DATE NOT INDEPENDENTLY VERIFIED — calculate
from the date stated in the notice but flag that the calculation
relies on an unverified date; note the risk of an earlier date

Notice period NOT confirmed (amendment document not retrieved) →
CANNOT CALCULATE TIME BAR — state what is missing

Both unconfirmed → CANNOT ASSESS time bar position

**Form and content:**

All requirements confirmed from retrieved documents and met →
COMPLIANT — cite source for each requirement

One or more requirements not met → DEFECTIVE — state each defect
specifically and its source; state whether curable or fatal

Requirements cannot be confirmed → CANNOT CONFIRM compliance with
[specific requirement]

No notice found for a claim in the warehouse →
NO NOTICE FOUND — call tools to search; do not conclude absence
without exhausting search

**Recipient routing:**

Notice addressed to confirmed contract administrator →
CORRECT ROUTING
Notice addressed to incorrect party for confirmed standard form →
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
records for that period retrieved
**Action:** `search_chunks` with query "[event description]
[approximate date range]"; `get_related_documents` with document
types "Site Diary", "Daily Report", "Progress Report"
**Look for:** Any document recording the same event at an earlier date

**Signal:** Amendment document not retrieved — notice period cannot
be confirmed
**Action:** `search_chunks` with query "particular conditions notice
claim period days"; `get_document` on the amendment document ID
if known from orchestrator findings
**Look for:** The notice provision and any period stated in the
amendment document

**Signal:** Layer 2b notice provision not retrieved
**Action:** `search_chunks` with `layer_type = '2b'` and query
"[standard form name] notice claim time bar awareness"
**Look for:** Standard form claim notice provision for the confirmed
standard form

---

## Always flag — regardless of query

1. **POTENTIALLY TIME-BARRED** — state the consequence: the right
   to the claim may be extinguished subject to the governing law
   position on strict enforcement.

2. **Notice period not confirmed from amendment document** — state
   that no time bar calculation can be made.

3. **Awareness date not independently verified** — state that the
   analysis relies on the date stated in the notice which has not
   been confirmed by contemporaneous records.

4. **No notice found for a claim in the warehouse** — state the
   claim reference and the absence after tool search.

5. **Notice recipient inconsistent with confirmed contract
   administrator** — state the routing issue and its potential
   effect on validity.

6. **Employer deductions or claims without corresponding notice**
   — if the confirmed standard form requires employer claims to
   follow the same notice procedure, and employer deductions exist
   without a retrieved employer notice: flag after confirming the
   requirement from Layer 2b.

7. **Governing standard not retrieved from Layer 2b** — flag when
   the notice provisions could not be retrieved; state what standard
   would need to be ingested.

---

## Output format

```
## Notice Compliance Assessment

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
[List every document required but not found. State which steps
are affected.]

### Layer 2b Reference Retrieved
[State whether the notice provisions for the confirmed standard form
were retrieved from Layer 2b. If not: state CANNOT CONFIRM —
STANDARD FORM NOT IN WAREHOUSE and list which analysis steps
are affected.]

### Applicable Notice Requirements (this project)
Notice period: [value from retrieved amendment document / CANNOT CONFIRM]
Source: [amendment document reference and provision / NOT RETRIEVED]
Delivery method required: [from retrieved Contract Data / CANNOT CONFIRM]
Notice recipient: [from orchestrator findings / CANNOT CONFIRM]
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
Awareness date: [date — source / STATED IN NOTICE ONLY — NOT VERIFIED]
Days elapsed: [number / CANNOT CALCULATE — reason]
Applicable notice period: [from retrieved amendment document / CANNOT CONFIRM]
Form compliance:
  Written: [YES / NO — from retrieved document]
  Delivery method: [method used vs required from Contract Data / CANNOT CONFIRM REQUIREMENT]
  Recipient: [named vs confirmed administrator / CORRECT / WRONG / CANNOT CONFIRM]
  Event identified: [YES / NO — from notice content]
  Clause cited: [YES — clause / NO]
Continuing notices: [ASSESSED / NOT APPLICABLE / NOT CONFIRMED FROM LAYER 2b]
Source documents: [list with references]
Finding: [from retrieved documents only]

### Employer Claims Notice Assessment
[Assessment if confirmed applicable from Layer 2b / NOT APPLICABLE /
CANNOT CONFIRM — Layer 2b not retrieved]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
*(Confidence scale: GREEN = all required evidence retrieved and findings fully supported | AMBER = Layer 2b not retrieved or amendment position unknown -- findings provisional | RED = critical document absent -- findings materially constrained | GREY = standard form unconfirmed -- form-specific analysis suspended. Full definition: skills/c1-skill-authoring/references/grounding_protocol.md)*
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not apply any period, threshold, or requirement
from this section without first confirming it from retrieved project
documents.*

**Notice provisions — structural summary (analytical reference):**
Standard forms of contract impose notice requirements on parties
wishing to claim time extensions, additional cost, or other relief.
These provisions typically require notice within a specified period
after the party becomes aware of the event, delivered in writing to
the contract administrator. The specific period, formal requirements,
and consequences of non-compliance vary significantly between standard
forms and between versions. Some standard forms are more prescriptive
about formal requirements than others. Retrieve the applicable
provision from Layer 2b before applying any requirement.

**Time bar — analytical reference:**
The notice period is stated in the contract — either in the general
conditions or as amended by the particular conditions. Amendment
documents frequently modify notice periods. The period to apply is
always the period in the retrieved documents — never a default.

**Awareness date — analytical reference:**
The time bar runs from when the party became aware or should
reasonably have become aware. The objective test means
contemporaneous records can evidence an earlier awareness date
than what the notice states. Retrieve contemporaneous records
to verify the date independently.

**Governing law — analytical reference:**
The enforceability of time bars and the consequences of non-compliance
vary by governing law. Some legal systems apply time bars strictly;
others apply good faith or other doctrines that may soften strict
enforcement. The governing law must be confirmed from the retrieved
contract documents — do not assume a governing law or its approach.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies to
any contract form. All characterisations grounded in retrieved warehouse
documents only.*
