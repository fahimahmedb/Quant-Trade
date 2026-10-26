# Source Basis

This project is grounded in source material supplied by the project owner. The sources are architectural inspiration and design constraints; their financial results, vendor claims and performance figures are not treated as verified evidence.

Read `QUANT_NORTH_STAR.md` for the project translation of these sources.

## A. Continuous-strategy-discovery article

The source article's central thesis is that the durable advantage is not one permanent strategy but a pipeline that continuously discovers/replaces strategies as alpha decays.

It describes four initial categories of market mispricing:

1. statistical arbitrage;
2. volatility-surface mispricings;
3. factor-decomposition anomalies;
4. insider-signal detection.

It also describes a two-layer compute model:

- broad, cheaper monitoring/scanning that processes many observations and filters candidates;
- deeper, more capable reasoning that receives filtered candidates and performs strategy reasoning/testing.

Its named functional roles include:

- Chief of Staff / coordinator;
- Scanner;
- Hypothesis;
- Backtest;
- Validation;
- Deployment;
- Risk;
- Notification.

The article also illustrates monitoring inputs spanning multiple venues/information sources such as equities, crypto perpetual markets, prediction markets, options activity, SEC filings, public information feeds and macro calendars.

### Direct architectural lessons retained

- continuous strategy discovery;
- alpha decay and strategy replacement;
- broad/cheap monitoring before narrow/deep reasoning;
- specialized logical functions;
- persistent scheduling/monitoring as a system capability;
- research that can progress from hypothesis through validation into downstream deployment/evaluation functions.

## B. Project screenshots

The screenshots are not treated as verified performance evidence.

Their architectural ideas are nevertheless primary references for the target product:

- many candidate signals can be rejected;
- inactivity can be deliberate rather than a system failure;
- visible functional separation of `SCAN`, `VET`, `SIZE`, `RISK`, `FILLS` and `BOOK`;
- `RUN` / `IDLE` style component state;
- persistent account/bankroll state rather than a fresh seed for each decision;
- ticket/activity traceability;
- uptime and system-status presentation;
- a distinction between build-time work and functions that keep running after the builder leaves.

These screenshots are therefore used as **system topology and observability references**, not as evidence that their displayed profits, win rates or model identities are genuine or reproducible.

## C. Project adaptation

The project adapts the sources in several ways:

- roles are logical functions; one separate LLM per role is not required;
- deterministic code should handle broad/cheap work where possible;
- expensive reasoning is invoked selectively;
- Research Factory, Control Plane, Data Plane, Capital Desk, persistent Book, Learning and Build Plane are explicit subsystems of one coherent system;
- the first implementation may use paper/shadow state while preserving the topology of the complete target system;
- old NASDAQ work is historical research, not the definition of Quant.

## What is not assumed

Do not assume as factual merely because the source claims it:

- vendor/model capability claims;
- exact model context lengths or agent counts;
- provider pricing/economics;
- institutional-equivalence claims;
- screenshot profit/P&L claims;
- reported strategy performance without independent reproduction.

The useful source contribution is the architecture and operating pattern. Empirical and commercial claims must be validated separately when they matter.
