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
WEATHER_FORWARD_SPEC_V2  = AUDITED @94b59348 → ASTRA_WEATHER_V2_REAUDIT = BLOCKED_D4_STRUCTURED_BOUND_FALSE_ECONOMIC_EXCLUSION (@7d95c00)
WEATHER_FORWARD_SPEC_V2_D4_REPAIR = AUDITED @24d2342 → ASTRA_WEATHER_V2_D4_RECHECK = BLOCKED_D4_PROSPECTIVE_ESTIMAND_UNSAMPLED_TAIL_FALSE_EXCLUSION (@3d18085)
WEATHER_FORWARD_SPEC_V2_D4_C2_REPAIR = READY_FOR_ASTRA_D4_C2_RECHECK   (D4 repair R2: sections 5.1, 6, 8.5, 8.5b, 17; section 27)
ASTRA_REAUDIT            = astra/weather-forward-v2-independent-reaudit-2026-09-29 @ 7d95c00abccfbc805c0d8abca65a6b93268741a2
ASTRA_D4_RECHECK         = astra/weather-forward-v2-independent-reaudit-2026-09-29 @ 3d18085862f239a81936345989b4e26414cedcf3
WEATHER_FORWARD_SPEC_V1  = HISTORICAL_FROZEN_OBJECT
EXPERIMENT_FEASIBILITY   = BLOCKED_POWER_BELOW_DECLARED_MEUE   (Astra's verdict on V1; only Astra may change it)
EXPERIMENT_FEASIBILITY_V2 = BLOCKED_D4_PROSPECTIVE_ESTIMAND_UNSAMPLED_TAIL_FALSE_EXCLUSION   (Astra's verdict on 24d2342; only Astra may change it)
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
| Effect 120 dates can confirm with 80% power (`θ_PCE`) | ≈ 0.06–0.08 if the executable mix has no material sub-4¢ share; ≈ 0.12–0.36 if lottery legs persist (power table §2, §4.2) — above the 0.10 ceiling, V2 does not start (section 10.3) | FORMULA FROZEN; value populated pre-t0 from outcome-free prices (section 10) |
| Can a 120-date design confirm **or** exclude θ = 0.02? | **No.** Both need `SE(θ̂) ≤ 0.008` (≈ 15,500 independent trades at σ = 1; ≈ 1,300 dates at 35 trades/day) | DERIVED, reproduced from Astra and Fable |
| Can it detect an **executable mispricing** in the rule's chosen legs, including a real negative result? | Yes for the core stratum: SE(κ_core) ≈ 0.013–0.017, MDE80 ≈ 0.032–0.043 per share, independent of the lottery share; tail stratum by an exact win-count test | DERIVED + SIMULATED |

Therefore V2 does **not** pretend 0.02 is adjudicable. It keeps θ as the only economic estimand, separates `θ_ERT` (what matters economically) from `θ_PCE` (what the design can confirm), adds a well-powered, stratified information axis (not a gate) that can say "the rule's chosen legs are not underpriced", and labels the band `[θ_ERT, θ_PCE)` explicitly **unresolved** — never "zero edge".

---

## 2. Decision record (one row per major decision)

`OUTCOME_INFORMATION_USED = FALSE` and `TRADING_RULE_CHANGED = FALSE` for every row; the only changed execution assumption is D-EXEC.

| ID | ASTRA_FINDING | FABLE_RECOMMENDATION | ARCHITECT_DECISION | RATIONALE | OUTCOME INFO USED | TRADING RULE CHANGED |
|---|---|---|---|---|---|---|
| D1-ARCH | D1 CRITICAL: θ_MEUE = 0.02 undetectable in ≤ 120 dates; realistic MDE 0.06–0.10 (0.15–0.25 with lottery legs) | Family D (stratified two-estimand) with Family B honest labels | **Adopt a configured Family D + B hybrid** (fixed 120 counted dates; θ the only economic estimand; stratified κ_core / tail win-count information axis; θ_ERT ≠ θ_PCE); reject A (multi-year, mechanics drift) and C (no interim, section 11) | the only architecture with a real negative result at 120 dates, tail-immune on the information axis, honest about the unresolved band; A answers a 2030 question about a venue that changed templates twice in six months | NO | NO |
| D1-GATE | — | fixed-sequence gatekeeping: θ tested only after the information gate T1 passes | **Reject the gatekeeper. Information and economics are two parallel axes; θ is tested unconditionally; every joint claim is an intersection of tests each at α (intersection-union), so error control is unchanged** | SIMULATED: with an edge concentrated in the cheapest legs (true θ = 0.44) the θ engine detects it 0.535–0.61 of the time but a count-based gate would let only 0.21–0.30 through (runs A/B) — a gate would block a real, large edge roughly half to two-thirds of the time; a confirmed θ is itself payout-weighted evidence that the chosen legs are underpriced | NO | NO |
| D1-THR | MEUE unreachable | θ_ERT reporting threshold; θ_PCE from pre-t0 prices | **θ_ERT = 0.02 frozen; θ_PCE by frozen price-implied formula; PCE_CEILING = 0.10 → NO_GO** | a design that can confirm only edges > 5 × ERT is not worth starting (section 10) | NO (prices, depth, counts only) | NO |
| D4-EST | D4 MAJOR: heavy-tailed θ, percentile bootstrap unreliable | κ_core + W_tail vs Λ_tail as confirmatory information estimands, θ untouched | **Adopt, with κ defined net of all-in executable cost; strata by price (a < 0.04), not by the tick field** | κ is bounded and tail-immune; the tick field is a market-level property shared by YES and NO tokens (MEASURED: 1,550 of 2,981 temperature markets at 0.001) | NO | NO |
| D4-ENG | D4: interval method must fit heavy tails and few clusters | PINM primary + two-way studentised bootstrap; reject only if both reject | **Modify: empirical two-way cluster-robust engine is primary for κ_core, θ_core and pooled θ; PINM is primary only for the rare-event tail count (T1b); PINM on θ is reported, not gating** (V2@94b5934 also used PINM for the tail part of the θ upper bound; retired by D4 repair R1) | SIMULATED: PINM with a declared (not oracle) dependence halves power on core statistics (core-only θ = 0.10: CR 0.855–0.91 vs PINM 0.73–0.755, runs A/B) while the empirical engine is already conservative for positive θ claims with tails (null rejection 0.000–0.020 at nominal 0.05); dependence barely matters for rare tail counts, so PINM is exact-in-practice there | NO | NO |
| D4-UB (REPAIRED, R1) | V2 re-audit C1 (CRITICAL): the TPM ∨ SHR structured bound false-excludes θ = 0.0315 > θ_ERT at 7.46% (coverage 0.885) and θ = 0.085 > θ_PCE at 11.2% in a GO-compatible design; MP1 committed sim ≠ frozen bisection contract | (Fable: PINM tail engine; no full-class bound proposed) | **Exclusion bound = core two-way CR bound + assumption-free tail supremum `M_tail` (every TAIL leg wins); TPM / SHR retired from every role; pooled naive bounds never used** | the tail's admissible class is all `p ∈ [0,1]` under any dependence; the only bound valid over it is the identified-set supremum; coverage then equals core coverage (run D: 0.9705–0.993 over nine adversarial core geometries; both Astra attacks: coverage 1.0, false exclusion 0) | NO | NO |
| D4-REJ (REPAIRED, R1) | consequence of C1: V2 rule 17.6 also rejected R* as a net strategy on NEGATIVE_INFORMATION alone | — | **Economic rejection only through `U(θ) < θ_ERT`; NEGATIVE_INFORMATION becomes the information-level `R*_CORE_INFORMATION_REJECTED`** (superseded by D4-C2: no economic rejection of R* is issued in V2) | run D: in Astra's positive-tail / negative-core geometry the NEG clause produced a false economic rejection in 32.0% of runs | NO | NO |
| D4-C2 (REPAIRED, R2) | V2 D4 recheck C2 (CRITICAL, Astra @3d18085): R1's bound covers only the realised-window value θ_W; when rare 0.001 legs are absent from a GO-compatible window, prospective θ_P = 0.025 > θ_ERT is falsely excluded 5.92% of runs (0.19–0.35 at p_tail 0.5–1.0) and θ_P = 0.10 is falsely LARGE-excluded 15.3% | — | **Prospective exclusion is NOT IDENTIFIED in V2: no prospective exclusion label exists; ECONOMIC_RESULT = PROSPECTIVE_VALUE_{CONFIRMED, NOT_ROBUST, INDETERMINATE}; R1's bound is kept, re-scoped to θ_W and reported only as REALIZED_WINDOW_BOUND; R*_REJECTED_AS_NET_STRATEGY is never issued** | identification theorem (8.5b): under V2's own admissible class (p ∈ [0,1], 0.001 tick, date common modes) every level-0.05 test of θ_P ≥ θ_ERT or θ_P ≥ θ_PCE has power ≤ 0.058 against every admissible truth over the 134 observed dates; the arrival-bound alternative (R2-A) needs trade-level independence V2 does not grant and, even granted, never excludes (allowance ≈ 1.2 at zero observed sub-cent legs) | NO | NO |
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
4. The information axis can neither create nor withhold a net-value claim: the economic axis is decided by θ alone (T2, θ̂, gates; prospective exclusion is not identified, 8.5b); the information axis only adds diagnostic claims about which legs are mispriced and the real negative result. No trade exists or disappears because of it.

---

## 5. Estimands

### 5.1 Primary economic estimand (unchanged)

```text
θ = E[N_j] / E[C_j],  estimated by θ̂ = Σ_j N_j / Σ_j C_j
over trades j of R* on the prospective eligible cohort, REALISTIC execution, S_ref = 50 USD,
N_j = n_j · (y_j − c_j),  C_j = V_j + F_j,  c_j = C_j / n_j (all-in cost per share, fee included).
```

No winsorising, trimming, capping or leg deletion inside θ, ever. Winsorised or trimmed θ may appear only in the sensitivity section with the label `NOT_THE_ESTIMAND`.

**Prospective vs realised-window value (D4 repair R2, after Astra D4 recheck C2).** The estimand above is **prospective** and is written `θ_P` wherever the distinction matters: the expectation is over the executed-trade process of R* (market opportunity process × R* × REALISTIC fill at S_ref, section 8.5b), so it includes opportunity types — in particular rare sub-4¢ TAIL legs — that a finite window may not contain. `θ_P` is the only strategic economic quantity; every `PROSPECTIVE_*` label refers to it. A second, **report-only** estimand is frozen:

```text
θ_W = Σ_{j∈WINDOW} n_j (p_j − c_j) / Σ_{j∈WINDOW} C_j
      p_j = true settlement probability of trade j's token given the information at T_entry(j)
```

`θ_W` is the expected net value per dollar of the trades R* actually executed in the window, conditional on which trades occurred. It is neither the realised P&L `Σ N_j / Σ C_j` nor `θ_P`. It is reported only through `REALIZED_WINDOW_BOUND` (17.3), never enters a `PROSPECTIVE_*` label and never rejects R*.

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
| T1a core information | κ_core ≤ 0 | κ_core > 0 | α/2 = 0.025 | two-way CR t-test on κ̂_core |
| T1b tail information | λ_tail ≤ 1 (sharp null `p_j = c_j` on TAIL) | λ_tail > 1 | α/2 = 0.025 | PINM exact win-count test |
| **T1 information** | both T1a and T1b nulls | information exists in core **or** tail | α = 0.05 (Bonferroni) | rejects iff T1a or T1b rejects |
| **T2 economic (primary)** | θ ≤ 0 | θ > 0 | α = 0.05, **evaluated unconditionally** (no gate) | two-way CR t-test on θ̂ |
| NEG core adverse | κ_core ≥ 0 | κ_core < 0 | **0.025** (absorbs the documented lower-tail skew inflation, 8.4) | two-way CR t-test |
| EXCL-P prospective exclusion | θ_P ≥ threshold | θ_P < threshold | — | **none: not identified in V2 (section 8.5b); no test is run and no label exists** |
| EXCL-W realised-window bound (report field) | θ_W ≥ threshold | θ_W < threshold | declared 0.05 (core CR at one-sided 0.025 + deterministic tail supremum) | U_W = w_core U_core + M_tail (section 8.5) |

### 6.2 Powered claim

```text
ECONOMIC_RELEVANCE_THRESHOLD   θ_ERT = 0.02            (economic reporting threshold; not a powered claim)
PRIMARY_CONFIRMABLE_EFFECT     θ_PCE = frozen formula    (section 10; nominal 80% power for T2 at α = 0.05)
TARGET_POWER                   0.80 at θ_PCE (nominal, normal approximation, before the robustness gates G1–G3)
```

### 6.3 Error control

- **T1** is a union test at familywise α = 0.05 over its two strata: T1a and T1b at α/2 each (Bonferroni; valid under any dependence between core and tail; with two tests Holm's first step is identical and Simes' gain is confined to both p in (0.025, 0.05]).
- **T2** is the single primary economic test at α = 0.05, tested whether or not T1 rejects. Every scientific state that asserts more than one favourable claim (for example INFORMATION_DETECTED together with PROSPECTIVE_VALUE_CONFIRMED) asserts an **intersection** of claims, each tested at α; by the intersection-union principle the probability that such a state is issued while any of its claims is false is ≤ α. No α is spent twice and none is recycled.
- Adverse claims: NEG at 0.025 on κ_core (information axis). There is **no adverse prospective economic claim** (D4 repair R2, section 8.5b). The realised-window bound U_W (section 8.5) is a report field on θ_W at declared level 0.05; it is never part of a SCIENTIFIC_STATE label and cannot reject R*, so no α is shared with T2.
- Why not Fable's fixed-sequence gate: under IUT the joint claim needs no gate for error control, and the gate's only other effect is to withhold a confirmed θ when the count-based information statistic is less efficient than θ itself (SIMULATED, D1-GATE). A confirmed θ without detected information is reported as it is (`NO_INFORMATION_DETECTED__PROSPECTIVE_VALUE_CONFIRMED`), and the forward-signal rule (17.5) still requires that the core not be significantly adverse.
- Exploratory family (V1 §15, E1–E15): Holm at α = 0.05 within the family, never promoted (unchanged).

---

## 7. Information and power (D1; details in the power table file)

DERIVED with `z_{0.95} + z_{0.80} = 2.4865`, `z_{0.95} + z_{0.90} = 2.9264`:

- Independent trades for 80% power: θ = 0.02 → 15,456 / 61,826 / 129,988 at σ_eff = 1.0 / 2.0 / 2.9; θ = 0.05 → 2,473 / 9,892 / 20,798; θ = 0.10 → 618 / 2,473 / 5,200 (reproduces Astra §6.3 and Fable §1.1 to the unit).
- **Binding constraint = target dates.** With `m` trades per date and latent within-date correlation, the date design effect is `1 + (m − 1) ρ_d`, so `n_eff ≤ D / ρ_d`: at ρ_d = 0.03, 120 dates cap `n_eff` at 4,000 regardless of throughput; at 0.05, 2,400. The planning dependence model is `DEFF(m) = 1.5 × (1 + 0.03 (m − 1))` (station factor 1.5 × date factor), giving DEFF 2.2 / 3.0 / 3.9 at 17 / 35 / 55 trades per date — inside Astra's 2–4 range and rising with throughput as the date ceiling requires.
- At 120 counted dates and the conservative V2 throughput (35/day, °C + °F): `SE(θ̂)` = 0.027 / 0.054 / 0.078 at σ_eff 1.0 / 2.0 / 2.9 → **MDE80 = 0.067 / 0.134 / 0.194**; `SE(κ_core)` ≈ 0.014 → MDE80 ≈ 0.035 per share.
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

### 8.4 NEG (core adverse)

`NEG` holds iff `κ̂_core + t_{df,0.975} · SE_CR(κ̂_core) < 0` (one-sided 0.025). Reason (SIMULATED, 3,200 null replications): the per-share residual `y − c` of favourite-bucket NO legs is negatively skewed, so the CR engine's **lower** tail over-rejects (0.061–0.068 at nominal 0.05 under clustered dependence); at 0.025 its size is 0.022–0.028, inside the 0.05 guarantee. Power against a public-bot-like κ ≈ −0.07 stays ≈ 0.98 at 0.025 (SE ≈ 0.017).

### 8.5 Realised-window upper bound U_W (D4 repair R1; re-scoped to θ_W by D4 repair R2)

**Scope after D4 repair R2 (Astra D4 recheck C2 @3d18085).** Everything in this section is a statement about the realised-window estimand `θ_W` (5.1). The proof conditions on the realised trade set, so the bound covers the tail legs that occurred and nothing else. It is **not** a bound on the prospective `θ_P`. After R2 it drives no `SCIENTIFIC_STATE` label and no rejection: its only use is the report field `REALIZED_WINDOW_BOUND` (17.3). Prospective exclusion is treated in 8.5b.

History (R1, kept). A pooled empirical upper bound cannot represent tail wins that did not occur, and it under-covers: SIMULATED coverage 0.79–0.91 for a nominal 0.95 bound when sub-4¢ legs are present. The V2@94b5934 structured bound replaced the tail part with the larger of two ASSUMED tail models (TPM, SHR). Astra showed, and run D reproduced, that the admissible tail outcome class is not restricted to those models (C1). **The TPM / SHR tail models are retired from every role.**

Admissible tail outcome class for θ_W (frozen): every vector of true win probabilities `p_j ∈ [0, 1]` on the realised TAIL trades, under any dependence. Nothing the experiment observes can shrink this class without an assumption. The only upper bound on the realised tail's contribution that is valid over the whole class is therefore its identified-set supremum, "every realised TAIL leg wins":

```text
U_W     = w_core · U_core + M_tail                                  (one-sided upper bound for θ_W; declared level 95%)
U_core  = θ̂_core + t_{df, 0.975} · SE_CR(θ̂_core)                   (unchanged: two-way CR, section 8.1; core level 0.975
                                                                     keeps the documented lower-tail skew allowance of 8.4)
M_tail  = Σ_{TAIL} (n_j − C_j) / Σ_{all} C_j  = w_tail · (Σ_TAIL n_j / Σ_TAIL C_j − 1)
          (TAIL_MAX_CONTRIBUTION: θ_W-contribution of the realised TAIL stratum if every realised TAIL leg pays 1;
           0 if TAIL is empty; computed from fills only, known at T_entry, deterministic)
```

Coverage proof, for θ_W only. Condition on the realised trade set: fills, `n_j`, `C_j` and strata are fixed at T_entry, before any outcome. Then `θ_W = w_core θ_core,W + w_tail θ_tail,W` with `θ_tail,W = Σ_TAIL n_j p_j / Σ_TAIL C_j − 1 ≤ Σ_TAIL n_j / Σ_TAIL C_j − 1` for every `p ∈ [0, 1]^TAIL` and every dependence structure. Hence `{θ_core,W ≤ U_core} ⊆ {θ_W ≤ U_W}` and `P(θ_W ≤ U_W) ≥ P(θ_core,W ≤ U_core)`: uncertainty about the outcomes of the realised tail legs costs no coverage.

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

### 8.5b Prospective exclusion is not identified in V2 (D4 repair R2)

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

**Theorem (non-identification of prospective exclusion).**

- Setup. Let 𝒫 be the admissible class: stationary executed-trade processes consistent with R*'s frozen mechanics, with any win probabilities `p ∈ [0, 1]`, executable prices ≥ the 0.001 tick, and any dependence, including the date / regime common modes that V2's own dependence model declares (section 9). Fix a threshold `θ* ∈ {θ_ERT, θ_PCE}`. Let φ be any test, possibly randomised, that uses the data V2 can observe (the 14 OP dates and the 120 window dates, `D = 134` target dates, plus anything independent of them). Suppose φ has level α over the null: `P_Q(φ = 1) ≤ α` for every `Q ∈ 𝒫` with `θ_P(Q) ≥ θ*`.
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

Numbers (DERIVED; `WEATHER_FORWARD_V2_D4_C2_SIM_2026-09-30.py ceiling`), with α = 0.05 and D = 134:
- The power ceiling is ≤ **0.0577** for θ* = θ_ERT and ≤ **0.0584** for θ* = 0.10, at every θ_0 ≥ −1 (−1 is the minimum possible θ: every leg loses). At θ_0 = −0.10 it is 0.0509 (ERT) and 0.0514 (θ_PCE = 0.10).
- So a valid prospective exclusion test can have at most ≈ 0.8 percentage points more power than a coin that rejects with probability 0.05, against every admissible truth, including an R* that loses everything.
- Even under trade-level independence of arrivals, which V2's dependence model does **not** grant, the ceiling over N = 4,200 trades is 0.085 at θ_0 = −0.10 and 0.50 at θ_0 = −0.5. That is still no useful exclusion in the plausible range.

**Zero-count rule (frozen).** The theorem does not depend on how many tail legs the window contains. Whether it has 0, 1, 2, 5 or 10 observed sub-cent legs, or no tail leg of any price, the unobserved jackpot-date type stays equally possible. **Zero observed TAIL arrivals never implies a zero prospective tail rate.** SIMULATED (run E, counts): with 0 observed sub-cent legs, the retired rule excluded in 92–93% of runs whatever θ_P was (0.019, 0.376 or 1.089), and with ≥ 1 observed leg in 0%. The frozen rule issues no prospective exclusion at any count.

**Frozen consequence.** `PROSPECTIVE_EXCLUSION_IDENTIFIABLE = FALSE`. This is a constant derived above from frozen quantities (tick, fee, the h-rule's admissible asks, D = 134, α = 0.05) and the frozen dependence class, so no run-time gate and no discretion exist. V2 contains **no prospective exclusion label**:
- ECONOMIC_RESULT has no EXCLUDED value (17.2).
- `R*_REJECTED_AS_NET_STRATEGY` is never issued (17.6).
- Every result prints `PROSPECTIVE_EXCLUSION = NOT_IDENTIFIED_IN_V2`.

This is loss of power, not a validity defect: by the theorem no valid alternative has materially more.

**Error guarantee after R2.**
- Prospective claims are confirmatory only. T2 at one-sided α = 0.05 (8.1), combined with the information claims by intersection-union (6.3). The effective α of every `PROSPECTIVE_*` label is ≤ 0.05.
- No prospective adverse claim is issued, so no arrival-uncertainty component needs an α share.
- The realised-window bound U_W has a single stochastic component (the core CR bound at nominal one-sided 0.025) plus a deterministic tail term, at declared level 95%. No two stochastic bounds are combined anywhere.

**Alternatives evaluated (not adopted).**
- *R2-A arrival-process bound.* Replace `M_tail` by the sum over tail price bins `[c_min, 0.002), [0.002, 0.005), [0.005, 0.01), [0.01, 0.02), [0.02, 0.04)` of an exact Poisson upper bound on executed arrivals × the bin's maximum payoff per dollar.
  - It is valid only under trade-level (or known-cluster) independence of arrivals, which V2's dependence class does not grant. Under date-clustered arrivals a trade-count bound overstates the information.
  - Even granting independence, zero observed legs in the lowest bin give an allowance ≥ 5.30/N × 951 ≈ 1.2 at N = 4,200 (Bonferroni 0.005 per bin). Exclusion is never reached: SIMULATED run E, `P(U_R2A < θ_ERT) = P(U_R2A < θ_PCE) = 0` in every scenario.
  - R2-A is therefore R2-B with an unjustified assumption added.
- *R2-C, realised-window estimand only.* θ_W exclusion answers "were the trades R* happened to execute worth less than 0.02 per dollar", not the North Star question. It is adopted **only** as the report field `REALIZED_WINDOW_BOUND`, never as a prospective claim and never as a rejection of R*.
- Excluding sub-cent legs, raising h, or a price floor would be trading-rule changes. They are not authorised and would be V3 material.

**Finite horizon vs long run (structural non-identification region).**
- A mechanism whose arrival interval materially exceeds the observed dates, but whose payoff per dollar can reach 951, cannot be excluded by 134 dates. The whole region `θ_P ≥ θ_ERT` is non-excludable in V2.
- Excluding it would need either a declared and independently audited arrival model, or a horizon with `D · η* ≫ 1`. For θ_0 = −0.10 that is `1/η* ≈ 7,900` dates per unit of the exponent. Both are outside V2.

**Why no capital decision is weakened.** Deployment requires `WEATHER_EDGE_FORWARD_SIGNAL` (17.5), i.e. prospective confirmation. "Not confirmed" already means no capital, so the absence of prospective exclusion changes no capital decision. Governance may retire R* using the information-level (`R*_CORE_INFORMATION_REJECTED`) and realised-window evidence. That is a governance judgement, not a V2 statistical claim.

**Prospective confirmation (unchanged; asymmetry).**
- The same construction against confirmation needs "catastrophic dates", on which every trade loses (at worst −1 per dollar). Pulling θ_P from θ_0 down to 0 takes `η = θ_0 / (1 + θ_0)`.
- For θ_0 ≥ θ_ERT that is ≥ 0.0196 per date, so the probability that 134 dates contain no such date is ≤ 0.071 at θ_0 = 0.02 and ≤ 0.0015 at θ_0 = 0.05. Bounded downside makes an unsampled type that could overturn a confirmation visible, so confirmation has no structural non-identification.
- Residual finite-sample risk under exactly this alternative with θ_P = 0 (SIMULATED run E, confirm; 4,000 replications each): false `PROSPECTIVE_VALUE_CONFIRMED` is 0.0378 [0.0318, 0.0437] at θ_0 = 0.02, 0.0372 at 0.03, 0.0315 at 0.05 and 0.0177 at 0.10. All are ≤ α = 0.05.

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
| Small-cluster correction | CR1 factor per dimension + `t_{min(G_B, G_S) − 1}` reference |
| Minimum clusters | ≥ 12 blocks with ≥ 1 trade; ≥ 25 traded stations; Kish-effective traded stations ≥ 15 (information floor, section 11.4) |
| Kish-effective stations | `(Σ_s n_s)² / Σ_s n_s²` on trade counts (for κ) and on capital (for θ); both reported |
| Reported dependence | `DEFF_B = V_B/V_iid`, `DEFF_S = V_S/V_iid`, `DEFF_2w = max(V_2w, V_B, V_S)/V_iid` with `V_iid = n/(n−1) Σ e_j² / Q²`; `n_eff = n / DEFF_2w`; information per date; structural cap `D / ρ̂_d`, where ρ̂_d, ρ̂_s come from the variance decomposition of standardised residuals `(y_j − c_j)/√(c_j(1 − c_j))` (reported only) |
| Concentration diagnostics | share of `Σ e²` by the largest block and the largest station (reported); gross-profit shares enter gate G2 (section 17) |
| Mechanisms named | synoptic regimes shared across stations on one date (date/block); persistent station bias and the lag of the 30-date trailing bias through a seasonal transition (station); HIGHEST/LOWEST of one station-day (cell); unequal station activity (Kish); hemisphere/season common modes (sensitivity cluster) |

Date-only inference is never primary and never a fallback. SIMULATED (section 20): the date-only κ test rejects 0.095–0.205 under the null at nominal 0.025 with date/station dependence present; the two-way max-of-three test holds size.

---

## 10. Thresholds, PCE formula and GO / NO_GO (D1, sections 19 and 27 of the mission)

### 10.1 Frozen constants

```text
θ_ERT             = 0.02
ALPHA             = 0.05 one-sided (favourable family); T1a, T1b at 0.025
TARGET_POWER      = 0.80 at θ_PCE
Z_80              = 2.4865   (z_0.95 + z_0.80)
DEFF_PLAN(m)      = 1.5 × (1 + 0.03 × (m − 1))
MAX_INFORMATION   = 120 counted target dates
PCE_CEILING       = 0.10
SE_KAPPA_CEILING  = 0.020
```

### 10.2 θ_PCE formula (frozen now; populated once from the observation phase; never recomputed after t0)

Inputs: every R* decision with action TRADE under REALISTIC at S_ref whose target date is one of the 14 observation-phase dates (section 11.2). No settlement, outcome, hit rate or P&L enters.

```text
J          = those trades;  |J| = number of trades;  m̄ = |J| / 14
σ0²        = |J| · Σ_J C_j² (1 − c_j)/c_j  /  (Σ_J C_j)²          (price-implied fair-null variance per trade, capital-weighted)
n_120      = 120 · m̄
SE0_θ      = σ0 · sqrt( DEFF_PLAN(m̄) / n_120 )
θ_PCE      = ceil( 100 · Z_80 · SE0_θ ) / 100                      (rounded UP to the next 0.01)
m̄_core     = |J ∩ CORE| / 14
SE0_κ      = sqrt( mean_{J∩CORE} c_j (1 − c_j) ) · sqrt( DEFF_PLAN(m̄) / (120 · m̄_core) )
Λ_120      = (120 / 14) · Σ_{J∩TAIL} c_j                            (expected tail wins under the fair null)
```

### 10.3 GO / NO_GO (outcome-free design check, not a strategy result)

```text
GO iff   θ_PCE ≤ PCE_CEILING (0.10)
    and  SE0_κ ≤ SE_KAPPA_CEILING (0.020)
    and  distinct traded stations in J ≥ 25 and Kish-effective (trade counts) ≥ 15
    and  the observation phase met every GLOBAL_READY condition on all 14 dates
else NO_GO_<first failing reason in this order: PCE_ABOVE_CEILING, KAPPA_UNDERPOWERED, STATION_DIVERSITY, READINESS>
```

Rationale for `PCE_CEILING = 0.10`: it is 5 × θ_ERT and the lower end of the confirmable range V1 itself disclosed (§5: "≳ 0.10–0.13"). An economic arm that can confirm only edges larger than that answers a question whose plausible prior mass is negligible for a public-information taker rule in a market with public bots (V1 C11, C12); starting it would spend five calendar months to issue INDETERMINATE for every plausible truth. Rationale for `SE_KAPPA_CEILING = 0.020`: the information axis is V2's only real negative-result instrument; at SE 0.020 its MDE80 is 0.050 per share, and NEG (at 0.025) still rejects a public-bot-like loss rate (V1 C12, about −0.07 per share) with power ≈ 0.9; beyond that ceiling V2 would lose its only real negative result.

Honest consequence (DERIVED + SIMULATED, power table §2 and §4.2): at Astra's measured all-trigger dispersion (σ_eff ≈ 2.93) the formula gives θ_PCE ≈ 0.18–0.26 → **NO_GO**; at the no-lottery dispersion (σ_eff ≈ 0.96) it gives ≈ 0.06–0.08 → GO; in synthetic mixes, θ_PCE = 0.08 with no sub-4¢ legs (GO), 0.21 with 5% (NO_GO), 0.36 with 16% (NO_GO). **Because a single sub-cent leg carries the variance of hundreds of core legs, even a small lottery share makes the economic arm unpowerable in 120 dates.** Which case applies depends on how the frozen bias correction changes the executable leg mix, which only the observation phase can measure; the most likely pre-declared outcome, given Astra's b = 0 cross-section, is NO_GO_PCE_ABOVE_CEILING. A NO_GO is a design finding recorded as `WEATHER_FORWARD_SPEC_V2 = NO_GO_<reason>`, not a strategy result. It returns the decision to governance, which may (outcome-blind, since no outcome will have been observed) retire the Weather candidate or commission a new pre-registration (V3) — for example an information-primary experiment, or constant-payout sizing (which would make θ ≈ κ) or a tail-leg exclusion. Those are **trading-rule or design changes** that need their own freeze and independent audit; none is an amendment of V2.

Drift (mission §28 item 10): θ_PCE is frozen at t0 and labels always use the frozen value. At analysis the outcome-free realised `SE0_θ` over the whole window is reported; if it exceeds 1.5 × the planned value the report carries `PCE_DRIFT = TRUE` (descriptive; no label changes). After D4 repair R1, a post-OP drift of the tail price mix (Astra: 2 sub-cent legs appearing after a GO observation phase) can no longer create a false exclusion; it can only raise `M_tail` and make exclusion unattainable, which is reported. After D4 repair R2 there is no prospective exclusion at all; θ_PCE and GO keep only their confirmability role and are **not** an arrival-sufficiency check for rare tail types (Astra D4 recheck: GO passes 82–94% of the C2 designs).

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

IF4 and IF5 use outcomes but are direction-neutral reliability conditions; they cannot convert a favourable result into an adverse one or vice versa.

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

Definitions: `T1`, `T2`, `NEG` from sections 6 and 8 (`T2` tests the prospective θ_P); `GATES = G1 ∧ G2 ∧ G3` with
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

ECONOMIC_RESULT (prospective, estimand θ_P; ordered, first match; D4 repair R2):

| Order | Condition | Value |
|---|---|---|
| E1 | T2 ∧ θ̂ ≥ θ_ERT ∧ GATES | PROSPECTIVE_VALUE_CONFIRMED |
| E2 | T2 ∧ θ̂ ≥ θ_ERT ∧ ¬GATES | PROSPECTIVE_VALUE_NOT_ROBUST (lists failing gates) |
| E3 | otherwise | PROSPECTIVE_VALUE_INDETERMINATE |

There is no EXCLUDED value: prospective exclusion is not identified in V2 (8.5b). The V2@24d2342 row `E1: U < θ_ERT → NET_VALUE_EXCLUDED` is deleted. No confirmable result is lost by the deletion, because `U_W ≥ θ̂` (8.5) means the old row could never pre-empt a run with `θ̂ ≥ θ_ERT`. The realised-window statement it used to make is kept, with its correct estimand θ_W, in the `REALIZED_WINDOW_BOUND` report field (17.3).

Totality and exclusivity: each axis is an ordered list whose last row is "otherwise", so every reachable state has exactly one INFORMATION_RESULT and one ECONOMIC_RESULT. The 3 × 3 = 9 products plus the two pre-empting values are the complete SCIENTIFIC_STATE space (**11 values** after D4 repair R2; 14 before). A positive but economically irrelevant θ̂ (`θ̂ < θ_ERT`) is never CONFIRMED because E1 and E2 require `θ̂ ≥ θ_ERT`. I1 precedes I2, so a tail-detected run with an adverse core is INFORMATION_DETECTED with `CORE_ADVERSE = TRUE`; the forward-signal rule and `R*_CORE_INFORMATION_REJECTED` read `CORE_ADVERSE`, not INFORMATION_RESULT (17.5, 17.6).

Relation to Fable's six-label partition (mission §16): Fable's NEGATIVE_INFORMATION and NO_INFORMATION_DETECTED are V2's I2 and I3 rows (with the economic column now always reported); Fable's INFORMATION_CONFIRMED_NET_VALUE_{CONFIRMED, NOT_ROBUST, INDETERMINATE} are V2's I1 × {E1, E2, E3}; Fable's INFORMATION_CONFIRMED_NET_VALUE_EXCLUDED has no prospective counterpart after D4 repair R2 (8.5b) — its realised-window analogue is INFORMATION_DETECTED with a `REALIZED_WINDOW_*_EXCLUDED` report field. **Modified**: V2 also evaluates the economic column when information is not detected (six cells Fable's gate left unevaluated), because θ is the North Star quantity and must not be withheld by a less efficient statistic (D1-GATE); and INFORMATION_INSUFFICIENT is added as a pre-empting non-result. Validity and operability stay orthogonal, as Fable proposed.

### 17.3 Report fields (evaluated whenever SCIENTIFIC_STATE ∉ {NOT_EVALUATED, INFORMATION_INSUFFICIENT}; else NOT_EVALUATED)

```text
PROSPECTIVE_EXCLUSION  = NOT_IDENTIFIED_IN_V2   (constant, section 8.5b; always printed)
REALIZED_WINDOW_BOUND  estimand θ_W (5.1), bound U_W (8.5); a report field — never a prospective claim, never a rejection of R*
                 ordered on U_W:  U_W < 0 → REALIZED_WINDOW_LOSS_CONFIRMED;  U_W < θ_ERT → REALIZED_WINDOW_RELEVANT_VALUE_EXCLUDED;
                                  U_W < max(θ_PCE, θ_ERT) → REALIZED_WINDOW_LARGE_VALUE_EXCLUDED;  else REALIZED_WINDOW_NOT_EXCLUDED
                 always printed with w_tail, M_tail (TAIL_MAX_CONTRIBUTION), w_core·U_core and EXCLUSION_BLOCKED_BY_TAIL;
                 the tail term is assumption-free for θ_W (8.5)
TAIL_ARRIVAL_REPORT  counts of EXECUTED TAIL arrivals and of unfilled TAIL_TRIGGERs (8.5b) by price bin [c_min, 0.002),
                 [0.002, 0.005), [0.005, 0.01), [0.01, 0.02), [0.02, 0.04), separately for the OP and the window, with their
                 capital share; descriptive, changes no label
INFO_SOURCE      T1a ∧ T1b → CORE_AND_TAIL;  T1a → CORE;  T1b → TAIL;  else NONE
CORE_ADVERSE     NEG (TRUE / FALSE), printed even when T1 passes via the tail
```

Mandatory sentences:
- (a) Whenever ECONOMIC_RESULT ∈ {PROSPECTIVE_VALUE_INDETERMINATE, PROSPECTIVE_VALUE_NOT_ROBUST}: **"θ in [θ_ERT, θ_PCE) is neither confirmed nor excluded by this experiment; this is not evidence of zero edge."**
- (b) Always: **"V2 cannot exclude prospective net value (section 8.5b): a rare, high-payoff opportunity type absent from the observed dates cannot be ruled out. REALIZED_WINDOW statements describe only the expected value of the trades executed in the window."**

The result headline always prints θ̂, the two-way 90% interval, `PROSPECTIVE_EXCLUSION`, U_W (labelled "realised-window bound"), θ_ERT and θ_PCE.

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

### 17.5 Forward-signal rule

```text
WEATHER_EDGE_FORWARD_SIGNAL = TRUE  iff  VALIDITY = VALID_COMPLETE
                                     and ECONOMIC_RESULT = PROSPECTIVE_VALUE_CONFIRMED
                                     and CORE_ADVERSE = FALSE
                                     and OPERABILITY_STATE = ACCESSIBLE
                              FALSE otherwise
```

TRUE authorises nothing beyond proposing a further paper/shadow phase to governance. No capital, no live trading.

D4 repair R2 (Astra D4 recheck, minor m2): the rule now reads `CORE_ADVERSE = FALSE` instead of `INFORMATION_RESULT ≠ NEGATIVE_INFORMATION`. Under I1 precedence, a run detected through the tail with an adverse core used to pass; now it does not. This is strictly tighter, and the economic label names are the only other change.

### 17.6 Rejection rule

```text
R*_REJECTED_AS_NET_STRATEGY   never issued by V2; printed as NOT_IDENTIFIED_IN_V2   (prospective exclusion not identified, 8.5b)
R*_CORE_INFORMATION_REJECTED  iff  CORE_ADVERSE = TRUE (NEG)                       (information-level, not economic)
```

**D4 repair R2 (after Astra D4 recheck C2 @3d18085).** Under R1 the rule was `R*_REJECTED_AS_NET_STRATEGY iff U(θ) < θ_ERT`, and that bound covers only θ_W. Astra reproduced false prospective rejections: 5.92% at θ_P = 0.025 with p_tail = 0.17, and 19–35% at p_tail 0.5–1.0. Run E reproduced 4.75% / 16.5–17.6% / 31.4% with fresh code. By the theorem of 8.5b, no valid rule can reject R* as a net strategy with useful power in V2. The label is therefore unreachable, and every result prints it as `NOT_IDENTIFIED_IN_V2`.

The information-level falsification `R*_CORE_INFORMATION_REJECTED` means "the rule's core legs are overpriced net of executable costs". It now fires on `CORE_ADVERSE` (NEG) whatever INFORMATION_RESULT is (Astra minor m2), says nothing about the tail or θ_P, and is never read as "R* has no net value". `NEGATIVE_INFORMATION` alone still never rejects R* economically, as R1 established.

History (R1, kept). The V2@94b5934 rule also rejected R* as a net strategy on `NEGATIVE_INFORMATION ∧ ECONOMIC_RESULT ≠ NET_VALUE_CONFIRMED`. In Astra's A1 geometry that clause fired in 32.0% of runs at θ = 0.0315 > θ_ERT. R1 removed it.

A REALIZED_WINDOW_* value is a statement about θ_W only: "the trades executed in this window had expected net value below the threshold per dollar". It is never a rejection of R*.

### 17.7 Old-to-new label map

| V1 label | V2 equivalent |
|---|---|
| WEATHER_EDGE_FORWARD_SIGNAL | FORWARD_SIGNAL = TRUE (17.5) |
| WEATHER_EDGE_REJECTED | no prospective economic equivalent (17.6: R*_REJECTED_AS_NET_STRATEGY = NOT_IDENTIFIED_IN_V2); information-level R*_CORE_INFORMATION_REJECTED; realised-window REALIZED_WINDOW_* report field |
| WEATHER_EDGE_NOT_PROVEN | PROSPECTIVE_VALUE_NOT_ROBUST / PROSPECTIVE_VALUE_INDETERMINATE (with the information column) |
| WEATHER_EDGE_REQUIRES_MORE_DATA | retired (PROSPECTIVE_VALUE_INDETERMINATE plus mandatory sentences (a) and (b)) |
| WEATHER_EDGE_OPERATIONALLY_INACCESSIBLE | OPERABILITY_STATE axis (never a scientific label) |
| WEATHER_FORWARD_TEST_INVALID | VALIDITY_STATE = INVALID_* |

### 17.8 Claim matrix (D4 repair R2)

| Label / field | Axis | Estimand | Null | Test / bound | Level / coverage | May claim | May not claim |
|---|---|---|---|---|---|---|---|
| PROSPECTIVE_VALUE_CONFIRMED | economic (prospective) | θ_P | θ_P ≤ 0 | T2 two-way CR + θ̂ ≥ θ_ERT + G1–G3 | size ≤ 0.05 (IUT with information claims) | R*'s prospective net value per dollar is positive; point estimate ≥ θ_ERT; robust to G1–G3 | "θ_P ≥ θ_ERT with 95% confidence"; deployment; capital |
| PROSPECTIVE_VALUE_NOT_ROBUST | economic (prospective) | θ_P | θ_P ≤ 0 | T2 + θ̂ ≥ θ_ERT, a gate fails | size ≤ 0.05 | a positive θ_P that fails the listed robustness gates | a forward signal; deployment |
| PROSPECTIVE_VALUE_INDETERMINATE | economic (prospective) | θ_P | — | — | — | neither confirmed nor excluded (sentences a, b) | "no edge"; "edge excluded"; "edge exists" |
| PROSPECTIVE_EXCLUSION = NOT_IDENTIFIED_IN_V2 | economic (prospective) | θ_P | θ_P ≥ θ_ERT / θ_PCE | none; theorem 8.5b | any valid test has power ≤ 0.058 | V2 cannot exclude prospective value at any threshold | any exclusion of θ_P |
| R*_REJECTED_AS_NET_STRATEGY | economic (prospective) | θ_P | — | not identified | — | never issued | — |
| REALIZED_WINDOW_{LOSS_CONFIRMED, RELEVANT_VALUE_EXCLUDED, LARGE_VALUE_EXCLUDED} | realised window (report) | θ_W | θ_W ≥ 0 / θ_ERT / max(θ_PCE, θ_ERT) | U_W < threshold | declared 95% (core CR one-sided 0.975 nominal; tail term deterministic) | the trades executed in the window had expected net value below the threshold per dollar | anything about θ_P or R*'s future value; a rejection of R*; "the observed return was negative" (it bounds the expected value of those trades, not the realised P&L) |
| REALIZED_WINDOW_NOT_EXCLUDED | realised window (report) | θ_W | — | U_W ≥ threshold | — | no realised-window exclusion (EXCLUSION_BLOCKED_BY_TAIL says whether the realised tail is the reason) | evidence of value |
| INFORMATION_DETECTED (INFO_SOURCE) | information | κ_core; λ_tail | κ_core ≤ 0 ∧ λ_tail ≤ 1 | T1a (CR) ∪ T1b (PINM) | FWER 0.05 | R*'s chosen legs are underpriced net of all-in cost (core and/or tail) | net value; θ_P |
| NEGATIVE_INFORMATION / CORE_ADVERSE / R*_CORE_INFORMATION_REJECTED | information | κ_core | κ_core ≥ 0 | NEG (CR) | 0.025 | the core legs are overpriced net of executable costs | anything about the tail, θ_W or θ_P; "R* has no net value" |
| NO_INFORMATION_DETECTED | information | κ_core, λ_tail | — | — | — | no information detected | no information exists |
| WEATHER_EDGE_FORWARD_SIGNAL | combined | θ_P, κ_core, validity, operability | — | 17.5 | IUT ≤ 0.05 | a further paper/shadow phase may be proposed to governance | capital; live trading |
| OPERABILITY_STATE | operability | depth, ρ_30, mechanics, access | — | 17.4 | descriptive | accessibility at small capital | any scientific label |

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
| 1 | κ_core detects calibration but not net value | CLOSED | κ uses all-in executable cost, so κ > 0 is net per share; net value for R* is only ever claimed through θ (T2, θ̂, gates); after D4 repair R2 V2 cannot state prospectively "the chosen legs are underpriced, yet R* has no relevant net value" (8.5b); its realised-window analogue is INFORMATION_DETECTED with REALIZED_WINDOW_RELEVANT_VALUE_EXCLUDED |
| 2 | a tail-only edge blocked by a pooled gate | CLOSED | there is no gate on θ at all (D1-GATE); the information axis is stratified with an exact tail win-count test (SIMULATED power in the power table §4) |
| 3 | "either core or tail" rejection inflates FWER | CLOSED | Bonferroni α/2 + α/2 ≤ α under any dependence; SIMULATED T1 null rejection ≤ 0.05 within Monte-Carlo error (power table §4) |
| 4 | Bonferroni inside T1 too weak / too conservative | BOUNDED | with two tests Holm = Bonferroni for the union rejection; Simes' gain limited to both p in (0.025, 0.05]; accepted |
| 5 | θ tested only after T1 changes its interpretation | CLOSED (by design change) | θ is not gated (D1-GATE); joint claims use intersection-union; a θ-only edge is reported in the NO_INFORMATION_DETECTED__PROSPECTIVE_VALUE_* cells, never hidden |
| 6 | requiring PINM and bootstrap agreement kills power | CLOSED (by design change) | agreement is not required; engines assigned by where each is valid (8.2) |
| 7 | assumed PINM copula wrong | BOUNDED | PINM gates only rare-event tail counts, where observed-scale dependence is ≈ 0.01 under latent 0.10; declared values conservative; ×0.5 / ×2 sensitivity reported; residual risk MINOR |
| 8 | ≈ 25–35 effective station clusters | BOUNDED | 48 NOAA stations after D7; max-of-three SE; t with `min(G_B, G_S) − 1` df; floor Kish ≥ 15; SIMULATED size under strong station dependence in the power table §4 |
| 9 | tail wins destabilise bootstrap intervals | CLOSED | no bootstrap in any gating role; empirical CR is self-normalising (a lone tail win inflates its own SE); the realised-window bound's tail term cannot be moved by any tail win or loss; prospective exclusion is not issued (8.5b); G2 removes the top 5 trades |
| 10 | pre-t0 PCE drifts over 120 dates | BOUNDED | PCE frozen at t0 and used as a label constant; realised outcome-free SE0 reported; `PCE_DRIFT` flag; re-run of the OP if t0 slips > 21 days |

---

## 21. Architect self-attack (mission §40)

| # | Attack | Result | Severity if surviving |
|---|---|---|---|
| 1 | V2 still claims power it does not have | Refuted: the only powered economic claim is θ_PCE (nominal, normal approximation, before the robustness gates G1–G3); the power table states engine sizes and simulated powers; 0.02 is declared non-adjudicable; a lottery-heavy mix is pre-declared NO_GO rather than run underpowered | — |
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
| 19 | the 0.02–PCE band treated rhetorically as zero | Refuted: mandatory sentences (a) and (b), PROSPECTIVE_EXCLUSION = NOT_IDENTIFIED_IN_V2, REALIZED_WINDOW_BOUND field clearly scoped to θ_W | — |
| 20 | silent mutation under venue drift | Refuted: automated mechanics codes, truncation rule, new-experiment policy (22) | — |
| 21 | (added) exclusions rest on a tail model | **Resolved by D4 repair R1**: the tail term is the assumption-free supremum `M_tail`; coverage over the whole admissible tail class is at least the core coverage; Astra's two attacks give coverage 1.0 and zero false exclusions (power table §4.5). Scope after D4 repair R2: θ_W only (item 25) | — (cost: MINOR, disclosed) |
| 22 | (added) GO/NO_GO likely NO_GO at Astra's measured mix | Carried: an honest pre-declared outcome, not a defect; V2 does not pretend otherwise | MINOR |
| 23 | (added, D4 repair) an economic rejection is issued without a valid θ bound | **Resolved by D4 repair R1**: 17.6 now rejects R* as a net strategy only through `U(θ) < θ_ERT`; the NEG-only path (false economic rejection 32.0% in Astra's A1 geometry) is re-labelled information-level. After D4 repair R2 no economic rejection of R* is issued at all (item 25) | — |
| 24 | (added, D4 repair) the core bound itself under-covers for hidden edges at the 0.04 boundary | Refuted by run D: boundary-hidden coverage 0.993, boundary-diffuse 0.9705, false exclusion ≤ 0.0295; core payouts are capped at 25 per dollar by the stratum boundary | — |
| 25 | (added, D4 repair R2) prospective exclusion from a bound that sees only the sampled tail (Astra C2) | **Resolved by D4 repair R2**: identification theorem (8.5b); no prospective exclusion label; R1 bound re-scoped to θ_W. Run E: 0 prospective exclusions and 0 R* rejections in every scenario (retired rule 4.75–56% false) | — (cost: exclusion power ≤ 0.058 for any valid test; disclosed) |
| 26 | (added, R2) a θ_W exclusion read as a prospective rejection | Refuted: separate REALIZED_WINDOW_* vocabulary, mandatory sentence (b), claim matrix 17.8; no rule reads REALIZED_WINDOW_BOUND | — |
| 27 | (added, R2) prospective confirmation has the same sampling problem | Bounded: bounded downside (≥ −1 per dollar) makes an overturning unsampled type visible with probability ≥ 0.93 over 134 dates at θ_0 = 0.02; run E false PROSPECTIVE_VALUE_CONFIRMED at θ_P = 0 under catastrophic-date alternatives ≤ 0.0378 (upper MC 0.0437) | MINOR |
| 28 | (added, R2) GO / PCE relied on to rule out rare tail arrivals | Refuted: PCE and GO unchanged and not used for that; C2 designs pass GO 80–100% (run E) | — |
| 29 | (added, R2) zero observed tail legs read as a zero prospective tail rate | Refuted: zero-count rule (8.5b); retired rule excluded 92–93% at zero observed legs whatever θ_P was; frozen rule 0 | — |

No CRITICAL issue survives.

---

## 22. Post-t0 mutation policy

Before t0: scientific repairs are allowed only if outcome-blind, documented, re-frozen with new hashes, and independently re-audited. After t0: any material change to signal, cohort, STATION_TABLE, estimand, strata, thresholds, PCE, inference engines, dependence declaration, seeds, execution models, capture contract, completeness rules, mechanics rules, terminal logic or analysis time **creates a new experiment**; the running window is closed as INVALID_PARAMETER_MUTATION if the change touched it, and nothing is repaired retroactively. Engineering fixes that provably leave every archived decision and every analysis output byte-identical (replay proves it) are not material.

---

## 23. Unchanged V1 elements carried explicitly

Economic accounting and full ledger (V1 §11); settlement controls, anomaly flag, per-station 20% cap (§20); access fields (§21); survivorship cohort (§23, descriptive); exploratory family E1–E15 with Holm (§15; E8 now uses the tick-aware CONSERVATIVE model; E13/E14 are now populated); anti-leakage invariants 1–10, 12–20 (§24) — invariant 11 is replaced by section 12.3 and invariants 21–24 are added in section 25.

---

## 24. What V2 can and cannot conclude

Can: whether R*'s chosen legs are underpriced net of executable costs, in the core and in the tail (including a real negative result); whether a net edge of at least θ_PCE exists (80% nominal power); an interval for θ with its core/tail decomposition; an assumption-free upper bound on the realised-window value θ_W of the trades actually executed; the information actually collected; operability at small capital.

Cannot: confirm θ in [0.02, θ_PCE); exclude prospective net value at any threshold (8.5b: no valid test has more than 0.058 power at α = 0.05); reject R* as a net strategy; exclude realised-window value whenever `M_tail` keeps U_W above the threshold (in practice: any sub-cent leg held at S_ref); reject R* economically from core information alone; attribute an edge to NWP information rather than structure beyond the descriptive baselines; say anything about the venue after a mechanics change.

---

## 25. Builder schema and invariant deltas (additions to V1 §22 / §24)

SIGNAL_DECISION adds `phase ∈ {PRE_T0, FORWARD}`, `stratum ∈ {CORE, TAIL}`, `best_ask_chosen`, `q_chosen`, `bias_window_dates[30]`, `bias_span_days`, `bias_contaminated`. ORDER_BOOK_SNAPSHOT adds `request_sent_at`, `http_status`, `method`, `attempt_no`, `valid_capture`, `invalid_reason`, `tick_size_recorded`, `book_age_ms`. EVENT adds `reason_family`, `mechanics_code`, `unit`, `bucket_lo[11]`, `bucket_hi[11]`. SETTLEMENT adds `first_observed_final_at`. CAPITAL_USAGE adds `alloc_hash`. New table READINESS (per station-kind-date: BIAS_N, BIAS_SPAN, READY flags) and PHASE_LOG (GLOBAL_READY per date, OP dates, t0, D_0, pauses, counted dates, mechanics events).

Added invariants: **21 `PRE_T0_OUTCOME_BLIND`** — no PRE_T0 decision is joined to a settlement or payout; **22 `ANALYSIS_TIME_LOCK`** — no forward P&L / κ / θ / win-count computation before ANALYSIS_TIME outside synthetic tests; **23 `STRATUM_AT_DECISION`** — stratum stored at decision time, never recomputed; **24 `CAPTURE_TIME_WINDOW`** — replaces invariant 11 with section 12.3.

---

## 26. Builder contract

Builder may decide: languages, storage engines, process layout, scheduling mechanics, retry implementation within 12.2, test design, dashboards.

Builder may **not** decide (all frozen here and in the manifest): estimands, strata, cohort, °F arithmetic, station-table membership, thresholds, PCE formula and ceilings, power claims, inference engines, dependence declaration, seeds and draw order, terminal labels and their order, readiness and GLOBAL_READY, OP length, t0, capture windows and validity, completeness definitions, allocation order, mechanics semantics, analysis time, sensitivity list.

Verification required before a t0 request (in addition to V1 §28): unit tests for the four title regexes and E4 (°C and °F, negative temperatures, malformed titles); interval arithmetic against hand-computed q for a 2 °F ladder; CONSERVATIVE tick rule in both regimes; VALID_CAPTURE with a quiet book (old exchange timestamp) and with a future timestamp; completeness denominator; USABLE / BIAS_HISTORY_READY with a correction hold and a missing vintage; the two-way CR engine against a hand-worked 3 × 3 example including a negative `V_2w`; PINM reproducibility (same seed → identical p-values); `M_tail` and `EXCLUSION_BLOCKED_BY_TAIL` against hand-worked examples (empty tail, one 0.001 leg, several 0.039 legs); REALIZED_WINDOW_BOUND ordering; PROSPECTIVE_EXCLUSION printed as NOT_IDENTIFIED_IN_V2 and R*_REJECTED_AS_NET_STRATEGY never TRUE in any synthetic run; TAIL_ARRIVAL_REPORT bins including zero counts; the 11-value SCIENTIFIC partition; adverse imputation; every row of every state table reachable in a synthetic test; PRE_T0 outcome-blind and ANALYSIS_TIME_LOCK enforcement; restart/replay idempotence (no duplicated fills, P&L or sessions after crash and replay).

---

## 27. Status

```text
WEATHER_FORWARD_SPEC_V2              = AUDITED @94b59348 (immutable ancestor of this commit)
ASTRA_WEATHER_V2_REAUDIT             = BLOCKED_D4_STRUCTURED_BOUND_FALSE_ECONOMIC_EXCLUSION   (Astra @7d95c00)
WEATHER_FORWARD_SPEC_V2_D4_REPAIR    = R1 @0583614 / 24d2342 → ASTRA_WEATHER_V2_D4_RECHECK =
                                       BLOCKED_D4_PROSPECTIVE_ESTIMAND_UNSAMPLED_TAIL_FALSE_EXCLUSION (Astra @3d18085)
EXPERIMENT_FEASIBILITY_V2            = BLOCKED_D4_PROSPECTIVE_ESTIMAND_UNSAMPLED_TAIL_FALSE_EXCLUSION   (Astra's; unchanged until Astra rechecks)
WEATHER_FORWARD_SPEC_V2_D4_C2_REPAIR = READY_FOR_ASTRA_D4_C2_RECHECK
D4_C2_REPAIR                         = R2 = R2_B_PROSPECTIVE_EXCLUSION_INDETERMINATE_WHEN_UNIDENTIFIED (hybrid: R1 bound kept as
                                       the θ_W report field REALIZED_WINDOW_BOUND). Identification theorem 8.5b: under the frozen
                                       admissible class no valid prospective exclusion test has power > 0.058 over 134 dates, so
                                       PROSPECTIVE_EXCLUSION = NOT_IDENTIFIED_IN_V2; ECONOMIC_RESULT ∈ PROSPECTIVE_VALUE_{CONFIRMED,
                                       NOT_ROBUST, INDETERMINATE}; R*_REJECTED_AS_NET_STRATEGY never issued; R*_CORE_INFORMATION_REJECTED
                                       and the forward-signal rule read CORE_ADVERSE (Astra minor m2); §24 wording fixed (Astra minor m1)
D4_R1_STATUS                         = KEPT: U_W = w_core·U_core + M_tail valid for θ_W (C1 closed for the realised trade set)
MP1                                  = CLOSED (Astra @3d18085)
CARRIED CLOSED                       = D1 D2 D3 D5 D6 D7 D8 D9 D11 D12 CLOSED; D10 CLOSED_ACCEPTED_AND_DISCLOSED
                                       (D2 partition re-derived: 11 values, total by construction; only the economic axis changed)
NOT_MEANING                          = EXPERIMENT_FEASIBILITY = PASS / BUILDER_AUTHORIZED / t0 / edge / capital
NEXT_AUTHORIZED_ACTION               = ASTRA BOUNDED D4-C2 RECHECK ONLY
BUILDER_AUTHORIZED                   = FALSE
REAL_CAPITAL_AUTHORIZED              = FALSE
LIVE_TRADING_AUTHORIZED              = FALSE
t0                                   = NOT_DECLARED
```
