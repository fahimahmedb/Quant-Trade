# BLUE — GATE B TO t0 ENTRANCE BINDING SPEC — CANDIDATE — 2026-09-21

## Status

**PREPARED CANDIDATE — DO NOT EXECUTE AS A QUALIFYING START YET**

`t0 = NOT DECLARED`

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

`TARGET_HOST_READY = FALSE`

This supplement prepares the exact transition from target-host Gate B to a prospective qualifying t0 under the proposed `HYBRID_EVENT_BASED_V1` method.

It does not supersede:
- `governance/TARGET_HOST_RODAGE_ENTRANCE_CONTRACT_2026-09-20.md`;
- `governance/TARGET_HOST_P0_RODAGE_RUNBOOK_2026-09-20.md`;
- current fixed-P14D authority.

## 1. Preconditions before any qualifying use

Do not enter this sequence until all are true:

1. exact replacement candidate is frozen;
2. exact-head repository CI is green;
3. independent Astra/Red Team review has a durable final handoff;
4. Blue has issued a final candidate disposition permitting target-host entrance;
5. the P14D superseding amendment is authoritative if the hybrid method is to be used;
6. target-host operator has the exact candidate/release identity;
7. no previous failed-candidate authority/state is being silently reused.

Failure of any precondition => `NO_T0`.

## 2. Keep Builder/admin and qualifying runtime separated

The repository/admin clone is not the qualifying runtime.

Qualifying evidence must bind the immutable release/service view and persistent P0 state root defined by current deployment governance.

No development checkout mutation may be presented as qualifying runtime evidence.

No Product/Forward/Economic runtime is allowed to share acquisition-critical writable state with P0.

## 3. Gate B destructive/offline phase

Before t0, execute the target-host checks using synthetic/offline state where destructive behavior is required.

Required categories:

### B1 — release/state isolation
- exact immutable release;
- exact service view;
- persistent state mount;
- code read-only outside allowed state;
- controlled missing-mount test fails closed and does not create shadow state.

### B2 — filesystem semantics
- flock/advisory-lock behavior;
- hardlink support;
- same-filesystem publication assumptions;
- atomic rename where relied on;
- file fsync;
- directory fsync;
- acknowledged synthetic records survive controlled restart/reboot.

### B3 — loaded service authority
Bind:
- FragmentPath;
- DropInPaths;
- ExecStart semantic definition;
- WorkingDirectory;
- Restart;
- RestartUSec;
- StartLimitIntervalUSec;
- StartLimitBurst;
- KillMode;
- KillSignal;
- TimeoutStopUSec.

Unbound drop-in or semantic mismatch => Gate B FAIL.

### B4 — lifecycle
Using synthetic/offline state:
- normal start;
- stop;
- start;
- child failure;
- supervisor SIGKILL;
- controlled host reboot.

Every lifecycle event must have externally attributable provenance and expected durable-state consequences.

### B5 — runtime identity
Bind:
- Git SHA/tree/input-tree digest;
- interpreter/build;
- OpenSSL;
- runtime/package identity;
- effective SEC configuration;
- private requester identity availability without publication;
- one global requester-budget authority;
- host/storage identities needed by the contract.

### B6 — materialization
Require:
- active fingerprint == materialized fingerprint;
- stale/foreign/missing materialization fails closed;
- no integrity latch;
- no unexplained acquisition-critical pre-seeding.

Gate B produces one restricted artifact:

`GATE_B_ENTRANCE_ARTIFACT`

with a hash-addressable digest.

Gate B PASS still does not create t0.

## 4. Post-Gate-B sanitization before qualifying launch

After destructive Gate B work:

1. qualifying service must be stopped;
2. synthetic/offline destructive-test state must be separated from or removed from the future qualifying state according to the deployment contract;
3. exact persistent-state identity for qualification must be fixed;
4. exact release/service/fingerprint must be reverified;
5. no stale one-use deployment authority may remain;
6. no ambiguous lifecycle record may remain;
7. no integrity latch may remain;
8. final entrance artifact must bind the state that will actually enter Gate C.

Any uncertainty => `NO_T0`.

## 5. Precommit the unique t0 event

Recommended mode:

`T0_BINDING_MODE = PRECOMMITTED_NEXT_AUTHORIZED_QUALIFYING_LAUNCH`

Before starting the service, Blue/operator must durably bind:

- exact candidate SHA/tree/input-tree digest;
- exact materialized/active acquisition fingerprint;
- exact effective service digest;
- exact persistent-state identity;
- exact Gate B entrance artifact digest;
- one fresh one-use qualifying launch/deployment authority identifier;
- the statement that the next single qualifying launch consuming this authority is the unique t0 event;
- the prospectively selected source-calendar event window that Gate C must cross.

This precommit must be sealed before any qualifying source outcome exists.

## 6. Launch and t0 materialization

Perform exactly one qualifying launch under the precommitted authority.

The exact UTC `t0` is:

the externally attributable timestamp of the unique qualifying launch event that consumes the precommitted authority.

Immediately bind:
- t0 UTC;
- lifecycle event identity;
- consumed authority identity;
- service PID/unit identity as safe restricted evidence;
- boot identity;
- active/materialized fingerprint;
- state-mount identity.

If:
- launch does not occur;
- authority is not consumed;
- multiple qualifying launches occur;
- launch provenance is ambiguous;
- wrong candidate/service/fingerprint/state is observed;

then:
`NO_T0`.

Do not choose another timestamp from the same already-observed interval.

## 7. Gate C starts immediately at t0

From t0 onward:
- no unauthorized/manual qualifying restart;
- no acquisition-critical state mutation;
- no service/fingerprint/state-mount substitution;
- every prospective scheduler obligation must remain attributable;
- source-normal silence must remain distinguishable from service death/failure.

Gate C stays open until the full real event set required by the authoritative hybrid amendment has occurred.

## 8. Failure handling after t0

A qualifying-window invalidator does not permit selecting a later good sub-window.

Instead:
1. mark the current Gate C interval FAIL/INVALIDATED;
2. preserve evidence;
3. classify cause;
4. Blue decides whether a fresh Gate B/entrance recheck is required;
5. only a new prospectively precommitted qualifying launch may establish a new t0.

This prevents retrospective cherry-picking.

## 9. Relationship to existing target-host contracts

This supplement strengthens entrance semantics only.

Until the hybrid amendment is explicitly promoted:
- fixed P14D remains authoritative;
- this file cannot be used to shorten the qualifying minimum;
- existing target-host contract/runbook remain the operational authority.

After promotion, Blue must reconcile this supplement into the authoritative target-host runbook before the first hybrid t0.

## 10. Safety state

`t0 = NOT DECLARED`

`GATE_B = NOT_EXECUTED_FOR_CURRENT_REPLACEMENT_CANDIDATE`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

`REAL_CAPITAL_AUTHORIZED = FALSE`

`PRODUCT_INTEGRATION = PAUSED`
