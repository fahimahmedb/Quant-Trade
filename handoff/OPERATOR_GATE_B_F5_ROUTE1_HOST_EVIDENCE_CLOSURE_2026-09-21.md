# OPERATOR — GATE B F5 ROUTE-1 HOST EVIDENCE CLOSURE — 2026-09-21

## 0. Final classification

`F5_ROUTE1_HOST_EVIDENCE = BLOCKED_ROUTE1_NOT_PROVEN`

`ROUTE2_PRODUCTION_TESTABILITY_WORK_REQUIRED = NOT_YET_PROVEN_REQUIRED`

`RETURN_CONTROL_TO = BLUE`

This mission was limited to read-only closure of N1 and N2. It does not authorize
Gate-B mutation, does not execute the destructive lifecycle campaign, does not
declare Gate B PASS, and does not declare t0.

```text
TARGET_HOST_MUTATION_PERFORMED = FALSE
FIREWALL_MUTATION_PERFORMED = FALSE
MOUNT_MUTATION_PERFORMED = FALSE
SYSTEMD_LIFECYCLE_MUTATION_PERFORMED = FALSE
RESERVOIR_CREATED_OR_DELETED = FALSE
RELEASE_MATERIALIZATION_PERFORMED = FALSE
P0_STATE_MUTATION_PERFORMED = FALSE
REAL_SEC_NETWORK_REQUESTS_MADE_BY_THIS_MISSION = 0
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
```

## 1. Mission identity

Mission branch:

`operator/gate-b-f5-route1-host-evidence-closure-2026-09-21`

Verified remote starting HEAD:

`6c9706b9d18f59a6d27a34ca2db230392ec5ba3f`

The mission file embedded in the branch still names an older expected starting
HEAD, `f0c4e25300e8ad0536461f3ed5136d5e215c12c3`. The branch ref itself resolved
exactly to the user-specified `6c9706b9...`, so the current remote ref was used
as the operational starting authority.

Read:
- `QUANT_NORTH_STAR.md`;
- `governance/BLUE_GATE_B_F5_ROUTE1_HOST_EVIDENCE_CLOSURE_2026-09-21.md`;
- `handoff/OPERATOR_GATE_B_F5_ROUTE1_HOST_EVIDENCE_CLOSURE_MISSION_2026-09-21.md`;
- prior F5 handoff at
  `a5493f052c458e1bbf76e00cbc4943dca8632e71`;
- `governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md`;
- `governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md`.

## 2. Execution boundary

The Blue evidence-closure specification requires N1 and N2 to be established
from the actual target host.

This mission was resumed from durable branch HEAD
`ec44c85b919570e70a0d562905b35e226260c93f` specifically to perform the
previously missing host observations.

A read-only execution-environment identity preflight was performed before any N1
or N2 interpretation. The command environment exposed to this operator did not
match the previously bound target-host runtime identity: OS/architecture/runtime
identity differed, PID 1 was not the target systemd service manager, and the
expected Quant target paths were absent.

Restricted raw identity output was not committed. Its canonical local digest for
this resume attempt is:

`RESUME_EXECUTION_ENVIRONMENT_IDENTITY_SHA256 = sha256:4258783b85d4d151623a181a13dd290132602007826bee9cc74599e9784ee5ec`

Therefore:

`EXECUTION_ENVIRONMENT_MATCHES_TARGET_HOST = FALSE`

No firewall or mount observation from that non-target execution environment is
admissible as target-host N1/N2 evidence.

The durable public host evidence already available from the prior operator
preflight establishes useful baseline facts, including:
- the loaded service fragment matched frozen V4 and had no drop-ins;
- the service was not running at the recorded snapshot;
- `/opt/quant` was a read-only service view;
- the writable service state view and durable state root resolved to the same
  filesystem identity.

However, the prior restricted raw snapshot was intentionally not committed, and
the public checkpoint does not contain the exact current firewall ruleset or the
exact current mount/fstab/systemd-mount topology required to close N1/N2.

Therefore this mission cannot promote assumptions about generic Linux capability
into target-host proof.

## 3. N1 — external network impossibility

Required question:

Can every frozen-V4 real SEC HTTPS path later be made externally impossible,
covering IPv4 and IPv6, without changing:
- loaded unit bytes;
- ExecStart;
- WorkingDirectory;
- frozen V4 code;
- interpreter/runtime binding?

### Existing evidence

Frozen V4 itself has no admissible production offline selector, so Route 1
depends on a host-external network enforcement mechanism.

The prior F5 feasibility handoff correctly left N1 open because no current
target-host evidence was bound for:
- authoritative firewall implementation/backend;
- IPv4 OUTPUT/egress policy;
- IPv6 OUTPUT/egress policy;
- service/network namespace path;
- alternate proxy/tunnel bypass;
- finite future allowlist and rollback evidence.

### Closure result

The resumed mission attempted to begin actual-host read-only observation only
after the execution-environment identity check. Because that check proved the
available command environment was not the qualifying target host, firewall
inspection was stopped before interpreting any local ruleset as target-host
evidence.

No new admissible actual-target-host firewall evidence was collected.

The following mandatory facts remain unproved:
1. authoritative firewall stack actually controlling target-host egress;
2. current IPv4 and IPv6 ruleset/backend identity;
3. whether the frozen service shares the host network namespace or another path
   relevant to enforcement;
4. whether any proxy/tunnel path can bypass the proposed deny boundary;
5. whether a later deny can be represented as a finite, reversible allowlist
   without altering V4 service semantics;
6. exact pre/post read-only evidence commands and expected bindings.

`N1_EXTERNAL_NETWORK_IMPOSSIBILITY = NOT_PROVEN`

This is a missing-proof result, not a hard negative.

## 4. N2 — synthetic state reservoir binding

Required question:

Can `/opt/quant/var` later be rebound to a unique synthetic reservoir while:
- keeping the exact service-visible path;
- preserving the future qualifying reservoir untouched;
- leaving the frozen release/service binding unchanged;
- proving service stopped before each reservoir transition;
- binding source/destination by auditable filesystem identity;
- supporting reversible rebind to the future qualifying reservoir?

### Existing evidence

The prior public host preflight establishes:
- `/opt/quant` was externally presented as read-only;
- the service had a writable state view;
- the writable state view and durable state root shared a filesystem identity.

Those facts make an external reservoir-selection mechanism architecturally
plausible.

They do not establish the current exact topology required by the Blue closure
specification.

### Closure result

For the same reason, local mount/fstab/systemd-mount inspection was not treated as
target-host evidence after the execution-environment identity mismatch was
established.

No new admissible actual-target-host mount evidence was collected.

The following mandatory facts remain unproved:
1. exact current `findmnt` source/target/fsroot/options for
   `/opt/quant`, `/opt/quant/var`, and `/var/lib/quant-p0`;
2. filesystem/device/UUID or equivalent opaque source identities;
3. relevant `/etc/fstab`, systemd mount-unit/generator and ordering topology;
4. whether `/opt/quant/var` is a bind mount, nested mount or another mechanism;
5. whether a unique synthetic source can later replace only the writable state
   view while keeping `/opt/quant/var` unchanged;
6. whether the future qualifying reservoir can remain outside the campaign's
   writable service view for the entire destructive campaign;
7. whether the service-stopped precondition can be independently proved before
   both synthetic selection and qualifying-reservoir restoration;
8. whether the transition/rollback can be sealed as a finite auditable mutation
   allowlist.

`N2_SYNTHETIC_RESERVOIR_BINDING = NOT_PROVEN`

This is also a missing-proof result, not a hard negative.

## 5. Exact evidence still required

A future target-host read-only closure can promote Route 1 only after preserving
restricted evidence for both groups below.

### N1 evidence set

At minimum:
- tool/backend identity for `nftables`, `iptables`/`ip6tables`, UFW or other
  authoritative firewall stack;
- complete effective IPv4 and IPv6 output/egress policy relevant to the service;
- network namespace identity and relevant route/path identity;
- non-secret effective proxy/environment identity;
- a reviewed future deny design that cannot be bypassed by the frozen service;
- exact read-only commands used to prove pre/post state.

No firewall rule should be installed during evidence closure.

### N2 evidence set

At minimum:
- `findmnt`/equivalent topology and opaque filesystem identity for the release,
  `/opt/quant`, `/opt/quant/var`, and `/var/lib/quant-p0`;
- relevant fstab/systemd mount definitions and dependency ordering;
- proof that the exact service-visible writable path can accept an external
  synthetic source without changing V4 service semantics;
- proof that the future qualifying reservoir can be excluded from the campaign's
  writable view;
- proof that service-stop state is observable before each transition;
- exact read-only commands used to bind all of those facts.

No mount, remount, unmount, reservoir creation or service lifecycle operation
should be performed during evidence closure.

## 6. Route 2 classification

`ROUTE2_PRODUCTION_TESTABILITY_WORK_REQUIRED = NOT_YET_PROVEN_REQUIRED`

Reason:

Neither N1 nor N2 produced a hard negative. The resumed operator attempt also
proved that the command environment available to this mission did not match the
qualifying target host, so its local firewall/mount state cannot close N1/N2.

The blocker remains absence of current, admissible actual-target-host evidence,
not proof that the host lacks the required capability.

Route 2 becomes mandatory only if a completed target-host read-only inspection
shows that either:
- all frozen-V4 SEC egress cannot be externally denied across every effective
  IPv4/IPv6 path without changing service semantics; or
- the writable state view cannot be rebound to an isolated synthetic reservoir
  while preserving the exact service-visible path and future qualifying
  reservoir.

No such negative was established here.

## 7. Final status

```text
ASTRA_FINDING = F5
N1_EXTERNAL_NETWORK_IMPOSSIBILITY = NOT_PROVEN
N2_SYNTHETIC_RESERVOIR_BINDING = NOT_PROVEN
F5_ROUTE1_HOST_EVIDENCE = BLOCKED_ROUTE1_NOT_PROVEN
ROUTE2_PRODUCTION_TESTABILITY_WORK_REQUIRED = NOT_YET_PROVEN_REQUIRED
TARGET_HOST_MUTATION_PERFORMED = FALSE
REAL_SEC_NETWORK_REQUESTS_MADE_BY_THIS_MISSION = 0
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
RETURN_CONTROL_TO = BLUE
```
