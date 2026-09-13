# Quant Operating Model

Read `QUANT_NORTH_STAR.md` and `SYSTEM_ARCHITECTURE.md` first.

This document defines how the major functions should behave together over time.

## Persistent lifecycle

Quant is a stateful system, not a sequence of isolated runs.

Conceptually:

```text
BOOT / RESUME
   -> load persistent state
   -> verify data/system health
   -> CLOCK chooses due work
   -> functions wake on events
   -> decisions/results persist
   -> learning updates priorities
   -> IDLE or next event
   -> repeat
```

A process restart should resume the same system state rather than create a new experiment world.

## System states

At minimum, every major logical function should expose one of:

- `RUN` — actively processing due work;
- `IDLE` — alive, nothing useful due now;
- `BLOCKED` — work exists but a named dependency is missing;
- `FAULT` — unexpected failure requires recovery/attention;
- `PAUSED` — intentionally suspended by budget/operator/system policy.

`IDLE` is not `FINISHED`.

## Functional roles

### ROOT / CONTROL

Routes events, owns the clock, coordinates dependencies and exposes global system state.

### RESEARCH

Searches for new edge and replacement strategies. Negative results normally generate learning and another research choice rather than human escalation.

### SCAN

Surfaces current candidates from available data/registered strategy logic.

### VET

Determines whether a candidate deserves deeper current evaluation.

### SIZE

Produces a paper/shadow exposure proposal from opportunity quality and current Book context.

### RISK

Evaluates the proposal in portfolio context and may reject it even when the candidate itself is credible.

### FILLS

Maintains paper/shadow implementation evidence so theoretical results can be compared with modeled executable outcomes.

### BOOK

Owns the authoritative persistent paper/shadow bankroll and attribution state for V1.

### BUILD

Implements missing capabilities. Codex belongs here.

## Research versus current-opportunity decisions

Two loops must remain distinct:

```text
RESEARCH LOOP
find new/replacement edge

CAPITAL/SHADOW LOOP
apply known evidence to current opportunities
```

A research candidate is not automatically a current opportunity. A validated strategy is not automatically an accepted paper/shadow position.

## Core state transitions

### ResearchTicket

`DETECTED -> FILTERED/RESEARCHING -> REJECTED/REVISE/VALIDATED -> LEARNED`

### StrategyDefinition

`RESEARCH -> VALIDATED -> SHADOW -> ACTIVE_SHADOW -> DECAYING -> RETIRED`

### OpportunityTicket

At a high level:

`DETECTED -> VET -> SIZE -> RISK -> SHADOW_OUTCOME -> BOOK -> LEARNED`

Any stage can reject/stop progression while preserving the reason and counterfactual outcome when available.

## Clock behavior

The Clock should schedule work based on information arrival and due events, not arbitrary activity targets.

Examples:

- new data version -> eligible scanners;
- scheduled research scan -> Research Factory;
- registered strategy + fresh data -> current-opportunity scan;
- closed shadow outcome -> Book/Learning;
- strategy health deterioration -> review/retirement research;
- blocked dependency resolved -> task unblocked;
- missing capability -> BuildTask.

## Wide/cheap -> narrow/deep

Cheap deterministic filters should process broad universes first. Deeper reasoning/engineering is reserved for candidates with sufficient value of information.

The system should measure whether expensive reasoning improves economic decision quality rather than invoke it ceremonially.

## Decision quality

Quant should eventually learn from both sides of selection:

- accepted outcomes;
- rejected outcomes/counterfactuals where measurable;
- false accepts;
- false rejects;
- opportunity cost versus cash/alternative opportunities.

A high rejection rate is not inherently good.

## Human interaction

The human is not the next-strategy generator.

Human escalation is reserved for genuine boundaries such as unavailable external resources, irreversible integrations, credentials, paid access or strategic ambiguity that cannot be resolved from evidence.

## Build interaction

When Quant lacks a software capability, that gap should be representable as a `BuildTask` with:

- capability needed;
- reason/evidence;
- affected subsystems;
- acceptance criteria;
- priority/value of information.

Codex can execute the BuildTask and return the capability to the system.

## Status UI contract

The UI should be generated from persistent state/events, not maintained manually.

A viewer should be able to answer quickly:

- Is Quant alive?
- What is running, idle, blocked or faulty?
- What does the shadow Book currently contain?
- What research is active?
- What opportunities were rejected/accepted?
- What strategy evidence is decaying?
- What data/capability is missing?
- What will the Clock do next?
