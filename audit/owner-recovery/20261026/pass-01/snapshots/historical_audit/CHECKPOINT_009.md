# Forensic Audit Continuation — Checkpoint 009

Date: 2026-10-19
Audit branch: `audit/forensic-checkpoint-20261019`
Parent audit head: `4aa7a0aefc6e4529da98926478a59d49116fa8f9`
Status: `ORACLE_RAIL_AUDIT_COMPLETE_FOR_RECOVERY_ENTRY`

## Scope

Audit the two existing Oracle-related rails against CP8 before any operational recovery implementation:

1. `builder/research-os-vm-autonomy-20261019` @ `8a1bdadc9bc52c4889ee19d0472bcee61fe24318`
2. `ops/oci-one-shot-install-20261019` @ `6e8ea155b05086f8e5eabcf830a5f835d3e3d09c`

No merge is performed by this checkpoint.

## 1. Branch ancestry and divergence

### VM autonomy rail

Comparison:

`d0dc70f5dd71f3e6cb8097d2f15807bb99ebc8ec -> 8a1bdadc9bc52c4889ee19d0472bcee61fe24318`

Result:

- status: ahead
- ahead by: `1`
- behind by: `0`
- changed file only:
  `research/research_os/runtime/VM_AUTONOMY_CHECKPOINT_20261019.md`

Therefore the VM rail is a documentary checkpoint directly on top of the modern autonomous Research OS head, not an implementation branch with a runner/service.

### OCI one-shot rail

Comparison:

`6e8ea155b05086f8e5eabcf830a5f835d3e3d09c -> d0dc70f5dd71f3e6cb8097d2f15807bb99ebc8ec`

Result:

- status: diverged
- modern Research OS ahead by: `55`
- OCI rail has `3` commits not in modern head
- merge base:
  `e980d201d3c84d16d7d91fde0d27a06c9a2c3121`

The OCI installer itself pins exactly that old merge-base SHA:

`HEAD = e980d201d3c84d16d7d91fde0d27a06c9a2c3121`

Therefore:

`WHOLESALE_OCI_MERGE_SAFE = FALSE`

Selective porting is required.

### Current economic rail relative to modern autonomous head

Comparison:

`d0dc70f5dd71f3e6cb8097d2f15807bb99ebc8ec -> ac3b32ffa8ff4d768525c6da2a7ae3f9e2cdddc7`

Result:

- ahead by: `5`
- behind by: `0`

Those five commits contain the current UST economic screen/validation/receipt state.

Thus any Oracle recovery should be based on the newer economic state, not on the old OCI merge base and not merely on the documentary VM checkpoint.

## 2. VM autonomy rail — positive properties

Commit `8a1bdadc...` correctly declares:

- Oracle VM is an execution host, not a new research architecture;
- fresh GitHub state on every wake;
- existing queue/lease/receipt/event semantics must be reused;
- one lineage per wake;
- producer/challenge separation;
- optimistic locking;
- bounded lease;
- deterministic empty-queue refill only through existing policy;
- no free-form research invention;
- Legacy screening before freeze;
- dry-run/canary before continuous scheduling;
- all four hard economic/live authority flags remain false.

Classification:

`VM_INTENT_ARCHITECTURALLY_ALIGNED = PASS`

## 3. VM autonomy rail — missing implementation

The commit changes only the checkpoint markdown file.

It explicitly states:

- `VM_SERVICE_IMPLEMENTED = FALSE`
- `VM_SERVICE_ENABLED = FALSE`

Therefore it does not yet prove:

- executable wake runner;
- startup preflight;
- concrete Legacy materialization;
- exact Legacy blob verification;
- current-frozen corpus loading;
- schema normalization;
- Portfolio peer-set binding;
- duplicate/overlap readiness gating;
- durable worker service/timer;
- restart recovery behavior of an actual worker;
- no-mutation canary execution.

Classification:

`VM_EXECUTION_LAYER = MISSING`

`VM_CP8_SCIENTIFIC_PREFLIGHT = MISSING`

## 4. OCI one-shot rail — positive deployment properties

`deploy/oci_one_shot.py` contains several reusable properties:

### Installation identity / immutability

- installs into a SHA-addressed release directory;
- retains old installations;
- refuses an unknown pre-existing release without a matching receipt;
- publishes only after verification.

### Installation concurrency

- obtains an exclusive `fcntl` install lock;
- restart state is persisted locally;
- repair mode refuses to create a new command if prior state is absent.

### Verification discipline

- runs selected pre-outcome readiness unit/integration tests before publishing the release;
- runs a synthetic readiness composition;
- verifies authority equals the closed `AUTHORITY` constant;
- verifies no outcome was accessed and result remains `NOT_OBSERVED`.

### OCI/IAM fail-closed behavior

- nonzero CLI return => explicit failure;
- unexpected empty GET => failure;
- malformed JSON => failure;
- missing expected `data` => failure;
- IAM dynamic group is bound to one VM id;
- policy is constrained to that instance consuming its own Run Commands;
- incompatible pre-existing IAM objects are not silently replaced.

### No scheduler activation

The generated receipt explicitly records:

`scheduler_started = false`

and the module docstring states:

`No scheduler starts.`

Classification:

- `OCI_INSTALL_RESTARTABILITY = PASS_FOR_INSTALLATION_SCOPE`
- `OCI_RESPONSE_ERROR_HANDLING = PASS`
- `OCI_IAM_SCOPE = NARROW_BY_DESIGN`
- `OCI_UNAUTHORIZED_SCHEDULER_START = ABSENT`

These are selective-port candidates.

## 5. OCI one-shot rail — stale source pin

The installer hardcodes:

`HEAD = e980d201d3c84d16d7d91fde0d27a06c9a2c3121`

and the embedded remote installer repeats the same SHA.

This SHA is the divergence merge base and is 55 modern commits behind `d0dc70...`, before the additional five current economic commits to `ac3b32...`.

Classification:

`OCI_DEPLOYED_RESEARCH_OS_HEAD = STALE`

Reusing the installer unchanged would deploy old scientific/runtime state.

## 6. OCI one-shot Legacy preflight classification

The embedded remote verification imports:

`fixture, legacy`

from:

`research.research_os.tests.test_economic_readiness_integration`

and executes:

`economic_test_readiness(fixture(), legacy=legacy())`

The test helper `legacy()` constructs a populated **synthetic fixture corpus**. It does not materialize and verify the pinned real historical ledger declared in:

`research/research_os/legacy/source_manifest.json`

The OCI installer therefore does not prove:

- source commit `183ad65ff260b903a16548ce37948f54d47a9ec8` fetched;
- blob `ba9b165aaf96956776672df51233bb9bf1e6cbc9` materialized;
- real record count loaded;
- PR #1 gaps acknowledged at worker startup.

Classification against CP8:

- `A1 missing real ledger fail-closed`: MISSING
- `A2 exact real ledger blob verification`: MISSING
- `A4 real record-count sanity`: MISSING
- `A5 partial-memory status`: NOT BOUND INTO INSTALL RECEIPT

Synthetic readiness is a useful code smoke test, not historical-memory preflight.

## 7. OCI current-frozen / anti-redetection classification

The reviewed installer does not:

- enumerate `research/research_os/hypotheses/`;
- normalize heterogeneous hypothesis schemas;
- create/bind a current frozen-corpus hash;
- supply a complete peer set to Portfolio/readiness;
- block ASML-style current-lineage duplication;
- bind same-exposure resolution into a receipt.

Classification:

- `B1 current-corpus binding`: MISSING
- `B2 schema normalization`: MISSING
- `B3 ASML regression`: MISSING
- `D1 peer-set completeness binding`: MISSING
- `D2 overlap blocks readiness`: inherited defect / MISSING

## 8. OCI worker restart-safety classification

The installer itself is restart-conscious, but it is not a worker scheduler.

It proves installation-command reuse and release immutability. It does not prove runtime worker semantics such as:

- lease reclaim after interruption;
- no duplicate candidate freeze;
- no duplicate experiment plan;
- exactly one receipt per wake;
- current task optimistic-lock race handling from Oracle service;
- stage-by-stage fresh authority/state recheck.

Classification:

`F2_ORACLE_INSTALL_RESTART_SAFETY = PASS_PARTIAL`

`F2_ORACLE_WORKER_RESTART_SAFETY = NOT_IMPLEMENTED`

## 9. CP8 matrix classification by rail

| Acceptance area | VM autonomy `8a1bd...` | OCI one-shot `6e8ea...` |
|---|---|---|
| Fresh GitHub state intent | PASS intent | STALE fixed SHA |
| Preserve canonical architecture | PASS intent | PARTIAL, old qualified snapshot |
| Hard authority closure | PASS intent | PASS in synthetic verification |
| Legacy screen required | PASS intent | synthetic only |
| Real pinned Legacy materialization | MISSING | MISSING |
| Exact Legacy blob verification | MISSING | MISSING |
| Real Legacy count sanity | MISSING | MISSING |
| Current frozen-corpus binding | MISSING | MISSING |
| Heterogeneous schema normalization | MISSING | MISSING |
| ASML duplicate regression | MISSING | MISSING |
| Complete peer-set binding | MISSING | MISSING |
| Overlap blocks readiness | inherited FAIL | inherited/stale FAIL |
| Producer/validator separation | inherited PASS | old test snapshot only |
| Install idempotency/restart | N/A | PASS |
| Worker lease/restart implementation | MISSING | MISSING |
| Narrow OCI IAM | not implemented | PASS design |
| Scheduler/service implemented | FALSE | FALSE |
| Scheduler/service enabled | FALSE | FALSE |
| Live/economic authority opened | FALSE | FALSE |

## 10. Recovery design decision

The recovery branch already created earlier is the correct integration surface:

`builder/oracle-economic-loop-recovery-20261019`

baseline CP0:

`d69298b70c832955cf3bac7e0475dc7208412fc5`

It was created from current economic-flow head:

`ac3b32ffa8ff4d768525c6da2a7ae3f9e2cdddc7`

Required strategy:

1. **Do not merge `ops/oci-one-shot-install-20261019`.**
2. Selectively port/adapt installation lock, SHA-addressed release, atomic receipt, OCI response validation and narrow IAM behavior.
3. Replace stale fixed release SHA semantics with an explicitly pinned recovery/current deployment ref whose identity is recorded in the install receipt.
4. Add CP8 scientific preflight before any discovery/freeze-capable scheduled wake.
5. Reuse canonical control-plane / queue / lease semantics.
6. Add the worker/service only after local/static/tests and no-mutation canary contracts are in place.
7. Keep scheduler disabled until the recovery branch itself records exact verification status.

## 11. Oracle CP1 minimum acceptance

Operational CP1 should be considered complete only when the recovery branch has a modern deployment surface that:

- cannot silently deploy `e980d201...`;
- installs an explicit modern/recovery ref;
- is single-install locked and restartable;
- publishes only verified release state;
- emits an atomic receipt with deployed SHA;
- preserves narrow IAM behavior without committing credentials;
- runs pre-outcome code smoke tests;
- performs/defines fail-closed real Legacy bootstrap verification;
- does not start a scheduler;
- keeps all four authority flags false.

Current status before implementation:

`ORACLE_CP1 = NOT_COMPLETE`

## 12. Oracle CP2 minimum acceptance

Operational CP2 must bind scheduled wake behavior to the canonical worker protocol and additionally close the CP7/CP8 current-lineage gap:

- one lineage per wake;
- optimistic-lock lease claim;
- durable event/receipt;
- deterministic refill only where authorized;
- exact real Legacy preflight;
- current-frozen corpus snapshot + normalization;
- complete relevant peer-set binding;
- unresolved same-exposure overlap blocks independent readiness/freeze path;
- restart cannot duplicate lineage/freeze;
- no direct outcome opening;
- no capital/live authority.

Current status before implementation:

`ORACLE_CP2 = NOT_COMPLETE`

## 13. Final audit verdict for recovery entry

- `WHOLESALE_OCI_MERGE_SAFE = FALSE`
- `OCI_REUSABLE_DEPLOYMENT_PRIMITIVES_EXIST = TRUE`
- `OCI_CURRENT_SCIENTIFIC_STATE = STALE`
- `VM_AUTONOMY_INTENT_ALIGNED = TRUE`
- `VM_AUTONOMY_IMPLEMENTED = FALSE`
- `REAL_LEGACY_ORACLE_PREFLIGHT_IMPLEMENTED = FALSE`
- `CURRENT_FROZEN_DEDUP_ORACLE_PREFLIGHT_IMPLEMENTED = FALSE`
- `SCHEDULER_IMPLEMENTED = FALSE`
- `SCHEDULER_ENABLED = FALSE`
- `ORACLE_CP1 = NOT_COMPLETE`
- `ORACLE_CP2 = NOT_COMPLETE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

## Next action

Return to:

`builder/oracle-economic-loop-recovery-20261019`

and implement **CP1 modern Oracle/OCI deployment reconciliation** by selectively adapting the proven OCI deployment primitives onto the current economic branch, with scheduler still disabled and CP8 preflight requirements preserved.
