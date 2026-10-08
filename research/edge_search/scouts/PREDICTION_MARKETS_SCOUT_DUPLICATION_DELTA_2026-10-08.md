# AGENT 2 — PREDICTION MARKETS DUPLICATION DELTA

DATE = 2026-10-08
BASE_SCOUT_COMMIT = ad9c518af4f1f41d3cf282ffdc8c98dc43945892
F2_EVIDENCE_SNAPSHOT = 25b95cdad27e4f1dfb00fdc4cfb670d6a25bd46b
OUTCOME_CONFIRMATION_READ = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE

## Candidate 1 relation to F2

CANDIDATE_1_RELATION = SAME_FAMILY_NEW_EXPRESSION

EVIDENCE =
- MECHANISM: same causal family. Scout Candidate 1 is favourite–longshot bias: longshots are overpriced because of probability weighting/noisy demand and correction is limited by fees/collateral. F2 `KALSHI-FLB-OOS-001` states the same mechanism: takers overweight small probabilities; buying the high-probability complementary side should earn positive net return.
- UNIVERSE: materially the same. Both target Kalshi binary contracts; F2 fixes a post-publication historical Kalshi window and a primary non-Sports universe. The scout's proposed cross-category extension changes breadth, not mechanism.
- SIGNAL TIMING: overlapping. Scout explicitly proposed fixed pre-resolution horizons including T-24h; F2 fixes the signal at T-24h using one hourly bid/ask candle in (T-25h,T-24h].
- EXPRESSION: materially the same economic trade. Scout proposes buying the complementary/favourite side of overpriced longshots. F2 buys YES or NO when its executable ask is >=0.80 and holds to settlement.
- DATA: same core source class. Both rely on Kalshi historical market metadata, bid/ask/candlestick data, event/series metadata, fees and settlement join. F2 already has a blinded acquisition harness and joins `result` only at the analysis stage.
- TEST: different statistical expression, not a new causal family. Scout proposed calibration bins/cross-category monotonicity plus complementary-side net returns; F2 preregisters an executable favourite-side return gate at >=0.80, T-24h, with category/price-bucket sensitivities and mirror-longshot reporting. The scout would therefore extend/reshape F2 rather than test a causally distinct edge.

DECISION = Candidate 1 is retrograded. Do not open a separate family, do not reserve another Kalshi FLB confirmation window, and do not consume F2 outcomes for this delta.

## Updated top candidate — Polymarket structural negative-risk parity

UPDATED_TOP_CANDIDATE = Cross-outcome structural pricing inconsistency in standard Polymarket negative-risk events.

WHY = This is causally distinct from FLB. It does not require systematic probability miscalibration or settlement outcomes. The edge hypothesis is a transient violation of an algebraic cross-market identity caused by asynchronous books, fragmented liquidity and stale quotes. In a standard negative-risk event, only one outcome can win and one NO token can be atomically converted into one YES token for every other outcome; therefore executable quotes across the linked books must satisfy conversion parity after depth and fees.

PUBLIC_DATA_CONFIRMED = TRUE_BY_CURRENT_OFFICIAL_DOCUMENTATION

READ_ONLY_DATA_EVIDENCE =
- Polymarket market discovery data is public and documented as requiring no authentication: https://docs.polymarket.com/market-data/discover-markets
- Event objects expose their component markets; market objects expose condition IDs and YES/NO CLOB token IDs (`clobTokenIds`).
- Market status exposes `negRisk`; event metadata exposes `enableNegRisk` and `negRiskAugmented`, allowing standard negative-risk events to be selected while excluding augmented/placeholder semantics: https://docs.polymarket.com/market-data/market-details
- Official negative-risk mechanics state that a NO share in one market converts atomically into one YES share in every other market. Standard negative risk requires the complete outcome set to be known at creation; augmented negative risk can contain placeholders and a changing `Other`, so augmented events are excluded: https://docs.polymarket.com/concepts/negative-risk
- Public CLOB order-book reads expose bids, asks, sizes, timestamp, tick size, minimum order size, `negRisk` and a book hash. Batch order-book reads support up to 500 token IDs in one request, materially reducing cross-leg snapshot skew: https://docs.polymarket.com/market-data/prices-order-books
- Market details expose the active fee configuration; current fee documentation specifies taker fees and their price-dependent formula: https://docs.polymarket.com/trading/fees
- No settlement result, resolved outcome, sealed-confirmation observation, order placement or conversion was read/executed for this delta.

## Minimum discriminating test

MINIMUM_DISCRIMINATING_TEST = READ_ONLY_NEG_RISK_CONVERSION_PARITY_SCAN

1. METADATA-ONLY SELECTION: list active events and retain only standard negative-risk groups: every component market has `negRisk=true`, event `enableNegRisk=true`, `negRiskAugmented!=true`, all component markets are active/accepting orders, and all YES/NO token IDs plus fee/min-size fields are present. Exclude augmented negative-risk, placeholders and mutable `Other`. Selection is independent of prices and outcomes.
2. DETERMINISTIC SMALL UNIVERSE: sort eligible event IDs ascending and take the first events whose full token set fits one 500-token batch request, capped at 10 events. No cherry-picking by apparent spread.
3. SNAPSHOTS: make 60 read-only batch book snapshots, one every 10 seconds for 10 minutes. Record request time, each book timestamp/hash and raw response hash. No orders, wallet, API key, capital or resolution data.
4. PRIMARY IDENTITY: for each event and each component outcome i, simulate the direct negative-risk conversion route at executable depth: buy q NO_i at depth-weighted asks; convert NO_i -> YES_j for every j != i; sell those YES_j at depth-weighted bids. Use each market's exposed taker-fee schedule. Define `net_quote_gap_i(q) = sum_j!=i(net_bid_proceeds_YES_j) - gross_cost_NO_i`.
5. LEGAL COMMON SIZE: choose the smallest integer q that satisfies every involved leg's published minimum notional; if available depth cannot fill q, mark the route unavailable rather than extrapolating. Reject snapshots with missing books or >1 second max timestamp skew across the route.
6. DISCRIMINANT: `STRUCTURAL_VIOLATION` only if `net_quote_gap_i(q) >= max(0.10 USDC, 10 bp of route gross notional)` in at least 3 non-adjacent snapshots or in at least 2 distinct events. This margin is deliberately above zero because conversion gas/latency is not measured in this first read-only screen. Otherwise classify `NO_MATERIAL_QUOTE_SPACE_VIOLATION_IN_SCREEN` and deprioritize the mechanism.
7. The test consumes no settlement outcome and no future sealed confirmation. If a structural violation is observed, the next stage is a separate conversion-cost/latency validation; it is not authority to trade.

BLOCKER = NONE_FOR_READ_ONLY_SCREEN. Operational exploitation remains blocked by unmeasured conversion gas/latency, cross-book execution risk, jurisdiction/terms checks, and absent live-trading/real-capital authority.

REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
