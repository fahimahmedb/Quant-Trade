# Oracle Lab V1 — Canonical Roadmap

Status source for the Oracle H24 V1 qualification and handoff.

**Rule:** this file is the living roadmap. Update it only after verified evidence. Do not replace runtime proof with assumptions. Read fresh GitHub HEAD before every intervention because the Oracle timer may advance durable state autonomously.

## Branch and deployment identity

- Working branch: `builder/oracle-economic-loop-recovery-20261019`
- Qualified operational release: `f3943830e20b05d926d3013501573b8b21fdace7`
- Previous release superseded for qualification: `f138c980c94eea313fd77532c20857da5c02d3fe`
- CP4 handoff: `research/research_os/runtime/CP4_CHATGPT_HANDOFF_20261020.md`
- CP5 R1/R2 checkpoint: `research/research_os/runtime/CP5_R1_R2_PRE_REBOOT_20261020.md`
- Repaired-release live canary artifact: `research/research_os/artifacts/AAA-ORACLE-H24-CANARY-f3943830e20b05d9/qualification-5f9807e6bd84fc5a.json`

## Permanent safety invariants

The following remain CLOSED unless explicitly authorized by the Owner in a future governed phase:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

V1 qualification did not open any of these authorities.

## Project-management execution doctrine

ChatGPT acts as project lead for this qualification. The optimization target is **maximum verified progress per intervention**, not maximum number of tasks, agents, branches, prompts, or checkpoints.

1. Prefer one large coherent work package over many small subtasks when dependencies can safely be handled in one pass.
2. Split only when work is genuinely independent and wall-clock gain exceeds coordination cost.
3. Batch Owner commands into the smallest practical bounded intervention.
4. Delegate to another AI only substantial packages with exact branch/base SHA, scope, surfaces, invariants, evidence, forbidden actions, acceptance tests, output and handoff format.
5. External AI output is advisory until reconciled against fresh GitHub state and required runtime evidence.
6. Avoid serial micro-checkpoints; checkpoint meaningful proof, deployment, failure/handoff or architectural boundaries.
7. Continue all independent GitHub/code/documentation work before escalating unavailable host actions.
8. Every large package should leave the repository easier for the next agent to reacquire.

Default delegation test: **if explaining, supervising, reviewing and integrating delegated work is likely to cost as much as doing it directly, do it directly.**

## Evidence acquired

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

### Repaired-release live canary

Release: `f3943830e20b05d926d3013501573b8b21fdace7`

GitHub evidence commit: `623864e707871d2e1f6d8a7ce9db5774129b9a3f`.

Measured result:

- [x] `PASS_PRE_ACTIVATION`
- [x] all 13 gates true
- [x] exact-release CI success
- [x] local GPT-OSS health and structured inference
- [x] crash-after-claim / expired-lease recovery
- [x] two successive wakes
- [x] no duplicate artifacts
- [x] GitHub receipts verified
- [x] hosted model calls = 0
- [x] scheduler disabled during canary as required
- [x] four authority flags false

Model output from the canary remains `UNVERIFIED_MODEL_COMMENTARY`; generated commentary is not evidence or authority.

### Current durable research state after repaired-release reboot wake

Task: `FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003`

- status after generation 4 completion: `READY`
- generation: `4`
- release: `f3943830e20b05d926d3013501573b8b21fdace7`
- completed stages include `legacy_duplicate_check`, `document_or_fundamental_research`, `disconfirmation`, `freeze_hypothesis`
- generation-4 claim commit: `51ab3674962b6f920eab4e3b61335fa294d64c11`
- generation-4 completion commit: `c840e4837af985deba70c1eb59b5e2a0f4a91273`
- generation-4 receipt: `research/research_os/receipts/FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003/FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003-g4-a3b030c9452e.json`
- frozen hypothesis: `research/research_os/hypotheses/DOC-FUND-9219d7f488ada3c2.json`
- economic result remains `NOT_OBSERVED`
- outcome access remains false
- four authority flags remain false

The timer may advance this state after this document is written. Always reacquire fresh HEAD/task/receipts before acting.

## V1 roadmap

### R1 — Final CI disposition for Git compatibility fix — CLOSED PASS

Repair SHA: `f3943830e20b05d926d3013501573b8b21fdace7`.

- [x] Oracle Economic Loop Recovery CI run `39346723653`: SUCCESS.
- [x] `cp1-static-and-regression` job: SUCCESS.
- [x] SEC P0 pre-t0 gate run `39346723807`: SUCCESS.
- [x] full unit, SEC P0 and V1 end-to-end regression gates: SUCCESS.
- [x] exact-head repair approved for host qualification.

### R2 — Host release reconciliation — CLOSED PASS

- [x] Identified Git 2.43 incompatibility in old release maintenance path.
- [x] Installed exact repaired release `f394383...`.
- [x] Host preparation returned `HOST_PREPARED_TIMER_NOT_ACTIVATED` before canary.
- [x] Repaired-release live canary reached `PASS_PRE_ACTIVATION` with all 13 gates true.
- [x] Timer was activated only after the matching canary.
- [x] Pre-reboot hard gate verified release/model/timer state before the reboot.

### R3 — Real VM cold reboot — CLOSED PASS

Owner-captured bounded proof completed `2026-10-20T00:56:12.725302+00:00`.

- [x] Actual VM reboot performed.
- [x] Boot identity changed from `289d8c8b-d312-482b-9126-49deb61f2751` to `79a29c0f-c7cd-4cd2-885c-9e4c18e123b6`.
- [x] Current release after reboot resolved to `/opt/quant-research/releases/f3943830e20b05d926d3013501573b8b21fdace7`.
- [x] `quant-local-model.service`: enabled + active.
- [x] GPT-OSS health: PASS, local-only, model `gpt-oss-10.2b-q4-k-m`, runtime `openai_compatible`.
- [x] One bounded local inference succeeded after cold boot; hosted model calls remained zero.
- [x] Research timer returned enabled + active without manual reconstruction.

Exit criterion met: services recovered from a genuine reboot without reconstruction of canonical research state.

### R4 — Natural post-reboot autonomous wake — CLOSED PASS

Measured natural systemd worker interval:

- start: `2026-10-20 00:50:17 UTC`
- exit: `2026-10-20 00:52:15 UTC`
- result: `success`
- exit status: `0`
- manual worker start used: `false`

Within that same interval:

- [x] generation-4 claim commit `51ab3674...` emitted at `00:51:14Z`.
- [x] generation-4 `freeze_hypothesis` completion commit `c840e483...` emitted at `00:51:31Z`.
- [x] both identify release `f394383...` and session `FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003-g4-a3b030c9452e`.
- [x] completion input head is the claim commit, forming a direct durable claim -> completion chain.
- [x] matching receipt persisted and task returned to `READY`.
- [x] exactly one generation-4 freeze stage / matching receipt is present in the observed task state.
- [x] final worker-observed GitHub ref was `c840e4837af985deba70c1eb59b5e2a0f4a91273`.
- [x] four authority flags remained false.

Important interpretation: the post-reboot observer reported the same `c840e483...` HEAD before/after its own observation window because the durable transition had already landed by the time it sampled the branch. R4 is therefore grounded in the measured systemd interval plus the in-window GitHub timestamps, matching release/session/worker identity, direct commit chain and receipt—not in a claimed HEAD delta inside the later observer window.

Exit criterion met: a natural post-reboot systemd wake performed a valid durable transition with traceable systemd -> GitHub -> receipt evidence.

### R5 — V1 final operational disposition — CLOSED PASS

Classification:

`ORACLE_H24_V1_OPERATIONALLY_QUALIFIED`

V1 proves for the qualified release and observed host configuration:

- autonomous scheduling by systemd;
- durable GitHub state and fresh state acquisition;
- local GPT-OSS health/inference with zero hosted fallback calls;
- durable claim/receipt/artifact/event publication;
- crash and expired-lease recovery without duplicate work;
- exact-release host upgrade discipline;
- genuine reboot resilience;
- automatic model/timer recovery after reboot;
- natural post-reboot continuation into a durable GitHub transition;
- continued fail-closed authority boundaries.

V1 does **not** prove:

- positive economic expectancy or an investable edge;
- scientific completeness of every M3 worker/engine;
- economic-test readiness for every frozen candidate;
- prospective Forward Farm operation;
- empirical portfolio correlation where admissible return data is unavailable;
- Live Lab native ingress/UI completeness;
- real-capital or live-trading authorization.

Forward Farm remains closed while prospective observation is unauthorized. Economic experimentation, real capital and live trading remain closed.

## After V1 — V2 planning boundary

R1-R5 are closed. Any further work should be framed explicitly as V2 or another separately governed package rather than silently extending V1.

V2 design topics:

1. scientific depth/completeness of M3 workers: Quant, Fundamental, Event/Documents, Institutional/Forced Flows, Validator;
2. engine-level acceptance tests and falsification criteria;
3. release/deployment upgrade procedure as a reusable operating contract;
4. stronger restart/idempotency/lease fault injection;
5. Portfolio Map evidence boundaries and empirical-correlation rules;
6. Live Lab native event ingress and UI proof;
7. Forward Farm only if separately authorized;
8. economic experiment path only if separately authorized;
9. continued prohibition on real capital/live trading unless explicitly authorized.

## Checkpoint discipline

At every future major milestone:

1. reacquire fresh branch HEAD;
2. verify current task/receipts/artifacts rather than relying on chat memory;
3. checkpoint only meaningful proof/deployment/failure/architecture boundaries;
4. update this roadmap in the same milestone window when V1/V2 status changes;
5. include exact SHAs, evidence paths, status, failures/unknowns, next gate and authority flags;
6. never claim runtime results from GitHub-only evidence;
7. never force-push/reset over autonomous Oracle commits;
8. if concurrent Oracle activity advances HEAD, reacquire before mutation.

## Reacquisition protocol for Claude / Codex / another agent

Read in this order:

1. fresh branch HEAD for `builder/oracle-economic-loop-recovery-20261019`;
2. `CLAUDE.md` for standing operating rules;
3. this roadmap;
4. repaired-release canary artifact `research/research_os/artifacts/AAA-ORACLE-H24-CANARY-f3943830e20b05d9/qualification-5f9807e6bd84fc5a.json`;
5. current task `research/research_os/tasks/FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003.json` if not superseded;
6. newest linked receipts/artifacts/events;
7. CP5, CP4 and CP3 only when historical detail is required.

Do not restart completed V1 qualification gates unless a later code/deployment change materially invalidates the property they proved.

---

Initialized 2026-10-20 (Europe/Paris) after Codex quota exhaustion. Updated after repaired-release cold reboot and natural post-reboot wake. V1 status: `ORACLE_H24_V1_OPERATIONALLY_QUALIFIED`.