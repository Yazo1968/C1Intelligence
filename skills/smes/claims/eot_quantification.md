# EOT Quantification

**Skill type:** Contract-type-specific (EOT clause, entitlement events,
and Engineer/Employer's Representative authority differ by book and edition)
**Domain:** Claims & Disputes SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply this skill when retrieved chunks contain an EOT claim submission,
a delay analysis report, a notice of delay referencing a programme impact,
a query about entitlement to additional time, or a request to assess
whether a claimed extension is supported. Also apply when a Taking-Over
Certificate shows a completion date that differs materially from the
contractual completion date and no EOT record has been found.

---

## Before you begin

**Step 1 — Establish the governing contract type.**
Read the Legal orchestrator findings. Extract:
- FIDIC book: Red / Yellow / Silver
- FIDIC edition: 1999 or 2017
- Time for Completion: extract from the contract documents — do not
  assume any period
- Contractual completion date: extract from the contract or the
  programme — this is the baseline against which delay is measured
- Any Particular Conditions amendments to the EOT clause

If Legal orchestrator findings are not available, call `search_chunks`
with query "time for completion contractual completion date programme"
before proceeding.

**Step 2 — Extract the EOT clause from the Particular Conditions.**
The EOT entitlement events are listed in the General Conditions but
are frequently amended by Particular Conditions — events added,
removed, or qualified. Extract the actual list of entitlement events
from the project's Particular Conditions. Do not apply the General
Conditions list without first confirming it has not been amended.

**Step 3 — Establish the notice position from notice_compliance skill.**
EOT entitlement is procedurally gated by notice compliance. If the
Claims SME has already assessed notice compliance for the relevant
claim, read those findings before beginning the EOT analysis. A
time-barred notice extinguishes the EOT entitlement regardless of
the merits of the delay analysis.

**Step 4 — Identify the delay analysis methodology used.**
This must be identified from the documents — do not assume. The
methodology determines what evidence is required and what the
output means. See Domain Knowledge section for the accepted
methodologies and their data requirements.

---

## Analysis workflow

**Step 1 — Retrieve all EOT claim documents.**
Call `get_related_documents` with document_type "EOT Claim".
Call `get_related_documents` with document_type "Delay Analysis Report".
Call `search_chunks` with query "extension of time critical path
delay programme impact".
Compile a complete list of claim submissions and supporting analyses.

**Step 2 — Map claimed delay events to entitlement clauses.**
For each delay event in the claim:
- Identify the FIDIC clause cited as the entitlement basis
- Verify that clause is present and unamended in the project's
  Particular Conditions (Step 2 of Pre-Flight Check)
- Classify the event: Employer Risk Event / Neutral Event /
  Contractor Risk Event
- Note that entitlement differs by event type — see decision framework

**Step 3 — Assess the baseline programme.**
The delay analysis requires a valid baseline programme. Retrieve the
baseline programme document. Assess:
- Is it the programme accepted by the Engineer (Red/Yellow) or
  approved by the Employer's Representative (Silver)?
- Does it show the contractual completion date?
- Is it a CPM network — does it show the critical path?
- Was it submitted within the period required by the contract?
  Extract the programme submission requirement from the Particular
  Conditions — do not apply the standard form default.

If no baseline programme is in the warehouse, flag this immediately.
A delay analysis without a baseline programme cannot be verified.

**Step 4 — Assess as-built records.**
The as-built programme or contemporaneous progress records are
required to verify actual performance. Retrieve:
- As-built programme (if submitted)
- Monthly progress reports for the delay period
- Site diaries for key delay events
Assess whether the delay events are evidenced in contemporaneous
records or only in the retrospective claim submission.

**Step 5 — Assess the delay analysis methodology.**
Identify the methodology used (see Domain Knowledge). For each
methodology, apply the specific assessment criteria below. Flag
any methodology that is unsupported by the available records.

**Step 6 — Assess concurrent delay.**
Concurrent delay is the simultaneous occurrence of Employer-caused
and Contractor-caused delay events affecting the critical path. It
must always be considered when the as-built programme shows multiple
overlapping delay events. Assess:
- Has the claim addressed concurrent delay?
- If concurrent delay is present, what is its effect on the
  entitlement? — see decision framework
- Has the Contractor demonstrated that its own concurrent delay
  did not cause or contribute to the claimed completion delay?

**Step 7 — Assess float.**
Float is a buffer in the programme between an activity's early
completion and its latest permissible completion. Assess:
- Does the delay analysis correctly treat float as a shared resource
  (absent express contractual stipulation to the contrary)?
- Has the Contractor claimed an EOT for a period consumed by float
  rather than a true critical path delay?
- Does the Particular Conditions contain an express float ownership
  clause? If so, apply it — extract from documents.

**Step 8 — Assess the claimed EOT quantum.**
The claimed number of days must be supported by the delay analysis.
Compare: the delay event duration, the critical path impact
demonstrated, and the EOT days claimed. Flag any gap between the
demonstrated impact and the claimed quantum.

**Step 9 — Assess the Engineer's or Employer's Representative's
response.**
Retrieve any Engineer's determination or Employer's Representative
response to the EOT claim. Compare the awarded EOT (if any) against
the claimed EOT. Identify the reasons for any reduction or rejection
stated in the determination.

---

## Classification and decision rules

**Entitlement by event type:**

Employer Risk Event (e.g., late access, Employer instruction,
Employer-supplied materials failure, exceptionally adverse weather
where included, unforeseeable physical conditions under Red/Yellow):
→ **EOT + Cost** entitlement (both editions, all books where the
  event is listed — verify in Particular Conditions)

Neutral Event (e.g., exceptionally adverse climatic conditions
where listed as neutral, certain force majeure events):
→ **EOT only** — no cost entitlement (verify in Particular Conditions)

Contractor Risk Event:
→ **No entitlement** — Contractor bears the delay

**Concurrent delay:**

Employer-caused concurrent delay with Contractor-caused concurrent
delay on the critical path:
→ Under SCL Protocol 2nd Ed. 2017 (the GCC standard): Contractor
  retains time entitlement but cost entitlement may be reduced or
  extinguished for the concurrent period
→ Flag concurrent delay and state which events are concurrent and
  what period is affected
→ Do not resolve the entitlement question — state both positions
  and the documents that support each

**Critical path impact:**

Delay event demonstrated to affect critical path activities:
→ EOT entitlement assessment proceeds

Delay event affecting non-critical activities only (float absorbed):
→ No EOT entitlement for that event unless float is exhausted
→ Flag: state which activities were affected and that float
  absorption does not generate EOT entitlement

Critical path not demonstrated in the claim:
→ Classify as **CRITICAL PATH NOT ESTABLISHED**
→ Flag: EOT quantum cannot be verified without critical path
  analysis

**Baseline programme:**

Programme accepted/approved and CPM-based:
→ Proceed with analysis

Programme not accepted/approved or not CPM-based:
→ Flag: state the deficiency and its effect on the reliability
  of the delay analysis

Programme absent from warehouse:
→ Classify as **CANNOT VERIFY — BASELINE PROGRAMME MISSING**
→ Flag immediately

---

## When to call tools

**Signal:** The EOT claim references a delay event but no
contemporaneous record (site diary, RFI, instruction) has been
retrieved to support it.
**Action:** Call `search_chunks` with query "[event description]
[date range]" and call `get_related_documents` with document_type
"Site Diary" for the relevant period.
**Look for:** Any contemporaneous document that records the event
independently of the claim submission.

**Signal:** The delay analysis references a programme revision
or update but only the baseline programme has been retrieved.
**Action:** Call `get_related_documents` with document_type
"Revised Programme" or "Programme Update".
**Look for:** The programme update referenced in the analysis —
required to verify the TIA fragnet or windows analysis.

**Signal:** The claim references an Engineer's determination or
Employer's Representative response that has not been retrieved.
**Action:** Call `get_related_documents` with document_type
"Engineer's Determination" or `search_chunks` with query
"extension of time determination awarded".
**Look for:** The determination document and the awarded EOT,
if any.

**Signal:** The Particular Conditions have not been retrieved
and the EOT clause entitlement events cannot be confirmed.
**Action:** Call `search_chunks` with query "particular conditions
extension time entitlement clause".
**Look for:** Any Particular Conditions amendment to the EOT clause.
If none found, flag that the entitlement event list could not be
confirmed from the warehouse.

---

## Always flag — regardless of query

**Flag 1 — EOT claim present but notice time-barred.**
If notice_compliance findings show a POTENTIALLY TIME-BARRED or
NON-COMPLIANT notice for this claim, flag it at the top of the
EOT assessment. State that the procedural gateway is not satisfied
and that the entitlement analysis is conditional on the notice
position being resolved.

**Flag 2 — Baseline programme absent or unaccepted.**
If no accepted/approved baseline programme is in the warehouse,
flag that the delay analysis cannot be independently verified.
State what is missing and what cannot be assessed as a result.

**Flag 3 — Concurrent delay identified but not addressed in
the claim.**
If the as-built records or programme show concurrent Contractor
delay during the claimed EOT period, flag this even if the claim
does not address it. State the period affected and the overlapping
events.

**Flag 4 — Claimed EOT exceeds demonstrated critical path impact.**
If the claimed days exceed the delay demonstrated on the critical
path in the analysis, flag the gap. State the demonstrated impact
and the claimed quantum.

**Flag 5 — Methodology not supported by available records.**
If the methodology used requires data that is absent from the
warehouse (e.g., TIA requires programme updates that are missing),
flag that the methodology cannot be verified from the available
records.

---

## Output format
```
## EOT Quantification Assessment

### Contract Basis
- FIDIC book and edition: [extracted from Legal orchestrator or retrieved]
- EOT clause: [1999 Cl. 8.4 / 2017 Cl. 8.5 — confirm from PC]
- Time for Completion: [extracted from contract documents]
- Contractual completion date: [extracted from contract or programme]
- Particular Conditions amendments to EOT clause: [list or NONE FOUND]

### Baseline Programme
- Programme status: [ACCEPTED / APPROVED / NOT ACCEPTED / NOT FOUND]
- CPM-based: [YES / NO / CANNOT DETERMINE]
- Source document: [reference]

### Delay Event Register

| # | Event description | Clause cited | Event type | CP impact | Concurrent delay | EOT claimed | Supportable |
|---|---|---|---|---|---|---|---|
| 1 | [description] | [clause] | [ER/Neutral/CR] | [YES/NO/PARTIAL] | [YES/NO] | [days] | [YES/PARTIAL/NO/CANNOT ASSESS] |

### Findings by Delay Event

**[Event description]**
Entitlement clause: [clause from Particular Conditions]
Event type: [Employer Risk / Neutral / Contractor Risk]
Notice status: [from notice_compliance findings]
Critical path impact: [demonstrated / not demonstrated / partial]
Concurrent delay: [identified / not identified] — [detail if identified]
Float position: [absorbed / exhausted / not applicable]
EOT claimed: [days]
EOT supportable: [days or CANNOT ASSESS]
Methodology: [methodology name and assessment]
Contemporaneous records: [PRESENT / PARTIAL / ABSENT]
Source documents: [list with references]
Finding: [specific conclusion with source attribution]

### Methodology Assessment
Methodology used: [name]
Data requirements met: [YES / PARTIAL / NO]
SCL Protocol compliance: [COMPLIANT / ISSUES / CANNOT ASSESS]
Finding: [specific conclusion]

### Engineer's / Employer's Representative's Position
EOT awarded: [days or NOT FOUND]
Reasons for reduction/rejection: [summary or NOT FOUND]
Source document: [reference]

### FLAGS
[Each flag on a separate line with one-sentence implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences]
```

---

## Domain knowledge and standards

### Contract-type-specific EOT provisions

| Book | Edition | EOT clause | Key entitlement events |
|---|---|---|---|
| Red Book | 1999 | Cl. 8.4 | Cl. 8.4(a)–(e): Employer variation, exceptionally adverse climatic conditions, Employer delay, unforeseeable shortages, other Employer Risk Events |
| Red Book | 2017 | Cl. 8.5 | Cl. 8.5(a)–(e): same structure, updated drafting — verify PC amendments |
| Yellow Book | 1999 | Cl. 8.4 | Same as Red Book — design risk excluded from Employer Risk Events |
| Yellow Book | 2017 | Cl. 8.5 | Same as Red Book 2017 — design risk excluded |
| Silver Book | 1999 | Cl. 8.4 | Narrower — Contractor bears most risk; Employer Risk Events limited; unforeseeable physical conditions excluded |
| Silver Book | 2017 | Cl. 8.5 | Narrower than Red/Yellow — same principle as 1999 Silver |

All entitlement event lists in this table are standard form defaults.
**Read the Particular Conditions before applying any of these.**
GCC Particular Conditions frequently remove or qualify entitlement
events — particularly exceptionally adverse weather and unforeseeable
physical conditions.

### Delay analysis methodologies — assessment criteria

**Time Impact Analysis (TIA):**
Most defensible. Insert fragnet into current programme update,
measure forward impact on completion. Data required: programme
updates at regular intervals, fragnets for each delay event.
Assessment: verify the fragnet represents the actual event, verify
the programme update used is the one current at the time of the
event, verify the critical path impact is calculated from the
insertion point forward.

**Windows Analysis:**
Preferred retrospective method for concurrent delay. Divide the
project into time windows and analyse each separately. Data required:
programme updates across the project, delay event records per window.
Assessment: verify window boundaries are logical and not manipulated
to exclude unfavourable periods, verify concurrent delay is addressed
within each window.

**Collapsed As-Built:**
Remove delay events from as-built programme, derive undelayed
completion. Data required: complete as-built programme, defined
delay events. Assessment: verify the as-built programme is based
on contemporaneous records not retrospective reconstruction, verify
the delay events removed are correctly characterised.

**As-Planned vs As-Built:**
Compare planned completion to actual completion. Data required:
baseline programme, as-built records. Assessment: lowest reliability
for complex projects — flag if used on a project with multiple
concurrent delay events; it cannot isolate causation.

**Impacted As-Planned:**
Insert delay events into baseline programme theoretically. Data
required: baseline programme only. Assessment: flag this methodology
on any complex project — it does not account for actual performance
and is routinely challenged in GCC arbitration. State the
limitation in the finding.

### SCL Protocol 2nd Edition 2017 — key principles for EOT

Float is a shared resource: absent express contractual
stipulation, float belongs to the project, not to either party.
A Contractor cannot claim an EOT for a period covered by float
unless the float has been exhausted.

Concurrent delay: where Employer-caused and Contractor-caused
delays are truly concurrent on the critical path, the Contractor
retains time entitlement but cost entitlement for the concurrent
period is uncertain and depends on the governing law and contract
terms. The GCC position generally follows the SCL Protocol.

Contemporaneous records are the foundation: a retrospective
claim without contemporaneous support is inherently weaker.
Flag the absence of contemporaneous records as a credibility
issue, not merely an evidentiary gap.

### GCC-specific practice

Primavera P6 is the de facto standard on major GCC projects.
A delay analysis not traceable to a P6 schedule faces credibility
challenges in arbitration proceedings before ICC, DIAC, ADCCAC,
SCCA, and QICCA.

UAE government projects: internal approval thresholds on
determinations mean Engineer's responses to EOT claims are
frequently delayed beyond the contractual determination period.
Under FIDIC 2017 Cl. 3.7, a failure to determine within the
prescribed period results in deemed rejection. This creates a
significant procedural risk for Contractors on UAE government
projects — flag where a determination is outstanding beyond
the contractual period.

Saudi government projects: modified FIDIC forms frequently
restrict Contractor entitlement events. Always extract from
the Particular Conditions — do not assume Red Book defaults.

Qatar: FIFA World Cup legacy projects established strong
programme records culture. Absence of P6 records on a major
Qatar project is itself a forensic signal worth flagging.
