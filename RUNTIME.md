# Persistent Research Runtime

## Why this exists

A Codex task ending is not the same thing as the Quant research system ending.

The first autonomous vertical slice proved that one cycle can run end to end. The next architectural step is to move autonomy out of the temporary Codex task and into a persistent research runtime.

The intended distinction is:

```text
BUILD PLANE
Codex / engineer
    -> builds and improves Quant

RUN PLANE
Quant research runtime
    -> keeps scanning, testing, learning and reprioritizing after the build task ends
```

## Non-negotiable runtime rule

The following events are **not** normal stop conditions:

- one experiment completed;
- one candidate rejected;
- one vertical slice completed;
- one pull request opened;
- one scanner produced no candidate;
- one strategy failed validation.

A research campaign should continue until it reaches a real boundary such as:

- configured compute/time budget exhausted;
- no remaining credible research task with currently available data;
- required data is unavailable;
- paid/permissioned access is required;
- credentials or another external resource are required;
- an explicit human boundary is reached.

## Runtime responsibilities

The runtime should eventually own:

1. **Clock / scheduler** — decides which research jobs are due.
2. **Research queue** — persistent ordered backlog of candidate tasks.
3. **Worker dispatch** — wakes only the modules needed for a ticket.
4. **Campaign state** — persists across process restarts.
5. **Heartbeat** — proves the system is alive even when there is no candidate worth acting on.
6. **Memory integration** — lessons from completed tickets change future priorities.
7. **Watchdog** — detects repeated failures, stalled tasks and dead workers.
8. **Boundary detection** — distinguishes ordinary negative results from genuine reasons to stop/escalate.

## Event-driven model

The runtime should not force every role to run continuously.

Conceptual flow:

```text
CLOCK
  ↓
SCAN due?
  ↓
create candidate ticket
  ↓
FILTER
  ├─ reject -> memory -> continue
  ↓
HYPOTHESIS / TEST / VALIDATE
  ├─ reject -> memory -> continue
  ↓
PAPER/SHADOW evaluation
  ↓
feedback -> memory -> reprioritize
  ↺
```

Expensive reasoning should be activated only when a cheaper upstream stage produces something worth deeper work.

## Campaign state

A persistent campaign state should include at least:

- campaign ID;
- status;
- start time;
- last heartbeat;
- cycles completed;
- active ticket IDs;
- queued ticket IDs;
- blocked tasks;
- last completed ticket;
- latest lesson;
- current highest-value next action;
- data fingerprints / versions already processed;
- configured research budget;
- budget consumed;
- stop / pause reason when applicable.

See `schemas/campaign_state.schema.json`.

## Research queue

The queue must prevent two failure modes:

### Repeating the same dead experiment

A failed ticket should update memory and normally lower the priority of equivalent tasks unless there is a new reason to revisit them.

### Stopping because the first idea died

When a ticket closes, the orchestrator should inspect:

- ticket lesson;
- next-action hints;
- opportunity map;
- available datasets;
- existing memory;

and generate or promote the next credible task automatically.

## Data-aware idling

Autonomy does not mean generating artificial work.

If no new data or credible next experiment exists, the runtime may idle while remaining alive.

`IDLE` is different from `FINISHED`.

The runtime should expose why it is idle:

- waiting for new data;
- waiting for scheduled scan;
- no candidate above threshold;
- all available research lanes blocked by missing data;
- compute budget temporarily paused.

## Relationship with Codex

Codex should be treated as a builder / maintainer / deep-research worker, not as the process lifetime itself.

A good Codex run can finish while Quant remains conceptually active.

Future Codex tasks should therefore improve one or more parts of the persistent runtime rather than treating PR creation as the end of the research campaign.

## Implemented minimum runtime

The dependency-light campaign orchestrator now lives in
`src/autonomous_research/runtime.py`, with its operator entry point in
`scripts/run_research_runtime.py`.

Its minimum behavior is:

1. load campaign state;
2. inspect the research queue;
3. run due work;
4. persist ticket result and lesson;
5. update priorities;
6. choose the next action;
7. heartbeat while idle;
8. stop only on explicit budget/resource/human boundary.

State and queue transitions use atomic JSON replacement. An `ACTIVE` task found
at startup is returned to the queue, completed task IDs are durable
deduplication keys, blocked work remains inspectable, and unrelated executable
work continues. The worker registry keeps orchestration separate from specific
research lanes.

The next runtime increment should add scheduled task eligibility, retry policy
and watchdog alerts for repeated crashes or stale heartbeats. Those controls
should be added from observed operational need rather than by prematurely
building distributed infrastructure.
