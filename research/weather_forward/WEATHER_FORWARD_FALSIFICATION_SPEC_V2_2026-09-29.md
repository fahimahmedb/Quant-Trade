# WEATHER FORWARD FALSIFICATION SPEC — V2 — 2026-09-29

```text
DOCUMENT_ROLE            = PRE-REGISTERED FORWARD FALSIFICATION PROTOCOL, VERSION 2 (supersedes V1 as the candidate
                           pre-registration; V1 stays an immutable historical object)
AUTHOR_ROLE              = Weather Forward V2 Architect / convergence authority (sole V2 freeze authority)
BRANCH                   = claude/charming-allen-948kd8
V1 (HISTORICAL, FROZEN)  = claude/intelligent-gates-msidml @ 726070a199957a6fc05515ebb3027e945028fddc
ASTRA (DEFECT AUTHORITY) = claude/dreamy-franklin-1vki4t @ e1cf4ca0851eace2912ce8a9bcd4a8400ebf4250
FABLE (ADVISORY)         = claude/zen-einstein-9moyry @ 5760ffa5b5da2a988cfe6d1503c86c561acf9b1f
COMPANION_FILES          = WEATHER_FORWARD_FREEZE_MANIFEST_V2_2026-09-29.md
                           WEATHER_FORWARD_ARCHITECT_STATE_V2_2026-09-29.md
                           WEATHER_FORWARD_V1_TO_V2_DELTA_2026-09-29.md
                           WEATHER_FORWARD_V2_POWER_TABLE_2026-09-29.md
                           WEATHER_FORWARD_V2_SYNTHETIC_SIM_2026-09-29.py   (synthetic Monte Carlo, no market data)
                           WEATHER_FORWARD_V2_D4_C2_SIM_2026-09-30.py      (D4 repair R2 validation, synthetic only)
                           WEATHER_FORWARD_V2_D4_C3_SIM_2026-09-30.py      (D4 repair R3 validation, synthetic only)
                           WEATHER_FORWARD_V2_D4_C3_LW_CAL_SIM_2026-10-01.py (D4-C3-M1 source-bound calibration, run G, synthetic only)
                           WEATHER_FORWARD_V2_D4_C3_M2_CAL_SIM_2026-10-01.py (D4-C3-M2 calibration of L_W, U_W, T1a, NEG over 𝒟_P*, run H, synthetic only)
                           WEATHER_FORWARD_V2_D4_C3_P1_GATE_SIM_2026-10-02.py (D4-C3-P1 enlarged price class, lambda recalibration and design-gate calibration, run J, synthetic only)
                           WEATHER_FORWARD_V2_D4_C3_P1_SUMMARIZE_2026-10-02.py (mechanical selection / derivation / tables from the committed raw output)
                           WEATHER_FORWARD_V2_D4_C3_P1_CONSTANTS_2026-10-02.json (Z_EFF, SE_KAPPA_CEILING, lambda constants as derived)
                           WEATHER_FORWARD_V2_D4_C3_P1_RUN_J_*_2026-10-02.{jsonl,txt} (raw output and summaries; ARCHITECT_PROGRESS_CYCLE3.md holds the pre-run declaration)
WEATHER_FORWARD_SPEC_V2  = AUDITED @94b59348 → ASTRA_WEATHER_V2_REAUDIT = BLOCKED_D4_STRUCTURED_BOUND_FALSE_ECONOMIC_EXCLUSION (@7d95c00)
WEATHER_FORWARD_SPEC_V2_D4_REPAIR = AUDITED @24d2342 → ASTRA_WEATHER_V2_D4_RECHECK = BLOCKED_D4_PROSPECTIVE_ESTIMAND_UNSAMPLED_TAIL_FALSE_EXCLUSION (@3d18085)
WEATHER_FORWARD_SPEC_V2_D4_C2_REPAIR = AUDITED @e45d2ce7 → ASTRA_WEATHER_V2_D4_C2_RECHECK = BLOCKED_D4_PROSPECTIVE_CONFIRMATION_UNSAMPLED_LOSS_REGIME_FALSE_CONFIRMATION (@92c2f706)
WEATHER_FORWARD_SPEC_V2_D4_C3_TRANSPORT_REPAIR = AUDITED @341e0b7a → ASTRA_WEATHER_V2_D4_C3_TRANSPORT_RECHECK = BLOCKED_D4_R3_SOURCE_BOUND_UNDERCOVERAGE_CROSS_BLOCK_PERSISTENCE (@5bb57eb2)
WEATHER_FORWARD_SPEC_V2_D4_C3_M1_REPAIR = AUDITED @4423c5c3 → ASTRA_WEATHER_V2_D4_C3_M1_RECHECK = BLOCKED_D4_M1_SOURCE_BOUND_LEVEL_NOT_ATTAINED_OVER_DECLARED_CLASS_AND_FROZEN_SURFACE_UNDERCOVERAGE (@ac777a87)
WEATHER_FORWARD_SPEC_V2_D4_C3_M2_REPAIR = AUDITED @61f4904f → ASTRA_WEATHER_V2_D4_C3_M2_RECHECK = BLOCKED_D4_M2_GO_GATE_CONTRADICTED_BY_CALIBRATED_POWER_AND_LEVEL_EXCEEDED_AT_FAVOURITE_PRICE_CONCENTRATION (@8874dc54)
WEATHER_FORWARD_SPEC_V2_D4_C3_P1_REPAIR = READY_FOR_ASTRA_RECHECK   (D4-C3-P1, convergence cycle 3: new 8.1d and 10.4; sections 1, 2, 6.1–6.3, 7, 8.1, 8.1c marker, 8.4, 8.5, 8.5c, 9, 10.1–10.3, 17.3, 17.8, 21, 24, 26, 27)
ASTRA_REAUDIT            = astra/weather-forward-v2-independent-reaudit-2026-09-29 @ 7d95c00abccfbc805c0d8abca65a6b93268741a2
ASTRA_D4_RECHECK         = astra/weather-forward-v2-independent-reaudit-2026-09-29 @ 3d18085862f239a81936345989b4e26414cedcf3
ASTRA_D4_C2_RECHECK      = astra/weather-forward-v2-independent-reaudit-2026-09-29 @ 92c2f706d2ac75af9ae9710061c60df520234410
ASTRA_D4_C3_RECHECK      = astra/weather-forward-v2-independent-reaudit-2026-09-29 @ 5bb57eb2adf4cff35378f2c0e53e0316d45a4229
ASTRA_D4_C3_M1_RECHECK   = astra/weather-forward-v2-independent-reaudit-2026-09-29 @ ac777a870e7f6b09636f06fe7720194d257427eb
ASTRA_D4_C3_M2_RECHECK   = astra/weather-forward-v2-independent-reaudit-2026-09-29 @ 8874dc5422eecf432869894cb2098e1fc13fe50f
WEATHER_FORWARD_SPEC_V1  = HISTORICAL_FROZEN_OBJECT
EXPERIMENT_FEASIBILITY   = BLOCKED_POWER_BELOW_DECLARED_MEUE   (Astra's verdict on V1; only Astra may change it)
EXPERIMENT_FEASIBILITY_V2 = BLOCKED_POWER_NEGATIVE_RESULT_INSTRUMENT_INFEASIBLE_AND_T2_POWER_BELOW_FROZEN_GO_RATIONALE   (Astra's verdict on 61f4904f; only Astra may change it)
GO_STATUS_ON_DECLARED_LAWS = NO_GO_KAPPA_UNDERPOWERED_FOR_EVERY_DECLARED_DESIGN   (D4-C3-P1, 10.3–10.4: a measured design-gate finding, not a strategy result; governance / owner decision)
HURDLE_SAMPLE_INCOMPATIBILITY = FALSE
FABLE_DESIGN_CHALLENGE   = DONE_ADVISORY
BUILDER_AUTHORIZED       = FALSE
REAL_CAPITAL_AUTHORIZED  = FALSE
LIVE_TRADING_AUTHORIZED  = FALSE
t0                       = NOT_DECLARED
ACCESS_USER_REPORTED     = TRUE
LEGAL_ACCESS_CONFIRMED   = UNKNOWN
TRADING_RULE_CHANGED     = FALSE
EXECUTION_MODEL_CHANGED  = TRUE   (CONSERVATIVE robustness model only: one venue tick instead of a flat +0.01; section 15)
COHORT_CHANGED           = TRUE   (°F 2-degree ladders admitted by exact interval arithmetic; section 14)
OUTCOME_INFORMATION_USED = FALSE
```

Epistemic labels: **KNOWN** (primary source), **MEASURED** (pre-outcome public metadata read by this Architect on 2026-09-29: `gamma-api /events?tag_slug=weather&closed=false` titles, bucket labels, descriptions, `orderPriceMinTickSize`, `orderMinSize`, `feeSchedule`; **no price, book, settlement, resolution, trade, wallet or P&L field was read**), **DERIVED** (arithmetic), **SIMULATED** (synthetic Monte Carlo, declared inputs, no market data), **ASSUMED** (declared design choice), **UNKNOWN**.

Incorporation by reference. Every V1 section not amended here stays in force **verbatim at commit 726070a**: V1 §2–3 (evidence audit), §4.2–4.3 (timeline and per-trade quantities), §7 (information set), §8 (forecast sources), §9 (signal R*), §10 (baselines, now descriptive per section 18), §11 (economic accounting), §12 (execution, amended only for CONSERVATIVE slippage), §19 (tier economics, amended for allocation), §20 (oracle controls), §21 (access), §22 (schema, extended in section 25), §23 (survivorship), §24 (anti-leakage invariants, amended in section 25). Where this document and V1 disagree, **this document wins**; where this document is silent, **V1 applies**. The freeze manifest V2 enumerates every frozen value explicitly so the Builder never has to resolve a conflict.

---

## 1. The question, and what V2 can and cannot answer

**Primary economic question (unchanged from V1).** Can the frozen public-weather rule R* generate positive **net cashable** value per dollar of capital actually committed, prospectively, under realistic small-capital retail execution?

**What the venue permits (DERIVED, section 7 and the power table).** Information in this experiment is bounded by **target dates**, not by trade count: within-date dependence caps each date at roughly `1/ρ_d` effective trades, so 120 dates hold ≈ 900–2,400 effective trades whatever the trigger rate (power table §2.1, §2.4). At that information:

| Quantity | Value | Status |
|---|---|---|
| Economic relevance threshold `θ_ERT` | **0.02** net per dollar committed per trade (V1's MEUE, renamed, meaning unchanged) | FROZEN |
| Effect 120 dates can confirm with 80% power (`θ_PCE`) | ≈ 0.06–0.08 if the executable mix has no material sub-4¢ share; ≈ 0.12–0.36 if lottery legs persist (power table §2, §4.2) — above the 0.10 ceiling, V2 does not start (section 10.3). **Nominal (normal approximation).** Under the persistence-calibrated T2 the simulated 80%-power effect is about **7.2 × SE0_θ** (D4-C3-P1, 10.4), i.e. ≈ 0.15–0.21 for mid-price designs and ≈ 0.05–0.10 for favourite-concentrated ones (power table §4.10); it was ≈ 0.18 for D4-C3-M2 (8.1c), ≈ 0.11–0.12 for the cycle-1 rule and ≈ 0.09–0.10 for the R3 engine (no persistence). The design gate now uses that multiplier, so θ_PCE is again an effect the T2 actually run confirms with ≥ 80% power (simulated 0.976–1.000, 10.4) | FORMULA FROZEN with Z_EFF = 7.2 (10.2); value populated pre-t0 from outcome-free prices (section 10) |
| Can a 120-date design confirm **or** exclude θ = 0.02? | **No.** Both need `SE(θ̂) ≤ 0.008` (≈ 15,500 independent trades at σ = 1; ≈ 1,300 dates at 35 trades/day) | DERIVED, reproduced from Astra and Fable |
| Can it detect an **executable mispricing** in the rule's chosen legs, including a real negative result? | Nominally yes for the core stratum: SE(κ_core) ≈ 0.013–0.017, MDE80 ≈ 0.032–0.043 per share (5-date-block normal reference), independent of the lottery share; tail stratum by an exact win-count test. **D4-C3-P1: with T1a / NEG calibrated over the persistence class 𝒟_P* (8.1c, 8.1d), NEG power against −0.07 per share is 0.06–0.25 at m = 17 and at most 0.44 over every declared price law and throughput up to 96 trades per date (joint with INFO_SUFFICIENT; 10.4), against the ≈ 0.9 the design gate once assumed. A real negative result is not attainable at 120 dates: the information axis is not well powered, and no design passes the recalibrated GO (10.3)** | DERIVED + SIMULATED |

**What V2 can answer about the primary question after D4 repair R3 (section 8.5c).** No finite window can settle the prospective question unconditionally, in either direction (8.5b, 8.5c). V2 answers it in two explicit layers:
1. a sampling-inference verdict on the realised-window value θ_W of the trades R* actually executed;
2. a transport frontier: how much of a future epoch's expected executed cost could come from an arbitrarily adverse regime (worst case −1 per dollar) before positivity is lost.

No label asserts unconditional prospective value or its absence.

Therefore V2 does **not** pretend 0.02 is adjudicable. It keeps θ as the only economic estimand, separates `θ_ERT` (what matters economically) from `θ_PCE` (what the design can confirm), adds a stratified information axis (not a gate) whose positive side (T1a / T1b) can say "the rule's chosen legs are not underpriced" only for large core mispricing and whose negative side (NEG) is **not usable at this horizon** (10.3, 10.4, 27; it is not "well powered"), and labels the band `[θ_ERT, θ_PCE)` explicitly **unresolved** — never "zero edge".

**Feasibility finding (D4-C3-P1; stated plainly).** With the design gate recalibrated to the tests actually run (10.2–10.4), **no design on the declared price laws passes GO at any throughput up to 96 trades per date**. Mid-price, mixed and lottery-leg designs fail the θ_PCE clause (new θ_PCE ≥ 0.12 at the highest throughput); favourite-concentrated designs can pass it; and **every** design fails the NEG clause (it needs SE0_κ ≤ 0.005; the smallest reachable is ≈ 0.0070). The missing negative-result instrument at 120 counted dates over 𝒟_P* is fundamental for feasibility: Astra's oracle benchmark shows that a non-adaptive test which knows the worst-case dependence exactly has power 0.008 (mid) / 0.19 (favourite) at the cycle-2 θ_PCE, and the calibrated construction does about as well, so the loss is mostly intrinsic to the declared class at this horizon. It cannot be repaired inside V2 by recalibration, and it is not repaired by changing W or any owner-frozen surface. It is reported to the owner at loop end as a governance / resource decision (a longer horizon, an outcome-blind narrower class justified by non-outcome evidence, a different design, or retirement of the Weather candidate).

---

## 2. Decision record (one row per major decision)

`OUTCOME_INFORMATION_USED = FALSE` and `TRADING_RULE_CHANGED = FALSE` for every row; the only changed execution assumption is D-EXEC.

| ID | ASTRA_FINDING | FABLE_RECOMMENDATION | ARCHITECT_DECISION | RATIONALE | OUTCOME INFO USED | TRADING RULE CHANGED |
|---|---|---|---|---|---|---|
| D1-ARCH | D1 CRITICAL: θ_MEUE = 0.02 undetectable in ≤ 120 dates; realistic MDE 0.06–0.10 (0.15–0.25 with lottery legs) | Family D (stratified two-estimand) with Family B honest labels | **Adopt a configured Family D + B hybrid** (fixed 120 counted dates; θ the only economic estimand; stratified κ_core / tail win-count information axis; θ_ERT ≠ θ_PCE); reject A (multi-year, mechanics drift) and C (no interim, section 11) | the only architecture with a real negative result at 120 dates, tail-immune on the information axis, honest about the unresolved band; A answers a 2030 question about a venue that changed templates twice in six months | NO | NO |
| D1-GATE | — | fixed-sequence gatekeeping: θ tested only after the information gate T1 passes | **Reject the gatekeeper. Information and economics are two parallel axes; θ is tested unconditionally; every joint claim is an intersection of tests each at α (intersection-union), so error control is unchanged** | SIMULATED: with an edge concentrated in the cheapest legs (true θ = 0.44) the θ engine detects it 0.535–0.61 of the time but a count-based gate would let only 0.21–0.30 through (runs A/B) — a gate would block a real, large edge roughly half to two-thirds of the time; a confirmed θ is itself payout-weighted evidence that the chosen legs are underpriced | NO | NO |
| D1-THR | MEUE unreachable | θ_ERT reporting threshold; θ_PCE from pre-t0 prices | **θ_ERT = 0.02 frozen; θ_PCE by frozen price-implied formula (multiplier Z_EFF = 7.2 since D4-C3-P1); PCE_CEILING = 0.10 → NO_GO** | a design that can confirm only edges > 5 × ERT is not worth starting (section 10) | NO (prices, depth, counts only) | NO |
| D4-EST | D4 MAJOR: heavy-tailed θ, percentile bootstrap unreliable | κ_core + W_tail vs Λ_tail as confirmatory information estimands, θ untouched | **Adopt, with κ defined net of all-in executable cost; strata by price (a < 0.04), not by the tick field** | κ is bounded and tail-immune; the tick field is a market-level property shared by YES and NO tokens (MEASURED: 1,550 of 2,981 temperature markets at 0.001) | NO | NO |
| D4-ENG | D4: interval method must fit heavy tails and few clusters | PINM primary + two-way studentised bootstrap; reject only if both reject | **Modify: empirical two-way cluster-robust engine is primary for κ_core, θ_core and pooled θ; PINM is primary only for the rare-event tail count (T1b); PINM on θ is reported, not gating** (V2@94b5934 also used PINM for the tail part of the θ upper bound; retired by D4 repair R1) | SIMULATED: PINM with a declared (not oracle) dependence halves power on core statistics (core-only θ = 0.10: CR 0.855–0.91 vs PINM 0.73–0.755, runs A/B) while the empirical engine is already conservative for positive θ claims with tails (null rejection 0.000–0.020 at nominal 0.05); dependence barely matters for rare tail counts, so PINM is exact-in-practice there | NO | NO |
| D4-UB (REPAIRED, R1) | V2 re-audit C1 (CRITICAL): the TPM ∨ SHR structured bound false-excludes θ = 0.0315 > θ_ERT at 7.46% (coverage 0.885) and θ = 0.085 > θ_PCE at 11.2% in a GO-compatible design; MP1 committed sim ≠ frozen bisection contract | (Fable: PINM tail engine; no full-class bound proposed) | **Exclusion bound = core two-way CR bound + assumption-free tail supremum `M_tail` (every TAIL leg wins); TPM / SHR retired from every role; pooled naive bounds never used** | the tail's admissible class is all `p ∈ [0,1]` under any dependence; the only bound valid over it is the identified-set supremum; coverage then equals core coverage (run D: 0.9705–0.993 over nine adversarial core geometries; both Astra attacks: coverage 1.0, false exclusion 0) | NO | NO |
| D4-REJ (REPAIRED, R1) | consequence of C1: V2 rule 17.6 also rejected R* as a net strategy on NEGATIVE_INFORMATION alone | — | **Economic rejection only through `U(θ) < θ_ERT`; NEGATIVE_INFORMATION becomes the information-level `R*_CORE_INFORMATION_REJECTED`** (superseded by D4-C2: no economic rejection of R* is issued in V2) | run D: in Astra's positive-tail / negative-core geometry the NEG clause produced a false economic rejection in 32.0% of runs | NO | NO |
| D4-C2 (REPAIRED, R2) | V2 D4 recheck C2 (CRITICAL, Astra @3d18085): R1's bound covers only the realised-window value θ_W; when rare 0.001 legs are absent from a GO-compatible window, prospective θ_P = 0.025 > θ_ERT is falsely excluded 5.92% of runs (0.19–0.35 at p_tail 0.5–1.0) and θ_P = 0.10 is falsely LARGE-excluded 15.3% | — | **Prospective exclusion is NOT IDENTIFIED in V2: no prospective exclusion label exists; ECONOMIC_RESULT = PROSPECTIVE_VALUE_{CONFIRMED, NOT_ROBUST, INDETERMINATE}; R1's bound is kept, re-scoped to θ_W and reported only as REALIZED_WINDOW_BOUND; R*_REJECTED_AS_NET_STRATEGY is never issued** | identification theorem (8.5b): under V2's own admissible class (p ∈ [0,1], 0.001 tick, date common modes) every level-0.05 test of θ_P ≥ θ_ERT or θ_P ≥ θ_PCE has power ≤ 0.058 against every admissible truth over the 134 observed dates; the arrival-bound alternative (R2-A) needs trade-level independence V2 does not grant and, even granted, never excludes (allowance ≈ 1.2 at zero observed sub-cent legs) | NO | NO |
| D4-C3 (REPAIRED, R3) | V2 D4-C2 recheck C3 (CRITICAL, Astra @92c2f706): `PROSPECTIVE_VALUE_CONFIRMED` and the forward signal fired at θ_P = −0.005 in 43% (thin fills) and 12% (full fills) of runs, because rare loss dates carrying the 96-event cost cap are absent from most windows; R2's "bounded downside" asymmetry argument was false in general | — (Astra options a / b / c) | **Hybrid: no unconditional prospective label in either direction; ECONOMIC_RESULT is about θ_W (T2 unchanged); prospective content = cost-mass transport class 𝒯_H(ε, δ) with the deductive robust bound `L_T = (1 − ε)(L_W − δ) − ε` and the frontier ε*(δ, τ); forward signal renamed SHADOW_CONTINUATION_SIGNAL; no ε, δ, H or τ threshold chosen in V2** | mirror theorem (8.5c): any valid unconditional confirmation test has power ≤ 0.06–0.12 in thin geometries; Proposition 1 makes cost-mass contamination exact for θ = E[N]/E[C]; run F: 0 false realised-window claims; conditional claim false only through the sampling miss of L_W (≤ 0.027) | NO | NO |
| D4-C3-M1 (cycle 1; SUPERSEDED IN PART by D4-C3-M2) | Astra D4-C3 recheck M1 (MAJOR, @5bb57eb2): R3's 5-date-block L_W undercovers under cross-block date persistence that §9 names (false window positive 0.0805, miss 0.0902) | — | **Calibrate (option a): `L_W = θ̂ − max_{b∈{5,10,20,30}} t_{df_b,0.95} SE_2w(b)`, stated ≤ 0.05 over the run-G grid 𝒟_P; T1a / NEG / U_W left on 5-date blocks (orchestrator's cycle-1 bound) and qualified at statement level** (8.1b) | run G: worst 0.0465 on the grid; refuted over the class as written by Astra M1-R @ac777a87 (favourite prices 0.0605–0.0852, 30 paused dates 0.0531, §9 trailing mean 0.0597) and M2 (T1a 0.0888, NEG 0.0707, U_W 0.0755) | NO | NO |
| D4-C3-M2 (cycle 2; λ, class and gate meaning SUPERSEDED IN PART by D4-C3-P1) | Astra D4-C3-M1 recheck M1-R + M2 (MAJOR, @ac777a87), minors m10 / m11, proof gap T1b | — (Astra options (a) / (b) per item) | **Option (a) for both: one construction `stat ∓ λ · max_{b∈{5,10,20,30}} t_{df_b,q} SE_2w(b)` for L_W (q 0.95, λ_θ = 1.70), U_W's core (q 0.975, λ_θ), T1a / NEG (q 0.975, λ_κ = 1.60), calibrated over the completely stated class 𝒟_P*; headline interval = [L_W, U_W]; IF4 / IF5 / GO unchanged; every level stated jointly with reach over 𝒟_P*** (8.1c) | run H (1,183 reached cells × 20,000; 14 cells × 100,000): L_W ≤ 0.0415 [0.0403, 0.0427], size ≤ 0.0353, U_W ≤ 0.0089, T1a ≤ 0.0198, NEG ≤ 0.0106, T1b ≤ 0.0077; family, class and criterion declared before any run; failed members and comparators published. Cost: P(T2) at θ_PCE 0.07–0.11, NEG power ≈ 0.12 at −0.07 (disclosed; feasibility for Astra / governance) | NO | NO |
| D4-C3-P1 (cycle 3) | Astra D4-C3-M2 recheck @8874dc54: P1 (MAJOR: GO / θ_PCE (Z_80) / SE_KAPPA_CEILING keep a §10.3 rationale the calibrated tests contradict), M3 (MAJOR: level exceeded at near-cap favourite prices inside the printed "CORE prices to 0.90"), m12, m13 | — (Astra options (a) / (b) for P1; (i) / (ii) / (iii) for M3) | **P1 option (a) only: outcome-free, stricter-only recalibration of the design gate to the tests actually run — Z_80 → Z_EFF = 7.2 in θ_PCE and SE_KAPPA_CEILING 0.020 → 0.005, both derived by a synthetic rule declared and committed before the run (10.4); GO's meaning is unchanged. M3 option (i): the class 𝒟_P* is enlarged to near-cap favourite laws (U(0.80, 0.90), U(0.85, 0.90), a point mass at 0.89, two-point mixtures) and λ_θ 1.70 → 2.15, λ_κ 1.60 → 1.80 (8.1d); "CORE prices to 0.90" is no longer printed as a class.** m12 / m13 fixed. The feasibility finding (no design passes GO; no usable negative-result instrument) is stated, not repaired | run J: 1,288 enlarged-class cells × 20,000 + 27 cells × 100,000 (L_W miss ≤ 0.0397 [0.0385, 0.0409], size ≤ 0.0253, T1a ≤ 0.0199, NEG ≤ 0.0073, U_W ≤ 0.0034; Astra's M3 cells 0.0312 [0.0302, 0.0323] / T1a 0.0167 [0.0159, 0.0175] against 0.0568 / 0.0244 at the cycle-2 λ); 684 gate-derivation cells and 256 gate-verification / GO-rate cells; power of T2 at the design's own θ_PCE ≥ 0.976 under the new rule (0.014–0.51 under the old); GO_new = 0 for every declared design; failed candidates published (8.1d, 10.4) | NO | NO |
| D8-DEP | D8 MAJOR: date-only primary ignores station persistence | two-way date-block × station, max of three SEs | **Adopt** (section 9) | SIMULATED here and by Fable: date-only κ test rejects 0.095–0.205 at nominal 0.025 | NO | NO |
| D2-SM | D2 CRITICAL: undefined regions, unpinned analysis date | six-label partition + orthogonal validity/accessibility | **Adopt with modifications**: three orthogonal axes (VALIDITY, SCIENTIFIC, OPERABILITY); SCIENTIFIC is the product INFORMATION_RESULT × ECONOMIC_RESULT (Fable's six labels are six of its twelve cells); INFORMATION_INSUFFICIENT added; relevance exclusion evaluated before confirmation; ECONOMIC_BOUND report field; one analysis time (D4 repair R2: the economic axis loses its exclusion row — 3 × 3 + 2 = 11 values — and ECONOMIC_BOUND becomes the θ_W report field REALIZED_WINDOW_BOUND; D4-C2) | proves totality by construction (section 17) | NO | NO |
| D3-BOOK | D3 CRITICAL (operational): CLOB `timestamp` is last change, not observation | window on `captured_at` | **Adopt** with clock tolerance, retries, provenance and a new completeness denominator (section 12) | quiet books are valid books | NO | NO |
| D5-OPS | D5 MAJOR: INACCESSIBLE pre-empts REJECTED | orthogonal accessibility flag | **Adopt**: OPERABILITY_STATE is a separate axis and never replaces the scientific label | a negative result must stay visible | NO | NO |
| D6-READY | D6 MAJOR: 30-day burn-in cannot supply 30 prior resolved dates | station-level READY, GLOBAL_READY, 14-date observation phase | **Adopt with modifications** (station-kind readiness, 80% of table both kinds, 40-day freshness, 14 consecutive GLOBAL_READY dates, 21-day t0 validity) | converts burn-in into an outcome-free information phase | NO | NO |
| D7-UNIT | D7 MAJOR: °F 2-degree ladders fail E4 | Architect's call | **Include °F by exact interval arithmetic** (section 14) | mechanical, unambiguous (MEASURED 66/66 ladders: 2 tails + nine contiguous 2 °F buckets; whole-degree °F settlement, no unit conversion), 48 vs 37 stations for the station dimension, matches V1's own σ = 1.8 °F and E13 intent | NO | NO (cohort only) |
| D-EXEC | Astra §6.5: +0.01 on a 0.001 ask is 11× cost | one venue tick | **Adopt**: CONSERVATIVE slippage = one tick of the market's recorded tick size | the flat +0.01 is incoherent in the 0.001 regime; REALISTIC (the estimand's execution) is unchanged | NO | NO (`EXECUTION_MODEL_CHANGED = TRUE`) |
| D-SEQ | S4: optional 90/120 analysis | at most one futility look on bounded statistics | **No interim at all** | paper experiment, zero capital at risk; a futility look saves ≤ 60 days but adds α bookkeeping, a tail-kill hazard and a human peek (section 11) | NO | NO |
| D-ATTR | criterion 9 margin ≥ θ_MEUE has no inferential content | compare on κ / tail count or keep descriptive | **Descriptive only**; information attribution is carried by the T1 information test | a difference of two θ̂ with SE 0.04–0.14 cannot carry a 0.02 margin | NO | NO |
| D10-BIAS | D10 MINOR: NO_DATA_LOWEST enters the bias mean | excluding it is a rule change (Architect's call) | **Preserve V1 bias rule; disclose and monitor** | not logically required for validity; changing it would change R* | NO | NO |
| D11-MECH | D11 MINOR: mechanics baseline includes structural ineligibility | baseline excluding structural + readiness codes | **Adopt** with explicit mechanics reason codes and an immediate stop on a fee change | structural exclusion is not venue deterioration | NO | NO |
| D12-TIER | D12 MINOR: tier ledgers Asia-weighted | report tier θ separately | **Adopt**; T_entry order kept (causal), same-instant ties broken by a neutral hash | first-come-first-served is the only causal allocation without reservation | NO | NO |

---

## 3. Unchanged trading rule R* (restated for the Builder; V1 §9 governs)

Primary model Open-Meteo Ensemble `ecmwf_ifs025` (51 members, daily max/min, station time zone, `forecast_days=3`); point-in-time bias `b_{s,κ}` = mean over the last `W = 30` usable resolved local dates of `(y_d − mean_i m_i(d))`; dressed predictive CDF `P(T ≤ x) = (1/M) Σ_i Φ((x − m_i − b)/σ)` with `σ = 1.0 °C / 1.8 °F`; bucket probabilities `q_k` by the interval arithmetic of section 14; executable asks `a_k^YES`, `a_k^NO`; fee `f(a) = 0.05 a (1 − a)`; edges `E^YES = q − a − f(a)`, `E^NO = (1 − q) − a^NO − f(a^NO)`; single argmax leg over 22 legs, trade iff `E_max ≥ h = 0.10`; ties lower bucket index, YES before NO; hold to settlement; `T_entry = game_start_time − 6 h`; `S_ref = 50 USD` per leg without capital cap.

Clarifications that are **not** changes (V1 was silent; these are the only deterministic readings consistent with V1 text):

- Vintage selection: the decision for event e uses the PRIMARY vintage with the **greatest** `captured_at` satisfying `T_entry(e) − 3 h ≤ captured_at < T_entry(e)` (V1 E6 + invariant 2).
- Bias members `m_i(d)`: the members of the vintage that was (or, for pre-t0 dates, would have been) selected for date d under the previous bullet.
- `y_d` for a resolved middle bucket = the mean of the bucket's integer set (°C single-degree bucket → the integer itself, identical to V1; °F bucket `86-87°F` → 86.5); tail buckets → the boundary integer (V1). All final settlement modes are usable (V1; D10 in section 19).
- °F forecasts: members fetched in °C (V1 request) and converted exactly, `m_F = 1.8 m_C + 32`, no rounding.

---

## 4. Architecture selection (D1)

| Family | What it answers | Fatal / decisive property | Decision |
|---|---|---|---|
| A — cumulative multi-year | θ ≥ 0.02 after 1,300–11,000 dates (power table) | the venue changed the settlement template at least twice in ≈ 6 months (V1 C5, §20); a 4–30-year program answers a question about a venue that will not exist in that form; seasonal cycle of a 30-day trailing bias adds a between-window variance component | **REJECTED** |
| B — two-threshold fixed | confirm/exclude a large edge; honest labels | alone, a zero-edge rule is INDETERMINATE 75–88% of the time: no real negative result | **ADOPTED as the label layer** |
| C — group-sequential | early stop for large or absent edges | efficacy stopping is useless in the plausible effect range; futility on θ is hazardous with rare tail wins (Fable CD2); interim looks create a human peek | **REJECTED** (no interim, section 11) |
| D — stratified two-estimand | executable mispricing (core and tail) with a real negative result; θ confirmation at θ_PCE | the information test must be stratified (a pooled κ test is blind to a tail edge); a gate on θ blocks payout-concentrated edges; PINM exactness depends on declared dependence | **ADOPTED, configured without the gate** (sections 5–9, D1-GATE) |

### 4.1 Proof that the Family D information axis does not smuggle in a strategy change

1. For every event V1 would have admitted, R*'s inputs, parameters, leg choice, REALISTIC fills, capital, hold rule and contribution to θ are identical to V1; the replay invariant (V1 §24.14) is unchanged. The only domain change is the °F cohort (D7), decided from ladder mechanics, not from the information axis.
2. κ_core and the tail win count are computed **from the same trades** R* already opened; no leg is added, removed, resized or re-timed. The stratum label is a deterministic function of the chosen leg's best ask at T_entry, recorded before any outcome exists.
3. θ is the only quantity that enters a net-value label; κ is never reported as R*'s return. κ is, exactly, the average net P&L per share of a *constant-payout* (one share per leg) version of R* on the core stratum; the spec names it as an information statistic only.
4. The information axis can neither create nor withhold a net-value claim: the economic axis is decided by θ alone (T2, θ̂, gates on the realised-window value θ_W; prospective content only through the transport frontier, 8.5c); the information axis only adds diagnostic claims about which legs are mispriced and the real negative result. No trade exists or disappears because of it.

---

## 5. Estimands

### 5.1 Primary economic estimand (unchanged)

```text
θ = E[N_j] / E[C_j],  estimated by θ̂ = Σ_j N_j / Σ_j C_j
over trades j of R* on the prospective eligible cohort, REALISTIC execution, S_ref = 50 USD,
N_j = n_j · (y_j − c_j),  C_j = V_j + F_j,  c_j = C_j / n_j (all-in cost per share, fee included).
```

No winsorising, trimming, capping or leg deletion inside θ, ever. Winsorised or trimmed θ may appear only in the sensitivity section with the label `NOT_THE_ESTIMAND`.

**Prospective vs realised-window value (D4 repair R2, after Astra D4 recheck C2).** The estimand above is **prospective** and is written `θ_P` wherever the distinction matters: the expectation is over the executed-trade process of R* (market opportunity process × R* × REALISTIC fill at S_ref, section 8.5b), so it includes opportunity types — in particular rare sub-4¢ TAIL legs — that a finite window may not contain. `θ_P` is the only strategic economic quantity. After D4 repair R3 it is **not an empirical estimand of V2**: no label asserts it unconditionally (8.5c). A second estimand is frozen. It is report-only under R2, and under R3 it is the **empirical economic estimand** of ECONOMIC_RESULT:

```text
θ_W = Σ_{j∈WINDOW} n_j (p_j − c_j) / Σ_{j∈WINDOW} C_j
      p_j = true settlement probability of trade j's token given the information at T_entry(j)
```

`θ_W` is the expected net value per dollar of the trades R* actually executed in the window, conditional on which trades occurred. It is neither the realised P&L `Σ N_j / Σ C_j` nor `θ_P`. Under R3 it is tested by T2 (lower side) and bounded by U_W (upper side, `REALIZED_WINDOW_BOUND`). It never rejects R*, and it reaches the future only through the declared transport class of 8.5c.

### 5.2 Price strata (frozen, outcome-independent)

```text
TAIL(j)  iff  a_j < 0.04,   where a_j = best ask of the chosen token in the ENTRY snapshot used by the decision
CORE(j)  otherwise
```

`0.04` is a frozen numeric constant equal to the venue's low-price tick-regime boundary (V1 C15; Fable §2.4); it is **not** read from the live tick field, which is a market-level property shared by the YES and NO tokens (MEASURED: `orderPriceMinTickSize` = 0.001 on 1,550 and 0.01 on 1,431 of 2,981 live temperature markets) and whose transition semantics are UNKNOWN. R* can never trade a leg priced above 0.90 (a NO leg needs `1 − q − a − f ≥ 0.10`), so the price definition only ever separates cheap YES/NO lottery legs from the rest. Stratum membership is stored in SIGNAL_DECISION at decision time and is immutable.

### 5.3 Information estimands (confirmatory information axis; never economic returns)

```text
κ_core   = E[y_j − c_j | CORE]         estimated by κ̂_core = mean over CORE trades of (y_j − c_j)
λ_tail   = E[W_tail] / Λ_tail           with W_tail = Σ_{TAIL} y_j,  Λ_tail = Σ_{TAIL} c_j
```

Interpretation. `κ_core > 0` means R*'s core legs win more often than their **all-in executable cost** implies: an executable mispricing net of fee and walked spread, per share. `λ_tail > 1` means the tail legs win more often, in aggregate, than their all-in costs imply. Both are properties of the legs R* selected; they are information statements about the forecast-driven selection, not returns of R* (R* sizes by constant dollars, so its return is θ).

Why κ uses the all-in cost `c_j` and not the mid: the information test should ask whether the information survives the costs a taker actually pays; a mid-based calibration gap that the spread eats is reported by the descriptive baselines B1/B2 (V1 §10).

Reported decomposition (not separate claims): `θ = w_core θ_core + w_tail θ_tail` with `w` the realised capital shares (known at T_entry), `θ_core`, `θ_tail`, capital and count shares, `W_tail`, `Λ_tail`, the largest single-trade contribution to Σ N.

---

## 6. Hypotheses and test structure

### 6.1 Claims and nulls

| Test | Null | Alternative | Level (one-sided) | Engine (section 8) |
|---|---|---|---|---|
| T1a core information | κ_core ≤ 0 | κ_core > 0 | α/2 = 0.025, joint with reach, attained over 𝒟_P* (8.1c) | `κ̂_core − λ_κ · max_{b∈{5,10,20,30}} t_{df_b,0.975} SE_2w(b; κ̂_core) > 0`, λ_κ = 1.80 (D4-C3-P1, 8.1d; cycle 2: 1.60) |
| T1b tail information | λ_tail ≤ 1 (sharp null `p_j = c_j` on TAIL) | λ_tail > 1 | α/2 = 0.025 (exact under the declared copula; measured ≤ 0.0077 over 𝒟_P*, 8.1c, 8.1d) | PINM exact win-count test |
| **T1 information** | both T1a and T1b nulls | information exists in core **or** tail | α = 0.05 (Bonferroni) | rejects iff T1a or T1b rejects |
| **T2 economic (primary)** | θ_W ≤ 0 | θ_W > 0 | α = 0.05, **evaluated unconditionally** (no gate); joint with reach, attained over the completely stated class 𝒟_P* (8.1c) | `L_W > 0` with the calibrated multi-block two-way CR bound `L_W = θ̂ − λ_θ · max_{b∈{5,10,20,30}} t_{df_b,0.95} SE_2w(b)`, λ_θ = 2.15 (D4-C3-P1, 8.1d; cycle 2: 1.70; cycle-1 8.1b used λ = 1; R3 used 5-date blocks only); estimand θ_W after D4 repair R3 (8.5c) |
| NEG core adverse | κ_core ≥ 0 | κ_core < 0 | **0.025**, joint with reach, attained over 𝒟_P* including near-cap favourite (left-skewed) CORE prices (8.1c, 8.1d, 8.4) | `κ̂_core + λ_κ · max_{b} t_{df_b,0.975} SE_2w(b; κ̂_core) < 0`, λ_κ = 1.80 (8.1d) |
| EXCL-P prospective exclusion | θ_P ≥ threshold | θ_P < threshold | — | **none: not usefully testable within V2's observable horizon (8.5b); no test is run and no label exists** |
| CONF-P unconditional prospective confirmation | θ_P ≤ 0 | θ_P > 0 | — | **none: not usefully testable without a transport restriction (8.5c mirror theorem); no label exists** |
| TRANSPORT (report) | — | — | no α (assumption-indexed) | deductive robust bound `L_T(ε, δ) = (1 − ε)(L_W − δ) − ε` over 𝒯_H(ε, δ); frontier ε*(δ, τ) (8.5c) |
| EXCL-W realised-window bound (report field) | θ_W ≥ threshold | θ_W < threshold | 0.05, joint with reach, attained over 𝒟_P* (calibrated core bound at one-sided 0.975 + deterministic tail supremum; 8.1c) | U_W = w_core U_core + M_tail, `U_core = θ̂_core + λ_θ · max_b t_{df_b,0.975} SE_2w(b; θ̂_core)`, λ_θ = 2.15 (sections 8.5, 8.1c, 8.1d) |

### 6.2 Powered claim

```text
ECONOMIC_RELEVANCE_THRESHOLD   θ_ERT = 0.02            (economic reporting threshold; not a powered claim)
PRIMARY_CONFIRMABLE_EFFECT     θ_PCE = frozen formula    (section 10; 80% power for the calibrated T2 actually run, via Z_EFF = 7.2, under the planning model and given INFO_SUFFICIENT; D4-C3-P1, 10.4)
TARGET_POWER                   0.80 at θ_PCE (nominal, normal approximation, before the robustness gates G1–G3)
```

D4-C3-P1 disclosure (supersedes the gate meaning of the D4-C3-M2 disclosure kept next): θ_PCE is now computed with the effective multiplier Z_EFF = 7.2 (10.2, 10.4) instead of the nominal Z_80 = 2.4865, and SE_KAPPA_CEILING is 0.005. With T2 at λ_θ = 2.15, the simulated power of T2 at the design's **own** θ_PCE, given INFO_SUFFICIENT, is 0.976–1.000 in every declared design that passes the θ-side clause (≥ 2,000 GO ∧ INFO replications per cell; 100,000-replication worst cells 0.9744 [0.9734, 0.9754], 0.9825, 0.9969), against 0.014–0.51 under the cycle-2 formula (power table §4.10). The single multiplier is the maximum over the declared laws, so it **over-certifies** favourite-concentrated designs (power ≈ 1 where 0.80 was the target); that is the stricter-only direction. The mid-price 80%-power effect is ≈ 0.21 at m = 17 and ≈ 0.15 at m = 55, and no mid-price design passes the θ-side clause. The figures of the cycle-2 and cycle-1 disclosures below describe retired tests or a retired gate and are kept as history.

D4-C3-M2 disclosure (history; λ_θ = 1.70; supersedes the numbers of the D4-C3-M1 disclosure kept next): with the bounds calibrated over 𝒟_P* (8.1c), P(T2) at θ_PCE is 0.109 / 0.084 / 0.067 / 0.070 for m = 17 thin / 17 full / 35 thin / 35 full (joint with reach, no persistence), and the 80%-power effect is ≈ 0.18 (m = 17). (History: at that time θ_PCE's formula, PCE_CEILING and GO / NO_GO were left unchanged and not retuned (power table §4.9); Astra @8874dc54 showed that left the gate contradicting its rationale; D4-C3-P1 recalibrates the gate.)

D4-C3-M1 disclosure (history): θ_PCE's formula, its nominal meaning and GO / NO_GO are unchanged and not retuned. The persistence-calibrated T2 (8.1b) is more conservative than the normal-approximation reference, so its simulated power at the design's own θ_PCE is below 0.80: P(T2) at θ_PCE is 0.554 / 0.476 / 0.456 / 0.459 for m = 17 thin / 17 full / 35 thin / 35 full (θ_PCE = 0.09 / 0.08 / 0.07 / 0.07), against 0.779 / 0.701 / 0.673 / 0.675 for the R3 engine (no persistence). The simulated 80%-power effect is ≈ 0.11–0.12 (R3 engine ≈ 0.09–0.10; linear interpolation of P(T2) between θ_PCE and 0.12, no persistence) (power table §4.8).

### 6.3 Error control

- **Level convention (D4-C3-M2).** Every level in this section is a repeated-experiment rate jointly with reach (GO ∧ INFO_SUFFICIENT), attained over the completely stated class 𝒟_P* (8.1c); none is claimed outside 𝒟_P*, and none is a rate conditional on reach (8.1c discloses those).
- **T1** is a union test at familywise α = 0.05 over its two strata: T1a and T1b at α/2 each (Bonferroni; valid under any dependence between core and tail; with two tests Holm's first step is identical and Simes' gain is confined to both p in (0.025, 0.05]). Measured over 𝒟_P*: T1a ≤ 0.0199 (20,000; 0.0190 [0.0182, 0.0199] at 100,000), T1b ≤ 0.0077, T1 ≤ 0.0078 in the TAIL designs (8.1c, 8.1d).
- **T2** is the single primary economic test at α = 0.05, tested whether or not T1 rejects. Every scientific state that asserts more than one favourable claim (for example INFORMATION_DETECTED together with REALIZED_WINDOW_VALUE_SUPPORTED) asserts an **intersection** of claims, each tested at α; by the intersection-union principle the probability that such a state is issued while any of its claims is false is ≤ α. This rests on each component level, which holds over 𝒟_P* for the calibrated tests of 8.1c / 8.1d (and did not hold for the pre-repair 5-date T1a / NEG; Astra M2). No α is spent twice and none is recycled.
- Adverse claims: NEG at 0.025 on κ_core (information axis; calibrated, 8.1c). There is **no adverse prospective economic claim** (D4 repair R2, section 8.5b) and **no unconditional favourable prospective claim** (D4 repair R3, 8.5c). The transport frontier adds no α: its only probability is T2's own sampling coverage of θ_W. The realised-window bound U_W (section 8.5) is a report field on θ_W at level 0.05 over 𝒟_P* (8.1c, 8.1d; measured ≤ 0.0034); it is never part of a SCIENTIFIC_STATE label and cannot reject R*, so no α is shared with T2.
- Why not Fable's fixed-sequence gate: under IUT the joint claim needs no gate for error control, and the gate's only other effect is to withhold a confirmed θ when the count-based information statistic is less efficient than θ itself (SIMULATED, D1-GATE). A confirmed θ without detected information is reported as it is (`NO_INFORMATION_DETECTED__REALIZED_WINDOW_VALUE_SUPPORTED`), and the forward-signal rule (17.5) still requires that the core not be significantly adverse.
- Exploratory family (V1 §15, E1–E15): Holm at α = 0.05 within the family, never promoted (unchanged).

---

## 7. Information and power (D1; details in the power table file)

DERIVED with `z_{0.95} + z_{0.80} = 2.4865`, `z_{0.95} + z_{0.90} = 2.9264`:

- Independent trades for 80% power: θ = 0.02 → 15,456 / 61,826 / 129,988 at σ_eff = 1.0 / 2.0 / 2.9; θ = 0.05 → 2,473 / 9,892 / 20,798; θ = 0.10 → 618 / 2,473 / 5,200 (reproduces Astra §6.3 and Fable §1.1 to the unit).
- **Binding constraint = target dates.** With `m` trades per date and latent within-date correlation, the date design effect is `1 + (m − 1) ρ_d`, so `n_eff ≤ D / ρ_d`: at ρ_d = 0.03, 120 dates cap `n_eff` at 4,000 regardless of throughput; at 0.05, 2,400. The planning dependence model is `DEFF(m) = 1.5 × (1 + 0.03 (m − 1))` (station factor 1.5 × date factor), giving DEFF 2.2 / 3.0 / 3.9 at 17 / 35 / 55 trades per date — inside Astra's 2–4 range and rising with throughput as the date ceiling requires.
- At 120 counted dates and the conservative V2 throughput (35/day, °C + °F): `SE(θ̂)` = 0.027 / 0.054 / 0.078 at σ_eff 1.0 / 2.0 / 2.9 → **MDE80 = 0.067 / 0.134 / 0.194**; `SE(κ_core)` ≈ 0.014 → MDE80 ≈ 0.035 per share. (These θ and κ MDEs are for the normal-approximation, 5-date-block reference. The persistence-calibrated tests need much larger effects for 80% power: T2 ≈ 7.2 × SE0_θ (≈ 0.21 mid-price at m = 17, ≈ 0.10 favourite at m = 17, ≈ 0.05 near-cap favourites at m = 55; D4-C3-P1, power table §4.10), and NEG needs |κ| ≈ 10–12 × SE0_κ for 90% power (≈ 0.12–0.15 per share at m = 17); the T1a MDE80 of ≈ 0.11 per share measured for D4-C3-M2 at λ_κ = 1.60 is larger at 1.80 and was not re-measured; cycle-1 T2 ≈ 0.11–0.12, §4.8.)
- θ = 0.02 requires ≈ 1,340 dates at σ_eff = 1 (≈ 3.7 years) and ≈ 11,250 dates at σ_eff = 2.9 at that throughput (DERIVED).
- The information needed to **exclude** 0.02 when θ = 0 is identical to that needed to confirm it (Fable §1.6, reproduced): the 120-date outcome space is three-valued at the ERT scale by construction.

---

## 8. Inference engines (D4, D8, PINM)

All engines are deterministic given the archived data, the frozen constants and the frozen seeds. The Builder implements them exactly; no method substitution.

### 8.1 Primary engine for κ_core, θ_core and pooled θ: two-way cluster-robust (CR) t-test

For a statistic with linearised residuals `e_j` and denominator `Q`:

| Statistic | `e_j` | `Q` |
|---|---|---|
| κ̂_core | `(y_j − c_j) − κ̂_core`, CORE trades | number of CORE trades |
| θ̂ (pooled) | `N_j − θ̂ C_j`, all trades | `Σ C_j` |
| θ̂_core | `N_j − θ̂_core C_j`, CORE trades | `Σ_{CORE} C_j` |

Clusters (section 9): `B` = date block, `S` = station (ICAO), `BS` = block × station intersection. For each dimension `g ∈ {B, S, BS}` with `G_g` non-empty clusters: `V_g = G_g/(G_g − 1) × Σ_{clusters} (Σ_{j∈cluster} e_j)² / Q²`. Two-way: `V_2w = V_B + V_S − V_BS`.

```text
SE          = sqrt( max(V_B, V_S, V_2w) )          (never the IID variance; never date-only)
df          = min(G_B, G_S) − 1
one-sided upper / lower bounds at level 1 − a:   stat ± t_{df, 1−a} · SE
```

The max-of-three rule also resolves the non-PSD case: `V_2w` can be negative in finite samples; the maximum then selects the larger one-way variance, never zero and never IID.

**D4-C3-M2.** The bounds actually used by T2 (L_W), U_W, T1a and NEG apply this engine at 5-, 10-, 20- and 30-date calendar blocks, take the largest `t_{df_b, q} · SE_2w(b)` and multiply it by a frozen constant (λ_θ = 2.15 for θ̂ and θ̂_core, λ_κ = 1.80 for κ̂_core since D4-C3-P1; 1.70 / 1.60 in cycle 2): sections 8.1c, 8.1d. The single 5-date-block form above is used directly only by IF4 / IF5 (11.4) and in reported diagnostics.

### 8.1b Source lower bound L_W for T2: multi-block calibration (D4-C3-M1, after Astra D4-C3 recheck M1 @5bb57eb2) — cycle-1 record

**SUPERSEDED IN PART by 8.1c (D4-C3-M2, after Astra D4-C3-M1 recheck @ac777a87: M1-R, M2).** The derivation and the run-G evidence below are kept as the cycle-1 record. The authoritative rules are in 8.1c:
- L_W is the bound below multiplied by the frozen constant λ_θ = 2.15 (D4-C3-P1; 1.70 in cycle 2);
- κ̂_core (T1a, NEG) and θ̂_core (U_W) use the same multi-block construction with λ_κ = 1.80 / λ_θ = 2.15 (D4-C3-P1; 1.60 / 1.70 in cycle 2);
- the class is the completely stated 𝒟_P* (8.1c).

The level statements of this section ("≤ 0.05 over 𝒟_P") are SUPERSEDED. They held only on the run-G grid (c ~ U(0.35, 0.80), no pauses, Gaussian AR(1)). Inside the class as the spec wrote it, the cycle-1 rule reaches a joint miss of 0.1176 (run H, 8.1c).

**Defect repaired.** Section 8.1 counts covariance only inside a 5-date block. A date-common shock that persists across blocks is therefore under-counted. Section 9 itself names two such mechanisms: the lag of the 30-date trailing bias through a seasonal transition, and hemisphere/season common modes. Under them, R3's `L_W = θ̂ − t_{df,0.95} · SE_CR(θ̂)` undercovers θ_W.

DERIVED (a stationary AR(1) date component over 120 dates, demeaned, CR1 factor; 20,000 draws): the share of that component's variance that a b-date block estimator captures is

| Daily autocorrelation φ | b = 5 | b = 10 | b = 20 | b = 30 |
|---|---|---|---|---|
| 0.5 | 0.73 | 0.85 | 0.93 | 0.95 |
| 0.8 | 0.39 | 0.58 | 0.76 | 0.83 |
| 0.9 | 0.21 | 0.36 | 0.56 | 0.68 |

Astra M1 measured, at φ = 0.8 with latent regime variance 0.05 and 17 trades per date:
- a false REALIZED_WINDOW positive claim of 0.0805 at θ_W = 0;
- an L_W miss of 0.0902.

Run G reproduces both with fresh code and seeds: false positive 0.0789 [0.0752, 0.0826] and full-fill miss 0.0889 [0.0850, 0.0928] on the R3 engine; 0.0271 and 0.0319 under the rule below. Over the declared class below, the R3 engine reaches a joint miss of 0.1287 [0.1241, 0.1333] and a size of 0.1195 [0.1150, 0.1240] (φ = 0.9). It already exceeds 0.05 at φ = 0.5 (0.0621).

**Rule (cycle-1 form; in force only as the λ = 1 member of the 8.1c family, i.e. SUPERSEDED by 8.1c).**

```text
L_W      = θ̂ − max_{b ∈ {5, 10, 20, 30}} t_{df_b, 0.95} · SE_2w(b)
SE_2w(b) = the section-8.1 two-way max-of-three SE of θ̂ (e_j = N_j − θ̂ C_j, Q = Σ C_j), with
           date block   block_b(D) = floor((D − D_0) / b) in calendar days   (b = 5 is the section-9 block),
           station = ICAO, intersection = (block_b, ICAO)
df_b     = min(G_B(b), G_S) − 1          (G = number of clusters with ≥ 1 trade)
T2       ⟺ L_W > 0
HEADLINE   two-sided 90% interval  θ̂ ± max_b t_{df_b, 0.95} · SE_2w(b)   (its lower end is L_W)
```

- **Scope.** Only the pooled-θ lower bound changes: T2, L_W, the headline interval, and everything in 8.5c and 17.3 that reads L_W. κ̂_core (T1a, NEG, IF4, IF5), θ̂_core (U_W, 8.5) and every other use of 8.1 keep 5-date blocks. Those surfaces are frozen; their behaviour under persistence is disclosed at the end of this section. *SUPERSEDED by 8.1c:* κ̂_core and θ̂_core now use the same multi-block construction; IF4 / IF5 keep 5-date blocks.
- **Always defined when evaluated.** INFO_SUFFICIENT requires ≥ 12 non-empty 5-date blocks (IF2). The b-date blocks nest the 5-date blocks, so there are at least 6 / 3 / 2 non-empty 10- / 20- / 30-date blocks, and df_b ≥ 1. With 120 consecutive counted dates and ≥ 25 stations, df = 23 / 11 / 5 / 3 for b = 5 / 10 / 20 / 30.
- **Monotone.** b = 5 is one of the four bounds, so L_W is never above the R3 bound. T2 can only become harder to pass. No label, threshold or constant changes.
- **Outcome-blind.** b = 30 is W, the 30-date trailing-bias window whose seasonal lag is the mechanism §9 names; 10 and 20 are the intermediate doublings. Nothing is estimated from or selected on data.

**Declared persistence class 𝒟_P (cycle-1 grid; SUPERSEDED by the completely stated class 𝒟_P* of 8.1c).**
- V2's simulation dependence: latent Gaussian copula (date, station, cell) = (0.05, 0.05, 0.10).
- Plus a stationary daily AR(1) date regime `e_t = φ e_{t−1} + √(1 − φ²) z_t`, shared by every trade of date t and added on the latent scale with variance rv.
- φ ∈ {0.5, 0.7, 0.8, 0.9} and rv ∈ {0.02, 0.05, 0.10}, plus the no-persistence baseline.
- Geometry: 14 OP + 120 window dates; 48 stations with gamma(2) activity; Poisson(m) trades per date with m ∈ {17, 35}; fills thin (C ~ U(5, 25)) or full (C = 50); CORE prices; θ ∈ {0, 0.05, 0.10}.

In plain words, φ = 0.9 is a date-level shock whose correlation decays by 10% per day (integrated memory ≈ 19 days). That is the order of the 30-date trailing-bias lag that §9 names.

𝒟_P is this declared grid. Wherever this spec writes "φ ≤ 0.9, latent variance ≤ 0.10", it means the grid, and no level is claimed between grid points beyond what the grid shows. In every 17-trades/date slice, where the worst cells are, run G's miss rises monotonically with φ. Every 35-trades/date cell is ≤ 0.012.

**Level (what holds).** The error is the repeated-experiment joint rate `P(reach ∧ L_W > θ_W)`, with reach = GO ∧ INFO_SUFFICIENT. At θ_W = 0 it is the size of the positive REALIZED_WINDOW claim. Run G used 20,000 replications per cell over the 156 class cells, with ≥ 100,000 independent replications for the cells nearest 0.05 (power table §4.8).

| Dependence | This rule: worst joint miss (95% MC) | Worst size at θ_W = 0 | Stated level | R3 engine, same cells |
|---|---|---|---|---|
| 5-date-block model (no cross-block persistence) | 0.0174 [0.0155, 0.0192] | 0.0163 | ≤ 0.05 (conservative) | 0.0559 [0.0527, 0.0591] |
| 𝒟_P, φ ≤ 0.8 | 0.0319 [0.0295, 0.0343] | 0.0293 | ≤ 0.05 | 0.0889 [0.0850, 0.0928] |
| 𝒟_P, φ = 0.9 | 0.0465 [0.0436, 0.0494] at 20,000 replications (φ 0.9, latent variance 0.05, m = 17 thin, θ = 0.10); independent 100,000-replication re-runs 0.0458 [0.0445, 0.0471] (that cell) and 0.0464 [0.0451, 0.0477] (full fills) | 0.0423 [0.0395, 0.0451] | **≤ 0.05** | 0.1287 [0.1241, 0.1333] |
| outside 𝒟_P (φ 0.95–0.97, or rv 0.20) | up to 0.0721 [0.0685, 0.0757] (φ = 0.95) and 0.1098 [0.1055, 0.1141] (φ = 0.97), latent variance 0.05, m = 17; rv 0.20 is screened by IF5 (≤ 0.010) | — | **none claimed; the miss is higher (coverage lower)** | up to 0.1728 (φ = 0.95) and 0.2130 (φ = 0.97) |

*SUPERSEDED (Astra M1-R):* So, over the whole declared class 𝒟_P: `P(reach ∧ L_W > θ_W) ≤ 0.05`, and the positive REALIZED_WINDOW claim has size ≤ 0.05. This held on the run-G grid only. Under favourite CORE prices, paused dates, two-state regimes or the 30-date trailing-mean mechanism, the cycle-1 rule exceeds 0.05 (Astra @ac777a87: 0.0605–0.0852; run H: up to 0.1176, 8.1c).

The rate conditional on reach is larger, because IF5 screens high-dispersion windows rather than slow drifts. Over cells with reach ≥ 0.10 it reaches 0.085 (φ ≤ 0.8) and 0.136 (φ = 0.9) for this rule, against 0.189 / 0.281 for the R3 engine. This is the R3 caveat ("not the probability given that a label was issued"), now quantified.

**Why this rule.** The rule and the class were declared before any run. A first candidate, RM (blocks {5, 10, 20}), was declared first. A preliminary run showed it failing at φ = 0.9. Two comparators were then declared, each before its own first run, together with the selection criterion: validity over the whole class first, then power and information-floor behaviour. All four rules are reported on the same replications (power table §4.8):

| Rule | Worst joint miss, φ ≤ 0.8 | Worst joint miss, φ = 0.9 | Valid over 𝒟_P? | SUPPORTED at θ = 0.10, m = 17 thin, no persistence |
|---|---|---|---|---|
| R3 engine (5-date blocks) | 0.0889 | 0.1287 | no (fails from φ = 0.5) | 0.843 |
| RM {5, 10, 20} | 0.0477 | 0.0711 [0.0675, 0.0747] | no (φ ≤ 0.8 only) | 0.761 |
| RE two-way EWC, K = 4 (fixed-K t) | 0.0396 | 0.0574 [0.0542, 0.0606] | no (φ ≤ 0.8 only) | 0.716 |
| **adopted {5, 10, 20, 30}** | 0.0319 | 0.0465 (100,000-replication re-runs 0.0458 / 0.0464) | **yes** | 0.654 |

Only the adopted rule is valid over 𝒟_P, so it is adopted. With integrated memory ≈ 19 days, a 120-date window holds only about six independent date units. Any bound that is valid at φ = 0.9 must therefore work with few effective date degrees of freedom; the power cost below comes from persistence of that length, not from this particular estimator. RM and RE are published, not adopted.

**Power cost of the cycle-1 rule (stated, not retuned; superseded by the 8.1c power cost).**

SUPPORTED, joint with reach, no persistence; R3 engine → this rule:

| Fills, trades per date | θ = 0.10 | θ = 0.05 |
|---|---|---|
| thin, 17 | 0.843 → 0.654 | 0.379 → 0.187 |
| full, 17 | 0.851 → 0.668 | 0.386 → 0.195 |
| thin, 35 | 0.629 → 0.554 | 0.323 → 0.192 |
| full, 35 | 0.633 → 0.565 | 0.323 → 0.195 |

At the information floor (60 dates, 25 stations), df_30 = 1. Positive claims become nearly impossible there: SUPPORTED at θ = 0.10 is 0.001 (m = 17, thin) and 0.005 (m = 35, full), against 0.143 / 0.366 for the R3 engine.

- **T2 at the design's own θ_PCE:** P(T2) at θ_PCE is 0.554 / 0.476 / 0.456 / 0.459 for m = 17 thin / 17 full / 35 thin / 35 full (θ_PCE = 0.09 / 0.08 / 0.07 / 0.07), against 0.779 / 0.701 / 0.673 / 0.675 for the R3 engine (no persistence).
- **Effect confirmed with 80% T2 power:** ≈ 0.11–0.12 (R3 engine ≈ 0.09–0.10; linear interpolation of P(T2) between θ_PCE and 0.12, no persistence).
- **θ_PCE.** (Cycle-1 statement, SUPERSEDED by D4-C3-P1: the gate is now recalibrated to the tests actually run, 10.2–10.4.) Its frozen formula, GO / NO_GO and its nominal (normal-approximation) meaning were unchanged; it was not retuned (6.2, 10.3). An INDETERMINATE result is more likely than under R3; that is the price of a stated level that holds under the persistence §9 names.

**Frozen surfaces under persistence (cycle-1 disclosure; REPAIRED by D4-C3-M2, 8.1c).** T1a, NEG and U_W run on the unchanged 5-date-block engine. They are frozen and outside this bounded repair. On the same run-G replications:

| Surface | Nominal level | Baseline | 𝒟_P, φ ≤ 0.8 (worst) | 𝒟_P, φ = 0.9 (worst) |
|---|---|---|---|---|
| T1a false rejection (θ = 0) | 0.025 | 0.0293 | 0.0532 | 0.0893 |
| NEG false rejection | 0.025 | 0.0249 | 0.0400 | 0.0694 |
| U_W miss | 0.05 (declared) | 0.0269 | 0.0454 | 0.0765 |

Claim matrix 17.8 qualifies their stated levels accordingly. That is a statement change only: the tests are byte-identical. Calibrating them would need governance authority, so this is flagged to Astra and governance as an open observation. *SUPERSEDED:* the orchestrator ledger (cycle 2) records that these surfaces were a cycle-1 orchestrator bound, not an owner freeze. D4-C3-M2 calibrates them (8.1c).

### 8.1c Calibrated multi-block bounds for T2, U_W, T1a and NEG (D4-C3-M2, after Astra D4-C3-M1 recheck @ac777a87; authoritative)

**STATUS (D4-C3-P1).** The construction and the rule of this section stand. **The constants λ_θ and λ_κ, the CORE price laws of the class, and every level, selection, comparator, confirmation and power figure below are the cycle-2 (run H) record and are SUPERSEDED by 8.1d (λ_θ = 2.15, λ_κ = 1.80; enlarged class; levels re-stated) and by 10.4 (design gate).** Where they differ, 8.1d governs. The cycle-2 statement "CORE prices to 0.90" was wrong as a class description (Astra M3) and is withdrawn.

**Defects repaired.**
- **M1-R.** The 8.1b bound held ≤ 0.05 only on the run-G grid: c ~ U(0.35, 0.80), no pauses, Gaussian AR(1). Inside the class as the spec wrote it, it failed: favourite CORE prices, up to 30 paused dates, a two-state regime, and the literal 30-date trailing-mean mechanism that §9 names (Astra @ac777a87: 0.0531–0.0852).
- **M2.** T1a / NEG (κ̂_core) and U_W (θ̂_core) kept 5-date blocks. They undercovered inside the persistence class (Astra: 0.0888 / 0.0707 / 0.0755 against 0.025 / 0.025 / 0.05) while §6.1, §6.3, §8.4, §8.5, §9, §10.1, §10.3, §24, the 17.3 fields and the manifest asserted nominal levels.

Both are repaired by one construction, calibrated over one completely stated class (option (a) for both).

**Rule (frozen; D4-C3-M2).** For a statistic with the section-8.1 residuals and denominator (θ̂ pooled, κ̂_core, θ̂_core):

```text
H_q(stat)  = max_{b ∈ {5, 10, 20, 30}} t_{df_b, q} · SE_2w(b; stat)        (8.1b blocks: calendar floor((D − D_0)/b), df_b = min(G_B(b), G_S) − 1)
L_W        = θ̂ − λ_θ · H_0.95(θ̂)                                          T2 ⟺ L_W > 0
U_W        = w_core · (θ̂_core + λ_θ · H_0.975(θ̂_core)) + M_tail          (8.5 structure and M_tail unchanged)
T1a        ⟺ κ̂_core − λ_κ · H_0.975(κ̂_core) > 0
NEG        ⟺ κ̂_core + λ_κ · H_0.975(κ̂_core) < 0
HEADLINE   = realised-window interval [L_W, U_W]
λ_θ = 2.15,  λ_κ = 1.80                                                   (frozen constants; section 10.1; D4-C3-P1, 8.1d. Cycle 2: 1.70 / 1.60)
```

- **Unchanged.** IF4 (`SE_CR(κ̂_core) ≤ 0.025`) and IF5 (`DEFF_2w(κ̂_core) ≤ 6`) keep their frozen 5-date-block definitions, and GO / NO_GO is unchanged, so **reach is numerically unchanged**. IF4 keeps its meaning: a reliability floor on the 5-date-block SE. It is no longer the test's half-width scale. The median ratio of T1a's half-width to the 5-date-block half-width `t_{df5,0.975} SE_κ(5)` is 1.52 × 1.60 ≈ 2.4 without persistence (run H).
- **Monotone.** b = 5 is one of the four blocks and λ ≥ 1, so every bound is at least as wide as its 5-date-block (R3) form, and as the cycle-1 form of 8.1b. Every favourable and adverse test can only become harder to pass.
- **Always defined when evaluated.** IF2 gives df_b ≥ 1 (8.1b).
- **Headline consistency (Astra M2 second-order).** The headline interval is now `[L_W, U_W]`, so REALIZED_WINDOW_LOSS_CONFIRMED (U_W < 0) is printed only when the headline interval lies below 0. Its two ends are the two calibrated one-sided bounds. By the union bound its joint non-coverage is ≤ 0.05 + 0.05, so it is a two-sided interval at stated joint level ≥ 0.90. Measured joint non-coverage in run H: ≤ 0.0429 [0.0417, 0.0442] at 100,000. Under the cycle-1 symmetric interval the inconsistency could occur; under this rule it cannot.

**Declared class 𝒟_P* (frozen; completely stated; the only class over which any level of T2, L_W, U_W, T1a, NEG, T1b or T1 is stated).** It was declared in the run-H script header before any run of that script.
- **Dependence.** V2's latent copula (date, station, cell) = (0.05, 0.05, 0.10), plus at most one persistent date-level component of latent variance rv ∈ {0.02, 0.05, 0.10}. The component runs on calendar days, paused days included, and is shared by every trade of the date. Its shape is one of:
  - (i) stationary Gaussian AR(1), φ ∈ {0.5, 0.7, 0.8, 0.9};
  - (ii) two-state ±1 Markov regime with autocorrelation φ^k, φ ∈ {0.8, 0.9} (non-Gaussian; same second moments as (i));
  - (iii) trailing L-date mean of iid date shocks, L ∈ {15, 30}. **L = 30 is the literal error of the 30-date trailing-mean bias correction that §9 names, so that mechanism is inside 𝒟_P*;**
  - (iv) two hemisphere AR(1) regimes (φ 0.9);
  - (v) station-specific AR(1) drifts (φ 0.9);
  - or none (the 5-date-block model).
  Latent thresholds are exact for every shape (P(y = 1) = p).
- **Calendar.** D ∈ {120, 90, 60} counted dates (60 = the IF1 floor of a truncated window) plus P ∈ {0, 30} paused calendar dates. 30 is the DATA_FAILURE limit of 11.3. Pauses sit at uniformly random interior positions or as one contiguous run.
- **Geometry.** 14 OP dates; 48 stations with gamma(2) activity; Poisson(m) trades per counted date (cap 96), m ∈ {17, 35}; thin (C ~ U(5, 25)) or full (C = 50) fills.
- **Prices.** OP and window share the same law:
  - c ~ U(0.35, 0.80);
  - favourite-heavy CORE c ~ U(0.70, 0.90). R* cannot buy above 0.90 (5.2), and this is the left-skewed case of 8.4;
  - a 50/50 mix of the two;
  - log-uniform CORE [0.04, 0.90] and U(0.04, 0.35). Both are NO_GO in every run (reach 0; measured, not assumed);
  - the U(0.35, 0.80) law with a 1% (m 17, thin) or 3% (m 35, full) TAIL share c ~ U(0.02, 0.039).
- **Effect.** p = min(1, c(1 + θ)), θ ∈ {0, 0.05, 0.10}. Information power cells also use −0.12, −0.06 and 0.06.
- **Grid.** Shapes (i)–(iii) × rv × the three GO-feasible CORE price laws × {P 0, 30 random, 30 contiguous} × fills × θ ∈ {0, 0.10} at m = 17 is the full factorial (900 cells), because every run-G and Astra worst cell lies at m = 17. The other dimensions are run on the worst-shape slices (fav35 160 cells, geo 72, astra 12, power 36, t1b 12). In total there are 1,183 in-class cells with reach > 0 plus 8 NO_GO cells, all at 20,000 replications.
- **Outside 𝒟_P*** (disclosure only, never claimed): φ ≥ 0.95, a 60-date trailing mean, rv > 0.10, more than one persistent component.
- **No level is claimed between grid points beyond what the grid shows.** A real experiment is not on the grid. The stated class is therefore a declared reference family, broad enough to contain every mechanism the spec names, and is not a proof about every dependence law.

**Selection (declared before any run; nothing chosen afterwards).**
- **Family.** The construction above with λ on the grid {1.00, 1.05, …, 2.50}. λ = 1 for L_W is the cycle-1 rule of 8.1b.
- **Criterion.**
  - λ_θ is the smallest grid value with joint L_W miss ≤ 0.040, false REALIZED_WINDOW positive ≤ 0.040 and U_W miss ≤ 0.040 in every 𝒟_P* cell at 20,000 replications.
  - λ_κ is the smallest grid value with joint T1a and NEG false rejection ≤ 0.020 in every cell.
  - Confirmation: the three worst cells per surface are re-run at 100,000 fresh replications, and their 95% Wilson upper bounds must be ≤ 0.050 (L_W, U_W) or ≤ 0.025 (T1a, NEG). If a confirmation failed, λ would move up the grid, never down.
  - The targets 0.040 / 0.020 are 80% of the nominal levels. That margin is deliberate: Astra showed that a thin margin on one grid (0.3 pp) was the symptom of overfitting.
- **Result.** λ_θ = 1.70 and λ_κ = 1.60. Every confirmation passed on the first pass (below).
- **Pilot.** The only pre-run use of the engine was one 4,000-replication pilot of the Astra cells, to check that the engine reproduces Astra's numbers (it does). The class, family and criterion were not changed after it.

**Level (what holds; run H).** Each error below is the repeated-experiment joint rate with reach (reach = GO ∧ INFO_SUFFICIENT), worst over the cells shown, at the frozen λ_θ = 1.70 / λ_κ = 1.60, with 20,000 replications per cell.

| Dependence in 𝒟_P* | L_W miss | False positive (size) | U_W miss | T1a false | NEG false | cycle-1 L_W miss (λ = 1) | 5-date T1a / NEG / U_W (pre-repair) |
|---|---|---|---|---|---|---|---|
| none (5-date-block model) | 0.0026 | 0.0021 | 0.0002 | 0.0004 | 0.0002 | 0.0360 | 0.038 / 0.027 / 0.029 |
| AR(1) φ 0.5 / 0.7 / 0.8 | 0.0050 / 0.0081 / 0.0121 | ≤ 0.0107 | ≤ 0.0009 | ≤ 0.0043 | ≤ 0.0012 | 0.046 / 0.054 / 0.066 | up to 0.082 / 0.046 / 0.047 |
| AR(1) φ 0.9 | 0.0268 | 0.0220 | 0.0028 | 0.0115 | 0.0031 | 0.0954 | 0.158 / 0.079 / 0.081 |
| two-state φ 0.8 / 0.9 | 0.0115 / 0.0279 | ≤ 0.0255 | ≤ 0.0089 | ≤ 0.0163 | ≤ 0.0106 | 0.057 / 0.086 | up to 0.119 / 0.094 / 0.105 |
| trailing mean L = 15 | 0.0211 | 0.0155 | 0.0013 | 0.0080 | 0.0014 | 0.0811 | 0.110 / 0.059 / 0.062 |
| trailing mean L = 30 (§9 mechanism) | **0.0395** | **0.0353** | 0.0044 | **0.0198** | 0.0057 | 0.1176 | 0.175 / 0.103 / 0.108 |
| hemisphere / station AR φ 0.9 | 0.0100 / 0.0008 | ≤ 0.0094 | ≤ 0.0007 | ≤ 0.0032 | ≤ 0.0008 | 0.061 / 0.022 | up to 0.107 / 0.063 / 0.064 |
| **all of 𝒟_P*** | **0.0395** | **0.0353** | **0.0089** | **0.0198** | **0.0106** | 0.1176 | 0.175 / 0.103 / 0.108 |

By the other dimensions (worst L_W miss):
- prices: favourite 0.0395, mix 0.0241, U(0.35, 0.80) 0.0194, TAIL mixes ≤ 0.0108;
- calendars: P 0 0.0350, 30 random 0.0359, 30 contiguous 0.0395;
- D 90 0.0168, D 60 0.0011;
- m 35 ≤ 0.0344.

**Confirmation at 100,000 fresh replications (streams 1–5; 95% Wilson).**

| Surface | Worst cell | Joint rate | Bound required | Pass |
|---|---|---|---|---|
| L_W miss | trailing mean 30, rv 0.10, favourite prices, 30 contiguous paused dates, m 17 full, θ 0.10 | 0.0415 [0.0403, 0.0427] | ≤ 0.050 | yes |
| L_W miss | same, thin fills | 0.0400 [0.0388, 0.0413] | ≤ 0.050 | yes |
| false positive (size) | same geometry, θ_W = 0, full / thin | 0.0336 [0.0325, 0.0347] / 0.0336 [0.0325, 0.0347] | ≤ 0.050 | yes |
| U_W miss | two-state φ 0.9, rv 0.10, 30 contiguous paused, m 17 full, θ 0 | 0.0085 [0.0079, 0.0091] | ≤ 0.050 | yes |
| T1a false rejection | trailing mean 30, rv 0.10, favourite, 30 contiguous paused, m 17 thin, κ_core = 0 | 0.0193 [0.0185, 0.0202] | ≤ 0.025 | yes |
| NEG false rejection | two-state φ 0.9, rv 0.10, 30 contiguous paused, m 17 full, κ_core = 0 | 0.0100 [0.0095, 0.0107] | ≤ 0.025 | yes |
| headline [L_W, U_W] joint non-coverage | trailing mean 30 cell above | 0.0429 [0.0417, 0.0442] | ≤ 0.10 (stated level ≥ 0.90) | yes |

**Astra @ac777a87 counterexample cells under this rule** (cycle-1 rule or pre-repair 5-date test in brackets; 100,000 replications at the first three, 20,000 otherwise):
- favourite CORE, φ 0.9, rv 0.05, thin:
  - L_W miss 0.0114 [0.0108, 0.0121] (0.0639);
  - false positive 0.0100 [0.0094, 0.0106] (0.0595);
- 30 random paused dates: 0.0069 [0.0064, 0.0074] (0.0534);
- favourite rv 0.10: miss 0.0209, size 0.0168 (0.0845 / 0.0724);
- two-state: 0.0107 (0.0547);
- literal §9 trailing mean 30, rv 0.05: miss 0.0114, size 0.0097 (0.0610 / 0.0556);
- φ 0.95 (outside 𝒟_P*): 0.0303 (0.1047);
- M2 cells, φ 0.9, rv 0.05 / 0.10, κ_core = 0:
  - T1a 0.0018 / 0.0037 (0.0881 / 0.0606);
  - NEG 0.0009 / 0.0019 (0.0707 / 0.0358);
  - U_W miss 0.0008 / 0.0014 (0.0698 / 0.0360).

Every pre-repair value reproduces Astra's within Monte-Carlo error.

**Stated levels (D4-C3-M2).** Over 𝒟_P*, as repeated-experiment rates jointly with reach:
- `P(reach ∧ L_W > θ_W) ≤ 0.05`, and the positive REALIZED_WINDOW claim has size ≤ 0.05;
- `P(reach ∧ U_W < θ_W) ≤ 0.05`;
- T1a false rejection ≤ 0.025 and NEG false rejection ≤ 0.025;
- T1b ≤ 0.025 (below), so T1 FWER ≤ 0.05;
- headline `[L_W, U_W]` joint coverage ≥ 0.90.

Measured worst values: 0.0415 / 0.0353 / 0.0089 / 0.0198 / 0.0106; T1b 0.0077; T1 0.0089; headline non-coverage 0.0429. No level is claimed outside 𝒟_P*.

**Conditional on reach (disclosed; not the stated level).** IF5 screens high-dispersion windows, not slow drifts, so rates given reach are larger. Over cells with reach ≥ 0.10 the worst values are:
- L_W miss 0.182 (two-state φ 0.9, rv 0.10, favourite prices, m 35 full, reach 0.11; 0.120 at m 17 with reach 0.16);
- size 0.112;
- U_W miss 0.054;
- T1a 0.069;
- NEG 0.065.
In the worst joint cells (reach 0.59–0.81) the conditional L_W miss is 0.044–0.057. A printed label is therefore not "wrong with probability ≤ 0.05 given that it was printed".

**T1b (PINM) under persistence (proof gap closed by measurement; T1b unchanged).** The test is spec 8.3 with the declared copula (0.10, 0.10, 0.10) and B = 2,000 draws per replication. A finite-B p-value is valid under the declared model for any B; the spec's B is 20,000. Designs: 1% TAIL share at m 17 thin (≈ 20 TAIL trades) and 3% at m 35 full (≈ 126). Sharp null p = c on TAIL, κ_core = 0, 20,000 replications.

| Persistence | T1b joint (1% / 3%) | T1 = T1a ∪ T1b, this rule (1% / 3%) | T1 with the pre-repair 5-date T1a (1% / 3%) |
|---|---|---|---|
| none | 0.0076 / 0.0077 | 0.0076 / 0.0079 | 0.0286 / 0.0303 |
| AR φ 0.8, rv 0.05 | 0.0060 / 0.0011 | 0.0066 / 0.0012 | 0.0452 / 0.0098 |
| AR φ 0.9, rv 0.05 / 0.10 | 0.0063 / 0.0033 (1%); 0.0013 / 0.0001 (3%) | ≤ 0.0076 | up to 0.0662 |
| two-state φ 0.9, rv 0.10 | 0.0018 / 0.0003 | 0.0089 / 0.0037 | 0.0460 / 0.0046 |
| trailing mean 30, rv 0.10 | 0.0036 / 0.0003 | 0.0081 / 0.0013 | 0.0713 / 0.0054 |

T1b is conservative throughout 𝒟_P* (≤ 0.0077 against 0.025). The declared copula over-states the latent dependence of rare wins, so persistence does not inflate it. The T1 FWER is ≤ 0.0089 under this rule; before the repair it reached 0.0713.

**Failed and published candidates (same replications, worst over 𝒟_P*).**

| Candidate | Worst L_W miss | Worst size | Status |
|---|---|---|---|
| R3 engine (5-date blocks) | 0.2439 | — | retired |
| cycle-1 rule (8.1b; λ = 1) | 0.1176 [0.1132, 0.1221] | 0.1035 | fails |
| blocks {5, 10, 20, 30, 40}, λ = 1 | 0.0968 [0.0928, 0.1010] | 0.0854 | fails |
| reference quantile 0.975 for L_W, λ = 1 | 0.0742 [0.0706, 0.0779] | 0.0658 | fails |
| family members λ_θ = 1.00 … 1.65 | > 0.040 in at least one cell (1.65: trailing mean 30, favourite) | — | fail the declared criterion |
| **adopted λ_θ = 1.70** | 0.0395 (100,000: 0.0415 [0.0403, 0.0427]) | 0.0353 | criterion met |
| κ family λ_κ = 1.00 … 1.55 | T1a > 0.020 in at least one cell | — | fail |
| **adopted λ_κ = 1.60** | T1a 0.0198 (100,000: 0.0193 [0.0185, 0.0202]); NEG 0.0106 | — | criterion met |
| 5-date T1a / NEG / U_W (pre-repair) | 0.1752 / 0.1025 / 0.1077 | — | retired |

**What drives λ (disclosure; not a level claim and not a selection).** Run on the same replications, the smallest λ meeting the same criterion within each sub-family is:

| Sub-family | λ_θ | λ_κ |
|---|---|---|
| none | 1.00 | 1.00 |
| AR(1) φ ≤ 0.8 | ≤ 1.25 | ≤ 1.15 |
| AR(1) φ 0.9 | 1.50 | 1.40 |
| two-state φ 0.9 | 1.50 | 1.50 |
| trailing mean 15 / 30 | 1.35 / 1.70 | 1.30 / 1.60 |
| run-G-like (U(0.35, 0.80) prices, no pauses, AR only) | 1.10 | 1.00 |

The 30-date trailing-mean mechanism at rv 0.10 with favourite prices sets both constants. A narrower class would be cheaper, but choosing one now, after seeing these numbers, would be selection on results. V2 does not do it. Any narrower class needs its own outcome-blind declaration and audit (governance / V3).

**Power and feasibility cost (stated, not retuned; power table §4.9).** Joint with reach; no persistence; 20,000 replications.

| Quantity | R3 engine | cycle-1 (8.1b) | **D4-C3-M2** |
|---|---|---|---|
| P(T2) at θ_PCE: m 17 thin / 17 full / 35 thin / 35 full | 0.774 / 0.705 / 0.477 / 0.481 (SUPPORTED) | 0.551 / 0.473 / 0.343 / 0.349 | **0.109 / 0.084 / 0.067 / 0.070** |
| SUPPORTED at θ = 0.10, m 17 thin / full | 0.840 / 0.856 | 0.648 / 0.669 | **0.161 / 0.181** |
| SUPPORTED at θ = 0.15 / 0.20, m 17 thin | 0.984 / 0.995 | 0.948 / 0.994 | **0.596 / 0.922** |
| 80%-power effect for T2 (m 17; linear interpolation) | ≈ 0.09–0.10 | ≈ 0.11–0.12 | **≈ 0.18** (m 35: reach-limited, 0.75–0.76 at θ = 0.20) |
| T1a power at κ_core ≈ +0.035 / +0.058 / +0.115 (θ 0.06 / 0.10 / 0.20, m 17 thin) | 0.426 / 0.836 / 0.995 (5-date) | — | **0.007 / 0.079 / 0.888** |
| T1a MDE80 per share (m 17) | ≈ 0.035 | — | **≈ 0.11** |
| NEG power at κ_core ≈ −0.069 / −0.035 (θ −0.12 / −0.06, m 17) | 0.889 / 0.386 (5-date) | — | **0.116 / 0.004** (m 35: 0.166 / 0.008) |
| REALIZED_WINDOW_LOSS_CONFIRMED at θ_W = −0.12 (m 17 thin) | 0.505 (λ = 1, multi-block) | — | **0.053** |
| GO / NO_GO and INFO_SUFFICIENT (reach) | — | — | **unchanged numerically** (no gate or threshold changed) |

**Feasibility consequence (stated plainly).**
- **The repair buys validity over 𝒟_P* at the cost of most of V2's power.**
- **θ_PCE.** The frozen θ_PCE / GO no longer imply useful T2 power: P(T2) at θ_PCE is ≈ 0.07–0.11.
- **NEG and T1a.** NEG, "the only real negative-result instrument" (10.3), has power ≈ 0.12 against a public-bot-like −0.07 per share. T1a needs κ_core ≈ 0.11 per share for 80% power.
- **Not retuned.** No threshold, gate or constant is retuned to recover power. GO's PCE_CEILING and SE_KAPPA_CEILING keep their frozen meanings, which are design reference values (nominal, normal approximation, 5-date-block SE) and no longer the power of the tests actually run.
- **Whether a valid but this weakly powered V2 is worth running** is an EXPERIMENT_FEASIBILITY question for Astra and governance, not an Architect decision. It is flagged as such (27).

### 8.1d Enlarged price class and recalibrated λ (D4-C3-P1, M3 option (i), after Astra D4-C3-M2 recheck @8874dc54; authoritative for λ_θ, λ_κ, the price laws of 𝒟_P* and every level)

**Defect repaired (M3).** The cycle-2 class text said "CORE prices to 0.90", and the printed level text of 17.3 and the 8.5c error statement repeated it, while run H calibrated only U(0.35, 0.80), U(0.70, 0.90) and their mix. R* buys a NO leg at ask `a` only when `1 − q − a − f(a) ≥ 0.10`, so asks of 0.80–0.89 are exactly its high-confidence legs: the left-skewed case of 8.4. Astra @8874dc54: c ~ U(0.85, 0.90), 30-date trailing mean, rv 0.10, m 17, 120 counted dates: L_W miss 0.0587 [0.0573, 0.0602] (100,000) with 30 contiguous paused dates, 0.0523 without pauses, and T1a 0.0262 [0.0253, 0.0273]. Reproduced here at the cycle-2 constants (table below). The repair is option (i): recalibrate over an enlarged, completely stated class. No stated level is lowered.

**Class 𝒟_P* after D4-C3-P1.** Everything under "Declared class" in 8.1c stands (dependence, calendar, geometry, effect, the outside list) except the CORE price laws, which are now exactly these (OP and window share the law):
- the 8.1c laws: c ~ U(0.35, 0.80); favourite c ~ U(0.70, 0.90); the 50/50 mix; U(0.35, 0.80) with a 1% / 3% TAIL share; log-uniform [0.04, 0.90] and U(0.04, 0.35) (NO_GO under the cycle-2 gate in every run, reach 0);
- **new near-cap laws:** c ~ U(0.80, 0.90); c ~ U(0.85, 0.90); a **point mass at c = 0.89** (the extremal concentration: R* cannot buy at or above 0.90, so asks lie below 0.90 by the fee and by q); and the two-point mixtures with a 10 / 50 / 90% point mass at 0.89, the rest U(0.35, 0.80).

The laws are **enumerated**. "CORE prices to 0.90" is not printed as an unqualified class anywhere in V2 (17.3, 8.5c and the manifest carry the enumerated wording). That the point mass at 0.89 and U(0.85, 0.90) are the most adverse of the near-cap laws is an empirical observation, not a theorem: in-between laws (point masses at 0.80 and 0.85, U(0.88, 0.90), U(0.60, 0.90)) and a point mass at 0.899 were probed at the adopted constants and stayed inside the stated level (below), but no level is claimed for a price law that is not enumerated.

**Cells.** Run J (`WEATHER_FORWARD_V2_D4_C3_P1_GATE_SIM_2026-10-02.py`, seeds `SeedSequence([20261102, plan, cell, stream])`) ran the 8.1c class grid on the three new single laws (25 dependence × 3 laws × {no pauses, 30 random, 30 contiguous} × {thin, full} × θ {0, 0.10} at m 17 = 900 cells), the two-point mixtures on the five worst dependence shapes (60), the m 35 / θ 0.05 slice (240), D 60 / 90 and hemisphere / station slices (72), Astra's M3 cells verbatim with neighbours (10), and six addendum cells for D 60 + 30 contiguous paused dates (in class). The old cells (1,183 reached cells of run H) are not re-run: L_W, U_W, T1a and NEG are monotone in λ, so each remains inside its criterion at any λ ≥ (1.70, 1.60), and their levels at the adopted λ are read from the committed run-H raw output (λ grid ≤ 2.50). The GO check used for reach in these cells is the cycle-2 GO, a **superset** of the cycle-3 GO (10.3), so every level below, counted jointly with that reach, upper-bounds the level under the stricter cycle-3 GO.

**Selection (declared before any run: `ARCHITECT_PROGRESS_CYCLE3.md`, commit 03640425, which precedes the run output commit 7d7d75ae; mechanical).**
- λ_θ = the smallest value on the grid {1.00, 1.05, …, 3.50} that is ≥ 1.70 such that in every new-law cell at 20,000 replications P(reach ∧ L_W > θ_W) ≤ 0.040, P(reach ∧ false REALIZED_WINDOW positive) ≤ 0.040 and P(reach ∧ U_W < θ_W) ≤ 0.040.
- λ_κ = the smallest value ≥ 1.60 with T1a and NEG false rejection ≤ 0.020 in every such cell.
- Confirmation: the three worst new-law cells per surface plus every Astra-M3 cell at 100,000 fresh replications (streams 1–5), Wilson 95% upper bounds ≤ 0.050 (L_W, size, U_W) / ≤ 0.025 (T1a, NEG); a failure would move λ up one grid step, never down. No grid value ≤ 3.50 meeting the criterion would have been a FUNDAMENTAL_BLOCKER for option (i).
- The 0.040 / 0.020 targets are 80% of the nominal levels, the same deliberate margin as in 8.1c.
- Disclosure: the Architect had seen Astra's M3 numbers and its "effective multiplier about 5" before declaring; the rules are mechanical functions of the raw output. A preview of the first 272 cells was read to test the summariser while the rest ran; no plan, rule or cell was changed.

**Result: λ_θ = 2.15 and λ_κ = 1.80** (the cycle-2 values 1.70 / 1.60 fail the criterion on the enlarged class). Every confirmation passed on the first pass.

*Published failed candidates (worst over the new-law cells, 20,000 replications):*

| Candidate | Worst L_W miss | Worst size | Worst T1a | Status |
|---|---|---|---|---|
| cycle-2 λ_θ 1.70 / λ_κ 1.60 | 0.0683 (point mass 0.89, trailing mean 30, rv 0.10, m 35, no pauses, θ 0.10); 100,000: 0.0568 [0.0554, 0.0583] at U(0.85, 0.90), 0.0611 [0.0596, 0.0626] at the point mass (m 17) | 0.0469 (100,000: 0.0451 [0.0438, 0.0464]) | 0.0289 (100,000: 0.0269 [0.0259, 0.0279]) | fails the criterion; the stated level 0.05 / 0.025 is exceeded |
| λ_θ 1.75 / 1.80 / 1.90 / 2.00 / 2.05 / 2.10 | 0.0648 / 0.0608 / 0.0537 / 0.0474 / 0.0442 / 0.0419 | 0.0444 / 0.0417 / 0.0361 / 0.0316 / 0.0290 / 0.0274 | — | fail the declared 0.040 target |
| λ_κ 1.65 / 1.70 / 1.75 | — | — | 0.0265 / 0.0243 / 0.0220 | fail the declared 0.020 target |
| **adopted λ_θ = 2.15 / λ_κ = 1.80** | 0.0394 (100,000: 0.0397 [0.0385, 0.0409]) | 0.0253 (100,000: 0.0240 [0.0231, 0.0250]) | 0.0199 (100,000: 0.0190 [0.0182, 0.0199]) | criterion met |

**Level (what holds; run J + run H).** Each error is the repeated-experiment joint rate with reach, worst over the cells of the row, at λ_θ = 2.15 / λ_κ = 1.80, 20,000 replications per cell (old cells from run H, new-law cells from run J):

| Dependence in 𝒟_P* | L_W miss | size | U_W miss | T1a false | NEG false |
|---|---|---|---|---|---|
| none (5-date-block model) | 0.0010 | 0.0005 | 0.0000 | 0.0003 | 0.0001 |
| AR(1) φ 0.5 / 0.7 / 0.8 | 0.0028 / 0.0053 / 0.0084 | ≤ 0.0053 | ≤ 0.0001 | ≤ 0.0038 | ≤ 0.0006 |
| AR(1) φ 0.9 | 0.0226 | 0.0143 | 0.0008 | 0.0112 | 0.0019 |
| two-state φ 0.8 / 0.9 | 0.0067 / 0.0199 | ≤ 0.0180 | ≤ 0.0034 | ≤ 0.0139 | ≤ 0.0073 |
| trailing mean L = 15 | 0.0144 | 0.0097 | 0.0004 | 0.0073 | 0.0008 |
| trailing mean L = 30 (§9 mechanism) | **0.0394** | **0.0253** | 0.0014 | **0.0199** | 0.0032 |
| hemisphere / station AR φ 0.9 | 0.0062 / 0.0008 | ≤ 0.0050 | ≤ 0.0001 | ≤ 0.0032 | ≤ 0.0004 |
| **all of 𝒟_P*** | **0.0394** | **0.0253** | **0.0034** | **0.0199** | **0.0073** |

By the other dimensions (worst L_W miss / size):
- CORE price laws: point mass 0.89 0.0394 / 0.0253; U(0.85, 0.90) 0.0340 / 0.0231; U(0.80, 0.90) 0.0281 / 0.0200; U(0.70, 0.90) 0.0208 / 0.0173; mixes with the point mass ≤ 0.0167; 50/50 mix 0.0120; U(0.35, 0.80) 0.0107; TAIL mixes ≤ 0.0021;
- calendars: no pauses 0.0394, 30 random 0.0389, 30 contiguous 0.0358 (size 0.0253);
- D 90 0.0096, D 60 0.0180 (two-state, 30 contiguous paused);
- m 17 0.0358, m 35 0.0394.

**Confirmation at 100,000 fresh replications (streams 1–5; Wilson 95%; λ_θ 2.15 / λ_κ 1.80).**

| Surface | Worst cell | Joint rate | Required | Pass |
|---|---|---|---|---|
| L_W miss | point mass 0.89, trailing mean 30, rv 0.10, no pauses, m 35 full, θ 0.10 | 0.0397 [0.0385, 0.0409] | ≤ 0.050 | yes |
| L_W miss | same, thin / 30 random paused full | 0.0384 [0.0372, 0.0396] / 0.0374 [0.0362, 0.0386] | ≤ 0.050 | yes |
| size | point mass 0.89, trailing 30, rv 0.10, 30 contiguous paused, m 17 full / thin, θ 0 | 0.0240 [0.0231, 0.0250] / 0.0231 [0.0222, 0.0240] | ≤ 0.050 | yes |
| U_W miss | 10% point-mass mix, two-state φ 0.9, rv 0.10, 30 contiguous paused, thin, θ 0 / 0.10 | 0.0027 [0.0024, 0.0031] / 0.0021 [0.0019, 0.0024] | ≤ 0.050 | yes |
| T1a false | point mass 0.89, trailing 30, rv 0.10, 30 contiguous paused, m 17 full / thin, θ 0 | 0.0190 [0.0182, 0.0199] / 0.0186 [0.0178, 0.0194] | ≤ 0.025 | yes |
| NEG false | 10% point-mass mix, two-state φ 0.9, rv 0.10, 30 contiguous paused, thin, θ 0 | 0.0062 [0.0057, 0.0067] | ≤ 0.025 | yes |
| headline [L_W, U_W] joint non-coverage | the L_W cell above | 0.0397 [0.0385, 0.0409] | ≤ 0.10 (stated level ≥ 0.90) | yes |

The cycle-2 worst cells (run-H confirmations) at the adopted λ: L_W miss 0.0208, T1a 0.0129, NEG 0.0067, U_W 0.0034 (derived from the committed run-H arrays).

**Astra @8874dc54 M3 cells under both constants (100,000 replications; trailing mean 30, rv 0.10, m 17; Astra's own number in brackets).**

| Cell | Cycle-2 λ (1.70 / 1.60) | **Adopted (2.15 / 1.80)** |
|---|---|---|
| U(0.85, 0.90), full, θ 0.10, 30 contiguous paused: L_W miss | 0.0568 [0.0554, 0.0583] (Astra 0.0587) | **0.0312 [0.0302, 0.0323]** |
| same, thin | 0.0573 [0.0558, 0.0587] (0.0557) | **0.0313 [0.0302, 0.0324]** |
| same, full, no pauses | 0.0513 [0.0499, 0.0527] (0.0523) | **0.0278 [0.0268, 0.0289]** |
| same, 30 random paused | 0.0514 [0.0500, 0.0528] (0.0522) | **0.0273 [0.0263, 0.0283]** |
| U(0.80, 0.90), thin, θ 0.10, 30 contiguous paused | 0.0499 [0.0486, 0.0513] (0.0506) | **0.0266 [0.0256, 0.0276]** |
| U(0.85, 0.90), thin, θ 0, 30 contiguous paused: T1a / size | 0.0244 [0.0235, 0.0254] / 0.0418 (Astra T1a 0.0262) | **0.0167 [0.0159, 0.0175] / 0.0209** |
| point mass 0.89, thin, θ 0.10, 30 contiguous paused | 0.0611 [0.0596, 0.0626] | **0.0343 [0.0331, 0.0354]** |
| point mass 0.89, thin, θ 0, 30 contiguous paused: T1a / size | 0.0269 [0.0259, 0.0279] / 0.0451 | **0.0188 [0.0180, 0.0197] / 0.0234** |

**Price-law sensitivity at the adopted constants (disclosure; m3_probe, 20,000 per cell, trailing mean 30 / AR 0.9 / two-state 0.9 at rv 0.10, 30 contiguous paused, thin, θ {0, 0.10}, m 17).** In-between laws: point mass 0.85 ≤ 0.0291, point mass 0.80 ≤ 0.0230, U(0.88, 0.90) ≤ 0.0337, U(0.60, 0.90) ≤ 0.0158 (L_W miss); T1a ≤ 0.0200 (U(0.88, 0.90)). Outside the enumerated class: a point mass at 0.899, m 17: L_W miss ≤ 0.0372, T1a ≤ 0.0188; in the m 35 geometry that binds the point mass 0.89 (no pauses, trailing 30, rv 0.10, θ 0.10, 100,000): point mass 0.899 0.0397 [0.0385, 0.0409] thin / 0.0411 [0.0399, 0.0423] full (above the 0.040 target, inside the stated 0.05), U(0.88, 0.90) 0.0376 / 0.0380. These are disclosures, not claims for the laws involved.

**Conditional on reach (disclosed; not the stated level; supersedes the 8.1c figures).** Over the enumerated cells with reach ≥ 0.10 the worst values are: L_W miss 0.148 (point mass 0.89, two-state φ 0.9, rv 0.10, m 35 full, reach 0.102), size 0.148, U_W miss 0.021, T1a 0.121, NEG 0.044. **These are grid figures, not a maximum over 𝒟_P*:** Astra's off-grid in-class cell (D 60, 30 contiguous paused, two-state φ 0.9, rv 0.10) gave 0.203 at the cycle-2 λ; at the adopted λ the same geometry (mid prices, θ 0.10, reach 0.111, thin, m 17; run J addendum) gives 0.086 (0.214 at the cycle-2 λ), favourite prices θ 0 (reach 0.368) 0.041, point mass 0.89 θ 0 (reach 0.907) 0.020. A printed label is therefore not "wrong with probability ≤ 0.05 given that it was printed", and no figure in this paragraph bounds the conditional rate in every in-class cell.

**T1b and T1.** T1b is unchanged by λ (tail only): ≤ 0.0077. T1 = T1a ∪ T1b at λ_κ = 1.80 over the run-H TAIL designs: ≤ 0.0078 (the T1b maximum; T1a adds nothing at the maximum).

**Outside 𝒟_P* (disclosure only; never claimed):** φ ≥ 0.95, a 60-date trailing mean, rv > 0.10, more than one persistent component, price laws that are not enumerated (including a point mass at 0.899, measured above).

**What the constants cost.** λ_θ rises from 1.70 to 2.15 (the T2, U_W bound is 26% wider than in cycle 2) and λ_κ from 1.60 to 1.80. T2 and T1a are therefore harder to pass than in cycle 2; NEG's power falls with the wider bound. The cost is stated in 10.4 and the power table §4.10; it is a consequence of validity over the enlarged class, not a retuning.

### 8.2 PINM (price-implied null Monte Carlo): primary for the tail count, auxiliary elsewhere

```text
SHARP NULL           p_j = c_j for every trade in the tested set (every chosen leg fairly priced after all costs)
MARGINAL             y*_j = 1{ U_j < p_j }
DEPENDENCE (ASSUMED) latent Gaussian copula  Z_j = √ρ_d A_date(j) + √ρ_s S_station(j) + √ρ_c K_cell(j) + √(1−ρ_d−ρ_s−ρ_c) E_j,
                     U_j = Φ(Z_j),  cell = (local target date, ICAO)  [pairs HIGHEST and LOWEST of the same station-date]
DECLARED VALUES      ρ_d = 0.10, ρ_s = 0.10, ρ_c = 0.10          (sensitivity rows at ×0.5 and ×2, reported, non-gating)
DRAWS                B = 20,000, generated in 20 sequential chunks of 1,000
RNG                  NumPy Generator(PCG64(SeedSequence([20260929, 1]))); per draw, standard normals in this order:
                     dates (ascending), stations (ascending ICAO), cells (ascending date, ICAO), trades (canonical order:
                     T_entry, then event_id, then decision_id)
p-VALUE              (1 + #{stat* ≥ stat_obs}) / (B + 1)   (upper tail; lower tail symmetric)
```

Assumption status: the latent-correlation values are **ASSUMED**, not estimated; no outcome data is used to set them. They are twice Fable's advisory 0.05 and above Astra's observed-scale range once mapped from the latent scale. Positive latent association on win indicators is the variance-maximising (conservative) declaration for one-sided sum statistics relative to a mixed-sign true dependence of equal magnitude. **PINM is therefore not claimed exact; it is exact only under the declared copula.** It is used as a gating engine only where its residual dependence risk is small (rare tail wins: observed-scale correlation of rare events under latent 0.10 is ≈ 0.01, so the design effect of `W_tail` stays near 1).

Uses: (i) **T1b** (statistic `W_tail`, TAIL trades, upper tail) — gating, and the only gating use; (ii) θ̂ and κ̂_core under the sharp null — **reported only** (`PINM_THETA_P`, `PINM_KAPPA_P`), with the rule that a disagreement with the CR engine is printed as `ENGINE_DISAGREEMENT` and changes no label. PINM no longer enters any upper bound (D4 repair R1, section 8.5).

Why PINM does not gate θ or κ_core (SIMULATED, power table §4): with a declared rather than oracle dependence, PINM is either anti-conservative (declared below truth: Fable measured 0.13–0.21 size) or power-destroying (declared above truth: T2 power 0.73–0.755 vs 0.855–0.91 for CR at core-only θ = 0.10, and 0.275–0.28 vs 0.52–0.54 with 5% tail legs; runs A/B); the empirical CR engine adapts to the actual dependence and is conservative for positive θ claims when tail legs are present (null rejection 0.000–0.020 at nominal 0.05).

### 8.3 T1b exact tail test

`T1b` rejects iff `PINM_W_p ≤ 0.025`, where `PINM_W_p = (1 + #{W*_tail ≥ W_tail}) / (B + 1)` under the sharp null on TAIL trades with the declared copula. If the TAIL stratum is empty, T1b does not reject. Reported alongside (non-gating): Poisson-binomial p-value under independence; block-collapsed count p-value (number of 5-date blocks containing ≥ 1 tail win against its exact Poisson-binomial null `1 − Π(1 − c_j)` per block), and `λ̂_tail = W_tail / Λ_tail`.

Under persistence (D4-C3-M2 proof-gap closure; T1b unchanged): over the 𝒟_P* TAIL designs T1b's joint rejection rate under the sharp null is ≤ 0.0077, and T1 = T1a ∪ T1b is ≤ 0.0089 (run H, 8.1c).

### 8.4 NEG (core adverse)

`NEG` holds iff `κ̂_core + λ_κ · max_{b∈{5,10,20,30}} t_{df_b,0.975} · SE_2w(b; κ̂_core) < 0` (one-sided 0.025; λ_κ = 1.80; D4-C3-P1, 8.1d; cycle 2: 1.60). Over 𝒟_P*, including near-cap favourite CORE prices, its joint false-rejection rate is ≤ 0.0073 (20,000; 100,000-replication worst 0.0062 [0.0057, 0.0067]). Its power against κ = −0.07 per share, given INFO_SUFFICIENT, is 0.06 (mid prices, m = 17) to 0.25 (point mass 0.89, m = 17), 0.16–0.52 at m = 35 and 0.33–0.75 at m = 55; jointly with INFO_SUFFICIENT at most 0.44 over every declared law and throughput up to 96 trades per date (power table §4.10); against 0.89 for the pre-repair 5-date test (§4.9). **NEG is therefore not a usable negative-result instrument at 120 dates (10.3, 10.4).** *History (V2, 5-date-block form `κ̂_core + t_{df,0.975} · SE_CR(κ̂_core) < 0`; its level was refuted under persistence by Astra M2 @ac777a87: 0.0707, and run H: up to 0.1025):* Reason (SIMULATED, 3,200 null replications): the per-share residual `y − c` of favourite-bucket NO legs is negatively skewed, so the CR engine's **lower** tail over-rejects (0.061–0.068 at nominal 0.05 under clustered dependence); at 0.025 its size is 0.022–0.028, inside the 0.05 guarantee. Power against a public-bot-like κ ≈ −0.07 stays ≈ 0.98 at 0.025 (SE ≈ 0.017).

### 8.5 Realised-window upper bound U_W (D4 repair R1; re-scoped to θ_W by D4 repair R2)

**Scope after D4 repair R2 (Astra D4 recheck C2 @3d18085).** Everything in this section is a statement about the realised-window estimand `θ_W` (5.1). The proof conditions on the realised trade set, so the bound covers the tail legs that occurred and nothing else. It is **not** a bound on the prospective `θ_P`. After R2 it drives no `SCIENTIFIC_STATE` label and no rejection: its only use is the report field `REALIZED_WINDOW_BOUND` (17.3). Prospective exclusion is treated in 8.5b.

History (R1, kept). A pooled empirical upper bound cannot represent tail wins that did not occur, and it under-covers: SIMULATED coverage 0.79–0.91 for a nominal 0.95 bound when sub-4¢ legs are present. The V2@94b5934 structured bound replaced the tail part with the larger of two ASSUMED tail models (TPM, SHR). Astra showed, and run D reproduced, that the admissible tail outcome class is not restricted to those models (C1). **The TPM / SHR tail models are retired from every role.**

Admissible tail outcome class for θ_W (frozen): every vector of true win probabilities `p_j ∈ [0, 1]` on the realised TAIL trades, under any dependence. Nothing the experiment observes can shrink this class without an assumption. The only upper bound on the realised tail's contribution that is valid over the whole class is therefore its identified-set supremum, "every realised TAIL leg wins":

```text
U_W     = w_core · U_core + M_tail                                  (one-sided upper bound for θ_W; level 95% joint with reach over 𝒟_P*, 8.1c)
U_core  = θ̂_core + λ_θ · max_{b∈{5,10,20,30}} t_{df_b, 0.975} · SE_2w(b; θ̂_core)
                                                                    (D4-C3-M2, 8.1c / D4-C3-P1, 8.1d: calibrated multi-block two-way CR, λ_θ = 2.15;
                                                                     core level 0.975 keeps the lower-tail skew allowance of 8.4;
                                                                     was θ̂_core + t_{df,0.975} · SE_CR(θ̂_core), 5-date blocks, refuted
                                                                     under persistence by Astra M2: miss 0.0755; run H up to 0.1077)
M_tail  = Σ_{TAIL} (n_j − C_j) / Σ_{all} C_j  = w_tail · (Σ_TAIL n_j / Σ_TAIL C_j − 1)
          (TAIL_MAX_CONTRIBUTION: θ_W-contribution of the realised TAIL stratum if every realised TAIL leg pays 1;
           0 if TAIL is empty; computed from fills only, known at T_entry, deterministic)
```

Coverage proof, for θ_W only. Condition on the realised trade set: fills, `n_j`, `C_j` and strata are fixed at T_entry, before any outcome. Then `θ_W = w_core θ_core,W + w_tail θ_tail,W` with `θ_tail,W = Σ_TAIL n_j p_j / Σ_TAIL C_j − 1 ≤ Σ_TAIL n_j / Σ_TAIL C_j − 1` for every `p ∈ [0, 1]^TAIL` and every dependence structure. Hence `{θ_core,W ≤ U_core} ⊆ {θ_W ≤ U_W}` and `P(θ_W ≤ U_W) ≥ P(θ_core,W ≤ U_core)`: uncertainty about the outcomes of the realised tail legs costs no coverage. The core coverage itself is the calibrated level of 8.1c / 8.1d (joint U_W miss ≤ 0.0034 over 𝒟_P*).

SIMULATED evidence:
- Run D: coverage 0.9705–0.993 over nine adversarial core geometries.
- Astra D4 recheck §7–§8: zero violations in 240,000 adversarial replications; core coverage 0.946–0.992.
- Run E (power table §4.6): coverage of θ_W 0.9705–1.0 in every prospective scenario, including those where θ_P is falsely excluded by the retired rule.

What the proof does **not** cover is the second stochastic layer: *which* trades appear, i.e. the arrival process of opportunity types (8.5b).

Consequences:
- `U_W < θ_ERT` is attainable only when the realised tail is economically small, because `U_W ≥ M_tail`. A single 0.001 leg at S_ref (M ≈ +0.24 at 4,200 trades) makes every REALIZED_WINDOW exclusion impossible for the run. A few 0.039 legs (≈ +0.006 each) merely widen the bound.
- `EXCLUSION_BLOCKED_BY_TAIL = TRUE` whenever `w_core · U_core < θ_ERT ≤ U_W` (descriptive; changes no label).
- In tail-free runs U_W equals the V2@94b5934 bound exactly (`M_tail = 0`).
- `U_W ≥ θ̂`, because `M_tail ≥ w_tail θ̂_tail` and §8.6 imputes unresolved trades as wins for U_W.
- U_W never drives ECONOMIC_RESULT, never rejects R*, and never states anything about θ_P.

### 8.5b Prospective exclusion is not usefully testable within V2's horizon (D4 repair R2; wording and D corrected by R3, Astra m6 / m7)

**Population of θ_P.** θ_P = E[N]/E[C] is a ratio over **executed** trades. It is induced by the market opportunity process × R* × the REALISTIC fill model at S_ref. The opportunity chain is frozen for reporting:

```text
OPPORTUNITY_UNIT   = one STATION_TABLE event e (ICAO, kind HIGHEST / LOWEST, local target date) at T_entry(e);
                     at most 96 per target date (48 stations × 2 kinds)
SIGNAL             = R* evaluated for e on a VALID_CAPTURE entry snapshot and vintage (action ∉ {MISSING, INELIGIBLE})
TRIGGER            = SIGNAL with E_max ≥ h (a chosen leg exists)
ATTEMPTED          = TRIGGER passed to the REALISTIC fill model at S_ref
EXECUTED (trade j) = ATTEMPTED with a REALISTIC fill (≥ 5 shares within best ask + 0.02); only executed trades enter
                     N, C, θ̂, θ_W and θ_P
NO_FILL_*          = ATTEMPTED without a fill; contributes nothing to N or C (V1 §11), so it lies outside θ_P's
                     population by the frozen estimand, not by conditioning
TAIL_ARRIVAL       = EXECUTED trade with a_j < 0.04 (stratum at T_entry, 5.2)
TAIL_TRIGGER       = TRIGGER whose chosen leg has a_j < 0.04, executed or not
TIME / CLUSTERS    = local target date; 5-date block; ICAO station; (block, ICAO) — as section 9
```

The random object C2 is about is therefore the **arrival process of executed trades by type** (price bin × outcome probability). Unfilled triggers are reported in `TAIL_ARRIVAL_REPORT` (17.3) but do not change θ_P. Tier allocation (15.3) acts only on tier ledgers, never on the S_ref estimand.

**Maximum payoff.** R* may execute any leg whose ask `a ≥ 0.001` (the venue tick) satisfies `q − a − f(a) ≥ h`, and nothing in R* bounds `a` from below. The all-in cost per share is at least `c_min = 0.001 + 0.05 · 0.001 · 0.999 = 0.00104995`, so a winning executed leg returns at most `1/c_min − 1 = 951.4` per dollar committed.

**Theorem (finite-horizon power ceiling for prospective exclusion).** This is a finite-horizon power ceiling, not non-identification in the asymptotic sense: the ceiling grows without bound as D grows (Astra m7).

- Setup. Let 𝒫 be the admissible class: stationary executed-trade processes consistent with R*'s frozen mechanics, with any win probabilities `p ∈ [0, 1]`, executable prices ≥ the 0.001 tick, and any dependence, including the date / regime common modes that V2's own dependence model declares (section 9). Fix a threshold `θ* ∈ {θ_ERT, θ_PCE}`. Let φ be any test, possibly randomised, that uses the data V2 can observe. These are all target dates whose outcomes V2 can see before ANALYSIS_TIME: the 120 window dates, the 14 OP dates, and the resolved pre-t0 history (BIAS_HISTORY ≤ 40 dates span, GR3 parser history), so `D = D_obs ≈ 174` (Astra m6), plus anything independent of them. Suppose φ has level α over the null: `P_Q(φ = 1) ≤ α` for every `Q ∈ 𝒫` with `θ_P(Q) ≥ θ*`.
- Claim. Then for every `P ∈ 𝒫` with `θ_P(P) = θ_0 < θ*`:

```text
P_P(φ = 1)  ≤  α · (1 − η*)^(−D),        η* = (θ* − θ_0) / (1/c_min − 1 − θ_0)
```

*Proof.*
1. Build Q from P. Independently of everything else, each target date is, with probability η*, a "jackpot date": on it every executed trade (same events, same capital `C_j`) is instead a 0.001-ask leg with `p = 1`. All other dates follow P.
2. Q ∈ 𝒫: it has 0.001 asks, `p ∈ [0, 1]` and a date common mode. Per dollar, `θ_P(Q) = (1 − η*) θ_0 + η* (1/c_min − 1) = θ*`.
3. The event "no jackpot date among the D dates" has probability `(1 − η*)^D` and is independent of P's data. On that event Q's data law equals P's.
4. Hence `α ≥ P_Q(φ = 1) ≥ (1 − η*)^D · P_P(φ = 1)`. ∎

The construction needs only one admissible Q. It uses no information about real markets.

Numbers (DERIVED), with α = 0.05:
- With D = 174 (m6 correction), the power ceiling is ≤ **0.0602** for θ* = θ_ERT and ≤ **0.0611** for θ* = 0.10, at every θ_0 ≥ −1 (−1 is the minimum possible θ: every leg loses). At θ_0 = −0.10 it is 0.0511 (ERT) and 0.0519 (0.10).
- The earlier R2 numbers at D = 134 (0.0577 / 0.0584; `WEATHER_FORWARD_V2_D4_C2_SIM_2026-09-30.py ceiling`) omitted the pre-t0 resolved history.
- So a valid prospective exclusion test can have at most ≈ 0.8 percentage points more power than a coin that rejects with probability 0.05, against every admissible truth, including an R* that loses everything.
- Even under trade-level independence of arrivals, which V2's dependence model does **not** grant, the ceiling over N = 4,200 trades is 0.085 at θ_0 = −0.10 and 0.50 at θ_0 = −0.5. That is still no useful exclusion in the plausible range.

**Zero-count rule (frozen).** The theorem does not depend on how many tail legs the window contains. Whether it has 0, 1, 2, 5 or 10 observed sub-cent legs, or no tail leg of any price, the unobserved jackpot-date type stays equally possible. **Zero observed TAIL arrivals never implies a zero prospective tail rate.** SIMULATED (run E, counts): with 0 observed sub-cent legs, the retired rule excluded in 92–93% of runs whatever θ_P was (0.019, 0.376 or 1.089), and with ≥ 1 observed leg in 0%. The frozen rule issues no prospective exclusion at any count.

**Frozen consequence.** `PROSPECTIVE_EXCLUSION_USEFULLY_TESTABLE = FALSE` (named `PROSPECTIVE_EXCLUSION_IDENTIFIABLE` before R3). This is a constant derived above from frozen quantities (tick, fee, the h-rule's admissible asks, D_obs, α = 0.05) and the frozen dependence class, so no run-time gate and no discretion exist. V2 contains **no prospective exclusion label**:
- ECONOMIC_RESULT has no EXCLUDED value (17.2).
- `R*_REJECTED_AS_NET_STRATEGY` is never issued (17.6).
- Every result prints `PROSPECTIVE_EXCLUSION = NOT_USEFULLY_TESTABLE_IN_V2_HORIZON` (printed `NOT_IDENTIFIED_IN_V2` before R3).

This is loss of power, not a validity defect: by the theorem no valid alternative has materially more.

**Error guarantee after R2.**
- (Superseded by R3, 8.5c.) Under R2 the positive claim was `PROSPECTIVE_VALUE_CONFIRMED` via T2. After R3 T2 tests θ_W, at one-sided α = 0.05, combined with the information claims by intersection-union (6.3). No label is prospective.
- No prospective adverse claim is issued, so no arrival-uncertainty component needs an α share.
- The realised-window bound U_W has a single stochastic component (the calibrated core bound of 8.1c at one-sided 0.025) plus a deterministic tail term, at level 95% jointly with reach over 𝒟_P*. No two stochastic bounds are combined anywhere.

**Alternatives evaluated (not adopted).**
- *R2-A arrival-process bound.* Replace `M_tail` by the sum over tail price bins `[c_min, 0.002), [0.002, 0.005), [0.005, 0.01), [0.01, 0.02), [0.02, 0.04)` of an exact Poisson upper bound on executed arrivals × the bin's maximum payoff per dollar.
  - It is valid only under trade-level (or known-cluster) independence of arrivals, which V2's dependence class does not grant. Under date-clustered arrivals a trade-count bound overstates the information.
  - Even granting independence, zero observed legs in the lowest bin give an allowance ≥ 5.30/N × 951 ≈ 1.2 at N = 4,200 (Bonferroni 0.005 per bin). Exclusion is never reached: SIMULATED run E, `P(U_R2A < θ_ERT) = P(U_R2A < θ_PCE) = 0` in every scenario.
  - R2-A is therefore R2-B with an unjustified assumption added.
- *R2-C, realised-window estimand only.* θ_W exclusion answers "were the trades R* happened to execute worth less than 0.02 per dollar", not the North Star question. It is adopted **only** as the report field `REALIZED_WINDOW_BOUND`, never as a prospective claim and never as a rejection of R*.
- Excluding sub-cent legs, raising h, or a price floor would be trading-rule changes. They are not authorised and would be V3 material.

**Finite horizon vs long run (finite-horizon non-testability region).**
- A mechanism whose arrival interval materially exceeds the observed dates, but whose payoff per dollar can reach 951, cannot usefully be excluded by the ≈ 174 observed dates. The whole region `θ_P ≥ θ_ERT` is non-excludable in V2.
- Excluding it would need either a declared and independently audited arrival model, or a horizon with `D · η* ≫ 1`. For θ_0 = −0.10 that is `1/η* ≈ 7,900` dates per unit of the exponent. Both are outside V2.

**Why no capital decision is weakened.** Deployment was never authorised by V2. After R3 the only forward-looking output is `SHADOW_CONTINUATION_SIGNAL` (17.5) plus the transport frontier (8.5c), and capital needs a separate governance decision. "Not confirmed" already means no capital, so the absence of prospective exclusion changes no capital decision. Governance may retire R* using the information-level (`R*_CORE_INFORMATION_REJECTED`) and realised-window evidence. That is a governance judgement, not a V2 statistical claim.

**Prospective confirmation: superseded by D4 repair R3 (8.5c).** The R2 text here argued that bounded downside made unconditional prospective confirmation safe. It compared loss regimes by date frequency (`η = θ_0/(1 + θ_0)`) instead of cost mass. A loss date can carry up to `C_CAP_DATE / C̄_d` times an ordinary date's cost, so the argument is false in general (Astra C3: false confirmation 0.43 / 0.12). The R2 run-E confirm rows (0.0378 at θ_0 = 0.02, …) are correct for their equal-capital design only. The correct treatment is 8.5c.

### 8.5c Transport contract and robustness frontier (D4 repair R3, after Astra D4-C2 recheck C3 @92c2f706)

**What "prospective" means.** Let `P_obs` be the joint law of everything V2 observes before ANALYSIS_TIME: the window, the OP, and the resolved pre-t0 history. Let `Q_H` be the law of R*'s executed-trade process over a future deployment epoch of H counted dates. Apart from mechanics, V2 freezes **no** relation between `P_obs` and `Q_H`. The mechanics are: R* frozen, REALISTIC execution at S_ref, `N_j ≥ −C_j`, and a per-date cost cap.

Under that class, finite data cannot establish an unconditional statement about `θ_P = E_Q[N]/E_Q[C]` in either direction:
- Exclusion: the ceiling theorem of 8.5b.
- Confirmation: the mirror theorem below. Astra C3 showed the realised consequence: the retired R2 label `PROSPECTIVE_VALUE_CONFIRMED` was issued at θ_P = −0.005 in 43% (thin fills) and 12% (full fills) of runs.

`θ_P` therefore remains the strategic target, but it is **not an empirical estimand of V2**. V2 separates two layers:
- **Sampling inference** on the realised-window value θ_W (5.1), by T2's calibrated multi-block source bound L_W (8.1c; D4-C3-M2). The R3 5-date-block engine is retired for T2 (Astra M1, M1-R; m10). It asks: given the process that produced these trades, what is the uncertainty about their expected value?
- **Transport**: an explicit, assumption-indexed, deductive map from θ_W to a finite future epoch. It is never estimated from data.

A cluster-robust SE answers the first question only.

**Mirror theorem (unconditional prospective confirmation is not usefully testable).** Let P ∈ 𝒫 (the 8.5b class) have `θ_P = θ_0 > 0` and expected executed cost per date `A = E_P[C_d]`. Build Q: independently of everything else, each date is, with probability η, a loss date on which all `2·|STATION_TABLE|` events execute at the per-trade cost cap and every leg loses. With `B = C_CAP_DATE` (defined below):

```text
θ_P(Q) = ((1 − η) A θ_0 − η B) / ((1 − η) A + η B) = 0   for   η = A θ_0 / (A θ_0 + B)
```

On "no loss date among the D observed dates" (probability `(1 − η)^D`), Q's data law equals P's. Hence any level-α test of `θ_P ≤ 0` has power at P of at most `α (1 − η)^(−D)`. With α = 0.05, D = 174 (DERIVED; `D_obs` in m6 below):

| Ordinary expected date cost A (USD) | θ_0 = 0.02 | θ_0 = 0.05 | θ_0 = 0.10 |
|---|---|---|---|
| 255 (17 trades × 15 USD) | 0.060 | 0.078 | 0.120 |
| 525 (35 × 15) | 0.072 | 0.123 | 0.303 |
| 850 (17 × 50) | 0.090 | 0.216 | 0.918 |
| 1,750 (35 × 50) | 0.167 | 0.999 | 1 |

Unconditional confirmation is therefore powerless whenever ordinary dates carry little cost relative to the date cap. It is not excluded in thick geometries, but no test is valid over the whole class without a transport restriction. **V2 issues no unconditional prospective label** (17.2, 17.3). The asymmetry with exclusion is only one of degree:
- An unseen *positive* regime needs cost mass of only `(θ* − θ_0)/(951 − θ_0)`, because payoff can reach 951 per dollar. Exclusion is powerless in every geometry.
- An unseen *negative* regime needs cost mass `θ_0 / (1 + θ_0)`, because loss is at most −1 per dollar. That is a larger mass, but a date can carry up to `B / A` times an ordinary date's cost, so the required date *frequency* can still be small enough to go unseen.

**Worst-case return per unit of the θ denominator (exact).** For every executed trade `N_j = n_j (y_j − c_j)`, `C_j = n_j c_j` and `y_j ∈ [0, 1]`, so `N_j ≥ −C_j`. This holds exactly because:
- `c_j` is the all-in cost per share (walked levels and fee included);
- partial fills scale `n_j` and `C_j` together;
- void / 50-50 settlement has `y ≥ 0`;
- an unresolved trade is imputed `y = 0` for favourable claims (8.6);
- V1 charges no settlement-time fee;
- positions are unlevered and held to settlement;
- simultaneous positions sum.

Hence for any set of trades, `Σ N ≥ −Σ C`, and `WORST_CASE_REGIME_RETURN = −1` per dollar of C, with no approximation. A fee or settlement mechanics change (D11 codes M3, M5) would break this and invalidates the contract (below).

**Cost cap.** `C_TRADE_MAX = 1.05 × S_ref = 52.5 USD`: notional ≤ S_ref, and the fee `0.05 p (1 − p)` per share is ≤ 0.05 per dollar of notional. `C_CAP_DATE = 2 · |STATION_TABLE| · C_TRADE_MAX` (5,040 USD at 48 stations). Both are derived from frozen mechanics.

**Proposition 1 (cost-mass mixture identity).** For any epoch law Q and any partition of the epoch's executed trades into a *represented* set A and an *adverse* set B (the partition may depend on anything, including outcomes), let `ε_Q = E_Q[C_B] / E_Q[C]`. Then exactly

```text
θ_F(Q) := E_Q[N] / E_Q[C] = (1 − ε_Q) θ_A + ε_Q θ_B,   θ_A = E_Q[N_A]/E_Q[C_A],   θ_B = E_Q[N_B]/E_Q[C_B] ≥ −1
```

*Proof.* `E[N] = E[C_A] θ_A + E[C_B] θ_B`; divide by `E[C] = E[C_A] + E[C_B]`. `θ_B ≥ −1` follows from `N_j ≥ −C_j`. ∎

The contamination parameter must be **cost mass**, not dates, trades or stations. A single maximum-exposure date in an epoch of H dates carries `ε_1(H) = C_CAP_DATE / (C_CAP_DATE + (H − 1) C̄_d)`: 0.142 at H = 120 with 17 × 15 USD ordinary dates, but 1/H = 0.008 by date count. This is exactly the lever of Astra C3.

**Transport class (frozen).** `𝒯_H(ε, δ)` is the set of epoch laws `Q_H` over the next H counted dates for which some partition (A, B) satisfies:

```text
(T1)  E_Q[C_B] ≤ ε · E_Q[C]                      at most a fraction ε of expected executed cost is adverse (any return ≥ −1)
(T2)  θ_A(Q) ≥ θ_W − δ                            the represented cost earns at least the window's expected value, less δ
```

ε covers concentrated regimes: loss dates, template or station catastrophes, unseen trade types, anything. δ covers diffuse degradation of the whole book. The class is a **declared assumption** indexed by (ε, δ). V2 neither estimates nor verifies it.

**Theorem 2 (robust lower bound).** Let `L_W` be T2's one-sided lower bound (T2 ⟺ L_W > 0; 6.1). Since D4-C3-M2 this is the calibrated multi-block bound of 8.1c, `θ̂ − λ_θ · max_{b∈{5,10,20,30}} t_{df_b,0.95} · SE_2w(b)` with λ_θ = 2.15 (8.1d; cycle 2: 1.70; D4-C3-M1 used λ = 1, 8.1b); R3 used the 5-date-block `θ̂ − t_{df,0.95} · SE_CR(θ̂)` of 8.1. The algebra below holds for any L_W. On the event `{θ_W ≥ L_W}`, for every H, every (ε, δ) with `δ < 1 + L_W`, and every `Q ∈ 𝒯_H(ε, δ)`:

```text
θ_F(Q) ≥ L_T(ε, δ) := (1 − ε)(L_W − δ) − ε
```

*Proof.*
1. By Proposition 1 with `ε' = ε_Q ≤ ε`: `θ_F ≥ (1 − ε')(θ_W − δ) − ε'`.
2. The right side is decreasing in ε' because `∂/∂ε' = −(1 + θ_W − δ) < 0`, so it is ≥ `(1 − ε)(θ_W − δ) − ε`.
3. `θ_W ≥ L_W` gives the result. ∎

**Error statement (D4-C3-P1; supersedes the D4-C3-M2, D4-C3-M1 and R3 wordings kept below as history).** The only probability in any prospective statement is the sampling event `{θ_W ≥ L_W}` for the calibrated bound of 8.1c / 8.1d. `P(reach ∧ L_W > θ_W) ≤ 0.05` over the completely stated class 𝒟_P* (8.1c with the price laws of 8.1d): the 5-date-block model; date-level AR(1) (φ ≤ 0.9), two-state (φ ≤ 0.9), 15- and 30-date trailing-mean (the §9 mechanism), hemisphere and station regimes with latent variance ≤ 0.10; up to 30 paused dates; 60–120 counted dates; **the enumerated CORE price laws of 8.1d (U(0.35, 0.80), U(0.70, 0.90), U(0.80, 0.90), U(0.85, 0.90), a point mass at 0.89, and their mixes; not "CORE prices to 0.90" in general)**; m ∈ {17, 35}; thin / full fills. Run J worst cell 0.0394 at 20,000 replications; 100,000-replication confirmation 0.0397 [0.0385, 0.0409] (point mass 0.89, 30-date trailing mean, rv 0.10, m 35, no pauses). No level is claimed outside 𝒟_P*; the measured values for the nearest laws outside it are in 8.1d.

*D4-C3-M2 error statement, SUPERSEDED (Astra M3 @8874dc54: its printed class "CORE prices including favourite-heavy mixes up to 0.90" was calibrated only on U(0.35, 0.80), U(0.70, 0.90) and their mix; at U(0.85, 0.90) the miss was 0.0587 [0.0573, 0.0602]). Kept as history:* the same sentence with λ_θ = 1.70, "CORE prices including favourite-heavy mixes up to 0.90", run-H worst cell 0.0395 / 0.0415 [0.0403, 0.0427].

*D4-C3-M1 error statement, SUPERSEDED (Astra M1-R @ac777a87: it held only on the run-G grid; inside the class as written the cycle-1 bound reaches 0.0605–0.0852 (Astra) and 0.1176 (run H)). Kept as history:* The only probability in any prospective statement is the sampling event `{θ_W ≥ L_W}` for the multi-block bound of 8.1b. Its stated level is indexed by a declared dependence class.
- `P(reach ∧ L_W > θ_W) ≤ 0.05` under the 5-date-block model, and over the whole declared persistence class 𝒟_P: daily AR(1) date regimes with φ ≤ 0.9 and latent variance ≤ 0.10, across the 8.1b geometries. Run G worst cell: 0.0465 [0.0436, 0.0494] at 20,000 replications (φ 0.9, latent variance 0.05, m = 17 thin, θ = 0.10); independent 100,000-replication re-runs 0.0458 [0.0445, 0.0471] (that cell) and 0.0464 [0.0451, 0.0477] (full fills).
- Outside 𝒟_P no level is claimed, and the miss is higher (coverage lower): up to 0.072 at φ = 0.95 and 0.110 at φ = 0.97.

The class parameters (ε, δ) are not estimated and carry no α. The statement holds simultaneously for all (ε, δ, H), because it rests on the single event above. No second probability is combined with it.

The level is a repeated-experiment rate, counted jointly with reaching an evaluated state. It is not the probability that the bound holds given that a favourable label was issued. Given reach, the miss can be larger: for the D4-C3-P1 bound up to 0.148 over the enumerated 𝒟_P* cells with reach ≥ 0.10 (a grid figure, not a maximum: 8.1d); for the D4-C3-M2 bound up to 0.182 on the run-H grid and 0.203 in Astra's off-grid cell (8.1c); for the cycle-1 bound up to 0.136 at φ = 0.9 and 0.085 for φ ≤ 0.8 (8.1b).

*R3 wording, SUPERSEDED by D4-C3-M1.* Astra M1 (@5bb57eb2) showed that its 0.95 fails under the cross-block persistence §9 names; the R3 engine's joint miss reaches 0.08–0.13 over 𝒟_P (run G). Kept as history:

**Error statement (exact).** The only probability in any prospective statement is `P(θ_W ≥ L_W) ≥ 0.95`. This is the sampling coverage of the D8-accepted two-way CR engine for the realised-window value, conditional on the realised trade set. The class parameters (ε, δ) are not estimated and carry no α. The statement holds simultaneously for all (ε, δ, H), because it rests on the single event above. No second 95% is combined with it.

The 95% is an unconditional repeated-experiment coverage. It is not the probability that the bound holds given that a favourable label was issued. SIMULATED (run F, 20,000 replications per design): `P(L_W > θ_W)` is 0.0498 [0.0468, 0.0529] in a thick design (35 trades/date, full fills), 0.044 at θ = 0, and 0.0552 [0.0520, 0.0584] in a sparse, heterogeneous-fill design (17 trades/date, fills U(5, 25)). The ≈ 0.5 pp shortfall is the carried D8 finite-cluster property of the unchanged T2 engine (Astra: T2 0.0497–0.0573 under stress). It is disclosed and not corrected here.

**Robustness frontier (the scientific output).** For a threshold τ:

```text
ε*(δ, τ) = max{ε ∈ [0, 1] : L_T(ε, δ) ≥ τ} = (L_W − δ − τ) / (1 + L_W − δ)   if L_W − δ > τ,   else 0 (no support)
```

Properties (DERIVED; `WEATHER_FORWARD_V2_D4_C3_SIM_2026-09-30.py frontier`):
- `L_T` is strictly decreasing in ε, δ and τ: a larger adverse budget never yields stronger support.
- `L_T(0, δ) = L_W − δ` and `L_T(1, δ) = −1` (the mechanical worst case).
- `ε* < 1`, and ε* is decreasing in δ and τ.

Sanity check: `L_W = 0.10` gives `ε*(0, 0) = 0.10 / 1.10 = 0.091`. **No ε threshold is frozen in V2.** The frontier is reported on a fixed, outcome-blind reporting grid `δ ∈ {0, 0.01, 0.02, 0.05}` × `τ ∈ {0, θ_ERT}`, together with the formula, and is never compared with a required value. Any required ε, δ or H is a capital-governance choice outside V2 (see "Science vs capital" below).

**Epoch translation k*(H).** For a reporting grid `H ∈ {14, 30, 60, 120}` counted dates (existing V2 constants: OP length, W, IF1 floor, window; none selected), V2 prints how many **maximum-exposure fully-adverse dates** an H-date epoch could contain before positivity is lost:

```text
k*(H) = ε* H C̄_d / (C_CAP_DATE (1 − ε*) + ε* C̄_d),   ε* = ε*(0, 0)
```

C̄_d is the window's mean executed cost per counted date, and the translation assumes ordinary future dates carry C̄_d. This is a labelled volume-translation assumption. ε* itself does not depend on H: the expected-return bound is per unit of cost. What H changes is:
- the scope and expiry of the conditional claim;
- how much adverse mass one date represents (`ε_1(H)`);
- the observation cadence of the invalidation rules below.

A longer epoch leaves more room for regime shift. That is a governance judgement V2 does not make.

**Date-level economic concentration (always reported).**
- `C̄_d`, the maximum window date cost and the top-date cost share;
- `n_eff,C = (Σ_d C_d)² / Σ_d C_d²`, the effective number of economic dates (120 dates are not 120 equally informative economic units);
- `C_CAP_DATE`, the cap ratio `C_CAP_DATE / C̄_d`, and `ε_1(H)` on the H grid.

**Observable invalidation (future epochs; for a future Builder contract, not part of the single V2 analysis).** An epoch's transport status becomes `INVALIDATED`, with reason, from the first date on which any outcome-blind flag fires. The rules use only the window's own observed ranges, so there are no tuning constants:
- `MECHANICS`: any D11 code.
- `STATION_UNIVERSE`: station set differs from the frozen STATION_TABLE.
- `TICK_FEE_REGIME`: tick or fee schedule differs.
- `NEW_TAIL_BIN`: an executed arrival in a TAIL price bin with zero window arrivals.
- `COST_EXCEEDS_EVIDENCE`: a date's executed cost > the window maximum.
- `TRIGGER_COUNT_OUT_OF_RANGE`: a date's trigger count is outside the window's [min, max].
- `FILL_DEPTH_OUT_OF_RANGE`: a date's share of partially filled legs is outside the window's [min, max].

These flags **can only revoke** a contract. They cannot certify it. A loss regime with identical observable covariates until it occurs (run F scenario 06: same trade counts and fills, every leg loses) trips no flag. The only protection against it is the ε budget, which V2 reports and does not verify (`TRANSPORT_ASSUMPTION_STATUS = DECLARED_UNVERIFIED`). Astra C3's 96-event loss dates would trip `COST_EXCEEDS_EVIDENCE` at T_entry in 100% of simulated designs (run F). That is useful, but not a proof of transport.

**Rolling finite-epoch architecture (design only; not implemented; no authority granted).** A future Builder contract that consumes this frontier should carry:
- `EPOCH_START`, `EPOCH_END` (H counted dates);
- `EVIDENCE_VERSION` (window, hashes, θ̂, L_W);
- `TRANSPORT_CONTRACT_VERSION` (this section);
- `ROBUSTNESS_CERTIFICATE` (ε* grid, k*(H), concentration);
- `REGIME_INVALIDATION_REASON` (first flag, if any).

At `EPOCH_END` or invalidation the strategy returns to shadow and is reassessed with the enlarged evidence. That enlargement is how a rare loss regime eventually gets sampled.

**Science vs capital.** The scientific layer reports θ_W evidence, the frontier and concentration. Choosing a required ε, δ, H or τ for any capital size or risk budget is **capital governance**, a separate layer that V2 does not contain. `REAL_CAPITAL_AUTHORIZED = FALSE` is unaffected by any value of ε*.

**Quant-wide note (recommendation only; not implemented).** The finding is generic: any Quant strategy validated on a finite window faces the same θ_W → θ_P gap. A small interface between VET and SIZE, `TRANSPORT_CERTIFICATE {estimand, L_source, worst_case_return_per_denominator, frontier(ε, δ), concentration, observable_reference_ranges, contract_version, epoch, invalidation_reason}`, would let SIZE / RISK consume conditional evidence without reading it as unconditional edge. This mission does not refactor Quant.

### 8.6 Unresolved trades at analysis time

A trade whose market is not FINAL at ANALYSIS_TIME (section 11) is imputed **adversely per claim**: payout 0 for every favourable test (T1a, T1b, T2, gates) and payout `n_j` (win) for every adverse test or bound (NEG, U_W). Both imputations are computed; if no trade is unresolved they coincide. The count of unresolved trades is reported.

### 8.7 Reported, non-gating sensitivity set

V1 percentile moving-block bootstrap over dates (block 5, 10,000, seed 20260929); two-way pigeonhole bootstrap; block length {3, 7, 10}; hemisphere × block clusters; drop-one-station and drop-one-block jackknives; first vs second half of the window; PINM at ρ × {0.5, 2}; CONSERVATIVE execution; θ excluding non-NOAA settlement modes; winsorised θ labelled `NOT_THE_ESTIMAND`; tier ledgers.

---

## 9. Dependence model (D8)

| Element | Frozen definition |
|---|---|
| Date | the market's local target date `D` |
| Date block | `block(D) = floor((D − D_0) / 5)` in calendar days, `D_0` = first forward target date; blocks are calendar-contiguous, non-overlapping; paused dates simply contribute no trades |
| Station cluster | ICAO from the frozen STATION_TABLE (°C and °F) |
| Two-way intersection | (block, ICAO) |
| PINM cell | (local target date, ICAO): pairs the HIGHEST and LOWEST legs of one station-day |
| Variance | CGM two-way with CR1 factors, `SE = √max(V_B, V_S, V_2w)` (8.1) |
| Small-cluster correction | CR1 factor per dimension + `t_{min(G_B, G_S) − 1}` reference; for L_W, U_W, T1a and NEG the 5-, 10-, 20- and 30-date calendar-block forms with their own df_b, the largest taken and scaled by λ_θ = 2.15 / λ_κ = 1.80 (8.1c, 8.1d) |
| Minimum clusters | ≥ 12 blocks with ≥ 1 trade; ≥ 25 traded stations; Kish-effective traded stations ≥ 15 (information floor, section 11.4) |
| Kish-effective stations | `(Σ_s n_s)² / Σ_s n_s²` on trade counts (for κ) and on capital (for θ); both reported |
| Reported dependence | `DEFF_B = V_B/V_iid`, `DEFF_S = V_S/V_iid`, `DEFF_2w = max(V_2w, V_B, V_S)/V_iid` with `V_iid = n/(n−1) Σ e_j² / Q²`; `n_eff = n / DEFF_2w`; information per date; structural cap `D / ρ̂_d`, where ρ̂_d, ρ̂_s come from the variance decomposition of standardised residuals `(y_j − c_j)/√(c_j(1 − c_j))` (reported only) |
| Concentration diagnostics | share of `Σ e²` by the largest block and the largest station (reported); gross-profit shares enter gate G2 (section 17) |
| Mechanisms named | synoptic regimes shared across stations on one date (date/block); persistent station bias and the lag of the 30-date trailing bias through a seasonal transition (station); HIGHEST/LOWEST of one station-day (cell); unequal station activity (Kish); hemisphere/season common modes (sensitivity cluster) |

Date-only inference is never primary and never a fallback. SIMULATED (section 20): the date-only κ test rejects 0.095–0.205 under the null at nominal 0.025 with date/station dependence present; the two-way max-of-three test held size there, without cross-block persistence. *D4-C3-M2:* under the cross-block persistence this section names (seasonal lag of the 30-date trailing bias, regimes), the 5-date-block two-way tests do **not** hold size (run H: T1a up to 0.175, NEG 0.103, U_W miss 0.108, L_W 0.244 over 𝒟_P*; Astra M1 / M2). The calibrated multi-block tests of 8.1c hold their levels over 𝒟_P*, jointly with reach.

---

## 10. Thresholds, PCE formula and GO / NO_GO (D1, sections 19 and 27 of the mission)

### 10.1 Frozen constants

```text
θ_ERT             = 0.02
ALPHA             = 0.05 one-sided (favourable family); T1a, T1b at 0.025; attained over 𝒟_P* (8.1c)
TARGET_POWER      = 0.80 at θ_PCE
Z_80              = 2.4865   (z_0.95 + z_0.80: the nominal normal-approximation reference; the lower bound of Z_EFF)
Z_EFF             = 7.2      (D4-C3-P1, 10.4: effective multiplier of the T2 actually run, max over the declared laws of
                              theta80/SE0_theta rounded up to 0.1; Z_EFF >= Z_80, so every theta_PCE can only rise)
DEFF_PLAN(m)      = 1.5 × (1 + 0.03 × (m − 1))
MAX_INFORMATION   = 120 counted target dates
PCE_CEILING       = 0.10
SE_KAPPA_CEILING  = 0.005    (D4-C3-P1, 10.4: NEG power >= 0.90 at -0.07 per share for any design below it; was 0.020)
BLOCK_SET         = {5, 10, 20, 30} calendar days               (8.1b / 8.1c)
LAMBDA_THETA      = 2.15   (L_W, U_W; 8.1d, D4-C3-P1; calibrated over the enlarged 𝒟_P*; cycle 2: 1.70)
LAMBDA_KAPPA      = 1.80   (T1a, NEG; 8.1d, D4-C3-P1; calibrated over the enlarged 𝒟_P*; cycle 2: 1.60)
LEVEL_CONVENTION  = joint with reach (GO ∧ INFO_SUFFICIENT), over 𝒟_P* (8.1c); none claimed outside 𝒟_P*
```

### 10.2 θ_PCE formula (frozen now; populated once from the observation phase; never recomputed after t0)

Inputs: every R* decision with action TRADE under REALISTIC at S_ref whose target date is one of the 14 observation-phase dates (section 11.2). No settlement, outcome, hit rate or P&L enters.

```text
J          = those trades;  |J| = number of trades;  m̄ = |J| / 14
σ0²        = |J| · Σ_J C_j² (1 − c_j)/c_j  /  (Σ_J C_j)²          (price-implied fair-null variance per trade, capital-weighted)
n_120      = 120 · m̄
SE0_θ      = σ0 · sqrt( DEFF_PLAN(m̄) / n_120 )
θ_PCE      = ceil( 100 · Z_EFF · SE0_θ ) / 100                     (rounded UP to the next 0.01; Z_EFF = 7.2 since D4-C3-P1, was Z_80 = 2.4865)
m̄_core     = |J ∩ CORE| / 14
SE0_κ      = sqrt( mean_{J∩CORE} c_j (1 − c_j) ) · sqrt( DEFF_PLAN(m̄) / (120 · m̄_core) )
Λ_120      = (120 / 14) · Σ_{J∩TAIL} c_j                            (expected tail wins under the fair null)
```

### 10.3 GO / NO_GO (outcome-free design check, not a strategy result)

```text
GO iff   θ_PCE ≤ PCE_CEILING (0.10)
    and  SE0_κ ≤ SE_KAPPA_CEILING (0.005; was 0.020)
    and  distinct traded stations in J ≥ 25 and Kish-effective (trade counts) ≥ 15
    and  the observation phase met every GLOBAL_READY condition on all 14 dates
else NO_GO_<first failing reason in this order: PCE_ABOVE_CEILING, KAPPA_UNDERPOWERED, STATION_DIVERSITY, READINESS>
```

Rationale for `PCE_CEILING = 0.10` (D4-C3-P1: with θ_PCE computed by Z_EFF the ceiling again means what it says, "a design that can confirm with 80% power only edges above 0.10 is NO_GO"): it is 5 × θ_ERT and the lower end of the confirmable range V1 itself disclosed (§5: "≳ 0.10–0.13"). An economic arm that can confirm only edges larger than that answers a question whose plausible prior mass is negligible for a public-information taker rule in a market with public bots (V1 C11, C12); starting it would spend five calendar months to issue INDETERMINATE for every plausible truth. Rationale for `SE_KAPPA_CEILING = 0.020`: the information axis is V2's only real negative-result instrument; at SE 0.020 its MDE80 is 0.050 per share, and NEG (at 0.025) still rejects a public-bot-like loss rate (V1 C12, about −0.07 per share) with power ≈ 0.9; beyond that ceiling V2 would lose its only real negative result. **D4-C3-P1: both ceilings now certify what this paragraph says, for the tests actually run (T2 and NEG calibrated over 𝒟_P*, 8.1d): θ_PCE uses Z_EFF = 7.2 and SE_KAPPA_CEILING is 0.005, both derived outcome-free (10.4), and both only stricter than before. The consequence is measured and stated, not repaired: no design on the declared price laws passes GO at any throughput up to 96 trades per date (the NEG clause cannot be met; 10.4, 27). GO's meaning is unchanged.**

Honest consequence (DERIVED + SIMULATED, power table §2 and §4.2; **history: the θ_PCE values in this paragraph use Z_80 and are about 2.9 times larger with Z_EFF (10.4); every design it lists as GO is NO_GO under the recalibrated gate except favourite-concentrated ones, and those fail the κ clause**): at Astra's measured all-trigger dispersion (σ_eff ≈ 2.93) the formula gives θ_PCE ≈ 0.18–0.26 → **NO_GO**; at the no-lottery dispersion (σ_eff ≈ 0.96) it gives ≈ 0.06–0.08 → GO; in synthetic mixes, θ_PCE = 0.08 with no sub-4¢ legs (GO), 0.21 with 5% (NO_GO), 0.36 with 16% (NO_GO). **Because a single sub-cent leg carries the variance of hundreds of core legs, even a small lottery share makes the economic arm unpowerable in 120 dates.** Which case applies depends on how the frozen bias correction changes the executable leg mix, which only the observation phase can measure; the most likely pre-declared outcome, given Astra's b = 0 cross-section, is NO_GO_PCE_ABOVE_CEILING. A NO_GO is a design finding recorded as `WEATHER_FORWARD_SPEC_V2 = NO_GO_<reason>`, not a strategy result. It returns the decision to governance, which may (outcome-blind, since no outcome will have been observed) retire the Weather candidate or commission a new pre-registration (V3) — for example an information-primary experiment, or constant-payout sizing (which would make θ ≈ κ) or a tail-leg exclusion. Those are **trading-rule or design changes** that need their own freeze and independent audit; none is an amendment of V2.

Drift (mission §28 item 10): θ_PCE is frozen at t0 and labels always use the frozen value. At analysis the outcome-free realised `SE0_θ` over the whole window is reported; if it exceeds 1.5 × the planned value the report carries `PCE_DRIFT = TRUE` (descriptive; no label changes). After D4 repair R1, a post-OP drift of the tail price mix (Astra: 2 sub-cent legs appearing after a GO observation phase) can no longer create a false exclusion; it can only raise `M_tail` and make exclusion unattainable, which is reported. After D4 repair R2 there is no prospective exclusion at all; θ_PCE and GO keep only their confirmability role and are **not** an arrival-sufficiency check for rare tail types (Astra D4 recheck: GO passes 82–94% of the C2 designs).

*History (cycle 2; the gate was then left at its nominal meaning, which Astra @8874dc54 showed contradicted its rationale; D4-C3-P1 recalibrates it in 10.2–10.4).* Power under the calibrated T2 (D4-C3-M2, 8.1c; SIMULATED, power table §4.9): P(T2) at θ_PCE is 0.109 / 0.084 / 0.067 / 0.070 for m = 17 thin / 17 full / 35 thin / 35 full (joint with reach, no persistence), and the 80%-power effect is ≈ 0.18 (m = 17). A GO therefore no longer implies material T2 power at θ_PCE; θ_PCE, PCE_CEILING and GO / NO_GO are not retuned. *Cycle-1 numbers (history):* Power under the calibrated T2 (D4-C3-M1, 8.1b; SIMULATED, power table §4.8): P(T2) at θ_PCE is 0.554 / 0.476 / 0.456 / 0.459 for m = 17 thin / 17 full / 35 thin / 35 full (θ_PCE = 0.09 / 0.08 / 0.07 / 0.07), against 0.779 / 0.701 / 0.673 / 0.675 for the R3 engine (no persistence). The 80%-power effect is ≈ 0.11–0.12 (R3 engine ≈ 0.09–0.10; linear interpolation of P(T2) between θ_PCE and 0.12, no persistence). θ_PCE, PCE_CEILING and GO / NO_GO are frozen and are **not** retuned to this. A GO therefore no longer means "nominal 80% power at θ_PCE" for the T2 actually run. It means the design passes the frozen pre-registration ceiling, and the shortfall is disclosed here.

### 10.4 Gate calibration record (D4-C3-P1, P1 option (a); after Astra D4-C3-M2 recheck @8874dc54)

**Defect repaired (P1).** After D4-C3-M2 the tests actually run (T2 with L_W, NEG with κ̂_core, both multi-block and λ-scaled) were calibrated over 𝒟_P*, but θ_PCE (Z_80 = 2.4865 × SE0_θ) and SE_KAPPA_CEILING (0.020) kept the meaning of the nominal 5-date-block reference. GO would have started designs that its own frozen rationale forbids (mid-price designs with a simulated 80%-power effect ≈ 0.18 against PCE_CEILING 0.10; an information axis whose NEG had power ≈ 0.12 at −0.07 per share against the ≈ 0.9 SE_KAPPA_CEILING was frozen to guarantee). Spec 10.3 said so but did not say what GO certified. The repair is option (a): **an outcome-free, stricter-only recalibration of the design gate to the tests actually run**. GO's meaning is not redefined: GO still certifies what 10.3 says it certifies, now for the tests that are run. Option (b) (a governance redefinition of GO) is not taken.

**Procedure (declared and committed before any run of run J: `ARCHITECT_PROGRESS_CYCLE3.md`, commit 03640425; seeds `SeedSequence([20261102, plan, cell, 0])`; 20,000 replications per cell).**
- Tests: T2 at λ_θ = 2.15 and NEG at λ_κ = 1.80 (8.1d). Dependence: the **planning** model only (V2 latent copula 0.05 / 0.05 / 0.10, no persistent component, 120 dates, no pauses, 48 stations), because the gate is computed from 14 outcome-free OP dates and cannot know a persistence shape. The further power lost to persistence is disclosed in the power table, not gated.
- Laws: price laws {U(0.35, 0.80), 50/50 mix, U(0.70, 0.90), U(0.80, 0.90), U(0.85, 0.90), point mass 0.89} × m ∈ {17, 35, 55} × {thin, full} = 36 designs; no GO filter. Power is stated **given INFO_SUFFICIENT** (IF1–IF5 unchanged, so reach is unchanged); P(INFO_SUFFICIENT) and the joint power are reported beside it.
- T2: a power curve over θ ∈ {0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.20, 0.25, 0.30}, x-axis the realised mean θ_W; `θ80_ℓ` = first linear-interpolated crossing of 0.80; `R_ℓ = θ80_ℓ / mean SE0_θ` (the unrounded SE0_θ of 10.2 over the OP draws of the cell). **Z_EFF = max(Z_80, ceil(10 · max_ℓ R_ℓ) / 10).** A law without a crossing would have been "T2-uncertifiable" and would have added a mean-ask clause; none occurred.
- NEG: a power curve over κ_core ∈ {−0.03, −0.05, −0.07, −0.09, −0.12, −0.16, −0.20, −0.25}; `κ90_ℓ` = the |κ| at which NEG power reaches 0.90; `R^κ_ℓ = κ90_ℓ / mean SE0_κ`. **SE_KAPPA_CEILING = min(0.020, floor(1000 · 0.07 / max_ℓ R^κ_ℓ) / 1000)**, i.e. exactly the 10.3 rationale: a design passing the ceiling has NEG power ≥ 0.90 at −0.07 per share.
- Verification: with the effect set to each replication's own θ_PCE (old and new formula), the claim "P(T2 | θ-side GO ∧ INFO_SUFFICIENT) ≥ 0.80" in every cell with ≥ 2,000 such replications; the worst cells at 100,000. A failure would move Z_EFF up by 0.1 (never down).
- Order and rule are mechanical (summariser `p1derive`, `verify`, `go`); the constants are frozen in 10.1 and in `WEATHER_FORWARD_V2_D4_C3_P1_CONSTANTS_2026-10-02.json`.

**Derived (run J, 684 derivation cells).**

| Price law | θ80 / SE0_θ over m 17–55 × fills | NEG κ90 / SE0_κ over the same | SE0_θ range | SE0_κ range |
|---|---|---|---|---|
| U(0.35, 0.80) | 6.29–**7.19** (θ80 0.147–0.215) | 9.43–9.73 | 0.0223–0.0324 | 0.0116–0.0158 |
| 50/50 mix | 5.85–6.47 (0.112–0.153) | 10.05–10.50 | 0.0180–0.0261 | 0.0107–0.0145 |
| U(0.70, 0.90) | 5.42–6.08 (0.074–0.097) | 10.47–11.29 | 0.0124–0.0179 | 0.0097–0.0131 |
| U(0.80, 0.90) | 5.11–5.86 (0.058–0.076) | 10.30–11.71 | 0.0103–0.0149 | 0.0087–0.0118 |
| U(0.85, 0.90) | 4.99–5.73 (0.053–0.067) | 10.72–**11.85** | 0.0092–0.0134 | 0.0081–0.0109 |
| point mass 0.89 | 4.67–5.70 (0.049–0.058) | 11.02–11.84 | 0.0086–0.0124 | 0.0076–0.0103 |

- **Z_EFF = 7.2** (the maximum, mid prices at m 35, full fills, 7.193; Astra's "about 5.0" is the favourite-law value). Z_80 = 2.4865 understated the multiplier of the T2 actually run by a factor 2.9. Z_EFF ≥ Z_80 always, so every design's θ_PCE can only rise: stricter-only.
- **SE_KAPPA_CEILING = 0.005** (max R^κ = 11.85 at U(0.85, 0.90), m 35: 0.07 / 11.85 = 0.0059 → 0.005). It is stricter than 0.020. Its meaning is the 10.3 rationale and nothing else.

**Verification: power at the design's own θ_PCE (θ-side clause, given INFO_SUFFICIENT; 20,000 per cell).**

| Formula | Cells with ≥ 2,000 GO ∧ INFO | P(T2 \| GO ∧ INFO) at θ = θ_PCE | 100,000-replication worst cells |
|---|---|---|---|
| old (Z_80 = 2.4865) | 40 of 48 | **0.014 – 0.51** (mid m 17: 0.014 / 0.022; favourite m 17: 0.07 / 0.08; point mass 0.89 up to 0.51) | — |
| **new (Z_EFF = 7.2)** | 28 of 48 (18 cells have no θ-side GO at all: mid, 50/50 mix and U(0.70, 0.90) at m 17; 2 more have < 2,000, power 1.00) | **0.976 – 1.000** | U(0.70, 0.90) m 35 full 0.9744 [0.9734, 0.9754]; m 55 full 0.9825 [0.9815, 0.9835]; U(0.80, 0.90) m 17 full 0.9969 [0.9963, 0.9974] |

The old formula fails the 0.80 claim in every cell: P1's defect, measured. The new formula meets it everywhere it can pass. It **over-certifies** favourite-concentrated designs (power ≈ 1 where 0.80 was the target) because one multiplier covers all laws; a law-specific multiplier would be less strict but is not adopted (a design-gate change in the looser direction on some laws is not stricter-only). The fraction of replications that are both θ-side GO and INFO_SUFFICIENT is 0.12–1.00 over the 28 cells (it falls with throughput: IF5 screens high-dispersion windows); it is reported, not gated.

**GO / NO_GO rates by price law (OP-only, 20,000 OP draws per cell; m = trades per date; "old" = the cycle-2 GO; "new" = this GO; "θ-side" = the θ_PCE ≤ 0.10 clause with Z_EFF; "κ-side" = SE0_κ ≤ 0.005).**

| Price law | old GO | θ-side new | κ-side new | **new GO** |
|---|---|---|---|---|
| U(0.35, 0.80) | 0.99–1.00 from m 12 (0.08–0.16 at m 8) | 0 at every m 8–96 (θ_PCE 0.15–0.31) | 0 | **0** |
| 50/50 mix | 1.00 from m 12 | 0 at every m 8–96 (0.12–0.25) | 0 | **0** |
| U(0.70, 0.90) | 1.00 | 0 below m 35; full fills 0.93 at m 35 and 1.00 from m 55; thin fills 0 at m 35 and 1.00 from m 55 | 0 | **0** |
| U(0.80, 0.90) | 1.00 | 0.47 at m 17 full; ≥ 0.99 from m 25 | 0 | **0** |
| U(0.85, 0.90) | 1.00 | 0.31 at m 12 full; 0.95–1.00 from m 17 | 0 | **0** |
| point mass 0.89 | 1.00 | 0.97 at m 12 full; 1.00 from m 17 | 0 | **0** |
| 1% / 3% TAIL mixes | 0.02–1.00 / 0.002–1.00 (rising with m) | 0 | 0 | **0** |
| log-uniform [0.04, 0.90], U(0.04, 0.35) | 0 (NO_GO under the cycle-2 gate too) | 0 | 0 | **0** |

**The recalibrated GO is not attained by any declared design at any throughput up to 96 trades per date, on every declared price law: the first failing reason is PCE_ABOVE_CEILING for mid, mixed and lottery-leg designs and KAPPA_UNDERPOWERED for favourite-concentrated designs that pass the θ-side clause.** The reason is the NEG clause: the smallest SE0_κ reachable (point mass 0.89, m 96) is ≈ 0.0070 > 0.005. Even at the best throughput NEG power at −0.07 per share is far below 0.9:

| Throughput | NEG power at κ = −0.07 given INFO_SUFFICIENT | P(INFO_SUFFICIENT) | Joint |
|---|---|---|---|
| m 17 | 0.06 (mid) – 0.25 (point mass 0.89) | 0.97 – 1.00 | 0.06 – 0.25 |
| m 35 | 0.16 – 0.52 | 0.59 – 0.84 | 0.09 – 0.44 |
| m 55 | 0.33 – 0.75 | 0.12 – 0.38 | 0.04 – 0.29 |
| m 80 / 96 | 0.61 – 0.89 | 0.002 – 0.055 (IF4 / IF5 fail) | ≤ 0.047 |

(the joint maximum over all 48 declared law-throughput-fill cells at κ = −0.07 is 0.44.)

**Consequences, stated plainly (and not repaired).**
1. **V2 as specified cannot start on any declared design.** This is a measured design-gate finding recorded as `WEATHER_FORWARD_SPEC_V2 = NO_GO_KAPPA_UNDERPOWERED` for every price law of 𝒟_P*, not a strategy result. If the Weather candidate is to continue, governance must change the horizon, the class, or the design (a V3 pre-registration), or accept an information axis without a usable negative-result instrument (option (b), which this loop does not take).
2. **The negative-result instrument at the −0.07 per share scale is unattainable at 120 counted dates over 𝒟_P*** (fundamental for feasibility; Astra's oracle benchmark: a worst-case-valid non-adaptive test has power 0.008 mid / 0.19 favourite at the cycle-2 θ_PCE). Window length W and every owner-frozen surface (R*, h, W, signal, cohort, entry rule, T_entry, S_ref sizing, execution rule, the 0.04 CORE / TAIL split) are untouched; this finding goes to the owner at loop end.
3. The θ-side clause alone would admit favourite-concentrated designs at m ≥ 17–55 with T2 power ≥ 0.976 at their own θ_PCE; that is reported, but without the NEG clause GO is not the GO of 10.3.
4. No gate was loosened; PCE_CEILING (0.10), the station and readiness clauses, IF1–IF5, the estimands, the accounting, R1 / R2 / R3, the label vocabulary, the 11-state machine and the SHADOW_CONTINUATION_SIGNAL are unchanged.

---

## 11. Horizon, readiness, t0 and analysis timing (D2, D6)

### 11.1 Readiness (D6)

```text
USABLE(s, κ, d | t)  iff  an archived PRIMARY vintage for (s, d) satisfying the section-3 selection rule exists,
                          and market (s, d, κ) is FINAL (resolved; not open for correction; not DISPUTED) with
                          first_observed_final_at ≤ t  (our own capture time of the final state),
                          and its settlement_mode is recorded.
BIAS_HISTORY_READY(s, κ, D)  iff  #{ d < D : USABLE(s, κ, d | T_entry(D)) } ≥ 30        (= V1 E8, clarified)
BIAS_WINDOW(s, κ, D)         = the 30 most recent such dates (no calendar cap after t0: V1 E8 as frozen)
BIAS_SPAN(s, κ, D)           = D − (oldest date in BIAS_WINDOW)   (reported for every decision)
FRESH_READY(s, κ, D)         iff  BIAS_HISTORY_READY and BIAS_SPAN ≤ 40 days      (readiness criterion only)
ELIGIBILITY_DATE(s, κ)       = first D with BIAS_HISTORY_READY (reported per station-kind)
```

Missing vintages make that date permanently unusable for that station-kind; a correction hold or dispute delays usability until FINAL; a clarification that changes a value after it was used leaves earlier decisions untouched (point-in-time, append-only, `supersedes`); WU_FALLBACK and NO_DATA_LOWEST settlements are usable exactly as in V1 (section 19, D10). Thirty elapsed days never substitute for thirty usable dates.

### 11.2 GLOBAL_READY, observation phase, t0 preconditions

```text
GLOBAL_READY(D) iff all of:
  GR1  ≥ 80% of STATION_TABLE stations are FRESH_READY for both kinds at T_entry(D), and ≥ 30 stations for ≥ 1 kind
  GR2  entry completeness (section 12.4) ≥ 95% over the 14 target dates ending D − 1
  GR3  settlement-parser agreement ≥ 98% over ≥ 30 resolved dates (V1 §20.2; automated, aggregate only)
  GR4  FORECAST_ACCESS procedure item closed (V1 manifest B)
  GR5  replay equivalence 100% over the 14 target dates ending D − 1
  GR6  no mechanics reason code (section 16) on ≥ 10% of baseline-eligible events in the 7 target dates ending D − 1

OBSERVATION_PHASE (OP) = the first 14 CONSECUTIVE local target dates on each of which GLOBAL_READY holds;
                         if GLOBAL_READY fails on an OP date, the OP restarts at the next date on which it holds.
OP ACTIVITY            = R* runs in decision-only mode (phase = PRE_T0): eligibility, q, edges, chosen leg, stratum,
                         REALISTIC/CONSERVATIVE hypothetical fills, capital demand, tier NO_TRADE_CAPITAL counts.
OP MAY INSPECT         = forecasts, q, edges, triggers, prices, tick regime, depth, hypothetical fills, capital demand,
                         station distribution, stratum shares, the section-10.2 quantities.
OP MUST NOT INSPECT    = any outcome, settlement or payout of a PRE_T0 decision, realised P&L, hit rate, winner identity.
ENFORCEMENT            = the PNL engine refuses decisions with phase = PRE_T0 (unit-tested); no query may join a PRE_T0
                         SIGNAL_DECISION row to a SETTLEMENT row; the readiness report schema has no outcome field.
READINESS REPORT       = WEATHER_FORWARD_V2_READINESS_REPORT (committed, hashed): GLOBAL_READY history, per-station
                         ELIGIBILITY_DATE, OP trades/day by stratum and station, σ0, SE0_θ, θ_PCE, SE0_κ, Λ_120,
                         depth ≥ 25 USD share, capital demand, GO / NO_GO, and (descriptive, D4 repair R1) the OP
                         TAIL_MAX_CONTRIBUTION Σ_TAIL (n_j − C_j) / Σ C_j, which shows whether an economic exclusion
                         can be attainable at all; it is not a GO criterion; and (descriptive, D4 repair R2) the OP
                         TAIL_ARRIVAL_REPORT (17.3).

t0 PRECONDITIONS (all): independent Astra re-audit of this exact V2 commit passes; BUILDER_AUTHORIZED by governance;
  Builder verification suite green (section 26); GLOBAL_READY + OP complete; readiness report committed with GO;
  STATION_TABLE / PARAMS / ENGINE / MANIFEST hashes recorded; t0 declared by Blue in governance within 21 days
  after the last OP date (otherwise the OP is re-run on the latest 14 GLOBAL_READY dates and θ_PCE recomputed by the
  same formula before any t0).
```

### 11.3 Forward window, counted dates, analysis time

```text
D_0              = the first local target date D such that T_entry(e) ≥ t0 for every event e of D in the STATION_TABLE
FORWARD DATE     = any local target date D ≥ D_0
PAUSE            = triggered at the end of forward date D if entry completeness over the trailing 14 counted dates < 80%;
                   it covers D + 1 onward and ends after 3 consecutive paused dates each with completeness ≥ 95%
COUNTED DATE     = a forward date not inside a PAUSE ("complete target date": every entry-expected event of D has a
                   recorded action code — TRADE / NO_TRADE / NO_FILL_* / INELIGIBLE / MISSING — and D is not paused)
WINDOW           = the first 120 COUNTED DATES; D_120 = the last of them
ANALYSIS_TIME    = 00:00 UTC on D_120 + 10 calendar days
                   (resolution by 23:59 ET on D + 1, + up to 7 days correction hold, + 1 day redemption, + margin)
DATA_FAILURE     = total paused dates > 30  → INVALID_DATA_FAILURE (V1)
```

One analysis, at ANALYSIS_TIME, over exactly the WINDOW (or the truncated window of section 16). No 60 / 90 option, no extension because results look promising, no early stop because they do not.

### 11.4 Information floor (INFORMATION_INSUFFICIENT is not a scientific negative)

```text
INFO_SUFFICIENT iff all of:
  IF1  counted dates in the analysed window ≥ 60
  IF2  ≥ 12 date blocks containing ≥ 1 trade
  IF3  ≥ 25 traded stations and Kish-effective traded stations (trade counts) ≥ 15
  IF4  SE_CR(κ̂_core) ≤ 0.025
  IF5  DEFF_2w(κ̂_core) ≤ 6
```

IF4 and IF5 use outcomes but are direction-neutral reliability conditions; they cannot convert a favourable result into an adverse one or vice versa. D4-C3-M2: IF4 and IF5 keep their 5-date-block definitions (8.1), so reach is unchanged by the calibration of 8.1c. IF4 is a reliability floor on the 5-date-block SE, not the half-width of the calibrated T1a / NEG (median ratio ≈ 2.4 without persistence).

### 11.5 Interim analyses

**None.** No efficacy look, no futility look, no "check at 90 if interesting". Before ANALYSIS_TIME the only forward-phase outputs are the automated integrity dashboard fields: completeness, eligibility and reason-code counts, mechanics checks, capture latency, replay status. No P&L, κ, θ, hit rate, win count or tail count may be computed on forward trades before ANALYSIS_TIME; the analysis module refuses to run on forward data earlier (unit-tested).

---

## 12. Book / capture observation contract (D3)

### 12.1 Timestamps

| Field | Semantics |
|---|---|
| `request_sent_at` | host wall clock when the HTTP request is sent |
| `captured_at` | host wall clock when the complete response body has been received (= `information_available_at` of the snapshot) |
| `exchange_book_timestamp` | CLOB `timestamp` field: **time of the book's last change**, not observation time (Astra X3) |
| `book_age` | `captured_at − exchange_book_timestamp` (diagnostic only; never gating) |

### 12.2 Capture windows and retries

```text
ENTRY window         captured_at ∈ [T_entry − 300 s, T_entry]
                     first attempt at T_entry − 240 s; on any failure retry every 20 s while inside the window
ENTRY_PLUS_5 window  captured_at ∈ [T_entry + 300 s, T_entry + 360 s] (CONSERVATIVE model only), same retry rule
SNAPSHOT USED        per token, the VALID capture with the greatest captured_at inside the window
BATCHING             POST /books and GET /book are both allowed; validity is judged per token
```

### 12.3 VALID_CAPTURE (per token)

```text
VALID_CAPTURE iff  captured_at inside the window
              and  HTTP 200, body parses, response asset_id equals the requested token_id
              and  exchange_book_timestamp ≤ captured_at + 2,000 ms          (else FUTURE_TIMESTAMP: invalid, retry)
              and  host clock offset ≤ 250 ms at the last NTP check, which is ≤ 60 min old
              and  provenance complete: request URL, method, HTTP status, request_sent_at, captured_at,
                   raw body sha256, engine version
```

No lower bound is placed on `exchange_book_timestamp`: a book that has not changed for hours is a valid, quiet book.

### 12.4 Entry completeness (E6 redefined)

```text
ENTRY-EXPECTED event   = an event that satisfies E1–E5, E7 and E8 at T_entry (every condition except the entry record)
COMPLETE entry record  = VALID_CAPTURE for all 22 tokens in the ENTRY window
                         and a PRIMARY vintage satisfying the section-3 selection rule
MISSING                = entry-expected but not complete (reason codes: missing_book_capture, future_timestamp,
                         missing_vintage); counted, listed, never dropped
ENTRY COMPLETENESS     = complete / entry-expected   (per date, per trailing 14 dates, and over the window)
VALIDITY THRESHOLD     = window entry completeness ≥ 95%   (else INVALID_DATA_COMPLETENESS)
```

A missing ENTRY_PLUS_5 capture does not make an event MISSING; its CONSERVATIVE fill uses the ENTRY book alone with the CONSERVATIVE haircuts, and the count is reported.

---

## 13. Pre-t0 phases (summary)

`CAPTURE START (day 1, table frozen) → BIAS_HISTORY_READY per station-kind (≈ day 33–40) → GLOBAL_READY (≈ day 40–45) → OBSERVATION PHASE (14 dates) → READINESS REPORT + GO/NO_GO → independent re-audit already passed + Builder authorised → t0 (Blue) → WINDOW (120 counted dates) → ANALYSIS_TIME (D_120 + 10)`. Expected calendar from capture start to analysis ≈ 190–200 days (DERIVED; Fable §5.3 with the V2 window).

---

## 14. Cohort, °F policy and bucket arithmetic (D7)

**Decision: include °F stations in the primary cohort via exact published-interval arithmetic.** Basis (mechanical, no outcomes): (i) MEASURED 66/66 open °F NOAA ladders have exactly 11 markets = `X°F or below`, nine contiguous 2 °F buckets `a-(a+1)°F`, `Y°F or higher`, with the same NOAA WRH template stating whole degrees Fahrenheit; (ii) °F settlement needs no unit conversion (the WRH page's native unit is °F), so its settlement chain is *less* ambiguous than °C; (iii) station diversity: 48 NOAA stations (37 °C + 11 °F, MEASURED) instead of 37, which directly strengthens the weakest inferential dimension (station clusters); (iv) V1 already froze σ = 1.8 °F and enumerated E13 (°F only), so its intent covered °F; (v) the arithmetic is a strict generalisation of V1's single-degree rule and reproduces it exactly for °C.

### 14.1 Frozen interval arithmetic (all units)

Parse each market's `groupItemTitle` with exactly these patterns (unit `U ∈ {C, F}`):

```text
^(-?\d+)°U or below$            → integer set (−∞, N]
^(-?\d+)°U or higher$           → integer set [N, +∞)
^(-?\d+)°U$                     → integer set [N, N]
^(-?\d+)-(-?\d+)°U$             → integer set [a, b], requires b ≥ a
Continuous interval of integer set [lo, hi]  =  [lo − 0.5, hi + 0.5)   (−∞ / +∞ at open tails)
q_k = F(hi + 0.5) − F(lo − 0.5) with the dressed mixture CDF F in the market unit (section 3)
Settled integer ↔ whole-degree reading; a continuous temperature x maps to integer N iff x ∈ [N − 0.5, N + 0.5)
```

### 14.2 E4 (V2): standard ladder

Exactly 11 markets; all titles parse; exactly one `or below` and one `or higher`; the nine middle integer sets have identical width `w` with `w = 1` if unit C and `w = 2` if unit F; sets are contiguous (`hi_k + 1 = lo_{k+1}`) and cover all integers; unit equals the STATION_TABLE unit. Otherwise `INELIGIBLE(ladder_nonstandard)` if the station never had a standard ladder, or mechanics code `M2 ladder_changed` if it had one at table freeze (section 16).

### 14.3 STATION_TABLE

Membership = every ICAO appearing in a NOAA-WRH-template daily temperature event (°C or °F) in the `closed=false` gamma listing at compilation, compiled once **before capture day 1** and frozen (hash) from then; stations appearing later are `EXPLORATORY_NEW_STATION` (never primary). Coordinates, elevation and IANA time zone from one OurAirports `airports.csv` snapshot committed as bytes with its sha256; unit from the observed ladder. Stations whose template is not NOAA WRH (MEASURED today: Hong Kong, Jinan, Taipei, Zhengzhou) are structurally ineligible.

Station-count robustness: the primary cohort has 48 NOAA stations (MEASURED); the information floor requires ≥ 25 traded and Kish ≥ 15, not "≥ 30 of ≈ 35".

---

## 15. Execution, capital allocation and tiers

### 15.1 REALISTIC (primary, unchanged)

V1 §12: ENTRY book; asks with price ≤ best ask + 0.02; 100% displayed size; level price; minimum 5 shares; fee per share `0.05 p (1 − p)`.

### 15.2 CONSERVATIVE (robustness; `EXECUTION_MODEL_CHANGED = TRUE`)

```text
book           worse of ENTRY and ENTRY_PLUS_5 (level-by-level max price / min size)   [unchanged]
levels walked  price ≤ best ask + 0.02                                               [unchanged]
size           50% of displayed                                                        [unchanged]
price paid     level price + ONE TICK, tick = the market's orderPriceMinTickSize recorded with the ENTRY snapshot;
               if absent: 0.001 when the best ask < 0.04 or > 0.96, else 0.01        [CHANGED from + 0.01]
```

Identical to V1 in the 0.01 regime; it removes an 11× artefact for 0.001-regime legs (Astra §6.5, Fable CD9). The signal, the REALISTIC fill and θ are unaffected.

### 15.3 Capital tiers and allocation (D12)

Tiers 100 / 500 / 1,000 / 5,000 USD; stake 5% of tier; open committed ≤ tier; per-station ≤ 20% of tier (V1). Allocation order: ascending `T_entry`; events with an identical `T_entry` (same time zone, or HIGHEST and LOWEST of one station) ordered by ascending `sha256(event_id + ":WFV2")`. First-come-first-served in time is the only causal allocation without reservation; the hash replaces V1's `event_id` tie-break, which would favour the same cities every day. Tier results are always labelled `CAPACITY_CONSTRAINED_SUBSAMPLE (T_entry order, Asia-Pacific first)`, reported with their regional composition next to the S_ref composition, and never read as θ.

---

## 16. Mechanics change (D11)

Reason-code families (every non-eligible event carries exactly one family):

| Family | Codes | Counts toward MECHANICS_SHARE? |
|---|---|---|
| STRUCTURALLY_INELIGIBLE | kind_not_temperature, template_not_noaa_wrh (station never NOAA at table freeze), station_unknown, EXPLORATORY_NEW_STATION, ladder_nonstandard (never standard) | NO |
| READINESS_INELIGIBLE | bias_history, created_too_late, not_accepting_orders, missing_entry_record (MISSING) | NO |
| AMBIGUOUS | rule_change, unit_mismatch, game_start_mismatch, description_deviates (V1) | NO (excluded; listed) |
| MECHANICS_CHANGED | M1 template_changed (a table station leaves the NOAA WRH template); M2 ladder_changed; M3 fee_changed (`feeSchedule` ≠ {rate 0.05, takerOnly true, exponent 1}); M4 tick_or_min_changed (tick ∉ {0.01, 0.001} or `orderMinSize` ≠ 5); M5 resolution_host_changed; M6 negrisk_changed | YES |

```text
BASELINE-ELIGIBLE event  = an event of a STATION_TABLE station that is not STRUCTURALLY_INELIGIBLE
MECHANICS_SHARE(D)       = #events of D with a MECHANICS code / #baseline-eligible events of D
MECHANICS_CHANGE fires   = (M3 on ≥ 50% of the baseline-eligible events of one forward date) → effective at that date
                           [a venue fee change is venue-wide; a single-market anomaly only makes that event ineligible]
                           or (MECHANICS_SHARE ≥ 0.50 on 14 consecutive forward dates) → effective at the first of them
EFFECT                   = the WINDOW is truncated to counted dates strictly before the effective date;
                           ≥ 60 counted dates → VALIDITY = VALID_TRUNCATED_MECHANICS_CHANGE (one analysis at
                           effective date + 10 days); < 60 → INVALID_MECHANICS_CHANGE_EARLY
```

Detection is automated from recorded fields. A semantic API change that no recorded field reveals may be declared by Blue with documentary evidence, effective from the documented change time (never from discovery time, never chosen after inspecting results). An event with a mechanics code is never traded. A mechanics change never authorises re-parameterisation; any continuation is a new experiment.

---

## 17. Terminal state machine (D2, D5; mission §§15–16, 30–31)

Three orthogonal axes plus three report fields. Each axis is evaluated by an ordered list; the first matching row is the value, so each axis is a total, mutually exclusive partition by construction.

### 17.1 VALIDITY_STATE (evaluated first)

| Order | Condition | Value |
|---|---|---|
| 1 | any decision used a record with `information_available_at > T_entry` | INVALID_LEAKAGE |
| 2 | params / engine / station-table hash differs from the t0 record | INVALID_PARAMETER_MUTATION |
| 3 | replay does not reproduce 100% of decisions byte-for-byte | INVALID_REPLAY_MISMATCH |
| 4 | total paused dates > 30 | INVALID_DATA_FAILURE |
| 5 | window entry completeness < 95% | INVALID_DATA_COMPLETENESS |
| 6 | MECHANICS_CHANGE with < 60 counted dates before the effective date | INVALID_MECHANICS_CHANGE_EARLY |
| 7 | MECHANICS_CHANGE with ≥ 60 counted dates before the effective date | VALID_TRUNCATED_MECHANICS_CHANGE |
| 8 | otherwise | VALID_COMPLETE |

### 17.2 SCIENTIFIC_STATE (product of two ordered axes)

Definitions: `T1`, `T2`, `NEG` from sections 6 and 8 (`T2` tests the realised-window value θ_W, D4 repair R3); `GATES = G1 ∧ G2 ∧ G3` with
G1 `θ̂_CONSERVATIVE > 0` (tick-aware, section 15.2); G2 `(Σ N_j − Σ top-5 N_j) / Σ C_j > 0` and no single target date > 25% and no single station > 20% of gross profit `Σ max(N_j, 0)`; G3 θ̂ over NOAA-mode settlements only > 0.

Pre-emption (ordered):

| Order | Condition | SCIENTIFIC_STATE |
|---|---|---|
| 1 | VALIDITY_STATE is INVALID_* | NOT_EVALUATED |
| 2 | ¬ INFO_SUFFICIENT (11.4) | INFORMATION_INSUFFICIENT |
| 3 | otherwise | `<INFORMATION_RESULT>__<ECONOMIC_RESULT>` |

INFORMATION_RESULT (ordered, first match):

| Order | Condition | Value |
|---|---|---|
| I1 | T1 | INFORMATION_DETECTED (INFO_SOURCE = CORE / TAIL / CORE_AND_TAIL) |
| I2 | NEG | NEGATIVE_INFORMATION |
| I3 | otherwise | NO_INFORMATION_DETECTED |

ECONOMIC_RESULT (estimand θ_W, the realised-window value; ordered, first match; D4 repair R3 — same conditions as R2, re-scoped and renamed):

| Order | Condition | Value |
|---|---|---|
| E1 | T2 ∧ θ̂ ≥ θ_ERT ∧ GATES | REALIZED_WINDOW_VALUE_SUPPORTED |
| E2 | T2 ∧ θ̂ ≥ θ_ERT ∧ ¬GATES | REALIZED_WINDOW_VALUE_NOT_ROBUST (lists failing gates) |
| E3 | otherwise | REALIZED_WINDOW_VALUE_INDETERMINATE |

No value asserts anything unconditional about θ_P (8.5c). The R2 names PROSPECTIVE_VALUE_{CONFIRMED, NOT_ROBUST, INDETERMINATE} are retired because their conditions test θ_W, not θ_P (Astra C3). There is no EXCLUDED value, because prospective exclusion is not usefully testable (8.5b). The V2@24d2342 row `E1: U < θ_ERT → NET_VALUE_EXCLUDED` is deleted. No confirmable result is lost by the deletion, because `U_W ≥ θ̂` (8.5) means the old row could never pre-empt a run with `θ̂ ≥ θ_ERT`. The realised-window statement it used to make is kept, with its correct estimand θ_W, in the `REALIZED_WINDOW_BOUND` report field (17.3).

Totality and exclusivity: each axis is an ordered list whose last row is "otherwise", so every reachable state has exactly one INFORMATION_RESULT and one ECONOMIC_RESULT. The 3 × 3 = 9 products plus the two pre-empting values are the complete SCIENTIFIC_STATE space (**11 values** after D4 repair R2; 14 before). A positive but economically irrelevant θ̂ (`θ̂ < θ_ERT`) is never SUPPORTED because E1 and E2 require `θ̂ ≥ θ_ERT`. I1 precedes I2, so a tail-detected run with an adverse core is INFORMATION_DETECTED with `CORE_ADVERSE = TRUE`; the forward-signal rule and `R*_CORE_INFORMATION_REJECTED` read `CORE_ADVERSE`, not INFORMATION_RESULT (17.5, 17.6).

Relation to Fable's six-label partition (mission §16): Fable's NEGATIVE_INFORMATION and NO_INFORMATION_DETECTED are V2's I2 and I3 rows (with the economic column now always reported); Fable's INFORMATION_CONFIRMED_NET_VALUE_{CONFIRMED, NOT_ROBUST, INDETERMINATE} map to V2's I1 × {E1, E2, E3} with the estimand made explicit (θ_W; prospective reading only via 8.5c); Fable's INFORMATION_CONFIRMED_NET_VALUE_EXCLUDED has no prospective counterpart after D4 repair R2 (8.5b) — its realised-window analogue is INFORMATION_DETECTED with a `REALIZED_WINDOW_*_EXCLUDED` report field. **Modified**: V2 also evaluates the economic column when information is not detected (six cells Fable's gate left unevaluated), because θ is the North Star quantity and must not be withheld by a less efficient statistic (D1-GATE); and INFORMATION_INSUFFICIENT is added as a pre-empting non-result. Validity and operability stay orthogonal, as Fable proposed.

### 17.3 Report fields (evaluated whenever SCIENTIFIC_STATE ∉ {NOT_EVALUATED, INFORMATION_INSUFFICIENT}; else NOT_EVALUATED)

```text
PROSPECTIVE_EXCLUSION     = NOT_USEFULLY_TESTABLE_IN_V2_HORIZON   (constant, section 8.5b; always printed)
PROSPECTIVE_CONFIRMATION  = NOT_ESTABLISHED_UNCONDITIONALLY        (constant, section 8.5c; always printed)
TRANSPORT_ROBUSTNESS_REPORT (section 8.5c; always printed when SCIENTIFIC_STATE is evaluated)
    SOURCE_ESTIMAND            θ_W (5.1)
    SOURCE_LOWER_BOUND         L_W = θ̂ − λ_θ · max_{b∈{5,10,20,30}} t_{df_b,0.95} · SE_2w(b), λ_θ = 2.15   (8.1d, D4-C3-P1; 8.1c
                               construction; T2 ⟺ L_W > 0), printed with the constant level text: "repeated-experiment sampling miss
                               P(reach ∧ L_W > θ_W) ≤ 0.05, counted jointly with reaching an evaluated state (not given this
                               label), over the declared class 𝒟_P* (spec 8.1c, 8.1d: date-level persistence up to daily autocorrelation
                               0.9 or a 30-date trailing-mean lag, latent variance ≤ 0.10, ≤ 30 paused dates, and the
                               ENUMERATED CORE price laws U(0.35, 0.80), U(0.70, 0.90), U(0.80, 0.90), U(0.85, 0.90), a
                               point mass at 0.89 and their mixes; not CORE prices in general);
                               no level is claimed outside 𝒟_P*"
                               (D4-C3-M2: λ_θ = 1.70 and the wording "CORE prices to 0.90"; SUPERSEDED, Astra M3 @8874dc54)
                               (D4-C3-M1: λ = 1 and the run-G grid 𝒟_P; SUPERSEDED, Astra M1-R @ac777a87)
                               (R3: L_W = θ̂ − t_{df,0.95} · SE_CR(θ̂), "one-sided 95% sampling coverage of θ_W"; SUPERSEDED, Astra M1)
    WORST_CASE_REGIME_RETURN   −1 per dollar of C (exact, 8.5c)
    ROBUSTNESS_FRONTIER        ε*(δ, τ) = (L_W − δ − τ)/(1 + L_W − δ) if L_W − δ > τ, else 0 (8.5c domain guard; Astra m8)
                               printed for δ ∈ {0, 0.01, 0.02, 0.05} × τ ∈ {0, θ_ERT},
                               with the formula and L_T(ε, δ) = (1 − ε)(L_W − δ) − ε; reporting grid only, never a decision threshold
    EPOCH_TRANSLATION          k*(H) for H ∈ {14, 30, 60, 120} counted dates (maximum-exposure adverse dates absorbed; volume-translation
                               assumption C̄_d labelled)
    COST_MASS_CONCENTRATION    C̄_d, max date cost, top-date cost share, n_eff,C, C_CAP_DATE, cap ratio, ε_1(H) on the H grid
    OBSERVABLE_REGIME_REFERENCE window ranges for the 8.5c invalidation flags (trigger count, date cost, fill depth, tail bins, stations, tick / fee)
    TRANSPORT_ASSUMPTION_STATUS DECLARED_UNVERIFIED (constant for the V2 analysis)
    CONDITIONAL_PROSPECTIVE_CLAIM  if ECONOMIC_RESULT = REALIZED_WINDOW_VALUE_SUPPORTED:
                               CONDITIONAL_PROSPECTIVE_SUPPORT(ε ≤ ε*(δ, 0), δ) — the sentence (c) below with the numbers; else NONE
REALIZED_WINDOW_BOUND  estimand θ_W (5.1), bound U_W (8.5, calibrated core bound of 8.1c); a report field — never a prospective
                 claim, never a rejection of R*; printed with the constant level text "U_W ≥ θ_W except with repeated-experiment
                 probability ≤ 0.05, counted jointly with reaching an evaluated state, over the declared class 𝒟_P* (spec 8.1c, 8.1d)"
                 ordered on U_W:  U_W < 0 → REALIZED_WINDOW_LOSS_CONFIRMED;  U_W < θ_ERT → REALIZED_WINDOW_RELEVANT_VALUE_EXCLUDED;
                                  U_W < max(θ_PCE, θ_ERT) → REALIZED_WINDOW_LARGE_VALUE_EXCLUDED;  else REALIZED_WINDOW_NOT_EXCLUDED
                 always printed with w_tail, M_tail (TAIL_MAX_CONTRIBUTION), w_core·U_core and EXCLUSION_BLOCKED_BY_TAIL;
                 the tail term is assumption-free for θ_W (8.5)
TAIL_ARRIVAL_REPORT  counts of EXECUTED TAIL arrivals and of unfilled TAIL_TRIGGERs (8.5b) by price bin [c_min, 0.002),
                 [0.002, 0.005), [0.005, 0.01), [0.01, 0.02), [0.02, 0.04), separately for the OP and the window, with their
                 capital share; descriptive, changes no label
INFO_SOURCE      T1a ∧ T1b → CORE_AND_TAIL;  T1a → CORE;  T1b → TAIL;  else NONE; printed with the constant level text
                 "T1a and T1b each at one-sided 0.025, T1 familywise ≤ 0.05, repeated-experiment rates counted jointly with reaching
                 an evaluated state, over the declared class 𝒟_P* (spec 8.1c, 8.1d; T1b exact under its declared copula)"
CORE_ADVERSE     NEG (TRUE / FALSE), printed even when T1 passes via the tail; printed with the constant level text "NEG at
                 one-sided 0.025, a repeated-experiment rate counted jointly with reaching an evaluated state, over the declared
                 class 𝒟_P* (spec 8.1c, 8.1d)"
```

Mandatory sentences:
- (a) Whenever ECONOMIC_RESULT ∈ {REALIZED_WINDOW_VALUE_INDETERMINATE, REALIZED_WINDOW_VALUE_NOT_ROBUST}: **"θ in [θ_ERT, θ_PCE) is neither confirmed nor excluded by this experiment; this is not evidence of zero edge."**
- (b) Always: **"V2 cannot usefully test prospective net value in either direction within its horizon (sections 8.5b, 8.5c): a rare, high-payoff or high-loss regime absent from the observed dates cannot be ruled out. REALIZED_WINDOW statements describe only the expected value of the trades executed in the window."**
- (c) Whenever ECONOMIC_RESULT ∈ {REALIZED_WINDOW_VALUE_SUPPORTED, REALIZED_WINDOW_VALUE_NOT_ROBUST}: **"This is evidence about the trades executed in the window. It becomes a prospective statement only under the declared transport class: with a stated sampling level of 95% (a repeated-experiment rate counted jointly with reaching an evaluated state, not a confidence given that this label was printed; it holds over the declared class 𝒟_P* of spec 8.1c / 8.1d — date-level persistence up to daily autocorrelation 0.9 or a 30-date trailing-mean lag, with the enumerated CORE price laws of 8.1d — and no level is claimed beyond it), R*'s expected return per dollar in a future epoch stays ≥ 0 if at most ε*(δ) of that epoch's expected executed cost comes from any worse regime (worst case −1 per dollar) and the rest earns at least θ_W − δ. V2 does not verify this premise and establishes no unconditional prospective edge."**

The result headline always prints θ̂, the realised-window interval `[L_W, U_W]` of 8.1c (stated joint level ≥ 0.90 over 𝒟_P*; it replaces the symmetric 90% interval of 8.1b, so REALIZED_WINDOW_LOSS_CONFIRMED and the interval can never disagree), L_W and U_W (labelled "realised-window bounds"), `PROSPECTIVE_EXCLUSION`, `PROSPECTIVE_CONFIRMATION`, ε*(0, 0), θ_ERT and θ_PCE.

Naming note (Astra m5): every `REALIZED_WINDOW_*` value, whether economic axis or bound, is a statement about θ_W only. The prefix is mandatory in every printed or stored field name.

### 17.4 OPERABILITY_STATE (orthogonal; never replaces or pre-empts the scientific label)

| Order | Condition | Value |
|---|---|---|
| 1 | no R* trade exists | NOT_EVALUATED |
| 2 | legal access confirmed impossible | INACCESSIBLE_LEGAL |
| 3 | VALIDITY = VALID_TRUNCATED_MECHANICS_CHANGE or any MECHANICS_CHANGE fired | NOT_OPERABLE_AS_TESTED |
| 4 | share of R* triggers with ≥ 25 USD fillable within the price cap (REALISTIC, ENTRY book) < 0.80 | DEPTH_INSUFFICIENT |
| 5 | ρ_30 at the 1,000 USD tier (REALISTIC, point estimate) < 0.05 | CAPITAL_INEFFICIENT |
| 6 | otherwise | ACCESSIBLE |

Flag `ACCESS_UNCONFIRMED = TRUE` while LEGAL_ACCESS_CONFIRMED = UNKNOWN. Row 5 uses outcomes and describes deployability at small capital only; it is not a scientific quantity.

### 17.5 Shadow-continuation rule (was the forward-signal rule)

```text
SHADOW_CONTINUATION_SIGNAL = TRUE  iff  VALIDITY = VALID_COMPLETE
                                    and ECONOMIC_RESULT = REALIZED_WINDOW_VALUE_SUPPORTED
                                    and CORE_ADVERSE = FALSE
                                    and OPERABILITY_STATE = ACCESSIBLE
                             FALSE otherwise
```

TRUE means only: propose to governance a further **paper / shadow evidence epoch** (8.5c rolling architecture). It is **not** a statement that an economic edge exists, it grants no capital and no live trading, and it carries the transport frontier as context. Continuing shadow evidence is also how a rare regime missing from this window eventually gets sampled.

History:
- D4 repair R3: renamed from `WEATHER_EDGE_FORWARD_SIGNAL`, whose name implied a prospective edge and which fired in Astra C3's false-confirmation runs. The conditions are unchanged apart from the label rename.
- D4 repair R2 (Astra minor m2): `CORE_ADVERSE = FALSE` replaced `INFORMATION_RESULT ≠ NEGATIVE_INFORMATION`.

### 17.6 Rejection rule

```text
R*_REJECTED_AS_NET_STRATEGY   never issued by V2; printed as NOT_USEFULLY_TESTABLE_IN_V2_HORIZON   (8.5b)
R*_CORE_INFORMATION_REJECTED  iff  CORE_ADVERSE = TRUE (NEG)                       (information-level, not economic)
```

**D4 repair R2 (after Astra D4 recheck C2 @3d18085).** Under R1 the rule was `R*_REJECTED_AS_NET_STRATEGY iff U(θ) < θ_ERT`, and that bound covers only θ_W. Astra reproduced false prospective rejections: 5.92% at θ_P = 0.025 with p_tail = 0.17, and 19–35% at p_tail 0.5–1.0. Run E reproduced 4.75% / 16.5–17.6% / 31.4% with fresh code. By the theorem of 8.5b, no valid rule can reject R* as a net strategy with useful power in V2. The label is therefore unreachable, and every result prints it as `NOT_IDENTIFIED_IN_V2`.

The information-level falsification `R*_CORE_INFORMATION_REJECTED` means "the rule's core legs are overpriced net of executable costs". It now fires on `CORE_ADVERSE` (NEG) whatever INFORMATION_RESULT is (Astra minor m2), says nothing about the tail or θ_P, and is never read as "R* has no net value". `NEGATIVE_INFORMATION` alone still never rejects R* economically, as R1 established.

History (R1, kept). The V2@94b5934 rule also rejected R* as a net strategy on `NEGATIVE_INFORMATION ∧ ECONOMIC_RESULT ≠ NET_VALUE_CONFIRMED`. In Astra's A1 geometry that clause fired in 32.0% of runs at θ = 0.0315 > θ_ERT. R1 removed it.

A REALIZED_WINDOW_* value is a statement about θ_W only: "the trades executed in this window had expected net value below the threshold per dollar". It is never a rejection of R*.

### 17.7 Old-to-new label map

| V1 label | V2 equivalent |
|---|---|
| WEATHER_EDGE_FORWARD_SIGNAL | SHADOW_CONTINUATION_SIGNAL = TRUE (17.5; not an edge verdict) |
| WEATHER_EDGE_REJECTED | no prospective economic equivalent (17.6: R*_REJECTED_AS_NET_STRATEGY = NOT_USEFULLY_TESTABLE_IN_V2_HORIZON); information-level R*_CORE_INFORMATION_REJECTED; realised-window REALIZED_WINDOW_* report field |
| WEATHER_EDGE_NOT_PROVEN | REALIZED_WINDOW_VALUE_NOT_ROBUST / REALIZED_WINDOW_VALUE_INDETERMINATE (with the information column) |
| WEATHER_EDGE_REQUIRES_MORE_DATA | retired (REALIZED_WINDOW_VALUE_INDETERMINATE plus mandatory sentences (a) and (b)) |
| WEATHER_EDGE_OPERATIONALLY_INACCESSIBLE | OPERABILITY_STATE axis (never a scientific label) |
| WEATHER_FORWARD_TEST_INVALID | VALIDITY_STATE = INVALID_* |

### 17.8 Claim matrix (D4 repair R3; supersedes the R2 matrix)

| Label / field | Axis | Estimand | Null | Test / bound | Level / coverage | Assumptions | May claim | May not claim | Rejects R*? | Builder? | Capital? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| REALIZED_WINDOW_VALUE_SUPPORTED | economic | θ_W | θ_W ≤ 0 | T2 (L_W > 0, calibrated multi-block bound 8.1c / 8.1d, λ_θ = 2.15) + θ̂ ≥ θ_ERT + G1–G3 | size ≤ 0.05, joint with reach, over the completely stated class 𝒟_P* (8.1d; measured worst 0.0253; 100,000-replication 0.0240 [0.0231, 0.0250]); none claimed outside 𝒟_P*; not a rate given that the label was printed (IUT with information claims) | dependence inside 𝒟_P* | the executed window trades had positive expected value, point estimate ≥ θ_ERT, robust to G1–G3 | anything unconditional about θ_P; "edge exists"; deployment | no | no | no |
| REALIZED_WINDOW_VALUE_NOT_ROBUST | economic | θ_W | θ_W ≤ 0 | T2 (8.1c) + θ̂ ≥ θ_ERT, a gate fails | size ≤ 0.05, joint with reach, over 𝒟_P* (8.1c); none claimed outside 𝒟_P* | as above | positive θ_W failing the listed gates | shadow continuation; any prospective claim | no | no | no |
| REALIZED_WINDOW_VALUE_INDETERMINATE | economic | θ_W | — | — | — | — | not supported (sentences a, b) | "no edge"; "edge excluded" | no | no | no |
| TRANSPORT_ROBUSTNESS_REPORT / CONDITIONAL_PROSPECTIVE_SUPPORT(ε*, δ) | transport (report) | θ_F over a future H-epoch | — | deductive: `L_T(ε, δ) = (1 − ε)(L_W − δ) − ε` over 𝒯_H(ε, δ) | the single sampling event θ_W ≥ L_W, at the class-indexed level of 8.1c (miss ≤ 0.05 joint with reach over 𝒟_P*; worst 0.0397 [0.0385, 0.0409] at 100,000; none claimed outside 𝒟_P*); ε, δ carry no α | the declared class 𝒯_H(ε, δ) (8.5c), unverified | if the premise holds, θ_F ≥ L_T(ε, δ); frontier ε* | that the premise holds; an unconditional θ_P claim; that any ε is "enough" | no | no | no |
| PROSPECTIVE_CONFIRMATION = NOT_ESTABLISHED_UNCONDITIONALLY | prospective | θ_P | θ_P ≤ 0 | none (mirror theorem 8.5c) | — | — | no unconditional positive claim is made | any unconditional positive claim | no | no | no |
| PROSPECTIVE_EXCLUSION = NOT_USEFULLY_TESTABLE_IN_V2_HORIZON | prospective | θ_P | θ_P ≥ θ_ERT / θ_PCE | none (8.5b ceiling ≈ 0.06) | — | — | no exclusion is made | any exclusion of θ_P | no | no | no |
| R*_REJECTED_AS_NET_STRATEGY | prospective | θ_P | — | not usefully testable | — | — | never issued | — | — | no | no |
| REALIZED_WINDOW_BOUND (LOSS_CONFIRMED / RELEVANT / LARGE / NOT_EXCLUDED) | realised window (report) | θ_W | θ_W ≥ 0 / θ_ERT / max(θ_PCE, θ_ERT) | U_W (calibrated core bound 8.1c / 8.1d, λ_θ = 2.15, one-sided 0.975; tail term deterministic) | 95%, joint with reach, over 𝒟_P* (8.1d; measured worst miss 0.0034; pre-repair 5-date U_W reached 0.108); none claimed outside 𝒟_P* | dependence inside 𝒟_P* for the core | the executed window trades had expected value below the threshold | anything about θ_P; a rejection of R*; "the observed return was negative" | no | no | no |
| INFORMATION_DETECTED (INFO_SOURCE) | information | κ_core; λ_tail | κ_core ≤ 0 ∧ λ_tail ≤ 1 | T1a (calibrated CR, 8.1c / 8.1d, λ_κ = 1.80) ∪ T1b (PINM) | FWER ≤ 0.05 (T1a, T1b each 0.025), joint with reach, over 𝒟_P* (8.1d; measured T1a ≤ 0.0199, T1b ≤ 0.0077, T1 ≤ 0.0078 in the TAIL designs; pre-repair 5-date T1a reached 0.175); none claimed outside 𝒟_P* | PINM copula for T1b; dependence inside 𝒟_P* | chosen legs underpriced net of all-in cost | net value; θ_W; θ_P | no | no | no |
| NEGATIVE_INFORMATION / CORE_ADVERSE / R*_CORE_INFORMATION_REJECTED | information | κ_core | κ_core ≥ 0 | NEG (calibrated CR, 8.1c / 8.1d, λ_κ = 1.80) | 0.025, joint with reach, over 𝒟_P* incl. favourite (left-skewed) prices (8.1d; measured ≤ 0.0073; pre-repair 5-date NEG reached 0.103); none claimed outside 𝒟_P*; power at −0.07 per share 0.06–0.25 at m 17 and ≤ 0.44 jointly over every declared design (disclosed: not a usable negative-result instrument, 10.4) | dependence inside 𝒟_P* | core legs overpriced net of executable costs | tail, θ_W, θ_P; "R* has no net value" | no (information-level) | no | no |
| NO_INFORMATION_DETECTED | information | κ_core, λ_tail | — | — | — | — | no information detected | no information exists | no | no | no |
| SHADOW_CONTINUATION_SIGNAL | routing | — | — | 17.5 | inherits the labels it reads | — | a further paper/shadow epoch may be proposed | an edge exists; capital; live trading | no | no | no |
| OPERABILITY_STATE | operability | depth, ρ_30, mechanics, access | — | 17.4 | descriptive | — | accessibility at small capital | any scientific label | no | no | no |

No V2 label authorises the Builder or capital: Builder authority comes only from governance after an Astra pass, and capital only from separate capital governance.

Persistence note (D4-C3-P1; supersedes the D4-C3-M2 and D4-C3-M1 notes). Every economic, transport, realised-window and information row rests on the calibrated multi-block construction of 8.1c with the constants of 8.1d, and every level is stated jointly with reach over the one completely stated class 𝒟_P* (8.1c with the enumerated price laws of 8.1d), with the measured worst value. No row claims a level outside 𝒟_P* or conditional on a printed label. *D4-C3-M1 note (history):* the economic rows rested on the 8.1b bound over the run-G grid 𝒟_P, and the information rows and REALIZED_WINDOW_BOUND on 5-date-block tests qualified at statement level (Astra M1-R / M2).

---

## 18. Baselines, placebo and attribution (mission §25)

B0–B6 (V1 §10) are computed exactly as frozen, from archived records only, and reported with θ̂, κ̂_core, W_tail / Λ_tail and proper scores. **V1 gate criterion 9 ("R* beats B4 and B5 by ≥ θ_MEUE on θ") is retired as an inferential criterion and is purely descriptive in V2**: the standard error of a difference of two θ̂ (0.04–0.14) gives a 0.02 margin no inferential content. Information attribution is carried by T1 (the legs R* selects are, or are not, underpriced net of costs). Descriptive flag `ATTRIBUTION_NOT_ESTABLISHED = TRUE` if B5 (persistence) or B6 (structural tail) has κ̂_core or λ̂_tail ≥ R*'s; the flag changes no label. A B4 placebo with κ̂ significantly > 0 (two-way CR, 0.05) is reported as `PLACEBO_ANOMALY` and must be investigated as possible leakage before the result is published; it changes no label unless the investigation establishes leakage (then VALIDITY = INVALID_LEAKAGE).

---

## 19. Minor defects D9–D12

| ID | Decision |
|---|---|
| D9 MIN_SAMPLE = 1,000 non-binding / misleading | **Closed.** Retired as a power claim; replaced by the information floor (11.4) and the date-based power statement (7). Trade counts are reported. |
| D10 NO_DATA_LOWEST in the bias mean | **Accepted as frozen (MINOR, disclosed).** Removing it would change R*'s bias estimator (a rule change) and is not needed for validity; the experiment tests R* as frozen. Reported: per-station counts of non-NOAA modes inside bias windows; decisions whose window contains a NO_DATA_LOWEST date carry `BIAS_CONTAMINATED = TRUE`; θ̂ and κ̂ on the uncontaminated subset are a non-gating sensitivity. |
| D11 mechanics baseline | **Closed** (section 16). |
| D12 tier selection | **Closed** (section 15.3). |

---

## 20. Family D challenge — every failure mode closed, bounded or carried

SIMULATED numbers: `WEATHER_FORWARD_V2_POWER_TABLE_2026-09-29.md` §4 (script committed as `WEATHER_FORWARD_V2_SYNTHETIC_SIM_2026-09-29.py`).

| # | Failure mode | Status | How |
|---|---|---|---|
| 1 | κ_core detects calibration but not net value | CLOSED | κ uses all-in executable cost, so κ > 0 is net per share; net value for R* is only ever claimed through θ (T2, θ̂, gates; estimand θ_W after R3); after D4 repair R2 V2 cannot state prospectively "the chosen legs are underpriced, yet R* has no relevant net value" (8.5b); its realised-window analogue is INFORMATION_DETECTED with REALIZED_WINDOW_RELEVANT_VALUE_EXCLUDED |
| 2 | a tail-only edge blocked by a pooled gate | CLOSED | there is no gate on θ at all (D1-GATE); the information axis is stratified with an exact tail win-count test (SIMULATED power in the power table §4) |
| 3 | "either core or tail" rejection inflates FWER | CLOSED | Bonferroni α/2 + α/2 ≤ α under any dependence; SIMULATED T1 null rejection ≤ 0.05 within Monte-Carlo error (power table §4); under cross-block persistence the pre-repair T1 reached 0.071 and the D4-C3-P1 T1 is ≤ 0.0078 over the 𝒟_P* TAIL designs (8.1c, 8.1d) |
| 4 | Bonferroni inside T1 too weak / too conservative | BOUNDED | with two tests Holm = Bonferroni for the union rejection; Simes' gain limited to both p in (0.025, 0.05]; accepted |
| 5 | θ tested only after T1 changes its interpretation | CLOSED (by design change) | θ is not gated (D1-GATE); joint claims use intersection-union; a θ-only edge is reported in the NO_INFORMATION_DETECTED__REALIZED_WINDOW_VALUE_* cells, never hidden |
| 6 | requiring PINM and bootstrap agreement kills power | CLOSED (by design change) | agreement is not required; engines assigned by where each is valid (8.2) |
| 7 | assumed PINM copula wrong | BOUNDED | PINM gates only rare-event tail counts, where observed-scale dependence is ≈ 0.01 under latent 0.10; declared values conservative; ×0.5 / ×2 sensitivity reported; residual risk MINOR |
| 8 | ≈ 25–35 effective station clusters | BOUNDED | 48 NOAA stations after D7; max-of-three SE; t with `min(G_B, G_S) − 1` df; floor Kish ≥ 15; SIMULATED size under strong station dependence in the power table §4 |
| 9 | tail wins destabilise bootstrap intervals | CLOSED | no bootstrap in any gating role; empirical CR is self-normalising (a lone tail win inflates its own SE); the realised-window bound's tail term cannot be moved by any tail win or loss; prospective exclusion is not issued (8.5b); G2 removes the top 5 trades |
| 10 | pre-t0 PCE drifts over 120 dates | BOUNDED | PCE frozen at t0 and used as a label constant; realised outcome-free SE0 reported; `PCE_DRIFT` flag; re-run of the OP if t0 slips > 21 days |

---

## 21. Architect self-attack (mission §40)

| # | Attack | Result | Severity if surviving |
|---|---|---|---|
| 1 | V2 still claims power it does not have | **Not refuted as of cycle 2 (Astra m12); repaired by D4-C3-P1.** The only powered economic claim is θ_PCE; after D4-C3-P1 it is computed with the effective multiplier of the T2 actually run (Z_EFF = 7.2) and the simulated power of T2 at θ_PCE is 0.976–1.000 (10.4); §1 no longer calls the information axis "well-powered" and states that the NEG negative-result instrument is not usable at 120 dates; item 46 and 10.4 state the cost; 0.02 is declared non-adjudicable; every declared design is NO_GO (item 52) rather than run underpowered | MAJOR for feasibility (item 52; for Astra / the owner), not a statement defect |
| 2 | raw trade count confused with information | Refuted: date ceiling (7), DEFF(m) rising with m, information floor on dates / blocks / stations / SE | — |
| 3 | θ_ERT confused with θ_PCE | Refuted: separate constants, separate roles, mandatory sentence | — |
| 4 | κ presented as economic return | Refuted: κ enters only T1 / NEG / INFO_SOURCE; every net-value label uses θ | — |
| 5 | strata outcome-responsive | Refuted: price at T_entry, frozen constant 0.04, stored at decision time | — |
| 6 | tail-only edge hidden | Bounded: T1b detects a material tail edge; a weak one (λ ≈ 1.5) is under-powered and reported as such | MINOR |
| 7 | one tail win dominates the conclusion | Refuted for confirmation (CR self-normalisation + G2) and for the realised-window bound (the tail term assumes every realised tail leg wins, so no tail outcome can lower it); prospective exclusion does not exist after D4 repair R2 (8.5b) | — |
| 8 | date-only dependence sneaks back | Refuted: max-of-three never includes an IID or date-only fallback | — |
| 9 | assumed PINM dependence anti-conservative | Bounded: PINM gates only the tail count T1b (it no longer enters any bound); declared values above the advisory and observed-scale ranges | MINOR |
| 10 | undefined region in the state machine | Refuted: ordered total partitions (17) | — |
| 11 | operability hides a scientific rejection | Refuted: separate axis, never pre-empts | — |
| 12 | quiet books marked missing | Refuted: no lower bound on the exchange timestamp (12.3) | — |
| 13 | burn-in uses unresolved dates | Refuted: USABLE requires FINAL at T_entry(D) by our own capture time | — |
| 14 | °F arithmetic ambiguous | Refuted: frozen regexes, integer sets, half-open intervals, °F bias target = bucket midpoint, exact unit conversion | — |
| 15 | capital scarcity creates an unacknowledged subsample | Refuted: S_ref estimand has no capital cap; tiers labelled capacity-constrained with composition | — |
| 16 | optional stopping | Refuted: one analysis time; no interim; analysis module time-locked | — |
| 17 | Builder still makes a scientific decision | Refuted: section 26 lists every scientific item as frozen; residual Builder choices are engineering only | — |
| 18 | a trading-rule parameter changed because of feasibility | Refuted: R* unchanged; only CONSERVATIVE slippage (execution robustness) and the cohort domain changed, both mechanically motivated | — |
| 19 | the 0.02–PCE band treated rhetorically as zero | Refuted: mandatory sentences (a) and (b), PROSPECTIVE_EXCLUSION = NOT_USEFULLY_TESTABLE_IN_V2_HORIZON, REALIZED_WINDOW_BOUND field clearly scoped to θ_W | — |
| 20 | silent mutation under venue drift | Refuted: automated mechanics codes, truncation rule, new-experiment policy (22) | — |
| 21 | (added) exclusions rest on a tail model | **Resolved by D4 repair R1**: the tail term is the assumption-free supremum `M_tail`; coverage over the whole admissible tail class is at least the core coverage; Astra's two attacks give coverage 1.0 and zero false exclusions (power table §4.5). Scope after D4 repair R2: θ_W only (item 25) | — (cost: MINOR, disclosed) |
| 22 | (added) GO/NO_GO likely NO_GO at Astra's measured mix | Carried: an honest pre-declared outcome, not a defect; V2 does not pretend otherwise | MINOR |
| 23 | (added, D4 repair) an economic rejection is issued without a valid θ bound | **Resolved by D4 repair R1**: 17.6 now rejects R* as a net strategy only through `U(θ) < θ_ERT`; the NEG-only path (false economic rejection 32.0% in Astra's A1 geometry) is re-labelled information-level. After D4 repair R2 no economic rejection of R* is issued at all (item 25) | — |
| 24 | (added, D4 repair) the core bound itself under-covers for hidden edges at the 0.04 boundary | Refuted by run D: boundary-hidden coverage 0.993, boundary-diffuse 0.9705, false exclusion ≤ 0.0295; core payouts are capped at 25 per dollar by the stratum boundary | — |
| 25 | (added, D4 repair R2) prospective exclusion from a bound that sees only the sampled tail (Astra C2) | **Resolved by D4 repair R2**: identification theorem (8.5b); no prospective exclusion label; R1 bound re-scoped to θ_W. Run E: 0 prospective exclusions and 0 R* rejections in every scenario (retired rule 4.75–56% false) | — (cost: exclusion power ≤ 0.058 for any valid test; disclosed) |
| 26 | (added, R2) a θ_W exclusion read as a prospective rejection | Refuted: separate REALIZED_WINDOW_* vocabulary, mandatory sentence (b), claim matrix 17.8; no rule reads REALIZED_WINDOW_BOUND | — |
| 27 | (added, R2) prospective confirmation has the same sampling problem | **R2 answer refuted by Astra C3** (loss dates carrying the 96-event cap: false confirmation 0.43 / 0.12). **Resolved by D4 repair R3**: no unconditional prospective label; items 30–35 | — |
| 28 | (added, R2) GO / PCE relied on to rule out rare tail arrivals | Refuted: PCE and GO unchanged and not used for that; C2 designs pass GO 80–100% (run E) | — |
| 29 | (added, R2) zero observed tail legs read as a zero prospective tail rate | Refuted: zero-count rule (8.5b); retired rule excluded 92–93% at zero observed legs whatever θ_P was; frozen rule 0 | — |
| 30 | (added, R3) a realised-window positive read as a prospective edge | Refuted: economic labels renamed REALIZED_WINDOW_VALUE_*; PROSPECTIVE_CONFIRMATION = NOT_ESTABLISHED_UNCONDITIONALLY; sentence (c); claim matrix 17.8 | — |
| 31 | (added, R3) contamination measured in dates or trades, so a rare cap-date slips through | Refuted: ε is cost mass (Proposition 1, exact for E[N]/E[C]); ε_1(H) and k*(H) printed; one cap-date = 0.142 of cost mass at H = 120 with 17 × 15 USD dates | — |
| 32 | (added, R3) hidden loss regime with identical observable covariates | Bounded, not refuted: no flag can see it (run F scenario 06); only the ε budget covers it, and it is reported as DECLARED_UNVERIFIED | MINOR (disclosed; irreducible) |
| 33 | (added, R3) ε, δ or H chosen after seeing results | Refuted: none is chosen; frontier printed on fixed outcome-blind grids of existing constants; required values are capital-governance choices outside V2 | — |
| 34 | (added, R3) two confidence levels combined as one | Refuted: only θ_W ≥ L_W is stochastic; (ε, δ) index an assumption set; the bound is simultaneous over them | — |
| 35 | (added, R3) shadow continuation read as an edge verdict | Refuted: renamed SHADOW_CONTINUATION_SIGNAL; meaning restricted to another paper/shadow epoch; no capital path | — |
| 36 | (added, D4-C3-M1) the source bound's 95% holds only under the 5-date-block model, while §9 names cross-block persistence (Astra M1) | *SUPERSEDED by item 43 (Astra M1-R: the cycle-1 level held only on the run-G grid).* **Resolved by D4-C3-M1**: multi-block bound (8.1b). Joint miss / size ≤ 0.05 over the 5-date-block model and the declared class 𝒟_P (φ ≤ 0.9, latent variance ≤ 0.10); worst cell 0.0465 [0.0436, 0.0494] at 20,000 replications (φ 0.9, latent variance 0.05, m = 17 thin, θ = 0.10); independent 100,000-replication re-runs 0.0458 [0.0445, 0.0471] (that cell) and 0.0464 [0.0451, 0.0477] (full fills). No level is claimed outside 𝒟_P (up to 0.072 at φ = 0.95 and 0.110 at φ = 0.97). The R3 engine at the same cells reaches 0.1287 | MINOR (disclosed: outside-𝒟_P degradation; power cost) |
| 37 | (added, M1) the calibration tuned until a synthetic number passed | Refuted. The class, the pass criterion and the first candidate RM were declared before any run. RM's φ = 0.9 failure is published; no constant of RM was changed. The comparators and the selection criterion (validity over 𝒟_P first) were declared before their own first run. The adopted 30-date block is W, the 30-date trailing-bias window that §9 names | — |
| 38 | (added, M1) the repair makes a positive claim easier | Refuted: b = 5 is one of the four bounds, so L_W ≤ the R3 bound pointwise; no label, threshold or constant changed | — |
| 39 | (added, M1) the power cost is hidden, or θ_PCE silently retuned | Refuted: power table §4.8 (SUPPORTED, and P(T2) at θ_PCE and at 0.12 / 0.15, R3 vs M1). θ_PCE formula and GO / NO_GO are unchanged. The nominal-80% wording is qualified in 1, 6.2, 7, 10.3 and 24 | MINOR (disclosed: INDETERMINATE more likely) |
| 40 | (added, M1) the reach-inclusive (joint) rate hides a larger miss among reached runs | Disclosed. The error is the repeated-experiment joint rate, as in R3. Given reach, the miss is larger (up to 0.085 for φ ≤ 0.8 and 0.136 at φ = 0.9 in cells with reach ≥ 0.10), because IF5 screens high-dispersion windows, not slow drifts (8.1b, 8.5c) | MINOR (disclosed) |
| 41 | (added, M1) the frozen 5-date-block surfaces (T1a, NEG, U_W) carry the same persistence defect | Cycle 1: not repaired (T1a up to 0.089, NEG 0.070, U_W miss 0.0765 on run G). **Resolved by D4-C3-M2 (Astra M2):** T1a / NEG / U_W use the calibrated construction of 8.1c; over 𝒟_P* T1a ≤ 0.0198, NEG ≤ 0.0106, U_W miss ≤ 0.0089 (100,000-replication confirmations inside 0.025 / 0.025 / 0.05) | — (cost: item 46) |
| 42 | (added, M1) the information floor or a dominant date breaks the new bound | Refuted. The bound is always defined when INFO_SUFFICIENT (df_30 ≥ 1). Boundary designs: worst joint miss 0.0381 (one 96-trade date, φ = 0.9). At 60 dates / 25 stations it is valid but nearly powerless (0.001 (m = 17, thin) and 0.005 (m = 35, full), against 0.143 / 0.366 for the R3 engine), which is disclosed | MINOR (disclosed) |
| 43 | (added, M2 cycle 2) the cycle-1 level held only on one simulated grid (Astra M1-R) | *Cycle-2 text; its class wording "CORE prices to 0.90" and its λ are SUPERSEDED by item 50 (Astra M3).* **Resolved by D4-C3-M2**: one completely stated class 𝒟_P* (8.1c) containing favourite CORE prices (U(0.70, 0.90)), ≤ 30 paused dates (random or contiguous), truncated windows, two-state and trailing-mean (incl. the literal 30-date §9 mechanism) regimes; λ_θ / λ_κ calibrated over all 1,183 reached cells with an 80% target margin; worst cells confirmed at 100,000 (L_W 0.0415 [0.0403, 0.0427]) | MINOR (a class is never exhaustive; outside 𝒟_P* no level is claimed, e.g. φ 0.97 with favourites 0.0486, item 47) |
| 44 | (added, cycle 2) λ chosen by searching until one cell just passes | Refuted. Family, grid, class, targets (0.040 / 0.020) and the confirm-or-move-up rule were in the run-H header before any run; the only pre-run activity was a 4,000-replication engine pilot of Astra's cells. λ is the smallest grid value meeting the criterion in **every** cell; all failed members and three comparators are published (8.1c). Sub-family λ values are published as disclosure, not used | — |
| 45 | (added, cycle 2) U_W and the headline interval disagree (Astra M2 second-order) | Resolved: the headline interval is `[L_W, U_W]`, so LOSS_CONFIRMED ⟺ the interval lies below 0; joint non-coverage ≤ 0.0429 (stated level ≥ 0.90) | — |
| 46 | (added, cycle 2) the calibration destroys power | **Not refuted; disclosed as a feasibility consequence.** Cycle 2: P(T2) at θ_PCE 0.07–0.11; 80%-power effect ≈ 0.18; T1a MDE80 ≈ 0.11 per share; NEG power ≈ 0.12 at −0.07 per share. D4-C3-P1 (λ_θ 2.15, λ_κ 1.80): the 80%-power effect is 7.2 × SE0_θ (≈ 0.21 mid-price at m 17 to ≈ 0.05 near-cap favourites at m 55); NEG power at −0.07 is 0.06–0.25 at m 17 and ≤ 0.44 jointly over every declared design; the gate is recalibrated to this (item 49) and no design passes it (item 52). EXPERIMENT_FEASIBILITY is Astra's / governance's call (27) | MAJOR for feasibility (not a validity defect; for Astra / governance) |
| 47 | (added, cycle 2) levels outside the class or given reach | Disclosed: outside 𝒟_P* (φ 0.95 / 0.97, 60-date trailing mean, rv 0.20) the calibrated L_W stayed ≤ 0.0494 in run H at λ 1.70 (higher λ is wider), but no level is claimed; given reach (cells with reach ≥ 0.10) the **grid** figures are L_W miss up to 0.148, T1a 0.121, NEG 0.044, U_W 0.021 at the adopted constants (8.1d; cycle 2: 0.182 / 0.069 / 0.065 / 0.054 at λ 1.70 / 1.60), and the grid is not a maximum (Astra's off-grid cell reached 0.203 at the cycle-2 λ, 0.086 at the adopted λ; m13); sentence (c) now says "counted jointly with reaching an evaluated state" (m11) | MINOR (disclosed) |
| 48 | (added, cycle 2) T1b untested under persistence (Astra proof gap) | Closed by measurement: T1b ≤ 0.0077 over the 𝒟_P* TAIL designs; T1 ≤ 0.0078 at λ_κ 1.80 (8.1c, 8.1d) | — |
| 49 | (added, cycle 3, Astra P1) GO / θ_PCE / SE_KAPPA_CEILING keep a rationale the calibrated tests contradict | **Resolved by D4-C3-P1 option (a)**: Z_80 → Z_EFF = 7.2 and SE_KAPPA_CEILING 0.020 → 0.005, both derived by a synthetic rule declared and committed before the run (10.4); both only stricter; GO's meaning is not redefined. Measured: P(T2 at the design's own θ_PCE) 0.976–1.000 (old formula 0.014–0.51); NEG ceiling certifies ≥ 0.90 power at −0.07 per share for any design below it | — (cost: item 52) |
| 50 | (added, cycle 3, Astra M3) the level text "CORE prices to 0.90" exceeds the calibrated class | **Resolved by D4-C3-P1 option (i)**: class enlarged to U(0.80, 0.90), U(0.85, 0.90), a point mass at 0.89 and two-point mixtures; λ_θ 2.15 / λ_κ 1.80 selected by a declared mechanical rule over 1,288 cells; worst L_W miss 0.0397 [0.0385, 0.0409], T1a 0.0190 [0.0182, 0.0199] at 100,000; Astra's cells 0.0312 [0.0302, 0.0323] / 0.0167; the class is printed as the enumerated laws, never as "CORE prices to 0.90"; nearby laws and a point mass at 0.899 probed (≤ 0.0411, 8.1d) | MINOR (the extremality of the point mass 0.89 is empirical; a class is never exhaustive; no level is claimed for a price law not enumerated) |
| 51 | (added, cycle 3) the gate constants were chosen to give a convenient answer | Refuted: the procedure (laws, grids, interpolation, rounding, verification, move-up-never-down) was written into `ARCHITECT_PROGRESS_CYCLE3.md` and committed (03640425) before any run of run J; constants are mechanical outputs (summariser `p1derive`); the Architect had seen Astra's "about 5.0" and its NEG power before declaring and the result (7.2, 0.005) is far stricter than that, i.e. not tuned toward a desired GO | — |
| 52 | (added, cycle 3) V2 is NO_GO for every declared design | **Not refuted; stated as the central feasibility finding (1, 10.3, 10.4, 24, 27).** GO_new = 0 on every declared price law at every throughput 8–96 trades per date, because the NEG clause cannot be met (smallest SE0_κ ≈ 0.0070 > 0.005; joint NEG power at −0.07 ≤ 0.44). The missing negative-result instrument at 120 dates over 𝒟_P* is fundamental for feasibility (Astra's oracle benchmark); W and every owner-frozen surface are untouched; reported to the owner at loop end | MAJOR for feasibility (not a validity defect; for the owner / governance) |
| 53 | (added, cycle 3) the single multiplier over-certifies favourites and the θ-side clause is not the whole of GO | Disclosed: Z_EFF is the maximum over laws, so favourite-concentrated designs that pass the θ-side clause have T2 power ≈ 1 at their θ_PCE (0.80 targeted); a law-specific multiplier would loosen some designs and is not stricter-only. The θ-side clause alone is not GO (item 52) | MINOR (disclosed) |

No CRITICAL issue survives. One MAJOR feasibility consequence (items 46 and 52: no declared design passes GO; no usable negative-result instrument at 120 dates) is handed to Astra / the owner; it is not a validity defect.

---

## 22. Post-t0 mutation policy

Before t0: scientific repairs are allowed only if outcome-blind, documented, re-frozen with new hashes, and independently re-audited. After t0: any material change to signal, cohort, STATION_TABLE, estimand, strata, thresholds, PCE, inference engines, dependence declaration, seeds, execution models, capture contract, completeness rules, mechanics rules, terminal logic or analysis time **creates a new experiment**; the running window is closed as INVALID_PARAMETER_MUTATION if the change touched it, and nothing is repaired retroactively. Engineering fixes that provably leave every archived decision and every analysis output byte-identical (replay proves it) are not material.

---

## 23. Unchanged V1 elements carried explicitly

Economic accounting and full ledger (V1 §11); settlement controls, anomaly flag, per-station 20% cap (§20); access fields (§21); survivorship cohort (§23, descriptive); exploratory family E1–E15 with Holm (§15; E8 now uses the tick-aware CONSERVATIVE model; E13/E14 are now populated); anti-leakage invariants 1–10, 12–20 (§24) — invariant 11 is replaced by section 12.3 and invariants 21–24 are added in section 25.

---

## 24. What V2 can and cannot conclude

Can: whether R*'s chosen legs are underpriced net of executable costs, in the core and in the tail, at levels attained over 𝒟_P* (8.1c); a real negative result is **not attainable at 120 dates over 𝒟_P*** (D4-C3-P1: NEG power at −0.07 per share is 0.06–0.25 at m 17 and ≤ 0.44 jointly over every declared design, against the ≈ 0.9 the design gate once assumed; only a large core overpricing, |κ| ≳ 0.12–0.15 per share at m 17, would be rejected with 90% power), and the positive information test T1a needs a core underpricing of about 0.11 per share or more (cycle-2 figure at λ_κ = 1.60; larger at 1.80); whether the trades R* executed in the window had positive expected net value, with θ̂ ≥ θ_ERT (T2 on θ_W with the calibrated bound of 8.1c, size ≤ 0.05 jointly with reach over the completely stated class 𝒟_P*; θ_PCE is computed with the effective multiplier Z_EFF = 7.2 of the T2 actually run, so the simulated power of T2 at θ_PCE is ≥ 0.976 in every design that passes the θ-side clause (cycle 2: 0.07–0.11 with Z_80; cycle-1 0.47–0.55, R3 engine 0.67–0.78); in practice only effects ≳ 0.15–0.21 (mid-price designs) or ≳ 0.05–0.10 (favourite-concentrated designs) are confirmable, and **no declared design passes GO, so V2 as specified cannot start (10.4)**); how much adverse future cost mass that evidence could absorb (transport frontier ε*, 8.5c); an interval for θ with its core/tail decomposition; an assumption-free upper bound on the realised-window value θ_W of the trades actually executed; the information actually collected; operability at small capital.

Cannot: confirm θ in [0.02, θ_PCE); establish or exclude prospective net value unconditionally (8.5b ceiling ≈ 0.06; 8.5c mirror theorem); certify that a future epoch satisfies the transport premise; reject R* as a net strategy; exclude realised-window value whenever `M_tail` keeps U_W above the threshold (in practice: any sub-cent leg held at S_ref); reject R* economically from core information alone; attribute an edge to NWP information rather than structure beyond the descriptive baselines; say anything about the venue after a mechanics change.

---

## 25. Builder schema and invariant deltas (additions to V1 §22 / §24)

SIGNAL_DECISION adds `phase ∈ {PRE_T0, FORWARD}`, `stratum ∈ {CORE, TAIL}`, `best_ask_chosen`, `q_chosen`, `bias_window_dates[30]`, `bias_span_days`, `bias_contaminated`. ORDER_BOOK_SNAPSHOT adds `request_sent_at`, `http_status`, `method`, `attempt_no`, `valid_capture`, `invalid_reason`, `tick_size_recorded`, `book_age_ms`. EVENT adds `reason_family`, `mechanics_code`, `unit`, `bucket_lo[11]`, `bucket_hi[11]`. SETTLEMENT adds `first_observed_final_at`. CAPITAL_USAGE adds `alloc_hash`. New table READINESS (per station-kind-date: BIAS_N, BIAS_SPAN, READY flags) and PHASE_LOG (GLOBAL_READY per date, OP dates, t0, D_0, pauses, counted dates, mechanics events).

Added invariants: **21 `PRE_T0_OUTCOME_BLIND`** — no PRE_T0 decision is joined to a settlement or payout; **22 `ANALYSIS_TIME_LOCK`** — no forward P&L / κ / θ / win-count computation before ANALYSIS_TIME outside synthetic tests; **23 `STRATUM_AT_DECISION`** — stratum stored at decision time, never recomputed; **24 `CAPTURE_TIME_WINDOW`** — replaces invariant 11 with section 12.3.

---

## 26. Builder contract

Builder may decide: languages, storage engines, process layout, scheduling mechanics, retry implementation within 12.2, test design, dashboards.

Builder may **not** decide (all frozen here and in the manifest): estimands, strata, cohort, °F arithmetic, station-table membership, thresholds, PCE formula (including Z_EFF) and ceilings (including SE_KAPPA_CEILING), power claims, inference engines, dependence declaration, seeds and draw order, terminal labels and their order, readiness and GLOBAL_READY, OP length, t0, capture windows and validity, completeness definitions, allocation order, mechanics semantics, analysis time, sensitivity list.

Verification required before a t0 request (in addition to V1 §28): unit tests for the four title regexes and E4 (°C and °F, negative temperatures, malformed titles); interval arithmetic against hand-computed q for a 2 °F ladder; CONSERVATIVE tick rule in both regimes; VALID_CAPTURE with a quiet book (old exchange timestamp) and with a future timestamp; completeness denominator; USABLE / BIAS_HISTORY_READY with a correction hold and a missing vintage; the two-way CR engine against a hand-worked 3 × 3 example including a negative `V_2w`; PINM reproducibility (same seed → identical p-values); `M_tail` and `EXCLUSION_BLOCKED_BY_TAIL` against hand-worked examples (empty tail, one 0.001 leg, several 0.039 legs); REALIZED_WINDOW_BOUND ordering; PROSPECTIVE_EXCLUSION / PROSPECTIVE_CONFIRMATION constants printed and R*_REJECTED_AS_NET_STRATEGY never TRUE in any synthetic run; L_W, ε*(δ, τ) grid, k*(H) grid, ε_1(H) and n_eff,C against hand-worked examples (L_W ≤ 0, L_W = 0.10, a single cap-date window); the multi-block L_W of 8.1b against a hand-worked example with 5-, 10-, 20- and 30-date calendar blocks, including df_30 = 1 on a 60-date window and a paused date inside a block, plus the property L_W ≤ the 5-date-block bound; the D4-C3-P1 constants λ_θ = 2.15 and λ_κ = 1.80 applied to L_W, U_W's core term, T1a and NEG (8.1c, 8.1d); θ_PCE with Z_EFF = 7.2 and the GO clause SE0_κ ≤ 0.005 against hand-worked OP examples (10.2, 10.3, 10.4) against hand-worked examples, with IF4 / IF5 still on 5-date blocks, and the headline interval `[L_W, U_W]` with LOSS_CONFIRMED ⟺ upper end < 0; SHADOW_CONTINUATION_SIGNAL truth table; TAIL_ARRIVAL_REPORT bins including zero counts; the 11-value SCIENTIFIC partition; adverse imputation; every row of every state table reachable in a synthetic test; PRE_T0 outcome-blind and ANALYSIS_TIME_LOCK enforcement; restart/replay idempotence (no duplicated fills, P&L or sessions after crash and replay).

---

## 27. Status

```text
WEATHER_FORWARD_SPEC_V2                  = AUDITED @94b59348 (immutable ancestor of this commit)
ASTRA_WEATHER_V2_REAUDIT                 = BLOCKED_D4_STRUCTURED_BOUND_FALSE_ECONOMIC_EXCLUSION   (Astra @7d95c00)
WEATHER_FORWARD_SPEC_V2_D4_REPAIR        = R1 @24d2342 → BLOCKED_D4_PROSPECTIVE_ESTIMAND_UNSAMPLED_TAIL_FALSE_EXCLUSION (Astra @3d18085)
WEATHER_FORWARD_SPEC_V2_D4_C2_REPAIR     = R2 @e45d2ce7 → BLOCKED_D4_PROSPECTIVE_CONFIRMATION_UNSAMPLED_LOSS_REGIME_FALSE_CONFIRMATION
                                           (Astra @92c2f706; R2 exclusion removal PASS, R1 θ_W bound PASS, state machine PASS)
WEATHER_FORWARD_SPEC_V2_D4_C3_TRANSPORT_REPAIR = R3 @341e0b7a → BLOCKED_D4_R3_SOURCE_BOUND_UNDERCOVERAGE_CROSS_BLOCK_PERSISTENCE
                                           (Astra @5bb57eb2; R1 / R2 / C3 removal / transport bound / frontier / semantics / state machine PASS; M1 MAJOR; m8, m9)
WEATHER_FORWARD_SPEC_V2_D4_C3_M1_REPAIR  = cycle 1 @4423c5c3 → BLOCKED_D4_M1_SOURCE_BOUND_LEVEL_NOT_ATTAINED_OVER_DECLARED_CLASS_AND_FROZEN_SURFACE_UNDERCOVERAGE
                                           (Astra @ac777a87: M1-R, M2 MAJOR; m10, m11; T1b proof gap; R1 / R2 / R3 surfaces PASS)
WEATHER_FORWARD_SPEC_V2_D4_C3_M2_REPAIR  = cycle 2 @61f4904f → BLOCKED_D4_M2_GO_GATE_CONTRADICTED_BY_CALIBRATED_POWER_AND_LEVEL_EXCEEDED_AT_FAVOURITE_PRICE_CONCENTRATION
                                           (Astra @8874dc54: P1, M3 MAJOR; m12, m13; M1-R / M2 repaired on the enumerated grid, independently verified;
                                           R1 / R2 / R3 surfaces PASS)
EXPERIMENT_FEASIBILITY_V2                = BLOCKED_POWER_NEGATIVE_RESULT_INSTRUMENT_INFEASIBLE_AND_T2_POWER_BELOW_FROZEN_GO_RATIONALE
                                           (Astra's, on 61f4904f; unchanged until Astra rechecks; this candidate does not change it)
WEATHER_FORWARD_SPEC_V2_D4_C3_P1_REPAIR  = READY_FOR_ASTRA_RECHECK
D4_C3_P1_REPAIR                          = P1 option (a) (10.4): outcome-free, stricter-only recalibration of the design gate to the tests actually run:
                                           Z_80 = 2.4865 → Z_EFF = 7.2 in θ_PCE; SE_KAPPA_CEILING 0.020 → 0.005; both derived by a rule declared and
                                           committed before the run (03640425); measured: P(T2 at the design's own θ_PCE | θ-side GO, INFO) 0.976–1.000
                                           (old formula 0.014–0.51); GO's meaning unchanged.
                                           M3 option (i) (8.1d): class 𝒟_P* enlarged to U(0.80, 0.90), U(0.85, 0.90), a point mass at 0.89 and two-point
                                           mixtures; λ_θ 1.70 → 2.15, λ_κ 1.60 → 1.80 (smallest grid values meeting the declared criterion over 1,288
                                           cells; cycle-2 λ fails: 0.0568 [0.0554, 0.0583] at U(0.85, 0.90)); stated levels (joint with reach, over 𝒟_P*)
                                           unchanged (L_W miss and size ≤ 0.05, U_W miss ≤ 0.05, T1a / NEG / T1b ≤ 0.025, T1 ≤ 0.05, headline ≥ 0.90);
                                           measured worst 0.0397 [0.0385, 0.0409] / 0.0253 (0.0240 [0.0231, 0.0250] at 100,000) / 0.0034 / 0.0199
                                           (0.0190 [0.0182, 0.0199]) / 0.0073 / 0.0077 / 0.0078 / headline non-coverage 0.0397; "CORE prices to 0.90" is
                                           no longer printed as a class. m12 (stale "well-powered", item 1) and m13 (grid figure) fixed.
GO_STATUS_ON_DECLARED_LAWS               = NO_GO_KAPPA_UNDERPOWERED for every declared design (GO_new = 0 on every price law at every throughput 8–96
                                           trades per date; smallest SE0_κ ≈ 0.0070 > 0.005; joint NEG power at −0.07 ≤ 0.44) — a measured design-gate
                                           finding, not a strategy result
FEASIBILITY_FINDING (for Astra and the OWNER; not a validity defect; NOT repaired; W and every owner-frozen surface untouched)
                                         = the missing negative-result instrument at 120 counted dates over 𝒟_P* is fundamental (oracle benchmark); V2 as
                                           specified cannot start on any declared design; options are a longer horizon, an outcome-blind narrower class
                                           justified by non-outcome evidence, a different design (V3), or retirement — governance / resource decisions
D4_C3_M2_REPAIR (cycle-2 record; λ, class and gate meaning SUPERSEDED IN PART by D4_C3_P1_REPAIR)
                                         = option (a) for M1-R and M2 (8.1c): one calibrated construction
                                           stat ∓ λ · max_{b∈{5,10,20,30}} t_{df_b,q} SE_2w(b) for L_W (q 0.95, λ_θ = 1.70), U_W's core
                                           (q 0.975, λ_θ), T1a / NEG (q 0.975, λ_κ = 1.60); class 𝒟_P* completely stated (8.1c) incl.
                                           favourite CORE prices to 0.90, ≤ 30 paused dates, 60–120 counted dates, AR(1) / two-state /
                                           15- and 30-date trailing-mean (§9 mechanism) / hemisphere / station regimes, latent var ≤ 0.10;
                                           stated levels (joint with reach, over 𝒟_P*): L_W miss and T2 size ≤ 0.05, U_W miss ≤ 0.05,
                                           T1a ≤ 0.025, NEG ≤ 0.025, T1b ≤ 0.025, T1 ≤ 0.05, headline [L_W, U_W] ≥ 0.90; measured worst
                                           0.0415 [0.0403, 0.0427] / 0.0353 / 0.0089 / 0.0198 / 0.0106 / 0.0077 / 0.0089 / 0.0429 non-coverage;
                                           IF4 / IF5 / GO / constants other than λ unchanged; m10 (stale wording, §2 rows) and m11
                                           (sentence (c) joint-with-reach qualifier) fixed; T1b measured under persistence
FEASIBILITY_CONSEQUENCE (cycle-2 record; superseded by FEASIBILITY_FINDING above)
                                         = calibrated V2 was nearly powerless: P(T2) at θ_PCE 0.07–0.11, 80%-power effect ≈ 0.18,
                                           T1a MDE80 ≈ 0.11 per share, NEG power ≈ 0.12 at −0.07 per share; GO / θ_PCE / SE_KAPPA_CEILING
                                           were not retuned then (Astra @8874dc54: that contradicted the gate's rationale; repaired by D4_C3_P1_REPAIR)
WEATHER_FORWARD_SPEC_V2_D4_C3_M1_REPAIR (cycle-1 record, superseded by the D4-C3-M2 lines above)
                                         = option (a), calibrate: T2's source bound L_W = θ̂ − max_{b∈{5,10,20,30}} t_{df_b,0.95} SE_2w(b)
                                           (8.1b; never above the R3 bound); stated level P(reach ∧ L_W > θ_W) ≤ 0.05 over the
                                           5-date-block model and the declared persistence class 𝒟_P (daily AR(1) φ ≤ 0.9, latent
                                           variance ≤ 0.10, m ∈ {17, 35}, thin / full fills); none claimed outside 𝒟_P; power cost and
                                           θ_PCE shortfall disclosed, not retuned; m8 (frontier domain guard) and m9 (SUPERSEDED markers) fixed
                                           (open observation T1a / NEG / U_W on 5-date blocks: CLOSED by D4-C3-M2)
WEATHER_FORWARD_SPEC_V2_D4_C3_TRANSPORT_REPAIR (history) = READY_FOR_ASTRA_D4_C3_RECHECK at 341e0b7a (superseded by the line above)
D4_C3_REPAIR                             = R3 = hybrid C3_C (no unconditional prospective label in either direction) + C3_A (cost-mass transport
                                           class 𝒯_H(ε, δ), deductive bound L_T = (1 − ε)(L_W − δ) − ε, frontier ε*(δ, τ), k*(H), concentration,
                                           observable invalidation that can only revoke); ECONOMIC_RESULT = REALIZED_WINDOW_VALUE_{SUPPORTED,
                                           NOT_ROBUST, INDETERMINATE} on θ_W with T2 unchanged (its source bound recalibrated by D4-C3-M1, 8.1b);
                                           SHADOW_CONTINUATION_SIGNAL replaces the forward
                                           signal; no ε / δ / H / τ threshold chosen in V2
MINORS m3–m7                             = fixed (manifest §C superseded markers; checkpoint §4; REALIZED_WINDOW prefix note; D_obs ≈ 174;
                                           "not usefully testable" wording)
D4_R1 / D4_R2                            = KEPT (θ_W upper-bound structure and M_tail unchanged — its core term calibrated by D4-C3-M2, 8.1c; no
                                           prospective exclusion; no R* rejection)
CARRIED CLOSED                           = D1 D2 D3 D5 D6 D7 D8 D9 D11 D12 CLOSED; D10 CLOSED_ACCEPTED_AND_DISCLOSED (11-value partition unchanged
                                           in structure; economic labels renamed; D1 power and D8 engine for T2, U_W, T1a and NEG re-qualified by D4-C3-M1 / D4-C3-M2)
NOT_MEANING                              = EXPERIMENT_FEASIBILITY = PASS / BUILDER_AUTHORIZED / t0 / edge / capital
NEXT_AUTHORIZED_ACTION                   = ASTRA BOUNDED D4-C3-P1 RECHECK ONLY (P1 gate meaning vs simulated power over the declared laws; M3 levels at U(0.85, 0.90) and the enlarged class; m12, m13; R1 / R2 / R3 and D1–D12 regression), then the FEASIBILITY finding to the owner
BUILDER_AUTHORIZED                       = FALSE
REAL_CAPITAL_AUTHORIZED                  = FALSE
LIVE_TRADING_AUTHORIZED                  = FALSE
t0                                       = NOT_DECLARED
```
