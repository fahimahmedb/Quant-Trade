# BLUE — GATE-B RUN RESERVATION RECEPTION — 2026-09-21

## 0. Received authoritative host reservation

Owner executed the approved host-relay against the actual target host from the
accepted executable authority checkout:

`e117ddda2b20669f98419761e09490f30885d59e`

Accepted runctl blob observed by the relay:

`e9b5a137aee98ec269a1fd8cf5171b9fd99df927`

The relay first verified:

```text
HEAD = e117ddda2b20669f98419761e09490f30885d59e
QUAL_ROOT_DEV = 2049
QUAL_ROOT_INODE = 293551
AUTH_PARENT_ABSENT = true
EXISTING_EVENT_COUNT = 0
```

No alternate Gate-B authority history was reported by the pre-check.

## 1. Revocation authority initialization

Because the authoritative registry was empty, the accepted Registry implementation
initialized the first revocation epoch exactly once:

```text
REVOCATION_EPOCH_INITIALIZED = 1
REVOCATION_EPOCH = 1
REVOCATION_REFERENCE =
gate-b-host-relay-preseal-2026-09-21-initial-epoch

REVOCATION_EPOCH_EVENT_DIGEST =
sha256:d290d2d07da56bbdf5dbae7243b595da682a5970c7a6a075c538f55b510fb1c8
```

No existing epoch/history was reset or overwritten.

## 2. Exact reservation

The accepted append-only registry then created exactly one reservation:

```text
GATE_B_RUN_ID =
gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811

GATE_B_ATTEMPT_NUMBER = 1

RUN_RESERVATION_DIGEST =
sha256:97dac3e09e453dae189111c6f6d014aa2b426dea532bae6ae51de016c37ed8bc

REGISTRY_HEAD_DIGEST =
sha256:97dac3e09e453dae189111c6f6d014aa2b426dea532bae6ae51de016c37ed8bc
```

The reservation binds the already-frozen candidate triple and accepted target-host
opaque identity from the preseal mission.

## 3. Authority storage binding

The created authority storage is:

```text
RUN_AUTHORITY_PARENT =
/var/lib/quant-p0-qualification/gate-b-authority

device = 2049
inode = 294019
mode = 0700
```

This storage is outside the Git source checkout and under the previously rebound
qualification parent.

The relay was constrained to this authority subtree only.

## 4. What was NOT done

```text
ACTIVATION_SEALED = FALSE
ACTIVATION_CONSUMED = FALSE
TARGET_HOST_RUNTIME_MUTATION_PERFORMED = FALSE
V4_RELEASE_MATERIALIZED = FALSE
MOUNTS_CHANGED = FALSE
SYSTEMD_CHANGED = FALSE
FIREWALL_CHANGED = FALSE
P0_STATE_MUTATED = FALSE
REAL_SEC_NETWORK_REQUESTS_MADE = 0
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
```

Creating the append-only authority registry and reservation does not itself start
Gate B.

## 5. Blue reception

`GATE_B_RUN_RESERVATION = RESERVED_READY_FOR_ACTIVATION_SEAL`

This is the one authoritative run reservation for the current attempt.

Blue MUST NOT allocate another run ID while this run is nonterminal merely because
a cloud session restarts or a documentation commit receives a new SHA.

The next step is to construct and seal one activation bound to this exact
reservation, current revocation epoch/reference and accepted host/candidate
identities.

Consumption remains a later, separate target-host boundary immediately before the
first authorized Gate-B runtime mutation.

## 6. Economic alignment

```text
ECONOMIC_PROGRESS =
Rail A now has one concrete durable Gate-B run identity and can proceed to one
bounded activation instead of more design/audit work.

REMAINING_BLOCKER =
construct and seal one complete activation, then perform final host freshness
verification and consume it exactly once before the first Gate-B runtime mutation.

EXIT_CONDITION =
one activation for gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811 is sealed and
verified, ready for immediate one-use consumption by the target-host Operator.
```
