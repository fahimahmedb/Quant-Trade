# CLAUDE — S11 DEPENDENCE / INTERVAL INDEPENDENT METHODS CHALLENGE — DELIVERY — 2026-09-21

ROLE: independent scientific-methods reviewer (not Blue, not Product, not the prior
S11 author, not Astra F11). ONE bounded delivery.

## 0. Launch gate (satisfied)

```
HEAD                       = b851113b44083d38739088efdf17e8aff65b672e
assigned branch            = b851113b44083d38739088efdf17e8aff65b672e (identical)
mission base 3f54cd5..     = ancestor of HEAD (yes)
origin/blue/master-v2-2026-09-20 = cd9c0e8ec5d4d944970a04faf36a1fc8d1713647 (no newer S11 disposition found there)
competing S11 delivery      = none found (only the mission file exists under handoff/)
```

No supersession or duplication found. Proceeding.

## 1. Authority read

`QUANT_NORTH_STAR.md`; `governance/BLUE_RESEARCH_FROZEN_EFFECT_ESTIMATE_PRESTAGE_2026-09-21.md`
§§9–12 (decision table S01–S17, §10.4 O4/interval procedure, §11 unresolved
contradiction, §12 challenge charter); `governance/BLUE_POST_P0_VERTICAL_PREBIGBUILD_CORRECTION_SPEC_2026-09-21.md`
§13 confirms S11 is the sole open blocker and adds no new interval constraint.
Pinned `parallel/claude-forward-data-2026-09-20@8352...c5:src/quant/science/inference.py`
inspected directly (`ratio_estimate`, `cluster_bootstrap_ratio`) to ground the
analysis in the actual candidate mechanics, not a paraphrase. Pinned economic
coordinate `parallel/claude-economic-v2-2026-09-20@35dff...069` not modified.

## 2. Restated structural fact (Blue's proof, not re-derived, only used)

Entry indices run 0..251. Each connected component's influence span (formation/ADV
lead + holding + 20-session buffers each side) occupies **≥80 sessions**. Two
components can only be temporally disjoint if their entries are separated by ≥80
sessions, so the cohort admits at most `floor(251/80)+1 = 4` disjoint components
before issuer links merge more of them together. This is a **hard combinatorial
ceiling on the cohort as already frozen**, not a tunable guard value.

## 3. Why this defeats every established dependence-robust interval class, not only G>=30

The rejected candidate is one instance of "resample/aggregate independent units."
Checking the other established candidates against the same ceiling (G_max = 4,
possibly fewer once issuer recurrence is applied) shows they all fail for the same
underlying reason: **every one of them requires the number of (approximately)
independent evidence units to grow, and this cohort's geometry fixes it at ≤4.**

- **Cluster-robust sandwich / delta method** (this repo's own `ratio_estimate`,
  `METHOD_DELTA_CLUSTERED`). Its normal interval is justified by a CLT over a
  growing number of cluster sums; the code's `G/(G-1)` term is a finite-sample
  bias correction *on top of* that asymptotic, not a substitute for it. Applied
  literature (Cameron & Miller 2015) already treats G<20-30 as unreliable and
  G<10 as unusable without further correction. At G≤4 the between-cluster sample
  variance has 3 degrees of freedom; the normal quantile is not a defensible
  approximation to its sampling distribution. This is precisely the "ordinary
  normal/t interval without a justified dependence model" the mission forbids —
  clustering the variance does not change that at G=4.
- **Nonparametric cluster bootstrap** (this repo's own `cluster_bootstrap_ratio`,
  `METHOD_CLUSTER_BOOTSTRAP`, resample G whole clusters with replacement). With
  G=4, a resample is an unordered multiset of 4 draws from 4 labels; the number of
  distinct achievable resample compositions is `C(G+G-1, G) = C(7,4) = 35`. The
  percentile distribution therefore has **at most 35 support points** regardless
  of how many of the requested draws (9,999 or any other count) are taken — most
  of the requested draws are exact duplicates of an existing support point. A
  fixed, small, discrete support set is not evidence of convergence to a
  continuous sampling distribution; asking for more draws cannot manufacture
  more information than 4 independent units contain. The 2.5%/97.5% percentile
  indices land on one of those 35 fixed values, not on a stable quantile of an
  approximately continuous distribution — the interval's claimed coverage is not
  supportable.
- **Wild cluster bootstrap** (Cameron, Gelbach & Miller 2008; MacKinnon & Webb
  2018 — cited by the prestage as "methodological context, not validation").
  This is the literature's own answer to *few* clusters, so it is the strongest
  candidate to check. With Rademacher weights on G=4 clusters there are exactly
  `2^G = 16` distinct sign-flip realizations under full enumeration. The finest
  two-sided tail this can resolve is `2/16 = 0.125`, coarser than the requested
  `alpha=.05` (`0.025`/`0.975` quantiles do not exist on a 16-point empirical
  distribution; the closest achievable coverage is unavoidably granular and
  cannot be interpolated into a valid 95% claim without an additional smoothing
  model that would itself need justification and is not established for G=4 in
  this literature). MacKinnon & Webb's own results on "few treated clusters"
  examine cases with more like 6-12 clusters and still report size distortion;
  none of the literature the prestage or this review can point to establishes
  validity at G=4.
- **Reframing as a time-series long-run-variance problem** (Newey-West /
  Driscoll-Kraay HAC on a session-indexed series instead of a cluster sum) is not
  a way around the ceiling: HAC consistency needs the number of "effective"
  decorrelation windows `T/bandwidth` to be large (folklore/simulation guidance
  is roughly ≥20). The dependence-generating mechanism here (shared SPY shocks,
  issuer recurrence, formation/ADV/holding overlap) is exactly what forces the
  ≥80-session influence span, so any honest bandwidth choice is ≥80 sessions by
  the same argument Blue already made. `T/bandwidth = 252/80 ≈ 3.15` — the same
  "≈4 independent units" ceiling reappears under a different name. This is not a
  second, independent rescue; it is the identical information deficit.
- **Permutation / randomization inference** over the components (exchangeability
  under a sharp null) is bounded by `4! = 24` relabelings at best (fewer once
  issuer/SPY-shock connectivity forces some labels together), giving an
  achievable exact two-sided tail granularity no finer than `2/24 ≈ 0.083`,
  again coarser than the requested 0.05, and for the same reason: only 4
  information units exist to permute.
- **A Bayesian / partial-identification interval with an explicit dependence
  prior** does not evade the deficit either; it relocates it into a prior over
  the cross-component dependence structure. With only 4 realized units there is
  no internal evidence to calibrate that prior, and the mission forbids
  empirical tuning on target outcomes — an uncalibrated informative prior
  chosen to "make G=4 work" would be exactly the disallowed outcome-shaped
  rescue in different notation, and interval semantics would silently change
  from a frequentist sampling interval to a posterior credible interval without
  the applicability evidence to support that switch.

Every path checked collapses to the same number: **this cohort, as already
frozen (S01-S10, S12-S17), supplies at most ~4 independent temporal evidence
units, and no interval-construction method in the applicable statistical
literature — cluster-robust sandwich, nonparametric cluster bootstrap, wild
cluster bootstrap, HAC/long-run-variance, permutation, or a defensible Bayesian
alternative — is established as valid at that count.** This is stronger than
the original G>=30 finding: it is not that one particular guard threshold was
too strict, it is that the *smallest* threshold any of these methods can
defensibly claim (roughly 10-20 even for the most permissive, few-cluster wild
bootstrap literature) already exceeds what the frozen cohort geometry can ever
supply, independent of which specific numeric guard Blue had chosen.

## 4. Finite/structural demonstrations (analytically tractable; no simulation needed)

The ten required stress dimensions are covered by the combinatorial facts above,
not by running code, because the failure is in the *support size* of every
candidate resampling/asymptotic distribution, which is a property of G_max=4
alone and does not depend on the realized (a, T) values:

1. Simultaneous common market shocks / 2. repeated-issuer dependence / 3.
   overlapping windows — these are exactly what forces the ≥80-session span and
   therefore the G_max=4 ceiling; they are the *cause* of the deficit, not a
   separate case to test against a method that already fails on support size.
2. Unequal allocations / random denominator — irrelevant to the objection: the
   35-point (bootstrap) or 16-point (wild sign) or 24-point (permutation)
   support-size arguments hold for **any** finite, nonnegative (a_j, T_j)
   values, since they follow from counting label assignments, not from the
   realized weights or outcomes.
3. One dominant exposure component — makes the deficit worse (effectively
   fewer than 4 "equally informative" units), not better.
4. Insufficient-information state — this *is* the finding: the correct method
   output for this cohort is the existing D19-style `INSUFFICIENT` disposition,
   not a numeric interval.
5. Null-effect / positive-effect states — the support-size argument is
   distribution-free; it applies identically regardless of the true effect,
   so no choice of effect state rescues coverage.
6. Dependence-model-misspecification stress — moot: the objection here is prior
   to model misspecification; even a *correctly specified* dependence model
   cannot be validated or produce a non-degenerate interval from 4 units.

No numeric fixture run changes any of this, because the argument is about the
cardinality of the achievable resample/permutation/HAC-window space, which is
fixed by cohort geometry alone (S02/S06 entry rule + the ≥80-session span),
independent of realized data. Running the existing `cluster_bootstrap_ratio`
against synthetic (a, T) would only reproduce the 35-point degeneracy already
derived; it would not add applicability evidence, per the mission's own
instruction that synthetic coverage cannot establish real-world validity, and
here it cannot even establish *numerical* validity since the discreteness is
exact, not approximate.

## 5. Exact missing assumption / evidence and smallest legitimate resolution

**Missing assumption/evidence:** a cohort design (entry-session count, minimum
issuer/temporal separation, or influence-span construction) that yields enough
disjoint or weakly-dependent evidence units — realistically ≥10-20 for the most
permissive established few-cluster method (wild cluster bootstrap), ≥20-30 for
the cluster-robust sandwich or plain nonparametric cluster bootstrap — for at
least one established interval method to have a citable validity argument at
that count.

**Why necessary:** every checked method's coverage guarantee is a statement
about behavior as the number of independent units grows; at the frozen cohort's
ceiling of ~4 units, all of them degenerate to either a support-size argument
(bootstrap/wild/permutation) or an unsupported small-sample normal
approximation (sandwich/HAC), for the same underlying-information reason. No
change of estimator, kernel, seed, draw count, or numeric guard threshold
changes a count of 4.

**Smallest scientifically legitimate resolution (explicitly not performed
here, per scope limits):** redesign the cohort/allocation-constructor geometry
(e.g., a materially longer entry-session count under the existing calendar, a
different formation/ADV/holding/buffer construction that shortens the
per-component influence span, or explicit acceptance of an issuer/time-block
design that produces ≥10-20 disjoint or documented weakly-dependent units)
**before** any outcome is observed, then re-run this same challenge against the
new design. This is a first-slice/cohort-design decision, not an estimator
choice, and is out of this review's scope (`do not change the 252-session cohort
after seeing outcomes`; no new cohort is proposed or implemented here).

## Required fields

```
MISSION_BASE = 3f54cd5dd4ee879b4b10ff7052939e0fb0187437
S11_METHOD = NONE_QUALIFIES: no established dependence-robust interval method (cluster-robust sandwich, nonparametric cluster bootstrap, wild cluster bootstrap, HAC/long-run-variance reframing, permutation, or a non-outcome-tuned Bayesian alternative) has a defensible validity argument at the cohort's proven ceiling of at most ~4 disjoint temporal evidence units.
S11_ASSUMPTIONS = N/A (no candidate reaches the assumption-statement stage; the blocking fact -- G_max<=4 disjoint components under the frozen entry/influence-span rules -- is a direct consequence of already-frozen S02/S06/§10.4 rules, not a new assumption introduced here).
S11_FINITE_GUARDS = N/A for a frozen contract. The correct guard is the existing D19-style disposition INSUFFICIENT_CLUSTER_INFORMATION / DEPENDENCE_MODEL_UNSUPPORTED already named in §10.4, applied unconditionally at this cohort's fixed geometry, not just when a numeric threshold happens to be missed by chance.
S11_RANDOM_DENOMINATOR_HANDLING = N/A: no interval is produced; the point ratio sum(a*T)/sum(a) can still be reported as a diagnostic cross-check per §10.4's existing "Point ... is diagnostic only" provision, with the random denominator handled exactly as F ratio_estimate already does (finite positive total exposure required), but this is not a confidence interval and must not be presented as one.
S11_INTERVAL_SEMANTICS = NOT_APPLICABLE: no interval is certified; per §10.5/§10.4 the correct emitted state is a refusal (INSUFFICIENT_CLUSTER_INFORMATION / DEPENDENCE_MODEL_UNSUPPORTED), never a widened, clipped, or reinterpreted (e.g. Bayesian) interval substituted for the requested nominal two-sided 95% sampling interval.
S11_APPLICABILITY_EVIDENCE = None exists and none can be manufactured from this cohort: the deficit is a support-size/asymptotic-count argument that holds for any realized (a,T) values, so no synthetic fixture, additional draw count, or alternate seed changes it; only a redesigned cohort geometry (out of scope here) could later supply applicability evidence.
S11_LIMITATIONS = This review only established that the checked, established method classes fail at G_max<=4; it does not prove no method could ever exist (a bespoke, peer-validated few-unit procedure might), and it does not evaluate cohorts other than the one already frozen by S01-S17.
S11_TARGETED_FALSIFIERS = (1) A cited, peer-reviewed interval method with a stated and applicable validity argument at G=4 independent units for a ratio statistic -- none found in this review. (2) A cohort/allocation-constructor redesign (pre-outcome) that raises the disjoint-component ceiling to the range (~10-30) where an established method's own validity claim applies. (3) A documented, non-outcome-tuned dependence bound proving cross-component correlation is negligible beyond the current spans without shrinking the influence-span buffers post hoc.
S11_VERDICT = S11_BLOCKED_MAX_4_INDEPENDENT_COMPONENTS_INSUFFICIENT_FOR_ANY_ESTABLISHED_INTERVAL_METHOD
```

`S11_BLOCKED_MAX_4_INDEPENDENT_COMPONENTS_INSUFFICIENT_FOR_ANY_ESTABLISHED_INTERVAL_METHOD`

Scope respected: no Product code, no estimator implementation, no P0/target-host
access, no capital-state change, no F11 reopening, no cohort/coordinate change,
no menu of speculative missions. One bounded delivery. Returning control to Blue.
