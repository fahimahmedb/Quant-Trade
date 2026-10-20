# Oracle Lab V1 — Canonical Roadmap

Status source for the Oracle H24 V1 qualification and handoff.

**Rule:** this file is the living roadmap. Update it only after verified evidence. Do not replace runtime proof with assumptions. Read fresh GitHub HEAD before every intervention because the Oracle timer may advance durable state autonomously.

## Branch and deployment identity

- Working branch: `builder/oracle-economic-loop-recovery-20261019`
- Roadmap initialized from GitHub HEAD: `780e2609cf6fc8f52bec50f30f0e310795e60db6`
- Current operational release still observed/pinned in task state: `f138c980c94eea313fd77532c20857da5c02d3fe`
- Latest code fix awaiting/subject to host deployment decision: `f3943830e20b05d926d3013501573b8b21fdace7`
- CP4 handoff: `research/research_os/runtime/CP4_CHATGPT_HANDOFF_20261020.md`

## Permanent safety invariants

The following remain CLOSED unless explicitly authorized by the Owner in a future governed phase:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

V1 qualification must not silently open any of these authorities.

## Evidence already acquired

### CP3 — native canary / crash recovery

- [x] Host preparation completed.
- [x] Local GPT-OSS service proven enabled/running.
- [x] Canonical service-user canary completed.
- [x] `PASS_PRE_ACTIVATION` with all 13 gates true.
- [x] Real claim persisted to GitHub.
- [x] Process was deliberately stopped after claim.
- [x] Expired lease was recovered by fresh worker instances.
- [x] Recovery completed without duplicate lineage/stages/receipts.
- [x] Local inference used; hosted model calls remained zero.
- [x] 20-record Legacy ledger and 13 frozen hypotheses loaded in the proven canary.
- [x] Four authority flags remained false.

Canonical evidence: `research/research_os/runtime/CP3_NATIVE_GITHUB_CANARY_20261020.md`.

### CP3 automatic wake

- [x] Timer activated.
- [x] At least one native automatic scheduled wake produced a durable GitHub transaction.
- [x] Canonical queue refill created `FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003`.
- [x] Historical frontier metadata normalization repaired an identifier collision without changing historical results.
- [x] Automatic wake evidence checkpointed as `DURABLE_AUTOMATIC_WAKE_PROVEN_VM_REBOOT_PENDING`.

Canonical evidence: `research/research_os/runtime/CP3_AUTOMATIC_GITHUB_WAKE_20261020.json`.

### Current durable research state at handoff

Task: `FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003`

Last verified before roadmap initialization:

- status: `READY`
- lease generation observed: `1`
- completed stage: `legacy_duplicate_check`
- last automatic commit before CP4: `8ababd83f7020cb123d8b939549c6afcf872ba13`
- four authority flags: all false

The Oracle timer may advance this state after this document is written. Always reacquire fresh HEAD/task/receipts before acting.

## V1 remaining roadmap

### R1 — Final CI disposition for Git compatibility fix

Goal: establish the final CI state of `f3943830e20b05d926d3013501573b8b21fdace7`.

- [x] Oracle Economic Loop Recovery CI observed successful during Codex session.
- [ ] Confirm final conclusion of the general / SEC P0 gate for the same SHA.
- [ ] Record run IDs and conclusions in the next checkpoint.

Exit criterion: all required CI relevant to the host fix is explicitly classified PASS / FAIL / NOT_REQUIRED with evidence.

### R2 — Host release reconciliation

Goal: determine whether the running Oracle host must move from `f138c980...` to `f394383...` before reboot qualification.

- [ ] Read fresh branch HEAD.
- [ ] Re-read current task/receipt progression.
- [ ] Verify installed host release identity.
- [ ] If `f394383...` is required and CI-approved, install via a bounded, hash-verified Owner/Ubuntu command.
- [ ] Verify model service and timer after installation.
- [ ] Create checkpoint before reboot.

Do not reinstall merely because GitHub HEAD advanced: deployment identity and durable research state are intentionally separate.

### R3 — Real VM cold reboot

Goal: prove host recovery rather than process-only recovery.

- [ ] Capture pre-reboot state: HEAD, current task, timer/service state, relevant receipt, boot identity if available.
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

Goal: close the V1 qualification without overstating scientific capability.

- [ ] Produce final V1 operational checkpoint/receipt.
- [ ] Bind exact deployment SHA, boot/reboot evidence, systemd timer evidence, local-model evidence, GitHub state transition, task/receipt identifiers, CI references, and authority flags.
- [ ] State explicitly what V1 proves and what it does not prove.
- [ ] Only then classify Oracle H24 V1 operational status.

Required distinction:

- V1 may prove autonomous scheduling, durable GitHub state, local inference, claim/recovery, and reboot resilience.
- V1 does **not** by itself prove that every M3 research engine is scientifically complete.
- Forward Farm remains closed while prospective observation is unauthorized.
- Economic experimentation, real capital, and live trading remain closed.
- Live Lab native ingress/UI integration is a separate unfinished surface unless later proven.

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

Do not silently treat this V2 list as authorization to execute those phases.

## Checkpoint discipline

At every major verified milestone:

1. reacquire fresh branch HEAD;
2. verify current task/receipts/artifacts rather than relying on chat memory;
3. create or update a durable checkpoint under `research/research_os/runtime/`;
4. update this roadmap in the same milestone window;
5. include exact SHA(s), evidence paths, status, failures/unknowns, next gate, and all authority flags;
6. never claim a runtime result from GitHub-only evidence;
7. never force-push/reset over autonomous Oracle commits;
8. if concurrent Oracle activity advances HEAD, rebase/reacquire before any write.

## Reacquisition protocol for Codex / another agent

On resumption, read in this order:

1. fresh branch HEAD for `builder/oracle-economic-loop-recovery-20261019`;
2. this file: `research/research_os/runtime/ORACLE_LAB_V1_ROADMAP.md`;
3. `research/research_os/runtime/CP4_CHATGPT_HANDOFF_20261020.md`;
4. `research/research_os/runtime/CP3_NATIVE_GITHUB_CANARY_20261020.md`;
5. `research/research_os/runtime/CP3_AUTOMATIC_GITHUB_WAKE_20261020.json`;
6. current `research/research_os/tasks/FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003.json` if it still exists/has not been superseded;
7. newest receipts/artifacts/events linked by the task;
8. CI state for `f3943830e20b05d926d3013501573b8b21fdace7`;
9. only then decide the next action from R1-R5.

Do not restart earlier canaries unless their evidence is invalidated by a later code/deployment change that materially affects the proven property.

---

Initialized 2026-10-20 (Europe/Paris) after Codex quota exhaustion. This roadmap is intended to be kept current through V1 closure.