# TARGET-HOST QUALIFICATION / FINAL RODAGE ENTRANCE CONTRACT — 2026-09-20

Authority: Blue / Mission Control.
Architectural authority: `QUANT_NORTH_STAR.md`.
Repository Gate input: `handoff/BLUE_GATE_A_V3_FINAL_DISPOSITION_2026-09-20.md`.
Deployment-contract source: `governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md`.

Status:
`PREPARED / NOT_EXECUTED / t0_NOT_DECLARED`

This document defines the minimum evidence required before Blue may even consider declaring t0 on the qualifying target host. It does not claim that the target host exists, is configured, or is ready.

## 1. Exact immutable repository input

The only candidate authorized for this entrance is:

- branch: `blue/p0-gate-a-v3-frozen-2026-09-20`
- SHA: `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`
- Builder exact-head CI: `35514180655 = COMPLETED / SUCCESS`
- independent Astra audit HEAD: `33995d03c8632e5c3a7b77a12b87366fb06b4d30`
- independent Astra exact-head CI: `35517935710 = COMPLETED / SUCCESS`
- Blue Gate A repository disposition: `PASS`

No proof from another SHA may be silently transferred.

## 2. Entrance principle

Target-host entrance is a separate evidence domain.

Repository PASS proves the repository-side proof machinery under its audited threat model.
Target-host qualification must prove that the real running environment preserves the assumptions on which that machinery depends.

Until every mandatory entrance condition below is evidenced:

`READY_FOR_FINAL_RODAGE = FALSE`

`t0 = NOT DECLARED`

## 3. Required deployment topology

The target host must evidence the topology already selected by the P0 qualifying deployment contract:

- `/opt/quant-releases/<exact-git-sha>/` is a complete detached release checkout for the exact candidate;
- release checkout has self-contained Git metadata and no development-worktree/alternate dependency;
- `/opt/quant` is a fixed bind/mount view of that release, not a moving symlink;
- `/var/lib/quant-p0/` is the durable writable operational-state volume;
- `/opt/quant/var` is the writable bind view of that durable volume;
- everything outside `var` is read-only from the running-service view;
- the release backing tree cannot be mutated by development/deployment automation during observation;
- mounts are established before service start and restored before service start after reboot;
- missing state mount must fail startup rather than silently create fresh local state.

Any mismatch is:

`TARGET_HOST_ENTRANCE = FAIL / NO_T0`

## 4. Exact release and tree binding

Collect and preserve target evidence for:

- `git rev-parse HEAD` in the deployed release;
- `git status --porcelain` = empty;
- `git rev-parse^{tree}` / exact Git tree id;
- repository input-tree digest used by the P0 verification mechanism;
- acquisition-critical fingerprint;
- materialized manifest schema/version;
- active fingerprint/manifest versus materialized fingerprint/manifest;
- release filesystem mount source and mount options.

Required relation:

`deployed SHA == frozen Gate A candidate SHA`

and the deployed bytes must agree with the expected tree/fingerprint.

Foreign, stale or auto-repaired freezes are forbidden.

## 5. Loaded systemd authority

The qualifying service must be the actual loaded systemd service, not a shell imitation.

Verify and record:

- `systemctl show quant-sec-capture.service`;
- `FragmentPath`;
- `DropInPaths`;
- `ExecStart`;
- `WorkingDirectory`;
- `Restart`;
- `RestartUSec`;
- `StartLimitIntervalUSec`;
- `StartLimitBurst`;
- `KillMode`;
- `KillSignal`;
- `TimeoutStopUSec`;
- `EnvironmentFiles`;
- loaded unit-file SHA-256;
- repository `deploy/quant-sec-capture.service` SHA-256;
- effective unit digest emitted/bound by the supervisor.

Mandatory:
- loaded fragment must byte-match the frozen repository unit;
- no unbound drop-ins;
- service manager must be recognised as `systemd`;
- a genuine per-invocation `INVOCATION_ID` must exist;
- effective values must match frozen qualifying semantics.

Failure classification:
`TARGET_HOST_ONLY / ENTRANCE_BLOCKER`

## 6. Runtime-image binding

Repository fingerprinting is not a full operating-system/image hash.

Record target-host runtime identity at entrance:

- OS/distribution and kernel identity;
- Python executable real path;
- Python version + implementation;
- OpenSSL/runtime version;
- installed package/environment identity relevant to the service;
- container/image/package digest if applicable;
- host boot id;
- machine/host identity in the restricted evidence artifact.

The same runtime identity must be checked again at rodage exit.

Unexpected runtime drift during rodage invalidates the observation interval unless explicitly classified and restarted under a new authorized entrance.

## 7. Durable-state-root cleanliness — mandatory Gate-A residual closure

This is a mandatory target-host entrance condition because Astra found that acquisition fingerprint equality alone does not bind `service_managed` / service invocation id.

Before the first qualifying service start of the final rodage:

1. identify the exact durable state root presented to the service;
2. prove ownership/permissions and writer policy;
3. record current file inventory + hashes/metadata for P0 authority/provenance files;
4. verify no unrecognized process is currently holding the collector writer lock;
5. verify no unauthorized qualifying lifecycle rows, supervisor events, deployment-authority rows or scheduler/attempt mutations pre-seed the state;
6. verify any existing preserved state has an explainable lineage from authorized prior P0 activity;
7. if a clean-new reservoir is intentionally required, establish it explicitly — never obtain a "clean" state by deleting inconvenient journals from an existing qualifying reservoir;
8. bind the resulting entrance inventory into the restricted target-host evidence artifact.

Critical falsifier:

If unauthorized pre-seeding can occur and the subsequent retrospective audit can still return `accountable=True`, classify:

`REAL_DEFECT`

and:

`REOPEN_GATE_A = TRUE`

Until the durable-state-root authority is evidenced:

`NO_T0`

## 8. Single-writer and global SEC budget

Verify on the target host:

- only the qualifying P0 service can mutate the qualifying P0 state;
- collector service lock works on the actual filesystem;
- no Product QuantSystem shares the writable P0 `var` tree;
- no second SEC requester bypasses the one global requester budget;
- requester identity is privately configured and not committed;
- absence of requester identity fails closed;
- local filesystem supports the durability assumptions used by the code:
  - `flock`
  - hard links
  - atomic rename
  - directory fsync
- staging and raw publication are on the same filesystem.

Any ambiguous second writer or second requester authority is a blocker.

## 9. Deployment authority and first qualifying launch

Before final rodage service start:

- create explicit one-use deployment authority according to the frozen supervisor contract;
- record the authority nonce/reason/timestamp;
- verify it is fresh and unconsumed;
- start through systemd;
- verify the generated `CHILD_LAUNCH_AUTHORIZED` event binds:
  - supervisor id;
  - systemd invocation id;
  - boot id;
  - lifecycle cause;
  - exact acquisition fingerprint;
  - qualifying mode;
  - deployment-authority nonce;
- verify `record_service_start()` consumes/binds exactly one external launch authority;
- verify duplicate/replayed claim fails closed.

A shell-started collector is not a qualifying launch.

## 10. Pre-t0 destructive/offline fault validation

Before the final live rodage, destructive failure exercises must use synthetic/offline state where required so preserved acquisition evidence is not destroyed.

At minimum verify on the actual target environment or an environment identical in the relevant host semantics:

- `systemctl stop` produces expected terminal supervisor/service evidence;
- `systemctl start` requires fresh valid deployment authority when appropriate;
- child SIGKILL / abnormal child failure is witnessed by the same live supervisor;
- automatic restart cannot be claimed by a replacement supervisor without genuine witness;
- service restart limits and delay match loaded systemd values;
- host reboot preserves the durable state mount and does not silently create a new reservoir;
- missing mount blocks startup;
- writer-lock contention fails closed.

These are TARGET_HOST_ONLY proofs; repository CI is not a substitute.

## 11. Final bounded pre-t0 rodage

Only after Sections 3–10 pass may Blue authorize a bounded final pre-t0 rodage.

The rodage plan must name before start:

- exact start timestamp;
- exact host;
- exact candidate SHA/tree/fingerprint;
- exact runtime-image identity;
- expected poll/reconcile cadence;
- expected lifecycle/supervisor behavior;
- expected durability/integrity checks;
- observation duration;
- stop conditions;
- invalidating outcomes.

Rodage must use the actual qualifying systemd service and effective environment.

Readiness/audit success generated by a shell process with a different environment is not admissible.

## 12. Mandatory invalidators / NO_T0

Any of the following blocks t0:

- deployed SHA/tree differs from frozen candidate;
- dirty deployed release;
- writable mutation outside `var`;
- moving symlink or development worktree deployment;
- missing/incorrect durable-state mount;
- unexplained pre-seeded durable authority/provenance state;
- unbound systemd drop-in;
- loaded unit differs from repository unit;
- no genuine systemd invocation identity;
- effective unit digest mismatch;
- runtime image identity unresolved or drifts unexpectedly;
- active/materialized fingerprint mismatch;
- stale/foreign fingerprint materialization;
- no valid one-use deployment authority;
- duplicate/ambiguous launch authority;
- unexplained operator intervention;
- integrity latch / missing referenced raw object;
- second writer or second SEC requester authority;
- startup succeeds with missing state mount;
- target-host SIGKILL/restart/reboot semantics contradict the audited assumptions;
- retrospective audit is non-accountable;
- any new REAL_DEFECT.

For every invalidator:

`t0 = NOT DECLARED`

No "mostly passed" entrance is sufficient.

## 13. Required entrance evidence artifact

Create a restricted, hash-addressable artifact outside the immutable release, for example:

`TARGET_HOST_P0_RODAGE_ENTRANCE_<UTC>.json`

It must bind at minimum:

- artifact schema/version;
- target host identifier;
- entrance timestamp UTC;
- frozen candidate SHA;
- Git tree;
- verified input-tree digest;
- Builder CI run id;
- Astra final audit SHA;
- Astra final CI run id;
- acquisition fingerprint;
- materialized manifest/schema;
- effective service configuration;
- loaded systemd fragment digest;
- repository unit digest;
- effective unit digest;
- runtime image identity;
- boot id;
- mount topology + mount options;
- durable-state-root inventory digest;
- ownership/permission evidence;
- deployment authority reference/nonce digest;
- supervisor launch reference;
- single-writer/budget checks;
- offline fault-test artifact references;
- each entrance check as PASS/FAIL/UNKNOWN;
- overall `READY_FOR_FINAL_RODAGE`;
- explicit `t0_declared: false`.

Do not place private requester identity, filing identities, raw SEC content or interpretable acquisition detail into a public artifact.

## 14. Decision states

Before execution:
`TARGET_HOST_ENTRANCE = PREPARED_ONLY`

All checks evidenced:
`TARGET_HOST_ENTRANCE = PASS`
`READY_FOR_FINAL_RODAGE = TRUE`

Any required check failed/unknown:
`TARGET_HOST_ENTRANCE = BLOCKED`
`READY_FOR_FINAL_RODAGE = FALSE`

Even after entrance PASS and rodage success:

`t0 = NOT DECLARED`

until Blue makes a separate explicit t0 decision from the completed target-host evidence.

## 15. Current status

`GATE_A_V3_REPOSITORY_DISPOSITION = PASS`
`TARGET_HOST_ENTRANCE = PREPARED_ONLY`
`READY_FOR_FINAL_RODAGE = FALSE`
`t0 = NOT DECLARED`
`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`
`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`
`GATE_B = NOT_STARTED`
`REAL_CAPITAL_AUTHORIZED = FALSE`
`PRODUCT_INTEGRATION = PAUSED`
