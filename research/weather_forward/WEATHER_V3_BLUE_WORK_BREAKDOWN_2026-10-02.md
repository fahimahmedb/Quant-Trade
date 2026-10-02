# WEATHER V3 — ORDERED WORK BREAKDOWN FOR BLUE — 2026-10-02

Status: PLANNING HANDOFF, committed on the Astra/orchestrator branch astra/weather-forward-v2-independent-reaudit-2026-09-29 only so it is not lost; V3 branch ownership remains Blue's / the owner's call (nothing inferred).
Authority: REAL_CAPITAL_AUTHORIZED = FALSE; LIVE_TRADING_AUTHORIZED = FALSE; t0 = NOT_DECLARED; BUILDER_AUTHORIZED = FALSE.
V2 (running loop, cycle 3 of 5, branch claude/charming-allen-948kd8) is NOT modified by anything below. V3 is a NEW pre-registration with its own freeze and independent audit.
Any V3 change to a surface the owner froze in V2 (R*, h, W, signal, cohort, entry, T_entry, S_ref, execution, 0.04 CORE/TAIL split) is an OWNER DECISION (section 6); the owner opened V3 on 2026-10-02 but has not yet confirmed those changes item by item.

## 1. Why V3 (diagnosis, all from V2 audits; numbers SIMULATED unless stated)
1. 120 counted dates cannot support a usable negative-result instrument: NEG power at -0.07/share is about 0.12 after calibration (0.89 before); Astra's oracle check shows a test that knows the true variance does no better (spec 8.1c, power table 4.9, Astra @8874dc54).
2. Detectable effect at 80% power over 120 dates: about 0.08 (favourite-heavy prices) to 0.18 (mid prices).
3. Variance is dominated by sub-cent TAIL legs under constant-dollar sizing: one such leg carries the variance of hundreds of CORE legs (spec 10.3).
4. The 30-date trailing bias creates cross-block dependence (lag through seasonal transitions); the multi-block inflation (lambda_theta 1.70 -> 2.15 WIP, lambda_kappa 1.60 -> 1.80 WIP) is what removed the power. WIP values are unaudited cycle-3 Architect numbers.
5. Calendar: capture start -> analysis is about 190-200 days for one window.
6. Time (independent dates) is the scarce resource, not compute.

## 2. Consolidated idea register (O = owner idea, C = Claude idea; all must be outcome-blind in design)
| ID | Idea | Fixes | Touches frozen V2 surface? | Owner decision? |
|---|---|---|---|---|
| I1 | Numpy vectorisation of sim engines + equivalence proof (O) | wall-clock | no | no |
| I2 | Cell-slicing of plans, one session per slice, seeds independent of slice (O,C) | wall-clock | no | no |
| I3 | Token-efficiency protocol (O) | cost/limits | no | no |
| I4 | Hourly auto-resume routine (O) | idle time after limits | no | done |
| I5 | Search (never recreate) historical market-price data and other external data (O) | more data | no | no |
| I6 | Cross with meteorological data: multi-model ensemble (ECMWF+GFS+ICON), anticipation via better q (O,C) | information | signal | YES |
| I7 | Covariate adjustment (ANCOVA/CUPED, fixed external coefficients, pre-trade covariates only) incl. comparison to external references (O) | variance, maybe lambda | estimator | YES |
| I8 | Replace 30-day trailing bias by a fixed multi-year hindcast correction (EMOS-style) (C) | removes the dependence source behind lambda | signal | YES |
| I9 | Tail handling: exclude TAIL or constant-payout sizing (spec 10.3 names both) (C) | dominant variance | sizing / split | YES |
| I10 | Design-time gating to favourite-heavy designs (effect 0.08 vs 0.18) (C) | power | gate | YES |
| I11 | Longer W and/or sequential design with pre-declared alpha spending; use SHADOW_CONTINUATION (C) | dates | W | YES |
| I12 | Capture-all order books now (data accumulation mode, point-in-time) (C) | own price history | entry/t0 | YES (t0, Builder) |
| I13 | Broaden cohort: more stations, other contract types/venues (O,C) | independent obs | cohort | YES |
| I14 | Hierarchical pooling across stations (C) | efficiency | estimator | YES |
| I15 | Economic arm in shadow: Kelly-fraction / drawdown budget study, bandit-style exploration budget (O,C) | gain if edge exists | sizing (shadow only) | YES |
| I16 | Use other Quant lanes (SEC Form-4 / Gate-B) in parallel; Weather blocked != project stopped (CLAUDE.md) (C) | system progress | no | no |
| I17 | Held-out forward window never touched during design (C) | validity | no | no |
Not on the list (rejected): lowering any level after seeing results; using leverage/size to compensate for an unproven edge (North Star 7: profit is not alpha); post-outcome covariates (ERA5/observations of the target date).

## 3. Execution order (dependencies in brackets)
PHASE 0 — enabling work, no owner decision, no outcome data (start now, parallel)
- WP0.1 numpy vectorisation of the cycle-2/3 sim engine + equivalence evidence [I1]  (start when the cores of the V2 cycle-3 job are free)
- WP0.2 slicing driver: `--slice i/n`, per-slice JSONL, merge+sort+verify tool [I2]  [after WP0.1]
- WP0.3 token-efficiency protocol into every brief + V3 digest (section 7, 8) [I3]
- WP0.4 data-source inventory (running; report in scratchpad EXTERNAL_DATA_INVENTORY_2026-10-02.md) [I5]
- WP0.5 variance-reduction feasibility (running; VARRED_FEASIBILITY_2026-10-02.md) [I7]
PHASE 1 — owner decisions (section 6) [needs WP0.4, WP0.5 results]
PHASE 2 — outcome-blind design, one session per work package, in this order
- WP2.1 V3 objective + estimand statement (information-primary vs economic; what theta/kappa mean) [P1 decisions]
- WP2.2 tail handling design [I9] -> first because it removes the dominant variance
- WP2.3 bias-correction redesign from hindcasts [I8] (needs firewall: dev period / forward window; uses historical observations only for the correction, never for tuning R* thresholds) [WP0.4, I17]
- WP2.4 covariate set, fixed external coefficients, estimator [I7, I14] [WP0.5, WP2.2, WP2.3]
- WP2.5 sequential/window design and power [I11, I10] [WP2.2-2.4]
- WP2.6 cohort/venue expansion plan [I13] [WP0.4]
- WP2.7 shadow economic arm: Kelly/drawdown/exploration study, synthetic only [I15] (parallel, independent)
PHASE 3 — calibration (numpy, sliced, many sessions)
- WP3.1 declare class (persistence, price laws, pauses, shapes) BEFORE any run, commit; WP3.2 calibrate lambda/level over the class (20,000 reps/cell, worst >= 100,000); WP3.3 power/feasibility + GO/NO_GO rates per design
PHASE 4 — independent audit
- WP4.1 fresh Astra session per recheck, own engine, reproduces blocker/counterexamples old vs new, second-order search
PHASE 5 — freeze and start
- WP5.1 freeze manifest V3; WP5.2 t0 request (owner); forward window untouched until here
PARALLEL — WP6.1 I12 capture-all (if owner authorises t0/Builder); WP6.2 other Quant lanes (I16)

## 4. Work-package card template for Blue (fill one per session)
ID | goal | inputs (paths+sections, never pasted text) | outputs (paths) | role (Architect on Sonnet / Astra independent on Opus / Builder) | depends | CPU class (light/heavy; sliceable?) | token class (S/M/L) | acceptance (measurable) | owner decision needed | stop conditions (frozen surface touched; outcome info used; standard lowered after results)

## 5. Compute rules (apply from the next brief; do not disturb running V2 jobs)
1. Run CPU-heavy work as separate cloud SESSIONS (own ~4 vCPU, 15 GB each), not sub-agents of one session. One session = one work package or one plan slice.
2. Hard prerequisites for any optimised engine: seeds SeedSequence([base, plan, cell, stream]); equivalence test vs the replaced engine on a declared cell sample (record-for-record or declared tolerance with identical decisions), committed BEFORE the large run.
3. Slice by cell; every session appends one JSONL line per finished cell and skips finished cells on rerun; merge tool verifies cell count, duplicates, seeds.
4. Same standards: 20,000 reps/cell, worst cells >= 100,000, same criteria. No cell dropped.
5. Architecture: byte-identical reproduction checks run on the same CPU architecture as the original (ARM and x86 may differ in last bits). The owner's Oracle host quant-p0-targer (2 OCPU ARM, 12 GB) is the P0 qualification target: NOT used for Weather. Extra x86 compute VM = owner cost decision.
6. Parallel sessions share account rate limits: keep compute-only sessions thin (run script, push, short report).

## 6. Owner decisions needed (nothing proceeds on these without an explicit answer)
D-1 V3 objective: information-primary, economic, or both with separate estimands.
D-2 Which frozen surfaces may change in V3 (signal bias method, tail handling/sizing, W or sequential design, cohort/venues, entry).
D-3 Same economic target theta, or reweighted kappa (adjustment may change the estimand).
D-4 Shadow risk/drawdown budget for the economic-arm study (paper/shadow only; real capital stays FALSE).
D-5 Authorise t0 / Builder for capture-all data accumulation (I12), or keep it design-only.
D-6 Extra compute budget (x86 VM) or stay on cloud sessions.
D-7 Weather lane priority versus other Quant lanes.

## 7. Token-efficiency protocol (apply now, in parallel)
1. Every brief references file paths + section numbers; never paste spec text. Sessions read the digest (section 8) first and slice the 1,600-line spec with grep/sed.
2. Hand-back <= 12 lines; details only in files. Raw outputs are JSONL; sessions read summaries, not raw.
3. Progress file + WIP commits per major step (resume without re-reading).
4. Sonnet for implementation, sims, documentation; Opus only for independent Astra audits and arbitration. Lower reasoning effort for mechanical work.
5. One distinct question per session; no duplicated exploration; review scope = REQUIRED_REAUDIT_SURFACE only.
6. Orchestrator output kept short; durable facts live in the ledger.

## 8. Digest for new sessions (verified facts; spec = research/weather_forward/WEATHER_FORWARD_FALSIFICATION_SPEC_V2_2026-09-29.md)
- R* (spec 9, V1 9): Open-Meteo ensemble ecmwf_ifs025, 51 members; bias b = mean over last W=30 usable local dates; dressed CDF with sigma 1.0 C / 1.8 F; edges E = q - a - f(a), f(a)=0.05 a(1-a); single argmax leg of 22; trade iff E >= h = 0.10; hold to settlement; T_entry = game_start - 6h; S_ref = 50 USD/leg.
- Estimands: theta = E[N]/E[C]; theta_W realised-window; theta_F future under Q_H; kappa_core information arm; C_CAP_DATE = 96 x 52.5 = 5040.
- Inference: two-way cluster-robust SE (date blocks x ICAO); multi-block 5/10/20/30 with lambda (8.1c); bounds L_W, U_W; T1a/T1b/NEG; 11 scientific states; SHADOW_CONTINUATION_SIGNAL.
- Transport (R3): Proposition 1, Theorem 2, eps*(delta,tau), k*(H) — verified twice; do not reopen.
- Rules: never fabricate market data; OUTCOME_INFORMATION_USED = FALSE; declare class/procedure before running; publish failed candidates.
- Ledger and audits: branch astra/weather-forward-v2-independent-reaudit-2026-09-29 (WEATHER_V2_D4_CONVERGENCE_LEDGER_2026-10-01.md).
