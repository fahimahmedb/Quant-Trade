# L0 Research Seed — Market Sentiment Dislocation

Status: IDEA_GENERATED only. This is a causal research seed under `EDGE_DISCOVERY_METHOD.md`; it is not a trading signal and it does not authorize an economic look by itself.

## Question

Can public, timestamped measures of market sentiment or positioning identify repeatable underreaction, overreaction, crowding, or reversal mechanisms that are not merely contemporaneous descriptions of price moves?

## L0 fields

- `MECHANISM`: sentiment/positioning shocks may propagate nonlinearly because some participants chase, de-risk, rebalance, or fade extreme consensus at different speeds.
- `WHO_PAYS`: late trend followers, crowded discretionary positioning, forced hedgers/deleveragers, or investors reacting after confirmation.
- `WHY_PERSIST`: heterogeneous mandates and horizons, mechanical risk limits, slow fund-flow transmission, sticky positioning, and attention constraints.
- `CHEAP_DATA_NOW`: public or freely accessible timestamped sentiment/positioning proxies such as official/industry surveys, options-based public measures where reproducible, public fund-flow/positioning summaries, fear/volatility gauges, and timestamped news/social aggregates only when provenance and history are auditable.
- `CHEAP_EXPRESSION`: candidate relative or directional expressions tied to a clearly pre-specified sentiment mechanism. No expression is selected by looking at future returns.
- `FATAL_PROBLEM`: many sentiment indicators are derived from price itself, revised, paywalled historically, timestamp-ambiguous, or only predictive after arbitrary thresholds/windows. If the signal cannot be separated from contemporaneous price and made point-in-time reproducible, kill or park it.

## Required L0 discipline

1. Separate genuinely exogenous/independent sentiment information from price-derived indicators.
2. Require reproducible publication timestamps and historical availability semantics.
3. Prefer signals with a plausible `WHO_PAYS` mechanism over generic “fear is high” narratives.
4. Search for disconfirming regimes where sentiment extremes did not mean-revert or where continuation dominated.
5. Do not inspect signal-to-future-return/PnL outcomes during L0.
6. Do not tune thresholds, lookbacks, asset universes, aggregation weights, or horizons after reading outcomes.
7. Respect the global one-economic-look invariant and every already-frozen prospective.

## Candidate causal channels to triage

- positioning/crowding → unwind or continuation under forced flows;
- options skew / volatility demand → insurance pressure or dealer-hedging transmission;
- survey sentiment → delayed allocation/rebalancing behavior;
- fund-flow / ETF-flow sentiment → mechanical follow-through or exhaustion;
- news-attention shock → underreaction or short-lived overreaction;
- social sentiment → only where historical timestamps, bot/noise controls and survivorship are tractable.

## Cheap next test

Choose one public sentiment family with point-in-time timestamps and minimal revision risk. Document the causal mechanism, whether the indicator adds information beyond contemporaneous price/volatility, one cheap expression, and main confounds. Produce only an L0 verdict: `L1_NOW`, `PARK_DATA`, `PARK_ECONOMICS`, or `DUPLICATE`.

## Guardrails

- No real capital.
- No live trading.
- No paid data/services.
- No outcome browsing to select the most attractive sentiment proxy.
- No generic technical-indicator search disguised as sentiment research.


## L0 disposition — 2026-10-14

Consumed once as `market-sentiment-cftc-cad-positioning`; verdict `PARK_DATA`, exposure `DATA_FEASIBILITY`, no economic look. [Primary evidence and next source question](../discovery/qualifications/market-sentiment-cot-clock-l0-2026-10-14.json). COT position date is Tuesday; normal publication Friday 15:30 Eastern. Exact TFF/CAD classification, as-published history and usable daily FX semantics remain unqualified. No directional conclusion. Do not consume this narrative again under another name; only the explicitly recorded new primary-source gaps may be resolved. France and Trump seeds were inspected but not consumed.
