# Current Build / Mission Router

This file is intentionally a router, not a frozen mission specification.

Do not infer the active task from historical content at this path.

## Current restart order

Read:

1. `QUANT_NORTH_STAR.md`
2. `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`
3. `handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`
4. `handoff/BLUE_CONTEXT_REACQUISITION_2026-09-21.md`
5. `governance/BLUE_REPOSITORY_HYGIENE_AUDIT_2026-09-21.md`
6. `governance/BRANCH_AUTHORITY_REGISTRY_2026-09-21.md`
7. the exact active mission/handoff.

Resolve the live HEAD of `blue/master-v2-2026-09-20` before acting.

## Current routing at last update

Frozen V4 production candidate:

`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

V4 repository disposition:

`GATE_A_V4_REPOSITORY_DISPOSITION = PASS`

Final independent hybrid fault-matrix review:

`ASTRA_FAULT_MATRIX = BLOCKED_MISSING_PROOF`

Unresolved row:

`restart_burst_limit`

Production REAL_DEFECT:

`0`

Active Builder proof-only repair:

`builder/codex-p0-hybrid-restart-burst-proof-fix-2026-09-21`

Prepared mission SHA:

`6f0ca1d858d6937dc8199cc1690dce049ddb79a6`

Blue acceptance oracle:

`EXPECTED_RESTART_BURST_LIMIT = 5`

Mandatory RED mutations:
- launcher 5 -> 4;
- unit 5 -> 4;
- launcher + unit 5 -> 4 simultaneously.

After Builder delivery:
Blue reception -> targeted Astra recheck -> Blue final fault-matrix disposition
-> final consistency review -> possible hybrid-method promotion.

Do not use the known-bad replay branch as the repair base.

## Repository hygiene

Repository default:
`blue/master-v2-2026-09-20`.

Live branches:
`45`.

Open PRs/issues:
`0 / 0`.

Previous delete batch:
`34 / 34 COMPLETE`.

Deleted refs reappeared:
`0`.

No new branch deletion is currently authorized.

## Safety state

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

`P14D_PROMOTION_READY = FALSE`

`TARGET_HOST_READY = FALSE`

`GATE_B_MUTATION_AUTHORIZED = FALSE`

`GATE_B = NOT_STARTED`

`t0 = NOT_DECLARED`

`PRODUCT_INTEGRATION = PAUSED`

`REAL_CAPITAL_AUTHORIZED = FALSE`

This router is not proof that a branch, CI run, candidate or gate is current.
The current governance index and exact GitHub state control.
