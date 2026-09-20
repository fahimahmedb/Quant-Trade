# CLAUDE ECONOMIC V2 — 2026-09-20

```
BASE_SHA  = b17b381a8fa1f6a24e6cd6f92a090b40627bfe78
FINAL_SHA = branch tip; resolve immutably with `git rev-parse HEAD` (a commit
            cannot embed its own SHA — this document's own commit necessarily
            advances HEAD past whatever value would be written here)
BRANCH    = parallel/claude-economic-v2-2026-09-20
```

Last code commit before this documentation commit: `c52b4359521be4d446592e74c37f282b49c86cdf`.

Role: consolidation Builder for `quant.economics`. Not P0. Not Clock. Not the
scientific-protocol writer (`src/quant/science/**` untouched throughout).

**Branch note.** This session's harness-level git config initially named a
different branch (`claude/economic-v2-consolidation-cl3cnb`), whose remote had
been deleted (`git fetch` reported `[deleted]`). `parallel/claude-economic-v2-
2026-09-20` exists, matched the mission's stated base exactly at session
start, and fits this repository's live `parallel/*` wave-naming convention.
Proceeded on the mission-specified branch; see `handoff/
CLAUDE_ECONOMIC_V2_LIVE.md` Slice 0 for the full verification trail.

Full working log, written incrementally per slice with exact test counts at
each step: `handoff/CLAUDE_ECONOMIC_V2_LIVE.md`. This document is the
end-of-mission summary; that one is the evidence.

---

## 1. Architecture, before and after

**Before (base commit).** Wave 1 had built a genuinely sophisticated,
D09-cited economics package (`states, fingerprint, coordinate, parameters,
frictions, capacity, scenarios, margin, partition, theta, recipe, decision,
consistency, opening, timeline, sizing` — 18 modules) implementing the full
North Star chain mechanically and outcome-blind. But:

* `economic_gate`'s `authority` field followed evidence label alone, never
  recipe consumability — a `RECIPE_PROVISIONAL` (uncalibrated) evaluation
  could produce `CONTINUE` indistinguishable from an authoritative one
  (Wave 1's own red team item 8.1, explicitly flagged as needing a ruling).
* The ECON-001 consistency check (`consistency.py`) existed and was already
  correctly wired as an *optional* parameter to `economic_gate` — nothing
  forced it to run before a verdict was trusted.
* No cost component declared *how* it scaled with size beyond an ad hoc
  `Dependence` flag set — the same class of gap Codex's parallel engine
  admitted to (self red team item 1).
* Provenance bottomed out in free-text fields with no binding to anything
  checkable (Wave 1's own red team item 4).
* No joint-adverse-scenario category discipline beyond "at least one adverse
  scenario must perturb each model-risk parameter" — nothing required the
  mission's five named stress categories to be addressed or excluded.
* No durable, conflict-aware assessment journal existed at all (Wave 1 WS31
  and Codex's own top-priority gap, independently).
* **`src/quant/desk/desk.py` imported nothing from `quant.economics`.** The
  live SCAN→VET→SIZE→RISK→FILLS→BOOK session ran on its own older
  `ExecutionModel`/`RiskLimits` logic, entirely disconnected from the
  economics package. Only `factory/prioritization.py` (a hash utility) and
  `operations/readiness.py` (a constant) touched the package at all.

**After (this branch).** The chain-of-custody gaps above are closed inside
`quant.economics` itself, additively, with the existing architecture's own
idioms (a declared-and-probed functional, a modelled-or-authorised-zero
coverage discipline, an append-only idempotent JSONL ledger) rather than a
parallel structure:

* `EconomicVerdict` now carries `recipe_state` and a `capital_order_eligibility`
  tier (`NOT_ELIGIBLE` / `DEVELOPMENT_SIGNAL_ONLY` /
  `PORTFOLIO_CONSIDERATION_ELIGIBLE`), computed from recipe consumability,
  evidence maturity, clustering-unit resolution and verified cost
  consistency together — never from evidence label alone. `CONTINUE` itself
  is unchanged.
* `CostComponent.shape` (explicit typology) is probed numerically against
  the component's own functional (`verify_shape_declarations`).
* `ProvenanceBinding` makes a `PROVENANCE_CALIBRATED` claim checkable
  (dataset fingerprint/artifact hash/version/as_of/authority/validation
  state), not merely asserted.
* `JointScenarioSet.category_coverage_violations()` requires each of the
  five named adverse categories addressed or explicitly excluded.
* `EconomicAssessmentJournal` (new module) gives every assessment a durable,
  replay-safe, conflict-detecting home.
* The disconnection between `quant.economics` and the live Desk session is
  **named, not fixed** — see §10.

Every one of the additions above is wired through the *existing*
consumability/eligibility machinery (`MEUERecipe._consumability`,
`economic_gate`'s eligibility computation) rather than a second decision
path, and every one defaults to non-blocking (a note/eligibility cap, not a
new `RECIPE_INVALID`) specifically so it did not require rewriting Wave 1's
existing ~75-test suite wholesale — two exceptions needed one fixture file
and one existing test updated (§3, ECON-CS and ECON-PROV rows).

---

## 2. Claude Wave 1 vs Codex — comparison summary

Full point-by-point table in `handoff/CLAUDE_ECONOMIC_V2_LIVE.md` §1. Summary
verdict: Codex's ~200-line single-file engine is an honest, bounded, correctly
self-critical prototype, not a competing architecture at comparable scope. It
independently reached several of the same conclusions Wave 1 did (fail closed
on missing frictions, no real-capital mode, persist-before-Desk, portfolio
interaction as an eligibility question not an order). Its most valuable
contribution was its own red team, which named exactly the three gaps this
pass closed inside Claude's package (cost-shape provenance, provenance
authenticity, the missing journal) — its code was not cherry-picked; its
*findings* were, and closed using Wave 1's own idioms. **No second economic
engine was created.**

Codex was decisively behind on: D09/EC1 coordinate binding (silent on
whether its scalar effect is even the frozen estimand), anti-double-counting
structure (its own admitted gaps, `W1-SELF-002`/`003`), and joint-scenario
correlation representation (a single scalar `effect_uncertainty`).

---

## 3. Defects

| ID | Status | Note |
|---|---|---|
| ECON-001 (`RESEARCH_COST_ASSUMPTION_UNDERSTATES_MODELLED_EXECUTION`) | **Reproduced (independently) + residual gap fixed** | Wave 1 had already reproduced the 6.5 bps / 0.6125% defect against real shipped constants (`test_economics_timeline_execution.py::ResearchExecutionConsistencyTest`) and wired an *optional* consistency check. This pass added an independent hand-rederivation with no dependency on `consistency.py` (`Econ001FailClosedTest.test_red_independent_rederivation...`), and closed the fail-open gap: `capital_order_eligibility` now fails closed (`RESEARCH_EXECUTION_CONSISTENCY_NOT_VERIFIED`) whenever the check was never run or failed. **Neither `RESEARCH_ONE_WAY_COST_BPS` nor `max_participation` was moved** — asserted directly by a test. Which constant should move, if either, remains Blue's (§5). |
| Wave 1 red team 8.1 (`RECIPE_PROVISIONAL` can produce `CONTINUE`) | **Fixed, without ruling on the underlying question** | `CONTINUE` is unchanged (still mechanically reachable on a provisional recipe, by original Wave 1 design, for development). `capital_order_eligibility` now makes it structurally impossible to read that `CONTINUE` as anything beyond a development signal. Whether a provisional recipe *should* ever produce `CONTINUE` at all remains Blue's (§5), per the mission's explicit instruction not to invent that ruling. |
| Wave 1 red team item 3 (clustering unit trusts an unfrozen O4) | **Exposed, not fixed in `science/`** | `EffectEstimate.clustering_unit_provenance` (new) caps eligibility when undeclared or explicitly O4-unresolved. `src/quant/science/**` (a distinct writer domain) was not touched. |
| Wave 1 red team item 4 / Codex self red team item 5 (provenance is declared, not proved) | **Fixed** | `ProvenanceBinding` + `ParameterInventory.bind_provenance()`; a `PROVENANCE_CALIBRATED` claim without one keeps a recipe `RECIPE_PROVISIONAL`. |
| Codex self red team item 1 (`W1-SELF-001`, cost amount doesn't prove size dependence) | **Fixed** | `CostComponent.shape` + `verify_shape_declarations`, probing the real functional. |
| Codex self red team item 2 (`W1-SELF-002`, scalar uncertainty can't represent correlated joint scenarios) | **Mechanism hardened, values not authored** | `JointScenarioSet.category_coverage_violations()` requires the five named categories addressed-or-excluded; Claude's pre-existing `JointScenarioSet`/`m_economic` machinery already represents joint (not marginal) scenarios, which is architecturally ahead of Codex's own scalar subtraction. |
| Codex self red team item 3 / Wave 1 WS31 (no durable assessment journal) | **Fixed** | `EconomicAssessmentJournal` (new). |
| Codex self red team item 4 (no portfolio interaction) | **Already present in Claude's engine; now integration-tested** | `PortfolioInteraction` predates this pass; `test_economic_portfolio_integration.py` proves the eligibility/approval separation against the real `desk.risk`/`book.ledger`. |
| ECON-002 (`QUOTE_STALENESS_LIMIT_HAS_NO_PROVENANCE`) | **Still open** | Out of this pass's scope (`operations/failures.check_quote`'s 300s default); flagged by Wave 1, not touched here. |
| `quant.economics` not wired into `desk.py`'s live session | **Named, not fixed** | See §10. Pre-existing at base, not introduced by this pass. |

---

## 4. Tests

```
PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"
-> 640 passed, 0 failed, 0 errors (588 Wave 1 baseline + 52 this pass)
```

New/updated files: `tests/test_economic_v2_consolidation.py` (38: recipe
eligibility, ECON-001 fail-closed, clustering/O4, cost-shape typology,
provenance authenticity, joint-scenario categories),
`tests/test_economic_assessment_journal.py` (8: duplicate append, same-id
conflict, restart, crash-after-assessment-before-Desk replay, torn append,
fingerprint stability/sensitivity), `tests/test_economic_portfolio_integration.py`
(6: eligibility-vs-approval against real `desk.risk`/`book.ledger`, sleeve
attribution, capacity/RISK composition, overlap). `tests/economics_fixtures.py`
and one test in `tests/test_economics_engine.py` updated minimally (shape
declarations, provenance binding) to satisfy deliberately strengthened
preconditions their own assertions already expected to hold — no existing
assertion weakened or removed. Every red-team-named failure mode in the
mission's test list is covered: negative economics despite significance
(pre-existing, re-verified), cost scaling, capacity clipping (pre-existing),
double counting (pre-existing partition, re-verified), joint scenario,
provisional authority, portfolio interaction, same-id conflict, restart/
idempotence, torn journal, provenance forgery/incomplete provenance, no real
capital authority (pre-existing, re-verified).

`test_sec_form4_capture.py` (P0-adjacent unit tests over synthetic fixtures,
no reservoir access) ran as part of the full suite with no code path from
this pass touching it.

---

## 5. Decisions requiring Blue

Unchanged from Wave 1 except where noted; this pass added no new items to
this list, per its own scope discipline:

1. Whether `RESEARCH_ONE_WAY_COST_BPS` rises or the desk's `max_participation`
   falls to close ECON-001's underlying inconsistency (this pass made the
   absence of a decision fail closed on eligibility; it did not decide it).
2. Whether a `RECIPE_PROVISIONAL` evaluation may ever justify more than a
   development signal (this pass made the current answer — "no, capped at
   `DEVELOPMENT_SIGNAL_ONLY`" — explicit and structural, not a ruling that it
   must stay that way).
3. D07 O1–O4 selections and the unenumerated O2/O3 admissible sets; the D05-A
   metric list/strata/stopping rule; α/power/one- vs two-sided/sequential
   stopping/futility/variance-method authority; every D19 terminal-treatment
   option and adverse perturbation set; numerical Form 4 cost coefficients,
   uncertainty envelopes and joint adverse scenario *values* (the mechanism
   for the latter is now built — §3 — the numbers are not); promotion of
   `M_economic` from freeze candidate to authority (all carried from Wave 1,
   untouched).
4. **New, narrow:** whether the five named joint-adverse-scenario categories
   this pass added (`ADVERSE_SCENARIO_CATEGORIES`) are the right taxonomy, or
   need a sixth. The mechanism enforces whatever list Blue confirms; this
   pass did not claim the list itself is authoritative beyond the mission's
   own naming.

---

## 6. P0 attestation

```
P0_RESERVOIR_ACCESSED   = FALSE
P0_PROTOCOL_MUTATED     = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
T0_TOUCHED              = FALSE
```

Supporting facts: `git diff --stat b17b381a8fa1f6a24e6cd6f92a090b40627bfe78
c52b4359521be4d446592e74c37f282b49c86cdf` (last code commit) touches only
`src/quant/economics/**`, four `tests/` files, and
`handoff/`. No file under `src/quant/dataplane/sec/`, `deploy/`,
`src/quant/clock.py` or `scripts/quant.py` appears in that diff (verified by
direct `grep` against the diff, not by assertion). The Codex branch
(`parallel/codex-wave1-economic-system-2026-09-19`) was read exclusively via
`git show <sha>:<path>` against its exact cited tip
(`738a5879ef8634d3e08c717a2d439632fe64e1ff`, confirmed by `git rev-parse`);
the working tree never left this branch and nothing from it was merged or
cherry-picked. Every `EconomicVerdict` still carries `PAPER_SHADOW_ONLY`
(unchanged); no path in this pass's new code constructs or authorises a
`REAL` capital mode.

---

## 7. Top contributions by expected net economic value

1. **The durable assessment journal.** The one gap Wave 1 and Codex
   independently ranked highest; without it, every other check in this
   package is advisory until Desk acts on it, because a crash between
   assessment and Desk had no recorded truth to resume from.
2. **`capital_order_eligibility`.** Closes the one defect in this pass with
   real deployment relevance if missed: a red-team-identified path (item
   8.1) by which an uncalibrated threshold's `CONTINUE` could be
   misread as authoritative downstream.
3. **ECON-001's eligibility fail-close.** The consistency check existed but
   was skippable; a lane could reach the top eligibility tier without ever
   having its research-vs-execution cost gap checked at all.
4. **Cost-shape verification.** Turns "the functional could in principle
   depend on size correctly" into "a mismatch between claimed and actual
   scaling is mechanically caught," closing Codex's own top self-identified
   weakness.
5. **Provenance binding.** Same treatment for "this parameter is calibrated":
   a label is no longer sufficient on its own to reach `RECIPE_CONSUMABLE`.
6. **Joint adverse scenario category coverage.** Turns five named stress
   categories from a checklist in a handoff document into a mechanically
   enforced modelled-or-excluded requirement.
7. **Portfolio integration tests.** Lowest code-risk item here (no
   production change), but closes the gap between "the mechanism exists"
   and "it is proven to compose with the real Desk/Book objects."
8. **Naming, not fixing, the `desk.py`/`quant.economics` disconnection.**
   Negative-value avoided: wiring the full economics gate into the live
   session would have been the highest-risk change available this pass, for
   a package whose own numbers are still provisional — see §10.

---

## 8. §10 — Integration (why `desk.py` is not wired this pass)

`quant.economics` reuses the Research Factory's evidence vocabulary
(`EVIDENCE_*` labels shared with `operations/registry.EvidenceRegistry`),
the Desk's own `ExecutionModel` (via `ExecutionCostModel.from_execution_model`,
never duplicating its state), and `book.ledger.Ledger`/`desk.risk` directly in
this pass's integration tests (§6 of the live checkpoint) — no parallel
Economic System was created, and the one honestly missing piece (`desk.py`
calling `economic_gate` in its live `SCAN→VET→SIZE→RISK→FILLS→BOOK` session)
predates this pass and was deliberately not attempted now: every recipe in
this codebase is still `RECIPE_PROVISIONAL` (no calibrated Form 4 coefficient
exists anywhere), so wiring it into the live paper/shadow session today would
either (a) gate real sessions on a `capital_order_eligibility` that can never
exceed `DEVELOPMENT_SIGNAL_ONLY` yet, making the wiring inert, or (b) invite
exactly the "quietly relax a threshold to make it reachable" failure mode
Wave 1's Builder-allocation proposal was written to prevent, under this
pass's time budget and without Blue's calibration authority. The correct
future hook is named, not built: `factory/lanes.py`'s declared lanes and
`desk.py`'s `_run_strategy` SIZE stage are the two call sites a future pass
should connect through `EconomicAssessmentJournal`, once Blue supplies
calibrated parameters and the ECON-001 ruling above. If Clock integration
is ever needed for scheduling that connection, `src/quant/clock.py` remains
untouched here per the P0/Clock boundary.

---

```
P0_RESERVOIR_ACCESSED   = FALSE
P0_PROTOCOL_MUTATED     = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
T0_TOUCHED              = FALSE
```

`git status` clean; pushed to `origin/parallel/claude-economic-v2-2026-09-20`
at this document's own commit (`git rev-parse HEAD`). Nothing merged. STOP.
