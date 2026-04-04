# Statutory Authority Mapping

**SME:** Compliance
**Tier:** 2
**Invoked by:** Legal & Compliance Orchestrator (primary); Technical Orchestrator

---

## Purpose

Identify all statutory authorities with jurisdiction over the project.
Map required approvals, permits, and NOCs to project milestones. Assess
whether required interactions with statutory authorities are evidenced
in the warehouse. Statutory authority is not conferred by the contract —
it derives from legislation and is not contestable. The relevant forensic
questions are whether the correct authorities have been identified, what
interactions are required, and whether those interactions are documented.

---

## Evidence Declaration

Every output produced by this skill must begin with an Evidence Declaration
block in the following format:

    EVIDENCE DECLARATION
    Layer 1 sources retrieved: [list document titles and chunk references, or NONE]
    Layer 2a sources retrieved: [list document titles and chunk references, or NONE]
    Layer 2b sources retrieved: [list document titles and chunk references, or NONE]
    Statutory authorities identified: [count]
    Required interactions identified: [count]
    Interactions evidenced in warehouse: [count]
    Interactions not evidenced: [count]
    Confidence: [GREEN / AMBER / GREY — see rules below]

Confidence rules:
- GREEN: all statutory authorities identified from retrieved documents;
  all required interactions assessed against retrieved evidence
- AMBER: one or more statutory authorities inferred from context rather
  than explicitly named in a retrieved document; or jurisdiction scope
  of a retrieved authority is uncertain
- GREY: insufficient documents retrieved to identify statutory authorities
  with jurisdiction over the project — mapping is incomplete

---

## Retrieval Instructions

**Layer 1 — Project documents:**
Use search_chunks to retrieve:
- The construction contract — any provisions referencing statutory
  authorities, permits, approvals, or regulatory requirements
- Correspondence with statutory authorities
- Permits, NOCs, approvals, and inspection certificates
- Programme or milestone documents referencing regulatory hold points
- Any statutory authority approval conditions or correspondence

Query terms: "permit", "approval", "NOC", "no objection", "municipality",
"authority", "regulatory", "inspection", "licence", "statutory",
"civil defence", "utility", "traffic", "planning", "building permit",
"completion certificate", "occupancy".

**Layer 2a — Internal documents:**
Use search_chunks to retrieve any internal procedures or checklists
referencing statutory approvals or permit requirements.

**Layer 2b — External standards:**
Use search_chunks_reference to retrieve the governing contract standard.
Retrieve provisions placing statutory compliance obligations on the
Contractor, Employer, or Engineer. Apply retrieved provisions — never
assumed ones.

If the governing standard is not in Layer 2b: state CANNOT CONFIRM —
STANDARD FORM NOT RETRIEVED. Contractual statutory compliance obligations
cannot be assessed.

---

## Mapping Steps

Execute in this order.

**Step 1 — Retrieve across all three layers** as instructed above.

**Step 2 — Identify statutory authorities.**
From all retrieved documents, identify every entity that:
- Is referenced as a government body, municipality, regulatory authority,
  or statutory body
- Issues permits, NOCs, approvals, or inspection certificates
- Has jurisdiction over any aspect of the project (planning, building,
  civil defence, utilities, traffic, environmental, health and safety,
  or any other regulatory domain)

For each identified authority record:
- Authority name (exactly as it appears in retrieved documents)
- Jurisdiction scope (what aspect of the project it regulates)
- Identification basis: confirmed (explicitly named in retrieved document)
  or inferred (deduced from context)

**Step 3 — Map required interactions.**
For each identified statutory authority, establish from retrieved documents
what interactions are required:
- Type of interaction (permit / NOC / approval / inspection / certificate /
  notification / other)
- Project milestone or activity to which it relates
- Which party bears the obligation (Contractor / Employer / Engineer /
  other — from retrieved contract provisions)
- Whether the interaction is a hold point (work cannot proceed without it)
  or a notification only

**Step 4 — Assess evidence in the warehouse.**
For each required interaction, assess whether the relevant document is
present in the warehouse:
- Retrieved: the permit, NOC, approval, or correspondence is in the warehouse
- Not retrieved: no document evidencing this interaction has been retrieved
- Partial: correspondence is retrieved but the approval outcome is not,
  or the document is incomplete

**Step 5 — Identify gaps.**
List every required interaction for which no evidencing document has been
retrieved. Flag each gap with the authority name, interaction type,
and the project milestone affected.

---

## CANNOT CONFIRM Rules

Apply these exactly.

- If a statutory authority is referenced in project documents but its
  jurisdiction scope cannot be determined from retrieved documents:
  CANNOT CONFIRM — JURISDICTION SCOPE OF [authority name] NOT DETERMINABLE
  FROM RETRIEVED DOCUMENTS.

- If a required interaction is indicated by retrieved contract provisions
  but no corresponding permit, NOC, or approval document is in the warehouse:
  CANNOT CONFIRM — [interaction type] FROM [authority name] NOT RETRIEVED.
  This is a gap, not a finding that the approval was not obtained.

- If the governing standard is not in Layer 2b:
  CANNOT CONFIRM — STANDARD FORM NOT RETRIEVED. Contractual statutory
  compliance obligations cannot be assessed from the standard form.

- If project location or regulatory jurisdiction cannot be determined
  from retrieved documents:
  CANNOT CONFIRM — PROJECT JURISDICTION NOT DETERMINABLE. Statutory
  authority identification is based on retrieved document references only.

---

## Output Format

### Statutory Authority Register

| Authority | Jurisdiction Scope | Identification Basis |
|---|---|---|
| [name] | [scope] | Confirmed / Inferred |

### Required Interactions Map

| Authority | Interaction Type | Project Milestone / Activity | Obligated Party | Hold Point | Evidence in Warehouse |
|---|---|---|---|---|---|
| [name] | permit / NOC / approval / inspection / certificate | [milestone] | Contractor / Employer / Engineer | Yes / No | Retrieved / Not retrieved / Partial |

### Gaps

List every required interaction not evidenced in the warehouse.
For each gap state: authority, interaction type, milestone affected,
and which party bears the obligation.
If no gaps: state "All identified required interactions evidenced in
retrieved documents."

### Always Flag

The following must always be reported regardless of findings:
- Total statutory authorities identified (confirmed vs inferred)
- Total required interactions identified
- Total interactions not evidenced in the warehouse
- Any authority referenced in project documents that could not be
  retrieved for jurisdiction confirmation
- Governing standard retrieval status

---

## Scope Boundary

This skill identifies statutory authorities and maps required interactions.
It does not assess the internal governance or authority structure of
statutory bodies — their authority derives from legislation, not from
appointment chains, and is not contestable. The compliance question is
whether the project has obtained and documented the required interactions,
not whether the statutory body had authority to issue them.

---

*Governed by SKILLS_STANDARDS.md v2.0. Form-agnostic — applies to any
contract form. All characterisations grounded in retrieved warehouse
documents only.*
