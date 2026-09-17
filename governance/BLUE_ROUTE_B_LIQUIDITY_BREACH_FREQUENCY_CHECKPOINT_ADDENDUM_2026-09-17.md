# BLUE ROUTE-B CHECKPOINT ADDENDUM — LIQUIDITY BREACH-FREQUENCY TAIL CALIBRATION — 2026-09-17

**Status:** CURRENT CHECKPOINT ADDENDUM  
**Authority:** Blue Team / Mission Control  
**Parents:** `BLUE_ROUTE_B_Q_DOMAIN_STABILITY_CHECKPOINT_ADDENDUM_2026-09-17.md`, `D05A_D09_LIQUIDITY_BREACH_FREQUENCY_AND_Q_SELECTION_RETIREMENT_AMENDMENT_2026-09-17.md`

This addendum controls where more recent/specific than the q-domain checkpoint.

## 1. q-selection retired

Current lineage no longer selects q from external calibration data.

Define the governed breach-frequency tolerance:

`BETA_LIQ_MAX`.

Then:

`Q_LIQ = 1 - BETA_LIQ_MAX`

mechanically.

Retired current-lineage selector objects:

- `Q_ADMISSIBLE`;
- `Q_TAIL_MIN` / `Q_ESTIMABILITY_MAX` as selection bounds;
- highest-stable-q rule;
- q candidate lattice;
- dedicated `Q_SELECTION_SPLIT` used to choose q;
- `N_Q_REQUIRED` for a retired q selector.

Historical q-domain artifacts remain part of the audit trail but do not control the current selector.

## 2. Tail rule now has two orthogonal governance coordinates

Magnitude boundary:

`EPSILON_ADV_BAR = log(P_MAX_REF/P_TARGET_REF)`.

Frequency boundary:

`BETA_LIQ_MAX = maximum authorized weighted breach mass above EPSILON_ADV_BAR`.

The participation ratio determines magnitude, not breach frequency. `BETA_LIQ_MAX` therefore requires its own pre-result governance rationale/value.

Both objects can change W* and are claim-defining through `LIQUIDITY_ELIGIBILITY_RULE_HASH`.

## 3. Authority-bearing statistic

For candidate W and lambda endpoint x:

`B_W(x) = P_weighted(L_bar_x(E(W)) > EPSILON_ADV_BAR)`.

Pass condition:

`B_W(x) <= BETA_LIQ_MAX`.

This is equivalent to the prior quantile-threshold condition under the frozen weighted lower-quantile convention.

The lambda endpoint theorem remains controlling with shortest-passing windows at x=0 and x=1.

## 4. Precision and capacity

Quantile-value stability is no longer the calibration target.

Freeze before capacity inspection:

- `BETA_LIQ_MAX`;
- probability-scale tolerance `TAU_BETA`;
- confidence/failure level `ALPHA_BETA` where used;
- weighted breach estimator;
- corporate-dependence-group confidence/concentration construction;
- uniformity across all candidate W and x in {0,1};
- required effective dependence-group capacity rule.

Under equal-security target weighting, define group weights omega_g and:

`N_GROUP_EFF = 1 / sum_g omega_g^2`.

Derive `N_GROUP_EFF_REQUIRED` before computing eligible available capacity.

If available effective capacity is insufficient:

`LIQUIDITY_BREACH_CALIBRATION_UNDERPOWERED`.

If capacity is adequate but the frozen estimator/confidence protocol cannot be instantiated:

`LIQUIDITY_BREACH_CALIBRATION_UNRESOLVED`.

Neither state authorizes relaxing `BETA_LIQ_MAX`, `TAU_BETA`, `ALPHA_BETA`, corporate grouping or target weighting.

## 5. Split consequence

The dedicated q-selection split is retired.

The current lineage may reserve the eligible external calibration information for one authority-bearing `WINDOW_CALIBRATION_SAMPLE`, because no nuisance q is selected from it.

This sample may estimate breach frequencies and select W* only after all upstream governance inputs, candidate windows, weighting, source semantics and precision rules are frozen.

A future empirically tuned nuisance parameter would require a separately justified split/cross-fitting contract; the retired q split does not persist by inertia.

## 6. Revised immediate order

Before any external calibration results:

1. freeze numerical/value authority for `P_MAX_REF`;
2. freeze numerical convention for `P_TARGET_REF`;
3. derive `EPSILON_ADV_BAR`;
4. freeze `BETA_LIQ_MAX` and its governance rationale;
5. freeze candidate windows / source / calibration-domain / date-sampling / weighting / corporate-dependence semantics;
6. freeze `TAU_BETA` / `ALPHA_BETA` / breach estimator / uniform confidence-concentration rule;
7. derive `N_GROUP_EFF_REQUIRED`;
8. only then compute eligible `N_GROUP_EFF_AVAILABLE`;
9. if sufficient, instantiate the window calibration sample and compute endpoint breach statistics;
10. apply shortest-passing endpoint W* rule and lambda materiality discharge.

No available-corpus count or result may feed back to steps 1–7.

## 7. Current blockers

Still open before numerical window calibration:

- numerical `P_MAX_REF` rule/value;
- numerical `P_TARGET_REF` convention/value;
- numerical `BETA_LIQ_MAX` governance value;
- numerical `TAU_BETA` / `ALPHA_BETA`;
- exact weighted clustered breach-confidence construction and `N_GROUP_EFF_REQUIRED` formula;
- candidate windows;
- corporate-dependence source/resolver;
- source/provider / daily-notional route;
- calibration domain / date sampling / true-zero / minimum-history rules.

Route-B firewall remains unsatisfied. No D05 ceiling visibility, Form-4 outcome access or numerical window calibration is authorized.
