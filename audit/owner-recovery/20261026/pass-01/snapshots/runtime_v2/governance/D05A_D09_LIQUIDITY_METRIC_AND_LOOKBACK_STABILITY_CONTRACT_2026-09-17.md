# D05-A / D09 LIQUIDITY METRIC AND LOOKBACK-STABILITY CONTRACT — 2026-09-17

**Status:** CLOSED / FROZEN SEMANTICS — NUMERICAL WINDOW / PRECISION THRESHOLD / ADV THRESHOLD / PROVIDER STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D05A_D09_LIQUIDITY_IDENTITY_AND_LOOKBACK_SELECTION_AMENDMENT_2026-09-17.md`, `D09_ROUTE_B_LIQUIDITY_ELIGIBILITY_AND_FINITE_COST_SCENARIO_AMENDMENT_2026-09-17.md`, `D09_ROUTE_B_FRICTION_MARGIN_PARTITION_2026-09-17.md`

This contract closes the economic purpose and metric family of the claim-defining liquidity gate, and the admissible form of the lookback-selection criterion. It does not select numerical values or authorize numerical source inspection.

## 1. The liquidity gate has one purpose: capacity eligibility

The claim-defining liquidity gate answers only:

> Is the security sufficiently liquid, under a frozen ex-ante rule, for the intended policy to admit non-zero deployment support without relying on an economically implausible participation regime?

The gate does **not** attempt to classify expected opening execution quality.

Accordingly, opening spread, opening depth, opening-auction quality, opening slippage and other execution-quality terms remain economic-cost objects governed through:

`K_forward -> BEEE -> M_economic -> MEUE`.

A security may be capacity-eligible yet expensive to execute at the open. In that case it remains in scientific deployment support and carries the higher expected/adverse execution cost under the frozen economic recipe.

**Invariants**

- `LIQUIDITY_GATE_PURPOSE_IS_CAPACITY_ELIGIBILITY`
- `OPEN_EXECUTION_QUALITY_IS_NOT_A_SUPPORT_GATE`
- `CAPACITY_ELIGIBLE_BUT_EXPENSIVE_REMAINS_IN_SUPPORT_WITH_COST`
- `EXECUTION_COST_IS_NOT_HIDDEN_BY_SUPPORT_FILTER`

## 2. Claim-defining liquidity metric family = notional ADV

The gate metric is average daily **notional traded value**, not raw share volume.

Conceptually:

`ADV_NOTIONAL(W) = mean_{d in W} DAILY_TRADED_NOTIONAL_d`.

The intended participation coordinate is therefore dimensionless in capital terms:

`PARTICIPATION(theta) = INTENDED_ORDER_NOTIONAL(theta) / ADV_NOTIONAL(theta)`.

This aligns the capacity denominator with the capital/notional scale on which `C`, deployment size and market impact are economically expressed.

Raw share-volume ADV is not the claim-defining capacity metric in this lineage because an equal share-volume threshold has different capital meaning at different security price levels.

**Invariants**

- `CLAIM_LIQUIDITY_METRIC_IS_NOTIONAL_ADV`
- `SHARE_VOLUME_ADV_IS_NOT_THE_CAPACITY_GATE_COORDINATE`
- `PARTICIPATION_USES_NOTIONAL_OVER_NOTIONAL_ADV`

## 3. PIT price / traded-notional semantics remain explicit

Notional ADV introduces a price/traded-value convention that must remain point-in-time and reproducible.

The final `LIQUIDITY_ELIGIBILITY_RULE_HASH` must therefore bind either:

1. a source-provided daily traded-notional field with documented PIT semantics; or
2. a deterministic daily notional construction from frozen price and share-volume fields.

If constructed, the rule must bind:

- exact daily price field/reference used in the product;
- exact share-volume field;
- adjustment / corporate-action convention;
- source/provider/version;
- PIT listing/security lineage;
- missing-session treatment.

No post-hoc switch between raw/adjusted/vendor-derived daily notional is authorized because one representation changes eligibility more favorably.

**Invariants**

- `NOTIONAL_ADV_PRICE_VOLUME_CONVENTION_IS_FINGERPRINTED`
- `NOTIONAL_ADV_INPUTS_ARE_PIT`
- `NO_POST_HOC_DOLLAR_VOLUME_REPRESENTATION_SWITCH`

## 4. Opening-cost dimensions remain outside the fingerprinted gate

The following do not enter `LIQUIDITY_ELIGIBILITY_RULE_HASH` merely because they affect implementation quality:

- opening spread;
- opening quoted/effective depth;
- opening-auction imbalance;
- opening-specific slippage;
- opening-impact coefficient.

They may enter the separately frozen F2/F3/F4 expected-cost and model-risk parameter registry.

If final economics imply that a capacity-eligible event has unacceptable expected net value after those costs, the economic threshold may reject/withhold deployment under the governed capital process. The scientific support is not retroactively rewritten as liquidity-ineligible.

**Invariant:** `ECONOMIC_COST_FAILURE_DOES_NOT_RETROACTIVELY_REDEFINE_LIQUIDITY_SUPPORT`.

## 5. Lookback-selection target = estimator stability / relative precision

The exact lookback length remains open, but the property used to choose it is now closed.

The lookback is selected to obtain a sufficiently stable estimate of `ADV_NOTIONAL` while retaining responsiveness to the current liquidity regime.

The selection criterion must be expressed in terms of the relative precision / dispersion of the ADV estimator itself, not in terms of Form-4 target retention.

Conceptually define a frozen external calibration functional:

`RELATIVE_ADV_ERROR(W)`

measuring the predeclared relative sampling/stability error of `ADV_NOTIONAL(W)` under an eligible non-target calibration corpus and frozen evaluation procedure.

The lookback rule has the form:

`W* = shortest predeclared candidate window W such that RELATIVE_ADV_ERROR(W) <= epsilon_ADV`

where both the candidate-window set and `epsilon_ADV` must be frozen before candidate numerical results are inspected.

The exact estimator for `RELATIVE_ADV_ERROR`, candidate windows and numerical `epsilon_ADV` are not fixed by this artifact.

**Invariants**

- `LOOKBACK_TARGETS_ADV_ESTIMATOR_STABILITY`
- `LOOKBACK_USES_SHORTEST_WINDOW_MEETING_PREDECLARED_PRECISION`
- `PRECISION_THRESHOLD_PRECEDES_CALIBRATION_RESULTS`
- `CANDIDATE_WINDOWS_PRECEDE_CALIBRATION_RESULTS`

## 6. Calibration corpus must be independent of Form-4 support

The lookback-stability calibration may use only a separately frozen non-target corpus / evidence route whose construction is independent of:

- Form-4 target retention by candidate window;
- D05 counts or ceilings;
- final crossing counts;
- `Q(theta)`;
- BEEE/MEUE;
- return outcomes.

The calibration corpus must be relevant to the intended US-equity deployment/liquidity regime under a separately frozen applicability rule, but it is not selected because it makes the eventual Form-4 support larger.

If no defensible external calibration route can establish the declared stability criterion:

`LIQUIDITY_LOOKBACK_CALIBRATION_UNRESOLVED`.

**Invariants**

- `LOOKBACK_CALIBRATION_IS_TARGET_SUPPORT_BLIND`
- `TARGET_RETENTION_DOES_NOT_SELECT_WINDOW`
- `NO_FALLBACK_WINDOW_CHOSEN_FOR_FORM4_INCLUSION`

## 7. Why shortest passing window is the governing form

Liquidity is time-varying. Longer windows can mechanically reduce estimator dispersion while increasingly mixing historical liquidity regimes.

Therefore the goal is not to minimize estimator variance without limit.

The current-lineage rule uses the **shortest** window that satisfies the predeclared precision requirement, preserving as much recency/regime responsiveness as possible subject to adequate measurement stability.

This is a rule form, not a numerical claim that any particular window is sufficient.

**Invariant:** `STABILITY_REQUIREMENT_DOES_NOT_AUTHORIZE_MAXIMAL_SMOOTHING`.

## 8. Interaction with insufficient history

The exact minimum-valid-observation and recently-listed treatment remain open.

However they must be frozen jointly with the numerical lookback before D05 ceiling visibility because they determine claim support.

No candidate lookback may be preferred because it happens to retain more target securities with short listing histories.

Once frozen:

- deterministic history failure declared ineligible by policy -> `DEPLOYMENT_INELIGIBLE_BY_FROZEN_RULE`;
- unexpectedly unavailable required history/input -> `DEPLOYMENT_ELIGIBILITY_UNRESOLVED` / FM-08.

## 9. Relationship to impact calibration and `C_claim(G)`

`ADV_NOTIONAL` supplies the natural denominator for participation-dependent cost/capacity modeling.

It does not itself establish:

- an impact coefficient;
- acceptable participation limit;
- capital homogeneity;
- `C_claim(G)`.

Those remain separately governed.

A security passing the ADV gate may still encounter differential capacity clipping as `C` rises; therefore:

`ADV_GATE_PASS != C_CLAIM_HOMOGENEITY_PROOF`.

## 10. Current state

Closed/frozen:

- liquidity gate purpose = capacity eligibility only;
- claim-defining metric family = notional ADV;
- participation coordinate = order notional / notional ADV;
- opening spread/depth/slippage remain cost-model dimensions, not support-gate dimensions;
- notional price/volume convention must be PIT and fingerprinted;
- lookback is selected by a predeclared relative-stability criterion on a non-target corpus;
- rule form = shortest predeclared window satisfying the frozen precision threshold;
- target retention / D05 / Q / MEUE / outcomes cannot choose the window.

Still open:

- exact daily traded-notional construction or provider field;
- exact candidate-window set;
- exact external stability functional;
- numerical `epsilon_ADV`;
- final lookback length;
- minimum valid observations;
- insufficient-history policy;
- numerical ADV eligibility threshold / participation rule;
- source/provider/version;
- numerical calibration values.

No numerical liquidity-source search, D05 ceiling visibility or Form-4 outcome access is authorized by this artifact.
