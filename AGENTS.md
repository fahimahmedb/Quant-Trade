# AGENTS.md — Quant-Trade agent contract

## Minimal recovery and durable work

This is the single recovery procedure; README routes here. It applies without chat history, custom instructions or a previous agent.

1. Read QUANT_NORTH_STAR.md, then governance/CURRENT_PROJECT_STATE_2026-10-31.md on the repository default ref. The 2026-10-20 router is retained as historical baseline only; follow it when the current router explicitly sends you there. Resolve the default ref remotely; do not assume an old checkout contains the latest router.
2. Treat summaries as navigation claims. Check LAST_VERIFIED_AT, LAST_VERIFIED_REF and OBSERVATION_METHOD. Reconcile relevant current refs, newer work and exact evidence before choosing an action. Unindexed or conflicting activity stays UNKNOWN/UNRECONCILED. Absence of a handoff is not a reason to restart completed work.
3. Distinguish VERIFIED (specific assertion actually checked), REPORTED (document claim), STALE and UNKNOWN. Work may be ACTIVE, PARKED or BLOCKED. Built, qualified, integrated, promoted, active and used are different dimensions. CI on another SHA does not qualify this subject; Git does not prove current runtime health.
4. Inspect existing evidence before proposing work. Reuse, connect or repair before building. NO_CHANGE_REQUIRED, BLOCK, PARK and UNKNOWN are valid deliverables; a patch is not mandatory.
5. High-value work (including autonomous prompts, architecture, scientific protocols and persistent working rules) self-triggers: OBJECTIVE → INSPECT EXISTING EVIDENCE → PROPOSE → COUNTEREXAMPLE / BYPASS / BLIND SPOT → REVISE IF NEEDED → VERIFY → RECORD RESULT. Record the concrete objection, its disposition, revisions or why none were needed, exact checks and limits. Ordinary small tasks need only proportionate verification.
6. Before pursuing a side finding ask: DOES THIS CHANGE THE DECISION OR UNBLOCK THE USER OBJECTIVE? If no, PARK it with a reopening condition. UNKNOWN can BLOCK the affected action; it does not authorize unlimited auditing. Request independent review only when consequences/risk warrant it. Owner permission and technical/scientific verification are separate; self-review is not independent review.
7. Update only the necessary existing state/index: what was actually done, subject/base identity, evidence versus reports, checks performed, remaining unknowns, parked issues and the next bounded action with revalidation conditions. Use native Git history for changes, not duplicate logs. Verify the remote update before claiming durable completion. An unpushed local SHA remains provisional.
8. After interruption repeat reconciliation, not the completed task. If a decisive premise cannot be established, record BLOCK/UNKNOWN and stop that action.

Historical routing and cleanup documents may conflict. CP11 destructive commands are superseded; no branch deletion, runtime activation, promotion or economic authority follows from this documentary repair. Follow the current state rather than old September handoffs or an old NEXT_BUILD_MISSION.

## Prime rule

Do not reduce Quant to the subsystem currently being worked on.

A worker, runtime, data adapter, research engine, validator, Book, UI, Oracle host or agent is a component of Quant, not the whole project.

When lower-level implementation choices conflict with `QUANT_NORTH_STAR.md`, preserve the North Star and surface the conflict.

## Permanent authority boundary

Unless changed by a later explicit Owner decision:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

Tests, audits, validator PASS, local-model output, operational qualification and branch cleanup grant none of these authorities.

## Functional roles

### Builder / engineering

Build, repair and integrate persistent capabilities. Leave tests, observability, restart safety and durable evidence. Do not create architectural novelty without a demonstrated need.

### Research / producer

Generate falsifiable economically meaningful hypotheses, screen against Legacy/current knowledge, preserve negative results and produce explicit evidence.

### Independent validation / red team

Attempt to falsify promising work. Check timing, provenance, leakage, multiplicity, implementability, costs, sensitivity, structural duplication and decision-map integrity as relevant.

### Portfolio / integration

Reason about economic identity and structural overlap without inventing empirical correlation. Without admissible returns, empirical correlation is UNKNOWN/UNAVAILABLE and marginal contribution is NOT_ESTIMATED.

### Control / clock

Maintain lifetime, due work, claim/lease fencing, recovery, liveness, bounded work selection and durable state.

## Scientific invariants

- never fabricate data or evidence;
- preserve point-in-time timing and provenance;
- UNKNOWN is not evidence of independence or PASS;
- negative results remain scientific memory;
- a local PASS is not automatically a family-level or economic-edge claim;
- producer and independent challenge functions remain separated;
- historical result immutability survives branch cleanup;
- persistent state mutation must be restart-safe and idempotent.

## Research autonomy

Ordinary negative experiments should normally produce:

`RESULT -> LESSON -> PRIORITY UPDATE -> NEXT LEGITIMATE ACTION`

not a request for the human to invent another strategy.

Use broad inexpensive/deterministic monitoring before expensive reasoning. Reserve deeper analysis and engineering for candidates with sufficient information value.

## Repository hygiene

Historical procedure (not execution authority):

`governance/REPOSITORY_HYGIENE_V2_2026-10-20.md`. Reconcile the current project state and later audit decisions before using it.

Branch sprawl is now considered a project defect.

- reuse an existing authorized branch when appropriate;
- absorbed ancestors do not need permanent branch refs;
- unique historical tips can be archived before deleting their working refs;
- do not delete scientific meaning merely because a branch is old;
- do not mutate Oracle V1 as incidental cleanup;
- do not create another top-level V2 architecture before the canonical trunk is declared.

## Human escalation

Do not escalate routine coding choices, ordinary research negatives or expected test failures.

Escalate genuine boundaries such as unavailable external resources, paid/permissioned access, credentials, irreversible authority/integration decisions or strategic ambiguity that current project evidence cannot resolve.

## Reporting standard

Report milestones with:

- exact branch and HEAD;
- capability/evidence added or invalidated;
- scientific limits;
- tests / adversarial checks;
- durable state changes;
- genuine blockers;
- next legitimate action.

Durable truth belongs in GitHub, code, tests and evidence artifacts rather than in chat-only summaries.
