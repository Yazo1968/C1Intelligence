# Notice and Instruction Compliance — Legal & Contractual Specialist

## When to apply this skill

Apply this skill when a query concerns whether a notice or instruction was validly
issued — including Notice of Claim, Notice of Delay, Engineer's Instruction, variation
instruction, notice of suspension, termination notice, or any other contractual
communication whose validity depends on form, timing, or routing. Also apply when
assessing whether a time bar has been triggered, whether an instruction was within
the issuing party's authority, or whether a communication constitutes a valid notice
under the contract.

---

## Before you begin

This is a Round 1 skill. There are no upstream specialist findings to read.

The following must be established from prior skill outputs before this skill runs:

From contract_assembly.md:
- FIDIC book type and edition
- Particular Conditions Clause 1.3 amendments (notice form and method requirements)
- Governing law and jurisdiction

From engineer_identification.md:
- Identity of the Engineer or Employer's Representative
- Notice recipient for Contractor claims
- Split-role pattern (if any) and which entity receives which category of notice
- Engineer independence status

If either prior skill output is unavailable, retrieve the Particular Conditions and
Engineer appointment documents from the warehouse before proceeding.

---

## Analysis workflow

**Step 1 — Establish the applicable notice requirements**

From the Particular Conditions and Contract Data, identify the notice requirements
that govern this project. FIDIC Clause 1.3 sets the baseline — all notices must be
in writing. The 2017 editions significantly tightened these requirements.

FIDIC 1999 Clause 1.3 — notices must be:
- In writing
- Delivered by hand, sent by mail, or transmitted by agreed system
- Sent to the address stated in the Appendix to Tender

FIDIC 2017 Clause 1.3 — notices must satisfy five formal requirements:
- In writing
- Signed by the issuing party's representative (original signature or electronic
  from the assigned address)
- Identified as a Notice (capital N — the defined term)
- Delivered by one of the specified methods (hand delivery with receipt, recorded
  postal service, agreed electronic transmission system)
- Sent to the address stated in the Contract Data

Note: The 2017 edition uses approximately 80 instances of the defined term "Notice"
throughout the General Conditions. A communication that does not satisfy all five
requirements is not a Notice under 2017 FIDIC, regardless of its content.

Check the Particular Conditions for any amendments to Clause 1.3. GCC Particular
Conditions sometimes specify additional requirements (specific email addresses,
copy recipients, prescribed forms) or restrict accepted delivery methods.

**Step 2 — Identify the notice or instruction under assessment**

From the retrieved documents, identify the specific communication being assessed:
- Document type (Notice of Claim, Engineer's Instruction, variation instruction, etc.)
- Issuing party
- Date of issue
- Method of delivery
- Recipient named on the document
- Content summary

If multiple notices are being assessed (e.g. a series of notices relating to one
claim), assess each separately and note whether they form a compliant sequence.

**Step 3 — Assess form compliance**

Check the notice or instruction against the applicable Clause 1.3 requirements
established in Step 1.

For each requirement, classify: COMPLIANT / NON-COMPLIANT / CANNOT ASSESS

Under 1999: in writing ✓/✗ — delivered by accepted method ✓/✗ — sent to correct
address ✓/✗

Under 2017: in writing ✓/✗ — signed ✓/✗ — identified as a Notice ✓/✗ — correct
delivery method ✓/✗ — correct address ✓/✗

A notice that fails any one of the 2017 requirements is formally non-compliant,
even if its content is otherwise correct. Flag each failure specifically — do not
issue a general non-compliance finding without identifying which requirement failed.

**Step 4 — Assess routing compliance**

The notice must have been sent to the correct recipient. Using the engineer
identification findings:

For Contractor notices under Red and Yellow Books: the notice must be addressed to
the Engineer (or the specific entity holding the relevant function if a split-role
pattern exists).

For Contractor notices under Silver Book: the notice must be addressed to the
Employer or Employer's Representative as identified in the Contract Data.

For Engineer's Instructions: the instruction must come from the Engineer (or a
properly delegated assistant). An instruction from the Supervision Consultant that
was not delegated the authority to issue Clause 3 instructions is not a valid
Engineer's Instruction.

If the notice was sent to the wrong entity, classify as ROUTING NON-COMPLIANT and
flag the correct recipient. Note that routing errors in split-role GCC projects are
a primary source of time bar arguments — an Employer may argue that a notice sent
to the SC rather than the PMC was not validly issued.

**Step 5 — Assess timing compliance for Contractor notices**

For any Contractor notice that triggers or relates to a claim for additional time
or cost, assess time bar compliance.

Identify the awareness date: the date on which the Contractor first became aware
(or should have been aware as an experienced contractor) of the event giving rise
to the claim. This is the trigger for the 28-day time bar. Sources for the awareness
date: site daily reports, progress reports, RFI responses, correspondence, meeting
minutes. Use the earliest date evidenced in the documents.

Calculate days elapsed between awareness date and notice date.

Apply the applicable clause:
- FIDIC 1999 Cl. 20.1: notice required within 28 days of awareness
- FIDIC 2017 Cl. 20.2.1: notice required within 28 days of awareness (same period;
  additionally requires identification of the contractual basis within 84 days or
  the Notice lapses)

Classify:
- 0–28 days elapsed: COMPLIANT
- 29+ days elapsed: POTENTIALLY TIME-BARRED
- Awareness date not determinable from documents: CANNOT ASSESS — flag documents
  that would establish the awareness date and call tools to find them

Note Qatar-specific flag: Qatar Civil Code Article 418 limits contractual shortening
of prescription periods. In Qatar-seated disputes, a POTENTIALLY TIME-BARRED finding
must include a note that the enforceability of the time bar is subject to Article 418
and requires legal opinion.

**Step 6 — Assess instruction validity (Engineer's Instructions)**

For Engineer's Instructions, assess:
- Was the instruction issued by the Engineer or a properly delegated assistant?
  (Use engineer_identification.md findings)
- Was the instruction in writing per Clause 1.3?
- Did the instruction fall within the Engineer's Clause 3 authority or was it a
  variation instruction under Clause 13.1?
- If the instruction requires the Contractor to execute work that constitutes a
  variation, was it accompanied by or followed by a formal variation order, or did
  the Contractor issue a notice of entitlement?

A verbal instruction that was not confirmed in writing is not a valid Engineer's
Instruction under FIDIC. If the Contractor acted on a verbal instruction without
written confirmation, flag the risk that the instruction may be unenforceable and
that any resulting claim may face entitlement challenges.

**Step 7 — Compile and structure findings**

Compile all findings in the output format below. Time bar findings must be passed
forward explicitly to the Claims specialist — they are foundational to the claims
assessment and must not be re-assessed by Claims from scratch.

---

## Classification and decision rules

**Form compliance:**
- All applicable Clause 1.3 requirements met: FORM COMPLIANT
- One or more requirements not met: FORM NON-COMPLIANT — list each failed requirement
- Requirements cannot be assessed from documents: CANNOT ASSESS FORM

**Routing compliance:**
- Notice addressed to correct entity per engineer_identification.md findings: ROUTING
  COMPLIANT
- Notice addressed to wrong entity: ROUTING NON-COMPLIANT — state correct recipient
- Split-role ambiguity makes routing assessment uncertain: ROUTING UNCERTAIN — flag
  ambiguity and both possible correct recipients

**Time bar — Contractor notices:**
- Notice within 28 days of confirmed awareness date: COMPLIANT
- Notice more than 28 days after confirmed awareness date: POTENTIALLY TIME-BARRED
- Awareness date established from documents but notice date not found: NON-COMPLIANT
  (notice not found — treat as not given)
- Neither awareness date nor notice date determinable: CANNOT ASSESS — call tools
- Qatar-seated dispute: append enforceability caveat per Article 418 to any
  POTENTIALLY TIME-BARRED finding

**Overall notice validity:**
- Form compliant + routing compliant + time compliant: VALID
- Any one element non-compliant: DEFECTIVE — state which element(s) failed
- Time bar triggered: POTENTIALLY TIME-BARRED — regardless of form and routing
  compliance; entitlement may be lost even if notice was otherwise correct

**Engineer's Instructions:**
- Issued by authorised entity in writing within Clause 3 authority: VALID INSTRUCTION
- Issued by entity without confirmed delegation: AUTHORITY UNCERTAIN
- Verbal only, not confirmed in writing: NOT A VALID INSTRUCTION
- Instruction constitutes a variation but no variation order issued: flag VARIATION
  NOTICE REQUIRED — Contractor should have issued notice of entitlement

---

## When to call tools

**Signal:** Notice references an awareness date or triggering event but no
contemporaneous documents (daily reports, progress reports, correspondence) have
been retrieved to confirm the actual awareness date
**Tool:** `search_chunks` querying for the event description and date range
**Look for:** Site daily reports, progress reports, RFI logs, meeting minutes from
the period — any document that evidences when the Contractor first recorded the event

**Signal:** Notice was sent to a named individual rather than an entity — need to
confirm whether that individual held a valid delegation
**Tool:** `get_related_documents` filtered to Delegation Notice, Engineer's
Instruction
**Look for:** Written delegation confirming that individual's authority to receive
notices on behalf of the Engineer

**Signal:** A notice references a prior notice or a series of notices but only one
notice is in the retrieved chunks
**Tool:** `search_chunks` querying for the claim reference number or event
description
**Look for:** The complete notice sequence; assess each notice in the sequence
separately

**Signal:** The Particular Conditions reference a prescribed notice form or a
specific correspondence management system (e.g. Aconex, Procore) but no documents
from that system have been retrieved
**Tool:** `search_chunks` querying for the system name and document type
**Look for:** Whether notices were issued through the prescribed system; a notice
issued outside a contractually mandated system may be non-compliant

---

## Always flag — regardless of query

1. **Time bar status on any Contractor notice that relates to a claim** — always
   assess and state the time bar position, even if the query is about something else.
   A missed time bar is the single most consequential procedural finding in
   construction disputes. It must be surfaced whenever a notice is assessed.

2. **2017 edition formal Notice requirements** — on any 2017 edition project, always
   check all five Clause 1.3 requirements. A substantively correct notice that fails
   the defined-term or delivery-method requirement is non-compliant under 2017 FIDIC.

3. **Routing errors in split-role projects** — whenever a split-role pattern has been
   identified by engineer_identification.md, always check that each notice was sent
   to the entity holding the relevant function. Do not assume routing is correct
   because the notice reached someone.

4. **Verbal instructions not confirmed in writing** — whenever correspondence or
   site records reference a verbal instruction, always flag it. Verbal instructions
   are not valid under FIDIC and create risk for both parties.

5. **Qatar Article 418 enforceability caveat** — whenever a POTENTIALLY TIME-BARRED
   finding is reached on a project with Qatar as governing law or Qatar as arbitration
   seat, always append the Article 418 caveat. Do not omit this — it materially
   affects the forensic significance of the time bar finding.

---

## Output format
```
## Notice and Instruction Compliance Assessment

### Applicable Notice Requirements
FIDIC edition: [1999 / 2017]
Clause 1.3 baseline: [1999 standard / 2017 five-requirement standard]
Particular Conditions amendments to Clause 1.3: [list or "None"]
Prescribed system (if any): [system name or "None specified"]

### Notice / Instruction Assessed
[For each notice or instruction — repeat block as needed:]

**[Document reference and type]**
Issuing party: [party name]
Date of issue: [date]
Delivery method: [method]
Recipient named: [entity]
Content summary: [one sentence]

Form compliance:
| Requirement | Status | Notes |
|---|---|---|
| In writing | [COMPLIANT / NON-COMPLIANT] | |
| Signed (2017 only) | [COMPLIANT / NON-COMPLIANT / N/A] | |
| Identified as Notice (2017 only) | [COMPLIANT / NON-COMPLIANT / N/A] | |
| Correct delivery method | [COMPLIANT / NON-COMPLIANT] | |
| Correct address | [COMPLIANT / NON-COMPLIANT] | |
Form classification: [FORM COMPLIANT / FORM NON-COMPLIANT]

Routing compliance:
Correct recipient: [entity per engineer_identification.md]
Recipient on document: [entity]
Routing classification: [ROUTING COMPLIANT / ROUTING NON-COMPLIANT / ROUTING
UNCERTAIN]

Time bar (Contractor claim notices only):
Awareness date: [date or "not determinable"]
Source of awareness date: [document reference]
Notice date: [date]
Days elapsed: [number or "cannot calculate"]
Applicable clause: [FIDIC 1999 Cl. 20.1 / FIDIC 2017 Cl. 20.2.1]
Time bar classification: [COMPLIANT / POTENTIALLY TIME-BARRED / CANNOT ASSESS]
Qatar enforceability caveat: [YES — Article 418 applies / NO]

Instruction validity (Engineer's Instructions only):
Issuing entity authority: [VALID / AUTHORITY UNCERTAIN / NOT DELEGATED]
Written confirmation: [YES / NO — verbal only]
Within Clause 3 authority: [YES / NO — constitutes variation]
Instruction classification: [VALID INSTRUCTION / AUTHORITY UNCERTAIN /
NOT A VALID INSTRUCTION]

**Overall classification: [VALID / DEFECTIVE / POTENTIALLY TIME-BARRED /
CANNOT ASSESS]**

### Findings for Downstream Specialists
[For each assessed notice relating to a claim:]
Claim reference: [reference]
Time bar status: [COMPLIANT / POTENTIALLY TIME-BARRED / CANNOT ASSESS]
Days elapsed: [number]
Applicable clause: [clause reference]
Form status: [COMPLIANT / DEFECTIVE]
Routing status: [COMPLIANT / NON-COMPLIANT / UNCERTAIN]
Qatar caveat: [YES / NO]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences stating the overall notice compliance position,
the most significant finding, and any time bar exposure identified]
```

---

## Domain knowledge and standards

### FIDIC Clause 1.3 — Communications

The 2017 editions introduced the defined term "Notice" (capital N) with five formal
requirements. This was a deliberate response to disputes about whether informal
communications constituted notices. The practical effect in GCC disputes: under 2017
FIDIC, an email from an engineer's individual email address that was not the assigned
address, or a letter that was not expressly identified as a Notice, may be argued
non-compliant even if the content was entirely correct.

Under 1999 FIDIC the notice requirements are less formal. Courts and tribunals in the
GCC have generally taken a substance-over-form approach to 1999 notices — a
communication that clearly conveys the required information and was received by the
correct party has generally been treated as a valid notice even if technical delivery
requirements were not met. The 2017 formal requirements shift this balance toward form.

### FIDIC Clause 20.1 / 20.2.1 — The 28-Day Time Bar

The 28-day Notice of Claim time bar is one of the most consequential provisions in
FIDIC contracts. Key principles confirmed by GCC tribunals and DIFC Court decisions:

- The time bar is strictly enforced in UAE (FIVE v Reem; Panther v Modern Executive)
- Implied good faith obligations do not override a missed time bar in UAE
- The awareness date is determined objectively — when an experienced contractor should
  have been aware, not merely when the contractor says it became aware
- Site daily reports and progress reports are primary evidence for the awareness date
- A continuing event (e.g. ongoing delay) requires periodic notices under 1999 Clause
  20.1 — a single notice at the start does not cover the entire duration
- Under 2017 Clause 20.2.1, a notice that does not identify the contractual basis
  within 84 days lapses — the 84-day requirement is a second time gate after the
  28-day notice gate

### GCC-Specific Notice Patterns

**Aconex and document management systems:** Many large GCC projects use Aconex or
similar systems as the contractually mandated correspondence management platform.
Where the Particular Conditions or a project protocol specify that notices must be
issued through such a system, a notice issued outside the system (e.g. by email or
letter) may be argued non-compliant. Always check whether a prescribed system is
specified and whether the notice was issued through it.

**Bilingual notices:** Saudi government projects typically require notices in Arabic.
UAE projects may have bilingual requirements with Arabic prevailing. A notice issued
only in English on a project requiring Arabic may be argued non-compliant. When the
governing language is not English, flag any notice issued solely in English.

**Notice to Proceed / Commencement Date notices:** These are Employer or Engineer
obligations, not Contractor obligations, but their timing establishes the
Commencement Date from which the Time for Completion runs. Always check that a formal
Notice to Proceed was issued and that the Commencement Date is confirmed — it is the
anchor for every time-related calculation on the project.
