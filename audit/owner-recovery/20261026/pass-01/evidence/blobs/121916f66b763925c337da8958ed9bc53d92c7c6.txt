# WORKFLOW DISPOSITION — 2026-10-20

Authority: CP12 organizational audit.

Purpose: distinguish live guards from historical execution/proof surfaces. Branch cleanup alone is insufficient if obsolete workflows remain visually and operationally active.

## Classes

- `ACTIVE_V1_RUNTIME_GUARD`
- `ACTIVE_V2_BUILD_GUARD`
- `ACTIVE_PARALLEL_PRODUCT_GUARD`
- `SOURCE_IMPORT_GUARD`
- `HISTORICAL_PROOF_ONLY`
- `HISTORICAL_RESEARCH_EXECUTION_DO_NOT_RERUN`
- `CONSOLIDATE_INTO_V2_GATE`
- `RETIRE_AFTER_IMPORT`
- `REVIEW_REQUIRED`

No workflow classification opens economic/prospective/live/capital authority.

---

## 1. Keep active now

### `.github/workflows/oracle-economic-loop-recovery-ci.yml`

Class: `ACTIVE_V1_RUNTIME_GUARD`

Reason: current Oracle H24 V1 remains a live qualified subsystem and its regression/deployment contracts are still operationally relevant.

Retirement condition: V1 is intentionally decommissioned or equivalent V1 compatibility/regression coverage is explicitly imported into the final V2 deployment gate.

### `.github/workflows/oracle-v2-core.yml`

Class: `ACTIVE_V2_BUILD_GUARD`

Reason: current V2 Core qualification/regression surface.

Must retain hard-authority-false, sealed evaluation membrane, V1 regression compatibility and no destructive Git authority.

### `.github/workflows/live-lab-native-integration-ci.yml`

Class: `ACTIVE_PARALLEL_PRODUCT_GUARD / RECONCILIATION_REQUIRED`

Reason: Live Lab is active parallel product work. Exact final workflow should be reconciled with current `live-lab-oracle-*` rails rather than multiplied further.

---

## 2. Research OS workflows that should converge into V2

### `research-os-aggressive-architecture-ci.yml`
### `research-os-aggressive-final-gate.yml`
### `research-os-autonomous-loop-ci.yml`
### `research-os-canonical-depth-ci.yml`
### `research-os-canonical-spine-ci.yml`
### `research-os-final-shape-sim.yml`
### `research-os-multi-engine-ci.yml`
### `research-os-queue-replenishment-ci.yml`
### `research-os-workflow-lanes-ci.yml`

Class: `CONSOLIDATE_INTO_V2_GATE / RETIRE_AFTER_IMPORT`

These workflows document important intermediate architecture/regression gates, but the current project should not require an operator or agent to understand nine generations of Research OS CI to know whether V2 is healthy.

Required action before retirement:

1. map each unique discriminant/test to current V2 coverage;
2. import any missing discriminant into V2 CI;
3. preserve workflow SHAs/runs as historical proof;
4. retire obsolete workflow files from the active workflow directory only after the above mapping is reviewed.

A workflow being old is not proof its discriminants are obsolete.

---

## 3. Economic readiness workflow

### `economic-readiness-integration-ci.yml`

Class: `SOURCE_IMPORT_GUARD / CONSOLIDATE_INTO_V2_GATE`

Reason: current V2 reuses economic readiness/validator components and must preserve the ASML/current-corpus/portfolio blocking regressions.

Do not retire until equivalent V2 tests explicitly cover:

- current-corpus anti-redetection;
- unresolved overlap readiness block;
- peer-set/current-lineage context;
- no fabricated empirical correlation;
- no fabricated marginal portfolio contribution;
- authority remains closed.

---

## 4. Edge Lab workflows

### `edge-lab.yml`
### `edge-lab-binance-funding-reversal.yml`
### `edge-lab-monthend-pension-rebalance.yml`
### `edge-lab-sector-relative-shock-reversal.yml`
### `edge-lab-stockbond-joint-stress-rebound.yml`

Class: `HISTORICAL_RESEARCH_EXECUTION_DO_NOT_RERUN / RETIRE_AFTER_IMPORT`

These belong to a research lineage now classified as scientific-memory/import source. They must not remain an ambiguous invitation to rerun historical looks after the V2 memory migration.

Required action:

- identify which workflows are replay/test-only versus outcome-consuming;
- preserve run/result provenance;
- import experiment/result identities into V2 memory;
- disable/retire historical execution entry points when doing so cannot destroy needed active research capability.

Do not rerun an already consumed look merely to make CI or publication cleaner.

---

## 5. SEC/P0 and Data Plane workflows

### `sec-p0-pre-t0-gate.yml`

Class: `SOURCE_IMPORT_GUARD`

Reason: Evidence/Identity and SEC Census capabilities are not yet proven absorbed by V2. The SEC/P0 line contains historical integrity/census/capture discriminants that may still be needed when Data Plane capabilities are imported.

Do not retire before the V2 Data Plane import decision.

### `data-feeds.yml`

Class: `SOURCE_IMPORT_GUARD / REVIEW_REQUIRED`

Reason: Data Plane is a North-Star subsystem and current V2 Core is not a complete Data Plane replacement. Determine whether this workflow is still feeding any current committed/state surface and whether its provenance/fingerprint semantics are required by V2.

---

## 6. V1 proof workflow

### `v1-proof-gate.yml`

Class: `HISTORICAL_PROOF_ONLY / POSSIBLE_REGRESSION_GUARD`

V1 qualification evidence is already durable, but V2 still depends on V1-qualified runtime mechanics. Retain until the V2 gate explicitly proves equivalent restart/idempotence/control-plane invariants or until the workflow is shown to be fully redundant with `oracle-economic-loop-recovery-ci.yml`.

---

## 7. Workflow retirement acceptance rule

A workflow may be removed from `.github/workflows/` only if one of the following is true:

1. it is exact/redundant proof and all unique discriminants are present in a retained workflow;
2. its workstream has become historical, all scientific/product state is indexed, and rerunning it would be misleading or unsafe;
3. its capability was explicitly rejected/superseded and the reason is durable.

For every retirement record:

- workflow path;
- last relevant commit SHA;
- last meaningful run if applicable;
- replacement workflow/test mapping or historical-memory reference;
- reason for retirement.

Git history remains evidence, but active workflow namespace should converge toward a small set an agent can interpret without reconstructing a month of project history.