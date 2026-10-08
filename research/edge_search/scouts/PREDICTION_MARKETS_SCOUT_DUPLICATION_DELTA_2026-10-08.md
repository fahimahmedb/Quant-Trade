# AGENT 2 — PREDICTION MARKETS DUPLICATION / NEG-RISK DELTA

DATE = 2026-10-08
BASE_SCOUT_COMMIT = ad9c518af4f1f41d3cf282ffdc8c98dc43945892
F2_EVIDENCE_SNAPSHOT = 25b95cdad27e4f1dfb00fdc4cfb670d6a25bd46b
OUTCOME_CONFIRMATION_READ = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE

## 1. FLB ownership is already F2

FLB_BELONGS_TO_EXISTING_F2 = TRUE
CANDIDATE_1_RELATION = SAME_FAMILY_NEW_EXPRESSION
NEW_FAMILY_CREATED_FOR_FLB = FALSE

EVIDENCE =
- MECHANISM: same favourite–longshot causal family. Scout Candidate 1 attributes low-probability overpricing to probability weighting/noisy demand and correction frictions; F2 `KALSHI-FLB-OOS-001` states the same mechanism.
- UNIVERSE: both target Kalshi binary contracts; cross-category breadth does not create a new mechanism.
- TIMING: scout proposed fixed pre-resolution horizons including T-24h; F2 fixes T-24h using a one-hour bid/ask candle.
- EXPRESSION: both economically buy the favourite/complement of the overpriced longshot and hold to settlement.
- DATA: same Kalshi market/event metadata, bid/ask/candlestick, fee and settlement data class; F2 already has blinded acquisition and a dedicated analysis harness.
- TEST: calibration bins/cross-category monotonicity are a different statistic around the same FLB family, not a causally distinct edge.

DECISION = Do not open another FLB family, do not reserve another Kalshi FLB confirmation window, and do not consume F2 outcomes for this scout.

## 2. All remaining scout capacity moved to Polymarket standard negative-risk parity

UPDATED_TOP_CANDIDATE = Cross-outcome structural pricing inconsistency in standard Polymarket negative-risk events.

WHY_CAUSALLY_DISTINCT = This mechanism requires no probability miscalibration and no settlement outcome. It tests a live algebraic identity created by the Neg Risk Adapter: one `NO_i` can be converted into one `YES_j` for every `j != i`. Candidate edge source is asynchronous books / fragmented liquidity / stale quotes, not longshot preference.

PUBLIC_READ_ENDPOINTS_VERIFIED =
- `GET https://gamma-api.polymarket.com/events?...` — public event discovery.
- `GET https://gamma-api.polymarket.com/events/{event_id}` — current event/component refresh.
- `POST https://clob.polymarket.com/books` — public batch order-book read; HTTP POST is data retrieval only.
- `GET https://clob.polymarket.com/book?token_id=...` — single-book diagnostic.
- `GET https://clob.polymarket.com/fee-rate?token_id=...` — fee diagnostic; primary arithmetic uses the market's explicit Gamma `feesEnabled`/`feeSchedule` and fails closed if fee-enabled configuration is incomplete.

BATCH_LIMIT_CORRECTION = The prior note's blanket `500 token` statement for `/books` is withdrawn. Current official `/books` reference confirms the endpoint/body but does not state 500 there. Implementation uses `MAX_EVENT_TOKENS = 100` as a local safety cap, not an exchange-limit claim.

## 3. Completeness / Other semantics

STANDARD_NEG_RISK_COMPLETENESS = Standard negative risk requires the full outcome set to be known at creation. Collector requires `enableNegRisk=true`, explicit `negRiskAugmented=false`, >=3 component markets, every component live/order-enabled/negRisk, unique condition IDs and exactly two unique YES/NO CLOB tokens. The event is fetched again by ID and the condition set must be unchanged before book sampling.

OTHER_SEMANTICS = A literal `Other` is allowed in standard negative risk. It is not filtered by text. Augmented negative risk is excluded as a whole because placeholders can be clarified later and the semantic coverage of `Other` narrows as placeholders are assigned. Missing `negRiskAugmented` also fails closed.

## 4. Fees / depth / arithmetic

EXECUTABLE_ONLY = No midpoint, Gamma displayed probability, last trade or outcome result enters parity arithmetic.

DEPTH = All event token books are requested together. Every required book must exist, report `neg_risk=true`, and have cross-token timestamp skew <= 1 second. The code walks every consumed ask/bid level. Missing depth makes the route unavailable; it is never extrapolated.

FEES = Per-level taker cost uses the explicit fee schedule: `shares * rate * [p*(1-p)]**exponent`, with conservative upward rounding to 5 decimals. Fee-enabled market with missing/unsupported schedule fails closed.

MIN_ORDER_SIZE_NOTE = Current documentation is not fully consistent on the unit of minimum order size: Gamma market details describe `orderMinSize` as USDC while CLOB `/book` exposes `min_order_size` without specifying units on that reference page. The read-only model treats CLOB `min_order_size` as the common share floor. This ambiguity is a blocker for execution-capable work, not for code/synthetic verification.

PRIMARY_ROUTE = For each source market i: buy q `NO_i` at executable asks -> conceptual atomic conversion -> sell q `YES_j` for every j != i at executable bids. `gap = sum(net YES sale proceeds) - (NO buy gross + NO taker fee)`.

SCREEN_THRESHOLD = `max(0.10 pUSD, 10 bp * total traded gross notional)`.

## 5. Collector / synthetic verification

IMPLEMENTATION = `research/edge_search/scouts/polymarket_neg_risk/neg_risk_collector.py`
CONTRACT = `research/edge_search/scouts/polymarket_neg_risk/README.md`
TESTS = `research/edge_search/scouts/polymarket_neg_risk/test_neg_risk_collector.py`

COLLECTOR_PROPERTIES = public reads only; no auth; no wallet; no order endpoint; no conversion call; no position endpoint; no settlement/result endpoint; raw `/books` responses stored once with SHA-256; deterministic event-ID selection; event completeness refetch; depth-aware route evaluation.

SYNTHETIC_TEST_RESULT = PASS — 11/11 locally before push.

TEST_COVERAGE = standard `Other`; augmented rejection; unknown augmented-state rejection; incomplete live component; multi-level depth; insufficient depth; fee rounding; profitable synthetic basket; fee-killed small gap; timestamp skew; missing token/book.

MINIMUM_DISCRIMINATING_TEST = Deterministically select the first 10 eligible standard-neg-risk event IDs (no price cherry-picking), then 60 read-only snapshots spaced 10 seconds apart. Require the same route over threshold in >=3 non-adjacent snapshots OR threshold exceedance in >=2 distinct events. Otherwise classify `NO_MATERIAL_QUOTE_SPACE_VIOLATION_IN_SCREEN`. A positive result only motivates a separate conversion-cost/latency validation.

BLOCKER = NONE_FOR_READ_ONLY_COLLECTION_CODE. Before any execution-capable stage: resolve min-order-size units; measure current Neg Risk Adapter conversion cost/latency; model asynchronous cross-book fill risk; check applicable terms/jurisdiction; obtain explicit live/capital authority.

REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
