# TARGET-HOST GATE B ENTRANCE CONTRACT — 2026-09-21

Authority: Blue / Mission Control.
Architectural authority: `QUANT_NORTH_STAR.md`.

## Status

`CONTRACT_STATUS = AUTHORITATIVE_PROCEDURE / NOT_ACTIVATED`

`GATE_A_V4_REPOSITORY_DISPOSITION = PASS`

`TARGET_HOST_READY = FALSE`

`GATE_B = NOT_STARTED`

`t0 = NOT_DECLARED`

`P14D_GOVERNANCE_STATUS = HISTORICAL / SUPERSEDED_FOR_FUTURE_QUALIFICATION`

This contract is the authoritative Gate-B entrance procedure for frozen V4 under
`P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1`.
It does NOT authorize target-host mutation. A separate sealed Blue activation
artifact is mandatory before the first mutating command.

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

`CONTRACT_STATUS = AUTHORITATIVE_PROCEDURE / NOT_ACTIVATED`

`REAL_CAPITAL_AUTHORIZED = FALSE`


## 17. Hardening addendum — mandatory before activation

The following controls are mandatory parts of any activated successor.

### 17.1 Explicit activation artifact

No mutating Gate-B command is authorized merely because this candidate file
exists.

Before the first mutation, the operator must possess an explicit Blue activation
record binding:

- activated contract path/version;
- activated contract digest;
- exact frozen candidate SHA/tree/input-tree digest;
- exact operator runbook version/digest;
- allowed target host opaque identity;
- authorization timestamp;
- `GATE_B_RUN_ID`.

Missing or mismatched activation:

`GATE_B_MUTATION_AUTHORIZED = FALSE`

### 17.2 Unique Gate-B attempt identity

Every destructive qualification attempt must receive a unique:

`GATE_B_RUN_ID`

All sub-artifacts must bind that run ID.

The first mandatory FAIL makes that run terminal:

`GATE_B_RUN_STATUS = FAILED_TERMINAL`

A repaired retry requires a NEW run ID. Red evidence from the failed run must be
retained immutably.

Blue decides whether prior PASS evidence is reusable; the operator cannot decide
that locally.

### 17.3 Host time authority

Before lifecycle timing evidence is admissible, bind:

- current UTC wall clock;
- host timezone configuration;
- boot ID;
- NTP/synchronization status;
- realtime-to-monotonic clock correlation snapshot;
- time-service identity/configuration relevant to synchronization.

A t0-capable launch later must use an externally attributable lifecycle timestamp
(systemd/journal or equivalent), not an operator-typed timestamp.

Unsynchronized or ambiguous time authority:

`GATE_B = BLOCKED`

### 17.4 Evidence-retention authority

Bind and verify:

- persistent/restricted evidence root;
- filesystem and mount identity for that evidence root;
- journald/log persistence/retention relevant to Gate C;
- sufficient disk/inode headroom for the planned observation window;
- hash-addressable manifest of every Gate-B sub-artifact.

Evidence loss, truncation or unexplained rotation that destroys mandatory proof is:

`GATE_B = BLOCKED`

not “no defect observed”.

### 17.5 Network / proxy / TLS binding

Before any real-source qualifying phase, bind at an opaque/non-secret level:

- effective proxy-related environment/configuration;
- resolver identity/configuration relevant to the service;
- TLS/OpenSSL trust/runtime identity;
- requester network-path identity sufficient to detect drift;
- any service environment file that can alter network behavior.

Synthetic/destructive Gate-B tests must not make real SEC requests unless a
specific test explicitly requires it and Blue has separately authorized that
network activity.

### 17.6 Resource-health baseline

Before future Gate C, record at minimum:

- filesystem free bytes;
- inode usage/headroom;
- P0 state-root size;
- restricted evidence-root size;
- process RSS/memory;
- open file-descriptor count and limits;
- relevant cgroup/process limits;
- journald/evidence retention headroom.

Do not invent arbitrary PASS thresholds.

Unexpected monotonic growth or insufficient headroom is evidence requiring
classification before t0.

### 17.7 Safe synthetic-state fallback

If the exact target topology cannot safely exercise a destructive property without
contaminating preserved qualifying state, STOP.

Do not improvise:
- ad hoc path substitution;
- manual journal deletion;
- hidden bind-mount swaps;
- hand-edited authority state.

Classify:

`MISSING_OPERATIONAL_PROOF / GATE_B_BLOCKER`

until a reproducible safe mechanism exists.

### 17.8 Artifact chain

The final Gate-B artifact must include or reference:

- `GATE_B_RUN_ID`;
- Blue activation artifact digest;
- contract digest;
- runbook digest;
- every sub-artifact digest;
- time-authority snapshot digest;
- resource-baseline digest;
- network/runtime binding digest;
- final sanitization artifact digest.

This creates a reviewable evidence chain rather than a bag of unrelated files.


## 18. Activation and evidence-schema references

Any activated successor must reference and bind an activated form of:

- `governance/BLUE_GATE_B_ACTIVATION_TEMPLATE_2026-09-21.md`;
- `governance/TARGET_HOST_GATE_B_EVIDENCE_SCHEMA_2026-09-21.json`.

The activation artifact is the mutation authority boundary.

The Gate-B final artifact must validate against the activated evidence schema or
a later explicitly superseding schema.

A prose “PASS” that cannot satisfy the machine-checkable evidence schema is not an
admissible Gate-B PASS.


## 19. Release materialization prerequisite

Before B1 may PASS, the exact SHA-addressed release must satisfy an activated
successor of:

`governance/TARGET_HOST_V4_RELEASE_MATERIALIZATION_2026-09-21.md`.

A release path name, branch checkout or development worktree is not admissible
identity evidence.

The release-materialization artifact becomes a required Gate-B sub-artifact.
