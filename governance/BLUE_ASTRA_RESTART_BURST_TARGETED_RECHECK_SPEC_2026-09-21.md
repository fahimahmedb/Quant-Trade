# BLUE — TARGETED ASTRA RECHECK MISSION SPEC — RESTART BURST PROOF REPAIR — 2026-09-21

## 0. Status

`MISSION_STATUS = PREPARED / BUILDER_SHA_BOUND / WAITING_FOR_EXACT_HEAD_CI`

`SCOPE = TARGETED_INDEPENDENT_RECHECK_ONLY`

`FULL_GATE_A_REAUDIT = FORBIDDEN_UNLESS_NEW_CONTRADICTORY_EVIDENCE`

This specification defines the independent review that follows the bounded
Builder/Codex restart-burst proof repair.

Do not create the Astra branch until the exact Builder delivery SHA exists AND its exact-head CI is COMPLETED / SUCCESS.

## 1. Prior independent blocker

Prior final Astra branch:

`astra/p0-hybrid-fault-matrix-independent-review-2026-09-21`

Prior final reviewed HEAD:

`c6be804e99e409ab36a455f09ea2fccbe3d88252`

Prior verdict:

`ASTRA_FAULT_MATRIX = BLOCKED_MISSING_PROOF`

Unresolved row:

`restart_burst_limit`

Prior production finding:

`REAL_DEFECT = 0`

The production property itself was consistent with the intended contract:
- launcher constant = 5;
- unit = StartLimitBurst=5;
- loaded 5 accepted;
- loaded 4 rejected.

The missing proof was discriminant independence.

## 2. Builder repair authority

Blue specification:

`governance/BLUE_RESTART_BURST_PROOF_REPAIR_SPEC_2026-09-21.md`

Prepared Builder branch:

`builder/codex-p0-hybrid-restart-burst-proof-fix-2026-09-21`

Mission dispatch base:

`6f0ca1d858d6937dc8199cc1690dce049ddb79a6`

Exact Builder delivery SHA:

`1fa82a75485661bf9bbb3de10b925126397dfec5`

Astra must review the exact delivered SHA, never merely a branch name.

## 3. Mandatory Astra attacks

Astra must independently verify all of the following.

### A1 — lineage / scope

Verify:
- repair branch descends exactly from the intended predecessor;
- no production path changed;
- changed paths are confined to qualification evidence/handoff scope;
- no known-bad replay or later phase was merged into the repair.

Unexpected production delta:
`REAL_DEFECT_OR_SCOPE_VIOLATION / STOP`.

### A2 — independent oracle provenance

Confirm the expected value `5` is not derived from:
- `launcher.RESTART_BURST_LIMIT`;
- service unit value;
- mocked loaded systemd value;
- another production object under test.

The oracle must be traceable to Blue's acceptance contract.

If the proof oracle still follows production:
`TEST_DEFECT -> MISSING_PROOF`.

### A3 — positive current-candidate proof

Independently confirm on the repaired exact SHA:
- launcher constant == 5;
- frozen unit == StartLimitBurst=5;
- real validation path accepts loaded 5;
- real validation path rejects loaded 4.

### A4 — launcher-only mutation sensitivity

Temporarily mutate launcher constant:
`5 -> 4`

Leave unit contract unchanged.

Required result:
the repaired discriminant turns RED.

### A5 — unit-only mutation sensitivity

Temporarily mutate unit:
`StartLimitBurst=5 -> StartLimitBurst=4`

Leave launcher constant unchanged.

Required result:
the repaired discriminant turns RED.

### A6 — simultaneous mutation sensitivity

Temporarily mutate BOTH:
- launcher constant `5 -> 4`;
- unit `StartLimitBurst=5 -> 4`.

Required result:
the repaired discriminant STILL turns RED.

This is the critical anti-self-reference falsifier.

If simultaneous mutation remains GREEN:
`ASTRA_RECHECK = BLOCKED_MISSING_PROOF`.

### A7 — matrix integrity

Confirm:
- exact required property set still has 19 rows;
- no duplicate/renamed-away property;
- `restart_burst_limit` classification changed only if justified;
- stored proof counts match independent recount;
- no unrelated row was altered to make counts pass.

### A8 — artifact precision

Confirm the Builder does not overclaim:
- cross-Python-build digest reproducibility;
- `harness_input_tree_digest` as standalone production-byte binding.

Those prior Astra limitations remain durable unless separately repaired and
independently proven.

### A9 — production immutability

Verify exact diff from predecessor:
- no `src/` change;
- no `deploy/` change;
- no production workflow change;
- no frozen candidate change.

### A10 — exact-head CI

Require exact-head CI SUCCESS on the Builder delivery before independent PASS.

Green CI is execution evidence only; it does not replace A1–A9.

## 4. Allowed dispositions

Astra may return only:

`ASTRA_RESTART_BURST_RECHECK = PASS_REPOSITORY_EVIDENCE`

or

`ASTRA_RESTART_BURST_RECHECK = BLOCKED_MISSING_PROOF`

or

`ASTRA_RESTART_BURST_RECHECK = BLOCKED_REAL_DEFECT`

If a production defect appears, preserve RED evidence and STOP.
Do not repair production as auditor.

## 5. PASS meaning

PASS closes ONLY the prior unresolved repository proof row:

`restart_burst_limit`

It does NOT by itself declare:
- P14D hybrid amendment;
- target-host readiness;
- Gate B;
- t0;
- Product integration;
- economic/scientific readiness;
- real-capital authorization.

## 6. Required handoff

When the recheck branch is eventually created, final handoff path:

`handoff/ASTRA_P0_RESTART_BURST_PROOF_RECHECK_2026-09-21.md`

It must bind:
- exact Builder delivery SHA;
- exact changed paths;
- A1–A10 outcomes;
- M1/M2/M3 independent mutation results;
- final matrix recount;
- defect classifications;
- exact-head Astra CI.

## 7. Blue reception after PASS

Only if Astra returns:
`PASS_REPOSITORY_EVIDENCE`

Blue may then evaluate:
`FINAL_INDEPENDENT_FAULT_MATRIX_REVIEW = PASS`

and proceed to the final hybrid consistency merge.

No promotion occurs automatically.


## 8. Bound delivery / CI wait — 2026-09-21

Builder delivery is now bound to:
`1fa82a75485661bf9bbb3de10b925126397dfec5`.

Exact-head workflow:
`35549017908`.

At last Blue observation the workflow was `IN_PROGRESS`, currently executing
the full unit suite. Dispatch remains blocked until the same SHA is still live
and this run is `COMPLETED / SUCCESS`.


## 9. Owner-authorized speculative pre-staging — 2026-09-21

The owner authorized advancing reversible preparation while exact-head CI is still running.

Allowed before CI success:
- create the targeted Astra branch exactly from Builder delivery SHA
  `1fa82a75485661bf9bbb3de10b925126397dfec5`;
- commit only the audit mission/specification on top of that candidate;
- prepare commands/checklists.

Forbidden before CI success:
- execute the independent audit as authoritative evidence;
- classify PASS/BLOCK based on the prestaged branch;
- promote hybrid governance;
- authorize Gate B;
- infer Builder acceptance.

If exact-head CI `35549017908` fails or Builder HEAD moves, the prestaged branch is invalid as an audit input and must be abandoned/rebased from the newly accepted exact SHA.

`PRESTAGING_AUTHORITY = REVERSIBLE_PREPARATION_ONLY`
`AUDIT_AUTHORITY = BLOCKED_UNTIL_BUILDER_EXACT_HEAD_CI_SUCCESS`
