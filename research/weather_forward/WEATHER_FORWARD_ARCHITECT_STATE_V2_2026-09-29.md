# WEATHER FORWARD ARCHITECT STATE — V2 — 2026-09-29

```text
ROLE                          = Weather Forward V2 Architect / convergence authority
STATUS                        = DONE — bounded D4-C3-M1 source-bound calibration committed and pushed on top of R3 (341e0b7a) after Astra's D4-C3 recheck (5bb57eb2)
BRANCH                        = claude/charming-allen-948kd8
WEATHER_FORWARD_SPEC_V2       = AUDITED @94b59348d5b79cd3c53dcba0b791ce1daeb75d60 (immutable ancestor)
ASTRA_WEATHER_V2_REAUDIT      = BLOCKED_D4_STRUCTURED_BOUND_FALSE_ECONOMIC_EXCLUSION
                                (astra/weather-forward-v2-independent-reaudit-2026-09-29 @7d95c00abccfbc805c0d8abca65a6b93268741a2)
WEATHER_FORWARD_SPEC_V2_D4_REPAIR = AUDITED @24d2342 → ASTRA_WEATHER_V2_D4_RECHECK = BLOCKED_D4_PROSPECTIVE_ESTIMAND_UNSAMPLED_TAIL_FALSE_EXCLUSION (@3d18085)
WEATHER_FORWARD_SPEC_V2_D4_C2_REPAIR = AUDITED @e45d2ce7 → ASTRA_WEATHER_V2_D4_C2_RECHECK = BLOCKED_D4_PROSPECTIVE_CONFIRMATION_UNSAMPLED_LOSS_REGIME_FALSE_CONFIRMATION (@92c2f706)
WEATHER_FORWARD_SPEC_V2_D4_C3_TRANSPORT_REPAIR = AUDITED @341e0b7a → ASTRA_WEATHER_V2_D4_C3_TRANSPORT_RECHECK = BLOCKED_D4_R3_SOURCE_BOUND_UNDERCOVERAGE_CROSS_BLOCK_PERSISTENCE (@5bb57eb2)
WEATHER_FORWARD_SPEC_V2_D4_C3_M1_REPAIR = READY_FOR_ASTRA_RECHECK
WEATHER_FORWARD_SPEC_V1       = HISTORICAL_FROZEN_OBJECT (726070a, byte-identical in this branch)
EXPERIMENT_FEASIBILITY        = BLOCKED_POWER_BELOW_DECLARED_MEUE   (Astra's V1 verdict)
EXPERIMENT_FEASIBILITY_V2     = BLOCKED_D4_R3_SOURCE_BOUND_UNDERCOVERAGE_CROSS_BLOCK_PERSISTENCE   (Astra's @5bb57eb2; unchanged until Astra rechecks)
HURDLE_SAMPLE_INCOMPATIBILITY = FALSE
FABLE_DESIGN_CHALLENGE        = DONE_ADVISORY
BUILDER_AUTHORIZED            = FALSE
REAL_CAPITAL_AUTHORIZED       = FALSE
LIVE_TRADING_AUTHORIZED       = FALSE
t0                            = NOT_DECLARED
ACCESS_USER_REPORTED          = TRUE
LEGAL_ACCESS_CONFIRMED        = UNKNOWN
TRADING_RULE_CHANGED          = FALSE
EXECUTION_MODEL_CHANGED       = TRUE (CONSERVATIVE slippage only; unchanged by R1, R2, R3 and D4-C3-M1)
OUTCOME_INFORMATION_USED      = FALSE
NEXT_AUTHORIZED_ACTION        = ASTRA BOUNDED D4-C3-M1 RECHECK ONLY (M1, m8, m9; R1 / R2 / R3 regression; not Builder, not t0, not capital)
```

## Inputs read (exact objects; none modified)

- `QUANT_NORTH_STAR.md` (unchanged between 94b5934 and 7d95c00).
- V1 spec, manifest, architect state @ `726070a199957a6fc05515ebb3027e945028fddc` (byte-identical in this branch).
- Astra feasibility review @ `e1cf4ca0851eace2912ce8a9bcd4a8400ebf4250`; Fable design challenge @ `5760ffa5b5da2a988cfe6d1503c86c561acf9b1f` (byte-identical).
- V2 object @ `94b59348d5b79cd3c53dcba0b791ce1daeb75d60` (this Architect's; unmodified as a commit).
- Astra V2 independent re-audit and re-audit state @ `7d95c00abccfbc805c0d8abca65a6b93268741a2` (brought in by fast-forward; byte-identical).
- D4 repair R1 head @ `24d2342fcff8fd78a769a9ecaf7551ab2578e2ef` (verified as the remote head before R2).
- Astra D4 recheck and updated re-audit state @ `3d18085862f239a81936345989b4e26414cedcf3` (read from the Astra branch; not merged here, not modified).
- D4-C2 repair R2 head @ `e45d2ce7e2605a4136804d2c1b31efa3aa8120e1` (verified as the remote head before R3).
- Astra D4-C2 recheck and updated re-audit state @ `92c2f706d2ac75af9ae9710061c60df520234410` (read in full from the Astra branch; not merged here, not modified).
- D4-C3 repair R3 head @ `341e0b7aede716fdb68e2c9806cc1a09fdd50b82` (verified as local and remote head before D4-C3-M1).
- Astra D4-C3 + transportability recheck @ `5bb57eb2adf4cff35378f2c0e53e0316d45a4229` (§1, §6, §8, §10, §12, §13; evidence `astra_d4_c3_recheck_2026-10-01/`) and the orchestrator convergence ledger @ `c47080bc1741d91e0f7e23a41b3752291658b4df` (read from the Astra worktree; not merged here, not modified).

## Live data read by this Architect (pre-outcome metadata only)

V2 (unchanged): `gamma-api.polymarket.com/events?tag_slug=weather&closed=false` metadata only (titles, bucket labels, descriptions, tick, minimum size, fee schedule, resolution source). D4 repairs R1, R2, R3 and D4-C3-M1: **no live data read at all**; synthetic Monte Carlo and algebra only.

## Decisions frozen (see manifest V2 sections A and C)

Route = Family D + B hybrid, **without the gate**: θ (economic, unchanged, two-way CR) and a stratified information axis (κ_core by two-way CR; tail win count by PINM) tested in parallel; θ_ERT = 0.02; θ_PCE by frozen price-implied formula from a 14-date outcome-free observation phase; PCE_CEILING 0.10 and SE_KAPPA_CEILING 0.020 → GO/NO_GO; **R1 bound U_W = w_core·U_core + M_tail kept as the realised-window (θ_W) report field REALIZED_WINDOW_BOUND (R1, re-scoped by R2)**; **prospective exclusion not usefully testable and no economic rejection of R* (R2); no unconditional prospective label, economic axis REALIZED_WINDOW_VALUE_{SUPPORTED, NOT_ROBUST, INDETERMINATE} on θ_W, cost-mass transport frontier ε*(δ, τ) with no chosen threshold, SHADOW_CONTINUATION_SIGNAL (R3)**; two-way (5-date block × ICAO) dependence, max-of-three SE; readiness by usable resolved dates; capture-time book contract; °F included by exact interval arithmetic; CONSERVATIVE slippage one tick; T_entry allocation with hash tie-break; mechanics codes over a baseline; one analysis at D_120 + 10 days; no interim; VALIDITY × SCIENTIFIC (INFORMATION × ECONOMIC) × OPERABILITY state machine.

## D4 repair R1 (bounded; only Astra's C1 and MP1)

- Retired: the TPM ∨ SHR structured tail term (model-conditional; Astra C1 falsified its coverage in a GO region).
- Repaired bound: `U(θ) = w_core (θ̂_core + t_{df,0.975} SE_CR) + M_tail`, `M_tail = Σ_TAIL (n_j − C_j)/Σ C_j`; coverage ≥ core coverage for every tail geometry and dependence (proof: spec §8.5).
- Repaired rule 17.6: `R*_REJECTED_AS_NET_STRATEGY` iff `NET_VALUE_EXCLUDED`; `NEGATIVE_INFORMATION` → `R*_CORE_INFORMATION_REJECTED` (information-level). Found during the reproduction: the V2@94b5934 NEG clause issued a false economic rejection in 32% of Astra's A1 runs.
- Routes A–D evaluated (spec §8.5, delta D4.d): A subsumed; B adopted in its assumption-free form; C cannot restrict true tail probabilities; nothing smaller is valid.
- MP1 closed: committed simulation implements the retired bound with the exact frozen contract and the repaired bound; run D (power table §4.5).
- Unchanged: R*, cohort, strata, θ, κ_core, T1a, T1b, T2, NEG test, engines, dependence, PCE / GO, gates, the 14-value SCIENTIFIC partition, validity, operability, forward-signal rule, analysis time.

## D4-C2 repair R2 (bounded; only Astra's C2, plus Astra minors m1 / m2)

- Defect: R1's proof conditions on the realised trade set, so its bound covers θ_W and not the frozen prospective θ_P = E[N]/E[C]. Rare, high-payoff tail types absent from the window were treated as absent from the population.
- Decision: **R2_B_PROSPECTIVE_EXCLUSION_INDETERMINATE_WHEN_UNIDENTIFIED** (hybrid: R1 bound kept for θ_W as a report field). Minimality: the identification theorem (spec §8.5b) shows that any valid level-0.05 prospective exclusion test has power ≤ 0.058 over 134 dates under V2's own admissible class. R2-A (arrival bound) needs an unjustified independence assumption and never excludes (allowance ≈ 1.2 at zero observed sub-cent legs). R2-C cannot answer the prospective question and is used only as a θ_W report field. A trading-rule fix is out of scope.
- State machine: the ECONOMIC_RESULT EXCLUDED row is deleted, leaving an 11-value SCIENTIFIC partition. Other changes: labels renamed PROSPECTIVE_VALUE_*; ECONOMIC_BOUND → REALIZED_WINDOW_BOUND (θ_W); PROSPECTIVE_EXCLUSION = NOT_IDENTIFIED_IN_V2; TAIL_ARRIVAL_REPORT; R*_REJECTED_AS_NET_STRATEGY never issued; R*_CORE_INFORMATION_REJECTED and the forward signal read CORE_ADVERSE (m2); §24 wording (m1); claim matrix §17.8.
- Unchanged: R*, h, W, signal, cohort, entry rule, T_entry, S_ref sizing, execution models, 0.04 strata, κ_core, T1a, T1b, T2, NEG test, engines, dependence, PCE / GO, gates G1–G3, validity, operability, analysis time.
- Role-independence disclosure: the Astra D4 recheck @3d18085 and this Architect repair were produced in the same agent session under different role instructions. Run E is a fresh implementation with fresh seeds, but governance should treat the next Astra D4-C2 recheck as the independent check and may prefer a separate reviewer session.

## D4-C3 transport repair R3 (bounded; Astra's C3 + MP2, plus minors m3–m7)

- **Defect.** T2 is sampling inference about θ_W, yet R2 read it as a claim about θ_P. No relation between the observed law and the future law was frozen. R2's bounded-downside argument used date frequency where cost mass is what matters.
- **Decision.** A hybrid of C3_C and C3_A:
  - no unconditional prospective label in either direction; the mirror theorem (spec §8.5c) caps any valid unconditional confirmation test at power 0.06–0.12 in thin geometries;
  - the economic axis is REALIZED_WINDOW_VALUE_* on θ_W, with T2 unchanged;
  - prospective content is the declared, unverified cost-mass transport class 𝒯_H(ε, δ), with the exact deductive bound L_T = (1 − ε)(L_W − δ) − ε (Proposition 1, Theorem 2) and the frontier ε*(δ, τ), reported on outcome-blind grids. No threshold is chosen.
- **C3_B rejected.** Explicit stationarity would be the same hidden assumption, and no observable check can certify it.
- **Also added.** k*(H), cost-mass concentration, revoke-only observable invalidation, and the rolling-epoch contract fields (design only). SHADOW_CONTINUATION_SIGNAL replaces the forward signal. Minors m3–m7 are fixed.
- **Unchanged.** R*, h, W, signal, cohort, entry, T_entry, S_ref sizing, execution, 0.04 strata, κ_core, T1a, T1b, the T2 statistic and level, NEG, engines, dependence, PCE / GO, gates, validity, operability, analysis time, the R1 U_W, and the R2 exclusion removal.
- **Role-independence disclosure.** Every step from the Astra D4 recheck @3d18085 to this R3 repair (Astra rechecks and Architect repairs alike) was produced in one agent session under different role instructions. Run F is fresh code with fresh seeds. Governance should treat the next Astra recheck as the independent check, and may prefer a separate reviewer session.

## D4-C3-M1 source-bound calibration (bounded; Astra M1 + minors m8 / m9, after the D4-C3 recheck @5bb57eb2)

- **Defect.** After R3, `L_W` (two-way CR, 5-date blocks) is the only probability behind the positive REALIZED_WINDOW labels and every conditional prospective statement. Date persistence across blocks, which spec §9 names, makes it undercover in sparse designs that pass the information floor.
- **Reproduced** (run G, fresh code and seeds, 20,000 replications per cell): false positive 0.0789 [0.0752, 0.0826] (Astra 0.0805) and full-fill miss 0.0889 [0.0850, 0.0928] (Astra 0.0902). Over the declared class the R3 engine reaches 0.1287 at φ = 0.9 and exceeds 0.05 from φ = 0.5.
- **Decision.** Option (a), calibrate: `L_W = θ̂ − max_{b∈{5,10,20,30}} t_{df_b,0.95} SE_2w(b)` (spec 8.1b).
  - It is never above the R3 bound, and defined whenever INFO_SUFFICIENT.
  - The 30-date block is W, the trailing-bias window whose seasonal lag §9 names.
  - Stated level: P(reach ∧ L_W > θ_W) ≤ 0.05, with size ≤ 0.05, over the 5-date-block model and the declared persistence class 𝒟_P (daily AR(1) φ ≤ 0.9, latent variance ≤ 0.10, m ∈ {17, 35}, thin / full). Worst cell 0.0465 [0.0436, 0.0494]; 100,000-replication re-runs 0.0458 / 0.0464.
  - No level is claimed outside 𝒟_P: φ = 0.95 gives up to 0.072, φ = 0.97 up to 0.110.
- **Selection, disclosed.** The class, the pass criterion and the first candidate RM ({5, 10, 20}) were declared before any run. RM's preliminary run failed at φ = 0.9 (0.0708 at 100,000) and was not retuned. Comparators RE (two-way EWC, K = 4; φ = 0.9: 0.0557) and the adopted rule were then declared, with the criterion "validity over the whole class first". Only the adopted rule is valid over 𝒟_P.
- **Power cost** (no persistence, disclosed, not retuned):
  - SUPPORTED at θ = 0.10: 0.843 → 0.654 (thin, 17) and 0.633 → 0.565 (full, 35).
  - P(T2) at θ_PCE: 0.46–0.55 (R3 engine 0.67–0.78).
  - 80%-power effect ≈ 0.11–0.12 (R3 ≈ 0.09–0.10).
  - Information floor (60 / 25): nearly powerless (0.001–0.005).
- **Open observation (not repaired; frozen; outside the bounded mission).** T1a, NEG and U_W keep 5-date blocks. Under 𝒟_P they reach 0.089 (T1a, nominal 0.025), 0.069 (NEG, nominal 0.025) and 0.077 (U_W miss, declared 0.05). Spec 17.8 qualifies their stated levels at statement level only. Flagged for Astra / governance.
- **m8 / m9.**
  - m8: the frontier domain guard is now in spec 17.3, the manifest row and delta D4-C3.
  - m9: SUPERSEDED markers on power table §4.6 reading 5 (and its catastrophic-date table) and on delta D4-C2 "CLAIM STRENGTH".
  - R3-era coverage readings (power table §4.7 reading 4; delta D4-C3) are re-qualified.
- **Unchanged:** R*, h, W, signal, cohort, entry, T_entry, S_ref sizing, execution, 0.04 strata, κ_core, T1a, T1b, NEG, the PCE formula, GO / NO_GO, U_W (R1), R2's exclusion removal, the R3 transport algebra (Proposition 1, Theorem 2), the cost-mass ε, the frontier definition, the constants, the label vocabulary, SHADOW_CONTINUATION_SIGNAL, and the 11-value state machine.
- **Role independence.** This repair was produced in a fresh Architect context that wrote none of R1–R3 and none of the Astra audits. Run G is new code with new seeds. Astra's evidence directory was read, not reused.

## Independent checks performed

- Analytic: N_naive, MDE, date ceiling, label probabilities (power table §2–3), reproducing Astra §6.3 and Fable §1.1 exactly.
- Synthetic Monte Carlo runs A–C (power table §4.1–4.3; script at 94b5934; retired-bound columns labelled).
- Run D (power table §4.5): Astra A1 reproduced (θ = 0.0315, GO design with θ_PCE = 0.08; retired coverage 0.8885, false ERT exclusion 0.0742, false economic rejection 0.320 → repaired 1.0 / 0 / 0); Astra A2 reproduced (θ = 0.0852; retired coverage 0.8632, false LARGE exclusion 0.1126 → repaired 1.0 / 0); adversarial core class: coverage 0.9705–0.993, false ERT exclusion 0.019–0.0295; regression: tail-free run B row and run C seed 11 reproduce bit-for-bit.
- Run E (power table §4.6, `WEATHER_FORWARD_V2_D4_C2_SIM_2026-09-30.py`, fresh code and seeds): Astra C2 reproduced. V2-R1 false ERT exclusion was 0.0475 (S1 joint; 0.098 given GO ∧ INFO), 0.165–0.176 (p_t = 0.5), 0.314 (p_t = 1), 0.56 (date-clustered); false LARGE exclusion 0.147 at θ_P = 0.10; 414 of 1,002 grid cells > 0.05. By observed count: 92–93% exclusion with 0 observed rare legs whatever θ_P was, 0% with ≥ 1. **R2: 0 prospective exclusions and 0 R* rejections in all scenario, count and grid replications (268,400).** θ_W coverage by U_W ≥ 0.97 per scenario. R2-A never excludes. False prospective confirmation at θ_P = 0 under catastrophic-date alternatives ≤ 0.0378. Confirmation power unchanged (0.62 at θ_P = 0.10 tail-free, joint with GO ∧ INFO).

- Run F (power table §4.7, `WEATHER_FORWARD_V2_D4_C3_SIM_2026-09-30.py`, fresh code and seeds):
  - C3 reproduced: retired label false 0.4334 [0.4265, 0.4403] (thin) and 0.1175 [0.1130, 0.1220] (full); grid: above 0.05 in 55 of 148 non-positive cells, maximum 0.36.
  - R3: 0 unconditional prospective labels and 0 prospective exclusions in 443,000 replications; false window claims ≤ 0.043.
  - The conditional claim is false only through the L_W miss: 0.044–0.0552 at 20,000 replications, the carried D8 limitation.
  - The frontier lies below the true adverse cost share in every C3 design.
  - The cap-date observable flag fires 100% (cap96), ≈ 75% (template / stations) and 0% (hidden).
  - Frontier algebra verified: monotone decreasing; endpoints L_W − δ and −1.

- Run G (power table §4.8, `WEATHER_FORWARD_V2_D4_C3_LW_CAL_SIM_2026-10-01.py`, fresh code and seeds):
  - Astra M1 reproduced.
  - 156 class cells × 20,000 replications, 36 boundary, 15 outside-class, 16 power, 2 C3 and 3 × 100,000 re-runs.
  - Adopted rule: worst joint miss 0.0465 (re-runs 0.0458 / 0.0464), worst size 0.0423, boundary worst 0.0381.
  - C3 cells: 0 false window claims; conditional claim false only through the L_W miss (0.008 / 0.005).
  - repro-mode lines byte-identical to the class lines.

## Self-attack before READY — D4-C3-M1 (orchestrator mission)

| # | Required check | Result |
|---|---|---|
| 1 | Reproduce Astra M1 with fresh code and seeds (≥ 20,000) | PASS: 0.0789 [0.0752, 0.0826] vs 0.0805; 0.0889 [0.0850, 0.0928] vs 0.0902; three further Astra cells inside the run-G intervals |
| 2 | Repair on the counterexample cells and over the declared class (≥ 20,000 per cell; ≥ 100,000 near 0.05) | PASS: adopted rule ≤ 0.05 in all 156 cells (worst 0.0465 [0.0436, 0.0494]; 100,000-replication re-runs 0.0458 [0.0445, 0.0471] and 0.0464 [0.0451, 0.0477]); size ≤ 0.0423; Astra cells 0.0271 / 0.0319 / 0.0297 / 0.0382 / 0.0348 |
| 3 | Boundary: 60 / 25, dominant station, dominant date, no-persistence baseline, thick 35 / date | PASS: worst 0.0381; baseline ≤ 0.0174 (conservative, never anti-conservative: L_W ≤ R3's bound pointwise); 60 / 25 valid but nearly powerless (disclosed) |
| 4 | Regression: R1 / R2 / R3 surfaces byte-identical, 11 states, no unconditional prospective label, C3 cells | PASS: section-level byte comparison against 341e0b7a (delta D4-C3-M1 REGRESSION); C3 cells 0 false window claims, conditional claim false only via the L_W miss |
| 5 | Power cost reported honestly | PASS: power table §4.8; spec 1, 6.2, 7, 8.1b, 10.3, 24 |
| 6 | Committed script reproduces the committed output | PASS: repro mode = class lines byte-identical; stress / C3 / boundary / re-run cell 1073 re-run from the committed script byte-identical (resume checkpoint §3d) |
| 7 | No threshold, no tuning to a synthetic number | PASS: class and criterion declared first; RM failure published; no ε, δ, H or τ introduced |
| 8 | Capital / live / t0 / Builder | unchanged: FALSE / FALSE / NOT_DECLARED / FALSE |

## Self-attack before READY — R3 (mission §42)

| # | Question | Answer |
|---|---|---|
| 1 | What distribution does the prospective expectation use? | Q_H, the law of R*'s executed trades over the next H counted dates. It is unrestricted except for the mechanics and the declared class 𝒯_H(ε, δ) |
| 2 | What links Q to P? | Only 𝒯_H(ε, δ), which is declared and never verified, plus the mechanics (N ≥ −C, the date cost cap) |
| 3 | Can an unseen losing regime have identical observed covariates? | Yes (run F scenario 06) |
| 4 | What protects the claim then? | Nothing statistical. The claim is conditional: it holds only if the regime's cost mass is ≤ ε* |
| 5 | Is protection statistical or assumption-based? | The sampling part (θ_W ≥ L_W, 0.95) is statistical; the transport part is an explicit assumption with no α |
| 6 | Does ε measure the correct economic mass? | Yes: cost mass. Proposition 1 is exact for E[N]/E[C] |
| 7 | Could a rare high-capital date defeat a trade-count calculation? | Yes, which is why ε is cost mass; ε_1(H) and k*(H) are printed (one cap-date = 0.142 at H = 120, thin) |
| 8 | Is the ratio E[N]/E[C] handled exactly? | Yes (Proposition 1; no linearisation) |
| 9 | Can the forward signal still imply an unconditional edge? | No. It is renamed SHADOW_CONTINUATION_SIGNAL, its meaning is restricted to another paper/shadow epoch, and there is no capital path |
| 10 | Can a conditional claim be mistaken for unconditional confirmation? | Mitigated: the constant PROSPECTIVE_CONFIRMATION = NOT_ESTABLISHED_UNCONDITIONALLY, sentence (c), and REALIZED_WINDOW_ / CONDITIONAL_ prefixes |
| 11 | Is an ε threshold selected after seeing results? | No. None is selected; grids use existing constants |
| 12 | Is H outcome-blind? | Yes: {14, 30, 60, 120} are pre-existing V2 constants, reporting only |
| 13 | Does C2 remain closed? | Yes. No prospective exclusion label; run F 0 in 443,000; scenario 01 regression |
| 14 | Does R1 remain valid? | Yes. U_W is unchanged |
| 15 | Does any negative prospective rejection return? | No |
| 16 | Are false confirmations controlled over the declared class? | No unconditional confirmation exists. The conditional claim's error equals the L_W sampling miss: nominal 0.05, simulated 0.044–0.0552 (disclosed D8 limitation) |
| 17 | Can the Builder implement without choosing thresholds? | Yes. All formulas, grids and constants are frozen; no decision threshold exists |
| 18 | Is lack of transportability ever read as positive? | No. DECLARED_UNVERIFIED is not a pass; INDETERMINATE is never favourable |
| 19 | Can regime drift revoke an epoch? | Yes, in the future-epoch contract (revoke-only flags) |
| 20 | Is capital still unauthorised? | Yes |

## Self-attack before READY — R2 (mission §31, kept as history; answer 14 is refuted by Astra C3 and superseded by R3)

| # | Question | Answer |
|---|---|---|
| 1 | Can θ_P > θ_ERT while zero relevant tails appear? | Yes. Spec 8.5b construction; run E: 16–99% of windows contain no rare leg in the C2 scenarios |
| 2 | Can the protocol still output a prospective exclusion then? | **No.** No prospective exclusion label exists; 0 in 268,400 replications |
| 3 | Can a rare 0.001 type be absent from both the OP and the window yet economically important? | Yes. That is the theorem's jackpot-date alternative (P(absent) = (1 − η*)^134 ≥ 0.85) |
| 4 | Does an arrival bound cover it? | No arrival bound is used. R2-A was evaluated and rejected: it is invalid under date clustering and never excludes |
| 5 | Does dependence invalidate the argument? | No. The theorem allows any dependence and uses a date common mode, which V2 itself declares |
| 6 | Does fill selection alter the population estimand? | No. θ_P is over executed trades by the frozen estimand (8.5b); NO_FILL contributes nothing to N or C |
| 7 | Are unfilled eligible signals relevant? | Only descriptively (TAIL_ARRIVAL_REPORT); they are outside θ_P's population |
| 8 | Are core and tail denominators consistent? | Yes. U_W uses Σ_all C_j throughout (unchanged R1) |
| 9 | Are outcome and arrival uncertainty jointly covered at the declared level? | Prospective: no adverse claim, hence nothing to cover. θ_W: one stochastic component (core CR) plus a deterministic tail term, declared 95% |
| 10 | Can a new INDETERMINATE state become R*_REJECTED? | No. R*_REJECTED_AS_NET_STRATEGY is never issued (17.6); no rule reads REALIZED_WINDOW_BOUND |
| 11 | Has R* changed? | No (manifest D) |
| 12 | Was real outcome information used? | No. Synthetic run E and algebra only |
| 13 | Is loss of exclusion power honestly reported? | Yes: spec 8.5b, 17.3 sentence (b), 24, delta D4-C2, power table 4.6 |
| 14 | Does prospective confirmation remain valid? | (R2 answer, **refuted by Astra C3**) Yes. Bounded downside; run E false confirmation ≤ 0.0378 at θ_P = 0; T2 unchanged |
| 15 | Could a Builder implement it without scientific discretion? | Yes. U_W as R1, constant PROSPECTIVE_EXCLUSION, 3-row economic axis, fixed TAIL_ARRIVAL bins, CORE_ADVERSE rule; no tuning parameter |

## Remaining limitations (none CRITICAL)

0. **MINOR (cost of R3, disclosed):** no unconditional prospective verdict in either direction. Prospective content is conditional on the declared, unverified transport class. Hidden regimes with identical covariates are covered only by the ε budget. (The R3 statement "source bound ≈ 0.5 pp liberal" is SUPERSEDED by D4-C3-M1: the calibrated bound holds 0.05 over the declared persistence class 𝒟_P and no level is claimed outside it.)
0a. **MINOR (cost of D4-C3-M1, disclosed):** the calibrated T2 costs confirmation power (80%-power effect ≈ 0.11–0.12 instead of ≈ 0.09–0.10; nearly powerless at the 60-date floor). Outside 𝒟_P (φ ≥ 0.95) the source bound's miss is higher (up to 0.110) and is not claimed. Given reach, the miss is larger than the joint rate (disclosed).
0b. **OPEN OBSERVATION (frozen surfaces; not repaired by D4-C3-M1):** T1a, NEG and U_W keep 5-date blocks and exceed their nominal levels under 𝒟_P (T1a 0.089 at nominal 0.025; NEG 0.069; U_W miss 0.077 at φ = 0.9). Their 17.8 statements are qualified. Calibrating them needs governance authority; the same multi-block construction would apply.
1. **MINOR (cost of R2, disclosed):** prospective economic exclusion is not usefully testable within V2's horizon (no valid test has power > ≈ 0.06); V2's negative results are information-level (NEG / R*_CORE_INFORMATION_REJECTED) and realised-window (θ_W, attainable only when the realised tail is small). No capital decision changes, because deployment always required prospective confirmation.
2. **MINOR:** GO/NO_GO will likely be NO_GO if the post-bias-correction leg mix resembles Astra's b = 0 cross-section (σ_eff ≈ 2.9 → θ_PCE ≈ 0.18–0.26); an honest pre-declared outcome.
3. **MINOR:** CR engine size with ≈ 24 date blocks and ≈ 40 stations runs near nominal; T1a ≈ 1.3× its 0.025 component level (Astra: PASS for T1 union and T2).
4. **MINOR:** D10 bias contamination by NO_DATA_LOWEST settlements accepted as frozen and disclosed.
5. **MINOR:** PINM dependence is ASSUMED (gates only the rare-event tail count T1b).

## Blockers

None within the bounded M1 mission. Astra's V2 verdict remains BLOCKED until Astra rechecks D4-C3-M1. Open observation 0b (frozen surfaces) is for Astra / governance. Procedure items before t0: manifest V2 section B.

## Next action

ASTRA BOUNDED D4-C3-M1 RECHECK ONLY, of the exact D4-C3-M1 commit (M1, m8, m9; regression of the R1 / R2 / R3 surfaces). Builder remains unauthorised; t0 is not declared; no capital.
