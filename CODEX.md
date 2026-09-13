# Codex Launch Mandate

Work from this branch as the autonomous research lead for Quant-Trade.

Before changing code, read:

1. `MISSION.md`
2. `SOURCE_BASIS.md`
3. `AGENTS.md`
4. `PIPELINE.md`
5. `README.md`
6. `schemas/research_ticket.schema.json`
7. the existing source, scripts, data notes and results

## Mission

Build the first coherent version of an autonomous alpha-discovery system.

Do not treat this as a request to backtest one strategy.

Do not inherit the historical NASDAQ research direction automatically.

The system should become capable of:

- broad candidate discovery;
- filtering candidates before expensive reasoning;
- generating its own falsifiable hypotheses;
- implementing tests;
- adversarial validation;
- paper/shadow decision filtering;
- persistent research memory;
- autonomous selection of the next research action.

## Preserve the architecture's nature

The project is inspired by a continuous-strategy-discovery model where:

- broad, cheaper monitoring runs continuously;
- a stronger reasoning layer receives filtered candidates;
- specialized logical roles handle scanning, hypothesis generation, backtesting, validation and downstream decision evaluation;
- strategies are expected to decay and be replaced.

The supplied screenshots add an important idea: many signals can be rejected, and inactivity can be intentional. In research/paper evaluation, `NO_TRADE` is a valid output.

Do not copy vendor names, profit claims, model counts or exact agent counts as requirements.

## First build target

Do not build a giant platform all at once.

Build one complete autonomous vertical slice with reusable interfaces:

`DATA -> SCAN -> RESEARCH TICKET -> HYPOTHESIS -> TEST -> VALIDATE -> PAPER/SHADOW FILTER -> MEMORY -> NEXT ACTION`

Then use it on real historical data so the architecture is exercised rather than merely documented.

## ResearchTicket

Use one persistent ticket object to trace a candidate through the system.

Do not allow each module to invent its own incompatible result format.

The ticket should retain:

- origin;
- market/instruments;
- timestamp semantics;
- candidate evidence;
- hypothesis;
- test result;
- validation result;
- rejection reason if any;
- final lesson.

## Research universe

Construct and rank a compact opportunity map before choosing the first lane.

At minimum consider the four source-derived families:

- statistical arbitrage / relative value;
- volatility-surface anomalies;
- factor-residual anomalies;
- insider / filing-driven signals.

You may identify a better fifth lane if evidence supports it.

Rank lanes by:

- plausible mechanism;
- data availability and point-in-time quality;
- ability to isolate edge from passive beta;
- research cost;
- falsifiability;
- implementation realism;
- likely economic significance;
- value of information.

Choose the first lane yourself.

## Autonomy after failure

When a candidate fails:

1. record why;
2. update memory;
3. decide whether the failure applies to the expression, hypothesis, scanner or entire lane;
4. choose the next highest-value action;
5. continue.

Do not stop to ask the human for a new strategy idea after an ordinary negative result.

## Evidence standard

A positive-looking result is not enough.

Check, as relevant:

- point-in-time correctness;
- look-ahead / leakage;
- survivorship;
- common beta/factor exposure;
- multiple testing;
- out-of-sample behavior;
- realistic costs;
- parameter sensitivity;
- regime dependence;
- concentration in a few observations.

## Paper/shadow decision layer

For a validated strategy, test whether conditional selectivity adds value.

Compare:

- raw signal outcomes;
- filtered paper/shadow signal outcomes;
- rejected-signal outcomes.

A high rejection rate is not automatically good. Measure false rejections and false accepts.

## Existing code

Reuse old NASDAQ modules only if they are useful primitives. Do not spend the run defending or extending the old direction by inertia.

## Deliverables for this run

Leave the branch with:

1. a small, coherent package structure for the autonomous discovery loop;
2. a machine-readable ResearchTicket implementation matching the schema;
3. one scanner/candidate generator for the chosen lane;
4. one hypothesis/test/validation path exercised end-to-end;
5. persistent research-memory artifacts;
6. tests for timing/causality and core state transitions;
7. a concise `STATE.md` stating what the system now knows, what it rejected, what survived, and what it will do next autonomously.

## Stop conditions

Stop and escalate only if the next meaningful research step requires unavailable external access, paid data, credentials, an irreversible integration, or another boundary outside the current research environment.

Otherwise keep working through the research loop.

## Final instruction

Build an autonomous researcher, not a pile of disconnected backtests.

The desired behavior is:

> **search broadly, reason deeply, reject freely, learn continuously, and keep looking for real economic edge.**
