# BLUE — GATE B ACTIVATION TEMPLATE — CANDIDATE — 2026-09-21

## Status

`ACTIVATION_TEMPLATE = PREPARED_CANDIDATE`

`GATE_B_MUTATION_AUTHORIZED = FALSE`

This template is the explicit Blue authorization boundary between:
- prepared repository governance; and
- actual target-host mutation.

The existence of a Gate-B contract/runbook is never sufficient authorization.

## 1. Required immutable inputs

Before activation, bind:

```text
ACTIVATION_SCHEMA_VERSION =

BLUE_DECISION_TIMESTAMP_UTC =

CANDIDATE_SHA = 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
GIT_TREE = 4d15ef6f471213ee6ab56337b555d2906ef9bf16
VERIFIED_INPUT_TREE_DIGEST = sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2

AUTHORITATIVE_HYBRID_AMENDMENT_REF =
AUTHORITATIVE_HYBRID_AMENDMENT_DIGEST =

ACTIVATED_GATE_B_CONTRACT_REF =
ACTIVATED_GATE_B_CONTRACT_DIGEST =

ACTIVATED_GATE_B_RUNBOOK_REF =
ACTIVATED_GATE_B_RUNBOOK_DIGEST =

TARGET_HOST_OPAQUE_ID =
EXPECTED_SERVICE_UNIT = quant-sec-capture.service

GATE_B_RUN_ID =
GATE_B_ATTEMPT_NUMBER =

OPERATOR_IDENTITY_REFERENCE =
```

No activation is valid while the hybrid amendment fields are blank.

## 2. Scope of authorization

Blue must enumerate allowed mutation classes explicitly:

```text
ALLOW_RELEASE_MATERIALIZATION = TRUE|FALSE
ALLOW_MOUNT_RECONFIGURATION = TRUE|FALSE
ALLOW_SYNTHETIC_STATE_SETUP = TRUE|FALSE
ALLOW_SYSTEMD_START_STOP = TRUE|FALSE
ALLOW_CHILD_FAULT_INJECTION = TRUE|FALSE
ALLOW_SUPERVISOR_SIGKILL = TRUE|FALSE
ALLOW_CONTROLLED_REBOOT = TRUE|FALSE
ALLOW_MISSING_MOUNT_TEST = TRUE|FALSE
ALLOW_WRITER_LOCK_CONTENTION_TEST = TRUE|FALSE
ALLOW_REAL_SEC_NETWORK = TRUE|FALSE
```

Default for any omitted field:

`FALSE`.

For the destructive/synthetic Gate-B campaign:

`ALLOW_REAL_SEC_NETWORK = FALSE`

unless Blue separately documents why a specific target-host property requires
real network access.

## 3. Mandatory pre-activation evidence

Activation must cite exact refs for:

- V4 repository PASS;
- independent V4 audit PASS;
- independent fault-matrix review PASS;
- hybrid amendment promotion;
- exact lineage binder;
- operator-pack Red Team;
- current target-host preflight snapshot if already available.

No chat-only claim is admissible.

## 4. Expiry / invalidation

Activation is invalidated by:

- candidate SHA/tree/input-tree mismatch;
- contract or runbook digest change;
- target host mismatch;
- boot/environment change that Blue declared activation-critical;
- consumed/reused Gate-B run ID;
- prior terminal FAIL on that run ID;
- hybrid amendment rollback/supersession;
- explicit Blue revocation.

## 5. Seal

Before any target-host mutation:

```text
ACTIVATION_CANONICAL_DIGEST =
ACTIVATION_STORAGE_REFERENCE =
ACTIVATION_SEALED_AT_UTC =
GATE_B_MUTATION_AUTHORIZED = TRUE
```

The operator must verify the digest immediately before the first mutating command.

## 6. Terminal failure

If the run reaches a mandatory FAIL:

```text
GATE_B_RUN_ID =
GATE_B_RUN_STATUS = FAILED_TERMINAL
ACTIVATION_CONSUMED = TRUE
```

The activation may not be reused for a retry.

A retry requires:
- a new Gate-B run ID;
- a new Blue activation artifact;
- explicit disposition on which prior PASS evidence remains reusable.

## 7. Non-authority

This candidate template itself does NOT authorize any mutation.

Current state:

`GATE_B_MUTATION_AUTHORIZED = FALSE`

`GATE_B = NOT_STARTED`

`t0 = NOT_DECLARED`
