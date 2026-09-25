# BLUE — CLAUDE POST-P0 VERTICAL BUILD PREP — 2026-09-21

## 0. Status

`CLAUDE_VERTICAL_BUILD_PREP = AUTHORIZED / NON_IMPLEMENTING_PRODUCT_PREP`

`PRODUCT_INTEGRATION = PAUSED`

`P0_RUNTIME_MUTATION = FALSE`

`REAL_CAPITAL_AUTHORIZED = FALSE`

This authority opens one parallel Product/Economic workstream while the P0/Gate-B
critical rail continues independently.

It does NOT authorize Product implementation, merge, deployment, target-host
mutation, or capital activity.

The concurrency policy remains two substantial rails only:

1. Rail A — P0/Gate-B critical path.
2. Rail B — one isolated Product/Economic preparation lane.

No second Product Builder/Claude lane is authorized concurrently.

## 1. Authorities

Highest authority:
`QUANT_NORTH_STAR.md`

Work-allocation authority:
`governance/BLUE_WORK_ALLOCATION_PRE_GREEN_TO_ECONOMIC_LOOP_2026-09-21.md`

Vertical prestage:
`governance/BLUE_POST_P0_VERTICAL_SHADOW_LOOP_PRESTAGE_PLAN_2026-09-21.md`

Canonical Forward:
`parallel/claude-forward-data-2026-09-20@83521dbfdd90027c90d04adfb7d814593c2355c5`

Canonical Economic:
`parallel/claude-economic-v2-2026-09-20@35dff27b8fac53618da434ee6d31febbddcc0e69`

Blue Product spine:
`cbf30c1bb38dd69c11fb64c523c3aec694116b9c`

Interface map:
`builder/post-p0-vertical-interface-map-2026-09-21@8d40af1f2333474d8f26509b61cb257d96f8772d`

Antigravity design:
`parallel/antigravity-post-p0-vertical-shadow-loop-design-2026-09-21@568eea1e028302e14f96a06eb2515bb89aa73ad4`

## 2. Blue decisions now fixed for implementation planning

### D1 — Research -> Economic coordinate

ACCEPTED:

Research may feed Economic only through an explicit semantic bridge.

The bridge MUST fail closed if the research result cannot be represented faithfully
on the frozen Economic `EffectEstimate` coordinate.

It MUST NOT heuristically invent:
- `delta_hat`;
- `lower`;
- `upper`;
- confidence semantics;
- evidence labels;
- provenance.

Required fail-closed outcome:

`NO_TRADE / EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE`

Forward-captured data does not automatically become
`FORWARD_CONFIRMATION`; existing admissibility authority still controls that label.

### D2 — SIZE authority

ACCEPTED:

`FINAL_SIZE = min(ECONOMIC_MARGIN_SIZE, DESK_LIFECYCLE_CAP)`

Economic `MarginSizingRule` is the opportunity allocation authority.

Desk lifecycle `capital_fraction` is only the upper lifecycle cap.

Desk portfolio Risk remains the independent downstream veto/throttle.

Zero size is valid and must remain equivalent to a non-executed opportunity.

No second sizing engine may be created.

### D3 — SHADOW promotion

ACCEPTED:

Research `VALIDATED` MUST NOT auto-promote to `SHADOW`.

Required ordering:

`RESEARCH_VALIDATED -> ELIGIBLE_FOR_ECONOMIC_ASSESSMENT -> ECONOMIC_VERDICT -> SHADOW | NO_TRADE`

Only an economically eligible/continuing opportunity may reach SHADOW consideration.

### D4 — execution model

ACCEPTED:

- Economic `OpeningExecutionModel` may supply assumptions/cost modelling to the
  economic gate.
- Blue `ExecutionModel.fill` is the sole shadow-fill authority that feeds Book
  mutation.
- `verify_research_cost_consistency` must bind the assumptions so Economic cannot
  assume a cheaper execution regime than the actual shadow fill model.

No duplicate booking or fill authority.

### D5 — provenance

ACCEPTED minimum durable chain:

`ForwardObservation -> ResearchTicket -> EconomicAssessment -> OpportunityTicket -> DeskJournal -> Ledger -> LearningStore`

Exact upstream identifiers/digests must remain recoverable through the chain.

No second Book is authorized.

## 3. Current Claude Code mission type

Authorized mission type:

`READ_ONLY_ANALYSIS + PATCH_PLAN + TEST_SPEC + FUTURE_BUILDER_HANDOFF_ONLY`

Claude Code may:
- inspect all exact authorities above;
- compare exact branches/SHAs;
- inspect Product code at the Blue spine;
- inspect canonical Forward/Economic implementations;
- identify the smallest semantically correct patch set;
- draft exact function-level changes;
- draft acceptance-test structure and fixtures in prose/pseudocode;
- identify import/dependency conflicts;
- identify deterministic operation IDs and provenance fields;
- produce a future Builder mission that can be executed once Gate-C implementation
  work is authorized.

Claude Code must NOT yet:
- modify Product source;
- modify tests;
- create schemas/scripts/workflows;
- merge/cherry-pick Forward or Economic leaves;
- modify P0 runtime;
- touch target host;
- authorize Product integration;
- submit live orders;
- authorize real capital.

## 4. Required planning target

Future implementation branch remains:

`builder/post-p0-first-vertical-shadow-loop-2026-09-21`

The future implementation must prove exactly one vertical slice:

```text
one ForwardObservation
-> one ResearchTicket
-> scientific VET disposition
-> one EconomicAssessment
-> one SIZE/RISK decision
-> one shadow fill OR NO_TRADE
-> one persistent Book transition
-> one durable Learning/Memory record
```

The future implementation MUST include both:

1. legitimate `NO_TRADE` path;
2. positive-size `SHADOW` path.

## 5. Required Claude deliverable

Claude must produce:

`handoff/CLAUDE_POST_P0_VERTICAL_BUILD_PREP_2026-09-21.md`

It must contain:

1. exact source SHAs actually inspected;
2. exact current Product-spine paths/functions;
3. exact Forward/Economic paths/functions to semantically reuse;
4. no-whole-leaf-merge proof/decision;
5. final proposed changed-path list;
6. function/class-level patch plan;
7. exact new glue interfaces and signatures;
8. exact provenance identifiers carried at every boundary;
9. exact state-machine transition changes;
10. exact sizing/risk ordering;
11. execution-cost consistency placement;
12. idempotence and restart semantics;
13. `NO_TRADE` acceptance-test specification;
14. positive SHADOW acceptance-test specification;
15. full future Builder mission text;
16. any remaining `BLUE_DECISION_REQUIRED` items that cannot be resolved from
    existing authority.

Claude must minimize unresolved decisions. It may not reopen D1-D5 above unless it
finds a concrete contradiction in exact code.

## 6. Future implementation changed-path budget

Expected minimum implementation surface from current design:

- `src/quant/integration/forward_adapter.py` — new narrow glue;
- `src/quant/integration/econ_bridge.py` — new fail-closed bridge;
- `src/quant/factory/workers.py` — remove implicit VALIDATED -> SHADOW authority;
- `src/quant/desk/desk.py` — insert Economic gate/SIZE before Risk;
- `src/quant/learning/store.py` — terminal outcome/provenance ingestion;
- `tests/integration/test_first_vertical_shadow_loop.py` — deterministic E2E proof.

Claude must independently confirm whether every path is truly required.

Do not expand this budget merely for architectural neatness.

## 7. Phase gate

This Claude prep may complete now.

Actual Product implementation remains gated until Blue explicitly records the
appropriate Gate-C isolated-build authorization.

Until then:

```text
PRODUCT_IMPLEMENTATION_AUTHORIZED = FALSE
PRODUCT_INTEGRATION = PAUSED
P0_RUNTIME_MUTATION = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
```

## 8. Mission-selection rule

The work must answer:

`WHAT ECONOMIC UNCERTAINTY DOES THIS CLOSE?`

For this mission:

Can the already-existing Forward, Research, Economic, Desk, Book and Learning
surfaces be joined through the smallest fail-closed, provenance-preserving,
friction-aware vertical slice without creating duplicate economic/execution
authority?

If the proposed work does not help answer that question, defer it.
