# Architect progress — D4 convergence cycle 2 (D4-C3-M2) — 2026-10-01

WIP tracker only; not an audited object. The audited candidate is the final commit marked READY_FOR_ASTRA_RECHECK.
Base: claude/charming-allen-948kd8 @ 4423c5c3. Blocking audit: Astra @ac777a87 (M1-R, M2, m10, m11, T1b proof gap).
SYNTHETIC ONLY; OUTCOME_INFORMATION_USED = FALSE.

## Done
- Authority verified (remote head 4423c5c3; ac777a87 on the Astra branch).
- Run H declared in the header of `WEATHER_FORWARD_V2_D4_C3_M2_CAL_SIM_2026-10-01.py` before any run (class D_P*, construction family,
  lam grid, selection criterion, comparators). One 4,000-rep bug-check pilot of plan `astra` (engine check only; plan, family and criterion unchanged after it).
- Run H plans at 20,000 reps/cell: astra 12, class 900, fav35 160, geo 72, outside 20, power 36, t1b 12
  -> `WEATHER_FORWARD_V2_D4_C3_M2_RUN_H_OUTPUT_2026-10-01.jsonl` (concatenated in that order).
- Selection (declared criterion): lam_theta = 1.70, lam_kappa = 1.60.
- Confirmation at 100,000 (streams 1..5): 3 worst cells per surface + Astra cells astra#0/#1/#4
  -> `WEATHER_FORWARD_V2_D4_C3_M2_RUN_H_CONFIRM_100K_2026-10-01.jsonl`. All pass (worst L_W miss 0.0415 [0.0403, 0.0427];
  T1a 0.0193 [0.0185, 0.0202]; NEG 0.0100 [0.0095, 0.0107]; U_W 0.0085 [0.0079, 0.0091]).
- m10 wording fixes (spec 8.5c, 8.1b table, power table 4.8 reading 4, delta D4-C3 marker, architect state).

- Spec: 8.1b marked SUPERSEDED IN PART; new 8.1c (rule, class D_P*, selection, levels, 100k confirmation, T1b, failed candidates,
  power / feasibility cost).

## In progress
- Spec propagation (header, 1, 2, 6.1-6.3, 7, 8.3-8.5c, 9, 10, 11.4, 17.3, 17.8, 20, 21, 24, 26, 27); manifest; delta; power table 4.9;
  architect state; resume checkpoint 3e.

## Next
- Final commit marked READY_FOR_ASTRA_RECHECK (only if every stated level equals a measured level).

## Seeds
- Run H: SeedSequence([20261101, plan_code, cell_index, stream]); plan codes class_=1, fav35=2, geo=3, outside=4, t1b=5, power=6,
  astra=7; stream 0 for plan runs, streams 1..5 (20,000 each) for `cell` confirmations.
- Reproduce: `OMP_NUM_THREADS=1 python3 WEATHER_FORWARD_V2_D4_C3_M2_CAL_SIM_2026-10-01.py <plan> 20000`;
  `... cell <plan> <idx> 100000`.
