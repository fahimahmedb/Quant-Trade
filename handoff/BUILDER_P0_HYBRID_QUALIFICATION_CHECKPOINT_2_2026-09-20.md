# BUILDER — P0 Hybrid Qualification Harness — Checkpoint 2 — 2026-09-20

Delta since `handoff/BUILDER_P0_HYBRID_QUALIFICATION_CHECKPOINT_2026-09-20.md`
("Checkpoint 1"). Read Checkpoint 1 first — it has the full mission context,
codebase facts and boundaries; this file only records what changed.

`PRODUCTION_CODE_CHANGED = FALSE` still holds. Only `tools/p0_qualification/`
and `handoff/` were touched.

## What's done now

### `common/synthetic.py` — bugfix
`response()` was calling the real `SecHttpResponse` dataclass with fields it
doesn't have (`encoding_lied`, `truncated`, `elapsed_seconds` do not exist on
it; the real fields are `status, reason, body, headers, transfer_outcome`).
Fixed. `timing_matrix.py` never exercised this path (it doesn't use
`response()`), so the earlier committed timing-matrix results are unaffected;
`calendar_matrix.py` is the first module that needed it, which is how the bug
surfaced.

### `gate_a/calendar_matrix.py` — DONE and verified
Run: `PYTHONPATH=. python3 -m tools.p0_qualification.gate_a.calendar_matrix`

- Classifies 6 sample dates (ordinary weekday, Friday, Saturday, Sunday,
  Monday, the 2026-11-26 Thanksgiving closure) via
  `is_edgar_business_day` directly — all `NON_ISSUE`.
- Confirms all 11 bound 2026 EDGAR closures and that year 2027 (unbound)
  raises `EdgarCalendarUnbound` — fail-closed confirmed.
- Cites existing weekend/holiday/DST/business-day-independent-of-HTTP tests
  in `tests/test_p0_continuity_compression.py`, verifying at run time that
  each citation still resolves.
- **New direct end-to-end proof of `404 != holiday`**: builds a real
  `SecForm4Collector` via `SyntheticEnvironment`, bootstraps it, advances
  `FrozenTimebase` past the 30h settle threshold for an ordinary business
  day, calls the real `collector.reconcile(due)` against a daily-index
  endpoint that always 404s, and confirms the gap is classified
  `DAILY_INDEX_UNAVAILABLE` — never treated as reconciled, never treated as
  a holiday, never silently dropped. This is genuinely new evidence (no
  existing test drives this exact path end-to-end through the real
  collector).

Result: **15/15 records `NON_ISSUE`**. No `MISSING_PROOF`, no `REAL_DEFECT`.
Committed artifact: `tools/p0_qualification/evidence/gate_a/calendar_matrix.json`.

### `gate_a/long_history.py` — WRITTEN, run IN PROGRESS at time of this checkpoint

Implements mission section 8.C. Design decision worth preserving: an
in-process replay at the real 60s discovery cadence for 14 virtual days would
be ~20,160 `collector.poll()` calls, and each call's cost grows with journal
size (`read_jsonl` re-reads the whole growing JSONL file every call — fine
for a long-running service, not for a tight in-process replay loop).
Measured: 200 polls → 3.25s, 600 → 14.3s, 1200 → 42.8s (clearly superlinear,
not a bug — just not the right tool for calendar-cadence replay in one
process). So this campaign uses a **600s (10-minute) compressed discovery
cadence** for exactly the stress duration, which reproduces the mission's
own cited "2,016-obligation" stress figure (14 days × 24h × 6 ticks/hour =
2016) while keeping wall-clock runtime bounded. The real 60s production
cadence is exercised as-is (uncompressed) elsewhere (existing test suite,
`gate_a/timing_matrix.py`); this campaign is about obligation-ledger
invariants at scale, not the cadence constant itself.

Two sub-campaigns:
1. `_run_clean_horizon` — ~2016 polls + interleaved `reconcile()` calls
   across the compressed 14-day horizon, then **one** call to the real
   `audit_observation_window(collector, now=...)` (this reads the whole
   journal once — O(n), not O(n²) — so it's cheap even at this scale).
   Asserts `accountable=True`, `fingerprint_stable=True`.
2. `_run_discriminating_break` — a short 20-poll history, then a **forged**
   `SchedulerTransition` is appended directly to the journal (bypassing the
   collector's own bookkeeping) representing a due obligation nothing ever
   answers. Asserts the audit correctly flags
   `UNEXPLAINED_EXPECTED_ACTION` and `accountable=False`. This is the
   mission-9-style discriminating-power check applied at the campaign level:
   a stress driver that can only ever pass is worthless as evidence.

**Status at this checkpoint: the clean-horizon run (~2016 polls) was
launched and had not finished within the immediate session window** (the
per-call cost growth described above makes ~2016 calls take on the order of
minutes, not seconds — extrapolating from the 1200-call measurement above,
roughly 1.5–3 minutes, but this was not yet confirmed to completion when
this checkpoint was written).

**Next action for whoever resumes**: run
`PYTHONPATH=. python3 -m tools.p0_qualification.gate_a.long_history` (give
it several minutes; consider `run_in_background` / a generous timeout) and
inspect `tools/p0_qualification/evidence/gate_a/long_history.json`. Two
outcomes:
- Both records `NON_ISSUE` → commit the evidence file as-is, mark this item
  done in the next checkpoint.
- If wall-clock cost is unacceptably long in CI (this module will also need
  to run in the dedicated qualification CI workflow, item 10 in Checkpoint
  1's next-steps list) → reduce `STRESS_VIRTUAL_DAYS` in
  `gate_a/long_history.py` (e.g. to 3–4 days) and say so explicitly in the
  evidence record's `residual` field as a CI-runtime accommodation, not a
  proof gap — the invariant being tested (obligation-ledger correctness at
  scale) does not depend on the specific day count, only on exercising
  "many" obligations, and the discriminating-break sub-campaign (which is
  cheap, ~20 polls) independently proves the audit's detection power
  regardless of horizon length.
- If either record comes back `REAL_DEFECT` → **stop the production-fix
  path immediately** per the mission's immutability boundary (section 5):
  preserve the red evidence file, classify it, do not patch
  `src/quant/dataplane/sec/` from this branch, and record the finding
  prominently in the next checkpoint for Blue.

## Immediate next steps (supersedes Checkpoint 1 section 5, items 1–2 now done)

1. Confirm `long_history.py`'s result (above) and commit its evidence JSON.
2. `gate_a/fault_matrix.py` (Checkpoint 1 §5 item 3) — not started.
3. Everything else in Checkpoint 1 §5 items 4–12 is unchanged and still
   pending, in the same priority order.

## Boundaries

Unchanged from Checkpoint 1 §6 — re-read it, don't assume it from memory.
