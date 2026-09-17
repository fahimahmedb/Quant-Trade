# BLUE POWER-ROUTE DECISION — ROUTE B FINAL PROTOCOL ONLY

**Date:** 2026-09-17  
**Status:** CLOSED / FROZEN DECISION  
**Authority:** Blue Team / Mission Control  
**Lineage:** current Form 4 scientific lineage

## 1. Decision

The current lineage does **not** pursue a pre-D07 global power-floor / early-impossibility route.

Active route:

`ROUTE_B_FINAL_PROTOCOL_ONLY`.

The two pre-D07 power-impossibility Economic Learning Events are retired for this lineage:

- `CLAIM_POPULATION_TOO_SPARSE_FOR_REQUIRED_POWER`
- `POWER_IMPOSSIBLE_DUE_TO_AVAILABILITY`

They are not merely unresolved; they are **not reachable authority states in the current lineage**.

D05-A retains its outcome-blind descriptive, denominator, availability, condition-ledger, unit-conversion and robustness-routing roles, but it cannot issue a pre-D07 power kill.

## 2. Why Route A is unavailable

The corrected Route-A floor would require a non-trivial lower bound on raw observations required that is valid over the complete honest pre-D07 scientific/deployment domain.

For the deployment-weighted estimator frozen by D09 EC1, Route A must prevent an admissible weight/covariance configuration from becoming arbitrarily precise.

For normalized admissible weights `w` and the relevant covariance object `Sigma`, PSD establishes only:

`w' Sigma w >= 0`.

It does not establish:

`w' Sigma w >= epsilon > 0`.

Even positive/equal weights do not prevent cancellation. Example:

`w=(1/2,1/2)` and `Sigma=[[1,-1],[-1,1]]`

give a PSD covariance matrix with:

`w' Sigma w = 0`.

The frozen insider-information mechanism asserts an average economic effect on the affected security. It does not assert a uniform lower eigenvalue, non-cancellable idiosyncratic component, factor-structure restriction, or other covariance condition sufficient to keep weighted estimator variance bounded away from zero over all admissible geometries, policies and capital domains.

Adding such a restriction solely to obtain a useful floor would narrow/change the honest scientific claim space to rescue Route A.

Therefore:

`RD2_UNIFORM_FLOOR_TRIVIAL`.

The non-trivial global floor is not identifiable on the honest current scientific domain.

## 3. Consequence for `N_RAW_REQUIRED_FLOOR`

The current lineage no longer seeks an authority-bearing non-trivial `N_RAW_REQUIRED_FLOOR` for pre-D07 rejection.

Any formal infimum that collapses to the trivial minimum admissible raw count has no useful kill authority.

Accordingly:

`PRE_D07_POWER_FLOOR_AUTHORITY = RETIRED_CURRENT_LINEAGE`.

No external numerical floor-source search is authorized for this lineage.

Existing D08 floor-transform and external-transport artifacts are retained as historical/scientific work products but are inactive for the current lineage unless a future Blue decision creates a new lineage with independently justified assumptions.

## 4. Structural reason the early-kill region contracts

The early Route-A kill would have required:

`N_obs_ceiling < N_RAW_REQUIRED_FLOOR`.

The scientific protections intentionally move both sides against false rejection:

- D05 uses generous valid observation ceilings;
- the power floor takes the most favorable admissible detection configuration;
- expansion of the admissible statistical/deployment domain can only preserve or lower the infimum;
- additional independent admissible external sources under a minimum rule can only preserve or lower the floor.

Thus:

`ANTI_FALSE_KILL_PROTECTIONS_MONOTONICALLY_SHRINK_EARLY_KILL_REGION`.

This does not estimate `p_K`; the route is closed because useful authority itself is not identifiable, not because `p_K` was estimated as small.

## 5. D05-A authority after this decision

D05-A remains required.

It may produce and, once the Route-B visibility firewall is satisfied, publish authorized quantities including:

- denominator/reconciliation states;
- qualification counts;
- source/parsing/PIT/market availability states;
- claim-density upper-bound outputs;
- available-substrate upper-bound outputs;
- open recovery/classification conditions;
- Branch-B missingness/robustness routing inputs;
- unit/conversion proof references.

These ceilings are descriptive/feasibility objects in Route B. They are **not compared to a pre-D07 power floor**.

The active power status exposed by D05-A is:

`EARLY_POWER_AUTHORITY_STATE = ROUTE_B_NO_PRE_D07_POWER_KILL`.

No `POWER_AVAILABILITY_VERDICT` implying early statistical impossibility is emitted.

## 6. Supersession of prior D05 power language

For the current lineage, this decision supersedes the active authority of the following portions of `D05_SAMPLE_SUFFICIENCY_AND_ROBUSTNESS_GENERATOR_AMENDMENT_2026-09-16.md`:

- §9 as an active Route-A construction requirement;
- §10 early power verdict theorem;
- §14 floor-recipe visibility firewall;
- §15 requirement to consume a pre-D07 raw floor;
- §16 precedence logic for early power verdicts;
- corresponding power-floor invariants in §17.

The fatal-theorem correction remains scientifically valid and historical: if a future new lineage ever reintroduces an early floor, raw ceilings may only be compared to a raw-observation requirement and no unproved `N_eff -> N_raw` bridge may be used.

This decision also supersedes the current-lineage power-specific portions of `D05A_MINIMAL_METRIC_AND_STRATUM_SURFACE.md` §§19–20 and the power-floor-specific visibility/pass-identity clauses of `D05A_STOPPING_SNAPSHOT_REPLAY_RULE.md`.

## 7. Route-B final-protocol firewall contract

The route-selection contract is now frozen as:

`ROUTE_B_FINAL_PROTOCOL_FIREWALL_CONTRACT_FROZEN`.

This is **not yet the same as permission to publish ceilings**.

Before human-visible D05 ceiling values may be released to actors capable of modifying the final scientific protocol, the following authority objects must be hash-addressable:

1. D09 EC1 effect coordinate and economic mapping semantics;
2. completed common mini-D09 derivation recipe, including BEEE/MEUE conservative-margin rule and permitted economic inputs;
3. frozen `A_CONSTRUCTOR` and the rule deriving `C_claim(G)` from demonstrated weight homogeneity;
4. a D07 final-geometry selection procedure defining permitted inputs, possible outputs, failure/indeterminate states, and prohibited sealed inputs;
5. the final-inference selection/error-control contract defining which information may select the final estimator/test, the possible outputs, failure states, and how the complete procedure preserves its announced statistical guarantees;
6. alpha/error-control policy and any target-power rule whose value could otherwise be adapted after seeing D05 ceilings.

Until all required hashes exist:

`ROUTE_B_FINAL_PROTOCOL_FIREWALL_SATISFIED = FALSE`.

D05-A may execute under mechanically proven separation, but human-visible ceiling release remains blocked to protocol-mutating actors.

Once all required objects are frozen and bound into the pass/publication identity:

`ROUTE_B_FINAL_PROTOCOL_FIREWALL_SATISFIED = TRUE`.

**Invariants**

- `ROUTE_B_CONTRACT_FREEZE_IS_NOT_AUTOMATIC_VISIBILITY_AUTHORIZATION`
- `CEILING_CANNOT_TUNE_ECONOMIC_THRESHOLD`
- `CEILING_CANNOT_TUNE_FINAL_ERROR_CONTROL`
- `PREDETERMINED_SELECTION_RULE_DOES_NOT_IMPLY_STATISTICAL_VALIDITY`

## 8. Sealed D07 information remains sealed

Route B does not authorize release of design-sensitive internal envelope information.

The following remain sealed unless separately authorized by the final selection contract:

- `C_PREVIOUS`
- `C_NEXT`
- `O1_ARGMAX`
- O1-specific crossing identities
- O2-specific trigger identities
- any equivalent design-sensitive intermediate.

A predeclared selection procedure may consume only the inputs explicitly authorized by its frozen contract.

## 9. Constructor/instance order under Route B

The current order is:

`freeze A_CONSTRUCTOR + C_claim(G) derivation rule`
→ `D05-A`
→ `discharge required conditions`
→ `freeze/select final D07 geometry G* under the pre-frozen rule`
→ `instantiate A_claim^{G*}`
→ `bind final Scientific Claim Fingerprint`
→ `D05-B / final D08 inference`
→ `outcome release when all remaining gates permit`.

The public-knowledge/entry function is a separate dependency and must be specified before any final entry/outcome geometry consumes it.

D19 adverse-treatment mechanics are not a general prerequisite to D05-A counting. They must be consumable before the final robustness inference consumes missing-outcome treatment.

## 10. Lineage irreversibility

After any human-visible D05 ceiling exposure in this Route-B lineage:

`ROUTE_A_REACTIVATION_FORBIDDEN_SAME_LINEAGE`.

A later desire to construct a pre-D07 power floor cannot use this lineage's exposed ceilings to design or tune the floor.

Reactivation would require a new scientific lineage and, at minimum:

- an independently justified scientific restriction capable of supporting a non-trivial uniform floor;
- a fully pre-frozen Route-A recipe before exposure to that new lineage's ceilings;
- no inheritance of contaminated design authority from the current exposed lineage, absent a mechanically proven separation established beforehand.

## 11. Reuse-accounting closure

The route decision does not rely on a numerical estimate of `p_K`.

For future VOI accounting:

- `R_U` means Route-B work actually displaced by prior Route-A work;
- reuse credit may not exceed the corresponding Route-B work avoided;
- `B_ONLY` work does not automatically increase the A-vs-B differential because it would also exist on the direct Route-B path;
- no component receives reuse credit twice.

These accounting rules remain available for future route comparisons but no further A/B calculation is needed for the current lineage.

## 12. Current route state

- Route A pre-D07 global power floor: **CLOSED / NOT AVAILABLE CURRENT LINEAGE**
- Route B final protocol only: **SELECTED**
- D05-A: **REQUIRED, NO EARLY POWER KILL**
- Route-B firewall contract: **FROZEN**
- Route-B firewall satisfaction: **NOT YET SATISFIED**
- D08 floor-source numerical search: **NOT AUTHORIZED**
- final D07 geometry: **NOT YET FROZEN**
- final D08 inference: **NOT YET FROZEN**
- outcome access: **NOT AUTHORIZED**

## 13. Core invariants

- `RD2_UNIFORM_FLOOR_TRIVIAL`
- `ROUTE_B_FINAL_PROTOCOL_ONLY`
- `EARLY_POWER_ELE_RETIRED_CURRENT_LINEAGE`
- `ROUTE_B_FINAL_PROTOCOL_FIREWALL_CONTRACT_FROZEN`
- `ROUTE_B_CONTRACT_FREEZE_IS_NOT_AUTOMATIC_VISIBILITY_AUTHORIZATION`
- `ROUTE_A_REACTIVATION_FORBIDDEN_SAME_LINEAGE`
- `ANTI_FALSE_KILL_PROTECTIONS_MONOTONICALLY_SHRINK_EARLY_KILL_REGION`
- `REUSE_CREDIT_CANNOT_EXCEED_DISPLACED_B_WORK`
