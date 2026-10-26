# EDGE SEARCH BOARD — independent Claude (Builder) shortlist

Date: 2026-10-08. Status: board only. **No outcome data was downloaded or read.** Four read-only research agents consulted the repository history and public documentation (papers, API/docs pages, dataset listings). Only file and directory names of `data.binance.vision` were listed. Tags: `VF` = page fetched this session; `UM` = from memory/search snippet only (unverified); `DER` = my arithmetic under i.i.d. assumptions; `ASSUMED` = planning assumption, not a measurement.

Owner directive answered here: PR #22 comment `6061968640` (FIND A REAL EDGE) and the protection of hypotheses requested in comment `6062989770`.

## 1. What the repository audit established (VERIFIED_IN_REPO by the audit agent)

- **No live, tested edge exists.** Sector relative value (9 ETFs, 36 expressions) and macro TSMOM on SPY/TLT/GLD (B4, t=0.49) are dead ends *as expressed*. B4 is a **breadth** failure, not a verdict on trend. The repo's own lab showed Sharpe rising with instrument count (3 instruments 0.37 → 40 instruments 0.65, `REPORT.md:47-66` on `origin/claude/deep-research-project-6vr22g`).
- **Every rejection so far is "not confirmed", never "refuted".** The gate cannot say "no edge". Statuses from now on: `REJECTED` (powered to see the target effect, absent), `INCONCLUSIVE_UNDERPOWERED`, `CONFIRMED`.
- **Gate mis-specification (candidate audit findings, not applied):** (G1) `required_t_statistic` uses two-sided Bonferroni α/(2m) while the test is one-sided; for m=40 that is 3.227 vs 3.023 (DER). (G2) m counts ± direction pairs and overlapping lookbacks as independent trials although they are perfectly or highly correlated. These are the right place to relax the penalty. Any change applies to **new pre-registrations only**, fixed before observation, never retroactively to B2/B4.
- **Weather/Polymarket temperature R\***: external evidence is against the premise (arXiv 2609.23969, jattree/weather-edge −13.9% per trade, VF). A2 stays frozen.
- **Branches never merged hold useful negatives** (Fast Rail registry: sharp-vs-venue 0/60 capacity, HL listing fade top 10% of events = 98% of P&L, futures lab Sharpe 1.06 was cost-optimistic).

## 2. Ranked board (all NEW/RESURRECTED/MODIFIED labelled)

Columns: rank, family, mechanism & economic reason, prior evidence, status, public data/source, cheapest falsification test, leakage/multiple-testing/overfit risks, information gain, effort, my survival estimate (judgement, not a measurement).

| # | Family | Mechanism & economic reason | Evidence for / against | Status | Public data (credential-free) | Cheapest falsification test | Main risks | Info gain | Effort | P(survive net costs) |
|--:|---|---|---|---|---|---|---|---|---|---|
| 1 | **CRYPTO-CARRY** — delta-neutral spot-long/perp-short funding carry across 100+ USDT perps | Levered retail longs pay funding; arbitrage capital limited by margin/venue segmentation (He-Manela-Ross-von Wachter; Schmeling-Schrimpf-Todorov). Price-hedged, so **low volatility → statistically testable on 3–6 years** | FOR: arXiv 2212.06888 net Sharpe BTC 1.8…BNB 4.8, 2020-01..2024-03 (VF). AGAINST: |deviation| −11%/yr (VF); a 2025 survey claims Sharpe turned negative (UM) | NEW | Binance `data.binance.vision` monthly `fundingRate`, perp/spot 1m klines, incl. delisted symbols (listing VF); T&C **not yet read** | Freeze params on 2020-01..2023-12; sealed test 2024-01..2026-09; 7-day mean funding > fee-amortisation threshold; costs 0.05% perp + spot taker both legs, +5 bp non-top-20; 3x cap, liquidation on 1m high | Universe from file listing (survivorship), funding-interval switches (1h/4h/8h), effective n = days (~1000), exchange-failure tail not in sample, 3–4 cell grid counts as trials | **HIGH** — only candidate passable in 3–6y; rejection closes the family | Medium (1–2 wk) | 12% clears gate; ~35% net-positive but sub-gate |
| 2 | **KALSHI-FLB-OOS** — favourite-longshot bias, post-publication window, executable ask | Takers over-weight small probabilities; longshot sellers must lock 90c+ for 5–10c; makers sort beliefs (Bürgi-Deng-Whelan) | FOR: 46,282 contracts, 12,403 events to 2025-04; contracts ≤10c lose >60% post-fee (VF). AGAINST: decay in 2025, fees at mid prices, tail risk | RESURRECTED + MODIFIED (executable ask, post-cutoff holdout) | Kalshi public REST `/markets`, `/historical/trades`, candlesticks with bid/ask (docs VF; credential-free **probably**, confirm with one metadata call; ToS **not read**) | All binary markets settling 2025-05-01..freeze; paper's own filters; at T-24h buy side with ask ≥ 0.80, hold to settlement; fee schedule in force + 1c stress; maker fills NOT simulated; sports reported separately | Ask fallback pre-declared, cluster by event and date, threshold fixed (grid adds trials), fee schedule not yet fetched (429) | **HIGH** — thousands of independent events; ~360 events detect +2.5%, ~2,250 detect +1% (ASSUMED sd) | Small–medium (1–2 d) | 10% |
| 3 | **FORM4-HIST** — officer/director open-market purchase clusters, historical census then one test | Insiders know more than counterparties in illiquid small caps; capacity small, costs high | FOR: Lakonishok-Lee, Cohen-Malloy-Pomorski opportunistic trades (VF). AGAINST: >50% of trades routine (VF), post-publication decay | MODIFIED (the repo's frozen forward-only 3.6–5y plan becomes a historical development test) | SEC Insider Transactions Data Sets 2006–2026 (VF; no licence stated; 10 req/s, User-Agent required). **Prices: no credential-free delisting-inclusive source**; Yahoo survivors only | Step 0 outcome-blind census (no prices) 2006Q1–2023Q4 with the repo's frozen rule; stop if <800 clusters; then entry open after 2nd insider filing; 21 sessions primary; **m=3 → two-sided t 2.39**; holdout 2024+ sealed; 100 bp round trip central | Survivorship biases **toward** H1 so a null on survivors is conclusive against the lane; a positive needs a tipping-point bound; governance firewall for the forward cohort | **HIGH** — decides whether ~4,680 lines of capture + 3.6–5y plan are worth continuing | Medium–large (1–2 builds) | 4% |
| 4 | **BREADTH-TSMOM** — vol-scaled 12-month trend on 20–25 cross-asset ETFs from 2008 | Hedger risk transfer + under-reaction; breadth raises independent bets | FOR: lab Sharpe 0.22 (1) → 0.65 (40). AGAINST: B4 t=0.49; corrected lab costs removed most of the edge | MODIFIED (B4 breadth) + RESURRECTED (futures lab) | Existing Yahoo adapter (grey ToS); universe named once | One expression, 2008–2016 first-read window, sign of 252-day return | Universe choice = main degree of freedom; survivorship; same family as B4 | MEDIUM — screen only; cannot confirm at 3.227 on 8.7y (DER SE of Sharpe ≈ 0.34) | Small–medium | 5% |
| 5 | **KALSHI-TEMP-MOS** — daily-high bracket calibration vs archived MOS vintages | Retail anchors on app point forecasts; settlement-day quirks | UM/VF mix; weather market now the fastest-growing, forecast-driven | NEW | Kalshi API + Iowa Environmental Mesonet MOS archive (VF) | Fixed city list at freeze, latest GFS MOS/NBS, date-clustered | Vintage timing assumed; DST day-window mismatch | HIGH | Medium (3–5 d) | 6% |
| 6 | **CRYPTO-FUNDING-REV** — cross-sectional funding-sorted long/short (Codex P1) | Crowded levered longs unwind; reversal + funding collection | Indirect (Kozlowski-Puleo-Zhou reversal). Signal mechanically correlated with past returns | MODIFIED of rejected relative-value design, new universe | Same Binance files as #1 | Daily deciles, 30-day volume filter, fees+slippage | Directional ⇒ low-Sharpe ⇒ needs Sharpe ≥ 1.7–2.0 on the holdout | MEDIUM | Medium | 5% |
| 7 | **CROSS-VENUE-FUNDING** — Binance vs Bybit vs Hyperliquid spread | Venue segmentation of funding | Hyperliquid `predictedFundings` exposes it (VF) | NEW | Three REST APIs | Normalised per hour, daily rebalance | Basis risk on small coins, double taker costs | MEDIUM–HIGH | Medium | 8% |
| 8 | **LAZY-PRICES** — 10-K/10-Q language change, evaluated post-2015 | Hard-to-parse text under-reacted | Published effect; 58% average post-publication decay (McLean-Pontiff) | NEW | EDGAR full text | Single text-similarity score | Needs delisting-inclusive prices | MEDIUM | Large | 6% |
| 9 | **KALSHI-DUTCH** — intra-venue bracket sum arbitrage | Thin books, stale quotes | arXiv 2508.03474 (Polymarket) | MODIFIED of Codex #6 | Kalshi 1-min candles | Deterministic: any set with Σask<1 net of fees | Candle highs/lows need not coexist | MEDIUM (deterministic) | Small–medium | 3% |
| 10 | **GEFS-HDD→GAS** (Codex P2) | Forecast revisions price winter gas demand | Contemporaneous only (Hu et al. 2014) | MODIFIED | NOAA GEFS (AWS); **free NYMEX gas ends 2024-04-05**; no free intraday | Lead-lag, winter only, ~700 days | **A daily bar cannot test a tradable entry**: a null does not disprove an intraday edge; a positive is not tradable | MEDIUM-LOW | **High** (GRIB2) | 3% |
| 11 | **EIA-STORAGE-DRIFT** / **COT** / NT-filings / 13D / FOMC / buyback / short interest | Various | Mostly published, crowded or underpowered with free data | NEW/MODIFIED | Free CFTC/EIA/EDGAR | See agent notes | Power: ≈60–740 events; most cannot reach t>3 | LOW | Small–medium | 2–4% |
| 12 | **OVERNIGHT-001** (Q30 route 1) | Close-to-open premium vs daily round trip | STATE.md: +0.20 → −0.015 shift is inside noise | MODIFIED | Local panel, no acquisition | One SPY expression | Window spent; mostly beta | LOW-MEDIUM | Small | 3% |

Rejected without a test (reasons recorded, may be resurrected on new evidence): pre-FOMC drift (disappeared after 2015, ~8 events/yr), S&P/Russell index effects (competed away), cross-exchange latency arbitrage (needs ticks), BTC-only seasonality, single-asset funding-return prediction, token-unlock shorts (no point-in-time calendar), exchange-listing drift (documented effect is at an uncapturable horizon), Weather R\* on Polymarket.

## 3. Comparison with Codex board v1 (`2efa5e46…`)

| Codex rank | Claude disposition |
|---|---|
| 1 Crypto funding reversal | Same data. I rank the **carry** expression above the **reversal** expression because carry is low-volatility and passable. Reversal = my #6. Propose one crypto *family* with two pre-registered expressions sharing the family budget. |
| 2 GEFS-HDD → gas | **Disagree.** Daily bars cannot represent the intraday entry, free gas data ends 2024-04-05, setup cost is high. Information gain is mechanism-only. Keep as a reserve. |
| 3 Filing-timestamp PEAD | Needs delisting-inclusive single-stock prices; my elimination-test version ranks last (P≈1%). I replace it with Form-4 clusters (#3), where survivorship bias favours H1, so a null stays decisive. |
| 4 EIA storage gas | Merged into #11 (underpowered, consensus-free proxy). |
| 5 ETF close/open pressure | Merged with #12 (overnight diagnostic). |
| 6 Prediction-market cross-venue | **Moved to intra-venue** (#9) and, more importantly, replaced as the family by **#2 Kalshi favourite-longshot**, which has thousands of independent events. |
| 7 Overnight attribution | Same as #12. |

Genuine convergence: crypto funding first; avoid more sector-ETF variants; every test pre-registered before outcomes; negatives persisted.

## 4. Proposed TOP 3 (maximally different, provisional until Codex challenges)

| Slot | Family | Mechanism class | Market | Data type |
|---|---|---|---|---|
| F1 | CRYPTO-CARRY (#1; #6 as a second expression sharing the family budget) | Structural financing premium | Crypto perps | Funding + klines |
| F2 | KALSHI-FLB-OOS (#2) | Behavioural mispricing | Binary event contracts | Trades/candles/settlements |
| F3 | FORM4-HIST (#3) | Information asymmetry | US small-cap equities | Filings + survivor prices |

Reserve (not selected): BREADTH-TSMOM, KALSHI-TEMP-MOS, GEFS-HDD→GAS.

**Error-budget proposal (fixed now, before any outcome):** family-wise α = 0.05 split equally over F1/F2/F3 (≈0.0167 each) and Bonferroni **only within a family over its pre-declared expressions** (F1 m≤4 cells + 1 reversal expression, F2 m=1 primary, F3 m=3). The unified `40 + n` count does not apply to a new family on independent data; this follows from Codex's own reading of the rule (comment `6063017475`). Per-family thresholds are written into each pre-registration and cannot be moved after the outcome. Underpowered results are labelled `INCONCLUSIVE_UNDERPOWERED`, not `REJECTED`.

## 5. Acquisition manifest rules (reserve item 3 lifted by the Owner; terms of use first)

For each family, before any outcome is downloaded: (a) read and quote the terms of use of the source (Binance T&C, Kalshi API terms, SEC fair access); (b) publish source URLs, endpoints, parameters, planned file list, expected hashes, sealed-holdout boundaries; (c) a pre-registration with a primary statistic, a gate, a rejection rule and a stop rule; (d) User-Agent without personal information; respect rate limits; (e) on acquisition record retrieval time, raw hashes, row/time bounds, missingness. No paid source, account or credential is used. If Kalshi requires registration, F2 is re-routed, not forced.

## 6. Open issues for Codex to challenge

1. F1 expression set (carry primary; is the reversal expression worth the budget?).
2. F2: ask ≥ 0.80 at T-24h versus another fixed rule; which categories form the primary subsample.
3. F3: governance firewall question (is pre-2026 historical filing evidence DEVELOPMENT outside the forward cohort firewall?) and the survivor-price source.
4. The proposed per-family α split and G1/G2 handling.
5. Whether the reserve should rank GEFS above BREADTH-TSMOM.
