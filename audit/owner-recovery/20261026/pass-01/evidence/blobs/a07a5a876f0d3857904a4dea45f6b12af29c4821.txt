# BLUE — P0 Target-Host Entrance & Rodage Runbook — 2026-09-20

## Scope

Operational runbook for the **actual target host**. It prepares evidence collection; it does not claim the host has been tested.

Read first:
- `QUANT_NORTH_STAR.md`
- `governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md`
- `governance/BLUE_P0_COMPRESSED_QUALIFICATION_PROTOCOL_2026-09-20.md`
- latest `handoff/ASTRA_P0_CHECKPOINT.md`

Never run destructive steps against the preserved live evidence reservoir unless the step explicitly says it is safe. Use a synthetic/offline state root for destructive pre-t0 fault exercises.

## Required operator inputs

Set these explicitly; do not infer them from a moving branch:

```bash
export P0_REPO=fahimahmedb/Quant-Trade
export P0_SHA=<exact-release-commit>
export P0_RELEASE=/opt/quant-releases/$P0_SHA
export P0_VIEW=/opt/quant
export P0_STATE=/var/lib/quant-p0
export P0_UNIT=quant-sec-capture.service
export P0_EVIDENCE=/var/lib/quant-p0-evidence
```

Requester identity remains private. Do not print it into evidence:

```bash
test -n "$QUANT_SEC_USER_AGENT" || { echo SEC_IDENTITY_MISSING; exit 1; }
case "$QUANT_SEC_USER_AGENT" in
  *"@"*.*) ;;
  *) echo SEC_IDENTITY_CONTACT_INVALID; exit 1 ;;
esac
```

## Phase 0 — create restricted evidence directory

```bash
sudo install -d -m 0700 "$P0_EVIDENCE"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
e="$P0_EVIDENCE/entrance-$stamp"
sudo install -d -m 0700 "$e"
```

All raw command output below goes only into `$e`.
Public/status surfaces receive opaque PASS/FAIL/BLOCKED only.

## Phase 1 — exact release identity

```bash
cd "$P0_RELEASE"
test "$(git rev-parse HEAD)" = "$P0_SHA"
git status --porcelain=v1 >"$e/git-status.txt"
test ! -s "$e/git-status.txt"
git rev-parse HEAD >"$e/git-head.txt"
git rev-parse HEAD^{tree} >"$e/git-tree.txt"
git show -s --format=fuller HEAD >"$e/git-commit.txt"
```

Fail if:
- checkout is dirty;
- HEAD differs from the authorized SHA;
- the release checkout relies on a development worktree/alternates;
- release backing bytes are writable by the service identity.

Record mount/filesystem identity:

```bash
findmnt -T "$P0_RELEASE" -o TARGET,SOURCE,FSTYPE,OPTIONS -n >"$e/release-mount.txt"
findmnt -T "$P0_STATE" -o TARGET,SOURCE,FSTYPE,OPTIONS -n >"$e/state-mount.txt"
stat -f -c '%T %d' "$P0_RELEASE" "$P0_STATE" >"$e/fs-identity.txt"
```

## Phase 2 — fixed service view and persistent state

```bash
findmnt -T "$P0_VIEW" -o TARGET,SOURCE,FSTYPE,OPTIONS -n >"$e/view-mount.txt"
findmnt -T "$P0_VIEW/var" -o TARGET,SOURCE,FSTYPE,OPTIONS -n >"$e/var-mount.txt"
readlink -f "$P0_VIEW" >"$e/view-realpath.txt"
readlink -f "$P0_VIEW/var" >"$e/var-realpath.txt"
```

Expected:
- `$P0_VIEW` resolves to the exact immutable release view;
- `$P0_VIEW/var` is backed by `$P0_STATE`;
- code outside `var` is read-only to the service;
- Product QuantSystem state is not the same writable tree.

### Negative mount test — synthetic/pre-t0 only

Do this before live rodage, under controlled synthetic state:

1. stop service;
2. temporarily prevent the P0 state mount;
3. attempt service start;
4. require startup to fail;
5. verify no fresh `$P0_VIEW/var` state tree was silently created;
6. restore mount;
7. verify original durable state is unchanged.

A missing state mount that causes automatic fresh state is a hard FAIL.

## Phase 3 — target filesystem semantics

Use a scratch directory **on the same filesystem as `$P0_STATE`**.

```bash
scratch="$P0_STATE/.qualification-fs-$stamp"
mkdir -m 0700 "$scratch"
python3 - "$scratch" <<'PY'
import fcntl, os, pathlib, sys, tempfile
root=pathlib.Path(sys.argv[1])
a=root/"a"; b=root/"b"; c=root/"c"; lock=root/"lock"
a.write_bytes(b"p0-durability-probe")
fd=os.open(a, os.O_RDONLY)
os.fsync(fd); os.close(fd)
os.link(a,b)
d=os.open(root, os.O_RDONLY | getattr(os,"O_DIRECTORY",0))
os.fsync(d); os.close(d)
c_tmp=root/"c.tmp"
c_tmp.write_bytes(b"atomic-rename")
fd=os.open(c_tmp, os.O_RDONLY); os.fsync(fd); os.close(fd)
os.replace(c_tmp,c)
d=os.open(root, os.O_RDONLY | getattr(os,"O_DIRECTORY",0))
os.fsync(d); os.close(d)
with lock.open("w") as h:
    fcntl.flock(h, fcntl.LOCK_EX | fcntl.LOCK_NB)
print("FS_PRIMITIVES_PASS")
PY
rm -rf "$scratch"
```

Fail if flock, hardlink, atomic rename or directory fsync is unsupported on the actual state filesystem.

## Phase 4 — loaded systemd authority

```bash
systemctl cat "$P0_UNIT" >"$e/systemctl-cat.txt"
systemctl show "$P0_UNIT" --no-pager \
  -p FragmentPath \
  -p DropInPaths \
  -p ExecStart \
  -p WorkingDirectory \
  -p Restart \
  -p RestartUSec \
  -p StartLimitIntervalUSec \
  -p StartLimitBurst \
  -p KillMode \
  -p KillSignal \
  -p TimeoutStopUSec \
  >"$e/systemctl-show.txt"
systemctl show "$P0_UNIT" --no-pager >"$e/systemctl-show-full.txt"
systemd-analyze verify "$P0_RELEASE/deploy/quant-sec-capture.service" \
  >"$e/systemd-analyze-verify.txt" 2>&1
```

Require:
- FragmentPath is the intended unit;
- DropInPaths is empty unless every drop-in is explicitly bound;
- effective ExecStart and WorkingDirectory preserve the accepted contract;
- Restart/Kill/timeout/start-limit values match repository authority.

Hash both repository and loaded definitions:

```bash
sha256sum "$P0_RELEASE/deploy/quant-sec-capture.service" >"$e/repo-unit.sha256"
sha256sum "$(systemctl show -p FragmentPath --value "$P0_UNIT")" >"$e/loaded-unit.sha256"
```

## Phase 5 — runtime identity

```bash
python3 --version >"$e/python-version.txt" 2>&1
python3 - <<'PY' >"$e/runtime.txt"
import platform, ssl, sys
print("executable", sys.executable)
print("python", sys.version.replace("\n"," "))
print("openssl", ssl.OPENSSL_VERSION)
print("platform", platform.platform())
PY
uname -a >"$e/uname.txt"
cat /proc/sys/kernel/random/boot_id >"$e/host-boot-id.txt"
```

Bind package/container/runtime image identity using the actual deployment mechanism. If containerized, record image digest, not a mutable tag.

## Phase 6 — single writer / global requester authority

Before start:

```bash
pgrep -af 'quant_sec_supervisor|quant.py.*serve-sec' >"$e/prestart-processes.txt" || true
systemctl status "$P0_UNIT" --no-pager >"$e/prestart-status.txt" 2>&1 || true
```

Verify no Product/Forward process has an independent SEC requester path.
There must be one global traffic-budget authority for all SEC requests.

Do not expose request counts publicly.

## Phase 7 — exact materialization / fingerprint binding

Run only through the same interpreter/environment/service configuration that production uses.
Do not substitute an interactive shell with different env.

Required result:
- manifest schema `p0_materialized_fingerprint/v2`;
- semantic fingerprint schema `acquisition_critical_fingerprint/v1`;
- active fingerprint equals materialized fingerprint;
- exact SHA/tree/runtime/service bindings match;
- no durable integrity latch.

Store the complete manifest only inside restricted evidence.

Public output:
`P0_FINGERPRINT_BINDING = PASS|FAIL|BLOCKED`.

## Phase 8 — lifecycle fault checks, synthetic state

Use a separate synthetic state root or an explicitly disposable pre-t0 reservoir.

### 8.1 normal start

```bash
sudo systemctl start "$P0_UNIT"
systemctl is-active "$P0_UNIT"
```

Capture service/supervisor state and lifecycle evidence.

### 8.2 normal stop/start

```bash
sudo systemctl stop "$P0_UNIT"
systemctl is-active "$P0_UNIT" || true
sudo systemctl start "$P0_UNIT"
```

A replacement supervisor after operator stop/start must not manufacture automatic continuity.

### 8.3 child failure

Induce a controlled child failure without killing the continuously-running supervisor.
Require the same supervisor to witness/restart the child and emit the authorized automatic cause.

### 8.4 supervisor SIGKILL

Record the supervisor PID, then under disposable state:

```bash
sudo kill -KILL <supervisor-pid>
```

Verify actual systemd/cgroup behavior, child fate, and replacement lifecycle classification.

### 8.5 host reboot

Only pre-t0:

```bash
sync
sudo systemctl reboot
```

After reboot verify:
- state mount present before service;
- same durable reservoir;
- loaded unit unchanged;
- lifecycle is not falsely upgraded to automatic continuity;
- no unexplained due obligation;
- no silent fresh state.

## Phase 9 — final pre-t0 entrance audit

Only after all destructive checks are complete and the final live state is clean.

Re-check immediately before any qualifying t0:
- exact SHA/tree;
- clean release;
- mount identities;
- loaded unit digest;
- runtime identity;
- private requester identity present;
- active == materialized fingerprint;
- no integrity latch;
- exact-head CI success;
- SEC operating calendar/current documentation.

No code/service semantic mutation after this point without a new deployment event.

If the superseding continuity governance rule is already authoritative and every entrance check is green, Blue now makes the explicit prospective declaration:

`t0 = <exact UTC timestamp>`

Record that declaration in restricted evidence before the first qualifying post-t0 observation. Never choose t0 retroactively.

## Phase 10 — qualifying live event window

Predeclare UTC and Eastern calendar boundaries before observation. The interval begins at the explicit t0 above.

Require:
- at least one normal 22:00→06:00 ET source-closed interval;
- reopening after that interval;
- one complete weekend closure;
- first required post-weekend acquisition cycle;
- applicable daily-index reconciliation after its exact settlement rule;
- every scheduler obligation accounted;
- no unexplained heartbeat/attempt hole;
- stable fingerprint/runtime/service binding;
- no invalidating intervention.

If governance still says P14D at the entrance point, do **not** substitute this event-based window: P14D remains binding until an explicit amendment is already in force before t0.

## Phase 11 — before/after resource checks

Restricted evidence only:

```bash
systemctl show "$P0_UNIT" -p MainPID -p NRestarts -p ActiveEnterTimestamp \
  >"$e/service-resource-summary.txt"
df -hT "$P0_STATE" >"$e/df.txt"
df -i "$P0_STATE" >"$e/df-inodes.txt"
```

For the active MainPID record:
- `/proc/<pid>/fd` health;
- memory/status summary;
- mount identity;
- readable journals;
- integrity latch;
- state volume growth sanity.

Do not publish request/capture counts or source-content proxies.

## Phase 12 — final artifact

Create one restricted artifact outside the immutable release binding:
- SHA;
- Git tree;
- verified input-tree digest;
- acquisition fingerprint;
- manifest/schema;
- runtime identity;
- repository + loaded service digests;
- exact CI run id;
- live UTC interval;
- deployment/lifecycle authority references;
- Gate A/B/C verdicts;
- retrospective obligation audit verdict.

Hash the artifact:

```bash
sha256sum "$e"/* >"$e/SHA256SUMS"
```

Do not call a self-referential documentation commit the tested runtime SHA.

## Stop conditions

Stop and mark BLOCKED rather than improvise if:
- state mount topology differs;
- service identity can mutate release code;
- filesystem primitive unsupported;
- loaded systemd differs/unbound drop-in exists;
- requester identity unavailable;
- multiple SEC requester authorities exist;
- materialized/active fingerprint differs;
- integrity latch exists;
- any due obligation is unexplained;
- target evidence would require leaking restricted P0 content/counts.

## Non-claims

Completion of this runbook is not automatically:
- t0 declaration;
- P14D proof;
- scientific admissibility;
- economic authority;
- real-capital authority.
