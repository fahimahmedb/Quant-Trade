# Discovery V4.2 — France OAT/Bund delayed EDP repricing L1 v1 public-daily-route

STATUS = PREDECLARED_BEFORE_V1_EVENT_PAYOFF_ACCESS
LABEL = EXPLORATORY
PARENT = `disc-france-oat-bund-l1-v0`
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
paid_usd_total = 0

## Why this linked version exists

The parent v0 was PARK_DATA because its exact declared France daily ECB key returned HTTP 404 and Germany was therefore not fetched. No 2022–2025 event-window yield changes were computed in v0.

A genuinely new source fact has since appeared: Banque de France Webstat publicly catalogs a daily French constant-maturity 10-year government yield series, `FM.D.FR.EUR.FR2.BB.FRMOYTEC10.HSTA`, with daily frequency and history from November 2004; Deutsche Bundesbank publicly catalogs a daily current 10-year federal bond yield series, `BBSSY.D.REN.EUR.A630.000000WT1010.A`. This linked version changes only the source route. It does not change the mechanism, event dates, horizon, direction, costs or thresholds of v0.

During source qualification, current 2026 France TEC10 headline values and the existence/metadata of the Bundesbank series were visible. Those 2026 values are outside the frozen 2022–2025 event sample and were not used to choose the rule. No selected 2022–2025 event-window France/Germany observations were read before this declaration.

## Question

Does the exact fixed short-France / long-Germany relative-yield expression after scheduled Eurostat EDP releases exhibit material delayed spread widening over the already-declared five-common-observation horizon?

## Frozen event population

Exactly these eight scheduled EDP release dates from v0, no substitutions:

- 2022-04-22
- 2022-10-21
- 2023-04-21
- 2023-10-23
- 2024-04-22
- 2024-10-22
- 2025-04-22
- 2025-10-21

These dates remain calendar-selected, not price-selected.

## Frozen source route

France source only:
- Banque de France Webstat series `FM.D.FR.EUR.FR2.BB.FRMOYTEC10.HSTA`
- title: Taux de l'Echéance Constante - 10 ans
- daily French government constant-maturity 10-year yield
- source agency displayed by Webstat: EURONEXT

Germany source only:
- Deutsche Bundesbank series `BBSSY.D.REN.EUR.A630.000000WT1010.A`
- daily yield of the current 10-year federal bond

No third data vendor, alternate French yield series, alternate Bund maturity, futures price, ETF proxy or search-selected replacement is allowed after this declaration.

If either source cannot provide all required observations under the bounded public/no-paid route available to this research pass, verdict = `PARK_DATA`; do not substitute another series.

## Frozen sampling rule

For each event date:
1. build common dates on which both source series have a finite daily observation;
2. entry = first common daily observation strictly AFTER the release date;
3. exit = fifth subsequent common daily observation after entry;
4. entry must be within 7 calendar days of the release date;
5. exit must be within 12 calendar days of entry;
6. require all eight events or return `PARK_DATA` without an economic verdict.

Spread = France 10Y yield minus Germany 10Y yield, in basis points.
Gross payoff proxy = exit spread minus entry spread. Positive = spread widening, corresponding to the declared short-France / long-Germany relative-yield direction under idealised equal-DV01 interpretation.

No alternate entry day, close/open choice, horizon, event exclusion, sign filter or missing-data replacement.

## Costs and reporting

Exactly as v0:
- central screening friction = 2 bp round trip per event;
- stress screening friction = 4 bp round trip per event;
- central net = gross spread change - 2 bp;
- stress net = gross spread change - 4 bp.

Report exactly:
- all eight gross spread changes;
- mean, median, worst gross;
- central-net mean;
- stress-net mean;
- number gross-positive out of 8;
- calendar-year gross totals;
- break-even friction = mean gross bp;
- descriptive 95% year-block bootstrap mean, four calendar-year blocks, 2,000 draws, seed 41012.

No EUR PnL, Sharpe, CAGR, futures capacity or executable-alpha claim.

## Decision rule

`KILL_EXPRESSION` if a complete valid eight-event sample exists and either:
- mean gross <= 0; or
- central-net mean <= 0.

`PROMOTE_EXPRESSION` only if all are true:
- complete valid eight-event sample;
- central-net mean >= 3 bp;
- stress-net mean > 0;
- at least 6/8 gross spread changes are positive.

Otherwise `PARK_ECONOMICS` for a complete mixed/weak sample.

Any source/clock/sample failure before a complete eight-event sample => `PARK_DATA`.

## One adversarial check

Only if the primary result qualifies for `PROMOTE_EXPRESSION`, perform exactly one predeclared concentration check: remove the single calendar-year block with the largest positive gross year-total (earliest year breaks a tie). The remaining-event central-net mean must stay > 0. Failure downgrades to `PARK_ECONOMICS`.

No other red-team, nearby horizon or parameter search is authorized here.

## Inference ceiling

TEST_CAN_KILL = exact delayed bearish EDP expression only.
TEST_CAN_SUPPORT = `PROMOTE_EXPRESSION` only.
TEST_CANNOT_SAY = broader France crisis thesis, causal fiscal surprise, ALPHA, EDGE_VALIDATED, LIVE_READY, executable futures PnL, capacity, or prediction of French default.

The strong alternative explanation remains ordinary compensation/repricing of sovereign risk plus simultaneous euro-area/global news; EDP releases can be anticipated and the ECB backstop can suppress or reverse the expression.
