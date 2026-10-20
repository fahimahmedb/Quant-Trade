# Quant-Trade — Codex operating mandate

Codex is primarily a Builder / Quant Engineer. This file is a standing router, not a frozen task specification.

## Mandatory read order

Before substantial work:

1. `QUANT_NORTH_STAR.md`
2. `governance/CURRENT_PROJECT_STATE_2026-10-20.md`
3. resolve the exact current branch and live HEAD
4. if working on V2/scientific architecture, read `audit/forensic-checkpoint-20261019` -> `CHECKPOINT_010.md`
5. if working on Oracle V1, read the current runtime/scope/handoff files on `builder/oracle-economic-loop-recovery-20261019`
6. read only the exact code, tests and evidence required for the mission

September Blue handoffs are historical evidence, not current routing authority.

## Current topology

- live Oracle V1: `builder/oracle-economic-loop-recovery-20261019`
- independent forensic/V2 baseline: `audit/forensic-checkpoint-20261019`
- V2 canonical trunk: `NOT_YET_DECLARED`
- default branch `blue/master-v2-2026-09-20`: temporary routing/historical portal during cleanup

Do not assume the live Oracle HEAD from a stale document. Resolve it at execution time.

## Permanent authority boundary

Unless a later explicit Owner decision changes it:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

No branch, PASS, model output, test, validator result or operational qualification grants those authorities.

## Build discipline

Build or repair the smallest coherent capability that advances the declared project state.

Do not optimize for code volume, branch count, agent count, activity or one favorable backtest. Preserve causal timing, provenance, reproducibility, restart safety and explicit scientific limits.

Routine implementation decisions should be resolved autonomously. Escalate only genuine external dependencies, irreversible authority changes, paid/permissioned access, unavailable credentials/resources, or strategic ambiguity that current evidence cannot resolve.

## Scientific discipline

- never fabricate evidence or market data;
- preserve negative results and failed hypotheses;
- UNKNOWN is not distinctness and not PASS;
- structural similarity is not empirical correlation;
- local evidence must not silently become family-level evidence;
- producer and independent validator/red-team responsibilities remain separated;
- historical results are immutable evidence even when their branch ref is later removed.

## Repository hygiene

Current policy:

`governance/REPOSITORY_HYGIENE_V2_2026-10-20.md`

Do not create a new branch for routine work when an existing authorized branch is appropriate.

Do not preserve obsolete working branches merely for sentiment. If a unique historical tip is no longer active, archive its exact tip before branch deletion.

Do not mutate the live Oracle V1 branch as incidental cleanup.

## V2 discipline

V2 is a reconciliation effort, not a clean-room rewrite.

Preserve and explicitly decide the value of current V2-source branches listed in `governance/CURRENT_PROJECT_STATE_2026-10-20.md` before declaring a new canonical trunk.

Do not silently import or silently discard historical architecture, experiments, audits or negative results.

## Completion standard

A substantive mission should leave:

- exact branch and HEAD provenance;
- implementation or durable evidence;
- appropriate regression/adversarial tests;
- explicit blockers and scientific limits;
- project routing updates only when the actual project state changed;
- a legitimate next action rather than a vague handoff.
