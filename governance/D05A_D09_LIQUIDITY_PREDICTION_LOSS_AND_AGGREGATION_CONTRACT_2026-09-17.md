# D05-A / D09 LIQUIDITY PREDICTION-LOSS / AGGREGATION CONTRACT — 2026-09-17

**Status:** CLOSED / FROZEN FUNCTIONAL FORM — NUMERICAL ASYMMETRY / QUANTILE / EPSILON STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D05A_D09_LIQUIDITY_PREDICTIVE_LOOKBACK_AND_NOTIONAL_SOURCE_CONTRACT_2026-09-17.md`, `D05A_D09_LIQUIDITY_METRIC_AND_LOOKBACK_STABILITY_CONTRACT_2026-09-17.md`

This contract closes the functional form used to compare candidate notional-ADV lookbacks before any candidate-window results are inspected. It does not select numerical loss weights, quantile level, error threshold, lookback, provider, Form-4 support value or outcome.

## 1. Economic asymmetry of prediction error

The capacity use of `ADV_NOTIONAL(W,t)` is asymmetric.

For a fixed intended order notional, overpredicting near-term traded notional causes the realized participation rate to be higher than modeled and can therefore produce underestimated impact / execution loss.

Underpredicting near-term traded notional can reduce deployable size and create opportunity cost, but it does not create the same execution-capacity failure mechanism.

Therefore a symmetric squared-error objective is not the authority-bearing lookback criterion in this lineage.

**Invariants**

- `ADV_OVERPREDICTION_IS_MORE_ADVERSE_THAN_UNDERPREDICTION`
- `SYMMETRIC_SQUARED_ERROR_DOES_NOT_SELECT_LOOKBACK`
- `UNDERPREDICTION_REMAINS_COSTLY_NOT_ZERO_COST`

## 2. Scale-free multiplicative forecast coordinate

For security/listing `i` and eligible calibration cutoff `t`, define:

`A_i,t(W) = ADV_NOTIONAL_i(W,t)`

and:

`Y_i,t = NEXT_SESSION_TRADED_NOTIONAL_i(t)`.

For `Y_i,t > 0`, define the multiplicative forecast ratio:

`R_i,t(W) = A_i,t(W) / Y_i,t`

and log-ratio error:

`E_i,t(W) = log R_i,t(W)`.

Interpretation:

- `E > 0`: ADV overprediction / capacity optimism;
- `E < 0`: ADV underprediction / capacity conservatism;
- `E = 0`: exact multiplicative prediction.

This coordinate is invariant to the dollar liquidity scale of the security. A two-fold error has the same base magnitude whether the security trades millions or hundreds of millions of dollars per day.

**Invariants**

- `ADV_PREDICTION_ERROR_IS_SCALE_FREE`
- `NO_ABSOLUTE_DOLLAR_ERROR_WEIGHTING_ACROSS_SECURITIES`
- `MULTIPLICATIVE_ERROR_PRECEDES_LOSS_AGGREGATION`

## 3. Frozen loss family = asymmetric absolute log loss

The authority-bearing per-observation loss has the form:

`L_i,t(W) = lambda_over * max(E_i,t(W), 0) + lambda_under * max(-E_i,t(W), 0)`

with the required ordering:

`lambda_over > lambda_under > 0`.

The common normalization may set `lambda_under = 1` and write:

`lambda = lambda_over / lambda_under > 1`.

The exact numerical asymmetry coefficient must be frozen before any candidate-window prediction results are inspected.

Why this form:

- multiplicative / scale-free across securities;
- explicitly penalizes capacity optimism more than conservatism;
- retains a non-zero opportunity-cost penalty for systematic underprediction;
- uses linear rather than quadratic tails so a small number of extreme sessions do not dominate solely through squaring;
- does not require pretending the economic impact function itself is linear in forecast error.

The loss is a lookback-selection criterion, not the `K_forward` impact-cost model. It does not replace the separately governed impact coefficient or execution-cost recipe.

**Invariants**

- `LOSS_IS_ASYMMETRIC_ABSOLUTE_LOG_RATIO`
- `OVERPREDICTION_WEIGHT_EXCEEDS_UNDERPREDICTION_WEIGHT`
- `LOSS_DOES_NOT_REPLACE_IMPACT_MODEL`
- `LOSS_ASYMMETRY_PRECEDES_WINDOW_RESULTS`

## 4. Aggregation = quantile, not arithmetic mean

Daily traded notional and resulting forecast errors are heavy-tailed. A raw arithmetic mean of loss can be dominated by a small number of unusual sessions and is not the current-lineage authority aggregator.

The authority-bearing predictive error for candidate window `W` is therefore a frozen upper quantile of the per-observation asymmetric loss:

`ADV_PREDICTION_ERROR(W) = Q_q^weighted( L_i,t(W) )`

where the quantile level `q` must satisfy:

`0.5 < q < 1`

and its exact numerical value must be frozen before candidate-window prediction results are inspected.

The median alone is not selected because it can ignore an economically material adverse overprediction tail. The quantile form retains robustness to isolated extremes while requiring a predeclared amount of tail protection.

**Invariants**

- `ADV_PREDICTION_AGGREGATOR_IS_UPPER_QUANTILE`
- `MEAN_LOSS_DOES_NOT_SELECT_LOOKBACK`
- `MEDIAN_ALONE_DOES_NOT_CONTROL_ADVERSE_OVERPREDICTION_TAIL`
- `QUANTILE_LEVEL_PRECEDES_WINDOW_RESULTS`

## 5. Equal security mass; no capitalization or liquidity weighting

Scale-free loss removes the need to weight errors by dollar liquidity magnitude.

To prevent securities with longer usable histories from automatically dominating the calibration, aggregation assigns equal total mass to each eligible security/listing identity in the frozen calibration corpus.

Within each security, eligible calibration dates receive equal mass unless a separately frozen calendar-sampling rule states otherwise.

Conceptually, if security `i` has `n_i` eligible calibration dates, each `(i,t)` observation receives weight proportional to:

`1 / n_i`

followed by normalization across securities so every security contributes equal total weight.

Forbidden weighting for lookback selection includes:

- market capitalization;
- current or future ADV magnitude;
- realized next-session notional magnitude;
- Form-4 frequency;
- eventual target support;
- order size chosen from the Form-4 policy.

This does not assert that all securities have equal capital importance in deployment. It only prevents the external lookback-calibration functional from silently becoming a large-cap liquidity objective.

**Invariants**

- `EACH_CALIBRATION_SECURITY_HAS_EQUAL_TOTAL_WEIGHT`
- `NO_MARKET_CAP_OR_ADV_WEIGHTING_IN_LOOKBACK_SELECTION`
- `LONGER_SECURITY_HISTORY_DOES_NOT_CREATE_MORE_TOTAL_CALIBRATION_MASS`

## 6. Zero-trade and missing-target semantics

A true next regular trading session with zero realized traded notional is economically distinct from a missing market-data record.

The future calibration implementation must therefore distinguish:

- `REALIZED_ZERO_TRADING`: the authorized source establishes zero traded notional for the otherwise applicable next regular session;
- `PREDICTION_TARGET_MISSING_OR_UNRESOLVED`: the target cannot be established under the frozen source/PIT rule.

If `A_i,t(W) > 0` and `Y_i,t = 0` is a true realized zero-trading state, the forecast ratio is an adverse capacity failure and must not be silently dropped or replaced by a small positive denominator. The exact finite/infinite representation in the numerical implementation must be frozen before calibration results.

Missing/unresolved targets follow the separately frozen calibration-data completeness/failure rule; they are not recoded as zero.

**Invariants**

- `REAL_ZERO_TRADING_IS_NOT_MISSING_DATA`
- `NO_EPSILON_DENOMINATOR_RESCUE_AFTER_RESULTS`
- `MISSING_TARGET_IS_NOT_ZERO_TARGET`

## 7. Lookback rule after this closure

The previously frozen rule becomes:

`W* = shortest W in frozen candidate set such that ADV_PREDICTION_ERROR(W) <= epsilon_ADV`

with:

`ADV_PREDICTION_ERROR(W) = Q_q^weighted(L_i,t(W))`

and:

`L_i,t(W) = lambda_over * max(log(A_i,t(W)/Y_i,t),0) + lambda_under * max(-log(A_i,t(W)/Y_i,t),0)`.

Before inspecting candidate-window results, the calibration protocol must freeze/hash at minimum:

- candidate window set;
- numerical `lambda_over/lambda_under` ratio;
- numerical quantile `q`;
- numerical `epsilon_ADV`;
- calibration liquidity domain / corpus rule;
- calendar/date sampling rule;
- valid-target and zero-trading treatment;
- tie rule;
- failure state if no candidate window passes.

No one of these quantities may be tuned because the resulting `W*` looks operationally convenient or retains more Form-4 support.

## 8. Relationship to the North Star and economic costs

This functional is deliberately aligned with future wealth rather than statistical symmetry:

- optimism about available liquidity can create unmodeled implementation loss;
- conservatism can leave capital idle or underdeployed;
- the two harms are represented asymmetrically without moving execution costs into the support gate itself.

The numerical asymmetry weight is still a governance parameter and must receive an independent ex-ante justification. It is not inferred from Form-4 outcomes or chosen to obtain a preferred lookback.

## 9. Current state

Closed/frozen:

- predictive error coordinate = `ADV_NOTIONAL / next-session traded notional`;
- multiplicative error represented as log ratio;
- loss family = asymmetric absolute log loss;
- overprediction receives strictly greater weight than underprediction;
- aggregation family = upper quantile, not mean or median alone;
- each eligible calibration security receives equal total aggregation mass;
- no capitalization/ADV/notional weighting;
- true zero trading and missing target must remain distinct.

Still open before numerical calibration:

- numerical asymmetry ratio `lambda_over/lambda_under`;
- numerical quantile level `q`;
- candidate window set;
- numerical `epsilon_ADV`;
- exact calibration-domain implementation;
- exact calendar/date sampling rule;
- exact true-zero numerical representation;
- exact source/provider and daily-notional route;
- final lookback length;
- minimum-history / insufficient-history policy;
- numerical support threshold / participation rule.

No numerical lookback calibration, D05 ceiling visibility or Form-4 outcome access is authorized by this artifact.
