# BLUE — PROJECT REACQUISITION — 2026-09-21

This file is the compact restart surface for a fresh Blue session.

Historical detail is preserved in Git history and in the individual mission/handoff files.
Do not infer current state from older override blocks.

## 1. Highest authority

Read:

1. `QUANT_NORTH_STAR.md`
2. `NEXT_BUILD_MISSION.md`
3. `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`
4. exact active mission/handoff after live HEAD/CI verification

## 2. Current two-rail state

### Rail A — Gate-B / target host

```text
F11_REPOSITORY_DEFECT = CLOSED
TARGET_HOST_READ_ONLY_REBIND = PASS
GATE_B_RUN_RESERVED = TRUE
ACTIVATION_SEALED = FALSE
ACTIVATION_CONSUMED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
```

Reserved run:

```text
GATE_B_RUN_ID =
gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811

GATE_B_ATTEMPT_NUMBER = 1

RUN_RESERVATION_DIGEST =
sha256:97dac3e09e453dae189111c6f6d014aa2b426dea532bae6ae51de016c37ed8bc

REVOCATION_EPOCH = 1

REVOCATION_REFERENCE =
gate-b-host-relay-preseal-2026-09-21-initial-epoch
```

Authority storage:

`/var/lib/quant-p0-qualification/gate-b-authority`

Current activation blocker:

`BLOCKED_MISSING_CONCRETE_ROUTE1_MUTATION_PACK`

Active Builder:

`builder/gate-b-route1-concrete-mutation-pack-2026-09-21@6e4f37d77d8ddb7cab4e53133e6c8570d3e9fc25`

Exact-head CI:

`35641260071 = COMPLETED / SUCCESS`

Do NOT reserve another run.

### Rail B — first vertical economic loop

Final Builder:

`builder/post-p0-first-vertical-shadow-loop-2026-09-21@5c8b5b71ef627ac0ec0faa509edc40b7d9d0c4df`

Exact-head CI:

`35639267629 = COMPLETED / SUCCESS`

Disposition:

`BUILDER_VERTICAL_SHADOW_LOOP = READY_FOR_INDEPENDENT_REVIEW`

Current next owner sequence:

`BLUE reception -> one independent Astra review -> Blue final reception`

No second Product Builder is authorized.

## 3. Frozen production candidate

```text
CANDIDATE_SHA =
4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072

GIT_TREE =
4d15ef6f471213ee6ab56337b555d2906ef9bf16

VERIFIED_INPUT_TREE_DIGEST =
sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2
```

## 4. North-Star economic loop

Target Product loop:

`Forward -> Research -> Economic -> SIZE -> RISK -> FILLS -> BOOK -> Learning`

The One Big Build implements this first vertical in isolated shadow/paper form.

## 5. Current prohibitions

```text
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
ACTIVATION_CONSUMED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
```

## 6. Anti-drift rule

Before creating or reopening substantial work:

```text
ECONOMIC_PROGRESS =
REMAINING_BLOCKER =
EXIT_CONDITION =
```

Do not reopen:
- F11;
- S11;
- cohort geometry;
- Economic Question Map;
- general first-vertical architecture;

unless a new concrete contradiction is reproduced.

## 7. Branch hygiene

See:

`governance/GITHUB_BRANCH_HYGIENE_2026-09-21.md`

Only branches classified ACTIVE or FROZEN AUTHORITY should be used as starting points.
Historical and superseded branches remain traceability objects, not routing authorities.
