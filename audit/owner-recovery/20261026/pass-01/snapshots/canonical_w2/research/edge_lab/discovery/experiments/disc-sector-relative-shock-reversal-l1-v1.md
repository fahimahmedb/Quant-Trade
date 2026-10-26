# Discovery V4.2 — sector relative-shock reversal L1 v1

STATUS = PREDECLARED_BEFORE_OUTCOME_ACCESS
LABEL = EXPLORATORY
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE

## Mechanism

MECHANISM = A large one-day move of one U.S. sector ETF relative to the contemporaneous cross-sector median can partly reflect concentrated allocation/ETF-flow and dealer inventory pressure rather than new permanent sector information. After the close reveals the shock, some of that pressure may reverse during the next session.
WHO_PAYS = Large allocators/rebalancers demanding immediacy and liquidity providers carrying temporary sector inventory.
WHY_PERSIST = Sector reallocations and benchmark/rebalancing flows are lumpy, while small actors can trade sizes far below the capacity needed to eliminate a short-lived cross-sectional dislocation.

## Distinctness / closed-family guard

MECHANISM_CLUSTER = sector-relative-flow-reversal
CLOSED_FAMILY_NOT_REOPENED = daily-etf-b2-b4
DISTINCTNESS = This expression is defined only by contemporaneous cross-sectional sector-relative shocks and next-session open-to-close reversal. It does not reuse any B2/B4 parameter, threshold, outcome, shadow result, or post-outcome variant. If an existing B2/B4 contract is later shown to use the same economic signal AND the same payoff horizon, abort this expression as DUPLICATE before reading its result.

## Frozen dataset

DATASET = data/datasets/us_sector_etf_daily.csv
DATASET_META = data/datasets/us_sector_etf_daily.meta.json
DATASET_FINGERPRINT_EXPECTED = sha256:f108a6f41552afdb42100d3188d7194006de1aae6a27bd7722330818e6dcb6d1
SOURCE = already-committed Yahoo Finance daily-bar panel; no new market-data request.
SAMPLE = full aligned committed panel, 2016-09-12 through 2026-09-11.
UNIVERSE = XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY only.
REQUIRED_COLUMNS = date, symbol, open, close.
PRICE_FIELD = raw open/close only. adj_close is not used because the sidecar records retrospective corporate-action restatement.

Pre-outcome schema rule: if any required column is absent, any sector does not cover the aligned panel, or any raw sector close-to-close absolute return exceeds 25% (mechanical split/corporate-action contamination guard), return PARK_DATA. Do not repair/exclude individual observations after seeing payoffs.

## Frozen signal

For each aligned session t after the first:
1. Compute each sector's raw close-to-close return r(i,t) = close(i,t) / close(i,t-1) - 1.
2. Compute the median of the nine sector returns on t.
3. residual(i,t) = r(i,t) - median_sector_return(t).
4. Select at most two events per day: the sector with the maximum residual and the sector with the minimum residual.
5. Positive event exists only if max residual >= +0.0200. Negative event exists only if min residual <= -0.0200.
6. SIGNAL = -sign(residual): short the positive extreme, long the negative extreme.

No other sector/date is traded. No threshold search is allowed.

## Frozen payoff

The signal is known only after session t closes.
ENTRY_PROXY = next aligned session t+1 raw OPEN of that same ETF.
EXIT_PROXY = t+1 raw CLOSE.
SIGNED_GROSS_RETURN = SIGNAL * (close(t+1) / open(t+1) - 1).
CENTRAL_ROUNDTRIP_COST = 0.0008 (8 bps).
STRESS_ROUNDTRIP_COST = 0.0015 (15 bps).
CENTRAL_NET_RETURN = gross - 0.0008.
STRESS_NET_RETURN = gross - 0.0015.

Daily bars are proxies, not authenticated executable fills.

## Adequacy

Require all:
- at least 80 events total;
- at least 25 positive-shock events and 25 negative-shock events;
- at least 90% of qualifying events have a next-session open and close;
- no event exclusion based on subsequent return.

Failure => PARK_DATA. No threshold/window/cost/universe change.

## Frozen decision rule

KILL_EXPRESSION if pooled mean CENTRAL_NET_RETURN <= 0.

PROMOTE_EXPRESSION only if ALL are true:
- pooled mean SIGNED_GROSS_RETURN >= +0.0015 (+15 bps);
- pooled mean CENTRAL_NET_RETURN >= +0.0005 (+5 bps);
- pooled mean STRESS_NET_RETURN > 0;
- median CENTRAL_NET_RETURN > 0;
- CENTRAL_NET_RETURN hit rate > 0 is >= 53%;
- mean CENTRAL_NET_RETURN > 0 separately for positive-shock and negative-shock events;
- mean CENTRAL_NET_RETURN > 0 in both chronological blocks: 2016-09-12..2021-12-31 and 2022-01-01..2026-09-11;
- the single adversarial check below passes.

Otherwise => PARK_ECONOMICS.

## Single adversarial check

Run only if all primary promotion criteria pass.
Remove the UTC/calendar year with the largest positive sum of CENTRAL_NET_RETURN; earliest year breaks ties. PASS only if remaining pooled mean CENTRAL_NET_RETURN > 0. No other variant/adversary/search is allowed.

## Inference rights

TEST_CAN_KILL = KILL_EXPRESSION only.
TEST_CAN_SUPPORT = PROMOTE_EXPRESSION only.
TEST_CANNOT_SAY = ALPHA, EDGE_VALIDATED, LIVE_READY, EXECUTABLE_PNL, CAUSAL_IDENTIFICATION, CAPACITY, OR REOPEN DAILY-ETF-B2-B4.

Known limits: consolidated Yahoo daily bars, raw-price corporate-action sensitivity guarded only by fail-closed 25% rule, cross-sectional/day dependence, no authenticated open/close fill, no borrow/short locate modelling, and mechanism may be ordinary short-horizon reversal rather than ETF-flow causality.
