# P0 qualifying deployment isolation contract

Decision basis: remote P0 `8dbe25aea136332f73174917af42dc524f8454e7`,
exact-head CI `35476749853` COMPLETED/SUCCESS, North Star and latest Blue
master checkpoint (including Section 0). Later committed evidence supersedes
older checkpoint claims. This contract does not declare t0 or admissibility.

## Decision and scope

Retain the conservative acquisition fingerprint and isolate a pinned P0
deployment. Do not narrow imports in this mission. Freeze the P0 deployment,
not repository development or Product integration. No other mission is merged.

Three different states must remain distinguishable:

1. Development branches: changing GitHub refs, no authority over running P0.
2. Product integration trees: Economic/Forward integration elsewhere, no write
   access to P0 state, no second SEC acquisition authority.
3. Qualifying P0 deployment: exact release, environment, loaded service and
   persistent evidence. Only this state supplies continuity evidence.

`sec-serve` constructs the broad QuantSystem and calls boot() before its
acquisition-only serve_sec() loop. Constructors, registry refresh, recovery and
task seeding really execute. A syntax/import failure in Research can prevent
capture. The fingerprint therefore hashes every Python file under src/quant
and src/autonomous_research, plus explicit entrypoint/proof files and service
definitions. This conservative closure is justified today.

## Accepted topology, conditional on target-host verification

* `/opt/quant-releases/<exact-git-sha>/`: complete dedicated release checkout,
  detached HEAD, with a self-contained `.git` directory; no alternates pointing
  into development. Commit, tree and deployed bytes must agree.
* `/opt/quant`: fixed bind/mount view of that release, preserving the existing
  WorkingDirectory and `--root /opt/quant` contract. Not a moving symlink.
* `/var/lib/quant-p0/`: durable writable operational state, retained across
  replacement releases; `/opt/quant/var` is its writable bind view.
* Everything outside var is read-only in the service view AND cannot be changed
  through the backing release path by development/deployment automation during
  observation. A read-only bind alone does not protect a writable backing tree.
* Mounts are established and checked before service start, including after host
  reboot. If the state mount is absent, startup must fail, never create fresh
  state beneath the mount point. Demonstrate this on the target host.
* SEC directories and mount roots are durably provisioned before capture. Confirm
  local filesystem support for flock, hard links, atomic rename and directory
  fsync; staging and raw publication must reside on the same filesystem.
* Only the P0 service writes its state. Do not share the entire var tree with a
  live Product QuantSystem: boot/heartbeat also write control, registry and Book
  scaffolding. Those P0-local objects are not a second authoritative capital Book.
* No Product SEC requester bypasses the one global requester budget. Separate
  checkouts/hosts do not create separate SEC fair-access allowances.
* Development actors receive only the approved opaque P0 projection, never raw
  or per-event operator journals, counts, timing distributions or storage sizes.

The repository unit does not enforce these mounts or permissions. This is an
acceptance contract to verify, not a claim that infrastructure exists. Preserve
the existing unit and reject unbound drop-ins; supply mount ordering externally
without changing its effective frozen semantics. No mounted paths are changed
by this mission.

## Binding and replacement

A GitHub merge alone has no runtime effect. Changing covered files in the
deployed tree changes the recomputed manifest, even if Python already imported
old bytes: qualifying requests revalidate materialization and fail closed.
The cached active fingerprint is not silently replaced. A SHA-only change can
also fail the separate materialized commit check after restart.

Pin interpreter/stdlib/OpenSSL/runtime image, requester identity, effective
configuration and loaded unit as well as source. The semantic fingerprint binds
runtime version strings; those are not a complete operating-system image hash.
Record the runtime image/package identity as additional deployment evidence.
Resource starvation or another service's network use can still break liveness
without changing the source fingerprint; isolation does not replace coverage
and obligation audits.

The fragment loaded by systemd must match the repository unit, with no drop-ins,
and the effective definition digest must be the one actually used by the service.
The manifest is host-bound: never copy a foreign-host freeze and call it active.
Source archive without Git metadata and linked development worktree are not the
approved release form: current commit resolvers are not uniform for worktrees.

An intentional release replacement stops the old writer, preserves the same
durable evidence volume, installs/verifies the new view and records explicit
one-use deployment authority, consumed authority nonce and lifecycle provenance.
Never replace a live bind or discard journals to obtain a clean-looking start.
A deployment authority proves cause; it does NOT waive fingerprint stability,
gaps, or the reset requirement for changed acquisition semantics. New supervisor
without positive deployment authority remains invalidating by default. Only the
same live supervisor can attest its directly witnessed child failure/restart.

## Alternatives attacked

| Criterion | Freeze shared Quant deployment | Dedicated pinned P0 (selected) | Narrow SEC closure |
|---|---|---|---|
| Capture/PIT | Existing guarantees, deployment discipline essential | Same guarantees; preserve durable volume | Must reprove boot/recovery/persistence equivalence |
| Firewall | Existing boundaries | Also isolate access to state and evidence | Must retain proof/projection dependencies |
| Binding | Existing fingerprint | Exact release + environment + service + host evidence | New membership, new fingerprint and rodage |
| Failure/restart | Any shared edit can stop capture | Mount loss, backing writes, host updates remain hazards | New launch/import failure paths |
| Accidental reset | High if development uses the same tree | Lower; GitHub movement cannot touch deployed bytes | Lower for excluded modules, not zero |
| Complexity/auditability | Simple, operationally restrictive | Small operational contract, no runtime refactor | More code and equivalence proof now |
| Opportunity cost | Blocks covered deployments in the shared runtime, not Git work | Other development/deployments continue elsewhere | Delays capture qualification for an avoidable refactor |
| North Star | Compatible but constraining | One logical acquisition authority, independent Build progress | Compatible only with one owner of SEC obligations |

Narrowing could later extract the existing timer/capture-step/heartbeat/lifecycle
contract from broad boot. It is not merely deleting hashed filenames or making
imports lazy. Audit, firewall, launchers and persistence remain critical even if
not direct imports. There is no demonstrated need to pay that cost before the
first t0 when deployment isolation suffices.

## Exact target-runtime rodage entrance conditions

READY_FOR_FINAL_RODAGE remains FALSE until these prerequisites are evidenced:

1. Exact candidate SHA and tree, clean deployed content, exact-head successful CI.
2. Target host/operator identified; actual systemd available; mounts, persistence,
   access restrictions, runtime image and single-writer/budget scope verified.
3. Production loaded-unit values/fragment/digest verified; no foreign environment
   or unbound override. Authorized requester identity available privately.
4. Materialized schema v2 manifest created explicitly in the effective target
   service environment, semantic schema v1; active and materialized manifests
   match. Missing/stale/foreign freezes never auto-repair.
5. Durable deployment authority and lifecycle provenance bound to this candidate;
   no unresolved known capture/PIT/firewall defect or durable integrity latch.
6. A bounded pre-t0 rodage protocol names expected observations and invalidating
   outcomes, including actual systemctl stop/start and host SIGKILL behavior.
   Destructive fault exercises use synthetic/offline state before the final live
   rodage; they must not overwrite the preserved acquisition reservoir.

The result artifact is produced AFTER the final candidate commit, outside the
immutable release (restricted evidence volume/artifact storage). Bind exact SHA,
Git tree, verified input-tree digest, acquisition fingerprint, full manifest/schema,
effective runtime configuration, runtime image identity, repository AND loaded
service digests, exact CI run id, UTC observation interval and lifecycle/authority
references. Verify the same bindings before and after rodage. Do not commit an
artifact and then call the new commit the tested head; no self-referential SHA.

Publish only opaque verdicts and binding metadata. Internal request/obligation
evidence remains restricted. Readiness/audit successes at rodage end must come
from the actual service, not a shell with a different effective environment.
Rodage success establishes readiness for Blue's later decision, never 14 days.

t0 = NOT DECLARED

P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS
