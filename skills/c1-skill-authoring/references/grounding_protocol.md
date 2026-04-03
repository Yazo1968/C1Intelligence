# C1 Grounding Protocol — Evidence Declaration and Retrieval Rules

These rules govern every C1 skill file and orchestrator directive.
They prevent agents from generating unverified content by making
retrieval status explicit and structurally enforced in every output.

---

## Why this protocol exists

A production query produced this output:
> "Sub-Clause 11.8 (Fresh Milk / Unfulfilled Obligations at Completion)
> has been deleted."

"Fresh Milk" is a hallucination. The warehouse contained the correct answer:
Sub-Clause 11.8 = "Contractor to Search" (FIDIC Yellow Book 1999).
The agent skipped retrieval because it had FIDIC knowledge in its system
prompt and generated plausible-sounding content instead.

The fix is structural: agents must declare what they retrieved and what
they could not retrieve, and the output format enforces this declaration.
When retrieval fails, the output is CANNOT CONFIRM — not generated content.

---

## Evidence Declaration Block — Mandatory Format

This block must appear as the **first section** of every agent output.
It may not be omitted under any circumstances.

```
### Evidence Declaration
Layer 2b retrieved: [YES / NO / PARTIAL]
Layer 2b source: [name of ingested standard, e.g. "FIDIC Yellow Book 1999
  General Conditions" or "NEC4 Engineering and Construction Contract"
  — or NOT RETRIEVED]
Layer 2b provisions retrieved: [brief description of what was retrieved,
  e.g. "Clause 20.1 Notice of Claim, Clause 8.4 EOT" — or NONE]
Layer 2a retrieved: [YES / NO / NOT APPLICABLE]
Layer 2a source: [internal policy name — or NOT RETRIEVED / NOT APPLICABLE]
Layer 1 primary document: [document name and reference number —
  or NOT RETRIEVED]
Layer 1 amendment document: [Particular Conditions / Special Conditions /
  Z Clauses / equivalent — or NOT RETRIEVED / NOT APPLICABLE]
Provisions CANNOT CONFIRM: [list of provisions where Layer 2b retrieval
  failed — or NONE]
```

---

## Hard Rules

### Rule 1 — Block always present
Every output must begin with the Evidence Declaration block.
An output without this block fails the quality gate.

### Rule 2 — No standard form characterisation without retrieval
If a provision appears in `Provisions CANNOT CONFIRM`, the output must state:

    CANNOT CONFIRM — STANDARD FORM NOT RETRIEVED

No description of that provision's content or effect is permitted.
Training knowledge is not evidence. It is never a substitute for retrieval.

### Rule 3 — Confidence cap when Layer 2b not retrieved
If `Layer 2b retrieved: NO` for any provision in the analysis:
confidence for findings that depend on that provision must be **AMBER** maximum.

### Rule 4 — Confidence cap when amendment document not retrieved
If `Layer 1 amendment document: NOT RETRIEVED`:
confidence for any finding that depends on the amendment position
must be **GREY**. Clause-level analysis cannot proceed.

### Rule 5 — PARTIAL means incomplete, not sufficient
If `Layer 2b retrieved: PARTIAL`: findings from retrieved provisions
may proceed. Findings from unretrieved provisions must be CANNOT CONFIRM.

### Rule 6 — Custom numbering must be flagged
If the Layer 1 contract uses a numbering scheme that departs from the
standard form: flag this explicitly. The Layer 2b provision at a given
number may not correspond to the Layer 1 usage. Mark the subject matter
as CANNOT CONFIRM from Layer 2b rather than silently applying the
standard form text.

---

## Retrieval Instructions for Skill Files

**Required language in Before you begin — Layer 2b:**

> After identifying the governing contract standard from Layer 1,
> call search_chunks to retrieve the relevant provision from Layer 2b.
>
> Query format: describe the provision by subject matter, not by
> clause number. Example: search for "notice of claim time bar
> contractor" rather than a specific clause number. The clause number
> in Layer 2b corresponds to the standard form — not necessarily to
> the numbering used in this project's contract.
>
> If retrieval returns no result: record the provision in
> `Provisions CANNOT CONFIRM` in the Evidence Declaration block.
> Do not describe the provision from training knowledge.
> State CANNOT CONFIRM — STANDARD FORM NOT RETRIEVED in the output body.

**Required language in Always flag:**

> **Governing standard not retrieved from Layer 2b** — flag when any
> provision characterisation is based on CANNOT CONFIRM status. State
> which provision was not retrieved, what analysis cannot proceed as a
> result, and what standard would need to be ingested to resolve it.

---

## Classification Rules for CANNOT CONFIRM

| Layer 2b status | Amendment doc status | Output permitted |
|---|---|---|
| RETRIEVED | RETRIEVED | Full characterisation with source citations |
| RETRIEVED | NOT RETRIEVED | Standard form text only — amendment position unknown |
| NOT RETRIEVED | RETRIEVED | Amendment noted, provision content CANNOT CONFIRM |
| NOT RETRIEVED | NOT RETRIEVED | CANNOT CONFIRM — confidence GREY |
| PARTIAL | Either | Retrieved provisions proceed; rest CANNOT CONFIRM |

**Confidence cap summary:**

| Condition | Maximum confidence |
|---|---|
| All required Layer 2b retrieved, amendment doc retrieved | GREEN (if evidence supports) |
| Layer 2b retrieved, amendment doc not retrieved | AMBER |
| Layer 2b not retrieved for any provision | AMBER |
| Amendment doc not retrieved AND Layer 2b not retrieved | GREY |
