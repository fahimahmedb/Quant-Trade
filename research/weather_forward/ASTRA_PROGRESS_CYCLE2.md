# ASTRA PROGRESS — CYCLE 2 RECHECK (D4-C3-M2 candidate 61f4904f)

Resume rule: a resumed/fresh Astra context continues from this file and committed outputs; never from scratch.
Simulations append one JSONL line per completed cell and skip completed cells on rerun.

- Candidate: claude/charming-allen-948kd8 @ 61f4904f94f8662084fa5245c92b647c061148ae (ancestor 4423c5c3 OK)
- Astra start: 7408c0c58fb0869c9f14ab686cbc7b0074cbf185
- Evidence dir: research/weather_forward/astra_d4_c3_m2_recheck_2026-10-01/
- Seeds: SeedSequence([77200201, plan, cell, chunk]) (cycle-2 base 77200201)

## Done
- [x] 0. Authority verified (remote heads match; ancestor OK)
- [x] 1. Read prior audit, ledger, candidate diff (spec 8.1c and propagation, sim script)
- [x] 2. Own engine astra_m2_engine.py + test_m2_engine.py (CR vs direct trade-level, exact thresholds, shapes) PASS
- [x] 3a. Repro plan (16 cells x 20k) -> out_repro_20000.jsonl
- [x] E (partial). Spec section byte diff (out_spec_section_diff.txt), R3 algebra + state machine rerun (identical to cycle 1)

- [x] 3b. repro100 (4 cells x 100k) -> out_repro100_100000.jsonl (old 0.0633 / new 0.0114 etc.)
- [x] 4a. probe (80 cells x 20k) -> out_probe_20000.jsonl. FINDING: favourite price concentration (U(0.80,0.90),
      U(0.85,0.90), point 0.90) inside 'CORE prices to 0.90' wording, worst declared dependence slice (box30 rv0.10, P30 run):
      L_W miss 0.053-0.071, T1a 0.027-0.029 (> 0.05 / 0.025). Needs probe2 sweep + 100k confirmation.
- [x] Architect selection re-derived from its raw output: lambda 1.70 / 1.60 over 1,183 cells (out_verify_arch_selection.txt)

- [x] 4b. probe2 stopped deliberately at 311/394 cells (fav80, fav85 complete; pt90 partial — pt90 is beyond R*'s
      admissible range since a = 0.90 needs q > 1). fav85 x box30 rv0.10: L_W miss 0.051-0.060 at 20k (also without pauses).
- [x] 4c. Power plan partial (m17 thin, 10 cells): reproduces Architect (P(T2) 0.111 @0.09; 0.825 @0.18; NEG 0.116 @-0.12)

- [x] probe100 (6 x 100k): fav85 box30 rv0.10 L_W miss 0.0587 [0.0573,0.0602] (P30 run, full), 0.0557 (thin),
      0.0523 [0.0509,0.0537] (no pauses); T1a 0.0262 [0.0253,0.0273]; fav80 0.0506 [0.0492,0.0520]
- [x] power plan complete (52 cells); oracle benchmark out_oracle_benchmark.txt (sd ratio worst/none 2.96 mid prices;
      non-adaptive oracle power at theta_PCE 0.008) => power shortfall intrinsic to 120 dates x D_P*

- [x] power2 (44 cells), sample (175 cells), T1b (8 cells, B 2,000), Architect rerun byte-identical
- [x] 7. Audit written (ASTRA_WEATHER_V2_D4_C3_M2_RECHECK_2026-10-01.md), state file updated (history verbatim under H5)

## In progress
- none

## Next
- final verdict commit + push (verdict: BLOCKED_D4_M2_GO_GATE_CONTRADICTED_BY_CALIBRATED_POWER_AND_LEVEL_EXCEEDED_AT_FAVOURITE_PRICE_CONCENTRATION)

## Output files
- see astra_d4_c3_m2_recheck_2026-10-01/README.md
