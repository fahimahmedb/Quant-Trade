# GITHUB BRANCH HYGIENE — 2026-09-21

Purpose: keep GitHub readable without destroying audit/proof history.

Rules:

- ACTIVE branches are the only branches used for current routing/work.
- FROZEN AUTHORITY branches remain reference authorities and should not be edited.
- HISTORICAL branches are evidence/history only; do not restart work from them.
- SUPERSEDED branches must never be used as authority.
- Deleting a branch ref is optional housekeeping only; do not delete proof commits or
  rewrite accepted history.

## ACTIVE

### Coordination

- `blue/master-v2-2026-09-20`

### Rail A

- `builder/gate-b-route1-concrete-mutation-pack-2026-09-21`
- `blue/gate-b-activation-seal-host-relay-2026-09-21`

### Rail B

- `builder/post-p0-first-vertical-shadow-loop-2026-09-21`

Rail-B next branch is not yet created. Expected next work is one bounded independent
Astra review after Blue reception.

## FROZEN / CURRENT REFERENCE AUTHORITIES — KEEP

### P0 / V4

- `blue/p0-gate-a-v4-frozen-2026-09-20`
- `astra/p0-gate-a-v4-independent-audit-2026-09-20`

### Gate-B repository authority

- `blue/gate-b-f11-final-integration-2026-09-21`
- `astra/gate-b-f11-lock-identity-recheck-2026-09-21`
- `blue/gate-b-post-astra-convergence-2026-09-21`
- `builder/gate-b-v4-materialization-activation-prestage-2026-09-21`
- `operator/gate-b-f5-route1-host-evidence-closure-2026-09-21`
- `operator/gate-b-target-host-read-only-rebind-2026-09-21`
- `blue/gate-b-run-reservation-host-relay-preseal-2026-09-21`

### Product / science source authorities

- `parallel/claude-forward-data-2026-09-20`
- `parallel/claude-economic-v2-2026-09-20`
- `parallel/claude-first-slice-cohort-geometry-2026-09-21`
- `parallel/claude-post-p0-vertical-build-prep-2026-09-21`
- `builder/post-p0-vertical-interface-map-2026-09-21`
- `claude/confident-mendel-h4qqo4`

These are reference objects, not active implementation lanes.

## SUPERSEDED / DO NOT USE

The following are known superseded branches:

- `blue/gate-b-run-reservation-activation-preseal-2026-09-21`
  - wrong base for accepted F11 runctl;
  - superseded by `blue/gate-b-run-reservation-host-relay-preseal-2026-09-21`.

- `builder/gate-b-f11-lock-identity-repair-2026-09-21`
  - mission-only/superseded F11 branch;
  - active implementation was `builder/gate-b-lock-path-identity-repair-2026-09-21`.

- `operator/gate-b-f5-route1-host-feasibility-2026-09-21`
  - superseded by the later host-evidence closure branch.

- `blue/checkpoint-gate-a-v2-audit-2026-09-20`
- `astra/checkpoint-gate-a-v2-independent-audit-2026-09-20`
  - checkpoint refs superseded by later Gate-A generations.

These refs may be deleted manually from GitHub after confirming no external automation
depends on the branch name. Their accepted evidence, where relevant, is preserved in
later branches/commits.

## OBVIOUS NON-PROJECT / TEST CLEANUP CANDIDATES

These branch names do not belong to the current Quant mission routing and should not be
used as project authority:

- `codex/test`
- `claude/restaurant-stock-management-mvp-6oq43e`

The branch:

- `claude/nasdaq-trading-model-design-h3mp4n`

is not part of the current two-rail authority and should be treated as historical
research unless explicitly re-promoted by Blue.

## HISTORICAL

All remaining `blue/`, `builder/`, `astra/`, `operator/`, `parallel/`,
`research/`, `reviewer/`, and `recovery/` branches not listed ACTIVE or FROZEN
above are historical evidence only.

They may be retained for audit traceability, but must not be used to infer the current
mission.

## Current restart rule

A fresh session should use only:

1. `QUANT_NORTH_STAR.md`
2. `NEXT_BUILD_MISSION.md`
3. `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`
4. the exact active mission branch after live HEAD/CI verification

Do not browse the branch list and guess the active mission from branch names.
