# Architect progress — D4 convergence cycle 3 (D4-C3-P1) — 2026-10-02

WIP tracker only; not an audited object. The audited candidate is the final commit marked READY_FOR_ASTRA_RECHECK (or FUNDAMENTAL_BLOCKER).
Base: claude/charming-allen-948kd8 @ 61f4904f. Blocking audit: Astra @8874dc54 (P1, M3, m12, m13).
SYNTHETIC ONLY; OUTCOME_INFORMATION_USED = FALSE. No real Weather outcome, price, P&L, wallet performance or settlement is used.

## Declaration (written and committed BEFORE any run of the cycle-3 script; order is git-verifiable)

Script: `WEATHER_FORWARD_V2_D4_C3_P1_GATE_SIM_2026-10-02.py` (imports the cycle-2 engine unchanged; `check` mode asserts
record-for-record equivalence with the cycle-2 engine and its GO check; the only pre-declaration use of the engine is that
`check` run, 60 replications x 4 cells, no result consulted). Seeds: SeedSequence([20261102, plan_code, cell_index, stream]);
plan codes m3_class 11, m3_mix 12, m3_m35 13, m3_geo 14, m3_astra 15, m3_probe 16, p1_t2 21, p1_neg 22, p1_hi 23, p1_verify 24,
p1_go 25; stream 0 for plan runs, streams 1..5 (REPS/5 each) for `cell` confirmations. 20,000 replications per plan cell.
Known to the Architect before declaring (from Astra's report, disclosed): Astra's M3 cells (0.0587 at U(0.85,0.90)), Astra's P1
power table and its "effective multiplier about 5.0". The rules below are mechanical functions of the cycle-3 raw output.

### Order of work
1. M3 plans (m3_class 900, m3_mix 60, m3_m35 240, m3_geo 72, m3_astra 10) -> lambda selection -> 100k confirmations -> m3_probe (30).
2. P1 derive plans (p1_t2 360, p1_neg 288, p1_hi 36) at the SAME runs (each cell stores every lambda on GRID3 = 1.00..3.50 step 0.05; the adopted lambda is read out after step 1; no run depends on the selection).
3. Derive Z_EFF and SE_KAPPA_CEILING (rules below) -> constants file -> p1_verify (96) and p1_go (160 OP-only cells) -> 100k worst verification cells.
4. Documents.

### M3 — option (i): recalibrate over an enlarged, completely stated class (declared)
Class D_P** = D_P* (8.1c, unchanged) plus the CORE price laws `fav80` c ~ U(0.80, 0.90), `fav85` c ~ U(0.85, 0.90), `pm89` c = 0.89 (the
extremal concentration used for the cap: R* buys at ask a only when 1 - q - a - f(a) >= 0.10, so a < 0.90 strictly) and the two-point
mixtures `pmmix10/50/90` (10 / 50 / 90 % point mass at 0.89, remainder U(0.35, 0.80)). Cells = the D_P* factorial on each new law
(m3_class: 25 dependence x 3 laws x {no pauses, 30 random, 30 contiguous} x {thin, full} x theta {0, 0.10} at m 17), mixtures on the five
worst dependence shapes (m3_mix), the m 35 / theta 0.05 slice (m3_m35), D 60 / 90 and hemisphere / station slices (m3_geo), and
Astra's M3 cells verbatim plus neighbours (m3_astra). The GO check used for reach in these cells is the cycle-2 GO (a SUPERSET of the
cycle-3 GO), so levels measured jointly with that reach upper-bound the levels under the stricter cycle-3 GO.
Selection (mechanical):
- lambda_theta = smallest GRID3 value >= 1.70 such that in EVERY new-law cell at 20,000 reps P(reach and L_W > theta_W) <= 0.040, P(reach and false
  positive REALIZED_WINDOW claim) <= 0.040 and P(reach and U_W < theta_W) <= 0.040.
- lambda_kappa = smallest GRID3 value >= 1.60 such that in every new-law cell with theta = 0 (kappa_core = 0) P(reach and T1a) <= 0.020 and P(reach and NEG) <= 0.020.
- Old D_P* cells need no re-run: L_W, U_W, T1a, NEG are monotone in lambda, so every old cell still meets its criterion at any lambda >= (1.70, 1.60); their levels at the
  final lambda are read from the committed run-H raw lines (GRID <= 2.50).
- Confirmation: the 3 worst new-law cells per surface (L_W miss, false positive, U_W miss, T1a, NEG) plus every m3_astra cell are re-run at 100,000 fresh replications
  (streams 1..5); Wilson 95% upper bound must be <= 0.050 (L_W, size, U_W) / <= 0.025 (T1a, NEG); headline [L_W, U_W] joint non-coverage <= 0.10. A failure moves lambda up
  one grid step (never down) and repeats on the then-worst cells. No grid value <= 3.50 meeting the criterion -> FUNDAMENTAL_BLOCKER (M3 not repairable by option (i)).
- Level statement text after M3: the class is the ENUMERATED laws above; "CORE prices to 0.90" is not printed as an unqualified class. Price laws not enumerated are disclosed
  by m3_probe (in-between laws pm85, pm80, fav88, fav60 and the outside law pm899 under the three worst dependence shapes, 30 contiguous paused, thin, theta {0, 0.10}).
- Published failed candidate: the cycle-2 lambda (1.70 / 1.60) over the enlarged class.

### P1 — option (a): outcome-free, stricter-only recalibration of the design gate (declared)
Tests used: T2 with lambda_theta and NEG with lambda_kappa as adopted in M3 (8.1c construction unchanged). Dependence for the gate derivation: the PLANNING model only
(V2 copula 0.05 / 0.05 / 0.10, no persistent component, D 120, no pauses, 48 stations), because the gate is computed from 14 outcome-free OP dates and cannot know a persistence
shape; the power lost to persistence is disclosed separately (power table), not gated.
Laws: price laws {mid, favmix, fav, fav80, fav85, pm89} x (m, fill) in {17, 35, 55} x {thin, full} = 36 designs (the three cycle-2 GO-feasible price laws, the new near-cap laws, and
throughput up to 55 trades per date; m 96 is covered by p1_hi/p1_go). No GO filter in the derive cells.
Power is stated GIVEN INFO_SUFFICIENT (IF1-IF5 unchanged, reach unchanged); P(INFO_SUFFICIENT) and the joint power are reported beside it.
- T2 power curve pi_l(theta) over theta in {0.04, ..., 0.30} (P1_THETA); x-axis = the cell's mean REALISED theta_W (p = min(1, c (1+theta)) saturates for favourites).
  theta80_l = linear-interpolated first crossing of 0.80. R_l = theta80_l / mean SE0_theta (mean over OP draws of the unrounded SE0_theta of 10.2).
  Z_EFF = max(2.4865, ceil(10 * max_l R_l) / 10) over laws where 0.80 is attained. A law where 0.80 is never attained is "T2-UNCERTIFIABLE"; if any exist, GO also gets the clause
  MEAN_CORE_ASK <= c_cut with c_cut = the largest law mean (mid 0.575, favmix 0.6875, fav 0.80, fav80 0.85, fav85 0.875, pm89 0.89) among attainable laws (coarse, stricter-only).
- theta_PCE (new) = ceil(100 * Z_EFF * SE0_theta) / 100, GO clause theta_PCE <= PCE_CEILING (0.10) unchanged. Z_EFF >= Z_80, so every design's theta_PCE can only rise: stricter-only.
- NEG power curve over kappa_core in {-0.03, -0.05, -0.07, -0.09, -0.12, -0.16, -0.20, -0.25} (theta = kappa / law mean ask); x-axis = mean realised kappa_core.
  kappa90_l = |kappa| at the interpolated first crossing of NEG power 0.90; R^k_l = kappa90_l / mean SE0_kappa (10.2).
  SE_KAPPA_CEILING (new) = min(0.020, floor(1000 * 0.07 / max_l R^k_l) / 1000). This is exactly the 10.3 rationale: designs passing the ceiling have NEG power >= 0.90 at -0.07 per share.
  If kappa90 is not attained by -0.25, or if the ceiling is below the smallest SE0_kappa reachable at <= 96 trades per date (p1_go), GO is unreachable and the spec says so plainly.
- Verification (p1_verify, 96 cells at 20,000; worst cells at 100,000): effect theta := the replication's own theta_PCE under the old rule (Z_80) and under the new rule, GO = theta-side
  clause (+ station clauses) of that rule; claim to certify: P(T2 | GO and INFO_SUFFICIENT) >= 0.80 in every cell with >= 2,000 GO-and-INFO replications. Failure moves Z_EFF up 0.1 (never down) and repeats.
  The old rule is run as the published comparator (its failure is the P1 defect).
- GO / NO_GO rates (p1_go): 10 price laws (mid, favmix, fav, fav80, fav85, pm89, tail1, tail3, wide, low) x m in {8, 12, 17, 25, 35, 55, 80, 96} x {thin, full}, 20,000 OP draws each, old vs new
  gate, with the first failing reason in the 10.3 order.
- Standard: no gate is loosened; no owner-frozen surface (R*, h, W, signal, cohort, entry, T_entry, S_ref, execution, 0.04 split) is touched; GO's meaning is not redefined.
  If the only route to a passing verification is lowering a standard after seeing results: STOP, FUNDAMENTAL_BLOCKER.

### Feasibility (statement only, declared)
The missing negative-result instrument at 120 dates over D_P* is fundamental (Astra oracle benchmark). It is stated in 1 / 10.3 / 24 / 27 as a feasibility finding for the owner at loop end. W and every owner-frozen surface stay unchanged.

## Done
- Authority verified: remote claude/charming-allen-948kd8 = 61f4904f; Astra audit commit 8874dc54 present on the Astra branch.
- Read: Astra recheck (5.1, 7, 15), ledger blocker, spec sections, cycle-2 script.
- Script written; `check` PASS (engine and GO equivalence with cycle 2).

- WIP1 03640425: declaration + script committed before any run (`check` only).
- M3 plans run (m3_astra 10, m3_mix 60, m3_geo 72, m3_m35 240, m3_class 900 = 1,282 cells at 20,000) -> `WEATHER_FORWARD_V2_D4_C3_P1_RUN_J_M3_OUTPUT_2026-10-02.jsonl`.
  (Disclosure: a preview of the first 272 cells was read by the summariser while the rest ran, to test the summariser; no plan, rule or cell was changed.)
- Declared selection applied (summariser `m3`): lambda_theta = 2.15 (2.10 fails: worst L_W miss 0.0419 > 0.040; 1.75 fails T1a 0.0220 > 0.020 for kappa), lambda_kappa = 1.80; binding cells pm89 trailing-30 rv 0.10 m 35 (L_W miss 0.0394), pm89 m 17 P30-run (size 0.0253, T1a 0.0199).
  Cycle-2 lambda (1.70/1.60) over the enlarged class FAILS the declared criterion: worst L_W miss 0.0683, size 0.0469, T1a 0.0289 at 20,000 (published failed candidate).

- 100k confirmations (20 cells) done -> all inside the required bounds (worst L_W miss 0.0397 [0.0385, 0.0409]; size 0.0240 [0.0231, 0.0250]; T1a 0.0190 [0.0182, 0.0199]; U_W 0.0027; NEG 0.0062; headline 0.0397).
- m3_probe (30 cells at 20,000) done: in-between and outside laws all <= 0.0372 (pm899, m 17).
- ADDENDUM DECLARED NOW, BEFORE ITS RUN: plan m3_probe2 (plan code 17): pm899 and fav88 at m 35, trailing-30 rv 0.10, no pauses, theta 0.10, thin and full, run with `cell` at 100,000 (disclosure of the geometry that binds pm89; no selection depends on it).

- P1 derive run: p1_hi 36/36 and p1_neg 288/288 complete; p1_t2 crashed at cell 305 (pm89, m 17 thin, theta 0.14: p = min(1, 0.89 x 1.14) = 1, every trade wins, so the IF5 ratio sek5^2 / viid was 0/0 -> ZeroDivisionError). The pool is ordered, so cells 0..304 were written intact; 55 cells (305..359) are missing.
- SCRIPT CHANGE after the crash (only change; committed in the next WIP): in one_rep_p1 the INFO test `sek5*sek5/viid <= 6.0` became `(viid <= 0.0 or sek5*sek5/viid <= 6.0)`. It differs from the old expression ONLY when viid == 0 (all outcomes identical), where the old code raised; so it cannot alter any cell already written (a completed cell never hit viid == 0, otherwise it would have crashed). `check` mode (record-for-record equivalence with the cycle-2 engine, 4 cells x 60 reps, plus GO equivalence) re-run after the change: PASS. The cycle-2 engine file is untouched. Effect of the new branch: an all-win replication counts as INFO_SUFFICIENT if sek5 <= 0.025 (it is 0), i.e. power 1 at saturated effects (p = 1); these saturated points lie beyond the theta used by any GO design (theta_PCE <= 0.10) and only affect the high end of the power curve of pm89 / fav85.
- Resume (after an API session limit): no sim process running; P1 derive resumed for p1_t2 (skips completed cells).

- p1_t2 resumed and completed (55 missing cells); P1 derive complete: 684 cells.
- Declared derivation rule applied (summariser `p1derive 2.15 1.80`, output committed as `..._RUN_J_P1_DERIVE_SUMMARY_2026-10-02.txt`): max R_theta = 7.193 (mid, m 35, full) -> Z_EFF = 7.2 (Z_80 = 2.4865 was a 2.9x understatement); max R_kappa = 11.85 (fav85, m 35) -> SE_KAPPA_CEILING = floor(1000 x 0.07 / 11.85)/1000 = 0.005. No law is T2-uncertifiable (no PRICE clause needed). Constants file `WEATHER_FORWARD_V2_D4_C3_P1_CONSTANTS_2026-10-02.json`.
  The smallest SE0_kappa reachable at <= 96 trades per date (pm89, m 96) is about 0.0070 > 0.005, so the kappa clause cannot be met by any executable design on the declared laws.

## In progress
- 100k confirmations of 20 cells (3 worst per surface + all m3_astra) -> `..._RUN_J_CONFIRM_100K_2026-10-02.jsonl`; P1 derive plans (p1_hi, p1_t2, p1_neg) running in the queue.

## Next
- Run plans in the order above; selection; confirmations; probes; P1 derive; constants file; verification; GO rates; documents; final candidate commit.

## Seeds / outputs
- Outputs (committed raw JSONL, one line per completed cell, resumable by rerunning the same command):
  `WEATHER_FORWARD_V2_D4_C3_P1_RUN_J_M3_OUTPUT_2026-10-02.jsonl` (m3_*), `..._RUN_J_P1_DERIVE_OUTPUT_...jsonl` (p1_t2, p1_neg, p1_hi),
  `..._RUN_J_P1_VERIFY_OUTPUT_...jsonl` (p1_verify, p1_go), `..._RUN_J_CONFIRM_100K_...jsonl`.
- Command pattern: `OMP_NUM_THREADS=1 python3 WEATHER_FORWARD_V2_D4_C3_P1_GATE_SIM_2026-10-02.py run PLAN 20000 --out FILE`;
  `... cell PLAN IDX 100000 --out FILE`.
