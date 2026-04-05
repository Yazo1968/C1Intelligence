# Time at Large

**Skill type:** Mixed
- Contract-type-specific: the time extension mechanism that prevents
  time going at large differs by standard form and version; whether
  the amendment document provides an adequate mechanism is project-
  specific
- Contract-type-agnostic: the prevention principle and the conditions
  for time going at large apply as a matter of law regardless of
  contract type; the assessment framework is consistent
**Layer dependency:**
- Layer 1 — project documents: amendment document (time extension
  clause, agreed damages clause, completion mechanism); Contract Data
  (Time for Completion, agreed damages rate); evidence of employer
  acts of prevention (instructions, delays, access restrictions);
  time extension claim history and responses; completion certificate
  (if issued)
- Layer 2b — reference standards: time extension provision and agreed
  damages provision for the confirmed standard form (whatever is in
  the warehouse); applicable law (if ingested in Layer 2b)
**Domain:** Schedule & Programme SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when a query concerns whether time is at large, whether the
Employer's right to agreed damages is enforceable, whether the
prevention principle has been triggered, or whether the Contractor
has an obligation to complete within a reasonable time rather than
by the contractual completion date. Apply when employer-caused delays
have been identified but no time extension mechanism appears to have
been triggered or was available.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings, delay_identification
findings, and eot_quantification findings.

From the invoking orchestrator:
- Confirmed standard form and version
- Governing law as confirmed from retrieved contract documents
- Agreed damages rate and cap as confirmed from retrieved Contract
  Data
- Whether the time extension clause exists in the retrieved amendment
  document and whether it provides an adequate mechanism to extend
  time for employer-caused delays

From delay_identification:
- What employer-caused delay events have been identified from
  retrieved documents

From eot_quantification:
- Whether a time extension has been claimed and what the response was
- Whether a time extension was granted, denied, or not responded to

**Time at large is a legal remedy of last resort.** It arises only
when the Employer has caused delay AND the contract does not provide
an adequate mechanism to extend time for that delay. Under most
standard forms, the time extension clause is specifically designed
to prevent time going at large. Flag this context in the output.

**If no employer-caused delay events have been identified from
retrieved documents:** State CANNOT ESTABLISH the prevention
principle from retrieved documents. Do not assess time at large
without a founded employer delay.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The amendment document — time extension clause, agreed damages
  clause, completion clause, and any provision addressing the
  consequences of employer delay
- The Contract Data — Time for Completion, agreed damages rate, cap
- Evidence of the employer-caused acts of prevention (from
  delay_identification findings)
- The time extension claim history and responses (from
  eot_quantification findings)
- The completion certificate (if issued — establishes actual
  completion date)
- The governing law clause in the amendment document

**If the amendment document and agreed damages clause have not been
retrieved:**
State CANNOT ASSESS whether time is at large — the agreed damages
mechanism is central to the analysis.

**If the governing law has not been confirmed from retrieved
documents:** State CANNOT ASSESS the legal framework for time at
large. The prevention principle operates differently under different
governing laws.

### Layer 2b documents to retrieve (reference standards)

Call `search_chunks` with `layer_type = '2b'` to retrieve:
- Time extension provision for the confirmed standard form (search
  by subject matter: "time extension employer risk event prevention")
- Agreed damages provision for the confirmed standard form (search
  by subject matter: "agreed damages delay damages liquidated
  damages rate cap")
- Any applicable law from Layer 2b if ingested (search by subject
  matter: "[governing law name] construction contract time at large
  prevention principle")

**Purpose:** To establish the standard form time extension and agreed
damages mechanism for structural comparison against the retrieved
amendment document.

**If the governing standard form is not retrieved from Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE for the
time extension and agreed damages provisions.

---

## Analysis workflow

### Step 1 — Confirm the time extension mechanism in the retrieved contract
*Contract-type-specific*

From the retrieved amendment document:
- Is the time extension clause present and unamended?
- Has the time extension clause been deleted, restricted, or modified
  in a way that prevents the Contractor from obtaining a time
  extension for employer-caused delays?
- Does the amendment document time extension mechanism cover the
  specific employer acts of prevention identified in
  delay_identification?

**If the time extension mechanism is present and covers employer-caused
delays:** The standard position is that the prevention principle is
excluded by the time extension mechanism. Time is not at large
provided the Contractor has properly invoked the procedure.

**If the time extension mechanism has been deleted or restricted so
that it does not cover the employer's acts of prevention:** The
prevention principle may apply — flag and proceed with the analysis.

### Step 2 — Identify acts of prevention from retrieved documents
*Contract-type-agnostic*

From delay_identification findings and the retrieved documents,
identify the specific employer acts of prevention:
- Instructions that varied the works and prevented completion by
  the contractual date
- Failure to give access, late information, or other employer
  defaults that prevented timely completion

**The acts of prevention must be evidenced in retrieved documents.**
Do not identify acts of prevention from the claim submission alone.

For each act: state the event, the date, the source document, and
whether it is an act for which the time extension mechanism provides
relief.

### Step 3 — Assess whether the time extension mechanism was properly invoked
*Contract-type-specific*

From notice_and_instruction_compliance and eot_quantification findings:
- Was a notice of claim issued for each act of prevention?
- Was the time extension claim properly submitted?
- Was a time extension granted for each act of prevention?

**If the Contractor failed to invoke the time extension mechanism
properly:** Time at large may not be available as a remedy — the
Contractor's failure to invoke the mechanism may prevent it from
relying on the prevention principle. Flag this dependency.

**If the Contractor properly invoked the mechanism but the time
extension was denied or not responded to:** The prevention principle
argument is stronger. State this from the retrieved documents.

### Step 4 — Assess the agreed damages enforceability position
*Contract-type-specific*

From the retrieved amendment document and Contract Data:
- What is the agreed damages rate? (Extract from Contract Data — do
  not apply any default)
- Is there an agreed damages cap? (Extract from retrieved documents)
- Has the agreed damages rate been applied by the Employer? (From
  retrieved payment certificates)
- Is the rate genuine pre-estimate of loss or potentially a penalty?
  (This is a legal question — flag that it requires legal advice;
  state the rate from retrieved documents)

**If time is at large:** The Employer's right to agreed damages is
suspended for the period of time at large. The Contractor is obliged
to complete within a reasonable time. Agreed damages cannot accrue
while time is at large.

### Step 5 — Assess the governing law impact
*Contract-type-specific*

The prevention principle and time at large operate differently
depending on the governing law confirmed from the retrieved contract
documents.

From the retrieved governing law clause:
- State the confirmed governing law
- Retrieve any applicable law from Layer 2b if ingested
- Flag that the time at large analysis requires legal advice specific
  to the confirmed governing law

**Do not state a legal conclusion on whether time is at large —
state the facts from the retrieved documents and the legal framework.**
The governing law must be confirmed from the retrieved documents.
Do not assume any governing law position.

In all cases: state the governing law confirmed from retrieved
documents and flag that the time at large argument requires legal
advice specific to that law.

---

## Classification and decision rules

**Prevention principle:**

Employer acts of prevention identified in retrieved documents AND
time extension mechanism does not cover those acts from the retrieved
amendment document → PREVENTION PRINCIPLE POTENTIALLY ENGAGED —
flag; proceed to agreed damages enforceability assessment

Employer acts of prevention identified AND adequate time extension
mechanism exists in retrieved amendment document covering those
acts AND Contractor properly invoked it → TIME EXTENSION MECHANISM
AVAILABLE — time at large unlikely under standard analysis; flag
if time extension was denied without justification

Employer acts of prevention identified AND Contractor failed to
invoke time extension mechanism → PROCEDURAL FAILURE — flag; time
at large argument weakened by failure to invoke available mechanism

No employer acts of prevention confirmed from retrieved documents →
PREVENTION PRINCIPLE NOT ESTABLISHED FROM RETRIEVED DOCUMENTS

**Agreed damages enforceability:**

Time at large conditions met AND agreed damages rate confirmed from
retrieved Contract Data → AGREED DAMAGES POTENTIALLY UNENFORCEABLE
FOR PERIOD OF PREVENTION — flag; state the rate and implications
Time not at large → AGREED DAMAGES MECHANISM OPERATIVE — state
confirmed rate and cap from retrieved documents
Agreed damages rate not confirmed → CANNOT CONFIRM DAMAGES EXPOSURE

---

## When to call tools

**Signal:** Agreed damages clause or rate not confirmed from retrieved
Contract Data or amendment document
**Action:** `search_chunks` with query "agreed damages rate clause
particular conditions contract data"; `get_document` on Contract
Data document ID
**Look for:** The agreed damages rate, cap, and the clause

**Signal:** Acts of prevention referenced but underlying instructions
or access records not retrieved
**Action:** `search_chunks` with query "[act description]
[date range]"; `get_related_documents` with document types
"Instruction", "Site Diary", "Correspondence"
**Look for:** The instruction or record evidencing the act of
prevention

**Signal:** Governing law not confirmed from retrieved amendment
document
**Action:** `search_chunks` with query "governing law applicable
law contract clause"
**Look for:** The governing law clause in the contract

**Signal:** Layer 2b time extension or agreed damages provision not
retrieved
**Action:** `search_chunks` with `layer_type = '2b'` and query
"[standard form name] time extension agreed damages prevention"
**Look for:** Standard form time extension and agreed damages
provisions

---

## Always flag — regardless of query

1. **Prevention principle potentially engaged** — always flag when
   employer acts of prevention have been identified and the time
   extension mechanism does not cover them from the retrieved
   amendment document; state the consequence in one sentence.

2. **Agreed damages rate not confirmed from retrieved Contract Data**
   — always flag; state that agreed damages exposure cannot be
   confirmed.

3. **Contractor's failure to invoke time extension mechanism** —
   always flag where acts of prevention exist but no notice or time
   extension claim was issued; state the forensic implication.

4. **Governing law not confirmed** — always flag; the time at large
   analysis depends fundamentally on the governing law.

5. **Agreed damages applied by Employer for a period that includes
   confirmed employer-caused delays without granted time extension**
   — always flag; state the period, the agreed damages amount applied
   (from retrieved payment certificates), and the employer delay
   events during that period.

---

## Output format

```
## Time at Large Assessment

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
[State whether the time extension provision, agreed damages provision,
and applicable law were retrieved from Layer 2b. If not: state
CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE and list which
analysis steps are affected.]

### Governing Law
Confirmed: [YES — governing law and source document / CANNOT CONFIRM]

### Time Extension Mechanism Assessment
Time extension clause in retrieved amendment document: [PRESENT AND
UNAMENDED / AMENDED — describe / DELETED / CANNOT CONFIRM — not retrieved]
Covers employer-caused delays identified: [YES / PARTIALLY / NO /
CANNOT CONFIRM]
Source: [amendment document reference]

### Acts of Prevention
[List from delay_identification findings with retrieved document
sources for each act. State whether each act is covered by the
retrieved time extension mechanism.]

### Time Extension Invocation Assessment
[From notice_and_instruction_compliance and eot_quantification
findings — whether the Contractor properly invoked the mechanism
for each act of prevention]

### Prevention Principle Assessment
Prevention principle engagement: [POTENTIALLY ENGAGED — reason /
NOT ESTABLISHED FROM RETRIEVED DOCUMENTS / TIME EXTENSION MECHANISM
AVAILABLE / PROCEDURAL FAILURE — Contractor failed to invoke mechanism]

### Agreed Damages Enforceability
Agreed damages rate: [from retrieved Contract Data / CANNOT CONFIRM]
Agreed damages cap: [from retrieved Contract Data / CANNOT CONFIRM /
NONE STATED]
Agreed damages applied by Employer: [YES — amount and period from
retrieved payment certificates / NOT FOUND IN WAREHOUSE / CANNOT CONFIRM]
Enforceability assessment: [OPERATIVE / POTENTIALLY UNENFORCEABLE —
state period and basis / CANNOT ASSESS]
Note: [Legal advice required on [governing law] position on time
at large and agreed damages enforceability — this assessment presents
the factual position from retrieved documents only]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
*(Confidence scale: GREEN = all required evidence retrieved and findings fully supported | AMBER = Layer 2b not retrieved or amendment position unknown -- findings provisional | RED = critical document absent -- findings materially constrained | GREY = standard form unconfirmed -- form-specific analysis suspended. Full definition: skills/c1-skill-authoring/references/grounding_protocol.md)*
Summary: [two to three sentences — facts from retrieved documents only;
note that legal advice is required for the legal conclusion]
```

---

## Analytical framework
*Reference only — do not apply any legal principle, governing law
position, or agreed damages enforceability conclusion from this section
without first confirming the applicable facts from retrieved project
documents and noting that legal advice is required.*

**Prevention principle — analytical reference:**
The prevention principle holds that a party cannot take advantage of
its own wrong. In construction contracts, if the Employer prevents
the Contractor from completing by the contractual date and the
contract contains no mechanism to extend time for that prevention,
time goes at large. The Contractor's obligation becomes one of
reasonable time, and the Employer loses the right to agreed damages.
Under most standard forms, the time extension clause is designed to
prevent this outcome. Time at large remains available where the time
extension clause does not cover the act of prevention or where the
mechanism has been removed.

**Governing law — analytical reference:**
The governing law fundamentally affects the time at large analysis.
The prevention principle operates differently under common law
systems and civil law systems. Some legal systems have well-developed
case law on time at large; others treat it as an emerging or
unsettled concept. The governing law must be confirmed from the
retrieved contract documents before any legal analysis is stated.
This skill presents the factual position from retrieved documents
only — legal advice is required for the legal conclusion on whether
time is at large.

**Agreed damages provisions — analytical reference:**
Most standard forms provide for agreed damages as the Employer's
remedy for late completion. The rate and cap are in the Contract
Data — always extract from Layer 1. Where time is at large, the
agreed damages mechanism is suspended and the Contractor's
obligation is to complete within a reasonable time.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies to
any contract form. All characterisations grounded in retrieved warehouse
documents only.*
