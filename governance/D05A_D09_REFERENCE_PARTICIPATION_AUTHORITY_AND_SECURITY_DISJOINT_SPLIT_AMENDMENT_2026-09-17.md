# D05-A / D09 REFERENCE-PARTICIPATION AUTHORITY / SECURITY-DISJOINT SPLIT AMENDMENT — 2026-09-17

**Status:** CLOSED / FROZEN STRUCTURAL AMENDMENT — NUMERICAL REFERENCE VALUES / q RULE INPUTS STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D05A_D09_LIQUIDITY_LAMBDA_DISCHARGE_AND_REFERENCE_PARTICIPATION_AMENDMENT_2026-09-17.md`, `D05A_D09_LIQUIDITY_PREDICTION_LOSS_AND_AGGREGATION_CONTRACT_2026-09-17.md`, `D09_ECONOMIC_CORE_EC1_ALLOCATION_WEIGHTED_EFFECT.md`

This amendment separates the authority types of `P_MAX_REF` and `P_TARGET_REF`, and strengthens the q-selection/window-selection separation from observation-disjoint to security-lineage-disjoint. It does not select numerical participation values, q, windows, provider values, D05 counts or outcomes.

## 1. `P_MAX_REF` and `P_TARGET_REF` do not have the same authority type

The two reference-participation objects serve different roles and must not be justified by one symmetric rule.

### 1.1 `P_MAX_REF` — execution-risk governance constraint

`P_MAX_REF` is a hard reference ceiling on participation justified as an execution-risk governance constraint, not as the optimizer of an expected-cost model.

Its authority question is:

> Above what participation is the current lineage unwilling to authorize execution under the reference capacity convention, irrespective of whether an expected-cost model could make that participation appear attractive?

Therefore `P_MAX_REF` may be declared under a separately frozen execution-risk governance rule without requiring an optimized spread/impact tradeoff.

It must satisfy:

`0 < P_MAX_REF < 1`.

This artifact freezes the authority **type**, not the numerical ceiling.

**Invariants**

- `P_MAX_REF_IS_EXECUTION_RISK_GOVERNANCE_CONSTRAINT`
- `P_MAX_REF_IS_NOT_EXPECTED_COST_OPTIMUM`
- `P_MAX_REF_PRECEDES_WINDOW_RESULTS`

### 1.2 `P_TARGET_REF` — measurement-calibration convention

`P_TARGET_REF` is not asserted to be the economically optimal participation rate.

It is a predeclared calibration reference used solely to convert the hard risk ceiling into an interpretable tolerance for ADV overprediction:

`R_CAP_REF = P_MAX_REF / P_TARGET_REF`

`EPSILON_ADV_BAR = log(R_CAP_REF)`.

Its authority question is:

> From what fixed conventional reference participation should lookback measurement error be assessed before that error would cause the hard participation ceiling to be breached?

The numerical `P_TARGET_REF` may therefore be declared as a governance/calibration convention, provided that:

- it is frozen before q/window calibration results;
- it is strictly positive and below `P_MAX_REF`;
- it is independent of Form-4 support, D05 ceilings, outcomes and resulting `W*`;
- its convention/status is stated explicitly rather than represented as a cost-optimal target.

No expected-impact optimization is required merely to call this object a calibration reference.

**Invariants**

- `P_TARGET_REF_IS_CALIBRATION_CONVENTION_NOT_EXECUTION_OPTIMUM`
- `P_TARGET_REF_DOES_NOT_CLAIM_COST_OPTIMALITY`
- `P_TARGET_REF_PRECEDES_WINDOW_RESULTS`

## 2. Reference participation is not actual deployment participation

`P_TARGET_REF` exists only for lookback-selector calibration unless a separate future policy explicitly reuses the same numerical value for actual sizing.

Therefore:

`P_TARGET_REF != P_TARGET_ACTUAL(theta)` by default.

The Capital Desk / `A_CONSTRUCTOR` may later use a distinct actual participation/sizing rule under its separately frozen authority.

Changing actual deployment participation does not automatically change `W*`.

Conversely, changing `P_TARGET_REF` changes the measurement-selector tolerance and may change `W*`; it is therefore a claim-defining calibration input even though it is not the execution target.

**Invariants**

- `REFERENCE_PARTICIPATION_IS_NOT_ACTUAL_SIZING_POLICY`
- `LOOKBACK_DOES_NOT_BECOME_W_STAR_OF_THETA`
- `P_TARGET_REF_IS_CLAIM_DEFINING_THROUGH_LOOKBACK_SELECTION`

## 3. Fingerprint consequence

Because `P_TARGET_REF` and `P_MAX_REF` determine `EPSILON_ADV_BAR`, and `EPSILON_ADV_BAR` may determine `W*`, which in turn enters the liquidity eligibility rule, the final `LIQUIDITY_ELIGIBILITY_RULE_HASH` must bind:

- `P_MAX_REF` value and authority/version identifier;
- `P_TARGET_REF` value and explicit `CALIBRATION_CONVENTION` status;
- the formula `EPSILON_ADV_BAR = log(P_MAX_REF/P_TARGET_REF)`;
- update/version rule for each object.

A post-authority change that changes the selected lookback or deployment support is a policy/fingerprint change and cannot silently inherit confirmatory authority.

**Invariant:** `REFERENCE_PARTICIPATION_OBJECTS_ARE_FINGERPRINTED_IF_THEY_CAN_CHANGE_SUPPORT`.

## 4. No false derivation claim for epsilon

With these authority types, `EPSILON_ADV_BAR` is mathematically derived from two frozen reference objects, but it is not represented as fully model-derived economic truth.

The correct interpretation is:

- `P_MAX_REF`: governance risk constraint;
- `P_TARGET_REF`: declared calibration convention;
- `EPSILON_ADV_BAR`: deterministic consequence of those two objects.

Therefore the current lineage must not describe `EPSILON_ADV_BAR` as an independently estimated economic optimum.

If either reference object remains unauthorized numerically:

`EPSILON_ADV_DERIVATION_BLOCKED`.

No convenient epsilon may substitute.

**Invariants**

- `EPSILON_IS_DERIVED_FROM_GOVERNED_REFERENCES_NOT_CLAIMED_OPTIMUM`
- `CONVENTIONAL_INPUT_STATUS_PROPAGATES_TO_EPSILON_INTERPRETATION`

## 5. q-selection and window-selection splits are disjoint by security lineage

Observation/date disjointness alone is insufficient because liquidity dynamics and forecast errors persist within a security through time.

Define a frozen calibration grouping key:

`CALIBRATION_SECURITY_LINEAGE_ID`

which identifies one coherent economic security/listing lineage across ordinary ticker changes and other resolver-authorized identity transitions.

All observations belonging to one `CALIBRATION_SECURITY_LINEAGE_ID` must be assigned to exactly one of:

- `Q_SELECTION_SPLIT`; or
- `WINDOW_SELECTION_SPLIT`.

No security lineage may appear in both splits, even on disjoint dates.

Ticker renames or listing-identifier changes that remain one coherent security lineage do not create permission to cross the split boundary.

If the source/resolver cannot determine the lineage grouping needed to prevent cross-split identity leakage, split authority is unresolved rather than falling back to row-level randomization.

**Invariants**

- `Q_AND_WINDOW_SPLITS_ARE_SECURITY_LINEAGE_DISJOINT`
- `DATE_DISJOINTNESS_ALONE_IS_INSUFFICIENT`
- `TICKER_CHANGE_DOES_NOT_RESET_CALIBRATION_IDENTITY`
- `NO_ROW_LEVEL_SPLIT_FALLBACK_WHEN_SECURITY_LINEAGE_IS_UNRESOLVED`

## 6. Split construction must precede q and window results

Before any q-stability or candidate-window result is inspected, freeze/hash:

- security-lineage grouping rule;
- deterministic assignment procedure from eligible lineages to q-selection versus window-selection split;
- target split proportions/count rule;
- any stratification variables and their source semantics;
- minimum lineages required in each split;
- failure rule when the calibration corpus is too small or cannot satisfy required coverage in both splits.

Assignment may not be revised because:

- a q estimate is unstable;
- a preferred q fails;
- a preferred window fails;
- one split produces a more convenient `W*`.

**Invariant:** `SECURITY_SPLIT_ASSIGNMENT_PRECEDES_Q_AND_WINDOW_RESULTS`.

## 7. Equal-security weighting remains downstream of the split

The existing rule that each eligible calibration security receives equal total mass remains controlling **within the split used for the relevant calculation**.

The split does not authorize market-cap, ADV or history-length weighting.

A security lineage with more dates does not receive more total mass merely because it has a longer history.

## 8. Revised procedural order

The current-lineage order is now:

`freeze calibration domain / source semantics / security-lineage resolver`

`-> freeze security-lineage-disjoint split assignment`

`-> freeze candidate windows`

`-> freeze P_MAX_REF authority rule + numerical value`

`-> freeze P_TARGET_REF calibration convention + numerical value`

`-> derive EPSILON_ADV_BAR = log(P_MAX_REF/P_TARGET_REF)`

`-> freeze q candidates / stability statistic / resampling / threshold`

`-> select q using only Q_SELECTION_SPLIT`

`-> freeze q`

`-> run lambda endpoint discharge and W* selection using only WINDOW_SELECTION_SPLIT`

`-> if lambda nonmaterial, authorize W* subject to remaining gates`

`-> if lambda material, resolve upstream allocation/marginal-economics dependencies before W* authority`.

No q-selection statistic may consume window-selection securities, and no window-selector object may be redesigned after either split's results.

## 9. Current state

Closed/frozen:

- `P_MAX_REF` authority type = hard execution-risk governance constraint;
- `P_TARGET_REF` authority type = explicit measurement-calibration convention, not claimed optimum;
- reference participation is separated from actual sizing participation;
- both reference objects are fingerprinted if they can change selected lookback/support;
- epsilon interpretation preserves the conventional status of its inputs;
- q/window calibration separation is security-lineage-disjoint, not merely date-disjoint;
- ticker/listing renames within one coherent lineage remain in one split.

Still open before calibration:

- numerical `P_MAX_REF` and its exact governance rationale;
- numerical `P_TARGET_REF` and its exact convention rationale;
- exact `CALIBRATION_SECURITY_LINEAGE_ID` resolver implementation;
- deterministic split proportions/assignment/stratification/minimum-size rule;
- q candidate set / stability statistic / resampling / stability threshold;
- candidate windows;
- source/provider and daily-notional route;
- calibration-domain implementation;
- calendar/date sampling;
- true-zero target treatment;
- minimum-history / insufficient-history policy.

No numerical q/window calibration, D05 ceiling visibility or Form-4 outcome access is authorized by this artifact.
