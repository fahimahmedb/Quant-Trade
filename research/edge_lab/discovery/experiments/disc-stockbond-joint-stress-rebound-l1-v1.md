# Discovery V4.2 — stock/bond joint-stress rebound L1 v1

STATUS = PREDECLARED_BEFORE_OUTCOME_ACCESS
LABEL = EXPLORATORY
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE

## Mechanism

MECHANISM = A same-day material selloff in both equities and long-duration Treasuries can indicate cross-asset deleveraging / margin-driven liquidation rather than independent fundamental information in both legs. Once the forced flow is absorbed, some of the pressure may reverse during the next session.
WHO_PAYS = Leveraged balanced/risk-parity investors and other multi-asset holders forced to reduce gross exposure under volatility, margin, or risk-budget pressure.
WHY_PERSIST = Deleveraging is constraint-driven, lumpy, and often implemented through the most liquid instruments; small capital can trade far below the capacity of those forced flows.
MECHANISM_CLUSTER = crossasset-forced-deleveraging

## Closed-family guard

CLOSED_FAMILY_NOT_REOPENED = daily-etf-b2-b4
DISTINCTNESS = Signal requires a joint stock-and-bond stress state and tests a next-session two-leg rebound. It does not use sector residuals, single-asset technical ranks, B2/B4 parameters, or any B2/B4 outcome/shadow. If a pre-existing frozen B2/B4 contract is later demonstrated to use the same joint SPY/TLT threshold AND same next-session two-leg open-to-close payoff, abort as DUPLICATE before reading this result.

## Frozen data

DATASET = data/datasets/us_sector_etf_daily.csv
DATASET_META = data/datasets/us_sector_etf_daily.meta.json
DATASET_FINGERPRINT_EXPECTED = sha256:f108a6f41552afdb42100d3188d7194006de1aae6a27bd7722330818e6dcb6d1
SYMBOLS = SPY, TLT only
REQUIRED_COLUMNS = date, symbol, open, close
PRICE_FIELDS = raw open/close only; adj_close not used.
SAMPLE = full aligned committed panel 2016-09-12 through 2026-09-11.

Before any payoff calculation, PARK_DATA if required columns are absent, SPY/TLT dates are not exactly aligned, sidecar fingerprint differs, or either raw close-to-close daily return exceeds 25%. No post-claim alias, split repair, or observation exclusion.

## Frozen signal

For aligned session t after the first:
R_SPY(t) = SPY_close(t) / SPY_close(t-1) - 1.
R_TLT(t) = TLT_close(t) / TLT_close(t-1) - 1.
A JOINT_STRESS event occurs iff:
- R_SPY(t) <= -0.0100 (-1.00%), AND
- R_TLT(t) <= -0.0050 (-0.50%).

The event is known after t closes. No threshold search is allowed.

## Frozen payoff

ENTRY = next aligned session t+1 raw OPEN in both SPY and TLT.
EXIT = same next session raw CLOSE in both.
GROSS_RETURN = 0.5 * (SPY_close/open - 1) + 0.5 * (TLT_close/open - 1).
CENTRAL_ROUNDTRIP_COST = 0.0008 (8 bps on the equal-weight portfolio).
STRESS_ROUNDTRIP_COST = 0.0015 (15 bps).
CENTRAL_NET_RETURN = gross - 0.0008.
STRESS_NET_RETURN = gross - 0.0015.

This is a daily-bar portfolio proxy, not authenticated executable PnL. No leverage, financing, slippage, or market impact claim.

## Adequacy

Require all:
- at least 20 qualifying events total;
- at least 5 events with signal_date <= 2021-12-31;
- at least 5 events with signal_date >= 2022-01-01;
- 100% next-session open/close coverage for qualifying events.

Failure => PARK_DATA. No threshold/sample/instrument/cost change after access.

## Frozen decision rule

KILL_EXPRESSION if pooled mean CENTRAL_NET_RETURN <= 0.

PROMOTE_EXPRESSION only if ALL are true:
- pooled mean GROSS_RETURN >= +0.0020 (+20 bps);
- pooled mean CENTRAL_NET_RETURN >= +0.0010 (+10 bps);
- pooled mean STRESS_NET_RETURN > 0;
- median CENTRAL_NET_RETURN > 0;
- CENTRAL_NET_RETURN hit rate > 0 >= 55%;
- mean CENTRAL_NET_RETURN > 0 in both chronological blocks (through 2021 and from 2022);
- the single adversarial check below passes.

Otherwise => PARK_ECONOMICS.

## Single adversarial check

Run only if all primary promotion criteria pass. Remove the calendar year with the largest positive sum of CENTRAL_NET_RETURN; earliest year breaks ties. PASS only if remaining pooled mean CENTRAL_NET_RETURN > 0. No alternate threshold, horizon, weighting, leg subset, or nearby stress definition is allowed.

## Inference rights

TEST_CAN_KILL = KILL_EXPRESSION only.
TEST_CAN_SUPPORT = PROMOTE_EXPRESSION only.
TEST_CANNOT_SAY = ALPHA, EDGE_VALIDATED, LIVE_READY, EXECUTABLE_PNL, CAUSAL_IDENTIFICATION, CAPACITY, RISK_PARITY_FLOW_PROVEN, OR REOPEN DAILY-ETF-B2-B4.

Known limits: raw Yahoo daily-bar proxy, no direct leverage/margin-flow observation, threshold may mix macro-information shocks with forced flow, cross-asset execution/financing not authenticated, small event count possible by construction.
