# CHECKPOINT ASTRA P0

* timestamp UTC: 2026-09-19T23:30:00Z
* branch: `astra/p0-deep-adversarial-pre-t0` (single branch; no new branch created)
* HEAD SHA at start of this session: `288d224fc3f2830add4338c9875d9fd50ab174e2` (PR #18 merge commit, verified against remote before any work)
* parent/base SHA: PR #18 merge `288d224fc3f2830add4338c9875d9fd50ab174e2`; phase-6 documentation-binding correction `a321bfd9d77d42bb43a4fcd8b774a6eb38789179`; phase-6 verified code `b42ae73a805cc8a137561239c60fe917daf83c7b`
* t0 status: **NOT DECLARED**
* P0_CONTINUOUS_SERVICE_STATE: **OPEN / NOT_YET_PROVEN_CONTINUOUS**

## This session: Phase 7 campaign start

Scope for this increment: Phase 7 priority #3 (EFFECTIVE SYSTEMD CONTRACT) from the mission brief,
plus adversarial falsification of Phase 7 priority #1 (RESTART LIMIT EXHAUSTION).

### defects CONFIRMED CLOSED this session

- `SYSTEMD_EFFECTIVE_TIMING_AND_SIGNAL_NOT_VALIDATED` — **BLOCKS_CAPTURE_INTEGRITY**.
  - Scenario: `_effective_systemd_definition()` in `deploy/quant_sec_supervisor.py` fetched
    `RestartUSec`, `StartLimitIntervalUSec`, `KillSignal` and `TimeoutStopUSec` from `systemctl
    show` and folded them into the fingerprint digest, but only ever *validated* `Restart`,
    `KillMode` and `StartLimitBurst` against expected values. The other four properties could
    silently diverge from what the repository unit file declares (stale `daemon-reload`,
    hand-edited running unit, corrupted deploy) with no `RuntimeError` raised — the drift would
    just become a new, unaudited fingerprint input rather than a fail-closed rejection.
  - Reproduction (red, confirmed locally before the fix): with every other property matching the
    frozen unit exactly, `KillSignal=9` (SIGKILL instead of the declared SIGTERM) and, separately,
    `RestartUSec=1ms` / `StartLimitIntervalUSec=1ms` / `TimeoutStopUSec=1ms` (restart-storm
    protection and shutdown grace period effectively disabled) were both silently accepted with no
    exception. A SIGKILL-only shutdown path means the process can never flush/fsync
    raw-object/envelope/attempt-journal writes on stop — a direct capture-integrity /
    PIT-reconstructability risk at exactly the crash boundary this program audits.
  - Minimal correction: added `EXPECTED_KILL_SIGNAL` (derived from `signal.SIGTERM`, not a bare
    literal) to the existing exact-match `expected` dict, and a small `_systemd_duration_seconds()`
    parser (handles systemd's pretty-printed `us/ms/s/min/h` duration format) to numerically
    compare `RestartUSec`/`StartLimitIntervalUSec`/`TimeoutStopUSec` against
    `RESTART_DELAY_SECONDS` / `RESTART_BURST_WINDOW_SECONDS` / the new `TIMEOUT_STOP_SECONDS`
    constant, with a 1-second tolerance for pretty-print rounding. An unparseable duration raises
    rather than being treated as `0.0`.
  - Red→green test: `tests/test_astra_pre_t0.py::Phase7EffectiveSystemdContractCampaign` (4 new
    tests: consistent-unit accepted, KillSignal→SIGKILL rejected, each of the three timing
    properties independently rejected when drifted, unparseable duration rejected). Existing
    `Phase5AuthorityBindingCampaign.test_effective_systemd_restart_policy_mismatch_is_rejected`
    still passes unchanged (no regression).
  - Fingerprint impact: `_effective_systemd_definition()`'s return value flows into
    `supervisor_manifest()` → `acquisition_critical_fingerprint()` (confirmed by reading
    `fingerprint.py`), so this correction changes the acquisition-critical fingerprint. This is a
    fingerprint-critical file per the header comment in `deploy/quant-sec-capture.service`.
  - Rodage impact: none yet — no rodage has run since this correction; any future qualifying `t0`
    must be materialized on code that includes this fix, not before it.

### hypothesis tested and NOT reproduced (recorded per method: falsification attempted, defect did not exist)

- **Restart-burst exhaustion → fictitious continuity.** Concern: when the supervisor's *internal*
  child-restart loop exhausts `RESTART_BURST_LIMIT` and the process returns/exits, does systemd's
  subsequent fresh OS-level restart of the supervisor get incorrectly self-attributed
  `AUTOMATIC_RESTART_AFTER_FAILURE` (positive/non-invalidating), producing fictitious continuity?
  - Method: loaded the real `deploy/quant_sec_supervisor.py` twice as two independent module
    instances (simulating two separate OS processes sharing one `--root`), first exhausting its
    own internal burst limit against an always-failing fake child, then invoking a second, fresh
    `main()` to represent systemd's next `Restart=on-failure` launch. Inspected the *first*
    `CHILD_LAUNCH_AUTHORIZED` event of the second process's `supervisor_id` in
    `supervisor_events.jsonl` (not the final state snapshot, which can reflect a later internal
    iteration and gave a misleading first reading during this investigation).
  - Result: the second process's first launch is classified `MANUAL_START`, which **is** in
    `supervisor.INVALIDATING_CAUSES`. `classify()` never reads `previous` state and only returns
    `AUTOMATIC_RESTART_AFTER_FAILURE` when `witnessed_child_failure=True` is explicitly passed by
    the *same, still-live* process's own internal loop — a fresh process launch never sets that
    flag on its first iteration. Confirmed: no fictitious continuity across a burst-exhaustion →
    systemd-restart boundary under the current code. Not promoted to a defect.
  - Residual, non-blocking observation (not a defect under the class-1/2/3 test): the internal
    burst-exhaustion exit path appends no distinct `RESTART_BURST_EXHAUSTED`-style event before
    returning — the terminal `CHILD_EXIT_OBSERVED` looks the same as an ordinary mid-loop failure.
    This is a diagnostic/observability quality gap only: `MANUAL_START`'s default-invalidating
    classification already makes the window-safety outcome correct regardless, so per the burden-
    of-proof rule this is not classified as a P0 blocker. Left as a note for anyone doing incident
    forensics, not for this campaign to act on further.

- **Concurrent/interrupted fingerprint materialization** (`collector.materialize_fingerprint()` /
  `state.create_json_once`). Concern: two racing materializers, or a crash between temp-write,
  fsync and the durable create-once step, producing a partial or double-accepted freeze.
  - Method: read (not executed as a new test — this is code-reading falsification, method
    explicitly allows this) `create_json_once`: unique `tempfile.mkstemp` per caller, full
    write+flush+fsync of the temp file, then `os.link(temporary, path)` (atomic add-only rename
    substitute — fails `FileExistsError` if `path` already exists), then `_fsync_directory`, then
    unlink the temp name. `materialize_fingerprint()` explicitly handles the `FileExistsError` race
    by re-validating the winner's content against this process's own computed fingerprint rather
    than assuming success.
  - Result: no crash window produces a torn or double-written `acquisition_fingerprint.json`.
    Worst case of a crash before `os.link` is an orphaned temp file and a retryable empty target;
    worst case of a crash after `os.link` but before the final `unlink` is a harmless leftover hard
    link to already-durable content. Not promoted to a defect.

- **Budget/attempt write-ordering across a 429/403 crash boundary**
  (`collector._request_serialized`, `budget.enter_cooldown`, `audit._validate_request_accounting`).
  Concern: on a 429/403, `budget.enter_cooldown()` is called and durably persisted *before* the
  attempt journal's `FINISHED` event and `store.record_attempt()`. A crash in that window would
  leave `request_intents.jsonl` with INTENT/RESERVED/RECEIVED but no FINISHED, and no matching
  completed record in `store.attempts()` for that attempt id.
  - Method: read `_request_serialized` call order plus `_validate_request_accounting` in
    `audit.py`, which independently builds `by_attempt` from the intent journal and
    `attempt_by_id` from completed attempt records.
  - Result: this exact gap is already caught — `attempt_by_id.get(attempt_id) is None` yields
    both `REQUEST_INTENT_WITHOUT_ATTEMPT` and `REQUEST_ACCOUNTING_INCOMPLETE`, which makes
    `audit_observation_window` report `accountable=False` for a window containing the crash. The
    durable cooldown itself is independent of the attempt record (`budget.json`), so a restart
    still correctly refuses to poll through the cooldown even though the triggering attempt is
    unaccounted for — no silent hot-loop, only a (correct) non-accountable window. Not promoted to
    a defect.

### test-coverage observation (not a defect, not acted on this session)

`scripts/quant.py sec-audit`'s CLI stdout manually whitelists 5 keys from the full audit report
before printing (`accountable, findings, fingerprint_stable, coverage_state,
p0_continuous_service_state`), and `findings` values are confirmed-static uppercase codes (no
`findings.append(f"...")` interpolation exists in `audit.py`), so the current output is firewall-safe
by construction. But unlike `telemetry()`/the public snapshot/`CHIEF_BRIEF.md`, no test actually
runs `find_leaks`/`find_count_proxies` against this CLI's literal stdout — a future field added to
that manual allowlist would not be caught by any existing regression test. Attempting to add this
test hit real friction: `sec-audit --root <fresh temp dir>` fails before producing JSON, because
`fingerprint.py`'s `module_digests()` requires `.github/workflows/sec-p0-pre-t0-gate.yml` to exist
under `--root` (fingerprint-critical CI workflow), so a temp-dir invocation needs either a real
checkout copy or `--root` pointed at the repo itself with an isolated `var/`. Left for a future
session rather than forced under this checkpoint's time budget.

### defects CONFIRMED OPEN

None newly opened this session beyond what remains in the "hypotheses NOT YET REPRODUCED" list.

### hypotheses NOT YET REPRODUCED (carried forward, Phase 7 still incomplete)

SIGTERM/systemctl stop-start semantics beyond what Phase 5 already covers; supervisor SIGKILL
child-death behavior; truly concurrent/interrupted materialization (two materializers racing,
temp/write/fsync/rename interruption, stale/foreign-host manifest); deeper budget/state journal
failure ordering (DNS/connect/TLS failure, 403/429/Retry-After/5xx interaction with reconnect,
lock-holder death, two-process competition beyond the existing max-concurrency test); remaining PIT
crash boundaries (ENOSPC, partial append, torn JSONL, rename interruption, rollback, duplicate
replay, state-newer-than-journal / journal-newer-than-state); remaining public/protocol proxy leaks
beyond the existing public-snapshot tests; final evidence binding (commit SHA + tree digest +
fingerprint + manifest schema + effective runtime config + effective service digest + CI run id +
timestamp + lifecycle provenance, all bound together in one artifact); final exact-head rodage.

## Verification (local, this session)

* red tests (pre-fix, confirmed locally, not committed): ad hoc probes reproducing
  `KillSignal=9` and `RestartUSec/StartLimitIntervalUSec/TimeoutStopUSec=1ms` silently accepted by
  `_effective_systemd_definition()`.
* green tests: `PYTHONPATH=src python3 -m unittest tests.test_astra_pre_t0.Phase7EffectiveSystemdContractCampaign -v` — 4/4 PASS.
* full-suite status: **375/375 PASS** (was 371; +4 new Phase 7 tests).
* SEC P0 lane (`tests.test_sec_form4_capture tests.test_p0_adversarial tests.test_astra_pre_t0`): **271/271 PASS**.
* V1 end-to-end (`scripts/demo_quant_system.py`): **35/35 checks PASS**.
* `scripts/generate_schemas.py --check`: **PASS** (no schema drift).
* `scripts/status_artifacts.py --check`: **PASS** after `--write` regenerated `STATE.md`'s proof
  inventory line (371 → 375) to match authoritative package discovery; `CHIEF_BRIEF.md` was
  already fresh.
* CI run: **not yet triggered for this commit** — this checkpoint is being pushed now; the next
  session/CI observer should confirm the exact-head GitHub Actions run for the commit this
  checkpoint accompanies before treating it as gate-equivalent to a green CI run.

## Fingerprint / rodage / readiness (unchanged claims from prior checkpoint, still true)

* active fingerprint: NOT MEASURED IN ACTUAL SERVICE RUNTIME
* materialized fingerprint: NOT AVAILABLE
* manifest schema/version: `p0_materialized_fingerprint/v2`; `acquisition_critical_fingerprint/v1`; final freeze not performed
* final rodage exact artifact/status: **NOT YET RUN** on final code/target runtime
* 14-day continuity: **NOT PROVEN**; no claim is made about the required weekend or silence interval
* readiness: local discriminants green; final target-runtime readiness NOT ESTABLISHED
* audit: local authority/readiness consistency green; final coherent exact-head audit pending
* firewall: prior regressions green in the 375-test suite; final broad audit pending

## Acquisition-critical files changed this session

- `deploy/quant_sec_supervisor.py` — fingerprint-critical (see file header); this session's edit
  changes the acquisition-critical fingerprint the next time it is materialized.
- `tests/test_astra_pre_t0.py` — test-only, not fingerprint-critical.
- `STATE.md` — regenerated status artifact (proof inventory count), not fingerprint-critical.

## Next unique action

Continue Phase 7 against the "hypotheses NOT YET REPRODUCED" list above. Suggested next target:
concurrent/interrupted materialization (temp/write/fsync/rename interruption and stale/foreign-host
manifest), since it is a distinct capture-integrity surface from what this session covered and has
not yet had a dedicated adversarial pass in this campaign.

## Exact resume commands

- `git fetch origin astra/p0-deep-adversarial-pre-t0 && git checkout astra/p0-deep-adversarial-pre-t0 && git pull --ff-only`
- `PYTHONPATH=src python3 -m unittest tests.test_astra_pre_t0.Phase7EffectiveSystemdContractCampaign -v`
- `PYTHONPATH=src python3 -m unittest discover -s tests`
- `PYTHONPATH=src python3 -m unittest tests.test_sec_form4_capture tests.test_p0_adversarial tests.test_astra_pre_t0`
- `python3 scripts/demo_quant_system.py`
- `python3 scripts/status_artifacts.py --check`
- `git diff 288d224fc3f2830add4338c9875d9fd50ab174e2..HEAD`

No merge, no Blue review request, no t0 declaration, and no claim that any of the above proves the
14-day window.
