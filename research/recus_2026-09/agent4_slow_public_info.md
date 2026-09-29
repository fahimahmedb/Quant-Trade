# AGENT 4 — SLOW PUBLIC INFORMATION — deliverable

Date: 2026-09-29. External research + public-API measurement only. No orders, no strategy code, no wallet de-anonymisation.
REAL_CAPITAL_AUTHORIZED = FALSE.

Question answered: *outside weather*, where is there a **receipt** (third-party-verifiable realized P&L) that someone gets paid by trading **public information that arrives slowly before an objective resolution**, at a size and speed a small automated participant could plausibly match?

Reading rule: figures marked **(V)** were computed by this agent on 2026-09-29 from public endpoints (`data-api.polymarket.com` leaderboard / closed-positions / trades / activity, `user-pnl-api.polymarket.com`, `gamma-api.polymarket.com`). Figures marked (S) come from a secondary source and were not re-derived. "Unknown" means unknown; nothing is invented.

## 0. Exclusion map (what agents 1–3 already settled; not re-done here)

| Already covered | Verdict carried forward |
|---|---|
| Polymarket weather (R1/F3) | out of scope for this mission by order |
| Polymarket maker subsidies / rebates (R2/F4) | subsidy verified, net at small size unverified, likely ≤ 0 |
| Polymarket sports MM (R3), Hyperliquid MM (R4) | speed + capital; dead at small size |
| NegRisk / intra-market arbitrage (R5/F5, agent 2 R1) | receipt is 2024-25, pre-fee; contested ×100; speed-competed |
| Hyperliquid vaults / copy-trading (R6/F2) | negative expectancy; beta |
| Kalshi & Betfair maker vs taker (agent 2 R2/R3) | takers lose 2.5–31 %; makers ≈ 0 to +2.4 % gross; Kalshi US-only |
| Metaculus / Numerai payouts (agent 2 R4/R5) | prize pools, not markets; already carded |
| Polymarket ↔ Kalshi cross-venue (agent 2 R6) | no realized-profit receipt; dual access illegal |
| Uniswap LP (agent 2 R7) | LPs lose in aggregate |
| Standing rejections | carry, HLP, copy-trading, SPAC/merger arb, favourites > 90 ¢ (as a blind taker rule), systematic NO, 15-min crypto latency, soft-book value betting, pre-unlock shorts |

## 1. Method and funnel (receipt-first)

**Phase A — 12 preliminary mechanisms** (who pays / why / why competition has not removed it / why small size helps):

| # | Mechanism | Slow public information | Gate result |
|---|---|---|---|
| P1 | Polymarket weekly/2-day **tweet-count buckets** (Elon Musk) | xtracker.io post counter (resolution source), pace accrues hour by hour | → Phase C (C1) |
| P2 | Polymarket **opening-weekend box office / total-gross / Rotten Tomatoes** brackets | Thursday previews, Friday actuals, Sunday studio estimates, The Numbers finals; RT score as reviews accrue | → Phase C (C2) |
| P3 | Polymarket **"best AI model end of month"** (arena.ai rank) | model releases are announced; leaderboard rank updates days later as votes accrue | → Phase C (C3) |
| P4 | Polymarket **Spotify / chart** markets (top artist this month, streams) | daily chart data (Spotify charts, kworb) accrues over the month | → Phase C (C4) |
| P5 | Polymarket **mention markets** ("What will X say during…") | transcripts / live speech | → Phase C (C5), recency check |
| P6 | **Post-determination, pre-resolution capture** across P1–P4 (buy ≥ 0.90 once the public figure makes the outcome near-certain) | same sources; the lag is the resolution delay | → Phase C (C6) |
| P7 | Kalshi measurement series (TSA throughput, gas price, RT, Netflix, measles…) | daily official series | **DROPPED**: Kalshi exposes no per-account P&L; the only public "TSA bot" write-up (ferraijv blog) reports no P&L; the Bürgi–Deng–Whelan aggregate (takers −31 %, makers −10 %) is already carded by agent 2 |
| P8 | Airdrop / points farming (on-chain receipts) | eligibility criteria are public; distribution is later | **DROPPED**: Luo et al. 2025 (arXiv 2503.14316) measure Hop/LayerZero hunters: 69 % of 150 Hop groups net-positive but per-address reward < $350, most groups < $10 k, data 2021–24; sybil filtering has tightened since; labour, not a market edge |
| P9 | LST discount / withdrawal-queue capture (stETH) | queue length and discount are on-chain | **DROPPED**: episodic (depeg stress only), ETH beta unless hedged (→ carry, rejected), no per-wallet realized-P&L study found in a bounded search |
| P10 | Exchange listing-announcement effect (Coinbase/Binance/Upbit) | listing notices precede trading by hours | **DROPPED**: effect concentrated on Coinbase, negative after Binance/Gemini (S); seconds-scale competition and insider cases; fails speed + competition tests |
| P11 | Bitcoin difficulty / hashrate markets | difficulty is deterministic from public block times | **DROPPED**: no live venue found in a bounded search |
| P12 | Election-night count-lag trading (down-ballot) | official county counts vs lagging prices | **DROPPED**: one-event-per-cycle; the only receipts in the literature (Théo, cross-platform arbs, arXiv 2603.03152) are pre-election whale bets and arbitrage, not count-lag; survivorship-dominated |

**Phase B — receipt gate**: the Polymarket data API exposes per-wallet realized P&L (`closed-positions`), a daily mark-to-market series (`user-pnl`), and on-chain reward/rebate payments (`activity`). Categories with a leaderboard: WEATHER, POLITICS, SPORTS, CRYPTO, CULTURE, ECONOMICS, TECH, FINANCE, MENTIONS (V). I pulled the top 25 by P&L (MONTH and ALL) for CULTURE, MENTIONS, ECONOMICS, TECH, FINANCE (214 wallets), classified every closed position by title into mechanism classes, then pulled the **full** closed-position history (up to 3 000), the P&L curve and reward/rebate payments for 25 specialist wallets (tweets 8, box office 4, music 2, AI 6, mentions 5). Nobody was de-anonymised; usernames are the API's public display names.

**Fee context (V, gamma `feeSchedule` on 2026-09-29)**: tweet-count and AI-model events carry a taker-only fee `rate 0.04`, box-office / Rotten Tomatoes / Spotify events `rate 0.05`, all with `rebateRate 0.25` to makers. Fee per share ≈ rate × p × (1−p) (agent 1). Events created before spring 2026 carry no fee. The `closed-positions` endpoint no longer returns `entryFeesUsdc` (V), so net-of-fee semantics are inherited from agent 1's same-day observation, not re-verified here.

## 2. Receipt semantics (read before the cards)

Three public P&L views exist per wallet and they disagree in predictable ways (V):

- `closed-positions` (realized per position) **excludes resolved losing positions that were never redeemed** (they sit in `positions` with `curPrice = 0`) and assigns a near-zero cost basis to positions obtained by splitting full sets. It therefore **overstates** lottery-style buyers and split-heavy makers. Example: wallet `0x8565…0c43` shows +216 687 $ "realized" on tweet buckets over 12 months but carries 979 unredeemed losing buckets worth −339 739 $.
- `positions` (open) gives the unbooked losses (`cashPnl` with `curPrice = 0`) and live mark-to-market.
- `user-pnl` (daily series) is mark-to-market including those losers and is consistent with `closed + dead + live` wherever both were checkable (10 of 10 wallets with open positions). **All receipt amounts below use `user-pnl` over the last 12 months as the conservative figure; `closed-positions` is used only to attribute P&L to a market family.**

Per-wallet receipt table (V, 2026-09-29; identifiers are the API's public display names, not people):

| wallet | family / name | family realized 12m (closed-pos) | other-family realized | unredeemed losers (n) | live open cashPnl (n) | **user-pnl 12m** | user-pnl since first point | first point | last family month |
|---|---|---|---|---|---|---|---|---|---|
| 0x689a…779e | TWEETS Annica | 3 325 136 | 246 | 0 (0) | 0 (0) | **715 026** | 738 864 | 2025-08-26 | 2026-07 |
| 0x063a…eb4b | TWEETS noovd | 241 160 | −2 131 | −1 736 (3) | −268 (2) | **249 692** | 342 098 | 2024-11-28 | 2026-01 |
| 0x5e22…3993 | TWEETS 0xecc… | 59 272 | 9 863 | 0 (0) | 0 (0) | **94 684** | 211 416 | 2025-01-12 | 2026-01 |
| 0x90ed…b5bc | TWEETS failstober | 289 823 | 233 758 | −161 894 (86) | −13 453 (84) | **434 661** | 434 814 | 2025-11-11 | 2026-04 |
| 0x8565…0c43 | TWEETS dddtrips | 216 687 | 82 593 | −339 739 (979) | −208 (19) | **−28 932** | −29 455 | 2025-07-29 | 2026-09 |
| 0x524d…4495 | TWEETS Mac-Gyver | 88 968 | 83 157 | −162 724 (375) | 11 127 (46) | **43 275** | 43 137 | 2026-06-26 | 2026-09 |
| 0xb0cc…f09b | TWEETS EffyBig | 15 676 | −52 | −2 973 (68) | 0 (0) | **22 083** | 22 084 | 2026-03-31 | 2026-09 |
| 0xf14e…6173 | TWEETS 0xf14e… | 10 388 | 0 | −3 210 (3) | 333 (5) | **8 578** | 8 576 | 2026-07-22 | 2026-09 |
| 0x06dc…af59 | BOX Big.Chungus | 96 774 | 216 931 | 0 (0) | 0 (0) | **269 106** | 365 348 | 2024-11-28 | 2026-06 |
| 0x9aeb…2729 | BOX The-Joker | 60 790 | 66 866 | −1 872 (5) | 6 031 (49) | **158 771** | 158 866 | 2025-10-15 | 2026-09 |
| 0x33f8…c5e4 | BOX fanat12 | 30 492 | 525 | −1 296 (13) | −187 (15) | **36 042** | 36 050 | 2025-10-19 | 2026-09 |
| 0x7056…c95c | BOX denzeldumfries | 28 019 | 230 | −723 (1) | 4 263 (17) | **42 264** | 42 362 | 2026-06-16 | 2026-09 |
| 0xe904…2d9f | MUSIC shovelingdigging | 11 960 | 25 816 | −487 (1) | 5 207 (49) | **47 355** | 47 357 | 2026-01-03 | 2026-09 |
| 0x9578…f066 | MUSIC KimchiCapital | 5 698 | 18 862 | −48 (1) | 5 582 (149) | **34 264** | 34 263 | 2025-12-30 | 2026-09 |
| 0x81ca…3b87 | AI orac07 | 21 089 | −10 | −855 (7) | 10 066 (9) | **31 491** | 34 658 | 2025-03-01 | 2026-09 |
| 0xf0ca…66ed | AI Hauchn | 151 359 | 65 339 | −2 305 (15) | −2 116 (16) | **359 230** | 359 224 | 2025-01-01 | 2026-09 |
| 0xb89f…1c44 | AI iutwpfal | 20 944 | 66 857 | −11 (1) | 1 583 (59) | **92 740** | 92 760 | 2026-01-11 | 2026-09 |
| 0x38d8…ea7c | AI thanksforplayin | 154 018 | 559 746 | 0 (0) | 1 163 (21) | **259 497** | 259 859 | 2024-11-28 | 2026-09 |
| 0x17ce…beec | AI fffffz | 27 556 | 78 416 | 0 (0) | −18 (1) | **4 538** | 87 834 | 2025-01-08 | 2026-05 |
| 0xc451…2609 | AI beeply | 52 317 | 56 726 | −18 320 (8) | 0 (0) | **89 591** | 86 714 | 2025-08-04 | 2026-07 |
| 0x7bda…121b | MENT anon1565 | 0 | −243 847 | 0 (0) | 0 (0) | **0** | −238 669 | 2024-11-28 | 2024-11 |
| 0xe4e2…f26c | MENT Ch5 | 0 | 1 573 | −6 502 (13) | 0 (0) | **−4 037** | 130 035 | 2024-11-28 | 2024-10 |
| 0x8f62…02ef | MENT JanSobieski3 | 0 | 28 740 | −832 (2) | 0 (0) | **−449** | 116 666 | 2024-11-28 | 2025-01 |
| 0x7a70…52cc | MENT Mr-Yolos | 0 | −113 236 | 0 (0) | 0 (0) | **−13 156** | −30 090 | 2024-11-28 | 2025-01 |
| 0x9981…dec4 | MENT EscalateFund | 25 108 | 399 151 | −301 407 (66) | 0 (0) | **69 886** | 207 207 | 2024-11-28 | 2026-03 |

Monthly family-realized series (closed-pos, attribution only, last six active months):
- Annica (tweets): Feb-26 +952 k, Mar +984 k, Apr +289 k, May +214 k, Jun +90 k, Jul +16 k, then nothing. 35 % of its tweet markets held both outcomes and its largest positions carry an average price of 0.00 (split-and-sell), i.e. a structured maker, not a forecaster. user-pnl +715 k vs closed-pos +3.3 M: split accounting inflates the latter ×4.6.
- noovd: last month Jan-26 (−183 k); 0xecc…: last month Jan-26 (−261 k); failstober: Jan +112 k, Feb +202 k, Mar −26 k, Apr −2 k, then stopped. All four large 2025-26 tweet winners exited between January and April 2026, i.e. around the fee introduction (spring 2026) and the volume decline (weekly events 4–10 M$ in late 2025 → 1–2 M$ in September 2026, V).
- Box office: The-Joker Apr +3.3 k, May +0.8 k, Jun +7.9 k, Jul +12.9 k, Aug +10.1 k, Sep +6.7 k; fanat12 Apr −1.3 k, May +1.3 k, Jun +3.0 k, Jul +6.2 k, Aug +4.2 k, Sep +0.5 k; denzeldumfries Jun +4.8 k, Jul +8.4 k, Aug +1.7 k, Sep +13.1 k; Big.Chungus faded to ≈ 0 after March 2026.
- Music: shovelingdigging ≈ +0.4 to +3.2 k/month; KimchiCapital ≈ +0.3 to +3.0 k/month.
- AI-leaderboard: orac07 +9.5 k (Apr) and +10.3 k (Aug), ≈ 0 otherwise; iutwpfal −4 k to +10.7 k/month with 38 % two-sided markets. Hauchn's +205 k (Jul-26) is one "largest company by market cap on July 31" event; thanksforplayin's positions are daily stock-close markets with a 100 % closed-position win rate (unredeemed-loser artefact) — neither is slow information.
- Mentions: every specialist's family P&L dates from Aug 2024–Jan 2025; 12-month user-pnl is ≤ 0 for four of five. Speech-time information, decayed → **C5 dropped**.

## 3. Candidate cards (Phase D survivors, ranked in §6)

### SPI-1 — Opening-weekend box-office brackets (Polymarket "Movies")

| Field | Content |
|---|---|
| ID | SPI-1 BOX-OFFICE |
| TITLE | Weekly bracket markets on a film's 3-day domestic opening (and total-gross / nth-weekend siblings), resolved on The Numbers finals |
| ECONOMIC TYPE | information |
| MARKET / VENUE | Polymarket, category CULTURE → Movies. 111 active box-office markets on 2026-09-29 (S, polymarket.com). Recent events: 7 k–343 k$ volume each, 6–10 brackets, taker fee rate 0.05 (V) |
| PUBLIC INFORMATION USED | Tracking (long lead), Thursday previews (Fri morning), Friday actuals (Sat morning), Saturday estimate + Sunday studio estimate (Sun ~11:00 ET), The Numbers finals (Mon/Tue). All free, all timestamped |
| INFORMATION LATENCY | hours to days; the last-mile information (estimate → final) takes ~24 h |
| MECHANISM | Recreational film bettors and slow limit orders price brackets on tracking and intuition; the Friday/Saturday numbers pin the weekend within a few percent, and the estimate-to-final revision decides boundary cases. Whoever updates first on each public release is paid by whoever does not |
| WHY IT MAY PERSIST | Markets are tiny (winning bracket 25–30 k$ of volume across a week, V), recur weekly, need a domain-specific reader; the fee is 0.05·p(1−p), small at the extremes |
| RECEIPT | `user-pnl` 12 m (V): The-Joker `0x9aeb…2729` +158 771 $ (box-office share of closed realized: 60 790 $); fanat12 `0x33f8…c5e4` +36 042 $ (30 492 $ box); denzeldumfries `0x7056…c95c` +42 264 $ (28 019 $ box, since 2026-06); Big.Chungus `0x06dc…af59` +269 106 $ (96 774 $ box, but box activity ended 2026-03). Unredeemed losers small (≤ 1.9 k$ each, V) |
| RECEIPT PERIOD | 2025-10 → 2026-09 (three wallets active in September 2026) |
| LAST OBSERVED PROFITABLE DATE | September 2026 (closed positions dated 2026-09-24 and later, V) |
| REALIZED OR SIMULATED? | realized (on-chain, public API) |
| GROSS OR NET? | net of Polymarket trading fees as booked by the platform (user-pnl); before infrastructure cost |
| FEES INCLUDED? | yes for trades since the fee rollout (rate 0.05 on these events, V); the endpoint no longer exposes the fee field, so the netting is inherited from agent 1's same-day check, not re-verified |
| CAPITAL ACTUALLY IMMOBILIZED | estimated from live open positions: The-Joker ≈ 100 k$, denzeldumfries ≈ 28 k$, fanat12 ≈ 4 k$ (V, snapshot). Turnover: The-Joker bought 1.14 M$ of box-office positions in 12 m |
| OBSERVED P&L / RETURN | family realized / family bought: The-Joker 5.3 %, fanat12 3.7 %, denzeldumfries 12.4 %, Big.Chungus 5.3 % per dollar traded (V); ≈ 0.5–13 k$/month per wallet in the last four months |
| LOSERS | see §4: sample of the 70 most active participants of three September-2026 events, corrected for unredeemed losers and cross-checked with user-pnl |
| SURVIVORSHIP RISK | High by construction (wallets found via the P&L leaderboard). Mitigated only by §4. Big.Chungus exiting after March 2026 is a warning |
| SPEED REQUIREMENT | none below minutes: the two September winners' brackets traded at 0.15–0.39 VWAP all Saturday and Sunday and converged only Monday (V) |
| DATA REQUIREMENT | The Numbers / Box Office Mojo pages, Deadline/Variety estimate posts, Polymarket CLOB; an archive of estimates vs finals for calibration |
| MINIMUM CAPITAL | 1–5 k$ (positions of 0.7–2 k$ per bracket are typical for the receipts, V) |
| CAPACITY AT SMALL SIZE | ≈ 1–5 k$ per event without moving the book; 3–6 events per weekend |
| POTENTIAL MONTHLY € AT SMALL SIZE | UNKNOWN; the receipts show 0.5–13 k$/month for wallets turning 30–100 k$; nothing is demonstrated for a new entrant |
| MAIN HIDDEN RISK | Boundary cases: both September winners' Sunday estimates sat exactly on a bracket edge (Forgotten Island 12.8 M$ vs the 13 M line; Heart of the Beast 20.0 M$ vs the 20 M line, S: Deadline/GoldDerby), so the weekend "uncertainty" was real, not a lag; estimate-to-final revisions decide the bracket. Also: resolution-source edits, fee changes, thin books |
| WHY LARGE PROFESSIONAL CAPITAL MAY NOT FULLY ARBITRAGE IT | 25–30 k$ of winning-bracket volume per film per week cannot absorb a fund; the work is manual-domain and low-notional |
| ACCESS | Polymarket international: US and France close-only per official geoblock list (agent 1); the owner declares access from their location; must be confirmed with `GET polymarket.com/api/geoblock` |
| CAN QUANT VERIFY IT IN ≤ 1 DAY USING PUBLIC DATA? | yes: (1) pull every box-office event of the last 26 weeks from gamma, (2) rebuild bracket VWAPs by hour from `trades`, (3) join with the public Friday actual / Sunday estimate timeline, (4) measure the return of buying the bracket implied by each public release at the prevailing ask, net of 0.05·p(1−p) |
| CHEAPEST FALSIFICATION EXPERIMENT | the 1-day replay above with strict timestamps; the edge is falsified if the post-release implied bracket is already ≥ 0.85 within one hour of each public release, or if the estimate-to-final revision flips brackets more often than the price gap pays |
| CONFIDENCE | **PROBABLE** (receipts verified and recent; reproducibility not shown) |

### SPI-2 — Elon Musk tweet-count buckets (weekly and 2-day)

| Field | Content |
|---|---|
| ID | SPI-2 TWEET-COUNT |
| TITLE | "How many tweets will Elon Musk post from D1 to D2?" bucket markets, resolved on the xtracker.io post counter |
| ECONOMIC TYPE | information |
| MARKET / VENUE | Polymarket CULTURE. Weekly events 1.1–2.0 M$ and 2-day events 0.4–0.7 M$ in September 2026, versus 4–10 M$ per weekly event in late 2025 (V); taker fee rate 0.04 (V); events since June 2024 |
| PUBLIC INFORMATION USED | the resolution counter itself, readable continuously; pace and intraday patterns; 86 weeks of history are public (S, Polymarket "Tweet Quant" newsletter) |
| INFORMATION LATENCY | minutes to hours (the count accrues in real time; buckets close on a fixed timestamp) |
| MECHANISM | Recreational buyers pay for lottery buckets (avg entry ≤ 0.15) that the current pace already makes unlikely; two-sided makers and late NO-sellers are paid the excess. The four large 2025-26 winners were all mostly two-sided (12–35 % of markets held both outcomes) and one is a split-and-sell maker (Annica) |
| WHY IT MAY PERSIST | New event every 2–7 days, heavy retail flow, cheap buckets are attractive to gamblers |
| RECEIPT | `user-pnl` 12 m (V): Annica `0x689a…779e` +715 026 $; failstober `0x90ed…b5bc` +434 661 $; noovd `0x063a…eb4b` +249 692 $; 0xecc `0x5e22…3993` +94 684 $ — all four **stopped or collapsed between Jan and Apr 2026**. Active in September 2026: EffyBig `0xb0cc…f09b` +22 083 $ since 2026-03-31 (41 % two-sided); 0xf14e `0xf14e…6173` +8 578 $ since 2026-07-22 (buys NO at 0.84–0.90 on buckets already out of reach); Mac-Gyver `0x524d…4495` +43 275 $ since 2026-06 (but −162 724 $ of unredeemed losers against +172 k$ closed realized, i.e. ≈ break-even on tweets, V); dddtrips `0x8565…0c43` **−28 932 $** despite +216 687 $ "realized" |
| RECEIPT PERIOD | 2025-08 → 2026-09 |
| LAST OBSERVED PROFITABLE DATE | September 2026 for the small active wallets; February–March 2026 for the large ones |
| REALIZED OR SIMULATED? | realized (user-pnl); the "92.8 % win rate on NO of 10–20 % buckets" in Polymarket's own newsletter is a **backtest** (S) |
| GROSS OR NET? | net of platform fees as booked |
| FEES INCLUDED? | fee rate 0.04 applies to 2026 events (V); the large receipts are mostly pre-fee |
| CAPITAL ACTUALLY IMMOBILIZED | unknown for the large wallets (they turned 20–50 M$/yr); live open positions ≈ 64 k$ (Mac-Gyver), 14 k$ (0xf14e), 0 (EffyBig turns over fully each week) (V) |
| OBSERVED P&L / RETURN | large winners: 0.3–6.6 % per dollar traded (V, closed-pos, upper-biased); active small wallets: ≈ 2–4 k$/month (EffyBig), +8.6 k$ over ten weeks (0xf14e) |
| LOSERS | see §4 (70 most active participants of the September-2026 monthly event). Public secondary case: "sb911", celebrated in April–May 2026 for +106 k$ in one month on cheap buckets, now shows −31.4 k$ lifetime on its public profile (S, polymarket.com/@sb911, 2026-09-29) |
| SURVIVORSHIP RISK | very high: leaderboard selection + the unredeemed-loser artefact makes cheap-bucket buyers look profitable when they are not |
| SPEED REQUIREMENT | low for pace-based selling of dead buckets; the maker variant needs order-management in seconds |
| DATA REQUIREMENT | xtracker.io counter (also via elon-tracker / xtracker APIs, S), Polymarket CLOB, history of bucket prices |
| MINIMUM CAPITAL | 1–3 k$ (EffyBig's average position is 1.7 k$, V) |
| CAPACITY AT SMALL SIZE | ample (1–2 M$ weekly events) |
| POTENTIAL MONTHLY € AT SMALL SIZE | UNKNOWN; the only consistent small receipt is ≈ 2–4 k$/month over six months |
| MAIN HIDDEN RISK | The edge that paid 0.7–3 M$ per wallet in 2025-26 is gone from the receipts (all four exited); what remains is a small two-sided/late-NO residual that competes with bots reading the same counter. Counter outages/definition changes (replies, deleted posts) are resolution risk |
| WHY LARGE PROFESSIONAL CAPITAL MAY NOT FULLY ARBITRAGE IT | it partly did: the largest wallets are structured makers turning tens of millions; the residual is too small and too silly for funds |
| ACCESS | as SPI-1 |
| CAN QUANT VERIFY IT IN ≤ 1 DAY USING PUBLIC DATA? | yes: replay the last 12 weekly events with bucket price paths (trades endpoint) against the counter's timestamped pace (xtracker export); compute the return of selling/buying-NO on buckets already outside the reachable range at the prevailing bid, net of 0.04·p(1−p) |
| CHEAPEST FALSIFICATION EXPERIMENT | the replay above; falsified if dead-bucket asks are < 0.02 within an hour of becoming unreachable (nothing left to sell) |
| CONFIDENCE | receipts **VERIFIED** (historical, large) / **PROBABLE** (small, current); persistence **UNVERIFIED** |

### SPI-3 — Music chart / album-sales / streaming-count markets

| Field | Content |
|---|---|
| ID | SPI-3 MUSIC-COUNTS |
| TITLE | "Will X be the Billboard 200 #1 / Hot 100 #k", "debut-week album sales between a and b", "top Spotify artist this month", "monthly listeners ≥ N by date" |
| ECONOMIC TYPE | information |
| MARKET / VENUE | Polymarket CULTURE → Music. Monthly "top Spotify artist" events 0.5–1.1 M$ (V); album-sales and chart-position markets much smaller; fee rate 0.05 (V) |
| PUBLIC INFORMATION USED | HITS Daily Double / Luminate mid-week sales projections, Spotify daily charts, Billboard rules (release timing, bundles), Spotify monthly-listener pages |
| INFORMATION LATENCY | days (a chart week is 7 days; projections update mid-week) |
| MECHANISM | Fans and casual traders price on sentiment; chart mechanics are rule-based and mid-week projections are public and accurate to a few percent |
| WHY IT MAY PERSIST | tiny notional, requires niche knowledge, recurs weekly |
| RECEIPT | `user-pnl` 12 m (V): shovelingdigging `0xe904…2d9f` +47 355 $ (music share of closed realized 11 960 $ on 209 k$ bought, 75 % win rate, 288 positions); KimchiCapital `0x9578…f066` +34 264 $ (5 698 $ music on 138 k$, 82 % win rate). Unredeemed losers ≤ 0.5 k$ |
| RECEIPT PERIOD | 2026-01 → 2026-09 |
| LAST OBSERVED PROFITABLE DATE | September 2026 |
| REALIZED OR SIMULATED? | realized |
| GROSS OR NET? | net of platform fees as booked |
| FEES INCLUDED? | yes (rate 0.05 events) |
| CAPITAL ACTUALLY IMMOBILIZED | live open positions ≈ 27 k$ and ≈ 34 k$ (V, mostly other families) |
| OBSERVED P&L / RETURN | 4–6 % per dollar traded on music positions; ≈ 0.3–3 k$/month per wallet |
| LOSERS | not sampled (budget); unknown |
| SURVIVORSHIP RISK | high (leaderboard selection, only two wallets, short history) |
| SPEED REQUIREMENT | none |
| DATA REQUIREMENT | HITS/Billboard projections, Spotify charts (kworb mirrors), Polymarket CLOB |
| MINIMUM CAPITAL | < 1 k$ (average position 0.4–0.7 k$, V) |
| CAPACITY AT SMALL SIZE | very small (hundreds of dollars per market) |
| POTENTIAL MONTHLY € AT SMALL SIZE | UNKNOWN; receipts ≈ 1 k$/month |
| MAIN HIDDEN RISK | chart-rule changes and data-source disputes; capacity |
| WHY LARGE PROFESSIONAL CAPITAL MAY NOT FULLY ARBITRAGE IT | notional too small |
| ACCESS | as SPI-1 |
| CAN QUANT VERIFY IT IN ≤ 1 DAY USING PUBLIC DATA? | partially: bracket price paths vs dated projection posts; projection archives are less clean than box office |
| CHEAPEST FALSIFICATION EXPERIMENT | replay 8 recent album-sales bracket events against the HITS mid-week projection timestamp |
| CONFIDENCE | **PROBABLE** (receipts verified; small; losers unknown) |

### SPI-4 — "Which company has the best AI model at end of month" (arena.ai rank)

| Field | Content |
|---|---|
| ID | SPI-4 AI-LEADERBOARD |
| TITLE | Monthly multi-outcome markets resolved on the arena.ai Text Arena overall rank at a fixed check time (plus "model X debuts at score ≥ s" siblings) |
| ECONOMIC TYPE | information |
| MARKET / VENUE | Polymarket TECH/CULTURE. Monthly events 4.1 M$ (Sep 2026), 29–36 M$ (Dec 2025 / Jan 2026) (V); fee rate 0.04 |
| PUBLIC INFORMATION USED | model release announcements, arena.ai leaderboard (public, updates as votes accrue over days), style-control and AutoEval rules in the market text |
| INFORMATION LATENCY | days (release → enough votes for a stable rank) |
| MECHANISM | hype traders price on release news; the leaderboard mechanics (vote accrual, style control off, tie-breaks by score then company name) are knowable and slow |
| WHY IT MAY PERSIST | the check-time rule and leaderboard quirks reward reading the resolution text; but the markets are large and liquid |
| RECEIPT | `user-pnl` 12 m (V): orac07 `0x81ca…3b87` +31 491 $ (AI share 21 089 $, two events April/August 2026 dominate; ≈ 0 in other months); iutwpfal `0xb89f…1c44` +92 740 $ (AI share 20 944 $, 38 % two-sided, rewards 3.1 k$). Other TECH-leaderboard wallets tested are **not** slow-information: Hauchn's +205 k$ is one "largest company by market cap on July 31" event; thanksforplayin trades daily stock-close markets |
| RECEIPT PERIOD | 2026-04 → 2026-09 |
| LAST OBSERVED PROFITABLE DATE | September 2026 (iutwpfal +10.7 k$ in AI markets) |
| REALIZED OR SIMULATED? | realized |
| GROSS OR NET? | net as booked |
| FEES INCLUDED? | yes for 2026 events |
| CAPITAL ACTUALLY IMMOBILIZED | live open ≈ 1 k$ (orac07) and ≈ 27 k$ (iutwpfal) (V) |
| OBSERVED P&L / RETURN | 1.9 % (iutwpfal) and 15 % (orac07, two events) per dollar traded |
| LOSERS | not sampled; unknown |
| SURVIVORSHIP RISK | very high: two small wallets, lumpy P&L, one of them a maker |
| SPEED REQUIREMENT | low for the monthly rank; the "debut score" siblings resolve fast |
| DATA REQUIREMENT | arena.ai leaderboard scrape at the market's exact filter settings; release calendars |
| MINIMUM CAPITAL | 1 k$ |
| CAPACITY AT SMALL SIZE | large |
| POTENTIAL MONTHLY € AT SMALL SIZE | UNKNOWN |
| MAIN HIDDEN RISK | the market is big enough for informed labs' employees and fast traders; resolution-rule edge cases (AutoEval flags, style control, ties) |
| WHY LARGE PROFESSIONAL CAPITAL MAY NOT FULLY ARBITRAGE IT | unclear that it does not; volumes of 4–36 M$ attract sophisticated flow |
| ACCESS | as SPI-1 |
| CAN QUANT VERIFY IT IN ≤ 1 DAY USING PUBLIC DATA? | partially: price paths of the eventual winner across the last 8 monthly events vs dated leaderboard snapshots (Wayback) |
| CHEAPEST FALSIFICATION EXPERIMENT | that replay; falsified if the winner already trades ≥ 0.9 within a day of each rank change |
| CONFIDENCE | **UNVERIFIED** as an edge (receipts small and lumpy) |

### SPI-5 — Post-determination, pre-resolution capture (cross-family)

| Field | Content |
|---|---|
| ID | SPI-5 POST-DETERMINATION |
| TITLE | Buying the side already decided by the public figure at 0.85–0.97 and holding to resolution (the non-weather analogue of HighTempTation in agent 1's R1) |
| ECONOMIC TYPE | structural (resolution lag) |
| MARKET / VENUE | any Polymarket count/bracket market: tweet buckets once the count passes a bound, box-office brackets after the final, chart markets after the chart posts |
| PUBLIC INFORMATION USED | the resolution source itself |
| INFORMATION LATENCY | hours to days between determination and UMA resolution |
| MECHANISM | holders of the losing side sell late or never; impatient winners sell at a discount; the buyer earns the discount for locking capital and bearing resolution risk |
| WHY IT MAY PERSIST | fee 0.04–0.05·p(1−p) is ≈ 0.1–0.4 % at p ≥ 0.9; too small and too slow for bots on tiny markets; capital lock-up deters |
| RECEIPT | (V) aggregates over the specialist wallets, closed positions with average entry ≥ 0.90: tweets 916+ positions 1.7 % return on 9.7 M$ bought; box office 3.5 % on 1.14 M$; music 4.2 % on 124 k$; **AI −16.5 % on 335 k$** (losing). One wallet is a clean small case: 0xf14e `0xf14e…6173`, 71 of 92 positions at ≥ 0.90, NO bought at 0.84–0.90 on unreachable tweet buckets, user-pnl +8 578 $ since 2026-07-22 |
| RECEIPT PERIOD | 2025-10 → 2026-09 |
| LAST OBSERVED PROFITABLE DATE | September 2026 |
| REALIZED OR SIMULATED? | realized (aggregates are upper-biased by the closed-position artefact; 0xf14e is user-pnl) |
| GROSS OR NET? | net as booked |
| FEES INCLUDED? | yes for 2026 events |
| CAPITAL ACTUALLY IMMOBILIZED | ≈ the full notional for 1–7 days per position (14 k$ live for 0xf14e, V) |
| OBSERVED P&L / RETURN | 1.7–4.2 % per dollar for tweets/box/music entries ≥ 0.90; negative for AI |
| LOSERS | the AI aggregate is the loser; box-office boundary cases (Forgotten Island, Heart of the Beast) show that "determined" is often not determined |
| SURVIVORSHIP RISK | high; 0xf14e has ten weeks of history |
| SPEED REQUIREMENT | low (the discount persists for hours) but competition from bots is likely on the larger markets |
| DATA REQUIREMENT | live resolution sources + CLOB |
| MINIMUM CAPITAL | 1 k$ |
| CAPACITY AT SMALL SIZE | a few k$ per market |
| POTENTIAL MONTHLY € AT SMALL SIZE | UNKNOWN; annualised 1.7–4.2 % per 1–7-day lock-up is large only if turnover is high |
| MAIN HIDDEN RISK | resolution disputes and source revisions (finals vs estimates; counter definition changes); one bad resolution erases many 2 % gains |
| WHY LARGE PROFESSIONAL CAPITAL MAY NOT FULLY ARBITRAGE IT | capital lock-up in tiny markets |
| ACCESS | as SPI-1 |
| CAN QUANT VERIFY IT IN ≤ 1 DAY USING PUBLIC DATA? | yes: for resolved bracket markets, measure the asks available after the public determination timestamp, and the frequency of resolution flips |
| CHEAPEST FALSIFICATION EXPERIMENT | that replay; falsified if net return after flips and fees is < 0.5 % per lock-up |
| CONFIDENCE | **PROBABLE** for tweets/box/music at ≥ 0.90; **negative** for AI |

<!-- SURV -->

## 5. Final self-attack (per surviving card)

| Attack | SPI-1 box office | SPI-2 tweet counts | SPI-3 music | SPI-4 AI leaderboard | SPI-5 post-determination |
|---|---|---|---|---|---|
| 1. Winner selection only? | Yes by construction; §4 sample partially corrects it: see loser share there | Yes, and the artefact is severe: the "hot" wallets (dddtrips, sb911) are net losers | Yes; only two wallets, no loser sample | Yes; two wallets, lumpy | Yes; aggregates are from selected wallets |
| 2. Needs information Quant lacks? | No: all inputs are public and timestamped | No: the counter is the resolution source | No | Partly: release timing is insider-adjacent for lab employees | No |
| 3. Latency explains the profit? | No: winners' brackets traded 0.15–0.39 for two days after the public numbers (V) | Partly: the maker variant (Annica, 35 % two-sided, split-and-sell) is order-management in seconds; the late-NO variant is slow | No | For "debut score" siblings yes; for month-end rank no | Partly: bots sweep the larger markets first |
| 4. Fees erase it? | Fee 0.05·p(1−p) ≤ 1.25 % per share; receipts are post-fee (as booked) | The large receipts are pre-fee and their authors exited around the fee rollout; the small post-fee receipts are ≈ 2–4 k$/month | Post-fee receipts, small | Post-fee, small | ≈ 0.1–0.4 % at p ≥ 0.9; not the binding constraint |
| 5. One extreme event? | No: monthly series of +0.5 to +13 k$ across four months for three wallets | Annica: Feb–Mar 2026 = 57 % of its 12-m closed realized; small wallets are steady | No | **Yes**: orac07 = two events; Hauchn = one event (excluded) | No, but one resolution flip can erase many gains |
| 6. Accounting semantics exaggerate? | Checked: unredeemed losers ≤ 1.9 k$; user-pnl ≈ closed + live | **Yes, badly**, corrected: dddtrips +217 k → −29 k; Mac-Gyver +172 k → ≈ +9 k on closed+dead; Annica ×4.6 split inflation | Checked: negligible | Checked: negligible for the two kept; thanksforplayin excluded (100 % "win rate") | Aggregates upper-biased; 0xf14e is user-pnl-verified |
| 7. Capacity exhausted? | Yes at small size only: 25–30 k$ winning-bracket volume per film-week; a few k$ per event for a new entrant | No (1–2 M$ weekly events) | Yes (hundreds of $ per market) | No | Yes (a few k$ per market) |
| 8. Public disclosure killed it? | Box-office markets are public but un-hyped; no bot ecosystem found | **Largely yes**: Polymarket's own newsletter, xtracker tools, "skills" and bots exist; the four large winners left | No | No specific disclosure | The mechanism is a well-known "late favourite" pattern; small markets keep some residual |
| Verdict | **kept, PROBABLE** | **downgraded**: receipts verified but the exploitable edge is small and mostly closed | **kept, PROBABLE, tiny** | **downgraded to UNVERIFIED** | **kept, PROBABLE, small; negative for AI** |

## 6. Final ranking (receipt quality > mechanism clarity > speed independence > public data > small capital > verification cost)

| Rank | ID | Why |
|---|---|---|
| 1 | SPI-1 BOX-OFFICE | three wallets with consistent post-fee monthly gains through September 2026 and negligible unredeemed losers; the information timeline is fully public and archived; verification is a one-day replay; capacity and boundary cases are the honest limits |
| 2 | SPI-5 POST-DETERMINATION | one small user-pnl-verified wallet plus positive ≥ 0.90 aggregates in three families; mechanism is structural and fee-cheap; risk is resolution flips; verification is one day |
| 3 | SPI-2 TWEET-COUNT | the largest receipts of the whole search (0.7–3 M$ per wallet in 12 m) but their owners are gone and the public "star" is net negative; what remains is small and bot-contested |
| 4 | SPI-3 MUSIC-COUNTS | clean, slow, public, but capacity in the hundreds of dollars per market and only two wallets |
| 5 | SPI-4 AI-LEADERBOARD | large liquid markets, lumpy receipts, information partly insider-adjacent |

Receipt evidence ≠ reproducibility evidence: none of the five cards includes a public method tied to a public wallet. The only public methods found are a Polymarket-authored backtest (tweets) and hobbyist bots without P&L (Kalshi TSA). Quant does not know how to reproduce any of these; §3's "cheapest falsification experiment" fields are the next step, not a strategy.

## 7. NEGATIFS UTILES

1. **Tweet-count "stars" are an artefact**: closed-position P&L excludes unredeemed losing buckets; dddtrips (+217 k$ "realized") is −29 k$ mark-to-market, sb911 (+106 k$ month) is −31 k$ lifetime; the four real 2025-26 winners all exited Jan–Apr 2026 (V).
2. **Mention markets ("what will X say")**: all specialist receipts date from Aug 2024–Jan 2025; 12-month user-pnl ≤ 0 for four of five; information is speech-time, not slow (V).
3. **AI/TECH leaderboard winners are mostly not slow-information**: the largest (Hauchn +205 k$) is one market-cap-ranking event; thanksforplayin trades daily stock-close markets with a 100 % closed-position "win rate" (artefact); hi-price (≥ 0.90) entries in AI markets lost 16.5 % (V).
4. **Post-determination in box office is not free**: both September-2026 winners' Sunday estimates sat on a bracket boundary; the two-day 0.15–0.39 pricing was genuine boundary risk, not lag (V + S).
5. **Kalshi measurement series** (TSA, gas, RT, Netflix): no per-account receipts exist; the one public bot write-up publishes no P&L; aggregate takers lose 31 % (agent 2).
6. **Airdrop farming**: measured per-address rewards < 350 $ and mostly < 10 k$ per group on 2021-24 data; sybil filtering tightened since; labour, not edge.
7. **Listing-announcement effect**: Coinbase-only, seconds-scale, insider-prone; **stETH discount capture**: episodic and ETH-beta; **election-night count lag**: one event per cycle with whale/arbitrage receipts only.
8. **Closed-positions and leaderboard windows must never be used as receipts without `positions` (dead losers) and `user-pnl` cross-checks** (V, 10 of 10 wallets consistent only after correction).

## 8. Terminal status

SLOW_PUBLIC_INFO_SEARCH = CANDIDATES_WITH_RECEIPTS

Five cards carry recent, third-party-verifiable receipts (SPI-1, SPI-2, SPI-3, SPI-5 realized and post-fee; SPI-4 weak). None is declared profitable for Quant; none has reproducibility evidence.

REAL_CAPITAL_AUTHORIZED = FALSE.

Next cheapest falsification mission: SPI-1 one-day replay — every Polymarket box-office bracket event of the last 26 weeks, hourly bracket VWAPs from `trades`, joined to the dated public release timeline (Thursday previews, Friday actuals, Sunday estimate, The Numbers final), returns net of 0.05·p(1−p) for buying the bracket implied by each release at the prevailing ask, plus the frequency of estimate-to-final bracket flips.

