# BLUE ROUTE-B CHECKPOINT AMENDMENT — LIQUIDITY SUPPORT / FM-08 — 2026-09-17

**Status:** CURRENT CHECKPOINT AMENDMENT  
**Authority:** Blue Team / Mission Control  
**Parent checkpoint:** `BLUE_D05_D09_ROUTE_B_CHECKPOINT_2026-09-17.md`

This amendment controls where it is more recent/specific than the parent checkpoint.

## 1. New controlling artifact

Add:

`governance/D05A_LIQUIDITY_GATE_RESOLUTION_AND_D19_ROUTING_AMENDMENT_2026-09-17.md`.

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

Known ineligibility remains scientifically qualifying and receives zero support under the fingerprinted `A_claim` policy.

## 3. D05 representativeness register extension

`D05_REPRESENTATIVENESS_FAILURE_MODE_REGISTER.md` remains controlling for FM-01 through FM-07.

Current lineage adds:

`FM-08 = DEPLOYMENT_ELIGIBILITY_PIT_INPUT_FAILURE`.

FM-08 covers unresolved claim-defining liquidity/deployment-gate inputs after scientific qualification.

It does not convert deterministic policy ineligibility into missingness.

## 4. D19 dependency extension

`DEPLOYMENT_ELIGIBILITY_UNRESOLVED` can alter whether a qualifying event receives non-zero weight in the primary allocation-weighted estimand.

Absent separately frozen causal clearance it routes:

`ROUTED_B_FOR_LACK_OF_CAUSAL_CLEARANCE`.

The future consumable D19 specification must explicitly cover missingness in claim-defining deployment support as well as missing membership/outcomes.

Current authority remains:

`D19_ADVERSE_TREATMENT_SPEC_PENDING`.

## 5. D05-A visibility / geometry rule

Final liquidity eligible/ineligible counts may be exposed in D05-A only if the frozen liquidity-gate reference semantics are mechanically D07-independent.

Otherwise D05-A may record only D07-independent resolution/lineage states, and final deployment-support counts are instantiated after:

`G* -> A_claim^{G*}`.

This prevents the liquidity gate from becoming a backdoor pre-D07 geometry statistic.

## 6. Liquidity metric contract blocker

Before `LIQUIDITY_ELIGIBILITY_RULE_HASH` becomes consumable, freeze/hash at minimum:

- exact metric definition;
- PIT lookback window;
- reference/cutoff time;
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

## 7. Firewall consequence

`ROUTE_B_FINAL_PROTOCOL_FIREWALL_SATISFIED` remains `FALSE`.

Add the following blockers before ceiling release to protocol-mutating actors:

- hash-addressable `LIQUIDITY_ELIGIBILITY_RULE_HASH` including window/source/history semantics;
- frozen rule for whether insufficient history is deterministic ineligibility or unresolved eligibility;
- frozen D05/D19 routing semantics for FM-08;
- concrete `A_CONSTRUCTOR` binding the liquidity gate.

## 8. Current state additions

- scientific Form-4 qualification partition: **UNCHANGED / FROZEN**
- deployment-support partition: **CLOSED / FROZEN STRUCTURE**
- FM-08 deployment-eligibility PIT failure: **CLOSED / REGISTERED**
- exact liquidity metric/window/source: **OPEN / NOT YET CONSUMABLE**
- insufficient-history policy: **OPEN / NOT YET CONSUMABLE**
- whether final liquidity-gate evaluation is D07-independent: **OPEN**
- D19 adverse mechanics for unresolved deployment support: **NOT YET CONSUMABLE**
- D05-A empirical pass: **NOT YET EXECUTED**
- outcome access: **NOT AUTHORIZED**

## 9. Next closure

Before instantiating the F1–F7 numerical source registry, close the non-numerical liquidity-gate measurement contract:

`metric + PIT window + source class + minimum-history rule + missing-data semantics + D07-independence status`.

Only then bind liquidity-sensitive F2/F3/F4 parameter source contracts to that deployment class.
