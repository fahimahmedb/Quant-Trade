# BLUE — ONE BIG BUILD PRESTAGE — FIRST TRACEABLE ECONOMIC LOOP — 2026-09-21

## 0. Status / authority boundary

This document prepares the future single Product Builder mission.

It is NOT implementation authority.

```text
ONE_BIG_BUILD_PRESTAGE = READY_PENDING_COHORT_GEOMETRY
VERTICAL_LOOP_BUILD_SPEC = NOT_FROZEN
PRODUCT_IMPLEMENTATION_AUTHORIZED = FALSE
PRODUCT_INTEGRATION = PAUSED
TARGET_HOST_TOUCHED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
```

```text
ECONOMIC_PROGRESS = Product implementation scope, authority ordering, milestones,
  provenance chain, failure semantics and acceptance matrix are prepared in advance.
REMAINING_BLOCKER = exact prospective cohort/inference geometry from the active
  FIRST_SLICE_COHORT_INFORMATION_GEOMETRY_CLOSURE mission.
EXIT_CONDITION = receive COHORT_GEOMETRY_READY_FOR_SPEC_FREEZE, substitute the finite
  pending science fields below, live-refresh exact refs/base SHA, then issue one frozen
  Builder mission without another general architecture cycle.
```

This prestage does not create the future Builder branch.

## 1. Terminal implementation objective

The future single build must create the first traceable economic loop:

```text
Forward
-> Research
-> Scientific Effect
-> Economic Assessment
-> SHADOW admission
-> SIZE
-> RISK
-> FILLS
-> BOOK
-> Learning
```

The implementation succeeds when Quant can:

- fail closed on unavailable/invalid evidence;
- produce a lawful scientific effect artifact when enough prospective evidence exists;
- distinguish DEVELOPMENT from lawful FORWARD_CONFIRMATION;
- decide whether the effect survives real modeled frictions;
- compute one authoritative economic size;
- preserve independent portfolio Risk authority;
- perform exactly one authoritative shadow execution path;
- mutate one persistent Book idempotently;
- persist both TRADE and NO_TRADE outcomes for later Learning;
- preserve enough immutable history to answer the accepted Q1-Q12 economic questions over time.

Profitability is not an acceptance criterion.
A valid NO_TRADE result is a successful system decision.

## 2. Frozen architecture decisions — do not reopen

The future Builder receives these as fixed unless exact current code creates a concrete contradiction.

### 2.1 Scientific / Economic boundary

No current Research metric such as net return, gross portfolio return, Sharpe,
t-statistic or beta is a substitute for the frozen Economic effect coordinate.

Planned producer:

`src/quant/science/effect.py :: assemble_form4_effect`

It returns a typed immutable scientific artifact and optional lawful `EffectEstimate`.

Missing/invalid scientific authority must fail closed.

### 2.2 Promotion boundary

`SHADOW` means scientifically validated + economically admitted for shadow trading.

Required ordering:

```text
Research validated
-> scientific/evidence adjudication
-> durable Economic AssessmentRecord
-> Economic CONTINUE + capital-order-eligible
-> VALIDATED -> SHADOW
-> Desk opportunity
-> SIZE
-> RISK
-> FILL | VETO | NO_TRADE
```

Research alone must never auto-promote `VALIDATED -> SHADOW`.

### 2.3 SIZE

```text
available_lane_capital = current_decision_NAV * strategy_allocation
economic_margin_notional = MarginSizingRule(...)
desk_lifecycle_cap_notional =
    available_lane_capital * definition.capital_fraction
FINAL_SIZE = min(economic_margin_notional, desk_lifecycle_cap_notional)
```

Economic owns opportunity sizing.
Lifecycle capital fraction is only a ceiling.
Risk remains downstream and independent.
Zero size is valid.

### 2.4 RISK

Economic CONTINUE is not an approved order.

Existing Desk Risk remains the sole downstream portfolio veto/throttle authority.

### 2.5 FILLS / BOOK

`src/quant/desk/execution.py::ExecutionModel.fill` remains the sole shadow-fill authority.

No second execution engine may feed Book.

The existing persistent Ledger remains the sole Book.

No fresh bankroll per experiment/run/restart.

### 2.6 Cost consistency — both checks mandatory

Before sizing:
- bind the exact authoritative ExecutionModel type/version/config;
- compare Research/Economic execution assumptions over the declared participation envelope;
- same units/components/reference-notional conventions;
- Research/Economic assumptions must not be cheaper than executable assumptions.

After sizing and before fill:
- derive actual implied participation from final proposed notional/quantity and current authorized ADV/capacity input;
- re-check the same envelope after rounding/capacity transformations;
- any violation fails closed before `ExecutionModel.fill`.

### 2.7 Forward evidence identity

Forward confirmation identity is session/content-address scoped, not whole-ledger scoped.

Unrelated ledger growth must not refresh already-consumed evidence.

FORWARD_CONFIRMATION is never a caller Boolean.

### 2.8 Learning durability

The human-readable last-200 lesson window is not idempotence authority.

Processed Research/Economic outcome identities and semantic payload digests must survive restart independently of that display window.

Same processed id + same semantics = no-op.
Same processed id + conflicting semantics = conflict/fail closed.

## 3. Accepted economic question surface

The future build must support or persist the evidence needed for:

- Q1: does the effect exist?
- Q2: is the evidence valid?
- Q3: DEVELOPMENT vs FORWARD_CONFIRMATION?
- Q4: does the effect survive frictions?
- Q5: what size is economically justified?
- Q6: does portfolio Risk accept/scale/veto it?
- Q7: is TRADE economically superior to NO_TRADE?
- Q8: did execution preserve the expected edge?
- Q9: did the decision increase modeled/real wealth?
- Q10: is the edge persistent or decaying?
- Q11: was a rejection later shown to be correct/false?
- Q12: where should Research search next?

First-build behavior:
- Q1-Q8: directly answerable or explicit fail-closed/insufficient states;
- Q9: persist first shadow wealth/contribution outcome;
- Q10-Q12: persist raw evidence from the first decision, while later verdicts wait for repeated evidence;
- real-execution forms of Q8/Q9 remain deferred until separately authorized live execution.

## 4. Current final science placeholders — ONLY remaining freeze variables

The active cohort-geometry mission alone may fill these fields.

Until then, they remain non-authoritative placeholders:

```text
PENDING_COHORT_GEOMETRY.protocol_id =
PENDING_COHORT_GEOMETRY.entry_session_horizon =
PENDING_COHORT_GEOMETRY.registration_freeze_instant =
PENDING_COHORT_GEOMETRY.influence_span =
PENDING_COHORT_GEOMETRY.component_or_block_construction =
PENDING_COHORT_GEOMETRY.minimum_information_guard =
PENDING_COHORT_GEOMETRY.interval_method =
PENDING_COHORT_GEOMETRY.interval_parameters =
PENDING_COHORT_GEOMETRY.repeated_cohort_accumulation_rule =
PENDING_COHORT_GEOMETRY.one_look_multiplicity_rule =
PENDING_COHORT_GEOMETRY.development_before_guard_rule =
PENDING_COHORT_GEOMETRY.forward_confirmation_rule =
PENDING_COHORT_GEOMETRY.first_lawful_q1_q2_condition =
```

No Builder may infer or choose these values.

If Rail B returns `COHORT_GEOMETRY_BLOCKED_<EXACT_REASON>`, Blue must revise the build disposition before implementation rather than letting the Builder invent science.

## 5. Code-availability decision — closed now

Blue chooses bounded selective composition, not whole-branch merge.

Future Builder base:
- exact base SHA will be named only at final dispatch after live refresh;
- do not assume an old Blue/Product SHA remains current.

Canonical sources remain pinned semantically:
- Forward: `parallel/claude-forward-data-2026-09-20@83521dbfdd90027c90d04adfb7d814593c2355c5`
- Economic: `parallel/claude-economic-v2-2026-09-20@35dff27b8fac53618da434ee6d31febbddcc0e69`

Future Builder must import only the exact transitive dependency closure needed by the vertical slice from those pinned authorities.

Rules:
- copied REUSE_AS_IS files remain byte-identical to their source SHA;
- record source SHA + blob identity in the Builder handoff;
- no whole Forward branch merge;
- no whole Economic branch merge;
- any file requiring semantic modification belongs in the explicit ADAPT allowlist, never silently edited while vendoring;
- resolve and document the transitive import closure before the first semantic Product edit.

Expected canonical reusable surfaces include, subject to exact dependency closure:
- Forward recorder/admissibility contracts needed by the session-scoped evidence path;
- Form-4 eligibility/formation/inference primitives;
- Economic coordinate/decision/journal/recipe/friction/value/state/capacity/consistency/sizing surfaces.

This closes the old `PRODUCT_SPINE_DEPENDENCY_AVAILABILITY` sequencing ambiguity.

## 6. Expected implementation surface

### New scientific/integration surfaces

Expected new paths:
- `src/quant/science/effect.py`
- `src/quant/integration/__init__.py`
- `src/quant/integration/forward_adapter.py`
- `src/quant/integration/econ_bridge.py`

A separate generic framework/plugin architecture is forbidden unless a concrete code dependency makes it unavoidable.

### Existing Product surfaces to adapt

Expected ADAPT paths:
- `src/quant/factory/workers.py`
  - remove Research-owned `VALIDATED -> SHADOW`;
- `src/quant/factory/strategies.py`
  - only narrow lifecycle/provenance adaptation if required;
- `src/quant/desk/desk.py`
  - pre-Desk Economic admission;
  - Economic size composition;
  - post-size/pre-fill consistency;
  - preserve downstream Risk/Execution/Book authority;
- `src/quant/desk/opportunity.py`
  - carry exact Research/Economic provenance if current detail surface is insufficient;
- `src/quant/learning/store.py`
  - durable Economic/Desk terminal outcomes + durable processed-id authority;
- `src/quant/paths.py`
  - only if a required durable journal/index path is genuinely absent.

### Existing authorities to preserve

Do not change semantics of:
- `src/quant/desk/risk.py` except if an exact integration contradiction is proven;
- `src/quant/desk/execution.py` as the sole Book-feeding fill authority, except the already-specified explicit scheduled-close execution-phase extension required by the frozen science holding convention;
- `src/quant/book/ledger.py` as sole Book;
- the existing Clock as sole runtime scheduler/control surface.

No second Book, scheduler, sizing engine, execution engine or ticket family.

## 7. Canonical persistent provenance chain

Every positive or negative decision must preserve:

```text
ForwardObservation
-> ResearchTicket
-> ScientificEffectArtifact
-> AssessmentRecord
-> OpportunityTicket
-> DeskJournal
-> Ledger (if executed)
-> LearningStore
```

For NO_TRADE/KILL/VETO:
- preserve the chain through the last applicable authority;
- persist the exact reason and next-action dependency;
- zero Book mutation unless a real fill has already occurred by design.

## 8. Internal milestones — ONE Builder, not four missions

The future Builder owns one branch and one final delivery.

### M1 — Scientific artifact + evidence authority

Implement:
- exact Form-4 scientific artifact assembler under the final cohort geometry;
- frozen point estimate;
- final accepted dependence/interval procedure;
- D19/missingness refusal;
- exact DeltaCoordinateBinding;
- sample/protocol/use/trial commitments;
- DEVELOPMENT/FORWARD_CONFIRMATION authority;
- synthetic marker cannot enter real admission.

Checkpoint:
`M1_SCIENTIFIC_ARTIFACT = GREEN | BLOCKED_<EXACT_REASON>`

### M2 — Research -> Economic admission

Implement:
- Forward session/content-address identity fix;
- ResearchTicket scientific envelope/reference;
- fail-closed bridge;
- `evaluate_delta_coordinate`;
- durable AssessmentRecord;
- remove Research auto-SHADOW;
- Economic-admitted `VALIDATED -> SHADOW`.

Checkpoint:
`M2_RESEARCH_ECONOMIC_BOUNDARY = GREEN | BLOCKED_<EXACT_REASON>`

### M3 — Desk / SIZE / RISK / FILLS / BOOK

Implement:
- Economic MarginSizingRule authority;
- lifecycle cap;
- pre-size execution consistency;
- post-size implied-participation consistency;
- Risk independent veto/throttle;
- sole ExecutionModel entry and scheduled-exit phases;
- deterministic Opportunity/operation identity;
- single persistent Book mutation;
- corporate-action authoritative Book records where required.

Checkpoint:
`M3_DESK_BOOK_BOUNDARY = GREEN | BLOCKED_<EXACT_REASON>`

### M4 — Learning / restart / economic-question closure

Implement:
- durable processed IDs/payload digests;
- NO_TRADE and BOOKED outcomes;
- expected-vs-realized/shadow execution records;
- counterfactual rejection record support without mutating original decision;
- raw histories required later for Q10-Q12;
- restart/replay/conflict controls;
- full deterministic vertical matrix.

Checkpoint:
`M4_LEARNING_E2E = GREEN | BLOCKED_<EXACT_REASON>`

Milestone checkpoints are internal Builder evidence only.
They do not create four Builder dispatches.

## 9. Economic Decision Card — persistence requirement

Persist or reconstruct from durable linked records at minimum:

```text
hypothesis_id
research_ticket_id
sample_id
evidence_label
delta_coordinate_hash
delta_hat
lower
upper
confidence_level
event_count

economic_margin
cost_model_identity
pre_size_cost_consistency

economic_size
lifecycle_cap
final_pre_risk_size

risk_verdict
risk_adjusted_size

execution_model_identity
post_size_participation
post_size_cost_consistency

action
reason_codes
expected_wealth_delta

book_operation_id
learning_outcome_id
```

If a field is scientifically unavailable, preserve explicit unavailable/insufficient state.
Never fabricate a value just to complete the card.

## 10. Mandatory fail-closed reasons

At minimum preserve distinct paths for:

- `EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE`
- `INSUFFICIENT_EVIDENCE`
- `DEPENDENCE_MODEL_UNSUPPORTED`
- `DELTA_COORDINATE_UNRESOLVED`
- `DELTA_COORDINATE_MISMATCH`
- invalid/non-containing/nonfinite interval;
- evidence already consumed / not forward-admissible;
- execution-model incompatibility;
- missing/stale/invalid ADV or capacity;
- economic margin insufficient;
- zero economic size;
- lifecycle cap yielding zero final size;
- Risk veto;
- `EXECUTION_COST_CONSISTENCY_EXCEEDED_AFTER_SIZING`;
- conflicting replay;
- missing scheduled-exit support;
- unresolved D19/terminal outcome.

Every refusal must produce:
- durable reason;
- zero unauthorized Book mutation;
- Learning-visible outcome/dependency.

## 11. Mandatory deterministic acceptance matrix

The future Builder test suite must prove at least:

1. missing EffectEstimate -> NO_TRADE;
2. insufficient cohort information -> no certified interval / NO_TRADE;
3. coordinate unresolved -> NO_TRADE;
4. coordinate mismatch -> NO_TRADE;
5. invalid interval -> NO_TRADE;
6. DEVELOPMENT evidence cannot masquerade as FORWARD_CONFIRMATION;
7. already-consumed forward atoms remain consumed;
8. unrelated Forward-ledger growth does not refresh identity;
9. Economic NO_TRADE -> no SHADOW/no Book mutation;
10. Economic KILL -> no SHADOW/no Book mutation;
11. Economic CONTINUE but capital-order-ineligible -> no SHADOW;
12. lawful Economic admission -> exactly one durable SHADOW transition;
13. positive margin -> positive Economic size where rule permits;
14. lifecycle cap only reduces size;
15. zero size -> zero fill;
16. pre-size cost inconsistency -> zero fill;
17. post-size participation/cost inconsistency -> zero fill;
18. Risk veto after genuine Economic CONTINUE -> zero fill;
19. valid shadow entry -> exactly one ExecutionModel.fill + Ledger mutation;
20. required scheduled exit -> exactly one authorized exit fill / lifecycle closure;
21. capacity truncation stays coherent with Risk + post-size checks;
22. crash after AssessmentRecord -> safe replay;
23. crash after Desk intent -> safe resume;
24. crash after Book apply -> no double fill;
25. same assessment id + changed inputs -> conflict;
26. same Book operation id + conflicting fill -> conflict;
27. NO_TRADE -> exactly one Learning outcome;
28. BOOKED -> exactly one Learning outcome;
29. >200 later lessons + restart + replay old Research id -> no duplicate;
30. >200 later outcomes + restart + replay old Economic id -> no duplicate;
31. counterfactual rejection outcome cannot mutate original Decision Card;
32. synthetic scientific artifact cannot reach real admission;
33. ordinary Research ticket without lawful scientific artifact stays fail-closed;
34. positive fixture proves plumbing only and is labeled synthetic;
35. full provenance chain is queryable end-to-end.

Full existing unit/integration suite must remain green.

## 12. Builder branch and final delivery shape

Intended future branch:

`builder/post-p0-first-vertical-shadow-loop-2026-09-21`

Do NOT create it before Blue freezes the spec and explicitly names:
- exact base SHA;
- exact final cohort-science contract;
- exact imported-file manifest / dependency closure;
- exact Product implementation authority.

Final Builder handoff must include:
- exact final SHA;
- exact changed-path list;
- vendored source SHA/blob manifest;
- M1-M4 checkpoint evidence;
- exact test commands/results;
- generated/schema checks if applicable;
- any unavailable real input and resulting fail-closed behavior;
- explicit statement that synthetic positive paths are not evidence of market edge.

Final Builder status may only be:

`BUILDER_VERTICAL_SHADOW_LOOP = READY_FOR_INDEPENDENT_REVIEW`

or one precise implementation blocker.

No self-certification as final Product PASS.

## 13. Independent review after Builder

One bounded independent review will test:
- scientific contract implementation;
- false-positive admission paths;
- cost consistency;
- Risk independence;
- fill/Book singular authority;
- restart/idempotence/conflicts;
- provenance;
- Q1-Q9 first-slice behavior and persistence for Q10-Q12.

Do not pre-create that reviewer now.
Do not start recurring review loops.

## 14. Freeze procedure when Rail B returns

If Rail B returns:

`COHORT_GEOMETRY_READY_FOR_SPEC_FREEZE`

Blue performs only:

1. verify Rail-B exact HEAD/handoff and any CI;
2. fill Section 4 placeholders verbatim from accepted cohort authority;
3. reconcile no contradiction with Sections 1-13;
4. live-refresh canonical Forward/Economic refs;
5. select exact future Builder base SHA;
6. compute the selective dependency import manifest;
7. change:
   `VERTICAL_LOOP_BUILD_SPEC = FROZEN`;
8. explicitly authorize and create exactly one Builder branch.

No new general architecture/prestage/challenge cycle is required absent a concrete contradiction.

If Rail B returns:

`COHORT_GEOMETRY_BLOCKED_<EXACT_REASON>`

do not launch Builder under this prestage as if positive Q1/Q2 were available.
Blue must first choose a revised Product disposition.

## 15. Current state

```text
ONE_BIG_BUILD_PRESTAGE = READY_PENDING_COHORT_GEOMETRY
CODE_AVAILABILITY_MECHANISM = SELECTIVE_PINNED_IMPORT / WHOLE_BRANCH_MERGE_FORBIDDEN
PRODUCT_IMPLEMENTATION_AUTHORIZED = FALSE
VERTICAL_LOOP_BUILD_SPEC = NOT_FROZEN
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE

ECONOMIC_PROGRESS = nearly all implementation design is now prepared before Rail B returns
REMAINING_BLOCKER = final prospective cohort/inference geometry only
EXIT_CONDITION = cohort geometry accepted -> fill finite placeholders -> freeze -> dispatch ONE Builder
```
