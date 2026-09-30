# S2 SETTLEMENT LIQUIDITY — 30-DAY FALSIFICATION (post-determination / pre-resolution)

REAL_CAPITAL_AUTHORIZED = FALSE. Research only. No orders were placed, signed or cancelled; every data source is
public and read-only.

Branch `claude/hopeful-dirac-4ahy2z` (harness-assigned; the only branch used). Pre-registration:
`PROTOCOL_PREDECLARED_2026-09-29.md` (commit `4433a24`, frozen before any fill or payout of the window was
examined). Resume/state file: `SETTLEMENT_LIQUIDITY_STATE_2026-09-30.md`.

```text
SETTLEMENT_LIQUIDITY_S2 = REJECTED_FILL_ACCESS
```

Rule 1 (net) passes; rule 2 (newcomer fill access) fails on both the historical strict bound (3.23 %) and the live
conservative queue check (1.23 % on 273 timed post-final markets, 7 games). Nothing here authorizes capital.

## 1. Answer

The post-determination 0.999 trade is real and clean in aggregate. Once an independent public source has
timestamped the event as decided, every buy at ≥ 0.998 before resolution earned **+0.1003 %** net on 55.6 M$
(September; August replication +0.1003 % on 32.3 M$), with only 6 losing fills, all in disputed markets. Agent 7's
negative pooled result was an in-play artefact.

It is **not an accessible small-player premium**:

1. **Queue.** The floor is already occupied. In the median market one incumbent maker absorbs 100 % of the floor
   flow. Live snapshots at the final whistle show 0.999 queues of 10⁴–2.6 × 10⁵ shares against 10¹–10⁴ shares of
   later flow. Newcomer fill share: strict lower bound 3.23 %, live conservative 1.23 %; the pre-declared threshold
   is 5 %.
2. **Adverse selection.** A newcomer that follows the source side gets about 3 % of its bid filled when it is
   right. When it is wrong (0.07 % of markets: METAR vs NOAA, shootout conventions, stale consensus, disputes),
   every holder of the losing token sells to it, so it is filled 100 %. Under the frozen side rule that means ruin
   at every capital level.

With a source-and-consensus guard (sensitivity S1) the expected value is about zero: at EUR 1,000, +10 to +14 EUR
per 30 days before an expected tail of about −29 EUR per month.

The premium persists because it pays for liquidity and time value, floored by the 0.001 tick. It does not come
from information error. Competition shows up as queue concentration, not as a lower price.

## 2. Key numbers (primary window: markets closed 2026-08-30 → 2026-09-28, 30 complete UTC days)

| Quantity | Value |
|---|---|
| Markets enumerated (closed, volume ≥ 1 k$) | 115,574 |
| Excluded outcome-blind: Up-or-Down (E1) / asset-price thresholds (E2) | 31,466 / 4,519 |
| Kept | 79,589 (3.69 bn$ lifetime volume) |
| **T_DETERMINED verified** from an independent public timestamped source | **36,982** (1.42 bn$); 42,607 DETERMINATION_UNVERIFIABLE (excluded before economics) |
| Verified with a non-empty settlement window [T_DET, T_RES) | 36,079 |
| **Primary cohort N** (verified markets with ≥ 1 qualifying buy in the window) | **13,371 markets / 119,737 fills** |
| Qualifying notional (BUY ≥ 0.998 in the window, maker + taker) | 55.62 M$ |
| **Net cash P&L, all qualifying fills, after losses and fees** | **+55,810 $ = +0.1003 %** (market-cluster bootstrap 95 % CI 0.1002–0.1005 %) |
| **Losing fills** | **6 fills in 3 markets, −27 $** (all in disputed markets) |
| Median / p90 / notional-weighted capital lock | **0.42 h** / 2.08 h / 0.76 h |
| Verified markets disputed / disputed with fills | 21 / 9 |
| False determination (source side ≠ final payout) | 21 / 28,884 source-determined markets (0.073 %) |
| **Newcomer fill share** (S = 100 $/market; frozen side rule; LB / CENTRAL-live / UB) | **3.23 % / 4.90 % / 26.78 %** |
| Live conservative fill share (273 timed post-final markets, 7 games) | **1.23 %** (main markets 1.26 %) |
| **EUR 1,000 per 30 d** — frozen rule (LB / CENTRAL / UB) | **−1,000 / −1,000 / −1,000 (ruin)** |
| EUR 1,000 per 30 d — S1 guard (LB / CENTRAL / UB) | +9.8 / +14.3 / +117.4 (path-lucky; expected tail ≈ −29 EUR/month) |
| Secondary window (Aug; MLB + soccer + weather) | +0.1003 % on 32.34 M$, 1 losing fill (−2 $), median lock 0.74 h |

## 3. Design (pre-declared) and deviations

- **Universe**: every closed gamma market with `closedTime` in the window and `volumeNum ≥ 1,000`. No market was
  dropped for its outcome, P&L or dispute state.
- **T_DETERMINED** (protocol §3): the official MLB live feed (`endTime` of the last play; NRFI, first-five and
  inning markets use the inning boundaries). ESPN play-by-play `wallclock` for NFL, NCAAF, WNBA, NHL and every soccer
  league whose summary publishes timestamped terminal events. The METAR archive (IEM) for NOAA- and WU-resolved
  temperature markets (first observation of the next local day; °F markets only when ≥ 1 °F from every bracket
  edge). Esports, tennis, UFC, F1, cricket, lower-tier soccer without a timestamped final whistle, politics, culture,
  mentions, tweets and economics are DETERMINATION_UNVERIFIABLE.
- **T_RESOLUTION** = gamma `closedTime`. W = [T_DET, T_RES).
- **Validation**: the independent source precedes Polymarket's own venue feed (`finishedTimestamp`) by a median of
  62–102 s in every sports family (MLB 83 s, NFL/NCAAF 95 s, soccer 81 s, WNBA 62 s, NHL 102 s). The 5–95 %
  range is about −9 min to +1 min. The venue feed was never used as authority.
- **Deviations** (disclosed; generic rules, no per-market overrides):
  - **D1** — MLB doubleheaders: statsapi lists game 2 at a placeholder start, so ties are broken by the closest
    start.
  - **D2** — team→outcome mapping must be unique and one-to-one ("Utah"/"Utah State", "NYCFC"/"NY Red Bulls",
    "Real Madrid"/"Rayo Vallecano de Madrid").
  - **D3** — same-sport candidates only, and no city-only or abbreviation name variants. This removed 3 CFB↔college
    soccer pairings historically and 404 cross-sport live pairings (for example MLB BOS@NYY ↔ NHL NYR@BOS).
  - D1 and D2 were found by classifier QA before any newcomer result existed. D3 was found from the live monitor.
    The as-frozen determination is kept in `data/determination_primary_asfrozen.csv.gz` (35 disagreements → 21
    after the fixes). Rule-1 figures are unchanged by D3 (same 119,737 fills).
  - The live monitor needed operational fixes (closed-market query, game-start filter, tracking from game start,
    unified-book depth).

## 4. Cohort and determination (primary)

| Family | Verified | Window > 0 | Median window | Source |
|---|---|---|---|---|
| Soccer, ESPN leagues | 13,536 | 13,536 | 0.60 h | ESPN keyEvents wallclock |
| Soccer, other series matched to ESPN | 4,438 | 4,438 | 2.07 h | idem |
| Weather (51 stations) | 10,643 | 10,639 | 0.43 h | IEM METAR |
| MLB | 4,115 | 3,514 | 0.32 h (props often resolve mid-game) | statsapi.mlb.com |
| NFL / NCAAF | 3,885 | 3,592 | 0.43 h | ESPN plays wallclock |
| WNBA / NHL | 262 / 103 | 262 / 98 | 0.53 h / 0.35 h | idem |

Unverifiable markets: no independent source 26,402; ESPN summary without a terminal timestamp 8,098; non-sports
6,101; weather rounding, HKO and midnight-extreme 1,507; other 499.

False determination: 21 of 28,884 source-determined markets disagree with the payout. 18 are weather (METAR proxy
vs NOAA timeseries, mostly daily lows) and 3 are NHL preseason (shootout-goal convention; 2 disputed). These are real
classifier risk and are kept.

## 5. Rejection rule 1 — every qualifying fill

All BUY records (maker and taker, either token) at ≥ 0.998 inside [T_DET, T_RES). Payout comes from the final
`outcomePrices`. Taker fee = size × rate × (p(1−p))^exponent; makers pay 0; rebates are ignored.

| Slice | Fills | Markets | Notional $ | Net $ | Net / notional | Losing fills |
|---|---|---|---|---|---|---|
| **All ≥ 0.998** | 119,737 | 13,371 | 55,624,499 | **+55,810** | **+0.1003 %** | 6 |
| at 0.999 (tick floor) | 118,301 | 13,310 | 55,022,324 | +55,011 | +0.1000 % | 6 |
| at 0.998 | 486 | 172 | 56,262 | +110 | +0.195 % | 0 |
| makers only | 113,453 | 12,495 | 54,164,825 | +54,229 | +0.1001 % | 2 |
| takers only (fees 75 $) | 6,284 | 2,087 | 1,459,674 | +1,581 | +0.108 % | 4 |
| ESPN families | 66,356 | 8,033 | 39,889,109 | +39,982 | +0.1002 % | 0 |
| MLB | 23,848 | 1,661 | 6,576,480 | +6,649 | +0.1011 % | 2 |
| Other soccer (ESPN-matched) | 22,225 | 2,618 | 8,795,419 | +8,793 | +0.1000 % | 4 |
| Weather | 7,308 | 1,059 | 363,490 | +386 | +0.106 % | 0 |

The complete list of losing fills:

- 4 fills (−22 $) on "Will Oliver Nielsen be in Denmark's Starting 11?". NO was bought at 0.999 after the match; the
  market resolved YES after 2 disputes.
- 2 fills (−5 $) on MLB "Jared Jones: Strikeouts O/U" (two lines). Both were voided to 50/50 after 2 disputes.

No game result reversed.

**In-play contrast.** The same buys in [T_DET − 2 h, T_DET): 48,517 fills, 31.70 M$, +0.063 % (95 % CI −0.005 % …
+0.103 %), with 30 losing fills in 14 markets (−13.6 k$). The losses are an in-play phenomenon.

Per-fill simple annualized return has a median of 2,099 %. It is descriptive only, because capital utilization binds.

**Rule 1: net = +55,810 $ > 0 → not rejected on net.**

## 6. Rejection rule 2 — newcomer access

### 6.1 Identification

Exact FIFO reconstruction is **impossible**. Polymarket publishes no historical L2 book and no order-placement
times, and the Goldsky order-book subgraph is deprecated. A partial-identification bound is used instead (protocol §5).

- The newcomer rests a BUY on side X at 0.999 from t_p = T_DET + 60 s to T_RES. X is the source side, or else the
  last-trade consensus.
- **LB (identified):** a taker trade after t_p at a winning-equivalent price ≤ 0.998 can only print when the X
  0.999 bid level is empty (price priority; mirrored YES/NO book). A resting newcomer would therefore have been first
  in queue. LB counts that flow only.
- **UB:** the newcomer is first in queue at t_p.
- **CENTRAL (protocol):** LB + floor hits × r. r is calibrated live because the live sample reached ≥ 20 markets:
  r = 0.28 %, the share of post-t_p floor hits a back-of-queue newcomer captured. The equal-share variant
  1/(k+1) is reported as optimistic.

### 6.2 Results (S = 100 $ per eligible market, no capital constraint)

| Side rule | Eligible | Model | Fill share | Fill prob. | Newcomer P&L $ | Wrong-side markets |
|---|---|---|---|---|---|---|
| **P (frozen: source, else consensus)** | 31,234 | **LB** | **3.23 %** | 4.66 % | −1,982 | 23 |
| | | CENTRAL (live r) | 4.90 % | 37.86 % | −1,930 | 23 |
| | | CENTRAL (equal share, optimistic) | 22.95 % | 37.85 % | −1,365 | 23 |
| | | UB | 26.78 % | 37.86 % | −1,246 | 23 |
| S1 (source ∧ consensus agree) | 14,157 | LB / CENTRAL / UB | 3.15 / 6.35 / 40.55 % | 4.58 / 54.19 / 54.19 % | −55 / −9 / +475 | 1 |
| S2 (source only) | 28,044 | LB / CENTRAL / UB | 3.29 / 5.07 / 27.51 % | 4.71 / 38.76 / 38.76 % | −1,611 / −1,561 / −931 | 18 |
| Aug secondary, P | 28,253 | LB / CENTRAL / UB | 3.05 / 4.41 / 25.09 % | — | −3,855 / −3,816 / −3,230 | 52 |
| Aug secondary, S1 | 14,823 | LB / CENTRAL / UB | 3.19 / 5.50 / 37.77 % | — | +47 / +82 / +561 | 0 |

At S = 1,000 $ the fill shares under the frozen rule fall to 1.62 % (LB), 1.99 % (CENTRAL) and 15.18 % (UB).

**Adverse selection dominates.**

- When right, the newcomer sits behind an incumbent and gets about 3 %. When wrong, every holder of the losing token
  sells to it at 0.999. One wrong-side market costs roughly as much as 1,000 right-side fills earn.
- Frozen-rule losers:
  - 15 weather markets where the METAR proxy disagreed with NOAA and the market already traded the NOAA side;
  - 3 NHL preseason markets (shootout-goal convention; disputed);
  - 5 stale-consensus picks.
- S1 removes all but one: the NHL MTL–OTT total (ESPN 4–3 incl. shootout → Over; resolved Under after 2 disputes).

### 6.3 Queue competition (historical maker records, `data/competition_primary.json`)

- 3,591 distinct makers were filled at the post-determination floor. The top 1 / 5 / 10 hold 17.3 / 45.0 / 58.0 % of
  53.97 M$. Gebele & Matthes' `0x751a…` is still #4 (5.4 %).
- **In the median market a single maker absorbs 100 % of floor fills.**
- Only 11.4 % of floor-hit volume trades before T_DET + 60 s, and the median first floor fill comes 206 s after
  T_DET. The problem is not speed. It is being behind one large resting order.
- 75 % of floor maker notional comes from bids posted after determination; 25 % from bids resting through the end
  of the event.
- 11,461 distinct wallets sold into the floor.

### 6.4 Live read-only queue check (S8)

Public CLOB `/book` snapshots were taken every ~20 s, from 2026-09-29 23:35Z to 2026-09-30 ~04:00Z. From 00:53Z,
main markets were tracked from game start. Authoritative finals came from ESPN and MLB statsapi, polled every 30 s.
t_p = final first seen + 60 s.

| Sample | Markets | Games | Conservative fill share | Optimistic | Fill prob. | Median Q0 (shares) |
|---|---|---|---|---|---|---|
| **Timed (all)** | **273** | 7 | **1.23 %** | 1.23 % | 3.66 % | 50 |
| Timed, main market types | 83 | 6 | 1.26 % | 1.26 % | 2.41 % | 1,150 |
| Timed, with any floor flow | 34 | 6 | 9.9 % | 9.9 % | 29.4 % | 11,004 (median flow 39) |
| Late placement (already final at start) | 252 | 12 | 0.009 % | 0.009 % | 0.79 % | 85 |

The games were Ponte Preta @ Botafogo-SP, WNBA LV @ IND and MIN @ NYL, NHL MTL @ TOR and NYR @ BOS, CWS @ HOU (MLB)
and Aruba @ Anguilla.

Queue versus subsequent flow in the largest markets (shares):

| Market | Queue at 0.999 (Q0) | Floor hits after t_p | Newcomer fill |
|---|---|---|---|
| NHL MTL–TOR moneyline | 261,280 | 30,445 | 0 |
| NHL NYR–BOS moneyline | 72,997 | 17,189 | 0 |
| WNBA LV–IND moneyline | 257,663 | 4,671 | 0 |
| WNBA MIN–NYL moneyline | 218,390 | 1,892 | 0 |
| Brazil B moneyline | 27,808 | 720 | 0 |

Fills occurred only in thin markets with an empty queue (exact score, team totals), and those flows were 5–280
shares.

Tonight's MLB CWS@HOU markets resolved at 00:41–00:44Z. That was **before** statsapi's schedule showed "Final" at
00:45:34, so settlement windows can now be minutes and the queue forms in-play. Cancellation credit changed nothing:
queues did not thin in time.

**Pre-declared decision:** LB 3.23 % < 5 % ≤ UB 26.78 %, and live conservative 1.23 % < 5 % on ≥ 20 timed markets
→ **REJECTED_FILL_ACCESS**.

## 7. Capital economics (chronological, 30 days, no leverage)

Resting bids reserve S × 0.999 from t_p to T_RES. S = min(free capital, 25 % of capital). EUR/USD 1.1378 (ECB
2026-09-28). CENTRAL uses the live r.

| Capital EUR | Frozen rule P: LB / CENTRAL / UB (net EUR per 30 d) | S1 guard: LB / CENTRAL / UB | S1 markets posted / filled (CENTRAL) |
|---|---|---|---|
| 100 | −98.6 / −97.5 / −100 (ruin) | +1.6 / +3.8 / +16.4 | 1,393 / 699 |
| 500 | −500 / −500 / −500 (ruin) | +5.8 / +9.8 / +67.4 | 1,569 / 789 |
| **1,000** | **−1,000 / −1,000 / −1,000 (ruin)** | **+9.8 / +14.3 / +117.4** | 1,625 / 819 |
| 5,000 | −5,000 / −5,000 / −5,000 (ruin) | +28.2 / +33.1 / +379.4 | 1,706 / 866 |
| Aug secondary, EUR 1,000 | −246 / −244 / −205 | +11.5 / +16.6 / +112.0 | 1,611 / 828 |

The S1 capital paths happened not to post into the single S1 wrong-side market. Its expected cost is about 1 per
14,157 eligible markets × ~1,625 posts per month × 25 % of capital, which is about −29 EUR per month at EUR 1,000.
S1 LB and CENTRAL are therefore about zero or negative in expectation. UB assumes first-in-queue, which the live
check contradicts.

**OPPORTUNITY_RATE_TOO_LOW = TRUE**: CENTRAL at EUR 1,000 is below 10 EUR per 30 d (negative under the frozen rule;
≈ 14 − 29 EUR in expectation under S1).

## 8. Decay and persistence

Primary window by ISO week of T_RES:

| Week | Verified | With fills | Fills | Notional $ | Net | Losing fills | Median lock h | Disputed | Buyers | LB flow $ | UB flow $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| W35 (Aug 30–31) | 1,852 | 864 | 8,012 | 2.34 M | +0.1007 % | 0 | 1.84 | 0 | 2,404 | 115 k | 2.24 M |
| W36 | 7,460 | 2,547 | 17,566 | 7.73 M | +0.1001 % | 2 | 0.42 | 4 | 2,456 | 635 k | 7.29 M |
| W37 | 8,984 | 2,998 | 26,663 | 13.56 M | +0.1004 % | 0 | 0.29 | 3 | 3,339 | 3.02 M | 13.54 M |
| W38 | 9,493 | 3,499 | 27,615 | 19.13 M | +0.1004 % | 0 | 0.32 | 10 | 3,374 | 1.57 M | 17.80 M |
| W39 | 8,049 | 2,987 | 36,823 | 11.82 M | +0.1002 % | 4 | 0.65 | 4 | 3,359 | 418 k | 10.65 M |
| W40 (Sep 28) | 1,153 | 476 | 3,058 | 1.05 M | +0.1010 % | 0 | 1.85 | 0 | 130 | 59 k | 1.04 M |

**Secondary window (replication only).** Markets closed 2026-07-31 → 2026-08-29. The gamma keyset endpoint returned
repeated HTTP 500s, so the window was enumerated by events for MLB, soccer and weather (`s01b_enumerate_events.py`).
It is not a full census.

- 51,469 markets; 31,318 verified; 12,927 with fills; 84,313 fills.
- 32.34 M$ notional, **net +0.1003 %** (95 % CI 0.0995–0.1009 %).
- 1 losing fill (−2 $); median lock 0.74 h; 3,549 buyers.
- Weekly net 0.0995–0.1009 %.
- In-play contrast: +0.067 %, 28 losing fills.

Month over month the premium is identical (tick floor). Median lock shortened from 0.74 h to 0.42 h, consistent with
faster resolution (Agent 7). Competition and newcomer bounds are unchanged (LB 3.05 % vs 3.23 %). Agent 7 found the
mechanism in 8 windows over about 20 months, so there is no measurable decay of the per-fill premium. By
construction it is tick-bounded.

**Information error vs liquidity/time value.**

- After mechanical determination the premium equals the tick in every week, family and month.
- Losses fall from 30 in-play fills to 6 dispute artefacts, so the premium does not compensate outcome information.
- Locks last minutes to hours.
- 11,461 sellers pay to exit early while a concentrated maker set supplies balance sheet.

Persistence = **liquidity / time-value / operational friction, floored by the 0.001 tick**. Competition is expressed
as queue concentration, not price.

## 9. Limitations

- The historical queue is unidentified. LB is a bound, and the live check covers one night (7 games, clustered).
  Every liquid market in it shows queue ≫ flow.
- The executable universe excludes esports, tennis and lower-tier soccer, which have no historically timestamped
  public final.
- The weather METAR proxy differed from NOAA in 18 markets, the largest single source of newcomer losses.
- Rebates, holding rewards, gas and redemption latency are ignored (small relative to one wrong-side fill).
- data-api caps never truncated a window (coverage flags empty). The secondary window is a family-restricted
  replication, not a census.

## 10. Next action

Close S2 as a small-player candidate: **REJECTED_FILL_ACCESS**. Do not build execution, and do not spend paper or
shadow time on it.

Record in Quant learning:

- At tick floors, queue share, not the premium, is the binding variable.
- Any post-determination strategy needs a source-and-market-consensus guard. The METAR proxy is unsafe for weather,
  and shootout and void conventions must be encoded.

Route research to the next Blue-governed candidate, for example A5-S1 (NegRisk YES basket), with the same
source-first, adverse-selection-aware falsification.

The only residual worth a cheap read-only probe is thin markets with empty queues (exact score, team totals). Their
measured flow is 5–300 $ per market; the ceiling is < 20 EUR/month at EUR 1,000, so it is not recommended.

## 11. Reproduction

```bash
cd research/settlement_liquidity/scripts
python3 s01_enumerate_markets.py 2026-08-30 2026-09-29 markets_primary      # resumable (keyset cursor)
python3 s02_classify.py markets_primary
python3 s04a_mlb.py 2026-08-29 2026-09-28
python3 s04b_espn.py markets_primary 2026-08-28 2026-09-29
python3 s04c_weather.py markets_primary 2026-08-27 2026-10-01
python3 s04d_assemble.py markets_primary
python3 s05_fetch_trades.py primary 14 7200                                  # resumable per market
python3 s06_accounting.py primary 60
python3 s08_live_queue_monitor.py 30 ; python3 s08b_live_summary.py           # read-only live check
python3 s07_newcomer.py primary
python3 s09_competition.py primary
# secondary replication (Aug): s01b_enumerate_events.py 2026-07-31 2026-08-30 markets_secondary, then
# s02 / s04a (… secondary) / s04b / s04c / s04d / s05 secondary / s06 secondary / s07 secondary
```

Committed data (`data/`):

- the cohort (both windows);
- MLB, ESPN and weather determination inputs;
- per-market T_DET (corrected and as-frozen);
- every qualifying fill and the in-play contrast;
- newcomer inputs and results;
- competition diagnostics;
- the live queue summary and per-market live rows.

API caches (`data/raw/`) are not committed. All endpoints are public, and re-runs drift slightly with the live APIs.
