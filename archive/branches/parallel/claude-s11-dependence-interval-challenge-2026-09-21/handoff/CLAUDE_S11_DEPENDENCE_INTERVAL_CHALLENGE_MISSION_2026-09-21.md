# CLAUDE — S11 DEPENDENCE / INTERVAL INDEPENDENT METHODS CHALLENGE — 2026-09-21

ROLE:

`INDEPENDENT SCIENTIFIC-METHODS REVIEWER`

You are NOT Blue.
You are NOT the Product Builder.
You are NOT the prior scientific-specification author.
You are NOT Astra F11.

REPOSITORY:

`fahimahmedb/Quant-Trade`

WORK ONLY ON:

`parallel/claude-s11-dependence-interval-challenge-2026-09-21`

MISSION BASE:

`3f54cd5dd4ee879b4b10ff7052939e0fb0187437`

DO NOT CREATE ANOTHER BRANCH.

## 0. Launch gate

First:

```bash
git fetch origin --prune
git rev-parse HEAD
git rev-parse origin/parallel/claude-s11-dependence-interval-challenge-2026-09-21
git rev-parse origin/blue/master-v2-2026-09-20
```

Verify:
- assigned branch descends from the exact mission base;
- Blue has not superseded S11 with a newer methods decision;
- no competing S11 reviewer branch/delivery already exists.

If superseded or duplicated, STOP and report the exact newer authority.

## 1. Read only required authority

Read:

1. `QUANT_NORTH_STAR.md`
2. `governance/BLUE_RESEARCH_FROZEN_EFFECT_ESTIMATE_PRESTAGE_2026-09-21.md`
   - especially §§9–12
3. `governance/BLUE_POST_P0_VERTICAL_PREBIGBUILD_CORRECTION_SPEC_2026-09-21.md`
   - especially §13
4. the exact D07 / D19 / EC1 authorities cited by those sections
5. pinned Forward scientific inference implementation:
   `parallel/claude-forward-data-2026-09-20@83521dbfdd90027c90d04adfb7d814593c2355c5`
6. pinned Economic coordinate/decision implementation:
   `parallel/claude-economic-v2-2026-09-20@35dff27b8fac53618da434ee6d31febbddcc0e69`

Do not reopen S01–S10 or S12–S17 unless a direct contradiction with S11 requires it.

## 2. Fixed starting point

Blue has already closed the first-slice scientific producer except S11.

Current state:

```text
SCIENCE_SPEC_STATE = PARTIALLY_CLOSED / BLOCKED_S11_DEPENDENCE_INTERVAL
VERTICAL_LOOP_BUILD_SPEC = NOT_FROZEN / ONLY_S11_OPEN
PRODUCT_IMPLEMENTATION_AUTHORIZED = FALSE
```

The rejected S11 candidate used connected dependence components over issuer/corporate and overlapping influence spans, then required:

`G >= 30`

within a 252-entry-session cohort.

Blue proved this impossible because each influence span occupies at least ~80 sessions,
so at most four disjoint temporal components are possible before issuer links merge more.

Do NOT rescue that design by silently changing 30 to 4.
Do NOT extend the cohort merely to satisfy 30.
Do NOT assume component independence because a graph label exists.

## 3. Exact question

Is there ONE defensible, implementable interval estimator for the fixed first-slice
allocation-weighted ratio that can handle:

- overlapping formation / ADV / holding windows;
- common SPY / market time shocks;
- repeated issuer / corporate dependence;
- allocation-state competition;
- unequal allocation weights;
- random denominator;
- the fixed 252-entry-session prospective cohort;

without outcome-tuned method choice?

The question is inferential validity, not profitability.

## 4. Required candidate contract

If a valid procedure exists, specify exactly:

- sampling/dependence assumptions;
- resampling or analytic unit;
- any block/bandwidth/nuisance rule;
- how those tuning choices are frozen before target outcomes;
- random-denominator treatment;
- confidence level and interval semantics;
- finite-sample / insufficient-information guards;
- deterministic seed/draw/quantile rules if resampling is used;
- handling of heavy concentration;
- handling of repeated issuer dependence;
- handling of common market shocks;
- failure behavior when assumptions are unsupported;
- what evidence could justify applicability to a real cohort.

Do not use:
- event-iid resampling;
- issuer-only resampling that ignores common time shocks;
- arbitrary post-outcome block selection;
- ordinary normal/t intervals without a justified dependence model;
- a new return coordinate;
- empirical tuning on target outcomes.

## 5. Finite acceptance tests

Demonstrate the recommended method on analytically tractable fixtures or a declared
finite simulation matrix covering at least:

1. simultaneous common market shocks;
2. repeated-issuer dependence;
3. overlapping windows;
4. unequal allocations;
5. random denominator;
6. one dominant exposure component;
7. insufficient-information state;
8. a null-effect state;
9. a positive-effect state;
10. a dependence-model-misspecification stress case.

For each, state:
- data-generating assumptions;
- expected qualitative behavior;
- actual method behavior;
- what would falsify the method.

Synthetic coverage can qualify numerical behavior under declared models only.
It does NOT prove real-world independence or edge.

## 6. Literature / support

Use primary methodological support where needed.

You may use established methods literature, but distinguish:
- mathematical support for an estimator;
- simulation/stress evidence;
- real-world applicability assumptions.

Do not treat a paper citation as proof that Quant's cohort satisfies the paper's assumptions.

## 7. Allowed conclusions

### PASS

Return:

`S11_READY_FOR_BLUE_FREEZE`

only if you provide one complete implementable S11 contract whose own sample/information
requirements are feasible under the fixed cohort and whose assumptions are explicit.

### BLOCKED

Return:

`S11_BLOCKED_<EXACT_REASON>`

if no defensible method can be justified under the fixed first-slice design.

In that case identify:
- the exact missing assumption/evidence;
- why it is necessary;
- the smallest scientifically legitimate resolution.

Do NOT output a menu of speculative future missions.

## 8. Scope limits

Do NOT:
- implement Product code;
- implement the estimator in production;
- modify P0;
- touch target host;
- change capital state;
- reopen F11;
- redesign Product architecture;
- claim profitable Form-4 edge;
- change the 252-session cohort after seeing outcomes;
- change the frozen Economic coordinate.

## 9. Exit discipline

This is ONE bounded independent methods challenge.

Stop after one final delivery.

A second review cycle requires a new concrete contradiction and explicit Blue authority.

## 10. Required handoff

Write exactly:

`handoff/CLAUDE_S11_DEPENDENCE_INTERVAL_CHALLENGE_2026-09-21.md`

Include:

```text
MISSION_BASE =
S11_METHOD =
S11_ASSUMPTIONS =
S11_FINITE_GUARDS =
S11_RANDOM_DENOMINATOR_HANDLING =
S11_INTERVAL_SEMANTICS =
S11_APPLICABILITY_EVIDENCE =
S11_LIMITATIONS =
S11_TARGETED_FALSIFIERS =
S11_VERDICT =
```

Final verdict must be exactly:

`S11_READY_FOR_BLUE_FREEZE`

or

`S11_BLOCKED_<EXACT_REASON>`

Commit and push only the final handoff to the assigned branch.

Return control to Blue.
