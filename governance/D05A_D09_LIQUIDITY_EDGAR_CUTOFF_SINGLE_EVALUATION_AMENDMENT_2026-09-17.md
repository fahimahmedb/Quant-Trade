# D05-A / D09 LIQUIDITY EDGAR-CUTOFF / SINGLE-EVALUATION AMENDMENT — 2026-09-17

**Status:** CLOSED / FROZEN SEMANTICS — LOOKBACK LENGTH, SOURCE PROVIDER AND NUMERICAL THRESHOLD STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D07_OPEN_SPACE_BOUNDARY.md`, `D07_PUBLIC_OBSERVABILITY_ENTRY_DEPENDENCY.md`, `D05A_LIQUIDITY_GATE_RESOLUTION_AND_D19_ROUTING_AMENDMENT_2026-09-17.md`, `D09_ROUTE_B_LIQUIDITY_ELIGIBILITY_AND_FINITE_COST_SCENARIO_AMENDMENT_2026-09-17.md`

This amendment closes the liquidity-gate reference-time semantics and scientific re-evaluation rule before D05-A execution. It consumes no D05 empirical values, no Form-4 outcomes and no numerical cost-source values.

## 1. Liquidity measurement is source-date anchored, not entry/formation anchored

For the current lineage, the liquidity metric is anchored to the frozen EDGAR source date rather than to:

- `formation_session`;
- O1/O2 trigger position;
- final executable entry session/open;
- any post-entry observation.

For a source filing/fact `f`:

`LIQUIDITY_REFERENCE_DATE(f) = EDGAR_DATE(f)`.

The EDGAR date is used here as immutable source metadata. This rule does **not** assert that EDGAR date is the final D07 public-knowledge timestamp/proxy for entry authority. `D07_PUBLIC_OBSERVABILITY_ENTRY_DEPENDENCY.md` remains open and controlling for final executable entry timing.

**Invariants**

- `LIQUIDITY_REFERENCE_USES_EDGAR_SOURCE_DATE_NOT_D07_GEOMETRY`
- `LIQUIDITY_EDGAR_ANCHOR_DOES_NOT_RESOLVE_PUBLIC_KNOWLEDGE_TIME`
- `FORMATION_OR_ENTRY_CONVENTION_DOES_NOT_MOVE_LIQUIDITY_REFERENCE_DATE`

## 2. Daily PIT cutoff uses completed sessions only

Because the liquidity metric is expected to use daily market data, the admissible lookback may consume only regular sessions whose market observations are fully completed before the EDGAR source date.

Define:

`LIQUIDITY_CUTOFF_SESSION(f) = last completed regular session strictly before EDGAR_DATE(f)`.

The eventual ADV/liquidity lookback ends on that session.

Therefore, for a filing whose EDGAR date is itself a regular session, the metric does **not** use that same session's full-day volume/price data. This avoids silently consuming observations that may occur after an intraday filing time when only the date-level source anchor is being used.

For a non-session EDGAR date, the cutoff remains the immediately preceding completed regular session and does not depend on whether O1 later attaches the filing to the previous or next formation session.

Exact lookback length, minimum valid-session count, price/volume convention and provider remain separately open.

**Invariants**

- `LIQUIDITY_DAILY_LOOKBACK_USES_ONLY_PRE_EDGAR_COMPLETED_SESSIONS`
- `NO_SAME_EDGAR_DATE_FULL_SESSION_LOOKAHEAD`
- `LIQUIDITY_CUTOFF_IS_O1_INVARIANT`

## 3. What becomes D07-independent in D05-A

The EDGAR-anchored liquidity **measurement object** is D07-independent.

D05-A may therefore compute and, subject to the Route-B visibility firewall, expose source-unit objects such as:

- liquidity-input resolution state;
- frozen-gate eligible/ineligible/unresolved state at a resolved `security/listing × EDGAR_DATE` source unit;
- the corresponding source-unit counts/reason codes where admitted by the frozen surface.

These are not final crossing/observation support counts.

**Invariant:** `SOURCE_UNIT_LIQUIDITY_SNAPSHOT_IS_D07_INDEPENDENT`.

## 4. Final deployment-support counts remain geometry dependent unless separately proven invariant

Source-date anchoring does **not** make the identity of final threshold crossings or scientific observations D07-independent.

The event/crossing that eventually consumes a liquidity snapshot can still depend on frozen final geometry, including O1/O2 and the final observation representation under O4.

Therefore D05-A must not relabel source-unit liquidity counts as:

- final deployable crossing count;
- final `Q(theta)` support count;
- final observation count.

For a final crossing under `G*`, define its liquidity reference date mechanically from the source facts that establish that crossing:

`CROSSING_LIQUIDITY_REFERENCE_DATE(G*) = max EDGAR_DATE(f)`

over the frozen source facts required to establish that crossing under the final crossing construction.

The final support state is then evaluated from the already-defined EDGAR-anchored liquidity snapshot at that date/security under the frozen `LIQUIDITY_ELIGIBILITY_RULE_HASH`.

This mapping rule is frozen now; its final crossing instances are created only after `G*` exists.

**Invariants**

- `D07_INDEPENDENT_LIQUIDITY_MEASUREMENT_DOES_NOT_IMPLY_D07_INDEPENDENT_CROSSING_SUPPORT`
- `FINAL_CROSSING_SUPPORT_FOLLOWS_G_STAR`
- `Q_THETA_CONSUMES_FINAL_CROSSING_SUPPORT_NOT_SOURCE_UNIT_COUNTS`

## 5. Unit-reconciliation correction

Any earlier current-lineage language implying a direct reconciliation:

`QUALIFYING_COUNT = ELIGIBLE + INELIGIBLE + UNRESOLVED`

is valid only when both sides have the same explicitly proven scientific unit and multiplicity semantics.

It must not be used to reconcile a filing/owner/source-unit qualification count directly to crossing-level deployment support.

The correct law is:

`SOURCE_UNIT_PARTITION_RECONCILES_WITHIN_SOURCE_UNIT`

and separately, after final unit conversion:

`FINAL_CROSSING_SUPPORT_PARTITION_RECONCILES_WITHIN_CROSSING_UNIT`.

Cross-unit reconciliation requires the existing hash-addressable accession/owner/security/formation/crossing conversion contract.

**Invariants**

- `NO_CROSS_UNIT_RECONCILIATION_WITHOUT_EXPLICIT_CONVERSION`
- `SOURCE_LIQUIDITY_COUNTS_ARE_NOT_CROSSING_COUNTS`

## 6. Scientific eligibility is evaluated once per final crossing

For the confirmatory scientific policy, deployment eligibility is a **single-shot entry-decision property**.

Once a final crossing receives its deployment-support state from the frozen EDGAR-anchored liquidity rule, that scientific support state is fixed for the 20-regular-session exposure.

The current lineage does not continuously re-evaluate the liquidity gate during the holding interval to add/remove the event from the scientific support.

A later deterioration in liquidity may affect separately governed objects such as:

- realized/expected execution cost;
- Capital Desk risk controls;
- execution feasibility;
- terminal/forced-exit treatment if such mechanics are independently frozen;

but it does not retroactively redefine whether the event belonged to the confirmatory deployment-weighted estimand.

A policy that dynamically removes or reweights scientific support based on post-entry liquidity is a different claim/policy version unless explicitly frozen before authority as part of the claim.

**Invariants**

- `DEPLOYMENT_ELIGIBILITY_IS_SINGLE_SHOT_FOR_CONFIRMATORY_SUPPORT`
- `NO_POST_ENTRY_LIQUIDITY_REEVALUATION_OF_SCIENTIFIC_SUPPORT`
- `POST_ENTRY_LIQUIDITY_CAN_AFFECT_EXECUTION_NOT_RETROACTIVE_CLAIM_MEMBERSHIP`

## 7. FM-08 / D19 consequence

An unresolved source-unit liquidity snapshot is recorded in D05-A under FM-08.

However, D19 adverse treatment for claim-defining support is required only when that unresolved source-unit state propagates through the final `G*` crossing/unit conversion into unresolved support for a final scientific crossing/observation.

Thus:

`SOURCE_UNIT_LIQUIDITY_UNRESOLVED`

is a lineage/failure input, while:

`FINAL_CROSSING_DEPLOYMENT_ELIGIBILITY_UNRESOLVED`

is the claim-support missingness state consumed by final D19 robustness.

No unresolved source unit is automatically counted as one unresolved crossing without the frozen conversion.

**Invariants**

- `FM08_SOURCE_FAILURE_PRECEDES_FINAL_SUPPORT_PROPAGATION`
- `D19_CONSUMES_FINAL_CLAIM_SUPPORT_MISSINGNESS_AFTER_UNIT_CONVERSION`
- `ONE_SOURCE_FAILURE_IS_NOT_AUTOMATICALLY_ONE_MISSING_CROSSING`

## 8. Newly closed versus still open

Closed/frozen now:

- liquidity reference anchor = EDGAR source date;
- daily lookback uses completed regular sessions strictly before that date;
- liquidity measurement/snapshot is D07-independent;
- final crossing support remains post-`G*` unless independently proven invariant;
- cross-unit reconciliation requires explicit conversion;
- confirmatory deployment eligibility is evaluated once and not refreshed during the 20-session hold;
- D19 consumes unresolved final support after source-to-crossing propagation, not raw source-unit failures.

Still open:

- exact liquidity metric (ADV or otherwise);
- exact lookback length;
- minimum valid-session count;
- source/provider/version;
- numerical threshold/class definition;
- insufficient-history policy;
- price/volume adjustment convention;
- exact `A_CONSTRUCTOR` implementation binding the gate;
- D19 consumable adverse-treatment mechanics.

No D05 ceiling visibility, numerical liquidity-source search or Form-4 outcome access is authorized by this amendment.
