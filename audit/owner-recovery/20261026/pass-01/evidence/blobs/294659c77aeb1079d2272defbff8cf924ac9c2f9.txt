# Claude Current Mission Router

This file is deliberately a router, not a frozen mission.

## Current source of truth

Read:

1. `QUANT_NORTH_STAR.md`
2. `governance/CURRENT_PROJECT_STATE_2026-10-20.md`
3. resolve the exact current branch and live HEAD
4. read the branch-specific mission / audit / runtime evidence required for the work

Do not infer current work from historical September governance, `STATE.md`, `CHIEF_BRIEF.md`, old issues/PRs or a stale branch name.

## Current project rails

### Oracle V1

Live branch:

`builder/oracle-economic-loop-recovery-20261019`

Status: operational H24 V1 line. It may advance autonomously. Resolve live HEAD at execution time.

Do not mutate this line as incidental repository cleanup.

### Forensic / V2 preparation

Audit branch:

`audit/forensic-checkpoint-20261019`

Current forensic checkpoint:

`CHECKPOINT_010.md`

V2 canonical trunk:

`NOT_YET_DECLARED`

Current objective is repository cleanup + evidence reconciliation + explicit V2 source selection before declaring a small canonical V2 trunk.

## Permanent safety

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

No lower-level mission may silently change these values.

## Repository hygiene

Use:

`governance/REPOSITORY_HYGIENE_V2_2026-10-20.md`

and, for terminal execution:

`scripts/repository_hygiene_20261020.sh`

Branch deletion is namespace cleanup, not evidence deletion. Unique historical tips must remain reachable before their branch refs disappear.
