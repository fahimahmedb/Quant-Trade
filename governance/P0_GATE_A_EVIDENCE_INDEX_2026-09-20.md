# P0 Gate A Evidence Index — 2026-09-20

Purpose: preserve forensic provenance from finding -> primitive -> original red evidence -> final audit verdict -> current regression location -> retained ref. This index does not certify Gate A v3.

Canonical frozen v2 candidate: `db166fd04c681e67a2c6d4440828af14ef58c48c`.
Canonical independent v2 audit: `64b105f5a2cc1d798d1cf1e41e715b967c845a85`.
Frozen Gate A v3 candidate after Blue reception: `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`.
Blue reception: `handoff/BLUE_GATE_A_V3_RECEPTION_2026-09-20.md` => PASS_FOR_INDEPENDENT_ASTRA_REVIEW.
Independent v3 audit branch: `astra/p0-gate-a-v3-independent-audit-2026-09-20` initialized at exact frozen candidate; no audit verdict yet.

| FINDING | ORIGINAL RED / REPRODUCTION | PRIMITIVE EXERCISED | FINAL V2 AUDIT | CURRENT REGRESSION LOCATION | RETAINED REF |
|---|---|---|---|---|---|
| B1 direct reconciliation bypass | `c81fa1cdf93d5b08265c5f06ed0f4424bdda917f` | public `collector.reconcile(day)` directly | STILL_OPEN / REAL_DEFECT | `tests/test_gate_a_v3_red.py::test_direct_reconcile_before_settlement_emits_no_request` on frozen v3; direct `collector.reconcile()` preserved | `blue/p0-calendar-direct-reconcile-red-2026-09-20` |
| B3 direct manual probe bypass | `345e18d94963b4fcc7063d73d1c23aff5244ca28` | public `collector.poll()` directly | STILL_OPEN / REAL_DEFECT | `tests/test_gate_a_v3_red.py::test_direct_poll_from_unattested_process_invalidates_qualifying_window` plus direct-drain companion; do **not** substitute CLI wrapper | parent commit retained through `blue/p0-manual-probe-red-2026-09-20` |
| B3 fingerprint rematerialization provenance | manual independent reproduction documented in canonical audit | `sec-fingerprint` freeze rematerialization | STILL_OPEN / REAL_DEFECT | `tests/test_gate_a_v3_red.py::test_direct_fingerprint_rematerialization_is_not_silent` | canonical audit handoff `64b105f5...` |
| B3 cooldown mutation provenance | manual independent reproduction documented in canonical audit | `SecTrafficBudget.clear_cooldown()` | STILL_OPEN / REAL_DEFECT | `tests/test_gate_a_v3_red.py::test_direct_clear_cooldown_is_rejected_or_provenanced` plus fresh-budget/no-op-authority second-order regressions | canonical audit handoff `64b105f5...` |
| D1 omitted reconciliation | audit commit lineage from `04f84d02b9f541e65bc5a8bb5ec64e8837fcb9ca` | scheduler/audit obligation derivation with reconciliation deliberately omitted | REAL_DEFECT | `tests/test_gate_a_v3_red.py::test_omitted_due_daily_reconciliation_cannot_audit_accountable` | `astra/p0-gate-a-v2-independent-audit-2026-09-20` |
| D2 typed obligation resolution | audit branch red added before final `64b105f5...` | `audit._resolve_attempts()`; `RECONCILE` attempt against `AWAITING_POLL` obligation | REAL_DEFECT | `tests/test_gate_a_v3_red.py::test_reconcile_attempt_cannot_retire_discovery_poll_obligation` | `astra/p0-gate-a-v2-independent-audit-2026-09-20` |
| D3 raw-object referential integrity | manual independent reproduction documented in canonical audit | `store.verify_objects()` after deleting still-referenced raw object | REAL_DEFECT | `tests/test_gate_a_v3_red.py::test_missing_referenced_raw_object_fails_verification_and_audit` | canonical audit handoff `64b105f5...` |
| D4 supervisor terminal liveness | manual independent reproduction documented in canonical audit | retrospective audit after `CHILD_EXIT_OBSERVED` + `supervisor_running=False` | REAL_DEFECT | `tests/test_gate_a_v3_red.py::test_stopped_supervisor_with_pending_obligation_is_not_accountable` plus no-state terminal-event companion | canonical audit handoff `64b105f5...` |
| D5 t0 baseline lifecycle | audit commit lineage from `04f84d02b9f541e65bc5a8bb5ec64e8837fcb9ca` | `audit_observation_window(..., window_start=t0)` / structural validation | REAL_DEFECT / qualification usability | `tests/test_gate_a_v3_red.py::test_t0_between_ticks_preserves_pre_t0_baseline_lifecycle` | `astra/p0-gate-a-v2-independent-audit-2026-09-20` |

## Anti-redirection evidence

Two historical test mutations are governance evidence:

1. B1: a test originally calling raw `reconcile()` was later repointed to `reconcile_due()` on the insufficient fix path.
2. B3: commit `345e18d9...` directly calls `collector.poll()`; the later `blue/p0-manual-probe-red-2026-09-20` tip rewrote the scenario through `cli.sec_command()`.

Blue Gate A v3 reception inspected the test bodies and found the named public primitives preserved. Independent Astra must still replay them rather than relying on Blue's conclusion. A passing discriminant is invalid evidence if it no longer invokes the primitive named by the defect.

## Preservation rule

Through independent Gate A v3 Astra review:
- retain `blue/p0-calendar-direct-reconcile-red-2026-09-20`;
- retain `blue/p0-manual-probe-red-2026-09-20` so `345e18d9...` remains directly named and easy to recover;
- retain canonical Astra audit and Blue audit diary branches;
- do not delete rejected v2 or any ref required to replay original reds.

After Astra disposition, deletion may be considered only after Blue re-verifies that successor tests durably absorb the discriminants, immutable SHAs remain named here, and no unique audit/CI evidence would become hard to recover.
