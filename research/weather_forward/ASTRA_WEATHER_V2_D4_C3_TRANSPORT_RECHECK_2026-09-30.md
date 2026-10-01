# ASTRA — WEATHER FORWARD V2 — BOUNDED D4-C3 + TRANSPORTABILITY RECHECK — 2026-09-30 (run 2026-10-01)

```text
ASTRA_ROLE              = independent adversarial scientific reviewer (bounded D4-C3 + transportability recheck only)
AUDIT_BRANCH            = astra/weather-forward-v2-independent-reaudit-2026-09-29
ASTRA_START_SHA         = 92c2f706d2ac75af9ae9710061c60df520234410
PREVIOUS_ASTRA_SHA      = 92c2f706d2ac75af9ae9710061c60df520234410
AUDITED_BRANCH          = claude/charming-allen-948kd8
AUDITED_SHA             = 341e0b7aede716fdb68e2c9806cc1a09fdd50b82
AUDITED_TREE            = 37412bdc3e0307ec3073f091552d6ab2d5332783
R3_CONTENT_COMMIT       = 3086efb (341e0b7a = resume-checkpoint commit on top)
ASTRA_WEATHER_V2_D4_C3_TRANSPORT_RECHECK = BLOCKED_D4_R3_SOURCE_BOUND_UNDERCOVERAGE_CROSS_BLOCK_PERSISTENCE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
t0                      = NOT_DECLARED
BUILDER_AUTHORIZED      = FALSE
```

## 0. Independence disclosure

This recheck, the R3 repair it audits, and all earlier repairs and rechecks in this chain were produced in one agent session under different role instructions. The architect state discloses the same.

To limit self-confirmation, this audit:
- uses a separate engine and fresh seeds (1 001 000 – 1 120 300; fuzz seed 2026100101);
- spends most of its compute on the surface R3 declared safe and did not attack hardest: the sampling coverage of L_W under dependence the 5-date block model does not capture.

Governance may still prefer a separate reviewer session.

## 1. Executive verdict

R3 is mathematically and semantically sound on everything it adds:
- C3 reproduces, and R3 removes every unconditional prospective label in both directions.
- The cost-mass transport bound is exact for θ_F = E_Q[N]/E_Q[C], and the worst case of −1 per dollar of C is exact for the frozen exchange-level N.
- The frontier ε* is correct and monotone in its domain.
- No ε, δ, H or τ threshold was selected.
- Observable flags can only revoke the transport premise, and hidden regimes are handled honestly by the ε premise.
- SHADOW_CONTINUATION_SIGNAL means shadow-only.
- R1 and R2 are intact, and the state machine is total.

R3 fails on the one stochastic quantity it rests on. After R3, `P(θ_W ≥ L_W) ≥ 0.95` is the *only* probability behind every positive economic label (REALIZED_WINDOW_VALUE_SUPPORTED / NOT_ROBUST: "size ≤ 0.05") and behind every conditional prospective statement (spec §8.5c: "the only probability in any prospective statement").

Spec §9 itself names a cross-block persistence mechanism: "the lag of the 30-date trailing bias through a seasonal transition", plus hemisphere/season common modes. With that mechanism at the same latent size as V2's own declared date component (latent variance 0.05, daily AR φ = 0.8), and in 17-trades/date geometries that pass the information floor 72–82% of the time:

| Fresh Astra Monte Carlo (20,000 replications each) | Result (95% MC) | Declared |
|---|---|---|
| False REALIZED_WINDOW positive claim at θ_W = 0, thin fills | **0.0805** [0.0767, 0.0843] | ≤ 0.05 |
| L_W misses θ_W, full fills, θ_W = 0.10 | **0.0902** [0.0863, 0.0942] | ≤ 0.05 |
| L_W misses θ_W, thin fills, θ_W = 0.05 | **0.0828** [0.0790, 0.0867] | ≤ 0.05 |
| Stronger regime (latent 0.10, φ = 0.9), thin, θ_W = 0 | 0.0761 [0.0724, 0.0797] | ≤ 0.05 |

The same geometries *without* cross-block persistence sit at 0.0524–0.0534 (the 0.5 pp that R3 disclosed). R3's disclosure states only that 0.5 pp. The spec still asserts nominal 95% / size ≤ 0.05 for the claims that rest on L_W.

By mission §41 and §44 ("source bound materially undercovers while still marketed as exact nominal control") this is **MAJOR and blocking**. It is not a regression of a closed item (T2 is unchanged since V2). R3 made L_W the sole probability of the whole economic and prospective layer, and this audit is the first to measure it under the spec-named cross-block mechanism in geometries that pass the information floor. The previous O2 observation found such regimes screened by IF5 only in thick designs.

The minimal repair is bounded: calibrate L_W, or state its true guarantee (§12).

## 2. Authority verification

| Check | Result |
|---|---|
| `origin/claude/charming-allen-948kd8` | `341e0b7aede716fdb68e2c9806cc1a09fdd50b82`: MATCH (start and pre-write) |
| Audited tree | `37412bdc3e0307ec3073f091552d6ab2d5332783` |
| Astra start | `92c2f706d2ac75af9ae9710061c60df520234410`: MATCH |
| Ancestry | 94b59348, 7d95c00, 24d2342 and e45d2ce7 are all ancestors; R3 = 3086efb → 341e0b7a (fast-forward) |
| `QUANT_NORTH_STAR.md`, Astra artifacts in candidate | unchanged vs e45d2ce7 (`git diff --quiet`) |
| Prior simulation files (run D / run E scripts and output) | unchanged vs e45d2ce7 |
| Spec sections §3, §5.2, §8.1, §8.5 (R1), §8.6, §9, §10.2, §10.3, §14, §15, §17.1, §17.4 | byte-identical to e45d2ce7 |

## 3. Objects reconstructed independently

| Object | Population / denominator | Horizon | Conditioning | Status |
|---|---|---|---|---|
| N_j, C_j | executed R* trades, REALISTIC, S_ref; `N_j = n_j y_j − C_j` (exchange-level; V1 §4.3), `C_j = V_j + F_j` | per trade | — | observed |
| θ_W | `Σ_W n_j(p_j − c_j)/Σ_W C_j`, window trades | window (≤ 120 counted dates) | realised trade set; p_j given T_entry information | estimand, not observed (p_j unknown) |
| L_W | `θ̂ − t_{df,0.95} SE_CR(θ̂)` | window | sampling | **estimated**; claimed 95% coverage of θ_W |
| P (source law) | law generating the window's trades and outcomes | — | — | not identified beyond the window |
| Q_H | law of executed trades over the next H counted dates | H ∈ {14, 30, 60, 120}, each separately | — | unknown |
| θ_F | `E_Q[N]/E_Q[C]` over the epoch | horizon-specific | Q_H | unknown; bounded only conditionally |
| ε | `E_Q[C_B]/E_Q[C]`, cost-mass share of the adverse part of the epoch | per epoch | partition (A, B) arbitrary, outcome-dependent allowed | **assumed (declared), adversarial, never estimated** |
| δ | additive degradation in θ units of the represented part: `θ_A ≥ θ_W − δ` (cost-weighted through θ_A) | per epoch | — | **assumed** |
| τ | target level of the robust bound | — | — | reporting grid {0, θ_ERT} |
| ε*(δ, τ) | largest ε with `L_T(ε, δ) ≥ τ` | H-invariant as a number; premise per H | the realised L_W | derived (a robustness capacity, not a forecast) |

The spec matches this reconstruction. It states that ε and δ are declared and unverified, that ε* is a capacity, and that θ_F is horizon-specific with H-invariant algebra.

The scan for semantic drift (forecast, probability of regime, validated / confirmed / estimated transport) found none in authoritative text; see §8.

## 4. C3 reproduction and R3 structural kill (`run_c3_r3.py`, 20,000 replications each, seeds 1 100 000+)

| Attack (θ_P = −0.005 exactly) | Retired R2 `PROSPECTIVE_VALUE_CONFIRMED` (95% MC) | R3 window-positive (true statement about θ_W) | R3 false window claim (θ_W ≤ 0) | Conditional transport claim false at true ε (premise holds) | Shadow signal |
|---|---|---|---|---|---|
| Thin fills, 96-event loss dates, m = 17, ε_true 0.0955 | **0.4324** [0.4255, 0.4393] | 0.4324 | 0.0000 | 0.0258 [0.0237, 0.0280] (= L_W miss) | 0.4324 |
| Full fills, same, ε_true 0.0524 | **0.1193** [0.1148, 0.1238] | 0.1193 | 0.0000 | 0.0161 [0.0144, 0.0178] | 0.1193 |
| Hidden loss dates, identical counts and fills, ε_true 0.0433 | 0.0417 | 0.0417 | 0.0069 | 0.0036 | 0.0417 |
| Single-cap-date scale (E = 0.5 loss dates / 120), m = 35 thin, ε_true 0.0368 | 0.1210 | 0.1210 | 0.0000 | 0.0269 | 0.1210 |

The mechanism reproduces against Astra @92c2f706 (0.4266 / 0.1245) and Architect run F (0.4334 / 0.1175).

Under R3 the same runs emit only REALIZED_WINDOW_VALUE_SUPPORTED. That is a true statement about θ_W: the loss dates were not in the window. The run also carries the transport report and the constants `PROSPECTIVE_CONFIRMATION = NOT_ESTABLISHED_UNCONDITIONALLY` and `PROSPECTIVE_EXCLUSION = NOT_USEFULLY_TESTABLE_IN_V2_HORIZON`. The vocabulary contains:
- 0 unconditional prospective labels;
- 0 prospective exclusions;
- 0 R* rejections.

Shadow continuation fires in these runs. That is semantically correct: it only proposes more shadow evidence, which is how the regime eventually gets sampled.

The conditional claim is false only through the L_W sampling miss, as Theorem 2 predicts.

**D4_C3_UNCONDITIONAL_CONFIRMATION_REMOVAL = PASS. C3_REPRODUCED = TRUE.**

## 5. Cost-mass transport bound (P0; `astra_transport_fuzz.py`)

**Derivation.** For an epoch law Q and any partition (A, B) of its trades:
- `E_Q[N] = E[N_A] + E[N_B] = E[C_A] θ_A + E[C_B] θ_B`.
- Dividing by `E[C] = E[C_A] + E[C_B]` gives `θ_F = (1 − ε_Q) θ_A + ε_Q θ_B` with `ε_Q = E[C_B]/E[C]`.

This is exact for the ratio of expectations precisely because ε is the share of the denominator's expectation. A share of trades or dates would leave a remainder term `(E[C_B]/E[C] − ε_count)(θ_B − θ_A)`.

**Worst case.** `N_j = n_j y_j − C_j ≥ −C_j` for y_j ∈ [0, 1] (including voids and 50-50). C_j includes the entry fee and walked levels; partial fills scale both sides. V1 §11 charges no settlement or redemption cost inside exchange-level N: rebates, infrastructure and ramps sit only in the separate `N^full`. So `θ_B ≥ −1` exactly. The transport statement is about exchange-level θ only, which the spec makes explicit.

**Theorem 2.** Under `θ_A ≥ θ_W − δ` and `ε_Q ≤ ε`:
1. `θ_F ≥ (1 − ε_Q)(θ_W − δ) − ε_Q`.
2. That is decreasing in ε_Q when `θ_W − δ > −1`, so it is ≥ `(1 − ε)(θ_W − δ) − ε`.
3. With `θ_W ≥ L_W`, it is ≥ `L_T(ε, δ)`.

ε and δ are premises (membership is assumed, not estimated), so they carry no α. The only probability is `P(θ_W ≥ L_W)`. **The proof is correct.**

Fuzz results (deterministic):
- 99,239 random epoch laws: mixtures of 1–5 worlds, 1–120 trades each, asks 0.001–0.90, partial / thin / full fills, real fee formula, arbitrary p. Partitions were random, worst-return-first, or the single highest-cost item.
- Identity violations 0 (max relative error 9e-15); bound violations 0; min θ_B = −1.000.
- Worst N/C over 200,000 fee-inclusive trades with y ∈ {0, 0.5, 1}: exactly −1.

Counterexample ("trade-count mixing passes, cost-weighted fails"): one 96-event cap date (5,040 USD) among 119 ordinary 17 × 15 USD dates earning +0.10 gives true θ_F = −0.0567.

| ε definition | ε | Bound with L_W = 0.10 | Valid? |
|---|---|---|---|
| dates | 0.0083 | +0.0908 | false |
| trades | 0.0453 | +0.0502 | false |
| **cost mass (frozen)** | 0.1424 | **−0.0567** | exact |

The frozen protocol uses cost mass everywhere it binds. Date counts appear only in the explicitly derived, labelled k*(H) translation.

**D4_R3_COST_MASS_TRANSPORT_BOUND = PASS.**

## 6. Frontier, k*(H), H and thresholds (P4)

- `ε*(δ, τ) = (L_W − δ − τ)/(1 + L_W − δ)` if `L_W − δ > τ`, else 0 (spec §8.5c). Over 3,000 random cases with a 200,001-point brute force: 0 mismatches.
- Monotonicity within the domain `L_W − δ > −1`: 0 violations. L_T decreases in ε; ε* decreases in δ and τ. Endpoints: `L_T(0) = L_W − δ`, `L_T(1) = −1`.
- **MINOR m8 (Builder-visible formula inconsistency).** Spec §17.3 (ROBUSTNESS_FRONTIER) and manifest row ROBUST_BOUND / FRONTIER write `max(0, (L_W − δ − τ)/(1 + L_W − δ))` without the domain guard.
  - For `L_W − δ < −1` this prints a positive ε* (for example 3 at L_W − δ = −1.5, τ = 0); at `−1` it divides by zero.
  - L_W < −1 + δ is reachable only in near-total-loss windows: θ̂ ≥ −1 always, and SE > 0.
  - No label consumes ε*, but the Builder-facing rows must carry §8.5c's guard. The Architect's `frontier()` code does guard.
- k*(H) solves `ε(k) = kC_cap/(kC_cap + (H − k)C̄_d) = ε*` exactly (3,000 cases, 0 mismatches). It is real-valued and unrounded, explicitly derived and labelled as a volume-translation assumption, and does not replace the cost-mass proof.
- H ∈ {14, 30, 60, 120} are pre-existing V2 constants, reporting only. θ_F is per-H, and the premise `Q_H ∈ 𝒯_H` is separate for each H, so a statement for H = 14 does not cover H = 120.
- No ε, δ, H or τ requirement exists anywhere. The scan for "sufficiently / acceptable / deployment-ready robust", READY_FOR_CAPITAL, DEPLOYABLE and similar found nothing in authoritative text. Required values are assigned to capital governance outside V2.

**D4_R3_ROBUSTNESS_FRONTIER = PASS** (authoritative definition and code correct; m8 must be fixed in the Builder-facing rows).

## 7. Hidden-regime and one-date attacks (P3)

- **Hidden regime** (identical counts and fills until the loss): the observable flags never fire (run F 0%), and the spec says so. The conditional claim stays valid because the regime's cost mass enters ε (false-claim rate 0.0036, below the L_W miss). The spec never presents flags as certification. `TRANSPORT_ASSUMPTION_STATUS = DECLARED_UNVERIFIED`.
- **One high-cost date**: §5 counterexample. The cost-mass ε is 17× the date share; ε_1(H) is printed (0.142 at H = 120 with thin dates; 0.60 at H = 14).

## 8. Claim semantics (P2)

- **No unconditional future economic verdict exists.** The authoritative economic labels are REALIZED_WINDOW_VALUE_* (θ_W). The constants deny unconditional confirmation and exclusion. The conditional label CONDITIONAL_PROSPECTIVE_SUPPORT is prefixed and carries sentence (c) with the unverified premise. The claim matrix shows "Builder? no / Capital? no / Rejects R*? no" for every label.
- **SHADOW_CONTINUATION_SIGNAL** is reachable only from `{INFORMATION_DETECTED, NO_INFORMATION_DETECTED}__REALIZED_WINDOW_VALUE_SUPPORTED` with VALID_COMPLETE, CORE_ADVERSE = FALSE and ACCESSIBLE (exhaustive enumeration, §9). Its meaning is "propose a further paper / shadow epoch"; it does not authorise Builder, t0, live trading or capital.
- **"SUPPORTED"** is scoped by the mandatory REALIZED_WINDOW_ prefix, the m5 naming note, sentence (c) and claim matrix 17.8. It is acceptable.
- **MINOR m9 (stale, non-authoritative).** Two R2-era statements still assert the refuted claim without a SUPERSEDED marker. A reader could cite them:
  - power table §4.6 reading 5: "Prospective confirmation remains valid … ≤ 0.0378";
  - delta D4-C2 "CLAIM STRENGTH AFTER REPAIR: PROSPECTIVE_VALUE_CONFIRMED = T2 at 0.05 … no structural non-identification".

  Both are corrected later in the same files (D4-C3, §4.7), but they should be marked.
- The claim matrix's "size ≤ 0.05" for REALIZED_WINDOW_VALUE_* is false under cross-block persistence. That is part of the primary finding (§10).

**D4_R3_CLAIM_SEMANTICS = PASS** (m9 minor; the size statement is carried by the primary finding).

## 9. State machine (`enumerate_states_r3.py`)

- 3,072 combinations of VALIDITY (8) × INFO × T1 × NEG × T2 × θ̂ ≥ θ_ERT × GATES × OPERABILITY (6) map to exactly **11** SCIENTIFIC_STATE values.
- The partition is total and deterministic. No state name contains PROSPECTIVE, EXCLUDED, DEPLOY or CAPITAL, and the shadow signal comes only from SUPPORTED with CORE_ADVERSE = FALSE.

**D4_R3_STATE_MACHINE = PASS.**

## 10. PRIMARY FINDING M1 (MAJOR, blocking): L_W undercoverage under spec-named cross-block persistence (P1)

**Engine.** `astra_lw.py` / `run_lw.py`:
- Window: 14 OP + 60 / 120 window dates; GO and INFO (IF2–IF5) as frozen.
- L_W exactly T2's bound: two-way CR max-of-three, 5-date blocks, t_{df,0.95}.
- θ_W exact from p.
- Optional daily AR(1) date regime `e_t = φ e_{t−1} + √(1 − φ²) z_t`, added to the latent copula with variance `rv`.

Without cross-block persistence (the declared block model), coverage is near nominal:

| Geometry | N | Joint miss P(reach ∧ L_W > θ_W) | 95% MC |
|---|---|---|---|
| 120/48, m = 17, thin (Architect scenario 13) | 50,000 | 0.0534 | [0.0515, 0.0554] |
| 120/48, m = 17, thin, one dominant 96-trade date | 20,000 | 0.0556 | [0.0524, 0.0588] |
| 120/48, m = 17, thin, θ = 0 (size) | 20,000 | 0.0524 | [0.0494, 0.0555] |
| 120/48, m = 35, full (thick) | 20,000 | 0.0460 | [0.0431, 0.0489] |
| 120/48, m = 35, full, θ = 0 (size) | 20,000 | 0.0447 | [0.0418, 0.0476] |
| 120/48, m = 17, thin, dominant station 20% | 20,000 | 0.0382 | [0.0355, 0.0409] |
| 60/25, m = 35, full | 20,000 | 0.0310 | — |
| 60/25, m = 17, thin | 20,000 | 0.0139 | (reach 0.18) |

With cross-block date persistence (the spec's own named mechanism), coverage fails:

| Geometry (120/48) | Regime (φ, latent var) | N | Reach | Joint miss / false window claim | 95% MC |
|---|---|---|---|---|---|
| m = 17, thin, θ = 0.05 | 0.8, 0.05 | 20,000 | 0.77 | miss **0.0828** | [0.0790, 0.0867] |
| m = 17, full, θ = 0.10 | 0.8, 0.05 | 20,000 | 0.82 | miss **0.0902** | [0.0863, 0.0942] |
| m = 17, thin, **θ = 0 (false REALIZED_WINDOW positive)** | 0.8, 0.05 | 20,000 | 0.72 | **0.0805** | [0.0767, 0.0843] |
| m = 17, thin, θ = 0.05 | 0.9, 0.10 | 20,000 | 0.32 | miss 0.0866 | [0.0827, 0.0905] |
| m = 17, thin, θ = 0 (false positive) | 0.9, 0.10 | 20,000 | 0.27 | 0.0761 | [0.0724, 0.0797] |
| m = 35, full, θ = 0 (false positive) | 0.8, 0.05 | 20,000 | 0.06 | 0.0096 | (IF5 screens) |
| m = 35, full, θ = 0.10 | 0.9, 0.10 | 20,000 | 0.008 | 0.0035 | (IF5 screens) |

**Diagnosis** (mission §22: A, B, C or D):
- Not Monte Carlo noise: intervals exclude 0.05 by 2.6–4 pp.
- Not a simulation mismatch: the same engine reproduces nominal behaviour without persistence and the Architect's 0.055.
- It is a genuine undercoverage of the frozen engine when dependence persists beyond its 5-date blocks.

That dependence is not exotic. Spec §9 names it (the 30-date trailing-bias lag through seasonal transitions; hemisphere/season common modes) and lists block lengths {3, 7, 10} only as non-gating sensitivity. In thick designs IF5 (DEFF ≤ 6) screens it, which was the earlier O2 observation. In sparse 17-trades/date designs that pass the information floor 72–82% of the time, it does not.

**Consequence under R3:**
- The positive economic label's size is ≈ 0.08, not ≤ 0.05.
- Every conditional prospective statement rests on a 95% that is ≈ 0.91.
- The spec markets both as nominal (error statement §8.5c, claim matrix 17.8 "size ≤ 0.05", report field "one-sided 95% sampling coverage of θ_W"). Its only disclosure is the 0.5 pp shortfall without persistence.

No capital or unconditional claim follows, which is why this is MAJOR rather than CRITICAL. But it is a materially false probability statement on the layer R3 made load-bearing.

**D4_R3_LW_CALIBRATION = BLOCKED.**

## 11. Other checks

- **R1:** spec §8.5 is byte-identical to e45d2ce7; U_W is unchanged. **D4_R1_REALIZED_WINDOW_BOUND = PASS.**
- **R2 / C2:** no prospective exclusion and no R* rejection exist (§4, §9). Run F scenario 01 (rare 0.001 tail, θ_P = 0.025): 0 prospective labels. In @92c2f706, zero-count windows gave 0 R2 exclusions. **D4_R2_PROSPECTIVE_EXCLUSION_REMOVAL = PASS.**
- **Power-ceiling theorems (§8.5b / §8.5c):**
  - Wording is now "finite-horizon power ceiling" / "not usefully testable".
  - D_obs ≈ 174 counts window + OP + pre-t0 resolved history in both the exclusion and the mirror theorem, consistently.
  - Ceilings reproduce: 0.0602 / 0.0611 for exclusion; mirror table 0.060–0.120 (thin) up to 1 (thick).
  - The mirror construction (independent loss dates at the 2·|STATION_TABLE| × C_TRADE_MAX cap, coupling on "no loss date") is valid.

  **D4_R3_POWER_CEILING_THEOREM = SUPPORTED.**
- **Architect run F reproducibility:** modes `frontier` and `c3 20000` re-run at 341e0b7a are byte-identical to the committed raw output. The script is synthetic only.
- **Outcome leakage:** none. R3 used synthetic run F, algebra and Astra artifacts.
- **Trading rule:** unchanged (§2 sections byte-identical). TRADING_RULE_CHANGED = FALSE.
- **Builder / capital:** BUILDER_AUTHORIZED = FALSE everywhere; no capital path.
- **Minors:**

| Minor | Status | Evidence |
|---|---|---|
| m3 | CLOSED | manifest §C header "HISTORICAL; rows marked SUPERSEDED", §D markers |
| m4 | CLOSED | checkpoint §4 items 1, 3 and 5 marked |
| m5 | CLOSED | 17.3 naming note |
| m6 | CLOSED | D_obs ≈ 174 |
| m7 | CLOSED | "finite-horizon power ceiling", constant renamed |

- **New minors:** m8 (frontier domain guard in Builder-facing rows), m9 (two stale R2 confirmation-validity statements unmarked).
- **Quant-wide TRANSPORT_CERTIFICATE interface:** conceptually coherent; design-only; not implemented.
- **North Star:** evidence, future truth and capital authorisation stay separate. INDETERMINATE and conditional evidence are never approval, and ε* is a capacity, not a forecast.
- **Regressions (D1–D3, D5–D12): NONE.** D8's finite-cluster limitation is quantified more sharply by M1, but R3 did not change D8.

## 12. Minimal repair surface (bounded Architect repair only)

PRIMARY_BLOCKER: `D4_R3_SOURCE_BOUND_UNDERCOVERAGE_CROSS_BLOCK_PERSISTENCE` (M1).

EXACT_INVARIANT: the probability attached to L_W, and hence to REALIZED_WINDOW_VALUE_* and every conditional prospective statement, must hold over the dependence class the spec itself names (§9), or the stated level must be weakened to what actually holds there.

Options (Architect's choice):
- **(a) Calibrate.** Make L_W robust to cross-block persistence with a frozen, outcome-blind rule. Examples: the max of two-way CR variances over block lengths {5, 10, 20} dates with matching df, or a date-level HAC with frozen bandwidth. Re-show coverage ≥ 0.95 over a declared persistence class (at least φ ≤ 0.9, latent variance ≤ 0.10, m ∈ {17, 35}, thin and full fills). This changes the T2 statistic, so the D1 / PCE power statements need re-derivation, disclosed.
- **(b) Weaken honestly.** Keep the engine, but state L_W's guarantee as "nominal 95% under the declared 5-date-block model; ≥ 0.90 under tested cross-block persistence (φ ≤ 0.9, latent variance ≤ 0.10)". Propagate the actual level to the error statement in §8.5c, the 17.3 field, the 17.8 claim matrix sizes, sentence (c) and manifest ROBUST_BOUND / FRONTIER, and add the persistence class to the run-F evidence.

Either way, fix m8 and m9.

DO NOT CHANGE: R*, h, W, cohort, strata, S_ref, execution, the R3 transport algebra, the cost-mass ε, the frontier definition, the constants, the label vocabulary, the shadow signal, R1, R2, PCE / GO (except power statements under option a).

AFFECTED_FILES: spec §8.5c error statement (and §6.1 / §8.1 under option a), §17.3, §17.8, §21; manifest ROBUST_BOUND / FRONTIER (+ ALPHA / NULLS under option a); delta (new entry); power table §4.7 (persistence rows); C3 simulation (persistence mode); m9 in the power table §4.6 / delta D4-C2.

REQUIRED_REAUDIT_SURFACE: L_W coverage over the declared persistence class at ≥ 20,000 replications per cell; the stated level everywhere it appears; m8 and m9.

## 13. Verdict

```text
ASTRA_WEATHER_V2_D4_C3_TRANSPORT_RECHECK   = BLOCKED_D4_R3_SOURCE_BOUND_UNDERCOVERAGE_CROSS_BLOCK_PERSISTENCE
C3_REPRODUCED                              = TRUE (0.4324 thin / 0.1193 full; fresh seeds)
D4_R1_REALIZED_WINDOW_BOUND                = PASS
D4_R2_PROSPECTIVE_EXCLUSION_REMOVAL        = PASS
D4_C3_UNCONDITIONAL_CONFIRMATION_REMOVAL   = PASS
D4_R3_COST_MASS_TRANSPORT_BOUND            = PASS (exact for E[N]/E[C]; 99,239 fuzz cases, 0 violations; worst N/C = −1 exactly)
D4_R3_ROBUSTNESS_FRONTIER                  = PASS (m8: domain guard missing in 17.3 / manifest rows)
D4_R3_LW_CALIBRATION                       = BLOCKED (M1: false window claim 0.0805 [0.0767, 0.0843]; L_W miss up to 0.0902
                                                      [0.0863, 0.0942] under spec-named cross-block persistence; disclosed 0.5 pp only)
D4_R3_CLAIM_SEMANTICS                      = PASS (no unconditional future verdict; shadow-only signal; m9 stale history)
D4_R3_STATE_MACHINE                        = PASS (11 values, total; shadow only from SUPPORTED ∧ ¬CORE_ADVERSE)
D4_R3_POWER_CEILING_THEOREM                = SUPPORTED
m3 m4 m5 m6 m7                             = CLOSED
REGRESSIONS                                = NONE (D1–D3, D5–D12)
CRITICAL_FINDINGS                          = NONE
MAJOR_FINDINGS                             = M1
MINOR_FINDINGS                             = m8, m9
MISSING_PROOF                              = NONE beyond M1
EXPERIMENT_FEASIBILITY_V2                  = BLOCKED_D4_R3_SOURCE_BOUND_UNDERCOVERAGE_CROSS_BLOCK_PERSISTENCE
NEXT_AUTHORIZED_ACTION                     = BOUNDED ARCHITECT REPAIR ONLY (section 12)
BUILDER_AUTHORIZED                         = FALSE
REAL_CAPITAL_AUTHORIZED                    = FALSE
LIVE_TRADING_AUTHORIZED                    = FALSE
t0                                         = NOT_DECLARED
```
