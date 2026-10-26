# D05 REPRESENTATIVENESS FAILURE-MODE REGISTER

**Status:** CLOSED  
**Authority:** Blue Team / Mission Control  
**Purpose:** derive the minimal D05-A inspection surface from ex-ante representativeness failure modes.

The register is written before inspection of D05-A values.

It starts from:

> **How can the measured population stop representing the claim population?**

It does not start from available variables.

## 1. Line schema

Each failure mode records `FAILURE_MODE`, `CAUSAL_MECHANISM`, `THREATENED_PROPERTY`, `DETECTABILITY_CLASS`, `MINIMAL_OBSERVABLE_UNIT`, `MINIMAL_STRATUM`, `REQUIRED_CONTROL`, `ADMISSIBLE_OUTPUT` and `POSSIBLE_VERDICT`.

### Detectability classes

#### `INTERNAL_DETECTABLE`

The failure mode leaves a measurable trace inside the observed population.

#### `EXTERNAL_RECONCILIATION_REQUIRED`

The observed population cannot prove its own completeness; an external reference/invariant is required.

#### `STRUCTURALLY_UNVERIFIABLE`

Even admissible controls cannot establish the necessary completeness/representativeness.

This yields `COVERAGE_UNKNOWN` or `INSUFFICIENT` under D19.

## 2. FM-01 — Technical source availability failure

### Failure mode

A source or reference system becomes technically unavailable or partially accessible over part of the target period.

### Causal mechanism

- outage;
- endpoint unavailable;
- archive unavailable;
- missing version;
- interrupted acquisition;
- corruption;
- infrastructure transition.

### Threatened property

Temporal continuity of the observable population.

### Detectability

`INTERNAL_DETECTABLE`, with possible support from external source metadata/logs.

### Minimal observable unit

- source request;
- raw object;
- expected/received accession;
- reference snapshot.

### Minimal stratum

`SOURCE_AVAILABILITY_REGIME`, defined by actual source/acquisition regime boundaries. Never arbitrary calendar years by default.

### Required control

- continuity ledger;
- expected-vs-observed source availability;
- gap ledger;
- immutable provenance.

### Possible verdicts

- `SUFFICIENT`
- `PARTIAL_COVERAGE`
- `COVERAGE_UNKNOWN`
- `INSUFFICIENT`

## 3. FM-02 — Identity / security resolution failure

### Failure mode

Claim units exist, but their operational PIT identity cannot be reliably resolved to a security/listing/reference identity.

### Causal mechanism

- missing key;
- incomplete reference data;
- ambiguity;
- ticker/listing transition;
- insufficient temporal mapping;
- resolver unable to produce a unique identity.

### Threatened property

Ability to connect the claim population to required downstream observations without selection bias.

### Detectability

`INTERNAL_DETECTABLE` if the qualifying-filing denominator is itself certified.

### Minimal observable unit

`qualifying_filing` with explicit U2 resolution state.

### Minimal stratum

Only strata needed to detect structural concentration of resolution failures, such as a documented reference/listing regime. No sector/size strata by default.

### Required control

Frozen resolver + frozen mapping contract.

### Outputs

- `PIT_RESOLVED`
- `PIT_UNRESOLVED`
- `PIT_AMBIGUOUS`
- `REFERENCE_NOT_AVAILABLE`
- global rate;
- authorized causal-stratum rates;
- denominator-certainty state.

### Possible verdicts

- `SUFFICIENT`
- `CONCENTRATED_MISSINGNESS`
- `COVERAGE_UNKNOWN`
- `INSUFFICIENT`

## 4. FM-03 — Market-observation coverage failure

### Failure mode

The security is resolved, but required market observations are not sufficiently available or PIT-consistent.

### Causal mechanism

- missing series;
- truncated history;
- listing not covered;
- suspension;
- price-source absence;
- calendar incompatibility;
- unresolved listing/corporate-action transition.

### Threatened property

Economic measurability of the claim population.

### Detectability

`INTERNAL_DETECTABLE` at security/session level before D07 where the metric does not use an event.

### Minimal observable unit

- resolved security;
- security-session;
- listing interval.

### Minimal stratum

A stratum matching the actual coverage mechanism, for example market-data source regime, listing/reference regime or structural listing class where justified ex ante.

### Required control

- source availability contract;
- PIT listing/security lineage;
- session-calendar contract;
- market-data presence ledger.

### Possible verdicts

- `SUFFICIENT`
- `PARTIAL_COVERAGE`
- `CONCENTRATED_MISSINGNESS`
- `INSUFFICIENT`

No payoff or delisting treatment is decided here.

## 5. FM-04 — Denominator incompleteness

### Failure mode

The observed population can be incomplete even when every present object parses and resolves correctly.

Examples include filings never ingested, objects missing from the local index, an accession absent with no internal trace, a silently skipped period, or source objects whose existence the local system does not know.

### Causal mechanism

The system measures only what it has.

An incomplete population can therefore report 100% parse success, 100% resolution and 100% downstream coverage.

### Threatened property

**Denominator certainty.**

### Detectability

`EXTERNAL_RECONCILIATION_REQUIRED`

### Minimal observable unit

None is sufficient internally:

`MINIMAL_OBSERVABLE_UNIT = NONE`

### Minimal stratum

`NONE` for proving completeness.

A stratum may localize a discovered mismatch but cannot prove its initial absence.

### Required control

Reconciliation against an external invariant, for example an official SEC index, independently constructed manifest or externally documented expected totals where applicable.

The control compares:

`EXPECTED POPULATION`

to:

`OBSERVED POPULATION`.

It never reasons only about `OBSERVED POPULATION`.

### Possible verdicts

- `DENOMINATOR_CERTIFIED`
- `DENOMINATOR_PARTIAL`
- `COVERAGE_UNKNOWN`
- `INSUFFICIENT`

### Invariants

`COMPLETENESS_REQUIRES_EXTERNAL_INVARIANT`

`NO_INTERNAL_ZERO_AS_COMPLETENESS_PROOF`

Completeness cannot be proven from the captured population alone.

## 6. FM-05 — Parsing / ingestion integrity failure

### Failure mode

Objects exist and are acquired but their content is lost, misinterpreted or rejected during ingestion.

### Causal mechanism

- schema variant;
- parser incompatibility;
- required field absent;
- malformed document;
- destructive transform;
- fallback parser;
- silent coercion.

### Threatened property

Representativeness of the normalized population relative to acquired raw source objects.

### Detectability

`INTERNAL_DETECTABLE` provided raw objects are preserved.

### Minimal observable unit

`raw filing object -> parser result`

### Minimal stratum

`DOCUMENT_STRUCTURE_REGIME` only where variants are defined ex ante by public schema/documentation.

### Required control

- immutable raw preservation;
- parser outcome ledger;
- explicit parse-failure states;
- no silent dropping;
- raw→normalized reconciliation.

### Possible verdicts

- `SUFFICIENT`
- `STRUCTURAL_PARSE_GAP`
- `COVERAGE_UNKNOWN`
- `INSUFFICIENT`

## 7. FM-06 — Documentary / regulatory regime shift

### Failure mode

The observable population changes over time for institutional, regulatory or documentary reasons even when the technical pipeline works perfectly.

### Causal mechanism

- filing-obligation change;
- reporting-population change;
- format/schema change;
- required-field change;
- regulatory change in filing practice;
- institutional change affecting what becomes observable.

### Threatened property

Temporal comparability between the measured population and the conceptual claim population.

Technical coverage can be 100% while representativeness breaks.

### Detectability

Some consequences are internally measurable, but **regime boundaries must be defined ex ante from public documentary/regulatory information**.

### Minimal observable unit

- filing;
- schema/format metadata;
- regulatory-regime metadata.

### Minimal stratum

`DOCUMENTARY_REGIME`, defined before D05-A from public documentation. Not `YEAR` by convenience.

### Required control

- regulatory/documentary change register;
- frozen regime boundaries;
- regime-level coverage metrics where justified;
- comparability assessment.

### Possible verdicts

- `REGIME_COMPARABLE`
- `REGIME_HETEROGENEITY`
- `COVERAGE_UNKNOWN`
- `INSUFFICIENT`

No outcome frequency is inspected here.

## 8. FM-07 — Reference-regime drift

### Failure mode

The semantics or quality of the resolver's reference data changes through time.

### Causal mechanism

- provider change;
- version change;
- new keys;
- historical data removal;
- changed PIT semantics.

### Threatened property

Comparability of resolution quality through time.

### Detectability

`INTERNAL_DETECTABLE` with externally defined regime boundaries.

### Minimal observable unit

resolution attempt / reference snapshot.

### Minimal stratum

`REFERENCE_DATA_REGIME`, defined by documented source/version semantics.

### Required control

- versioned reference lineage;
- mapping-contract hash;
- regime identifier;
- no silent fallback migration.

### Possible verdicts

- `SUFFICIENT`
- `REGIME_DEPENDENT_COVERAGE`
- `COVERAGE_UNKNOWN`
- `INSUFFICIENT`

## 9. Cross-cutting rule — aggregate pass does not imply strata pass

Hidden concentrated missingness is **not** a separate failure mode.

For every `INTERNAL_DETECTABLE` failure mode, evaluation must occur at the authorized aggregate level and over each pre-authorized causal stratum.

A satisfactory global rate cannot automatically compensate for failure of a material causal stratum.

This rule creates no new failure mode, authorizes no new stratum and creates no new observation unit.

Only strata already justified by FM-01 through FM-07 may be used.

## 10. Deriving strata

A stratum enters D05-A only when the register demonstrates:

`failure mode`
→ `causal mechanism`
→ `why aggregate coverage can hide it`
→ `minimal stratum that exposes it`.

A stratum without this causal chain:

`OUT_OF_PASS`.

A crossing requires its own justification showing why each individual dimension is insufficient.

### Invariants

`FAILURE_MODES_BEFORE_VARIABLES`

`NO_FAILURE_MODE_NO_STRATUM`

`TEMPORAL_STRATA_FOLLOW_CAUSAL_REGIMES`

## 11. Internal controls vs external completeness controls

Internal controls ask:

> Among what we observed, what fraction is usable/resolved/covered?

External completeness controls ask:

> Did we observe everything we were supposed to observe?

These are logically distinct.

A 100% internal rate cannot answer the second question.

## 12. Coverage Requirement Generator principles

The register defines which failure modes must be confronted against coverage requirements.

It does **not** set the requirement based on observed D05-A values.

Separate:

`Coverage Requirement Generator`

from:

`Observed Coverage State`.

The requirement level is derived outside D05-A from power required at MEUE, estimand sensitivity to missingness, worst-case bias from concentrated missingness, D19 rules and pre-specified conservatism.

D05-A reports the actual state against that requirement.

### Invariants

`COVERAGE_REQUIREMENT_INDEPENDENCE`

`D05A_INFORMS_APPLICATION_NOT_LENIENCY`

`INSUFFICIENT_MUST_BE_REACHABLE`

A valid gate must structurally be able to conclude `INSUFFICIENT`.

## 13. Denominator uncertainty requirements

Distinguish:

### `DENOMINATOR_CERTIFIED`

The expected population is externally reconstructible under the frozen rule.

### `DENOMINATOR_PARTIAL`

External evidence bounds the possible missing denominator even if exact completeness is not proven.

### `DENOMINATOR_UNKNOWN`

The missing denominator cannot be bounded externally.

`DENOMINATOR_UNKNOWN` is not a weaker form of `DENOMINATOR_PARTIAL`. It is unbounded missingness.

For an authority-bearing population:

`ALLOWABLE_UNBOUNDED_DENOMINATOR_UNKNOWN = 0`.

A numerical tolerance only makes sense on a bounded quantity.

Therefore an unbounded denominator produces `COVERAGE_UNKNOWN` and, where required by the pre-frozen gate, `INSUFFICIENT`.

### Calendar fraction is not population fraction

A small fraction of uncertified calendar time does not imply a small fraction of missing population.

Any tolerance requires a certified denominator or an externally bounded missing denominator; otherwise `COVERAGE_UNKNOWN`.

### Invariants

`COVERAGE_UNKNOWN_IS_A_RESULT`

`ALLOWABLE_UNBOUNDED_DENOMINATOR_UNKNOWN = 0`

## 14. Verdict vocabulary

The register permits outputs including:

- `SUFFICIENT`
- `PARTIAL_COVERAGE`
- `CONCENTRATED_MISSINGNESS`
- `REGIME_HETEROGENEITY`
- `DENOMINATOR_CERTIFIED`
- `DENOMINATOR_PARTIAL`
- `COVERAGE_UNKNOWN`
- `INSUFFICIENT`

Intermediate labels never automatically imply acceptance.

`COVERAGE_UNKNOWN != SUFFICIENT`

and:

`absence of detected failure != proof of representativeness`.

## 15. Core invariants

- `FAILURE_MODES_BEFORE_VARIABLES`
- `NO_FAILURE_MODE_NO_STRATUM`
- `COMPLETENESS_REQUIRES_EXTERNAL_INVARIANT`
- `NO_INTERNAL_ZERO_AS_COMPLETENESS_PROOF`
- `TEMPORAL_STRATA_FOLLOW_CAUSAL_REGIMES`
- `COVERAGE_REQUIREMENT_INDEPENDENCE`
- `D05A_INFORMS_APPLICATION_NOT_LENIENCY`
- `INSUFFICIENT_MUST_BE_REACHABLE`
- `COVERAGE_UNKNOWN_IS_A_RESULT`
- `ALLOWABLE_UNBOUNDED_DENOMINATOR_UNKNOWN = 0`
