# AGENT 7 — EDGE ARCHAEOLOGY / DECAY

Date: 2026-09-29 (UTC). External research, public-API measurement and validation-latency audit.
No orders, no wallets, no credentials, no bots, no strategy code, no de-anonymisation.
**REAL_CAPITAL_AUTHORIZED = FALSE. LIVE_TRADING_AUTHORIZED = FALSE.**
Branch: `claude/exciting-planck-uq6rir` (harness-assigned). State file: `agent7_edge_archaeology_decay_etat.md`.
Supporting data and scripts: `agent7_data/`.

Central question: *when a real, publicly observable edge exists, does it survive long enough for Quant's
DISCOVERY → VERIFICATION → FALSIFICATION → SHADOW VALIDATION process to reach it before it decays?*

> Terminal answers are in §11 at the end of this file, after the evidence.

---

## 1. Method, labels, and what this file does not do

**Labels** (every quantitative claim carries one):
- **MEASURED**: recomputed by this agent on 2026-09-29 from public APIs / on-chain logs / git history (script in `agent7_data/scripts/`).
- **DERIVED**: arithmetic on MEASURED or cited figures (formula stated).
- **INFERRED**: an interpretation that goes beyond the data (reason stated).
- **ASSUMED**: an input without direct evidence (flagged).
- **UNKNOWN**: not established.
- **(P)** read in a primary document, **(S)** secondary source, **(A1…A6)** inherited from Agents 1–6 at the heads named in the mission, **(WS-A/B/C)** from this mission's three bounded archaeology workstreams (scratch notes summarised in §2).

**Evidence hierarchy** used to grade receipts, mechanisms and decay: raw on-chain/API data > official platform docs/changelogs > peer-reviewed or serious academic study > public source code tied to receipts > archived posts > reputable secondary analysis > anecdote.

**Chronology before narrative.** For every case, the dated chronology table is written first; the decay mechanism and causal attribution are written afterwards and graded `CAUSE_CONFIDENCE = HIGH / MEDIUM / LOW / UNKNOWN`. Publication preceding decay is never, by itself, treated as causal.

**Time variables** (mission §5): `T0` edge start, `T1` first observed receipt, `T2` first credible public disclosure, `T3` wide diffusion, `T4` decay start, `T5` edge end, `T_NOW` = 2026-09-29. Dates are `YYYY-MM-DD` only where supported; otherwise intervals or UNKNOWN. Edges still alive are **RIGHT_CENSORED** and only a minimum lifetime is reported.

**Not done here (by mission):** no strategy is built, validated or promoted; the Weather frozen rule and experiment are not touched; nothing here is a trading recommendation.

---

## 2. Source map

### 2.1 Prior Quant evidence reused (not redone)

| Source | Used for |
|---|---|
| A1 `claude/dazzling-dirac-foklrv@4682fbb` | Weather receipts (3 wallets), weather star decline, HL vaults (73.2% losers), HL small MM, rewards pool, fee rollout dates |
| A2 `claude/gallant-cerf-e0rpao@9438173` | Saguillo vs Gebele arbitrage, Kalshi maker/taker (Bürgi-Deng-Whelan + replication), Betfair, Metaculus, Numerai, LP, funding carry |
| A3 `claude/exciting-edison-w68tos@454d852` | polymm / @b00k13 recipe+receipt with monthly fill-rate collapse, poly-maker README, weather styles, NegRisk top-account exits |
| A4 `claude/magical-ramanujan-wsktyr@501093d` | Box office, tweet counts, music, mentions, post-determination; receipt semantics (`user-pnl` vs `closed-positions`) |
| A5 `claude/hopeful-hamilton-81rab1@85483fb` | 39.59 M$ vs 291 k$ reconciliation, #5/#8 cash reconstructions, settlement liquidity (0.14–0.15%), NegRisk YES basket, HLP |
| A6 `claude/epic-cannon-1sy39m@fff0cca` | 320-wallet reward cohorts, reward/rebate pool series, Numerai census, Metaculus, Kalshi LIP |
| Weather V1 spec `726070a`, Astra `e1cf4ca`, Fable V2 memo `5760ffa` | **Only** latency facts (burn-in, sample size, calendar) and venue-mechanics changes |
| Fast rail `claude/new-session-0ydmkg` (`TWO_SPEED_RESEARCH_PROPOSAL.md`, `FAST_RAIL_STATE.md`, `registry.jsonl`) | Measured engineering latency of Quant's existing fast rail; its statistical horizons |

### 2.2 New measurements by this agent (all MEASURED, 2026-09-29; scripts in `agent7_data/scripts/`)

| ID | Measurement | Source endpoint | Output |
|---|---|---|---|
| M1 | HLP vault period returns 2023-05-10 → 2026-09-29, quarterly medians, log-linear half-life, return-vs-AV elasticity | `POST api.hyperliquid.xyz/info {vaultDetails, 0xdfc2…f303}` | §4.1 |
| M2 | Polymarket maker-rebate pool decomposed **by recipient** for the 13 dates of A6's series (Polygon `Transfer` logs from the A6 payers), plus the dominant recipient's full API history | Polygon public RPC `eth_getLogs`; `data-api /activity?type=MAKER_REBATE` | §4.2 |
| M3 | Box office: winning-bracket and favourite prices at release anchors (Thu 18:00, Fri 14:00, Sat 14:00, Sun 14:00, Mon 18:00 ET) for 152 resolved opening-weekend events, 2023-11 → 2026-09; monthly event counts | gamma `events?tag_slug=box-office`; `clob /prices-history` | §4.3 |
| M4 | Weather NYC + London daily-high events (continuous since 2025-01) — winner/favourite prices at fixed local anchors, same-month year-over-year | gamma `events?tag_slug=weather`; `clob /prices-history` | §4.4 |
| M5 | Settlement liquidity: all fills ≥ 0.995 in the final 24 h of 200 random non-"Up or Down" markets (volume ≥ 1 k$) in eight mid-month windows 2025-01 → 2026-09 | gamma `markets?closed=true`; `data-api /trades` | §4.5 |
| M6 | Tweet-count family (Elon Musk post counts) monthly event volume 2024-04 → 2026-09 | gamma `events?tag_slug=` tweets-markets / elon-tweets / elon-musk | §4.6 |
| M7 | Monthly `user-pnl` deltas and weather-only realized P&L for already-public wallets (b00k13, gopfan2, aenews2, BeefSlayer, russell110320, HighTempTation, Bilberry) | `user-pnl-api`, `data-api /closed-positions` | §4.7 |
| M8 | Numerai Classic payout-rule regimes and round-level payout/stake, rounds 250 → 1365 (every 5th round) | `api-tournament.numer.ai` GraphQL `roundDetails` | §4.8 |
| M9 | Quant's own validation latency from git history and fast-rail registry timestamps | local `git log`, `registry.jsonl` | §3 |

Files: `agent7_data/m1_hlp_periods.json`, `m2_rebate_pool_by_recipient.csv`, `m3_box_office_anchors.csv`, `m3_box_office_event_counts.csv`, `m7_weather_strict.json`, `m4_weather_nyc_london_anchors.csv`, `m5_settlement_summary.json`, `m6_tweet_count_monthly_volume.csv`, `m7_wallet_monthly_userpnl.json`, `m8_numerai_rounds.json`, and `measurement_outputs.txt` (printed results of the analysis scripts). Scripts: `agent7_data/scripts/` (`hlp.py`, `rebate_by_recipient.py` + `rpc.py`, `box.py` + `box_analyze.py`, `wx_list.py` + `wx2.py` + `wx_analyze.py`, `settle_sample.py` + `settle_split.py`, `nmr.py`, `tweets_and_wallets.py`). All endpoints are public and unauthenticated; re-runs drift slightly with the live APIs.

### 2.3 External archaeology (WS-A informational, WS-B structural, WS-C subsidies/tournaments)

Three bounded research workstreams collected dated chronologies (docs/changelogs, papers, press, git first-commit dates of public repos). Their key dated facts are cited inline as (WS-A/B/C) with the underlying URL; items only seen in search summaries are marked (S, unopened). Wayback Machine was unreachable from this environment, so historical doc versions could not be recovered; this is the main archaeology limitation.

---

## 3. Quant's own validation latency (M9)

### 3.1 What Quant has actually taken to do each step (MEASURED from git / registry)

| Component | Quant evidence (timestamps UTC) | Value | Label |
|---|---|---|---|
| L_DISCOVERY | Receipt-first wave, Agents 1–6: first commit 15:09, last 17:36 on 2026-09-29 (six parallel agents; per-agent commit spans 9–57 min) | **hours (≤ 1 day)** | MEASURED |
| L_RECEIPT_VERIFICATION | A5 uncapped cash reconstruction of #8 (532,608 actions) committed 17:25; A6 320-wallet cohorts 16:54 → 17:36 (cohort windows are historical, no waiting) | **hours** | MEASURED |
| L_MECHANISM_RECONSTRUCTION | Same wave (A4/A5 mechanism cards) | hours – days | MEASURED / INFERRED |
| L_EXPERIMENT_DESIGN | Weather V1 frozen spec 16:25 (≈ 1 h after A1's weather receipt). Fast rail H-001: IDEA 2026-09-25 14:10 → statistic amended 2026-09-29 11:15 | **hours for a first freeze; ~4 days with red-team amendments** | MEASURED |
| L_INDEPENDENT_AUDIT | Astra feasibility review 17:11 (46 min after the freeze); Fable V2 challenge 17:41; H-001 red teams RT-2026-09-29-02 and -03 on the same day | **hours per round; 2–3 rounds typical** | MEASURED |
| L_REDESIGN after a failed audit | Weather V1 → `BLOCKED_POWER_BELOW_DECLARED_MEUE`; V2 architect + re-audit still pending at T_NOW | ≥ days, open | MEASURED (open) |
| L_BUILDER | H-001 collector merged 2026-09-27 03:58 (≈ 1.6 days after IDEA); SHADOW_DIRECT from 2026-09-29 14:00. The chassis itself (P0 → first vertical) took 2026-09-13 → 2026-09-21 but is reusable | **per-strategy collector ≈ 1–3 days**; full vertical adapter UNKNOWN (days–weeks) | MEASURED / INFERRED |
| L_BURN_IN | Weather: readiness-gated t0 at capture day ≈ 33–36, plus ≈ 3–4 weeks readiness and ≥ 14 decision-only dates (Fable V2 §5) | **≈ 7–10 weeks** (Weather) ; 0 for SHADOW_DIRECT lanes | DERIVED (Quant docs) |
| L_FORWARD_SAMPLE | Weather Family D: 120 complete dates (+3 d) for a powered label at θ_PCE ≈ 0.06–0.25/$; θ = 0.02/$ needs 1,145–2,290 dates ≈ **3.1–6.3 years** (Fable §2). H-001: 806 matches expected if H1 true, horizon 1,500. H-014: "decision possible in ≈ 3–4 months". H-009: ≈ 1,500 adjudications, no achievable verdict. FOMC calendar: years. Form-4 vertical: ≈ **3.6 years** to a first economic answer (its own frozen spec, quoted in `TWO_SPEED_RESEARCH_PROPOSAL.md` §1) | **months to years** | DERIVED (Quant docs) |
| L_INTEGRATION | Reorientation checkpoint §2: Control Plane does not yet auto-invoke the economic-admission bridge; legacy Desk path not spliced | UNKNOWN (bounded gaps) | INFERRED |
| L_GOVERNANCE | Owner checkpoint cadence (fast-rail checkpoint set for 2026-10-05); any capital step is owner-only | ≈ weekly for routing; capital: not applicable here | MEASURED (docs) |

### 3.2 The two clocks

- **Engineering / human-AI clock** (discovery → verification → design → audit → build): **≈ 1–3 weeks per candidate**, dominated by redesign/re-audit cycles when a first freeze fails (Weather V1 is the live example). The AI-agent research wave compresses discovery and receipt verification to hours.
- **Statistical clock** (independent forward observations the market must produce): **≈ 2–12 months** for daily/weekly edges at economically plausible effect sizes, **years** for small effects. Quant's own fast rail recorded the same lesson: *"Le goulot est le forward, pas les idées"* (`FAST_RAIL_STATE.md`, 2026-09-29).

**The statistical clock dominates the engineering clock by roughly one order of magnitude** (DERIVED from the table). Engineering acceleration cannot fix this; only (a) higher-frequency independent observations, (b) lower-variance statistics that still describe the executable economics, or (c) historical evidence that is legitimately admissible, can.

### 3.3 Validation-latency archetypes used in the case cards (DERIVED)

| Archetype | Independent observations | Realistic L_TOTAL_VALIDATION (paper/shadow, powered for a plausible effect) |
|---|---|---|
| V1 high-frequency, many obs/day (settlement fills, reward accrual) | hundreds–thousands/day | **2–8 weeks** (a historical census in days + a shadow queue proxy in weeks). **Caveat:** queue priority / adverse selection of a *new* maker is not observable in paper; only a proxy can be validated |
| V2 daily markets (weather) | ≈ 1 effective obs/day after date clustering | **≈ 6–8 months** to a first powered label, large effects only; years for θ ≈ 0.02 |
| V3 weekly markets (box office) | ≈ 2–6 events/week | historical replay (falsification): days (MDE only ≈ 0.13/$); prospective validation: **≈ 9–22 months** for +10%/$ (M3, §4.3) |
| V4 regime/round programs (Numerai v3) | one resolution cycle ≈ 60 days + ≥ 20 rounds | **≈ 3–5 months** |
| V5 delegated, episodic payoff (HLP) | a few liquidation episodes per year | **≥ 12–24 months** to separate excess return from lending yield |

### 3.4 Discovery lag: the receipt-first method finds edges late in life (DERIVED)

Receipt-first search can only see an edge **after** it has produced visible winners. The gap between a mechanism becoming available (T0) and Quant's discovery (2026-09-29) is:

| Case | T0 (earliest defensible) | Discovery lag at T_NOW | Main decay already observed before discovery? |
|---|---|---|---|
| Weather (daily city markets) | 2025-01-21 (first NYC/London daily events, M4) | ≈ 20 months | **Yes for the first specialist cohort** (weather-wide peak 2024-09 → 2025-02, decline from 2025-03, M7 word-boundary filter); mechanism still pays a new cohort |
| Box office (regular weekly series) | 2025-10 (M3: 1–5 events/month before, 5–26/month after) | ≈ 12 months | No measured decay (M3) |
| Tweet counts | 2024-05 (first weekly events, M6) | ≈ 28 months | **Yes** (large-winner P&L falls from 2026-03/04; three of four large winners gone by 2026-04, the fourth by 2026-07; family volume −87% from peak, M6) |
| polymm esports MM | 2026-01-06 (first trades, A3) | ≈ 9 months | **Yes** (fill rate 37% → 1% by 2026-04; A3, M7) |
| NegRisk conversion arbitrage | 2023-11-28 (adapter on-chain, WS-B) | ≈ 34 months | **Yes** (≈ $1 → $0.08 per conversion; A5 #8 dried in 3 months) |
| HLP | 2023-05-10 (vault inception, M1) | ≈ 40 months | **Yes** (return half-life ≈ 5 months, M1) |
| Settlement liquidity | ≤ 2025-01 (M5; A5's academic sample starts at market inception) | ≥ 20 months | No (floor premium unchanged, M5) |
| Polymarket liquidity rewards | 2022-02-17 (WS-C, inferred year) | ≈ 4.6 years | Per-recipient dilution; program alive |

**Median discovery lag ≈ 24 months (range 9–55); in 5 of 8 dated cases the principal decay had already happened before Quant found the edge.** This is a structural property of receipt-first discovery (it conditions on visible success), not a flaw of any one agent. It is the single most important timing fact for Quant: *the binding constraint is often not validation speed after discovery, but how late in an edge's life discovery occurs.*

---

## 4. New empirical measurements

### 4.1 M1 — HLP (Hyperliquid protocol vault): a clean measured decay curve

Data: `vaultDetails` portfolio `allTime` (98 usable periods of ≈ 2–14 days, 2023-05-10 → 2026-09-29). Period return = Δpnl / account value at period start (MEASURED).

| Half-year | Median AV (M$) | Annualised return, all periods | Annualised, excluding the single best period | Median daily return (bp) | Best period's share of half-year P&L |
|---|---|---|---|---|---|
| 2023H2 | 7 | 158.5% | 137.3% | 20.5 | 42% |
| 2024H1 | 84 | 153.7% | 135.9% | 13.3 | 18% |
| 2024H2 | 179 | 28.0% | 23.3% | 6.2 | 19% |
| 2025H1 | 356 | 11.8% | 8.4% | 2.6 | 34% |
| 2025H2 | 448 | 26.1% | **5.1%** | 1.6 | **82%** (period ending 2025-10-15: +41.4 M$, the 10–11 Oct crash) |
| 2026H1 | 372 | 14.8% | **0.2%** | 0.18 | **101%** (period ending 2026-02-04: +18.8 M$) |
| 2026H2 (to 09-29) | 202 | 3.0% | 1.8% | 0.8 | 49% |

- Log-linear fit of quarterly median daily return, 2023Q4 → 2026Q3: slope −1.62 ± 0.24 per year ⇒ **half-life ≈ 5.1 months (95% CI 4.0–7.2)** (DERIVED).
- Elasticity of median return to vault AV ≈ −0.98 (DERIVED): dollar P&L per period roughly constant while capital grew ~60× — the signature of a **fixed flow shared by more capital** (capacity saturation / platform-growth dilution). Time and AV are collinear, so this does not separate competition from dilution.
- Since 2026H1 the ex-best-period return (0.2%, 1.8% annualised) is below HLP's own current API APR (3.94%, A5); **no USDC lending benchmark was measured here**. What remains is **episodic crash insurance**: the two liquidation windfalls (periods ending 2025-10-15 and 2026-02-04) are ≈ 44% of lifetime P&L in the M1 data (≈ 41% per CoinGecko, (S)).

### 4.2 M2 — The Polymarket maker-rebate "collapse" is a single-recipient discontinuity

A6 reported the daily rebate pool falling from ≈ 1.01 M$ (09-01) to 162 k$ (09-15) and 124 k$ (09-29). Re-reading the same payer logs **by recipient** (MEASURED):

| Date (2026) | Total paid by rebate payer | Paid to `0x2d50…ea54` | **All other recipients** | Recipients |
|---|---|---|---|---|
| 04-01 | 915,293 | 768,759 | **146,534** | 5,203 |
| 04-15 | 1,035,744 | 813,647 | **222,097** | 7,125 |
| 05-01 ⚠ | 1,686,916 | 710,490 | 976,426 (incl. 772,343 to the pUSD token contract — migration artefact) | 7,470 |
| 05-15 | 841,924 | 652,048 | **189,876** | 7,642 |
| 06-01 | 854,223 | 657,610 | **196,612** | 6,708 |
| 06-15 | 1,678,066 | 1,277,731 | **400,335** | 7,794 |
| 07-01 | 1,643,540 | 1,255,018 | **388,522** | 7,522 |
| 07-15 | 2,299,043 | 1,929,643 | **369,400** | 7,522 |
| 08-01 | 1,054,074 | 877,684 | **176,390** | 5,697 |
| 08-15 | 1,168,086 | 971,954 | **196,132** | 5,482 |
| 09-01 | 1,014,299 | 837,373 | **176,926** | 4,632 |
| 09-15 | 161,994 | 0 | **161,994** | 4,727 |
| 09-29 | 123,954 | 0 | **123,954** | 4,396 |

The dominant recipient (MEASURED through `data-api /activity`): **243 MAKER_REBATE payments totalling 165.3 M$ from 2026-01-16 to 2026-09-10, then none**; monthly 1.2 M$ (Jan) → 36.4 M$ (Jul) → 8.8 M$ (Sep 1–10). The same address has **no trades, no positions, no `user-pnl` series and no leaderboard entry** in the public API (only MAKER_REBATE, YIELD, REWARD and REFERRAL_REWARD receipts); its code is a 23-byte `0xef0100…` delegation stub. INFERRED: it collects rebates for trading done from other addresses, or reflects a special arrangement; its owner is not investigated (no de-anonymisation).

Consequences (DERIVED / INFERRED):
- For every other maker the rebate pool was ≈ 150–220 k$/day (Apr–May), ≈ 370–400 k$/day during the World Cup window (FIFA World Cup 2026-06-11 → 07-19; WS-C: platform volume −36.7% Jul → Aug), ≈ 176–196 k$/day (Aug → 09-01), then 162 k$ and 124 k$ in September: **a ≈ 30% decline over September for everyone else, not the ≈ 13× (07-01 → 09-29, as quoted in A6's state file and the reorientation checkpoint) or ≈ 8× (09-01 → 09-29) fall of the aggregate.** The recipient count is flat across the break (4,632 → 4,727).
- WS-C's independent consistency check reaches the same place from the fee side: at 15–25% of ≈ 1.2–2.7 M$/day gross fees, pure maker rebates should be ≈ 0.2–0.7 M$/day, so the pre-September level was too high for ordinary rebates; the post-break level is consistent with documented economics. No changelog entry explains a program-wide change in 09-01..09-15 (WS-C, docs.polymarket.com/changelog).
- **Classification of the event:** `COUNTERPARTY_SPECIFIC_DISCONTINUITY` (one recipient's rebate stream ended), cause UNKNOWN (CAUSE_CONFIDENCE LOW for any specific cause). It is **not** evidence of program-wide competitive decay and **not** a program-wide regime break. A6's cohort conclusion (rebates add 0–5 points to the share of net-positive wallets) is unaffected because its sampled wallets were not the dominant recipient (A6: sampled B·T4 rebates 102 k$ → 105 k$ in months 2–3).

### 4.3 M3 — Box office: information absorption did not speed up over 12 months

Market history (MEASURED, gamma, 273 box-office-tagged events): sporadic 2023-11 → 2025-09 (0–7 events/month, mostly tentpole films); **regular weekly series from 2025-10** (5, 8, 18, 12, 20, 20, 14, 24, 25, 20, 24, 26 events/month Oct-2025 → Sep-2026).

Winning bracket's price at release anchors (ET; opening-weekend events; 152 usable):

| Period | n | Median event volume | Winner median: Thu 18:00 / Fri 14:00 / Sat 14:00 / Sun 14:00 / Mon 18:00 | Winner = favourite at Sat 14:00 / Sun 14:00 |
|---|---|---|---|---|
| 2023-11 → 2025-09 (sporadic, big films) | 35 | 248 k$ | 0.51 / 0.67 / 0.95 / 0.99 / 1.00 | 91% / 97% |
| 2025Q4 | 26 | 134 k$ | 0.45 / 0.52 / 0.78 / 0.95 / 1.00 | 92% / 96% |
| 2026Q1 | 31 | 179 k$ | 0.44 / 0.46 / 0.83 / 0.96 / 1.00 | 84% / 90% |
| 2026Q2 | 30 | 208 k$ | 0.40 / 0.60 / 0.84 / 0.97 / 1.00 | 87% / 93% |
| 2026Q3 | 30 | 83 k$ | 0.35 / 0.42 / 0.78 / 0.98 / 1.00 | 73% / 90% |

- Trend in the winner's price over the regular series (Spearman vs date): Fri 14:00 ρ = −0.05 (z −0.56), Sat 14:00 ρ = −0.03 (z −0.34), Sun 14:00 ρ = −0.05 (z −0.53). **No evidence that Friday actuals or Sunday estimates are priced faster in 2026 than in late 2025** (MEASURED).
- Descriptive calibration diagnostic (not a strategy; mid price + 0.05·p(1−p) fee, no spread): buying the **Saturday-14:00 favourite** returned +25.0% [+2.4, +44.4] (2025Q4, n=22), +7.1% (2026Q1), +14.8% (2026Q2), **−14.4%** [−35.2, +5.2] (2026Q3); pooled +6.9% [−4.4, +17.8], n=106; trend ρ = −0.14 (z −1.47). The **Sunday-14:00 favourite** returned ≈ 0 in every quarter (pooled +0.9% [−7.2, +8.3]): **the Sunday estimate is absorbed within ≈ 3 h of publication.** The only residual slow-information window is between Friday actuals and Sunday, and boundary-case judgement (A4).
- Reading: consistent with **no measurable decay** (right-censored at 12 months), with a weak, non-significant downward drift in the naive Saturday signal that cannot be separated from sampling variance (n ≈ 25/quarter) or from the 2026Q3 mix of smaller films (median volume 83 k$).
- **Statistical latency (DERIVED):** usable opening-weekend events ≈ 2.2/week; per-event return SD ≈ 0.58/$; detecting +10%/$ at 80% power (one-sided α 0.05) needs ≈ 208 events ≈ **96 weeks** at that rate (≈ 9 months if every box-office family at ≈ 5–6 events/week were admissible); +25%/$ needs ≈ 33 events (≈ 15 weeks).

### 4.4 M4 — Weather (NYC + London, continuous since 2025-01)

Market history (MEASURED, gamma, and WS-A's per-city first-appearance dates): daily "Highest temperature in <city>" events start **2025-01-21** with NYC and London only (≈ 60 events/month through 2025-11); **2 → 13 cities on 2025-12-04/05, 14 → 38 during 2026-03, 51 by 2026-04** (WS-A), "Lowest temperature" series from 2026-04-13, ≈ 100 events/day by 2026-09 (Weather V1 spec C15). (My own event enumeration is truncated by the gamma offset cap at 2,100 events, so its 2025-12 → 2026-03 counts are not used for levels.) Bucket ladder per event: **7 buckets (2025) → 9 (2026-02) → 11 (from 2026-03/04)**. Median volume per NYC/London event: 40–110 k$ (2025-02 → 10) → 150–315 k$ (2025-11 → 2026-04, excluding 2026-03 where the `volume` field reads 0–14 k$, an API anomaly) → 63–79 k$ (2026-09).

1,223 NYC + London events; prices of every bucket at D−1 12:00, D 00:00, D 09:00 and D 15:00 local (MEASURED):

| Quarter | Bucket-level calibration error at D 00:00 (ECE, 7 price bins) | Favourite return at D−1 12:00 (mid + 0.05·p(1−p)) [95% CI] | Favourite return at D 00:00 |
|---|---|---|---|
| 2025Q1 (launch) | **0.038** (e.g. buckets priced 0.76 hit 50%; 0.39 → 31%) | **−34.9% [−54.1, −14.8]** | **−29.8% [−44.9, −12.7]** |
| 2025Q2 | 0.021 | −7.1% | −8.4% |
| 2025Q3 | 0.026 | +4.2% | +10.6% |
| 2025Q4 | 0.011 | −0.2% | −0.6% |
| 2026Q1 | 0.021 | +20.6% [+4.7, +36.6] | +3.5% |
| 2026Q2 | 0.009 | −9.0% | −2.4% |
| 2026Q3 | 0.011 | −4.3% | −2.3% |

Same-month year-over-year (Feb–Sep 2025 vs Feb–Sep 2026, same city, same anchor):
- **NYC**: mean multi-bucket Brier at D−1 12:00 **0.769 → 0.664**, at D 00:00 0.706 → 0.630; favourite hit rate 34% → 47% and 42% → 48% — the market got **sharper despite finer buckets** (7 → 11, which mechanically raises Brier).
- **London**: essentially unchanged (D 00:00 Brier 0.653 → 0.657; D−1 0.739 → 0.689).

Reading (DERIVED / INFERRED):
- The **simple price-internal inefficiency of the launch quarter (overpriced favourites, ECE 0.038) was gone within ≈ 2–3 quarters** (by 2025Q3–Q4), i.e. within ≈ 6–9 months of the daily-market launch. This coincides with the first specialist cohort's weather P&L fading from 2025-05 (M7).
- ECE has a small-sample floor (≈ 0.01–0.02 at these bin sizes) and 2026 has more buckets per quarter, so the post-2025Q2 values are near the noise floor; the launch-quarter value is not.
- **Calibration is not forecast skill.** A calibrated market can still be beaten by a sharper forecast; this measurement cannot see that edge (it needs archived forecast vintages, deliberately not used here to stay outside the Weather rail). It shows only that the easiest inefficiency decayed fast and that NYC prices became sharper year-over-year.
- **Venue mechanics changed at least 4 times in 8 months**: ladder 7→9→11 buckets (2026-02 → 04), weather taker fee (2026-03-30), taker-rebate program (2026-05-28), settlement template Weather Underground → NOAA (≈ 2026-08, Weather V1 spec C5). City count 2 → 51 over 2025-12 → 2026-09.

### 4.5 M5 — Settlement liquidity across 2025–2026

Eight mid-month windows, 200 random resolved binary markets each (volume ≥ 1 k$, crypto "Up or Down" excluded), every fill at ≥ 0.995 in the final 24 h before `closedTime` (MEASURED; 1,499 markets, 31,064 fills):

| Window | ≥ 0.999 notional (k$) | Gross (= tick floor) | ≥ 0.999 losing fills / loss | ≥ 0.999 net | Share of ≥ 0.995 notional at ≥ 0.999 | Median hold, winners (h) | Distinct taker wallets at ≥ 0.999 |
|---|---|---|---|---|---|---|---|
| 2025-01 | 1,321 | 0.100% | 1 / 7 $ | +0.100% | 78% | 2.1 | 834 |
| 2025-04 | 1,215 | 0.100% | 6 / 19,171 $ | **−1.479%** | 76% | 2.7 | 2,131 |
| 2025-07 | 1,053 | 0.100% | 0 | +0.100% | 79% | 2.6 | 836 |
| 2025-10 | 4,620 | 0.100% | 0 | +0.100% | 89% | 10.7 | 4,402 |
| 2026-01 | 1,304 | 0.100% | 27 / 8,237 $ | **−0.532%** | 76% | 2.4 | 1,980 |
| 2026-04 | 2,360 | 0.100% | 0 | +0.100% | 89% | 3.0 | 3,635 |
| 2026-07 | 274 | 0.100% | 0 | +0.100% | 63% | 0.6 | 741 |
| 2026-09 | 626 | 0.100% | 0 | +0.100% | 89% | 0.6 | 825 |
| **Pooled** | **12,774** | 12,759 $ | **34 fills / 27,415 $** | **−0.115%** | — | — | — |

- Every losing ≥ 0.999 fill is a **live sports game** (NBA Timberwolves–Bucks, NHL Canucks–Stars, NCAA Marquette–St John's, a tennis set O/U), bought 0.2–3.6 h before close — i.e. **not yet decided**. No resolution dispute appears in these samples.
- The 0.995–0.998 band is pooled ≈ 0.00% net (2.57 M$ notional, 76 losing fills).
- Reading (DERIVED): the gross return of a ≥ 0.999 fill is **≈ 0.100% by construction** (the tick floor), so this design **cannot test whether the premium per fill decays**; what it does show is that the floor trade occurred in every window for ≈ 20 months and that the share of near-certain volume executed at the floor is stable (63–89%); holds shortened in 2026-07/09 (0.6 h vs 2–3 h), consistent with faster resolution paths (crypto auto-resolution Aug 2026, settlement-time estimates published 2026-09-28; WS-B). The net figures cover **every buyer at ≥ 0.999 (side not distinguished: resting bids and taker lifts)**, not only the resting-bid strategy of A5-S2; the "distinct taker wallets" column counts trade-record wallets (buyers or sellers). **The economics are governed by the tail rate of "near-certain but not decided" fills (≈ 1.4 per 1,000 fills here, size-weighted loss ≈ 2.1× gross), not by a measured decay.** A5's two September-2026 slices (+0.14–0.15%, 3 losers in ≈ 11,000 fills) are consistent with the good months here, not with the pooled result.

### 4.6 M6 — Tweet-count family volume

Monthly volume of Elon-Musk post-count events (MEASURED, gamma, 390 keyword-matched events; the single 2024-04 item is a "will Elon post X" market, not a count event): 2024-05 → 2024-12 0.3–9.2 M$/month; 2025-01 → 2025-09 17–41 M$; 2025-10 58 M$; 2025-11 114 M$; 2025-12 173 M$; **2026-01 240 M$ (peak)**; 2026-02 211 M$; 2026-03 124 M$; 2026-04 149 M$; 2026-05 136 M$; 2026-06 79 M$; 2026-07 47 M$; 2026-08 41 M$; **2026-09 31 M$ (−87% from peak)**. Of the four large 2025-26 winners (A4), noovd and 0xecc stopped in 2026-01 after losing months, failstober peaked in 2026-02 and stopped in 2026-04, and Annica peaked in 2026-02/03 (+952k, +984k closed-realized) and stopped after 2026-07; the category fee (rate 0.04) started 2026-03-30 (A1, WS-C).

### 4.7 M7 — Named public wallets: decay of traders vs decay of mechanisms

Weather-only realized P&L from `closed-positions` (upper-biased, attribution only; MEASURED):
- **gopfan2** (word-boundary weather filter; an initial loose filter also matched "Ukraine"/"Bahrain" titles and was replaced): 2024-09 +27.0k, 2024-10 +14.7k, 2024-11 +17.8k, 2024-12 +20.4k, **2025-01 +42.9k, 2025-02 +84.6k**, then **2025-03 +9.8k**, 2025-04 +6.8k, 2025-05 +3.1k, 2025-06 +0.9k, a few later bumps (2025-11 +17.4k, 2026-01 +16.2k), and 1–4 weather positions/month since 2026-02. Whole-wallet `user-pnl` stays large and volatile (e.g. +161.2k in 2026-09): the trader left weather; the wallet did not stop.
- **aenews2** (same filter): weather gains 2024-08 +148.4k (one position), 2024-09 +44.5k, 2025-02 +27.9k, then ≤ +3.5k/month from 2025-03; whole-wallet still active (e.g. +696.8k 2026-06, −187.7k 2026-07). Data: `agent7_data/m7_weather_strict.json`.
- Current weather receipt wallets start later: BeefSlayer first point 2025-09-18 (weather-period gains 2026-01 → 04), HighTempTation 2026-03-06 (+15–28k/month since 2026-06), Bilberry 2025-12-30 (≈ 0 until 2026-08, then +46.8k in 2026-09).
- **polymm author b00k13** (`user-pnl`, all categories): +2.0k (2026-01), +2.5k (02), +0.4k (03), +0.1k (04), then ≈ 0 (≤ +0.7k/month) — matching the author's published fill-rate collapse 37% → 1% (A3).

Reading: **cohort turnover** — early specialists fade (or migrate) after ≈ 6–10 months at peak, while new wallets earn later. The *mechanism* survived the *first traders*. Individual-wallet decline is therefore not evidence that the mechanism ended (self-audit item 17).

### 4.8 M8 — Numerai: payout rules change every 8–24 months

Payout-multiplier regimes on the Classic tournament from the round API (sampled every 5th round, so boundaries ± 5 rounds; MEASURED), cross-checked with WS-C (numerai/docs git history, forum posts):

| Regime (round API) | First sampled round (open date) | Length |
|---|---|---|
| corr20 ×1 (+ mmc ×0) | ≤ 250 (≤ 2021-02-06) | ≥ 15 months |
| corr20 ×1 + TC ×0 (TC era, from round 311 per WS-C) | 315 (2022-05-07) | ≈ 12 months |
| v2_corr20 ×1 + TC | 485 (2023-05-16) | ≈ 8 months |
| v2_corr20 ×0.5 + mmc ×2.0 ("MMC only" cut after payouts judged "overly generous", 30.65%/yr; forum 2023-11-15, WS-C) | 650 (2024-01-02) | ≈ 24 months |
| v2_corr20 ×0.75 + mmc ×2.25 | 1175 (2026-01-06) | ≈ 8 months |
| **corr60 ×3 + mmc60 ×15, payout factor 1.0 (v3 atomic staking, 60-day target)** | **1345 (2026-09-01)**; WS-C: "rounds starting on or after 2026-08-28" = round 1343 | open (no v3 round resolved at T_NOW) |

Correction to A6: the v3 regime starts at round **≈ 1343 (2026-08-28)**, not ≈ 1363 (2026-09-25); both place every A6-measured round (1213–1341) in the legacy regime, so A6's legacy result stands. Five discretionary rule changes in ≈ 5.6 years ⇒ **regime length 8–24 months (median ≈ 12)**; the 60-day scoring target means the first v3 rounds resolve ≈ late October–November 2026.

---

## 5. Case studies

Each case: (1) chronology table (built first), (2) decay-vs-variance discrimination, (3) causal attribution, (4) the §29 card. `L_val` = expected Quant validation latency from §3.3; `τ_rem` = expected remaining edge lifetime at T_NOW; ACTIONABILITY_RATIO = τ_rem / L_val.

### 5.A WEATHER — Polymarket daily city temperature markets (Type I, informational)

**Chronology**

| Date | Event | Source | Label |
|---|---|---|---|
| 2024 (monthly) | Only monthly/annual global-temperature markets exist | gamma (WS-A) | MEASURED (WS-A) |
| 2024-08 → 2025-02 | gopfan2 weather realized P&L 2024-09 +27.0k … 2025-01 +42.9k, **2025-02 +84.6k** (upper-biased closed-positions, word-boundary filter) | M7 | MEASURED |
| **2025-01-18 / 01-21** | First daily city market (DC inauguration); **daily NYC + London markets start** (Weather Underground settlement) | gamma (WS-A, M4) | MEASURED — **T0** |
| 2025Q1 | Launch-quarter mispricing: favourites overpriced (favourite return −30% to −35%, CI excludes 0), ECE 0.038 | M4 | MEASURED |
| 2025-05-07 | First Polymarket-specific public analysis repo (`aheck3/nyc-temperature-forecasting-polymarket`, ≈ 16★) | WS-A | MEASURED (repo) — first niche public mention |
| **2025-03** | First-cohort decay: gopfan2 +84.6k → +9.8k, aenews2 +27.9k → +0.4k (weather-only, M7) | M7 | MEASURED — **T4 (first cohort)** |
| 2025Q3–Q4 | Market calibrated: ECE 0.011–0.026, favourite return ≈ 0 | M4 | MEASURED |
| 2025-09-18 | New-cohort wallet BeefSlayer first P&L point | M7 | MEASURED |
| 2025-11 | NYC/London event volume ≈ 60–70 k$ → ≈ 290 k$ | M4, WS-A | MEASURED |
| 2025-12-04 | Expansion 2 → 13 cities | WS-A (gamma) | MEASURED |
| **2025-12-30/31** | Viral X posts on a London-only bot ($204 → ≈ $24k) and "Hans323" | investx.fr recap of tweets (WS-A) | (S) — **T2 first broad disclosure** |
| 2026-01 → 02 | 11 then 29 "polymarket weather" repos/month; 2026-01-28 Simmer "gopfan2-style" AI-agent skill; 2026-01-29 first dated source naming gopfan2 with weather; 2026-02-05 PolyWeather (319★), 2026-02-10 suislanchez (768★); 2026-02-06 Odaily/KuCoin method write-up (neobrother "temperature laddering") | WS-A (git, press) | MEASURED / (S) — **T3 wide diffusion** |
| 2026-02 → 04 | Bucket ladder 7 → 9 → 11; cities 14 → 38 (March) → 51 (April); 62 and 68 new repos in March/April | M4, WS-A | MEASURED |
| 2026-03-30 | Weather taker fee 0.05·p(1−p), maker rebate 25% | A1, WS-C (docs changelog) | MEASURED (docs) |
| 2026-04-06 / 04-15 | Roissy (LFPG) sensor tampering; bets paid 14 k$ / 20 k$ | A3 (Bloomberg/NPR/CNN 2026-04-23) | (S) |
| 2026-05-28 | Taker-rebate program | WS-C | MEASURED (docs) |
| 2026-05-29 | `jattree/weather-edge` post-mortem: calibrated-ensemble bot, simulated −13.9%/trade, "the market's probabilities were better on every measure" | Weather V1 spec C12, WS-A | (S) |
| **2026-08-22** | Settlement template → NOAA weather.gov for events created from this date (Jinan/Taipei stay WU); WU clarification 08-04; NOAA fallback clause 08-28 | WS-A (gamma, simmer-sdk PR #341) | MEASURED |
| 2026-09 | Receipt wallets still positive (Bilberry +46.8k in Sep; HighTempTation +15–28k/month since June); NYC/London event volume ≈ 63–79 k$ | M7, M4, A1/A3 | MEASURED |

**Decay vs variance.** The launch-quarter favourite bias has a CI excluding zero (−54% to −15%) and disappears in every later quarter; the NYC year-over-year Brier improvement uses the same months, so seasonality is controlled; the first-cohort P&L decline is accompanied by a collapse of weather *position counts* (activity exit), which variance cannot produce. Residual confounds: weather-regime differences between 2025 and 2026, ladder changes (which bias the Brier comparison *against* finding improvement), and trader migration (gopfan2's whole wallet stays active). 2026Q1 shows a transient positive favourite return at D−1 (+20.6% [+4.7, +36.6]) coinciding with the ladder change: **mispricing appears at mechanism changes and decays within 1–2 quarters** (two episodes; INFERRED, LOW).

**Causal attribution.** PUBLICATION_DATE: niche 2025-05-07 (16★ analysis repo, ≈ 2 months after the decay onset), broad 2025-12-30; first-cohort DECAY_START 2025-03 (named-wallet weather P&L; the favourite bias was still −7% in 2025Q2 and gone by 2025Q3); SIMULTANEOUS: first-quarter learning by other participants; later market expansion, fee (2026-03-30), ladder and template changes. Publication cannot have caused the first-cohort decay. For the 2026 wave of bots, competition is plausible but unmeasured. CAUSE_CONFIDENCE: competition/better pricing for the oldest markets MEDIUM; publication LOW.

| Field | Value |
|---|---|
| ID | E7-A WEATHER |
| EDGE / MECHANISM | Pricing daily max/min temperature buckets better than recreational flow, using public forecasts/observations |
| VENUE | Polymarket (international CLOB); owner-declared access, `/api/geoblock` unverified (A1) |
| ECONOMIC PAYER | Recreational takers and naive makers |
| SMALL-CAP ACCESS | Yes technically (tens of $; depth a few k$ per bucket) |
| T_EDGE_START | 2025-01-21 (daily city markets); earlier weather markets from 2024 |
| T_FIRST_RECEIPT | ≤ 2024-09 (weather broadly, M7); 2025-01/02 for daily city markets |
| T_PUBLIC_DISCLOSURE | niche 2025-05-07; broad 2025-12-30/31 |
| T_WIDE_DIFFUSION | 2026-01 → 02 (skills, 768★/319★ repos, crypto press) |
| T_DECAY_START | 2025-03 (first cohort); price-internal bias gone by 2025Q3–Q4 |
| T_EDGE_END | UNKNOWN (mechanism alive) |
| RIGHT_CENSORED | TRUE |
| PRE_DISCLOSURE_LIFETIME | ≈ 11 months (T0 → broad disclosure); first cohort's weather-wide run ≈ 6–7 months (2024-08/09 → 2025-02), of which ≈ 2 months in daily city markets |
| POST_DISCLOSURE_SURVIVAL | ≥ 9 months (right-censored; new-cohort receipts in 2026-09) |
| CURRENT_STATE | Mechanism pays a turning-over cohort; easiest inefficiency decayed; NYC sharper YoY; ≥ 4 mechanics changes in 8 months |
| RECEIPT_EVIDENCE | Strong-but-selected (A1: +87–96k 12m; 36% losers among top 1,050 by volume; median sampled +264 $) |
| DECAY_EVIDENCE | MEASURED (M4 calibration, M7 cohort) |
| PRIMARY_DECAY_MECHANISM | COMPETITION / BETTER_PRICING (oldest markets) + MARKET_DESIGN / ORACLE changes; PLATFORM_GROWTH creates fresh markets |
| CAUSE_CONFIDENCE | MEDIUM (competition, oldest markets); LOW (publication) |
| CAPACITY | Per bucket a few k$; ≈ 100 events/day; per-event volume falling (NYC/London 290 k$ → 63–79 k$) |
| SPEED_REQUIREMENT | Minutes (model runs, observations) |
| RULE / FEE CHANGES | Fee 2026-03-30; ladder 2026-02/04; template 2026-08-22; taker rebates 2026-05-28 |
| CURRENT 2026 EVIDENCE | Post-fee receipts (A1, A3, M7); public calibrated-ensemble post-mortem negative (S) |
| EXPECTED_QUANT_VALIDATION_LATENCY | ≈ 6–8 months to a first powered label (readiness t0 7–10 weeks + 120 dates; Fable Family D); 3–6 years for θ = 0.02 |
| ACTIONABILITY_RATIO / RANGE | τ_rem for a specific frozen rule: LOWER ≈ 3 months (post-change inefficiency half-life; mechanics-change hazard ≈ 1 per 2 months) → **0.4**; CENTRAL 6–12 months → **≈ 1–1.8**; UPPER > 24 months if forecast skill is structural → **> 3** |
| TERMINAL_CLASSIFICATION | **B — DECAY_COMPARABLE_TO_VALIDATION** |
| CHEAPEST CURRENT FALSIFICATION | Owned by the Weather rail (not altered here). Decay-side context only: re-run M4 quarterly across all 51 cities (calibration, favourite return, same-month Brier) |
| REAL_CAPITAL_AUTHORIZED | FALSE |

### 5.B POLYMM / @b00k13 — esports devigged-sportsbook market making (Type I/IV, practitioner edge)

**Chronology**

| Date | Event | Source | Label |
|---|---|---|---|
| 2025-04 → 09 | Esports markets become daily (772 events in 2025-09) | WS-A (gamma) | MEASURED |
| **2026-01-06** | Wallet `0x1c55…84ce` starts trading; `user-pnl` first point 2026-01-07 | A3, M7 | MEASURED — **T1** |
| 2026-01 → 04 | Monthly P&L +2.0k / **+2.5k** / +0.4k / +0.1k; two-leg fill rate 37% → 15% → 5% → 1% | M7; author (A3) | MEASURED / practitioner |
| 2026-01-17 | poly-maker author: "not profitable … increased competition" (another MM bot) | WS-C (git) | MEASURED (repo) |
| 2026-02-18 / 03-30 | Sports fees / Fee Structure V2 (hedge legs taken as taker pay fees; esports inclusion in sports fee UNKNOWN) | WS-C | MEASURED (docs) |
| **2026-03** | P&L drops ≈ ×6–7 (author: +2,506 → +390; `user-pnl`: +2.45k → +0.37k) | M7, author (A3) | MEASURED — **T4** |
| **2026-04-28** | Phase 1 stopped (fill rate 1%) | A3 | practitioner — **T5 (this implementation)** |
| **2026-06-06 / 06-30** | Two blog posts ("other market-making bots are quicker to outbid me"; fill rate 37.4% → 1.0%) | kacho.io (WS-A) | direct — **T2** |
| 2026-07-19 | Code open-sourced (MIT), 105★ / 35 forks at T_NOW | github.com/kachence/polymm (git clone) | MEASURED — T3 (modest) |
| 2026-09-29 | 30 d +130 $; residual niche claim (minor esports) | A3 | MEASURED |

**Decay vs variance.** Fill rate is an operating statistic with thousands of attempts per month; a 37× fall is not sampling noise. **Causal attribution.** DECAY Feb–Apr 2026; PUBLICATION June 2026 (after the end); SIMULTANEOUS: fee rollout. The author attributes it to faster competing bots and fees. CAUSE_CONFIDENCE: COMPETITION MEDIUM (direct symptom), VENUE_FEE_CHANGE LOW-MEDIUM.

| Field | Value |
|---|---|
| ID | E7-B POLYMM |
| EDGE / MECHANISM | Post limit orders 1¢ inside the best bid when devigged sportsbook fair value implies ≥ 5–7% edge; hedge the other side to lock YES+NO < 1 |
| VENUE / PAYER | Polymarket esports / recreational takers and stale limit orders |
| SMALL-CAP ACCESS | Yes (300–3,000 $) — but speed-contested (seconds) |
| T_EDGE_START / T_FIRST_RECEIPT | ≤ 2026-01 (esports daily since 2025-04 → 09) / 2026-01-06 |
| T_PUBLIC_DISCLOSURE / T_WIDE_DIFFUSION | 2026-06-06 / not reached (105★) |
| T_DECAY_START / T_EDGE_END | 2026-02 → 03 / 2026-04 (for this implementation) |
| RIGHT_CENSORED | FALSE for the main edge; residual niche UNKNOWN |
| PRE_DISCLOSURE_LIFETIME | ≈ 3–4 months (T1 → T5); ≈ 2 months at full strength |
| POST_DISCLOSURE_SURVIVAL | **≤ 0** (first post ≈ 6 weeks after the stop and ≈ 3 months after decay began) |
| CURRENT_STATE | Dead at scale; residual ≈ 0–150 €/month claimed (A3) |
| RECEIPT_EVIDENCE | Strong: code + author-declared wallet + monthly blog numbers reconciled with `user-pnl` (A6: +$4,961 vs +$4,973 claimed) |
| DECAY_EVIDENCE | Strong: fill-rate collapse (practitioner) + `user-pnl` monthly (MEASURED) |
| PRIMARY_DECAY_MECHANISM / CAUSE_CONFIDENCE | COMPETITION (MEDIUM); VENUE_FEE_CHANGE (LOW-MEDIUM) |
| CAPACITY / SPEED | Positions ≤ 3 k$ / seconds-level requoting |
| CURRENT 2026 EVIDENCE | ≈ 0 since April (M7) |
| EXPECTED_QUANT_VALIDATION_LATENCY | ≥ 1–3 months, **and not measurable in paper** (fill rate and adverse selection require live queue position) |
| ACTIONABILITY_RATIO / RANGE | Historical from T1: ≈ 3 months / 1–3 months ≈ **1–3 but unmeasurable in shadow**; at T_NOW: **0** |
| TERMINAL_CLASSIFICATION | **C — REAL_BUT_NOT_ACTIONABLE_UNDER_CURRENT_VALIDATION_PROCESS** |
| CHEAPEST CURRENT FALSIFICATION | None needed (dead). Keep as the reference template for maker-edge half-life (≈ 2–3 months) |
| REAL_CAPITAL_AUTHORIZED | FALSE |

### 5.C1 POLYMARKET LIQUIDITY REWARDS — incumbent reward tier T4 (Type III, subsidy)

**Chronology**

| Date | Event | Source | Label |
|---|---|---|---|
| **2022-02-17** (year inferred) | Program starts: weekly epochs, 50,000 USDC + 10,000 UMA | legacy-docs.polymarket.com (WS-C) | (P), year MEDIUM — **T0 = T2 (public by design)** |
| 2023-02-17 | Polymarket open-sources its market-maker keeper (dormant since 2024-03) | github Polymarket/poly-market-maker (WS-C git) | MEASURED |
| 2023-03-15 | dYdX-style quadratic scoring, UMA-funded weekly epochs | Polymarket blog (WS-C) | (P) |
| 2025-03-31 | warproxxx/poly-maker first commit (1,509★ / 492 forks today) | WS-C git | MEASURED — **T3** |
| 2025H2 → 2026 | Polymarket-MM repos created: 16 (2025H2) → 45 / 48 / 46 per quarter (2026) | WS-C (GitHub search) | MEASURED (proxy) |
| 2026-01-17 | poly-maker README: "not profitable and will lose money … increased competition" | WS-C git | MEASURED (repo) |
| 2026-03-17 | March Madness: "$2M+" LR | docs changelog (WS-C) | (P) |
| 2026-04-01 / 04-15 | On-chain pool 30 k$/day / 126–128 k$/day (cohort A frame) | A6 | MEASURED (A6) |
| 2026-04-28 | CLOB V2 + pUSD; "$1M" LR program | changelog, crypto.news (WS-C) | (P)/(S) |
| 2026-07-01 | Cohort B frame: 3,259 recipients, 137 k$ | A6 | MEASURED (A6) |
| 2026-07-05 → 09 | poly-maker V2 rewrite explicitly farms rewards + rebates | WS-C git | MEASURED |
| 2026-08 | $1M crypto-TWAP LR grant, ended 2026-08-31 | PolymarketDevs X, docs (WS-C) | (P) |
| 2026-08 → 09 | Pool 101–112 k$/day; 2.2–2.6k recipients; median payout 4–5 $ | A6 | MEASURED (A6) |

**Decay vs variance.** Within each cohort the share of T4 wallets net positive falls month by month (A: 78 → 62 → 50%; B: 88 → 80 → 75%), but T4 is selected on a high reward *on one day*, so regression to the mean predicts exactly this; **between cohorts (later B vs earlier A) persistence is higher, not lower** (55% positive in all 3 months vs 22%). The pool fell 23% (07-01 → 09-29) while recipients fell 32%, so reward per recipient rose. No evidence of cohort-over-cohort decay; the level moves by documented discretionary step changes.

**Causal attribution.** Budget changes are documented decisions (HIGH that they are discretionary); competition among farmers is asserted by practitioners (LOW-MEDIUM as a cause of lower small-tier net). **Q14 answer:** T4 is an **INCUMBENT_ADVANTAGE on a persistent-but-discretionary subsidy** — the rent is the subsidy (median T4 trading ≈ 0), it accrues to scale/uptime incumbents (being T4 on D0 embeds prior survival; cash ≥ 12–14 k$ is a *lower* bound on capital), and the paying program has existed ≈ 4.6 years. It is neither a Quant strategy candidate at current capital nor a short-lived "temporary harvest" in the observable window.

| Field | Value |
|---|---|
| ID | E7-C1 PM-LR-T4 |
| EDGE / MECHANISM | Resting two-sided liquidity scored by a quadratic distance rule; daily pro-rata subsidy |
| VENUE / PAYER | Polymarket; treasury + sponsors (sponsor-funded pools exist since ≤ 2026-03, WS-C) |
| SMALL-CAP ACCESS | **No net rent below T4** (A6: T1–T3 median net ≈ 0 or negative; frame-weighted 44–49% net positive) |
| T_EDGE_START / T_FIRST_RECEIPT | 2022-02 / A6 cohorts 2026-04 and 2026-07 |
| T_PUBLIC_DISCLOSURE / T_WIDE_DIFFUSION | 2022-02 (by design) / 2025-03 → 2026 (poly-maker; 45–48 repos/quarter) |
| T_DECAY_START / T_EDGE_END | None measurable at program level / none |
| RIGHT_CENSORED | TRUE |
| PRE_DISCLOSURE_LIFETIME / POST_DISCLOSURE_SURVIVAL | 0 / ≥ 4.6 years (program) |
| CURRENT_STATE | 105.7 k$/day on 2026-09-29; B·T4 month 3: 75% net positive, median +4.6k |
| RECEIPT / DECAY EVIDENCE | Strong (320-wallet pre-declared cohorts, on-chain) / pool series + cohort months (A6) |
| PRIMARY_DECAY_MECHANISM / CAUSE_CONFIDENCE | REWARD_BUDGET_CHANGE (discretionary steps) HIGH that it happens, direction mixed; COMPETITION for small tiers LOW-MEDIUM |
| CAPACITY / SPEED | ≈ 100–110 k$/day for all makers; T4 median 3–8 k$/month per wallet / moderate automation, seconds to pull quotes |
| RULE / FEE CHANGES | Event programs (03-17, 04-28, Aug TWAP); single-sided factor c = 3.0; both sides required outside [0.10, 0.90] |
| EXPECTED_QUANT_VALIDATION_LATENCY | Incumbent persistence: 1 month (A6 pre-registered cohort C, 2026-10-29). **For Quant as an entrant: not measurable in paper** (queue and adverse selection) |
| ACTIONABILITY_RATIO / RANGE | Time ratio ≫ 1 (program years vs 1 month), but access fails → NOT_APPLICABLE |
| TERMINAL_CLASSIFICATION | **H — INACCESSIBLE_FOR_SMALL_QUANT** |
| CHEAPEST CURRENT FALSIFICATION | A6 cohort C on 2026-10-29 (fail if T4 net>0 < 60% or median ≤ 0) |
| REAL_CAPITAL_AUTHORIZED | FALSE |

### 5.C2 POLYMARKET MAKER REBATES — fee-share program (Type III)

**Chronology**

| Date | Event | Source | Label |
|---|---|---|---|
| **2026-01-05** | Taker fees on 15-min crypto markets; "daily USDC rebates … funded by taker fees" | docs changelog (WS-C) | (P) — **T0 = T2** |
| 2026-01-16 | Dominant recipient `0x2d50…ea54` first MAKER_REBATE; docs update the funding schedule | M2; changelog | MEASURED |
| 2026-02-18 | Rebates computed per market | changelog (WS-C) | (P) |
| 2026-03-02 | Rebate payer: 77.8 k$ to 874 recipients | A6 | MEASURED (A6) |
| 2026-03-06 / 03-30 | Fees on all crypto / Fee Structure V2 (all categories except geopolitics) | changelog | (P) |
| 2026-04 → 09-01 | Payer total 0.84–2.30 M$/day, of which the dominant recipient 0.65–1.93 M$/day; all others 0.15–0.40 M$/day | M2 | MEASURED |
| 2026-05-28 | Taker-rebate program; referral payouts cut (30%/10% gross → 10%/5% net) | docs (WS-C) | (P) |
| 2026-07-10 | Sports taker fee 0.03 → 0.05, sports maker rebate 25% → 15% | changelog (WS-C) | (P) |
| 2026-06-11 → 07-19 | FIFA World Cup; broad pool peaks ≈ 0.37–0.40 M$/day; platform volume −36.7% Jul → Aug | M2; The Block 2026-09-02 (WS-C) | MEASURED / (S) |
| **2026-09-10** | Dominant recipient's last payment (165.3 M$ total since 01-16) | M2 | MEASURED — **counterparty-specific discontinuity** |
| 2026-09-15 / 09-29 | Payer total 162 k$ / 124 k$; recipients 4,727 / 4,396 | A6, M2 | MEASURED |

**Decay vs variance.** Excluding the dominant recipient, the pool shows seasonality (World Cup) and a ≈ 30% September decline — too short to separate from post-World-Cup and crypto-volume effects (TWAP resolution 2026-08-07 cut 5-min BTC cycle volume ≈ 40%, WS-C (S)). **Causal attribution.** The aggregate fall (≈ 13× from 07-01, ≈ 8× from 09-01) is one recipient's stream ending (MEASURED). Its cause is UNKNOWN: that recipient's exit cannot be distinguished from a category-specific rule change affecting it (its stream began 11 days after the 15-min-crypto rebate launch and ended ≈ 5 weeks after the 2026-08-07 crypto TWAP change; no changelog entry). CAUSE_CONFIDENCE LOW for any specific explanation. Documented rate cuts (sports 07-10; finance 50% → 25% at an unknown date) are RULE_CHANGE (HIGH).

| Field | Value |
|---|---|
| ID | E7-C2 PM-MAKER-REBATES |
| EDGE / MECHANISM | Share (15–25%) of taker fees paid pro rata to fee-curve-weighted maker volume, per market |
| VENUE / PAYER | Polymarket / takers via fees |
| SMALL-CAP ACCESS | Proportional to own maker volume; a 300–3,000 $ maker earned 5 $/30 d (A3); A6: rebates change the share of net-positive wallets by only 0–5 points |
| T_EDGE_START / T_FIRST_RECEIPT / T_PUBLIC_DISCLOSURE | 2026-01-05 / 2026-01-16 / 2026-01-05 (docs) |
| T_WIDE_DIFFUSION | 2026-07 (poly-maker V2 targets "the new maker-rebate program") |
| T_DECAY_START / T_EDGE_END | Broad pool: none established (−30% in Sep, confounded) / none |
| RIGHT_CENSORED | TRUE |
| POST_DISCLOSURE_SURVIVAL | ≥ 9 months |
| CURRENT_STATE | 124 k$/day to 4,396 recipients (top-10 share 20.5%) |
| RECEIPT / DECAY EVIDENCE | On-chain payments (strong) / by-recipient decomposition (strong for the discontinuity, weak for trend) |
| PRIMARY_DECAY_MECHANISM | COUNTERPARTY-SPECIFIC DISCONTINUITY (cause UNKNOWN) + RULE_CHANGE (category rates) |
| CAUSE_CONFIDENCE | LOW (discontinuity cause); HIGH (documented rate cuts exist) |
| EXPECTED_QUANT_VALIDATION_LATENCY / ACTIONABILITY | Not a standalone edge: NOT_APPLICABLE |
| TERMINAL_CLASSIFICATION | **H — INACCESSIBLE_FOR_SMALL_QUANT** in the same sense as C1: **no net rent at small scale** (rebates scale with own maker volume; a 300–3,000 $ maker earned 5 $/30 d; A6: rebates change the share of net-positive wallets by 0–5 points). The aggregate "collapse" reading is corrected here: a program-wide regime break for ordinary makers is not supported by the data. |
| CHEAPEST CURRENT FALSIFICATION | Re-run M2 monthly: if the non-dominant pool falls > 50% from its Aug level for two consecutive months, record a program regime change |
| REAL_CAPITAL_AUTHORIZED | FALSE |

### 5.D SETTLEMENT LIQUIDITY at 0.999 (Type II, structural liquidity premium)

**Chronology**

| Date | Event | Source | Label |
|---|---|---|---|
| 2021-08 → 2022-10 | UMA CTF adapter; move to Optimistic Oracle V2 | github Polymarket/uma-ctf-adapter (WS-B) | MEASURED (repo) |
| 2023-04-19 | Clients support ticks 0.1 / 0.01 / **0.001** / 0.0001 (dynamic-tick activation date UNKNOWN) | clob-client PR #86 (WS-B) | MEASURED (repo) |
| 2023-05-31 | Default liveness 2 h ("currently about 2 hours") | uma-ctf-adapter v3.0.0 (WS-B) | MEASURED (repo) |
| inception → 2025-12 | Top-10 short-horizon settlement-liquidity providers 104 k$, median 0.04 $/trade, hold 1–2 h; disputes excluded | Gebele & Matthes 2605.31431 Table 6 (A5, WS-B) | (P) — **T1** |
| late 2024 → | "Frontier-implied rates compress" for *long-dated* near-certain bonds (median maturity 144 → 38.5 days) | 2605.31431 §5.1 (WS-B) | (P) |
| **2025-01** | ≥ 0.999 gross = 0.100%, 78% of near-certain notional at the floor | M5 | MEASURED — earliest measured T0 |
| 2025-03-24/27; 2025-07-01 | Ukraine-minerals and Zelensky-suit resolution controversies (hits on near-certain holders) | CoinDesk, Decrypt (WS-B) | (S) |
| 2025-04; 2026-01 | Samples with in-play "0.999" losses (−1.48%, −0.53% net) | M5 | MEASURED |
| 2025-08-06 / 08-12 | UMIP-189 managed proposers; dispute rate ≈ 1.3% (UMA blog) | The Block, UMA (WS-B) | (S)/(P) |
| **2025-12-04** | "bonding 101 on polymarket … buying above 95c" (broad social publicity) | x.com/probabilitygod (WS-B) | (S) — **T2/T3 (practitioner)** |
| 2026-01-05 | Fees ∝ p(1−p) ≈ 0 at 0.999 | docs (WS-B) | (P) |
| **2026-05-29** | Gebele & Matthes arXiv: first detailed reproducible description | arxiv.org/abs/2605.31431 | (P) — **T2 (academic)** |
| 2026-08-07 / 09-28 | Crypto up/down auto-resolution (TWAP); API publishes expected settlement times | changelog (WS-B) | (P) |
| 2026-07 / 09 | Holds shorten to 0.55–0.64 h; gross still 0.100% | M5 | MEASURED |
| 2026-09-29 | A5 slices +0.14–0.15% (3 losers / ≈ 11,000 fills) | A5 | MEASURED (A5) |

**Decay vs variance.** Gross at ≥ 0.999 equals the tick floor by construction, so decay of the per-fill premium is **not testable** with this design; what is measured is that the floor trade occurred in all 8 windows (≈ 20 months) with a stable floor share (63–89%). Net varies only with rare losing fills. **Causal attribution.** Any premium decay is mechanically bounded by the tick (≥ 0.1% per fill while the tick and resolution delay exist); faster resolution paths shorten holds (MEDIUM). **Q12 answer:** the premium is **compensation for impatience / capital lock, floored by the 0.001 tick — not an information edge**; competition acts on queue share and capacity, not on the per-fill premium. The economic risk is the tail rate of "near-certain but undecided" fills and disputes, and the unmeasured newcomer queue share.

| Field | Value |
|---|---|
| ID | E7-D SETTLEMENT-0.999 |
| EDGE / MECHANISM | Resting bid at 0.999 on already-decided claims; redeem at 1 after resolution |
| VENUE / PAYER | Polymarket / holders who want immediate cash |
| SMALL-CAP ACCESS | Yes (fills of a few to a few hundred $); newcomer queue share UNKNOWN |
| T_EDGE_START / T_FIRST_RECEIPT | ≤ 2025-01 (MEASURED; likely since dynamic ticks, UNKNOWN) / ≤ 2025-12 (academic top-10) |
| T_PUBLIC_DISCLOSURE / T_WIDE_DIFFUSION | 2025-12-04 (practitioner) and 2026-05-29 (academic) / 2025-12 ("bonding" publicity) |
| T_DECAY_START / T_EDGE_END | None for the 0.999 premium / none |
| RIGHT_CENSORED | TRUE |
| PRE_DISCLOSURE_LIFETIME / POST_DISCLOSURE_SURVIVAL | ≥ 11 months / ≥ 9 months (practitioner), ≥ 4 months (academic) |
| CURRENT_STATE | Alive; gross 0.1%; holds ≈ 0.6–3 h; pooled 2025–26 naive-window net −0.115% because of in-play losses |
| RECEIPT_EVIDENCE | Academic actor-level (disputes excluded) + two A5 slices + 8 M5 windows |
| DECAY_EVIDENCE | None (floor) |
| PRIMARY_DECAY_MECHANISM | NONE observed; hazards: TICK_CHANGE (0.0001 exists in client types), ORACLE/SETTLEMENT speed-up (instant resolution would remove the window) |
| CAUSE_CONFIDENCE | NOT_APPLICABLE for decay (no decay testable by design); tick-floor bound is mechanical |
| CAPACITY | Small: 0.1% of ≈ 0.3–4.6 M$ floor notional per sampled window; 741–4,402 distinct trade-record wallets (buyers or sellers) per window |
| SPEED_REQUIREMENT | Queue priority at 0.999 (seconds–minutes), not milliseconds; crypto up/down excluded |
| RULE / FEE CHANGES | Fees ≈ 0 at 0.999; faster resolution (2026-08/09) |
| CURRENT 2026 EVIDENCE | 2026-04/07/09 windows net +0.100% with 0 losers |
| EXPECTED_QUANT_VALIDATION_LATENCY | **≈ 1–2 months** (V1: 30-day historical census in days + shadow queue proxy 2–4 weeks) |
| ACTIONABILITY_RATIO / RANGE | LOWER ≈ 6 (τ_rem 12 months if a tick/resolution change arrives within a year / 2 months), CENTRAL ≥ 12, UPPER ≫ 12 |
| TERMINAL_CLASSIFICATION | **A — DURABLE_BEYOND_VALIDATION** for the premium-paying mechanism (observed in every window for ≈ 20 months; L_val 1–2 months). Not a statement about economics: net for a post-determination resting-bid newcomer and its queue share are unmeasured, and A5 bounds value at ≤ ≈ €90/month at €5k before tails. (The integrity review argued for D; retained as A because persistence of the mechanism is the best-evidenced property, while net and queue share are validation questions.) |
| CHEAPEST CURRENT FALSIFICATION | A5's 30-day census, **restricted to fills after an observable event-end / determination timestamp**, including disputed markets; reject if pooled net ≤ 0 or newcomer queue share < 5% |
| REAL_CAPITAL_AUTHORIZED | FALSE |

### 5.E NEGRISK / COMPLETE-SET ARBITRAGE (Type IV, mechanical arbitrage)

**Chronology**

| Date | Event | Source | Label |
|---|---|---|---|
| **2023-11-28** | NegRiskAdapter `0xd91E…5296` bytecode first on Polygon (block 50,505,403) | on-chain (WS-B) | MEASURED — **T0** |
| ≤ 2024-07 | Median profit per conversion ≈ 1 $ | Gebele et al. 2608.00666 Fig. 6 (A5) | (P) — **T1** |
| 2024-04 → 2025-04 | Saguillo window (39.59 M$ gross construct; 291 k$ mechanism-linked) | A2, A5 | (P) |
| 2024-10-20 → 2025-03 | #8 marksman monthly net cash +1.7k, **+10.3k**, +3.3k, +1.9k, +0.1k, +0.1k | A5 | MEASURED (A5) |
| **late 2024 → 2025** | Median profit per conversion ≈ 0.20 $ | 2608.00666 | (P) — **T4** |
| 2025-01-24 | Early OSS arbitrage repo: "abandoned" given thin liquidity | WS-B | (S) |
| 2025-03 → 07 | 3 of 5 identified top Saguillo accounts stop trading | A3 | MEASURED (A3) |
| **2025-08-05** | Saguillo arXiv — first detailed reproducible $ description | arxiv 2508.03474 | (P) — **T2** |
| 2025-08-21/22 | Flashbots post; DL News, Cryptopolitan ("$40M") | WS-B | (S) — broad publicity |
| 2025-08-05 → 12-31 / 2026 | Repos mentioning "negrisk": 4 before → 94 → 397; "polymarket arbitrage": ≈ 35 → 88 → 886 | WS-B (GitHub search) | MEASURED (proxy) — **T3** |
| early 2026 | ≈ 0.08 $ per conversion; NO-side episodes median 7.99 s | 2608.00666 | (P) |
| 2026-03-30 | Taker fees on politics etc.; geopolitics fee-free | changelog | (P) |
| 2026-04-29 / 07-17 | New NegRisk adapter; old adapter's relayer support deprecated | on-chain, changelog (WS-B) | MEASURED |
| 2026-09 | 45 of 525 top monthly accounts convert — mostly market makers recycling inventory | A5 | MEASURED (A5) |

**Decay vs variance.** A monotone fall across three periods in a large conversion sample, plus a 100× fall in one pure converter's monthly cash within 3 months, while the venue was fee-free: not variance. **Causal attribution.** DECAY_START (late 2024) precedes PUBLICATION (2025-08-05) by ≈ 9 months and fees (2026) by > 12 months: COMPETITION among existing bots is the best-supported cause (MEDIUM); publication may have accelerated the *residual* compression (0.20 → 0.08 $) together with fees (LOW; repo counts are a diffusion proxy, not competitors).

| Field | Value |
|---|---|
| ID | E7-E NEGRISK |
| EDGE / MECHANISM | Buy NO legs / YES baskets when Σ prices + fees < payout; convert via adapter or hold to settlement |
| VENUE / PAYER | Polymarket / takers who move one outcome without repricing the rest |
| SMALL-CAP ACCESS | Converter side: seconds-level race (no); YES-basket side: microscopic (≈ 700 $/month platform-wide in 2024–25, A5) |
| T_EDGE_START / T_FIRST_RECEIPT | 2023-11-28 / ≤ 2024-07 |
| T_PUBLIC_DISCLOSURE / T_WIDE_DIFFUSION | 2025-08-05 / 2025-08 → 2026 |
| T_DECAY_START / T_EDGE_END | late 2024 / not ended — compressed to ≈ 0.08 $/conversion (seconds-level) by early 2026 |
| RIGHT_CENSORED | TRUE (compressed to ≈ 0.08 $/conversion, not ended; alive as a market-maker inventory tool) |
| PRE_DISCLOSURE_LIFETIME | ≈ 20 months (T0 → T2), of which the rich phase ≈ 8–12 months |
| POST_DISCLOSURE_SURVIVAL | ≈ 5–8 months of an already-compressed residual |
| CURRENT_STATE | Inventory tool for market makers; no standalone 2026 profit established |
| RECEIPT / DECAY EVIDENCE | Strong (academic + independent cash reconstructions) / strong (per-conversion series, account months) |
| PRIMARY_DECAY_MECHANISM / CAUSE_CONFIDENCE | COMPETITION (automation) MEDIUM; later VENUE_FEE_CHANGE + PUBLICATION_DIFFUSION LOW |
| CAPACITY / SPEED | ≈ 0.3 M$/year platform-wide mechanism-linked (2024–25), top-10 ≈ 75% / seconds |
| EXPECTED_QUANT_VALIDATION_LATENCY | ≈ 1–2 months (high-frequency) — but the residual requires execution infrastructure outside the paper/shadow authority |
| ACTIONABILITY_RATIO / RANGE | Had Quant discovered it at T2: residual 5–8 months / 1–2 months ≈ 3–8, on an edge already worth ≈ 0.08–0.20 $/conversion and speed-bound → economically ≈ 0. At T_NOW: 0 |
| TERMINAL_CLASSIFICATION | **H — INACCESSIBLE_FOR_SMALL_QUANT** (the residual is a seconds-level multi-leg race needing execution infrastructure outside paper/shadow authority; validation latency, ratio 3–8 at T2, was not the binding constraint) |
| CHEAPEST CURRENT FALSIFICATION | A5-S1: 24 h of 1-min NegRisk snapshots; reject if Σ(executable YES-basket gap × depth) < 5 $/day |
| REAL_CAPITAL_AUTHORIZED | FALSE |

### 5.F BOX OFFICE — opening-weekend brackets (Type I, slow public information)

**Chronology**

| Date | Event | Source | Label |
|---|---|---|---|
| 2023-09/10 (WS-A) → 2025-09 | Sporadic tentpole markets (first box-office-tagged event in M3: 2023-11-10; 35 usable events; Box Office Mojo then The Numbers); winner already at 0.95 by Sat 14:00 ET | M3, WS-A | MEASURED |
| 2024-11 → 2026-03 | Big.Chungus box-office activity (then fades) | A4 | MEASURED (A4) |
| **2025-10-14** | Templated weekly regime begins (Black Phone 2), resolving on The Numbers finals incl. Thursday previews | gamma (WS-A) | MEASURED — **T0** |
| 2025-10-15 / 10-19 | The-Joker and fanat12 first P&L points | A4 | MEASURED (A4) — **T1** |
| 2025Q4 | Winner median Sat 14:00 = 0.78; Saturday-favourite diagnostic +25% [+2.4, +44.4] | M3 | MEASURED |
| 2026-01-29 | Only open-source artefact: 1★ backtest repo | WS-A | MEASURED |
| 2026-03-30 | Culture fee 0.05·p(1−p) | A1, WS-C | (P) |
| 2026-06-16 | denzeldumfries first point; +4.8k → +13.1k/month by Sep | A4 | MEASURED (A4) |
| 2026Q3 | Winner median Sat 14:00 = 0.78, Sun 14:00 = 0.98; Saturday-favourite diagnostic −14% [−35, +5]; median event volume 83 k$ (Q2: 208 k$) | M3 | MEASURED |
| 2026-09 | Three wallets still positive (A4) | A4 | MEASURED (A4) |
| — | **No guides, press, skills or bots found** | WS-A | MEASURED (absence) |

**Decay vs variance.** No trend in absorption at any anchor (|z| < 0.6). The naive Saturday-favourite diagnostic drifts down (ρ = −0.14, z = −1.47) but the pre-declared trend test is not significant (z −1.47, n ≈ 25/quarter; a post-hoc 2025Q4-vs-2026Q3 contrast would be ≈ 2.6 SE and is not used as a test); the 2026Q3 film mix (smaller films, 83 k$ median volume) is a competing explanation. **Causal attribution.** No decay established; no disclosure found. CAUSE_CONFIDENCE: UNKNOWN.

**§19 key question.** The Sunday estimate is absorbed within ≈ 3 h (Sunday-favourite return ≈ 0 in every quarter); the Saturday window carries residual uncertainty that is partly genuine (bracket-boundary cases, A4). Over 12 months of the templated regime, **nothing shows the niche being competed away**: consistent with a *structural* delay in absorbing Friday-actuals-based projections in a small, undiscussed market. But 12 months is short: an **undercompeted niche** that has not yet been discovered would look identical. The evidence cannot discriminate; the absence of diffusion is the main reason for durability, and it is not guaranteed.

| Field | Value |
|---|---|
| ID | E7-F BOX-OFFICE |
| EDGE / MECHANISM | Update bracket prices on Thursday previews / Friday actuals / Sunday estimates faster than the recreational flow |
| VENUE / PAYER | Polymarket culture / recreational film bettors |
| SMALL-CAP ACCESS | Yes; ≈ 1–5 k$ per event (A4) |
| T_EDGE_START / T_FIRST_RECEIPT | 2025-10-14 / 2025-10-15 |
| T_PUBLIC_DISCLOSURE / T_WIDE_DIFFUSION | NOT FOUND / NOT REACHED |
| T_DECAY_START / T_EDGE_END | None measured / none |
| RIGHT_CENSORED | TRUE (minimum observed lifetime ≈ 11.5 months) |
| PRE_DISCLOSURE_LIFETIME / POST_DISCLOSURE_SURVIVAL | ≥ 11.5 months / NOT_APPLICABLE |
| CURRENT_STATE | Alive; receipts in 2026-09; volume per event lower in Q3 |
| RECEIPT_EVIDENCE | Good (A4: 3 active wallets, activity-selected sample 34% whole-wallet losers) |
| DECAY_EVIDENCE | None significant (M3) |
| PRIMARY_DECAY_MECHANISM / CAUSE_CONFIDENCE | None established / UNKNOWN; watch: COMPETITION, CAPACITY (volume) |
| CAPACITY / SPEED | Winning bracket 25–30 k$ volume per film-week; a few k$ per event / hours |
| RULE / FEE CHANGES | Fee 2026-03-30 only |
| CURRENT 2026 EVIDENCE | M3 anchors through 2026-09-25; A4 receipts |
| EXPECTED_QUANT_VALIDATION_LATENCY | **Historical replay (falsification only): days** (MDE ≈ 0.13/$ on the ≈ 112–117 opening weekends of the templated regime; lower only if other box-office families are admissible). **Prospective validation: ≈ 9–22 months** for +10%/$; ≈ 4 months only for +25%/$ |
| ACTIONABILITY_RATIO / RANGE | Prospective: LOWER ≈ 0.3 (τ_rem 6 months / 22), CENTRAL ≈ 1 (12–24 / 9–22), UPPER > 3. Historical replay: ≫ 1 for large effects |
| TERMINAL_CLASSIFICATION | **D — PERSISTENCE_UNKNOWN** (no decay measured; lifetime and prospective validation of similar order) |
| CHEAPEST CURRENT FALSIFICATION | A4's strict-timestamp replay over the full templated regime (2025-10-14 → T_NOW), reported per quarter so the same run is both falsification and decay series |
| REAL_CAPITAL_AUTHORIZED | FALSE |

### 5.G TWEET COUNTS — Elon Musk post-count buckets (Type I; with mention markets as sub-control)

**Chronology**

| Date | Event | Source | Label |
|---|---|---|---|
| **2024-05-03** | First weekly count event (0.49 M$) | gamma (WS-A, M6) | MEASURED — **T0** |
| 2024-11-28 | Earliest P&L points of the later winners (API series floor) | A4 | MEASURED (A4) — T1 ≤ |
| 2025-01-17 | Counting rules formalised; xtracker.io as resolution source | gamma (WS-A) | MEASURED |
| 2025-01 → 09 | Family volume 17–41 M$/month | M6 | MEASURED |
| 2025-07-11 | Community-repost clause added | gamma (WS-A) | MEASURED |
| 2025-10 → 11 | Tracker moves to xtracker.polymarket.com (exact day UNKNOWN) | WS-A | MEASURED (interval) |
| **2025-11 → 2026-01** | Volume 114 → 173 → **240 M$/month (peak)** | M6 | MEASURED |
| 2026-01 | noovd and 0xecc stop after losing months (−183k, −261k); family volume peaks (240 M$) | A4, M6 | MEASURED |
| 2026-02-16 | Simmer AI-agent "polymarket-elon-tweets" skill | WS-A (git) | MEASURED |
| **2026-03-19** | Polymarket's own "Tweet Quant" newsletter: buy NO at 10–20%, 92.8% win rate (backtest) | news.polymarket.com (A4, WS-A) | (S) — **T2 (first reproducible method)** |
| 2026-03-30 | Fee rate 0.04 on new events | A4, WS-C | (P) |
| 2026-04 | failstober stops; sb911 celebrated (+106k/month) — now −31.4k lifetime | A4 | MEASURED (A4) / (S) |
| 2026-07 | Annica's last month (+16k) — last of the four large winners | A4 | MEASURED (A4) |
| 2026-09 | 31 M$/month (−87% from peak); small wallets +2–4k/month | M6, A4 | MEASURED |

Mention markets (sub-control): first events 2024-06-20; specialist receipts 2024-08 → 2025-01; 12-month `user-pnl` ≤ 0 for 4 of 5 specialists (A4); listings ≈ 3,000/month by mid-2026 but volume per market ≈ 60 k$ (2024) → ≈ 1.2 k$ (Aug–Sep 2026) (WS-A) — lifetime ≈ 6 months, then fragmentation.

**Decay vs variance.** A −87% volume fall and the exit of all four large winners (three by 2026-04, the fourth after 2026-07) are not variance. **Causal attribution.** Within Jan–Apr 2026: volume peak and two exits after losses (Jan), agent skill (Feb 16), official newsletter method (Mar 19), category fee (Mar 30), the largest winners' P&L falling (Mar–Apr: failstober −26k in March, Annica +289k in April after +984k in March). **Large-winner decay (≈ 2026-03/04) coincides with the first reproducible disclosure and the fee**; it did not clearly precede them. CAUSE_CONFIDENCE: LOW for every single cause (fee, participation collapse, competition, publication all coincide).

| Field | Value |
|---|---|
| ID | E7-G TWEET-COUNT |
| EDGE / MECHANISM | Two-sided making / late NO on buckets the counter's pace makes unreachable |
| VENUE / PAYER | Polymarket culture / lottery-bucket buyers |
| SMALL-CAP ACCESS | Yes for the residual |
| T_EDGE_START / T_FIRST_RECEIPT | 2024-05-03 / ≤ 2024-11 |
| T_PUBLIC_DISCLOSURE / T_WIDE_DIFFUSION | 2026-03-19 (official method) / 2026-02 → 03 |
| T_DECAY_START / T_EDGE_END | ≈ 2026-03/04 (large-winner P&L; volume from 2026-02) / UNKNOWN (large winners gone by 2026-07; capacity −87%) |
| RIGHT_CENSORED | TRUE (mechanism alive at −87% capacity; trader exits are not proof that it ended) |
| PRE_DISCLOSURE_LIFETIME | ≈ 22 months (T0 → T2); high-volume winner era ≈ 12 months (2025-01 → 2026-01) |
| POST_DISCLOSURE_SURVIVAL | ≈ 0–4 months for the large edge; ≥ 6 months for the residual |
| CURRENT_STATE | Residual small (EffyBig ≈ 2–4k/month; 0xf14e +8.6k in 10 weeks); several "stars" are accounting artefacts (X2) |
| RECEIPT / DECAY EVIDENCE | Strong (whole-wallet `user-pnl`) / strong (volume, exits) |
| PRIMARY_DECAY_MECHANISM / CAUSE_CONFIDENCE | Mixed: VENUE_FEE_CHANGE + PLATFORM/participation decline + COMPETITION + PUBLICATION / LOW |
| CAPACITY / SPEED | 1–2 M$ weekly events now / maker variant seconds; late-NO variant slow |
| EXPECTED_QUANT_VALIDATION_LATENCY | Weekly/2-day events: prospective ≈ 3–9 months; historical replay days |
| ACTIONABILITY_RATIO / RANGE | Large edge at T_NOW: 0. Residual: CENTRAL ≈ 1 (τ_rem 3–9 months / 3–9) |
| TERMINAL_CLASSIFICATION | **C — REAL_BUT_NOT_ACTIONABLE_UNDER_CURRENT_VALIDATION_PROCESS** (the large 2025 edge ended before discovery); residual would be E |
| CHEAPEST CURRENT FALSIFICATION | A4's 12-event replay of dead-bucket NO bids vs xtracker pace; falsified if dead-bucket asks < 0.02 within 1 h |
| REAL_CAPITAL_AUTHORIZED | FALSE |

### 5.H HYPERLIQUID HLP — protocol backstop vault (Type II structural, delegated)

**Chronology**

| Date | Event | Source | Label |
|---|---|---|---|
| **2023-05-10** | Vault inception; P&L public from day 1 | M1 | MEASURED — **T0 = T1 = T2** |
| 2023H2 → 2024H1 | Ex-best-period annualised ≈ 136–137%; median AV 7 → 84 M$ | M1 | MEASURED |
| **2024H2** | Median daily return 13 → 6 bp; ex-best 23%; AV 179 M$ | M1 | MEASURED — **T4** |
| 2025-03-12 / 03-26 | ETH-whale loss ≈ 4 M$; JELLY incident | The Block (WS-B) | (S) |
| 2025-05-05 | Fee schedule change (taker 0.035% → 0.045%) | Hyperliquid X / PANews (WS-B) | (P)/(S) |
| 2025-09 | TVL peak ≈ 604 M$ | CoinGecko (WS-B) | (S) |
| 2025-10-10/11 | Crash windfall: +41.4 M$ (period to 10-15, 9.7%) | M1 | MEASURED |
| 2025-11-12 | POPCAT attack −4.9 M$ | CoinGecko (WS-B) | (S) |
| 2026-01-31 → 02-04 | Windfall +18.8 M$ (7.0%) | M1 | MEASURED |
| **2026H1** | Ex-best annualised **0.2%** | M1 | MEASURED — **T5 (excess over lending)** |
| 2026-08 | "yields near zero"; lending sub-strategy planned | blog.1token (WS-B) | (S) |
| 2026-09-29 | API APR 4.0%; TVL ≈ 183–202 M$ | M1, A5 | MEASURED |

**Decay vs variance.** Quarterly medians fall with a tight log-linear fit (half-life 5.1 months, CI 4.0–7.2) across 12 quarters; not variance. **Causal attribution.** AV rose ≈ 60× while dollar P&L per period stayed flat (elasticity −0.98): CAPACITY_SATURATION / dilution (MEDIUM; collinear with time); maturing external market making ("order book liquidity mature", (S)) BETTER_PRICING (LOW); volatility regime drives the episodic part (UNDERLYING_REGIME, MEDIUM).

| Field | Value |
|---|---|
| ID | E7-H HLP |
| EDGE / MECHANISM | Pro-rata share of protocol market making + liquidation backstop |
| VENUE / PAYER | Hyperliquid / liquidated leveraged traders, takers |
| SMALL-CAP ACCESS | Yes (deposit; 4-day lock) — delegated, not run by Quant |
| T_EDGE_START / T_FIRST_RECEIPT / T_PUBLIC_DISCLOSURE | 2023-05-10 (all three) |
| T_WIDE_DIFFUSION | 2024H1 (AV 7 → 84 M$) |
| T_DECAY_START / T_EDGE_END | 2024H2 / 2025H2–2026H1 for excess over lending (episodic crash-insurance payoff remains) |
| RIGHT_CENSORED | FALSE (excess base return); TRUE (episodic payoff) |
| PRE_DISCLOSURE_LIFETIME / POST_DISCLOSURE_SURVIVAL | 0 / ≈ 14–18 months before decay start; ≈ 24–36 months to cash-like |
| CURRENT_STATE | Crash insurance with ≈ cash-like base |
| RECEIPT / DECAY EVIDENCE | Strong (on-chain vault) / strong (M1) |
| PRIMARY_DECAY_MECHANISM / CAUSE_CONFIDENCE | CAPACITY_SATURATION / PLATFORM_GROWTH_DILUTION (MEDIUM) |
| CAPACITY / SPEED | Large / none (delegated) |
| RULE / FEE CHANGES | 2025-05-05 fees; leverage caps after 2025-03 |
| EXPECTED_QUANT_VALIDATION_LATENCY | ≥ 12–24 months to separate excess return from lending (episodic payoff) |
| ACTIONABILITY_RATIO / RANGE | Return half-life ≈ 5 months / ≥ 12 months ⇒ **< 0.5** |
| TERMINAL_CLASSIFICATION | **C — REAL_BUT_NOT_ACTIONABLE_UNDER_CURRENT_VALIDATION_PROCESS** |
| CHEAPEST CURRENT FALSIFICATION | A5: 24-month daily excess over Aave USDC; reject as repeatable edge if median monthly excess ≤ 0 and > 70% of profit from ≤ 2 episodes (M1 already shows 82–101% from one period per half-year since 2025H2) |
| REAL_CAPITAL_AUTHORIZED | FALSE |

### 5.I KALSHI MAKER ECONOMICS (Type II, market-design / behavioural rent)

**Chronology**

| Date | Event | Source | Label |
|---|---|---|---|
| 2021 → 2025-04 | Makers −9.64%, takers −31.46%; makers ≥ 50¢ +2.6% (+2.09% in replication) | Bürgi-Deng-Whelan (A2); replication README (WS-B) | (P) — T0 ≤ 2021 |
| after 2025-04 | Maker fee on selected series (flat 0.25¢) | karlwhelan.com; replication (WS-B) | (P)/(S) |
| 2025-07-01 | Maker fee formula 0.0175·C·P(1−P) on selected series | InGame 2025-07-07 (WS-B) | (S) |
| 2025-09-15 | Liquidity Incentive Program (start from search summary only) | WS-B/WS-C | (S) |
| **2026-01** | Bürgi-Deng-Whelan working paper — first detailed public description | GWU WP 2026-001 (A2) | (P) — **T2** |
| 2025-05 → 2026-06 | Makers ≥ 50¢ +2.40% gross; fee-treatment effect −0.0016 (s.e. 0.0064); 41% of slope change is composition (sports 0.009% → 58.8% of markets) | replication README (WS-B) | (P) |
| 2026-05 | Private liquidity-provider program (up to 50 k$/series/week) | help.kalshi.com (WS-C) | (P) |
| 2026-08-12 | CFTC DMO Letter 26-23 on incentive programs | cftc.gov (WS-C) | (P) |
| 2026-08-19 | Maker fees on resting orders more broadly (search summaries) | WS-C | (S) |
| 2026-09-25 | Quant fast-rail H-004: Kalshi maker markouts in weather/settlement series REJECT (−0.10¢, t −0.55) | `research/fast_rail` registry | MEASURED (Quant) |

**Decay vs variance / causality.** No decay of the gross ≥ 50¢ maker premium through 2026-06 (+2.09% → +2.40%) — right-censored ≥ 5 months after disclosure. Net erosion comes from RULE/FEE changes (HIGH that they exist; effect size on the premium not isolated).

| Field | Value |
|---|---|
| ID | E7-I KALSHI-MAKER |
| EDGE / MECHANISM | Resting liquidity against takers with favourite-longshot beliefs |
| VENUE / PAYER | Kalshi (CFTC DCM) / takers |
| SMALL-CAP ACCESS | **No — US-only** (A2) |
| T_EDGE_START / T_FIRST_RECEIPT / T_PUBLIC_DISCLOSURE / T_WIDE_DIFFUSION | ≤ 2021 / 2021–2025 (aggregate) / 2026-01 / 2026 (replication, press) |
| T_DECAY_START / T_EDGE_END | None measured (gross) / none |
| RIGHT_CENSORED | TRUE |
| PRE_DISCLOSURE_LIFETIME / POST_DISCLOSURE_SURVIVAL | ≥ 4 years / ≥ 5 months |
| PRIMARY_DECAY_MECHANISM / CAUSE_CONFIDENCE | VENUE_FEE_CHANGE on net (HIGH that fees were introduced; size UNKNOWN) |
| CAPACITY / SPEED | Large / moderate (cancel on news) |
| EXPECTED_QUANT_VALIDATION_LATENCY | Weeks (markouts, V1) — Quant already measures it (H-004 rejected one subset; H-010 running) |
| ACTIONABILITY_RATIO / RANGE | Time ≫ 1; access fails |
| TERMINAL_CLASSIFICATION | **H — INACCESSIBLE_FOR_SMALL_QUANT** |
| CHEAPEST CURRENT FALSIFICATION | Fast-rail H-010 (Kalshi markouts by category), already running |
| REAL_CAPITAL_AUTHORIZED | FALSE |

### 5.J NUMERAI CLASSIC — legacy staking vs v3 (Type V, service/tournament payment)

**Chronology**: see §4.8 (payout regimes 2021 → 2026, M8 + WS-C) plus: 2023-11-15 "overly generous" (30.65%/yr) cut announced; 2026-05-05 migration blog; 2026-06-16 → 19 v3 docs, multipliers revised three times in three days (WS-C git); 2026-07-10 v3 migration start; 2026-08-04 blog: v3 + 60-day target for rounds on/after 2026-08-28; rounds 1213–1341 measured by A6: +10.2% NMR over ≈ 6 months, NMR −27% over 12 months.

| Field | Value |
|---|---|
| ID | E7-J NUMERAI |
| EDGE / MECHANISM | Payment for predictions that improve the meta-model; stake burn/payout |
| VENUE / PAYER | Numerai / hedge-fund treasury (NMR) |
| SMALL-CAP ACCESS | Yes (NMR stake; A6: $500–2k stakes 78% positive in NMR, legacy) |
| T_EDGE_START (legacy MMC regime) | 2024-01-02 |
| T_FIRST_RECEIPT / T_PUBLIC_DISCLOSURE | Per-round public payouts / rules public by design |
| T_WIDE_DIFFUSION | NOT_APPLICABLE (tournament) |
| T_DECAY_START / T_EDGE_END | Payout factor diluted 0.14 → 0.09 (2024 → 2026, stake growth) / **legacy regime ends at round ≈ 1343 (2026-08-28)** |
| RIGHT_CENSORED | FALSE (OLD_EDGE_LIFETIME ≈ 32 months for the 2024–26 MMC regime family; parameter regimes 8–24 months) ; NEW_REGIME: UNKNOWN |
| PRE_DISCLOSURE_LIFETIME / POST_DISCLOSURE_SURVIVAL | 0 / ≈ 32 months |
| CURRENT_STATE | v3 (3·CORR60 + 15·MMC60, PF 1, clip ±100%); no v3 round resolved |
| RECEIPT / DECAY EVIDENCE | Strong (full census, A6) / rule chronology (M8, WS-C) |
| PRIMARY_DECAY_MECHANISM / CAUSE_CONFIDENCE | RULE_CHANGE (HIGH) + TOKEN_PRICE / BETA (HIGH for USD results) |
| CAPACITY / SPEED | Not binding for small stakes / daily submissions |
| EXPECTED_QUANT_VALIDATION_LATENCY | ≈ 3–5 months (60-day target + ≥ 20 resolved v3 rounds → first answer ≈ late Nov–Dec 2026) |
| ACTIONABILITY_RATIO / RANGE | v3 regime expected 8–24 months (median ≈ 12) / 3–5 ⇒ LOWER ≈ 1.6, CENTRAL ≈ 3, UPPER ≈ 8 (in NMR; USD dominated by token beta) |
| TERMINAL_CLASSIFICATION | **F — MECHANISM_CHANGED_NEW_EXPERIMENT_REQUIRED** (legacy profitability does not transfer to v3) |
| CHEAPEST CURRENT FALSIFICATION | A6's recompute on the first 20 resolved v3 rounds (≥ 1343) — fail if < $2k stakes have median NMR return ≤ 0 or < 55% positive |
| REAL_CAPITAL_AUTHORIZED | FALSE |

### 5.K METACULUS AI BENCHMARK (additional case, Type V: clean competition dilution with a flat budget)

| Date | Event | Source | Label |
|---|---|---|---|
| 2024-06-25 | Open-source template bot (first commit) | Metaculus/metac-bot-template (WS-C git) | MEASURED — T2 = T3 by design |
| Q1 2025 / Q2 2025 | 30 k$ pools; 45 → 96 bots; pros lead −20.03 | notebooks, LessWrong (A2, WS-C) | (P) |
| 2025-08-05 | Seasonal 50 k$ format + MiniBench | template git (WS-C) | MEASURED |
| 2026-05-14 | "Onboarding friendliness pass for new bot makers" | template git (WS-C) | MEASURED |
| 2026-09-09 | Spring 2026: 173 bots (111 external); pros' lead 1.25 (n.s.); no template bot in top 10; 28% of owners paid | LessWrong (WS-C), A6 | (P) |
| 2026-09-25 | Fall 2026 58 k$ within a flat 175 k$ year-2 pool | Metaculus PR #5205 (WS-C) | (P) |

Pool per external entrant ≈ 882 $ → ≈ 450 $ in ≈ 15 months (A6) while the budget was flat or stepped up: **decay by entry — COMPETITION / entry dilution CAUSE_CONFIDENCE MEDIUM; the role of the open template (publication diffusion) LOW** (timing plus the template's existence only; no template bot is in the Spring-2026 top 10). Half-life of prize-per-entrant ≈ 15 months; L_val = one 4-month season; ACTIONABILITY_RATIO ≈ 3–4; **TERMINAL_CLASSIFICATION: E — CURRENTLY_DECAYING_BUT_STILL_TESTABLE** (zero capital; median entrant ≤ 0). REAL_CAPITAL_AUTHORIZED = FALSE.

---

## 6. Negative / control cases

| ID | Apparent edge | Why it is not a (usable) edge | EDGE_LIFETIME | Status |
|---|---|---|---|---|
| X1 | "39.59 M$ realized Polymarket arbitrage" (Saguillo) | Gross, one-sided, partly imputed construct; #5 cashed 122 k$ vs 750 k$ attributed, #8 17 k$ vs 468 k$ (A5) | **NOT_APPLICABLE** (the real mechanism is E7-E) | **G — ACCOUNTING_ARTIFACT** |
| X2 | Tweet-count "stars" from closed-position P&L (dddtrips +216.7k "realized"; sb911 +106k/month) | Unredeemed losers excluded: dddtrips −28.9k whole-wallet; sb911 −31.4k lifetime (A4) | NOT_APPLICABLE | **G** |
| X3 | Small Hyperliquid market making | Tier-0 maker fee 1.5 bp ≥ incumbents' total margin 0.2–1.9 bp/$; 56.5% of maker-like accounts lost in the month (A1) | NOT_APPLICABLE for small size | **H — INACCESSIBLE** |
| X4 | Hyperliquid user vaults / copy trading | 8,029 vaults: net −61.3 M$, 73.2% losers (A1); survivors are selection | NOT_APPLICABLE | **G — NOT_REAL** |
| X5 | Passive Uniswap LP | 49.5% of v3 LPs negative, fees 199 M$ < IL 260 M$ (Topaze Blue 2021-11); LVR formalised 2022-08-11; worse after the 2025-12-28 fee switch (WS-B, A2). The payee is the fast arbitrageur | NOT_APPLICABLE for the LP | **G** (LP side); arbitrage side **H** |
| X6 | Mention markets ("what will X say") | Receipts 2024-08 → 2025-01, then ≤ 0; volume per market 60 k$ → 1.2 k$ (A4, WS-A) | ≈ 6 months, ended 2025 | **C** |
| X7 | Crypto funding-rate carry | Sharpe 6.45 (2020-08 → 2025-05), 4.06 "beginning in 2024", negative in 2025 (Borri et al., 2025-10-23; no cause stated); Quant fast-rail H-002 (a related funding-spread expression) REJECT (SR −0.03) | ≈ 4 years real; ended with a market-structure change (delta-neutral capital scaling; USDe launch 2024-02-19 and spot ETFs 2024-01 concurrent) | **F — MECHANISM_CHANGED_NEW_EXPERIMENT_REQUIRED** (2020–24 evidence does not transfer) |

---

## 7. Cross-case comparison (evidence status, not attractiveness)

RC = right-censored. L_val from §3.3. Actionability = LOWER / CENTRAL / UPPER where defensible.

| CASE | TYPE | REAL RECEIPT? | PUBLIC DATE | DECAY DATE | PUBLIC SURVIVAL | CURRENT? | SMALL-CAP? | LIKELY VALIDATION LATENCY | ACTIONABILITY | STATUS |
|---|---|---|---|---|---|---|---|---|---|---|
| A Weather | I | Yes (selected, post-fee) | 2025-12-30 broad (2025-05-07 niche) | 2025-03 (1st cohort); price bias gone 2025Q3 | ≥ 9 mo (RC) | Yes, cohort turnover | Yes | 6–8 mo | 0.4 / 1–1.8 / > 3 | **B** |
| B polymm | I/IV | Yes (code + wallet) | 2026-06-06 | 2026-02/03 | ≤ 0 | No | Yes, speed-contested | ≥ 1–3 mo, not paper-measurable | 0 now | **C** |
| C1 LR T4 | III | Yes (T4 only) | 2022-02 (by design) | none (program) | ≥ 4.6 y (RC) | Yes | No | 1 mo (incumbents) | N/A (access) | **H** |
| C2 Maker rebates | III | Payments yes; net edge no | 2026-01-05 | 2026-09-10 one recipient; broad −30% in Sep | ≥ 9 mo (RC) | Yes | ∝ volume | N/A | N/A | **H** |
| D Settlement 0.999 | II | Yes (all buyers; newcomer net unmeasured) | 2025-12-04 / 2026-05-29 | not testable by design (tick-bounded) | ≥ 9 mo (RC) | Yes | Yes (queue UNKNOWN) | 1–2 mo | ≥ 6 / ≥ 12 / ≫ | **A** |
| E NegRisk | IV | Yes (strict) | 2025-08-05 | late 2024 | 5–8 mo (residual, RC) | MM tool only | No (speed) | 1–2 mo + infra | 0 now | **H** |
| F Box office | I | Yes | not found | none measured | N/A | Yes | Yes | days (replay) / 9–22 mo (prospective) | 0.3 / ≈ 1 / > 3 | **D** |
| G Tweet counts | I | Yes (historical, large) | 2026-03-19 (skill 2026-02-16) | ≈ 2026-03/04 | ≈ 0 (coincident); ≥ 6 mo at −87% capacity (RC) | Residual only | Yes | 3–9 mo | 0 / ≈ 1 (residual) | **C** |
| H HLP | II | Yes | 2023-05-10 (by design) | 2024H2 | 14–18 mo to decay; 24–36 to cash-like | Episodic only | Yes (delegated) | ≥ 12–24 mo | < 0.5 | **C** |
| I Kalshi maker | II | Yes (aggregate) | 2026-01 | none (gross) | ≥ 5 mo (RC) | Yes | No (US-only) | weeks | N/A (access) | **H** |
| J Numerai | V | Yes (NMR, legacy) | by design | regime end 2026-08-28 | ≈ 32 mo (MMC family) | New regime | Yes | 3–5 mo | 1.6 / 3 / 8 | **F** |
| K Metaculus AIB | V | Yes (prizes) | 2024-06-25 (template) | per-entrant halving ≈ 15 mo | ≥ 27 mo (RC) | Yes | Yes (0 capital) | 4 mo | ≈ 3–4 | **E** |
| X1 39.59 M$ arb | VI | No (construct) | 2025-08-05 | — | NOT_APPLICABLE | — | — | — | — | **G** |
| X2 closed-P&L stars | VI | No | — | — | NOT_APPLICABLE | — | — | — | — | **G** |
| X3 HL small MM | — | Incumbents only | — | — | — | — | No | — | — | **H** |
| X4 HL user vaults | VI | No (net −61.3 M$) | — | — | NOT_APPLICABLE | — | — | — | — | **G** |
| X5 Passive LP | VI (LP) | No for LP | 2021-11 | — | NOT_APPLICABLE | — | — | — | — | **G** |
| X6 Mentions | I | Yes (2024–25) | UNKNOWN (2024); ≈ 2025-12 (S, approximate) | 2025-01 | ≤ 0 if the approximate date holds | No | — | — | 0 | **C** |
| X7 Funding carry | II / regime | Yes (2020–24) | practitioner years earlier; paper 2025-10-23 | 2024 → 2025 | years (practitioner) | No | — | — | 0 | **F** |

**REAL_BUT_NOT_ACTIONABLE (C): 4** (B polymm, G tweet counts, H HLP, X6 mentions). NegRisk was re-classified H and funding carry F after the independent integrity review.

---

## 8. Cross-case synthesis

### 8.1 Archetypes observed (only where the evidence supports them)

| Archetype | Cases | Observed lifetime pattern | Dominant decay mode |
|---|---|---|---|
| I Informational inefficiency | A, B, F, G, X6 | **Trader/rule-level edges ≈ 3–15 months** (polymm ≈ 3, mentions ≈ 6, weather first cohort ≈ 6–7 weather-wide, tweets ≈ 12–15); mechanism-level can persist with cohort turnover (weather ≥ 20 months, box office ≥ 12) | Competition / better pricing; mispricing regenerates at mechanism changes |
| II Structural liquidity premium | D, I, H | Floor-protected premia persist (settlement trade observed ≈ 20 months, Kalshi ≥ 4 years); **open-capacity structural returns dilute** (HLP half-life ≈ 5 months) | Capacity dilution when capital can enter freely; bounded by the tick when a floor binds |
| III Platform subsidy / fee share | C1, C2 | Programs live for years; parameters change every 1–4 months (Polymarket fee/rebate entries 01-05, 01-16, 02-18, 03-06, 03-30, 05-28, 07-10); counterparty-specific breaks | Discretionary rule/budget steps; rent accrues to incumbents |
| IV Mechanical arbitrage | E | Rich phase ≈ 8–12 months; per-conversion profit ≈ −80% within ≈ 6 months | Automation / competition before any publication |
| V Service / tournament payment | J, K | Payer persistent; **rule regimes 8–24 months**; per-entrant pool halves in ≈ 15 months under open templates | Rule change (J), entry dilution (K) |
| VI Accounting illusion | X1, X2, X4, X5 | Not an edge | — |

### 8.2 Answers to the mission's questions

**Q1. Do public strategy disclosures typically precede decay?** **No.** Among the five competitive (Type I/IV) cases, four have dated disclosures: decay onset **preceded** the first detailed public disclosure in 3 — NegRisk (≈ 9 months earlier), polymm (≈ 3), weather first cohort (≈ 2 months before a niche 16★ repo, ≈ 9–10 before broad disclosure) — and **coincided** with it in 1 (tweet counts: large-winner decay ≈ 2026-03/04 vs agent skill 2026-02-16, newsletter method 2026-03-19, fee 2026-03-30). Mentions: disclosure date UNKNOWN (excluded). Lead where it preceded: 2–9 months (median ≈ 3). Disclosure is mostly **lagging and endogenous**: academic papers carry 6–18-month data lags; practitioners publish after they stop. Counter-examples are mechanisms public for years before decaying — funding carry (well known long before its 2024–25 decline, which coincided with capital scaling, not with publication) and mechanisms public *by design* (HLP, reward programs, tournaments).

**Q2. How often can causality be established?** Rarely. HIGH only for **documented rule changes** (Numerai v3; Kalshi maker fees; Polymarket rebate-rate cuts) and for the **mechanical absence of decay** at the settlement tick floor. MEDIUM for competition where a direct symptom is measured (polymm fill rate; NegRisk per-conversion profit falling while fee-free; HLP dilution elasticity; Metaculus entrants). LOW in every attempt to attribute decay to publication.

**Q3. Post-publication survival where measurable.** Bimodal:
- **Competitive edges (I, IV)**: the original edge's survival after its first detailed disclosure is **≈ 0** — it was already decaying at or before disclosure in 4 of 4 dated cases (strictly before in 3); residuals survive 0–8 months (tweets ≥ 6 at reduced capacity, NegRisk 5–8).
- **Public-by-design structural / subsidy / tournament mechanisms (II, III, V)**: ≥ 5 months (Kalshi) to ≥ 4.6 years (liquidity rewards), mostly right-censored; they decay by dilution or rule change rather than by disappearing.
A single pooled median would be misleading and is not reported.

**Q4. Small-capacity vs large-capacity persistence?** Capacity alone does not decide it. **Small-capacity *slow* edges look more persistent** (box office: no measured compression in 12 months; the settlement floor trade present in every window for ≈ 20 months); **small-capacity *speed* edges do not** (polymm died in ≈ 3 months); **open-capacity edges that passive capital can enter decay by dilution** (HLP median daily return 20.5 → 0.8 bp, ≈ −96% to the latest half-year, trough 0.18 bp, as AV rose ≈ 60×). CONFIDENCE LOW (n small).

**Q5. Are subsidy edges more fragile than informational edges?** Different fragility: subsidies carry **jump risk by decree** (every Type III/V case shows discretionary parameter changes within months), while informational edges suffer **continuous competitive erosion** at the trader level. Subsidy programs themselves have lasted longer than any informational edge measured here; the *rent to a small entrant* has not been shown to exist (A6).

**Q6. Do rule/fee changes destroy more edges than competition?** In this sample, **competition/dilution is the primary decay mode more often** (NegRisk, polymm, HLP, weather first cohort, Metaculus; 5) than rule/fee changes (Numerai v3, Kalshi maker net; 2), with tweet counts and the rebate discontinuity UNKNOWN. Rule changes create *discontinuities that require a new experiment* (status F); competition creates *gradual decay* (status B/C).

**Q7. Does open-source publication materially accelerate decay?** Not demonstrably in any case studied. polymm's repo appeared ≈ 3 months after it stopped; NegRisk repos exploded (4 → 94 → 397) after most compression; weather's bot wave (Jan–Apr 2026) came after the first cohort's decay and the market still pays a new cohort; Metaculus's official template precedes entry dilution but no template bot reached the top 10 in Spring 2026. CAUSE_CONFIDENCE LOW in every case.

**Q8. Which candidates look slow enough for the current validation method?** Settlement liquidity 0.999 (A: premium tick-bounded, L_val 1–2 months — but economically tiny, tail-dominated, queue share unmeasured); Numerai v3 (F: regime ≈ 8–24 months vs L_val 3–5 months, in NMR; borderline on the lower bound); box office can be **falsified** fast by historical replay, but prospective **validation** (9–22 months) is comparable to its plausible lifetime; Kalshi maker and T4 rewards would be slow enough but fail access.

**Q9. Which look too fast?** NegRisk / complete-set taker arbitrage; esports/sports requote market making (polymm type); tweet-count large-maker and cheap-bucket variants; mention markets; crypto "Up or Down" latency; HLP as a "strategy" (validation ≥ 12 months vs half-life ≈ 5); new-maker reward farming in contested markets.

**Q10. Is Weather validation likely slower than Weather edge decay?** **Comparable or slower, for any specific frozen rule.** Weather's first powered label needs ≈ 6–8 months (MEUE-level confirmation 3–6 years); the first specialist cohort's weather-wide run lasted ≈ 6–7 months (2024-08/09 → 2025-02), of which ≈ 2 months in daily city markets; the launch-quarter price bias was gone within ≈ 2 quarters; venue mechanics changed ≥ 4 times in 8 months (a MECHANICS_CHANGE stop is likely inside a 120-date window). The *mechanism* (recreational flow vs public forecasts) has persisted ≥ 20 months with turnover, which is why the classification is B, not C.

**Q11. Does box office look structurally more durable?** It **looks** durable — no measurable absorption speed-up in 12 months, small capacity, almost no public diffusion — but the same property (≈ 2–6 events/week) makes prospective validation slow (≈ 9–22 months for +10%/$). The Sunday-estimate information is absorbed within ≈ 3 h; any residual edge sits in the Friday-actuals → Sunday window and in boundary judgement. Durability is **not established**, only undecayed so far (D).

**Q12. Does settlement liquidity persist because it compensates impatience/capital lock rather than ignorance?** **Yes, on mechanism grounds.** The per-fill gross is fixed at the tick floor by construction (so decay of the premium is not testable here); the floor trade occurred in all 8 windows over ≈ 20 months with a stable floor share, and holds shortened with faster resolution. Competition compresses queue share/capacity, not the per-fill premium. The economics hinge on correctly identifying *decided* states: pooled naive in-window net across all buyers is −0.115% because of in-play sports fills (§4.5).

**Q13. Did Polymarket rebates demonstrate a regime break rather than normal competitive decay?** **Neither is established.** The aggregate drop (≈ 13× from 07-01, ≈ 8× from 09-01) is **one non-trading recipient address** whose 165.3 M$ rebate stream (2026-01-16 → 09-10) stopped. All other recipients' pool fell ≈ 30% in September after a World-Cup peak — within the range of seasonality and crypto-volume changes. A program-wide regime break for ordinary makers is not supported; whether the dominant stream ended through that recipient's exit or through a category-specific rule change cannot be distinguished. Classification: COUNTERPARTY_SPECIFIC_DISCONTINUITY, cause UNKNOWN.

**Q14. Is Agent 6's T4 reward result a strategy candidate, a temporary subsidy harvest, or an incumbent-scale rent?** **An incumbent-scale rent on a persistent-but-discretionary subsidy** (§5.C1). Not a Quant strategy candidate at current capital; not shown to be temporary in the observable window.

**Q15. Lanes to stop spending validation time on** (likely half-life shorter than validation, or no small-player access): NegRisk / complete-set taker arbitrage; requote-race market making (polymm type); tweet-count large-maker and cheap-bucket variants; mention markets; crypto up/down latency; HLP as an edge; copy trading / user vaults; small Hyperliquid MM; Kalshi (access); small-tier reward farming; and **any confirmatory design targeting small effects on daily/weekly markets** (e.g. θ = 0.02/$ weather: 3–6 years vs trader-level lifetimes of months).

### 8.3 Special checks (mission §§18–22), explicit verdicts

- **Weather (§18)**: first specialist receipts ≤ 2024-09; first public detailed descriptions 2025-12-30 → 2026-02-06; open-source bots from 2025-05 (niche) and 2026-01 → 04 (mass, 768★/319★); fee 2026-03-30; settlement source WU → NOAA 2026-08-22; publicly named wallets' weather P&L fell from 2025-03 (activity migration, not wallet death); participation widened (2 → 51 cities, per-event volume up then down); the simple price bias compressed by 2025Q3; NYC sharper YoY. The edge plausibly **migrated** from "any forecast beats the launch-quarter crowd" toward new cities / post-change windows / execution — consistent with new-cohort receipts, not proven. **WEATHER_EDGE_DECAY_STATE = DECAYING (confidence LOW–MEDIUM)**. Contextual only; the frozen Weather rule and experiment are untouched.
- **Box office (§19)**: liquid weekly regime since 2025-10-14; practitioners active from 2025-10-15; no absorption speed-up at any anchor; volumes not rising (median event volume 208 k$ → 83 k$ Q2 → Q3); one early specialist (Big.Chungus) left in 2026-03; the naive Saturday-favourite diagnostic fell +25% → −14% (pre-declared trend test not significant, z −1.47; a post-hoc Q4-vs-Q3 contrast would be ≈ 2.6 SE); continued 2026 receipts; capacity a few k$/event; disclosure footprint ≈ nil. Structural delay vs undercompeted niche: **not discriminable yet**. **BOX_OFFICE_DECAY_STATE = UNKNOWN** (no decay detected; underpowered; 12-month right-censored).
- **Settlement liquidity (§20)**: liquidity/time-value premium, tick-floored; payout delay ≈ 2 h (undisputed), 4–6 days disputed; dispute rate ≈ 1.3% (UMA, Aug 2025); queue competition real; resolution speeding up. **SETTLEMENT_LIQUIDITY_DECAY_STATE = PERSISTENT** (mechanism observed in every window for ≈ 20 months; per-fill premium tick-bounded, so its decay is not testable; net for a newcomer and queue share unmeasured; confidence MEDIUM).
- **Maker rewards (§21)**: LIQUIDITY_REWARD_PROGRAM persistent at program level (≈ 100–110 k$/day since August; discretionary steps), rent concentrated in incumbents; MAKER_REBATE_PROGRAM: single-recipient discontinuity (cause UNKNOWN) plus ≈ −30% September for everyone else. T4 = INCUMBENT_ADVANTAGE on a structural-need, discretionary subsidy; entrant scale ≥ 12–14 k$ cash (lower bound on capital). **MAKER_REWARD_DECAY_STATE = PERSISTENT** (program level; confidence MEDIUM); a program-wide rebate regime break is not supported by the data.
- **Numerai (§22)**: OLD_EDGE_LIFETIME ≈ 32 months for the 2024–26 MMC regime family (parameter regimes 8–24 months); NEW_REGIME from round ≈ 1343 (2026-08-28), unmeasured; legacy profitability is not transferred. **MECHANISM_CHANGED_NEW_EXPERIMENT_REQUIRED.**

### 8.4 Change-point / decay-measurement summary

| Series | Method | Result | Label |
|---|---|---|---|
| HLP median daily return (quarterly) | Log-linear regression, 12 quarters | Half-life 5.1 months (95% CI 4.0–7.2); elasticity to AV −0.98 | MEASURED / DERIVED |
| Polymarket rebate pool | Decomposition by recipient, 13 dates | Discontinuity = one recipient (last paid 2026-09-10); others −30% in Sep | MEASURED |
| Box-office winner price at anchors | Spearman trend, 117 events | No trend (abs z < 0.6) | MEASURED |
| Box-office Saturday favourite (diagnostic) | Quarterly bootstrap CIs + trend | +25% → −14%, ρ = −0.14 (z −1.47): not significant | MEASURED |
| Weather calibration / favourite return | Quarterly ECE + bootstrap CIs; same-month YoY Brier | Launch-quarter bias gone by 2025Q3; NYC Brier 0.769 → 0.664 | MEASURED |
| Settlement ≥ 0.999 | 8 windows, gross vs losses | Gross = tick floor throughout; net set by rare in-play losers | MEASURED |
| Tweet-count volume | Monthly series | Peak 2026-01, −87% by 2026-09 | MEASURED |
| Named-wallet P&L | Monthly realized (word-boundary weather filter) / `user-pnl` | Cohort turnover (2025-03 decay onset for the first weather cohort) | MEASURED |
| Numerai rules | Round-API regime boundaries | 5 changes in 5.6 years | MEASURED |
| Formal Bayesian change-point | — | Not run: series too short/sparse relative to the discontinuities, which are already identified exactly (single recipient, documented rule dates) | — |

---

## 9. Validation-latency implications for Quant

### 9.1 Is the current process "scientifically correct but too slow"?

**Yes, for part of the edge population — but mostly not for engineering reasons.** Decomposition (from §3):

| Latency | Observed scale | Dominance |
|---|---|---|
| A. Research (discovery, receipts, mechanism) | hours – days | small |
| B. Engineering (collectors, adapters) | 1–3 days (fast rail) to weeks (full vertical) | small–moderate |
| C. **Statistical** (forward observations to a powered verdict) | **months – years** | **dominant** |
| D. Governance (freeze → audit → redesign → re-audit loops) | days – weeks per failed freeze | second |
| E. Integration (chassis gaps) | UNKNOWN (bounded) | unknown |
| (upstream) **Discovery lag** (age of the edge when receipts make it visible) | **median ≈ 24 months** | often decisive |

Two structural facts follow. (1) The fast rail cannot make a weekly-frequency edge validate faster; only more independent observations, lower-variance statistics that still equal the executable economics, or admissible historical evidence can. (2) Receipt-first discovery conditions on visible success and therefore finds edges after their peak in 5 of 8 dated cases.

### 9.2 Do FAST / STANDARD / SLOW rails need to exist?

Quant already has a **two-speed split by governance and capital proximity** (SAFE vs FAST rail, accepted 2026-09-25) and a `SHADOW_DIRECT` ladder that already implements the honest fast-rail ingredients: one frozen expression, parameters fixed by source or mechanism, immediate forward shadow, no capital, pre-declared kill boundaries and horizon, anytime-valid sequential test, α-spending across entries. What it lacks is **routing by edge half-life versus statistical latency**. The evidence here says such routing is economically necessary:

| Route (recommendation) | Admission condition | Evidence standard (unchanged) | Typical decision time |
|---|---|---|---|
| **FAST** | ≥ tens of independent observations per day **and** a test statistic that *is* the executable net economics (not a proxy); queue/adverse-selection unknowns either observable in paper or explicitly carried as unvalidated | Same α, fees, PIT; sequential t-SPRT/e-process; FORWARD_PASS needs net P&L | weeks |
| **STANDARD** | Daily/weekly markets with τ_rem ≥ 2 × L_val on the lower bound, or a replay-first path | Strict-PIT historical replay as falsification + forward screen powered for large effects (θ_PCE) | 4–8 months |
| **SLOW SCIENCE** | Structural, capacity-limited mechanisms with evidence that competition cannot erode them (floors, payer-side need) | Full design; multi-period | years |
| **DO NOT VALIDATE** | τ_rem (central) < L_val and no faster valid path | — | record as C and stop |

FAST never means lower evidence quality; it means more independent observations per unit time plus sequential stopping.

### 9.3 Architectural responses (recommendations only; nothing is implemented here)

1. **Move discovery upstream (T0, not T1).** Watch for *mechanism births and changes* — new market families, new cities, new ladders/templates, new fee/reward regimes — instead of waiting for leaderboard receipts. Evidence: mispricing appeared at the weather launch (2025Q1) and around the 2026Q1 ladder change, and decayed within 1–2 quarters; box-office specialists entered within 1–5 days of the 2025-10-14 regime start.
2. **Power/latency-first triage before any design or build**: compute L_val (statistical) from observation rate, dispersion and plausible effect before freezing; the Weather V1 failure (power below MEUE) was detectable by this arithmetic alone.
3. **Prebuilt Polymarket venue capture** (books, trades, resolution states, fee schedules) shared across weather, box office and settlement, so collection starts at freeze rather than after a build.
4. **Replay-first for archived public-information markets**: strict-timestamp historical replay counts as falsification (never as confirmation), cutting the statistical clock for weekly edges from months to days for large effects.
5. **Standing decay monitors per live candidate** (the measurements in §4 are directly reusable): absorption at release anchors, calibration/favourite returns, cohort turnover of receipt wallets, pool-by-recipient decomposition, return half-life fits.
6. **Templated pre-registration** for recurring archetypes (bracket markets, settlement census, reward cohorts, tournament re-scoring) to shorten freeze → audit → redesign loops.

### 9.4 Decay-aware research gate (pre-build test)

Definitions: `L_val = L_eng + L_burn_in + L_forward(effect, σ, observation rate) (+ L_integration)`; `τ_rem` estimated with LOWER / CENTRAL bounds from (a) archetype base rates (§8.1), (b) decay evidence at discovery (absorption trend, cohort turnover, volume/pool trend), (c) the edge's age at discovery, (d) the venue's mechanics-change hazard.

```text
if   τ_rem.CENTRAL <  L_val                       -> DO_NOT_BUILD_FULL_VERTICAL; zero-build falsification only; record status C
elif τ_rem.LOWER   <  SF × L_val                  -> BUILD ONLY VIA A FASTER VALID PATH (FAST route or replay-first); no full vertical yet
else                                              -> STANDARD path allowed
```

**Safety factor SF = 2** (DERIVED heuristic, not calibrated): the post-validation exploitation window must at least equal the validation period to repay it, and the lifetime estimates here carry roughly ×2 uncertainty (HLP half-life CI 4–7 months; weather τ_rem 3–24 months). Recalibrate SF from Quant's own realized validation-vs-decay outcomes; until then SF is ASSUMED at 2.

Illustration on current candidates (not decisions): settlement (1–2 vs ≥ 12 months) passes; Numerai v3 passes on the central estimate and is borderline on the lower bound (L_val 3–5 months vs regime lifetime 8–24, median ≈ 12; in NMR); box office passes **only** replay-first; weather sits in the middle branch (6–8 vs 3–12 on the lower-to-central range), which is the Weather rail's own design decision; NegRisk, polymm-type MM, tweet counts and HLP fail.

---

## 10. Self-audit (mission §38)

| # | Attack | Finding | Correction made |
|---|---|---|---|
| 1 | Public disclosure confused with wide diffusion? | Kept separate: first niche mention, first detailed method, first open source, broad publicity are distinct columns (e.g. weather 2025-05-07 / 2025-12-30 / 2026-01 → 02) | — |
| 2 | Causality from chronology? | No publication-caused decay is claimed; CAUSE_CONFIDENCE LOW wherever only timing exists | — |
| 3 | Survivor wallets as persistence evidence? | Mechanism persistence is argued from market-level series (M3, M4, M5) and A6's pre-declared cohorts; named wallets used only for cohort turnover | — |
| 4 | Regime change called competition? | Rebate drop re-labelled from "regime break/decay" to single-recipient discontinuity; Numerai labelled RULE_CHANGE | **Corrected A6's reading** |
| 5 | Lower recent P&L called decay without statistics? | Box-office Saturday diagnostic decline reported as non-significant; weather claims rest on CI-excluding-zero launch quarter and same-month YoY | — |
| 6 | Accounting artefact used as edge? | X1, X2, X4 classified G; `user-pnl` used for receipts | — |
| 7 | Historical evidence transferred to 2026? | NegRisk, tweets, Numerai legacy explicitly not transferred | — |
| 8 | Right-censored treated as ended? | Weather, box office, settlement, rewards, Kalshi marked RC with minimum lifetimes | — |
| 9 | Invented precise edge-start dates? | Dates only from gamma/on-chain/git/docs; intervals otherwise (e.g. dynamic tick UNKNOWN; LR start year inferred, MEDIUM) | — |
| 10 | Capacity changes ignored? | HLP dilution, weather/box-office per-event volume, mention fragmentation, reward recipients reported | — |
| 11 | Fee/rule changes ignored? | Every chronology lists them | — |
| 12 | Gross vs net? | Settlement gross (tick) vs net (tails) separated; Kalshi +2.40% flagged gross | — |
| 13 | Time for independent observations ignored? | Statistical clock is the central result (§3, §9) | — |
| 14 | Fast rail that lowers standards? | FAST keeps α, fees, PIT; admission requires observation rate and an executable statistic | — |
| 15 | Silent promotion to validated? | None: A/D/F statuses are lifetime/actionability labels only | — |
| 16 | Real edges dying before validation overlooked? | Six C cases listed | — |
| 17 | Mechanism decay vs one trader's decay? | Weather: trader exit (gopfan2 still active elsewhere) distinguished from mechanism (new cohort, market-level calibration) | A1's "stars ≈ 0 since April 2026" window understates how early the first cohort faded (2025-03). **An initial loose weather filter matched "Ukraine"/"Bahrain" titles; replaced by a word-boundary filter after the integrity review** |
| 18 | Temporary subsidy vs structural rent? | T4 = incumbent rent on a persistent-but-discretionary subsidy | — |
| 19 | Endogenous publication? | Q1: in 5/5 measurable competitive cases the edge was decaying at or before the first detailed disclosure (4 strictly before) | **Corrected an initial "6 of 6" that mis-dated weather (niche repo same month) and funding carry (public for years)** |
| 20 | Reproducibility? | Every MEASURED figure has an endpoint and script in `agent7_data/`; WS-A/B/C facts carry URLs | — |

Other corrections to prior agents recorded here: Numerai v3 starts at round ≈ 1343 (2026-08-28), not ≈ 1363 (A6); tweet-count events start 2024-05-03, not June 2024 (A4); A5's settlement +0.14–0.15% holds in 6 of 8 windows but the 2025–26 pooled naive in-window result across all buyers is −0.115%.

**Independent integrity review (applied):** corrections made to the weather filter and onset (2025-03), tweet-count decay timing (2026-03/04, coincident with disclosure), Q1/Q3 counts, NegRisk status (C → H) and right-censoring, funding carry (C → F), box-office decay state (PERSISTENT → UNKNOWN), settlement wording (per-fill premium not testable by design; all buyers; confidence HIGH → MEDIUM), rebate-break wording, Metaculus causal confidence, HLP benchmark (no lending yield measured), discovery-lag median (≈ 24 months), and several numeric details. One recommendation was not adopted: settlement status A was kept rather than D (see §5.D).

**Known limits (not fixable here):** weather measured on NYC + London only and without forecast archives (by design); gamma `volume` is unaudited (WS-A's box-office monthly volumes differ from mine; only direction is used); ECE has a small-sample floor; settlement windows are 3 days × 8, so tail frequency is estimated from 34 losing fills; the dominant rebate recipient's economics and the cause of its stop are unknown; Wayback was unreachable, so older doc versions (rebate shares in January 2026, dynamic-tick activation) could not be dated.

---

## 11. Terminal answers

```text
EDGE_DECAY_IS_A_FIRST_CLASS_QUANT_RISK                    = TRUE
CURRENT_VALIDATION_PROCESS_TOO_SLOW_FOR_SOME_REAL_EDGES   = TRUE
FAST_VALIDATION_RAIL_ECONOMICALLY_JUSTIFIED               = TRUE   (for high-observation-rate mechanisms with an executable statistic; largely already present as SHADOW_DIRECT; cannot rescue low-frequency short-lived edges)
WEATHER_EDGE_DECAY_STATE                                  = DECAYING        (confidence LOW–MEDIUM; contextual only)
BOX_OFFICE_DECAY_STATE                                    = UNKNOWN         (no decay detected over 12 months; underpowered; case status D)
SETTLEMENT_LIQUIDITY_DECAY_STATE                          = PERSISTENT      (mechanism in every window for ≈ 20 months; per-fill premium tick-bounded; net/queue share unmeasured; MEDIUM)
MAKER_REWARD_DECAY_STATE                                  = PERSISTENT      (liquidity-reward program level, discretionary; rebate aggregate drop = single-recipient discontinuity, cause UNKNOWN; program-wide regime break not supported)
BEST_NEXT_DECAY_AWARE_RESEARCH_ACTION                     = Run A4's strict-timestamp box-office replay over the whole templated regime (2025-10-14 → T_NOW), reporting the Friday-actuals→Sunday-window return per quarter, so one run is both the cheapest falsification (not a validation) of the current candidate and its decay series.
REAL_CAPITAL_AUTHORIZED                                   = FALSE
```

Nothing in this file is a trading recommendation, and no candidate is promoted to VALIDATED.
