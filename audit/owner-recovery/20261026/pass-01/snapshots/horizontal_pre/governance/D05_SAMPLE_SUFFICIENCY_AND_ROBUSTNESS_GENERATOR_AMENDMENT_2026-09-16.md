# D05 SAMPLE SUFFICIENCY AND ROBUSTNESS GENERATOR — BLUE AMENDMENT 2026-09-16

**Status:** FROZEN AMENDMENT — ASTRA-CORRECTED  
**Authority:** Blue Team / Mission Control  
**Supersedes:** conflicting language in §§15–18, §§23–34 of `D05_SAMPLE_SUFFICIENCY_AND_ROBUSTNESS_GENERATOR.md` where this amendment is more specific. In particular, this amendment supersedes any use of `N_eff_required_floor` against a raw observation ceiling and any reliance on `N_eff <= N_raw_observations` for early impossibility.

## 1. Purpose

This amendment closes Branch-A availability classification, Branch-B routing, and the one-sided pre-D07 power-impossibility theorem without introducing a numeric concentration threshold.

Astra adversarial review identified a fatal unit mismatch in the prior theorem: a raw observation count is not in general an upper bound on effective information when admissible negative dependence can increase precision. The corrected gate therefore compares **raw observations to a raw-observation requirement**, with dependence handled inside the power function exactly once.

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

A loss denied causal clearance is routed directly to the D19 adverse-treatment framework.

The old concentration-routing requirement is removed for this lineage.

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

This is not population duplication. The implementation must maintain one canonical missing-object identity and allow multiple gate-role annotations; it must not subtract or weight the same object twice inside one estimand merely because it has multiple failure reasons.

**Invariants**

- `SAME_MISSING_OBJECT_MAY_FEED_MULTIPLE_GATES_WITHOUT_POPULATION_DUPLICATION`
- `ONE_MISSING_OBJECT_ONE_POPULATION_IDENTITY`

## 9. Fatal-theorem repair — raw requirement, not effective-sample comparison

The prior implication relied on:

`N_eff <= N_raw_observations`.

That statement is not generally valid under admissible negative dependence. It is therefore **not authority-bearing** for D05 early rejection.

The pre-D07 gate now uses one common unit on both sides: raw statistical observations.

For a fully specified admissible statistical scenario `theta`, define:

`N_raw_required(theta) = min { n : Power_n(MEUE(theta), Sigma_n(theta), T(theta), alpha, target_power) >= target_power }`.

Dependence, variance structure, estimator/test behavior and any admissible precision gain or loss are represented inside `Power_n(...)` / `Sigma_n(theta)` exactly once.

The one-sided favorable requirement is:

`N_RAW_REQUIRED_FLOOR = inf_{theta in THETA_POWER_FLOOR} N_raw_required(theta)`.

If no defensible authority-bearing value can be produced:

`POWER_REQUIREMENT_UNRESOLVED`.

D05 may never recreate an effective-sample proxy and compare it to a raw ceiling unless a separate theorem proves unit compatibility.

**Invariants**

- `RAW_CEILING_COMPARES_ONLY_TO_RAW_REQUIREMENT`
- `DEPENDENCE_ENTERS_POWER_FLOOR_EXACTLY_ONCE`
- `NO_UNPROVEN_NEFF_TO_NRAW_BRIDGE`

## 10. Corrected one-sided verdict theorem

Maintain the existing favorable raw ceilings:

- `N_obs_ceiling_claim_density`
- `N_obs_ceiling_available`

When an authority-bearing `N_RAW_REQUIRED_FLOOR` exists:

### Case 1 — intrinsic density impossible

If:

`N_obs_ceiling_claim_density < N_RAW_REQUIRED_FLOOR`

then:

`CLAIM_POPULATION_TOO_SPARSE_FOR_REQUIRED_POWER`.

### Case 2 — available substrate impossible

If claim density can reach the floor but:

`N_obs_ceiling_available < N_RAW_REQUIRED_FLOOR`

then:

`POWER_IMPOSSIBLE_DUE_TO_AVAILABILITY`.

### Case 3 — impossibility not established

If:

`N_obs_ceiling_available >= N_RAW_REQUIRED_FLOOR`

then:

`POWER_UNDETERMINED_PENDING_D07`.

The inverse remains invalid: ceiling above the raw requirement floor does not establish positive power sufficiency.

**Invariant:** `UPPER_BOUND_PASS_IS_NOT_POWER_PASS`.

## 11. Favorable claim completion is global, not pointwise

For `N_obs_ceiling_claim_density`, unresolved claim membership must be completed in the way that maximizes the authorized crossing-count ceiling subject to all frozen claim/state-machine constraints.

It is **not** generally valid to implement favorable completion as:

`ALL_UNRESOLVED -> QUALIFYING`.

Additional qualifying observations can keep a signal armed across later sessions and reduce future re-arm/crossing count.

The ceiling implementation must therefore use either:

1. exact global maximization over all compatible unresolved completions; or
2. a looser analytic majorant proven never to understate the true admissible maximum.

**Invariants**

- `FAVORABLE_CLAIM_COMPLETION_IS_NOT_ALL_QUALIFYING`
- `CLAIM_DENSITY_CEILING_REQUIRES_GLOBAL_MAXIMIZATION_OR_PROVEN_MAJORANT`

## 12. Unit-conversion authority

D05 ceilings consume several scientific units: accession/submission, reporting-owner CIK, qualifying observation, issuer/security identity, formation-session state and threshold crossing.

No implementation may divide, aggregate or convert across these units without an explicit deterministic key/mapping contract.

In particular:

- `1 accession != 1 owner`;
- a filing may contain multiple reporting owners / transaction rows;
- missing outcome/market coverage never retroactively deletes a filing or owner observation from the frozen formation/re-arm state machine;
- crossing identity and market/outcome availability remain separate dimensions.

Until the required mapping contract is hash-addressable, D05-A may count source-stage objects but its final event ceilings are not consumable authority.

**Invariants**

- `SCIENTIFIC_UNIT_CONVERSION_REQUIRES_EXPLICIT_KEYS`
- `OUTCOME_UNAVAILABILITY_DOES_NOT_REWRITE_FORMATION_HISTORY`

## 13. D19 authority state

Branch-B routing may be computed outcome-blind, but the label `BIAS_RULE_READY_PENDING_OUTCOME_APPLICATION` is authority-bearing only after D19 resolves to a hash-addressable adverse-treatment specification defining at minimum:

- admissible missing-outcome completions / support;
- treatment of qualification-indecidable units across pre-parse and post-parse states;
- identified/robustness-bound construction;
- primary-verdict application;
- any boundedness assumptions.

Until then use:

`D19_ADVERSE_TREATMENT_SPEC_PENDING`.

This does not reopen the D19 decision. It records `DECIDED_NOT_YET_CONSUMABLE_AUTHORITY`.

**Invariant:** `D19_DECISION_NAME_IS_NOT_ADVERSE_TREATMENT_SPEC`.

## 14. Floor-recipe contamination firewall

D05 outcome blindness is not sufficient by itself. A visible D05 ceiling can contaminate subsequent construction of the power floor even without any return outcomes.

Therefore, before any human-visible D05-A ceiling value is published, the complete **derivation recipe** for `N_RAW_REQUIRED_FLOOR` must already be frozen/hash-addressable, including as applicable:

- D09 delta / MEUE mapping rule;
- deployment-domain rule;
- alpha and target-power policy;
- floor transform admission rule;
- power-function family / estimator-test family used for the floor;
- external source admission/search/stop rule;
- extraction and source-uncertainty rule;
- horizon-scaling rule if any;
- numerical-infimum certification rule.

The final numerical floor may still depend on external source measurements acquired later, but the recipe may not be redesigned after a ceiling is visible.

Alternative: a mechanically proven access separation may allow D05 computation to occur earlier, but no actor authorized to modify the floor recipe may receive ceiling values before the recipe freeze.

**Invariants**

- `POWER_FLOOR_RECIPE_PRECEDES_D05_CEILING_VISIBILITY`
- `NO_CEILING_INFORMED_POWER_FLOOR_DESIGN`

## 15. Power-floor unresolved state

D05 consumes `N_RAW_REQUIRED_FLOOR` from upstream D09/D08 authority. D05 does not choose or tune it.

If:

`POWER_REQUIREMENT_UNRESOLVED`

D05-A may execute mechanically and produce its non-power substrate internally, but human-visible ceiling publication is governed by §14.

No definitive power-impossibility ELE may issue until an authority-bearing raw requirement floor exists.

**Invariant:** `D05_CONSUMES_POWER_FLOOR_D05_DOES_NOT_CHOOSE_IT`.

## 16. Verdict precedence amendment

After denominator authority:

1. if `N_RAW_REQUIRED_FLOOR` is unresolved, report `POWER_REQUIREMENT_UNRESOLVED`; no power-impossibility ELE;
2. otherwise evaluate the corrected raw-count comparisons in §10;
3. Branch-B robustness authority remains separately blocked until the D19 adverse-treatment specification is consumable.

No positive power authorization is produced before final D07/D08 inference.

## 17. Core amendment invariants

- `CONSERVATIVE_ON_BIAS`
- `GENEROUS_ON_IMPOSSIBILITY_BOUND`
- `UNKNOWN_AVAILABILITY_IS_FAVORABLE_FOR_REJECTION_BOUND`
- `ONLY_PROVEN_STRUCTURAL_LOSS_REDUCES_REJECTION_CEILING`
- `OPEN_CONDITION_MUST_HAVE_OWNER_CERTIFIER_AND_DEADLINE`
- `NO_CAUSAL_CLEARANCE_IMPLIES_ROBUSTNESS_TREATMENT`
- `ROUTED_B_FOR_LACK_OF_CAUSAL_CLEARANCE_IS_NOT_BIAS_CLASSIFICATION`
- `CONSERVATIVE_ROUTING_FAILURE_DOES_NOT_AUTHORIZE_POST_HOC_RECLASSIFICATION`
- `SAME_MISSING_OBJECT_MAY_FEED_MULTIPLE_GATES_WITHOUT_POPULATION_DUPLICATION`
- `RAW_CEILING_COMPARES_ONLY_TO_RAW_REQUIREMENT`
- `DEPENDENCE_ENTERS_POWER_FLOOR_EXACTLY_ONCE`
- `NO_UNPROVEN_NEFF_TO_NRAW_BRIDGE`
- `FAVORABLE_CLAIM_COMPLETION_IS_NOT_ALL_QUALIFYING`
- `CLAIM_DENSITY_CEILING_REQUIRES_GLOBAL_MAXIMIZATION_OR_PROVEN_MAJORANT`
- `SCIENTIFIC_UNIT_CONVERSION_REQUIRES_EXPLICIT_KEYS`
- `POWER_FLOOR_RECIPE_PRECEDES_D05_CEILING_VISIBILITY`
- `D05_CONSUMES_POWER_FLOOR_D05_DOES_NOT_CHOOSE_IT`
