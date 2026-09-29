# ASTRA — WEATHER FORWARD EXPERIMENT FEASIBILITY REVIEW — 2026-09-29

```text
REVIEW_ROLE              = independent experiment-feasibility reviewer (read-only on the audited spec)
AUDITED_BRANCH           = claude/intelligent-gates-msidml
AUDITED_COMMIT           = 726070a199957a6fc05515ebb3027e945028fddc
AUDITED_FILES            = WEATHER_FORWARD_FALSIFICATION_SPEC_2026-09-29.md
                           WEATHER_FORWARD_FREEZE_MANIFEST_2026-09-29.md
                           WEATHER_FORWARD_ARCHITECT_STATE_2026-09-29.md   (none modified)
REAL_CAPITAL_AUTHORIZED  = FALSE
t0                       = NOT_DECLARED
EXPERIMENT_FEASIBILITY   = BLOCKED_POWER_BELOW_DECLARED_MEUE
SECONDARY_BLOCKERS       = STATE_MACHINE_GAPS; E6_BOOK_TIMESTAMP_COMPLETENESS; E8_BURN_IN_BOOTSTRAP; E4_EXCLUDES_ALL_US_STATIONS
HURDLE_SAMPLE_INCOMPATIBILITY = FALSE   (at h = 0.10 the 1,000-fill sample is reached well inside 60 dates)
CALENDAR                 = CALENDAR_FEASIBLE for sample counts, conditional on the E6 timestamp defect being repaired
STATUS                   = DONE
```

Epistemic labels: **MEASURED** (pre-outcome public API data captured by this reviewer on 2026-09-29), **DERIVED** (arithmetic on measured values or on the frozen spec), **ASSUMED** (declared scenario range; no data available without outcomes).

---

## 1. Executive verdict

The frozen design is **operationally able to generate its target sample** (at h = 0.10 the rule fires on roughly 40–65% of eligible °C events, ≈ 27–44 triggers/day, essentially all of them producing a ≥ 5-share REALISTIC fill), but it is **statistically unable to answer the economic question it declares**:

1. **θ_MEUE = 0.02 is structurally undetectable.** Even with zero dependence, the most favourable measured return dispersion (SD ≈ 1.0) and 100% triggering of every eligible event for 120 dates (≈ 8,400 trades), 80% power at θ = 0.02 needs ≈ 15,500 independent trades. With realistic dependence (DEFF 2–4) the requirement is 31k–62k (SD 1.0) or 260k–520k (SD 2.9, measured when sub-5¢ "lottery" legs are included). No throughput repair can close this inside 120 target dates.
2. **The realistic minimum detectable effect (80% power, one-sided α = 0.05) is ≈ 0.06–0.10 per dollar committed** if lottery legs are negligible, and **≈ 0.16–0.28** if they occur at the measured rate. The spec's own §5 statement (confirmable edges only ≳ 0.10–0.13) is directionally honest but uses a per-trade SD (1.2) that the measured trigger mix does not support in either direction.
3. The terminal-state logic has **undefined regions** that are reachable with non-trivial probability, and a precedence rule that can label a clearly losing rule `OPERATIONALLY_INACCESSIBLE` instead of `REJECTED`.
4. Two **procedural** defects can invalidate the run before any science happens: the E6/invariant-11 book-timestamp window (the CLOB `timestamp` is the book's last-change time, not the observation time — ≈ 1/3 of weather tokens are older than 5 min at any instant), and a 30-day burn-in that cannot deliver 30 *prior resolved* archived dates at t0.
5. A cohort defect: US markets use **2 °F-wide buckets**, which fail frozen E4 ("nine single-degree buckets"). All 11 °F stations (22 events/day) are ineligible, exploratory E13 is empty by construction, and MIN_STATIONS = 30 must be met from ≈ 35 remaining NOAA °C stations.

`EXPERIMENT_FEASIBILITY = BLOCKED_POWER_BELOW_DECLARED_MEUE`. F7 (no outcome tuning) passes. F1 and F4 pass conditionally; F2, F3, F5 and F6 fail.

---

## 2. Measurement basis (pre-outcome only)

| Dataset | What | When (UTC) | Size |
|---|---|---|---|
| X1 cross-section | All open NOAA-template temperature events for target date 2026-09-30: live CLOB books (22 tokens each) + live Open-Meteo `ecmwf_ifs025` 51-member forecast at the station (OurAirports coordinates, `timezone=auto`); frozen R* applied with b = 0 (bias history does not exist yet) | 16:37–16:50, 2026-09-29 | 80 events (60 °C / 20 °F), 41 stations; lead to T_entry −8.4 h … +11.6 h (26 events within ±2 h) |
| X2 exact T_entry | Collector capturing forecast at T_entry − 60 min (or first opportunity inside [T_entry − 3 h, T_entry]), books at T_entry − 100 s and at T_entry + 5 min | London, target 2026-09-30 (T_entry 17:00) | 2 events |
| X3 book-timestamp probe | `POST /books` and `GET /book` on weather tokens; age = wall clock − CLOB `timestamp` | 16:4x, 2026-09-29 | 180 + 120 tokens |
| X4 cohort census | Gamma `events?tag_slug=weather&closed=false` | 16:3x, 2026-09-29 | 370 events, 284 temperature events, 52 cities |

Scope limits: X2 was intended to run ≥ 24 h to cover every station once at its exact T_entry; it was stopped after the first station on the project owner's instruction to finalise without further sampling. X1 is therefore the throughput basis; it evaluates each event at its current lead, not exactly at T_entry, and with b = 0 instead of the frozen 30-day point-in-time bias. Both limitations are carried as ranges below. **No settlement, resolution, price-history, P&L or wallet endpoint was read.** Only closed-market-free `closed=false` listings were used.

---

## 3. Cohort census (MEASURED, X4)

| Item | Value |
|---|---|
| Temperature events currently open (3 target dates) | 284 |
| NOAA-WRH template | 270 (204 °C, 66 °F) |
| Non-NOAA (HKO, WU) | 14 |
| °C NOAA ladders = 11 legs, 9 single-degree mids | 204 / 204 |
| °F NOAA ladders | 66 / 66 use **2 °F buckets** (`86-87°F`, …) → fail E4 as frozen |
| NOAA °C stations | ≈ 35 → ≈ 70 E1–E5-eligible events/day before E6/E8 |

---

## 4. Trigger-rate audit (Audit B)

Frozen rule R*, h = 0.10, 22 legs, fee 0.05·a(1−a), tie rule as frozen; b = 0 (explained above).

| Stage | °C (E4-eligible) | °F (E4-ineligible, shown for information) |
|---|---|---|
| Events evaluated | 60 | 20 |
| E_max ≥ 0.10 (triggers) | **38 (63%)** | 14 (70%) |
| Triggers with E_max ≥ 0.20 (robust to moderate bias shifts, heuristic) | 24 (40%) | 7 |
| Non-zero REALISTIC fill (≥ 5 shares within best ask + 0.02) | **38 / 38** | 13 / 14 |
| Full 50 USD fill (S_ref) | 26 / 38 (68%) | 8 / 14 |
| Depth within cap ≥ 25 USD (500-tier stake; gate criterion 7) | **29 / 38 (76%)** | 9 / 14 |
| Median REALISTIC notional | 50 USD | 50 USD |
| Stations with ≥ 1 fill (one target date) | 30 of 35 | 11 |
| Leg mix | 30 NO / 8 YES; 29 HIGHEST / 9 LOWEST; 6 legs with ask < 0.05 | |

X2 (exact T_entry, London, target 2026-09-30): both events triggered at b = 0 (E = 0.155 LOWEST, 0.130 HIGHEST), both FULL at 50 USD under REALISTIC and CONSERVATIVE. Under a ±2 °C bias grid the HIGHEST trigger persisted at every b; the LOWEST trigger did not — the bias term can remove triggers, which is why the lower end of the range below is wide.

**Bias caveat.** The 29/9 HIGHEST/LOWEST skew at b = 0 is consistent with an unremoved systematic Tmax offset (raw ensemble vs airport sensor). The frozen 30-day bias will remove part of that disagreement, so b = 0 most likely **overstates** triggers. The E ≥ 0.20 subset (40%) is used as the conservative case and a 20% trigger rate as a pessimistic floor.

| Quantity | Pessimistic | Conservative | Central |
|---|---|---|---|
| Eligible °C events/day after 95% completeness | 66 | 66 | 66 |
| Trigger rate | 20% | 40% | 63% |
| **TRIGGERS_PER_DAY** | ≈ 13 | ≈ 27 | ≈ 42 |
| **FILLED_TRADES_PER_DAY** (REALISTIC, ≥ 5 shares) | ≈ 13 | ≈ 27 | ≈ 42 |
| CONSERVATIVE non-zero fills/day | ≈ 12 | ≈ 25 | ≈ 40 (50% haircut rarely drops below 5 shares; +0.01 slip does not change fill existence) |
| **STATIONS_PER_30D** | ≥ 30 likely | 30–35 | 33–35 |

---

## 5. Calendar arithmetic (Audit C)

DERIVED from §4:

| | Pessimistic (13/d) | Conservative (27/d) | Central (42/d) |
|---|---|---|---|
| days_to_1000_trades | ≈ 77 | ≈ 37 | ≈ 24 |
| trades in 60 d | ≈ 780 | ≈ 1,620 | ≈ 2,520 |
| trades in 90 d | ≈ 1,170 | ≈ 2,430 | ≈ 3,780 |
| trades in 120 d | ≈ 1,560 | ≈ 3,240 | ≈ 5,040 |

- ≥ 60 target dates and ≥ 1,000 fills: met in the conservative and central cases; the pessimistic case reaches 1,000 between dates 60 and 120.
- ≥ 30 distinct stations: 30 of 35 on one date at b = 0; very likely over 60 dates, with only ~5 stations of margin because of the E4 °F exclusion.
- ≥ 95% completeness: **not achievable under the literal E6/invariant 11** (§8, D3). Achievable in principle if the window is tested on capture time.

**Classification: CALENDAR_FEASIBLE** (sample counts), **conditional on D3**. Under the literal spec the classification is CALENDAR_INFEASIBLE through completeness, not throughput. `HURDLE_SAMPLE_INCOMPATIBILITY = FALSE`: at h = 0.10 the minimum sample is **not** the binding constraint; MIN_DURATION = 60 dates is, and MIN_SAMPLE = 1,000 becomes a non-binding floor.

---

## 6. Power audit and dependence (Audits A, D)

### 6.1 Per-trade dispersion (DERIVED from the measured leg mix, no outcomes)

For a leg bought at all-in cost c per share, r = N/C is −1 or (1−c)/c; near θ ≈ 0, SD(r) ≈ √((1−c)/c). The ratio-of-means estimator weights by C_j, so the effective SD is σ_eff² = n·Σ C_j² SD_j² / (Σ C_j)².

| Trigger set (X1, °C) | n | σ_eff | Kish weight DEFF | Unweighted mean SD |
|---|---|---|---|---|
| All triggers | 38 | **2.93** | 1.20 | 3.77 |
| Excluding asks < 0.05 | 32 | **0.96** | 1.06 | 0.92 |

The rule mainly buys NO on the market-favoured middle bucket (ask 0.4–0.8, SD 0.5–1.2) plus occasional sub-5¢ YES legs (asks 0.001–0.04) where the dressed ensemble puts ≥ 10% on a bucket the book prices near zero. These legs are small in capital but have SD 5–30 and dominate variance. The spec's σ = 1.2 is neither the no-lottery value (≈ 1.0) nor the measured all-trigger value (≈ 2.9).

### 6.2 Dependence (ASSUMED ranges; not measurable without outcomes)

| Source | Mechanism | DEFF contribution (range) |
|---|---|---|
| Target date | ≈ 27–42 trades/date; shared synoptic regimes; the rule takes the same structural position (NO on the favoured bucket) everywhere, which creates common-mode exposure to any date-level market-calibration shift | ρ_d 0.01–0.05 → 1 + (m−1)ρ_d = 1.3–3.1 |
| Station | ≈ 45–150 trades per station over 60–120 dates; a 30-day trailing bias lags seasonal drift (the window deliberately spans an autumn/spring transition) | ρ_s 0.005–0.02 → 1.2–4 (**not captured by the primary date-block bootstrap**) |
| Highest/Lowest same station-date | Both legs can trade; same airmass and bias error | absorbed in the date and station terms |
| Weather-system (multi-day) | Regimes of 3–7 days; slower seasonal common mode across one hemisphere | 5-date blocks capture the first, not the second |
| Unequal capital | Partial fills (32% of triggers below 50 USD) | Kish 1.06–1.20 |

Working range: **DEFF_total ≈ 2–4** (central 3), before any heavy-tail penalty. Structural cap: with m trades per date, n_eff ≤ D/ρ_d. At ρ_d = 0.03, n_eff ≤ 1,800 (60 d) or 3,600 (120 d) no matter how many trades are taken.

### 6.3 Required samples and detectable effects (one-sided α = 0.05, power 0.80)

N_NAIVE (independent trades required):

| θ | σ = 1.0 | σ = 2.0 | σ = 2.9 |
|---|---|---|---|
| 0.02 | 15,457 | 61,827 | 129,991 |
| 0.05 | 2,473 | 9,892 | 20,799 |
| 0.10 | 618 | 2,473 | 5,200 |

N_EFFECTIVE requirement → trades required = N_NAIVE × DESIGN_EFFECT:

| θ | σ 1.0, DEFF 2 | σ 1.0, DEFF 4 | σ 2.9, DEFF 2 | σ 2.9, DEFF 4 |
|---|---|---|---|---|
| 0.02 | 30,913 | 61,827 | 259,982 | 519,964 |
| 0.05 | 4,946 | 9,892 | 41,597 | 83,194 |
| 0.10 | 1,237 | 2,473 | 10,399 | 20,799 |

Hard ceiling: ≈ 70 eligible events/day × 120 dates ≈ 8,400 trades at a 100% trigger rate.

Minimum detectable effect (80% power) for achievable trade counts:

| Trades | σ 1.0 DEFF 2 | σ 1.0 DEFF 4 | σ 2.9 DEFF 2 | σ 2.9 DEFF 4 |
|---|---|---|---|---|
| 1,000 (spec minimum) | 0.111 | 0.157 | 0.322 | 0.456 |
| 1,620 (60 d conservative) | 0.087 | 0.124 | 0.253 | 0.358 |
| 3,780 (90 d central) | 0.057 | 0.081 | 0.166 | 0.234 |
| 5,040 (120 d central) | 0.050 | 0.070 | 0.143 | 0.203 |
| 8,400 (120 d, 100% trigger) | 0.038 | 0.054 | 0.111 | 0.157 |

**Smallest effect the design can realistically detect: θ ≈ 0.06–0.10 without lottery legs; ≈ 0.15–0.25 with them.** θ = 0.02 cannot be confirmed in the permitted window under any throughput.

### 6.4 The pathological outcome exists (Audit D)

Normal approximation of the §18 gate at SE = 0.054 (spec's own 1,000-trade figure). Criteria 6, 7 and 9 are assumed to pass and the CONSERVATIVE check is ignored, so these are upper bounds on FORWARD_SIGNAL:

| True θ | FORWARD_SIGNAL | REJECTED | NOT_PROVEN | REQUIRES_MORE_DATA (if at max duration) |
|---|---|---|---|---|
| −0.05 | 0.005 | 0.36 | 0.54 | 0.09 |
| 0.00 | 0.05 | 0.10 | 0.54 | **0.31** |
| 0.02 (= MEUE) | **0.10** | 0.05 | 0.45 | 0.40 |
| 0.05 | **0.24** | 0.01 | 0.28 | 0.47 |
| 0.10 | 0.58 | 0.00 | 0.07 | 0.35 |

At SE = 0.03 (≈ 3,000–4,000 trades, σ ≈ 1.0, DEFF ≈ 3): θ = 0.05 → FORWARD_SIGNAL 0.51, NOT_PROVEN 0.16, RMD 0.33.

Characterisation: a true edge of 2–5¢ per dollar (2.5–13× the declared MEUE, and worth ≈ 250–650 USD/month at the 1,000 tier) returns NOT_PROVEN or REQUIRES_MORE_DATA **76–90% of the time**. Meanwhile a **zero-edge rule is labelled REQUIRES_MORE_DATA 31% of the time** and REJECTED only 10%. The design answers "is θ ≥ ~0.10?" while its declared estimand, MEUE, economic rationale (§5, ≈ 200 USD/month at θ = 0.02) and REJECTED criterion (U95 < 0.02) are all calibrated to "is θ ≥ 0.02?". The outcome labels therefore systematically read as "maybe" for exactly the economically interesting region.

### 6.5 Execution drag on the gate

X2 London: CONSERVATIVE all-in average cost exceeds REALISTIC by 2.6–5.6% per share. Hence θ_CONS ≈ θ_REAL − (0.03 to 0.06) for mid-price legs, and far worse for sub-5¢ legs (+0.01 on a 0.001 ask is an 11× cost). Gate criterion 2 (θ̂_CONS > 0) therefore requires θ_REAL ≳ 0.03–0.06 in practice, which makes the MEUE even less reachable.

---

## 7. Execution / depth feasibility (Audit F)

| Metric (°C triggers, X1) | Value |
|---|---|
| Fraction fillable (≥ 5 shares, REALISTIC) | 100% (38/38) |
| Full S_ref = 50 USD fill | 68% |
| Median executable size within cap | 50 USD (capped); depth-within-cap median ≈ 210 USD |
| Depth-constrained (< 50 USD within cap) | 32% |
| Depth ≥ 25 USD (criterion 7 metric) | **76%, below the 80% threshold** (95% CI ≈ 60–89%) |
| Station concentration | Thin books (< 25 USD within cap) concentrated in Wellington, Manila, Chongqing, Wuhan, Chengdu, Shanghai-LOWEST and Zhengzhou (mostly the sub-5¢ YES legs); deep books (> 3,000 USD) in Tel Aviv, Shanghai (HIGHEST), Guangzhou, Jeddah, Karachi, Qingdao |

Depth alone does **not** make 1,000 fills impossible. It does make **gate criterion 7 marginal**. Because OPERATIONALLY_INACCESSIBLE is evaluated before REJECTED, depth can decide the terminal label independently of the edge (D5).

Capital: at the 1,000 tier (stake 50, open ≤ 1,000 → ≤ 20 concurrent legs, τ ≈ 2.3 d), demand is ≈ 60–100 concurrent legs. Tier ledgers are therefore capital-bound, and in T_entry order they systematically favour Asia-Pacific stations. The tier sample is a different selection from the S_ref sample. This is not a validity defect, but tier θ must not be read as S_ref θ.

---

## 8. Burn-in feasibility (Audit G)

**The bootstrapping problem exists.**

- The decision for target date D at T_entry = 18:00 local on D−1 can only use dates already resolved, i.e. ≤ D−2 (date D−1 resolves after local midnight at the earliest, up to 23:59 ET on D). A station therefore needs archived T_entry vintages for 30 dates ending at D−2.
- If capture starts on day 1, the first archived T_entry is for D = 2, and the 30th usable prior date is D = 31. The first E8-eligible target date is **D = 33 at 100% completeness**, ≈ 34–35 at 95% completeness, and later for stations with clustered outages, 7-day correction holds or disputes.
- With a 30-day burn-in and t0 on day 31, the first ≈ 2–5 forward target dates are fully or partly INELIGIBLE(bias_history). They still count toward the 60/120-date clocks while yielding few or no trades.
- **The frozen rule's trigger rate cannot be observed during a 30-day burn-in at all**, because no station has a complete bias history before day ≈ 33. Only the b = 0 variant (E7) is observable, and §4 shows it likely overstates triggers. The burn-in cannot "observe enough trigger-rate data to forecast forward feasibility".
- Settlement-parser ≥ 98% over ≥ 30 days and capture completeness ≥ 95%: feasible if D3 is repaired; otherwise completeness fails.
- ≥ 30 stations: feasible from ≈ 35 °C NOAA stations. A city added during burn-in cannot reach 30 prior dates, and cities added after t0 are EXPLORATORY_NEW_STATION.
- Side note (not feasibility): a `NO_DATA_LOWEST` settlement enters the bias mean as the lower tail boundary, a non-meteorological value that can shift b by (tail − true)/30.

---

## 9. State-machine audit (Audit H)

Evaluation order per §18: FORWARD_SIGNAL (all nine criteria) → OPERATIONALLY_INACCESSIBLE → REJECTED → NOT_PROVEN → REQUIRES_MORE_DATA.

| # | Region | Result |
|---|---|---|
| S1 | Sample not met at max duration, L95 > 0, θ̂ ≥ 0.02 (strong but under-sampled) | FS fails c4; RMD requires L95 ≤ 0; NOT_PROVEN requires sample met → **UNDEFINED** |
| S2 | Sample not met at max duration, θ̂ < 0.02, and REJECTED clause 2 not fully met (e.g. θ̂ ∈ [0, 0.02), or B2 shows skill) | **UNDEFINED** |
| S3 | Sample met, L95 > 0, θ̂ ≥ 0.02, but c2 (CONSERVATIVE ≤ 0), c5 (L80 < 0.01) or c8 fails | NOT_PROVEN requires L95 ≤ 0 (under either parse) → **UNDEFINED**. Reachable: e.g. θ̂ = 0.02, SE = 0.01 gives L95 > 0 but L80 < 0.01 (≈ 4–25% of runs in the simulation above) |
| S4 | Sample met, L95 ≤ 0, θ̂ ≥ 0.02, c6 and c9 hold, analysis before max duration (the "target 90 dates" case) | RMD requires max duration → **UNDEFINED**. It is also not stated whether analysis occurs at 90 or 120 dates once the minimum is met: an analyst degree of freedom (optional stopping) |
| S5 | NOT_PROVEN wording "…and at least one of criteria 6 or 9 fails, or θ̂ < θ_MEUE" | Operator precedence ambiguous: does "or θ̂ < θ_MEUE" bypass "sample met, L95 ≤ 0"? |
| S6 | REJECTED clause 2 (θ̂ < 0, U95 < 0.02, B2 no skill) | When the sample is met it is a strict subset of clause 1 (U95 < θ_MEUE = 0.02). It is only active when the sample is **not** met, and it is unclear whether that is intended |
| S7 | Clearly losing rule (U95 < 0) with criterion 7 failing (≈ 24% of triggers < 25 USD depth, measured) | Labelled **OPERATIONALLY_INACCESSIBLE**, not REJECTED — misleading |
| S8 | Zero-edge rule at max duration | REQUIRES_MORE_DATA ≈ 31% (SE 0.054). The label implies promise where none exists |
| S9 | MECHANICS_CHANGE threshold (≥ 50% ineligible for 14 dates) | Structural ineligibility is already ≈ 28% (22 °F + ≈ 4 non-NOAA of ≈ 94). Early-window E8 ineligibility adds more, so headroom before a false MECHANICS_CHANGE is ≈ 22 points |

No overlap produces a contradiction once the evaluation order is applied. The defects are **gaps (S1–S4)**, **ambiguity (S5, S6, S4 timing)** and **misleading precedence/labels (S7, S8)**.

---

## 10. Defects (ranked)

| ID | Severity | DEFECT | WHY IT MATTERS | MINIMUM TYPE OF CHANGE REQUIRED |
|---|---|---|---|---|
| D1 | **CRITICAL** | θ_MEUE = 0.02 is undetectable within 120 dates. Even the 100%-trigger ceiling (≈ 8,400 trades) is below the ≈ 15.5k independent trades needed at the most favourable σ; realistic MDE is 0.06–0.10 (0.15–0.25 with lottery legs) | The experiment cannot answer its declared economic question. Useful edges are mostly labelled NOT_PROVEN / REQUIRES_MORE_DATA | Pre-registration change, outcome-independent: either (a) declare the estimand the design can actually test (the MDE at the achievable n under a stated DEFF) and re-derive the REJECTED threshold and economic rationale to match, or (b) replace the fixed-window design with a pre-declared sequential / longer-horizon design whose maximum sample is sized from the power calculation. Must be decided before t0 without any forward data |
| D2 | **CRITICAL** | Terminal-state gaps S1–S4 and the unpinned analysis date (90 vs 120) | Reachable outcomes have no label; the choice of analysis date is a post-hoc degree of freedom | Procedural: complete the state partition (every combination of sample-met × L95 × θ̂ × criteria maps to exactly one state); fix the analysis date as a frozen constant |
| D3 | **CRITICAL** (operational) | E6 / invariant 11 test `book_timestamp ∈ [T_entry − 5 min, T_entry]` for all 22 tokens. The CLOB `timestamp` is the last-change time (measured: ≈ 28–33% of weather tokens > 5 min old; London LOWEST at T_entry had 36% stale tokens) | Quiet books make events MISSING; completeness ≥ 95% is unreachable, leading to DATA_FAILURE pauses and an INVALID run | Procedural: test the window on `captured_at`, and require `book_timestamp ≤ captured_at ≤ T_entry` |
| D4 | **MAJOR** | Per-trade SD in §5 (1.2) is not the measured mix. Sub-5¢ YES legs (≈ 16% of triggers) raise σ_eff to ≈ 2.9 and make θ̂ extremely skewed (a single 0.001-ask win can pay ~1,000× its stake). Percentile block-bootstrap intervals with 12–24 blocks are unreliable in this regime | The power statement is misstated, and the primary interval can be anti-conservative or unstable | Statistical/procedural: restate power from the executable leg mix; pre-declare an interval method valid for heavy-tailed ratios with few clusters (e.g. studentised or BCa block bootstrap, or a leg-price-stratified analysis). Any change to the *trading rule* to exclude such legs is a strategy change and outside this review |
| D5 | **MAJOR** | OPERATIONALLY_INACCESSIBLE precedes REJECTED, and criterion 7 is marginal (76% measured vs 80% required) | A losing rule can exit as "inaccessible", which hides a falsification | Procedural: evaluate REJECTED (edge excluded) independently of accessibility, or report both labels |
| D6 | **MAJOR** | 30-day burn-in cannot supply 30 prior *resolved* archived dates at t0 (first E8-eligible date ≈ day 33–35), and cannot observe the frozen rule's trigger rate before t0 | Early forward dates burn the clock with no trades; the feasibility forecast rests on the b = 0 proxy | Procedural: define burn-in as "until every station in the table has ≥ W resolved archived dates, or N days", plus a pre-t0 trigger-rate observation period on the frozen rule |
| D7 | **MAJOR** | E4 excludes all US 2 °F-bucket ladders (22 events/day, 11 stations). §6 and §15 E13 assume °F single-degree buckets | ≈ 24% of the cohort is lost, E13 is empty, and MIN_STATIONS must come from ≈ 35 stations | Cohort-definition decision before t0: either declare °F ineligible explicitly (and drop E13) or define 2-degree bucket arithmetic. Either is outcome-independent |
| D8 | **MAJOR** | The primary bootstrap is date-block only. Station-level persistence (trailing-bias lag through a seasonal transition) and hemisphere-wide slow common modes are not in the primary SE | Effective N overstated. Station DEFF 1.2–4 is plausible with ≈ 45–150 trades/station | Statistical: pre-declare two-way (date × station) clustering as primary, or the more conservative of the two |
| D9 | MINOR | MIN_SAMPLE = 1,000 is non-binding at h = 0.10 (reached by day ≈ 24–37; the pessimistic case ≈ 77); rationale in §16 ("SE ≈ 0.05") is tied to it | Mis-signals where power comes from | Documentation, after D1 |
| D10 | MINOR | `NO_DATA_LOWEST` settlements enter the 30-day bias mean as tail boundaries | Non-meteorological values in b | Procedural: exclude non-NOAA settlement modes from the bias history |
| D11 | MINOR | MECHANICS_CHANGE threshold ignores ≈ 28% structural ineligibility | False stop risk narrowed to ≈ 22 points | Procedural: express the threshold relative to the burn-in baseline |
| D12 | MINOR | Tier ledgers are capital-bound (≈ 20 concurrent legs vs ≈ 60–100 demanded) and allocate in T_entry order | Tier economics describe an Asia-Pacific-weighted subsample | Reporting: show tier θ separately from S_ref θ (already implied; make explicit) |

---

## 11. Pass-condition scorecard

| | Condition | Result |
|---|---|---|
| F1 | Target sample achievable within max duration (conservative throughput) | **PASS (conditional on D3)** — 1,000 fills by ≈ day 37 conservative; ≈ 77 pessimistic |
| F2 | Useful power for an effect aligned with the declared economic question | **FAIL** — D1 |
| F3 | Dependence handled; effective N not grossly overstated | **FAIL** — D4, D8 |
| F4 | S_ref / execution produce enough fillable observations | **PASS** (100% ≥ 5 shares; 68% full) — criterion 7 marginal (D5) |
| F5 | Burn-in can satisfy its own prerequisites | **FAIL** — D6 (and D3) |
| F6 | Terminal-state logic coherent | **FAIL** — D2, D5 |
| F7 | No outcome/P&L information used to tune a frozen parameter | **PASS** — no evidence of tuning in the spec; none performed here |

`EXPERIMENT_FEASIBILITY = BLOCKED_POWER_BELOW_DECLARED_MEUE`

---

## 12. Minimum closure conditions (before t0; all outcome-independent)

1. **D1**: the architect re-pre-registers the primary claim so that the declared economically relevant effect, the REJECTED threshold and the achievable sample are mutually consistent. The power calculation must use the measured executable leg mix and a declared DEFF range. Hurdle, σ, W, entry time and the model stay as frozen unless a separate, outcome-blind decision changes them.
2. **D2**: a complete, mutually exclusive terminal-state table and a frozen analysis date.
3. **D3**: the E6 book window is tested on capture time.
4. **D4 / D8**: a pre-declared interval method and clustering that fit heavy-tailed ratios with station and date dependence.
5. **D5**: REJECTED is evaluable regardless of accessibility.
6. **D6**: burn-in is redefined by station-level bias-history completeness, and the frozen rule's trigger rate is observed before t0.
7. **D7**: an explicit °F cohort decision.
8. Re-audit by an independent reviewer after the revision. A new freeze manifest hash is required (a change after t0 would be a new experiment; before t0 it is a revision).

---

## 13. Anti-leakage confirmation

- No settlement, resolution, `closedTime`, price-history, trade, leaderboard, wallet or P&L endpoint was queried. Only `closed=false` event listings, live order books and live forecasts were used.
- No trigger's eventual outcome was inspected; no win rate, hit rate or P&L was computed.
- h, σ, W, entry time, provider, model, stations and sample size were **not** searched, varied or recommended. The b grid (±2 °C) was used only to bound the throughput uncertainty caused by the not-yet-existing bias history, not to choose b.
- Effect sizes 0.02 / 0.05 / 0.10 were evaluated as hypotheticals. Return dispersion was derived from executable prices under a fair-price assumption, not from outcomes.
- **No outcome-based parameter optimisation was performed.**

Reproduction: the scripts (`engine.py`, `collector.py`, `xsec.py`, `analyze.py`, `power.py`, `gate.py`) and raw captures were kept in the reviewer's session scratchpad. They are not committed, per the one-file deliverable scope. Every endpoint is listed in §2, and the airport coordinates came from the OurAirports `airports.csv` snapshot (sha256 `e5b485bd1453002071231563dcc54fbf1efacb7c3cbaa486c73247b3aa1b2398`, fetched 2026-09-29 16:35 UTC).

```text
STATUS = DONE
NEXT_AUTHORIZED_ACTION = Architect revision of the pre-registration (D1–D8) before any Builder burn-in;
                         no t0; REAL_CAPITAL_AUTHORIZED = FALSE
```
