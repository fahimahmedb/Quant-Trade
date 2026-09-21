# BLUE — GATE B ACTIVATION PRESEAL — 2026-09-21

## Status

`GATE_B_ACTIVATION_PRESEAL = PREPARED / NON_AUTHORIZING`

`GATE_B_MUTATION_AUTHORIZED = FALSE`

This document fixes all Gate-B activation inputs already knowable before hybrid
promotion. It is NOT the activation artifact.

No target-host mutation is authorized by this file.

## 1. Candidate identity — fixed

`CANDIDATE_SHA = 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

`CANDIDATE_GIT_TREE = 4d15ef6f471213ee6ab56337b555d2906ef9bf16`

`CANDIDATE_VERIFIED_INPUT_TREE_DIGEST = sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2`

`CANDIDATE_SELECTED_CI_RUN = 35536353538`

`CANDIDATE_VERIFICATION_ARTIFACT_ID = 10612758620`

`CANDIDATE_VERIFICATION_ARCHIVE_DIGEST = sha256:06c690203d589e389847cd345809480da2b99254fe7fd7f38b82c6bf5d54659a`

Prepared immutable release path:

`/opt/quant-releases/4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072/`

## 2. Repository proof closure — pending final independent input

Builder restart-burst repair:

`1fa82a75485661bf9bbb3de10b925126397dfec5`

Selected Builder repair CI:

`35549017908`

Required final fields:

```text
ASTRA_RESTART_BURST_FINAL_HEAD =
ASTRA_RESTART_BURST_FINAL_CI =
BLUE_FINAL_FAULT_MATRIX_DISPOSITION_SHA =
```

No activation may proceed while any are blank.

## 3. Hybrid authority — pending promotion

Required future fields:

```text
AUTHORITATIVE_HYBRID_AMENDMENT_REF =
AUTHORITATIVE_HYBRID_AMENDMENT_DIGEST =

AUTHORITATIVE_GATE_B_CONTRACT_REF =
AUTHORITATIVE_GATE_B_CONTRACT_DIGEST =

AUTHORITATIVE_GATE_B_RUNBOOK_REF =
AUTHORITATIVE_GATE_B_RUNBOOK_DIGEST =

AUTHORITATIVE_T0_PRECOMMIT_TEMPLATE_REF =
AUTHORITATIVE_T0_PRECOMMIT_TEMPLATE_DIGEST =

AUTHORITATIVE_GATE_B_EVIDENCE_SCHEMA_REF =
AUTHORITATIVE_GATE_B_EVIDENCE_SCHEMA_DIGEST =

AUTHORITATIVE_RELEASE_MATERIALIZATION_REF =
AUTHORITATIVE_RELEASE_MATERIALIZATION_DIGEST =
```

No candidate-only file may fill an authoritative field.

## 4. Runtime-specific activation fields — deliberately unassigned

These fields must be generated only at actual activation time:

```text
GATE_B_RUN_ID =
GATE_B_ATTEMPT_NUMBER =
ACTIVATION_SEALED_AT_UTC =
ACTIVATION_CANONICAL_DIGEST =
ACTIVATION_STORAGE_REFERENCE =

HOST_BOOT_ID =
HOST_TIME_AUTHORITY_DIGEST =
HOST_NETWORK_BINDING_DIGEST =
HOST_RESOURCE_BASELINE_DIGEST =
HOST_STATE_ROOT_IDENTITY =
```

Do not pre-invent these values.

## 5. Mutation capabilities — default deny

Until the final sealed activation artifact explicitly changes them:

```text
ALLOW_RELEASE_MATERIALIZATION = FALSE
ALLOW_MOUNT_RECONFIGURATION = FALSE
ALLOW_SYNTHETIC_STATE_SETUP = FALSE
ALLOW_SYSTEMD_START_STOP = FALSE
ALLOW_CHILD_FAULT_INJECTION = FALSE
ALLOW_SUPERVISOR_SIGKILL = FALSE
ALLOW_CONTROLLED_REBOOT = FALSE
ALLOW_MISSING_MOUNT_TEST = FALSE
ALLOW_WRITER_LOCK_CONTENTION_TEST = FALSE
ALLOW_REAL_SEC_NETWORK = FALSE
```

Real SEC network remains default-deny for destructive Gate-B tests.

## 6. Activation preconditions

A later sealed activation requires all of:

- hybrid amendment authoritative;
- complete Gate-B authority pack authoritative;
- final repository fault matrix independently closed;
- exact V4 identity unchanged;
- current target-host preflight revalidated;
- unique new `GATE_B_RUN_ID`;
- explicit per-mutation authorization;
- evidence-retention path bound;
- synchronized/attributable host time;
- no stale or consumed prior activation.

## 7. Post-promotion boundary

Hybrid promotion alone must leave:

`GATE_B_MUTATION_AUTHORIZED = FALSE`

A distinct Blue activation decision is required afterward.

## 8. Safety

`TARGET_HOST_READY = FALSE`

`GATE_B = NOT_STARTED`

`t0 = NOT_DECLARED`

`REAL_CAPITAL_AUTHORIZED = FALSE`
