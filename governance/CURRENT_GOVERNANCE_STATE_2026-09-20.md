# CURRENT GOVERNANCE STATE — 2026-09-21

This file is the compact current-state authority. Older governance states remain in Git history.

## 1. North Star

Quant exists to increase long-run real wealth after real frictions through a persistent,
traceable system that discovers, falsifies, selects, sizes, executes and learns from market edge.

Core loop:

`Forward -> Research -> Economic -> SIZE -> RISK -> FILLS -> BOOK -> Learning`

`NO_TRADE` is a valid economic decision.

## 2. Frozen production candidate

```text
GATE_A_V4_REPOSITORY_DISPOSITION = PASS

CANDIDATE_SHA =
4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072

GIT_TREE =
4d15ef6f471213ee6ab56337b555d2906ef9bf16

VERIFIED_INPUT_TREE_DIGEST =
sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2

SELECTED_V4_CI_RUN = 35536353538
V4_CI_ARTIFACT_ID = 10612758620
V4_CI_ARCHIVE_DIGEST =
sha256:06c690203d589e389847cd345809480da2b99254fe7fd7f38b82c6bf5d54659a
```

## 3. Rail A — Gate-B / target host

Closed/prepared:

```text
F1_SCHEMA = CLOSED_REPOSITORY_EVIDENCE
F5_ROUTE1_FEASIBILITY = CLOSED
F11_REPOSITORY_DEFECT = CLOSED
V4_ACTIVATION_PRESTAGE = READY
TARGET_HOST_READ_ONLY_REBIND = PASS
```

Authoritative real run:

```text
GATE_B_RUN_RESERVED = TRUE

GATE_B_RUN_ID =
gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811

GATE_B_ATTEMPT_NUMBER = 1

RUN_RESERVATION_DIGEST =
sha256:97dac3e09e453dae189111c6f6d014aa2b426dea532bae6ae51de016c37ed8bc

REVOCATION_EPOCH = 1

REVOCATION_REFERENCE =
gate-b-host-relay-preseal-2026-09-21-initial-epoch

RUN_AUTHORITY_PARENT =
/var/lib/quant-p0-qualification/gate-b-authority
```

Current blocker:

`GATE_B_ACTIVATION_SEAL_PREP = BLOCKED_MISSING_CONCRETE_ROUTE1_MUTATION_PACK`

Current active Builder:

`builder/gate-b-route1-concrete-mutation-pack-2026-09-21@6e4f37d77d8ddb7cab4e53133e6c8570d3e9fc25`

Exact-head CI:

`35641260071 = COMPLETED / SUCCESS`

Corrected activation authority:

`blue/gate-b-activation-seal-host-relay-2026-09-21@ad1b4d318c9e3657326e81b94cb9710b3953ffcd`

State:

```text
ACTIVATION_SEALED = FALSE
ACTIVATION_CONSUMED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
```

## 4. Rail B — first economic vertical

Builder:

`builder/post-p0-first-vertical-shadow-loop-2026-09-21@5c8b5b71ef627ac0ec0faa509edc40b7d9d0c4df`

Exact-head CI:

`35639267629 = COMPLETED / SUCCESS`

Disposition:

`BUILDER_VERTICAL_SHADOW_LOOP = READY_FOR_INDEPENDENT_REVIEW`

Delivered:

```text
M1_SCIENTIFIC_ARTIFACT = GREEN
M2_RESEARCH_ECONOMIC_BOUNDARY = GREEN
M3_DESK_BOOK_BOUNDARY = GREEN
M4_LEARNING_E2E = GREEN
FULL_SUITE_RESULT = GREEN
```

Next:

`BLUE_BUILDER_RECEPTION -> ONE_BOUNDED_INDEPENDENT_ASTRA_REVIEW -> BLUE_FINAL_RECEPTION`

Product integration remains paused until that bounded review/reception completes.

## 5. Safety and capital state

```text
P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
```

## 6. Do-not-reopen list

Absent a new reproduced contradiction, do not reopen:

- F11 repository lock/path identity;
- F1 evidence-schema repair;
- F5 Route-1 feasibility;
- S11 dependence interval challenge;
- first-slice cohort geometry;
- Economic Question Map;
- general first-vertical architecture;
- frozen V4 production bytes.

## 7. Mission discipline

Before substantial work:

```text
ECONOMIC_PROGRESS =
REMAINING_BLOCKER =
EXIT_CONDITION =
```

One concrete blocker -> one bounded owner -> one exit condition.

## 8. Branch hygiene

See:

`governance/GITHUB_BRANCH_HYGIENE_2026-09-21.md`
