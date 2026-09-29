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

