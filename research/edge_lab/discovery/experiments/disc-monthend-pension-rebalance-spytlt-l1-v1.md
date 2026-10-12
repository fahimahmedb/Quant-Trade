# Discovery V4.2 — month-end pension rebalance SPY/TLT L1 v1

STATUS = PREDECLARED_BEFORE_OUTCOME_ACCESS
LABEL = EXPLORATORY
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE

## Mechanism

MECHANISM = Target-weight pension / balanced-portfolio rebalancing can create predictable month-end demand: when equities outperform bonds during the month, allocators must sell equities and buy bonds to restore weights, and vice versa. The pressure is concentrated into the final trading session because benchmark tracking and month-end valuation make timing non-uniform.
WHO_PAYS = Large target-weight allocators accepting implementation pressure near month-end to restore mandated weights.
WHY_PERSIST = The flow is mandate-driven rather than informational, and small capital can trade far below the capacity of the institutional rebalancing flow.
MECHANISM_CLUSTER = monthend-crossasset-rebalancing

## Closed-family guard

CLOSED_FAMILY_NOT_REOPENED = daily-etf-b2-b4
DUPLICATE_ABORT_RULE = If a pre-existing B2/B4 frozen contract is later shown to use the same month-to-date SPY-vs-TLT relative-performance signal AND the same final-session open-to-close SPY/TLT relative-spread payoff, classify DUPLICATE and do not read this result. A bounded repository search before this freeze found no exact month-end pension/rebalancing expression.

## Frozen dataset

DATASET = data/datasets/us_sector_etf_daily.csv
DATASET_META = data/datasets/us_sector_etf_daily.meta.json
DATASET_FINGERPRINT_EXPECTED = sha256:f108a6f41552afdb42100d3188d7194006de1aae6a27bd7722330818e6dcb6d1
SOURCE = already-committed Yahoo Finance daily-bar panel; no new market-data request.
SYMBOLS = SPY, TLT only.
REQUIRED_COLUMNS = date, symbol, open, close.
PRICE_FIELDS = raw open and raw close only; adj_close is not used.
SAMPLE = all complete calendar months whose previous month-end close, penultimate trading-session close, and final trading-session open/close are present inside the committed 2016-09-12..2026-09-11 panel.

Fail closed to PARK_DATA before payoff calculation if: required exact columns are absent; SPY/TLT dates are not exactly aligned; either symbol has any raw close-to-close absolute daily return >25%; or the sidecar fingerprint differs. No aliases, split repair, date substitution, or observation exclusion after claim.

## Frozen signal

For each eligible calendar month M:
1. PREV_END = last aligned trading session of calendar month M-1.
2. PENULTIMATE = second-to-last aligned trading session of M.
3. FINAL = last aligned trading session of M.
4. Compute raw month-to-date returns known after PENULTIMATE close:
   R_SPY_MTD = SPY_close(PENULTIMATE) / SPY_close(PREV_END) - 1.
   R_TLT_MTD = TLT_close(PENULTIMATE) / TLT_close(PREV_END) - 1.
5. RELATIVE_MTD = R_SPY_MTD - R_TLT_MTD.
6. SIGNAL = -sign(RELATIVE_MTD). If RELATIVE_MTD == 0 exactly, no event for that month.

Interpretation: SIGNAL=-1 means short SPY / long TLT; SIGNAL=+1 means long SPY / short TLT.

No magnitude threshold and no parameter search.

## Frozen payoff

On FINAL session:
SPY_OC = SPY_close(FINAL) / SPY_open(FINAL) - 1.
TLT_OC = TLT_close(FINAL) / TLT_open(FINAL) - 1.
RELATIVE_OC = SPY_OC - TLT_OC.
SIGNED_GROSS_RETURN = SIGNAL * RELATIVE_OC.
CENTRAL_ROUNDTRIP_COST = 0.0008 (8 bps total for the two-leg spread).
STRESS_ROUNDTRIP_COST = 0.0016 (16 bps total).
CENTRAL_NET_RETURN = gross - 0.0008.
STRESS_NET_RETURN = gross - 0.0016.

Daily open/close bars are proxies, not authenticated fills. Borrow, financing and legging risk are not modeled.

## Adequacy

Require all:
- at least 100 eligible monthly events;
- at least 40 SIGNAL=+1 and at least 40 SIGNAL=-1 events;
- 100% endpoint coverage for eligible events because the panel is pre-aligned.

Failure => PARK_DATA. No threshold, horizon, cost, sample, or instrument change.

## Frozen decision rule

KILL_EXPRESSION if pooled mean CENTRAL_NET_RETURN <= 0.

PROMOTE_EXPRESSION only if ALL are true:
- pooled mean SIGNED_GROSS_RETURN >= +0.0015 (+15 bps);
- pooled mean CENTRAL_NET_RETURN >= +0.0005 (+5 bps);
- pooled mean STRESS_NET_RETURN > 0;
- median CENTRAL_NET_RETURN > 0;
- CENTRAL_NET_RETURN hit rate > 0 is >= 53%;
- mean CENTRAL_NET_RETURN > 0 separately for SIGNAL=+1 and SIGNAL=-1;
- mean CENTRAL_NET_RETURN > 0 in both chronological blocks: through 2021-12-31 and from 2022-01-01 onward;
- the single adversarial check below passes.

Otherwise => PARK_ECONOMICS.

## Single adversarial check

Run only if all primary promotion criteria pass.
Remove the calendar year with the largest positive sum of CENTRAL_NET_RETURN; earliest year breaks ties. PASS only if remaining pooled mean CENTRAL_NET_RETURN > 0. No other variant, threshold, alternate close, or nearby month-end window is allowed.

## Inference rights

TEST_CAN_KILL = KILL_EXPRESSION only.
TEST_CAN_SUPPORT = PROMOTE_EXPRESSION only.
TEST_CANNOT_SAY = ALPHA, EDGE_VALIDATED, LIVE_READY, EXECUTABLE_PNL, CAUSAL_IDENTIFICATION, CAPACITY, OR REOPEN DAILY-ETF-B2-B4.

Known limits: daily consolidated proxy bars; raw-close dividend effects in the month-to-date signal; only SPY/TLT as equity/bond proxies; no actual pension-flow measurement; no closing-auction imbalance data; cross-leg execution/financing not authenticated.
