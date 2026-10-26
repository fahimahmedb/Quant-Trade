# Market Selection Doctrine

## Objective

Quant-Trade must discover **alpha**, not merely own positive long-run beta.

The project therefore avoids making broad secularly rising assets or indices the primary substrate of research when a passive buy-and-hold position can dominate the interpretation of success.

This does not assert that any asset is guaranteed to rise. It is a research-design rule: do not let persistent directional drift masquerade as strategy skill.

## Forbidden shortcut: beta laundering

A profitable backtest is not accepted as evidence of alpha when its P&L is substantially explained by unconditional long exposure to a broad risk asset.

Examples of weak evidence:

- long-only NASDAQ timing that is invested most of the time;
- equity strategies whose returns disappear after market-beta neutralization;
- a strategy that mainly earns the equity risk premium but is described as predictive;
- comparing a low-exposure tactical strategy only to cash while ignoring passive market exposure;
- calling volatility reduction an edge when wealth growth is inferior and the P&L source is still market drift.

## Preferred research substrates

Prioritize environments where economic value can be attributed to a specific relative or conditional edge rather than passive secular appreciation.

### 1. Relative value / statistical arbitrage

Examples:

- pairs and baskets;
- cointegration / residual spreads;
- cross-venue price dislocations;
- basis and convergence trades;
- relative value across related contracts.

Primary question: does the spread or residual produce net P&L after realistic financing, borrow, fees, latency, and execution?

### 2. Cross-sectional long/short

Examples:

- factor residuals;
- ranking anomalies;
- event-conditioned relative performance;
- sector-neutral or beta-neutral stock selection.

Primary question: does the ranking contain information after neutralizing common market and sector exposures?

### 3. Volatility / derivatives relative value

Examples:

- implied vs subsequently realized volatility;
- term-structure dislocations;
- skew / surface relative value;
- cross-asset or cross-expiry volatility relationships.

Primary question: is compensation left after transaction costs, hedging error, jump risk, financing, margin, and known risk premia?

### 4. Event-driven / information signals

Examples:

- filings;
- insider transactions;
- corporate actions;
- scheduled or unscheduled information events.

Primary question: does information available at time t predict a tradeable relative return after delay and implementation costs?

### 5. Microstructure / execution edges

Examples:

- temporary order-book imbalances;
- cross-market lead-lag;
- venue fragmentation;
- short-lived liquidity dislocations.

Primary question: does the edge survive latency, queue position, fees, adverse selection, and realistic fill probability?

### 6. Markets without a simple passive drift benchmark

Research may include futures, FX, rates, commodities, prediction markets, or crypto relative-value structures where a permanent long-only benchmark is not the obvious source of returns.

The instrument choice itself is never evidence of edge.

## Exposure constraints for research claims

A strategy may have directional exposure when the exposure is an explicit consequence of a predictive hypothesis, but the evidence must separate alpha from passive beta.

Where applicable, report:

- average net exposure;
- gross exposure;
- market beta;
- sector/factor exposures;
- alpha after common-factor regression;
- P&L from hedged / neutralized form;
- P&L from passive beta component;
- financing and borrow costs.

If most of the economic result vanishes after removing broad beta, classify the candidate as beta-dependent rather than discovered alpha.

## Benchmark doctrine

Benchmarks must match the hypothesis.

Examples:

- pair trade -> no-trade / spread baseline, not broad-index buy-and-hold;
- cross-sectional long/short -> beta/sector-neutral baseline;
- options relative value -> matched hedge / volatility-risk-premium baseline;
- event signal -> matched control portfolio with identical broad exposures;
- execution edge -> arrival-price / implementation-shortfall benchmark.

A benchmark should answer: **what would capital have earned without the claimed informational edge but with comparable unavoidable exposures?**

## Market admission test

Before a new research lane receives substantial engineering effort, answer:

1. What is the hypothesized mispricing or conditional edge?
2. Why should it persist long enough to monetize?
3. Can the P&L be separated from passive directional drift?
4. Is there a realistic tradeable expression?
5. Are the required data available point-in-time?
6. What costs, financing, borrow, margin, or execution constraints matter?
7. What simple benchmark would falsify the claim?
8. Can a cheap experiment reject the idea before major infrastructure is built?

If question 3 cannot be answered convincingly, the market/research design is low priority for Quant-Trade.

## Consequence for existing NASDAQ work

The current NASDAQ Composite research is retained as historical evidence and methodology work.

It should not be the primary destination of the Alpha Factory merely because the repository already contains NASDAQ data.

Future research should prioritize strategies whose return source can be distinguished from the secular equity risk premium.
