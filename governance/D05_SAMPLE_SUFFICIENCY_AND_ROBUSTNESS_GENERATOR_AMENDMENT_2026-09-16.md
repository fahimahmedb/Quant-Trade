# D05 SAMPLE SUFFICIENCY AND ROBUSTNESS GENERATOR — BLUE AMENDMENT 2026-09-16

**Status:** FROZEN AMENDMENT  
**Authority:** Blue Team / Mission Control  
**Supersedes:** conflicting language in §§15–18, §§24–28, §31–34 of `D05_SAMPLE_SUFFICIENCY_AND_ROBUSTNESS_GENERATOR.md` where this amendment is more specific.

## 1. Purpose

This amendment closes the residual ambiguity in Branch A availability classification and Branch B routing without introducing a numeric concentration threshold.

## 2. Two opposite conservative directions

### Bias / validity

When causal clearance for availability-only treatment is absent:

`UNKNOWN_BIAS_MECHANISM -> ADVERSE_ROBUSTNESS_TREATMENT`.

This protects against false scientific validity.

### Impossibility / rejection bound

When availability is not yet classifiable as structural or recoverable:

`UNKNOWN_AVAILABILITY -> FAVORABLE_REJECTION_BOUND`.

This protects against a false impossibility verdict.

**Invariants**

- `CONSERVATIVE_ON_BIAS`
- `GENEROUS_ON_IMPOSSIBILITY_BOUND`
- `UNKNOWN_AVAILABILITY_IS_FAVORABLE_FOR_REJECTION_BOUND`

## 3. Availability classification

Every Branch-A availability loss is one of:

- `STRUCTURAL`
- `RECOVERABLE`
- `UNCLASSIFIED`

Only proven structural loss may reduce `N_obs_ceiling_available`.

`RECOVERABLE` and `UNCLASSIFIED` objects remain included favorably in the rejection ceiling.

The first creates a recovery condition. The second creates an availability-classification condition.

**Invariants**

- `ONLY_PROVEN_STRUCTURAL_LOSS_REDUCES_REJECTION_CEILING`
- `UNCLASSIFIED_AVAILABILITY_CANNOT_CREATE_IMPOSSIBILITY`

## 4. Unified condition ledger

Recovery and availability-classification conditions use one governed ledger with:

- `condition_id`
- `condition_type = RECOVERY | AVAILABILITY_CLASSIFICATION`
- object/accession
- failure/status
- permitted recovery/classification path
- `execution_owner`
- `mission_id`
- `discharge_certifier`
- `deadline_gate`
- status
- proof artifact/hash
- materiality / continuation dependence

Required:

`execution_owner != discharge_certifier`.

For any condition supporting progression:

`deadline_gate = BEFORE_D07_SCIENTIFIC_FREEZE`.

Recovery is engineering/execution work. Availability classification is analysis/review work and does not imply repair.

**Invariants**

- `OPEN_CONDITION_MUST_HAVE_OWNER_CERTIFIER_AND_DEADLINE`
- `CLASSIFICATION_DISCHARGE_IS_ANALYSIS_NOT_IMPLICIT_REPAIR`
- `NO_D07_AUTHORITY_ON_OPEN_RECOVERY_CONDITION`
- `NO_D07_AUTHORITY_ON_OPEN_AVAILABILITY_CLASSIFICATION`

## 5. Branch B treatment states

The earlier state `LOSS_MECHANISM_UNCLASSIFIED` no longer blocks routing.

Use:

### `BIAS_CAPABLE`

The frozen causal mechanism establishes that the missingness can shift the estimand.

### `AVAILABILITY_ONLY`

Ex-ante structural evidence establishes non-differential availability loss.

### `ROUTED_B_FOR_LACK_OF_CAUSAL_CLEARANCE`

Quant lacks sufficient causal evidence to grant availability-only treatment.

This is a conservative treatment state, not a causal classification.

**Invariants**

- `NO_CAUSAL_CLEARANCE_IMPLIES_ROBUSTNESS_TREATMENT`
- `ROUTED_B_FOR_LACK_OF_CAUSAL_CLEARANCE_IS_NOT_BIAS_CLASSIFICATION`

## 6. No concentration threshold in this lineage

This lineage does not instantiate:

- `B_route`
- `m_star`
- concentration percentages
- concentration-routing strata

A loss denied causal clearance is routed directly to the frozen D19 adverse-treatment framework.

The old concentration-routing requirement is therefore removed for this lineage.

`NONDIFFERENTIAL_MISSINGNESS_IS_NOT_BIAS_BY_MAGNITUDE` remains intact: magnitude alone never causally classifies missingness as bias.

## 7. Anti-rescue

If conservative robustness routing later produces `INSUFFICIENT` or wider bounds, the current lineage may not respond by inspecting concentration, inventing `B_route`, adding `m_star`, creating new routing strata or reclassifying losses as availability-only.

That requires a new scientific lineage with a pre-frozen routing contract.

**Invariants**

- `CONSERVATIVE_ROUTING_FAILURE_DOES_NOT_AUTHORIZE_POST_HOC_RECLASSIFICATION`
- `SIMPLICITY_MAY_SPEND_POWER_NOT_VALIDITY`

## 8. Same object, multiple gates

A missing object may reduce attainable information in Branch A and also belong to the robustness missing set in Branch B.

Example: unresolved or ambiguous PIT resolution.

This is not population duplication.

It is one scientific object viewed by two distinct gates.

**Invariant:** `SAME_MISSING_OBJECT_MAY_FEED_MULTIPLE_GATES_WITHOUT_POPULATION_DUPLICATION`

## 9. Power-floor unresolved state

`N_eff_required_floor` is consumed from D09/D08 authority.

D05 does not choose or tune it.

If:

`POWER_REQUIREMENT_UNRESOLVED`

then D05-A may still produce:

- denominator state
- qualification partition
- availability classifications
- missing sets
- `N_obs_ceiling_claim_density`
- `N_obs_ceiling_available`
- condition ledger

but may not issue:

- `CLAIM_POPULATION_TOO_SPARSE_FOR_REQUIRED_POWER`
- `POWER_IMPOSSIBLE_DUE_TO_AVAILABILITY`

until an authority-bearing floor exists.

**Invariant:** `D05_CONSUMES_POWER_FLOOR_D05_DOES_NOT_CHOOSE_IT`

## 10. Verdict precedence amendment

After denominator authority:

- if no authority-bearing power floor exists, report `POWER_REQUIREMENT_UNRESOLVED` with the computed D05-A substrate and ceilings;
- otherwise apply the existing claim-density and availability impossibility comparisons.

No positive power authorization is produced before D07/D08 finalization.

## 11. Core amendment invariants

- `CONSERVATIVE_ON_BIAS`
- `GENEROUS_ON_IMPOSSIBILITY_BOUND`
- `UNKNOWN_AVAILABILITY_IS_FAVORABLE_FOR_REJECTION_BOUND`
- `ONLY_PROVEN_STRUCTURAL_LOSS_REDUCES_REJECTION_CEILING`
- `OPEN_CONDITION_MUST_HAVE_OWNER_CERTIFIER_AND_DEADLINE`
- `NO_CAUSAL_CLEARANCE_IMPLIES_ROBUSTNESS_TREATMENT`
- `ROUTED_B_FOR_LACK_OF_CAUSAL_CLEARANCE_IS_NOT_BIAS_CLASSIFICATION`
- `CONSERVATIVE_ROUTING_FAILURE_DOES_NOT_AUTHORIZE_POST_HOC_RECLASSIFICATION`
- `SAME_MISSING_OBJECT_MAY_FEED_MULTIPLE_GATES_WITHOUT_POPULATION_DUPLICATION`
- `D05_CONSUMES_POWER_FLOOR_D05_DOES_NOT_CHOOSE_IT`
