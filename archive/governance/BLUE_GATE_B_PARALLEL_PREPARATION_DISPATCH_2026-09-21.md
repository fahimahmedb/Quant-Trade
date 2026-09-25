# BLUE — GATE B PARALLEL PREPARATION DISPATCH — 2026-09-21

## 0. Owner authorization and scope

Owner explicitly authorizes a temporary increase in pre-Gate-B parallelism.

This supersedes the earlier concurrency cap of two substantial workstreams ONLY
for independent, non-mutating preparation lanes.

Runtime mutation concurrency remains exactly:

`TARGET_HOST_MUTATING_WORKSTREAMS_MAX = 1`

No two agents may mutate the qualifying host/runtime concurrently.

## 1. Exact current authority

Blue authority before this dispatch:
`4c855dca152d237d2b8d86419ebc5e3a59acde42`

North Star blob:
`8295041a8d253636d8f8aab941b811dce64939d9`

Hybrid authority:
`P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1`

Promotion exact-head CI:
`35552847998 = COMPLETED / SUCCESS`

Current safety:
```text
TARGET_HOST_READY = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```

## 2. Read-only preflight result received

Operator branch:
`operator/gate-b-read-only-preflight-2026-09-21@44285788fce3d5d048b037dd8d1089e1f08f43e9`

Public handoff blob:
`48dfd849095362b924412f474a641010addd3406`

Disposition:
`GATE_B_ACTIVATION_PREP = BLOCKED_EXPECTED_V4_RELEASE_ABSENT_AND_SERVICE_VIEW_ON_REJECTED_V3`

Blockers:
1. expected frozen V4 release path is absent;
2. fixed service view still points to rejected V3.

Important non-blocking observations:
- host time/NTP suitable for preparation;
- loaded unit bytes match frozen V4 unit;
- durable-state mount identity is visible;
- service is failed/disabled;
- no approved restricted evidence root is yet bound;
- live process resource baseline unavailable while service is stopped.

No mutation occurred.

## 3. Temporary parallel lanes

### Lane A — V4 materialization + service-view activation prestage
Role: Builder / Codex.
Mission: prepare the exact sealed mutation plan needed to resolve the two
preflight blockers, WITHOUT executing it.

Must bind:
- exact V4 release source;
- exact release materialization procedure;
- exact service-view transition procedure;
- state preservation;
- mount ordering;
- rollback/terminal-failure behavior;
- explicit mutation-capability matrix;
- proposed evidence-root binding;
- fields still requiring activation-time observation.

No target-host mutation.

### Lane B — independent adversarial preactivation review
Role: Astra / Red Team.
Mission: independently attack the authoritative Gate-B pack plus the actual
read-only preflight findings.

Do not start from Lane A's conclusions.

Look for:
- unsafe or ambiguous V3->V4 transition;
- evidence contamination;
- materialization identity weakness;
- mount/state loss risk;
- hidden real-network path;
- activation/schema bypass;
- retry/run-id ambiguity;
- sanitization impossibility;
- evidence-retention gap.

No fixes and no target-host mutation.

### Lane C — Gate-B evidence reception prestage
Role: Builder / Codex.
Mission: prepare Blue's future Gate-B evidence acceptance matrix and validation
procedure from the authoritative JSON schema and B1-B10 contract.

No claim of PASS.
No target-host mutation.

### Lane D — Gate-C prospective event-plan prestage
Role: Builder / Codex.
Mission: prepare the prospective source-calendar event plan/template needed
after a future Gate-B PASS and t0 precommit.

Must not declare t0 or pick a retrospective launch.
No target-host mutation.

## 4. Convergence rule

All four lanes return to Blue.

Blue alone decides:
1. whether Lane A's mutation plan is acceptable;
2. whether Lane B found a blocker;
3. whether Lane C reception criteria are complete;
4. whether Lane D is prospectively usable;
5. whether to seal one concrete Gate-B activation.

Only after convergence may Blue authorize:

`GATE_B_MUTATION_AUTHORIZED = TRUE`

for exactly one unique `GATE_B_RUN_ID`.

## 5. Runtime serialization rule

Once activation is sealed:

```text
ONE Gate-B run
ONE operator
ONE GATE_B_RUN_ID
ONE evidence chain
ONE terminal result
```

No second mutating operator may run in parallel.

First mandatory FAIL makes that run terminal.

## 6. Capital / Product boundary

Parallelization does not alter:

```text
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```

This dispatch optimizes calendar time only; it does not weaken proof standards.
