# Quant Alpha Factory v1 — Design Plan

## Mission

Transform Quant-Trade from a single-thread research repository into a continuous discovery system that can generate, test, reject, validate, monitor, and retire strategies across multiple independent research lanes.

The terminal objective remains defined in `OBJECTIVE.md`.

The project must not rely on passive long exposure to secularly rising markets as its principal source of P&L. See `docs/MARKET_SELECTION_DOCTRINE.md`.

## Design principle

The product is not one strategy.

The product is a process that repeatedly converts market observations into validated economic decisions:

`market/data -> scanners -> candidate queue -> hypothesis -> preregistration -> experiment -> adversarial review -> portfolio decision -> live observation -> decay detection -> retirement / new research`

## Layer 1 — Data and provenance

Build a data inventory before adding more modelling complexity.

Every dataset must carry:

- source;
- instrument identity;
- timestamp semantics;
- timezone/session;
- point-in-time availability;
- revision policy;
- adjustment conventions;
- survivorship implications;
- license/access constraints;
- checksum/version where feasible.

The first objective is not maximum data volume. It is trustworthy data capable of supporting falsifiable experiments.

## Layer 2 — Research lanes

Initial lanes are inspired by the source article but adapted to the anti-beta doctrine.

### Lane A — Statistical / relative value

Candidate classes:

- pairs;
- baskets;
- residual mean reversion;
- futures basis/convergence;
- cross-venue dislocations.

Research emphasis:

- spread stationarity is not sufficient;
- trading costs, borrow, financing, latency, and structural breaks determine economic value.

### Lane B — Volatility / derivatives relative value

Candidate classes:

- implied-realized relationships;
- term structure;
- skew;
- relative surface dislocations;
- cross-sectional volatility relationships.

Research emphasis:

- distinguish structural volatility risk premia from true mispricing;
- include hedging costs, jumps, margin, and liquidity.

### Lane C — Cross-sectional factors / residuals

Candidate classes:

- factor residual ranking;
- sector-neutral anomalies;
- quality/value/momentum interactions;
- conditional factor dispersion;
- event-conditioned relative return.

Research emphasis:

- long/short or otherwise neutralized evidence;
- common-factor attribution;
- turnover and crowding.

### Lane D — Event / filing / insider information

Candidate classes:

- Form 4 / insider transactions;
- corporate filings;
- corporate actions;
- scheduled events;
- information timing anomalies.

Research emphasis:

- exact historical availability time;
- reporting delay;
- matched-control benchmark;
- realistic execution after publication.

### Lane E — Microstructure / venue-relative opportunities

This lane is later-stage because data and execution requirements are higher.

Candidate classes:

- lead-lag;
- venue fragmentation;
- short-lived spread dislocations;
- order-book imbalance conditional on liquidity state.

Research emphasis:

- fill probability;
- latency;
- adverse selection;
- queue position;
- fee tiers.

## Layer 3 — Scanner system

Scanners do not declare strategies profitable.

They only generate candidate observations with structured metadata.

Suggested candidate schema:

- `candidate_id`
- `timestamp`
- `lane`
- `instruments`
- `observation`
- `possible_mechanism`
- `expected_horizon`
- `required_data`
- `estimated_research_cost`
- `known_exposures`
- `source_refs`

Scanners should be cheap and broad. Expensive reasoning should occur after filtering.

## Layer 4 — Opportunity ranking

The system will eventually generate more hypotheses than can be tested.

Each candidate should be ranked by a qualitative or quantitative value-of-information score based on:

- probability an exploitable edge exists;
- potential economic value if true;
- probability of cheaply falsifying a major assumption;
- data availability;
- implementation cost;
- compute cost;
- time to result;
- false-positive / overfitting risk;
- expected strategy capacity / scalability where relevant.

The purpose is research capital allocation.

## Layer 5 — Hypothesis engine

A candidate becomes a hypothesis only when it states:

- the exact anomaly;
- plausible mechanism;
- observable information at decision time;
- tradeable expression;
- expected horizon;
- baseline;
- expected failure mode.

The system must prefer falsifiable hypotheses to vague pattern descriptions.

## Layer 6 — Experiment builder

Before final evaluation:

- define train/development data;
- define untouched evaluation data;
- freeze material parameters;
- freeze primary metric;
- freeze cost model;
- freeze benchmark;
- freeze decision rule;
- commit preregistration separately from result execution.

The experiment builder should eventually create machine-readable specifications so that execution is deterministic.

## Layer 7 — Researcher

Codex or another capable engineering/research model may implement the experiment.

Researcher responsibilities:

- minimal implementation;
- reproducibility;
- raw outputs;
- attempt accounting;
- honest result interpretation;
- no retroactive modification of preregistered criteria.

Researcher is allowed to fail.

## Layer 8 — Independent Judge

Judge operates in a fresh context where feasible.

Judge inspects:

- preregistration commit;
- code;
- data timing;
- raw output;
- ledger;
- execution assumptions;
- selection pressure;
- beta/factor attribution;
- costs;
- perturbation robustness.

Judge cannot optimize the strategy being judged.

Verdict:

- `REJECT`
- `NEEDS_MORE_EVIDENCE`
- `ACCEPT_FOR_NEXT_STAGE`

## Layer 9 — Strategy registry

Every strategy has a lifecycle state:

- `RESEARCH`
- `VALIDATION`
- `PAPER`
- `LIMITED_LIVE`
- `ACTIVE`
- `DECAY_WATCH`
- `RETIRED`

Minimum registry fields:

- strategy ID;
- originating hypothesis;
- research lane;
- discovery date;
- validation evidence;
- exposures;
- expected capacity;
- expected costs;
- live assumptions;
- promotion history;
- current state;
- retirement reason.

A dead strategy remains visible.

## Layer 10 — Portfolio layer

This comes only after more than one validated edge exists.

Portfolio allocation should consider:

- expected edge;
- correlation between strategies;
- factor/beta exposure overlap;
- liquidity/capacity;
- leverage/margin;
- tail interactions;
- live degradation;
- capital efficiency.

The portfolio layer must not turn individually neutral strategies into an accidental directional beta portfolio without explicit attribution.

## Layer 11 — Monitoring and alpha decay

A validated strategy is not permanently valid.

Monitor:

- realized vs expected return;
- realized vs expected costs;
- exposure drift;
- capacity/crowding indicators;
- regime dependence;
- signal frequency;
- execution slippage;
- distribution shift;
- drawdown relative to research expectations.

Monitoring should trigger evidence review, not automatic parameter tuning on live losses.

## Repository target structure

Proposed long-run structure:

```text
OBJECTIVE.md
AGENTS.md

docs/
    SOURCE_ANALYSIS_ROAN.md
    MARKET_SELECTION_DOCTRINE.md
    ALPHA_FACTORY_V1_PLAN.md

data/
    registry/

scanners/
    relative_value/
    volatility/
    cross_sectional/
    events/
    microstructure/

candidates/

hypotheses/

experiments/
    specs/
    outputs/

research/
    ledger.jsonl

evaluation/
    judge/

strategies/
    registry/
    research/
    validated/
    retired/

portfolio/

monitoring/
```

Do not create this entire tree pre-emptively. Add components only as the first vertical slice requires them.

## Build order

### Phase 0 — Consolidate research governance

- keep the existing alignment constitution;
- preserve P0-E1 as a killed historical experiment;
- enforce separate preregistration and execution commits;
- enforce beta attribution in evaluation.

### Phase 1 — Select one non-secular-beta lane

Choose the first lane by value of information and data availability.

The default shortlist is:

1. relative-value / pairs;
2. cross-sectional market-neutral factors;
3. event/filing signals;
4. volatility relative value if trustworthy options data is available.

Do not default to NASDAQ directional timing.

### Phase 2 — Build one complete vertical slice

Implement exactly one pipeline:

`data -> scanner -> candidate -> hypothesis -> preregistration -> researcher -> judge -> registry`

No live deployment is required at this stage.

### Phase 3 — Generalize

Only after the first vertical slice works:

- standardize candidate schemas;
- standardize experiment specs;
- add second/third research lanes;
- add automated opportunity ranking.

### Phase 4 — Continuous research loop

Automate scanning and candidate generation.

Research remains capacity-bounded and prioritized by value of information.

### Phase 5 — Paper / shadow observation

Candidates accepted by Judge move to live-data observation without assuming historical edge will persist.

### Phase 6 — Limited capital architecture

Only after independent evidence and paper/shadow validation should the project design bounded live-capital promotion and rollback logic.

## Success criteria for Alpha Factory v1

Alpha Factory v1 is successful when it can demonstrate the following process end-to-end on at least one non-beta-dependent research lane:

1. detect a candidate;
2. formalize a falsifiable hypothesis;
3. preregister before final evaluation;
4. execute reproducibly;
5. attribute returns and common exposures;
6. include realistic economics;
7. receive an independent verdict;
8. retain the result whether killed or advanced;
9. select the next experiment using what was learned.

It does **not** need to find a winning strategy on the first attempt.

It does need to make false alpha difficult to survive.
