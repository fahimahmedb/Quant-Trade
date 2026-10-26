# Astra D4 recheck evidence (2026-09-30) — SYNTHETIC ONLY

Independent of the Architect simulation. No market, outcome, settlement, wallet or P&L data. Requires numpy, scipy.

| Script | Output | Purpose |
|---|---|---|
| `run_attacks.py A1 8000 930201` / `A2 5000 930202` / `P3 2000 930203` | `out_attacks.jsonl` | old (TPM∨SHR) vs repaired bound on Astra C1 geometry |
| `run_core.py coverage` / `boundary` / `pce` | `out_cov.jsonl`, `out_bnd.jsonl`, `out_pce.jsonl` | core-bound coverage stress, θ_ERT boundary, θ_PCE exclusion |
| `run_super.py 4000` | `out_super.jsonl` | C2: prospective-estimand attack (rare sub-cent leg arrivals) |
| `run_search.py 1200 200`, then `run_search_top.py` | `out_search.jsonl`, `out_search_top.jsonl` | adversarial random search over the conditional admissible class |
| `check_det.py` | `out_check_det.jsonl` | deterministic domination check + D4-touched state enumeration |

`astra_d4.py` is the shared engine: design, spec-8.1 two-way CR1 max-of-three SE, latent copula, retired-bound inversion by order statistics, and spec-10.2 readiness.
