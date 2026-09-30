# WEATHER FORWARD V2 — POWER, FEASIBILITY AND SIMULATION TABLE — 2026-09-29

```text
ROLE    = Builder-readable power / feasibility evidence for WEATHER_FORWARD_FALSIFICATION_SPEC_V2_2026-09-29.md
LABELS  = DERIVED (arithmetic) · SIMULATED (synthetic Monte Carlo, script committed alongside) · ASSUMED (scenario input)
DATA    = no outcome, settlement, P&L, winner, wallet or price-history data used; throughput scenarios are Astra's
          measured pre-outcome trigger rates rescaled to the V2 cohort
```

## 1. Conventions

- `z_{0.95} + z_{0.80} = 2.4865` (MDE80), `z_{0.95} + z_{0.90} = 2.9264` (MDE90), one-sided α = 0.05.
- `SE(θ̂) = σ_eff √(DEFF / n)`; `SE(κ̂_core) = 0.48 √(DEFF / n_core)` (per-share SD at the core price mix c ~ U(0.35, 0.80)).
- Planning dependence `DEFF(m) = 1.5 × (1 + 0.03 (m − 1))`: date factor with latent-scale ρ_d = 0.03 (the date ceiling), station factor 1.5. It lies inside Astra's 2–4 range and rises with trades per date.
- V2 cohort throughput (°C + °F): ≈ 66 °C + 21 °F entry-expected events/day at 95% completeness ≈ 87/day; Astra's trigger rates 20% / 40% / 63% → **PESSIMISTIC 17, CONSERVATIVE 35, CENTRAL 55 trades/day**. Astra's °C-only 13 / 27 / 42 are shown in 2.2 for reference.
- Tail share 16% of trades (Astra: 6 of 38 triggers below 0.05), mean tail all-in cost 0.0127 (log-uniform 0.002–0.04).

## 2. Analytic feasibility (DERIVED)

### 2.1 Feasibility grid, V2 cohort

| Dates | Scenario | m | RAW trades | CORE | TAIL | Λ_tail (fair-null wins) | Date blocks | Station clusters (traded / Kish, ASSUMED) | DEFF | n_eff | SE κ_core | MDE80 κ_core | SE θ σ=1.0 | MDE80 / MDE90 θ σ=1.0 | SE θ σ=2.0 | MDE80 / MDE90 θ σ=2.0 | SE θ σ=2.9 | MDE80 / MDE90 θ σ=2.9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 60 | PESSIMISTIC | 17 | 1,020 | 857 | 163 | 2.1 | 12 | ≈ 38 / ≈ 28 | 2.22 | 459 | 0.0244 | 0.061 | 0.0467 | 0.116 / 0.137 | 0.0933 | 0.232 / 0.273 | 0.1353 | 0.336 / 0.396 |
| 60 | CONSERVATIVE | 35 | 2,100 | 1,764 | 336 | 4.3 | 12 | ≈ 44 / ≈ 32 | 3.03 | 693 | 0.0199 | 0.049 | 0.0380 | 0.094 / 0.111 | 0.0760 | 0.189 / 0.222 | 0.1102 | 0.274 / 0.322 |
| 60 | CENTRAL | 55 | 3,300 | 2,772 | 528 | 6.7 | 12 | ≈ 46 / ≈ 34 | 3.93 | 840 | 0.0181 | 0.045 | 0.0345 | 0.086 / 0.101 | 0.0690 | 0.172 / 0.202 | 0.1001 | 0.249 / 0.293 |
| 90 | PESSIMISTIC | 17 | 1,530 | 1,285 | 245 | 3.1 | 18 | ≈ 38 / ≈ 28 | 2.22 | 689 | 0.0199 | 0.050 | 0.0381 | 0.095 / 0.111 | 0.0762 | 0.189 / 0.223 | 0.1105 | 0.275 / 0.323 |
| 90 | CONSERVATIVE | 35 | 3,150 | 2,646 | 504 | 6.4 | 18 | ≈ 44 / ≈ 32 | 3.03 | 1,040 | 0.0162 | 0.040 | 0.0310 | 0.077 / 0.091 | 0.0620 | 0.154 / 0.182 | 0.0899 | 0.224 / 0.263 |
| 90 | CENTRAL | 55 | 4,950 | 4,158 | 792 | 10.1 | 18 | ≈ 46 / ≈ 34 | 3.93 | 1,260 | 0.0148 | 0.037 | 0.0282 | 0.070 / 0.082 | 0.0564 | 0.140 / 0.165 | 0.0817 | 0.203 / 0.239 |
| **120** | PESSIMISTIC | 17 | 2,040 | 1,714 | 326 | 4.1 | 24 | ≈ 38 / ≈ 28 | 2.22 | 919 | 0.0173 | 0.043 | 0.0330 | 0.082 / 0.097 | 0.0660 | 0.164 / 0.193 | 0.0957 | 0.238 / 0.280 |
| **120** | CONSERVATIVE | 35 | 4,200 | 3,528 | 672 | 8.5 | 24 | ≈ 44 / ≈ 32 | 3.03 | 1,386 | 0.0141 | 0.035 | 0.0269 | 0.067 / 0.079 | 0.0537 | 0.134 / 0.157 | 0.0779 | 0.194 / 0.228 |
| **120** | CENTRAL | 55 | 6,600 | 5,544 | 1,056 | 13.4 | 24 | ≈ 46 / ≈ 34 | 3.93 | 1,679 | 0.0128 | 0.032 | 0.0244 | 0.061 / 0.071 | 0.0488 | 0.121 / 0.143 | 0.0708 | 0.176 / 0.207 |

120 counted dates is the only analysed horizon (spec §11.3); 60 and 90 are shown to make the information growth visible, not as analysis options. Station-cluster counts are projections (48 NOAA stations, gamma-distributed activity); the observation phase measures them.

### 2.2 Astra °C-only throughput at 120 dates (reference)

| Scenario | m | RAW | DEFF | SE θ σ=1.0 | MDE80 σ=1.0 | SE θ σ=2.9 | MDE80 σ=2.9 | SE κ_core | MDE80 κ_core |
|---|---|---|---|---|---|---|---|---|---|
| PESSIMISTIC | 13 | 1,560 | 2.04 | 0.0362 | 0.090 | 0.1049 | 0.261 | 0.0189 | 0.047 |
| CONSERVATIVE | 27 | 3,240 | 2.67 | 0.0287 | 0.071 | 0.0832 | 0.207 | 0.0150 | 0.037 |
| CENTRAL | 42 | 5,040 | 3.34 | 0.0258 | 0.064 | 0.0747 | 0.186 | 0.0135 | 0.034 |

### 2.3 Required independent trades and calendar

| θ | N_naive σ=1.0 | σ=2.0 | σ=2.9 | dates at 35/day, DEFF 3.03, σ=1.0 | σ=2.0 | σ=2.9 |
|---|---|---|---|---|---|---|
| 0.02 | 15,457 | 61,827 | 129,991 | 1,338 | 5,352 | 11,253 |
| 0.05 | 2,473 | 9,892 | 20,799 | 214 | 856 | 1,801 |
| 0.10 | 618 | 2,473 | 5,200 | 54 | 214 | 450 |

Reproduces Astra §6.3 and Fable §1.1. **θ = 0.02 is a 3.7-year quantity at σ = 1 and a 31-year quantity at σ = 2.9.**

### 2.4 Binding constraint: target dates (date ceiling `n_eff ≤ D / ρ_d`)

| ρ_d | 60 dates | 90 | 120 | 240 |
|---|---|---|---|---|
| 0.02 | 3,000 | 4,500 | 6,000 | 12,000 |
| 0.03 | 2,000 | 3,000 | 4,000 | 8,000 |
| 0.05 | 1,200 | 1,800 | 2,400 | 4,800 |
| 0.10 | 600 | 900 | 1,200 | 2,400 |

Raising trades per date beyond `≈ 1/ρ_d` buys almost nothing; only dates (or a lower-variance statistic, κ) buy information. The table in 2.1 shows it directly: going from 35 to 55 trades/day (+57% trades) raises n_eff by only 21%.

## 3. θ label probabilities at 120 dates, CONSERVATIVE throughput (DERIVED, normal approximation, CR engine, before gates)

| σ_eff | SE θ | θ_PCE (formula) | θ = 0.00 | θ = 0.02 | θ = 0.05 | θ = 0.10 |
|---|---|---|---|---|---|---|
| 1.0 | 0.0269 | 0.07 | 0.05 / 0.18 / 0.83 | 0.18 / 0.05 / 0.59 | 0.59 / 0.00 / 0.18 | 0.98 / 0.00 / 0.00 |
| 2.0 | 0.0537 | 0.14 | 0.05 / 0.10 / 0.83 | 0.10 / 0.05 / 0.72 | 0.24 / 0.01 / 0.51 | 0.59 / 0.00 / 0.18 |
| 2.9 | 0.0779 | 0.20 | 0.05 / 0.08 / 0.82 | 0.08 / 0.05 / 0.75 | 0.16 / 0.02 / 0.61 | 0.36 / 0.00 / 0.36 |

Cells: `P(T2 rejects) / P(U < θ_ERT) / P(U < θ_PCE)`. These are core-only bounds; with lottery legs the exclusion bound makes `P(U < θ_ERT) ≈ 0` (section 4; after D4 repair R1 exactly 0 whenever `M_tail` alone exceeds the threshold). At σ_eff = 1, a true θ = 0.02 is confirmed 18% and excluded 5% of the time: the ERT band is unresolved by construction.

## 4. Synthetic Monte Carlo (SIMULATED)

Script: `WEATHER_FORWARD_V2_SYNTHETIC_SIM_2026-09-29.py`. Design per replication: 120 dates, Poisson(35) trades/date, 48 stations with gamma(2, 1) activity, 5-date blocks; price mixes **M00** (95% core c ~ U(0.35, 0.80), 5% mid c ~ U(0.04, 0.35), no tail), **M05** (5% tail, 5% mid), **M16** (16% tail log-U(0.002, 0.04), Fable's mix); capital 50 USD w.p. 0.68 else U(10, 50); true dependence latent Gaussian (date, station, station-day cell) = **TRUE** (0.05, 0.05, 0.10), **STRESS** (0.15, 0.15, 0.10), **SST** strong station (0.02, 0.15, 0.10); PINM declared (0.10, 0.10, 0.10), B = 1,000 in simulation. **Runs A and B were produced by the script at V2@94b5934; their U(θ) columns ("struct.", U<ERT, False U<PCE) refer to the RETIRED TPM ∨ SHR bound computed with that script's bisection (λ ≤ 200, μ ≤ 20, 30 iterations — Astra MP1). They are kept as the record. The repaired bound satisfies U_repaired ≥ U_retired pointwise, so every repaired exclusion rate is ≤ the tabulated one and every repaired coverage ≥ it; in tail-free rows (M00) the two bounds are identical. Exact-contract evidence and the repair are in §4.5 (run D).** 200 replications per row (Monte-Carlo SE ≈ 0.015 near 0.05, ≈ 0.035 near 0.5). Scenario "uniform(θ)": every leg `p = c (1 + θ)`; "tail_mult(k)": core fair, tail `p = k c`; "core_plus_tail_over": core `p = 1.05 c`, tail `p = 0.5 c`; "hidden_lottery(10)": only legs with `c < 0.005` at `p = 10 c`; "shrink(μ)": `p = c + μ (q − c)`.

### 4.1 Run A — Fable-style configuration (engine conjunction + fixed-sequence gate), seeds 1000–1016

| Scenario | Mix | θ_true | T1 (conj.) | T2 CR | T2 PINM | T2 conj. | Gated net-value claim (S3+S4) | U(θ) coverage (struct. / naive) | Notes |
|---|---|---|---|---|---|---|---|---|---|
| uniform(0) | M00 | 0 | 0.000 | 0.060 | 0.010 | 0.010 | 0.00 | 0.975 / 0.915 | date-only κ 0.105 |
| uniform(0.02) | M00 | 0.02 | 0.005 | 0.115 | 0.030 | 0.030 | 0.005 | 0.985 / 0.955 | |
| uniform(0.05) | M00 | 0.05 | 0.125 | 0.395 | 0.150 | 0.150 | 0.12 | 0.975 / 0.925 | |
| uniform(0.10) | M00 | 0.10 | 0.725 | **0.910** | **0.755** | 0.755 | 0.70 | 0.98 / 0.955 | PINM power loss |
| uniform(0) | M05 | 0 | 0.015 | 0.010 | 0.040 | 0.005 | 0.00 | 1.00 / 0.87 | |
| uniform(0.10) | M05 | 0.10 | 0.69 | 0.52 | 0.275 | 0.205 | 0.185 | 1.00 / 0.845 | |
| uniform(0) | M16 | 0 | 0.010 | 0.015 | 0.065 | 0.010 | 0.00 | 1.00 / 0.83 | |
| uniform(0.10) | M16 | 0.10 | 0.70 | 0.185 | 0.195 | 0.110 | 0.10 | 1.00 / 0.825 | |
| tail_mult(3) | M16 | 0.32 | 0.915 | 0.645 | 0.77 | 0.615 | 0.615 | 1.00 / 0.87 | |
| hidden_lottery(10) | M16 | 0.44 | 0.23 | **0.61** | 0.885 | 0.61 | **0.23** | **0.89** / 0.885 | gate blocks 2/3 |
| uniform(−0.10) | M16 | −0.10 | 0 | 0 | 0 | 0 | 0 | 1.00 / 0.83 | NEG (conj.) 0.83 |
| core_plus_tail_over | M16 | −0.038 | 0.155 | 0.000 | 0.015 | 0 | 0 | 1.00 / 0.79 | κ_core = +0.029 |

### 4.2 Run B — V2 configuration (spec §6–8; NEG shown at 0.05, see 4.3), seeds 1000–1017

| Scenario | Mix / dep. | θ_true | κ_true | T1a CR | T1b PINM (block) | T1 | T2 CR (PINM aux.) | NEG@0.05 | U cover (struct. / naive) | U<ERT | False U<PCE | Main states (INFORMATION \| ECONOMIC) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| uniform(0) | M00 TRUE | 0 | 0 | 0.025 | – | 0.025 | 0.060 (0.010) | 0.070 | 0.975 / 0.915 | 0.095 | 0 | ND\|IND 0.845, ADV\|EXCL 0.07, ND\|CONF 0.035, DET\|CONF 0.025 |
| uniform(0) | M00 STRESS | 0 | 0 | 0.015 | – | 0.015 | 0.030 (0.065) | 0.045 | 0.98 / 0.945 | 0.055 | 0 | ND\|IND 0.915 |
| uniform(0) | M00 SST | 0 | 0 | 0.025 | – | 0.025 | 0.055 (0.050) | 0.040 | 0.98 / 0.945 | 0.055 | 0 | ND\|IND 0.89 |
| uniform(0.05) | M00 | 0.05 | 0.028 | 0.39 | – | 0.39 | 0.43 (0.23) | 0 | 0.975 / 0.955 | 0 | 0 | DET\|CONF 0.365, ND\|CONF 0.065, ND\|IND 0.545 |
| uniform(0.10) | M00 | 0.10 | 0.056 | 0.865 | – | 0.865 | **0.855 (0.73)** | 0 | 0.945 / 0.93 | 0.005 | 0.01 | DET\|CONF 0.855 |
| uniform(0) | M05 | 0 | 0 | 0.030 | 0.020 (0.015) | 0.050 | 0.015 (0.035) | 0.065 | 1.00 / 0.91 | 0 | 0 | ND\|IND 0.885 |
| uniform(0.05) | M05 | 0.05 | 0.028 | 0.34 | 0.015 | 0.345 | 0.11 (0.09) | 0 | 1.00 / 0.85 | 0 | 0 | DET\|IND 0.24, DET\|CONF 0.10, ND\|IND 0.65 |
| uniform(0.10) | M05 | 0.10 | 0.056 | 0.87 | 0.010 | 0.87 | 0.54 (0.28) | 0 | 1.00 / 0.825 | 0 | 0 | DET\|CONF 0.52, DET\|IND 0.335 |
| uniform(0) | M16 | 0 | 0 | 0.030 | 0.010 (0.005) | 0.040 | 0.000 (0.045) | 0.055 | 1.00 / 0.82 | 0 | 0 | ND\|IND 0.905 |
| uniform(0.10) | M16 | 0.10 | 0.058 | 0.875 | 0.025 | 0.875 | 0.185 (0.195) | 0 | 1.00 / 0.825 | 0 | 0 | DET\|IND 0.69, DET\|CONF 0.17 |
| tail_mult(3) | M16 | 0.32 | 0 | 0.035 | **0.975 (0.925)** | 0.975 | 0.645 (0.77) | 0.035 | 1.00 / 0.87 | 0 | 0 | DET\|CONF 0.62, DET\|IND 0.33 |
| tail_mult(2) | M16 | 0.16 | 0 | 0.020 | **0.585 (0.455)** | 0.585 | 0.24 (0.38) | 0.050 | 1.00 / 0.90 | 0 | 0 | ND\|IND 0.38, DET\|IND 0.355, DET\|CONF 0.185 |
| tail_mult(1) | M16 STRESS | 0 | 0 | 0.020 | 0.030 (0.025) | 0.050 | 0.020 (0.065) | 0.070 | 0.995 / 0.83 | 0.005 | 0 | ND\|IND 0.875 |
| core_plus_tail_over | M16 | −0.038 | 0.029 | 0.375 | 0 | 0.375 | 0 (0.01) | 0 | 1.00 / 0.80 | 0 | 0 | ND\|IND 0.625, DET\|IND 0.375 |
| hidden_lottery(10) | M16 | 0.44 | 0 | 0.040 | 0.305 (0.21) | 0.325 | **0.535** (0.85) | 0.065 | **0.86** / 0.885 | 0 | **0.06** | ND\|IND 0.385, DET\|CONF 0.245, ND\|CONF 0.145, NROB 0.15 |
| uniform(−0.10) | M16 | −0.10 | −0.058 | 0 | 0 | 0 | 0 | **0.94** | 1.00 / 0.875 | 0.07 | 0 | ADV\|IND 0.87, ADV\|EXCL 0.07 |
| uniform(−0.05) | M00 | −0.05 | −0.028 | 0.005 | – | 0.005 | 0.01 | 0.44 | 0.98 / 0.94 | 0.41 | 0 | ADV\|EXCL 0.395, ND\|IND 0.535 |
| shrink(0.1) | M16 | 0.47 | 0.018 | 0.15 | 0.77 (0.715) | 0.78 | 0.765 (0.905) | 0.005 | 0.985 / 0.84 | 0 | 0.005 | DET\|CONF 0.635, DET\|NROB 0.09 |

Date-only κ test (nominal 0.025) under the null: 0.095–0.205 across run B null rows (0.105 TRUE, 0.13 STRESS, **0.205 SST**, 0.105 M16, 0.175 M16 STRESS).

θ_PCE by the frozen formula on the first 14 synthetic dates (median over replications): **M00 0.08 (σ0 1.08) → GO; M05 0.21 (σ0 3.07) → NO_GO; M16 0.35–0.36 (σ0 5.2–5.3) → NO_GO.** Planned `SE0_κ` ≈ 0.013–0.014 in every mix (κ is immune to the tail); realised `SE(κ̂_core)` 0.016–0.018 under TRUE dependence, 0.025–0.028 under STRESS (IF4 floor 0.025 binds only under the extreme STRESS setting).

### 4.3 Run C — CR engine null size, M00, 1,600 replications per cell per setting (seeds 1–4 with NEG at 0.05; seeds 11–14 with NEG at 0.025)

| True dependence | T1a (nominal 0.025) | T2 (nominal 0.05) | NEG at 0.05 | NEG at 0.025 (frozen) |
|---|---|---|---|---|
| TRUE (0.05, 0.05, 0.10) | 0.032 | 0.053 | 0.068 | **0.028** |
| SST (0.02, 0.15, 0.10) | 0.031 | 0.051 | 0.061 | **0.022** |
| independence | 0.020 | 0.041 | 0.033 | **0.013** |

Monte-Carlo SE ≈ 0.003–0.004 (pooled 3,200 for T1a and T2). Reading: T2 is at nominal; T1a runs ≈ 1.3× nominal but the T1 union stays ≤ 0.05 in run B (0.015–0.05) because T1b is conservative; NEG at 0.05 over-rejects through negative skew of `y − c` on favourite-bucket NO legs, hence the frozen 0.025.

### 4.4 What the simulation settles

1. **PINM with a declared dependence must not gate core statistics** (4.1: 0.755 vs 0.91; 4.2: 0.73 vs 0.855; M05 0.28 vs 0.54). It is valuable for the rare tail count (T1b 0.975 at 3×, 0.585 at 2×), where the declared dependence barely matters.
2. **No gate on θ**: a payout-concentrated edge (hidden lottery, θ = 0.44) is claimed 0.535 ungated vs 0.30 gated (run B; run A 0.61 vs 0.23).
3. **Two-way CR holds size** where date-only fails (0.095–0.205 at nominal 0.025).
4. **Naive pooled upper bounds under-cover with lottery legs** (0.79–0.91); the retired structured bound under-covered in hidden-lottery geometries (0.86–0.89 here; Astra C1 and run D show a GO-compatible false ERT exclusion of 7.4%) — **retired by D4 repair R1** (§4.5).
5. **With any material lottery share, relevance (0.02) cannot be excluded** (U < ERT = 0 in every tail scenario) and θ_PCE exceeds the 0.10 ceiling → NO_GO. The information axis keeps full power in every mix (T1a 0.865–0.875 at κ ≈ 0.056).
6. **A public-bot-like loss rate is detected**: NEG 0.94 at κ = −0.058 (0.05 level; ≈ 0.9 at the frozen 0.025).

### 4.5 Run D — D4 repair R1 validation (after Astra V2 re-audit @7d95c00), fresh seeds 5000–5014, design seed 424242

Command: `python3 WEATHER_FORWARD_V2_SYNTHETIC_SIM_2026-09-29.py d4`. The **retired** bound is computed with the exact frozen V2@94b5934 contract: λ ∈ [0.05, 1000] log-bisection, μ ∈ [0, 50], 40 iterations, interval-end rule, P* from B = 20,000 PINM draws in 20 chunks of 1,000 with `SeedSequence([20260929, 1])` and the per-draw normal order dates → stations → cells → trades (Astra MP1 closed). The fixed attack design reproduces Astra C1: 120 dates × 35 trades, 48 gamma-activity stations, C = 50, core c ~ U(0.35, 0.80), 84 tail legs at 0.039 (9 inside the 14 OP dates) and 2 legs at 0.001 after the OP, q = min(0.999, c + 0.12), true latent dependence (0.05, 0.05, 0.10). Outcome-free readiness of that design: σ0² = 1.326, SE0_θ = 0.0309, **θ_PCE = 0.08**, SE0_κ = 0.01296, 46 stations, Kish 26.2 → **GO** (identical to Astra's figures to the third decimal). `M_tail = 0.9685`.

| Scenario | Reps | θ_true | Retired: coverage | Retired: false U<θ_ERT | Retired: false U<θ_PCE | Retired rule 17.6: false economic rejection | **Repaired: coverage** | **Repaired: false exclusion (ERT / PCE)** | **Repaired: false economic rejection** | T2 | NEG | T1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 positive tail / negative core (Astra C1) | 8,000 | **0.0315** | 0.8885 | **0.0742** (Astra 0.0746) | 0.4119 (θ_true < PCE: not false) | **0.3204** | **1.000** | **0 / 0** | **0** | 0.001 | 0.322 | 0.032 |
| A2 pure hidden lottery (Astra C1 §6.3) | 5,000 | **0.0852** | 0.8632 (Astra 0.8682) | 0.0082 | **0.1126** (Astra 0.1120) | 0.0292 | **1.000** | **0 / 0** | **0** | 0.032 | 0.026 | 0.056 |
| P3 cost check: negative core, fair tail, same design | 2,000 | −0.0980 | 0.9985 | (true exclusion) 0.3815 | 0.7975 | (true) 0.829 | 1.000 | exclusion power **0.000** | 0 | 0 | 0.842 | 0.019 |

Adversarial CORE class for the repaired bound (random designs per replication; θ_true set at or just above θ_ERT so every exclusion is false):

| Geometry | Dependence | Reps | θ_true | θ_PCE (median) | Coverage | False U < θ_ERT | T2 |
|---|---|---|---|---|---|---|---|
| uniform edge, c ~ U(0.35, 0.80) | TRUE | 4,000 | 0.020 | 0.07 | 0.9782 | 0.0217 | 0.153 |
| uniform edge | STRESS (0.15, 0.15, 0.10) | 4,000 | 0.020 | 0.07 | 0.9705 | 0.0295 | 0.108 |
| uniform edge | SST (0.02, 0.15, 0.10) | 4,000 | 0.020 | 0.07 | 0.9762 | 0.0238 | 0.119 |
| favourite NO legs, c ~ U(0.60, 0.90) (negative skew) | TRUE | 4,000 | 0.020 | 0.05 | 0.9810 | 0.0190 | 0.276 |
| 5% mid legs c ~ U(0.04, 0.35) | TRUE | 4,000 | 0.020 | 0.08 | 0.9745 | 0.0255 | 0.136 |
| 6% boundary legs c ~ U(0.04, 0.06), edge hidden in 10% of them, bulk p = 0.95 c | TRUE | 4,000 | 0.025 | 0.10 | 0.9930 | 0.0052 | 0.030 |
| 6% boundary legs, diffuse edge, bulk p = 0.95 c | TRUE | 4,000 | 0.025 | 0.10 | 0.9705 | 0.0248 | 0.107 |
| minimum geometry 60 dates / 25 stations | TRUE | 4,000 | 0.020 | 0.07 | 0.9748 | 0.0253 | 0.119 |
| minimum geometry 60 dates / 25 stations | SST | 4,000 | 0.020 | 0.07 | 0.9740 | 0.0260 | 0.104 |
| 3 tail legs at 0.039 that **all win**, core −0.05 | TRUE | 4,000 | −0.032 | 0.07 | 0.9730 | (true) 0.3388 | 0.006 |
| tail-free, uniform −0.05 (power) | TRUE | 2,000 | −0.050 | 0.07 | 0.9680 | (true) 0.513 | 0.002 |
| tail-free, uniform −0.10 (power) | TRUE | 2,000 | −0.100 | 0.07 | 0.9730 | (true) 0.926 | 0.000 |

Monte-Carlo SE ≈ 0.003 at 4,000 replications near 0.03. Readings:
1. **Both Astra attacks reproduce** with independent code and fresh seeds, and the retired rule 17.6 is worse than the bound alone: its NEG clause turns a true θ = 0.0315 into "R* rejected as a net strategy" 32% of the time.
2. **The repaired bound cannot false-exclude either attack** (coverage 1.0: `M_tail` = 0.97 exceeds every threshold); the repaired rule 17.6 issues no false economic rejection; T2, NEG (now `R*_CORE_INFORMATION_REJECTED`), T1 and the decomposition are unchanged.
3. **Coverage no longer depends on the tail.** Over the adversarial core class it is 0.9705–0.993 and the false ERT exclusion rate is 0.019–0.0295 (≤ 0.05), including hidden edges at the 0.04 boundary, negatively skewed favourites, the minimum truncated geometry and stress dependence.
4. **Cost:** exclusion power is unchanged for tail-free runs (0.51 / 0.93 at θ = −0.05 / −0.10) and small tails (0.34 with three 0.039 legs that all win), but is **zero whenever sub-cent legs are held** (P3), because the sample cannot price them. Such runs are economically INDETERMINATE for exclusion; information-level falsification (NEG 0.84 in P3) remains.

### 4.6 Run E — D4 repair R2 validation (prospective estimand vs unsampled rare tail arrivals; after Astra D4 recheck @3d18085)

Script: `WEATHER_FORWARD_V2_D4_C2_SIM_2026-09-30.py` (independent of run D; seeds 20260930+). Raw output: `WEATHER_FORWARD_V2_D4_C2_RUN_E_OUTPUT_2026-09-30.jsonl`.

Design per replication (a fresh prospective realisation each time):
- 14 observation-phase dates + 120 window dates, Poisson(35) executed trades per date, 48 gamma(2) stations, C = 50.
- CORE c ~ U(0.35, 0.80) with p = c(1 + θ_core).
- A rare TAIL type at all-in cost c_t with win probability p_t arrives per trade (rate r) or per date ("date": a tail date with probability η, on which every trade is of that type).
- Outcomes follow the latent copula (0.05, 0.05, 0.10).
- θ_P is the exact E[N]/E[C] of the generating process.

"Reach" = GO (OP, spec 10.3) ∧ INFO_SUFFICIENT (IF2–IF5). "Old" = the V2-R1 rule at 24d2342 (E1: U < θ_ERT → NET_VALUE_EXCLUDED → R* rejected). "New" = frozen R2. False exclusion = reach ∧ label ∧ θ_P ≥ threshold. 4,000 replications per row, with 95% MC intervals.

| Scenario | θ_P | E[rare legs in window] | GO | INFO | Old false ERT exclusion (joint) | Old, given reach | Old false LARGE exclusion | **New prospective exclusions / R* rejections** | New CONFIRMED | Realised-window excl. (true for θ_W) | Coverage of θ_W by U_W | R2-A candidate exclusions |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C2-S1 p_t=0.17 core=-0.05 thP=0.025 | 0.025 | 1.86 | 0.804 | 0.603 | 0.0475 [0.0409, 0.0541] | 0.0981 | 0.0000 | **0 / 0** | 0.0010 | 0.0475 (false 0.0000) | 0.9962 | 0 |
| C2 p_t=0.50 core=-0.10 thP=0.025 | 0.025 | 1.05 | 0.887 | 0.603 | 0.1755 [0.1637, 0.1873] | 0.3293 | 0.0000 | **0 / 0** | 0.0000 | 0.1755 (false 0.0000) | 0.9885 | 0 |
| C2 p_t=0.50 core=-0.05 thP=0.025 | 0.025 | 0.63 | 0.930 | 0.598 | 0.1650 [0.1535, 0.1765] | 0.2964 | 0.0000 | **0 / 0** | 0.0010 | 0.1650 (false 0.0000) | 0.9848 | 0 |
| C2 p_t=1.00 core=-0.10 thP=0.025 | 0.025 | 0.53 | 0.942 | 0.596 | 0.3137 [0.2994, 0.3281] | 0.5593 | 0.0000 | **0 / 0** | 0.0000 | 0.3137 (false 0.0000) | 0.9738 | 0 |
| C2 PCE p_t=0.50 core=0 thP=0.10 | 0.1 | 0.84 | 0.906 | 0.623 | 0.0292 [0.0240, 0.0345] | 0.0516 | 0.1468 | **0 / 0** | 0.0245 | 0.0292 (false 0.0000) | 0.9872 | 0 |
| date-clustered jackpot p_t=1 core=-0.10 thP=0.025 | 0.025 | 0.53 | 0.998 | 0.602 | 0.5635 [0.5481, 0.5789] | 0.9384 | 0.0000 | **0 / 0** | 0.0000 | 0.5635 (false 0.0000) | 0.9745 | 0 |
| C2 p_t=1.00 core=-0.10 thP=0.025 (independent replicate seed) | 0.025 | 0.53 | 0.937 | 0.610 | 0.3260 [0.3115, 0.3405] | 0.5704 | 0.0000 | **0 / 0** | 0.0000 | 0.3260 (false 0.0000) | 0.9705 | 0 |
| frequent tail: c_t=0.01 p_t=0.05 core=-0.05 thP=0.025 | 0.025 | 77.78 | 0.270 | 0.637 | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | **0 / 0** | 0.0100 | 0.0000 (false 0.0000) | 1.0000 | 0 |
| Astra C1-like: 84 fair 0.039 legs + rare 0.001 p=0.17, core=-0.05 | 0.025 | 1.86 | 0.806 | 0.636 | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | **0 / 0** | 0.0005 | 0.0000 (false 0.0000) | 1.0000 | 0 |
| tail-free regression core=-0.05 | -0.05 | 0.0 | 1.000 | 0.614 | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | **0 / 0** | 0.0010 | 0.3615 (false 0.0000) | 0.9735 | 0 |
| tail-free regression core=-0.10 | -0.1 | 0.0 | 1.000 | 0.606 | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | **0 / 0** | 0.0000 | 0.5732 (false 0.0000) | 0.9728 | 0 |
| tail-free regression core=+0.02 (ERT boundary) | 0.02 | 0.0 | 1.000 | 0.626 | 0.0213 [0.0168, 0.0257] | 0.0339 | 0.0000 | **0 / 0** | 0.1108 | 0.0213 (false 0.0213) | 0.9740 | 0 |
| tail-free core=+0.10 (confirmation power) | 0.1 | 0.0 | 1.000 | 0.666 | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0015 | **0 / 0** | 0.6242 | 0.0000 (false 0.0000) | 0.9770 | 0 |

Tail-free rows: the "old false" columns are false only where θ_P ≥ θ_ERT (the +0.02 row). In the negative rows the realised-window exclusion is a true statement about θ_W.

Old rule by observed count of rare 0.001 legs (p_t = 1, θ_core = −0.10; ungated label frequency; 4,000 replications per λ):

| E[rare legs] | θ_P | observed 0 | 1 | 2 | 5 | ≥ 10 | New prospective exclusions (all counts) |
|---|---|---|---|---|---|---|---|
| 0.5 | 0.0189 | 0.930 (n=2426) | 0.000 (n=1223) | 0.000 (n=294) | — | — | 0 |
| 2.0 | 0.3758 | 0.929 (n=575) | 0.000 (n=1099) | 0.000 (n=1017) | 0.000 (n=155) | 0.000 (n=1) | 0 |
| 5.0 | 1.0894 | 0.920 (n=25) | 0.000 (n=150) | 0.000 (n=306) | 0.000 (n=673) | 0.000 (n=139) | 0 |
| 10.0 | 2.2788 | — | 0.000 (n=4) | 0.000 (n=11) | 0.000 (n=143) | 0.000 (n=2151) | 0 |

Prospective confirmation under rare catastrophic dates (every trade loses on a catastrophic date; η = θ_0/(1+θ_0), so θ_P = 0):

| θ_core (θ_0) | η per date | GO | reach | False PROSPECTIVE_VALUE_CONFIRMED (joint) |
|---|---|---|---|---|
| 0.02 | 0.0196 | 1.000 | 0.469 | 0.0378 [0.0318, 0.0437] |
| 0.03 | 0.0291 | 1.000 | 0.397 | 0.0372 [0.0314, 0.0431] |
| 0.05 | 0.0476 | 1.000 | 0.276 | 0.0315 [0.0261, 0.0369] |
| 0.1 | 0.0909 | 1.000 | 0.097 | 0.0177 [0.0137, 0.0218] |

Dangerous-region grid (spec mission §14): c_t ∈ {0.001, 0.002, 0.005, 0.01, 0.02, 0.039} × p_t ∈ {0, implied, 0.05, 0.17, 0.50, 1.00} × θ_core ∈ {−0.15, −0.10, −0.05, 0, +0.02} × target θ_P ∈ {0.02, 0.021, 0.025, 0.05, 0.08, 0.10} × arrival ∈ {per trade, per date}.
- Feasible rare-region cells: the tail type can lift θ_P to the target and E[rare legs] ≤ 30.
- Scale: 1002 cells × 200 replications = 200,400.
- Old rule: false ERT exclusion > 0.05 in 414 cells (max 0.64, date-clustered arrivals); false LARGE exclusion > 0.05 in 206 cells (max 0.60).
- **New rule: 0 prospective exclusions and 0 R* rejections in all 200,400 replications.**
- R2-A candidate: 0 exclusions.
- Realised-window bound: coverage of θ_W ≥ 0.945 and false θ_W exclusion ≤ 0.055 (200 replications per cell, MC SE ≈ 0.016).

Identification ceiling (DERIVED; `... ceiling`): any level-0.05 prospective exclusion test over D = 134 dates has power ≤ 0.0577 (θ_ERT) / 0.0584 (θ = 0.10) at every θ_0 ≥ −1, and ≤ 0.0509 at θ_0 = −0.10 (spec 8.5b).

Readings:
1. **C2 reproduces** with independent code: the V2-R1 rule false-excludes θ_P ≥ θ_ERT whenever rare, high-payoff types are absent from the window. For S1 the joint rate is 0.0475, below Astra's 0.0592 because the OP dates are separate from the window here, and 0.098 given a reachable analysis state. The rate is 0.17 at p_t = 0.5, 0.31 at p_t = 1, 0.56 with date-clustered arrivals, and 0.15 for false LARGE exclusion at θ_P = 0.10.
2. The old rule's failure is entirely the zero-count case: 92–93% exclusion with 0 observed rare legs whatever θ_P was (0.019 to 1.09), 0% with ≥ 1.
3. **R2 issues no prospective exclusion and no R* rejection anywhere.** Its realised-window statements are true for θ_W (coverage ≥ 0.97 in every scenario row).
4. R2-A never excludes, so it would add an assumption and no power.
5. Prospective confirmation remains valid: false confirmation at θ_P = 0 is ≤ 0.0378 under the catastrophic-date alternative, and confirmation power is unchanged (0.62 at θ_P = 0.10 tail-free, jointly with GO ∧ INFO).


## 5. Terminal-state implications at 120 dates (DERIVED + SIMULATED)

| True θ | Core-dominated mix (M00, θ_PCE ≈ 0.08, GO) | 5% lottery (M05, θ_PCE ≈ 0.21, NO_GO) | 16% lottery (M16, θ_PCE ≈ 0.36, NO_GO) |
|---|---|---|---|
| 0.00 | ND\|IND ≈ 0.85–0.92; false CONFIRMED ≈ 0.03–0.06; false NEG ≈ 0.03 (at 0.025) | would not start | would not start |
| 0.02 (= ERT) | PROSPECTIVE_VALUE_CONFIRMED ≈ 0.11–0.18 (analytic 0.18 before gates; run E 0.11); prospective exclusion not identified (R2); REALIZED_WINDOW_RELEVANT_VALUE_EXCLUDED ≈ 0.02 (run E 0.0213); otherwise INDETERMINATE: **unresolved band** | would not start | would not start |
| 0.05 | CONFIRMED ≈ 0.43; information DETECTED ≈ 0.39; INDETERMINATE ≈ 0.55 | (if run: CONFIRMED 0.10, DET 0.345) | (if run: CONFIRMED ≈ 0.01) |
| 0.10 | CONFIRMED ≈ 0.86; information DETECTED ≈ 0.87 | (if run: CONFIRMED 0.52) | (if run: CONFIRMED 0.17, DET 0.875) |
| −0.05 / −0.10 | NEGATIVE_INFORMATION ≈ 0.44 (−0.05, at 0.05); prospective exclusion not identified (R2); REALIZED_WINDOW exclusion (θ_W) ≈ 0.36–0.51 (−0.05), 0.57–0.93 (−0.10) (run E joint with GO ∧ INFO / run D unconditional) | — | NEGATIVE_INFORMATION ≈ 0.94 (−0.10); realised-window exclusion 0 (tail supremum) |

Label names after D4 repair R2: CONFIRMED = PROSPECTIVE_VALUE_CONFIRMED, INDETERMINATE = PROSPECTIVE_VALUE_INDETERMINATE; no prospective EXCLUDED label exists (spec 8.5b). Runs A–D above used the pre-R2 vocabulary and are kept as historical evidence.

Reading for governance: V2 is a well-powered screen for θ ≳ 0.08–0.10 and for executable mispricing of ≳ 0.035 per share **only if** the post-bias-correction executable mix is core-dominated; otherwise its pre-declared outcome is NO_GO before t0, which is an outcome-free design finding, not a strategy result.
