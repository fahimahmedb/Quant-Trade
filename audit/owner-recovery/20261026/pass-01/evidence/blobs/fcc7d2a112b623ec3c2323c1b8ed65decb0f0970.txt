# BLUE — P14D Challenge: Evidence-Based Continuity Qualification — 2026-09-20

## Status

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

`P14D_TECHNICAL_RECOMMENDATION = REPLACE_FIXED_DURATION_WITH_HYBRID_EVIDENCE_CONTRACT`

`t0 = NOT DECLARED`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

This memo is a Blue technical decision record, not yet the amendment that changes the frozen P14D authority.

## 1. Question

Does `P0_CONTINUOUS_OBSERVATION_MIN = P14D` provide indispensable evidence that cannot be obtained faster and more directly through deterministic/accelerated time, fault injection, process/supervisor tests, target-host failure tests and a bounded real live rodage?

North-Star constraint: calendar waiting is not a terminal objective. We should preserve only the real evidence value needed for capture integrity, PIT reconstructability and the anti-selection/visibility firewall.

## 2. Where P14D came from

The current rule is frozen in:
- `handoff/BLUE_CHECKPOINT_2026-09-18_P0_CONTINUITY.md`;
- `governance/BLUE_P0_RAW_CAPTURE_CHECKPOINT_ADDENDUM_2026-09-18.md`.

The rule requires at least 14 consecutive calendar days plus:
- one complete weekend;
- one predeclared source-normal silence interval;
- prospective scheduler-state provenance;
- external lifecycle provenance;
- a prospectively materialized acquisition-critical fingerprint;
- no invalidating intervention;
- retrospective accounting of every expected acquisition action.

The same governance identifies three operational claims the window was intended to support:
1. unattended continuity;
2. restart durability;
3. discovery fail-closed.

`QUANT_NORTH_STAR.md` does not specify 14 days. The governing P0 documents read for this challenge state the number as a frozen minimum but do not provide an empirical failure-rate derivation for the number 14 itself.

## 3. Prior art

### SQLite

SQLite explicitly performs crash and power-loss testing in simulation. Its crash VFS can reorder/corrupt unsynchronized writes, crash at different points, restore snapshots and verify atomic recovery. It also performs I/O-error, OOM, compound-failure and resource-leak tests.

Sources:
- https://www.sqlite.org/testing.html
- https://sqlite.org/atomiccommit.html

Transferable lesson: power-loss correctness is better attacked by controlled crash-point coverage than by hoping a long soak naturally hits the right boundary.

### RocksDB

RocksDB runs randomized black-box and white-box crash tests. Black-box uses `kill -9`; white-box crash points are placed before/after filesystem operations. State is verified after restart, including comparison with an external log. The project describes continuous crash testing as complementary to deterministic unit tests.

Source:
- https://github.com/facebook/rocksdb/wiki/Stress-test

Transferable lesson: combine repeated crash/restart, randomized operation sequences and an external oracle.

### FoundationDB

FoundationDB uses a combined regime of deterministic simulation, live performance tests and hardware-based failure testing. Simulation accelerates time, injects machine/network/disk/reboot failures and makes failures reproducible by seed. FoundationDB explicitly treats simulation and physical/live testing as complementary.

Sources:
- https://apple.github.io/foundationdb/testing.html
- https://apple.github.io/foundationdb/client-testing.html

Transferable lesson: compress logical/calendar state-space in simulation, then reserve real time for physical/runtime properties that simulation cannot honestly prove.

### TigerBeetle

TigerBeetle's VOPR simulator injects storage faults and can speed up time dramatically while exercising the actual implementation deterministically.

Source:
- https://github.com/tigerbeetle/tigerbeetle/blob/main/docs/ARCHITECTURE.md

Transferable lesson: long calendar duration is not the only way to exercise long state histories.

### etcd

etcd had a real durability gap where a WAL rename could be visible but not durable because the parent directory was not fsynced. The issue reports that the data-loss case was reproduced with their testing framework.

Source:
- https://github.com/etcd-io/etcd/issues/6368

Transferable lesson: this is the same bug class Astra just found in P0 raw-object publication; explicit filesystem-boundary fault injection is high-value.

### Git

Git distinguishes ordinary visibility/writeback from hardened durable state and has explicit fsync policies/transactions before final object exposure.

Sources:
- https://github.com/git/git/blob/master/object-file.c
- https://github.com/git/git/blob/master/Documentation/config/core.adoc

### systemd / Linux supervision

systemd's own integration tests explicitly signal/kill units and verify state/restart behavior. systemd service semantics also distinguish graceful SIGTERM from eventual forced SIGKILL after stop timeout.

Sources:
- https://github.com/systemd/systemd/blob/main/test/units/TEST-59-RELOADING-RESTART.sh
- https://github.com/systemd/systemd/blob/main/man/systemd.service.xml

### SEC calendar authority

Current SEC guidance says EDGAR accepts filings from 06:00 to 22:00 Eastern Time Monday through Friday except federal holidays. SEC guidance also says daily indexes are updated nightly beginning around 22:00 ET and usually complete within a few hours.

Sources:
- https://www.sec.gov/submit-filings/filer-support-resources/how-do-i-guides/determine-status-my-filing
- https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data

Transferable lesson: a normal overnight closure and a complete weekend are prospectively knowable source-silence states; they do not require a two-week wait to encounter.

## 4. What Quant P0 already compresses

Current Astra candidate has an injectable `FrozenTimebase`; tests can advance cadence, backoff and cooldown without sleeping. P0 also has real calendar logic: daily-index reconciliation waits `DAILY_INDEX_SETTLE_HOURS = 30` and deliberately skips weekend target days (`day.weekday() < 5`). That means weekend semantics are a genuine boundary, but the branch logic itself can be exercised deterministically with the injected timebase.

The scheduler creates named prospective obligations with `next_due_at_utc`; the audit reconciles every due obligation to one attempt or a valid prospective supersession and rejects unexplained holes.

Current repository evidence also covers:
- crash boundaries around discovery/queue/raw/envelope/state transitions;
- durable cooldown across restart;
- 429/403/error accounting;
- `NO_NEW_DATA` vs request failure vs never-ran vs stale collector;
- invalid/incomplete discovery never becoming `NO_NEW_DATA`;
- fingerprint mismatch and malformed evidence fail-closed;
- real Linux SIGTERM supervisor/child boundary;
- real Linux SIGKILL/PDEATHSIG boundary;
- systemd effective restart/timing/KillSignal configuration validation;
- raw-object parent-directory durability after hardlink publication;
- visibility/count-proxy regressions including `sec-audit` stdout.

Exact tested code candidate `88566cb4fb08bdf01561ffcbfe18fd391e57c572` passed GitHub Actions run `35478291920`: 380/380 full unit suite, 271/271 explicit SEC P0 lane and V1 E2E.

## 5. Coverage matrix

| Claim / failure class | Current evidence | Fixed 14d adds unique proof? | Classification |
|---|---|---|---|
| Scheduler cadence/backoff/cooldown logic across long time | FrozenTimebase + durable obligation ledger/audit | Little; arbitrary time can be advanced deterministically | COVERED |
| Missed due action vs no action due | Prospective named obligations + one-to-one reconciliation | Little | COVERED |
| Restart durability at application commit boundaries | Crash-boundary replay tests | Little | COVERED |
| SIGTERM/SIGKILL parent-child behavior | Real Linux process tests | Target systemd/cgroup still differs | PARTIAL |
| Parent-directory fsync/power-loss boundary | Targeted red/green test; fix on candidate | Target filesystem/power behavior still differs | PARTIAL |
| Discovery fail-closed | Invalid/truncated/error payload regressions | Little | COVERED |
| NO_NEW_DATA vs dead/failed collector | Explicit semantic/liveness tests | Live source silence still adds source/runtime evidence | PARTIAL |
| 429/403/cooldown ordering | deterministic tests | 14d does not guarantee these happen naturally | COVERED logically; LIVE SOURCE PARTIAL |
| Complete weekend semantics | Daily-index reconciliation has a real weekday/weekend branch and 30-hour settle rule; a dedicated Friday->weekend->Monday boundary regression was not found | Branch semantics can be accelerated; real host/source crossing a weekend still adds operational evidence | PARTIAL + REAL-TIME component |
| Source-normal silence | Logical distinction tested | A naturally occurring, prospectively declared live silence is not synthetically equivalent | REAL-TIME-ONLY component |
| Loaded systemd/drop-ins/cgroup behavior | Config parser/validation + process tests | Only actual target host proves loaded unit behavior | TARGET-HOST-ONLY |
| Mount absence/read-only code/persistent state binding | Deployment contract only | Calendar time does not prove setup correctness by itself | TARGET-HOST-ONLY |
| Actual filesystem support for flock/link/rename/dir-fsync | Code relies on it; repo tests on CI filesystem | Must verify target filesystem | TARGET-HOST-ONLY |
| Actual SEC identity/network path | Repo fail-closed + historical live probe | Must verify target private identity/network | TARGET-HOST-ONLY |
| Resource leakage / unbounded state growth | No complete long-run target proof identified | Long soak may expose it, but accelerated high-cycle test is stronger per unit time | PARTIAL |
| Unknown interactions in exact deployed runtime | impossible to prove exhaustively | Real soak retains residual discovery value | REAL-TIME-ONLY residual |

## 6. Finding

A fixed P14D soak is a weak way to force failure-space coverage. Fourteen quiet days can pass without a crash, reboot, disk error, 429, process kill, mount failure or important recovery boundary. Conversely, deterministic/fault-injected testing can exercise those boundaries thousands of times quickly.

However, eliminating real elapsed time entirely would also be wrong. Simulation cannot honestly prove the actual target host's loaded systemd behavior, mount lifecycle, filesystem implementation, requester identity/network path or a naturally occurring source-normal silence.

Therefore the stronger architecture is hybrid: compress what can be compressed and retain real time only where the environment itself is the object under test.

## 7. Proposed replacement qualification contract

### Gate A — Repository/fault-compression proof

On the exact candidate semantics:
- exercise every scheduler state/cause and every policy timing threshold;
- cover all backoff steps and maximum cooldown paths;
- advance virtual time across at least the former P14D horizon including virtual weekends/silence;
- inject crashes before/after durability-critical filesystem and state-commit boundaries;
- exercise request failures, malformed/truncated responses, 429/403 and restart replay;
- require zero unexplained obligations and no integrity/firewall violations;
- retain deterministic reproduction seeds/inputs for any randomized campaign.

This gate may be implemented in an external harness so the frozen acquisition candidate need not be changed merely to host the stress driver.

### Gate B — Target-host destructive entrance checks (pre-t0, synthetic/offline state)

On the actual target host and exact pinned release:
- verify immutable release + fixed `/opt/quant` view + persistent `/var/lib/quant-p0` mount;
- prove missing state mount fails closed rather than creating fresh hidden state;
- verify filesystem support for flock, hardlink, atomic rename and directory fsync;
- verify loaded systemd fragment/effective values/digest and absence of unbound drop-ins;
- run actual `systemctl stop` / `start`; verify lifecycle evidence;
- test supervisor/child kill behavior under the real systemd cgroup;
- perform a controlled host reboot before t0 and prove durable state/fingerprint/lifecycle handling;
- verify private SEC requester identity and one global requester budget;
- bind runtime image/interpreter/OpenSSL/configuration and active/materialized fingerprint.

### Gate C — Qualifying live event window

After Gate B, perform one final restricted entrance audit on the exact pinned runtime. If it passes and the superseding governance rule is already in force, Blue explicitly declares:

`t0 = <exact UTC timestamp>`

That declaration starts the qualifying live continuity window. Run the exact pinned target runtime prospectively from t0 with no invalidating intervention.

Closure is event-based, not `N` arbitrary days. Use the SEC's prospectively known EDGAR operating calendar as the source authority: EDGAR accepts filings 06:00–22:00 Eastern Time Monday–Friday except federal holidays, and daily indexes are updated nightly beginning around 22:00 ET. The live window must:
- include one ordinary weekday overnight source-closed interval (22:00–06:00 ET) declared before observing outcomes;
- then include one complete weekend source closure and remain accountable through at least the first required post-weekend acquisition cycle after EDGAR reopens;
- complete the applicable Friday/preceding-business-day daily-index reconciliation under the existing 30-hour settle rule;
- therefore exercise both source-normal silence and the collector's real weekday/weekend reconciliation boundary prospectively;
- account for every prospective scheduler obligation through the durable audit;
- show no unexplained heartbeat/attempt hole;
- preserve stable active/materialized fingerprint and target runtime/service bindings;
- expose only opaque operational verdicts outside the restricted P0 evidence boundary;
- include restricted before/after resource-stability checks for file descriptors, memory/state growth and storage pressure without leaking scientific/count proxies.

If the required source-calendar conditions have not occurred, the window stays open. A practical qualifying live window can normally be scheduled from before a weekday EDGAR close through the next Monday reopen, while still remaining event-based rather than hard-coding a shorter arbitrary duration. No fixed minimum of fourteen days is needed once Gates A/B provide the failure coverage that calendar waiting previously proxied.

### Gate D — Final retrospective audit

Produce one target artifact binding exact SHA/tree/input-tree digest/fingerprint/manifest/runtime image/effective service digest/CI run/UTC interval/lifecycle authority and the Gate A/B/C verdicts. Gate D decides whether the continuity proof that began at the declared t0 is complete; it does not retroactively choose t0.

## 8. Why this is stronger than fixed P14D

- It deliberately hits crash and recovery boundaries instead of waiting for accidents.
- It preserves the real weekend/silence evidence P14D was designed to obtain.
- It proves target systemd/mount/filesystem behavior directly.
- It turns long semantic histories into accelerated test coverage.
- It retains a real soak for unknown target-runtime interactions.
- It reduces calendar opportunity cost without lowering the capture/PIT/firewall bar.

## 9. Decision boundary

This memo does **not** yet change the frozen rule. Until a separate Blue governance amendment explicitly supersedes it:

`P0_CONTINUOUS_OBSERVATION_MIN = P14D` remains authoritative.

Next action: red-team this replacement contract against the current P0 implementation and target-runtime entrance conditions. If no unique P14D-only property is found, commit an explicit governance amendment before any t0 declaration.