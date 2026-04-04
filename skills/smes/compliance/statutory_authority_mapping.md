# Statutory Authority Mapping

**Skill type:** Contract-type-agnostic for the identification and mapping
logic; contract-type-specific for which party bears statutory compliance
obligations
- The identification of statutory authorities with jurisdiction over a
  project and the mapping of required interactions to project milestones
  applies regardless of the standard form in use
- Which contractual party (Employer, Contractor, or Engineer/PMC) bears
  the obligation to obtain a specific approval is contract-type-specific
  and retrieved from Layer 2b

**Layer dependency:**
- Layer 1 — project documents: the construction contract (statutory
  compliance provisions), correspondence with statutory authorities,
  permits, NOCs, approvals, inspection certificates, programme and
  milestone documents referencing regulatory hold points
- Layer 2a — internal documents: internal procedures or checklists
  referencing statutory approvals or permit requirements (if ingested)
- Layer 2b — reference standards: governing contract standard — provisions
  placing statutory compliance obligations on the Contractor, Employer,
  or Engineer/PMC; any statutory framework applicable to the project
  jurisdiction (if ingested)

**Domain:** Compliance SME

**Invoked by:** Legal & Compliance Orchestrator (primary); also invoked
as part of governance establishment (Step 5 — statutory authority
identification)

---

## When to apply this skill

Apply when a query asks whether required statutory approvals, permits, or
NOCs have been obtained and documented for this project. Apply when
establishing the full governance structure to identify all authority
sources — statutory authorities are a distinct category from contractual
parties. Apply when a project milestone is in question and a statutory
hold point may be relevant.

This skill does not assess the internal governance or authority structure
of statutory bodies — their authority derives from legislation and is not
contestable. The questions for this skill are: which authorities have
jurisdiction, what interactions are required, and are those interactions
documented in the warehouse.

---

## Before you begin

### Layer 1 documents to retrieve

Call `search_chunks` using the following query terms across all ingested
project documents:

- "permit", "building permit", "approval", "approved"
- "NOC", "no objection", "no objection certificate"
- "municipality", "municipal", "authority", "regulatory"
- "inspection", "inspection certificate", "hold point"
- "civil defence", "fire authority", "utilities"
- "traffic department", "road authority"
- "planning", "planning approval", "planning permission"
- "completion certificate", "occupancy certificate", "occupancy permit"
- "environmental", "environmental approval"
- "statutory", "statutory authority", "government"
- "licence", "licensed"

Also retrieve:
- The construction contract — clauses placing statutory compliance
  obligations on any party
- The project programme or milestone schedule — for regulatory hold
  points and milestone-linked approvals
- Any correspondence with statutory authorities ingested in the warehouse

**If the construction contract is not retrieved:**
State CANNOT CONFIRM — CONSTRUCTION CONTRACT NOT RETRIEVED. The party
bearing each statutory obligation cannot be confirmed.

### Layer 2a documents to retrieve

Call `search_chunks` with `layer_type = '2a'` to retrieve:
- Any internal procedures referencing statutory approval requirements
- Internal project governance frameworks that include regulatory
  compliance checkpoints

**If Layer 2a is not retrieved:**
Note the absence. Proceed with Layer 1 and Layer 2b only. State that
internal procedures for statutory compliance have not been retrieved.

### Layer 2b documents to retrieve

Call `search_chunks` with `layer_type = '2b'` to retrieve:
- Governing contract standard provisions on statutory compliance —
  which party is responsible for obtaining permits, licences, and
  approvals
- Any statutory framework or regulatory document ingested in the
  warehouse for this project's jurisdiction

Query format: search by subject matter — "statutory obligations
Contractor permits" or "compliance with laws regulations" — not by
clause number.

**If the governing standard is not in Layer 2b:**
State CANNOT CONFIRM — STANDARD FORM NOT RETRIEVED. The contractual
party bearing each statutory obligation cannot be confirmed from the
standard form. Identification of required interactions proceeds from
Layer 1 documents only.

---

## Analysis workflow

### Step 1 — Retrieve across all three layers

Execute the retrieval instructions above. Record what was retrieved.
Do not proceed until retrieval is complete.

### Step 2 — Identify statutory authorities

From all retrieved documents, identify every entity that:
- Is referenced as a government body, municipality, or regulatory authority
- Issues permits, NOCs, approvals, or inspection certificates
- Has jurisdiction over any aspect of the project (planning, building,
  civil defence, utilities, traffic, environmental, health and safety,
  or any other regulatory domain)

For each identified authority record:
- Authority name exactly as it appears in retrieved documents
- Jurisdiction scope — what aspect of the project it regulates
- Identification basis: confirmed (explicitly named in retrieved document
  as having issued or being required to issue an approval) or inferred
  (referenced indirectly without a retrieved approval or correspondence)

### Step 3 — Map required interactions

For each identified statutory authority, establish from retrieved documents:
- Type of interaction: permit / NOC / approval / inspection / completion
  certificate / occupancy certificate / other
- Project milestone or activity to which it relates (from retrieved
  programme or contract provisions)
- Which party bears the obligation (from retrieved contract provisions
  and Layer 2b standard form)
- Whether the interaction is a hold point (work cannot proceed without it)
  or a notification / submission

### Step 4 — Assess evidence in the warehouse

For each required interaction, assess whether the relevant document is
present in the retrieved warehouse content:
- Retrieved: the permit, NOC, approval, correspondence, or certificate
  is in the warehouse and has been retrieved
- Not retrieved: no document evidencing this interaction has been retrieved
  from the warehouse
- Partial: correspondence is retrieved but the approval outcome is not,
  or the document appears incomplete

**Note:** "Not retrieved" means the document was not found in the
warehouse. It does not mean the approval was not obtained — the document
may exist but not have been ingested. This distinction must be stated
explicitly in the output.

### Step 5 — Identify gaps

List every required interaction for which no evidencing document has been
retrieved. For each gap state:
- Authority name
- Interaction type
- Project milestone affected
- Party bearing the obligation
- Whether the gap is a missing document (not ingested) or a missing
  interaction (no evidence of the interaction in any retrieved document)

---

## Classification and decision rules

**Confirmed statutory authority:** Named explicitly in a retrieved Layer 1
document as having issued or being required to issue an approval, permit,
NOC, or inspection certificate for this project.

**Inferred statutory authority:** Referenced indirectly in retrieved
documents without a corresponding retrieved approval or correspondence.
Must be flagged — the authority's jurisdiction may be real but cannot
be confirmed from retrieved documents alone.

**Retrieved interaction:** The evidencing document (permit, NOC, approval,
certificate, or correspondence) has been retrieved from the warehouse.

**Not retrieved interaction:** No evidencing document found in retrieved
warehouse content. This is a gap in the warehouse evidence, not a confirmed
absence of the approval. State this distinction explicitly.

**Partial interaction:** Some evidence retrieved (e.g., application
correspondence) but the outcome (e.g., approval granted) is not confirmed
from retrieved documents.

**Hold point:** An interaction that must precede a specific project activity.
Work at a hold point cannot be confirmed as compliant if the approval is
not retrieved.

---

## When to call tools

- `search_chunks` — retrieve Layer 1 project documents using the query
  terms listed above. Multiple search passes are required — statutory
  authority references are distributed across contracts, correspondence,
  programmes, and certificates.
- `search_chunks` with `layer_type = '2a'` — retrieve internal statutory
  compliance procedures
- `search_chunks` with `layer_type = '2b'` — retrieve governing standard
  statutory obligation provisions
- `get_document` — where a specific permit, NOC, or approval letter
  needs to be read in full for its terms and conditions

---

## Always flag — regardless of query

The following must always be reported:
- **Governing standard not retrieved from Layer 2b** — the contractual
  party bearing each obligation cannot be confirmed; state this explicitly
  for each required interaction
- **Statutory authorities identified as inferred** — jurisdiction claimed
  but not confirmed from a retrieved approval or correspondence; flag for
  user verification
- **Required interactions not evidenced in the warehouse** — list every
  required interaction for which no evidencing document has been retrieved;
  state whether the document may exist but not be ingested, or whether
  there is no evidence of the interaction in any retrieved document
- **Hold points without confirmed approvals** — specifically flag every
  hold point where the required approval has not been retrieved; work
  at that hold point cannot be confirmed as compliant

---

## Output format

```
## Statutory Authority Mapping Assessment

### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [standard form name — or NOT RETRIEVED]
Layer 2b provisions retrieved: [statutory obligation provisions
  description — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE]
Layer 2a source: [internal procedure document name — or NOT RETRIEVED / NOT APPLICABLE]
Layer 1 primary document: [construction contract name and reference — or NOT RETRIEVED]
Layer 1 amendment document: [particular conditions or equivalent — or NOT RETRIEVED / NOT APPLICABLE]
Provisions CANNOT CONFIRM: [list of statutory obligation provisions not
  retrieved — or NONE]

### Statutory Authority Register

| Authority | Jurisdiction Scope | Identification Basis |
|---|---|---|
| [name] | [scope] | Confirmed / Inferred |

### Required Interactions Map

| Authority | Interaction Type | Project Milestone / Activity | Obligated Party | Hold Point | Evidence in Warehouse |
|---|---|---|---|---|---|
| [name] | [permit / NOC / approval / inspection / certificate] | [milestone] | [Contractor / Employer / Engineer / CANNOT CONFIRM] | Yes / No | Retrieved / Not retrieved / Partial |

### Documents Not Retrieved

[List every statutory document referenced in recovered project documents
but not itself retrieved from the warehouse. For each: state the authority,
document type, and milestone affected.
If none: "No statutory documents identified as missing from warehouse."]

### Governance Gaps

[List every required interaction not evidenced in the warehouse.
For each: authority, interaction type, milestone affected, obligated party,
and whether this is a missing document or missing evidence of the interaction.
If none: "All identified required interactions evidenced in retrieved documents."]

### FLAGS
FLAG: [finding] — [forensic implication in one sentence]
[One flag per hold point without confirmed approval, per inferred authority
requiring user verification, per required interaction not evidenced.]

### Overall Assessment
Confidence: [GREEN / AMBER / GREY]
[GREEN: all statutory authorities confirmed from retrieved documents, all
required interactions evidenced in warehouse]
[AMBER: one or more authorities inferred; or one or more required interactions
not evidenced in warehouse; or governing standard not retrieved]
[GREY: construction contract not retrieved — statutory obligation assignments
cannot be confirmed; or insufficient documents retrieved to map interactions]
Summary: [Two to three sentences — retrieved facts only]
```

---

## Domain knowledge and standards

Statutory authorities are treated differently from contractual parties
for one reason: their authority derives from legislation, not from
appointment. It is not contestable in the way that contractual authority
can be. The Compliance SME does not assess whether a statutory body
had authority to issue a requirement — it assesses whether the project
has documented compliance with that requirement.

The distinction between "not retrieved" and "not obtained" is fundamental.
A permit that was obtained but not ingested into the warehouse will appear
as a gap in this assessment. The output must make this explicit — findings
state what is evidenced in the retrieved documents, not what the project
team represents as having occurred.

*Governed by skills/c1-skill-authoring/SKILL.md. Form-agnostic — applies to any
contract form. All characterisations grounded in retrieved warehouse
documents only.*
