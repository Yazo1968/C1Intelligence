# Delay Identification

**Skill type:** Contract-type-specific
The classification of delay events as employer risk events, neutral
events, or contractor risk events depends on the entitlement event
list in the retrieved amendment document — which differs by standard
form and version. The analysis framework for identifying delay events
is contract-type-agnostic.
**Layer dependency:**
- Layer 1 — project documents: programme updates; as-built programme;
  site diaries and daily reports; progress reports; instructions, RFIs,
  and correspondence that caused or evidenced delays; amendment document
  (time extension clause, entitlement event list)
- Layer 2b — reference standards: time extension provision for the
  confirmed standard form and version (whatever is in the warehouse);
  SCL Protocol 2nd Edition 2017 (delay event classification principles,
  if ingested)
**Domain:** Schedule & Programme SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when a query requires identification of delay events on a
project, classification of those events by responsibility, or
assessment of whether specific delay events qualify for time
extension entitlement. Apply as the foundational step before
eot_quantification — delay events must be identified and classified
before their critical path impact is quantified.

---

## Before you begin

### Foundational requirements

Read programme_assessment and critical_path_analysis findings first.

From programme_assessment:
- Whether a valid baseline programme is in the warehouse
- The contractual completion date as confirmed from retrieved
  Contract Data

From critical_path_analysis:
- Which activities are on the critical path
- Float position and ownership

From the invoking orchestrator:
- Confirmed standard form and version
- Amendment document provisions affecting the time extension clause
  and entitlement event list

**If no baseline programme has been retrieved:** Delay events can
still be identified from contemporaneous records, but their critical
path impact cannot be assessed. Flag this dependency.

**If the amendment document has not been retrieved:**
State CANNOT CLASSIFY delay events as employer risk events, neutral
events, or contractor risk events. The entitlement event list is in
the amendment document.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- Programme updates for the full project duration (or the period
  under analysis)
- As-built programme (if available)
- Site diaries and daily reports — the primary contemporaneous
  record of delay events
- Monthly progress reports — record delay events and their causes
- Contract administrator instructions — potential employer-caused
  delay triggers
- Notices of delay issued by the Contractor
- RFI logs and responses — delayed responses may constitute
  employer-caused delay
- Weather records (where weather delays are claimed)
- Correspondence recording access problems, late information, or
  employer instructions
- The amendment document — time extension clause and entitlement
  event list

**For each delay event identified:** the evidence must come from
retrieved documents. Do not identify delay events from the claim
submission alone without corroborating contemporaneous records.

**If contemporaneous records (site diaries, progress reports) have
not been retrieved for the delay period:**
State that delay events during this period have not been
independently verified from contemporaneous warehouse documents.

### Layer 2b documents to retrieve (reference standards)

Call `search_chunks` with `layer_type = '2b'` to retrieve:
- Time extension entitlement event provision for the confirmed
  standard form (search by subject matter: "time extension
  entitlement employer risk event qualifying event")
- SCL Protocol 2nd Edition 2017 — delay event classification
  principles (search by subject matter: "SCL Protocol excusable
  compensable delay classification")

**Purpose:** To establish the standard form entitlement events as
the comparison baseline. The actual list to apply is always the
retrieved amendment document version.

**If the governing standard form is not retrieved from Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT IN WAREHOUSE for the
entitlement event provisions. Do not characterise the standard
event list from training knowledge.

---

## Analysis workflow

### Step 1 — Identify all delay events from retrieved documents
*Contract-type-agnostic*

From the retrieved contemporaneous records (site diaries, progress
reports, programme updates, correspondence, instructions):
- Compile a list of all delay events recorded in the retrieved
  documents during the period under analysis
- For each event: state the date, duration, and source document(s)
- Note events recorded in the claim submission that are NOT
  evidenced in retrieved contemporaneous records — flag each as
  NOT INDEPENDENTLY VERIFIED FROM CONTEMPORANEOUS RECORDS

### Step 2 — Confirm the entitlement event list
*Contract-type-specific*

From the retrieved amendment document, confirm the entitlement
event list under the time extension provision (as amended).

Retrieve the standard form provision from Layer 2b to establish
the baseline. Then apply the amendment document version — the
amendment document governs.

**Do not apply any entitlement event list without retrieving it
from the amendment document.** The list differs materially between
standard forms and between versions:
- Some forms allocate physical conditions risk to the employer
- Others allocate it to the contractor
- Design risk allocation differs by contract type
- The scope of force majeure or exceptional events varies

Retrieve from Layer 2b for the standard form baseline and from
Layer 1 for the project-specific version. If the amendment document
has not been retrieved: state CANNOT CLASSIFY delay events by
entitlement category.

### Step 3 — Classify each delay event
*Contract-type-specific*

For each identified delay event, classify as:

**Employer Risk Event:** The event falls within the entitlement
events as stated in the retrieved amendment document and the
employer (or contract administrator acting on employer instructions)
caused or is responsible for it. Cite the specific retrieved
amendment provision.

**Neutral Event:** The event is listed in the retrieved amendment
document as entitling the Contractor to a time extension but not
cost (e.g. exceptionally adverse climatic conditions where listed
as neutral). Cite the retrieved provision.

**Contractor Risk Event:** The event is caused by or falls within
the Contractor's risk under the retrieved contract.

**CANNOT CLASSIFY:** The event type cannot be determined because
the amendment document has not been retrieved, or the evidence
does not allow classification.

**Do not classify any event without a retrieved amendment provision
to support the classification.**

### Step 4 — Assess excusable vs compensable distinction
*Contract-type-agnostic principle / contract-type-specific application*

Retrieve the SCL Protocol from Layer 2b if available. Map the
excusable/compensable framework against the retrieved amendment
document classification — the amendment document terms govern what
is excusable and what is compensable for this project.

Excusable delay: entitles the Contractor to a time extension but
not cost.
Compensable delay: entitles the Contractor to both time and cost.

Do not apply SCL terminology without confirming the amendment
document entitlement terms.

### Step 5 — Assess weather and force majeure events
*Contract-type-specific*

**Adverse weather or climatic conditions:**
Retrieve the applicable provision from the amendment document and
from Layer 2b. The standard for qualifying weather events varies
by standard form (e.g. "exceptionally adverse" is a common
threshold). Assess against the retrieved provision.

For weather events: the qualifying status must be assessed against
historical weather data for the location, which is typically not
in the warehouse — flag that exceptionality cannot be confirmed
without meteorological comparison data.

**Force majeure or exceptional events:**
Retrieve the applicable provision from the amendment document and
from Layer 2b. Identify what events are listed and whether the
amendment document modifies the standard form provision. Classify
from retrieved documents only.

### Step 6 — Assess employer-caused delay patterns
*Contract-type-agnostic*

From the retrieved documents, identify whether there are patterns
of employer-caused delay:
- Late information or late drawings from the contract administrator
  or employer
- Delayed RFI responses — compare RFI issue dates against response
  dates from retrieved RFI logs
- Access restrictions — compare programme access dates against
  actual access dates from retrieved site records
- Late instructions requiring out-of-sequence working

**Identify patterns only from retrieved documents.** Do not
characterise a pattern without multiple retrieved records
evidencing it.

---

## Classification and decision rules

**Delay event identification:**

Event recorded in contemporaneous records (site diary, progress
report, correspondence) → EVIDENCED — state sources
Event in claim submission but not in any retrieved contemporaneous
record → NOT INDEPENDENTLY VERIFIED — flag
Event in neither claim nor contemporaneous records →
NOT IDENTIFIED IN RETRIEVED DOCUMENTS

**Delay event classification:**

Event falls within retrieved amendment document entitlement event
list → EMPLOYER RISK EVENT (time + cost) or NEUTRAL EVENT
(time only) — cite specific amendment provision
Event does not fall within retrieved amendment document entitlement
event list → CONTRACTOR RISK EVENT — cite specific provision
Classification cannot be determined (amendment document not
retrieved) → CANNOT CLASSIFY

**Weather:**

Weather event recorded in retrieved documents → EVIDENCED —
qualifying status (exceptionally adverse or equivalent standard)
CANNOT CONFIRM without meteorological comparison data — flag

---

## When to call tools

**Signal:** Delay event referenced in claim but no contemporaneous
record retrieved for the event period
**Action:** `search_chunks` with query "[event description]
[date range]"; `get_related_documents` with document types
"Site Diary", "Daily Report", "Progress Report"
**Look for:** Any contemporaneous record independently evidencing
the delay event

**Signal:** RFI delays claimed but no RFI log retrieved
**Action:** `get_related_documents` with document type "RFI Log",
"Request for Information"; `search_chunks` with query "RFI
request information response outstanding"
**Look for:** RFI register with issue dates, response dates

**Signal:** Late access claimed but no access records retrieved
**Action:** `search_chunks` with query "site access possession
employer late access"; `get_related_documents` with document
types "Site Diary", "Correspondence"
**Look for:** Documents recording actual access dates vs planned
access dates

**Signal:** Amendment document not retrieved — entitlement event
list unconfirmed
**Action:** `search_chunks` with query "particular conditions time
extension entitlement event"; `get_document` on amendment
document ID if known
**Look for:** The entitlement event list in the amendment document

---

## Always flag — regardless of query

1. **Delay events in the claim not evidenced in retrieved
   contemporaneous records** — flag each; state that independent
   verification is not possible from warehouse documents.

2. **Risk allocation differs by standard form** — always retrieve
   and confirm the entitlement event list from the amendment document
   before classifying any event; flag if standard form not retrieved.

3. **Weather delay claimed but qualifying status cannot be confirmed
   from warehouse documents** — flag; state that meteorological
   comparison data would be needed.

4. **Pattern of late RFI responses or late information** — flag
   the pattern with specific references from retrieved documents.

5. **Amendment document not retrieved — entitlement event list
   unconfirmed** — flag; state that no delay event can be classified
   for entitlement purposes.

6. **Governing standard not retrieved from Layer 2b** — flag when
   the time extension provision could not be retrieved; state what
   standard would need to be ingested.

---

## Output format

```
## Delay Identification Assessment

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
[State whether the time extension provision and SCL Protocol were
retrieved from Layer 2b. If not: state CANNOT CONFIRM —
STANDARD FORM NOT IN WAREHOUSE and list which analysis steps
are affected.]

### Entitlement Event List Confirmed
Source: [amendment document reference / CANNOT CONFIRM — not retrieved]
Amendments to standard form list: [list or NONE FOUND / CANNOT CONFIRM]

### Delay Event Register

| # | Event description | Period | Duration | Contemporaneous evidence | Classification | Entitlement | Source |
|---|---|---|---|---|---|---|---|
| 1 | [description] | [dates] | [days] | [EVIDENCED / NOT VERIFIED] | [ER/Neutral/CR/CANNOT CLASSIFY] | [Time+Cost / Time only / Nil / CANNOT CONFIRM] | [docs] |

### Findings by Delay Event

**[Event description]**
Period: [dates]
Duration: [days — from retrieved records / CANNOT CONFIRM]
Contemporaneous evidence: [EVIDENCED — source documents /
NOT INDEPENDENTLY VERIFIED — records not in warehouse]
Classification: [EMPLOYER RISK EVENT / NEUTRAL EVENT /
CONTRACTOR RISK EVENT / CANNOT CLASSIFY]
Classification basis: [retrieved amendment provision / CANNOT CONFIRM]
Entitlement: [Time + Cost / Time only / No entitlement / CANNOT CONFIRM]
Critical path impact: [from critical_path_analysis findings /
CANNOT ASSESS — programme not available]
Finding: [from retrieved documents only]

### Employer-Caused Delay Patterns
[Pattern identified with specific document references, or
NO PATTERN IDENTIFIED FROM RETRIEVED DOCUMENTS]

### FLAGS
[Each flag with one-sentence forensic implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences — facts from retrieved documents only]
```

---

## Analytical framework
*Reference only — do not classify any delay event without first
confirming the applicable entitlement event list from the retrieved
amendment document.*

**Delay event categories — analytical reference:**
Standard forms of contract distinguish between events that entitle
the Contractor to a time extension and cost, events that entitle
time only, and events that are at the Contractor's risk. The
specific events in each category differ by standard form — some
forms have a broader employer risk event list; others are more
restrictive. Both the standard form and the amendment document
must be retrieved before any event can be classified. Retrieve
from Layer 2b for the standard text and from Layer 1 for the
project-specific version.

**SCL Protocol delay classification — analytical reference:**
The SCL Protocol uses the terms "excusable" (time entitlement)
and "compensable" (time and cost entitlement). These map onto
the neutral event and employer risk event categories in many
standard forms. Apply the terminology from the retrieved contract
— not the SCL terms — when classifying delay events.

**Concurrent delay — analytical reference:**
Where employer-caused and contractor-caused delays overlap on the
critical path in the same period, concurrent delay principles apply.
The concurrent period is determined from the retrieved programme
records — not from the claim submission.
