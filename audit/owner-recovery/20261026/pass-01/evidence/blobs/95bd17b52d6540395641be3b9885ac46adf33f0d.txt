# Quant — Persistent Autonomous Quantitative System

Quant exists to increase real capital by repeatedly discovering, selecting and exploiting genuine market edge.

Read **`QUANT_NORTH_STAR.md` first**. It is the highest-level product specification for this repository.

Quant is not a backtester, a scanner, an LLM wrapper or a collection of strategies. The target is a persistent system combining:

- Control Plane / Clock;
- Data Plane;
- Research Factory;
- the paper/shadow functional chain `SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK`;
- persistent Book/economic state;
- learning feedback;
- Build/Codex plane;
- status/control UI backed by real state.

## Architecture

```text
                     HUMAN / PROJECT CONTROL
                              |
                              v
                       ROOT / CLOCK
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
       DATA PLANE       RESEARCH FACTORY       BUILD PLANE
          |                   |                   |
          +-------------------+-------------------+
                              |
                              v
                  SCAN -> VET -> SIZE -> RISK
                              -> FILLS -> BOOK
                                     |
                                     v
                              LEARNING / MEMORY
                                     |
                                     +----> SEARCH AGAIN
```

Quant System V1 is developed in persistent paper/shadow mode while preserving the topology of the intended complete system.

## Source basis

The supplied source material contributes the principles of continuous strategy discovery, alpha replacement/decay, broad inexpensive monitoring before deeper reasoning and specialized functional roles.

The project screenshots contribute system-level ideas including persistent runtime, `RUN/IDLE` state, ticket/activity traceability, bankroll continuity and the visible `SCAN/VET/SIZE/RISK/FILLS/BOOK` chain.

Their financial results, vendor claims and performance numbers are **not treated as verified evidence**.

See `SOURCE_BASIS.md`.

## Core specification hierarchy

1. `QUANT_NORTH_STAR.md` — what Quant is and what wins when priorities conflict.
2. `SYSTEM_ARCHITECTURE.md` — whole-system planes and boundaries.
3. `OPERATING_MODEL.md` — how the system behaves over time.
4. `MISSION.md` — terminal economic objective and autonomy rules.
5. `SOURCE_BASIS.md` — source-derived ideas versus project adaptations.
6. `PIPELINE.md` — Research Factory sub-pipeline, not the whole product.
7. `STATE.md` — current implementation/research frontier.

Lower-level documents and code must not silently redefine the North Star.

## Current state

The existing PR #9 persistent research campaign is valuable **Control Plane / Research Factory bootstrap work**. It provides restart-safe campaign state, a durable queue, heartbeat/watchdog concepts and a first bounded research worker.

It is not yet the whole Quant system.

Major remaining system areas include a first-class Data Plane, broader Research Factory, versioned strategy lifecycle, persistent paper/shadow Book, whole-system feedback and a status UI driven by actual persistent state.

## Historical NASDAQ work

The existing NASDAQ research predates the rebuild. It remains prior evidence and reusable code where useful, but it does not define Quant's future market universe or architecture.

## Build philosophy

Codex is primarily the Builder / Quant Engineer. Quant is the persistent system.

A Codex task may end. Quant's state, Book, research memory, pending work and next legitimate action must remain coherent.

Build large coherent North-Star milestones instead of accumulating unrelated micro-fixes.
