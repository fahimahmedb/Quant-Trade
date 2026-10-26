# BLUE TARGET-HOST QUALIFICATION MISSION — 2026-09-20

Authority: Blue / Mission Control.

Status:
`READY_TO_DISPATCH / NOT_EXECUTED`

This is the durable mission handoff for the next operator/conversation. It assumes Gate A v3 repository proof is already closed and must not be re-litigated unless new evidence contradicts the frozen candidate or final audit.

## 1. Mission objective

Qualify the real target host for final pre-t0 rodage using the exact frozen Gate A v3 candidate and the approved deployment contract.

The mission is NOT:
- to rebuild Gate A;
- to modify the frozen candidate;
- to declare t0 automatically;
- to start Gate B;
- to resume Product integration;
- to authorize real capital.

The mission succeeds only by producing target-host evidence sufficient for a later explicit Blue decision.

## 2. Mandatory authorities

Read first, in this order:

1. `QUANT_NORTH_STAR.md`
2. `handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`
3. `handoff/BLUE_GATE_A_V3_FINAL_DISPOSITION_2026-09-20.md`
4. `governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md`
5. `governance/TARGET_HOST_RODAGE_ENTRANCE_CONTRACT_2026-09-20.md`
6. `governance/TARGET_HOST_P0_RODAGE_RUNBOOK_2026-09-20.md`

Repository truth wins over this handoff if later durable evidence exists.

## 3. Exact immutable inputs

Frozen candidate:
`blue/p0-gate-a-v3-frozen-2026-09-20@2da079d8ad75c69eb3fc2990c512735cb4bdc02b`

Builder CI:
`35514180655 = COMPLETED / SUCCESS`

Final independent Astra audit:
`astra/p0-gate-a-v3-independent-audit-2026-09-20@33995d03c8632e5c3a7b77a12b87366fb06b4d30`

Astra CI:
`35517935710 = COMPLETED / SUCCESS`

Blue disposition:
`GATE_A_V3_REPOSITORY_DISPOSITION = PASS`

Do not silently substitute another SHA.

## 4. Current safety state

`t0 = NOT DECLARED`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

`TARGET_HOST_READY = FALSE / NOT_YET_QUALIFIED`

`GATE_B = NOT_STARTED`

`REAL_CAPITAL_AUTHORIZED = FALSE`

`PRODUCT_INTEGRATION = PAUSED`

## 5. Required execution order

### Stage A — read-only target preflight

Collect and bind:
- target host identity;
- deployed SHA/tree;
- release cleanliness;
- mount topology;
- ownership/permissions;
- runtime image identity;
- loaded systemd unit and effective values;
- durable-state-root inventory;
- writer/lock state.

Do not mutate P0 state yet.

Disposition:
- if exact frozen candidate or host topology cannot be established: `BLOCKED / NO_T0`;
- otherwise continue.

### Stage B — anti-pre-seeding review

This is mandatory because Gate A left a target-host-only concern around service-managed/invocation identity versus acquisition fingerprint equality.

Independently determine whether the durable state root has been altered by an unauthorized process before the legitimate qualifying service start.

Inspect and cross-bind:
- supervisor events;
- lifecycle provenance;
- deployment-authority ledger;
- scheduler/attempt state;
- collector state commit ledger;
- SEC traffic-budget commit ledger;
- lock ownership;
- file inventory digest.

Do not delete unexplained history.

If unauthorized pre-seeding is demonstrated and the later audit can still reach `accountable=True`:
`REAL_DEFECT`
`REOPEN_GATE_A = TRUE`
`STOP`

### Stage C — filesystem/single-writer capability

Prove on the real target filesystem:
- `flock`;
- hard links;
- atomic rename;
- directory fsync;
- staging/raw same filesystem;
- single writer;
- single global SEC requester budget;
- missing requester identity fails closed.

Unknown = BLOCKED.

### Stage D — materialization and deployment authority

Using the approved restricted operator environment:
- materialize the acquisition fingerprint/manifest with the frozen supported primitive;
- verify active/materialized identity;
- issue exactly one one-use deployment authority with the frozen supervisor primitive;
- preserve only opaque proof metadata.

Do not expose requester identity.

### Stage E — qualifying systemd start

Start through systemd only.

Verify:
- genuine `INVOCATION_ID`;
- recognised service manager;
- exact loaded unit;
- exactly one matching `CHILD_LAUNCH_AUTHORIZED`;
- authority consumed once;
- lifecycle start cross-binds supervisor/invocation/boot/fingerprint/authority;
- no manual/operator contamination.

Any ambiguity = NO_T0.

### Stage F — target-host fault proof

Before final rodage, establish the required real-host semantics:
- systemctl stop/start;
- abnormal child failure/SIGKILL;
- same-supervisor automatic restart witness;
- replacement supervisor cannot forge automatic restart;
- restart delay/burst;
- reboot persistence;
- missing-mount fail-closed;
- writer-lock contention fail-closed.

Use synthetic/offline state where destructive tests would contaminate the preserved reservoir.

### Stage G — final entrance decision

Produce only one:

`TARGET_HOST_ENTRANCE = PASS`
`READY_FOR_FINAL_RODAGE = TRUE`

or

`TARGET_HOST_ENTRANCE = BLOCKED`
`READY_FOR_FINAL_RODAGE = FALSE`

Unknown mandatory evidence counts as BLOCKED.

Even on PASS:
`t0 = NOT DECLARED`

## 6. Required durable outputs

The operator/conversation must produce:

1. a restricted hash-addressable target-host entrance evidence artifact outside the immutable release;
2. a Blue-readable opaque summary with PASS/FAIL/UNKNOWN per entrance check;
3. references to fault-test artifacts;
4. exact pre/post bindings for SHA/tree/fingerprint/runtime/systemd/mount/state inventory;
5. a durable handoff in the repository describing:
   - what was actually executed;
   - what remains unexecuted;
   - any blocker;
   - any REAL_DEFECT;
   - whether `READY_FOR_FINAL_RODAGE` is true.

Do not commit secrets, requester identity, raw SEC payloads or interpretable acquisition contents.

Suggested durable handoff path after execution:
`handoff/BLUE_TARGET_HOST_ENTRANCE_RESULT_<DATE>.md`

## 7. Stop conditions

STOP immediately and return ownership to Blue if:
- exact candidate identity differs;
- release tree is dirty;
- mounted topology differs from the contract;
- state mount can be absent without startup failure;
- unbound systemd drop-ins exist;
- loaded unit differs from repository unit;
- runtime identity cannot be bound;
- unexplained pre-seeding exists;
- second writer/requester authority exists;
- deployment authority is replayed/ambiguous;
- manual start contaminates qualifying history;
- fingerprint/materialization is stale/foreign;
- integrity latch or raw-reference mismatch exists;
- target-host failure semantics contradict the audited model;
- retrospective audit reaches a false accountable PASS;
- any new REAL_DEFECT is reproduced.

Do not patch the frozen candidate during this mission.

A code defect follows:
finding → Blue decision → specification → Builder → independent review → Blue decision.

## 8. Parallel work allowed

While target-host execution is pending, Blue may continue:
- post-Gate branch cleanup;
- default-branch migration preparation;
- authority simplification.

Do not resume Forward/Economic Product integration unless Blue explicitly opens that mission.

## 9. Mission ownership

Current owner:
`BLUE / MISSION CONTROL`

Execution may be delegated to an operator/agent with real target-host access.

Repository-only agents must not claim target-host proof they did not execute.

## 10. Current launch state

`TARGET_HOST_MISSION = READY_TO_DISPATCH`

`TARGET_HOST_ENTRANCE = PREPARED_ONLY`

`READY_FOR_FINAL_RODAGE = FALSE`

`t0 = NOT DECLARED`
