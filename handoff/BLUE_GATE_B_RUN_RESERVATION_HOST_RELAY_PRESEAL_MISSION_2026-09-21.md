# BLUE — GATE-B RUN RESERVATION / HOST-RELAY PRESEAL MISSION — 2026-09-21

## 0. Mission identity

Repository:

`fahimahmedb/Quant-Trade`

Work ONLY on:

`blue/gate-b-run-reservation-host-relay-preseal-2026-09-21`

Mission base:

`blue/gate-b-f11-final-integration-2026-09-21@4f26c1f015efb8c3530aeba8b3f87a81b0361a3f`

This base is intentional because it contains the accepted final F11/run-authority
implementation bytes.

Latest target-host read-only evidence remains external immutable authority and MUST be
read from its exact refs:

`operator/gate-b-target-host-read-only-rebind-2026-09-21@4a503eed81df6656d6aec856f8440b66c5c39943`

Blue reception:

`blue/master-v2-2026-09-20@68e72392d8ee3db5cd099da43ef6c60a3ad8bd68`

handoff:

`handoff/BLUE_TARGET_HOST_READ_ONLY_REBIND_RECEPTION_2026-09-21.md`

Base-reception exact-head CI:

`35635653668`

## 1. Current rail state

```text
RAIL_A_REPOSITORY_CONVERGENCE = COMPLETE
F11_REPOSITORY_DEFECT = CLOSED
F1_SCHEMA = CLOSED_REPOSITORY_EVIDENCE
F5_ROUTE1_FEASIBILITY = CLOSED
V4_ACTIVATION_PRESTAGE = READY
TARGET_HOST_READ_ONLY_REBIND = READY_FOR_BLUE_RUN_RESERVATION

GATE_B_RUN_RESERVED = FALSE
ACTIVATION_SEALED = FALSE
ACTIVATION_CONSUMED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
```

The historical:

`BLOCKED_NO_TARGET_HOST_ACCESS_FROM_THIS_SESSION`

is superseded by the later live owner-operated SSH evidence and MUST NOT be treated as
the current Rail-A blocker.

## 2. Important execution-model correction

The accepted M1-M3 implementation is NOT a repository-only fictional ledger.

`scripts/quant_gate_b_runctl.py::Registry` requires the authoritative registry path
to resolve OUTSIDE the source checkout.

The accepted Builder handoff explicitly leaves these concrete bindings to Blue:

- actual external registry location;
- receipt root;
- target-host ownership/permissions/persistence;
- target-host grandparent namespace stability;
- concrete activation storage reference.

Therefore:

**an isolated ephemeral cloud container MUST NOT create the real GATE_B_RUN_ID in a
temporary registry.**

Cloud Blue may prepare and verify the reservation inputs and exact host-relay command,
but the authoritative append must occur against the Blue-bound persistent authority
storage on the real target host.

## 3. Transient CI state semantics

Before ANY authority-state mutation, resolve live:

`35635653668`

If:

`status = in_progress | queued | waiting`

then the mission state is only:

`GATE_B_RUN_RESERVATION = WAITING_FOR_EXACT_HEAD_CI`

This is NOT:
- a Gate-B defect;
- a host defect;
- an F11 reopen;
- a terminal blocker.

Do not write a terminal BLOCKED handoff solely because CI is still running.

Recheck later.

If CI resolves:

`COMPLETED / FAILURE`

then stop with:

`GATE_B_RUN_RESERVATION = BLOCKED_BLUE_RECEPTION_EXACT_HEAD_CI_FAILURE`

If CI resolves:

`COMPLETED / SUCCESS`

continue directly. Do NOT repeat target-host R1-R9 observations.

## 4. Frozen candidate / accepted live binding

Frozen V4:

```text
CANDIDATE_SHA =
4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072

GIT_TREE =
4d15ef6f471213ee6ab56337b555d2906ef9bf16

VERIFIED_INPUT_TREE_DIGEST =
sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2
```

Latest live host binding:

```text
TARGET_HOST_OPAQUE_ID =
sha256:8880e5f6d980ae94454b13dcdb0b8bb85db989b0b17a36a70b1829243d989ad5

HOST_BOOT_ID_BINDING =
sha256:919bed5983f85cbec29e18537bdbe15f8bf35610ce19d77bc43b8bc0df2c8cac

READ_ONLY_REBIND_CANONICAL_DIGEST =
sha256:fdeba510c26b1ab3f37f9bd3539d084263faafcacb03a815e849ee1199306f87
```

The service was non-running, frozen V4 object was available in the host repository,
the final V4 release path was absent preactivation, and Route-1 remained feasible.

## 5. Accepted run-authority implementation

Use the implementation from this mission ancestry.

Required file:

`scripts/quant_gate_b_runctl.py`

The mission MUST verify its blob against the accepted F11 final integration object
before preparing any host relay.

Do NOT reimplement Registry semantics.

Use only the accepted public API, including as applicable:

- `Registry(...)`
- `load_registry(...)`
- `validate_registry(...)`
- `set_revocation_epoch(...)`
- `reserve(...)`
- `seal_activation(...)`
- `consume_activation(...)`

This mission does NOT call `consume_activation`.

## 6. Authority-storage candidate

Blue's preferred concrete authority-storage parent is:

`/var/lib/quant-p0-qualification/gate-b-authority`

Candidate paths:

```text
RUN_AUTHORITY_PARENT =
/var/lib/quant-p0-qualification/gate-b-authority

RUN_REGISTRY =
/var/lib/quant-p0-qualification/gate-b-authority/registry.jsonl

RUN_RECEIPT_ROOT =
/var/lib/quant-p0-qualification/gate-b-authority/receipts

ACTIVATION_STORAGE_ROOT =
/var/lib/quant-p0-qualification/gate-b-authority/activations
```

This is a CANDIDATE binding until the host relay confirms all of:

1. `/var/lib/quant-p0-qualification` is still the same observed root-owned persistent
   parent;
2. its device/inode identity has not unexpectedly drifted;
3. no symlink substitution exists in the chosen path;
4. no previously established Gate-B registry exists elsewhere under the approved
   qualification authority that would make this a second history;
5. if `gate-b-authority` already exists, its ownership/mode/content are explainable
   and match one existing authority history;
6. if it does not exist, Blue explicitly authorizes creation as run-authority state,
   not as Gate-B runtime mutation.

Observed parent anchor from the accepted read-only rebind:

```text
/var/lib/quant-p0-qualification
dev = 2049
inode = 293551
uid = 0
gid = 0
mode = 755
```

Do not silently accept a different identity.

## 7. Cloud phase — PREPARE, DO NOT RESERVE

Once the required CI is green, the cloud Blue agent performs only:

### P1 — exact authority verification

Verify live:
- current mission branch/HEAD;
- mission ancestry from exact F11 final integration;
- accepted runctl blob;
- final F11/Astra PASS chain;
- target-host rebind final Operator ref;
- Blue rebind reception ref;
- current authoritative Gate-B governance digests.

### P2 — inspect run-authority semantics

Read the implementation before generating a command.

Determine:
- exact constructor/path requirements;
- whether an existing registry can be loaded safely read-only;
- bootstrap rules;
- revocation epoch handling;
- reserve return fields;
- canonical event digest semantics.

Do not invent a CLI that does not exist.

### P3 — build one HOST RELAY package

Prepare one copy/paste-safe host command/script that:

1. verifies the owner is on the actual target host;
2. verifies exact accepted source checkout/ref/blob;
3. performs a READ-ONLY search/check for an existing authoritative registry/history;
4. verifies the candidate authority parent/grandparent identity;
5. stops before mutation on ambiguity;
6. only if no ambiguity exists, creates the exact Blue-bound authority directories
   with explicit root ownership/restricted mode as required;
7. initializes revocation authority only according to the accepted implementation
   and ONLY if no prior epoch/history exists;
8. calls the accepted `Registry.reserve(...)` exactly once;
9. uses:
   - exact frozen candidate triple;
   - exact target-host opaque ID;
   - exact Blue reception/reference;
   - exact operator identity reference chosen by Blue;
10. prints ONLY the safe reservation result required by Blue:
    - GATE_B_RUN_ID;
    - attempt_number;
    - RUN_RESERVATION_DIGEST;
    - registry head digest;
    - revocation epoch/reference;
    - opaque storage-binding digest/metadata;
11. does NOT seal or consume activation;
12. does NOT touch V4 release, mounts, firewall, systemd, P0 state or SEC network.

The host relay must fail closed on:
- alternate pre-existing registry history;
- path identity ambiguity;
- symlink/path substitution;
- stale/nonmonotonic revocation authority;
- nonterminal conflicting run;
- candidate/host mismatch;
- any runctl blob mismatch.

### P4 — preseal activation template

Before reservation result exists, prepare but DO NOT finalize:
- canonical `quant-gate-b-activation/v1` field map;
- broader Blue activation-envelope field map;
- authoritative governance digests;
- planned mutation capability matrix.

Reservation-derived fields MUST stay placeholders until the owner returns the actual
host reservation output.

## 8. Host relay boundary

The authoritative reservation is performed by the OWNER on the real target host using
the exact cloud-prepared command.

This is allowed to mutate ONLY:

`RUN_AUTHORITY_PARENT`

and its approved registry/receipt/activation-control state.

It MUST NOT mutate:
- `/opt/quant`;
- `/opt/quant-releases`;
- `/var/lib/quant-p0`;
- systemd unit state/config;
- mounts;
- nftables/iptables;
- network;
- SEC requester state;
- production P0 state.

At this point:

`GATE_B = NOT_STARTED`

remains true because no Gate-B runtime mutation has occurred.

## 9. Post-relay Blue phase

After the owner returns the exact reservation output, Blue:

1. verifies the registry event against the accepted implementation;
2. binds the real reservation fields;
3. constructs canonical machine activation v1;
4. computes exact activation digest;
5. constructs broader Blue activation envelope;
6. seals the activation in the registry only after all fields/digests are final;
7. performs final pre-mutation verification;
8. RETURNS TO OWNER / OPERATOR before consumption.

This mission MUST NOT consume activation.

The actual first consumption occurs immediately before the first authorized target-host
Gate-B mutation, after a final host freshness recheck.

## 10. No re-open / no duplication

Do NOT:
- repeat the completed read-only host rebind;
- create another F11/Astra audit;
- redesign the run registry;
- create a second run-authority implementation;
- create a temporary cloud registry and call it authoritative;
- create more than one run reservation;
- reserve a new run just because a cloud session restarted;
- declare Gate-B PASS;
- declare t0.

## 11. Cloud mission exit states

Before host relay:

`GATE_B_RUN_RESERVATION_PRESEAL = READY_FOR_OWNER_HOST_RELAY`

Transient CI:

`GATE_B_RUN_RESERVATION_PRESEAL = WAITING_FOR_EXACT_HEAD_CI`

Concrete defect:

`GATE_B_RUN_RESERVATION_PRESEAL = BLOCKED_<EXACT_REASON>`

After actual reservation is returned and Blue validates it, a later Blue continuation
may state:

`GATE_B_RUN_RESERVATION = RESERVED_READY_FOR_ACTIVATION_SEAL`

No stronger state is allowed before the real append-only registry event exists.

## 12. Economic alignment

```text
ECONOMIC_PROGRESS =
P0 qualification rail is one concrete authority step away from a bounded real Gate-B run.

REMAINING_BLOCKER =
complete exact-head CI, bind persistent run-authority storage, reserve exactly one run
on the actual host authority ledger, then seal/consume activation before runtime mutation.

EXIT_CONDITION =
one real append-only Gate-B reservation exists on the target-host authority storage,
followed by one sealed activation ready for immediate pre-mutation consumption.
```

## 13. Safety state

Until host reservation + later seal/consume occur:

```text
GATE_B_RUN_RESERVED = FALSE
ACTIVATION_SEALED = FALSE
ACTIVATION_CONSUMED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```


## 14. Required cloud output

When the cloud preparation is complete and all required exact-head CI gates are green,
write exactly:

`handoff/BLUE_GATE_B_RUN_RESERVATION_HOST_RELAY_PRESEAL_2026-09-21.md`

That handoff MUST contain:

- exact mission HEAD and CI;
- exact accepted runctl blob;
- exact external host-rebind/Blue-reception refs;
- authority-storage binding proposal and all read-only prerequisites;
- exact copy/paste-safe OWNER HOST RELAY command block;
- exact expected safe output fields;
- preseal machine-activation field map with reservation fields left unfilled;
- broader Blue activation-envelope field map;
- mutation attestation;
- one allowed final state from section 11.

Do NOT add a new production executable or alternate run-authority implementation merely to
make the relay convenient. The relay must call the accepted `Registry` API.

If CI is still transiently running after read-only preparation, do NOT publish a false
terminal blocker. Return:

`GATE_B_RUN_RESERVATION_PRESEAL = WAITING_FOR_EXACT_HEAD_CI`

and preserve all completed analysis for resume.
