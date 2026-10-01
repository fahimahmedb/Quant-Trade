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

## In progress
- [ ] chain2.sh: probe2 (394 cells x 20k, price concentration across declared shapes). Resumable.
- chain1 paused after power cell 10 (resume: ./chain1.sh — skips completed cells).

## Next
- probe100 confirmations (cells_probe100.json) of worst probe/probe2 cells at 100k
- resume chain1 (power, class_, slice); T1b (astra_t1b.py 20000 2000); Architect rerun 'astra 20000' (byte compare)
- 2. Engine (own, from spec text) + tests
- 3. A: old vs new counterexample reproduction (20k, worst 100k)
- 4. B: class verification + second-order search
- 5. D: power check
- 6. E/F/G: R3, frozen bytes, raw-output reproduction, m10/m11, D1–D12
- 7. Write audit, update state file, final commit + push

## Output files
(none yet)
