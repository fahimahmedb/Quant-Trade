# BUILDER GATE A V3 CHECKPOINT — 2026-09-20

BASE_SHA = db166fd04c681e67a2c6d4440828af14ef58c48c
CURRENT_BRANCH = builder/p0-gate-a-v3-2026-09-20
CURRENT_HEAD = resolve origin/builder/p0-gate-a-v3-2026-09-20; a commit cannot truthfully contain its own SHA
SURFACE_1 = IMPLEMENTED_PENDING_REGRESSION_CI
SURFACE_2 = IMPLEMENTED_PENDING_REGRESSION_CI
SURFACE_3 = IMPLEMENTED_PENDING_REGRESSION_CI; DIRECT_RECONCILE_POLL_DRAIN_FIDELITY_RETAINED
SURFACE_4 = IMPLEMENTED_PENDING_REGRESSION_CI; TERMINAL_EVENT_WITHOUT_STATE_FIX_AT_bccd9420
SURFACE_5 = IMPLEMENTED_PENDING_REGRESSION_CI
SURFACE_6 = IMPLEMENTED_PENDING_REGRESSION_CI
SURFACE_7 = IMPLEMENTED_PENDING_REGRESSION_CI; FORGED_BUDGET_CALLBACK_FIX_AT_6fc9f10d
B2_REGRESSION = CLOSED_IN_BASE; MUST_REMAIN_GREEN
FOCUSED_TESTS = NEW_ADVERSARIAL_CASES_PUSHED; EXACT_HEAD_CI_PENDING
FULL_SUITE = EXACT_HEAD_CI_PENDING
CI = PENDING_ON_CURRENT_DELIVERED_HEAD
KNOWN_BLOCKERS = NONE_KNOWN; FORGED_QUALIFYING_PROCESS_FIX_PENDING_EXACT_HEAD_CI
NEXT_ACTION = Inspect exact-head CI for 7c54516d...; fix only reproduced regressions; if green, write final Builder handoff and require CI again on the delivered handoff HEAD.

## Red integrity matrix

- B1 calls public collector.reconcile() directly.
- B3 poll calls public collector.poll() directly from an unattested process identity.
- B3 drain calls public collector.drain() directly from an unattested process identity.
- D1 keeps discovery polls healthy for 44 virtual hours while deliberately omitting reconciliation.
- D2 calls public collector.reconcile() at a discovery obligation deadline and requires action-kind binding.
- D3 deletes a raw object still named by the durable raw manifest.
- D4 records durable child exit plus supervisor_running=false while an obligation remains pending.
- D5 places prospective t0 between service ticks and requires pre-window baseline lifecycle context.
- S7 fingerprint calls public materialize_fingerprint() directly after deleting the freeze.
- S7 cooldown calls public SecTrafficBudget.clear_cooldown() directly.

No test above is redirected to a CLI or safer wrapper.


## Current durable implementation milestones

- 8609aaa0: primitive RED set added from frozen v2 base.
- 3fe5b805 / 1c497244: typed obligations, due-reconciliation proof, raw-integrity/lifecycle/mutation-boundary implementation and legacy compatibility work.
- 7d11e812 / a550da04: D1 fidelity restored; fresh/unbound budget mutation made fail-closed.
- f287f74f: added second-order attacks for terminal event evidence and forged public budget authority binding.
- 6fc9f10d: arbitrary/no-op budget callback no longer installs mutation authority.
- bccd9420: current-child terminal exit is consumed even when supervisor_state.json is absent.

These are implementation facts only, not a Gate A verdict.


## Second-order mutation-authority hardening

- 7b56a064: reproduced a forged qualifying-environment direct poll bypass as the sole full-suite failure.
- a6ad8bbf: qualifying public mutation now requires this collector instance to claim one exact durable CHILD_LAUNCH_AUTHORIZED record at record_service_start().
- 6ed7c9a5: added a stronger discriminant proving the same external launch cannot be reclaimed by a second collector through record_service_start().
- 7c54516d: proof inventory refreshed to 411 unit tests.

Status: implementation complete pending exact-head regression/CI. This is not a Gate A verdict.
