# ASTRA — WEATHER FORWARD V2 — BOUNDED CYCLE-2 (D4-C3-M2) RECHECK — 2026-10-01

```text
ASTRA_ROLE              = independent adversarial scientific reviewer (fresh context; bounded cycle-2 recheck; no repair authority)
AUDIT_BRANCH            = astra/weather-forward-v2-independent-reaudit-2026-09-29
ASTRA_START_SHA         = 7408c0c58fb0869c9f14ab686cbc7b0074cbf185
PREVIOUS_ASTRA_VERDICT  = ac777a87 (BLOCKED_D4_M1_SOURCE_BOUND_LEVEL_NOT_ATTAINED_OVER_DECLARED_CLASS_AND_FROZEN_SURFACE_UNDERCOVERAGE)
AUDITED_BRANCH          = claude/charming-allen-948kd8
AUDITED_SHA             = 61f4904f94f8662084fa5245c92b647c061148ae   (ancestor 4423c5c3fe36c1d425b832ef87a9a774913377b4 verified)
ASTRA_WEATHER_V2_D4_C3_M2_RECHECK = BLOCKED_D4_M2_GO_GATE_CONTRADICTED_BY_CALIBRATED_POWER_AND_LEVEL_EXCEEDED_AT_FAVOURITE_PRICE_CONCENTRATION
ASTRA_WEATHER_V2_SCIENTIFIC_CONTRACT = BLOCKED (see 15)
EXPERIMENT_FEASIBILITY_V2 = BLOCKED_POWER_NEGATIVE_RESULT_INSTRUMENT_INFEASIBLE_AND_T2_POWER_BELOW_FROZEN_GO_RATIONALE
OUTCOME_INFORMATION_USED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
t0                      = NOT_DECLARED
BUILDER_AUTHORIZED      = FALSE
```

## 1. Authority

| Check | Result |
|---|---|
| `origin/claude/charming-allen-948kd8` (fetched) | `61f4904f94f8662084fa5245c92b647c061148ae`: MATCH; re-verified before commit |
| 4423c5c3 ancestor of 61f4904f | yes |
| Astra branch remote head at start | `7408c0c58fb0869c9f14ab686cbc7b0074cbf185`: MATCH |
| Files changed 4423c5c3 → 61f4904f | only `research/weather_forward/`: spec, manifest, delta, power table, architect state, resume checkpoint, ARCHITECT_PROGRESS_CYCLE2, run-H script + two raw outputs. Nothing else in the repository changed |
| `QUANT_NORTH_STAR.md` | unchanged (last touched by 31f7169, long before 94b59348) |
| Spec section byte comparison (`out_spec_section_diff.txt`) | Identical: §3, §4, §4.1, §5–§5.3, §6, §8, §8.2, §8.6, §8.7, §10, §10.2, §11–§11.3, §11.5, §12–§12.4, §13, §14–§14.3, §15–§15.3, §16, §17, §17.1, §17.2, §17.4–§17.7, §18, §19, §22, §23, §25. Changed: header, §1, §2, §6.1–§6.3, §7, §8.1, §8.1b (markers), new §8.1c, §8.3, §8.4, §8.5, §8.5b (one line), §8.5c, §9, §10.1, §10.3, §11.4, §17.3, §17.8, §20, §21, §24, §26, §27 |
| Owner-frozen surfaces (R*, h, W = 30, signal, cohort, entry, T_entry, S_ref, execution, 0.04 CORE/TAIL split) | §3, §5.2, §11.1–§11.3, §12, §14, §15 byte-identical to 4423c5c3: **unchanged** |
| Outcome information | none used by the candidate (synthetic only) or by this audit |
| Commit order | run-H script and both raw outputs land together in 791083d (WIP); the "declared before any run" claim is self-attested and not verifiable from git (as in cycle 1). The selection is reproducible from the committed raw output (§6) |

## 2. Independence disclosure

- Fresh Astra context. I wrote neither the D4-C3-M2 repair nor any earlier audit or repair.
- All simulation uses my own engine `astra_m2_engine.py`, written from the spec text at 61f4904f and extending Astra's own cycle-1 engine; it does not import or copy run-H code. Seeds `SeedSequence([77200201, plan, cell, chunk])`.
- `test_m2_engine.py` checks the two-way CR at b = 5/10/20/30 against a direct trade-level implementation (exact), the exact Gaussian and two-state thresholds (|F(q) − p| < 1e-10) and the shapes (variance ≈ 1, acf as declared).
- The Architect's script was only re-run (§9). Its raw output was used for one thing: re-deriving the λ selection arithmetic (§6).
- The R3 algebra and state-machine scripts are Astra's cycle-1 scripts, re-run unchanged.

## 3. Reproduction: counterexamples under OLD (4423c5c3) and NEW (61f4904f) rules

Same replications for both rules; joint with reach; 120 + 14 dates, 48 stations, m = 17, latent (0.05, 0.05, 0.10) + one persistent component. 100,000 replications where marked, otherwise 20,000. Wilson 95% where shown.

| Cell (Astra @ac777a87 counterexample) | Reach | OLD | NEW | Architect (NEW) |
|---|---|---|---|---|
| M1-R favourite c ~ U(0.70, 0.90), AR φ 0.9 rv 0.05, thin, θ 0.10: L_W miss (100k) | 0.979 | **0.0633** | **0.0114 [0.0107, 0.0120]** | 0.0114 |
| same, θ_W = 0: false REALIZED_WINDOW positive (100k) | 0.902 | 0.0600 | 0.0107 [0.0101, 0.0114] | 0.0100 |
| same θ = 0 cell: T1a / NEG / U_W miss (100k) | 0.902 | 0.1155 / 0.0680 / 0.0665 | 0.0041 / 0.0005 / 0.0003 | — |
| favourite, rv 0.10: miss / size | 0.84 / 0.58 | 0.0838 / 0.0716 | 0.0223 / 0.0175 | 0.0209 / 0.0168 |
| 30 random paused dates, mid, AR 0.9 rv 0.05, θ 0.10 (100k) | 0.841 | 0.0540 | 0.0077 [0.0071, 0.0082] | 0.0069 |
| two-state φ 0.9 rv 0.05 | 0.798 | 0.0521 | 0.0120 | 0.0107 |
| literal §9 trailing mean 30, rv 0.05: miss / size | 0.76 / 0.66 | 0.0585 / 0.0535 | 0.0115 / 0.0095 | 0.0114 / 0.0097 |
| M2 mid AR 0.9 rv 0.05 thin κ = 0: T1a / NEG / U_W miss (100k) | 0.668 | 0.0891 / 0.0679 / 0.0685 | 0.0018 / 0.0012 / 0.0007 | 0.0018 / 0.0009 / 0.0008 |
| M2 rv 0.10: T1a / NEG / U_W | 0.267 | 0.0635 / 0.0369 / 0.0381 | 0.0032 / 0.0018 / 0.0014 | 0.0037 / 0.0019 / 0.0014 |
| M2 full fills rv 0.05: T1a / NEG / U_W | 0.675 | 0.0883 / 0.0685 / 0.0695 | 0.0019 / 0.0013 / 0.0009 | — |
| M2 trailing mean 30 rv 0.05: T1a / NEG / U_W | 0.664 | 0.1227 / 0.0919 / 0.0929 | 0.0046 / 0.0027 / 0.0021 | — |
| outside: φ 0.95 favourite (disclosure) | 0.975 | 0.0994 | 0.0265 | 0.0303 |

- Every cycle-1 counterexample reproduces under the OLD rule within MC error of Astra @ac777a87 (0.0635 → 0.0633; 0.0605 → 0.0600; 0.0531 → 0.0540; M2 0.0888 / 0.0707 / 0.0755 → 0.0891 / 0.0679 / 0.0685 at 100,000).
- Every one is repaired under the NEW rule, and my NEW numbers match the Architect's within MC error.
- Monotonicity: over all my runs (11,977,228 reached replications) the new L_W was never above the old L_W, and the new U_W never below the old U_W (0 / 0).
- Headline consistency: REALIZED_WINDOW_LOSS_CONFIRMED with a headline interval not below 0 occurred 0 times; L_W > U_W never occurred.

## 4. Class verification over 𝒟_P* (independent)

`out_sample_20000.jsonl`: 175 in-class cells × 20,000. The sample is the Architect's 8 worst run-H cells per surface (L_W miss, size, U_W, T1a, NEG), 110 random cells of the 900-cell main grid and 40 random cells of my slice plan (m 35, θ 0.05, D 60 / 90 with contiguous pauses, hemisphere / station regimes, TAIL 1% / 3% mixes). I also ran the 16 repro cells.

| Surface (stated level) | Worst in my sample (joint with reach) [Wilson 95%] | Cell | Architect worst |
|---|---|---|---|
| L_W miss (0.05) | **0.0418 [0.0391, 0.0446]** | trailing mean 30, rv 0.10, favourite, 30 contiguous paused, m 17 thin, θ 0.10 | 0.0395 (20k) / 0.0415 (100k) |
| T2 false positive (0.05) | 0.0340 [0.0315, 0.0366] | same geometry, θ 0, full | 0.0353 |
| U_W miss (0.05) | 0.0093 [0.0080, 0.0107] | two-state φ 0.9 rv 0.10, mid, 30 contiguous paused | 0.0089 |
| T1a (0.025) | 0.0199 [0.0181, 0.0219] | trailing mean 30 rv 0.10 favourite, 30 contiguous paused | 0.0198 |
| NEG (0.025) | 0.0110 [0.0096, 0.0125] | two-state φ 0.9 rv 0.10, mid, 30 contiguous paused | 0.0106 |
| headline [L_W, U_W] non-coverage (0.10) | 0.0429 [0.0402, 0.0458] | as L_W | 0.0429 (100k) |
| T1b (0.025), `out_t1b_20000_2000.jsonl` | 0.0071 [0.0060, 0.0083] | m 35 full, 3% TAIL, no persistence | 0.0077 |
| T1 = T1a ∪ T1b (0.05) | 0.0095 | 1% TAIL, two-state φ 0.9 rv 0.10 | 0.0089 |

- **On the enumerated 𝒟_P* grid the stated levels hold.** I measured no in-class value above its stated level. Margins: L_W ≈ 0.8 pp, T1a ≈ 0.5 pp, others large.
- Selection reproducibility (m14): applying the declared criterion to my independent 188 cells selects λ_θ = 1.75 (not 1.70), because my worst cell is 0.0418 > 0.040. That is MC noise at the target boundary. The stated level ≤ 0.05 is unaffected.
- Conditional on reach (disclosed, not a stated level): my in-class off-grid cell D 60, 30 contiguous paused, two-state φ 0.9 rv 0.10 gives L_W miss 0.203 given reach (reach 0.109). The spec's "up to 0.182" is a run-H grid figure (m13).

## 5. Second-order search (`out_probe*`, `out_probe100_100000.jsonl`)

### 5.1 New finding M3: favourite price concentration inside "CORE prices to 0.90"

The level text printed in every report (17.3 SOURCE_LOWER_BOUND) and the 8.5c error statement describe the class as "CORE prices to 0.90" / "CORE prices including favourite-heavy mixes up to 0.90". The calibration used one favourite law, U(0.70, 0.90). R* buys a NO leg at ask a iff 1 − q − a − f(a) ≥ 0.10, so legs at 0.80–0.89 are exactly R*'s high-confidence NO legs: the left-skewed case 8.4 names. Concentrating prices there, at declared dependence shapes and calendars:

| Cell (m 17; trailing mean 30, rv 0.10 = the §9 mechanism at the declared maximum variance) | N | Reach | NEW L_W miss [95%] | NEW T1a | OLD (4423c5c3) |
|---|---|---|---|---|---|
| c ~ U(0.85, 0.90), full, θ 0.10, 30 contiguous paused | 100,000 | 0.974 | **0.0587 [0.0573, 0.0602]** | — | 0.1491 |
| same, thin fills | 100,000 | 0.974 | **0.0557 [0.0543, 0.0571]** | — | 0.1452 |
| same, full, **no pauses** | 100,000 | 0.974 | **0.0523 [0.0509, 0.0537]** | — | 0.1375 |
| c ~ U(0.85, 0.90), thin, θ 0, 30 contiguous paused | 100,000 | 0.752 | 0.0439 (size) | **0.0262 [0.0253, 0.0273]** | T1a 0.1998 |
| c ~ U(0.80, 0.90), thin, θ 0.10, 30 contiguous paused | 100,000 | 0.930 | 0.0506 [0.0492, 0.0520] | — | 0.1381 |
| c ~ U(0.85, 0.90), 30 random paused, full, θ 0.10 | 20,000 | 0.984 | 0.0522 | — | — |

Worst cell per price law and dependence shape over calendars, fills and θ ∈ {0, 0.05, 0.10} (`out_probe2_summary.txt`, 20,000 each):
- the exceedance is confined to the trailing-mean-30, rv 0.10 shape: U(0.85, 0.90) 0.0604, U(0.80, 0.90) 0.0512;
- AR 0.9 / two-state 0.9 / trailing 15 / trailing 30 at rv 0.05 stay ≤ 0.036;
- a point mass at 0.90 gives 0.0555–0.0708, but R* cannot buy at 0.90 (it would need q > 1), so I treat it as a bound only;
- T2 size stays ≤ 0.046, U_W ≤ 0.002 and NEG ≤ 0.003 in every price-concentration cell.

Assessment:
- **This is the M1-R pattern at smaller magnitude.** The frozen manifest row PERSISTENCE_CLASS_DP_STAR enumerates the price laws and says "no level claimed between grid points", and 8.1c calls the class a "reference family … not a proof about every dependence law". But:
  - the printed level text (17.3) and the 8.5c error statement state the class as "CORE prices to 0.90";
  - 8.1c claims the family is "broad enough to contain every mechanism the spec names";
  - the 80% margin was introduced precisely because "a class is never exhaustive", and it is exhausted by a price law R*'s own rule generates.
- Under the cycle-1 precedent (0.0531 [0.0517, 0.0544] with 30 paused dates counted towards M1-R), an exceedance with a CI excluding 0.05 inside the printed class text is material. The size of T2's false positive is not affected. What is affected: the sampling event used by the transport statement and by sentence (c), and T1a.
- **Severity: MAJOR (statement-level; cheap to repair).**

### 5.2 Other probes (20,000 each; the fixed slice is trailing mean 30 rv 0.10, favourite U(0.70, 0.90), 30 contiguous paused, m 17 full; worst over θ ∈ {0, 0.10})

| Probe | Worst NEW L_W miss | Status |
|---|---|---|
| m 8 / 12 / 25 / 50 (class has m ∈ {17, 35}) | 0.0357 / 0.0386 / 0.0395 / 0.0208 | holds |
| trailing mean L 20 / 25 (between grid points) | 0.0271 / 0.0334 | holds (monotone in L) |
| trailing mean L 40 / 45 (not named; "30-date lag" is the printed limit) | 0.0533 / 0.0638 | outside; disclose |
| AR 0.85 / two-state 0.85 / AR 0.9 rv 0.07 / trailing 30 rv 0.07 (gaps) | 0.0163 / 0.0153 / 0.0205 / 0.0316 | holds |
| two-state 0.95 / AR 0.95 (outside) | 0.0684 / 0.0544 | outside, disclosed class boundary |
| pauses as two runs / at the start / at the end; P 10 / 20 | 0.0384 / 0.0483 / 0.0451; 0.0437 / 0.0420 | holds; "early" contiguous run 0.0483 is inside "one contiguous run at a random interior start", margin 0.2 pp |
| D 60 / 90 with 30 contiguous paused | 0.0352 / 0.0402 | holds |
| θ −0.05 / −0.10 / +0.05 / +0.15 | 0.0324 / 0.0262 / 0.0372 / 0.0431 | holds (negative θ is not in the class's effect grid but holds) |
| favourite + 3% TAIL; mid + 5% / 10% TAIL | 0.0042; reach 0.002–0.004; NO_GO | holds / NO_GO |
| OP prices mid, window favourite (price drift after GO) | 0.0408 | holds |
| two persistent components (outside by declaration) | 0.0462 | outside; holds |
| U(0.60, 0.90) | 0.0355 | holds |

- **Semantic aliases.** The stated level is nominal everywhere it is stated (0.05 / 0.025 / ≥ 0.90). The 0.040 / 0.020 targets appear only as calibration targets. The class wording differs across sections: the manifest is enumerated, while 17.3, 8.5c, §21 item 43, §27 and the delta say "CORE prices to 0.90". That difference is M3.
- **Regressions.** None found in R1 / R2 / R3 surfaces (§8).

## 6. Freeze and implementability (C)

| Item | Finding |
|---|---|
| Rule | Fully specified and mechanical: blocks {5, 10, 20, 30}, calendar alignment floor((D − D_0)/b), df_b = min(G_B(b), G_S) − 1, q 0.95 / 0.975, λ_θ = 1.70 / λ_κ = 1.60 frozen in §10.1 and manifest CALIBRATED_BOUNDS; IF4 / IF5 / GO unchanged (reach unchanged); df_b ≥ 1 whenever INFO_SUFFICIENT (IF2) |
| Outcome-blindness | No real Weather outcome, price, P&L or settlement used; λ selected on synthetic output only |
| Pre-declaration | The class, family, grid, 0.040 / 0.020 targets and confirm-or-move-up rule are in the run-H header. Their being written before any run is self-attested; git cannot order them (791083d contains script and outputs) |
| Selection arithmetic | **Reproduced** from the committed raw output (`out_verify_arch_selection.txt`): 1,183 in-class reached cells; smallest grid λ meeting the criterion is λ_θ = 1.70 (worst 0.0395, class idx 887) and λ_κ = 1.60 (T1a 0.0198, idx 886). 1.65 fails (0.0423) |
| "80% of nominal" | A defensible, declared engineering margin and a selection target only; it is not stated as a level anywhere. With independent replications the same criterion would select 1.75 (§4; MC noise at a hard threshold), so it is not a sharp, reproducible selector. It does not have to be: validity rests on the stated nominal level, which holds on the grid |
| Stated vs claimed level | Nominal (not calibrated) levels are stated everywhere, joint with reach, over 𝒟_P*. Conditional-on-reach rates disclosed (m13 for the "up to 0.182" figure) |
| PINM B | The sim uses B = 2,000; spec B = 20,000. The finite-B p-value (1 + #)/(B + 1) is valid under the declared copula for any B, and T1b is measured conservative. Not a defect |

## 7. Power and feasibility (D)

Independent power (`out_power_20000.jsonl`, `out_power2_20000.jsonl`; joint with reach; no persistence; 20,000 each):

| Design (m 17) | θ_PCE (modal) | P(T2) at θ_PCE, NEW (OLD λ = 1) | NEW 80%-power effect | T1a power at θ 0.10 | NEG power at θ −0.12 (κ) | NEG (5-date, pre-repair) |
|---|---|---|---|---|---|---|
| mid U(0.35, 0.80), thin / full | 0.09 / 0.08 | 0.111 (0.547) / 0.081 (0.473) | ≈ 0.18 | 0.078 / 0.080 | 0.116 / 0.115 (κ ≈ −0.069) | 0.888 |
| m 35 mid, thin / full | 0.07 | 0.069 / 0.070 (reach 0.66) | ≈ 0.25 (reach-limited) | 0.13 | 0.166 / 0.163 | 0.576 |
| 50/50 mix, thin / full | 0.07 | 0.134 / 0.148 | ≈ 0.125 | 0.41 | 0.30 (κ ≈ −0.08) | 0.97 |
| favourite U(0.70, 0.90), thin / full | 0.05 | 0.211 / 0.234 | ≈ 0.08 | 0.90 | 0.60 (κ ≈ −0.096); 0.13 at κ ≈ −0.064 | 0.99 / 0.95 |

- **The Architect's numbers reproduce:** P(T2) 0.109 / 0.084 / 0.067 / 0.070; 80%-power effect ≈ 0.18 for mid prices; T1a 0.007 / 0.079 / 0.888; NEG 0.116 / 0.004.
- **What the spec does not show:** power depends strongly on the executable price mix. Over the GO-feasible laws, P(T2) at θ_PCE is 0.07–0.23 and the 80%-power effect is 0.08–0.18, i.e. about 5 × SD(θ̂) rather than the 2.49 × SE0 of the θ_PCE formula (ratio ≈ 4.9–5.2 in every law measured). NEG at the public-bot scale (−0.064 to −0.07 per share) has power 0.12–0.13 in every law measured.

Oracle benchmark (`out_oracle_benchmark.txt`; normal approximation):
- Under 𝒟_P*'s worst member (trailing mean 30, rv 0.10), the true sampling SD of θ̂ is 2.96× (mid) and 2.52× (favourite) its no-persistence value.
- A non-adaptive test that knows the worst-case SD exactly, and is valid there, has power 0.008 (mid) / 0.19 (favourite) at θ_PCE under no persistence. Its 80%-power effect is 0.21 / 0.077.
- The calibrated λ construction does slightly better (0.11 / 0.21), because its multi-block SEs adapt. **The power loss is therefore mostly intrinsic to the declared class at a 120-date horizon, not waste in the construction.** It cannot be recovered by re-calibrating inside V2. Only a longer window, an outcome-blind narrower class justified by external non-outcome evidence (for example historical forecast-error persistence, which is not trading outcome information), or a different design can recover it.

Honesty of the statements:
- §6.2, §7, §10.3, §24, §27, §21 item 46, the manifest TARGET_POWER and power table §4.9 state the collapse and that GO no longer implies material T2 power.
- Not honest (m12, stale):
  - §1, last paragraph: V2 "adds a **well-powered**, stratified information axis … that can say 'the rule's chosen legs are not underpriced'";
  - §21 item 1, "V2 still claims power it does not have | **Refuted**", which contradicts item 46.

Judgement:
- **(i) Contract validity — GO gate (P1, MAJOR).**
  - GO / NO_GO is the start decision. Its frozen rationale (§10.3) is twofold:
    - PCE_CEILING exists so that V2 does not start a design that "can confirm only edges larger than 0.10 … [and would] spend five calendar months to issue INDETERMINATE for every plausible truth";
    - SE_KAPPA_CEILING exists so that NEG "still rejects a public-bot-like loss rate (about −0.07 per share) with power ≈ 0.9; beyond that ceiling V2 would lose its only real negative result".
  - Under the tests actually run:
    - every mid-price GO design has an 80%-power effect ≈ 0.18 > 0.10;
    - **no** GO design measured has NEG power above 0.13 at −0.07.
  - The spec keeps GO unchanged and says it "no longer implies" these properties. It does not say what a GO now certifies, and it would start designs that its own frozen criterion says must not be started.
  - That is a decision the contract markets (the start decision and its "real negative result" justification) but cannot make. It is internally inconsistent, not merely low-powered.
  - It is repairable at the gate / statement layer, outcome-free, and only in the stricter direction:
    - (a) recompute θ_PCE and SE0_κ's ceiling for the calibrated tests (e.g. replace Z_80 by the synthetic effective multiplier ≈ 5.0 and recalibrate the κ ceiling for NEG's real power), which makes GO honest design by design (favourite-heavy designs may still pass; mid designs NO_GO);
    - or (b) governance explicitly redefines what GO certifies (a valid but weak, positive-side experiment without a usable negative-result instrument) and rewrites §1, §10.3, §21 item 1 and §24 to match.
- **(ii) Feasibility (EXPERIMENT_FEASIBILITY_V2 = BLOCKED).**
  - The negative-result instrument at the −0.07 per share scale is unattainable at 120 dates over 𝒟_P* (power ≤ 0.13 in every GO-feasible law measured). At this horizon this is **fundamental** (oracle benchmark), i.e. a governance / resource decision: horizon, class evidence, or retirement.
  - T2 confirmability is design-dependent (80%-power effect 0.08–0.18).
- **(iii) Not a fundamental non-identifiability of the contract as such.** The tests are valid on the grid and could be honestly gated. So the overall classification is **REPAIRABLE_BOUNDED** for the contract, with a feasibility consequence that only governance can accept or change.

## 8. R3 and frozen-surface re-verification (E)

| Surface | Result |
|---|---|
| Proposition 1, Theorem 2 (L_T = (1 − ε)(L_W − δ) − ε for any L_W) | `out_r3_algebra.json`: 59,600 random epoch laws, 0 identity / Theorem-2 violations (max rel. error 6e-12); min N/C = −1 exactly over 300,000 fee-inclusive trades; cost-mass counterexample unchanged (date / trade share invalid, cost mass exact). Identical to cycle 1. 8.5c changed only in the L_W definition sentence, the error statement and the m10 wording |
| ε* domain guard | present in 17.3 and manifest ROBUST_BOUND; 3,000 cases vs brute force: 0 mismatches; guard prevents 3 / 6 at L_W −1.5 / −1.2 |
| k*(H) | 3,000 cases: 0 mismatches |
| 11-state machine | §17.1 / §17.2 / §17.5 / §17.6 byte-identical; `out_states.json`: 4,608 combinations → exactly 11 SCIENTIFIC_STATE values; T1a ∧ NEG still impossible under the λ rule (κ̂ − λH > 0 and κ̂ + λH < 0 are exclusive) |
| SHADOW_CONTINUATION_SIGNAL | unchanged; only from {INFORMATION_DETECTED, NO_INFORMATION_DETECTED}__REALIZED_WINDOW_VALUE_SUPPORTED with CORE_ADVERSE = FALSE |
| ε / δ / H / τ thresholds | none; grids reporting-only |
| Unconditional prospective labels | none; PROSPECTIVE_* constants; R*_REJECTED_AS_NET_STRATEGY never issued; claim-language scan of all V2 files: forbidden phrases appear only as history / negation |
| Owner-frozen sections | byte-identical to 4423c5c3 (§1 of this report); North Star unchanged |

## 9. Raw-output reproduction (F)

- The Architect's script was copied byte-for-byte (sha256 84b0a9be…) and run as `astra 20000` and as `cell class 887 100000`.
- **Byte-identical** to the committed RUN_H lines 1–12 and to CONFIRM line 1 (0.0415 [0.0403, 0.0427]).
- Synthetic only.

## 10. Claim matrix (17.8 at 61f4904f)

| Row | Stated level | Holds? |
|---|---|---|
| REALIZED_WINDOW_VALUE_SUPPORTED / NOT_ROBUST | size ≤ 0.05 joint over 𝒟_P* | yes on the grid (≤ 0.0340); also ≤ 0.046 under favourite concentration |
| TRANSPORT / CONDITIONAL_PROSPECTIVE_SUPPORT | sampling miss ≤ 0.05 joint over 𝒟_P* | on the grid yes (0.0418); **no** under the printed "CORE prices to 0.90": 0.0523–0.0587 (M3) |
| REALIZED_WINDOW_BOUND | 95% joint | yes (≤ 0.0093) |
| INFORMATION_DETECTED | FWER ≤ 0.05, T1a ≤ 0.025 | on the grid yes (0.0199); T1a 0.0262 [0.0253, 0.0273] under favourite concentration (M3) |
| NEGATIVE_INFORMATION / CORE_ADVERSE | 0.025; "power ≈ 0.12 at −0.07 (disclosed)" | level yes (≤ 0.0110); power disclosed correctly for mid prices; ≤ 0.13 in every law measured |
| PROSPECTIVE_*, R*_REJECTED_AS_NET_STRATEGY, SHADOW, OPERABILITY | constants / never / shadow-only / descriptive | yes |
| Rejects R*? / Builder? / Capital? | all "no" | yes |

## 11. D1–D12 regression

| Item | Status at 61f4904f |
|---|---|
| D1 power / PCE | **REOPENED (MAJOR, P1):** GO / θ_PCE / SE_KAPPA_CEILING keep a frozen rationale the calibrated tests contradict; feasibility BLOCKED |
| D2, D3, D5, D6, D7, D9, D11, D12 | CLOSED (sections byte-identical) |
| D4 | **OPEN_MAJOR (M3):** M1-R and M2 repaired on the enumerated 𝒟_P* grid (independently verified); residual level exceedance at favourite price concentration within the printed class text |
| D8 | CLOSED; engine re-qualified by 8.1c and verified |
| D10 | CLOSED_ACCEPTED_AND_DISCLOSED |

## 12. Minors

| Minor | Status |
|---|---|
| m10 | **CLOSED**: 8.5c wording replaced; delta D4-C3 size line marked SUPERSEDED; §2 rows D4-C3-M1 and D4-C3-M2 present; "the level is lower" → "the miss is higher (coverage lower)" |
| m11 | **CLOSED**: sentence (c) carries "a repeated-experiment rate counted jointly with reaching an evaluated state, not a confidence given that this label was printed" |
| T1b proof gap | **CLOSED** by measurement (Architect ≤ 0.0077; Astra ≤ 0.0071, T1 ≤ 0.0095) |
| m12 (new) | stale power marketing: §1 "well-powered" information axis; §21 item 1 "Refuted" (contradicts item 46) |
| m13 (new) | the conditional-on-reach disclosure "up to 0.182" is a grid figure; an in-class off-grid cell (D 60, 30 contiguous paused, two-state φ 0.9 rv 0.10) gives 0.203 |
| m14 (new, informational) | the 0.040-target λ selection is MC-noise sensitive at the boundary (independent replications select 1.75); the stated level is unaffected |

## 13. Subverdicts

```text
M1R_M2_REPRODUCED_ON_OLD_RULE        = TRUE (fav 0.0633 / 0.0600 @100k; 30 paused 0.0540 @100k; M2 0.0891 / 0.0679 / 0.0685 @100k)
M1R_M2_REPAIRED_ON_NEW_RULE          = TRUE (0.0114 [0.0107,0.0120] / 0.0107 / 0.0077 @100k; M2 0.0018 / 0.0012 / 0.0007 @100k)
D4_M1_SOURCE_BOUND_CALIBRATION       = PASS over the enumerated D_P* grid (independent worst 0.0418 [0.0391,0.0446]; Architect
                                       0.0415 [0.0403,0.0427] @100k reproduced byte-identically); BLOCKED (M3) under the printed
                                       class text "CORE prices to 0.90": U(0.85,0.90) 0.0587 [0.0573,0.0602] @100k (0.0523 without pauses)
D4_INFORMATION_AND_UW_CALIBRATION    = PASS on the grid (T1a <= 0.0199, NEG <= 0.0110, U_W <= 0.0093, T1b <= 0.0071, T1 <= 0.0095,
                                       headline non-coverage <= 0.0429); T1a 0.0262 [0.0253,0.0273] under favourite concentration (M3)
D4_R1_REALIZED_WINDOW_BOUND          = PASS (algebra, tail supremum, calibrated core; headline [L_W, U_W] consistent: 0 inversions)
D4_R2_PROSPECTIVE_EXCLUSION_REMOVAL  = PASS
D4_R3_TRANSPORT                      = PASS (Proposition 1, Theorem 2, cost-mass eps, frontier + guard, k*(H), semantics, 11-state
                                       machine, SHADOW_CONTINUATION_SIGNAL); its sampling level is carried by M3
D4_R3_POWER_CEILING_THEOREM          = SUPPORTED (unchanged)
FROZEN_OWNER_SURFACES                = UNCHANGED (byte-identical); QUANT_NORTH_STAR unchanged
RAW_OUTPUT_REPRODUCTION              = PASS (byte-identical)
SELECTION_ARITHMETIC                 = REPRODUCED (1.70 / 1.60 from committed raw output); pre-declaration self-attested
m10 = CLOSED; m11 = CLOSED; T1b_PROOF_GAP = CLOSED; m12, m13, m14 = NEW (minor / informational)
EXPERIMENT_FEASIBILITY_V2            = BLOCKED_POWER_NEGATIVE_RESULT_INSTRUMENT_INFEASIBLE_AND_T2_POWER_BELOW_FROZEN_GO_RATIONALE
TRADING_RULE_CHANGED = FALSE; OUTCOME_LEAKAGE = NONE
```

## 14. Verdict

```text
ASTRA_WEATHER_V2_D4_C3_M2_RECHECK    = BLOCKED_D4_M2_GO_GATE_CONTRADICTED_BY_CALIBRATED_POWER_AND_LEVEL_EXCEEDED_AT_FAVOURITE_PRICE_CONCENTRATION
ASTRA_WEATHER_V2_SCIENTIFIC_CONTRACT = BLOCKED
NEXT_AUTHORIZED_ACTION               = GOVERNANCE FEASIBILITY DECISION (accept a V2 without a usable negative-result instrument /
                                       lengthen the horizon / retire) TOGETHER WITH a BOUNDED ARCHITECT GATE-AND-STATEMENT REPAIR
                                       (P1, M3, m12, m13); NO BUILDER
CRITICAL_FINDINGS = NONE
MAJOR_FINDINGS    = P1 (GO / θ_PCE / SE_KAPPA_CEILING decision gate contradicted by the calibrated tests), M3 (level exceeded at
                    favourite price concentration inside the printed class text)
MINOR_FINDINGS    = m12, m13 (m14 informational); m10, m11 CLOSED
CLASSIFICATION    = REPAIRABLE_BOUNDED (contract: gate / statement layer, outcome-free, stricter-only); the feasibility limitation of
                    the negative-result instrument at 120 dates is FUNDAMENTAL at this horizon and is a governance / resource decision
```

### 15. Blocker detail

**PRIMARY_BLOCKER: P1 (MAJOR).**
- **Defect.** The start decision GO / NO_GO and its frozen constants θ_PCE (Z_80 = 2.4865) and SE_KAPPA_CEILING (0.020) are kept with a §10.3 rationale that the calibrated tests of 8.1c contradict. The spec discloses that GO "no longer implies" power but does not define what GO now certifies.
- **What GO would start, on the spec's own criterion:**
  - mid-price designs whose 80%-power effect is ≈ 0.18 (> PCE_CEILING 0.10), the case the PCE_CEILING rationale says must not be started;
  - designs whose "only real negative-result instrument" (NEG) has power 0.12–0.13 at −0.07 per share in every law measured, against the ≈ 0.9 that SE_KAPPA_CEILING is frozen to guarantee.
- **Stale marketing (m12).** §1 still advertises a "well-powered" information axis, and §21 item 1 still marks "V2 still claims power it does not have" as Refuted.
- **SEVERITY: MAJOR.** The contract markets a start decision and a negative-result capability it cannot make. No capital or prospective path is involved.
- **ROOT_CAUSE.** The D4-C3-M2 calibration was correctly applied to the tests but not to the design gate that is supposed to certify their power. Validity was repaired while the frozen feasibility gate kept its nominal 5-date-block meaning.
- **COUNTEREXAMPLE** (synthetic, `out_power*_20000.jsonl`, seeds [77200201, 7 / 11, cell, chunk]):
  - mid c ~ U(0.35, 0.80), m 17 thin, no persistence: θ_PCE = 0.09 → GO (reach 0.99), P(T2) at θ_PCE 0.111; 80%-power effect ≈ 0.18; NEG power at θ = −0.12 (κ ≈ −0.069) 0.116;
  - favourite law: GO, NEG at κ ≈ −0.064 0.13;
  - pre-repair 5-date NEG: 0.89 / 0.95.
- **MINIMAL_REPAIR_SURFACE:**
  - Either (a) outcome-free, stricter-only recalibration of the design gate to the tests actually run: θ_PCE with the synthetic effective multiplier (≈ 5.0 × SE0_θ measured over the GO-feasible laws), and the κ ceiling re-derived from NEG's calibrated power. Disclose that most mid-price designs and probably all designs then become NO_GO (KAPPA_UNDERPOWERED).
  - Or (b) a governance redefinition of GO's meaning, rewriting §10.3's rationale, §1, §21 item 1 and §24 to match.
  - Plus m12.
  - No level may be lowered and no owner-frozen surface touched.

**SECOND BLOCKER: M3 (MAJOR, statement-level).**
- **Defect.** The printed level text (17.3) and the 8.5c error statement claim the L_W / T1a levels over "CORE prices to 0.90". The calibration covers only U(0.35, 0.80), U(0.70, 0.90) and their mix.
- **COUNTEREXAMPLE** (`out_probe100_100000.jsonl`, seeds [77200201, 8, cell, 0..19]): c ~ U(0.85, 0.90) (R*'s high-confidence NO legs), 30-date trailing-mean persistence at rv 0.10 (the §9 mechanism, a declared shape and variance), m 17, 120 counted dates:
  - L_W miss 0.0587 [0.0573, 0.0602] with 30 contiguous paused dates;
  - 0.0523 [0.0509, 0.0537] without pauses;
  - T1a 0.0262 [0.0253, 0.0273].
- **MINIMAL_REPAIR_SURFACE.** Either (b) restrict every printed class description (17.3 level texts, 8.5c, §21 item 43, §27, delta, power table) to the enumerated price laws, and disclose the measured exceedance for favourite concentration (≥ 0.80) together with the price-mix dependence of the level. Or (a) recalibrate over near-cap favourite laws, at further power cost. Or a design-conditional, outcome-free calibration on the realised trade design (prices, fills, stations, calendar are known at T_entry).
- **Plus m13:** disclose the conditional-on-reach maximum as a grid figure.

**AFFECTED_FILES:**
- spec §1, §6.2, §7, §8.1c, §8.5c, §10.1–§10.3, §17.3, §17.8, §21, §24, §27;
- manifest GO / NO_GO, THETA_PCE / Z_80, SE_KAPPA_CEILING, PERSISTENCE_CLASS_DP_STAR, section G;
- delta (new entry);
- power table §4.9;
- architect state;
- a synthetic gate-calibration run if (a).

**UNCHANGED_SURFACES:**
- owner-frozen R*, h, W, signal, cohort, entry, T_entry, S_ref, execution, 0.04 split;
- estimands; accounting;
- the 8.1c construction and λ constants (unless M3 option (a));
- R1 / R2 / R3 algebra; label vocabulary; 11-state machine; SHADOW_CONTINUATION_SIGNAL; IF1–IF5.

**REQUIRED_REAUDIT_SURFACE:** GO / θ_PCE / κ-ceiling meaning against simulated power of the calibrated tests over the GO-feasible price laws; M3 statement or level (favourite concentration ≥ 0.80 at trailing-mean 30 rv 0.10, ≥ 20,000 per cell, worst ≥ 100,000); m12, m13; regression of R1 / R2 / R3 and D1–D12.

**CLASSIFICATION: REPAIRABLE_BOUNDED.**
- **Contract.** Both items are gate / statement repairs or calibrations of existing objects. They are outcome-free, stricter-only, and touch no owner-frozen surface.
- **Feasibility.** Whether to run a V2 whose honest gate likely says NO_GO (or which has no usable negative-result instrument) is a governance / resource decision. At 120 counted dates over 𝒟_P* the lack of a negative-result instrument is FUNDAMENTAL (oracle benchmark §7): it cannot be repaired by recalibration inside V2.

```text
BUILDER_AUTHORIZED = FALSE; REAL_CAPITAL_AUTHORIZED = FALSE; LIVE_TRADING_AUTHORIZED = FALSE; t0 = NOT_DECLARED
```
