# D09 ROUTE-B LIQUIDITY-ELIGIBILITY / FINITE-COST-SCENARIO AMENDMENT — 2026-09-17

**Status:** CLOSED / FROZEN STRUCTURAL AMENDMENT — NUMERICAL LIQUIDITY GATE AND SOURCE VALUES STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D09_ECONOMIC_CORE_EC1_ALLOCATION_WEIGHTED_EFFECT.md`, `D09_ROUTE_B_COST_PARAMETER_SOURCE_AND_JOINT_SCENARIO_CONTRACT_2026-09-17.md`

This amendment supersedes any current-lineage reading of the parent cost/scenario contract that would allow an open-ended scenario set, Cartesian endpoint expansion, population-derived liquidity calibration before D05 visibility, or an un-fingerprinted liquidity eligibility rule.

## 1. Finite named scenario set

For Route B, the joint cost uncertainty set is not an arbitrary product of marginal parameter bounds and is not an open continuous uncertainty region consumed directly by the `M_economic` functional.

Before any numerical source values relevant to scenario construction are inspected, freeze/hash a **finite named scenario registry**:

`S_cost = {s_0, s_1, ..., s_m}`

with finite, predeclared `m`.

Each scenario must have:

- immutable `scenario_id` and name;
- economic interpretation;
- full vector of active cost-model dimensions or deterministic construction rule for that full vector;
- explicit cross-parameter dependence/coherence constraints;
- source-contract references for every dimension it consumes;
- applicability domain in `theta`;
- failure state when a required dimension cannot be instantiated;
- update/version rule.

`s_0` is the central expected-cost scenario used by `K_forward`.

Every adverse scenario must represent a separately defensible coherent economic/model state. It is not created merely by combining every adverse marginal endpoint.

**Invariants**

- `S_COST_IS_FINITE_NAMED_AND_PREDECLARED`
- `NO_CARTESIAN_ENDPOINT_EXPANSION`
- `SCENARIO_COHERENCE_PRECEDES_SCENARIO_VALUES`
- `SCENARIO_COUNT_CANNOT_EXPAND_AFTER_MEUE_RESULT`

## 2. `max` is authorized only on the finite registry

The candidate margin functional:

`M_economic(theta) = max_{s in S_cost_adverse} [BEEE_s(theta) - BEEE_0(theta)]_+`

is mathematically meaningful as a `max` only when:

- `S_cost_adverse` is the finite frozen registry defined above;
- every included scenario has a consumable `BEEE_s(theta)` under the same frozen `Phi` recipe;
- no unresolved required scenario is silently dropped;
- the registry was not expanded or contracted because the resulting MEUE was convenient or inconvenient.

If scenario authority is open-ended, continuously parameterized, or missing required members under the frozen registry:

`M_ECONOMIC_SCENARIO_SET_UNRESOLVED`.

The current lineage does not silently replace the finite-registry requirement with a supremum over an open uncertainty set.

**Invariants**

- `M_ECONOMIC_MAX_REQUIRES_FINITE_FROZEN_SCENARIO_SET`
- `UNRESOLVED_REQUIRED_SCENARIO_CANNOT_BE_SILENTLY_DROPPED`

## 3. Liquidity class is an ex-ante deployment assumption, not a D05-discovered calibration input

Microstructure quantities such as spread and impact depend materially on liquidity / capitalization / participation. A broad-market expected spread or impact statistic is not automatically transportable to the Form 4 deployment policy merely because both concern US equities.

Before D05 ceiling visibility, Route B must therefore freeze a deployment-liquidity eligibility rule as part of `theta` and the allocation constructor contract.

Conceptually define:

`L_deploy(theta)` = the ex-ante liquidity class / eligibility rule under which the strategy is willing to deploy.

The rule may use only permitted point-in-time pre-outcome market information and must be defined independently of observed Form 4 return outcomes and D05 ceiling values.

A source for a liquidity-sensitive parameter is admissible only if its parameter-specific source contract establishes applicability to `L_deploy(theta)` or a conservative/explicitly governed transformation to that class.

If applicability cannot be established under the frozen rule:

`PARAMETER_POPULATION_APPLICABILITY_UNRESOLVED`.

The project does not inspect the realized Form 4 population distribution and then choose the liquidity class that makes an external cost estimate convenient.

**Invariants**

- `LIQUIDITY_CLASS_IS_EX_ANTE_DEPLOYMENT_INPUT`
- `D05_POPULATION_DISTRIBUTION_DOES_NOT_CHOOSE_COST_CALIBRATION_CLASS`
- `SOURCE_APPLICABILITY_MUST_RESOLVE_TO_FROZEN_LIQUIDITY_CLASS`

## 4. Liquidity eligibility is claim-defining through `A_claim`

EC1 already makes deployment eligibility part of `A_claim` and therefore part of the deployment-weighted estimand.

A liquidity gate that determines whether an event receives deployable weight is therefore not a merely operational Desk preference.

The Scientific Claim Fingerprint must bind the liquidity-eligibility semantics consumed by `A_CONSTRUCTOR`, including at minimum:

- `LIQUIDITY_ELIGIBILITY_RULE_HASH`;
- permitted liquidity metric(s) and point-in-time semantics;
- threshold/rule version once numerically instantiated;
- missing-liquidity behavior;
- relation to capacity clipping and `C_claim(G)`;
- source/reference-data identity required to evaluate the gate.

Changing the liquidity eligibility rule in a way that changes which events may receive non-zero scientific weight is:

`NEW_POLICY_VERSION`.

This does not add a new D07 O-dimension. It is an allocation-policy / deployment-support dimension under EC1.

**Invariants**

- `LIQUIDITY_ELIGIBILITY_IS_CLAIM_FINGERPRINTED`
- `LIQUIDITY_GATE_CHANGE_THAT_CHANGES_SUPPORT_IS_NEW_POLICY_VERSION`
- `LIQUIDITY_ELIGIBILITY_IS_NOT_NEW_D07_O_DIMENSION`

## 5. Interaction with `C_claim(G)`

`C_claim(G)` remains the domain on which weight homogeneity is demonstrated.

The liquidity eligibility rule and the capital-homogeneity rule are related but distinct:

- `L_deploy(theta)` determines which events/securities are eligible for deployment under the claim policy;
- `C_claim(G)` determines where scaling capital preserves relative scientific weights for that policy.

A fixed liquidity threshold does not by itself prove weight homogeneity at larger capital. Capacity clipping may still bind differentially as `C` rises.

Therefore:

`LIQUIDITY_ELIGIBLE != SCALE_HOMOGENEOUS`.

Both rules must be frozen/consumable before they can support final economic authority.

## 6. One-way evaluation order

For any final Route-B economic evaluation, the causal order is:

`freeze/instantiate theta including L_deploy`
→ `A_claim^{G*}(theta)`
→ `participation/liquidity state permitted by theta`
→ `K_forward(theta, s_0)`
→ `BEEE_0(theta)`
→ `BEEE_s(theta)` for each frozen adverse scenario
→ `M_economic(theta)`
→ `MEUE(theta)`.

There is no same-evaluation feedback from `MEUE` to:

- liquidity threshold/class;
- `C`;
- allocation support/weights;
- participation target;
- scenario membership.

Any search of these objects because the resulting threshold is unattractive is threshold shopping and requires a new policy/protocol version with the corresponding authority consequences.

**Invariants**

- `THETA_AND_LIQUIDITY_GATE_PRECEDE_MEUE_EVALUATION`
- `MEUE_DOES_NOT_TUNE_LIQUIDITY_CLASS`
- `MEUE_DOES_NOT_TUNE_CAPITAL_OR_PARTICIPATION_SAME_EVALUATION`

## 7. Parameter-specific source contract consequence

Every liquidity-sensitive parameter record must now declare:

- exact `L_deploy` applicability condition;
- whether the source is direct for that class or requires a frozen transport/transformation;
- what happens if several admissible sources cover the same class;
- what happens if source coverage spans only part of the permitted class;
- whether one source jointly informs multiple scenario dimensions and therefore creates cross-parameter dependence that must be represented at scenario level.

A single study/source may inform several parameters, but that shared provenance must be carried into scenario coherence rather than treated as independent evidence.

**Invariant:** `SHARED_SOURCE_PROVENANCE_CREATES_SCENARIO_DEPENDENCE_METADATA`.

## 8. Numerical search remains unauthorized

This amendment does not select:

- an ADV threshold;
- a market-cap threshold;
- any spread/impact coefficient;
- any scenario value;
- any numerical `M_economic`.

Before numerical source inspection for a parameter, its full parameter-specific source contract and `L_deploy` applicability rule must be hash-addressable.

Before numerical scenario calibration, the finite named `S_cost` registry and cross-parameter construction rules must be hash-addressable.

Current state:

- finite-scenario architecture: **CLOSED / FROZEN**;
- liquidity-as-`theta` role: **CLOSED / FROZEN**;
- liquidity eligibility fingerprint requirement: **CLOSED / FROZEN**;
- exact numerical liquidity gate: **OPEN / NOT YET CONSUMABLE**;
- parameter-specific numerical source contracts: **OPEN / NOT YET CONSUMABLE**;
- numerical `S_cost`: **OPEN / NOT YET CONSUMABLE**;
- numerical `M_economic`: **OPEN / UNRESOLVED**.

No D05 ceiling visibility, numerical cost-source search or Form 4 outcome access is authorized by this artifact.
