# ASTRA Gate A v2 independent audit checkpoint — 2026-09-20

## Authority and frozen object

FACT

- Repo: `fahimahmedb/Quant-Trade`
- Owner checkpoint: `7261220a9dc60736ed71b3e66030e4c58eb29c6e`
- Frozen candidate: `blue/p0-gate-a-v2-final-2026-09-20`
- Candidate SHA: `db166fd04c681e67a2c6d4440828af14ef58c48c`
- Candidate exact-head CI: `35504152951 = COMPLETED / SUCCESS`
- Astra baseline: `643deacdf5bbbdb1d2410c762eb20f72aff16bbf`
- Rejected v1: `19b6069e485c2e619698e235d24a6110556b1865`
- Independent red proof branch: `astra/p0-gate-a-v2-independent-audit-2026-09-20`
- Independent red proof SHA: `04f84d02b9f541e65bc5a8bb5ec64e8837fcb9ca`
- Independent red CI: `35506706067 = COMPLETED / FAILURE`

The candidate branch still pointed exactly to `db166fd...` when rechecked. Candidate -> red proof changes only `STATE.md` proof count plus `tests/test_gate_a_v2_independent_audit.py`; no candidate production source was modified.

North Star, `handoff/ASTRA_P0_CHECKPOINT.md`, and `governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md` were read before this verdict.

## Prior v1 blocker families

The same independent red run executed the candidate regressions and they passed:

- B1: direct and real-CLI early reconciliation are rejected; oldest-due ordering passes.
- B2: an offline auditor cannot downgrade durable qualifying external authority validation.
- B3: an early manual sec-probe cannot silently supersede the qualifying obligation.

VERDICTS

`B1_DIRECT_RECONCILE = CLOSED`

`B2_OFFLINE_AUDIT_AUTHORITY = CLOSED`

`B3_MANUAL_OPERATOR_INTERVENTION = CLOSED`

These are narrow regression closures, not a Gate A certification.

## New finding A — omitted due reconciliation false-passes

CLASSIFICATION: `REAL_DEFECT`

Independent discriminant:
`test_omitted_due_daily_reconciliation_cannot_audit_accountable`

Scenario: qualifying collector; normal start; normal discovery/acquisition; then 44 virtual hours of normal discovery polls every 60 seconds with daily reconciliation deliberately omitted. No scheduler-journal edit and no fabricated reconciliation state.

At the end production `reconciliation_due()` says source day `2026-09-18` is due, while retrospective audit returns `accountable=True` and `findings=[]`.

Exact CI failure:

`AssertionError: True is not false ... due=2026-09-18, findings=[]`

FACT: `reconciliation_due()` derives the duty independently from bootstrap time + EDGAR calendar + settlement. But `audit.py` derives expected obligations from scheduler transitions carrying `next_due_at_utc`. The reconciliation transition is emitted only after reconciliation executes. If the action is omitted entirely, the retrospective auditor has no reconciliation obligation to reconcile.

INFERENCE: this is an active proof false-pass, not merely missing evidence.

## New finding B — t0 between ticks loses boundary context

CLASSIFICATION: `REAL_DEFECT`

Independent discriminant:
`test_t0_between_ticks_preserves_pre_t0_lifecycle_and_supersession_context`

The service first audits accountable without slicing. t0 is then placed midway between normal 60-second ticks and the next normal poll executes.

The sliced audit fails with exactly:

`['LIFECYCLE_PROVENANCE_MISSING', 'NONPROSPECTIVE_SUPERSESSION', 'SUPERSESSION_TARGET_UNKNOWN']`

FACT: with `window_start`, audit filters lifecycle rows to at/after t0, computes a pre-t0 baseline separately, but supplies that baseline only to external-authority validation, not structural validation. Also a carried-in successor transition can reference a predecessor obligation excluded by the slice.

FACT: the qualifying deployment contract allows bounded pre-t0 rodage followed by Blue's later t0 decision; it does not require a relaunch exactly at t0.

INFERENCE: this is a real observation-window defect. It fails closed rather than false-passing, but prevents a supported already-running qualifying service from being audited correctly.

## Red-harness issue separated from candidate

CLASSIFICATION: `TEST_DEFECT`

An earlier version directly imported a TestCase helper, causing unittest to rediscover inherited tests and generated status to report 406 instead of the intended 398. The helper import was corrected. On proof run `35506706067`, status freshness passed, 398 tests ran, and exactly the two intended independent discriminants failed.

## Formal verdict

`AUDIT_GATE_A_V2 = BLOCKED`

`REPO_GATE_A_MUST_REOPEN`

The full red proof run reports `Ran 398 tests` and `FAILED (failures=2)`; the other 396 tests pass.

Hard flags remain:

- `t0 = NOT DECLARED`
- `P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`
- `P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- target-host Gate B is not proven.

## Next governance step

RECOMMENDATION

Use the owner-defined flow:
`finding -> Blue decision -> specification -> Builder -> independent review / Red Team -> Blue decision`.

Do not patch the frozen candidate in place. A successor should make daily reconciliation omission independently detectable and preserve the minimal lifecycle plus predecessor-obligation context across `window_start`. Re-run exact-head CI and independent red review on the successor SHA before Gate A closure.

UNKNOWN

This repository audit does not establish target-host runtime behavior, live continuity, P14D evidence, scientific/economic validity, or capital readiness.
