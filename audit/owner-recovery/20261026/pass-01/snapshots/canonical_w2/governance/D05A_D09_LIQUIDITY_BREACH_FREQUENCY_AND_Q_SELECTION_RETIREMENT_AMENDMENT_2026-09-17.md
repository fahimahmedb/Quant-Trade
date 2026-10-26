# D05-A / D09 LIQUIDITY BREACH-FREQUENCY / q-SELECTION RETIREMENT AMENDMENT — 2026-09-17

**Status:** CLOSED / FROZEN STRUCTURAL AMENDMENT — NUMERICAL BREACH BUDGET / PRECISION BUDGET STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D05A_D09_Q_DOMAIN_VALUE_STABILITY_AND_UNDERPOWERED_PROTOCOL_AMENDMENT_2026-09-17.md`, `D05A_D09_LIQUIDITY_LAMBDA_DISCHARGE_AND_REFERENCE_PARTICIPATION_AMENDMENT_2026-09-17.md`, `D05A_D09_PMAX_CORPORATE_DEPENDENCE_AND_SPLIT_CAPACITY_AMENDMENT_2026-09-17.md`

This amendment replaces current-lineage q-selection as a data-selected robustness object with an equivalent, more direct governance object: the maximum admissible frequency/mass of liquidity-forecast errors that would breach the frozen reference participation ceiling. It removes the circular rule “choose the highest q estimable by the available corpus” and preserves the same economic tail-protection meaning without requiring the calibration corpus to choose q.

No Form-4 target values, D05 ceilings, return outcomes, candidate-window results, provider values or numerical breach tolerances are consumed by this amendment.

## 1. Quantile-threshold criterion is equivalent to a breach-frequency criterion

For any frozen candidate window `W`, normalized lambda endpoint `x`, weighted calibration distribution and threshold `EPSILON_ADV_BAR`, define:

`L_bar_x(E) = max(E,0) + x * max(-E,0)`

and the weighted CDF:

`F_{W,x}(l) = P_weighted(L_bar_x(E(W)) <= l)`.

Using the frozen lower-quantile convention:

`Q_q(W,x) = inf { l : F_{W,x}(l) >= q }`.

Then, including mass/ties at the threshold under this convention:

`Q_q(W,x) <= EPSILON_ADV_BAR`

if and only if:

`F_{W,x}(EPSILON_ADV_BAR) >= q`,

which is equivalent to:

`P_weighted(L_bar_x(E(W)) > EPSILON_ADV_BAR) <= 1 - q`.

Define the breach-frequency object:

`B_W(x) = P_weighted(L_bar_x(E(W)) > EPSILON_ADV_BAR)`.

The current-lineage tail-protection rule can therefore be governed directly as:

`B_W(x) <= BETA_LIQ_MAX`.

The equivalent quantile level is then deterministic:

`Q_LIQ = 1 - BETA_LIQ_MAX`.

`Q_LIQ` is no longer selected from the calibration corpus.

**Invariants**

- `QUANTILE_THRESHOLD_AND_BREACH_FREQUENCY_ARE_EQUIVALENT_UNDER_FROZEN_QUANTILE_CONVENTION`
- `Q_LIQ_EQUALS_ONE_MINUS_BETA_LIQ_MAX`
- `CALIBRATION_CORPUS_DOES_NOT_SELECT_Q`

## 2. Magnitude tolerance and frequency tolerance are distinct governance objects

`EPSILON_ADV_BAR` and `BETA_LIQ_MAX` answer different questions.

`EPSILON_ADV_BAR = log(P_MAX_REF / P_TARGET_REF)` determines the **magnitude** of forecast optimism that would push the fixed reference participation from `P_TARGET_REF` to the hard execution-risk ceiling `P_MAX_REF`.

`BETA_LIQ_MAX` determines the maximum admissible **weighted frequency/mass** of calibration cases in which that magnitude boundary may be exceeded.

The ratio `P_MAX_REF / P_TARGET_REF` does not mathematically determine `BETA_LIQ_MAX`.

Therefore `BETA_LIQ_MAX` is a separately frozen execution-risk / measurement-governance tolerance. It must be fixed before candidate-window results and may not depend on:

- available calibration-corpus size;
- which W passes;
- Form-4 support or outcomes;
- D05 ceilings;
- BEEE/MEUE;
- a desire to make the lookback selector feasible.

Because changing `BETA_LIQ_MAX` can change `W*` and therefore deployment support, the final `LIQUIDITY_ELIGIBILITY_RULE_HASH` must bind its value, rationale/version identifier and update rule.

**Invariants**

- `BREACH_MAGNITUDE_AND_BREACH_FREQUENCY_ARE_DISTINCT`
- `BETA_LIQ_MAX_IS_PRE_RESULT_GOVERNANCE_INPUT`
- `BETA_LIQ_MAX_IS_CLAIM_DEFINING_THROUGH_LOOKBACK_SELECTION`
- `AVAILABLE_CORPUS_CAPACITY_CANNOT_CHOOSE_BETA_LIQ_MAX`

## 3. q candidate domain and q-selection split are retired for this lineage

Because `Q_LIQ = 1 - BETA_LIQ_MAX` is fixed ex ante, the following current-lineage objects are retired as active selectors:

- `Q_ADMISSIBLE = [Q_TAIL_MIN, Q_ESTIMABILITY_MAX]`;
- “choose the highest stable q”;
- q candidate lattice/list;
- a dedicated `Q_SELECTION_SPLIT` whose purpose is to choose q from data;
- empirical q-selection based on available capacity.

The historical q-domain/value-stability amendment remains useful for documenting why corpus-driven q selection is invalid, but its q-selection machinery is superseded by this amendment.

No information is lost: the economically relevant tail requirement is now encoded directly by `BETA_LIQ_MAX`, while estimability/precision becomes a feasibility condition for the breach-frequency statistic rather than a selector of the risk tolerance.

**Invariants**

- `Q_SELECTION_IS_RETIRED_CURRENT_LINEAGE`
- `RISK_TOLERANCE_IS_NOT_SELECTED_BY_ESTIMABILITY`
- `ESTIMABILITY_CAN_BLOCK_THE_PROTOCOL_BUT_CANNOT_RELAX_THE_RISK_TOLERANCE`

## 4. Why tail-count logic is valid on probability scale but not sufficient for quantile-value precision

A minimum count of observations in the tail can support probability/tail-frequency estimation.

It does not, without additional assumptions, determine the relative precision of the **value** of a quantile. Quantile-value uncertainty also depends on the local distribution/density around the quantile, and current calibration observations are clustered by corporate-dependence group rather than iid rows.

The current lineage therefore does not claim that `N_required(q)` derived solely from expected tail count guarantees relative precision of `Q_q` as a loss value.

By moving the authority-bearing statistic to the breach probability `B_W(x)`, the estimation target is a bounded probability/mass, which admits ex-ante probability-scale precision guarantees without a local-density model.

**Invariants**

- `TAIL_COUNT_DOES_NOT_BY_ITSELF_AUTHORIZE_QUANTILE_VALUE_PRECISION`
- `BREACH_PROBABILITY_IS_THE_AUTHORITY_BEARING_TAIL_ESTIMAND`

## 5. Equal-security weighting remains the target measure

The existing loss-distribution weighting remains controlling:

- each eligible `CALIBRATION_SECURITY_LINEAGE_ID` receives equal total mass within the authority-bearing calibration sample;
- dates within a security share that security's mass under the frozen date-sampling rule;
- market cap, ADV magnitude, realized next-session notional and Form-4 frequency do not determine weight.

Thus `B_W(x)` is the breach mass under the same equal-security target distribution previously used by the quantile statistic.

Corporate-reorganization dependence remains represented by `CALIBRATION_DEPENDENCE_GROUP_ID`; this grouping is the independence/uncertainty unit, not a replacement for equal-security target weighting.

## 6. Precision requirement is frozen on probability scale

Before observing eligible external capacity or candidate-window breach results, freeze/hash:

- `BETA_LIQ_MAX`;
- an absolute probability-scale estimation tolerance `TAU_BETA > 0`;
- confidence/failure probability `ALPHA_BETA` if the design uses an explicit confidence guarantee;
- the exact weighted breach estimator;
- corporate-dependence-group uncertainty/concentration rule;
- uniformity rule across all predeclared candidate windows and lambda endpoints `x in {0,1}`;
- minimum effective dependence-group capacity rule;
- failure state.

The authority question is no longer “is the q-th quantile value stable?” It is:

> Can the breach mass relevant to every candidate window and both lambda endpoints be estimated with the predeclared probability-scale precision required to apply the frozen `BETA_LIQ_MAX` rule?

The numerical `TAU_BETA` / `ALPHA_BETA` remain open. They may not be chosen after seeing available corpus capacity or window results.

**Invariants**

- `BREACH_PRECISION_IS_DEFINED_ON_PROBABILITY_SCALE`
- `BREACH_PRECISION_REQUIREMENT_PRECEDES_AVAILABLE_CAPACITY`
- `BREACH_PRECISION_IS_UNIFORM_OVER_WINDOWS_AND_LAMBDA_ENDPOINTS`

## 7. Capacity design uses effective independent corporate-group mass

Corporate-linked lineages are not independent rows. Let the frozen calibration sample induce dependence groups `g = 1,...,G`.

Under equal-security target weighting, let `omega_g` be the total normalized target weight carried by dependence group `g`, so:

`omega_g >= 0`, `sum_g omega_g = 1`.

Define the design-effective independent group mass:

`N_GROUP_EFF = 1 / sum_g omega_g^2`.

This quantity equals the ordinary group count only when groups carry equal target mass. It decreases when one corporate-dependence group carries disproportionate security weight.

The pre-result precision design must derive a required minimum:

`N_GROUP_EFF_REQUIRED = f(TAU_BETA, ALPHA_BETA, familywise/uniformity rule)`

under the separately frozen bounded-cluster concentration or confidence construction.

The exact function `f` remains open, but it must be fixed before comparing to the eligible corpus.

This preserves equal-security target weighting while preventing a large linked corporate group from being counted as many independent units.

**Invariants**

- `BREACH_CAPACITY_IS_MEASURED_IN_EFFECTIVE_DEPENDENCE_GROUP_MASS`
- `EQUAL_SECURITY_TARGET_WEIGHTING_DOES_NOT_IMPLY_SECURITY_LEVEL_INDEPENDENCE`
- `EFFECTIVE_GROUP_CAPACITY_REQUIREMENT_PRECEDES_CAPACITY_COMPARISON`

## 8. Underpowered versus unresolved states

After the complete breach-frequency precision design is frozen, compute the eligible external calibration capacity under the already-frozen domain, source, lineage, corporate-linkage and exclusion rules.

If:

`N_GROUP_EFF_AVAILABLE < N_GROUP_EFF_REQUIRED`,

emit:

`LIQUIDITY_BREACH_CALIBRATION_UNDERPOWERED`.

This state does not authorize increasing `BETA_LIQ_MAX`, increasing `TAU_BETA`, increasing `ALPHA_BETA`, weakening corporate grouping, changing equal-security weighting or using Form-4 data to rescue the protocol.

If capacity is adequate but the authorized estimator/precision procedure cannot be instantiated because required inputs or assumptions fail, emit:

`LIQUIDITY_BREACH_CALIBRATION_UNRESOLVED`.

These states supersede `Q_SELECTION_UNDERPOWERED` / `Q_SELECTION_UNRESOLVED` for the retired q-selection consumer.

**Invariants**

- `BREACH_CALIBRATION_UNDERPOWERED_IS_NOT_RISK_TOLERANCE_RESCUE`
- `BREACH_CALIBRATION_UNRESOLVED_IS_DISTINCT_FROM_UNDERPOWERED`

## 9. Window-selection rule after q retirement

Once `BETA_LIQ_MAX`, `EPSILON_ADV_BAR`, the candidate windows, weighting, source semantics and breach-precision design are frozen and capacity authority is satisfied, define for each candidate `W` and lambda endpoint `x`:

`B_W(x) = P_weighted(L_bar_x(E(W)) > EPSILON_ADV_BAR)`.

The lambda endpoint discharge remains structurally valid because for every observation `L_bar_x(E)` is nondecreasing in `x`; therefore breach indicators and `B_W(x)` are nondecreasing in `x`.

For each endpoint, define the shortest passing window by the frozen breach-frequency rule:

`W*(x) = shortest W such that B_W(x) <= BETA_LIQ_MAX`.

If:

`W*(0) = W*(1) = W0`,

then the same monotone-threshold argument proves `W0` is the shortest passing window for every `x in [0,1]`, yielding:

`LAMBDA_UNRESOLVED_BUT_NONMATERIAL_TO_LOOKBACK`.

If endpoint selections/failure states differ:

`LAMBDA_MATERIAL_TO_LOOKBACK`.

Thus q retirement does not break the exact lambda endpoint theorem; it expresses the same threshold logic directly in breach-frequency coordinates.

## 10. Split consequence

A dedicated q-selection split is no longer justified merely to choose q, because q is fixed by `BETA_LIQ_MAX` before data.

Current-lineage calibration therefore returns to a simpler design:

- one external **WINDOW_CALIBRATION_SAMPLE** may be used for authority-bearing breach-frequency estimation and `W*` selection, subject to the frozen effective-group precision requirement;
- no part of that sample chooses `BETA_LIQ_MAX`, `P_MAX_REF`, `P_TARGET_REF`, candidate windows or precision tolerances;
- if a future nuisance parameter genuinely requires empirical tuning, it must receive its own separately justified split or cross-fitting contract; the retired q selector does not justify retaining a split by inertia.

This supersedes the prior minimum-q-split / residual-window-split architecture for the current lineage.

**Invariants**

- `NO_Q_SELECTION_SPLIT_AFTER_Q_IS_GOVERNANCE_FIXED`
- `CALIBRATION_DATA_IS_NOT_RESERVED_FOR_A_RETIRED_SELECTOR`
- `WINDOW_CALIBRATION_SAMPLE_CANNOT_TUNE_UPSTREAM_GOVERNANCE_INPUTS`

## 11. Revised local order

Before any external window-calibration result:

`freeze P_MAX_REF governance rule/value + P_TARGET_REF convention/value`

`-> derive EPSILON_ADV_BAR = log(P_MAX_REF/P_TARGET_REF)`

`-> freeze BETA_LIQ_MAX breach-frequency tolerance`

`-> set Q_LIQ = 1 - BETA_LIQ_MAX mechanically`

`-> freeze candidate windows / source / calibration-domain / date-sampling / weighting / corporate-dependence rules`

`-> freeze TAU_BETA / ALPHA_BETA / weighted breach estimator / uniform confidence-concentration rule`

`-> derive N_GROUP_EFF_REQUIRED`

`-> only then compute N_GROUP_EFF_AVAILABLE`

`-> if insufficient: LIQUIDITY_BREACH_CALIBRATION_UNDERPOWERED`

`-> if sufficient: instantiate WINDOW_CALIBRATION_SAMPLE and compute endpoint breach statistics`

`-> apply shortest-passing endpoint rule`

`-> if endpoint W* agree: discharge lambda for lookback`

`-> otherwise: promote lambda/execution economics to the scientific critical path`.

No available-capacity result may revise `BETA_LIQ_MAX`, `TAU_BETA`, `ALPHA_BETA`, candidate windows or corporate-group rules.

## 12. Current state

Closed/frozen:

- tail protection is represented directly as governed breach frequency at the reference participation boundary;
- `Q_LIQ = 1 - BETA_LIQ_MAX` is deterministic, not data-selected;
- q candidate domain / highest-stable-q selector / dedicated q-selection split are retired for current lineage;
- magnitude tolerance `EPSILON_ADV_BAR` and frequency tolerance `BETA_LIQ_MAX` are distinct;
- breach probability/mass is the authority-bearing tail estimand;
- precision requirement is on probability scale, uniform across candidate windows and lambda endpoints;
- effective independence is measured at corporate-dependence-group level while preserving equal-security target weighting;
- inadequate capacity produces `LIQUIDITY_BREACH_CALIBRATION_UNDERPOWERED` without risk-tolerance rescue;
- the lambda endpoint theorem remains valid in breach-frequency coordinates.

Still open before numerical calibration:

- numerical `P_MAX_REF` authority/value rule;
- numerical `P_TARGET_REF` convention/value rule;
- numerical `BETA_LIQ_MAX` and its governance rationale;
- numerical `TAU_BETA` / `ALPHA_BETA` and exact confidence/concentration construction;
- exact formula for `N_GROUP_EFF_REQUIRED`;
- candidate windows;
- exact dependence-group resolver/source implementation;
- source/provider and daily-notional route;
- calibration-domain/date-sampling/true-zero/minimum-history rules;
- final window-calibration sample construction.

No numerical window calibration, D05 ceiling visibility or Form-4 outcome access is authorized by this amendment.
