# BLUE — GATE-B ACTIVATION SEAL / HOST-RELAY MISSION — 2026-09-21

## 0. Mission identity

Repository:

`fahimahmedb/Quant-Trade`

Work ONLY on:

`blue/gate-b-activation-seal-host-relay-2026-09-21`

Mission base:

`blue/gate-b-run-reservation-host-relay-preseal-2026-09-21@5ea73f3ff3b29242c56073ca2cf4e7bde645c143`

DO NOT CREATE ANOTHER BRANCH.

This mission begins AFTER the one real append-only Gate-B reservation already exists.

## 1. Exact reserved run authority

The ONLY current Gate-B run is:

```text
GATE_B_RUN_ID =
gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811

GATE_B_ATTEMPT_NUMBER = 1

RUN_RESERVATION_DIGEST =
sha256:97dac3e09e453dae189111c6f6d014aa2b426dea532bae6ae51de016c37ed8bc

REGISTRY_HEAD_DIGEST =
sha256:97dac3e09e453dae189111c6f6d014aa2b426dea532bae6ae51de016c37ed8bc

REVOCATION_EPOCH = 1

REVOCATION_REFERENCE =
gate-b-host-relay-preseal-2026-09-21-initial-epoch

REVOCATION_EPOCH_EVENT_DIGEST =
sha256:d290d2d07da56bbdf5dbae7243b595da682a5970c7a6a075c538f55b510fb1c8
```

Authority storage:

```text
/var/lib/quant-p0-qualification/gate-b-authority
device = 2049
inode = 294019
mode = 0700
```

NO second run may be reserved.

A cloud restart, documentation commit, CI rerun or activation-preparation failure does
NOT authorize a second reservation.

## 2. Frozen production and target-host binding

```text
CANDIDATE_SHA =
4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072

GIT_TREE =
4d15ef6f471213ee6ab56337b555d2906ef9bf16

VERIFIED_INPUT_TREE_DIGEST =
sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2

TARGET_HOST_OPAQUE_ID =
sha256:8880e5f6d980ae94454b13dcdb0b8bb85db989b0b17a36a70b1829243d989ad5

HOST_BOOT_ID_BINDING =
sha256:919bed5983f85cbec29e18537bdbe15f8bf35610ce19d77bc43b8bc0df2c8cac

READ_ONLY_REBIND_CANONICAL_DIGEST =
sha256:fdeba510c26b1ab3f37f9bd3539d084263faafcacb03a815e849ee1199306f87
```

Accepted executable authority checkout / runctl:

```text
EXECUTABLE_AUTHORITY_HEAD =
e117ddda2b20669f98419761e09490f30885d59e

EXECUTABLE_AUTHORITY_CI =
35637245376 = COMPLETED / SUCCESS

RUNCTL_BLOB_SHA1 =
e9b5a137aee98ec269a1fd8cf5171b9fd99df927
```

## 3. Mission purpose

This is a bounded:

`CLOUD ACTIVATION CONSTRUCTION + OWNER HOST SEAL RELAY`

The mission must:

1. verify the complete accepted Gate-B authority chain;
2. compute exact canonical byte digests for every governance object the activation
   envelope binds;
3. construct the exact machine-activation template for the reserved run;
4. construct the broader Blue activation envelope;
5. generate ONE copy/paste-safe owner host relay that:
   - re-verifies registry/host/run authority;
   - creates the final machine activation bytes;
   - stores the machine activation under the approved activation root;
   - stores the broader Blue envelope under the approved activation root;
   - appends exactly one `ACTIVATION_SEALED` event using the accepted
     `Registry.seal_activation(...)`;
   - prints only safe sealed-activation outputs;
6. STOP.

This mission MUST NOT consume the activation.

## 4. Activation validity policy

Blue chooses for this concrete manual owner-relay run:

`ACTIVATION_VALIDITY_WINDOW = 4 HOURS`

At the host seal relay:

```text
issued_at_utc    = current authoritative target-host UTC
not_before_utc  = issued_at_utc
expires_at_utc  = issued_at_utc + 4 hours
```

All timestamps must be canonical second-resolution UTC `Z` timestamps accepted by
the runctl implementation.

If the activation expires before consumption:

- DO NOT consume it;
- DO NOT silently extend or edit the bytes;
- terminate/disposition the run under Blue authority;
- a future retry requires a new run according to the append-only authority rules.

## 5. Required repository authorities

Read and digest-verify at minimum:

- `QUANT_NORTH_STAR.md`
- `governance/P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT_2026-09-21.md`
- `governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md`
- `governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md`
- `governance/TARGET_HOST_GATE_B_EVIDENCE_SCHEMA_2026-09-21.json`
- `governance/TARGET_HOST_V4_RELEASE_MATERIALIZATION_2026-09-21.md`
- `governance/P0_T0_PRECOMMIT_TEMPLATE_2026-09-21.md`
- `governance/BLUE_GATE_B_ACTIVATION_TEMPLATE_2026-09-21.md`
- `governance/BLUE_GATE_B_FINAL_ACTIVATION_CONVERGENCE_PACK_2026-09-21.md`
- accepted final F11 Blue reception;
- accepted final Astra F11 PASS;
- target-host Operator rebind;
- Blue target-host rebind reception;
- Blue run-reservation reception.

For activation envelope digest fields, compute SHA-256 over exact repository file bytes.
Do not substitute a Git blob SHA-1 where the field says SHA-256.

## 6. Exact machine activation schema

The machine object must contain EXACTLY the accepted key set:

```text
schema
activation_id
run_id
attempt_number
reservation_digest
candidate_sha
git_tree
verified_input_tree_digest
target_host_opaque_id
issued_at_utc
not_before_utc
expires_at_utc
revocation_epoch
revocation_reference
gate_b_mutation_authorized
```

Fixed values:

```text
schema = quant-gate-b-activation/v1
run_id = gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811
attempt_number = 1
reservation_digest =
sha256:97dac3e09e453dae189111c6f6d014aa2b426dea532bae6ae51de016c37ed8bc
candidate_sha =
4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
git_tree =
4d15ef6f471213ee6ab56337b555d2906ef9bf16
verified_input_tree_digest =
sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2
target_host_opaque_id =
sha256:8880e5f6d980ae94454b13dcdb0b8bb85db989b0b17a36a70b1829243d989ad5
revocation_epoch = 1
revocation_reference =
gate-b-host-relay-preseal-2026-09-21-initial-epoch
gate_b_mutation_authorized = true
```

`activation_id` must be a fresh unique nonempty identifier generated exactly once by
the owner host seal relay.

Canonicalization MUST be exactly:

`json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()`

Machine digest:

`sha256:<SHA256(canonical_machine_bytes)>`

No trailing newline is part of the machine activation digest unless the accepted runctl
implementation explicitly requires one. Follow the implementation exactly.

## 7. Broader Blue activation envelope

The cloud phase must fully define a canonical broader envelope that binds at minimum:

- Blue decision timestamp;
- exact reserved run fields;
- exact machine activation reference/digest;
- exact candidate triple;
- exact target-host opaque identity;
- activation-critical boot binding;
- host read-only rebind digest;
- accepted runtime/systemd/mount/network/resource bindings;
- run-authority storage identity;
- current revocation epoch/reference;
- every authoritative governance file ref + SHA-256 byte digest;
- accepted F11 Builder/Blue/Astra refs;
- evidence-root planned canonical path and creation rule;
- Route-1 network-deny mechanism reference/digest;
- synthetic-reservoir mechanism reference/digest;
- allowed mount source/destination matrix reference/digest;
- exact mutation capability matrix;
- activation storage reference;
- canonical envelope digest;
- sealed-at UTC.

Mutation capability matrix for the later complete Route-1 Gate-B campaign:

```text
ALLOW_EVIDENCE_ROOT_SETUP = TRUE
ALLOW_RELEASE_MATERIALIZATION = TRUE
ALLOW_MOUNT_RECONFIGURATION = TRUE
ALLOW_PERSISTENT_MOUNT_AUTHORITY_UPDATE = TRUE
ALLOW_SYNTHETIC_STATE_SETUP = TRUE
ALLOW_SYSTEMD_START_STOP = TRUE
ALLOW_CHILD_FAULT_INJECTION = TRUE
ALLOW_SUPERVISOR_SIGKILL = TRUE
ALLOW_CONTROLLED_REBOOT = TRUE
ALLOW_MISSING_MOUNT_TEST = TRUE
ALLOW_WRITER_LOCK_CONTENTION_TEST = TRUE

ALLOW_REAL_SEC_NETWORK = FALSE
```

Every omitted capability remains FALSE.

This matrix authorizes nothing before successful one-use activation consumption.

## 8. Host-seal relay mandatory prechecks

Before ANY new authority-storage write, the relay must verify:

1. actual target host opaque identity still matches;
2. activation-critical boot ID still matches
   `919bed5983f85cbec29e18537bdbe15f8bf35610ce19d77bc43b8bc0df2c8cac`;
3. NTP remains synchronized;
4. service remains non-running / MainPID=0;
5. exact executable-authority checkout
   `e117ddda2b20669f98419761e09490f30885d59e`;
6. exact runctl blob
   `e9b5a137aee98ec269a1fd8cf5171b9fd99df927`;
7. qualification parent identity still matches accepted dev/inode;
8. run-authority parent still matches:
   device 2049 / inode 294019 / mode 0700 / no symlink;
9. registry validates under the accepted implementation;
10. exact current registry head equals reservation digest
    `sha256:97dac3e09e453dae189111c6f6d014aa2b426dea532bae6ae51de016c37ed8bc`;
11. exact reserved run fields match;
12. no `ACTIVATION_SEALED`, `ACTIVATION_CONSUMED`, terminal event or unexpected
    revocation-epoch change exists;
13. revocation epoch/reference remains exactly 1 /
    `gate-b-host-relay-preseal-2026-09-21-initial-epoch`.

Any mismatch => STOP before write.

## 9. Host-seal relay write boundary

The owner host relay may write ONLY within:

`/var/lib/quant-p0-qualification/gate-b-authority`

It may:

- write one canonical machine activation file under `activations/`;
- write one canonical broader Blue envelope under `activations/`;
- append exactly one `ACTIVATION_SEALED` event through accepted
  `Registry.seal_activation(...)`.

It MUST NOT:

- call `consume_activation`;
- create Gate-B evidence root;
- materialize V4;
- change mounts;
- change systemd;
- change firewall/network;
- touch `/var/lib/quant-p0`;
- start/stop the service;
- create synthetic reservoir;
- execute destructive tests;
- contact SEC;
- declare Gate-B PASS;
- declare t0.

## 10. Required safe host output

The generated host relay must print at least:

```text
ACTIVATION_ID
MACHINE_ACTIVATION_REFERENCE
MACHINE_ACTIVATION_DIGEST
BLUE_ACTIVATION_ENVELOPE_REFERENCE
BLUE_ACTIVATION_ENVELOPE_DIGEST
ACTIVATION_SEALED_EVENT_DIGEST
REGISTRY_HEAD_DIGEST
ISSUED_AT_UTC
NOT_BEFORE_UTC
EXPIRES_AT_UTC
REVOCATION_EPOCH
REVOCATION_REFERENCE
```

No secret environment content may be printed.

## 11. Required cloud handoff

Write exactly:

`handoff/BLUE_GATE_B_ACTIVATION_SEAL_HOST_RELAY_2026-09-21.md`

It must contain:

- exact mission HEAD + exact-head CI;
- exact reservation authority;
- exact governance byte SHA-256 inventory;
- exact machine activation fixed field map;
- exact broader Blue envelope schema/content map;
- one copy/paste-safe host seal relay block;
- expected safe output fields;
- explicit no-consume boundary;
- one final disposition.

Allowed successful cloud disposition:

`GATE_B_ACTIVATION_SEAL_PREP = READY_FOR_OWNER_HOST_SEAL_RELAY`

Transient CI state:

`GATE_B_ACTIVATION_SEAL_PREP = WAITING_FOR_EXACT_HEAD_CI`

A transient CI state is not a Gate-B defect.

## 12. State before owner host seal

```text
GATE_B_RUN_RESERVED = TRUE
GATE_B_RUN_ID = gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811
GATE_B_ATTEMPT_NUMBER = 1

ACTIVATION_SEALED = FALSE
ACTIVATION_CONSUMED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
```

## 13. Economic alignment

```text
ECONOMIC_PROGRESS =
Rail A now has one durable run identity; the next bounded step is one complete activation
seal, not further architecture or audit.

REMAINING_BLOCKER =
construct and host-seal one activation for the already-reserved run, then perform final
freshness verification and consume exactly once immediately before Gate-B runtime mutation.

EXIT_CONDITION =
one activation is durably sealed against the reserved run and returned to Blue for
pre-consumption verification.
```
