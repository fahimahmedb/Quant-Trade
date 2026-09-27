# H-004 WIP (Kalshi weather maker-side settlement P&L)

- Sample rule declared in scripts/build_kalshi_weather_trades.py docstring BEFORE fetching trades:
  7 KXHIGH series (NY,CHI,MIA,AUS,LAX,DEN,PHIL), event dates 2025-09-01..2026-08-31 with day in {5,15,25};
  comparison KXBTCD 17:00 ET event on the 15th (descriptive only).
- Pure logic: src/quant/factory/kalshi_maker.py.

Next step: run `python3 scripts/build_kalshi_weather_trades.py --fetch` (resumable), then evaluate.
