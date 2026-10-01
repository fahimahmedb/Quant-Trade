# WEATHER FORWARD — V1 → V2 DELTA — 2026-09-29

```text
V1     = claude/intelligent-gates-msidml @ 726070a199957a6fc05515ebb3027e945028fddc  (immutable; unchanged in this branch)
ASTRA  = claude/dreamy-franklin-1vki4t  @ e1cf4ca0851eace2912ce8a9bcd4a8400ebf4250  (immutable)
FABLE  = claude/zen-einstein-9moyry     @ 5760ffa5b5da2a988cfe6d1503c86c561acf9b1f  (immutable, advisory)
V2     = WEATHER_FORWARD_FALSIFICATION_SPEC_V2_2026-09-29.md (+ manifest, state, power table, synthetic sim); audited @94b59348
V2-R1  = D4 repair R1 after Astra V2 re-audit @7d95c00abccfbc805c0d8abca65a6b93268741a2 (section D4.d / D4.e)
V2-R2  = D4 repair R2 after Astra D4 recheck @3d18085862f239a81936345989b4e26414cedcf3 (section D4-C2; D4.d / D4.e kept as the R1 record)
V2-R3  = D4 repair R3 after Astra D4-C2 recheck @92c2f706d2ac75af9ae9710061c60df520234410 (section D4-C3; D4-C2 kept as the R2 record)
V2-R3-M1 = D4-C3-M1 source-bound calibration after Astra D4-C3 recheck @5bb57eb2adf4cff35378f2c0e53e0316d45a4229 (section D4-C3-M1; D4-C3 kept as the R3 record)
SUMMARY: OUTCOME_INFORMATION_USED = FALSE for every item · TRADING_RULE_CHANGED = FALSE for every item ·
         EXECUTION_MODEL_CHANGED = TRUE for one item (X1, CONSERVATIVE only) · COHORT_CHANGED = TRUE for one item (D7)
```

Each block: OLD / NEW / WHY / ASTRA_FINDING / FABLE_RECOMMENDATION / ARCHITECT_DECISION / OUTCOME_INFORMATION_USED / TRADING_RULE_CHANGED / EXECUTION_MODEL_CHANGED / BUILDER_IMPACT.

---

## D1 — Power / effect-size architecture (CRITICAL → CLOSED)

**D1.a Thresholds**
- OLD: single θ_MEUE = 0.02 used as the economic threshold, the REJECTED threshold (U95 < 0.02) and a FORWARD_SIGNAL criterion; power statement "≥ 1,000 trades, SE ≈ 0.05".
- NEW: θ_ERT = 0.02 (economic relevance, reporting threshold, not powered); θ_PCE by a frozen price-implied formula populated in an outcome-free observation phase; PCE_CEILING = 0.10 and SE_KAPPA_CEILING = 0.020 as a pre-t0 GO/NO_GO; the band [θ_ERT, θ_PCE) is declared unresolved.
- WHY: confirming or excluding 0.02 needs SE ≤ 0.008 (≈ 15,500 independent trades at σ = 1), ≈ 1,340 dates at 35 trades/day; 120 dates hold ≈ 1,100–2,400 effective trades.
- ASTRA_FINDING: D1 CRITICAL; MDE 0.06–0.10 (0.15–0.25 with lottery legs).
- FABLE_RECOMMENDATION: Family B two-threshold labels; PCE from pre-t0 prices; PCE ceiling (CD11).
- ARCHITECT_DECISION: adopted; ceiling fixed at 0.10 = 5 × θ_ERT = lower end of V1's own disclosed confirmable range.
- OUTCOME_INFORMATION_USED: FALSE (prices, depth and counts only). TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE.
- BUILDER_IMPACT: implement the OP computation (spec §10.2) and the GO/NO_GO report; no scientific choice.

**D1.b Architecture**
- OLD: fixed 60/90/120-date window, one primary test on θ, percentile date-block bootstrap.
- NEW: Family D + B hybrid: θ (economic) and a stratified information axis (κ_core, tail win count) tested in **parallel**; fixed 120 counted dates; no interim.
- WHY: the only design with a real negative result at 120 dates that is immune to lottery-leg variance on the information axis and honest about the unresolved band.
- ASTRA_FINDING: D1 minimum closure option (a) "declare the estimand the design can test".
- FABLE_RECOMMENDATION: Family D with fixed-sequence gatekeeping (θ only after the information gate).
- ARCHITECT_DECISION: Family D **without the gate** (D1-GATE). SIMULATED: an edge concentrated in the cheapest legs (true θ = 0.44) is seen by the θ engine 0.535–0.61 of the time, but only 0.21–0.30 of runs would pass a count-based gate (runs A/B); joint claims are controlled by intersection-union instead. Families A and C rejected (spec §4).
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE.
- BUILDER_IMPACT: stratum field at decision time; κ_core, W_tail, Λ_tail computations; product state machine.

## D2 — Terminal state machine (CRITICAL → CLOSED)

- OLD: five labels evaluated in order, with gaps S1–S4, ambiguities S5–S6, misleading precedence S7–S8 (Astra §9) and an unpinned 90/120 analysis date.
- NEW: VALIDITY (8 ordered rows) × SCIENTIFIC (NOT_EVALUATED | INFORMATION_INSUFFICIENT | INFORMATION_RESULT × ECONOMIC_RESULT = 3 × 4) × OPERABILITY (6 ordered rows); report fields ECONOMIC_BOUND, INFO_SOURCE, CORE_ADVERSE; forward-signal and rejection rules defined on the axes; one ANALYSIS_TIME = D_120 + 10 days.
- WHY: every axis is an ordered list ending in "otherwise", so each is a total, mutually exclusive partition by construction.
- ASTRA_FINDING: D2 CRITICAL.
- FABLE_RECOMMENDATION: six-label partition + orthogonal VALID / ACCESSIBLE.
- ARCHITECT_DECISION: **modified** — Fable's six labels are six of V2's twelve product cells; the economic column is also evaluated when no information is detected; INFORMATION_INSUFFICIENT added; relevance exclusion ordered before confirmation (a positive but irrelevant θ is never "confirmed").
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE.
- BUILDER_IMPACT: implement three ordered tables exactly; synthetic tests must reach every row.

## D3 — Book timestamp / observation contract (CRITICAL operational → CLOSED)

- OLD: E6 / invariant 11 `book_timestamp ∈ [T_entry − 5 min, T_entry]` for 22 tokens.
- NEW: window on `captured_at ∈ [T_entry − 300 s, T_entry]`; `exchange_book_timestamp ≤ captured_at + 2 s`; no lower bound; retries every 20 s; per-token last valid capture; provenance fields; NTP ≤ 250 ms; completeness = complete / entry-expected (E1–E5, E7, E8 true).
- WHY: the CLOB `timestamp` is the book's last change; ≈ 28–33% of weather tokens are quiet for > 5 min (Astra X3); a quiet book is a valid book.
- ASTRA_FINDING: D3. FABLE_RECOMMENDATION: test on captured_at (Fable §5.2 GR condition).
- ARCHITECT_DECISION: adopted with exact windows, tolerance and denominator.
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE (same book, correctly timed).
- BUILDER_IMPACT: capture scheduler, retry loop, VALID_CAPTURE predicate, new snapshot fields, invariant 24.

## D4 — Heavy-tail inference (MAJOR → CLOSED)

**D4.a Estimand layer**
- OLD: θ only; per-trade SD assumed 1.2.
- NEW: θ unchanged and never winsorised; price strata (TAIL iff chosen best ask < 0.04, frozen constant); κ_core and λ_tail information estimands; θ_core / θ_tail decomposition reported.
- WHY: θ's ratio-of-means weights each leg's surprise by shares (a 0.001 leg carries ≈ 600× the weight of a 0.6 leg); no resampling method represents unobserved 1,000× wins.
- ASTRA_FINDING: D4 MAJOR. FABLE_RECOMMENDATION: κ_core + W_tail vs Λ_tail, strata by the tick regime.
- ARCHITECT_DECISION: adopted; κ uses all-in executable cost (net per share); strata by price, not by the live tick field (MEASURED: tick is market-level, shared by YES and NO; 1,550 / 2,981 markets at 0.001).
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE.
- BUILDER_IMPACT: `stratum`, `best_ask_chosen`, `q_chosen` stored at decision time (invariant 23).

**D4.b Engines**
- OLD: moving-block percentile bootstrap over dates (primary).
- NEW: two-way cluster-robust t (max-of-three SE, df = min(G_B, G_S) − 1) primary for κ_core, θ_core, θ; PINM (declared copula ρ = 0.10 / 0.10 / 0.10, B = 20,000, fixed seed) gating only the tail count (T1b) and the tail part of the upper bound; PINM on θ and κ reported; percentile bootstrap a sensitivity row.
- WHY (SIMULATED): PINM with a declared (not oracle) dependence is either anti-conservative (Fable: 0.13–0.21) or power-destroying (core-only θ = 0.10: 0.73–0.755 vs 0.855–0.91 for CR); CR is conservative for positive θ claims when tails are present (null 0.000–0.020); rare-event counts are nearly insensitive to the declared dependence.
- ASTRA_FINDING: D4 (studentised / BCa / stratified). FABLE_RECOMMENDATION: PINM primary + two-way studentised bootstrap, reject only if both reject.
- ARCHITECT_DECISION: **modified** — engines assigned by domain of validity; no agreement requirement.
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE.
- BUILDER_IMPACT: CR engine; PINM with exact seed and draw order; bisection for λ_U, μ_U.

**D4.c Exclusion bound** — *SUPERSEDED by D4.d (repair R1); kept as the record of V2@94b5934*
- OLD: U95 of the percentile bootstrap used for REJECTED.
- NEW: structured bound `U(θ) = w_core U_core + w_tail max(θ^TPM, θ^SHR)`, tagged MODEL_CONDITIONAL_TAIL.
- WHY (SIMULATED): naive pooled U95 covers 0.79–0.91 with lottery legs; the structured bound ≥ 0.945 except in a deliberately adversarial hidden-lottery scenario (disclosed as a MAJOR non-blocking limitation).
- ASTRA_FINDING: D4. FABLE_RECOMMENDATION: not specified (Fable §4.2 documented the false-exclusion problem).
- ARCHITECT_DECISION: new; exclusions are model-conditional and labelled.
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE.
- BUILDER_IMPACT: implement spec §8.5 exactly.

**D4.d D4 REPAIR R1 — exclusion bound and rejection rule (after Astra V2 re-audit @7d95c00; delta V2@94b5934 → V2-R1)**
- OLD (V2@94b5934): `U(θ) = w_core U_core + w_tail max(θ^TPM(λ_U), θ^SHR(μ_U))`, tail term from the observed win count under two ASSUMED tail models, tagged MODEL_CONDITIONAL_TAIL; rule 17.6 rejected R* as a net strategy on `NET_VALUE_EXCLUDED` **or** on `NEGATIVE_INFORMATION ∧ ECONOMIC_RESULT ≠ NET_VALUE_CONFIRMED`.
- NEW: `U(θ) = w_core U_core + M_tail`, `M_tail = Σ_TAIL (n_j − C_j) / Σ C_j` (every TAIL leg wins) — the identified-set supremum over the full admissible tail class (all `p ∈ [0,1]`, any dependence); TPM / SHR retired from every role; PINM gates only T1b; rule 17.6: `R*_REJECTED_AS_NET_STRATEGY` iff `NET_VALUE_EXCLUDED`, and `NEGATIVE_INFORMATION` is reported as the information-level `R*_CORE_INFORMATION_REJECTED`; report fields `M_tail`, `w_core·U_core`, `EXCLUSION_BLOCKED_BY_TAIL`; OP readiness report adds the descriptive TAIL_MAX_CONTRIBUTION.
- WHY: coverage of the new bound is at least the core CR coverage for every tail geometry (proof in spec §8.5). Run D (fresh seeds, exact frozen contract for the retired bound) reproduces both Astra attacks — positive-tail / negative-core, true θ = 0.0315: retired coverage 0.8885, false ERT exclusion 0.0742, false economic rejection 0.320 (mostly through the NEG clause); pure hidden lottery, true θ = 0.0852 > θ_PCE = 0.08: retired coverage 0.8632, false LARGE exclusion 0.1126 — and gives coverage 1.0 and zero false exclusions or rejections under the repair. Over nine adversarial core geometries the repaired bound covers 0.9705–0.993 with false ERT exclusion 0.019–0.0295.
- Routes evaluated (spec §8.5; power table §4.5): **A** (remove exclusion when tail exposure is material) needs an arbitrary materiality threshold and still a valid bound below it — subsumed by the continuous `M_tail`; **B** (partial identification over the full class) — adopted in its assumption-free form; a count-tightened version needs a dependence assumption and, under arbitrary dependence, collapses to ≈ (1 − α) Σ n, so it buys nothing valid; **C** (stricter pre-t0 tail admissibility) cannot work: a price condition on the OP does not restrict true tail probabilities, and Astra's attack puts the sub-cent legs after a GO observation phase; **D** (other) — none smaller is valid.
- COST (disclosed): exclusion is unattainable whenever sub-cent legs are held at S_ref (P3 in run D: true θ = −0.098 with 2 sub-cent legs, retired ERT exclusion 0.38, repaired 0.00); tail-free runs keep full exclusion power (0.51 at θ = −0.05, 0.93 at θ = −0.10).
- ASTRA_FINDING: V2 re-audit C1 CRITICAL and MP1. FABLE_RECOMMENDATION: — (Fable proposed PINM tail inference, not a full-class bound). ARCHITECT_DECISION: R1 as above.
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE. D2 partition unchanged (14 values; only the E1 bound and rule 17.6 changed).
- BUILDER_IMPACT: compute `M_tail` from fills (no simulation, no bisection); drop the TPM / SHR implementation; implement the two rejection labels.

**D4.e MP1 — simulation contract**
- OLD: committed script bisection λ ≤ 200, μ ≤ 20, 30 iterations (frozen spec: 1000, 50, 40).
- NEW: the committed script implements the retired bound exactly as frozen (λ ∈ [0.05, 1000] log-bisection, μ ∈ [0, 50], 40 iterations, interval-end rule, B = 20,000 in 20 chunks of 1,000, SeedSequence([20260929, 1]), per-draw normal order) for the reproduction in run D, plus the repaired bound. Runs A/B in the power table were produced by the 94b5934 script; their retired-bound columns are labelled as such, and every repaired exclusion rate is ≤ the tabulated retired one (repaired U ≥ retired U pointwise).
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE. BUILDER_IMPACT: none.

**D4-C2 D4 REPAIR R2 — prospective estimand vs unsampled rare tail arrivals (after Astra D4 recheck @3d18085; delta V2-R1 @24d2342 → V2-R2)**
- OLD CLAIM (V2-R1): `U(θ) = w_core U_core + M_tail < θ_ERT` → `NET_VALUE_EXCLUDED` → `R*_REJECTED_AS_NET_STRATEGY`; `U < max(θ_PCE, θ_ERT)` → `LARGE_VALUE_EXCLUDED`; read as statements about the §5.1 prospective θ.
- ASTRA COUNTEREXAMPLE (C2, CRITICAL): GO-compatible designs with rare 0.001 legs (p = 0.17, E[count] 1.86, core −0.05, θ_P = 0.025): false `NET_VALUE_EXCLUDED` 0.0592 [0.0519, 0.0666]; p = 0.5–1.0: 0.19–0.35; θ_P = 0.10: false `LARGE_VALUE_EXCLUDED` 0.153; GO passes 82–94%. REPRODUCED here with independent code and fresh seeds (run E): 0.0475 [0.0409, 0.0541] joint and 0.098 given a reachable analysis state (GO ∧ INFO_SUFFICIENT) for S1; 0.165–0.176 at p = 0.5; 0.314 at p = 1.0; 0.56 with date-clustered arrivals; false LARGE 0.147 at θ_P = 0.10; dangerous-region grid 414 of 1,002 cells > 0.05 (max 0.64).
- ROOT CAUSE: the R1 proof conditions on the realised trade set, so `M_tail` bounds only the tail legs that occurred (θ_W). θ_P also depends on the arrival process of executed trade types; a rare type with payoff up to 951 per dollar can be absent from every observed date while carrying θ_P above any threshold. Zero observed arrivals were implicitly treated as a zero prospective rate.
- NEW INVARIANT: no label may claim `θ_P < θ_ERT` or `θ_P < θ_PCE` unless a valid bound covers both tail-outcome uncertainty on observed types and tail-arrival uncertainty; where no such bound exists, prospective exclusion is not issued. Identification theorem (spec 8.5b): under the frozen admissible class (p ∈ [0,1], 0.001 tick, date common modes) any level-0.05 prospective exclusion test has power ≤ α (1 − η*)^−134 ≤ 0.0584 at every θ_0 ≥ −1. So no valid bound with useful power exists in V2.
- REPAIR (R2 = R2_B_PROSPECTIVE_EXCLUSION_INDETERMINATE_WHEN_UNIDENTIFIED, hybrid):
  - PROSPECTIVE_EXCLUSION = NOT_IDENTIFIED_IN_V2 (constant).
  - ECONOMIC_RESULT = PROSPECTIVE_VALUE_{CONFIRMED, NOT_ROBUST, INDETERMINATE}; the EXCLUDED row is deleted and the SCIENTIFIC partition has 11 values.
  - R1's bound is kept unchanged but re-scoped to the report-only estimand θ_W: `REALIZED_WINDOW_BOUND` with REALIZED_WINDOW_{LOSS_CONFIRMED, RELEVANT_VALUE_EXCLUDED, LARGE_VALUE_EXCLUDED, NOT_EXCLUDED}.
  - `R*_REJECTED_AS_NET_STRATEGY` is never issued.
  - `R*_CORE_INFORMATION_REJECTED` and the forward-signal rule read `CORE_ADVERSE` (Astra minor m2), and the stale "model-conditional" wording in §24 is fixed (Astra minor m1).
  - The opportunity chain is defined, with a TAIL_ARRIVAL_REPORT, a zero-count rule, the claim matrix (17.8) and mandatory sentence (b).
- REPAIR FAMILIES: R2-A (arrival bound) needs trade-level independence that V2 does not grant, and even granted it never excludes (allowance ≈ 1.2 at zero observed sub-cent legs; run E P(exclusion) = 0 everywhere), so it is R2-B plus an assumption. R2-C (θ_W only) does not answer the prospective question, so it is used only as a report field, never for rejection. Trading-rule fixes (sub-cent exclusion, price floor) need broader authority and are V3 material.
- CLAIM STRENGTH AFTER REPAIR: **SUPERSEDED — this R2 claim was refuted by Astra C3 (@92c2f706) and replaced by D4-C3 (R3: no unconditional prospective label); the T2 level it cites is re-qualified by D4-C3-M1. Kept as history (Astra m9):** PROSPECTIVE_VALUE_CONFIRMED = T2 at 0.05 (IUT), unchanged; with bounded downside, prospective confirmation has no structural non-identification (run E: false confirmation at θ_P = 0 under catastrophic-date alternatives ≤ 0.0378, upper MC 0.0437). REALIZED_WINDOW_* = θ_W below a threshold at declared 95%, never θ_P and never a rejection. No prospective exclusion exists.
- POWER COST: prospective exclusion power drops from the R1 values (0.51 at θ = −0.05, 0.93 at θ = −0.10 in tail-free runs) to none. The theorem shows no valid test could exceed 0.058. Realised-window exclusion keeps R1's power (run E tail-free: 0.36 at θ_W = −0.05, 0.57 at −0.10, joint with GO ∧ INFO). No capital decision changes, because deployment always required confirmation.
- ASTRA_FINDING: D4 recheck C2 CRITICAL, minors m1 and m2. FABLE_RECOMMENDATION: —. ARCHITECT_DECISION: R2 as above.
- OUTCOME_INFORMATION_USED: FALSE (synthetic run E and algebra only). TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE (by R2). COHORT_CHANGED: FALSE (by R2).
- BUILDER_IMPACT: compute U_W exactly as R1; print PROSPECTIVE_EXCLUSION constant, REALIZED_WINDOW_BOUND and TAIL_ARRIVAL_REPORT; implement the 3-value economic axis, the renamed labels, the CORE_ADVERSE-based forward signal and flag; no TPM / SHR, no arrival bound.
- FILES CHANGED: spec (header, §2 D4-C2 / D2-SM / D4-REJ notes, §4.1, §5.1, §6.1, §6.3, §8.5, new §8.5b, §8.6, §10.3, §11.2, §17.2, §17.3, §17.5, §17.6, §17.7, new §17.8, §20, §21 items 7 / 19 / 21 / 23 / 25–29, §24, §26, §27); manifest (header, A rows ECONOMIC_ESTIMAND / REALIZED_WINDOW_ESTIMAND / NULLS / ALPHA / REALIZED_WINDOW_UPPER_BOUND / PROSPECTIVE_EXCLUSION / OPPORTUNITY_CHAIN / TAIL_ARRIVAL_REPORT / TERMINAL_STATE_MACHINE / FORWARD_SIGNAL_RULE / REJECTION_RULE / MANDATORY_SENTENCES, B INDEPENDENT_REAUDIT, new section D); this delta; power table §4.6; architect state; resume checkpoint; new `WEATHER_FORWARD_V2_D4_C2_SIM_2026-09-30.py` and its raw output `WEATHER_FORWARD_V2_D4_C2_RUN_E_OUTPUT_2026-09-30.jsonl`.

**D4-C3 D4 REPAIR R3 — transportability: finite realised evidence → prospective claim (after Astra D4-C2 recheck @92c2f706; delta V2-R2 @e45d2ce7 → V2-R3)**

ASTRA_FINDING: C3 (CRITICAL). The R2 label `PROSPECTIVE_VALUE_CONFIRMED` (T2 + θ̂ ≥ θ_ERT + gates) and the forward signal were issued at θ_P = −0.005: 0.4266 (thin fills) and 0.1245 (full fills). Rare loss dates carrying the 96-event cost cap were absent from most 120-date windows, inside the class R2 itself declared for θ_P. MP2: no frozen bridge from the window to θ_P. Minors m3–m7.

ROOT_CAUSE: V2 froze no relation between the observed law and the future law, yet read T2 as a statement about θ_P. R2's "bounded downside" argument compared regimes by date frequency, not cost mass. A loss date can carry `C_CAP_DATE / C̄_d` (≈ 2.9–20 in run F) times an ordinary date's cost, so the date frequency needed to cancel a positive θ can be small enough to go unseen.

WHY_T2_WAS_NOT_ENOUGH: T2 is sampling inference. It quantifies the uncertainty of the process that produced the observed trades, which here is θ_W, conditional on the realised trade set. A cluster-robust SE cannot see types or regimes that did not occur. Transport from θ_W to a future law is a separate, non-statistical step.

SOURCE_VS_FUTURE_DISTRIBUTION: `P_obs` (window + OP + resolved pre-t0 history) versus `Q_H` (executed-trade law of a future epoch of H counted dates). The frozen relation is now explicit:
- the mechanics `N_j ≥ −C_j` and `C_d ≤ C_CAP_DATE`;
- the declared, unverified transport class 𝒯_H(ε, δ);
- nothing else.

SELECTED_TRANSPORT_ARCHITECTURE: hybrid **C3_C + C3_A**.
- C3_C: no unconditional prospective label in either direction. The mirror theorem (8.5c) shows any valid unconditional confirmation test has power ≤ 0.06–0.12 in thin geometries.
- C3_A: a cost-mass robustness frontier with no chosen threshold.
- C3_B (explicit stationarity) was evaluated and rejected. It would be exactly the hidden assumption Astra found, and no observable check can certify it (8.5c: a hidden regime with identical covariates trips no flag).
- Falsification attempt on C3_A: the conditional claim can be false only through the sampling event θ_W < L_W. Run F confirms this (cond. claim false = L_W miss).

FORMAL_ESTIMAND:
- empirical: θ_W (ECONOMIC_RESULT, T2 unchanged; U_W unchanged);
- strategic: θ_P (not a V2 estimand);
- conditional prospective: `θ_F(Q_H) = E_Q[N]/E_Q[C]` over the next H counted dates, for Q_H ∈ 𝒯_H(ε, δ).

ROBUSTNESS_CONTRACT:
- Proposition 1 (exact cost-mass mixture identity for E[N]/E[C]) and `WORST_CASE_REGIME_RETURN = −1` per dollar of C (exact).
- Theorem 2: on {θ_W ≥ L_W}, `θ_F ≥ L_T(ε, δ) = (1 − ε)(L_W − δ) − ε` for all Q ∈ 𝒯_H(ε, δ), simultaneously for all (ε, δ, H).
- Frontier `ε*(δ, τ) = (L_W − δ − τ)/(1 + L_W − δ)` if `L_W − δ > τ`, else 0 (domain guard as in spec 8.5c; the unguarded `max(0, …)` form printed here before D4-C3-M1 gave a positive ε* for `L_W − δ < −1`; Astra m8).
- Reporting grids only: δ ∈ {0, 0.01, 0.02, 0.05}, τ ∈ {0, θ_ERT}, H ∈ {14, 30, 60, 120} (existing constants). No ε, δ, H or τ threshold is chosen in V2.
- Reported with it: k*(H), cost-mass concentration (n_eff,C, cap ratio, ε_1(H)), and observable invalidation flags that can only revoke.
- Rolling-epoch fields (design only).

CLAIM_STRENGTH:
- REALIZED_WINDOW_VALUE_SUPPORTED: θ_W > 0 (size ≤ 0.05, IUT) with θ̂ ≥ θ_ERT and robust to G1–G3. **SUPERSEDED (m10): this size held only without cross-block persistence; the level is restated over a declared class by D4-C3-M1 and, after Astra M1-R, by D4-C3-M2 (spec 8.1c).**
- CONDITIONAL_PROSPECTIVE_SUPPORT(ε*, δ): if the premise holds, θ_F ≥ L_T. Its only probability is the sampling event (0.95 nominal; simulated 0.9448–0.9502). **SUPERSEDED by D4-C3-M1: those designs had no cross-block persistence; the attained level is now stated by dependence class (spec 8.1b).**
- PROSPECTIVE_CONFIRMATION = NOT_ESTABLISHED_UNCONDITIONALLY.
- PROSPECTIVE_EXCLUSION = NOT_USEFULLY_TESTABLE_IN_V2_HORIZON.

FALSE-CONFIRMATION_RESULT (run F, power table §4.7):
- C3 reproduced: retired label false 0.4334 [0.4265, 0.4403] (thin) and 0.1175 [0.1130, 0.1220] (full); in the grid, above 0.05 in 55 of 148 non-positive cells (max 0.36).
- R3: 0 unconditional prospective labels and 0 prospective exclusions in all 443,000 scenario / C3 / grid / coverage replications.
- R3 false window claims ≤ 0.043 (grid, 1,000 replications per cell).
- L_W miss 0.044–0.0552 at 20,000 replications (carried D8 limitation, disclosed).
- In every C3 design the frontier lies below the true adverse cost share: median ε* 0.011–0.045 against ε_true 0.034–0.096.

POWER / INFORMATION COST:
- No unconditional prospective verdict in either direction.
- The positive realised-window claim keeps T2's power (0.62 at θ = 0.10 thick; 0.83 thin, stable).
- The prospective content is only as strong as the reader's belief that at most ε* of a future epoch's cost mass is adverse. In C3-like geometries the evidence absorbs well under one maximum-exposure adverse date per 120-date epoch (k*(120) medians 0.14–0.86; 2.2 in a thick, stable design).

FORWARD-SIGNAL_CHANGE: `WEATHER_EDGE_FORWARD_SIGNAL` is renamed `SHADOW_CONTINUATION_SIGNAL`, with the same conditions. Its meaning is restricted to "propose a further paper/shadow epoch". It is not an edge verdict and has no capital path.

MINORS m3–m7:
- m3: manifest §C / §D rows marked SUPERSEDED, and section A declared authoritative.
- m4: checkpoint §4 items 1, 3 and 5 marked superseded.
- m5: mandatory REALIZED_WINDOW_ prefix note in 17.3, and the economic labels now carry the same prefix.
- m6: D_obs ≈ 174 (window + OP + pre-t0 resolved history); the ceiling becomes 0.0602 / 0.0611.
- m7: "not identified" becomes "not usefully testable within V2's horizon (finite-horizon power ceiling)"; the constant and printed value are renamed.

FILES CHANGED:
- spec (header, §1, §2 D4-C3, §4.1, §5.1, §6.1, §6.3, §8.5b wording, new §8.5c, §17.2, §17.3, §17.5–17.8, §21 items 27 and 30–35, §24, §26, §27);
- manifest (A rows, C / D markers, new E);
- this delta; power table §4.7 / §5; architect state; resume checkpoint;
- new `WEATHER_FORWARD_V2_D4_C3_SIM_2026-09-30.py` and `WEATHER_FORWARD_V2_D4_C3_RUN_F_OUTPUT_2026-09-30.jsonl`.

OUTCOME_INFORMATION_USED: FALSE (synthetic run F, algebra and the Astra audit only).

TRADING_RULE_CHANGED: FALSE. R*, h, W, signal, cohort, entry rule, T_entry, S_ref sizing, execution and the 0.04 strata are byte-identical in the spec. EXECUTION_MODEL_CHANGED: FALSE (by R3).

BUILDER_IMPACT:
- print L_W, the ε* grid, k*(H), concentration fields, the two constants and sentence (c);
- rename the economic labels and the signal;
- implement no transport threshold and no capital logic.

**D4-C3-M1 — source-bound calibration under cross-block date persistence (after Astra D4-C3 + transportability recheck @5bb57eb2; delta V2-R3 @341e0b7a → V2-R3-M1)**

ASTRA_FINDING: M1 (MAJOR, blocking), plus minors m8 and m9.
- After R3, `L_W = θ̂ − t_{df,0.95} SE_CR(θ̂)` (two-way CR, 5-date blocks × ICAO) is the only probability behind REALIZED_WINDOW_VALUE_SUPPORTED / NOT_ROBUST ("size ≤ 0.05") and behind every conditional prospective statement (8.5c).
- Under date persistence across 5-date blocks — a mechanism spec §9 names — it undercovers in sparse designs that pass the information floor. Astra measured a false window positive of 0.0805 [0.0767, 0.0843] at θ_W = 0 and an L_W miss of 0.0902 [0.0863, 0.0942] (φ = 0.8, latent regime variance 0.05, m = 17).
- m8: the ROBUSTNESS_FRONTIER line (17.3) and the manifest ROBUST_BOUND / FRONTIER row lacked the 8.5c domain guard.
- m9: power table §4.6 reading 5 and the D4-C2 "CLAIM STRENGTH" bullet still asserted R2's refuted prospective-confirmation validity without a marker.

REPRODUCED (run G: fresh code and seeds, 20,000 replications per cell; R3 engine):
- false positive 0.0789 [0.0752, 0.0826];
- full-fill miss 0.0889 [0.0850, 0.0928];
- thin miss 0.0866 [0.0827, 0.0905];
- φ = 0.9 / 0.10 cells: 0.0844 and 0.0737.

Every Astra value lies inside the run-G 95% MC interval. Over the declared class the R3 engine is worse than in Astra's cells: up to 0.1287 [0.1241, 0.1333] (φ = 0.9, latent variance 0.05, m = 17 full, θ = 0.10). It already exceeds 0.05 at φ = 0.5 (0.0621).

ROOT_CAUSE: two-way CR with 5-date blocks omits covariance between blocks.
- A stationary AR(1) date component keeps only 0.39 (φ = 0.8) or 0.21 (φ = 0.9) of its variance inside 5-date blocks (DERIVED, spec 8.1b).
- IF5 (DEFF_2w(κ̂_core) ≤ 6) screens strong regimes in thick designs, but not in 17-trades/date designs.
- R3 disclosed only the ≈ 0.5 pp finite-cluster shortfall seen without persistence.

REPAIR (option a, calibrate):
- **Rule.** `L_W = θ̂ − max_{b∈{5,10,20,30}} t_{df_b,0.95} SE_2w(b)`. It uses the unchanged 8.1 engine at 5-, 10-, 20- and 30-date calendar blocks, with matching df_b = min(G_B(b), G_S) − 1 (spec 8.1b). T2 ⟺ L_W > 0.
- **Properties.** Never above the R3 bound. Defined whenever INFO_SUFFICIENT (df_30 ≥ 1). The 30-date block is W, the trailing-bias window whose seasonal lag §9 names.
- **Stated level.** P(reach ∧ L_W > θ_W) ≤ 0.05, and size of the positive REALIZED_WINDOW claim ≤ 0.05, over the 5-date-block model and the declared persistence class 𝒟_P:
  - daily AR(1) date regime with φ ∈ {0.5, 0.7, 0.8, 0.9} and latent variance ∈ {0.02, 0.05, 0.10}, on V2's copula (0.05, 0.05, 0.10);
  - 120 dates, 48 stations; m ∈ {17, 35}; thin and full fills; θ ∈ {0, 0.05, 0.10}.

  Worst cell 0.0465 [0.0436, 0.0494] at 20,000 replications (φ 0.9, latent variance 0.05, m = 17 thin, θ = 0.10); independent 100,000-replication re-runs 0.0458 [0.0445, 0.0471] (that cell) and 0.0464 [0.0451, 0.0477] (full fills). No level is claimed outside 𝒟_P; there it is measured lower (up to 0.072 at φ = 0.95 and 0.110 at φ = 0.97). The class-indexed level is written into spec 6.1, 6.2, 8.1b, the 8.5c error statement and Theorem 2's definition of L_W (algebra unchanged), 10.3, 17.3 (SOURCE_LOWER_BOUND text, sentence (c), headline interval), 17.8, 21, 24, 26 and 27, and into the manifest.
- m8 and m9 fixed mechanically: guarded formula; SUPERSEDED markers, with history kept.

DECLARATION AND SELECTION (no tuning):
- The class, the pass criterion and a first candidate RM (blocks {5, 10, 20}) were declared in the run-G script header before any run.
- A preliminary run of RM on 45 class cells showed it failing at φ = 0.9. No constant of RM was changed. Its R3-engine and RM counts are identical, cell for cell, to the committed class run (same seeds).
- Two comparators were then declared, each before its own first run, together with the selection criterion "validity over the whole declared class first, then power and information-floor behaviour":
  - RW (adds the 30-date block);
  - RE (two-way equally-weighted-cosine HAR, K = 4 at 120 dates, fixed-K t reference).
- All four rules are reported on the same replications:
  - RM: φ ≤ 0.8 worst 0.0477; φ = 0.9 worst 0.0711 [0.0675, 0.0747].
  - RE: 0.0396; φ = 0.9 worst 0.0574 [0.0542, 0.0606].
  - RW: 0.0319; φ = 0.9 worst 0.0465 (100,000-replication re-runs 0.0458 / 0.0464).
- Only RW is valid over 𝒟_P, so RW is adopted. Option (b) on the R3 engine would have had to state a size of ≈ 0.13 at φ = 0.9, and > 0.05 already at φ = 0.5.

CLAIM_STRENGTH:
- REALIZED_WINDOW_VALUE_SUPPORTED / NOT_ROBUST: size ≤ 0.05 over the 5-date-block model and 𝒟_P; none claimed outside 𝒟_P.
- CONDITIONAL_PROSPECTIVE_SUPPORT: the same single sampling event, at the same class-indexed level.
- Given reach, the miss is larger: up to 0.085 (φ ≤ 0.8) and 0.136 (φ = 0.9) in cells with reach ≥ 0.10, against 0.189 / 0.281 for the R3 engine. Disclosed, as in R3's "not the probability given a label".
- PROSPECTIVE_CONFIRMATION / PROSPECTIVE_EXCLUSION constants unchanged. No unconditional prospective label.

POWER_COST (SUPPORTED joint with reach, no persistence; R3 engine → M1):

| Fills, trades per date | θ = 0.10 | θ = 0.05 |
|---|---|---|
| thin, 17 | 0.843 → 0.654 | 0.379 → 0.187 |
| full, 17 | 0.851 → 0.668 | 0.386 → 0.195 |
| thin, 35 | 0.629 → 0.554 | 0.323 → 0.192 |
| full, 35 | 0.633 → 0.565 | 0.323 → 0.195 |

- T2 power at the design's own θ_PCE: P(T2) at θ_PCE is 0.554 / 0.476 / 0.456 / 0.459 for m = 17 thin / 17 full / 35 thin / 35 full (θ_PCE = 0.09 / 0.08 / 0.07 / 0.07), against 0.779 / 0.701 / 0.673 / 0.675 for the R3 engine (no persistence).
- Effect confirmed with 80% T2 power: ≈ 0.11–0.12 (R3 engine ≈ 0.09–0.10; linear interpolation of P(T2) between θ_PCE and 0.12, no persistence).
- At the information floor (60 dates, 25 stations), positive claims become nearly impossible: 0.001 (m = 17, thin) and 0.005 (m = 35, full), against 0.143 / 0.366 for the R3 engine.
- θ_PCE's formula, PCE_CEILING and GO / NO_GO are unchanged and are not retuned. The shortfall against the nominal 0.80 is disclosed in spec 1, 6.2, 7, 10.3 and 24.

FROZEN SURFACES UNDER PERSISTENCE (observation; not repaired; outside the bounded mission): T1a, NEG and U_W use the unchanged 5-date-block engine. Run G, worst cell, φ ≤ 0.8 / φ = 0.9:
- T1a false rejection: 0.053 / 0.089 (nominal 0.025);
- NEG: 0.040 / 0.070 (nominal 0.025);
- U_W miss: 0.045 / 0.077 (declared 0.05).

Spec 8.1b and 17.8 qualify their stated levels at statement level; the tests are byte-identical. Flagged to Astra and governance.

REGRESSION:
- Byte-identical to 341e0b7a: spec §3, §4, §5, §8.1, §8.2–8.5b, §9, §10.1, §10.2, §11–§16, §17.1, §17.2 (state machine, 11 values), §17.4–§17.7, §18–§20, §22, §23 and §25.
- In §8.5c, only Theorem 2's definition sentence for L_W and the error statement changed; Proposition 1, the proof, the frontier definition, k*(H), concentration and invalidation are unchanged.
- No unconditional prospective label exists.
- Astra C3 cells under M1 (run F's own process): window-positive 0.329 / 0.061 (thin / full; R3 engine 0.428 / 0.121); false window claims 0; conditional claim false only through the L_W miss (0.0081 / 0.0053).

FILES_CHANGED:
- spec;
- manifest (header, rows NULLS / ALPHA / TARGET_POWER / PRIMARY_INFERENCE / new T2_SOURCE_BOUND / ROBUST_BOUND / FRONTIER / DEPENDENCE_MODEL / MANDATORY_SENTENCES / INDEPENDENT_REAUDIT, new section F);
- this delta (new entry; markers on D4-C2 and D4-C3);
- power table (§4.6 and §4.7 markers, new §4.8, §5 note);
- architect state;
- resume checkpoint;
- new `WEATHER_FORWARD_V2_D4_C3_LW_CAL_SIM_2026-10-01.py`, and its raw output `WEATHER_FORWARD_V2_D4_C3_M1_RUN_G_OUTPUT_2026-10-01.jsonl`.

OUTCOME_INFORMATION_USED = FALSE (synthetic run G, algebra and the Astra audit only).

TRADING_RULE_CHANGED = FALSE. EXECUTION_MODEL_CHANGED = FALSE (by M1). COHORT_CHANGED = FALSE (by M1).

BUILDER_IMPACT: compute the 8.1 two-way SE of θ̂ at 5-, 10-, 20- and 30-date calendar blocks, and set L_W = θ̂ − max_b t_{df_b,0.95}·SE_2w(b). Print the class-indexed level text with L_W. Everything else is unchanged.

## D5 — Science vs operability (MAJOR → CLOSED)

- OLD: OPERATIONALLY_INACCESSIBLE evaluated before REJECTED.
- NEW: OPERABILITY_STATE is an orthogonal axis (legal, mechanics, depth ≥ 25 USD share ≥ 0.80, ρ_30 at 1,000 tier ≥ 0.05) that never replaces or pre-empts the scientific label.
- WHY: a losing rule must not exit as "inaccessible"; depth is marginal (76% measured vs 80%).
- ASTRA_FINDING: D5. FABLE_RECOMMENDATION: orthogonal flag.
- ARCHITECT_DECISION: adopted; V1 criteria 7 and 8 moved here.
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE.
- BUILDER_IMPACT: separate state computation and report section.

## D6 — Burn-in / readiness (MAJOR → CLOSED)

- OLD: burn-in ≥ 30 consecutive days, then t0.
- NEW: USABLE / BIAS_HISTORY_READY per station-kind (30 usable resolved dates at T_entry, FINAL by our own capture time); FRESH_READY (span ≤ 40 days) for readiness; GLOBAL_READY (GR1–GR6); 14-date outcome-free observation phase; readiness report; t0 within 21 days of the OP.
- WHY: the first E8-eligible date is ≈ day 33–35; the frozen rule's trigger rate is unobservable in a 30-day burn-in.
- ASTRA_FINDING: D6. FABLE_RECOMMENDATION: READY / GLOBAL_READY / 14-date observation.
- ARCHITECT_DECISION: adopted with a stricter GR1 (80% of 48 stations, both kinds) and the 21-day t0 validity.
- OUTCOME_INFORMATION_USED: FALSE (settled values of past dates enter only the frozen bias term, as in V1; parser agreement is aggregate). TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE.
- BUILDER_IMPACT: READINESS table, PHASE_LOG, phase flag, invariant 21.

## D7 — °F / 2 °F cohort (MAJOR → CLOSED)

- OLD: E4 "nine consecutive single-degree buckets" (excluded every °F ladder); bucket arithmetic single-degree only.
- NEW: °F included; four frozen title regexes; integer sets; half-open continuous intervals; E4 by width `w = 1` (°C) / `w = 2` (°F); °F bias target = bucket midpoint; exact unit conversion.
- WHY: MEASURED 66/66 °F ladders are 2 tails + nine contiguous 2 °F buckets with the same NOAA template in whole °F (no conversion chain); 48 vs 37 stations for the weakest inferential dimension; V1's σ = 1.8 °F and E13 show the intent.
- ASTRA_FINDING: D7. FABLE_RECOMMENDATION: Architect's call.
- ARCHITECT_DECISION: route B (generalise), fully specified.
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE (same formula on a clarified domain). EXECUTION_MODEL_CHANGED: FALSE. COHORT_CHANGED: TRUE.
- BUILDER_IMPACT: parser, arithmetic tests (spec §26), unit field.

## D8 — Date × station dependence (MAJOR → CLOSED)

- OLD: date-block bootstrap primary; station and two-way as sensitivities.
- NEW: two-way (5-date calendar block × ICAO) cluster-robust primary, max-of-three SE, t(min G − 1), cluster floors, Kish reporting, DEFF reporting; PINM copula with date, station and station-day cell effects.
- WHY (SIMULATED here and by Fable): date-only κ test rejects 0.095–0.205 at nominal 0.025 under station dependence.
- ASTRA_FINDING: D8. FABLE_RECOMMENDATION: two-way, max of three.
- ARCHITECT_DECISION: adopted.
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE.
- BUILDER_IMPACT: CR engine; cluster keys in PNL rows.

## D9 — MIN_SAMPLE (MINOR → CLOSED)

- OLD: ≥ 1,000 trades as the power basis. NEW: information floor IF1–IF5 (dates, blocks, stations, SE, DEFF). WHY: 1,000 is reached by day 24–77 and is not where information binds. ASTRA: D9. FABLE: date ceiling §1.3. DECISION: retired. OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE. BUILDER_IMPACT: floor computation.

## D10 — NO_DATA_LOWEST in the bias history (MINOR → ACCEPTED, DISCLOSED)

- OLD: all settlements enter the bias mean (tail boundary). NEW: unchanged; `BIAS_CONTAMINATED` flag per decision; per-station counts; non-gating sensitivity on the uncontaminated subset.
- WHY: excluding non-meteorological settlements would change R*'s bias estimator (a rule change) and is not needed for validity.
- ASTRA: D10 (exclude). FABLE: exclusion is a rule change, Architect's call. DECISION: preserve the rule. OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE. BUILDER_IMPACT: flag and report fields.

## D11 — Mechanics-change baseline (MINOR → CLOSED)

- OLD: ≥ 50% of all daily temperature events ineligible / ambiguous for 14 dates → OPERATIONALLY_INACCESSIBLE.
- NEW: reason-code families; share over baseline-eligible events (structural and readiness codes excluded); M3 fee change → immediate; ≥ 50% on 14 dates → effective at the first; truncation with ≥ 60 counted dates → VALID_TRUNCATED, else INVALID.
- WHY: ≈ 28% structural ineligibility left ≈ 22 points of headroom. ASTRA: D11. FABLE: §5.6. DECISION: adopted. OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE. BUILDER_IMPACT: reason-family field, detectors M1–M6.

## D12 — Tier selection (MINOR → CLOSED)

- OLD: T_entry order, ties by event_id. NEW: T_entry order, ties by `sha256(event_id + ":WFV2")`; CAPACITY_CONSTRAINED_SUBSAMPLE label with regional composition.
- WHY: T_entry order is the causal constraint; a fixed event_id tie-break favours the same cities daily. ASTRA: D12. FABLE: CD5. DECISION: adopted. OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE. BUILDER_IMPACT: tie-break function, report labels.

## X1 — CONSERVATIVE slippage (cross-defect → CLOSED)

- OLD: level price + 0.01. NEW: level price + one tick (recorded `orderPriceMinTickSize`; fallback rule).
- WHY: + 0.01 on a 0.001 ask is an 11× cost; the robustness gate would fail mechanically whenever tail legs matter.
- ASTRA: §6.5. FABLE: CD9. DECISION: adopted. OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. **EXECUTION_MODEL_CHANGED: TRUE (CONSERVATIVE only)**. BUILDER_IMPACT: tick lookup in the fill engine.

## X2 — Sequential design (CLOSED)

- OLD: "no early stopping" but a 60/90/120 window with an unpinned analysis date. NEW: one analysis at D_120 + 10 days; no interim; time-locked analysis module.
- WHY: efficacy stopping is useless in the plausible range; futility on θ is hazardous with rare tail wins; a paper experiment has no capital at risk. ASTRA: S4. FABLE: Family C, one futility look optional. DECISION: no interim. OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE. BUILDER_IMPACT: invariant 22.

## X3 — Attribution / placebo (CLOSED)

- OLD: criterion 9 "beats B4 and B5 by ≥ θ_MEUE" gating FORWARD_SIGNAL. NEW: descriptive; T1 carries information attribution; ATTRIBUTION_NOT_ESTABLISHED and PLACEBO_ANOMALY flags.
- WHY: SE of a difference of two θ̂ is 0.04–0.14. ASTRA: —. FABLE: CD13. DECISION: descriptive. OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE. BUILDER_IMPACT: report fields.

## X4 — Other V1 gate criteria

| V1 criterion | V2 location |
|---|---|
| c1 L95 > 0 | T2 (two-way CR) |
| c2 θ̂_CONS > 0, θ̂ ≥ θ_MEUE | G1 (tick-aware) and `θ̂ ≥ θ_ERT` in E2 / E3 |
| c3 no leakage / replay | VALIDITY rows 1–3 |
| c4 minimum sample | MIN_INFORMATION IF1–IF5 |
| c5 L80 ≥ 0.01 | retired (created Astra's S3 gap; the relevance question is carried by U(θ) and ECONOMIC_BOUND); L80 printed descriptively |
| c6 concentration, settlement modes | G2, G3 |
| c7 accessibility | OPERABILITY row 4 |
| c8 capital efficiency | OPERABILITY row 5 |
| c9 attribution | descriptive (X3) |

## Unchanged (explicitly)

h = 0.10; W = 30; σ = 1.0 °C / 1.8 °F; model, provider, members, variables, cadence; T_entry; argmax and tie rule; hold to settlement; fee; S_ref = 50; tiers and stake fraction; REALISTIC fill model; accounting and full ledger; settlement controls; survivorship cohort; exploratory family E1–E15; anti-leakage invariants other than 11.
