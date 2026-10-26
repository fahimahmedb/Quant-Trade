# Discovery V4.2 — US spin-off mandate-disposal prospective L1 v1

STATUS = PREDECLARED_BEFORE_PROSPECTIVE_EVENT
LABEL = EXPLORATORY_CASE_SERIES
PROSPECTIVE_T0 = 2026-10-15T13:05:00Z
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
PAID_USD_AUTHORIZED = 0

Linked route qualification: `../qualifications/us-spinoff-mandate-disposal-route-2026-10-15.json`.

## Question

For a newly distributed Nasdaq-listed spin-off child, does buying at the first regular-way close and holding through five subsequent regular-way closes earn positive benchmark-relative return after conservative fixed frictions, consistent with temporary disposal pressure from inherited/mandate-mismatched holders?

This is a prospective case screen, not proof that recipients are forced sellers and not a historical backtest.

## Mechanism

MECHANISM = a pro-rata spin-off distributes a separately traded child equity to parent holders irrespective of their standalone demand for that child. Some recipients may sell because of mandate, concentration, size, tax, operational or portfolio-preference constraints. A buyer supplying liquidity after regular-way trading begins may earn normalization if that disposal pressure exceeds fundamental repricing and costs.

WHO_PAYS = hypothesized liquidity-demanding recipients of the distributed child shares. No claim is made that every recipient sells or that the parent/issuer transfers free wealth.

WHY_PERSIST = irregular events, temporary when-issued symbols, new-listing liquidity, small capacity, mandate mismatch and operational nuisance. Public anticipation and when-issued price discovery can eliminate the effect.

MECHANISM_CLUSTER = event-driven forced/optional-flow; related to but distinct from index deletion and IPO lockup release. No multiplicity reset is claimed.

## Prospective universe and selection — frozen

Only a future public **Nasdaq Trader Equity Corporate Actions Alert** is eligible. All of the following must hold before any selected child or benchmark numeric price is read:

1. The alert page is dated **2026-10-16 or later**. The entire 2026-10-15 calendar day is excluded because the page exposes a date but not a sufficiently precise publication time relative to T0.
2. It describes a bona fide pro-rata spin-off/distribution of common equity from a parent to existing parent holders.
3. The child will be listed on Nasdaq as common stock and the alert states the child regular-way symbol and first regular-way trading date.
4. The alert states the distribution ratio and record/payment or ex-distribution dates.
5. If a when-issued child market exists, its symbol and first-trade date must be documented. No when-issued **price** is used.
6. The child is not an ETF, SPAC business-combination successor, exchange-offer consideration, tracking stock, rights distribution, preferred security, debt security or merely a name/CUSIP change.
7. The selected regular-way child symbol must be retrievable from the already-qualified Yahoo `v8/finance/chart/<symbol>` raw daily route. If retrieval fails, `PARK_DATA`; do not replace the event.
8. SPY on the same frozen Yahoo raw-daily route is the benchmark. If SPY or the exact common sessions cannot be reconstructed, `PARK_DATA`; no alternate benchmark/provider.
9. No child/benchmark numeric price, future return, analyst target, post-event performance summary or payoff may be intentionally read before the event claim is persisted.

Selection rule: select the **first chronologically dated qualifying Nasdaq Trader alert** after the date gate above. If more than one qualifying alert has the same page date, smaller numeric `ECAYYYY-NNN` alert number wins. Do not skip an unattractive, illiquid or complicated qualifying case.

Every spin-off example or alert exposed before this protocol T0 is permanently excluded, including all route-calibration/search examples observed during L0/qualification. This includes, non-exhaustively, Honeywell/Honeywell Aerospace, Middleby/Midera, Anaptys/First Tracks, ServiceMaster/frontdoor, iStar/Star Holdings, GE/GE HealthCare, Becton/Embecta, Labcorp/Fortrea, MetLife/Brighthouse, IAC/Vimeo and Toro. Historical examples may never be recycled into this prospective sample.

## Claim and clock — frozen

Before numeric prices:

- re-read fresh remote HEAD and CONTROL;
- confirm no unresolved economic look is active;
- persist and push one claim containing the exact Nasdaq alert URL/ID/date, parent, child, distribution ratio, record date, payment/ex date, when-issued symbol/date if applicable, regular-way symbol/date, and provider routes;
- a newer valid remote economic claim wins; if another look is active, do documentary work only.

`ALERT_DATE` = date printed on the qualifying Nasdaq Trader alert page.
`CLAIM_OBSERVED_AT` = actual UTC observation time recorded in the pushed claim; it is an observation receipt, not asserted as Nasdaq's first-public timestamp.
`ENTRY_SESSION` = the child’s first regular-way trading session specified by Nasdaq.

No entry is permitted on a when-issued session. No intraday timing inference is made.

## Frozen price route and event payoff

Source for both legs: Yahoo public `v8/finance/chart/<symbol>` daily chart JSON, raw `indicators.quote.close`, with exchange timezone/timestamp checked. Do not use adjusted close.

Let:
- `C0` = child raw regular-session close on `ENTRY_SESSION`;
- `B0` = SPY raw regular-session close on the same session;
- `EXIT_SESSION` = the fifth subsequent session for which **both** child and SPY have finite raw closes, and it must occur within 10 calendar days after `ENTRY_SESSION`;
- `C1`, `B1` = corresponding raw closes on `EXIT_SESSION`.

If any required close is absent or corporate-action units become ambiguous inside the holding window, `PARK_DATA`; no alternate day, source, adjusted series or replacement event.

Compute once:

`CHILD_BP = 10000 * (C1 / C0 - 1)`

`BENCHMARK_BP = 10000 * (B1 / B0 - 1)`

`GROSS_EXCESS_BP = CHILD_BP - BENCHMARK_BP`

This is a screening proxy. It is not executable paired-trade PnL and does not model beta, sector exposure or borrow on the benchmark.

## Frozen frictions and decisions

`CENTRAL_COST_BP = 50`

`STRESS_COST_BP = 100`

`CENTRAL_NET_EXCESS_BP = GROSS_EXCESS_BP - 50`

`STRESS_NET_EXCESS_BP = GROSS_EXCESS_BP - 100`

The 50/100 bp deductions are deliberately conservative exploratory round-trip frictions for a potentially illiquid newly listed child; they are not authenticated broker/exchange costs.

Per prospective case:

- `KILL_CASE` if `GROSS_EXCESS_BP <= 0` or `CENTRAL_NET_EXCESS_BP <= 0`.
- `PARK_ECONOMICS` if central is positive but `STRESS_NET_EXCESS_BP <= 0`.
- `SURVIVES_PROSPECTIVE_CASE` only if `STRESS_NET_EXCESS_BP > 0`.

A surviving case does **not** promote the family. Family-level escalation requires at least **5 qualifying prospective cases** under this unchanged v1 protocol and a separately predeclared review before aggregating them. Do not alter the horizon, benchmark, event type, listing venue or costs to accumulate five cases faster.

## Single adversarial check

The only predeclared adversarial economic check is the `STRESS_COST_BP = 100` path above. No second horizon, entry at open, when-issued entry, sector benchmark, factor regression, outlier deletion or nearby friction grid is authorized after outcome access.

## Required case output

Persist immediately after the one allowed computation:

- alert ID/date and claim commit;
- parent/child/ticker and distribution ratio;
- record/payment/ex/when-issued/regular-way dates;
- entry/exit session;
- C0, C1, B0, B1;
- child bp, benchmark bp, gross excess bp;
- central/stress net excess bp;
- typed case verdict;
- uncertainty and failed criteria;
- explicit statement that when-issued prices and actual holder flows were not used.

Release the economic claim after the result is durably pushed.

## Bias and alternative explanations

- Distribution creates ownership, not compulsory selling; actual holder flow is unobserved.
- The child may have distinct fundamental news, leverage, sector beta or valuation changes during the five-session window.
- When-issued trading can price expected selling before regular-way entry, making the test conservative for a transient-dislocation hypothesis.
- First regular-way close is an index-like observable proxy, not proof of an executable fill for a small account.
- SPY is a coarse market benchmark and does not neutralize sector/factor exposures.
- One case is anecdotal evidence only; five prospective cases remain a very small exploratory sample.

## Inference rights

TEST_CAN_KILL = one exact prospective case under this fixed expression.
TEST_CAN_SUPPORT = one case survives a 100 bp benchmark-relative stress deduction and is worth continued prospective incubation.
TEST_CANNOT_SAY = ALPHA, EDGE_VALIDATED, FORCED_SELLING_CAUSALITY, EXECUTABLE_PAIRED_PNL, CAPACITY, TAX BENEFIT, BROKER ELIGIBILITY, LIVE_READY or REAL_CAPITAL_READINESS.

No historical backfill, no post-outcome retuning, no paid data, no live order and no capital authorization are permitted.
