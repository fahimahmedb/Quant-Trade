# OPERATOR — GATE-B TARGET-HOST READ-ONLY REBIND — 2026-09-21 (FINAL)

ROLE:
TARGET-HOST OPERATOR / READ-ONLY BINDING AUTHORITY

REPOSITORY:
fahimahmedb/Quant-Trade

BRANCH:
operator/gate-b-target-host-read-only-rebind-2026-09-21

MISSION START HEAD:
`b5301bb53dc9e77b534050679eb7a3a8dd12bfdc`

PRIOR ACCESS-BLOCKED CHECKPOINT:
`9a53ed9ee8d2f0582753721bf6cf7b5d6d9e113e`

The prior blocked checkpoint is preserved in Git history. It established only that
the first cloud execution environment lacked target-host access.

The owner then connected by SSH to the actual target host and executed the mission's
read-only R1-R9 observations directly on that machine. The live host transcript was
supplied to Blue. No target-host mutation was performed.

## 0. Repository authority

Post-Astra convergence:

`blue/gate-b-post-astra-convergence-2026-09-21@c14f28466cf7aeaddfe265a8b8aaf77fd301d4d3`

Exact-head CI:

`35627516386 = COMPLETED / SUCCESS`

Controlling disposition:

`POST_ASTRA_GATE_B_CONVERGENCE = READY_FOR_TARGET_HOST_READ_ONLY_REBIND`

Frozen V4:

`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Expected tree:

`4d15ef6f471213ee6ab56337b555d2906ef9bf16`

## 1. Observation provenance

Observed directly on the actual target host over the owner's SSH session.

Repository context observed on-host:

```text
PWD = /mnt/quant-data/quant/Quant-Trade
BRANCH = operator/gate-b-target-host-read-only-rebind-2026-09-21
CHECKPOINT_HEAD = 9a53ed9ee8d2f0582753721bf6cf7b5d6d9e113e
```

Primary host snapshot UTC:

`2026-09-21T17:48:53+00:00`

A later read-only time-correlation sample reported:

```text
REALTIME_NS = 1790013092592772226
MONOTONIC_NS = 88207782112045
```

## 2. R1 — host / time

Observed:

```text
HOST_OPAQUE_SHA256 =
8880e5f6d980ae94454b13dcdb0b8bb85db989b0b17a36a70b1829243d989ad5

BOOT_ID_SHA256 =
919bed5983f85cbec29e18537bdbe15f8bf35610ce19d77bc43b8bc0df2c8cac

Timezone = Etc/UTC
LocalRTC = no
CanNTP = yes
NTP = yes
NTPSynchronized = yes

OS = Ubuntu 24.04.5 LTS
Kernel = Linux 6.17.0-1020-oracle
Architecture = aarch64
```

The opaque host identity matches the prior target-host comparison anchor.

Classification:

`R1_HOST_TIME = PASS_FOR_RUN_RESERVATION_BINDING`

## 3. R2 — runtime

Observed:

```text
python command = /usr/bin/python3
python realpath = /usr/bin/python3.12
Python = 3.12.3
Implementation = CPython
OpenSSL = OpenSSL 3.0.13 30 Jan 2024
```

Classification:

`R2_RUNTIME = PASS_FOR_RUN_RESERVATION_BINDING`

## 4. R3 — loaded systemd authority

Observed service state/properties:

```text
LoadState = loaded
ActiveState = failed
SubState = failed
MainPID = 0
UnitFileState = disabled

FragmentPath = /etc/systemd/system/quant-sec-capture.service
DropInPaths =

WorkingDirectory = /opt/quant
Restart = on-failure
RestartUSec = 15s
StartLimitIntervalUSec = 10min
StartLimitBurst = 5
KillMode = control-group
KillSignal = 15
TimeoutStopUSec = 30s
EnvironmentFiles = /etc/quant/sec-capture.env
```

Exact byte identity:

```text
LOADED_FRAGMENT_SHA256 =
cfeeb12ac670b5e8f46932db113ba71ed153f389e28da0c3eb41f1c0581b15a9

FROZEN_V4_REPO_UNIT_SHA256 =
cfeeb12ac670b5e8f46932db113ba71ed153f389e28da0c3eb41f1c0581b15a9
```

Network namespace/service isolation properties:

```text
PrivateNetwork = no
NetworkNamespacePath =
JoinsNamespaceOf =
IPAddressAllow =
IPAddressDeny =
```

The loaded service fragment matches the frozen repository unit bytes exactly and
there are no drop-ins.

Classification:

`R3_LOADED_SYSTEMD = PASS_FOR_RUN_RESERVATION_BINDING`

## 5. R4 — mount / service-view / state topology

Observed current service view:

```text
/opt/quant ->
/dev/sda1[/opt/quant-releases/2da079d8ad75c69eb3fc2990c512735cb4bdc02b]
ext4 ro

/opt/quant/var ->
/dev/sdb[/quant-p0-state]
ext4 rw

/var/lib/quant-p0 ->
/dev/sdb[/quant-p0-state]
ext4 rw
```

This is the already-known rejected V3 service view with the preserved durable P0
state attached separately.

Persistent mount authorities are loaded, active and enabled.

Observed unit digests:

```text
opt-quant.mount =
84aaf95463d7d85c3efbbb3f38a11fa6a5e133d0b8f7607e7c4730c2f5ebf16f

opt-quant-var.mount =
a7f083c931b4a507bafda56442fa29523d2911a2fe2ab4e98a73c207e07a7b83

var-lib-quant\x2dp0.mount =
fb37ed643fcb237fcb0c3ec54ee9ceada1e376ee88cc16f39cff47ef68a19875
```

The current V3 code view is not a qualifying V4 runtime. Its continued presence
before activation is the expected preactivation state already covered by the V4
materialization/service-view transition authority.

Classification:

`R4_MOUNT_SERVICE_VIEW = EXPECTED_PREACTIVATION_STATE`

## 6. R5 — frozen V4 source / materialization readiness

Observed from the on-host repository:

```text
SOURCE_CLONE_TOPLEVEL = /mnt/quant-data/quant/Quant-Trade
SOURCE_HAS_FROZEN_V4_OBJECT = true

V4_COMMIT =
4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072

V4_TREE =
4d15ef6f471213ee6ab56337b555d2906ef9bf16

V4_TREE_MATCH = true

EXPECTED_V4_FINAL_PATH = ABSENT_PREACTIVATION
```

The exact V4 object is locally available from the approved repository source and
the final SHA-addressed release path remains absent.

Per the authoritative materialization procedure, absence before a sealed activation
is expected and is not by itself a blocker. No foreign/mismatched V4 final path was
observed.

Classification:

`R5_V4_READINESS = EXPECTED_PREACTIVATION_STATE`

## 7. R6 — current service / writer presence

Observed:

```text
ActiveState = failed
SubState = failed
MainPID = 0

QUANT_SUPERVISOR_PROCESS_COUNT = 0
QUANT_SEC_SERVE_PROCESS_COUNT = 0
```

No qualifying collector/supervisor process was observed running.

Classification:

`R6_CURRENT_SERVICE_STATE = PASS_FOR_RUN_RESERVATION_BINDING`

## 8. R7 — durable-state identity

Observed current state mount:

```text
/dev/sdb[/quant-p0-state] /quant-p0-state ext4 rw,relatime,stripe=256
```

Metadata-only inventory digest:

`sha256:fecf62f341995c41e18cd57b18aefca534afa0e9631dbb4fb039679f0b8088ec`

This matches the prior comparison anchor exactly.

This digest binds metadata state for drift comparison only; it is not interpreted
as semantic P0-state validity proof.

Classification:

`R7_DURABLE_STATE_IDENTITY = PASS_FOR_RUN_RESERVATION_BINDING`

## 9. R8 — network / Route-1 binding

Observed route bindings:

```text
IPV4_ROUTESET_SHA256 =
d5e7fa57f38c7a02c30b5c7476eb270313cf3f179d0461ffc46a01b90dca241d

IPV6_ROUTESET_SHA256 =
ef880734525ac262381ba69b40f2170bd998e682f8a7a94c20267256cccd6e70

IPV4_DEFAULT_ROUTE_PRESENT = true
IPV6_DEFAULT_ROUTE_PRESENT = false
```

Current nft OUTPUT chains:

```text
IPv4 OUTPUT policy = accept
IPv6 OUTPUT policy = accept
```

Current firewall digests:

```text
NFT_RULESET_SHA256 =
e72afb3689f51f5e3fb1cbcb3dd98565e28bd71818c3e198d3c86f55650af9d7

IPTABLES_RULESET_SHA256 =
9ffc79eb41f9fa2913302b675e12623e2411e638ed4329e3f9c5f86090cb4e5a
```

Resolver:

`sha256:70cdb37efe507d7b6e575b27172140323116146cbbb99c687680482117b203da`

This matches the prior resolver comparison anchor.

Service environment file binding:

```text
SERVICE_ENVFILE_SHA256 =
7c11401a46ff1924f8a4cea3fc948960e31f2d833d3bb077d1c5234d6141379a

mode = 600
uid = 0
gid = 0
size = 50
```

No service-specific network namespace or IP allow/deny bypass was observed.

The current OUTPUT policy ACCEPT is not interpreted as a Gate-B failure because
the accepted F5 Route-1 design requires the deny authority to be installed later
under an explicit sealed activation. This read-only rebind proves only that the
current host binding remains compatible with that already-accepted composition.

No real SEC request was made.

Classification:

`R8_NETWORK_ROUTE1_BINDING = PASS_FOR_RUN_RESERVATION_BINDING`

## 10. R9 — evidence retention / resources

Observed resource headroom:

```text
/opt/quant filesystem:
  blocks used ~6%
  inodes used ~2%

/var/lib/quant-p0 filesystem:
  blocks used ~1%
  inodes used ~1%

STATE_SIZE_KB = 4
journald disk usage = 32.1M
```

Qualification parent state:

```text
QUALIFICATION_ROOT_PRESENT = true
dev = 2049
inode = 293551
mode = 755
uid = 0
gid = 0
type = directory
```

Effective journald config digest:

`sha256:c34f00dc108e3898df2b0d008b48c1a8c7a04e2810098bc7c3fda61621f013c6`

The existing qualification parent is not treated as the future run-scoped restricted
evidence root. The run-scoped evidence directory remains a post-seal mutation and
must satisfy the authoritative 0700/root-owned requirements when created.

Classification:

`R9_EVIDENCE_RETENTION_RESOURCES = WARN_RECHECK_AT_SEAL`

The warning is non-blocking for run reservation and exists because exact run-scoped
retention identity does not exist until the separately authorized evidence-root
creation.

## 11. Canonical live-binding digest

The owner-operated transcript was projected into a public-safe canonical JSON
binding containing the R1-R9 identities above.

Canonicalization:

`json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=True).encode()`

Projection schema:

`quant-gate-b-read-only-rebind/v1`

Canonical projection digest:

`sha256:fdeba510c26b1ab3f37f9bd3539d084263faafcacb03a815e849ee1199306f87`

The raw SSH transcript is not committed to the public repository.

## 12. Drift comparison

Compared with the earlier target-host evidence:

- opaque host identity: MATCH;
- OS/kernel/runtime family: MATCH;
- loaded service unit: MATCH;
- resolver digest: MATCH;
- durable-state metadata digest: MATCH;
- service remains non-running;
- V3 fixed code view remains in place;
- final V4 SHA path remains absent;
- exact V4 Git object is available locally;
- persistent mount authorities are now concretely digest-bound;
- Route-1 host feasibility remains applicable.

No unexpected drift requiring a blocker was observed.

## 13. Mutation attestation

```text
TARGET_HOST_MUTATION_PERFORMED = FALSE
SYSTEMD_MUTATION_PERFORMED = FALSE
MOUNT_MUTATION_PERFORMED = FALSE
P0_STATE_MUTATION_PERFORMED = FALSE
RELEASE_MATERIALIZATION_PERFORMED = FALSE
RUN_RESERVATION_PERFORMED = FALSE
ACTIVATION_SEALED = FALSE
ACTIVATION_CONSUMED = FALSE
REAL_SEC_NETWORK_REQUESTS_MADE = 0
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
```

## 14. Final disposition

`TARGET_HOST_READ_ONLY_REBIND = READY_FOR_BLUE_RUN_RESERVATION`

This disposition authorizes no mutation by itself.

It means only that the current live target-host state has been rebound sufficiently
for Blue to perform the next governance/run-authority step: reserve exactly one
Gate-B run, then separately construct/seal/verify the activation before any target-
host mutation.

Gate-B remains NOT_STARTED and t0 remains NOT_DECLARED.

Returning control to Blue.
