# ASTRA — P0 HYBRID FAULT MATRIX INDEPENDENT REVIEW — CHECKPOINT — 2026-09-21

Role: independent Astra / Red Team reviewer.

MISSION_BRANCH = `astra/p0-hybrid-fault-matrix-independent-review-2026-09-21`

MISSION_START_HEAD = `2f6c134f1202c6e22943638379be4e3435ecded0`

CODEX_DELIVERY_SHA = `686f77a383fb0e8c7ecd1b4a737585bedb544701`

CODEX_FINAL_CHECKPOINT_HEAD = `e5c4c720e758cd8ab3f0e04faf541b26e204be16`

FROZEN_PRODUCTION_CANDIDATE = `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

ASTRA_AUDIT_FALSIFIERS_COMMIT = `b9c8afefe296b6c6c7c8d8a9c6b929e4902ccf62`

## Scope / lineage verified

- merge-base(`d4d446c...`, `686f77a...`) = exact predecessor `d4d446c412258b2a9e4792cdcd9e2442ef24b615`;
- predecessor -> Codex delivery = one commit;
- Codex delivery -> final checkpoint = one documentation-only commit;
- final checkpoint -> Astra mission start = one mission-document-only commit;
- Codex delivery adds only:
  - `tools/p0_qualification/gate_a/fault_matrix.py`;
  - `tools/p0_qualification/evidence/gate_a/fault_matrix.json`;
- Codex final checkpoint adds only:
  - `handoff/BUILDER_CODEX_P0_HYBRID_FAULT_MATRIX_CHECKPOINT_2026-09-21.md`;
- no production file under `src/`, `deploy/`, `scripts/`, existing production tests, workflow, timing/calendar/long-history harness was modified by the Codex fault-matrix delta.

F1 = PASS.

## Row completeness

All 19 required minimum properties are present exactly once by semantic property:

1. raw write
2. file fsync
3. hardlink/publication
4. directory fsync
5. envelope append
6. attempt completion
7. cursor advancement
8. successor scheduler obligation
9. cooldown persistence
10. supervisor death
11. child death
12. torn/corrupt journal
13. duplicate replay
14. state newer than journal
15. journal newer than state
16. missing fingerprint
17. foreign fingerprint
18. missing deployment authority
19. restart burst limit

Artifact counts are structurally 15 existing + 4 new = 19.

F2 = PASS.

## Existing-proof citation review

All 18 cited unittest methods resolve in the frozen candidate and their bodies were inspected, not accepted by name alone.

Current independent disposition of the 15 EXISTING_DISCRIMINATING_PROOF rows:
- raw write: NON_ISSUE;
- hardlink/publication: NON_ISSUE;
- directory fsync: NON_ISSUE;
- envelope append: NON_ISSUE;
- attempt completion: NON_ISSUE;
- cursor advancement: NON_ISSUE;
- successor scheduler obligation: NON_ISSUE;
- cooldown persistence: NON_ISSUE;
- supervisor death: NON_ISSUE;
- child death: NON_ISSUE;
- torn/corrupt journal: NON_ISSUE; cited primitive is the same `read_jsonl` used by the production SchedulerJournal path and fails closed for SEC evidence;
- duplicate replay: NON_ISSUE;
- missing fingerprint: NON_ISSUE;
- foreign fingerprint: NON_ISSUE;
- missing deployment authority: NON_ISSUE.

No stale citation found.

F3 = PASS so far.

## Four new discriminants — independent falsification

Audit-only test:
`tests/test_astra_p0_hybrid_fault_matrix_independent_review.py`

### file fsync

Independent in-memory production mutation removes the staging regular-file fsync.

Expected result: Codex discriminant must turn RED.

Observed design result: discriminant is sensitive because it requires:
- regular file fsync actually observed;
- `SecStorageFailure`;
- no published target;
- no staging residue.

Disposition:
`NON_ISSUE / FACT`.

### state newer than journal

Independent in-memory mutation makes the real collector loader accept state without checking the commit journal.

Expected result: Codex discriminant turns RED.

Disposition:
`NON_ISSUE / FACT`.

### journal newer than state

Same loader-bypass mutation causes the opposite divergence discriminant to turn RED.

Disposition:
`NON_ISSUE / FACT`.

### restart_burst_limit

Material finding.

Codex implementation:

`_restart_burst_limit_discriminant()`

constructs the accepted fixture with:

`shown(launcher.RESTART_BURST_LIMIT)`

and the rejected fixture with:

`shown(launcher.RESTART_BURST_LIMIT - 1)`.

It does not independently pin the required frozen value to 5.

Independent mutation:
`launcher.RESTART_BURST_LIMIT: 5 -> 4`.

Under that mutation the Codex discriminant still returns PASS:
- it accepts loaded value 4;
- rejects 3;
- therefore follows the mutated production constant instead of falsifying the required frozen value 5.

The paired runtime citation
`Phase4LifecycleAndWindowCampaign.test_unsolicited_zero_child_exit_cannot_cleanly_stop_qualifying_service`
patches `RESTART_BURST_LIMIT=0` only to exercise the unsolicited-child-exit guard. It does not pin or discriminate the required value 5.

Independent FACT check on the frozen production candidate confirms:
- `deploy/quant_sec_supervisor.py: RESTART_BURST_LIMIT = 5`;
- `deploy/quant-sec-capture.service: StartLimitBurst=5`.

Therefore this is not a production REAL_DEFECT. It is a proof defect.

CLASSIFICATION:
- primary: `TEST_DEFECT`;
- consequence for the Codex row under mission F6/F10: `MISSING_PROOF`;
- production: `NON_ISSUE`;
- physical service-manager restart semantics remain `TARGET_HOST_ONLY`.

This directly challenges the artifact's:
`MISSING_PROOF_COUNT = 0`.

## Artifact reproducibility / self-consistency

Audit-only tests independently regenerate the fault matrix twice in one environment, compare byte-for-byte output, recompute the embedded report digest using an independent canonical-JSON SHA-256 calculation, and check:
- row count = 19;
- proof counts = 15/4/0/0 as emitted;
- frozen candidate field = `4d06bdbf...`.

Final execution result is pending exact-head CI observation for the Astra falsifier commit.

## Provisional mission disposition

No production REAL_DEFECT has been reproduced.

Current material finding:
`restart_burst_limit = TEST_DEFECT -> MISSING_PROOF`.

Unless a separate discriminating proof already present in the Codex evidence package pins the exact required value 5 and goes RED under 5->4 mutation, the final permitted verdict will be:

`ASTRA_FAULT_MATRIX = BLOCKED_MISSING_PROOF`.

No t0, P14D amendment, Gate B, target-host readiness, or capital authority is declared.
