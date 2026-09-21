# ASTRA — TARGETED RESTART-BURST PROOF RECHECK MISSION — 2026-09-21

## 0. Status / authority

`MISSION = PRESTAGED / DO_NOT_EXECUTE_AS_AUTHORITY_UNTIL_BUILDER_CI_SUCCESS`

This branch was created exactly from Builder delivery:

`1fa82a75485661bf9bbb3de10b925126397dfec5`

Builder exact-head CI required before authoritative audit execution:

`35549017908 = MUST_BE_COMPLETED_SUCCESS`

If that run fails, or the Builder branch moves, STOP. This prestaged audit input is invalid.

## 1. Role

You are Astra / independent reviewer.

Do not confirm Builder claims by inspection alone.
Attack the repaired proof independently.

Do not modify production.

Do not broaden into a full Gate-A re-audit unless new contradictory evidence appears.

## 2. Mandatory references

Read:

1. `QUANT_NORTH_STAR.md`
2. Builder handoff:
   `handoff/BUILDER_CODEX_P0_RESTART_BURST_PROOF_REPAIR_2026-09-21.md`
3. Blue repair specification from `blue/master-v2-2026-09-20`:
   `governance/BLUE_RESTART_BURST_PROOF_REPAIR_SPEC_2026-09-21.md`
4. Blue targeted recheck specification:
   `governance/BLUE_ASTRA_RESTART_BURST_TARGETED_RECHECK_SPEC_2026-09-21.md`
5. Prior final blocking audit:
   `astra/p0-hybrid-fault-matrix-independent-review-2026-09-21@c6be804e99e409ab36a455f09ea2fccbe3d88252`

## 3. Prior finding

Prior final verdict:

`ASTRA_FAULT_MATRIX = BLOCKED_MISSING_PROOF`

Prior unresolved row:

`restart_burst_limit`

Prior production REAL_DEFECT:

`0`

The prior helper followed the production constant as its oracle and remained
GREEN under a temporary `5 -> 4` production-constant mutation.

## 4. Exact object under recheck

Builder repair SHA:

`1fa82a75485661bf9bbb3de10b925126397dfec5`

Frozen production candidate bound by the matrix remains:

`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Expected independent contract:

`EXPECTED_RESTART_BURST_LIMIT = 5`

## 5. Required independent attacks

### A1 lineage/scope
Verify exact ancestry from predecessor and confirm no production delta.

### A2 oracle independence
Verify expected 5 is not derived from launcher constant, unit contents, loaded
systemd value, or another production object under test.

### A3 current-candidate facts
Independently verify:
- launcher constant = 5;
- unit StartLimitBurst = 5;
- real validation path accepts loaded 5;
- real validation path rejects loaded 4.

### A4 M1
Mutate launcher only 5 -> 4.
Required: repaired discriminant RED.

### A5 M2
Mutate unit only 5 -> 4.
Required: repaired discriminant RED.

### A6 M3
Mutate BOTH launcher and unit 5 -> 4.
Required: repaired discriminant still RED.

This is the critical anti-self-reference attack.

### A7 matrix integrity
Independently recount:
- 19 required rows;
- 19 unique property names;
- no unrelated row laundering;
- restart row classification justified;
- stored counts consistent.

### A8 prior evidence debt
Preserve prior limitations:
- report digest is Python-build-bound;
- harness_input_tree_digest is not standalone full production-byte binding.

### A9 production immutability
No src/, deploy/, production tests or workflows changed in the repair.

### A10 exact-head CI
Before PASS, confirm Builder exact-head run:
`35549017908 = COMPLETED / SUCCESS`.

## 6. Classifications

Use:
- REAL_DEFECT
- TEST_DEFECT
- MISSING_PROOF
- TARGET_HOST_ONLY
- NON_ISSUE

If any mandatory mutation remains GREEN:
`ASTRA_RESTART_BURST_RECHECK = BLOCKED_MISSING_PROOF`.

If production itself fails:
`ASTRA_RESTART_BURST_RECHECK = BLOCKED_REAL_DEFECT`.

Only if all repository requirements close:
`ASTRA_RESTART_BURST_RECHECK = PASS_REPOSITORY_EVIDENCE`.

## 7. Handoff

Write:

`handoff/ASTRA_P0_RESTART_BURST_PROOF_RECHECK_2026-09-21.md`

Bind:
- Builder exact SHA;
- Builder exact-head CI;
- Astra branch HEAD;
- exact changed paths;
- A1-A10 results;
- M1/M2/M3 results;
- matrix recount;
- production immutability;
- residual TARGET_HOST_ONLY scope.

## 8. Non-claims

Do not declare:
- hybrid amendment;
- Gate B;
- target-host readiness;
- t0;
- Product integration;
- capital authorization.

After final handoff and exact-head Astra CI, STOP and return control to Blue.
