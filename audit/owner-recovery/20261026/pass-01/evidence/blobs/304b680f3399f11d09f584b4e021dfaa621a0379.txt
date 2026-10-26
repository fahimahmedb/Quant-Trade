# BUILDER — P0 Hybrid Qualification Harness — Checkpoint 3 — 2026-09-20

Delta since Checkpoint 2. Read Checkpoint 1 (full context) and Checkpoint 2
(the lifecycle/coverage debugging that led here) first.

`PRODUCTION_CODE_CHANGED = FALSE` still holds.

## `gate_a/long_history.py` — DONE, both sub-campaigns NON_ISSUE, full P14D horizon

Checkpoint 2 left this at a 576-obligation (4-day) partial run with three
findings unexplained (`LIFECYCLE_PROVENANCE_MISSING`, `INVALIDATING_INTERVENTION`,
`COVERAGE_NOT_COMPLETE`/`OPEN_COVERAGE_GAPS`). All three turned out to be
**harness-methodology gaps, not production defects** — each one is production
correctly rejecting an unrealistic synthetic fixture:

1. `LIFECYCLE_PROVENANCE_MISSING` — `SyntheticEnvironment` never wrote a
   lifecycle record at all (only the real launcher/supervisor does that).
   Fixed: `common/synthetic.py:seed_lifecycle_start()` appends one legitimate
   record before a campaign starts.
2. `INVALIDATING_INTERVENTION` — the obvious lifecycle cause to seed with,
   `SCHEDULED_START`, is *deliberately* in `INVALIDATING_CAUSES`
   (`src/quant/dataplane/sec/supervisor.py`'s module docstring: an ordinary
   boot is not positive authority for a qualifying window — correct
   conservatism, irrelevant to what this campaign tests). Switched the seed
   to `DEPLOYMENT_RESTART`, one of the two causes with positive
   non-invalidating authority.
3. `COVERAGE_NOT_COMPLETE` / `OPEN_COVERAGE_GAPS` — two separate unrealistic
   fixtures, found in sequence:
   - `empty_atom_feed()` (zero entries, forever) can never let the collector
     re-establish cursor continuity after the first poll — a real EDGAR
     "latest filings" feed always shows its rolling window, even when
     nothing *new* has filed. Added `common/synthetic.py:stable_atom_feed()`
     (one stable synthetic entry, always the same identity — captured once,
     deduplicated forever after).
   - `empty_daily_index()` (zero rows) is *deliberately* rejected by
     production (`daily_index_contained_no_rows`: "a published daily index
     always lists that day's filings" — real EDGAR index files are never
     truly empty). Fixed the fixture to carry one non-Form-4 row, so
     Form-4 reconciliation still finds zero missing accessions.
   - Also had to actually call `collector.drain()` when
     `collector.state.pending_tasks` is non-empty (a real service loop polls
     *and* drains each tick; the campaign wasn't doing the second half),
     and route `.txt` filing fetches to the shared
     `tests/fixtures/sec/form4_submission.txt` fixture so drain can resolve
     what poll() enqueues.

With all four fixes, the campaign runs the **full un-reduced 14-day
horizon** (not the 4-day fallback Checkpoint 2 anticipated needing):

```
polls_executed: 2016   (14d * 24h * 6 ticks/hour, matching the mission's own
                         cited "2,016-obligation" stress figure exactly)
wall_clock_seconds: ~118s
accountable: true
obligations: 2035, obligations_unexplained: 0
obligations_resolved_by_attempt: 2025, obligations_resolved_by_supersession: 8
fingerprint_stable: true
coverage_state: COMPLETE
```

Plus the discriminating-break sub-campaign: a forged unanswered obligation
is correctly caught (`accountable=False`,
`UNEXPLAINED_EXPECTED_ACTION` in findings) — confirmed only after also
fixing its tolerance-window arithmetic (the original `advance(cadence * 2)`
was still inside the audit's grace period; `DUE_TOLERANCE_MULTIPLIER=3.0` at
a 600s cadence means the grace window is 1800s, so the advance needed to be
`> 1800s`; changed to `cadence * 5`).

**Result: `tools/p0_qualification/evidence/gate_a/long_history.json` — 2/2
records `NON_ISSUE`.** No `REAL_DEFECT`, no `MISSING_PROOF`.

New/changed common fixtures (reusable by later gate modules — `fault_matrix.py`
in particular should reach for these rather than re-deriving them):
- `common/synthetic.py:seed_lifecycle_start(collector)` — required before any
  campaign calls `audit_observation_window()` on a `SyntheticEnvironment`
  collector.
- `common/synthetic.py:stable_atom_feed()` — use instead of `empty_atom_feed()`
  whenever a campaign needs coverage to reach and stay `COMPLETE`.
  `empty_atom_feed()` is still correct for campaigns (like
  `calendar_matrix.py`'s 404≠holiday check) that only need a *structurally
  valid* feed and don't care about coverage continuity.
- `common/synthetic.py:empty_daily_index()` — now carries one non-Form-4 row;
  update any earlier assumption that it's literally zero-row.
- `common/synthetic.py:daily_index_router(..., filing_body=...)` — now also
  answers `.txt` filing fetches (defaults to the shared
  `tests/fixtures/sec/form4_submission.txt` fixture).

## Next steps

Unchanged from Checkpoint 1 §5, items 3 onward (`gate_a/fault_matrix.py` is
next). Item 1 (calendar_matrix) and item 2 (long_history) are now both done.
