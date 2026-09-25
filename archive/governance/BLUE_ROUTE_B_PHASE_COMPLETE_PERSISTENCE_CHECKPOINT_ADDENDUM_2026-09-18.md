# BLUE ROUTE-B CHECKPOINT ADDENDUM — PHASE-COMPLETE ENSEMBLE / PERSISTENCE MATERIALITY — 2026-09-18

**Status:** CURRENT CHECKPOINT ADDENDUM  
**Authority:** Blue Team / Mission Control  
**Parents:** `BLUE_ROUTE_B_NONOVERLAP_THINNING_COMMON_TARGET_CHECKPOINT_ADDENDUM_2026-09-18.md`, `D05A_D09_PHASE_COMPLETE_ENSEMBLE_AND_PERSISTENCE_MATERIALITY_AMENDMENT_2026-09-18.md`

This addendum controls where more recent/specific than its parent checkpoint.

## 1. New controlling artifact

Add:

`governance/D05A_D09_PHASE_COMPLETE_ENSEMBLE_AND_PERSISTENCE_MATERIALITY_AMENDMENT_2026-09-18.md`.

## 2. Phase handling supersession

The prior open thinning-phase/seed choice is retired.

For every W:
- partition common-support anchors into all `W+1` modulo-session phases;
- each phase is internally non-overlap;
- retain every phase;
- aggregate phases by their frozen common-target mass.

Current state:

`PHASE_HANDLING = CLOSED / PHASE_COMPLETE_ENSEMBLE`.

There is no phase selection and no phase-shopping multiplicity.

## 3. Point estimate versus uncertainty

The phase-complete point estimator is algebraically the full common-target breach estimator over all common-support anchors.

Therefore:
- all windows use the same common-support anchor universe in the point estimate;
- a longer W does not automatically have fewer **total** point-estimate anchors;
- longer-W information cost appears in per-phase sparsity and interphase/residual covariance.

The previous shorthand that preferred thinning globally "removes mechanical overlap" is superseded.

Current state:

`MECHANICAL_OVERLAP_HANDLING = PHASE_COMPLETE_NONOVERLAP_DECOMPOSITION_WITH_JOINT_COVARIANCE`.

## 4. Residual dependence

All phase estimators must be treated jointly.

Cross-phase mechanical covariance, common calendar/regime dependence, W-specific response to common shocks, and corporate dependence remain authority-bearing.

Common shocks are shared in source; their induced dependence magnitude need not be equal across W.

`UCB_W(x)` remains W-specific.

## 5. Cheap persistence materiality diagnostic

A pre-result, W-independent external-market liquidity-state diagnostic may instantiate:

`H_MARKET_RESIDUAL`.

After W_SET is frozen:

`H_STRUCT_MAX = W_MAX + 1`

and:

`D_PERSIST = H_MARKET_RESIDUAL / H_STRUCT_MAX`.

This is a diagnostic for engineering priority only.

It cannot:
- certify a W;
- change BETA/TAU/ALPHA;
- remove a candidate;
- shorten a dependence horizon;
- declare capacity sufficient.

Any diagnostic-to-method branch requires its own pre-frozen rule before D_PERSIST is observed.

## 6. Simultaneous UCB

Any authority-bearing bootstrap/resampling procedure must:
- use common calendar/market-state draws across the full 2K family;
- preserve corporate grouping;
- preserve/recompute all W+1 phases;
- aggregate phases under the frozen common-target mass rule;
- construct one-sided simultaneous UCBs on the phase-complete functionals.

Independent phase bootstrap is not authorized.

## 7. Revised immediate order

Before numerical breach calibration:

1. freeze W_SET / W_MAX;
2. freeze common calibration target/support;
3. freeze exact W-independent external liquidity-state object and persistence diagnostic rule;
4. optionally instantiate D_PERSIST for engineering triage only;
5. freeze any diagnostic-to-method branch before reading D_PERSIST if branching is desired;
6. freeze synchronized calendar x corporate phase-complete UCB method;
7. freeze numerical P_MAX_REF / P_TARGET_REF / BETA_LIQ_MAX / TAU_BETA / ALPHA_BETA under their authority rules;
8. derive epsilon/precision requirements;
9. only then evaluate capacity and breach statistics.

Route-B firewall remains unsatisfied.
D05 ceiling visibility remains unauthorized.
Form-4 outcome access remains unauthorized.
