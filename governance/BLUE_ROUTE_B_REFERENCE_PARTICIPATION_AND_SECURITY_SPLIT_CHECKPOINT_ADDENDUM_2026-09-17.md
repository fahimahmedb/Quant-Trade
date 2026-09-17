# BLUE ROUTE-B CHECKPOINT ADDENDUM — REFERENCE PARTICIPATION / SECURITY-DISJOINT SPLITS — 2026-09-17

**Status:** CURRENT CHECKPOINT ADDENDUM  
**Authority:** Blue Team / Mission Control  
**Parents:** `BLUE_ROUTE_B_LIQUIDITY_LAMBDA_DISCHARGE_CHECKPOINT_ADDENDUM_2026-09-17.md`, `D05A_D09_REFERENCE_PARTICIPATION_AUTHORITY_AND_SECURITY_DISJOINT_SPLIT_AMENDMENT_2026-09-17.md`

This addendum controls where more recent/specific than its parents.

## 1. New controlling artifact

Add:

`governance/D05A_D09_REFERENCE_PARTICIPATION_AUTHORITY_AND_SECURITY_DISJOINT_SPLIT_AMENDMENT_2026-09-17.md`.

## 2. Reference-participation authority types

Current lineage distinguishes:

- `P_MAX_REF`: **execution-risk governance constraint**, not an expected-cost optimum;
- `P_TARGET_REF`: **measurement-calibration convention**, not an execution optimum and not actual SIZE participation by default.

When both are numerically authorized:

`EPSILON_ADV_BAR = log(P_MAX_REF / P_TARGET_REF)`.

`EPSILON_ADV_BAR` is a deterministic consequence of governed reference objects, not independently estimated economic truth.

Both reference objects must be bound into `LIQUIDITY_ELIGIBILITY_RULE_HASH` if they can change `W*` / support.

Current states:

- `P_MAX_REF_AUTHORITY_TYPE = CLOSED / EXECUTION_RISK_GOVERNANCE`
- `P_TARGET_REF_AUTHORITY_TYPE = CLOSED / CALIBRATION_CONVENTION`
- `P_MAX_REF_NUMERIC = OPEN`
- `P_TARGET_REF_NUMERIC = OPEN`
- `EPSILON_ADV_DERIVATION = BLOCKED UNTIL BOTH NUMERIC REFERENCES AUTHORIZED`.

## 3. q/window split identity

q selection and W* selection must use disjoint sets of `CALIBRATION_SECURITY_LINEAGE_ID`.

Date-only or row-level disjointness is insufficient.

A ticker/listing rename that remains within one coherent security lineage stays on the same side of the split.

If security-lineage identity cannot be resolved, split authority is unresolved; no random row fallback is authorized.

Current state:

`Q_WINDOW_SPLIT_DISJOINTNESS = CLOSED / SECURITY_LINEAGE_LEVEL`.

## 4. Firewall consequences

`ROUTE_B_FINAL_PROTOCOL_FIREWALL_SATISFIED = FALSE` remains unchanged.

Before numerical q/window calibration, still require hash-addressable:

- numerical `P_MAX_REF` plus governance rationale/version;
- numerical `P_TARGET_REF` plus explicit convention rationale/version;
- `CALIBRATION_SECURITY_LINEAGE_ID` resolver;
- deterministic split assignment/proportions/stratification/minimum-size/failure rule;
- q candidates/stability/resampling/threshold;
- candidate windows;
- daily-notional source route/provider;
- calibration-domain and sampling rules;
- true-zero and minimum-history semantics.

## 5. Sequencing consequence

The next Blue closure is not yet a numerical lookback run.

It is:

1. freeze the **reference participation convention/governor values or their admissible authority source**;
2. freeze the **security-lineage split constructor**;
3. freeze q-selection mechanics;
4. only then inspect external calibration results.

No D05 ceiling visibility, Form-4 outcome access, or numerical q/window calibration is authorized by this addendum.
