# D08 EXTERNAL LOWER-BOUND TRANSPORT CONTRACT

**Status:** FROZEN CONTRACT — SOURCE SEARCH NOT YET AUTHORIZED  
**Authority:** Blue Team / Mission Control  
**Purpose:** define ex ante when external evidence may supply an authority-bearing lower bound for `N_eff_required_floor`.

Source search remains blocked until the D08 delta gate and the D09 MEUE mapping dependency are resolved.

## 1. Core distinction

Every admitted source contains two separate claims.

### `SOURCE_MEASUREMENT`

What the external source measured or reported.

### `TRANSPORT_ASSUMPTION`

Quant's governance assumption that the external quantity validly lower-bounds the target floor object.

The second is not proven merely because literature reports the first.

**Invariant:** `TRANSPORT_ASSUMPTION_IS_NOT_SOURCE_MEASUREMENT`

## 2. Required direction

For variance transport:

`V_external_floor <= V_target`.

For direct required-sample transport:

`N_required_external_floor <= N_required_target`.

The transport direction must make a false early impossibility verdict harder, never easier.

**Invariant:** `TRANSPORT_DIRECTION_PROTECTS_AGAINST_FALSE_IMPOSSIBILITY`

## 3. Admission before values

A source is admitted using non-numerical pre-frozen properties only, including where relevant:

- population class
- return/outcome definition
- horizon
- benchmark treatment
- study design
- provenance
- measurement construction

Numerical variance/power/required-N values may be used only after admission.

**Invariant:** `SOURCE_ADMISSION_PRECEDES_SOURCE_VALUES`

## 4. Floor-transform compatibility

A source must measure the frozen floor transform directly or an object connected to it by a lower-bound-preserving mapping frozen before source values are inspected.

Otherwise:

`SOURCE_INADMISSIBLE_FOR_POWER_FLOOR`.

## 5. Population transport

The contract requires directional dominance, not vague comparability.

An admitted external population must belong to a predeclared class for which Quant explicitly adopts the governance assumption that its relevant uncertainty / required-sample object lies at or below the target population's.

This assumption must remain labelled as governance, not later rewritten as an empirical theorem.

## 6. Horizon rule

Direct evidence at the frozen 20-regular-session horizon is preferred.

No horizon scaling is authorized without a pre-frozen lower-bound proof:

`Var(20-session object) >= f(external-horizon measurement)`.

The function `f` and the assumptions supporting the inequality must be frozen before candidate scaled-source values are inspected.

In particular, `20 x Var(1d)` is not automatically a valid lower bound because negative autocovariance can reduce cumulative variance.

A looser function may be used if defensible; its cost is reduced early-rejection power.

**Invariants**

- `NO_HORIZON_SCALING_WITHOUT_PRE_FROZEN_LOWER_BOUND_PROOF`
- `NO_HORIZON_RULE_AFTER_NUMERICAL_SOURCE_INSPECTION`

## 7. Direct-power route

A source may directly supply a lower bound such as:

`N_required_external(effect_T, alpha, target_power)`.

It is authority-bearing only when:

- the floor transform is admissible;
- MEUE conversion is frozen;
- alpha and target power are compatible or conservatively transformed by a pre-frozen rule;
- population transport passes;
- horizon transport passes;
- the source's inference construction validly serves as a lower bound.

Otherwise it is a prior, not floor authority.

## 8. Variance-plus-dependence route

If no direct-power source is admitted, a construction may instead combine:

- marginal variance floor;
- dependence favorability floor.

For example:

`kappa = V_aggregate / D_diagonal`

with:

`kappa >= kappa_floor`.

PSD alone is insufficient to establish `kappa_floor > 0`.

A positive dependence floor requires an explicit economic or empirical restriction independent of Form 4 outcomes.

**Invariant:** `POSITIVE_DEPENDENCE_FLOOR_REQUIRES_ECONOMIC_OR_EMPIRICAL_RESTRICTION`

## 9. Every independently admissible source enters

Each source passing the frozen contract is normalized to a lower bound on required effective sample:

`L_s`.

Then:

`N_eff_required_floor_external = min_s L_s`.

The minimum is deliberate protection against a false `POWER_IMPOSSIBLE` verdict: a lower floor makes the inequality required for early rejection harder to satisfy.

This is the same one-sided logic as:

`UNKNOWN_AVAILABILITY_IS_FAVORABLE_FOR_REJECTION_BOUND`.

No post-value quality ranking may be introduced to remove an inconvenient low-floor admitted source.

**Invariants**

- `ALL_ADMISSIBLE_SOURCES_ENTER`
- `MIN_EXTERNAL_FLOOR_PROTECTS_AGAINST_FALSE_IMPOSSIBILITY`
- `EXTERNAL_FLOOR_ARGMIN_IS_EMBARGOED`

## 10. Source authority package

Every admitted source must bind:

- immutable source identity/version/date
- artifact hash
- bibliographic/provenance metadata
- admission-rule result
- `TRANSPORT_ASSUMPTION_ID`
- measured quantity
- extraction rule
- transformation rule
- normalized `L_s`
- independent review/certification evidence

## 11. Failed source search

If no source passes:

`NO_ADMISSIBLE_EXTERNAL_FLOOR_SOURCE`.

The transport contract is not relaxed because search failed.

Allowed consequences are:

- pursue another already pre-frozen floor route;
- freeze a new horizon-scaling rule before numerical inspection in a new lineage;
- retain `POWER_REQUIREMENT_UNRESOLVED_SOURCE`.

**Invariant:** `FAILED_SOURCE_SEARCH_DOES_NOT_RELAX_TRANSPORT_CONTRACT`

## 12. Anti-rescue

After external numerical values/search outcomes have been inspected, the current lineage may not:

- broaden population classes;
- change floor transform;
- change MEUE mapping;
- weaken horizon requirements;
- add a favorable scaling rule;
- remove an admitted low-floor source;
- change alpha/target power.

Material changes require a new scientific lineage.

## 13. D05 interface

D05 consumes only:

- an authority-bearing `N_eff_required_floor`; or
- a cause-preserving unresolved state.

D05 does not source-shop or inspect transform/source argmins.

**Invariant:** `D05_CONSUMES_FLOOR_D05_DOES_NOT_SOURCE_SHOP`
