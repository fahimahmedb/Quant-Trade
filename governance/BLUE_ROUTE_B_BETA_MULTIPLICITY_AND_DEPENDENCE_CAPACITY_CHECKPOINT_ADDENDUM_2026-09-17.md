# BLUE ROUTE-B CHECKPOINT ADDENDUM — BETA / MULTIPLICITY / JOINT DEPENDENCE CAPACITY — 2026-09-17

**Status:** CURRENT CHECKPOINT ADDENDUM  
**Authority:** Blue Team / Mission Control  
**Parents:** `BLUE_ROUTE_B_BREACH_FREQUENCY_CHECKPOINT_ADDENDUM_2026-09-17.md`, `D05A_D09_BETA_AUTHORITY_WINDOW_MULTIPLICITY_AND_DEPENDENCE_CAPACITY_AMENDMENT_2026-09-17.md`

This addendum controls where more recent/specific than its parent checkpoint.

## 1. New controlling artifact

Add:

`governance/D05A_D09_BETA_AUTHORITY_WINDOW_MULTIPLICITY_AND_DEPENDENCE_CAPACITY_AMENDMENT_2026-09-17.md`.

## 2. BETA authority

`BETA_LIQ_MAX_AUTHORITY_TYPE = EXECUTION_RISK_BREACH_FREQUENCY_TOLERANCE`.

It is declared/frozen before calibration capacity and candidate-window results. It is not selected by available sample size and is fingerprinted because it can change `W*` and deployment support.

The reference rule has two distinct governed coordinates:

- breach magnitude: `EPSILON_ADV_BAR = log(P_MAX_REF/P_TARGET_REF)`;
- breach frequency: `BETA_LIQ_MAX`.

Neither may be traded against the other after results.

## 3. Candidate-window multiplicity

For `K = |W_SET|` candidate windows and lambda endpoint set `{0,1}`, the simultaneous authority family size is:

`M = 2K`.

Every additional candidate window consumes familywise calibration authority.

Candidate windows must therefore represent distinct predeclared measurement scales; dense/fine-grid lookback sweeping is not authorized.

## 4. One-sided breach authority

The relevant calibration error is underestimating true breach frequency.

The final authority rule must therefore use simultaneous one-sided upper protection over all `2K` breach statistics. A point estimate alone cannot certify pass status.

Exact UCB/concentration mechanics remain open until the joint dependence contract is frozen.

## 5. Effective capacity

Required reported corporate concentration diagnostic:

`N_GROUP_EFF_CORPORATE = 1 / sum_g omega_g^2`.

This object correctly discounts disproportionate mass carried by large corporate-reorganization dependence groups.

It is **not yet the final effective sample size**, because distinct corporate groups can remain dependent through common calendar/session liquidity shocks and serial market regimes.

Current state:

`BREACH_JOINT_DEPENDENCE_CONTRACT = OPEN`.

The final capacity rule must jointly address corporate, common-market/calendar and serial dependence before deriving the authority-bearing capacity requirement.

## 6. Conditional special case

If a future frozen dependence contract proves independent bounded corporate-group contributions, weighted one-sided Hoeffding plus a union bound yields the sufficient special-case requirement:

`N_GROUP_EFF_CORPORATE >= log((2K)/ALPHA_BETA) / (2 * TAU_BETA^2)`.

This is explanatory only and is not current authority absent the independence premise.

## 7. Current blockers

Still open before external breach calibration:

- numerical `P_MAX_REF`, `P_TARGET_REF`, `BETA_LIQ_MAX`;
- exact small candidate-window set and distinct-scale rationale;
- numerical `TAU_BETA`, `ALPHA_BETA`;
- exact breach estimator / simultaneous one-sided UCB construction;
- joint corporate + market/calendar + serial dependence contract;
- final authority-bearing capacity formula;
- source/provider/daily-notional route;
- calibration-domain/date-sampling/true-zero/minimum-history semantics.

If frozen available authority-bearing capacity is insufficient, emit `LIQUIDITY_BREACH_CALIBRATION_UNDERPOWERED`; do not relax risk tolerance, precision, multiplicity or dependence standards.

Route-B firewall remains unsatisfied. No external breach calibration, D05 ceiling visibility or Form-4 outcome access is authorized.
