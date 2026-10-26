# D05-A ROUTE-B SURFACE / VISIBILITY AMENDMENT — 2026-09-17

**Status:** FROZEN AMENDMENT  
**Authority:** Blue Team / Mission Control  
**Parent decision:** `BLUE_POWER_ROUTE_B_DECISION_2026-09-17.md`

This amendment supersedes conflicting active-current-lineage language in:

- `D05_SAMPLE_SUFFICIENCY_AND_ROBUSTNESS_GENERATOR_AMENDMENT_2026-09-16.md` §§9–10, 14–16 and corresponding early-floor invariants;
- `D05A_MINIMAL_METRIC_AND_STRATUM_SURFACE.md` §§19–20 and corresponding power-floor surface/invariants;
- `D05A_STOPPING_SNAPSHOT_REPLAY_RULE.md` §§1–2, 7, 10, 13, 16–17 only where those clauses require a pre-D07 power-floor recipe/hash for current-lineage visibility or pass identity.

All non-conflicting D05-A denominator, unit, availability, routing, stopping, replay, non-exposure and anti-rescue rules remain in force.

## 1. Early power states removed from active D05-A authority

For the current lineage D05-A cannot emit:

- `CLAIM_POPULATION_TOO_SPARSE_FOR_REQUIRED_POWER`;
- `POWER_IMPOSSIBLE_DUE_TO_AVAILABILITY`;
- a positive/negative `POWER_AVAILABILITY_VERDICT` based on a pre-D07 floor;
- `N_RAW_REQUIRED_FLOOR` as a current-lineage D05-A input/output;
- any legacy `N_EFF_REQUIRED_FLOOR` object as a current-lineage input/output.

Instead expose the fixed route state:

`EARLY_POWER_AUTHORITY_STATE = ROUTE_B_NO_PRE_D07_POWER_KILL`.

Historical raw-count unit corrections remain valid if a future new lineage reintroduces a floor.

### 1.1 Legacy floor invariants are N/A, not false

The previously frozen invariants:

- `D05_CONSUMES_POWER_FLOOR_D05_DOES_NOT_CHOOSE_IT`;
- `D05_CONSUMES_FLOOR_D05_DOES_NOT_SOURCE_SHOP`;
- `RAW_CEILING_COMPARES_ONLY_TO_RAW_REQUIREMENT`;
- related `N_eff -> N_raw` repair clauses;

remain scientifically correct for a lineage that has an active pre-D07 power-floor consumer.

For the current Route-B lineage they are:

`N/A_CURRENT_LINEAGE`.

They must not be read as pending obligations or blockers.

**Invariant:** `RETIRED_CONSUMER_RETIRES_ROUTE_SPECIFIC_INVARIANTS`.

## 2. Active terminal D05-A surface

Subject to the frozen visibility rules, active terminal outputs include:

- denominator/reconciliation verdict and J0–J5 status surface;
- `QUALIFYING_COUNT`;
- `NON_QUALIFYING_COUNT`;
- `QUALIFICATION_INDECIDABLE_COUNT`;
- `QUALIFICATION_DECIDABLE_COUNT`;
- authorized parsing/PIT/market-substrate availability quantities;
- `N_OBS_CEILING_CLAIM_DENSITY`;
- `N_OBS_CEILING_AVAILABLE`;
- `RECOVERY_CONDITIONS_OPEN_COUNT`;
- `AVAILABILITY_CLASSIFICATION_CONDITIONS_OPEN_COUNT`;
- unified `D05A_CONDITION_LEDGER`;
- Branch-B routing states/counts authorized by the frozen surface;
- `D19_ADVERSE_TREATMENT_SPEC_PENDING` or later authorized D19 readiness state;
- `EARLY_POWER_AUTHORITY_STATE = ROUTE_B_NO_PRE_D07_POWER_KILL`.

The two `N_OBS_CEILING_*` objects remain raw statistical-observation upper bounds. They are descriptive/feasibility outputs and are not compared to a pre-D07 power requirement.

## 3. Claim-density and availability ceilings remain conservative

The removal of early power authority does not relax their construction.

`N_OBS_CEILING_CLAIM_DENSITY` still requires exact global maximization over compatible unresolved completions or a proven majorant.

`N_OBS_CEILING_AVAILABLE` still excludes only proven structural availability loss; recoverable/unclassified availability remains included favorably and creates governed conditions.

These rules preserve honest D05-A characterization and prevent later D07 choice from inheriting an artificially pessimistic substrate.

## 4. Route-B visibility firewall replaces floor-recipe firewall

Before any human-visible D05 ceiling value is released to an actor capable of modifying the final scientific protocol, require:

`ROUTE_B_FINAL_PROTOCOL_FIREWALL_SATISFIED = TRUE`.

The frozen contract defining that gate lives in `BLUE_POWER_ROUTE_B_DECISION_2026-09-17.md`.

At minimum, the publication identity must bind the hashes/states of:

- D09 EC1;
- completed common mini-D09 recipe;
- `A_CONSTRUCTOR` plus the `C_claim(G)` homogeneity/domain rule;
- final-D07 selection procedure;
- final-inference selection/error-control contract;
- alpha/error-control and target-power rules that could otherwise be adapted to D05 ceilings.

Mechanical access separation may permit computation before all objects are finalized, but it does not authorize human-visible ceiling release to protocol-mutating actors.

**Invariants**

- `ROUTE_B_FIREWALL_PRECEDES_CEILING_VISIBILITY`
- `ROUTE_B_CONTRACT_FREEZE_IS_NOT_AUTOMATIC_VISIBILITY_AUTHORIZATION`
- `NO_CEILING_INFORMED_FINAL_PROTOCOL_DESIGN`

## 5. D05A pass identity under Route B

Every current-lineage `D05A_PASS_ID` must bind at minimum:

- protocol/science hashes;
- metric-surface hash;
- this Route-B amendment hash;
- Route-B route-decision hash;
- stopping/replay rule hash;
- reconciliation-rule hash;
- `EXPECTED_MANIFEST_HASH`;
- Route-B firewall contract state/hash bundle;
- source snapshot/epoch identity;
- implementation commit;
- parent pass where applicable;
- execution environment identity sufficient for reproducibility.

A pre-D07 power-floor derivation hash is no longer part of current-lineage pass identity.

## 6. Atomic publication artifact under Route B

A completed current-lineage D05-A publication artifact binds at minimum:

- `D05A_PASS_ID`;
- all authority hashes;
- completion state;
- denominator verdict;
- permitted D05-A surface outputs;
- sealed-envelope proof reference;
- open-condition ledger reference;
- `EARLY_POWER_AUTHORITY_STATE`;
- Route-B firewall satisfaction proof/hash bundle;
- publication timestamp;
- implementation commit.

It does not contain `N_RAW_REQUIRED_FLOOR` or a legacy effective-sample floor.

## 7. Partial exposure semantics

Visible partial output still forbids silent retry.

If a D05 ceiling is exposed before Route-B firewall satisfaction to an actor capable of mutating the final protocol:

`CEILING_BEFORE_ROUTE_B_FIREWALL_EXPOSURE`.

That exposure must remain in lineage and blocks authority for any later protocol element that was designed/tuned using the exposed ceiling.

No claim that “outcomes remained blind” cures this contamination.

## 8. Replay classes

`IDENTICAL_REPLAY` now requires the same Route-B route-decision/firewall authority bundle rather than the same pre-D07 floor-recipe hash.

`REPAIRED_REPLAY` remains a full pass under a new `D05A_PASS_ID` after independent semantic-equivalence certification.

A change to the Route-B final-protocol firewall contract or another authority-bearing scientific input creates a new scientific/pass lineage as applicable; it is not an identical replay.

## 9. Irreversibility

After any human-visible ceiling exposure in this lineage:

`ROUTE_A_REACTIVATION_FORBIDDEN_SAME_LINEAGE`.

The current D05-A ceilings may not be used to construct a new pre-D07 floor and then retroactively claim early-impossibility authority.

## 10. D19 and D07 dependency placement

D19 adverse-treatment mechanics are not required merely to count D05-A objects. They must be consumable before final robustness inference uses missing-outcome treatment.

The public-knowledge/entry function is not required for the raw D05 crossing-count ceiling but must be specified before final entry/outcome geometry consumes it.

Final D07 geometry remains post-D05-A under the separately frozen selection procedure.

## 11. Current state

- D05-A execution: **still not executed**
- expected SEC manifest: **still not materialized/hashed**
- early power kill: **retired current lineage**
- pre-D07 power-floor inputs/invariants: **N/A CURRENT LINEAGE**
- Route-B firewall contract: **frozen**
- Route-B firewall satisfaction: **not yet satisfied**
- human-visible ceiling release: **not yet authorized**

## 12. Core invariants

- `EARLY_POWER_ELE_RETIRED_CURRENT_LINEAGE`
- `RETIRED_CONSUMER_RETIRES_ROUTE_SPECIFIC_INVARIANTS`
- `ROUTE_B_FIREWALL_PRECEDES_CEILING_VISIBILITY`
- `NO_CEILING_INFORMED_FINAL_PROTOCOL_DESIGN`
- `D05_CEILINGS_REMAIN_DESCRIPTIVE_FEASIBILITY_OBJECTS`
- `D05A_PASS_ID_BINDS_ROUTE_B_AUTHORITY_BUNDLE`
- `ROUTE_A_REACTIVATION_FORBIDDEN_SAME_LINEAGE`
