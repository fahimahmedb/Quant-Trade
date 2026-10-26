# BLUE — HYBRID PROMOTION ATOMIC DRY-RUN MANIFEST — 2026-09-21

## 0. Status

`PROMOTION_DRY_RUN = PREPARED / NOT_EXECUTED`

`P14D_PROMOTION_READY = FALSE`

`AUTHORITY_CHANGE = NONE`

This is a reversible transaction rehearsal. It exists so that, after the
remaining independent proof closes, Blue can execute one coherent governance
promotion rather than assembling authority ad hoc.

## 1. Immutable production/evidence inputs already bound

Frozen V4 candidate:

`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Git tree:

`4d15ef6f471213ee6ab56337b555d2906ef9bf16`

Verified input-tree digest:

`sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2`

Selected exact-head V4 verification run:

`35536353538 = COMPLETED / SUCCESS`

V4 independent audit:

`astra/p0-gate-a-v4-independent-audit-2026-09-20@afe25984b0ddd261fda143d858106c3c71e45149`

V4 disposition:

`GATE_A_V4_REPOSITORY_DISPOSITION = PASS`

Original fault-matrix predecessor:

`builder/codex-p0-hybrid-fault-matrix-2026-09-21@e5c4c720e758cd8ab3f0e04faf541b26e204be16`

Restart-burst proof-repair delivery:

`builder/codex-p0-hybrid-restart-burst-proof-fix-2026-09-21@1fa82a75485661bf9bbb3de10b925126397dfec5`

Immutable restart-burst contract authority:

- commit `7d7bf6a27e4560951ec0fad58b69a99edf091a4b`;
- blob `e73013605c8e169a580aa1cd082f477bc5cd5722`;
- `EXPECTED_RESTART_BURST_LIMIT = 5`.

Fingerprint/calendar repository authority:

`governance/BLUE_P0_FINGERPRINT_AND_SOURCE_CALENDAR_BINDING_2026-09-21.md`

## 2. Still-open exact evidence fields

The promotion transaction MUST NOT execute until all placeholders below are
replaced with exact immutable evidence:

```text
SELECTED_BUILDER_REPAIR_CI_RESULT =
  run 35549017908 -> MUST BE COMPLETED / SUCCESS

ASTRA_TARGETED_RECHECK_FINAL_HEAD =
  PENDING

ASTRA_TARGETED_RECHECK_EXACT_HEAD_CI =
  PENDING

ASTRA_RESTART_BURST_RECHECK =
  MUST BE PASS_REPOSITORY_EVIDENCE

BLUE_FINAL_FAULT_MATRIX_DISPOSITION_SHA =
  PENDING
```

Any unresolved `MISSING_PROOF` or new `REAL_DEFECT` aborts this dry-run.

## 3. Current conflict-detection blobs

Before execution, Blue must re-fetch each file and abort/reconcile if any blob
has changed legitimately since this rehearsal.

- current governance:
  `d5f0a545ace8c563e5e72cb0f8715cf5781ab5ff`
- Blue master:
  `f99817671c56ddfdd643fc43450eaa6bb2b8f86b`
- promotion checklist:
  `b047895a98a6a3a0a5d024fcb7d385e84c222ad2`
- amendment candidate V2:
  `113b0294e5a13965305af90e84e87d9875e504e9`
- atomic promotion plan:
  `ed69460e7382bc92a5ca8d7b35cbd6f23c97d413`
- Gate-B contract candidate:
  `163cf87aa19d648a1301e4f3785f865b3ec779c6`
- Gate-B->Gate-C runbook candidate:
  `1aec3c5cfd0340cad88310054f42966d366aaa79`
- t0 precommit candidate:
  `e7f61083b7587e61e31de242c2d2a92d3ad144e5`
- Gate-B activation template candidate:
  `4158dedb579eb5368d491bea1021d5d008bf39fb`
- Gate-B evidence schema candidate:
  `1bcc373c499c99e47bfa2b55866b3379bd20493a`
- V4 release-materialization candidate:
  `e3f7c4bdea1e0f73a0e59ae951cad8cc288c270e`
- final consistency precheck:
  `1cca056a87443ebe2a07691003d3b80e295340e3`
- fingerprint/calendar binding:
  `67d551d31356e9cbd917a67395588421d3958ab4`
- Blue restart-burst reception:
  `cd76084b58bd7f18dee54238785f29234269181a`
- targeted Astra recheck specification:
  `da0ef5d2b3af494b388c5ea0e84cd458eb8d2106`

These are rehearsal snapshots, not permanent expected blobs.

## 4. Atomic transaction — create authoritative method

Create:

`governance/P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT_2026-09-21.md`

Source:
`governance/BLUE_P14D_HYBRID_AMENDMENT_CANDIDATE_V2_2026-09-21.md`

The authoritative version must add an exact evidence-binding appendix containing:
- V4 SHA/tree/input-tree/run;
- V4 Astra audit HEAD/run;
- Builder fault-matrix lineage;
- restart-burst repair SHA/run;
- targeted Astra recheck HEAD/run;
- Blue final fault-matrix disposition;
- fingerprint/calendar binding;
- final Red Team method review.

Required authority after creation:

`P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1`

Historical fixed-P14D evidence remains preserved.

## 5. Atomic transaction — promote complete Gate-B authority pack

Create new non-candidate authority files:

- `governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md`
- `governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md`
- `governance/P0_T0_PRECOMMIT_TEMPLATE_2026-09-21.md`
- `governance/BLUE_GATE_B_ACTIVATION_TEMPLATE_2026-09-21.md`
- `governance/TARGET_HOST_GATE_B_EVIDENCE_SCHEMA_2026-09-21.json`
- `governance/TARGET_HOST_V4_RELEASE_MATERIALIZATION_2026-09-21.md`

Each must be derived from the corresponding reviewed candidate and updated to
reference the authoritative hybrid amendment.

The pack becomes authoritative as a procedure only.

The promotion transaction MUST end with:

`GATE_B_MUTATION_AUTHORIZED = FALSE`

An explicit later sealed Blue activation remains required before any target-host
mutation.

## 6. Atomic transaction — update current routing

Update:

`governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`

to state:
- fixed P14D = historical/superseded for future qualification;
- `P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1`;
- repository qualification evidence closed for the accepted lineage;
- `GATE_B = NOT_STARTED`;
- `TARGET_HOST_READY = FALSE`;
- `t0 = NOT_DECLARED`;
- Product integration remains paused;
- real capital remains unauthorized.

Update:

`handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`

with the exact authoritative amendment reference/digest and the next action:
Gate-B activation preparation, not execution.

Update:

`governance/BLUE_P14D_HYBRID_PROMOTION_CHECKLIST_2026-09-21.md`

to close only evidence actually bound by exact refs.

## 7. Required post-promotion state

A successful transaction must finish in exactly this conceptual state:

```text
P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1
P14D_GOVERNANCE_STATUS = HISTORICAL / SUPERSEDED_FOR_FUTURE_QUALIFICATION

GATE_A_V4_REPOSITORY_DISPOSITION = PASS

TARGET_HOST_READY = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED

t0 = NOT_DECLARED
P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS

PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```

Promotion is therefore a method/governance change, not a runtime launch.

## 8. Abort conditions

Abort before writing authoritative files if:
- Builder selected exact-head CI is not SUCCESS;
- targeted Astra recheck is not PASS;
- any new repository REAL_DEFECT appears;
- any repository MISSING_PROOF remains;
- V4 candidate SHA/tree/input-tree changed;
- current routing blobs changed in a way not reconciled;
- promoted Gate-B pack would still reference candidate-only auxiliary authority;
- the transaction would implicitly declare t0 or authorize target-host mutation.

## 9. After successful promotion

Only then:
1. construct a concrete Blue Gate-B activation artifact;
2. bind amendment/contract/runbook/schema/materialization digests;
3. assign unique `GATE_B_RUN_ID`;
4. authorize only the explicit mutation classes needed;
5. execute Gate B on the real target host;
6. receive Gate-B evidence;
7. only after Gate-B PASS seal the t0 precommit;
8. the next unique matching qualifying launch establishes t0.

## 10. Current safety

`PROMOTION_DRY_RUN = PREPARED / NOT_EXECUTED`

`P14D_PROMOTION_READY = FALSE`

`GATE_B_MUTATION_AUTHORIZED = FALSE`

`GATE_B = NOT_STARTED`

`t0 = NOT_DECLARED`

`REAL_CAPITAL_AUTHORIZED = FALSE`
