# Delay Identification

**Skill type:** Contract-type-specific
The classification of delay events as Employer Risk Events, Neutral
Events, or Contractor Risk Events depends on the entitlement event
list in the retrieved Particular Conditions — which differs by FIDIC
book and edition. The analysis framework for identifying delay events
is contract-type-agnostic.
**Layer dependency:**
- Layer 1 — project documents: programme updates; as-built programme;
  site diaries and daily reports; progress reports; instructions,
  RFIs, and correspondence that caused or evidenced delays;
  Particular Conditions (EOT clause, entitlement event list)
- Layer 2 — reference standards: FIDIC EOT clause (8.4/8.5) for the
  confirmed book and edition; SCL Protocol 2nd Edition 2017 (delay
  event classification principles)
**Domain:** Schedule & Programme SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply when a query requires identification of delay events on a
project, classification of those events by responsibility, or
assessment of whether specific delay events qualify for EOT
entitlement. Apply as the foundational step before
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
- Confirmed FIDIC book and edition
- Particular Conditions amendments to the EOT clause and entitlement
  event list

**If no baseline programme has been retrieved:** Delay events can
still be identified from contemporaneous records, but their critical
path impact cannot be assessed. Flag this dependency.

**If the Particular Conditions have not been retrieved:**
State CANNOT CLASSIFY delay events as Employer Risk Events,
Neutral Events, or Contractor Risk Events. The entitlement event
list is in the Particular Conditions — not the General Conditions
defaults.

### Layer 1 documents to retrieve (project-specific)

Call `search_chunks` and `get_related_documents` to retrieve:
- Programme updates for the full project duration (or the period
  under analysis)
- As-built programme (if available)
- Site diaries and daily reports — the primary contemporaneous
  record of delay events
- Monthly progress reports — record delay events and their causes
- Engineer's Instructions — potential Employer-caused delay triggers
- Notices of delay issued by the Contractor
- RFI logs and responses — delayed responses may constitute
  Employer-caused delay
- Weather records (where weather delays are claimed)
- Correspondence recording access problems, late information,
  or Employer instructions
- The Particular Conditions — EOT clause and entitlement event list

**For each delay event identified:** the evidence must come from
retrieved documents. Do not identify delay events from the claim
submission alone without corroborating contemporaneous records.

**If contemporaneous records (site diaries, progress reports) have
not been retrieved for the delay period:**
State that delay events during this period have not been
independently verified from contemporaneous warehouse documents.

### Layer 2 documents to retrieve (reference standards)

Call `search_chunks` to retrieve from Layer 2:
- FIDIC Clause 8.4 (1999) or Clause 8.5 (2017) for the confirmed
  book — the qualifying entitlement events list
- SCL Protocol 2nd Edition 2017 — delay event classification
  principles, excusable vs compensable delay

**Purpose:** To establish the standard FIDIC entitlement events
as the comparison baseline. The actual list to apply is always
the retrieved Particular Conditions version.

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

From the retrieved Particular Conditions, confirm the entitlement
event list under the EOT clause (Clause 8.4/8.5 or equivalent
as amended).

**Do not apply the General Conditions entitlement event list
without confirming from the retrieved Particular Conditions
that it has not been amended.** Key differences between books
that affect classification:

**Red Book:**
Employer Risk Events include: variations, exceptionally adverse
climatic conditions, Employer delays, unforeseeable shortages,
unforeseeable physical conditions (Clause 4.12). Retrieve and
apply the PC version.

**Yellow Book:**
Same as Red Book except: Contractor bears design risk — design
errors are not Employer Risk Events. Retrieve and apply the PC
version.

**Silver Book:**
Narrower Employer Risk Event list. Unforeseeable physical
conditions are generally NOT an Employer Risk Event under the
Silver Book standard form. Retrieve and apply the PC version —
the PC may further restrict or expand the standard list.

If the Particular Conditions have not been retrieved: state
CANNOT CLASSIFY delay events by entitlement category.

### Step 3 — Classify each delay event
*Contract-type-specific*

For each identified delay event, classify as:

**Employer Risk Event:** The event falls within the entitlement
events as stated in the retrieved Particular Conditions and the
Employer (or Engineer/ERA acting on Employer instructions) caused
or is responsible for it. Cite the specific retrieved PC provision.

**Neutral Event:** The event is listed in the retrieved PC as
entitling the Contractor to EOT but not Cost (e.g. exceptionally
adverse climatic conditions where listed as neutral). Cite the
retrieved PC provision.

**Contractor Risk Event:** The event is caused by or falls within
the Contractor's risk under the retrieved contract.

**CANNOT CLASSIFY:** The event type cannot be determined because
the Particular Conditions have not been retrieved, or the
evidence does not allow classification.

**Do not classify any event without a retrieved PC provision
to support the classification.**

### Step 4 — Assess excusable vs compensable distinction
*Contract-type-agnostic principle / contract-type-specific application*

Under the SCL Protocol framework (Layer 2):

Excusable delay: entitles the Contractor to EOT but not Cost.
Compensable delay: entitles the Contractor to both EOT and Cost.

Map this framework against the retrieved Particular Conditions
classification — the PC terms govern what is excusable and what
is compensable for this project. Do not apply the SCL terminology
without confirming the PC entitlement terms.

### Step 5 — Assess weather and force majeure events
*Contract-type-specific*

**Exceptionally adverse climatic conditions:**
This is a qualifying event under the standard FIDIC EOT clause
(all books, both editions). However:
- The standard is "exceptionally adverse" — not simply adverse
  or inconvenient weather
- Whether conditions are "exceptional" must be assessed against
  the historical weather data for the location, which is typically
  not in the warehouse — flag that exceptionality cannot be
  confirmed without meteorological data not in the warehouse

**Force majeure / Exceptional events:**
Under FIDIC 2017, force majeure is replaced by "Exceptional Events"
(Clause 18). The events listed differ between editions. Identify
from the retrieved Particular Conditions whether any exceptional
event clause has been amended. Classify from retrieved documents.

### Step 6 — Assess Employer-caused delay patterns
*Contract-type-agnostic*

From the retrieved documents, identify whether there are patterns
of Employer-caused delay:
- Late information or late drawings from the Engineer (Red/Yellow)
  or Employer (Silver)
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
record → NOT INDEPENDENTLY VERIFIED — flag; state which records
were retrieved and which were not
Event in neither the claim nor contemporaneous records →
NOT IDENTIFIED IN RETRIEVED DOCUMENTS

**Delay event classification:**

Event falls within retrieved PC entitlement event list →
EMPLOYER RISK EVENT (EOT + Cost entitlement) or NEUTRAL EVENT
(EOT only) — cite specific PC provision
Event does not fall within retrieved PC entitlement event list →
CONTRACTOR RISK EVENT — cite specific PC provision that excludes it
Classification cannot be determined (PC not retrieved) →
CANNOT CLASSIFY

**Weather:**

Exceptionally adverse: CANNOT CONFIRM exceptionality without
meteorological comparison data — flag; state that the event
is recorded in retrieved documents but its qualifying status
cannot be determined from warehouse documents alone

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
"Request for Information"; `search_chunks` with query "RFI request
information response outstanding"
**Look for:** RFI register with issue dates, response dates, and
any outstanding RFIs

**Signal:** Late access claimed but no access records retrieved
**Action:** `search_chunks` with query "site access possession
Employer late access"; `get_related_documents` with document
types "Site Diary", "Correspondence"
**Look for:** Documents recording actual access dates vs planned
access dates

**Signal:** PC not retrieved — entitlement event list unconfirmed
**Action:** `search_chunks` with query "particular conditions
clause 8 EOT entitlement event extension time"; `get_document`
on PC document ID if known
**Look for:** The entitlement event list in the PC EOT clause

---

## Always flag — regardless of query

1. **Delay events in the claim not evidenced in retrieved
   contemporaneous records** — flag each; state that independent
   verification is not possible from warehouse documents.

2. **Silver Book: delay event that would be an Employer Risk Event
   under Red Book but is a Contractor risk under Silver Book** —
   flag the book-specific risk allocation; cite the retrieved PC
   provision.

3. **Weather delay claimed but exceptionality cannot be confirmed
   from warehouse documents** — flag; state that meteorological
   comparison data would be needed.

4. **Pattern of late RFI responses or late information from
   Engineer/Employer** — flag the pattern with specific references
   from retrieved documents.

5. **Particular Conditions not retrieved — entitlement event list
   unconfirmed** — flag; state that no delay event can be classified
   for entitlement purposes.

---

## Output format

```
## Delay Identification Assessment

### Documents Retrieved (Layer 1)
[List every document retrieved with reference numbers and dates.]

### Documents Not Retrieved
[List every document required but not found. State which steps
are affected.]

### Layer 2 Reference Retrieved
[State whether FIDIC EOT clause and SCL Protocol were retrieved.
If not: state analytical knowledge applied.]

### Entitlement Event List Confirmed
Source: [PC reference / CANNOT CONFIRM — PC not retrieved]
Amendments to standard FIDIC list: [list or NONE FOUND / CANNOT CONFIRM]

### Delay Event Register

| # | Event description | Period | Duration | Contemporaneous evidence | Classification | Entitlement | Source |
|---|---|---|---|---|---|---|---|
| 1 | [description] | [dates] | [days] | [EVIDENCED / NOT VERIFIED] | [ER/Neutral/CR/CANNOT CLASSIFY] | [EOT+Cost / EOT only / Nil / CANNOT CONFIRM] | [docs] |

### Findings by Delay Event

**[Event description]**
Period: [dates]
Duration: [days — from retrieved records / CANNOT CONFIRM]
Contemporaneous evidence: [EVIDENCED — source documents /
NOT INDEPENDENTLY VERIFIED — records not in warehouse]
Classification: [EMPLOYER RISK EVENT / NEUTRAL EVENT /
CONTRACTOR RISK EVENT / CANNOT CLASSIFY]
Classification basis: [retrieved PC provision / CANNOT CONFIRM — PC not retrieved]
Entitlement: [EOT + Cost / EOT only / No entitlement / CANNOT CONFIRM]
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
Particular Conditions.*

**FIDIC delay event categories — analytical reference:**
FIDIC distinguishes between events that entitle the Contractor to
EOT and Cost (Employer Risk Events), events that entitle EOT only
(Neutral Events), and events that are at the Contractor's risk.
The specific events in each category differ by book — the Red Book
has the broadest Employer Risk Event list; the Silver Book has the
narrowest. Both editions contain the same structural categories
but differ in drafting and numbering. The actual list for any
project is in the retrieved Particular Conditions. Retrieve from
Layer 2 for the standard text and from Layer 1 for the project-
specific version.

**SCL Protocol delay classification — analytical reference:**
The SCL Protocol uses the terms "excusable" (EOT entitlement)
and "compensable" (EOT + Cost entitlement). A delay that is
excusable but not compensable entitles the Contractor to time
but not money. These map onto the FIDIC Neutral Event and Employer
Risk Event categories but use different terminology. Apply the
FIDIC terminology from the retrieved contract — not the SCL terms.

**Concurrent delay — analytical reference:**
Where Employer-caused and Contractor-caused delays overlap on the
critical path in the same period, the concurrent delay principles
apply. Under the SCL Protocol, the Contractor retains time
entitlement for the concurrent period but cost entitlement is
less certain. The concurrent period is determined from the
retrieved programme records — not from the claim submission.
