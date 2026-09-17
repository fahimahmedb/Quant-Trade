# D05-A LIQUIDITY-GATE RESOLUTION / D19 ROUTING AMENDMENT — 2026-09-17

**Status:** CLOSED / FROZEN STRUCTURAL AMENDMENT — NUMERICAL LIQUIDITY RULE STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D05A_MINIMAL_METRIC_AND_STRATUM_SURFACE.md`, `D05_REPRESENTATIVENESS_FAILURE_MODE_REGISTER.md`, `D19_ADVERSE_TREATMENT_SPEC_DEPENDENCY.md`, `D09_ROUTE_B_LIQUIDITY_ELIGIBILITY_AND_FINITE_COST_SCENARIO_AMENDMENT_2026-09-17.md`

This amendment governs the interaction between frozen Form-4 scientific qualification and the later claim-defining liquidity/deployment eligibility rule.

It does **not** change the Form-4 signal definition, inspect D05 values, choose a numerical ADV threshold, authorize outcome access, or authorize D05 ceiling visibility.

## 1. Scientific qualification and deployment eligibility are orthogonal

The existing Form-4 qualification partition remains exactly:

- `QUALIFYING`
- `NON_QUALIFYING`
- `QUALIFICATION_INDECIDABLE`

A filing/crossing that satisfies the frozen Form-4 scientific rule does not become `NON_QUALIFYING` merely because its security is not deployable under the frozen liquidity gate.

For scientifically qualifying objects, define a separate deployment-support state:

- `DEPLOYMENT_ELIGIBLE`
- `DEPLOYMENT_INELIGIBLE_BY_FROZEN_RULE`
- `DEPLOYMENT_ELIGIBILITY_UNRESOLVED`

Therefore the scientific and deployment partitions are separate authority objects.

**Invariants**

- `FORM4_QUALIFICATION_IS_NOT_LIQUIDITY_ELIGIBILITY`
- `LIQUIDITY_INELIGIBLE_CAN_REMAIN_SCIENTIFICALLY_QUALIFYING`
- `DEPLOYMENT_ELIGIBILITY_IS_ORTHOGONAL_TO_FORM4_QUALIFICATION`

## 2. Reconciliation identity

For the scientifically qualifying population over any authority-covered evaluation scope where the liquidity gate is evaluable:

`QUALIFYING_COUNT`

must reconcile to:

`QUALIFYING_DEPLOYMENT_ELIGIBLE_COUNT`
`+ QUALIFYING_DEPLOYMENT_INELIGIBLE_COUNT`
`+ QUALIFYING_DEPLOYMENT_ELIGIBILITY_UNRESOLVED_COUNT`.

This identity does not imply that all three counts are publishable in D05-A before final geometry. Visibility depends on §5.

The deployment-weighted estimand and later `Q(theta)` consume only events receiving non-zero weight under the frozen `A_claim` policy. They do not substitute `QUALIFYING_COUNT` for deployable support.

**Invariants**

- `QUALIFYING_POPULATION_RECONCILES_TO_DEPLOYMENT_SUPPORT_STATES`
- `Q_THETA_CONSUMES_FROZEN_DEPLOYMENT_SUPPORT_NOT_RAW_QUALIFYING_COUNT`

## 3. Known ineligibility versus unresolved eligibility

A deterministic frozen policy exclusion is not missingness.

Examples may include, if frozen before D05 ceiling visibility:

- liquidity metric below the claim-defining deployment threshold;
- explicitly ineligible security/listing class;
- insufficient lookback history **when the frozen policy itself defines insufficient history as ineligible**.

These objects are:

`DEPLOYMENT_INELIGIBLE_BY_FROZEN_RULE`.

They remain part of the scientifically qualifying Form-4 population but receive zero deployment support under the claim policy.

By contrast, when the frozen policy requires a liquidity measurement and that measurement cannot be resolved under its authorized source/PIT rule, use:

`DEPLOYMENT_ELIGIBILITY_UNRESOLVED`.

Examples may include:

- required source data missing unexpectedly;
- PIT reference ambiguity;
- unresolved listing/security identity needed by the liquidity source;
- incomplete history where the policy did **not** predeclare deterministic ineligibility;
- unresolved corporate-action/reference semantics that prevent the metric from being computed as specified.

**Invariants**

- `POLICY_INELIGIBILITY_IS_NOT_MISSINGNESS`
- `UNRESOLVED_REQUIRED_LIQUIDITY_INPUT_IS_MISSINGNESS`
- `INSUFFICIENT_HISTORY_TREATMENT_MUST_BE_PRE_FROZEN`

## 4. New failure mode FM-08 — deployment-eligibility input failure

This amendment adds the following failure mode to the D05 representativeness register.

### `FM-08 — DEPLOYMENT_ELIGIBILITY_PIT_INPUT_FAILURE`

**Failure mode**  
A scientifically qualifying object cannot be classified under the frozen claim-defining liquidity/deployment gate because a required PIT input cannot be resolved.

**Causal mechanisms may include**

- missing/ambiguous liquidity history;
- recently listed security with insufficient history under a rule that requires a measurement rather than deterministic exclusion;
- liquidity-source coverage gap;
- unresolved listing/reference transition;
- missing session/volume observations required by the metric;
- inability to establish the frozen PIT cutoff.

**Threatened property**  
Representativeness of the deployable support of the allocation-weighted estimand.

**Detectability**  
`INTERNAL_DETECTABLE` when the scientifically qualifying denominator and required reference identities are certified; otherwise it inherits the relevant upstream denominator/reference uncertainty.

**Minimal observable unit**  
`qualifying crossing/security -> liquidity-gate evaluation result`.

**Minimal stratum**  
No exploratory size/ADV buckets. A stratum exists only when needed to classify a documented source/reference/listing regime causing the failure.

**Required control**

- frozen `LIQUIDITY_ELIGIBILITY_RULE_HASH`;
- PIT liquidity-input ledger;
- explicit resolved/ineligible/unresolved state;
- canonical missing-object identity;
- Branch-B routing when causal clearance is absent.

**Possible states/verdict contributions**

- `DEPLOYMENT_ELIGIBLE`
- `DEPLOYMENT_INELIGIBLE_BY_FROZEN_RULE`
- `DEPLOYMENT_ELIGIBILITY_UNRESOLVED`
- downstream `D19_ADVERSE_TREATMENT_SPEC_PENDING` where unresolved support can alter the estimand.

**Invariant:** `DEPLOYMENT_SUPPORT_FAILURE_IS_EXPLICIT_FAILURE_MODE`.

## 5. D05-A surface and D07 dependency

The liquidity gate is claim-defining through `A_claim`, but its per-event evaluation may or may not be D07-independent.

Therefore D05-A may expose the final eligible/ineligible qualifying counts **only when** the frozen liquidity-gate reference time and required inputs are mechanically D07-independent.

If final liquidity eligibility depends on the final authorized entry/geometry `G*`, D05-A must not publish a geometry-specific deployment-support partition before D07 freeze.

In that case D05-A may record only D07-independent input-resolution states necessary for lineage/robustness, while final:

- `QUALIFYING_DEPLOYMENT_ELIGIBLE_COUNT`
- `QUALIFYING_DEPLOYMENT_INELIGIBLE_COUNT`
- `QUALIFYING_DEPLOYMENT_ELIGIBILITY_UNRESOLVED_COUNT`

are instantiated after `G*` and `A_claim^{G*}` under the frozen rule.

No geometry-dependent liquidity statistic is silently promoted into the pre-D07 D05-A surface.

**Invariants**

- `D05A_EXPOSES_ONLY_D07_INDEPENDENT_LIQUIDITY_GATE_OUTPUTS`
- `FINAL_DEPLOYMENT_SUPPORT_MAY_FOLLOW_G_STAR`
- `LIQUIDITY_GATE_DOES_NOT_BACKDOOR_EXPAND_D07_BOUNDARY`

## 6. Minimal D05-A resolution surface

Where D07-independent and required for classification/lineage, the minimal added visible/status surface is:

- `LIQUIDITY_GATE_INPUT_RESOLVED_COUNT`
- `LIQUIDITY_GATE_INPUT_UNRESOLVED_COUNT`
- `LIQUIDITY_GATE_RESOLUTION_STATE`
- `LIQUIDITY_GATE_UNRESOLVED_COUNT_BY_REASON` only over pre-frozen FM-08 reason codes.

Where the final gate itself is D07-independent, the following derived counts may additionally be exposed under the Route-B visibility firewall:

- `QUALIFYING_DEPLOYMENT_ELIGIBLE_COUNT`
- `QUALIFYING_DEPLOYMENT_INELIGIBLE_COUNT`
- `QUALIFYING_DEPLOYMENT_ELIGIBILITY_UNRESOLVED_COUNT`.

These are deployment-support states, not new Form-4 qualification states and not exploratory strata.

## 7. Branch-B / D19 routing

`DEPLOYMENT_ELIGIBILITY_UNRESOLVED` can change whether a scientifically qualifying object receives non-zero weight in the primary deployment-weighted estimand.

Unless a separately frozen causal rule grants availability-only treatment, the object is routed:

`ROUTED_B_FOR_LACK_OF_CAUSAL_CLEARANCE`.

The existing D19 consumable specification must therefore explicitly handle missingness in claim-defining deployment support, not only missing return observations.

Its canonical missing-object population must preserve the link:

`qualifying crossing -> security/listing -> liquidity-gate state -> A_claim support/weight -> outcome object`.

Until D19 is extended to mechanically define adverse completion/treatment for unresolved deployment support:

`D19_ADVERSE_TREATMENT_SPEC_PENDING`.

No arbitrary assumption `UNRESOLVED -> INELIGIBLE` or `UNRESOLVED -> ELIGIBLE` is authorized unless that treatment was already part of the frozen policy semantics before the unresolved state was observed.

**Invariants**

- `UNRESOLVED_DEPLOYMENT_SUPPORT_ROUTES_B_ABSENT_CAUSAL_CLEARANCE`
- `D19_MUST_COVER_CLAIM_DEFINING_SUPPORT_MISSINGNESS`
- `UNRESOLVED_LIQUIDITY_GATE_HAS_NO_POST_HOC_DEFAULT`

## 8. ADV / liquidity metric contract requirements

Before the numerical liquidity gate becomes consumable, `LIQUIDITY_ELIGIBILITY_RULE_HASH` must bind at minimum:

- exact liquidity metric definition (ADV or another frozen metric);
- lookback-window length;
- PIT cutoff/reference time;
- minimum valid-observation count;
- treatment of non-trading/missing sessions;
- price/volume adjustment and corporate-action convention where relevant;
- source/provider and source-version/PIT semantics;
- listing/security identity used by the source;
- treatment of newly listed securities / insufficient history;
- treatment of suspensions and listing transitions;
- numerical threshold or deterministic eligibility functional once frozen;
- failure/recovery semantics;
- update/version rule.

A generic label `ADV` is not a consumable claim-defining rule.

**Invariants**

- `ADV_WINDOW_AND_SOURCE_ARE_CLAIM_FINGERPRINTED`
- `ADV_IS_NOT_DEFINED_WITHOUT_PIT_WINDOW_SOURCE_AND_HISTORY_RULE`
- `NEW_LISTING_HISTORY_RULE_PRECEDES_GATE_VALUES`

## 9. Effect on existing frozen artifacts

For the current lineage:

- `D05A_MINIMAL_METRIC_AND_STRATUM_SURFACE.md` remains controlling for Form-4 qualification and all non-conflicting surface rules;
- this amendment adds the orthogonal deployment-support/resolution surface and supersedes any reading that treats liquidity ineligibility as `NON_QUALIFYING`;
- `D05_REPRESENTATIVENESS_FAILURE_MODE_REGISTER.md` remains controlling for FM-01 through FM-07 and is extended by FM-08 here;
- `D19_ADVERSE_TREATMENT_SPEC_DEPENDENCY.md` remains `DECIDED_NOT_SPECIFIED` and now has an explicit additional required missingness class: unresolved claim-defining deployment support.

No prior scientific result is changed because D05-A has not yet executed.

## 10. Current state

Closed/frozen:

- scientific qualification remains three-state;
- deployment eligibility is a separate three-state object;
- known policy ineligibility is distinct from missingness;
- FM-08 deployment-eligibility PIT failure exists;
- unresolved deployment support routes Branch B absent causal clearance;
- final eligibility counts cannot be exposed pre-D07 unless their reference semantics are D07-independent;
- ADV/liquidity window/source/history semantics must be fingerprinted.

Still open:

- exact liquidity metric;
- exact lookback window;
- exact source/provider;
- exact numerical threshold;
- exact insufficient-history policy;
- whether final per-event gate evaluation is D07-independent;
- D19 consumable adverse-treatment mechanics for unresolved deployment support.

No D05 ceiling visibility, numerical liquidity-source search or Form-4 outcome access is authorized by this amendment.
