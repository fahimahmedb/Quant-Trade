# BLUE — P0 Compressed Qualification Protocol — 2026-09-20

## Authority state

This protocol is a **candidate replacement procedure** for the fixed P14D continuity rule.
It does not supersede frozen governance by itself.

Until a separate explicit amendment is committed:

`P0_CONTINUOUS_OBSERVATION_MIN = P14D`

remains authoritative.

`t0 = NOT DECLARED`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

`REAL_CAPITAL_AUTHORIZED = FALSE`

Read first:
1. `QUANT_NORTH_STAR.md`
2. `governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md`
3. `handoff/ASTRA_P0_CHECKPOINT.md`
4. `governance/BLUE_P14D_CHALLENGE_2026-09-20.md`

## Objective

Provide evidence equal or stronger than a passive 14-calendar-day soak for the properties that matter:
- capture integrity;
- PIT reconstructability;
- anti-selection / visibility firewall;
- unattended accountability;
- target-runtime restart and persistence behavior.

Do this by deliberately exercising failure space, then retaining only the irreducible real-environment and source-calendar observations.

## Candidate lineage

Astra's repository-side code candidate:
`88566cb4fb08bdf01561ffcbfe18fd391e57c572`

Verified code-candidate CI:
`35478291920 = COMPLETED / SUCCESS`

Astra final repository checkpoint:
`643deacdf5bbbdb1d2410c762eb20f72aff16bbf`

Blue calendar-compression research branch:
`blue/p0-continuity-qualification-2026-09-20`

First Blue test commit:
`8350dd214943a547af23294b8801cff98037896d`

Those Blue tests are research/qualification evidence only. They do not silently redefine the acquisition candidate.

---

# Gate A — Accelerated repository evidence

## A1. Existing proof inventory

Require all Astra repository evidence to remain green:
- exact schema drift;
- status freshness;
- full unit suite;
- explicit P0 lane;
- V1 E2E;
- exact-head verification artifact;
- clean tree.

Known repository-side properties include:
- named prospective scheduler obligations;
- one-obligation-to-one-resolution audit;
- deterministic FrozenTimebase;
- restart/crash replay;
- durable cooldown;
- no hidden retry;
- malformed/truncated/error discovery fail-closed;
- NO_NEW_DATA distinct from failed / never-ran / stale;
- fingerprint fail-closed;
- SIGTERM/SIGKILL/PDEATHSIG process boundaries;
- raw-object directory durability;
- visibility/count-proxy firewall regressions.

## A2. Calendar compression

Require dedicated tests to prove:
- Friday becomes daily-index reconciliation-due only after the exact 30-hour settle rule;
- Saturday/Sunday never become daily-index reconciliation targets;
- Monday becomes due only after its own settle threshold;
- scanning across at least 14 virtual days yields exactly the settled weekdays and no hidden calendar state.

Current implementation attempt:
`tests/test_p0_continuity_compression.py` on Blue research branch.

## A3. Timing-boundary matrix

Exercise exact boundaries and one point on each side for:
- discovery poll interval: 60 s;
- connection idle recycle: 20 s;
- connect timeout: 10 s;
- read timeout: 20 s;
- total request deadline: 60 s;
- backoff ladder: 5 / 15 / 60 / 300 / 900 s;
- 429 cooldown: 300 s;
- 403 cooldown: 3600 s;
- daily-index settle: 30 h;
- supervisor restart delay: 15 s;
- restart burst window: 600 s;
- stop timeout: 30 s;
- deployment-authority maximum age: 3600 s.

No production semantic constant may be changed merely to make the test easier.

## A4. Fault matrix

Every durability-critical transition should have either:
- an existing discriminating red/green test;
- a deliberate falsification showing why no defect exists;
- or an explicit residual target-host test in Gate B.

Minimum matrix:
- before/after raw write;
- before/after file fsync;
- before/after hardlink;
- before/after directory fsync;
- before/after envelope append;
- before/after attempt completion;
- before/after cursor advancement;
- before/after scheduler successor obligation;
- before/after cooldown persistence;
- supervisor death;
- child death;
- corrupted/torn journal tail;
- duplicate replay;
- state newer than journal;
- journal newer than state;
- missing/foreign fingerprint;
- missing deployment authority.

## A5. Long-history stress without calendar waiting

A separate stress driver may generate large event histories under FrozenTimebase or synthetic ledgers.

It must test invariants, not just count cycles:
- no duplicate obligation resolution;
- no unexplained due obligation;
- monotonic evidence ordering;
- no silent coverage upgrade;
- stable fingerprint;
- bounded/recoverable persistent state;
- no visibility proxy.

If randomized, every failure must emit a deterministic seed and minimal replay input.

Gate A passes only when exact-head CI is green and the result is reproducible.

---

# Gate B — Target-host destructive entrance checks

Gate B uses the **actual target host** and exact pinned release, before any qualifying t0.
Destructive checks use synthetic/offline state where needed.

## B1. Immutable deployment

Verify:
- `/opt/quant-releases/<exact-sha>/` is complete, detached, immutable and self-contained;
- `/opt/quant` is the fixed service view of that exact release;
- `/var/lib/quant-p0/` is the durable writable state root;
- `/opt/quant/var` maps to that state root;
- code outside `var/` is read-only to the service;
- backing release cannot be mutated through a development path;
- Product/Forward/Economic runtimes live elsewhere.

Negative test:
- remove/prevent the state mount in a controlled pre-t0 exercise;
- service must fail closed and must not create a fresh shadow state tree underneath the absent mount.

## B2. Filesystem semantics

On the exact filesystem used by P0, demonstrate:
- advisory lock / flock semantics required by the requester budget;
- hard links;
- same-filesystem staging/publication;
- atomic rename where relied upon;
- directory fsync;
- durable file fsync;
- crash/restart visibility of already-acknowledged synthetic records.

Record filesystem type, mount options and relevant storage identity.

## B3. Effective systemd

Record:
- `systemctl cat quant-sec-capture.service`;
- `systemctl show quant-sec-capture.service --no-pager`;
- FragmentPath;
- DropInPaths;
- ExecStart;
- WorkingDirectory;
- Restart;
- RestartUSec;
- StartLimitIntervalUSec;
- StartLimitBurst;
- KillMode;
- KillSignal;
- TimeoutStopUSec.

Require repository declaration == loaded/effective contract.
Unbound drop-ins fail the gate.

## B4. Actual lifecycle tests

Using synthetic/offline state:
1. normal start;
2. `systemctl stop`;
3. `systemctl start`;
4. child failure observed by the same supervisor;
5. supervisor SIGKILL;
6. controlled host reboot.

For each event verify:
- child process fate;
- externally attributable lifecycle cause;
- expected invalidation/non-invalidation classification;
- durable journals survive;
- no unexplained scheduler obligation;
- no fresh bankroll/state reset;
- active/materialized fingerprint behavior is correct.

Do not infer these properties from container-only tests.

## B5. Runtime binding

Bind and record:
- exact Git SHA and tree;
- verified input-tree digest;
- Python version/build;
- OpenSSL version;
- runtime image/package identity;
- effective SEC configuration;
- private requester identity availability without publishing it;
- one global SEC requester-budget authority;
- loaded service digest;
- host boot identity where relevant.

## B6. Fingerprint materialization

In the exact service environment:
- materialize schema v2;
- require semantic schema v1;
- prove `ACTIVE_RUNTIME_FINGERPRINT == MATERIALIZED_FINGERPRINT`;
- prove stale/foreign/missing freeze fails closed;
- confirm no durable integrity latch.

Gate B produces a restricted entrance artifact.

---

# Gate C — Prospective live event window

This is the irreducible live portion. It tests the real host + real SEC source, not a synthetic substitute.

## C1. Start condition

Start only after Gates A and B are green, the exact candidate is frozen, and the final restricted entrance audit passes.

Before observing qualifying outcomes:
1. predeclare the UTC/ET source-calendar intervals;
2. ensure the superseding governance contract is already authoritative;
3. Blue explicitly declares `t0 = <exact UTC timestamp>`.

The qualifying live window begins at that t0. t0 is never chosen retrospectively after seeing the window.

Use current SEC source authority:
- filing acceptance generally 06:00–22:00 ET Monday–Friday except federal holidays;
- daily indexes update nightly beginning around 22:00 ET.

Re-check SEC documentation immediately before starting because source operating rules may change.

## C2. Required source/calendar events

The live window must include all of:
1. an ordinary weekday EDGAR closed interval spanning 22:00→06:00 ET;
2. the next live reopening and expected acquisition cycle;
3. one complete weekend closure;
4. the first required acquisition cycle after Monday reopening;
5. applicable daily-index reconciliation after the existing 30-hour settle threshold.

A holiday is not substituted unless it was declared as the intended source-normal silence before observing the result.

## C3. Continuous accountability

For the whole live window:
- every prospective scheduler obligation is accounted for;
- no unexplained heartbeat/attempt hole;
- no invalidating intervention;
- fingerprint remains stable;
- active/materialized manifests remain equal;
- loaded runtime/service binding remains stable;
- source-normal silence remains distinguishable from service death;
- malformed/failed source interactions never become NO_NEW_DATA;
- no protocol-visible count/content/timing proxy escapes the firewall.

## C4. Resource stability

Restricted evidence only; do not expose scientific/count proxies.

Compare before/after:
- process restart count and reason;
- file descriptor/resource health;
- disk free space and state-volume health;
- journal readability;
- integrity latch;
- state-file growth sanity;
- mount identity;
- runtime/service digest.

This is for operational leak detection, not scientific inference.

Gate C is event-based. It does not close merely because a shorter number of hours elapsed.

---

# Gate D — Final retrospective proof

Produce one restricted exact-runtime artifact binding:
- candidate SHA;
- Git tree;
- verified input-tree digest;
- acquisition fingerprint;
- materialized manifest/schema;
- runtime image/interpreter/OpenSSL;
- effective configuration;
- repository + loaded service digests;
- exact CI run(s);
- Gate A evidence;
- Gate B evidence;
- live Gate C interval;
- lifecycle/deployment authority references;
- before/after resource verdicts.

Run the existing retrospective obligation audit over the prospective live interval beginning at the already-declared t0.

Public output must remain opaque:
- PASS / FAIL / BLOCKED;
- binding metadata safe for publication;
- no accession/content/count/timing-distribution proxy.

Only then may Blue decide whether continuity qualification is satisfied under an amended governance rule.

---

# Failure / reset rules

The candidate live window fails or resets on:
- acquisition-critical fingerprint change;
- unauthorized MANUAL_START after stop/failure;
- manual mutation of durable acquisition state;
- bypass of cadence/limiter/backoff/cooldown/coverage validation;
- unexplained due obligation;
- lost/unbound state mount;
- stale/foreign materialization accepted;
- unbound systemd override;
- integrity fault;
- source failure silently classified as NO_NEW_DATA.

Read-only audit and unrelated Product development remain allowed when they cannot mutate the qualifying runtime.

---

# Current recommendation

Do **not** start a passive 14-day wait yet.

First:
1. complete Gate A calendar-compression proof;
2. red-team the full Gate A timing/fault matrix;
3. commit an explicit governance amendment only if no unique P14D-only property remains;
4. instantiate Gate B on the target host;
5. run Gate C prospectively across the required SEC calendar events.

This preserves the real temporal evidence while removing calendar waiting as a substitute for deliberate failure testing.
