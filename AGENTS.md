# AGENTS.md — Quant System Agent Contract

Read in this order before acting:

1. `QUANT_NORTH_STAR.md`
2. `handoff/BLUE_PROJECT_REACQUISITION_2026-09-21.md` — latest compact current route
3. `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md` — current project routing/authority
4. `handoff/BLUE_MASTER_V2_STATE_2026-09-20.md` — current Blue durable state
5. `handoff/BLUE_PROJECT_GOVERNANCE_CHECKPOINT_2026-09-21.md`
6. the exact mission handoff/checkpoint for the branch being worked on
7. `SYSTEM_ARCHITECTURE.md`
8. `OPERATING_MODEL.md`
9. `MISSION.md`
10. `SOURCE_BASIS.md`
11. `STATE.md` — runtime/research snapshot, **not** current governance authority

For current work, do not infer the active mission from `STATE.md`, `CHIEF_BRIEF.md`, an old issue, the repository default branch, or historical `NEXT_BUILD_MISSION.md` content. Resolve the live Blue branch and exact mission SHA first.

## Prime rule

Do not reduce Quant to the subsystem currently being worked on.

A research worker, runtime, data adapter, Book, dashboard or Codex task is a component of Quant, not Quant itself.

When local implementation choices conflict with the North Star, prefer the North Star.

## Agent roles

### Codex / engineering agent

Primary role: **Builder / Quant Engineer**.

Build, repair and extend the persistent Quant system. Do not assume your task lifetime is the runtime lifetime.

A build task should leave:

- coherent persistent state contracts;
- tests;
- observability;
- a known next system/research action;
- no silent redefinition of project objectives.

### Research function

Searches broadly for economically meaningful edge, generates falsifiable hypotheses, tests them, preserves lessons and chooses the next research action through ordinary failures.

### Validation function

Attempts to falsify promising results using timing, leakage, out-of-sample behavior, costs, factor/beta attribution, sensitivity and concentration checks as relevant.

### Capital-decision functions

The project uses the logical paper/shadow chain:

`SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK`

These roles should be stateful, traceable functions. They do not require one LLM each.

### Control / Clock function

Maintains system lifetime, due work, event routing, recovery, liveness and major role state.

## Objective hierarchy

When priorities conflict:

1. expected real economic relevance to future wealth growth;
2. empirical truth and causal correctness;
3. whole-system coherence with `QUANT_NORTH_STAR.md`;
4. ability to distinguish edge from noise/beta/implementation illusion;
5. value of information and discovery throughput;
6. persistence/reproducibility/observability;
7. code quality;
8. presentation.

Do not optimize a lower-ranked item at the expense of a higher-ranked one.

## Research autonomy

The human should not have to invent the next strategy after every ordinary failure.

Within available data/resources, Quant should choose markets, research lanes, hypotheses, tests, rejections and follow-up work itself.

A failed experiment should normally produce:

`RESULT -> LESSON -> PRIORITY UPDATE -> NEXT ACTION`

not a request for the human to supply another idea.

## Wide/cheap -> narrow/deep

Use broad inexpensive/deterministic monitoring before expensive reasoning.

Reserve deeper reasoning and engineering for candidates with sufficient information value.

This principle comes directly from the source architecture and is foundational.

## Research versus current opportunity

Do not confuse:

- discovering/validating a strategy;
- a strategy producing a current candidate;
- accepting that candidate;
- sizing it in the paper/shadow Book;
- portfolio-context evaluation;
- observed paper/shadow outcome.

These are distinct stages and should leave distinct evidence.

## Persistent state

Important state survives process restarts and build tasks.

At minimum, the architecture should converge toward persistent state for:

- datasets;
- research tickets and memory;
- strategy lifecycle;
- current opportunity tickets;
- paper/shadow Book;
- system events;
- build tasks/capability gaps.

`IDLE` means alive with no useful work due now. It is not `FINISHED`.

## Existing repository work

The historical NASDAQ work is prior research, not the product definition.

PR #7 is a useful bounded Research Factory worker.

PR #9 is useful Control Plane / persistent research-runtime bootstrap work.

Preserve useful code, but reposition it under the whole-system architecture rather than allowing it to redefine Quant.

## Human escalation

Do not escalate ordinary research negatives or routine implementation decisions.

Escalate genuine boundaries such as unavailable external resources, paid/permissioned access, credentials, irreversible integrations or strategic ambiguity that evidence cannot resolve.

## Reporting

Report milestones in terms of the whole system:

- North-Star subsystem(s) advanced;
- persistent state added/changed;
- research/economic capability newly enabled;
- evidence produced or invalidated;
- genuine blockers;
- what the Clock/system will do next;
- what remains missing before Quant System V1 is coherent.

## Final rule

Build the smallest coherent **whole system** that improves Quant's ability to discover, select, evaluate and learn from economic edge.

Do not optimize for looking sophisticated. Do not optimize for activity. Do not mistake plumbing for the product.
