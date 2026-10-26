# BUILDER GATE A V3 CHECKPOINT — 2026-09-20

BASE_SHA = db166fd04c681e67a2c6d4440828af14ef58c48c
CURRENT_BRANCH = builder/p0-gate-a-v3-2026-09-20
CURRENT_HEAD = resolve origin/builder/p0-gate-a-v3-2026-09-20; a commit cannot truthfully contain its own SHA
SURFACE_1 = IMPLEMENTED; EXACT_HEAD_CI_SUCCESS_ON_b278e4c5
SURFACE_2 = IMPLEMENTED; EXACT_HEAD_CI_SUCCESS_ON_b278e4c5
SURFACE_3 = IMPLEMENTED; DIRECT_RECONCILE_POLL_DRAIN_FIDELITY_RETAINED; EXACT_HEAD_CI_SUCCESS_ON_b278e4c5
SURFACE_4 = IMPLEMENTED; TERMINAL_EVENT_WITHOUT_STATE_FIX_AT_bccd9420; EXACT_HEAD_CI_SUCCESS_ON_b278e4c5
SURFACE_5 = IMPLEMENTED; EXACT_HEAD_CI_SUCCESS_ON_b278e4c5
SURFACE_6 = IMPLEMENTED; BASELINE_LIFECYCLE_ONLY; EXACT_HEAD_CI_SUCCESS_ON_b278e4c5
SURFACE_7 = IMPLEMENTED; FORGED_BUDGET_CALLBACK_FIX_AT_6fc9f10d; EXACT_HEAD_CI_SUCCESS_ON_b278e4c5
B2_REGRESSION = CLOSED_IN_BASE; PRESERVED_GREEN_ON_b278e4c5
FOCUSED_TESTS = GREEN_ON_EXACT_HEAD_b278e4c5
FULL_SUITE = GREEN_ON_EXACT_HEAD_b278e4c5
CI = RUN_35513010411_COMPLETED_SUCCESS_ON_b278e4c5403adcc92d2c065f2d305365e48ec6f0
KNOWN_BLOCKERS = NONE_KNOWN_IN_BUILDER_SCOPE
NEXT_ACTION = Write final Builder handoff, commit/push it, then require exact-head CI SUCCESS on the handoff HEAD before returning to Blue.

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
