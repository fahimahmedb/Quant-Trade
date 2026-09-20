# CURRENT GOVERNANCE STATE — 2026-09-20

Purpose: compact current-governance index for Quant. This is a routing/index document, not a replacement for the authorities it cites.

## 0. Authority precedence

1. `QUANT_NORTH_STAR.md` — highest architecture/product authority unless explicitly revised by owner.
2. Current Blue durable governance — `blue/master-v2-2026-09-20`, especially `handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`.
3. Exact frozen candidates, contracts, independent audits and hash-addressable evidence relevant to the active decision.
4. Historical branches, checkpoints and chat summaries.

When two sources conflict, later committed durable evidence at the correct authority level wins. Do not transfer proof silently across SHAs.

## 1. Roles

`BLUE / MISSION CONTROL`
- owns project-level decisions;
- decides gates, specifications, integration, deployment progression and capital authorization;
- does not self-certify a Builder correction as independent evidence.

`BUILDER`
- implements a Blue-approved specification;
- stops after durable delivery/handoff;
- does not independently certify its own fix.

`ASTRA / RED TEAM`
- independently attacks/reproduces;
- does not start from Blue's desired conclusion;
- classifies REAL_DEFECT / TEST_DEFECT / MISSING_PROOF / TARGET_HOST_ONLY / NON_ISSUE;
- does not modify the audited production candidate while acting as independent auditor.

General flow:
`finding/challenge → Blue decision → specification → Builder → independent review → Blue decision`.

## 2. Current program state

`CURRENT_BLUE_OWNER = blue/master-v2-2026-09-20`

Resolve live HEAD rather than copying a stale self-reference.

`GATE_A_V3_REPOSITORY_DISPOSITION = PASS`

Frozen candidate:
`blue/p0-gate-a-v3-frozen-2026-09-20@2da079d8ad75c69eb3fc2990c512735cb4bdc02b`

Independent final audit:
`astra/p0-gate-a-v3-independent-audit-2026-09-20@33995d03c8632e5c3a7b77a12b87366fb06b4d30`

Astra exact-head CI:
`35517935710 = COMPLETED / SUCCESS`

Blue final disposition:
`handoff/BLUE_GATE_A_V3_FINAL_DISPOSITION_2026-09-20.md`

## 3. Current safety/gate state

`t0 = NOT DECLARED`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

`TARGET_HOST_READY = FALSE / NOT_YET_QUALIFIED`

`GATE_B = NOT_STARTED`

`REAL_CAPITAL_AUTHORIZED = FALSE`

`PRODUCT_INTEGRATION = PAUSED`

Gate A PASS must not be promoted into any stronger statement above.

## 4. Active mission

`MISSION = TARGET-HOST QUALIFICATION / FINAL RODAGE ENTRANCE`

`STATUS = READY_TO_DISPATCH / NOT_EXECUTED`

Mission handoff:
`handoff/BLUE_TARGET_HOST_QUALIFICATION_MISSION_2026-09-20.md`

Entrance contract:
`governance/TARGET_HOST_RODAGE_ENTRANCE_CONTRACT_2026-09-20.md`

Execution runbook:
`governance/TARGET_HOST_P0_RODAGE_RUNBOOK_2026-09-20.md`

Only an operator/agent with real target-host access may claim target-host execution evidence.

Repository-only work may prepare/check specifications but must not claim host proof.

## 5. Gate A residuals carried forward

Disabled-lane direct-poll observation:
`NON_BLOCKING_DESIGN_OBSERVATION_FOR_GATE_A`

Fingerprint/service-manager/invocation pre-seeding concern:
`MISSING_PROOF / TARGET_HOST_ENTRANCE_CONCERN`

Mandatory target-host falsifier:
if unauthorized pre-seeding can occur and the later qualifying audit still reaches `accountable=True`:
`REAL_DEFECT / REOPEN_GATE_A = TRUE`.

## 6. Cleanup governance

Open PRs:
`0`

Current branch inventory:
`71`

Single operational deletion authority:
`governance/BRANCH_DELETE_READY_INDEX_2026-09-20.md`

Current verified delete-ready state:
- refs = 35;
- exact pinned SHA matches = 35/35;
- unprotected = 35/35;
- physical deletions executed = 0.

Deletion must use a true branch-delete/delete-ref operation. Never emulate deletion by moving refs.

Divergent falsifier/audit refs and unique Product/recovery/learning/design refs remain preserved until separate retirement decisions.

## 7. Default branch governance

Current repository default:
`claude/nasdaq-trading-model-design-h3mp4n@8fea558143d0c46bc6eeb9f2aa57527b4e6c1fce`

It is stale and non-authoritative.

Review:
`governance/DEFAULT_BRANCH_MIGRATION_REVIEW_2026-09-20.md`

`DEFAULT_BRANCH_REVIEW = COMPLETE`

`DEFAULT_BRANCH_MIGRATION_EXECUTED = FALSE`

Proposed interim default:
`blue/master-v2-2026-09-20`

Migration must use an actual repository-admin default-branch mutation and be verified afterward. Do not emulate it with ref movement.

## 8. Product authorities — paused

Canonical Forward:
`parallel/claude-forward-data-2026-09-20@83521dbfdd90027c90d04adfb7d814593c2355c5`

Canonical Economic:
`parallel/claude-economic-v2-2026-09-20@35dff27b8fac53618da434ee6d31febbddcc0e69`

Product integration topology reference:
`blue/integration-readiness-2026-09-20`

These are not active integration authority while `PRODUCT_INTEGRATION = PAUSED`.

Preserve unique Product capabilities until explicit mapping decisions:
- Evidence/PIT identity;
- Research Factory core;
- product-side SEC census;
- relevant Forward recorder/live-smoke semantics;
- alternate Economic evidence until semantic supersession is recorded.

## 9. Scientific/economic governance

The terminal objective remains real long-run net wealth growth after real frictions.

Scientific validity, target-host continuity, economic readiness and capital authorization are distinct proof domains.

A green CI is execution evidence only.

`NO_TRADE` may be economically optimal.

No strategy, model, feature, risk metric, activity level, agent count or code volume is itself a terminal success criterion.

## 10. What the next conversation should do

First:
- read North Star;
- read Blue Master state;
- read this index;
- verify live Blue HEAD and current repository deltas.

Then:
- continue target-host qualification when real host access exists;
- otherwise continue non-destructive governance/cleanup work;
- do not reopen Gate A without new contradictory evidence;
- do not start Product integration without explicit Blue decision;
- do not declare t0, P14D proof, Gate B completion or capital authorization by implication.

## 11. Current governance verdict

`GOVERNANCE_AUTHORITY = CLEAR`

`DURABLE_MEMORY = ESTABLISHED`

`ROLE_SEPARATION = ESTABLISHED`

`GATE_DISCIPLINE = ESTABLISHED`

`BRANCH_CLEANUP = PREPARED / PHYSICAL_DELETE_PENDING_TOOLING`

`DEFAULT_BRANCH_MIGRATION = REVIEWED / NOT_EXECUTED`

`ACTIVE_FRONTIER = TARGET_HOST_QUALIFICATION`
