# D08 POWER-FLOOR OUTCOME TRANSFORM BOUNDARY

**Status:** SUPERSEDED_FOR_THIS_LINEAGE — HISTORICAL ROUTE-A ARTIFACT — ASTRA-CORRECTED  
**Authority:** Blue Team / Mission Control  
**Purpose:** historical/candidate contract for a one-sided pre-D07 raw-observation power floor. It is not an active dependency of the current Route-B lineage.

## Current-lineage supersession notice — 2026-09-17

`BLUE_POWER_ROUTE_B_DECISION_2026-09-17.md` selected `ROUTE_B_FINAL_PROTOCOL_ONLY` and retired pre-D07 global power-floor authority for the current Form 4 lineage after `RD2_UNIFORM_FLOOR_TRIVIAL`.

Therefore this artifact is scientifically retained but has **no active downstream consumer in the current lineage**.

- `T_SPY_SIMPLE_EXCESS_20` remains useful as the primitive gross scientific outcome concept through D09 EC1.
- The floor-transform admission, floor instantiation, source-coverage and carry-forward-impossibility clauses below are not current-lineage obligations.
- No numerical floor-source work is authorized from this artifact.
- A future new lineage may reactivate these rules only through a new Blue decision with independently justified assumptions and an exposure-safe pre-freeze.

`STATUS_CURRENT_LINEAGE = SUPERSEDED_FOR_THIS_LINEAGE`.

The historical text below is preserved because it remains correct for the Route-A problem it was written to govern.

## 1. Scope

This artifact does not choose the final D08 estimator, dependence treatment or confirmatory test.

It defines only the transform space allowed to support:

`N_raw_required(final science) >= N_RAW_REQUIRED_FLOOR`.

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

No execution-noise term is silently added to this gross market-return transform. If final science instead targets a net executed-return transform, that is a distinct transform requiring its own admission/mapping/covariance treatment.

**Invariant:** `GROSS_MARKET_TRANSFORM_DOES_NOT_SILENTLY_ABSORB_EXECUTION_NOISE`.

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

**Invariant:** `DELTA_MISMATCH_INVALIDATES_FLOOR_TRANSFORM_ASSUMPTION`.

## 6. Singleton consequence

If the delta gate passes:

`|G_T_FLOOR| = 1`.

There is no transform optimization channel in this lineage and no active transform argmin to reveal.

**Invariant:** `SINGLETON_FLOOR_TRANSFORM_HAS_NO_DESIGN_SELECTION_CHANNEL`.

## 7. Transform admission vs floor instantiation

Define:

`G_T_INSTANTIATED`

as the subset of admitted transforms for which an authority-bearing lower bound on raw required sample has been produced under the frozen external lower-bound transport contract or another pre-frozen admissible route.

A transform may be scientifically admissible yet have no admissible external floor source.

**Invariant:** `TRANSFORM_ADMISSION_AND_FLOOR_INSTANTIATION_ARE_SEPARATE`.

### Current singleton lineage

If the delta gate passes, either:

- `T_SPY_SIMPLE_EXCESS_20` is instantiated; or
- `POWER_REQUIREMENT_UNRESOLVED_SOURCE` / another cause-preserving unresolved state remains.

No partial transform aggregation exists because the set is a singleton.

### Generic future multi-transform lineage

A generic future lineage may use:

`N_RAW_REQUIRED_FLOOR = min_T N_raw_floor(T)`

**only when every transform in the authority-covered admissible set is either:**

1. independently instantiated with an authority-bearing lower bound; or
2. covered by an independently frozen/proven dominance relation showing that omitting its separate instantiation cannot make the true minimum lower than the published floor.

An admissible transform with unknown/unbounded required-sample floor may not simply be omitted from the minimum.

Otherwise:

`POWER_REQUIREMENT_UNRESOLVED_TRANSFORM_COVERAGE`.

**Invariants**

- `EVERY_ADMISSIBLE_TRANSFORM_MUST_BE_INSTANTIATED_OR_PROVEN_DOMINATED`
- `UNINSTANTIATED_TRANSFORM_CANNOT_BE_SILENTLY_DROPPED`

## 8. Distinct unresolved causes

### Object-definition failure

If no valid transform/MEUE mapping exists:

`POWER_FLOOR_OBJECT_UNDEFINED`
→ `POWER_REQUIREMENT_UNRESOLVED_OBJECT`.

### External-authority failure

If the floor object is defined but no source/route produces an admissible bound:

`NO_ADMISSIBLE_EXTERNAL_FLOOR_SOURCE`
→ `POWER_REQUIREMENT_UNRESOLVED_SOURCE`.

### Transform-coverage failure

In a future multi-transform authority set, if at least one admissible transform is neither instantiated nor proven dominated:

`POWER_REQUIREMENT_UNRESOLVED_TRANSFORM_COVERAGE`.

All roll up to:

`POWER_REQUIREMENT_UNRESOLVED`.

The child cause must be preserved.

**Invariant:** `POWER_UNRESOLVED_CAUSE_MUST_BE_PRESERVED`.

## 9. No source-failure transform rescue

Failed source search may not expand the transform set after source values/search outcomes are known.

**Invariant:** `SOURCE_FAILURE_DOES_NOT_EXPAND_TRANSFORM_SPACE`.

## 10. Relation to final D08

Final D08 may use a different estimator/transform only if prior impossibility authority remains valid under an independent proof:

`N_raw_required(final_D08) >= N_RAW_REQUIRED_FLOOR`.

Otherwise the earlier power-impossibility verdict cannot be carried into that new inference lineage.

**Invariant:** `FINAL_D08_CANNOT_UNDERCUT_PRIOR_POWER_FLOOR_WITHOUT_INVALIDATION`.

## 11. Historical status gate

Under a Route-A lineage this artifact would remain a `FREEZE_CANDIDATE` until D09 resolved:

- `DELTA_COORDINATE_COMPATIBILITY_GATE`;
- unique `MEUE -> effect_T` mapping;
- the common raw-required-sample power formulation consumed downstream.

For the current Route-B lineage this gate is not active.
