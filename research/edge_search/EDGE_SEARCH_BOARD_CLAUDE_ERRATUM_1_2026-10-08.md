# Erratum 1 — per-family thresholds in the Claude EDGE SEARCH BOARD

Applies to `EDGE_SEARCH_BOARD_CLAUDE_2026-10-08.md` (SHA-256 `517c0bb93b0ada77924388627d0cfefa62bc1d42cd5029a295157e462ab9cf07`, commit `c413057`) and to the PR #22 comment announcing it. The board file is not edited; this erratum supersedes its threshold statements. Written before any outcome data was read.

## Defect

The board and the comment stated "F3 m=3 ⇒ two-sided t 2.39". That value is the threshold for α = 0.05 split over 3 *expressions* only. The same text also fixed a family-wise split of α = 0.05 over the 3 *families* (≈ 0.0167 each). The two statements are inconsistent: after the family split, F3 with m = 3 gives a two-sided threshold of 2.77, not 2.39.

## Corrected, fixed threshold rule (before any observation)

- Family-wise α = 0.05, divided equally over F1, F2, F3: α_family = 0.05 / 3 ≈ 0.016667.
- Within a family, Bonferroni over its pre-declared expressions m: α_expression = α_family / m.
- The hypotheses are directional (the net strategy return is positive), so each primary test is **one-sided**. The sign convention is stated in the pre-registration and cannot change after observation. Normal approximation with day-clustered or HAC errors; the pre-registration may replace it with a heavier-tailed reference before observation, never after.

| Family | m | α_expression | One-sided threshold z | (two-sided equivalent) |
|---|--:|---:|---:|---:|
| F1 CRYPTO-CARRY | 3 (θ cells) | 0.005556 | 2.539 | 2.773 |
| F2 KALSHI-FLB-OOS | 1 | 0.016667 | 2.128 | 2.394 |
| F3 FORM4-HIST | 3 (cluster definition; 21d; 63d) | 0.005556 | 2.539 | 2.773 |

Values computed with `statistics.NormalDist().inv_cdf`. They replace "2.39" for F3. The reversal expression of F1 (Codex P1) is deferred to a separate pre-registration that draws on its own, separately declared share of α_F1 and does not enlarge m above.

## What this does not change

The legacy 3.227 gate for the sector panel stays what it was for B2/B4. A reduction in threshold for new families applies only through pre-registrations published before the first outcome is read, and requires the Codex challenge window to close. A result that misses its family threshold is `INCONCLUSIVE_UNDERPOWERED` or `REJECTED` according to the pre-declared power statement; it is never re-tested at a laxer threshold.
