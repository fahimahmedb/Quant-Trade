# Builder Codex P0 Hybrid Fault Matrix Checkpoint — 2026-09-21

## Scope and lineage

PREDECESSOR_BRANCH = `builder/p0-hybrid-qualification-harness-2026-09-20`

PREDECESSOR_SHA = `d4d446c412258b2a9e4792cdcd9e2442ef24b615`

CODEX_BRANCH = `builder/codex-p0-hybrid-fault-matrix-2026-09-21`

CODEX_DELIVERY_SHA = `686f77a383fb0e8c7ecd1b4a737585bedb544701`

CHANGED_PATHS:

- `tools/p0_qualification/gate_a/fault_matrix.py`
- `tools/p0_qualification/evidence/gate_a/fault_matrix.json`
- `handoff/BUILDER_CODEX_P0_HYBRID_FAULT_MATRIX_CHECKPOINT_2026-09-21.md`

PRODUCTION_CODE_CHANGED = `FALSE`

This bounded continuation advances repository qualification evidence for the
Control/Data Plane durability boundary. It does not itself establish economic
edge or change research, capital, runtime, deployment, or production behavior.

## Fault-matrix result

FAULT_MATRIX_ROWS = `19`

EXISTING_DISCRIMINATING_PROOF_COUNT = `15`

NEW_DISCRIMINATING_PROOF_COUNT = `4`

TARGET_HOST_ONLY_COUNT = `0`

MISSING_PROOF_COUNT = `0`

REAL_DEFECTS = `0`

TEST_DEFECTS = `0`

NON_ISSUES = `19`

The machine-readable artifact binds frozen production candidate
`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`. Its reproducible file digest is
`96d4d4561d59423a4584b3eb74b475b52ec7ec624b6a9a507867fccbb0d8f535`; its
embedded report digest is
`sha256:bc7682fe22450ad63a84df1ac8443107056c4949dc07e58ff5335e260e832d73`.

The four new harness-only discriminants cover regular-file fsync failure before
publication, state newer than journal, journal newer than state, and the exact
loaded `StartLimitBurst` binding.

RESTART_BURST_LIMIT_DISPOSITION = `NEW_DISCRIMINATING_PROOF / FACT / NON_ISSUE`.
The harness accepts exactly `StartLimitBurst=5`, rejects one below the frozen
value, and resolves and passes the existing runtime guard citation. Physical
service-manager behavior remains a target-host residual; no target-host result
is claimed here.

Residual proof domain: physical crash, filesystem, and effective systemd behavior
on the target host remain outside repository-only proof. There is no unresolved
repository fault-matrix row in this checkpoint.

## Commands run

- `git fetch origin --prune`
- `git rev-parse origin/builder/p0-hybrid-qualification-harness-2026-09-20`
- `git switch builder/codex-p0-hybrid-fault-matrix-2026-09-21`
- `python3 -m py_compile tools/p0_qualification/gate_a/fault_matrix.py`
- `PYTHONPATH=. python3 -m tools.p0_qualification.gate_a.fault_matrix`
- exact `rg` resolution of all 18 cited test methods
- `PYTHONPATH=src python3 -m unittest` with all 18 cited discriminating tests
- two independent artifact generations followed by `sha256sum`
- `git diff --check`
- `git diff --name-status d4d446c412258b2a9e4792cdcd9e2442ef24b615`
- `git commit -m "builder: add Gate A durability fault matrix"`
- `git push --set-upstream origin builder/codex-p0-hybrid-fault-matrix-2026-09-21`
- `gh run watch 35544777822 --exit-status`

## Results

- Predecessor remote invariant matched the required SHA exactly.
- Fault-matrix execution: PASS, 19/19 rows classified.
- Citation resolution: PASS, all cited tests exist.
- Targeted discriminating tests: PASS, 18/18.
- Artifact reproducibility: PASS, byte-identical digest across regeneration.
- Python compilation: PASS.
- Whitespace/error check: PASS.
- Production immutability: PASS; no existing path under `src/`, `deploy/`,
  `scripts/`, production tests, existing P0 workflow, or completed Gate A
  timing/calendar/long-history harnesses changed.
- No production `REAL_DEFECT` was found.

CI_RUN_ID = `35544777822`

CI_STATUS = `IN_PROGRESS` at exact delivery SHA
`686f77a383fb0e8c7ecd1b4a737585bedb544701`. All steps through the full unit,
SEC P0 lane, and V1 end-to-end suites were green; exact-head verification
artifact generation was still running when this safety checkpoint was written.
No final green conclusion is claimed until that exact-head run completes.

## Explicit non-claims

GATE_A_V4_PASS = `NOT CLAIMED_BY_BUILDER`

TARGET_HOST_READY = `NOT CLAIMED_BY_BUILDER`

P14D_AMENDMENT = `NOT CLAIMED_BY_BUILDER`

t0 = `NOT DECLARED`

REAL_CAPITAL_AUTHORIZED = `FALSE`

## Next recommended phase

After this bounded checkpoint is finalized and independently accepted, the next
recommended phase is historical known-bad replay. It has **not** been started by
this Builder continuation.
