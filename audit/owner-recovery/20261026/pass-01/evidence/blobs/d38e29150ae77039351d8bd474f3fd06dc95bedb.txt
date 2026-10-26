# Astra D4-C2 recheck evidence (2026-09-30) — SYNTHETIC ONLY

Independent of the Architect's run-E code. No market, outcome, settlement, wallet or P&L data. Requires numpy, scipy.

| Script | Output | Purpose |
|---|---|---|
| `run_c2_r2.py 4000` | `out_c2_r2.jsonl` | C2 reproduction (retired R1 rule) vs the frozen R2 labels, incl. observed-count stratification (seeds 991 000+) |
| `run_confirm_attack.py scan 2000` | `out_confirm_scan.jsonl` | false PROSPECTIVE_VALUE_CONFIRMED scan at θ_P = 0 over rare loss-regime geometries (seeds 990 000+) |
| `run_confirm_refine.py 20000` | `out_confirm_refine.jsonl` | worst cells at θ_P = −0.005, 20,000 replications in 5 seed chunks (seeds 996 000+) |
| `enumerate_states.py` | `out_enumerate_states.json` | exhaustive D4-touched state-machine enumeration (spec 17 @e45d2ce7) |

`astra_c2r2.py` is the shared engine: prospective process, spec-8.1 CR, spec-10.2 readiness, IF2–IF5, gates G1/G2, and R2 / retired-R1 labels.
