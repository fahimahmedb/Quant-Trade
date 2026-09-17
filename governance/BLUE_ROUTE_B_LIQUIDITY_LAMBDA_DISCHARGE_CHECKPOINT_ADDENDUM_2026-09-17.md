# BLUE ROUTE-B CHECKPOINT ADDENDUM — LAMBDA DISCHARGE / REFERENCE PARTICIPATION — 2026-09-17

**Status:** CURRENT CHECKPOINT ADDENDUM  
**Authority:** Blue Team / Mission Control  
**Parents:** `BLUE_D05_D09_ROUTE_B_LIQUIDITY_SUPPORT_CHECKPOINT_AMENDMENT_2026-09-17.md`, `D05A_D09_LIQUIDITY_LAMBDA_DISCHARGE_AND_REFERENCE_PARTICIPATION_AMENDMENT_2026-09-17.md`

This addendum controls where more recent/specific than the parent liquidity checkpoint.

## 1. New controlling artifact

Add:

`governance/D05A_D09_LIQUIDITY_LAMBDA_DISCHARGE_AND_REFERENCE_PARTICIPATION_AMENDMENT_2026-09-17.md`.

## 2. Lambda state

`LAMBDA_DERIVATION_STATE = DERIVATION_BLOCKED_PENDING_ALLOCATION_AND_MARGINAL_ECONOMICS`.

A numerical lambda is no longer an unconditional prerequisite to inspect authorized external candidate-window prediction results.

Instead, after all other selector objects are frozen, current lineage authorizes an exact endpoint materiality test over:

`x = 1/lambda in [0,1]`.

If the same candidate is the shortest passing window at `x=0` and `x=1`:

`LAMBDA_UNRESOLVED_BUT_NONMATERIAL_TO_LOOKBACK`.

If endpoint selections/failure states differ:

`LAMBDA_MATERIAL_TO_LOOKBACK`.

In the latter state, lookback authority is blocked until the economic asymmetry dependency is resolved.

## 3. Normalized epsilon / reference participation

Lookback selection uses one pre-frozen measurement reference rather than `W*(theta)`.

Required reference objects:

- `P_TARGET_REF`;
- `P_MAX_REF`;
- `0 < P_TARGET_REF < P_MAX_REF`.

When independently authorized:

`EPSILON_ADV_BAR = log(P_MAX_REF / P_TARGET_REF)`.

If the reference capacity governor cannot be justified independently of candidate-window results:

`EPSILON_ADV_DERIVATION_BLOCKED`.

No arbitrary epsilon fallback is authorized.

## 4. q-selection split

Before window-selection results:

- freeze q candidate set;
- freeze resampling/stability statistic and threshold;
- freeze split-construction rule;
- select q on a non-target external split disjoint from the window-selection split.

Current q state remains:

`Q_SELECTION_RULE = STRUCTURALLY_CLOSED / NUMERICAL_RULE_INPUTS_OPEN`.

## 5. Current liquidity selector state

- liquidity gate purpose: **CLOSED / CAPACITY ONLY**
- liquidity metric: **CLOSED / NOTIONAL ADV**
- prediction horizon: **CLOSED / NEXT REGULAR SESSION**
- loss family: **CLOSED / ASYMMETRIC ABSOLUTE LOG-RATIO**
- aggregation family: **CLOSED / UPPER QUANTILE**
- security weighting: **CLOSED / EQUAL TOTAL MASS PER SECURITY**
- lambda numerical derivation: **BLOCKED**
- lambda lookback materiality protocol: **CLOSED / ENDPOINT DISCHARGE**
- epsilon architecture: **CLOSED / REFERENCE-PARTICIPATION DERIVATION IF GOVERNOR AUTHORIZED**
- `P_TARGET_REF`, `P_MAX_REF`: **OPEN / NOT YET AUTHORIZED NUMERICALLY**
- q split architecture: **CLOSED / DISJOINT**
- q numerical selection inputs: **OPEN**
- candidate windows: **OPEN**
- daily-notional source route/provider: **OPEN**
- minimum-history semantics: **OPEN**
- D05-A empirical pass: **NOT YET EXECUTED**
- outcome access: **NOT AUTHORIZED**
- Route-B final-protocol firewall: **NOT YET SATISFIED**

## 6. Sequencing consequence

Execution-model calibration is not automatically promoted to the scientific critical path merely because lambda is unresolved.

It becomes a scientific prerequisite for lookback selection only if the frozen endpoint test returns:

`LAMBDA_MATERIAL_TO_LOOKBACK`.

This preserves North-Star focus: resolve execution detail when it changes economic/scientific decisions, not merely because it is available to refine.

No numerical calibration or D05 ceiling visibility is authorized by this addendum.
