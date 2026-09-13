# Quant-Trade Research State

This file is the compact strategic state of the autonomous research system.

Codex should update it at meaningful milestones rather than after every minor test.

## Current search space

Five lanes were scored on mechanism, point-in-time data, beta isolation, cost,
falsifiability, implementation, economic significance and information value.
The complete ranking is in `research/opportunity_map.json`. A fifth,
time-series relative-value lane was selected only because it permits an honest
vertical-slice test with the data already present; it is not a commitment to
continue the legacy NASDAQ direction.

## Strongest current evidence

On the discovery-only 60% subsample, the strongest of three pre-declared lag
scans was weak 5-day reversal (correlation -0.0369). The causal 500-observation
OOS expression made 2.03% after 5 bps per position change, but this is not
credible edge: it lost 3.27% at 10 bps, failed in the second OOS half, and its
apparent gain was extremely concentrated. Decision: `NO_TRADE`.

## Rejected / deprioritized directions

The tested fixed short-horizon index-reversal expression is rejected. No
parameter rescue will be attempted on this sample. Historical volatility-model
research remains prior work, not evidence of tradable alpha.

## Important data / timing constraints

The repository has one daily NASDAQ index proxy (1,251 observations through
2026-07-10), no executable instrument quotes or volume, and no synchronized
cross-sectional, options, factor or filing panel. Close-t signals are therefore
tested only against close-t-to-close-t+1 returns and are research evidence, not
fillable trade claims.

## What the system learned about how to search

A cheap discovery gate successfully prevented look-ahead selection: only the
first 60% ranked the pre-declared lags, while the last 40% was untouched until
testing. Friction and subperiod checks overturned a superficially positive
5-bps result, confirming that cost sensitivity must precede paper admission.

## Current highest-value next action

Construct or obtain a compact, synchronized ETF total-return/quote panel and
scan beta-neutral cross-sectional relative value. This has higher information
value than tuning the rejected single-index reversal rule. If external network
access remains unavailable, the next build action is a point-in-time panel
ingestion contract plus synthetic causality fixtures, not another NASDAQ fit.

## Human boundary currently reached?

No.
