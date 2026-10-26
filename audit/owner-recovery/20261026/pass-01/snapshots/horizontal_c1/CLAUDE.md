# Quant — Claude Code operating context

This file is intentionally compact because Claude Code loads it every session. Keep standing project rules here; keep task-specific procedures in the relevant mission, runtime roadmap, or `.claude/skills/`.

## North Star

Quant is a persistent quantitative research and paper/shadow decision system. Its terminal objective is net economic value from genuine market edge after realistic frictions. `QUANT_NORTH_STAR.md` remains the highest project-level authority.

Do not redefine Quant around whichever subsystem is currently being edited. Preserve the whole-system model: Control/Clock, Data, Research Factory, Capital Desk `SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK`, persistent Book, Learning, Build and Status.

No file in this repository silently grants real-capital or live-trading authority.

## Current Oracle state

Oracle H24 V1 is operationally qualified on release:

`f3943830e20b05d926d3013501573b8b21fdace7`

Canonical V1 roadmap:

`research/research_os/runtime/ORACLE_LAB_V1_ROADMAP.md`

V1 proved exact-release CI, local GPT-OSS inference, durable GitHub task/receipt/artifact state, claim/lease recovery, natural systemd scheduling, genuine VM reboot recovery and natural post-reboot continuation.

Do not reinterpret V1 as proof of positive economic expectancy, scientific completeness of all research engines, Forward Farm operation, Live Lab UI completeness, real-capital safety or live-trading readiness.

## Active V2 implementation mission

Working branch:

`builder/oracle-v2-core-20261020`

Owner authorization on 2026-10-20: execute the Oracle Research OS V2 Core build autonomously from the challenged v0.3 architecture.

This authorization opens implementation only. The authority boundary remains:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

Do not infer authority from task state, model output, tests, runtime health, Owner implementation approval or V2 readiness.

V2 Core target system status:

`AUTONOMOUS_PRE_OUTCOME_RESEARCH_PIPELINE_QUALIFIED`

Strongest candidate-level status:

`READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY`

Both are pre-outcome process claims only. They never mean profitable, alpha-proven or economically validated.

## Owner override — P0-D lifted

The prior V2 candidate proposed server-side canonical-ref protection / fast-forward-only branch enforcement as P0-D.

Owner decision: **P0-D is lifted and is not an implementation blocker.**

Therefore V2 Core MUST NOT require GitHub branch protection, rulesets, or server-side force-push prevention as a Definition-of-Done gate.

Operating discipline still forbids agents from force-pushing, rewinding, resetting or deleting autonomous evidence during normal project work. This is an operating rule, not a server-side qualification requirement.

GitHub remains the qualified initial orchestration backend under bounded-writer operation. A future backend migration requires an explicit migration gate and one authoritative orchestration source at a time.

## V2 architectural laws

1. **Research / Evaluation separation.** Research, Evidence and Validation remain outcome-blind. Evaluation is architecturally present but sealed while economic/prospective authority is false.
2. **Capability isolation over convention.** Future outcome access must not rely only on code choosing not to read an available file. Evaluation credentials/storage are a distinct capability boundary when activated.
3. **Research Epochs.** Every research trial belongs to a versioned epoch with knowledge cutoff, export policy, close policy, feedback-release policy, research policy, model-routing policy and lineage metadata.
4. **Precommitted closure.** After the first evaluation export, epoch close policy cannot silently change.
5. **Feedback lineage.** Economic feedback, once separately authorized and released in a future phase, may influence successor epochs only and may never rewrite historical Producer/Validator/trial state.
6. **Human/Supervisor blinding.** An actor that can influence an active blinded epoch must not observe sealed outcomes without contaminating that epoch.
7. **Model leakage accounting.** `SOURCE_PIT` and `MODEL_PIT` are distinct. Historical LLM idea generation is not assumed provably PIT merely because documentary sources are PIT.
8. **Trial accounting from ideation.** Multiplicity starts before CandidateHypothesis freeze; generated/discarded alternatives and retries remain traceable.
9. **Validator independence.** Information, retrieval, cognition and state isolation matter; different worker names alone do not prove independence.
10. **Multidimensional scientific state.** Scientific maturity, experiment readiness, portfolio relationship and authority are separate axes.
11. **Structural overlap is not empirical correlation.** Without admissible return data, empirical correlation and marginal portfolio contribution remain unknown/not estimated.
12. **Explicit research policy.** Forced Flows or any family priority is configurable/versioned policy, not a hidden scheduler belief.
13. **Explainable scheduling.** Undefined narrative concepts such as `HIGH_VALUE_CANDIDATE` must not drive priority; selection carries reason codes and policy version.
14. **Atomicity over artificial serialization.** The invariant is one authoritative atomic transition per claim. Initial resource policy may keep heavy local inference and authoritative writes bounded to one at a time.
15. **Negative knowledge is scoped.** Failure carries assumptions, regime context and revisit conditions; it does not mean an idea is false forever.
16. **No dual orchestration truth.** Any future SQLite/PostgreSQL promotion requires explicit migration proof and a single authoritative backend.
17. **Evaluation feedback is one-way while an epoch is active.** Only schema/integrity acknowledgements may cross back before governed feedback release.
18. **History remains epistemically honest.** Later learning never rewrites what the system knew, generated, discarded, prioritized or validated earlier.

## Reacquisition order on the V2 branch

Before substantial work:

1. read `QUANT_NORTH_STAR.md`;
2. resolve the fresh HEAD of `builder/oracle-v2-core-20261020`;
3. read this file;
4. read the canonical V2 architecture/spec and V2 roadmap under `research/research_os/` once created;
5. read only the code/tests relevant to the current V2 work package;
6. use V1 roadmap/checkpoints only for properties inherited from V1.

Do not route this branch through stale September Blue handoffs unless a current V2 file explicitly points there.

## Builder / project-execution role

Claude Code or another Builder may choose implementation details autonomously inside the governed V2 scope.

Optimize for verified progress per intervention:

- prefer one large coherent work package over many microtasks;
- split only genuinely independent work when wall-clock gain exceeds coordination cost;
- combine investigation, implementation, tests, evidence and durable documentation where practical;
- delegate only substantial independent packages with exact branch/base SHA, invariants, acceptance tests and handoff format;
- external-agent output remains advisory until reconciled against repository evidence;
- do not stop because one worker, lane, test or candidate fails if other high-value executable work remains.

Prefer coherent capability over local elegance. Avoid abstractions, agents, branches and refactors that do not directly advance V2 acceptance criteria.

## Oracle concurrency and Git discipline

GitHub is shared durable memory and may change between reads.

Before every mutation:

1. reacquire fresh branch HEAD;
2. reacquire the relevant task/receipt/artifact state;
3. preserve autonomous commits;
4. reconcile if HEAD advanced.

Never force-push, reset, rewind or delete autonomous evidence as a conflict-recovery tactic.

P0-D being lifted means server-side branch protection is not required; it does **not** authorize unsafe Git operations.

## Evidence hierarchy and model-output boundary

GitHub evidence proves repository state, ancestry, receipts and artifacts. It does not by itself prove host state, boot identity, model health or runtime execution.

Local or hosted model prose is not evidence by itself. Model output remains `UNVERIFIED_MODEL_OUTPUT` until bound to admissible evidence or deterministic checks.

A state enum is not a capability. Passing operational qualification is not a scientific result. A frozen hypothesis is not an economic result.

## Research and economic integrity

Never inspect future outcomes to tune a supposedly pre-outcome hypothesis.

Never fabricate market data. Preserve provenance, timestamps, PIT caveats, retrieval manifests, hashes and transformations.

Every persistent state mutation must remain restart-safe and idempotent. Crash plus replay must not duplicate sessions, receipts, candidates, freezes or attribution.

Research trials begin at ideation, not at candidate freeze. Keep discarded alternatives and retries attributable.

Where model-weight hindsight cannot be ruled out, record that limitation instead of claiming historical discovery ability.

## V1 / V2 boundary

V1 remains closed and qualified for the properties it actually proved.

V2 Core may reuse those mechanisms but must independently qualify new scientific properties introduced by V2.

Forward Farm remains closed while prospective observation is unauthorized. Economic evaluation remains sealed while economic experiment authority is false. Real capital and live trading remain closed.

## Verification

Passing tests is necessary, not sufficient. Verify the exact property claimed.

For code changes, run narrow affected tests plus relevant broader regression/CI. Add adversarial tests for each new V2 invariant.

For V2 Core qualification, required evidence must include at least:

- Research Epoch freeze and close-policy immutability;
- trial accounting from ideation;
- explicit `SOURCE_PIT` / `MODEL_PIT` classification;
- CandidateCore plus family-extension validation;
- independent Validator metadata and state separation;
- sealed Evaluation export with reverse-channel restrictions;
- successor-only feedback lineage;
- multidimensional maturity/portfolio state;
- explainable priority decisions;
- scoped Negative Memory;
- bounded-writer orchestration and failure recovery;
- unchanged four authority flags.

## Stop conditions

Stop only for a genuine external boundary: unavailable access, paid resources requiring approval, an irreversible external action requiring authority, missing canonical content that cannot be recovered, or an environment limitation that prevents further progress.

Do not stop merely because one test, candidate, worker, lane or subsystem completed or failed.
