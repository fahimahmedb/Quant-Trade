# CLAUDE — POST-P0 VERTICAL ADVERSARIAL CHALLENGE — 2026-09-21

## 0. Role and disposition

`READ_ONLY_ADVERSARIAL_ANALYSIS + FALSIFICATION_PLAN + BIG_BUILD_PRECONDITIONS`.

No file under `src/`, `tests/`, `scripts/`, schemas, or workflows was modified. No
Forward/Economic leaf was merged or cherry-picked. This document is the only write.

```text
PRODUCT_CODE_MODIFIED = FALSE
PRODUCT_INTEGRATION = PAUSED
P0_RUNTIME_MUTATION = FALSE
TARGET_HOST_TOUCHED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
t0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
```

## 1. Authorities read, exact SHAs re-verified

- `QUANT_NORTH_STAR.md`, `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`,
  `handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`.
- `handoff/CLAUDE_POST_P0_VERTICAL_BUILD_PREP_2026-09-21.md` (@ branch
  `parallel/claude-post-p0-vertical-build-prep-2026-09-21`) — the primary object
  challenged.
- `handoff/BLUE_CLAUDE_POST_P0_VERTICAL_BUILD_PREP_RECEPTION_2026-09-21.md`.
- `handoff/BUILDER_POST_P0_VERTICAL_INTERFACE_MAP_2026-09-21.md` @
  `8d40af1f2333474d8f26509b61cb257d96f8772d`.
- `handoff/ANTIGRAVITY_POST_P0_VERTICAL_SHADOW_LOOP_DESIGN_2026-09-21.md` @
  `568eea1e028302e14f96a06eb2515bb89aa73ad4`.
- Canonical Forward @ `83521dbfdd90027c90d04adfb7d814593c2355c5`: read in full
  `forward_recorder.py`, `forward_admissibility.py`, `admissibility.py` (signatures).
- Canonical Economic @ `35dff27b8fac53618da434ee6d31febbddcc0e69`: read in full
  `decision.py`, `coordinate.py`, `states.py`, `recipe.py`, `journal.py`,
  `sizing.py`, `capacity.py`, `consistency.py`.
- Blue Product spine (current tree, descends from `cbf30c1b...`): read in full
  `src/quant/factory/workers.py`, `src/quant/factory/strategies.py`,
  `src/quant/desk/desk.py` (SCAN→BOOK), `src/quant/book/ledger.py`,
  `src/quant/learning/store.py` (record_research).

I did not re-derive every line the three prior handoffs already re-derived from
exact code (build-prep and the interface map are both independently careful and
mostly agree with each other on file inventory and D1–D5 mechanics). Where they
already found a conflict correctly, I do not repeat their derivation; I only
re-verify the specific claims that gate whether the vertical slice can actually
work, and I go one layer deeper than either prior document went on four points
(§3.1, §3.4, §3.6, §5.3 below), each traced to an exact line of code neither
prior document quotes.

## 2. Headline finding: the D2/D3 composition is not merely "not yet wired" — as specified it cannot produce a nonzero Path B size

**Classification: REAL_DEFECT.**

`src/quant/factory/strategies.py:65-73`:

```python
@property
def tradable(self) -> bool:
    return self.lifecycle in TRADABLE          # TRADABLE = {"SHADOW":.., "ACTIVE_SHADOW":.., "DECAYING":..}

@property
def capital_fraction(self) -> float:
    if self.tradable:
        return TRADABLE[self.lifecycle]
    return EVALUATION_FRACTION if self.evaluation_track else 0.0
```

`workers.py:_finish` only sets `evaluation_track = True` on the **rejected**
branch (`else: definition.evaluation_track = True`, `workers.py:246`); a
`VALIDATED` strategy that passed research is left with `evaluation_track =
False`. Once Patch 1 (delete the `transition("SHADOW", ...)` call at
`workers.py:243`) is applied — which D3 correctly requires — a strategy sitting
at `VALIDATED` therefore has `capital_fraction == 0.0` by construction, until
something later calls `.transition("SHADOW", ...)`.

`desk.py:190` (the exact line Patch 4 in the build-prep is written to replace)
reads:

```python
capital = decision_ledger.nav_at(decision_prices) * definition.capital_fraction * self.strategy_allocation
```

D2 is `FINAL_SIZE = min(ECONOMIC_MARGIN_SIZE, DESK_LIFECYCLE_CAP)` where
`DESK_LIFECYCLE_CAP = capital * definition.capital_fraction` (build-prep §7,
Patch 3 docstring). The build-prep's own Path B acceptance test (§8) requires,
verbatim: *"Assert: `StrategyDefinition.transition` to `SHADOW` happened exactly
once, driven by the Economic verdict (not by `workers.py`), and only after
`_run_strategy`, not before."* That is a correct requirement in isolation — a
strategy must not become tradable before the fill it is being promoted for has
actually happened, otherwise SHADOW is granted on a verdict that Risk or
capacity-truncation could still veto. But it is incompatible with reading
`definition.capital_fraction` **during** `_run_strategy`'s SIZE step to compute
`DESK_LIFECYCLE_CAP`: at that point in the same call, by the test's own ordering
requirement, `definition.lifecycle` is still `VALIDATED` and
`evaluation_track` is `False`, so `capital_fraction == 0.0`, so
`DESK_LIFECYCLE_CAP == 0.0`, so `FINAL_SIZE = min(economic_margin_size, 0.0) =
0.0` for every single lane, unconditionally, regardless of how positive the
economic verdict is.

**Failure mechanism, concretely:** run the build-prep's own Path B fixture
exactly as specified in §8. `economic_gate` returns `CONTINUE` with
`margin_of_safety > 0`; `size_lane(...)` returns a `SizingPlan` with
`gross_notional > 0`. `econ_bridge.economic_size(...)` then multiplies that by
`min(1, capital_fraction)` — and `capital_fraction` is `0.0` — so
`SizingPlan.gross_notional` after the D2 composition is `0.0`. `_execute` then
skips every leg as below `MIN_ORDER_NOTIONAL` (the exact code path Path C.1 is
supposed to exercise as a **separate, deliberately-zero-margin** negative
control). Path B, the "positive-size SHADOW" path, degenerates into Path C.1 —
it cannot be told apart from a genuine zero-margin NO_TRADE by the very
assertions the spec proposes (`economic_margin_size > 0` still holds, but
`SizingPlan.gross_notional` after D2 composition is `0`, `ExecutionModel.fill`
is never called, `Ledger.apply_fill` never mutates). The acceptance test as
written would either fail outright (if it asserts `state.fills == 1`) or, worse,
silently pass a degenerate assertion set if a future Builder loosens the
"exactly one fill" assertion to make the suite green — turning the one test that
is supposed to prove the system can ever put on a shadow position into a test
that only proves NO_TRADE, permanently.

**Consequence:** as specified, D2+D3 jointly compose to a strategy that can
*never* reach a nonzero shadow fill through this path, because the one
lifecycle-cap source of truth (`capital_fraction`) is tied to a lifecycle state
(`SHADOW`) that policy correctly forbids granting until after the fill it would
cap. Neither the build-prep, the interface map, nor the Antigravity design
notices this — all three describe the transition-timing rule and the
capital-fraction-as-cap rule as if they were independent decisions; they are not
independent, they are circularly dependent through one property.

**Smallest correction (does not reopen D2 or D3):** the lifecycle cap must not
be read from the *current* `capital_fraction` at SIZE time. Two options, both
minimal:

1. Freeze the cap fraction that `VALIDATED → SHADOW` *would* award
   (`TRADABLE["SHADOW"]`, i.e. `0.35`) as the desk-lifecycle-cap constant used
   in the D2 `min(...)` for a strategy that is `VALIDATED` and has just received
   an economic `CONTINUE`, and only actually call `.transition("SHADOW", ...)`
   once the fill has durably occurred (Book-side, after `_apply`). This
   preserves "not tradable-in-lifecycle-history until Economics approves and the
   fill occurs" while giving SIZE a real, positive cap number to compose
   against.
2. Transition to `SHADOW` immediately upon `economic_gate` returning
   `CONTINUE` (before SIZE, not after `_run_strategy`), accepting that a
   strategy can carry the `SHADOW` lifecycle label for a session in which Risk
   or capacity-truncation subsequently reduces its fill to zero. This is
   internally consistent (capital_fraction is nonzero when SIZE reads it) but
   contradicts the Path B assertion ordering as literally written in the
   build-prep, so that assertion must be corrected to "transitioned before
   `_execute`, not before `economic_gate` returns `CONTINUE`."

Either is a small, bounded fix; both are cheaper than discovering this during
the Builder mission after `_execute` unexpectedly returns zero fills on every
positive fixture. **This is scope-changing**: the Builder mission text (build-prep
§10) must be corrected before Gate C, because as written it directs the Builder
to implement Patch 4 exactly as drafted, which cannot pass its own Path B test.

## 3. Science → EffectEstimate: the coordinate-identity gate exists and is never wired to the bridge

**Classification: SCIENTIFIC_CONTRACT_GAP** (S1/S2).

`src/quant/economics/coordinate.py` (Economic branch) is a complete,
already-authored answer to exactly the question S1/S2 ask: `DeltaCoordinateBinding`
declares `security`/`benchmark` return conventions, `benchmark_symbol`,
`aggregation`, `allocation_constructor_id`, `allocation_weight_precedes_outcome`;
`evaluate_delta_coordinate` refuses `ALLOCATION_WEIGHTED_RATIO` unless every
one of those is declared and mutually consistent, and explicitly rejects five
named substitute aggregations (`UNWEIGHTED_EVENT_MEAN`,
`REALISED_PORTFOLIO_RETURN`, `NET_OF_FRICTION_RETURN`, `EXPECTED_SAMPLE_RATIO`,
`PROGRAM_ROI`) by name (`coordinate.py:35-41`). This is real, working
machinery, not a placeholder.

But `EffectEstimate` (`decision.py:57-97`) does **not** carry a
`DeltaCoordinateBinding` and does not call `evaluate_delta_coordinate`.
`EffectEstimate.violations()` checks only that `estimator_form ==
ALLOCATION_WEIGHTED_RATIO` **as a string**
(`decision.py:87-88`) — a literal equality check against a frozen constant, with
no verification that the number in `delta_hat` was actually produced by that
aggregation. The only place `evaluate_delta_coordinate` is actually invoked is
inside `MEUERecipe.structural_violations()` (`recipe.py:83-105`), which checks
the coordinate binding used to define the **threshold** (`MEUEResult.meue`,
the `M_economic`/`BEEE` side), not the coordinate the **point estimate**
(`EffectEstimate.delta_hat`) was computed on. `economic_gate` (`decision.py:217`)
takes `estimate: EffectEstimate` and `meue_result: MEUEResult` as two
independently-constructed arguments; nothing cross-checks that whatever
`DeltaCoordinateBinding` gated the recipe that produced `meue_result` is the
same binding — or any binding at all — behind the number in `estimate.delta_hat`.

**Concrete failure mechanism (S2's exact attack):** a Research estimator that
computes an ordinary average trade return, or a strategy-level realised return,
or a naive regression coefficient, can populate
`ResearchTicket.validation_result["frozen_effect_estimate"]["estimator_form"]`
with the literal string `"E[sum_j a_j T_j] / E[sum_j a_j]"`
(`coordinate.ALLOCATION_WEIGHTED_RATIO`'s value) without having computed
anything of the kind, and the fail-closed bridge in build-prep §5.2
(`form_effect_estimate`) would accept it: it only calls
`EffectEstimate.violations()`, which passes. The economic gate then runs on a
scientifically mislabeled coordinate and produces a mechanically correct-looking
`CONTINUE`/`KILL` that means nothing, because delta_hat and meue are not
provably on the same axis. This is exactly the failure S3/S4 also name (mixed
coordinates for point estimate vs. interval vs. threshold) — here I can point at
the exact reason no runtime check would catch it: the enforcement mechanism
(`evaluate_delta_coordinate`) exists but is wired to the wrong operand.

**Minimal correction, does not reopen D1/D3:** either (a) the
Research→Economic bridge must construct and validate a `DeltaCoordinateBinding`
for the *estimator that produced delta_hat* and require
`evaluate_delta_coordinate(...).compatible` before constructing `EffectEstimate`
at all (fail closed with a new, explicit reason if the binding is
unresolved/mismatched — do not overload
`EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE` for this, since that already
means "no `frozen_effect_estimate` at all", a different failure), or (b) the
`frozen_effect_estimate` block Research is required to populate must itself
embed a `DeltaCoordinateBinding` alongside `delta_hat`/`lower`/`upper`, and the
bridge must check it. Neither the build-prep, the interface map, nor the
Antigravity design proposes either of these; all three describe
`estimator_form == ALLOCATION_WEIGHTED_RATIO` as if the string check were the
whole verification.

## 4. PIT / forward laundering vector: whole-ledger fingerprint used as per-session "version" identity

**Classification: REAL_DEFECT** (P4/P5/P8, exact code).

`forward_admissibility.forward_dataset_view` (`forward_admissibility.py:38-62`)
builds `version = f"{dataset_id}@{dataset['fingerprint'] or 'EMPTY_LEDGER'}"`
where `dataset['fingerprint']` is `recorder.ledger_fingerprint()`
(`forward_recorder.py:426-439`) — an order-independent hash over **every
accepted observation in the whole recorder**, explicitly documented as
"Changes whenever the accepted set changes." `evaluate_forward_confirmation`
(`forward_admissibility.py:65-93`) uses this same whole-ledger `version` both
to build the `EvidenceUse` record and to check
`ledger.uses_of(version) & CONSUMING_USES` for the
"already spent on fit/validation" anti-laundering guard
(`FORWARD_CONFIRMATION_VERSION_ALREADY_CONSUMED`).

**Concrete failure mechanism:** the forward ledger is explicitly designed to be
continuously appended to (capture is a repeated one-shot process,
`forward_capture.py`). Suppose session `S` for symbol `X` is used for
`EXPLORATORY_FIT` at ledger state `F1` — recorded under `version =
"D@F1"` in the `UseLedger`. Later, any new observation for **any other symbol or
session** is captured and accepted, changing `ledger_fingerprint()` to `F2`.
When `evaluate_forward_confirmation` is subsequently run for the *same* session
`S`/symbol `X` (whose own content has not changed at all), it computes
`version = "D@F2"`, which the `UseLedger` has never seen consumed —
`ledger.uses_of("D@F2")` returns nothing, the anti-laundering check silently
does not fire, and the identical session/symbol evidence that was already spent
on fit can pass as `FORWARD_CONFIRMATION`. This is precisely the shortcut P4
asks to rule out ("does anything automatically infer `FORWARD_CONFIRMATION`?
It must not… challenge every possible shortcut"), and it is reachable purely by
the ledger's own intended, unrelated forward growth — no adversarial input is
required, just normal operation over time.

A second, related defect in the same function: `recorded_from` in
`forward_dataset_view` is `recorder.earliest_recorded_at()`
(`forward_recorder.py:441-452`) — the **minimum** `recorded_at` across the
*entire* ledger, not the session being evaluated. As the ledger ages, this value
keeps reporting the timestamp of the very first observation the recorder ever
accepted (for whatever symbol/session that happened to be), regardless of when
the specific session under evaluation was actually recorded. If
`evaluate_admissibility`'s timing check compares `protocol_freeze_instant`
against `recorded_from` (as the module docstring literally says it should:
*"this is what the admissibility's forward-confirmation rule should compare a
protocol freeze against"*), a session recorded **after** a freeze can still pass
the "existed before the freeze" check, because some unrelated, older session in
the same ledger did. This is a second, independent lookahead-laundering vector
riding on the same "whole ledger, not the one session" granularity mistake.

**Minimal correction:** both `version` and `recorded_from` in
`forward_dataset_view`/`evaluate_forward_confirmation` must be scoped to the
exact `session_date` (and ideally the exact `content_address` set) actually
being confirmed — `session_seal(session_date)` already exists and is already
session-scoped (`forward_recorder.py:380-392`); it is passed to
`evaluate_admissibility` as `forward_seal` but is *not* what is used for the
`version` string or the freeze-timing comparison. Building `version` and
`recorded_from` from `session_seal`/per-session recorded_at instead of
whole-ledger aggregates closes both vectors without touching
`admissibility.py`'s own rules, which is exactly the "layer on top, don't edit
the frozen primitive" approach the module's own docstring commits to. This
belongs in the exact same file the vertical slice is meant to reuse
`REUSE_AS_IS`; the interface map's `REUSE_AS_IS` classification for
`forward_admissibility.py` (interface map §2) should be downgraded to
`ADAPT` pending this fix, or the vertical slice's Path B fixture must construct
its own `ForwardRecorder` containing *only* the one session under test (which
sidesteps the bug for the fixture, per the mission's own S11 warning, but does
not fix production behavior once real continuous capture is running).

## 5. Research/execution cost-consistency wiring is circular as specified

**Classification: MISSING_PROOF / INTEGRATION_CONFLICT** (E3/E5/X3, Z7).

`ResearchExecutionConsistency.participation_used` (`consistency.py:90-97`) is a
caller-supplied float; `verify_research_cost_consistency` does not derive it
from anything. The build-prep's own Patch 4 (§7) calls
`economic_gate(estimate, meue_result, theta, interaction, capacity,
consistency)` — i.e. `consistency` must already exist as an input to the gate
that produces the `CONTINUE` verdict SIZE is computed *from*. But the actual
participation a lane will use is a function of the sized notional relative to
ADV, and SIZE (`size_lane`/`economic_size`) runs strictly *after*
`economic_gate` returns `CONTINUE` in the same patch (§7, Patch 4). There is no
proposed value for `participation_used` anywhere in build-prep §5.2/§5.3/§7
except the test fixture's own comment, "`participation_used=<value implied by
the fixture's fixed order size>`" (§8) — which begs the question by hand-picking
a number to match a size that has not been computed yet at the point the
consistency check runs.

Concretely, this leaves two live possibilities neither prep doc distinguishes:
(a) `participation_used` is meant to be `theta`'s *permitted*/assumed
participation ceiling (a modelling input, independent of the eventual sized
order), in which case the consistency check only proves the *model* is
internally coherent and says nothing about the order the gate's own `CONTINUE`
verdict is about to authorize sizing for — Z7's exact attack ("if Risk scales
target size down, does that invalidate the original Economic assumptions?")
applies in the other direction too: nothing re-verifies
`ResearchExecutionConsistency` against the *actual* `SizingPlan.gross_notional`
once it exists, so a lane can pass consistency at an assumed participation and
then size to a notional that implies a materially higher one, with no second
consistency check anywhere in the proposed patch plan; or (b) `participation_used`
is meant to be derived from the sized order, in which case the dependency order
in Patch 4 is backwards and `economic_gate` cannot run before SIZE, which
contradicts D2's own stated chain (economic verdict → then size).

**Minimal correction:** state explicitly which of (a)/(b) is intended, and if
(a), add one more required assertion to Path B and one more required negative
control to Path C: after `economic_size` produces the final `SizingPlan`,
re-derive the implied participation from `SizingPlan.gross_notional` and the
same `CapacityLimit.adv_notional` capacity already supplies, and assert it does
not exceed `ResearchExecutionConsistency.ceiling`; if it does, the lane must be
re-routed to `NO_TRADE` post-sizing (a fail-closed check that does not exist
anywhere in the current chain) rather than allowed to fill on an order whose
real participation was never checked against the research cost assumption.

## 6. Confirmed findings that reproduce or sharpen the prior handoffs (no new re-derivation needed beyond what is stated)

| # | Item | Classification | Note |
|---|---|---|---|
| F1 | D3 auto-promotion (`workers.py:241-244`) | REAL_DEFECT, already found by build-prep | Confirmed by direct read; `transition()` is the *only* setter of `self.lifecycle` (`strategies.py:75-80`) and `workers.py:243` is the only call site anywhere in `src/` that names `"SHADOW"` as a transition target (repo-wide grep). R2/R3 therefore reduce to exactly the one patch already proposed — there is no second live auto-promotion path today. |
| F2 | Two independent SIZE authorities (Blue lifecycle-fraction vs. Economic margin) | ECONOMIC_SEMANTIC_CONFLICT, already found (interface map C5) | Confirmed at `desk.py:190`, the exact line D2 must replace. See §2 above for why the replacement as specified is not sufficient by itself. |
| F3 | Two independent execution-cost/opening models (`OpeningExecutionModel` vs. `ExecutionModel.fill`) | INTEGRATION_CONFLICT, already found (interface map C6) | Confirmed `consistency.py:from_execution_model` reads only `commission_bps`/`half_spread_bps`/`impact_bps_at_full_participation`/`max_participation` off *whichever* model object is passed; nothing prevents a future caller from passing `OpeningExecutionModel`'s numbers instead of the real `desk.execution.ExecutionModel`'s, silently defeating ECON-001's guard. The Builder mission must name `desk.execution.ExecutionModel` as the only legal argument, not just "the execution model." |
| F4 | Two independent capacity layers (economic `apply_capacity` on modelled exposure vs. `ExecutionModel.fill` truncation on the real order) | ACCEPTABLE_FAIL_CLOSED, already found (interface map C7) | Confirmed both fail closed independently (`capacity.py` treats an absent `CapacityLimit` as zero, never unlimited; `Risk.verify_final` reruns on the *executed* portfolio per `desk.py:243-252`). Order is sound provided the economic layer's `CapacityOutcome` never itself increases the ceiling execution-side capacity would otherwise apply — nothing in the read code violates that, so this is a genuine non-issue given current code, contingent on F5. |
| F5 | Learning idempotence keys (`record_research`, and the proposed `record_economic_outcome` modelled on it) truncate persisted history to the last 200 entries | REAL_DEFECT, not previously found | `learning/store.py:save()`: `"lessons": self.lessons[-200:]`. The in-process idempotence check (`record_research`/proposed `record_economic_outcome`) scans `self.lessons`, but a fresh process reloads only the last 200 persisted entries (`__init__`: `self.lessons = payload.get("lessons", [])`). Once total lessons exceed 200 across the system's life, a restart followed by replay of an old ticket/opportunity whose lesson has aged out of the window produces a **duplicate** lesson entry — L4's exact failure mode ("replay must not create duplicate Learning records"), reachable in ordinary long-running operation, not just adversarially. This affects the *existing* `record_research` today, independent of the vertical slice, and the build-prep's proposed `record_economic_outcome` (§7 Patch 5) explicitly copies the same pattern, so it inherits the same defect. Minimal correction: key idempotence off a separately-persisted, unbounded id set (or `EconomicAssessmentJournal`/`DeskJournal`, which already are unbounded and already durable) rather than off a truncated display list; do not fix by simply removing the `[-200:]` slice, since that is presumably there to bound `LearningStore`'s on-disk size and an unbounded `lessons` list is its own future problem — the id-set and the display list are different data structures and should be split. |
| F6 | `Ledger.apply_fill` operation id (`f"{opportunity_id}:{fill['symbol']}"`) collapses a *second, legitimately distinct* fill under the same opportunity+symbol (e.g., a capacity-truncated fill later completed by a follow-up order) into a no-op replay | TEST_GAP | Not exercised by the vertical slice (which asserts exactly one fill per symbol per opportunity), and not a defect for that slice. It is a real gap the moment X4 (partial fills / capacity truncation continuation) is in scope, since `has_applied` cannot distinguish "already recorded, identical event" from "already recorded, this is actually a different, later, legitimate event for the same key." Record as a named future E2E case (§8 below), not a blocker for Gate C. |

## 7. Document-level conflict between the two design handoffs

**Classification: INTEGRATION_CONFLICT**, Blue must pick one authority.

The Antigravity design (`ANTIGRAVITY_POST_P0_VERTICAL_SHADOW_LOOP_DESIGN_2026-09-21.md`)
and the Claude build-prep disagree on two concrete points that the interface map
does not mention because it predates both:

1. Antigravity §3/D1: *"`delta_hat` (mean per-trade return)"* — this is exactly
   one of the rejected aggregations `coordinate.py` names by law
   (`UNWEIGHTED_EVENT_MEAN`, `coordinate.py:36`). Antigravity's own description
   of the bridge would fail `evaluate_delta_coordinate` were that check wired up
   (per §3 above, it currently is not). Build-prep is the more careful of the
   two documents here — it correctly refuses to invent a mapping from existing
   `net_return`/`t_statistic` metrics and states plainly that no such mapping
   exists (build-prep §5.2). Antigravity's parenthetical is not authoritative
   and must not be read as an approved definition of `delta_hat`.
2. Antigravity §3/D5 proposes `operation_id = hash(opportunity_id + strategy_id
   + session_date)`; build-prep §5.4 keeps the existing, code-verified
   `f"{opportunity_id}:{fill['symbol']}"` (`desk.py:275`). These are two
   different id schemes for the same object. Build-prep's is the one that
   matches exact current code (`Ledger.apply_fill`'s existing contract, which
   the mission forbids changing); Antigravity's is a hypothetical replacement
   that was never checked against `desk.py`. Blue should explicitly mark
   Antigravity's operation-id proposal superseded, not merely silent, so a
   future Builder does not treat it as an alternative option.

Neither of these was a Blue-authorized decision point in either handoff; they
are simple factual disagreements where one document did the code archaeology and
the other did not. Recommend Blue formally note build-prep as authoritative over
Antigravity wherever the two conflict, rather than carrying both forward as
co-equal inputs into Gate C.

## 8. E2E false-positive matrix — status against the required list

Of the 20 cases in the adversarial mission's required matrix, the build-prep's
§8 test specification (Paths A/B/C) already covers 1, 2 (partially — see §3
above, the *coordinate* mismatch case is not covered, only the *presence*
mismatch case), 5, 6 (not explicitly split from 5, but structurally identical),
7, 8, 10 (blocked by §2's finding — cannot pass as specified), 11, 15, 16, 19,
20. Not covered by the current specification, and required before Gate C
authorizes the Builder:

- **Case 3** (invalid confidence interval → NO_TRADE): covered mechanically by
  `EffectEstimate.violations()`'s `POINT_ESTIMATE_OUTSIDE_ITS_OWN_INTERVAL` /
  `CONFIDENCE_LEVEL_OUT_OF_RANGE` checks, but no fixture in §8 exercises it.
  Add one.
- **Case 4** (unadmitted forward evidence → no FORWARD_CONFIRMATION): §8's Path
  B fixture *asserts* the fixture may call `evaluate_forward_confirmation` for
  real, but does not include a fixture where it is called and correctly
  refuses. Given §4's finding, this case should specifically include a
  ledger-growth scenario (append an unrelated observation between fit-use and
  confirmation-attempt) to prove the laundering vector in §4 either does not
  fire (if fixed first) or is caught (if the fix lands as a NO_TRADE fallback
  rather than a code-level guarantee).
- **Case 9** (capacity truncation → coherent reduced fill): not in §8 at all;
  `apply_capacity`/`ExecutionModel.fill` truncation are both individually
  tested per-module but not through this exact vertical chain.
- **Cases 12–14** (crash-recovery at each of the three named boundaries): §9 of
  build-prep *argues* idempotence rather than specifying a test that exercises
  it end-to-end through the actual `CapitalDesk`/`EconomicAssessmentJournal`
  pair (only Path A/B's "replay" assertions exist, which cover case 11/case-14-adjacent
  but not a genuine kill-and-restart at the `journal.begin`-before-`_apply`
  boundary specifically).
- **Cases 17–18** (same id, changed inputs/fill → conflict): `AssessmentConflict`
  (`journal.py`) already proves this at the assessment layer in the Economic
  branch's own existing test suite (not re-verified here, out of scope), but no
  fixture in build-prep §8 exercises it through the vertical slice's actual
  wiring (`assessment_id = f"{ticket.opportunity_id}:ECON"`).

None of these gaps blocks writing the Builder mission, but the Builder mission
text (build-prep §10, "Required tests") should name Cases 3/4/9/12-14/17-18
explicitly rather than only "the three paths ... including both paths'
replay-idempotence assertions," or a Builder implementing exactly what is
written will under-test relative to the mission's own §14.

## 9. Required summary matrix

```text
SCIENCE_EFFECT_ESTIMATE_CONTRACT = FAIL (coordinate-identity gate exists in code
    but is not wired to EffectEstimate; estimator_form is a self-declared string
    with no cross-check — §3)
PIT_PROVENANCE_CONTRACT = FAIL (whole-ledger fingerprint/earliest_recorded_at
    used as per-session version/timing proxy — real laundering and staleness
    vector on ordinary continuous operation — §4)
RESEARCH_STATE_MACHINE = PASS (single auto-promotion site confirmed, single
    proposed patch sufficient; version identity / rejection persistence already
    sound — §6/F1)
ECONOMIC_GATE = PASS_WITH_CONDITIONS (fails closed on every input class
    inspected; capital_order_eligibility correctly gates on recipe/evidence/
    clustering/consistency; condition: §5's circularity must be resolved before
    the consistency check can be trusted end-to-end)
SIZING_CAPACITY_RISK = FAIL (D2 composition as specified always yields
    FINAL_SIZE = 0 for a not-yet-SHADOW strategy under the transition-ordering
    rule the same spec requires — §2, headline finding)
EXECUTION_FRICTIONS = PASS_WITH_CONDITIONS (single fill authority confirmed;
    ECON-001 already guarded; condition: the guard's execution-model argument
    must be pinned to desk.execution.ExecutionModel by name, not "the execution
    model" — §6/F3)
BOOK_IDEMPOTENCE = PASS_WITH_CONDITIONS (Ledger.apply_fill is sound and
    idempotent for the vertical slice's exactly-one-fill shape; condition: the
    opportunity_id:symbol operation id does not extend safely to a later
    multi-fill/partial-completion case — §6/F6, named as a future test, not a
    Gate-C blocker)
LEARNING_FEEDBACK = FAIL (existing record_research idempotence silently breaks
    once total lessons exceed the 200-entry persisted window; the proposed
    record_economic_outcome explicitly inherits the same pattern — §6/F5)
RESTART_RECOVERY = PASS_WITH_CONDITIONS (EconomicAssessmentJournal and
    DeskJournal/Ledger are each independently idempotent and restart-safe by
    direct read; condition: no fixture in the current test spec actually drives
    a kill-and-restart through the assembled chain — §8)
FORWARD_ECONOMIC_MODULE_RECONCILIATION = PASS (vendoring plan is additive,
    file-scoped, and correctly avoids whole-leaf merge; the one open item —
    option (a) vs (b) in build-prep §7 — is a legitimate build-sequencing choice
    for Blue, not a defect)
BIG_BUILD_SCOPE = PASS_WITH_CONDITIONS (changed-path allowlist is minimal and
    justified; condition: the allowlist's Patch 4 diff must be corrected per §2
    before the Builder mission is issued, or the Builder will spend its own
    budget rediscovering §2 mid-implementation)
E2E_FALSE_POSITIVE_MATRIX = INCOMPLETE (12/20 required cases covered by the
    current test specification; six gaps named in §8, none individually large)
```

## 10. Final status

```text
VERTICAL_CHALLENGE = PASS_WITH_REQUIRED_PREBUILD_CORRECTIONS
```

## 11. PRE_BIG_BUILD_CORRECTION_SET

Ordered by blocking severity. Corrections 1–2 must land before the Builder
mission is issued at all (they falsify the mission's own acceptance test as
written); 3–6 should land in the same governance pass so the Builder mission
text does not need a second revision cycle.

1. **Fix the D2/D3 sizing circularity (§2).** Pick option 1 or 2 from §2 and
   rewrite build-prep §7 Patch 4 and §10's changed-path allowlist accordingly.
   This is the one correction that, left unfixed, makes the vertical slice
   structurally unable to demonstrate a positive fill under its own acceptance
   criteria.
2. **Wire `evaluate_delta_coordinate` into the Research→Economic bridge, or
   explicitly defer it with a named, dated follow-up mission (§3).** Do not
   ship a bridge that treats `estimator_form == ALLOCATION_WEIGHTED_RATIO` as a
   sufficient check; at minimum, require the `frozen_effect_estimate` block to
   carry a `DeltaCoordinateBinding` and fail closed
   (`DELTA_COORDINATE_MISMATCH`/`_UNRESOLVED`) with its own named reason,
   distinct from `EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE`.
3. **Scope `forward_dataset_view`'s `version`/`recorded_from` to the session
   under evaluation, not the whole ledger (§4).** This is a pre-existing defect
   in reused, `REUSE_AS_IS`-classified code, not new work the vertical slice
   introduces, but the vertical slice is exactly what will start exercising
   `evaluate_forward_confirmation` under continuous ledger growth for the first
   time, so it should not inherit the bug silently.
4. **State explicitly whether `ResearchExecutionConsistency.participation_used`
   is a pre-sizing model assumption or a post-sizing verification, and add the
   missing post-sizing re-check if it is the former (§5).**
5. **Correct the Antigravity design doc's `delta_hat` description and
   operation-id formula, or mark the whole document superseded by build-prep
   where they conflict (§7).**
6. **Expand the Builder mission's "Required tests" to name the six E2E cases
   listed in §8** rather than leaving them implicit in "the three paths."

None of these six corrections requires reopening D1–D5 as frozen Blue
decisions; all six are either implementation-order clarifications inside D1–D5,
or defects in already-existing, previously-reused code that the vertical slice
is the first work item to actually depend on.

## 12. Big-build freeze conditions — current state

```text
SCIENCE_EFFECT_ESTIMATE_CONTRACT = FAIL  (correction 2 required)
PIT_PROVENANCE_CONTRACT = FAIL  (correction 3 required)
ECONOMIC_AUTHORITY_ORDERING = FAIL  (correction 1 required — this is the D2/D3
    ordering the freeze condition names)
SIZE_RISK_EXECUTION_ORDERING = FAIL  (same root cause as above)
FORWARD_ECONOMIC_MODULE_RECONCILIATION = PASS
RESTART_IDEMPOTENCE_CONTRACT = PASS_WITH_CONDITIONS  (correction 6, test
    coverage only — the mechanisms themselves are sound)
E2E_FALSE_POSITIVE_MATRIX = INCOMPLETE
UNRESOLVED_BLUE_DECISIONS = 0  (no D1-D5 reopening; six bounded corrections only)
```

`VERTICAL_LOOP_BUILD_SPEC = FROZEN` is **not** recommended yet. Recommend Blue
route corrections 1–2 (and ideally 3–6) back through a short, bounded prep
revision — not a new full build-prep mission, since D1–D5 and the file
inventory both remain correct — before authorizing
`builder/post-p0-first-vertical-shadow-loop-2026-09-21`.

## 13. Safety state

```text
PRODUCT_CODE_MODIFIED = FALSE
PRODUCT_INTEGRATION = PAUSED
P0_RUNTIME_MUTATION = FALSE
TARGET_HOST_TOUCHED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
t0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
```

Control returns to Blue.
