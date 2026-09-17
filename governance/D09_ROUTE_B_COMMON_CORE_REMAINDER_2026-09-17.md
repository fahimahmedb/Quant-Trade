# D09 ROUTE-B COMMON CORE REMAINDER — 2026-09-17

**Status:** DECIDED_NOT_SPECIFIED — ACTIVE ROUTE-B DEPENDENCY  
**Authority:** Blue Team / Mission Control  
**Parent decisions:** `D09_ECONOMIC_CORE_EC1_ALLOCATION_WEIGHTED_EFFECT.md`, `BLUE_POWER_ROUTE_B_DECISION_2026-09-17.md`, `D09_ROUTE_B_FRICTION_MARGIN_PARTITION_2026-09-17.md`

## 1. Purpose

Route A is retired for the current Form 4 lineage. D09 therefore no longer needs to construct a global pre-D07 power-floor map over all admissible `theta`, optimize an infimum, freeze a discretization scheme, or support external lower-bound transport.

Route B still requires a consumable economic threshold for final inference on the final authorized geometry and allocation-policy instance.

This artifact lists only the remaining common/Route-B D09 obligations.

**Invariant:** `RETIRED_ROUTE_DOES_NOT_LEAVE_PHANTOM_D09_OBLIGATIONS`.

## 2. Already closed by EC1

The following are closed/frozen in `D09_ECONOMIC_CORE_EC1_ALLOCATION_WEIGHTED_EFFECT.md`:

- primitive outcome coordinate starts from gross SPY simple excess under authorized geometry;
- allocation policy is claim-defining;
- `A_CONSTRUCTOR` versus `A_claim^{G*}` distinction;
- `C_claim(G)` is derived from demonstrated weight homogeneity;
- primary economic coordinate:
  `delta(theta) = E[sum a_j T_j] / E[sum a_j]`;
- primitive-return variance is not aggregate-estimator variance;
- general value mapping:
  `Phi(delta, theta) = Q(theta) * delta - K_forward(delta, theta)`;
- BEEE is defined by the economically meaningful root of `Phi`;
- `BEEE = K_forward/Q` is only an affine special case;
- program/research sunk costs remain outside market/deployment MEUE.

EC1 closes semantics, not all executable inputs.

## 3. Remaining active object A — `DELTA_COORDINATE_COMPATIBILITY_GATE`

The economic meaning of `delta` is closed, but final Route-B consumption still requires proof that the final scientific outcome/accounting implementation is on the same coordinate.

Before final inference authority, bind/hash at minimum:

- exact return interval after final D07/public-time resolution;
- exact corporate-action / distribution convention;
- terminal/delisting treatment as jointly governed with D19 where applicable;
- benchmark interval/convention compatibility;
- exact aggregation from primitive `T_j` to the allocation-weighted estimator.

Possible states:

- `DELTA_COORDINATE_COMPATIBLE`
- `DELTA_COORDINATE_MISMATCH`
- `DELTA_COORDINATE_UNRESOLVED`

A mismatch reopens the final outcome/estimand implementation. It does not redefine EC1's economic coordinate to fit available data.

## 4. Remaining active object B — `PHI_AND_BEEE_ROOT_CONTRACT`

EC1 fixes the general root semantics. Route B still needs the exact consumable `Phi` instance recipe.

Before ceiling visibility under the Route-B firewall, freeze the rule that identifies:

- admissible forward deployment-cost components;
- units and sign convention for every component;
- whether each component can depend on `delta`, capital, geometry, liquidity or allocation state;
- the effect domain on which root existence/monotonicity is evaluated;
- the deterministic root-selection/failure rule.

Required outputs include:

- `BEEE(theta_final)` when a unique economically meaningful root exists;
- `BEEE_NO_ECONOMIC_ROOT`;
- `BEEE_NONUNIQUE_ROOT`;
- `BEEE_NONMONOTONE_MAPPING`.

The recipe must be outcome-blind even though its final numerical instantiation may consume the later authorized final geometry and market-state inputs allowed by that recipe.

## 5. Forward-friction role is closed; expected-cost calibration remains open

The role partition is frozen in `D09_ROUTE_B_FRICTION_MARGIN_PARTITION_2026-09-17.md`.

For Route B:

`K_forward(theta) = E[forward deployment cost | frozen execution regime and permitted inputs]`.

`K_forward` is an expected-cost object, not a conservative upper bound.

Model/economic uncertainty about the expected-cost model belongs to `M_economic`, subject to the frozen anti-double-counting rule.

Therefore the former state:

`FRICTION_TO_MEUE_RULE = UNRESOLVED`

is superseded by:

`FRICTION_ROLE_PARTITION = CLOSED`.

Still unresolved are the executable inputs/calibration needed to instantiate that role:

- exact Form 4 cost-component inventory;
- provenance/estimation rule for every expected-cost parameter;
- allowed central/expected parameter estimator;
- failure state when an expected-cost input lacks authority;
- permitted dependence on capital, geometry, liquidity and allocation state.

The current V1 execution model may supply implementation structure or provisional inputs, but assumed spread/impact coefficients do not become calibrated authority merely because they exist in code.

**Invariants**

- `K_FORWARD_IS_EXPECTED_FORWARD_COST_NOT_CONSERVATIVE_BOUND`
- `K_FORWARD_RECIPE_PRECEDES_D05_CEILING_VISIBILITY`
- `K_FORWARD_NUMERICAL_INSTANTIATION_MAY_FOLLOW_FINAL_GEOMETRY`
- `EXISTING_EXECUTION_PARAMETER_IS_NOT_AUTOMATIC_CALIBRATION_AUTHORITY`

## 6. Remaining active object C — `M_economic`

Route B still requires:

`MEUE(theta_final) = BEEE(theta_final) + M_economic(theta_final)`.

The conservative economic-margin role is now partially closed:

- model/economic risk protection belongs here rather than in a prudentially inflated `K_forward`;
- uncertainty about expected-cost parameters belongs here unless explicitly reassigned under a non-overlap decomposition;
- the same risk may not be charged in both `K_forward` and `M_economic`;
- asymmetric economic harm from cost-model misspecification must be respected.

The **numerical/functional calibration rule remains open**.

It must define before ceiling visibility:

- purpose/risk classes covered by the margin;
- units and sign;
- plausible parameter/model uncertainty set or another independently justified representation;
- deterministic mapping from that uncertainty into effect-coordinate units;
- treatment of asymmetric downside;
- whether the margin is constant, state-dependent or a deterministic functional of permitted ex-ante inputs;
- how uncertainty already charged elsewhere is excluded from duplicate charge;
- failure state when required inputs are unavailable;
- whether/how the rule varies inside the authorized `C_claim(G*)` domain.

The margin is not statistical standard error, alpha, MDE, program TCO or research opportunity cost.

It may not depend on D05 ceiling values or Form 4 outcomes.

**Invariants**

- `ECONOMIC_MODEL_RISK_LIVES_IN_M_ECONOMIC`
- `M_ECONOMIC_MUST_RESPECT_ASYMMETRIC_MODEL_RISK`
- `FRICTION_AND_MARGIN_DO_NOT_DOUBLE_COUNT_SAME_RISK`

## 7. Route-B final instantiation

Route B does **not** require an authority-bearing `MEUE_POWER_FLOOR_MAP` over all admissible geometries/capital scenarios.

It requires:

1. the common economic recipe frozen before ceiling visibility;
2. final D07 geometry `G*` selected under the separately frozen selection procedure;
3. `A_claim^{G*}` instantiated from the frozen `A_CONSTRUCTOR`;
4. an authorized capital point/domain inside `C_claim(G*)` according to the frozen economic recipe;
5. permitted expected forward-friction inputs instantiated under the frozen `K_forward` recipe;
6. `BEEE(theta_final)` derived mechanically;
7. `M_economic(theta_final)` derived mechanically under its frozen calibration rule;
8. `MEUE(theta_final)` derived mechanically;
9. final D08 inference targeting that same economic coordinate.

No global infimum, full-domain search or certified numerical discretization is required merely because those objects were previously needed by Route A.

**Invariants**

- `ROUTE_B_REQUIRES_FINAL_MEUE_NOT_GLOBAL_POWER_FLOOR_MAP`
- `FINAL_MEUE_INSTANTIATION_CANNOT_REWRITE_PRE_FROZEN_RECIPE`

## 8. Relation to Route-B visibility firewall

The Route-B firewall cannot be marked satisfied until the following D09-side objects are hash-addressable:

- EC1;
- this remainder contract;
- frozen friction/margin role partition;
- closed executable `K_forward` expected-cost recipe;
- closed numerical/functional `M_economic` calibration rule;
- consumable `PHI_AND_BEEE_ROOT_CONTRACT` recipe;
- `A_CONSTRUCTOR` plus `C_claim(G)` derivation rule.

The final numerical `MEUE(theta_final)` need not exist before D05-A ceiling visibility because `G*` is chosen after D05-A. What must be frozen first is the recipe and the inputs it is allowed to consume.

**Invariant:** `RECIPE_PRECEDES_CEILING_NUMERICAL_FINAL_MEUE_MAY_FOLLOW_GEOMETRY`.

## 9. Explicitly retired Route-A D09 objects

The following are `N/A_CURRENT_LINEAGE`:

- `MEUE_POWER_FLOOR_MAP` over full `THETA`;
- `THETA_POWER_FLOOR`;
- external floor-source transport/search;
- `inf_theta N_raw_required(theta)`;
- certified lower-bound optimization/discretization;
- Route-A deployment-domain monotonicity rules;
- Route-A floor-recipe contamination firewall.

They are not invalid. They are superseded because their consumer was retired.

## 10. Current status

- EC1: **CLOSED / FROZEN**
- friction versus margin role partition: **CLOSED / FROZEN**
- delta final-coordinate compatibility: **NOT YET CONSUMABLE**
- exact `Phi/BEEE` recipe inputs: **NOT YET CONSUMABLE**
- executable `K_forward` expected-cost recipe: **OPEN / NOT YET CONSUMABLE**
- numerical/functional `M_economic` calibration rule: **OPEN / UNRESOLVED**
- full-domain power-floor map: **N/A CURRENT LINEAGE**
- external numerical power-floor search: **NOT AUTHORIZED / NO CURRENT CONSUMER**

No outcome access or ceiling-visibility authorization is granted by this artifact.
