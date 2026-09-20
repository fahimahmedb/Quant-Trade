# BLUE — P0 Gate A Evidence Matrix — 2026-09-20

## Purpose

Evidence ledger for the proposed compressed P0 qualification.

This file does **not** amend `P0_CONTINUOUS_OBSERVATION_MIN = P14D`.
A governance amendment is forbidden while any required row remains OPEN or while a fix lacks exact-head green proof.

Statuses:
- `GREEN` — discriminating repository proof exists and exact-head CI is known green.
- `GREEN/PRIOR` — covered by the Astra exact candidate `88566cb4...` / run `35478291920`.
- `FIX_UNDER_CI` — red reproduced and a minimal fix exists, exact-head closure pending.
- `RED_OPEN` — defect/hypothesis reproduced red, no accepted green yet.
- `TARGET_ONLY` — cannot be proved honestly in repository simulation.
- `LIVE_ONLY` — requires prospective real-source observation.

## Baseline

Astra repository checkpoint:
`643deacdf5bbbdb1d2410c762eb20f72aff16bbf`

Astra exact checkpoint CI:
`35478796506 = SUCCESS`

Astra tested code candidate:
`88566cb4fb08bdf01561ffcbfe18fd391e57c572`

Candidate CI:
`35478291920 = SUCCESS`

Astra candidate proof inventory:
- 380 unit tests;
- explicit P0 lane 271/271;
- V1 E2E green;
- exact-head artifact;
- clean tree.

## Matrix

| Property / failure class | Evidence | Status | Residual |
|---|---|---:|---|
| One request reservation / one emitted request | Permit-spent tests, request accounting, hidden retry removal | GREEN/PRIOR | target network path |
| Global SEC traffic budget | second-consumer shared-budget tests | GREEN/PRIOR | target process topology |
| 429 Retry-After and fallback cooldown | request-control tests | GREEN/PRIOR | naturally occurring live 429 not required |
| 403 access-control cooldown | request-control tests | GREEN/PRIOR | target requester identity/network |
| bounded backoff ladder | full ladder + reset tests | GREEN/PRIOR | none logical |
| cooldown survives restart | durable budget restart test | GREEN/PRIOR | target filesystem |
| whole-request deadline | real socket trickle test | GREEN/PRIOR | target network/kernel |
| connection truncation | real socket truncation test | GREEN/PRIOR | target network/kernel |
| idle keepalive recycle without retry | transport accounting test | GREEN/PRIOR | none logical |
| malformed/HTML discovery cannot be NO_NEW_DATA | AntiFalseSuccess tests | GREEN/PRIOR | none logical |
| incomplete pagination => coverage unknown | coverage tests | GREEN/PRIOR | none logical |
| restart during pagination | replay/coverage tests | GREEN/PRIOR | target process/systemd |
| discovery queue crash replay | crash-boundary tests | GREEN/PRIOR | target filesystem |
| raw write/envelope crash replay | crash-boundary tests | GREEN/PRIOR | target filesystem/power |
| raw hardlink parent directory durability | Astra deployment-boundary red→green | GREEN/PRIOR | target filesystem/power |
| request intent vs attempt ordering | Astra audit tests | GREEN/PRIOR | target durability |
| due obligation cannot disappear on restart | Astra obligation tests | GREEN/PRIOR | target lifecycle |
| one obligation resolves at most once | audit one-to-one reconciliation | GREEN/PRIOR | none logical |
| post-hoc supersession cannot erase miss | audit adversarial tests | GREEN/PRIOR | none logical |
| fingerprint mismatch fails closed | materialization tests | GREEN/PRIOR | actual target binding |
| malformed/corrupt evidence fails audit | audit tests | GREEN/PRIOR | target storage |
| lifecycle automatic restart needs witness | Astra lifecycle tests | GREEN/PRIOR | actual systemd/cgroup |
| deployment restart needs consumed authority | Astra lifecycle tests | GREEN/PRIOR | actual deployment authority |
| SIGTERM supervisor/child boundary | real Linux subprocess test | GREEN/PRIOR | actual systemd |
| SIGKILL/PDEATHSIG boundary | real Linux subprocess test | GREEN/PRIOR | actual systemd/cgroup |
| effective Restart/Kill/timeout config | Astra Phase-7 systemd contract tests | GREEN/PRIOR | loaded target unit |
| stdout/status visibility firewall | dedicated sec-audit + snapshot tests | GREEN/PRIOR | target access/mount surfaces |
| weekend dates not daily-index obligations | Blue virtual calendar tests `8350dd214...` | GREEN | exact source-time settlement fix modifies oracle |
| virtual P14D state-space contains no hidden simple date loop | Blue virtual-horizon test | GREEN on old settlement semantics; revalidation pending | must use corrected close semantics |
| EDGAR source date uses America/New_York | red `a9dd684...`; fix `5b5489...` | FIX_UNDER_CI | exact-head green pending |
| 30h settle measured after 22:00 ET close | red `a9dd684...`; fix `5b5489...` | FIX_UNDER_CI | exact-head green pending |
| DST cannot shorten/lengthen 30 elapsed hours | implementation converts close to UTC before duration | OPEN TEST GAP | add direct boundary regression |
| federal holiday is source-normal silence, not missing index | red branch `blue/p0-calendar-holiday-red-2026-09-20` | RED TEST RUNNING | prospective calendar authority required |
| unexpected business-day 404 remains fail-closed | existing unavailable-index tests | GREEN/PRIOR | must stay green after holiday fix |
| long state history does not duplicate/erase obligations | audit + virtual horizon | PARTIAL | optional high-cycle stress driver |
| actual mounts/read-only release/persistent state | deployment contract only | TARGET_ONLY | Gate B |
| actual flock/hardlink/rename/dir-fsync semantics | CI + code tests insufficient for host | TARGET_ONLY | Gate B |
| loaded systemd fragment/drop-ins | repository parser only | TARGET_ONLY | Gate B |
| actual interpreter/OpenSSL/runtime image | CI records runner only | TARGET_ONLY | Gate B |
| active == materialized target fingerprint | no final target manifest | TARGET_ONLY | Gate B |
| host stop/start/SIGKILL/reboot | subprocess simulation only | TARGET_ONLY | Gate B |
| real requester identity/network route | fail-closed config only | TARGET_ONLY | Gate B |
| normal overnight source silence vs dead service | logical states exist | LIVE_ONLY | Gate C |
| complete real weekend + Monday reopen | simulated calendar only | LIVE_ONLY | Gate C |
| residual unknown exact-runtime interactions | cannot be exhausted synthetically | LIVE_ONLY | bounded soak/event window |

## Exact current Blue research commits

- `8350dd214943a547af23294b8801cff98037896d` — weekend + virtual P14D tests; exact-head run `35479246181 = SUCCESS`.
- `a9dd68457397e7c392c3866ccefdef2b9bd22910` — two EDGAR close/source-date red discriminants; run `35479512122 = FAILURE` with exactly those 2 failures.
- `5b5489edef620080df3410d93e9b213c7e6c66bf` — candidate fix binding settlement to 22:00 ET + 30 elapsed hours, Eastern business date; its first CI showed the new red tests green but exposed two stale old-oracle tests.
- `3dfc54a4219f1b31374ff4a007f1d9a2dfc0ec4c` — updates those old-oracle tests independently; exact-head CI pending when this matrix was written.
- holiday red branch current line: `blue/p0-calendar-holiday-red-2026-09-20`; exact isolated red result pending.

## Amendment gate

Do not amend P14D until all of these are true:
1. CAL-001 exact-head green on one coherent qualification head.
2. CAL-002 either fixed green or explicitly proven non-defect.
3. DST elapsed-time boundary has a direct test.
4. No business-day 404 can be laundered as a holiday.
5. Gate A high-cycle history has no unexplained obligation/coverage issue, or Blue explicitly documents why existing evidence is sufficient.
6. Gate B runbook exists (it does) and target-only claims remain unclaimed.
7. Gate C keeps real overnight + full weekend + reopen as irreducible prospective evidence.

Only then may Blue draft a superseding governance amendment.
