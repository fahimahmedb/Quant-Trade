# D05-A / D09 BETA AUTHORITY / WINDOW MULTIPLICITY / DEPENDENCE-CAPACITY AMENDMENT — 2026-09-17

**Status:** CLOSED / FROZEN STRUCTURAL AMENDMENT — NUMERICAL BETA / PRECISION / JOINT DEPENDENCE RULE STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D05A_D09_LIQUIDITY_BREACH_FREQUENCY_Q_SELECTION_RETIREMENT_AMENDMENT_2026-09-17.md`, `D05A_D09_PMAX_CORPORATE_DEPENDENCE_AND_SPLIT_CAPACITY_AMENDMENT_2026-09-17.md`, `D05A_D09_LIQUIDITY_LAMBDA_DISCHARGE_AND_REFERENCE_PARTICIPATION_AMENDMENT_2026-09-17.md`

This amendment closes three structural questions revealed by the breach-frequency reformulation: the authority type of `BETA_LIQ_MAX`, the multiplicity cost of the candidate-window family, and the limit of `N_GROUP_EFF` as a capacity object when common calendar/market shocks can induce dependence across otherwise distinct corporate-dependence groups.

No Form-4 target values, D05 ceilings, outcomes, candidate-window breach results, external corpus counts or numerical governance tolerances are consumed by this amendment.

## 1. `BETA_LIQ_MAX` is an explicit execution-risk tolerance

`BETA_LIQ_MAX` is the maximum admissible weighted frequency/mass with which the frozen ADV forecast may be optimistic enough to breach the frozen reference participation ceiling.

It is a governance decision about tolerated execution-risk frequency. It is not estimated from the calibration corpus and is not derived from available sample size.

Its authority question is:

> What maximum ex-ante frequency of reference-capacity breaches is the lineage willing to tolerate under the frozen measurement convention?

It must satisfy:

`0 < BETA_LIQ_MAX < 1`.

Its numerical value/rationale must be frozen before candidate-window breach results and before eligible calibration capacity is inspected for feasibility.

It may not depend on:

- available calibration sample size or effective capacity;
- which lookback window passes;
- Form-4 support, D05 ceilings or outcomes;
- BEEE, MEUE, `delta` or target strategy profitability;
- a desire to avoid `LIQUIDITY_BREACH_CALIBRATION_UNDERPOWERED`;
- a desire to preserve a preferred candidate window.

Because changing `BETA_LIQ_MAX` can change `W*` and therefore deployment support, the final `LIQUIDITY_ELIGIBILITY_RULE_HASH` must bind its numerical value, authority/rationale identifier, version and update rule.

**Invariants**

- `BETA_LIQ_MAX_IS_EXECUTION_RISK_FREQUENCY_TOLERANCE`
- `BETA_LIQ_MAX_IS_DECLARED_NOT_CORPUS_SELECTED`
- `BETA_LIQ_MAX_IS_CLAIM_DEFINING_THROUGH_W_STAR`
- `UNDERPOWERED_STATE_CANNOT_RELAX_BETA_LIQ_MAX`

## 2. Breach magnitude and breach frequency remain orthogonal

The parent distinction remains controlling:

`EPSILON_ADV_BAR = log(P_MAX_REF / P_TARGET_REF)`

sets the **magnitude** of forecast optimism that reaches the hard reference participation ceiling, while:

`BETA_LIQ_MAX`

sets the maximum tolerated **frequency** of exceeding that magnitude.

Neither object determines the other mathematically.

Thus the reference-capacity rule has two independent governed coordinates:

`(breach magnitude, breach frequency) = (EPSILON_ADV_BAR, BETA_LIQ_MAX)`.

No later calibration result may trade one against the other to rescue feasibility.

## 3. Candidate windows carry a real multiplicity cost

Let the frozen candidate-window set be:

`W_SET = {W_1, ..., W_K}`

with `K = |W_SET|`.

The exact lambda-discharge protocol evaluates each window at two structural endpoints:

`x in {0,1}`.

Therefore the authority-bearing simultaneous breach family contains:

`M = 2K`

statistics before any additional family expansion.

Any confidence/concentration construction used to authorize breach-frequency estimates must control the full finite family simultaneously.

Under a simple union construction, the per-statistic failure budget is at most:

`ALPHA_BETA / (2K)`

for a one-sided familywise guarantee, or the exact equivalent implied by the frozen concentration construction.

The precise concentration constant remains open, but the multiplicity cardinality `2K` is structural and cannot disappear merely because the same sample is reused across windows.

**Invariants**

- `BREACH_UNIFORMITY_FAMILY_SIZE_IS_TWO_TIMES_WINDOW_COUNT`
- `EVERY_ADDITIONAL_WINDOW_CONSUMES_CALIBRATION_AUTHORITY`
- `WINDOW_REUSE_ON_SAME_SAMPLE_DOES_NOT_REMOVE_MULTIPLICITY`

## 4. Candidate windows must represent distinct measurement scales

Because each additional candidate window increases multiplicity burden and therefore required calibration authority, `W_SET` must remain deliberately small.

A candidate window is admissible only when it represents a predeclared, substantively distinct liquidity-measurement time scale or regime-resolution purpose.

Forbidden reasons for adding candidate windows include:

- fine parameter sweeping for a numerically convenient `W*`;
- filling every integer day between two already represented scales;
- inspecting breach results and adding an intermediate window;
- increasing the chance that at least one window passes;
- retaining more Form-4 support.

The set, ordering and economic/measurement rationale for each candidate window must be frozen before external breach results.

If two proposed windows have no predeclared materially distinct measurement rationale beyond numerical proximity, the burden is to remove one rather than spend multiplicity authority by default.

**Invariants**

- `CANDIDATE_WINDOWS_REPRESENT_DISTINCT_MEASUREMENT_SCALES`
- `NO_FINE_GRID_WINDOW_SWEEP`
- `WINDOW_SET_PRECEDES_BREACH_RESULTS`
- `WINDOW_MULTIPLICITY_COST_IS_A_DESIGN_CONSTRAINT`

## 5. One-sided precision is the economically relevant direction

The authority risk in breach calibration is underestimating the true breach frequency and thereby declaring a window acceptable when its true breach mass exceeds `BETA_LIQ_MAX`.

Therefore, absent a separately justified downstream need for two-sided precision, the preferred authority construction is a simultaneous **upper confidence bound** on each true breach mass:

`B_W(x) <= UCB_W(x)`

with familywise failure probability at most `ALPHA_BETA` over all `W in W_SET` and `x in {0,1}`.

A window passes an endpoint only if the authority-bearing upper bound satisfies:

`UCB_W(x) <= BETA_LIQ_MAX`.

This is stricter and more operationally meaningful than comparing an unprotected point estimate directly with the risk tolerance.

The numerical construction of `UCB_W(x)` remains open until the joint dependence model is frozen.

**Invariants**

- `BREACH_AUTHORITY_USES_ONE_SIDED_UPPER_PROTECTION`
- `POINT_ESTIMATE_ALONE_CANNOT_CERTIFY_BREACH_TOLERANCE`
- `FAMILYWISE_UPPER_BOUND_PRECEDES_WINDOW_PASS_AUTHORITY`

## 6. `N_GROUP_EFF` correctly captures corporate-weight concentration, but not all dependence

Under equal-security target weighting, let corporate-dependence group `g` carry normalized target mass `omega_g`, with:

`sum_g omega_g = 1`.

The previously defined concentration object remains valid:

`N_GROUP_EFF_CORPORATE = 1 / sum_g omega_g^2`.

This correctly penalizes a calibration corpus in which a small number of large merger/spin-off dependence groups carry disproportionate security mass.

It is therefore a required reported capacity diagnostic, and ordinary security count is not an authority substitute.

However, `CALIBRATION_DEPENDENCE_GROUP_ID` addresses corporate lineage dependence only. Distinct corporate groups can still share dependence through common market/calendar liquidity shocks, volatility regimes, exchange-wide events or other synchronized conditions.

Therefore `N_GROUP_EFF_CORPORATE` is **not yet the final authority-bearing effective sample size** unless the final dependence construction independently justifies treating group-level breach contributions as independent for the required concentration result.

**Invariants**

- `SECURITY_COUNT_IS_NOT_EFFECTIVE_BREACH_CAPACITY`
- `CORPORATE_GROUP_WEIGHT_CONCENTRATION_REDUCES_EFFECTIVE_CAPACITY`
- `N_GROUP_EFF_CORPORATE_DOES_NOT_BY_ITSELF_PROVE_GROUP_INDEPENDENCE`
- `COMMON_MARKET_DATE_DEPENDENCE_MUST_NOT_BE_IGNORED`

## 7. Conditional special case: weighted one-sided Hoeffding

A simple closed-form capacity relation exists only under a stronger condition.

Suppose the final frozen calibration construction proves that the corporate-dependence-group contributions relevant to one breach statistic can be represented as independent bounded random variables:

`Z_g(W,x) in [0,1]`

with frozen normalized weights `omega_g` and:

`B_hat_W(x) = sum_g omega_g Z_g(W,x)`.

Then a one-sided weighted Hoeffding bound gives the special-case design relation:

`P(B_W(x) - B_hat_W(x) >= tau) <= exp(-2 * tau^2 / sum_g omega_g^2)`

or equivalently:

`<= exp(-2 * N_GROUP_EFF_CORPORATE * tau^2)`.

For the simultaneous family `M = 2K`, a union-bound sufficient condition would be:

`N_GROUP_EFF_CORPORATE >= log((2K)/ALPHA_BETA) / (2 * TAU_BETA^2)`.

This formula is **not current authority** unless its independence/bounded-contribution premises are satisfied by the final calibration-dependence contract.

It is recorded only as the exact special case explaining why window multiplicity enters logarithmically and why unequal corporate-group weights reduce capacity.

**Invariants**

- `WEIGHTED_HOEFFDING_FORMULA_IS_CONDITIONAL_NOT_DEFAULT_AUTHORITY`
- `HOEFFDING_REQUIRES_FROZEN_INDEPENDENCE_PREMISE`
- `TWO_K_MULTIPLICITY_ENTERS_THE_SPECIAL_CASE_LOGARITHMICALLY`

## 8. Final capacity rule must account for joint dependence

Before deriving the authority-bearing `N_EFF_REQUIRED` or equivalent feasibility object, freeze a joint calibration-dependence contract that addresses at minimum:

- corporate reorganization dependence across security lineages;
- common calendar/session or market-regime dependence across different corporate groups;
- serial dependence in breach outcomes over nearby calibration dates;
- the equal-security target weighting convention;
- the exact one-sided simultaneous confidence/concentration construction;
- failure behavior when the required dependence assumptions cannot be supported.

Permitted future structural approaches may include a predeclared whole-market calendar-block resampling scheme, another dependence-robust bounded-process construction, or a stronger independently justified model that makes the required concentration theorem valid.

No approach may be chosen after observing which one makes `W*` pass or produces the smallest required capacity.

Until this is closed:

`BREACH_JOINT_DEPENDENCE_CONTRACT = OPEN`

and:

`N_GROUP_EFF_CORPORATE` remains a required diagnostic, not the final sufficiency certificate.

## 9. Corpus-size consequence

The external corpus should be broad enough that corporate-linkage concentration and the final joint dependence correction do not force standards to be weakened.

If the frozen corpus rule later yields insufficient authority-bearing capacity, the correct response is:

`LIQUIDITY_BREACH_CALIBRATION_UNDERPOWERED`,

not:

- relaxing `BETA_LIQ_MAX`;
- increasing `TAU_BETA`;
- increasing `ALPHA_BETA`;
- deleting candidate windows after seeing their results;
- breaking corporate dependence groups apart;
- shortening market-dependence blocks after seeing feasibility;
- importing Form-4 target data into the calibration design.

Prospectively broadening an independently defined external corpus under a pre-frozen source/domain expansion rule is a different action and must not be selected based on target support or candidate-window results.

## 10. Revised immediate critical path

Before external breach calibration:

`freeze numerical P_MAX_REF + P_TARGET_REF under their already frozen authority types`

`-> derive EPSILON_ADV_BAR`

`-> freeze numerical BETA_LIQ_MAX as explicit breach-frequency governance tolerance`

`-> freeze a small candidate-window set justified by distinct measurement scales`

`-> freeze TAU_BETA / ALPHA_BETA and one-sided familywise authority rule`

`-> freeze source / calibration-domain / date-sampling / security-lineage / corporate-group semantics`

`-> freeze joint market-calendar / serial / corporate dependence construction`

`-> derive the authority-bearing effective-capacity requirement with multiplicity M = 2K`

`-> only then compute available capacity under the frozen external corpus`

`-> if insufficient: LIQUIDITY_BREACH_CALIBRATION_UNDERPOWERED`

`-> if sufficient: compute simultaneous one-sided breach upper bounds and apply the shortest-passing endpoint rule`.

No later capacity or window result may feed backward into the risk tolerances, candidate set, dependence model or precision budget.

## 11. Current state

Closed/frozen:

- `BETA_LIQ_MAX` authority type = explicit execution-risk breach-frequency tolerance;
- `BETA_LIQ_MAX` is claim-defining through lookback selection and cannot be selected by available calibration capacity;
- candidate-window multiplicity family size = `2K` for `K` windows and two lambda endpoints;
- candidate windows must represent distinct predeclared measurement scales, not a fine search grid;
- breach authority is one-sided: protect against underestimating true breach frequency;
- point estimates alone do not certify a window;
- `N_GROUP_EFF_CORPORATE = 1/sum omega_g^2` remains required and correctly reflects corporate-group weight concentration;
- corporate-group effective mass alone does not resolve common market/calendar/serial dependence;
- weighted Hoeffding plus `log(2K/ALPHA_BETA)/(2 TAU_BETA^2)` is a conditional special case, not default authority.

Still open before calibration:

- numerical `BETA_LIQ_MAX` and its exact governance rationale/value;
- numerical `P_MAX_REF` / `P_TARGET_REF`;
- exact candidate windows and scale rationale;
- numerical `TAU_BETA` / `ALPHA_BETA`;
- exact weighted breach estimator implementation;
- final joint dependence model / resampling / concentration rule;
- final authority-bearing capacity formula;
- source/provider/daily-notional route;
- calibration-domain/date-sampling/true-zero/minimum-history rules.

No external breach calibration, D05 ceiling visibility or Form-4 outcome access is authorized by this amendment.
