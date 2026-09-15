# D08 POWER-FLOOR OUTCOME TRANSFORM BOUNDARY

**Status:** FREEZE CANDIDATE — `DELTA_COORDINATE_COMPATIBILITY_GATE` OPEN  
**Authority:** Blue Team / Mission Control  
**Purpose:** bound the outcome transform space used only to construct a one-sided lower bound on required effective sample before final D08 inference is frozen.

## 1. Scope

This artifact does not choose the final D08 estimator, dependence treatment or confirmatory test.

It defines only the transform space allowed to support:

`N_eff_required(final science) >= N_eff_required_floor`.

The floor can support early impossibility only. It cannot authorize positive sufficiency.

## 2. Transform admission law

A floor transform is admissible only if:

1. it preserves the frozen economic comparison against SPY;
2. it uses the frozen 20-regular-session holding horizon;
3. there is a unique ex-ante `MEUE -> effect_T` mapping;
4. that mapping is outcome-blind;
5. defining the transform does not introduce arbitrary estimator/calibration choices merely to reduce variance.

**Invariants**

- `UNIQUE_EX_ANTE_MEUE_TO_FLOOR_EFFECT_MAPPING`
- `LOWER_VARIANCE_DOES_NOT_AUTHORIZE_ESTIMAND_CHANGE`
- `TRANSFORM_ADMISSION_PRECEDES_POWER_VALUES`

## 3. Current candidate set

Subject to the open delta-coordinate gate, the current candidate set is a singleton:

`G_T_FLOOR = {T_SPY_SIMPLE_EXCESS_20}`

with:

`T_SPY_SIMPLE_EXCESS_20 = R_security_20 - R_SPY_20`.

The security and SPY use the same frozen economic interval and compatible return/corporate-action conventions.

## 4. Rejected transforms in the current lineage

### Market-model abnormal return

Rejected because it requires additional design choices such as beta-estimation window, estimator, intercept handling, history sufficiency and missing-history treatment.

`FLOOR_TRANSFORM_INADMISSIBLE_EXTRA_DESIGN_DEGREES`.

### Sum of daily market-adjusted returns

Rejected because additive daily excess returns are not generally identical to the simple 20-session wealth difference under compounding; unique MEUE mapping would require path assumptions.

`FLOOR_TRANSFORM_INADMISSIBLE_NONUNIQUE_MEUE_MAPPING`.

### Log relative return

Rejected because mapping from a simple wealth-difference MEUE to the log-relative coordinate is not unique without an additional benchmark-return-level convention.

`FLOOR_TRANSFORM_INADMISSIBLE_NONUNIQUE_MEUE_MAPPING`.

### Raw security return

Rejected because it omits the frozen SPY scientific benchmark.

`FLOOR_TRANSFORM_INADMISSIBLE_BENCHMARK_MISMATCH`.

### Multifactor residualized return

Rejected because it introduces additional design degrees not implied by the frozen economic claim.

## 5. Delta-coordinate compatibility gate

The singleton is not yet authority-bearing.

D09 must resolve the canonical meaning of `delta` in:

`V_annual = Phi(delta, C, G, execution)`.

If `delta` is not on the same economic coordinate as `T_SPY_SIMPLE_EXCESS_20`, the boundary does **not** redefine delta to make the singleton fit.

Instead:

`DELTA_COORDINATE_MISMATCH`

forces a return to this boundary using the true D09 coordinate and a new admission test.

**Invariant:** `DELTA_MISMATCH_INVALIDATES_FLOOR_TRANSFORM_ASSUMPTION`

## 6. Singleton consequence

If the delta gate passes:

`|G_T_FLOOR| = 1`.

There is no transform optimization channel in this lineage and no active transform argmin to reveal.

**Invariant:** `SINGLETON_FLOOR_TRANSFORM_HAS_NO_DESIGN_SELECTION_CHANNEL`

## 7. Transform admission vs floor instantiation

Define:

`G_T_INSTANTIATED`

as the subset of admitted transforms for which at least one external source passes the frozen external lower-bound transport contract.

A transform may be scientifically admissible yet have no admissible external floor source.

**Invariant:** `TRANSFORM_ADMISSION_AND_FLOOR_INSTANTIATION_ARE_SEPARATE`

In a generic multi-transform lineage:

`N_eff_required_floor = min_{T in G_T_INSTANTIATED} N_floor(T)`.

A transform with no admissible source is absent from this aggregation; its absence does not invalidate floors from other already-admitted transforms.

In the current singleton lineage, either the singleton is instantiated or no external floor is available.

## 8. Distinct unresolved causes

### Object-definition failure

If no valid transform/MEUE mapping exists:

`POWER_FLOOR_OBJECT_UNDEFINED`
→ `POWER_REQUIREMENT_UNRESOLVED_OBJECT`.

### External-authority failure

If the floor object is defined but no source passes the frozen transport contract:

`NO_ADMISSIBLE_EXTERNAL_FLOOR_SOURCE`
→ `POWER_REQUIREMENT_UNRESOLVED_SOURCE`.

Both roll up to:

`POWER_REQUIREMENT_UNRESOLVED`.

The child cause must be preserved.

**Invariant:** `POWER_UNRESOLVED_CAUSE_MUST_BE_PRESERVED`

## 9. No source-failure transform rescue

Failed source search may not expand the transform set after source values/search outcomes are known.

**Invariant:** `SOURCE_FAILURE_DOES_NOT_EXPAND_TRANSFORM_SPACE`

## 10. Relation to final D08

Final D08 may use a different estimator/transform only if prior impossibility authority remains valid under an independent proof:

`N_required(final_D08) >= N_eff_required_floor`.

Otherwise the earlier power-impossibility verdict cannot be carried into that new inference lineage.

**Invariant:** `FINAL_D08_CANNOT_UNDERCUT_PRIOR_POWER_FLOOR_WITHOUT_INVALIDATION`

## 11. Status gate

This artifact remains `FREEZE_CANDIDATE`, not a hash-addressable scientific authority for the floor, until D09 resolves:

- `DELTA_COORDINATE_COMPATIBILITY_GATE`;
- unique `MEUE -> effect_T` mapping.
