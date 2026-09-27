# OPERATOR — GATE B F5 ROUTE-1 HOST FEASIBILITY — 2026-09-21

## 0. Final disposition

`F5_ROUTE1_FEASIBILITY = NOT_PROVEN`

`RETURN_CONTROL_TO = BLUE`

This is a target-host read-only feasibility handoff for Astra finding F5 only.
It does not authorize Gate-B mutation, does not execute the destructive lifecycle
campaign, does not declare Gate B PASS, and does not declare t0.

```text
TARGET_HOST_MUTATION_PERFORMED = FALSE
SYSTEMD_LIFECYCLE_MUTATION_PERFORMED = FALSE
FIREWALL_MUTATION_PERFORMED = FALSE
MOUNT_MUTATION_PERFORMED = FALSE
RESERVOIR_CREATED_OR_DELETED = FALSE
RELEASE_MATERIALIZATION_PERFORMED = FALSE
P0_STATE_MUTATION_PERFORMED = FALSE
REAL_SEC_NETWORK_REQUESTS_MADE_BY_THIS_MISSION = 0
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
```

## 1. Mission identity and authorities

Mission branch:

`operator/gate-b-f5-route1-host-feasibility-2026-09-21`

Verified remote mission HEAD before this handoff:

`5e88625bc10a30f3e0d2dcc4b43d57322b2ee147`

The mission file embedded in that snapshot still names an older starting HEAD,
`366d9b5ccb2a0ce7dfae3a923d3e93beceb93aab`. The branch ref itself resolved
exactly to the user-specified `5e88625...`, so the remote branch ref was treated
as the operational starting authority.

Read:
- `QUANT_NORTH_STAR.md`;
- `governance/BLUE_GATE_B_F5_ROUTE1_HOST_FEASIBILITY_SPEC_2026-09-21.md`;
- `handoff/OPERATOR_GATE_B_F5_ROUTE1_HOST_FEASIBILITY_MISSION_2026-09-21.md`;
- `governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md`;
- `governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md`;
- Builder F5 prestage from
  `builder/gate-b-offline-lifecycle-sanitization-prestage-2026-09-21@6693b1e91febe907151e69f27807373c10eb40da`,
  file `handoff/BUILDER_GATE_B_OFFLINE_LIFECYCLE_SANITIZATION_PRESTAGE_2026-09-21.md`.

The Builder prestage concluded that frozen V4 contains no production-reachable
offline transport selector and no independent state-root selector. Therefore
Route 1 can close F5 only if the target host can supply both controls externally,
without changing the loaded unit, ExecStart, WorkingDirectory, interpreter, code,
or effective V4 semantics.

## 2. Frozen V4 properties relevant to Route 1

The exact frozen service authority remains:

- candidate SHA
  `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`;
- service root `/opt/quant`;
- state view `/opt/quant/var`;
- future qualifying durable state root `/var/lib/quant-p0`;
- `WorkingDirectory=/opt/quant`;
- qualifying supervisor launch:
  `/usr/bin/python3 -I /opt/quant/deploy/quant_sec_supervisor.py --root /opt/quant --qualifying`;
- no loaded drop-ins are admissible;
- successful configured `sec-serve` uses the production SEC HTTP transport and
  can attempt a real HTTPS request when a poll is due.

Consequently:
- changing ExecStart, WorkingDirectory, `--root`, the unit, or adding a drop-in
  is not Route 1;
- removing requester identity blocks the successful service path and is not a
  substitute for an offline destructive lifecycle campaign;
- fake-transport constructor injection is a repository-test mechanism, not the
  frozen production service path;
- sanitization must be reservoir separation, not deletion or rewriting of
  lifecycle/authority journals.

## 3. Existing target-host evidence reused read-only

A prior target-host read-only checkpoint exists at:

`operator/gate-b-read-only-preflight-2026-09-21@44285788fce3d5d048b037dd8d1089e1f08f43e9`

Its public checkpoint binds the restricted snapshot by:

`RESTRICTED_SNAPSHOT_CANONICAL_SHA256 = sha256:77bfe820fa981ca3dfa70ba74d11bdb03aad6595b5752c72cd6510817e487d6b`

and reports a snapshot time of:

`2026-09-21T08:13:50Z`.

Relevant public facts from that read-only host inspection:

- loaded `quant-sec-capture.service` fragment bytes matched the frozen V4 unit;
- no drop-ins were loaded;
- the service was not running: public state was `failed`, enablement
  `disabled`;
- the fixed service view was read-only;
- the fixed service view still pointed to rejected V3
  `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`;
- the exact V4 release path was absent at that snapshot;
- the writable service state view and durable state root resolved to the same
  filesystem identity;
- no authorized restricted evidence root was yet bound;
- no real network request was made by that preflight.

These facts are sufficient to show that the host already uses external topology
to make code read-only while exposing a writable state view. They are not
sufficient to prove that the state view can be safely rebound to a dedicated
synthetic reservoir under the existing mount/fstab/systemd-mount topology.

## 4. Route-1 property A — external real-SEC egress impossibility

Required property:

The exact frozen V4 service must be able to run far enough to exercise child and
supervisor lifecycle behavior while a host-external control makes real SEC HTTPS
egress impossible.

### What is established

Frozen V4 itself does not provide an admissible offline selector.

The service's production transport uses HTTPS. Therefore a host firewall boundary
could in principle satisfy Route 1 without altering the loaded unit or V4 code,
provided the boundary is proved effective for every address family/path available
to the service and the effective service environment contains no alternate proxy
path.

### What is NOT proved on the target host

No admissible current target-host evidence available to this mission proves all
of the following:

1. which of `nftables`, `iptables`, `ip6tables`, UFW, or another host
   firewall authority is installed and authoritative;
2. the current ruleset and backend actually controlling outbound traffic;
3. an externally enforceable deny rule can cover both IPv4 and IPv6 for the
   frozen service path without modifying the systemd unit or adding a drop-in;
4. the deny can make NEW outbound SEC HTTPS impossible while preserving the
   operator/control channel needed to observe and stop the campaign;
5. the effective service network path contains no alternate proxy/tunnel route
   that bypasses that deny;
6. the pre/post firewall state can be captured in restricted evidence and bound
   to the exact Gate-B run ID.

Therefore:

`ROUTE1_NETWORK_IMPOSSIBILITY_PROOF = MISSING`

A generic statement that Linux supports firewalls is not target-host proof.

## 5. Route-1 property B — dedicated synthetic state reservoir

Required property:

All destructive-campaign writes visible as `/opt/quant/var` must land only in a
dedicated synthetic reservoir, while the future qualifying reservoir remains
untouched and all synthetic lifecycle provenance remains retained.

### What is established

The public preflight proves:
- `/opt/quant` is a read-only service view;
- the service nevertheless has a writable state view;
- that state view and the durable state root share a filesystem identity.

This makes an external reservoir-selection mechanism plausible without changing
ExecStart or `--root`.

### What is NOT proved on the target host

No admissible current evidence available to this mission proves all of the
following:

1. the exact `findmnt` source, target, fsroot, filesystem and mount options for
   `/opt/quant`, `/opt/quant/var`, and `/var/lib/quant-p0`;
2. whether `/opt/quant/var` is presently a bind mount, a nested filesystem
   mount, or another mechanism;
3. the exact `/etc/fstab`, systemd mount-unit, generator, or boot dependency
   responsible for restoring that view;
4. that an activated synthetic source can be mounted/bound at the exact
   `/opt/quant/var` path while leaving the frozen V4 release view unchanged;
5. that the preserved future qualifying reservoir can be made non-service-
   writable for the whole destructive campaign;
6. that the service can be proven stopped before both the synthetic bind and the
   later qualifying-reservoir rebind;
7. that the synthetic reservoir can be retained immutably/restricted after the
   campaign rather than cleaned in place;
8. that the transition can be represented as a finite sealed mutation allowlist
   with before/after filesystem identities and no hidden path substitution.

Therefore:

`ROUTE1_SYNTHETIC_RESERVOIR_BINDING_PROOF = MISSING`

## 6. Exact read-only evidence needed to promote Route 1

Before Blue may classify Route 1 as provably feasible, a target-host read-only
inspection must capture restricted evidence for at least:

### Firewall/network authority

- command/tool availability and versions for the actual firewall stack;
- authoritative IPv4 and IPv6 ruleset/backend identity;
- network namespace identity for the service path;
- effective service proxy/environment-file network identity without publishing
  secrets;
- resolver/TLS identity;
- a reviewed deny design that covers every production HTTPS path used by frozen
  V4 and does not require a unit/drop-in/ExecStart change;
- exact precondition and rollback evidence commands for that deny.

No deny rule is to be installed during feasibility inspection.

### Mount/state authority

- `findmnt`/equivalent identity for `/opt/quant`,
  `/opt/quant/var`, `/var/lib/quant-p0`, and the release path;
- filesystem device/UUID or other opaque filesystem identity sufficient to bind
  the source;
- relevant `fstab`, systemd mount-unit and ordering/dependency information;
- proof that the service-visible path can remain exactly
  `/opt/quant/var` while an external synthetic source is selected;
- proof that the future qualifying reservoir can remain outside the campaign's
  writable service view;
- proof that service stop can be checked before each reservoir transition.

No mount operation, reservoir creation, or service lifecycle action is to be
performed during that feasibility inspection.

## 7. Sealed activation shape if Route 1 is later proved

If the missing read-only evidence proves the required host capabilities, the
future Blue activation should seal a finite operation allowlist with this logical
ordering:

1. verify exact V4 release/materialization and exact loaded V4 unit;
2. verify service stopped and no MainPID;
3. bind/capture preserved qualifying-reservoir identity before any destructive
   operation;
4. create/select a unique synthetic reservoir under the activated run ID;
5. expose only that synthetic reservoir at the existing service-visible
   `/opt/quant/var` path;
6. verify mount/source identity before service start;
7. install the predeclared external egress-denial boundary and verify both IPv4
   and IPv6 effective state;
8. materialize/consume only synthetic Gate-B authority in the synthetic
   reservoir;
9. execute the destructive lifecycle campaign;
10. stop the service and verify no surviving service process;
11. preserve/hash the synthetic reservoir and lifecycle evidence;
12. remove the egress-denial boundary according to the sealed rollback;
13. detach the synthetic service-view binding;
14. rebind/select the preserved future qualifying reservoir;
15. verify exact qualifying-reservoir identity and inventory;
16. recheck no stale one-use authority, ambiguous lifecycle rows or integrity
   latch in the future qualifying reservoir;
17. rebind exact SHA/tree/input-tree/fingerprint/unit/runtime/mount identities;
18. seal the final Gate-B evidence chain and return to Blue.

This sequence is descriptive only. It is NOT authorized by this handoff.

## 8. Route 2 decision

`ROUTE2_PRODUCTION_TESTABILITY_WORK_REQUIRED = NOT_YET_PROVEN_REQUIRED`

Reason:

The current evidence does not prove that Route 1 is impossible. It proves only
that Route 1 has not yet been demonstrated on the actual host. The host already
shows an externally managed read-only code view plus writable state view, which
is compatible with the Route-1 architecture in principle.

Route 2 production testability work becomes required if the dedicated read-only
host inspection proves any of the following:

- no authoritative firewall mechanism can make the frozen service's real SEC
  HTTPS egress externally impossible without changing service semantics;
- the state view cannot be rebound to a synthetic reservoir while preserving the
  exact frozen service path;
- the future qualifying reservoir cannot be kept outside the campaign's writable
  service view;
- mount/firewall transitions cannot be represented as a sealed, auditable and
  reversible allowlist with service stopped before every reservoir transition.

Until one of those negatives is proved, Blue should not refreeze V4 solely on
the basis of this feasibility gap.

## 9. Final classification

```text
ASTRA_FINDING = F5
ROUTE = 1
F5_ROUTE1_FEASIBILITY = NOT_PROVEN
ROUTE1_NETWORK_IMPOSSIBILITY_PROOF = MISSING
ROUTE1_SYNTHETIC_RESERVOIR_BINDING_PROOF = MISSING
ROUTE2_PRODUCTION_TESTABILITY_WORK_REQUIRED = NOT_YET_PROVEN_REQUIRED
TARGET_HOST_MUTATION_PERFORMED = FALSE
REAL_SEC_NETWORK_REQUESTS_MADE_BY_THIS_MISSION = 0
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
RETURN_CONTROL_TO = BLUE
```
