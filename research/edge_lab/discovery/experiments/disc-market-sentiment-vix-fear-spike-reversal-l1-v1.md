# Discovery V4.2 — VIX fear-spike reversal L1 v1

STATUS = PREDECLARED_BEFORE_JOINED_SIGNAL_RETURN_ACCESS
LABEL = EXPLORATORY
PARENT = `../qualifications/market-sentiment-vix-fear-spike-reversal-l0-2026-10-14.json`
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
paid_usd_total = 0

## Question

When VIX first enters an unusually high tail relative only to its own trailing history, does a strictly next-close long S&P 500 proxy earn enough over the following five closes to justify deeper execution/capturability work?

## Frozen data routes

Signal only:
- FRED `VIXCLS`, daily close, source Cboe.

Outcome proxy only:
- FRED `SP500`, daily close.

No alternate volatility index, intraday value, ETF, futures contract, realized-vol filter, macro filter or third-party price source may replace these routes after this declaration.

## Frozen sample

- Warm-up VIX history: all valid `VIXCLS` closes needed before `2018-01-01` to build the first 252-observation threshold.
- Economic signal dates: `2018-01-01 <= signal_date <= 2024-12-31`.
- No 2025/2026 date enters the economic sample.

Prior exposure disclosure: generic current-2026 VIX snippets and one old 2014 VIX snippet were visible during source qualification. No joined 2018-2024 VIX/SP500 signal-return pair was inspected before this declaration.

## Frozen signal

For each valid VIX close on date `t`:

- take exactly the 252 immediately preceding valid VIX closes, excluding current `t`;
- compute `Q95_t` with linear empirical quantile equivalent to NumPy `quantile(..., 0.95, method="linear")`;
- current day is `EXTREME_t = VIX_t >= Q95_t`.

A trigger occurs only when:

1. `EXTREME_t = true`; and
2. on the immediately preceding valid VIX observation `t-1`, `EXTREME_(t-1) = false` using its own prior-252 threshold.

This is an entry-into-extreme event, not every day spent above the threshold.

No percentile, lookback or direction change is permitted after outcome access.

## Frozen trade-proxy clock

Direction is always `LONG` SP500 for this exact contrarian expression.

For each trigger:
- `ENTRY_DATE = first finite SP500 close strictly AFTER signal_date`;
- entry must be within 4 calendar days after signal_date;
- `EXIT_DATE = fifth subsequent finite SP500 close after ENTRY_DATE`;
- exit must be within 10 calendar days after entry.

To prevent clustered crisis signals from implicitly multiplying exposure, events are non-overlapping:
- after an accepted trigger opens an event, ignore any later trigger whose `ENTRY_DATE <= active EXIT_DATE`;
- this suppression is mechanical and outcome-independent.

Missing entry/exit within the fixed bounds => `PARK_DATA` for the whole test; no alternate close or source.

## Frozen economics

For each accepted event:

`GROSS_BP = 10000 * (EXIT_CLOSE / ENTRY_CLOSE - 1)`

Screening hurdles only:
- `CENTRAL_COST_BP = 10`;
- `STRESS_COST_BP = 25`;
- `CENTRAL_NET_BP = GROSS_BP - 10`;
- `STRESS_NET_BP = GROSS_BP - 25`.

These are not authenticated ES/SPY execution costs. No futures multiplier, leverage, margin, roll, bid/ask, slippage or capacity claim is permitted.

## Adequacy

Require all source/clock rules plus:
- at least 12 accepted non-overlapping events across 2018-2024;
- accepted events must span at least 4 distinct calendar years.

If source/clock integrity fails => `PARK_DATA`.
If the source is valid but signal incidence fails the 12-event/4-year adequacy rule => `PARK_ECONOMICS` without a kill/promote verdict and without changing the threshold.

## Required outputs

For every accepted event report:
- signal date;
- VIX close;
- Q95 threshold;
- entry date / SP500 close;
- exit date / SP500 close;
- gross bp.

Aggregate exactly:
- event count and number of distinct calendar years;
- gross mean / median / worst;
- central-net mean;
- stress-net mean;
- positive gross count / total;
- calendar-year gross totals 2018 through 2024 (zero if no accepted event that year);
- break-even friction = gross mean bp;
- descriptive year-block bootstrap gross-mean interval: resample the seven calendar-year blocks, 2,000 draws, seed `41015`, 95% interval.

No iid p-value, Sharpe, CAGR or annualized alpha.

## Decision rule

After adequacy passes:

`KILL_EXPRESSION` if either:
- gross mean <= 0; or
- central-net mean <= 0.

`PROMOTE_EXPRESSION` only if ALL are true:
- central-net mean >= 35 bp per event;
- stress-net mean > 0;
- positive gross fraction >= 60%.

Otherwise `PARK_ECONOMICS`.

## One adversarial check

Run only if the primary result qualifies for `PROMOTE_EXPRESSION`.

Remove the single calendar-year block with the largest positive gross year-total; earliest year breaks a tie. Recompute remaining-event central-net mean. It must remain > 0 or the verdict downgrades to `PARK_ECONOMICS`.

No second adversarial check, nearby percentile, alternate holding period, trend condition, VIX-level floor, macro split or crisis exclusion is authorized.

## Bias / alternative explanations

- High VIX can correctly anticipate further losses; this expression bears crash/liquidity risk.
- Rebounds after fear spikes may be risk compensation rather than mispricing.
- The sample includes COVID and multiple rate/geopolitical regimes; events are dependent and sparse.
- VIX and SP500 closes are index observations, not guaranteed simultaneous executable fills.
- Year-block bootstrap is descriptive only.

## Inference ceiling

TEST_CAN_KILL = this exact next-close, 5-close, q95-entry fear-reversal expression.
TEST_CAN_SUPPORT = `PROMOTE_EXPRESSION`, meaning only that stricter execution/capturability work may be worth doing.
TEST_CANNOT_SAY = ALPHA, EDGE_VALIDATED, LIVE_READY, CAUSAL_FORCED_SELLING, EXECUTABLE_FUTURES_PNL, CAPACITY, LEVERAGE, REAL_CAPITAL_READINESS.
