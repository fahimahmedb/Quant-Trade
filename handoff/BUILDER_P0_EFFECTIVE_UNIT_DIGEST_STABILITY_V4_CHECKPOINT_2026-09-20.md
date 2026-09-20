# BUILDER P0 EFFECTIVE UNIT DIGEST STABILITY V4 CHECKPOINT — 2026-09-20

BASE_SHA = 2da079d8ad75c69eb3fc2990c512735cb4bdc02b
CURRENT_BRANCH = builder/p0-effective-unit-digest-stability-v4-2026-09-20
CURRENT_HEAD = resolve origin/builder/p0-effective-unit-digest-stability-v4-2026-09-20; a commit cannot truthfully contain its own SHA
DELIVERY_SHA = 0bdd397d7409b01529c1f958c68781499679a95e
DEFECT_INDEPENDENTLY_REPRODUCED_ON_UNMODIFIED_BASELINE = TRUE
FIX_SURFACE = deploy/quant_sec_supervisor.py::_effective_systemd_definition; canonicalize ExecStart, drop start_time/stop_time/pid/code/status
INCIDENTAL_TIGHTENING = qualifying flag check: substring -> exact argv-token match (same function, required by mandatory test list)
NEW_DISCRIMINATING_TESTS = Phase8EffectiveUnitDigestStabilityCampaign (12 tests) in tests/test_astra_pre_t0.py
DISCRIMINATING_POWER_VERIFIED = 4 of the 12 new tests independently confirmed FAIL against unmodified baseline, then PASS after fix restored
FOCUSED_TESTS = GREEN_ON_EXACT_HEAD_0bdd397d (Phase5/Phase7/Phase8 = 22 passed, 5 subtests)
SEC_P0_LANE_SUITE = GREEN_ON_EXACT_HEAD_0bdd397d (287 tests)
FULL_SUITE = GREEN_ON_EXACT_HEAD_0bdd397d (423 tests)
DEMO_E2E = GREEN_ON_EXACT_HEAD_0bdd397d (35/35 assertions)
SCHEMA_DRIFT_CHECK = PASS
STATUS_FRESHNESS_CHECK = PASS (STATE.md proof-inventory regenerated 411 -> 423)
CI = RUN_35535347844_COMPLETED_SUCCESS_ON_0bdd397d7409b01529c1f958c68781499679a95e
KNOWN_BLOCKERS = NONE_KNOWN_IN_BUILDER_SCOPE
NEXT_ACTION = Stop; hand control back to Blue for reception and independent Astra/Red Team review. Builder does not declare Gate A v4 PASS, target-host readiness, or t0.

## Delivery sequence

- `b3fc705f`: mission doc (pre-existing on branch before this session).
- `0bdd397d`: independent reproduction against unmodified baseline; corrective fix; 12 mandatory discriminating tests; STATE.md regeneration. Exact-head CI SUCCESS at run `35535347844`.

## What was NOT done (out of scope, per mission)

- No target-host execution — this is a repository-level correction only.
- No rematerialization, reauthorization, or freezing of the frozen v3 candidate.
- No Blue governance file changed.
- No Gate A v4, target-host-readiness, t0, P14D, Gate B, or capital-authorization claim.

See `handoff/BUILDER_P0_EFFECTIVE_UNIT_DIGEST_STABILITY_V4_HANDOFF_2026-09-20.md` for the full report.
