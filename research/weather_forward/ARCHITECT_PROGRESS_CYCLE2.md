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

- Spec propagation done (header, 1, 2 rows D4-C3-M1 / D4-C3-M2, 6.1-6.3, 7, 8.1, 8.3-8.5c, 9, 10.1, 10.3, 11.4, 17.3 incl. m11
  sentence (c) and level texts, 17.8, 20, 21 items 36/41/43-48, 24, 26, 27).
- Reproducibility: `astra 20000` re-run byte-identical to RUN_H lines 1-12; `cell astra 4 100000` byte-identical to the confirm line.

- Manifest (CALIBRATED_BOUNDS, PERSISTENCE_CLASS_DP_STAR, T1a RULE, NEG RULE, U_W, ALPHA, NULLS, section G); delta D4-C3-M2;
  power table 4.9; architect state; resume checkpoint 3e.
- Adversarial re-read: owner-frozen spec sections (3, 5.1, 5.2, 14, 15, 17.2, 17.5) byte-identical to 4423c5c3; nothing outside
  research/weather_forward changed; Astra / Fable artifacts and North Star untouched.

## In progress
- none

## Next
- Final candidate commit (READY_FOR_ASTRA_RECHECK); then ASTRA BOUNDED D4-C3-M2 RECHECK ONLY.
- Flag for Astra / governance: feasibility consequence (P(T2) at theta_PCE 0.07-0.11; NEG power ~0.12 at -0.07).

## Seeds
- Run H: SeedSequence([20261101, plan_code, cell_index, stream]); plan codes class_=1, fav35=2, geo=3, outside=4, t1b=5, power=6,
  astra=7; stream 0 for plan runs, streams 1..5 (20,000 each) for `cell` confirmations.
- Reproduce: `OMP_NUM_THREADS=1 python3 WEATHER_FORWARD_V2_D4_C3_M2_CAL_SIM_2026-10-01.py <plan> 20000`;
  `... cell <plan> <idx> 100000`.
