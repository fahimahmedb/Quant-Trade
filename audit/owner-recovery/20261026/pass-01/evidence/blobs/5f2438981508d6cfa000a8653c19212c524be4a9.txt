# BLUE ROUTE-B CHECKPOINT AMENDMENT — LIQUIDITY SUPPORT / FM-08 — 2026-09-17

**Status:** CURRENT CHECKPOINT AMENDMENT  
**Authority:** Blue Team / Mission Control  
**Parent checkpoint:** `BLUE_D05_D09_ROUTE_B_CHECKPOINT_2026-09-17.md`

This amendment controls where it is more recent/specific than the parent checkpoint.

## 1. New controlling artifacts

Add:

- `governance/D05A_LIQUIDITY_GATE_RESOLUTION_AND_D19_ROUTING_AMENDMENT_2026-09-17.md`;
- `governance/D05A_D09_LIQUIDITY_EDGAR_CUTOFF_SINGLE_EVALUATION_AMENDMENT_2026-09-17.md`.

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

## 4. Liquidity cutoff semantics are now closed

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

Therefore:

- pre-D07 liquidity measurement/snapshot: **D05-A eligible**;
- final crossing deployment-support partition: **post-G*** unless separately proven invariant;
- final `Q(theta)` consumes crossing-level support, not source-unit liquidity counts.

**Invariants**

- `SOURCE_UNIT_LIQUIDITY_SNAPSHOT_IS_D07_INDEPENDENT`
- `D07_INDEPENDENT_LIQUIDITY_MEASUREMENT_DOES_NOT_IMPLY_D07_INDEPENDENT_CROSSING_SUPPORT`
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

## 8. D19 dependency extension

An unresolved source-unit liquidity snapshot is recorded under FM-08.

D19 claim-support adverse treatment becomes relevant when that unresolved state propagates through final `G*` and unit conversion into:

`FINAL_CROSSING_DEPLOYMENT_ELIGIBILITY_UNRESOLVED`.

One unresolved source record is not automatically one missing crossing.

The future consumable D19 specification must explicitly cover unresolved claim-defining deployment support.

Current authority remains:

`D19_ADVERSE_TREATMENT_SPEC_PENDING`.

## 9. Remaining liquidity metric contract blockers

Before `LIQUIDITY_ELIGIBILITY_RULE_HASH` becomes consumable, still freeze/hash:

- exact metric definition;
- exact PIT lookback length;
- minimum valid observations;
- missing/non-trading session handling;
- adjustment/corporate-action convention where relevant;
- source/provider/version/PIT semantics;
- listing/security identity semantics;
- recently listed / insufficient-history treatment;
- suspension/listing-transition treatment;
- numerical threshold or deterministic eligibility functional;
- recovery/failure/update/version rules.

A generic `ADV` label is not sufficient.

The cutoff/reference anchor and single-shot evaluation semantics are no longer open.

## 10. Firewall consequence

`ROUTE_B_FINAL_PROTOCOL_FIREWALL_SATISFIED` remains `FALSE`.

Current liquidity-side blockers before ceiling release to protocol-mutating actors are:

- hash-addressable `LIQUIDITY_ELIGIBILITY_RULE_HASH` completing the remaining metric/window/source/history/threshold semantics;
- frozen insufficient-history treatment;
- concrete `A_CONSTRUCTOR` binding the liquidity gate;
- frozen source-to-final-crossing propagation/unit-conversion rule in the implementation contract;
- D19 consumable adverse mechanics for unresolved final deployment support where required.

## 11. Current state additions

- scientific Form-4 qualification partition: **UNCHANGED / FROZEN**
- deployment-support partition: **CLOSED / FROZEN STRUCTURE**
- FM-08 deployment-eligibility PIT failure: **CLOSED / REGISTERED**
- liquidity reference anchor: **CLOSED / EDGAR SOURCE DATE**
- daily liquidity cutoff semantics: **CLOSED / LAST COMPLETED SESSION STRICTLY BEFORE EDGAR DATE**
- source-unit liquidity snapshot D07-independence: **CLOSED / YES**
- final crossing support D07-independence: **NO — FOLLOWS G***
- confirmatory eligibility refresh: **CLOSED / SINGLE-SHOT**
- exact liquidity metric/lookback length/source/threshold: **OPEN / NOT YET CONSUMABLE**
- insufficient-history policy: **OPEN / NOT YET CONSUMABLE**
- D19 adverse mechanics for unresolved final deployment support: **NOT YET CONSUMABLE**
- D05-A empirical pass: **NOT YET EXECUTED**
- outcome access: **NOT AUTHORIZED**

## 12. Next closure

Before instantiating the F1–F7 numerical source registry, close the remaining non-numerical liquidity-gate measurement contract:

`exact metric + lookback length + source class + minimum-history rule + missing-session/adjustment semantics`.

The cutoff/reference-time question and the 20-session re-evaluation question are now closed.

Only after the full liquidity rule is hash-addressable should liquidity-sensitive F2/F3/F4 parameter source contracts be bound to that deployment class.
