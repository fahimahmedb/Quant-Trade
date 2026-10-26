# BLUE — RESTART BURST PROOF REPAIR SPECIFICATION — 2026-09-21

## 0. Decision

`BLUE_DECISION = REPAIR_PROOF_ONLY`

`PRODUCTION_CHANGE_AUTHORIZED = FALSE`

`P14D_PROMOTION_READY = FALSE`

`GATE_B = NOT_STARTED`

`t0 = NOT_DECLARED`

This specification responds to the independent Astra finding on the Codex
Gate-A fault matrix.

Frozen production candidate remains:

`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

No production REAL_DEFECT was reproduced.

The required repair is limited to evidence/test machinery.

## 1. Independent finding

Astra final review branch:

`astra/p0-hybrid-fault-matrix-independent-review-2026-09-21`

Current reviewed HEAD at specification time:

`c6be804e99e409ab36a455f09ea2fccbe3d88252`

Independent verdict:

`ASTRA_FAULT_MATRIX = BLOCKED_MISSING_PROOF`

Unresolved repository proof row:

`restart_burst_limit`

Astra classification:

- production property: `NON_ISSUE / FACT`;
- Codex helper: `TEST_DEFECT`;
- consequence: `MISSING_PROOF`;
- target-host physical restart enforcement remains `TARGET_HOST_ONLY`.

## 2. Exact defect in the proof

Current helper derives its expected accepted value from:

`launcher.RESTART_BURST_LIMIT`

and its rejected value from:

`launcher.RESTART_BURST_LIMIT - 1`.

Therefore a temporary production-constant mutation:

`5 -> 4`

changes both the implementation and the helper's oracle.

The helper stays green.

That is insufficient discriminating power for the required proof row.

## 3. Normative independent contract

For the exact frozen V4 candidate under this Gate-A qualification:

`EXPECTED_RESTART_BURST_LIMIT = 5`

This value is a Blue acceptance contract for this proof repair.

The proof oracle MUST NOT be derived from:
- `launcher.RESTART_BURST_LIMIT`;
- the loaded systemd value;
- the unit file being tested;
- any other production value under test.

The proof may encode the literal expected value `5`, with provenance to this
Blue specification.

## 4. Required repaired discriminant

The repaired repository proof must independently establish ALL of:

1. production constant equals exactly `5`;
2. frozen service unit declares exactly `StartLimitBurst=5`;
3. real `_effective_systemd_definition` path accepts loaded value `5`;
4. same real path rejects loaded value `4`;
5. temporary launcher constant mutation `5 -> 4` makes the discriminant RED;
6. temporary unit-file value mutation `5 -> 4` makes the discriminant RED;
7. temporary simultaneous mutation of BOTH launcher constant and unit value
   `5 -> 4` still makes the discriminant RED because the acceptance oracle is
   independent and remains `5`.

The last condition is mandatory. It proves the repair is not merely moving the
self-reference from one production source to another.

## 5. Mutation discipline

Mutations must be temporary, isolated test/harness mutations.

Do not commit any production change.

Allowed mutation mechanisms include:
- monkeypatch;
- temporary copied module/unit fixture;
- temporary worktree/file restoration that leaves the final tree unchanged.

Final delivery must satisfy:

`PRODUCTION_CODE_CHANGED = FALSE`

and no existing production path may differ from predecessor.

## 6. Allowed changed paths

Preferred bounded paths:

- `tools/p0_qualification/gate_a/fault_matrix.py`;
- `tools/p0_qualification/evidence/gate_a/fault_matrix.json`;
- Builder mission/checkpoint/handoff for this repair.

A narrowly-scoped proof test under a qualification/audit-only path is allowed
only if necessary.

Do not modify:
- `src/`;
- `deploy/`;
- production tests;
- production workflows;
- frozen branches;
- Astra branches;
- target host.

## 7. Artifact requirements

The repaired matrix must still contain exactly the same 19 required properties.

For `restart_burst_limit`, the row must report:

`NEW_DISCRIMINATING_PROOF`

only if the independent mutation tests above pass.

The row must record:
- Blue contract value `5`;
- production constant observed;
- unit-file value observed;
- loaded-5 acceptance;
- loaded-4 rejection;
- launcher-only mutation red result;
- unit-only mutation red result;
- simultaneous launcher+unit mutation red result;
- residual target-host domain.

If any required mutation remains green:

`MISSING_PROOF`

and the mission stops without laundering the row into PASS.

## 8. Required validation

At minimum:

- Python compile of changed harness;
- repaired fault-matrix generation;
- targeted current-candidate test;
- launcher-only 5->4 falsifier;
- unit-only 5->4 falsifier;
- simultaneous launcher+unit 5->4 falsifier;
- all cited restart-related existing tests;
- full fault-matrix self-consistency/recount;
- artifact reproducibility under the same interpreter build;
- `git diff --check`;
- exact changed-path check against predecessor;
- exact-head CI after push.

Do not rerun unrelated expensive campaigns unless the changed scope or CI
requires them.

## 9. Stop conditions

If the repaired proof exposes an actual frozen-candidate production failure:

`REAL_DEFECT`

Preserve evidence and STOP.

Do not repair production in this mission.

If the proof cannot be made independently discriminating without production
changes:

`MISSING_PROOF`

Preserve evidence and STOP.

## 10. Required Builder handoff

Create:

`handoff/BUILDER_CODEX_P0_RESTART_BURST_PROOF_REPAIR_2026-09-21.md`

Include:
- predecessor SHA;
- delivery SHA;
- exact changed paths;
- proof-oracle provenance;
- all three mutation results;
- matrix counts;
- production-immutability result;
- commands/results;
- exact-head CI run/status;
- next action = targeted independent Astra recheck.

## 11. Explicit non-claims

Builder must retain:

`GATE_A_V4_REPOSITORY_DISPOSITION = NOT_REDECIDED_BY_BUILDER`

`P14D_AMENDMENT = NOT_CLAIMED_BY_BUILDER`

`TARGET_HOST_READY = NOT_CLAIMED_BY_BUILDER`

`GATE_B = NOT_STARTED`

`t0 = NOT_DECLARED`

`REAL_CAPITAL_AUTHORIZED = FALSE`

## 12. Next independent step

After Builder delivery and exact-head CI:

Astra performs a targeted independent recheck of ONLY:
- restart-burst oracle independence;
- 5->4 launcher mutation sensitivity;
- 5->4 unit mutation sensitivity;
- simultaneous 5->4 mutation sensitivity;
- matrix count/row classification integrity;
- production immutability.

Astra must not re-audit the entire V4 correction unless new contradictory
evidence appears.
