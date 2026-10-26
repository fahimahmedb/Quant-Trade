# BLUE — COHORT GEOMETRY RECEPTION / SPEC-FREEZE DECISION — 2026-09-21

## 0. Received object

Branch:
`parallel/claude-first-slice-cohort-geometry-2026-09-21`

Final HEAD:
`6eb0c23da0c8f16a2dcc0c50bd1898baaa9b21d0`

Handoff:
`handoff/CLAUDE_FIRST_SLICE_COHORT_GEOMETRY_2026-09-21.md`

Reviewer verdict:
`COHORT_GEOMETRY_READY_FOR_SPEC_FREEZE`

Delivery delta:
- one handoff only;
- no Product/science implementation changed.

## 1. Blue reception

Blue accepts the preferred geometry:

```text
DESIGN = repeated frozen 252-entry-session cohorts
K_TARGET = 3
K_MAX = 4
INTER_COHORT_GAP = >=80 regular sessions
POOLING = union of components across accrued cohorts
STOPPING_GUARD = pooled post-merge G >= 10
CONCENTRATION_GUARD = max(component exposure)/A <= 0.10
PRIMARY_INTERVAL_CLASS = wild cluster bootstrap / Rademacher sign-flip
ONE_CLAIM_ONE_LOOK = TRUE
```

All prior S01-S10 and S12-S17 scientific rules remain fixed.

## 2. Blue correction required for one-look integrity

The handoff contains two statements that cannot both remain operationally true:

- before the information guard, the point ratio may be reported diagnostically;
- no estimate or interval is computed/examined before the stopping instant.

Blue resolves this in favor of strict one-look integrity.

For this prospective confirmatory lineage:

```text
INTERMEDIATE_TARGET_OUTCOME_ACCESS = FORBIDDEN
INTERMEDIATE_POINT_ESTIMATE_DISPLAY = FORBIDDEN
INTERMEDIATE_INTERVAL_COMPUTATION = FORBIDDEN
STOPPING_DECISION_INPUT = STRUCTURAL_COMPONENT_COUNT_ONLY
```

During cohort accumulation, the system may inspect only non-outcome structural facts
required to determine:
- cohort completion;
- issuer/corporate component merging;
- pooled positive-exposure component count G;
- concentration guard inputs that are fixed from pre-outcome allocation commitments.

Target T_j outcomes for earlier cohorts must remain sealed from confirmatory inference
and human/model decision surfaces until:
- G>=10 at a permitted stopping cohort; or
- K_MAX=4 is exhausted and the lineage terminates INSUFFICIENT.

After K_MAX exhaustion, diagnostic point reporting is permitted only as DEVELOPMENT
evidence and cannot retroactively restore confirmatory authority.

## 3. Method qualification boundary

G>=10 is a necessary information guard, not by itself proof of calibrated real-world
coverage.

Therefore FORWARD_CONFIRMATION additionally requires the already-specified method
qualification artifact for the exact implemented wild-cluster interval procedure,
including:
- declared dependence assumptions;
- deterministic algorithm/runtime identity;
- finite simulation/stress evidence under prespecified models;
- random-denominator handling;
- heavy-concentration stress;
- real-cohort applicability rationale independent of target outcomes.

If method qualification is missing/failed:
`DEPENDENCE_MODEL_UNSUPPORTED`
and evidence remains DEVELOPMENT.

This keeps the build fail-closed without reopening another general methods-design cycle.

## 4. Final cohort contract

```text
COHORT_PROTOCOL = FORM4_FIRST_VERTICAL_MULTI_COHORT_V1
COHORT_ENTRY_SESSIONS = 252 per cohort
K_TARGET = 3
K_MAX = 4
INTER_COHORT_GAP = >=80 regular sessions
INFLUENCE_SPAN = unchanged frozen S02/§10.4 span
COMPONENT_RULE = frozen connected-component rule over the union of accrued cohorts
ISSUER/CORPORATE_RECURRENCE = merges across cohorts
MIN_INFORMATION_GUARD = pooled post-merge positive-exposure G >= 10
MAX_COMPONENT_EXPOSURE_SHARE = 0.10
STOPPING_RULE = first fully matured cohort where G>=10; otherwise stop after K_MAX=4
STOPPING_RULE_USES_TARGET_OUTCOMES = FALSE
ONE_CLAIM_ONE_LOOK_FAMILY_ALPHA = 0.05
BEFORE_GUARD = DEVELOPMENT / NO CERTIFIED INTERVAL / NO FORWARD_CONFIRMATION
AFTER_GUARD = interval computation permitted, subject to all scientific/admissibility/method-qualification gates
KMAX_EXHAUSTED_BELOW_GUARD = INSUFFICIENT_CLUSTER_INFORMATION
EXPECTED_TIME_TO_FIRST_LAWFUL_Q1_Q2 = ~3.6 years at K=3 if guard reached; up to ~5.0 years at K=4
```

The time figures are planning estimates only, not guarantees of event availability or
issuer-recurrence behavior.

## 5. Build-freeze disposition

The design-level science blocker is closed.

```text
COHORT_GEOMETRY = ACCEPTED_WITH_BLUE_ONE_LOOK_CORRECTION
SCIENCE_SPEC_STATE = CLOSED_FOR_IMPLEMENTATION
VERTICAL_LOOP_BUILD_SPEC = READY_TO_FREEZE
PRODUCT_IMPLEMENTATION_AUTHORIZED = FALSE
PRODUCT_INTEGRATION = PAUSED
```

No profitable edge, data availability, calibrated execution cost or forward-confirmed
effect is asserted.

## 6. Exit

```text
ECONOMIC_PROGRESS = final prospective information geometry selected and reconciled
REMAINING_BLOCKER = none at design/specification level
EXIT_CONDITION = met; freeze one-big-build spec without another architecture loop
```
