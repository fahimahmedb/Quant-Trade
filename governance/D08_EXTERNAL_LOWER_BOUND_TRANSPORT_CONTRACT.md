# D08 EXTERNAL LOWER-BOUND TRANSPORT CONTRACT

**Status:** FROZEN CONTRACT — ASTRA-CORRECTED — SOURCE SEARCH NOT YET AUTHORIZED  
**Authority:** Blue Team / Mission Control  
**Purpose:** define ex ante when external evidence may supply authority-bearing ingredients for `N_RAW_REQUIRED_FLOOR`.

Source search remains blocked until the D08 delta gate, D09 MEUE mapping dependency, raw-count power formulation, source-search rule and uncertainty treatment are resolved.

## 1. Core distinction

Every admitted source contains two separate claims.

### `SOURCE_MEASUREMENT`

What the external source measured or reported.

### `TRANSPORT_ASSUMPTION`

Quant's governance assumption that the external quantity validly lower-bounds the target floor object or an ingredient used to derive it.

The second is not proven merely because literature reports the first.

**Invariant:** `TRANSPORT_ASSUMPTION_IS_NOT_SOURCE_MEASUREMENT`.

## 2. Required direction

The final authority-bearing object is a lower bound on the **raw number of statistical observations required** for target power.

For a direct required-sample route:

`N_raw_required_external_floor <= N_raw_required_target`.

For a variance/dependence ingredient route, every transported inequality must be oriented such that the resulting normalized raw requirement satisfies the same inequality.

The transport direction must make a false early impossibility verdict harder, never easier.

**Invariants**

- `TRANSPORT_DIRECTION_PROTECTS_AGAINST_FALSE_IMPOSSIBILITY`
- `RAW_REQUIRED_SAMPLE_IS_THE_COMMON_POWER_FLOOR_UNIT`

## 3. Admission before values

A source is admitted using non-numerical pre-frozen properties only, including where relevant:

- population class;
- return/outcome definition;
- horizon;
- benchmark treatment;
- study design;
- provenance class;
- measurement construction;
- whether the statistic can be mapped to the frozen raw-count power object.

Numerical variance/power/required-N values may be used only after admission.

**Invariant:** `SOURCE_ADMISSION_PRECEDES_SOURCE_VALUES`.

## 4. Search universe, search procedure and stopping rule precede values

Before numerical source inspection, freeze/hash-address at minimum:

- allowed bibliographic/data-source classes;
- search query/procedure or reproducible discovery protocol;
- inclusion/exclusion rule;
- duplicate/publication-family handling;
- search stopping rule;
- extraction schema;
- rule for inaccessible or incompletely reported studies;
- rule for superseded/corrected versions.

A search may not stop because a convenient low required-N value has been found or continue because an inconvenient value was found.

**Invariants**

- `SOURCE_SEARCH_RULE_PRECEDES_SOURCE_VALUES`
- `SEARCH_STOPPING_IS_NOT_RESULT_DRIVEN`

## 5. Floor-transform compatibility

A source must measure the frozen floor transform directly or an object connected to it by a lower-bound-preserving mapping frozen before source values are inspected.

Otherwise:

`SOURCE_INADMISSIBLE_FOR_POWER_FLOOR`.

## 6. Population transport

The contract requires directional dominance, not vague comparability.

An admitted external population must belong to a predeclared class for which Quant explicitly adopts the governance assumption that the transported uncertainty/power ingredient is oriented favorably enough that the normalized raw required-sample floor cannot exceed the true target requirement.

This assumption must remain labelled as governance, not later rewritten as an empirical theorem.

## 7. Horizon rule

Direct evidence at the frozen 20-regular-session horizon is preferred.

No horizon scaling is authorized without a pre-frozen lower-bound proof connecting the source statistic to the frozen 20-session outcome transform.

For example, if variance is transported, the rule must establish an inequality of the form:

`V_20_target >= f(source_measurement)`

under explicitly frozen assumptions.

The function `f` and its assumptions must be frozen before candidate scaled-source values are inspected.

`20 x Var(1d)` is not automatically a valid lower bound because negative autocovariance can reduce cumulative variance.

A looser valid function may be used; its cost is reduced early-rejection power.

**Invariants**

- `NO_HORIZON_SCALING_WITHOUT_PRE_FROZEN_LOWER_BOUND_PROOF`
- `NO_HORIZON_RULE_AFTER_NUMERICAL_SOURCE_INSPECTION`

## 8. Alpha, target power and inferential family

Before source values are inspected, freeze/hash-address:

- scientific alpha/error policy relevant to the floor;
- target power;
- one-sided/two-sided status as applicable;
- the inference/test family used to convert transported ingredients into `N_raw_required`;
- any multiplicity coupling required by D10.

A source using a different alpha/power/test construction is admissible only through a pre-frozen conservative transformation that preserves the lower-bound direction.

**Invariant:** `POWER_POLICY_PRECEDES_EXTERNAL_VALUES`.

## 9. Direct-power / direct-required-sample route

A source may directly supply or permit deterministic derivation of:

`N_raw_required_external(effect_T, alpha, target_power)`.

It is authority-bearing only when:

- the floor transform is admissible;
- MEUE conversion is frozen;
- alpha and target power are compatible or conservatively transformed by a pre-frozen rule;
- population transport passes;
- horizon transport passes;
- the source's inference construction validly lower-bounds the target raw required sample.

Otherwise it is a prior, not floor authority.

## 10. Variance-plus-dependence ingredient route

If no direct raw-required-sample source is admitted, a construction may instead use externally transported statistical ingredients.

For example:

- marginal variance lower envelope;
- covariance/dependence restrictions;
- a directly transported aggregate variance lower envelope.

A helper factor may be defined, such as:

`kappa = V_aggregate / D_diagonal`,

but PSD alone is insufficient to establish a positive `kappa_floor`.

The transported ingredients do **not** create an `N_eff` object for comparison with D05. They feed the frozen `Power_n(...)` construction, which returns `N_raw_required`.

**Invariants**

- `POSITIVE_DEPENDENCE_FLOOR_REQUIRES_ECONOMIC_OR_EMPIRICAL_RESTRICTION`
- `DEPENDENCE_ENTERS_POWER_FLOOR_EXACTLY_ONCE`
- `NO_EXTERNAL_NEFF_BRIDGE_TO_D05`

## 11. Source-estimation uncertainty

A point estimate reported by an external source is not automatically a lower bound.

For every numerical source measurement, freeze before inspection the rule that converts sampling/measurement uncertainty into an authority-bearing lower-bound ingredient.

The rule may use, where justified:

- reported confidence intervals;
- standard errors with a pre-frozen confidence construction;
- conservative endpoint extraction;
- exact reported bounds;
- or another independently reviewable method.

If the source does not contain enough information to apply the frozen uncertainty rule:

`SOURCE_NUMERIC_BOUND_UNRESOLVED`.

It may remain a prior/diagnostic but cannot support the power floor.

**Invariant:** `SOURCE_POINT_ESTIMATE_IS_NOT_AUTOMATIC_BOUND`.

## 12. Every independently admissible source enters

Each admitted source that successfully produces an authority-bearing normalized raw required-sample lower bound yields:

`L_s_raw`.

Then:

`N_RAW_REQUIRED_FLOOR_EXTERNAL = min_s L_s_raw`.

The minimum deliberately protects against a false `POWER_IMPOSSIBLE` verdict: a lower raw requirement floor makes early rejection harder.

This is the same one-sided logic as:

`UNKNOWN_AVAILABILITY_IS_FAVORABLE_FOR_REJECTION_BOUND`.

Exact duplication/dependence among sources does not create multiplicative evidence or raise the minimum. Publication-family/duplicate handling remains governed by the pre-frozen search rule so that the source inventory is reproducible.

No post-value quality ranking may be introduced to remove an inconvenient low-floor admitted source.

**Invariants**

- `ALL_ADMISSIBLE_BOUNDED_SOURCES_ENTER`
- `MIN_EXTERNAL_FLOOR_PROTECTS_AGAINST_FALSE_IMPOSSIBILITY`
- `EXTERNAL_FLOOR_ARGMIN_IS_EMBARGOED`

## 13. Source authority package

Every admitted authority-bearing source must bind:

- immutable source identity/version/date;
- artifact hash or stable content identity;
- bibliographic/provenance metadata;
- source-family/duplicate identity;
- admission-rule result;
- `TRANSPORT_ASSUMPTION_ID`;
- measured quantity;
- extraction rule/result;
- source-uncertainty transformation;
- horizon/population transformation where applicable;
- normalized `L_s_raw`;
- independent review/certification evidence.

## 14. Failed source search

If no source passes and produces a usable bound:

`NO_ADMISSIBLE_EXTERNAL_FLOOR_SOURCE`.

The transport contract is not relaxed because search failed.

Allowed consequences are:

- pursue another already pre-frozen floor route;
- freeze a new transport/scaling rule only in a new lineage that has not been exposed to candidate numerical values relevant to that rule;
- retain `POWER_REQUIREMENT_UNRESOLVED_SOURCE`.

**Invariant:** `FAILED_SOURCE_SEARCH_DOES_NOT_RELAX_TRANSPORT_CONTRACT`.

## 15. Anti-rescue

After external numerical values/search outcomes have been inspected, the current lineage may not:

- broaden population classes;
- change floor transform;
- change MEUE mapping;
- weaken horizon requirements;
- add a favorable scaling rule;
- remove an admitted low-floor source;
- change alpha/target power;
- change source-uncertainty treatment;
- change search/stop rules to obtain a preferred floor.

Material changes require a new scientific lineage and appropriate contamination treatment.

## 16. D05 interface

D05 consumes only:

- an authority-bearing `N_RAW_REQUIRED_FLOOR`; or
- a cause-preserving unresolved state.

D05 does not source-shop, inspect transform/source argmins, or construct an effective-sample proxy.

**Invariants**

- `D05_CONSUMES_FLOOR_D05_DOES_NOT_SOURCE_SHOP`
- `RAW_CEILING_COMPARES_ONLY_TO_RAW_REQUIREMENT`
