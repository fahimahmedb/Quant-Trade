# BLUE — POST-P0 VERTICAL ADVERSARIAL CHALLENGE RECEPTION / PRE-BIG-BUILD CORRECTION SPEC — 2026-09-21

## 0. Reception

Advisory challenge received from:

`claude/confident-mendel-h4qqo4@9e6431dedaa621d58218f6ffb09ed1300de1bd1b`

Handoff:

`handoff/CLAUDE_POST_P0_VERTICAL_ADVERSARIAL_CHALLENGE_2026-09-21.md`

Advisory verdict:

`VERTICAL_CHALLENGE = PASS_WITH_REQUIRED_PREBUILD_CORRECTIONS`

Blue disposition:

`VERTICAL_CHALLENGE = ACCEPTED_WITH_BLUE_CORRECTION_CONSOLIDATION`

This is not implementation evidence and does not authorize Product integration.

Safety remains:

```text
PRODUCT_CODE_MODIFIED = FALSE
PRODUCT_INTEGRATION = PAUSED
P0_RUNTIME_MUTATION = FALSE
TARGET_HOST_TOUCHED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
t0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
```

## 1. Challenge integrity

The challenger wrote one handoff only and did not modify Product code, tests,
schemas, scripts, workflows or P0 runtime.

The challenge independently re-read the exact Product, Forward and Economic code
needed for the falsification questions.

Blue accepts the challenge as advisory design evidence.

## 2. Accepted findings

Blue accepts the following findings as real pre-build corrections or explicit
pre-build contracts.

### C1 — D2/D3 / Desk eligibility circularity

The challenge correctly established that deleting the current Research
`VALIDATED -> SHADOW` auto-promotion while still reading
`StrategyDefinition.capital_fraction` during Desk SIZE would force a passed
`VALIDATED` strategy to a zero lifecycle cap.

Blue additionally verified a deeper current-code constraint:

`CapitalDesk.actionable()` only returns definitions where:

- `definition.tradable`; or
- `definition.evaluation_track`.

A normal research-passed `VALIDATED` strategy has neither.

Therefore a plain `VALIDATED` strategy cannot currently enter
`CapitalDesk._run_strategy()` at all.

This means the earlier draft idea of placing the initial Economic promotion gate
inside the current Desk chain before SHADOW is not a valid minimal composition.

### C2 — estimator coordinate identity is not enforced

Accepted.

`EffectEstimate.estimator_form` is only a string equality check.

The already-existing:

`evaluate_delta_coordinate(DeltaCoordinateBinding)`

must be used for the estimator that produced `delta_hat/lower/upper`, not only
for the MEUE threshold/recipe side.

### C3 — Forward confirmation identity is too coarse

Accepted.

The current `forward_dataset_view` uses:

- whole-ledger `ledger_fingerprint()`; and
- whole-ledger `earliest_recorded_at()`

for a session-specific confirmation decision.

Unrelated ledger growth can change version identity and therefore sever prior
UseLedger consumption identity for unchanged evidence.

Session-specific confirmation must bind to the exact session/content-address set
being evaluated.

### C4 — execution-cost consistency needs two phases

Accepted.

The pre-Economic check may validate the declared modelling/participation ceiling.

After final sizing, the system must derive the actual implied participation from the
sized notional and re-check that the concrete proposed order remains inside the same
execution-cost consistency envelope.

If not:

`NO_TRADE / EXECUTION_COST_CONSISTENCY_EXCEEDED_AFTER_SIZING`

No fill is allowed.

### C5 — LearningStore replay idempotence is not durable beyond the 200-entry window

Accepted.

`LearningStore.save()` persists only:

`self.lessons[-200:]`

while `record_research` discovers duplicates by scanning the in-memory/persisted
lesson list.

After an older lesson ages out and the process restarts, replay of that old ticket can
create a duplicate lesson and re-apply its lane-priority delta.

The challenger correctly marked:

`LEARNING_FEEDBACK = FAIL`

but accidentally omitted this defect from its six-item
`PRE_BIG_BUILD_CORRECTION_SET`.

Blue corrects that omission here.

### C6 — Antigravity conflict precedence

Accepted.

Where Antigravity and the later exact-code build-prep conflict:

- the Antigravity description of `delta_hat` as ordinary mean per-trade return is
  superseded;
- the hypothetical Antigravity operation-id formula is not authoritative over the
  exact current Book/Desk code.

Later exact-code build-prep + this Blue correction spec control.

### C7 — E2E matrix is incomplete

Accepted.

The future large Builder mission must explicitly include the missing controls rather
than relying only on the three headline scenarios.

At minimum add:

- invalid confidence interval -> NO_TRADE;
- coordinate mismatch/unresolved -> NO_TRADE;
- unadmitted/previously-consumed forward evidence -> never FORWARD_CONFIRMATION;
- unrelated forward-ledger growth cannot reset consumption identity;
- capacity truncation through the assembled vertical path;
- crash/restart after Economic assessment;
- crash/restart after Desk intent before Book apply;
- crash/restart after Book apply before final commit/outcome;
- same economic assessment id + changed inputs -> conflict;
- same Book operation id + conflicting fill -> conflict;
- >200 Learning outcomes + restart + replay of old id -> no duplicate outcome.

### C8 — real Research -> frozen EffectEstimate producer remains unresolved

This was already identified before the challenge and remains open.

Current ordinary Research output does not yet prove that it natively produces the
frozen Economic coordinate.

A positive fixture can prove integration plumbing, but cannot establish that real
Research currently emits a lawful positive `EffectEstimate`.

Before the big-build specification is frozen, Blue requires one exact scientific
output contract identifying:

- the producer function/module;
- the frozen delta estimand;
- point-estimate computation;
- interval computation;
- confidence level semantics;
- clustering provenance;
- exact DeltaCoordinateBinding;
- sample provenance;
- allocation-constructor identity;
- proof that allocation weights precede outcomes.

If existing science code cannot provide that contract, the large build must retain
real Research -> Economic as fail-closed NO_TRADE and must not fabricate the producer.

## 3. Blue resolution of C1 — exact promotion boundary

Blue chooses the following semantics.

`SHADOW` means:

> scientifically validated and economically admitted for shadow trading.

It does NOT mean:

> a fill has already occurred.

Therefore the transition is intentionally before the first shadow fill, but only
after durable Economic admission.

Required high-level sequence:

```text
RESEARCH
  -> VALIDATED
  -> ECONOMIC ASSESSMENT
       -> NO_TRADE / KILL     => remain non-tradable
       -> CONTINUE + capital-order-eligible
            -> persist AssessmentRecord
            -> VALIDATED -> SHADOW
            -> persist StrategyRegistry transition
            -> next/current authorized Desk opportunity
                 -> SIZE
                 -> RISK
                 -> FILL | NO_TRADE/VETO
```

A per-opportunity Risk veto does not by itself undo the strategy's broader SHADOW
eligibility.

This resolves the challenger's D2/D3 circularity without inventing a prospective
capital fraction for a lifecycle state the object does not yet hold.

It also respects the current Desk invariant that only tradable/evaluation-track
strategies enter `CapitalDesk.actionable()`.

### Important implementation consequence

The initial Research -> Economic promotion step must be outside the current
`CapitalDesk._run_strategy()` path, or must be an explicit pre-Desk orchestration
step that completes before `CapitalDesk.run_session()` selects actionable strategies
and ledger authority.

Do not simply insert the first Economic gate halfway through the current Desk VET
block.

## 4. Blue resolution of D2 after C1

Once a strategy is durably `SHADOW`, the Desk may read the real current lifecycle cap.

Define for the first vertical slice:

```text
available_lane_capital
    = current_decision_NAV * strategy_allocation

economic_margin_notional
    = Economic MarginSizingRule applied to
      current available_lane_capital and the persisted/current Economic margin

desk_lifecycle_cap_notional
    = available_lane_capital * definition.capital_fraction

FINAL_SIZE
    = min(economic_margin_notional, desk_lifecycle_cap_notional)
```

For ordinary SHADOW:

`definition.capital_fraction == TRADABLE["SHADOW"] == 0.35`

Economic sizing remains authoritative for opportunity sizing.

The lifecycle fraction is only a ceiling.

Risk remains an independent downstream veto/throttle.

Zero remains valid.

## 5. Delta-coordinate contract

The future Research-side frozen estimate must carry or reference an exact:

`DeltaCoordinateBinding`

The Research -> Economic bridge must:

1. load/construct that binding from authoritative Research output;
2. call `evaluate_delta_coordinate`;
3. require `.compatible == True`;
4. verify that point estimate and interval both refer to that same binding;
5. preserve the binding hash in Economic provenance.

Required refusal reasons are distinct:

- missing estimate:
  `EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE`
- undeclared binding:
  `DELTA_COORDINATE_UNRESOLVED`
- incompatible binding:
  `DELTA_COORDINATE_MISMATCH`

A matching `estimator_form` string alone is never sufficient.

## 6. Forward confirmation contract

For a session-specific confirmation decision, dataset identity must be derived from
the exact evidence consumed for that session.

The future adaptation must bind at minimum:

- `dataset_id`;
- `session_date`;
- exact sorted contributing content addresses;
- session seal;
- session-scoped recorded-at facts required by the timing rule.

The same unchanged session evidence must retain the same UseLedger identity when
unrelated future observations are appended to the recorder.

Unrelated ledger growth must not create a fresh admissibility identity for already
spent evidence.

The exact implementation may use `session_seal(session_date)` plus exact
session-record identity, but the future Builder must prove collision/identity behavior
with tests rather than merely rename the whole-ledger fingerprint.

## 7. Execution-cost consistency contract

Pre-sizing:

- bind to the actual Blue Desk `ExecutionModel`;
- verify research/economic model coefficients are not cheaper than the authorized
  execution model;
- use the declared participation ceiling/assumption.

Post-sizing:

- derive implied participation from the actual final SizingPlan and authorized
  capacity/ADV input;
- require the implied participation to remain within the pre-checked consistency
  envelope.

If Risk subsequently scales DOWN the order, this cannot create a higher participation
than the pre-Risk sized order and therefore does not require a wider envelope.

If any later transformation could increase participation, re-check before fill.

## 8. Learning durability contract

Do not use the last-200 lesson display/history window as the idempotence authority.

The large build must provide a separately durable exact idempotence identity for:

- Research lessons;
- Economic/Desk terminal outcomes.

Minimum semantics:

- bounded human-readable lesson history may remain capped;
- exact processed lesson/outcome IDs must survive restart independently of that cap;
- replay of an old already-processed ID remains a no-op even after >200 later lessons;
- same ID with materially conflicting semantic payload must not silently overwrite.

Implementation may use a dedicated durable key index/journal, but must not turn the
human-facing lesson list itself into an unbounded proof store merely to fix replay.

## 9. Book operation-id boundary

For the first vertical slice, existing one-fill-per-symbol-per-opportunity semantics
may remain unchanged.

The known partial-fill/follow-up limitation is explicitly:

`DEFERRED_BEYOND_FIRST_VERTICAL_SLICE`

Do not claim the current operation-id scheme generalizes to arbitrary multi-fill
continuations.

If follow-up/partial-completion behavior enters the large build scope, operation
identity must be revisited then.

## 10. Big-build test matrix

The future large Builder must implement deterministic tests for at least:

1. missing EffectEstimate -> NO_TRADE;
2. DeltaCoordinateBinding unresolved -> NO_TRADE;
3. DeltaCoordinateBinding mismatch -> NO_TRADE;
4. invalid estimate interval/confidence -> NO_TRADE;
5. forward evidence already consumed -> no FORWARD_CONFIRMATION;
6. unrelated ledger growth -> same consumed session still remains consumed;
7. Economic NO_TRADE -> no SHADOW promotion/no Book mutation;
8. Economic KILL -> no SHADOW promotion/no Book mutation;
9. Economic CONTINUE but capital-order-ineligible -> no SHADOW promotion;
10. Economic CONTINUE + eligible -> durable VALIDATED -> SHADOW promotion;
11. SHADOW positive margin -> positive Economic size;
12. lifecycle cap actually caps but never creates size;
13. zero Economic size -> no fill;
14. Risk veto -> no fill;
15. post-size participation consistency failure -> no fill;
16. valid positive path -> exactly one fill and one Book mutation;
17. capacity-truncated valid path -> coherent executed portfolio + final Risk recheck;
18. replay positive path -> no double fill;
19. restart after AssessmentRecord persistence -> no duplicate assessment;
20. restart after DeskJournal intent -> safe resume;
21. restart after Ledger apply -> no double fill;
22. same assessment id + changed inputs -> conflict;
23. same operation id + conflicting fill -> conflict;
24. NO_TRADE -> one durable Learning outcome;
25. BOOKED -> one durable Learning outcome;
26. >200 subsequent lessons + restart + replay old Research id -> no duplicate;
27. >200 subsequent lessons + restart + replay old Economic outcome id -> no duplicate;
28. VALIDATED alone -> never actionable in capital Desk;
29. only economically admitted SHADOW strategy enters capital authority;
30. ordinary real Research lacking frozen estimate -> fail-closed NO_TRADE.

## 11. Build-freeze state

Current state after Blue consolidation:

```text
SCIENCE_EFFECT_ESTIMATE_CONTRACT = NOT_YET_CLOSED
DELTA_COORDINATE_RUNTIME_BINDING = SPECIFIED / NOT_IMPLEMENTED
PIT_PROVENANCE_CONTRACT = CORRECTION_SPECIFIED / NOT_IMPLEMENTED
ECONOMIC_PROMOTION_ORDERING = RESOLVED_BY_BLUE
SIZE_RISK_EXECUTION_ORDERING = RESOLVED_BY_BLUE
LEARNING_IDEMPOTENCE_CONTRACT = CORRECTION_SPECIFIED / NOT_IMPLEMENTED
FORWARD_ECONOMIC_MODULE_RECONCILIATION = PASS_FOR_PLANNING
E2E_FALSE_POSITIVE_MATRIX = EXPANDED / NOT_IMPLEMENTED
UNRESOLVED_BLUE_SEMANTIC_DECISIONS = 0
```

`VERTICAL_LOOP_BUILD_SPEC = NOT_FROZEN`

The remaining non-code prerequisite before freeze is the exact scientific
Research -> frozen EffectEstimate producer/output contract.

After that contract is closed, Blue should issue one consolidated large Builder mission
rather than several small implementation missions.

## 12. Final routing

Current Product/Economic route:

```text
challenge
  -> Blue consolidated correction spec              [THIS DOCUMENT]
  -> close Research -> frozen EffectEstimate contract
  -> freeze final vertical build specification
  -> ONE LARGE BOUNDED BUILD
  -> targeted adversarial reception
  -> repeated shadow evidence
```

Do not dispatch implementation before the scientific output contract is closed.


## 13. SCIENTIFIC CLOSURE RECEPTION / CONSOLIDATED BUILD DISPOSITION — latest, 2026-09-21

This section is the sole current first-vertical build disposition. Sections 3–10
remain required. The estimator contract and decision table are maintained in the
existing authority, not a competing specification:

`governance/BLUE_RESEARCH_FROZEN_EFFECT_ESTIMATE_PRESTAGE_2026-09-21.md` §§9–12.

```
SCIENCE_SPEC_STATE = PARTIALLY_CLOSED / BLOCKED_S11_DEPENDENCE_INTERVAL
VERTICAL_LOOP_BUILD_SPEC = NOT_FROZEN / ONLY_S11_OPEN
PRODUCT_IMPLEMENTATION_AUTHORIZED = FALSE
PRODUCT_INTEGRATION = PAUSED
DEPLOYMENT_AUTHORIZED = FALSE
ONE_BIG_BUILD = DEFAULT_AFTER_S11_CLOSURE / NOT_DISPATCHED
INDEPENDENT_REVIEW_REQUIRED = ONE_BOUNDED_S11_CHALLENGE_PREPARED; IMPLEMENTATION_REVIEW_AFTER_DELIVERY
```

Blue closed population, formation/entry, allocation identity/timing, return/action/
terminal rules, denominator checks, data-use/trial/evidence authority and output mapping.
O4 observation semantics are closed; inferential dependence/interval authority is not.
The draft connected-component bootstrap can supply at most four components in the
252-session cohort while requiring 30. That method is rejected. Declaring all real
results insufficient by this impossible guard is not coherent scientific closure.
The exact bounded next action is §12 of the science authority. This disposition grants
no right to weaken existing admission checks merely to demonstrate a fill.

### 13.1 Two execution-cost checks — precise shared contract

**Before sizing**, bind actual `ExecutionModel` type/version/config and the exact
price/volume/ADV inputs and cutoff, order side, reference price, execution phase,
participation denominator, units, and cost inventory. The Research/Economic comparison
must use compatible price units and per-leg reference-notional units, not just a higher
scalar cost. `1 bp = 0.0001` of the declared notional. Declare entry and exit separately;
round-trip cost is the sum of leg currency costs divided by the original allocated
notional, not blindly twice a one-way coefficient when exit notional differs.

The pinned Desk model has `s(p)=half_spread_bps + impact_bps_at_full_participation *
sqrt(min(p,1)/max_participation)`, fill price `P*(1+side*s/10000)`, and commission
`abs(q)*fill_price*commission_bps/10000`. Thus exact per-leg shortfall on reference
notional includes the commission cross-term:
`cost_bps = s + commission_bps*(1+side*s/10000)`.
The existing Economic consistency helper's additive bps comparison is useful but
not sufficient for this exact check. Reuse its model extraction; add a pure comparison
against the actual fill formula without calling fill to simulate an admission.
Reject invalid coefficients, nonpositive ADV/capacity, stale/unavailable units, unknown
execution phase or uncovered components. Missing ADV must not exploit the current
fill function's zero-participation fallback.

Compare a declared Research/Economic execution-assumption envelope against that exact
cost model over its full allowed participation range, including both sides and reference
bases. A component present only on one side requires a governed unit/applicability
mapping, not implicit zero. Cover commissions/fees, spread, impact/slippage, financing,
borrow and other applicable losses. Long-only unlevered policy may justify no borrow
or financing liability, but zeros require explicit applicability evidence. The SPY leg
is a scientific comparator, not an assumed executed hedge incurring fictional fees.
The current assumed Desk coefficients retain assumed provenance; compatibility does
not make the MEUE recipe calibrated or `RECIPE_CONSUMABLE`.

`T_j` stays gross. Expected costs enter `K_forward`; adverse parameter/model uncertainty
enters `M_economic` under the existing partition. Research's old net portfolio-cost
charge is not subtracted again from T_j. Actual Book costs arise once through fills or
separately identified applicable ledger charges. A cost class cannot be both charged
in fill price and again as a duplicate cash debit. Larger assumptions alone do not
establish compatibility, and conservatism is not silently loaded into expected cost.

**After sizing and before fill**, compute implied participation from the actual final
quantity/reference notional and the same authorized ADV basis, on each proposed leg.
Validate the participation/cost envelope again after rounding, execution-price updates,
capacity truncation or any transformation that changes the order. Persist both check
artifacts with the AssessmentRecord/OpportunityTicket. Risk scaling down cannot increase
participation only while the same prices/ADV apply; changed inputs require recheck.
Failure yields `NO_TRADE / EXECUTION_COST_CONSISTENCY_EXCEEDED_AFTER_SIZING` (or the
precise missing-input reason) before `ExecutionModel.fill` and before Book mutation.
A pure order preview may validate inputs but is not a second fill authority.

### 13.2 Exact integration consequences retained for one build

- Initial Economic assessment precedes `VALIDATED -> SHADOW` and Desk actionable
  selection. Persist AssessmentRecord and StrategyRegistry transition with linked
  identities and restart recovery. CONTINUE alone does not confer order eligibility.
- Size remains `min(MarginSizingRule(NAV*strategy_allocation, economic_margin),
  NAV*strategy_allocation*definition.capital_fraction)`. The science constructor is
  reference-policy evidence, not a parallel SIZE engine. Verify policy applicability
  and EC1 weight homogeneity; changed support/relative weights require a new policy
  version and cannot silently inherit the reference estimate.
- Risk remains independent downstream veto/throttle. A Risk rejection persists a
  refusal/lesson. No scientific pass overrides portfolio context or missing beta
  attribution. SPY excess alone is not proof of factor-adjusted alpha.
- `ExecutionModel.fill` remains the sole shadow-fill authority. The science holding
  convention requires explicit scheduled close support for the twentieth session;
  the pinned implementation only reads an opening price. The future single build must
  extend that function's explicit execution-phase contract, preserve open defaults,
  and test exact entry/exit references. It must not substitute next-open returns.
- Entry and scheduled exit use separate deterministic OpportunityTicket IDs linked to
  one position lifecycle, retaining one-fill-per-symbol-per-opportunity semantics.
  This permits the required round trip without general partial-fill continuations.
  Corporate-action entitlements/cash must enter the existing authoritative Book as
  idempotent action records, never a second ledger or fabricated trade fill.
- Forward confirmation identity is session/content-address scoped; consumption also
  follows shared source atoms/ancestry. Durable Learning processed IDs and payload
  digests survive the last-200 display window and reject conflicting replay.
- Preserve the single chain `ForwardObservation -> ResearchTicket -> AssessmentRecord
  -> OpportunityTicket -> DeskJournal -> Ledger -> LearningStore`. All refused,
  unmatured, incomplete and economically negative outcomes retain reasons and next
  actions. The existing Clock wakes only on new data, due outcomes or resolved blockers;
  it does not repeatedly spend the same cohort's inferential look.

### 13.3 Prepared implementation shape — not permission

One intended implementation owner: **one primary Product Builder**, on
`builder/post-p0-first-vertical-shadow-loop-2026-09-21`, only after explicit Blue
freeze and dispatch. This branch is not created by this mission. No separate estimator
implementation precursor is justified: estimator code, typed output, promotion and
vertical integration can be built together once S11 is resolved. Independent method
specification is needed first; profitable alpha is not.

Internal verifiable milestones for that eventual mission:

1. **Scientific artifact:** assembler with S01–S17, interval method as finally accepted,
   D19 refusals, real lineage/commitment checks and deterministic arithmetic fixtures.
2. **Research/Economic boundary:** typed ticket persistence, exact coordinate/recipe
   binding, use/trial ledger, session evidence identity, durable initial admission.
3. **Desk/Book boundary:** sole Economic size with lifecycle cap, policy transport,
   independent Risk, both exact cost checks, sole fill authority with entry/exit phases,
   existing Book action/position accounting and recovery.
4. **Learning/Clock closure:** bounded display plus durable idempotence; full correction
   §10 restart/conflict/negative matrix and scientific falsifiers; one final handoff
   with exact commit, actual tests and a real-data capability report. Synthetic positive
   cases are explicitly labeled and never presented as market-edge evidence.

These are checkpoints inside ONE BIG BUILD, not four Builder dispatches. The final
handoff must identify unavailable real inputs and resulting NO_TRADE states without
manufacturing a positive estimate. Subsequent independent review is bounded to the
scientific and integration contracts and the frozen delivery; Blue receives it before
any later integration/deployment decision. No whole Forward/Economic branch merge is
implied. No target-host, qualifying P0, data-unsealing or capital permission is granted.

```
ECONOMIC_PROGRESS = Precise producer and Product integration decisions are preserved; the impossible interval candidate was rejected before it could become production authority.
REMAINING_BLOCKER = S11: scientifically justified issuer/calendar dependence and interval contract for the bounded first-slice cohort.
EXIT_CONDITION = One bounded methods delivery resolves S11 or proves the exact insufficiency; Blue then makes the freeze decision without reopening settled architecture.
```
