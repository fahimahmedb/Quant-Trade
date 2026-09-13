# Quant System State

This file is the compact current state of the whole Quant project. It should be updated at meaningful milestones, not after every minor experiment.

Read `QUANT_NORTH_STAR.md` before interpreting this file.

## Architectural state

The project has been re-centered on the full Quant system rather than an autonomous-research-only interpretation.

Current hierarchy:

- `QUANT_NORTH_STAR.md` — product/architecture North Star;
- `SYSTEM_ARCHITECTURE.md` — whole-system planes;
- `OPERATING_MODEL.md` — persistent behavior and role model;
- `MISSION.md` — terminal economic objective;
- `SOURCE_BASIS.md` — source-derived architecture and caveats;
- `PIPELINE.md` — Research Factory sub-pipeline only.

The persistent research runtime introduced by PR #9 is now interpreted as **Control Plane / Research Factory bootstrap infrastructure**, not as Quant itself.

## What exists today

Useful implemented pieces include:

- historical NASDAQ research and reusable quantitative utilities;
- a `ResearchTicket` state machine;
- append-only research memory;
- one bounded research worker/vertical slice;
- persistent campaign state and task queue;
- restart/recovery behavior;
- heartbeat/watchdog concepts;
- operator controls for the research campaign.

## Current research evidence

The first bounded time-series relative-value test selected a weak 5-day reversal pattern on the discovery sample.

Its out-of-sample result was not credible edge after stronger friction/subperiod/concentration checks. The fixed expression remains rejected and should not be parameter-rescued on the same evidence.

This result is useful primarily as integration evidence for the Research Factory and as a reminder that superficially positive results can fail economic validation.

## Current data frontier

The repository remains data-constrained.

It lacks the broader synchronized point-in-time datasets required to exercise several higher-value research lanes. The existing runtime correctly represents those missing resources as blocked work rather than silently inventing data.

A first-class Data Plane is still missing.

## Whole-system maturity

### Control Plane / Clock

**Partial v0.** Persistent campaign state, queue, restart/recovery and watchdog concepts exist. The current research CLI is not yet the complete persistent whole-system Clock.

### Data Plane

**Mostly absent.** No unified dataset registry, lineage, validation and dependency/unblocking layer yet.

### Research Factory

**Early v0.** One bounded worker exists; research breadth, strategy lifecycle and replacement/decay loops remain immature.

### Capital decision / paper-shadow chain

**Not yet implemented as a coherent whole-system subsystem.** The target functional topology remains `SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK` as defined in the North Star.

### Persistent Book

**Absent.** Runtime/research state persists, but the target paper/shadow economic state and bankroll continuity are not yet implemented.

### Learning feedback

**Research-centric v0.** Experiment lessons persist, but whole-system feedback from current opportunity decisions, paper/shadow outcomes, strategy degradation and missed opportunities is not yet unified.

### Build Plane

**Informal but active.** Codex has successfully built bounded research and persistent-runtime components. `CODEX.md` now defines Codex as Builder / Quant Engineer rather than the runtime itself.

### Status / Control UI

**Absent.** A future UI must be generated from real persistent state and act as an architectural checksum, not a mock dashboard.

## Highest-value next milestone

The next large implementation milestone should be **Quant System V1 in persistent paper/shadow mode**.

It should close several connected North-Star gaps together rather than perform another isolated infrastructure pass.

Priority areas are:

1. persistent whole-system Clock / event model;
2. first-class Data Plane;
3. broader Research Factory plus versioned strategy lifecycle;
4. persistent paper/shadow Book and whole-system learning state;
5. paper/shadow current-opportunity functions matching the North-Star topology;
6. status/control UI backed by actual persistent state.

## Human boundary currently reached?

No architectural boundary is currently blocking the next build milestone.

Some future research lanes remain genuinely blocked by missing data/resources, but that should not prevent building the coherent system topology or executing other available work.
