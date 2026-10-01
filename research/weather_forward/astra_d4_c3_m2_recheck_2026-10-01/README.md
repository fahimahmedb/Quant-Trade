# Astra cycle-2 (D4-C3-M2) recheck evidence — 2026-10-01

SYNTHETIC ONLY. No market, forecast, order-book, settlement, wallet or P&L data was read. OUTCOME_INFORMATION_USED = FALSE.
Audited candidate: claude/charming-allen-948kd8 @ 61f4904f94f8662084fa5245c92b647c061148ae.

| File | What |
|---|---|
| astra_m2_engine.py | Astra's independent engine (spec 8.1, 8.1c, 8.5, 9, 10.2/10.3, 11.4); OLD (4423c5c3) and NEW (61f4904f) rules on the same replications; lambda grid 1.00..2.50 |
| test_m2_engine.py | self-checks: CR vs direct trade-level two-way CR at b = 5/10/20/30; exact thresholds (Gaussian, two-state); shape variance/acf |
| astra_m2_run.py | resumable runner (one JSONL line per completed cell; skips completed keys); plans repro, repro100, probe, probe2, power, power2, sample, probe100 |
| astra_t1b.py | independent PINM T1b / T1 check (B = 2,000) under persistence |
| summarize_m2.py, power_m2.py | summaries (Wilson 95%), power tables, sd moments |
| verify_arch_selection.py | re-derives lambda_theta / lambda_kappa from the Architect's committed run-H raw output |
| secdiff2.py | spec section byte comparison 4423c5c3 -> 61f4904f (inputs: `git show <sha>:research/weather_forward/WEATHER_FORWARD_FALSIFICATION_SPEC_V2_2026-09-29.md > spec_old.md / spec_new.md`) |
| astra_r3_algebra.py, astra_states.py | Astra's R3 algebra fuzz and SCIENTIFIC_STATE enumeration (rerun; identical to cycle 1) |
| out_repro_20000.jsonl, out_repro100_100000.jsonl | M1-R / M2 counterexamples, OLD vs NEW |
| out_sample_20000.jsonl (+ cells_sample.json), out_sample_summary.txt | 175 in-class cells: Architect's 8 worst per surface + 110 random class + 40 random slice cells |
| out_probe_20000.jsonl, out_probe2_20000.jsonl (stopped at 311/394 deliberately), out_probe2_summary.txt, out_probe100_100000.jsonl | second-order search; price-concentration finding confirmed at 100,000 |
| out_power_20000.jsonl, out_power2_20000.jsonl, out_oracle_benchmark.txt | power / feasibility |
| out_t1b_20000_2000.jsonl | T1b / T1 |
| arch_rerun_astra_20000.jsonl, arch_rerun_cell_class_887_100000.jsonl, arch_rerun.sh | Architect script rerun: byte-identical to committed RUN_H lines 1-12 and confirm line 1 |
| out_r3_algebra.json, out_states.json, out_spec_section_diff.txt, out_verify_arch_selection.txt | R3 / frozen-surface / selection checks |
| chain*.sh | the run order used |

Seeds: SeedSequence([77200201, plan_code, cell_index, chunk]) (T1b: [77200201, 20, cell, chunk]).
Reproduce: `OMP_NUM_THREADS=1 python3 astra_m2_run.py <plan> <reps>` (probe100 / sample read cells_<plan>.json).
