# Quant-Trade

Quant-Trade is a persistent quantitative research system whose long-term objective is genuine **net economic value after realistic frictions**.

`QUANT_NORTH_STAR.md` remains the highest-level product specification.

## Start here — current state

The repository has undergone several generations of architecture, research, governance and deployment work. Do **not** infer the current project state from an old branch name, historical handoff or September 2026 Blue document.

Read first:

1. `QUANT_NORTH_STAR.md`
2. `governance/CURRENT_PROJECT_STATE_2026-10-20.md`
3. resolve the exact branch and live HEAD relevant to your task
4. then read only the branch-specific audit/runtime/design evidence required for that task

## Current lines

### Live Oracle V1

Current live runtime branch:

`builder/oracle-economic-loop-recovery-20261019`

This is the operational H24 Research OS / Oracle line. It can advance autonomously. Always resolve its current HEAD before making implementation claims.

V1 operational qualification proves scheduling, persistence, claim/lease recovery and fail-closed authority behavior. It does **not** prove economic edge.

### Independent audit / V2 forensic baseline

`audit/forensic-checkpoint-20261019`

Current audit checkpoint:

`090076945ff4d3e8006757047bbc6d2716d2eea6`

Read `CHECKPOINT_010.md` on that branch for the current CP7–CP9 reconciliation against qualified Oracle V1.

### V2

`V2_CANONICAL_TRUNK = NOT_YET_DECLARED`

V2 is being prepared from reconciled source branches and historical evidence. Do not create a competing top-level architecture or silently promote an old branch into V2 authority.

## Permanent safety boundary

Unless a later explicit Owner decision changes them:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

No test PASS, validator PASS, branch cleanup, model output or operational qualification changes these values.

## Repository cleanup

The active branch namespace became excessively large again (roughly 227 branches observed before the 2026-10-20 cleanup pass).

Current cleanup authority:

- `governance/REPOSITORY_HYGIENE_V2_2026-10-20.md`
- `scripts/repository_hygiene_20261020.sh`

The cleanup is aggressive on branch refs but conservative on information:

- absorbed ancestors are deleted as refs;
- duplicate refs are collapsed;
- unique historical/diverged tips are archived before branch deletion;
- live V1, the independent audit line and explicit V2 source branches remain active.

## Default branch warning

The GitHub default branch is currently still:

`blue/master-v2-2026-09-20`

During cleanup it acts as a **routing / historical portal**, not as proof that its code snapshot is the latest implementation.

The default branch will only move after a canonical V2 trunk is explicitly declared and its imported capabilities/evidence are documented.

## Core scientific principles

- preserve point-in-time provenance and timing correctness;
- never fabricate market data or evidence;
- treat structural similarity as structural similarity, not empirical correlation;
- preserve negative results and failed hypotheses as scientific memory;
- separate producer, validator/red-team and portfolio/integration authority;
- make persistent mutations restart-safe and idempotent;
- prefer wide/cheap deterministic monitoring before narrow/deep reasoning;
- do not confuse research, current opportunity, simulated execution, portfolio state or observed outcome.

## Historical material

Historical NASDAQ work, Gate A/B, Weather, Forward/Economic, Edge Lab, Blue/Astra/Builder/Owner handoffs and old runtime experiments remain valuable evidence where applicable.

They are **not automatically current authority** merely because their branch or document still exists.

Use `governance/CURRENT_PROJECT_STATE_2026-10-20.md` to determine what is live, retained for V2, scientific memory, archival evidence or cleanup material.
