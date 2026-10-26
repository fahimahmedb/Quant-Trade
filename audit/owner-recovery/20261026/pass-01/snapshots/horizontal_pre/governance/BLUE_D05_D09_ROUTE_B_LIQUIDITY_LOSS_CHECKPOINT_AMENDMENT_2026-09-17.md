# BLUE ROUTE-B CHECKPOINT AMENDMENT — LIQUIDITY PREDICTION LOSS — 2026-09-17

**Status:** CURRENT CHECKPOINT AMENDMENT  
**Authority:** Blue Team / Mission Control  
**Parents:** `BLUE_D05_D09_ROUTE_B_LIQUIDITY_SUPPORT_CHECKPOINT_AMENDMENT_2026-09-17.md`, `D05A_D09_LIQUIDITY_PREDICTION_LOSS_AND_AGGREGATION_CONTRACT_2026-09-17.md`

This amendment controls where it is more recent/specific than its parent checkpoint.

## 1. New controlling artifact

Add:

`governance/D05A_D09_LIQUIDITY_PREDICTION_LOSS_AND_AGGREGATION_CONTRACT_2026-09-17.md`.

## 2. Prediction-error coordinate is closed

For candidate lookback `W`:

`R_i,t(W) = ADV_NOTIONAL_i(W,t) / NEXT_SESSION_TRADED_NOTIONAL_i(t)`

and:

`E_i,t(W) = log R_i,t(W)`.

The coordinate is multiplicative and scale-free across securities.

Current state:

`ADV_PREDICTION_ERROR_COORDINATE = CLOSED / LOG-RATIO`.

## 3. Loss family is closed

The authority-bearing per-observation loss is asymmetric absolute log loss:

`L_i,t(W) = lambda_over * max(E_i,t(W),0) + lambda_under * max(-E_i,t(W),0)`

with:

`lambda_over > lambda_under > 0`.

Overprediction is penalized more heavily because it creates optimistic participation/capacity estimates and can understate implementation loss. Underprediction retains non-zero penalty because underdeployment/opportunity cost is economically real.

Symmetric squared error is not the current-lineage selector.

Current state:

`ADV_PREDICTION_LOSS_FAMILY = CLOSED / ASYMMETRIC_ABSOLUTE_LOG`.

The numerical asymmetry ratio remains open and must be frozen before candidate-window results.

## 4. Aggregation is closed in form

Candidate-window authority uses an upper quantile of the asymmetric loss:

`ADV_PREDICTION_ERROR(W) = Q_q^weighted(L_i,t(W))`

with:

`0.5 < q < 1`.

The arithmetic mean is not the selector, and median alone is insufficient because it can ignore an economically relevant overprediction tail.

Each eligible calibration security receives equal total mass. Eligible dates within a security share that mass under the frozen sampling rule.

No market-cap, ADV, realized-notional or Form-4-frequency weighting is authorized for lookback selection.

Current states:

`ADV_PREDICTION_AGGREGATOR = CLOSED / UPPER_QUANTILE`

`CALIBRATION_SECURITY_WEIGHTING = CLOSED / EQUAL_TOTAL_SECURITY_MASS`.

The numerical quantile `q` remains open and must be frozen before candidate-window results.

## 5. Zero versus missing target

A true next-session zero-trading state is not missing data.

The numerical implementation must preserve:

- `REALIZED_ZERO_TRADING`;
- `PREDICTION_TARGET_MISSING_OR_UNRESOLVED`.

No post-result epsilon-denominator rescue is authorized.

## 6. Updated lookback selector

The governing form is now:

`W* = shortest W in frozen candidate set such that Q_q^weighted(L_i,t(W)) <= epsilon_ADV`.

Before numerical calibration, freeze/hash:

- candidate-window set;
- `lambda_over/lambda_under`;
- upper quantile `q`;
- `epsilon_ADV`;
- calibration-domain/corpus rule;
- calendar/date sampling rule;
- valid-target / zero-trading rule;
- tie rule;
- no-window-pass failure state.

No one of these may be tuned after inspecting which candidate window wins or how much Form-4 support it preserves.

## 7. Firewall state

`ROUTE_B_FINAL_PROTOCOL_FIREWALL_SATISFIED = FALSE` remains unchanged.

The predictive-loss functional form and aggregation family are now closed, but the numerical selector parameters and remaining source/history/capacity rules are not yet consumable.

## 8. Current liquidity-selector state

Closed/frozen:

- gate purpose = capacity only;
- metric family = notional ADV;
- forecast target = next-session traded notional;
- error coordinate = log ratio;
- loss family = asymmetric absolute log loss;
- overprediction weight strictly exceeds underprediction weight;
- aggregator = upper quantile;
- each security has equal total calibration mass;
- no size/liquidity weighting;
- true zero-trading distinct from missing target.

Still open before calibration:

- numerical asymmetry ratio;
- numerical quantile `q`;
- candidate windows;
- numerical `epsilon_ADV`;
- exact calibration-domain implementation;
- date-sampling rule;
- exact zero-trading numerical treatment;
- source/provider and daily-notional route;
- minimum-history / insufficient-history rule;
- numerical support threshold / participation rule.

No numerical calibration, D05 ceiling visibility or Form-4 outcome access is authorized by this amendment.
