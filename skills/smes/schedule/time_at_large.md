# Time at Large

**Skill type:** Mixed
- Contract-type-specific: the EOT mechanism that prevents time going
  at large differs by FIDIC book and edition; whether the Particular
  Conditions provide an adequate EOT mechanism is project-specific
- Contract-type-agnostic: the prevention principle and the conditions
  for time going at large apply as a matter of law regardless of
  contract type; the assessment framework is consistent
**Layer dependency:**
- Layer 1 — project documents: Particular Conditions (EOT clause,
  LD clause, completion mechanism); Contract Data (Time for
  Completion, LD rate); evidence of Employer acts of prevention
  (instructions, delays, access restrictions); EOT claim history
  and responses; Taking-Over Certificate (if issued)
- Layer 2 — reference standards: FIDIC EOT clause for the confirmed
  book and edition; FIDIC LD clause; applicable law (governing law
  confirmed from contract documents — UAE Civil Code, Saudi law,
  Qatar Civil Code, or English common law)
**Domain:** Schedule & Programme SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when a query concerns whether time is at large, whether the
Employer's right to liquidated damages is enforceable, whether the
prevention principle has been triggered, or whether the Contractor
has an obligation to complete within a reasonable time rather than
by the contractual completion date. Apply when Employer-caused delays
have been identified but no EOT mechanism appears to have been
triggered or was available.

---

## Before you begin

### Foundational requirements

Read the invoking orchestrator findings, delay_identification
findings, and eot_quantification findings.

From the invoking orchestrator:
- Confirmed FIDIC book and edition
- Governing law as confirmed from retrieved contract documents
- LD rate and cap as confirmed from retrieved Contract Data
- Whether the EOT clause exists in the retrieved Particular
  Conditions and whether it provides an adequate mechanism to
  extend time for Employer-caused delays

From delay_identification:
- What Employer-caused delay events have been identified from
  retrieved documents

From eot_quantification:
- Whether EOT has been claimed and what the response was
- Whether EOT was granted, denied, or not responded to

**Time at large is a legal remedy of last resort.** It arises
only when the Employer has caused delay AND the contract does not
provide an adequate mechanism to extend time for that delay.
Under standard FIDIC (all books, both editions), the EOT clause
is specifically designed to prevent time going at large. Flag this
context in the output.

**If no Employer-caused delay events have been identified from
retrieved documents:** State CANNOT ESTABLISH the prevention
principle from retrieved documents. Do not assess time at large
without a founded Employer delay.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- The Particular Conditions — EOT clause, LD clause, completion
  clause, and any provision addressing the consequences of Employer
  delay
- The Contract Data — Time for Completion, LD rate, LD cap
- Evidence of the Employer-caused acts of prevention (instructions,
  access restrictions, delayed information — from delay_identification
  findings)
- The EOT claim history and responses (from eot_quantification
  findings)
- The Taking-Over Certificate (if issued — establishes actual
  completion date)
- The governing law clause in the Particular Conditions

**If the Particular Conditions and LD clause have not been retrieved:**
State CANNOT ASSESS whether time is at large — the LD mechanism
is central to the analysis.

**If the governing law has not been confirmed from retrieved
documents:** State CANNOT ASSESS the legal framework for time at
large. The prevention principle operates differently under English
common law, UAE Civil Code, Saudi law, and Qatar Civil Code.

### Layer 2 documents to retrieve (reference standards)

Call `search_chunks` to retrieve from Layer 2:
- FIDIC EOT clause for the confirmed book and edition
- FIDIC LD clause (Clause 8.7 for 1999 / Clause 8.8 for 2017 or
  equivalent) for the confirmed book
- Any applicable law from Layer 2 (UAE Civil Code, Qatar Civil Code
  if available in Layer 2)

**Purpose:** To establish the standard FIDIC EOT and LD mechanism
for structural comparison against the retrieved Particular
Conditions. The actual terms are in the retrieved PC.

---

## Analysis workflow

### Step 1 — Confirm the EOT mechanism in the retrieved contract
*Contract-type-specific*

From the retrieved Particular Conditions:
- Is the FIDIC EOT clause present and unamended?
- Has the EOT clause been deleted, restricted, or modified in a
  way that prevents the Contractor from obtaining an EOT for
  Employer-caused delays?
- Does the Particular Conditions EOT mechanism cover the specific
  Employer acts of prevention identified in delay_identification?

**If the EOT mechanism is present and unamended, or amended in a
way that still provides for Employer-caused delays:** The standard
FIDIC position is that the prevention principle is excluded by the
EOT mechanism. Time is not at large provided the Contractor has
properly invoked the EOT procedure.

**If the EOT mechanism has been deleted or restricted so that it
does not cover the Employer's acts of prevention:** The prevention
principle may apply — flag and proceed with the analysis.

### Step 2 — Identify acts of prevention from retrieved documents
*Contract-type-agnostic*

From delay_identification findings and the retrieved documents,
identify the specific Employer acts of prevention:
- Instructions that varied the works and prevented completion by
  the contractual date
- Failure to give access, late information, or other Employer
  defaults that prevented timely completion

**The acts of prevention must be evidenced in retrieved documents.**
Do not identify acts of prevention from the claim submission alone.

For each act: state the event, the date, the source document, and
whether it is an act for which the EOT mechanism provides relief.

### Step 3 — Assess whether the EOT mechanism was properly invoked
*Contract-type-specific*

From notice_and_instruction_compliance and eot_quantification
findings:
- Was a notice of claim issued for each act of prevention?
- Was the EOT claim properly submitted?
- Was EOT granted for each act of prevention?

**If the Contractor failed to invoke the EOT mechanism properly:**
Time at large may not be available as a remedy — the Contractor's
failure to invoke the mechanism may prevent it from relying on
the prevention principle. Flag this dependency.

**If the Contractor properly invoked the EOT mechanism but EOT
was denied or not responded to:** The prevention principle argument
is stronger — the Contractor did what the contract required and
was denied relief. State this from the retrieved documents.

### Step 4 — Assess the LD enforceability position
*Contract-type-specific*

From the retrieved Particular Conditions and Contract Data:
- What is the LD rate? (Extract from Contract Data — do not apply
  any default)
- Is there an LD cap? (Extract from retrieved documents)
- Has the LD rate been applied by the Employer? (From retrieved
  payment certificates)
- Is the LD rate genuine pre-estimate of loss or potentially
  a penalty? (This is a legal question — flag that it requires
  legal advice; state the LD rate and any evidence from retrieved
  documents about the basis for the rate)

**If time is at large:** The Employer's right to LDs is suspended
for the period of time at large. The Contractor is obliged to
complete within a reasonable time. LDs cannot accrue while time
is at large.

### Step 5 — Assess the governing law impact
*Contract-type-specific*

The prevention principle and time at large operate differently
depending on the governing law confirmed from the retrieved
contract documents.

**English common law (DIFC, English law contracts):**
The prevention principle is well-established. Time goes at large
when the Employer prevents completion and no mechanism exists to
extend time. LDs cannot be recovered.

**UAE Civil Code (UAE onshore):**
The UAE Civil Code does not expressly codify the prevention
principle. UAE courts have assessed LD clauses under the penalty
clause framework (Art. 390) and have reduced disproportionate LDs.
The good faith doctrine (Art. 246) has been applied. The position
on time at large is less settled than under English law.

**Qatar Civil Code:**
Similar framework to UAE. LD assessment under the Civil Code
penalty provisions. Time at large less developed in Qatari
jurisprudence.

**Saudi law:**
Saudi courts apply Sharia principles alongside commercial law.
LD clauses are assessed for consistency with Sharia principles
on permitted compensation. Time at large as a concept has limited
direct precedent in Saudi proceedings.

**In all cases:** State the governing law confirmed from retrieved
documents and flag that the time at large argument requires legal
advice specific to the governing law. Do not state a legal
conclusion on whether time is at large — state the facts from
the retrieved documents and the legal framework.

---

## Classification and decision rules

**Prevention principle:**

Employer acts of prevention identified in retrieved documents AND
EOT mechanism does not cover those acts from the retrieved PC →
PREVENTION PRINCIPLE POTENTIALLY ENGAGED — flag; proceed to LD
enforceability assessment

Employer acts of prevention identified AND adequate EOT mechanism
exists in retrieved PC covering those acts AND Contractor properly
invoked it → EOT MECHANISM AVAILABLE — time at large unlikely
under standard FIDIC; flag if EOT was denied without justification

Employer acts of prevention identified AND Contractor failed to
invoke EOT mechanism → PROCEDURAL FAILURE — flag; time at large
argument weakened by failure to invoke available mechanism

No Employer acts of prevention confirmed from retrieved documents →
PREVENTION PRINCIPLE NOT ESTABLISHED FROM RETRIEVED DOCUMENTS

**LD enforceability:**

Time at large conditions met AND LD rate confirmed from retrieved
Contract Data → LDs POTENTIALLY UNENFORCEABLE FOR PERIOD OF
PREVENTION — flag; state the LD rate and the implications
Time not at large → LD MECHANISM OPERATIVE — state confirmed LD
rate and cap from retrieved documents
LD rate not confirmed from retrieved Contract Data →
CANNOT CONFIRM LD EXPOSURE

---

## When to call tools

**Signal:** LD clause or LD rate not confirmed from retrieved
Contract Data or Particular Conditions
**Action:** `search_chunks` with query "liquidated damages rate
clause 8.7 8.8 particular conditions contract data"; `get_document`
on Contract Data document ID
**Look for:** The LD rate, LD cap, and the LD clause

**Signal:** Acts of prevention referenced but the underlying
instructions or access records not retrieved
**Action:** `search_chunks` with query "[act description]
[date range]"; `get_related_documents` with document types
"Engineer's Instruction", "Site Diary", "Correspondence"
**Look for:** The instruction or record evidencing the act of
prevention

**Signal:** Governing law not confirmed from retrieved Particular
Conditions
**Action:** `search_chunks` with query "governing law applicable
law particular conditions clause 1.4"
**Look for:** The governing law clause in the contract

**Signal:** Layer 2 FIDIC LD clause not retrieved
**Action:** `search_chunks` with query "[FIDIC book] [edition]
clause 8.7 8.8 liquidated damages delay damages"
**Look for:** Standard FIDIC LD clause for the confirmed book
and edition

---

## Always flag — regardless of query

1. **Prevention principle potentially engaged** — always flag when
   Employer acts of prevention have been identified and the EOT
   mechanism does not cover them from the retrieved PC; state the
   consequence in one sentence.

2. **LD rate not confirmed from retrieved Contract Data** — always
   flag; state that LD exposure cannot be confirmed.

3. **Contractor's failure to invoke EOT mechanism** — always flag
   where acts of prevention exist but no notice or EOT claim was
   issued; state the forensic implication for the time at large
   argument.

4. **Governing law not confirmed** — always flag; the time at large
   analysis depends fundamentally on the governing law.

5. **LDs applied by Employer for a period that includes confirmed
   Employer-caused delays without granted EOT** — always flag;
   state the period, the LD amount applied (from retrieved payment
   certificates), and the Employer delay events during that period.

---

## Output format

```
## Time at Large Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2 Reference Retrieved
[State whether FIDIC EOT clause, LD clause, and applicable law
were retrieved. If not: state analytical knowledge applied.]

### Governing Law
Confirmed: [YES — governing law and source document / CANNOT CONFIRM]

### EOT Mechanism Assessment
EOT clause in retrieved PC: [PRESENT AND UNAMENDED / AMENDED —
describe / DELETED / CANNOT CONFIRM — PC not retrieved]
Covers Employer-caused delays identified: [YES / PARTIALLY /
NO / CANNOT CONFIRM]
Source: [PC reference]

### Acts of Prevention
[List from delay_identification findings with retrieved document
sources for each act. State whether each act is covered by the
retrieved EOT mechanism.]

### EOT Invocation Assessment
[From notice_and_instruction_compliance and eot_quantification
findings — whether the Contractor properly invoked the mechanism
for each act of prevention]

### Prevention Principle Assessment
Prevention principle engagement: [POTENTIALLY ENGAGED — reason /
NOT ESTABLISHED FROM RETRIEVED DOCUMENTS / EOT MECHANISM AVAILABLE /
PROCEDURAL FAILURE — Contractor failed to invoke mechanism]

### LD Enforceability
LD rate: [from retrieved Contract Data / CANNOT CONFIRM]
LD cap: [from retrieved Contract Data / CANNOT CONFIRM / NONE STATED]
LDs applied by Employer: [YES — amount and period from retrieved PCs /
NOT FOUND IN WAREHOUSE / CANNOT CONFIRM]
LD enforceability assessment: [LDs OPERATIVE / LDs POTENTIALLY
UNENFORCEABLE — state period and basis / CANNOT ASSESS]
Note: [Legal advice required on [governing law] position on time
at large and LD enforceability — this assessment presents the
factual position from retrieved documents only]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only;
note that legal advice is required for the legal conclusion]
```

---

## Analytical framework
*Reference only — do not apply any legal principle, governing law
position, or LD enforceability conclusion from this section without
first confirming the applicable facts from retrieved project documents
and noting that legal advice is required.*

**Prevention principle — analytical reference:**
The prevention principle holds that a party cannot take advantage
of its own wrong. In construction contracts, if the Employer
prevents the Contractor from completing by the contractual date,
and the contract contains no mechanism to extend time for that
prevention, time goes at large. The Contractor's obligation
becomes one of reasonable time, and the Employer loses the right
to LDs. Under standard FIDIC, the EOT clause is designed to
prevent this outcome. Time at large remains available as an
argument where the EOT clause does not cover the act of
prevention or where the mechanism has been removed.

**FIDIC LD clause — analytical reference:**
FIDIC provides for delay damages (LDs) as the Employer's remedy
for late completion. The rate and cap are in the Contract Data —
always extract from Layer 1. The LD clause does not prevent time
going at large where the prevention principle is engaged —
it simply sets the rate of LDs where they do apply.

**GCC governing law — analytical reference:**
The governing law fundamentally affects the time at large analysis.
English common law (DIFC) — established prevention principle.
UAE Civil Code — LD penalty reduction mechanism under Art. 390;
good faith doctrine under Art. 246; time at large less developed.
Saudi law — Sharia-influenced assessment of compensation.
Qatar — hybrid civil law system; similar to UAE. The governing
law must be confirmed from the retrieved contract before any
legal analysis is stated. This skill presents the factual position
only — legal advice is required for the legal conclusion.
