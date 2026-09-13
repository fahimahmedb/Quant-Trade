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

## Runtime maturity

The first persistent Research Campaign Orchestrator now wraps the PR #7 bounded
worker. Campaign state, queue tasks (including blocked and completed records),
heartbeats, lessons, cycle budget, next action and processed execution
fingerprints are atomically persisted under `runtime/` and recovered on a new
process. A rejected experiment promotes an available follow-up; absent data
blocks only its own task. With no executable work, the campaign is `IDLE`, not
stopped.

The scheduler dispatches only due work, and task identity plus data fingerprint
prevents the unchanged `TSR-NDX-001` experiment from being repeated. The
watchdog reports stale heartbeat, interrupted/stuck work, repeated crashes,
duplicate work identity and queue starvation. It diagnoses faults without
rewriting research conclusions.

## Current highest-value next action

There are two parallel priorities selected by the runtime:

1. construct or obtain a compact synchronized ETF total-return/quote panel and
   scan beta-neutral cross-sectional relative value rather than tuning the
   rejected single-index reversal rule;
2. keep the factor-residual, filing and volatility-surface lanes durably queued
   as blocked until their point-in-time datasets exist, while continuing any
   newly executable independent work.

The runtime should represent unavailable-data work as a blocked queued task and
continue any other executable research rather than silently declaring the
campaign complete.

## Human boundary currently reached?

No for runtime operation. The current research queue does contain genuine data
boundaries: no synchronized multi-asset panel, survivorship-controlled factor
panel, point-in-time filing feed, or historical option surface is present.
Those tasks remain visible and do not convert the whole campaign to `STOPPED`.
