# D05-A UNIT AND CEILING CONVERSION CONTRACT

**Status:** FROZEN CONVERSION CONTRACT — NUMERIC EXECUTION PENDING  
**Authority:** Blue Team / Mission Control  
**Purpose:** make every conversion from SEC submissions to potential Form-4 threshold-crossing observations explicit so D05 raw ceilings cannot mix incompatible scientific units.

## 1. Why this contract exists

D05 uses several distinct units:

- SEC accession/submission;
- reporting-owner identity;
- qualifying owner observation;
- issuer formation-session state;
- threshold crossing;
- market/outcome availability record.

No count or ratio may silently treat one unit as another.

**Invariant:** `SCIENTIFIC_UNIT_CONVERSION_REQUIRES_EXPLICIT_KEYS`.

## 2. Canonical keys

### 2.1 Submission key

`SUBMISSION_KEY = ACCESSION_NUMBER`.

One accession is one SEC submission in the denominator contract.

It is not one owner, one transaction, or one statistical observation.

### 2.2 Reporting-owner identity

`OWNER_KEY = REPORTING_OWNER_CIK`.

No fuzzy natural-person merge is authorized.

### 2.3 Issuer identity

`ISSUER_KEY = ISSUER_CIK`.

Security/ticker mapping is downstream and point-in-time governed; it does not redefine issuer formation history.

### 2.4 Qualifying owner-observation key

For formation counting, the logical qualifying unit is an issuer/owner/public-observation fact derived under the frozen Form-4 qualification rules.

At minimum its identity binds:

`(ACCESSION_NUMBER, ISSUER_CIK, REPORTING_OWNER_CIK, PUBLIC_OBSERVABILITY_FACTS)`.

Multiple qualifying transaction rows for the same reporting owner inside one filing do not create multiple distinct insiders.

Multiple filings by the same owner may create multiple source observations but owner distinctness inside the trailing window is determined by `REPORTING_OWNER_CIK`.

## 3. Qualification is not accession counting

A submission may contain:

- multiple reporting owners;
- multiple transaction rows;
- qualifying and non-qualifying rows;
- information insufficient to determine qualification.

Therefore:

`EXPECTED_ACCESSION_COUNT`

must never be used directly as:

`QUALIFYING_OWNER_COUNT`

or:

`THRESHOLD_CROSSING_COUNT`.

**Invariant:** `ACCESSION_COUNT_IS_NOT_EVENT_COUNT`.

## 4. Formation state

For each issuer and formation session, the frozen state machine maintains the set of distinct qualifying reporting-owner CIKs inside the trailing ten regular-session window.

Closed semantics remain:

`WINDOW_EXPIRY_PRECEDES_SESSION_ADDITIONS`.

A threshold crossing is a derived state transition:

`distinct_owner_count < 2 -> distinct_owner_count >= 2`.

After a crossing, no new signal occurs until the state rearms below 2 according to the frozen expiry semantics.

The statistical raw observation ceiling counts threshold crossings under the separately frozen O1/O2/O3/O4 envelope rules. It does not count filings or owners directly.

**Invariant:** `CROSSING_IS_DERIVED_FROM_FORMATION_STATE_NOT_SOURCE_ROW_COUNT`.

## 5. Market/outcome availability does not rewrite formation

Market/security resolution and outcome availability are downstream properties.

If a filing/owner observation legitimately belongs to the frozen formation state but later lacks market/outcome coverage, that downstream absence may affect availability or robustness treatment.

It may not retroactively erase the observation from formation/re-arm history merely to simplify the statistical sample.

**Invariant:** `OUTCOME_UNAVAILABILITY_DOES_NOT_REWRITE_FORMATION_HISTORY`.

## 6. Same object across gates

Where one source object produces both an availability limitation and robustness concern, use one canonical object identity with multiple role/reason annotations.

Do not create duplicate population units because the object feeds both Branch A and Branch B.

**Invariants**

- `SAME_MISSING_OBJECT_MAY_FEED_MULTIPLE_GATES_WITHOUT_POPULATION_DUPLICATION`
- `ONE_MISSING_OBJECT_ONE_POPULATION_IDENTITY`

## 7. Unresolved qualification and ceiling completion

D05 claim-density ceilings must account for objects whose eventual qualifying owner content is unresolved.

A favorable ceiling is not computed by mechanically declaring every unresolved object qualifying.

Reasons include:

- unresolved objects may duplicate an owner already active in the window;
- added qualifying observations can delay re-arm and reduce later crossings;
- a missing/unparsed accession may have unknown owner multiplicity.

The authority-bearing ceiling must therefore use either:

1. exact global maximization over all completions compatible with known source facts and frozen identity rules; or
2. an analytic majorant proven never to understate the true admissible maximum.

**Invariants**

- `FAVORABLE_CLAIM_COMPLETION_IS_NOT_ALL_QUALIFYING`
- `CLAIM_DENSITY_CEILING_REQUIRES_GLOBAL_MAXIMIZATION_OR_PROVEN_MAJORANT`

## 8. Unknown owner multiplicity

If an unresolved source object has no defensible finite upper bound on the number/identity of reporting owners it may contain, the implementation must not invent a numeric multiplicity cap.

Allowed states are:

- resolve the object through an authorized path;
- derive a finite bound from a separately frozen source/schema rule;
- or emit `CLAIM_DENSITY_CEILING_UNBOUNDED_OR_UNRESOLVED` for the affected ceiling construction.

A numerically convenient owner cap may not be chosen after observing D05 counts.

**Invariant:** `NO_INVENTED_OWNER_MULTIPLICITY_CAP`.

## 9. Required lineage table for implementation

Every authority-bearing ceiling implementation must be able to reconstruct a lineage table containing, where applicable:

- `accession_number`;
- `issuer_cik`;
- `reporting_owner_cik` or explicit unresolved-owner state;
- qualification state;
- qualification reason/proof lineage;
- EDGAR/public-observability source facts;
- O1 formation-session attachment internal to the sealed envelope;
- formation-state contribution identity;
- threshold-crossing identity internal to the sealed envelope;
- downstream security-resolution state;
- downstream market/outcome-availability state;
- Branch-A availability class;
- Branch-B treatment role where applicable.

Design-sensitive O1/O2/crossing identities remain sealed from the D07 decision surface as required by the envelope contract.

## 10. Ratios and cumulative counts

Every reported ratio must name numerator and denominator units explicitly.

Examples:

`PARSED_SUBMISSIONS / EXPECTED_SUBMISSIONS`

is valid when both are accession/submission units.

A ratio such as:

`QUALIFYING_OWNERS / EXPECTED_SUBMISSIONS`

is not a generic coverage rate and must not be interpreted as one without an explicitly authorized scientific meaning.

**Invariant:** `RATIO_NUMERATOR_AND_DENOMINATOR_DECLARE_UNIT`.

## 11. Authority gate

Before final D05 event ceilings receive scientific authority, implementation proof must show:

- all cross-unit mappings use the keys/rules above;
- no accession-count shortcut substitutes for crossing derivation;
- unresolved owner multiplicity is handled by exact completion, proven majorant, or explicit unresolved state;
- downstream outcome availability does not modify formation history;
- design-sensitive identities remain sealed.

Failure of this proof blocks ceiling authority but does not invalidate denominator/source-stage counts measured in their own declared units.

## 12. Core invariants

- `SCIENTIFIC_UNIT_CONVERSION_REQUIRES_EXPLICIT_KEYS`
- `ACCESSION_COUNT_IS_NOT_EVENT_COUNT`
- `CROSSING_IS_DERIVED_FROM_FORMATION_STATE_NOT_SOURCE_ROW_COUNT`
- `OUTCOME_UNAVAILABILITY_DOES_NOT_REWRITE_FORMATION_HISTORY`
- `ONE_MISSING_OBJECT_ONE_POPULATION_IDENTITY`
- `FAVORABLE_CLAIM_COMPLETION_IS_NOT_ALL_QUALIFYING`
- `CLAIM_DENSITY_CEILING_REQUIRES_GLOBAL_MAXIMIZATION_OR_PROVEN_MAJORANT`
- `NO_INVENTED_OWNER_MULTIPLICITY_CAP`
- `RATIO_NUMERATOR_AND_DENOMINATOR_DECLARE_UNIT`
