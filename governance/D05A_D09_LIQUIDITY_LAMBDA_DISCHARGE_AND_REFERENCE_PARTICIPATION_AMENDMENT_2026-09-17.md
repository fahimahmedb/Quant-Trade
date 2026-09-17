# D05-A / D09 LIQUIDITY LAMBDA-DISCHARGE / REFERENCE-PARTICIPATION AMENDMENT — 2026-09-17

**Status:** CLOSED / FROZEN PROCEDURAL AMENDMENT — NUMERICAL CAPACITY GOVERNOR / q / WINDOW CALIBRATION STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D05A_D09_LIQUIDITY_PREDICTION_LOSS_AND_AGGREGATION_CONTRACT_2026-09-17.md`, `D05A_D09_LIQUIDITY_PREDICTIVE_LOOKBACK_AND_NOTIONAL_SOURCE_CONTRACT_2026-09-17.md`, `D09_ECONOMIC_CORE_EC1_ALLOCATION_WEIGHTED_EFFECT.md`, `D09_ROUTE_B_FRICTION_MARGIN_PARTITION_2026-09-17.md`

This amendment replaces the current-lineage requirement that one numerical asymmetry ratio `lambda_over/lambda_under` must be resolved before any candidate-window prediction results are inspected. It authorizes a pre-frozen structural robustness discharge over the complete admissible asymmetry domain. If the selected lookback is invariant over that domain, numerical `lambda` may remain unresolved for lookback selection. If it is not invariant, `lambda` becomes a material scientific dependency and must be resolved before lookback authority.

No Form-4 target values, D05 ceilings, return outcomes or candidate-window calibration results are consumed by this amendment.

## 1. `lambda` remains economically derivation-blocked

The loss-family asymmetry remains economically motivated, but a numerical ratio is not currently derivable with authority.

For a multiplicative liquidity forecast error around `R = 1`, the desired economic recipe is conceptually:

`lambda_over(theta) ∝ d[adverse execution loss] / d log(R) | R=1+`

`lambda_under(theta) ∝ -d[missed economic value] / d log(R) | R=1-`

and:

`lambda(theta) = lambda_over(theta) / lambda_under(theta)`.

The overprediction derivative depends on the frozen sizing/allocation/capacity mechanics. If sizing consumes predicted ADV, order notional and realized participation can move jointly; if order notional is fixed independently, the derivative is different.

The underprediction derivative depends on marginal economic surplus, not gross `delta` alone. EC1 defines value through `Q * delta - K_forward`; idle/undeployed capital cannot be assigned zero opportunity value by shortcut.

Therefore current authority is:

`LAMBDA_DERIVATION_STATE = DERIVATION_BLOCKED_PENDING_ALLOCATION_AND_MARGINAL_ECONOMICS`.

The existence of a square-root impact form in V1 does not resolve this blocker because its coefficients are not calibrated Route-B authority and because the sizing dependence is itself claim-defining.

**Invariants**

- `LAMBDA_IS_NOT_DERIVED_FROM_GROSS_RETURN_SHORTCUT`
- `LAMBDA_DERIVATION_BINDS_ALLOCATION_AND_MARGINAL_ECONOMICS`
- `V1_IMPACT_FORM_DOES_NOT_BY_ITSELF_AUTHORIZE_LAMBDA`

## 2. Normalize by the adverse-side weight

Set the overprediction weight to the normalization unit. Let:

`lambda = lambda_over / lambda_under > 1`

and:

`x = 1 / lambda`, so structurally `0 < x < 1`.

Use the closure of that domain for robustness proof:

`x ∈ [0, 1]`,

where:

- `x = 0` is the limit `lambda -> ∞`: underprediction receives zero relative weight;
- `x = 1` is the limit `lambda -> 1+`: symmetric absolute log loss.

For log forecast error `E = log(ADV_NOTIONAL / NEXT_SESSION_TRADED_NOTIONAL)`, define normalized loss:

`L_bar_x(E) = max(E, 0) + x * max(-E, 0)`.

This is the same asymmetric absolute-log family up to positive scaling; it removes the artificial coupling in which changing `lambda_over` also changes the absolute pass threshold.

For every fixed observation, `L_bar_x(E)` is nondecreasing in `x`.

With fixed weights and fixed `q`, its weighted upper quantile is therefore also nondecreasing in `x`.

**Invariants**

- `LAMBDA_SENSITIVITY_USES_ADVERSE_WEIGHT_NORMALIZATION`
- `NORMALIZED_LOSS_VARIES_ONLY_RELATIVE_UNDERPREDICTION_WEIGHT`
- `WINDOW_ERROR_IS_MONOTONE_IN_X`

## 3. `epsilon_ADV` is tied to a single pre-frozen reference participation governor

The lookback window is a liquidity-measurement property and must not become `W*(theta)` merely because actual deployment capital or sizing later changes.

Before lookback calibration, freeze one reference capacity governor for measurement selection:

- `P_TARGET_REF`: reference target participation used only to define the tolerated liquidity-forecast error for lookback selection;
- `P_MAX_REF`: maximum admissible participation under the same independently governed reference capacity convention;
- required `0 < P_TARGET_REF < P_MAX_REF`.

Define:

`R_CAP_REF = P_MAX_REF / P_TARGET_REF > 1`

and the normalized prediction-loss threshold:

`EPSILON_ADV_BAR = log(R_CAP_REF)`.

Interpretation: an ADV overprediction by exactly `R_CAP_REF` turns intended reference participation `P_TARGET_REF` into realized participation `P_MAX_REF`.

`P_TARGET_REF` and `P_MAX_REF` must be frozen independently of candidate-window results, Form-4 support, D05 ceilings and outcomes.

If no independent capacity-governor authority exists:

`EPSILON_ADV_DERIVATION_BLOCKED`.

There is no fallback to a convenient numerical epsilon.

This amendment freezes the **single-reference architecture**, not numerical values for `P_TARGET_REF` or `P_MAX_REF` and not the final capacity-support functional.

**Invariants**

- `LOOKBACK_WINDOW_IS_NOT_THETA_DEPENDENT`
- `EPSILON_ADV_USES_SINGLE_PRE_FROZEN_REFERENCE_PARTICIPATION`
- `CAPACITY_REFERENCE_PRECEDES_WINDOW_RESULTS`
- `NO_ARBITRARY_EPSILON_FALLBACK_IF_CAPACITY_GOVERNOR_UNRESOLVED`

## 4. Lambda materiality is tested over the complete structural domain

No arbitrary plausible interval for `lambda` is required to decide whether unresolved asymmetry matters to `W*`.

Once all other lookback-selector objects are frozen, define for each candidate window `W`:

`F_W(x) = Q_q^weighted( L_bar_x(E_i,t(W)) )`.

The pass rule is:

`F_W(x) <= EPSILON_ADV_BAR`.

For each `x`, `W*(x)` is the **shortest predeclared candidate window that passes**. It is not the window minimizing `F_W(x)`.

The robustness domain is the full structural closure:

`x ∈ [0,1]`.

No narrower range may be chosen because it makes one window robust.

**Invariant:** `LAMBDA_ROBUSTNESS_USES_FULL_STRUCTURAL_DOMAIN`.

## 5. Exact endpoint theorem — no grid required

Because `F_W(x)` is nondecreasing in `x`, lambda invariance of the shortest-passing-window rule can be certified from the two structural endpoints.

Suppose the same candidate `W0` is the shortest passing window at both:

`x = 0`

and:

`x = 1`.

Then:

1. `W0` passes at `x=1`; monotonicity implies it passes for every `x ∈ [0,1]`.
2. Every candidate shorter than `W0` fails at `x=0`; monotonicity implies each shorter candidate fails for every `x ∈ [0,1]`.
3. Therefore `W0` is the shortest passing window for every `x ∈ [0,1]`.

Hence:

`W*(0) = W*(1) = W0  =>  W*(x) = W0 for all x ∈ [0,1]`.

This proof uses the threshold/shortest-passing structure. It would not hold merely from equal endpoint winners under a generic argmin-ranking problem.

No continuity argument, lambda grid, plausible-bound choice, or intermediate breakpoint scan is required.

At `x=0`, the loss is `max(E,0)`. The resulting `W*(0)` is the shortest candidate satisfying the frozen overprediction-loss threshold; it is **not** necessarily the candidate minimizing the overprediction quantile.

**Invariants**

- `LAMBDA_ENDPOINT_DISCHARGE_IS_EXACT_FOR_SHORTEST_PASSING_RULE`
- `NO_LAMBDA_GRID_REQUIRED_FOR_MATERIALITY_DISCHARGE`
- `ENDPOINT_EQUALITY_PLUS_MONOTONE_PASS_RULE_PROVES_FULL_DOMAIN_INVARIANCE`
- `X_ZERO_SELECTS_SHORTEST_PASSING_NOT_GLOBAL_MINIMUM`

## 6. Authority states after the endpoint test

The endpoint test is run only after its complete protocol is frozen and only on the authorized non-target calibration corpus.

### State A — nonmaterial unresolved lambda

If:

`W*(0) = W*(1) = W0`,

emit:

`LAMBDA_UNRESOLVED_BUT_NONMATERIAL_TO_LOOKBACK`.

Then `W0` may receive lookback-selection authority even though numerical `lambda` remains unresolved.

This discharge applies only to the lookback consumer. It does not resolve `lambda` for any later economic consumer that genuinely requires the numerical marginal-cost ratio.

### State B — lambda material to lookback

If endpoint selected windows differ, or one endpoint produces a different failure/pass state:

`LAMBDA_MATERIAL_TO_LOOKBACK`.

No final lookback is selected under unresolved `lambda`.

The critical path then returns to the prerequisites required to resolve the economic asymmetry, including as applicable:

- concrete `A_CONSTRUCTOR` sizing/capacity mechanics;
- expected impact/cost calibration;
- marginal economic surplus semantics consistent with EC1;
- any additional execution-model authority required by the derivative recipe.

Improved execution calibration is therefore a scientific prerequisite **only when unresolved execution economics is proven material to the lookback decision**.

**Invariants**

- `UNRESOLVED_PARAMETER_MAY_BE_DISCHARGED_ONLY_FOR_A_PROVEN_NONMATERIAL_CONSUMER`
- `LAMBDA_MATERIALITY_PROMOTES_EXECUTION_CALIBRATION_TO_SCIENTIFIC_CRITICAL_PATH`
- `NONMATERIAL_LOOKBACK_DISCHARGE_DOES_NOT_GLOBALLY_RESOLVE_LAMBDA`

## 7. q selection requires a disjoint external selection split

The numerical quantile `q` remains a robustness parameter rather than a direct economic derivative.

Its selection procedure must be frozen before any candidate-window selection results are inspected and must use a dedicated non-target external split that is disjoint from the data used to select `W*`.

The intended rule family is:

> select the highest candidate upper quantile whose estimator satisfies a separately pre-frozen resampling/stability criterion on the q-selection split.

Before q-selection results, freeze/hash:

- candidate `q` set;
- exact stability statistic;
- resampling method;
- stability threshold;
- minimum effective sample / failure rule;
- split-construction rule.

After `q` is selected and frozen, the window-selection split may evaluate candidate windows. No information about which `q` favors which `W` may flow back into q selection.

If no candidate `q` satisfies the frozen stability criterion:

`Q_SELECTION_UNRESOLVED`.

**Invariants**

- `Q_SELECTION_SPLIT_IS_DISJOINT_FROM_WINDOW_SELECTION_SPLIT`
- `Q_IS_SELECTED_FOR_ESTIMABILITY_NOT_PREFERRED_WINDOW`
- `Q_SELECTION_PRECEDES_WINDOW_SELECTION_RESULTS`

## 8. Procedural order

The authorized order is now:

`freeze candidate windows / source semantics / calibration domain / sampling`

`-> freeze single reference capacity-governor rule (P_TARGET_REF, P_MAX_REF)`

`-> derive EPSILON_ADV_BAR = log(P_MAX_REF / P_TARGET_REF)`

`-> freeze q-selection candidates + stability rule + disjoint splits`

`-> select/freeze q on q-selection split`

`-> freeze endpoint lambda-discharge protocol`

`-> evaluate W*(0) and W*(1) on window-selection split`

`-> if equal: LAMBDA_UNRESOLVED_BUT_NONMATERIAL_TO_LOOKBACK and authorize W*`

`-> if different: LAMBDA_MATERIAL_TO_LOOKBACK and resolve upstream economic dependencies before W* authority`.

No sensitivity output may be used to redesign the candidate-window set, q procedure, reference participation governor, daily-notional representation or calibration corpus.

## 9. Supersession of prior numerical-lambda requirement

For this lineage, this amendment supersedes the sentence-level reading of `D05A_D09_LIQUIDITY_PREDICTION_LOSS_AND_AGGREGATION_CONTRACT_2026-09-17.md` that requires one numerical `lambda_over/lambda_under` ratio to be frozen before any candidate-window prediction results.

The controlling current-lineage rule is instead:

- the **functional loss family and normalization** must be frozen before results;
- the **endpoint materiality-discharge protocol** must be frozen before results;
- a numerical `lambda` is required before lookback authority only if the endpoint test proves `lambda` material to the selected window.

All anti-rescue prohibitions in the parent contract remain in force.

## 10. Current state

Closed/frozen:

- numerical `lambda` derivation is currently blocked by allocation/marginal-economics dependencies;
- normalized loss coordinate uses `x = 1/lambda` and adverse-side normalization;
- structural robustness domain is the full closure `x ∈ [0,1]`;
- lookback uses one pre-frozen reference participation governor, not `W*(theta)`;
- `EPSILON_ADV_BAR` derives from `log(P_MAX_REF/P_TARGET_REF)` if the capacity governor is independently authorized;
- endpoint equality is an exact full-domain lambda-discharge proof for the shortest-passing-window rule;
- q requires a dedicated disjoint external selection split;
- unresolved lambda can be nonmaterial for lookback without becoming globally resolved.

Still open before any endpoint/window calibration:

- numerical/reference authority for `P_TARGET_REF` and `P_MAX_REF`;
- candidate windows;
- q candidate set / stability statistic / resampling / stability threshold / split construction;
- calibration-domain implementation;
- source/provider and daily-notional route;
- calendar/date sampling;
- true-zero target treatment;
- minimum-history / insufficient-history policy;
- final numerical capacity-support threshold/functional beyond the measurement-selector reference governor.

No numerical lookback calibration, D05 ceiling visibility or Form-4 outcome access is authorized by this amendment.
