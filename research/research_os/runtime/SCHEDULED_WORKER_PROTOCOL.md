# Scheduled Workflow Protocol

This protocol governs external workers operating on the durable Quant-Trade queue.
The Oracle implementation is `research.research_os.oracle_worker`: systemd wakes
one bounded stage, with optional local model reasoning through `ModelBackend`.
Codex is a build/repair plane, never a scheduled runtime dependency.

## Source of truth

The state branch is an explicit runtime configuration. The recovery deployment
uses `builder/oracle-economic-loop-recovery-20261019`. Executable releases are
identified by exact immutable Git SHA; state is fetched fresh from the configured
branch on every wake and before critical transitions.

Canonical runtime files:
- `research/research_os/runtime/CONTROL_PLANE.json`
- `research/research_os/runtime/CAPABILITY_REGISTRY.json`
- `research/research_os/runtime/WORKFLOW_LANES.json`
- `research/research_os/runtime/RESEARCH_FRONTIER.json`

A worker MUST reconstruct context from fresh GitHub state on every wake. Conversation memory is advisory only.

## Core execution rule

```text
MAX_LINEAGES_PER_WAKE = 1
MULTI_STAGE_SAME_LINEAGE = TRUE
MAX_STAGES_PER_WAKE = 5
SELF_VALIDATION = FORBIDDEN
FREE_FORM_WORK_INVENTION = FORBIDDEN
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

1. Read fresh branch HEAD and all canonical runtime files.
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
8. Persist `ACTION_STARTED` using the proven native worker-event fields. Its payload SHOULD include `queue_state = "WORKING"` when the worker has durably claimed the task.
9. Execute up to five authorized stages for this same lineage. Before every stage:
   - re-read fresh relevant GitHub state;
   - verify the stage remains in the same lineage;
   - verify it belongs to the current lane;
   - verify no authority boundary changed.
10. Persist durable output after every meaningful stage. Never rely on chat memory as the only record.
11. A handoff task may be created only when the currently claimed task explicitly authorizes that exact downstream handoff. The new task must preserve lineage identity and identify the destination lane/capability.
12. Persist exactly one receipt for the wake under `research/research_os/receipts/<task_id>/` summarizing all stages actually executed. The Oracle adapter executes one small stage per wake. The stage artifact, terminal event, receipt and task progress publish atomically in one Git commit; the durable claim/start event is a preceding transaction.
13. Immediately before the terminal worker event, perform a fresh queue observation sufficient to classify the state under **Queue observability semantics** below. Persist `ACTION_COMPLETED`, or `SESSION_ENDED` if blocked/failed, with explicit queue observability fields whenever they are proved.
14. Re-fetch the claimed task and set it to `COMPLETE`, `BLOCKED` or `FAILED`, preserving lease generation and linking all durable artifacts.
15. Stop. Do not claim another lineage in the same wake.

## Deterministic empty-queue replenishment

This is the **only** exception to ordinary idle behavior and is control-plane maintenance, not free-form research.

Only the `integrator_portfolio` lane acting through `control_integrator` may perform it.

The refill path is allowed only when a fresh global scan proves:

```text
READY_TASKS_GLOBAL = 0
CLAIMED_TASKS_GLOBAL = 0
```

Then the steward must:

1. Read fresh `CONTROL_PLANE.json`, `WORKFLOW_LANES.json` and `RESEARCH_FRONTIER.json`.
2. Re-enumerate every task file immediately before derivation.
3. Apply the deterministic policy implemented by `research.research_os.queue_replenisher`:
   `LOWEST_ISSUED_COUNT_THEN_HIGHEST_PRIORITY_THEN_FRONTIER_ID`.
4. Derive **at most one** new `READY` producer task from an enabled frontier mandate.
5. Include a stable `derivation.frontier_id`, sequence and `derivation_key` in the new task.
6. Require Legacy screening before any CandidateHypothesis freeze.
7. Preserve all four hard authority flags as `false`.
8. Persist the derived task plus a bounded queue-refill receipt/event identifying the frontier and derivation key. The refill completion event MUST report `queue_state = "QUEUED"`, `ready_count >= 1`, and the derived `next_task_id` / `next_lane` when those facts are durably known.
9. Stop immediately. The steward MUST NOT execute the newly derived producer task in the refill wake.

The steward must not:
- write a free-form objective not present in `RESEARCH_FRONTIER.json`;
- derive more than one task per wake;
- recursively refill after creating a task;
- create a duplicate derivation key;
- refill while any global `READY` or `CLAIMED` task exists;
- perform producer research itself as part of refill;
- authorize economic experiments, prospective observation, capital or trading.

If every frontier reaches its configured issuance bound, the correct result is:

```text
NOOP_FRONTIER_EXHAUSTED
```

and the system idles until the Owner changes the frontier. This prevents an unbounded self-generated research loop.

## Lane boundaries

### market_discovery
May perform quant/mechanism and institutional-flow discovery, legacy duplicate checks, disconfirmation and freeze. May create an explicitly authorized `VALIDATION` handoff. May not validate or red-team its own hypothesis. It may consume a `READY` task derived by the queue steward but may not perform queue refill itself.

### fundamental_events
May perform fundamental and event/document research, duplicate checks, disconfirmation and freeze. May create an explicitly authorized `VALIDATION` handoff. May not validate or red-team its own hypothesis. It may consume a `READY` task derived by the queue steward but may not perform queue refill itself.

### evidence_data
May perform legacy recovery, provenance/PIT/source qualification and trial accounting. It must preserve historical verdict immutability and must never recreate missing economic results. It may not perform queue refill.

### independent_challenge
May perform independent validation, cross-examination and Red Team stages for an already frozen lineage. It may restrict or block claims. It may not generate, tune or repair a signal until profitable. If challenge passes and the task authorizes it, it may create one integration/portfolio handoff. It may not perform queue refill.

### integrator_portfolio
May perform economic identity, overlap mapping, Portfolio Map, shadow-readiness assessment, queue reconciliation and learning telemetry. It may not override a Red Team blocker. It may not allocate capital, size positions, generate orders or start prospective observation without separate Owner authority. When and only when the **global** queue has zero `READY` and zero `CLAIMED` tasks, it is the sole queue steward and may derive one bounded producer task under the deterministic frontier rules above.

## Atomicity / concurrency

The task file Git blob SHA is the optimistic lock. A claim update that loses the SHA race MUST abort. Never force-overwrite another worker's lease.

Lease expiry alone does not authorize blind stealing. Reclaim only if the persisted task is still non-terminal and the lease is objectively expired; increment lease generation on reclaim.

Queue refill requires a second fresh global task scan immediately before task creation. If another worker created or claimed work after the first scan, refill must abort rather than race a second lineage into the queue.

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

### Queue observability semantics

Worker lifecycle state and Research OS global queue state are separate facts. A worker becoming inactive MUST NOT by itself imply that the Research OS is `IDLE`.

The optional event payload fields are:

```text
queue_state = WORKING | QUEUED | WAITING | IDLE | UNKNOWN
ready_count = non-negative integer when proved
claimed_count = non-negative integer when proved
next_task_id = durable next task id when known
next_lane = destination workflow lane when known
```

Use them conservatively:

- `WORKING`: the emitting worker has a durably claimed task and is executing it.
- `QUEUED`: at least one durable `READY` task is known. When the current wake created an authorized handoff, the terminal event SHOULD include that handoff's `next_task_id` and `next_lane`.
- `WAITING`: at least one durable `CLAIMED` task exists, while no stronger `WORKING` fact is being emitted by this event.
- `IDLE`: allowed **only after a fresh GLOBAL queue scan proves `READY = 0` and `CLAIMED = 0`**. A worker completion, session end, missing task for the current lane, or absence of recent animation is never sufficient evidence for global `IDLE`.
- `UNKNOWN`: use when the worker cannot prove the global queue state. `UNKNOWN` is preferred to a false `IDLE`.

For an `ACTION_COMPLETED` that creates a durable downstream handoff, the preferred payload is:

```json
{
  "result": "..._QUEUED_FOR_...",
  "queue_state": "QUEUED",
  "ready_count": 1,
  "next_task_id": "<durable task id>",
  "next_lane": "<destination lane>"
}
```

`ready_count` MUST reflect the observed global count if a global scan was performed; do not hard-code `1` when other READY work exists. If exact counts are not established, omit them while still reporting `QUEUED` when the created handoff itself proves at least one READY task.

A future native Site snapshot may expose an explicit `queue_summary` with `ready_count`, `claimed_count`, `next_task_id` and `next_lane`. When present, that queue summary is authoritative for the global system-state display. The Live Lab must keep individual worker state (`WORKING` / inactive) separate from this global queue state.

## Current hard boundaries

```text
ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
```

These boundaries survive handoffs and frontier refill. A downstream task cannot inherit authority that the upstream task or frontier did not possess.

## Idle behavior

For `market_discovery`, `fundamental_events`, `evidence_data` and `independent_challenge`, if no admissible `READY` task exists for the current lane:
- do not invent work;
- do not create a new lineage;
- do not create a task merely to avoid idling;
- do not modify economic state;
- stop quietly.

For `integrator_portfolio`, first process any admissible lane task normally. If none exists, it may invoke deterministic empty-queue replenishment **only** after proving the global queue has no `READY` or `CLAIMED` tasks. Otherwise it stops quietly.
