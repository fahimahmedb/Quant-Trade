# Source Basis

This rebuild is grounded in two kinds of source material supplied by the project owner.

## A. Continuous-strategy-discovery article

The source article's central thesis is that the durable advantage is not one permanent strategy but a pipeline that continuously discovers new strategies as old alpha decays.

It describes four initial categories of market mispricing:

1. statistical arbitrage;
2. volatility-surface mispricings;
3. factor-decomposition anomalies;
4. insider-signal detection.

It also describes a two-layer compute model:

- a broad, cheaper monitoring layer that scans many markets and filters candidates;
- a more capable reasoning layer that receives filtered candidates and performs deeper strategy reasoning.

Its named functional roles include:

- Chief of Staff / coordinator;
- Scanner;
- Hypothesis;
- Backtest;
- Validation;
- Deployment;
- Risk;
- Notification.

The article also illustrates monitoring inputs such as equity order books, crypto perpetual markets, prediction markets, options flow, SEC Form 4 filings, public information feeds and macro calendars.

## B. Trading-system screenshots supplied later

The screenshots are not treated as verified performance evidence.

The architectural ideas visible in them are nevertheless useful:

- a large number of candidate signals can be rejected;
- inactivity can be a deliberate decision rather than a system failure;
- the visible workflow separates `SCAN`, `VET`, `SIZE`, `RISK`, `FILLS`, and `BOOK`;
- the displayed account state appears persistent rather than reset for each decision;
- an activity log / ticket concept suggests stateful traceability across decisions.

The repository extracts those ideas without assuming the displayed profits, win rates, account history or model identity are genuine or reproducible.

## What is source-derived versus project inference

### Directly source-derived

- continuous strategy discovery;
- alpha decay / strategy replacement;
- four initial research categories;
- cheap broad scanning before expensive deep reasoning;
- specialized logical roles;
- many candidates can be filtered before deeper work.

### Project inference / adaptation

- treating roles as logical functions rather than requiring one model per role;
- using one persistent ticket object across research stages;
- measuring rejection quality, not only accepted candidates;
- using the historical research log to improve future search allocation;
- separating the autonomous research engine from any future real-capital integration;
- treating old NASDAQ work as historical research rather than the project definition.

## Important limitation

Vendor capabilities, pricing claims, profit screenshots and comparisons with institutional firms in the source material are not assumed true merely because they appear in the source.

Quant-Trade should preserve the useful architecture while validating factual and empirical claims independently when those claims matter to implementation decisions.
