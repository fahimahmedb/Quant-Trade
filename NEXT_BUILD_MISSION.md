# Current Build / Mission Router

> **CURRENT ROUTING — 2026-10-20**
>
> Historical missions remain available in Git history. This file intentionally describes only the current top-level routing surface.

## Read first

1. `QUANT_NORTH_STAR.md`
2. `governance/CURRENT_PROJECT_STATE_2026-10-20.md`
3. resolve exact branch + live HEAD
4. read the exact mission/audit/runtime evidence for the selected workstream

## Rail A — live Oracle V1

Branch:

`builder/oracle-economic-loop-recovery-20261019`

Purpose:

- deterministic H24 Research OS runtime;
- GitHub durable state;
- claim/lease recovery;
- fail-closed scientific/authority gates;
- local/free execution path where qualified.

This branch may advance autonomously. Do not use an old SHA as current state without resolving the live ref.

Do not perform incidental repository cleanup on this branch.

## Rail B — forensic cleanup / V2 preparation

Audit baseline:

`audit/forensic-checkpoint-20261019`

Current checkpoint:

`CHECKPOINT_010.md`

Current project objective:

```text
CLEAN_REPOSITORY
-> PRESERVE SCIENTIFIC / GOVERNANCE MEMORY
-> RECONCILE UNIQUE V2 SOURCE BRANCHES
-> DECLARE SMALL CANONICAL V2 TRUNK
-> CONTINUE V2 FROM EXPLICITLY IMPORTED CAPABILITIES
```

V2 canonical trunk is **not yet declared**.

## Repository hygiene mission

Authority / method:

`governance/REPOSITORY_HYGIENE_V2_2026-10-20.md`

Terminal tool:

`scripts/repository_hygiene_20261020.sh`

The cleanup should aggressively reduce active branch refs while preserving unique historical tips through archive tags when they are not already reachable from retained branches.

## Current retained source set

At minimum preserve as active/source refs during the first cleanup pass:

- `blue/master-v2-2026-09-20` — default/routing portal until V2 migration
- `builder/oracle-economic-loop-recovery-20261019`
- `audit/forensic-checkpoint-20261019`
- `builder/research-os-aggressive-architecture-20261015`
- `builder/research-factory-core-v2`
- `research/edge-lab-continuous`
- `research/legacy-economic-reconciliation-20261015`
- `research/design-v1`
- `codex/test`
- `builder/weather-v4-a2-doc-integration-root-candidate-2026-10-08`
- Owner-retained restaurant branch if it still exists

All other branch refs should be tested for ancestry/redundancy and otherwise archived before deletion.

## Permanent authority boundary

```text
ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
```

Repository cleanup, operational qualification or V2 design work does not alter those values.

## Completion condition for this phase

This phase is complete when:

- the branch namespace is reduced to a small understandable retained set;
- every removed unique tip remains reconstructable;
- a cleanup receipt records branch -> SHA -> disposition/archive;
- current routing files no longer point agents to obsolete September missions;
- V2 source branches have explicit retain/import/reject decisions;
- a canonical V2 trunk can be declared without guessing where prior work lives.
