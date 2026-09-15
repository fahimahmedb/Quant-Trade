# D09 MEUE / POWER-FLOOR DERIVATION DEPENDENCY

**Status:** DECIDED_NOT_SPECIFIED — ASTRA-CORRECTED — BLOCKING CONSUMABLE POWER-FLOOR AUTHORITY  
**Authority:** Blue Team / Mission Control  
**Nature:** specification/execution of already-decided D09 semantics, not a reopening of D09's economic decision.

## 1. Why this artifact exists

Dependency-pull from D05/D08 reached D09 and found that the conceptual decision is not yet represented by a standalone hash-addressable derivation object.

Current decided semantics include:

- derive `BEEE` first;
- `MEUE = BEEE + predetermined conservative economic margin`;
- economic mapping is geometry/execution aware:
  `V_annual = Phi(delta, C, G, execution)`;
- D09 power consumes MEUE rather than allowing D05 to tune it.

Astra review additionally established that the one-sided D05 theorem must use a **raw-observation requirement**, not an unproven bridge from effective sample to raw observations.

The repository does not yet expose an authority-bearing specification for the exact `delta` coordinate, root equation, deployment domain, execution-cost decomposition and deterministic MEUE mapping needed by D08.

**Governance finding:** `DECIDED != CONSUMABLE_AUTHORITY`.

## 2. Required D09 specification outputs

The downstream consumer must resolve to a hash-addressable artifact implementing the following objects.

### 2.1 `DELTA_COORDINATE_COMPATIBILITY_GATE`

Specify exactly what `delta` means in:

`Phi(delta, C, G, execution)`.

This is a gate, not a confirmation exercise.

If delta is not on the coordinate assumed by `D08_POWER_FLOOR_OUTCOME_TRANSFORM_BOUNDARY.md`, D09 does not redefine delta to fit D08.

Instead D08 must return to transform admission using the true D09 coordinate.

**Invariant:** `DELTA_MISMATCH_INVALIDATES_FLOOR_TRANSFORM_ASSUMPTION`.

### 2.2 `PHI_AND_BEEE_ROOT_CONTRACT`

Define the exact economic value function and break-even equation.

Conceptually:

`Phi(BEEE, C, G, execution) = 0`

or the exact mathematically equivalent root condition.

The contract must state:

- which economic terms enter expected value;
- their units and sign conventions;
- whether a BEEE root exists;
- whether it is unique;
- what state is emitted when there is no economically meaningful root or multiple roots.

Research/program sunk costs remain outside the market/deployment MEUE unless an already-decided upstream rule explicitly places them there.

**Invariants**

- `BEEE_ROOT_EXISTENCE_AND_UNIQUENESS_MUST_BE_SPECIFIED`
- `PROGRAM_COST_DOES_NOT_SILENTLY_ENTER_MARKET_MEUE`

### 2.3 `THETA_PROGRAM_DEPLOYMENT`

The power-floor economic domain is not all theoretically executable capital.

Define:

`THETA_PROGRAM_DEPLOYMENT = THETA_EXECUTION_FEASIBLE ∩ THETA_EX_ANTE_PROGRAM_INTENDED`.

The intended-deployment component must resolve upstream to D02/D03 authority, not be invented inside D09 after D05 ceiling values or market outcomes are observed.

The domain must name the dimensions that materially alter `Phi` or the statistical power object, including where applicable:

- capital/equity budget;
- feasible allocation / position size;
- ADV/capacity constraints;
- event frequency / overlap geometry inputs already authorized for this stage;
- capital saturation;
- execution regime.

This prevents the floor from being protected by a capital scale the program never contemplated deploying.

### 2.4 Execution terms declare their moment and estimand role

Each execution component must declare whether it enters:

- expected economic cost / mean inside `Phi`;
- statistical variance of the **tested outcome transform**;
- or both through separately named parameters with an explicit covariance model.

**Invariants**

- `EXECUTION_TERM_DECLARES_ITS_MOMENT`
- `MEAN_AND_VARIANCE_EXECUTION_PARAMETERS_ARE_DISTINCT_AUTHORITY_OBJECTS`
- `EXECUTION_VARIANCE_REQUIRES_ESTIMAND_COMPATIBILITY`

For the current D08 candidate:

`T_SPY_SIMPLE_EXCESS_20 = R_security_20 - R_SPY_20`

which is a gross market-return transform. Therefore execution mean/cost may enter `Phi -> BEEE -> MEUE`, but execution variance is **not automatically added to the variance of T**.

If a future inference target is net executed return, it is a distinct transform and must explicitly define execution-error variance and covariance with market return, e.g. the relevant terms in:

`Var(T - execution_error)`.

No generic rule `execution_variance -> Sigma_floor` is authority-bearing for the current gross transform.

### 2.5 Execution-feasible friction envelope

The admissible friction domain is bounded by execution feasibility, not by a prior on expected insider alpha.

A friction bound may be an explicit governance assumption when calibration is unavailable, but it must be economically/execution feasible and frozen before D05 ceiling visibility / outcome inspection.

It must never be justified by choosing a value that makes the hypothesized alpha look plausible.

**Invariants**

- `FRICTION_BOUND_USES_EXECUTION_FEASIBILITY_NOT_ALPHA_PRIOR`
- `FRICTION_BOUND_PRECEDES_D05_CEILING_VISIBILITY`

### 2.6 `MEUE_POWER_FLOOR_MAP`

D09 should expose a deterministic/hashable mapping over the frozen deployment domain:

`theta -> {MEUE(theta), execution_mean_components(theta), economic_geometry_inputs(theta)}`.

Where execution-uncertainty components are relevant to a separately admitted statistical transform, they must be exposed as separately named objects rather than silently folded into the MEUE map.

D09 should not collapse the map to a single scenario merely to simplify D08.

## 3. Correct downstream power-floor object

The D05 early-impossibility gate consumes a raw-observation requirement.

For each fully specified admissible statistical/economic scenario `theta`, define:

`N_raw_required(theta) = min { n : Power_n(MEUE(theta), Sigma_n(theta), T(theta), alpha, target_power) >= target_power }`.

`Sigma_n(theta)` here represents the covariance/variance structure of the admitted tested outcome under `n` raw observations. Dependence is handled inside the power calculation exactly once.

The one-sided floor is:

`N_RAW_REQUIRED_FLOOR = inf_{theta in THETA_POWER_FLOOR} N_raw_required(theta)`.

`THETA_POWER_FLOOR` must be a frozen authority-covered domain constructed from `THETA_PROGRAM_DEPLOYMENT` plus the admitted D08 statistical/transport uncertainty dimensions.

D05 then compares raw observation ceilings only to this raw observation requirement.

**Invariants**

- `RAW_CEILING_COMPARES_ONLY_TO_RAW_REQUIREMENT`
- `DEPENDENCE_ENTERS_POWER_FLOOR_EXACTLY_ONCE`
- `NO_UNPROVEN_NEFF_TO_NRAW_BRIDGE`

## 4. Joint optimization and safe relaxations

The default authority object is the joint infimum over a common admissible scenario because MEUE, statistical uncertainty and deployment geometry can co-vary.

Do not combine scenario-specific values and present them as one realizable scenario when no such scenario exists.

**Invariant:** `POWER_FLOOR_OPTIMIZES_JOINTLY_OVER_ONE_SCENARIO`.

A mathematically relaxed lower bound that combines separately favorable components may be used **only** when an independent proof establishes that the relaxation is less than or equal to the true joint infimum. Such a relaxation must be labelled as a bound, not as an attainable scenario.

**Invariant:** `NONREALIZABLE_RELAXATION_REQUIRES_LOWER_BOUND_PROOF`.

## 5. Continuous-domain numerical rule

There is no assumption that the infimum occurs at a boundary of the deployment/statistical domain.

If the domain is continuous, the numerical procedure must be frozen before result inspection and must deliver a certified lower bound, not merely a grid minimum whose error direction is unknown.

Required authority property:

`N_floor_authorized <= true_inf_theta N_raw_required(theta)`.

An implementation may use exact optimization, interval methods, deterministic gridding with a proven error bound, or another method satisfying the inequality.

**Invariant:** `NUMERICAL_INFIMUM_MUST_BE_A_CERTIFIED_LOWER_BOUND`.

## 6. Deployment-domain changes

If the deployment domain expands:

`THETA_new ⊃ THETA_old`

then the infimum may fall. Prior impossibility authority must be reevaluated.

If the deployment domain contracts:

`THETA_new ⊂ THETA_old`

then the infimum cannot fall **provided the scientific function, estimand, units, population, transport assumptions and ceiling construction are otherwise unchanged**.

A change to those objects is not a mere domain contraction and does not automatically inherit prior authority.

**Invariants**

- `DEPLOYMENT_DOMAIN_EXPANSION_REQUIRES_POWER_FLOOR_REEVALUATION`
- `PURE_DEPLOYMENT_DOMAIN_CONTRACTION_PRESERVES_PRIOR_IMPOSSIBILITY_AUTHORITY`

## 7. Ceiling-contamination firewall

All rules capable of moving `N_RAW_REQUIRED_FLOOR` must be frozen before human-visible D05 ceiling values are available to actors who can modify those rules.

This includes:

- the D09 objects in §2;
- alpha / target power;
- the D08 transform space;
- the power-function/inference family used for the floor;
- external source admission/search/stop rules;
- source uncertainty treatment;
- numerical-infimum rule.

Mechanical access separation is an acceptable alternative if it proves recipe designers could not inspect D05 ceiling values.

**Invariants**

- `POWER_FLOOR_RECIPE_PRECEDES_D05_CEILING_VISIBILITY`
- `NO_CEILING_INFORMED_POWER_FLOOR_DESIGN`

## 8. Dependency-pull governance technique

This gap was discovered by following a real downstream consumer from D05 to D08 to D09, not by abstractly rereading D09.

General reusable rule:

`DOWNSTREAM_CONSUMER_MUST_RESOLVE_TO_HASHED_AUTHORITY_ARTIFACT`.

A hash is necessary but not sufficient: the artifact must also define the units, domain, assumptions, mappings and inequality direction actually consumed by the downstream gate.

If the chain terminates in conceptual prose, handoff language, an ambiguous unit, or an unproved inequality, that dependency is:

`NOT_YET_CONSUMABLE_AUTHORITY`.

This dependency-pull audit should be reused on other `DECIDED` blocks before granting operational scientific authority.

## 9. Current blocker chain

`D05 early power-impossibility authority`
← `N_RAW_REQUIRED_FLOOR`
← `D08 raw-count lower-bound construction`
← `D08 floor outcome transform`
← `D09 delta / MEUE mapping + deployment domain`
← **this missing specification object**.

No external numerical floor-source search and no human-visible D05 ceiling should precede freeze of the authority-bearing floor recipe, absent mechanically proven access separation.
