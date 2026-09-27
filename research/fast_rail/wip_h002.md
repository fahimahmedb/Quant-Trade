# H-002 status: DONE — REJECT_RESEARCH (6 trials consumed, one run)

- Dataset perp_funding_hl_dydx_daily: 10 symbols (HL/DX x BTC ETH SOL XRP DOGE), 2023-11-13..2026-09-26,
  universe by pre-declared volume rule (min-leg median notional >= $1M). Raw + manifest in data/raw/fast_rail/h002.
- Family funding_spread_hold (causal hysteresis, exit E/2); venue pair read from universe; HL-vs-BY unchanged (tests).
- Lane perp_funding_spread_hl_dydx_hold, run via research/fast_rail/run_h002.py -> h002_result.json.
- Discovery best: l7_z0.25 (SR 1.49, +0.54%); validation 2025-06-12..2026-04-21: net -0.006%,
  SR -0.03, t -0.03 vs required 3.29, 70 active days, beta 0.0003, costs 0.084% vs gross 0.078%.
- Failed: t, net>0, both halves, 2x cost, top-5 concentration, >=100 active obs.
- Capacity: median $64k per leg at 1% of min-leg 30d ADV (p10 $33k).
Next: nothing on this history (validation spent). Not CANDIDATE: no --market perp-hl-dydx added.
