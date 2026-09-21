# BLUE — RESTART BURST PROOF REPAIR RECEPTION — 2026-09-21

## 0. Status

`BLUE_RESTART_BURST_REPAIR_RECEPTION = PRELIMINARY_PASS / PENDING_EXACT_HEAD_CI`

`FINAL_INDEPENDENT_FAULT_MATRIX_REVIEW = STILL_OPEN`

`P14D_PROMOTION_READY = FALSE`

This reception is limited to Builder scope/implementation review. It does not
replace the required targeted independent Astra recheck.

## 1. Builder delivery

Branch:

`builder/codex-p0-hybrid-restart-burst-proof-fix-2026-09-21`

Mission-start SHA:

`6f0ca1d858d6937dc8199cc1690dce049ddb79a6`

Exact delivery HEAD observed by Blue:

`1fa82a75485661bf9bbb3de10b925126397dfec5`

Exact predecessor before mission dispatch:

`e5c4c720e758cd8ab3f0e04faf541b26e204be16`

Frozen production candidate remains:

`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

## 2. Scope review

Delta from predecessor contains only:

- `handoff/BUILDER_CODEX_P0_RESTART_BURST_PROOF_REPAIR_MISSION_2026-09-21.md`
- `handoff/BUILDER_CODEX_P0_RESTART_BURST_PROOF_REPAIR_2026-09-21.md`
- `tools/p0_qualification/gate_a/fault_matrix.py`
- `tools/p0_qualification/evidence/gate_a/fault_matrix.json`

No `src/`, `deploy/`, production workflow, or production test path changed.

`PRODUCTION_CODE_CHANGED = FALSE`

## 3. Independent oracle review

Blue inspected the repaired harness body.

The acceptance oracle is encoded as:

`EXPECTED_RESTART_BURST_LIMIT = 5`

with explicit provenance to:

`governance/BLUE_RESTART_BURST_PROOF_REPAIR_SPEC_2026-09-21.md#3`

The expected value is not derived from:
- launcher `RESTART_BURST_LIMIT`;
- service unit contents;
- mocked systemd output;
- another production value under test.

This closes the original self-reference design defect at the Builder
implementation level, subject to independent recheck.

## 4. Mandatory discriminants

Builder evidence reports:

- baseline launcher constant = 5;
- baseline unit `StartLimitBurst=5`;
- loaded 5 accepted;
- loaded 4 rejected;
- M1 launcher-only 5->4 = RED;
- M2 unit-only 5->4 = RED;
- M3 launcher + unit simultaneous 5->4 = RED.

Blue inspected the harness logic and confirmed that:
- launcher mutation changes the isolated loaded launcher module;
- unit mutation copies the repository unit into a disposable directory before
  editing it;
- `_effective_systemd_definition(root)` compares against the supplied isolated
  root's unit and the isolated module's current constant;
- the final pass predicate still compares both observed production values
  against the independent literal contract value 5.

Therefore M3 is structurally capable of detecting a coherent production drift
from 5 to 4 rather than following it.

## 5. Matrix integrity

Builder artifact reports:

- rows = 19;
- existing discriminating proofs = 15;
- new discriminating proofs = 4;
- missing proofs = 0;
- real defects = 0;
- non-issues = 19.

The `restart_burst_limit` row is now claimed as:

`NEW_DISCRIMINATING_PROOF / NON_ISSUE`

Physical service-manager enforcement remains correctly outside repository proof:

`TARGET_HOST_ONLY` residual.

## 6. Known evidence-quality debt preserved

This repair does not erase earlier Astra findings:

1. fault-matrix report digest remains Python-build-bound;
2. `harness_input_tree_digest` is not standalone production-byte binding.

Those remain non-blocking evidence-quality limitations.

## 7. CI state

Exact-head workflow:

`35549017908`

Current observed status at reception preparation:

`IN_PROGRESS / NO CONCLUSION`

Therefore Blue does NOT yet mark the delivery complete.

Required before dispatching targeted Astra:

`35549017908 = COMPLETED / SUCCESS`

at exact HEAD:

`1fa82a75485661bf9bbb3de10b925126397dfec5`.

## 8. Preliminary Blue disposition

Subject to exact-head CI success:

`BUILDER_RESTART_BURST_PROOF_REPAIR = PASS_FOR_TARGETED_INDEPENDENT_RECHECK`

This is not an independent certification.

## 9. Next action

After exact-head CI SUCCESS:
1. confirm branch HEAD has not moved;
2. create targeted Astra recheck branch exactly from
   `1fa82a75485661bf9bbb3de10b925126397dfec5`;
3. install the already-prepared targeted recheck mission;
4. require Astra independent M1/M2/M3 falsification and production-immutability
   confirmation;
5. return to Blue for final fault-matrix disposition.

## 10. Safety

`P14D_PROMOTION_READY = FALSE`

`TARGET_HOST_READY = FALSE`

`GATE_B_MUTATION_AUTHORIZED = FALSE`

`GATE_B = NOT_STARTED`

`t0 = NOT_DECLARED`

`REAL_CAPITAL_AUTHORIZED = FALSE`


## 11. Independent Blue artifact recount

Blue parsed the exact committed artifact at Builder delivery SHA
`1fa82a75485661bf9bbb3de10b925126397dfec5` rather than relying on Builder's
summary.

Observed:
- row count = `19`;
- unique property names = `19`;
- duplicate property names = `0`;
- `EXISTING_DISCRIMINATING_PROOF = 15`;
- `NEW_DISCRIMINATING_PROOF = 4`;
- defect classifications = `NON_ISSUE: 19`;
- restart row frozen candidate = `4d06bdbf...`;
- restart contract expected value = `5`;
- M1/M2/M3 = `true / true / true`;
- residual remains target-host physical enforcement.

`BLUE_INDEPENDENT_ARTIFACT_RECOUNT = PASS`.
