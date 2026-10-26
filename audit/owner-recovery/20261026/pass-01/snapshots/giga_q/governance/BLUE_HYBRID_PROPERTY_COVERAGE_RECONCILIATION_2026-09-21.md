# BLUE — HYBRID PROPERTY-COVERAGE RECONCILIATION — 2026-09-21

## 0. Status

`HYBRID_PROPERTY_COVERAGE_RECONCILIATION = PASS_CONTENT_LEVEL / PENDING_FINAL_ASTRA_ACCEPTANCE`

This document answers one question only:

> Does the proposed `HYBRID_EVENT_BASED_V1` method omit any property that the
> current 19-row Gate-A durability/fault matrix requires?

Answer:

`NO_PROPERTY_OMISSION_FOUND`

This is a content/method reconciliation. It does not close the currently open
restart-burst independent-proof gate.

## 1. Inputs

Frozen production candidate:

`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Builder repaired fault matrix:

`builder/codex-p0-hybrid-restart-burst-proof-fix-2026-09-21@1fa82a75485661bf9bbb3de10b925126397dfec5`

Candidate amendment:

`governance/BLUE_P14D_HYBRID_AMENDMENT_CANDIDATE_V2_2026-09-21.md`

Final P14D method Red Team:

`governance/BLUE_P14D_FINAL_RED_TEAM_2026-09-21.md`

## 2. Exact 19-row reconciliation

| Fault-matrix property | Hybrid-method coverage | Residual domain |
| --- | --- | --- |
| before_after_raw_write | Gate A filesystem publication/durability fault proof | target-host physical crash/filesystem |
| before_after_file_fsync | Gate A filesystem publication/durability fault proof | target-host physical crash/filesystem |
| before_after_hardlink_publication | Gate A filesystem publication logic | target-host physical crash/filesystem |
| before_after_directory_fsync | Gate A filesystem publication/durability fault proof | target-host physical crash/filesystem |
| before_after_envelope_append | Gate A durability fault matrix / one-obligation-one-resolution | target-host physical crash/filesystem |
| before_after_attempt_completion | Gate A durability fault matrix / attempt accountability | target-host physical crash/runtime |
| before_after_cursor_advancement | Gate A durability fault matrix / acquisition continuity | target-host physical crash/runtime |
| before_after_successor_scheduler_obligation | Gate A scheduler obligations + long-history one-obligation-to-one-resolution | target-host physical crash/runtime |
| before_after_cooldown_persistence | Gate A backoff/cooldown semantics | target-host physical crash/runtime |
| supervisor_death | Gate A crash/restart boundaries | Gate B real service-manager/process boundary |
| child_death | Gate A crash/restart boundaries | Gate B real service-manager/process boundary |
| corrupt_torn_journal_tail | Gate A durability fault matrix / malformed-truncated durable state | target-host physical crash/filesystem |
| duplicate_replay | Gate A long-history one-obligation-to-one-resolution | target-host runtime |
| state_newer_than_journal | Gate A durability fault matrix / divergent durable-state falsification | target-host physical crash/filesystem |
| journal_newer_than_state | Gate A durability fault matrix / divergent durable-state falsification | target-host physical crash/filesystem |
| missing_fingerprint | Gate A fingerprint/integrity/firewall semantics | Gate B materialized/runtime fingerprint binding |
| foreign_fingerprint | Gate A fingerprint/integrity/firewall semantics | Gate B materialized/runtime fingerprint binding |
| missing_deployment_authority | Gate A lifecycle/deployment authority falsification | Gate B one-use real deployment authority |
| restart_burst_limit | Gate A crash/restart boundary + exact independent contract | Gate B physical systemd restart-burst enforcement |

## 3. Coverage conclusion

All 19 rows are represented by the candidate amendment's explicit Gate-A
requirements:

- scheduler obligations and timing boundaries;
- backoff/cooldown semantics;
- crash/restart boundaries;
- filesystem publication logic;
- malformed/truncated/error states;
- long-history one-obligation-to-one-resolution;
- fingerprint/integrity/firewall semantics;
- complete durability fault matrix.

The remaining physical residuals are not silently dropped. They are explicitly
carried into Gate B by the amendment's requirements for:

- immutable exact release;
- persistent state mount;
- filesystem semantics;
- loaded systemd/effective values;
- runtime/interpreter identity;
- active == materialized fingerprint;
- accountable stop/start, child failure, supervisor death and reboot;
- no unexplained pre-seeded authority/state.

Therefore:

`HYBRID_METHOD_OMITS_CURRENT_FAULT_MATRIX_PROPERTY = FALSE`

## 4. Fixed-P14D unique-property check

The final Blue method Red Team already recorded:

`FIXED_P14D_UNIQUE_SPECIFIC_ACCEPTANCE_PROPERTY = NONE_FOUND`

This reconciliation found no contradiction to that result.

The hybrid rule does not claim elapsed time is worthless; residual passive-time
value remains preserved by post-qualification surveillance.

## 5. Restart-burst caveat

The repaired matrix currently reports:

`restart_burst_limit = NEW_DISCRIMINATING_PROOF / NON_ISSUE`

but that classification is not final Blue authority until:

1. selected Builder exact-head CI succeeds;
2. targeted Astra independently reproduces M1/M2/M3;
3. Blue receives Astra and closes the final fault-matrix disposition.

Thus this document closes **method coverage**, not the independent proof gate.

## 6. Checklist effect

The following can now be treated as prepared/closed at content level:

- candidate amendment reconciled with final Builder fault-matrix classifications;
- no current 19-row Gate-A property omitted by the hybrid rule;
- atomic current-state updates prepared via
  `governance/BLUE_HYBRID_PROMOTION_ATOMIC_DRY_RUN_2026-09-21.md`.

Still open:
- selected Builder repair exact-head CI;
- targeted Astra recheck;
- reconciliation with Astra final findings;
- Blue final fault-matrix disposition;
- execution of the atomic promotion transaction.

## 7. Safety

`P14D_PROMOTION_READY = FALSE`

`GATE_B_MUTATION_AUTHORIZED = FALSE`

`GATE_B = NOT_STARTED`

`t0 = NOT_DECLARED`

`REAL_CAPITAL_AUTHORIZED = FALSE`
