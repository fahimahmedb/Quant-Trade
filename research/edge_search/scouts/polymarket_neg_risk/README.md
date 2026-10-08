# Polymarket standard negative-risk — read-only parity screen

DATE = 2026-10-08
STATUS = SCOUT_IMPLEMENTATION_ONLY
FLB_BELONGS_TO_EXISTING_F2 = TRUE
NEW_FAMILY_CREATED_FOR_FLB = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
OUTCOME_CONFIRMATION_READ = FALSE

## Scope decision

Favourite–Longshot Bias is already represented by `research/kalshi_flb_f2/` (`KALSHI-FLB-OOS-001`). The scout FLB proposal changes statistical expression/breadth, not causal mechanism, so no separate family is opened. Remaining work is exclusively the causally distinct Polymarket standard negative-risk parity mechanism.

## Official public read surface used

The collector intentionally contains no wallet, API key, order, conversion, position, settlement-result or resolution endpoint.

- Gamma discovery: `GET https://gamma-api.polymarket.com/events?closed=false&order=id&ascending=true&limit=100&offset=N`
- Gamma completeness refresh: `GET https://gamma-api.polymarket.com/events/{event_id}`
- CLOB depth snapshot: `POST https://clob.polymarket.com/books` with body `[ {"token_id": "..."}, ... ]`.
- Single-book diagnostic, not needed by the primary collector: `GET https://clob.polymarket.com/book?token_id=...`.
- Fee diagnostic, not needed when Gamma `feeSchedule` is complete: `GET https://clob.polymarket.com/fee-rate?token_id=...`.

Sources checked 2026-10-08:
- https://docs.polymarket.com/market-data/discover-markets
- https://docs.polymarket.com/market-data/market-details
- https://docs.polymarket.com/concepts/negative-risk
- https://docs.polymarket.com/api-reference/market-data/get-order-book
- https://docs.polymarket.com/api-reference/market-data/get-order-books-request-body
- https://docs.polymarket.com/api-reference/market-data/get-fee-rate
- https://docs.polymarket.com/trading/fees

The earlier scout note's blanket `500 token` claim for `/books` is withdrawn: the current `/books` reference confirms the batch endpoint but does not state 500 on that page. This collector therefore uses a conservative **local** cap of 100 token IDs per event and does not present it as an exchange limit.

## Outcome-set completeness and `Other`

Standard negative risk requires the complete outcome set to be known at market creation. The collector therefore accepts an event only when:

1. `enableNegRisk == true`;
2. `negRiskAugmented == false` explicitly — missing is rejected;
3. at least three component markets are present;
4. every component is `active == true`, `closed == false`, `acceptingOrders == true`, `enableOrderBook == true`, `negRisk == true`;
5. every component has exactly binary `Yes/No` labels, exactly two unique CLOB token IDs and a unique condition ID;
6. the event is re-fetched by ID and the condition-ID set must be unchanged before books are sampled.

`Other` is **not** rejected by string matching. In a standard negative-risk event, an `Other` outcome may legitimately be part of the complete partition. In augmented negative risk, placeholders can be clarified after launch and the meaning of `Other` narrows as they are assigned. Therefore the entire augmented event is excluded, including apparently named current components and `Other`.

## Fees and depth

No midpoint, displayed probability, last trade or Gamma `outcomePrices` is used in parity arithmetic.

For each event, all YES and NO token books needed for the event are requested in one `/books` call. Each returned book must:
- be present exactly once;
- report `neg_risk == true`;
- expose timestamp, bids, asks, `min_order_size`, tick size and book hash;
- have cross-token timestamp skew <= 1,000 ms.

Depth is walked level-by-level. A route is unavailable if any required leg cannot fill the common share quantity `q`; no extrapolation or top-of-book fantasy fill is allowed.

Fee source is the market's Gamma `feesEnabled` + `feeSchedule`. Fee-enabled markets without an explicit schedule are rejected. The generic model is:

`fee_usdc = shares * rate * [p * (1-p)] ** exponent`

and is applied per consumed depth level. Taker fees are rounded **up** to 5 decimals in the screen, which is conservative relative to the documented 5-decimal fee precision. Fee-free markets use zero.

Known documentation ambiguity: Gamma's market-details page currently describes `orderMinSize` as USDC notional while the CLOB order-book surface exposes `min_order_size` without a unit on that API page; current CLOB client semantics treat book `min_order_size` as share quantity. The read-only screen uses the CLOB field as the common share floor. This ambiguity must be resolved before any execution-capable stage; it cannot authorize live trading.

## Basket arithmetic

For each source outcome `i` in an N-outcome standard negative-risk event:

1. buy `q` shares of `NO_i` by walking the `NO_i` asks;
2. apply the documented atomic identity conceptually: `NO_i -> YES_j` for every `j != i`;
3. sell `q` shares of every `YES_j, j != i` by walking each YES bid book;
4. apply taker fee at every consumed price level;
5. compute:

`gap_i(q) = sum(net sell proceeds YES_j) - (NO_i buy cost + NO_i taker fee)`

`gross_traded_notional = NO buy gross + sum(YES sell gross)`

`screen_threshold = max(0.10 pUSD, 10 bp * gross_traded_notional)`

A snapshot-level quote-space violation is `gap_i(q) >= screen_threshold`. This does **not** include conversion gas/relayer latency/cross-book fill risk, so it is only a discovery signal.

## Minimum discriminating screen

Deterministic metadata selection: sort eligible standard-neg-risk event IDs ascending and take the first 10, with no price/spread cherry-picking. For each selected event, collect 60 snapshots at 10-second spacing. Primary evidence requires either:
- the same route to exceed the threshold in >=3 non-adjacent snapshots; or
- threshold exceedance in >=2 distinct events.

Otherwise classify `NO_MATERIAL_QUOTE_SPACE_VIOLATION_IN_SCREEN` and deprioritize. A positive screen only authorizes a separate conversion-cost/latency study; it does not authorize an order.

## Synthetic verification

`python -m unittest -v test_neg_risk_collector.py`

The synthetic suite covers:
- standard `Other` accepted;
- augmented / unknown semantics rejected;
- incomplete live component rejected;
- multi-level depth walking;
- insufficient depth fail-closed;
- conservative fee rounding;
- clearly profitable synthetic conversion basket;
- small quote gap removed by fees;
- timestamp-skew rejection;
- missing-book rejection.

Local result before push: **11 tests, all PASS**.

## Remaining blockers before anything beyond read-only discovery

- resolve minimum-order-size unit ambiguity against the production contract/API version;
- measure actual Neg Risk Adapter conversion cost and latency on the current protocol version;
- model asynchronous cross-book execution/fill risk rather than simultaneous quote-space arithmetic;
- verify jurisdiction/terms for any action beyond public data reads;
- obtain explicit authority for any authenticated, on-chain, order or capital action.

REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
