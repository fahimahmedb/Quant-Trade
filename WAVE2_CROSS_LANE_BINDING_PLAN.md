# WAVE 2 — CROSS-LANE BINDING PLAN

Purpose: make cross-lane semantics executable before canonical Convergence #2. This plan does not integrate any sibling and does not authorize task creation, experiments, observation, capital or trading.

## Binding law

Every seam must preserve all of the following:

- exact subject identity;
- source/evidence provenance;
- point-in-time clocks where applicable;
- generation/ancestry;
- UNKNOWN as UNKNOWN;
- blocker semantics;
- authority state;
- idempotency / duplicate prevention;
- no outcome access;
- no implicit operational promotion.

The central membrane is:

```text
scientific eligibility != operational READY
Candidate != ResearchTask
scientific decision != scheduler decision
Research Intelligence != Control Plane
ModelBackend != scheduler
Proposal/Ideation ledger != queue
IdeationSourceClaim != lease
```

## 1. MULTI-SOURCE → MEGA B

### Producer

Multi-Source Ideation V2, exact branch/ref and final contract not yet reacquired.

### Consumer

MEGA B Discovery Engine.

### Intended semantic transition

```text
qualified ideation object
status = ELIGIBLE_FOR_DISCOVERY
        ↓
MEGA B producer-level discovery intake
```

`ELIGIBLE_FOR_DISCOVERY` is a scientific intake eligibility state only. It MUST NOT create or imply a Research OS task with `status=READY`.

### Required identity/provenance transfer

Until the final Multi-Source schema is visible, the following are acceptance requirements rather than invented field names:

- stable ideation/seed/proposal identity;
- exact Research Intelligence decision/reference that admitted ideation;
- context snapshot identity/hash, when present;
- exact source/document identity and version;
- `IdeationSourceClaim` or equivalent source claim identity;
- public/available/effective clocks where the source contract carries them;
- Scientific Memory/negative-knowledge references used to screen novelty;
- source qualification state and stale/reopen condition;
- generation/ancestry if ideation can be revised.

### Required semantic distinctions

- `IDEATION_SEED` and `IDEA_PROPOSAL` MUST remain distinct if the producer defines them distinctly.
- A source claim is evidence/provenance, not a scheduler lease.
- A source becoming stale MUST force the producer-defined requalification path; MEGA B may not silently treat stale provenance as current.
- Multi-Source may declare an idea scientifically eligible; it may not route around MEGA B discovery or Control Plane task admission.

### Binding adapter rule

Prefer a pure, deterministic conversion/validation function that receives the final producer object and returns either:

```text
DISCOVERY_INTAKE_ACCEPTED
```

with preserved immutable refs, or an explicit scoped blocker such as:

```text
BLOCKED_MISSING_PROVENANCE
BLOCKED_STALE_CONTEXT
BLOCKED_IDENTITY_AMBIGUITY
```

Never convert a missing/unknown field into a negative assertion.

### Current status

`EXPECTED_MISSING_BINDING` because exact Multi-Source branch/schema/final manifest is unresolved.

---

## 2. MEGA B → MEGA C0

### Producer

MEGA B Discovery Engine.

### Consumer

MEGA C0 Scientific Adjudication.

### Canonical shared object

`Candidate` from `research/research_os/engines/protocol.py` remains the canonical producer-level scientific object unless a final, explicitly versioned migration proves otherwise.

Required existing core identity/claim fields:

- `hypothesis_id`
- `generation_id`
- `mechanism`
- `claim`
- `falsification_scope`
- `decision_map`
- `economic_tags`

Existing context also includes horizon, source refs/document evidence, research decision/evidence timing and no-observation authorization.

MEGA B CP001 plans additive discovery metadata, not a second family-specific Candidate dialect.

### Required transfer to C0

C0 must receive/bind:

1. exact Candidate snapshot or stable content hash;
2. `hypothesis_id + generation_id`;
3. mechanism identity and expression/universe identity when B supplies them;
4. source lineage and all relevant source clocks;
5. ancestry/duplicate-expression identity;
6. falsifiers/disconfirmation already recorded;
7. evidence gaps and claim ceiling;
8. implementability assumptions/gaps;
9. Research Intelligence / ideation ancestry as provenance, not adjudication evidence by itself.

### Freeze/adjudication prerequisite

C0 must not cross-examine a silently mutable idea. The seam must bind to the Factory/freeze identity:

- frozen Candidate expression;
- protocol hash;
- generation/trial/epoch identity as defined by canonical Factory law;
- explicit outcome firewall state.

If B changes a material Candidate expression after freeze, the correct operation is a new generation, not in-place mutation.

### Independence

The B producer/discovery lane may not validate or Red Team its own hypothesis. C0 composes the independent challenge path; it does not hand validation authority back to B.

### Current status

`EXPECTED_SCHEMA_GAP`: canonical base Candidate/freeze semantics are known, but B implementation and C0 final input/verdict contracts are not yet final.

---

## 3. MEGA C0 → ECONOMIC / MEGA D0

### Producer

MEGA C0 scientific disposition.

### Consumers

Existing Economic Identity / Portfolio Readiness law, then MEGA D0 lifecycle.

### Required scientific disposition identity

The cross-lane envelope must bind all of:

- exact scientific subject (Candidate snapshot/hash);
- hypothesis/generation identity;
- frozen expression/protocol hash;
- experiment/trial/epoch identity where canonical Factory exposes it;
- Validator disposition;
- Red Team disposition/blockers;
- claim restriction/claim ceiling;
- uncertainty/evidence-gap state;
- verdict provenance;
- evidence refs used for adjudication;
- explicit no-outcome/no-prospective-observation state.

A favorable scientific disposition is not economic authorization and not prospective observation authorization.

### Economic identity binding

The existing Economic layer owns the structural economic identity. D0 must consume references equivalent to:

```text
EconomicIdentityRef
PortfolioReadinessRef
```

that remain bound to the same Candidate generation/scientific subject.

D0 CP001 explicitly preserves:

- existing economic fingerprint;
- exact candidate/economic-identity binding;
- KNOWN / UNKNOWN / NOT_APPLICABLE / CONFLICTED semantics;
- structural overlap and wrapper equivalence;
- portfolio readiness.

### Lifecycle admission rule

A D0 lifecycle object may be created only from a qualified scientific/economic boundary. Its initial readiness may describe contract preparation, but:

```text
READY_AWAITING_OWNER_AUTHORITY != PROSPECTIVE_OBSERVATION_AUTHORIZED
```

No lifecycle transition may synthesize an observation, decay result, resize decision or retirement result from absent future evidence.

### Current status

`EXPECTED_SCHEMA_GAP`: C0 final disposition schema and D0 implementation are not yet observable.

---

## 4. RESEARCH INTELLIGENCE / IDEATION / B → MEGA E CONTROL PLANE

### Governing question

**Where does scientific eligibility become operational work?**

The base repository already answers the authority part: operational work is a canonical Research OS `ResearchTask`, and `READY` is a task state owned by the Control Plane/runtime protocol.

### Canonical admission routes

There are only two currently authorized patterns:

#### A. Explicit downstream handoff

A currently claimed task may create a downstream task only when that exact handoff is explicitly authorized by the current task. The new task must preserve lineage identity and route to the destination lane/capability.

#### B. Deterministic empty-queue replenishment

Only the `integrator_portfolio` lane through capability `control_integrator` may derive one new READY producer task, and only after fresh proof that:

```text
READY_TASKS_GLOBAL = 0
CLAIMED_TASKS_GLOBAL = 0
```

It derives from owner-governed `RESEARCH_FRONTIER.json`, uses a stable derivation key, may create at most one task, and MUST stop without executing the producer task in the same refill wake.

### Forbidden promotions

The following MUST NOT create a READY task directly:

- `ELIGIBLE_FOR_DISCOVERY`;
- Candidate existence;
- Candidate scientific quality;
- favorable C0 scientific verdict;
- Research Intelligence recommendation;
- Multi-Source Proposal Ledger entry;
- GPT-OSS/ModelBackend suggestion;
- source novelty alone;
- Scientific Memory gap;
- D0 review cadence metadata.

### Task identity / authority payload

When admission is authorized, the canonical operational object must conform to `research-task.schema.json` and carry:

- `task_id`;
- `task_type`;
- required capability;
- `status=READY` at admission;
- priority;
- explicit inputs;
- allowed actions;
- forbidden actions;
- success condition;
- task authority object;
- initial lease object;
- lineage and derivation identity when applicable.

All four economic/prospective/capital/trading authority flags remain false.

### Runtime ownership

MEGA E must adapt the existing Research OS Control Plane/Oracle/task protocol. It is explicitly forbidden to create a second scheduler, second queue registry, second authority registry or second Oracle.

The older `src/autonomous_research` `PersistentQueue`/`ResearchCampaign` path must be explicitly bridged, quarantined or retired from canonical authority; it may not silently become a competing scheduler.

### Current status

`SPEC_READY / IMPLEMENTATION_PENDING_E`.

---

## 5. MEGA E → LIVE LAB

### Producer

Durable Research OS runtime state/events/receipts plus authenticated delivery path.

### Consumer

Existing factual native Live Lab projection.

### Canonical evidence chain

At minimum, factual runtime projection must retain continuity across:

```text
task_id
→ lease generation
→ worker/session/action identity
→ WorkerEvent sequence/generation
→ WorkerReceipt
→ durable artifacts/output commit
→ outbox/delivery identity (if E finalizes one)
→ Live Lab event evidence ref
```

### Existing event contract

Current supported WorkerEvent types are:

- `ACTION_STARTED`
- `ACTION_COMPLETED`
- `WORKER_HEARTBEAT`
- `SESSION_ENDED`

with required `event_id`, `session_id`, `worker_id`, `action_id`, `event_type`, `event_seq`, `generation`, `emitted_at`, and payload.

### Existing receipt contract

WorkerReceipt binds `receipt_id`, `task_id`, worker/session, lease generation, start/end times, input head, terminal status, artifacts, evidence refs and an authority assertion whose economic/prospective/capital/trading performed fields are all const false.

### Projection rules

The Live Lab may show only facts proved by durable runtime evidence.

- Never synthesize work because a UI animation expects it.
- Never infer role/progress/economic result from worker identity/timing.
- `UNKNOWN` is preferred to false `IDLE` or false progress.
- Worker inactive/SESSION_ENDED is not by itself proof that the **global queue** is idle.
- Global `IDLE` requires a fresh global queue proof with `READY=0` and `CLAIMED=0`.
- A stale stream/session must remain explicitly stale/unknown until fresh evidence supersedes it.
- Replay must be idempotent by event identity + stream generation/sequence.
- Delivery retries/outbox state must not create duplicate scientific/runtime facts.

### Crash/reboot requirement

After crash/reboot, a fresh process must reconstruct from durable task/lease/event/receipt/outbox state. No fact needed for continuity may exist only in process/chat memory.

### Current status

`SPEC_READY / FINAL_E_DELTA_PENDING`.

---

## Binding acceptance checklist

A seam cannot be declared ready for canonical port unless all applicable answers are YES:

- Exact producer FINAL/qualified head known?
- Exact consumer contract known?
- Stable subject identity crosses unchanged?
- Generation/ancestry retained?
- Source provenance retained?
- PIT/source clocks retained?
- UNKNOWN retained?
- BLOCKED distinct from FAILED?
- No scientific state maps directly to operational READY?
- No new scheduler/queue/authority registry introduced?
- Authority flags remain false?
- Duplicate/idempotency semantics explicit?
- Stale/requalification semantics explicit?
- Fixture exists and is deterministic/pre-outcome/non-economic?
- Seam test exists and runs on exact integrated head?

Until those hold, status remains `EXPECTED_MISSING_BINDING`, `EXPECTED_SCHEMA_GAP`, or `NOT_RUN`; tests must not be weakened to manufacture green.
