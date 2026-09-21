# CLAUDE — POST-P0 VERTICAL ECONOMIC BUILD PREP — 2026-09-21

## 0. Status

`CLAUDE_VERTICAL_BUILD_PREP = READY_FOR_BLUE_REVIEW`

```text
PRODUCT_CODE_MODIFIED = FALSE
PRODUCT_INTEGRATION = PAUSED
P0_RUNTIME_MUTATION = FALSE
TARGET_HOST_TOUCHED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
t0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
```

Mission type executed: `READ_ONLY_ANALYSIS + PATCH_PLAN + TEST_SPEC + FUTURE_BUILDER_HANDOFF_ONLY`.
No file under `src/`, `tests/`, `scripts/`, `schemas/`, workflows or config was modified.
This document is the only write.

## 1. Mission / base / final SHA

- Repository: `fahimahmedb/quant-trade`
- Branch: `parallel/claude-post-p0-vertical-build-prep-2026-09-21`
- Mission base (verified ancestor of branch head): `c62f63219068373e759cb63c095d62084da584f3`
- Branch head at start of this session (verified via `git fetch --prune` + `git rev-parse`): `674971836b4b4e118877905a70540dc48e3f2749`
- This handoff commits on top of that head; no rebase, no force-push, no merge.

## 2. Exact source refs verified

All resolved by `git cat-file -t` / `git rev-parse` against `origin` after `git fetch origin --prune`; none required assumption from branch name alone.

| Authority | Ref | Resolved SHA | Status |
|---|---|---|---|
| Canonical Forward | `parallel/claude-forward-data-2026-09-20` | `83521dbfdd90027c90d04adfb7d814593c2355c5` | branch tip == pinned SHA |
| Canonical Economic | `parallel/claude-economic-v2-2026-09-20` | `35dff27b8fac53618da434ee6d31febbddcc0e69` | branch tip == pinned SHA |
| Blue Product spine | (detached) | `cbf30c1bb38dd69c11fb64c523c3aec694116b9c` | ancestor of mission HEAD |
| Interface map | `builder/post-p0-vertical-interface-map-2026-09-21` | `8d40af1f2333474d8f26509b61cb257d96f8772d` | branch tip == pinned SHA |
| Antigravity design | `parallel/antigravity-post-p0-vertical-shadow-loop-design-2026-09-21` | `568eea1e028302e14f96a06eb2515bb89aa73ad4` | branch tip == pinned SHA |
| Mission base | (governance) | `c62f63219068373e759cb63c095d62084da584f3` | ancestor of mission HEAD |

No pinned authority was unresolved. `BLOCKED_AUTHORITY_MISMATCH` does not apply.

`handoff/BUILDER_POST_P0_VERTICAL_INTERFACE_MAP_2026-09-21.md` and
`handoff/ANTIGRAVITY_POST_P0_VERTICAL_SHADOW_LOOP_DESIGN_2026-09-21.md` were read from
those exact pinned SHAs (not the moving branch tip, though they were identical at fetch
time). This handoff independently re-derived every contract below from the actual code
at the pinned SHAs rather than trusting either prior document's path/line claims; where
my own reading disagrees with the interface map I say so explicitly (Section 5, Section 7).

## 3. Exact inspected path inventory

### Blue Product spine (current branch tree, descends from `cbf30c1b`)

| Path | Classes / functions actually inspected |
|---|---|
| `src/autonomous_research/ticket.py` | `ResearchTicket`, `TRANSITIONS` |
| `src/quant/factory/workers.py` | `run_lane`, `_finish` (lines 217–261) |
| `src/quant/factory/evaluate.py` | `walk_forward`, `summarize`, `falsify` (unrelated `weights_fn` diff, see §7) |
| `src/quant/factory/strategies.py` | `StrategyDefinition`, `LIFECYCLE`, `TRANSITIONS`, `TRADABLE`, `.transition()` |
| `src/quant/desk/desk.py` | `CapitalDesk.__init__`, `run_session`, `_run_strategy`, `_apply`, `_resume`, `_finish`, `_execute` |
| `src/quant/desk/opportunity.py` | `OpportunityTicket`, `STAGES`, `TERMINAL` |
| `src/quant/desk/risk.py` | `RiskLimits`, `evaluate`, `verify_final` (signatures) |
| `src/quant/desk/execution.py` | `ExecutionModel.fill`, `.adv`, `RESEARCH_ONE_WAY_COST_BPS` |
| `src/quant/desk/journal.py` | `DeskJournal.begin`, `.commit`, `.pending_plan`, `.decision_snapshot`, `.begin_session` |
| `src/quant/book/ledger.py` | `Ledger.apply_fill`, `.has_applied`, `.from_document`, `.save` |
| `src/quant/learning/store.py` | `LearningStore.record_research`, `.save`, `BuildTask` |
| `src/quant/dataplane/panel.py` | `PricePanel.__init__`, `.FIELDS`, `.has`, `.adjusted` |

Confirmed **absent** from the Blue spine tree (verified by `git ls-tree`, not assumed):
`src/quant/economics/` (whole package), `src/quant/dataplane/forward_recorder.py`,
`forward_admissibility.py`, `forward_contracts.py`, `forward_capture.py`,
`forward_coverage.py`, `admissibility.py`, `src/quant/integration/` (whole package).
This is a structural fact the changed-path budget in §7 depends on.

### Canonical Forward (`83521dbf...`)

| Path | Classes / functions actually inspected |
|---|---|
| `src/quant/dataplane/forward_recorder.py` | `ForwardObservation` (fields, `violations`, `time_provenance`, `key`, `content_address`), `ForwardRecorder.record`, `.as_of`, `.session_seal`, `.coverage`, `.ledger_fingerprint`, `.earliest_recorded_at` |
| `src/quant/dataplane/forward_admissibility.py` | `forward_dataset_view`, `evaluate_forward_confirmation` (full file, 93 lines) |
| `src/quant/dataplane/forward_contracts.py` | class/def signatures only (`SourceProfile`, `admissible_for_forward_capture`) |

### Canonical Economic (`35dff27b...`)

| Path | Classes / functions actually inspected |
|---|---|
| `src/quant/economics/decision.py` | `EffectEstimate` (all fields + `violations`), `PortfolioInteraction`, `EconomicVerdict`, `economic_gate` (full 327-line file read) |
| `src/quant/economics/journal.py` | `compute_input_fingerprint`, `AssessmentRecord`, `AssessmentRecord.from_verdict`, `EconomicAssessmentJournal.record/get/replay`, `AssessmentConflict` |
| `src/quant/economics/sizing.py` | `MarginSizingRule.fraction`, `SleeveTarget`, `SizingPlan` (`transformed`, `finalise`, `final_state_hash`), `RiskApproval`, `verify_risk_approval`, `size_lane`, `combine_lanes` (full 207-line file read) |
| `src/quant/economics/capacity.py` | `CapacityLimit`, `CapacityOutcome`, `apply_capacity` (signatures) |
| `src/quant/economics/consistency.py` | `ExecutionCostModel`, `ResearchExecutionConsistency` (all properties + `violations`), `verify_research_cost_consistency` |
| `src/quant/economics/opening.py` | `OpeningExecutionModel.fill`, `.execution_loss_bps` (signatures) |
| `src/quant/economics/coordinate.py` | `DeltaCoordinateBinding`, `evaluate_delta_coordinate` (signatures) |
| `src/quant/factory/evaluate.py` | diff vs spine (confirmed unrelated to this mission, see §7) |

`src/quant/economics/journal.py` exists **only** on the Economic branch, not on Forward.
`forward_admissibility.py` / `forward_contracts.py` / `forward_capture.py` /
`forward_coverage.py` exist **only** on Forward, not on Economic. Each branch's
`economics/` directory is otherwise near-identical (both carry `decision.py`,
`sizing.py`, `capacity.py`, `consistency.py`, `opening.py`, `coordinate.py`, etc.);
this handoff treats the Economic branch (`35dff27b...`) as canonical for all of
`economics/`, per the assigned authority, and does not diff the two economics/ copies
line-by-line since neither task nor D1–D5 requires reconciling them.

## 4. D1–D5 compatibility confirmed against exact code

- **D1** (fail-closed bridge): Confirmed compatible. `EffectEstimate` (`decision.py:58`)
  is a closed, frozen-field dataclass — `delta_hat`, `lower`, `upper`,
  `confidence_level`, `evidence_label`, `sample_provenance`, `estimator_form`,
  `event_count`, `p_value`, `clustering_unit_provenance` — with no optional/derivable
  fallback path. `.violations()` already fails closed on missing/invalid values; no
  bridge code needs to duplicate that logic, only to refuse constructing the object
  when a Research-side field is genuinely absent (§5.2).
- **D2** (`FINAL_SIZE = min(ECONOMIC_MARGIN_SIZE, DESK_LIFECYCLE_CAP)`): Confirmed
  compatible and *not yet wired*. `economics/sizing.py:size_lane` computes
  `capital * rule.fraction(margin_of_safety)` from the **economic** margin of safety
  and a capital figure the caller supplies — it does not itself know about
  `StrategyDefinition.capital_fraction` (the desk lifecycle cap, `strategies.py:70`).
  Composing the two is exactly the missing glue in §5.3/§7.
- **D3** (no VALIDATED→SHADOW auto-promotion): **Confirmed contradiction, exact
  site found.** `src/quant/factory/workers.py:241-244`:
  ```python
  if verdict["passed"]:
      definition.transition("VALIDATED", "survived every declared falsification test")
      definition.transition("SHADOW", "evidence accepted; shadow track record required "
                                      "before full capital")
  ```
  This is a live, exercised auto-promotion inside the same `_finish` call — not a
  hypothetical. It is not a reason to reopen D3 (D3 is exactly the rule this violates);
  it is the minimum-diff patch site: delete the second `transition("SHADOW", ...)` call
  so a strategy stops at `VALIDATED` until an external Economic verdict promotes it
  (§7, patch 3). `StrategyDefinition.LIFECYCLE`/`TRANSITIONS` (`strategies.py:24-35`)
  already allow `VALIDATED -> SHADOW` as an explicit transition callable from outside
  `workers.py`, so no new lifecycle state is needed to represent
  "ELIGIBLE_FOR_ECONOMIC_ASSESSMENT" — a strategy sitting at `VALIDATED` already *is*
  that state; inventing a new enum value for it would violate the North Star's "a state
  enum is not a capability" invariant for no behavioural gain.
- **D4** (execution consistency): Confirmed compatible. `desk/execution.py` declares
  `RESEARCH_ONE_WAY_COST_BPS = 5.0` as the cost the Research Factory assumes;
  `economics/consistency.py:ExecutionCostModel.from_execution_model` explicitly exists
  to derive an `ExecutionCostModel` from a Blue `ExecutionModel` instance, and
  `verify_research_cost_consistency(research_one_way_cost_bps, model, participation_used)`
  is the exact call D4 requires. It is not currently invoked from `desk.py` or
  `workers.py` anywhere — genuinely missing glue, not a contradiction.
- **D5** (provenance chain): Confirmed compatible, with one wording correction against
  the governance doc. `governance/BLUE_CLAUDE_POST_P0_VERTICAL_BUILD_PREP_2026-09-21.md`
  §2/D5 states the chain as
  `ForwardObservation -> ResearchTicket -> EconomicAssessment -> OpportunityTicket -> DeskJournal -> Ledger -> LearningStore`.
  Exact code shows `EconomicAssessmentJournal`/`AssessmentRecord` is the persisted object
  (there is no class literally named `EconomicAssessment`); `OpportunityTicket` is the
  correct next hop as declared. No contradiction — just naming: the handoff below uses
  `AssessmentRecord` (economics/journal.py) as the concrete type behind "EconomicAssessment".

No `BLUE_DECISION_REQUIRED` is raised. The one exact-code contradiction found (D3) is
resolved by following D3, not by reopening it.

## 5. Final data-contract chain

### 5.1 Forward → Research

Proposed new module `src/quant/integration/forward_adapter.py` (NEW, not yet written):

```python
def materialize_pit_panel(recorder: ForwardRecorder, recorded_before: str,
                          symbols: Sequence[str] | None = None) -> tuple[PricePanel, dict[str, Any]]:
    """PIT-safe PricePanel view built only from ForwardRecorder.as_of(recorded_before).

    Returns (panel, coverage_report). A (date, symbol) bar is included only when
    every PricePanel.FIELDS name is present in that observation's `fields` mapping;
    a partially-observed bar is dropped and counted in coverage_report["dropped"],
    never filled or interpolated. This does not create a second data plane: it is a
    read-only, PIT-filtered reshape of exactly the rows ForwardRecorder.as_of already
    returns, into the one shape PricePanel already accepts. No new persistence.
    """

def research_ticket_provenance(recorder: ForwardRecorder, recorded_before: str,
                               symbols: Sequence[str]) -> dict[str, Any]:
    """Provenance block for a ResearchTicket sourced from forward data.

    Returns {"source_refs": [<content_address> for each contributing observation,
    sorted], "information_available_at": recorded_before,
    "observed_at": recorder.earliest_recorded_at(), "dataset_fingerprint":
    recorder.ledger_fingerprint()}. `information_available_at` is the caller-supplied
    PIT cutoff, never upgraded to a stronger time authority than
    ForwardObservation.time_provenance() itself declares (TIME_AUTHORITY_UNATTESTED_LOCAL_CLOCK).
    """
```

- Exact input type: `ForwardRecorder` (forward_recorder.py) plus a `recorded_before`
  ISO-8601 cutoff supplied by the caller (the desk/factory clock), never inferred.
- PIT cutoff: `ForwardRecorder.as_of(recorded_before, symbols)` — already exists,
  already the correct accessor per its own docstring ("the accessor research is
  supposed to use").
- Provenance fields preserved: `content_address` (per observation, sha256 of
  symbol/session/fields/source/fingerprint), `ledger_fingerprint()` (whole-ledger,
  order-independent), `earliest_recorded_at()`.
- No DatasetRegistry-compatible materialized view is required beyond the
  `PricePanel` reshape above: `run_lane`/`walk_forward`/`CapitalDesk` already consume
  `PricePanel`, so producing one from the forward ledger is sufficient; a second
  registry entry would be exactly the "second data plane" the mission forbids.
- `information_available_at` is derived as the literal `recorded_before` argument
  the caller passed to `as_of` — not `recorded_at` of any individual bar, and not
  upgraded past `TIME_AUTHORITY_UNATTESTED_LOCAL_CLOCK` (forward_recorder.py's own
  declared authority).

### 5.2 Research → Economic

Proposed new module `src/quant/integration/econ_bridge.py` (NEW):

```python
FAIL_CLOSED_REASON = "EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE"

def form_effect_estimate(ticket: ResearchTicket) -> EffectEstimate | None:
    """The fail-closed Research -> EffectEstimate bridge required by D1.

    Returns None (never a fabricated EffectEstimate) unless ticket.validation_result
    already carries an explicit, upstream-populated `frozen_effect_estimate` block with
    every one of: delta_hat, lower, upper, confidence_level, evidence_label,
    sample_provenance, estimator_form == ALLOCATION_WEIGHTED_RATIO,
    clustering_unit_provenance. When present, this function only *reshapes* those
    fields into EffectEstimate and calls .violations() (never invents any of them).
    When absent, returns None; the caller is responsible for the NO_TRADE / FAIL_CLOSED_REASON
    terminal outcome.
    """

def bridge_disposition(ticket: ResearchTicket) -> tuple[EffectEstimate | None, str | None]:
    """(estimate, fail_reason). fail_reason is FAIL_CLOSED_REASON or None."""
```

**Exact finding, stated plainly per the mission's instruction not to fake a positive
path:** current `ResearchTicket.validation_result` / `StrategyDefinition.evidence`
(populated by `factory/workers.py:_finish` from `factory/evaluate.py:summarize`/
`falsify`) contain `gross_return`, `net_return`, `annual_turnover`, `t_statistic`,
`required_t_statistic`, `beta_attribution` — **none of which is `delta_hat` on the
frozen `ALLOCATION_WEIGHTED_RATIO` coordinate, an interval, a `confidence_level`, or a
`clustering_unit_provenance`.** Today, `form_effect_estimate` on *any* real
`ResearchTicket` produced by the existing pipeline returns `None` and the bridge fails
closed with `EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE`. This is correct
behaviour, not a bug to route around.

- What must already exist to form `EffectEstimate`: a `frozen_effect_estimate` sub-object
  on `ResearchTicket.validation_result`, populated by Research/science code that is
  **out of scope for the first vertical slice** (it belongs to the Forward branch's
  `src/quant/science/` package — `formation.py`, `inference.py` — which computes
  point/interval estimates on a declared coordinate; that package is not part of the
  D1–D5 authority set and this handoff does not design it).
- What cannot be derived safely: `delta_hat`/`lower`/`upper` cannot be back-computed
  from `gross_return`/`net_return`/`t_statistic` without inventing a coordinate
  transform D1 explicitly forbids inventing.
- Fail-closed condition: `frozen_effect_estimate` absent, incomplete, or
  `EffectEstimate.violations()` non-empty ⇒ `bridge_disposition` returns
  `(None, "EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE")`.
- Evidence-label/admissibility rule: `evidence_label` is copied verbatim from the
  upstream ticket field, never set to `EVIDENCE_FORWARD_CONFIRMATION` by this bridge —
  that label may only be assigned by
  `forward_admissibility.evaluate_forward_confirmation`, per D1's explicit statement
  that "Forward-captured data does not automatically become `FORWARD_CONFIRMATION`."
  The bridge treats `evidence_label` as an opaque pass-through.
- Sample/dataset provenance: `sample_provenance` is populated from
  `ticket.source_refs` / the forward adapter's `dataset_fingerprint` (§5.1), not
  invented.

**Smallest upstream Research output extension required** (for the future Builder,
not for this slice's test — see §8 Path B): a `frozen_effect_estimate: dict` field
inside `ResearchTicket.validation_result`, written by whatever component eventually
performs the frozen-coordinate estimation. The vertical-slice acceptance test (§8) may
construct this field directly on a fixture `ResearchTicket` rather than deriving it
from `walk_forward`/`summarize`, because the mission explicitly forbids synthesizing
it through a production heuristic — this is a test fixture, not new production code.

### 5.3 Economic → Desk

`economic_gate(estimate, meue_result, theta, interaction, capacity, consistency)` returns
one `EconomicVerdict` (`decision.py:143`). The Desk-facing transfer object composes:

```python
@dataclass(frozen=True)
class EconomicAssessmentRef:
    """What the Desk receives; adapts EconomicVerdict + AssessmentRecord onto OpportunityTicket."""
    assessment_id: str                 # AssessmentRecord.assessment_id
    input_fingerprint: str             # compute_input_fingerprint(...)
    verdict: str                       # EconomicVerdict.verdict: CONTINUE | NO_TRADE | KILL
    reason: str                        # EconomicVerdict.reason
    capital_order_eligibility: str     # EconomicVerdict.capital_order_eligibility
    margin_of_safety: float | None     # EconomicVerdict.margin_of_safety
    economic_margin_size: float        # size_lane(...).gross_notional, 0.0 if not CONTINUE-eligible
    capacity_state: str                # from CapacityOutcome, "" if none applied
    sample_provenance: str             # EffectEstimate.sample_provenance
    research_ticket_id: str            # ResearchTicket.ticket_id
```

No new ticket family: this is carried as a new field on `OpportunityTicket`
(`opportunity.py:23`) — e.g. `ticket.record("VET", ..., economic_assessment=ref.to_dict())`
via the existing `record(stage, verdict, reason, **detail)` mechanism, which already
accepts arbitrary `**detail` per stage. `OpportunityTicket.stage_trace` already exists
precisely to carry per-stage structured detail; this needs no schema change to
`OpportunityTicket` itself, only a call site.

### 5.4 Desk → Book → Learning

- Deterministic operation ID: unchanged — `f"{opportunity_id}:{fill['symbol']}"`
  (`desk.py:275`, existing `Ledger.apply_fill` contract). The Economic assessment_id
  and input_fingerprint are additive provenance on the `OpportunityTicket`, not a
  second operation-id scheme; `Ledger.has_applied`/`apply_fill` need no change.
- Upstream identifiers stored in `DeskJournal`: `DeskJournal.begin`/`commit` already
  persist the full `ticket.to_dict()` (`journal.py:80-109`); once `EconomicAssessmentRef`
  is embedded in the ticket's stage_trace (§5.3), it is durable there for free — no
  `DeskJournal` schema change required.
  `DeskJournal.commit`'s status→counter mapping (`{"BOOKED":..., "NO_TRADE":...,
  "VETOED":..., "BLOCKED":...}`, `journal.py:100`) already has a bucket for a
  fail-closed `NO_TRADE` from the economic gate; no new terminal status is needed.
- Book idempotence boundary: unchanged (`Ledger.apply_fill`, `has_applied`).
- Learning outcome key: proposed new method
  `LearningStore.record_economic_outcome(opportunity_id, verdict, reason,
  assessment_id, ticket_id, **detail) -> bool`, following the exact idempotent
  pattern of `record_research` (`store.py:56-74`: check-then-append-then-save, keyed
  on an id already seen). Reuses `self.lessons` / `self.lane_priorities` structures;
  no new persisted top-level collection.
- NO_TRADE persistence semantics: a NO_TRADE from `economic_gate` (whether
  `BLOCKING_INPUT_DEFECT`, `EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE`,
  `UNCERTAINTY_STRADDLES_ECONOMIC_THRESHOLD`, or `NO_DEPLOYABLE_EXPOSURE`) is recorded
  via `ticket.stop("VET", "NO_TRADE", reason, economic_assessment=ref.to_dict())`
  → `DeskJournal.commit(...)` (no pending plan ever opened, since `journal.begin` is
  only called immediately before `_apply`, at `desk.py:264`) → zero Ledger mutation →
  `LearningStore.record_economic_outcome(...)`.
- Restart/replay: unchanged mechanism. Since NO_TRADE never calls `journal.begin`, a
  crash before the economic gate simply re-runs `_run_strategy` from `SCAN` on
  restart (idempotent, no partial fill state exists to resume). A crash *after*
  `journal.begin` but before `_apply` completes resumes exactly as `_resume` already
  handles today (`desk.py:291-299`) — the Economic gate is not re-run, because its
  result is already baked into the persisted `ticket.to_dict()` the pending plan carries.

## 6. State transition table

| State | Terminal? | Next authority | Durable record | Book may mutate | Learning must receive outcome |
|---|---|---|---|---|---|
| Research rejected (`falsify` fails) | Yes (ticket) | none | `ResearchTicket` (REJECTED→LEARNED), `research_memory` jsonl | No | Yes (`record_research`, existing) |
| Research validated, no valid EffectEstimate (`bridge_disposition` → None) | Yes (this vertical path) | none | `OpportunityTicket.stop("VET","NO_TRADE", FAIL_CLOSED_REASON)`, `DeskJournal.commit` | No | Yes (`record_economic_outcome`) |
| Economic `NO_TRADE` (threshold/defect/no exposure) | Yes | none | as above, `economic_gate` reason in ticket detail | No | Yes |
| Economic `KILL` | Yes | none (lane dominated) | as above; `EconomicVerdict.verdict == "KILL"` recorded verbatim | No | Yes |
| Economic `CONTINUE`, size = 0 (`fraction(margin) == 0` or `capital_fraction == 0`) | Yes | none | ticket stopped at `SIZE`, `NO_TRADE`, `economic_margin_size=0.0` | No | Yes |
| Economic `CONTINUE`, size > 0, Risk veto (`evaluate_risk`/`verify_final` not approved) | Yes | none | ticket stopped at `RISK`, `VETOED`, `verdict["vetoes"]` | No | Yes |
| Economic `CONTINUE`, size > 0, Risk approved, shadow fill | No until `BOOK` | Book/Ledger | `ticket.complete(...)`, `DeskJournal.begin`→`commit` | Yes, exactly once via `apply_fill` | Yes |
| Fill capacity-truncated (`ExecutionModel.fill` truncates) | No (continues chain) | Risk re-check (`verify_final`) | fill dict carries `capacity_truncated=True`; ticket records final ratios | Yes, on the truncated quantity | Yes, on eventual terminal state |
| Restart between assessment and Desk (`journal.begin` never called) | N/A | re-decide from SCAN | none pending; assessment itself durable only if `EconomicAssessmentJournal.record` was already called (Gate-C decision: see §9) | No | On the re-decided terminal state |
| Restart after `DeskJournal.begin`, before Book commit | N/A | `_resume` | `journal.pending[opportunity_id]` | Yes, exactly once (`apply_fill` idempotent by `operation_id`) | Yes, once `_finish` completes |
| Replay of same observation/opportunity (`opportunity_id` already `is_processed`) | terminal (already recorded) | none | `journal.outcomes[opportunity_id]` returned unchanged | No (no new mutation) | Not re-emitted (`record_economic_outcome` must be idempotent by id, matching `record_research`'s pattern) |

## 7. Function-level patch plan and changed-path budget

Classification per path, independently verified against exact code (not copied from
the governance doc's forecast):

| Path | Classification | Justification |
|---|---|---|
| `src/quant/integration/forward_adapter.py` | **NEW** | Confirmed required; no existing module reshapes `ForwardRecorder.as_of` output into `PricePanel`. |
| `src/quant/integration/econ_bridge.py` | **NEW** | Confirmed required; no existing module maps `ResearchTicket` → `EffectEstimate` or composes D2's `min(...)`. |
| `src/quant/factory/workers.py` | **MODIFY** | Exactly one deletion: the `definition.transition("SHADOW", ...)` call at line 243 (§4/D3). No other change to this file is needed for the vertical slice. |
| `src/quant/factory/evaluate.py` | **NOT_NEEDED** — correction against the governance doc's forecast. The only diff between the Blue spine and both Forward/Economic branches in this file is an unrelated `weights_fn: Callable` parameter added to `walk_forward` for a second signal family (confirmed by direct diff, §3). It has no relationship to the Research→Economic bridge, `EffectEstimate`, or SIZE/RISK ordering. Including it in the changed-path budget would be scope creep. |
| `src/quant/desk/desk.py` | **MODIFY** | Insert the Economic gate + `min(ECONOMIC_MARGIN_SIZE, DESK_LIFECYCLE_CAP)` composition between the existing VET and SIZE stages in `_run_strategy` (between `desk.py:186` and `desk.py:188`, i.e. after the existing rebalance/VET check and before the existing capital-fraction sizing). Desk `RISK` (`evaluate_risk`/`verify_final`) is **not modified** — D2 requires Risk stay an independent downstream veto, and it already is. |
| `src/quant/learning/store.py` | **MODIFY** | Add `record_economic_outcome`, following the exact idempotent shape of `record_research` (§5.4). No change to existing methods. |
| `tests/integration/test_first_vertical_shadow_loop.py` | **NEW** (spec only, §8) | Deterministic E2E proof; does not exist today (confirmed: no `tests/integration/` directory matches this name on the current tree). |

**Prerequisite not captured by the governance doc's changed-path budget, flagged here
as a factual gap, not a re-opening of D1–D5:** the Blue spine tree has **no**
`src/quant/economics/` package and **no** `forward_recorder.py`/`forward_admissibility.py`
at all (§3). `econ_bridge.py` cannot import `EffectEstimate`, `economic_gate`,
`MarginSizingRule`, `size_lane`, or `verify_research_cost_consistency` unless those
modules exist on whatever base branch Gate-C builds from. Two options exist, and Blue
decides between them before Gate C, not this document:

1. Vendor the exact files `decision.py`, `journal.py`, `sizing.py`, `capacity.py`,
   `consistency.py`, `opening.py`, `coordinate.py`, `margin.py`, `frictions.py`,
   `recipe.py`, `states.py`, `theta.py`, `timeline.py`, `value.py`, `parameters.py`,
   `fingerprint.py`, `partition.py`, `scenarios.py` from the Economic branch
   (`35dff27b...`) as new, unmodified files under `src/quant/economics/`, and
   `forward_recorder.py` + `forward_admissibility.py` (+ `admissibility.py`,
   `forward_contracts.py` if `SourceProfile` gating is wanted for the fixture) from
   the Forward branch (`83521dbf...`), each individually — **file-level vendoring of
   named modules is not a whole-leaf merge** of either parallel branch (neither
   branch's `factory/families.py`, `science/`, `operations/`, `status/` changes are
   touched), so this stays inside the "no whole-leaf merge" constraint.
2. Blue merges the Forward and/or Economic branches into the spine through its own
   separate governance action before Gate C, ahead of the Builder mission in §10.

Either way, this is additive file creation (copies of already-authored, already-pinned
code), not new economic/execution/sizing logic invented by the Builder — it does not
expand the semantic surface this mission was scoped to. The Builder mission in §10
states this prerequisite explicitly so it is not silently assumed away.

### Patch 1 — `src/quant/factory/workers.py`

```diff
     if verdict["passed"]:
         definition.transition("VALIDATED", "survived every declared falsification test")
-        definition.transition("SHADOW", "evidence accepted; shadow track record required "
-                                        "before full capital")
     else:
```

### Patch 2 — `src/quant/integration/forward_adapter.py` (new)

Signatures and contract: §5.1.

### Patch 3 — `src/quant/integration/econ_bridge.py` (new)

Signatures and contract: §5.2, §5.3. Additionally:

```python
def economic_size(verdict: EconomicVerdict, rule: MarginSizingRule, capital: float,
                  weights: Mapping[str, float], strategy_id: str, plan_id: str,
                  lifecycle_cap_fraction: float) -> SizingPlan:
    """D2: FINAL_SIZE = min(ECONOMIC_MARGIN_SIZE, DESK_LIFECYCLE_CAP).

    economic_margin_size = size_lane(plan_id, rule, verdict.margin_of_safety, capital,
    weights, strategy_id) when verdict.verdict == CONTINUE, else an all-zero SizingPlan.
    desk_lifecycle_cap = capital * lifecycle_cap_fraction (StrategyDefinition.capital_fraction).
    The final plan scales the economic plan's sleeves down (never up) so its gross_notional
    does not exceed desk_lifecycle_cap; never invents an economic size when the desk cap
    is smaller, and never lets the desk cap override a genuine economic NO_TRADE/zero.
    """
```

### Patch 4 — `src/quant/desk/desk.py`

In `_run_strategy`, between the existing VET acceptance (`desk.py:186`) and the
existing SIZE block (`desk.py:188`):

```python
        # --- ECONOMIC GATE (D1/D3) -----------------------------------------
        estimate, fail_reason = econ_bridge.bridge_disposition(research_ticket)
        if estimate is None:
            return self._finish(definition, ticket.stop(
                "VET", "NO_TRADE", fail_reason, economic_assessment=None))
        verdict = economic_gate(estimate, meue_result, theta, interaction,
                                capacity, consistency)
        assessment_id = f"{ticket.opportunity_id}:ECON"
        input_fingerprint = compute_input_fingerprint(estimate, meue_result, theta,
                                                       interaction, capacity, consistency)
        record = AssessmentRecord.from_verdict(assessment_id, input_fingerprint, verdict,
                                               meue_result)
        self.economic_journal.record(record)   # idempotent; raises AssessmentConflict on
                                                 # a genuine input change under the same id
        ticket.record("VET", verdict.verdict, verdict.reason,
                      economic_assessment=record.to_dict())
        if verdict.verdict != "CONTINUE":
            return self._finish(definition, ticket.stop(
                "VET", "NO_TRADE" if verdict.verdict != "KILL" else "REJECTED",
                verdict.reason))
```

This requires `CapitalDesk.__init__` to accept a new
`economic_journal: EconomicAssessmentJournal | None = None` parameter (constructed
from `paths.economic_journal` analogous to `paths.desk_journal`), and `research_ticket`
to be threaded into `_run_strategy` from `run_session` (currently `_run_strategy` only
receives `definition`, not the `ResearchTicket` that validated it — today's desk loop
scans `StrategyDefinition`s, not `ResearchTicket`s directly, since a definition already
embeds `evidence.research_ticket` as an id string, not the object; the vertical slice's
test harness must load the actual `ResearchTicket` by that id before calling
`_run_strategy`, or `_run_strategy` gains a small loader call). This coupling is the
single largest structural seam the vertical slice must close; the exact mechanism
(load-by-id inside desk.py vs. pass-through from the caller) is left to the Builder
mission (§10) as an implementation-order-only decision, since either choice is
semantically identical and neither reopens D1–D5.

Then, at the existing SIZE block, replace the pure lifecycle-fraction sizing with
`econ_bridge.economic_size(verdict, rule, capital, weights, strategy_id, plan_id,
definition.capital_fraction)`, and derive `target_notional` from the resulting
`SizingPlan.by_strategy()[strategy_id]` instead of the current
`capital * weight` computation at `desk.py:190-191`.

### Patch 5 — `src/quant/learning/store.py`

```python
def record_economic_outcome(self, opportunity_id: str, verdict: str, reason: str,
                            assessment_id: str, research_ticket_id: str,
                            **detail: Any) -> bool:
    """Idempotent by opportunity_id, mirroring record_research's shape."""
    if any(item.get("source") == "ECONOMIC" and item.get("opportunity_id") == opportunity_id
          for item in self.lessons):
        return False
    self.lessons.append({"at": utc_now(), "source": "ECONOMIC", "opportunity_id": opportunity_id,
                        "outcome": verdict, "reason": reason, "assessment_id": assessment_id,
                        "research_ticket_id": research_ticket_id, **detail})
    self.save()
    return True
```

Called from `CapitalDesk._finish` (or a thin wrapper around it) exactly once per
terminal `OpportunityTicket`, for every terminal status — `NO_TRADE` and `BOOKED`
alike, since NO_TRADE is a first-class required outcome (mission §3/§9).

## 8. Deterministic E2E test specification

`tests/integration/test_first_vertical_shadow_loop.py` (NOT written — specification only).

Common fixture skeleton for all three paths:

- One `PricePanel` built from 3 fixed sessions (`2026-01-05`, `2026-01-06`,
  `2026-01-07`) × 1 symbol (`TEST`), fixed OHLCV values, no randomness.
- One `ForwardObservation` per session for `TEST`, fixed `source_fingerprint`,
  recorded via a real `ForwardRecorder(tmp_path / "forward.jsonl")`.
- One `ResearchTicket` (`ticket_id="RT-VERTICAL-001"`), `status="VALIDATED"`,
  `instruments=["TEST"]`, `source_refs=[<content_address of each observation>]`,
  `information_available_at` = the adapter's PIT cutoff.
- One `StrategyDefinition` at lifecycle `VALIDATED` (never `SHADOW` — proves patch 1),
  `evidence={"research_ticket": "RT-VERTICAL-001"}`.
- One `CapitalDesk` constructed against a fresh `tmp_path` (fresh `Ledger`,
  `DeskJournal`, `EconomicAssessmentJournal`, `LearningStore`).

### Path A — fail-closed NO_TRADE

- `ResearchTicket.validation_result` has **no** `frozen_effect_estimate` key.
- Run one `CapitalDesk.run_session`.
- Assert: `tickets[0].status == "NO_TRADE"`, `tickets[0].reason ==
  "EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE"`.
- Assert: `Ledger.state.cash == initial_capital` and `Ledger.state.applied_operations == []`
  (zero Book cash/position mutation).
- Assert: `DeskJournal.outcomes[opportunity_id]` and `LearningStore.lessons` each carry
  one entry referencing `research_ticket_id="RT-VERTICAL-001"` (durable provenance).
- Assert: `StrategyDefinition.lifecycle == "VALIDATED"` still (no accidental SHADOW).
- Replay: construct a second `CapitalDesk` against the same `tmp_path` and re-run the
  identical session date; assert `replayed == [opportunity_id]`, no new ledger
  mutation, no duplicate `LearningStore` entry (idempotence).

### Path B — positive-size SHADOW

- `ResearchTicket.validation_result["frozen_effect_estimate"]` is populated directly
  on the fixture with legitimate, hand-chosen values satisfying
  `EffectEstimate.violations() == []`: `evidence_label = "FORWARD_CONFIRMATION"`
  (set on the fixture directly, standing in for a real
  `evaluate_forward_confirmation` call — the test may call
  `evaluate_forward_confirmation` for real against the fixture's own `ForwardRecorder`
  to justify the label rather than merely asserting it, which is the stronger and
  preferred form), `delta_hat/lower/upper` positive and comfortably above a small
  fixed `meue` fixture, `confidence_level=0.95`,
  `clustering_unit_provenance` set to a declared (non-`UNDECLARED`) value,
  `estimator_form = ALLOCATION_WEIGHTED_RATIO`.
- `ThetaState`, `MEUEResult`, `PortfolioInteraction`, `CapacityOutcome` fixtures are
  constructed with small, fixed, declared values (not derived from search) sufficient
  for `economic_gate` to return `CONTINUE` with `capital_order_eligibility ==
  ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE`.
- `verify_research_cost_consistency(RESEARCH_ONE_WAY_COST_BPS,
  ExecutionCostModel.from_execution_model(desk.execution), participation_used=<value
  implied by the fixture's fixed order size>)` is called and passed into
  `economic_gate`, and asserted `.consistent`.
- Run one `CapitalDesk.run_session` across sessions `2026-01-05` → execute at
  `2026-01-06` open.
- Assert: research eligibility (`StrategyDefinition.lifecycle == "VALIDATED"` at
  start), Economic verdict `CONTINUE`, `economic_margin_size > 0`.
- Assert: `SizingPlan.gross_notional == min(economic_margin_size, capital *
  definition.capital_fraction)` exactly (D2, composed not merely asserted separately).
- Assert: `RiskLimits`/`evaluate_risk` approves (fixture sized well inside default
  `RiskLimits()`).
- Assert: `ExecutionModel.fill` called exactly once for `TEST` (mock-count or a
  counting wrapper around `self.execution.fill`).
- Assert: `Ledger.apply_fill` applied exactly once (`state.fills == 1`,
  `len(state.applied_operations) == 1`).
- Assert: implementation shortfall preserved — `ticket.book_effect`/fill dict carries
  a nonzero `implementation_shortfall` matching `ExecutionModel.fill`'s own computed
  value (not recomputed independently).
- Assert: full provenance — `ticket.stage_trace` contains the `economic_assessment`
  detail with `assessment_id`, `input_fingerprint`, and `research_ticket_id ==
  "RT-VERTICAL-001"`; `EconomicAssessmentJournal.get(assessment_id)` returns the same
  `input_fingerprint`.
- Assert: `LearningStore.record_economic_outcome` recorded once with `outcome ==
  "BOOKED"`.
- Assert: `StrategyDefinition.transition` to `SHADOW` happened exactly once, driven by
  the Economic verdict (not by `workers.py`), and only after `_run_strategy`, not
  before.
- Replay: identical to Path A's replay assertion — re-run, assert zero double-fill
  (`Ledger.has_applied` recognises the `operation_id`), zero duplicate Learning entry,
  identical final `Ledger.state.cash`.

### Path C — Risk veto / zero-size negative control

Two sub-cases, both required:

1. **Zero size cannot fill.** Same fixture as Path B but with `MarginSizingRule`
   fixture parameters (`minimum_margin` set above the fixture's `margin_of_safety`)
   forcing `rule.fraction(margin_of_safety) == 0.0`. Assert `economic_margin_size ==
   0.0`, `SizingPlan.sleeves == ()`, `_execute` produces zero fills (all legs skipped
   as below `MIN_ORDER_NOTIONAL`), ticket terminal status `NO_TRADE`, zero Ledger
   mutation, zero `ExecutionModel.fill` calls.
2. **Economic CONTINUE does not bypass Risk.** Same Path-B fixture but with
   `RiskLimits` fixture parameters set so `evaluate_risk`'s gross/net ratio checks
   reject the sized portfolio (e.g. an artificially tiny `RiskLimits.max_gross`).
   Assert ticket terminal status `VETOED` at stage `RISK` (not `SIZE`, not `VET`),
   `verdict["approved"] is False`, zero Ledger mutation, `ExecutionModel.fill` never
   called (proves Risk runs and can block *after* a genuine Economic `CONTINUE`,
   i.e. Risk is not short-circuited by economic eligibility).

## 9. Idempotence / restart / provenance summary

- Every persistent mutation on this new path (`EconomicAssessmentJournal.record`,
  `DeskJournal.begin/commit`, `Ledger.apply_fill`, `LearningStore.record_economic_outcome`)
  is keyed by a deterministic id derived from `opportunity_id` and is a no-op (or a
  detected-conflict raise, for `EconomicAssessmentJournal`) on replay with unchanged
  inputs — no new non-idempotent write is introduced.
- `EconomicAssessmentJournal.record` is called **before** `DeskJournal.begin`
  (assessment precedes intent-to-fill), so a crash between assessment and
  `journal.begin` on restart simply re-decides from `SCAN`, recomputes the identical
  `EffectEstimate`/`EconomicVerdict` (deterministic fixture inputs), and
  `EconomicAssessmentJournal.record` recognises the identical `input_fingerprint` and
  no-ops rather than raising `AssessmentConflict`. This is safe *only* because nothing
  between assessment and `journal.begin` depends on wall-clock or non-deterministic
  state in the vertical slice's design — true in this fixture; a future non-deterministic
  input (e.g. a live clock in `theta`) would need its own idempotence argument, out of
  scope here.
- A crash after `DeskJournal.begin` before `Ledger.apply_fill` completes resumes via
  the existing `_resume` path unchanged; the Economic verdict is not re-evaluated
  because it is already embedded in the persisted ticket the pending plan carries.

## 10. Complete future Builder mission

```markdown
# BUILDER — POST-P0 FIRST VERTICAL SHADOW LOOP — 2026-09-21

ROLE: Claude Code / Product Builder
REPOSITORY: fahimahmedb/quant-trade
WORK ONLY ON: builder/post-p0-first-vertical-shadow-loop-2026-09-21
BASE SELECTION RULE: branch from the exact commit Blue names at Gate-C authorization
time as the current Blue Product spine HEAD (do not assume cbf30c1b still applies;
resolve it fresh via `git log` on the assigned base ref). Do NOT create the branch
until Blue's Gate-C authorization message names this exact base commit.

## Authorities (highest first)
1. QUANT_NORTH_STAR.md
2. Gate-C authorization message from Blue (names base commit + any changed decision)
3. This prep handoff: handoff/CLAUDE_POST_P0_VERTICAL_BUILD_PREP_2026-09-21.md
4. handoff/BUILDER_POST_P0_VERTICAL_INTERFACE_MAP_2026-09-21.md
5. handoff/ANTIGRAVITY_POST_P0_VERTICAL_SHADOW_LOOP_DESIGN_2026-09-21.md
6. Canonical Forward: parallel/claude-forward-data-2026-09-20@83521dbfdd90027c90d04adfb7d814593c2355c5
7. Canonical Economic: parallel/claude-economic-v2-2026-09-20@35dff27b8fac53618da434ee6d31febbddcc0e69

D1-D5 (governance/BLUE_CLAUDE_POST_P0_VERTICAL_BUILD_PREP_2026-09-21.md) are fixed.
Do not reopen without an exact code contradiction, documented as
BLUE_DECISION_REQUIRED_<ID> with file/function/current-behavior/contradiction/options.

## Prerequisite (resolve before writing glue code)
The Blue spine has no src/quant/economics/ package and no forward_recorder.py /
forward_admissibility.py. Before Patch 2-4 below can import anything from them,
either (a) vendor the exact named files from the pinned Economic/Forward SHAs above
as new, byte-identical files (no edits) into the base branch, and cite each file's
exact source SHA in the commit message, or (b) confirm Blue has already merged them
via separate governance action, and cite that merge commit. Do not invent, "improve",
or partially rewrite any vendored file while copying it.

## Exact changed-path allowlist
- src/quant/integration/__init__.py (new, empty package init)
- src/quant/integration/forward_adapter.py (new)
- src/quant/integration/econ_bridge.py (new)
- src/quant/factory/workers.py (modify: delete the VALIDATED->SHADOW auto-transition
  at the site identified in this handoff's Section 4/D3)
- src/quant/desk/desk.py (modify: insert Economic gate + D2 sizing composition between
  VET and SIZE, per Section 7 Patch 4 of this handoff)
- src/quant/learning/store.py (modify: add record_economic_outcome, per Section 7
  Patch 5)
- src/quant/paths.py (modify only if a new persisted path, e.g. economic_journal, is
  genuinely required — confirm against exact QuantPaths fields first)
- tests/integration/test_first_vertical_shadow_loop.py (new, per Section 8 of this
  handoff)
- Vendored economics/forward files per the Prerequisite above, if option (a) is taken.

## Forbidden
- No change to src/quant/desk/risk.py, src/quant/desk/execution.py,
  src/quant/book/ledger.py semantics (reuse as-is; risk stays an independent veto,
  execution stays the sole shadow-fill authority, Book stays the one ledger).
- No second Book, sizing engine, execution engine, scheduler, or ticket family.
- No auto-promotion of VALIDATED to SHADOW from research code; only the Economic-gate
  path in desk.py may call StrategyDefinition.transition("SHADOW", ...).
- No fabricated EffectEstimate field, no fabricated evidence_label, no fabricated
  FORWARD_CONFIRMATION status outside forward_admissibility.evaluate_forward_confirmation.
- No merge of whole Forward or Economic branches; only the named vendored files.
- No P0 runtime, target-host, schema, or workflow modification.
- No real-capital authorization, no live order submission, no t0 declaration.

## Required tests
tests/integration/test_first_vertical_shadow_loop.py implementing exactly the three
paths (A: fail-closed NO_TRADE, B: positive SHADOW, C: Risk veto / zero-size control)
specified in Section 8 of handoff/CLAUDE_POST_P0_VERTICAL_BUILD_PREP_2026-09-21.md,
including both paths' replay-idempotence assertions. Existing suite
(PYTHONPATH=src python3 -m unittest discover -s tests -v) must remain green.

## Acceptance criteria
- All three E2E paths pass, deterministically (no wall-clock, no randomness, no
  network).
- Zero Book cash/position mutation on Path A and Path C.
- Exactly one Ledger.apply_fill and one ExecutionModel.fill call on Path B.
- Full existing test suite green.
- python3 scripts/generate_schemas.py --check clean if any dataclass touched by this
  work is schema-tracked; otherwise state explicitly that none are.
- No lifecycle transition to SHADOW except via the new Economic-gate call site.

## Handoff
Write handoff/BUILDER_POST_P0_FIRST_VERTICAL_SHADOW_LOOP_2026-09-21.md with: exact
diff summary, exact test run output, any BLUE_DECISION_REQUIRED raised, and final
status BUILDER_VERTICAL_SHADOW_LOOP = COMPLETE or one precise blocker.

## Safety state (preserve unless Blue's Gate-C message explicitly changes it)
PRODUCT_INTEGRATION = the value Blue's Gate-C message sets (this mission may finally
flip it, since it is the authorized implementation mission — confirm the exact value
Blue names rather than assuming)
P0_RUNTIME_MUTATION = FALSE
TARGET_HOST_TOUCHED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
t0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
```

## 11. Remaining Blue decisions

None required. D1–D5 are sufficient to fully specify the vertical slice; the one
exact-code contradiction found (§4/D3) is resolved by applying D3, not by reopening
it. The economics/forward vendoring question (§7 prerequisite) is a build-sequencing
choice for Blue, not a semantic decision about D1–D5.

## 12. Opportunity-cost assessment

This prep closes the specific uncertainty "can the existing Forward, Research,
Economic, Desk, Book and Learning surfaces be joined through the smallest fail-closed
slice without a second authority" — answer: **yes**, with exactly one existing-code
deletion (workers.py) and two new narrow glue modules, provided the economics/forward
files are made available on the base branch first. The main remaining risk to
Gate-C velocity is not architectural: it is that a real, non-fixture
`frozen_effect_estimate` on `ResearchTicket.validation_result` does not exist yet
anywhere in this repository (Forward's `science/formation.py`/`inference.py` compute
something in that direction but were not in this mission's authority set to verify).
Until that lands, every real (non-fixture) `ResearchTicket` will hit Path A
(fail-closed NO_TRADE) in production, which is correct system behaviour, not a defect
of this design — but Blue should not expect Path B to fire on real research output
before that science-side work is separately authorized and verified.

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
