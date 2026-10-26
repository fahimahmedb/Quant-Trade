# BLUE ROUTE-B CHECKPOINT ADDENDUM — NON-OVERLAP THINNING / COMMON CALIBRATION TARGET — 2026-09-18

**Status:** CURRENT CHECKPOINT ADDENDUM  
**Authority:** Blue Team / Mission Control  
**Parents:** `BLUE_ROUTE_B_WINDOW_SPECIFIC_DEPENDENCE_CHECKPOINT_ADDENDUM_2026-09-17.md`, `D05A_D09_NONOVERLAP_THINNING_COMMON_CALIBRATION_TARGET_CONTRACT_2026-09-18.md`

This addendum controls where more recent/specific than its parent checkpoint.

## 1. New controlling artifact

Add:

`governance/D05A_D09_NONOVERLAP_THINNING_COMMON_CALIBRATION_TARGET_CONTRACT_2026-09-18.md`.

## 2. Mechanical overlap handling

Current-lineage preferred handling is:

`MECHANICAL_OVERLAP_HANDLING = W_SPECIFIC_PRE_FROZEN_THINNING`.

For each W:

`minimum anchor spacing = W + 1 regular sessions`.

This removes shared predictor/target sessions by design but does not establish independence.

If thinning is not used in the final implementation, the prior overlap-aware H_SERIAL(W) dependence contract again carries the full burden.

## 3. Common calibration target and support

All candidate windows must estimate the same:

`COMMON_LIQUIDITY_CALIBRATION_TARGET_MEASURE`.

Before W-specific thinning, construct one common support valid for the full candidate family, including the history required by:

`W_MAX = max(W_SET)`.

A shorter window may not gain authority by changing the calibration population or calendar target.

Window-specific anchor subsets require a frozen design/inclusion-weight rule that maps them back to the common target measure.

If that mapping cannot be authorized:

`WINDOW_SPECIFIC_THINNING_AUTHORITY_UNRESOLVED`.

## 4. Residual dependence

After thinning, current authority still requires:

- common-session / market-regime dependence;
- security-level residual persistence;
- corporate-reorganization dependence;
- W-specific UCB/precision.

Residual persistence may be instantiated empirically on the external non-target corpus only under a pre-frozen measurement rule.

`W+1` is no longer treated as a complete serial-dependence horizon.

## 5. Simultaneous inference

The 2K family remains:

`W in W_SET, x in {0,1}`.

If resampling is used, common calendar block/market-state draws must be coupled across all windows/endpoints within each replicate.

Each W applies its own thinned anchor schedule and corporate-group structure inside those common calendar draws.

Independent bootstrap histories for different W are not authorized.

## 6. Capacity reporting

For every W, report at least:

- common-support eligible calendar dates;
- thinned anchor count;
- final calendar block/unit count;
- corporate-group concentration diagnostics;
- UCB/precision authority state.

Longer W may have fewer anchors by construction. Raw anchor count is diagnostic, not final effective sample size.

If any frozen candidate is underpowered under the final dependence/UCB design:

`LIQUIDITY_BREACH_CALIBRATION_UNDERPOWERED`.

No post-hoc candidate deletion is authorized.

## 7. Revised immediate order

Before external breach calibration:

1. freeze W_SET and W_MAX;
2. freeze common calibration calendar/security target measure;
3. freeze common pre-thinning support valid for all W;
4. freeze W-specific calendar-only thinning constructor / phase rule;
5. freeze design/inclusion weighting back to the common target;
6. freeze residual-persistence measurement rule;
7. freeze synchronized calendar × corporate joint-dependence / simultaneous UCB method;
8. freeze numerical P_MAX_REF / P_TARGET_REF / BETA_LIQ_MAX / TAU_BETA / ALPHA_BETA under their authority rules;
9. derive epsilon and precision requirements;
10. only then instantiate external capacity and breach results.

No result may feed backward into support, phase, weighting, persistence rule, candidate family or risk tolerances.

## 8. Current state

- mechanical overlap treatment: **STRUCTURALLY CLOSED / W-SPECIFIC THINNING**
- common calibration target: **CLOSED / REQUIRED**
- common pre-thinning support across W: **CLOSED / REQUIRED**
- exact thinning phase/seed: **OPEN**
- exact design/inclusion weighting: **OPEN**
- residual persistence rule: **STRUCTURALLY REQUIRED / NUMERICAL FUNCTION OPEN**
- synchronized joint-dependence UCB: **OPEN / NOT YET CONSUMABLE**
- Route-B final-protocol firewall: **NOT YET SATISFIED**
- D05 ceiling visibility: **NOT AUTHORIZED**
- Form-4 outcome access: **NOT AUTHORIZED**
