# D05-A / D09 DIRECT FULL-SUPPORT / SINGLE ROBUST UCB SIMPLIFICATION AMENDMENT — 2026-09-18

**Status:** CLOSED / FROZEN STRUCTURAL SIMPLIFICATION — EXACT RESAMPLING / BLOCK-LENGTH RULE STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D05A_D09_PHASE_COMPLETE_ENSEMBLE_AND_PERSISTENCE_MATERIALITY_AMENDMENT_2026-09-18.md`, `D05A_D09_NONOVERLAP_THINNING_COMMON_CALIBRATION_TARGET_CONTRACT_2026-09-18.md`, `D05A_D09_WINDOW_SPECIFIC_CALENDAR_SERIAL_DEPENDENCE_CONTRACT_2026-09-17.md`, `D05A_D09_BETA_AUTHORITY_WINDOW_MULTIPLICITY_AND_DEPENDENCE_CAPACITY_AMENDMENT_2026-09-17.md`

This amendment simplifies the active liquidity-breach inference path after proving that a phase-complete non-overlap decomposition reproduces the original full-support point estimator while retaining cross-phase overlap covariance. It retires thinning/phase decomposition and persistence-diagnostic method branching from the active authority path and freezes one robust joint-UCB method class to be instantiated prospectively.

No candidate-window breach results, available-capacity counts, Form-4 target values, D05 ceilings, outcomes, provider values or numerical risk tolerances are consumed by this amendment.

## 1. Phase-complete thinning has no active inferential advantage

The prior phase-complete construction proved:

`B_hat_W^PC(x) = sum_{i,t} a_{i,t} I_{i,t}(W,x)`.

This is exactly the original common-target full-support weighted breach estimator.

At the same time, different phases retain non-zero covariance because their rolling windows reuse raw sessions.

Therefore phase decomposition:
- does not increase the information in the point estimator;
- does not remove the mechanical-overlap burden from the final uncertainty calculation;
- introduces phase bookkeeping without reducing the required joint covariance problem.

The current lineage therefore retires phase/thinning decomposition as an active authority mechanism.

Historical phase/thinning artifacts remain as governance evidence documenting the attempted simplification and its exact failure mode.

**Invariants**
- `PHASE_COMPLETE_DECOMPOSITION_IS_RETIRED_FROM_ACTIVE_AUTHORITY_PATH`
- `DIRECT_FULL_SUPPORT_ESTIMATOR_IS_THE_ACTIVE_BREACH_ESTIMATOR`
- `FAILED_SIMPLIFICATION_IS_RETAINED_AS_GOVERNANCE_EVIDENCE_NOT_RUNTIME_COMPLEXITY`

## 2. Active breach estimator returns to the direct common-target form

For every candidate W and lambda endpoint x:

`I_i,t(W,x) = 1{ L_bar_x(E_i,t(W)) > EPSILON_ADV_BAR }`.

Under the frozen common calibration target weights `a_{i,t}`, with total mass 1:

`B_hat_W(x) = sum_{i,t} a_{i,t} I_i,t(W,x)`.

All W use the same pre-frozen common calibration support and target measure.

No phase variable enters the scientific claim fingerprint or production implementation unless a future separately authorized consumer needs it.

**Invariants**
- `BREACH_POINT_ESTIMATOR_IS_DIRECT_COMMON_TARGET_WEIGHTED_FREQUENCY`
- `NO_PHASE_OBJECT_IS_REQUIRED_FOR_WINDOW_SELECTION`
- `ALL_WINDOWS_RETAIN_COMMON_SUPPORT_AND_COMMON_TARGET_MEASURE`

## 3. Mechanical overlap is handled only in inference

For W, one breach observation depends on:

`INFLUENCE_SPAN(W,t) = [t-W+1, ..., t, t+1]`.

The resulting rolling-window overlap remains part of the time-series dependence structure of `B_hat_W(x)`.

The active protocol does not claim to eliminate this dependence through date thinning.

Instead the single joint-UCB method must account for:
- deterministic rolling-window overlap;
- security-level serial liquidity persistence;
- common market/session liquidity shocks;
- market-regime persistence;
- corporate-reorganization dependence.

**Invariants**
- `ROLLING_OVERLAP_IS_AN_INFERENCE_DEPENDENCE_NOT_A_THINNING_PROBLEM`
- `ACTIVE_PROTOCOL_DOES_NOT_CLAIM_DESIGN_BASED_OVERLAP_REMOVAL`

## 4. Persistence diagnostic is retired from method selection

The previously authorized `D_PERSIST = H_MARKET_RESIDUAL/(W_MAX+1)` concept may remain an optional descriptive diagnostic or implementation telemetry if a future Builder finds it useful.

It is no longer on the authority-bearing critical path and may not select between multiple UCB methods.

Reasons:
- the ratio may naturally lie near 1 for plausible candidate-window horizons and liquidity-regime persistence;
- a branching protocol requires two valid UCB implementations, a pre-frozen branch threshold, an intermediate-case rule and additional governance;
- method selection based on an external diagnostic adds complexity without changing the scientific estimand;
- a single robust method valid across the intended dependence regimes avoids this model-selection layer.

Current state:

`PERSISTENCE_MATERIALITY_DIAGNOSTIC = OPTIONAL_DESCRIPTIVE_ONLY`.

**Invariants**
- `D_PERSIST_DOES_NOT_SELECT_AUTHORITY_METHOD`
- `NO_DIAGNOSTIC_BRANCHING_IN_ACTIVE_BREACH_UCB_PATH`

## 5. One robust joint-UCB method class controls the complete family

The active method class is one synchronized dependence-preserving inference procedure applied jointly to the full vector:

`V_t = { contributions to B_hat_W(x) : W in W_SET, x in {0,1} }`.

The implementation must preserve all relevant dependence dimensions in one authority chain:

`CALENDAR_SERIAL x CORPORATE_DEPENDENCE`.

Required structural properties:
- contiguous calendar/session dependence is preserved through a pre-frozen block/bandwidth construction that covers rolling overlap and residual persistence;
- the same calendar resampling/randomization draw is applied to the full 2K family;
- corporate-linked lineages remain grouped through the frozen `CALIBRATION_DEPENDENCE_GROUP_ID` structure or an independently justified equivalent;
- each W retains its own statistic and UCB response even though calendar draws are shared;
- the procedure outputs simultaneous one-sided upper bounds over all 2K statistics.

This freezes a single method **class**, not yet a particular bootstrap theorem or numerical block-length rule.

**Invariants**
- `ONE_JOINT_UCB_METHOD_CLASS_FOR_FULL_2K_FAMILY`
- `COMMON_CALENDAR_DRAWS_PRESERVE_CROSS_WINDOW_COVARIANCE`
- `CORPORATE_DEPENDENCE_REMAINS_IN_SAME_AUTHORITY_CHAIN`
- `UCB_REMAINS_W_SPECIFIC_WITHIN_ONE_SHARED_METHOD`

## 6. Simultaneous max-statistic authority is preferred over Bonferroni when valid

Because all 2K statistics are computed on the same market history and are strongly dependent, a synchronized resampling construction can preserve their covariance.

The preferred simultaneous one-sided construction, if supported by the final resampling theorem, is a joint maximum-statistic critical value rather than treating all 2K coordinates as independent tests.

Conceptually, for replicate b let the centered/scaled error vector be `Z_b(W,x)` and define:

`M_b = max_{W,x} Z_b(W,x)`.

A frozen upper quantile of the `M_b` distribution supplies one familywise critical value used to form all one-sided `UCB_W(x)`.

This may be less conservative than Bonferroni while preserving the same familywise error target because the common resampling draw retains actual cross-window/end-point covariance.

Bonferroni remains a valid fallback only if separately pre-frozen before results; it may not be selected after seeing which method yields more passing windows.

**Invariants**
- `SIMULTANEOUS_MAX_STATISTIC_IS_PREFERRED_WHEN_THEOREM_SUPPORTS_IT`
- `CROSS_WINDOW_COVARIANCE_MAY_REDUCE_CONSERVATISM_WITHOUT_RELAXING_ALPHA`
- `UCB_METHOD_CANNOT_BE_CHOSEN_BY_PASS_RESULT`

## 7. Block/bandwidth selection is a nuisance rule inside the single method, not a method branch

A robust calendar-block or bandwidth method still needs an exact dependence-length rule.

That rule may be empirically instantiated on the external calibration corpus only if its estimator is frozen before its value is observed.

The block/bandwidth rule must account for the complete 2K vector and cannot be tuned independently per W to improve pass rates.

A permitted structural direction is:
- compute a pre-frozen dependence-length diagnostic for every required component/process;
- aggregate those diagnostics by a pre-frozen conservative family rule, such as a maximum or proven majorant;
- instantiate one calendar block/bandwidth rule for the synchronized 2K resampling.

The exact diagnostic, aggregation rule and theorem remain open.

If the final method genuinely requires W-specific block lengths, they must be deterministic outputs of one common pre-frozen rule and remain coupled through one shared-calendar resampling construction.

**Invariants**
- `DEPENDENCE_LENGTH_IS_NUISANCE_CALIBRATION_NOT_METHOD_SELECTION`
- `BLOCK_LENGTH_RULE_PRECEDES_ITS_EMPIRICAL_VALUE`
- `NO_W_SPECIFIC_BLOCK_SHOPPING`
- `SINGLE_METHOD_DOES_NOT_REQUIRE_SINGLE_NUMERICAL_UCB_ACROSS_W`

## 8. Comparison: single robust method dominates diagnostic branching procedurally

The current lineage chooses the single-method architecture because diagnostic branching would add:
- an additional measured object;
- a branch threshold and intermediate-case policy;
- two separately validated UCB implementations;
- additional version/fingerprint state;
- additional pathways for post-result method selection.

Its possible benefit is lower conservatism in some persistence regimes.

The single-method architecture instead pays conservatism directly in required calibration capacity, which is visible and auditable.

If that conservatism later causes:

`LIQUIDITY_BREACH_CALIBRATION_UNDERPOWERED`,

the protocol may prospectively broaden an independently defined external corpus or create a new method version before results. It may not retrospectively introduce diagnostic branching to rescue the same lineage.

**Invariants**
- `VISIBLE_CAPACITY_COST_IS_PREFERRED_TO_ADAPTIVE_METHOD_COMPLEXITY`
- `UNDERPOWERED_SINGLE_METHOD_DOES_NOT_AUTHORIZE_POST_HOC_BRANCHING`

## 9. Window-specific uncertainty remains despite one common method

Retiring phase decomposition does not restore one common effective sample size.

Rolling overlap grows with W and the same market shock can affect each W differently.

Therefore:
- point estimand/support/weights are common;
- inference method class and calendar draws are common;
- uncertainty/UCB outputs remain W-specific.

If any frozen candidate cannot meet the predeclared precision requirement under the single joint method:

`LIQUIDITY_BREACH_CALIBRATION_UNDERPOWERED`.

The candidate may not be removed after this state is observed.

## 10. Revised immediate critical path

Before any numerical breach/window result:

`freeze W_SET / W_MAX / common calibration support and target weights`

`-> freeze P_MAX_REF / P_TARGET_REF / BETA_LIQ_MAX / TAU_BETA / ALPHA_BETA under their existing authority types`

`-> derive EPSILON_ADV_BAR`

`-> freeze exact single synchronized calendar x corporate resampling/UCB theorem`

`-> freeze its one dependence-length / block-bandwidth selection rule for the full 2K family`

`-> derive pre-result precision/capacity requirement`

`-> only then inspect available external capacity`

`-> if underpowered: LIQUIDITY_BREACH_CALIBRATION_UNDERPOWERED`

`-> if sufficient: compute simultaneous one-sided UCB_W(x)`

`-> apply shortest-passing endpoint rule and lambda materiality discharge`.

No thinning, phase selection or D_PERSIST method branch remains in the active path.

## 11. Current state

Closed/frozen:
- active point estimator = direct common-target full-support breach frequency;
- phase/thinning decomposition retired from active authority path;
- D_PERSIST retired from method selection;
- mechanical overlap remains an inference dependence;
- one synchronized calendar x corporate UCB method class controls the whole 2K family;
- max-statistic simultaneous one-sided authority is preferred if supported by the final theorem;
- block/bandwidth calibration is a nuisance rule inside that single method, not a method branch;
- W-specific uncertainty and all-window capacity requirement remain.

Still open:
- exact W_SET / W_MAX;
- exact synchronized calendar x corporate bootstrap/resampling/concentration theorem;
- exact block/bandwidth/dependence-length selector;
- exact max-statistic studentization / centering / critical-value construction;
- numerical P_MAX_REF, P_TARGET_REF, BETA_LIQ_MAX, TAU_BETA, ALPHA_BETA;
- source/provider / daily-notional / calibration-domain / missingness implementation;
- final external capacity.

Current state:

`ACTIVE_BREACH_ESTIMATOR = DIRECT_FULL_SUPPORT_WEIGHTED_FREQUENCY`

`ACTIVE_UCB_ARCHITECTURE = SINGLE_SYNCHRONIZED_CALENDAR_X_CORPORATE_METHOD_CLASS`

`PHASE_THINNING_AUTHORITY = RETIRED_CURRENT_LINEAGE`

`D_PERSIST_METHOD_BRANCHING = RETIRED_CURRENT_LINEAGE`.

Route-B firewall remains unsatisfied. No numerical breach calibration, D05 ceiling visibility or Form-4 outcome access is authorized.
