# Discovery V4.2 — CFTC E-mini S&P 500 leveraged-funds extremes L1 v1

STATUS = PREDECLARED_BEFORE_JOINED_SIGNAL_RETURN_ACCESS
LABEL = EXPLORATORY
PARENT = `../qualifications/market-sentiment-cftc-es-leveraged-extremes-l0-2026-10-14.json`
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
paid_usd_total = 0

## Question

Does a simple release-lag-safe contrarian expression after unusually extreme Leveraged Funds net positioning in E-mini S&P 500 futures show enough subsequent 5-session cash-index reversal to justify deeper futures/execution reconstruction?

## Frozen data routes

Signal source only:
- CFTC Traders in Financial Futures — Futures Only;
- E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE;
- CFTC contract code `13874A` where available;
- fields: report date, open interest, Leveraged Money long, Leveraged Money short.

Outcome proxy only:
- FRED series `SP500`;
- daily S&P 500 close.

No alternate positioning report, asset-manager field, options-combined report, ETF, ES futures price, VIX filter or third-party signal source may replace either route after this declaration.

## Frozen sample and warm-up

- Signal evaluation sample: CFTC report dates from `2020-01-01` through `2024-12-31` inclusive.
- Warm-up signal history: use 2019 reports only as needed to provide the 52 prior observations for early-2020 thresholds.
- No 2025 or 2026 report enters the economic sample.

Reason for ending at 2024: 2025 COT publication was disrupted by a documented appropriations lapse/backlog. This exclusion is fixed before joined returns are inspected.

Adequacy requires:
- one unique E-mini S&P 500 TFF Futures-Only row per CFTC report date used;
- finite open interest > 0 and finite Leveraged Money long/short;
- at least 52 prior valid weekly signal observations before any current report can trigger;
- at least 30 triggered events total in 2020-2024;
- at least 8 LONG and at least 8 SHORT triggered events.

If source integrity fails, or fewer than 30 total / 8 per direction trigger, return `PARK_DATA` or `PARK_ECONOMICS` as appropriate without threshold/horizon changes.

## Frozen signal

For every valid report row define:

`NET_PCT_OI = (Lev_Money_Long - Lev_Money_Short) / Open_Interest_All`

For current report `t`, compute `Q10_t` and `Q90_t` from exactly the 52 immediately preceding valid `NET_PCT_OI` observations, excluding current `t`, using linear empirical quantiles equivalent to NumPy `quantile(..., method="linear")`.

Signal:
- if current `NET_PCT_OI <= Q10_t`: `DIRECTION = +1` (LONG S&P proxy; contrarian to extreme leveraged-fund net short);
- if current `NET_PCT_OI >= Q90_t`: `DIRECTION = -1` (SHORT S&P proxy; contrarian to extreme leveraged-fund net long);
- otherwise no event.

If `Q10_t == Q90_t`, no signal for that report.

No percentile, lookback, category, normalization or direction change is authorized after outcome access.

## Frozen release-safe clock

CFTC report dates refer to Tuesday positions and are normally published later. To avoid using Tuesday information as if it were contemporaneously known:

- `TARGET_ENTRY_DATE = REPORT_DATE + 8 calendar days`;
- `ENTRY_DATE = first FRED SP500 finite close on or after TARGET_ENTRY_DATE`;
- entry must occur within 4 calendar days of TARGET_ENTRY_DATE;
- `EXIT_DATE = fifth subsequent finite SP500 daily close after ENTRY_DATE`;
- exit must occur within 10 calendar days of ENTRY_DATE.

No same-week Friday, Tuesday, next-day or alternative horizon is permitted.

This conservative lag is part of the expression. The test does not claim to reconstruct exact historical intraday COT publication timestamps.

## Frozen economics

For each triggered event:

`INDEX_RETURN = EXIT_CLOSE / ENTRY_CLOSE - 1`

`GROSS_BP = DIRECTION * 10000 * INDEX_RETURN`

Screening frictions/hurdles only:
- `CENTRAL_COST_BP = 10` per event;
- `STRESS_COST_BP = 25` per event;
- `CENTRAL_NET_BP = GROSS_BP - 10`;
- `STRESS_NET_BP = GROSS_BP - 25`.

These are not authenticated ES execution costs. No futures multiplier, margin, roll, slippage, market impact or live PnL claim is allowed.

## Required outputs

For the complete triggered-event sample report:
- total events and LONG/SHORT counts;
- chronological report/entry/exit dates, signal direction, `NET_PCT_OI`, `Q10`, `Q90`, and `GROSS_BP`;
- gross mean, median, worst event;
- central-net mean and stress-net mean;
- positive gross count / total;
- LONG subgroup gross and central-net means;
- SHORT subgroup gross and central-net means;
- calendar-year gross totals for 2020, 2021, 2022, 2023, 2024;
- break-even friction = gross mean bp;
- descriptive year-block bootstrap of gross mean: resample the five calendar-year blocks, 2,000 draws, seed `41014`, 95% descriptive interval.

No iid p-value, Sharpe, CAGR or alpha claim.

## Decision rule

After adequacy passes:

`KILL_EXPRESSION` if either:
- gross mean <= 0; or
- central-net mean <= 0.

`PROMOTE_EXPRESSION` only if ALL are true:
- central-net mean >= 25 bp per triggered event;
- stress-net mean > 0;
- positive gross fraction >= 55%;
- LONG subgroup gross mean > 0;
- SHORT subgroup gross mean > 0.

Otherwise `PARK_ECONOMICS`.

If adequacy/source-clock rules fail before a valid complete sample, use `PARK_DATA` where the failure is data/clock integrity, or `PARK_ECONOMICS` where the only failure is insufficient predeclared signal incidence.

## One adversarial check

Run only if the primary rule yields `PROMOTE_EXPRESSION`.

Remove the single calendar-year block with the largest positive gross year-total; earliest year breaks ties. Recompute the remaining-event central-net mean. It must remain > 0. Otherwise downgrade to `PARK_ECONOMICS`.

No second red-team, tail-specific retuning, nearby percentile, alternate lookback, trend filter or horizon search.

## Bias and alternative explanations

- COT is delayed and widely observed; any simple effect may already be arbitraged.
- Leveraged-fund positioning can be informed or trend-following rather than forced/crowded.
- Cash SP500 close is a coarse proxy, not ES executable fills.
- Weekly signals and 5-session outcomes are serially dependent; year-block bootstrap is descriptive only.
- 2020-2024 includes unusual pandemic/rate regimes and cannot establish permanent persistence.
- Generic 2025/2026 CFTC rows and one June-2025 E-mini S&P row were seen during source qualification; they are outside the frozen economic sample and were not used to choose outcomes. No pristine-source claim is made for those rows.

## Inference ceiling

TEST_CAN_KILL = this exact contrarian release-lagged leveraged-funds-extremes expression.
TEST_CAN_SUPPORT = `PROMOTE_EXPRESSION`, meaning only that deeper ES futures/capturability work may be worth doing.
TEST_CANNOT_SAY = ALPHA, EDGE_VALIDATED, LIVE_READY, CAUSAL_FORCED_FLOW, EXECUTABLE_ES_PNL, CAPACITY, LEVERAGE, REAL_CAPITAL_READINESS.
