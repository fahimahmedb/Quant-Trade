# Weather V3 — CURRENT — 2026-10-03

This file is the compact source of truth for new Codex tasks.

## Durable inputs
- Blue orchestration: `blue/weather-v3-orchestration-2026-10-02@31e69ee47e0fab9a79d0efdedc1eb9ef68e1f088` before this refresh.
- S1 Data Archaeology DONE: `claude/weather-v3-s1-data-archaeology-2026-10-02@697865d4f8ba5ecfcb23025272b50b5eee2b2f30`.
- S2 Capture Architecture DONE: `claude/weather-v3-s2-capture-architecture-2026-10-02@9751368c90150a71eb88147ff69446f0711c81f2`.
- S0 durable remote WIP: `claude/weather-v3-s0-compute-2026-10-02@1fa81100d3d4f32cd8f8842356c043c3d502910d`.
  - Layer A PASS, slicing determinism PASS, resume PASS, merge guards PASS.
  - A newer local Codex completion was reported but is NOT durable on GitHub; do not rely on it unless its commit is imported.
- V2 remains separate; do not modify it from V3.

## Scientific diagnosis
The scarce resource is independent information per calendar day, not CPU.
Primary problems: sparse independent dates, TAIL/price-driven variance, rolling-bias dependence, incomplete historical executable market data.

## Keep
1. NumPy-first compute + deterministic slicing.
2. Forecast-side PIT archaeology and fixed/hindcast bias redesign.
3. Tail/price-geometry redesign.
4. Only genuinely independent cohort expansion.
5. Simple pre-trade variance reduction on survivors.
6. Fresh independent Astra after one V3 candidate is frozen.

## Defer / cut
- Kelly/bandit/exploration sizing: defer until an edge candidate survives.
- Sequential/W redesign: defer until variance + signal redesign is known.
- Capture deployment: architecture is DONE; implementation waits for owner DATA_T0 authorization.
- Fancy hierarchical models: do not start before simple ANCOVA/CUPED baseline shows room for gain.
- Multi-model forecast complexity: only if verified PIT archives support the required vintages.
- Venue expansion without compatible settlement + PIT prices: reject early.
- Reopening R3 transport algebra: closed unless a new candidate changes its assumptions.

## Minimal task graph
A. COMPUTE_CLOSEOUT
   Reuse S0 remote artifacts. Run only missing Layer-B + honest benchmark + README/progress closeout. Do not redo Layer A.

B. TAIL_PRICE
   Starts after A. Compare max 3 predeclared families: V2 baseline / no-TAIL / risk-normalized or constant-payout sizing.
   Measure calibrated variance, MDE80, usable opportunities, cost-mass concentration, estimand change.

C. FORECAST_HINDCAST
   May run now from S1. Verify as-issued archive feasibility; design fixed historical bias correction; add a simple multi-model candidate only if PIT-valid.

D. COHORT_EXPANSION
   May run now from S1. Keep only expansions adding independent event/date information with compatible settlement and PIT observability.

E. VARRED
   Starts after B+C. Test simple pre-trade ANCOVA/CUPED first. Hierarchical pooling only if simple adjustment leaves material residual opportunity.

F. BLUE_SYNTHESIS
   Starts after B+C+D+E. Choose the smallest coherent V3 candidate; do not combine every survivor.

G. FRESH_ASTRA
   New task/worktree, exact frozen SHA, independent engine/attacks. PASS = scientific contract only.

## Stop rule
If B+C+D fail to produce a credible route to materially more information or lower calibrated MDE, stop Weather V3 redesign rather than create additional research tails.

## Output discipline
Each task writes one decision report + one small machine-readable summary + one progress ledger. No duplicate narrative files.
