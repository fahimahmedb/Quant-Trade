# CLAUDE FORWARD DATA — 2026-09-20

```
BASE_SHA  = b17b381a8fa1f6a24e6cd6f92a090b40627bfe78
FINAL_SHA = 8862a54fcba814dee44bcbda6c9c44af9aec1b91  (last code commit; this
            documentation commit is the branch tip)
BRANCH    = parallel/claude-forward-data-2026-09-20
```

Role: Data Plane Builder, forward-data-operability track. P0 SEC/Form-4 remains
exclusively `astra/p0-deep-adversarial-pre-t0`'s; this track never read the P0
reservoir, never modified `src/quant/dataplane/sec/**`,
`deploy/quant_sec_supervisor.py`, `deploy/quant-sec-capture.service`,
`src/quant/clock.py` or `scripts/quant.py` (verified below by `git diff --stat`
against those exact paths, empty). No new branch was created; all work landed
on the branch named in the mission, from its exact stated base.

Wave 1's own opportunity-cost review named this session's reason for existing:
*"The forward recorder is built and is recording nothing... Start the forward
recorder. Everything else in this wave can wait a week without loss; forward
data cannot."* This document reports what changed, what was found by
falsifying the existing recorder and this session's own new code, and whether
capture is now actually running.

---

## 1. Commits, in order

| SHA | Subject |
|---|---|
| `15c93f02` | `forward-data:` open live checkpoint, record starting state and boundaries |
| `7ac8ebaa` | `data:` honest forward-recorder time provenance, fix two-writer race at read time |
| `ce3ff106` | `data:` real source inventory and a Control-Plane-callable capture contract |
| `61ba4c85` | `data:` Forward Coverage Ledger with seven-state per-cell provenance |
| `c2d71c4c` | `data:` compose the forward ledger with Wave 1 admissibility, close a laundering gap |
| `8862a54f` | `data:` manual capture runner, and a real live capture proves the pipeline works |

14 files changed, 2,904 insertions, 20 deletions. Full diff is additive except
for targeted edits inside `forward_recorder.py` (hardening, not rewriting) and
two small additive properties in `paths.py`.

---

## 2. What was built

| File | Role |
|---|---|
| `src/quant/dataplane/forward_recorder.py` | (existing, hardened) append-only, immutable, PIT-readable observation ledger |
| `src/quant/dataplane/forward_contracts.py` | source inventory: `SourceProfile` per real candidate, each traced to repository evidence |
| `src/quant/dataplane/forward_capture.py` | adapter contract (`CaptureAttempt`), durable `AttemptJournal`, `ForwardCaptureRequest`/`ForwardCaptureTaskState`, `due()`/`execute_forward_capture()` |
| `src/quant/dataplane/forward_coverage.py` | `ExpectedCalendar` (versioned, append-only declarations) + `ForwardCoverageLedger` (seven-state per-cell classification) |
| `src/quant/dataplane/forward_admissibility.py` | composes the forward ledger with Wave 1's `admissibility.py`, unmodified |
| `src/quant/paths.py` | additive `forward` path subtree (not on the mission's forbidden list) |
| `scripts/forward_capture_runner.py` | manual runner; calls exactly the Control-Plane-facing contract above |
| `tests/test_dataplane_forward_lane.py` (extended) | 13 new adversarial recorder tests |
| `tests/test_dataplane_forward_capture.py` (new) | 23 tests: due-predicate, success/failure paths, restart replay |
| `tests/test_dataplane_forward_coverage.py` (new) | 18 tests: calendar versioning, seven-state classification, summary correctness |
| `tests/test_dataplane_forward_admissibility.py` (new) | 8 tests: forward-confirmation composition, laundering guard |
| `tests/test_forward_capture_runner.py` (new) | 4 wiring checks, no network |

No file under `src/quant/factory`, `src/quant/desk`, `src/quant/book`,
`src/quant/science`, `src/quant/economics` or `src/quant/learning` was
touched. This mission built evidence infrastructure only.

---

## 3. Source inventory — proof, not preference

Full detail with per-field evidence in `forward_contracts.SOURCE_INVENTORY`.

| Source | State | Why |
|---|---|---|
| `yahoo_daily_chart` | **AUTHORIZED, capturable now** | Already used, unmodified, by `dataplane/adapters.fetch_yahoo_daily` for the committed `us_sector_etf_daily` dataset. Reachability re-verified live this session (`HTTP 200` from `query1.finance.yahoo.com`) and again via two real captures (§6). No new credential, provider or licence. |
| `local_tsv_index` | Not live-capturable | Static, one-time operator-supplied export (`nasdaq_composite_daily`). There is no vendor endpoint behind it to poll — forward capture has nothing to attempt going forward. |
| `factor_residual_panel` | Blocked, new provider required | `research/opportunity_map.json`'s own recorded constraint: "no survivorship-controlled security and factor panel." Not fabricated here. |
| `volatility_surface_panel` | Blocked, new provider required | Same file: "historical option chains, quotes, rates, dividends, and corporate actions absent." Not fabricated here. |
| `sec_form4_p0` | Out of scope by boundary | P0-exclusive. This entry records deliberate exclusion; no reservoir content, count, identity or rhythm was read to produce it. |

Selection criterion used: **already-authorized, already-reachable, no open
scientific decision required** — not results, not outcomes. The universe
captured is exactly `SECTOR_UNIVERSE + BENCHMARK + CONTEXT` from
`dataplane/ingest.py`, unchanged (12 symbols), reused rather than reinvented
(`tests/test_forward_capture_runner.py` pins this equality).

---

## 4. Adapter contract / forward schema

Every `CaptureAttempt` (one per fetch, success or failure) carries:
`attempt_id`, `source_id`, `source_version`, `market_session`,
`symbols_requested`, `fetch_started_at`, `fetch_completed_at`, `outcome`,
`failure_state`, `schema_version`, `payload_hash`, `validation_state`,
`lineage`, `symbols_observed`, `sessions_observed`, `detail`. A
`__post_init__` refuses a failed attempt with no `failure_state`, and a
succeeded one that carries one — the pairing is checked, not just documented.

Every `ForwardObservation` (one per accepted session/symbol/field-set) carries
`symbol`, `session_date`, `fields`, `source`, `source_fingerprint`,
`recorded_at`, `note`, plus this mission's additions: `market_session`,
`fetch_started_at`, `fetch_completed_at`, `source_timestamp`,
`source_timestamp_state`. No coercion: a source that omits a field is never
represented as `0.0` (`test_no_field_is_silently_coerced_to_zero`); no
observation without a declared `source_fingerprint` is ever accepted.

## 5. Time authority

Six time concepts, kept distinct rather than collapsed into one
caller-supplied instant (the exact weakness Wave 1's own red team named:
*"`recorded_at` fourni par le caller n'est pas une preuve de temps"*):

| Concept | Field | Trust |
|---|---|---|
| source event / calendar identity | `session_date` | as declared by the adapter |
| source-declared instant, if any | `source_timestamp` + `source_timestamp_state` | `PRESENT`/`ABSENT`, never invented |
| market session | `market_session` | as declared |
| fetch start / end | `fetch_started_at` / `fetch_completed_at` | this process's own clock |
| system receipt time | `recorded_at` | **`TIME_AUTHORITY_UNATTESTED_LOCAL_CLOCK`** — explicitly labelled, never presented as externally attested |

`ForwardObservation.time_provenance()` returns all six together with that
label. Nothing here claims a trusted external timestamp exists, because none
does; the honest fix for the red team's finding is naming the limitation, not
hiding it.

## 6. Coverage model

`ForwardCoverageLedger.classify(session, symbol, now)` resolves every cell to
exactly one of `UNKNOWN`, `EXPECTED`, `ATTEMPTED`, `OBSERVED`, `VALID`,
`CONFLICT`, `MISSING`, with a documented precedence order and a `known_since`
timestamp taken from the determining record (never the query time).
`UNKNOWN != MISSING`, `MISSING != ZERO` are each covered by a dedicated,
named test. `ExpectedCalendar` sessions and universe are both explicit,
durable, append-only, versioned declarations — no trading calendar is
invented; sessions are seeded from the already-validated
`us_sector_etf_daily` snapshot (`seed_expected_sessions_from_dataset`), and a
universe change is versioned by `effective_from` so it is never applied
retroactively.

## 7. PIT semantics

Unchanged from Wave 1, restated: forward-only in wall clock
(`recorded_at` monotonicity, structurally enforced), immutable per key
(a differing resubmission is a visible `CONFLICT`, never a silent overwrite),
and `as_of(instant)` is the only accessor research should read from — it
returns strictly what existed before `instant`. `information_available_at`
for `yahoo_daily_chart` is the close of the dated session, with a minimum
one-day decision lag, identical to `ingest.py`'s already-accepted convention.

## 8. Failure modes tested

DNS/network, timeout, HTTP error (including rate-limit), malformed JSON,
source-reported error payload, no-usable-rows, schema drift (moved response
keys), truncated transfer (exercised via direct injection — the real Yahoo
adapter cannot yet distinguish it from other malformed JSON, named as a
limitation rather than faked), torn/partial final write, duplicate records,
vendor restatement, out-of-order fetch delivery, late correction,
timezone/session boundary, missing expected session, symbol-universe change,
and the two-writer race (below). Each has a dedicated, named test.

---

## 9. Real defects found by falsification, and how each was closed

1. **Two-writer race in `ForwardRecorder`'s read path.** Two independent
   recorder instances, neither yet aware of the other's write, could each
   locally accept a different value for the same brand-new key; the prior
   `accepted()`/`__init__` did not re-enforce first-accepted-per-key across
   such a race, so a third, freshly opened reader could see two different
   `ACCEPTED` rows for one key. Fixed with a single `_replay()` every reader
   now goes through; the second racer's row is surfaced via a new
   `race_conflicts()` accessor instead of silently returned as a second valid
   observation. History already on disk is never rewritten.
2. **`CONFLICT` was structurally unreachable in the coverage ledger.** The
   first precedence order checked accepted-before-conflict; since a conflict
   can only exist for a key that already has an accepted value, "accepted
   first" always won. Fixed by checking conflicts first.
3. **A version already spent on a fit could still separately pass forward
   confirmation.** `evaluate_admissibility`'s `FORWARD_CONFIRMATION` branch
   checks only timing and the seal, never the `UseLedger`'s fit/validation
   history for that version. Closed with an additive guard in this session's
   own `forward_admissibility.evaluate_forward_confirmation` (Wave 1's
   `admissibility.py` untouched) that refuses the verdict when the version's
   prior uses intersect `CONSUMING_USES`.
4. **`ForwardCoverageLedger.summary()` silently skipped cells, then was too
   slow once fixed.** Found by running the actual tool against the real,
   2,514-session calendar (not by a unit test — every unit test happened to
   declare a universe whose `effective_from` already covered its own test
   sessions). The inner loop iterated `expected_symbols_for(session) or ()`,
   which silently dropped any session older than a universe declaration
   instead of reporting it `UNKNOWN`; the report showed all-zero counts.
   Fixed by enumerating every declared session against every symbol *ever*
   declared and letting `classify` resolve each cell — which then made
   `summary()` O(cells x file-scans), correct but impractically slow at
   30,168 cells. Fixed by computing the accepted/conflict/attempt indexes
   once per call.
5. **The static dataset's calendar could not "see" sessions the live fetch
   just observed.** `us_sector_etf_daily`'s own last date is 2026-09-11; the
   live fetch reached 2026-09-14..18. Closed by having `run-once` also
   declare the sessions its own successful payload contained as expected — a
   record of an observed fact, never a forward-looking claim, and it never
   touches any attempt's own success/failure outcome.

Items 1, 2 and 4 were each caught by a test failing honestly, not by
inspection — the test files show the exact reproduction for each.

---

## 10. Scheduling boundary

No second Control Plane, no second Clock, no autonomous loop. `due()` and
`execute_forward_capture()` in `forward_capture.py` are pure: given a state
and a `now`, they answer "is this due" and "do exactly one unit of work,"
mirroring the *already-existing, unmodified* relationship `clock.py` has with
`SecForm4Collector.poll_due()`/`.poll()` for the P0 lane. Nothing here is
inserted into `PersistentQueue`/`ResearchTask`: that queue's dispatch is
hard-coded in `clock.py` to the `research_lane` worker, and this mission does
not modify `clock.py`, so a foreign task there would only ever sit
permanently `BLOCKED` — status-surface noise, not infrastructure. When the
Control Plane is ready to own this, a future (out-of-scope-here) change to
`clock.py` can add a `_run_due_forward_capture` tick branch calling this
exact same pair. `scripts/forward_capture_runner.py` calls nothing else
either — it is the "runner manuel/stateless" the mission asked for, using the
identical contract.

---

## 11. Tests

```
PYTHONPATH=src python3 -m unittest discover -s tests   -> 654 passed (0 failures, 0 errors)
python3 scripts/generate_schemas.py --check             -> schemas checked
python3 scripts/demo_quant_system.py                    -> 35/35 checks passed
```

The whole-system demo (restart/crash recovery, Control Plane, Desk, Book,
status surface) is unaffected by this branch's changes, confirming the
existing V1 system's own invariants still hold end to end.

66 new tests this session (588 → 654), across 5 new test files plus 13 added
to the existing forward-lane suite. `git diff --stat` confirms zero changes
under `src/quant/dataplane/sec/**`, `deploy/quant_sec_supervisor.py`,
`deploy/quant-sec-capture.service`, `src/quant/clock.py` or
`scripts/quant.py`.

---

## 12. CAPTURE_IS_ACTUALLY_RUNNING = **FALSE** (as a continuous service)

This needs to be precise, because two different claims are easy to conflate:

- **The capture mechanism is real and live-proven.** This session ran
  `scripts/forward_capture_runner.py run-once` twice against the live,
  reachable Yahoo endpoint (no mock, no fixture) and durably recorded **60
  real observations** (12 symbols x 5 real sessions, 2026-09-14..18) with
  full provenance. A forced identical re-attempt produced 0 newly-accepted,
  proving idempotence live. Evidence:
  `handoff/FORWARD_DATA_FIRST_LIVE_CAPTURE_2026-09-20.json`.
- **Nothing invokes it automatically.** Both runs were manual, one-shot
  invocations inside this session's container, which is reclaimed when the
  session ends. There is no cron, systemd timer, or Control Plane tick
  calling `run-once` on a schedule anywhere yet.

**`BLOCKED_BY`**: continuous operation requires exactly one of two things
this mission does not have authority to do unilaterally:

1. **Control Plane integration** — a `clock.py` change adding a
   `_run_due_forward_capture` tick branch. `clock.py` is on this mission's
   explicit forbidden-file list.
2. **An operator-provisioned external scheduler** — a cron entry or a
   systemd timer unit analogous to the already-existing
   `deploy/quant-sec-capture.service` for the P0 lane. This is an
   infrastructure/deployment decision on a *persistent* host, which this
   ephemeral session's container is not.

**Exact command to run once either is authorized** (nothing else needed —
the code, tests and universe/session declarations already exist):

```bash
python3 scripts/forward_capture_runner.py declare-universe    # once
python3 scripts/forward_capture_runner.py declare-sessions    # once, re-run after each dataset refresh
python3 scripts/forward_capture_runner.py run-once            # on a schedule, e.g. hourly via cron/systemd timer
```

A minimal cron line, once a persistent host is authorized:
`0 * * * * cd /path/to/Quant-Trade && PYTHONPATH=src python3 scripts/forward_capture_runner.py run-once >> var/forward/runner.log 2>&1`

Nothing here fabricates continuity, and nothing here weakens the request
policy to make continuity look closer than it is.

---

## 13. Opportunity-cost assessment

Universe is 12 symbols, one bar per completed session, roughly 5 trading
sessions per week. Every day this runner is not scheduled:

- **~12 observations** (one session's worth, all 12 symbols) become
  permanently unrecordable *as forward evidence* for that date — a later
  fetch of that same historical date is development evidence, not forward
  evidence, by the recorder's own founding rule (its `recorded_at` would
  postdate the session by more than the deliberate collection window, and
  more importantly the point of forward evidence is that it could not have
  been shaped by hindsight; a late backfill can still be captured as raw
  history, but it never earns the same evidentiary status a same-day capture
  does).
- Annualized at ~252 trading sessions/year: **~3,024 observations/year** of
  genuinely forward-collected evidence foregone for as long as this stays
  unscheduled.

This is smaller in raw volume than the SEC/Form-4 lane's daily filing stream,
but it is the same *kind* of cost Wave 1 named: **the only cost in this whole
mission that compounds with calendar time and cannot be bought back later.**
Every other artifact in this branch (the coverage ledger, the admissibility
guard, the adapter contract) can be rebuilt in a day if lost; the specific
calendar days this lane does not run cannot.

---

## 14. No scientific decisions made

Nothing in this branch selects a D07 geometry, a D05 metric, a D08 inference
method, a D19 rule, a MEUE parameter, or a strategy. No captured forward data
was read for any purpose other than proving the capture mechanism itself
works (counts, hashes, session/symbol identities — never a price level's
implication). This mission built the evidence infrastructure; it does not
exploit it.

---

## 15. Attestation

```
P0_RESERVOIR_ACCESSED   = FALSE
P0_PROTOCOL_MUTATED     = FALSE
T0_TOUCHED              = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
```

Supporting facts:

* **`P0_RESERVOIR_ACCESSED = FALSE`.** No file under `src/quant/dataplane/sec/`,
  `var/sec/`, or any `handoff/SEC_FORM4_*.json` artifact was read for content.
  `sec/timebase.py` was read once, read-only, purely to mirror its
  already-established injectable-clock *pattern* (`Timebase`/`FrozenTimebase`)
  for this session's own, separately-declared `ForwardTimebase` — no reservoir
  data, count, identity or rhythm was read or inferred from it. No filing
  count, accession, identity, outcome, locator or attempt-journal content was
  read.
* **`P0_PROTOCOL_MUTATED = FALSE`.** No file in `governance/` was modified.
  `git diff --stat b17b381a..HEAD` against `src/quant/dataplane/sec/`,
  `deploy/quant_sec_supervisor.py`, `deploy/quant-sec-capture.service`,
  `src/quant/clock.py` and `scripts/quant.py` is empty (reproduced in §11).
* **`T0_TOUCHED = FALSE`.** No scheduler, service, supervisor or `t0`
  readiness path was read for modification or changed. This branch adds a
  *separate*, non-P0 capture lane's own manual runner; it does not touch the
  SEC lane's continuity clock in any way.
* **`REAL_CAPITAL_AUTHORIZED = FALSE`.** Nothing in this branch reads, writes,
  or references the Capital Desk, the Book, or any execution path. The two
  live network calls this session made were read-only market-data fetches
  against a public, credential-free endpoint already used elsewhere in this
  repository — no order, no position, no capital decision.

Nothing on this branch was merged. `scripts/quant.py`, `src/quant/clock.py`
and every file under `src/quant/dataplane/sec/` are byte-identical to the
base commit.

---

## 16. Final state

```
$ git status
On branch parallel/claude-forward-data-2026-09-20
nothing to commit, working tree clean
```

Pushed to `origin/parallel/claude-forward-data-2026-09-20`. No merge
performed or requested. STOP.
