# AGENT 5 — STRUCTURAL / FRAGMENTATION RECEIPTS — state

Date: 2026-09-29. External research only. REAL_CAPITAL_AUTHORIZED = FALSE.
Branch: `claude/hopeful-hamilton-81rab1`. This is the harness-assigned branch; it is used instead
of the suggested `research/agent5-structural-fragmentation-2026-09-29`.
Deliverable: `research/recus_2026-09/agent5_structural_fragmentation.md`.

## Status

`DONE`

```text
POLYMARKET_ARBITRAGE_RECONCILIATION = RESOLVED
STRUCTURAL_RECEIPT_SEARCH = VALID_SMALL_PLAYER_CANDIDATES_FOUND   (economically marginal: <= ~90 EUR/month at 5k EUR)
BEST_CANDIDATES = A5-S2 (settlement liquidity at 0.999), A5-S1 (NegRisk YES basket < 1), A5-S3 (HLP)
REAL_CAPITAL_AUTHORIZED = FALSE
```

## Inputs read

- `QUANT_NORTH_STAR.md`; current governance routing files (router only, not used as research input).
- Deliverables from earlier agents:
  - `agent1_registres.md` (`claude/dazzling-dirac-foklrv`)
  - `agent2_profits_mesures.md` (`claude/gallant-cerf-e0rpao`)
  - `agent3_recette_recu.md` (`claude/exciting-edison-w68tos`)
- Primary sources read in full:
  - Saguillo et al., arXiv 2508.03474 v1, plus the AFT 2025 LIPIcs version.
  - Gebele, Mutzel, Matthes, arXiv 2608.00666 v1.
  - Gebele & Matthes, arXiv 2605.31431 (settlement discount, App. 9.3 / Table 6).
- Abstracts read: 2605.00864 (Cheng et al., NBA), 2604.24366 (Dubach), 2603.03136 (Tsang & Yang),
  2601.01706 (Gebele & Matthes, cross-venue).

## Key verified facts (V = recomputed from public APIs on 2026-09-29)

- Saguillo components sum to 39,692,372.19 $; the stated total is 39,587,585.02 $.
- Saguillo top 10 were resolved to full proxy wallets via the public leaderboard. For 5 of 10, the one-year
  "arbitrage profit" (4.98 M$) is larger than lifetime P&L (~1.0 M$) on both Polymarket measures.
- #5 undertaker, complete lifetime (2024-02-17 → 2024-12-01, 314,848 actions, 0 open positions):
  net cash +122,362 $ (in-window +140,316 $), against 749,796 $ attributed by Saguillo.
- #8 marksman is a pure NegRisk converter. Its first 400,662 actions (20 Oct → 27 Dec 2024) net
  +15,223 $. The fetch hit its cap, and the account is still active. Polymarket MTM is +10.8 k$ at
  2025-04-01, against 468,392 $ attributed by Saguillo.
- Same-condition replication on #9 and #4: legs are a median 394–1,014 s apart, and netting flips #9 to −18.6 k$.
- 45 of 525 top monthly accounts converted in the last 30 days. The sampled 2026 conversions use
  accumulated inventory; none is a ≤60 s bundle.
- Settlement-liquidity trade is live today. Two slices of 300 closed markets each gave
  +1,680 $ and +1,564 $ (~0.14–0.15% of notional), with 3 losing fills out of ~11,000 and
  1,155 distinct buyers in the first slice.
- HLP: +60.7 M$ over 12 months, ≈0 over 6 months, API APR 3.94%, TVL 183 M$.
- Polymarket fee schedule: taker only, rate × p(1−p); geopolitics is fee-free.
  Holding rewards are 3.25%, computed on YES+NO at mid.

## Not done / limits

- The ~100× factor inside NegRisk is not split by cause (Saguillo's code is not public).
- Independent cash reconstruction: #5 over its complete lifetime; #8 over its first 400k actions
  (the rest of its window, 2024-12-27 → 2025-04-01, may be added if the uncapped fetch completes).
- 2026 realized profit for S1 was not measured. For S2, 30-day net P&L including disputes and
  newcomer fill share were not measured.

## Next mission (cheapest falsification)

Take 30 days of closed Polymarket markets, excluding crypto "Up or Down". For every buy at ≥0.998,
compute net P&L per buyer, including disputed or flipped markets. Then run a shadow simulation of
the fill share a new 0.999 bid would get. Reject S2 if net ≤ 0 or newcomer fill share < 5%.
