# C1 — Skills Standards

**Version:** 2.0
**Status:** Active — human-readable authoritative reference
**Operational guidance:** `skills/c1-skill-authoring/SKILL.md`

---

## Purpose

This document states the four warehouse-grounding principles that govern all
C1 agent skill files and orchestrator directives. These principles are
authoritative. The operational skill authorship workflow — structure,
templates, retrieval instructions, validation scenarios — is in the
`c1-skill-authoring` skill.

---

## What C1 Agent Skills Are

Skill files are operational instruction files. They tell an LLM how to reason
over construction project documents. They are not reference documents, not
knowledge bases, and not training guides.

**Skills contain:** reasoning frameworks, retrieval instructions, decision
rules, output formats, mandatory flags.

**Skills do not contain:** standard form knowledge, clause content, legal
rules, domain-specific facts. All of that lives in the warehouse.

The warehouse has three layers:
- **Layer 1 — Project:** Project-specific documents (any contract form,
  correspondence, claims, schedules, payment records, technical documents)
- **Layer 2a — Internal:** Organisation policies, DOA matrices, authority
  frameworks, internal procedures
- **Layer 2b — External:** Standard forms (FIDIC, NEC, JCT, AIA, or any
  other), professional standards (PMBOK, IFRS, SCL, AACE), laws, regulations

---

## Four Warehouse-Grounding Principles

These apply to every skill file. They supersede all earlier guidance.
A skill file that violates any of these principles fails the quality gate.

### Principle 1 — No Assumption, Extrapolation, or Inference

An agent may only state what the retrieved documents support. If a required
document is not in the warehouse, the output is CANNOT ASSESS — not an
estimate, not a default, not training knowledge applied as a substitute.

Every value, date, period, amount, and clause description must trace to a
specific retrieved document. The output format must include a Documents Not
Retrieved section listing every required document absent from the warehouse.

### Principle 2 — Contract-Type and Standard Form Always Identified

Every analytical step that involves a contractual provision must first
identify the governing standard from Layer 1 project documents. The agent
does not assume which contract form is in use. It identifies it, then
retrieves the relevant provision from Layer 2b.

Where the analysis differs depending on the contract form or standard in
use, this must be stated explicitly in the skill file.

### Principle 3 — Three-Layer Retrieval Always Distinguished

Every skill file must explicitly distinguish between:
- Layer 1 facts (what this project agreed)
- Layer 2a policy (what the organisation requires internally)
- Layer 2b standards (what the governing external standard says)

The retrieval sequence is always: identify from Layer 1 → retrieve from
Layer 2b → retrieve amendment position from Layer 1 → apply Layer 1 position.

If the governing standard is not in Layer 2b: CANNOT CONFIRM.
If the amendment document is not in Layer 1: CANNOT CONFIRM the amendment.

### Principle 4 — CANNOT CONFIRM Is the Opening State

The agent starts from zero evidence. CANNOT CONFIRM is not a fallback —
it is the correct output for any step where required evidence was not
retrieved.

The skill must instruct the agent to call tools to search before concluding
a document is absent. After a tool search returns nothing: state CANNOT
CONFIRM, list the missing document, and state which steps cannot proceed.

---

## Evidence Declaration Block

Every skill output must begin with an Evidence Declaration block. This block
makes the retrieval status explicit and auditable. Format and rules are in
`skills/c1-skill-authoring/references/grounding_protocol.md`.

---

## Document Control

| Field | Value |
|---|---|
| Version | 2.0 — Supersedes v1.4; operational guidance moved to c1-skill-authoring skill |
| Date | April 2026 |
