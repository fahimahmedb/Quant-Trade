# ASTRA — GATE-B F11 FINAL TARGETED RECHECK MISSION — 2026-09-21

## Mission identity

ROLE:

`ASTRA / INDEPENDENT REVIEWER`

REPOSITORY:

`fahimahmedb/Quant-Trade`

WORK ONLY ON:

`astra/gate-b-f11-lock-identity-recheck-2026-09-21`

AUDITED_INTEGRATION_BRANCH:

`blue/gate-b-f11-final-integration-2026-09-21`

AUDITED_INTEGRATION_SHA:

`4f26c1f015efb8c3530aeba8b3f87a81b0361a3f`

AUDITED_INTEGRATION_EXACT_HEAD_CI:

`35619545254 = COMPLETED / SUCCESS`

BUILDER_FINAL_SHA:

`e600295b2aa7056e8176e0286f9d67f5c65b1c11`

BUILDER_FINAL_EXACT_HEAD_CI:

`35617257622 = COMPLETED / SUCCESS`

Blue authorization:

`handoff/BLUE_GATE_B_F11_PASS_FOR_INDEPENDENT_ASTRA_RECHECK_2026-09-21.md`

Do NOT create another branch.

## 0. Verify before substantive work

```bash
git fetch origin --prune
git rev-parse HEAD
git rev-parse origin/astra/gate-b-f11-lock-identity-recheck-2026-09-21
git rev-parse origin/blue/gate-b-f11-final-integration-2026-09-21
```

Verify:
- assigned Astra branch HEAD equals the exact mission HEAD recorded by Blue after this
  mission commit;
- audited integration still resolves exactly to
  `4f26c1f015efb8c3530aeba8b3f87a81b0361a3f`;
- CI `35619545254` is exact-head and `COMPLETED / SUCCESS`;
- Builder provenance and CI remain exactly as declared;
- Astra delta above the integration is mission/audit material only.

Any mismatch => STOP.

## 1. Read only required authorities

Read:

1. `QUANT_NORTH_STAR.md`
2. `handoff/BLUE_GATE_B_F11_PASS_FOR_INDEPENDENT_ASTRA_RECHECK_2026-09-21.md`
3. `handoff/BLUE_GATE_B_F11_FINAL_INTEGRATION_RECEPTION_2026-09-21.md`
4. `governance/BLUE_GATE_B_F11_LOCK_IDENTITY_REPAIR_SPEC_2026-09-21.md`
5. `governance/BLUE_GATE_B_F11_BRANCH_RECONCILIATION_PARENT_PATH_CHALLENGE_2026-09-21.md`
6. original blocker:
   `handoff/ASTRA_GATE_B_RUN_AUTHORITY_MECHANISMS_RECHECK_2026-09-21.md`
7. final Builder handoff:
   `handoff/BUILDER_GATE_B_LOCK_PATH_IDENTITY_REPAIR_2026-09-21.md`

Do not restart the whole Gate-B architecture audit.

## 2. Mandatory targeted F11 matrix

Use disposable local directories and real independent OS processes.

### F11-R1
Public lock pathname replacement while holder A owns the real production Registry
critical section.

Required: B cannot enter a concurrent second mutation domain.

### F11-R2
Coordinated public-lock + authority-anchor replacement while A remains active.

Required: B cannot enter a concurrent second mutation domain.

### F11-P1
Whole immediate configured registry parent replacement:
- A inside real `Registry._locked()`;
- move original parent P1 away;
- create fresh P2 at same configured pathname;
- B constructs same logical Registry and calls a real mutation entrypoint.

Required: B rejects while A is still independently confirmed active.

### F11-P2
Rejected replacement-parent contender must create no:
- registry;
- lock;
- anchor;
- reservation;
- activation;
- receipt;
- evidence binding;
- terminal mutation;
- reusable authority.

### F11-P3
While P2 persists, repeated attempts fail closed.

After operator repair restoring original P1, access must continue the original registry
history rather than bootstrap a second history.

### F11-R5
No-attack positive control:
independent real processes serialize normally and Registry remains usable.

## 3. Grandparent-anchor review

Inspect the actual final implementation.

Verify:
- parent identity marker is checked before replacement P2 can bootstrap authority;
- marker creation/revalidation is fail-closed;
- critical-section path operations are anchored to held parent dir fd where intended;
- no mutation is redirected into replacement P2;
- no competing marker can silently establish a second history under the declared
  immediate-parent attack model.

Do NOT demand infinite recursive ancestor locking.

If residual risk genuinely requires control of grandparent/ancestor ownership, mounts or
namespace on the real host, classify that residual:

`TARGET_HOST_ONLY`

rather than reopening repository F11.

## 4. A1-A10 non-regression — targeted only

Do not redo the full previous audit.

A1-A5:
targeted smoke/negative controls because `quant_gate_b_runctl.py` changed.

A6-A8:
if `scripts/verify_gate_b_deployed_bytes.py` and the exact frozen candidate surfaces
are unchanged, record prior-proof preservation rather than repeating the full audit.

A9-A10:
materially recheck because they are adjacent to cross-process/path-race authority.

Run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Do not weaken/skip/xfail tests.

## 5. Bounded adjacent search

Only search for defects introduced by the F11 repair:
- marker/bootstrap race;
- stale marker adoption;
- dir_fd/path mismatch;
- write escaping to P2;
- crash during bootstrap;
- lock-order deadlock;
- recovery creating two histories.

Classify any finding:

`REAL_DEFECT | TEST_DEFECT | MISSING_PROOF | TARGET_HOST_ONLY | NON_ISSUE`

Do not broaden scope.

## 6. Final handoff

Write exactly:

`handoff/ASTRA_GATE_B_F11_LOCK_IDENTITY_RECHECK_2026-09-21.md`

Record:

```text
AUDITED_INTEGRATION_BRANCH =
AUDITED_INTEGRATION_SHA =
AUDITED_INTEGRATION_EXACT_HEAD_CI =

BUILDER_FINAL_SHA =
BUILDER_FINAL_EXACT_HEAD_CI =

ASTRA_START_HEAD =
ASTRA_FINAL_HEAD =
ASTRA_EXACT_HEAD_CI =
```

Result matrix:

```text
F11_PUBLIC_LOCK =
F11_LOCK_PLUS_ANCHOR =
F11_PARENT_REPLACEMENT =
F11_PARENT_NO_MUTATION =
F11_PARENT_RECOVERY =
F11_NORMAL_SERIALIZATION =

A1_A5_NON_REGRESSION =
A6_A8_PRIOR_PROOF_PRESERVED =
A9_A10_NON_REGRESSION =

ADJACENT_FINDING =
ASTRA_GATE_B_F11_RECHECK =
```

PASS allowed only if all repository-level F11 controls are independently established
and no new repository blocker exists:

`ASTRA_GATE_B_F11_RECHECK = PASS_REPOSITORY_EVIDENCE`

Otherwise return one precise blocker.

## 7. Safety

Even on PASS:

```text
TARGET_HOST_TOUCHED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```

Commit/push only Astra audit material.

Return control to Blue.
