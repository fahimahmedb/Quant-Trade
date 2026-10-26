# Builder Codex P0 Historical Known-Bad Replay Checkpoint — 2026-09-21

## Scope and lineage

PREDECESSOR_BRANCH = `builder/codex-p0-hybrid-fault-matrix-2026-09-21`

PREDECESSOR_SHA = `e5c4c720e758cd8ab3f0e04faf541b26e204be16`

CODEX_BRANCH = `builder/codex-p0-hybrid-known-bad-replay-2026-09-21`

CODEX_DELIVERY_SHA = `a4a3700b135ebce779de8e216fa9fa6fc5fcde47`

FROZEN_PRODUCTION_CANDIDATE_SHA = `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

KNOWN_BAD_SHA = `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`

CHANGED_PATHS:

- `tools/p0_qualification/discrimination/__init__.py`
- `tools/p0_qualification/discrimination/known_bad_replay.py`
- `tools/p0_qualification/evidence/discrimination/known_bad_replay.json`
- `handoff/BUILDER_CODEX_P0_HYBRID_KNOWN_BAD_REPLAY_CHECKPOINT_2026-09-21.md`

PRODUCTION_CODE_CHANGED = `FALSE`

HISTORICAL_BRANCH_MODIFIED = `FALSE`

This bounded phase advances repository qualification evidence only. It does not
change production, deployment, scientific rules, target-host state, or capital
authority.

## Discrimination result

KNOWN_BAD_RESULT = `RED`

FROZEN_V4_RESULT = `GREEN`

DISCRIMINATING = `TRUE`

HISTORICAL_REAL_DEFECTS_REPRODUCED = `1`

FROZEN_V4_REAL_DEFECTS = `0`

TEST_DEFECTS = `0`

MISSING_PROOFS = `0`

The exact historical launcher and unit blobs were read with `git show`, written
only to a temporary directory, and loaded without checking out or changing the
historical branch. The pre-fix launcher reproduced digest movement caused solely
by transient systemd PID/timestamp/code/status observations. Frozen V4 kept the
digest stable across the same fixture and still rejected or digested a genuine
executable-path change.

The historical `REAL_DEFECT` classification is expected sensitivity evidence at
the exact pre-fix SHA. It is not a newly discovered defect in frozen V4 and does
not invoke the frozen-V4 repair stop rule.

ARTIFACT_SHA256 =
`fb36913400fdc7639cc1469a366d5543cf632e47573a028d113ecfb36cf17c13`

REPORT_DIGEST =
`sha256:63577b3dbaa0bc86654573d8bed0513acad4d924b0279ca8fbef7f2baf36ece6`

Residual proof domain: target-host physical systemd behavior remains outside this
repository replay. No repository residual remains for this discriminant.

## Commands and results

COMMANDS_RUN:

- targeted search and inspection of the Phase 8 discriminant and predecessor phase specification;
- `git diff 2da079d8... 4d06bdbf... -- deploy/quant_sec_supervisor.py`;
- `python3 -m py_compile tools/p0_qualification/discrimination/known_bad_replay.py`;
- `PYTHONPATH=. python3 -m tools.p0_qualification.discrimination.known_bad_replay`;
- two independent artifact generations with `sha256sum`;
- three exact Phase 8 unit tests;
- `PYTHONPATH=. python3 -m tools.p0_qualification.gate_a.fault_matrix`;
- `git diff --check`.

RESULTS:

- exact historical replay: PASS, expected RED reproduced;
- exact frozen V4 replay: PASS, GREEN;
- semantic-drift positive control: PASS;
- artifact reproducibility: PASS, byte-identical;
- Phase 8 unit tests: PASS, 3/3;
- Gate A fault-matrix non-regression: PASS, 19 rows, original report digest restored;
- production immutability: PASS;
- no target-host action was performed.

BASE_FAULT_MATRIX_CI_RUN_ID = `35545784230`

BASE_FAULT_MATRIX_CI_STATUS = `COMPLETED / SUCCESS` at exact SHA
`e5c4c720e758cd8ab3f0e04faf541b26e204be16`.

CI_RUN_ID = `35546505914`

CI_STATUS = `IN_PROGRESS` at exact delivery SHA
`a4a3700b135ebce779de8e216fa9fa6fc5fcde47` when this safety checkpoint
was written. No exact-head green claim is made before completion.

## Explicit non-claims

GATE_A_V4_PASS = `NOT CLAIMED_BY_BUILDER`

TARGET_HOST_READY = `NOT CLAIMED_BY_BUILDER`

P14D_AMENDMENT = `NOT CLAIMED_BY_BUILDER`

t0 = `NOT DECLARED`

REAL_CAPITAL_AUTHORIZED = `FALSE`

## Next recommended phase

The next recommended phase is Gate B target-host tooling, constrained to
READ_ONLY / PLAN / DRY_RUN by default and never run automatically from CI.
It has not been started in this checkpoint.
