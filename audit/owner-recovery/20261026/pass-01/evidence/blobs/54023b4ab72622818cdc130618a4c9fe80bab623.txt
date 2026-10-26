# Astra D4-C3-M1 recheck evidence (2026-10-01): SYNTHETIC ONLY

This evidence is independent of the Architect's run-G code. The engine was written from the spec text at 4423c5c3. `test_engine.py` cross-checks only that the two-way CR numerics agree on one random window.

No market, outcome, settlement, wallet or P&L data is used. Requires numpy and scipy. Set `OMP_NUM_THREADS=1`.

## Seeds

`SeedSequence([77100101, plan_code, cell_index, chunk])`, with 4 chunks per cell.

| Plan | Code |
|---|---|
| repro | 1 |
| cls | 2 |
| worst | 3 |
| beyond | 4 |
| frozen | 5 |
| mech | 6 |
| fav | 7 |
| confirm | 8 |

- Algebra fuzz seed: 2026100177.
- The state enumeration is deterministic.

## Scripts and outputs

| Command | Output | Content |
|---|---|---|
| `astra_m1_run.py repro 20000` | `out_repro_20k.jsonl` | Astra M1 cells: old (341e0b7a, 5-date) vs new (4423c5c3 8.1b) rule |
| `astra_m1_run.py cls 20000` | `out_class_20k.jsonl` | All 156 cells of the declared class 𝒟_P, with old / RM / new rules and T1a / NEG / U_W. Cells 0–104 and 105–155 were run in two invocations after a session interruption; seeds are per cell, so the result is identical to one run |
| `astra_m1_run.py worst 100000` | `out_worst_100k.jsonl` | Worst class cells at 100,000 replications |
| `astra_m1_run.py beyond 20000` | `out_beyond_20k.jsonl` | Grid gaps (m 12/20/25, rv 0.03/0.07); φ 0.95; two-component; station / hemisphere; 60/25; 30 paused dates; dominant station / date; heterogeneous θ; thick; price mixes ('low', 'wide' and 'barbell' are NO_GO: reach 0) |
| `astra_m1_run.py frozen 20000` | `out_frozen_20k.jsonl` | T1a / NEG / U_W at κ_core = 0, and U_W at θ = −0.05 |
| `astra_m1_run.py mech 20000` | `out_mech_20k.jsonl` | The spec-§9 30-date trailing-mean mechanism (boxcar MA), and a two-state regime with AR(0.9) autocorrelation |
| `astra_m1_run.py fav 20000` | `out_fav_20k.jsonl` | Favourite-heavy CORE prices, c ~ U(0.70, 0.90), across the class φ / rv grid |
| `astra_m1_run.py confirm 100000` | `out_confirm_100k.jsonl` | 100,000-replication confirmation of the favourite and 30-paused-date counterexamples |
| `astra_r3_algebra.py` | `out_r3_algebra.json` | Proposition 1 / Theorem 2 fuzz, worst N/C, cost-mass counterexample, ε* frontier and guard, k*(H) |
| `astra_states.py` | `out_states.json` | 11-value SCIENTIFIC_STATE partition; shadow-signal reachability |
| `secdiff.py` (spec_old.md / spec_new.md from `git show 341e0b7a:` / `4423c5c3:`) | `out_spec_section_diff.txt` | Section-level byte comparison |
| Architect script, modes `repro 20000` and `c3 20000` at 4423c5c3 | `arch_repro_rerun.jsonl`, `arch_c3_rerun.jsonl` | Byte-identical to the committed run-G output (repro block, class lines and c3 block) |

`*_summary.txt` files are tables printed by `summarize.py`.

## Output fields

- `miss_*`: joint P(reach ∧ L > θ_W).
- `fpos_*`: P(reach ∧ L > 0 ∧ θ̂ ≥ θ_ERT ∧ θ_W ≤ 0).
- `T1a` / `NEG` / `UW_miss`: joint with reach.
- `*_given_reach`: conditional on reach.
