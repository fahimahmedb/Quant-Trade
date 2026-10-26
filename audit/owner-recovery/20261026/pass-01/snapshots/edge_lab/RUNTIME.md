# Control Plane / Persistent Research Runtime

> **Current-routing notice:** this is subsystem/history documentation for the research runtime. It is not the current project mission, P0 target-host runbook, or repository-administration runbook. For current work, read `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md` and the exact mission it references.

Read `QUANT_NORTH_STAR.md` and `SYSTEM_ARCHITECTURE.md` first.

This document describes the **research-campaign portion of Quant's Control Plane**. It is important infrastructure, but it is not the whole Quant system.

## Why this exists

A Codex task ending is not the same thing as Quant ending.

The first bounded research worker proved that one cycle can execute end to end. The persistent runtime moves campaign state, scheduling, recovery and next-action logic into the software itself.

```text
BUILD PLANE
Codex / engineer
    -> builds and improves Quant

CONTROL / RUN PLANE
Quant
    -> persists state, schedules due work and remains coherent after the build task ends
```

## Non-negotiable runtime rule

These events are not normal campaign stop conditions:

- one experiment completed;
- one candidate rejected;
- one vertical slice completed;
- one pull request opened;
- one scanner produced no candidate;
- one research path failed validation.

A campaign may become idle, paused or blocked for explicit reasons, but ordinary negative evidence should become memory and reprioritization.

## Responsibilities of this subsystem

The research runtime/control bootstrap owns or contributes to:

1. Clock / scheduler for research work;
2. persistent research task queue;
3. worker dispatch;
4. campaign state across restarts;
5. heartbeat and liveness;
6. research-memory integration;
7. watchdog/fault detection;
8. explicit resource/budget boundaries.

PR #9 implements a useful v0 of these capabilities.

## Event-driven model

The runtime should wake functions only when useful work is due.

Expensive reasoning should be activated only after cheaper upstream filtering produces something worth deeper work.

## Campaign state

Persistent state should expose at least:

- campaign identity/status;
- heartbeat;
- completed/active/queued/blocked work;
- latest lesson;
- current next action;
- processed data/task identities;
- configured/consumed research budget;
- explicit pause/block reason.

See `schemas/campaign_state.schema.json` for the current v0 contract.

## Research queue

The queue should prevent both:

- repeating equivalent dead work without new evidence;
- stopping simply because the first idea failed.

When work closes, the runtime should preserve the result and promote the next credible executable research action when one exists.

## Data-aware idling

`IDLE` means alive with no useful research work due at that moment.

Possible reasons include waiting for new data, a scheduled event or resolution of a dependency.

`IDLE` is not `FINISHED`.

## Relationship to the whole system

This runtime is only part of the architecture.

Quant also requires the Data Plane, Research Factory breadth/strategy lifecycle, the paper/shadow decision functions described in the North Star, persistent Book/feedback, Build Plane and status UI.

Do not use this document to redefine Quant as a research orchestrator.

## Current maturity

PR #9 provides the first restart-safe campaign orchestrator and should be preserved as a Control Plane bootstrap.

Its remaining weaknesses should be fixed inside larger North-Star milestones rather than becoming an endless sequence of isolated runtime micro-projects.
