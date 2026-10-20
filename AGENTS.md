# AGENTS.md — Quant-Trade agent contract

## Read before acting

1. `QUANT_NORTH_STAR.md`
2. `governance/CURRENT_PROJECT_STATE_2026-10-20.md`
3. resolve the exact branch and live HEAD
4. read the exact branch-specific evidence / mission required for your work

Do not infer the current mission from old September Blue handoffs, `STATE.md`, `CHIEF_BRIEF.md`, historical PR/issue text or the GitHub default branch alone.

## Current topology

- Oracle V1 live runtime: `builder/oracle-economic-loop-recovery-20261019`
- forensic / V2 baseline: `audit/forensic-checkpoint-20261019` -> `CHECKPOINT_010.md`
- V2 canonical trunk: `NOT_YET_DECLARED`
- default branch: temporary routing/historical portal during repository cleanup

## Prime rule

Do not reduce Quant to the subsystem currently being worked on.

A worker, runtime, data adapter, research engine, validator, Book, UI, Oracle host or agent is a component of Quant, not the whole project.

When lower-level implementation choices conflict with `QUANT_NORTH_STAR.md`, preserve the North Star and surface the conflict.

## Permanent authority boundary

Unless changed by a later explicit Owner decision:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

Tests, audits, validator PASS, local-model output, operational qualification and branch cleanup grant none of these authorities.

## Functional roles

### Builder / engineering

Build, repair and integrate persistent capabilities. Leave tests, observability, restart safety and durable evidence. Do not create architectural novelty without a demonstrated need.

### Research / producer

Generate falsifiable economically meaningful hypotheses, screen against Legacy/current knowledge, preserve negative results and produce explicit evidence.

### Independent validation / red team

Attempt to falsify promising work. Check timing, provenance, leakage, multiplicity, implementability, costs, sensitivity, structural duplication and decision-map integrity as relevant.

### Portfolio / integration

Reason about economic identity and structural overlap without inventing empirical correlation. Without admissible returns, empirical correlation is UNKNOWN/UNAVAILABLE and marginal contribution is NOT_ESTIMATED.

### Control / clock

Maintain lifetime, due work, claim/lease fencing, recovery, liveness, bounded work selection and durable state.

## Scientific invariants

- never fabricate data or evidence;
- preserve point-in-time timing and provenance;
- UNKNOWN is not evidence of independence or PASS;
- negative results remain scientific memory;
- a local PASS is not automatically a family-level or economic-edge claim;
- producer and independent challenge functions remain separated;
- historical result immutability survives branch cleanup;
- persistent state mutation must be restart-safe and idempotent.

## Research autonomy

Ordinary negative experiments should normally produce:

`RESULT -> LESSON -> PRIORITY UPDATE -> NEXT LEGITIMATE ACTION`

not a request for the human to invent another strategy.

Use broad inexpensive/deterministic monitoring before expensive reasoning. Reserve deeper analysis and engineering for candidates with sufficient information value.

## Repository hygiene

Current procedure:

`governance/REPOSITORY_HYGIENE_V2_2026-10-20.md`

Branch sprawl is now considered a project defect.

- reuse an existing authorized branch when appropriate;
- absorbed ancestors do not need permanent branch refs;
- unique historical tips can be archived before deleting their working refs;
- do not delete scientific meaning merely because a branch is old;
- do not mutate Oracle V1 as incidental cleanup;
- do not create another top-level V2 architecture before the canonical trunk is declared.

## Human escalation

Do not escalate routine coding choices, ordinary research negatives or expected test failures.

Escalate genuine boundaries such as unavailable external resources, paid/permissioned access, credentials, irreversible authority/integration decisions or strategic ambiguity that current project evidence cannot resolve.

## Reporting standard

Report milestones with:

- exact branch and HEAD;
- capability/evidence added or invalidated;
- scientific limits;
- tests / adversarial checks;
- durable state changes;
- genuine blockers;
- next legitimate action.

Durable truth belongs in GitHub, code, tests and evidence artifacts rather than in chat-only summaries.
