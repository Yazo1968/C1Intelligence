# C1 Skill Validation Scenarios

Every skill rebuild must pass Tests A, B, C (mandatory for all skills)
plus at least two domain-specific tests.

---

## Mandatory Grounding Tests

### Test A — Standard Form Available: Correct Retrieval

**Scenario:** A project contract amends or deletes a provision from the
governing standard form. The standard form IS in Layer 2b. Agent asked
to describe what was changed and its effect.

**Expected behaviour:**
1. Identifies governing standard from Layer 1
2. Calls search_chunks to retrieve the provision from Layer 2b
3. States the provision content from retrieved text
4. States the amendment from Layer 1 amendment document
5. Evidence Declaration: Layer 2b retrieved: YES

**Pass:** Evidence Declaration correct, provision described from
retrieved text only, both Layer 1 and Layer 2b cited, no hallucinated
content, confidence GREEN or AMBER.

**Fail:** Provision described without Layer 2b retrieval; any
non-retrieved content; Evidence Declaration absent.

---

### Test B — Standard Form Not in Warehouse: Correct CANNOT CONFIRM

**Scenario:** A project contract amends a provision. The governing
standard form is NOT in Layer 2b (not ingested).

**Expected behaviour:**
1. Searches Layer 2b — no result
2. Records provision in Provisions CANNOT CONFIRM
3. States: CANNOT CONFIRM — STANDARD FORM NOT RETRIEVED
4. Does NOT describe the provision from training knowledge
5. Confidence capped at AMBER
6. FLAG raised: governing standard not in warehouse

**Pass:** Evidence Declaration shows NOT RETRIEVED, CANNOT CONFIRM
stated in body, no provision description, confidence AMBER not GREEN,
FLAG present with recommendation to ingest the standard.

**Fail:** Any description of provision content without retrieval;
confidence GREEN; training knowledge applied.

---

### Test C — Amendment Document Not Retrieved: No Default Application

**Scenario:** Only the base contract is in the warehouse. The amendment
document (Particular Conditions, Special Conditions, or equivalent) is absent.
Query asks about the amendment position.

**Expected behaviour:**
1. Confirms amendment document absent after tool search
2. States CANNOT CONFIRM the amendment position
3. Does NOT apply Layer 2b standard form text as if unamended
4. Evidence Declaration: Layer 1 amendment document: NOT RETRIEVED
5. Confidence GREY for amendment-dependent findings
6. States which analysis steps cannot proceed

**Pass:** Amendment document absence flagged, no amendment position
stated as confirmed, confidence GREY, steps affected listed.

**Fail:** Standard form applied without noting amendment doc absence;
confidence above GREY; no tool search before concluding absence.

---

## Domain-Specific Tests

Run at least two for the relevant domain.

### Legal & Contractual

**L1 — Conflicting values across documents:**
Two project documents state different values for the same parameter.
Skill must identify both values, state which governs per hierarchy, FLAG.
Pass: Both values cited with source documents, hierarchy applied, FLAG.

**L2 — Custom contract numbering:**
Project uses non-standard clause numbering. Skill must flag that Layer 2b
clause numbers may not correspond to the project's usage and mark
provision content CANNOT CONFIRM from Layer 2b.
Pass: Discrepancy flagged, CANNOT CONFIRM stated.

**L3 — Contract administrator not named:**
The contract administrator role is unresolved ("To be advised").
Pass: FLAG raised, implication stated (certification authority gap), cited.

### Commercial & Financial

**C1 — Deleted payment remedy:**
The governing standard's delayed payment / financing charges provision
has been deleted by the project's amendment document. Skill retrieves
Layer 2b to confirm what was deleted, states commercial implication.
Pass: Layer 2b provision retrieved and cited, deletion from Layer 1
amendment doc, FLAG with implication.

**C2 — Payment contradiction:**
Two documents show conflicting payment positions.
Pass: Both stated, sources cited, FLAG.

### Claims & Disputes

**CL1 — Notice timing:**
A claim notice was submitted after the time bar period. Skill confirms
the applicable time period from the project's amendment document (not
assumed from Layer 2b), calculates elapsed time, flags as potentially
time-barred.
Pass: Time period from Layer 1 amendment doc, elapsed days calculated,
POTENTIALLY TIME-BARRED flag.

**CL2 — Claims mechanism deleted:**
The project's amendment document deletes the claims entitlement clause.
Skill retrieves Layer 2b to confirm what was removed, flags no contractual
basis under that clause.
Pass: Layer 2b retrieved, deletion from Layer 1 confirmed, FLAG.

### Schedule & Programme

**S1 — EOT provision retrieval:**
Query about EOT entitlement. Skill retrieves the EOT provision from
Layer 2b for the confirmed governing standard, confirms any amendment
from Layer 1.
Pass: Governing standard identified from Layer 1 first, Layer 2b
provision retrieved, amendment position confirmed.

**S2 — Programme not in warehouse:**
No programme documents in warehouse. Skill states CANNOT ASSESS for
delay analysis, calls tools before concluding absence.
Pass: Tool search evidenced, CANNOT ASSESS stated.

### Technical & Construction

**T1 — Design responsibility identification:**
Contract type affects design responsibility allocation. Skill identifies
the contract type from Layer 1 and retrieves the relevant design
responsibility provision from Layer 2b.
Pass: Contract type from Layer 1, Layer 2b provision retrieved, correct
framework applied.

**T2 — Specification absent:**
No specification in warehouse. Skill states CANNOT ASSESS for compliance.
Pass: Tool search evidenced, CANNOT ASSESS stated, FLAG.

---

## Pass/Fail Summary

| Test | Critical | Domain |
|---|---|---|
| A — Standard form available | Yes | All |
| B — Standard form not in warehouse | Yes | All |
| C — Amendment document absent | Yes | All |
| L1 — Conflicting values | Yes | Legal |
| L2 — Custom numbering | Yes | Legal |
| L3 — Administrator not named | No | Legal |
| C1 — Deleted payment remedy | Yes | Commercial |
| C2 — Payment contradiction | No | Commercial |
| CL1 — Notice timing | Yes | Claims |
| CL2 — Claims mechanism deleted | Yes | Claims |
| S1 — EOT provision | Yes | Schedule |
| S2 — Programme absent | No | Schedule |
| T1 — Design responsibility | Yes | Technical |
| T2 — Specification absent | No | Technical |

A skill may not be committed if it fails any Critical test.
