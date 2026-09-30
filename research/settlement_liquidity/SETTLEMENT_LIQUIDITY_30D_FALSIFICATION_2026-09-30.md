# S2 SETTLEMENT LIQUIDITY — 30-DAY FALSIFICATION (post-determination / pre-resolution)

REAL_CAPITAL_AUTHORIZED = FALSE. Research only. No orders were placed, signed or cancelled; every data source is
public and read-only.

Branch `claude/hopeful-dirac-4ahy2z` (harness-assigned; the only branch used). Pre-registration:
`PROTOCOL_PREDECLARED_2026-09-29.md` (commit `4433a24`, frozen before any fill or payout of the window was examined).
Resume/state file: `SETTLEMENT_LIQUIDITY_STATE_2026-09-30.md`.

```text
SETTLEMENT_LIQUIDITY_S2 = <<TERMINAL_STATE>>
```

SURVIVES_FALSIFICATION would not have been validation and would not have authorized capital; it was not reached.

## 1. Answer in one paragraph

<<ANSWER>>

## 2. Key numbers (primary window: markets closed 2026-08-30 → 2026-09-28, 30 complete UTC days)

| Quantity | Value |
|---|---|
| Markets enumerated (closed, volume ≥ 1 k$) | 115,574 |
| Excluded outcome-blind: crypto/asset Up-or-Down (E1) / asset-price thresholds (E2) | 31,466 / 4,519 |
| Kept | 79,589 (3.69 bn$ lifetime volume) |
| **T_DETERMINED verified** from an independent public timestamped source | **36,991** (1.42 bn$ volume); 42,598 DETERMINATION_UNVERIFIABLE |
| Verified markets with a non-empty settlement window [T_DET, T_RES) | 36,087 |
| **Primary cohort N** (verified markets with ≥ 1 qualifying buy in the window) | **13,371 markets / 119,737 fills** |
| Qualifying notional (BUY ≥ 0.998 in window, maker + taker) | 55.62 M$ |
| **Net cash P&L, all qualifying fills, after losses and fees** | **+55,810 $ = +0.1003 %** (market-cluster bootstrap 95 % CI 0.1002–0.1005 %) |
| **Losing fills** | **6 fills in 3 markets, −27 $** (all in disputed markets) |
| Median / p90 / notional-weighted capital lock | 0.42 h / 2.08 h / 0.76 h |
| Disputed markets among verified / among those with fills | 21 / 9 |
| Source-side vs final payout disagreement (false determination) | 21 / 28,889 source-determined markets (0.073 %) |
| Newcomer fill share, S = 100 $/market, frozen side rule (LB / CENTRAL / UB) | **3.23 % / 22.95 % / 26.78 %** |
| Newcomer P&L, frozen side rule, all queue models | negative; capital sims: ruin at EUR 100–5,000 |
| Newcomer with S1 guard (source ∧ market consensus), EUR 1,000, per 30 d (LB / CENTRAL / UB) | +9.8 / +96 / +118 EUR (path-lucky; expected value LB < 0, see §6.4) |
| Live read-only queue check (S8) | <<LIVE_ROW>> |

## 3. Design (pre-declared) and deviations

- **Universe**: every closed gamma market with `closedTime` in the window and `volumeNum ≥ 1,000`. No market was
  dropped for its outcome, P&L or dispute state.
- **T_DETERMINED** (protocol §3): official MLB live feed (`endTime` of the last play; NRFI / first-five / inning
  markets use the inning boundaries); ESPN play-by-play `wallclock` for NFL, NCAAF, WNBA, NHL and every soccer league
  whose summary publishes timestamped terminal events ('End of Game', 'End of Half', 'end-regular-time', 'halftime');
  METAR archive (IEM) for NOAA/WU-resolved daily temperature markets (first observation of the next local day;
  °F markets only when ≥ 1 °F from every bracket edge). Esports, tennis, UFC, F1, cricket, lower-tier soccer without
  timestamped whistles, politics, culture, mentions, tweets, economics → DETERMINATION_UNVERIFIABLE, excluded
  before economics.
- **T_RESOLUTION** = gamma `closedTime`. Settlement window W = [T_DET, T_RES).
- **Validation of T_DET**: the independent source precedes Polymarket's own venue feed (`finishedTimestamp`) by a
  median 62–102 s in every sports family (MLB 83 s, NFL/NCAAF 95 s, soccer 81 s, WNBA 62 s, NHL 102 s); 5–95 %
  range about −9 min to +1 min. The venue feed was never used as authority.
- **Deviations (disclosed; generic rules, found by classifier QA on source-side vs payout before any newcomer
  result existed)**: D1 MLB doubleheaders — ties broken by closest scheduled start (statsapi lists game 2 at a
  placeholder time); D2 team→outcome mapping must be unique and one-to-one ("Utah"/"Utah State", "NYCFC"/"NY Red
  Bulls", "Real Madrid"/"Rayo Vallecano de Madrid"). As-frozen output kept (`data/determination_primary_asfrozen.csv.gz`,
  35 disagreements → 21 after D1/D2). The live monitor needed two operational fixes (closed-market query, game-start
  filter); see state file.

## 4. Cohort and determination

| Family | Verified markets | Window > 0 | Median window | Source |
|---|---|---|---|---|
| Soccer (ESPN, top leagues + UEFA) | 13,536 + 4,438 (other soccer series matched to ESPN) | all | 0.60 h / 2.07 h | ESPN keyEvents wallclock |
| Weather (51 stations) | 10,643 | 10,639 | 0.43 h | IEM METAR |
| MLB | 4,115 | 3,501 | 0.32 h (p10 < 0: props resolved mid-game) | statsapi.mlb.com |
| NFL / NCAAF | 3,894 | 3,600 | 0.43 h | ESPN plays wallclock |
| WNBA / NHL | 262 / 103 | 262 / 98 | 0.53 h / 0.35 h | ESPN plays wallclock |

Unverifiable (excluded before economics): no independent source 26,361 (esports, tennis, UFC, F1, cricket, lower
soccer tiers unmatched); ESPN summary without timestamped terminal event 8,130; non-sports categories 6,101;
weather °F rounding 692, HKO 437, midnight-extreme 378, other 499.

**False determination.** Over 28,889 markets whose winning side is computable from the source, 21 disagree with the
final payout (0.073 %): 18 weather (METAR proxy vs NOAA timeseries, mostly daily lows and Chinese/SE-Asian
stations) and 3 NHL preseason (MTL–OTT, MTL–TOR; shootout-goal convention; 2 disputed on Polymarket). These are real
classifier risk for any newcomer using the same sources and are kept.

## 5. Rejection rule 1 — accounting of every qualifying fill

All BUY records (maker and taker, either outcome token) at price ≥ 0.998 inside [T_DET, T_RES) of the primary cohort.
Payout from final `outcomePrices`; taker fee size × rate × (p(1−p))^exponent; makers 0; rebates ignored.

| Slice | Fills | Markets | Notional $ | Net $ | Net / notional | Losing fills |
|---|---|---|---|---|---|---|
| **All ≥ 0.998** | 119,737 | 13,371 | 55,624,499 | **+55,810** | **+0.1003 %** | 6 |
| at 0.999 (tick floor) | 118,301 | 13,310 | 55,022,324 | +55,011 | +0.1000 % | 6 |
| at 0.998 | 486 | 172 | 56,262 | +110 | +0.195 % | 0 |
| makers only | 113,453 | 12,495 | 54,164,825 | +54,229 | +0.1001 % | 2 |
| takers only | 6,284 | 2,087 | 1,459,674 | +1,581 (fees 75) | +0.108 % | 4 |
| ESPN families | 66,356 | 8,033 | 39,889,109 | +39,982 | +0.1002 % | 0 |
| MLB | 23,848 | 1,661 | 6,576,480 | +6,649 | +0.1011 % | 2 |
| Other soccer matched to ESPN | 22,225 | 2,618 | 8,795,419 | +8,793 | +0.1000 % | 4 |
| Weather | 7,308 | 1,059 | 363,490 | +386 | +0.106 % | 0 |

Losing fills (complete list): 4 fills (−22 $) on "Will Oliver Nielsen be in Denmark's Starting 11?" — bought NO at
0.999 after the match; resolved YES after 2 disputes. 2 fills (−5 $) on MLB "Jared Jones: Strikeouts O/U 2.5/3.5" —
voided to 50/50 after 2 disputes. No fill lost to a genuine outcome reversal of a game result.

Descriptive: per-fill simple annualized return median 2,099 % (p10 419 %, p90 5,452 %) — meaningless for sizing
because capital utilization, not the per-fill rate, binds (§6).

**Contrast (in-play "0.999"):** the same buys in [T_DET − 2 h, T_DET): 48,520 fills, 31.70 M$, net +0.063 %
(95 % CI −0.005 % … +0.103 %), **30 losing fills in 14 markets (−13.6 k$)**. Agent 7's negative pooled result is an
in-play phenomenon; after mechanical determination the loss rate collapses from 30 to 6 fills (and those 6 are
dispute artefacts).

**Rule 1 verdict: primary post-determination net P&L = +55,810 $ > 0 → not rejected on net.**

## 6. Rejection rule 2 — newcomer access

### 6.1 Identification

Exact FIFO reconstruction is **impossible**: Polymarket publishes no historical L2 book and no order placement
times (the Goldsky order-book subgraph is deprecated). Partial identification used (protocol §5):

- A hypothetical newcomer rests BUY X at the floor (0.999) from t_p = T_DET + 60 s until T_RES, X = source side
  (else last-trade consensus).
- **Identified lower bound (LB)**: any taker trade after t_p at a winning-equivalent price ≤ 0.998 can only occur
  when the X 0.999 bid level is empty (price priority; mirrored YES/NO books), so a resting newcomer would have been
  first in queue. LB = that flow only (back of an unobserved queue, no credit for cancellations ahead).
- UB = first in queue at t_p (all floor hits + sub-floor flow). CENTRAL = LB + floor hits/(k+1).

### 6.2 Results (S = 100 $ per eligible market, no capital constraint)

| Side rule | Eligible markets | Model | Fill share | Fill probability | Flow share | Newcomer P&L $ | Wrong-side markets filled |
|---|---|---|---|---|---|---|---|
| **P (frozen: source, else consensus)** | 31,234 | **LB** | **3.23 %** | 4.66 % | 0.19 % | −1,982 | 23 |
| | | CENTRAL | 22.95 % | 37.85 % | 1.36 % | −1,365 | 23 |
| | | UB | 26.78 % | 37.85 % | 1.59 % | −1,246 | 23 |
| S1 (source ∧ consensus agree) | 14,157 | LB | 3.15 % | 4.58 % | 0.10 % | −55 | 1 |
| | | CENTRAL | 35.09 % | 54.18 % | 1.11 % | +398 | 1 |
| | | UB | 40.54 % | 54.18 % | 1.28 % | +475 | 1 |
| S2 (source only) | 28,044 | LB / CENTRAL / UB | 3.29 / 23.62 / 27.50 % | 4.71 / 38.76 / 38.76 % | — | −1,611 / −1,040 / −931 | 18 |

At S = 1,000 $ the frozen-rule fill shares fall to 1.62 / 10.71 / 15.18 %.

**Adverse selection is the dominant economic fact.** When the newcomer's side is right it sits behind an incumbent
and gets ≈ 3 % (LB); in the 0.07 % of markets where its side is wrong every holder of the losing token sells to it
at 0.999 and it is filled 100 %. Losses of 0.999 $/share against gains of 0.001 $/share make one wrong-side market
worth ≈ 1,000 right-side fills. Frozen-rule losers: 15 weather (METAR proxy ≠ NOAA), 3 NHL preseason (shootout
convention/disputes), 5 stale-consensus picks. The S1 guard removes all but one (NHL MTL–OTT total, disputed twice).

### 6.3 Queue competition (historical maker records, `data/competition_primary.json`)

- 3,591 distinct makers filled at the post-determination floor; top-1 17.3 %, top-5 45.0 %, top-10 58.0 % of
  53.97 M$ maker notional. Gebele & Matthes' `0x751a…` is still #4 (5.4 %).
- **In the median market a single maker absorbs 100 % of floor fills** (median top-maker share per market = 1.00).
- Only 11.4 % of floor-hit volume trades before t_p = T_DET + 60 s; the first floor fill comes a median 206 s after
  T_DET. Being late is not the problem; being behind one large resting order is.
- 75 % of floor maker notional comes from wallets with no floor fill before T_DET (bids posted after
  determination), 25 % from bids resting through the end of the event.
- 11,461 distinct wallets sold into the floor (liquidity demanders).

The equal-share CENTRAL model (k = 1 → newcomer takes half of the floor flow) is therefore optimistic.

### 6.4 Live read-only queue check (S8)

<<LIVE_SECTION>>

## 7. Capital economics (chronological simulation, 30 days, no leverage)

Resting bids reserve S × 0.999 from t_p to T_RES; S = min(free, 25 % of capital); EUR/USD 1.1378 (ECB 2026-09-28).

| Capital EUR | Frozen rule P: LB / CENTRAL / UB net EUR per 30 d | S1 guard: LB / CENTRAL / UB net EUR per 30 d | S1 markets posted / filled (CENTRAL) |
|---|---|---|---|
| 100 | −98.6 / −100 / −100 (ruin) | +1.6 / +15.2 / +16.4 | 1,621 / 816 |
| 500 | −500 / −500 / −500 (ruin) | +5.8 / +57.0 / +67.4 | 1,694 / 859 |
| **1,000** | **−1,000 / −1,000 / −1,000 (ruin)** | **+9.8 / +96.3 / +117.6** | 1,708 / 867 |
| 5,000 | −5,000 / −5,000 / −5,000 (ruin) | +28.2 / +255.8 / +380.7 | 1,722 / 875 |

S1 capital paths did not post into the single S1 wrong-side market (capital was busy elsewhere). Posting it would
have cost ≈ 25 % of capital (EUR 1,000: ≈ −250 EUR), flipping LB, CENTRAL and UB negative for that month. In
expectation (reference table, all eligible markets) S1 is negative at LB and positive at CENTRAL/UB; break-even
fill share ≈ 7 %. OPPORTUNITY_RATE_TOO_LOW (CENTRAL at EUR 1k < 10 EUR/30 d): **TRUE under the frozen rule**
(negative), not triggered under S1-CENTRAL.

## 8. Decay and persistence

| ISO week (by T_RES) | Verified | With fills | Fills | Notional $ | Net | Losing fills | Median lock h | Disputed | Distinct buyers | LB flow $ | UB flow $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-W35 (Aug 30–31) | 1,852 | 864 | 8,012 | 2.34 M | +0.1007 % | 0 | 1.84 | 0 | 2,404 | 115 k | 2.24 M |
| 2026-W36 | 7,460 | 2,547 | 17,566 | 7.73 M | +0.1001 % | 2 | 0.42 | 4 | 2,456 | 635 k | 7.29 M |
| 2026-W37 | 8,984 | 2,998 | 26,663 | 13.56 M | +0.1004 % | 0 | 0.29 | 3 | 3,339 | 3.02 M | 13.54 M |
| 2026-W38 | 9,493 | 3,499 | 27,615 | 19.13 M | +0.1004 % | 0 | 0.32 | 10 | 3,374 | 1.57 M | 17.80 M |
| 2026-W39 | 8,049 | 2,987 | 36,823 | 11.82 M | +0.1002 % | 4 | 0.65 | 4 | 3,359 | 418 k | 10.65 M |
| 2026-W40 (Sep 28) | 1,153 | 476 | 3,058 | 1.05 M | +0.1010 % | 0 | 1.85 | 0 | 130 | 59 k | 1.04 M |

<<SECONDARY_WINDOW>>

**Information error vs liquidity/time-value.** After mechanical determination the premium is the tick (0.1000 % at
0.999) in every week and family; losses fall from 30 fills (in-play contrast) to 6 dispute artefacts; locks are
minutes to hours; 11,461 sellers pay to exit early while a concentrated maker set supplies the balance sheet. The
persistence is **liquidity / time-value / operational friction floored by the 0.001 tick**, not information error.
Competition shows up as queue concentration, not price.

## 9. Limitations

- Queue position historically unidentified; LB is a bound, CENTRAL an assumption; live check is short and clustered.
- The executable universe excludes esports/tennis/lower-tier soccer (no timestamped public source); a live bot could
  watch more, but it cannot be verified historically.
- Weather determination uses a METAR proxy; the real source (NOAA timeseries) differed in 18 markets — the largest
  single cause of newcomer losses.
- Rebates, holding rewards, gas and redemption latency ignored (all small relative to one wrong-side fill).
- data-api caps (11,000 records per query) never truncated a window in this cohort (coverage flags empty).

## 10. Next action

<<NEXT_ACTION>>

## 11. Reproduction

```bash
cd research/settlement_liquidity/scripts
python3 s01_enumerate_markets.py 2026-08-30 2026-09-29 markets_primary      # resumable
python3 s02_classify.py markets_primary
python3 s04a_mlb.py 2026-08-29 2026-09-28
python3 s04b_espn.py markets_primary 2026-08-28 2026-09-29
python3 s04c_weather.py markets_primary 2026-08-27 2026-10-01
python3 s04d_assemble.py markets_primary
python3 s05_fetch_trades.py primary 14 7200                                  # resumable
python3 s06_accounting.py primary 60
python3 s07_newcomer.py primary
python3 s09_competition.py primary
python3 s08_live_queue_monitor.py 30 && python3 s08b_live_summary.py         # read-only live check
```

Committed data (`data/`): cohort, MLB/ESPN/weather determination inputs, per-market T_DET (corrected and as-frozen),
all qualifying fills and the in-play contrast, newcomer inputs/results, competition and live summaries. API caches
(`data/raw/`) are not committed; all endpoints are public and re-runs drift slightly with the live APIs.
