# BLUE — GATE-B RUN RESERVATION / HOST-RELAY PRESEAL — 2026-09-21

## 0. Mission identity

Branch: `blue/gate-b-run-reservation-host-relay-preseal-2026-09-21`
Mission HEAD (verified): `e117ddda2b20669f98419761e09490f30885d59e`
Mission-head CI: `35637245376` on `SEC P0 pre-t0 gate`, head_sha `e117ddda2b20669f98419761e09490f30885d59e` — **status: `completed` / conclusion: `success`** (confirmed on recheck).

All read-only preparation below is complete. The host-relay command block in section 4 is
now cleared to run.

## 1. External authority chain (verified)

- Operator target-host rebind: `operator/gate-b-target-host-read-only-rebind-2026-09-21@4a503eed81df6656d6aec856f8440b66c5c39943` → `TARGET_HOST_READ_ONLY_REBIND = READY_FOR_BLUE_RUN_RESERVATION`
- Blue reception: `blue/master-v2-2026-09-20@68e72392d8ee3db5cd099da43ef6c60a3ad8bd68`, handoff `handoff/BLUE_TARGET_HOST_READ_ONLY_REBIND_RECEPTION_2026-09-21.md`, exact-head CI `35635653668 = COMPLETED / SUCCESS`.
- Mission base: `blue/gate-b-f11-final-integration-2026-09-21@4f26c1f015efb8c3530aeba8b3f87a81b0361a3f` (contains accepted `scripts/quant_gate_b_runctl.py`).

R1-R9 are NOT re-observed in this mission, per instruction.

## 2. Accepted runctl implementation (read, not modified)

`scripts/quant_gate_b_runctl.py` (1162 lines) at mission HEAD provides the accepted
fail-closed `Registry` API used verbatim below:

- `Registry(path, source_checkout)` — refuses a registry path inside the source checkout.
- `load_registry(path)` / `validate_registry(events)` — read-only, fail-closed on any
  malformed/non-canonical/non-monotonic event chain.
- `Registry.set_revocation_epoch(epoch, reference)` — append-only, epoch must be
  monotonically increasing.
- `Registry.reserve(candidate_sha, git_tree, verified_input_tree_digest,
  target_host_opaque_id, blue_reference, operator_identity_reference, run_id_factory)` —
  appends exactly one `RUN_RESERVED` event; fails closed on duplicate run id, non-monotonic
  attempt number, or any other non-terminal run already mutating the same host.
- `Registry.seal_activation(activation_bytes, activation_digest)` — validates the
  activation JSON matches schema `quant-gate-b-activation/v1` and the reservation exactly,
  then appends `ACTIVATION_SEALED`. **Not called in this mission.**
- `Registry.consume_activation(...)` — **not called in this mission.**

No reimplementation was made; the host relay below calls only this module's public API.

## 3. Authority-storage binding (candidate, host-relay-verified before use)

```text
RUN_AUTHORITY_PARENT   = /var/lib/quant-p0-qualification/gate-b-authority
RUN_REGISTRY           = /var/lib/quant-p0-qualification/gate-b-authority/registry.jsonl
RUN_RECEIPT_ROOT       = /var/lib/quant-p0-qualification/gate-b-authority/receipts
ACTIVATION_STORAGE_ROOT= /var/lib/quant-p0-qualification/gate-b-authority/activations
```

Observed grandparent anchor from the accepted read-only rebind (must still match live):

```text
/var/lib/quant-p0-qualification
dev = 2049
inode = 293551
uid = 0
gid = 0
mode = 755
```

`Registry` itself enforces (via `_validate_registry_parent_authority` /
`_ensure_lock_authority`): registry-outside-checkout, no symlink substitution, a single
grandparent-anchored parent-authority marker bound to one directory inode, and refuses to
silently adopt a replaced parent or a pre-existing unanchored lock. The relay script adds
the read-only pre-checks the mission requires (host identity, source blob identity,
existing-history search) before ever calling into `Registry`.

## 4. OWNER HOST RELAY — copy/paste-safe command block

Run this **only on the actual target host**, as root, from a checkout at the exact mission
commit. It performs steps 1-11 of mission section 7/P3: verify → read-only search →
fail-closed on ambiguity → create authority dirs only if safe → init revocation epoch only
if genuinely absent → `reserve()` exactly once → print safe fields only. It does not seal
or consume, and it touches nothing outside `RUN_AUTHORITY_PARENT`.

```bash
#!/usr/bin/env bash
set -euo pipefail

REPO_CHECKOUT="/mnt/quant-data/quant/Quant-Trade"
EXPECTED_MISSION_SHA="e117ddda2b20669f98419761e09490f30885d59e"
RUNCTL_REL="scripts/quant_gate_b_runctl.py"
AUTH_PARENT="/var/lib/quant-p0-qualification/gate-b-authority"
QUAL_ROOT="/var/lib/quant-p0-qualification"
EXPECTED_QUAL_DEV="2049"
EXPECTED_QUAL_INO="293551"

cd "$REPO_CHECKOUT"

# 1. host + source identity
actual_head="$(git rev-parse HEAD)"
[ "$actual_head" = "$EXPECTED_MISSION_SHA" ] || { echo "ABORT: checkout HEAD $actual_head != $EXPECTED_MISSION_SHA"; exit 1; }
git diff --quiet -- "$RUNCTL_REL" || { echo "ABORT: $RUNCTL_REL has local modifications"; exit 1; }
runctl_blob="$(git hash-object "$RUNCTL_REL")"
echo "RUNCTL_BLOB_SHA1=$runctl_blob"

# 2. grandparent identity — must match accepted anchor exactly, no symlink
[ -L "$QUAL_ROOT" ] && { echo "ABORT: $QUAL_ROOT is a symlink"; exit 1; }
read -r qual_dev qual_ino < <(stat -c '%d %i' "$QUAL_ROOT")
[ "$qual_dev" = "$EXPECTED_QUAL_DEV" ] && [ "$qual_ino" = "$EXPECTED_QUAL_INO" ] || {
  echo "ABORT: $QUAL_ROOT dev/inode drifted (got $qual_dev/$qual_ino, expected $EXPECTED_QUAL_DEV/$EXPECTED_QUAL_INO)"
  exit 1
}

# 3. search for any pre-existing Gate-B authority/history anywhere under the qualification root
existing="$(find "$QUAL_ROOT" -xdev -iname '*gate-b*' 2>/dev/null | grep -v "^$AUTH_PARENT\$" || true)"
if [ -n "$existing" ]; then
  echo "ABORT: found other gate-b-named paths under $QUAL_ROOT that are not the approved authority dir:"
  echo "$existing"
  exit 1
fi

# 4. if authority dir already exists, it must be explainable (no symlink, root-owned, expected mode)
if [ -e "$AUTH_PARENT" ]; then
  [ -L "$AUTH_PARENT" ] && { echo "ABORT: $AUTH_PARENT is a symlink"; exit 1; }
  owner_mode="$(stat -c '%u %g %a' "$AUTH_PARENT")"
  echo "EXISTING_AUTH_PARENT_OWNER_MODE=$owner_mode"
  [ -f "$AUTH_PARENT/registry.jsonl" ] && echo "EXISTING_REGISTRY_FOUND=true (will be loaded read-only and validated; no reset)"
else
  echo "AUTH_PARENT_ABSENT=true (will be created root:root 0700)"
fi

# 5. run the reservation via the accepted module only — no reimplementation
PYTHONPATH="$REPO_CHECKOUT/scripts:$PYTHONPATH" python3 - "$AUTH_PARENT" "$REPO_CHECKOUT" <<'PYEOF'
import sys, os, json
sys.path.insert(0, sys.argv[2] + "/scripts")
from pathlib import Path
from quant_gate_b_runctl import Registry, load_registry, validate_registry, AuthorityError

auth_parent = Path(sys.argv[1])
checkout = Path(sys.argv[2])
registry_path = auth_parent / "registry.jsonl"
receipt_root = auth_parent / "receipts"
activation_root = auth_parent / "activations"

auth_parent.mkdir(parents=True, exist_ok=True, mode=0o700)
os.chmod(auth_parent, 0o700)
receipt_root.mkdir(parents=True, exist_ok=True, mode=0o700)
activation_root.mkdir(parents=True, exist_ok=True, mode=0o700)

reg = Registry(registry_path, checkout)

# read-only load + validate existing history first (fails closed on any corruption)
existing_events = load_registry(registry_path)
validate_registry(existing_events)
print(f"EXISTING_EVENT_COUNT={len(existing_events)}")

# init revocation epoch ONLY if genuinely absent
has_epoch = any(e["event_type"] == "REVOCATION_EPOCH_SET" for e in existing_events)
if not has_epoch:
    ev = reg.set_revocation_epoch(
        epoch=1,
        reference="gate-b-host-relay-preseal-2026-09-21-initial-epoch",
    )
    print(f"REVOCATION_EPOCH_INITIALIZED=1")
    print(f"REVOCATION_EPOCH_EVENT_DIGEST={ev['event_digest']}")
else:
    print("REVOCATION_EPOCH_ALREADY_PRESENT=true")

# reserve exactly once
ev = reg.reserve(
    candidate_sha="4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072",
    git_tree="4d15ef6f471213ee6ab56337b555d2906ef9bf16",
    verified_input_tree_digest="sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2",
    target_host_opaque_id="sha256:8880e5f6d980ae94454b13dcdb0b8bb85db989b0b17a36a70b1829243d989ad5",
    blue_reference="blue/master-v2-2026-09-20@68e72392d8ee3db5cd099da43ef6c60a3ad8bd68:handoff/BLUE_TARGET_HOST_READ_ONLY_REBIND_RECEPTION_2026-09-21.md",
    operator_identity_reference="operator/gate-b-target-host-read-only-rebind-2026-09-21@4a503eed81df6656d6aec856f8440b66c5c39943",
)

final_events = load_registry(registry_path)
head_digest = final_events[-1]["event_digest"]

print(f"GATE_B_RUN_ID={ev['run_id']}")
print(f"GATE_B_ATTEMPT_NUMBER={ev['attempt_number']}")
print(f"RUN_RESERVATION_DIGEST={ev['event_digest']}")
print(f"REGISTRY_HEAD_DIGEST={head_digest}")
ep_events = [e for e in final_events if e["event_type"] == "REVOCATION_EPOCH_SET"]
print(f"REVOCATION_EPOCH={ep_events[-1]['revocation_epoch']}")
print(f"REVOCATION_REFERENCE={ep_events[-1]['revocation_reference']}")
st = os.stat(auth_parent)
print(f"AUTHORITY_STORAGE_BINDING={auth_parent} dev={st.st_dev} inode={st.st_ino} mode={oct(st.st_mode)[-4:]}")
PYEOF
```

**Fail-closed guarantees inherited from `Registry` itself** (no relay reimplementation
needed): non-symlink checkout-external registry path; single grandparent-anchored parent
identity; rejection of a second logical registry history under a replaced parent directory;
rejection of a duplicate run id or non-monotonic attempt number; rejection of a concurrent
non-terminal mutating run on the same `target_host_opaque_id`.

## 5. Expected safe output fields (from step above)

```text
GATE_B_RUN_ID                = <printed by relay>
GATE_B_ATTEMPT_NUMBER         = <printed by relay>
RUN_RESERVATION_DIGEST        = <printed by relay, sha256:...>
REGISTRY_HEAD_DIGEST          = <printed by relay, sha256:...>
REVOCATION_EPOCH               = <printed by relay, integer>
REVOCATION_REFERENCE           = <printed by relay, string>
AUTHORITY_STORAGE_BINDING      = <path dev inode mode>
```

None of these fields have been generated by this cloud session. No cloud-side registry,
lock, or reservation was created; nothing under `/var/lib/quant-p0-qualification` was
touched from this container.

## 6. Preseal `quant-gate-b-activation/v1` field map (reservation fields left as placeholders)

```json
{
  "schema": "quant-gate-b-activation/v1",
  "activation_id": "<PLACEHOLDER: assigned by Blue after reservation returns>",
  "run_id": "<PLACEHOLDER: GATE_B_RUN_ID from host relay>",
  "attempt_number": "<PLACEHOLDER: GATE_B_ATTEMPT_NUMBER from host relay>",
  "reservation_digest": "<PLACEHOLDER: RUN_RESERVATION_DIGEST from host relay>",
  "candidate_sha": "4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072",
  "git_tree": "4d15ef6f471213ee6ab56337b555d2906ef9bf16",
  "verified_input_tree_digest": "sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2",
  "target_host_opaque_id": "sha256:8880e5f6d980ae94454b13dcdb0b8bb85db989b0b17a36a70b1829243d989ad5",
  "issued_at_utc": "<PLACEHOLDER: bounded, set at seal time>",
  "not_before_utc": "<PLACEHOLDER: >= issued_at_utc, set at seal time>",
  "expires_at_utc": "<PLACEHOLDER: > not_before_utc, set at seal time>",
  "revocation_epoch": "<PLACEHOLDER: REVOCATION_EPOCH from host relay>",
  "revocation_reference": "<PLACEHOLDER: REVOCATION_REFERENCE from host relay>",
  "gate_b_mutation_authorized": true
}
```

This exact key set matches `_activation()`'s required `keys` set in
`scripts/quant_gate_b_runctl.py`. It is NOT sealed in this mission; `seal_activation` and
`consume_activation` are not called.

## 7. Broader Blue activation-envelope field map (fixed fields only)

```text
governance_refs:
  post_astra_convergence   = blue/gate-b-post-astra-convergence-2026-09-21@c14f28466cf7aeaddfe265a8b8aaf77fd301d4d3 (CI 35627516386 = COMPLETED/SUCCESS)
  f11_final_integration    = blue/gate-b-f11-final-integration-2026-09-21@4f26c1f015efb8c3530aeba8b3f87a81b0361a3f
  host_rebind_operator     = operator/gate-b-target-host-read-only-rebind-2026-09-21@4a503eed81df6656d6aec856f8440b66c5c39943
  host_rebind_reception    = blue/master-v2-2026-09-20@68e72392d8ee3db5cd099da43ef6c60a3ad8bd68 (CI 35635653668 = COMPLETED/SUCCESS)
  this_mission             = blue/gate-b-run-reservation-host-relay-preseal-2026-09-21@e117ddda2b20669f98419761e09490f30885d59e (CI 35637245376 = <recheck>)

host_binding:
  target_host_opaque_id     = sha256:8880e5f6d980ae94454b13dcdb0b8bb85db989b0b17a36a70b1829243d989ad5
  host_boot_id_binding       = sha256:919bed5983f85cbec29e18537bdbe15f8bf35610ce19d77bc43b8bc0df2c8cac
  read_only_rebind_digest    = sha256:fdeba510c26b1ab3f37f9bd3539d084263faafcacb03a815e849ee1199306f87

mount_systemd_network_resource_bindings: (from accepted Operator R1-R9, not re-observed here)
  service_fragment_sha256    = cfeeb12ac670b5e8f46932db113ba71ed153f389e28da0c3eb41f1c0581b15a9
  opt_quant_mount_digest     = 84aaf95463d7d85c3efbbb3f38a11fa6a5e133d0b8f7607e7c4730c2f5ebf16f
  opt_quant_var_mount_digest = a7f083c931b4a507bafda56442fa29523d2911a2fe2ab4e98a73c207e07a7b83
  quant_p0_mount_digest      = fb37ed643fcb237fcb0c3ec54ee9ceada1e376ee88cc16f39cff47ef68a19875
  nft_ruleset_digest         = e72afb3689f51f5e3fb1cbcb3dd98565e28bd71818c3e198d3c86f55650af9d7

route1_mutation_capability_matrix:
  allowed_at_this_stage      = NONE (registry-only mutation under RUN_AUTHORITY_PARENT)
  deferred_to_seal_time      = evidence-root creation, Route-1 nft deny install, V4 materialization, service switch

evidence_root_binding        = NOT YET CREATED (deferred to seal time, per mission WARN_RECHECK_AT_SEAL)
synthetic_reservoir_binding  = NOT APPLICABLE AT THIS STAGE
activation_storage_reference = /var/lib/quant-p0-qualification/gate-b-authority/activations (created empty by relay if absent)
```

## 8. Mutation attestation (this cloud session)

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

No file was created or modified outside this repository checkout. No registry, lock, or
reservation was created anywhere by this session.

## 9. Final disposition

Mission-head CI `35637245376` resolved `completed` / `success` on head_sha
`e117ddda2b20669f98419761e09490f30885d59e` (exact match to this mission's verified HEAD).

`GATE_B_RUN_RESERVATION_PRESEAL = READY_FOR_OWNER_HOST_RELAY`

The owner may now run the section 4 command block on the actual target host. All fields in
section 6/7 marked `<PLACEHOLDER>` remain unfilled until the owner returns the real
reservation output from the host relay; this mission does not seal or consume any
activation.

Returning control to Blue / owner.
