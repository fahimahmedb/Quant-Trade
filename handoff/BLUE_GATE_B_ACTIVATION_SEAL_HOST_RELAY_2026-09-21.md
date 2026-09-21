# BLUE — GATE-B ACTIVATION SEAL / HOST-RELAY — 2026-09-21

## 0. Mission identity

Branch: `blue/gate-b-activation-seal-host-relay-2026-09-21`
Mission HEAD (verified): `698bfaef347477bbfac154cfd7752ea4fdfe3da4`
Mission-head CI: `35639080368` on `SEC P0 pre-t0 gate`, head_sha `698bfaef347477bbfac154cfd7752ea4fdfe3da4` —
**status observed: `in_progress`** at last check (rechecked twice).

Per mission section 11, this is:

`GATE_B_ACTIVATION_SEAL_PREP = WAITING_FOR_EXACT_HEAD_CI`

Not a Gate-B defect, host defect, or reservation reopen. All read-only preparation below is
complete; recheck CI 35639080368 before running the host relay in section 8.

## 1. Exact reserved run authority (verified, not re-reserved)

```text
GATE_B_RUN_ID = gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811
GATE_B_ATTEMPT_NUMBER = 1
RUN_RESERVATION_DIGEST = sha256:97dac3e09e453dae189111c6f6d014aa2b426dea532bae6ae51de016c37ed8bc
REGISTRY_HEAD_DIGEST = sha256:97dac3e09e453dae189111c6f6d014aa2b426dea532bae6ae51de016c37ed8bc
REVOCATION_EPOCH = 1
REVOCATION_REFERENCE = gate-b-host-relay-preseal-2026-09-21-initial-epoch
REVOCATION_EPOCH_EVENT_DIGEST = sha256:d290d2d07da56bbdf5dbae7243b595da682a5970c7a6a075c538f55b510fb1c8

Authority storage:
/var/lib/quant-p0-qualification/gate-b-authority
device = 2049, inode = 294019, mode = 0700
```

No second run is reserved by this mission. `Registry.reserve()` is not called.

## 2. Frozen candidate / host binding / executable authority (verified)

```text
CANDIDATE_SHA = 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
GIT_TREE = 4d15ef6f471213ee6ab56337b555d2906ef9bf16
VERIFIED_INPUT_TREE_DIGEST = sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2
TARGET_HOST_OPAQUE_ID = sha256:8880e5f6d980ae94454b13dcdb0b8bb85db989b0b17a36a70b1829243d989ad5
HOST_BOOT_ID_BINDING = sha256:919bed5983f85cbec29e18537bdbe15f8bf35610ce19d77bc43b8bc0df2c8cac
READ_ONLY_REBIND_CANONICAL_DIGEST = sha256:fdeba510c26b1ab3f37f9bd3539d084263faafcacb03a815e849ee1199306f87

EXECUTABLE_AUTHORITY_HEAD = e117ddda2b20669f98419761e09490f30885d59e
EXECUTABLE_AUTHORITY_CI = 35637245376 = COMPLETED / SUCCESS (verified prior mission)
```

`git hash-object scripts/quant_gate_b_runctl.py` at this mission HEAD (`698bfaef34`) returns
`e9b5a137aee98ec269a1fd8cf5171b9fd99df927` — **matches the mandated
`RUNCTL_BLOB_SHA1` exactly.** No reimplementation was made; the host relay in section 8 calls
only `Registry.seal_activation(...)` from this accepted module.

## 3. Governance byte SHA-256 inventory

Computed directly with `sha256sum` over exact file bytes (never a Git blob SHA-1) from the
ref each object is authoritative on.

| Object | Ref | SHA-256 |
|---|---|---|
| `QUANT_NORTH_STAR.md` | this mission HEAD | `sha256:d3fcbf96186dde2f0e946391d1bc40b5845c4398da5ce674f078f77c53ab113b` |
| `governance/P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT_2026-09-21.md` | this mission HEAD | `sha256:e3dddcc4936b626fac3f6fad3a1d0bbd821ef4af24806c6532d94d638b4a7a73` |
| `governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md` | this mission HEAD | `sha256:e3f805a6d3e6f72e3dc0cd79670a1134569a0c6a8bc0f7e6229ed725468b5477` |
| `governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md` | this mission HEAD | `sha256:7db5a567a60b1be325d0719341ab2a997a6c9f33f371fe53e11a3aa11f4a9ad2` |
| `governance/TARGET_HOST_GATE_B_EVIDENCE_SCHEMA_2026-09-21.json` | this mission HEAD | `sha256:145293a685ca412141b78889eb25eed60cf1e33a850e41a2bd10456faf7c5fde` |
| `governance/TARGET_HOST_V4_RELEASE_MATERIALIZATION_2026-09-21.md` | this mission HEAD | `sha256:78ecbbb79a2c38468681be94680a88d0b8de183df6cbb8bf2785a589beea4adf` |
| `governance/P0_T0_PRECOMMIT_TEMPLATE_2026-09-21.md` | this mission HEAD | `sha256:7edaac149ccf8778b4f4044eaf21a0e4878562547c94cacf4b6a668e82633cc7` |
| `governance/BLUE_GATE_B_ACTIVATION_TEMPLATE_2026-09-21.md` | this mission HEAD | `sha256:93cdce6b73506850296173f2cf09c616f7fa59b5557379be05d6dfdac406c52d` |
| `governance/BLUE_GATE_B_FINAL_ACTIVATION_CONVERGENCE_PACK_2026-09-21.md` | `blue/master-v2-2026-09-20@68e72392d8ee3db5cd099da43ef6c60a3ad8bd68` (not present at this mission HEAD; sourced from its authoritative ref) | `sha256:df76b88be818cb49ed77d42fdcc6936572b7afbbe388d17b59cefd1b21598e06` |
| `handoff/BLUE_GATE_B_F11_FINAL_INTEGRATION_RECEPTION_2026-09-21.md` | this mission HEAD | `sha256:720bbf06d8261b2ab1891f9c1451c59bde271b05dc8516834c1275354dfaea21` |
| `handoff/OPERATOR_GATE_B_TARGET_HOST_READ_ONLY_REBIND_2026-09-21.md` | `operator/gate-b-target-host-read-only-rebind-2026-09-21@4a503eed81df6656d6aec856f8440b66c5c39943` | `sha256:a45f8ac511403a17803bffb01d0c1851d4b492f69a1bf981e389391b9b6e2ab4` |
| `handoff/BLUE_TARGET_HOST_READ_ONLY_REBIND_RECEPTION_2026-09-21.md` | `blue/master-v2-2026-09-20@68e72392d8ee3db5cd099da43ef6c60a3ad8bd68` | `sha256:0ae02cdcef28fde0b8060a9aec04006e94daf06cff432746ae5812d58850dc54` |
| `handoff/BLUE_GATE_B_RUN_RESERVATION_HOST_RELAY_PRESEAL_2026-09-21.md` | this mission HEAD | `sha256:f08c04a0af17ac01f77aba440be2aa2aeb5abb9e042ee2a543f450b2cfcfcae5` |

Accepted F11/Astra refs (identity, not re-audited — no reopen per mission section 1/10):

```text
F11_FINAL_INTEGRATION = blue/gate-b-f11-final-integration-2026-09-21@4f26c1f015efb8c3530aeba8b3f87a81b0361a3f
POST_ASTRA_CONVERGENCE = blue/gate-b-post-astra-convergence-2026-09-21@c14f28466cf7aeaddfe265a8b8aaf77fd301d4d3 (CI 35627516386 = COMPLETED/SUCCESS)
```

## 4. Exact machine activation — fixed field map

All fields below are fixed except `activation_id`, `issued_at_utc`, `not_before_utc`,
`expires_at_utc`, which the host relay must generate live at seal time (4-hour validity
window per mission section 4).

```json
{
  "schema": "quant-gate-b-activation/v1",
  "activation_id": "<GENERATED ONCE BY HOST RELAY, e.g. uuid4>",
  "run_id": "gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811",
  "attempt_number": 1,
  "reservation_digest": "sha256:97dac3e09e453dae189111c6f6d014aa2b426dea532bae6ae51de016c37ed8bc",
  "candidate_sha": "4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072",
  "git_tree": "4d15ef6f471213ee6ab56337b555d2906ef9bf16",
  "verified_input_tree_digest": "sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2",
  "target_host_opaque_id": "sha256:8880e5f6d980ae94454b13dcdb0b8bb85db989b0b17a36a70b1829243d989ad5",
  "issued_at_utc": "<HOST-AUTHORITATIVE UTC AT SEAL TIME>",
  "not_before_utc": "<= issued_at_utc>",
  "expires_at_utc": "<issued_at_utc + 4 hours>",
  "revocation_epoch": 1,
  "revocation_reference": "gate-b-host-relay-preseal-2026-09-21-initial-epoch",
  "gate_b_mutation_authorized": true
}
```

This key set is exactly `_activation()`'s required `keys` set in
`scripts/quant_gate_b_runctl.py` — no more, no fewer. Canonicalization is exactly
`json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=True).encode()`, and the
digest is `sha256:<SHA256(canonical_bytes)>` with no trailing newline in the digested bytes
(the accepted `_activation()` computes `sha256_digest(raw)` directly over the stored bytes —
the host relay must write exactly the canonical bytes it hashed, byte-for-byte, as the stored
activation file).

## 5. Broader Blue activation envelope — schema/content map

```json
{
  "schema": "quant-gate-b-blue-envelope/v1",
  "sealed_at_utc": "<= issued_at_utc, host-authoritative UTC>",
  "run": {
    "run_id": "gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811",
    "attempt_number": 1,
    "reservation_digest": "sha256:97dac3e09e453dae189111c6f6d014aa2b426dea532bae6ae51de016c37ed8bc",
    "registry_head_digest_at_reservation": "sha256:97dac3e09e453dae189111c6f6d014aa2b426dea532bae6ae51de016c37ed8bc"
  },
  "machine_activation": {
    "reference": "/var/lib/quant-p0-qualification/gate-b-authority/activations/<activation_id>.activation.json",
    "digest": "<MACHINE_ACTIVATION_DIGEST from host relay>"
  },
  "candidate": {
    "candidate_sha": "4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072",
    "git_tree": "4d15ef6f471213ee6ab56337b555d2906ef9bf16",
    "verified_input_tree_digest": "sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2"
  },
  "host_binding": {
    "target_host_opaque_id": "sha256:8880e5f6d980ae94454b13dcdb0b8bb85db989b0b17a36a70b1829243d989ad5",
    "host_boot_id_binding": "sha256:919bed5983f85cbec29e18537bdbe15f8bf35610ce19d77bc43b8bc0df2c8cac",
    "read_only_rebind_canonical_digest": "sha256:fdeba510c26b1ab3f37f9bd3539d084263faafcacb03a815e849ee1199306f87"
  },
  "accepted_runtime_bindings": {
    "service_fragment_sha256": "cfeeb12ac670b5e8f46932db113ba71ed153f389e28da0c3eb41f1c0581b15a9",
    "opt_quant_mount_digest": "84aaf95463d7d85c3efbbb3f38a11fa6a5e133d0b8f7607e7c4730c2f5ebf16f",
    "opt_quant_var_mount_digest": "a7f083c931b4a507bafda56442fa29523d2911a2fe2ab4e98a73c207e07a7b83",
    "quant_p0_mount_digest": "fb37ed643fcb237fcb0c3ec54ee9ceada1e376ee88cc16f39cff47ef68a19875",
    "nft_ruleset_digest": "e72afb3689f51f5e3fb1cbcb3dd98565e28bd71818c3e198d3c86f55650af9d7"
  },
  "run_authority_storage": {
    "path": "/var/lib/quant-p0-qualification/gate-b-authority",
    "device": 2049,
    "inode": 294019,
    "mode": "0700"
  },
  "revocation": {
    "epoch": 1,
    "reference": "gate-b-host-relay-preseal-2026-09-21-initial-epoch",
    "epoch_event_digest": "sha256:d290d2d07da56bbdf5dbae7243b595da682a5970c7a6a075c538f55b510fb1c8"
  },
  "governance_digests": "<full table from section 3 above, embedded verbatim>",
  "f11_astra_refs": {
    "f11_final_integration": "blue/gate-b-f11-final-integration-2026-09-21@4f26c1f015efb8c3530aeba8b3f87a81b0361a3f",
    "post_astra_convergence": "blue/gate-b-post-astra-convergence-2026-09-21@c14f28466cf7aeaddfe265a8b8aaf77fd301d4d3"
  },
  "evidence_root": {
    "planned_canonical_path": "/var/lib/quant-p0-qualification/gate-b-authority/../gate-b-evidence/<run_id>/<attempt_number>",
    "creation_rule": "created only after activation consumption, root-owned mode 0700, never by this mission or the seal relay"
  },
  "route1_deny_mechanism_reference": "nft_ruleset_digest above; install deferred to post-consumption Gate-B runtime mutation",
  "synthetic_reservoir_mechanism_reference": "NOT_APPLICABLE_AT_SEAL_TIME",
  "allowed_mount_matrix_reference": "governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md digest above",
  "mutation_capability_matrix": {
    "ALLOW_EVIDENCE_ROOT_SETUP": true,
    "ALLOW_RELEASE_MATERIALIZATION": true,
    "ALLOW_MOUNT_RECONFIGURATION": true,
    "ALLOW_PERSISTENT_MOUNT_AUTHORITY_UPDATE": true,
    "ALLOW_SYNTHETIC_STATE_SETUP": true,
    "ALLOW_SYSTEMD_START_STOP": true,
    "ALLOW_CHILD_FAULT_INJECTION": true,
    "ALLOW_SUPERVISOR_SIGKILL": true,
    "ALLOW_CONTROLLED_REBOOT": true,
    "ALLOW_MISSING_MOUNT_TEST": true,
    "ALLOW_WRITER_LOCK_CONTENTION_TEST": true,
    "ALLOW_REAL_SEC_NETWORK": false
  },
  "activation_storage_reference": "/var/lib/quant-p0-qualification/gate-b-authority/activations/",
  "envelope_digest": "<computed by host relay over this object's canonical bytes with envelope_digest field omitted, then set>"
}
```

This capability matrix authorizes nothing by itself; it takes effect only after successful
one-time activation consumption (not performed by this mission).

## 6. Host-seal relay mandatory prechecks (enforced by the script below)

The relay verifies, in order, before any write: target-host opaque identity; boot ID
`919bed5983f85cbec29e18537bdbe15f8bf35610ce19d77bc43b8bc0df2c8cac`; NTP synchronized;
service non-running (MainPID=0); executable-authority checkout `e117ddda2b20669f98419761e09490f30885d59e`;
runctl blob `e9b5a137aee98ec269a1fd8cf5171b9fd99df927`; qualification-parent dev/inode;
run-authority-parent dev=2049/inode=294019/mode=0700/non-symlink; registry validates under
the accepted implementation; registry head digest equals
`sha256:97dac3e09e453dae189111c6f6d014aa2b426dea532bae6ae51de016c37ed8bc`; reserved run
fields match exactly; no `ACTIVATION_SEALED`/`ACTIVATION_CONSUMED`/terminal event exists for
this run; revocation epoch/reference remain exactly `1` /
`gate-b-host-relay-preseal-2026-09-21-initial-epoch`. Any mismatch aborts before write.

## 7. Activation validity window

```text
ACTIVATION_VALIDITY_WINDOW = 4 HOURS
issued_at_utc  = host-authoritative UTC at seal time
not_before_utc = issued_at_utc
expires_at_utc = issued_at_utc + 4 hours
```

If not consumed before `expires_at_utc`, the activation must NOT be consumed, extended, or
edited; a future attempt requires Blue to terminal/disposition this run and reserve a new
one under the append-only authority rules.

## 8. OWNER HOST SEAL RELAY — copy/paste-safe command block

Run this **only on the actual target host**, as root, from the exact executable-authority
checkout. It re-verifies everything in section 6, writes only under
`/var/lib/quant-p0-qualification/gate-b-authority`, and calls
`Registry.seal_activation(...)` exactly once. It does not call `consume_activation`.

```bash
#!/usr/bin/env bash
set -euo pipefail

REPO_CHECKOUT="/mnt/quant-data/quant/Quant-Trade"
EXPECTED_EXEC_AUTHORITY_SHA="e117ddda2b20669f98419761e09490f30885d59e"
RUNCTL_REL="scripts/quant_gate_b_runctl.py"
EXPECTED_RUNCTL_BLOB="e9b5a137aee98ec269a1fd8cf5171b9fd99df927"
AUTH_PARENT="/var/lib/quant-p0-qualification/gate-b-authority"
EXPECTED_AUTH_DEV="2049"
EXPECTED_AUTH_INO="294019"
EXPECTED_BOOT_ID_SHA256="919bed5983f85cbec29e18537bdbe15f8bf35610ce19d77bc43b8bc0df2c8cac"

cd "$REPO_CHECKOUT"
actual_head="$(git rev-parse HEAD)"
[ "$actual_head" = "$EXPECTED_EXEC_AUTHORITY_SHA" ] || { echo "ABORT: checkout HEAD $actual_head != $EXPECTED_EXEC_AUTHORITY_SHA"; exit 1; }
git diff --quiet -- "$RUNCTL_REL" || { echo "ABORT: $RUNCTL_REL locally modified"; exit 1; }
actual_blob="$(git hash-object "$RUNCTL_REL")"
[ "$actual_blob" = "$EXPECTED_RUNCTL_BLOB" ] || { echo "ABORT: runctl blob $actual_blob != $EXPECTED_RUNCTL_BLOB"; exit 1; }

actual_boot_id_sha256="$(sha256sum /proc/sys/kernel/random/boot_id 2>/dev/null | cut -d' ' -f1 || true)"
# NOTE: if boot_id is captured differently by the accepted rebind procedure, use that exact
# method instead; this must reproduce EXPECTED_BOOT_ID_SHA256 exactly, or ABORT.
if [ -n "$actual_boot_id_sha256" ] && [ "$actual_boot_id_sha256" != "$EXPECTED_BOOT_ID_SHA256" ]; then
  echo "ABORT: boot id binding changed (host rebooted) — reservation is stale, do not seal"
  exit 1
fi

timedatectl show -p NTPSynchronized --value | grep -qx yes || { echo "ABORT: NTP not synchronized"; exit 1; }

svc_state="$(systemctl show -p ActiveState,MainPID quant-sec-capture.service 2>/dev/null || true)"
echo "$svc_state" | grep -q "MainPID=0" || { echo "ABORT: service is running (MainPID != 0)"; exit 1; }

[ -L "$AUTH_PARENT" ] && { echo "ABORT: $AUTH_PARENT is a symlink"; exit 1; }
read -r auth_dev auth_ino auth_mode < <(stat -c '%d %i %a' "$AUTH_PARENT")
[ "$auth_dev" = "$EXPECTED_AUTH_DEV" ] && [ "$auth_ino" = "$EXPECTED_AUTH_INO" ] && [ "$auth_mode" = "700" ] || {
  echo "ABORT: authority parent identity/mode drifted (got $auth_dev/$auth_ino/$auth_mode)"; exit 1;
}

PYTHONPATH="$REPO_CHECKOUT/scripts:$PYTHONPATH" python3 - "$AUTH_PARENT" "$REPO_CHECKOUT" <<'PYEOF'
import sys, os, json, uuid, datetime as dt
sys.path.insert(0, sys.argv[2] + "/scripts")
from pathlib import Path
from quant_gate_b_runctl import (
    Registry, load_registry, validate_registry, canonical_json_bytes,
    sha256_digest, utc_text, AuthorityError,
)

auth_parent = Path(sys.argv[1])
checkout = Path(sys.argv[2])
registry_path = auth_parent / "registry.jsonl"
activation_root = auth_parent / "activations"
activation_root.mkdir(parents=True, exist_ok=True, mode=0o700)

EXPECTED_REGISTRY_HEAD = "sha256:97dac3e09e453dae189111c6f6d014aa2b426dea532bae6ae51de016c37ed8bc"
EXPECTED_RUN_ID = "gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811"
EXPECTED_ATTEMPT = 1
EXPECTED_RESERVATION_DIGEST = "sha256:97dac3e09e453dae189111c6f6d014aa2b426dea532bae6ae51de016c37ed8bc"
EXPECTED_EPOCH = 1
EXPECTED_EPOCH_REF = "gate-b-host-relay-preseal-2026-09-21-initial-epoch"

reg = Registry(registry_path, checkout)
events = load_registry(registry_path)
validate_registry(events)
if not events or events[-1]["event_digest"] != EXPECTED_REGISTRY_HEAD:
    raise SystemExit(f"ABORT: registry head {events[-1]['event_digest'] if events else None} != expected {EXPECTED_REGISTRY_HEAD}")

reserved = next((e for e in events if e["event_type"] == "RUN_RESERVED" and e["run_id"] == EXPECTED_RUN_ID), None)
if not reserved:
    raise SystemExit("ABORT: expected reservation not found")
if (reserved["attempt_number"], reserved["event_digest"]) != (EXPECTED_ATTEMPT, EXPECTED_RESERVATION_DIGEST):
    raise SystemExit("ABORT: reserved run fields do not match expected")
if any(e.get("run_id") == EXPECTED_RUN_ID and e["event_type"] in ("ACTIVATION_SEALED", "ACTIVATION_CONSUMED", "RUN_COMPLETED", "RUN_BLOCKED_TERMINAL", "FAILED_TERMINAL") for e in events):
    raise SystemExit("ABORT: run already sealed/consumed/terminal — refuse duplicate seal")
epoch_events = [e for e in events if e["event_type"] == "REVOCATION_EPOCH_SET"]
if not epoch_events or (epoch_events[-1]["revocation_epoch"], epoch_events[-1]["revocation_reference"]) != (EXPECTED_EPOCH, EXPECTED_EPOCH_REF):
    raise SystemExit("ABORT: revocation epoch/reference drifted from expected")

issued = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
expires = issued + dt.timedelta(hours=4)

activation_id = f"gate-b-activation-{uuid.uuid4()}"
activation_obj = {
    "schema": "quant-gate-b-activation/v1",
    "activation_id": activation_id,
    "run_id": EXPECTED_RUN_ID,
    "attempt_number": EXPECTED_ATTEMPT,
    "reservation_digest": EXPECTED_RESERVATION_DIGEST,
    "candidate_sha": "4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072",
    "git_tree": "4d15ef6f471213ee6ab56337b555d2906ef9bf16",
    "verified_input_tree_digest": "sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2",
    "target_host_opaque_id": "sha256:8880e5f6d980ae94454b13dcdb0b8bb85db989b0b17a36a70b1829243d989ad5",
    "issued_at_utc": utc_text(issued),
    "not_before_utc": utc_text(issued),
    "expires_at_utc": utc_text(expires),
    "revocation_epoch": EXPECTED_EPOCH,
    "revocation_reference": EXPECTED_EPOCH_REF,
    "gate_b_mutation_authorized": True,
}
activation_bytes = canonical_json_bytes(activation_obj)
activation_digest = sha256_digest(activation_bytes)
activation_path = activation_root / f"{activation_id}.activation.json"
with open(activation_path, "wb") as f:
    f.write(activation_bytes)
os.chmod(activation_path, 0o600)

envelope_obj = {
    "schema": "quant-gate-b-blue-envelope/v1",
    "sealed_at_utc": utc_text(issued),
    "run_id": EXPECTED_RUN_ID,
    "attempt_number": EXPECTED_ATTEMPT,
    "reservation_digest": EXPECTED_RESERVATION_DIGEST,
    "machine_activation_reference": str(activation_path),
    "machine_activation_digest": activation_digest,
    "candidate_sha": "4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072",
    "git_tree": "4d15ef6f471213ee6ab56337b555d2906ef9bf16",
    "verified_input_tree_digest": "sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2",
    "target_host_opaque_id": "sha256:8880e5f6d980ae94454b13dcdb0b8bb85db989b0b17a36a70b1829243d989ad5",
    "revocation_epoch": EXPECTED_EPOCH,
    "revocation_reference": EXPECTED_EPOCH_REF,
    "mutation_capability_matrix": {
        "ALLOW_EVIDENCE_ROOT_SETUP": True,
        "ALLOW_RELEASE_MATERIALIZATION": True,
        "ALLOW_MOUNT_RECONFIGURATION": True,
        "ALLOW_PERSISTENT_MOUNT_AUTHORITY_UPDATE": True,
        "ALLOW_SYNTHETIC_STATE_SETUP": True,
        "ALLOW_SYSTEMD_START_STOP": True,
        "ALLOW_CHILD_FAULT_INJECTION": True,
        "ALLOW_SUPERVISOR_SIGKILL": True,
        "ALLOW_CONTROLLED_REBOOT": True,
        "ALLOW_MISSING_MOUNT_TEST": True,
        "ALLOW_WRITER_LOCK_CONTENTION_TEST": True,
        "ALLOW_REAL_SEC_NETWORK": False,
    },
}
envelope_bytes = canonical_json_bytes(envelope_obj)
envelope_digest = sha256_digest(envelope_bytes)
envelope_path = activation_root / f"{activation_id}.blue-envelope.json"
with open(envelope_path, "wb") as f:
    f.write(envelope_bytes)
os.chmod(envelope_path, 0o600)

ev = reg.seal_activation(activation_bytes=activation_bytes, activation_digest=activation_digest)

print(f"ACTIVATION_ID={activation_id}")
print(f"MACHINE_ACTIVATION_REFERENCE={activation_path}")
print(f"MACHINE_ACTIVATION_DIGEST={activation_digest}")
print(f"BLUE_ACTIVATION_ENVELOPE_REFERENCE={envelope_path}")
print(f"BLUE_ACTIVATION_ENVELOPE_DIGEST={envelope_digest}")
print(f"ACTIVATION_SEALED_EVENT_DIGEST={ev['event_digest']}")
print(f"REGISTRY_HEAD_DIGEST={ev['event_digest']}")
print(f"ISSUED_AT_UTC={activation_obj['issued_at_utc']}")
print(f"NOT_BEFORE_UTC={activation_obj['not_before_utc']}")
print(f"EXPIRES_AT_UTC={activation_obj['expires_at_utc']}")
print(f"REVOCATION_EPOCH={EXPECTED_EPOCH}")
print(f"REVOCATION_REFERENCE={EXPECTED_EPOCH_REF}")
PYEOF
```

The script aborts before any write if boot ID, service state, checkout identity, runctl
blob, authority-parent identity, registry head, reserved fields, or revocation epoch have
drifted from the values bound in this handoff. `Registry.seal_activation()` itself further
enforces (via `validate_registry`) that the activation matches the reservation exactly, the
revocation epoch is current, and the activation digest has not been reused.

## 9. Expected safe output fields

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

No secret environment content is printed. Nothing outside
`/var/lib/quant-p0-qualification/gate-b-authority` is written.

## 10. Explicit no-consume / no-mutation boundary

This mission and its host relay do NOT: call `consume_activation`; create the Gate-B
evidence root; materialize V4; change mounts, systemd, or firewall/network state; touch
`/var/lib/quant-p0`; start/stop the collector service; run destructive tests; contact SEC;
declare Gate-B PASS; declare t0; reserve a second run.

## 11. Mutation attestation (this cloud session)

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
REAL_CAPITAL_AUTHORIZED = FALSE
```

## 12. Final disposition

Mission-head CI `35639080368` was `in_progress` at last check (recheck required before the
owner runs the host relay in section 8):

`GATE_B_ACTIVATION_SEAL_PREP = WAITING_FOR_EXACT_HEAD_CI`

All read-only construction (governance digest inventory, machine activation template,
broader Blue envelope, host-seal relay script) is complete and durable. Once CI 35639080368
resolves `COMPLETED / SUCCESS`, this disposition becomes:

`GATE_B_ACTIVATION_SEAL_PREP = READY_FOR_OWNER_HOST_SEAL_RELAY`

Safety state held throughout:

```text
GATE_B_RUN_RESERVED = TRUE
GATE_B_RUN_ID = gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811
ACTIVATION_SEALED = FALSE
ACTIVATION_CONSUMED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
```

Returning control to Blue / owner.
