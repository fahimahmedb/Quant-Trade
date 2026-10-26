# D09 ROUTE-B COST-PARAMETER SOURCE / JOINT-SCENARIO CONTRACT — 2026-09-17

**Status:** CLOSED / FROZEN STRUCTURE — PARAMETER-SPECIFIC NUMERICAL SOURCE RULES STILL TO BE INSTANTIATED  
**Authority:** Blue Team / Mission Control  
**Parents:** `D09_ROUTE_B_FRICTION_MARGIN_PARTITION_2026-09-17.md`, `D09_ROUTE_B_M_ECONOMIC_UNCERTAINTY_ENVELOPE_2026-09-17.md`

## 1. Purpose

This contract governs how Route B will obtain expected forward-cost parameters for `K_forward` and joint model-risk scenarios for `M_economic` without source shopping, independent-envelope composition, or threshold-driven capital selection.

It freezes structure before any numerical source search or candidate-value inspection.

No numerical cost coefficient, uncertainty interval, D05 ceiling or Form 4 outcome is consumed by this artifact.

## 2. Parameter-specific source governance

There is no global authority rule such as:

`USE_MICROSTRUCTURE_LITERATURE`.

Every parameter in the frozen cost inventory must carry its own source contract.

For each `parameter_id`, freeze/hash before numerical source inspection:

- exact economic quantity/estimand;
- execution regime and population applicability;
- unit and normalization;
- central expected-value role in `K_forward`;
- model-risk role in the joint scenario envelope;
- admissible source classes for that parameter;
- source applicability/exclusion rule;
- source priority/tiering rule where applicable;
- deterministic multiple-source rule;
- evidence-update/version rule;
- failure state if no source passes.

A source admissible for one cost parameter is not automatically admissible for another.

**Invariants**

- `SOURCE_AUTHORITY_IS_PARAMETER_SPECIFIC`
- `GLOBAL_MICROSTRUCTURE_LABEL_DOES_NOT_AUTHORIZE_PARAMETER_VALUE`
- `PARAMETER_SOURCE_RULE_PRECEDES_CANDIDATE_VALUES`

## 3. Multiple-source rule is not the Route-A minimum

Route B is estimating expected forward cost and model uncertainty. It is not constructing a one-sided lower power floor.

Therefore the historical Route-A rule:

`take the minimum across independently admissible sources`

is `N/A_CURRENT_LINEAGE` for cost calibration.

For each parameter, the frozen source contract must specify what happens when multiple sources pass.

Permitted structures include only predeclared deterministic procedures, for example:

- ordered applicability tiers, consuming the highest-priority non-empty tier;
- a parameter-specific meta-estimator when sources are commensurable;
- a jointly calibrated dataset/model route;
- `SOURCE_SET_NONCOMMENSURABLE -> PARAMETER_UNRESOLVED` when no scientifically meaningful aggregation has been pre-specified.

No rule may select the lowest cost, highest cost, most convenient study, most favorable MEUE, or post-hoc preferred source.

There is deliberately **no single global aggregation functional** imposed on all cost parameters. The scientific quantity and available evidence differ by parameter; the aggregation rule is part of each parameter's frozen contract.

**Invariants**

- `ROUTE_A_SOURCE_MINIMUM_DOES_NOT_TRANSFER_TO_EXPECTED_COST`
- `MULTIPLE_SOURCE_RULE_IS_PARAMETER_SPECIFIC`
- `NO_RESULT_DRIVEN_SOURCE_SELECTION`

## 4. Initial Form-4 cost inventory classes

The active inventory must account for the following economic cost classes where applicable under the final execution convention. Exact formulas and numerical source contracts remain separate parameter records.

### F1 — explicit fees / commissions

Expected explicit transaction charges for entry and exit.

### F2 — opening-regime entry crossing / spread

Expected execution loss attributable to the authorized first-open entry regime relative to the frozen executable reference price.

Generic intraday spread evidence is inadmissible unless the parameter-specific contract proves representativeness for the opening regime.

### F3 — opening-regime entry slippage / auction-continuous transition

Expected execution loss specific to the selected opening execution mechanism that is not already represented in F2 or F4.

This component must not double count the market move defining `T_j`.

### F4 — market impact

Expected impact under the frozen execution policy as a function of permitted liquidity, participation, order-size and execution-regime inputs.

### F5 — exit execution cost

Expected spread/slippage/impact at the final authorized exit convention. Its exact regime is instantiated only after the final D07/O3 economic-exit implementation is consumable.

### F6 — financing / borrow

Expected financing or borrow cost only where economically applicable to the final policy/exposure. A zero value requires explicit authority; omission is not equivalent to zero.

### F7 — residual-capital drag

Included only if the frozen economic accounting convention identifies a causal incremental cost from capital that cannot be deployed because of the Form-4 policy. It must not duplicate the separate Capital Opportunity Set or program/research opportunity cost.

Any later new cost class requires the governed inventory/version consequence. It cannot be inserted merely because final MEUE appears too low or high.

**Invariants**

- `ENTRY_OPEN_COST_IS_SEPARATE_MODEL_DIMENSION`
- `EXIT_COST_REQUIRES_FINAL_EXIT_REGIME`
- `OMITTED_COST_IS_NOT_IMPLICIT_ZERO`
- `NEW_COST_CLASS_AFTER_RESULT_REQUIRES_VERSION_CONSEQUENCE`

## 5. Participation and liquidity are state inputs, not free calibration knobs

For impact and any other participation-dependent term, define the permitted causal chain:

`theta`
→ `G, A_claim^G, C, execution policy, permitted liquidity state`
→ `participation(theta)`
→ `K_forward(theta)`
→ `M_economic(theta)`
→ `MEUE(theta)`.

The direction is one-way.

The resulting `MEUE(theta)` may not feed back into the same evaluation to alter `C`, `A_claim`, participation, or another component of `theta`.

**Invariants**

- `THETA_PRECEDES_COST_AND_MARGIN_EVALUATION`
- `MEUE_DOES_NOT_FEED_BACK_TO_THETA_SAME_EVALUATION`
- `NO_SIZE_SEARCH_TO_MAKE_MEUE_ATTAINABLE`

## 6. Theta selection must itself be pre-frozen

Because cost and margin depend on size/liquidity, final economic evaluation requires a deterministic authorized `theta` selection rule.

Before D05 ceiling visibility, freeze the rule specifying:

- which upstream D02/D03/D07/A-CONSTRUCTOR objects may determine `theta`;
- permitted capital point/domain selection inside `C_claim(G*)`;
- permitted liquidity/reference inputs;
- failure state when no authorized `theta` can be instantiated;
- whether multiple predeclared economic scenarios are evaluated and, if so, their authority/multiplicity semantics.

Forbidden:

`choose C -> compute MEUE -> change C because threshold is inconvenient -> recompute`.

That is threshold shopping even if every iteration is outcome-blind.

**Invariant:** `THETA_SELECTION_RULE_PRECEDES_MEUE_RESULT`.

## 7. Joint uncertainty scenarios replace marginal-envelope addition

Spread, impact, opening slippage, liquidity and participation uncertainty may share data, model assumptions and misspecification channels.

Therefore Route B does not define total model risk as:

`sum_k marginal_parameter_margin_k`

unless a future independent proof establishes that such a decomposition has the intended economic meaning without under/over-counting dependence.

The default current-lineage object is a frozen set of coherent joint cost-model scenarios:

`S_cost = {s_0, s_1, ..., s_m}`.

Each scenario `s` contains a mutually coherent vector of relevant parameter/model states, including their dependence constraints.

- `s_0` identifies the expected/central model used to instantiate `K_forward`.
- adverse scenarios represent independently defensible joint model-risk states.
- scenarios are not generated as an unrestricted Cartesian product of marginal endpoints unless that construction is independently justified.

**Invariants**

- `M_ECONOMIC_USES_JOINT_COST_SCENARIOS`
- `MARGINAL_ENVELOPES_ARE_NOT_SUMMED_BY_DEFAULT`
- `JOINT_SCENARIO_SET_PRECEDES_NUMERICAL_SCENARIO_VALUES`
- `NO_UNJUSTIFIED_CARTESIAN_WORST_CASE`

## 8. Scenario-source construction

Before inspecting numerical source values, the scenario protocol must define:

- which parameter source contracts feed each scenario dimension;
- how cross-parameter dependence is represented;
- which combinations are economically/model-coherent;
- central-scenario construction;
- adverse-scenario construction;
- rule for conflicting/noncommensurable evidence;
- scenario update/version rule;
- failure state when joint dependence cannot be justified.

If marginal parameter evidence exists but the joint scenario structure cannot be justified:

`JOINT_COST_SCENARIO_UNRESOLVED`.

This blocks consumable `M_economic`; it does not authorize an independence assumption by default.

**Invariant:** `UNKNOWN_PARAMETER_DEPENDENCE_IS_NOT_ZERO_DEPENDENCE`.

## 9. Mapping joint scenarios into M_economic

For fixed authorized `theta`, let:

`BEEE_s(theta)`

be the break-even effect implied by the same frozen `Phi` recipe under scenario `s`.

The central expected-cost model uses `s_0`:

`BEEE_0(theta)`.

The Route-B margin functional must be frozen before D05 ceiling visibility. A canonical candidate consistent with the closed role partition is:

`M_economic(theta) = max_{s in S_cost_adverse} [BEEE_s(theta) - BEEE_0(theta)]_+`

provided the final `Phi`/scenario contract validates this mapping and no separate admitted economic-risk class requires an additional non-overlapping margin component.

This equation is a **freeze candidate**, not yet numerical authority. It becomes consumable only when the final Phi/BEEE recipe and joint scenario construction are closed.

It has the intended direction:

- expected costs remain in `K_forward` / `BEEE_0`;
- adverse model uncertainty raises `M_economic`;
- better independent calibration can narrow `S_cost` and legitimately reduce the margin;
- no final MEUE value is used to tune the scenario set.

## 10. Source-search authorization state

No numerical literature/source search for Form-4 cost calibration is authorized merely by this structural contract.

Before any parameter's candidate numerical values are inspected, that parameter must have a hash-addressable source contract satisfying §§2–3.

Before numerical joint-scenario calibration, the cross-parameter scenario protocol in §8 must also be hash-addressable.

This preserves:

`RULE_BEFORE_VALUES`.

## 11. Current closure and remaining work

Closed/frozen by this artifact:

- source authority is parameter-specific;
- multiple-source aggregation/selection is parameter-specific and cannot inherit Route-A min logic;
- initial Form-4 cost-class inventory;
- participation/liquidity causal order;
- no MEUE-to-theta feedback;
- joint coherent scenarios replace independent marginal-envelope summation;
- unknown cross-parameter dependence does not default to independence.

Still open before numerical calibration/search:

- exact parameter records within F1–F7;
- exact admissible source classes and ordered/aggregation rule for each parameter;
- exact `theta` selection rule;
- exact scenario-dependence construction;
- final adoption or replacement of the candidate `M_economic` functional in §9;
- exact Phi/BEEE consumable recipe.

No D05 ceiling visibility, Form-4 outcome access or numerical source search is authorized by this artifact.
