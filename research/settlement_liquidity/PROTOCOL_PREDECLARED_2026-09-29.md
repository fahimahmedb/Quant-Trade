# S2 settlement-liquidity falsification — PREDECLARED PROTOCOL (frozen before economics)

REAL_CAPITAL_AUTHORIZED = FALSE. Research only. No orders are placed, signed or cancelled by any script.

Frozen at commit time of this file (git timestamp = pre-registration). At freeze time **no fill, payout,
P&L or post-determination trade of the 30-day window had been examined**. Only market metadata
(question, category, sportsMarketType, resolution-source text, counts) and external game timelines were
inspected. Any later deviation is listed in the report under "Protocol deviations" with its reason.

## 1. Question

After mechanically proving (public, timestamped, authoritative source) that the economic event is
determined but the Polymarket contract is not yet resolved, can a **new small participant** earn positive
net value by supplying liquidity at/near the 0.999 tick floor, after resolution delay, disputes, reversals,
false determination, queue position, fill probability, opportunity cost, fees and capital lock?

Target object: **POST-DETERMINATION / PRE-RESOLUTION liquidity**, not all ≥0.999 buys.

## 2. Window, universe, exclusions

- PRIMARY window: markets with gamma `closedTime` in **[2026-08-30T00:00Z, 2026-09-29T00:00Z)** = 30 complete
  UTC days ending 2026-09-28 (2026-09-29 was incomplete at run time).
- Optional SECONDARY window (replication only, never merged into the decision): [2026-07-31, 2026-08-30).
- Universe: every closed market returned by gamma `/markets/keyset` with `volumeNum ≥ 1,000` USDC.
- Outcome-blind exclusions (`scripts/s02_classify.py`, regexes frozen here):
  - E1_UPDOWN: any "Up or Down" market, any asset or horizon.
  - E2_ASSET_PRICE: asset-price threshold / range / hit markets on crypto, equities, indices, commodities, FX
    (latency-driven family). Counted, not analysed.
- No market is ever dropped because of its outcome, P&L or dispute state.

## 3. T_DETERMINED (mechanical, public, timestamped, authoritative)

Placement latency for the newcomer: **L = 60 s** after T_DET (sensitivity L = 0 s and 300 s).
T_RESOLUTION = gamma `closedTime`. SETTLEMENT_WINDOW W = [T_DET, T_RES). If T_RES ≤ T_DET the market stays in
the cohort with an empty window (zero opportunity).

| Family | Source | T_DET rule |
|---|---|---|
| MLB | statsapi.mlb.com live feed (official MLB) | full-game markets: `endTime` of the last play, status Final. NRFI: min(end of first 1st-inning scoring play, end of 1st inning). First-five markets: end of 5th inning (max of 5T/5B half ends). Player props: game over (conservative). Cancelled/suspended/postponed → UNVERIFIABLE |
| ESPN football (NFL, NCAAF FBS/FCS) | site.api.espn.com play-by-play `wallclock` | full game: 'End of Game' play (after OT). First-half markets: 'End of Half'. Q1 markets: 'End Period' of period 1. Missing play → UNVERIFIABLE |
| ESPN basketball / hockey | idem | full game: 'End Game' play. Other partial-game markets → full-game time (conservative) |
| ESPN soccer (any league whose summary publishes timestamped terminal key events) | idem | full-time (regular-time) markets: 'end-regular-time' wallclock; if the match had extra time/shootout and the market text does not restrict to regular time (90 minutes / regular time / regulation): last terminal event. First-half markets: 'halftime'. No timestamped terminal event → UNVERIFIABLE |
| Weather (NOAA/NWS timeseries or WU, both METAR-based) | METAR archive (IEM ASOS), station from the market's resolution URL | T_DET = valid time of the first METAR after local midnight ending the observation date ("resolves once the first data point for the following date is published"). Verified only if the METAR-derived daily extreme is unambiguous w.r.t. the bracket (°C whole-degree data: exact; °F: ≥ 1.0 °F from every bracket edge). HKO-resolved → UNVERIFIABLE |
| Everything else (esports, tennis, UFC, F1, cricket, golf, lower-tier soccer without timestamped final, politics, culture, mentions, tweet counts, economics, weather with ambiguity) | — | **DETERMINATION_UNVERIFIABLE** → excluded from the primary causal cohort before economics; counted |

Matching ESPN ↔ Polymarket: |kickoff difference| ≤ 20 min and team-name similarity ≥ 1.5 / 2.
Market-type → partial-game rules by `sportsMarketType` tokens (first_half / halftime / q1 / nrfi /
first_five); every other type uses the full-game time (a later T_DET only shrinks windows, never adds
in-play risk). Polymarket's own `finishedTimestamp` (venue feed) is **not** a primary authority; it is used
only (a) to report agreement with the independent source and (b) in a clearly labelled SECONDARY sensitivity
cohort for families without an independent source.

## 4. Fill accounting (rejection rule 1)

- Trades: data-api `/trades?market=<conditionId>` with `takerOnly=false` (maker + taker records) and
  `takerOnly=true` (taker records); maker records = multiset difference on
  (tx, wallet, side, asset, price, size, timestamp). Coverage flag if the 11,000-record API cap prevents
  reaching T_DET.
- Qualifying fill: every **BUY** record (maker or taker, either outcome token) with price ≥ 0.998 and
  timestamp in W. Reported pooled (≥0.998) and separately at 0.998 and 0.999. Markets whose tick is 0.01
  report their floor level (0.99) separately (not in the ≥0.998 pool).
- Per fill: payout (final `outcomePrices`), entry price, fee (taker only: size × rate × (p(1−p))^exponent
  from the market `feeSchedule`; makers 0; rebates ignored), net cash P&L = size × (payout − price) − fee,
  capital locked = size × price + fee, lock duration = T_RES − t_fill, annualized return (descriptive only),
  dispute count (`disputed` entries in `umaResolutionStatuses`), reversal / false-determination flag
  (source-derived outcome ≠ final payout, for types whose outcome is computable from the source).
- **Every losing fill is kept.** Primary statistic: Σ net cash P&L over all qualifying fills of the primary
  cohort; also per-notional return with market-cluster bootstrap CI (descriptive).
- REJECTED_NET if primary Σ net ≤ 0.

## 5. Newcomer access (rejection rule 2)

Exact FIFO queue reconstruction is **impossible**: Polymarket publishes no historical L2 book or order
placement times. A partial-identification bound is used.

- Side X: the source-derived winning side where computable (moneyline/draw, spreads, totals, team totals,
  BTTS, exact score, halftime/first-half results, weather brackets); otherwise the side whose last trade
  before placement priced X ≥ 0.99 (market consensus, flagged); otherwise no bid.
- Bid: resting BUY X at 0.999 (1 − tick), placed at t_p = T_DET + L, alive until T_RES.
- Winning-equivalent price of a record: p on X, 1 − p on not-X.
- F999(t): taker records after t that sell X at 0.999 or buy not-X at 0.001 (they hit the X 0.999 bid level).
- Fsub(t): taker records after t with winning-equivalent price ≤ 0.998. **Identification:** by price
  priority, such a trade can only occur when the X 0.999 bid level is empty, so a resting newcomer bid would
  have been first in queue and filled (at 0.999, or better if it crossed a resting ask on arrival).
- Fill models for order size S (chronological, capped at S):
  - **LB (strict conservative)**: back of an unobserved queue, no credit for cancellations ahead, no 0.999
    flow: fill = min(S, Fsub(t_p)).
  - **UB**: first in queue at t_p: fill = min(S, F999(t_p) + Fsub(t_p)).
  - **CENTRAL**: LB + F999(t_p)/(k+1), k = distinct maker wallets filled at X-0.999 after t_p (equal share
    with active competitors); replaced by the live-calibrated queue ratio if S8 yields ≥ 20 post-final
    markets.
- NEWCOMER_FILL_SHARE = Σ fills / Σ posted size over all eligible primary markets at reference size
  S_ref = 100 USDC per market (no capital constraint). Also reported: fill probability (share of eligible
  markets with any fill), flow share, eligible time, F999, Fsub, k.
- Live check (S8, read-only): public CLOB `/book` snapshots of markets already final but unresolved, depth
  at X-0.999 (X bids at 0.999 + not-X asks at 0.001) at t_p, subsequent taker flow; conservative FIFO fill
  (no cancellation credit) and optimistic (cancellations ahead credited).
- Decision on access: LB share ≥ 5% → access passes. LB < 5% and (UB < 5% or live conservative < 5% on
  ≥ 20 markets) → REJECTED_FILL_ACCESS. LB < 5% ≤ UB with live conservative ≥ 5% or live sample < 20
  markets → INDETERMINATE_QUEUE.

## 6. Capital economics

EUR 100 / 500 / 1,000 / 5,000 (converted at the ECB EUR/USD reference rate of 2026-09-28, or stated
fallback). Chronological simulation over the 30 days; no leverage; a resting bid reserves S × 0.999 from
t_p until T_RES (unfilled remainder released at T_RES; filled part redeemed at T_RES); order size
S = min(free capital, 25% of capital) (sensitivity 100%); fills per LB / CENTRAL / UB; losses at payout.
Reported: monthly net EUR, return on capital, utilization, number of fills, worst loss.
OPPORTUNITY_RATE_TOO_LOW flag if CENTRAL monthly net at EUR 1,000 < EUR 10.

## 7. Decay / persistence

Weekly (and secondary window if run): opportunities, median lock, gross tick premium, disputes, distinct
competing buyers/makers, LB/UB newcomer capacity. Persistence attributed to information error vs
liquidity/time-value/operational friction using: loss rate after T_DET, premium fixed at the tick,
lock-time dependence, seller composition.

## 8. Terminal state (exactly one)

1. If fewer than 30 primary markets have a non-empty W with any qualifying fill → INDETERMINATE_DETERMINATION.
2. net ≤ 0 and access rejected → REJECTED_BOTH; net ≤ 0 only → REJECTED_NET; access rejected only →
   REJECTED_FILL_ACCESS; access INDETERMINATE_QUEUE (and net > 0) → INDETERMINATE_QUEUE.
3. Otherwise SURVIVES_FALSIFICATION (not validation; authorizes nothing).
