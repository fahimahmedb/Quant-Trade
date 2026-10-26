# D05-A / D09 WINDOW-SPECIFIC CALENDAR / SERIAL DEPENDENCE CONTRACT — 2026-09-17

**Status:** CLOSED / FROZEN STRUCTURAL CONTRACT — EXACT JOINT RESAMPLING / BLOCK-HORIZON RULE STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D05A_D09_BETA_AUTHORITY_WINDOW_MULTIPLICITY_AND_DEPENDENCE_CAPACITY_AMENDMENT_2026-09-17.md`, `D05A_D09_LIQUIDITY_BREACH_FREQUENCY_Q_SELECTION_RETIREMENT_AMENDMENT_2026-09-17.md`, `D05A_D09_PMAX_CORPORATE_DEPENDENCE_AND_SPLIT_CAPACITY_AMENDMENT_2026-09-17.md`

This contract closes the architecture of the joint dependence problem for breach-frequency calibration. It recognizes that common market/session shocks can dominate cross-sectional dependence and that rolling ADV construction creates a **window-specific serial dependence horizon**. It does not yet choose a numerical calendar block length, bootstrap implementation, HAC/mixing model, `BETA_LIQ_MAX`, `TAU_BETA`, `ALPHA_BETA`, candidate windows, provider values, D05 counts or Form-4 outcomes.

No candidate-window breach results or available-capacity counts are consumed by this contract.

## 1. Dependence is window-specific, not a common scalar correction

For candidate lookback `W`, calibration anchor session `t`, security lineage `i`, and normalized lambda endpoint `x`, let:

`I_i,t(W,x) = 1{ L_bar_x(E_i,t(W)) > EPSILON_ADV_BAR }`.

The uncertainty of the weighted breach estimator is not governed by one universal effective-sample multiplier shared across candidate windows.

The rolling predictor `ADV_NOTIONAL(W,t)` changes the dependence structure itself. Longer windows mechanically reuse more of the same historical market observations across neighboring calibration anchors.

Therefore the authority-bearing uncertainty construction must be indexed by `W`:

`UCB_W(x) = JOINT_DEPENDENCE_UCB(W, x, frozen calibration panel, frozen dependence contract)`.

A shorter-window uncertainty estimate may not be reused for a longer window merely because the sample contains the same anchor dates.

**Invariants**

- `BREACH_DEPENDENCE_IS_WINDOW_SPECIFIC`
- `LONG_WINDOW_CANNOT_INHERIT_SHORT_WINDOW_PRECISION`
- `ONE_COMMON_NEFF_REQUIRES_SEPARATE_PROOF`

## 2. Mechanical influence span of one breach observation

At anchor `t`, the `W`-session ADV predictor consumes the `W` completed regular sessions ending at `t`, and its prediction target is the immediately following regular session `t+1`.

Define the raw-data influence interval:

`INFLUENCE_SPAN(W,t) = [t-W+1, ..., t, t+1]`

with structural length:

`H_OVERLAP(W) = W + 1 regular sessions`.

Neighboring breach observations can therefore share raw inputs even before any economic or market-regime serial dependence is considered.

Any block/resampling/bandwidth construction claiming to absorb the deterministic rolling-window overlap must not use a dependence horizon shorter than the structural overlap requirement without an independent theorem proving validity.

`H_OVERLAP(W)` is a **minimum structural horizon**, not a claim that all dependence vanishes after `W+1` sessions.

**Invariants**

- `ROLLING_ADV_CREATES_MECHANICAL_SERIAL_DEPENDENCE`
- `STRUCTURAL_OVERLAP_HORIZON_GROWS_WITH_W`
- `W_PLUS_ONE_IS_A_MINIMUM_NOT_A_COMPLETE_DEPENDENCE_MODEL`

## 3. Common-session shocks make the calendar axis an authority-bearing dependence dimension

Liquidity shocks can affect many otherwise unrelated securities on the same market session. Stress, volatility regimes, exchange-wide events and market-wide flow conditions can therefore synchronize breach events across distinct corporate-dependence groups.

Consequently, row-level security-date independence is forbidden.

Any resampling construction used for authority must preserve the **whole eligible cross-section for a calendar session together** when representing common-session dependence.

If calendar blocks are used, they are synchronized across the full eligible panel: one resampled calendar block carries all eligible security/group observations belonging to those sessions under the frozen missingness/weighting rules.

Resampling each security independently across dates is not an authority-bearing approximation for the common-shock channel.

**Invariants**

- `COMMON_SESSION_LIQUIDITY_SHOCK_IS_A_DEPENDENCE_AXIS`
- `ROW_LEVEL_SECURITY_DATE_INDEPENDENCE_IS_FORBIDDEN`
- `CALENDAR_BLOCKS_PRESERVE_FULL_CROSS_SECTION_SYNCHRONY`

## 4. Distinct-date count is a capacity dimension, not pair count

A panel with many securities observed on the same finite set of sessions does not acquire independent common-shock information in proportion to the number of security-date pairs.

Therefore neither:

`N_SECURITY_DATE_PAIRS`

nor raw security count may be used as the authority-bearing breach-calibration sample size.

The number and weighting of distinct eligible calendar sessions, after the final serial-dependence construction, are required capacity diagnostics.

This contract does **not** assert a universal identity `N_eff = number_of_dates`; cross-sectional security variation and the corporate-group axis remain relevant. It asserts only that common-session dependence can make the calendar dimension binding and that pair count cannot bypass it.

**Invariants**

- `SECURITY_DATE_PAIR_COUNT_IS_NOT_BREACH_CAPACITY`
- `DISTINCT_CALENDAR_INFORMATION_CANNOT_BE_MULTIPLIED_BY_CROSS_SECTIONAL_ROWS`

## 5. Corporate dependence remains a second axis, not a substitute for calendar dependence

The frozen `CALIBRATION_DEPENDENCE_GROUP_ID` remains the grouping object for mergers, successors, spin-offs/separations and other authorized corporate reorganization linkages.

Calendar synchronization does not retire this corporate dependence dimension.

The final joint dependence construction must address both:

1. **calendar/serial dependence** — common shocks and overlapping rolling inputs through time;
2. **corporate dependence** — linked security lineages that must not be treated as unrelated cross-sectional units.

A calendar-only method is not automatically sufficient for cross-security generalization, and a corporate-only method is not sufficient for common-session/serial dependence.

The authority-bearing method class is therefore multi-axis:

`JOINT_DEPENDENCE = CALENDAR_SERIAL_AXIS x CORPORATE_DEPENDENCE_AXIS`.

The exact theorem/bootstrap/resampling implementation remains open, but it must preserve both axes or independently prove that one axis is conditioned/fixed in a way that makes the other sufficient.

**Invariants**

- `JOINT_DEPENDENCE_HAS_CALENDAR_AND_CORPORATE_AXES`
- `CORPORATE_GROUPING_DOES_NOT_REPLACE_MARKET_DATE_DEPENDENCE`
- `CALENDAR_BLOCKING_DOES_NOT_SILENTLY_ERASE_CORPORATE_DEPENDENCE`

## 6. Window-specific serial horizon rule must be frozen before results

The final dependence procedure must define a deterministic serial-memory/block/bandwidth rule:

`H_SERIAL(W)`

for every `W in W_SET` before breach results or available-capacity feasibility are inspected.

Required properties:

- `H_SERIAL(W)` must respect the structural rolling-input overlap represented by `H_OVERLAP(W)`;
- the rule must be nondecreasing in `W` unless a separate proof establishes why a longer rolling predictor legitimately requires no greater dependence horizon;
- any additional persistence attributed to common market/regime shocks must be incorporated under a frozen rule;
- no block length/bandwidth may be shortened because a longer choice makes calibration underpowered or makes a preferred window fail;
- the rule may not be selected by comparing which dependence specification yields the most convenient `W*`.

This contract deliberately does **not** freeze `H_SERIAL(W) = W+1`, `max(W+1,H_market)`, or any other unproved closed form. Market persistence and rolling-window overlap can interact, so composition of the two horizons requires its own authority.

If no defensible pre-result rule can be frozen:

`BREACH_SERIAL_DEPENDENCE_RULE_UNRESOLVED`.

**Invariants**

- `SERIAL_DEPENDENCE_HORIZON_IS_PRE_RESULT_AND_W_SPECIFIC`
- `LONGER_W_CANNOT_RECEIVE_SHORTER_MEMORY_BY_CONVENIENCE`
- `DEPENDENCE_HORIZON_CANNOT_BE_TUNED_TO_PASS_CAPACITY`

## 7. Preferred resampling architecture: synchronized calendar blocks with corporate grouping

The current structural preference, if resampling is used, is a dependence-preserving scheme in which:

- contiguous regular-session calendar blocks are resampled synchronously across the full eligible cross-section;
- block construction is `W`-specific through the frozen `H_SERIAL(W)` rule;
- corporate-linked security lineages remain grouped under `CALIBRATION_DEPENDENCE_GROUP_ID` in the cross-sectional uncertainty construction;
- the exact resampling/bootstrap theorem and confidence construction are frozen before results.

This preference does not yet authorize a particular moving-block, stationary-block, circular-block, wild-cluster or multiway-bootstrap algorithm. The exact implementation must demonstrate that its assumptions match the two-axis structure above.

If another dependence-robust bounded-process construction is used instead of resampling, it must provide equivalent protection against common-session shocks, rolling overlap and corporate linkage.

## 8. Capacity and precision are vectors over W before they become a global verdict

Let the final joint-dependence construction induce, for each window, an authority-bearing precision/capacity object:

`CAPACITY_AUTH(W)`

or an equivalent `N_EFF_AUTH(W)` when such a scalar is mathematically justified.

The protocol may not assume:

`CAPACITY_AUTH(W1) = CAPACITY_AUTH(W2)`.

The design precision target `TAU_BETA` and familywise error target `ALPHA_BETA` remain common governance inputs unless separately amended, but the data capacity required to satisfy them may differ by `W`.

Uniform authority over the frozen candidate family requires:

`CAPACITY_SUFFICIENT_FOR_ALL_WINDOWS = TRUE`.

If even one predeclared candidate lacks the precision required by the frozen joint-dependence construction, the selector-level state is:

`LIQUIDITY_BREACH_CALIBRATION_UNDERPOWERED`.

The underpowered window may not simply be removed after capacity is seen, because that would change the candidate family after its multiplicity/dependence cost became known.

**Invariants**

- `BREACH_CAPACITY_IS_W_SPECIFIC`
- `UNIFORM_SELECTOR_AUTHORITY_REQUIRES_ALL_WINDOWS_TO_MEET_PRECISION_DESIGN`
- `UNDERPOWERED_WINDOW_CANNOT_BE_DROPPED_POST_HOC`

## 9. Longer windows must pay their actual information cost

A longer window can produce a smoother point predictor while simultaneously reducing the amount of independent information available to validate its breach frequency because neighboring predictions reuse more history.

The calibration protocol must preserve both facts.

It is forbidden to let the smoother appearance of a long-window breach series substitute for a dependence-aware uncertainty calculation.

Thus a long window does not receive authority merely because its raw breach-rate time series looks less variable.

**Invariants**

- `SMOOTHER_LONG_WINDOW_SERIES_DOES_NOT_IMPLY_MORE_INFORMATION`
- `WINDOW_SMOOTHING_AND_WINDOW_INFORMATION_ARE_DISTINCT`

## 10. Simultaneous one-sided family remains 2K under one frozen dependence rule per window

The parent multiplicity family remains:

`M = 2 * |W_SET|`

for `W in W_SET` and `x in {0,1}`, provided each `(W,x)` has exactly one pre-frozen dependence/UCB construction.

If the protocol instead evaluates multiple block horizons, bootstrap variants or dependence models and then selects among them, those additional choices must either:

- enter the simultaneous error-control family; or
- be combined by a predeclared conservative envelope/worst-case rule.

They may not be tried until one makes a window pass.

**Invariants**

- `DEPENDENCE_MODEL_SEARCH_CANNOT_ESCAPE_MULTIPLICITY`
- `ONE_PRE_FROZEN_DEPENDENCE_RULE_PER_WINDOW_PRESERVES_2K_FAMILY`

## 11. Pass authority remains UCB-based and window-specific

For each `W` and endpoint `x`, the final calibrated statistic must provide a simultaneous one-sided upper bound:

`UCB_W(x)`.

An endpoint passes only if:

`UCB_W(x) <= BETA_LIQ_MAX`.

The UCB must use the `W`-specific dependence construction. No pooled UCB with a common short-window uncertainty estimate may certify the family.

The shortest-passing endpoint rule and exact lambda materiality discharge remain intact once uniform capacity authority has been established.

## 12. Revised dependency state

Closed/frozen by this contract:

- common-session shocks are an authority-bearing dependence dimension;
- rolling ADV creates deterministic serial dependence whose structural influence span grows with `W`;
- `W+1` sessions is a minimum overlap span, not a complete dependence model;
- joint dependence must represent both calendar/serial and corporate axes;
- dependence/UCB/capacity are window-specific;
- longer windows may not inherit short-window precision;
- the full candidate family must satisfy the precision design before selector authority;
- synchronized whole-cross-section calendar blocks are the preferred resampling architecture if resampling is used;
- dependence-model search cannot be used as a rescue mechanism.

Still open before numerical breach calibration:

- exact `H_SERIAL(W)` construction, including market-regime persistence;
- exact two-axis bootstrap/concentration theorem;
- exact one-sided simultaneous UCB implementation;
- numerical `P_MAX_REF`, `P_TARGET_REF`, `BETA_LIQ_MAX`, `TAU_BETA`, `ALPHA_BETA`;
- exact small candidate-window set and rationale for each measurement scale;
- exact source/provider / daily-notional route / calibration-domain and date-sampling rules;
- final available capacity under the frozen external corpus.

Current state:

`BREACH_JOINT_DEPENDENCE_CONTRACT = STRUCTURALLY_CLOSED / NUMERICAL_METHOD_NOT_YET_CONSUMABLE`.

No external breach calibration, D05 ceiling visibility or Form-4 outcome access is authorized by this contract.
