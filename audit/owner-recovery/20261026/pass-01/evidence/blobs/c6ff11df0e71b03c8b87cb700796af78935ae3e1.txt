# CLAUDE CODE — POST-P0 VERTICAL ECONOMIC BUILD PREP MISSION — 2026-09-21

## Mission identity

ROLE:

`CLAUDE CODE / PRODUCT-ECONOMIC PREP BUILDER`

REPOSITORY:

`fahimahmedb/Quant-Trade`

WORK ONLY ON:

`parallel/claude-post-p0-vertical-build-prep-2026-09-21`

MISSION BASE SHA:

`c62f63219068373e759cb63c095d62084da584f3`

DO NOT CREATE ANOTHER BRANCH.

This is a parallel non-implementing Product/Economic mission while the P0/Gate-B
critical rail continues independently.

## 0. Hard branch / authority verification

First:

```bash
git fetch origin --prune
git rev-parse HEAD
git rev-parse origin/parallel/claude-post-p0-vertical-build-prep-2026-09-21
```

Verify the assigned branch descends from:

`c62f63219068373e759cb63c095d62084da584f3`

Before substantive work, read in full:

1. `QUANT_NORTH_STAR.md`
2. `governance/BLUE_CLAUDE_POST_P0_VERTICAL_BUILD_PREP_2026-09-21.md`
3. `governance/BLUE_WORK_ALLOCATION_PRE_GREEN_TO_ECONOMIC_LOOP_2026-09-21.md`
4. `governance/BLUE_POST_P0_VERTICAL_SHADOW_LOOP_PRESTAGE_PLAN_2026-09-21.md`
5. interface-map handoff from:
   `builder/post-p0-vertical-interface-map-2026-09-21@8d40af1f2333474d8f26509b61cb257d96f8772d`
   file:
   `handoff/BUILDER_POST_P0_VERTICAL_INTERFACE_MAP_2026-09-21.md`
6. Antigravity design from:
   `parallel/antigravity-post-p0-vertical-shadow-loop-design-2026-09-21@568eea1e028302e14f96a06eb2515bb89aa73ad4`
   file:
   `handoff/ANTIGRAVITY_POST_P0_VERTICAL_SHADOW_LOOP_DESIGN_2026-09-21.md`
7. canonical Forward:
   `parallel/claude-forward-data-2026-09-20@83521dbfdd90027c90d04adfb7d814593c2355c5`
8. canonical Economic:
   `parallel/claude-economic-v2-2026-09-20@35dff27b8fac53618da434ee6d31febbddcc0e69`
9. Blue Product spine:
   `cbf30c1bb38dd69c11fb64c523c3aec694116b9c`

Resolve those exact refs from GitHub/git. Do not assume moving branch names still match.

If any pinned authority cannot be resolved exactly, STOP with:

`CLAUDE_VERTICAL_BUILD_PREP = BLOCKED_AUTHORITY_MISMATCH`

## 1. Mission type

`READ_ONLY_ANALYSIS + PATCH_PLAN + TEST_SPEC + FUTURE_BUILDER_HANDOFF_ONLY`

You are NOT authorized to implement Product code now.

Do NOT modify:

- `src/`
- `tests/`
- `scripts/`
- `schemas/`
- workflows
- production config
- P0 runtime
- frozen V4
- target host

Do NOT merge or cherry-pick whole Forward or Economic branches.

Do NOT authorize:
- Product integration;
- live orders;
- real capital;
- Gate B;
- t0.

Your only repository write on this branch should be the final handoff/checkpoint for
this prep mission.

## 2. Fixed Blue decisions — do not reopen without concrete contradiction

### D1 — Research -> Economic

An explicit bridge is required.

It fails closed if Research cannot faithfully emit the frozen Economic
`EffectEstimate` coordinate.

No heuristic invention of missing statistical/economic fields.

Required refusal:

`NO_TRADE / EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE`

### D2 — SIZE

`FINAL_SIZE = min(ECONOMIC_MARGIN_SIZE, DESK_LIFECYCLE_CAP)`

Economic `MarginSizingRule` owns economic allocation.

Desk lifecycle sizing is only an upper cap.

Desk Risk remains downstream independent veto/throttle.

Zero size is valid.

### D3 — SHADOW authority

Research `VALIDATED` must not auto-promote to `SHADOW`.

Required authority sequence:

`RESEARCH_VALIDATED -> ELIGIBLE_FOR_ECONOMIC_ASSESSMENT -> ECONOMIC_VERDICT -> SHADOW | NO_TRADE`

### D4 — execution

Economic opening/execution modelling provides assumptions only.

Blue `ExecutionModel.fill` is the sole shadow fill that can feed Book mutation.

`verify_research_cost_consistency` must prevent the economic gate from assuming a
cheaper execution regime than the actual shadow execution model.

### D5 — provenance

Preserve one durable chain:

`ForwardObservation -> ResearchTicket -> EconomicAssessment -> OpportunityTicket -> DeskJournal -> Ledger -> LearningStore`

No second Book, execution engine, sizing engine or scheduler.

## 3. Core objective

Prepare the future implementation so completely that, once Blue authorizes isolated
Product implementation during Gate C, a Builder can implement the first vertical
economic shadow loop without repeating architecture analysis.

The future slice is exactly:

```text
one ForwardObservation
-> one ResearchTicket
-> one scientific VET disposition
-> one EconomicAssessment
-> one Economic SIZE
-> one Desk Risk decision
-> one shadow fill OR NO_TRADE
-> one persistent Book transition
-> one durable Learning/Memory outcome
```

This is not an alpha claim.

A correct `NO_TRADE` result is a first-class success path.

## 4. Exact code archaeology required

Inspect the exact current Blue Product-spine implementations and the pinned Forward
and Economic leaves.

At minimum resolve and document the actual current signatures / semantics of:

### Forward

- `src/quant/dataplane/forward_recorder.py`
  - `ForwardObservation`
  - `ForwardRecorder.as_of`
  - content address / ledger fingerprint
- `src/quant/dataplane/forward_admissibility.py`
  - forward-confirmation admission semantics
- any minimal DatasetRegistry / PricePanel boundary required by current factory code

### Research / Factory

- `src/autonomous_research/ticket.py`
  - `ResearchTicket`
- `src/quant/factory/workers.py`
  - `run_lane`
  - `_finish`
- `src/quant/factory/evaluate.py`
- `src/quant/factory/strategies.py`
  - `StrategyDefinition`
  - lifecycle transitions
  - `StrategyRegistry`

### Economic

From exact Economic V2:

- `src/quant/economics/decision.py`
  - `EffectEstimate`
  - `PortfolioInteraction`
  - `EconomicVerdict`
  - `economic_gate`
- `src/quant/economics/journal.py`
  - assessment identity / idempotence
- `src/quant/economics/sizing.py`
  - `MarginSizingRule`
  - `SizingPlan`
  - `size_lane`
- `src/quant/economics/capacity.py`
- `src/quant/economics/consistency.py`
  - `verify_research_cost_consistency`
- `src/quant/economics/opening.py`
  - modelling overlap with Desk execution

### Desk / Book / Learning

- `src/quant/desk/desk.py`
  - current VET / SIZE / RISK / FILLS / BOOK sequence
- `src/quant/desk/opportunity.py`
  - `OpportunityTicket`
- `src/quant/desk/risk.py`
- `src/quant/desk/execution.py`
  - `ExecutionModel.fill`
- `src/quant/desk/journal.py`
- `src/quant/book/ledger.py`
  - `apply_fill`
  - idempotence / operation IDs
- `src/quant/learning/store.py`
  - existing durable learning APIs

Do not trust prior handoff path forecasts blindly. Confirm everything in code.

## 5. Required semantic bridge design

Produce the exact future contract for:

### 5.1 Forward -> Research

Define:
- exact input type;
- exact PIT cutoff;
- exact provenance fields;
- how Forward content addresses/fingerprint are preserved;
- whether a DatasetRegistry-compatible materialized view is required;
- how `information_available_at` is derived without upgrading time authority.

Do not create a second data plane.

### 5.2 Research -> Economic

Define an explicit proposed function/class signature for the bridge.

It must make clear:
- what fields come from Research;
- what fields must already exist to form `EffectEstimate`;
- what fields cannot be derived safely;
- exact fail-closed condition;
- evidence-label/admissibility rule;
- sample/dataset provenance.

If current Research output cannot support a valid positive `EffectEstimate`, say so
and specify the smallest upstream Research output extension required.

Do not fake a positive path merely to make the future test easy.

### 5.3 Economic -> Desk

Define exact transfer object(s) or references needed for:
- assessment id;
- input fingerprint;
- verdict;
- margin;
- size;
- capacity;
- reasons;
- provenance.

Prefer adapting existing `OpportunityTicket` over introducing a new ticket family.

### 5.4 Desk -> Book -> Learning

Define:
- deterministic operation ID;
- upstream identifiers stored in DeskJournal;
- Book idempotence boundary;
- Learning outcome key;
- exact NO_TRADE persistence semantics;
- restart/replay behavior.

## 6. Required state machine

Write the exact proposed state transition table.

At minimum distinguish:

- research rejected;
- research validated but no valid Economic coordinate;
- Economic NO_TRADE;
- Economic KILL if applicable;
- Economic CONTINUE but size = 0;
- Economic CONTINUE + size > 0 + Risk veto;
- Economic CONTINUE + size > 0 + Risk approval + shadow fill;
- fill capacity-truncated;
- restart between assessment and Desk;
- restart after DeskJournal begin before Book commit;
- replay of same observation/opportunity.

For each state specify:
- terminal/nonterminal;
- next authority;
- durable record;
- whether Book may mutate;
- whether Learning must receive an outcome.

## 7. Future changed-path minimization

Start with the current forecast:

- `src/quant/integration/forward_adapter.py` — possible new glue;
- `src/quant/integration/econ_bridge.py` — possible new fail-closed bridge;
- `src/quant/factory/workers.py`;
- `src/quant/desk/desk.py`;
- `src/quant/learning/store.py`;
- `tests/integration/test_first_vertical_shadow_loop.py`.

Independently verify this list.

For every proposed path classify:

`NEW | MODIFY | REUSE_AS_IS | NOT_NEEDED`

If additional Product paths are genuinely required, justify them with a concrete
vertical-loop blocker.

Do not expand for code cleanliness alone.

## 8. Future acceptance test — specify exactly, do not implement yet

Target future test:

`tests/integration/test_first_vertical_shadow_loop.py`

Specify deterministic fixtures and assertions for at least:

### Path A — fail-closed NO_TRADE

Use a case where Research evidence cannot legally form the frozen Economic
coordinate OR where economics rejects after frictions.

Require:
- explicit terminal NO_TRADE reason;
- zero Book cash/position mutation;
- durable economic/Desk/learning provenance;
- replay idempotence;
- no accidental SHADOW promotion.

### Path B — positive-size SHADOW

Use a semantically valid fixture that actually supplies the required
`EffectEstimate` fields.

Do NOT synthesize missing fields through a production heuristic.

Require:
- research eligibility;
- Economic CONTINUE;
- positive Economic margin size;
- lifecycle cap composition;
- Risk approval;
- `ExecutionModel.fill` used exactly once;
- Ledger mutation exactly once;
- implementation shortfall preserved;
- full provenance chain;
- Learning record;
- replay idempotence.

### Path C — Risk veto / zero-size safety

Specify at least one control proving:
- Economic CONTINUE does not bypass Risk; or
- Economic size zero cannot accidentally fill.

## 9. Future Builder mission draft

Your handoff must contain a complete copy-paste-ready mission for:

`builder/post-p0-first-vertical-shadow-loop-2026-09-21`

The mission must include:

- exact future base selection rule;
- exact authorities;
- exact changed-path allowlist;
- exact forbidden areas;
- required tests;
- acceptance criteria;
- handoff name;
- final Builder status;
- no real-capital / no P0 runtime boundary.

Do NOT create that implementation branch during this prep mission.

## 10. Contradiction handling

If exact code contradicts D1-D5 or makes one impossible:

Do NOT silently redesign.

Record:

`BLUE_DECISION_REQUIRED_<ID>`

with:
- exact file/function;
- current behavior;
- contradiction;
- minimum options;
- consequence of each.

Only reopen a Blue decision when the contradiction is concrete.

## 11. Required final handoff

Write only:

`handoff/CLAUDE_POST_P0_VERTICAL_BUILD_PREP_2026-09-21.md`

Final handoff must include:

1. exact mission/base/final SHA information;
2. exact source refs verified;
3. exact inspected path inventory;
4. confirmed D1-D5 compatibility;
5. final data-contract chain;
6. function-level patch plan;
7. exact future changed-path budget;
8. state transition table;
9. provenance/idempotence/restart rules;
10. future E2E test specification;
11. complete future Builder mission;
12. remaining Blue decisions, if any;
13. opportunity-cost assessment;
14. safety state.

Allowed final status:

`CLAUDE_VERTICAL_BUILD_PREP = READY_FOR_BLUE_REVIEW`

or one precise blocker.

## 12. Safety state

Preserve:

```text
PRODUCT_CODE_MODIFIED = FALSE
PRODUCT_INTEGRATION = PAUSED
P0_RUNTIME_MUTATION = FALSE
TARGET_HOST_TOUCHED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
t0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
```

Commit and push only the final prep handoff to the assigned branch.

Return control to Blue.
