# H-002 WIP (HL vs dYdX funding spread, hysteresis)

Done:
- scripts/build_hl_dydx_funding_dataset.py (fetch-candles/select/fetch-funding/build, stdlib)
- universe rule (volume only, pre-declared): min-leg median daily notional >= $1M -> BTC ETH SOL XRP DOGE
- signals.py: funding_venues() from universe; family funding_spread_hold (causal hysteresis, exit E/2)
- lanes.py: perp_funding_spread_hl_dydx_hold (6 specs, prior 44, cost 6bp, pristine 2026-09-25)
- tests/test_fast_rail_h002.py (12 tests pass)

- dataset built: 10416 rows, 10 symbols, 2023-11-13..2026-09-26 (raw 9.5MB gz + manifest)
Next: run workers.run_lane once on perp_funding_hl_dydx_daily (trials count), record verdict.
