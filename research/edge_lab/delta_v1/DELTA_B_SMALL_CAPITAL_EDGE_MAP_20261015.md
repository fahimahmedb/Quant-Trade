# DELTA B — Small-Capital Edge Map

Date: 2026-10-15
Status: DECISIONAL RESEARCH ONLY
Branch: `research/delta-research-pack-v1-20261015`
Base: `93534d9c365b52f2aa80c4277da1cac4e7338d31`

## Mandate boundary

This DELTA maps search spaces and baselines. It does not authorize a strategy, live trading, prospective collection or capital deployment.

## Decision question

Which market/mechanism spaces are structurally attractive or unattractive for a small research operation, and which strategy families should serve as baselines rather than discovery targets?

## Executive decision

Small capital is not an alpha source by itself. It changes the economics of what can be worth researching.

The most defensible comparative advantages are:

1. capacity-insensitive or low-dollar-capacity opportunities that large funds rationally ignore;
2. public-information niches whose research cost is high relative to absolute P&L capacity;
3. episodic institutional-flow, event and regulatory mechanisms where market impact from our own size is negligible;
4. operationally annoying opportunities that are too small to matter to multi-billion-dollar portfolios.

The weakest near-term spaces are:

- latency/HFT market making;
- generic microcap long-short anomaly mining dependent on expensive borrow;
- high-turnover stat-arb requiring institutional execution and data;
- strategies whose edge is smaller than realistic spread/borrow/impact uncertainty.

## Part 1 — Strategy-family evidence

The purpose of this section is baseline/prior/failure-library construction, not discovery-budget allocation.

| Strategy family | Long-run evidence | Main economic risk | Small-capital relevance | Decision |
|---|---|---|---|---|
| Trend following / time-series momentum | Broad historical evidence across futures/asset classes, with counter-literature on significance/implementation | crowdedness, whipsaw, leverage/roll costs, regime dependence | accessible through liquid instruments but not a unique small-cap edge | BASELINE |
| Cross-sectional momentum | Extensive evidence across markets | crashes, turnover, crowding, implementation | useful benchmark; not a primary novelty target | BASELINE |
| Value | Extensive but cyclical evidence | long droughts, definition sensitivity, structural change | benchmark / prior, not privileged discovery space | BASELINE |
| Quality / profitability | strong cross-sectional evidence | valuation overlap, crowding, slow horizon | benchmark / enhancement prior | BASELINE |
| Carry | broad multi-asset evidence | crash/liquidity/global-risk exposure | benchmark; leverage/funding important | BASELINE |
| Defensive / low-risk | substantial evidence but leverage/benchmark/friction debates | leverage constraints, valuation, crowding | benchmark only | BASELINE |
| Simple pairs / relative value | historical evidence, often implementation-sensitive | microstructure, shorting, decay | EXPLORE only when turnover/borrow modest | DEFER / EXPLORE |
| Merger arbitrage / event driven | durable historical premium in studies, nonlinear downside | deal breaks, concentration, financing, transaction costs | episodic low-capacity deals may be relevant | RETAIN SEARCH SPACE |
| Fundamental long/short | strong institutional track record but weak causal public evidence on process | data, short borrow, human intensity, factor overlap | use as comparison; not first autonomous engine | DEFER |
| Macro / cross-asset | long institutional history, heterogeneous | leverage, macro regime, instrument expertise | not structurally advantaged by small capital | DEFER |
| Volatility risk premium | well documented premium | severe tail risk, margin, option data/execution | useful baseline/failure library; not first target | DEFER |
| Crisis / long-vol | insurance-like negative carry with episodic payoff | timing/cost | control/failure library, not primary alpha target | DEFER |
| Market making / HFT | profitable for top specialized firms | latency arms race, queue/fill semantics, infra cost | structurally unattractive | REJECT NEAR-TERM |
| High-turnover statistical arbitrage | institutional evidence exists but private | data, latency, borrow, turnover | current scale poorly matched | DEFER |
| Cross-sectional ML | credible OOS academic gains | flexibility, multiple testing, turnover, stability | benchmark for later controlled research | DEFER AS FIRST TARGET |
| Alternative-data strategies | case-specific | acquisition/licensing, PIT, decay | only if free/cheap unique source appears | UNKNOWN / CASE-BY-CASE |

## Key empirical constraints

### Transaction costs and turnover

Transaction-cost research shows that low-turnover anomalies are much more likely to survive implementation than high-turnover anomalies. Therefore `gross alpha` is not an acceptable small-cap attractiveness metric.

### Borrow and microcaps

Recent evidence using actual securities-lending fees finds that many anomaly portfolios, especially microcap/short-leg-heavy portfolios, lose most or all of their apparent performance after borrow costs. This directly weakens the naive idea that “small stocks are ignored, therefore easy alpha.”

### HFT / market making

The documented arms race in electronic markets operates at microsecond-scale latency and is highly concentrated among sophisticated firms. Small capital reduces market impact but does not remove latency, queue-position, colocation or data disadvantages.

### Event / merger-arb type opportunities

Academic evidence finds a historical merger-arbitrage premium after transaction costs, but with nonlinear crash-like downside. The lesson is not “trade all deals”; it is that discrete event mechanisms can support economically real premia while remaining capacity-limited and operationally intensive.

## Part 2 — Large-manager advantages we cannot assume

`NOT_REPLICABLE_BY_DEFAULT`:

- prime-broker balance sheet and financing;
- institutional borrow inventories / locate quality;
- colocation / ultra-low-latency execution;
- proprietary exchange feeds and normalized historical order books;
- large alternative-data budgets;
- cross-venue execution infrastructure;
- large specialist teams;
- internal datasets accumulated over decades;
- broad OTC / derivatives access;
- large-scale capital allocation and netting.

These are not reasons to abandon research; they are filters against copying the surface form of Citadel/Renaissance/D. E. Shaw/Millennium strategies.

## Part 3 — Small-capital advantages

### RETAINED advantages

1. **Low market impact at tiny notional.** A trade too small to matter to an institution can still matter economically to a small book.
2. **Low capacity ceiling is acceptable.** A strategy capped at tens/hundreds of thousands may be irrelevant to a large fund and still useful here.
3. **Operationally annoying public-data niches can be rational.** Research overhead that cannot scale to billions may still be acceptable for a small book if automation reduces human cost.
4. **Narrow event sets are acceptable.** Low frequency is not disqualifying if evidence is handled as rare-event research rather than overfit backtesting.
5. **No need to deploy capital continuously.** `NO_OPPORTUNITY` can be economically rational.

### DISADVANTAGES

1. data subscriptions can be large relative to P&L capacity;
2. fixed commissions/spreads can dominate tiny gross signals;
3. borrow access and fees are worse than institutional prime-broker access;
4. financing/margin terms are worse;
5. some instruments/markets may be inaccessible;
6. retail/professional routing may lack queue/venue control;
7. limited capital makes absolute drawdown tolerance small even when percentage Sharpe looks attractive.

## Search-space decision matrix

### RETAINED_SEARCH_SPACES

```text
1. FORCED / PREDICTABLE INSTITUTIONAL FLOWS
2. EVENT / DOCUMENT / EARNINGS / GUIDANCE INFORMATION PROCESSING
3. REGULATORY / SETTLEMENT / MARKET-STRUCTURE CHANGES
4. CAPACITY-LIMITED EVENT-DRIVEN / RELATIVE-VALUE CASES
5. PUBLIC-DATA COMPLEXITY NICHES
```

### DEFERRED_SEARCH_SPACES

```text
FUNDAMENTAL_LONG_SHORT_AUTOMATION
GENERIC_CROSS_MARKET
VOLATILITY_RISK_PREMIUM_AS_PRIMARY_ENGINE
HIGH_TURNOVER_STAT_ARB
MICROSTRUCTURE_REQUIRING_FULL_ORDER_BOOK
GENERIC_CROSS_SECTIONAL_ML
ALTERNATIVE_DATA_WITH_NONTRIVIAL_LICENSE_COST
```

### REJECTED_SEARCH_SPACES — near-term only

```text
ULTRA_LOW_LATENCY_HFT
MARKET_MAKING_REQUIRING_COLOCATION_QUEUE_EDGE
GENERIC_MICROCAP_SHORT_ANOMALY_MINING_WITHOUT_BORROW_PROOF
```

### UNKNOWN_SEARCH_SPACES

Any niche where data rights, timestamp integrity, borrow or actual implementation economics are not yet known.

## BASELINE_STRATEGIES

Baselines are controls for what a simpler architecture can achieve, not preferred research budgets:

```text
BASELINE_1 = diversified trend / time-series momentum
BASELINE_2 = value + momentum + profitability/quality cross-sectional mix
BASELINE_3 = carry where instruments/costs are observable
BASELINE_4 = simple event-driven / merger-arb historical benchmark
BASELINE_5 = simple pairs/relative-value benchmark with realistic costs
```

## FAILURE_LIBRARY_CANDIDATES

```text
- published anomaly with strong post-publication decay
- high-turnover anomaly killed by transaction costs
- microcap/short-leg anomaly killed by borrow fees
- regime-sliced signal whose significance appears only after partition search
- order-book strategy where midpoint/quote-touch was mistaken for executable fill
- merger/event strategy with hidden short-put tail
- carry/short-vol strategy whose average return hides crash exposure
```

## Retained-space contracts

### Forced / predictable flows

`WHY_PREMIUM_MAY_EXIST`: constrained institutions trade for non-informational reasons; liquidity suppliers demand compensation.

`WHY_LARGE_CAPITAL_MAY_IGNORE`: capacity can be limited; implementing against the flow may be small relative to institutional AUM.

`DATA_REQUIREMENT`: official flow/rebalance/event information + timestamped price/execution proxy.

`EXECUTION_REQUIREMENT`: horizon-specific; can range daily to intraday, must be tested before economic look.

`CAPACITY`: usually LOW/MEDIUM, mechanism-specific.

`MAIN_FAILURE_MODE`: flow proxy known only after market move; crowding; wrong instrument/horizon; execution eats effect.

### Event / Document

`WHY_PREMIUM_MAY_EXIST`: costly interpretation, heterogeneous disclosures, limited attention, cross-document synthesis.

`WHY_LARGE_CAPITAL_MAY_IGNORE`: not necessarily ignored; advantage may exist only in small/niche universes or low-capacity cases. Competition is high on major earnings.

`DATA_REQUIREMENT`: official timestamped filings/transcripts/releases; PIT consensus/context where claimed.

`EXECUTION_REQUIREMENT`: event-specific latency and spread realism.

`CAPACITY`: HIGH for large-cap earnings if edge exists, LOW for niche documents/small issuers.

`MAIN_FAILURE_MODE`: information already priced, timestamp leakage, survivorship/universe bias, narrative rationalization after price move.

### Regulatory / settlement / market-structure

`WHY_PREMIUM_MAY_EXIST`: mandates and mechanical constraints change holdings, funding or settlement behavior.

`WHY_LARGE_CAPITAL_MAY_IGNORE`: some cases have small absolute capacity or operational overhead.

`DATA_REQUIREMENT`: authoritative rule/event timing + affected universe + tradable instrument mapping.

`EXECUTION_REQUIREMENT`: depends on implementation window.

`CAPACITY`: case-specific.

`MAIN_FAILURE_MODE`: mechanism anticipated/prepriced; legal interpretation error; implementation impossible.

## Trajectory implication

DELTA B does not select an architecture. It supports designing Quant-Trade around **small-capacity comparative advantage**, not copying institution-scale execution businesses.

## Governance compatibility

```text
OD01_OD12 = PASS
STRUCTURAL_PRE_OP = PASS
EXISTING_INVARIANTS = PASS
```

No result authorizes real capital, strategy validation or trading.

## Key evidence used

- Moskowitz, Ooi & Pedersen, *Time Series Momentum*, JFE.
- Asness, Moskowitz & Pedersen, *Value and Momentum Everywhere*, JF.
- Koijen, Moskowitz, Pedersen & Vrugt, *Carry*, JFE.
- Novy-Marx & Velikov, transaction-cost/anomaly implementation research.
- Securities-lending evidence on short borrow costs and cross-sectional anomalies, 2025.
- Budish, Cramton & Shim, *The High-Frequency Trading Arms Race*.
- Mitchell & Pulvino, *Characteristics of Risk and Return in Risk Arbitrage*.
- Coval & Stafford, *Asset Fire Sales (and Purchases) in Equity Markets*.
