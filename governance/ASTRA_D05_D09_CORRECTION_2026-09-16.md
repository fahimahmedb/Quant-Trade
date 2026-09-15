# ASTRA D05–D09 CORRECTION PHASE — 2026-09-16

**Authority:** Blue Team / Mission Control  
**Review basis:** Astra adversarial review of Blue head `dfedf1e11ebee932351ee96450cf769000792d92`  
**Purpose:** record which findings Blue accepted and the exact governance repairs made. Astra findings are inputs; Blue retains decision authority.

## 1. Fatal finding accepted — F1

Astra demonstrated that the prior bridge:

`N_eff <= N_raw_observations`

is false in general under admissible negative dependence.

Therefore a D05 raw observation ceiling cannot be compared to an effective-sample requirement unless a separate unit-compatibility theorem is proven.

### Blue repair

The early-impossibility object is now:

`N_RAW_REQUIRED_FLOOR`.

For each admissible scenario:

`N_raw_required(theta) = min { n : Power_n(MEUE(theta), Sigma_n(theta), T(theta), alpha, target_power) >= target_power }`.

Then:

`N_RAW_REQUIRED_FLOOR = inf_theta N_raw_required(theta)`.

Dependence enters `Power_n` / `Sigma_n` exactly once.

D05 compares:

`raw ceiling < raw required floor`.

No authority-bearing D05 theorem now depends on `N_eff <= N_raw`.

## 2. Ceiling-contamination finding accepted

A D05 ceiling is itself decision-relevant information. Seeing it before the power-floor recipe is frozen could adapt the threshold without reading any market outcome.

### Blue repair

Before human-visible D05 ceiling publication, freeze/hash-address the complete power-floor recipe, including:

- D09 delta/MEUE mapping rule;
- deployment-domain rule;
- alpha/target power;
- transform rule;
- power-function/inference family;
- external search/admission/stop rule;
- extraction/source-uncertainty rule;
- horizon scaling if any;
- numerical-infimum certification.

Mechanical access separation is the only alternative.

## 3. Favorable-completion finding accepted

A favorable claim-density completion is not generally:

`ALL_UNRESOLVED -> QUALIFYING`.

Added qualifying observations can delay re-arm and reduce future crossings.

### Blue repair

Use either:

- exact global maximization over compatible completions; or
- a proven analytic majorant that never understates the admissible maximum.

No numeric owner-multiplicity cap may be invented for unresolved submissions.

## 4. Unit-conversion gap accepted

Accession, reporting owner, formation state, crossing and market/outcome availability are distinct scientific units.

### Blue repair

Created:

`D05A_UNIT_AND_CEILING_CONVERSION_CONTRACT.md`.

Key laws include:

- `ACCESSION_NUMBER` is submission identity;
- `REPORTING_OWNER_CIK` is owner identity;
- `1 accession != 1 owner != 1 crossing`;
- crossing derives from issuer/session formation state;
- outcome unavailability does not rewrite formation history;
- one missing object may feed multiple gates without becoming duplicate population units.

## 5. D19 authority gap accepted

D19 is conceptually decided, but the repository did not expose the adverse-treatment mechanics required by a downstream outcome robustness consumer.

### Blue repair

Created:

`D19_ADVERSE_TREATMENT_SPEC_DEPENDENCY.md`.

Until a consumable specification exists:

`D19_ADVERSE_TREATMENT_SPEC_PENDING`.

`BIAS_RULE_READY_PENDING_OUTCOME_APPLICATION` is not authority-bearing.

This does not reopen D19.

## 6. D08 external-source gaps accepted

Blue accepted Astra's point that a published point estimate is not automatically a lower bound and that source search itself requires ex-ante stopping rules.

### Blue repair

The transport contract now freezes before numerical inspection:

- search universe/procedure;
- inclusion/exclusion;
- duplicate/publication-family handling;
- stopping rule;
- extraction schema;
- source uncertainty conversion;
- alpha/target power/inference family.

All sources normalize to the common object:

`L_s_raw = lower bound on raw observations required`.

The authority floor uses:

`min_s L_s_raw`.

## 7. Multi-transform dormant bug accepted

An admitted transform with no source cannot simply be omitted from a generic transform minimum, because its unknown requirement might lie below the published floor.

### Blue repair

In any future multi-transform lineage:

`EVERY_ADMISSIBLE_TRANSFORM_MUST_BE_INSTANTIATED_OR_PROVEN_DOMINATED`.

Otherwise:

`POWER_REQUIREMENT_UNRESOLVED_TRANSFORM_COVERAGE`.

The current singleton remains a freeze candidate subject to the D09 delta gate.

## 8. Execution-cost / statistical-variance clarification

For the current candidate transform:

`T_SPY_SIMPLE_EXCESS_20 = R_security_20 - R_SPY_20`,

execution mean/cost may enter `Phi -> BEEE -> MEUE`.

Execution variance is not automatically added to the variance of this gross market-return transform.

A net executed-return estimand would be a distinct transform requiring explicit execution-error variance and covariance treatment.

## 9. D07 public-observability gap accepted

Logical O2 trigger identity is not necessarily the time at which the complete crossing becomes public.

### Blue repair

Created:

`D07_PUBLIC_OBSERVABILITY_ENTRY_DEPENDENCY.md`.

Final D07/entry authority must define public-knowledge time from authoritative SEC availability facts and prohibit entry before the complete crossing is public.

This blocks final entry/outcome geometry, not the D05 raw crossing-count ceiling.

## 10. Findings confirmed without reversal

Blue retained:

- the two opposite conservatisms;
- direct Branch-B robustness routing without `B_route` / `m_star`;
- same missing object feeding A and B without duplication;
- `min` across independently admissible external raw floors as false-impossibility protection;
- joint/raw required-sample infimum over the frozen authority domain;
- domain expansion requiring reevaluation;
- pure domain contraction preserving prior impossibility authority when all other science remains unchanged;
- D08 singleton only as `FREEZE_CANDIDATE` pending D09 delta compatibility.

## 11. Current blockers after correction

The correction phase does **not** authorize D05 early power-impossibility yet.

Remaining blockers are explicit:

1. D09 consumable derivation specification:
   - delta coordinate;
   - `Phi` and BEEE root;
   - D02/D03 deployment domain;
   - MEUE map;
   - power-floor recipe components.
2. D08 singleton delta compatibility.
3. External raw-floor source search/measurement under the frozen transport recipe.
4. D05 expected SEC manifest materialization/hash.
5. D05 ceiling implementation proof under the unit/conversion contract.
6. D19 adverse-treatment specification before outcome robustness authority.
7. D07 public-observability/entry specification before final outcome geometry.

## 12. Governance lesson

Reusable dependency-pull law:

`DOWNSTREAM_CONSUMER_MUST_RESOLVE_TO_HASHED_AUTHORITY_ARTIFACT`.

A hash alone is insufficient. The artifact must define the units, domain, assumptions, mappings and inequality direction actually consumed by the gate.

This technique should be applied to other `DECIDED` blocks before granting operational scientific authority.
