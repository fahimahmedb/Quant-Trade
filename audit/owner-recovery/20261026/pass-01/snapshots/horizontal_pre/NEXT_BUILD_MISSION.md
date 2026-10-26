# Current Build / Mission Router

> **CURRENT AUTHORITY — 2026-09-21**
>
> Historical routing remains available in Git history. This file is intentionally kept
> compact and should describe only the live routing surface.

## North Star

Read first:

1. `QUANT_NORTH_STAR.md`
2. `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`
3. the exact active mission/handoff after resolving its live branch HEAD and CI

## Active primary rails

### Rail A — Gate-B / target host

Current state:

```text
F11_REPOSITORY_DEFECT = CLOSED
TARGET_HOST_READ_ONLY_REBIND = PASS
GATE_B_RUN_RESERVED = TRUE

GATE_B_RUN_ID =
gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811

GATE_B_ATTEMPT_NUMBER = 1

ACTIVATION_SEALED = FALSE
ACTIVATION_CONSUMED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
```

Current blocker:

`GATE_B_ACTIVATION_SEAL_PREP = BLOCKED_MISSING_CONCRETE_ROUTE1_MUTATION_PACK`

Active bounded Builder:

`builder/gate-b-route1-concrete-mutation-pack-2026-09-21@6e4f37d77d8ddb7cab4e53133e6c8570d3e9fc25`

Mission:

`handoff/BUILDER_GATE_B_ROUTE1_CONCRETE_MUTATION_PACK_MISSION_2026-09-21.md`

Mission-head CI:

`35641260071 = COMPLETED / SUCCESS`

Activation-correction authority:

`blue/gate-b-activation-seal-host-relay-2026-09-21@ad1b4d318c9e3657326e81b94cb9710b3953ffcd`

Next Rail-A flow:

```text
Route-1 concrete mutation pack
-> Blue reception
-> seal existing reserved run activation
-> final host freshness check
-> consume activation exactly once
-> bounded Gate-B execution
-> Blue Gate-B evidence reception
-> possible Gate-B PASS
-> later t0 boundary
```

Do NOT reserve another Gate-B run.

### Rail B — first economic vertical

Builder delivery:

`builder/post-p0-first-vertical-shadow-loop-2026-09-21@5c8b5b71ef627ac0ec0faa509edc40b7d9d0c4df`

Exact-head CI:

`35639267629 = COMPLETED / SUCCESS`

Builder disposition:

`BUILDER_VERTICAL_SHADOW_LOOP = READY_FOR_INDEPENDENT_REVIEW`

Delivered milestones:

```text
M1_SCIENTIFIC_ARTIFACT = GREEN
M2_RESEARCH_ECONOMIC_BOUNDARY = GREEN
M3_DESK_BOOK_BOUNDARY = GREEN
M4_LEARNING_E2E = GREEN
FULL_SUITE_RESULT = GREEN
```

Current next step:

`BLUE_BUILDER_RECEPTION -> ONE_BOUNDED_INDEPENDENT_ASTRA_REVIEW -> BLUE_FINAL_RECEPTION`

Do NOT reopen general science design, S11, cohort geometry, Economic Question Map,
or launch another competing Product Builder absent a concrete contradiction.

## Frozen production identity

```text
CANDIDATE_SHA =
4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072

GIT_TREE =
4d15ef6f471213ee6ab56337b555d2906ef9bf16

VERIFIED_INPUT_TREE_DIGEST =
sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2
```

## Global safety state

```text
P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
```

## Mission-dispatch discipline

Before extending or reopening substantial work, record:

```text
ECONOMIC_PROGRESS =
REMAINING_BLOCKER =
EXIT_CONDITION =
```

Prefer one bounded owner and one exit condition. Do not dispatch another audit merely
because another audit is possible.

## Branch hygiene

Use:

`governance/GITHUB_BRANCH_HYGIENE_2026-09-21.md`

for the authoritative list of active, frozen, historical and superseded branches.
