# ASTRA — P0 RESTART-BURST PROOF RECHECK — 2026-09-21

## 0. Final disposition

`ASTRA_RESTART_BURST_RECHECK = PASS_REPOSITORY_EVIDENCE`

This disposition closes only the previously unresolved repository-side proof row:

`restart_burst_limit`

It does not promote the hybrid amendment, declare target-host readiness, start Gate B, declare t0, start Product integration, or authorize capital.

## 1. Exact authorities and lineage

Repository:

`fahimahmedb/Quant-Trade`

Astra branch:

`astra/p0-restart-burst-proof-recheck-2026-09-21`

Exact Builder delivery reviewed:

`1fa82a75485661bf9bbb3de10b925126397dfec5`

Builder branch remains exactly at that SHA at finalization.

Astra authoritative audit input HEAD before this final handoff commit:

`5f9b65d61d69ca32ddfab117502f264e2a72b2d8`

That Astra HEAD is exactly two audit/governance commits ahead of the Builder SHA and zero commits behind it. The only cumulative Astra file delta above Builder before this final handoff is:

- `handoff/ASTRA_P0_RESTART_BURST_PROOF_RECHECK_MISSION_2026-09-21.md`

The commit containing this handoff cannot truthfully embed its own SHA. Resolve the live branch HEAD after this file is pushed; that resulting commit is the final Astra delivery HEAD and is bound externally together with its exact-head CI result.

Immutable Blue acceptance authority:

- commit: `7d7bf6a27e4560951ec0fad58b69a99edf091a4b`
- exact spec blob: `e73013605c8e169a580aa1cd082f477bc5cd5722`
- file: `governance/BLUE_RESTART_BURST_PROOF_REPAIR_SPEC_2026-09-21.md`
- normative value: `EXPECTED_RESTART_BURST_LIMIT = 5`

The current `blue/master-v2-2026-09-20` copy resolves to the same exact blob. The moving branch name is not used as normative acceptance authority.

## 2. A1 — lineage / scope

Result:

`A1 = PASS / NON_ISSUE`

The Builder delivery descends exactly from the intended proof-repair predecessor. Relative to predecessor `e5c4c720e758cd8ab3f0e04faf541b26e204be16`, the bounded repair changes only:

- `handoff/BUILDER_CODEX_P0_RESTART_BURST_PROOF_REPAIR_2026-09-21.md`
- `handoff/BUILDER_CODEX_P0_RESTART_BURST_PROOF_REPAIR_MISSION_2026-09-21.md`
- `tools/p0_qualification/evidence/gate_a/fault_matrix.json`
- `tools/p0_qualification/gate_a/fault_matrix.py`

No production change was introduced by the repair.

Classification:

`NON_ISSUE`

## 3. A2 — oracle independence

Result:

`A2 = PASS / NON_ISSUE`

The repaired harness pins:

`EXPECTED_RESTART_BURST_LIMIT = 5`

as an explicit Blue acceptance contract.

The expected value is not derived from:

- `launcher.RESTART_BURST_LIMIT`;
- the service unit contents;
- the mocked loaded systemd value;
- another production value under test.

The immutable Blue commit/blob pair above independently fixes the acceptance value at 5.

Classification:

`NON_ISSUE`

## 4. A3 — baseline current-candidate proof

Result:

`A3 = PASS / NON_ISSUE`

Independent repository inspection confirms:

- launcher `RESTART_BURST_LIMIT = 5`;
- unit contains exactly one `StartLimitBurst=5` declaration;
- the real `_effective_systemd_definition` validation path accepts mocked loaded value 5 against the exact unit fixture;
- the same validation path rejects loaded value 4 with the expected StartLimitBurst mismatch.

No production defect was reproduced.

Classification:

`NON_ISSUE`

## 5. A4 — M1 launcher-only mutation

Temporary isolated mutation:

- launcher: `5 -> 4`
- unit remains: `5`

Observed result:

`M1 = RED`

The repaired discriminant fails because the independent contract remains 5 while the observed launcher constant is 4.

Classification:

`NON_ISSUE / DISCRIMINATING_PROOF_CONFIRMED`

## 6. A5 — M2 unit-only mutation

Temporary disposable unit mutation:

- launcher remains: `5`
- unit: `StartLimitBurst=5 -> StartLimitBurst=4`

Observed result:

`M2 = RED`

The repaired discriminant fails while the independent acceptance contract remains 5.

Classification:

`NON_ISSUE / DISCRIMINATING_PROOF_CONFIRMED`

## 7. A6 — M3 simultaneous mutation — critical

Temporary isolated simultaneous mutation:

- launcher: `5 -> 4`
- unit: `5 -> 4`

Observed result:

`M3 = RED`

This is the critical anti-self-reference result. Even when both production sources under test move together to 4, the discriminant remains RED because the acceptance oracle stays independently fixed at 5.

Therefore the prior circular-oracle defect is closed.

Classification:

`NON_ISSUE / DISCRIMINATING_PROOF_CONFIRMED`

## 8. A7 — matrix integrity

Result:

`A7 = PASS / NON_ISSUE`

Independent recount of the committed repaired matrix:

- exact rows: `19`
- unique property names: `19`
- duplicate properties: `0`
- missing properties: `0`
- added/renamed-away properties: `0`
- `EXISTING_DISCRIMINATING_PROOF = 15`
- `NEW_DISCRIMINATING_PROOF = 4`
- `MISSING_PROOF = 0`
- `TARGET_HOST_ONLY rows = 0`
- `NON_ISSUE = 19`
- `REAL_DEFECT = 0`

Stored counts match the independent recount.

The 18 non-`restart_burst_limit` rows are byte-structurally unchanged as row objects between the repair predecessor artifact and the repaired Builder artifact. No unrelated row was altered to launder classification counts.

The only material proof change is the repaired `restart_burst_limit` evidence.

Classification:

`NON_ISSUE`

## 9. A8 — preserved evidence debt

Result:

`A8 = PASS_WITH_DURABLE_LIMITATIONS`

The prior independent evidence limitations remain in force and are not overclaimed:

1. `report_digest` reproducibility is interpreter-build-bound because Python version metadata participates in the hashed payload. Same-interpreter reproducibility does not prove cross-Python-build digest stability.

2. `harness_input_tree_digest` is not accepted as a standalone complete proof that every production byte exercised by the harness is bound into that digest.

These remain evidence-precision limitations, not reproduced frozen-candidate production defects. Exact Git lineage and production-immutability checks provide the independent repository binding used in this recheck.

Classification:

`TEST_DEFECT / NON_BLOCKING_EVIDENCE_PRECISION`

## 10. A9 — production immutability

Result:

`A9 = PASS / NON_ISSUE`

Relative to the intended Builder predecessor, the proof repair contains no change under:

- `src/`
- `deploy/`
- `tests/`
- `.github/workflows/`

No production fix was made by Builder or Astra in this mission.

`PRODUCTION_CODE_CHANGED = FALSE`

Classification:

`NON_ISSUE`

## 11. A10 — exact-head Builder CI

Result:

`A10 = PASS`

Authoritative selected Builder delivery run:

`35549017908`

Exact SHA:

`1fa82a75485661bf9bbb3de10b925126397dfec5`

Final observed state:

`COMPLETED / SUCCESS`

This exact run is used as the Builder delivery CI authority.

Supplementary same-SHA run:

`35549509130 = COMPLETED / SUCCESS`

It is corroborating evidence only and was not substituted for the selected Builder run.

No same-SHA contradictory failure was observed.

## 12. Classification summary

### REAL_DEFECT

None reproduced.

### TEST_DEFECT

The prior circular restart-burst proof defect is repaired.

Residual non-blocking evidence-precision debt remains for:

- cross-Python-build report digest reproducibility;
- `harness_input_tree_digest` as standalone complete production-byte proof.

### MISSING_PROOF

None remains for the targeted repository-side `restart_burst_limit` row.

### TARGET_HOST_ONLY

Repository PASS does not prove physical target-host behavior. Residual scope still includes:

- actual loaded systemd configuration on the target host;
- physical service-manager restart-burst enforcement;
- runtime package/image behavior;
- deployed filesystem behavior;
- crash/power-loss ordering and persistence semantics;
- reboot/mount/state-root behavior;
- any other target-host entrance requirement already defined by governance.

### NON_ISSUE

The repaired repository proof for `restart_burst_limit` is independently discriminating under M1, M2 and M3, and the frozen production candidate itself remains consistent with the exact value 5.

## 13. Final targeted verdict

`ASTRA_RESTART_BURST_RECHECK = PASS_REPOSITORY_EVIDENCE`

Meaning:

- the prior repository-side `restart_burst_limit` missing-proof blocker is closed;
- no production REAL_DEFECT was reproduced;
- exact Builder delivery CI is successful;
- production remains unchanged;
- target-host physical enforcement remains outside this verdict.

This PASS does not itself authorize any later gate or promotion.

## 14. Explicit non-claims

- `HYBRID_EVENT_BASED_V1 = NOT_PROMOTED_BY_ASTRA`
- `GATE_B = NOT_STARTED`
- `t0 = NOT_DECLARED`
- `PRODUCT_INTEGRATION = NOT_STARTED`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `TARGET_HOST_READY = NOT_DECLARED`

Next authority:

`RETURN_CONTROL_TO_BLUE`
