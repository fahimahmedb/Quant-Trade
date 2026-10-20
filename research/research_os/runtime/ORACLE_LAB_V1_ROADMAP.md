# Oracle Lab V1 — Canonical Roadmap

Status source for the Oracle H24 V1 qualification and handoff.

**Rule:** this file is the living roadmap. Update it only after verified evidence. Do not replace runtime proof with assumptions. Read fresh GitHub HEAD before every intervention because the Oracle timer may advance durable state autonomously.

## Branch and deployment identity

- Working branch: `builder/oracle-economic-loop-recovery-20261019`
- Current operational release still observed in live task state: `f138c980c94eea313fd77532c20857da5c02d3fe`
- Required repair release before cold reboot: `f3943830e20b05d926d3013501573b8b21fdace7`
- CP4 handoff: `research/research_os/runtime/CP4_CHATGPT_HANDOFF_20261020.md`
- CP5 R1/R2 checkpoint: `research/research_os/runtime/CP5_R1_R2_PRE_REBOOT_20261020.md`

## Permanent safety invariants

The following remain CLOSED unless explicitly authorized by the Owner in a future governed phase:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

V1 qualification must not silently open any of these authorities.

## Project-management execution doctrine

ChatGPT acts as project lead for this qualification. The optimization target is **maximum verified progress per intervention**, not maximum number of tasks, agents, branches, prompts, or checkpoints.

1. Prefer one large coherent work package over many small subtasks when dependencies can safely be handled in one pass.
2. Do not split work merely to parallelize it. Split only when work is genuinely independent and integration cost is lower than the expected wall-clock gain.
3. Before asking the Owner to run commands, batch everything safely executable together into the smallest practical number of bounded commands.
4. Delegate to another AI only substantial packages with exact branch/base SHA, scope, files, invariants, evidence, forbidden actions, acceptance tests, required output, and checkpoint format.
5. External AI output is advisory until reconciled against fresh GitHub state and required runtime evidence.
6. Avoid serial micro-checkpoints. Checkpoint meaningful proof, release/deployment, failure/handoff, or architectural boundaries.
7. Continue all independent GitHub/code/documentation work before escalating an unavailable host/OCI action to the Owner.
8. Every large package must leave the repository easier for Codex or another agent to reacquire.

Default delegation test: **if explaining, supervising, reviewing and integrating delegated work is likely to cost as much as doing it directly, do it directly.**

## Evidence already acquired

### CP3 — native canary / crash recovery

- [x] Host preparation completed.
- [x] Local GPT-OSS service proven enabled/running.
- [x] Canonical service-user canary completed.
- [x] `PASS_PRE_ACTIVATION` with all 13 gates true.
- [x] Real claim persisted to GitHub.
- [x] Process deliberately stopped after claim.
- [x] Expired lease recovered by fresh worker instances.
- [x] Recovery completed without duplicate lineage/stages/receipts.
- [x] Local inference used; hosted model calls remained zero.
- [x] 20-record Legacy ledger and 13 frozen hypotheses loaded in the proven canary.
- [x] Four authority flags remained false.

Canonical evidence: `research/research_os/runtime/CP3_NATIVE_GITHUB_CANARY_20261020.md`.

### CP3 — automatic wake

- [x] Timer activated.
- [x] Native automatic scheduled wake produced a durable GitHub transaction.
- [x] Canonical queue refill created `FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003`.
- [x] Historical frontier metadata normalization repaired an identifier collision without changing historical results.
- [x] Automatic wake checkpointed as `DURABLE_AUTOMATIC_WAKE_PROVEN_VM_REBOOT_PENDING`.

Canonical evidence: `research/research_os/runtime/CP3_AUTOMATIC_GITHUB_WAKE_20261020.json`.

### Current durable research state — last verified before CP5

Task: `FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003`

- status: `READY`
- lease generation: `2`
- completed stages: `legacy_duplicate_check`, `document_or_fundamental_research`
- generation-2 claim commit: `8945589e5b9fc9cb7de2550aa154a06431efd535`
- generation-2 research-stage commit: `255b4e0e865620c8c26f2e6ace630221c3278279`
- execution release: `f138c980c94eea313fd77532c20857da5c02d3fe`
- four authority flags: all false

The Oracle timer may advance this state after this document is written. Always reacquire fresh HEAD/task/receipts before acting.

## V1 roadmap

### R1 — Final CI disposition for Git compatibility fix — CLOSED PASS

Repair SHA: `f3943830e20b05d926d3013501573b8b21fdace7`.

- [x] Oracle Economic Loop Recovery CI run `39346723653`: SUCCESS.
- [x] `cp1-static-and-regression` job: SUCCESS.
- [x] SEC P0 pre-t0 gate run `39346723807`: SUCCESS.
- [x] `gate` job including full unit suite, SEC P0 lane suite and V1 end-to-end regression: SUCCESS.
- [x] Exact-head repair is CI-approved for the next host gate.

Canonical checkpoint: `research/research_os/runtime/CP5_R1_R2_PRE_REBOOT_20261020.md`.

### R2 — Host release reconciliation — DECISION CLOSED / EXECUTION PENDING

Goal: move the runtime from known-defective `f138c980...` to repaired `f394383...` before reboot qualification.

- [x] Fresh branch HEAD reacquired before CP5.
- [x] Current task/receipt progression reacquired.
- [x] Running worker still reports release `f138c980...`.
- [x] Deployment decision: `f394383...` is required before reboot qualification.
- [x] Reason recorded: Ubuntu 24.04 Git 2.43 rejects `git gc --no-detach`; old release can publish a transition then fail in maintenance.
- [ ] Install exact `f394383...` via bounded Owner/root preparation.
- [ ] Run repaired-release live canary and require `PASS_PRE_ACTIVATION`.
- [ ] Reactivate timer only after matching canary.
- [ ] Verify repaired release, local model service and timer on the VM.
- [ ] Capture pre-reboot boot identity and runtime state.

Do not qualify reboot resilience on `f138c980...`.

### R3 — Real VM cold reboot

Goal: prove host recovery rather than process-only recovery.

- [ ] Capture pre-reboot state: HEAD, task, timer/service state, relevant receipt and boot identity.
- [ ] Perform an actual VM reboot.
- [ ] Verify a new boot occurred.
- [ ] Verify `quant-local-model.service` returns enabled/active.
- [ ] Verify GPT-OSS loopback health and one bounded local inference after cold start.
- [ ] Verify research timer returns enabled/active without manual wake substitution.

Exit criterion: services recover from a genuine reboot without manual reconstruction of canonical research state.

### R4 — Natural post-reboot autonomous wake

Goal: prove the lab resumes work from GitHub after reboot.

- [ ] Do not use a manual wake as substitute evidence.
- [ ] Observe the next scheduled systemd invocation.
- [ ] Link journald/systemd invocation to a fresh GitHub transaction.
- [ ] Confirm fresh GitHub HEAD/state was read after boot.
- [ ] Confirm the durable task resumes or transitions correctly.
- [ ] Confirm no duplicate task lineage, stage, receipt, candidate, or freeze is produced.
- [ ] Confirm four authorities remain false.

Exit criterion: one natural post-reboot wake performs a valid durable transition or justified no-op/retry, with traceable systemd -> GitHub -> receipt evidence.

### R5 — V1 final operational receipt

Goal: close V1 without overstating scientific capability.

- [ ] Produce final V1 operational checkpoint/receipt.
- [ ] Bind exact deployment SHA, boot/reboot evidence, systemd timer evidence, local-model evidence, GitHub transition, task/receipt IDs, CI references and authority flags.
- [ ] State explicitly what V1 proves and does not prove.
- [ ] Only then classify Oracle H24 V1 operational status.

Required distinction:

- V1 may prove autonomous scheduling, durable GitHub state, local inference, claim/recovery, and reboot resilience.
- V1 does **not** by itself prove that every M3 research engine is scientifically complete.
- Forward Farm remains closed while prospective observation is unauthorized.
- Economic experimentation, real capital, and live trading remain closed.
- Live Lab native ingress/UI integration remains a separate unfinished surface unless later proven.

## After V1 — V2 planning, not execution yet

Once R1-R5 are closed, create a separate V2 specification before broadening scope.

V2 design topics:

1. scientific depth/completeness of M3 workers: Quant, Fundamental, Event/Documents, Institutional/Forced Flows, Validator;
2. explicit research-engine test specifications and falsification criteria;
3. deployment/upgrade procedure for Oracle releases;
4. stronger restart/idempotency/lease fault injection;
5. Portfolio Map evidence boundaries and empirical-correlation rules;
6. Live Lab native event ingress and UI proof;
7. Forward Farm only if separately authorized;
8. economic experiment path only if separately authorized;
9. continued prohibition on real capital/live trading unless explicitly authorized.

## Checkpoint discipline

At every major verified milestone:

1. reacquire fresh branch HEAD;
2. verify current task/receipts/artifacts rather than relying on chat memory;
3. create/update a durable checkpoint under `research/research_os/runtime/`;
4. update this roadmap in the same milestone window;
5. include exact SHA(s), evidence paths, status, failures/unknowns, next gate and all authority flags;
6. never claim a runtime result from GitHub-only evidence;
7. never force-push/reset over autonomous Oracle commits;
8. if concurrent Oracle activity advances HEAD, reacquire before any write.

## Reacquisition protocol for Codex / another agent

Read in this order:

1. fresh branch HEAD for `builder/oracle-economic-loop-recovery-20261019`;
2. this roadmap;
3. `research/research_os/runtime/CP5_R1_R2_PRE_REBOOT_20261020.md`;
4. `research/research_os/runtime/CP4_CHATGPT_HANDOFF_20261020.md`;
5. `research/research_os/runtime/CP3_NATIVE_GITHUB_CANARY_20261020.md`;
6. `research/research_os/runtime/CP3_AUTOMATIC_GITHUB_WAKE_20261020.json`;
7. current task `FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003` if not superseded;
8. newest linked receipts/artifacts/events;
9. only then decide the next action from R2-R5.

Do not restart earlier canaries unless later code/deployment changes materially invalidate the proven property.

---

Initialized 2026-10-20 (Europe/Paris) after Codex quota exhaustion. Updated through CP5 R1/R2 decision.