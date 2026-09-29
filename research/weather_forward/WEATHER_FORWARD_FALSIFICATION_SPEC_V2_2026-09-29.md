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
WEATHER_FORWARD_SPEC_V2  = READY_FOR_INDEPENDENT_REAUDIT   (section 27)
WEATHER_FORWARD_SPEC_V1  = HISTORICAL_FROZEN_OBJECT
EXPERIMENT_FEASIBILITY   = BLOCKED_POWER_BELOW_DECLARED_MEUE   (Astra's verdict on V1; only Astra may change it)
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
| D4-ENG | D4: interval method must fit heavy tails and few clusters | PINM primary + two-way studentised bootstrap; reject only if both reject | **Modify: empirical two-way cluster-robust engine is primary for κ_core, θ_core and pooled θ; PINM is primary only for the rare-event tail count and for the tail part of the θ upper bound; PINM on θ is reported, not gating** | SIMULATED: PINM with a declared (not oracle) dependence halves power on core statistics (core-only θ = 0.10: CR 0.855–0.91 vs PINM 0.73–0.755, runs A/B) while the empirical engine is already conservative for positive θ claims with tails (null rejection 0.000–0.020 at nominal 0.05); dependence barely matters for rare tail counts, so PINM is exact-in-practice there | NO | NO |
| D4-UB | D4 / Fable §4.2: bootstrap upper bound falsely excludes MEUE with tails | not specified beyond PINM | **Structured upper bound**: capital-share-weighted combination of the core two-way bound and a tail bound from the exact win count under two declared tail models; pooled naive bounds never used for exclusion | SIMULATED: naive pooled U95 covers only 0.79–0.91 with tail legs; the structured bound covers ≥ 0.945 in every tested scenario except the deliberately adversarial hidden-lottery one (0.86–0.89), which is disclosed (section 21, item 21) | NO | NO |
| D8-DEP | D8 MAJOR: date-only primary ignores station persistence | two-way date-block × station, max of three SEs | **Adopt** (section 9) | SIMULATED here and by Fable: date-only κ test rejects 0.095–0.205 at nominal 0.025 | NO | NO |
| D2-SM | D2 CRITICAL: undefined regions, unpinned analysis date | six-label partition + orthogonal validity/accessibility | **Adopt with modifications**: three orthogonal axes (VALIDITY, SCIENTIFIC, OPERABILITY); SCIENTIFIC is the product INFORMATION_RESULT × ECONOMIC_RESULT (Fable's six labels are six of its twelve cells); INFORMATION_INSUFFICIENT added; relevance exclusion evaluated before confirmation; ECONOMIC_BOUND report field; one analysis time | proves totality by construction (section 17) | NO | NO |
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
4. The information axis can neither create nor withhold a net-value claim: the economic axis is decided by θ alone (T2, U(θ), gates); the information axis only adds diagnostic claims about which legs are mispriced and the real negative result. No trade exists or disappears because of it.

---

## 5. Estimands

### 5.1 Primary economic estimand (unchanged)

```text
θ = E[N_j] / E[C_j],  estimated by θ̂ = Σ_j N_j / Σ_j C_j
over trades j of R* on the prospective eligible cohort, REALISTIC execution, S_ref = 50 USD,
N_j = n_j · (y_j − c_j),  C_j = V_j + F_j,  c_j = C_j / n_j (all-in cost per share, fee included).
```

No winsorising, trimming, capping or leg deletion inside θ, ever. Winsorised or trimmed θ may appear only in the sensitivity section with the label `NOT_THE_ESTIMAND`.

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
| EXCL economic bound | θ ≥ threshold | θ < threshold | 0.05 | structured upper bound U(θ) (section 8.5) |

### 6.2 Powered claim

```text
ECONOMIC_RELEVANCE_THRESHOLD   θ_ERT = 0.02            (economic reporting threshold; not a powered claim)
PRIMARY_CONFIRMABLE_EFFECT     θ_PCE = frozen formula    (section 10; nominal 80% power for T2 at α = 0.05)
TARGET_POWER                   0.80 at θ_PCE (nominal, normal approximation, before the robustness gates G1–G3)
```

### 6.3 Error control

- **T1** is a union test at familywise α = 0.05 over its two strata: T1a and T1b at α/2 each (Bonferroni; valid under any dependence between core and tail; with two tests Holm's first step is identical and Simes' gain is confined to both p in (0.025, 0.05]).
- **T2** is the single primary economic test at α = 0.05, tested whether or not T1 rejects. Every scientific state that asserts more than one favourable claim (for example INFORMATION_DETECTED together with NET_VALUE_CONFIRMED) asserts an **intersection** of claims, each tested at α; by the intersection-union principle the probability that such a state is issued while any of its claims is false is ≤ α. No α is spent twice and none is recycled.
- Adverse claims are one-sided in the opposite direction (NEG at 0.025; NET_VALUE_EXCLUDED through the Bonferroni-split structured bound at 0.05) on the same parameters; the state machine orders them so that one axis never carries both a favourable and an adverse claim (section 17).
- Why not Fable's fixed-sequence gate: under IUT the joint claim needs no gate for error control, and the gate's only other effect is to withhold a confirmed θ when the count-based information statistic is less efficient than θ itself (SIMULATED, D1-GATE). A confirmed θ without detected information is reported as it is (`NO_INFORMATION_DETECTED__NET_VALUE_CONFIRMED`), and the forward-signal rule (17.5) still requires that the core not be significantly adverse.
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

Uses: (i) **T1b** (statistic `W_tail`, TAIL trades, upper tail) — gating; (ii) the tail part of the structured upper bound (8.5) — gating; (iii) θ̂ and κ̂_core under the sharp null — **reported only** (`PINM_THETA_P`, `PINM_KAPPA_P`), with the rule that a disagreement with the CR engine is printed as `ENGINE_DISAGREEMENT` and changes no label.

Why PINM does not gate θ or κ_core (SIMULATED, power table §4): with a declared rather than oracle dependence, PINM is either anti-conservative (declared below truth: Fable measured 0.13–0.21 size) or power-destroying (declared above truth: T2 power 0.73–0.755 vs 0.855–0.91 for CR at core-only θ = 0.10, and 0.275–0.28 vs 0.52–0.54 with 5% tail legs; runs A/B); the empirical CR engine adapts to the actual dependence and is conservative for positive θ claims when tail legs are present (null rejection 0.000–0.020 at nominal 0.05).

### 8.3 T1b exact tail test

`T1b` rejects iff `PINM_W_p ≤ 0.025`, where `PINM_W_p = (1 + #{W*_tail ≥ W_tail}) / (B + 1)` under the sharp null on TAIL trades with the declared copula. If the TAIL stratum is empty, T1b does not reject. Reported alongside (non-gating): Poisson-binomial p-value under independence; block-collapsed count p-value (number of 5-date blocks containing ≥ 1 tail win against its exact Poisson-binomial null `1 − Π(1 − c_j)` per block), and `λ̂_tail = W_tail / Λ_tail`.

### 8.4 NEG (core adverse)

`NEG` holds iff `κ̂_core + t_{df,0.975} · SE_CR(κ̂_core) < 0` (one-sided 0.025). Reason (SIMULATED, 3,200 null replications): the per-share residual `y − c` of favourite-bucket NO legs is negatively skewed, so the CR engine's **lower** tail over-rejects (0.061–0.068 at nominal 0.05 under clustered dependence); at 0.025 its size is 0.022–0.028, inside the 0.05 guarantee. Power against a public-bot-like κ ≈ −0.07 stays ≈ 0.98 at 0.025 (SE ≈ 0.017).

### 8.5 Structured upper bound for θ (all exclusion claims)

A pooled empirical upper bound cannot represent tail wins that did not occur and under-covers (SIMULATED coverage 0.79–0.91 for a nominal 0.95 bound when sub-4¢ legs are present). Non-parametrically, pooled θ cannot be excluded at all when the rule buys sub-cent legs: a single unobserved win on a 0.001 leg at S_ref moves θ by ≈ `50,000 / Σ C` (≈ +0.3 at 3,000 trades). V2 therefore makes every exclusion claim **model-conditional on the tail and labels it so**:

```text
U(θ) = w_core · U_core + w_tail · U_tail            (each part at one-sided level 1 − 0.025; Bonferroni → 1 − 0.05)
U_core = θ̂_core + t_{df, 0.975} · SE_CR(θ̂_core)
U_tail = max( θ_tail^TPM(λ_U), θ_tail^SHR(μ_U) )    [0 contribution if TAIL is empty]

TAIL MODELS (ASSUMED, both evaluated, the larger bound wins):
  TPM (proportional multiplier):  p_j(λ) = min(1, λ c_j)               θ_tail^TPM(λ) = Σ n_j p_j(λ) / Σ C_j − 1
  SHR (shrink toward forecast):   p_j(μ) = min(1, c_j + μ (q_j − c_j))  θ_tail^SHR(μ) = Σ n_j (p_j(μ) − c_j) / Σ C_j
     q_j = R*'s own forecast probability of the traded token (q for YES, 1 − q for NO)
  λ_U = sup{ λ ∈ [0.05, 1000] : P*_λ( W*_tail ≤ W_tail ) > 0.025 }
  μ_U = sup{ μ ∈ [0, 50]      : P*_μ( W*_tail ≤ W_tail ) > 0.025 }
  P* = PINM copula of 8.2 with the tilted marginals, same uniforms (common random numbers → monotone in λ, μ);
  bisection, 40 iterations (log-scale for λ); a sup at the interval end is reported as that end.
```

`U(θ)` is labelled `MODEL_CONDITIONAL_TAIL(TPM ∨ SHR)` in every report. Consequence stated up front: with a material tail capital share, `U(θ) < θ_ERT` is essentially unreachable (SIMULATED with 16% tail legs: 0.000–0.005 when θ ≥ 0, and only 0.07 even when the true θ = −0.10) — V2 cannot "exclude relevant value" for a rule that buys lotteries, and says so rather than borrowing precision from a bootstrap that cannot see unobserved wins.

### 8.6 Unresolved trades at analysis time

A trade whose market is not FINAL at ANALYSIS_TIME (section 11) is imputed **adversely per claim**: payout 0 for every favourable test (T1a, T1b, T2, gates) and payout `n_j` (win) for every adverse test or bound (NEG, U(θ)). Both imputations are computed; if no trade is unresolved they coincide. The count of unresolved trades is reported.

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

Drift (mission §28 item 10): θ_PCE is frozen at t0 and labels always use the frozen value. At analysis the outcome-free realised `SE0_θ` over the whole window is reported; if it exceeds 1.5 × the planned value the report carries `PCE_DRIFT = TRUE` (descriptive; no label changes).

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
                         depth ≥ 25 USD share, capital demand, GO / NO_GO.

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

Definitions: `T1`, `T2`, `NEG` from sections 6 and 8; `U = U(θ)` from 8.5; `GATES = G1 ∧ G2 ∧ G3` with
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

ECONOMIC_RESULT (ordered, first match):

| Order | Condition | Value |
|---|---|---|
| E1 | U < θ_ERT | NET_VALUE_EXCLUDED |
| E2 | T2 ∧ θ̂ ≥ θ_ERT ∧ GATES | NET_VALUE_CONFIRMED |
| E3 | T2 ∧ θ̂ ≥ θ_ERT ∧ ¬GATES | NET_VALUE_NOT_ROBUST (lists failing gates) |
| E4 | otherwise | NET_VALUE_INDETERMINATE |

Totality and exclusivity: each axis is an ordered list whose last row is "otherwise", so every reachable state has exactly one INFORMATION_RESULT and one ECONOMIC_RESULT; the 3 × 4 = 12 products plus the two pre-empting values are the complete SCIENTIFIC_STATE space (14 values). E1 precedes E2 so that a positive but economically irrelevant θ (`L > 0`, `U < θ_ERT`) is never labelled CONFIRMED. I1 precedes I2, so a tail-detected run with an adverse core is INFORMATION_DETECTED with `CORE_ADVERSE = TRUE`.

Relation to Fable's six-label partition (mission §16): Fable's NEGATIVE_INFORMATION and NO_INFORMATION_DETECTED are V2's I2 and I3 rows (with the economic column now always reported); Fable's four INFORMATION_CONFIRMED_NET_VALUE_{EXCLUDED, CONFIRMED, NOT_ROBUST, INDETERMINATE} are V2's I1 × {E1, E2, E3, E4}. **Modified**: V2 also evaluates the economic column when information is not detected (six cells Fable's gate left unevaluated), because θ is the North Star quantity and must not be withheld by a less efficient statistic (D1-GATE); and INFORMATION_INSUFFICIENT is added as a pre-empting non-result. Validity and operability stay orthogonal, as Fable proposed.

### 17.3 Report fields (evaluated whenever SCIENTIFIC_STATE ∉ {NOT_EVALUATED, INFORMATION_INSUFFICIENT}; else NOT_EVALUATED)

```text
ECONOMIC_BOUND   ordered on U(θ):  U < 0 → NET_LOSS_CONFIRMED;  U < θ_ERT → RELEVANT_VALUE_EXCLUDED;
                                   U < max(θ_PCE, θ_ERT) → LARGE_VALUE_EXCLUDED;  else NOT_EXCLUDED
                 always printed with the tag MODEL_CONDITIONAL_TAIL(TPM ∨ SHR) and w_tail
INFO_SOURCE      T1a ∧ T1b → CORE_AND_TAIL;  T1a → CORE;  T1b → TAIL;  else NONE
CORE_ADVERSE     NEG (TRUE / FALSE), printed even when T1 passes via the tail
```

Mandatory sentence whenever ECONOMIC_RESULT ∈ {NET_VALUE_INDETERMINATE, NET_VALUE_NOT_ROBUST} or ECONOMIC_BOUND ∈ {LARGE_VALUE_EXCLUDED, NOT_EXCLUDED}: **"θ in [θ_ERT, θ_PCE) is neither confirmed nor excluded by this experiment; this is not evidence of zero edge."** The result headline always prints θ̂, the two-way 90% interval, U(θ), θ_ERT and θ_PCE.

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
                                     and ECONOMIC_RESULT = NET_VALUE_CONFIRMED
                                     and INFORMATION_RESULT ≠ NEGATIVE_INFORMATION
                                     and OPERABILITY_STATE = ACCESSIBLE
                              FALSE otherwise
```

TRUE authorises nothing beyond proposing a further paper/shadow phase to governance. No capital, no live trading.

### 17.6 Rejection rule

```text
R*_REJECTED_AS_NET_STRATEGY  iff  ECONOMIC_RESULT = NET_VALUE_EXCLUDED
                                  or (INFORMATION_RESULT = NEGATIVE_INFORMATION and ECONOMIC_RESULT ≠ NET_VALUE_CONFIRMED)
```

An ECONOMIC_BOUND of LARGE_VALUE_EXCLUDED (with any INFORMATION_RESULT other than NEGATIVE_INFORMATION) means "a large edge is excluded; the relevant band is unresolved" — not a rejection of economic relevance.

### 17.7 Old-to-new label map

| V1 label | V2 equivalent |
|---|---|
| WEATHER_EDGE_FORWARD_SIGNAL | FORWARD_SIGNAL = TRUE (17.5) |
| WEATHER_EDGE_REJECTED | R*_REJECTED_AS_NET_STRATEGY (17.6) |
| WEATHER_EDGE_NOT_PROVEN | NET_VALUE_NOT_ROBUST / NET_VALUE_INDETERMINATE (with the information column) |
| WEATHER_EDGE_REQUIRES_MORE_DATA | retired (NET_VALUE_INDETERMINATE plus the mandatory sentence) |
| WEATHER_EDGE_OPERATIONALLY_INACCESSIBLE | OPERABILITY_STATE axis (never a scientific label) |
| WEATHER_FORWARD_TEST_INVALID | VALIDITY_STATE = INVALID_* |

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
| 1 | κ_core detects calibration but not net value | CLOSED | κ uses all-in executable cost, so κ > 0 is net per share; net value for R* is only ever claimed through θ (T2, U(θ), gates); the cell INFORMATION_DETECTED__NET_VALUE_EXCLUDED exists precisely for "the chosen legs are underpriced, yet R* has no relevant net value" |
| 2 | a tail-only edge blocked by a pooled gate | CLOSED | there is no gate on θ at all (D1-GATE); the information axis is stratified with an exact tail win-count test (SIMULATED power in the power table §4) |
| 3 | "either core or tail" rejection inflates FWER | CLOSED | Bonferroni α/2 + α/2 ≤ α under any dependence; SIMULATED T1 null rejection ≤ 0.05 within Monte-Carlo error (power table §4) |
| 4 | Bonferroni inside T1 too weak / too conservative | BOUNDED | with two tests Holm = Bonferroni for the union rejection; Simes' gain limited to both p in (0.025, 0.05]; accepted |
| 5 | θ tested only after T1 changes its interpretation | CLOSED (by design change) | θ is not gated (D1-GATE); joint claims use intersection-union; a θ-only edge is reported in the NO_INFORMATION_DETECTED__NET_VALUE_* cells, never hidden |
| 6 | requiring PINM and bootstrap agreement kills power | CLOSED (by design change) | agreement is not required; engines assigned by where each is valid (8.2) |
| 7 | assumed PINM copula wrong | BOUNDED | PINM gates only rare-event tail counts, where observed-scale dependence is ≈ 0.01 under latent 0.10; declared values conservative; ×0.5 / ×2 sensitivity reported; residual risk MINOR |
| 8 | ≈ 25–35 effective station clusters | BOUNDED | 48 NOAA stations after D7; max-of-three SE; t with `min(G_B, G_S) − 1` df; floor Kish ≥ 15; SIMULATED size under strong station dependence in the power table §4 |
| 9 | tail wins destabilise bootstrap intervals | CLOSED | no bootstrap in any gating role; empirical CR is self-normalising (a lone tail win inflates its own SE); exclusion uses the structured bound; G2 removes the top 5 trades |
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
| 7 | one tail win dominates the conclusion | Refuted for confirmation (CR self-normalisation + G2) and for exclusion (structured bound includes the observed win count); surviving risk is the opposite one (no exclusion possible), which is disclosed | — |
| 8 | date-only dependence sneaks back | Refuted: max-of-three never includes an IID or date-only fallback | — |
| 9 | assumed PINM dependence anti-conservative | Bounded: PINM gates only tail counts and the tail bound; declared values above the advisory and observed-scale ranges | MINOR |
| 10 | undefined region in the state machine | Refuted: ordered total partitions (17) | — |
| 11 | operability hides a scientific rejection | Refuted: separate axis, never pre-empts | — |
| 12 | quiet books marked missing | Refuted: no lower bound on the exchange timestamp (12.3) | — |
| 13 | burn-in uses unresolved dates | Refuted: USABLE requires FINAL at T_entry(D) by our own capture time | — |
| 14 | °F arithmetic ambiguous | Refuted: frozen regexes, integer sets, half-open intervals, °F bias target = bucket midpoint, exact unit conversion | — |
| 15 | capital scarcity creates an unacknowledged subsample | Refuted: S_ref estimand has no capital cap; tiers labelled capacity-constrained with composition | — |
| 16 | optional stopping | Refuted: one analysis time; no interim; analysis module time-locked | — |
| 17 | Builder still makes a scientific decision | Refuted: section 26 lists every scientific item as frozen; residual Builder choices are engineering only | — |
| 18 | a trading-rule parameter changed because of feasibility | Refuted: R* unchanged; only CONSERVATIVE slippage (execution robustness) and the cohort domain changed, both mechanically motivated | — |
| 19 | the 0.02–PCE band treated rhetorically as zero | Refuted: mandatory sentence, ECONOMIC_BOUND field, rejection rule excludes LARGE_VALUE_EXCLUDED | — |
| 20 | silent mutation under venue drift | Refuted: automated mechanics codes, truncation rule, new-experiment policy (22) | — |
| 21 | (added) exclusions rest on a tail model | Carried: U(θ) is MODEL_CONDITIONAL_TAIL(TPM ∨ SHR); an edge concentrated in the cheapest legs beyond both models could be excluded wrongly at the LARGE_VALUE level (see power table §4, hidden-lottery scenario) | **MAJOR (disclosed, non-blocking)** |
| 22 | (added) GO/NO_GO likely NO_GO at Astra's measured mix | Carried: an honest pre-declared outcome, not a defect; V2 does not pretend otherwise | MINOR |

No CRITICAL issue survives.

---

## 22. Post-t0 mutation policy

Before t0: scientific repairs are allowed only if outcome-blind, documented, re-frozen with new hashes, and independently re-audited. After t0: any material change to signal, cohort, STATION_TABLE, estimand, strata, thresholds, PCE, inference engines, dependence declaration, seeds, execution models, capture contract, completeness rules, mechanics rules, terminal logic or analysis time **creates a new experiment**; the running window is closed as INVALID_PARAMETER_MUTATION if the change touched it, and nothing is repaired retroactively. Engineering fixes that provably leave every archived decision and every analysis output byte-identical (replay proves it) are not material.

---

## 23. Unchanged V1 elements carried explicitly

Economic accounting and full ledger (V1 §11); settlement controls, anomaly flag, per-station 20% cap (§20); access fields (§21); survivorship cohort (§23, descriptive); exploratory family E1–E15 with Holm (§15; E8 now uses the tick-aware CONSERVATIVE model; E13/E14 are now populated); anti-leakage invariants 1–10, 12–20 (§24) — invariant 11 is replaced by section 12.3 and invariants 21–24 are added in section 25.

---

## 24. What V2 can and cannot conclude

Can: whether R*'s chosen legs are underpriced net of executable costs, in the core and in the tail (including a real negative result); whether a net edge of at least θ_PCE exists (80% nominal power); an interval for θ with its core/tail decomposition and a model-conditional upper bound; the information actually collected; operability at small capital.

Cannot: confirm or exclude θ in [0.02, θ_PCE); exclude relevant value for a rule with material lottery-leg capital; attribute an edge to NWP information rather than structure beyond the descriptive baselines; say anything about the venue after a mechanics change.

---

## 25. Builder schema and invariant deltas (additions to V1 §22 / §24)

SIGNAL_DECISION adds `phase ∈ {PRE_T0, FORWARD}`, `stratum ∈ {CORE, TAIL}`, `best_ask_chosen`, `q_chosen`, `bias_window_dates[30]`, `bias_span_days`, `bias_contaminated`. ORDER_BOOK_SNAPSHOT adds `request_sent_at`, `http_status`, `method`, `attempt_no`, `valid_capture`, `invalid_reason`, `tick_size_recorded`, `book_age_ms`. EVENT adds `reason_family`, `mechanics_code`, `unit`, `bucket_lo[11]`, `bucket_hi[11]`. SETTLEMENT adds `first_observed_final_at`. CAPITAL_USAGE adds `alloc_hash`. New table READINESS (per station-kind-date: BIAS_N, BIAS_SPAN, READY flags) and PHASE_LOG (GLOBAL_READY per date, OP dates, t0, D_0, pauses, counted dates, mechanics events).

Added invariants: **21 `PRE_T0_OUTCOME_BLIND`** — no PRE_T0 decision is joined to a settlement or payout; **22 `ANALYSIS_TIME_LOCK`** — no forward P&L / κ / θ / win-count computation before ANALYSIS_TIME outside synthetic tests; **23 `STRATUM_AT_DECISION`** — stratum stored at decision time, never recomputed; **24 `CAPTURE_TIME_WINDOW`** — replaces invariant 11 with section 12.3.

---

## 26. Builder contract

Builder may decide: languages, storage engines, process layout, scheduling mechanics, retry implementation within 12.2, test design, dashboards.

Builder may **not** decide (all frozen here and in the manifest): estimands, strata, cohort, °F arithmetic, station-table membership, thresholds, PCE formula and ceilings, power claims, inference engines, dependence declaration, seeds and draw order, terminal labels and their order, readiness and GLOBAL_READY, OP length, t0, capture windows and validity, completeness definitions, allocation order, mechanics semantics, analysis time, sensitivity list.

Verification required before a t0 request (in addition to V1 §28): unit tests for the four title regexes and E4 (°C and °F, negative temperatures, malformed titles); interval arithmetic against hand-computed q for a 2 °F ladder; CONSERVATIVE tick rule in both regimes; VALID_CAPTURE with a quiet book (old exchange timestamp) and with a future timestamp; completeness denominator; USABLE / BIAS_HISTORY_READY with a correction hold and a missing vintage; the two-way CR engine against a hand-worked 3 × 3 example including a negative `V_2w`; PINM reproducibility (same seed → identical p-values) and monotonicity of the λ / μ bisection; adverse imputation; every row of every state table reachable in a synthetic test; PRE_T0 outcome-blind and ANALYSIS_TIME_LOCK enforcement; restart/replay idempotence (no duplicated fills, P&L or sessions after crash and replay).

---

## 27. Status

```text
WEATHER_FORWARD_SPEC_V2   = READY_FOR_INDEPENDENT_REAUDIT
MEANING                   = D1–D8 closed at the design level, D9–D12 closed or accepted and disclosed; no CRITICAL
                            issue survives the self-attack; no outcome information used; Builder has no scientific
                            discretion; one analysis time; total terminal partitions
NOT_MEANING               = EXPERIMENT_FEASIBILITY = PASS (Astra's call) / BUILDER_AUTHORIZED / t0 / edge / capital
EXPERIMENT_FEASIBILITY    = BLOCKED_POWER_BELOW_DECLARED_MEUE   (unchanged until Astra re-audits)
NEXT_AUTHORIZED_ACTION    = INDEPENDENT ASTRA RE-AUDIT OF THIS EXACT V2 SHA
REAL_CAPITAL_AUTHORIZED   = FALSE
LIVE_TRADING_AUTHORIZED   = FALSE
t0                        = NOT_DECLARED
```
