# D09 ECONOMIC CORE — EC1 ALLOCATION-WEIGHTED EFFECT

**Status:** CLOSED / FROZEN — COMMON D09 CORE  
**Authority:** Blue Team / Mission Control  
**Scope:** effect coordinate, allocation-policy role, economic-value/root semantics. This artifact does not complete the full mini-D09 common specification and does not authorize outcome access.

## 1. Primitive scientific outcome

For each admissible Form 4 threshold crossing `j` under an authorized D07 geometry `G`:

`T_j(G) = R_security,j(G) - R_SPY,j(G)`.

The security and SPY use the same economically valid holding interval and compatible return/corporate-action convention. Entry may not precede the separately authorized public-knowledge rule. `T_j` is gross of Form 4 deployment frictions.

SPY remains the Scientific Benchmark. The dynamic Capital Opportunity Set is not substituted into the scientific outcome.

## 2. Allocation policy is claim-defining

Let `A_CONSTRUCTOR` be the frozen outcome-blind function that maps an admissible geometry plus permitted pre-outcome state into an allocation-policy instance:

`A_CONSTRUCTOR(G, pre_outcome_state, C) -> A_claim^G`.

`A_claim^G` determines, where applicable:

- deployment eligibility;
- relative event weights;
- allocation from permitted pre-outcome state;
- issuer/security capacity clipping;
- overlap/capital-saturation handling;
- treatment of competing simultaneous events.

The policy function is part of the scientific estimand. It is therefore part of the Scientific Claim Fingerprint.

A post-confirmation change that alters relative weights, eligibility, event-specific clipping, or the mapping from pre-outcome state into relative size is `NEW_POLICY_VERSION` and does not inherit confirmatory authority merely because the underlying Form 4 signal is unchanged.

**Invariants**

- `ALLOCATION_POLICY_IS_CLAIM_DEFINING`
- `CLAIM_FINGERPRINT_BINDS_ALLOCATION_POLICY`
- `RELATIVE_WEIGHT_CHANGE_IS_NEW_POLICY_VERSION`

## 3. Constructor versus instance

The final D07 geometry is not required before the allocation semantics can be protected.

Before ceiling visibility, the authority-bearing object is the constructor and its admissible-input contract, not a prematurely selected geometry-specific instance.

After D07 freezes `G*`:

`A_claim^{G*} = A_CONSTRUCTOR(G*, permitted_pre_outcome_state, C)`.

The instance may not rewrite the constructor.

**Invariants**

- `ALLOCATION_CONSTRUCTOR_PRECEDES_D05_CEILING_VISIBILITY`
- `ALLOCATION_INSTANCE_FOLLOWS_FINAL_GEOMETRY`
- `POST_D05_GEOMETRY_INSTANTIATION_CANNOT_REWRITE_ALLOCATION_CONSTRUCTOR`

## 4. Capital domain is proved, not presumed

For each admissible geometry `G`, define `C_claim(G)` as the capital domain on which scientific weight homogeneity is demonstrated under the frozen constructor.

No capital interval receives scientific scaling authority merely because it was chosen in advance.

If for two capital levels in an authorized homogeneous region:

`a_j(C2) = lambda * a_j(C1)`

for one positive scalar `lambda`, with identical eligibility, relative weights, geometry, and no newly binding capacity clipping, the scientific effect coordinate is unchanged.

If capacity clipping or another constraint changes relative weights, the estimand changes and the resulting policy is a new scientific policy version unless already represented as a separately fingerprinted claim.

Until homogeneity is proved, scaling authority is unresolved.

**Invariants**

- `NO_SCALING_AUTHORITY_WITHOUT_WEIGHT_HOMOGENEITY_PROOF`
- `CAPACITY_CLIPPING_THAT_CHANGES_RELATIVE_WEIGHTS_IS_NEW_POLICY_VERSION`
- `C_CLAIM_IS_DERIVED_FROM_HOMOGENEITY_PROOF`

## 5. Economic effect coordinate

For fixed admissible deployment scenario `theta`, let `a_j(theta)` be the exposure assigned by the frozen policy before `T_j` is known.

Define expected deployed exposure over the authority-bearing evaluation regime:

`Q(theta) = E[sum_j a_j(theta)]`.

For `Q(theta) > 0`:

`delta(theta) = E[sum_j a_j(theta) * T_j(G)] / E[sum_j a_j(theta)]`.

`delta(theta)` is the expected gross SPY-relative return per unit of Form 4 capital actually deployed under the frozen policy and deployment scenario.

It is a ratio of population expectations. It is not an unweighted event mean, realized portfolio return, net-of-friction return, expectation of an arbitrary sample ratio, or program ROI.

**Invariants**

- `DELTA_IS_DEPLOYMENT_WEIGHTED_GROSS_SPY_EXCESS`
- `ALLOCATION_WEIGHT_PRECEDES_OUTCOME`
- `UNWEIGHTED_EVENT_MEAN_DOES_NOT_DEFINE_DEPLOYMENT_VALUE`

## 6. Estimand versus estimator

A natural finite-sample estimator may take the form:

`delta_hat = sum_j a_j T_j / sum_j a_j`.

The realized denominator may be random because event count, eligibility, overlap, capacity and pre-outcome weights can vary.

Therefore the variance of `delta_hat` is not generally the variance of one primitive `T_j` divided by an event count.

The primitive transform and the aggregate estimator are distinct authority objects.

**Invariants**

- `PRIMITIVE_RETURN_VARIANCE_IS_NOT_AGGREGATE_ESTIMATOR_VARIANCE`
- `PRIMITIVE_TRANSFORM_DOES_NOT_FIX_POWER_OBJECT`

## 7. Economic value function

For fixed `theta`, define gross economic contribution:

`GROSS_VALUE(delta, theta) = Q(theta) * delta`.

`Q(theta)` must reflect actual frozen allocation/overlap/capital-saturation semantics and is never replaced by naive `C * event_count` annualization.

Define expected forward deployment cost generally as:

`K_forward(delta, theta)`.

Permitted components must declare unit, sign, provenance, applicability and whether they depend on `delta`. Past research cost, Builder cost and sunk program cost remain outside market/deployment MEUE.

The general economic value function is:

`Phi(delta, theta) = GROSS_VALUE(delta, theta) - K_forward(delta, theta)`.

No default assumption is made that `Phi` is affine in `delta`.

## 8. BEEE root semantics

Define:

`R_BEEE(theta) = {delta : Phi(delta, theta) = 0}`.

Authority requires an ex-ante rule for the economically meaningful root.

If the authorized `Phi` is continuous and strictly increasing over the admissible effect domain with one root:

`BEEE(theta) = unique delta such that Phi(delta, theta) = 0`.

Otherwise preserve the appropriate state:

- `BEEE_NO_ECONOMIC_ROOT`
- `BEEE_NONUNIQUE_ROOT`
- `BEEE_NONMONOTONE_MAPPING`

Only in the independently established affine special case where `Q(theta) > 0`, `Q` does not depend on `delta`, and `K_forward` does not depend on `delta`, may one use:

`BEEE(theta) = K_forward(theta) / Q(theta)`.

**Invariant:** `BEEE_QUOTIENT_REQUIRES_AFFINE_COST_INDEPENDENCE`.

## 9. MEUE interface

The common D09 core retains:

`MEUE(theta) = BEEE(theta) + M_economic(theta)`.

The conservative economic-margin rule must be frozen separately before it is consumed. It has the same effect units as `delta`, is not statistical uncertainty, cannot depend on D05 ceilings or Form 4 outcomes, and cannot contain sunk program cost.

This EC1 artifact closes the coordinate and mapping semantics but does **not** by itself complete `M_economic`, all permitted `theta` inputs, or the final Route-B inference-selection contract.

## 10. D07 boundary relation

Allocation is claim-defining but is not added as a new D07 O-dimension.

D07 remains responsible for formation/event/entry/exposure geometry. The frozen allocation constructor consumes the later authorized geometry.

D05-A design-invariance remains tested over the legitimate D07 open geometry. Allocation-weighted outcomes are not D05-A outputs.

## 11. Route relation

The common economic semantics above are required regardless of power-route architecture.

For the current lineage, the separate Blue Power-Route Decision has retired the pre-D07 global power-floor route. Final inference must still target the same frozen deployment-weighted economic coordinate on the final geometry.

## 12. Core invariants

- `SCIENTIFIC_BENCHMARK_REMAINS_SPY`
- `ALLOCATION_POLICY_IS_CLAIM_DEFINING`
- `CLAIM_FINGERPRINT_BINDS_ALLOCATION_POLICY`
- `ALLOCATION_CONSTRUCTOR_PRECEDES_D05_CEILING_VISIBILITY`
- `ALLOCATION_INSTANCE_FOLLOWS_FINAL_GEOMETRY`
- `NO_SCALING_AUTHORITY_WITHOUT_WEIGHT_HOMOGENEITY_PROOF`
- `DELTA_IS_DEPLOYMENT_WEIGHTED_GROSS_SPY_EXCESS`
- `PRIMITIVE_RETURN_VARIANCE_IS_NOT_AGGREGATE_ESTIMATOR_VARIANCE`
- `BEEE_QUOTIENT_REQUIRES_AFFINE_COST_INDEPENDENCE`
- `PROGRAM_COST_DOES_NOT_ENTER_MARKET_DEPLOYMENT_MEUE`
