# D05-A / D09 q-DOMAIN / VALUE-STABILITY / UNDERPOWERED PROTOCOL AMENDMENT — 2026-09-17

**Status:** CLOSED / FROZEN STRUCTURAL AMENDMENT — NUMERICAL q BOUNDS / STABILITY THRESHOLD / N_Q_REQUIRED STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D05A_D09_PMAX_CORPORATE_DEPENDENCE_AND_SPLIT_CAPACITY_AMENDMENT_2026-09-17.md`, `D05A_D09_LIQUIDITY_LAMBDA_DISCHARGE_AND_REFERENCE_PARTICIPATION_AMENDMENT_2026-09-17.md`, `D05A_D09_LIQUIDITY_PREDICTION_LOSS_AND_AGGREGATION_CONTRACT_2026-09-17.md`

This amendment closes the internal ordering and structural form of q selection before any numerical q/window calibration. It prevents six-object parallel closure from using available corpus capacity or candidate-window behavior to relax q authority after the fact.

No Form-4 target values, D05 ceilings, return outcomes, numerical q values, candidate-window calibration results or external market-data values are consumed by this amendment.

## 1. Expanded-pass ordering is sequential, not simultaneous

The current q/split block must respect the dependency chain:

`q admissible-domain rule`

`-> q estimator + value-stability statistic`

`-> stability threshold / resampling / minimum-cluster rule`

`-> N_Q_REQUIRED design functional`

`-> compare required capacity with eligible external calibration capacity`

`-> only if sufficient, instantiate Q_SELECTION_SPLIT`

`-> select/freeze q`

`-> only then use WINDOW_SELECTION_SPLIT for lambda endpoint discharge and W*`.

No downstream capacity observation may be used to revise an upstream q bound, stability threshold, resampling rule or design requirement.

**Invariants**

- `Q_PROTOCOL_DEPENDENCIES_ARE_ORDERED_NOT_PARALLEL`
- `AVAILABLE_CORPUS_CAPACITY_CANNOT_RELAX_Q_AUTHORITY`
- `N_Q_REQUIRED_PRECEDES_CAPACITY_COMPARISON`

## 2. q is governed by an admissible interval, not a habitual list

The current lineage does not authorize a convenience candidate list such as familiar percentile values merely because they are conventional.

Define instead an admissible interval:

`Q_ADMISSIBLE = [Q_TAIL_MIN, Q_ESTIMABILITY_MAX]`

with:

`0.5 < Q_TAIL_MIN <= Q_ESTIMABILITY_MAX < 1`.

The two bounds have different roles.

### 2.1 Lower bound — tail-protection requirement

`Q_TAIL_MIN` is the lowest quantile level consistent with the predeclared requirement that the adverse prediction-loss tail materially enter the authority-bearing statistic.

Its value/rule must be justified through a separately frozen tail-protection / maximum-unprotected-mass governance requirement, not by:

- familiar statistical convention;
- which q yields a convenient W*;
- available q-split size;
- Form-4 support or outcomes.

The exact numerical mapping from the tail-protection rule to `Q_TAIL_MIN` remains open.

### 2.2 Upper bound — estimability design requirement

`Q_ESTIMABILITY_MAX` is the highest quantile level the predeclared q-estimation design is intended to support with the frozen value-stability guarantee.

It must be derived from the estimator / clustered-resampling / stability-design requirements, including the minimum independent corporate-dependence-group tail support required by that design.

It may not be moved downward after inspecting q-estimation results merely to make the procedure pass.

If the external corpus cannot supply the capacity required to support the already-frozen admissible q domain, the correct state is underpowered; the domain is not shrunk to fit the corpus.

**Invariants**

- `Q_DOMAIN_IS_DERIVED_NOT_HABITUAL_LIST`
- `Q_LOWER_BOUND_COMES_FROM_TAIL_PROTECTION_REQUIREMENT`
- `Q_UPPER_BOUND_COMES_FROM_ESTIMABILITY_DESIGN`
- `Q_DOMAIN_DOES_NOT_SHRINK_TO_AVAILABLE_CORPUS_AFTER_FREEZE`

## 3. q selection rule inside the admissible interval

Once the interval and stability protocol are frozen, q selection uses the existing principle:

> choose the highest q in the frozen admissible domain whose estimator satisfies the frozen value-stability criterion on the dedicated Q_SELECTION_SPLIT.

The procedure must define deterministic treatment of a continuous interval or a mechanically generated evaluation lattice/resolution before results. Any lattice is an implementation of the interval rule, not a discretionary candidate list chosen after seeing results.

If no q in the admissible interval satisfies the frozen criterion despite adequate design capacity:

`Q_SELECTION_UNRESOLVED`.

No lower-than-`Q_TAIL_MIN` fallback is authorized.

**Invariant:** `Q_SELECTION_CHOSES_HIGHEST_STABLE_Q_WITHIN_PREAUTHORIZED_DOMAIN`.

## 4. Stability is about quantile value, not window ordering

The q-selection split exists to establish that the q-level loss quantile can be estimated with sufficient stability.

It does **not** select or rank lookback windows.

Therefore the authority-bearing q-stability statistic must be defined on the estimated **quantile value** and its resampling variability/uncertainty, not on:

- rank correlation between candidate windows;
- identity of the best/shortest-passing window;
- frequency with which one W beats another;
- stability of the final W* decision.

Those ranking/decision objects belong to the later WINDOW_SELECTION_SPLIT.

A value-based criterion may be more conservative than a rank-based criterion. That conservatism is accepted as the cost of preserving the split firewall.

**Invariants**

- `Q_STABILITY_TARGET_IS_QUANTILE_VALUE_NOT_WINDOW_RANKING`
- `Q_SELECTION_SPLIT_DOES_NOT_SELECT_W_STAR`
- `NO_RANK_STABILITY_LEAKAGE_FROM_WINDOW_DECISION`

## 5. q-stability must cover every downstream quantile value that will be consumed

The quantile value depends on candidate window W and on the normalized lambda endpoint loss.

The later exact lambda discharge consumes only the structural endpoints:

- `x = 0`: `L_bar_0(E) = max(E,0)`;
- `x = 1`: `L_bar_1(E) = |E|`.

Therefore q authority requires value-stability on the Q_SELECTION_SPLIT uniformly over the finite predeclared family:

`{ Q_q^weighted(L_bar_x(E(W))) : W in CANDIDATE_WINDOWS, x in {0,1} }`.

The exact uniform stability functional remains to be frozen, but its authority cannot be based on one favorable W or one favorable lambda endpoint.

Permitted structural forms include a predeclared maximum across the family of a bootstrap/cluster-resampling value-instability statistic, provided its exact definition and threshold are frozen before results.

This use of candidate-window losses inside the q split is not W selection: no ordering or pass/fail W authority is produced there. It only tests whether the quantile level is estimable for every value the later endpoint procedure may consume.

**Invariants**

- `Q_STABILITY_IS_UNIFORM_OVER_PREDECLARED_WINDOWS_AND_LAMBDA_ENDPOINTS`
- `ONE_FAVORABLE_WINDOW_CANNOT_AUTHORIZE_Q`
- `Q_SPLIT_MAY_TEST_VALUE_ESTIMABILITY_WITHOUT_RANKING_WINDOWS`

## 6. Corporate-dependence-group clustering remains controlling

The q-stability resampling outer cluster remains:

`CALIBRATION_DEPENDENCE_GROUP_ID`.

Corporate-linked lineages may not be treated as independent bootstrap/resampling units merely because their observations or security-lineage identifiers differ.

The equal-total-mass-per-security loss aggregation rule remains distinct from this outer dependence cluster.

## 7. N_Q_REQUIRED is derived from the frozen q protocol

Only after freezing:

- `Q_ADMISSIBLE` derivation rules;
- q estimator / weighted-quantile convention;
- corporate-dependence-group resampling design;
- value-stability statistic;
- value-stability threshold;
- any confidence/repetition rule;
- minimum tail/support requirement;
- uniform-over-W-and-endpoints rule;

may the protocol derive:

`N_Q_REQUIRED`

or an equivalent deterministic minimum-capacity functional.

`N_Q_REQUIRED` is the minimum external independent dependence-group capacity required by the design. It is not chosen by looking at how many groups happen to be available.

The exact mathematical/sample-size derivation remains open and must be frozen before the eligible corpus count is used as a pass/fail comparison.

**Invariants**

- `N_Q_REQUIRED_DERIVES_FROM_Q_PROTOCOL_NOT_AVAILABLE_N`
- `Q_SPLIT_SIZE_IS_DESIGN_OUTPUT_NOT_CORPUS_FIT`

## 8. Explicit underpowered state

After `N_Q_REQUIRED` is frozen, compare it with the eligible capacity available under the already-frozen calibration-domain, lineage, corporate-dependence and exclusion rules.

If eligible capacity is below the design requirement:

`Q_SELECTION_UNDERPOWERED`.

This state does not authorize:

- lowering the stability threshold;
- lowering `Q_TAIL_MIN`;
- lowering/redefining `Q_ESTIMABILITY_MAX` merely to fit capacity;
- switching from dependence-group to row/security resampling;
- borrowing groups from the window split after results;
- weakening corporate-action exclusions;
- inspecting Form-4 data to justify a rescue.

A future protocol version may redesign the q authority prospectively, but the current frozen design does not silently adapt to the available corpus.

If capacity is adequate but no admissible q satisfies the frozen value-stability criterion, the state is `Q_SELECTION_UNRESOLVED`, not `Q_SELECTION_UNDERPOWERED`.

**Invariants**

- `Q_SELECTION_UNDERPOWERED_IS_DISTINCT_FROM_Q_SELECTION_UNRESOLVED`
- `UNDERPOWERED_DOES_NOT_RELAX_STABILITY_STANDARD`
- `NO_POST_CAPACITY_Q_PROTOCOL_RESCUE`

## 9. Split-capacity consequence

The prior principle remains:

`Q_SELECTION_SPLIT = minimum ex-ante sufficient capacity`

and:

`WINDOW_SELECTION_SPLIT = residual eligible information subject to its own frozen minimum/coverage rules`.

But “minimum sufficient” is now explicitly:

`N_Q_REQUIRED`

or its deterministic grouped/stratified equivalent under the frozen q protocol.

The split constructor may allocate more than the bare minimum only if a predeclared deterministic stratification/coverage/rounding rule requires it. It may not allocate more or less because observed q stability or W behavior is convenient.

## 10. Interaction with P_MAX_REF / P_TARGET_REF

`P_MAX_REF` remains an execution-risk governance ceiling independent of cost optimization.

`P_TARGET_REF` remains a claim-defining measurement-calibration convention.

Their numerical authority/value rules are separate from q estimability. The q-domain/stability protocol may not use resulting W* or Form-4 support to choose either reference participation object.

If a future chosen stability statistic normalizes value uncertainty by `EPSILON_ADV_BAR`, then numerical `P_MAX_REF` and `P_TARGET_REF` must be frozen before that statistic is instantiated. If the stability statistic is independent of epsilon, their numerical values may remain on their existing separate branch of the dependency graph until before window selection. The exact choice is still open.

## 11. Revised local critical path

Before any q/window calibration result:

`freeze q tail-protection rule -> derive Q_TAIL_MIN rule`

`-> freeze q estimator / group-cluster resampling / value-stability statistic / threshold / minimum-tail-support rule`

`-> derive Q_ESTIMABILITY_MAX rule and Q_ADMISSIBLE`

`-> freeze uniform-over-candidate-W-and-{0,1}-endpoints stability rule`

`-> derive N_Q_REQUIRED`

`-> compare to eligible external dependence-group capacity`

`-> if insufficient: Q_SELECTION_UNDERPOWERED`

`-> if sufficient: instantiate frozen group-disjoint q/window split`

`-> select highest stable q on Q_SELECTION_SPLIT`

`-> freeze q`

`-> only then run lambda endpoint discharge / W* selection on WINDOW_SELECTION_SPLIT`.

No later object may feed backward to relax an earlier one in this chain.

## 12. Current state

Closed/frozen:

- q governance uses a derived admissible interval, not a habitual percentile list;
- lower q bound comes from a tail-protection requirement;
- upper q bound comes from estimability design;
- q stability targets quantile value, not window ranking/decision stability;
- q value stability must be uniform over all predeclared candidate windows and lambda endpoints x=0,1;
- corporate-dependence groups remain the outer resampling clusters;
- N_Q_REQUIRED derives from the frozen q protocol before capacity comparison;
- insufficient eligible capacity produces `Q_SELECTION_UNDERPOWERED` with no standards rescue;
- adequate capacity but no stable admissible q produces `Q_SELECTION_UNRESOLVED`.

Still open before calibration:

- exact tail-protection rule and numerical/rule value for `Q_TAIL_MIN`;
- exact q estimator convention;
- exact value-stability statistic and threshold;
- exact clustered-resampling/confidence/repetition rule;
- exact minimum tail/group support rule;
- exact derivation of `Q_ESTIMABILITY_MAX`;
- exact derivation of `N_Q_REQUIRED`;
- numerical `P_MAX_REF` / `P_TARGET_REF` authority/value rules;
- exact dependence-group resolver/source implementation;
- deterministic split assignment/stratification/minimum WINDOW capacity;
- candidate windows;
- source/provider/daily-notional route;
- calibration-domain/date-sampling/true-zero/minimum-history rules.

No numerical q/window calibration, D05 ceiling visibility or Form-4 outcome access is authorized by this amendment.
