# BUILDER CODEX — P0 RESTART BURST PROOF REPAIR — 2026-09-21

## Scope and lineage

- Branch: `builder/codex-p0-hybrid-restart-burst-proof-fix-2026-09-21`
- Mission start HEAD: `6f0ca1d858d6937dc8199cc1690dce049ddb79a6`
- Frozen predecessor: `e5c4c720e758cd8ab3f0e04faf541b26e204be16`
- Frozen production candidate: `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`
- Proof delivery SHA: `PENDING_SELF_REFERENCE_CUT`

This is a proof-only repair. No production behavior was changed.

## Changed paths relative to predecessor

- `handoff/BUILDER_CODEX_P0_RESTART_BURST_PROOF_REPAIR_MISSION_2026-09-21.md` (mission input already present at mission start)
- `tools/p0_qualification/gate_a/fault_matrix.py`
- `tools/p0_qualification/evidence/gate_a/fault_matrix.json`
- `handoff/BUILDER_CODEX_P0_RESTART_BURST_PROOF_REPAIR_2026-09-21.md`

No additional proof file was needed.

## Independent oracle

`EXPECTED_RESTART_BURST_LIMIT = 5` is encoded in the qualification harness with provenance to
`blue/master-v2-2026-09-20:governance/BLUE_RESTART_BURST_PROOF_REPAIR_SPEC_2026-09-21.md#3`.

It is not derived from the launcher constant, unit file, mocked loaded value, or another production object. The repaired proof:

- observes launcher `RESTART_BURST_LIMIT == 5`;
- parses exactly one unit declaration and observes `StartLimitBurst=5`;
- verifies real `_effective_systemd_definition` accepts loaded 5;
- verifies the same path rejects loaded 4;
- executes M1, M2, and M3 in isolated temporary fixtures.

## Mandatory falsifiers

- M1 launcher only, 5 -> 4, unit remains 5: `RED / PASS`
- M2 unit only, 5 -> 4, launcher remains 5: `RED / PASS`
- M3 launcher and unit, both 5 -> 4: `RED / PASS`

The row is therefore `NEW_DISCRIMINATING_PROOF / NON_ISSUE`. Physical service-manager enforcement remains `TARGET_HOST_ONLY`.

## Matrix result

- Rows: `19` exactly
- `EXISTING_DISCRIMINATING_PROOF = 15`
- `NEW_DISCRIMINATING_PROOF = 4`
- `MISSING_PROOF = 0`
- `TARGET_HOST_ONLY rows = 0`
- `REAL_DEFECT = 0`
- `TEST_DEFECT = 0`
- `NON_ISSUE = 19`

Stored counts, row recount, SHA binding, report digest, restart disposition, and required non-claims are self-consistent. Two generations under the same Python interpreter were byte-identical. No cross-interpreter digest claim is made.

## Production immutability

`PRODUCTION_CODE_CHANGED = FALSE`

Exact diff against `e5c4c720e758cd8ab3f0e04faf541b26e204be16` is empty for `src/`, `deploy/`, `scripts/`, `tests/`, and `.github/workflows/`.

Temporary mutations occurred only in disposable directories and module instances.

## Commands and results

- `python3 -m py_compile tools/p0_qualification/gate_a/fault_matrix.py` — PASS
- `PYTHONPATH=. python3 -m tools.p0_qualification.gate_a.fault_matrix` — PASS; 19 rows; 0 missing proofs; 0 real defects
- direct `_restart_burst_limit_proof()` execution — PASS; exact 5/5 observations; loaded 5 accepted; loaded 4 rejected; M1/M2/M3 RED
- structural recount/digest/non-claim validation — PASS
- two same-interpreter generations and byte comparison — PASS
- targeted Phase 4 lifecycle guard, Phase 5 restart-policy mismatch, and Phase 7 effective-unit acceptance tests — 3/3 PASS
- `git diff --check` — PASS
- exact changed-path and production-immutability checks against predecessor — PASS

## CI

- Proof delivery exact-head CI: `PENDING_AFTER_PUSH`
- A later docs-only handoff commit cannot embed its own SHA/CI run. Its exact head and CI are resolved from the branch and reported to Blue after observation.

## Non-claims

- `GATE_A_V4_REPOSITORY_DISPOSITION = NOT_REDECIDED_BY_BUILDER`
- `P14D_AMENDMENT = NOT_CLAIMED_BY_BUILDER`
- `TARGET_HOST_READY = NOT_CLAIMED_BY_BUILDER`
- `GATE_B = NOT_STARTED`
- `GATE_C = NOT_STARTED`
- `GATE_D = NOT_STARTED`
- `t0 = NOT_DECLARED`
- `REAL_CAPITAL_AUTHORIZED = FALSE`

## Next action

Targeted independent Astra recheck only: oracle independence, M1/M2/M3 sensitivity, matrix integrity, and production immutability. Then control returns to Blue.
