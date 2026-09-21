# BUILDER — GATE-B ROUTE-1 CONCRETE MUTATION PACK MISSION — 2026-09-21

## 0. Mission identity

Repository:

`fahimahmedb/Quant-Trade`

Work ONLY on:

`builder/gate-b-route1-concrete-mutation-pack-2026-09-21`

Expected starting HEAD:

`ad1b4d318c9e3657326e81b94cb9710b3953ffcd`

DO NOT CREATE ANOTHER BRANCH.

Mission type:

`REPOSITORY-ONLY CONCRETE OPERATIONAL PACK / NO TARGET-HOST MUTATION`

This is not another architecture review and not another F5 feasibility study.
Route 1 is already accepted as feasible.

The sole purpose is to materialize the exact future mutation bytes/operands that the
existing reserved run's Blue activation must seal.

## 1. Current reserved run — immutable input

DO NOT reserve another run.

```text
GATE_B_RUN_ID =
gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811

GATE_B_ATTEMPT_NUMBER = 1

RUN_RESERVATION_DIGEST =
sha256:97dac3e09e453dae189111c6f6d014aa2b426dea532bae6ae51de016c37ed8bc

REVOCATION_EPOCH = 1

REVOCATION_REFERENCE =
gate-b-host-relay-preseal-2026-09-21-initial-epoch
```

Authority storage:

`/var/lib/quant-p0-qualification/gate-b-authority`

The run remains reserved, unsealed and unconsumed.

## 2. Read first

Read in full:

1. `QUANT_NORTH_STAR.md`
2. `handoff/BLUE_GATE_B_ACTIVATION_SEAL_CORRECTION_2026-09-21.md`
3. `handoff/OPERATOR_GATE_B_F5_ROUTE1_HOST_EVIDENCE_CLOSURE_2026-09-21.md`
   from:
   `operator/gate-b-f5-route1-host-evidence-closure-2026-09-21@17d692beaa8013101670c0c0164c9bb204f471d9`
4. `governance/BLUE_GATE_B_F5_ROUTE1_RECEPTION_2026-09-21.md`
5. `governance/BLUE_GATE_B_F5_ROUTE1_HOST_FEASIBILITY_SPEC_2026-09-21.md`
6. `governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md`
7. `governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md`
8. `governance/TARGET_HOST_V4_RELEASE_MATERIALIZATION_2026-09-21.md`
9. `handoff/BUILDER_GATE_B_V4_MATERIALIZATION_ACTIVATION_PRESTAGE_2026-09-21.md`
10. the current activation-seal handoff and mission.

Do not reopen accepted F5 feasibility or F11/run-authority.

## 3. Fixed host/topology authority

Preserve these accepted facts:

- frozen V4 production bytes MUST remain unchanged;
- exact service remains `quant-sec-capture.service`;
- no service drop-in is permitted;
- service-visible state path remains `/var/lib/quant-p0` and
  `/opt/quant/var`;
- current qualifying-state backing is under the persistent `/mnt/quant-data`
  filesystem;
- Route 1 uses host-level nftables `inet` OUTPUT denial for TCP/443;
- frozen V4 transport is direct HTTPS/TCP and does not use QUIC;
- synthetic state selection is external infrastructure, not a new V4 state-root
  feature;
- service MUST be stopped before any reservoir switch;
- preserved qualifying state MUST NOT be used as disposable destructive-test state.

Current expected original mount-unit digest from the accepted host rebind:

`sha256:fb37ed643fcb237fcb0c3ec54ee9ceada1e376ee88cc16f39cff47ef68a19875`

Do not guess a different original unit. The later Operator relay must resolve the live
FragmentPath and verify exact bytes against that digest before replacement.

## 4. Exact run-scoped paths to freeze

Use exactly:

```text
ROUTE1_PACK_VERSION =
quant-gate-b-route1-mutation-pack/v1

SYNTHETIC_RESERVOIR =
/mnt/quant-data/gate-b-synthetic/gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811/state

RESTRICTED_EVIDENCE_ROOT =
/var/lib/quant-p0-qualification/gate-b-evidence/gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811/1

EGRESS_RULES_INSTALL_PATH =
/etc/quant/gate-b/quant-gate-b-egress.nft

EGRESS_GUARD_UNIT_INSTALL_PATH =
/etc/systemd/system/quant-gate-b-egress-guard.service

SYNTHETIC_STATE_MOUNT_UNIT_INSTALL_PATH =
/etc/systemd/system/var-lib-quant\x2dp0.mount
```

No ad-hoc /tmp authority or hidden alternate path.

## 5. Required exact artifact bytes

Create exact repository files under:

`governance/gate_b_route1/`

At minimum:

### A. nft rules

`quant-gate-b-egress.nft`

It must:

- create a dedicated `table inet quant_gate_b`;
- create an OUTPUT hook covering both IPv4 and IPv6;
- default to no broader policy change than required;
- DROP outbound TCP destination port 443;
- contain no allow exception for SEC;
- contain no rule that permits bypass through a second chain;
- be deterministic exact bytes.

The destructive Gate-B campaign must have:

`ALLOW_REAL_SEC_NETWORK = FALSE`

### B. systemd egress guard

`quant-gate-b-egress-guard.service`

It must:

- be a one-shot unit;
- load only the exact sealed nft rules file;
- become active only if the rule load succeeds;
- order before the synthetic state mount and collector service;
- be required by the temporary synthetic-state mount;
- support an explicit rollback/removal path only after the collector is stopped;
- not modify the frozen collector unit.

### C. temporary state mount authority

`var-lib-quant-p0.synthetic.mount.unit`

It represents the exact future bytes to install as the temporary
`var-lib-quant\x2dp0.mount` authority for this run.

It must:

- keep `Where=/var/lib/quant-p0`;
- bind exactly the fixed SYNTHETIC_RESERVOIR as `What=`;
- use bind/rw semantics;
- require and order after `quant-gate-b-egress-guard.service`;
- require the persistent `/mnt/quant-data` backing needed by the synthetic path;
- order before `quant-sec-capture.service`;
- preserve compatibility with unchanged `opt-quant-var.mount`;
- contain no production-service semantic change.

### D. canonical mutation manifest

`GATE_B_ROUTE1_MUTATION_PACK_2026-09-21.json`

Canonical JSON.

It must bind:

- schema/version;
- exact run ID/attempt/reservation digest;
- frozen candidate triple;
- target-host opaque identity;
- exact synthetic reservoir path;
- exact evidence root path;
- exact future install paths;
- SHA-256 digest of A/B/C exact bytes;
- expected original state-mount-unit digest;
- exact allowed mutation phases;
- exact ordered command/operation specification;
- exact verification/postcondition specification;
- exact rollback specification;
- capability matrix;
- `ALLOW_REAL_SEC_NETWORK=false`;
- statement that no activation is consumed by this artifact.

Do not include secrets.

## 6. Required command sequence semantics

The pack must define an exact fail-closed sequence, not prose such as “configure firewall”.

### PRE-MUTATION / after later one-use activation consumption

Require exact live verification of:

- service stopped / MainPID=0;
- target host identity;
- activation/run identity;
- original state mount FragmentPath;
- original state mount exact byte SHA-256 =
  `fb37ed643fcb237fcb0c3ec54ee9ceada1e376ee88cc16f39cff47ef68a19875`;
- current `/var/lib/quant-p0` backing identity;
- current `/opt/quant/var` binding;
- no existing foreign `table inet quant_gate_b`;
- synthetic reservoir path absent before creation;
- evidence root absent before creation.

Any mismatch => STOP.

### EVIDENCE / BACKUP FIRST

Before replacing any host authority:

- create the run-scoped restricted evidence root;
- save exact original mount-unit bytes and their digest into restricted evidence;
- save current nft ruleset digest;
- save mount topology;
- fsync evidence files/directories as required.

Do not edit the original file in place.

### INSTALL NETWORK GUARD

- install the exact sealed nft rules bytes at the exact install path;
- install the exact sealed guard unit bytes;
- daemon-reload if required;
- start guard;
- require active/exited success;
- verify `table inet quant_gate_b`;
- verify an OUTPUT hook exists;
- verify TCP/443 is denied.

No real SEC request is used as the verification mechanism.

### SYNTHETIC RESERVOIR SWITCH

- create exact run-scoped synthetic reservoir under /mnt/quant-data;
- prove service stopped;
- detach `/opt/quant/var` first;
- detach current `/var/lib/quant-p0` view without deleting/changing its backing bytes;
- atomically install the exact temporary synthetic mount-unit bytes;
- daemon-reload;
- start/mount the temporary `var-lib-quant\x2dp0.mount`;
- restore/start unchanged `opt-quant-var.mount`;
- prove:
  - `/var/lib/quant-p0` resolves to SYNTHETIC_RESERVOIR;
  - `/opt/quant/var` resolves through that synthetic reservoir;
  - preserved qualifying backing remains distinct;
  - egress guard remains active.

Only after these postconditions can later destructive lifecycle work proceed.

### ROLLBACK / SANITIZATION

After destructive Gate-B work and while service is stopped:

- preserve/hash the synthetic reservoir as restricted evidence;
- detach `/opt/quant/var`;
- detach synthetic `/var/lib/quant-p0`;
- restore the exact original state-mount-unit bytes from the restricted backup;
- verify restored bytes match the expected original digest;
- daemon-reload;
- restore original `/var/lib/quant-p0` mount;
- restore unchanged `opt-quant-var.mount`;
- verify original qualifying reservoir identity/inventory;
- stop/remove the temporary egress guard only after service remains stopped and state
  rollback is complete;
- verify `table inet quant_gate_b` absent after guard rollback;
- retain synthetic reservoir/evidence; do NOT delete lifecycle evidence to make state
  look clean.

No service start is authorized merely by rollback.

## 7. Capability mapping

The canonical manifest must explicitly map each future command class to an activation
capability.

At minimum:

```text
ALLOW_EVIDENCE_ROOT_SETUP
ALLOW_MOUNT_RECONFIGURATION
ALLOW_PERSISTENT_MOUNT_AUTHORITY_UPDATE
ALLOW_SYNTHETIC_STATE_SETUP
ALLOW_SYSTEMD_START_STOP
ALLOW_CONTROLLED_REBOOT
ALLOW_MISSING_MOUNT_TEST
ALLOW_WRITER_LOCK_CONTENTION_TEST
ALLOW_CHILD_FAULT_INJECTION
ALLOW_SUPERVISOR_SIGKILL

ALLOW_REAL_SEC_NETWORK = FALSE
```

Release materialization remains governed by the already-authoritative V4 procedure,
not reimplemented here.

## 8. Verification requirements

Repository-side verification must at minimum:

- prove deterministic byte digests for A/B/C;
- validate canonical JSON manifest;
- verify manifest paths/digests match exact files;
- verify run ID/candidate values are exact;
- assert nft artifact contains `table inet quant_gate_b`, `hook output`,
  TCP and dport 443 denial;
- assert no SEC allow exception exists;
- verify systemd guard references only the exact sealed nft path;
- verify temporary mount unit references exactly the fixed synthetic reservoir;
- verify temporary mount unit requires the guard;
- verify no file modifies frozen V4 `src/`, frozen service unit, or Product code;
- run `systemd-analyze verify` against generated unit bytes when available;
- fail closed if an exact semantic cannot be verified repository-side.

Do not claim actual nft/kernel behavior from repository tests. That remains Operator evidence.

## 9. Explicit prohibitions

DO NOT:

- touch target host;
- reserve another run;
- seal activation;
- consume activation;
- modify frozen V4 production bytes;
- modify `quant-sec-capture.service`;
- create a Product feature;
- contact SEC;
- declare Gate B PASS;
- declare t0.

## 10. Required final handoff

Write exactly:

`handoff/BUILDER_GATE_B_ROUTE1_CONCRETE_MUTATION_PACK_2026-09-21.md`

Required Builder disposition:

`GATE_B_ROUTE1_CONCRETE_MUTATION_PACK = READY_FOR_BLUE_SEAL_INTEGRATION`

or one precise blocker.

The handoff must give:

- changed files;
- exact SHA-256 for every pack artifact;
- exact test commands/results;
- exact remaining TARGET_HOST_ONLY checks;
- explicit statement that no activation was sealed/consumed;
- exact mutation-pack manifest digest.

## 11. Economic alignment

```text
ECONOMIC_PROGRESS =
Rail A already has one real run reservation; this mission converts the accepted Route-1
feasibility design into the exact sealable mutation authority needed to execute Gate B.

REMAINING_BLOCKER =
exact Route-1 mutation bytes/operands are not yet sealed.

EXIT_CONDITION =
one deterministic concrete mutation pack is ready for Blue to bind into the already
reserved run's activation without another architecture/audit cycle.
```
