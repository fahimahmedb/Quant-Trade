# CLAUDE FORWARD DATA — live checkpoint

**Branch:** `parallel/claude-forward-data-2026-09-20`
**Base:** `b17b381a8fa1f6a24e6cd6f92a090b40627bfe78` (Wave 1 CLAUDE handoff tip)
**Role:** Data Plane Builder, forward-data operability track. P0 SEC/Form-4 remains
exclusively `astra/p0-deep-adversarial-pre-t0`'s. This track does not read the P0
reservoir, does not modify `src/quant/dataplane/sec/**`, `deploy/quant_sec_supervisor.py`,
`deploy/quant-sec-capture.service`, `src/quant/clock.py` or `scripts/quant.py`.

This file is updated after each significant slice of work, before every checkpoint
commit. It is the running log; `handoff/CLAUDE_FORWARD_DATA_2026-09-20.md` is the
final deliverable written once the mission is complete.

---

## Mission (compressed)

Wave 1 built `src/quant/dataplane/forward_recorder.py` and left it recording zero
observations — the single highest-value-per-day item in the Wave 1 opportunity-cost
review. This mission's job is to make the forward lane *realistically operable*
without creating a second Control Plane / scheduler and without touching P0.

Concretely: audit the recorder adversarially, make time provenance honest and
explicit (no fake "trusted external timestamp"), inventory real non-P0 sources
already authorized in this repository, define an adapter contract, build a forward
coverage ledger with EXPECTED/ATTEMPTED/OBSERVED/VALID/CONFLICT/MISSING/UNKNOWN,
define a clean `ForwardCaptureTask`/`ForwardCaptureRequest` interface a future Clock
can call (or a manual runner using the identical contract today), and answer with
repository proof whether capture can actually start now.

## Starting state (read before any code)

Read in full: `QUANT_NORTH_STAR.md`, `STATE.md`, `SYSTEM_ARCHITECTURE.md`,
`NEXT_BUILD_MISSION.md`, `handoff/PARALLEL_WAVE1_CLAUDE_2026-09-19.md`, `SOURCE_BASIS.md`,
`research/opportunity_map.json`. Inspected: `src/quant/dataplane/**` (non-sec),
`src/quant/clock.py` (read-only — Control Plane contract, not modified),
`src/quant/dataplane/sec/timebase.py` (read-only, small interface file, to mirror the
injectable-clock convention already established for the SEC lane; no reservoir
content read), `src/quant/state.py`, `src/quant/paths.py`, `src/quant/events.py`,
`src/autonomous_research/runtime.py`.

Baseline before any change: `588 tests passed` (`PYTHONPATH=src python3 -m unittest
discover -s tests`).

Key facts established before writing code:

* `ForwardObservation`/`ForwardRecorder` are used only inside `forward_recorder.py`
  itself and `tests/test_dataplane_forward_lane.py` — no other module imports them,
  so they can be extended (additive, default-valued fields) without a large blast
  radius.
* The only two datasets ever registered are `us_sector_etf_daily` (Yahoo Finance
  public chart endpoint, credential-free, already fetched over the network by this
  repository's own `ingest.py`) and `nasdaq_composite_daily` (a static local export
  with no live update path — not forward-capturable).
* Live network egress to `https://query1.finance.yahoo.com` **is reachable from this
  execution environment** (`curl` returned HTTP 200 with real quote data during
  reconnaissance) — this is direct repository-adjacent proof that the already-used,
  already-authorized source is live-operable right now, without new credentials.
* `research/opportunity_map.json` names the *other* candidate lanes' exact blockers:
  `factor_residual` needs a survivorship-controlled security/factor panel (new
  provider), `volatility_surface` needs option chains/quotes/rates/corporate actions
  (new provider), `insider_filings` is the P0 SEC/Form-4 lane (out of scope here).
  None of these are invented as "available" — they stay named-blocked.
* A real defect found by falsification before writing any fix: `ForwardRecorder`'s
  read path (`accepted()`, and the count in `__init__`) does not enforce
  first-accepted-wins per key across *two independent recorder instances* racing on
  the same file — only the in-memory guard of a single already-running instance
  does. Two processes that both see an empty/older file and both accept the same new
  key with different values can both get journaled as `ACCEPTED`, and the naive
  reader returns both. This is being fixed and covered by an adversarial test (see
  progress log).

## Non-negotiable boundaries (restated for this file's own audit trail)

```
P0_RESERVOIR_ACCESSED   = FALSE  (kept true throughout; no var/sec/**, no handoff/SEC_FORM4_*.json read)
CLOCK_PY_MODIFIED       = FALSE
SEC_DIR_MODIFIED        = FALSE
SCRIPTS_QUANT_PY_MODIFIED = FALSE
SECOND_SCHEDULER_CREATED = FALSE
SCIENTIFIC_SELECTION_MADE = FALSE  (no D07/D05/D08/D19/MEUE/strategy choice)
NEW_BRANCH_CREATED      = FALSE (working on parallel/claude-forward-data-2026-09-20 as instructed)
```

## Progress log

- [done] Checkpoint file created. Baseline established (588 tests).
- [done] **Time authority** (`src/quant/dataplane/forward_recorder.py`).
  `ForwardObservation` gained explicit, additive, default-valued fields:
  `market_session`, `fetch_started_at`, `fetch_completed_at`, `source_timestamp`,
  `source_timestamp_state`. A new `time_provenance()` method names all six time
  concepts the mission distinguishes (source event time, market session, fetch
  start/end, system receipt time, vendor publication time) and explicitly labels
  `recorded_at` with `TIME_AUTHORITY_UNATTESTED_LOCAL_CLOCK` — it is this
  process's own clock, never claimed as externally attested. New violations:
  inconsistent fetch-window ordering, a `source_timestamp_state` that
  contradicts whether a value was actually supplied, an undeclared
  `market_session`. Zero renames, zero required-field additions — fully
  backward compatible with the 33 tests Wave 1 left passing.
- [done] **Real defect found and fixed by falsification**: the recorder's read
  path (`accepted()`, and the count computed in `__init__`) did not enforce
  first-accepted-per-key across two independent recorder instances racing the
  same file — only a single already-running instance's in-memory guard did.
  Reproduced with a test that opens two `ForwardRecorder`s against the same
  empty file and has both accept a different value for the same brand-new key;
  before the fix, a third, freshly opened reader saw two different "ACCEPTED"
  rows for one key. Fixed with a single `_replay()` method every reader now
  goes through, which keeps the first accepted content address per key in
  append order and reports every later, differently-addressed row through a
  new `race_conflicts()` accessor instead of silently returning it as a second
  valid observation. Nothing already committed to a `ForwardRecorder` file is
  rewritten — this is a read-time reclassification, not history editing.
- [done] 13 new adversarial tests added to `tests/test_dataplane_forward_lane.py`
  covering: time-provenance fields and violations, out-of-order fetch delivery
  tolerance vs. ledger-order enforcement, timezone-offset normalisation at the
  monotonicity boundary, torn/partial final write recovery at the recorder
  level, the two-writer race (and the identical-value non-race control case),
  vendor restatement, and late correction. Full suite: **601 tests, all
  passing** (588 baseline + 13 new), zero regressions.
- [done] **Source inventory** (`src/quant/dataplane/forward_contracts.py`).
  `SourceProfile` dataclass with a hard `__post_init__` rule: anything not
  `SOURCE_AUTHORIZED` must name its exact `blocker`, never a vague category.
  Real inventory, five entries, every claim traced to a repository artifact in
  its `evidence` field: `yahoo_daily_chart` (AUTHORIZED — already used by
  `ingest.py`, reachability re-verified live), `local_tsv_index` (NOT_LIVE_
  CAPTURABLE — static export, no endpoint to poll), `factor_residual_panel` and
  `volatility_surface_panel` (BLOCKED_NEW_PROVIDER, quoting
  `research/opportunity_map.json`'s own named constraints verbatim), and
  `sec_form4_p0` (P0_EXCLUSIVE_OUT_OF_SCOPE — no reservoir content read to
  produce this entry, exists only to record deliberate exclusion).
- [done] **Adapter contract + execution engine**
  (`src/quant/dataplane/forward_capture.py`). `CaptureAttempt` carries every
  mission-required field (source id/version, fetch window, market session,
  symbol identity, schema version, payload hash, validation state, lineage,
  failure state) and its own `__post_init__` refuses a failed attempt with no
  failure_state or a succeeded one that carries one. `AttemptJournal` is
  append-only jsonl. `ForwardCaptureRequest`/`ForwardCaptureTaskState`/
  `due()`/`execute_forward_capture()` are the Control-Plane-callable seam:
  `execute_forward_capture` performs exactly one capture cycle and contains no
  loop, sleep or thread of its own — deciding *when* to call it is entirely
  the caller's job, mirroring the existing `SecForm4Collector.poll_due()`/
  `.poll()` relationship with `clock.py` (read for the pattern, not modified).
  Deliberately **not** inserted into `PersistentQueue`/`ResearchTask`: that
  queue's dispatch is hard-coded in `clock.py` to the `research_lane` worker,
  so a foreign task there would only sit permanently `BLOCKED` — noise, not
  infrastructure. `yahoo_forward_adapter()` wraps the existing, unmodified
  `adapters.fetch_yahoo_daily` with no retry/coercion added. Failure states
  are classified honestly from what that adapter actually raises (via
  `__cause__` inspection), not invented; `FAILURE_TRUNCATED` is exercisable
  only via direct injection today, documented as a named, honest limitation
  of the current real adapter rather than a fabricated detection path.
  23 new tests (`tests/test_dataplane_forward_capture.py`): due-predicate
  behaviour, success/idempotence/no-zero-coercion, one test per named failure
  state (DNS, timeout, HTTP/rate-limit, malformed JSON, source-error-payload,
  no-usable-rows, truncated-via-injection, schema-drift-via-moved-keys),
  consecutive-failure accounting, and restart/replay of the journal + task
  store + recorder together. Full suite: **624 passed**, 0 regressions.
- [done] **Forward Coverage Ledger** (`src/quant/dataplane/forward_coverage.py`).
  `ExpectedCalendar` holds two append-only declaration logs: sessions (an
  idempotent, monotonically growing set) and universe (versioned by
  `effective_from`, so a symbol added today is never applied retroactively to
  older sessions — tested directly). `seed_expected_sessions_from_dataset`
  bootstraps the session dimension from the already-validated
  `us_sector_etf_daily` snapshot instead of inventing a trading-holiday
  calendar. `ForwardCoverageLedger.classify()` resolves every (session,
  symbol) cell to exactly one of the seven mission-named states with a
  documented precedence order, and `known_since` is always the determining
  record's own timestamp, never the query time.
  **A real design bug found by testing the mission's own invariant list**: my
  first precedence order checked accepted-before-conflict, which made
  `CONFLICT` structurally unreachable — a `CONFLICT` record can only exist for
  a key that *already* has an accepted observation (the recorder only refuses
  a second, differing write for an already-claimed key), so "accepted first"
  always won before conflict was ever checked. Fixed by checking conflicts
  first: surfacing a dispute now takes priority over quietly reporting the
  first-accepted value. Caught by `test_conflict_is_visible_as_its_own_state`
  failing honestly rather than by inspection.
  `MISSING` requires both a post-close attempt *and* an elapsed grace period
  (`DEFAULT_MISSING_GRACE_HOURS`, named explicitly as an assumed operational
  parameter, not a derived SLA); an unattempted cell is `EXPECTED`, never a
  silent `MISSING` default — both inequalities the mission states
  (`UNKNOWN != MISSING`, `MISSING != ZERO`) have a dedicated test each.
  16 new tests, including one lightweight integration check against the real
  committed dataset file. Full suite: **640 passed**, 0 regressions.
- [done] **UseLedger/admissibility integration**
  (`src/quant/dataplane/forward_admissibility.py`), zero changes to Wave 1's
  `admissibility.py`. `forward_dataset_view()` renders a `ForwardRecorder` as a
  registry-record-shaped dict; critically, `recorded_from` is
  `ForwardRecorder.earliest_recorded_at()` (a new small accessor, added
  alongside `ledger_fingerprint()`), never a session's calendar label — a
  caller could mislabel a session date, but not move this recorder's own
  forward-only clock earlier.
  **A second real gap found by testing section 9's own words**
  ("une version déjà utilisée pour fit ne devient jamais forward
  confirmation"): `evaluate_admissibility`'s FORWARD_CONFIRMATION branch checks
  only timing and the pre-outcome seal — it never cross-checks the UseLedger's
  fit/validation history for that version, so a version already spent on
  `EXPLORATORY_FIT` could still separately pass forward-confirmation purely on
  timing. Closed with an additive guard in `evaluate_forward_confirmation()`
  (this new module only, `admissibility.py` untouched) that refuses the
  verdict when the version's prior uses intersect `CONSUMING_USES`, labelled
  `FORWARD_CONFIRMATION_VERSION_ALREADY_CONSUMED_BY_FIT_OR_VALIDATION`. A
  contrast test proves the guard is doing real work (the identical version
  passes when no ledger is supplied, and is refused once one records the
  prior fit).
  8 new tests. Full suite: **648 passed**, 0 regressions.
- [done] **Manual runner + a real live capture** (`scripts/forward_capture_runner.py`).
  Subcommands `declare-universe`/`declare-sessions`/`run-once`/`status`/`coverage`,
  all thin wrappers calling exactly `forward_capture.due`/
  `execute_forward_capture` and `forward_coverage.*` -- no logic of its own
  beyond argument parsing and printing. `paths.py` gained a `forward` subtree
  (`forward_observations`, `forward_attempts`, `forward_tasks`,
  `forward_expected_sessions`, `forward_expected_universe`), mirroring the
  existing `sec_*` convention; `paths.py` is not on the mission's forbidden
  list, only `clock.py`, `scripts/quant.py` and `sec/**` are.
  **Ran it for real** against the live, already-reachable Yahoo endpoint:
  `declare-sessions` seeded 2,514 real trading sessions from the committed,
  already-validated `us_sector_etf_daily` snapshot; `run-once` made one real
  HTTP fetch and durably recorded **60 real observations** (12 symbols x 5
  sessions, 2026-09-14 to 2026-09-18 -- sessions newer than the static
  snapshot's own last date) with full provenance (content hashes,
  fetch_started_at/completed_at, payload_hash); a second `run-once --force`
  against the identical window correctly produced 0 newly-accepted
  (idempotent resubmission, live-proven, not just unit-tested).
  **Two more real gaps found by running the actual tool, not by inspection**:
  (1) `ForwardCoverageLedger.summary()`'s inner loop iterated
  `expected_symbols_for(session) or ()`, which silently *skipped* any session
  older than a universe declaration's `effective_from` instead of reporting
  it `UNKNOWN` -- against the real 2,514-session calendar this made the
  entire coverage report show all-zero counts. Fixed by enumerating every
  declared session against every symbol *ever* declared
  (`ExpectedCalendar.all_declared_symbols`, new) and letting `classify` itself
  resolve each cell, so nothing is dropped from the report; a regression test
  reproduces the exact scenario. (2) That same fix made `summary()`
  O(cells x file-scans) -- correct but impractically slow at 30,168 cells.
  Fixed by computing the accepted/conflict/attempt indexes once per `summary()`
  call and threading them through `classify()`'s new optional keyword
  arguments, dropping real wall-clock time from unmeasured/slow to ~0.15-0.8s.
  A third, purely operational gap, also found live: the static dataset
  snapshot's calendar stops at its own last ingested date, so sessions the
  live fetch newly observed (09-14..09-18) were not yet in the declared
  calendar and could not classify as `VALID` until declared. Closed
  honestly, not by inventing a trading-calendar generator: `run-once` now
  also declares the exact sessions its own successful payload contained
  (`sessions_observed`) as expected -- a retroactive record of an observed
  fact, never a forward-looking claim, and it never touches whether any
  attempt outcome itself succeeded or failed. A `summary(session_from=...)` /
  `coverage --since` filter was added so a status check can focus on the
  operationally relevant recent window instead of the honest but
  UNKNOWN-heavy multi-year tail.
  6 new tests (2 coverage-ledger regressions, 4 runner-wiring checks with no
  network calls). Full suite: **654 passed**, 0 regressions.
- [done] Final deliverable written: `handoff/CLAUDE_FORWARD_DATA_2026-09-20.md`.
  Whole-system demo re-verified (`scripts/demo_quant_system.py` -> 35/35
  checks passed), confirming this branch's changes leave the existing V1
  system's own invariants intact. Mission complete; see that document for the
  full report, attestation and `CAPTURE_IS_ACTUALLY_RUNNING = FALSE` verdict
  with its exact blocker.

(Mission complete. See `handoff/CLAUDE_FORWARD_DATA_2026-09-20.md` for the
final deliverable.)
