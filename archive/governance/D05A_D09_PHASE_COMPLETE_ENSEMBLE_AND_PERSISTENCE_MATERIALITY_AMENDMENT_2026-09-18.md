# D05-A / D09 PHASE-COMPLETE ENSEMBLE / RESIDUAL-PERSISTENCE MATERIALITY AMENDMENT — 2026-09-18

**Status:** CLOSED / FROZEN STRUCTURAL AMENDMENT — EXACT RESIDUAL-PERSISTENCE DIAGNOSTIC / JOINT UCB METHOD STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D05A_D09_NONOVERLAP_THINNING_COMMON_CALIBRATION_TARGET_CONTRACT_2026-09-18.md`, `D05A_D09_WINDOW_SPECIFIC_CALENDAR_SERIAL_DEPENDENCE_CONTRACT_2026-09-17.md`, `D05A_D09_BETA_AUTHORITY_WINDOW_MULTIPLICITY_AND_DEPENDENCE_CAPACITY_AMENDMENT_2026-09-17.md`

This amendment removes thinning phase as a discretionary object by using every non-overlap phase deterministically. It also distinguishes a cheap residual-persistence materiality diagnostic from the final authority-bearing dependence/UCB construction.

No candidate-window breach results, available-capacity counts, Form-4 target values, D05 ceilings or outcomes are consumed by this amendment.

## 1. All non-overlap phases are used; none is selected

For candidate lookback W define:

`m(W) = W + 1`.

Index every regular market session by one frozen global exchange-session ordinal `s(t)`.

Define the phase of an eligible calibration anchor t by:

`PHASE_W(t) = s(t) mod m(W)`.

There are exactly `m(W)` phase classes:

`p in {0,...,W}`.

Within one phase, consecutive anchors are separated by at least W+1 regular sessions, so their raw influence intervals do not overlap mechanically.

Every common-support anchor belongs to exactly one phase and **all phases are retained**.

No phase is chosen, optimized, seeded, screened or dropped.

Because all residue classes are included, changing the arbitrary origin of the session ordinal only relabels phase identifiers; it does not change the partition or the final phase-complete estimator.

**Invariants**
- `ALL_NONOVERLAP_PHASES_ARE_USED`
- `PHASE_IS_NOT_A_SELECTED_HYPERPARAMETER`
- `GLOBAL_SESSION_MODULO_DEFINES_PHASE_PARTITION`
- `PHASE_ORIGIN_ONLY_RELABELS_WHEN_ALL_PHASES_ARE_INCLUDED`

## 2. Phase-complete estimator exactly targets the common calibration measure

Let the already-frozen common target measure assign normalized target weight `a_{i,t}` to eligible security-date calibration observations, with total mass 1 under the existing equal-security semantics.

For W and phase p define phase target mass:

`Omega_{W,p} = sum_{(i,t): PHASE_W(t)=p} a_{i,t}`.

For endpoint x define the phase-specific breach estimator using the inherited target weights normalized within phase:

`B_hat_{W,p}(x) = [sum_{(i,t) in p} a_{i,t} I_{i,t}(W,x)] / Omega_{W,p}`

when `Omega_{W,p} > 0`.

Define the phase-complete ensemble:

`B_hat_W^PC(x) = sum_p Omega_{W,p} * B_hat_{W,p}(x)`.

Algebraically:

`B_hat_W^PC(x) = sum_{i,t} a_{i,t} I_{i,t}(W,x)`.

Thus the ensemble is exactly the common-target weighted full-support breach estimator. It does not introduce a W-specific calendar estimand and it uses every eligible anchor once.

An empty required phase under the frozen support/weighting convention is a design failure requiring an explicit rule; it may not be silently renormalized after results if doing so changes the target measure.

**Invariants**
- `PHASE_COMPLETE_ESTIMATOR_EQUALS_COMMON_TARGET_FULL_SUPPORT_ESTIMATOR`
- `PHASE_ENSEMBLE_DOES_NOT_CHANGE_CALIBRATION_ESTIMAND`
- `ALL_ELIGIBLE_COMMON_SUPPORT_ANCHORS_ARE_USED_ONCE_IN_POINT_ESTIMATE`

## 3. Critical correction: phase completeness removes phase discretion, not total mechanical dependence

Each phase sequence is internally free of deterministic raw-window overlap.

However different phases reuse many of the same raw sessions. Therefore:

`Cov(B_hat_{W,p}, B_hat_{W,p'}) != 0`

in general for `p != p'`.

The variance/UCB of:

`B_hat_W^PC`

must account for the full covariance matrix across phases, together with residual calendar/regime and corporate dependence.

It is forbidden to treat the W+1 phase estimators as independent replicates.

Accordingly, the previous shorthand:

`MECHANICAL_OVERLAP_HANDLING = W_SPECIFIC_THINNING`

is superseded by the more precise state:

`MECHANICAL_OVERLAP_HANDLING = PHASE_COMPLETE_NONOVERLAP_DECOMPOSITION_WITH_JOINT_COVARIANCE`.

Mechanical overlap has been reorganized into an explicit phase covariance geometry; it has not disappeared from the final estimator.

**Invariants**
- `NONOVERLAP_WITHIN_PHASE_DOES_NOT_IMPLY_INDEPENDENCE_ACROSS_PHASES`
- `PHASE_ENSEMBLE_UCB_INCLUDES_INTERPHASE_COVARIANCE`
- `PHASE_AVERAGING_DOES_NOT_CLAIM_ZERO_MECHANICAL_DEPENDENCE`

## 4. Information cost of long W remains visible, but not as a reduced total point-estimate count

Because every phase is included, the phase-complete point estimator uses the same common-support anchor universe for every W.

Therefore the earlier statement that a longer W necessarily has fewer **total** point-estimate anchors under the preferred design is superseded.

The actual long-W information cost appears through:
- fewer anchors inside each non-overlap phase, approximately scaling with `1/(W+1)`;
- a larger phase dimension `W+1`;
- stronger / more extended covariance geometry among phase estimators due to overlapping raw windows;
- any additional W-specific sensitivity to persistent liquidity regimes.

Required reporting for each W therefore includes:
- total common-support anchor mass/count;
- number of phases `W+1`;
- phase masses `Omega_{W,p}`;
- anchors per phase;
- interphase / residual dependence diagnostics required by the final UCB;
- final W-specific precision state.

**Invariants**
- `PHASE_COMPLETE_POINT_ESTIMATE_USES_FULL_COMMON_SUPPORT`
- `LONG_W_INFORMATION_COST_APPEARS_IN_PHASE_GEOMETRY_AND_COVARIANCE`
- `TOTAL_ANCHOR_COUNT_ALONE_DOES_NOT_MEASURE_LONG_W_INFORMATION`

## 5. Common calendar shocks are common in source, not necessarily equal in effect across W

Market-wide liquidity shocks and regimes are shared calendar phenomena, so final resampling/randomization must remain coupled across all windows.

But the induced breach process can respond differently to the same regime for different W.

Therefore this amendment does not claim that residual dependence becomes numerically identical across windows after phase decomposition.

The correct statement is:

`COMMON_CALENDAR_DEPENDENCE_AXIS = SHARED`

while:

`RESIDUAL_RESPONSE_AND_UCB = W_SPECIFIC`.

**Invariants**
- `COMMON_MARKET_SHOCK_SOURCE_DOES_NOT_IMPLY_COMMON_W_DEPENDENCE_MAGNITUDE`
- `UCB_REMAINS_W_SPECIFIC_UNDER_SHARED_CALENDAR_RESAMPLING`

## 6. Residual-persistence materiality diagnostic before expensive UCB engineering

Before committing to a more elaborate authority-bearing UCB implementation, the lineage may run a cheap non-target diagnostic on the external calibration corpus to learn whether persistent market-liquidity regimes are likely to dominate the structural W scale.

The diagnostic must be frozen before its numerical output and must use a W-independent market/liquidity-state object, not Form-4 outcomes and not a window chosen because of its breach result.

Define under a future frozen rule:

`H_MARKET_RESIDUAL`

= a common-market/session persistence horizon measured from the authorized external liquidity-state process.

After W_SET is frozen, define the structural comparison scale:

`H_STRUCT_MAX = W_MAX + 1`.

Report the diagnostic ratio:

`D_PERSIST = H_MARKET_RESIDUAL / H_STRUCT_MAX`.

Interpretation is diagnostic only:
- `D_PERSIST >> 1`: common regime persistence is longer than the largest structural rolling span; calendar/regime dependence is likely to dominate engineering and capacity considerations;
- `D_PERSIST << 1`: structural rolling geometry remains comparatively important and phase decomposition is likely to remove a larger share of the serial-dependence burden;
- intermediate values require no qualitative simplification.

No numerical threshold for ">>" or "<<" is authorized by this artifact.

**Invariants**
- `PERSISTENCE_DOMINANCE_DIAGNOSTIC_IS_W_INDEPENDENT_IN_INPUT`
- `PERSISTENCE_DIAGNOSTIC_PRECEDES_EXPENSIVE_UCB_ENGINEERING`
- `D_PERSIST_IS_DIAGNOSTIC_NOT_PASS_FAIL_AUTHORITY`

## 7. The diagnostic may guide engineering priority but cannot weaken authority

The North-Star-consistent purpose of `D_PERSIST` is computational triage: wide/cheap information before narrow/deep statistical engineering.

It may guide whether implementation effort should prioritize:
- a conservative synchronized calendar-block UCB first; or
- a more refined covariance-efficient simultaneous construction.

It may not:
- change `BETA_LIQ_MAX`, `TAU_BETA` or `ALPHA_BETA`;
- delete candidate windows;
- shorten a required block horizon;
- declare capacity sufficient;
- certify a W;
- replace the final joint-dependence UCB.

Any branch from the diagnostic to a different authority method must itself be frozen as a decision rule before the diagnostic value is inspected. Otherwise the diagnostic is descriptive only.

**Invariants**
- `CHEAP_PERSISTENCE_DIAGNOSTIC_CAN_PRIORITIZE_ENGINEERING_NOT_RELAX_SCIENCE`
- `METHOD_BRANCHING_FROM_DIAGNOSTIC_REQUIRES_PRE_FROZEN_RULE`
- `DIAGNOSTIC_DOES_NOT_AUTHORIZE_WINDOW_PASS`

## 8. Simultaneous UCB must operate on the phase-complete functional

The authority-bearing family remains:

`(W,x) in W_SET x {0,1}`.

For every bootstrap/resampling/randomization replicate, the implementation must:
1. apply one coupled calendar/market-state draw across the full W family;
2. preserve the corporate-dependence grouping required by the frozen contract;
3. recompute or validly transport every phase-specific contribution under that draw;
4. aggregate all phases with the frozen `Omega_{W,p}` rule;
5. produce the replicate phase-complete breach estimator for each `(W,x)`;
6. construct one-sided simultaneous UCBs over the full 2K family.

A bootstrap that treats phases as independent or resamples phases separately is not authorized.

## 9. Revised open objects

Closed/frozen:
- all W+1 non-overlap phases are used;
- phase selection / seed shopping is retired;
- phase-complete estimator equals the common-target full-support estimator;
- phase decomposition does not eliminate cross-phase mechanical covariance;
- long-W information cost is represented through phase/covariance geometry rather than reduced total point-estimate count;
- common market dependence axis is shared but its effect remains W-specific;
- a cheap W-independent residual-persistence materiality diagnostic is authorized in structure only;
- the diagnostic cannot itself alter scientific thresholds or certify W.

Still open:
- exact W_SET / W_MAX;
- exact external common-market liquidity-state object for `H_MARKET_RESIDUAL`;
- exact persistence statistic / cutoff / horizon functional;
- any pre-frozen diagnostic-to-method branching threshold/rule;
- exact synchronized calendar x corporate phase-complete UCB;
- numerical P_MAX_REF, P_TARGET_REF, BETA_LIQ_MAX, TAU_BETA, ALPHA_BETA;
- source/provider, calibration domain, missingness/date support and daily-notional implementation.

Current state:

`PHASE_HANDLING = CLOSED / PHASE_COMPLETE_ENSEMBLE`

`PERSISTENCE_MATERIALITY_DIAGNOSTIC = STRUCTURALLY_AUTHORIZED / NUMERICAL_RULE_OPEN`

`RESIDUAL_JOINT_DEPENDENCE_METHOD = OPEN / NOT YET CONSUMABLE`.

No numerical breach calibration, D05 ceiling visibility or Form-4 outcome access is authorized by this amendment.
