# BLUE ROUTE-B CHECKPOINT AMENDMENT — LIQUIDITY SUPPORT / FM-08 — 2026-09-17

**Status:** CURRENT CHECKPOINT AMENDMENT  
**Authority:** Blue Team / Mission Control  
**Parent checkpoint:** `BLUE_D05_D09_ROUTE_B_CHECKPOINT_2026-09-17.md`

This amendment controls where it is more recent/specific than the parent checkpoint.

## 1. New controlling artifacts

Add:

- `governance/D05A_LIQUIDITY_GATE_RESOLUTION_AND_D19_ROUTING_AMENDMENT_2026-09-17.md`;
- `governance/D05A_D09_LIQUIDITY_EDGAR_CUTOFF_SINGLE_EVALUATION_AMENDMENT_2026-09-17.md`;
- `governance/D05A_D09_LIQUIDITY_IDENTITY_AND_LOOKBACK_SELECTION_AMENDMENT_2026-09-17.md`;
- `governance/D05A_D09_LIQUIDITY_METRIC_AND_LOOKBACK_STABILITY_CONTRACT_2026-09-17.md`;
- `governance/D05A_D09_LIQUIDITY_PREDICTIVE_LOOKBACK_AND_NOTIONAL_SOURCE_CONTRACT_2026-09-17.md`.

## 2. Qualification versus deployment support

The Form-4 scientific qualification partition remains:

- `QUALIFYING`
- `NON_QUALIFYING`
- `QUALIFICATION_INDECIDABLE`

Liquidity does not create a new Form-4 qualification state.

For scientifically qualifying objects, use the orthogonal deployment-support partition:

- `DEPLOYMENT_ELIGIBLE`
- `DEPLOYMENT_INELIGIBLE_BY_FROZEN_RULE`
- `DEPLOYMENT_ELIGIBILITY_UNRESOLVED`

Known policy ineligibility remains scientifically qualifying and receives zero support under the fingerprinted `A_claim` policy.

## 3. D05 representativeness register extension

`D05_REPRESENTATIVENESS_FAILURE_MODE_REGISTER.md` remains controlling for FM-01 through FM-07.

Current lineage adds:

`FM-08 = DEPLOYMENT_ELIGIBILITY_PIT_INPUT_FAILURE`.

FM-08 covers unresolved claim-defining liquidity/deployment-gate inputs after scientific qualification.

It does not convert deterministic policy ineligibility into missingness.

## 4. Liquidity cutoff semantics are closed

The liquidity measurement is anchored to source metadata, not final D07 geometry:

`LIQUIDITY_REFERENCE_DATE(f) = EDGAR_DATE(f)`.

For daily market-data liquidity metrics:

`LIQUIDITY_CUTOFF_SESSION(f) = last completed regular session strictly before EDGAR_DATE(f)`.

Consequences:

- no same-EDGAR-date full-session volume/price may enter the lookback;
- the cutoff is invariant to O1 formation-session convention;
- entry/session geometry does not move the liquidity reference date;
- this rule does not resolve the separately open public-knowledge timestamp/proxy used for final entry authority.

Current state:

`LIQUIDITY_REFERENCE_ANCHOR = CLOSED / EDGAR_SOURCE_DATE`

`LIQUIDITY_DAILY_CUTOFF = CLOSED / PRE_EDGAR_COMPLETED_SESSION`.

## 5. D05-A visibility: snapshot versus final crossing support

EDGAR anchoring makes the **source-unit liquidity snapshot** D07-independent.

D05-A may therefore compute/expose, subject to the Route-B firewall, source-unit liquidity input-resolution and frozen-gate state at a resolved `security/listing × EDGAR_DATE` unit.

It does **not** follow that final deployable crossing/observation counts are D07-independent.

Final crossings still depend on `G*`. For a final crossing:

`CROSSING_LIQUIDITY_REFERENCE_DATE(G*) = max EDGAR_DATE(f)`

over the frozen source facts required to establish that crossing under final geometry.

The deployment security/listing identity for that crossing is resolved PIT at that latest required EDGAR date under the frozen downstream resolver contract. Earlier filing identities do not override the final PIT identity. If the required identity is unresolved/ambiguous, the crossing enters FM-08 rather than using a stale fallback.

Therefore:

- pre-D07 liquidity measurement/snapshot: **D05-A eligible**;
- final crossing deployment-support partition: **post-G*** unless separately proven invariant;
- final `Q(theta)` consumes crossing-level support, not source-unit liquidity counts.

**Invariants**

- `SOURCE_UNIT_LIQUIDITY_SNAPSHOT_IS_D07_INDEPENDENT`
- `D07_INDEPENDENT_LIQUIDITY_MEASUREMENT_DOES_NOT_IMPLY_D07_INDEPENDENT_CROSSING_SUPPORT`
- `DEPLOYMENT_SECURITY_IDENTITY_IS_PIT_AT_CROSSING_REFERENCE_DATE`
- `Q_THETA_CONSUMES_FINAL_CROSSING_SUPPORT_NOT_SOURCE_UNIT_COUNTS`

## 6. Cross-unit reconciliation correction

No direct identity may reconcile a filing/owner/source qualification count to crossing-level deployment support without the frozen unit-conversion contract.

The valid rule is:

`SOURCE_UNIT_PARTITION_RECONCILES_WITHIN_SOURCE_UNIT`

and, after final crossing construction:

`FINAL_CROSSING_SUPPORT_PARTITION_RECONCILES_WITHIN_CROSSING_UNIT`.

Earlier language implying direct reconciliation from `QUALIFYING_COUNT` to deployment-support crossing counts is superseded unless unit identity/multiplicity is independently proven.

## 7. Single-shot confirmatory eligibility

Scientific deployment eligibility is evaluated once for the final crossing from the frozen EDGAR-anchored liquidity snapshot and remains fixed through the 20-regular-session confirmatory exposure.

No continuous liquidity-gate refresh may remove/reweight an event from scientific support after entry.

Post-entry liquidity deterioration may affect separately frozen execution-cost, risk, feasibility or terminal-treatment mechanics, but it does not retroactively rewrite claim membership/support.

Current state:

`DEPLOYMENT_ELIGIBILITY_REEVALUATION = SINGLE_SHOT / CLOSED`.

**Invariant:** `NO_POST_ENTRY_LIQUIDITY_REEVALUATION_OF_SCIENTIFIC_SUPPORT`.

## 8. Liquidity gate purpose / metric family are closed

The claim-defining liquidity gate is a **capacity-eligibility gate only**.

It does not gate on opening spread, opening depth, auction quality or opening slippage. Those remain economic-cost/model-risk objects in `K_forward` / `M_economic`.

The claim-defining metric family is:

`ADV_NOTIONAL(W) = mean DAILY_TRADED_NOTIONAL over the frozen lookback`.

Participation is expressed as:

`INTENDED_ORDER_NOTIONAL / ADV_NOTIONAL`.

Raw share-volume ADV is not the claim-support coordinate in this lineage.

Current state:

`LIQUIDITY_GATE_PURPOSE = CLOSED / CAPACITY_ONLY`

`LIQUIDITY_METRIC_FAMILY = CLOSED / NOTIONAL_ADV`.

**Invariants**

- `OPEN_EXECUTION_QUALITY_IS_NOT_A_SUPPORT_GATE`
- `CLAIM_LIQUIDITY_METRIC_IS_NOTIONAL_ADV`
- `PARTICIPATION_USES_NOTIONAL_OVER_NOTIONAL_ADV`

## 9. Lookback criterion is predictive, not fixed-parameter estimation

The authority-bearing lookback objective is no longer interpreted as estimating a fixed latent ADV.

For cutoff session `t`, the primary external calibration target is:

`NEXT_SESSION_TRADED_NOTIONAL(t)`

for the immediately following regular session of the same PIT-resolved security/listing lineage.

The lookback-selection form is:

`W* = shortest W in the frozen candidate set such that ADV_PREDICTION_ERROR(W) <= epsilon_ADV`.

Before inspecting candidate-window results, freeze/hash:

- candidate window set;
- exact prediction-error/loss functional;
- pooling/aggregation/weighting rule;
- `epsilon_ADV`;
- tie/failure rule;
- calibration-corpus construction.

The 20-session holding horizon does not redefine this entry-capacity forecast horizon. Post-entry/exit liquidity remains cost/risk/terminal treatment rather than support refresh.

Current state:

`LOOKBACK_OBJECTIVE = CLOSED / NEXT-SESSION PREDICTIVE LIQUIDITY`

while the exact error functional and numerical threshold remain open.

**Invariants**

- `ADV_LOOKBACK_TARGET_IS_PREDICTIVE_LIQUIDITY`
- `ADV_CAPACITY_FORECAST_HORIZON_IS_NEXT_REGULAR_SESSION`
- `PREDICTION_ERROR_FUNCTIONAL_PRECEDES_WINDOW_RESULTS`
- `EPSILON_ADV_PRECEDES_WINDOW_RESULTS`

## 10. Calibration corpus applicability and non-circularity

The non-target lookback-calibration corpus must cover the intended `L_deploy(theta)` liquidity regime.

Its inclusion rule may not depend on realized candidate-window ADV outputs, because that would make the window selector choose the corpus that chooses the window.

Before calibration, freeze a candidate-window-independent `CALIBRATION_LIQUIDITY_DOMAIN` using a separately justified provider/source class, independent reference convention, or broader predeclared universe/stratification that contains the intended deployment regime.

If no non-circular applicability rule can be frozen:

`LIQUIDITY_LOOKBACK_CALIBRATION_DOMAIN_UNRESOLVED`.

**Invariants**

- `CALIBRATION_CORPUS_COVERS_INTENDED_LIQUIDITY_REGIME`
- `CALIBRATION_CORPUS_MEMBERSHIP_IS_INDEPENDENT_OF_CANDIDATE_WINDOW_RESULTS`

## 11. Daily traded-notional representation follows source authority

The exact `DAILY_TRADED_NOTIONAL` route is still open, but its selection logic is closed.

Allowed routes are:

- a source-provided daily traded-notional field with sufficient PIT/version/reproducibility semantics; or
- a deterministic frozen price × share-volume construction.

If constructed, the exact price reference (for example close, VWAP or another justified field), volume field, corporate-action convention and PIT lineage must be frozen.

No price convention is selected merely because it is theoretically preferable if the authorized source cannot reproduce it historically/PIT. Conversely, no simpler convention is selected because it retains more target securities or changes ADV favorably.

Current state:

`DAILY_NOTIONAL_REPRESENTATION_RULE = CLOSED / SOURCE-AUTHORITY-AND-REPRODUCIBILITY-FIRST`

while N1 versus N2 and any exact price/volume fields remain open.

**Invariants**

- `DAILY_NOTIONAL_REPRESENTATION_FOLLOWS_FROZEN_SOURCE_AUTHORITY`
- `THEORETICAL_PREFERENCE_DOES_NOT_OVERRIDE_PIT_REPRODUCIBILITY`
- `NO_TARGET_RETENTION_DRIVEN_PRICE_CONVENTION`

## 12. D19 dependency extension

An unresolved source-unit liquidity snapshot is recorded under FM-08.

D19 claim-support adverse treatment becomes relevant when that unresolved state propagates through final `G*` and unit conversion into:

`FINAL_CROSSING_DEPLOYMENT_ELIGIBILITY_UNRESOLVED`.

One unresolved source record is not automatically one missing crossing.

The future consumable D19 specification must explicitly cover unresolved claim-defining deployment support.

Current authority remains:

`D19_ADVERSE_TREATMENT_SPEC_PENDING`.

## 13. Remaining liquidity metric contract blockers

Before `LIQUIDITY_ELIGIBILITY_RULE_HASH` becomes consumable, still freeze/hash:

- exact candidate-window set;
- exact `ADV_PREDICTION_ERROR(W)` functional and aggregation rule;
- numerical `epsilon_ADV`;
- exact candidate-window-independent `CALIBRATION_LIQUIDITY_DOMAIN`;
- exact daily-notional source/construction route;
- source class/provider/version/PIT semantics;
- final lookback length derived under the frozen rule;
- minimum valid observations;
- missing/non-trading session handling;
- recently listed / insufficient-history treatment;
- suspension/listing-transition treatment;
- numerical ADV threshold or deterministic capacity/participation eligibility functional;
- recovery/failure/update/version rules.

The cutoff/reference anchor, final identity-resolution time, gate purpose, metric family, forecast horizon, lookback objective form and single-shot support evaluation are no longer open.

## 14. Firewall consequence

`ROUTE_B_FINAL_PROTOCOL_FIREWALL_SATISFIED` remains `FALSE`.

Current liquidity-side blockers before ceiling release to protocol-mutating actors are the hash-addressable completion of the remaining objects in §13, plus:

- concrete `A_CONSTRUCTOR` binding the liquidity gate;
- frozen source-to-final-crossing propagation/unit-conversion rule in the implementation contract;
- D19 consumable adverse mechanics for unresolved final deployment support where required.

## 15. Current state additions

- scientific Form-4 qualification partition: **UNCHANGED / FROZEN**
- deployment-support partition: **CLOSED / FROZEN STRUCTURE**
- FM-08 deployment-eligibility PIT failure: **CLOSED / REGISTERED**
- liquidity reference anchor: **CLOSED / EDGAR SOURCE DATE**
- daily liquidity cutoff semantics: **CLOSED / LAST COMPLETED SESSION STRICTLY BEFORE EDGAR DATE**
- source-unit liquidity snapshot D07-independence: **CLOSED / YES**
- final crossing support D07-independence: **NO — FOLLOWS G***
- final deployment security identity time: **CLOSED / PIT AT LATEST REQUIRED EDGAR DATE**
- confirmatory eligibility refresh: **CLOSED / SINGLE-SHOT**
- gate purpose: **CLOSED / CAPACITY ONLY**
- metric family: **CLOSED / NOTIONAL ADV**
- lookback objective: **CLOSED / NEXT-SESSION PREDICTIVE LIQUIDITY**
- calibration-corpus non-circularity: **CLOSED / REQUIRED**
- daily-notional representation selection principle: **CLOSED / SOURCE AUTHORITY FIRST**
- exact loss/window/epsilon/corpus/provider/notional route/threshold: **OPEN / NOT YET CONSUMABLE**
- insufficient-history policy: **OPEN / NOT YET CONSUMABLE**
- D19 adverse mechanics for unresolved final deployment support: **NOT YET CONSUMABLE**
- D05-A empirical pass: **NOT YET EXECUTED**
- outcome access: **NOT AUTHORIZED**

## 16. Next closure

Before instantiating liquidity-sensitive F2/F3/F4 source contracts or authorizing numerical calibration, close the remaining non-numerical selector objects:

`candidate windows + prediction-error functional + aggregation rule + epsilon rule/source + calibration-liquidity-domain rule + daily-notional source/construction precedence + minimum-history semantics`.

Only after these objects are hash-addressable may numerical source/calibration results choose the final window and feed the liquidity gate.
