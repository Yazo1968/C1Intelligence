# Engineer Identification — Legal & Contractual Specialist

## When to apply this skill

Apply this skill at the start of every Legal & Contractual analysis, immediately after
contract_assembly.md. The identity and authority of the contract administrator must be
established before notice compliance, instruction validity, entitlement, or any other
legal analysis can proceed. Also apply when a query directly concerns the Engineer's
authority, the validity of a determination, the identity of the certifier, or the
delegation of Engineer functions.

---

## Before you begin

This is a Round 1 skill. There are no upstream specialist findings to read.

The FIDIC book type and edition must already be established from contract_assembly.md
before this skill runs. Read the contract_assembly.md output and extract:
- FIDIC book type (Red / Yellow / Silver)
- FIDIC edition (1999 / 2017)

If contract_assembly.md has not yet run or its output is not available, run
contract_assembly.md first. Do not begin engineer identification without knowing the
book type — the entire analysis differs between Red/Yellow and Silver Book.

Before beginning the analysis, retrieve the following from the warehouse:
- Engineer's appointment letter or Employer's Representative appointment letter
- Any delegation notices issued by the Engineer or Employer's Representative
- Particular Conditions Clause 3 (Engineer / Employer's Representative)
- Any PMC, Supervision Consultant, or Construction Manager appointment letters
- Correspondence headers and notice routing from project correspondence

---

## Analysis workflow

**Step 1 — Determine the contract administrator role from the book type**

Red Book and Yellow Book: the contract administrator is the Engineer under Clause 3.
The Engineer acts for the Employer in most matters but holds an independent determination
obligation — in 1999 editions the duty is to act fairly; in 2017 editions the Engineer
must act neutrally between the parties when making determinations under Clause 3.7.

Silver Book: there is no Engineer. The contract administrator is the Employer's
Representative under Clause 3. The Employer's Representative acts as the Employer's
agent with no independent determination obligation. On Silver Book projects, skip
Steps 2 and 3 and proceed directly to Step 4.

**Step 2 — Identify the Engineer (Red and Yellow Books only)**

From the Particular Conditions Contract Data / Appendix to Tender and the Engineer's
appointment letter, identify:
- The name and organisation of the Engineer
- The date of appointment
- Whether the appointment was in place at the contract commencement date

Check whether the entity named as Engineer in the Particular Conditions matches the
entity in the appointment letter. If they differ, flag as a CONTRADICTION — both
identities must be surfaced and the discrepancy noted.

**Step 3 — Map the Engineer's authority under Clause 3 (Red and Yellow Books only)**

The Engineer's authority under FIDIC Clause 3 covers the following functions. For each
function, confirm whether the Engineer holds full authority, delegated authority, or
restricted authority based on the Particular Conditions and any delegation notices:

- Issue instructions (Clause 3.3 / 3.4 in 1999; Clause 3.5 in 2017)
- Agree or determine entitlement (Clause 3.5 in 1999; Clause 3.7 in 2017)
- Issue payment certificates (Clause 14.6)
- Issue Taking-Over Certificate (Clause 10.1)
- Issue Performance Certificate (Clause 11.9)
- Approve programme submissions (Clause 8.3)
- Issue variation instructions (Clause 13.1)

Check the Particular Conditions for any amendment to Clause 3 that restricts the
Engineer's authority or requires Employer approval before the Engineer can act. This
is a common and forensically significant pattern in GCC contracts — an Engineer whose
authority is subject to Employer approval is not independent and cannot make neutral
determinations. Flag any such restriction explicitly.

**Step 4 — Identify the Employer's Representative (Silver Book only)**

From the Particular Conditions Contract Data and the Employer's Representative
appointment letter, identify:
- The name and organisation of the Employer's Representative
- The scope of delegated authority
- Whether any functions have been sub-delegated to named individuals

On Silver Book projects, flag immediately that there is no independent certifier — the
Employer or Employer's Representative issues payment notices rather than independent
IPCs. Flag that Engineer's determinations do not exist on Silver Book projects —
disputes escalate directly to DAB (1999) or DAAB (2017) without a prior determination
step. This is a critical distinction for Claims and Governance specialists.

**Step 5 — Check for GCC split-role pattern (Red and Yellow Books only)**

In many GCC projects the Engineer's role under FIDIC is split between two or more
entities — typically a Project Management Consultant (PMC) or Construction Manager (CM)
handling administrative functions and a Supervision Consultant (SC) handling technical
functions. FIDIC does not provide for this split.

Search for evidence of role fragmentation:
- Multiple appointment letters covering different Engineer functions
- Correspondence routed to different entities for different purposes
- References in correspondence to "PMC", "SC", "CM", "Supervision Engineer",
  "Contract Administrator" as distinct roles
- Site instructions signed by a different entity than payment certificates

If role fragmentation is identified, map each Engineer function listed in Step 3 to
the entity actually performing it. Identify any functions where the responsible entity
is unclear or where both entities appear to have acted. Flag every gap and ambiguity
— notice routing errors caused by split-role ambiguity are a primary source of
procedural deficiency findings.

**Step 6 — Assess delegation validity**

Under FIDIC Clause 3.2 (1999) and Clause 3.4 (2017), the Engineer may delegate
authority to assistants. Any delegation must be in writing and must specify the scope
of delegated authority. A determination or instruction issued by a person who was not
properly delegated authority may be invalid.

For each entity or individual found to be performing Engineer functions, confirm:
- Was a written delegation notice issued?
- Does the delegation cover the function being performed?
- Was the delegation notice communicated to the Contractor?

If any function is being performed without a valid written delegation, flag as
DELEGATION GAP with the specific function and entity identified.

**Step 7 — Compile and structure findings**

Compile all findings in the output format below. Flag any ambiguity about Engineer
identity or authority clearly — these findings are critical for notice_and_instruction_
compliance.md, which cannot assess notice validity without knowing who the correct
recipient is.

---

## Classification and decision rules

**Engineer identity confirmed:**
- Single entity named consistently in Particular Conditions and appointment letter,
  appointment pre-dates contract commencement: CONFIRMED
- Entity named in Particular Conditions differs from appointment letter: CONTRADICTION
  — flag both, state which governs per hierarchy, AMBER confidence
- No appointment letter in warehouse: UNCONFIRMED — flag absence, state name from
  Particular Conditions only, AMBER confidence

**Split-role pattern:**
- No evidence of role fragmentation: state Engineer is single entity, no split-role
  flag required
- Evidence of role fragmentation but functions clearly allocated: SPLIT-ROLE IDENTIFIED
  — map functions, flag for notice routing, AMBER confidence
- Evidence of role fragmentation with gaps or overlaps in function allocation:
  SPLIT-ROLE WITH GAPS — list each gap explicitly, RED confidence for affected functions

**Engineer independence (Red and Yellow Books):**
- No Particular Conditions restriction on Engineer authority: INDEPENDENT
- Particular Conditions require Employer approval for Engineer decisions: NOT INDEPENDENT
  — flag explicitly; determinations issued under these conditions may not satisfy the
  FIDIC neutrality standard; forensically significant in any dispute about
  Engineer's determinations

**Silver Book Employer's Representative:**
- Appointment confirmed, authority scope documented: CONFIRMED — note absence of
  independence obligation; note no determination mechanism
- Appointment not in warehouse: UNCONFIRMED — flag absence

**Delegation:**
- All functions covered by written delegations: VALID
- One or more functions performed without written delegation: DELEGATION GAP — list
  each gap

---

## When to call tools

**Signal:** Particular Conditions name an Engineer entity but no appointment letter
has been retrieved
**Tool:** `search_chunks` querying for the Engineer entity name and "appointment"
**Look for:** Appointment letter, novation of appointment, any document confirming
the entity's authority to act

**Signal:** Correspondence headers route notices to different entities for different
purposes — possible split-role
**Tool:** `search_chunks` querying for "PMC", "Supervision Consultant", "Construction
Manager", "Contract Administrator"
**Look for:** Appointment letters or scope documents for each entity; confirmation of
which functions each entity holds

**Signal:** A delegation notice is referenced in correspondence but has not been
retrieved
**Tool:** `get_related_documents` filtered to document type: Delegation Notice,
Engineer's Instruction
**Look for:** Written delegation confirming scope and date; confirm it was issued
before the relevant action was taken

**Signal:** The Engineer entity named in the contract appears to have changed during
the project — different entity names appear in earlier vs later correspondence
**Tool:** `search_chunks` querying for "novation", "replacement", "new Engineer",
"Engineer appointment"
**Look for:** Novation of Engineer appointment or formal replacement notice; if found,
flag the date of change and its effect on prior notices and instructions

---

## Always flag — regardless of query

1. **The identity of the contract administrator** — always state who the Engineer or
   Employer's Representative is and the source document that confirms this. Every
   downstream specialist needs to know who issued instructions, certificates, and
   determinations.

2. **Any Particular Conditions restriction on Engineer independence** — always flag
   if the Engineer's authority is subject to Employer approval. This affects the
   validity of every determination the Engineer has issued and is one of the most
   forensically significant findings in GCC contract administration.

3. **Split-role pattern** — always flag if two or more entities are performing
   Engineer functions. The ambiguity about who is "the Engineer" for notice purposes
   affects every notice compliance assessment downstream.

4. **Silver Book — absence of independent certifier and determination mechanism** —
   always flag on Silver Book projects. Claims and Governance specialists must know
   that payment notices come from the Employer, not an independent certifier, and
   that disputes go directly to DAB/DAAB without an Engineer's determination.

5. **Delegation gaps** — always flag any Engineer function being performed by an
   entity or individual without a confirmed written delegation. Instructions or
   determinations issued outside delegated authority may be invalid.

---

## Output format

```
## Engineer Identification Assessment

### Contract Administrator Role
Book type: [Red / Yellow / Silver]
Role: [Engineer (Clause 3) / Employer's Representative (Clause 3)]
Independence obligation: [YES — fair determination (1999) / YES — neutral determination
(2017) / NO — Silver Book / RESTRICTED — Employer approval required per PC Clause X.X]

### Engineer / Employer's Representative Identity
Name and organisation: [identity or UNCONFIRMED]
Source: [document name and reference]
Appointment date: [date or not confirmed]
Appointment pre-dates contract commencement: [YES / NO / CANNOT CONFIRM]
Contradiction with Particular Conditions: [YES — state both identities / NO]

### Authority Mapping (Red and Yellow Books)
| Function | FIDIC Clause | Authority Status | Delegated To | Notes |
|---|---|---|---|---|
| Issue instructions | 3.3/3.4 (1999) / 3.5 (2017) | [FULL/DELEGATED/RESTRICTED] | | |
| Agree or determine entitlement | 3.5 (1999) / 3.7 (2017) | [FULL/DELEGATED/RESTRICTED] | | |
| Issue payment certificates | 14.6 | [FULL/DELEGATED/RESTRICTED] | | |
| Issue Taking-Over Certificate | 10.1 | [FULL/DELEGATED/RESTRICTED] | | |
| Issue Performance Certificate | 11.9 | [FULL/DELEGATED/RESTRICTED] | | |
| Approve programme | 8.3 | [FULL/DELEGATED/RESTRICTED] | | |
| Issue variations | 13.1 | [FULL/DELEGATED/RESTRICTED] | | |

### Split-Role Assessment
Split-role pattern identified: [YES / NO]
[If YES:]
| Function | Entity performing function | Delegation confirmed |
|---|---|---|
| [function] | [entity] | [YES / NO / PARTIAL] |
Gaps identified: [list or "None"]
Notice routing implication: [state which entity notices must be addressed to for each
function, or flag ambiguity]

### Employer's Representative Assessment (Silver Book only)
Name and organisation: [identity or UNCONFIRMED]
Source: [document name and reference]
Authority scope: [summary of delegated authority]
Sub-delegations: [list or "None identified"]
No independent certifier: CONFIRMED — payment notices issued by Employer /
Employer's Representative
No determination mechanism: CONFIRMED — disputes escalate directly to
[DAB (1999) / DAAB (2017)]

### Delegation Validity
Overall delegation status: [VALID / DELEGATION GAPS IDENTIFIED]
[If gaps:]
| Function | Performed by | Written delegation | Gap description |
|---|---|---|---|

### Findings for Downstream Specialists
Contract administrator: [name and entity]
Notice recipient for Contractor claims: [entity name — critical for notice compliance]
Payment certifier: [entity name and independence status]
Determination mechanism: [Engineer Cl. 3.5/3.7 / None — Silver Book]
Split-role flag: [YES with mapping / NO]
Engineer independence: [INDEPENDENT / RESTRICTED / NOT APPLICABLE — Silver Book]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences stating who the contract administrator is, any
authority restrictions or split-role ambiguity, and the key forensic implication
for downstream specialists]
```

---

## Domain knowledge and standards

### FIDIC Clause 3 — The Engineer's Role

**Red and Yellow Books 1999:** The Engineer acts for the Employer under Clause 3.1 but
is required to act fairly when making determinations under Clause 3.5. The 1999 standard
does not use the word "neutral" — the obligation is fairness, not neutrality. The
Engineer has no time limit to issue a determination under 1999 Clause 3.5.

**Red and Yellow Books 2017:** The Engineer is required to act neutrally between the
parties when exercising functions under Clause 3.7 (determinations). The 2017 edition
introduces an 84-day timetable for determinations (42 days consultation + 42 days
determination). If no determination is issued within the period, it is deemed a
rejection. The neutrality obligation is a significant enhancement of Engineer
independence compared to 1999.

**Silver Book 1999 and 2017:** There is no Engineer. Clause 3 governs the Employer's
Representative. The Employer's Representative acts as the Employer's agent. In the 2017
Silver Book the 84-day timetable is adopted but the neutrality obligation is deliberately
omitted — this was a conscious FIDIC drafting decision reflecting the Silver Book's
risk allocation philosophy. The absence of neutrality is not a Particular Conditions
amendment — it is the standard Silver Book position.

### GCC-Specific Engineer Authority Patterns

**Employer approval requirements:** A common Particular Conditions amendment in GCC
contracts (particularly Abu Dhabi government projects and Saudi Vision 2030 projects)
requires the Engineer to obtain the Employer's approval before issuing determinations,
granting extensions of time, or certifying variations above a threshold value. This
amendment is forensically significant because:
- It means the Engineer cannot act independently on these matters
- Determinations issued without required Employer approval may be challengeable
- It creates a conflict of interest — the Employer is effectively determining its own
  liability to the Contractor
- Under FIDIC 2017 this amendment conflicts with the Engineer's neutrality obligation
  and may constitute a Golden Principles violation (GP1)

When this pattern is found, flag it explicitly and note its implications for every
determination and certificate in the project record.

**PMC/SC split-role pattern:** The most common GCC split-role pattern is:
- Project Management Consultant (PMC) or Construction Manager (CM): holds contract
  administration authority including payment certification, variation approval, and
  formal determinations
- Supervision Consultant (SC) or Resident Engineer (RE): holds technical authority
  including site instructions, RFI responses, drawing approvals, and NCR issuance

FIDIC does not accommodate this structure. The forensic consequences are:
- A notice addressed to the SC rather than the PMC (or vice versa) may be argued
  invalid by the Employer
- A site instruction issued by the SC may be argued not to constitute a formal
  Engineer's Instruction under Clause 3 unless the SC held a valid delegation
- Payment certificates issued by the PMC may be challenged if the PMC was not
  formally appointed as Engineer

The test is always: what do the contract documents say, and is there a written
delegation that covers the relevant function?

### DIFC Court Guidance on Engineer Authority

Key DIFC Court decisions confirm that the Engineer's determination under FIDIC Clause
3.5 (1999) is a condition precedent to DAB proceedings in most circumstances. An attempt
to go to DAB without a prior Engineer's determination (or a deemed rejection) may be
challenged as procedurally premature. This reinforces the importance of correctly
identifying who holds the determination authority and whether determinations were
properly issued.
