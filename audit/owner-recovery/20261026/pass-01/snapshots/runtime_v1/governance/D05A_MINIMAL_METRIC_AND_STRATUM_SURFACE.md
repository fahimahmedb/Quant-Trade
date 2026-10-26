# D05-A MINIMAL METRIC AND STRATUM SURFACE

**Status:** CLOSED / FROZEN SURFACE — ASTRA-CORRECTED  
**Authority:** Blue Team / Mission Control  
**Purpose:** define the smallest outcome-blind D05-A surface capable of feeding the frozen D05 generator without exploratory leakage.

## 1. Admission law

For Branch A and Branch B, an item is admitted only when it has both:

`NAMED_FAILURE_MODE + REQUIRED_DESTINATION_VERDICT`.

Otherwise:

`OUT_OF_PASS`.

Branch C is the explicit exception: claim density is admitted by the frozen qualification partition plus the claim-density verdict. No synthetic `FM-00` exists.

**Invariants**

- `NO_VERDICT_NO_METRIC`
- `CLAIM_DENSITY_IS_NOT_A_FAILURE_MODE`

## 2. Object classes and visibility

Authorized object classes:

- `METRIC`
- `STATUS_OR_REASON_CODE`
- `STRATUM`
- `SEALED_INTERNAL`

Visibility is part of the scientific surface:

- `VISIBLE`
- `DERIVED_VISIBLE`
- `NOT_VISIBLE`

A reason/status code is not automatically a stratum. A stratum exists only when an authorized routing/classification decision cannot be made without that partition.

**Invariants**

- `REASON_CODE_IS_NOT_STRATUM`
- `STRATUM_EXISTS_ONLY_FOR_DECISION`
- `VISIBILITY_IS_PART_OF_THE_SURFACE`

## 3. Two opposite conservative directions

D05-A contains two one-sided scientific protections.

### Bias / validity

If a loss cannot obtain causal clearance for availability-only treatment, route it to robustness treatment.

`UNKNOWN_BIAS_MECHANISM -> ADVERSE_ROBUSTNESS_TREATMENT`.

### Impossibility / rejection bound

If availability cannot yet be classified as structural or recoverable, include it favorably in the attainable ceiling.

`UNKNOWN_AVAILABILITY -> FAVORABLE_REJECTION_BOUND`.

These directions are intentionally opposite because they protect against different errors.

**Invariants**

- `CONSERVATIVE_ON_BIAS`
- `GENEROUS_ON_IMPOSSIBILITY_BOUND`
- `UNKNOWN_AVAILABILITY_IS_FAVORABLE_FOR_REJECTION_BOUND`
- `UNCLASSIFIED_AVAILABILITY_CANNOT_CREATE_IMPOSSIBILITY`

## 4. Branch C — claim density

Branch C has no strata.

Primitive visible counts:

- `QUALIFYING_COUNT`
- `NON_QUALIFYING_COUNT`
- `QUALIFICATION_INDECIDABLE_COUNT`

Derived visible count:

`QUALIFICATION_DECIDABLE_COUNT = QUALIFYING_COUNT + NON_QUALIFYING_COUNT`.

Terminal outputs:

- `N_OBS_CEILING_CLAIM_DENSITY`
- `CLAIM_DENSITY_VERDICT`

No segmentation of Branch C is authorized.

The favorable ceiling is a **global** upper-bound problem over compatible unresolved completions. It must not be implemented as `ALL_UNRESOLVED -> QUALIFYING` unless a proof establishes that this is an upper bound under the frozen state machine.

**Invariants**

- `FAVORABLE_CLAIM_COMPLETION_IS_NOT_ALL_QUALIFYING`
- `CLAIM_DENSITY_CEILING_REQUIRES_GLOBAL_MAXIMIZATION_OR_PROVEN_MAJORANT`

## 5. Branch A — denominator / join

The exact J0-J5 taxonomy is inherited from `D05_DENOMINATOR_RECONCILIATION_CONTRACT.md`:

- J0 `JOIN_OK_IN_SCOPE`
- J1 `EXPECTED_PAYLOAD_MISSING`
- J2 `PAYLOAD_INDEXED_OUT_OF_SCOPE`
- J3 `PAYLOAD_NOT_IN_INDEX_MANIFEST`
- J4 `PAYLOAD_ACCESSION_UNRESOLVED`
- J5 `ACCESSION_PAYLOAD_CONFLICT`

Authorized visible quantities include:

- `EXPECTED_COUNT`
- `DENOMINATOR_STATUS`
- J0-J5 counts
- `INGESTED_COUNT`

J0-J5 are statuses/reason codes, not strata.

## 6. Branch A — parsing

Authorized visible quantities:

- `PARSED_COUNT`
- `PARSE_FAILURE_COUNT`
- `PARSE_FAILURE_BY_REASON_CODE`
- `PARSE_RECOVERABLE_COUNT`
- `PARSE_STRUCTURAL_LOSS_COUNT`
- `PARSE_AVAILABILITY_UNCLASSIFIED_COUNT`

Only proven structural loss reduces `N_OBS_CEILING_AVAILABLE`.

Recoverable and unclassified availability are included favorably in the rejection ceiling and create governed conditions.

## 7. Minimal document-structure regime

`DOCUMENT_STRUCTURE_REGIME` exists only when parser availability classification cannot otherwise be made.

Current minimal registry:

- `DSR_BULK_FORM345`
- `DSR_EDGAR_OWNERSHIP_XML`
- `DSR_UNREGISTERED`

The regime may classify availability. It may not become an exploratory segmentation surface.

## 8. Branch A — PIT resolution

Authorized visible quantities:

- `PIT_RESOLVED_COUNT`
- `PIT_UNRESOLVED_COUNT`
- `PIT_AMBIGUOUS_COUNT`
- `RESOLUTION_RECOVERABLE_COUNT`
- `RESOLUTION_STRUCTURAL_LOSS_COUNT`
- `RESOLUTION_AVAILABILITY_UNCLASSIFIED_COUNT`

Unresolved/ambiguous objects may also enter Branch B robustness treatment when causal clearance is absent.

This is the same missing object viewed by two gates, not two different population units.

The implementation must preserve one canonical missing-object identity and may attach multiple gate-role/reason annotations without subtracting or weighting the same object twice inside one estimand.

**Invariants**

- `SAME_MISSING_OBJECT_MAY_FEED_MULTIPLE_GATES_WITHOUT_POPULATION_DUPLICATION`
- `ONE_MISSING_OBJECT_ONE_POPULATION_IDENTITY`

## 9. Branch A — market substrate

Only D07-independent market-substrate availability is authorized.

Visible quantities:

- `MARKET_SUBSTRATE_AVAILABLE_COUNT`
- `MARKET_SUBSTRATE_UNAVAILABLE_COUNT`
- `MARKET_RECOVERABLE_COUNT`
- `MARKET_STRUCTURAL_LOSS_COUNT`
- `MARKET_AVAILABILITY_UNCLASSIFIED_COUNT`

Signal-entry/exit performance is not a D05-A output.

Market/outcome unavailability may not retroactively erase filing/owner observations from the formation/re-arm state machine.

**Invariant:** `OUTCOME_UNAVAILABILITY_DOES_NOT_REWRITE_FORMATION_HISTORY`.

## 10. Availability state semantics

Every availability loss is one of:

### `STRUCTURAL`

Scientifically established unavailable under the frozen source/claim structure.

Treatment:

`EXCLUDE_FROM_N_OBS_CEILING_AVAILABLE`.

### `RECOVERABLE`

A preauthorized recovery path exists.

Treatment:

`INCLUDE_IN_N_OBS_CEILING_AVAILABLE + RECOVERY_CONDITION`.

### `UNCLASSIFIED`

Recoverable versus structural is unresolved.

Treatment:

`INCLUDE_IN_N_OBS_CEILING_AVAILABLE + AVAILABILITY_CLASSIFICATION_CONDITION`.

**Invariant:** `ONLY_PROVEN_STRUCTURAL_LOSS_REDUCES_REJECTION_CEILING`.

## 11. Authorized Branch-A classification strata

Only the following classifications are authorized, and only when needed for the availability decision:

- `SOURCE_AVAILABILITY_REGIME` — FM-01
- `DOCUMENT_STRUCTURE_REGIME` — FM-05
- `REFERENCE_DATA_REGIME` — FM-02/FM-07
- `MARKET_OBSERVABILITY_REGIME` — FM-03

No Cartesian products are authorized without a separately frozen causal proof that the individual strata are insufficient.

**Invariants**

- `BRANCH_A_STRATA_CLASSIFY_AVAILABILITY_NOT_DESCRIBE_POPULATION`
- `NO_CARTESIAN_EXPLORATION`

## 12. Unified open-condition ledger

`RECOVERY_CONDITIONS_OPEN` and `AVAILABILITY_CLASSIFICATION_CONDITIONS_OPEN` share one governed ledger.

Each condition records at minimum:

- `condition_id`
- `condition_type = RECOVERY | AVAILABILITY_CLASSIFICATION`
- object/accession scope
- originating failure/status
- `execution_owner`
- `mission_id`
- `discharge_certifier`
- `deadline_gate`
- current status
- proof artifact/hash
- originating D05-A pass
- whether the condition materially supports continuation

Required:

`execution_owner != discharge_certifier`.

For continuation-supporting conditions:

`deadline_gate = BEFORE_D07_SCIENTIFIC_FREEZE`.

Recovery is engineering/execution work. Availability classification is analysis/review work; it does not imply repair.

**Invariants**

- `OPEN_CONDITION_MUST_HAVE_OWNER_CERTIFIER_AND_DEADLINE`
- `CLASSIFICATION_DISCHARGE_IS_ANALYSIS_NOT_IMPLICIT_REPAIR`
- `NO_D07_AUTHORITY_ON_OPEN_RECOVERY_CONDITION`
- `NO_D07_AUTHORITY_ON_OPEN_AVAILABILITY_CLASSIFICATION`

## 13. Branch B — classification versus treatment

Three concepts are distinct:

### `BIAS_CAPABLE`

The frozen causal mechanism establishes that missingness can shift the estimand.

### `AVAILABILITY_ONLY`

Sufficient ex-ante structural evidence establishes non-differential availability loss.

### `ROUTED_B_FOR_LACK_OF_CAUSAL_CLEARANCE`

The mechanism has not been established as bias-capable, but there is insufficient causal evidence to grant Branch-A-only treatment.

This is a conservative treatment state, not a causal claim.

**Invariants**

- `NO_CAUSAL_CLEARANCE_IMPLIES_ROBUSTNESS_TREATMENT`
- `ROUTED_B_FOR_LACK_OF_CAUSAL_CLEARANCE_IS_NOT_BIAS_CLASSIFICATION`

## 14. No concentration threshold in this lineage

This lineage does not instantiate:

- `B_route`
- `m_star`
- concentration percentages
- concentration-routing strata

Losses denied causal clearance receive D19 robustness treatment directly.

Therefore the earlier state `LOSS_MECHANISM_UNCLASSIFIED` has no remaining routing function and is not part of the minimal surface.

There is no `B04` metric for it.

## 15. Branch B authorized surface

Visible quantities/statuses:

- `QUALIFICATION_INDECIDABLE_COUNT`
- `BIAS_CAPABLE_MISSING_COUNT_BY_REASON`
- `ROUTED_B_FOR_LACK_OF_CAUSAL_CLEARANCE_COUNT_BY_REASON`
- `BIAS_RULE_STATE`

Until the D19 adverse-treatment mechanics resolve to a hash-addressable specification, the authority-bearing state is:

`D19_ADVERSE_TREATMENT_SPEC_PENDING`.

Only after that specification exists may the surface emit:

`BIAS_RULE_READY_PENDING_OUTCOME_APPLICATION`.

**Invariant:** `D19_DECISION_NAME_IS_NOT_ADVERSE_TREATMENT_SPEC`.

## 16. Conservative-routing anti-rescue

If robustness treatment later produces `INSUFFICIENT` or wide bounds, the same lineage may not inspect concentration, invent `B_route`, introduce `m_star`, create new routing strata or reclassify losses as availability-only.

Such refinement requires a new scientific lineage with a pre-frozen routing contract.

**Invariants**

- `CONSERVATIVE_ROUTING_FAILURE_DOES_NOT_AUTHORIZE_POST_HOC_RECLASSIFICATION`
- `SIMPLICITY_MAY_SPEND_POWER_NOT_VALIDITY`

## 17. Scientific unit-conversion gate

The surface spans several units that must never be silently conflated:

- EDGAR accession / submission;
- reporting-owner CIK;
- qualifying owner observation;
- issuer/security identity;
- formation-session state;
- threshold crossing;
- market/outcome availability record.

Every cross-unit conversion used by a ceiling must resolve to explicit deterministic keys and multiplicity rules.

Examples:

- `1 accession` may contain multiple reporting owners and transaction rows;
- owner identity is reporting-owner CIK, not fuzzy natural-person merge;
- a crossing is derived from frozen formation state and is not equivalent to a filing count;
- outcome availability is downstream of crossing formation.

Until the conversion contract is hash-addressable, source-stage counts may be recorded but final event ceilings are not consumable scientific authority.

**Invariant:** `SCIENTIFIC_UNIT_CONVERSION_REQUIRES_EXPLICIT_KEYS`.

## 18. Sealed envelope surface

The following may be computed mechanically but remain `NOT_VISIBLE`:

- `C_PREVIOUS`
- `C_NEXT`
- `O1_ARGMAX`
- O1-specific crossing identities
- O2-specific trigger identities
- unnecessary cell-level routing details

Visible authority is limited to the scalar envelope outputs already allowed by the generator.

**Invariants**

- `ARGMAX_IS_EMBARGOED`
- `ENVELOPE_OUTPUT_ONLY`

## 19. Terminal D05-A surface

Visible terminal quantities include:

- `N_RAW_REQUIRED_FLOOR` or explicit unresolved state
- `N_OBS_CEILING_CLAIM_DENSITY`
- `N_OBS_CEILING_AVAILABLE`
- `POWER_AVAILABILITY_VERDICT`
- `RECOVERY_CONDITIONS_OPEN_COUNT`
- `AVAILABILITY_CLASSIFICATION_CONDITIONS_OPEN_COUNT`
- unified `D05A_CONDITION_LEDGER`

`N_RAW_REQUIRED_FLOOR` and both ceilings are all measured in **raw statistical-observation count**. No authority-bearing D05 theorem compares a raw ceiling to an effective-sample scalar.

No independent stage-level scientific q threshold is authorized.

**Invariants**

- `RAW_CEILING_COMPARES_ONLY_TO_RAW_REQUIREMENT`
- `NO_UNPROVEN_NEFF_TO_NRAW_BRIDGE`

## 20. Power-floor dependency and visibility firewall

D05 consumes the raw requirement floor. D05 does not choose it.

`D05_CONSUMES_POWER_FLOOR_D05_DOES_NOT_CHOOSE_IT`.

Before any human-visible ceiling value is published, the complete upstream recipe for deriving `N_RAW_REQUIRED_FLOOR` must already be frozen/hash-addressable, or a mechanically proven access separation must prevent every actor able to modify that recipe from seeing the ceiling.

The numerical floor may remain unresolved because external measurements are not yet acquired, but its derivation rules may not remain designable after ceiling visibility.

**Invariants**

- `POWER_FLOOR_RECIPE_PRECEDES_D05_CEILING_VISIBILITY`
- `NO_CEILING_INFORMED_POWER_FLOOR_DESIGN`

## 21. Explicit OUT_OF_PASS examples

Unless separately frozen before execution:

- sector
- market-cap bucket
- issuer ranking
- arbitrary calendar-year tables
- filing-count quantiles
- transaction-value distributions
- insider-title breakdowns
- alternative resolver outputs
- O1-specific event counts
- signal/exposure/overlap statistics outside the sealed envelope
- outcome data
- return data
- benchmark performance

## 22. Minimality tests

### Metric

If removing the quantity leaves every authorized D05-A verdict calculable, it is `OUT_OF_PASS`.

### Stratum

If routing/classification remains decidable without the partition, it is `OUT_OF_PASS`.

### Reason/status code

If it is unnecessary for lineage, causal treatment, recovery or condition discharge, it is `OUT_OF_PASS`.

## 23. Core invariants

- `NO_VERDICT_NO_METRIC`
- `CLAIM_DENSITY_IS_NOT_A_FAILURE_MODE`
- `REASON_CODE_IS_NOT_STRATUM`
- `STRATUM_EXISTS_ONLY_FOR_DECISION`
- `CONSERVATIVE_ON_BIAS`
- `GENEROUS_ON_IMPOSSIBILITY_BOUND`
- `UNKNOWN_AVAILABILITY_IS_FAVORABLE_FOR_REJECTION_BOUND`
- `ONLY_PROVEN_STRUCTURAL_LOSS_REDUCES_REJECTION_CEILING`
- `SAME_MISSING_OBJECT_MAY_FEED_MULTIPLE_GATES_WITHOUT_POPULATION_DUPLICATION`
- `ONE_MISSING_OBJECT_ONE_POPULATION_IDENTITY`
- `NO_CAUSAL_CLEARANCE_IMPLIES_ROBUSTNESS_TREATMENT`
- `ROUTED_B_FOR_LACK_OF_CAUSAL_CLEARANCE_IS_NOT_BIAS_CLASSIFICATION`
- `CONSERVATIVE_ROUTING_FAILURE_DOES_NOT_AUTHORIZE_POST_HOC_RECLASSIFICATION`
- `SIMPLICITY_MAY_SPEND_POWER_NOT_VALIDITY`
- `NO_CARTESIAN_EXPLORATION`
- `FAVORABLE_CLAIM_COMPLETION_IS_NOT_ALL_QUALIFYING`
- `SCIENTIFIC_UNIT_CONVERSION_REQUIRES_EXPLICIT_KEYS`
- `RAW_CEILING_COMPARES_ONLY_TO_RAW_REQUIREMENT`
- `POWER_FLOOR_RECIPE_PRECEDES_D05_CEILING_VISIBILITY`
- `D05_CONSUMES_POWER_FLOOR_D05_DOES_NOT_CHOOSE_IT`
