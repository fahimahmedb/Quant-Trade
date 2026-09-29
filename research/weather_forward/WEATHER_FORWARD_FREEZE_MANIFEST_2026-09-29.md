# WEATHER FORWARD FREEZE MANIFEST — 2026-09-29

```text
MANIFEST_ROLE            = enumeration of every quantity that must be immutable before t0
SPEC                     = research/weather_forward/WEATHER_FORWARD_FALSIFICATION_SPEC_2026-09-29.md
WEATHER_FORWARD_SPEC     = READY_FOR_BUILDER
REAL_CAPITAL_AUTHORIZED  = FALSE
t0                       = NOT_DECLARED (declared by Blue after burn-in; see BLOCKED-BY-PROCEDURE items)
FREEZE_RULE              = every FROZEN row below has CAN_CHANGE_AFTER_t0 = NO; a change creates a new experiment, never an amendment
```

## A. Frozen values

| FIELD | FROZEN VALUE | RATIONALE | CAN CHANGE AFTER t0? |
|---|---|---|---|
| VENUE | Polymarket international CLOB (read-only public APIs) | the only venue with the receipts under test | NO |
| MARKET_KIND | daily `Highest`/`Lowest temperature in <city> on <date>` events, 11-bucket NegRisk ladder | homogeneous, machine-classifiable cohort | NO |
| SETTLEMENT_TEMPLATE | NOAA WRH `weather.gov/wrh/timeseries?site=<ICAO>`, whole degrees, WU fallback, no-data → lowest bracket | current template (KNOWN 2026-09-29); other templates INELIGIBLE | NO |
| COHORT_RULES | E1–E8 (spec §6), reason codes, AMBIGUOUS list | deterministic inclusion, no hand edits | NO |
| STATION_TABLE_SOURCE | one named static airport table snapshot + sha256, ICAO-keyed (lat, lon, elevation, IANA tz, unit) | station, not city name, defines the target | NO (new stations → EXPLORATORY_NEW_STATION only) |
| T_ENTRY | `game_start_time − 6 h` (18:00 station-local, D−1) | precedes any observation of D; one rule for all zones; books exist | NO |
| PRIMARY_FORECAST_PROVIDER | Open-Meteo Ensemble API, `ecmwf_ifs025`, 51 members, daily max/min, station tz, forecast_days=3 | reference global ensemble; smallest sampling error; captured live | NO (provider outage → MISSING, never substitution) |
| LICENSED_FALLBACK_PROVIDER | ECMWF Open Data (data.ecmwf.int) for the same ENS fields | only if Open-Meteo access/licence fails **before t0**; after t0 a switch is a new experiment | NO |
| EXPLORATORY_MODELS | `gfs025` (31), `icon_seamless` (40), same provider | provider effect separable | NO |
| CAPTURE_CADENCE | every 3 h + mandatory capture at T_entry − 60 min ± 30 min | completeness with margin below free-tier limits | NO |
| VINTAGE_PROVENANCE | raw JSON, request URL, `captured_at`, sha256, `run_init_time` if derivable; append-only | reconstructibility; leakage audit | NO |
| SIGNAL_FORMULA | dressed ensemble: `q_k = (1/M) Σ_i [Φ((u_k − m_i − b)/σ) − Φ((l_k − m_i − b)/σ)]`; edge `E = q − a − 0.05a(1−a)` (YES) and `(1−q) − a^NO − fee` (NO); single argmax leg; trade iff `E_max ≥ h` | interpretable, economic, no fitted parameter beyond the online bias mean | NO |
| BIAS_WINDOW_W | 30 resolved local dates per (station, kind); tail boundary for tail settlements; < 30 → INELIGIBLE | standard EMOS-style training length; point-in-time | NO |
| SIGMA_DRESS | 1.0 °C / 1.8 °F | order of day-1 station error; not tuned | NO |
| HURDLE_H | 0.10 | ≈ one ensemble sampling SE at mid-probability + spread margin; not tuned | NO |
| BUCKET_ARITHMETIC | integer N ↔ [N−0.5, N+0.5); tails half-open | matches whole-degree settlement | NO |
| TIE_RULE | lower bucket index, YES before NO | determinism | NO |
| HOLD_RULE | hold to settlement, no exit/re-entry | zero exit degrees of freedom | NO |
| FEE_RULE | taker `0.05 × p × (1−p)` per share; makers not used | KNOWN docs + gamma feeSchedule | NO (a fee change is a MECHANICS_CHANGE stop) |
| EXEC_REALISTIC | book at T_entry; asks ≤ best + 0.02; 100% displayed size; level price; min 5 shares | never assumes mid; caps walking | NO |
| EXEC_CONSERVATIVE | worse of T_entry and T_entry+5 min books; asks ≤ best + 0.02; 50% size; level price + 0.01 | robustness to fading/latency | NO |
| S_REF | 50 USD per leg, no capital cap | edge measurement independent of tier | NO |
| TIERS_AND_SIZING | 100/500/1,000/5,000 USD; stake 5% of tier; open committed ≤ tier; per-station ≤ 20% of tier; T_entry-order allocation | fractional Kelly; no leverage; determinism | NO |
| CAPITAL_DEFINITION | `C_j = notional + fee` (cash leaving wallet), immobilized until `t_res + 24 h` | actual capital, not nominal volume | NO |
| PRIMARY_ESTIMAND | `θ = E[N_j]/E[C_j]`, REALISTIC execution, S_ref, eligible prospective cohort | net cash per dollar committed | NO |
| PRIMARY_HYPOTHESIS | H0: θ ≤ 0 vs H1: θ > 0; α = 0.05 one-sided; θ_MEUE = 0.02 | single primary test | NO |
| EXPLORATORY_FAMILY | E1–E15 (spec §15), Holm α = 0.05 | enumerated now; no ex-post winner | NO |
| BASELINES | B0, B1, B2, B4 (200 placebo reps, seed 20260929), B5, B6 | each answers one falsification question | NO |
| STATISTICAL_METHOD | ratio-of-means; moving-block bootstrap over target dates, block 5, 10,000 resamples, percentile; sensitivities: station cluster, two-way | dependence across cities/dates | NO |
| MIN_SAMPLE | ≥ 1,000 trades at S_ref, ≥ 60 target dates, ≥ 30 stations | SE ≈ 0.05 needed for the targeted effect sizes | NO |
| DURATION | burn-in ≥ 30 d; min 60 / target 90 / max 120 complete target dates; resolution lag 3 d | regime coverage; no early stop on results | NO |
| COMPLETENESS | gate ≥ 95%; < 80% over 14 dates → PAUSE; pauses > 30 d → INVALID | data failure handled before science | NO |
| STOP_CONDITIONS | DATA_FAILURE, MECHANICS_CHANGE (≥ 50% ineligible 14 d), LEAKAGE_DETECTED, PARAMETER_MUTATION; no efficacy/futility stops | pre-declared | NO |
| PASS_FAIL_GATE | spec §18 criteria 1–9 and state precedence | P&L > 0 alone never passes | NO |
| FULL_LEDGER_CONSTANTS | infra 10 EUR/30 d; ramp 5 EUR/30 d + 0.20%; opportunity cost 3% p.a.; taker rebates excluded from θ (sensitivity only) | declared, non-scientific | NO |
| SETTLEMENT_CONTROLS | settlement_mode recorded; page render at D+1 02:00 local and at t_res; anomaly flag rule; ≥ 98% reconciliation at burn-in | oracle/tail evidence | NO |
| SURVIVORSHIP_COHORT | wallets with ≥ 20 fills across ≥ 10 eligible events in-window; realized P&L at settlement; fee bounds all-taker/all-maker | population estimate without profit selection | NO |
| ANTI_LEAKAGE_INVARIANTS | spec §24 items 1–20 | enforced by code and replay | NO |
| ACCESS_FIELDS | ACCESS_USER_REPORTED = TRUE; LEGAL_ACCESS_CONFIRMED = UNKNOWN; circumvention forbidden | operational, separate from science | NO |

## B. Blocked-by-procedure items (not scientific degrees of freedom; must close before t0)

| FIELD | STATE | MISSING EVIDENCE | EXACT CLOSURE CONDITION |
|---|---|---|---|
| STATION_TABLE (concrete rows) | BLOCKED_BY_PROCEDURE | table not yet compiled and hashed | Builder commits the table from the named static source with sha256 for every ICAO in the current cohort; Blue records the hash in this manifest before burn-in |
| SETTLEMENT_PARSER | BLOCKED_BY_PROCEDURE | parse-vs-resolution agreement not yet measured | ≥ 98% agreement between parsed page extreme and resolved bucket over ≥ 30 burn-in days; disagreements archived |
| FORECAST_ACCESS | BLOCKED_BY_PROCEDURE | licence status and rate-limit stability UNKNOWN (429 observed on one endpoint) | either a written non-commercial/licensed status for Open-Meteo ensemble use with observed completeness ≥ 95% over burn-in, or a working ECMWF Open Data pipeline decided **before t0** |
| PARAMS_HASH, ENGINE_HASH, MANIFEST_HASH | BLOCKED_BY_PROCEDURE | code not written | recorded here by Blue at t0 declaration; asserted at every decision |
| t0 | NOT_DECLARED | burn-in not run | Blue declares t0 in governance after the three items above close; the Builder never declares t0 |

No value above was invented to complete the manifest; every blocked item is a procedure with a testable closure, not a missing scientific choice.
