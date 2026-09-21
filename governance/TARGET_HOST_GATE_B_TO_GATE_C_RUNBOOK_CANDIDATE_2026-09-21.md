# TARGET-HOST GATE B -> GATE C RUNBOOK — CANDIDATE — 2026-09-21

Parent candidate:
`governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_CANDIDATE_2026-09-21.md`

## Status

`RUNBOOK_STATUS = PREPARED_CANDIDATE / DO_NOT_EXECUTE_AS_QUALIFYING_AUTHORITY`

`GATE_B = NOT_STARTED`

`t0 = NOT_DECLARED`

This file is an operator sequence candidate only.
It does not authorize target-host mutation until Blue promotes the hybrid method
and activates this runbook or a reconciled successor.

## Phase 0 — exact immutable variables

After activation, the operator must use the exact candidate:

```bash
export EXPECTED_SHA=4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
export EXPECTED_TREE=4d15ef6f471213ee6ab56337b555d2906ef9bf16
export EXPECTED_INPUT_TREE_DIGEST=sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2
export QUANT_RELEASE=/opt/quant-releases/$EXPECTED_SHA
export QUANT_ROOT=/opt/quant
export QUANT_STATE=/var/lib/quant-p0
export UNIT=quant-sec-capture.service
```

The restricted evidence root must be outside the immutable release.

Do not create it or execute destructive phases until this runbook is activated.

## Phase 1 — read-only immutable release preflight

When authorized, preserve:

```bash
cd "$QUANT_RELEASE"
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
git status --porcelain=v1
```

Require:
- HEAD == `EXPECTED_SHA`;
- tree == `EXPECTED_TREE`;
- clean tree.

Inspect mount topology for:
- `$QUANT_RELEASE`;
- `$QUANT_ROOT`;
- `$QUANT_ROOT/var`;
- `$QUANT_STATE`.

No mutation in this phase.

## Phase 2 — read-only runtime/systemd preflight

Record:
- uname/os-release;
- boot id;
- Python real path/version;
- OpenSSL;
- relevant environment identity;
- `systemctl show` properties required by the Gate-B contract;
- `systemctl cat` output;
- repository and loaded unit digests.

This phase is evidence collection only.

## Phase 3 — state authority inventory

Before destructive testing:
- snapshot state-root file inventory and metadata;
- hash acquisition-critical authority/provenance files;
- verify lock holders;
- identify any prior state lineage;
- preserve unexplained rows rather than deleting them.

If the state cannot be explained, STOP before qualification.

## Phase 4 — synthetic filesystem campaign

Use a dedicated synthetic/offline test area on the same relevant filesystem.

Exercise:
- flock;
- hardlink;
- rename;
- file fsync;
- directory fsync;
- writer-lock conflict;
- acknowledged synthetic-state durability.

Do not use preserved acquisition evidence as disposable test material.

## Phase 5 — materialization/readiness preflight

Using the exact frozen supported primitives:
- evaluate readiness;
- materialize fingerprint only through the authorized restricted procedure;
- verify active/materialized equality;
- preserve opaque digests only.

No qualifying t0 authority is created here.

## Phase 6 — destructive lifecycle Gate B

Execute only after Blue/operator explicitly enters destructive Gate B.

Required sequence:
- controlled authorized start on synthetic/offline state;
- stop;
- fresh authorized start;
- abnormal child exit / child SIGKILL;
- supervisor SIGKILL;
- restart-delay/burst observation;
- replacement-supervisor forgery attempt must fail;
- controlled reboot;
- missing-state-mount startup test;
- writer-lock contention.

Each subtest gets a separate restricted artifact/reference.

Any REAL_DEFECT:
preserve evidence and STOP.

## Phase 7 — sanitize for future Gate C

After destructive Gate B:

- service stopped;
- synthetic state separated from qualifying state;
- exact qualifying state reservoir selected;
- final state inventory recorded;
- stale one-use authorities absent;
- no ambiguous lifecycle provenance;
- no integrity latch;
- SHA/tree/input-tree rechecked;
- systemd/runtime/mount identity rechecked;
- active/materialized fingerprint rechecked.

Then seal:

`TARGET_HOST_GATE_B_ENTRANCE_<UTC>.json`

## Phase 8 — Blue Gate B reception

Do not continue autonomously from a local green result.

Blue reviews the restricted Gate-B artifact and records either:

`GATE_B = PASS`

or:

`GATE_B = BLOCKED`

Even on PASS:

`t0 = NOT_DECLARED`.

## Phase 9 — prepare one-use t0 precommit

Only after Blue Gate-B PASS:

Use the authoritative version of:

`governance/P0_T0_PRECOMMIT_TEMPLATE_CANDIDATE_2026-09-21.md`

Precommit:
- exact SHA/tree/input-tree;
- exact fingerprint;
- effective service digest;
- qualifying state identity;
- Gate-B artifact digest;
- fresh one-use launch authority;
- prospective Gate-C source-calendar event plan.

Seal the precommit BEFORE the qualifying launch.

## Phase 10 — exactly one qualifying launch

The operator performs one systemd launch consuming the precommitted authority.

The externally attributable UTC timestamp of that unique launch event becomes:

`t0`

only if all precommitted bindings match.

If no matching launch, multiple launches, wrong fingerprint/service/state, or
ambiguous provenance:

`NO_T0`

Do not select another timestamp from the same observed interval.

## Phase 11 — Gate C immediately begins

From t0 onward:
- no unauthorized restart;
- no acquisition-critical state mutation;
- no service/runtime/fingerprint/state-mount substitution;
- every scheduler obligation attributable;
- source-normal silence distinguishable from failure/service death.

Gate C remains open until every event required by the authoritative hybrid
amendment occurs.

## Phase 12 — Gate C invalidation

On any invalidator:
1. preserve the interval;
2. mark it FAIL/INVALIDATED;
3. classify;
4. return to Blue;
5. do not move t0 forward inside the same interval.

A new attempt requires a fresh precommit and qualifying launch.

## Phase 13 — Gate D closure

After all Gate-C events:

bind:
- Gate A evidence;
- Gate B artifact;
- t0 precommit + launch event;
- full Gate-C interval;
- lifecycle/authority evidence;
- final obligation audit;
- resource-health before/after;
- exact runtime/service/fingerprint lineage.

Only a separate Blue disposition may then declare P0 continuity qualified.

## Current prohibition

This runbook currently has no execution authority.

Do not touch:
- `/opt/quant`;
- `/var/lib/quant-p0`;
- systemd;
- mounts;
- reboot;

on the basis of this candidate file alone.
