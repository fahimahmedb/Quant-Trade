# D09 MEUE / POWER-FLOOR DERIVATION DEPENDENCY

**Status:** SUPERSEDED_FOR_THIS_LINEAGE — HISTORICAL ROUTE-A DEPENDENCY — ASTRA-CORRECTED  
**Authority:** Blue Team / Mission Control  
**Nature:** historical specification dependency for a pre-D07 power floor. It is not the active D09 blocker list for the current Route-B lineage.

## Current-lineage supersession notice — 2026-09-17

`BLUE_POWER_ROUTE_B_DECISION_2026-09-17.md` selected `ROUTE_B_FINAL_PROTOCOL_ONLY` and retired the global pre-D07 power-floor route after `RD2_UNIFORM_FLOOR_TRIVIAL`.

The current common economic coordinate/root semantics are now controlled by:

`D09_ECONOMIC_CORE_EC1_ALLOCATION_WEIGHTED_EFFECT.md`.

The remaining Route-B D09 obligations are controlled separately by:

`D09_ROUTE_B_COMMON_CORE_REMAINDER_2026-09-17.md`.

Accordingly, the following objects in this historical dependency are **not current-lineage obligations**:

- `MEUE_POWER_FLOOR_MAP` over the full deployment domain;
- `THETA_POWER_FLOOR`;
- joint infimum optimization across the Route-A domain;
- certified numerical-infimum rule;
- external power-floor transport dependencies;
- power-floor deployment-domain expansion/contraction authority;
- floor-recipe contamination firewall.

The historical clauses below remain correct for a future lineage that independently re-authorizes Route A. They must not be imported into Route B merely because they were previously frozen.

`STATUS_CURRENT_LINEAGE = SUPERSEDED_FOR_THIS_LINEAGE`.

## 1. Why this historical artifact exists

Dependency-pull from D05/D08 reached D09 and found that the conceptual decision was not represented by a standalone hash-addressable derivation object.

Decided semantics included:

- derive `BEEE` first;
- `MEUE = BEEE + predetermined conservative economic margin`;
- economic mapping is geometry/execution aware;
- D09 power consumes MEUE rather than allowing D05 to tune it.

Astra additionally established that a Route-A one-sided D05 theorem must use a raw-observation requirement rather than an unproven effective-sample bridge.

**Governance finding:** `DECIDED != CONSUMABLE_AUTHORITY`.

## 2. Historical Route-A required specification outputs

### 2.1 `DELTA_COORDINATE_COMPATIBILITY_GATE`

Specify exactly what `delta` means in:

`Phi(delta, C, G, execution)`.

If delta is not on the coordinate assumed by a Route-A floor transform, D09 does not redefine delta to fit that transform.

### 2.2 `PHI_AND_BEEE_ROOT_CONTRACT`

Define the exact economic value function and break-even equation, economic terms, units/sign conventions, root existence/uniqueness and failure states.

Research/program sunk costs remain outside market/deployment MEUE unless an already-decided upstream rule explicitly places them there.

### 2.3 Historical `THETA_PROGRAM_DEPLOYMENT`

The Route-A power-floor economic domain was defined as execution-feasible and ex-ante program-intended, with dimensions capable of altering `Phi` or the power object.

This full-domain construction is no longer a Route-B requirement. Route B still requires outcome-blind economic/allocation semantics and a valid final geometry-specific instantiation.

### 2.4 Execution terms declare their moment and estimand role

Each execution component must still, when consumed by final science, declare whether it enters expected economic cost/mean, statistical variance of the tested outcome, or both through separately named parameters with explicit covariance treatment.

For the gross SPY-excess primitive outcome, execution mean/cost may enter `Phi -> BEEE -> MEUE`, but execution variance is not automatically added to the statistical variance of the gross market-return transform.

This principle remains reusable in Route B because it is estimand semantics, not a floor-specific rule.

### 2.5 Historical execution-feasible friction envelope

The Route-A contract required an execution-feasible friction domain frozen before D05 ceiling visibility and used it in the one-sided floor construction.

For Route B, the need to freeze an outcome-blind friction rule remains, but the one-sided floor direction does **not** carry over. The active Route-B rule is specified in `D09_ROUTE_B_COMMON_CORE_REMAINDER_2026-09-17.md`.

### 2.6 Historical `MEUE_POWER_FLOOR_MAP`

Route A required a deterministic/hashable map over the full frozen deployment domain:

`theta -> {MEUE(theta), execution_mean_components(theta), economic_geometry_inputs(theta)}`.

This full-domain map is `N/A_CURRENT_LINEAGE`.

Route B needs the common mapping recipe frozen outcome-blind and a final instantiation after `G*` and the authorized capital/policy instance are fixed.

## 3. Historical corrected downstream power-floor object

For each admissible Route-A scenario:

`N_raw_required(theta) = min { n : Power_n(MEUE(theta), Sigma_n(theta), T(theta), alpha, target_power) >= target_power }`.

and:

`N_RAW_REQUIRED_FLOOR = inf_theta N_raw_required(theta)`.

Dependence enters the power construction exactly once.

These raw-count unit corrections remain scientifically valid but have no active D05 consumer in the current lineage.

## 4. Historical joint optimization and safe relaxations

Route A required a joint infimum over one common admissible scenario and prohibited combining incompatible scenario-specific favorable components without an independent lower-bound proof.

`N/A_CURRENT_LINEAGE` for Route B.

## 5. Historical continuous-domain numerical rule

Route A required a certified numerical lower bound on the continuous-domain infimum rather than an uncertified grid minimum.

`N/A_CURRENT_LINEAGE` for Route B.

## 6. Historical deployment-domain changes

Expansion/contraction rules governed preservation of prior Route-A impossibility authority.

`N/A_CURRENT_LINEAGE` because no current-lineage pre-D07 impossibility authority exists.

## 7. Historical ceiling-contamination firewall

Route A required all floor-moving rules frozen before ceiling visibility.

This is superseded by the current-lineage Route-B firewall:

`ROUTE_B_FINAL_PROTOCOL_FIREWALL_CONTRACT_FROZEN`

with satisfaction still required before ceiling publication to protocol-mutating actors.

## 8. Dependency-pull governance technique — retained

The reusable governance rule remains active:

`DOWNSTREAM_CONSUMER_MUST_RESOLVE_TO_HASHED_AUTHORITY_ARTIFACT`.

A hash is necessary but not sufficient: the artifact must define the units, domain, assumptions, mappings and decision semantics actually consumed downstream.

If a former consumer disappears because a route is retired, its dependency must be marked superseded rather than left as a phantom blocker.

**Invariant:** `RETIRED_CONSUMER_RETIRES_ITS_ROUTE_SPECIFIC_DEPENDENCIES`.

## 9. Current blocker chain

The historical chain:

`D05 early power-impossibility authority <- N_RAW_REQUIRED_FLOOR <- D08 <- D09 power-floor map`

is closed and inactive for this lineage.

The current Route-B chain is instead:

`D05 ceiling visibility`
← `ROUTE_B_FINAL_PROTOCOL_FIREWALL_SATISFIED`
← common mini-D09 completion + `A_CONSTRUCTOR/C_claim(G)` rule + D07 selection procedure + final-inference selection/error-control contract.
