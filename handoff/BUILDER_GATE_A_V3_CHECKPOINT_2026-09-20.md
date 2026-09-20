# BUILDER GATE A V3 CHECKPOINT — 2026-09-20

BASE_SHA = db166fd04c681e67a2c6d4440828af14ef58c48c
CURRENT_BRANCH = builder/p0-gate-a-v3-2026-09-20
CURRENT_HEAD = resolve origin/builder/p0-gate-a-v3-2026-09-20; a commit cannot truthfully contain its own SHA
SURFACE_1 = RED_DISCRIMINANT_ADDED
SURFACE_2 = RED_DISCRIMINANT_ADDED
SURFACE_3 = RED_DISCRIMINANTS_ADDED_FOR_DIRECT_RECONCILE_POLL_DRAIN
SURFACE_4 = RED_DISCRIMINANT_ADDED
SURFACE_5 = RED_DISCRIMINANT_ADDED
SURFACE_6 = RED_DISCRIMINANT_ADDED
SURFACE_7 = RED_DISCRIMINANTS_ADDED_FOR_FINGERPRINT_AND_CLEAR_COOLDOWN
B2_REGRESSION = CLOSED_IN_BASE; MUST_REMAIN_GREEN
FOCUSED_TESTS = PENDING_RED_CI
FULL_SUITE = NOT_RUN_FOR_V3
CI = PENDING_RED_CI
KNOWN_BLOCKERS = NONE
NEXT_ACTION = Inspect exact-head red CI; confirm failures are intended primitive-level Gate A v3 defects, then implement minimal corrections without redirecting tests.

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
