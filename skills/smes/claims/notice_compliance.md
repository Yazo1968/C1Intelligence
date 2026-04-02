# Notice Compliance

**Skill type:** Contract-type-specific (clause references, routing, and
procedural requirements differ by FIDIC book and edition)
**Domain:** Claims & Disputes SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply this skill when retrieved chunks contain any of the following:
a Notice of Claim, a Notice of Delay, a Notice of Potential Claim, a
letter asserting a right to additional time or money, or a query about
whether a notice was validly given, defective, or time-barred. Also
apply when a claim submission is present but no corresponding notice
has been found in the warehouse.

---

## Before you begin

This skill is contract-type-specific. The analysis depends on which
FIDIC book and which edition governs the project. Before any notice
assessment begins you must establish both.

**Step 1 — Establish the governing contract type.**
Read the Legal orchestrator findings. Extract:
- FIDIC book: Red Book (Construction) / Yellow Book (Plant and
  Design-Build) / Silver Book (EPC/Turnkey)
- FIDIC edition: 1999 or 2017
- Whether any Particular Conditions amend the notice provisions

If Legal orchestrator findings are not available, retrieve the contract
documents using `search_chunks` with query "FIDIC conditions particular
conditions contract type" before proceeding.

**Step 2 — Extract the actual notice period from the Particular
Conditions.**
Do not apply the standard form default. Search for the Particular
Conditions document and locate any amendment to the notice clause.
The notice period to use in your analysis is the period stated in the
project's Particular Conditions. If no amendment is found and you have
confirmed the Particular Conditions are in the warehouse, only then
note that the standard form default appears to apply — and cite the
source document that supports this conclusion.

**Step 3 — Extract the actual detailed particulars submission period.**
Same principle. Find the Particular Conditions amendment, if any.
Do not assume the standard form default.

**Step 4 — Identify the correct notice recipient.**
This is contract-type-specific:
- Red Book (all editions): notices go to the Engineer
- Yellow Book (all editions): notices go to the Engineer
- Silver Book (all editions): there is no Engineer. Notices go to
  the Employer's Representative. The Employer's Representative is
  the Employer's agent — there is no impartiality obligation.

Retrieve the contract to identify the named Engineer or Employer's
Representative and their contact details if stated.

---

## Analysis workflow

**Step 1 — Identify all notices in the warehouse.**
Call `get_related_documents` with document_type "Notice of Claim".
Then call `get_related_documents` with document_type "Notice of Delay".
Then call `search_chunks` with query "notice claim additional time
payment extension of time" to catch notices not classified by type.
Compile a complete list. Note any gaps — a claim in the warehouse
with no corresponding notice is itself a significant finding.

**Step 2 — For each notice, determine the awareness date.**
The awareness date is the date on which the notifying party first
became aware, or should reasonably have become aware, of the event
giving rise to the claim. This is not always the date of the notice
itself. Look for:
- Site diaries or daily reports referencing the event before the
  notice date
- RFIs, instructions, or correspondence referencing the event
- Progress reports noting the condition before the notice
- Meeting minutes recording the event
If an earlier awareness date is evidenced in any document, use it
for the time bar calculation — not the date stated in the notice.

**Step 3 — Calculate days elapsed from awareness to notice.**
Days elapsed = notice date minus awareness date.
Compare against the notice period extracted from the Particular
Conditions in the Pre-Flight Check. Do not use the standard form
default unless confirmed in Step 2 of the Pre-Flight Check.

**Step 4 — Assess notice form and content.**
A valid notice must satisfy all of the following — assess each:

*Contract-type-agnostic requirements (all books, both editions):*
- In writing
- Delivered by the method specified in the contract (check the
  Particular Conditions for the communications clause — email,
  registered post, hand delivery)
- Identifies the event or circumstance giving rise to the claim
- References the contractual basis (FIDIC clause)
- Given within the time period extracted from the Particular Conditions

*Contract-type-specific requirements:*
- **Red Book / Yellow Book — 1999:** Addressed to the Engineer.
  References Cl. 20.1. Quantum not required at notice stage.
- **Red Book / Yellow Book — 2017:** Addressed to the Engineer.
  References Cl. 20.2.1. Must describe the event or circumstance
  with more specificity than the 1999 edition requires. Monthly
  updates required after the initial notice.
- **Silver Book — 1999:** Addressed to the Employer's Representative.
  References Cl. 20.1. No Engineer — routing to Engineer is invalid.
- **Silver Book — 2017:** Addressed to the Employer's Representative.
  References Cl. 20.2.1. Monthly updates required.

**Step 5 — Assess Employer claims (2017 editions only).**
FIDIC 2017 makes Employer claims symmetric — the Employer must follow
the same notice procedure under Cl. 20.2.1 as the Contractor. Check
whether the Employer has raised any claims (liquidated damages
deductions, set-offs, backcharges). If so, assess whether the Employer
has complied with Cl. 20.2.1 — the same time bar applies. This does
not apply to 1999 editions (Employer claims are under Cl. 2.5 with
different procedural requirements).

**Step 6 — Assess continuing notice obligations.**
Under both 1999 and 2017 editions, where a delay or claim event is
continuing, updated particulars must be submitted at intervals (monthly
under 2017 Cl. 20.2.4). Check whether the claimant has maintained
continuing notices where the event extended over time. A failure to
maintain continuing notices may limit the period of entitlement even
where the initial notice was valid.

**Step 7 — Classify each notice.**
Apply the decision framework below. Classify and record each notice
separately.

---

## Classification and decision rules

**Time bar assessment:**

If days elapsed from awareness to notice exceed the notice period
extracted from the Particular Conditions:
→ Classify as **POTENTIALLY TIME-BARRED**
→ Flag immediately regardless of other findings
→ State: the awareness date used, the notice date, the days elapsed,
  the applicable period from the Particular Conditions (with source),
  and the contractual consequence

If days elapsed cannot be calculated because the awareness date is not
determinable from the documents:
→ Classify as **AWARENESS DATE UNCERTAIN**
→ Flag: the documents reviewed, why the awareness date cannot be fixed,
  and the risk that an earlier awareness date may be evidenced by
  documents not in the warehouse

If days elapsed are within the notice period:
→ Classify as **WITHIN TIME** — proceed to form and content assessment

**Form and content assessment:**

If the notice satisfies all requirements:
→ Classify as **COMPLIANT**

If the notice fails one or more requirements:
→ Classify as **DEFECTIVE** — state each defect specifically
→ Note whether the defect is curable (addressable by subsequent
  correspondence) or fatal (cannot be remedied retrospectively)

If no notice exists for a claim in the warehouse:
→ Classify as **NO NOTICE FOUND**
→ Flag: the claim reference, the event, and the absence of notice
→ This does not mean no notice was given — it may mean it is not
  in the warehouse. Flag the gap and call tools to search further
  before concluding.

**Recipient routing:**

If the notice is addressed to the wrong party for the contract type:
→ Classify as **DEFECTIVE — WRONG RECIPIENT**
→ State the correct recipient for the book type and cite the clause

---

## When to call tools

**Signal:** A claim submission exists but no corresponding notice
appears in the initial retrieval.
**Action:** Call `search_chunks` with query "[claim event description]
notice" and call `get_related_documents` with document_type "Notice".
**Look for:** A notice document that predates the claim submission
and references the same event.

**Signal:** The notice states an awareness date but no supporting
contemporaneous documentation has been retrieved to verify it.
**Action:** Call `search_chunks` with query "[event description]
[approximate date range]" and call `get_related_documents` with
document_type "Site Diary" or "Progress Report" for the relevant
period.
**Look for:** Any document predating the notice that references
the same event — earlier awareness date evidence.

**Signal:** The Particular Conditions document has not been retrieved
and the notice period cannot be confirmed.
**Action:** Call `search_chunks` with query "particular conditions
notice claim period days" and call `get_document` if a Particular
Conditions document ID is available from Legal orchestrator findings.
**Look for:** Any amendment to the notice clause. If none found
after searching, flag that the Particular Conditions were not located
and state that the notice period cannot be confirmed from the
warehouse — do not apply the standard form default.

**Signal:** The contract uses a specific communications method
(registered post, specific email address, named representative) and
the notice delivery method is unclear from the chunk content.
**Action:** Call `get_document` on the notice document to read its
full content including any delivery confirmation or header.
**Look for:** Delivery method, addressee, and any delivery confirmation.

---

## Always flag — regardless of query

**Flag 1 — Time bar risk on any notice assessed as POTENTIALLY
TIME-BARRED or AWARENESS DATE UNCERTAIN.**
State in one sentence: the consequence — the right to the claim may
be extinguished if the time bar is upheld, subject to the governing
law position on strict enforcement.

**Flag 2 — Notice period confirmed from Particular Conditions vs.
assumed from standard form.**
If the notice period has been extracted from a confirmed Particular
Conditions document, state this clearly. If it could not be confirmed,
flag this as a gap — the analysis is based on an unconfirmed period
and may need to be revised once the Particular Conditions are located.

**Flag 3 — Absence of notice for a claim present in the warehouse.**
If a claim submission, EOT claim, or prolongation cost claim exists
but no corresponding initial notice has been found after tool search,
flag this explicitly. State the claim reference and the finding.

**Flag 4 — Silver Book: any notice routed to the Engineer.**
On a Silver Book project, the Engineer does not exist. A notice
addressed to an "Engineer" on a Silver Book project is addressed
to the wrong party. Flag as DEFECTIVE — WRONG RECIPIENT and state
the correct recipient.

**Flag 5 — FIDIC 2017: Employer claims without symmetric notice
compliance.**
If Employer deductions (LDs, backcharges, set-offs) are present and
no corresponding Cl. 20.2.1 notice from the Employer has been found,
flag this as a potential procedural deficiency in the Employer's
position.

---

## Output format
```
## Notice Compliance Assessment

### Contract Basis
- FIDIC book and edition: [extracted from Legal orchestrator or retrieved]
- Notice period: [period extracted from Particular Conditions,
  citing source document and clause reference — NOT a standard form default]
- Detailed particulars period: [period extracted from Particular
  Conditions, citing source — NOT a standard form default]
- Notice recipient: [Engineer / Employer's Representative, with
  named individual if identified from contract documents]

### Notice Register

| # | Notice ref | Notice date | Awareness date | Days elapsed | Period | Classification | Defects |
|---|---|---|---|---|---|---|---|
| 1 | [ref] | [date] | [date or UNCERTAIN] | [number or N/A] | [from PC] | [classification] | [defects or NONE] |

### Findings by Notice

**[Notice reference]**
Classification: [COMPLIANT / DEFECTIVE / POTENTIALLY TIME-BARRED /
AWARENESS DATE UNCERTAIN / NO NOTICE FOUND]
Awareness date: [date and source document, or basis for uncertainty]
Notice date: [date and source document]
Days elapsed: [number]
Applicable period: [period from Particular Conditions, source cited]
Form and content: [assessment of each formal requirement]
Recipient: [correct / defective — state finding]
Continuing notices: [compliant / gap identified / not applicable]
Source documents: [list with references]
Finding: [specific conclusion with source attribution]

### Employer Claims (FIDIC 2017 only)
[Assessment of Employer notice compliance, or NOT APPLICABLE for
1999 editions]

### FLAGS
[Each flag on a separate line, classified as FLAG with one-sentence
implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences]
```

---

## Domain knowledge and standards

### Contract-type-agnostic principles

The notice obligation exists to give the party receiving the notice
the opportunity to investigate the event contemporaneously, mitigate
its effects, and maintain its own records. This purpose is relevant
to whether a technically defective notice should be treated as
non-compliant — tribunals have occasionally held that a notice that
achieves its purpose despite technical deficiency is effective,
though this is the exception not the rule.

Written notice is universally required under all FIDIC books and
editions. The method of delivery is contract-specific — read the
communications clause in the Particular Conditions, not the General
Conditions default.

The awareness test is objective — it is when the party became aware
or *should reasonably have become aware*. A party cannot delay notice
by claiming ignorance of an event that its site team had recorded.
This is the most frequently litigated aspect of the time bar provision
in GCC arbitration.

**Never apply standard form default periods.** Particular Conditions
in GCC projects routinely amend notice periods — shortening them to
14 or 21 days, or in some cases extending them. Some GCC government
Employer standard forms reduce the notice period to 7 days. The
analysis must be based on the period stated in the project's
Particular Conditions. If the Particular Conditions are not in the
warehouse, state this gap explicitly.

### Contract-type-specific provisions

**Notice clause by book and edition:**

| Book | Edition | Contractor notice clause | Time bar | Detailed particulars |
|---|---|---|---|---|
| Red Book | 1999 | Cl. 20.1 | 28 days (default — check PC) | 42 days (default — check PC) |
| Red Book | 2017 | Cl. 20.2.1 | 28 days (default — check PC) | 84 days (default — check PC) |
| Yellow Book | 1999 | Cl. 20.1 | 28 days (default — check PC) | 42 days (default — check PC) |
| Yellow Book | 2017 | Cl. 20.2.1 | 28 days (default — check PC) | 84 days (default — check PC) |
| Silver Book | 1999 | Cl. 20.1 | 28 days (default — check PC) | 42 days (default — check PC) |
| Silver Book | 2017 | Cl. 20.2.1 | 28 days (default — check PC) | 84 days (default — check PC) |

All periods in this table are standard form defaults. **Read the
Particular Conditions before applying any of these figures.**

**Engineer's determination — Red Book and Yellow Book only:**
Under Red Book and Yellow Book (1999 Cl. 3.5 / 2017 Cl. 3.7) the
Engineer has a determination function. The Engineer must consult with
both parties and then make a fair determination. Under 2017 Cl. 3.7
the Engineer's determination is time-limited — if no determination
is made within the prescribed period the claim is deemed rejected.
Under 1999 Cl. 3.5 there is no express time limit on the
determination. **Silver Book has no Engineer and no determination
mechanism** — disputes go directly to DAB (1999) or DAAB (2017).

**Employer claims — asymmetric (1999) vs. symmetric (2017):**
Under FIDIC 1999, Contractor claims are under Cl. 20.1 and Employer
claims are under Cl. 2.5, which has different and less prescriptive
procedural requirements. Under FIDIC 2017, Cl. 20 applies to both
Contractor and Employer claims — the same 28-day notice period and
the same detailed particulars requirements apply to both parties.
This is one of the most significant structural changes between the
two editions. An Employer who deducts LDs or raises backcharges
under a 2017 contract without complying with Cl. 20.2.1 is in a
procedurally deficient position — symmetrically.

**GCC-specific practice:**

UAE onshore courts (Abu Dhabi and Dubai): the good faith doctrine
under UAE Civil Code Art. 246 has been applied in isolated cases to
soften strict time bar enforcement where the Employer suffered no
prejudice from a late notice. This remains the exception. DIFC Court
and DIFC-LCIA follow English common law — strict enforcement is the
norm and the good faith argument carries less weight.

Saudi Arabia: strict enforcement is the norm. Government Employer
contracts frequently use modified forms with shorter notice periods —
always extract from the Particular Conditions.

Qatar: Qatar Civil Code applies. QICCA and ICC proceedings both
follow strict notice compliance assessment. The FIFA World Cup legacy
projects established a strong contemporaneous records culture —
failure to maintain records alongside notices weakens the claim
significantly.

Bilingual contracts (Arabic/English): in UAE onshore courts, the
Arabic version prevails absent an express governing language clause.
A notice period stated as 28 days in English may differ in the Arabic
version. Flag this risk where the contract appears to be bilingual
and no governing language clause has been identified.
