# OPERATOR — GATE B READ-ONLY PREFLIGHT — 2026-09-21

## 0. Scope and authority

`MISSION_TYPE = TARGET_HOST_READ_ONLY_PREFLIGHT`

`MISSION_BRANCH = operator/gate-b-read-only-preflight-2026-09-21`

`MISSION_START_HEAD = 25b3d08f19e716332cae7445ef57329c577f9e91`

`BLUE_AUTHORITY_SHA = 4c855dca152d237d2b8d86419ebc5e3a59acde42`

`SNAPSHOT_UTC = 2026-09-21T08:13:50+00:00`

`TARGET_HOST_OPAQUE_ID = sha256:8880e5f6d980ae94454b13dcdb0b8bb85db989b0b17a36a70b1829243d989ad5`

This checkpoint reports read-only activation preparation only. It is not Gate B
execution and does not authorize remediation, release materialization, service
lifecycle operations, mount changes, state changes, real-source traffic, or
activation-authority consumption.

The raw target-host snapshot is RESTRICTED. It existed only in the operator
session and is not committed. The canonical snapshot byte stream was the exact
LF-separated R1-R8 command output, encoded as UTF-8, with terminal trailing LF
bytes removed before hashing.

`RESTRICTED_SNAPSHOT_CANONICAL_SHA256 = sha256:77bfe820fa981ca3dfa70ba74d11bdb03aad6595b5752c72cd6510817e487d6b`

## 1. R1-R8 classification

| Check | Classification | Public high-level result |
| --- | --- | --- |
| R1 — host/time authority | `PASS_FOR_ACTIVATION_PREPARATION` | UTC timezone; NTP available, enabled and synchronized; boot identity captured only in restricted evidence; Ubuntu 24.04.5 LTS; Linux 6.17.0-1020-oracle on AArch64. |
| R2 — loaded systemd state | `WARN_RECHECK_AT_ACTIVATION` | Unit loaded with no drop-ins; loaded fragment bytes exactly match frozen V4 unit digest `sha256:cfeeb12ac670b5e8f46932db113ba71ed153f389e28da0c3eb41f1c0581b15a9`; frozen semantics observed, including `Restart=on-failure`, 15-second restart delay, 10-minute start-limit interval, burst 5, control-group kill mode, and 30-second stop timeout. Service state is `failed`; enablement is `disabled`; no lifecycle operation was performed. |
| R3 — mounts/state root/release topology | `BLOCKER_BEFORE_ACTIVATION` | Fixed service view is read-only but points to rejected V3 candidate `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`; expected V4 release path for `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072` is absent. Writable service state view and durable state root resolve to the same filesystem identity. No path or mount was changed. |
| R4 — runtime identity | `PASS_FOR_ACTIVATION_PREPARATION` | CPython 3.12.3 at the resolved system interpreter; OpenSSL 3.0.13; Debian/Ubuntu AArch64 runtime. No package or runtime change was performed. |
| R5 — disk/inode/evidence headroom | `WARN_RECHECK_AT_ACTIVATION` | Service-view filesystem: 6% blocks and 2% inodes used. Durable-state filesystem: 1% blocks and 1% inodes used. Journald usage: 32.1 MiB. No authorized restricted evidence root is bound: `EVIDENCE_ROOT = NOT_YET_BOUND`. No arbitrary capacity threshold is inferred. |
| R6 — process/resource baseline | `WARN_RECHECK_AT_ACTIVATION` | No service process is running, so RSS, live task and open-FD baselines are unavailable. Loaded `LimitNOFILE` is 524288. Capture must be repeated if activation is later authorized. No signal was sent. |
| R7 — proxy/resolver/TLS identity | `WARN_RECHECK_AT_ACTIVATION` | No proxy-variable names were present in the operator session; no values were printed. Resolver configuration was hashed as `sha256:70cdb37efe507d7b6e575b27172140323116146cbbb99c687680482117b203da`; TLS runtime is OpenSSL 3.0.13. Effective service network identity must be rebound without publishing secret values if activation is authorized. No network request was made. |
| R8 — metadata-only durable-state inventory | `PASS_FOR_ACTIVATION_PREPARATION` | Metadata-only inventory was available and produced `sha256:fecf62f341995c41e18cd57b18aefca534afa0e9631dbb4fb039679f0b8088ec`. No filenames or state contents are published. This digest is a drift hint only and does not prove state validity. |

## 2. Blockers

1. `EXPECTED_V4_RELEASE_PATH = ABSENT` for frozen candidate
   `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`.
2. `FIXED_SERVICE_VIEW_CANDIDATE = REJECTED_V3` at
   `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`, not frozen V4.

These findings require a separate Blue decision and sealed mutation authority.
They were not repaired during this mission.

## 3. Warnings requiring activation-time recheck

- The loaded unit is byte-identical to the frozen V4 repository unit, but the
  service remains failed and disabled and the service view is not V4.
- The restricted evidence root is not yet bound.
- A live process resource baseline is unavailable because the service is not
  running.
- Effective service proxy/requester/network identity was not exposed; it must be
  rebound privately if Blue later authorizes activation.
- The durable-state metadata digest is not a semantic or integrity verdict.

## 4. Final disposition

`GATE_B_ACTIVATION_PREP = BLOCKED_EXPECTED_V4_RELEASE_ABSENT_AND_SERVICE_VIEW_ON_REJECTED_V3`

`TARGET_HOST_READY = FALSE`

## 5. Mandatory mutation attestation

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

Operator work stops at this public checkpoint and returns control to Blue.
