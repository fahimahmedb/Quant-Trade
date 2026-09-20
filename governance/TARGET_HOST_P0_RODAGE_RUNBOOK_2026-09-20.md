# TARGET-HOST P0 RODAGE RUNBOOK — 2026-09-20

Authority: Blue / Mission Control.
Parent contract: `governance/TARGET_HOST_RODAGE_ENTRANCE_CONTRACT_2026-09-20.md`.
Status: `PREPARED_ONLY / NOT_EXECUTED`.

This runbook is the operator sequence for collecting target-host entrance evidence for the exact Gate A v3 PASS candidate. Commands are intentionally split into read-only preflight, explicit state-authorizing operations, and fault exercises.

Frozen candidate:
`2da079d8ad75c69eb3fc2990c512735cb4bdc02b`

No command in this file declares t0.

## Phase 0 — variables and restricted evidence directory

Use a restricted root-owned evidence directory outside the immutable release.

Example shell variables:

```bash
export QUANT_RELEASE=/opt/quant-releases/2da079d8ad75c69eb3fc2990c512735cb4bdc02b
export QUANT_ROOT=/opt/quant
export QUANT_STATE=/var/lib/quant-p0
export UNIT=quant-sec-capture.service
export EXPECTED_SHA=2da079d8ad75c69eb3fc2990c512735cb4bdc02b
export EVIDENCE=/var/lib/quant-p0-qualification/entrance-$(date -u +%Y%m%dT%H%M%SZ)
sudo install -d -m 0700 "$EVIDENCE"
```

Do not write requester identity or SEC content into the evidence artifact.

## Phase 1 — immutable release identity

Read-only:

```bash
cd "$QUANT_RELEASE"
git rev-parse HEAD | tee "$EVIDENCE/git-head.txt"
git rev-parse 'HEAD^{tree}' | tee "$EVIDENCE/git-tree.txt"
git status --porcelain=v1 | tee "$EVIDENCE/git-status.txt"
test "$(git rev-parse HEAD)" = "$EXPECTED_SHA"
test -z "$(git status --porcelain=v1)"
git rev-parse --git-dir | tee "$EVIDENCE/git-dir.txt"
```

Reject:
- wrong SHA;
- dirty release;
- linked development worktree / foreign Git alternate dependency;
- unexpected mutable source tree.

Record the relationship between `$QUANT_ROOT` and `$QUANT_RELEASE`:

```bash
findmnt -T "$QUANT_ROOT" -o TARGET,SOURCE,FSTYPE,OPTIONS | tee "$EVIDENCE/mount-root.txt"
findmnt -T "$QUANT_ROOT/var" -o TARGET,SOURCE,FSTYPE,OPTIONS | tee "$EVIDENCE/mount-var.txt"
findmnt -T "$QUANT_STATE" -o TARGET,SOURCE,FSTYPE,OPTIONS | tee "$EVIDENCE/mount-state.txt"
stat -c '%A %a %U %G %n' "$QUANT_ROOT" "$QUANT_ROOT/var" "$QUANT_STATE" | tee "$EVIDENCE/path-permissions.txt"
```

Blue must inspect the output, not merely archive it.

## Phase 2 — target runtime identity

```bash
uname -a | tee "$EVIDENCE/uname.txt"
cat /etc/os-release | tee "$EVIDENCE/os-release.txt"
cat /proc/sys/kernel/random/boot_id | tee "$EVIDENCE/boot-id.txt"
/usr/bin/python3 -V 2>&1 | tee "$EVIDENCE/python-version.txt"
/usr/bin/python3 - <<'PY' | tee "$EVIDENCE/python-runtime.txt"
import platform, ssl, sys
print(sys.executable)
print(platform.python_implementation())
print(platform.platform())
print(ssl.OPENSSL_VERSION)
PY
openssl version -a | tee "$EVIDENCE/openssl.txt"
```

If a container/image/package layer is used, record its immutable digest separately.

## Phase 3 — loaded systemd definition

The repository supervisor already validates the loaded definition. Preserve the raw target-host evidence too:

```bash
systemctl show "$UNIT" --no-pager \
  --property=FragmentPath,DropInPaths,ExecStart,WorkingDirectory,Restart,RestartUSec,StartLimitIntervalUSec,StartLimitBurst,KillMode,KillSignal,TimeoutStopUSec,EnvironmentFiles \
  | tee "$EVIDENCE/systemd-show.txt"

FRAGMENT="$(systemctl show "$UNIT" --property=FragmentPath --value)"
test -n "$FRAGMENT"
sha256sum "$FRAGMENT" "$QUANT_ROOT/deploy/quant-sec-capture.service" \
  | tee "$EVIDENCE/unit-digests.txt"

systemctl cat "$UNIT" | tee "$EVIDENCE/systemd-cat.txt"
```

Mandatory review:
- no unbound drop-ins;
- loaded fragment and repository unit are byte-identical;
- `WorkingDirectory=/opt/quant`;
- `ExecStart` is the frozen qualifying supervisor invocation;
- restart/kill/timeout values match the contract.

Do not infer equivalence from file names.

## Phase 4 — durable-state authority / anti-pre-seeding inventory

Before final qualifying launch:

```bash
sudo find "$QUANT_STATE" -xdev -printf '%m %u %g %s %T@ %p\n' \
  | sort | sudo tee "$EVIDENCE/state-inventory.txt" >/dev/null

sudo find "$QUANT_STATE" -xdev -type f -print0 \
  | sort -z \
  | sudo xargs -0 -r sha256sum \
  | sudo tee "$EVIDENCE/state-file-hashes.txt" >/dev/null

sudo sha256sum "$EVIDENCE/state-inventory.txt" "$EVIDENCE/state-file-hashes.txt" \
  | tee "$EVIDENCE/state-inventory-digest.txt"
```

Record owner/permissions of at least:
- `var/sec/supervisor_state.json`;
- `var/sec/supervisor_events.jsonl`;
- `var/sec/deployment_authority.json` if present;
- `var/sec/deployment_authorities.jsonl`;
- lifecycle journal;
- scheduler journal;
- attempt journal;
- collector state + commit ledger;
- SEC traffic budget + commit ledger;
- collector/supervisor lock files.

Do not delete unexplained rows to obtain a clean result.

Any unexplained pre-seeded authority/lifecycle/scheduler state is `NO_T0` until classified.

## Phase 5 — lock / filesystem capability preflight

Run on synthetic files inside the same target filesystem, not on captured raw evidence.

Verify:
- advisory `flock`;
- hard-link creation;
- atomic rename;
- directory fsync;
- staging/raw same-filesystem requirement.

Also verify only one qualifying writer can hold the service lock.

A second acquisition authority is a blocker.

## Phase 6 — fingerprint/materialization readiness

The fingerprint must be materialized from the effective target service semantics and exact frozen release.

Use the frozen supported command path; do not hand-edit the manifest:

```bash
cd "$QUANT_ROOT"
PYTHONPATH=src /usr/bin/python3 scripts/quant.py sec-readiness --root "$QUANT_ROOT"
```

Before the qualifying service exists, a not-ready result may be expected. Preserve output and classify why.

Fingerprint materialization and the one-use deployment authorization require the authorized requester environment. Execute them only through the approved restricted operator procedure; do not expose `QUANT_SEC_USER_AGENT` in public logs.

Supported frozen primitives are:

```text
python3 scripts/quant.py sec-fingerprint --root /opt/quant
python3 -I /opt/quant/deploy/quant_sec_supervisor.py --root /opt/quant --authorize-deployment
```

The supervisor's `--authorize-deployment` operation does **not** declare t0. It writes a one-use deployment/start authority and validates the loaded systemd definition for the qualifying target.

Preserve only opaque binding metadata and digests.

## Phase 7 — authorized systemd launch

After one-use deployment authority is recorded:

```bash
sudo systemctl start "$UNIT"
systemctl status "$UNIT" --no-pager | tee "$EVIDENCE/systemd-status-after-start.txt"
systemctl show "$UNIT" --property=InvocationID,MainPID,ActiveState,SubState,Result \
  | tee "$EVIDENCE/systemd-runtime-after-start.txt"
```

Confirm from restricted P0 evidence:
- genuine systemd invocation identity;
- exactly one matching `CHILD_LAUNCH_AUTHORIZED`;
- deployment nonce consumed exactly once;
- lifecycle start binds the same fingerprint/authority/boot/supervisor identity;
- duplicate claim is impossible;
- no operator-intervention contamination.

If the launch becomes `MANUAL_START` or authority is ambiguous: `NO_T0`.

## Phase 8 — opaque live health / integrity

Use repository-supported public surfaces:

```bash
cd "$QUANT_ROOT"
PYTHONPATH=src /usr/bin/python3 scripts/quant.py sec-status --root "$QUANT_ROOT" \
  | tee "$EVIDENCE/sec-status.json"

PYTHONPATH=src /usr/bin/python3 scripts/quant.py sec-verify --root "$QUANT_ROOT" \
  | tee "$EVIDENCE/sec-verify.json"

PYTHONPATH=src /usr/bin/python3 scripts/quant.py sec-readiness --root "$QUANT_ROOT" \
  | tee "$EVIDENCE/sec-readiness.json"
```

Do not publish restricted journals or interpretable filing content.

## Phase 9 — target-host fault evidence before final rodage

Destructive fault tests must be planned separately and must not destroy the preserved acquisition reservoir.

Evidence required before final rodage:
- real `systemctl stop/start`;
- child abnormal exit / SIGKILL witnessed by same supervisor;
- replacement supervisor cannot forge automatic restart;
- restart delay/burst behavior;
- reboot with durable mount restored before service;
- missing-mount startup fails;
- writer-lock contention fails closed.

Use synthetic/offline P0 state where a destructive test would otherwise contaminate the final preserved reservoir.

Each fault exercise gets its own hash-addressable restricted artifact.

## Phase 10 — entrance verdict

After all evidence is collected, Blue records only one of:

`TARGET_HOST_ENTRANCE = PASS`
`READY_FOR_FINAL_RODAGE = TRUE`

or

`TARGET_HOST_ENTRANCE = BLOCKED`
`READY_FOR_FINAL_RODAGE = FALSE`

Unknown mandatory evidence is BLOCKED, not PASS.

## Phase 11 — pre/post rodage bindings

At final rodage start and end, re-record:
- SHA/tree;
- fingerprint/materialized manifest;
- loaded-unit digests;
- runtime identity;
- boot id;
- mount topology;
- durable-state inventory digest;
- supervisor/lifecycle authority references;
- raw-object integrity verdict.

Any unexplained drift invalidates the interval.

## Phase 12 — explicit non-authority

Even a fully green entrance and rodage do not themselves set t0.

After rodage:

`t0 = NOT DECLARED`

until Blue reviews the completed evidence and writes a separate explicit t0 decision.

Current state:
- `GATE_A_V3_REPOSITORY_DISPOSITION = PASS`
- `TARGET_HOST_ENTRANCE = PREPARED_ONLY`
- `READY_FOR_FINAL_RODAGE = FALSE`
- `t0 = NOT DECLARED`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
