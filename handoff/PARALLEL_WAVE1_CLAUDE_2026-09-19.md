# PARALLEL WAVE 1 — CLAUDE track

**Branch:** `parallel/claude-wave1-economic-system-2026-09-19`
**Role:** Builder / Quant Engineer, parallel track. Astra owns P0 SEC/Form-4 pre-`t0` exclusively.
**Terminal objective this wave serves:** net economic gain after real frictions.

Wave 1 built the economic layer that turns a scientific effect into an economic
decision, made the already-closed protocol semantics executable, and left every
open scientific decision to Blue. The single most useful sentence in this report is
that `quant.economics` asserts **no numerical Form 4 cost coefficient**: the recipe
is complete and hash-addressable, and it reports `RECIPE_PROVISIONAL` rather than
pretending the calibration exists.

---

## 1. Matrix — 35 workstreams

Commit SHAs are short SHAs on this branch. "Tests" counts tests added by this wave
for that workstream, in the named file.

| ID | Workstream | Blue gate | Status | Files / artifacts | Tests | Commit | New findings | Remaining blocker | Next action |
|---|---|---|---|---|---|---|---|---|---|
| 1 | D09 Economic Core restant | GO WITH FIREWALL | TESTED | `src/quant/economics/{states,fingerprint,coordinate,parameters,frictions,value,scenarios,margin,partition,theta,recipe}.py` | 75 (`test_economics_engine.py`) | `6fe1de53` | `M_economic` (12.6 bps on the fixture) exceeds `BEEE` (9.8 bps) purely because two coefficients are uncalibrated — the envelope contract's "width of uncertainty is economically meaningful" is quantitatively dominant, not a footnote | numerical parameter values, envelopes and the promotion of the §9 margin functional from freeze candidate to authority are Blue's | Blue supplies per-parameter source contracts; then `instantiate()` and re-run `evaluate()` for a consumable MEUE |
| 2 | Modèle complet de frictions | GO | TESTED | `economics/frictions.py`, `economics/opening.py` | included above + 41 (`test_economics_timeline_execution.py`) | `6fe1de53`, `f1a6713c` | `NO_HIDDEN_CONSERVATISM_INSIDE_K_FORWARD` is enforceable structurally: an upper-quantile estimator or a non-zero markup fails the recipe | "latency" is not an admitted class in the frozen F1–F7 inventory; it currently lives inside F3 opening slippage. Adding a class is a governed version consequence | Blue decides whether latency becomes its own cost class or stays inside F3 |
| 3 | Capacity model | GO | TESTED | `economics/capacity.py` | included in 75 | `6fe1de53` | a name with no liquidity reference is granted **zero**, not unlimited capacity; uneven clipping is reported as a new policy version rather than a smaller position | ADV/liquidity references for the Form 4 universe are not available pre-`t0` | wire `CapacityLimit` to the permitted pre-outcome panel lookback once a universe exists |
| 4 | Signal → ordre → PnL net | GO WITH FIREWALL | TESTED | `economics/timeline.py` | 41 | `f1a6713c` | dates and timestamps must be normalised to one UTC scale before comparison, otherwise a bare session date slips past a same-day timestamp and the lookahead is invisible | none for the event lane; V1's session timeline already held | use `CausalEventLedger` as the persistence path when the Form 4 lane runs |
| 5 | Portfolio construction / sizing | GO | TESTED | `economics/sizing.py` | included in 41 | `f1a6713c` | binding risk approval to a hash of the **final** post-transform plan catches approval of a pre-scale portfolio, which no amount of reviewing catches | factor/sector caps not added; V1 `desk/risk.py` enforces gross, net and per-name only | add a declared sector/factor cap as a named transform in `SizingPlan` |
| 6 | Critères économiques continue / kill | GO WITH FIREWALL | TESTED | `economics/decision.py` | included in 75 | `6fe1de53` | a p-value of 1e-9 with the whole interval below MEUE returns `KILL`; portfolio overlap alone can turn `CONTINUE` into `KILL` | the gate accepts `RECIPE_PROVISIONAL` and can return `CONTINUE` with `authority=DEVELOPMENT_EVIDENCE_ONLY` — see red team §8.1 | Blue decides whether a provisional recipe may ever produce `CONTINUE` |
| 7 | Execution simulator | GO | TESTED | `economics/opening.py` | included in 41 | `f1a6713c` | measuring execution loss against the prior close charges the overnight gap — market return, part of `T_j` — as slippage; the gap is now reported and labelled, never charged | V1 `desk/execution.py` left unchanged on purpose (see defect ECON-001) | Blue chooses the ECON-001 resolution before the two models are reconciled |
| 8 | Passive Forward Market Recorder | GO | TESTED | `dataplane/forward_recorder.py` | 33 (`test_dataplane_forward_lane.py`) | `6f8531b9` | forward-only in wall clock plus immutable plus `as_of` is enough to make later evidence out-of-sample *by construction*; a vendor restatement becomes a visible conflict record instead of silently replacing history | nothing is being recorded yet: scheduling it needs `clock.py`, which is fingerprint-critical this wave | start recording on any schedule outside the clock; every unrecorded session is permanently lost forward evidence (see §7) |
| 9 | Données externes non-Form-4 | GO WITH FIREWALL | DESIGNED | `dataplane/admissibility.py`, existing `dataplane/registry.py` | included in 33 | `6f8531b9` | admissibility is decidable from provenance and use history alone, before any value is read | capturing a new external source needs network/licence authority not granted to this branch | Blue names the admissible non-Form-4 sources; ingestion follows the existing registry path |
| 10 | Parser Form-4 downstream | GO WITH FIREWALL | TESTED | `dataplane/form4_parse.py` | included in 33 | `6f8531b9` | `periodOfReport` is not the public-observability instant and the parser refuses to supply one; a footnote-only price is a state, never 0.0 | none — the parser is a pure function over bytes with no filesystem access, so it cannot reach the P0 reservoir | point it at the reservoir only when Astra's firewall permits, via an explicit caller |
| 11 | Qualification/admissibilité downstream | GO WITH FIREWALL | TESTED | `dataplane/admissibility.py`, `science/eligibility.py` | included in 33 and 59 | `6f8531b9`, `3ba24cea` | the use ledger is a one-way ratchet on dataset **version**: a refreshed fingerprint is new evidence, a re-fit version is not | none | record every existing lane's dataset use so the ratchet reflects history |
| 12 | D07 Final Geometry | GO WITH FIREWALL | DESIGNED | `science/formation.py`, `handoff/CLAUDE_WAVE1_PROTOCOL_PROPOSALS_2026-09-19.md` | 59 (`test_science_protocol.py`) | `3ba24cea`, `dac84c9d` | a weekend EDGAR date can straddle the ten-session window boundary, so **formation event count is claim-design-sensitive** and belongs to D05-B; also the O2 ordering demonstrably changes which filing is the trigger | O1, O2, O3 and O4 selections are Blue's; the admissible O2 and O3 *sets* are not enumerated by D07 | Blue selects, or enumerates the sets; the engine consumes the choice unchanged |
| 13 | D05 discharge conditions | GO WITH FIREWALL | DESIGNED | `science/invariance.py` | included in 59 | `3ba24cea` | the D07 §5 invariance test is now mechanical, so candidate metrics can be classified **before** a geometry is chosen | the metric list, strata and stopping rule are D05-A freeze objects | classify every named candidate metric with `design_invariance`, publish the table, then open the freeze |
| 14 | D05-B / D08 protocol preparation | GO WITH FIREWALL | DESIGNED | `science/inference.py`, `science/nulls.py` | included in 59 | `3ba24cea` | the clustering unit is defined by O4, so the variance object cannot be frozen before O4 | α, power, one- vs two-sided, sequential stopping, futility/equivalence, and which variance method is authoritative | Blue freezes those five; the code already supplies the estimator and both variance methods |
| 15 | D19 specification | GO WITH FIREWALL | DESIGNED | routing in `science/formation.py`; options in the proposals artifact | included in 59 | `3ba24cea`, `dac84c9d` | every terminal-treatment option changes the sign or magnitude of a realised outcome, so none can be picked as a default | the treatment set and the adverse perturbation thresholds are Blue's | Blue specifies; the engine already refuses to substitute a payoff |
| 16 | Route A vs Route B | WAIT / DO NOT REOPEN | WAIT | — | — | — | untouched | — | none |
| 17 | Research Factory — familles indépendantes | GO | TESTED | `factory/families.py` | 23 (`test_factory_families.py`) | `52f90363` | declared independence must be *checked*: the module reports `FAMILIES_EMPIRICALLY_COLLINEAR` when two families' realised score vectors agree despite differing on paper | the lane is not in `lanes.lane_definitions`, because that changes what `clock.py` schedules | add the lane when `clock.py` is unfrozen; the dispatch and grid are ready |
| 18 | Hypothesis scouting / littérature | GO | DESIGNED | mechanism statement in `factory/families.py` | included in 23 | `dac84c9d` | — | no literature search performed: this branch assumed no authority to fetch and cite external sources | Blue authorises a source-search scope; the per-parameter source contract structure already exists |
| 19 | Historical exploratory research | GO | TESTED | `scripts/explore_peer_lead_lag.py`, `handoff/CLAUDE_WAVE1_EXPLORATION_PEER_LEAD_LAG_2026-09-19.json` | included in 23 | `dac84c9d` | **0 of 48** peer lead-lag expressions clear the multiplicity threshold (|t| ≥ 3.434); best |t| = 0.779, beta 0.024. A negative result, recorded rather than re-gridded | none | do not promote; the family stays explored-and-rejected unless the mechanism is restated |
| 20 | Benchmarks / null models | GO WITH FIREWALL | TESTED | `science/nulls.py` | included in 59 | `3ba24cea` | a placebo offset inside the true exposure window shares its returns and understates the null spread, so those offsets are refused by name | matched-control and sector/factor-neutral nulls not built; SPY-relative is already the primitive | add matched controls when the Form 4 universe exists |
| 21 | Statistical decision framework | GO WITH FIREWALL | TESTED | `science/inference.py` | included in 59 | `3ba24cea` | correctly clustering overlapping exposures widens the interval measurably — the "free t-statistic" EC1 warns about is reproducible in a test | sequential rules and futility boundaries are Blue's (WS14) | as WS14 |
| 22 | Robustness methodology | GO WITH FIREWALL | IMPLEMENTED | `science/invariance.py`, `science/inference.py` (two variance methods), `science/regimes.py` | included in 59 | `3ba24cea` | the invariance harness generalises to any perturbation set, not only D07 dimensions | window, universe and outlier perturbation sets not yet declared | declare those sets and run them through the same harness |
| 23 | Regime / market-state methodology | GO WITH FIREWALL | TESTED | `science/regimes.py` | included in 59 | `3ba24cea` | a partition declared at or after outcome observation is refused, and the pooled estimate is the headline: `BEST_REGIME_IS_NOT_THE_RESULT` | no regime partition declared yet for any lane | declare one before the first forward window, not after |
| 24 | Economic falsifiers | GO WITH FIREWALL | TESTED | `economics/consistency.py`, `economics/decision.py`, `economics/timeline.py` | included in 41 and 75 | `f1a6713c` | four falsifiers now fire in code: research cheaper than execution, net-of-friction returns fed into a gross coordinate, overnight gap charged as cost, and an effect interval entirely below MEUE | — | run them against every lane before promotion |
| 25 | Capital-readiness framework V3 | GO | TESTED | `operations/readiness.py` | 47 (`test_operations.py`) | `52f90363` | reporting the **weakest** gate rather than an average is what stops strong statistics covering for absent capacity | no lane has evidence for all five gates | assess the existing V1 lanes against the five gates |
| 26 | Paper/shadow execution architecture | GO | IMPLEMENTED | `operations/failures.py` (order ledger, reconciliation) on top of existing V1 desk/book | included in 47 | `52f90363` | after an outage the honest state is `RECONCILIATION_UNKNOWN`; a system that guesses books a position it does not have | the ledger is not yet wired into `desk/desk.py` | wire it at the FILLS stage |
| 27 | Monitoring post-deployment | GO | TESTED | `operations/monitoring.py` | included in 47 | `52f90363` | a retirement rule declared after the window it judges is refused — deciding what counts as decay afterwards is a negotiation with a losing position | no deployed lane to monitor | declare a retirement rule at the moment any lane goes to shadow |
| 28 | Research prioritization | GO WITH FIREWALL | TESTED | `factory/prioritization.py` | included in 23 | `52f90363` | prioritising by what the reservoir seems to contain is the same leak as reading it; `P0_RESERVOIR_IS_NEVER_A_PRIORITY_SIGNAL` is enforced on the input classes | — | run the current candidate list through it |
| 29 | Builder allocation | GO | DESIGNED | proposals artifact §6 | — | `dac84c9d` | the economic engine and the scientific protocol need different writers: they are the two objects that can be traded off against each other | Blue's to adopt | adopt or amend the one-writer-per-domain table |
| 30 | Red Team méthodologique | GO | IMPLEMENTED | §8 of this report; adversarial tests throughout | 278 total, most of them refusals | this commit | eight self-found weaknesses in this wave's own work, listed in §8 | items 8.1 and 8.3 need Blue decisions | Blue rules on 8.1; O4 closes 8.3 |
| 31 | Evidence / experiment registry | GO | TESTED | `operations/registry.py` | included in 47 | `7e90a9af` | a partial provenance chain looks like evidence and is worse than none, so an incomplete record is refused and journaled | not yet populated from the existing V1 research history | backfill the existing lane results as `DEVELOPMENT` records |
| 32 | Economic dashboard minimal | GO — LOW PRIORITY | IMPLEMENTED | `scripts/economic_dashboard.py` | 2 (in `test_operations.py`) | `7e90a9af` | research cost and expected net economic value print as `UNAVAILABLE`; filling those gaps with plausible numbers is the most expensive kind of cosmetic | registry not yet populated | backfill, then read it |
| 33 | Broker/API sandbox | GO | BLOCKED | — | — | — | — | needs external broker credentials and network egress authorisation; neither is granted to this branch, and a sandbox account is an outward-facing action | project owner provisions a paper account and authorises egress |
| 34 | Operational failure modelling | GO | TESTED | `operations/failures.py` | included in 47 | `52f90363` | the write-ahead reservation is what makes a crash between submit and record safe: on restart the id is reserved and the resubmission is suppressed instead of doubling the exposure and its frictions | `check_quote`'s 300-second default has no provenance — the same class of assumed parameter as ECON-001 | declare a per-venue staleness limit with provenance |
| 35 | Opportunity-cost review | GO — VERY HIGH PRIORITY | IMPLEMENTED | §7 of this report | — | this commit | the two irreversible costs this wave incurred and the one it is still incurring every day are named in §7 | — | act on §7's single recommendation |

---

## 2. Base, branch, tip

```
BASE_SHA  = 8d5dbb41559c4716e94d5290b6ae979a8b96143c
FINAL_SHA = dac84c9d  (last code commit; this documentation commit is the branch tip)
BRANCH    = parallel/claude-wave1-economic-system-2026-09-19
```

Commits, in order:

| SHA | Subject |
|---|---|
| `6fe1de53` | `economic:` executable MEUE recipe engine (D09 Route-B mini-core) |
| `f1a6713c` | `execution:` event causal timeline, opening-regime fills, economic sizing |
| `6f8531b9` | `data:` forward recorder, Form 4 structure extraction, dataset admissibility |
| `3ba24cea` | `protocol:` closed D07 semantics executable, D05-A invariance test, ratio inference |
| `52f90363` | `research:` second independent family, prioritisation, operational failure modelling |
| `7e90a9af` | `evidence:` minimal economic dashboard over the evidence registry |
| `dac84c9d` | `research:` exploratory run of the peer lead-lag family, and protocol proposals |

No merge, no cherry-pick, no force-push. The Codex branch was not read.

---

## 3. Tests executed

```
PYTHONPATH=src python3 -m unittest discover -s tests      -> 588 passed
python3 scripts/demo_quant_system.py                      -> 35/35 checks passed
python3 scripts/generate_schemas.py --check               -> schemas checked
python3 scripts/explore_peer_lead_lag.py                  -> 48 expressions, 0 clear |t|>=3.434
python3 scripts/economic_dashboard.py --evidence <path>    -> renders, UNAVAILABLE where unrecorded
```

278 tests added this wave (310 → 588). By file:

| File | Tests | Covers |
|---|---|---|
| `tests/test_economics_engine.py` | 75 | coordinate gate, parameter inventory, K_forward, BEEE roots, joint scenarios, margin, partition, recipe assembly, theta ordering, capacity, economic gate |
| `tests/test_economics_timeline_execution.py` | 41 | causal timeline, net-P&L decomposition, idempotent event ledger, opening fills, research/execution consistency, sizing |
| `tests/test_dataplane_forward_lane.py` | 33 | forward recorder, Form 4 parsing, admissibility ratchet |
| `tests/test_science_protocol.py` | 59 | eligibility, formation semantics, exposure intervals, design invariance, ratio inference, nulls, regimes |
| `tests/test_operations.py` | 47 | quotes/bars, order ledger, reconciliation, readiness, monitoring, evidence registry, dashboard |
| `tests/test_factory_families.py` | 23 | peer lead-lag signal, independence, declared lane, prioritisation |
| `tests/economics_fixtures.py` | — | illustrative recipe, labelled as having no scientific authority |

The tests that matter are the refusals. A representative sample, each of which
fails if the corresponding rule is quietly dropped:
`WINDOW_EXPIRY_PRECEDES_SESSION_ADDITIONS`,
`OMITTED_COST_IS_NOT_IMPLICIT_ZERO`,
`NO_HIDDEN_CONSERVATISM_INSIDE_K_FORWARD`,
`BEEE_QUOTIENT_REQUIRES_AFFINE_COST_INDEPENDENCE`,
`FRICTION_MARGIN_DOUBLE_COUNT`,
`NO_SIZE_SEARCH_TO_MAKE_MEUE_ATTAINABLE`,
`CAPACITY_CLIPPING_THAT_CHANGES_RELATIVE_WEIGHTS_IS_NEW_POLICY_VERSION`,
`LOOKAHEAD_INPUT_NOT_YET_AVAILABLE`,
`OPEN_EXECUTION_COST_MUST_NOT_DOUBLE_COUNT_MARKET_RETURN`,
`RISK_APPROVAL_MUST_DESCRIBE_FINAL_PORTFOLIO`,
`HISTORICAL_EVIDENCE_IS_NOT_INDEPENDENT_CONFIRMATION`,
`POST_HOC_REGIME_SELECTION_REFUSED`,
`P0_RESERVOIR_IS_NEVER_A_PRIORITY_SIGNAL`,
`DUPLICATE_ORDER_SUPPRESSED`,
`RECONCILIATION_UNKNOWN`.

---

## 4. New datasets and provenance

**None ingested.** No market data was fetched, no external source was contacted,
and no dataset was added to `var/dataset_registry.json`.

What changed around data:

* a new persistent *kind* exists — the forward observation store
  (`dataplane/forward_recorder.py`) — with per-record source and source
  fingerprint required, content addressing, and per-session seals. It currently
  holds zero observations, which §7 treats as the wave's live cost.
* `us_sector_etf_daily@sha256:f108a6f4…` was read for the exploratory run, on the
  DISCOVERY window only. Provenance unchanged: operator-supplied export already
  committed to the repository, point-in-time semantics as registered. Its
  multiplicity budget is now 84 declared trials (36 pre-existing + 48 declared
  here).
* synthetic Form 4 fixtures exist only inside `tests/`, with invented CIKs, and
  are labelled as fixtures.

---

## 5. New research families

One: **`peer_lead_lag`** — cross-asset information diffusion.

* **Mechanism.** Sectors share factors but absorb information at different speeds.
  A name that has not moved with its most correlated peers either catches up
  (momentum direction) or the peers overreacted (reversal direction).
* **Why it is structurally independent, not a re-roll.** The score never reads the
  asset's own return. The existing family is entirely built from the asset's own
  cross-sectionally demeaned return. Different input, different story. Declared on
  named axes in `factory/families.py` and then checked against the other family's
  realised score vectors.
* **One design detail that carries the honesty.** Peers are selected on a
  correlation window that ends *before* the signal window opens. A test perturbs
  only the signal window and asserts the selected peer sets are unchanged while the
  scores move.
* **Result.** Explored and not promoted: 0 of 48 declared expressions clear the
  multiplicity-adjusted threshold on DISCOVERY. Best |t| = 0.779, net 12.5% over
  the window, market beta 0.024. Labelled `EXPLORATION`,
  `is_independent_confirmation = false`.

---

## 6. New defects found

### ECON-001 — `RESEARCH_COST_ASSUMPTION_UNDERSTATES_MODELLED_EXECUTION`

**Where.** `src/quant/desk/execution.py:19-22` and `src/quant/factory/lanes.py:22`.

**Claim in the code.** "The desk model below is calibrated to land at or under
this, so research evidence is conservative relative to modelled execution rather
than flattering."

**Reproduction.** From the shipped coefficients, one-way desk cost is
`commission + half_spread + impact_at_full * sqrt(participation / max_participation)`
`= 0.5 + 1.0 + 10.0 * sqrt(p / 0.05)`. At the desk's own `max_participation = 0.05`
that is **11.5 bps** against a research assumption of **5.0 bps** — a 6.5 bps
understatement. The assumption is only covered below **p = 0.6125 %** of ADV, which
is 8.2× below the desk limit. The 2× cost stress test in `factory/evaluate.py`
reaches 10 bps and does not cover it either.

**Second half of the defect.** `RESEARCH_ONE_WAY_COST_BPS` is never imported
anywhere. The research charge is a separate literal in another module, so nothing
was checking the documented relationship at any participation.

**Economic impact.** Research evidence gates promotion to the Desk. A lane can be
validated on 5 bps and lose money at the desk's own modelled 11.5 bps, which is
exactly the failure the integrity invariant "research evidence must describe the
executable paper/shadow strategy rather than a more favorable backtest object"
forbids.

**What this wave did.** `economics/consistency.py` computes the implied
participation ceiling from the execution model's own fields and blocks the economic
gate when research is cheaper than execution. A discriminating test asserts the
6.5 bps understatement and the 0.6125 % ceiling.

**What this wave deliberately did not do.** Change either constant. Raising the
research cost re-rates already recorded lane evidence; lowering the desk's
participation does not. That trade-off is the project owner's.

### ECON-002 — `QUOTE_STALENESS_LIMIT_HAS_NO_PROVENANCE` (introduced and flagged)

`operations/failures.check_quote` defaults to 300 seconds. That is an assumed
parameter of precisely the class ECON-001 is about, introduced by this wave. It is
flagged rather than hidden: the limit must be declared per venue with provenance
before it gates anything real.

### Observations that are not defects

* V1's session-level causal timeline (decision after close(t), fill at open(t+1),
  mark at close(t+1)) held under review. No change needed.
* `desk/risk.py verify_final` already re-checks the exact post-fill portfolio, so
  the final-state principle was already honoured at the desk. `economics/sizing.py`
  extends it to the sizing plan rather than duplicating it.

---

## 7. Opportunity-cost review (workstream 35)

### What was spent

One autonomous Builder session: 7 code commits, ~4,900 lines of new source and
tests across `quant.economics`, `quant.science`, `quant.operations`, two
`quant.dataplane` modules, two `quant.factory` modules, two scripts, 278 tests.

### What was displaced

Nothing of Astra's: P0 pre-`t0` is exclusively theirs and was untouched. Inside
this track, the work displaced is **numerical economic calibration** — and that is
the honest limit of this wave. A complete recipe engine does not move the threshold
by one basis point until per-parameter source contracts and values exist, and those
are Blue's. Wave 1 removed the excuse for not calibrating; it did not calibrate.

### Two irreversible costs incurred, knowingly

1. **48 trials charged against `us_sector_etf_daily` forever.** The multiplicity
   budget on that dataset went from 36 to 84 declared trials, so every future
   expression on it needs |t| ≥ 3.434 instead of |t| ≥ 3.24. That is the real price
   of testing the peer lead-lag family, it was paid before the result was seen, and
   it cannot be refunded by the family failing. The alternative — not declaring the
   grid — would have been cheaper only by being dishonest.
2. **One DISCOVERY-window use.** The window is still available for other families,
   but this family's claim on it is spent: a second grid on the same mechanism
   would be the same search continued, not new evidence.

### The cost still being incurred, every day

**The forward recorder is built and is recording nothing.** Its value is
proportional to the calendar time it has been running when the first forward
confirmation is needed, and that time cannot be bought later at any price. Every
session not recorded is forward evidence permanently lost. This is the only cost in
this review that compounds, and it is blocked on nothing scientific — only on a
scheduling integration that `clock.py`'s freeze currently prevents.

Everything else on this branch can be rebuilt in a week. Six months of forward
observations cannot.

### Information value obtained

* The Form 4 economic lane's remaining blockers are now a short, specific list of
  Blue decisions instead of an open-ended "complete mini-D09" (proposals artifact).
* D05-A eligibility is decidable mechanically before D07 is chosen, which removes
  the sequencing argument that sits in front of the whole lane.
* A quantified, previously unchecked inconsistency between research and execution
  costs (ECON-001), worth 6.5 bps one-way at full participation.
* A negative result on a new family, cheaply: 48 expressions, no promotion, and the
  Builder-days a validation run would have cost are saved.

### Capital potential

Unchanged, and deliberately so: no capital authority was created. What changed is
the number of ways the system could have *wrongly* authorised capital — research
cheaper than execution, uncharged model risk on assumed coefficients, a clipped
allocation presented as the confirmed policy, the same risk charged twice, a
significant effect below its own break-even. Each of those is now a failing check.

### Single recommendation

Start the forward recorder. Everything else in this wave can wait a week without
loss; forward data cannot.

---

## 8. Red team against this wave's own work (workstream 30)

Eight weaknesses, found by attacking my own output rather than the base.

1. **A provisional recipe can still produce `CONTINUE`.** `economic_gate` accepts
   `RECIPE_PROVISIONAL` and can return `CONTINUE` with
   `authority = DEVELOPMENT_EVIDENCE_ONLY`. I allowed this so development can
   proceed before calibration, but it means an uncalibrated threshold can gate a
   positive verdict. **Needs a Blue ruling.**
2. **The affine-shortcut probe samples three points.** A cost function equal at the
   domain endpoints and midpoint but varying in between would pass
   `beee_affine`'s check. Bounded: the grid root-finder is the authoritative path
   and would disagree.
3. **The cluster-robust variance trusts the clustering unit.** A misspecified unit
   silently understates the variance, and the correct unit is defined by D07-O4,
   which is unfrozen. Named dependency, not fixed.
4. **`ExposureBudget` provenance is declared, not proved.** It reports
   `FROZEN_ALLOCATION_CONSTRUCTOR` because the caller says so; nothing verifies the
   per-event exposures came from that constructor.
5. **The forward recorder's guard enforces monotonicity, not truthfulness.**
   `recorded_at` is supplied by the caller, so a wrong clock still writes a wrong
   instant. A real fix needs an external time attestation.
6. **ECON-002**: the 300-second quote staleness default has no provenance (§6).
7. **A narrow candidate space can produce a false `DESIGN_INVARIANT`.** The O2/O3/O4
   candidate sets are caller-supplied. Mitigated by returning the space used with
   every verdict, not by preventing the narrowing.
8. **`placebo_offsets` checks overlap against the event's own exposure window**, not
   against other events' windows in a clustered sample. In a heavily overlapping
   sample a nominally admissible offset can still share returns with a neighbour.

Items 1 and 3 are the two that could change a deployment decision.

---

## 9. Decisions refused as beyond this Builder's authority

Full list with reasoning in `handoff/CLAUDE_WAVE1_PROTOCOL_PROPOSALS_2026-09-19.md`
§7. In brief:

1. D07 O1, O2, O3, O4 selections, and the unenumerated O2/O3 admissible sets.
2. D05-A metric list, strata, stopping rule.
3. α, power, one- vs two-sided form, sequential stopping, futility and equivalence
   boundaries, authoritative variance method.
4. Every D19 terminal-treatment option and the adverse perturbation set.
5. Numerical Form 4 cost coefficients, uncertainty envelopes, joint adverse
   scenario values.
6. Promotion of the `M_economic` functional from freeze candidate to authority.
7. Whether ECON-001 is closed by raising the research cost or lowering desk
   participation.
8. Whether a `RECIPE_PROVISIONAL` evaluation may ever yield `CONTINUE` (red team
   8.1).
9. Reopening Route A or workstream 16.
10. Anything that would move `t0`, change P0 governance, or authorise real capital.

---

## 10. Top 10 contributions by expected contribution to net economic value

Ranked by expected effect on net economic value, not by sophistication.

1. **ECON-001 and its guard.** The only finding in this wave that quantifies money
   the system was about to lose: 6.5 bps one-way at full participation, on evidence
   that gates promotion to the Desk. Prevents deploying lanes that were validated
   against a cheaper strategy than the one that would run.
2. **The economic gate's `KILL` on significant-but-dominated lanes.** Turns
   statistical significance from a licence into one of two required conditions.
   Every lane killed here saves its frictions and the Builder-days its validation
   would have consumed.
3. **Capacity clipping as a new policy version.** Deploying a clipped allocation
   under a claim confirmed on the unclipped weights is deploying an unconfirmed
   strategy. This is the difference between a smaller position and a different
   estimand, and it was invisible before.
4. **The MEUE recipe engine.** The object that converts a research result into an
   economic decision at all. It produces no authoritative number yet, which is why
   it ranks below the three findings above — but without it, every lane is decided
   on statistics alone, which is how a system pays 22 bps to capture 10.
5. **Uncharged model risk is now a failing check.** A cost coefficient that carries
   only "it exists in V1 code" provenance must appear in the adverse scenario set or
   the margin is unresolved. On the fixture this is worth 12.6 bps of required
   effect — larger than break-even itself.
6. **Forward recorder.** Zero value today, the highest ceiling of anything here,
   and the only item whose value is destroyed by delay (§7).
7. **Order write-ahead plus `RECONCILIATION_UNKNOWN`.** Prevents the two
   operational failures that cost real currency directly: a restart doubling an
   exposure, and an outage resolved by assuming a fill.
8. **Cluster-robust ratio variance.** Removes the free t-statistic that comes from
   treating overlapping exposures as independent. Deploying noise is the most
   expensive thing a quant system does.
9. **Executable D05-A invariance test.** Unblocks the sequencing in front of the
   entire Form 4 lane by making eligibility decidable before a geometry is chosen.
   Economic value is indirect but the lane is the largest capital opportunity in the
   system.
10. **The negative peer lead-lag result.** A cheap, honest no. Saves a validation
    cycle and prices the multiplicity cost of having asked.

---

## 11. Attestation

```
P0_RESERVOIR_ACCESSED   = FALSE
P0_PROTOCOL_MUTATED     = FALSE
ROUTE_A_REOPENED        = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
T0_TOUCHED              = FALSE
```

Supporting facts for each:

* **`P0_RESERVOIR_ACCESSED = FALSE`.** No file under `src/quant/dataplane/sec/`,
  `var/sec/`, or `deploy/` was read for content or modified. `form4_parse.py` is a
  pure function over bytes with no filesystem or network access, so it is
  structurally incapable of reaching the reservoir; its fixtures are synthetic with
  invented CIKs. No filing count, accession, identity, outcome, locator, attempt
  journal or distribution was read or inferred. `prioritization.py` refuses any
  prospective P0 signal as a priority input.
* **`P0_PROTOCOL_MUTATED = FALSE`.** No file in `governance/` was modified. This
  branch writes only to `handoff/`, `src/quant/{economics,science,operations}`,
  three additive `src/quant/{dataplane,factory}` modules, one backward-compatible
  parameter on `factory/evaluate.walk_forward`, `scripts/`, and `tests/`.
  `src/quant/clock.py`, `scripts/quant.py`, `deploy/**` and
  `src/quant/dataplane/sec/**` are untouched — confirmed by `git diff --stat`
  against the base.
* **`ROUTE_A_REOPENED = FALSE`.** Workstream 16 is `WAIT`. No retired Route-A
  object was reintroduced; `parameters.py` refuses `MINIMUM_ACROSS_SOURCES` by name
  as `ROUTE_A_SOURCE_MINIMUM_DOES_NOT_TRANSFER_TO_EXPECTED_COST`.
* **`REAL_CAPITAL_AUTHORIZED = FALSE`.** Every economic verdict carries
  `capital_authority = PAPER_SHADOW_ONLY`, and a test asserts it across the whole
  verdict range. The best state `readiness.py` can reach is `PAPER_SHADOW_READY`.
* **`T0_TOUCHED = FALSE`.** No scheduler, service, supervisor or `t0` readiness
  path was read for modification or changed.

Nothing on this branch was merged. PR #17 was not touched. The Codex branch was
not read, searched for, or coordinated with.
