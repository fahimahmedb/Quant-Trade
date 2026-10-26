# D05-A / D09 LIQUIDITY PREDICTIVE-LOOKBACK / NOTIONAL-SOURCE CONTRACT — 2026-09-17

**Status:** CLOSED / FROZEN SEMANTICS — NUMERICAL FORECAST-ERROR FUNCTIONAL / THRESHOLD / WINDOW / PROVIDER STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D05A_D09_LIQUIDITY_METRIC_AND_LOOKBACK_STABILITY_CONTRACT_2026-09-17.md`, `D05A_D09_LIQUIDITY_IDENTITY_AND_LOOKBACK_SELECTION_AMENDMENT_2026-09-17.md`, `D09_ROUTE_B_LIQUIDITY_ELIGIBILITY_AND_FINITE_COST_SCENARIO_AMENDMENT_2026-09-17.md`

This contract corrects the interpretation of the previously named `RELATIVE_ADV_ERROR(W)`. `ADV_NOTIONAL(W)` is not an estimate of a fixed latent constant whose sampling error is intrinsically defined. The economically relevant property is predictive adequacy for the liquidity available at the next deployment opportunity.

No Form-4 target counts, D05 ceilings, outcomes, numerical provider values or candidate-window results are consumed by this artifact.

## 1. Lookback target is predictive, not estimation-of-a-constant

The claim-defining capacity gate uses `ADV_NOTIONAL(W)` as a predictor of near-term deployable liquidity.

Therefore the lookback-selection object is renamed conceptually from a generic estimator error to:

`ADV_PREDICTION_ERROR(W)`.

The target is future traded notional under the authorized short-horizon deployment regime, not an unobservable fixed “true ADV”.

The current lineage does not select `W` from:

- internal day-to-day smoothness alone;
- standard error of the window mean under an unverified stationarity assumption;
- target-population retention.

Those quantities may be diagnostics but do not define the authority-bearing lookback criterion.

**Invariants**

- `ADV_LOOKBACK_TARGET_IS_PREDICTIVE_LIQUIDITY`
- `ADV_IS_NOT_TREATED_AS_FIXED_LATENT_CONSTANT`
- `INTERNAL_SMOOTHNESS_ALONE_DOES_NOT_SELECT_LOOKBACK`
- `STATIONARY_STANDARD_ERROR_ALONE_DOES_NOT_SELECT_LOOKBACK`

## 2. Prediction horizon = next regular trading session

For a daily liquidity snapshot with cutoff session `t`, the primary calibration target is:

`NEXT_SESSION_TRADED_NOTIONAL(t)`

for the immediately following regular trading session of the same PIT-resolved security/listing lineage.

This horizon is chosen because the capacity gate governs the decision to admit non-zero deployment support for the next authorized entry opportunity. The 20-session holding horizon does not turn the support gate into a 20-session liquidity forecast.

Exit execution and post-entry liquidity deterioration remain economic-cost/risk/terminal-treatment objects and do not continuously redefine scientific support.

The exact opening-execution quality is not the forecast target of this capacity gate; opening spread/depth/slippage remain in `K_forward` / `M_economic`.

**Invariants**

- `ADV_CAPACITY_FORECAST_HORIZON_IS_NEXT_REGULAR_SESSION`
- `HOLDING_HORIZON_DOES_NOT_DEFINE_CAPACITY_GATE_FORECAST_HORIZON`
- `OPEN_EXECUTION_QUALITY_REMAINS_COST_NOT_SUPPORT`

## 3. Predictive lookback rule form

The previously frozen shortest-passing-window structure remains, with the corrected predictive target:

`W* = shortest W in frozen candidate set such that ADV_PREDICTION_ERROR(W) <= epsilon_ADV`.

Before inspecting candidate-window calibration results, freeze/hash:

- candidate window set;
- exact loss/error functional used to compare `ADV_NOTIONAL(W,t)` with `NEXT_SESSION_TRADED_NOTIONAL(t)`;
- pooling/aggregation rule across securities and dates;
- any weighting rule;
- `epsilon_ADV`;
- tie rule;
- calibration-corpus construction;
- failure state if no window passes.

The exact loss functional is still open. It must be scale-compatible with a notional capacity predictor and robust enough that a few extreme volume days do not silently determine the claim-support window unless that behavior is explicitly intended and frozen.

**Invariants**

- `PREDICTION_ERROR_FUNCTIONAL_PRECEDES_WINDOW_RESULTS`
- `EPSILON_ADV_PRECEDES_WINDOW_RESULTS`
- `CANDIDATE_WINDOWS_PRECEDE_WINDOW_RESULTS`
- `NO_POST_RESULT_PREDICTION_LOSS_SWITCH`

## 4. External calibration corpus must cover the intended liquidity regime

The non-target calibration corpus must be relevant to the ex-ante deployment liquidity regime that `L_deploy(theta)` intends to admit.

However, the corpus-selection rule may not depend on the realized values of the candidate `ADV_NOTIONAL(W)` windows that it is being used to choose. Otherwise window selection and corpus membership become circular.

Therefore, before calibration, freeze a `CALIBRATION_LIQUIDITY_DOMAIN` rule that is independent of candidate-window results and is justified as covering the intended deployment regime.

Permitted structures may include, once separately specified:

- a provider/source-native liquidity class with stable documented semantics;
- an economically predeclared notional-liquidity band measured by an independent reference convention;
- a broader ex-ante universe proven to contain the intended `L_deploy` region, with a frozen weighting/stratification rule.

Forbidden:

`compute candidate ADV windows -> see which securities pass -> choose calibration corpus that favors the preferred window`.

If no non-circular applicability rule can be frozen:

`LIQUIDITY_LOOKBACK_CALIBRATION_DOMAIN_UNRESOLVED`.

**Invariants**

- `CALIBRATION_CORPUS_COVERS_INTENDED_LIQUIDITY_REGIME`
- `CALIBRATION_CORPUS_MEMBERSHIP_IS_INDEPENDENT_OF_CANDIDATE_WINDOW_RESULTS`
- `L_DEPLOY_APPLICABILITY_DOES_NOT_CREATE_LOOKBACK_CIRCULARITY`

## 5. `DAILY_TRADED_NOTIONAL` representation is source-contract dependent

The metric remains notional traded value, but this artifact does not force a theoretically preferred price convention that the eventual PIT source cannot reproduce.

The parameter/source contract must freeze, before numerical comparison of representations, exactly one admissible daily-notional route:

### Route N1 — source-provided daily traded notional

Admissible only if the source documents its economic meaning, PIT/version semantics and reproducibility sufficiently for the claim fingerprint.

### Route N2 — deterministic price × share-volume construction

If constructed, the exact price reference and volume field must be frozen, with adjustment/corporate-action and PIT lineage semantics.

Candidate price conventions may include close, VWAP or another separately justified daily reference, but no convention is preferred merely because it is theoretically more precise if it is not historically/PIT reproducible under the authorized source class.

The selection criterion is **source-semantic authority and reproducibility first**, not the resulting eligibility count or numerical ADV magnitude.

A fallback representation may be used only if its precedence/failure rule is frozen before values; there is no post-hoc switching because one representation retains more target securities or produces a more favorable threshold.

**Invariants**

- `DAILY_NOTIONAL_REPRESENTATION_FOLLOWS_FROZEN_SOURCE_AUTHORITY`
- `THEORETICAL_PREFERENCE_DOES_NOT_OVERRIDE_PIT_REPRODUCIBILITY`
- `NO_TARGET_RETENTION_DRIVEN_PRICE_CONVENTION`
- `NO_POST_HOC_NOTIONAL_REPRESENTATION_FALLBACK`

## 6. PIT and corporate-action consistency

Whatever daily-notional route is selected must remain consistent with:

- the PIT-resolved deployment security/listing identity;
- the last completed regular session strictly before the relevant EDGAR reference date;
- coherent historical listing/security lineage across the lookback;
- frozen corporate-action semantics;
- source version/provenance.

If a ticker/listing/security transition prevents coherent construction under the frozen route, use the governed unresolved state / FM-08 rather than splice incompatible histories merely to obtain a value.

## 7. Separation from support threshold and cost calibration

This contract governs how the lookback is chosen and how daily notional is represented. It does not yet select:

- the numerical ADV eligibility threshold;
- an acceptable participation limit;
- an impact coefficient;
- a `C_claim(G)` scale domain;
- opening execution cost.

Those remain separately governed.

In particular, a predictive ADV window that performs well does not itself authorize a participation threshold or prove execution feasibility.

## 8. Current state

Closed/frozen:

- authority-bearing lookback property = near-term predictive liquidity, not estimation error around a fixed ADV;
- forecast target = next regular session traded notional;
- shortest-window-meeting-threshold form retained;
- exact error/loss functional must be frozen before calibration results;
- calibration corpus must cover the intended deployment liquidity regime without using candidate-window outputs to define corpus membership;
- daily-notional representation is selected by frozen PIT/source authority and reproducibility, not by theoretical preference or target retention;
- open execution quality remains outside the support gate.

Still open:

- exact `ADV_PREDICTION_ERROR(W)` loss/aggregation functional;
- candidate window set;
- numerical `epsilon_ADV`;
- exact `CALIBRATION_LIQUIDITY_DOMAIN` implementation;
- exact source class/provider;
- N1 versus N2 daily-notional route;
- if N2, exact price and volume fields;
- final lookback length;
- minimum valid observations / insufficient-history treatment;
- numerical ADV support threshold / participation rule.

No numerical liquidity-source search, D05 ceiling visibility or Form-4 outcome access is authorized by this artifact.
