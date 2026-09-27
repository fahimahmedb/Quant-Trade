# CLAUDE — RESEARCH -> FROZEN EFFECT ESTIMATE SCIENTIFIC PRESTAGE — RESULT — 2026-09-21

Mission type: `READ_ONLY_ANALYSIS + SCIENTIFIC_CONTRACT_PREP`. No Product code,
tests, scripts, schemas or workflows were modified.

## 0. Exact refs inspected

- Assigned branch: `parallel/claude-research-frozen-effect-estimate-prestage-2026-09-21`
  @ `866e6c1e96ab7460a7cd6464ead922e710ce7b0b` (verified via `git fetch` +
  `git rev-parse` before substantive work; matched expected mission head).
- Canonical Economic: `parallel/claude-economic-v2-2026-09-20@35dff27b8fac53618da434ee6d31febbddcc0e69`
  — `src/quant/economics/decision.py`, `coordinate.py`, `recipe.py`, `states.py`,
  `timeline.py`.
- Canonical Forward: `parallel/claude-forward-data-2026-09-20@83521dbfdd90027c90d04adfb7d814593c2355c5`
  — `src/quant/science/{eligibility,formation,inference,invariance,nulls,regimes}.py`,
  `src/quant/dataplane/*`.
- Blue Product/Research spine: `cbf30c1bb38dd69c11fb64c523c3aec694116b9c` —
  `src/autonomous_research/ticket.py`, `src/quant/factory/{evaluate,workers,signals}.py`.
- Cross-checked with `git grep` across every `origin/*` branch for callers of
  `ratio_estimate(`, `EffectEstimate`, `DeltaCoordinateBinding`,
  `evaluate_delta_coordinate` in `src/quant/factory` and `src/autonomous_research`.

## 1. Candidate producer inventory

| Candidate | Location | Computes |
|---|---|---|
| P1 `walk_forward` / `summarize` / `falsify` | `src/quant/factory/evaluate.py`, wired into `ticket.test_result` / `ticket.validation_result` by `src/quant/factory/workers.py:90-154` | Portfolio-rebalanced `gross_return`/`net_return`/Sharpe/t-stat/beta over `weights_for()` allocations, benchmarked against a configurable symbol |
| P2 `ratio_estimate` / `cluster_bootstrap_ratio` | `src/quant/science/inference.py` | Cluster-robust delta-method (and bootstrap) point + CI for `sum a_j T_j / sum a_j`, generic `(weights, outcomes, clusters)` |
| P3 `aggregate_allocation_weighted` | `src/quant/economics/timeline.py:243` | Point-only `delta_hat = sum(notional*excess_return)/sum(notional)` over `NetOutcome` records, gross-of-friction, SPY-checked |
| P4 `qualifying_events` / `eligibility.py` | `src/quant/science/eligibility.py` | Form 4 population predicate (issuer/insider/code P/indicator A). No return, no weight, no outcome. |
| P5 `formation.py` geometry | `src/quant/science/formation.py` | Formation window/threshold/hold-length state machine (D07 O1–O4). No return, no weight, no outcome. |
| P6 `ResearchTicket` | `src/autonomous_research/ticket.py` | Generic `dict[str, Any]` fields (`test_result`, `validation_result`, `hypothesis`). No `EffectEstimate`/`DeltaCoordinateBinding` field exists at all. |

`ratio_estimate` is reachable only from `src/quant/science/nulls.py` and
`src/quant/science/regimes.py` (robustness/placebo tooling) and from
`tests/test_science_protocol.py`. No commit on any `origin/*` branch calls it
from `src/quant/factory/*` or `src/autonomous_research/*`.

## 2. Rejected candidates + exact reason

- **P1 (`evaluate.py`/`workers.py`, the actual live ticket pipeline) — `WRONG_COORDINATE`.**
  It computes `net_return`/`gross_return` on `weights_for()` portfolio
  rebalancing (`evaluate.py:59-77`), not per-event Form 4 allocation weights.
  Its aggregation is exactly what `coordinate.py`'s `REJECTED_AGGREGATIONS`
  names and refuses: `net_return`/`gross_return` here are period-compounded
  `REALISED_PORTFOLIO_RETURN`, and `falsify()`'s headline test operates on
  `net_return` (`NET_OF_FRICTION_RETURN`, explicitly rejected — delta is
  gross). This is the function actually wired into `ticket.test_result` /
  `ticket.validation_result` (`workers.py:151-154`), i.e. it is the real
  current Research output, and it is not on the frozen coordinate. Renaming or
  relabeling its `net_return`/`t_statistic` as `delta_hat`/`p_value` would be
  exactly the prohibited inference from similar names/units.
- **P3 (`aggregate_allocation_weighted`) — `PARTIAL_BUT_COMPATIBLE`, not a producer.**
  Its point formula is identical in shape and inputs to the frozen estimand
  (`notional` weight, gross `excess_return` vs SPY, `ALLOCATION_WEIGHTED_RATIO`
  numerator/denominator) — but it returns `delta_hat`/`event_count` only. No
  `lower`, `upper`, `confidence_level`, `p_value`, or clustering unit is
  computed anywhere in this module. It is downstream ledger/accounting over
  already-decided `NetOutcome`/`CausalEventLedger` fill records (module
  docstring: "signal -> order -> fill -> net P&L"), i.e. a realized-outcome
  tally, not a pre-decision Research inference object. It cannot itself
  satisfy the interval/confidence/clustering fields the contract requires, and
  its `notional` weight is a fill-time exposure, not a declared pre-outcome
  allocation-constructor weight with a stated `allocation_constructor_id`.
- **P4/P5 (`eligibility.py`, `formation.py`) — `NOT_RELEVANT` as direct producers.**
  They define the qualifying population and event geometry (D07 closed/open
  dimensions) but emit no return, weight, or outcome value at all. They are
  necessary future inputs to any real producer, not candidates themselves.
- **P6 (`ResearchTicket`) — `NOT_RELEVANT`.** Carries no `EffectEstimate` or
  `DeltaCoordinateBinding` field; `test_result`/`validation_result` are
  untyped dicts populated only by P1.

## 3. Non-rejected candidate requiring the falsification questions

**P2 (`ratio_estimate` / `RatioEstimate`, `src/quant/science/inference.py`) —
`INSUFFICIENT_PROOF` (mathematically compatible in isolation; never assembled
into a lawful producer).**

Answering the mission's falsification questions for P2 as a *function*, not as
an assembled pipeline:

1. Estimand: exactly `sum_j a_j T_j / sum_j a_j` on caller-supplied
   `(weights, outcomes)` — form matches frozen `delta`, **if** the caller
   supplies `weights = a_j` fixed pre-outcome and `outcomes = T_j` on the
   frozen `security_return - SPY_excess`, gross-of-friction convention. The
   function itself does not know or enforce this; it accepts any floats.
2. Aggregation: literally `ALLOCATION_WEIGHTED_RATIO`
   (`numerator/denominator`, docstring cites EC1 section 6) — proof by
   construction of the formula, not by string tag.
3. Weights precede outcomes: **not provable from this module alone.** No
   caller in the repository passes it Form 4 `notional`/exposure fixed at a
   declared pre-outcome instant; the only current callers (`nulls.py`,
   `regimes.py`, tests) use synthetic arrays.
4. Point and interval same estimand: **yes**, within one call — `point`,
   `lower`, `upper` are all derived from the same `(weights, outcomes,
   clusters)` triple via the closed-form delta-method or the percentile
   bootstrap.
5–6. Security/benchmark convention and SPY: **undeclared** — `outcomes` is an
   opaque `Sequence[float]`; the module carries no `ReturnConvention` or
   `benchmark_symbol` and cannot itself prove the SPY-excess, gross,
   single-holding-interval convention was used to build `outcomes`.
7. Holding interval identical both sides: **undeclared**, same reason.
8. Corporate actions / terminal treatment: **undeclared**, same reason — this
   is D19's domain and nothing in `inference.py` or its current callers
   references D19.
9. Clustering scientifically justified: the *mechanism* is legitimate
   (cluster-robust sandwich variance, small-cluster `G/(G-1)` correction,
   `ESTIMATE_SINGLE_CLUSTER` refusal when `groups < 2`) but the *unit itself*
   is caller-supplied and undeclared for any real Form 4 population; D07-O4
   (overlap geometry) is explicitly still open (`formation.py` docstring),
   which is exactly the state `decision.py` encodes as
   `CLUSTERING_UNIT_O4_UNRESOLVED`.
10. Sample provenance immutable/PIT-safe: **not addressed by this module**;
    provenance would have to come from the (nonexistent) caller.
11. Discovery/validation reuse: **not addressed**; no caller exists to check.
12. `FORWARD_CONFIRMATION` vs `DEVELOPMENT`: **cannot be determined** absent a
    caller and a Forward admissibility check (`forward_admissibility.py`) tying
    a specific invocation to specific forward-only evidence.
13. Multiple testing: `MultiplicityBudget` exists in the same module
    (`inference.py`) and is a legitimate declared-trial-budget mechanism, but
    nothing wires it to a real per-lane trial count for Form 4 research.
14. Gross vs net-of-friction silently changed: no — the function does not
    touch cost/friction at all; that discipline is entirely the caller's
    responsibility, which does not currently exist.

Conclusion for P2: the estimator math is exactly the frozen aggregation and
the interval/clustering machinery is sound, but it is a general-purpose
statistics utility with no binding, no Form 4/SPY caller, and no
`DeltaCoordinateBinding`. Supplying that binding and the actual Form 4/SPY
`(weights, outcomes, clusters)` construction is not exposing missing
metadata on an otherwise-complete computation — it is writing the scientific
computation (excess-return convention, corporate-action/terminal treatment,
clustering unit choice, allocation-constructor identity) that the mission
explicitly forbids inventing here.

## 4. Winning producer

**None.** No commit on any inspected or grepped branch assembles Form 4
qualifying events into `(a_j, T_j, cluster_j)` and calls `ratio_estimate` (or
equivalent), attaches a `DeltaCoordinateBinding`, calls
`evaluate_delta_coordinate`, or populates an `EffectEstimate`. The only
pipeline actually wired into `ResearchTicket` (P1) computes a different,
explicitly rejected coordinate.

## 5. Field-by-field mapping to `EffectEstimate`

| `EffectEstimate` field | Available today? |
|---|---|
| `delta_hat` | No lawful producer emits this. P1's `net_return`/`gross_return` are the wrong coordinate. P2 can compute it only given inputs no caller builds. P3 computes the right point formula but only post-fill, with no interval. |
| `lower` / `upper` | Not available on the frozen coordinate anywhere; P2's CI machinery exists but is unbound. |
| `confidence_level` | Only meaningful attached to a real P2 call; none exists. |
| `evidence_label` | No code currently classifies any Research output as `EXPLORATION`/`TRAINING`/`DEVELOPMENT`/`FORWARD_CONFIRMATION`. |
| `sample_provenance` | Not attached to any candidate estimate. |
| `event_count` | P2/P3 both report this correctly *if* invoked; not invoked. |
| `p_value` | `nulls.empirical_p_value` exists and is sound, but is not wired to any real Form 4 estimate either. |
| `clustering_unit_provenance` | Undeclared everywhere; D07-O4 (overlap geometry) is open, so even a hypothetical wiring could not currently declare a resolved clustering unit — it would have to report `CLUSTERING_UNIT_O4_UNRESOLVED` or `CLUSTERING_UNIT_UNDECLARED`. |

## 6. `DeltaCoordinateBinding`

No binding exists anywhere in the codebase for a Research-produced estimate.
`coordinate.py`'s own `_missing()` would return every field:
`SECURITY_RETURN_CONVENTION_UNDECLARED`, `BENCHMARK_RETURN_CONVENTION_UNDECLARED`,
`BENCHMARK_SYMBOL_UNDECLARED`, `AGGREGATION_UNDECLARED`,
`ALLOCATION_CONSTRUCTOR_UNDECLARED`, `ALLOCATION_WEIGHT_ORDERING_UNDECLARED`.
`evaluate_delta_coordinate(binding).compatible` cannot be `True` because no
binding is ever constructed to evaluate. State: `DELTA_COORDINATE_UNRESOLVED`.

## 7. Interval / clustering provenance

The only interval-and-clustering-capable code (P2) is unbound to any real
sample. The clustering unit for a real Form 4 population additionally depends
on D07-O4 (overlap geometry), which the same commit range declares open
(`formation.py`: "O4 — overlap geometry ... Until it is declared, an
observation count is `D05_B_UNTIL_O4_FROZEN`"). A lawful clustering
declaration therefore cannot precede O4 resolution.

## 8. PIT / evidence-label constraints

- Forward admissibility machinery exists (`src/quant/dataplane/forward_admissibility.py`,
  `forward_recorder.py`, `forward_coverage.py`) and is a plausible future
  source of `FORWARD_CONFIRMATION` gating, but nothing in P1/P2/P3 currently
  calls it, so no existing estimate can legally claim
  `EVIDENCE_FORWARD_CONFIRMATION` today — every existing Research output
  (P1's `test_result`/`validation_result`) is at most `DEVELOPMENT` evidence,
  consistent with the correction spec's C6/C8.
- Whether discovery/validation data have already been consumed for a given
  sample is not tracked by any candidate producer; this is a further
  prerequisite before any future estimate could claim non-reused evidence.

## 9. Smallest future changed-path set (not authorized here)

If/when Blue authorizes the actual estimator build, the minimum path set is:

1. A new Form 4 event-outcome assembler (new module, e.g.
   `src/quant/science/effect.py`) that, for a declared `GeometryChoice` +
   `O3Convention` + resolved O4 unit, turns `qualifying_events()` output into
   `(a_j, T_j, cluster_j)` triples with `a_j` fixed at the pre-outcome
   allocation-constructor instant, `T_j` on the declared gross SPY-excess
   `ReturnConvention`.
2. A `DeltaCoordinateBinding` construction bound to that assembler's declared
   conventions, evaluated via `evaluate_delta_coordinate` before any estimate
   is trusted.
3. A thin adapter calling `ratio_estimate`/`cluster_bootstrap_ratio` with
   those triples and wrapping the result plus the binding hash into
   `economics.decision.EffectEstimate`.
4. A new typed field on `ResearchTicket` (or a wrapper object) to carry that
   `EffectEstimate` instead of today's untyped `test_result`/`validation_result`.
5. An evidence-label rule that ties the assembler's input sample to
   `forward_admissibility.py` state, defaulting to `DEVELOPMENT` unless proven
   `FORWARD_CONFIRMATION`.

None of this was implemented in this mission. Step 1 in particular requires
resolving D07-O4 first, which is outside this mission's scope.

## 10. Consequence for the ONE BIG BUILD

`SCIENCE_EFFECT_ESTIMATE_CONTRACT` cannot close as ready. Per
`governance/BLUE_RESEARCH_FROZEN_EFFECT_ESTIMATE_PRESTAGE_2026-09-21.md`
section 5 (Outcome C) and
`governance/BLUE_POST_P0_VERTICAL_PREBIGBUILD_CORRECTION_SPEC_2026-09-21.md`
C8, the future large Builder mission must retain real Research -> Economic as
fail-closed `NO_TRADE` (`EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE`)
for every real ticket until the section-9 changed-path set above is built and
separately reviewed. Test matrix item 30
(`ordinary real Research lacking frozen estimate -> fail-closed NO_TRADE`) is
therefore not a hypothetical edge case for the first vertical slice — it is
the *only* reachable outcome for genuine Research tickets today. Any fixture
that manufactures a positive `EffectEstimate` for wiring/E2E tests must be
labeled as a synthetic fixture and must not be cited as evidence that real
Research produces this coordinate.

## 11. Remaining unresolved scientific questions

- D07-O4 (overlap geometry) resolution, which the clustering unit depends on.
- The exact allocation-constructor definition (`allocation_constructor_id`)
  and proof it is computable from information available strictly before each
  event's outcome.
- The exact `ReturnConvention` (return definition, interval spec,
  corporate-action convention, terminal/D19 treatment) for both the security
  leg and the SPY leg of `T_j`.
- Whether any existing Form 4 sample has already been used for
  discovery/threshold-setting, which would bar it from being reused as a
  confirmatory sample.
- The declared multiple-testing trial budget for the Form 4 lane specifically
  (`MultiplicityBudget` exists but is uninstantiated for this lane).
- The link between a future assembler's sample and `forward_admissibility.py`
  sufficient to legally claim `FORWARD_CONFIRMATION` rather than
  `DEVELOPMENT`.

## 12. Final status

```text
SCIENCE_EFFECT_ESTIMATE_CONTRACT = BLOCKED_MISSING_SCIENTIFIC_ESTIMATOR
```

## 13. Safety / authority preserved

```text
PRODUCT_CODE_MODIFIED = FALSE
PRODUCT_INTEGRATION = PAUSED
P0_RUNTIME_MUTATION = FALSE
TARGET_HOST_TOUCHED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
t0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
```

Returning control to Blue.
