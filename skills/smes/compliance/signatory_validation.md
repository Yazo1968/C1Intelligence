# Signatory Validation

**SME:** Compliance
**Tier:** 2
**Invoked by:** Legal & Compliance Orchestrator (primary); Commercial Orchestrator; Financial Orchestrator

---

## Purpose

Given a signed document, trace the signatory's authority back through the
appointment chain. Confirm or challenge whether the individual had authority
to sign on behalf of their organisation in the relevant role on the date of
signing. This skill operates at query time and depends entirely on a confirmed
governance event log produced by governance_establishment.md.

---

## Evidence Declaration

Every output produced by this skill must begin with an Evidence Declaration
block in the following format:

    EVIDENCE DECLARATION
    Layer 1 sources retrieved: [list document titles and chunk references, or NONE]
    Layer 2a sources retrieved: [list document titles and chunk references, or NONE]
    Layer 2b sources retrieved: [list document titles and chunk references, or NONE]
    Governance event log: [confirmed / not established / stale]
    Signatories assessed: [count]
    Authority confirmed: [count]
    Authority challenged: [count]
    Confidence: [GREEN / AMBER / GREY — see rules below]

Confidence rules:
- GREEN: signatory authority confirmed from retrieved documents and confirmed
  governance event log
- AMBER: one or more signatories assessed against inferred or unconfirmed
  governance events
- GREY: governance event log not established or source appointment instruments
  not retrieved — validation cannot be completed

---

## Prerequisite Check

Before any analysis, confirm governance readiness:

1. Has governance_establishment.md been run and confirmed by the user?
2. Is the governance event log current — no new documents ingested since the
   last run that may contain authority events?

If governance has not been established: state CANNOT CONFIRM — GOVERNANCE
NOT ESTABLISHED. Signatory validation requires a confirmed governance event
log. Advise the user to run governance establishment first.

If governance is stale: state WARNING — GOVERNANCE MAY BE STALE. New documents
have been ingested since the last governance run. Proceed with current event
log but flag that findings may be incomplete.

---

## Retrieval Instructions

**Layer 1 — Project documents:**
Use search_chunks to retrieve:
- The document under assessment (full text)
- The appointment instrument for each signatory
- Any delegation letter conferring authority on the signatory
- The governing contract — provisions on who may sign on behalf of each party

**Layer 2a — Internal documents:**
Use search_chunks to retrieve:
- The DOA framework applicable at the date of signing
- Any internal authorised signatory list

**Layer 2b — External standards:**
Use search_chunks_reference to retrieve the governing contract standard.
Retrieve provisions on notice execution, payment certificate signing, and
any formal requirement for who may sign on behalf of each contractual party.
Apply retrieved provisions — never assumed ones.

If the governing standard is not in Layer 2b: state CANNOT CONFIRM —
STANDARD FORM NOT RETRIEVED. Signing requirements cannot be assessed
against the standard form.

---

## Validation Steps

Execute in this order for each signatory on the document under assessment.

**Step 1 — Identify the signatory.**
Extract the signatory's name exactly as it appears on the document.
Resolve to canonical name using the governance entity registry.
If the name cannot be resolved to a known entity: flag as UNRECOGNISED
SIGNATORY — not in entity registry.

**Step 2 — Establish the signing date.**
Extract the date of signing from the document. If no date appears on the
document, use the document date. If neither is present: state CANNOT CONFIRM
— SIGNING DATE NOT RETRIEVABLE. Flag for user review.

**Step 3 — Identify the required authority.**
From the retrieved governing contract standard and Layer 1 project documents,
establish what authority is required to sign this type of document on behalf
of the relevant party. Record the retrieved provision.

**Step 4 — Trace the appointment chain.**
Using the confirmed governance event log, trace the signatory's authority
at the signing date:
- What role did the individual hold on that date?
- Under what instrument was that role conferred?
- Was the appointment active on the signing date — not terminated, replaced,
  or suspended before that date?
- Was the authority scope sufficient to cover this type of document?

**Step 5 — Check internal DOA compliance.**
Using the retrieved Layer 2a DOA framework applicable at the signing date:
- Does the internal DOA require a specific authority level to sign this
  type of document?
- Does the signatory's confirmed role satisfy that authority level?

**Step 6 — Assess and conclude.**
For each signatory state one of:

- AUTHORITY CONFIRMED: the individual held the required role under a confirmed
  appointment active on the signing date, and internal DOA requirements are
  satisfied. Source the specific governance event and appointment instrument.

- AUTHORITY CHALLENGED: one or more of the following apply —
  (a) no confirmed appointment event found for this individual in this role
      at the signing date
  (b) the appointment was terminated or suspended before the signing date
  (c) the authority scope does not cover this document type
  (d) internal DOA level not satisfied
  State which condition applies and cite the specific gap.

- CANNOT CONFIRM: required appointment instrument or DOA framework not
  retrieved. Assessment incomplete.

---

## CANNOT CONFIRM Rules

Apply these exactly.

- If the signatory cannot be resolved to a known entity in the registry:
  CANNOT CONFIRM — SIGNATORY NOT IN ENTITY REGISTRY.

- If the appointment instrument for the signatory is not retrieved:
  CANNOT CONFIRM — APPOINTMENT INSTRUMENT NOT RETRIEVED.

- If the DOA framework applicable at the signing date is not retrieved:
  CANNOT CONFIRM — DOA FRAMEWORK NOT RETRIEVED. Internal authority
  level cannot be assessed.

- If the governing standard is not in Layer 2b:
  CANNOT CONFIRM — STANDARD FORM NOT RETRIEVED. Formal signing
  requirements cannot be assessed.

---

## Output Format

### Signatory Assessment

For each signatory on the document:

**Signatory:** [canonical name]
**Role at signing date:** [role — from governance event log]
**Appointment instrument:** [instrument title and date]
**Appointment active on signing date:** Yes / No / CANNOT CONFIRM
**Authority scope covers this document type:** Yes / No / CANNOT CONFIRM
**Internal DOA satisfied:** Yes / No / CANNOT CONFIRM
**Finding:** AUTHORITY CONFIRMED / AUTHORITY CHALLENGED / CANNOT CONFIRM
**Basis:** [citation to specific governance event, appointment instrument,
and retrieved standard provision]

### Document Assessment Summary

**Document:** [title and date]
**Document type:** [notice / certificate / instruction / agreement / other]
**Overall finding:** VALID / CHALLENGED / CANNOT CONFIRM
**Conditions:** [summary of any challenges or gaps]

### Always Flag

The following must always be reported regardless of findings:
- Governance event log status at time of assessment
- Any signatory not resolvable to the entity registry
- Any appointment instrument not retrieved
- Any DOA framework gap
- Governing standard retrieval status

---

*Governed by SKILLS_STANDARDS.md v2.0. Form-agnostic — applies to any
contract form. All characterisations grounded in retrieved warehouse
documents only.*
