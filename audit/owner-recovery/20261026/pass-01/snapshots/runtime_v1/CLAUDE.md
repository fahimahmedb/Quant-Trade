# Quant — Claude Code operating context

This file is intentionally compact because Claude Code loads it every session. Keep standing project rules here; keep task-specific procedures in the relevant mission, runtime roadmap, or `.claude/skills/`.

## North Star

Quant is a persistent quantitative research and paper/shadow decision system. Its terminal objective is net economic value from genuine market edge after realistic frictions. `QUANT_NORTH_STAR.md` remains the highest project-level authority.

Do not redefine Quant around whichever subsystem is currently being edited. Preserve the whole-system model: Control/Clock, Data, Research Factory, Capital Desk `SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK`, persistent Book, Learning, Build and Status.

No file in this repository silently grants real-capital or live-trading authority.

## Current Oracle H24 operational truth

For branch `builder/oracle-economic-loop-recovery-20261019`, the canonical live roadmap is:

`research/research_os/runtime/ORACLE_LAB_V1_ROADMAP.md`

As of the verified 2026-10-20 checkpoint, Oracle H24 V1 is classified:

`ORACLE_H24_V1_OPERATIONALLY_QUALIFIED`

Qualified release:

`f3943830e20b05d926d3013501573b8b21fdace7`

V1 has verified exact-release CI, local GPT-OSS inference, durable GitHub task/receipt/artifact state, claim/lease recovery, natural systemd scheduling, a genuine VM reboot, automatic model/timer recovery, and a natural post-reboot worker transition correlated to GitHub.

Do **not** reinterpret this as proof of positive economic expectancy, scientific completeness of every research engine, Forward Farm operation, Live Lab UI completeness, real-capital safety, or live-trading readiness.

The permanent Oracle authority boundary remains:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

A future phase may change one of these only through explicit governed Owner authorization. Never infer authority from task status, model output, test success, or operational uptime.

## Reacquisition order

Before substantial work, first resolve the current branch and exact HEAD.

### If on the Oracle recovery / H24 branch

Read in this order:

1. `QUANT_NORTH_STAR.md`
2. fresh HEAD of `builder/oracle-economic-loop-recovery-20261019`
3. `research/research_os/runtime/ORACLE_LAB_V1_ROADMAP.md`
4. current `research/research_os/tasks/*.json` relevant to the active lineage
5. newest linked receipts, artifacts and events
6. repaired-release canary artifact `research/research_os/artifacts/AAA-ORACLE-H24-CANARY-f3943830e20b05d9/qualification-5f9807e6bd84fc5a.json` when runtime qualification detail is needed
7. CP5 / CP4 / CP3 only when historical detail is required

The Oracle timer may mutate durable GitHub state while an agent is working. Never rely on a previously remembered HEAD before a write.

### Otherwise

Use the current Blue/governance routing surfaces for that branch. Historical September files such as `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`, `handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`, and `handoff/BLUE_CONTEXT_REACQUISITION_2026-09-20.md` remain branch-context documents, but they are **not** a substitute for the Oracle roadmap on the Oracle H24 branch.

`CLAUDE_CURRENT_MISSION.md`, `STATE.md`, `CHIEF_BRIEF.md`, repository default branch state, old PR text, and old chat summaries must not override fresher branch-specific canonical evidence.

## Builder / project-execution role

Claude Code is a Builder / Quant Engineer operating inside the governed project. Choose local implementation details autonomously, but do not redefine product scope or authority.

Optimize for **verified progress per intervention**:

- prefer one large coherent work package over many microtasks;
- split only genuinely independent work when wall-clock gain exceeds coordination cost;
- batch Owner/root commands into the smallest safe bounded intervention;
- delegate to another AI only substantial independent packages with exact branch/base SHA, scope, surfaces, invariants, evidence, forbidden actions, acceptance tests and handoff format;
- treat external-agent output as advisory until reconciled against fresh GitHub state and required runtime evidence;
- combine investigation, implementation, tests, evidence and durable documentation in the same package when practical;
- do not stop because one lane, test or experiment failed if other high-value executable work remains.

Prefer coherent capability over local elegance. Avoid new abstractions, files, agents, branches and refactors unless they directly advance the current mission or repair a demonstrated invariant.

## Oracle concurrency and Git discipline

On autonomous Oracle branches, GitHub is canonical shared memory and may change between reads.

Before every mutation:

1. reacquire fresh branch HEAD;
2. reacquire the current task/receipt/artifact state involved;
3. preserve autonomous commits;
4. write only after confirming the intended base still makes sense.

Never force-push, reset, rewind, delete autonomous evidence, or overwrite a newer Oracle transition to recover from a conflict. If HEAD advances concurrently, reacquire and reconcile.

Commit coherent checkpoints. Do not create serial documentation commits for every minor observation.

## Evidence hierarchy and model-output boundary

GitHub evidence can prove durable repository state, commit ancestry, receipts and artifacts. It cannot by itself prove live host state such as systemd service health, a reboot, current boot identity, or local inference. Runtime claims require corresponding host/runtime evidence.

Local model output is research commentary, not authority. In particular, Oracle qualification explicitly classifies representative model reasoning as `UNVERIFIED_MODEL_COMMENTARY`. Never promote generated prose to evidence merely because the model ran successfully.

A state enum is not a capability. A passing operational qualification is not a scientific result. A frozen hypothesis is not an economic result. Preserve these distinctions.

## Research and economic integrity

Use one causal information timeline across research, paper/shadow decisions and the Book. Never inspect future outcomes to tune a supposedly pre-outcome hypothesis.

Research evidence must describe the executable paper/shadow object rather than a more favorable backtest object.

Never fabricate market data. Preserve provenance, timestamps, point-in-time caveats, validation and fingerprints.

Every persistent economic-state mutation must be restart-safe and idempotent. Crash plus replay must not duplicate simulated fills, cash movements, P&L, sessions, receipts, candidates or attribution.

Multiple strategies may reference the same instrument. Preserve strategy-level sleeves/attribution and aggregate separately for portfolio state.

Risk approval must describe the final post-transform/post-scale portfolio that would actually be simulated.

Structural similarity is not empirical correlation. Where admissible return data is unavailable, correlation and marginal portfolio contribution remain unknown/not estimated.

## V1 closed / V2 boundary

Oracle H24 V1 is operationally closed. Do not silently extend V1 and then describe new work as already-qualified.

Further Oracle work should begin from an explicit V2 or separately governed specification. Candidate V2 topics include:

- scientific depth and acceptance criteria for Quant, Fundamental, Event/Documents, Institutional/Forced Flows and Validator engines;
- stronger fault injection and restart/idempotency tests;
- reusable release/upgrade operating contract;
- Portfolio Map evidence boundaries;
- Live Lab native ingress/UI proof;
- Forward Farm only if prospective observation is separately authorized;
- economic experiment paths only if separately authorized.

Operational V1 proof remains valid only for properties not materially invalidated by later code/deployment changes. Do not rerun completed qualification gates by habit; do rerun the affected gate when a later change can invalidate what it proved.

## Multi-agent discipline

Use parallel agents only when workstreams are genuinely independent, require isolated context, or benefit from adversarial review. Do not spawn agents for trivial reads, one-file edits, sequential debugging, or multiple writers against the same evolving state.

For substantive changes, separate implementation from independent scientific/economic-integrity and runtime/restart review when that separation adds value, then synthesize once in the lead agent.

Avoid duplicated exploration. Give each agent one distinct responsibility and require a concise durable result.

## Token discipline

Use targeted search and file slices before full-file reads. Do not repeatedly restate architecture or facts already established in canonical repository evidence.

Do not revisit a settled implementation choice unless new evidence contradicts it or a relevant test fails.

Keep progress updates short. Put durable truth in code, tests, roadmaps and generated artifacts rather than long chat summaries.

Use `/compact` or a fresh session when the task changes materially. After branch/context changes, reacquire through the canonical router rather than rereading the entire repository.

## Verification

Passing tests is necessary, not sufficient. Verify the specific property being claimed.

For code changes, run the narrow affected tests plus the relevant broader regression/CI path. Add adversarial coverage for the demonstrated failure mode being repaired.

For runtime claims, bind exact release SHA, host/runtime evidence, GitHub evidence and authority state. Never substitute a simulated/manual wake for a property that specifically requires a natural scheduled wake.

## Stop conditions

Stop only for a genuine external boundary: unavailable access, paid resources requiring approval, irreversible external action requiring authority, missing canonical content that cannot be recovered, or an environment limitation that prevents further progress.

Do not stop merely because one test, research candidate, worker, lane or subsystem completed or failed.
