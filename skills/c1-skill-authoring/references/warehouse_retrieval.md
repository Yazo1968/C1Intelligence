# C1 Warehouse Retrieval — Three-Layer Model

This file defines the three-layer warehouse model and the retrieval patterns
agents must follow. Read this before writing any Before you begin section
in a C1 skill file.

---

## The Three Layers

### Layer 1 — Project Documents

Everything uploaded for this specific project by any party. This is the
primary evidence layer. All project-specific facts come exclusively from here.

**What Layer 1 contains:**
- Contracts of any form (FIDIC, NEC, JCT, AIA, bespoke, PPP — whatever was
  executed for this project)
- Contract amendments, side letters, supplemental agreements, novation
- Correspondence, notices, instructions, determinations
- Claims, counterclaims, expert reports, adjudication decisions
- Schedules, programmes, delay analyses, progress reports
- Payment applications, certificates, variations, final accounts
- Technical documents: drawings, specifications, RFIs, shop drawings, NCRs
- Financial reports, budgets, cost reports, EVM data
- Internal approvals, meeting minutes, site diaries

**How to retrieve:**
`search_chunks` with query + optional `document_type` filter
`get_document` when full document needed, not just chunks

**Critical:** Project-specific facts (contract sum, key dates, party names,
specific clause amendments, certified amounts) must come from Layer 1.
Never assume or infer these from any other source.

---

### Layer 2a — Internal Reference Documents

The organisation's own governing documents — policies, standards, authority
frameworks. These apply across all projects for this organisation.

**What Layer 2a contains:**
- Delegation of Authority (DOA) matrices
- Approval and sign-off authority frameworks
- Internal procurement policies and procedures
- Internal financial control standards
- Project governance frameworks and charters
- Internal quality management standards
- Corporate ethics and compliance policies

**How to retrieve:**
`search_chunks` with `layer_type = '2a'` filter

**Use when:** The analysis requires checking whether a decision, approval,
or action complied with the organisation's own internal requirements —
independent of what the external contract requires.

**If Layer 2a not retrieved when needed:**
State that the applicable internal policy was not retrieved. Do not assume
the policy content. State CANNOT CONFIRM — INTERNAL POLICY NOT RETRIEVED.

---

### Layer 2b — External Reference Documents

The external standards, standard forms, laws, and professional frameworks
against which project conduct is assessed. These are ingested by the
platform owner and are available to all projects.

**What Layer 2b may contain** (depends on what has been ingested):
- Standard forms of contract: FIDIC Red/Yellow/Silver Book editions,
  NEC4, JCT contracts, AIA contracts, or any other standard form
- Professional standards: PMBOK, IFRS, SCL Protocol, AACE RP 29R-03,
  ISO standards
- Applicable laws and regulations: construction law, commercial law,
  procurement regulations, jurisdiction-specific requirements
- Government authority standards and requirements
- Industry codes and specifications

**How to retrieve:**
`search_chunks` with `layer_type = '2b'` filter
Query format: "[standard name] [provision description]"
Example: "clause governing notice of claim" — not "FIDIC 20.1"
Do not assume a specific standard form is present. Retrieve and confirm.

**The retrieval-first pattern:**
1. Identify from Layer 1 what governing standard applies
   (what contract form does the project use?)
2. Retrieve the relevant provision from Layer 2b
   (search for it — do not assume it is there)
3. Confirm it was retrieved before characterising it
4. If not retrieved: CANNOT CONFIRM — STANDARD NOT IN WAREHOUSE

**If Layer 2b not retrieved when needed:**
This is a significant gap. State what standard was expected, that it was
not found in Layer 2b, and that the analysis for that provision cannot
proceed. Flag it clearly. Do not characterise the provision from training
knowledge.

---

## The Retrieval Sequence

For every analytical step that involves a provision from a governing standard:

```
Step 1: Identify the governing standard from Layer 1
        "What contract form does this project use?"
        Source: Layer 1 contract documents

Step 2: Retrieve the provision from Layer 2b
        search_chunks(query="[provision description]", layer_type="2b")
        "What does the governing standard say about this?"

Step 3: Retrieve the project's position from Layer 1
        "Has this project amended the standard provision?"
        Source: Layer 1 amendment documents (Particular Conditions,
        Special Conditions, Z clauses, or equivalent)

Step 4: Apply the project's position — not the Layer 2b default
        If the standard was amended: apply the amendment
        If the standard was not amended: apply the standard form provision
        If the amendment document was not retrieved: CANNOT CONFIRM

Step 5: Check internal policy from Layer 2a if relevant
        "Does internal policy impose any additional requirement?"
```

---

## What Belongs Where

| Type of knowledge | Where it belongs | NOT in |
|---|---|---|
| Contract sum, dates, parties | Layer 1 | Skills, prompts |
| Clause amendments, PC provisions | Layer 1 | Skills, prompts |
| What a standard form clause says | Layer 2b | Skills, prompts |
| What the law requires | Layer 2b | Skills, prompts |
| What PMBOK says about EVM | Layer 2b | Skills, prompts |
| DOA and approval limits | Layer 2a | Skills, prompts |
| How to analyse (reasoning framework) | Skill files | Warehouse |
| What to retrieve | Skill files | Warehouse |
| How to classify findings | Skill files | Warehouse |
| What to flag | Skill files | Warehouse |

---

## When a Required Standard Is Not in the Warehouse

If the governing standard for this project is not in Layer 2b:

1. Flag this clearly in the Evidence Declaration block
2. State which standard was expected and not found
3. State which analysis steps cannot proceed
4. Do NOT apply training knowledge as a substitute
5. Recommend the platform owner ingest the relevant standard

This is not a failure of the analysis — it is an honest and forensically
correct output. An explicit CANNOT CONFIRM with a stated reason is more
valuable than a finding based on unverified training knowledge.

---

## Layer 2b Currently Ingested (Example)

The following are currently in the warehouse as of April 2026.
This list changes as the platform owner ingests additional references.
Always retrieve and confirm — do not assume.

- FIDIC Red Book 1999 General Conditions
- FIDIC Red Book 2017 General Conditions
- FIDIC Yellow Book 1999 General Conditions
- FIDIC Yellow Book 2017 General Conditions
- FIDIC Silver Book 1999 General Conditions
- FIDIC Silver Book 2017 General Conditions

Future ingestion candidates (not yet present):
- NEC4 Engineering and Construction Contract
- PMBOK 7th Edition
- IFRS 15 (Revenue from Contracts with Customers)
- SCL Delay and Disruption Protocol 2nd Edition
- Applicable jurisdiction laws and regulations
- Government authority requirements

**The skill file never assumes this list is current or complete.**
The agent always retrieves to confirm what is available.
