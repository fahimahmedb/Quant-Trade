# D05 SAMPLE SUFFICIENCY AND ROBUSTNESS GENERATOR

**Status:** FROZEN RULE — PRE-D05-A  
**Authority:** Blue Team / Mission Control  
**Prerequisites:** canonical D07 boundary, D05 unit taxonomy, representativeness failure-mode register and denominator reconciliation contract.

## 1. Purpose

This artifact freezes the rules transforming the D05-A scientific substrate into three logically distinct gates:

1. `POWER / AVAILABILITY GATE`
2. `BIAS / ROBUSTNESS GATE`
3. `CLAIM DENSITY GATE`

It does **not** define one independent coverage threshold for every pipeline stage.

The terminal scientific question is:

> Is the frozen claim population, after legitimate qualification and unavoidable data limitations, capable of supporting detection of the frozen MEUE with the required scientific authority?

Stage-level rates diagnose where information is lost.

They do not independently define sufficiency.

## 2. Three outputs, three meanings

### A. `THETA_COVERAGE_REQUIREMENT`

Covers availability-type limitations that reduce attainable information/sample size.

This is the only branch whose requirements instantiate `Theta_coverage` in the D19 sense.

### B. `MISSINGNESS_ROBUSTNESS_RULE`

Covers missingness capable of changing population composition or shifting the estimand.

This lives alongside `Theta_coverage`.

It feeds adverse-treatment / partial-identification reasoning but is not itself a coverage threshold.

### C. `CLAIM_DENSITY_RULE`

Covers intrinsic incidence of legitimately qualifying units.

This is neither coverage loss nor missingness.

It is a separate feasibility/economic-learning gate.

**Invariant:** `THETA_COVERAGE_DOES_NOT_ABSORB_ALL_FEASIBILITY`

## 3. No independent stage thresholds

The generator must never define scientific sufficiency as independent stage conditions such as:

`q_ingestion >= q1`

`q_parse >= q2`

`q_resolution >= q3`

`q_market >= q4`

with each threshold selected independently.

Such thresholds have no guaranteed terminal meaning.

Multiple individually high stage rates can compound into a materially deficient terminal sample.

Therefore the scientific requirement starts from one terminal information requirement.

Stage rates remain diagnostics and causal decomposition tools.

**Invariants:**

`POWER_REQUIREMENT_IS_TERMINAL_NOT_STAGEWISE`

`STAGE_RATES_DIAGNOSE_BUT_DO_NOT_DEFINE_TERMINAL_SUFFICIENCY`

## 4. Terminal power requirement

The frozen power framework defines the minimum effective information required to detect the MEUE.

Conceptually:

`N_eff_required = PowerRequirement(MEUE, alpha, target_power, variance/dependence assumptions)`.

The mapping must respect D09, including:

- frozen MEUE;
- scientific alpha/error policy;
- target power;
- admissible variance envelope;
- estimator/inference assumptions;
- dependence treatment when finalized;
- predetermined conservative margin where required.

The requirement may never be fitted to D05-A coverage.

**Invariant:** `COVERAGE_REQUIREMENT_INDEPENDENCE`

## 5. Requirement floor before D07

Because final D07/D08 geometry is not yet frozen, final `N_eff_required` may not yet be uniquely instantiable.

For one-sided early rejection define:

`N_eff_required_floor`

as the **smallest scientifically admissible effective-sample requirement** under the frozen power framework and the remaining bounded inference envelope.

The floor is intentionally favorable to the claim.

If even this favorable requirement cannot be reached, later scientific choices cannot rescue the claim.

If no defensible floor can yet be produced:

`POWER_REQUIREMENT_UNRESOLVED`

and no early power-impossibility verdict may be issued.

The floor cannot be inferred from D05-A values.

## 6. Positive power sufficiency is unavailable before D07

At D05-A:

- O1 remains open;
- O2 remains open;
- O4 remains open;
- final observation geometry is not frozen;
- final dependence geometry is not frozen;
- actual `N_eff` is unknown.

D05-A may not select one D07 convention to manufacture a positive power verdict.

However, it may prove **impossibility** using an upper bound over the entire frozen open design space.

**Invariant:** `OPEN_DESIGN_SPACE_CAN_REJECT_BUT_NOT_AUTHORIZE`

## 7. Design-space envelope authority

The pre-D07 ceiling is a special governance bound.

It is not:

- an event count under a selected geometry;
- a D05-A event metric;
- evidence that one D07 convention is preferable.

A sealed calculation consumes:

- frozen D05-A-eligible substrate;
- the complete frozen D07 open-space definition;

and emits only authorized envelope outputs.

**Invariant:** `DESIGN_SENSITIVE_INTERMEDIATES_HAVE_AUTHORITY_ZERO`

Intermediate event counts or identities produced solely to calculate the envelope:

- are not D05-A scientific outputs;
- are not inspectable D07 evidence;
- have `AUTHORITY=0`;
- cannot inform later design choice.

## 8. O4 monotonicity theorem

For the observation-count ceiling, O4 does not require optimization.

The maximally generous admissible O4 convention is:

> every threshold crossing remains a distinct statistical observation, with no fusion or exclusion merely because exposure windows overlap.

Call this:

`O4_MAXIMAL_SEPARATION`.

For any fixed formation state machine, alternative admissible O4 conventions may merge overlapping crossings, group crossings, exclude a crossing from a statistical representation, or treat overlapping exposures as one unit.

They may not create a threshold crossing that does not exist in the formation state machine.

Therefore:

`N_observations(O4) <= N_threshold_crossings`

with equality under:

`O4_MAXIMAL_SEPARATION`.

Thus:

`sup_O4 N_observations = N_threshold_crossings`.

The O4 supremum is a **count**, not an optimization problem.

**Invariant:** `O4_MAXIMUM_IS_NO_MERGE_COUNT`

## 9. O2 crossing-count invariance

The proof relies on the closed signal invariant in the canonical boundary:

`WINDOW_EXPIRY_PRECEDES_SESSION_ADDITIONS`.

For each formation session `S`:

1. all observations outside the 10-session window are expired before any observation attached to `S` is applied;
2. re-arm caused by expiry is applied at that session boundary;
3. only then are same-session qualifying observations processed;
4. no expiry occurs between same-session additions.

Therefore, once O2 processing begins for `S`, the set of distinct qualifying insider CIKs can only remain unchanged or grow.

For a fixed O1 projection:

- if the post-expiry/pre-addition state is `<2` and the final same-session state is `>=2`, exactly one crossing occurs in that session;
- otherwise zero crossing occurs in that session.

Different admissible O2 orderings may change which filing is designated the threshold-triggering filing, which owner is the logical trigger, and the logical intra-session trigger position.

They cannot change whether the session contains a crossing or total crossing count.

Therefore:

`N_threshold_crossings(O1, O2_a) = N_threshold_crossings(O1, O2_b)`

for all admissible O2 conventions.

**Invariant:** `O2_CHANGES_TRIGGER_IDENTITY_NOT_CROSSING_COUNT`

Without the canonical boundary invariant `WINDOW_EXPIRY_PRECEDES_SESSION_ADDITIONS`, this proof would not be valid.

## 10. O3 irrelevance to crossing-count ceiling

O3 governs indexing of the 20-session post-signal interval.

It does not alter whether the formation state machine produces a threshold crossing.

Under `O4_MAXIMAL_SEPARATION`, the raw observation ceiling counts crossings before overlap fusion or outcome-interval handling.

Therefore O3 does not enter the raw crossing-count ceiling.

**Invariant:** `O3_DOES_NOT_DEFINE_PRE_D07_CROSSING_CEILING`

## 11. O1 finite exhaustive enumeration

The canonical D07 boundary freezes the complete admissible O1 set as:

`G_O1 = {PREVIOUS_REGULAR_SESSION, NEXT_REGULAR_SESSION}`

for EDGAR dates with no regular session.

For EDGAR dates that are regular sessions, the attachment is already fixed to that session.

No `nearest`, hybrid or locally adaptive convention is admissible.

For each admissible global O1 convention `g_i`, the sealed envelope engine computes:

`C_i = threshold-crossing count under g_i`

using closed rolling-window semantics, O2 crossing-count invariance and `O4_MAXIMAL_SEPARATION`.

Therefore:

`N_obs_ceiling_open_D07 = max(C_previous, C_next)`.

This maximum is over the **entire admissible O1 space**, not over all mathematically conceivable projections.

Because the canonical boundary defines the admissible design space, this is the required supremum.

## 12. O1 output embargo

The pair:

`(C_previous, C_next)`

is design-sensitive.

Revealing it would tell D07 which convention produces more crossings.

Therefore the only authorized visible value is:

`max(C_previous, C_next)`.

The following remain sealed:

- each convention-specific count;
- difference between counts;
- ranking;
- convention-specific crossing identities;
- identity of the argmax convention.

**Invariants:**

`ENVELOPE_OUTPUT_ONLY`

`ARGMAX_IS_EMBARGOED`

If implementation stores the argmax or convention-specific proof data for reproducibility, those records must be sealed and unavailable to the D07 decision surface until D07 has independently frozen its O1 choice.

## 13. Envelope non-interference

The envelope engine exists solely to answer:

> Is every admissible D07 design incapable of reaching the power requirement?

It must not answer:

> Which D07 design gives the largest N?

The arithmetic may overlap. Scientific authority does not.

**Invariant:** `ENVELOPE_CAN_PROVE_IMPOSSIBILITY_NOT_DESIGN_PREFERENCE`

## 14. Branch A — availability-only loss

A loss belongs to the power/availability branch when a frozen structural justification establishes that its mechanism does not plausibly select observations based on insider mechanism, qualification state, economic outcome or outcome-related population characteristics after conditioning on pre-authorized causal strata.

Examples may include genuinely non-differential transport failures, source outages, mechanically missing bytes or acquisition interruptions independent of claim composition.

Such losses reduce attainable N.

They are not automatically estimand bias.

**Invariant:** `MECHANISM_INDEPENDENT_LOSS_IS_SAMPLE_LOSS_NOT_BIAS`

## 15. Branch B — bias-capable missingness

A loss belongs to Branch B when its mechanism can plausibly select observations according to something related to the claim mechanism, owner/issuer/security composition, listing/reference regime material to the estimand, economic-outcome observability or a pre-registered representativeness dimension.

It also belongs here when missingness is materially concentrated in an authorized causal stratum in a way capable of shifting population composition.

Examples include `QUALIFICATION_INDECIDABLE`, structural resolution failure concentrated in a claim-relevant group, market-data absence associated with listing/survival, differential documentary-regime missingness or outcome-related disappearance/delisting mechanisms.

Such missingness reduces N **and** may shift the estimand.

**Invariant:** `BIAS_IS_NOT_PURCHASABLE_WITH_SAMPLE_SIZE`

## 16. Symmetric routing protection

A large non-differential loss must not be treated as bias solely because it is numerically large.

Where the missingness mechanism is structurally established as non-differential under authorized causal strata:

`loss -> Branch A`.

Its consequence is information/sample-size loss.

**Invariant:** `NONDIFFERENTIAL_MISSINGNESS_IS_NOT_BIAS_BY_MAGNITUDE`

## 17. Unclassified loss mechanism

If causal evidence available before values cannot establish whether a loss is `AVAILABILITY_ONLY` or `BIAS_CAPABLE`, assign:

`LOSS_MECHANISM_UNCLASSIFIED`.

It cannot be resolved by inspecting outcomes.

The system may not silently route it to either branch for convenience.

## 18. Concentration trigger

A failure mechanism may be availability-like globally but bias-capable when concentrated in an authorized causal stratum.

A frozen classification rule may therefore state:

`diffuse under authorized causal strata -> Branch A`

`materially concentrated in claim-relevant causal stratum -> Branch B`.

The concentration rule itself must be frozen before D05-A.

Only strata already authorized by the Failure-Mode Register may be used.

No post-hoc segmentation is permitted.

## 19. Branch B has no generic q threshold

The robustness branch does not define `q_bias_min`.

Instead:

`observed estimand + bias-capable missing set -> frozen adverse treatment -> identified/robustness bounds -> primary scientific decision`.

Missingness is admissible only while the primary decision remains unchanged under the frozen adverse treatment.

## 20. D05-A role in Branch B

D05-A remains outcome-blind.

It may establish missing/indecidable identities, causal missingness class, authorized strata, missing-set cardinality, bounded/unbounded denominator state and lineage needed for future adverse-treatment application.

It does not evaluate outcome-dependent robustness before authorized outcome release.

Normal state:

`BIAS_RULE_READY_PENDING_OUTCOME_APPLICATION`.

An unbounded denominator can fail earlier:

`DENOMINATOR_UNKNOWN -> COVERAGE_UNKNOWN`

under:

`ALLOWABLE_UNBOUNDED_DENOMINATOR_UNKNOWN = 0`.

## 21. `QUALIFICATION_INDECIDABLE`

`QUALIFICATION_INDECIDABLE` belongs to Branch B.

Its true state may alter composition of the qualifying population.

It must never be silently converted to `NON_QUALIFYING` or treated solely as sample shrinkage.

## 22. Branch C — claim density

`NON_QUALIFYING` belongs to neither Branch A nor Branch B.

It is not data loss, missingness or measurement failure.

It is the legitimate result of applying the frozen claim.

Therefore `qualification incidence` is reported separately from coverage.

Example:

`QUALIFYING / QUALIFICATION_DECIDABLE`.

**Invariant:** `NON_QUALIFYING_IS_INCIDENCE_NOT_COVERAGE_LOSS`

## 23. Claim-density ceiling

For early impossibility testing, construct a ceiling favorable to the claim.

Known `NON_QUALIFYING` units remain non-qualifying.

Every unresolved object that could still legitimately qualify is treated in the most favorable admissible way for an upper bound.

Downstream data availability is assumed perfect.

Formation count uses the sealed D07 envelope rules defined above.

This produces:

`N_obs_ceiling_claim_density`.

It asks:

> Even with perfect infrastructure and maximally favorable treatment of unresolved claim membership, can the frozen claim produce enough potential observations?

Where exact favorable completion is not uniquely constructible, a looser analytic upper bound is allowed only if proven never to understate the true admissible maximum.

A looser ceiling may reduce rejection power. It may never create a false impossibility verdict.

## 24. Available-substrate ceiling

A second ceiling respects structural availability losses established by D05-A while remaining favorable over open D07 geometry.

Define:

`N_obs_ceiling_available`.

It incorporates frozen claim rules, observed qualifying/possible-qualifying substrate, structural unrecoverable availability limitations, exhaustive O1 maximum, O2 count invariance and `O4_MAXIMAL_SEPARATION`.

Since:

`N_eff <= N_raw_observations`

if the raw ceiling is already below the favorable requirement floor, actual effective information cannot pass.

## 25. Recoverable transport defects

A state such as `EXPECTED_PAYLOAD_MISSING` may be treated as recoverable in the availability ceiling only if the expected accession is known, an authorized recovery channel exists, recovery cannot change scope, and the recovery rule was frozen in advance.

This allows the ceiling to ask what is structurally attainable if a predetermined Data Plane repair is completed.

**Invariant:** `RECOVERABLE_TRANSPORT_DEFECT_IS_NOT_STRUCTURAL_INFORMATION_LOSS`

## 26. Recovery-assumption ledger

Every ceiling computation that assumes an unrecovered object can be recovered must produce a:

`RECOVERY_ASSUMPTION_LEDGER`.

Each condition must record at minimum:

- `recovery_condition_id`;
- accession/object identity;
- failure state;
- permitted recovery path;
- `execution_owner`;
- `mission_id`;
- `discharge_certifier`;
- `deadline_gate`;
- current `status`;
- proof artifact/hash when discharged;
- whether the condition materially supports the continuation verdict.

Required governance:

`execution_owner != discharge_certifier`.

For every recovery assumption used to support progression toward D07:

`deadline_gate = BEFORE_D07_SCIENTIFIC_FREEZE`.

**Invariant:** `RECOVERY_CONDITION_MUST_HAVE_OWNER_AND_DEADLINE`

## 27. Recovery-dependent verdicts and discharge

If `POWER_UNDETERMINED_PENDING_D07` depends on any unrecovered assumed repair, attach:

`RECOVERY_CONDITIONS_OPEN`.

This is a conditional continuation verdict.

Before D07 receives scientific authority to freeze geometry, every material recovery condition must be:

1. completed and independently certified; or
2. removed from the ceiling and the ceiling recomputed.

If no authorized execution owner or independent certifier can be assigned, or the condition otherwise cannot be discharged:

`RECOVERY_CONDITION_UNDISCHARGEABLE`.

Then the assumed recovery is removed and the ceiling is recomputed without it.

If the recomputed ceiling falls below the requirement floor, the verdict changes to the corresponding impossibility state.

**Invariants:**

`ASSUMED_RECOVERY_MUST_BE_VISIBLE`

`NO_D07_AUTHORITY_ON_UNREALIZED_RECOVERY_ASSUMPTION`

`UNVERIFIED_RECOVERY_CANNOT_SUPPORT_D07_FREEZE`

## 28. Two scientific ceilings and three power/density cases

Maintain:

### A. `N_obs_ceiling_claim_density`

Assumes perfect downstream availability and isolates intrinsic claim abundance.

### B. `N_obs_ceiling_available`

Honors structural availability limitations while remaining maximally generous over open D07 geometry.

Compare both with `N_eff_required_floor`.

### Case 1 — intrinsic density impossible

If:

`N_obs_ceiling_claim_density < N_eff_required_floor`

then:

`CLAIM_POPULATION_TOO_SPARSE_FOR_REQUIRED_POWER`.

Even perfect infrastructure cannot rescue the frozen claim.

This is a definitive ELE.

### Case 2 — available substrate impossible

If the claim-density ceiling reaches the floor but:

`N_obs_ceiling_available < N_eff_required_floor`

then:

`POWER_IMPOSSIBLE_DUE_TO_AVAILABILITY`.

The claim may intrinsically contain enough material, but the scientifically attainable substrate cannot support it.

This is a definitive ELE.

### Case 3 — impossibility not established

If:

`N_obs_ceiling_available >= N_eff_required_floor`

then:

`POWER_UNDETERMINED_PENDING_D07`.

This means only that D05-A has not proven power impossible.

It does not mean power is sufficient, likely sufficient or promising.

If unrecovered repairs support the ceiling, append:

`RECOVERY_CONDITIONS_OPEN`.

## 29. Why an envelope pass cannot authorize

The ceiling intentionally uses favorable assumptions: requirement floor favorable to the claim, maximum over the complete admissible O1 set, no O4 fusion, O2 crossing-count invariance, raw count before dependence penalties and favorable completion where valid upper-bounding requires it.

Therefore only this implication is valid:

`ceiling < requirement floor -> impossible`.

The inverse is invalid:

`ceiling >= requirement floor -/-> sufficient`.

**Invariant:** `UPPER_BOUND_PASS_IS_NOT_POWER_PASS`

## 30. Relationship to `Theta_coverage`

Only Branch A availability requirements feed `Theta_coverage`.

These include, where applicable:

- denominator certainty;
- temporal/source availability;
- ingestion availability;
- parse availability;
- D07-independent resolution availability;
- market-data availability;
- authorized aggregate/stratum availability requirements;
- structural availability-loss budget;
- handling of `COVERAGE_UNKNOWN`.

Any operational stage threshold must be a mathematical consequence of the terminal requirement or a causal diagnostic, never an independently chosen scientific gate.

### Branch B remains outside `Theta_coverage`

`MISSINGNESS_ROBUSTNESS_RULE` is a separate adverse-treatment / partial-identification gate.

### Branch C remains outside `Theta_coverage`

`CLAIM_DENSITY_RULE` is a separate lane-feasibility gate.

## 31. Required D05-A outputs

### Branch A

- denominator status;
- expected population count;
- join/ingestion states;
- parse states;
- structural availability states;
- resolution states;
- market-data availability states;
- authorized causal strata;
- recoverable vs structural-loss classification;
- recovery-assumption ledger.

### Branch B

- all `QUALIFICATION_INDECIDABLE`;
- other pre-classified bias-capable missing sets;
- causal strata;
- bounded/unbounded status;
- lineage needed for later adverse-treatment evaluation.

### Branch C

- qualification-decidable count;
- qualifying count;
- non-qualifying count;
- qualification-indecidable count;
- inputs required for the favorable claim-density ceiling.

### Sealed envelope engine — internal only

- `C_previous`;
- `C_next`;
- convention-specific crossing identities;
- argmax O1 convention;
- O2 trigger identity;
- any other design-sensitive intermediate needed to prove the envelope.

Authorized visible outputs are limited to ceiling scalar(s), proof that O1 enumeration covered the complete frozen admissible set, proof of O2 count invariance using `WINDOW_EXPIRY_PRECEDES_SESSION_ADDITIONS`, proof that O4 maximal separation dominates admissible O4 conventions, and recovery conditions attached to a ceiling.

## 32. D05-A verdict precedence

### First — denominator authority

If expected population is unbounded:

`COVERAGE_UNKNOWN`

under:

`ALLOWABLE_UNBOUNDED_DENOMINATOR_UNKNOWN = 0`.

Stop authority progression.

### Second — intrinsic claim density

If:

`N_obs_ceiling_claim_density < N_eff_required_floor`

then:

`CLAIM_POPULATION_TOO_SPARSE_FOR_REQUIRED_POWER`.

### Third — available substrate

If claim density could suffice but:

`N_obs_ceiling_available < N_eff_required_floor`

then:

`POWER_IMPOSSIBLE_DUE_TO_AVAILABILITY`.

### Fourth — otherwise

`POWER_UNDETERMINED_PENDING_D07`.

Attach `RECOVERY_CONDITIONS_OPEN` where applicable.

Branch-B missingness remains attached for later robustness analysis.

No positive power authorization is generated.

## 33. Anti-rescue rules

After D05-A, none of the following may be weakened or altered because observed substrate is inconvenient:

- MEUE;
- target power;
- alpha/error policy;
- requirement-floor mapping;
- admissible O1 set;
- envelope calculation;
- O2 invariance rule;
- O4 maximal-separation rule;
- claim-density ceiling definition;
- availability ceiling definition;
- recoverable/structural classification;
- Branch A/Branch B routing rule;
- adverse-treatment rule;
- D07 boundary.

Any material change is scientific redesign/new lineage.

**Invariants:**

`NO_POWER_THRESHOLD_RESCUE`

`NO_MISSINGNESS_CLASSIFICATION_RESCUE`

`NO_ENVELOPE_REDEFINITION_AFTER_VALUES`

## 34. Core invariants

- `POWER_REQUIREMENT_IS_TERMINAL_NOT_STAGEWISE`
- `STAGE_RATES_DIAGNOSE_BUT_DO_NOT_DEFINE_TERMINAL_SUFFICIENCY`
- `OPEN_DESIGN_SPACE_CAN_REJECT_BUT_NOT_AUTHORIZE`
- `DESIGN_SENSITIVE_INTERMEDIATES_HAVE_AUTHORITY_ZERO`
- `O4_MAXIMUM_IS_NO_MERGE_COUNT`
- `O2_CHANGES_TRIGGER_IDENTITY_NOT_CROSSING_COUNT`
- `O3_DOES_NOT_DEFINE_PRE_D07_CROSSING_CEILING`
- `ENVELOPE_OUTPUT_ONLY`
- `ARGMAX_IS_EMBARGOED`
- `ENVELOPE_CAN_PROVE_IMPOSSIBILITY_NOT_DESIGN_PREFERENCE`
- `COVERAGE_REQUIREMENT_INDEPENDENCE`
- `MECHANISM_INDEPENDENT_LOSS_IS_SAMPLE_LOSS_NOT_BIAS`
- `NONDIFFERENTIAL_MISSINGNESS_IS_NOT_BIAS_BY_MAGNITUDE`
- `BIAS_IS_NOT_PURCHASABLE_WITH_SAMPLE_SIZE`
- `NON_QUALIFYING_IS_INCIDENCE_NOT_COVERAGE_LOSS`
- `RECOVERABLE_TRANSPORT_DEFECT_IS_NOT_STRUCTURAL_INFORMATION_LOSS`
- `RECOVERY_CONDITION_MUST_HAVE_OWNER_AND_DEADLINE`
- `ASSUMED_RECOVERY_MUST_BE_VISIBLE`
- `NO_D07_AUTHORITY_ON_UNREALIZED_RECOVERY_ASSUMPTION`
- `UNVERIFIED_RECOVERY_CANNOT_SUPPORT_D07_FREEZE`
- `UPPER_BOUND_PASS_IS_NOT_POWER_PASS`
- `THETA_COVERAGE_DOES_NOT_ABSORB_ALL_FEASIBILITY`
- `INSUFFICIENT_MUST_BE_REACHABLE`
- `NO_POWER_THRESHOLD_RESCUE`
- `NO_MISSINGNESS_CLASSIFICATION_RESCUE`
- `NO_ENVELOPE_REDEFINITION_AFTER_VALUES`
