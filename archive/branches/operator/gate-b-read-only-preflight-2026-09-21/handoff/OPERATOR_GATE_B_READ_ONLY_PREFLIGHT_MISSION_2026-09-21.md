# OPERATOR — GATE B READ-ONLY PREFLIGHT — 2026-09-21

## 0. Mission type

`TARGET_HOST_READ_ONLY_PREFLIGHT`

This mission is diagnostic only. It is NOT Gate B execution.

No target-host mutation is authorized.

## 1. Exact repository authority

Start branch:
`operator/gate-b-read-only-preflight-2026-09-21`

Expected mission baseline:
`4c855dca152d237d2b8d86419ebc5e3a59acde42`

Blue promotion CI:
`35552847998 = COMPLETED / SUCCESS`

Read first:

1. `QUANT_NORTH_STAR.md`
2. `governance/P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT_2026-09-21.md`
3. `governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md`
4. `governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md`
5. `governance/BLUE_GATE_B_ACTIVATION_TEMPLATE_2026-09-21.md`
6. `governance/TARGET_HOST_V4_RELEASE_MATERIALIZATION_2026-09-21.md`
7. `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`

North Star blob at dispatch:
`8295041a8d253636d8f8aab941b811dce64939d9`

## 2. Current safety state

At mission start:

```text
P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1
TARGET_HOST_READY = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```

This mission MUST NOT change any of those values.

## 3. Strict prohibitions

Do NOT execute any command that may mutate:

- `/opt/quant`;
- `/opt/quant-releases`;
- `/var/lib/quant-p0`;
- systemd unit state;
- mounts;
- filesystems;
- journald retention/config;
- network configuration;
- package/runtime installation;
- repository working trees used by P0;
- deployment authority;
- fingerprints/materialization;
- P0 journals/state.

Explicitly forbidden:

- `systemctl start|stop|restart|reload|daemon-reload|enable|disable`;
- `reboot`, `shutdown`;
- `mount`, `umount`, `mount --bind`, remount;
- `mkdir`, `rm`, `mv`, `cp`, `touch`, `chmod`, `chown` under target-runtime/state/evidence paths;
- any fault injection or signal to P0 processes;
- any writer-lock test;
- any release materialization;
- any SEC/network request;
- any synthetic-state creation;
- any activation artifact consumption.

If a desired check would require mutation:
record `NOT_CHECKED_PRE_ACTIVATION` and continue.

## 4. Restricted evidence handling

Create the raw snapshot only in an already-existing safe temporary/user-writable
location outside P0 runtime/state, or keep it in the operator session if no
approved restricted path already exists.

Do NOT create a new target evidence root merely for this preflight.

Raw target-host evidence is RESTRICTED and MUST NOT be committed to GitHub.

Public GitHub handoff may contain only:
- opaque host identifier;
- UTC timestamp;
- digests;
- PASS/WARN/BLOCKER/UNKNOWN classifications;
- non-secret version strings;
- high-level counts;
- no requester identity;
- no IP/address;
- no environment values/secrets;
- no raw state inventory;
- no journal payload.

## 5. Read-only checks

### R1 — host/time authority

Collect read-only:
- UTC wall clock;
- timezone;
- boot ID;
- `timedatectl` NTP synchronization state;
- kernel/OS identity.

Suggested commands:

```bash
date -u --iso-8601=seconds
cat /proc/sys/kernel/random/boot_id
timedatectl show   -p Timezone -p NTPSynchronized -p NTP -p LocalRTC   -p CanNTP -p SystemClockSynchronized 2>/dev/null || true
uname -a
cat /etc/os-release
```

Do not change time settings.

### R2 — service state and loaded systemd semantics

Collect:

```bash
systemctl is-active quant-sec-capture.service || true
systemctl is-enabled quant-sec-capture.service || true
systemctl show quant-sec-capture.service   -p LoadState -p ActiveState -p SubState   -p FragmentPath -p DropInPaths   -p ExecStart -p WorkingDirectory   -p Restart -p RestartUSec   -p StartLimitIntervalUSec -p StartLimitBurst   -p KillMode -p KillSignal -p TimeoutStopUSec   -p EnvironmentFiles -p InvocationID   --no-pager
systemctl cat quant-sec-capture.service --no-pager
```

Do NOT start/stop/reload it.

### R3 — release/service-view/state mount topology

Read-only:

```bash
findmnt -T /opt/quant 2>/dev/null || true
findmnt -T /opt/quant/var 2>/dev/null || true
findmnt -T /var/lib/quant-p0 2>/dev/null || true
findmnt -T /opt/quant-releases/4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072 2>/dev/null || true

stat -Lc '%n|dev=%d|inode=%i|mode=%a|uid=%u|gid=%g|type=%F'   /opt/quant /opt/quant/var /var/lib/quant-p0 2>/dev/null || true

test -e /opt/quant-releases/4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072   && echo EXPECTED_RELEASE_PATH_EXISTS=true   || echo EXPECTED_RELEASE_PATH_EXISTS=false
```

Do not create missing paths.

### R4 — runtime identity

Read only:

```bash
command -v python3 || true
readlink -f "$(command -v python3)" 2>/dev/null || true
python3 --version 2>&1 || true
python3 - <<'PY'
import ssl, sys, platform
print("python_executable=", sys.executable)
print("python_version=", sys.version.replace("\n"," "))
print("implementation=", platform.python_implementation())
print("openssl=", ssl.OPENSSL_VERSION)
PY
openssl version -a 2>/dev/null || true
```

No installs/upgrades.

### R5 — filesystem/evidence headroom

Read only:

```bash
df -P /opt/quant /var/lib/quant-p0 2>/dev/null || true
df -Pi /opt/quant /var/lib/quant-p0 2>/dev/null || true
du -sx /var/lib/quant-p0 2>/dev/null || true
journalctl --disk-usage 2>/dev/null || true
```

If an already-authorized restricted evidence root exists, inspect it read-only.
Otherwise record `EVIDENCE_ROOT = NOT_YET_BOUND`.

### R6 — process/resource baseline

If service is running, read-only:

```bash
systemctl show quant-sec-capture.service   -p MainPID -p ControlGroup -p MemoryCurrent -p TasksCurrent   -p LimitNOFILE --no-pager 2>/dev/null || true

pid="$(systemctl show -p MainPID --value quant-sec-capture.service 2>/dev/null || true)"
if [ -n "$pid" ] && [ "$pid" != "0" ] && [ -d "/proc/$pid" ]; then
  ps -o pid,ppid,lstart,etime,rss,vsz,nlwp,cmd -p "$pid"
  ls "/proc/$pid/fd" 2>/dev/null | wc -l
fi
```

No signals.

### R7 — network/proxy/TLS identity without secret values

Record presence only:

```bash
env | awk -F= '
  BEGIN{IGNORECASE=1}
  /^(http_proxy|https_proxy|all_proxy|no_proxy|HTTP_PROXY|HTTPS_PROXY|ALL_PROXY|NO_PROXY)=/ {
    print $1"=<SET>"
  }' | sort -u

readlink -f /etc/resolv.conf 2>/dev/null || true
sha256sum /etc/resolv.conf 2>/dev/null || true
openssl version 2>/dev/null || true
```

Do NOT print proxy values, requester identity, API/user-agent secrets, or service EnvironmentFile contents.

Do NOT make a network request.

### R8 — durable-state inventory digest only

Do not print raw filenames into the public handoff.

If permissions allow, compute a restricted metadata-only inventory digest:

```bash
if [ -d /var/lib/quant-p0 ]; then
  find /var/lib/quant-p0 -xdev -printf '%P|%y|%s|%T@|%m|%u|%g\n' 2>/dev/null     | LC_ALL=C sort     | sha256sum
fi
```

This does NOT prove state validity. It is only a drift/binding hint.

Do not read or publish requester secrets or raw SEC content.

## 6. Classification

For each R1–R8 classify:

- `PASS_FOR_ACTIVATION_PREPARATION`
- `WARN_RECHECK_AT_ACTIVATION`
- `BLOCKER_BEFORE_ACTIVATION`
- `UNKNOWN_NOT_CHECKED`

This preflight can never declare Gate B PASS.

Examples of blocker-level findings:
- unexpected current runtime candidate;
- unexplained target release already dirty/mutable;
- missing/foreign durable state mount where current service is running;
- system clock unsynchronized/ambiguous;
- loaded unit obviously inconsistent with frozen semantics;
- insufficient permission to inspect mandatory activation-critical identity;
- target runtime already running under an unbound/unknown deployment.

Do not repair blockers in this mission.

## 7. Required public handoff

Write:

`handoff/OPERATOR_GATE_B_READ_ONLY_PREFLIGHT_2026-09-21.md`

Allowed contents:
- mission branch/HEAD;
- Blue authority SHA;
- snapshot UTC;
- opaque host ID or digest;
- R1–R8 classifications;
- non-secret versions/high-level state;
- restricted snapshot canonical SHA-256;
- exact blockers/warnings;
- explicit statement that no mutation occurred;
- final status:
  - `GATE_B_ACTIVATION_PREP = READY_FOR_BLUE_SEALING`, or
  - `GATE_B_ACTIVATION_PREP = BLOCKED_<REASON>`.

Do NOT commit the raw snapshot.

## 8. Mutation attestation

The final handoff must state:

```text
TARGET_HOST_MUTATION_PERFORMED = FALSE
SYSTEMD_MUTATION_PERFORMED = FALSE
MOUNT_MUTATION_PERFORMED = FALSE
P0_STATE_MUTATION_PERFORMED = FALSE
RELEASE_MATERIALIZATION_PERFORMED = FALSE
REAL_SEC_NETWORK_REQUESTS_MADE = 0
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
```

If any statement cannot be truthfully made, STOP and return to Blue immediately.

## 9. End of mission

Commit/push only the public handoff/checkpoint to the same operator branch.

Return control to Blue.

Do not continue into Gate B execution.
