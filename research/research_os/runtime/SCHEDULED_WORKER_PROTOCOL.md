# Scheduled Worker Protocol

This protocol is for ChatGPT/Codex-style workers that wake periodically and operate on the durable Quant-Trade task queue.

## Source of truth

Branch: `builder/research-os-autonomous-loop-20261015`

A worker MUST reconstruct context from GitHub on every wake. Conversation memory is advisory only.

## One-run algorithm

1. Read fresh branch HEAD.
2. Enumerate `research/research_os/tasks/`.
3. Select at most one `READY` task compatible with the worker capability, highest priority first.
4. Fetch the selected task and retain its current blob SHA.
5. Re-read authority and forbidden actions. If the requested work would exceed authority, mark nothing and stop with `OWNER_DECISION_REQUIRED` in the worker report.
6. Claim atomically by updating the same task with the fetched blob SHA:
   - `status = CLAIMED`
   - `lease.generation += 1`
   - `lease.owner = <stable worker id>`
   - `lease.claimed_at = <current timestamp>`
   - `lease.expires_at = <current timestamp + <= 55 minutes>`
7. Persist an `ACTION_STARTED` event under `research/research_os/events/<task_id>/` using the proven native worker-event fields.
8. Execute only the bounded allowed actions.
9. Persist output artifacts.
10. Persist exactly one receipt under `research/research_os/receipts/<task_id>/<receipt_id>.json`.
11. Persist an `ACTION_COMPLETED` event, or `SESSION_ENDED` if blocked/failed.
12. Re-fetch the task and update it to `COMPLETE`, `BLOCKED` or `FAILED`, preserving lease generation and linking receipt/artifacts.
13. Stop. Never create follow-up research tasks unless the task explicitly authorizes it.

## Atomicity / concurrency

The task file's Git blob SHA acts as the optimistic lock. A claim update that loses the SHA race must abort; the worker must not force-overwrite another lease.

Lease expiry does not authorize stealing a task blindly. A later worker may reclaim only if the persisted task is still non-terminal and the lease is objectively expired; reclamation increments generation.

## Native Live Lab events

Use only currently proven event types:

- `ACTION_STARTED`
- `ACTION_COMPLETED`
- `WORKER_HEARTBEAT`
- `SESSION_ENDED`

Required event identity fields:

```text
event_id
session_id
worker_id
action_id
event_type
event_seq
generation
emitted_at
payload
```

Do not claim Codex/Owner identity, research role, progress, economic meaning or decisions unless separately proven by a future contract.

## Current hard boundaries

```text
ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
```

A worker receiving a task inconsistent with these boundaries must refuse that part of the task and persist no fabricated evidence.

## Idle behavior

If no admissible `READY` task exists:

- do not invent work;
- do not create a new hypothesis;
- do not create a new task;
- do not modify economic state;
- stop quietly.
