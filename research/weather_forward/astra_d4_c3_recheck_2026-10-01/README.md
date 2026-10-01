# Astra D4-C3 + transportability recheck evidence (2026-10-01) — SYNTHETIC ONLY

Independent of the Architect's run-F code (except the two re-run files, which reproduce run F byte-for-byte). No market, outcome, settlement, wallet or P&L data. Requires numpy and scipy.

| Script | Output | Purpose |
|---|---|---|
| `astra_transport_fuzz.py` | `out_transport_fuzz.json` | Proposition 1 / Theorem 2 fuzz (99,239 cases), worst N/C, count-vs-cost counterexample, frontier and k*(H) checks |
| `run_c3_r3.py 20000` (engine `astra_c2r2.py`, L_W added) | `out_c3_r3.jsonl` | C3 reproduction; R3 labels; conditional claim at true ε (seeds 1 100 000+) |
| `run_lw.py 50000 0` | `out_lw_L01_50k.jsonl` | L_W coverage, Architect scenario 13 geometry |
| `run_lw.py 20000 1,4,6,7,8,13` | `out_lw_20k.jsonl` | L_W coverage, stress geometries |
| `run_lw.py 20000 14,15,16,17,18,19` | `out_lw_regime_20k.jsonl` | cross-block persistence (AR regime) |
| `run_lw.py 20000 20,21,22` | `out_lw_weak_20k.jsonl` | mild persistence (φ 0.8, latent 0.05), θ = 0 size |
| `enumerate_states_r3.py` | `out_enumerate_states_r3.json` | exhaustive R3 state machine |
| Architect script, modes `c3 20000` / `frontier` at 341e0b7a | `out_architect_runF_*_rerun.*` | byte-identical to the committed run F |

Seeds: `run_lw.py` uses `1 001 000 + 1000 × geometry index`.
