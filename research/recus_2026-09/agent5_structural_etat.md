# AGENT 5 — STRUCTURAL / FRAGMENTATION RECEIPTS — state

Date: 2026-09-29. External research only. REAL_CAPITAL_AUTHORIZED = FALSE.
Branch: `claude/hopeful-hamilton-81rab1` (harness-assigned; replaces the suggested
`research/agent5-structural-fragmentation-2026-09-29`).

## Status

`IN_PROGRESS` — Part A reconciliation written (RESOLVED); account #5 cash check running; Part B cards next.

## Inputs read

- `QUANT_NORTH_STAR.md` (main).
- `agent1_registres.md` (branch `claude/dazzling-dirac-foklrv`), `agent2_profits_mesures.md`
  (`claude/gallant-cerf-e0rpao`), `agent3_recette_recu.md` (`claude/exciting-edison-w68tos`).
- Primary sources, read in full:
  - Saguillo, Ghafouri, Kiffer, Suarez-Tangil, arXiv 2508.03474 v1 (5 Aug 2025) and the AFT 2025
    LIPIcs version (vol. 354, 27:1–27:24, published 2025-10-06). The key numbers are the same in both.
  - Gebele, Mutzel, Matthes, arXiv 2608.00666 v1 (1 Aug 2026). Its HTML and PDF both lose the text
    after each `%` sign (unescaped in the authors' source).

## Part A — established so far

- The two figures measure different things: Saguillo = executed fills grouped by address in
  950-block windows, basket = min leg quantity, missing low-probability NegRisk legs imputed,
  no netting; Gebele = only strategies with an identifiable realization path (Adapter call with
  inputs acquired ≤5 blocks before; complete baskets formed ≤10 min).
- Saguillo component sum = 39,692,372.19 vs stated total 39,587,585.02 (gap 104,787; probably the ε = $1 filter).
- Same-condition channel (10.58 M$) is set to zero by Gebele (unified YES/NO book; WebSocket validation).
- NegRisk channel 29.02 M$ (Saguillo) vs 0.29 M$ (Gebele, same window) → factor ≈100 left after removing same-condition.
- Saguillo top-10 addresses fully resolved via public leaderboard (file in scratchpad; to be listed in deliverable).
- Polymarket's own leaderboard P&L and user-pnl series disagree strongly for merge/conversion-heavy
  accounts (e.g. #1: −31.6 k$ vs +806 k$), so neither is used as ground truth.

## Part A — account-level evidence (V)

- #8 marksman: lifetime net cash +15,223 $ (≤62.1 k$ with open positions) vs Saguillo 468,392 $.
- 5/10 top accounts: Saguillo one-year profit > lifetime P&L on both Polymarket measures (4.98 M$ vs ~1.0 M$).
- Same-condition replication on #9/#4: legs minutes apart; netting flips #9 negative.
- 45/525 top monthly accounts converted in last 30 days; sampled 2026 conversions use accumulated inventory (no ≤60 s bundles).

## Next

1. Replicate Saguillo's same-condition rule on 2–3 addresses from raw activity (gross vs net, simultaneity).
2. Write the Part A reconciliation table.
3. Part B discovery (≤10 preliminary, ≤5 deep, ≤4 cards).
