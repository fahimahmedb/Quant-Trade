# BLUE — Long-Horizon Execution Protocol & Project Plan — 2026-09-20

## Purpose

This is Blue's durable operating contract while Work/Astra capacity is constrained. It exists to maximize verified progress in ordinary Chat mode without pretending that one chat turn is multiple independent agents or that work continues asynchronously after the response ends.

Read `QUANT_NORTH_STAR.md` first. The governing decision test remains: does this move Quant closer to a persistent autonomous system that can discover, select and monetize real edge while preserving state and learning from outcomes?

## Maximum-effort method in Chat

Current mode: GPT-5.6 Sol with user-selected High reasoning. Blue uses six enforced passes:

1. Planner — objective, constraints, acceptance criteria, stopping conditions.
2. Investigator — repository evidence plus relevant external prior art.
3. Builder — smallest durable artifact/change that advances the objective.
4. Red Team — counterexamples, wrong-target tests, hidden assumptions, boundary violations.
5. Verifier — exact files/diffs/tests/CI/branch ownership/invariants.
6. Integrator — check against the whole Quant topology and terminal economic objective.

These are sequential roles executed by one model unless an actual separate agent/tool is invoked. They are not six independent hidden brains.

## Long-horizon reliability rules

- Every substantial task gets an explicit specification before execution.
- Meaningful conclusions are committed to GitHub. Repository evidence outranks chat recollection.
- Preferred proof loop: hypothesis -> discriminating test -> reproduce/falsify -> minimal fix -> exact-head verification -> checkpoint.
- Do not promote a theory into a blocker without reproduction or strong code-level proof.
- Before accepting an important conclusion, run an adversarial pass: could the test pass for the wrong reason? what assumption would make the conclusion false? did the change cross an ownership boundary? did we optimize a proxy instead of the North Star?
- Prefer narrow file/range retrieval, exact commit diffs and exact workflow/job state over indiscriminate repository dumps.
- Parallelize independent reads/research only. Serialize authoritative writes and acceptance decisions.
- Project memory is disabled, so durable project state belongs in GitHub.

## Workstreams

### WS-A — P0 / Astra Mission #1 closure

Obtain exact-head green CI and Astra's final Mission #1 verdict. Keep `t0 = NOT DECLARED` and `P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS` until explicitly proven. Do not write to the moving Astra proof chain without a reproduced reason.

### WS-B — Challenge the frozen P14D rule

Question: does `P0_CONTINUOUS_OBSERVATION_MIN = P14D` provide indispensable evidence that cannot be obtained faster by stronger fault injection, deterministic simulation, process/supervisor tests and bounded real target-host rodage?

P14D is currently frozen Blue/P0 governance, but it is not stated in `QUANT_NORTH_STAR.md`. It must not be silently weakened. Any change requires an explicit durable governance amendment with evidence.

Deliverables:
- provenance/rationale audit for P14D;
- external prior-art matrix;
- Quant P0 failure-mode matrix with COVERED / PARTIAL / NOT_COVERED / REAL-TIME-ONLY;
- residual value-of-time analysis;
- recommendation to retain, replace or shorten P14D;
- governance amendment only if the evidence supports it.

### WS-C — Forward Data reception

Only after final handoff, manual runner, truthful real live capture attempt and stable callable contract. Receive it as a leaf capability; do not wire Clock before the seam is frozen.

### WS-D — Economic V2 reception

Only after final handoff and acceptance evidence. Receiving the package does not make economics a runtime guarantee.

### WS-E — Forward -> Clock

Clock owns WHEN. Forward owns one bounded capture attempt. No second scheduler/service/thread/loop. Restart-safe state and admissibility must reach the actual Research consumer.

### WS-F — Economic -> Desk/Risk/Book

`CONTINUE` alone never grants exposure. Require exact capital/order eligibility; fail closed on stale/missing/conflicting assessments; preserve causal identity through SIZE/RISK/FILLS/BOOK. Economics and Risk are both necessary.

### WS-G — Whole-system E2E closure

Run the Blue integration matrix: Forward due/not-due, restart/idempotence, conflict/missing/unknown, admissible Forward -> Research, economics fail-closed, positive eligible shadow path, size consistency, durable intent -> Book, realized economics traceability, causal learning, and P0 isolation regression.

### WS-H — Astra #2 / #3

Astra #2 only after Desk actually enforces economics with durable journal/bypass tests. Astra #3 only after one coherent integrated product head passes the whole-system E2E matrix.

## Immediate ordered task queue

T01 — Persist this long-horizon operating protocol.
T02 — Refresh current P0 exact-head state.
T03 — Audit P14D provenance and identify the exact claims the calendar window was meant to establish.
T04 — Build external prior-art corpus: SQLite, RocksDB, FoundationDB, TigerBeetle, etcd, Git, systemd, Moby where relevant.
T05 — Map each prior-art failure mode to Quant P0 and classify coverage.
T06 — Decide the P14D challenge using evidence, not a preference for speed.
T07 — Persist a P14D decision memo and any explicit governance amendment.
T08 — Refresh Forward/Economic branches and triggers.
T09+ — Execute newly unblocked integration gates one at a time.

## Decision rule for P14D

Choose the least calendar time that provides equal or stronger evidence for capture integrity, PIT reconstructability and the visibility firewall. Account for opportunity cost because delayed qualification slows the global Quant system, but do not trade away an irreplaceable temporal proof merely for speed.

## Stop conditions

Stop a line when the next step requires an unavailable target host/credential, would mutate qualifying P0 runtime without authority, depends on a still-moving branch contract, or cannot be evidenced honestly with available tools. Persist the exact blocker and smallest next action.

## Honesty constraints

Never claim background work continues after the response; never claim independent agents were used when they were not; never claim CI green before exact-head completion; never infer target-host behavior from container-only tests; never declare t0 or replace P14D without explicit governance evidence; never claim Forward/Economic final before their handoffs; never claim economics is enforced before Desk consumes it; never authorize real capital without authoritative superseding governance.

`REAL_CAPITAL_AUTHORIZED = FALSE` unless explicitly superseded.