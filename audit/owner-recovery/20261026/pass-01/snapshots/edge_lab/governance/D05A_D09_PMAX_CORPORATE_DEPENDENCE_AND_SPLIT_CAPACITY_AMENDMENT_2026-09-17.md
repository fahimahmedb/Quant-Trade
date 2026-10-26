# D05-A / D09 P_MAX INDEPENDENCE / CORPORATE-DEPENDENCE / SPLIT-CAPACITY AMENDMENT — 2026-09-17

**Status:** CLOSED / FROZEN STRUCTURAL AMENDMENT — NUMERICAL P_MAX / P_TARGET / q INPUTS STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D05A_D09_REFERENCE_PARTICIPATION_AUTHORITY_AND_SECURITY_DISJOINT_SPLIT_AMENDMENT_2026-09-17.md`, `D05A_D09_LIQUIDITY_LAMBDA_DISCHARGE_AND_REFERENCE_PARTICIPATION_AMENDMENT_2026-09-17.md`, `D09_ECONOMIC_CORE_EC1_ALLOCATION_WEIGHTED_EFFECT.md`

This amendment closes three structural questions before any numerical lookback calibration: the independence of `P_MAX_REF` from economic-cost optimization, corporate-action dependence in calibration splitting, and the ex-ante allocation of calibration information between q-selection and window-selection. It does not select numerical participation values, q, windows, provider values, D05 counts or outcomes.

## 1. `P_MAX_REF` is an independent execution-risk constraint

`P_MAX_REF` is a hard participation ceiling under the reference measurement convention.

Its authority is execution-risk governance. It is **not** justified by the point at which a calibrated expected-cost curve becomes unattractive or by the point at which marginal impact exceeds expected alpha.

Permitted rationale class:

> above the governed participation ceiling, the lineage refuses to rely on execution quality / market-footprint / capacity behavior as sufficiently controlled for this reference regime.

The numerical rule may later receive its own pre-frozen governance rationale and evidence class, but that rationale must not depend on:

- Form-4 return outcomes;
- `delta`;
- BEEE or MEUE;
- `K_forward` or `M_economic` values;
- the selected lookback `W*`;
- D05 ceilings or target-population retention;
- total program capital or a desired Form-4 deployment size;
- an optimization over a spread/impact cost curve.

`P_MAX_REF` is a dimensionless risk boundary. A later actual sizing policy may operate below it for economic reasons, but economics does not redefine the reference hard ceiling in the same lineage.

If the only proposed justification for a numerical `P_MAX_REF` is cost optimality or expected-alpha tradeoff:

`P_MAX_REF_AUTHORITY_UNRESOLVED`.

**Invariants**

- `P_MAX_REF_IS_EXECUTION_RISK_BOUND_NOT_COST_OPTIMUM`
- `P_MAX_REF_DOES_NOT_DEPEND_ON_DELTA_BEEE_OR_MEUE`
- `P_MAX_REF_DOES_NOT_DEPEND_ON_FORM4_CAPITAL_SIZE`
- `COST_MODEL_CANNOT_RETROFIT_P_MAX_REF`

## 2. `P_TARGET_REF` remains a convention and does not weaken the P_MAX independence

The parent authority split remains controlling:

- `P_MAX_REF` = hard execution-risk governance constraint;
- `P_TARGET_REF` = measurement-calibration convention, not claimed execution optimum.

Therefore:

`EPSILON_ADV_BAR = log(P_MAX_REF / P_TARGET_REF)`

is a deterministic tolerance implied by one hard governed ceiling and one declared calibration convention.

The conventional status of `P_TARGET_REF` is not transferred backward into `P_MAX_REF`: the ceiling keeps its independent risk-governance authority type.

Both objects remain fingerprinted because their ratio can change `W*` and therefore deployment support.

## 3. Ordinary identity continuity versus corporate reorganization dependence

The existing `CALIBRATION_SECURITY_LINEAGE_ID` remains the coherent economic security/listing lineage across ordinary identity transitions such as resolver-authorized ticker or listing identifier changes.

Ordinary stock splits / reverse splits do not create a new calibration lineage merely because share count or price scale changes; they remain corporate-action-consistent observations inside the same lineage when the authorized market-data convention can represent them coherently.

Mergers, acquisitions with successor identity, spin-offs / separations, and other material reorganizations can connect multiple otherwise distinct lineages. They create dependence that cannot be handled by pretending each successor/predecessor lineage is independent for split construction.

Define a second grouping object:

`CALIBRATION_DEPENDENCE_GROUP_ID`.

It is the connected component of the frozen corporate-action linkage graph over the calibration horizon, where nodes are `CALIBRATION_SECURITY_LINEAGE_ID`s and edges represent an authorized material reorganization that combines, succeeds, separates or otherwise links economic lineages in a way relevant to persistent liquidity characteristics.

Examples:

- two predecessor lineages merging into one successor -> all predecessors and successor share one dependence group;
- one parent lineage producing a spin-off lineage -> parent and spin-off share one dependence group;
- serial resolved reorganizations propagate transitively through the connected component.

This object is for calibration-dependence governance. It does not redefine issuer identity, Form-4 scientific formation, or the final deployment-security resolver.

**Invariants**

- `CORPORATE_REORGANIZATION_CREATES_CALIBRATION_DEPENDENCE_GROUPING`
- `ORDINARY_TICKER_CHANGE_DOES_NOT_RESET_DEPENDENCE_GROUP`
- `STOCK_SPLIT_DOES_NOT_BY_ITSELF_CREATE_NEW_CALIBRATION_LINEAGE`
- `CALIBRATION_DEPENDENCE_GROUP_DOES_NOT_REDEFINE_FORM4_ISSUER_IDENTITY`

## 4. Corporate-action ambiguity is excluded, not guessed

If the authorized source/resolver cannot establish the corporate-action linkage needed to assign an affected lineage unambiguously to a `CALIBRATION_DEPENDENCE_GROUP_ID`, no implementation-specific guess or row-level fallback is permitted.

Emit:

`CALIBRATION_DEPENDENCE_GROUP_UNRESOLVED`.

The affected ambiguous lineage(s), and any already-resolved linked group whose boundary cannot be established safely, are excluded from q/window calibration under the frozen rule unless a separately frozen recovery procedure resolves the linkage before calibration results.

The calibration corpus is external and is expected to be broad enough that preserving split independence takes precedence over retaining a small number of ambiguous reorganizations.

No exclusion decision may depend on which split/window/result would benefit from retaining the object.

**Invariants**

- `AMBIGUOUS_CORPORATE_LINKAGE_IS_EXCLUDED_NOT_GUESSED`
- `NO_SPLIT_ASSIGNMENT_FALLBACK_FOR_UNRESOLVED_REORGANIZATION`
- `CALIBRATION_RETENTION_DOES_NOT_OVERRIDE_DEPENDENCE_INTEGRITY`

## 5. q-selection and window-selection splits are disjoint by dependence group

The parent requirement of security-lineage disjointness is strengthened:

all lineages in one `CALIBRATION_DEPENDENCE_GROUP_ID` must be assigned to exactly one of:

- `Q_SELECTION_SPLIT`; or
- `WINDOW_SELECTION_SPLIT`.

No dependence group may cross the split boundary.

This implies security-lineage disjointness automatically but is stricter for mergers/spin-offs and related reorganizations.

The deterministic split constructor operates on dependence groups, not rows and not ticker symbols.

**Invariants**

- `Q_AND_WINDOW_SPLITS_ARE_CORPORATE_DEPENDENCE_GROUP_DISJOINT`
- `DEPENDENCE_GROUP_ASSIGNMENT_DOMINATES_ROW_OR_DATE_DISJOINTNESS`

## 6. q resampling uses the same dependence group as the resampling cluster

Preventing cross-split leakage is insufficient if the q-stability procedure then resamples related predecessor/successor/spin-off lineages as independent units.

Therefore the q-selection resampling/stability procedure must use `CALIBRATION_DEPENDENCE_GROUP_ID` as its outer resampling cluster.

Within a selected dependence group, the separately frozen procedure may preserve the existing per-security equal-total-mass loss weighting, but the group must enter/leave a resample as a coherent cluster unless a stronger dependence model is separately frozen before results.

This does not assert equal total loss weight per corporate group. It specifies the independence unit for stability assessment.

**Invariants**

- `Q_STABILITY_RESAMPLES_AT_DEPENDENCE_GROUP_LEVEL`
- `CORPORATE_LINKED_LINEAGES_ARE_NOT_INDEPENDENT_RESAMPLING_UNITS`

## 7. Split capacity is intentionally asymmetric

The two splits have different jobs:

- `Q_SELECTION_SPLIT` only needs enough independent calibration dependence groups to select an estimable robustness quantile `q` under the frozen stability protocol;
- `WINDOW_SELECTION_SPLIT` carries the authority-bearing selection of `W*` and should retain as much independent external information as possible after q-selection authority is secured.

Therefore the current lineage does **not** target a symmetric 50/50 split by default.

The governing allocation principle is:

> allocate the minimum ex-ante sufficient calibration capacity to q selection, then allocate the remaining eligible dependence groups to window selection, subject to frozen coverage/stratification/minimum-size constraints for both splits.

This principle is frozen before q/window results. It is not permission to shrink the q split after observing instability.

**Invariants**

- `Q_SPLIT_IS_MINIMUM_SUFFICIENT_NOT_SYMMETRIC_BY_DEFAULT`
- `WINDOW_SPLIT_RECEIVES_RESIDUAL_INFORMATION_AFTER_Q_AUTHORITY`
- `OBSERVED_Q_INSTABILITY_CANNOT_TRIGGER_POST_HOC_SPLIT_REALLOCATION`

## 8. q protocol inputs must precede split-size derivation

Because the minimum sufficient q split depends on what `q` values and what stability guarantee are being attempted, the parent procedural order is amended.

Before deriving the target q-split capacity, freeze/hash:

- candidate `q` set;
- exact q-estimator / weighted-quantile convention;
- resampling method using dependence-group clusters;
- stability statistic;
- stability threshold;
- confidence/repetition rule if applicable;
- minimum independent dependence-group requirement;
- failure rule when the desired q authority is not estimable.

Then derive a pre-result design requirement:

`N_Q_REQUIRED`

or an equivalent deterministic split-capacity functional.

`N_Q_REQUIRED` is a **design requirement**, not the result of repeatedly trying split sizes until a preferred q becomes stable.

Only after this design is frozen may the deterministic group assignment be executed.

This supersedes the earlier ordering in which split proportions/assignment were frozen before the q-selection protocol inputs needed to justify their size.

**Invariants**

- `Q_PROTOCOL_PRECEDES_Q_SPLIT_CAPACITY_DERIVATION`
- `N_Q_REQUIRED_IS_PRE_RESULT_DESIGN_NOT_ADAPTIVE_RETRY`
- `SPLIT_SIZE_CANNOT_BE_TUNED_TO_Q_OR_W_RESULTS`

## 9. Deterministic group assignment and coverage

Before executing the split, freeze/hash:

- eligible `CALIBRATION_DEPENDENCE_GROUP_ID` universe;
- deterministic assignment algorithm and immutable seed/hash where randomness is used;
- any allowed stratification variables and their PIT/source semantics;
- coverage requirements for the intended `CALIBRATION_LIQUIDITY_DOMAIN`;
- `N_Q_REQUIRED` / q minimum capacity rule;
- minimum window-selection group count / coverage rule;
- failure state if both split requirements cannot be satisfied simultaneously.

Permitted stratification must be ex ante and non-target, for example to preserve broad coverage of the calibration liquidity domain or calendar/source regimes. It may not use candidate-window prediction losses, q-selection outcomes, Form-4 support, D05 values, BEEE/MEUE or returns.

If the eligible corpus cannot satisfy both frozen split requirements:

`CALIBRATION_SPLIT_CAPACITY_UNRESOLVED`.

No security/dependence group is borrowed across the split boundary after results.

## 10. Equal-security weighting remains distinct from split sizing

The parent equal-total-mass-per-security rule remains the loss-aggregation rule within the relevant split.

It is not the split-sizing rule.

Thus:

- split assignment is at `CALIBRATION_DEPENDENCE_GROUP_ID` level;
- q stability resampling clusters at dependence-group level;
- loss aggregation may still assign equal total mass per eligible security lineage within a split under the existing contract.

These three units serve different purposes and must not be silently collapsed.

## 11. Revised procedural order

Before any q/window calibration result:

`freeze calibration domain / source semantics / daily-notional route`

`-> freeze security-lineage resolver + corporate-action linkage graph + dependence-group constructor`

`-> freeze candidate windows`

`-> freeze P_MAX_REF authority rule and P_TARGET_REF convention rule`

`-> freeze q candidate set / estimator / clustered resampling / stability criterion / minimum-group rule`

`-> derive N_Q_REQUIRED or equivalent q-split design capacity`

`-> freeze deterministic dependence-group split assignment / stratification / minimum WINDOW capacity`

`-> instantiate q/window splits without inspecting loss results`

`-> freeze numerical P_MAX_REF and P_TARGET_REF under their predeclared authority rules`

`-> derive EPSILON_ADV_BAR`

`-> select/freeze q using only Q_SELECTION_SPLIT`

`-> run lambda endpoint discharge and W* selection using only WINDOW_SELECTION_SPLIT`

`-> if lambda nonmaterial, authorize W* subject to remaining gates`

`-> if lambda material, promote the required execution/allocation calibration to the scientific critical path`.

Any numerical source-admission rule that must precede the numerical participation values remains separately governed; this ordering does not authorize source/value shopping.

## 12. Current state

Closed/frozen:

- `P_MAX_REF` independence from cost/alpha/BEEE/MEUE/program-size optimization;
- `P_TARGET_REF` remains a calibration convention;
- corporate reorganizations create calibration dependence groups;
- unresolved corporate-action linkage is excluded rather than guessed;
- q/window splits are disjoint by dependence group;
- q stability resamples at dependence-group level;
- split capacity is intentionally asymmetric in favor of the authority-bearing window-selection split after q authority is secured;
- q protocol inputs precede derivation of q split capacity;
- split sizing is a pre-result design, not adaptive retry.

Still open before calibration:

- numerical `P_MAX_REF` and its exact governance rationale/value rule;
- numerical `P_TARGET_REF` and its exact calibration-convention rationale/value rule;
- exact security-lineage/corporate-action source and resolver implementation;
- exact q candidate set / stability statistic / resampling details / threshold / `N_Q_REQUIRED` rule;
- exact deterministic dependence-group split assignment / stratification / minimum window capacity;
- candidate windows;
- source/provider and daily-notional route;
- calibration-domain implementation;
- calendar/date sampling;
- true-zero target treatment;
- minimum-history / insufficient-history policy.

No numerical q/window calibration, D05 ceiling visibility or Form-4 outcome access is authorized by this artifact.
