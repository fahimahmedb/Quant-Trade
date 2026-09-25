# BLUE ROUTE-B CHECKPOINT ADDENDUM — q DOMAIN / VALUE STABILITY / UNDERPOWERED — 2026-09-17

**Status:** CURRENT CHECKPOINT ADDENDUM  
**Authority:** Blue Team / Mission Control  
**Parents:** `BLUE_ROUTE_B_PMAX_CORPORATE_SPLIT_CAPACITY_CHECKPOINT_ADDENDUM_2026-09-17.md`, `D05A_D09_Q_DOMAIN_VALUE_STABILITY_AND_UNDERPOWERED_PROTOCOL_AMENDMENT_2026-09-17.md`

This addendum controls where more recent/specific than the parent checkpoint.

## 1. New controlling artifact

Add:

`governance/D05A_D09_Q_DOMAIN_VALUE_STABILITY_AND_UNDERPOWERED_PROTOCOL_AMENDMENT_2026-09-17.md`.

## 2. q candidate object

The current lineage no longer treats q as an arbitrary small list of familiar percentiles.

The authority-bearing object is a derived admissible interval:

`Q_ADMISSIBLE = [Q_TAIL_MIN, Q_ESTIMABILITY_MAX]`.

- lower bound: tail-protection requirement;
- upper bound: estimability-design requirement.

The exact numerical/rule derivations remain open.

## 3. q stability target

q stability is measured on estimated quantile **values**, not on window rankings or W* stability.

The Q_SELECTION_SPLIT may evaluate loss values needed to assess estimability, but it may not produce authority-bearing W ranking or W* selection.

Stability must cover every downstream quantile value consumed by the lambda endpoint procedure, uniformly over:

- every predeclared candidate window;
- `x=0` and `x=1` normalized lambda endpoints.

Corporate `CALIBRATION_DEPENDENCE_GROUP_ID` remains the outer resampling cluster.

## 4. Design-before-capacity rule

The q protocol must be frozen in this order:

`q-domain rule`

`-> estimator / clustered resampling / value-stability statistic`

`-> stability threshold / tail-support rule`

`-> derive Q_ESTIMABILITY_MAX / Q_ADMISSIBLE`

`-> derive N_Q_REQUIRED`

`-> only then compare with eligible external dependence-group capacity`.

Available corpus size cannot be used to relax upstream q rules.

## 5. Failure states

If eligible external dependence-group capacity is below frozen `N_Q_REQUIRED`:

`Q_SELECTION_UNDERPOWERED`.

No threshold/q-domain/resampling/corporate-linkage relaxation is authorized.

If capacity is adequate but no admissible q satisfies the frozen value-stability criterion:

`Q_SELECTION_UNRESOLVED`.

These states are distinct.

## 6. Split consequence

Q split remains minimum ex-ante sufficient, where “sufficient” now means the frozen `N_Q_REQUIRED` or deterministic grouped/stratified equivalent.

Window split receives residual eligible information subject to its own frozen minimum/coverage rules.

No post-result split reallocation is authorized.

## 7. Current blockers

Still open before numerical q/window calibration:

- q tail-protection rule / `Q_TAIL_MIN`;
- q estimator convention;
- value-stability statistic and threshold;
- clustered resampling/confidence/repetition rule;
- minimum tail/group support;
- `Q_ESTIMABILITY_MAX` derivation;
- `N_Q_REQUIRED` derivation;
- numerical `P_MAX_REF` and `P_TARGET_REF` authority/value rules;
- corporate-dependence resolver implementation;
- deterministic split assignment / WINDOW minimum coverage;
- candidate windows;
- source/provider / daily-notional / calibration-domain / date-sampling / true-zero / minimum-history rules.

Route-B firewall remains unsatisfied. No D05 ceiling visibility, q/window calibration or Form-4 outcome access is authorized.
