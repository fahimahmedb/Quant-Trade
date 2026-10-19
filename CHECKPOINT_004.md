# Forensic Audit Continuation — Checkpoint 004

Date: 2026-10-19
Audit branch: `audit/forensic-checkpoint-20261019`
Parent audit head: `b7f8cb27c535bfd5d785cf2c55589f3fcc11cd56`
Status: `PARTIAL_IN_PROGRESS`

## Purpose

Refine the executor finding from Checkpoint 003 after tracing the historical origin and evolution of the scheduled-worker contract.

This checkpoint is observational only. It adds no runtime, daemon, scheduler, deployment, task claim, economic result or authorization.

## 1. Historical execution model was explicitly external-agent driven

The scheduled-worker protocol first appears in commit:

`42976ddc5cf26f95a034d6a45c0d614a0f3b4353`

Commit message:

`research os: add scheduled worker claim/lease/receipt protocol`

That commit adds only:

`research/research_os/runtime/SCHEDULED_WORKER_PROTOCOL.md`

The protocol explicitly states that it is for **"ChatGPT/Codex-style workers that wake periodically and operate on the durable Quant-Trade task queue."**

Its source-of-truth rule requires a worker to reconstruct context from GitHub on every wake and treats conversation memory as advisory only.

Its one-run algorithm is repository-state mediated rather than daemon-internal:

1. read fresh branch HEAD;
2. enumerate durable task files;
3. select at most one admissible `READY` task;
4. retain the task blob SHA;
5. re-read authority / forbidden actions;
6. claim with an optimistic blob-SHA update and bounded lease;
7. persist `ACTION_STARTED`;
8. execute only bounded allowed actions;
9. persist artifacts;
10. persist one receipt;
11. persist terminal event;
12. re-fetch and terminalize the task;
13. stop.

This is strong evidence that the intended execution engine at protocol introduction was an **external conversational/coding agent using GitHub itself as durable coordination state**, not a repository-contained long-running worker process.

## 2. Later protocol revisions preserve the same external-worker model

### Multi-stage lineage revision

Commit:

`0df659e93755837a0b73e9fe1dc6fe0e0c2ea55e`

Message:

`research os: switch scheduler protocol to one-lineage multi-stage workflows`

The revised text still explicitly targets **"ChatGPT/Codex-style workflow workers that wake periodically"**.

It adds durable execution constraints rather than a daemon implementation:

- `MAX_LINEAGES_PER_WAKE = 1`
- `MULTI_STAGE_SAME_LINEAGE = TRUE`
- `MAX_STAGES_PER_WAKE = 5`
- `SELF_VALIDATION = FORBIDDEN`
- fresh-state re-read before every stage
- durable persistence after every meaningful stage
- explicit lane separation between discovery, evidence/data, independent challenge and integration/portfolio
- downstream handoff only when the claimed task explicitly authorizes it
- the four hard authority denials survive handoffs

### Deterministic empty-queue refill revision

Commit:

`9b04b7db5c33777074383bec7cc82d9f69d0782e`

Message:

`protocol: define bounded empty-queue refill exception`

This revision adds:

- `FREE_FORM_WORK_INVENTION = FORBIDDEN`
- queue refill only by the `integrator_portfolio` / `control_integrator` stewardship lane
- refill only after a fresh global scan proves `READY_TASKS_GLOBAL = 0` and `CLAIMED_TASKS_GLOBAL = 0`
- at most one deterministic producer task derived from `RESEARCH_FRONTIER.json`
- stable derivation key
- Legacy screening required before any candidate freeze
- all four hard authority flags remain `false`
- the steward must stop after refill and may not execute the derived producer task in the same wake
- `NOOP_FRONTIER_EXHAUSTED` when the bounded frontier is exhausted

This confirms that autonomous continuation was designed as **bounded external-agent orchestration over durable GitHub contracts**, not as unlimited self-generated research.

### Queue observability revision

Commit:

`b3b04efd99d18cbcefd0256d6f6f8ff3a69a1522`

Message:

`runtime: make Live Lab queue state explicit`

The protocol gains conservative queue-state semantics:

- `WORKING`
- `QUEUED`
- `WAITING`
- `IDLE`
- `UNKNOWN`

`IDLE` is permitted only after a fresh global task scan proves no `READY` and no `CLAIMED` tasks. Worker inactivity alone is explicitly insufficient.

Again, this changes the durable contract/observability model rather than introducing an in-repository worker implementation.

## 3. Modern tree remains consistent with that design

At modern Research OS reference:

`d0dc70f5dd71f3e6cb8097d2f15807bb99ebc8ec`

The reviewed runtime directory contains only contracts/state plus a simulator:

- `CAPABILITY_REGISTRY.json`
- `CONTROL_PLANE.json`
- `RESEARCH_FRONTIER.json`
- `SCHEDULED_WORKER_PROTOCOL.md`
- `WORKER_REGISTRY.sim.json`
- `WORKFLOW_LANES.json`
- `workflow_simulator.py`

The GitHub Actions surface `research-os-autonomous-loop-ci.yml` runs only pre-production simulation tests.

The multi-engine Python pipeline forces `synthetic_only=True` and reports `production_workers=false`.

The older `builder/research-os-autonomous-econ-readiness-port-20261016` tip is an ancestor of the modern line; the modern line is 75 commits ahead and the observed delta consists largely of durable tasks/events/receipts/assessments/hypotheses. No repository-contained executor was introduced by that compared delta.

## 4. Refined executor finding

Checkpoint 003 used the scoped statement:

`PRODUCTION_EXECUTOR_OBSERVED_IN_REVIEWED_MODERN_PATH = FALSE`

After historical tracing, the more precise classification is:

- `REPOSITORY_CONTAINED_PRODUCTION_EXECUTOR_OBSERVED = FALSE`
- `EXTERNAL_CHATGPT_CODEX_WORKER_MODEL_EXPLICIT_IN_PROTOCOL = TRUE`
- `GITHUB_DURABLE_STATE_IS_EXECUTION_COORDINATION_CONTRACT = TRUE`
- `EXTERNAL_SCHEDULER_OR_WAKE_MECHANISM_EXISTENCE_PROVEN_BY_REPOSITORY = FALSE`

The last line is important: the repository proves the contract expected of a periodically awakened external agent, but it does not by itself prove what external scheduler/service actually performed those wakes at any particular time.

## 5. Oracle implication

Oracle/OCI must not be treated as permission to invent a second autonomous architecture.

The safest architecture implied by existing evidence is:

```text
Oracle/OCI host or wake trigger
        ↓
existing external-agent worker contract
        ↓
fresh GitHub state reconstruction
        ↓
claim/lease via blob SHA
        ↓
existing lane/task authority checks
        ↓
bounded stage execution
        ↓
GitHub artifacts/events/receipt/task terminalization
```

NOT:

```text
Oracle VM
  ↓
new ad-hoc scheduler/executor
  ↓
new private state or parallel queue
  ↓
bypass / reinterpret existing GitHub contracts
```

Therefore:

`ORACLE_MAY_BE_HOST_OR_WAKE_INFRASTRUCTURE = POTENTIALLY_COMPATIBLE`

but:

`ORACLE_MAY_DEFINE_NEW_EXECUTION_SEMANTICS = FALSE`

and, given the still-unresolved UST authority-precedence conflict and incomplete scientific-memory coverage:

`ORACLE_AUTONOMOUS_ACTIVATION_SAFE = FALSE`

## 6. Crash/restart properties already implied by the contract

The existing protocol provides several useful restart/concurrency invariants that any eventual Oracle wake path must preserve:

- fresh GitHub context reconstruction on every wake;
- optimistic blob-SHA task claim;
- bounded lease generation;
- no force overwrite after a claim race;
- lease expiry alone does not justify blind stealing;
- durable `ACTION_STARTED` before bounded execution;
- durable artifacts after meaningful stages;
- exactly one receipt per wake/task contract;
- fresh task re-fetch before terminal transition;
- global queue rescan before refill;
- one lineage per wake;
- no producer execution in the same wake as empty-queue refill.

These are contract-level protections. They are not yet proof that every historical external worker implementation followed them perfectly.

## 7. Existing blockers remain unchanged

This refinement does **not** remove any blocker from Checkpoint 003.

Still unresolved:

1. UST durable authority precedence is contradictory: canonical/global economic-experiment authority is false while candidate-local post-freeze receipts claim bounded outcome authorization.
2. PR #1 scientific memory is absent from the reviewed Legacy ledger in important families, so anti-restart completeness is not proven.
3. OCI branch remains an older diverged patch rail and is unsafe for wholesale merge.
4. The actual external wake/scheduler implementation, if any, is outside what the repository alone proves.

## Current verdict

- `COVERAGE_COMPLETE = FALSE`
- `SAFE_TO_CONSOLIDATE = FALSE`
- `SAFE_TO_WHOLESALE_MERGE_OCI = FALSE`
- `REPOSITORY_CONTAINED_PRODUCTION_EXECUTOR_OBSERVED = FALSE`
- `EXTERNAL_CHATGPT_CODEX_WORKER_MODEL_EXPLICIT_IN_PROTOCOL = TRUE`
- `EXTERNAL_WAKE_MECHANISM_PROVEN = FALSE`
- `AUTHORITY_PRECEDENCE_CONFLICT = TRUE`
- `SCIENTIFIC_IDENTITY_COVERAGE_COMPLETE = FALSE`
- `ORACLE_AUTONOMOUS_ACTIVATION_SAFE = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

## Next forensic work

1. Build a semantic identity map of the PR #1 non-ML lineage (#0–#110 completed; #111–#112 untested) by economic mechanism/exposure family rather than by filename alone.
2. Separate each historical individual verdict from family-level statistical evidence and adaptive-trial context.
3. Crosswalk those families against the current Legacy ledger and current Research OS identities without mutating the operational ledger during audit.
4. Search for any external-wake configuration documented elsewhere in reachable branches/commits, while keeping absence claims scoped to what repository evidence proves.
5. Keep authority-precedence conflict fail-closed until durable precedence is established.
