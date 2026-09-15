# D05 OBSERVATION UNIT TAXONOMY

**Status:** CLOSED  
**Authority:** Blue Team / Mission Control  
**Prerequisite:** `D07_OPEN_SPACE_BOUNDARY` frozen before D05-A execution.

## 1. Principle

The status of an object does not depend on its label.

It depends on **what produces it**.

**Invariant:** `CLASSIFY_BY_PRODUCER`

The taxonomy distinguishes:

1. `SOURCE_PRIMITIVE` (U0)
2. `FROZEN_RULE_DERIVED` (U1)
3. `RESOLUTION_DERIVED` (U2)
4. `D07_DESIGN_DERIVED` (U3)

A metric inherits every dependency in:

`UNIT + DENOMINATOR + STRATA + MAPPING + TRANSFORM`.

Aggregation and stratification never remove a dependency.

## 2. Three authority destinations

### `D05-A`

The metric is D07-invariant **and** explicitly authorized in the frozen D05-A inspection surface.

### `D05-B`

The metric depends on at least one still-open D07 choice.

### `OUT_OF_PASS`

The metric is D07-invariant but the metric, stratum, crossing of strata, transform or visible output was not pre-authorized in the current D05-A pass.

`OUT_OF_PASS` is not D05-B. It may become D05-A in a later recorded pass. D05-B must wait for D07.

## 3. U0 — `SOURCE_PRIMITIVE`

A U0 object exists directly in the source or in a reference/calendar whose semantics do not depend on D07.

Its production requires no D07 geometry choice, no external identity resolution and no empirical target-distribution inspection.

Examples:

- raw SEC filing object;
- accession / filing identifier;
- original-filing marker;
- EDGAR date;
- reporting-owner CIK as declared;
- issuer CIK as declared;
- transaction row;
- declared role/relationship flags;
- calendar date;
- pinned regular-market-session object;
- raw reference-data object before resolution.

`SOURCE_PRIMITIVE -> D05-A ELIGIBLE`

subject to the frozen inspection-surface gate.

## 4. U1 — `FROZEN_RULE_DERIVED`

`U1 = f_frozen(U0)`

A U1 object is produced only by applying a previously frozen rule to U0 objects. It requires no open D07 choice and no external identity resolver.

### 4.1 Qualifying transaction

A qualifying transaction is:

- non-derivative;
- transaction code = `P`;
- acquired/disposed indicator = `A` (acquired).

This means:

`transaction code P` + `acquired/disposed indicator A`.

It does **not** admit transaction code `A` (award/grant).

`qualifying_transaction -> U1`

### 4.2 Qualifying reporting-owner identity

The frozen A1 scientific contract fixes:

`insider identity = reporting-owner CIK`

and the crossing is based on:

`>=2 distinct qualified insider CIKs`.

Therefore:

> For this scientific lineage, two owners are distinct when their reporting-owner CIKs are distinct.

No natural-person reconciliation is required or authorized for the current claim.

A future operation that tried to merge different CIKs as one natural person would be:

`natural_person_reconciliation -> U2`

and would alter claim semantics rather than merely improve measurement.

### 4.3 Joint filings

Where primary filing structure does not prove the attribution required by the frozen claim:

`JOINT_OWNER_AMBIGUOUS`.

This is preserved explicitly. It is never repaired through inference.

### 4.4 Qualifying filing

A qualifying filing is produced by the closed Form 4 qualification rules without constructing a D07 event.

It is therefore U1 and D07-independent.

Explicit decision:

`qualifying_filing -> U1`

and:

`qualifying_filing_count_per_issuer -> D05-A ELIGIBLE`.

O4 can change observation count. It cannot create, merge or remove filings that satisfy the frozen filing-level qualification rules.

## 5. U2 — `RESOLUTION_DERIVED`

`U2 = Resolver_frozen(U0/U1, ReferenceData)`

A U2 object does not depend on D07 but requires an external reference/mapping operation.

Examples:

- issuer → security;
- issuer → listing;
- security → PIT ticker;
- security → exchange/listing state;
- PIT security identity;
- security-session association after security resolution.

Allowed resolver states must be explicit, for example:

- `PIT_RESOLVED`
- `PIT_UNRESOLVED`
- `PIT_AMBIGUOUS`
- `REFERENCE_NOT_AVAILABLE`

A failed resolution is a feasibility observation, not an invitation to tune the resolver.

`RESOLUTION_DERIVED -> D05-A ELIGIBLE`

only if:

1. the resolver is independent of O1–O4;
2. its Resolution / Mapping Contract is frozen before measurement;
3. no empirical target distribution was used to select or optimize it.

### Invariant

`NO_SILENT_RESOLVER_OPTIMIZATION`

The first frozen resolver's poor coverage is a scientific result.

A later improved resolver requires a new identity/version, new hash, recorded reason, new pass/lineage treatment and preservation of the prior result.

## 6. U3 — `D07_DESIGN_DERIVED`

`U3 = g_D07(U0, U1, U2)`

A U3 object's existence, identity, denominator or cardinality depends on at least one of:

`O1 × O2 × O3 × O4`.

Examples:

- `formation_session` where produced by O1;
- formation-window membership;
- threshold-crossing event;
- signal;
- statistical observation;
- exposure episode;
- overlapping exposure group;
- event count;
- observation count;
- event-level price coverage;
- event-level identity coverage;
- observations per issuer;
- overlap-adjusted unit.

### Formation-window membership

`formation_window_membership -> U3`

without case-by-case exceptions.

Even if a particular filing would happen to receive the same membership under every plausible convention, the unit is produced by a function containing O1.

**Invariant:** `NO_SCENARIO_LOCAL_CLASSIFICATION`

Classification is over the full open design space, never over the observed or expected “easy case”.

`U3 -> D05-B`

## 7. Complete metric inheritance

For:

`M = Aggregate(U, denominator, strata, mapping, transform)`

D05-A authority requires every component to be D07-invariant, defined ex ante and pre-authorized in the inspection surface.

If any component depends on D07:

`M -> D05-B`.

If all components are D07-invariant but one inspection component was not pre-authorized:

`M -> OUT_OF_PASS`.

## 8. Stratification — Representativeness Necessity Test

D07-invariance is not sufficient to authorize a stratum.

Every candidate stratum must answer before measurement:

> **Which ex-ante identifiable representativeness failure mode requires this stratum to be visible?**

If no named causal failure mode requires it:

`OUT_OF_PASS`.

Strata exist to detect whether acceptable aggregate coverage masks a structural representativeness failure. They do not exist to discover interesting segments, frequent-signal segments, higher-performing segments or possible rescue sub-populations.

### Required frozen stratum registry

For each authorized stratum, record identifier, variable, producer/source, representativeness justification, metrics to which it applies, granularity, allowed crossings, small-cell treatment and visible outputs.

A crossing is never automatically authorized because both dimensions are separately authorized.

**Invariant:** `NO_CARTESIAN_EXPLORATION`

## 9. Minimal inspection surface

The D05-A surface follows the same minimality principle as the D07 boundary:

> **the smallest inspection surface sufficient to decide feasibility and representativeness of coverage.**

A metric or stratum is excluded if it is merely interesting, available, traditional, potentially predictive or useful for a future design.

It is included only when omitting it creates an identifiable risk of falsely concluding that the claim population is measurable/representative.

## 10. Same label, different producer

Example:

`identity_resolution_rate`

can be calculated per qualifying filing:

`resolved qualifying filings / qualifying filings`

U1 + U2 → D05-A possible.

Or per event:

`resolved events / events`

event is U3 → D05-B.

Same verbal concept, different authority.

## 11. O4 stress test

Quantities involving observation count, event count, signal count, exposure count, observations per issuer or overlap are presumed U3 until proven otherwise.

By contrast:

`qualifying_filing_count_per_issuer`

is explicitly U1 and D05-A-eligible.

## 12. Derivation chains

A typical chain is:

`filing`
→ `qualifying filing`
→ `resolved security`
→ `event`
→ `exposure observation`

or:

`U0 -> U1 -> U2 -> U3`.

Authority is determined by the most dependent stage used in the metric.

## 13. `AMBIGUOUS`

An ambiguous object must be resolved **before inspecting values**.

Question:

> Would it be produced, defined and measured identically under every admissible D07 geometry?

If yes, classify it U0/U1/U2, then apply the inspection-surface gate.

If no: `D05-B`.

If D07-invariant but not pre-authorized: `OUT_OF_PASS`.

If classification itself cannot be established without values: `EMBARGO`.

## 14. Core invariants

- `CLASSIFY_BY_PRODUCER`
- `CIK_IS_CLAIM_IDENTITY`
- `DEPENDENCY_INHERITANCE`
- `TWO_FILTER_AUTHORITY`
- `REPRESENTATIVENESS_ONLY_STRATA`
- `NO_CARTESIAN_EXPLORATION`
- `OUT_OF_PASS_IS_NOT_D05B`
- `NO_SILENT_RESOLVER_OPTIMIZATION`
- `NO_SCENARIO_LOCAL_CLASSIFICATION`
