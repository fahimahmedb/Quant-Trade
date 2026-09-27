# H-006 WIP (Hyperliquid new-listing fade) — DONE

- Dataset hl_listings_daily: 10844 rows, 222 symbols, 209 eligible listings (53 delisted),
  2023-06-08..2026-09-26; eligibility cutoff 2023-06-01; raw + manifest in data/raw/fast_rail/h006.
- listing_fade family (signals.py), lane hl_listing_fade (lanes.py), tests/test_fast_rail_h006.py.
- Evaluation run ONCE (scripts/evaluate_h006.py -> research/fast_rail/h006_result.json): 6 trials.
- Verdict REJECTED: best n30 hedged, validation t 1.82 < 2.64 (only failed test). See registry.jsonl.
- Not CANDIDATE: no --market hl-listings added.

Next step: none on history (validation spent). Only forward shadow events after 2026-09-25 could revive it.
