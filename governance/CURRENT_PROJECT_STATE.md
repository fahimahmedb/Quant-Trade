# Quant-Trade — current canonical project state

STATUS=`CANONICAL_PAIR_ACTIVE_BRANCH_RETIREMENT_PARKED`
DATE=`2026-10-31`

## Canonical authority

- CODE AUTHORITY: `code/canonical`
- PROJECT / GOVERNANCE AUTHORITY: `project/canonical`

These are the only branches authorized for new canonical work.
Legacy branches remain preserved as historical evidence until a later explicit Owner decision retires them.

`BRANCH_DELETION_AUTHORIZED=FALSE`
`BRANCH_RETIREMENT=PARK`

The repository default branch is still `blue/master-v2-2026-09-20` because the GitHub integration could not rename the default branch (`403 Resource not accessible by integration`). This does NOT restore engineering authority to that branch.

## Code state

Wave2 C2 base: `ebc72b9fd14f91420c37e0b7607f9bfb584a289a`.

Qualified canonical code head:
`fd3f8ce77d3a2f20cc5954c184c4487b44dac1d3`.

Exact-head canonical qualification:
- workflow: `Canonical Code Qualification`
- run: `41216401503`
- conclusion: `SUCCESS`
- exact-head identity: PASS
- compile integrated deltas: PASS
- CP099 carried-hardening regressions: PASS
- PR46 autonomy regressions: PASS
- Wave2 non-regression sample: PASS
- closed authority: PASS
- clean checkout: PASS

Challenge evidence retained:
- preceding head `2b7e3d77b4fe36e1720fe0a8b4620f91eee32132`
- run `41216294343`
- result: FAILURE
- cause: CP099 `legacy/source_manifest.json` taxonomy incompatible with Wave2 `legacy.py`
- correction: restore exact Wave2-compatible manifest blob `50e4e9088b9ce68336cf2ca34fd02882af44ea5e`
- corrected head: `fd3f8ce77d3a2f20cc5954c184c4487b44dac1d3`
- corrected run: `41216401503` SUCCESS

Included selectively:
- CP099 non-conflicting V2 hardening spine: `v2_core`, `v2_pipeline`, `v2_stage_executor`;
- PR46 autonomy delta: `gpt_oss_orchestrator`, `codex_adapter`, `codex_policy` and focused tests;
- exact CP099 regression tests for carried hardenings.

Direct CP099 wholesale merge was rejected: PR #47 conflicted and was closed without merge.

## Project memory

Forensic reconstruction is complete for convergence. Do not restart global archaeology.
Historical evidence remains under `governance/forensic-20261031/`, closed PRs, and Git history.
Legacy open PRs were closed; their commits remain evidence, not active integration lanes.

The attempted final cleanup workflow run `41216737420` failed before branch deletion. It preserved branch-tip evidence, then hit a GitHub permission failure while trying to rename the default branch. No mass branch deletion occurred.

A failed rollback left the qualified code ref temporarily named `code/canonical-qualified-tmp`; `code/canonical` was then recreated directly at the already-qualified SHA `fd3f8ce77d3a2f20cc5954c184c4487b44dac1d3`. The temporary branch is deliberately NOT deleted under the Owner PARK decision.

The destructive cleanup workflow is now parked and read-only. It cannot delete or rename branches unless explicitly rewritten in a future Owner-authorized mission.

## Authority

`ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE`
`PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE`
`REAL_CAPITAL_AUTHORIZED=FALSE`
`LIVE_TRADING_AUTHORIZED=FALSE`

## Current claim ceiling

`ENGINEERING_CODE_CANDIDATE_QUALIFIED=TRUE`.
`CANONICAL_PROJECT_AUTHORITY_ESTABLISHED=TRUE`.
`LEGACY_BRANCHES_RETIRED=FALSE`.
`DEFAULT_BRANCH_SWITCHED=FALSE`.

Actual VM `GPT-OSS -> Codex -> GPT-OSS` multi-wake autonomy remains `NOT_PROVEN`; CI does not establish deployment or runtime use.

## Next action

Continue project work only through `code/canonical` and `project/canonical`.
Do not delete, rename, or retire legacy branches until a new explicit Owner instruction authorizes that cleanup.
