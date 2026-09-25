# BLUE — POST-P0 VERTICAL SHADOW LOOP PRESTAGE PLAN — 2026-09-21

## 0. Status

`VERTICAL_SHADOW_PRESTAGE = PREPARED / PRODUCT_INTEGRATION_STILL_PAUSED`

This plan prepares the first economic Product phase while P0 finishes.

It does NOT authorize:
- Product merge into the qualifying runtime;
- target-host mutation;
- live capital;
- economic claims;
- unblinding or reinterpretation of locked scientific outcomes.

Its purpose is to prevent idle calendar time and to ensure P0 exit leads
immediately into an end-to-end economic loop rather than another horizontal
infrastructure program.

## 1. North Star target

The first post-P0 Product milestone is NOT:
- a perfect scanner;
- a perfect research framework;
- a perfect backtester;
- a dashboard;
- more agents.

It is:

`FIRST_END_TO_END_ECONOMIC_SHADOW_LOOP`

One opportunity must be able to travel through:

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

Final output may legitimately be:
`NO_TRADE`.

## 2. Canonical starting leaves

Canonical Forward:
`parallel/claude-forward-data-2026-09-20@83521dbfdd90027c90d04adfb7d814593c2355c5`

Canonical Economic:
`parallel/claude-economic-v2-2026-09-20@35dff27b8fac53618da434ee6d31febbddcc0e69`

Existing reusable surfaces include:

Forward/Data:
- `src/quant/dataplane/forward_capture.py`
- `src/quant/dataplane/forward_recorder.py`
- `src/quant/dataplane/forward_admissibility.py`
- `src/quant/dataplane/forward_coverage.py`

Research:
- `src/autonomous_research/scanner.py`
- `src/autonomous_research/orchestrator.py`
- `src/autonomous_research/backtest.py`
- `src/autonomous_research/runtime.py`
- `src/autonomous_research/memory.py`
- `research/opportunity_map.json`
- `research/memory.jsonl`

Economic:
- `src/quant/economics/frictions.py`
- `src/quant/economics/capacity.py`
- `src/quant/economics/sizing.py`
- `src/quant/economics/decision.py`
- `src/quant/economics/timeline.py`
- `src/quant/economics/value.py`

Book:
- `src/quant/book/ledger.py`
- `schemas/book_state.schema.json`

## 3. Prestaging objective

Before P0 exit, prepare enough evidence that Blue can choose the smallest
safe integration path immediately after P0 closes.

The prestage should answer:

1. What is the canonical interface between Forward data and Research?
2. What exact Research output becomes a VET input?
3. What exact fields are required for economic assessment?
4. Where are frictions/costs/capacity applied?
5. What object carries sizing/risk decisions?
6. What is the shadow-fill interface?
7. How does the Book persist cash/positions/PnL/provenance?
8. What learning record is emitted from:
   - acceptance;
   - rejection;
   - fill;
   - miss;
   - slippage;
   - decay;
   - retirement?
9. Which existing components already satisfy each interface?
10. What is the minimum missing glue?

## 4. First vertical slice

Use ONE lane only.

Do not start multi-lane orchestration first.

The first vertical slice should prove:

```text
one source observation
-> one research ticket
-> one explicit hypothesis/claim
-> one VET disposition
-> one economic decision
-> one SIZE/RISK output
-> one shadow fill or NO_TRADE
-> one Book transition
-> one durable learning record
```

This is a Product integration proof, not an edge-profitability proof.

## 5. Acceptance criteria for the first loop

The first loop is functionally complete only if all are true:

- exact data provenance survives through the decision;
- public/PIT timing is not lost;
- research claim is explicit and reproducible;
- VET can reject without pressure to trade;
- economic assessment includes real modeled frictions;
- sizing may produce zero;
- risk may veto;
- fills are shadow/simulated and use an explicit execution model;
- Book state survives restart;
- the decision and its reasons are durable;
- outcome feedback can update Learning/Memory;
- the loop can be rerun without owner manually stitching files together.

## 6. What NOT to build first

Defer until demanded by a concrete economic bottleneck:

- many-agent orchestration;
- generalized strategy DSL;
- broad UI redesign;
- every exchange/broker adapter;
- multi-asset universal execution;
- generalized portfolio optimizer;
- high-frequency infrastructure;
- elaborate notification UX;
- broad architecture rewrites.

A component is pulled forward only if the first vertical loop cannot produce
reliable economic learning without it.

## 7. Work allowed during Gate C

When the qualifying P0 runtime is in Gate C:

Allowed on separate non-runtime branches:
- read-only branch comparison;
- interface mapping;
- semantic diff of canonical Forward/Economic leaves;
- integration design;
- unit/integration fixtures using synthetic or historical inputs;
- preparation of a post-P0 Builder mission;
- preparation of an end-to-end shadow-loop acceptance test.

Forbidden:
- merge into the qualifying P0 release;
- deploy Product changes to the qualifying host runtime;
- modify P0 fingerprint/service/config/state;
- alter source-calendar expectations;
- let Product work become part of Gate-C evidence.

## 8. Immediate post-P0 execution order

After `P0 EXIT`:

1. unpause Product integration explicitly;
2. qualify canonical Forward leaf against exact-head CI;
3. qualify canonical Economic leaf against exact-head CI;
4. reconcile their semantic deltas;
5. select one integration baseline;
6. implement only missing glue for the first vertical slice;
7. run whole-loop shadow E2E;
8. independently review economic/provenance failure modes;
9. start repeated shadow runs;
10. let observed bottlenecks determine next implementation.

## 9. Economic decision discipline

Every mission after P0 must answer:

`WHAT ECONOMIC UNCERTAINTY DOES THIS CLOSE?`

Valid examples:
- does the signal survive forward timing?
- is it capturable after spread/slippage/fees?
- does capacity make the trade irrelevant?
- should size be zero?
- why was an opportunity rejected?
- did shadow fills match the execution model?
- is the edge decaying?
- which lane should replace it?

Insufficient justification:
`THE ARCHITECTURE WOULD BE CLEANER`.

## 10. Product exit state from first vertical loop

Desired first visible Product milestone:

```text
VERTICAL_SHADOW_LOOP = FUNCTIONAL
REAL_CAPITAL_AUTHORIZED = FALSE
BOOK_PERSISTS = TRUE
LEARNING_FEEDBACK_PERSISTS = TRUE
TRADE_OR_NO_TRADE_DECISION = REPRODUCIBLE
```

Only after repeated economically meaningful shadow evidence should Blue
consider Capital Readiness.

## 11. Capital boundary

This prestage creates no capital authority.

Progression remains:

```text
scientific evidence
-> capturability/cost/capacity
-> forward shadow
-> capital readiness
-> explicit owner authorization
-> tiny real capital
-> scaling
-> monitoring
-> decay
-> retirement/replacement
```

At every stage:
`REAL_CAPITAL_AUTHORIZED = FALSE`
until explicitly superseded by owner-authorized governance.
