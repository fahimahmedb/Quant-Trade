# AGENT 7 — EDGE ARCHAEOLOGY / DECAY

Date: 2026-09-29 (UTC). External research, public-API measurement and validation-latency audit.
No orders, no wallets, no credentials, no bots, no strategy code, no de-anonymisation.
**REAL_CAPITAL_AUTHORIZED = FALSE. LIVE_TRADING_AUTHORIZED = FALSE.**
Branch: `claude/exciting-planck-uq6rir` (harness-assigned). State file: `agent7_edge_archaeology_decay_etat.md`.
Supporting data and scripts: `agent7_data/`.

Central question: *when a real, publicly observable edge exists, does it survive long enough for Quant's
DISCOVERY → VERIFICATION → FALSIFICATION → SHADOW VALIDATION process to reach it before it decays?*

> Section 0 (terminal answers) is at the end of this file (§17), after the evidence.

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
| M6 | Tweet-count family (Elon Musk post counts) monthly event volume 2024-04 → 2026-09 | gamma `events?tag_slug=tweets-markets|elon-tweets|elon-musk` | §4.6 |
| M7 | Monthly `user-pnl` deltas and weather-only realized P&L for already-public wallets (b00k13, gopfan2, aenews2, BeefSlayer, russell110320, HighTempTation, Bilberry) | `user-pnl-api`, `data-api /closed-positions` | §4.7 |
| M8 | Numerai Classic payout-rule regimes and round-level payout/stake, rounds 250 → 1365 (every 5th round) | `api-tournament.numer.ai` GraphQL `roundDetails` | §4.8 |
| M9 | Quant's own validation latency from git history and fast-rail registry timestamps | local `git log`, `registry.jsonl` | §3 |

### 2.3 External archaeology (WS-A informational, WS-B structural, WS-C subsidies/tournaments)

Three bounded research workstreams collected dated chronologies (docs/changelogs, papers, press, git first-commit dates of public repos). Their key dated facts are cited inline as (WS-A/B/C) with the underlying URL; items only seen in search summaries are marked (S, unopened). Wayback Machine was unreachable from this environment, so historical doc versions could not be recovered; this is the main archaeology limitation.

---

## 3. Quant's own validation latency (M9)

### 3.1 What Quant has actually taken to do each step (MEASURED from git / registry)

| Component | Quant evidence (timestamps UTC) | Value | Label |
|---|---|---|---|
| L_DISCOVERY | Receipt-first wave, Agents 1–6: first commit 15:09, last 17:36 on 2026-09-29 (six parallel agents; per-agent commit spans 9–70 min) | **hours (≤ 1 day)** | MEASURED |
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
| V3 weekly markets (box office) | ≈ 2–6 events/week | historical replay: days (MDE only ≈ 0.10–0.13/$); prospective: **≈ 9–22 months** for +10%/$ (M3, §4.3) |
| V4 regime/round programs (Numerai v3) | one resolution cycle ≈ 60 days + ≥ 20 rounds | **≈ 3–5 months** |
| V5 delegated, episodic payoff (HLP) | a few liquidation episodes per year | **≥ 12–24 months** to separate excess return from lending yield |

### 3.4 Discovery lag: the receipt-first method finds edges late in life (DERIVED)

Receipt-first search can only see an edge **after** it has produced visible winners. The gap between a mechanism becoming available (T0) and Quant's discovery (2026-09-29) is:

| Case | T0 (earliest defensible) | Discovery lag at T_NOW | Main decay already observed before discovery? |
|---|---|---|---|
| Weather (daily city markets) | 2025-01-21 (first NYC/London daily events, M4) | ≈ 20 months | **Yes for the first specialist cohort** (peak 2024-09 → 2025-04, M7); mechanism still pays a new cohort |
| Box office (regular weekly series) | 2025-10 (M3: 1–5 events/month before, 5–26/month after) | ≈ 12 months | No measured decay (M3) |
| Tweet counts | 2024-05 (first weekly events, M6) | ≈ 28 months | **Yes** (large winners exited 2026-01 → 04; family volume −87% from peak, M6) |
| polymm esports MM | 2026-01-06 (first trades, A3) | ≈ 9 months | **Yes** (fill rate 37% → 1% by 2026-04; A3, M7) |
| NegRisk conversion arbitrage | ≤ 2024 (Gebele Fig. 6) | ≈ 24+ months | **Yes** (≈ $1 → $0.08 per conversion; A5 #8 dried in 3 months) |
| HLP | 2023-05-10 (vault inception, M1) | ≈ 40 months | **Yes** (return half-life ≈ 5 months, M1) |
| Settlement liquidity | ≤ 2025-01 (M5; A5's academic sample starts at market inception) | ≥ 20 months | No (floor premium unchanged, M5) |
| Polymarket liquidity rewards | 2022-02-17 (WS-C, inferred year) | ≈ 4.6 years | Per-recipient dilution; program alive |

**Median discovery lag ≈ 20 months; in 5 of 8 dated cases the principal decay had already happened before Quant found the edge.** This is a structural property of receipt-first discovery (it conditions on visible success), not a flaw of any one agent. It is the single most important timing fact for Quant: *the binding constraint is often not validation speed after discovery, but how late in an edge's life discovery occurs.*

---

## 4. New empirical measurements

### 4.1 M1 — HLP (Hyperliquid protocol vault): a clean measured decay curve

Data: `vaultDetails` portfolio `allTime` (99 periods of 7–14 days, 2023-05-10 → 2026-09-29). Period return = Δpnl / account value at period start (MEASURED).

| Half-year | Median AV (M$) | Annualised return, all periods | Annualised, excluding the single best period | Median daily return (bp) | Best period's share of half-year P&L |
|---|---|---|---|---|---|
| 2023H2 | 7 | 158.5% | 137.3% | 20.5 | 42% |
| 2024H1 | 84 | 153.7% | 135.9% | 13.3 | 18% |
| 2024H2 | 179 | 28.0% | 23.3% | 6.2 | 19% |
| 2025H1 | 356 | 11.8% | 8.4% | 2.6 | 34% |
| 2025H2 | 448 | 26.1% | **5.1%** | 1.6 | **82%** (period ending 2025-10-15: +41.4 M$, the 10–11 Oct crash) |
| 2026H1 | 372 | 14.8% | **0.2%** | 0.18 | **101%** (period ending 2026-02-04: +18.8 M$) |
| 2026H2 (to 09-29) | 202 | 3.0% | 1.8% | 0.8 | 48% |

- Log-linear fit of quarterly median daily return, 2023Q4 → 2026Q3: slope −1.62 ± 0.24 per year ⇒ **half-life ≈ 5.1 months (95% CI 4.0–7.2)** (DERIVED).
- Elasticity of median return to vault AV ≈ −0.98 (DERIVED): dollar P&L per period roughly constant while capital grew ~60× — the signature of a **fixed flow shared by more capital** (capacity saturation / platform-growth dilution). Time and AV are collinear, so this does not separate competition from dilution.
- Ex-episode return since 2025H2 is at or below a USDC lending yield (A5 reports API APR 3.94%); what remains is **episodic crash insurance** (two liquidation windfalls ≈ 41% of lifetime P&L, WS-B/CoinGecko (S)).

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

The dominant recipient (MEASURED through `data-api /activity`): **243 MAKER_REBATE payments totalling 165.3 M$ from 2026-01-16 to 2026-09-10, then none**; monthly 1.2 M$ (Jan) → 36.4 M$ (Jul) → 8.8 M$ (Sep 1–10). The same address has **no trades, no positions, no `user-pnl` series and no leaderboard entry** in the public API (only MAKER_REBATE, YIELD, REWARD and REFERRAL_REWARD receipts); its code is a 23-byte `0xef0100…` delegation stub. It is therefore a **collection address for rebates earned by trading done elsewhere** (or a special arrangement); its owner is not investigated (no de-anonymisation).

Consequences (DERIVED / INFERRED):
- For every other maker the rebate pool was ≈ 150–220 k$/day (Apr–May), ≈ 370–400 k$/day during the World Cup window (FIFA World Cup 2026-06-11 → 07-19; WS-C: platform volume −36.7% Jul → Aug), ≈ 176–196 k$/day (Aug → 09-01), then 162 k$ and 124 k$ in September: **a ≈ 30% decline over September, not a 13× collapse.** The recipient count is flat across the break (4,632 → 4,727).
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

Market history (MEASURED, gamma `tag_slug=weather`): daily "Highest temperature in <city>" events start **2025-01-21** with NYC and London only (≈ 60 events/month through 2025-11); expansion to 8 cities in **2025-12** (233 temperature events), 12+ cities by 2026-01/02 (288, 367), 432 in 2026-03, and ≈ 100 events/day (51 cities) by 2026-09 (Weather V1 spec C15). Bucket ladder per event: **7 buckets (2025) → 9 (2026-02) → 11 (from 2026-03/04)**. Median volume per NYC/London event: 40–110 k$ (2025-02 → 10) → 150–315 k$ (2025-11 → 2026-04) → 63–79 k$ (2026-09).

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

Eight mid-month windows, 200 random resolved binary markets each (volume ≥ 1 k$, crypto "Up or Down" excluded), every fill at ≥ 0.995 in the final 24 h before `closedTime` (MEASURED; 1,499 markets, 29,160 fills):

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
- Reading (DERIVED): the **gross premium is pinned at the 0.001 tick in every window for 21 months — no decay is possible below the floor**; the share of near-certain volume executed at the floor is stable (63–89%); holds shortened in 2026-07/09 (0.6 h vs 2–3 h), consistent with faster resolution paths (crypto auto-resolution Aug 2026, settlement-time estimates published 2026-09-28; WS-B). **The economics are governed by the tail rate of "near-certain but not decided" fills (≈ 1.4 per 1,000 fills here, size-weighted loss ≈ 2.1× gross), not by competitive decay.** A5's two September-2026 slices (+0.14–0.15%, 3 losers in ≈ 11,000 fills) are consistent with the good months here, not with the pooled result.

### 4.6 M6 — Tweet-count family volume

Monthly volume of Elon-Musk post-count events (MEASURED, gamma, 390 events): 2024-05 → 2024-12 0.3–9.2 M$/month; 2025-01 → 2025-09 17–41 M$; 2025-10 58 M$; 2025-11 114 M$; 2025-12 173 M$; **2026-01 240 M$ (peak)**; 2026-02 211 M$; 2026-03 124 M$; 2026-04 149 M$; 2026-05 136 M$; 2026-06 79 M$; 2026-07 47 M$; 2026-08 41 M$; **2026-09 31 M$ (−87% from peak)**. The four large 2025-26 winners exited between 2026-01 and 2026-04 (A4); the category fee (rate 0.04) started 2026-03-30 (A1, WS-C).

### 4.7 M7 — Named public wallets: decay of traders vs decay of mechanisms

Weather-only realized P&L from `closed-positions` (upper-biased, attribution only; MEASURED):
- **gopfan2**: 2024-09 +23.7k, 2024-12 +20.2k, **2025-01 +43.2k, 2025-02 +48.5k**, 2025-03 +4.9k, 2025-04 +11.9k, then 2025-05 → 2025-12 between −0.1k and +16.8k, and **≈ 0 on 1–5 weather positions/month since 2026-01**. Whole-wallet `user-pnl` stays large and volatile (e.g. +161.2k in 2026-09): the trader left weather; the wallet did not stop.
- **aenews2**: weather peak 2025-03 (+67.7k), −21.6k in 2025-06, ≈ 0 since; whole-wallet still active (e.g. +696.8k 2026-06, −187.7k 2026-07).
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
