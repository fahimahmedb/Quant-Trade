# TARGET-HOST GATE B ENTRANCE CONTRACT — CANDIDATE — 2026-09-21

Authority when promoted: Blue / Mission Control.
Architectural authority: `QUANT_NORTH_STAR.md`.

## Status

`CONTRACT_STATUS = PREPARED_CANDIDATE / NOT_AUTHORIZED_FOR_EXECUTION`

`GATE_A_V4_REPOSITORY_DISPOSITION = PASS`

`TARGET_HOST_READY = FALSE`

`GATE_B = NOT_STARTED`

`t0 = NOT_DECLARED`

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

This candidate replaces the stale V3-pinned target-host entrance contract only
after Blue promotes the hybrid qualification method and explicitly activates a
V4 target-host contract.

It MUST NOT be used as authority for a qualifying launch before that decision.

## 1. Exact frozen repository object

Frozen candidate:

`blue/p0-gate-a-v4-frozen-2026-09-20@4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Git tree:

`4d15ef6f471213ee6ab56337b555d2906ef9bf16`

Verified input-tree digest from exact-head CI artifact:

`sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2`

Selected candidate CI:

`35536353538 = COMPLETED / SUCCESS`

Independent Astra v4 final HEAD:

`afe25984b0ddd261fda143d858106c3c71e45149`

Independent exact-head CI:
- `35545297473 = COMPLETED / SUCCESS`
- `35545297451 = COMPLETED / SUCCESS`

Blue repository disposition:

`GATE_A_V4_REPOSITORY_DISPOSITION = PASS`

No proof may be transferred to a different SHA without a new Blue disposition.

## 2. Gate B purpose

Gate B proves target-host properties that repository evidence cannot prove.

Gate B must verify the exact candidate on the actual qualifying host before any
qualifying `t0` event may occur.

Gate B PASS does NOT itself declare t0.

## 3. Required deployment topology

Required target topology remains:

- immutable detached release at
  `/opt/quant-releases/4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072/`;
- `/opt/quant` is a fixed mounted/bound service view of that release;
- `/var/lib/quant-p0` is the durable P0 state root;
- `/opt/quant/var` is the writable view of that state root;
- code outside `var` is read-only from the service view;
- development checkout is not the qualifying runtime;
- missing durable-state mount must fail closed before service start.

Any mismatch:

`GATE_B = FAIL / NO_T0`

## 4. B1 — immutable release / state isolation

Evidence must bind:

- deployed Git SHA;
- Git tree;
- verified input-tree digest or exact equivalent regenerated under the
  authoritative verifier;
- clean release status;
- release mount source/options;
- `/opt/quant` mount source/options;
- `/opt/quant/var` and `/var/lib/quant-p0` identity;
- ownership and permissions;
- absence of an unexpected writable production-code path;
- fail-closed behavior when the durable state mount is intentionally absent in
  the controlled destructive test.

A fresh local directory silently replacing the missing state mount is a blocker.

## 5. B2 — actual filesystem durability semantics

On synthetic/offline files located on the same target filesystem used by P0,
verify:

- advisory `flock`;
- hard-link creation;
- same-filesystem publication assumptions;
- atomic rename where relied upon;
- regular-file fsync;
- directory fsync;
- durability across controlled restart/reboot for acknowledged synthetic state;
- writer-lock contention fails closed.

Repository fault-matrix evidence is supporting evidence only.
The real filesystem behavior is `TARGET_HOST_ONLY`.

## 6. B3 — loaded systemd authority

Bind the ACTUALLY LOADED service, not a file-name assumption.

Record:

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
- TimeoutStopUSec;
- EnvironmentFiles;
- InvocationID when running;
- repository unit digest;
- loaded fragment digest;
- effective-unit digest emitted by the supervisor.

Mandatory:
- loaded fragment matches the exact repository unit;
- no unbound drop-in;
- `StartLimitBurst=5`;
- all other frozen service semantics match;
- transient ExecStart execution metadata does not alter the v4 effective-unit
  digest;
- real semantic command drift remains fingerprint-changing or rejected.

Any unknown mandatory property is FAIL, not PASS.

## 7. B4 — runtime image / process identity

Bind:

- OS/distribution;
- kernel;
- boot id;
- machine/host identity in restricted evidence;
- Python executable real path;
- Python version/implementation;
- OpenSSL/runtime version;
- relevant package/environment identity;
- cgroup/service manager identity.

Runtime identity at Gate B entrance becomes a Gate C invariant unless the
authoritative amendment says otherwise.

## 8. B5 — durable state authority / anti-pre-seeding

Before qualifying launch:

- inventory acquisition-critical P0 authority/provenance files;
- hash/bind relevant state inventory;
- verify no unrecognized writer holds the collector lock;
- verify deployment-authority lineage;
- verify no unexplained supervisor/lifecycle/scheduler/attempt pre-seeding;
- verify no integrity latch;
- verify no referenced raw-object loss;
- preserve explainable prior state rather than deleting inconvenient history.

If unauthorized pre-seeding can survive and retrospective audit can still return
accountable:

`REAL_DEFECT`

and Gate B stops.

## 9. B6 — single writer / global requester budget

Verify:

- one qualifying P0 writer authority;
- no Product runtime shares writable P0 state;
- one global SEC requester-budget authority;
- requester identity exists privately when required;
- requester identity absence fails closed;
- no second SEC requester bypasses the global budget.

No private requester identity or filing-specific content enters public evidence.

## 10. B7 — fingerprint / materialization

Require:

- materialized fingerprint exists;
- active fingerprint == materialized fingerprint;
- candidate SHA/tree/input-tree identity is consistent with materialization;
- stale/foreign/missing materialization fails closed;
- materialization does not silently rewrite stale evidence;
- effective service digest is part of the acquisition-critical binding.

## 11. B8 — destructive lifecycle campaign

Using controlled synthetic/offline state where destructive behavior would
contaminate qualifying evidence, verify on the real host:

- normal systemd start;
- systemd stop;
- fresh authorized start;
- abnormal child failure;
- child SIGKILL where applicable;
- supervisor SIGKILL;
- replacement supervisor cannot forge automatic-restart witness;
- restart delay/burst behavior;
- controlled host reboot;
- state mount restored before service;
- missing-mount startup blocked;
- writer-lock contention blocked.

Every lifecycle transition must have externally attributable provenance.

## 12. B9 — one-use deployment authority

Before the future qualifying launch, Gate B must verify the one-use authority
mechanism with non-qualifying/synthetic evidence:

- authority is fresh;
- exact fingerprint bound;
- exact host boot identity bound as required;
- nonce/reference is unique;
- consumption is durable;
- replay fails closed;
- child launch cannot occur before materialization/authority validation.

The authority used for destructive Gate-B testing MUST NOT be reused for the
future t0 launch.

## 13. B10 — post-destructive sanitization

After destructive Gate-B exercises:

1. stop the service;
2. isolate/remove synthetic test state according to the deployment contract;
3. select/bind the exact future Gate-C persistent state root;
4. re-run state inventory;
5. verify no stale deployment authority remains;
6. verify no ambiguous lifecycle rows remain;
7. verify no integrity latch;
8. re-bind SHA/tree/input-tree/fingerprint/service/runtime/mount identity;
9. seal the final Gate-B entrance artifact.

Any ambiguity:

`GATE_B = BLOCKED / NO_T0`

## 14. Required restricted Gate-B artifact

Create a hash-addressable restricted artifact, conceptually:

`TARGET_HOST_GATE_B_ENTRANCE_<UTC>.json`

Minimum fields:

- schema/version;
- candidate SHA;
- Git tree;
- verified input-tree digest;
- exact repository CI run IDs;
- independent Astra audit HEAD/run IDs;
- target host opaque identity;
- boot id;
- runtime identity;
- mount topology;
- state-root inventory digest;
- loaded systemd properties;
- repository unit digest;
- loaded fragment digest;
- effective-unit digest;
- active/materialized fingerprint;
- requester-budget/single-writer verdicts;
- deployment-authority test references;
- destructive lifecycle artifact references;
- every B1–B10 check as PASS/FAIL/UNKNOWN;
- overall Gate-B verdict;
- explicit `t0_declared: false`.

Do not publish restricted runtime/acquisition data.

## 15. Gate B decision

All mandatory target-host checks evidenced:

`GATE_B = PASS`

Anything failed/unknown:

`GATE_B = BLOCKED`

Even on PASS:

`t0 = NOT_DECLARED`

A separate precommit + qualifying launch is required.

## 16. Current non-authority

Until Blue explicitly promotes this candidate contract:

`CONTRACT_STATUS = PREPARED_CANDIDATE / NOT_AUTHORIZED_FOR_EXECUTION`

`REAL_CAPITAL_AUTHORIZED = FALSE`
