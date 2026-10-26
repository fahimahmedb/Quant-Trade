# BUILDER — P0 Hybrid Qualification Harness — Checkpoint 1 — 2026-09-20

Authority: this is a Builder checkpoint, not a Blue decision. It does not
declare Gate A v4 PASS, target-host readiness, t0, or a P14D amendment.

## 0. Read this first if resuming

This mission is long-horizon (see the full mission brief this checkpoint was
dispatched under — restate it from `handoff/BUILDER_P0_HYBRID_QUALIFICATION_HANDOFF_2026-09-20.md`
once that final handoff exists, or from the dispatching conversation/issue if
it does not yet exist). Read, in order:

1. `QUANT_NORTH_STAR.md`
2. `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`
3. `handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`
4. `governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md`
5. `handoff/BLUE_GATE_A_V4_RECEPTION_2026-09-20.md`
6. This checkpoint.
7. The long-horizon method authority at exact ref
   `blue/long-horizon-research-2026-09-20@7e0fae86834db7f46ecea5755faf0ac544245399`
   — six files, listed in section 2 below. That branch is METHOD/GOVERNANCE
   evidence, not the implementation base.

## 1. Branch / baseline state

- Builder branch: `builder/p0-hybrid-qualification-harness-2026-09-20`
- Created exactly from frozen candidate:
  `blue/p0-gate-a-v4-frozen-2026-09-20@4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`
  (verified by `git rev-parse origin/blue/p0-gate-a-v4-frozen-2026-09-20` at
  dispatch time — matched exactly, no STOP condition triggered).
- Current branch HEAD at this checkpoint: see `git log -1` on this branch;
  this checkpoint commit is the delta since the frozen baseline.
- `PRODUCTION_CODE_CHANGED = FALSE` so far. Every path touched is under
  `tools/p0_qualification/` (new, isolated) or `handoff/` (this file). No file
  in `src/`, `deploy/`, `tests/`, `scripts/`, `.github/workflows/` has been
  modified.

## 2. Method authority already internalised (do not re-read on resume)

Read and internalised at dispatch, from
`blue/long-horizon-research-2026-09-20@7e0fae86834db7f46ecea5755faf0ac544245399`:

- `governance/BLUE_P14D_CHALLENGE_2026-09-20.md` — prior-art matrix (SQLite,
  RocksDB, FoundationDB, TigerBeetle, etcd, Git, systemd), coverage matrix,
  hybrid Gate A/B/C/D proposal.
- `governance/BLUE_P0_COMPRESSED_QUALIFICATION_PROTOCOL_2026-09-20.md` — the
  exact Gate A/B/C/D procedure this harness implements.
- `governance/BLUE_P0_GATE_A_EVIDENCE_MATRIX_2026-09-20.md` — property-level
  GREEN/PRIOR/TARGET_ONLY/LIVE_ONLY ledger as of that branch's head. Several
  rows marked `FIX_UNDER_CI` or `OPEN TEST GAP` there (EDGAR source-date
  timezone, 30h settle-after-close, DST elapsed-hours boundary) are **already
  closed** in the V4 frozen candidate: see `tests/test_p0_continuity_compression.py`
  (`test_settle_delay_is_measured_after_edgar_close_not_utc_date_start`,
  `test_spring_dst_does_not_shorten_30_elapsed_hours`,
  `test_fall_dst_does_not_lengthen_30_elapsed_hours`,
  `test_known_sec_federal_holiday_is_not_a_reconciliation_target`,
  `test_unbound_calendar_year_fails_closed`). Do not re-open these as gaps;
  cite them.
- `governance/BLUE_P14D_AMENDMENT_DRAFT_2026-09-20.md`,
  `governance/BLUE_P0_CALENDAR_ADVERSARIAL_FINDINGS_2026-09-20.md`,
  `governance/BLUE_LONG_HORIZON_EXECUTION_PROTOCOL_2026-09-20.md`,
  `handoff/BLUE_LONG_HORIZON_CHECKPOINT_2026-09-20.md` — supporting context,
  not re-summarised here; re-read directly if a decision turns on their detail.

## 3. Codebase facts established at dispatch (do not re-derive)

- Production SEC P0 lane lives under `src/quant/dataplane/sec/` (14 modules,
  ~6000 lines) plus `deploy/quant_sec_supervisor.py` (733 lines, the systemd
  launcher/supervisor — this is where the V4 fix landed) and
  `deploy/quant-sec-capture.service`.
- Existing test suite (14 files under `tests/`) is **already very mature**:
  `tests/test_astra_pre_t0.py` (1049 lines, Phases 1–8, including the 12 new
  Phase8EffectiveUnitDigestStabilityCampaign tests from the V4 fix),
  `tests/test_p0_adversarial.py`, `tests/test_p0_continuity_compression.py`
  (calendar/DST/settle boundary tests), `tests/test_p0_deployment_boundaries.py`
  (raw-publication durability, real SIGTERM/SIGKILL process tests),
  `tests/test_gate_a_v3_red.py` (historical red-team regressions, still run).
- **Phase A baseline reproduced and confirmed GREEN at this exact HEAD**
  (see section 4). Blue's reception record
  (`handoff/BLUE_GATE_A_V4_RECEPTION_2026-09-20.md`) claims: full unit 423
  PASS, SEC P0 lane 287 PASS, V1 E2E 35/35, two exact-head GitHub CI runs
  SUCCESS (`35535347844`, `35536353538`). Locally reproduced and matches.
- Key production entry points a harness needs (all read-only, all called
  through existing public constructors — never modified):
  - `src/quant/dataplane/sec/policy.py:SecAccessPolicy` — dataclass with every
    acquisition-timing constant as a field default (discovery_poll_seconds=60,
    idle_reuse_seconds=20, connect_timeout=10, read_timeout=20,
    total_deadline=60, backoff_schedule=(5,15,60,300,900), jitter=0.25,
    rate_limit_cooldown=300, forbidden_cooldown=3600).
  - `src/quant/dataplane/sec/collector.py:DAILY_INDEX_SETTLE_HOURS = 30`,
    `_daily_index_settled_at_utc(day)`, `_edgar_business_date(stamp)`.
  - `src/quant/dataplane/sec/calendar.py:is_edgar_business_day`,
    `edgar_closed_dates`, `EdgarCalendarUnbound` — EDGAR_CLOSED_DATES_BY_YEAR
    is bound only for 2026; any other year raises fail-closed.
  - `src/quant/dataplane/sec/fingerprint.py:build_manifest`,
    `acquisition_critical_fingerprint`, `ACQUISITION_CRITICAL_MODULES` — the
    module-closure + policy + runtime + supervisor manifest.
  - `src/quant/dataplane/sec/audit.py:audit_observation_window(collector, *,
    tolerance_seconds=None, now=None, window_start=None)` — **this is the
    production Gate C continuity verifier primitive**. Passing an explicit
    `window_start` (bound to a declared t0) is exactly what Phase F
    (continuity verifier) must wrap; do not reimplement reconciliation logic.
  - `src/quant/dataplane/sec/scheduler.py:SchedulerJournal` — named prospective
    obligations with `obligation_id`/`supersedes_obligation_id`.
  - `deploy/quant_sec_supervisor.py` — constants `RESTART_DELAY_SECONDS=15`,
    `RESTART_BURST_LIMIT=5`, `RESTART_BURST_WINDOW_SECONDS=600`,
    `TIMEOUT_STOP_SECONDS=30`, `DEPLOYMENT_AUTHORITY_MAX_AGE_SECONDS=3600`;
    functions `_effective_systemd_definition`, `_consume_deployment_authority`,
    `authority_path`, `authority_ledger_path`, `host_boot_id` (imported from
    `quant.dataplane.sec.supervisor`). No `__init__.py`; load it with
    `importlib.util.spec_from_file_location`, exactly as
    `tests/test_astra_pre_t0.py` already does (see
    `tools/p0_qualification/common/launcher_loader.py`, which mirrors that
    pattern — including symlinking `src/scripts/deploy` into an isolated root
    so the launcher's relative-path lookups resolve without ever writing into
    the checked-out tree).
  - `_consume_deployment_authority` reads real wall-clock
    (`datetime.now(timezone.utc)`), not an injectable timebase — to hit an
    exact age boundary deterministically you must monkeypatch the `datetime`
    class object inside the *loaded module instance* (subclass override, see
    `gate_a/timing_matrix.py:_deployment_authority_max_age_boundary`), never
    edit the file.

## 4. Work completed so far (this checkpoint)

### 4.1 Phase A — evidence inventory (baseline reproduction)

Reproduced locally at this exact branch HEAD (frozen V4 candidate, no code
changed):

| Suite | Command | Result |
|---|---|---|
| Full unit suite | `PYTHONPATH=src python3 -m unittest discover -s tests -v` | **423 PASS**, 242.4s |
| SEC P0 explicit lane | `PYTHONPATH=src python3 -m unittest tests.test_sec_form4_capture tests.test_p0_adversarial tests.test_astra_pre_t0 -v` | **287 PASS**, 18.2s |
| V1 E2E | `python3 scripts/demo_quant_system.py` | **35/35 PASS** |
| Generated schema drift | `python3 scripts/generate_schemas.py --check` | clean |
| Status artifact freshness | `python3 scripts/status_artifacts.py --check` | clean |

Classification: **FACT** — exact-head reproduction at
`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`, matches Blue's reception record.
This is repository-execution evidence only; it does not establish target-host
or live-source properties (see the evidence matrix domain column).

A full written evidence-matrix document (property → exact test → exact SHA →
result → failure class → remaining domain, per mission section 7) is
**not yet committed as a standalone file** — build it next from
`governance/BLUE_P0_GATE_A_EVIDENCE_MATRIX_2026-09-20.md` (the long-horizon
branch's version) updated for the tests actually present at V4 HEAD, plus the
harness's own generated JSON in `tools/p0_qualification/evidence/`.

### 4.2 Gate A harness scaffold — `tools/p0_qualification/`

New, isolated package. Nothing under `src/`, `deploy/`, `tests/`, `scripts/`
was touched.

```
tools/p0_qualification/
  __init__.py                    # FROZEN_CANDIDATE_SHA/REF constants
  common/
    __init__.py
    evidence.py                  # EvidenceRecord/Report: epistemic + defect
                                  #   classification, canonical JSON, digest,
                                  #   verified_input_tree_digest()
    synthetic.py                 # SyntheticEnvironment: builds a REAL
                                  #   SecForm4Collector against an isolated
                                  #   temp QuantPaths root with a FakeTransport
                                  #   (no socket ever opened) and FrozenTimebase.
                                  #   empty_atom_feed(), daily_index_router().
    launcher_loader.py            # load_launcher(), stage_isolated_root():
                                  #   loads deploy/quant_sec_supervisor.py by
                                  #   file path into a fresh module instance,
                                  #   symlinking src/scripts/deploy into an
                                  #   isolated root first.
  gate_a/
    __init__.py
    timing_matrix.py              # A3 timing-boundary matrix — DONE, see 4.3
  evidence/
    gate_a/timing_matrix.json     # generated artifact (committed as a
                                  #   baseline snapshot; regenerate before
                                  #   trusting it — see --check pattern below)
```

Directories created but **empty / not yet implemented**:
`discrimination/`, `gate_b/`, `gate_c/`, `gate_d/` (top-level), and
`evidence/{discrimination,gate_c,gate_d}/`.

### 4.3 `gate_a/timing_matrix.py` — DONE and verified

Run: `PYTHONPATH=. python3 -m tools.p0_qualification.gate_a.timing_matrix`

What it does:
- Reads the A3-scoped timing constants **directly from production source**
  (`SecAccessPolicy` dataclass field defaults; `DAILY_INDEX_SETTLE_HOURS`;
  the five `deploy/quant_sec_supervisor.py` constants) — never a copied
  number, so drift in production can't silently go unnoticed here.
- Cites the exact existing discriminating test for each constant (a
  hand-maintained `CITATIONS` table) and **verifies at run time that every
  cited test id still resolves** via `unittest.TestLoader().loadTestsFromName`
  — a stale citation becomes a `MISSING_PROOF` finding, not a silent pass.
- Closes one genuine gap the existing suite does not cover: the exact
  microsecond boundary of `DEPLOYMENT_AUTHORITY_MAX_AGE_SECONDS` (3600s).
  Verified, with the launcher's wall-clock `datetime.now()` frozen via a
  subclass monkeypatch (never editing the file):
  - age == 3600.000000s → **accepted** (correct)
  - age == 3600.000001s → **rejected** (correct)
  - age == 3601.0s → **rejected** (correct)
  All three: `NON_ISSUE`. This is new FACT-level evidence not previously in
  the repository.
- Also runs a direct boundary check of `policy.backoff_seconds(step)` at
  step ∈ {-1, 0, 1, last, last+1, last+10}, confirming the ladder clamps
  correctly at both ends (production function, not reimplemented).

Current output: 17 records, all `NON_ISSUE` except two intentionally
unresolved `MISSING_PROOF` entries that are the harness being honest about
its own scope, not defects:
- `restart_burst_limit` — citation is a real test
  (`Phase4LifecycleAndWindowCampaign.test_unsolicited_zero_child_exit_cannot_cleanly_stop_qualifying_service`)
  but it only exercises `RESTART_BURST_LIMIT=0` (disabled), not the N-vs-N-1
  count boundary. Residual: **add a genuine burst-count boundary test** (spawn
  exactly `RESTART_BURST_LIMIT` restarts inside the window vs one fewer) —
  this belongs in the fault matrix (4.4 below), not necessarily timing_matrix.
- `deployment_authority_max_age_seconds` (the bare constant-citation record)
  — intentionally has no citation; the three `:*_boundary` sub-records above
  are the actual proof. Reads as an artifact of how the module reports "the
  raw constant has no prior citation" separately from "the boundary is now
  proven here." Not a defect; could be quieted by suppressing the bare
  citation record when a dedicated boundary check for the same name exists in
  the same run, if a future pass wants a cleaner report.

## 5. Immediate next steps (in priority order)

1. **`gate_a/calendar_matrix.py`** (A2/mission-listed calendar matrix) — was
   about to be started when this checkpoint was written. Use
   `src/quant/dataplane/sec/calendar.py` (`is_edgar_business_day`,
   `edgar_closed_dates`, `EdgarCalendarUnbound`) directly. Cover: ordinary
   weekday, Friday, Saturday, Sunday, Monday, a known 2026 EDGAR closure (see
   `EDGAR_CLOSED_DATES_BY_YEAR[2026]` — 11 dates, e.g. `date(2026,11,26)`
   Thanksgiving), unbound future year (2027) fails closed, and the
   `404 != holiday` property (use
   `tools/p0_qualification/common/synthetic.py:daily_index_router` with
   `index_body=None` on a real business day and confirm the collector reports
   `COVERAGE_UNKNOWN`/a gap kind, never a holiday inference — grep
   `collector.py` for `DAILY_INDEX_UNAVAILABLE` / `DAILY_INDEX_GAP`). Cite
   `tests/test_p0_continuity_compression.py`'s existing holiday/weekend/DST
   tests the same way `timing_matrix.py` cites A3 tests; do not duplicate
   what they already prove.
2. **`gate_a/long_history.py`** (Phase A5 / mission section 8.C) — long
   synthetic-history stress using `SyntheticEnvironment` +
   `FrozenTimebase.advance()`, at least the former P14D horizon (14+ virtual
   days), asserting via `audit_observation_window` (or the lower-level
   `SchedulerJournal`/obligation reconciliation) that: no obligation
   disappears, none resolves twice, no post-hoc supersession erases a miss,
   fingerprint stays stable, state stays bounded. Try to meet or exceed the
   prior 2,016-obligation stress level mentioned in the mission if
   practical — check whether that figure traces to an existing test/branch
   before assuming it must be re-derived from scratch.
3. **`gate_a/fault_matrix.py`** (Phase A4/D) — ledger mapping every
   durability-critical transition in the mission's minimum list to either an
   existing citation (most already exist — see
   `tests/test_p0_deployment_boundaries.py`,
   `tests/test_astra_pre_t0.py` Phase 4/5) or a `TARGET_HOST_ONLY` residual
   classification for Gate B. Add the `restart_burst_limit` count-boundary
   test here if not done in step 1's cleanup.
4. **`gate_a/property_campaign.py`** (A/E randomized campaign) — optional per
   mission wording ("if useful"); lower priority than 1–3.
5. **`discrimination/known_bad_replay.py`** (mission Phase C / section 9) —
   replay a subset of the harness's discriminating tests (start with the
   Phase8EffectiveUnitDigestStabilityCampaign-equivalent boundary check
   against the **pre-fix** baseline `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`
   — i.e., load `deploy/quant_sec_supervisor.py` from that historical commit
   via `git show <sha>:deploy/quant_sec_supervisor.py` written to a temp file
   and loaded through `launcher_loader.load_launcher`) and prove
   KNOWN_BAD → RED, FROZEN_V4 → GREEN. Do not modify the historical branch;
   read its blob only.
6. **`gate_b/target_host_tooling.py`** (Phase D) — READ_ONLY/PLAN/DRY_RUN by
   default; must refuse to run destructive operations without an explicit
   operator flag; must never run automatically from CI.
7. **`gate_c/event_window_planner.py`** and **`gate_c/continuity_verifier.py`**
   (Phase E/F) — planner is pure calendar computation (reuse
   `calendar.py` + the 30h settle rule) that never declares t0; verifier
   should be a thin, well-tested wrapper around
   `audit.audit_observation_window(collector, window_start=<declared t0>)`.
8. **`gate_d/evidence_binder.py`** (Phase G) — consumes the above artifacts,
   rejects mismatched SHA/tree/stale manifest/missing gate per mission
   section 13.
9. **P14D evidence package** (Phase H) — a markdown deliverable in `handoff/`
   (not `governance/` — that's Blue's authority space; Builder does not write
   there) answering, per property, `NO_UNIQUE_P14D_ONLY_PROPERTY_FOUND` or
   naming the exception. Draft from
   `governance/BLUE_P0_GATE_A_EVIDENCE_MATRIX_2026-09-20.md`'s TARGET_ONLY/
   LIVE_ONLY rows (section 2 above) updated for V4.
10. **Dedicated CI workflow** for the qualification harness
    (`.github/workflows/p0-qualification-harness.yml` — new file, does not
    touch the existing `sec-p0-pre-t0-gate.yml`), running
    `python3 -m tools.p0_qualification.gate_a.timing_matrix` (and siblings as
    they're built) on `builder/**` pushes, same pattern as the existing gate.
11. A small self-test file, e.g. `tests/test_p0_qualification_harness.py`
    (allowed: `tests/**` is in the immutability boundary's allowed-changes
    list) asserting the harness modules run and produce `NON_ISSUE`-only
    reports at HEAD — keeps the harness itself honest under the existing
    `python3 -m unittest discover -s tests` invocation without polluting the
    production suite's file count/semantics.
12. Only after 1–9 are in reasonable shape: push, let
    `sec-p0-pre-t0-gate.yml` + the new qualification workflow run on this
    branch, record the exact-head CI run ids, then write
    `handoff/BUILDER_P0_HYBRID_QUALIFICATION_HANDOFF_2026-09-20.md` (the
    **final** handoff, per mission section 17 — do not write it until the
    above is substantially done; this checkpoint is intentionally not that
    file).

## 6. Boundaries a resuming session must keep

- **Never** modify `blue/p0-gate-a-v4-frozen-2026-09-20`,
  `astra/p0-gate-a-v4-independent-audit-2026-09-20`, or any file under
  `src/`, `deploy/`, `tests/` (existing files), `scripts/`,
  `.github/workflows/sec-p0-pre-t0-gate.yml`. New files under `tests/` and a
  new dedicated workflow file are fine (see mission section 5).
- If any harness campaign reveals a **REAL_DEFECT** in the frozen candidate,
  stop the production-fix path immediately: preserve the red evidence, commit
  it, classify it, and return the finding to Blue in the checkpoint/handoff
  rather than patching `src/`/`deploy/` from this branch. (See mission
  section 5 / 18.) No such defect has been found so far — everything in
  section 4.3 is `NON_ISSUE`.
- Do not declare t0, amend P14D, or claim target-host/live-source evidence
  from anything this harness runs in repository CI. Every generated report
  already sets `no_t0_declared`/`no_target_host_claimed`/
  `no_p14d_amendment_claimed` to `true` in `common/evidence.py:Report` — keep
  that convention in every new gate module.
- Keep evidence artifacts reproducible: every `EvidenceRecord` should carry
  either a `reproduce_command` or an explicit citation; avoid unreplayable
  randomized results (mission section 8.E — deterministic seed + minimal
  replay command is mandatory for any randomized campaign).

## 7. Open questions for Blue (do not resolve unilaterally)

None yet raised — no REAL_DEFECT, no scope ambiguity encountered so far that
required stopping. If one arises in later phases, add it here rather than
guessing.
