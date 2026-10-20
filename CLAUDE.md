# Quant-Trade — Claude operating context

Keep this file compact. It is a standing router, not a frozen mission.

## Mandatory orientation

Before substantial work, read in this order:

1. `QUANT_NORTH_STAR.md`
2. `governance/CURRENT_PROJECT_STATE_2026-10-20.md`
3. resolve the exact current branch and live HEAD
4. read the exact branch-specific audit/runtime/design evidence required for the assigned mission

Do **not** use September 2026 Blue handoffs, `STATE.md`, `CHIEF_BRIEF.md`, old issues, old PR text or the GitHub default branch alone to infer the current mission.

## Current project lines

- live Oracle V1: `builder/oracle-economic-loop-recovery-20261019`
- independent forensic / V2 baseline: `audit/forensic-checkpoint-20261019` -> `CHECKPOINT_010.md`
- V2 canonical trunk: `NOT_YET_DECLARED`
- default branch `blue/master-v2-2026-09-20`: routing/historical portal during cleanup, not latest-code authority

Oracle V1 may advance autonomously. Resolve its current HEAD rather than trusting a stale SHA in a chat or old document.

## Permanent authority boundary

Unless a later explicit Owner decision changes it:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

Operational qualification, tests, validator PASS, frozen hypotheses, branch cleanup or model output grant none of these authorities.

## Builder role

Claude Code is primarily a Builder / Quant Engineer.

Do not redefine Quant around the subsystem currently being edited. Prefer the smallest coherent implementation that advances the current declared architecture and preserves evidence, restart safety and scientific boundaries.

Routine engineering decisions do not require Owner escalation. Escalate only genuine external boundaries, irreversible authority changes, unavailable resources/credentials, paid access, or strategic ambiguity not resolvable from current evidence.

## Scientific / runtime invariants

- never fabricate market data or evidence;
- preserve point-in-time timing, provenance and immutable historical results;
- UNKNOWN is not evidence of independence or PASS;
- structural similarity is not empirical correlation;
- preserve producer / validator-red-team / integration separation;
- persistent mutations must be restart-safe and idempotent;
- failed experiments remain scientific memory;
- one local PASS must not silently become a family-level or economic-edge claim.

## Repository hygiene

Current cleanup authority:

`governance/REPOSITORY_HYGIENE_V2_2026-10-20.md`

Do not recreate branch sprawl. Reuse current branches where appropriate. If historical unique work is no longer active, archive its exact tip before deleting its working branch ref.

Do not mutate the live Oracle V1 branch as incidental cleanup.

## V2 discipline

V2 is being assembled from reconciled sources. Important current source branches are listed in `governance/CURRENT_PROJECT_STATE_2026-10-20.md`.

Do not:

- start a competing top-level architecture;
- silently promote an old branch to V2 authority;
- discard negative results because they are inconvenient;
- import historical work without recording provenance / supersession;
- treat cleanup as evidence that historical scientific conclusions disappeared.

## Completion standard

For substantive work, leave:

- coherent code or durable evidence;
- tests/adversarial checks appropriate to the failure mode;
- exact branch + HEAD provenance;
- updated current routing only when project state actually changed;
- a clear next legitimate action.
