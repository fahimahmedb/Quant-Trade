# CP4 — ChatGPT handoff after Codex quota exhaustion

Recorded on 2026-10-20 after Codex/Work quota exhaustion.

## Canonical branch

`builder/oracle-economic-loop-recovery-20261019`

Observed branch HEAD before this checkpoint:
`8ababd83f7020cb123d8b939549c6afcf872ba13`

That HEAD is an autonomous Research OS commit for:
`legacy_duplicate_check FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003-g1-436763aa9a09`.

## Verified completed evidence

1. Native Oracle service-user canary is already durable in GitHub.
2. Manual claim expiration/recovery completed without duplicate stage execution.
3. Timer activation happened and an actual scheduled wake created the canonical task
   `FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003`.
4. Historical frontier derivation metadata was normalized without changing prior results.
5. The first durable automatic wake is already checkpointed in
   `research/research_os/runtime/CP3_AUTOMATIC_GITHUB_WAKE_20261020.json`.
6. The Ubuntu 24.04 Git maintenance compatibility fix exists at
   `f3943830e20b05d926d3013501573b8b21fdace7`.
7. Oracle Economic Loop Recovery CI for that fix was observed SUCCESS.
8. The SEC P0 pre-t0 gate for that same SHA was still `in_progress` when this handoff was written;
   do not infer success until GitHub reports a terminal successful conclusion.

## Current durable task state observed

Task: `research/research_os/tasks/FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003.json`

Observed state before this checkpoint:

- status: `READY`
- lease generation: `1`
- completed stage: `legacy_duplicate_check`
- last receipt: `research/research_os/receipts/FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003/FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003-g1-436763aa9a09.json`
- operational release SHA recorded by the worker: `f138c980c94eea313fd77532c20857da5c02d3fe`

All authority remains closed:

- `economic_experiment_authorized = false`
- `prospective_observation_authorized = false`
- `real_capital_authorized = false`
- `live_trading_authorized = false`

## What is NOT yet proven

Do not mark Oracle Lab V1 fully qualified yet.

Remaining proof chain:

1. Confirm the SEC P0 pre-t0 gate for `f3943830e20b05d926d3013501573b8b21fdace7` reaches SUCCESS.
2. Install/update the Oracle VM to the Git-compatible fix if the running deployment still uses the older pinned release.
3. Perform an actual VM reboot.
4. Prove after cold boot that:
   - `quant-local-model.service` returns healthy,
   - the research timer/service is enabled and resumes automatically,
   - GPT-OSS local inference succeeds,
   - the worker reads fresh GitHub canonical state,
   - the existing task resumes or progresses without duplicated lineage/stages/receipts.
5. Bind post-reboot journald/systemd evidence to the corresponding GitHub transaction.
6. Persist a final V1 operational receipt/checkpoint only after all of the above pass.

## Handoff rule for Codex / next agent

Reacquire from GitHub, not from conversational memory.

Before any mutation:

1. fetch the live branch HEAD;
2. read CP3 native canary + CP3 automatic wake + this CP4 handoff;
3. read the current task JSON and its last receipt;
4. inspect workflow conclusions for the latest code SHA;
5. check whether autonomous Oracle commits advanced the branch after this checkpoint.

Do not rewrite or reset autonomous durable state. Do not force-push the branch. Use fresh-head / lease-aware updates.

## Checkpoint discipline going forward

At every major stage, create one durable checkpoint under
`research/research_os/runtime/` containing:

- input HEAD,
- code/deployment SHA,
- exact evidence obtained,
- task/lease state,
- authority flags,
- unresolved blockers,
- exact next gate,
- explicit distinction between CI evidence and actual Oracle runtime evidence.

A checkpoint is not permission to open economic, prospective, capital, or live-trading authority.
