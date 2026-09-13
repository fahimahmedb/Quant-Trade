# Research Runtime Runbook

This runbook defines the intended operator contract for the persistent research runtime that the next Codex run must implement.

## Start

Starting the runtime should create or load a campaign state and begin processing executable research tasks from the persistent queue.

A start must never erase prior research memory or completed-ticket history.

## Inspect

An operator should be able to inspect, without reading logs manually:

- campaign status;
- last heartbeat;
- active ticket(s);
- queued ticket(s);
- blocked tasks and reasons;
- cycles completed;
- latest lesson;
- current next action;
- budget consumed / remaining when configured.

## Idle

`IDLE` means the runtime is alive but has no useful work to execute at that instant.

Examples:

- waiting for new data;
- waiting for a scheduled scan;
- no candidate currently clears the upstream filter;
- all higher-priority tasks are blocked while a lower-priority scheduled task is not yet due.

`IDLE` must not be rendered as `FINISHED`.

## Pause

A pause preserves all state and queue contents.

Typical reasons:

- configured compute/time budget reached;
- operator-requested pause;
- temporary resource boundary.

Resume must continue from the same campaign state.

## Blocked

A blocked task remains visible in the queue with an explicit reason such as:

- missing dataset;
- network access unavailable;
- permissioned source required;
- dependency unavailable;
- human choice genuinely required.

One blocked task should not stop unrelated executable tasks.

## Stop

A stop is explicit and durable. The runtime should record who/what caused it and when.

Completing one experiment or opening a PR is not a stop.

## Restart safety

After process restart, the runtime should recover:

- campaign identity;
- completed work;
- queued work;
- blocked work;
- last processed data versions;
- latest lesson;
- next-action priority.

It must not repeat a completed task merely because the process restarted.

## Watchdog

The watchdog should eventually flag:

- task stuck in active state beyond its expected duration;
- repeated worker crash;
- heartbeat missing;
- identical failed task being regenerated repeatedly;
- queue starvation despite available executable work.

The watchdog reports a system fault; it should not silently rewrite research conclusions.
