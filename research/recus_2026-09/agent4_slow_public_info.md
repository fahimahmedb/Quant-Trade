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

