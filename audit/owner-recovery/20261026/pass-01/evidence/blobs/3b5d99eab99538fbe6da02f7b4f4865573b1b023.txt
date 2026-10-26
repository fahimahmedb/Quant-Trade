# Research Runtime Runbook

This runbook is the operator contract for the dependency-light persistent
research runtime. Runtime documents live under `runtime/` and are replaced
atomically. Starting or resuming never clears them.

## Start

Starting the runtime should create or load a campaign state and begin processing executable research tasks from the persistent queue.

A start must never erase prior research memory or completed-ticket history.

```bash
python scripts/research_runtime.py start
```

`start` loads or creates the campaign, seeds the queue from the opportunity
map, executes all currently due credible work, and then becomes `IDLE` (or
`PAUSED` at a configured boundary). For clock-driven operation, invoke one
scheduler heartbeat from cron/systemd with:

```bash
python scripts/research_runtime.py tick
```

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

```bash
python scripts/research_runtime.py inspect
python scripts/research_runtime.py watchdog
```

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

```bash
python scripts/research_runtime.py pause --reason "maintenance window"
python scripts/research_runtime.py resume
```

An optional cycle boundary can be set when the campaign is first created:

```bash
python scripts/research_runtime.py start --max-cycles 10
```

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

## Restart demonstration

The deterministic demonstration uses a temporary runtime directory, runs the
PR #7 worker once, records its rejection and follow-up lesson, idles with the
data-bound research lanes preserved, destroys the Python campaign object, then
reconstructs it from disk and proves the completed fingerprint is not rerun:

```bash
python scripts/demo_research_runtime.py
```
