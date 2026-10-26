# D19 ADVERSE-TREATMENT SPECIFICATION DEPENDENCY

**Status:** DECIDED_NOT_SPECIFIED — BLOCKING ROBUSTNESS AUTHORITY  
**Authority:** Blue Team / Mission Control  
**Nature:** specification of already-decided D19 missingness semantics; not a reopening of D19.

## 1. Dependency-pull finding

D05-A can identify and route missing/indecidable objects outcome-blind, but the repository does not yet expose a standalone hash-addressable D19 object that mechanically defines how those objects enter outcome robustness and the primary scientific verdict.

Therefore:

`D19 = DECIDED_NOT_YET_CONSUMABLE_AUTHORITY`

for adverse-treatment application.

**Invariant:** `D19_DECISION_NAME_IS_NOT_ADVERSE_TREATMENT_SPEC`.

## 2. What D05-A may do before this specification exists

D05-A may record:

- canonical missing-object identities;
- `QUALIFICATION_INDECIDABLE` identities/states;
- `BIAS_CAPABLE` reason/state;
- `ROUTED_B_FOR_LACK_OF_CAUSAL_CLEARANCE` reason/state;
- authorized causal strata where already frozen;
- bounded/unbounded denominator status;
- provenance and lineage needed by future robustness application.

It may not claim:

`BIAS_RULE_READY_PENDING_OUTCOME_APPLICATION`

with authority until this specification is hash-addressable.

Use instead:

`D19_ADVERSE_TREATMENT_SPEC_PENDING`.

## 3. Required specification outputs

The future D19 consumable artifact must define at minimum:

### 3.1 Canonical missing-object population

Define stable keys linking where applicable:

- accession/submission;
- reporting-owner CIK;
- issuer/security identity;
- formation/crossing object;
- outcome observation.

One scientific object may carry multiple missingness reasons, but one estimand must not count/subtract it twice merely because multiple reasons exist.

**Invariant:** `ONE_MISSING_OBJECT_ONE_POPULATION_IDENTITY`.

### 3.2 Qualification-indecidable translation

Define how objects that fail before successful parsing/qualification enter the possible qualifying population.

The contract must not assume that `QUALIFICATION_INDECIDABLE` exists only inside the already-parsed partition.

Expected-but-unacquired, unparsable, identity-unresolved and other upstream states require explicit translation rules where they can alter claim membership.

### 3.3 Adverse completion set

Define the complete set of outcome/membership completions over which the primary claim must remain valid.

The set must be broad enough that conservative routing spends power rather than scientific validity.

A treatment described only as `adverse` without a defined completion/support set has no consumable authority.

### 3.4 Missing-outcome support / boundedness

Define any support assumptions required to bound missing outcomes.

If no finite outcome/estimand bound is scientifically justified for a missingness class, the specification must make an unbounded/insufficient state reachable rather than silently truncate the adverse set.

**Invariant:** `UNBOUNDED_ADVERSE_SET_CANNOT_BE_SILENTLY_TRUNCATED`.

### 3.5 Robustness-bound construction

Define the exact identified/robustness-bound calculation from:

`observed outcomes + canonical missing set + adverse completion set`.

The calculation must preserve the primary estimand and frozen scientific benchmark.

### 3.6 Primary-verdict integration

D19 already decided that missingness bounds enter the primary scientific verdict rather than form a separate cosmetic gate.

The consumable specification must mechanically define how:

- pass;
- reject/no-edge where scientifically authorized;
- `INSUFFICIENT`;
- unbounded/unknown states

are generated from the robustness bounds.

It must preserve the distinction:

`INSUFFICIENT != NO_EDGE`.

## 4. Conservative routing requirement

`ROUTED_B_FOR_LACK_OF_CAUSAL_CLEARANCE` is a treatment state, not a causal assertion.

The future D19 adverse set must be sufficiently conservative that assigning an object to this state cannot make promotion easier than omitting the uncertainty.

**Invariant:** `CONSERVATIVE_ROUTING_MAY_SPEND_POWER_NOT_VALIDITY`.

## 5. No post-outcome rescue

After outcomes or robustness results are exposed, the current lineage may not narrow the adverse completion set, change support bounds, or redefine qualification-indecidable translation to rescue a failed/insufficient result.

Material changes require a new scientific lineage under D10 contamination rules.

**Invariant:** `NO_POST_OUTCOME_ADVERSE_SET_RESCUE`.

## 6. Current authority state

Until §§3.1–3.6 resolve to a versioned/hash-addressable artifact:

- D05-A Branch-B identities/statuses: **recordable**;
- Branch-B routing: **recordable under frozen D05 rules**;
- outcome robustness application: **NOT AUTHORIZED**;
- `BIAS_RULE_READY_PENDING_OUTCOME_APPLICATION`: **NOT AUTHORIZED**;
- `D19_ADVERSE_TREATMENT_SPEC_PENDING`: **required state**.

This gap blocks robustness authority, not denominator construction, D05 source-stage counting, or the D05 raw-ceiling engineering pass subject to its separate visibility gates.
