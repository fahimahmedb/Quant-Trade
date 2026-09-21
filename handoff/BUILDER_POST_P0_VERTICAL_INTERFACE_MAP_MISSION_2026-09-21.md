# BUILDER — POST-P0 VERTICAL INTERFACE MAP MISSION — 2026-09-21

## 0. Mission type

`READ_ONLY_ANALYSIS + HANDOFF_ONLY`

This mission exists to prepare the first post-P0 economic vertical slice.

It does NOT authorize Product implementation, merging, deployment, target-host
mutation, P0 runtime changes, scientific-claim changes, or capital.

## 1. Authority

Read first:

1. `QUANT_NORTH_STAR.md`
2. `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`
3. `governance/BLUE_WORK_ALLOCATION_PRE_GREEN_TO_ECONOMIC_LOOP_2026-09-21.md`
4. `governance/BLUE_POST_P0_VERTICAL_SHADOW_LOOP_PRESTAGE_PLAN_2026-09-21.md`
5. `governance/BLUE_P0_POST_ASTRA_GREEN_EXECUTION_CONTROL_PLAN_2026-09-21.md`

North Star is highest authority absent explicit owner revision.

Mission-control start SHA:

`cbf30c1bb38dd69c11fb64c523c3aec694116b9c`

This Builder branch was created exactly from that SHA.

## 2. Exact comparison inputs

Canonical Forward:

`parallel/claude-forward-data-2026-09-20@83521dbfdd90027c90d04adfb7d814593c2355c5`

Canonical Economic:

`parallel/claude-economic-v2-2026-09-20@35dff27b8fac53618da434ee6d31febbddcc0e69`

Current Blue/Research/Book baseline:

`blue/master-v2-2026-09-20@cbf30c1bb38dd69c11fb64c523c3aec694116b9c`

Do not replace exact SHAs with moving branch names in the final evidence.

## 3. Mission objective

Build one exact interface map for:

```text
SOURCE / FORWARD DATA
        ->
RESEARCH CANDIDATE
        ->
VET
        ->
ECONOMIC ASSESSMENT
        ->
SIZE
        ->
RISK
        ->
SHADOW FILL
        ->
PERSISTENT BOOK
        ->
LEARNING / MEMORY
        ->
RESCAN / RETIRE / REPLACE
```

The goal is to identify the smallest missing glue needed for one end-to-end
shadow slice after P0 exit.

Do NOT optimize for architecture completeness.

Do NOT propose generalized infrastructure without a concrete consumer in the
first vertical slice.

## 4. Required surfaces to inspect

At minimum inspect:

### Forward / Data
- `src/quant/dataplane/forward_capture.py`
- `src/quant/dataplane/forward_recorder.py`
- `src/quant/dataplane/forward_admissibility.py`
- `src/quant/dataplane/forward_coverage.py`
- relevant forward scripts/tests/handoffs

### Research
- `src/autonomous_research/scanner.py`
- `src/autonomous_research/orchestrator.py`
- `src/autonomous_research/backtest.py`
- `src/autonomous_research/runtime.py`
- `src/autonomous_research/pipeline.py`
- `src/autonomous_research/ticket.py`
- `src/autonomous_research/memory.py`
- `research/opportunity_map.json`
- `research/memory.jsonl`
- `schemas/research_ticket.schema.json`

### Economic
- `src/quant/economics/frictions.py`
- `src/quant/economics/capacity.py`
- `src/quant/economics/sizing.py`
- `src/quant/economics/decision.py`
- `src/quant/economics/timeline.py`
- `src/quant/economics/value.py`
- `src/quant/economics/states.py`
- `src/quant/economics/recipe.py`
- relevant economic tests/handoffs

### Book / persistence
- `src/quant/book/ledger.py`
- `schemas/book_state.schema.json`

### Existing whole-loop/runtime clues
- `scripts/research_runtime.py`
- `scripts/demo_research_runtime.py`
- `scripts/economic_dashboard.py`
- relevant integration tests

## 5. Questions that MUST be answered

1. What exact object/record does canonical Forward produce?
2. Which fields preserve source provenance and public/PIT timing?
3. What exact Research input can consume it today?
4. What exact Research output/ticket/hypothesis exists today?
5. What is missing for a real `VET` disposition?
6. Which fields are required by the economic engine?
7. Where are fees, spread, slippage, financing and capacity applied?
8. Is SIZE already represented by an existing object/function?
9. Is RISK already represented independently from economic sizing?
10. Does a shadow-fill abstraction already exist?
11. If not, what is the minimum fill object needed?
12. What exact API/state transition exists for Persistent Book?
13. Can Book preserve cash, positions, realized/unrealized P&L and provenance?
14. How can Learning/Memory consume:
    - accepted opportunities;
    - rejects;
    - no-trade decisions;
    - fills;
    - misses;
    - slippage;
    - errors;
    - decay;
    - retirement?
15. Which existing components are semantically duplicated/conflicting between
    Forward/Economic/current Blue?
16. What is the smallest coherent integration baseline?
17. What exact glue is missing for one vertical slice?

## 6. Classification required for every relevant component

Use only:

- `REUSE_AS_IS`
- `ADAPT`
- `MISSING_GLUE`
- `DEFER`
- `CONFLICT / BLUE_DECISION_REQUIRED`

For each classification include:
- exact path;
- exact source SHA;
- function/class/schema names;
- what role it would play in the vertical loop;
- why the classification is justified.

## 7. First vertical slice definition

Propose the smallest slice that can prove:

```text
one source observation
-> one research ticket
-> one explicit hypothesis/claim
-> one VET disposition
-> one economic assessment
-> one SIZE/RISK result
-> one shadow fill OR NO_TRADE
-> one persistent Book transition
-> one Learning/Memory record
```

This is a functional integration proof.

It is NOT:
- proof of alpha;
- proof of profitability;
- capital readiness;
- permission to trade.

`NO_TRADE` must be a first-class successful outcome.

## 8. Required output

Write exactly one primary handoff:

`handoff/BUILDER_POST_P0_VERTICAL_INTERFACE_MAP_2026-09-21.md`

The handoff must include:

1. exact branch HEAD;
2. exact source SHAs inspected;
3. a component/interface table;
4. exact data-contract chain;
5. provenance/PIT propagation map;
6. VET gap analysis;
7. economic/friction/sizing/risk map;
8. shadow-fill gap analysis;
9. Book transition map;
10. Learning/Memory feedback map;
11. conflict/duplication register;
12. minimum missing-glue list;
13. proposed first vertical slice;
14. proposed implementation order;
15. explicit list of work to DEFER;
16. Blue decisions required, if any;
17. final status:
   `PRODUCT_PRESTAGE_INTERFACE_MAP = READY_FOR_BLUE_REVIEW`
   or a precise blocker.

## 9. No-code rule

Do NOT modify:
- `src/`
- `tests/`
- `scripts/`
- `schemas/`
- production config/workflows

Do NOT cherry-pick or merge any canonical leaf.

The only allowed committed mission output is:
- this mission document;
- the final handoff/checkpoint documents for this mission.

If a code defect is discovered, document it as:
`FINDING`
with exact reproduction evidence and return to Blue.

Do not fix it.

## 10. Scientific/economic discipline

Distinguish:
- FACT
- CLAIM
- INFERENCE
- RECOMMENDATION
- UNKNOWN

Do not infer edge or profitability from code structure.

Do not treat:
- backtest presence;
- green CI;
- sizing code;
- Book code;
- shadow code

as evidence of economic edge.

The question is interface readiness for future economic learning.

## 11. Stop conditions

STOP and return to Blue if:
- an exact source SHA is unavailable;
- canonical Forward/Economic branch has moved from the pinned SHA and exact bytes
  cannot be recovered;
- a major semantic conflict means choosing one branch changes the economic or
  scientific claim;
- completing the requested map would require modifying Product code;
- the task starts expanding into architecture redesign.

## 12. Capital / P0 boundary

Throughout this mission:

```text
P0 runtime = untouched
PRODUCT_INTEGRATION = PAUSED
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
```

Return control to Blue after the final handoff.
