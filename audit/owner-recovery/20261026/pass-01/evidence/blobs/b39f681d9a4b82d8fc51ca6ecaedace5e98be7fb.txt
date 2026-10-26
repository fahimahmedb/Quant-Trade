# Quant-Trade

Quant-Trade is a persistent quantitative system whose long-term objective is genuine **net economic value after realistic frictions**.

`QUANT_NORTH_STAR.md` remains the highest-level product specification.

## Start here — current state

Do **not** infer current authority from branch names, old PRs, September Blue handoffs, CP11, or the default branch's code snapshot.

Read first:

1. `QUANT_NORTH_STAR.md`
2. `governance/CURRENT_PROJECT_STATE_2026-10-20.md`
3. current CP12 audit on `audit/forensic-checkpoint-20261019`
4. resolve the exact live branch + HEAD for the workstream you are changing

## Current live lines

### Oracle H24 V1

`builder/oracle-economic-loop-recovery-20261019`

Operationally qualified autonomous pre-outcome Research OS runtime. It continues to advance. V1 proves scheduling/persistence/recovery—not economic edge.

### Oracle V2 Core

`builder/oracle-v2-core-20261020`

Active V2 build rail. It reuses V1-qualified runtime mechanics and adds stricter scientific state/contracts, but it has **not yet absorbed every valuable historical Data/Research/Product capability**.

### Live Lab

Current Oracle/Live Lab rails remain under semantic reconciliation. Do not select a survivor only by branch date/name.

## Deep audit / repository cleanup

Current audit branch:

`audit/forensic-checkpoint-20261019`

Current cleanup authority is **CP12**, not CP11.

CP12 established:

- current branch count = **229**;
- V1 remains live;
- V2 Core is active but incomplete as a historical-capability absorption target;
- Research Factory Core, Evidence/Identity, SEC Census, aggressive Research OS, Edge Lab, Legacy reconciliation and Design V1 still carry material unique content;
- Weather V4 contains ratified/partial/structural Owner decisions that must be normalized before its branch family is retired;
- F1/F2/EURUSD PR chains contain scientific memory that must be indexed before cleanup;
- Live Lab canonical/integration rails diverge;
- workflow/CI sprawl is itself repository-governance debt.

Current CP12 registries:

- `governance/WORKSTREAM_INDEX_2026-10-20.md`
- `governance/OWNER_DECISIONS_2026-10-20.md`
- `governance/SCIENTIFIC_MEMORY_INDEX_2026-10-20.md`
- `governance/WORKFLOW_DISPOSITION_2026-10-20.md`
- `governance/REPOSITORY_AUTHORITY_REGISTRY_2026-10-20.md`

These files currently live on the audit branch until the V2 reconciliation package is ready for canonical integration.

### Important cleanup warning

The old CP11 mass-cleanup scripts are intentionally disabled.

Do **not** run an old one-shot branch deletion command. Current V2 policy also keeps autonomous destructive Git operations unauthorized.

The next physical cleanup must follow:

`DEEP_AUDIT -> IMPORT/REJECT UNIQUE CAPABILITIES -> INDEX SCIENTIFIC MEMORY -> INDEX OWNER DECISIONS -> RECONCILE LIVE LAB/WEATHER -> CONSOLIDATE WORKFLOWS -> DECLARE V2 TRUNK -> OWNER-EXECUTED DELETION`

## Permanent authority boundary

Unless a later explicit Owner artifact changes them:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

No model output, CI PASS, validator/Astra PASS, branch cleanup or operational qualification changes these values.

## Core scientific principles

- preserve point-in-time provenance and timing correctness;
- never fabricate data/evidence;
- structural similarity is not empirical correlation;
- preserve negative/blocked/unexecuted results as scientific memory;
- UNKNOWN remains UNKNOWN;
- producer/validator/integrator authority must remain distinct;
- persistent state transitions must be restart-safe/idempotent;
- model commentary is not evidence without the required scientific contract;
- wide/cheap monitoring precedes narrow/deep reasoning where appropriate.

## Default branch warning

The GitHub default remains `blue/master-v2-2026-09-20` as a temporary routing/historical portal.

Do not move it to V1. Do not silently promote an arbitrary V2 work branch. A clean V2 trunk is declared only after CP12 reconciliation shows exactly which historical capabilities/results/decisions were imported, rejected or retained as memory.