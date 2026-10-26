# D09 ROUTE-B FRICTION / ECONOMIC-MARGIN PARTITION — 2026-09-17

**Status:** CLOSED / FROZEN ROLE PARTITION — NUMERICAL CALIBRATION STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D09_ECONOMIC_CORE_EC1_ALLOCATION_WEIGHTED_EFFECT.md`, `D09_ROUTE_B_COMMON_CORE_REMAINDER_2026-09-17.md`

## 1. Decision

For the current Route-B lineage, `K_forward` is used to define the **expected forward deployment cost** entering the economic break-even equation.

It is not itself a conservative bound.

The canonical role split is:

`K_forward(theta) = E[forward deployment cost | frozen execution regime and permitted inputs]`

and:

`MEUE(theta) = BEEE(theta) + M_economic(theta)`.

`M_economic` carries the separately frozen protection for model risk / economic uncertainty that should make the market/deployment threshold more demanding than pure break-even.

**Invariants**

- `K_FORWARD_IS_EXPECTED_FORWARD_COST_NOT_CONSERVATIVE_BOUND`
- `ECONOMIC_MODEL_RISK_LIVES_IN_M_ECONOMIC`
- `EXPECTED_COST_AND_ECONOMIC_MARGIN_HAVE_DISTINCT_ROLES`

## 2. Why the split is necessary

BEEE answers the break-even question under the frozen expected execution-cost model.

If a prudential upward distortion is embedded inside `K_forward` and the same uncertainty is also charged through `M_economic`, the same risk is counted twice.

Therefore:

`K_forward` may not be converted into an upper confidence bound, worst-case cost, conservative quantile, or arbitrary prudential markup merely because a more demanding threshold is desired.

Any such protection belongs to the separately governed `M_economic` rule unless a future Blue decision explicitly reallocates a named risk class and removes it from the margin.

**Invariant:** `NO_HIDDEN_CONSERVATISM_INSIDE_K_FORWARD`.

## 3. K_forward is a recipe, not a pre-D05 number

Route B freezes the economic recipe before human-visible D05 ceilings, not the final numerical cost.

The frozen recipe must state for every admitted cost component:

- component name;
- economic unit and sign convention;
- execution regime / applicability condition;
- deterministic formula or estimation functional;
- allowed input classes;
- provenance requirement;
- whether the expected value depends on capital, geometry, liquidity, allocation state or delta;
- failure state if a required input is unavailable.

The final numerical value may be instantiated only after the final authorized geometry `G*`, `A_claim^{G*}`, and authorized capital point/domain inside `C_claim(G*)` are available.

Conceptually:

`K_FORWARD_RECIPE(theta_inputs) -> expected forward cost`.

**Invariants**

- `K_FORWARD_RECIPE_PRECEDES_D05_CEILING_VISIBILITY`
- `K_FORWARD_NUMERICAL_INSTANTIATION_MAY_FOLLOW_FINAL_GEOMETRY`
- `FINAL_K_FORWARD_CANNOT_REWRITE_PRE_FROZEN_RECIPE`

## 4. Expected-cost components

Where economically applicable, `K_forward` may contain expected values for components such as:

- commission / explicit fees;
- spread crossing;
- slippage;
- market impact;
- financing;
- borrow;
- other execution losses causally attributable to expressing the policy;
- economically real residual-capital drag when explicitly defined by the frozen accounting convention.

Admission of a component does not authorize an arbitrary value.

Every component requires a provenance-bearing expected-value rule.

Past research expense, Builder cost, program TCO and sunk cost remain outside `K_forward` and outside market/deployment MEUE.

## 5. Parameter uncertainty is not expected cost

Suppose an expected-cost model uses parameter `b`, for example an impact/spread coefficient.

The expected-cost recipe may use a frozen central/expected estimate:

`b_hat_expected`

under a declared provenance/estimation rule.

Uncertainty that the true coefficient may be materially worse than `b_hat_expected` is not silently converted into a larger `K_forward` value.

That model-risk contribution belongs to `M_economic`.

Thus distinguish:

`EXPECTED_COST_PARAMETER`

from:

`PARAMETER_MODEL_RISK`.

**Invariants**

- `PARAMETER_UNCERTAINTY_IS_NOT_SILENTLY_PROMOTED_TO_EXPECTED_COST`
- `MODEL_RISK_ON_COST_PARAMETERS_FEEDS_M_ECONOMIC`

## 6. Asymmetric model risk

Economic model error need not be symmetric.

Underestimating a forward-cost coefficient can authorize a threshold that is too low and can therefore admit deployment that is economically unattractive.

Overestimating the same coefficient raises the threshold and can instead reject an otherwise viable opportunity.

`M_economic` must therefore be calibrated to the economically adverse side of the declared model-risk set rather than assumed to be a generic fixed percentage.

The exact calibration rule is **not closed by this artifact**.

It must later define, outcome-blind and before D05 ceiling visibility:

- the risk classes it covers;
- the plausible parameter/model set or another independently justified uncertainty representation;
- the deterministic mapping from that uncertainty representation into effect-coordinate units;
- how asymmetry is handled;
- failure behavior when the uncertainty representation is not available.

**Invariant:** `M_ECONOMIC_MUST_RESPECT_ASYMMETRIC_MODEL_RISK`.

## 7. No double counting

Every named uncertainty/risk class must have exactly one primary economic home:

- expected component -> `K_forward`; or
- model/economic uncertainty protection -> `M_economic`.

If a future rule intentionally spreads one risk across both objects, it must prove and document a non-overlap decomposition.

Otherwise:

`FRICTION_MARGIN_DOUBLE_COUNT -> INVALID_MEUE_RECIPE`.

**Invariants**

- `FRICTION_AND_MARGIN_DO_NOT_DOUBLE_COUNT_SAME_RISK`
- `ONE_RISK_CLASS_ONE_PRIMARY_ECONOMIC_HOME`

## 8. Mean versus statistical execution noise

This partition concerns economic expected cost and economic model-risk protection.

It does not automatically change the statistical outcome transform.

For the current gross SPY-excess primitive outcome, expected execution cost enters `Phi -> BEEE -> MEUE` but execution-noise variance is not silently inserted into the variance of the gross return transform.

If final science later targets net executed return, the statistical execution-error variance/covariance becomes a separately admitted authority object.

**Invariant:** `ECONOMIC_COST_ROLE_DOES_NOT_SILENTLY_DEFINE_STATISTICAL_NOISE_ROLE`.

## 9. Relation to existing V1 execution model

The existing V1 system may supply implementation structure or provisional model inputs, but it does not automatically supply scientific calibration authority for Route B.

In particular, assumed spread/impact coefficients must retain their actual provenance state. Their existence in production/shadow code does not convert them into calibrated economic truth.

The Route-B recipe may consume them only under an explicitly frozen status/provenance rule and with the unresolved model risk handled through `M_economic` or an explicit failure state.

**Invariant:** `EXISTING_EXECUTION_PARAMETER_IS_NOT_AUTOMATIC_CALIBRATION_AUTHORITY`.

## 10. Current state after this decision

Closed/frozen:

- `K_forward` purpose = expected forward deployment cost;
- conservative/model-risk protection belongs to `M_economic`;
- recipe-before-ceiling / numerical-instantiation-after-geometry ordering;
- anti-double-counting role partition;
- parameter uncertainty is distinct from expected parameter value;
- asymmetric model risk must be respected.

Still open:

- exact component inventory for Form 4 Route B;
- provenance/estimation rule for each expected-cost parameter;
- exact plausible uncertainty representation for assumed/un-calibrated parameters;
- deterministic numerical `M_economic` calibration rule;
- failure behavior when the required friction/model-risk evidence is unavailable;
- final numerical `K_forward`, BEEE and MEUE on `G*` / `A_claim^{G*}` / authorized `C`.

No outcome access or D05 ceiling visibility authorization is granted by this artifact.
