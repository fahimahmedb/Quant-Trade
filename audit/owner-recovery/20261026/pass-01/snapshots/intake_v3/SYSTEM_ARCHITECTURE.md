# Quant System Architecture

Read `QUANT_NORTH_STAR.md` first. This file maps the whole system into stable subsystems so no local implementation is mistaken for Quant itself.

## Whole-system map

```text
PROJECT / HUMAN CONTROL
          |
          v
ROOT / CONTROL PLANE ---- BUILD PLANE
          |
          v
      DATA PLANE
          |
          +--------------------+
          |                    |
          v                    v
  RESEARCH FACTORY       CAPITAL DESK
          |                    |
          +---------+----------+
                    |
                    v
              PERSISTENT BOOK
                    |
                    v
              LEARNING LOOP
                    |
                    +----> RESEARCH / PRIORITIES

STATUS UI observes all planes from real persistent state.
```

## Control Plane / Clock

Owns system lifetime, scheduling, event routing, heartbeat, recovery, budgets, dependency state and observability.

The persistent runtime introduced in PR #9 belongs primarily to this plane. It is useful infrastructure, but it is not the whole product.

## Data Plane

Owns source adapters, point-in-time semantics, validation, normalization, lineage, dataset registry, versioning and data-availability events.

Research and downstream evaluation should declare data dependencies explicitly.

## Research Factory

Owns continuous edge discovery and replacement:

`OBSERVE -> SCAN -> FILTER -> HYPOTHESIZE -> TEST -> VALIDATE -> REGISTER -> SHADOW EVIDENCE -> DECAY/RETIRE -> SEARCH AGAIN`

Its output is evidence and versioned strategy definitions, not authoritative capital state.

## Capital Desk

The project screenshots motivate the functional chain:

`SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK`

For Quant System V1, this is represented in paper/shadow form. The important architectural requirement is that the stages exist as distinct stateful functions and that each decision is traceable.

## Persistent Book

The Book is the authoritative economic state of the system. The same bankroll carries forward through time and process restarts. Quant must never reset its economic history merely because a research run, build task or day ended.

Quant System V1 may use a shadow Book, but it must already provide persistent NAV/bankroll history, positions/exposures, modeled P&L/costs and strategy attribution sufficient to drive learning and the status UI.

## Learning Loop

Research outcomes, accepted/rejected opportunities, Book outcomes, implementation shortfall, strategy decay, data faults and false accepts/rejects feed persistent memory and future priorities.

## Build Plane

Codex is primarily a Builder / Quant Engineer. It adds or improves capabilities but is not the runtime lifetime itself.

A Codex task ending should leave Quant in a coherent persistent state with a known next action or legitimate idle/block reason.

## Status / Control UI

The UI is an architectural checksum, not decoration.

It should eventually display real state for:

- uptime and heartbeat;
- datasets and data health;
- research activity and strategy lifecycle;
- SCAN/VET/SIZE/RISK/FILLS/BOOK role state;
- bankroll/NAV and paper/shadow P&L;
- positions/exposures in the current operating mode;
- ticket counts and recent decisions;
- faults, blocked dependencies and next scheduled actions;
- Build Plane activity.

If the system cannot truthfully populate a UI field from persistent state, that subsystem is not yet fully implemented.

## Core state objects

The architecture should converge on explicit persistent contracts for:

- `ResearchTicket` — lifecycle of an edge hypothesis;
- `StrategyDefinition` — versioned strategy evidence and lifecycle;
- `OpportunityTicket` — lifecycle of a current paper/shadow opportunity;
- `BookState` — persistent economic state;
- `DatasetRecord` — data lineage/availability;
- `SystemEvent` — append-only trace for status and audit;
- `BuildTask` — missing capability or engineering work.

## Event-driven rule

Roles are logical functions and should wake when events require them. `RUN`, `IDLE`, `BLOCKED` and `FAULT` are first-class states.

The system should not create activity simply to appear autonomous.

## Scope boundary for V1

Quant System V1 should reproduce the topology and persistence of the target system in a paper/shadow environment. External irreversible integrations remain a later explicit boundary.
