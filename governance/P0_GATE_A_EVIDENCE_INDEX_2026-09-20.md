# P0 Gate A Evidence Index — 2026-09-20

Purpose: preserve forensic provenance from finding -> primitive -> original red evidence -> final audit verdict -> current regression location -> retained ref. This index does not certify Gate A v3.

Canonical frozen v2 candidate: `db166fd04c681e67a2c6d4440828af14ef58c48c`.
Canonical independent audit: `64b105f5a2cc1d798d1cf1e41e715b967c845a85`.

| FINDING | ORIGINAL RED / REPRODUCTION | PRIMITIVE EXERCISED | FINAL V2 AUDIT | CURRENT REGRESSION LOCATION | RETAINED REF |
|---|---|---|---|---|---|
| B1 direct reconciliation bypass | `c81fa1cdf93d5b08265c5f06ed0f4424bdda917f` | public `collector.reconcile(day)` directly | STILL_OPEN / REAL_DEFECT | original test `test_direct_reconcile_before_settlement_emits_no_request` on retained red branch; Builder must preserve direct `reconcile()` call | `blue/p0-calendar-direct-reconcile-red-2026-09-20` |
| B3 direct manual probe bypass | `345e18d94963b4fcc7063d73d1c23aff5244ca28` | public `collector.poll()` directly | STILL_OPEN / REAL_DEFECT | original test `test_early_manual_probe_cannot_supersede_qualifying_obligation`; do **not** use branch tip rewrite to CLI wrapper | parent commit retained through `blue/p0-manual-probe-red-2026-09-20` |
| B3 fingerprint rematerialization provenance | manual independent reproduction documented in canonical audit | `sec-fingerprint` freeze rematerialization | STILL_OPEN / REAL_DEFECT | no dedicated v2-audit discriminant committed; Builder must add primitive-faithful regression | canonical audit handoff `64b105f5...` |
| B3 cooldown mutation provenance | manual independent reproduction documented in canonical audit | `SecTrafficBudget.clear_cooldown()` | STILL_OPEN / REAL_DEFECT | no dedicated v2-audit discriminant committed; Builder must add direct regression | canonical audit handoff `64b105f5...` |
| D1 omitted reconciliation | audit commit lineage from `04f84d02b9f541e65bc5a8bb5ec64e8837fcb9ca` | scheduler/audit obligation derivation with reconciliation deliberately omitted | REAL_DEFECT | `tests/test_gate_a_v2_independent_audit.py::test_omitted_due_daily_reconciliation_cannot_audit_accountable` | `astra/p0-gate-a-v2-independent-audit-2026-09-20` |
| D2 typed obligation resolution | audit branch red added before final `64b105f5...` | `audit._resolve_attempts()`; `RECONCILE` attempt against `AWAITING_POLL` obligation | REAL_DEFECT | `tests/test_gate_a_v2_red.py::test_reconcile_attempt_cannot_retire_a_discovery_poll_obligation` | `astra/p0-gate-a-v2-independent-audit-2026-09-20` |
| D3 raw-object referential integrity | manual independent reproduction documented in canonical audit | `store.verify_objects()` after deleting still-referenced raw object | REAL_DEFECT | no dedicated v2-audit discriminant committed; Builder must add durable-reference existence + rehash regression | canonical audit handoff `64b105f5...` |
| D4 supervisor terminal liveness | manual independent reproduction documented in canonical audit | retrospective audit after `CHILD_EXIT_OBSERVED` + `supervisor_running=False` | REAL_DEFECT | no dedicated v2-audit discriminant committed; Builder must add terminal/current liveness regression | canonical audit handoff `64b105f5...` |
| D5 t0 baseline lifecycle | audit commit lineage from `04f84d02b9f541e65bc5a8bb5ec64e8837fcb9ca` | `audit_observation_window(..., window_start=t0)` / structural validation | REAL_DEFECT / qualification usability | `tests/test_gate_a_v2_independent_audit.py::test_t0_between_ticks_preserves_pre_t0_lifecycle_and_supersession_context` | `astra/p0-gate-a-v2-independent-audit-2026-09-20` |

## Anti-redirection evidence

Two historical test mutations are governance evidence:

1. B1: a test originally calling raw `reconcile()` was later repointed to `reconcile_due()` on the insufficient fix path.
2. B3: commit `345e18d9...` directly calls `collector.poll()`; the later `blue/p0-manual-probe-red-2026-09-20` tip rewrote the scenario through `cli.sec_command()`.

Gate A v3 reception must inspect test bodies, not test names. A passing discriminant is invalid evidence if it no longer invokes the primitive named by the defect.

## Preservation rule

Until Builder delivery and Blue reception:
- retain `blue/p0-calendar-direct-reconcile-red-2026-09-20`;
- retain `blue/p0-manual-probe-red-2026-09-20` so `345e18d9...` remains directly named and easy to recover;
- retain canonical Astra audit and Blue audit diary branches;
- do not delete rejected v2 or any ref required to replay original reds.

After Builder delivery, deletion may be considered only after the successor tests durably absorb the discriminants **and** this provenance index continues to name immutable SHAs.
