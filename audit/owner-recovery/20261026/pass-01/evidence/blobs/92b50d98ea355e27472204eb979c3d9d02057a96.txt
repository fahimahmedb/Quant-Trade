# BLUE — GATE B FINAL ACTIVATION / CONVERGENCE PACK — 2026-09-21

## 0. Status

`BLUE_GATE_B_FINAL_ACTIVATION_CONVERGENCE_PACK = PREPARED / WAITING_FOR_FINAL_F11_ASTRA_PASS`

`PACK_EXECUTION_MODE = POST_ASTRA_BIND_AND_SEAL`

`GATE_B_MUTATION_AUTHORIZED = FALSE`

`GATE_B = NOT_STARTED`

`t0 = NOT_DECLARED`

This pack is the final Blue convergence surface for turning the already-promoted
Gate-B governance, V4 materialization plan, Route-1 host feasibility and run-authority
mechanisms into one concrete Gate-B activation after the remaining F11 repository
proof is independently closed.

This file is deliberately non-authorizing now.

It MUST NOT be interpreted as a sealed activation merely because all static fields
below are known.

---

## 1. Why this pack exists

Most of the old `*_CANDIDATE` Gate-B operator pack has already been promoted into
authoritative files. The remaining work after a future F11 Astra PASS is therefore
not to redesign Gate B.

The post-Astra task is only to:

1. bind the final independently accepted F11/run-authority object;
2. refresh current host read-only identity;
3. reserve one unique Gate-B run;
4. generate the exact machine activation object consumed by
   `scripts/quant_gate_b_runctl.py`;
5. seal the broader Blue activation envelope and its allowed mutation classes;
6. verify all exact refs/digests;
7. consume the one-use activation immediately before the first authorized Gate-B
   mutation;
8. hand the already-authoritative runbook to the target-host Operator.

No new architecture is required if all bindings match.

---

## 2. Candidate -> authoritative promotion crosswalk

The following historical candidates are already superseded by promoted authorities.

| Historical candidate | Candidate blob | Current authoritative object | Current blob |
| --- | --- | --- | --- |
| Hybrid amendment candidate | `113b0294e5a13965305af90e84e87d9875e504e9` | `governance/P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT_2026-09-21.md` | `4f835b203fd2012d275b561608c21071aa0777e8` |
| Gate-B entrance contract candidate | `163cf87aa19d648a1301e4f3785f865b3ec779c6` | `governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md` | `d8827f219820f194845be585c2d3f4c70e4b266d` |
| Gate-B -> Gate-C runbook candidate | `1aec3c5cfd0340cad88310054f42966d366aaa79` | `governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md` | `4ff96fc2eea625428a3bf972f0b53eb2a205263a` |
| Gate-B activation template candidate | `4158dedb579eb5368d491bea1021d5d008bf39fb` | `governance/BLUE_GATE_B_ACTIVATION_TEMPLATE_2026-09-21.md` | `5bf0c5c7a8ab4c6c163f0e0e400276871a057bcc` |
| Gate-B evidence-schema candidate | `1bcc373c499c99e47bfa2b55866b3379bd20493a` | `governance/TARGET_HOST_GATE_B_EVIDENCE_SCHEMA_2026-09-21.json` | `993279ed89bffd19cec514b84dea7e5b44a15389` |
| V4 materialization candidate | `e3f7c4bdea1e0f73a0e59ae951cad8cc288c270e` | `governance/TARGET_HOST_V4_RELEASE_MATERIALIZATION_2026-09-21.md` | `8a01443b748de946a4ed057e42adc889b4645a12` |
| t0 precommit candidate | `e7f61083b7587e61e31de242c2d2a92d3ad144e5` | `governance/P0_T0_PRECOMMIT_TEMPLATE_2026-09-21.md` | `19db326ce4528f1a7778c21ecce6aa15f2195e03` |

Therefore:

`PROMOTE_OLD_GATE_B_CANDIDATES_AFTER_F11 = FALSE`

They are already promoted. The final activation must bind the authoritative objects
above, never the historical candidate blobs.

---

## 3. Frozen production identity — already fixed

The qualifying production candidate remains:

```text
CANDIDATE_SHA = 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
GIT_TREE = 4d15ef6f471213ee6ab56337b555d2906ef9bf16
VERIFIED_INPUT_TREE_DIGEST = sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2

SELECTED_V4_CI_RUN = 35536353538
V4_CI_ARTIFACT_ID = 10612758620
V4_CI_ARCHIVE_DIGEST = sha256:06c690203d589e389847cd345809480da2b99254fe7fd7f38b82c6bf5d54659a

EXPECTED_RELEASE = /opt/quant-releases/4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
EXPECTED_SERVICE_ROOT = /opt/quant
EXPECTED_STATE_ROOT = /var/lib/quant-p0
EXPECTED_SERVICE = quant-sec-capture.service
```

F11/run-authority repair work does not modify frozen V4 production `src/`.
It is a Gate-B governance/authority mechanism and therefore does not change the
frozen production candidate identity above.

---

## 4. Already-closed/prepared proof domains

### 4.1 Hybrid method

Authoritative:

`governance/P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT_2026-09-21.md`

State:

`P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1`

### 4.2 Gate A V4 repository identity

`GATE_A_V4_REPOSITORY_DISPOSITION = PASS`

Frozen V4:
`blue/p0-gate-a-v4-frozen-2026-09-20@4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Independent V4 audit:
`astra/p0-gate-a-v4-independent-audit-2026-09-20@afe25984b0ddd261fda143d858106c3c71e45149`

### 4.3 F1 evidence-schema false-PASS

Independent result:

`ASTRA_GATE_B_SCHEMA_RECHECK = PASS_REPOSITORY_EVIDENCE`

Authoritative repaired schema blob:

`993279ed89bffd19cec514b84dea7e5b44a15389`

### 4.4 F5 Route-1 host feasibility

Operator closure:

`operator/gate-b-f5-route1-host-evidence-closure-2026-09-21@17d692beaa8013101670c0c0164c9bb204f471d9`

Blue reception:

`F5_ROUTE1_FEASIBILITY = CLOSED`

`F5_ROUTE1_HOST_EVIDENCE = PASS_ROUTE1_FEASIBLE`

Preferred composition remains Route 1:
external network denial + synthetic reservoir selection without changing frozen V4
production bytes.

These capabilities MUST be re-observed and concretely sealed at activation;
feasibility evidence is not live execution evidence.

### 4.5 V4 materialization / activation prestage

Builder:

`builder/gate-b-v4-materialization-activation-prestage-2026-09-21@478735d5924df8bc79777b837e710c9083817512`

Disposition:

`GATE_B_ACTIVATION_PRESTAGE = READY_FOR_BLUE_REVIEW`

Recorded exact-head CI:

`35581739682 = COMPLETED / SUCCESS`

The exact V4 materialization, immutable release verification, V3->V4 fixed
service-view transition, state-preservation rules, evidence-root plan and fail-closed
recovery behavior are already specified.

### 4.6 Operator-pack adversarial review

`governance/BLUE_GATE_B_T0_OPERATOR_PACK_ADVERSARIAL_REVIEW_2026-09-21.md`

Disposition:

`OPERATOR_PACK_RED_TEAM = COMPLETE_FOR_CURRENT_DRAFT`

Its hardenings are already represented in the authoritative contract/runbook/t0
template and later Gate-B repair work.

---

## 5. The only repository-side closure still required before this pack may seal

Current remaining frontier:

`F11 = LOCK_PATH_IDENTITY`

Blue parent-path challenge:

`F11_PARENT_PATH_IDENTITY_CHALLENGE = OPEN`

Current Builder branch:

`builder/gate-b-lock-path-identity-repair-2026-09-21`

Current Builder handoff HEAD at pack creation:

`6ec12cd73de24b4a789d6abe9e292d8b616e3da1`

This pack MUST remain non-authorizing until Blue records all of:

```text
F11_P1 = GREEN
F11_P2 = GREEN
F11_P3 = GREEN

BUILDER_F11_FINAL_HEAD = <exact final sha>
BUILDER_F11_FINAL_CI = COMPLETED / SUCCESS

BLUE_F11_INTEGRATION_HEAD = <exact integrated candidate sha>
BLUE_F11_INTEGRATION_CI = COMPLETED / SUCCESS

ASTRA_F11_FINAL_HEAD = <exact independent review sha>
ASTRA_F11_FINAL_CI = COMPLETED / SUCCESS
ASTRA_F11_VERDICT = PASS_REPOSITORY_EVIDENCE

BLUE_F11_FINAL_RECEPTION_SHA = <exact Blue reception sha>
```

Astra must independently include:
- original public-lock replacement;
- public-lock + anchor coordinated replacement;
- whole-parent-path replacement;
- repeated replacement;
- no-mutation fail-closed semantics;
- ordinary real-process serialization;
- A1-A10 non-regression.

No value above may be guessed or copied from chat.

---

## 6. Post-Astra convergence gate

Immediately after a valid Astra PASS, Blue performs one short convergence review.

Required checks:

1. resolve all exact refs live from GitHub;
2. verify Builder, integration and Astra exact-head CI are actually
   `COMPLETED / SUCCESS`;
3. verify no frozen V4 production byte changed;
4. verify current authoritative Gate-B contract/runbook/schema/template blobs have
   not drifted unexpectedly;
5. verify F1 and F5 remain closed and V4 prestage remains applicable;
6. verify no new repository blocker was raised by Astra;
7. verify current Blue governance still says:
   `GATE_B_MUTATION_AUTHORIZED = FALSE` before sealing;
8. compute the final SHA-256 digests of the exact authoritative governance files
   used by the activation;
9. record a new Blue final convergence SHA.

If any mismatch is unexplained:

`POST_ASTRA_GATE_B_CONVERGENCE = BLOCKED`

and no activation is issued.

If all match:

`POST_ASTRA_GATE_B_CONVERGENCE = READY_TO_RESERVE_RUN`

---

## 7. Activation has two distinct layers

### Layer A — Blue activation envelope

This is the broader governance/operator authority.

It MUST bind at least:

```text
BLUE_ACTIVATION_SCHEMA_VERSION =
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

ACTIVATED_GATE_B_EVIDENCE_SCHEMA_REF =
ACTIVATED_GATE_B_EVIDENCE_SCHEMA_DIGEST =

ACTIVATED_RELEASE_MATERIALIZATION_REF =
ACTIVATED_RELEASE_MATERIALIZATION_DIGEST =

AUTHORITATIVE_T0_PRECOMMIT_TEMPLATE_REF =
AUTHORITATIVE_T0_PRECOMMIT_TEMPLATE_DIGEST =

F11_BLUE_FINAL_RECEPTION_REF =
F11_BLUE_FINAL_RECEPTION_DIGEST =
F11_ASTRA_FINAL_HEAD =
F11_ASTRA_FINAL_CI =

TARGET_HOST_OPAQUE_ID =
HOST_BOOT_ID =
HOST_TIME_AUTHORITY_DIGEST =
HOST_NETWORK_BINDING_DIGEST =
HOST_RESOURCE_BASELINE_DIGEST =
HOST_STATE_ROOT_IDENTITY =
HOST_MOUNT_IDENTITY_DIGEST =
HOST_SYSTEMD_IDENTITY_DIGEST =
EVIDENCE_RETENTION_BINDING_DIGEST =

GATE_B_RUN_ID =
GATE_B_ATTEMPT_NUMBER =
RUN_RESERVATION_DIGEST =

OPERATOR_IDENTITY_REFERENCE =

MACHINE_ACTIVATION_REFERENCE =
MACHINE_ACTIVATION_DIGEST =

ACTIVATION_STORAGE_REFERENCE =
ACTIVATION_CANONICAL_DIGEST =
ACTIVATION_SEALED_AT_UTC =

GATE_B_MUTATION_AUTHORIZED = TRUE
```

All blank fields above are seal-time values. They are intentionally not invented now.

### Layer B — machine activation consumed by M1/M2/M3

The actual object parsed by the accepted run-authority implementation is exactly:

`schema = quant-gate-b-activation/v1`

The canonical JSON object to generate after the run reservation is:

```json
{
  "schema": "quant-gate-b-activation/v1",
  "activation_id": "<fresh-nonempty-id>",
  "run_id": "<exact RUN_RESERVED run_id>",
  "attempt_number": "<exact RUN_RESERVED attempt_number>",
  "reservation_digest": "<exact RUN_RESERVED event_digest>",
  "candidate_sha": "4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072",
  "git_tree": "4d15ef6f471213ee6ab56337b555d2906ef9bf16",
  "verified_input_tree_digest": "sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2",
  "target_host_opaque_id": "<exact current host binding>",
  "issued_at_utc": "<seal-time UTC>",
  "not_before_utc": "<prospective UTC>",
  "expires_at_utc": "<bounded expiry UTC>",
  "revocation_epoch": "<current registry epoch>",
  "revocation_reference": "<exact current revocation authority>",
  "gate_b_mutation_authorized": true
}
```

The JSON MUST be canonicalized using the exact implementation semantics:

`json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()`

and its SHA-256 digest MUST be the exact `MACHINE_ACTIVATION_DIGEST`.

No additional field may be inserted into this machine object because the consumer
rejects schema drift.

---

## 8. Required reserve -> seal -> consume order

### Step 1 — read-only target-host rebind

Before run reservation, refresh and bind without mutation:

- target-host opaque identity;
- UTC/time/NTP state;
- boot ID;
- runtime/interpreter/OpenSSL identity;
- loaded systemd fragment/effective properties;
- exact mount topology;
- state-root identity/inventory;
- current network/firewall authority;
- evidence retention/headroom;
- current service stopped/inactive state required by the prestage;
- V4 source object availability;
- absence/presence of the final V4 release path and exact disposition.

Unexpected drift => STOP before reservation where possible.

### Step 2 — initialize/verify revocation epoch

Use the independently accepted run-authority implementation.

Do not silently reset an existing authority history.

### Step 3 — reserve one run

Reserve exactly one new run against:

```text
candidate_sha = 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
git_tree = 4d15ef6f471213ee6ab56337b555d2906ef9bf16
verified_input_tree_digest = sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2
target_host_opaque_id = <freshly observed>
blue_reference = <exact final Blue convergence/activation authority>
operator_identity_reference = <exact operator reference>
```

The registry creates:
- a unique `GATE_B_RUN_ID`;
- the monotonic `GATE_B_ATTEMPT_NUMBER`;
- the exact `RUN_RESERVATION_DIGEST`.

Do not hand-invent them.

### Step 4 — build machine activation

Use the exact reservation fields and bounded validity window.

### Step 5 — build and seal Blue activation envelope

The envelope binds:
- every current authoritative governance digest;
- final F11 independent PASS;
- current host read-only bindings;
- exact run reservation;
- exact machine activation digest;
- exact mutation capabilities;
- exact storage references.

### Step 6 — seal machine activation into registry

Call the accepted `seal_activation` path.

Reservation mismatch, stale revocation epoch or schema mismatch => STOP.

### Step 7 — final pre-mutation verification

Immediately before the first Gate-B mutation verify:
- Blue envelope canonical digest;
- machine activation canonical digest;
- expiry/not-before;
- same host binding;
- same boot/time critical state;
- exact activated contract/runbook/schema/materialization refs;
- no explicit revocation;
- service state expected by the runbook.

### Step 8 — consume activation exactly once

Use the accepted `consume_activation` mechanism.

Preserve its durable consumption receipt.

Only a successful one-use consumption against the expected run/candidate establishes
the run-authority boundary for the authorized Gate-B mutations.

---

## 9. Planned Gate-B mutation classes after seal

These are PREPARED intended values for the complete Route-1 Gate-B campaign.
They have no effect until written into a final sealed Blue activation envelope.

```text
ALLOW_RELEASE_MATERIALIZATION = TRUE
ALLOW_MOUNT_RECONFIGURATION = TRUE
ALLOW_SYNTHETIC_STATE_SETUP = TRUE
ALLOW_SYSTEMD_START_STOP = TRUE
ALLOW_CHILD_FAULT_INJECTION = TRUE
ALLOW_SUPERVISOR_SIGKILL = TRUE
ALLOW_CONTROLLED_REBOOT = TRUE
ALLOW_MISSING_MOUNT_TEST = TRUE
ALLOW_WRITER_LOCK_CONTENTION_TEST = TRUE

ALLOW_REAL_SEC_NETWORK = FALSE
```

Any additional mutation class is FALSE unless explicitly present in the final sealed
envelope.

Route-1 network denial and synthetic-reservoir switching must be concretely bound
from current target-host observations before execution.

The Operator may not infer permission merely because a step exists in a runbook.

---

## 10. First mutating boundary

The authoritative V4 prestage identifies the run-scoped restricted evidence-root
creation as the first planned Gate-B mutation unless that exact root was separately
pre-provisioned under another sealed authority.

Nothing before the successful activation-consumption boundary may create that root,
materialize V4, alter mounts, alter firewall state, start/stop the service, create a
synthetic reservoir, or mutate P0 state.

`READ_ONLY_PREBIND -> RESERVE/SEAL/CONSUME AUTHORITY -> FIRST AUTHORIZED GATE_B MUTATION`

must remain observable and ordered.

---

## 11. Immediate Operator handoff after successful seal

Once the activation is valid and consumed, the Operator executes the already
authoritative sequence:

1. `governance/TARGET_HOST_V4_RELEASE_MATERIALIZATION_2026-09-21.md`;
2. `governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md`;
3. `governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md`;
4. exact Route-1 network/synthetic-reservoir controls sealed in the activation;
5. Gate-B evidence validation against
   `governance/TARGET_HOST_GATE_B_EVIDENCE_SCHEMA_2026-09-21.json`.

Gate B PASS remains a later Blue decision on actual target-host evidence.

Even a successful activation does NOT imply:

`GATE_B = PASS`

and does NOT declare:

`t0`.

---

## 12. Gate-B completion -> t0 boundary

Only after actual Gate-B execution produces a valid PASS artifact and Blue receives
it may the authoritative:

`governance/P0_T0_PRECOMMIT_TEMPLATE_2026-09-21.md`

become executable for a prospective qualifying launch.

The Gate-B activation itself must never contain or guess a future t0.

---

## 13. Final post-Astra fast path

If the final F11 Astra review returns `PASS_REPOSITORY_EVIDENCE` with no new
blocker, the intended fast path is:

```text
1. Blue verifies exact final F11 Builder/integration/Astra refs + CI.
2. Blue records final F11 reception.
3. Blue checks authoritative Gate-B blobs for drift.
4. Blue performs fresh read-only target-host rebind.
5. Blue reserves unique Gate-B run through accepted Registry.
6. Blue generates canonical quant-gate-b-activation/v1.
7. Blue seals the complete activation envelope + machine activation.
8. Operator verifies and consumes activation exactly once.
9. Operator executes already-authoritative Gate-B runbook.
```

No additional design/prestage mission is required unless one of those checks finds
real drift or a new blocker.

---

## 14. Current blocking matrix

```text
HYBRID_AMENDMENT = AUTHORITATIVE
GATE_A_V4 = PASS
F1_SCHEMA = PASS_REPOSITORY_EVIDENCE
F5_ROUTE1 = PASS_ROUTE1_FEASIBLE
V4_ACTIVATION_PRESTAGE = READY_FOR_BLUE_REVIEW
OPERATOR_PACK_RED_TEAM = COMPLETE

F11_PARENT_PATH_IDENTITY_CHALLENGE = OPEN
FINAL_F11_ASTRA_PASS = MISSING
FINAL_F11_BLUE_RECEPTION = MISSING

BLUE_GATE_B_FINAL_ACTIVATION_CONVERGENCE_PACK = PREPARED
GATE_B_MUTATION_AUTHORIZED = FALSE
TARGET_HOST_READY = FALSE
GATE_B = NOT_STARTED
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```

## 15. Authority boundary

This pack reduces post-Astra work to binding and sealing.

It does not pre-authorize a future PASS.

If Astra returns BLOCKED, or the parent-path challenge remains open, this pack stays
prepared but dormant.

If Astra returns PASS and Blue verifies every exact dependency, this pack is the
intended direct bridge to a concrete Gate-B activation without reopening the
already-completed Gate-B architecture/prestage work.
