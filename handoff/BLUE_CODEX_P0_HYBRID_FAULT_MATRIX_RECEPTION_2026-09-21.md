# BLUE — CODEX P0 HYBRID FAULT MATRIX RECEPTION — 2026-09-21

## 0. Disposition

`BLUE_CODEX_FAULT_MATRIX_RECEPTION = PASS_FOR_INDEPENDENT_REVIEW`

This is not an independent certification and does not amend P14D.

## 1. Lineage

Predecessor:
`builder/p0-hybrid-qualification-harness-2026-09-20@d4d446c412258b2a9e4792cdcd9e2442ef24b615`

Codex delivery commit:
`686f77a383fb0e8c7ecd1b4a737585bedb544701`

Codex final checkpoint HEAD:
`e5c4c720e758cd8ab3f0e04faf541b26e204be16`

The final HEAD is exactly one documentation-only commit ahead of the delivery commit.

Changed paths across the bounded mission:
- `tools/p0_qualification/gate_a/fault_matrix.py`
- `tools/p0_qualification/evidence/gate_a/fault_matrix.json`
- `handoff/BUILDER_CODEX_P0_HYBRID_FAULT_MATRIX_CHECKPOINT_2026-09-21.md`

No production path changed.

## 2. Exact-head CI

Delivery SHA:
`686f77a383fb0e8c7ecd1b4a737585bedb544701`

Run:
`35544777822 = COMPLETED / SUCCESS`

Final checkpoint HEAD:
`e5c4c720e758cd8ab3f0e04faf541b26e204be16`

Run:
`35545784230 = COMPLETED / SUCCESS`

## 3. Fault-matrix result received

`FAULT_MATRIX_ROWS = 19`

`EXISTING_DISCRIMINATING_PROOF_COUNT = 15`

`NEW_DISCRIMINATING_PROOF_COUNT = 4`

`MISSING_PROOF_COUNT = 0`

`REAL_DEFECTS = 0`

`TEST_DEFECTS = 0`

`NON_ISSUES = 19`

New harness discriminants cover:
- file fsync failure before publication;
- state newer than journal;
- journal newer than state;
- restart burst limit / loaded StartLimitBurst binding.

## 4. restart_burst_limit

Received disposition:

`NEW_DISCRIMINATING_PROOF / FACT / NON_ISSUE`

Repository-side evidence:
- exact loaded value 5 accepted;
- one-below value rejected;
- paired runtime guard citation resolves.

Residual:
physical service-manager behavior remains `TARGET_HOST_ONLY`.

Blue accepts this as a valid repository-side proof claim for independent review.
It is not target-host proof.

## 5. Artifact binding

Machine-readable artifact:
`tools/p0_qualification/evidence/gate_a/fault_matrix.json`

Frozen production candidate bound inside artifact:
`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Embedded report digest:
`sha256:bc7682fe22450ad63a84df1ac8443107056c4949dc07e58ff5335e260e832d73`

Production code changed:
`FALSE`

## 6. Blue inspection result

Blue verified:
- predecessor ancestry;
- bounded changed-path scope;
- final checkpoint is docs-only over the delivery;
- exact-head CI success on both delivery and final checkpoint;
- machine-readable artifact binds the exact frozen v4 candidate;
- all 19 rows carry explicit residual proof domains;
- physical crash/filesystem/systemd behavior is not falsely claimed repository-side;
- no P14D/t0/target-host/capital claim is made.

No obvious governance contradiction was found in reception.

## 7. Independent-review requirement

Because this evidence was authored by Builder/Codex and is intended to close a
promotion blocker for a major governance amendment, Blue requires one independent
review before using it as final amendment evidence.

Independent review should focus on:
- discriminating power of the four new harness checks;
- correctness of the 15 cited existing proofs;
- stale/wrong-target citations;
- correctness of `MISSING_PROOF_COUNT = 0`;
- whether any row should instead be `TARGET_HOST_ONLY`;
- whether `restart_burst_limit` is honestly closed repository-side;
- whether production code truly remains unchanged.

Until that review:

`P14D_PROMOTION_READY = FALSE`

## 8. Safety state

`GATE_A_V4_REPOSITORY_DISPOSITION = PASS`

`TARGET_HOST_READY = FALSE`

`GATE_B = NOT_STARTED`

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

`t0 = NOT DECLARED`

`REAL_CAPITAL_AUTHORIZED = FALSE`
