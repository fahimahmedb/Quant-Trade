# Quant-Trade — current canonical project state

STATUS=`TWO_BRANCH_CONVERGENCE_QUALIFIED_CLEANUP_PENDING`
DATE=`2026-10-31`

## Canonical destinations

- CODE: `code/canonical`
- PROJECT/GOVERNANCE: `project/canonical`

No other branch is authoritative for new work once cleanup completes.

## Code state

Wave2 C2 base: `ebc72b9fd14f91420c37e0b7607f9bfb584a289a`.

Qualified canonical code head:
`fd3f8ce77d3a2f20cc5954c184c4487b44dac1d3`.

Exact-head canonical qualification:
- workflow: `Canonical Code Qualification`
- run: `41216401503`
- conclusion: `SUCCESS`
- all observed steps PASS: exact-head identity, compile, CP099 carried-hardening regressions, PR46 autonomy regressions, Wave2 non-regression sample, closed authority, clean checkout.

The preceding combined head `2b7e3d77b4fe36e1720fe0a8b4620f91eee32132` failed run `41216294343` because the CP099 source manifest taxonomies were incompatible with Wave2 `legacy.py`. Repair restored exact Wave2 manifest blob `50e4e9088b9ce68336cf2ca34fd02882af44ea5e` rather than importing the conflicting validator.

Included selectively:
- CP099 non-conflicting V2 hardening spine: `v2_core`, `v2_pipeline`, `v2_stage_executor`;
- PR46 autonomy delta: `gpt_oss_orchestrator`, `codex_adapter`, `codex_policy` and focused tests;
- exact CP099 regression tests for carried hardenings.

Direct CP099 wholesale merge was rejected: PR #47 conflicted and was closed without merge.

## Project memory

Forensic reconstruction is complete for convergence. Do not restart global archaeology.
Historical evidence remains under `governance/forensic-20261031/` and Git history.
Legacy open PRs have been closed; their commits remain evidence, not active integration lanes.

## Authority

`ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE`
`PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE`
`REAL_CAPITAL_AUTHORIZED=FALSE`
`LIVE_TRADING_AUTHORIZED=FALSE`

Repository cleanup to the two canonical branches is Owner-authorized and does not widen those scientific/economic authorities.

## Current claim ceiling

`ENGINEERING_CODE_CANDIDATE_QUALIFIED=TRUE`.
Actual VM `GPT-OSS -> Codex -> GPT-OSS` multi-wake autonomy remains `NOT_PROVEN`; CI does not establish deployment or runtime use.

## Next action

Preserve all legacy branch tips in the project history anchor, switch the repository default to `code/canonical`, retire all non-canonical branch refs, verify exactly two branches remain, then publish the final handoff.
