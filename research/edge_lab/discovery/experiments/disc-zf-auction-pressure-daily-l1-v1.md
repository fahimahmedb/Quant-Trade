# V4.2 executable declaration — U.S. 5Y Treasury auction daily pressure/reversal proxy

`EXPERIMENT_ID = disc-zf-auction-pressure-daily-l1-v1`

`PARENT = disc-zf-auction-pressure-v0`

`STATUS = PREDECLARED_BEFORE_5Y_OUTCOME_ACCESS`

`LEVEL = L1`

`LIVE_CAPITAL = FORBIDDEN`

## 1. Research decision

Decide whether the Treasury-auction inventory-pressure mechanism is visible at a deliberately coarse daily level strongly enough to justify later ZF intraday/futures reconstruction.

This is not a novelty claim. Prior exposure is explicit: Federal Reserve Bank of New York Staff Report 1188 (2026) reports intraday Treasury yields rising before auctions and reversing afterward, with dealer constraints/order flow as mechanisms. This experiment asks only whether a cheap official daily proxy preserves enough of that temporal signature to justify more expensive work.

## 2. Event population — frozen before market outcomes

Official source: U.S. Treasury FiscalData `Treasury Securities Auctions Data` / `auctions_query` API.

Population rule:
- `security_type = Note`;
- `security_term = 5-Year` / equivalent exact 5-year nominal-note label returned by the official dataset;
- `auction_date` from 2023-01-01 through 2026-09-30 inclusive;
- include every qualifying original issue and reopening returned by the mechanical filter;
- exclude TIPS/FRN/bills/bonds and non-5Y terms by source fields only;
- no event may be included/excluded because of a realized rate move, bid-to-cover, dealer share, tail, or remembered market reaction.

Auction metadata fields may be retained descriptively, but no threshold on bid-to-cover/dealer share/tail is searched in this L1.

## 3. Market proxy — frozen

Official source: U.S. Department of the Treasury `Daily Treasury Par Yield Curve Rates`, 5-year maturity.

The Treasury states these par yields are derived from market input/closing bid-side information and are not actual transaction fills. The 5Y daily series is therefore a coarse public rate proxy, not ZF executable P&L.

Sample interval for rates: enough official daily observations to form all frozen event and placebo windows for auctions dated 2023-01-01..2026-09-30. No other maturity or market series may replace the 5Y after outcomes are seen.

## 4. Exact temporal rule — frozen

For each auction date `A`, using only available official 5Y daily observations:

- `PRE1` = most recent observation date strictly before `A`;
- `PRE2` = second most recent observation date strictly before `A`;
- `PRE3` = third most recent observation date strictly before `A`;
- `POST1` = first observation date strictly after `A`;
- the auction-date observation itself is never used because the Treasury daily fixing can occur after the auction and can mix pre- and post-auction dynamics.

Define, in basis points:

- `CONCESSION_BP = (Y_PRE1 - Y_PRE3) * 100`; expected sign `> 0`;
- `RELIEF_BP = (Y_POST1 - Y_PRE1) * 100`; expected sign `< 0`;
- `PATTERN_BP = CONCESSION_BP - RELIEF_BP`; larger positive values mean stronger pre-auction rise plus post-auction reversal.

No alternative window, maturity, auction-day fixing, smoothing, threshold, or subperiod is searched after outcome access. Any such change is a new linked experiment.

## 5. Mechanism contract

`MECHANISM` — auction supply and dealer/inventory constraints can create temporary pre-auction price pressure that partially reverses after the auction.

`WHO_PAYS` — dealers/intermediaries and market participants absorbing auction supply under finite risk-bearing capacity.

`WHY_PERSIST` — balance-sheet, inventory, mandate and immediacy constraints; however public knowledge and risk compensation can limit exploitable alpha.

`PRIMARY_SIGNATURE` — the same auctions should show both a positive pre-auction yield concession and a negative post-auction yield change under the fixed daily windows, not merely a positive average yield move.

`ALTERNATIVE_EXPLANATION` — generic weekly/month-end/calendar rate drift or macro-news clustering rather than auction-specific pressure.

## 6. Adequacy gate — frozen

The expression is interpretable only if:

1. at least 40 qualifying auction events are returned by the official event source;
2. at least 90% of all mechanically qualifying auctions have complete PRE3/PRE2/PRE1/POST1 5Y observations;
3. no event is excluded because of realized market outcome;
4. all rate observations come from the same official Treasury daily 5Y series;
5. no single calendar year contributes more than 50% of the sum of absolute `PATTERN_BP` among complete events.

Failures of 1–4 => `INCONCLUSIVE` or `PARK_DATA` as appropriate. Failure of 5 prevents strong promotion and triggers concentration labeling; it does not erase raw results.

## 7. Fixed Discovery hurdle

Before outcomes, the expression is defined as economically interesting enough for L2 only if ALL are true across complete auctions:

- median `CONCESSION_BP >= +1.0 bp`;
- median `RELIEF_BP <= -0.5 bp`;
- share with `CONCESSION_BP > 0` >= 55%;
- share with `RELIEF_BP < 0` >= 55%;
- mean `PATTERN_BP > 0`;
- adequacy gate passes.

Decision map:
- both median legs opposite the hypothesized signs, or `PATTERN_BP` mean <= 0 with adequate data => `KILL_EXPRESSION`;
- correct-sign but below the hurdle => `PARK_ECONOMICS`;
- full hurdle passes => at most `PROMOTE_EXPRESSION` before the red-team;
- data inadequacy => `INCONCLUSIVE`/`PARK_DATA`, never a mechanism kill.

These thresholds are Discovery hurdles, not significance tests.

## 8. Inference rights

### TEST_CAN_KILL
Only this exact daily 5Y par-yield expression over the frozen 2023-01-01..2026-09-30 5-Year Note auction population.

### TEST_CAN_SUPPORT
A hurdle-passing temporal pattern can justify L2 work with intraday Treasury/ZF data, auction timing, roll rules and executable prices.

### TEST_CANNOT_SAY
This L1 cannot establish:
- executable ZF alpha or P&L;
- when-issued/tail economics;
- BBO/fills/slippage/market impact;
- exact intraday auction reaction;
- causality independent of macro announcements;
- current live profitability;
- capacity/margin/capital requirements;
- novelty, because the mechanism is already documented in public literature.

## 9. Bias map

- Timing: strongly coarse; skipping the auction-day fixing can dilute a fast intraday effect.
- Price quality: Treasury par yields are indicative/curve measures from market quotes, not fills.
- Amplitude: likely downward for short-lived pressure but may mix unrelated moves over multi-day PRE3→PRE1 windows.
- Costs/execution: completely unmodeled at L1; no tradable return claim.
- Publication/selection: event population is mechanical and official; low selection bias if API completeness passes.
- Prior literature: high contamination of novelty; only replication/decision value is claimed.

## 10. Unit-economics envelope

Do not translate this proxy into ZF dollars before promotion. A median 1bp pre-auction concession plus at least 0.5bp median relief is used as a coarse minimum headroom requirement before paying the cost of futures-level DV01/roll/BBO reconstruction.

Because auctions occur roughly monthly, an effect that is materially smaller than these hurdles is unlikely to justify heavy engineering for a small-capital strategy under the current objective.

## 11. One cheap red-team if primary hurdle passes

`RED_TEAM = CALENDAR_PLACEBO_MINUS_7D`

For every complete auction event, define placebo date `P = auction_date - 7 calendar days` and compute the same strict-before/strict-after 5Y windows around `P`:
- placebo PRE1/PRE2/PRE3 = three most recent observations strictly before `P`;
- placebo POST1 = first observation strictly after `P`;
- `PB_CONCESSION_BP`, `PB_RELIEF_BP`, `PB_PATTERN_BP` use identical formulas.

No alternative placebo offset is allowed.

Red-team passes only if:
- median actual-auction `PATTERN_BP` > median placebo `PB_PATTERN_BP`; AND
- the primary actual-auction hurdle remains satisfied.

Failing the placebo means at most `PARK_ECONOMICS` / no promotion; no further placebo search.

## 12. Prior exposure / multiplicity

Prior public exposure: NY Fed Staff Report 1188, 2026, explicitly reports the intraday pressure/reversal pattern. Existing `treasury-auction-zf` family was previously parked because full BBO/roll data were costly; no claim of a virgin mechanism is made.

This is one new linked expression/look in the existing mechanism cluster, not an independent discovery.

## 13. Resource and rights boundary

- public official sources only;
- paid USD = 0;
- no account/API key;
- no redistribution of raw third-party proprietary data;
- no real/live capital;
- one execution, no replay after realized outcomes;
- no architecture work if either official source is unavailable.

## 14. Execution authorization boundary

This declaration authorizes **no 5Y market-outcome access until committed remotely**. After remote publication, a distinct claim artifact/CAS receipt must be committed before retrieving/joining the official Treasury daily 5Y rates. Auction metadata may then be retrieved under the frozen mechanical population rule. One outcome execution only.
