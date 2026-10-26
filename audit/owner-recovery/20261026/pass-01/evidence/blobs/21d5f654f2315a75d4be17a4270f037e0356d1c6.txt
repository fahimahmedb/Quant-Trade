# OPERATOR — GATE B F5 ROUTE-1 HOST EVIDENCE CLOSURE — FINAL — 2026-09-21

## 0. Final classification

`F5_ROUTE1_HOST_EVIDENCE = PASS_ROUTE1_FEASIBLE`

`ROUTE2_PRODUCTION_TESTABILITY_WORK_REQUIRED = NOT_YET_PROVEN_REQUIRED`

`RETURN_CONTROL_TO = BLUE`

This is a **feasibility** closure for Astra finding F5. It proves that the
current target-host topology supports a future Blue-sealed Route-1 Gate-B
campaign without changing frozen-V4 production code or the frozen
`quant-sec-capture.service` bytes.

It is NOT Gate-B execution evidence, does NOT authorize mutation, and does NOT
declare Gate B PASS or t0.

```text
TARGET_HOST_MUTATION_PERFORMED = FALSE
FIREWALL_MUTATION_PERFORMED = FALSE
MOUNT_MUTATION_PERFORMED = FALSE
SYSTEMD_LIFECYCLE_MUTATION_PERFORMED = FALSE
RESERVOIR_CREATED_OR_DELETED = FALSE
RELEASE_MATERIALIZATION_PERFORMED = FALSE
P0_STATE_MUTATION_PERFORMED = FALSE
REAL_SEC_NETWORK_REQUESTS_MADE_BY_THIS_MISSION = 0
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
```

## 1. Evidence provenance and limitations

The earlier attempts on this branch correctly remained BLOCKED because their
execution environments were not the qualifying target host.

The owner subsequently executed the required read-only commands directly in an
SSH shell on the actual target host and supplied the resulting transcript to
Blue. No raw restricted host transcript is committed here.

Public safe facts below are taken from that owner-operated target-host read-only
observation and cross-checked against frozen V4 repository bytes at:

`blue/p0-gate-a-v4-frozen-2026-09-20@4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Because the live transcript itself is not a durable Gate-B artifact, every
host-specific fact below MUST be re-observed, hash-bound and preserved in the
restricted evidence root during the later concrete Gate-B activation. This
handoff closes feasibility only.

## 2. Target-host identity

Observed target-host identity was consistent with the prior qualifying host:

- hostname: `quant-p0-targer`;
- Linux Oracle kernel `6.17.0-1020-oracle`;
- architecture: `aarch64`;
- PID 1: systemd;
- `/opt/quant` present;
- `/var/lib/quant-p0` present.

The current service is:

`quant-sec-capture.service`

and is loaded but failed/inactive at the observation point with no MainPID.

## 3. N1 — external network impossibility

### 3.1 Host firewall authority

FACT:

- `nft`, `iptables`, and `ip6tables` are installed;
- iptables v1.8.10 uses the nf_tables backend;
- effective nftables families include both IPv4 and IPv6 filter tables;
- both IPv4 and IPv6 OUTPUT currently have policy ACCEPT;
- IPv6 is enabled;
- the host has no observed global IPv6 default route, only link-local IPv6.

Current ACCEPT policy is not a blocker: Route 1 needs a future sealed deny
mechanism, not a pre-existing deny.

### 3.2 Exact service network binding

FACT from the actual loaded service:

- `PrivateNetwork=no`;
- `NetworkNamespacePath=` empty;
- `JoinsNamespaceOf=` empty;
- `IPAddressAllow=` empty;
- `IPAddressDeny=` empty;
- WorkingDirectory is `/opt/quant`;
- ExecStart is the frozen supervisor through `/usr/bin/python3 -I`;
- no systemd network namespace substitution is configured.

FACT from frozen V4 repository bytes:

- `src/quant/dataplane/sec/transport.py` uses
  `http.client.HTTPSConnection` directly against `www.sec.gov`;
- the production transport is HTTPS/TCP, not QUIC;
- the supervisor whitelists the child ambient environment and deliberately does
  not propagate proxy variables;
- no reviewed frozen service/supervisor path creates or joins a separate network
  namespace.

Therefore frozen V4 traffic cannot bypass the host OUTPUT hook through a
service-specific network namespace or inherited proxy path.

### 3.3 Future-sealable deny design

RECOMMENDATION / future activation design, NOT executed here:

Blue can seal a dedicated nftables `inet` table/OUTPUT hook that denies outbound
TCP port 443 for the finite destructive Gate-B campaign. An `inet` hook covers
both IPv4 and IPv6. Frozen V4's direct HTTPS transport therefore cannot put a
real SEC HTTP request on the wire while that deny is effective.

For the controlled-reboot subtest, the deny must be made reboot-persistent and
fail closed before service start. The preferred Route-1 composition is:

1. a Blue-sealed one-shot systemd egress-guard unit whose exact bytes/digest are
   bound by the activation;
2. a Blue-sealed nft rules file creating the dedicated `inet` deny table;
3. the temporary synthetic state mount authority requires the egress guard;
4. `quant-sec-capture.service` already requires that state mount;
5. therefore a failed guard prevents the required mount and prevents the service
   from starting after reboot.

This preserves the frozen `quant-sec-capture.service` bytes, ExecStart,
WorkingDirectory, interpreter and production code.

Mandatory activation-time pre/post observations include:

```text
systemctl is-active quant-sec-capture.service
systemctl show quant-sec-capture.service -p MainPID -p PrivateNetwork -p NetworkNamespacePath -p JoinsNamespaceOf
nft list ruleset
nft list table inet quant_gate_b
ip -4 route show
ip -6 route show table all
```

The exact mutating nft/systemd commands and their rollback are to be sealed in
the later concrete Blue activation artifact. They are not authorized here.

`N1_EXTERNAL_NETWORK_IMPOSSIBILITY = PROVEN_FEASIBLE`

## 4. N2 — synthetic state reservoir binding

### 4.1 Current actual topology

FACT from target-host read-only observation:

`/opt/quant` is a read-only bind of the currently installed release.

Current writable state views resolve as:

```text
/opt/quant/var     -> /dev/sdb[/quant-p0-state]
/var/lib/quant-p0 -> /dev/sdb[/quant-p0-state]
```

The durable backing filesystem is the `quant_data` ext4 filesystem on
`/dev/sdb`.

The systemd mount chain is explicit:

`var-lib-quant\x2dp0.mount`

binds:

`/mnt/quant-data/quant-p0-state -> /var/lib/quant-p0`

and:

`opt-quant-var.mount`

binds:

`/var/lib/quant-p0 -> /opt/quant/var`

Both mount units are ordered before and required by
`quant-sec-capture.service`.

The release view is separately controlled by `opt-quant.mount`.

### 4.2 Future synthetic-reservoir composition

This topology positively supports an isolated persistent synthetic reservoir
without changing the service-visible path or frozen V4 code.

Preferred future Route-1 composition:

1. stop service and prove MainPID=0;
2. preserve/hash the original mount-unit bytes and current qualifying-reservoir
   filesystem identity;
3. create a persistent synthetic directory/reservoir under the durable
   `/mnt/quant-data` filesystem for the unique Gate-B run;
4. install a Blue-sealed temporary `var-lib-quant\x2dp0.mount` authority with
   the same unit name and same `Where=/var/lib/quant-p0`, but with
   `What=<synthetic-reservoir>`;
5. bind that temporary unit digest into the activation and make it require the
   egress guard from N1;
6. leave `opt-quant-var.mount` service-visible target unchanged, so
   `/opt/quant/var` continues to resolve through `/var/lib/quant-p0`;
7. execute the destructive campaign, including controlled reboot, against only
   the persistent synthetic reservoir;
8. stop service and prove no surviving process;
9. preserve/hash the synthetic reservoir as restricted Gate-B evidence;
10. restore the exact original state-mount authority bytes;
11. rebind the original qualifying reservoir;
12. verify its opaque filesystem identity/inventory before any future qualifying
    launch.

The synthetic reservoir is persistent across controlled reboot, while the future
qualifying reservoir is not the mounted writable service state during the
campaign.

This changes only Blue-sealed target-host infrastructure for the finite Gate-B
campaign. It does not alter frozen V4 production code or the frozen service unit.

Mandatory activation-time pre/post observations include:

```text
findmnt -R -o TARGET,SOURCE,FSROOT,FSTYPE,OPTIONS /opt/quant
findmnt -no TARGET,SOURCE,FSROOT,FSTYPE,OPTIONS /opt/quant/var
findmnt -no TARGET,SOURCE,FSROOT,FSTYPE,OPTIONS /var/lib/quant-p0
systemctl cat opt-quant.mount
systemctl cat opt-quant-var.mount
systemctl cat var-lib-quant\x2dp0.mount
lsblk -f
systemctl show quant-sec-capture.service -p ActiveState -p MainPID
```

`N2_SYNTHETIC_RESERVOIR_BINDING = PROVEN_FEASIBLE`

## 5. Frozen-V4 boundary

Frozen V4 remains:

`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

No V4 production byte needs to change for Route 1.

The current target host still points `/opt/quant` at the rejected historical V3
release. That is NOT a contradiction: Lane A separately specifies the future
authorized V3-to-V4 materialization/transition. No such transition occurred
during this read-only closure.

## 6. What this PASS does not prove

This PASS does not prove:

- that the future nft deny was actually installed;
- zero real SEC traffic during a Gate-B run;
- that the synthetic reservoir was actually selected;
- controlled-reboot behavior;
- final V4 materialization;
- F2/F3/F7 run-authority correctness;
- F6 evidence retention;
- Gate B;
- t0.

Those are future concrete-run evidence domains.

At activation time, Blue must bind exact infrastructure bytes/digests and the
operator must recapture host observations into the restricted hash-addressed
evidence chain. Any mismatch fails closed.

## 7. Final disposition

```text
ASTRA_FINDING = F5
N1_EXTERNAL_NETWORK_IMPOSSIBILITY = PROVEN_FEASIBLE
N2_SYNTHETIC_RESERVOIR_BINDING = PROVEN_FEASIBLE
F5_ROUTE1_HOST_EVIDENCE = PASS_ROUTE1_FEASIBLE
ROUTE2_PRODUCTION_TESTABILITY_WORK_REQUIRED = NOT_YET_PROVEN_REQUIRED
TARGET_HOST_MUTATION_PERFORMED = FALSE
REAL_SEC_NETWORK_REQUESTS_MADE_BY_THIS_MISSION = 0
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
RETURN_CONTROL_TO = BLUE
```
