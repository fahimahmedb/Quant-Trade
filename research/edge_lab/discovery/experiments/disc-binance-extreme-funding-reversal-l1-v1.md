# Discovery V4.2 — Binance extreme-funding reversal L1 v1

STATUS = PREDECLARED_BEFORE_OUTCOME_ACCESS
LABEL = EXPLORATORY
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE

## Mechanism

MECHANISM = Extreme same-sign perpetual funding is a public proxy for crowded leveraged positioning. After the funding timestamp, crowded traders may de-risk or mean-revert, creating a short-horizon move opposite the funding sign.
WHO_PAYS = Leveraged traders who remain crowded into the funding clock and then de-risk under inventory/margin pressure.
WHY_PERSIST = Periodic funding settlement, leverage constraints and heterogeneous forced/voluntary deleveraging can create recurring inventory pressure even when the funding rate itself is public.

## Relation to closed F1 crypto-carry

RELATION = CAUSALLY_DISTINCT_EXPRESSION
WHY_DISTINCT = F1 monetized the funding/basis carry itself. This test does not earn funding and does not hold a carry book. Funding is used only as a crowding state variable; the tested payoff is the subsequent directional reversal after the funding event. Same upstream observable does not imply the same monetization path.
DO_NOT_REOPEN_F1 = TRUE

## Frozen data

VENUE = Binance USD-M Futures
SYMBOLS = BTCUSDT, ETHUSDT only
EVENT_SOURCE = official public GET /fapi/v1/fundingRate
PRICE_SOURCE = official public GET /fapi/v1/klines, interval=5m
SAMPLE_START_UTC = 2021-01-01T00:00:00Z
SAMPLE_END_UTC = 2025-12-31T23:59:59Z
PAID_USD = 0

No economic endpoint has been queried for this expression before this predeclaration. Documentation/source-feasibility inspection only is permitted pre-freeze.

## Frozen event and payoff

EVENT = a BTCUSDT or ETHUSDT funding record with abs(fundingRate) >= 0.0005 (5 bps per funding interval).
SIGNAL = -sign(fundingRate).
ENTRY_PROXY = close of the first complete 5-minute futures kline whose open time is >= fundingTime.
EXIT_PROXY = close of the complete 5-minute futures kline ending nearest to fundingTime + 8 hours without using a bar ending after fundingTime + 8h + 5m.
SIGNED_GROSS_RETURN = SIGNAL * (EXIT_PROXY / ENTRY_PROXY - 1).
CENTRAL_ROUNDTRIP_COST = 0.0010 (10 bps).
SIGNED_NET_RETURN = SIGNED_GROSS_RETURN - 0.0010.

This is a close-to-close proxy, not an executable fill claim. No funding cashflow is included in PnL.

## Adequacy

Require all of:
- at least 30 qualifying events total;
- at least 5 qualifying events for each symbol;
- at least 90% of qualifying funding events have both frozen price endpoints;
- no event exclusion based on subsequent return;
- no threshold, horizon, symbols, cost, or sample-window change after outcome access.

If adequacy fails: PARK_DATA. Do not tune the threshold to manufacture sample size.

## Decision rule

KILL_EXPRESSION if mean SIGNED_NET_RETURN <= 0.

PROMOTE_EXPRESSION only if all are true:
- mean SIGNED_GROSS_RETURN >= 0.0020 (+20 bps);
- mean SIGNED_NET_RETURN > 0;
- median SIGNED_NET_RETURN > 0;
- hit rate SIGNED_NET_RETURN > 0 is >= 55%;
- mean SIGNED_GROSS_RETURN is > 0 separately for BTCUSDT and ETHUSDT;
- the single frozen adversarial check below passes.

Otherwise: PARK_ECONOMICS.

## Single adversarial check

Run only if the primary promotion criteria pass.
Remove the UTC calendar month with the largest positive sum of SIGNED_NET_RETURN across all events; earliest month breaks ties. PASS only if the remaining pooled mean SIGNED_NET_RETURN remains > 0. No additional variant search.

## Inference rights

TEST_CAN_KILL = KILL_EXPRESSION only.
TEST_CAN_SUPPORT = PROMOTE_EXPRESSION only.
TEST_CANNOT_SAY = ALPHA, EDGE_VALIDATED, LIVE_READY, EXECUTABLE_PNL, CAUSAL_IDENTIFICATION, CAPACITY, KILL_F1, PROMOTE_F1.

Main known biases: Binance venue selection, 2021 crypto-regime concentration, mark/last-price microstructure around funding, cross-symbol dependence, close-to-close non-executability, current cost assumption not historical fee proof.
