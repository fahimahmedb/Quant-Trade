# Quant-Trade — current canonical project state

STATUS=`TWO_BRANCH_CONVERGENCE_IN_PROGRESS`
DATE=`2026-10-31`

## Canonical destinations

- CODE: `code/canonical`
- PROJECT/GOVERNANCE: `project/canonical`

No other branch is authoritative for new work once convergence completes.

## Code state

Wave2 C2 base: `ebc72b9fd14f91420c37e0b7607f9bfb584a289a`.

Current code candidate head after selective ports and canonical qualification workflow creation:
`2b7e3d77b4fe36e1720fe0a8b4620f91eee32132`.

Included selectively:
- non-conflicting CP099 hardening spine (`v2_core`, `v2_pipeline`, `v2_stage_executor`, legacy source manifest);
- PR46 autonomy delta (`gpt_oss_orchestrator`, `codex_adapter`, `codex_policy` and focused tests);
- exact CP099 regression tests for the carried hardenings.

Direct CP099 wholesale merge is rejected: PR #47 is conflicting / not mergeable.

## Project memory

Forensic reconstruction is complete for convergence. Do not restart global archaeology.
Historical evidence remains under `governance/forensic-20261031/` and Git history.

## Authority

`ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE`
`PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE`
`REAL_CAPITAL_AUTHORIZED=FALSE`
`LIVE_TRADING_AUTHORIZED=FALSE`

## Current claim ceiling

The code candidate is an engineering convergence candidate. It is not production/live/scientific authority. Actual VM GPT-OSS -> Codex -> GPT-OSS multi-wake autonomy is not proven until a runtime receipt exists.

## Next action

Complete exact-head canonical code qualification, repair only demonstrated failures, then freeze the two canonical branches and retire legacy branches after preserving necessary evidence/data reachability.
