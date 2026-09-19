# CLAUDE ECONOMIC V2 — LIVE CHECKPOINT

**Branch:** `parallel/claude-economic-v2-2026-09-20`
**Base:** `b17b381a8fa1f6a24e6cd6f92a090b40627bfe78` (Wave 1 CLAUDE handoff commit)
**Role:** Builder / Quant Engineer, ECONOMIC V2 consolidation. Not P0. Not Clock.

This file is updated after every substantial slice of work. It is the running
log; `handoff/CLAUDE_ECONOMIC_V2_2026-09-20.md` is the final deliverable
written at the end.

---

## Branch note (read this first)

The mission brief names this branch and base SHA explicitly, and both check out
exactly as stated (`git merge-base --is-ancestor` confirms the base is the
branch tip; zero commits ahead at start). Separately, this session's own
harness-level git config named a *different* branch
(`claude/economic-v2-consolidation-cl3cnb`), but that branch's remote has been
**deleted** (`git fetch` reported `[deleted] (none) ->
origin/claude/economic-v2-consolidation-cl3cnb`), while
`parallel/claude-economic-v2-2026-09-20` exists, matches the mission's stated
base exactly, and fits the repository's live `parallel/*` wave-naming
convention alongside `parallel/claude-wave1-economic-system-2026-09-19` and
`parallel/codex-wave1-economic-system-2026-09-19`. Proceeding on the
mission-specified branch as the evidently-current target; flagging the
discrepancy here for the record rather than silently overriding either
instruction.

---

## 0. Setup verified

```
git fetch --all --prune
git checkout -B parallel/claude-economic-v2-2026-09-20 origin/parallel/claude-economic-v2-2026-09-20
HEAD = b17b381a8fa1f6a24e6cd6f92a090b40627bfe78  (exact match, 0 commits ahead)
```

Authority docs read: `QUANT_NORTH_STAR.md`, `STATE.md`,
`handoff/PARALLEL_WAVE1_CLAUDE_2026-09-19.md`,
`handoff/CLAUDE_WAVE1_PROTOCOL_PROPOSALS_2026-09-19.md`.

Codex red team read (reference only, read-only, not merged, not checked out):
`parallel/codex-wave1-economic-system-2026-09-19` @
`738a5879ef8634d3e08c717a2d439632fe64e1ff` (tip confirmed by `git rev-parse`) —
`handoff/PARALLEL_WAVE1_CODEX_2026-09-19.md`, `src/quant/economics/engine.py`,
`tests/test_economic_engine.py`, all via `git show <sha>:<path>`, working tree
never left the Claude branch.

P0 boundary respected: no read of `src/quant/dataplane/sec/**`,
`deploy/quant_sec_supervisor.py`, `deploy/quant-sec-capture.service`,
`src/quant/clock.py`, `scripts/quant.py`, or any P0 reservoir file. The P0-named
files under `handoff/` (`SEC_FORM4_*.json`) were listed but not opened; they
are unrelated to the economics engine.

---

## 1. Red team: Claude Wave 1 vs Codex Wave 1 economics engine

**Scope.** Codex's entire economic engine is one file,
`src/quant/economics/engine.py` (~200 lines): `EconomicEngine.assess()` maps a
flat `EconomicInputs` dataclass to `CONTINUE`/`NO_TRADE`/`KILL` through a single
function. Claude Wave 1's is a package of 18 modules
(`states, fingerprint, coordinate, parameters, frictions, capacity, scenarios,
margin, partition, theta, recipe, decision, consistency, opening, timeline,
sizing`) implementing the full chain the mission's North Star specifies:
`scientific effect -> expected gross effect -> executable exposure -> frictions
-> capacity -> uncertainty -> sizing -> portfolio interaction -> net value ->
CONTINUE/NO_TRADE/KILL`. These are not two engines of comparable scope; Codex's
is a bounded, honest, single-slice prototype, explicit that it is one. Point-by-
point:

| Axis | Codex (`engine.py`) | Claude Wave 1 (`economics/*`) | Verdict |
|---|---|---|---|
| **Architecturally correct decomposition** | One flat `assess()`: capacity → cost sum → uncertainty subtraction → margin → decision, in one function. | Chain is decomposed into named, independently-testable stages matching the North Star chain exactly (`coordinate.py` gate, `frictions.py` K_forward, `scenarios.py`/`margin.py` M_economic, `capacity.py`, `decision.py`). | **Claude.** The North Star's chain is a first-class requirement (`QUANT_NORTH_STAR.md` §Capital Desk); Codex's flat function cannot be audited stage-by-stage the way `EconomicVerdict.chain` can. |
| **Fail-closed on missing input** | Yes — `REQUIRED_COSTS` frozenset of exactly 8 named strings; a missing/extra name raises `ValueError` before any number is produced. | Yes, more structurally — `KForwardRecipe.coverage_violations()` requires every one of the *governed* F1–F7 cost classes to be modelled or explicitly `AuthorisedZero`'d with a named authority; `ParameterInventory` refuses to add a parameter after freeze. | **Tie on intent, Claude on rigor.** Codex's fail-closed set is a hardcoded Python set with no governance citation; Claude's is traceable to `D09_ROUTE_B_FRICTION_MARGIN_PARTITION_2026-09-17.md` and requires an explicit authority to declare a zero, not just an absent name. |
| **Double-counting** | Structurally exposed: `W1-SELF-002` (scalar uncertainty subtraction can't represent correlated joint scenarios) and `W1-SELF-003` (fixed costs unchanged after capacity clipping) are Codex's own admitted defects. No anti-double-count map exists. | Has a dedicated anti-double-count object, `partition.py` (`RiskPartition`/`FRICTION_MARGIN_DOUBLE_COUNT`), requiring a documented non-overlap proof before the same named risk class may be charged in both `K_forward` and `M_economic`. `frictions.py` separately forbids conservatism markups inside `K_forward` (`NO_HIDDEN_CONSERVATISM_INSIDE_K_FORWARD`) so double-charging can't hide there either. | **Claude.** Codex has no mechanism to catch this class of bug at all; Claude has both a structural rule and a runtime check. |
| **Economically dangerous state** | `mode not in {PAPER, SHADOW}` raises — good. But cost amounts are opaque pre-computed currency values (`CostInput.amount`) with no proof they scale with size (`W1-SELF-001`): a capacity change does not re-derive the friction, so the net value at a clipped size can be silently wrong in the safe *or* unsafe direction depending on cost shape. | Every cost is a `functional` (`delta, theta, params) -> currency`, so a change in `theta.capital` or `delta` mechanically changes the charge, and `verify_dependence_declarations` probes the functional numerically and fails the recipe if a declared-independent component actually varies (or vice versa). Capacity clipping is separately classified (`POLICY_UNCHANGED` / `POLICY_SCALED_HOMOGENEOUSLY` / `NEW_POLICY_VERSION`) rather than silently re-scaling a stale cost. | **Claude**, decisively — this is the exact failure mode Codex's own red team (§Self Red Team item 1) flagged as high deployment relevance in itself. |
| **Persistable / replayable** | `input_fingerprint` (SHA-256 of canonical JSON) exists and is order-independent/version-sensitive (tested). No journal; Codex's own handoff names this the top opportunity-cost gap (`W1-EVID-001`). | Every recipe object (`ParameterInventory`, `KForwardRecipe`, `JointScenarioSet`, `MEUERecipe`) is independently hashable via `recipe_hash()`, which structurally refuses to hash a document carrying a realised-outcome key (`RecipeNotOutcomeBlind`) — outcome-blindness is enforced at the hashing layer, not by convention. `theta.py`'s `EvaluationSession` additionally seals against re-evaluating a new `theta` after a threshold was seen (`NO_SIZE_SEARCH_TO_MAKE_MEUE_ATTAINABLE`), which Codex has no equivalent for. Neither side has a durable *assessment* journal yet — this is the one gap both waves independently identified as the top remaining priority, and it is new work for this V2 pass (§4 below), not a point of comparison. | **Claude** on fingerprinting rigor and anti-threshold-shopping; **both equally missing** the actual durable journal. |
| **D09 frozen-contract respect** | Consumes a single `effect_uncertainty` scalar with no coordinate binding, no reference to `ALLOCATION_WEIGHTED_RATIO`, no citation of the frozen EC1 estimand. Silent about whether its `expected_gross_effect` is even on the frozen `delta` coordinate. | `coordinate.py`'s `evaluate_delta_coordinate` is a dedicated, cited gate binding the five EC1 declarations (return convention, benchmark=SPY, `ALLOCATION_WEIGHTED_RATIO` aggregation, allocation-weight-precedes-outcome, D19 terminal-treatment reference) before any number is consumed, refusing to guess a missing one (`DELTA_COORDINATE_UNRESOLVED`) or bend the coordinate to fit data (`DELTA_COORDINATE_MISMATCH`). Every module's docstring cites the specific frozen `D09_ROUTE_B_*` document it implements. | **Claude, decisively.** Codex does not engage with the frozen D09/EC1 contracts by name at all; it is silent on whether its scalar effect is even the right estimand. This is not a defect in Codex's own stated scope (it declares itself outcome-blind and bounded), but it means Codex's engine could not stand in for Claude's without reopening every one of those bindings from scratch. |
| **RECIPE_PROVISIONAL vs authority** | No equivalent concept — Codex's engine has no notion of "this number is real vs a placeholder"; every consumed parameter is just a `ModelParameter` with a `source` string, treated as equally authoritative regardless of whether that source is `"predeclared-model"` (test fixture) or genuine calibration. | Has the concept and reports it honestly, but Wave 1's own red team (§8.1) flagged that `RECIPE_PROVISIONAL` can still produce `CONTINUE` — this is real, reproduced below and closed in this pass (§2). | **Claude has the concept Codex lacks entirely**, but Claude's own implementation of it had the gap this V2 pass closes. |
| **Cost provenance authenticity** | `ModelParameter.source` is a non-empty string check only (`test_weak_provenance_fails_closed` only tests emptiness). Codex's own red team item 5 names this: "a nonempty source string can lie." | `SourceContract` is far richer (admissible source classes, forbidden result-driven selection rules, per-parameter evidence-update rule) but still ultimately bottoms out in free-text fields (`central_provenance`, `population_applicability`) with no binding to an actual dataset fingerprint, artifact hash or validation-state record. | **Both share the same underlying gap** — Claude's is a more elaborate structure sitting on the same syntactic foundation. Hardened in this pass (§8/provenance work) by linking to the existing `EvidenceRegistry` chain-hash shape rather than inventing a new one. |
| **Portfolio interaction** | None. Codex's own red team item 4 names exactly the two-individually-positive-trades problem and proposes "treat CONTINUE as economic eligibility only, then require RISK/Book acceptance" — this is *the same principle* `decision.py`'s existing `PortfolioInteraction` already encodes (`overlap_fraction` scaling), independently arrived at. | Has `PortfolioInteraction` (overlap fraction, residual beta, correlation to book, capital contention) already reducing the incremental effect before the gate runs, and already tested to turn a `CONTINUE` into a `KILL` under high overlap. Not yet integrated with `desk/risk.py`'s hard gross/net/concentration limits — this pass makes that composition explicit and tested (§7). | **Claude already had the mechanism Codex's red team asked for**; the gap is downstream integration, not the concept. |

**Overall verdict.** Codex's engine is a smaller, honest, self-contained
prototype whose main value is as a second, independently-derived opinion on
what the minimum bar for a fail-closed economic gate looks like — and it
confirms, from a different starting point, several of the same conclusions
Wave 1 Claude reached (fail closed on missing frictions, no real-capital mode,
persist-before-Desk, portfolio interaction, provenance skepticism). None of
its concrete code is being cherry-picked wholesale: **no second economic
engine is created.** Where Codex's self-identified weaknesses point at a real
gap in Claude's own package too (cost-shape provenance, joint-scenario
correlation, the missing durable journal, provenance authenticity), those
gaps are closed *inside* `quant.economics` using Claude's existing primitives
(functional cost components, `JointScenarioSet`, `ParameterInventory`), not by
importing Codex's flatter data model.

---

## 2. Work log

### Slice 0 — setup, reading, red team (this commit)
- Verified branch/base, read all authority docs, read Codex branch read-only.
- Read the full `quant.economics` package (18 modules), `desk/{desk,execution,risk}.py`,
  `operations/{registry,readiness,failures}.py`, `book/ledger.py` header,
  `factory/lanes.py`, `science/{inference,formation}.py` (clustering/O4 sections).
- **Key integration finding:** `desk/desk.py` imports nothing from
  `quant.economics`. Only `factory/prioritization.py` (imports `recipe_hash`)
  and `operations/readiness.py` (imports `PAPER_SHADOW_ONLY`) touch the
  package at all. The Wave 1 economics engine is fully built but currently
  **not wired into the live SCAN→VET→SIZE→RISK→FILLS→BOOK session**. This is
  named explicitly rather than papered over; see §10 (Integration) in the
  final deliverable for the scope decision this pass makes about it.
- Confirmed ECON-001's exact numbers against the real shipped constants
  (`quant.desk.execution.ExecutionModel()`, `RESEARCH_ONE_WAY_COST_BPS = 5.0`):
  one-way cost at `max_participation=0.05` is `0.5 + 1.0 + 10.0 = 11.5 bps`,
  matching the mission's reproduction exactly. Confirmed Wave 1 **already**
  wrote an independent discriminating test for this
  (`tests/test_economics_timeline_execution.py::ResearchExecutionConsistencyTest`)
  that imports the real `ExecutionModel`/`RESEARCH_ONE_WAY_COST_BPS`, not a
  synthetic stand-in, and asserts the 6.5 bps understatement and 0.6125%
  ceiling. The genuinely open part of ECON-001 is narrower than "write a
  reproduction": `consistency` is an *optional* parameter to `economic_gate`,
  so nothing forces the check to run before a verdict is trusted downstream.
  Closed in Slice 1 by making the capital/order-eligibility tier (not the raw
  mechanical verdict) fail closed when consistency was never checked.
- Confirmed the red-team item 1 defect is real and reproducible today:
  `economic_gate` computes `authority` from `evidence_label` only and never
  looks at `meue_result.recipe_state`, so a `RECIPE_PROVISIONAL` MEUE
  (uncalibrated coefficients) combined with `EVIDENCE_FORWARD_CONFIRMATION`
  evidence can produce `verdict=CONTINUE, authority=FORWARD_CONFIRMED` — i.e.
  nothing in the returned object currently forces a caller to notice the
  threshold itself was non-authoritative.

### Slice 1 — RECIPE_PROVISIONAL eligibility tier + ECON-001 fail-closed + D07-O4 clustering exposure

Files: `src/quant/economics/states.py`, `src/quant/economics/decision.py`,
`src/quant/economics/__init__.py`, `tests/test_economic_v2_consolidation.py` (new).

- Added a `capital_order_eligibility` tier to `EconomicVerdict`
  (`NOT_ELIGIBLE` / `DEVELOPMENT_SIGNAL_ONLY` /
  `PORTFOLIO_CONSIDERATION_ELIGIBLE`) plus `recipe_state` and
  `capital_order_eligibility_reasons`, computed by a new
  `_capital_order_eligibility()` helper in `decision.py`. **Deliberately does
  not change whether `economic_gate` returns `CONTINUE`** — Wave 1's own
  mechanical verdict (development can proceed before calibration) is
  untouched, and whether a `RECIPE_PROVISIONAL` evaluation *may* ever produce
  a meaningful `CONTINUE` is explicitly left as Blue's ruling (red team 8.1).
  What changed: `CONTINUE` alone can no longer be read as anything beyond a
  development signal unless the recipe is `RECIPE_CONSUMABLE`, the evidence is
  forward-confirmed, the effect estimate's clustering-unit provenance is
  O4-resolved (not undeclared or assumed-independent), and a
  `ResearchExecutionConsistency` check was actually run and passed. This is a
  representation of the current governance gap, not an invented rule — see
  `states.py`'s new docstring block for the reasoning.
- **ECON-001 residual gap closed**: the discriminating reproduction against
  the real shipped constants already existed
  (`test_economics_timeline_execution.py::ResearchExecutionConsistencyTest`,
  confirmed passing, confirmed importing the real `ExecutionModel`/
  `RESEARCH_ONE_WAY_COST_BPS`, not a synthetic stand-in). The actual open part
  was that `consistency` is an optional parameter to `economic_gate`, so a
  verdict could reach `CONTINUE` without the check ever running. Fixed by
  making `capital_order_eligibility` fail closed
  (`RESEARCH_EXECUTION_CONSISTENCY_NOT_VERIFIED`) whenever `consistency is
  None`, and by adding an independent re-derivation of the 6.5 bps
  understatement / 0.6125% ceiling in the new test file that does not import
  `ExecutionCostModel` or `implied_participation_ceiling` at all (arithmetic
  redone by hand from `ExecutionModel`'s raw fields), as a cross-check against
  Wave 1's own reproduction. **Neither `RESEARCH_ONE_WAY_COST_BPS` nor
  `max_participation` was touched** — asserted directly by
  `test_no_new_scientific_constant_was_introduced`.
- **D07-O4 clustering exposure** (red team item 3): added
  `clustering_unit_provenance` to `EffectEstimate` (default
  `CLUSTERING_UNIT_UNDECLARED`), with three recognised states
  (`UNDECLARED` / `O4_UNRESOLVED_ASSUMED_INDEPENDENT` / `O4_RESOLVED_...`).
  Undeclared or O4-unresolved caps eligibility exactly like the other gates
  above; a genuinely unrecognised value is a hard input defect
  (`BLOCKING_INPUT_DEFECT`, mechanical `NO_TRADE`). **Scope discipline: this
  does not touch `src/quant/science/**` at all** — the clustering unit itself
  is that module's frozen-object dependency on O4 and a distinct writer
  domain per the Wave 1 Builder allocation proposal (§6 of
  `CLAUDE_WAVE1_PROTOCOL_PROPOSALS_2026-09-19.md`); this pass only refuses to
  let the *economics* engine treat an unresolved clustering unit as
  equivalent to a resolved one when deciding eligibility.
- All three fixes are additive dataclass fields with safe defaults — zero
  existing call sites needed updating, zero existing tests needed touching.
- New file `tests/test_economic_v2_consolidation.py`: 15 tests, explicit
  RED-then-GREEN pairs per defect (`test_red_*` reproduces the exact
  before-state, `test_green_*` proves the fix), plus one full positive case
  (`test_full_eligibility_requires_recipe_evidence_clustering_and_consistency_
  together`) proving the top eligibility tier is actually reachable, not just
  permanently closed.
- Exported the new `ORDER_ELIGIBILITY_*` / `CLUSTERING_UNIT_*` constants from
  `quant.economics.__init__` for downstream consumers (the journal in the next
  slice, and eventually Desk).

**Tests:** `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
→ 603 passed (588 pre-existing + 15 new), 0 failures, 0 skipped.

### Slice 2 — explicit cost-shape typology

Files: `src/quant/economics/frictions.py`, `src/quant/economics/recipe.py`,
`src/quant/economics/__init__.py`, `tests/economics_fixtures.py`,
`tests/test_economic_v2_consolidation.py`.

- Added an explicit `shape` declaration to `CostComponent`
  (`COST_SHAPES`: `FIXED`, `PER_SHARE`, `PER_NOTIONAL`, `SPREAD_CROSSING`,
  `SQRT_IMPACT`, `NONLINEAR_IMPACT`, `BORROW`, `FINANCING`,
  `TURNOVER_REBALANCE`, `LATENCY_SLIPPAGE_REGIME` — exactly the mission's
  named typology). Undeclared/unrecognised shape is a hard structural
  violation, the same idiom every other `CostComponent` declaration already
  uses.
- Added `verify_shape_declarations()`, wired into `MEUERecipe.evaluate()`
  alongside the pre-existing `verify_dependence_declarations()` (same call
  site, same fail-closed-to-`RECIPE_INVALID` behaviour). It numerically
  probes each component's functional against its declared shape by scaling
  two independent axes — `expected_deployed_exposure` (`Q(theta)`, what
  `gross_value` scales with) and `participation` (what the sqrt-impact shape
  scales with) — because the recipe's cost functionals take a full `theta`,
  not one size scalar, and (as discovered while building the fixture's own
  `MARKET_IMPACT` component) a pure exposure-scaling probe cannot see a
  sqrt-in-participation nonlinearity at all if participation is held fixed.
  `FIXED`/linear/`SQRT_IMPACT` shapes get an exact ratio check;
  `NONLINEAR_IMPACT`/`LATENCY_SLIPPAGE_REGIME` are checked only for not being
  silently constant, since neither claims one closed-form ratio — no
  numerical coefficient is invented for either.
- This directly closes the Codex-identified weakness this pass was asked to
  fix (self red team item 1 / `W1-SELF-001`): "cost amounts are supplied as
  already-computed currency values; the engine does not prove their
  functional dependence on order size." Claude Wave 1's functional-callable
  design already made size-dependence *possible*; this slice makes a
  mismatch between the declared shape and the actual functional
  *mechanically detectable*, with 6 new tests proving both the positive case
  (`fixtures.k_forward_recipe()` — all 4 real components pass) and 3
  independent mislabelling cases (a scaling cost mislabelled `FIXED`, a
  linear-in-participation cost mislabelled `SQRT_IMPACT`, a constant cost
  mislabelled `PER_NOTIONAL`) plus one full end-to-end
  `MEUERecipe.evaluate()` refusal.
- Updated the shared `tests/economics_fixtures.py` (labelled, as its own
  docstring already states, a test fixture with no scientific authority) to
  declare the correct shape on its 4 existing cost components
  (`PER_NOTIONAL` for the two Q-linear fee/exit charges, `SPREAD_CROSSING`
  for the entry crossing charge, `SQRT_IMPACT` for the market-impact
  charge — matching its own pre-existing `formula_statement` docstrings
  exactly). This is the only change to shared Wave 1 test infrastructure in
  this pass, made necessary by tightening a schema all four components
  already satisfied; no existing assertion was altered.

**Tests:** `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
→ 610 passed (588 Wave 1 + 22 this pass), 0 failures.

_(Further slices appended below as they land — checkpoint updated, committed
and pushed after each.)_
