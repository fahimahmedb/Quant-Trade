# Next Build Mission — Quant System V1

This is the next large Codex milestone.

Before acting, read the specification hierarchy beginning with `QUANT_NORTH_STAR.md`. Do not restate or reinterpret the target architecture locally.

## Mission

Build the first coherent **Quant System V1** in persistent paper/shadow mode.

Preserve useful PR #7 and PR #9 primitives, but extend them into a whole-system vertical slice. Do not deliver another isolated research-runtime improvement.

## Required workstreams

### A. Control Plane

Turn the current persistent research bootstrap into a genuine whole-system Clock/control layer with:

- persistent long-running mode through `IDLE`;
- durable events/heartbeat;
- explicit component state;
- restart/resume;
- durable run history;
- meaningful liveness/watchdog semantics;
- clear separation between repository fixtures and local operational state.

### B. Data Plane

Create first-class dataset state:

- registry;
- adapters;
- provenance/timestamp semantics;
- validation;
- normalized storage interface;
- fingerprints/versioning;
- dependency availability/unblocking.

Attempt at least one real free credential-free multi-asset ingestion if the environment permits network access. Never fabricate data.

### C. Research Factory

Generalize the current bounded worker into a broader autonomous Research Factory consistent with `PIPELINE.md`.

Required outcomes:

- multiple prioritized research tasks;
- learning from ordinary failures;
- versioned strategy lifecycle;
- protection against repeating equivalent dead work;
- bounded autonomous research when usable new data is available.

### D. Whole-system paper/shadow topology

Implement the paper/shadow system contracts defined in `QUANT_NORTH_STAR.md`, `SYSTEM_ARCHITECTURE.md` and `OPERATING_MODEL.md`.

Keep stage/function state explicit, persistent and traceable. Prefer deterministic logic where appropriate rather than creating an LLM per role.

### E. Persistent economic state and learning

Add the persistent paper/shadow economic state required by the North Star and status surface. Preserve continuity across process restarts and feed material outcomes into system learning.

### F. Status / Control UI

Build a minimal real local status surface inspired by the project screenshots.

It must render persistent state, not mocked values.

Expose at minimum:

- uptime / heartbeat;
- major component state;
- data health/availability;
- research activity and strategy lifecycle;
- paper/shadow economic summary;
- recent decisions/events;
- blockers/faults;
- next scheduled/system action.

Visual polish is secondary to truthful state.

### G. Chief Brief

Generate `CHIEF_BRIEF.md` automatically from persistent state at meaningful milestones.

It should summarize system health, available/missing data, research changes, strongest evidence/rejections, lifecycle changes, blockers, next autonomous actions and remaining North-Star gaps.

## Engineering cadence

Work through the connected milestone autonomously. Do not stop after the first sub-deliverable while meaningful work remains executable.

Resolve ordinary engineering failures yourself. Preserve external blockers explicitly.

Prefer simple coherent primitives over premature distributed architecture or agent swarms.

## Required demonstration

Before completion, run an end-to-end reproducible demonstration showing that:

- the system starts/resumes;
- the Clock remains coherent through active and idle periods;
- data state is loaded/validated;
- research work can be selected and recorded;
- whole-system paper/shadow state can update from actual internal events;
- persistent state survives process restart without resetting history;
- the status surface reflects real recovered state;
- `CHIEF_BRIEF.md` is generated from the same real state.

Rejected/no-action outcomes are valid. Activity is not the objective.

## Scope boundary

Do not add credentials, paid-data requirements, irreversible external integrations or real-capital authority in this milestone.

Do not spend the mission on a large distributed platform or a polished mock UI.

## Definition of done

The milestone is complete when Quant behaves like one coherent persistent system in paper/shadow mode rather than a set of research scripts.

At the end:

- run the relevant tests;
- run the restart/resume demonstration;
- generate the real status surface;
- generate `CHIEF_BRIEF.md`;
- update `STATE.md` from actual evidence;
- report which North-Star gaps were closed and which remain;
- open one reviewable PR against `quant-system-v1`.
