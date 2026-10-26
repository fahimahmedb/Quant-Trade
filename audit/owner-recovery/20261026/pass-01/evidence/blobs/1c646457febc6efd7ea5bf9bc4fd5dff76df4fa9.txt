# H-004 WIP (Kalshi weather maker-side settlement P&L) — DONE

- Sample declared before fetch (builder docstring, commit 0950c72): 7 KXHIGH series, event days 5/15/25,
  2025-09-05..2026-08-25; 252 events, 1507 weather markets, 1.30M trades; raw + manifest data/raw/fast_rail/h004.
- Dataset kalshi_weather_trades (fingerprint a3ccad2c...), logic src/quant/factory/kalshi_maker.py,
  evaluator scripts/evaluate_h004.py run ONCE -> research/fast_rail/h004_result.json (2 trials).
- Verdict REJECTED: 1-99c +0.46c/contract t 1.34 < 2.24; 10-90c t 0.86, 2nd half negative; top-10% markets > P&L.
- Comparison KXBTCD (descriptive only): +2.77c, date-clustered t 4.0 on 12 events -> could be a NEW pre-registered hypothesis.

Next step: none on this history. A crypto-maker hypothesis would need its own declaration + fresh sample.
