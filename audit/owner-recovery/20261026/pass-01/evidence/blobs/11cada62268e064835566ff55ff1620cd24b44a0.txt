# BUILDER CODEX — P0 RESTART BURST PROOF REPAIR MISSION — 2026-09-21

## 0. Role and scope

You are Builder / Codex.

This is a bounded PROOF-ONLY repair.

Do not modify production.

Do not advance to known-bad replay, Gate B, Gate C, Gate D, target-host
execution, P14D promotion, Product integration or capital work.

## 1. Exact branch and predecessor

Work only on:

`builder/codex-p0-hybrid-restart-burst-proof-fix-2026-09-21`

This branch was created exactly from:

`builder/codex-p0-hybrid-fault-matrix-2026-09-21@e5c4c720e758cd8ab3f0e04faf541b26e204be16`

Required predecessor invariant:

`origin/builder/codex-p0-hybrid-fault-matrix-2026-09-21 == e5c4c720e758cd8ab3f0e04faf541b26e204be16`

If the predecessor moved, STOP and report.

Do not use the later known-bad-replay branch as the base and do not cherry-pick
it into this repair.

## 2. Read before editing

Read:

1. `QUANT_NORTH_STAR.md`
2. from Blue current:
   `governance/BLUE_RESTART_BURST_PROOF_REPAIR_SPEC_2026-09-21.md`
3. Astra final review:
   `astra/p0-hybrid-fault-matrix-independent-review-2026-09-21:handoff/ASTRA_P0_HYBRID_FAULT_MATRIX_INDEPENDENT_REVIEW_2026-09-21.md`
4. predecessor:
   `tools/p0_qualification/gate_a/fault_matrix.py`
5. predecessor:
   `tools/p0_qualification/evidence/gate_a/fault_matrix.json`

Do not broadly re-orient the repository.

## 3. Finding to repair

Astra found:

`restart_burst_limit = TEST_DEFECT -> MISSING_PROOF`

No production REAL_DEFECT was found.

The current helper derives its expected loaded value from the production
constant itself, so mutating production `5 -> 4` leaves the helper green.

Your task is to repair ONLY this proof defect.

## 4. Independent oracle

The Blue acceptance contract is:

`EXPECTED_RESTART_BURST_LIMIT = 5`

The expected value MUST NOT be derived from:
- `launcher.RESTART_BURST_LIMIT`;
- the service unit;
- the mocked loaded value;
- another production object under test.

Use the Blue contract value as the independent oracle.

## 5. Mandatory discriminating proof

The repaired discriminant must prove:

- launcher production constant == 5;
- frozen service unit contains exactly `StartLimitBurst=5`;
- real `_effective_systemd_definition` accepts loaded 5;
- same real path rejects loaded 4.

Then independently demonstrate RED sensitivity under THREE temporary mutations:

### M1 — launcher only
production launcher constant `5 -> 4`, unit stays 5.

Expected:
`RED`.

### M2 — unit only
unit `StartLimitBurst=5 -> 4`, launcher stays 5.

Expected:
`RED`.

### M3 — simultaneous mutation
launcher constant `5 -> 4` AND unit `StartLimitBurst=5 -> 4`.

Expected:
`RED`.

M3 is mandatory.

If M3 remains green, the proof is still self-referential and the row must be
`MISSING_PROOF`.

## 6. Production immutability

Final delivery:

`PRODUCTION_CODE_CHANGED = FALSE`

Do not commit changes under:
- `src/`;
- `deploy/`;
- production test paths;
- production workflows.

Temporary mutation for discrimination is permitted only if the final committed
tree restores production bytes exactly.

## 7. Preferred changed paths

Keep changes limited to:

- `tools/p0_qualification/gate_a/fault_matrix.py`;
- `tools/p0_qualification/evidence/gate_a/fault_matrix.json`;
- `handoff/BUILDER_CODEX_P0_RESTART_BURST_PROOF_REPAIR_2026-09-21.md`.

If one additional qualification-only proof file is genuinely needed, document
why.

## 8. Matrix integrity

The matrix must remain exactly 19 rows.

No other row may change classification merely to make counts look green.

The repaired `restart_burst_limit` row may be:

`NEW_DISCRIMINATING_PROOF / NON_ISSUE`

only if all mandatory positive and mutation checks pass.

Otherwise:

`MISSING_PROOF`.

## 9. Required evidence fields

For the restart row, record at least:

- `contract_expected_value = 5`;
- observed launcher constant;
- observed unit value;
- loaded 5 accepted;
- loaded 4 rejected;
- M1 launcher-only mutation RED;
- M2 unit-only mutation RED;
- M3 simultaneous mutation RED;
- exact frozen candidate SHA;
- reproduction command;
- residual `TARGET_HOST_ONLY` physical service-manager behavior.

## 10. Validation

Run at minimum:

- `python3 -m py_compile tools/p0_qualification/gate_a/fault_matrix.py`;
- repaired fault-matrix generation;
- all three mandatory mutation falsifiers;
- relevant cited restart/lifecycle tests;
- row/count/self-consistency validation;
- two same-interpreter artifact generations and byte comparison;
- `git diff --check`;
- exact changed-path diff vs `e5c4c720...`.

Do not claim environment-independent artifact digest reproducibility.
Astra already showed the report digest is Python-build-bound.

## 11. REAL_DEFECT / MISSING_PROOF stop rule

If an actual production defect is exposed:

preserve RED evidence, classify `REAL_DEFECT`, commit audit/proof evidence, STOP.

Do not repair production.

If the independent oracle requirement cannot be satisfied:

classify `MISSING_PROOF`, preserve evidence, STOP.

## 12. Push and CI

Commit the bounded repair.

Push only:

`builder/codex-p0-hybrid-restart-burst-proof-fix-2026-09-21`

Record exact delivery SHA.

Observe exact-head CI.

Do not claim CI green until the exact delivery SHA is completed successfully.

## 13. Handoff

Create:

`handoff/BUILDER_CODEX_P0_RESTART_BURST_PROOF_REPAIR_2026-09-21.md`

Include:
- predecessor;
- delivery SHA;
- changed paths;
- independent-oracle design;
- M1/M2/M3 results;
- 19-row matrix recount;
- `MISSING_PROOF_COUNT`;
- production immutability;
- commands/results;
- CI run/status;
- next = targeted Astra recheck only.

## 14. Non-claims

Do not declare:
- P14D amendment;
- target-host readiness;
- Gate B;
- t0;
- Product integration;
- capital authorization.

## 15. Stop

After handoff + push + exact-head CI observation:

STOP.

Return control to Blue.
