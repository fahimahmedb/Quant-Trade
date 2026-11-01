# Quant North Star

This document is the highest-level product and architecture specification for Quant.

If a lower-level document, implementation detail, agent prompt, local optimization, or historical branch conflicts with this document, **this document wins unless it is explicitly revised**.

## 1. Terminal objective

Quant exists to increase real capital through repeatable discovery, selection, sizing, execution and replacement of genuine market edge.

The terminal objective is **net economic gain / long-run real wealth growth after real frictions**.

Risk, drawdown, leverage, Sharpe, hit rate, activity, number of trades, number of experiments, model complexity, code elegance and number of agents are instrumental variables or diagnostics. They are not terminal objectives.

A compact abstraction is:

`W(t+1) = W(t) + gross_pnl - fees - spread - slippage - financing - borrow - execution_losses`

The system should prefer the action that improves expected future wealth conditional on current evidence, including `NO_TRADE` when that is economically superior.

## 2. Quant is a system, not a research script

Quant must never be reduced to:

- a backtester;
- a strategy notebook;
- a market scanner;
- an LLM wrapper;
- a research queue;
- a collection of strategies;
- a dashboard with no underlying state.

The target is a **persistent autonomous quantitative system** composed of several interacting planes.

## 3. Target system

```text
                           HUMAN / CONTROL SURFACE
                                    |
                                    v
                           ROOT / CONTROL PLANE
                       clock · scheduler · routing
                                    |
        +---------------------------+---------------------------+
        |                           |                           |
        v                           v                           v
    DATA PLANE               RESEARCH FACTORY              BUILD PLANE
  ingest · validate          observe · discover         Codex / engineering
 point-in-time state          test · falsify               improve Quant
        |                           |
        +-------------+-------------+
                      |
                      v
                 OPPORTUNITIES
                      |
                      v
          SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK
                                              |
                                              v
                                      REAL / SHADOW FEEDBACK
                                              |
                          pnl · fills · rejects · decay · errors
                                              |
                                              +------> LEARNING / MEMORY
                                                           |
                                                           +------> SEARCH
```

The current implementation may begin in paper/shadow mode, but the topology should match the intended final system rather than inventing a temporary architecture that later has to be discarded.

## 4. Core planes

### Control Plane / Clock

Owns system lifetime, scheduling, event routing, liveness, state transitions, resource budgets, recovery and observability.

`IDLE` means alive with no useful work now. It does not mean finished.

### Data Plane

Owns acquisition, point-in-time semantics, validation, normalization, lineage, versioning and dataset availability.

No research or capital decision may silently assume data that the system cannot trace.

### Research Factory

Continuously searches for edge and replacement strategies as alpha decays.

Canonical pattern:

`OBSERVE -> SCAN -> FILTER -> HYPOTHESIZE -> TEST -> FALSIFY/VALIDATE -> REGISTER -> LEARN -> CONTINUE`

Research failure is normal and should usually be absorbed internally.

### Capital Desk

Transforms validated opportunity evidence into capital decisions.

Canonical functional chain:

`SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK`

These are logical functions, not a requirement for six separate LLMs.

- `SCAN`: surfaces actionable opportunity candidates from research/market state.
- `VET`: decides whether the opportunity itself deserves consideration now.
- `SIZE`: maps edge, uncertainty, liquidity, capacity and capital state into exposure.
- `RISK`: evaluates the opportunity in portfolio context, including correlation and concentration.
- `FILLS`: models/records execution quality and expected-versus-realized implementation loss.
- `BOOK`: authoritative ledger for bankroll, positions, cash, exposure and P&L.

### Persistent Book

The same bankroll carries forward through time.

There is no fresh seed per experiment, day, Codex run or process restart.

Conceptually:

`S_t = (wealth, cash, positions, exposures, history, active_strategies, market_state)`

Future decisions depend on this state.

### Learning / Memory

Quant learns from:

- profitable and losing trades;
- accepted and rejected opportunities;
- false accepts and false rejects;
- failed hypotheses;
- execution shortfall;
- strategy decay;
- data failures;
- scanner/router quality;
- missed opportunity cost.

The durable asset is the system's improving ability to find and monetize edge, not one permanent strategy.

### Build Plane

Codex is primarily a **Builder / Quant Engineer**, not the runtime itself.

Codex can create or improve scanners, tests, data adapters, execution models, UI and infrastructure. When the Codex task ends, Quant's persistent state and runtime should remain coherent and resumable.

## 5. Two-speed intelligence

The source architecture's most important compute principle is preserved:

`wide / cheap -> narrow / deep`

Broad deterministic or inexpensive monitoring should process many observations. Expensive reasoning should be concentrated on filtered candidates with high information value.

Do not spend frontier-model reasoning uniformly across all markets or observations.

## 6. Autonomy

Within configured boundaries, Quant should be able to choose:

- where to search;
- which markets/instruments/data deserve attention;
- which hypotheses to test;
- which strategies to revise or retire;
- which candidates to reject;
- what to research next;
- whether to stay idle;
- how much shadow/paper capital an opportunity deserves.

The human should not be required to invent the next strategy after every ordinary failure.

## 7. Alpha discipline

Profit is not automatically alpha.

Quant must distinguish genuine edge from:

- passive beta;
- factor exposure;
- look-ahead or leakage;
- survivorship bias;
- multiple-testing luck;
- unrealistic fills/costs;
- stale information;
- concentration in a few observations.

Directional exposure is allowed when economically justified, but secular drift must not be relabeled as discovered autonomous skill.

## 8. Source hierarchy

Primary architectural references:

1. the project owner's supplied source PDF/article;
2. the supplied project screenshots;
3. this North Star, which translates those references into the Quant target system.

The source PDF directly supports continuous strategy discovery, wide/cheap monitoring before deeper reasoning, specialized functional roles, alpha decay/replacement and deployment/risk functions.

The screenshots contribute system-level ideas including persistent runtime, `SCAN/VET/SIZE/RISK/FILLS/BOOK`, visible RUN/IDLE state, ticket/activity traceability, uptime and bankroll continuity.

**Financial performance, vendor claims, costs, model capability claims and screenshot profits are unverified and are not treated as empirical evidence.**

## 9. Product test

A useful test of architectural progress is whether a live status surface could truthfully display real system state such as:

```text
BANK / NAV
P&L
UPTIME
POSITIONS / SHADOW POSITIONS
ACTIVE STRATEGIES
TICKETS ACCEPTED / REJECTED / BLOCKED

SCAN    RUN|IDLE|BLOCKED
VET     RUN|IDLE|BLOCKED
SIZE    RUN|IDLE|BLOCKED
RISK    RUN|IDLE|BLOCKED
FILLS   RUN|IDLE|BLOCKED
BOOK    RUN|IDLE|BLOCKED

RESEARCH: scanning / testing / validated / rejected / decayed
DATA: healthy / stale / blocked
BUILD: idle / task running
SYSTEM: heartbeat / faults / next event
```

The UI is not the product, but it is an architectural checksum: every displayed value must come from real persistent system state.

## 10. Decision rule for future work

Before any major recommendation or implementation, ask:

> Does this move Quant closer to a persistent autonomous system that can discover, select and monetize real edge while preserving state and learning from outcomes?

If a local optimization improves a subcomponent but moves the overall system away from that target, prefer the global target.
