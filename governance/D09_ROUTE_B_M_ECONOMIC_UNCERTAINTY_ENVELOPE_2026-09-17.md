# D09 ROUTE-B M_ECONOMIC UNCERTAINTY ENVELOPE — 2026-09-17

**Status:** CLOSED / FROZEN CALIBRATION STRUCTURE — NUMERICAL ENVELOPES STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D09_ECONOMIC_CORE_EC1_ALLOCATION_WEIGHTED_EFFECT.md`, `D09_ROUTE_B_FRICTION_MARGIN_PARTITION_2026-09-17.md`

## 1. Decision

`M_economic` is calibrated from an ex-ante uncertainty envelope over economically relevant model parameters, not from the final MEUE value and not by applying an arbitrary percentage markup.

For each non-calibrated or imperfectly calibrated economic parameter `p_k`, define before D05 ceiling visibility:

- a central/expected-value rule `p_k^E` used by `K_forward` where applicable;
- an independently justified plausible set `U_k` representing model/economic uncertainty;
- a deterministic adverse-side mapping from `U_k` into the common `delta` effect coordinate;
- a provenance state and failure state.

The joint economic uncertainty object is:

`U_economic = combine_k(U_k, frozen dependence/aggregation rule)`.

The exact numerical intervals/sets are not fixed by this artifact.

**Invariants**

- `UNCERTAINTY_ENVELOPE_PRECEDES_MARGIN_VALUE`
- `M_ECONOMIC_IS_DERIVED_FROM_FROZEN_UNCERTAINTY_STRUCTURE`
- `MEUE_RESULT_CANNOT_TUNE_ITS_OWN_MARGIN`

## 2. Separation from expected cost

`K_forward(theta)` continues to use expected forward deployment costs under the frozen execution regime.

`M_economic(theta)` protects against the economically adverse consequences of model uncertainty around those expected costs and other separately admitted economic-model risks.

For every parameter/risk class:

`EXPECTED_COMPONENT -> K_forward`

or

`MODEL_UNCERTAINTY_PROTECTION -> M_economic`.

The same adverse deviation may not be charged twice.

**Invariant:** `ONE_RISK_CLASS_ONE_PRIMARY_ECONOMIC_HOME`.

## 3. Envelope admission rule

A numerical uncertainty envelope is admissible only if its construction is independent of:

- D05 ceiling values;
- Form 4 return outcomes;
- the resulting BEEE/MEUE magnitude;
- whether the resulting threshold appears favorable or unfavorable to the claim.

Admissible evidence classes may include, once separately specified and frozen:

- external microstructure literature;
- broad-market execution data not selected using Form 4 outcomes;
- independently calibrated execution records from an eligible non-target corpus;
- engineering plausibility bounds with explicit governance status when stronger evidence is unavailable.

The source/admission rule must be defined before inspecting candidate values that could influence the envelope.

**Invariants**

- `ENVELOPE_EVIDENCE_IS_TARGET_OUTCOME_BLIND`
- `ENVELOPE_SOURCE_RULE_PRECEDES_CANDIDATE_VALUES`
- `THRESHOLD_REASONABLENESS_IS_NOT_CALIBRATION_EVIDENCE`

## 4. Asymmetric adverse-side calibration

Model uncertainty is not assumed symmetric in economic consequence.

For each uncertainty set `U_k`, define the adverse economic deviation relative to the expected-cost model:

`DeltaK_k^adverse(theta) = adverse_side_effect_on_forward_value(U_k, theta)`.

`M_economic` must map the frozen adverse uncertainty set into `delta` units. Conceptually, in an affine local case with positive deployed exposure `Q(theta)`:

`M_economic(theta) >= adverse_incremental_cost_protection(theta) / Q(theta)`.

This formula is illustrative only; the general rule must respect the frozen non-linear `Phi` where applicable.

The calibration rule must never inspect the resulting MEUE and then shrink/expand the envelope because the answer appears too high or too low.

**Invariants**

- `M_ECONOMIC_USES_ECONOMICALLY_ADVERSE_SIDE`
- `NO_POST_RESULT_MARGIN_RESCUE`
- `NONLINEAR_PHI_REQUIRES_COMPATIBLE_MARGIN_MAPPING`

## 5. Width of uncertainty is economically meaningful

Poorly calibrated execution parameters create a wider admissible uncertainty envelope and therefore may raise `M_economic`.

Improved independent calibration can legitimately narrow the envelope and lower the required economic effect, provided:

- calibration evidence is independent of Form 4 target outcomes;
- the envelope-construction rule was frozen before ceiling visibility;
- the update follows a pre-authorized evidence-update rule or creates the appropriate new protocol version before outcome exposure.

Thus execution-calibration work can have direct scientific/economic value by reducing uncertainty in the market/deployment threshold without changing the underlying claim.

**Invariant:** `BETTER_INDEPENDENT_EXECUTION_CALIBRATION_MAY_REDUCE_MODEL_RISK_MARGIN`.

This is not permission to calibrate until MEUE becomes attractive.

## 6. Opening-specific execution-timing component

The Form 4 economic entry rule targets the first authorized regular-session open after public observability.

Therefore the expected-cost recipe must treat execution timing at the open as an explicit modeling dimension rather than silently substituting a generic all-session spread/slippage estimate.

Define a separately named component or parameter family, for example:

`OPEN_EXECUTION_TIMING_COST(theta)`.

Its empirical magnitude is **not asserted by this artifact**.

The requirement is only that the final expected-cost model and uncertainty envelope distinguish the opening execution regime whenever generic intraday calibration is not proven representative of that regime.

Potential contributors may include:

- opening spread/crossing cost;
- opening-auction versus continuous-open execution convention;
- overnight information incorporation / opening gap interaction with executable price;
- opening-specific slippage/impact conditional on participation and liquidity.

These components must not double count the scientific market return itself. The contract must distinguish a causal execution loss relative to the authorized executable benchmark price from the market move that defines `T_j`.

**Invariants**

- `ENTRY_AT_OPEN_REQUIRES_OPENING_REGIME_COST_MODEL`
- `GENERIC_INTRADAY_SPREAD_IS_NOT_AUTOMATIC_OPEN_CALIBRATION`
- `OPEN_EXECUTION_COST_MUST_NOT_DOUBLE_COUNT_MARKET_RETURN`

## 7. Parameter inventory structure

Before numerical envelope calibration, every economic parameter must be entered in a registry with at minimum:

- `parameter_id`;
- cost/risk component;
- expected-value role (`K_forward`, none, or other declared role);
- uncertainty role (`M_economic`, none, or separately declared role);
- execution regime;
- units;
- dependence on `G`, `A_claim`, `C`, liquidity and participation;
- central-estimate provenance rule;
- uncertainty-envelope provenance rule;
- allowed evidence classes;
- update/version rule;
- failure state when evidence is unavailable.

A parameter absent from the frozen inventory cannot later be inserted because the resulting MEUE appeared inconvenient without a protocol/version consequence.

## 8. Failure states

If an expected-cost central value cannot be justified under the frozen rule:

`K_FORWARD_PARAMETER_UNRESOLVED`.

If a central value exists but the required uncertainty envelope cannot be justified:

`M_ECONOMIC_ENVELOPE_UNRESOLVED`.

If the envelope exists but cannot be mapped to the `delta` coordinate under the frozen `Phi`:

`M_ECONOMIC_MAPPING_UNRESOLVED`.

These states block consumable final MEUE authority. They do not authorize an arbitrary fallback margin.

## 9. Recipe versus numerical instantiation

Before D05 ceiling visibility, freeze/hash:

- parameter inventory schema and admitted parameter classes;
- source/admission rules for central estimates and uncertainty envelopes;
- interval/set construction rules;
- joint aggregation/dependence rule across risk classes;
- adverse-side mapping to the economic effect coordinate;
- anti-double-counting map;
- failure/update/version rules.

After final `G*`, `A_claim^{G*}` and authorized `C` are available, instantiate the permitted parameters and derive:

`K_forward(theta_final)`
→ `BEEE(theta_final)`
→ `M_economic(theta_final)`
→ `MEUE(theta_final)`.

**Invariant:** `M_ECONOMIC_RECIPE_PRECEDES_CEILING_NUMERICAL_MARGIN_MAY_FOLLOW_FINAL_GEOMETRY`.

## 10. Current status

Closed/frozen:

- margin derives from a pre-frozen uncertainty envelope;
- envelope evidence is target-outcome blind;
- adverse-side/asymmetric economic mapping is required;
- final MEUE cannot be used to tune its own margin;
- opening execution timing receives an explicit cost/model-risk dimension;
- better independent calibration may narrow the margin under governed update/version rules.

Still open:

- exact Form 4 parameter inventory;
- exact evidence-source/search/admission protocol for each parameter;
- numerical central estimates;
- numerical uncertainty intervals/sets;
- dependence/aggregation rule across parameter uncertainties;
- exact non-linear mapping into `M_economic` where needed;
- final numerical margin.

No D05 ceiling visibility or outcome access is authorized by this artifact.
