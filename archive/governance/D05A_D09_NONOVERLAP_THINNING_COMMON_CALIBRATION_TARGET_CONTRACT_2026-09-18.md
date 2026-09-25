# D05-A / D09 NON-OVERLAP THINNING / COMMON CALIBRATION TARGET CONTRACT — 2026-09-18

**Status:** CLOSED / FROZEN STRUCTURAL CONTRACT — EXACT THINNING PHASE / DESIGN WEIGHTS / RESIDUAL BLOCK RULE STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D05A_D09_WINDOW_SPECIFIC_CALENDAR_SERIAL_DEPENDENCE_CONTRACT_2026-09-17.md`, `D05A_D09_BETA_AUTHORITY_WINDOW_MULTIPLICITY_AND_DEPENDENCE_CAPACITY_AMENDMENT_2026-09-17.md`, `D05A_D09_LIQUIDITY_BREACH_FREQUENCY_Q_SELECTION_RETIREMENT_AMENDMENT_2026-09-17.md`

This contract removes deterministic rolling-window overlap from the authority-bearing calibration design where feasible, while preventing window-specific date sampling from changing the calibration estimand or support. It does not choose numerical windows, persistence horizons, block lengths, participation values, breach tolerances, provider values, or Form-4 outcomes.

No candidate-window breach results or available-capacity counts are consumed by this contract.

## 1. Overlap intuition is structural, not a correlation theorem

For an arithmetic rolling mean of iid equal-variance daily inputs, adjacent W-session means have correlation `(W-1)/W`. This illustrates why overlap can create near-unit serial dependence for long W.

The current lineage does **not** use that expression as an authority formula for breach indicators, because actual traded-notional inputs may be serially dependent / heteroskedastic and the breach statistic is nonlinear and includes the next-session target.

The authority-bearing structural fact remains:

`INFLUENCE_SPAN(W,t) = [t-W+1, ..., t, t+1]`.

Two selected anchors for the same W have no shared raw predictor/target session when their anchor distance is at least:

`S_OVERLAP(W) = W + 1 regular sessions`.

**Invariants**
- `W_MINUS_ONE_OVER_W_IS_INTUITION_NOT_BREACH_AUTHORITY`
- `W_PLUS_ONE_SPACING_REMOVES_MECHANICAL_RAW_INPUT_OVERLAP`

## 2. Mechanical overlap is preferably removed by design

For each frozen candidate W, the authority-bearing calibration protocol should use a pre-result calendar-only anchor schedule:

`ANCHOR_SET(W)`

such that consecutive selected anchors for W are separated by at least `W+1` regular sessions.

The schedule constructor must be frozen before market-data loss/breach results and may depend only on predeclared calendar/session identifiers, W, protocol version, and any immutable seed/phase rule.

It may not depend on:
- realized ADV or next-session notional;
- breach indicators;
- which W passes;
- Form-4 support or outcomes;
- available capacity after candidate results.

This converts deterministic overlap from an estimated variance correction into an explicit sampling-design cost.

**Invariants**
- `MECHANICAL_OVERLAP_IS_REMOVED_BY_PRE_FROZEN_THINNING_WHERE_AUTHORIZED`
- `THINNING_SCHEDULE_IS_MARKET_VALUE_BLIND`
- `LONGER_WINDOWS_CONSUME_SARSER_AUTHORITY_ANCHORS`

## 3. Window-specific thinning must not create window-specific estimands

A naive W-specific thinning schedule can place different candidate windows on different historical regimes. That would make breach-rate differences partly a consequence of different sampled calendars rather than different forecast quality.

Therefore all W must target one frozen common calibration measure:

`COMMON_LIQUIDITY_CALIBRATION_TARGET_MEASURE`.

Changing W may change the **sampling design** used to estimate that target, but may not redefine:
- the intended calendar horizon/regime domain;
- the intended security-lineage population;
- equal-security total-mass semantics;
- the meaning of breach frequency.

The exact design-weight / inclusion-weight estimator remains open, but it must map every `ANCHOR_SET(W)` back to the same frozen target measure.

If a proposed thinning design cannot support a valid common-target estimator/UCB:

`WINDOW_SPECIFIC_THINNING_AUTHORITY_UNRESOLVED`.

A W-specific sample mean over an unweighted W-specific date subset is not automatically an authority-bearing comparison.

**Invariants**
- `THINNING_CHANGES_SAMPLING_NOT_TARGET_MEASURE`
- `ALL_WINDOWS_SHARE_ONE_CALIBRATION_TIME_TARGET`
- `WINDOW_SPECIFIC_DATE_SUBSET_CANNOT_SILENTLY_REDEFINE_BREACH_PROBABILITY`

## 4. Common pre-thinning support prevents population drift across windows

Before applying any W-specific anchor thinning, freeze a common security-date support that is valid for the complete candidate family.

Let:

`W_MAX = max(W_SET)`.

The comparison support must require enough PIT history and target availability to evaluate every candidate W on the same underlying security-date population, including the history required by W_MAX.

Conceptually:

`COMMON_WINDOW_CALIBRATION_SUPPORT = intersection_W VALID_CALIBRATION_SUPPORT(W)`.

Window selection may not obtain an advantage by admitting securities/dates unavailable to another candidate merely because the candidate uses less history.

This common calibration-support rule is distinct from the final deployment minimum-history rule after W* is selected.

**Invariants**
- `WINDOW_SELECTION_USES_COMMON_PRETHINNING_SUPPORT`
- `SHORT_WINDOW_CANNOT_WIN_BY_CHANGING_CALIBRATION_POPULATION`
- `COMMON_CALIBRATION_SUPPORT_DOES_NOT_SET_FINAL_DEPLOYMENT_HISTORY_POLICY`

## 5. Residual dependence remains after overlap removal

Spacing anchors by W+1 removes shared raw sessions. It does not establish independence.

Residual dependence may remain through:
- persistent security-level traded-notional regimes;
- market-wide liquidity / volatility regimes;
- exchange-wide/session shocks;
- corporate-linked lineages;
- nonlinear threshold persistence in breach indicators.

Therefore thinning does not retire the joint-dependence UCB.

The authority object remains:

`UCB_W(x) = JOINT_DEPENDENCE_UCB(W,x, thinned common-target calibration design)`.

Each W retains its own UCB and precision verdict.

**Invariants**
- `NONOVERLAP_DOES_NOT_IMPLY_INDEPENDENCE`
- `THINNING_DOES_NOT_RETIRE_CALENDAR_OR_CORPORATE_DEPENDENCE`
- `UCB_REMAINS_WINDOW_SPECIFIC_AFTER_THINNING`

## 6. Residual-persistence measurement may be empirical only under a frozen rule

The external calibration corpus may be used to instantiate a residual serial-persistence / block-horizon nuisance parameter because it is non-target data.

But before inspecting its value, freeze/hash:
- the raw liquidity/state series or breach-process object whose persistence is measured;
- transformation and missingness rules;
- dependence statistic;
- cutoff/decay criterion;
- aggregation across securities/market states;
- maximum/minimum horizon rules;
- failure state.

The result of that rule may inform the residual calendar block / bandwidth construction. The rule itself may not be selected after seeing which horizon makes W* pass or makes capacity sufficient.

The current lineage does not claim that W+1 alone captures persistent liquidity regimes.

**Invariants**
- `RESIDUAL_PERSISTENCE_RULE_PRECEDES_ITS_EMPIRICAL_VALUE`
- `PERSISTENCE_ESTIMATION_MAY_USE_EXTERNAL_CALIBRATION_DATA_NOT_FORM4_TARGETS`
- `BLOCK_HORIZON_CANNOT_BE_CHOSEN_TO_RESCUE_W_STAR`

## 7. Common calendar shocks require coupled inference across windows

Although `ANCHOR_SET(W)` may be W-specific, simultaneous inference must preserve the fact that all windows are exposed to the same historical market regimes.

The final UCB implementation must therefore couple the 2K family through a common calendar resampling/randomization structure rather than resampling each W independently.

If block resampling is used, a bootstrap replicate should use a common draw of calendar blocks / market-state units across all:
- W in W_SET;
- x in {0,1};

while applying each W's own anchor schedule and corporate-group structure inside that common draw.

This preserves cross-window covariance and common-shock dependence and allows a simultaneous one-sided familywise construction without pretending the 2K statistics are independent.

**Invariants**
- `SIMULTANEOUS_UCB_USES_COMMON_CALENDAR_DRAWS_ACROSS_WINDOWS`
- `WINDOWS_ARE_NOT_BOOTSTRAPPED_ON_UNRELATED_MARKET_HISTORIES`
- `COMMON_SHOCK_COVARIANCE_IS_PRESERVED_IN_THE_2K_FAMILY`

## 8. Window-specific sample count is visible but is not itself effective sample size

Under W-specific thinning, longer windows generally receive fewer selected anchors over the same frozen calendar horizon.

That is an explicit information cost and must be reported:

`N_ANCHOR_RAW(W)`.

But raw thinned-anchor count is still not the authority-bearing independent sample size because residual calendar/regime and corporate dependence remain.

The protocol must report, at minimum, per W:
- raw eligible common-support dates;
- thinned anchor count;
- distinct calendar blocks/units used by the final dependence method;
- corporate-group concentration diagnostics;
- final precision/UCB verdict.

**Invariants**
- `LONG_WINDOW_INFORMATION_COST_IS_VISIBLE_IN_ANCHOR_COUNT`
- `THINNED_ANCHOR_COUNT_IS_NOT_FINAL_NEFF`

## 9. Edge/phase selection is claim-defining and cannot be shopped

A thinning schedule needs an exact phase/start rule.

The exact rule is still open, but before results it must be deterministic or use an immutable precommitted seed and must be independent of liquidity values.

No phase may be selected because:
- it has lower breach frequency;
- it gives a preferred W;
- it increases available capacity;
- it avoids stress sessions.

If multiple phases are evaluated and one is chosen, phase search must enter multiplicity or be combined by a predeclared conservative envelope.

**Invariants**
- `THINNING_PHASE_PRECEDES_BREACH_RESULTS`
- `NO_PHASE_SHOPPING`
- `PHASE_SEARCH_CANNOT_ESCAPE_MULTIPLICITY`

## 10. Selector-level capacity remains uniform over the frozen family

For each W, after common-support construction, thinning, design weighting and residual joint-dependence inference, the protocol obtains a W-specific precision/UCB authority state.

Uniform selector authority still requires all frozen candidates to satisfy the predeclared precision design.

If any W is underpowered:

`LIQUIDITY_BREACH_CALIBRATION_UNDERPOWERED`.

That W may not be removed after its thinning cost or residual dependence becomes visible.

## 11. Relationship to the prior H_SERIAL contract

This amendment supersedes any reading that deterministic rolling overlap must necessarily be absorbed only by enlarging a resampling block.

Current-lineage preference is:

`mechanical rolling overlap -> remove by frozen anchor thinning`

then:

`residual market / security / corporate persistence -> handle by joint dependence UCB`.

`H_OVERLAP(W)=W+1` remains a structural fact and minimum anchor-spacing rule.

The remaining open dependence horizon is a **residual** persistence/block object, not a device for pretending overlapping anchors are independent.

If a future implementation declines thinning and uses all dates, the prior full H_SERIAL(W) overlap-aware contract becomes controlling again and must justify the corresponding UCB.

## 12. Current state

Closed/frozen:
- W+1 spacing removes deterministic raw-session overlap for one W;
- overlap correlation heuristics are not authority formulas;
- W-specific thinning is preferred for mechanical-overlap removal;
- all windows must target one common calibration measure;
- pre-thinning comparison support is common across W_SET and valid for W_MAX;
- residual dependence and UCB remain after thinning;
- residual persistence may be instantiated empirically only under a pre-frozen rule;
- simultaneous inference couples all windows through common calendar draws;
- thinning phase cannot be shopped;
- underpowered candidates cannot be deleted post hoc.

Still open:
- exact W_SET;
- exact common calibration target/calendar domain;
- exact thinning phase/seed constructor;
- exact design/inclusion weighting that preserves the common target measure;
- exact residual-persistence diagnostic and threshold;
- exact synchronized calendar × corporate UCB implementation;
- numerical P_MAX_REF, P_TARGET_REF, BETA_LIQ_MAX, TAU_BETA, ALPHA_BETA;
- source/provider / daily-notional route and minimum-history implementation.

Current state:

`MECHANICAL_OVERLAP_HANDLING = STRUCTURALLY_CLOSED / W_SPECIFIC_THINNING`

`RESIDUAL_JOINT_DEPENDENCE_METHOD = OPEN / NOT YET CONSUMABLE`.

No external breach calibration, D05 ceiling visibility or Form-4 outcome access is authorized by this contract.
