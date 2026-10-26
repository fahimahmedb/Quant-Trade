# D05-A STOPPING / SNAPSHOT / REPLAY RULE

**Status:** CLOSED / FROZEN RULE — ASTRA-CORRECTED  
**Authority:** Blue Team / Mission Control  
**Purpose:** define when a D05-A pass starts, completes, fails, publishes, and may be replayed without result-driven discretion.

## 1. D05-A is a deterministic pass, not sequential collection

A D05-A pass executes a frozen finite work definition over:

- frozen scientific protocol;
- frozen metric/stratum surface;
- frozen denominator reconciliation rule;
- frozen expected manifest;
- frozen implementation identity;
- frozen stopping/snapshot/replay rule;
- frozen power-floor derivation recipe hash or explicit mechanically enforced access-separation state.

Completion is defined by exhausting the frozen work, not by reaching a desired scientific answer.

**Invariant:** `PASS_COMPLETION_IS_DEFINED_BY_FROZEN_WORK_NOT_DESIRED_RESULT`

## 2. Pass identity

Every pass has an immutable `D05A_PASS_ID` binding at minimum:

- protocol/science hashes;
- metric-surface hash;
- stopping-rule hash;
- reconciliation-rule hash;
- `EXPECTED_MANIFEST_HASH`;
- power-floor derivation-recipe hash/state;
- source snapshot/epoch identity;
- implementation commit;
- parent pass where applicable;
- execution environment identity sufficient for reproducibility.

A change in an authority-bearing input creates a different pass identity.

## 3. Expected population is snapshot-versioned

The authority-bearing expected population is:

`E = P(official SEC index snapshot at T0)`.

The realized expected manifest is therefore a dated/versioned snapshot, not a timeless statement about EDGAR.

The manifest records at minimum:

- build timestamp;
- SEC index epoch identity;
- source artifact identities/hashes;
- frozen projection/rule hash;
- `EXPECTED_MANIFEST_HASH`.

## 4. Canonical denominator source

Full/quarterly SEC indexes are the canonical denominator source for the expected population snapshot.

Daily indexes may be used as secondary operational evidence but do not silently replace the canonical denominator snapshot.

## 5. Source freshness through the frozen projection

Freshness compares the authority-bearing projection `P`, not raw source-file byte equality.

If:

`P(index_t0) == P(index_t1)`

on all authority-bearing membership/fields, a non-scope raw metadata change does not force a new scientific pass.

Post-snapshot source deltas are classified as:

- `SOURCE_POST_SNAPSHOT_CHANGE_NON_SCOPE`
- `SOURCE_POST_SNAPSHOT_ADDITION`
- `SOURCE_POST_SNAPSHOT_REMOVAL`
- `SOURCE_POST_SNAPSHOT_SCOPE_MUTATION`

Addition/removal/scope mutation creates a new source snapshot, manifest hash and pass lineage. It does not mutate the completed pass.

**Invariants**

- `SOURCE_REVISION_IS_NOT_PIPELINE_INSTABILITY`
- `POST_HASH_INDEX_CHANGE_DOES_NOT_MUTATE_CURRENT_PASS`

## 6. SEC index epoch

Operational source epoch is derived mechanically from the canonical weekly SEC-index refresh regime using New York calendar semantics.

The epoch identifier and derivation rule must be stored in the pass identity.

An epoch change requires a freshness comparison under `P`; it does not automatically imply a rerun when the authority-bearing projection is unchanged.

## 7. Power-floor recipe must precede ceiling visibility

D05-A ceilings can influence later choices even when no market outcome has been exposed.

Therefore, before any human-readable value of:

- `N_OBS_CEILING_CLAIM_DENSITY`;
- `N_OBS_CEILING_AVAILABLE`;
- any equivalent count that materially reveals proximity to a future power threshold;

is published, the complete derivation recipe for `N_RAW_REQUIRED_FLOOR` must already be frozen/hash-addressable.

The recipe includes, as applicable:

- D09 delta / MEUE mapping;
- deployment-domain rule;
- alpha / target-power policy;
- floor transform;
- power-function / inference-family rule used for the floor;
- external source admission/search/stop rule;
- extraction and source-uncertainty treatment;
- horizon scaling rule if any;
- numerical-infimum certification rule.

The final numerical floor may remain unresolved pending external measurements. What may not remain mutable is the rule that will derive it.

Alternative execution is permitted only under a mechanically proven access separation in which no actor able to modify the floor recipe can inspect ceiling values before recipe freeze.

**Invariants**

- `POWER_FLOOR_RECIPE_PRECEDES_D05_CEILING_VISIBILITY`
- `NO_CEILING_INFORMED_POWER_FLOOR_DESIGN`

## 8. No intermediate scientific output by default

D05-A should publish nothing human-readable from the scientific result surface until the pass is atomically complete and all visibility gates in this rule are satisfied.

Execution state remains:

`UNPUBLISHED_EXECUTION_STATE`

until atomic publication of:

`COMPLETED_RESULT_ARTIFACT`.

**Invariant:** `NO_INTERMEDIATE_OUTPUT_BY_DEFAULT`

This is the preferred structural realization of outcome/result exposure level E0.

## 9. Mechanical evidence of non-exposure

If execution fails before publication:

`EXECUTION_E0_NO_VISIBLE_OUTPUT`.

Non-exposure must be mechanically supported.

Preferred proof is absence of any readable scientific artifact before completion.

If temporary persistent state is unavoidable, it must be accessible only through a governed interface with immutable access logging and no alternate human-readable path.

An ordinary workspace file cannot prove unread exposure.

**Invariant:** `NON_EXPOSURE_REQUIRES_MECHANICAL_EVIDENCE`

## 10. Visible partial output

If any partial scientific result becomes human-visible before atomic completion:

`PARTIAL_OUTPUT_EXPOSED`.

The engineering failure may be repaired, but the exposure fact remains in lineage.

There is no silent retry that pretends the exposure did not happen.

A ceiling exposed before power-floor recipe freeze additionally creates:

`CEILING_BEFORE_POWER_FLOOR_RECIPE_EXPOSURE`.

That lineage cannot later use a newly designed power-floor recipe for an authority-bearing early impossibility verdict unless a pre-existing mechanical separation proves the recipe designers were not exposed.

**Invariant:** `VISIBLE_PARTIAL_OUTPUT_NO_SILENT_RETRY`

## 11. Open recovery/classification conditions do not extend pass lifetime

A pass may complete with:

- `RECOVERY_CONDITIONS_OPEN`;
- `AVAILABILITY_CLASSIFICATION_CONDITIONS_OPEN`.

An open dependency does not mean the deterministic pass remains unfinished.

**Invariant:** `OPEN_RECOVERY_DOES_NOT_EXTEND_PASS_LIFETIME`

The completed pass and its result remain immutable.

## 12. Condition discharge after pass completion

Discharging a recovery or classification condition does not edit the completed pass.

If the discharge changes the scientific substrate needed by D05-A, run a new full pass under the same frozen science/manifest unless an authority-bearing input has changed, in which case create the corresponding new lineage.

**Invariants**

- `RECOVERY_REPLAY_IS_FULL_PASS`
- `RECOVERY_DOES_NOT_RETROACTIVELY_EDIT_RESULT`

No partial scientific replay is authorized merely because only one dependency changed.

## 13. Replay classes

### `IDENTICAL_REPLAY`

Requires:

- same implementation commit;
- same scientific/protocol hashes;
- same metric surface;
- same manifest hash;
- same power-floor recipe hash/state;
- same authority-bearing source snapshot/projection;
- same deterministic inputs.

Environmental re-execution with unchanged implementation/science may be an identical replay.

**Invariant:** `IDENTICAL_REPLAY_REQUIRES_SAME_IMPLEMENTATION_COMMIT`

### `REPAIRED_REPLAY`

A different implementation commit used solely to repair execution/engineering behavior.

Authority requires:

- independently proven/certified scientific semantic equivalence;
- repair explicitly recorded;
- new `D05A_PASS_ID` referencing the parent pass;
- full-pass replay.

A repaired replay is never called identical.

**Invariant:** `REPAIRED_REPLAY_REQUIRES_INDEPENDENT_SEMANTIC_EQUIVALENCE`

## 14. Engineering instability does not reopen science

If the same frozen pass repeatedly fails because of engineering/environment instability, that is a Control Plane / implementation problem.

It is not authority to change the scientific stopping rule, metric surface, denominator rule, power-floor recipe or pass-completion semantics.

## 15. Retry discipline

A retry is allowed only under its declared replay class and exposure state.

No retry may be selected because the partial/completed scientific result was inconvenient.

If scientific inputs/rules change, create a new scientific lineage rather than calling the run a replay.

## 16. Atomic completion artifact

A completed result artifact binds at minimum:

- `D05A_PASS_ID`;
- all authority hashes;
- completion state;
- denominator verdict;
- D05-A metric surface outputs permitted by the visibility gate;
- sealed-envelope proof reference;
- open-condition ledger reference;
- `N_RAW_REQUIRED_FLOOR` or cause-preserving unresolved state where applicable;
- power-floor recipe hash;
- publication timestamp;
- implementation commit.

## 17. Core invariants

- `PASS_COMPLETION_IS_DEFINED_BY_FROZEN_WORK_NOT_DESIRED_RESULT`
- `POWER_FLOOR_RECIPE_PRECEDES_D05_CEILING_VISIBILITY`
- `NO_CEILING_INFORMED_POWER_FLOOR_DESIGN`
- `NO_INTERMEDIATE_OUTPUT_BY_DEFAULT`
- `NON_EXPOSURE_REQUIRES_MECHANICAL_EVIDENCE`
- `VISIBLE_PARTIAL_OUTPUT_NO_SILENT_RETRY`
- `OPEN_RECOVERY_DOES_NOT_EXTEND_PASS_LIFETIME`
- `RECOVERY_REPLAY_IS_FULL_PASS`
- `RECOVERY_DOES_NOT_RETROACTIVELY_EDIT_RESULT`
- `IDENTICAL_REPLAY_REQUIRES_SAME_IMPLEMENTATION_COMMIT`
- `REPAIRED_REPLAY_REQUIRES_INDEPENDENT_SEMANTIC_EQUIVALENCE`
- `SOURCE_REVISION_IS_NOT_PIPELINE_INSTABILITY`
- `POST_HASH_INDEX_CHANGE_DOES_NOT_MUTATE_CURRENT_PASS`
