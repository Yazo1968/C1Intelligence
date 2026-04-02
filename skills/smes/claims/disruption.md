# Disruption

**Skill type:** Contract-type-specific (entitlement basis and recoverable
heads differ by FIDIC book and edition; methodology standards are
contract-type-agnostic)
**Domain:** Claims & Disputes SME
**Invoked by:** Legal orchestrator, Commercial orchestrator

---

## When to apply this skill

Apply this skill when retrieved chunks contain a disruption claim,
a loss of productivity claim, a measured mile analysis, a labour
inefficiency claim, or a query about whether reduced productivity
is recoverable. Also apply when retrieved chunks reference
acceleration without a formal acceleration instruction — this
may indicate constructive acceleration arising from disruption.

---

## Before you begin

**Step 1 — Establish the governing contract type and entitlement basis.**
Read the Legal orchestrator findings. Extract:
- FIDIC book and edition
- The clause under which disruption is claimed — disruption is
  not expressly addressed as a standalone head in FIDIC; it is
  typically claimed under the same Employer Risk Event clauses
  as EOT and prolongation cost
- Whether the Particular Conditions amend cost recovery provisions
  for the relevant clause

**Step 2 — Distinguish disruption from prolongation.**
Disruption and prolongation are distinct heads of claim:
- Prolongation: time-related costs of being on site longer than
  planned — addressed in prolongation_cost skill
- Disruption: loss of productivity during the works — the same
  work took more resources than planned due to Employer-caused
  interference, even if no additional time resulted

A claim may include both. Assess each separately. Do not merge
the two heads.

**Step 3 — Confirm notice compliance.**
Read notice_compliance findings for the disruption claim. A
disruption claim requires the same notice compliance as any
other FIDIC claim. If notice is time-barred or absent, flag
before proceeding.

**Step 4 — Identify the productivity measurement methodology.**
This must be identified from the documents. Measured mile is
the most defensible. Global disruption is the last resort.
Identify which has been applied before assessing quantum.

---

## Analysis workflow

**Step 1 — Retrieve all disruption claim documents.**
Call `get_related_documents` with document_type "Disruption Claim".
Call `search_chunks` with query "loss of productivity disruption
measured mile labour inefficiency".
Compile all disruption claim documents and supporting analyses.

**Step 2 — Identify the disruption events.**
For each disruption event claimed:
- Identify the event and the Employer Risk Event clause cited
- Identify the period of disruption
- Identify the work activity or trade affected
- Verify the event is supported by contemporaneous records —
  instructions, RFIs, change orders, site diaries

**Step 3 — Assess the productivity measurement methodology.**

*Measured mile:*
The preferred methodology. Compares productivity in a disrupted
period to productivity in an undisrupted (baseline) period on
the same project. The baseline must be from the same project,
same trade, and comparable conditions. Assess:
- Has a genuine undisrupted baseline period been identified?
- Is the baseline truly comparable — same trade, similar work
  type, similar conditions?
- Is the productivity metric consistent (e.g., cubic metres
  per labour hour, linear metres per day)?
- Is the measured mile calculation supported by site records
  (labour returns, daily reports, quantity records)?

*Industry productivity studies (MCAA, AACE, CII):*
Reference productivity loss factors from published studies.
Acceptable as secondary or corroborating evidence but not as
primary methodology. Identify which study is cited and whether
the disruption factors applied are appropriate for the specific
conditions. These studies reflect North American or European
norms — flag where applied to GCC projects without adjustment.

*Global disruption claim:*
Total actual labour cost minus total planned labour cost without
individual causation links. Least defensible. Assess whether the
global claim threshold is satisfied — it is truly impossible to
link productivity loss to individual events, and the aggregate
is supported by records. Flag a global disruption claim where
measured mile or event-based analysis was feasible.

**Step 4 — Assess the contemporaneous records foundation.**
Disruption claims are highly dependent on contemporaneous records.
Retrieve and assess:
- Labour returns and timesheets for the disrupted periods
- Daily site diaries recording disruption events and their effect
- Quantity records showing actual vs. planned output
- Supervision records or foreman reports noting productivity issues
- Correspondence or instructions from the Engineer that caused
  the disruption

A disruption claim without contemporaneous records is forensically
weak regardless of methodology. Flag the absence of records as
a material risk.

**Step 5 — Assess causation.**
For each disruption event, causation must be established — the
Employer-caused event must be the cause of the productivity loss,
not Contractor inefficiency, learning curve effects, or weather.
Assess:
- Is there a demonstrable causal link between the Employer event
  and the productivity reduction in the relevant period?
- Does the baseline period exclude periods affected by Contractor
  inefficiency?
- Has the Contractor addressed its own contribution to any
  productivity loss?

**Step 6 — Assess the quantum.**
Compare the claimed productivity loss (expressed as additional
labour hours, additional cost, or efficiency percentage) against
the records. Verify:
- The planned productivity rate is from the original programme
  or priced bill — not retrospectively revised
- The actual productivity rate is from contemporaneous records
- The cost rate applied to the additional hours is supported
  by the contract rates or actual payroll records

**Step 7 — Check for constructive acceleration.**
Where the Contractor has been denied an EOT and accelerated to
meet the original completion date, a constructive acceleration
claim may arise. Assess whether:
- An EOT was claimed and denied or not responded to
- The Contractor gave notice of the acceleration and its cost
- Acceleration measures were implemented and are evidenced

Constructive acceleration is distinct from voluntary acceleration.
Flag where the conditions appear to be present.

---

## Classification and decision rules

**Methodology assessment:**

Measured mile with comparable baseline and contemporaneous records:
→ **MOST DEFENSIBLE** — proceed with full quantum assessment

Industry study factors applied with project-specific adjustment:
→ **CORROBORATING EVIDENCE ONLY** — flag as secondary methodology

Global disruption claim where measured mile was feasible:
→ **METHODOLOGY WEAKNESS** — flag; state why measured mile was
  feasible and the risk this creates in proceedings

Global disruption claim where measured mile was genuinely not
feasible (no undisrupted baseline period exists):
→ **ACCEPTABLE AS LAST RESORT** — flag the limitation and verify
  the aggregate is supported by records

**Causation assessment:**

Clear causal link between Employer event and productivity loss
evidenced in contemporaneous records:
→ **CAUSATION ESTABLISHED** — proceed with quantum

Productivity loss present but causal link to specific Employer
event not established:
→ **CAUSATION NOT ESTABLISHED** — flag; state what evidence
  would be needed to establish causation

Mixed causation — both Employer events and Contractor factors
contributed to productivity loss:
→ **CAUSATION PARTIAL** — flag; state the mixed causation
  and note that apportionment will be required

**Constructive acceleration:**

EOT denied or not responded to + Contractor accelerated +
contemporaneous records of acceleration measures:
→ **POSSIBLE CONSTRUCTIVE ACCELERATION** — flag and state
  the elements present and absent

---

## When to call tools

**Signal:** Disruption claim references specific Employer
instructions or RFIs as the cause but these have not been
retrieved.
**Action:** Call `search_chunks` with query "[instruction or RFI
reference] [date range]" and call `get_related_documents` with
document_type "Engineer's Instruction" or "RFI".
**Look for:** The instruction or RFI cited as the disruption
cause — verify it exists and predates the claimed disruption period.

**Signal:** Measured mile analysis references a baseline period
but no site records for that period have been retrieved.
**Action:** Call `get_related_documents` with document_type
"Site Diary" or "Daily Report" for the baseline period dates.
Call `search_chunks` with query "labour return productivity
[baseline period dates]".
**Look for:** Labour returns, quantity records, or daily reports
covering the baseline period to verify the undisrupted productivity
rate.

**Signal:** The claim references industry productivity studies
but does not identify the specific study or factors used.
**Action:** Call `search_chunks` with query "productivity factor
MCAA AACE CII inefficiency table".
**Look for:** The specific study reference and the factors applied.

**Signal:** Acceleration costs are claimed but no acceleration
instruction has been retrieved.
**Action:** Call `search_chunks` with query "acceleration
instruction directed accelerate completion".
Call `get_related_documents` with document_type "Engineer's
Instruction".
**Look for:** A formal acceleration instruction — if absent,
assess whether constructive acceleration conditions are present.

---

## Always flag — regardless of query

**Flag 1 — Disruption claim without contemporaneous records.**
If no contemporaneous records (labour returns, daily reports,
quantity records) have been found to support the productivity
measurement, flag this as a material evidential risk. State
what records are absent.

**Flag 2 — Global disruption where measured mile was feasible.**
If the claim is presented as a global disruption claim but the
warehouse contains records from both disrupted and undisrupted
periods that would support a measured mile, flag the methodology
choice as a weakness and state the available records.

**Flag 3 — Industry study factors applied without GCC adjustment.**
If the claim applies MCAA, AACE, or CII productivity loss factors
without adjustment for GCC conditions, flag this. These studies
reflect North American and European norms — GCC tribunals treat
unadjusted factors with scepticism.

**Flag 4 — Causation not established for a material head.**
If a head of disruption claim lacks a demonstrable causal link
to a specific Employer event, flag this and state what evidence
would be required.

**Flag 5 — Possible constructive acceleration.**
If the conditions for constructive acceleration are present
(denied EOT + acceleration without instruction + evidence of
acceleration measures), flag this as a separate potential head
of claim that may require its own notice and quantum assessment.

---

## Output format
```
## Disruption Assessment

### Entitlement Basis
- FIDIC book and edition: [extracted]
- Applicable clause: [from Particular Conditions]
- Notice compliance: [from notice_compliance findings]

### Disruption Event Register

| # | Event | Period | Activity affected | Methodology | Causation | Records |
|---|---|---|---|---|---|---|
| 1 | [description] | [dates] | [trade/activity] | [methodology] | [ESTABLISHED/PARTIAL/NOT ESTABLISHED] | [PRESENT/PARTIAL/ABSENT] |

### Findings by Disruption Event

**[Event description]**
Period: [dates]
Activity affected: [trade or activity]
Employer event: [instruction, RFI, or event cited]
Methodology: [measured mile / industry study / global]
Baseline: [undisrupted period and source, or NOT IDENTIFIED]
Productivity metric: [unit of measurement]
Planned rate: [rate and source]
Actual rate: [rate and source]
Productivity loss: [percentage or hours]
Causation: [ESTABLISHED / PARTIAL / NOT ESTABLISHED]
Contemporaneous records: [PRESENT / PARTIAL / ABSENT — list documents]
Quantum claimed: [amount]
Quantum supportable: [amount or CANNOT ASSESS]
Finding: [specific conclusion with source attribution]

### Constructive Acceleration
[Assessment of constructive acceleration conditions, or NOT APPLICABLE]

### Overall Quantum
Total disruption claimed: [amount]
Total supportable: [amount or CANNOT ASSESS]
Methodology assessment: [summary]

### FLAGS
[Each flag with one-sentence implication]

### Overall Assessment
Confidence: [GREEN / AMBER / RED / GREY]
Summary: [two to three sentences]
```

---

## Domain knowledge and standards

### Contract-type-agnostic principles

Disruption is the loss of efficiency or productivity caused by
interference with the planned method and sequence of work. It
is distinct from delay — disruption may occur without any
extension to the completion date if the Contractor absorbs the
impact through additional resources rather than additional time.

FIDIC does not expressly provide for disruption as a standalone
head. Disruption costs are claimed under the same Employer Risk
Event clauses that support EOT — the Contractor must demonstrate
that the Employer Risk Event caused the loss of productivity.
The entitlement basis is therefore the same as for any other
cost claim — verify the applicable clause from the Particular
Conditions.

Causation is the critical issue in disruption claims. It is not
sufficient to show that productivity was reduced during a period
when Employer events occurred. The Contractor must demonstrate
that the Employer events caused the productivity loss, not that
the two simply coincided. This distinction is consistently
applied by GCC arbitration tribunals.

### Measured mile methodology — key requirements

The baseline period must be genuinely undisrupted — periods
affected by weather, Contractor learning curve, mobilisation,
or demobilisation are not valid baselines. If no undisrupted
period exists on the project, the measured mile cannot be applied
and the claim must use an alternative methodology with appropriate
disclosure of its limitations.

The comparison must be like-for-like — same trade, same work
type, comparable site conditions. A baseline from structural
concrete works cannot be used to measure productivity loss on
MEP installation.

The productivity metric must be consistent and objectively
measurable — labour hours per unit of output is the most
defensible metric. Cost per unit is acceptable where labour
hours are not separately recorded.

The records foundation is essential — the measured mile is only
as reliable as the records underlying it. Labour returns,
quantity records, and daily reports must cover both the baseline
and disrupted periods.

### SCL Protocol 2nd Edition 2017 — disruption principles

The SCL Protocol addresses disruption in its guidance notes.
Key principles: contemporaneous records are essential; the
measured mile is the preferred methodology; global claims for
disruption are treated with caution and require the Contractor
to demonstrate it was impossible to link individual causes to
individual effects.

The Protocol also notes that industry productivity studies are
not a substitute for project-specific evidence — they may
corroborate but should not replace actual records.

### GCC-specific practice

UAE and Qatar: labour productivity on GCC projects is affected
by factors not present in North American or European studies —
extreme summer heat (mandatory rest periods June-September
in the UAE), high labour turnover rates, mixed-nationality
workforces with supervision and communication challenges,
and Ramadan working patterns. A measured mile analysis that
does not account for these project-specific factors risks
challenge. Industry study factors that do not reflect GCC
conditions should be flagged as unadjusted.

Saudi Arabia: extreme heat and dust conditions, prayer time
breaks, and Friday/Saturday weekend patterns affect productivity
baselines. Summer working hour restrictions apply on major
government projects.

Qatar: FIFA World Cup legacy projects had strong daily
productivity reporting requirements. The absence of productivity
records on a major Qatar project is a forensic signal —
records almost certainly existed and their absence may
indicate selective disclosure.

Ramadan: productivity reduction during Ramadan is a recurring
issue across all GCC jurisdictions. A disruption claim that
includes Ramadan periods without separating the Ramadan
productivity baseline from the standard baseline will face
challenge — Ramadan working patterns should be treated as
a known and planned-for condition unless the contract
specifically addresses it otherwise.
