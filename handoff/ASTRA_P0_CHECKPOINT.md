# CHECKPOINT ASTRA P0 — final repository-side Phase-7 handoff

This section supersedes stale status/next-action statements below. Later target-runtime
evidence, when it exists, must supersede this repository-side checkpoint.

* timestamp UTC: 2026-09-20T00:26:21.773782+00:00
* branch: `astra/p0-deep-adversarial-pre-t0`
* exact HEAD SHA of the tested code candidate before this documentation-only checkpoint: `88566cb4fb08bdf01561ffcbfe18fd391e57c572`
* checkpoint-containing HEAD: intentionally resolve with `git log -1 --format=%H -- handoff/ASTRA_P0_CHECKPOINT.md`; a commit cannot truthfully contain its own SHA
* parent/base SHA: mission entry `8dbe25aea136332f73174917af42dc524f8454e7`; tested code candidate tree `061a9eb73a45c76184aa18f30dd7aacbe9b8ae15`
* t0 status: **NOT DECLARED**
* P0_CONTINUOUS_SERVICE_STATE: **OPEN / NOT_YET_PROVEN_CONTINUOUS**

## Deployment-isolation decision

Durable decision memo: `governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md`.

Repository development, Product integration and the qualifying P0 runtime are separate states.
Keep the conservative acquisition fingerprint. Do **not** narrow the SEC import closure merely
to reduce merge friction. The accepted target topology, subject to target-host verification, is
a complete immutable detached release under `/opt/quant-releases/<exact-git-sha>/`, presented
through the existing fixed `/opt/quant` service view, with persistent writable P0 state backed
by `/var/lib/quant-p0/` and mounted at `/opt/quant/var`. Development/integration live elsewhere.
GitHub branch motion alone has no runtime authority. An intentional release replacement is a
deployment event with explicit one-use deployment authority and lifecycle evidence.

The current `WorkingDirectory=/opt/quant` / `--root /opt/quant` contract does not prevent this
isolation and was not changed. No Economic V2 or Forward Data branch was merged.

## defects CONFIRMED OPEN

None known in the repository in the classes
`BLOCKS_CAPTURE_INTEGRITY`, `BLOCKS_PIT_RECONSTRUCTABILITY`, or
`BLOCKS_ANTI_SELECTION_OR_VISIBILITY_FIREWALL` after the tested candidate below.

Target-runtime entrance conditions are still unproven facts, not repository defects.

## defects CONFIRMED CLOSED this campaign

### RAW_OBJECT_DIRECTORY_DURABILITY_GAP — BLOCKS_PIT_RECONSTRUCTABILITY

Scenario/reproduction: raw publication uses a content-addressed hardlink. Before the fix, if
the hardlink became visible and directory `fsync` then failed/crashed, a restart seeing the
same bytes returned the deduplication immediately without re-establishing directory durability.
Also, a lazily-created two-hex hash-prefix directory was never `fsync`ed in its parent before
objects were published beneath it. Visibility of a pathname is not proof that its directory
entry survived a power-loss boundary.

Red discriminants are durable in `tests/test_p0_deployment_boundaries.py`:
* `test_retry_after_directory_fsync_failure_revalidates_durability`;
* `test_new_hash_prefix_is_fsynced_in_its_parent`.

The first test injects failure specifically after the hardlink, at the containing directory
`fsync`; an earlier version of the test failed too early after the new pre-publication sync and
was corrected to hit the intended crash boundary.

Minimal correction in `src/quant/dataplane/sec/store.py`:
* a deduplicated existing object re-`fsync`s the parent-of-prefix and object directory before ACK;
* creation of a hash-prefix directory is made durable in its parent before object publication;
* an `OSError` during revalidation fails closed as `SecStorageFailure`.

Green proof: exact-head run `35478291920` on candidate `88566cb4...` is
COMPLETED/SUCCESS; full unit discovery 380/380 PASS. This change is acquisition-fingerprint
critical because `store.py` is in the acquisition closure. All earlier materialized fingerprints
and rodages are superseded for a future qualifying candidate.

## hypotheses tested and NOT reproduced as defects

* **Real Linux SIGTERM supervisor/child boundary.** A real supervisor subprocess and real child
  process were exercised. SIGTERM to the supervisor produced a clean witnessed child stop; a
  replacement supervisor over the same durable state classified its first launch `MANUAL_START`.
  No false automatic continuity was reproduced.
* **Real Linux SIGKILL/PDEATHSIG boundary.** SIGKILL of the supervisor killed the child through
  the configured parent-death signal; a replacement supervisor again defaulted to
  `MANUAL_START`. No false continuity was reproduced.
* **`sec-audit` stdout proxy leak.** The literal CLI output was exercised after realistic
  synthetic capture activity and passed both `assert_no_count_proxies` and
  `assert_no_scientific_content`. No new protocol-visible count/content proxy was reproduced.

These Linux process tests are not an assertion about actual target systemd control-group behavior.
Real `systemctl stop/start`, loaded-unit behavior and host-level kill/reboot boundaries remain
target-rodage observations.

Previously closed/falsified hypotheses remain closed and were not reopened: restart-burst
exhaustion false continuity; create-once/materialized-fingerprint race; 403/429 cooldown-to-attempt
crash accounting.

## tests rouges ajoutés

* `tests/test_p0_deployment_boundaries.py::RawPublicationDurabilityTests` — two PIT durability
  crash-boundary discriminants.
* Process/firewall tests were added as falsification tests; they did not expose a new defect.

## tests verts obtenus / full-suite status

Exact tested code candidate: `88566cb4fb08bdf01561ffcbfe18fd391e57c572`.

GitHub Actions run `35478291920`: **COMPLETED / SUCCESS**.
* generated-schema drift: PASS
* status-artifact freshness: PASS
* full unit suite: **380/380 PASS**
* explicit SEC P0 lane suite: **271/271 PASS**
* V1 end-to-end regression: PASS
* exact-head verification artifact generation/check: PASS
* clean working tree: PASS

Exact-head verification artifact:
* GitHub artifact id: `10595186792`
* name: `sec-p0-verification-88566cb4fb08bdf01561ffcbfe18fd391e57c572`
* artifact digest: `sha256:d5effcc84ff66ada3f97ba68551fe165504e76e930335a9b43f34958aeda8a16`
* verified SHA: `88566cb4fb08bdf01561ffcbfe18fd391e57c572`
* Git tree: `061a9eb73a45c76184aa18f30dd7aacbe9b8ae15`
* verified input-tree digest:
  `sha256:744d699d060be21d0f27b4bbefbb7ab4f538ee41a0e72d8e9d0d7c1665f1cd6d`
* artifact recorded at: `2026-09-20T00:24:41.265501+00:00`
* CI environment: CPython 3.12.14, Linux Azure runner; network requests made: 0.

## fingerprint / manifest / evidence state

* active fingerprint: **NOT MEASURED IN THE FINAL TARGET RUNTIME**
* materialized fingerprint: **NOT AVAILABLE FOR THE FINAL TARGET RUNTIME**
* manifest schema/version: `p0_materialized_fingerprint/v2`;
  semantic fingerprint schema `acquisition_critical_fingerprint/v1`
* final target-runtime rodage status + exact artifact: **NOT RUN / DOES NOT EXIST**
* readiness status: **READY_FOR_FINAL_RODAGE = FALSE**
* audit status: repository audit/falsification regressions green; target exact-runtime final audit pending
* firewall status: repository public/protocol regressions including dedicated `sec-audit` stdout
  are green; target access/mount/operator-surface isolation remains to be verified
* 14-day continuity proof: **NOT PROVEN**

`READY_FOR_FINAL_RODAGE = FALSE` is not a request for more repository architecture work. The
remaining evidence is target-specific: no actual pinned release, mounts, production systemd,
private requester identity, target materialization or target lifecycle authority was available
to this session.

## fichiers acquisition-critical modifiés

* `src/quant/dataplane/sec/store.py` — **YES, fingerprint-critical**, for the durability fix above.

Other changes in this campaign:
* `tests/test_p0_deployment_boundaries.py` — tests only;
* `governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md` — deployment decision memo;
* `STATE.md` — canonical test inventory refresh;
* this checkpoint — handoff only.

The documentation-only checkpoint commit changes the repository SHA but does not change acquisition
semantics. A final target release must nevertheless pin the exact commit it actually deploys.

## exact remaining conditions before final target-runtime rodage

1. Select the exact release commit/tree only after this checkpoint is durable and its exact-head
   CI is green.
2. Instantiate and verify the pinned release topology from the deployment contract:
   immutable backing release, fixed `/opt/quant` view, persistent `/var/lib/quant-p0` state
   mount, code read-only outside `var`, mount-before-service fail-closed behavior.
3. Verify target filesystem semantics required by the store and journals; verify single P0 writer
   and one global SEC requester-budget authority.
4. Bind the actual target interpreter/runtime image/OpenSSL/private requester identity/effective
   SEC configuration.
5. Verify the loaded production systemd fragment, effective values and digest, with no unbound
   drop-in/override.
6. Materialize the v2 manifest in that exact effective service environment and prove
   ACTIVE_RUNTIME_FINGERPRINT == MATERIALIZED_FINGERPRINT with no integrity latch.
7. Record/consume explicit deployment authority and bind lifecycle provenance.
8. Execute bounded target pre-t0 fault checks, including actual `systemctl stop/start` and
   host/supervisor kill behavior, using synthetic/offline state where destructive.
9. Execute the final live target rodage on the same exact state and produce an artifact outside
   the immutable release that binds SHA + Git tree + verified input-tree digest + acquisition
   fingerprint + full manifest/schema + effective runtime config/image + repository and loaded
   service digests + exact CI run id + UTC interval + lifecycle/authority references. Verify the
   bindings both before and after rodage and publish only opaque verdicts.

Rodage success would establish readiness for Blue to decide what happens next. It does not
declare t0 and cannot prove the required 14 days.

## prochaine action unique

**Stop repository Phase-7 expansion. Instantiate/verify the target pinned P0 release contract and
run the final target-runtime entrance checks/rodage.** Reopen repository code only if that target
falsification produces concrete evidence of a class 1–3 defect.

## commandes exactes nécessaires pour reproduire/reprendre

Repository:
```bash
git fetch origin astra/p0-deep-adversarial-pre-t0
git checkout astra/p0-deep-adversarial-pre-t0
git pull --ff-only origin astra/p0-deep-adversarial-pre-t0
cat governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md
PYTHONPATH=src python3 -m unittest tests.test_p0_deployment_boundaries -v
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/status_artifacts.py --check
git diff 8dbe25aea136332f73174917af42dc524f8454e7..HEAD
```

Target evidence inspection (do not substitute these reads for the full contract):
```bash
systemctl cat quant-sec-capture.service
systemctl show quant-sec-capture.service --no-pager
```

t0 = NOT DECLARED

P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS

---

# CHECKPOINT ASTRA P0 — deployment isolation campaign

This section supersedes stale next-action/status statements below.

* timestamp UTC: 2026-09-19T23:57:29.850972+00:00
* branch: `astra/p0-deep-adversarial-pre-t0`
* exact HEAD SHA / parent/base SHA at campaign entry: `8dbe25aea136332f73174917af42dc524f8454e7`
* this checkpoint commit: resolve with `git log -1 --format=%H -- handoff/ASTRA_P0_CHECKPOINT.md`; no self-referential SHA claim
* t0 status: NOT DECLARED
* P0_CONTINUOUS_SERVICE_STATE: OPEN / NOT_YET_PROVEN_CONTINUOUS
* defects CONFIRMED OPEN: none newly confirmed at this checkpoint
* defects CONFIRMED CLOSED: prior committed closures retained below; none newly claimed
* hypotheses NOT YET REPRODUCED: real process signal/death boundaries, raw publication durability after interrupted fsync, CLI stdout firewall
* tests rouges ajoutés: none yet
* tests verts obtenus: prior exact-head CI only at this checkpoint
* full-suite status: baseline exact-head CI SUCCESS
* CI run id/status: 35476749853 COMPLETED/SUCCESS on exact entry SHA; successor CI pending
* active fingerprint: NOT MEASURED IN TARGET RUNTIME
* materialized fingerprint: NOT AVAILABLE IN TARGET RUNTIME
* manifest schema/version: p0_materialized_fingerprint/v2; acquisition_critical_fingerprint/v1
* rodage status + exact artifact: NOT RUN; no final artifact
* readiness status: READY_FOR_FINAL_RODAGE = FALSE; target prerequisites unverified
* audit status: target-runtime final audit pending
* firewall status: existing CI green; dedicated CLI stdout regression pending
* fichiers acquisition-critical modifiés: none
* prochaine action unique: falsify raw publication retry durability, then real process signal boundaries
* commandes exactes nécessaires pour reproduire/reprendre:
  `git fetch origin astra/p0-deep-adversarial-pre-t0 && git pull --ff-only origin astra/p0-deep-adversarial-pre-t0`
  `cat governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md`
  `PYTHONPATH=src python3 -m unittest tests.test_astra_pre_t0 -v`

The dedicated release contract is durable in governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md.
No import narrowing, WorkingDirectory change, target deployment, other branch merge or scientific change.
The local container has PID 1 `codex`, and systemctl explicitly reports systemd unavailable;
local signal tests must not be labelled actual systemd stop/start proof.
Already falsified materialization, restart-limit, and 403/429 accounting hypotheses are NOT reopened.

---

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
* CI run for the code fix (`ea86d6b4`): GitHub Actions run **35476131802**, "SEC P0 pre-t0 gate",
  **COMPLETED / SUCCESS** (all steps green: schema drift, status freshness, full unit suite,
  SEC P0 lane, V1 end-to-end, exact-head verification artifact, clean working tree). The follow-up
  documentation-only commit (`dbbdbe56`, this checkpoint's falsification notes) also triggers its
  own CI run; no code changed since `ea86d6b4` so it is not separately gate-relevant.

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
