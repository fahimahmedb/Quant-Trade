# FABLE — WEATHER V2 SCIENTIFIC DESIGN CHALLENGE — 2026-09-29

```text
DOCUMENT_ROLE            = NON-AUTHORITATIVE SCIENTIFIC DESIGN CHALLENGE (advisory options for the Weather Architect)
CHALLENGER_ROLE          = independent scientific design challenger (not Architect, not Astra, not Builder)
CHALLENGED_SPEC          = branch claude/intelligent-gates-msidml @ 726070a199957a6fc05515ebb3027e945028fddc
                           WEATHER_FORWARD_FALSIFICATION_SPEC / FREEZE_MANIFEST / ARCHITECT_STATE (2026-09-29) — read, not modified
CHALLENGED_AUDIT         = branch claude/dreamy-franklin-1vki4t @ e1cf4ca0851eace2912ce8a9bcd4a8400ebf4250
                           ASTRA_WEATHER_EXPERIMENT_FEASIBILITY_REVIEW_2026-09-29 — read, not modified
INPUT_VERDICT            = EXPERIMENT_FEASIBILITY = BLOCKED_POWER_BELOW_DECLARED_MEUE (Astra)
DESIGN_CHALLENGE         = DONE_ADVISORY
OUTCOME_DATA_INSPECTED   = NONE (no settlement, resolution, P&L, winner, wallet, leaderboard or price-history data read;
                           every number below is arithmetic on the frozen spec / Astra, or synthetic Monte Carlo with declared inputs)
WEATHER_V2_SPEC          = NOT_PRODUCED (options only; the Architect decides)
FEASIBILITY_PASS         = NOT_DECLARED
BUILDER_AUTHORIZED       = FALSE
REAL_CAPITAL_AUTHORIZED  = FALSE
t0                       = NOT_DECLARED
```

Epistemic labels: **DERIVED** (arithmetic on the frozen spec or on Astra's measured values), **SIMULATED** (synthetic Monte Carlo with declared scenario inputs; no market data), **ASSUMED** (declared scenario choice), **UNKNOWN** (not established here).

Notation carried from the frozen spec: `θ = E[N_j]/E[C_j]` (net cash per dollar committed, ratio of means, estimated by `Σ N_j / Σ C_j`); `c_j = C_j / n_j` (all-in cost per share, fee included); `y_j ∈ {0,1}` (leg resolves to 1); `N_j = n_j (y_j − c_j)`; `θ_MEUE = 0.02`; α = 0.05 one-sided; target power 0.80; `z_α + z_β = 2.486`.

---

## 0. Summary of the challenge

1. Astra's core arithmetic is reproduced exactly (section 1). The contradiction is real and, in one respect, worse than stated: at the venue's throughput the design can neither **confirm** nor **reject** an edge of 0.02 per dollar. Rejecting θ ≥ 0.02 with 80% power when the truth is zero needs SE ≈ 0.008, i.e. ≈ 15,000 effective trades, the same information the confirmation needs.
2. The binding constraint is not trades but **dates**: with within-date correlation ρ_d, no more than `1/ρ_d` effective trades can be extracted per target date whatever the trigger rate. A 120-date window is an information ceiling of roughly 1,100–2,500 effective trades (DERIVED, section 1.3).
3. The heavy-tail problem (D4) is not a variance nuisance but an **estimator-weighting** fact: the ratio-of-means estimator weights each leg's outcome by shares, so a leg bought at 0.001 carries ≈ 600× the outcome weight of a leg bought at 0.6. Under a 16% share of sub-4¢ legs, every resampling method loses essentially all power at θ ≤ 0.10, and the frozen percentile block bootstrap **falsely excludes the MEUE** 13% of the time when the true θ is 0.05 (SIMULATED, section 4).
4. A per-contract calibration estimand `κ = E[y_j − c_j]` (bounded, share-unweighted) is immune to the tails and keeps the power that the core stratum has; but it is a **different economic quantity** (the return of a constant-payout sizing, not the frozen constant-dollar sizing) and it is **blind to a tail-concentrated edge** (power 0.12 at θ = 0.32, SIMULATED). Any gatekeeper on κ must therefore be **stratified**: core-stratum calibration plus an exact tail win-count test (power 0.95 in the same scenario).
5. Date-only clustering (the frozen primary) over-rejects at 14–19% when station-level dependence of the size Astra assumes is present; two-way (date-block × station) inference holds size, at a real power cost that is the true power (SIMULATED, section 6).
6. Four repair families are developed (section 2). None recovers θ_MEUE = 0.02 inside 120 dates; the only family that can is a 3–6-year cumulative program (Family A). The recommendation (section 8) is a configured Family D: stratified two-estimand fixed-horizon design with price-implied null inference, honest labels that separate ECONOMIC_RELEVANCE_THRESHOLD from PRIMARY_CONFIRMABLE_EFFECT, a readiness-gated t0, and at most one futility-only interim on bounded statistics.

---

## 1. Independent reproduction of Astra's core power issue (D1)

### 1.1 Required independent trades (DERIVED)

`N = ((z_α + z_β) σ / θ)²` with `(z_α + z_β)² = 6.183`.

| θ | σ_eff = 1.0 | σ_eff = 2.0 | σ_eff = 2.9 |
|---|---|---|---|
| 0.02 | 15,456 | 61,826 | 129,988 |
| 0.05 | 2,473 | 9,892 | 20,798 |
| 0.10 | 618 | 2,473 | 5,200 |

Identical to Astra §6.3 (rounding aside). With DEFF ∈ {2, 3, 4} the trade requirement at θ = 0.02 is 30,913 / 46,369 / 61,826 (σ = 1) and 259,977 / 389,965 / 519,953 (σ = 2.9). The 120-date ceiling at a 100% trigger rate is ≈ 8,400 trades.

### 1.2 Calendar equivalent (DERIVED): dates needed for 80% power at 27 trades/day (Astra's conservative throughput)

| σ_eff | DEFF | θ = 0.02 | θ = 0.05 | θ = 0.10 |
|---|---|---|---|---|
| 1.0 | 2 | 1,145 d | 183 d | 46 d |
| 1.0 | 3 | 1,717 d | 275 d | 69 d |
| 1.0 | 4 | 2,290 d | 366 d | 92 d |
| 2.0 | 3 | 6,870 d | 1,099 d | 275 d |
| 2.9 | 3 | 14,443 d | 2,311 d | 578 d |

At 42 trades/day (central) the σ = 1 row becomes 736 / 1,104 / 1,472 dates for θ = 0.02. **θ_MEUE = 0.02 is a 3–6-year quantity at best, and a multi-decade quantity if the executable leg mix contains lottery legs.**

### 1.3 The date ceiling (DERIVED; not in Astra's framing)

If the m trades of one target date share a common component with correlation ρ_d, the variance of the date mean is `σ² (1 + (m − 1) ρ_d) / m → σ² ρ_d` as m grows. Each date therefore contributes at most `1/ρ_d` effective trades, so `n_eff ≤ D / ρ_d` regardless of the trigger rate. Astra's DEFF range 2–4 at m = 27 corresponds to ρ_d ≈ 0.04–0.12, i.e. 6.8–13.5 effective trades per date, hence:

| DEFF (m = 27) | n_eff at 60 dates | 120 dates | 365 dates |
|---|---|---|---|
| 2 | 810 | 1,620 | 4,928 |
| 3 | 540 | 1,080 | 3,285 |
| 4 | 405 | 810 | 2,464 |

Consequence: `MIN_SAMPLE = 1,000 trades` is not the information floor of this experiment; the number of complete target dates is. Any repair that raises trades per date (more legs, more stations) buys almost nothing once m ≳ 1/ρ_d. Only more dates, or a lower-variance statistic, buy information.

### 1.4 Frozen-gate label probabilities (DERIVED, normal approximation; criteria 6, 7, 9 and CONSERVATIVE assumed to pass)

FORWARD_SIGNAL = `L95 > 0 ∧ θ̂ ≥ 0.02 ∧ L80 ≥ 0.01`; REJECTED = `U95 < 0.02`; REQUIRES_MORE_DATA = `0.02 ≤ θ̂ ≤ 1.645·SE`; remainder = NOT_PROVEN or an undefined region (Astra S1–S4).

| SE | true θ | FORWARD_SIGNAL | REJECTED | REQUIRES_MORE_DATA | NOT_PROVEN / undefined |
|---|---|---|---|---|---|
| 0.054 (spec's own figure) | 0.00 | 0.05 | 0.10 | **0.31** | 0.54 |
| | 0.02 | 0.10 | 0.05 | 0.40 | 0.45 |
| | 0.05 | 0.24 | 0.01 | 0.47 | 0.28 |
| | 0.10 | 0.58 | 0.00 | 0.35 | 0.07 |
| 0.030 (n ≈ 3,240, σ 1, DEFF 3) | 0.00 | 0.05 | 0.16 | 0.20 | 0.58 |
| | 0.02 | 0.16 | 0.05 | 0.34 | 0.45 |
| | 0.05 | 0.51 | 0.00 | 0.33 | 0.15 |
| | 0.10 | 0.95 | 0.00 | 0.04 | 0.00 |
| 0.088 (n ≈ 3,240, σ 2.9, DEFF 3) | 0.00 | 0.05 | 0.08 | 0.36 | 0.51 |
| | 0.05 | 0.14 | 0.02 | 0.49 | 0.34 |
| | 0.10 | 0.31 | 0.01 | 0.51 | 0.18 |

Astra's SE = 0.054 row is reproduced to the second decimal. The additional rows show that even the most favourable achievable precision (SE 0.030) leaves a true θ = 0.02 unlabelled 79% of the time and a zero edge unlabelled 78% of the time.

### 1.5 Grid requested by the mission: θ ∈ {0, 0.02, 0.05, 0.10} × σ_eff ∈ {1, 2, 2.9} × DEFF ∈ {2, 3, 4} at n = 3,240 (DERIVED)

Cells read `P(L95 > 0) / P(U95 < 0.02) / P(indeterminate)`.

| σ_eff | DEFF | SE | MDE | θ = 0.00 | θ = 0.02 | θ = 0.05 | θ = 0.10 |
|---|---|---|---|---|---|---|---|
| 1.0 | 2 | 0.025 | 0.062 | 0.05/0.20/0.75 | 0.20/0.05/0.75 | 0.64/0.00/0.35 | 0.99/0.00/0.01 |
| 1.0 | 3 | 0.030 | 0.076 | 0.05/0.16/0.79 | 0.16/0.05/0.79 | 0.50/0.00/0.50 | 0.95/0.00/0.05 |
| 1.0 | 4 | 0.035 | 0.087 | 0.05/0.14/0.81 | 0.14/0.05/0.81 | 0.41/0.01/0.58 | 0.89/0.00/0.11 |
| 2.0 | 2 | 0.050 | 0.124 | 0.05/0.11/0.84 | 0.11/0.05/0.84 | 0.26/0.01/0.73 | 0.64/0.00/0.36 |
| 2.0 | 3 | 0.061 | 0.151 | 0.05/0.09/0.86 | 0.09/0.05/0.86 | 0.21/0.02/0.78 | 0.50/0.00/0.50 |
| 2.0 | 4 | 0.070 | 0.175 | 0.05/0.09/0.86 | 0.09/0.05/0.86 | 0.18/0.02/0.81 | 0.41/0.00/0.59 |
| 2.9 | 2 | 0.072 | 0.179 | 0.05/0.09/0.86 | 0.09/0.05/0.86 | 0.17/0.02/0.81 | 0.40/0.00/0.60 |
| 2.9 | 3 | 0.088 | 0.219 | 0.05/0.08/0.87 | 0.08/0.05/0.87 | 0.14/0.02/0.84 | 0.30/0.01/0.69 |
| 2.9 | 4 | 0.102 | 0.253 | 0.05/0.07/0.88 | 0.07/0.05/0.88 | 0.12/0.03/0.85 | 0.25/0.01/0.74 |

Reading: at σ_eff = 1 the design is a usable screen for θ ≳ 0.08; at σ_eff ≥ 2 it is a screen for θ ≳ 0.15–0.25 only; at no cell is θ = 0.02 either confirmable or rejectable.

### 1.6 The two-sided impossibility (DERIVED)

To **reject** economic relevance (`U95 < 0.02`) with 80% power when θ = 0 requires `SE ≤ 0.02 / 2.486 = 0.008`, i.e. `n_eff ≈ 15,456` at σ = 1: the same information as confirming θ = 0.02. A falsification protocol "designed to make the hypothesis fail" at the MEUE level cannot fail it either inside 120 dates. The honest outcome space of any 120-date design is therefore three-valued at the MEUE scale: confirm-large / reject-large / indeterminate.

### 1.7 What is and is not reproduced

- Reproduced: N_naive, DEFF-adjusted requirements, MDE at achievable n, the gate-label table, the burn-in day-33 arithmetic (section 5), the date-cap consequence of ρ_d.
- Not reproduced: Astra's **measured** σ_eff = 2.93 (its X1 book/forecast cross-section was not re-fetched). The synthetic price mix used below (84% legs at c ~ U(0.35, 0.80), 16% at c ~ log-U(0.002, 0.04)) yields σ_eff ≈ 5.1. The disagreement is itself the finding: **σ_eff is governed by the few lowest prices in the mix and is not a stable design constant**; it must be computed from the observed executable leg mix before t0 (section 5.5), which prices alone allow.
- Small disagreements with Astra: (a) the MEUE is also un-rejectable (1.6); (b) the trade floor is not where the information binds (1.3); (c) the spec's σ = 1.2 is not the defect, the share-weighting of the estimator is (section 4.1).

---

## 2. Candidate repair architectures (D1)

All families keep the frozen trading rule R* (M, W, σ_dress, h, T_entry, model, sizing) untouched. They change only the estimand set, the horizon, the analysis plan and the labels. Where a family would also require a trading-rule change, it is said so explicitly.

### 2.1 Family A — Cumulative multi-window program (retain θ_ERT = 0.02 as the test threshold)

| Field | Specification |
|---|---|
| Estimand | horizon-average `θ̄ = Σ_windows Σ N / Σ_windows Σ C` over K consecutive pre-registered 120-date windows under the same frozen rule |
| Null / alternative | `H0: θ̄ ≤ 0` vs `H1: θ̄ > 0`; economic gate `L95(θ̄) > 0 ∧ θ̄ ≥ 0.02`; rejection `U95(θ̄) < 0.02` |
| α / power | 0.05 one-sided; 0.80 at θ̄ = 0.02 |
| Information requirement | `n_eff ≈ 15,456` (σ = 1) → with DEFF 2–4 and 27 trades/day, **1,145–2,290 dates ≈ 10–19 windows ≈ 3.1–6.3 years**; σ = 2.9 → 26–53 years |
| DEFF | 2–4 within window, plus a between-window component (regime drift) that must be estimated from the window-level scatter (K − 1 degrees of freedom) |
| Analysis horizon | fixed K declared before window 1 from the power calculation; interim meta-analytic summaries reported but not gating |
| Stopping rule | none on results; a MECHANICS_CHANGE ends a window and starts a new one only if the rule still applies unchanged, otherwise the program ends |
| MDE | 0.02 at the declared K only; per window, the MDE of Family B applies |
| Justified conclusions | "the average edge of R* over 2026–2030 is ≥ 0.02 per dollar" (or is excluded). Not justified: anything about the current edge; anything if the venue changes mechanics before K windows complete |
| Verdict | scientifically coherent, economically weak: the North Star's decision problem (act on current evidence) is not served by a 2030 answer; the venue has changed its settlement template at least twice in ≈ 6 months (spec C5, §20), so the probability of completing K windows unchanged is low (UNKNOWN, but the base rate is adverse). Seasonality: a 30-day trailing bias correction creates an annual cycle in the edge; the within-window 5-date blocks do not capture it; the between-window variance term does, at the cost of K − 1 degrees of freedom |

### 2.2 Family B — Two-threshold honest-label fixed design (ECONOMIC_RELEVANCE_THRESHOLD ≠ PRIMARY_CONFIRMABLE_EFFECT)

| Field | Specification |
|---|---|
| Estimand | θ as frozen |
| Declared constants | `θ_ERT = 0.02` (economic relevance, a reporting threshold only); `θ_PCE` = the MDE at the pre-t0-computed information (section 5.5), frozen in the manifest before t0 (expected 0.06–0.09 if the executable mix is core-only; 0.15–0.25 if lottery legs persist) |
| Null / alternative | `H0: θ ≤ 0` vs `H1: θ > 0` |
| α / power | 0.05 one-sided; 0.80 **at θ_PCE**, stated as the only powered claim |
| Information requirement | 120 complete target dates (fixed, no 90-date option) |
| DEFF | declared range 2–4; the PCE is computed at DEFF = 3 and reported at 2 and 4 |
| Analysis horizon | one analysis at 120 complete dates + 3-day resolution lag; no interim |
| Stopping rule | none on results (as frozen) |
| MDE | = θ_PCE by construction |
| Labels | SIGNAL (`L95 > 0` + gates); LARGE_EDGE_EXCLUDED (`U95 < θ_PCE`); RELEVANT_EDGE_EXCLUDED (`U95 < θ_ERT`, rarely reachable); INDETERMINATE (else, with the CI as the result); "REQUIRES_MORE_DATA" retired |
| Justified conclusions | confirm or exclude a **large** edge; report the CI. Not justified: any statement about θ in [0, θ_PCE) beyond the interval; "no edge" from INDETERMINATE |
| Verdict | honest and cheap; on its own it leaves a zero-edge rule INDETERMINATE 75–88% of the time (section 1.5), which is a weak falsification instrument. It needs Family D's information gatekeeper to have a real negative result |

### 2.3 Family C — Information-monitored group-sequential design

| Field | Specification |
|---|---|
| Estimand | θ as frozen (pure version) or κ_core as the monitored statistic with θ tested once at the end (hybrid, section 8) |
| Null / alternative | as B |
| α / power | overall 0.05 one-sided, Lan–DeMets spending with an O'Brien–Fleming-type function `α(t) = 1 − Φ(z_α / √t)`; K = 3 looks at 60 / 90 / 120 complete dates (t ≈ 0.5, 0.75, 1.0): cumulative spend 0.010 / 0.029 / 0.050, z-boundaries **2.33 / 1.96 / 1.77** (DERIVED); final power at θ = 0.05: 0.49 vs 0.51 for the fixed design (SE_final 0.030) — a negligible cost |
| Information requirement | `I_max` = 120 dates unless the Architect extends it; the information fraction t_k is the ratio of the price-implied null variances (computable without outcomes) rather than the empirical variance (section 7, CD2) |
| DEFF | as B; DEFF enters through the empirical variance at the final look only |
| Stopping rule | efficacy at the boundaries above; futility non-binding or binding only on bounded statistics (κ_core, tail count), never on θ |
| Expected stopping (DERIVED, SE_final 0.030) | θ = 0.10: 51% stop at 60 dates, 32% at 90; θ = 0.15: 89% at 60; θ = 0.05: 12% / 19% / 17% (mostly runs to 120); θ = 0: 1% / 2% / 2% false efficacy |
| MDE | at the final look ≈ 1.05 × Family B's MDE (boundary 1.77 vs 1.645) |
| Justified conclusions | as B, plus "a large edge was detected early"; the CI at an early stop must be the stage-wise-ordering interval, not the naive one |
| Verdict | saves calendar only when the edge is large or absent; does nothing for θ ∈ [0.02, 0.06]. In its pure form it is **hazardous with lottery legs** (CD2): before the first tail win the empirical variance is understated (all tail legs have lost), which can trigger a false futility stop precisely when the rare wins have not yet arrived, and after a tail win the information fraction jumps. The hybrid form (monitor κ_core; test θ once) removes the hazard |

### 2.4 Family D — Stratified two-estimand hierarchical design (information gatekeeper → economics)

| Field | Specification |
|---|---|
| Estimands | **E1 (information, confirmatory)**: stratified calibration excess: `κ_core = E[y_j − c_j | j ∈ core]` and the tail-stratum win count `W_tail = Σ_{j∈tail} y_j` against its price-implied expectation `Λ_tail = Σ_{j∈tail} c_j`. **E2 (economic, primary)**: θ as frozen, pooled, plus `θ_core`, `θ_tail` reported. Strata are defined by the venue's own tick regime recorded at T_entry (the 0.001-tick zone; boundary ≈ 0.04 per spec C15 — to be read from the frozen `tick` field, UNKNOWN here), never by outcomes or by the analyst |
| Nulls | T1a: `κ_core ≤ 0`; T1b: `E[W_tail] ≤ Λ_tail`; T2: `θ ≤ 0` |
| Test structure | fixed-sequence gatekeeping: T1 = {T1a at α/2, T1b at α/2} (Bonferroni inside the gate; the gate passes if either rejects); T2 at α = 0.05 only if T1 passes. Familywise α = 0.05 for the economic claim |
| Inference engines | price-implied null Monte Carlo (PINM, section 4.4) **and** two-way studentized block bootstrap (section 6); a test rejects only if both reject ("more conservative of two", pre-declared) |
| α / power | 0.05 one-sided; **T1a power ≈ 0.6 at θ = 0.05 and ≈ 0.98 at θ = 0.10, unchanged by lottery legs** (DERIVED 0.57 / 0.98 at n = 3,240, DEFF 3; SIMULATED 0.61 / 0.97 at n = 2,700, section 4.2); T1b power 0.95 against a 3× tail mispricing with ≈ 6 expected wins (SIMULATED); T2 power = Family B's |
| Information requirement | 120 complete dates; minimum information floor `SE(κ_core) ≤ 0.02` (≈ n_eff ≥ 500) else INFORMATION_INSUFFICIENT (validity flag, not a scientific label) |
| DEFF | two-way; declared 2–4; measured and reported (section 6.3) |
| Stopping rule | one optional futility-only look at 60 complete dates on T1 (stop as NEGATIVE_INFORMATION if `U95(κ_core) < 0` and the tail-count upper bound < Λ_tail); no efficacy stopping; nothing on θ |
| MDE | κ_core: ≈ 0.033 probability units (θ-equivalent ≈ 0.07 in the core stratum); θ: Family B's PCE |
| Justified conclusions | (i) the forecast rule does / does not identify mispriced legs (well-powered, including a decisive negative if the public post-mortem C12 is representative: −13.9% per trade ≈ κ ≈ −0.07 → power ≈ 1.0); (ii) a large net edge is confirmed / excluded; (iii) an interval for θ with a stratified decomposition. Not justified: reading κ as the frozen strategy's return; reading INDETERMINATE θ as "no edge" or as "edge" |
| Verdict | the only family with a real negative result at 120 dates and with tail immunity in the confirmatory step; it still cannot resolve θ ∈ [0.02, 0.06]. Recommended configuration in section 8 |

### 2.5 Trading-rule changes deliberately NOT recommended here (listed only to keep the separation explicit)

| Option | Type | Effect on inference | Why it is not an inference repair |
|---|---|---|---|
| Constant-payout sizing (fixed shares per leg instead of S_ref = 50 USD) | TRADING-RULE CHANGE (sizing) | would make θ ≈ κ, removing the tail variance | it tests a different strategy; a decision the Architect may take outcome-blind, but it must be declared as a new rule, not as "robust inference" |
| Exclude legs in the 0.001-tick zone from R* | TRADING-RULE CHANGE (leg filter) | σ_eff 2.9–5 → ≈ 1 | deletes the part of the rule where the ensemble disagrees most with the market; forbidden by the mission as a power repair |
| Raise h | TRADING-RULE CHANGE | fewer, larger-edge triggers | tuning; forbidden |
| CONSERVATIVE slippage = one venue tick instead of a flat +0.01 | EXECUTION-MODEL CHANGE | removes an 11× artefact on 0.001-asks (Astra §6.5) | not a rule change and not an inference change; it repairs a gate criterion (CD9) and should be decided outcome-blind |

---

## 3. Comparative table

| Criterion | A — cumulative program | B — two-threshold fixed | C — group-sequential | D — stratified hierarchical (recommended config.) |
|---|---|---|---|---|
| Confirms θ ≥ 0.02 | yes, after 3–6 y (σ = 1) | no | no (unless I_max ≈ years) | no |
| Rejects θ ≥ 0.02 | yes, after 3–6 y | no (P ≈ 0.07–0.20 at θ = 0) | no | no |
| Confirms a large edge (≥ PCE) at 120 d | per window: as B | 0.80 at PCE | ≈ 0.78 at PCE, often earlier | 0.80 at PCE (T2), after T1 |
| Real negative result at 120 d | no | no (INDETERMINATE 75–88% at θ = 0) | no | **yes** (T1: κ_core significantly negative, power ≈ 0.6–1.0 for κ ≤ −0.03) |
| Immune to lottery-leg variance in the confirmatory step | no | no | no (hazardous) | **yes** (κ_core, W_tail); θ still reported with tails |
| Detects a tail-concentrated edge | via θ only (noisy) | via θ only | via θ only | **yes** (T1b, power 0.95 at 3×) |
| Handles date × station dependence | must add | must add | must add | built in (two-way) |
| Requires outcome-free pre-t0 σ_eff / PCE | optional | required | required | required |
| Calendar to first informative label | ≥ 3 y | 120 d | 60–120 d | 60 (futility) – 120 d |
| Mechanics-change exposure | very high | moderate | moderate | moderate |
| Complexity added for the Builder | low per window | low | medium (spending, ordering CIs) | medium (strata, PINM, two-way) |
| Hidden failure modes | seasonality, drift, venue changes (CD1) | zero edge reads as "maybe" | heavy tails × interim variance (CD2), few blocks (CD3) | gatekeeper blind to tails unless stratified (CD7); PINM dependence declaration (CD8) |

---

## 4. D4 — Heavy-tailed return inference

### 4.1 Mechanism (DERIVED)

`θ̂ = Σ_j n_j (y_j − c_j) / Σ_j C_j`. Each leg's calibration surprise `(y_j − c_j)` is weighted by its share count `n_j = C_j / c_j`. At equal capital, a leg bought at c = 0.001 has 600× the outcome weight of a leg at c = 0.6, and its surprise has the compound-Poisson shape of a rare 1,000× payout. The per-trade SD in θ units under a fair price is `√((1 − c)/c)`: 0.82 at c = 0.6, 4.9 at c = 0.04, 31.6 at c = 0.001. The spec's σ = 1.2 is the mid-price value; the mix value is dominated by the cheapest few percent of legs (Astra: 6 of 38 triggers below 0.05 → 2.93). This is a property of the economic estimand, not of the data quality, and it cannot be removed by any resampling method: a bootstrap cannot put mass on a 1,000× win that did not occur in the sample.

### 4.2 Simulation evidence (SIMULATED; synthetic prices, no market data)

Design: D = 90 dates × m = 30 trades = 2,700 trades; latent Gaussian copula with a date effect (latent ρ_d = 0.10); prices: 84% core legs c ~ U(0.35, 0.80), 16% tail legs c ~ log-U(0.002, 0.04); capital C_j = 50 with probability 0.68 else U(10, 50); edge model p_j = c_j (1 + θ) (every dollar earns θ in expectation); 300 replications; 300 bootstrap / null draws each. Methods: PCT = frozen percentile moving-block bootstrap over dates (block 5); STUD = studentized block bootstrap with the linearised date-cluster SE; CR = cluster-robust normal; PINM = price-implied null Monte Carlo with the correctly declared dependence; κ-CR = per-contract mean of (y − c) with date-cluster SE. Monte-Carlo error ≈ ±0.013 at rates near 0.05, ±0.03 near 0.5.

| Scenario | SD(θ̂) | skew | P(L95 > 0): PCT / STUD / CR / PINM | P(U95 < 0.02): PCT / STUD | 90% CI coverage PCT / STUD | P(L95(κ) > 0) |
|---|---|---|---|---|---|---|
| core-only, θ = 0 | 0.030 | 0.03 | 0.067 / 0.073 / 0.057 / 0.057 | 0.180 / 0.173 | 0.86 / 0.87 | 0.047 |
| core-only, θ = 0.05 | 0.031 | −0.22 | 0.58 / 0.59 / 0.58 / 0.55 | 0.013 / 0.007 | 0.87 / 0.86 | 0.63 |
| core-only, θ = 0.10 | 0.029 | −0.15 | 0.96 / 0.95 / 0.96 / 0.95 | 0.000 / 0.000 | 0.84 / 0.84 | 0.98 |
| **16% tails, θ = 0** | **0.100** | 0.75 | 0.013 / 0.033 / 0.003 / 0.050 | 0.253 / 0.180 | 0.79 / 0.82 | 0.050 |
| **16% tails, θ = 0.05** | 0.109 | 1.19 | **0.067 / 0.120 / 0.030 / 0.087** | **0.130 / 0.097** | 0.77 / 0.82 | **0.61** |
| **16% tails, θ = 0.10** | 0.114 | 0.89 | 0.24 / 0.32 / 0.14 / 0.17 | 0.053 / 0.030 | 0.76 / 0.78 | 0.97 |
| tails, θ = 0, PINM declares independence (true ρ_d 0.10) | 0.111 | 1.11 | PINM 0.067; **PINM on κ 0.133** | | | |
| tails, θ = 0, PINM declares ρ_d 0.10 (true 0.20) | 0.117 | 0.99 | PINM 0.047; PINM on κ 0.073 | | | |
| core-only, θ = 0, PINM declares independence | | | **PINM 0.207** | | | |

Readings:
- With tails, **no method on θ has meaningful power at θ ≤ 0.10** (0.03–0.32), reproducing Astra's MDE ≈ 0.2+ by simulation rather than by formula.
- The frozen percentile bootstrap **falsely excludes the MEUE** (`U95 < 0.02`) 13% of the time at true θ = 0.05 and 5% at θ = 0.10 (bootstrap cannot represent unobserved tail wins → upper bound too low). This is an anti-conservative failure in the falsification direction.
- 90% intervals under-cover with tails (0.76–0.82) for both percentile and studentised methods.
- κ keeps its power (0.61 / 0.97) with or without tails and holds size (0.05).
- PINM is exact under the declared dependence and mildly sensitive to mis-declaration for θ (0.067) but strongly for κ (0.133 when independence is wrongly declared), and it over-rejects badly for a core-only θ if independence is declared (0.207): **dependence must be declared or measured; PINM alone is not enough.**

Tail-concentrated edge (SIMULATED; core legs fair, tail legs win 3× their implied probability; θ_true = 0.32, κ_true = 0.004, expected tail wins 5.8 → 17.4):

| Test | rejection rate at 3× | at 1× (null) |
|---|---|---|
| θ, percentile block bootstrap | 0.77 | 0.010 |
| θ, PINM | 0.70 | 0.057 |
| κ pooled, CR | **0.12** | 0.053 |
| κ_core, CR | 0.06 | 0.047 |
| **W_tail vs Λ_tail, PINM** | **0.95** | 0.023 |
| W_tail, Poisson (no dependence) | 0.95 | 0.023 |

A pooled per-contract gatekeeper would block a genuine 32¢-per-dollar tail edge 88% of the time; a stratified gatekeeper with an exact tail win-count test sees it 95% of the time.

### 4.3 Method comparison for the θ interval and test

| Method | Validity with few clusters | Heavy tails (rare 25–1,000× wins) | Ratio-of-means, unequal capital | Estimand preserved | Verdict |
|---|---|---|---|---|---|
| Percentile block bootstrap (frozen) | acceptable at ≥ 12 blocks for light tails | fails: cannot represent unobserved wins; U95 too low; coverage 0.76–0.79 | yes | yes | **not adequate as primary** |
| Studentised (bootstrap-t) block bootstrap | better second-order accuracy | same limitation, slightly better (0.78–0.82) | yes | yes | primary interval **for the core stratum**; reported for pooled θ |
| BCa cluster bootstrap | needs a jackknife over clusters; OK at 60–120 dates | corrects skew but not missing mass | yes | yes | sensitivity only |
| Two-way cluster bootstrap (pigeonhole / wild) | conservative (size 0.01–0.03 in section 6) | as above | yes | yes | sensitivity; the two-way sandwich is preferred as primary SE |
| Cluster-robust asymptotics (CR2/CR3, Satterthwaite) | fine at 60–120 dates, weak at ≈ 27 effective stations | leverage point in the cluster with the win → unstable | yes | yes | reported; not primary |
| Winsorised / trimmed θ | fine | robust | yes | **no** (truncates the payouts that are the economics) | **rejected as an estimand**; a winsorised θ may be reported descriptively only, labelled as a different quantity |
| **Price-implied null Monte Carlo (PINM)** | exact under the sharp null with declared dependence, any n | **exact**: the null distribution of a 1,000× payout at c = 0.001 is computed, not resampled | yes | yes (tests H0 for θ itself) | **primary test engine**, paired with the empirical method |
| Per-contract κ (stratified) with CR / bootstrap | fine | immune (bounded in [−1, 1]) | not the same weighting | **no** (a different economic quantity: constant-payout sizing) | **confirmatory information estimand**, never reported as θ |
| Exact tail win-count test (Poisson-binomial / PINM) | exact | exact | not applicable | information only | **T1b** |

### 4.4 Recommendation (INFERENCE CHANGES only)

1. **Keep θ pooled as the primary economic estimand.** No winsorising, trimming, capping or leg deletion inside the estimand.
2. **Pre-declare a mechanics-defined stratification** by the venue tick regime recorded at T_entry (0.001-tick zone = tail stratum). Report `θ_core`, `θ_tail`, capital shares, `W_tail`, `Λ_tail`, and the largest single-trade contribution. The pooled θ is unchanged by the decomposition.
3. **Primary test engine = PINM**: draw `y*_j ~ Bernoulli(c_j)` for the actually traded legs under a declared dependence structure (latent Gaussian copula with date and station effects, ρ_d and ρ_s declared before t0; sensitivity at ×0.5 and ×2), B = 10,000; p-value = `P(θ* ≥ θ̂)`. It is the placebo B4 logic applied to the chosen legs instead of random legs, and it is the only engine that handles a rare 1,000× win exactly. It tests the sharp null "every traded leg is fairly priced after fees", the boundary of `θ ≤ 0`.
4. **Confirmatory engine = two-way studentised block bootstrap** (section 6). A hypothesis is rejected only if both engines reject. The 90% interval for θ is the studentised one, reported with the PINM null quantiles beside it.
5. **Confirmatory information estimands** `κ_core` and `W_tail` as in Family D, reported and tested with the same two engines.
6. **Retire the percentile block bootstrap as primary**; keep it as a sensitivity row.
7. **Retire the criterion "R* beats B4/B5 by ≥ θ_MEUE" as an inferential statement** (the SE of a difference of two θ's is 0.04–0.14; a 0.02 margin has no content); compare on κ_core and W_tail instead, or keep it descriptive.
8. **The pre-t0 σ_eff, PCE and information fraction come from prices** (`Var_0(N_j) = C_j² (1 − c_j)/c_j`), which is outcome-free (section 5.5).

### 4.5 Separation of change types

| Change | Type | Changes θ's meaning? | Outcome-blind? |
|---|---|---|---|
| Stratified reporting, PINM, studentised two-way bootstrap, κ_core / W_tail as confirmatory | INFERENCE CHANGE | no | yes |
| Retiring percentile bootstrap | INFERENCE CHANGE | no | yes |
| Constant-payout sizing; tail-leg exclusion; hurdle change | TRADING-RULE CHANGE | yes (new strategy) | possible, but must be declared as a new rule and re-frozen; not recommended by this memo |
| CONSERVATIVE slippage = one venue tick | EXECUTION-MODEL CHANGE | no (affects a gate, not θ_REALISTIC) | yes |

---

## 5. D6 — Outcome-free readiness architecture (W = 30 prior resolved dates)

### 5.1 The bootstrapping arithmetic (DERIVED; reproduces Astra §8)

A decision for target date D is taken at `T_entry(D) = 18:00 local, D − 1`. Date D − 1 cannot be resolved by then (its first observation is after local midnight). Date D − 2 becomes resolvable from early D − 1 local (the spec's resolution timing is the first data point of the following date; the proposal-to-final delay is UNKNOWN here) and is normally final before T_entry(D), but a slow resolution, a correction hold (up to 7 days) or a dispute pushes the latest usable date to D − 3 or earlier. If every station's first archived T_entry vintage targets D = 2 (capture starts before 18:00 local on capture day 1), the usable prior dates at T_entry(D) are {2, …, D − 2}, i.e. D − 3 of them: **the first E8-eligible target date is D = 33** at 100% completeness with D − 2 always final; D = 34 if D − 3 is the reliable latest; ≈ 35–36 at 95% completeness; + up to 7 for a station with a correction hold. The frozen "burn-in ≥ 30 days then t0" therefore starts the clock with zero E8-eligible stations, and the frozen rule's trigger rate is unobservable before day ≈ 33.

### 5.2 Definitions (all computable without any outcome of the experiment; settled values of past dates are inputs of the frozen rule, not outcomes of the experiment; P&L of pre-t0 decisions is never computed)

- `USABLE(s, κ, d)`: an archived FORECAST_VINTAGE for (s, d) with `captured_at ∈ [T_entry(d) − 3 h, T_entry(d)]` exists **and** the market (s, d, κ) is FINAL (resolved, not open for correction, not disputed) **and** `settlement_mode` is recorded **and** the parsed settlement page reconciles or the mismatch is logged. Whether non-NOAA modes count follows the frozen rule (they do, at the tail boundary); excluding them (Astra D10) is a TRADING-RULE CHANGE to the bias term and is the Architect's call, not a readiness rule.
- `BIAS_N(s, κ, D)` = number of USABLE dates d ≤ D − 2 whose resolution time ≤ T_entry(D). `BIAS_SPAN(s, κ, D)` = calendar days between the 30th-most-recent USABLE date and D − 2.
- `READY(s, κ, D)` iff `BIAS_N ≥ 30` **and** `BIAS_SPAN ≤ 40` (freshness: a 30-date window stretched over more than 40 calendar days by gaps is a stale bias estimate across a seasonal transition; this is a readiness criterion for t0 only — after t0 the frozen E8 applies as written).
- `GLOBAL_READY(D)` iff ≥ 30 distinct stations are READY for at least one kind **and** ≥ 25 are READY for both kinds **and** capture completeness ≥ 95% over the trailing 30 days **and** settlement-parse agreement ≥ 98% over ≥ 30 dates **and** the book-timestamp window is tested on `captured_at` (Astra D3; without it completeness is unreachable).
- `t0_ELIGIBLE(D)` iff GLOBAL_READY has held for ≥ 14 consecutive target dates (the pre-t0 observation phase, 5.4) and the readiness report is committed with its hash.

### 5.3 Earliest calendar (DERIVED, capture day 1 = day 1)

| Milestone | Earliest day | Typical (95% completeness, one correction hold among 35 stations) |
|---|---|---|
| first READY station-kind | 33 | 35–36 |
| GLOBAL_READY (30 stations; 35 available after the °F exclusion, Astra D7) | ≈ 36 | ≈ 40–45 |
| end of 14-date observation phase | ≈ 50 | ≈ 55–60 |
| t0 (declared by Blue) | ≥ 50 | ≈ 55–60 |

The readiness design costs ≈ 3–4 weeks of calendar relative to "t0 = day 31" and converts the burn-in from a capture test into an informative phase.

### 5.4 Pre-t0 observation phase (outcome-free)

Once GLOBAL_READY holds, the frozen rule R* runs in **decision-only mode** for ≥ 14 target dates: eligibility, q, edges, chosen leg, price stratum, fills under REALISTIC and CONSERVATIVE, tier ledgers' NO_TRADE_CAPITAL counts, per-station trigger rates. Enforcement: the PNL engine is not deployed before t0, or it filters `t_entry ≥ t0` by code with a unit test; pre-t0 SIGNAL_DECISION rows carry `phase = PRE_T0` and invariant 5 (OUTCOME_ISOLATION) is extended to forbid any join of PRE_T0 decisions to SETTLEMENT rows for P&L purposes. What the phase yields without outcomes:

- triggers/day and fills/day by stratum and station → the 120-date trade forecast (replacing Astra's b = 0 proxy);
- the executable price mix → `σ_eff` and the Kish capital DEFF from `Var_0(N_j) = C_j² (1 − c_j)/c_j` (prices only);
- the tail-stratum share and `Λ_tail` per 120 dates (how many tail wins the null expects);
- from these, `θ_PCE = 2.486 × σ_eff × √(DEFF_declared / n_120)` and `SE(κ_core)`, to be frozen in the manifest before t0;
- criterion-7 depth statistics (≥ 25 USD within cap) without outcomes.

### 5.5 Missing days, corrections and readiness

| Event | Effect on USABLE / READY |
|---|---|
| missing T_entry vintage for (s, d) | d is permanently unusable for that station; BIAS_N reaches further back; BIAS_SPAN grows; READY delays until 30 usable dates fit in 40 |
| missing settlement-page capture | not fatal (the settled bucket comes from the market's final state); reconciliation coverage drops; counted in the ≥ 98% agreement denominator only if a parse was attempted |
| market held open for correction (≤ 7 d) | not FINAL → not usable until final; can delay that station's READY by up to 7 days |
| clarification changing a value after it was used | point-in-time principle: decisions that used the earlier value stand; later decisions use the corrected value from its availability time (append-only, `supersedes`); readiness counts a date only once FINAL |
| NO_DATA_LOWEST / WU_FALLBACK | usable under the frozen rule; flagged; the share of non-NOAA modes per station is a readiness report field (a station with > 10% non-NOAA modes in its window is READY but flagged) |
| station added to the table after capture day 1 | READY no earlier than its own day 33; enters the primary cohort at its first READY date under the frozen E8 (per-event), never leaves for readiness reasons; stations added after t0 remain EXPLORATORY_NEW_STATION |

### 5.6 Interaction with the MECHANICS_CHANGE stop (Astra D11 / S9)

The ≥ 50% ineligibility threshold must be computed against a baseline that excludes structural ineligibility (°F ladders, non-NOAA templates) and readiness ineligibility (E8), i.e. only reason codes that indicate a venue change (template change on a formerly NOAA station, ladder change, unit change, fee change, rule change). The pre-t0 phase supplies that baseline.

---

## 6. D8 — Dependence design

### 6.1 Structure

Trades sit in a **crossed** design: target date × station, each cell holding at most two legs (HIGHEST, LOWEST). Dates carry synoptic regimes (3–7 days) and a slow seasonal common mode; stations carry persistent bias-window errors across dates (the 30-day trailing mean lags a seasonal transition); trades per station are unequal (thin books fill rarely). A hierarchical (nested) bootstrap is the wrong tool for a crossed design.

### 6.2 Simulation evidence (SIMULATED; core-only legs to isolate dependence; 35 stations with gamma-distributed activity, 10–162 trades per station, Kish-effective station count 26.9; latent ρ_d = 0.05; 300 replications)

| latent ρ_s | SE ratio two-way / date-only | size: date-block PCT | date CR | **two-way CR** | max-of-three | pigeonhole two-way boot | κ date-only | κ two-way |
|---|---|---|---|---|---|---|---|---|
| 0.00 | 0.97 | 0.073 | 0.070 | 0.083 | 0.060 | 0.010 | 0.060 | 0.073 |
| 0.05 | 1.58 | **0.150** | **0.140** | 0.063 | 0.063 | 0.030 | **0.163** | 0.060 |
| 0.10 | 2.04 | **0.170** | **0.167** | 0.047 | 0.047 | 0.017 | **0.187** | 0.043 |

Power at ρ_s = 0.05: θ = 0.05 → two-way 0.42 (date-only 0.62 is inflated by its size distortion), pigeonhole 0.29; θ = 0.10 → two-way 0.85, pigeonhole 0.74; κ two-way 0.49 / 0.90.

Readings: the frozen date-only primary over-rejects three-fold at a station dependence of the size Astra assumes; the two-way sandwich holds size; the pigeonhole (product-weights) bootstrap is conservative by a factor of 2–5; when station dependence is absent, two-way costs nothing (SE ratio 0.97). A station SE inflation of 1.6–2.0 corresponds to a station DEFF of 2.5–4 on top of the date DEFF, inside Astra's range.

### 6.3 Recommendation

- **Primary**: two-way cluster-robust inference with dimensions **date-block** (5 consecutive target dates, non-overlapping for the sandwich; moving for the bootstrap) × **station (ICAO)**: the ratio-estimator linearisation `e_j = N_j − θ̂ C_j`, `SE² = (V_block + V_station − V_cell) / (Σ C)²` (Cameron–Gelbach–Miller two-way), reported together with the two-way studentised block bootstrap for the interval and the pre-declared rule **SE_reported = max(SE_date-block, SE_station, SE_two-way)** (in simulation the maximum coincides with two-way whenever station dependence exists and costs nothing when it does not: the SE ratio is 0.97 and the maximum then picks the date-only SE). Station-only inference is never used alone: with ≈ 27 effective clusters of unequal size it over-rejects (size 0.12 at ρ_s = 0, SIMULATED).
- **Cluster definitions**: date = the market's local target date D (stations span 20 time zones; the 5-date block absorbs the offset); station = ICAO from the frozen table; cell = (D, ICAO) containing both kinds; hemisphere × block as a sensitivity cluster for slow common modes.
- **Minimum cluster counts**: ≥ 60 target dates (≥ 12 blocks) and ≥ 25 traded stations with Kish-effective count ≥ 15; below either, the affected dimension is flagged UNRELIABLE and the reported SE is the maximum of the remaining valid dimensions inflated by a pre-declared small-cluster correction (CR3 / jackknife).
- **Effective-N reporting** (mandatory in the result file): n, D, S, Kish-effective S, `DEFF_date`, `DEFF_station`, `DEFF_two-way = SE²_two-way / SE²_iid`, `n_eff = n / DEFF_two-way`, information per date `1/(SE² D)`, ρ̂_d and ρ̂_s from the variance decomposition of the standardised residuals `(y_j − c_j)/√(c_j (1 − c_j))`, and the structural cap `D / ρ̂_d`.
- **Failure conditions**: two-way variance not positive semi-definite → use max of the one-way SEs; `DEFF_two-way > 6` (n_eff < ≈ 500) → INFORMATION_INSUFFICIENT validity flag; any single block contributing > 25% of `Σ e_block²` or any station > 20% → concentration flag (aligns with gate 18.6); ρ̂_s > 0.05 across a seasonal transition → report the first-half / second-half split as the likely bias-lag mechanism.
- **Sensitivity set** (pre-declared, reported, non-gating): block length {3, 5, 7, 10}; hemisphere × block; drop-one-station and drop-one-block jackknives; first half vs second half of the window; Rademacher vs Webb weights for the wild variant; percentile vs studentised vs BCa; PINM at ρ_decl × {0.5, 1, 2}; tail stratum in / out (descriptive only, not the estimand).

---

## 7. Cross-defect failure modes (attacks on the candidate repairs)

| ID | Interaction | Mechanism | Consequence | Mitigation in the recommended design |
|---|---|---|---|---|
| CD1 | Family A × seasonality × 30-day bias lag × venue drift | the edge has an annual cycle the 5-date blocks cannot see; templates changed twice in ≈ 6 months | a multi-year program is likely ended by MECHANICS_CHANGE before K windows; between-window variance eats degrees of freedom | not adopted; if the Architect insists, windows must be treated as random effects and K declared |
| CD2 | Sequential stopping × heavy tails | before the first tail win the empirical variance is understated (every tail leg has lost) and θ̂ is biased negative; after a win the information fraction jumps | false **futility** stop exactly when the rare wins have not yet arrived; misallocated α spending | never stop on θ; futility only on bounded κ_core / W_tail; information fraction from price-implied variance |
| CD3 | Sequential × few clusters | at 60 dates the two-way SE rests on 12 blocks and ≈ 27 effective stations; interim SE noise of ±20–30% | boundary computed on a wrong information fraction | at most one interim; O'Brien–Fleming-type spending (least sensitive); calendar-fixed looks |
| CD4 | PCE ≠ ERT | the design answers "is the edge large?" while the economics asks "is it ≥ 2¢?" | INDETERMINATE covers the economically relevant band; a decision system reading it as "no edge" or "edge" errs either way | labels name the band explicitly; the CI is the product; sizing decisions on an INDETERMINATE result belong to a decision-theoretic rule (shrinkage), outside this protocol |
| CD5 | Station filtering (°F exclusion, readiness gating) × two-way inference | ≈ 35 stations, Kish-effective ≈ 27 | station dimension marginal; tier ledgers Asia-weighted (Astra D12) | minimum effective-station rule with fallback; tier θ reported separately from S_ref θ |
| CD6 | Heavy-tail handling × estimand | winsorising / trimming / exclusion silently changes θ; κ is a constant-payout return, not the frozen strategy's return | a "robust θ" reported as θ is a different strategy's result | θ untouched; κ labelled as information / constant-payout; strata by venue tick, never by outcomes |
| CD7 | Pooled κ gatekeeper × tail-concentrated edge | κ_true 0.004 at θ_true 0.32 | a real tail edge blocked at the gate 88% of the time | stratified gate: κ_core **or** W_tail (each at α/2) |
| CD8 | PINM × dependence declaration | PINM is exact only under the declared copula; declaring independence gives size 0.13 (κ) / 0.21 (core θ) | anti-conservative test | declare ρ_d, ρ_s before t0 (ASSUMED, conservative), sensitivity ×0.5/×2, and require the empirical two-way engine to agree; an outcome-free estimate of the spatial correlation of *forecast errors* from burn-in settlements is possible but is weather-outcome data, a grey zone the Architect must rule on |
| CD9 | CONSERVATIVE execution (+0.01 flat) × tail legs | +0.01 on a 0.001 ask is an 11× cost | gate criterion 2 fails mechanically whenever tail legs matter, independent of edge | slippage = one venue tick in the applicable regime (execution-model change, outcome-blind) |
| CD10 | Readiness-gated t0 × clock | the frozen t0 = day 31 counts 3–5 empty dates; readiness-gated t0 adds ≈ 3–4 weeks | calendar cost vs. information deficit | accept the calendar; the observation phase pays for it with an outcome-free PCE |
| CD11 | Fixed 120-date analysis × pessimistic throughput (13/day) | n ≈ 1,560 → SE(κ_core) ≈ 0.02, PCE(θ) ≈ 0.11–0.30 | a screen that only sees edges > 10–30¢/$ | the pre-t0 PCE is a go/no-go input for Blue: if PCE > a declared ceiling, the experiment is not worth running as designed (an honest stop, not a failure) |
| CD12 | Two-way sandwich × a single tail win | one (date, station) cell holds a 1,000× residual | leverage point; studentised interval unstable | stratified reporting; PINM as the test engine; the tail stratum's P&L interval is model-based (parametric bootstrap under the fitted tail multiplier `λ̂ = W_tail / Λ_tail`) and labelled as such |
| CD13 | Attribution criterion 9 (beats B4/B5 by ≥ 0.02) × SE 0.03–0.1 | a difference of two noisy θ's | no inferential content | compare on κ_core / W_tail; keep the θ comparison descriptive |
| CD14 | Futility look on κ_core × stratum share | if the core stratum is small (many tail triggers), κ_core has little information at 60 dates | premature NEGATIVE_INFORMATION | futility requires both κ_core significantly negative **and** the tail-count upper bound below Λ_tail |

---

## 8. Recommended architecture for the Architect to CONSIDER (advisory)

**Name**: stratified two-estimand fixed-horizon design with price-implied null inference and readiness-gated t0 (Family D, configured).

### 8.1 Components

1. **Trading rule**: R* exactly as frozen (no change to M, W, σ_dress, h, T_entry, model, S_ref, tiers). Two outcome-blind non-rule decisions are recommended alongside: CONSERVATIVE slippage = one venue tick; explicit °F cohort decision (Astra D7).
2. **Estimands**: θ pooled (economic, primary); θ_core, θ_tail (reported); κ_core and W_tail vs Λ_tail (information, confirmatory). Strata by the venue tick regime at T_entry.
3. **Thresholds**: `θ_ERT = 0.02` (reporting only); `θ_PCE` and `SE(κ_core)_expected` computed from prices in the pre-t0 observation phase at DEFF = 3 and frozen in the manifest. Declared dependence for PINM: ρ_d, ρ_s (ASSUMED; suggested 0.05 / 0.05 with ×0.5, ×2 sensitivities), frozen before t0.
4. **Tests**: T1 = {T1a: κ_core > 0; T1b: E[W_tail] > Λ_tail}, each at α = 0.025, gate passes if either rejects; T2: θ > 0 at α = 0.05 only if T1 passes. Each test rejects only if PINM **and** the two-way studentised block bootstrap both reject.
5. **Dependence**: two-way (date-block × station) primary; max-of-three SE; effective-N reporting; failure rules (section 6.3).
6. **Horizon**: readiness-gated t0 (section 5); 120 complete target dates fixed (no 90-date option); analysis 3 days after the last date; one optional futility-only look at 60 dates on T1 (CD14 rule); no efficacy stopping; nothing on θ.
7. **Gates for the economic label** (kept from the frozen spec, applied only after T2 rejects): CONSERVATIVE point estimate > 0 (with tick-aware slippage); concentration (18.6); operational accessibility (18.7) reported as an orthogonal flag, never pre-empting the scientific label (Astra D5); capital efficiency (18.8) reported.
8. **Validity flags** (orthogonal, always reported): VALID / INVALID (leakage, mutation, data failure); INFORMATION_INSUFFICIENT if `SE(κ_core) > 0.02` or `DEFF_two-way > 6`; ACCESSIBLE / INACCESSIBLE.

### 8.2 Terminal partition (complete and mutually exclusive; evaluated in this order)

| Order | Condition | Scientific label |
|---|---|---|
| 1 | T1 not passed and `U95(κ_core) < 0` (or futility stop) | NEGATIVE_INFORMATION (the market beats the forecast on the rule's legs) |
| 2 | T1 not passed, otherwise | NO_INFORMATION_DETECTED (sub-flag LARGE_EDGE_EXCLUDED if `U95(θ) < θ_PCE`) |
| 3 | T1 passed and `U95(θ) < θ_ERT` | INFORMATION_CONFIRMED_NET_VALUE_EXCLUDED (information exists; costs consume it) |
| 4 | T1 passed, `L95(θ) > 0`, gates pass | INFORMATION_CONFIRMED_NET_VALUE_CONFIRMED (the only state that could ever justify a next phase; still paper/shadow) |
| 5 | T1 passed, `L95(θ) > 0`, a gate fails | INFORMATION_CONFIRMED_NET_VALUE_NOT_ROBUST (naming the gate) |
| 6 | T1 passed, `L95(θ) ≤ 0`, `U95(θ) ≥ θ_ERT` | INFORMATION_CONFIRMED_NET_VALUE_INDETERMINATE (the CI, `θ̂`, `θ̂_core`, `θ̂_tail` are the result; "REQUIRES_MORE_DATA" is retired) |

Every combination of (T1, sign of L95(θ), U95(θ) vs θ_ERT, gates) maps to exactly one row; validity and accessibility are flags beside the label, not labels.

### 8.3 What the recommended design can and cannot conclude

- Can: whether R*'s chosen legs are mispriced in its favour (well-powered, tail-immune, with a real negative result); whether a large net edge (≥ θ_PCE) exists after realistic frictions; an honest interval for θ with a price-stratum decomposition; how much of any edge sits in lottery legs; the effective information actually collected.
- Cannot: confirm or reject an edge in [0.02, ≈ 0.06] per dollar; that band is reported as INDETERMINATE with its interval. This limit is set by the venue's daily event count and the within-date dependence, not by the analysis.

### 8.4 Decisions the Architect must take outcome-blind before any burn-in

1. Adopt / reject the stratified two-estimand structure and the label partition (8.2).
2. Freeze the stratum definition (venue tick regime) and the PINM dependence declaration.
3. Decide the °F cohort (Astra D7), the E6 book-window fix on `captured_at` (D3), the tick-aware CONSERVATIVE slippage, and whether non-NOAA modes stay in the bias term (D10; a rule decision).
4. Decide whether the 60-date futility look exists.
5. Declare a PCE ceiling above which Blue should decline to start (CD11).
6. Re-freeze the manifest with new hashes; re-audit independently.

### 8.5 Largest unresolved scientific risk

The economically relevant band θ ∈ [0.02, ≈ 0.06] per dollar is **structurally unresolvable** at this venue's throughput in any 120-date design; the recommended architecture makes that band honest, not smaller. If Quant needs to *act* on such an edge, the answer is not a longer falsification test but a pre-declared decision rule that sizes paper capital from the interval (shrinkage toward zero), which is a Capital-Desk design question outside this protocol. The second-largest risk is CD8: the PINM engine's exactness depends on a dependence structure that can only be declared, not measured, without touching outcome data.

---

## 9. Reproduction notes (SIMULATED components)

Scripts were kept in the challenger's session scratchpad (`power.py`, `tailsim.py`, `tailedge.py`, `twoway.py`, `grid.py`) and are not committed, matching the one-file deliverable scope. All inputs are stated here; any reader can re-implement them:

- Analytic tables: `N = (2.486 σ/θ)²`; `SE = σ √(DEFF/n)`; gate probabilities by normal approximation; group-sequential boundaries by numerical recursion on a 3,201-point grid with the one-sided spending function `α(t) = 1 − Φ(1.645/√t)`.
- Heavy-tail simulation: D = 90, m = 30, 300 replications, 300 bootstrap / null draws, seeds 20260929 and 7; price mix and copula as stated in 4.2; block length 5; PINM draws share the copula with the data-generating process except in the mis-declaration rows.
- Dependence simulation: 35 stations, activity weights gamma(2, 1), 300 replications, seed 11; two-way sandwich on non-overlapping 5-date blocks; pigeonhole bootstrap with multinomial weights on blocks and stations.

No market, forecast, book, settlement or wallet endpoint was called by this challenger.

---

## 10. Anti-leakage and scope statement

- No outcome, P&L, winner, settlement, wallet, leaderboard or price-history data was read. The frozen spec, the freeze manifest, the architect state and the Astra review were read at the exact commits named in the header and were not modified.
- No trading-rule parameter was tuned, varied or recommended for change; every effect size was analysed as a hypothetical.
- This memo does not create the Weather V2 specification, does not modify the freeze, does not declare feasibility, does not authorise the Builder and does not declare t0.

```text
DESIGN_CHALLENGE         = DONE_ADVISORY
RECOMMENDED_FOR_CONSIDERATION = Family D (stratified two-estimand, PINM + two-way inference, readiness-gated t0, honest labels)
NEXT_ACTOR               = Weather Architect (decides; then independent re-audit; then Builder)
REAL_CAPITAL_AUTHORIZED  = FALSE
t0                       = NOT_DECLARED
```
