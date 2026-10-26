# BLUE — FIRST VERTICAL ONE BIG BUILD FROZEN SPEC — 2026-09-21

## 0. Freeze

This document freezes the first traceable economic-loop implementation specification.

Authorities:
- `QUANT_NORTH_STAR.md`
- `governance/BLUE_ONE_BIG_BUILD_PRESTAGE_2026-09-21.md`
- `handoff/BLUE_COHORT_GEOMETRY_RECEPTION_2026-09-21.md`
- `governance/BLUE_ONE_BIG_BUILD_IMPORT_MANIFEST_2026-09-21.md`
- `governance/BLUE_POST_P0_VERTICAL_PREBIGBUILD_CORRECTION_SPEC_2026-09-21.md`
- `handoff/BLUE_ECONOMIC_QUESTION_MAP_RECEPTION_2026-09-21.md`

```text
SCIENCE_SPEC_STATE = CLOSED_FOR_IMPLEMENTATION
COHORT_GEOMETRY = FROZEN
SELECTIVE_IMPORT_MANIFEST = FROZEN
VERTICAL_LOOP_BUILD_SPEC = FROZEN

PRODUCT_IMPLEMENTATION_AUTHORIZED = FALSE
BUILDER_DISPATCH = PREPARED / NOT_YET_AUTHORIZED
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```

No further general architecture, S11-method or economic-question design cycle is
required before implementation.

## 1. Frozen science geometry

```text
protocol_id = FORM4_FIRST_VERTICAL_MULTI_COHORT_V1
entry_session_horizon = 252 per cohort
K_target = 3
K_max = 4
inter_cohort_gap = >=80 regular sessions
registration_freeze_instant =
  before cohort-1 activation and before its 20-session warm-up begins
influence_span =
  frozen S02/§10.4 formation/ADV lead -> scheduled exit,
  extended 20 regular sessions at each end
component_construction =
  frozen connected-component rule over the union of accrued cohorts;
  issuer/corporate recurrence merges across cohorts
minimum_information_guard =
  pooled post-merge positive-exposure G >= 10 AND
  max(component exposure)/A <= 0.10
primary_interval_class =
  wild cluster bootstrap / Rademacher sign-flip over pooled components
repeated_cohort_accumulation =
  stop at first fully matured cohort where structural G>=10;
  otherwise stop after K_max=4
one_claim_one_look_family_alpha = 0.05
before_guard =
  DEVELOPMENT only / no certified interval / no FORWARD_CONFIRMATION
Kmax_exhausted_below_guard =
  INSUFFICIENT_CLUSTER_INFORMATION
expected_time_to_first_lawful_Q1_Q2 =
  planning estimate ~3.6 years if K=3 reaches guard;
  up to ~5.0 years if K=4 is required
```

The calendar estimate is not a guarantee of event availability, issuer diversity or
data completeness.

## 2. One-look integrity — mandatory correction

Until the structural stopping instant:

```text
TARGET_OUTCOME_ACCESS_FOR_CONFIRMATORY_LINEAGE = FORBIDDEN
POINT_ESTIMATE_DISPLAY = FORBIDDEN
INTERVAL_COMPUTATION = FORBIDDEN
STOPPING_INPUT = STRUCTURAL_COMPONENT_FACTS_ONLY
```

Outcome-bearing records may be durably captured but must remain inaccessible to the
confirmatory inference/decision surface.

Permitted pre-stop structural inspection is limited to facts required to establish:
- cohort maturity;
- component identity/connectivity;
- issuer/corporate recurrence;
- positive-exposure component count;
- pre-outcome committed component exposure share.

If K_max is exhausted below the guard, the lineage terminates
`INSUFFICIENT_CLUSTER_INFORMATION`. Any later diagnostic point estimate is DEVELOPMENT
evidence only.

## 3. Method qualification — mandatory before FORWARD_CONFIRMATION

G>=10 permits the declared method to be attempted; it does not alone certify coverage.

The implemented interval method must produce a versioned qualification artifact bound
to this protocol containing:
- exact random-denominator statistic;
- exact Rademacher/sign-flip construction;
- deterministic enumeration/resampling/seed/runtime rules;
- declared sampling/dependence assumptions;
- prespecified null/positive/common-shock/repeated-issuer/overlap/unequal-weight/
  concentration/insufficient-information stress matrix;
- numerical behavior/coverage results under those declared models;
- explicit real-cohort applicability rationale independent of target outcomes.

Missing or failed qualification:
`DEPENDENCE_MODEL_UNSUPPORTED`
and evidence remains DEVELOPMENT.

No Builder may lower G, change K_max, alter influence spans, switch interval methods or
tune qualification against target outcomes.

## 4. Frozen implementation topology

```text
ForwardObservation
-> ResearchTicket
-> ScientificEffectArtifact
-> AssessmentRecord
-> VALIDATED -> SHADOW admission
-> OpportunityTicket
-> Economic SIZE
-> independent Risk
-> ExecutionModel.fill
-> Ledger
-> LearningStore
```

No second Book, scheduler, sizing authority, execution authority or ticket family.

## 5. Frozen Product decisions

- Research validation alone never promotes to SHADOW.
- Initial Economic admission occurs before Desk actionable selection.
- `FINAL_SIZE = min(economic_margin_notional, desk_lifecycle_cap_notional)`.
- Risk remains independent downstream veto/throttle.
- `ExecutionModel.fill` remains the sole Book-feeding shadow execution authority.
- Entry and scheduled exit are explicit execution phases under that same authority.
- Forward confirmation identity is session/content-address scoped.
- Both execution-cost consistency checks are mandatory:
  pre-size model envelope and post-size/pre-fill actual implied participation.
- Learning idempotence uses durable processed identities independent of the last-200
  display/history window.
- NO_TRADE, KILL, VETO and INSUFFICIENT are first-class durable economic outcomes.

## 6. Selective code composition

Use:
`governance/BLUE_ONE_BIG_BUILD_IMPORT_MANIFEST_2026-09-21.md`

Rules:
- exact pinned Forward/Economic blobs only;
- byte-identical REUSE_AS_IS imports;
- no whole branch merge;
- no unrelated SEC runtime/network code import;
- no silent semantic edits to imported authorities.

## 7. One Builder / four internal milestones

One future branch only:

`builder/post-p0-first-vertical-shadow-loop-2026-09-21`

Internal checkpoints:

```text
M1_SCIENTIFIC_ARTIFACT
M2_RESEARCH_ECONOMIC_BOUNDARY
M3_DESK_BOOK_BOUNDARY
M4_LEARNING_E2E
```

These are checkpoints, not four agent missions.

### M1

Implement:
- `src/quant/science/effect.py::assemble_form4_effect`;
- cohort accumulation/registration state;
- one-look quarantine;
- component construction;
- G/concentration guard;
- method qualification artifact;
- ratio/interval production or explicit refusal;
- D19 handling;
- DeltaCoordinateBinding;
- evidence-label adjudication.

### M2

Implement:
- session/content-address Forward identity;
- ResearchTicket scientific envelope/reference;
- Research -> Economic fail-closed bridge;
- durable AssessmentRecord;
- remove Research auto-SHADOW;
- Economic-admitted SHADOW transition.

### M3

Implement:
- Economic MarginSizingRule;
- lifecycle cap;
- both cost-consistency checks;
- independent Risk;
- same ExecutionModel entry/scheduled-exit phases;
- one persistent Book;
- exact provenance/operation identity;
- no double application on replay.

### M4

Implement:
- durable Learning processed-id/payload-digest authority;
- terminal NO_TRADE/BOOKED/VETO/INSUFFICIENT outcomes;
- expected-vs-realized shadow evidence;
- later rejection-counterfactual record support without original-record mutation;
- raw histories required for Q10-Q12;
- restart/replay/conflict matrix.

## 8. Economic question acceptance

The build must directly answer or fail closed for:
Q1-Q8.

It must persist the first observation needed for:
Q9-Q12.

Real/live execution variants remain separately unauthorized.

## 9. Required deterministic acceptance matrix

All cases in `governance/BLUE_ONE_BIG_BUILD_PRESTAGE_2026-09-21.md` section 11 are
mandatory, plus:

- intermediate cohort outcomes cannot be read/displayed by confirmatory inference;
- structural G checks do not inspect T_j;
- G<10 before K_max => continue accrual without statistical look;
- K_max exhausted below G=> explicit INSUFFICIENT;
- G>=10 + missing method qualification => DEVELOPMENT / DEPENDENCE_MODEL_UNSUPPORTED;
- G>=10 + valid qualification + all §10.5 receipts => interval evaluation allowed;
- protocol hash mismatch across cohorts => fail closed;
- cohort i+1 entry inside the 80-session gap => fail closed;
- cross-cohort repeated issuer merges components;
- no fifth cohort can be silently activated;
- no change to K/G/span/method after cohort-1 activation.

## 10. Builder output

The future Builder final state may only be:

`BUILDER_VERTICAL_SHADOW_LOOP = READY_FOR_INDEPENDENT_REVIEW`

or one precise implementation blocker.

It must not declare Product PASS, deployment readiness or economic profitability.

## 11. Safety

```text
PRODUCT_IMPLEMENTATION_AUTHORIZED = FALSE
PRODUCT_INTEGRATION = PAUSED
TARGET_HOST_TOUCHED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
t0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
```

## 12. Freeze result

```text
ECONOMIC_PROGRESS = first economic-loop Product specification is frozen
REMAINING_BLOCKER = explicit Blue authorization to start isolated Builder implementation
EXIT_CONDITION = one Builder delivery -> one bounded independent review
VERTICAL_LOOP_BUILD_SPEC = FROZEN
```
