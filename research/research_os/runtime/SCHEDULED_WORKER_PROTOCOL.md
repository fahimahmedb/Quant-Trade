# Scheduled Workflow Protocol

This protocol is for ChatGPT/Codex-style workflow workers that wake periodically and operate on the durable Quant-Trade queue.

## Source of truth

Branch: `builder/research-os-autonomous-loop-20261015`

Canonical runtime files:
- `research/research_os/runtime/CONTROL_PLANE.json`
- `research/research_os/runtime/CAPABILITY_REGISTRY.json`
- `research/research_os/runtime/WORKFLOW_LANES.json`

A worker MUST reconstruct context from fresh GitHub state on every wake. Conversation memory is advisory only.

## Core execution rule

```text
MAX_LINEAGES_PER_WAKE = 1
MULTI_STAGE_SAME_LINEAGE = TRUE
MAX_STAGES_PER_WAKE = 5
SELF_VALIDATION = FORBIDDEN
```

A workflow may perform several consecutive stages for the same lineage when all stages belong to its lane and each stage is explicitly authorized. It may not jump to a second independent lineage in the same wake.

Example allowed in one wake:

```text
candidate research
→ disconfirmation
→ freeze
→ persist
→ create explicitly-authorized validation handoff
```

Example forbidden in one discovery wake:

```text
candidate research
→ independent validation
→ red team
```

Independent challenge must occur in the `independent_challenge` lane on a later fresh-state wake.

## One-wake algorithm

1. Read fresh branch HEAD and all three canonical runtime files.
2. Identify the worker's `lane_id`.
3. Enumerate `research/research_os/tasks/`.
4. Select the highest-priority `READY` task routed to that lane. Select only one lineage.
5. Fetch the selected task and retain its current blob SHA.
6. Re-read task authority, allowed actions and forbidden actions. If any required stage would exceed authority, do not execute that stage; persist/report `OWNER_DECISION_REQUIRED` only when the task itself requires escalation.
7. Claim atomically by updating the same task with the fetched blob SHA:
   - `status = CLAIMED`
   - `lease.generation += 1`
   - `lease.owner = <stable workflow worker id>`
   - `lease.claimed_at = <current timestamp>`
   - `lease.expires_at = <current timestamp + <= 55 minutes>`
8. Persist `ACTION_STARTED` using the proven native worker-event fields.
9. Execute up to five authorized stages for this same lineage. Before every stage:
   - re-read fresh relevant GitHub state;
   - verify the stage remains in the same lineage;
   - verify it belongs to the current lane;
   - verify no authority boundary changed.
10. Persist durable output after every meaningful stage. Never rely on chat memory as the only record.
11. A handoff task may be created only when the currently claimed task explicitly authorizes that exact downstream handoff. The new task must preserve lineage identity and identify the destination lane/capability.
12. Persist exactly one receipt for the wake under `research/research_os/receipts/<task_id>/` summarizing all stages actually executed.
13. Persist `ACTION_COMPLETED`, or `SESSION_ENDED` if blocked/failed.
14. Re-fetch the claimed task and set it to `COMPLETE`, `BLOCKED` or `FAILED`, preserving lease generation and linking all durable artifacts.
15. Stop. Do not claim another lineage in the same wake.

## Lane boundaries

### market_discovery
May perform quant/mechanism and institutional-flow discovery, legacy duplicate checks, disconfirmation and freeze. May create an explicitly authorized `VALIDATION` handoff. May not validate or red-team its own hypothesis.

### fundamental_events
May perform fundamental and event/document research, duplicate checks, disconfirmation and freeze. May create an explicitly authorized `VALIDATION` handoff. May not validate or red-team its own hypothesis.

### evidence_data
May perform legacy recovery, provenance/PIT/source qualification and trial accounting. It must preserve historical verdict immutability and must never recreate missing economic results.

### independent_challenge
May perform independent validation, cross-examination and Red Team stages for an already frozen lineage. It may restrict or block claims. It may not generate, tune or repair a signal until profitable. If challenge passes and the task authorizes it, it may create one integration/portfolio handoff.

### integrator_portfolio
May perform economic identity, overlap mapping, Portfolio Map, shadow-readiness assessment, queue reconciliation and learning telemetry. It may not override a Red Team blocker. It may not allocate capital, size positions, generate orders or start prospective observation without separate Owner authority.

## Atomicity / concurrency

The task file Git blob SHA is the optimistic lock. A claim update that loses the SHA race MUST abort. Never force-overwrite another worker's lease.

Lease expiry alone does not authorize blind stealing. Reclaim only if the persisted task is still non-terminal and the lease is objectively expired; increment lease generation on reclaim.

## Independence invariant

A lineage's discovery worker and independent challenge worker must be different workflow lanes. Discovery output must be durably frozen before challenge begins. Challenge may inspect the frozen material but may not silently mutate it. Material changes require a new generation.

## Native Live Lab events

Use only currently proven event types:
- `ACTION_STARTED`
- `ACTION_COMPLETED`
- `WORKER_HEARTBEAT`
- `SESSION_ENDED`

Required identity fields:

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

## Current hard boundaries

```text
ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
```

These boundaries survive handoffs. A downstream task cannot inherit authority that the upstream task did not possess.

## Idle behavior

If no admissible `READY` task exists for the current lane:
- do not invent work;
- do not create a new lineage;
- do not create a task merely to avoid idling;
- do not modify economic state;
- stop quietly.
