# WEATHER FORWARD FALSIFICATION SPEC — 2026-09-29

```text
DOCUMENT_ROLE       = PRE-REGISTERED FORWARD FALSIFICATION PROTOCOL (FROZEN AT t0)
DOMAIN              = Polymarket daily city temperature markets ("Highest/Lowest temperature in <city> on <date>")
MISSION_TYPE        = scientific design + adversarial falsification + forward-protocol freeze
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
ACCESS_USER_REPORTED    = TRUE
LEGAL_ACCESS_CONFIRMED  = UNKNOWN
WEATHER_FORWARD_SPEC    = READY_FOR_BUILDER   (see section 27 for what this does and does not mean)
AUTHOR_ROLE         = Weather Falsification Architect (Claude Code, Builder plane)
BRANCH              = claude/intelligent-gates-msidml
COMPANION_FILES     = WEATHER_FORWARD_FREEZE_MANIFEST_2026-09-29.md, WEATHER_FORWARD_ARCHITECT_STATE_2026-09-29.md
```

Epistemic labels used throughout: **KNOWN** (verified by this author against a primary source on 2026-09-29), **INFERRED** (derived from KNOWN facts), **ASSUMED** (declared choice, not evidence), **UNKNOWN** (not established; never silently converted into an assumption).

All primary-source measurements in this document were taken on 2026-09-29 between 15:50 and 16:15 UTC from the public Polymarket Gamma/CLOB/Data APIs, docs.polymarket.com, api.weather.gov, aviationweather.gov, weather.gov/wrh and Open-Meteo. Scripts are reproducible from the endpoints named in section 8 and section 22; no wallet datasets were built.

---

## 1. Question

> Can we define TODAY, without using future outcomes, a reproducible Polymarket weather-market decision rule based only on information publicly available before trade time, and does that rule earn positive **net cashable economic value per euro of capital actually immobilized** when observed prospectively under realistic small-capital retail execution?

The protocol is designed to make the hypothesis fail. A survival is informative only because the protocol was frozen before outcomes.

Scope restriction (hard): daily Highest/Lowest temperature events only. No sports, politics, crypto, arbitrage, maker-reward farming, cross-venue trades, wallet copying, order placement or real capital.

---

## 2. Existing evidence (audit of Agents 1–3, "Ordre 13", 2026-09-29)

Sources audited in full: `research/recus_2026-09/agent1_registres.md` (branch `claude/dazzling-dirac-foklrv`), `agent2_profits_mesures.md` (`claude/gallant-cerf-e0rpao`), `agent3_recette_recu.md` (`claude/exciting-edison-w68tos`) and their `agent*_etat.md` files. These files are cited, not modified.

Status vocabulary: VERIFIED_PRIMARY / VERIFIED_SECONDARY / PROBABLE / UNVERIFIED / CONTRADICTED / NOT_RELEVANT_TO_WEATHER.

| # | CLAIM | SOURCE | PRIMARY/SECONDARY | PERIOD | WHAT IT ACTUALLY MEASURES | WHAT IT DOES NOT PROVE | LEAKAGE / SURVIVORSHIP RISK | STATUS |
|---|---|---|---|---|---|---|---|---|
| C1 | Three weather-leaderboard wallets (BeefSlayer, russell110320, HighTempTation) show +87k/+96k/+93k USD over 12 months and a winning September 2026 | Agent 1, `user-pnl-api` series + `closed-positions` | Primary API, agent-computed; not re-run here | 2025-09-29 → 2026-09-29 | Mark-to-market P&L series (all categories) and realized P&L of closed positions net of `entryFeesUsdc`, truncated at 1,500 positions per wallet | Strategy, capital immobilized, return on capital, that profit came from forecasts, or that it is repeatable | Wallets selected from a P&L-ranked leaderboard: pure survivor selection; all-categories mixing | PROBABLE |
| C2 | Same wallets positive since 2026-03-30 fee introduction (+38k/+41k/+93k, all categories) | Agent 1 | Primary API, agent-computed | 2026-03-30 → 2026-09-29 | Post-fee mark-to-market P&L, all categories | Weather-only post-fee profit; fee-period isolation for weather alone | As C1 | PROBABLE |
| C3 | Among top-1,050 weather wallets by volume, 36% are losers (ALL window); in a 20-wallet systematic sample, 4/17 active lose; median +264 USD | Agent 1, `v1/leaderboard?category=WEATHER&orderBy=VOL` + per-wallet P&L | Primary API, agent-computed | ALL / 12 months | Sign and rough distribution of leaderboard P&L among high-activity wallets | Distribution over all participants (long tail below top-1,050 UNKNOWN); ALL-window P&L mixes realized and unrealized | Selection on activity (volume) is itself survivor selection; small sample (17) | PROBABLE (weak) |
| C4 | Weather taker fee = C × 0.05 × p × (1−p); makers pay 0 and receive 25% rebate | docs.polymarket.com/trading/fees; gamma `feeSchedule` on live weather markets `{rate:0.05, takerOnly:true, rebateRate:0.25}` | Primary, re-verified here | Current (2026-09-29) | Exchange fee rule now in force | Effective date (2026-03-30 comes from Pine Analytics, secondary) | None | VERIFIED_PRIMARY (rule); PROBABLE (start date) |
| C5 | Settlement source is a Weather Underground station history page, whole degrees | Agents 1 and 3 | Primary at their time | Until ~Aug 2026 | Past resolution template | Current mechanics | Stale: the current template names NOAA (see section 20) | CONTRADICTED for current markets (superseded) |
| C6 | Unclaimed losing positions are small (−1.9k, −1.7k) for two wallets | Agent 1 | Primary API, agent-computed | 12 months | Value of unredeemed losing positions | Whether `closed-positions` realized P&L omits unredeemed losers (it appears to; magnitude small) | Accounting distortion (H7) if omitted losers were large; here small | PROBABLE |
| C7 | April 2026: Météo-France Roissy (LFPG) sensor tampered on 6 and 15 April; Polymarket temperature bets paid ~14k and ~20k USD; Météo-France filed a complaint | Agent 3; Zonebourse, Le Tribunal du Net, Bloomberg/NPR/CNN cited | Secondary (multiple independent press reports) | April 2026 | Existence of at least one physical-sensor manipulation case linked to these markets | Frequency of such events; whether current Paris station (LFPB Le Bourget, KNOWN today) was chosen because of it (UNKNOWN) | Unhedgeable tail risk (H9); not exploitable by an honest participant | VERIFIED_SECONDARY |
| C8 | Publicly known profitable weather wallets (gopfan2, aenews2, ColdMath) earn almost nothing since April 2026 | Agent 1 | Primary API, agent-computed | 2026-04 → 2026-09 | Recent P&L of previously prominent wallets | Causality (disclosure vs regime change vs regression to the mean) | Consistent with H8 (decay) and with mean reversion of selected winners | PROBABLE (fact); UNVERIFIED (interpretation) |
| C9 | Top-50 weather wallets earned +427k on 15.6M volume in the last 30 days (+2.7%) | Agent 3, `leaderboard?...timePeriod=MONTH` | Primary API, MONTH window | 30 days to 2026-09-29 | Leaderboard MONTH P&L field | Anything reliable: Agent 1 showed MONTH P&L is internally inconsistent (e.g. −732k MONTH vs −3.8k ALL, same volume). Spot check here: rank-1 by MONTH volume shows −53k | Top-50-by-P&L selection = pure survivor selection | CONTRADICTED / UNVERIFIED |
| C10 | Per-wallet 30-day figures (Bilberry +46.7k, etc.) and "styles" inferred from last 500 trades (tails, 0.21 median, favorites ≥ 0.90) | Agent 3 | Primary API, MONTH window + agent inference | 30 days | Same unreliable window; trade-price medians of selected winners | Any strategy; must not be used to define ours (section 14) | Survivor selection; strategy inference from winners is forbidden | UNVERIFIED and NOT USED |
| C11 | Public weather bots and guides exist since 2026 (competition) | Agent 1/3; GitHub repos (jattree/weather-edge, suislanchez, rainmaker-bot) | Secondary | 2026 | Existence of public competitors | Their profitability | Supports H8 (edge decay) | VERIFIED_SECONDARY |
| C12 | A public calibrated-ensemble bot post-mortem reports simulated −13.9% ± 5.3% per trade over 1,905 trades (1¢ half-spread + fee), live 210 → 51.61 USD in Sept 2026 (bugs), "the market's probabilities were better on every measure", raw models ~0.8 °C colder than airport sensors | github.com/jattree/weather-edge README (fetched 2026-09-29) | Secondary, single source, not replicated | Sept 2026 | One implementer's backtest and live run | General impossibility; timing of their comparisons vs intraday information is unclear | Their backtest is retrospective; our protocol is prospective | UNVERIFIED (directionally supports H8/H10 and baseline B1) |
| C13 | Liquidity rewards/rebates for the C1 wallets are small (0–1.3k per 30 days); weather markets are in the rewards program (min size 20 shares, max spread 4.5¢) | Agent 3; gamma `rewardsMinSize=20`, `rewardsMaxSpread=4.5` (re-verified) | Primary | Current | Rewards eligibility of weather markets; small reward income for those wallets | That taker P&L is the only source for all wallets | Rewards must be tracked separately (section 11) | VERIFIED_PRIMARY (eligibility); PROBABLE (amounts) |
| C14 | Capital actually immobilized by profitable wallets | — | — | — | Not measured by anyone | Return on capital | Denominator absent | UNKNOWN |
| C15 | Market structure: ~100 temperature events/day, 51 cities, 11 buckets, NegRisk, created ~55.5 h before the nominal end, trading open until resolution, min order 5 shares, tick 0.01 (0.001 near extremes) | This author, gamma/CLOB, 2026-09-29 | Primary | Current | Current mechanics (section 20) | Stability of mechanics over the forward window | Mechanics drift is an explicit stop condition (section 17) | VERIFIED_PRIMARY |
| C16 | Access: France is close-only per Polymarket geoblock docs; ANJ ordered ISP blocking 2026-07-16; owner reports access from their location | Agent 1; owner statement | Primary doc (geoblock) + secondary (ANJ) + owner report | Current | Policy and owner report | Legal access of the owner | Operational field only (section 21) | ACCESS_USER_REPORTED = TRUE; LEGAL_ACCESS_CONFIRMED = UNKNOWN |
| C17 | Kalshi maker/taker returns, Betfair, Metaculus, Numerai, Uniswap, Hyperliquid, Polymarket NegRisk arbitrage | Agents 1–3 | Various | Various | Other venues/mechanisms | Anything about Polymarket weather taker edge (only the general taker-loss / favorite-longshot pattern is used as motivation for baseline B6) | — | NOT_RELEVANT_TO_WEATHER |

Numbers whose construction is not understood are not carried forward: C9/C10 figures are excluded from all reasoning; C14 stays UNKNOWN.

---

## 3. What existing evidence does NOT prove

1. It does not prove a **repeatable** edge: every profitable-wallet figure is selected on realized profit (H5) and mixes categories, realized and unrealized P&L, and pre- and post-fee periods (H7).
2. It does not identify the **cause** of profit: H1 (unincorporated public forecast information), H2 (better calibration), H3 (execution/liquidity provision), H4 (private or faster information, including intraday observation of the outcome because markets trade until resolution), H6 (a few extreme events), H9 (settlement peculiarities, including sensor tampering) are all compatible with the receipts.
3. It does not prove the edge **still exists**: prominent wallets show near-zero P&L since April 2026 (C8), public competitors exist (C11), and one public calibrated attempt reports losses (C12) — consistent with H8/H10.
4. It gives no **denominator**: capital immobilized is UNKNOWN (C14), so return on capital is UNKNOWN.
5. It says nothing about **small-capital executability**: books at entry time are thin and heterogeneous (section 12).

Therefore the only admissible next step is a prospective, frozen falsification test, not deployment.

---

## 4. Primary estimand

### 4.1 Unit of observation

One **decision unit** = one eligible **event** `e = (station s, local target date D, kind κ ∈ {HIGHEST, LOWEST})` (an 11-bucket NegRisk Polymarket event). At most **one simulated leg** is opened per event. A **trade** `j` is an event on which the frozen rule opened a leg with a non-zero simulated fill.

### 4.2 Timeline per event (all UTC, all deterministic)

- `T_midnight(e)` = station-local midnight starting date D = CLOB field `game_start_time` (KNOWN: equals local midnight, e.g. London 2026-09-29T23:00Z, Seoul 2026-09-29T15:00Z).
- **Entry time** `T_entry(e) = T_midnight(e) − 6 h` (18:00 station-local civil time on D−1). Rationale: strictly before any observation of date D exists; markets have existed ≥ 20 h by then (creation ≈ 55.5 h before the nominal 12:00Z end, KNOWN); books have formed in major cities; a single rule for all time zones.
- **Information set** `I(e)` = all records with `information_available_at ≤ T_entry(e)` (section 7).
- **Settlement** at `T_res(e)` = market resolution time (first data point of the following date published, or 23:59 ET of D+1 at the latest per market text).
- **Redemption / cash availability** `T_cash(e) = T_res(e) + 24 h` (ASSUMED: manual redemption within one day).
- **Immobilization** `τ_j = (T_cash − T_entry)` in days.

### 4.3 Quantities per trade j

- Entry: token `k_j` (YES or NO of one bucket), simulated fills `{(p_i, n_i)}` walking the archived book (section 12), shares `n_j = Σ n_i`, notional `V_j = Σ p_i n_i`.
- Taker fee (KNOWN formula): `F_j = Σ_i n_i × 0.05 × p_i × (1 − p_i)` (USDC, charged on fills).
- **Capital committed** `C_j = V_j + F_j` (cash actually leaving the wallet; **not** nominal volume).
- Payout `Π_j = n_j × 1{token k_j resolves to 1}`.
- **Exchange-level net P&L** `N_j = Π_j − C_j` (rebates are NOT credited here; see 11).
- Return on committed capital `r_j = N_j / C_j`.

### 4.4 PRIMARY ESTIMAND

```text
θ  =  E[ N_j ]  /  E[ C_j ]      over trades j generated by the frozen rule R*
                                  on the prospective eligible cohort (section 6),
                                  under REALISTIC execution (section 12),
                                  at the reference stake S_ref = 50 USD per leg (section 19),
                                  estimated by  θ̂ = Σ_j N_j / Σ_j C_j.
```

Read as: **expected net cash profit per dollar of capital actually committed per trade**. It is a ratio-of-means so that large and small trades weigh by capital, not by count.

Secondary economic quantities (all reported, none primary):

- capital-time-weighted return `ρ = Σ_j N_j / Σ_j (C_j τ_j)` (per USD-day), and `ρ_30 = 30 ρ` (per month of immobilized capital);
- monthly cashable profit at tier K: `M_K = Σ_{j executed under tier K's capital rule} N_j × (30 / window_days)` (section 19);
- turnover at tier K: `Σ C_j / K` per 30 days;
- exposure overlap: max concurrent Σ C_j (open) per tier;
- **full economic net** `N^full = Σ N_j + Rebates − Infra − OnOffRamp − OpportunityCost` (section 11).

Accounting currency is USDC (pUSD); euro presentation uses the ECB reference rate on the report date (declared, non-scientific).

---

## 5. Primary hypothesis

```text
H0:  θ ≤ 0          (the frozen public-forecast rule does not earn positive net cash per dollar committed)
H1:  θ > 0
Test: one-sided, α = 0.05, moving-block bootstrap over target dates (section 13).
Minimum economically meaningful effect (MEUE): θ_MEUE = 0.02  (2 cents net per dollar committed per trade).
```

One primary hypothesis only. Rationale for θ_MEUE: at the 1,000 USD tier with ~2.5-day immobilization and full deployment, θ = 0.02 corresponds to roughly 200 USD/month before infrastructure, the smallest level worth operating; it is not derived from any historical P&L.

Power statement (INFERRED, pre-declared): per-trade returns are binary with SD ≈ 1.2 in units of committed capital at typical entry prices (0.3–0.5). With ≥ 1,000 trades and a date-cluster design effect of ≈ 2, the standard error of θ̂ is ≈ 0.05, so the test can confirm only true edges of roughly ≥ 0.10–0.13 per trade and can reject H1 at the MEUE level when the true θ is ≲ −0.05. Mid-range outcomes will land in `WEATHER_EDGE_REQUIRES_MORE_DATA` or `WEATHER_EDGE_NOT_PROVEN` by design; that is honest, not a defect.

---

## 6. Eligible cohort (frozen before outcomes)

Every event is classified by deterministic rules into ELIGIBLE / INELIGIBLE(reason) / AMBIGUOUS(reason). No event may be added or removed by hand.

**ELIGIBLE** iff all of E1–E8 hold at `T_entry`:

- E1 Gamma event has tag `weather` and title matches `^(Highest|Lowest) temperature in (.+?) on (.+)\?$`.
- E2 Market description matches the frozen **NOAA-WRH template**: contains `recorded by NOAA at the`, a resolution URL `https://www.weather.gov/wrh/timeseries?site=<code>`, `Weather Underground Daily Observations table will be used` (fallback clause), `resolve to the lowest bracket` (no-data clause), and `whole degrees` (KNOWN template text, section 20). `resolutionSource` host = `www.weather.gov`.
- E3 `<code>` (ICAO, case-insensitive) is present in the frozen `STATION_TABLE` (section 24) with latitude, longitude, elevation, IANA time zone and market unit (°C or °F).
- E4 Exactly 11 markets forming the standard ladder: one `N or below`, nine consecutive single-degree buckets, one `N or higher`, integers, unit equal to the station-table unit.
- E5 Event `createdAt ≤ T_entry − 12 h`; CLOB `accepting_orders = true` at T_entry; `game_start_time` present and equal to station-local midnight of D (computed from the frozen time zone).
- E6 Complete entry record: order-book snapshots for all 22 tokens taken in `[T_entry − 5 min, T_entry]`, and a primary-model forecast vintage captured in `[T_entry − 3 h, T_entry]` (section 8). Otherwise **MISSING** (counted against completeness, never silently dropped).
- E7 No Clarification / description change since first capture (description hash unchanged; `umaResolutionStatus` not disputed at T_entry). A change → AMBIGUOUS(rule_change).
- E8 Bias history available: ≥ 30 resolved (station, kind) days with archived T_entry vintages and settled integer values (section 9). Otherwise INELIGIBLE(bias_history), logged.

**INELIGIBLE** (reason codes): `kind_not_temperature` (e.g. "Where will it rain", tornado, precipitation, monthly events), `template_not_noaa_wrh` (e.g. Hong Kong Observatory one-decimal template, KNOWN; Weather Underground-only template, KNOWN for Jinan/Taipei), `station_unknown`, `ladder_nonstandard`, `created_too_late`, `not_accepting_orders`, `bias_history`, `missing_entry_record`.

**AMBIGUOUS**: `rule_change`, `unit_mismatch` (bucket unit ≠ station-table unit), `game_start_mismatch`, `description_deviates` (weather.gov host but template regex fails). AMBIGUOUS events are excluded from all primary and exploratory analyses and listed in the final report.

Cohort facts (KNOWN 2026-09-29): 51 cities currently listed, ~100 events/day (49 Highest + 49 Lowest + non-temperature events); 546/568 recent temperature events use the NOAA-WRH template; 22 use Weather Underground (Jinan ZSJN, Taipei RCSS); Hong Kong uses HKO one-decimal data. Units: 76 °C events, 22 °F events (US cities) in the current open set. Event volume over the last 30 days: p10 ≈ 1.1k, median ≈ 10k, p90 ≈ 59k USD. Winning bucket position over 589 resolved events: 529 middle, 42 lowest tail, 18 highest tail (the asymmetry may include no-data fallbacks; UNKNOWN).

No minimum-liquidity filter is applied to eligibility (it would be a hidden degree of freedom); liquidity enters only through executable depth in the fill model, and thin books self-limit the rule because the hurdle is computed on the executable ask.

---

## 7. Information set

A decision at `T_entry(e)` may consume only records with `information_available_at ≤ T_entry(e)`:

| Record | Available-at semantics | Permitted content |
|---|---|---|
| ORDER_BOOK_SNAPSHOT (22 tokens) | CLOB `timestamp` of the book response, must be ≤ T_entry | prices/sizes as displayed |
| FORECAST_VINTAGE (primary model, station) | `captured_at` (wall clock at fetch, ≤ T_entry); `run_init_time` if derivable | ensemble members for local date D |
| SETTLEMENT_OBSERVATION history for (s, κ) | resolution time of each past market ≤ T_entry | settled integer values of past dates only |
| MARKET/EVENT metadata | `first_captured_at` ≤ T_entry | rules text hash, ladder, station code |
| STATION_TABLE, FROZEN_PARAMETERS | frozen at t0 | constants |

Explicitly excluded from the information set: any observation of date D; any settlement; any forecast fetched after T_entry (even if its run initialised earlier); any wallet, leaderboard or trade-flow data; any revised or reanalysed weather product; any web page without an archived copy taken before T_entry.

---

## 8. Forecast sources

Only sources that Quant can consume prospectively with capture-time archiving are admissible. Provider archives are used for audit, never as the decision input.

| Source | Access (KNOWN 2026-09-29) | Update | Coverage | Issue time | Vintage availability | Limits / cost | Variable & mapping | Horizon | Same-as-real-time? | Role |
|---|---|---|---|---|---|---|---|---|---|---|
| **Open-Meteo Ensemble API, `ecmwf_ifs025`** (ECMWF IFS ENS 0.25°, 51 members) | reachable from the research container; JSON; `daily=temperature_2m_max,temperature_2m_min` with `timezone=<station tz>` returns per-member local-day extremes (KNOWN: 51 member series) | every 6 h (docs) | global | response does NOT echo run init time (KNOWN gap) → provenance = `captured_at` + content hash; availability ≈ 4–6 h after init for global models (Open-Meteo Single Runs doc) | Single Runs API archives runs by `run=` (UTC init) from 2026-04-02 for most models (audit only; ensemble members per run UNKNOWN) | free non-commercial tier 600/min, 5,000/h, 10,000/day; a 429 was observed on the previous-runs endpoint (KNOWN); pricing page says ensemble/historical need a paid plan yet the ensemble endpoint answered without a key (KNOWN) → `OPEN_METEO_LICENSE_STATUS = UNKNOWN`, treated as an operational field | 2 m temperature at station lat/lon with elevation downscaling | 15 days | Yes if captured live | **PRIMARY** |
| Open-Meteo Ensemble API, `gfs025` (GEFS 31 members) | as above (KNOWN: 31 members) | 6 h | global | as above | as above | as above | as above | 10 days | Yes if captured live | exploratory E3 |
| Open-Meteo Ensemble API, `icon_seamless` (DWD ICON EPS 40 members) | as above (KNOWN: 40 members) | 6–12 h | global | as above | as above | as above | as above | 7.5 days | Yes if captured live | exploratory E4 |
| ECMWF Open Data (data.ecmwf.int, GRIB2, CC-BY-4.0) | reachable (KNOWN index page) | 6 h, keyed by run | global | explicit in file path | explicit | free, any use; heavier engineering | raw ENS fields | 15 days | Yes | licensed fallback for PRIMARY if Open-Meteo access or license fails |
| NWS api.weather.gov gridpoint forecast | reachable; `generatedAt`/`updateTime` present (KNOWN) | ~hourly | US only | explicit | none by provider | free | deterministic maxTemperature | 7 days | Yes if captured live | NOT used (US-only, deterministic) |
| Weather pages without versioned issue times (Weather Underground forecasts, aggregator sites) | — | — | — | absent | absent | — | — | — | No | **UNSUITABLE** for the primary test |

Choice justification (ex ante, no trading results): ECMWF ENS is the reference global ensemble in WMO Lead Centre verification; 51 members give the smallest ensemble sampling error; the same provider serves the two exploratory models so provider effects can be separated. No other provider will be added during the window.

Vintage archiving rule: every capture stores the raw JSON, `captured_at`, request URL, `sha256(content)`, model id, and `run_init_time` when derivable (from Open-Meteo `model-updates` status at capture time or from the Single Runs API cross-check). Capture cadence: every 3 h for all stations and all three models, plus a mandatory capture at `T_entry − 60 min ± 30 min` per station. Captures are append-only; a later capture never overwrites an earlier one.

Observation feed for reconciliation (not for the decision): `aviationweather.gov/api/data/metar?ids=<ICAO>&hours=36` (KNOWN reachable, 72 reports/36 h for EGLC) and the rendered NOAA WRH page (section 20).

---

## 9. Signal definition (frozen rule R*)

Economic logic: buy the leg whose executable price is below the public-forecast probability by more than fees, spread and forecast sampling error. No parameter is chosen using historical P&L.

For eligible event e at T_entry, with primary vintage members `m_1..m_M` (M = 51) for the local date D and kind κ (max or min):

1. **Bias correction (point-in-time, per station and kind).** `b_{s,κ} = mean over the last W = 30 resolved local dates d < D of ( y_d − mean_i m_i(d) )`, where `y_d` is the settled integer value in the market unit and `m_i(d)` are the members of the vintage that was archived at `T_entry(d)`. Dates settled by a tail bucket use the tail boundary (censored, counted). Only dates whose market resolved before `T_entry(e)` enter. W = 30 follows the 30–40-day training windows standard in ensemble post-processing (Gneiting et al. 2005, EMOS); it is not tuned.
2. **Dressed predictive distribution.** `P(T ≤ x) = (1/M) Σ_i Φ((x − (m_i + b)) / σ)` with **σ = 1.0 °C (1.8 °F)**, a fixed kernel of the order of day-1 station forecast error; the ensemble spread itself supplies the rest of the dispersion.
3. **Bucket probabilities in the market unit.** Bucket "N" ↔ settled integer = N ↔ interval `[N − 0.5, N + 0.5)`; "N or below" ↔ `(−∞, N + 0.5)`; "N or higher" ↔ `[N − 0.5, ∞)`. `q_k = P(T ∈ bucket k)`; `Σ_k q_k = 1`.
4. **Executable prices.** `a_k^YES` = best ask of the YES token of bucket k; `a_k^NO` = best ask of the NO token (captured separately; not derived from 1 − bid). Fee per share at price a: `f(a) = 0.05 a (1 − a)`.
5. **Edge per leg.** `E_k^YES = q_k − a_k^YES − f(a_k^YES)`; `E_k^NO = (1 − q_k) − a_k^NO − f(a_k^NO)`.
6. **Decision.** Let `(k*, side*) = argmax` over the 22 legs of `E`. If `E_max ≥ h` with **h = 0.10**, open that single leg; else `NO_TRADE`. Ties → lower bucket index, YES before NO (deterministic).
7. **Hold to settlement.** No exit, no re-entry, no averaging. (Zero exit degrees of freedom.)

Hurdle justification (ex ante): the ensemble sampling standard error of a bucket probability near 0.4 with M = 51 is ≈ 0.07; typical mid-bucket spreads at T_entry are 0.02–0.05 (KNOWN snapshot); the fee is already subtracted. h = 0.10 ≈ one sampling standard error plus a spread-sized margin. It is not the P&L-maximising value of anything.

Exploratory variants (section 15) are computed from the same archived records, never by re-fetching.

Forbidden: changing M, W, σ, h, the entry time, the tie rule, the model or the sizing after t0; any per-city or per-kind parameter; any use of market outcomes, wallet behaviour or forward P&L in the rule.

---

## 10. Baselines (each answers one falsification question)

| ID | Definition | Question it answers |
|---|---|---|
| B0 | No trade (θ = 0, N = 0) | Is the rule better than doing nothing after all costs? (gate) |
| B1 | Market-only probability `m_k = mid(bid, ask)` of the YES token at T_entry, normalised over the ladder | Does the forecast carry information beyond the price? Compared by proper scores (Brier over the 11 buckets, log score of the winning bucket) with block-bootstrap CI against `q_k`. If `Brier(m) ≤ Brier(q)` with confidence, H1 is unsupported regardless of P&L. |
| B2 | Forecast-only skill of `q` (Brier, CRPS on the integer scale, reliability diagram, PIT histogram of the dressed ensemble) | Is the public forecast calibrated enough to price 1-degree buckets (H2)? A miscalibrated `q` with positive P&L points to structure, not information. |
| B3 | The rule R* (section 9) | Primary. |
| B4 | Placebo: same events, same T_entry, same sizing, leg chosen uniformly at random among legs with a displayed ask (seeded; 200 placebo replications) | Is R*'s P&L distinguishable from noise trading costs? Placebo expected value ≈ −(fee + half-spread). A positive placebo indicates structural drift or leakage. |
| B5 | Persistence rule: replace the ensemble by the single member `y_{D−1}` (yesterday's settled value for the same station and kind, available at T_entry only if resolved) with the same σ, b = 0, same h and sizing | Is profit due to NWP information or to any anchor against mispriced buckets? |
| B6 | Structural tail rule: buy the cheaper NO of the two tail buckets at T_entry if its edge under a uniform `q = 1/11` exceeds h; same sizing | Is profit explained by a longshot bias on tails rather than by forecasts? |

B4–B6 use the same execution model and the same clusters. No further baselines.

---

## 11. Economic accounting (2026)

Two ledgers are maintained for every trade and every tier.

**EXCHANGE-LEVEL NET P&L** (`N_j`, drives θ):

- taker fee `0.05 × p × (1 − p)` per share on every fill (KNOWN rule; makers pay 0; our rule is taker-only);
- spread: paid implicitly by filling at asks (never at mid);
- price impact / partial fills: modelled by walking displayed levels with a price cap and a size haircut (section 12);
- settlement at 1/0; unclaimed winners still counted as value at `T_res` (cash at `T_cash`); unclaimed losers worth 0 (no distortion possible);
- maker rebates: not applicable (taker-only);
- liquidity rewards: not applicable (no resting orders);
- taker-rebate program (KNOWN: launched 2026-05-28; 0% below 2,000 USD weighted volume/30 d, 3% at Bronze, 8% at 20k): **not credited** in exchange-level P&L; recorded as a sensitivity in the full ledger.

**FULL ECONOMIC NET P&L** (reported per tier per 30 days):

- exchange-level net;
- plus taker rebates under the tier reached by the tier's own weighted volume (sensitivity line);
- minus infrastructure: 10 EUR/30 d (ASSUMED: one small VPS; forecast data on the non-commercial tier or ECMWF open data at 0);
- minus on/off-ramp friction: 5 EUR per 30 d plus 0.20% of net deposits/withdrawals (ASSUMED; Polygon USDC bridging and fiat conversion);
- minus opportunity cost of immobilized capital: 3% p.a. on `Σ C_j τ_j` (ASSUMED risk-free proxy);
- stablecoin/chain gas for CLOB trades: 0 (KNOWN: relayed), redemption gas: 0 USD assumed (KNOWN small, included in the 5 EUR line);
- personal taxation: not modelled (mission scope);
- account/freeze risk and access risk: not monetised; reported as operational fields.

Never assume a displayed midpoint is executable.

---

## 12. Execution assumptions

Quant: no speed advantage, no colocation, small capital, automation, 24/7. Retail taker on the public CLOB.

Both models fill against the archived book at `T_entry` only.

| Parameter | REALISTIC (primary) | CONSERVATIVE (robustness) |
|---|---|---|
| Book used | snapshot at T_entry | worse of snapshots at T_entry and T_entry + 5 min (level-by-level max price / min size) |
| Levels walked | asks with price ≤ best ask + 0.02 | asks with price ≤ best ask + 0.02 |
| Price paid per level | displayed level price | displayed level price + 0.01 |
| Size available per level | 100% of displayed size | 50% of displayed size |
| Minimum order | 5 shares (KNOWN) else `NO_FILL_MIN_SIZE` | same |
| Fee | 0.05 p(1 − p) per share | same |
| Latency | fill assumed at T_entry + 0 | fill assumed at T_entry + 5 min (book above) |

Observed at ≈ T_entry for European cities (KNOWN 2026-09-29 16:14Z): mid-bucket YES ask depth within +2 ticks ≈ 140–180 USD (London, Paris), ≈ 45–60 USD (Seoul, entered 7 h earlier), < 10 USD in Ankara, Wellington and Lucknow; tail buckets have wide spreads and NegRisk ask sums far above 1 in thin ladders. Executable capacity is therefore small and heterogeneous; the tiers in section 19 measure it rather than assume it.

If the apparent edge disappears under CONSERVATIVE execution, that is a reportable result (gate criterion 2).

---

## 13. Statistical plan

Per-trade returns are binary, heavy-tailed, and dependent across cities on the same date (synoptic systems, shared market regime) and across dates at the same station (persistent biases). N trades ≠ N independent samples.

Primary estimator: `θ̂ = Σ N_j / Σ C_j`.

Primary uncertainty: **moving-block bootstrap over target dates**, block length 5 dates (synoptic regime scale 3–7 days), 10,000 resamples, percentile intervals: one-sided 95% lower bound (test), two-sided 80% and 90% intervals (economic magnitude). All trades of a date move together, so within-date cross-city dependence is preserved automatically. Sensitivity (reported, not gating): station-cluster bootstrap; two-way (date × station) pigeonhole bootstrap.

Also reported: mean and median `N_j`, hit rate, `r_j` distribution, calibration of `q` on traded legs and on all eligible buckets, Brier and log score for `q`, `m` and their average, drawdown and worst single date at every tier, tail loss (worst 1% of dates), capital-time-weighted return `ρ_30`, top-5-trade and top-date shares of gross profit, settlement-mode breakdown (NOAA / WU fallback / no-data lowest bracket / clarification), and MISSING counts.

Effective unit of independence: the **target date** (primary) with ≥ 60 dates required; station is the secondary unit with ≥ 30 stations traded.

---

## 14. Dependence handling

- One leg per event; Highest and Lowest of the same (station, date) may both be traded and are in the same date block and the same station cluster.
- Capital overlap: trades are sequenced by T_entry (Wellington first, Americas last within a date); tier capital caps are applied in that order (deterministic, no cherry-picking).
- Weather-system correlation: handled by date blocks; a 5-date block also absorbs multi-day regimes.
- Repeated markets on the same physical event: none besides Highest/Lowest; monthly or "where will it rain" markets are ineligible.
- Regime change during the window (mechanics or template change): handled by eligibility, not by re-parameterisation.

---

## 15. Multiple-testing policy

One primary test (section 5). All other analyses are **exploratory**, enumerated now, Holm-corrected within the family at α = 0.05, and never promoted to a claim without a new pre-registered window:

E1 h = 0.05; E2 h = 0.15; E3 model `gfs025`; E4 model `icon_seamless`; E5 σ = 0.5 °C; E6 σ = 1.5 °C; E7 no bias correction (b = 0); E8 CONSERVATIVE execution; E9 YES legs only; E10 NO legs only; E11 HIGHEST only; E12 LOWEST only; E13 °F stations only; E14 °C stations only; E15 EMOS calibration (nonhomogeneous Gaussian regression, 30-day window, fixed) instead of dressing.

No "best configuration" may be selected from the forward sample. The report must list every exploratory result, including the losers.

---

## 16. Forward duration and sample rules

```text
BURN_IN            ≥ 30 consecutive days of complete capture before t0 (fills the 30-day bias windows; validates settlement parsing)
START_CONDITION    t0 declared only when: capture completeness ≥ 95% over the burn-in; settlement parse agreement ≥ 98% (section 20);
                   FROZEN_PARAMETERS file hash recorded in the freeze manifest; parameter file made read-only; Blue declares t0 in governance
MINIMUM_DURATION   60 complete target dates after t0
TARGET_DURATION    90 complete target dates
MAXIMUM_DURATION   120 complete target dates, then analysis regardless of N
MINIMUM_SAMPLE     ≥ 1,000 trades with non-zero fills at S_ref (REALISTIC), ≥ 60 target dates, ≥ 30 distinct stations traded
DATA_COMPLETENESS  ≥ 95% of eligible events must have a complete entry record (E6) over the window; MISSING is reported, never dropped silently
RESOLUTION_LAG     analysis starts 3 days after the last target date (all markets resolved or classified)
```

Rationale: 60 dates give ≥ 12 five-date blocks and span a seasonal transition (autumn/spring); 1,000 trades is the smallest sample at which the standard error (≈ 0.05) can discriminate the effect sizes the rule targets (section 5). Nothing stops early because results look good.

---

## 17. Stop conditions (pre-declared)

- **No early stopping on results** (neither efficacy nor futility).
- DATA_FAILURE: completeness < 80% over any 14 consecutive dates → PAUSE; dates during the pause are excluded as MISSING; the window is extended by the pause length; if pauses exceed 30 days, the run is `WEATHER_FORWARD_TEST_INVALID` and restarts from burn-in.
- MECHANICS_CHANGE: if ≥ 50% of daily temperature events become INELIGIBLE/AMBIGUOUS for 14 consecutive dates (template change, fee change, ladder change), the run ends and the state is `WEATHER_EDGE_OPERATIONALLY_INACCESSIBLE` with reason `MECHANICS_CHANGED`; a new spec is required (fee-rate changes are mechanics changes: the fee constant is frozen).
- LEAKAGE_DETECTED: any decision found to depend on a record with `information_available_at > T_entry` → run `WEATHER_FORWARD_TEST_INVALID`.
- PARAMETER_MUTATION: any change to frozen parameters after t0 → run INVALID.

---

## 18. Pass/fail gate

Terminal states: `WEATHER_EDGE_REJECTED`, `WEATHER_EDGE_NOT_PROVEN`, `WEATHER_EDGE_REQUIRES_MORE_DATA`, `WEATHER_EDGE_FORWARD_SIGNAL`, `WEATHER_EDGE_OPERATIONALLY_INACCESSIBLE`. Orthogonal validity flag: `VALID` / `INVALID` (section 17).

Let `L95` = one-sided 95% lower bound, `U95` = one-sided 95% upper bound, `L80` = lower bound of the two-sided 80% interval of θ̂ (REALISTIC).

`WEATHER_EDGE_FORWARD_SIGNAL` requires **all** of:

1. **Positive net economics**: `L95 > 0`.
2. **Robust to execution**: `θ̂_CONSERVATIVE > 0` (point estimate) and `θ̂_REALISTIC ≥ θ_MEUE = 0.02`.
3. **No leakage**: 100% of decisions reconstructed by the replay tool from archived records only, zero information-time violations, freeze hash unchanged, forecast capture timestamps all < T_entry.
4. **Non-trivial sample**: minimum sample and duration of section 16 met.
5. **Interval compatible with meaningful value**: `L80 ≥ θ_MEUE / 2 = 0.01`.
6. **No freak concentration**: θ̂ remains > 0 after removing the 5 largest `N_j`; no single date contributes > 25% and no single station > 20% of gross profit; settlement-mode breakdown shows profit is not driven by no-data/clarification outcomes (θ̂ excluding those > 0).
7. **Operational accessibility**: ≥ 80% of R* triggers are fillable at the 500 USD tier stake within the price cap; completeness ≥ 95%; `ACCESS_STATUS` recorded (an UNKNOWN legal status does not block this state but is carried as `ACCESS_UNCONFIRMED`).
8. **Capital efficiency**: `ρ_30 ≥ 0.05` (≥ 5% per 30 days on immobilized capital) at the 1,000 USD tier under REALISTIC execution, net of exchange-level costs.
9. **Attribution**: R* beats B4 (placebo) and B5 (persistence) point estimates by ≥ θ_MEUE, so that profit is attributable to forecast information rather than to structure or noise.

Other states (evaluated in this order after validity):

- `WEATHER_EDGE_OPERATIONALLY_INACCESSIBLE`: mechanics changed (17), or criterion 7 fails, or legal access is confirmed impossible.
- `WEATHER_EDGE_REJECTED`: sample met and `U95 < θ_MEUE` (a meaningful edge is excluded), or `θ̂ < 0` with `U95 < 0.02` and B2 shows `q` has no skill over B1 on the traded legs.
- `WEATHER_EDGE_NOT_PROVEN`: sample met, `L95 ≤ 0`, and at least one of criteria 6 or 9 fails, or `θ̂ < θ_MEUE`.
- `WEATHER_EDGE_REQUIRES_MORE_DATA`: maximum duration reached, `L95 ≤ 0 < θ̂`, `θ̂ ≥ θ_MEUE`, criteria 3, 6, 7 and 9 hold.
- Any state reached with `INVALID` is not a scientific result.

`P&L > 0` alone never passes.

---

## 19. Small-capital economics

Tiers (USDC, presented in EUR at the report-date ECB rate): **100, 500, 1,000, 5,000**.

Sizing rule (frozen, fractional-Kelly justified: at a 10-point edge and price 0.4, full Kelly ≈ 17%, so 5% ≈ 0.3 Kelly): stake per leg `S_K = 0.05 × K`; shares `= floor(fillable notional within the price cap, capped at S_K) / fill price`; minimum 5 shares. Reference stake for θ: `S_ref = 50 USD` without a capital cap (edge measurement). Tier ledgers apply a hard cap: open committed capital ≤ K (no leverage); when cash < S_K the event is logged `NO_TRADE_CAPITAL` (capacity finding, not part of θ).

For each tier the analysis must estimate: number of executable opportunities per 30 days; average and maximum concurrent capital immobilized; turnover; expected net USD per 30 days (exchange-level and full economic); worst drawdown and worst date; capacity ceiling = the smallest stake at which ≥ 50% of triggers become depth-constrained; and the share of triggers lost to `NO_FILL_MIN_SIZE` or `NO_TRADE_CAPITAL`. No linear extrapolation beyond observed depth is permitted.

---

## 20. Oracle, settlement and tail-risk controls

Current settlement mechanics (KNOWN from live market text, 2026-09-29):

- Source: NOAA page `https://www.weather.gov/wrh/timeseries?site=<ICAO>`; value = highest/lowest reading under the "Temp" column for all times on the local date; whole degrees in the market unit. The page's script loads `https://api.synopticdata.com/v2/stations/timeseries?STID=...&obtimezone=local&units=temp|F` with an embedded token and converts units client-side (KNOWN from `obs.js`). Hence the displayed value is a station-local-day extreme of Synoptic/METAR-type reports, unit-converted and rounded in the page — the exact conversion/rounding chain is **UNKNOWN**.
- Fallback 1: Weather Underground Daily Observations table if NOAA data are unavailable by 23:59 ET on D+1.
- Fallback 2: **no data by 23:59 ET on D+1 → resolves to the lowest bracket** (a non-weather outcome).
- Resolution timing: first data point of the following date or 23:59 ET on D+1.
- Erroneous or tampered data: market may stay open up to 7 calendar days for a correction; otherwise a Clarification decides (clause present in the newest template only, 21/568 recent events).
- Revisions after the first data point of the following date are ignored.
- Trading continues until resolution, so intraday observations are tradable by others (H4 channel); our T_entry excludes this channel by construction.

Controls encoded in the protocol:

1. `SETTLEMENT_MODE ∈ {NOAA, WU_FALLBACK, NO_DATA_LOWEST, CLARIFICATION, DISPUTED}` recorded per event from the market's final text/status and from the parsed page; primary analysis includes all modes (economic reality), secondary excludes non-NOAA modes; gate criterion 6 requires profit not to depend on them.
2. The Builder archives the rendered settlement page (HTML + screenshot + parsed table) at `T_midnight(D+1) + 2 h` and again at `T_res`; the parsed extreme is reconciled against the resolved bucket. Burn-in acceptance requires ≥ 98% agreement; disagreements are logged with the raw captures.
3. Sensor anomaly flag: |settled value − max/min of aviationweather METAR for the same local day| ≥ 2 degrees, or a jump ≥ 4 degrees within 30 minutes in the timeseries → `OBS_ANOMALY = TRUE` (descriptive; feeds the tail-risk report; not an exclusion). The Roissy case (C7) is the reference example; such events are unhedgeable tail risk for an honest participant, not an edge.
4. Station identity: only ICAO codes in the frozen STATION_TABLE; Paris is LFPB (Le Bourget), NYC is KLGA, Denver is KBKF, London is EGLC (KNOWN) — the table, not the city name, defines the station.
5. Ambiguous wording, unit mismatch, or template deviation → AMBIGUOUS (excluded).
6. Provider disagreement (NOAA page vs WU vs METAR) is measured during burn-in and reported; it is a property of the target, absorbed by bias correction in the mean only.
7. Per-station exposure at any tier ≤ 20% of tier capital (concentration control); this is part of the sizing rule and frozen.

---

## 21. Access assumptions

```text
ACCESS_USER_REPORTED    = TRUE      (owner statement, 2026-09-29)
LEGAL_ACCESS_CONFIRMED  = UNKNOWN   (not inferred from nationality or from the report)
GEOBLOCK_CHECK          = NOT_PERFORMED_FROM_OWNER_LOCATION
CIRCUMVENTION           = FORBIDDEN (no VPN/proxy advice; a blocked location ends operational accessibility)
FORWARD_TEST_ACCESS     = READ-ONLY PUBLIC APIs (no account, no orders); reachable from the research container (KNOWN)
OPEN_METEO_LICENSE_STATUS = UNKNOWN (non-commercial research assumed for the paper test; ECMWF open data is the licensed fallback)
SYNOPTIC_TOKEN_STATUS   = UNKNOWN (the Builder must not reuse the page's embedded token; render the public page or obtain a token under Synoptic's terms)
```

Access uncertainty is an operational field; it does not invalidate the scientific experiment.

---

## 22. Builder data schema (minimum durable schema)

Conventions: all timestamps UTC ISO-8601 with millisecond precision; `captured_at` = wall clock at receipt; `information_available_at` = the earliest time the record could have been known (never later than `captured_at`); every raw payload stored append-only with `sha256`; every derived row references the raw rows it came from. REQ = required, OPT = optional.

### STATION (frozen at t0)
| NAME | TYPE | SOURCE | TIMESTAMP SEMANTICS | REQ | WHY |
|---|---|---|---|---|---|
| icao | str(4) | market resolution URL | static | REQ | station identity |
| city_label | str | gamma title | static | REQ | join key to events |
| lat, lon, elevation_m | float | frozen static table (named source + hash) | static | REQ | forecast point |
| tz_iana | str | frozen table | static | REQ | local midnight / local day |
| market_unit | enum(C,F) | observed ladder | static | REQ | bucket arithmetic |
| table_source, table_hash | str | manifest | frozen | REQ | provenance |

### EVENT / MARKET
| NAME | TYPE | SOURCE | TIMESTAMP SEMANTICS | REQ | WHY |
|---|---|---|---|---|---|
| event_id, slug, title | str | gamma | first_captured_at | REQ | identity |
| kind | enum(HIGHEST,LOWEST) | title regex | — | REQ | cohort |
| icao, target_date_local | str, date | description/URL, title | — | REQ | cohort, clustering |
| created_at, game_start_time, end_date_nominal | ts | gamma, CLOB | provider | REQ | E5, T_entry |
| t_entry | ts | computed | = game_start − 6 h | REQ | information boundary |
| description_hash_first, description_hash_at_entry | str | gamma | first capture, T_entry | REQ | E7 |
| resolution_source_url, template_id | str | gamma | first capture | REQ | E2 |
| market_id[11], condition_id[11], token_yes[11], token_no[11], bucket_low[11], bucket_high[11] | arrays | gamma/CLOB | first capture | REQ | ladder |
| fee_rate, min_order, tick | num | gamma/CLOB | first capture | REQ | cost model; mechanics-change detection |
| eligibility, eligibility_reason | enum, str | computed at T_entry | T_entry | REQ | cohort audit |

### ORDER_BOOK_SNAPSHOT
| NAME | TYPE | SOURCE | TIMESTAMP SEMANTICS | REQ | WHY |
|---|---|---|---|---|---|
| snapshot_id, token_id | str | CLOB `/book` | — | REQ | identity |
| book_timestamp | ts | CLOB `timestamp` | provider clock | REQ | information_available_at |
| captured_at | ts | local | receipt | REQ | leakage audit |
| bids[], asks[] (price, size) | arrays | CLOB | — | REQ | executable prices and depth |
| purpose | enum(ENTRY, ENTRY_PLUS_5, PERIODIC) | scheduler | — | REQ | execution models |
| raw_hash | str | local | — | REQ | immutability |

### FORECAST_VINTAGE (+ members)
| NAME | TYPE | SOURCE | TIMESTAMP SEMANTICS | REQ | WHY |
|---|---|---|---|---|---|
| vintage_id, icao, model_id | str | scheduler | — | REQ | identity |
| request_url | str | local | — | REQ | reproducibility |
| captured_at | ts | local | receipt (= information_available_at) | REQ | leakage boundary |
| run_init_time | ts | derived (model-updates status / single-runs cross-check) | provider | OPT | audit; availability-lag invariant |
| target_date_local, tz_iana | date, str | request | — | REQ | local-day alignment |
| members_max[M], members_min[M] | float arrays | response | — | REQ | signal |
| n_members | int | response | — | REQ | sanity (51/31/40) |
| raw_hash | str | local | — | REQ | immutability |

### SETTLEMENT_OBSERVATION (page captures and METAR)
| NAME | TYPE | SOURCE | TIMESTAMP SEMANTICS | REQ | WHY |
|---|---|---|---|---|---|
| icao, local_date, capture_purpose | str, date, enum(D_PLUS_1, AT_RESOLUTION) | scheduler | — | REQ | reconciliation |
| page_html_hash, screenshot_hash | str | rendered NOAA WRH page | captured_at | REQ | oracle evidence |
| parsed_max, parsed_min, parsed_unit, n_rows, first_row_ts, last_row_ts | num/str/int/ts | parser | captured_at | REQ | settlement value as displayed |
| metar_max, metar_min, n_metar | num, int | aviationweather | captured_at | OPT | anomaly flag, bias diagnostics |
| obs_anomaly | bool | computed | — | REQ | tail-risk report |

### SIGNAL_DECISION
| NAME | TYPE | SOURCE | TIMESTAMP SEMANTICS | REQ | WHY |
|---|---|---|---|---|---|
| decision_id, event_id, rule_id (R* or exploratory/baseline id) | str | engine | decided_at (must be ≥ T_entry and reference only records ≤ T_entry) | REQ | identity |
| vintage_id, snapshot_ids[22] | refs | engine | — | REQ | reconstructibility |
| bias_b, bias_n_days, sigma, h, M | num | engine | — | REQ | frozen-parameter echo |
| q[11], a_yes[11], a_no[11], fee_yes[11], fee_no[11], edge_yes[11], edge_no[11] | arrays | engine | — | REQ | audit of the argmax |
| chosen_leg, edge_max, action | str, num, enum(TRADE, NO_TRADE, NO_TRADE_CAPITAL, NO_FILL_MIN_SIZE, INELIGIBLE, MISSING) | engine | — | REQ | outcome |
| params_hash | str | frozen file | — | REQ | mutation detection |

### SIMULATED_ORDER / SIMULATED_FILL
| NAME | TYPE | SOURCE | TIMESTAMP SEMANTICS | REQ | WHY |
|---|---|---|---|---|---|
| order_id, decision_id, tier, exec_model | str, enum(REF, T100, T500, T1000, T5000), enum(REALISTIC, CONSERVATIVE) | engine | T_entry (+5 min for CONSERVATIVE) | REQ | identity |
| token_id, side, stake_target | str, enum(BUY), num | engine | — | REQ | what was attempted |
| fills[] (level_price, price_paid, shares, fee) | array | fill model over snapshot | — | REQ | cost accounting |
| shares, notional, fee_total, capital_committed | num | sum | — | REQ | C_j |
| fill_status | enum(FULL, PARTIAL, NONE_MIN_SIZE, NONE_DEPTH) | engine | — | REQ | capacity metrics |

### SETTLEMENT
| NAME | TYPE | SOURCE | TIMESTAMP SEMANTICS | REQ | WHY |
|---|---|---|---|---|---|
| event_id, resolved_bucket_index, settled_value_int (or tail boundary), settlement_mode | int, enum | gamma/CLOB final state + description | t_res | REQ | payout, bias history |
| t_res, t_cash | ts | gamma `closedTime`/resolution + 24 h | provider / computed | REQ | immobilization |
| resolution_text_final_hash, clarification_flag, dispute_flag | str, bool | gamma | t_res | REQ | H9 |

### PNL
| NAME | TYPE | SOURCE | TIMESTAMP SEMANTICS | REQ | WHY |
|---|---|---|---|---|---|
| order_id, payout, net_pnl_exchange, return_on_committed, tau_days | num | computed at t_cash | t_cash | REQ | θ, ρ |
| rebate_sensitivity, infra_alloc, ramp_alloc, opp_cost, net_pnl_full | num | computed per tier per 30 d | report | REQ | full economic ledger |
| cluster_date, cluster_station | date, str | event | — | REQ | bootstrap |

### CAPITAL_USAGE (per tier, per event in T_entry order)
| NAME | TYPE | SOURCE | TIMESTAMP SEMANTICS | REQ | WHY |
|---|---|---|---|---|---|
| tier, t, cash_available_before, committed_open_before, committed_after, per_station_exposure | num | ledger | T_entry | REQ | overlap, capacity, 20% station cap |
| capacity_flags | set | ledger | — | REQ | NO_TRADE_CAPITAL accounting |

### WALLET_TRADE (survivorship cohort only; never joined to decisions)
| NAME | TYPE | SOURCE | TIMESTAMP SEMANTICS | REQ | WHY |
|---|---|---|---|---|---|
| condition_id, proxy_wallet, side, outcome_index, price, size, timestamp, tx_hash | str/num | `data-api /trades?market=` | provider | REQ | section 23 cohort |

Provenance for every derived row: `(engine_version_hash, params_hash, input_row_hashes[])`. Nothing is ever updated in place; corrections are new rows with `supersedes`.

---

## 23. Survivorship test (descriptive, separate from the rule)

Purpose: estimate how common success is among weather participants **without selecting on profitability**.

- Cohort rule (frozen): all `proxyWallet` addresses with ≥ 20 fills across ≥ 10 distinct ELIGIBLE events whose T_entry lies in the forward window, collected prospectively from `data-api /trades?market=<condition_id>` for every eligible event (bounded: ~100 events/day).
- Realized P&L per wallet: cash flows of fills (buys −, sells +) plus settlement of net positions at 1/0 at `t_res`, valued whether or not redeemed (unclaimed winners count at value; unclaimed losers 0). Fees: maker/taker status is not exposed by the endpoint (KNOWN), so report bounds: all-taker (lower) and all-maker (upper) fee treatments.
- Report: fraction of wallets with positive realized P&L; median and quartiles; concentration of total positive P&L (top-1, top-5, top-10 shares); by activity decile; number of wallets.
- Interpretation: descriptive evidence about the population; it is neither proof nor refutation of R*. Wallet data never enter the rule, the cohort or the gate.
- No identities are sought behind addresses.

---

## 24. Anti-leakage invariants (Builder must enforce; each is testable)

1. `DECISION_TIME_BOUND`: a decision for event e references only records with `information_available_at ≤ T_entry(e)`; violation → run INVALID.
2. `FORECAST_CAPTURE_BEFORE_ENTRY`: `FORECAST_VINTAGE.captured_at < T_entry(e)`; a vintage captured after T_entry is never used for e, whatever its `run_init_time`.
3. `AVAILABILITY_LAG`: when `run_init_time` is known, `captured_at ≥ run_init_time` and the vintage's `captured_at ≤ T_entry`; a run whose products are published after T_entry is unusable even if it initialised before.
4. `NO_REVISION_OVERWRITE`: forecast, book, page and market rows are append-only; a re-fetch creates a new row; the row used by a decision is bound by hash.
5. `OUTCOME_ISOLATION`: settlement rows may not be joined to any feature or decision of the same event; they may enter the bias history only for events with `t_res ≤ T_entry` of the deciding event.
6. `NO_INTRADAY_OBSERVATION`: no observation with `obs_time ≥ T_midnight(e)` may exist in the information set of e (T_entry precedes midnight by 6 h, but the rule must be enforced by query, not by assumption).
7. `PARAMS_READ_ONLY_AFTER_T0`: `FROZEN_PARAMETERS` file hash is recorded at t0 and asserted at every decision; mismatch → INVALID.
8. `NO_WALLET_DATA_IN_SIGNAL`: the decision engine has no read access to WALLET_TRADE, leaderboard or P&L endpoints.
9. `COHORT_BY_RULE_ONLY`: eligibility is computed by code from E1–E8 at T_entry; no manual lists; hindsight inclusion is impossible because eligibility is stored at T_entry.
10. `STATION_TABLE_FROZEN`: station coordinates/time zones cannot change after t0; new stations are tracked as EXPLORATORY_NEW_STATION and excluded from the primary cohort.
11. `SNAPSHOT_TIME_WINDOW`: entry books must have `book_timestamp ∈ [T_entry − 5 min, T_entry]`; else MISSING.
12. `NO_PROVIDER_ARCHIVE_AS_INPUT`: Open-Meteo Previous/Single-Runs/Historical APIs are audit-only; decisions never read them.
13. `NO_REANALYSIS`: no reanalysis, climate or "historical weather" product enters any feature.
14. `REPLAY_EQUIVALENCE`: an offline replay from archived rows must reproduce every decision byte-for-byte (same `decision_id` content hash); the final report includes the replay result.
15. `EXPLORATORY_FROM_ARCHIVE_ONLY`: exploratory variants are computed from the same archived vintages/snapshots; no new fetches.
16. `TIER_ORDER_DETERMINISM`: capital caps are applied in T_entry order; ties by event_id.
17. `SETTLEMENT_MODE_RECORDED`: every resolved event has a settlement_mode; unknown → DISPUTED until classified.
18. `MISSING_IS_COUNTED`: MISSING events are counted in completeness and listed; they never disappear.
19. `NO_MID_WINDOW_MODEL_SWITCH`: primary model id is a frozen constant; provider outages produce MISSING, not substitution.
20. `CLOCK_DISCIPLINE`: the capture host runs NTP; `captured_at` uses the host clock; provider timestamps are stored alongside and never replace `captured_at`.

---

## 25. Frozen parameters

```text
PRIMARY_MODEL            = open-meteo ensemble-api, models=ecmwf_ifs025 (51 members)
EXPLORATORY_MODELS       = gfs025 (31), icon_seamless (40)
FORECAST_VARIABLES       = daily temperature_2m_max, temperature_2m_min, timezone=<station tz>, forecast_days=3
CAPTURE_CADENCE          = every 3 h, plus T_entry − 60 min ± 30 min
T_ENTRY_RULE             = game_start_time − 6 h
BIAS_WINDOW_W            = 30 resolved local dates, per (station, kind); tail settlements use the boundary value
BIAS_FALLBACK            = none: < 30 dates → INELIGIBLE(bias_history)
SIGMA_DRESS              = 1.0 °C (1.8 °F)
BUCKET_ARITHMETIC        = integer N ↔ [N − 0.5, N + 0.5); tails half-open as in section 9
HURDLE_H                 = 0.10
LEG_SELECTION            = single argmax over 22 legs; ties → lower bucket, YES before NO
HOLD_RULE                = hold to settlement; no exit
FEE_RATE                 = 0.05 × p × (1 − p) per share (taker); mechanics change if it differs
EXEC_REALISTIC           = book at T_entry; levels ≤ best ask + 0.02; 100% size; level price
EXEC_CONSERVATIVE        = worse of T_entry and T_entry + 5 min; levels ≤ best ask + 0.02; 50% size; level price + 0.01
MIN_ORDER                = 5 shares
S_REF                    = 50 USD per leg, no capital cap
TIERS                    = 100, 500, 1,000, 5,000 USD; stake 5% of tier; open committed ≤ tier; per-station ≤ 20% of tier
T_CASH                   = t_res + 24 h
FULL_LEDGER_CONSTANTS    = infra 10 EUR/30 d; ramp 5 EUR/30 d + 0.20%; opportunity cost 3% p.a.
BOOTSTRAP                = moving-block over target dates, block 5, 10,000 resamples, percentile
ALPHA                    = 0.05 one-sided (primary); Holm within the 15-variant exploratory family
THETA_MEUE               = 0.02
MIN_SAMPLE               = 1,000 trades, 60 dates, 30 stations
DURATION                 = min 60 / target 90 / max 120 complete target dates; burn-in ≥ 30 days
COMPLETENESS             = ≥ 95% (gate), < 80% over 14 dates → PAUSE
BASELINES                = B0, B1, B2, B4 (200 placebo replications, seed 20260929), B5, B6
PLACEBO_SEED             = 20260929
```

---

## 26. Open unknowns (carried, not assumed away)

1. Exact unit-conversion and rounding chain of the NOAA WRH page (Synoptic °F → page °C) — UNKNOWN; measured during burn-in via reconciliation; the bias term absorbs the mean.
2. Frequency of `NO_DATA_LOWEST`, `WU_FALLBACK`, Clarification and dispute outcomes — UNKNOWN; recorded prospectively.
3. Whether Open-Meteo ensemble access is licensed for this use and whether the observed 429 recurs — UNKNOWN; fallback is ECMWF open data.
4. Whether ensemble members are retrievable per archived run for audit — UNKNOWN (docs mention only an ensemble mean); audit may be limited to means.
5. Effective start date of the weather fee (2026-03-30 per a secondary source) — irrelevant to the forward test (rule is current) but PROBABLE only.
6. Capital immobilized by profitable wallets (C14) — UNKNOWN; not needed by the protocol.
7. Whether Polymarket will change the city list, template, ladder or fees during the window — UNKNOWN; handled by section 17.
8. Legal access status of the owner — UNKNOWN; operational field.
9. Whether the 6-hour pre-midnight entry leaves enough liquidity in Asian/Southern-Hemisphere cities — measured, not assumed (capacity metrics).

---

## 27. Final self-audit (attack on this design)

| ATTACK | DOES SPEC PREVENT IT? | EVIDENCE |
|---|---|---|
| Leakage: a forecast run that initialised before T_entry but was fetched after it is used for the decision (or a provider archive is silently used to "fill gaps") | YES | Invariants 2, 3, 12, 19: only vintages with `captured_at < T_entry` are usable; archives are audit-only; gaps become MISSING |
| Leakage: intraday observation of date D enters via the bias history or a late book snapshot | YES | Invariants 5, 6, 11: bias uses only events resolved before T_entry; entry books must be ≤ T_entry; T_entry is 6 h before local midnight |
| Survivorship: cities/stations that "work" are kept, others dropped after seeing results; or the window is stopped when ahead | YES | E1–E8 computed at T_entry and stored; invariants 9, 10; no early stopping (17); all exploratory results must be listed (15) |
| Accounting false positive: unclaimed losers ignored, rebates counted, mid-price fills, fee omitted | YES | Section 4/11: losers worth 0 by construction; rebates excluded from θ; fills only at displayed asks with cap; fee on every fill |
| Execution false positive: displayed depth assumed executable, stale book | PARTIALLY | REALISTIC still assumes displayed size at T_entry is hit; CONSERVATIVE (50% size, +1 tick, worse of two books) is a gating criterion (18.2). Residual risk: quote fading by makers who watch the same models is not modelled; this cannot be resolved without live orders, which are not authorised. Declared as the main execution caveat, not as a validity defect |
| Dependence/statistical false positive: 1,000 trades treated as independent; one hot week drives the CI | YES | Block bootstrap over dates (13); ≥ 60 dates and ≥ 12 blocks; concentration criterion 18.6 |
| Oracle/settlement failure: station outage resolves to the lowest bracket; sensor tampering; unit rounding mismatch | YES (measured, not eliminated) | Settlement_mode recorded; gate 18.6 excludes profit driven by non-NOAA modes; anomaly flag; per-station 20% cap; reconciliation ≥ 98% at burn-in |
| Historical wallet evidence misleads: the rule is nudged toward what winners appear to do (tails, favorites) | YES | Section 14 separation; invariant 8; C10 marked NOT USED; the rule's only inputs are ensemble members, past settled values and the book |
| Hidden degree of freedom: burn-in results influence σ, h or W before t0 | YES | Values are fixed in this document and in the manifest before any burn-in; the manifest forbids change; burn-in only validates capture and parsing |
| Multiple testing: an exploratory variant is reported as the finding | YES | Section 15: Holm within family; promotion requires a new pre-registered window |
| Mechanics drift: fee or template changes mid-window make results incomparable | YES | Section 17 MECHANICS_CHANGE stop rule; fee constant is frozen |

No attack found that invalidates the experiment as specified; the residual execution caveat is disclosed and gated by the CONSERVATIVE model.

---

## 28. Status and exact implementation mission for the future Builder

```text
WEATHER_FORWARD_SPEC     = READY_FOR_BUILDER
MEANING                  = the forward falsification experiment is specified without scientific degrees of freedom
                           left to the Builder; every constant is in section 25 and in the freeze manifest
NOT_MEANING              = edge proven / profitable strategy / capital authorised / live trading authorised
REAL_CAPITAL_AUTHORIZED  = FALSE
```

Builder mission (sequential, paper/shadow only, no orders, no accounts, no circumvention):

1. **Station table**: compile `STATION_TABLE` for every ICAO code present in NOAA-WRH-template weather events observed over the last 30 days plus the current open set (currently: EHAM, LTAC, KATL, KAUS, ZBAA, SAEZ, RKPK, FACT, ZUUU, KORD, ZUCK, KDAL, KBKF, ZGGG, EFHK, KHOU, LTFM, OEJN, OPKC, WMKK, EGLC, KLAX, VILK, LEMD, RPLL, MMMX, KMIA, LIMC, UUWW, EDDM, KLGA, MPMG, LFPB, ZSQD, KSFO, SBGR, KSEA, RKSI, ZSPD, ZGSZ, WSSS, LLBG, RJTT, CYYZ, EPWA, NZWN, ZHHH, ZHCC) from one named static source (e.g. an OurAirports snapshot) with its hash; commit before burn-in.
2. **Capture services** (Data plane): events/markets (gamma, hourly), CLOB books for all 22 tokens (periodic + T_entry − 5 min + T_entry + 5 min), forecast vintages (section 8 cadence, three models), settlement page renders (Playwright) at D+1 02:00 local and at resolution, METAR history, `data-api /trades` per eligible event after resolution. Append-only storage with hashes; NTP.
3. **Eligibility engine**: E1–E8 evaluated at T_entry; reason codes; AMBIGUOUS list.
4. **Decision engine**: R* exactly as section 9; exploratory variants and baselines from archives only; `params_hash` assertion on every decision.
5. **Fill and ledger engines**: REALISTIC and CONSERVATIVE fills; S_ref and four tiers; capital caps in T_entry order; exchange-level and full ledgers; CAPITAL_USAGE.
6. **Replay tool**: rebuild every decision from archived rows; report byte-equality (invariant 14).
7. **Burn-in** ≥ 30 days: completeness ≥ 95%; settlement reconciliation ≥ 98%; bias windows filled; no parameter edits. Produce `WEATHER_FORWARD_BURN_IN_REPORT`.
8. **t0 request**: submit the freeze manifest hash, params hash, engine version hash and burn-in report to Blue; t0 is declared in governance, not by the Builder.
9. **Forward window**: run 60–120 target dates; weekly status (completeness, MISSING, eligibility counts, mechanics checks only — no P&L peeking beyond an automated integrity dashboard; P&L is computed at analysis time).
10. **Analysis**: sections 13, 18, 19, 23; publish `WEATHER_FORWARD_RESULT_<date>.md` with the terminal state, validity flag, all exploratory results, tier economics, survivorship table and the replay result.

Verification expected from the Builder before t0: unit tests for bucket arithmetic (tails, °F), for `T_entry` across time zones and DST, for the information-time query filters (adversarial: inject a late vintage and assert rejection), for fill walking (price cap, min size, 50% haircut), for restart/replay idempotence (no duplicated fills or P&L after crash and replay), and for params-hash mutation detection.
