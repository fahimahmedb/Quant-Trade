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

Prospective confirmation under rare catastrophic dates (every trade loses on a catastrophic date; η = θ_0/(1+θ_0), so θ_P = 0) — **SUPERSEDED as evidence of prospective validity: this date-frequency construction is not the worst case (Astra C3, cost mass; §4.7); kept as history (Astra m9):**

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
5. **SUPERSEDED — R2 reading refuted by Astra C3 (@92c2f706; false confirmation 0.43 / 0.12 under cost-capped loss dates) and replaced by D4 repair R3 (§4.7); no unconditional prospective confirmation exists in V2 (spec 8.5c). Kept as history (Astra m9, D4-C3-M1):** Prospective confirmation remains valid: false confirmation at θ_P = 0 is ≤ 0.0378 under the catastrophic-date alternative, and confirmation power is unchanged (0.62 at θ_P = 0.10 tail-free, jointly with GO ∧ INFO).


### 4.7 Run F — D4 repair R3 validation (prospective confirmation vs unsampled loss regimes; transport frontier; after Astra D4-C2 recheck @92c2f706)

Script: `WEATHER_FORWARD_V2_D4_C3_SIM_2026-09-30.py` (independent of Astra's code; seeds 20261001+). Raw output: `WEATHER_FORWARD_V2_D4_C3_RUN_F_OUTPUT_2026-09-30.jsonl`.

Design per replication (a fresh prospective realisation each time):
- 14 OP + 120 window dates.
- Ordinary dates: Poisson(m) executed trades, 48 gamma(2) stations, CORE c ~ U(0.35, 0.80), p = c(1 + θ_core), capital "full" (50 USD) or "thin" (U(5, 25)).
- Loss-regime dates (probability η, independent): `cap96` (all 96 events at 50 USD, all lose), `template` (48 LOWEST legs), `stations` (both events of 24 stations), `hidden` (ordinary count and fills, all lose: identical observable covariates).
- η is solved so that θ_P, the exact E[N]/E[C] of the process, hits the stated target.

Definitions:
- "R2 false CONFIRMED": the retired @e45d2ce7 label `PROSPECTIVE_VALUE_CONFIRMED` issued while θ_P ≤ 0.
- "R3 false window claim": REALIZED_WINDOW_VALUE_SUPPORTED or NOT_ROBUST issued while θ_W ≤ 0.
- "L_W miss": P(reach ∧ L_W > θ_W), the only way any R3 prospective (conditional) statement can be false.
- "Cond. claim false": `(1 − ε_true) L_W − ε_true > θ_P` at the true loss-regime cost share, with δ = 0.

**Astra C3 reproduction (20,000 replications each):**

| Cell | θ_P | true adverse cost share ε | R2 false CONFIRMED (joint, 95% MC) | R2 forward signal | R3 false window claim | L_W miss | Cond. claim false | ε*(0,0) median when SUPPORTED | k*(120) median | cap-date flag would fire |
|---|---|---|---|---|---|---|---|---|---|---|
| C3-thin: cap96, m=17, thin, core 0.10, thP=-0.005 | -0.005 | 0.0955 | 0.4334 [0.4265, 0.4403] | 0.4334 | 0.0000 | 0.0265 [0.0243, 0.0287] | 0.0265 | 0.0442 | 0.2813 | 1.00 |
| C3-full: cap96, m=17, full, core 0.05, thP=-0.005 | -0.005 | 0.0524 | 0.1175 [0.1130, 0.1220] | 0.1175 | 0.0000 | 0.0172 [0.0154, 0.0189] | 0.0172 | 0.0229 | 0.4734 | 1.00 |

**Mission scenario set (4,000 replications each):**

| Scenario | θ_P | ε_true | E[loss dates in window] | reach | R2 CONFIRMED (false if θ_P ≤ 0) | R3 window claim (SUPPORTED + NOT_ROBUST) | R3 false window claim | L_W miss | unconditional / prospective-exclusion labels | ε*(0,0) median | k*(120) median | cap ratio C_CAP_DATE/C̄_d | ε_1(120) | cap-date flag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 C2 regression: rare 0.001 tail p=0.17, core -0.05, thP=0.025, no loss regime | 0.025 | 0.0 | 0.0 | 0.498 | 0.0010 | 0.0018 | 0.0005 | 0.0055 [0.0032, 0.0078] | 0 / 0 | 0.0097 | 0.4103 | 2.88 | 0.0236 | 0.00 |
| 02 C3 thin fills: cap96 loss dates, m=17, core 0.10, thP=-0.005 | -0.005 | 0.0955 | 0.67 | 0.511 | 0.4338 (false) | 0.4338 | 0.0000 | 0.0258 [0.0208, 0.0307] | 0 / 0 | 0.0451 | 0.2876 | 18.9168 | 0.1372 | 1.00 |
| 03 C3 full fills: cap96 loss dates, m=17, core 0.05, thP=-0.005 | -0.005 | 0.0524 | 1.16 | 0.298 | 0.1143 (false) | 0.1143 | 0.0000 | 0.0155 [0.0117, 0.0193] | 0 / 0 | 0.0214 | 0.4395 | 5.6976 | 0.0457 | 1.00 |
| 04 thP=0 exactly: cap96, m=35, thin, core 0.08 | 0.0 | 0.0741 | 1.04 | 0.244 | 0.1850 (false) | 0.1850 | 0.0000 | 0.0160 [0.0121, 0.0199] | 0 / 0 | 0.0347 | 0.4485 | 9.0197 | 0.0705 | 1.00 |
| 05 strong positive stable: core 0.10, m=35, full, no loss regime | 0.1 | 0.0 | 0.0 | 0.664 | 0.6210 | 0.6210 | 0.0000 | 0.0470 [0.0404, 0.0536] | 0 / 0 | 0.0511 | 2.2134 | 2.8779 | 0.0236 | 0.00 |
| 06 hidden catastrophe (identical covariates), m=17, full, core 0.04, thP=-0.005 | -0.005 | 0.0433 | 5.19 | 0.897 | 0.0455 (false) | 0.0455 | 0.0070 | 0.0290 [0.0238, 0.0342] | 0 / 0 | 0.011 | 0.2216 | 5.9294 | 0.0475 | 0.00 |
| 07 high date concentration: cap96, m=17, thin, core 0.05, thP=-0.005 | -0.005 | 0.0524 | 0.35 | 0.684 | 0.2590 (false) | 0.2590 | 0.0000 | 0.0392 [0.0332, 0.0453] | 0 / 0 | 0.0226 | 0.1426 | 19.5132 | 0.1409 | 1.00 |
| 08 low date concentration: cap96, m=35, full, core 0.03, thP=-0.005 | -0.005 | 0.034 | 1.52 | 0.150 | 0.0387 (false) | 0.0387 | 0.0000 | 0.0110 [0.0078, 0.0142] | 0 / 0 | 0.0199 | 0.8562 | 2.8212 | 0.0232 | 1.00 |
| 09 template-comonotone (48 LOWEST), m=17, full, core 0.04, thP=-0.005 | -0.005 | 0.0433 | 1.89 | 0.504 | 0.0600 (false) | 0.0600 | 0.0005 | 0.0180 [0.0139, 0.0221] | 0 / 0 | 0.0174 | 0.358 | 5.7682 | 0.0462 | 1.00 |
| 10 station-cluster (24 stations x 2), m=17, full, core 0.04, thP=-0.005 | -0.005 | 0.0433 | 1.89 | 0.496 | 0.0597 (false) | 0.0597 | 0.0010 | 0.0142 [0.0106, 0.0179] | 0 / 0 | 0.0139 | 0.2859 | 5.771 | 0.0463 | 1.00 |
| 11 frequent loss regime (E=10 in window): cap96, m=35, full, thP=0 | 0.0 | 0.1996 | 10.0 | 0.000 | 0.0000 (false) | 0.0000 | 0.0000 | 0.0000 [0.0000, 0.0000] | 0 / 0 | None | None | 2.5174 | 0.0207 | 1.00 |
| 12 tail-free stable baseline, core 0.00 (thP=0) | 0.0 | 0.0 | 0.0 | 0.617 | 0.0398 (false) | 0.0398 | 0.0398 | 0.0398 [0.0337, 0.0458] | 0 / 0 | 0.0109 | 0.4607 | 2.8793 | 0.0236 | 0.00 |
| 13 tail-free stable baseline, core 0.10, m=17, thin (confirmation power, thin) | 0.1 | 0.0 | 0.0 | 0.992 | 0.8303 | 0.8303 | 0.0000 | 0.0538 [0.0468, 0.0607] | 0 / 0 | 0.0447 | 0.2827 | 19.7693 | 0.1425 | 0.00 |

**By observed loss dates in the window** (scenario 03, C3 full fills, R2 CONFIRMED rate / R3 false window claim):
0 dates: n = 1201, R2 0.3797, R3 0.0 · 1 dates: n = 1482, R2 0.0007, R3 0.0 · 2 dates: n = 866, R2 0.0, R3 0.0 · 3 dates: n = 322, R2 0.0, R3 0.0 · 4 dates: n = 103, R2 0.0, R3 0.0 · 5 dates: n = 19, R2 0.0, R3 0.0 · 6 dates: n = 6, R2 0.0, R3 0.0 · 9 dates: n = 1, R2 0.0, R3 0.0

**Source-bound sampling coverage (20,000 replications each; nominal one-sided 0.95):**

| Design | P(reach ∧ L_W > θ_W) (95% MC) |
|---|---|
| 05 strong positive stable: core 0.10, m=35, full, no loss regime | 0.0498 [0.0468, 0.0529] |
| 12 tail-free stable baseline, core 0.00 (thP=0) | 0.0440 [0.0412, 0.0468] |
| 13 tail-free stable baseline, core 0.10, m=17, thin (confirmation power, thin) | 0.0552 [0.0520, 0.0584] |

**Loss-regime grid:**
- Axes: E[loss dates in window] ∈ {0.25, 1, 2, 5, 10} × kind ∈ {cap96, template, stations, hidden} × (m, fills) ∈ {17, 35} × {thin, full} × θ_P ∈ {−0.005, 0, θ_ERT, 0.08}. Cells whose ordinary effect would exceed 0.5 are skipped.
- Scale: 291 cells × 1,000 replications = 291,000.
- **R2 false CONFIRMED** at θ_P ≤ 0: above 0.05 in 55 of 148 cells, with the whole MC interval above 0.05 in 38. Maximum 0.36 (E = 1 cap96 loss date, m = 17, thin fills).
- R2 false CONFIRMED by kind: cap96 0.36, template 0.26, stations 0.26, hidden 0.057.
- **R3: 0 unconditional prospective labels and 0 prospective exclusions** in all 291,000 replications.
- R3 false window claims ≤ 0.043; L_W miss ≤ 0.061 (MC SE ≈ 0.007 at 1,000 replications; the largest cells are sparse m = 17 designs, see the coverage table).
- The outcome-blind `COST_EXCEEDS_EVIDENCE` flag would fire for a future loss date in 100% of cap96, ≈ 75% of template / stations and 0% of hidden designs.

**Frontier algebra** (`frontier` mode):
- `L_T(ε, δ)` is decreasing in ε for every tested L_W ∈ {−0.5, −0.05, 0, 0.03, 0.10, 0.30} and δ in the grid, with `L_T(0) = L_W − δ` and `L_T(1) = −1`.
- ε*(0, 0) = 0.0909 at L_W = 0.10 (the sanity example) and 0 when L_W ≤ 0.
- One maximum-exposure date carries cost mass ε_1(120) = 0.142 (17 × 15 USD dates), 0.048 (17 × 50) and 0.024 (35 × 50). At H = 14 the figures are 0.60 / 0.31 / 0.18.

Readings:
1. **C3 reproduces** with independent code. The retired `PROSPECTIVE_VALUE_CONFIRMED` was false at θ_P = −0.005 in 43% (thin) and 11–12% (full) of runs, and in up to 36% of grid cells. The forward signal fired at the same rates.
2. **R3 issues no unconditional prospective label.** Its economic labels are true statements about θ_W: false-claim rate ≤ α (in the run-F designs, which have no cross-block persistence; re-qualified by D4-C3-M1, §4.8).
3. Every prospective statement R3 makes is conditional on the transport premise and can be false only through the sampling miss of L_W. In C3 designs the frontier ε* lies *below* the true adverse cost share, so the conditional claim correctly does not cover the loss regime. k*(120) medians of 0.14–0.86 show the evidence cannot absorb even one maximum-exposure loss date per 120-date epoch.
4. **SUPERSEDED by D4-C3-M1 (Astra M1 @5bb57eb2; §4.8): this reading holds only without cross-block date persistence; under the spec-§9 persistence mechanism the R3 bound's joint miss reached 0.08–0.12. Kept as history:** The source bound's sampling coverage is nominal in thick designs (0.9502) and ≈ 0.5 pp liberal in sparse, heterogeneous-fill designs (0.9448). This is the carried D8 finite-cluster property of the unchanged T2 engine, disclosed as a MINOR limitation.
5. Hidden loss regimes with identical covariates trip no observable flag. Only the ε budget covers them.


### 4.8 Run G — D4-C3-M1 source-bound calibration (L_W under cross-block date persistence; after Astra D4-C3 recheck @5bb57eb2)

Script: `WEATHER_FORWARD_V2_D4_C3_LW_CAL_SIM_2026-10-01.py` (fresh code, independent of Astra's `astra_lw.py` and of run F; seeds `SeedSequence([20261017, cell_id])`, re-runs `[20261017, cell_id, 1..4]`). Raw output: `WEATHER_FORWARD_V2_D4_C3_M1_RUN_G_OUTPUT_2026-10-01.jsonl`. It is the concatenation, in this order, of the stdout of:
- `class 20000`
- `boundary 20000`
- `stress 20000`
- `c3 20000`
- `repro 20000`
- `power 20000`
- `cell 1037 100000`, `cell 1076 100000`, `cell 1073 100000`

Each mode re-runs byte-identically.

Design per replication:
- 14 OP + D window dates. Gamma(2) station activity. Poisson(m) trades per date, capped at 2S.
- CORE prices c ~ U(0.35, 0.80) with p = c(1 + θ). Fills thin (C ~ U(5, 25)) or full (C = 50).
- Outcomes from V2's latent copula (date, station, cell) = (0.05, 0.05, 0.10), plus an optional stationary daily AR(1) date regime with autocorrelation φ and latent variance rv.
- reach = GO (OP, spec 10.3) ∧ INFO_SUFFICIENT (IF2–IF5). θ_W is computed exactly from the true p.
- Joint miss = P(reach ∧ L_W > θ_W). Size = P(reach ∧ T2 ∧ θ̂ ≥ θ_ERT) at θ_W = 0. SUPPORTED additionally requires gates G1–G2; G3 is implied, since every synthetic settlement is NOAA-mode.

Rules, all computed on the same replications:
- **R3 engine**: 5-date blocks; retired for L_W.
- **RM**: blocks {5, 10, 20}; the first candidate, declared before any run.
- **RE**: two-way equally-weighted-cosine HAR estimator with K = max(2, ⌊T ω_h/π⌋) (4 at 120 dates) and a t_K reference; a comparator.
- **adopted**: blocks {5, 10, 20, 30}; spec 8.1b.

Declaration record: the class, the pass criterion and RM were declared before any run. A preliminary RM pass on 45 class cells showed RM failing at φ = 0.9; nothing in RM was changed. Its counts equal, cell for cell, the R3-engine and RM columns of the committed class run (same seeds). RE and the adopted rule were then declared, with the criterion "validity over the whole class first", before their own first run.

**Astra M1 reproduction (R3 engine; 20,000 replications per cell, fresh seeds).**

| Astra cell (φ, latent regime variance, geometry, θ) | Astra @5bb57eb2 | Run G, R3 engine (95% MC) | Run G, adopted rule | reach |
|---|---|---|---|---|
| false REALIZED_WINDOW positive: 0.8, 0.05, m 17 thin, θ_W = 0 | 0.0805 [0.0767, 0.0843] | 0.0789 [0.0752, 0.0826] | 0.0271 [0.0248, 0.0293] | 0.712 |
| L_W miss: 0.8, 0.05, m 17 full, θ = 0.10 | 0.0902 [0.0863, 0.0942] | 0.0889 [0.0850, 0.0928] | 0.0319 [0.0295, 0.0343] | 0.826 |
| L_W miss: 0.8, 0.05, m 17 thin, θ = 0.05 | 0.0828 [0.0790, 0.0867] | 0.0866 [0.0827, 0.0905] | 0.0297 [0.0274, 0.0321] | 0.774 |
| L_W miss: 0.9, 0.10, m 17 thin, θ = 0.05 | 0.0866 [0.0827, 0.0905] | 0.0844 [0.0806, 0.0883] | 0.0382 [0.0355, 0.0408] | 0.322 |
| false positive: 0.9, 0.10, m 17 thin, θ_W = 0 | 0.0761 [0.0724, 0.0797] | 0.0737 [0.0701, 0.0774] | 0.0348 [0.0322, 0.0373] | 0.271 |

**Declared class 𝒟_P (156 cells × 20,000 replications): worst cell per persistence level and rule.** Joint miss = P(reach ∧ L_W > θ_W); size = P(reach ∧ positive REALIZED_WINDOW claim) at θ_W = 0.

| Persistence | cells | R3 engine worst joint miss | RM worst joint miss | RE worst joint miss | **adopted** worst joint miss | R3 engine worst size | **adopted** worst size |
|---|---|---|---|---|---|---|---|
| none (5-date-block model) | 12 | 0.0559 [0.0527, 0.0591] (m 17, full, θ 0.1) | 0.0324 | 0.0256 | 0.0174 [0.0155, 0.0192] (m 17, full, θ 0.1) | 0.0553 [0.0521, 0.0584] | 0.0163 [0.0146, 0.0181] |
| AR φ = 0.5 | 36 | 0.0621 [0.0588, 0.0655] (φ 0.5, rv 0.05, m 17, full, θ 0.1) | 0.0387 | 0.0331 | 0.0237 [0.0216, 0.0258] (φ 0.5, rv 0.05, m 17, thin, θ 0.05) | 0.0587 [0.0555, 0.0620] | 0.0219 [0.0198, 0.0239] |
| AR φ = 0.7 | 36 | 0.0735 [0.0699, 0.0771] (φ 0.7, rv 0.05, m 17, full, θ 0.1) | 0.0412 | 0.0372 | 0.0284 [0.0261, 0.0307] (φ 0.7, rv 0.1, m 17, full, θ 0.1) | 0.0680 [0.0646, 0.0715] | 0.0233 [0.0213, 0.0254] |
| AR φ = 0.8 | 36 | 0.0889 [0.0850, 0.0928] (φ 0.8, rv 0.05, m 17, full, θ 0.1) | 0.0477 | 0.0396 | 0.0319 [0.0295, 0.0343] (φ 0.8, rv 0.05, m 17, full, θ 0.1) | 0.0807 [0.0769, 0.0845] | 0.0293 [0.0270, 0.0316] |
| AR φ = 0.9 | 36 | 0.1287 [0.1241, 0.1333] (φ 0.9, rv 0.05, m 17, full, θ 0.1) | 0.0711 | 0.0574 | 0.0465 [0.0436, 0.0494] (φ 0.9, rv 0.05, m 17, thin, θ 0.1) | 0.1195 [0.1150, 0.1240] | 0.0423 [0.0395, 0.0451] |

**Per-cell listing: no-persistence baseline and φ = 0.9 (all 156 cells are in the raw output).**

| id | Cell | reach | R3 engine | RM | RE | adopted (95% MC) | adopted, given reach |
|---|---|---|---|---|---|---|---|
| 1000 | m 17, thin, θ 0.0 | 0.978 | 0.0524 | 0.0283 | 0.0213 | 0.0144 [0.0128, 0.0161] | 0.015 |
| 1010 | φ 0.9, rv 0.02, m 17, thin, θ 0.0 | 0.919 | 0.0960 | 0.0542 | 0.0418 | 0.0331 [0.0306, 0.0356] | 0.036 |
| 1011 | φ 0.9, rv 0.05, m 17, thin, θ 0.0 | 0.672 | 0.1099 | 0.0624 | 0.0507 | 0.0420 [0.0392, 0.0448] | 0.063 |
| 1012 | φ 0.9, rv 0.1, m 17, thin, θ 0.0 | 0.271 | 0.0737 | 0.0466 | 0.0406 | 0.0348 [0.0322, 0.0373] | 0.128 |
| 1013 | m 17, thin, θ 0.05 | 0.985 | 0.0528 | 0.0303 | 0.0238 | 0.0149 [0.0132, 0.0165] | 0.015 |
| 1023 | φ 0.9, rv 0.02, m 17, thin, θ 0.05 | 0.940 | 0.0989 | 0.0539 | 0.0405 | 0.0330 [0.0305, 0.0355] | 0.035 |
| 1024 | φ 0.9, rv 0.05, m 17, thin, θ 0.05 | 0.729 | 0.1209 | 0.0666 | 0.0508 | 0.0433 [0.0405, 0.0462] | 0.059 |
| 1025 | φ 0.9, rv 0.1, m 17, thin, θ 0.05 | 0.322 | 0.0844 | 0.0512 | 0.0445 | 0.0382 [0.0355, 0.0408] | 0.118 |
| 1026 | m 17, thin, θ 0.1 | 0.989 | 0.0541 | 0.0307 | 0.0249 | 0.0168 [0.0150, 0.0185] | 0.017 |
| 1036 | φ 0.9, rv 0.02, m 17, thin, θ 0.1 | 0.960 | 0.1043 | 0.0592 | 0.0459 | 0.0357 [0.0332, 0.0383] | 0.037 |
| 1037 | φ 0.9, rv 0.05, m 17, thin, θ 0.1 | 0.785 | 0.1241 | 0.0702 | 0.0547 | 0.0465 [0.0436, 0.0494] | 0.059 |
| 1038 | φ 0.9, rv 0.1, m 17, thin, θ 0.1 | 0.377 | 0.0959 | 0.0599 | 0.0496 | 0.0413 [0.0385, 0.0440] | 0.109 |
| 1039 | m 17, full, θ 0.0 | 0.981 | 0.0553 | 0.0324 | 0.0236 | 0.0163 [0.0146, 0.0181] | 0.017 |
| 1049 | φ 0.9, rv 0.02, m 17, full, θ 0.0 | 0.917 | 0.0998 | 0.0563 | 0.0428 | 0.0350 [0.0325, 0.0376] | 0.038 |
| 1050 | φ 0.9, rv 0.05, m 17, full, θ 0.0 | 0.676 | 0.1195 | 0.0648 | 0.0515 | 0.0423 [0.0395, 0.0451] | 0.063 |
| 1051 | φ 0.9, rv 0.1, m 17, full, θ 0.0 | 0.269 | 0.0757 | 0.0510 | 0.0435 | 0.0367 [0.0341, 0.0393] | 0.136 |
| 1052 | m 17, full, θ 0.05 | 0.986 | 0.0528 | 0.0316 | 0.0237 | 0.0159 [0.0142, 0.0176] | 0.016 |
| 1062 | φ 0.9, rv 0.02, m 17, full, θ 0.05 | 0.942 | 0.1048 | 0.0569 | 0.0439 | 0.0338 [0.0313, 0.0364] | 0.036 |
| 1063 | φ 0.9, rv 0.05, m 17, full, θ 0.05 | 0.730 | 0.1227 | 0.0684 | 0.0527 | 0.0449 [0.0421, 0.0478] | 0.062 |
| 1064 | φ 0.9, rv 0.1, m 17, full, θ 0.05 | 0.317 | 0.0835 | 0.0524 | 0.0445 | 0.0384 [0.0358, 0.0411] | 0.121 |
| 1065 | m 17, full, θ 0.1 | 0.991 | 0.0559 | 0.0319 | 0.0256 | 0.0174 [0.0155, 0.0192] | 0.018 |
| 1075 | φ 0.9, rv 0.02, m 17, full, θ 0.1 | 0.959 | 0.1075 | 0.0590 | 0.0461 | 0.0379 [0.0352, 0.0405] | 0.039 |
| 1076 | φ 0.9, rv 0.05, m 17, full, θ 0.1 | 0.786 | 0.1287 | 0.0711 | 0.0574 | 0.0461 [0.0432, 0.0490] | 0.059 |
| 1077 | φ 0.9, rv 0.1, m 17, full, θ 0.1 | 0.375 | 0.0979 | 0.0612 | 0.0532 | 0.0447 [0.0418, 0.0476] | 0.119 |
| 1078 | m 35, thin, θ 0.0 | 0.622 | 0.0439 | 0.0278 | 0.0206 | 0.0152 [0.0135, 0.0168] | 0.024 |
| 1088 | φ 0.9, rv 0.02, m 35, thin, θ 0.0 | 0.267 | 0.0435 | 0.0291 | 0.0239 | 0.0204 [0.0184, 0.0223] | 0.076 |
| 1089 | φ 0.9, rv 0.05, m 35, thin, θ 0.0 | 0.055 | 0.0135 | 0.0099 | 0.0091 | 0.0077 [0.0065, 0.0090] | 0.140 |
| 1090 | φ 0.9, rv 0.1, m 35, thin, θ 0.0 | 0.005 | 0.0021 | 0.0018 | 0.0018 | 0.0016 [0.0011, 0.0022] | 0.355 |
| 1091 | m 35, thin, θ 0.05 | 0.645 | 0.0449 | 0.0278 | 0.0204 | 0.0159 [0.0142, 0.0177] | 0.025 |
| 1101 | φ 0.9, rv 0.02, m 35, thin, θ 0.05 | 0.294 | 0.0459 | 0.0291 | 0.0232 | 0.0200 [0.0181, 0.0220] | 0.068 |
| 1102 | φ 0.9, rv 0.05, m 35, thin, θ 0.05 | 0.066 | 0.0179 | 0.0132 | 0.0114 | 0.0101 [0.0087, 0.0115] | 0.154 |
| 1103 | φ 0.9, rv 0.1, m 35, thin, θ 0.05 | 0.005 | 0.0020 | 0.0017 | 0.0016 | 0.0015 [0.0010, 0.0021] | 0.287 |
| 1104 | m 35, thin, θ 0.1 | 0.672 | 0.0418 | 0.0269 | 0.0209 | 0.0149 [0.0133, 0.0166] | 0.022 |
| 1114 | φ 0.9, rv 0.02, m 35, thin, θ 0.1 | 0.329 | 0.0512 | 0.0324 | 0.0250 | 0.0217 [0.0197, 0.0238] | 0.066 |
| 1115 | φ 0.9, rv 0.05, m 35, thin, θ 0.1 | 0.078 | 0.0221 | 0.0158 | 0.0138 | 0.0119 [0.0104, 0.0134] | 0.153 |
| 1116 | φ 0.9, rv 0.1, m 35, thin, θ 0.1 | 0.008 | 0.0027 | 0.0024 | 0.0024 | 0.0022 [0.0016, 0.0029] | 0.290 |
| 1117 | m 35, full, θ 0.0 | 0.623 | 0.0464 | 0.0290 | 0.0210 | 0.0157 [0.0140, 0.0174] | 0.025 |
| 1127 | φ 0.9, rv 0.02, m 35, full, θ 0.0 | 0.269 | 0.0445 | 0.0288 | 0.0231 | 0.0190 [0.0171, 0.0209] | 0.071 |
| 1128 | φ 0.9, rv 0.05, m 35, full, θ 0.0 | 0.056 | 0.0134 | 0.0095 | 0.0083 | 0.0073 [0.0062, 0.0085] | 0.131 |
| 1129 | φ 0.9, rv 0.1, m 35, full, θ 0.0 | 0.004 | 0.0010 | 0.0008 | 0.0008 | 0.0007 [0.0003, 0.0011] | 0.192 |
| 1130 | m 35, full, θ 0.05 | 0.641 | 0.0455 | 0.0290 | 0.0227 | 0.0165 [0.0147, 0.0183] | 0.026 |
| 1140 | φ 0.9, rv 0.02, m 35, full, θ 0.05 | 0.293 | 0.0480 | 0.0318 | 0.0250 | 0.0217 [0.0197, 0.0237] | 0.074 |
| 1141 | φ 0.9, rv 0.05, m 35, full, θ 0.05 | 0.065 | 0.0173 | 0.0125 | 0.0110 | 0.0100 [0.0086, 0.0114] | 0.153 |
| 1142 | φ 0.9, rv 0.1, m 35, full, θ 0.05 | 0.005 | 0.0022 | 0.0019 | 0.0019 | 0.0016 [0.0010, 0.0022] | 0.302 |
| 1143 | m 35, full, θ 0.1 | 0.673 | 0.0476 | 0.0292 | 0.0223 | 0.0163 [0.0146, 0.0181] | 0.024 |
| 1153 | φ 0.9, rv 0.02, m 35, full, θ 0.1 | 0.323 | 0.0517 | 0.0323 | 0.0251 | 0.0220 [0.0200, 0.0240] | 0.068 |
| 1154 | φ 0.9, rv 0.05, m 35, full, θ 0.1 | 0.074 | 0.0204 | 0.0138 | 0.0116 | 0.0101 [0.0087, 0.0115] | 0.137 |
| 1155 | φ 0.9, rv 0.1, m 35, full, θ 0.1 | 0.007 | 0.0026 | 0.0020 | 0.0019 | 0.0019 [0.0013, 0.0025] | 0.259 |

**Independent re-runs at 100,000 replications (four streams of 25,000; seeds [20261017, id, 1..4]).**

| id | Cell | R3 engine joint miss | RM joint miss | RE joint miss | **adopted** joint miss |
|---|---|---|---|---|---|
| 1037 | φ 0.9, rv 0.05, m 17, thin, θ 0.1 | 0.1273 [0.1253, 0.1294] | 0.0703 [0.0687, 0.0718] | 0.0556 [0.0542, 0.0570] | 0.0458 [0.0445, 0.0471] |
| 1076 | φ 0.9, rv 0.05, m 17, full, θ 0.1 | 0.1282 [0.1262, 0.1303] | 0.0708 [0.0692, 0.0724] | 0.0557 [0.0542, 0.0571] | 0.0464 [0.0451, 0.0477] |
| 1073 | φ 0.8, rv 0.05, m 17, full, θ 0.1 | 0.0877 [0.0860, 0.0895] | 0.0474 [0.0461, 0.0487] | 0.0399 [0.0386, 0.0411] | 0.0302 [0.0292, 0.0313] |

**Boundary designs (20,000 replications each).**

| id | Cell | reach | R3 engine | RM | RE | adopted (95% MC) | SUPPORTED: R3 engine / adopted |
|---|---|---|---|---|---|---|---|
| 2000 | min geometry 60/25 m=17 thin th=0.0 no persistence | 0.165 | 0.0132 | 0.0019 | 0.0019 | 0.0000 [0.0000, 0.0000] | 0.0132 / 0.0000 |
| 2001 | min geometry 60/25 m=17 thin th=0.0 AR phi=0.8 rv=0.05 | 0.046 | 0.0104 | 0.0040 | 0.0035 | 0.0000 [0.0000, 0.0000] | 0.0104 / 0.0000 |
| 2002 | min geometry 60/25 m=17 thin th=0.0 AR phi=0.9 rv=0.1 | 0.019 | 0.0082 | 0.0047 | 0.0047 | 0.0008 [0.0004, 0.0012] | 0.0082 / 0.0008 |
| 2003 | min geometry 60/25 m=17 thin th=0.1 no persistence | 0.202 | 0.0143 | 0.0021 | 0.0021 | 0.0000 [0.0000, 0.0000] | 0.1429 / 0.0013 |
| 2004 | min geometry 60/25 m=17 thin th=0.1 AR phi=0.8 rv=0.05 | 0.075 | 0.0164 | 0.0053 | 0.0052 | 0.0002 [0.0000, 0.0004] | 0.0529 / 0.0032 |
| 2005 | min geometry 60/25 m=17 thin th=0.1 AR phi=0.9 rv=0.1 | 0.034 | 0.0163 | 0.0103 | 0.0098 | 0.0016 [0.0010, 0.0022] | 0.0253 / 0.0063 |
| 2006 | min geometry 60/25 m=35 full th=0.0 no persistence | 0.440 | 0.0318 | 0.0065 | 0.0057 | 0.0000 [0.0000, 0.0000] | 0.0318 / 0.0000 |
| 2007 | min geometry 60/25 m=35 full th=0.0 AR phi=0.8 rv=0.05 | 0.117 | 0.0243 | 0.0077 | 0.0069 | 0.0004 [0.0001, 0.0007] | 0.0243 / 0.0004 |
| 2008 | min geometry 60/25 m=35 full th=0.0 AR phi=0.9 rv=0.1 | 0.037 | 0.0135 | 0.0086 | 0.0081 | 0.0017 [0.0011, 0.0023] | 0.0135 / 0.0017 |
| 2009 | min geometry 60/25 m=35 full th=0.1 no persistence | 0.486 | 0.0315 | 0.0057 | 0.0055 | 0.0001 [0.0000, 0.0001] | 0.3656 / 0.0053 |
| 2010 | min geometry 60/25 m=35 full th=0.1 AR phi=0.8 rv=0.05 | 0.155 | 0.0286 | 0.0118 | 0.0111 | 0.0008 [0.0004, 0.0011] | 0.1057 / 0.0103 |
| 2011 | min geometry 60/25 m=35 full th=0.1 AR phi=0.9 rv=0.1 | 0.051 | 0.0178 | 0.0107 | 0.0102 | 0.0024 [0.0017, 0.0031] | 0.0347 / 0.0086 |
| 2012 | dominant station 20% m=17 thin th=0.0 no persistence | 0.484 | 0.0384 | 0.0239 | 0.0186 | 0.0132 [0.0117, 0.0148] | 0.0105 / 0.0040 |
| 2013 | dominant station 20% m=17 thin th=0.0 AR phi=0.8 rv=0.05 | 0.349 | 0.0450 | 0.0260 | 0.0223 | 0.0171 [0.0153, 0.0189] | 0.0163 / 0.0056 |
| 2014 | dominant station 20% m=17 thin th=0.0 AR phi=0.9 rv=0.1 | 0.150 | 0.0377 | 0.0234 | 0.0204 | 0.0178 [0.0160, 0.0196] | 0.0175 / 0.0083 |
| 2015 | dominant station 20% m=17 thin th=0.1 no persistence | 0.506 | 0.0377 | 0.0236 | 0.0195 | 0.0136 [0.0120, 0.0152] | 0.1868 / 0.1338 |
| 2016 | dominant station 20% m=17 thin th=0.1 AR phi=0.8 rv=0.05 | 0.398 | 0.0488 | 0.0287 | 0.0238 | 0.0179 [0.0161, 0.0197] | 0.1341 / 0.0795 |
| 2017 | dominant station 20% m=17 thin th=0.1 AR phi=0.9 rv=0.1 | 0.190 | 0.0498 | 0.0311 | 0.0263 | 0.0232 [0.0211, 0.0253] | 0.0640 / 0.0390 |
| 2018 | one dominant date (96 trades) m=17 thin th=0.0 no persistence | 0.977 | 0.0542 | 0.0301 | 0.0234 | 0.0158 [0.0140, 0.0175] | 0.0542 / 0.0158 |
| 2019 | one dominant date (96 trades) m=17 thin th=0.0 AR phi=0.8 rv=0.05 | 0.684 | 0.0753 | 0.0420 | 0.0361 | 0.0273 [0.0250, 0.0296] | 0.0753 / 0.0273 |
| 2020 | one dominant date (96 trades) m=17 thin th=0.0 AR phi=0.9 rv=0.1 | 0.257 | 0.0691 | 0.0440 | 0.0365 | 0.0321 [0.0296, 0.0345] | 0.0691 / 0.0321 |
| 2021 | one dominant date (96 trades) m=17 thin th=0.1 no persistence | 0.983 | 0.0566 | 0.0311 | 0.0242 | 0.0164 [0.0146, 0.0182] | 0.8339 / 0.6472 |
| 2022 | one dominant date (96 trades) m=17 thin th=0.1 AR phi=0.8 rv=0.05 | 0.770 | 0.0859 | 0.0469 | 0.0379 | 0.0293 [0.0269, 0.0316] | 0.5536 / 0.3548 |
| 2023 | one dominant date (96 trades) m=17 thin th=0.1 AR phi=0.9 rv=0.1 | 0.326 | 0.0824 | 0.0531 | 0.0440 | 0.0381 [0.0355, 0.0408] | 0.2188 / 0.1477 |
| 2024 | thick m=35 full th=0.0 no persistence | 0.624 | 0.0411 | 0.0246 | 0.0185 | 0.0144 [0.0127, 0.0160] | 0.0411 / 0.0144 |
| 2025 | thick m=35 full th=0.0 AR phi=0.8 rv=0.05 | 0.056 | 0.0096 | 0.0067 | 0.0061 | 0.0050 [0.0040, 0.0060] | 0.0096 / 0.0050 |
| 2026 | thick m=35 full th=0.0 AR phi=0.9 rv=0.1 | 0.005 | 0.0015 | 0.0014 | 0.0013 | 0.0013 [0.0008, 0.0018] | 0.0015 / 0.0013 |
| 2027 | thick m=35 full th=0.1 no persistence | 0.675 | 0.0479 | 0.0300 | 0.0220 | 0.0165 [0.0147, 0.0183] | 0.6345 / 0.5626 |
| 2028 | thick m=35 full th=0.1 AR phi=0.8 rv=0.05 | 0.076 | 0.0155 | 0.0106 | 0.0092 | 0.0082 [0.0069, 0.0095] | 0.0664 / 0.0537 |
| 2029 | thick m=35 full th=0.1 AR phi=0.9 rv=0.1 | 0.007 | 0.0029 | 0.0026 | 0.0024 | 0.0025 [0.0018, 0.0032] | 0.0054 / 0.0049 |
| 2030 | thick m=35 thin th=0.0 no persistence | 0.622 | 0.0435 | 0.0280 | 0.0215 | 0.0152 [0.0135, 0.0168] | 0.0435 / 0.0152 |
| 2031 | thick m=35 thin th=0.0 AR phi=0.8 rv=0.05 | 0.057 | 0.0094 | 0.0065 | 0.0063 | 0.0049 [0.0039, 0.0059] | 0.0094 / 0.0049 |
| 2032 | thick m=35 thin th=0.0 AR phi=0.9 rv=0.1 | 0.005 | 0.0018 | 0.0014 | 0.0014 | 0.0010 [0.0006, 0.0015] | 0.0018 / 0.0010 |
| 2033 | thick m=35 thin th=0.1 no persistence | 0.677 | 0.0464 | 0.0302 | 0.0230 | 0.0167 [0.0149, 0.0184] | 0.6325 / 0.5565 |
| 2034 | thick m=35 thin th=0.1 AR phi=0.8 rv=0.05 | 0.078 | 0.0155 | 0.0104 | 0.0091 | 0.0076 [0.0064, 0.0088] | 0.0673 / 0.0554 |
| 2035 | thick m=35 thin th=0.1 AR phi=0.9 rv=0.1 | 0.007 | 0.0026 | 0.0021 | 0.0020 | 0.0018 [0.0012, 0.0024] | 0.0053 / 0.0047 |

**Outside the declared class (disclosure only; no level claimed; 20,000 replications each; θ_W = 0).**

| id | Cell | reach | R3 engine | RM | RE | adopted (95% MC) |
|---|---|---|---|---|---|---|
| 3000 | AR phi=0.95 rv=0.05 m=17 thin th=0.0 | 0.708 | 0.1636 | 0.1035 | 0.0830 | 0.0717 [0.0682, 0.0753] |
| 3001 | AR phi=0.95 rv=0.05 m=17 full th=0.0 | 0.703 | 0.1728 | 0.1076 | 0.0839 | 0.0721 [0.0685, 0.0757] |
| 3002 | AR phi=0.95 rv=0.05 m=35 full th=0.0 | 0.085 | 0.0278 | 0.0223 | 0.0190 | 0.0171 [0.0154, 0.0190] |
| 3003 | AR phi=0.95 rv=0.1 m=17 thin th=0.0 | 0.354 | 0.1225 | 0.0877 | 0.0741 | 0.0665 [0.0630, 0.0699] |
| 3004 | AR phi=0.95 rv=0.1 m=17 full th=0.0 | 0.347 | 0.1208 | 0.0878 | 0.0764 | 0.0675 [0.0641, 0.0710] |
| 3005 | AR phi=0.95 rv=0.1 m=35 full th=0.0 | 0.011 | 0.0044 | 0.0037 | 0.0036 | 0.0033 [0.0025, 0.0041] |
| 3006 | AR phi=0.97 rv=0.05 m=17 thin th=0.0 | 0.762 | 0.2109 | 0.1474 | 0.1242 | 0.1089 [0.1045, 0.1132] |
| 3007 | AR phi=0.97 rv=0.05 m=17 full th=0.0 | 0.765 | 0.2130 | 0.1506 | 0.1260 | 0.1098 [0.1054, 0.1141] |
| 3008 | AR phi=0.97 rv=0.05 m=35 full th=0.0 | 0.122 | 0.0426 | 0.0348 | 0.0314 | 0.0289 [0.0266, 0.0312] |
| 3009 | AR phi=0.97 rv=0.1 m=17 thin th=0.0 | 0.464 | 0.1745 | 0.1343 | 0.1168 | 0.1072 [0.1030, 0.1115] |
| 3010 | AR phi=0.97 rv=0.1 m=17 full th=0.0 | 0.462 | 0.1718 | 0.1302 | 0.1147 | 0.1048 [0.1006, 0.1091] |
| 3011 | AR phi=0.97 rv=0.1 m=35 full th=0.0 | 0.027 | 0.0120 | 0.0108 | 0.0103 | 0.0100 [0.0086, 0.0114] |
| 3012 | AR phi=0.9 rv=0.2 m=17 thin th=0.0 | 0.030 | 0.0144 | 0.0117 | 0.0106 | 0.0097 [0.0084, 0.0111] |
| 3013 | AR phi=0.9 rv=0.2 m=17 full th=0.0 | 0.029 | 0.0129 | 0.0110 | 0.0099 | 0.0092 [0.0079, 0.0105] |
| 3014 | AR phi=0.9 rv=0.2 m=35 full th=0.0 | 0.000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 [0.0000, 0.0000] |

**Power cost — REALIZED_WINDOW_VALUE_SUPPORTED (joint with reach; gates G1–G2 applied), no persistence.**

| Geometry | θ | R3 engine | RM | RE | **adopted** |
|---|---|---|---|---|---|
| m 17, thin | 0.05 | 0.3789 | 0.2753 | 0.2351 | 0.1868 |
| m 17, thin | 0.1 | 0.8432 | 0.7609 | 0.7156 | 0.6539 |
| m 17, full | 0.05 | 0.3864 | 0.2867 | 0.2414 | 0.1950 |
| m 17, full | 0.1 | 0.8508 | 0.7708 | 0.7229 | 0.6681 |
| m 35, thin | 0.05 | 0.3226 | 0.2562 | 0.2221 | 0.1923 |
| m 35, thin | 0.1 | 0.6291 | 0.5999 | 0.5771 | 0.5538 |
| m 35, full | 0.05 | 0.3226 | 0.2601 | 0.2268 | 0.1950 |
| m 35, full | 0.1 | 0.6331 | 0.6086 | 0.5873 | 0.5649 |

**T2 power at the design's own θ_PCE and at 0.12 / 0.15 (P(L_W > 0), unconditional, the D1 / θ_PCE notion; 20,000 replications each).**

| Cell | θ_PCE (OP median) | P(T2) R3 engine | P(T2) RM | P(T2) RE | P(T2) **adopted** | SUPPORTED joint: R3 engine / adopted |
|---|---|---|---|---|---|---|
| theta_PCE=0.09 m=17 thin no persistence | 0.09 | 0.7790 | 0.6812 | 0.6256 | 0.5540 | 0.7741 / 0.5522 |
| theta=0.12 m=17 thin no persistence | 0.09 | 0.9456 | 0.8982 | 0.8628 | 0.8188 | 0.9399 / 0.8161 |
| theta=0.15 m=17 thin no persistence | 0.09 | 0.9922 | 0.9802 | 0.9684 | 0.9529 | 0.9850 / 0.9474 |
| theta_PCE=0.09 m=17 thin AR phi=0.8 rv=0.05 | 0.09 | 0.6119 | 0.4506 | 0.3969 | 0.3471 | 0.5312 / 0.3181 |
| theta_PCE=0.08 m=17 full no persistence | 0.08 | 0.7015 | 0.5977 | 0.5377 | 0.4759 | 0.6979 / 0.4747 |
| theta=0.12 m=17 full no persistence | 0.08 | 0.9509 | 0.9056 | 0.8758 | 0.8379 | 0.9446 / 0.8345 |
| theta=0.15 m=17 full no persistence | 0.08 | 0.9940 | 0.9847 | 0.9755 | 0.9631 | 0.9874 / 0.9580 |
| theta_PCE=0.08 m=17 full AR phi=0.8 rv=0.05 | 0.08 | 0.5554 | 0.3921 | 0.3412 | 0.2931 | 0.4820 / 0.2697 |
| theta_PCE=0.07 m=35 thin no persistence | 0.07 | 0.6730 | 0.5722 | 0.5110 | 0.4555 | 0.4807 / 0.3421 |
| theta=0.12 m=35 thin no persistence | 0.07 | 0.9696 | 0.9445 | 0.9215 | 0.8958 | 0.6769 / 0.6431 |
| theta=0.15 m=35 thin no persistence | 0.07 | 0.9978 | 0.9940 | 0.9888 | 0.9835 | 0.7129 / 0.7078 |
| theta_PCE=0.07 m=35 thin AR phi=0.8 rv=0.05 | 0.07 | 0.5103 | 0.3468 | 0.2960 | 0.2550 | 0.0466 / 0.0334 |
| theta_PCE=0.07 m=35 full no persistence | 0.07 | 0.6754 | 0.5758 | 0.5142 | 0.4588 | 0.4794 / 0.3469 |
| theta=0.12 m=35 full no persistence | 0.07 | 0.9752 | 0.9529 | 0.9338 | 0.9120 | 0.6874 / 0.6574 |
| theta=0.15 m=35 full no persistence | 0.07 | 0.9980 | 0.9951 | 0.9915 | 0.9877 | 0.7125 / 0.7092 |
| theta_PCE=0.07 m=35 full AR phi=0.8 rv=0.05 | 0.07 | 0.5061 | 0.3452 | 0.2954 | 0.2553 | 0.0452 / 0.0322 |

**Frozen 5-date-block surfaces on the same replications (not repaired; disclosure).**

| Persistence | T1a false rejection, θ = 0 (nominal 0.025) | NEG false rejection (nominal 0.025) | U_W miss (declared 0.05) |
|---|---|---|---|
| none | 0.0293 [0.0270, 0.0316] | 0.0249 [0.0228, 0.0271] | 0.0269 [0.0247, 0.0291] |
| AR φ = 0.5 | 0.0331 [0.0306, 0.0355] | 0.0267 [0.0245, 0.0290] | 0.0286 [0.0263, 0.0309] |
| AR φ = 0.7 | 0.0407 [0.0380, 0.0434] | 0.0340 [0.0314, 0.0365] | 0.0362 [0.0336, 0.0388] |
| AR φ = 0.8 | 0.0532 [0.0501, 0.0563] | 0.0400 [0.0373, 0.0427] | 0.0454 [0.0425, 0.0482] |
| AR φ = 0.9 | 0.0893 [0.0853, 0.0932] | 0.0694 [0.0659, 0.0730] | 0.0765 [0.0728, 0.0801] |

**Astra C3 cells on run F's own loss-date process (20,000 replications each).** Window-positive = SUPPORTED ∪ NOT_ROBUST, a true statement about θ_W in these runs; conditional claim false = `(1 − ε_true) L_W − ε_true > θ_P` with δ = 0.

| Cell | θ_P | ε_true | reach | window-positive R3 engine / adopted | false window claim R3 / adopted | L_W miss R3 / adopted | conditional claim false R3 / adopted |
|---|---|---|---|---|---|---|---|
| C3-thin: cap96, m=17, thin, core 0.10, thP=-0.005 | -0.005 | 0.0955 | 0.503 | 0.4279 / 0.3286 | 0.0000 / 0.0000 | 0.0263 / 0.0080 | 0.0263 / 0.0080 |
| C3-full: cap96, m=17, full, core 0.05, thP=-0.005 | -0.005 | 0.0524 | 0.307 | 0.1206 / 0.0605 | 0.0000 / 0.0000 | 0.0163 / 0.0053 | 0.0163 / 0.0053 |

Readings:
1. **M1 reproduces with independent code.**
   - R3 engine at Astra's cells: false positive 0.0789 and full-fill miss 0.0889 (Astra 0.0805 / 0.0902; every Astra value lies inside the run-G interval).
   - Over the declared class the R3 engine exceeds 0.05 from φ = 0.5, and reaches 0.1287 (joint miss) and 0.1195 (size) at φ = 0.9.
   - Without persistence it is ≈ 0.5 pp liberal (0.0559), as R3 disclosed.
2. **The adopted rule holds 0.05 over the whole declared class 𝒟_P.**
   - Worst cell 0.0465 [0.0436, 0.0494] at 20,000 replications; independent 100,000-replication re-runs give 0.0458 [0.0445, 0.0471] and 0.0464 [0.0451, 0.0477].
   - Worst size 0.0423. It is conservative without persistence (≤ 0.0174).
   - RM and RE pass for φ ≤ 0.8 (RM worst 0.0474 at 100,000) but fail at φ = 0.9: RM 0.0708 [0.0692, 0.0724], RE 0.0557 [0.0542, 0.0571] at 100,000.
3. **Boundary designs: valid everywhere.**
   - Worst 0.0381: one 96-trade date at φ = 0.9.
   - At the information floor (60 dates, 25 stations) the rule is valid but nearly powerless: SUPPORTED 0.001–0.005 at θ = 0.10, because df_30 = 1.
4. **Outside 𝒟_P the miss is higher (coverage lower) and no level is claimed:** up to 0.072 at φ = 0.95 and 0.110 at φ = 0.97 (R3 engine 0.173 / 0.213). At latent variance 0.20, IF5 screens almost every run.
5. **Power cost (disclosed, not retuned).**
   - SUPPORTED at θ = 0.10 falls by 0.07–0.19, most in thin 17-trades/date designs. At θ = 0.05 it falls by 0.13–0.19.
   - P(T2) at the design's own θ_PCE is 0.46–0.55, against 0.67–0.78 for the R3 engine.
   - The 80%-power effect rises from ≈ 0.09–0.10 to ≈ 0.11–0.12.
   - INDETERMINATE becomes more likely.
6. **Conditional on reach, the miss is larger.** IF5 screens high-dispersion windows, not slow drifts. In cells with reach ≥ 0.10 it reaches 0.085 (φ ≤ 0.8) and 0.136 (φ = 0.9), against 0.189 / 0.281 for the R3 engine. The stated level is the repeated-experiment joint rate, as in R3.
7. **Frozen 5-date-block surfaces exceed their nominal levels under persistence:** T1a up to 0.089 at nominal 0.025, NEG 0.069, U_W miss 0.077. They are not repaired (frozen; outside the bounded mission). Spec 17.8 qualifies their stated levels, and the observation is flagged.
8. **C3 regression.** On run F's own process the adopted rule issues the window-positive label (a true statement about θ_W there) in 0.329 / 0.061 of runs (R3 engine 0.428 / 0.121). It never issues a false window claim. The conditional claim is false only through the L_W miss (0.008 / 0.005). Structurally, no unconditional prospective label can be issued, because the vocabulary has none.


### 4.9 Run H — D4-C3-M2 calibration of L_W, U_W, T1a and NEG over the completely stated class 𝒟_P* (after Astra D4-C3-M1 recheck @ac777a87)

**SUPERSEDED IN PART by §4.10 (D4-C3-P1, after Astra @8874dc54): the constants λ_θ = 1.70 / λ_κ = 1.60, the price laws of the class, the levels, and the statement that GO / θ_PCE / SE_KAPPA_CEILING are "not retuned" are the cycle-2 record; §4.10 and spec 8.1d / 10.4 govern.**

Script `WEATHER_FORWARD_V2_D4_C3_M2_CAL_SIM_2026-10-01.py` (fresh code; seeds `SeedSequence([20261101, plan, cell, stream])`; synthetic only). Raw output:
- `WEATHER_FORWARD_V2_D4_C3_M2_RUN_H_OUTPUT_2026-10-01.jsonl`: plans astra 12, class 900, fav35 160, geo 72, outside 20, power 36 and t1b 12 cells, each at 20,000 replications;
- `WEATHER_FORWARD_V2_D4_C3_M2_RUN_H_CONFIRM_100K_2026-10-01.jsonl`: 14 cells at 100,000 replications (streams 1–5).

The class, construction family, λ grid, selection criterion and comparators were declared in the script header before any run (spec 8.1c). Each line stores, for every λ on the grid, the joint counts of:
- L_W miss, false positive, SUPPORTED and T2;
- U_W miss and loss, headline non-coverage;
- T1a / NEG (all and false).

It also stores the comparators and the pre-repair 5-date objects. Re-run check: `astra 20000` and `cell astra 4 100000` reproduce the committed lines byte-for-byte.

**Selection.** λ_θ = 1.70 and λ_κ = 1.60 are the smallest grid values meeting the declared targets (joint L_W miss, size and U_W miss ≤ 0.040; T1a, NEG ≤ 0.020) in all 1,183 reached in-class cells. Eight cells (log-uniform and U(0.04, 0.35) prices) are NO_GO in every run.

**Smallest passing λ by sub-family** (disclosure only; not a selection):

| Sub-family | λ_θ | λ_κ |
|---|---|---|
| none | 1.00 | 1.00 |
| AR φ 0.5 / 0.7 / 0.8 / 0.9 | 1.05 / 1.15 / 1.25 / 1.50 | 1.00 / 1.05 / 1.15 / 1.40 |
| two-state φ 0.8 / 0.9 | 1.15 / 1.50 | 1.10 / 1.50 |
| trailing mean 15 / 30 | 1.35 / 1.70 | 1.30 / 1.60 |
| hemisphere / station φ 0.9 | 1.20 / 1.00 | 1.10 / 1.00 |
| prices U(0.35, 0.80) / mix / favourite | 1.30 / 1.45 / 1.70 | 1.30 / 1.50 / 1.60 |
| run-G-like (U(0.35, 0.80), no pauses, AR only) | 1.10 | 1.00 |

**Worst joint rates at the adopted constants (20,000 per cell).**

| Dependence | L_W miss | size | U_W miss | T1a | NEG | cycle-1 L_W (λ 1) | pre-repair 5-date T1a / NEG / U_W |
|---|---|---|---|---|---|---|---|
| none | 0.0026 | 0.0021 | 0.0002 | 0.0004 | 0.0002 | 0.0360 | 0.0380 / 0.0274 / 0.0290 |
| AR φ 0.5 | 0.0050 | 0.0043 | 0.0003 | 0.0014 | 0.0003 | 0.0459 | 0.0466 / 0.0288 / 0.0301 |
| AR φ 0.7 | 0.0081 | 0.0072 | 0.0006 | 0.0027 | 0.0007 | 0.0537 | 0.0641 / 0.0349 / 0.0361 |
| AR φ 0.8 | 0.0121 | 0.0107 | 0.0009 | 0.0043 | 0.0012 | 0.0655 | 0.0820 / 0.0455 / 0.0471 |
| AR φ 0.9 | 0.0268 | 0.0220 | 0.0028 | 0.0115 | 0.0031 | 0.0954 | 0.1577 / 0.0792 / 0.0814 |
| two-state φ 0.8 | 0.0115 | 0.0095 | 0.0014 | 0.0050 | 0.0018 | 0.0568 | 0.0741 / 0.0498 / 0.0561 |
| two-state φ 0.9 | 0.0279 | 0.0255 | 0.0089 | 0.0163 | 0.0106 | 0.0856 | 0.1187 / 0.0937 / 0.1054 |
| trailing mean 15 | 0.0211 | 0.0155 | 0.0013 | 0.0080 | 0.0014 | 0.0811 | 0.1100 / 0.0593 / 0.0624 |
| trailing mean 30 | 0.0395 | 0.0353 | 0.0044 | 0.0198 | 0.0057 | 0.1176 | 0.1752 / 0.1025 / 0.1077 |
| hemisphere φ 0.9 | 0.0100 | 0.0094 | 0.0007 | 0.0032 | 0.0008 | 0.0612 | 0.1071 / 0.0627 / 0.0641 |
| station φ 0.9 | 0.0008 | 0.0007 | 0.0000 | 0.0001 | 0.0001 | 0.0222 | 0.0354 / 0.0238 / 0.0245 |

By other dimensions (worst L_W miss):
- calendars: P 0 0.0350, 30 random 0.0359, 30 contiguous 0.0395;
- truncated windows: D 90 0.0168, D 60 0.0011;
- m 35: 0.0344 (thin) / 0.0321 (full);
- TAIL mixes: 1% 0.0108, 3% 0.0039.

Comparators at λ = 1 (worst L_W miss / size): blocks {5, …, 40} 0.0968 / 0.0854; quantile 0.975 0.0742 / 0.0658; R3 engine 0.2439. All fail.

**100,000-replication confirmations (95% Wilson).**

| Cell (m 17) | L_W miss | size | U_W miss | T1a | NEG | headline non-coverage | cycle-1 L_W |
|---|---|---|---|---|---|---|---|
| trailing 30, rv 0.10, favourite, 30 contiguous paused, full, θ 0.10 | 0.0415 [0.0403, 0.0427] | — | 0.0014 | — | — | 0.0429 | 0.1219 |
| same, thin | 0.0400 [0.0388, 0.0413] | — | 0.0011 | — | — | 0.0411 | 0.1213 |
| trailing 30, rv 0.10, favourite, 30 random paused, full, θ 0.10 | 0.0352 [0.0341, 0.0364] | — | 0.0008 | — | — | 0.0360 | 0.1117 |
| trailing 30, rv 0.10, favourite, 30 contiguous paused, full, θ 0 | 0.0336 | 0.0336 [0.0325, 0.0347] | 0.0021 | 0.0188 [0.0180, 0.0197] | 0.0027 | 0.0356 | 0.1031 |
| same, thin, θ 0 | 0.0336 | 0.0336 [0.0325, 0.0347] | 0.0018 | 0.0193 [0.0185, 0.0202] | 0.0025 | 0.0354 | 0.1023 |
| trailing 30, rv 0.10, favourite, no pause, full, θ 0 | 0.0297 | 0.0297 | 0.0013 | 0.0148 | 0.0017 | 0.0310 | 0.0943 |
| trailing 30, rv 0.10, favourite, 30 random paused, thin, θ 0 | 0.0292 | 0.0292 | 0.0015 | 0.0165 | 0.0019 | 0.0307 | 0.0965 |
| two-state 0.9, rv 0.10, U(0.35, 0.80), 30 contiguous paused, full, θ 0 | 0.0194 | 0.0194 | 0.0085 [0.0079, 0.0091] | 0.0125 | 0.0100 [0.0095, 0.0107] | 0.0279 | 0.0464 |
| same, thin, θ 0 | 0.0186 | 0.0186 | 0.0082 | 0.0121 | 0.0098 | 0.0268 | 0.0459 |
| same, thin, θ 0.10 | 0.0193 | — | 0.0069 | — | 0.0003 | 0.0263 | 0.0512 |
| two-state 0.9, rv 0.10, no pause, thin, θ 0 | 0.0171 | 0.0171 | 0.0064 | 0.0105 | 0.0079 | 0.0236 | 0.0440 |
| Astra: favourite AR 0.9 rv 0.05 thin θ 0.10 | 0.0114 [0.0108, 0.0121] | — | 0.0001 | — | — | 0.0116 | 0.0639 |
| Astra: same, θ 0 | 0.0100 | 0.0100 [0.0094, 0.0106] | 0.0002 | 0.0036 | 0.0005 | 0.0102 | 0.0595 |
| Astra: 30 random paused, AR 0.9 rv 0.05, θ 0.10 | 0.0069 [0.0064, 0.0074] | — | 0.0010 | — | — | 0.0079 | 0.0534 |

Every confirmation upper bound is inside its requirement (≤ 0.050 for L_W / U_W; ≤ 0.025 for T1a / NEG). Given reach, the rates are larger: in cells with reach ≥ 0.10 the worst are L_W 0.182, size 0.112, U_W 0.054, T1a 0.069 and NEG 0.065.

**T1b and T1 (proof gap).** PINM is spec 8.3 with B = 2,000 per replication; sharp null; κ_core = 0; 20,000 replications.
- T1b: ≤ 0.0077 in all 12 TAIL cells (none / AR 0.8–0.9 / two-state / trailing 30).
- T1 under the calibrated T1a: ≤ 0.0089. With the pre-repair 5-date T1a it reached 0.0713.

**Outside 𝒟_P*** (disclosure only, no level claimed): calibrated L_W miss up to 0.0494 (60-date trailing mean, favourite prices); φ 0.97 0.0486; φ 0.95 0.0478; rv 0.20 ≤ 0.0341.

**Power and feasibility (joint with reach, no persistence unless stated).**

| Cell | reach | P(T2) R3 engine / cycle-1 / **M2** | SUPPORTED M2 | T1a pre-repair / **M2** | NEG pre-repair / **M2** | LOSS_CONFIRMED λ 1 / **M2** |
|---|---|---|---|---|---|---|
| m 17 thin θ_PCE 0.09 | 0.989 | 0.774 / 0.551 / **0.109** | 0.109 | 0.757 / 0.048 | — | — |
| m 17 thin θ 0.10 | 0.990 | 0.840 / 0.648 / **0.161** | 0.161 | 0.836 / 0.079 | — | — |
| m 17 thin θ 0.12 / 0.15 / 0.20 | 0.99 | 0.935 / 0.810 / **0.312**; 0.984 / 0.948 / **0.596**; 0.995 / 0.994 / **0.922** | same | 0.938 / 0.198; 0.987 / 0.466; 0.995 / 0.888 | — | — |
| m 17 thin θ 0.06 (κ ≈ 0.035) | 0.986 | 0.480 / 0.260 / **0.026** | 0.026 | 0.426 / **0.007** | — | — |
| m 17 thin θ −0.12 (κ ≈ −0.069) / −0.06 | 0.97 | — | — | — | 0.889 / **0.116**; 0.386 / **0.004** | 0.505 / **0.053**; 0.087 / **0.002** |
| m 17 full θ_PCE 0.08 / 0.10 / 0.15 / 0.20 | 0.99 | 0.705 / 0.473 / **0.084**; 0.856 / 0.669 / **0.181**; 0.987 / 0.958 / **0.635**; 0.995 / 0.994 / **0.936** | same | 0.660 / 0.028 (θ_PCE) | — | — |
| m 17 full θ −0.12 | 0.967 | — | — | — | 0.885 / **0.116** | 0.537 / **0.059** |
| m 35 thin θ_PCE 0.07 / 0.10 / 0.20 | 0.66–0.76 | 0.477 / 0.343 / **0.067**; 0.635 / 0.558 / **0.231**; 0.759 / 0.759 / **0.752** | same | 0.458 / 0.024 (θ_PCE) | — | — |
| m 35 thin / full θ −0.12 | 0.60 | — | — | — | 0.581 / **0.166**; 0.580 / **0.160** | 0.441 / **0.088**; 0.450 / **0.092** |
| m 35 full θ_PCE 0.07 / 0.10 | 0.66–0.67 | 0.481 / 0.349 / **0.070**; 0.634 / 0.565 / **0.239** | same | 0.453 / 0.024 | — | — |
| m 17 thin θ_PCE, AR 0.8 rv 0.05 | 0.814 | 0.537 / 0.323 / **0.075** | 0.075 | 0.513 / 0.040 | — | — |

Columns:
- The R3 engine column is SUPPORTED (gates applied). The cycle-1 and M2 columns are T2 joint with reach.
- The "pre-repair" T1a / NEG are the 5-date-block tests.

Readings:
1. The cycle-1 rule's class failure reproduces and is larger inside the completely stated class than in Astra's cells: 0.1176 against 0.0605–0.0852. The worst case is the literal §9 30-date trailing mean with favourite prices.
2. The calibrated construction holds every stated level over 𝒟_P* with the declared 80% margin, and the 100,000-replication confirmations sit inside the requirements.
3. **The cost is most of V2's power:**
   - P(T2) at θ_PCE 0.07–0.11;
   - 80%-power effect ≈ 0.18 (m 17; m 35 is reach-limited at ≈ 0.75);
   - T1a MDE80 ≈ 0.11 per share;
   - NEG power ≈ 0.12–0.17 against −0.07 per share;
   - REALIZED_WINDOW_LOSS_CONFIRMED ≈ 0.05–0.09 at θ_W = −0.12.

   GO, θ_PCE, PCE_CEILING, SE_KAPPA_CEILING and IF1–IF5 are not retuned. This is a feasibility consequence for Astra and governance (spec 8.1c, 27), not a validity defect.
4. λ is set by the 30-date trailing-mean regime at latent variance 0.10 with favourite prices. A narrower, separately declared and audited class (for example AR-only: λ_θ 1.50 / λ_κ 1.40) would be cheaper. V2 does not adopt one after seeing these numbers.


### 4.10 Run J — D4-C3-P1: enlarged price class, recalibrated λ and the recalibrated design gate (after Astra D4-C3-M2 recheck @8874dc54)

Script `WEATHER_FORWARD_V2_D4_C3_P1_GATE_SIM_2026-10-02.py` (imports the cycle-2 engine unchanged; `check` mode asserts record-for-record equivalence with it; seeds `SeedSequence([20261102, plan, cell, stream])`; synthetic only; 20,000 replications per cell, worst cells 100,000). Summaries: `WEATHER_FORWARD_V2_D4_C3_P1_SUMMARIZE_2026-10-02.py` (mechanical; no randomness). Raw output and text summaries:
- `..._P1_RUN_J_M3_OUTPUT_2026-10-02.jsonl` (m3_astra 10, m3_mix 60, m3_geo 72, m3_m35 240, m3_class 900; probes m3_probe 30, m3_probe3 6) and `..._M3_SUMMARY_...txt`;
- `..._P1_RUN_J_P1_DERIVE_OUTPUT_2026-10-02.jsonl` (p1_hi 36, p1_t2 360, p1_neg 288) and `..._P1_DERIVE_SUMMARY_...txt`;
- `..._P1_RUN_J_P1_VERIFY_OUTPUT_2026-10-02.jsonl` (p1_go 160 OP-only cells, p1_verify 96) and `..._P1_VERIFY_SUMMARY_...txt`;
- `..._P1_RUN_J_CONFIRM_100K_2026-10-02.jsonl` (20 M3 confirmations, 4 addendum probes m3_probe2, 3 gate-verification cells) and the two confirmation summaries.

The procedures were declared and committed (`ARCHITECT_PROGRESS_CYCLE3.md`, 03640425) before any run. Two small addenda were declared before their own runs (m3_probe2, m3_probe3). One bug fix after a crash (p1_t2 cell 305, an all-win replication, 0/0 in the IF5 ratio): `sek5² / viid <= 6.0` became `(viid <= 0.0 or sek5² / viid <= 6.0)`; it changes no completed cell, and in the saturated cells (p = 1 for every trade, θ ≥ 0.14 for the point mass 0.89) floating-point rounding leaves viid ≈ 1e-33 > 0, so those replications still fail IF5 (INFO_SUFFICIENT ≈ 0 there). Those cells lie beyond every θ a GO design can have (θ_PCE ≤ 0.10) and do not enter Z_EFF or the ceiling.

**M3 (spec 8.1d).** λ_θ = 2.15, λ_κ = 1.80 over 1,288 enlarged-class cells; worst 20,000-replication joint rates L_W miss 0.0394, size 0.0253, U_W 0.0034, T1a 0.0199, NEG 0.0073; 100,000-replication worst cells L_W 0.0397 [0.0385, 0.0409], size 0.0240 [0.0231, 0.0250], T1a 0.0190 [0.0182, 0.0199]. The cycle-2 constants fail (L_W 0.0683, size 0.0469, T1a 0.0289 at 20,000).

**P1 — power curves behind Z_EFF and the ceiling (planning model, no persistence, 120 dates, 20,000 per cell; T2 at λ_θ 2.15, NEG at λ_κ 1.80; power given INFO_SUFFICIENT; P(INFO) is the reach in the second line).**

| Design, thin fills, m 17 | θ = 0.04 | 0.06 | 0.08 | 0.10 | 0.12 | 0.14 | 0.16 | 0.20 | 0.25 |
|---|---|---|---|---|---|---|---|---|---|
| U(0.35, 0.80): P(T2) | 0.00 | 0.00 | 0.02 | 0.04 | 0.11 | 0.22 | 0.38 | 0.73 | 0.96 |
| U(0.70, 0.90): P(T2) | 0.03 | 0.17 | 0.51 | 0.85 | 0.98 | 1.00 | 1.00 | 1.00 | 1.00 |
| U(0.85, 0.90): P(T2) | 0.16 | 0.70 | 0.98 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| point mass 0.89: P(T2) | 0.26 | 0.85 | 1.00 | 1.00 | 1.00 | (saturated: p = 1) | | | |
| U(0.35, 0.80), m 35: P(T2) | 0.00 | 0.01 | 0.04 | 0.11 | 0.26 | 0.46 | 0.66 | 0.93 | 1.00 |
| U(0.35, 0.80), m 35: P(INFO) | 0.64 | 0.65 | 0.66 | 0.68 | 0.69 | 0.70 | 0.72 | 0.76 | 0.82 |

| κ_core | −0.03 | −0.05 | −0.07 | −0.09 | −0.12 | −0.16 | −0.20 |
|---|---|---|---|---|---|---|---|
| NEG, U(0.35, 0.80), m 17 | 0.00 | 0.01 | **0.06** | 0.22 | 0.63 | 0.95 | 1.00 |
| NEG, U(0.70, 0.90), m 17 | 0.00 | 0.01 | **0.10** | 0.32 | 0.75 | 0.97 | 1.00 |
| NEG, point mass 0.89, m 35 | 0.00 | 0.12 | **0.52** | 0.86 | 0.99 | 1.00 | 1.00 |

Per-law ratios (θ80 / SE0_θ, κ90 / SE0_κ), the derived Z_EFF = 7.2 and SE_KAPPA_CEILING = 0.005 are in spec 10.4. Reading:
1. The nominal Z_80 = 2.4865 understated the multiplier of the T2 actually run by a factor of 2.9 (mid prices) to 1.9 (near-cap favourites); NEG needs |κ| ≈ 10–12 × SE0_κ, not the ≈ 3 × SE0_κ of a 5-date-block normal test.
2. Near-cap favourite designs are much better powered than mid-price designs (the per-share variance of a 0.89-priced leg is 0.1 against 0.25), but their NEG power at −0.07 per share is still only 0.25 (m 17) to 0.52 (m 35).
3. P(INFO_SUFFICIENT) falls with throughput (IF5 screens high-dispersion windows): ≈ 1.00 at m 17, 0.59–0.84 at m 35, 0.12–0.38 at m 55, 0.002–0.055 at m 80 / 96.

**Verification at the design's own θ_PCE** (spec 10.4; given θ-side GO and INFO_SUFFICIENT): new rule 0.976–1.000 over 28 cells (100,000: 0.9744 [0.9734, 0.9754] U(0.70, 0.90) m 35 full; 0.9825 [0.9815, 0.9835] m 55 full; 0.9969 [0.9963, 0.9974] U(0.80, 0.90) m 17 full); old rule 0.014–0.51 over 40 cells.

**GO / NO_GO rates** (spec 10.4 table): new GO = 0 on every declared price law at every m ∈ {8, 12, 17, 25, 35, 55, 80, 96} and both fills; θ-side clause passes only for favourite-concentrated laws (U(0.70, 0.90) from m 35–55, U(0.80, 0.90) from m 17–25, U(0.85, 0.90) from m 12–17, point mass 0.89 from m 12–17); the NEG clause never (smallest SE0_κ ≈ 0.0070).

**Best-case NEG power at κ = −0.07 per share** (p1_neg and p1_hi, 48 law × throughput × fill cells): joint with INFO_SUFFICIENT at most 0.44 (point mass 0.89, m 35); 0.06–0.25 at m 17; ≤ 0.047 at m 80 / 96 because INFO_SUFFICIENT is attained in 0.2–5.5% of windows there.

**Feasibility reading.** The missing negative-result instrument at 120 counted dates over 𝒟_P* is fundamental for feasibility (Astra's oracle benchmark: a worst-case-valid non-adaptive test that knows the dependence exactly has power 0.008 (mid) / 0.19 (favourite) at the cycle-2 θ_PCE; the calibrated construction does about as well). It cannot be recovered by recalibration inside V2 and is not recovered by changing W or any owner-frozen surface; it goes to the owner at loop end.

## 5. Terminal-state implications at 120 dates (DERIVED + SIMULATED)

| True θ | Core-dominated mix (M00, θ_PCE ≈ 0.08, GO) | 5% lottery (M05, θ_PCE ≈ 0.21, NO_GO) | 16% lottery (M16, θ_PCE ≈ 0.36, NO_GO) |
|---|---|---|---|
| 0.00 | ND\|IND ≈ 0.85–0.92; false CONFIRMED ≈ 0.03–0.06; false NEG ≈ 0.03 (at 0.025) | would not start | would not start |
| 0.02 (= ERT) | REALIZED_WINDOW_VALUE_SUPPORTED ≈ 0.11–0.18 (analytic 0.18 before gates; run E 0.11); prospective exclusion not usefully testable (R2); REALIZED_WINDOW_RELEVANT_VALUE_EXCLUDED ≈ 0.02 (run E 0.0213); otherwise INDETERMINATE: **unresolved band** | would not start | would not start |
| 0.05 | CONFIRMED ≈ 0.43; information DETECTED ≈ 0.39; INDETERMINATE ≈ 0.55 | (if run: CONFIRMED 0.10, DET 0.345) | (if run: CONFIRMED ≈ 0.01) |
| 0.10 | CONFIRMED ≈ 0.86; information DETECTED ≈ 0.87 | (if run: CONFIRMED 0.52) | (if run: CONFIRMED 0.17, DET 0.875) |
| −0.05 / −0.10 | NEGATIVE_INFORMATION ≈ 0.44 (−0.05, at 0.05); prospective exclusion not usefully testable (R2); REALIZED_WINDOW exclusion (θ_W) ≈ 0.36–0.51 (−0.05), 0.57–0.93 (−0.10) (run E joint with GO ∧ INFO / run D unconditional) | — | NEGATIVE_INFORMATION ≈ 0.94 (−0.10); realised-window exclusion 0 (tail supremum) |

Label names after D4 repair R3: CONFIRMED = REALIZED_WINDOW_VALUE_SUPPORTED (estimand θ_W; the conditions are those of T2 and are unchanged, so the powers above stand for the R3 engine — **D4-C3-M1: T2 now uses the multi-block bound of spec 8.1b, which lowers these confirmation powers; see §4.8, e.g. SUPPORTED at θ = 0.10, m = 17 thin, 0.843 → 0.654; θ = 0.05 0.379 → 0.187**), INDETERMINATE = REALIZED_WINDOW_VALUE_INDETERMINATE. No unconditional prospective label exists in either direction (spec 8.5b, 8.5c); prospective content is the transport frontier (§4.7). Runs A–D above used the pre-R2 vocabulary and are kept as historical evidence.

Reading for governance (D4-C3-P1): the earlier reading described V2 as a screen for θ ≳ 0.08–0.10 with the R3 engine, θ ≳ 0.11–0.12 with the cycle-1 T2 and θ ≳ 0.18 with the cycle-2 T2. With the T2 calibrated over the enlarged 𝒟_P* (λ_θ 2.15, §4.10) the 80%-power effect is about 7.2 × SE0_θ (≈ 0.15–0.21 mid-price, ≈ 0.05–0.10 favourite-concentrated), the information axis has no usable negative-result instrument (NEG power at −0.07 per share ≤ 0.44 jointly over every declared design), and **no declared design passes the recalibrated GO** (spec 10.4): the pre-declared outcome is NO_GO_KAPPA_UNDERPOWERED before t0, an outcome-free design finding, not a strategy result. V2 is not a well-powered screen; the earlier sentence is withdrawn. Whether to continue the Weather candidate (longer horizon, narrower outcome-blind class, a different design, retirement) is for the owner.
