# ASTRA — WEATHER FORWARD V2 — BOUNDED D4 RECHECK — 2026-09-30

```text
ASTRA_ROLE              = independent adversarial scientific reviewer (bounded D4 recheck only)
AUDIT_BRANCH            = astra/weather-forward-v2-independent-reaudit-2026-09-29
AUDITED_BRANCH          = claude/charming-allen-948kd8
AUDITED_SHA             = 24d2342fcff8fd78a769a9ecaf7551ab2578e2ef
AUDITED_TREE            = 5ebe96e59b104318fbcc3b837583a43c20976171
D4_REPAIR_COMMIT        = 05836143a249f5571a29403727c6d90df2c8b7c8 (scientific content; later commits = resume checkpoint only)
PREVIOUS_AUDITED_V2     = 94b59348d5b79cd3c53dcba0b791ce1daeb75d60
PREVIOUS_ASTRA_SHA      = 7d95c00abccfbc805c0d8abca65a6b93268741a2
ASTRA_WEATHER_V2_D4_RECHECK = BLOCKED_D4_PROSPECTIVE_ESTIMAND_UNSAMPLED_TAIL_FALSE_EXCLUSION
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
t0                      = NOT_DECLARED
BUILDER_AUTHORIZED      = FALSE
```

## 1. Executive verdict

Repair R1 fixes exactly the mechanism Astra reported in C1. Conditional on the trades R* actually made in the window, the new tail term `M_tail` deterministically dominates every admissible tail outcome, and the exclusion bound inherits core-bound coverage. I reproduced the old defect independently, proved the conditional domination, confirmed it numerically (≈ 99,000 deterministic cases, 240,000 adversarial Monte Carlo replications, zero violations), and found the core bound defensible at the minimum geometry.

R1 does **not** close D4 for the estimand the protocol actually freezes. Spec §5.1 defines the economic estimand prospectively: `θ = E[N_j] / E[C_j]` over trades of R* on the prospective eligible cohort (§1: "can R* generate positive net cashable value … prospectively"). The §8.5 coverage proof begins "Conditional on the realised trade set…" and silently replaces that θ with the realised-window quantity `θ_W = Σ_window n_j (p_j − c_j) / Σ_window C_j`. `M_tail` bounds only the tail legs that happened to be sampled. R* can buy a 0.001 leg whenever `q − a − f ≥ 0.10`. When such legs arrive rarely, a GO-compatible window often contains none. `M_tail` is then 0, and a negative core produces `U(θ) < θ_ERT` while the prospective θ exceeds θ_ERT.

Fresh Monte Carlo evidence (§6): at the plausibility level Astra previously accepted for sub-cent legs (p = 0.17 at c = 0.001), with prospective θ = 0.025 > θ_ERT, the rate of false `NET_VALUE_EXCLUDED` plus `R*_REJECTED_AS_NET_STRATEGY` is **0.0592** (95% MC interval [0.0519, 0.0666]; 4,000 replications). That exceeds the declared 0.05. The frozen admissible class allows every p ∈ [0, 1]. Within it the false-exclusion rate reaches **0.19–0.35** (p = 0.5–1.0), and false `LARGE_VALUE_EXCLUDED` at prospective θ = 0.10 reaches **0.153**. The 14-date GO screen passes in 82–94% of these designs.

The failure class is the same as C1: a materially false terminal economic exclusion and a false economic rejection of R*. R1 made the exclusion valid for the *sampled* tail and moved the failure to the *arrival process* of tail legs. By the mission's severity rule this is **CRITICAL**, so D4 stays open.

## 2. Authority verification

| Check | Result |
|---|---|
| `origin/claude/charming-allen-948kd8` | `24d2342fcff8fd78a769a9ecaf7551ab2578e2ef`, checked at start and again immediately before writing: MATCH |
| Ancestry | 94b59348 < 594a3b7 < 7d95c00 < 0583614 < 020ec60 < 24d2342: TRUE (`git merge-base --is-ancestor`) |
| 0583614..24d2342 | touches only `WEATHER_FORWARD_V2_RESUME_CHECKPOINT_2026-09-29.md` (84 lines added) |
| Previous Astra files at 24d2342 vs 7d95c00 | `ASTRA_WEATHER_V2_INDEPENDENT_REAUDIT_2026-09-29.md` 957d28e7… = 957d28e7…; `ASTRA_WEATHER_V2_REAUDIT_STATE_2026-09-29.md` 7e6dec3e… = 7e6dec3e…: BYTE-IDENTICAL |
| `QUANT_NORTH_STAR.md` | blob 8295041a… at 94b59348, 7d95c00 and 24d2342: UNCHANGED |
| Files changed 7d95c00 → 24d2342 | spec, manifest, architect state, delta, power table, synthetic sim, resume checkpoint; nothing outside `research/weather_forward/` |

Audited blobs at 24d2342: spec 316e1c44…, manifest 9acf9e67…, architect state 0e14d5a3…, delta bb140d46…, power table 4e3f58c5…, sim e2ffa4ea…, resume checkpoint cd4982ff….

## 3. Outcome-blindness of this recheck

Astra used no Weather outcome, settlement, winner, hit rate, P&L, wallet or leaderboard information. Every number below comes from synthetic designs with declared prices, capital, dependence and hypothetical win probabilities. The code and raw outputs are committed in `research/weather_forward/astra_d4_recheck_2026-09-30/`. It is independent of the Architect script: its own generator, a vectorised sparse two-way CR engine, retired-bound inversion by order statistics, and seed bases 930 000–980 000.

## 4. Exact frozen formula (reconstructed from spec §8.5 and manifest A5 `EXCLUSION_UPPER_BOUND (D4-R1)`)

```text
U(θ)   = w_core · (θ̂_core + t_{df,0.975} · SE_CR(θ̂_core)) + M_tail
M_tail = Σ_TAIL (n_j − C_j) / Σ_all C_j           (0 if TAIL empty; TAIL iff best ask a_j < 0.04 at T_entry)
w_core = Σ_CORE C_j / Σ_all C_j;  C_j = V_j + F_j (all-in, fee included);  n_j = shares;  payout per share ≤ 1
SE_CR  = √max(V_B, V_S, V_2w), CR1, df = min(G_B, G_S) − 1  (spec 8.1, unchanged)
E1: U < θ_ERT → NET_VALUE_EXCLUDED;  ECONOMIC_BOUND: U<0 / U<θ_ERT / U<max(θ_PCE, θ_ERT) / else
Unresolved at ANALYSIS_TIME: imputed as a WIN for U(θ) (spec 8.6)
```

This matches the Architect's description, so R1 as described is R1 as frozen.

## 5. Old defect reproduced; repaired bound on the named attacks

Astra-C1 design, regenerated independently (design seed 930 777): 120 dates × 35 trades, 48 gamma(2) stations, C = 50, 84 legs at 0.039 (9 inside the observation phase) and 2 legs at 0.001 after it, core c ~ U(0.35, 0.80). Outcome-free readiness: θ_PCE = 0.08, SE0_κ = 0.0129, 47 stations, Kish 33.0, **GO**. Retired bound: TPM/SHR inverted through the (W+1)-th order statistic of the per-draw thresholds under the declared copula (20,000 fresh draws), clipped to λ ∈ [0.05, 1000], μ ∈ [0, 50]. Forward dependence: latent (0.05, 0.05, 0.10).

| Scenario | Reps | θ_true | OLD coverage | OLD false ERT excl. | OLD U<θ_PCE | OLD false rejection (old 17.6) | NEW coverage | NEW false ERT / PCE excl. | NEW false econ. rejection |
|---|---|---|---|---|---|---|---|---|---|
| A1 positive tail / negative core | 8,000 | 0.0315 | **0.8820** [0.8749, 0.8891] | **0.0774** [0.0715, 0.0832] | 0.4391 (not false: θ<PCE) | **0.3398** [0.3294, 0.3501] | 1.000 | 0 / 0 | 0 |
| A2 pure hidden lottery | 5,000 | 0.0852 | 0.8516 [0.8417, 0.8615] | 0.0054 | **0.1248** [0.1156, 0.1340] false LARGE excl. | 0.0280 | 1.000 | 0 / 0 | 0 |
| P3 negative core, fair tail | 2,000 | −0.098 | 0.9995 | (true) 0.381 | (true) 0.829 | (true) 0.859 | 1.000 | exclusion power 0.000 | 0 |

The previous finding reproduces within Monte Carlo error: Astra's 0.0746 [0.0689, 0.0804] against 0.0774 here; coverage 0.8854 against 0.8820. The Architect's run D (0.0742 / 0.8885 / 0.3204) agrees. `M_tail` = 0.9685 in this design, so the repaired bound cannot exclude anything. A1 and A2 are closed.

## 6. PRIMARY FINDING C2 (CRITICAL): R1's proof covers the realised-window estimand, not the frozen prospective estimand

### 6.1 Mathematics

For a **fixed** realised trade set, the §8.5 argument is correct:
`θ_W = w_core θ_core,W + Σ_TAIL n_j p_j / Σ C − Σ_TAIL C_j / Σ C ≤ w_core θ_core,W + M_tail`, for every p ∈ [0,1]^TAIL and every dependence structure (§7). But the labels assert `θ < θ_ERT` for the §5.1 estimand:

```text
θ = E[N]/E[C] = π_core · E[C|core]/E[C] · θ_core + Σ_{tail types k} π_k · E[C|k]/E[C] · (p_k / c_k − 1)
```

The tail contribution depends on the **population arrival rate** π_k of each tail leg type and on its payoff per dollar, which reaches 999 at c = 0.001. `M_tail` substitutes the realised count for π_k. With zero sampled sub-cent legs, `M_tail` contributes nothing for them, yet the prospective contribution `π_k · (p_k/c_k − 1)` is unrestricted. By §8.5's own reasoning ("one unobserved win on a 0.001 leg moves θ by ≈ +0.24"), one unobserved 0.001 **leg**, bought at a rate the window could not detect, moves prospective θ in the same way. The Architect's claim that "the tail can no longer reduce coverage at all, whatever its geometry, **drift** or dependence" is true only for θ_W.

The core stratum does not have this problem to a material degree: payoffs are ≤ 25 per dollar, and the CR residuals `N_j − θ̂ C_j` carry trade-type sampling variability. The gap is specific to the tail, where one leg type can carry a payoff of hundreds per dollar and arrive at a rate below 1/N.

### 6.2 Monte Carlo (`run_super.py`, 4,000 replications each, fresh random design per replication, seeds 950 000+)

Each replication draws 120 dates × Poisson(35) trades and 48 gamma(2) stations, each trade is a 0.001 leg with probability r and otherwise a core leg with c ~ U(0.35, 0.80) and p = c(1+θ_core), and C = 50. The r and p_tail values are declared, not estimated. θ_pop is the exact §5.1 θ. GO and INFO_SUFFICIENT (IF3–IF5) are evaluated per replication, and a false exclusion is counted only when GO ∧ INFO_SUFFICIENT ∧ U < threshold ≤ θ_pop, which is exactly the protocol's path to E1.

| Case | p_tail (×implied) | θ_core | E[# 0.001 legs] | θ_pop | P(GO) | **False exclusion (joint)** | Given GO∧INFO | Coverage of θ_W | Coverage of θ_pop |
|---|---|---|---|---|---|---|---|---|---|
| S1 | 0.17 (170×, Astra-C1 level) | −0.05 | 1.86 | 0.025 | 0.819 | **0.0592** [0.0519, 0.0666] | 0.122 | 0.994 | 0.906 |
| S2 | 0.17 | −0.10 | 3.10 | 0.025 | 0.702 | 0.0213 [0.0168, 0.0257] | 0.051 | 0.999 | 0.962 |
| S3 | 0.50 | −0.10 | 1.05 | 0.025 | 0.883 | **0.1930** [0.1808, 0.2052] | 0.364 | 0.992 | 0.680 |
| S4 | 0.50 | −0.05 | 0.63 | 0.025 | 0.925 | **0.2002** [0.1878, 0.2127] | 0.360 | 0.984 | 0.688 |
| S5 | 0.05 (50×) | −0.05 | 6.42 | 0.025 | 0.481 | 0.0000 | 0.000 | 1.000 | 1.000 |
| S6 | 1.00 | −0.10 | 0.53 | 0.025 | 0.939 | **0.3505** [0.3357, 0.3653] | 0.607 | 0.975 | 0.438 |
| S7 | 0.50 | −0.10 | 1.26 | 0.050 | 0.861 | **0.1538** [0.1426, 0.1649] | 0.303 | 0.994 | 0.734 |
| S8 (PCE) | 0.50 | 0.00 | 0.84 | 0.100 | 0.900 | **0.1532** [0.1421, 0.1644] false LARGE_VALUE_EXCLUDED | 0.272 | 0.991 | 0.645 |
| S9 (PCE) | 0.17 | 0.00 | 2.49 | 0.100 | 0.746 | 0.0275 [0.0224, 0.0326] | 0.060 | 0.998 | 0.933 |

Readings:

1. Coverage of the realised-window θ_W is ≥ 0.975 in every row, so the R1 proof is numerically right *for θ_W*.
2. Coverage of the frozen prospective θ falls to 0.44–0.91. False `NET_VALUE_EXCLUDED` (and therefore false `R*_REJECTED_AS_NET_STRATEGY`) exceeds 0.05 at the previously accepted p = 0.17 (S1) and reaches 0.19–0.35 inside the spec's own admissible class p ∈ [0,1].
3. The GO screen does not protect against this. It passes in 82–94% of the dangerous designs, because 14 dates (≈ 490 trades) usually contain no sub-cent leg. This is the same structural reason Astra's C1 attack was GO-compatible.
4. The failure disappears only when tail legs are frequent enough to appear in almost every window (S5). The dangerous region is rare, very high-payoff tail types, which is precisely what R1 was meant to make assumption-free.

### 6.3 Severity and classification

**CRITICAL.** This is a reproducible, GO-compatible configuration inside the admissible class the spec itself freezes (all p ∈ [0,1]; R* may buy any ask ≥ the 0.001 tick). In it, the protocol issues `NET_VALUE_EXCLUDED` and `R*_REJECTED_AS_NET_STRATEGY` with a false-claim probability above the declared 0.05, while the frozen estimand θ > θ_ERT. It is not loss of power, because the label is issued. It is not a model-misspecification caveat either, because no model is declared: the proof proves a statement about a different estimand.

`D4_STRUCTURED_BOUND = VALID_FOR_REALISED_WINDOW_ESTIMAND_ONLY — INVALID_FOR_FROZEN_PROSPECTIVE_θ (§5.1)`.

## 7. Deterministic domination over the conditional class (mission §6, §9)

With the trade set fixed, each TAIL leg contributes `n_j y_j − C_j ≤ n_j − C_j` for any payout per share `y_j ∈ [0,1]`. Summing gives `Σ_TAIL N_j ≤ Σ_TAIL (n_j − C_j)`, so `θ_W ≤ w_core θ_core,W + M_tail` pointwise, for every outcome configuration and every dependence structure. It follows that `{θ_core,W ≤ U_core} ⊆ {θ_W ≤ U}` and that coverage for θ_W is at least core coverage. **The proof is correct for θ_W.**

Attack surface checked for the conditional statement:

| Surface | Finding |
|---|---|
| denominator | `Σ_all C_j` is identical in θ̂, w_core and M_tail, so no mismatch |
| capital weighting / partial fills / tiny C_j | C_j cancels inside `n_j = C_j / c_j`; a partial fill scales both; tiny costs pass (numeric check covers C ∈ [0.01, 50]) |
| n_j, C_j | `C_j` includes the fee; `n_j` is the shares received; payout ≤ n_j |
| void / 50-50 / partial payoff | `y ∈ [0,1]` ⇒ dominated (numeric check includes y ∈ {0, 0.5, 1} and y ~ U(0,1)) |
| unresolved / disputed | §8.6 imputes a WIN for U(θ), so dominated |
| settlement fees | R* pays its fee at entry (inside C_j); any settlement deduction only lowers the payout |
| rounding | `M_tail` is computed from recorded fills; rounding enters only through the recorded n_j, C_j |
| duplicated capital / simultaneous positions | mutually exclusive tail legs cannot all win, so M_tail over-bounds (conservative); ledger duplication is a replay-invariant matter (V1 §24), outside D4 |
| missing legs | legs that never entered the ledger are **not** in θ_W. This is the same gap as C2 when the missing mechanism is the arrival process |

Numeric: `check_det.py` evaluated 99,310 random trade sets and payoff configurations. The maximum relative violation was 7.2e-16 (floating point). The adversarial random search `run_search.py` sampled 1,200 configurations × 200 replications = 240,000 across tail fraction {0, ≈0.01–0.1%, 1, 2, 5, 10, 16, 25, 40%}, tail price {0.001, 0.002, 0.005, 0.01, 0.02, 0.039}, core effect {−0.15, −0.10, −0.05, 0, +0.02}, tail p {0, implied, 2×, 5×, 10×, 1, tuned so θ = θ_ERT + 0.001}, dependence {independent, strong date, strong station, comonotone tail ("perfect" / "shared jackpot")}, capital {uniform, concentrated, dominant tail}, geometry {120/48/35, 60/25/35, 60/25/17} and core price floor {0.04, 0.2, 0.35, 0.6}. It found **zero** replications with a false exclusion but no core miss. The worst configurations were re-run with 20 fresh designs × 200 = 4,000 replications each: false ERT exclusion ≤ 0.0278 and coverage ≥ 0.9658. Within the conditional class there is **no new false-exclusion mechanism**.

## 8. Core-bound coverage (mission §10, §11, §12)

This is conditional-on-design truth with the tail empty unless stated, run on fresh random designs (100 replications per design). `cov_core` is coverage of θ_core by U_core at nominal 0.975. `False excl.` is P(U < θ_ERT ∧ INFO_SUFFICIENT) at θ_true = 0.02, which is the protocol's false-claim rate. There are 4,000 replications per row, so the MC SE is ≈ 0.0025 near 0.975.

| Geometry | Dependence (latent date, station, cell) | cov_core [95% MC] | False excl. [95% MC] | P(INFO_SUFF) |
|---|---|---|---|---|
| 120/48 standard | TRUE (0.05, 0.05, 0.10) | 0.9762 [0.9715, 0.9810] | 0.0177 [0.0137, 0.0218] | 0.63 |
| 120/48 | strong date (0.30, 0.02, 0.10) | 0.9768 | 0.0042 | 0.09 |
| 120/48 | strong station (0.02, 0.30, 0.10) | 0.9740 | 0.0000 | 0.00 |
| 120/48 | mixed (0.15, 0.15, 0.10) | 0.9730 | 0.0000 | 0.00 |
| 120/48 | AR(1) φ = 0.9 regime spanning blocks | **0.8768** [0.8666, 0.8869] | 0.0018 | 0.01 |
| 120/48 unequal stations gamma(0.7) | TRUE | 0.9742 | 0.0138 | 0.37 |
| 120/48 one station = 20% of trades | TRUE | 0.9685 | 0.0228 | 0.49 |
| 120/48 one date block = 25% of trades | TRUE | 0.9668 | 0.0148 | 0.32 |
| 120/48 favourite NO legs, edge in c>0.8 | TRUE | 0.9782 | 0.0190 | 0.83 |
| 120/48 6% boundary legs c∈[0.04,0.06], edge hidden there | TRUE | 0.9702 | 0.0250 [0.0202, 0.0298] | 0.64 |
| 120/48 station-heterogeneous edge (sd 0.15) | TRUE | 0.9920 | 0.0022 | 0.08 |
| 120/48 edge only at 20% dominant station | TRUE | 0.9602 [0.9542, 0.9663] | 0.0265 | 0.12 |
| 120/48 concentrated capital (50% at 1–5 USD) | TRUE | 0.9740 | 0.0208 | 0.63 |
| **60/25 minimum** | TRUE | 0.9735 | 0.0222 | 0.64 |
| 60/25 | strong date | 0.9730 | 0.0122 | 0.21 |
| 60/25 | strong station | 0.9760 | 0.0000 | 0.00 |
| 60/25 | mixed | 0.9728 | 0.0000 | 0.01 |
| 60/25 | regime AR(1) | **0.8810** [0.8710, 0.8910] | 0.0100 | 0.06 |
| 60/25 one station 12% | TRUE | 0.9745 | 0.0205 | 0.63 |
| 60/25 one block 25% | TRUE | 0.9730 | 0.0182 | 0.51 |
| 60/25 boundary hidden edge | TRUE | 0.9665 | 0.0290 [0.0238, 0.0342] | 0.70 |
| 60/25 favourite skew | TRUE | 0.9785 | 0.0210 | 0.84 |
| **60/25, 17 trades/date, log-uniform c∈[0.04,0.90]** | mixed | **0.9458** [0.9387, 0.9528] | **0.0440** [0.0376, 0.0504] | 0.32 |
| 60/25 edge at dominant station | strong station | 0.9818 | 0.0002 | 0.00 |

Boundary tests (§11), P(U < 0.02 ∧ INFO_SUFF), 4,000 replications each; the columns are 120/48 TRUE, 60/25 TRUE, 60/25 mixed and 60/25 strong station:

| θ_true | 120/48 TRUE | 60/25 TRUE | 60/25 mixed | 60/25 station |
|---|---|---|---|---|
| 0.020 | 0.0202 | 0.0222 | 0.0005 | 0.0000 |
| 0.021 | 0.0210 | 0.0185 | 0.0005 | 0.0000 |
| 0.025 | 0.0115 | 0.0165 | 0.0000 | 0.0000 |
| 0.030 | 0.0095 | 0.0148 | 0.0005 | 0.0000 |

Without the INFO filter the largest value is P(U < 0.02) = 0.0282. PCE tests (§12), P(U < θ_PCE ∧ INFO_SUFF) with θ_true = θ_PCE ∈ {0.05, 0.07, 0.08, 0.10}: 120/48 TRUE gives 0.0200 / 0.0238 / 0.0198 / 0.0242, and 60/25 mixed gives ≤ 0.0005.

Conclusion: **D4_CORE_COVERAGE = DEFENSIBLE.** The core CR bound, at nominal one-sided 0.975, delivers 0.946–0.992 across the adversarial class. The protocol's false ERT and PCE exclusion rates at or just above the threshold are ≤ 0.044 in every row, below the declared 0.05 for U(θ). The Architect's 0.9705–0.993 range reproduces, apart from my harsher m = 17 wide-price mixed case (0.946). The one geometry that breaks 0.95 is dependence persisting beyond the 5-date blocks (AR(1) regime, coverage ≈ 0.88). There IF5 (DEFF ≤ 6) fails in 94–99% of runs, so the realised false-claim rate stays ≤ 0.010. That is the carried D8 finite-cluster / block-length limitation, and R1 does not regress it.

## 9. Sub-cent consequence (mission §13)

Verified. One 0.001 leg at S_ref among 4,200 trades gives `M_tail` ≈ 0.238. In the Astra design `M_tail` = 0.9685, and every ERT or PCE exclusion becomes impossible (P3: exclusion power 0.000 at θ = −0.098). The labels are correct for this conservatism: E1 is unreachable, the run lands in E4 `NET_VALUE_INDETERMINATE` (or E2/E3 only if T2 ∧ θ̂ ≥ θ_ERT), `ECONOMIC_BOUND = NOT_EXCLUDED` and `EXCLUSION_BLOCKED_BY_TAIL` are reported, and the mandatory sentence fires. No "edge exists" or "edge excluded" label is produced. This is loss of power, **not** invalidity.

## 10. R* rejection semantics (mission §14)

The frozen rule 17.6 now reads `R*_REJECTED_AS_NET_STRATEGY iff ECONOMIC_RESULT = NET_VALUE_EXCLUDED` and `R*_CORE_INFORMATION_REJECTED iff INFORMATION_RESULT = NEGATIVE_INFORMATION`. The manifest `REJECTION_RULE (D4-R1)` row is identical.

Test case A1 (θ_true = 0.0315 > θ_ERT, core information negative, tail economically positive): `negInfo` = 0.336, `R*_REJECTED_AS_NET_STRATEGY` = 0.000 (old rule: 0.340). The terminal state `NEGATIVE_INFORMATION__NET_VALUE_INDETERMINATE` keeps the economic and information results separate. **The rule is correct as a rule.** Its economic input, E1, is the bound shown invalid for prospective θ in §6, so `R*_REJECTED_AS_NET_STRATEGY` inherits C2 (S1: 0.0592 false).

MINOR m2 (pre-existing precedence, not an R1 regression): I1 precedes I2, so when T1 passes through the tail and NEG also holds, INFORMATION_RESULT = INFORMATION_DETECTED with `CORE_ADVERSE = TRUE`. In that case `R*_CORE_INFORMATION_REJECTED` is not issued, and the forward-signal rule 17.5 does **not** refuse a signal. The new 17.6 prose ("the forward-signal rule … still refuses a forward signal when the core is adverse") is therefore inaccurate for this cell. Either key `R*_CORE_INFORMATION_REJECTED` and the 17.5 clause on NEG / CORE_ADVERSE, or correct the prose.

## 11. T1 / T2 / NEG, PINM and retired tail models (mission §15, §16)

- The spec diff 94b59348 → 24d2342 does not touch §6.1's T1a / T1b / T1 / T2 / NEG rows (only the EXCL row changed), §8.1, §8.3, §8.4 or §8.2's engine definition. Only the PINM "Uses" paragraph changed, removing the bound use. The manifest T1b RULE and NEG RULE rows are unchanged. **No coupling regression.**
- PINM now gates only T1b (spec §8.2, manifest A5). NEG enters only I2 and CORE_ADVERSE. Enumerating all 64 combinations of (T1, NEG, U<θ_ERT, T2, θ̂≥θ_ERT, GATES) shows `R*_REJECTED_AS_NET_STRATEGY ⇔ U < θ_ERT` in every combination, so NEG cannot drive NET_VALUE_EXCLUDED.
- TPM / SHR / model-conditional tail: remaining mentions are historical only (spec §2 row D4-UB, §8.5 first paragraph, §21 item 21, manifest "RETIRED" row, delta D4.c / D4.d, power table §4.5). There is no live dependency in E1, ECONOMIC_BOUND, 17.6, ERT/PCE exclusion or the terminal labels. MINOR m1: spec §24 "Can:" still says "an interval for θ … and a **model-conditional** upper bound", which is stale wording.

## 12. MP1 and spec / code consistency (mission §17)

**MP1 = CLOSED.** The committed sim at 24d2342 sets `LAMBDA_RANGE = (0.05, 1000.0)`, `MU_RANGE = (0.0, 50.0)`, `BISECTION_ITERS = 40`, log bisection for λ and the interval-end rule. Run D uses B = 20,000 in 20 chunks of 1,000 with `SeedSequence([20260929, 1])` and the date → station → cell → trade order. `tail_worst_case` implements `M_tail` exactly as frozen, and `core_stats` uses the frozen 0.975 core level and NEG at 0.025.

Residual spec/code note (non-blocking): all Architect run-D "core class" coverage is computed against the **conditional** θ of each design, matching the §8.5 proof and hence the C2 gap. The run-D table therefore cannot detect C2 by construction. Runs A/B keep B = 1,000 PINM draws (historical, disclosed).

## 13. State machine (mission §18)

The partition is unchanged: 3 INFORMATION_RESULT × 4 ECONOMIC_RESULT + 2 pre-empting values = 14 SCIENTIFIC_STATE values, ordered lists with "otherwise" rows, total and mutually exclusive. R1 adds a useful invariant: `U ≥ θ̂`, because `M_tail ≥ w_tail θ̂_tail`, and with §8.6 win-imputation for U, `U(win) ≥ θ̂(win) ≥ θ̂(loss)`. E1 and E2's `θ̂ ≥ θ_ERT` therefore cannot hold together, so E1 precedence can no longer override a confirmable result. The two rejection flags are independent Booleans; they can both be TRUE, which is correct. No new hole exists in the state machine itself. The only defect is C2 in E1's input and m2 above.

## 14. No outcome leakage; trading-rule immutability (mission §19, §20)

- R1's evidence is synthetic run D plus algebra. The manifest section C records outcome use = NO and the architect state records `OUTCOME_INFORMATION_USED = FALSE`. No committed file between 7d95c00 and 24d2342 contains or references Weather outcomes, wallet data or P&L. **No leakage found.**
- Spec §3 (R*), §5.1–5.2 (θ, strata), §10 (PCE / GO), §14 (cohort), §15 (execution) and §11 (horizon) are untouched. The manifest diff touches only the NULLS / ALPHA / PINM / bound / rejection / readiness-report rows. R*, the signal, h, W, entry, cohort, size (S_ref) and execution trigger are unchanged. **TRADING_RULE_CHANGED = FALSE is confirmed.** The OP report now also carries descriptive `TAIL_MAX_CONTRIBUTION`, which is not a GO criterion.

## 15. Claim strength (mission §21)

| Label | What the data actually support after R1 |
|---|---|
| NET_VALUE_EXCLUDED / RELEVANT_VALUE_EXCLUDED | `θ_W < θ_ERT` for **the trades R* made in the window**, at ≥ 95% (≥ core coverage). **Not** `θ < θ_ERT` for the §5.1 prospective θ: tail leg types absent from the window are unbounded (C2). |
| LARGE_VALUE_EXCLUDED | as above with θ_PCE |
| R*_REJECTED_AS_NET_STRATEGY | as NET_VALUE_EXCLUDED; the name asserts a prospective strategy-level claim that the bound does not support |
| R*_CORE_INFORMATION_REJECTED | κ_core < 0 at 0.025 (information-level), correctly not economic; see m2 for the T1-via-tail cell |
| NET_VALUE_INDETERMINATE / EXCLUSION_BLOCKED_BY_TAIL | legitimate and correctly used when M_tail is wide |
| NET_VALUE_CONFIRMED | T2 on θ, unchanged by R1, out of D4 scope (carried PASS) |

## 16. Carried-forward items

D1, D2, D3, D5, D6, D7, D8, D9, D11 and D12 remain **CLOSED**; D10 remains **CLOSED_ACCEPTED_AND_DISCLOSED**. R1 touched none of their frozen text, apart from the D2 E1 input (C2) and the 17.6 rule (correct as a rule). No regression was found.

Observations (not D4, not blocking, recorded for governance):
- O1: IF5 (`DEFF_2w(κ̂_core) ≤ 6`) fails in ≈ 37% of runs at 120/48 under the Architect's own TRUE dependence, and in ≈ 100% under strong-station or mixed dependence (§8, P(INFO_SUFF) column). INFORMATION_INSUFFICIENT may therefore be a frequent outcome. This is a feasibility risk, not a validity defect.
- O2: dependence persisting across 5-date blocks under-covers the core bound (≈ 0.88). The realised false-claim rate is held ≤ 0.010 only because IF5 screens it. This is the carried D8 limitation.

## 17. Acceptance conditions (mission §22)

| # | Condition | Result |
|---|---|---|
| 1 | Previous false-exclusion defect reproduced | **PASS**: 0.0774 [0.0715, 0.0832]; coverage 0.882 |
| 2 | New tail maximum dominates over the full frozen admissible tail class | **FAIL**: dominates for the realised trade set (proved; 99,310 + 240,000 checks), not for the frozen prospective θ, whose tail term depends on the unsampled arrival rate of tail leg types (§6) |
| 3 | No false economic exclusion mechanism found | **FAIL**: C2, S1 0.0592 at p = 0.17; up to 0.35 within the class; LARGE 0.153 |
| 4 | Core-bound coverage defensible at minimum geometry | **PASS**: 0.946–0.992; false-claim ≤ 0.044 |
| 5 | R* rejection depends only on economic exclusion | **PASS** as a rule (inherits C2 through E1) |
| 6 | NEGATIVE_INFORMATION is information-only | **PASS** (m2 minor) |
| 7 | TPM/SHR retired from exclusion authority | **PASS** (m1 stale wording) |
| 8 | Simulation matches the frozen contract | **PASS**: MP1 closed |
| 9 | No new state-machine hole | **PASS** (partition intact; C2 is a bound-validity defect) |
| 10 | No outcome leakage / strategy-rule change | **PASS** |

## 18. Smallest repair surface (bounded Architect repair only)

EXACT_INVARIANT_TO_ADD: an exclusion label may assert only the estimand its bound covers. Either the exclusion estimand is explicitly the realised-window value θ_W, or the bound covers the prospective θ over the full admissible class, including tail leg types whose arrival rate the window cannot resolve.

Options, from smallest to largest:

- **R2-a (recommended, semantic, no new statistics).** Freeze θ_W (conditional on the realised trade set) as the estimand of E1 and ECONOMIC_BOUND. Rename or qualify E1, the ECONOMIC_BOUND values and 17.6, for example `NET_VALUE_EXCLUDED_REALISED_WINDOW` and `R*_WINDOW_NET_VALUE_EXCLUDED`, instead of a prospective `R*_REJECTED_AS_NET_STRATEGY`. Add a mandatory sentence: "the prospective θ of R*, including tail leg types absent from the window (count of TAIL legs by price bin printed), is not excluded". State in §8.5 that the proof is conditional, and in §24 that prospective economic exclusion is not available assumption-free. Add the C2 attack (S1, S3) to the committed sim and power table. Keep T2 / confirmation semantics prospective and unchanged.
- **R2-b.** Keep prospective semantics and add a prospective tail allowance valid over the class, for example a one-sided 97.5% Poisson upper bound on the arrival rate of legs at each tick-price bin times the max payoff `1/c − 1`, with Bonferroni against the core. With zero observed 0.001 legs in ≈ 4,200 trades this is ≈ 3.69/4,200 × 999 ≈ 0.88, so economic exclusion becomes practically unreachable. The spec must then say so and route all negative evidence through the information axis.
- **R2-c (not recommended).** An outcome-blind declared cap on tail p/c. This re-introduces a model-conditional exclusion (the V2@94b5934 failure class) and would need its own coverage audit.

AFFECTED FILES: spec §5.1 (exclusion estimand), §8.5 (proof scope + consequences), §17.2 E1 wording, §17.3, §17.6, §17.7, §24, §27; manifest A5 `EXCLUSION_UPPER_BOUND` / `REJECTION_RULE` rows and section C; delta D4.f; power table §4.5 (add C2 evidence); synthetic sim (add the superpopulation run). Optionally fix m1 and m2 in the same pass.

DO NOT CHANGE: R*, h, W, cohort, strata, S_ref, T1a/T1b/T2/NEG, engines, dependence, PCE/GO, gates, analysis time, the closed D-items.

REQUIRED RECHECK SURFACE: the E1 / ECONOMIC_BOUND / 17.6 estimand and labels; a fresh prospective-estimand Monte Carlo (S1–S9 class); the claim matrix.

## 19. Verdict

```text
ASTRA_WEATHER_V2_D4_RECHECK = BLOCKED_D4_PROSPECTIVE_ESTIMAND_UNSAMPLED_TAIL_FALSE_EXCLUSION
D4                          = OPEN_CRITICAL (C1 mechanism closed for the realised trade set; C2 open)
D4_STRUCTURED_BOUND         = VALID_FOR_REALISED_WINDOW_θ_W_ONLY; INVALID_FOR_FROZEN_PROSPECTIVE_θ
D4_CORE_COVERAGE            = DEFENSIBLE (0.946–0.992; false-claim ≤ 0.044; regime-dependence limitation carried)
D4_FALSE_EXCLUSION          = C1 REPRODUCED AND CLOSED (A1/A2: 0); C2 NEW: prospective θ = 0.025 falsely excluded 0.0592
                              [0.0519, 0.0666] at p = 0.17, up to 0.35 within the frozen class; LARGE 0.153 at θ = 0.10
D4_RSTAR_SEMANTICS          = RULE CORRECT (iff NET_VALUE_EXCLUDED; NEG information-only); inherits C2; m2 minor
MP1_STATUS                  = CLOSED
REGRESSIONS                 = NONE in D1–D3, D5–D12, T1/T2/NEG, PINM, state partition; MINOR m1 (stale §24 wording), m2 (T1∧NEG cell)
EXPERIMENT_FEASIBILITY_V2   = BLOCKED_D4_PROSPECTIVE_ESTIMAND_UNSAMPLED_TAIL_FALSE_EXCLUSION
NEXT_AUTHORIZED_ACTION      = BOUNDED ARCHITECT REPAIR ONLY (section 18; R2-a recommended)
BUILDER_AUTHORIZED          = FALSE
REAL_CAPITAL_AUTHORIZED     = FALSE
LIVE_TRADING_AUTHORIZED     = FALSE
t0                          = NOT_DECLARED
```
