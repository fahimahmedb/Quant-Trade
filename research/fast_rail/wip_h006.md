# H-006 WIP (Hyperliquid new-listing fade)

Done:
- scripts/build_hl_listings_dataset.py (fetch -> data/raw/fast_rail/h006, build -> hl_listings_daily)
- listing_fade family (signals.py, StrategySpec.hedge_symbol omitted from to_dict when empty)
- lane hl_listing_fade (lanes.py), tests/test_fast_rail_h006.py (synthetic tests pass)
- scripts/evaluate_h006.py (run_lane + event view -> research/fast_rail/h006_result.json)

Dataset built: 10844 rows, 222 symbols, 209 eligible listings (53 delisted), 2023-06-08..2026-09-26.

Next exact step: `PYTHONPATH=src python3 scripts/evaluate_h006.py` ONCE (fetch done).
Trials consumed so far: 0.
