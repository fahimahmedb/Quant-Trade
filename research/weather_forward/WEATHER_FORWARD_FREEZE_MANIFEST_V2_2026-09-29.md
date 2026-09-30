# WEATHER FORWARD FREEZE MANIFEST — V2 — 2026-09-29

```text
MANIFEST_ROLE            = enumeration of every quantity that must be immutable before t0 (V2)
SPEC                     = research/weather_forward/WEATHER_FORWARD_FALSIFICATION_SPEC_V2_2026-09-29.md
SUPERSEDES               = WEATHER_FORWARD_FREEZE_MANIFEST_2026-09-29.md @ 726070a (kept immutable as V1)
WEATHER_FORWARD_SPEC_V2  = AUDITED @94b59348; ASTRA_WEATHER_V2_REAUDIT = BLOCKED_D4_STRUCTURED_BOUND_FALSE_ECONOMIC_EXCLUSION (@7d95c00)
WEATHER_FORWARD_SPEC_V2_D4_REPAIR = AUDITED @24d2342; ASTRA_WEATHER_V2_D4_RECHECK = BLOCKED_D4_PROSPECTIVE_ESTIMAND_UNSAMPLED_TAIL_FALSE_EXCLUSION (@3d18085)
WEATHER_FORWARD_SPEC_V2_D4_C2_REPAIR = AUDITED @e45d2ce7; ASTRA_WEATHER_V2_D4_C2_RECHECK = BLOCKED_D4_PROSPECTIVE_CONFIRMATION_UNSAMPLED_LOSS_REGIME_FALSE_CONFIRMATION (@92c2f706)
WEATHER_FORWARD_SPEC_V2_D4_C3_TRANSPORT_REPAIR = READY_FOR_ASTRA_D4_C3_RECHECK   (rows marked D4-R3 below; section E; section A is authoritative where it differs from the C / D records)
BUILDER_AUTHORIZED       = FALSE
REAL_CAPITAL_AUTHORIZED  = FALSE
LIVE_TRADING_AUTHORIZED  = FALSE
t0                       = NOT_DECLARED
FREEZE_RULE              = every row has CAN_CHANGE_AFTER_t0 = NO; after t0 a change creates a new experiment (spec §22);
                           before t0 a change requires an outcome-blind revision, new hashes and independent re-audit
STATUS COLUMN            = UNCHANGED (V1 value carried) / CLARIFIED (V1 silent or ambiguous; deterministic reading fixed) /
                           CHANGED (V1 value replaced) / NEW (did not exist in V1)
```

## A. Frozen values

### A1. Market, cohort, station, settlement

| FIELD | FROZEN VALUE | STATUS | SPEC § |
|---|---|---|---|
| VENUE | Polymarket international CLOB, read-only public APIs | UNCHANGED | V1 A |
| ELIGIBLE_MARKET_DEFINITION | daily `Highest`/`Lowest temperature in <city> on <date>` events; title regex `^(Highest\|Lowest) temperature in (.+?) on (.+)\?$`; tag `weather`; E1–E8 of V1 §6 with E4 and E6 replaced (below) | CLARIFIED | 14, 12.4 |
| E4_LADDER | exactly 11 markets; all titles parse by the four frozen regexes; one `or below`, one `or higher`; nine middle integer sets of identical width `w = 1` (°C) or `w = 2` (°F); contiguous; unit = STATION_TABLE unit | CHANGED | 14.2 |
| °F / °C POLICY | **both** in the primary cohort; °F via exact 2-degree interval arithmetic | CHANGED (V1 literal E4 excluded °F) | 14 |
| BUCKET_ARITHMETIC | regexes `^(-?\d+)°U or below$` → (−∞, N]; `^(-?\d+)°U or higher$` → [N, +∞); `^(-?\d+)°U$` → [N, N]; `^(-?\d+)-(-?\d+)°U$` → [a, b] (b ≥ a); continuous interval `[lo − 0.5, hi + 0.5)`; `q_k = F(hi + 0.5) − F(lo − 0.5)` in the market unit; x ↦ integer N iff x ∈ [N − 0.5, N + 0.5) | CHANGED (generalised; identical for °C) | 14.1 |
| UNIT_CONVERSION | forecasts requested in °C; °F members `m_F = 1.8 m_C + 32`, no rounding | CLARIFIED | 3 |
| STATION_TABLE_SEMANTICS | all ICAO codes in NOAA-WRH-template daily temperature events (°C and °F) in the `closed=false` gamma listing at compilation, compiled once before capture day 1, frozen by hash; later stations = EXPLORATORY_NEW_STATION; coordinates / elevation / IANA tz from one committed OurAirports `airports.csv` snapshot + sha256; unit from the observed ladder | CHANGED (freeze moved from t0 to capture day 1; °F added) | 14.3 |
| STATION_COUNT_REFERENCE | 48 NOAA stations MEASURED 2026-09-29 (37 °C + 11 °F); non-NOAA (Hong Kong, Jinan, Taipei, Zhengzhou) structurally ineligible | NEW (reference, not a threshold) | 14.3 |
| SETTLEMENT_SOURCE | NOAA WRH `weather.gov/wrh/timeseries?site=<ICAO>`, whole degrees in the market unit; WU fallback; no-data → lowest bracket | UNCHANGED | V1 §20 |
| SETTLEMENT_PARSER_CONTRACT | render + archive the WRH page at D+1 02:00 local and at t_res; parse the station-local-day extreme in the market unit; reconcile with the resolved bucket's integer set; ≥ 98% agreement over ≥ 30 dates before t0 (aggregate statistic only) | UNCHANGED (+ integer-set reconciliation for °F) | 11.2 GR3 |
| SETTLEMENT_MODE | {NOAA, WU_FALLBACK, NO_DATA_LOWEST, CLARIFICATION, DISPUTED}; FINAL required for use | UNCHANGED | V1 §20 |
| FIRST_OBSERVED_FINAL_AT | our own capture time of a market's final resolved state = its `information_available_at` | NEW | 11.1 |

### A2. Trading rule R* (all UNCHANGED from V1)

| FIELD | FROZEN VALUE | STATUS |
|---|---|---|
| FORECAST_PROVIDER | Open-Meteo Ensemble API | UNCHANGED |
| FORECAST_MODEL | `ecmwf_ifs025`, 51 members, `daily=temperature_2m_max,temperature_2m_min`, station tz, `forecast_days=3` | UNCHANGED |
| LICENSED_FALLBACK | ECMWF Open Data, decided before t0 only | UNCHANGED |
| CAPTURE_CADENCE (forecast) | every 3 h + mandatory capture at T_entry − 60 min ± 30 min | UNCHANGED |
| VINTAGE_SELECTION | greatest `captured_at` with `T_entry − 3 h ≤ captured_at < T_entry` | CLARIFIED |
| ENSEMBLE_TRANSFORMATION | dressed mixture `F(x) = (1/M) Σ Φ((x − m_i − b)/σ)` | UNCHANGED |
| DRESSING_SIGMA | 1.0 °C / 1.8 °F | UNCHANGED |
| W | 30 usable resolved local dates per (station, kind) | UNCHANGED |
| BIAS_ESTIMATOR | `b = mean over BIAS_WINDOW of (y_d − mean_i m_i(d))`; `m_i(d)` = members of the vintage selected (or that would have been selected) at T_entry(d); `y_d` = mean of the resolved middle bucket's integer set (°C → integer, °F → e.g. 86.5), tail → boundary integer; all FINAL settlement modes used | CLARIFIED (°F midpoint; D10 accepted) |
| T_ENTRY | `game_start_time − 6 h` | UNCHANGED |
| h | 0.10 | UNCHANGED |
| SIGNAL_SELECTION | single argmax over 22 legs, trade iff `E_max ≥ h`; ties lower bucket, YES before NO; hold to settlement | UNCHANGED |
| FEE_MODEL | taker `0.05 × p × (1 − p)` per share; `feeSchedule` = {rate 0.05, takerOnly true, exponent 1} (MEASURED) | UNCHANGED |
| S_REF | 50 USD per leg, no capital cap | UNCHANGED |

### A3. Execution, capital, capture

| FIELD | FROZEN VALUE | STATUS | SPEC § |
|---|---|---|---|
| EXECUTION_MODEL (REALISTIC, primary) | ENTRY book; asks ≤ best ask + 0.02; 100% size; level price; min 5 shares | UNCHANGED | 15.1 |
| CONSERVATIVE_EXECUTION | worse of ENTRY / ENTRY_PLUS_5 books; asks ≤ best + 0.02; 50% size; **level price + one tick** (market `orderPriceMinTickSize` recorded with the ENTRY snapshot; fallback 0.001 if best ask < 0.04 or > 0.96 else 0.01) | CHANGED (was + 0.01) | 15.2 |
| CAPITAL_TIERS | 100 / 500 / 1,000 / 5,000 USD; stake 5% of tier; open committed ≤ tier; per-station ≤ 20% of tier | UNCHANGED | 15.3 |
| CAPITAL_ALLOCATION | ascending T_entry; identical T_entry ordered by ascending `sha256(event_id + ":WFV2")`; tier results labelled CAPACITY_CONSTRAINED_SUBSAMPLE | CHANGED (tie-break) | 15.3 |
| CAPTURE_WINDOW (ENTRY) | `captured_at ∈ [T_entry − 300 s, T_entry]`; first attempt T_entry − 240 s; retry every 20 s inside the window; per token use the valid capture with the greatest `captured_at` | CHANGED | 12.2 |
| CAPTURE_WINDOW (ENTRY_PLUS_5) | `captured_at ∈ [T_entry + 300 s, T_entry + 360 s]`; same retry rule; missing → CONSERVATIVE uses ENTRY book alone | CHANGED | 12.2 |
| captured_at SEMANTICS | host wall clock at receipt of the complete response body; = `information_available_at` | CLARIFIED | 12.1 |
| exchange_book_timestamp SEMANTICS | CLOB `timestamp` = last change of the book; never an observation time; no lower bound | CHANGED | 12.1 |
| VALID_CAPTURE | window + HTTP 200 + parse + token match + `exchange_book_timestamp ≤ captured_at + 2,000 ms` + NTP offset ≤ 250 ms (check ≤ 60 min old) + complete provenance | NEW | 12.3 |
| COMPLETENESS | entry-expected = E1–E5, E7, E8 true; complete = 22 valid captures + valid vintage; completeness = complete / entry-expected; window ≥ 95% required for validity; trailing-14-counted-date < 80% → PAUSE | CHANGED | 12.4, 11.3 |

### A4. Readiness, observation phase, t0

| FIELD | FROZEN VALUE | STATUS | SPEC § |
|---|---|---|---|
| USABLE(s, κ, d \| t) | archived selected vintage exists ∧ market FINAL with `first_observed_final_at ≤ t` ∧ settlement_mode recorded | NEW | 11.1 |
| BIAS_HISTORY_READY | ≥ 30 USABLE dates d < D at T_entry(D); window = 30 most recent; no calendar cap after t0 | CLARIFIED (= V1 E8) | 11.1 |
| FRESH_READY | BIAS_HISTORY_READY ∧ BIAS_SPAN ≤ 40 days (readiness only) | NEW | 11.1 |
| GLOBAL_READY | GR1 ≥ 80% of table stations FRESH_READY both kinds and ≥ 30 stations ≥ 1 kind; GR2 trailing-14 completeness ≥ 95%; GR3 parser ≥ 98% over ≥ 30 dates; GR4 forecast access closed; GR5 replay 100% trailing 14; GR6 mechanics codes < 10% trailing 7 | NEW | 11.2 |
| PRE_T0_OBSERVATION_PHASE | first 14 consecutive target dates with GLOBAL_READY (restart on failure); decision-only; may inspect forecasts, q, edges, triggers, prices, ticks, depth, hypothetical fills, capital demand, station/stratum shares; must not inspect any outcome, settlement or payout of a PRE_T0 decision, P&L, hit rate or winner | NEW (replaces V1 30-day burn-in) | 11.2 |
| READINESS_REPORT | committed + hashed; fields fixed in spec §11.2 (incl. descriptive OP TAIL_MAX_CONTRIBUTION, D4-R1); no outcome field | NEW | 11.2 |
| t0_PRECONDITIONS | Astra re-audit pass on this exact V2 commit; BUILDER_AUTHORIZED; Builder verification suite green; GLOBAL_READY + OP complete; readiness report with GO; STATION_TABLE / PARAMS / ENGINE / MANIFEST hashes recorded; t0 declared by Blue within 21 days after the last OP date (else OP re-run and θ_PCE recomputed by the same formula) | CHANGED | 11.2 |
| D_0 | first local target date D with T_entry(e) ≥ t0 for every table event of D | NEW | 11.3 |

### A5. Estimands, thresholds, inference

| FIELD | FROZEN VALUE | STATUS | SPEC § |
|---|---|---|---|
| ECONOMIC_ESTIMAND | strategic target `θ_P = E[N]/E[C]` over the executed-trade process (spec 8.5b) — **not an empirical estimand of V2** (no unconditional label, spec 8.5c); empirical economic estimand = θ_W (row below); `θ̂ = ΣN/ΣC`, REALISTIC, S_ref; never winsorised / trimmed | CHANGED (D4-R3: θ_P strategic only) | 5.1, 8.5c |
| REALIZED_WINDOW_ESTIMAND (D4-R2, D4-R3) | `θ_W = Σ_W n_j (p_j − c_j) / Σ_W C_j` over the trades executed in the window, p_j = true settlement probability given the information at T_entry; **the estimand of ECONOMIC_RESULT and T2 (D4-R3)** and of REALIZED_WINDOW_BOUND; never a rejection of R* | CHANGED (D4-R3) | 5.1 |
| CORE / TAIL STRATA | TAIL iff best ask of the chosen token in the ENTRY snapshot `< 0.04` (frozen constant, not the live tick field); stored at decision time | NEW | 5.2 |
| INFORMATION_ESTIMANDS | `κ_core = E[y − c \| CORE]` with c = all-in cost per share; `λ_tail = E[W_tail]/Λ_tail`, `W_tail = Σ_TAIL y`, `Λ_tail = Σ_TAIL c` | NEW | 5.3 |
| THETA_ERT | 0.02 (V1 θ_MEUE renamed; meaning unchanged; not a powered claim) | CLARIFIED | 10.1 |
| THETA_PCE_FORMULA | `σ0² = \|J\| Σ C²(1−c)/c / (ΣC)²` over OP trades; `m̄ = \|J\|/14`; `DEFF_PLAN(m) = 1.5 (1 + 0.03 (m − 1))`; `SE0_θ = σ0 √(DEFF_PLAN(m̄)/(120 m̄))`; `θ_PCE = ceil(100 × 2.4865 × SE0_θ)/100`; populated once from the OP; never recomputed after t0 | NEW | 10.2 |
| SE0_KAPPA_FORMULA | `√(mean_CORE c(1−c)) × √(DEFF_PLAN(m̄)/(120 m̄_core))` | NEW | 10.2 |
| PCE_CEILING | 0.10 | NEW | 10.3 |
| SE_KAPPA_CEILING | 0.020 | NEW | 10.3 |
| GO / NO_GO | GO iff θ_PCE ≤ 0.10 ∧ SE0_κ ≤ 0.020 ∧ OP traded stations ≥ 25 ∧ Kish ≥ 15 ∧ GLOBAL_READY on all 14 OP dates; else NO_GO_<PCE_ABOVE_CEILING \| KAPPA_UNDERPOWERED \| STATION_DIVERSITY \| READINESS> (first failing) | NEW | 10.3 |
| NULLS / ALTERNATIVES | T1a κ_core ≤ 0 vs > 0 (0.025); T1b λ_tail ≤ 1 (sharp p = c on TAIL) vs > 1 (0.025); T2 θ_W ≤ 0 vs > 0 (0.05; D4-R3 estimand); NEG κ_core ≥ 0 vs < 0 (0.025); EXCL-P θ_P ≥ threshold vs < threshold: NOT USEFULLY TESTABLE, no test (D4-R2, 8.5b); CONF-P θ_P ≤ 0 vs > 0: NOT ESTABLISHED UNCONDITIONALLY, no test (D4-R3, 8.5c); EXCL-W θ_W ≥ threshold vs < threshold (report bound U_W: core CR 0.025 + assumption-free tail supremum, D4-R1) | NEW (T2 = V1 H0/H1) | 6.1 |
| ALPHA | 0.05 one-sided; T1a, T1b at 0.025 each (Bonferroni); T2 at 0.05 unconditionally (no gate); NEG at 0.025; realised-window report bound U_W: core CR at one-sided 0.025 + deterministic tail supremum (D4-R1), declared 95%; no prospective exclusion, so no α is spent on arrival uncertainty (D4-R2); transport frontier carries no α — its only probability is T2's sampling event θ_W ≥ L_W (D4-R3); joint claims by intersection-union | CHANGED | 6.3 |
| TARGET_POWER | 0.80 at θ_PCE (nominal) | NEW | 6.2 |
| PRIMARY_INFERENCE (κ_core, θ_core, θ) | two-way cluster-robust t-test: residuals `e_j` per spec §8.1; `V_g = G/(G−1) Σ (Σ e)² / Q²` for g ∈ {block, station, block×station}; `SE = √max(V_B, V_S, V_B + V_S − V_BS)`; df = min(G_B, G_S) − 1 | CHANGED (was date-block percentile bootstrap) | 8.1 |
| AUXILIARY / TAIL ENGINE (PINM) | sharp null `p = c`; latent Gaussian copula date / station / cell (date, ICAO) with ρ = 0.10 / 0.10 / 0.10 (ASSUMED); B = 20,000 in 20 chunks of 1,000; `Generator(PCG64(SeedSequence([20260929, 1])))`; draw order dates, stations, cells, trades (T_entry, event_id, decision_id); p = (1 + #extreme)/(B + 1); gating only for T1b (no longer part of any bound, D4-R1); reported for θ, κ | NEW | 8.2 |
| T1b RULE | PINM `W_tail` upper-tail p ≤ 0.025; empty TAIL → no rejection; Poisson-binomial and block-collapsed p reported | NEW | 8.3 |
| NEG RULE | `κ̂_core + t_{df,0.975} SE < 0` (one-sided 0.025) | NEW | 8.4 |
| REALIZED_WINDOW_UPPER_BOUND (D4-R1, re-scoped D4-R2) | `U_W = w_core (θ̂_core + t_{df,0.975} SE_CR(θ̂_core)) + M_tail`, `M_tail = Σ_TAIL (n_j − C_j) / Σ_all C_j` (every realised TAIL leg wins; 0 if TAIL empty); valid for θ_W for every `p ∈ [0,1]^TAIL` under any dependence; drives only the report field REALIZED_WINDOW_BOUND; reported with w_tail, M_tail, w_core·U_core, EXCLUSION_BLOCKED_BY_TAIL (= w_core·U_core < θ_ERT ≤ U_W) | CHANGED (D4-R1 bound; D4-R2 scope θ_W, no longer drives ECONOMIC_RESULT) | 8.5 |
| PROSPECTIVE_EXCLUSION (D4-R2; wording D4-R3) | constant `NOT_USEFULLY_TESTABLE_IN_V2_HORIZON` (printed `NOT_IDENTIFIED_IN_V2` before R3); finite-horizon power ceiling spec 8.5b: c_min = 0.00104995, max payoff 951.4 per dollar, D_obs ≈ 174 observed dates (window 120 + OP 14 + pre-t0 resolved history ≤ 40; Astra m6), α = 0.05, date common modes admissible ⇒ any valid prospective exclusion test has power ≤ 0.0611 at every θ_0 ≥ −1; not asymptotic non-identification (Astra m7); zero observed TAIL arrivals never imply a zero prospective rate | CHANGED (D4-R2, D4-R3) | 8.5b |
| OPPORTUNITY_CHAIN (D4-R2, reporting) | OPPORTUNITY_UNIT (event at T_entry, ≤ 96 / date) → SIGNAL → TRIGGER (E_max ≥ h) → ATTEMPTED → EXECUTED (REALISTIC fill, the θ population) / NO_FILL_*; TAIL_ARRIVAL = executed a_j < 0.04; TAIL_TRIGGER = trigger with a_j < 0.04 | NEW (D4-R2) | 8.5b |
| TAIL_ARRIVAL_REPORT (D4-R2) | executed TAIL arrivals and unfilled TAIL_TRIGGERs by price bin [c_min, 0.002), [0.002, 0.005), [0.005, 0.01), [0.01, 0.02), [0.02, 0.04), OP and window, with capital share; descriptive | NEW (D4-R2) | 17.3 |
| PROSPECTIVE_CONFIRMATION (D4-R3) | constant `NOT_ESTABLISHED_UNCONDITIONALLY`; mirror theorem spec 8.5c: any valid level-α test of θ_P ≤ 0 has power ≤ α(1 − η)^(−D_obs), η = Aθ_0/(Aθ_0 + C_CAP_DATE) (A = ordinary expected date cost) | NEW (D4-R3) | 8.5c |
| WORST_CASE_REGIME_RETURN (D4-R3) | −1 per dollar of C, exact: N_j ≥ −C_j (all-in c_j incl. fee and walked levels; partial fills proportional; y ≥ 0 incl. void / 50-50; unresolved imputed y = 0 for favourable claims; no settlement fee; unlevered; simultaneous positions sum); invalidated by D11 fee / settlement mechanics codes | NEW (D4-R3) | 8.5c |
| COST_CAPS (D4-R3) | C_TRADE_MAX = 1.05 × S_ref = 52.5 USD; C_CAP_DATE = 2·\|STATION_TABLE\|·C_TRADE_MAX (5,040 USD at 48 stations) | NEW (D4-R3) | 8.5c |
| TRANSPORT_CLASS (D4-R3) | 𝒯_H(ε, δ): epoch laws over the next H counted dates with a partition (A, B) such that E[C_B] ≤ ε·E[C] (cost mass, any return ≥ −1) and θ_A ≥ θ_W − δ; declared assumption, never estimated, status DECLARED_UNVERIFIED | NEW (D4-R3) | 8.5c |
| ROBUST_BOUND / FRONTIER (D4-R3) | L_W = θ̂ − t_{df,0.95}·SE_CR(θ̂) (T2's bound); L_T(ε, δ) = (1 − ε)(L_W − δ) − ε; ε*(δ, τ) = max(0, (L_W − δ − τ)/(1 + L_W − δ)); error statement: only P(θ_W ≥ L_W) ≥ 0.95 (sampling), simultaneous over (ε, δ, H) | NEW (D4-R3) | 8.5c |
| TRANSPORT_REPORTING_GRIDS (D4-R3) | δ ∈ {0, 0.01, 0.02, 0.05}; τ ∈ {0, θ_ERT}; H ∈ {14, 30, 60, 120} counted dates (existing V2 constants); reporting only — **no ε, δ, H or τ threshold is frozen or used for any label**; required values belong to capital governance outside V2 | NEW (D4-R3) | 8.5c, 17.3 |
| EPOCH_TRANSLATION (D4-R3) | k*(H) = ε*·H·C̄_d / (C_CAP_DATE(1 − ε*) + ε*·C̄_d), ε* = ε*(0, 0), C̄_d = window mean executed cost per counted date (labelled volume-translation assumption) | NEW (D4-R3) | 8.5c |
| COST_MASS_CONCENTRATION (D4-R3) | C̄_d, max date cost, top-date cost share, n_eff,C = (Σ C_d)²/Σ C_d², C_CAP_DATE, cap ratio C_CAP_DATE / C̄_d, ε_1(H) = C_CAP_DATE/(C_CAP_DATE + (H − 1)C̄_d) on the H grid | NEW (D4-R3) | 8.5c, 17.3 |
| OBSERVABLE_INVALIDATION (D4-R3; future-epoch contract, design only) | flags MECHANICS (D11), STATION_UNIVERSE, TICK_FEE_REGIME, NEW_TAIL_BIN, COST_EXCEEDS_EVIDENCE (date cost > window max), TRIGGER_COUNT_OUT_OF_RANGE and FILL_DEPTH_OUT_OF_RANGE (outside window [min, max]); any flag → epoch INVALIDATED; flags can only revoke, never certify transport | NEW (D4-R3) | 8.5c |
| EPOCH_CONTRACT_FIELDS (D4-R3; design only) | EPOCH_START, EPOCH_END, EVIDENCE_VERSION, TRANSPORT_CONTRACT_VERSION, ROBUSTNESS_CERTIFICATE, REGIME_INVALIDATION_REASON | NEW (D4-R3) | 8.5c |
| RETIRED: TPM / SHR TAIL MODELS | V2@94b5934 structured tail term (λ ∈ [0.05, 1000], μ ∈ [0, 50], 40 bisection iterations) — retired from every role; not computed, not reported | RETIRED (D4-R1) | 8.5 |
| UNRESOLVED_AT_ANALYSIS | adverse imputation per claim (payout 0 for favourable tests, win for adverse tests / bounds) | NEW | 8.6 |
| DEPENDENCE_MODEL | date = local target date; block = floor((D − D_0)/5) calendar days; station = ICAO; intersection = (block, ICAO); PINM cell = (date, ICAO); never IID, never date-only | CHANGED | 9 |
| SENSITIVITY_SET (non-gating) | spec §8.7 list, exactly | NEW | 8.7 |

### A6. Horizon, states, governance

| FIELD | FROZEN VALUE | STATUS | SPEC § |
|---|---|---|---|
| MIN_INFORMATION | IF1 ≥ 60 counted dates; IF2 ≥ 12 blocks with trades; IF3 ≥ 25 traded stations and Kish ≥ 15; IF4 SE(κ̂_core) ≤ 0.025; IF5 DEFF_2w(κ̂_core) ≤ 6; else INFORMATION_INSUFFICIENT | CHANGED (was 1,000 trades / 60 dates / 30 stations) | 11.4 |
| MAX_INFORMATION | 120 counted target dates | CHANGED (was min 60 / target 90 / max 120) | 11.3 |
| COUNTED_DATE | forward date not in a PAUSE with every entry-expected event carrying an action code | NEW | 11.3 |
| PAUSE | trailing-14-counted-date completeness < 80% → pause from next date; ends after 3 consecutive paused dates each ≥ 95%; total paused > 30 → INVALID_DATA_FAILURE | CLARIFIED | 11.3 |
| INTERIM_RULE | none (no efficacy, no futility); forward P&L / κ / θ / win counts not computable before ANALYSIS_TIME | CHANGED | 11.5 |
| FINAL_ANALYSIS_DATE | 00:00 UTC on D_120 + 10 calendar days (or effective mechanics date + 10 days if truncated) | CHANGED (was "3 days after", with 60/90/120 ambiguity) | 11.3 |
| STOPPING_RULE | no stop on results; validity stops only (spec §17.1) | UNCHANGED in spirit | 11.5 |
| TERMINAL_STATE_MACHINE | VALIDITY (8 ordered rows); SCIENTIFIC = NOT_EVALUATED \| INFORMATION_INSUFFICIENT \| INFORMATION_RESULT (DETECTED / NEGATIVE / NOT_DETECTED) × ECONOMIC_RESULT on θ_W (REALIZED_WINDOW_VALUE_SUPPORTED / REALIZED_WINDOW_VALUE_NOT_ROBUST / REALIZED_WINDOW_VALUE_INDETERMINATE) = 11 values; OPERABILITY (6 ordered rows); report fields PROSPECTIVE_EXCLUSION, PROSPECTIVE_CONFIRMATION, TRANSPORT_ROBUSTNESS_REPORT, REALIZED_WINDOW_BOUND, TAIL_ARRIVAL_REPORT, INFO_SOURCE, CORE_ADVERSE; claim matrix spec 17.8 | CHANGED (D4-R2: EXCLUDED row deleted, ECONOMIC_BOUND → REALIZED_WINDOW_BOUND; D4-R3: PROSPECTIVE_VALUE_* → REALIZED_WINDOW_VALUE_* on θ_W, same conditions) | 17 |
| GATES (economic robustness) | G1 θ̂_CONSERVATIVE > 0; G2 θ̂ without top-5 N_j > 0, no date > 25%, no station > 20% of gross profit; G3 θ̂ over NOAA-mode settlements > 0 | CHANGED (V1 c2, c6 kept; c5, c9 retired; c7, c8 moved to OPERABILITY; c3 → VALIDITY; c4 → MIN_INFORMATION) | 17.2 |
| SCIENCE / OPERABILITY / VALIDITY SEPARATION | three orthogonal axes; operability never pre-empts science | NEW | 17 |
| SHADOW_CONTINUATION_RULE (was FORWARD_SIGNAL_RULE) | SHADOW_CONTINUATION_SIGNAL = VALID_COMPLETE ∧ REALIZED_WINDOW_VALUE_SUPPORTED ∧ CORE_ADVERSE = FALSE ∧ ACCESSIBLE; meaning: propose a further paper/shadow epoch only; not an edge verdict; no capital | CHANGED (D4-R2: CORE_ADVERSE, Astra m2; D4-R3: renamed, label rename only) | 17.5 |
| REJECTION_RULE (D4-R2) | `R*_REJECTED_AS_NET_STRATEGY` never issued (printed NOT_USEFULLY_TESTABLE_IN_V2_HORIZON; NOT_IDENTIFIED_IN_V2 before R3); `R*_CORE_INFORMATION_REJECTED` iff CORE_ADVERSE = TRUE (information-level, never economic) | CHANGED (D4-R2; D4-R1 rejected iff NET_VALUE_EXCLUDED; V2@94b5934 also on NEGATIVE_INFORMATION ∧ economics ≠ CONFIRMED) | 17.6 |
| MANDATORY_SENTENCES | exactly spec 17.3 (a), (b), (c): (a) when ECONOMIC_RESULT ∈ {REALIZED_WINDOW_VALUE_INDETERMINATE, REALIZED_WINDOW_VALUE_NOT_ROBUST}; (b) always; (c) when ECONOMIC_RESULT ∈ {REALIZED_WINDOW_VALUE_SUPPORTED, REALIZED_WINDOW_VALUE_NOT_ROBUST} | CHANGED (D4-R2 adds b; D4-R3 rewords b, adds c) | 17.3 |
| PLACEBO / ATTRIBUTION | B0–B6 as V1, all descriptive; V1 criterion 9 retired; ATTRIBUTION_NOT_ESTABLISHED and PLACEBO_ANOMALY flags | CHANGED | 18 |
| EXPLORATORY_FAMILY | V1 E1–E15, Holm 0.05; E8 uses tick-aware CONSERVATIVE | UNCHANGED (E8 clarified) | 23 |
| MECHANICS_CHANGE | families STRUCTURAL / READINESS / AMBIGUOUS / MECHANICS (M1–M6); share over baseline-eligible events; M3 fee change on ≥ 50% of one date's baseline-eligible events → immediate; share ≥ 50% on 14 consecutive dates → effective at first; truncate; ≥ 60 counted → VALID_TRUNCATED else INVALID_EARLY | CHANGED | 16 |
| POST_t0_MUTATION_POLICY | any material change → new experiment; no retroactive repair; byte-identical engineering fixes allowed | UNCHANGED in spirit, enumerated | 22 |
| ANTI_LEAKAGE_INVARIANTS | V1 §24 items 1–10, 12–20; item 11 replaced by CAPTURE_TIME_WINDOW; new 21 PRE_T0_OUTCOME_BLIND, 22 ANALYSIS_TIME_LOCK, 23 STRATUM_AT_DECISION, 24 CAPTURE_TIME_WINDOW | CHANGED | 25 |
| FULL_LEDGER / ACCOUNTING / SURVIVORSHIP / ACCESS | V1 §11, §21, §23 | UNCHANGED | 23 |

## B. Blocked-by-procedure items (not scientific degrees of freedom; must close before t0)

| FIELD | STATE | CLOSURE CONDITION |
|---|---|---|
| INDEPENDENT_REAUDIT | V2@94b5934 BLOCKED (D4, @7d95c00); R1 @24d2342 BLOCKED (C2, @3d18085); R2 @e45d2ce7 BLOCKED (C3, @92c2f706); D4 repair R3 PENDING | Astra bounded D4-C3 + transportability recheck of the exact repair commit |
| BUILDER_AUTHORIZED | FALSE | governance decision after a passing re-audit |
| STATION_TABLE (rows, bytes, hash) | BLOCKED_BY_PROCEDURE | compiled by the frozen membership rule before capture day 1; OurAirports snapshot bytes committed with sha256 |
| SETTLEMENT_PARSER | BLOCKED_BY_PROCEDURE | GR3 met |
| FORECAST_ACCESS | BLOCKED_BY_PROCEDURE | V1 manifest B condition, decided before t0 |
| θ_PCE, SE0_κ, Λ_120 VALUES | BLOCKED_BY_PROCEDURE | populated by the frozen formula from the OP; committed in the readiness report |
| GO / NO_GO | BLOCKED_BY_PROCEDURE | frozen rule applied to the readiness report |
| PARAMS_HASH, ENGINE_HASH, MANIFEST_HASH | BLOCKED_BY_PROCEDURE | recorded by Blue at t0 |
| t0 | NOT_DECLARED | Blue, after every row above closes |

No value in section A was chosen using settlement outcomes, resolved winners, P&L, hit rates, wallet or leaderboard data. The only live data read by the V2 Architect were market metadata fields (titles, bucket labels, descriptions, tick size, minimum size, fee schedule, resolution source) of `closed=false` events.

## C. D4 repair R1 record (after Astra re-audit @7d95c00) — HISTORICAL; rows marked SUPERSEDED are replaced by section A (Astra m3)

| Item | Frozen value | Outcome information used | Trading rule changed |
|---|---|---|---|
| Admissible tail outcome class | every `p ∈ [0,1]` per TAIL trade, any dependence | NO | NO |
| Exclusion bound | SUPERSEDED (R2): the bound survives only as REALIZED_WINDOW_UPPER_BOUND on θ_W | NO | NO |
| Economic rejection | SUPERSEDED (R2): R*_REJECTED_AS_NET_STRATEGY is never issued | NO | NO |
| Unchanged (as of R1) | R*, cohort, strata, θ, κ_core, T1a, T1b, T2, NEG, engines, dependence, PCE formula, GO / NO_GO, gates G1–G3, validity, operability, analysis time; SUPERSEDED for the SCIENTIFIC partition (11 values since R2) and the forward-signal rule (SHADOW_CONTINUATION_SIGNAL since R3) | NO | NO |
| Simulation contract | committed script implements the retired bound exactly (λ ≤ 1000, μ ≤ 50, 40 iterations, B = 20,000, frozen seed and per-draw order) for the reproduction, and the repaired bound | NO | NO |

## D. D4 repair R2 record (after Astra D4 recheck @3d18085, finding C2) — rows superseded by section E where noted

| Item | Frozen value | Outcome information used | Trading rule changed |
|---|---|---|---|
| Prospective estimand | θ_P = E[N]/E[C] over the executed-trade process (unchanged; named) | NO | NO |
| Realised-window estimand | θ_W (report-only) | NO | NO |
| Prospective exclusion | NOT_USEFULLY_TESTABLE_IN_V2_HORIZON since R3 (finite-horizon power ceiling ≤ 0.0611 at D_obs ≈ 174; spec 8.5b) | NO | NO |
| Economic axis | SUPERSEDED (R3): REALIZED_WINDOW_VALUE_{SUPPORTED, NOT_ROBUST, INDETERMINATE} on θ_W; 11-value SCIENTIFIC partition unchanged | NO | NO |
| R1 bound | kept as REALIZED_WINDOW_UPPER_BOUND on θ_W | NO | NO |
| Rejection / forward signal | R*_REJECTED_AS_NET_STRATEGY never issued; R*_CORE_INFORMATION_REJECTED and the (since R3: shadow-continuation) signal read CORE_ADVERSE | NO | NO |
| Unchanged | R*, h, W, signal, cohort, entry rule, T_entry, S_ref sizing, REALISTIC / CONSERVATIVE execution, 0.04 strata, κ_core, T1a, T1b, T2, NEG, engines, dependence, PCE formula, GO / NO_GO, gates G1–G3, validity, operability, analysis time | NO | NO |
| Simulation | `WEATHER_FORWARD_V2_D4_C2_SIM_2026-09-30.py` (run E; synthetic only) | NO | NO |

## E. D4 repair R3 record (after Astra D4-C2 recheck @92c2f706, finding C3)

| Item | Frozen value | Outcome information used | Trading rule changed |
|---|---|---|---|
| Prospective meaning | θ_P = E_Q[N]/E_Q[C] under an unrestricted future law is a strategic target, not a V2 estimand; no unconditional label in either direction | NO | NO |
| Economic axis | REALIZED_WINDOW_VALUE_{SUPPORTED, NOT_ROBUST, INDETERMINATE} on θ_W; T2, θ̂ ≥ θ_ERT, G1–G3 unchanged | NO | NO |
| Transport | 𝒯_H(ε, δ) cost-mass class; L_T(ε, δ) = (1 − ε)(L_W − δ) − ε; ε*(δ, τ); k*(H); concentration; observable invalidation (revoke-only) | NO | NO |
| Thresholds | none frozen for ε, δ, H or τ; reporting grids only | NO | NO |
| Signal | SHADOW_CONTINUATION_SIGNAL (renamed; same conditions) | NO | NO |
| Minors | m3 (this section C / D marking), m4 (checkpoint), m5 (REALIZED_WINDOW prefix note), m6 (D_obs ≈ 174), m7 ("not usefully testable") | NO | NO |
| Unchanged | R*, h, W, signal, cohort, entry rule, T_entry, S_ref sizing, REALISTIC / CONSERVATIVE execution, 0.04 strata, κ_core, T1a, T1b, T2 statistic and level, NEG, engines, dependence, PCE formula, GO / NO_GO, gates, validity, operability, analysis time, R1 U_W, R2 exclusion removal | NO | NO |
| Simulation | `WEATHER_FORWARD_V2_D4_C3_SIM_2026-09-30.py` (run F; synthetic only) | NO | NO |
