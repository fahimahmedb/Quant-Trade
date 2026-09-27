# BUILDER — GATE B F11 LOCK-IDENTITY REPAIR MISSION — 2026-09-21

## 0. Role and branch

You are the implementation BUILDER for the bounded Quant Gate-B F11 lock-identity repair.

Repository:

`fahimahmedb/Quant-Trade`

Work ONLY on:

`builder/gate-b-f11-lock-identity-repair-2026-09-21`

DO NOT CREATE ANOTHER BRANCH.

Exact audited implementation base:

`644da76eb0227be275b8e3448118dac0cc7096ca`

Blue dispatch spec commit already present on this branch:

`113e60cb6ae9a56ffb4adb83c13a797e3563369e`

Before implementation, all commits above the audited base must be Blue governance/mission material only.

## 1. Authority to read first

Read in this order:

1. `QUANT_NORTH_STAR.md`
2. `governance/BLUE_GATE_B_F11_LOCK_IDENTITY_REPAIR_SPEC_2026-09-21.md`
3. `handoff/ASTRA_GATE_B_RUN_AUTHORITY_MECHANISMS_RECHECK_2026-09-21.md` from the Astra final branch if it is not present locally
4. `scripts/quant_gate_b_runctl.py`
5. existing run-authority repair tests

The Blue F11 repair spec is the bounded implementation authority for this mission.

## 2. Mission

Repair only:

`F11 = REAL_DEFECT / LOCK_PATH_IDENTITY`

Affected implementation:

`scripts/quant_gate_b_runctl.py :: Registry._locked()`

Required invariant:

All Registry mutation paths must serialize on one stable exclusivity identity, or fail closed before mutation when exclusivity identity is ambiguous.

Do not restart Gate-B run-authority design from zero.

Do not reopen A1-A10 except as regression checks.

## 3. Allowed implementation paths

Builder implementation changes are limited to:

- `scripts/quant_gate_b_runctl.py`
- F11-specific tests, preferably `tests/test_gate_b_f11_lock_identity_repair.py`
- `handoff/BUILDER_GATE_B_F11_LOCK_IDENTITY_REPAIR_2026-09-21.md`
- `STATE.md` only for a mechanical proof-inventory refresh if repository tooling requires it

Do not modify M4, frozen V4 `src/`, workflows, Product code, target-host runtime, evidence schema semantics, F1, F5, or V4 prestage.

## 4. Mandatory proof discipline

You MUST demonstrate RED-before / GREEN-after.

The committed F11 test must, at minimum:

1. have process A enter the actual `Registry._locked()` context;
2. replace the lock pathname with a different regular-file inode while A still holds authority;
3. start process B through the actual Registry lock/mutation path;
4. prove B cannot enter the mutation critical section concurrently;
5. accept only:
   - correct serialization until A releases, or
   - explicit fail-closed rejection before any mutation;
6. prove no rejected contender appends a registry mutation;
7. include an ordinary two-process serialization positive control;
8. exercise a replacement race while contention exists.

The RED-before result must identify the exact pre-implementation SHA. The GREEN-after result must identify the exact final Builder SHA.

A one-time `O_NOFOLLOW`, symlink test, current-path `lstat`, or post-open stat check is not by itself sufficient if a pathname can already have been replaced before the contender opens it.

## 5. Mandatory regressions

Run the existing A1-A10 suites and full repository suite.

At minimum:

`PYTHONPATH=src python3 -m unittest discover -s tests -v`

Preserve A3 post-lock freshness and A5 exact consumed-activation binding.

Do not skip, xfail, delete, weaken, or rename away any existing negative control.

## 6. Handoff

Required final handoff:

`handoff/BUILDER_GATE_B_F11_LOCK_IDENTITY_REPAIR_2026-09-21.md`

Record:

- exact branch;
- exact audited base;
- exact pre-implementation SHA;
- exact final Builder SHA;
- changed paths;
- chosen stable-lock/fail-closed mechanism;
- RED-before evidence;
- GREEN-after evidence;
- A1-A10 regression evidence;
- full-suite result;
- exact-head CI run/status once available;
- confirmation target host was not touched.

Final status may be only:

`READY_FOR_INDEPENDENT_REVIEW`

or an explicit blocker.

Do not declare `PASS_REPOSITORY_EVIDENCE`, Gate B PASS, t0, Product readiness, or real-capital authority.

## 7. Safety state

```text
TARGET_HOST_READY = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```

Return control to Blue after durable delivery and exact-head CI evidence.
