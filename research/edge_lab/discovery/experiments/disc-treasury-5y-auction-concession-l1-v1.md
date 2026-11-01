# Discovery V4.2 — U.S. Treasury 5Y auction concession/reversal L1 v1

STATUS = PREDECLARED_BEFORE_EVENT_JOIN_AND_PAYOFF_ACCESS
LABEL = EXPLORATORY
PARENT_FAMILY = `treasury-auction-zf`
SOURCE_QUALIFICATION = `../qualifications/treasury-auction-5y-public-proxy-l0-2026-10-14.json`
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
paid_usd_total = 0

## Decision question

Before paying the cost of ZF futures/BBO/roll reconstruction, does a coarse official-data proxy show a repeated next-day reversal after regular nominal 5-year Treasury note auctions that is large enough to justify deeper execution work?

## Mechanism

MECHANISM = concentrated 5-year duration supply and dealer/balance-sheet demand around the auction may create a temporary yield concession that partially reverses after the auction.
WHO_PAYS = participants demanding immediate balance-sheet/liquidity around primary issuance; ordinary macro-rate risk is a strong alternative explanation.
WHY_PERSIST = mechanical recurring supply, dealer intermediation and balance-sheet constraints can recur, but the effect may be crowded, tiny or fully absorbed intraday.

This L1 tests only a coarse daily expression. It does not identify auction-tail alpha or an executable futures strategy.

## Frozen population

Calendar window is fixed before event/yield joining:

`2024-01-01 <= AUCTION_DATE <= 2025-12-31`

Include every record satisfying all of:

1. U.S. Treasury Fiscal Data `auctions_query`;
2. `security_type = Note`;
3. `original_security_term = 5-Year` (or, if that field is absent in the returned schema, `security_term = 5-Year` only if the API itself shows the record as the regular five-year note; no manual substitution);
4. nominal/non-inflation-indexed;
5. non-floating-rate;
6. auction actually held in the fixed window.

Treasury describes 5-year notes as auctioned monthly. Adequacy therefore requires exactly one eligible auction in each calendar month of 2024 and 2025: 24 events total. If the official API/schema does not mechanically produce exactly 24 eligible monthly events, return `PARK_DATA` before computing an economic verdict. Do not repair the population by hand or drop a month.

No selection by auction yield, bid-to-cover, tail, dealer share, macro regime or subsequent market move.

## Frozen market proxy

Only the U.S. Treasury `Daily Treasury Par Yield Curve Rates`, 5-year nominal column, is allowed.

For each eligible auction:

- `ENTRY_DATE = AUCTION_DATE` and must have a finite official 5Y par-yield observation;
- `ENTRY_YIELD = official 5Y par yield on AUCTION_DATE`;
- `EXIT_DATE = first subsequent date with a finite official 5Y par-yield observation`;
- `EXIT_YIELD = official 5Y par yield on EXIT_DATE`;
- `GROSS_BP = 100 * (ENTRY_YIELD - EXIT_YIELD)` because source yields are percentage points.

Positive `GROSS_BP` means yields fell after the auction, consistent with a one-day long-duration reversal after an auction-date concession.

The exit must be within 4 calendar days of auction date. Missing entry or no subsequent observation within 4 calendar days => `PARK_DATA` for the entire test; no event deletion or alternate source.

No pre-auction close, intraday time, two-day horizon, auction high yield, WI yield, futures price, alternate maturity or nearby window may be inspected as a variant in this test.

## Screening frictions

These are deliberately coarse yield-space hurdles, not authenticated trading costs:

- `CENTRAL_COST_BP = 1.0` per event;
- `STRESS_COST_BP = 2.0` per event;
- `CENTRAL_NET_BP = GROSS_BP - 1.0`;
- `STRESS_NET_BP = GROSS_BP - 2.0`.

No DV01/EUR/USD PnL, leverage, margin, roll, carry, CTD, bid/ask or fill claim is permitted.

## Required outputs

For the complete 24-event sample report exactly:

- chronological auction date, entry date, exit date and `GROSS_BP` for all 24 events;
- mean and median `GROSS_BP`;
- worst `GROSS_BP`;
- mean `CENTRAL_NET_BP`;
- mean `STRESS_NET_BP`;
- count of positive `GROSS_BP` events;
- 2024 and 2025 year totals separately;
- break-even hurdle = mean gross bp;
- descriptive two-year block bootstrap of the mean: 2,000 draws, seed 41013, resampling the two calendar-year blocks. This interval is descriptive only and must not be presented as confirmatory significance.

## Primary decision rule

With a complete valid 24-event sample:

- `KILL_EXPRESSION` if mean gross <= 0 OR mean central-net <= 0.
- `PROMOTE_EXPRESSION` only if ALL are true:
  - mean gross >= 2.0 bp;
  - mean stress-net > 0;
  - at least 15 of 24 events have positive gross bp.
- otherwise `PARK_ECONOMICS`.

If adequacy/source requirements fail: `PARK_DATA`, with no economic verdict.

## Single predeclared adversarial check

Run only if the primary rule would yield `PROMOTE_EXPRESSION`.

Remove exactly the single event with the largest positive `GROSS_BP`; earliest auction date breaks a tie. Recompute the remaining-event mean central-net. It must remain > 0. If not, downgrade to `PARK_ECONOMICS`.

No other event removal, horizon search, regime split, threshold search or parameter tuning is authorized.

## Bias / alternative explanations

- Daily par-yield curve values are official curve estimates, not executable auction-time or futures fills.
- Auction date end-of-day yield may already contain the auction result and unrelated same-day news.
- Next-day changes can be dominated by CPI, payrolls, FOMC, geopolitical or risk-off moves.
- The fixed 2024–2025 sample spans only two years and events are dependent through rate regimes.
- A positive result may be compensation for duration/liquidity risk or chance, not mispricing.
- Generic Treasury daily-rate rows were incidentally visible during source qualification before this contract; no auction dates had been joined to them and no event-window statistic was computed. No pristine-data claim is made.

## Inference rights

TEST_CAN_KILL = this exact coarse one-day 5Y auction-reversal expression.
TEST_CAN_SUPPORT = `PROMOTE_EXPRESSION`, meaning only that ZF-level execution reconstruction may be worth the cost.
TEST_CANNOT_SAY = ALPHA, EDGE_VALIDATED, LIVE_READY, EXECUTABLE_PNL, AUCTION_TAIL_ALPHA, CAUSAL_DEALER_PRESSURE, CAPACITY, SHARPE, OR REAL_CAPITAL_READINESS.

Any promotion must be followed by one separate strict execution/capturability design; it must not trigger a nearby historical parameter search.
